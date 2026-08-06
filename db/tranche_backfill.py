"""The tranche-zero backfill, as one function so the migration and the test run the SAME code.

⚠ WHY THIS IS NOT INLINE IN THE MIGRATION.  A test that reimplements the backfill proves only that
two implementations agree, and 2026-08-06 recorded what that is worth: a verification sharing an
implementation with its subject will agree with it, and a verification *reimplementing* it proves
nothing about the code that actually runs.  The migration calls this; the test calls this.

⚠ THE PREDICATE IS DELIBERATELY UNCONDITIONAL.  It is `cohort_tranche IS NULL` — every existing row,
with **no** `WHERE pdb_path IS NOT NULL` and no filter of any kind.

The tempting version tags only rows that folded.  In production that skips exactly one row —
**IGF2R**, fold-failed at 2,491 aa (CUDA OOM) — leaving it with a null tag.  A null tag is a
CATEGORY, so the row is then excluded from every tranche-zero read and **silently vanishes from the
target list**: the reported cohort quietly becomes 79 of 80.  Nothing errors and nothing reddens.
That is the whole reason `test_backfill_tags_every_existing_row`'s fixture carries a null-`pdb_path`
row, and why the revert is proven against it.
"""

from __future__ import annotations

from typing import Any

TRANCHE_ZERO = 0


def backfill_tranche_zero(engine: Any) -> int:
    """Tag every currently-untagged `protein_analyses` row as tranche zero. Returns the row count.

    ⚠ Idempotent by construction: it touches only rows where `cohort_tranche IS NULL`, so a second
    run writes nothing. It never overwrites an existing tag — a row already assigned to a census
    tranche is not dragged back into the cohort.
    """
    from sqlalchemy import update
    from sqlalchemy.orm import Session

    from db.models import ProteinAnalysis

    with Session(engine) as s:
        result = s.execute(
            update(ProteinAnalysis)
            .where(ProteinAnalysis.cohort_tranche.is_(None))
            .values(cohort_tranche=TRANCHE_ZERO)
        )
        s.commit()
        return int(result.rowcount or 0)
