"""jobs.tier: the fold tier a worker must match to claim the job (F-035)

⚠⚠ WHY A COLUMN AND NOT A JOIN. The tier lives in `protein_analyses.meta['tier']`, and the claim is
one atomic `UPDATE … FOR UPDATE SKIP LOCKED` statement. Reaching the tier through JSON inside that
statement would need `meta->>'tier'` on Postgres and `json_extract(meta,'$.tier')` on SQLite — and
this queue is tested on **both**. A dialect-split claim is the one statement in the system that must
not have two versions.

⚠ ADDITIVE AND NULLABLE, with **no server_default**. A default of `'local'` would be shorter and
wrong: it would make every future untagged job silently claimable by the local worker, which is
precisely the defect (`F-035`) this column exists to close. A null is a **CATEGORY** — *this job
declares no tier* — and it must be unclaimable by anyone rather than claimable by whoever asks
first.

⚠⚠ AND THAT MEANS THE BACKFILL IS NOT OPTIONAL. Once `claim()` filters on `tier = :tier`, a
null-tier row is claimable by nobody. Run at a moment measured to have **0 pending and 0 claimed
jobs**, so nothing could be stranded; `backfill_job_tier` is still unconditional over every row so
history stays queryable by tier, and `census_untranched_count`'s sibling —
`pending_jobs_with_no_tier` — exists so a null can never hide behind an idle worker.

Revision ID: 0009_job_tier
Revises: 0008_cohort_tranche
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009_job_tier"
down_revision: Union[str, None] = "0008_cohort_tranche"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("tier", sa.String(length=20), nullable=True))
    # ⚠ Indexed: `claim()` now filters on it on every poll, and the queue's FIFO order already
    # relies on an explicit ORDER BY rather than an index — this one is for the predicate.
    op.create_index("ix_jobs_tier", "jobs", ["tier"])

    # ⚠ Calls the shared backfill rather than inlining the UPDATE, so the migration and
    # `test_backfill_tags_every_existing_job` exercise the SAME code. A test that reimplements the
    # backfill proves only that two implementations agree (the 0008 precedent).
    from db.job_tier_backfill import backfill_job_tier

    backfill_job_tier(op.get_bind())


def downgrade() -> None:
    op.drop_index("ix_jobs_tier", table_name="jobs")
    op.drop_column("jobs", "tier")
