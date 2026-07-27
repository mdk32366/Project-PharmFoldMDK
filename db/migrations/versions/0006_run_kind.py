"""ranking_runs.run_kind: preregistered vs sensitivity (D-065)

One ADDITIVE column on `ranking_runs`, `NOT NULL DEFAULT 'preregistered'`, so the two existing runs
(the enqueue anchor id=1 and the pre-registered fit id=2) backfill to `preregistered` — id=2 is
therefore correctly tagged without hardcoding an id, and id=1 stays filtered out by validity anyway.
The two D-065 ablation runs are written with `run_kind='sensitivity'` by `scripts/fit_scorer.py
--ablate`, so D-062's `/api/ranking` (which filters `run_kind='preregistered'`) never serves one as
the result (D-065 dec 4).

⚠ VERIFY BY QUERY, NOT BY EXIT CODE (`docs/HAZARD-search-path-seams.md`): confirm the column via
`information_schema.columns` after the upgrade; the `postgres` CI job runs the chain.

⚠ DEPLOY ORDERING: the D-062 route reads `ranking_runs.run_kind` once this ships, so prod must have
this column BEFORE the D-065 code deploys. Additive default column — the currently-deployed code
(which does not reference `run_kind`) ignores it — so it is safe to apply to prod ahead of the merge.

Revision ID: 0006_run_kind
Revises: 0005_ranking_result_status
Create Date: 2026-07-29
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006_run_kind"
down_revision: Union[str, None] = "0005_ranking_result_status"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "ranking_runs",
        sa.Column("run_kind", sa.String(length=16), nullable=False, server_default="preregistered"),
    )


def downgrade() -> None:
    op.drop_column("ranking_runs", "run_kind")
