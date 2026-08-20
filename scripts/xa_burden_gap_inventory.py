"""XA — how much of our tumour evidence sits in indications with no burden denominator. READ-ONLY.

⚠⚠ NO `DELETE`, `UPDATE`, `INSERT`, `TRUNCATE`, `DROP`, `ALTER` OR ANY DDL/DML. Every statement is
a bare `SELECT`, and the self-check refuses to run if that stops being true — the same discipline as
`scripts/sa_pae_probe.py` and `scripts/taskb_pae_inventory.py`, reused rather than re-derived.

⚠ Run ONLY while the owner's `fly mpg proxy … -p 16380` is up. The credential is never printed.

── WHAT THIS COUNTS, AND THE KEY OF EVERY NUMBER ────────────────────────────────────────────────
`CROSSWALK-2026-08-21-hpa-tumour-to-registry.md` measured twenty HPA tumour names against SEER's
site recode. Two **refuse**: `carcinoid` (a MORPHOLOGY, no site to join on) and `skin cancer`
(SEER's recode is literally *"Skin excluding Basal and Squamous"* and its remaining bucket is
*Other NON-EPITHELIAL Skin*, so there is no category that could hold BCC/SCC).

⚠ `urothelial cancer` is `uncertain`, NOT refused, and is reported **separately and never pooled
with the refusals** — renal pelvis sits inside two candidate categories, so it is a grouping
decision rather than a missing count. Pooling two different mechanisms under one number is the
mistake `F-011` and `F-016` were kept apart to avoid.

⚠⚠ THE POINT (`XA3`): a protein staining **High** in an indication nobody counts is tumour evidence
over a population whose size and mortality are unknown, and an ADC case cannot be made without a
denominator.
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

# ⚠ the two refusals and the one uncertain, from the crosswalk — named here so the script cannot
# drift from the document that justifies it
REFUSED = ("carcinoid", "skin cancer")
UNCERTAIN = ("urothelial cancer",)

# ⚠⚠⚠ THE JOIN REACHES THE COHORT ONLY, AND THE FIRST VERSION REPORTED THAT AS A FACT.
# `metadata ->> 'gene'` is populated on **80 of 80 cohort rows and 0 of 2,691 census rows** — the
# census keys on ACCESSION (`input_value`), and its gene symbol lives in the census manifest, not in
# `protein_analyses`. So the first run printed **"census (tranche > 0): 0"**, which is not a
# measurement — it is the join failing and returning a plausible zero. `F-047`'s class exactly, and
# `D-093` decision 6 question (3) is the clause that exists for it.
#
# ⚠ The join is now EXPLICITLY cohort-scoped (`AND pa.cohort_tranche = 0`) so it cannot be mistaken
# for a census answer, and the census side is derived from `clinical_pathology`'s own row scope
# instead: the table is scoped to **census manifest ∪ the 82** (see `db/models.py`), so a gene here
# that is not a cohort gene is a census-manifest gene.
# ⚠⚠ THE FOLDED subset of the census is NOT answerable from this database — it needs the manifest's
# accession↔symbol map — and is reported from the census surface separately rather than guessed.
#
# ⚠⚠ THE COLUMN IS `"metadata"`. `meta` is the ORM ATTRIBUTE — `db/models.py:124` is
# `mapped_column("metadata", ...)` — so raw SQL that copies the Python attribute name fails with
# `column pa.meta does not exist`. The first run of this script did exactly that.
#
# ⚠ AND THE EXPLANATION LIVES HERE, NOT INSIDE THE SQL. A `--` comment carrying a semicolon tripped
# `_self_check`'s statement-separator rule, which is the guard doing its job: a guard over production
# SQL should stay blunt, and prose belongs outside the statement it describes. **The fix was to move
# the comment, never to teach the guard about comments.**
SQL = {
    # every IHC row in the three tumour types of interest, with the cohort/census side resolved
    "rows": """
        SELECT cp.gene_name, cp.cancer, cp.high, cp.medium, cp.low, cp.not_detected,
               pa.cohort_tranche, pa.input_value
        FROM clinical_pathology AS cp
        LEFT JOIN protein_analyses AS pa
          ON pa."metadata" ->> 'gene' = cp.gene_name
         AND pa.cohort_tranche = 0
        WHERE cp.cancer IN ('carcinoid', 'skin cancer', 'urothelial cancer')
        ORDER BY cp.cancer, cp.gene_name
    """,
    # the denominators: how many distinct genes carry ANY IHC row at all
    "denominator": """
        SELECT COUNT(DISTINCT gene_name) FROM clinical_pathology
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


def _report(label: str, cancers: tuple[str, ...], rows: list) -> None:
    sel = [r for r in rows if r[1] in cancers]
    genes = {r[0] for r in sel}
    # ⚠ cohort_tranche 0 is the 82; anything else (or NULL) is not the cohort. A NULL tranche means
    # the gene has no analysis row at all — it carries IHC but was never folded on either surface.
    cohort = {r[0] for r in sel if r[6] == 0}
    # ⚠ NOT a tranche test — see the note above the SQL. `clinical_pathology` is row-scoped to
    # census manifest ∪ the 82, so everything here that is not a cohort gene is a census gene.
    census_manifest = genes - cohort
    high = {r[0] for r in sel if r[2] and r[2] > 0}
    high_cohort = high & cohort

    print()
    print("== %s ==" % label)
    print("   tumour types            : %s" % ", ".join(cancers))
    print("   IHC rows                : %d" % len(sel))
    print("   distinct genes          : %d   (key: DISTINCT gene_name in clinical_pathology)" % len(genes))
    print("   ├─ cohort               : %d   (key: metadata->>'gene' matches, cohort_tranche = 0)" % len(cohort))
    print("   └─ census manifest      : %d   (key: in clinical_pathology, which is scoped to" % len(census_manifest))
    print("                                    census manifest u the 82, and NOT a cohort gene)")
    print("   ⚠ the FOLDED census subset is not answerable here — it needs the manifest's")
    print("     accession<->symbol map, and is reported from the census surface, not guessed.")
    print("   ⚠⚠ genes with High > 0  : %d   (key: clinical_pathology.high > 0 in these types)" % len(high))
    print("        of which cohort    : %d" % len(high_cohort))
    if high_cohort:
        print("   ⚠ XA2 — the cohort rows, enumerated (82 is small enough to name):")
        for g in sorted(high_cohort):
            for r in sorted([x for x in sel if x[0] == g and x[2] and x[2] > 0], key=lambda x: x[1]):
                print("        %-10s %-18s high=%-3s med=%-3s low=%-3s nd=%-3s  acc=%s"
                      % (r[0], r[1], r[2], r[3], r[4], r[5], r[7]))


def main() -> int:
    _self_check()
    url, red = proxy_url()
    print("connecting: %s" % red)
    from sqlalchemy import create_engine, text
    eng = create_engine(url)
    with eng.connect() as c:
        rows = [tuple(r) for r in c.execute(text(SQL["rows"]))]
        denom = list(c.execute(text(SQL["denominator"])))[0][0]

    print()
    print("clinical_pathology distinct genes (all 20 types): %d" % denom)

    # ⚠⚠ REPORTED SEPARATELY AND NEVER POOLED — two different mechanisms.
    _report("XA1/XA3 — REFUSED: no burden counterpart exists", REFUSED, rows)
    _report("⚠ SEPARATE — UNCERTAIN: a grouping decision, not a missing count", UNCERTAIN, rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
