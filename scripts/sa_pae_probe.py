"""SA1 probe — where the 79 cohort PAE matrices live, and what shape they are. READ-ONLY.

⚠⚠ NO `DELETE`, `UPDATE`, `INSERT`, `TRUNCATE`, `DROP`, `ALTER` OR ANY DDL/DML. Every statement is
a bare `SELECT`, and the self-check below refuses to run if that stops being true — the same
discipline as `scripts/taskb_pae_inventory.py`, reused rather than re-derived.

⚠ Run ONLY while the owner's `fly mpg proxy … -p 16380` is up. The credential is never printed.
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

PROXY_HOST = "localhost"
PROXY_PORT = 16380

FORBIDDEN = ("DELETE", "UPDATE", "INSERT", "TRUNCATE", "DROP", "ALTER", "CREATE", "GRANT")

SQL = {
    "paths": """
        SELECT id, input_value, cohort_tranche, pae_json_path, mean_plddt, pdb_path
        FROM protein_analyses
        WHERE pae_json_path IS NOT NULL
        ORDER BY input_value
    """,
    "missing": """
        SELECT id, input_value, cohort_tranche, pdb_path, mean_plddt
        FROM protein_analyses
        WHERE cohort_tranche = 0 AND pae_json_path IS NULL
    """,
}


def _self_check() -> None:
    for name, body in SQL.items():
        b = body.strip()
        if not b.upper().startswith("SELECT"):
            raise SystemExit("⚠ REFUSING TO RUN — %s does not begin with SELECT" % name)
        hits = [w for w in FORBIDDEN if w in b.upper()]
        if hits:
            raise SystemExit("⚠ REFUSING TO RUN — %s contains %s" % (name, hits))
        if ";" in b.rstrip(";"):
            raise SystemExit("⚠ REFUSING TO RUN — %s contains a statement separator" % name)
    print("self-check: %d statements, all bare SELECT, no DML/DDL, no separators" % len(SQL))


def proxy_url() -> tuple[str, str]:
    from db.dburl import normalize_db_url
    env = REPO / ".env"
    if not env.is_file():
        raise SystemExit("⚠ no .env — cannot build the connection. STOP.")
    url = ""
    for line in env.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("DATABASE_URL"):
            url = line.split("=", 1)[1].strip().strip('"').strip("'")
            break
    if not url:
        raise SystemExit("⚠ no DATABASE_URL in .env — STOP.")
    url = re.sub(r"@[^/@]+/", "@%s:%d/" % (PROXY_HOST, PROXY_PORT), url, count=1)
    url = normalize_db_url(url)
    return url, re.sub(r"//[^@]+@", "//<redacted>@", url)


def main() -> int:
    _self_check()
    url, red = proxy_url()
    print("connecting: %s" % red)
    from sqlalchemy import create_engine, text
    eng = create_engine(url)
    with eng.connect() as c:
        rows = list(c.execute(text(SQL["paths"])))
        missing = list(c.execute(text(SQL["missing"])))

    print()
    print("rows carrying a PAE path : %d" % len(rows))
    print()
    print("⚠ SA2 — the cohort row with NO pae path, and its CAUSE:")
    for m in missing:
        print("   id=%s accession=%s tranche=%s pdb_path=%r mean_plddt=%r"
              % (m[0], m[1], m[2], m[3], m[4]))
        # ⚠ an absence is a category with a cause: no pdb_path means the fold never happened,
        # which is different from a fold that ran and emitted nothing
        print("   -> cause: %s" % ("NEVER FOLDED (no pdb_path) — not a fold that emitted no PAE"
                                   if not m[3] else "FOLDED but no PAE persisted ⚠ different defect"))
    print()
    print("⚠ SA1 — are the stored paths reachable from here?")
    seen = 0
    for r in rows[:6]:
        p = pathlib.Path(str(r[3]))
        local = p if p.is_absolute() else (REPO / str(r[3]))
        print("   %-8s %-58s exists=%s" % (r[1], str(r[3])[:58], local.exists()))
        seen += 1
    reachable = sum(1 for r in rows
                    if (pathlib.Path(str(r[3])) if pathlib.Path(str(r[3])).is_absolute()
                        else REPO / str(r[3])).exists())
    print()
    print("   reachable locally: %d of %d" % (reachable, len(rows)))
    if reachable == 0:
        print("   ⚠⚠ NONE are on this machine. The matrices live where the fold ran, so SA1's")
        print("      shape/symmetry question cannot be answered from here without fetching them.")
        print("      STOP AND REPORT rather than substituting the 20 control matrices, which are")
        print("      a DIFFERENT population (D-099 census-recipe controls, not the cohort 79).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
