"""target_scores + ranking_results: where per-target scores and the pre-registered result live (D-061)

Two ADDITIVE tables, no `ALTER`, no backfill — the lowest-risk class (as `0003` was). Closes the
gap D-058 decision 3 left (it said scores "hang off ranking_runs", a run-level table with no
per-target rows). `target_scores` is per-(run, target); `ranking_results` is per-run and is the home
of D-041's headline *distribution* (a scalar column would discard it).

⚠ VERIFY BY QUERY, NOT BY EXIT CODE (`docs/HAZARD-search-path-seams.md`): confirm both tables via
`information_schema.tables` after the upgrade; the `postgres` CI job runs the chain. One prod
`alembic upgrade head` covers 0003 and 0004 together.

Both are plain ORM models (no pgvector) so they also build under the SQLite `create_all` test path.

Revision ID: 0004_scores
Revises: 0003_protein_features
Create Date: 2026-07-27
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0004_scores"
down_revision: Union[str, None] = "0003_protein_features"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_JSON = sa.JSON().with_variant(JSONB(), "postgresql")


def upgrade() -> None:
    op.create_table(
        "target_scores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ranking_run_id", sa.Integer(), sa.ForeignKey("ranking_runs.id"), nullable=False),
        sa.Column("analysis_id", sa.Integer(), sa.ForeignKey("protein_analyses.id"), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("attributions", _JSON, nullable=False, server_default=sa.text("'[]'")),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_target_scores_ranking_run_id", "target_scores", ["ranking_run_id"])
    op.create_index("ix_target_scores_analysis_id", "target_scores", ["analysis_id"])

    op.create_table(
        "ranking_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ranking_run_id", sa.Integer(), sa.ForeignKey("ranking_runs.id"), nullable=False),
        sa.Column("structural_percentiles", _JSON, nullable=False, server_default=sa.text("'[]'")),
        sa.Column("headto_structural_percentiles", _JSON, nullable=False, server_default=sa.text("'[]'")),
        sa.Column("headto_evidence_percentiles", _JSON, nullable=False, server_default=sa.text("'[]'")),
        sa.Column("spearman", sa.Float(), nullable=True),
        sa.Column("spearman_n", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("n_ranking_set", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("n_fit_positives", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("headto_reference_n", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("plddt_floor", sa.Float(), nullable=True),
        sa.Column("lambda_per_fold", _JSON, nullable=False, server_default=sa.text("'[]'")),
        sa.Column("lambda_at_grid_edge", sa.Boolean(), nullable=True),
        sa.Column("excluded", _JSON, nullable=False, server_default=sa.text("'[]'")),
        sa.Column("scorer_version", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("feature_version", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_ranking_results_ranking_run_id", "ranking_results", ["ranking_run_id"])


def downgrade() -> None:
    op.drop_table("ranking_results")
    op.drop_table("target_scores")
