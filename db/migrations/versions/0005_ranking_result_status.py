"""ranking_results status fields: loo_status, fulldata_status, status_detail (D-064)

Three ADDITIVE nullable columns on `ranking_results`. `loo_status`/`fulldata_status` carry the
survivorship status of a scoring run (D-064 dec 5 — which pre-registered statistics were producible);
`status_detail` carries the human reason for any blocked statistic, and is also where the invalid
zero-positive artifact (`ranking_results` id=1) is MARKED by the owner after merge (D-064 dec 3).

Nullable ADD COLUMN on a table with one existing row (id=1) is the lowest-risk migration class — no
rewrite, no backfill, the existing row reads NULL until the owner marks it.

⚠ VERIFY BY QUERY, NOT BY EXIT CODE (`docs/HAZARD-search-path-seams.md`): confirm the columns via
`information_schema.columns` after the upgrade; the `postgres` CI job runs the chain.

Revision ID: 0005_ranking_result_status
Revises: 0004_scores
Create Date: 2026-07-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005_ranking_result_status"
down_revision: Union[str, None] = "0004_scores"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("ranking_results", sa.Column("loo_status", sa.String(length=16), nullable=True))
    op.add_column("ranking_results", sa.Column("fulldata_status", sa.String(length=16), nullable=True))
    op.add_column("ranking_results", sa.Column("status_detail", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("ranking_results", "status_detail")
    op.drop_column("ranking_results", "fulldata_status")
    op.drop_column("ranking_results", "loo_status")
