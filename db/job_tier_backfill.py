"""The `jobs.tier` backfill, as one function so the migration and the test run the SAME code.

⚠⚠ **IT TAKES A BIND, NEVER AN ENGINE**, and that is not a style preference — it is the rule
`db/tranche_backfill.py` was rewritten to encode after a helper that opened its own connection
deadlocked production against the migration's own `ACCESS EXCLUSIVE` lock, with zero other clients.
**A function that can create its own connection will.**

⚠ **The tier is resolved in PYTHON, not in SQL.** It lives in `protein_analyses.meta['tier']`, and
reaching it in SQL needs `meta->>'tier'` on Postgres and `json_extract(meta,'$.tier')` on SQLite.
This queue is tested on both, so a dialect-split statement here would mean the tested path and the
production path are different code. Reading the rows and writing back is slower and identical
everywhere.

⚠ **A job whose analysis declares no tier is left NULL, deliberately.** Guessing `'local'` for it
would make an unknown claimable — the exact defect (`F-035`) this column exists to close.
`pending_jobs_with_no_tier()` exists so that null can never hide behind an idle worker.
"""

from __future__ import annotations

from typing import Any

#: ⚠ Named here so the backfill and the claim path cannot disagree about the spelling.
LOCAL = "local"
RENTAL = "rental"


def _tier_of(meta: Any) -> str | None:
    """The tier a job's analysis declares, or `None`. ⚠ Never guesses and never defaults."""
    if not isinstance(meta, dict):
        return None
    tier = meta.get("tier")
    return tier if isinstance(tier, str) and tier.strip() else None


def backfill_job_tier(bind: Any) -> tuple[int, int]:
    """Copy each job's tier down from its analysis. Returns `(tagged, left_null)`.

    `bind` is a **Connection** (the migration passes `op.get_bind()`) or an **Engine** (tests).
    Given a Connection the writes run in the caller's transaction and **this does not commit** —
    the migration owns that transaction. Given an Engine it opens its own via `begin()`.

    ⚠ Idempotent: it touches only rows where `tier IS NULL`, so a second run writes nothing and an
    already-tagged job is never re-derived from a `meta` that may since have changed.
    """
    from sqlalchemy import select, update
    from sqlalchemy.engine import Connection

    from db.models import JobRecord, ProteinAnalysis

    def _run(conn: Any) -> tuple[int, int]:
        rows = conn.execute(
            select(JobRecord.id, ProteinAnalysis.meta)
            .join(ProteinAnalysis, JobRecord.analysis_id == ProteinAnalysis.id)
            .where(JobRecord.tier.is_(None))
        ).all()
        tagged = 0
        left_null = 0
        for job_id, meta in rows:
            tier = _tier_of(meta)
            if tier is None:
                # ⚠ Counted, not silently skipped. "No tier" is a finding about that row.
                left_null += 1
                continue
            conn.execute(update(JobRecord).where(JobRecord.id == job_id).values(tier=tier))
            tagged += 1
        return tagged, left_null

    if isinstance(bind, Connection):
        return _run(bind)
    with bind.begin() as conn:
        return _run(conn)


def pending_jobs_with_no_tier(bind: Any) -> int:
    """Pending jobs no worker can claim, because they declare no tier.

    ⚠⚠ **THE POINT OF THIS FUNCTION IS THAT THE NUMBER IS INVISIBLE OTHERWISE.** `claim()` filters
    on `tier = :tier`, so a null-tier row is claimed by nobody — and an idle worker beside a queue
    of unclaimable jobs looks **exactly** like an idle worker beside an empty queue. One is fine and
    the other is a stalled crank.
    """
    from sqlalchemy import func, select
    from sqlalchemy.engine import Connection

    from db.models import JobRecord

    stmt = (select(func.count()).select_from(JobRecord)
            .where(JobRecord.status == "pending").where(JobRecord.tier.is_(None)))
    if isinstance(bind, Connection):
        return int(bind.execute(stmt).scalar() or 0)
    with bind.begin() as conn:
        return int(conn.execute(stmt).scalar() or 0)
