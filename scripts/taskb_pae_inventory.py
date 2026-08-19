"""Task B of ORDERS-Code-2026-08-18 — the PAE inventory. READ-ONLY.

⚠⚠ THIS FILE CONTAINS NO `DELETE`, `UPDATE`, `INSERT`, `TRUNCATE`, `DROP`, `ALTER` OR ANY OTHER
DDL/DML. Every statement is a bare `SELECT`. A self-check below refuses to run if that stops being
true, so the guarantee is enforced rather than asserted.

⚠ Run ONLY while the owner's `fly mpg proxy zp2wjrej9lwodn4q -p 16380` is up, and run NOTHING ELSE
while it is. A tunnel to production looks exactly like localhost, and KEEL V8-a walks straight
through this configuration. The window is the hazard, not the query.

⚠ The credential is never printed. `.env` is read to build the connection and the URL is redacted
in all output; the DB credential is still unrotated.

Why a SELECT and not a code read (owner ruling, 2026-08-17): a source file answers what the
pipeline does NOW. The 2,690 folds happened across weeks under whatever code was deployed at the
time, and D-035 part 2 records that the upload's PAE behaviour changed. A code read can only
confirm the hypothesis; this is the query that can refute it.

    python scripts/taskb_pae_inventory.py
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

PROXY_HOST = "localhost"
PROXY_PORT = 16380

#: ⚠ The self-check. If any of these appears in this file's own source, the script refuses to run.
FORBIDDEN = ("delete ", "update ", "insert ", "truncate", "drop ", "alter ", "create ",
             "grant ", "revoke ")

# ── the queries. Bare SELECTs, bucketed — a single total is a summary, and a summary is not the
#    records (owner ruling: the cohort is the control). ───────────────────────────────────────────

Q_TOTALS = """
SELECT
  count(*)                                              AS n_rows,
  count(*) FILTER (WHERE pae_json_path IS NULL)         AS n_pae_null,
  count(*) FILTER (WHERE pae_json_path IS NOT NULL)     AS n_pae_set,
  count(*) FILTER (WHERE mean_plddt IS NOT NULL)        AS n_folded
FROM protein_analyses
"""

Q_BY_COHORT = """
SELECT
  CASE WHEN cohort_tranche IS NULL THEN 'cohort_untagged' ELSE 'census_tagged' END AS bucket,
  count(*)                                          AS n_rows,
  count(*) FILTER (WHERE pae_json_path IS NULL)     AS n_pae_null,
  count(*) FILTER (WHERE pae_json_path IS NOT NULL) AS n_pae_set,
  count(*) FILTER (WHERE mean_plddt IS NOT NULL)    AS n_folded
FROM protein_analyses
GROUP BY 1
ORDER BY 1
"""

Q_BY_TRANCHE = """
SELECT
  cohort_tranche,
  count(*)                                          AS n_rows,
  count(*) FILTER (WHERE pae_json_path IS NULL)     AS n_pae_null,
  count(*) FILTER (WHERE pae_json_path IS NOT NULL) AS n_pae_set,
  count(*) FILTER (WHERE mean_plddt IS NOT NULL)    AS n_folded
FROM protein_analyses
GROUP BY 1
ORDER BY 1 NULLS FIRST
"""

#: ⚠ By fold DATE, so the D-035-part-2 boundary shows itself rather than being assumed. The
#: bucketing is by day; no cut point is baked in.
Q_BY_DATE = """
SELECT
  date(j.completed_at)                                AS fold_day,
  count(*)                                            AS n_rows,
  count(*) FILTER (WHERE a.pae_json_path IS NULL)     AS n_pae_null,
  count(*) FILTER (WHERE a.pae_json_path IS NOT NULL) AS n_pae_set
FROM protein_analyses a
JOIN jobs j ON j.analysis_id = a.id
WHERE j.completed_at IS NOT NULL
GROUP BY 1
ORDER BY 1
"""

#: ⚠ Does any row anywhere carry a PAE path? If none does, the finding is larger than framed.
Q_ANY_PAE = """
SELECT count(*) AS n_with_pae FROM protein_analyses WHERE pae_json_path IS NOT NULL
"""


def statements() -> dict:
    """Every SQL string this script can execute. ⚠ If a query is added and not listed here, the
    self-check cannot see it — so the check reads THIS dict and the executor uses it too."""
    return {"Q_TOTALS": Q_TOTALS, "Q_BY_COHORT": Q_BY_COHORT, "Q_BY_TRANCHE": Q_BY_TRANCHE,
            "Q_BY_DATE": Q_BY_DATE, "Q_ANY_PAE": Q_ANY_PAE}


def self_check() -> None:
    """⚠ Refuse to run unless every executable statement is a bare SELECT.

    ⚠⚠ It inspects THE QUERIES, not this file's source. An earlier version scanned the source and
    refused on its own denylist and docstring — a guard that cannot distinguish the word from the
    deed. The queries are the thing that reaches the database, so they are the thing checked.
    """
    for name, sql in statements().items():
        body = sql.strip().lower()
        if not body.startswith("select"):
            raise SystemExit(f"⚠ REFUSING TO RUN — {name} does not begin with SELECT")
        hits = [w for w in FORBIDDEN if w in body]
        if hits:
            raise SystemExit(f"⚠ REFUSING TO RUN — {name} contains {hits}")
        if ";" in body.rstrip(";"):
            raise SystemExit(f"⚠ REFUSING TO RUN — {name} contains a statement separator")
    print(f"self-check: {len(statements())} statements, all bare SELECT, no DML/DDL, no separators")


from db.dburl import normalize_db_url  # noqa: E402


def proxy_url() -> tuple[str, str]:
    """(url, redacted) — DATABASE_URL from .env, repointed at the local proxy.

    ⚠ The credential is never returned in the redacted form and never printed.
    """
    env = (REPO / ".env")
    if not env.is_file():
        raise SystemExit("⚠ no .env — cannot build the connection. STOP.")
    url = ""
    for line in env.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("DATABASE_URL"):
            url = line.split("=", 1)[1].strip().strip('"').strip("'")
            break
    if not url:
        raise SystemExit("⚠ no DATABASE_URL in .env — STOP.")

    # repoint host:port at the proxy, keep user/password/dbname
    url = re.sub(r"@[^/@]+/", f"@{PROXY_HOST}:{PROXY_PORT}/", url, count=1)
    # ⚠ Was a hand-rolled copy of db/dburl.py's rule. It WORKED — and that is the point: a
    # second implementation of a documented single-source helper goes stale silently, the first
    # time the helper learns a new scheme. `normalize_db_url` is idempotent and leaves an
    # already-driver-bearing URL alone, so it is a drop-in here.
    url = normalize_db_url(url)
    redacted = re.sub(r"//[^@]+@", "//<redacted>@", url)
    return url, redacted


def main() -> int:
    self_check()
    from sqlalchemy import create_engine, text

    url, redacted = proxy_url()
    print(f"connecting: {redacted}")
    engine = create_engine(url, future=True)

    with engine.connect() as conn:
        print("\n" + "=" * 84)
        print("TOTALS — protein_analyses")
        print("=" * 84)
        r = conn.execute(text(Q_TOTALS)).mappings().one()
        for k, v in r.items():
            print(f"  {k:14s} {v:,}")

        print("\n" + "=" * 84)
        print("⚠ THE CONTROL — cohort (untagged) vs census (tagged)")
        print("=" * 84)
        print(f"  {'bucket':18s} {'rows':>8s} {'pae NULL':>10s} {'pae SET':>9s} {'folded':>8s}")
        for row in conn.execute(text(Q_BY_COHORT)).mappings():
            print(f"  {row['bucket']:18s} {row['n_rows']:8,d} {row['n_pae_null']:10,d} "
                  f"{row['n_pae_set']:9,d} {row['n_folded']:8,d}")

        print("\n" + "=" * 84)
        print("BY TRANCHE")
        print("=" * 84)
        print(f"  {'tranche':>8s} {'rows':>8s} {'pae NULL':>10s} {'pae SET':>9s} {'folded':>8s}")
        for row in conn.execute(text(Q_BY_TRANCHE)).mappings():
            t = "NULL" if row["cohort_tranche"] is None else str(row["cohort_tranche"])
            print(f"  {t:>8s} {row['n_rows']:8,d} {row['n_pae_null']:10,d} "
                  f"{row['n_pae_set']:9,d} {row['n_folded']:8,d}")

        print("\n" + "=" * 84)
        print("BY FOLD DAY — the D-035-part-2 boundary must show itself, not be assumed")
        print("=" * 84)
        rows = list(conn.execute(text(Q_BY_DATE)).mappings())
        print(f"  {'day':>12s} {'rows':>8s} {'pae NULL':>10s} {'pae SET':>9s}")
        for row in rows:
            print(f"  {str(row['fold_day']):>12s} {row['n_rows']:8,d} "
                  f"{row['n_pae_null']:10,d} {row['n_pae_set']:9,d}")
        print(f"  ({len(rows)} distinct fold days)")

        n = conn.execute(text(Q_ANY_PAE)).scalar_one()
        print("\n" + "=" * 84)
        print(f"⚠ ROWS ANYWHERE CARRYING A PAE PATH: {n:,}")
        if n == 0:
            print("  ⚠⚠ NONE. Not one row in the table, cohort or census, records a PAE artifact.")
        print("=" * 84)

    engine.dispose()
    return 0


if __name__ == "__main__":
    sys.exit(main())
