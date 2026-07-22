"""protein_analyses + ranking_runs + jobs FK closure + pgvector (D-019)

Discharges three deferred obligations in ONE migration (Amendment 4 requires the FK
and its target together):
- D-009 §1 Amendment 4: add the deferred `jobs.analysis_id` FK -> protein_analyses.
- D-015 §4: `ranking_runs` + a nullable `protein_analyses.ranking_run_id` FK.
- D-017: exercise the pgvector `extensions`-schema path — the last unproven point —
  by creating `analysis_embeddings (embedding vector(384))`.

pgvector handling (D-012 §5a choice, made here): rely on env.py's `search_path` seam
(public, extensions), so a BARE `vector(384)` resolves. `CREATE SCHEMA/EXTENSION IF
NOT EXISTS` are idempotent no-ops on prod, where D-014 measured both already present.

NOT run on SQLite (create_all builds the test schema — D-005). `analysis_embeddings`
is deliberately migration-only (no ORM model) so the vector type never reaches SQLite.
Targets Postgres 16 (D-014); the `postgres` CI job now uses a pgvector image (D-019).

Revision ID: 0002_protein_analyses
Revises: 0001_create_jobs
Create Date: 2026-07-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0002_protein_analyses"
down_revision: Union[str, None] = "0001_create_jobs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ranking_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("target_list_version", sa.String(length=64), nullable=False),
        sa.Column("scorer_version", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "protein_analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        # user_id FK DEFERRED (D-019) — users/auth unbuilt; plain nullable int for now.
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("input_type", sa.String(length=20), nullable=False),
        sa.Column("input_value", sa.Text(), nullable=False, server_default=""),
        sa.Column("structure_source", sa.String(length=30), nullable=False, server_default=""),
        sa.Column("pdb_path", sa.Text(), nullable=True),
        sa.Column("mean_plddt", sa.Float(), nullable=True),
        sa.Column("pae_json_path", sa.Text(), nullable=True),
        sa.Column("metadata", JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("ranking_run_id", sa.Integer(), sa.ForeignKey("ranking_runs.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_protein_analyses_user_created", "protein_analyses", ["user_id", "created_at"])
    op.create_index("ix_protein_analyses_structure_source", "protein_analyses", ["structure_source"])
    op.create_index("ix_protein_analyses_ranking_run_id", "protein_analyses", ["ranking_run_id"])

    # Close D-009 §1 Amendment 4: the deferred FK, now that its target exists. The
    # `ix_jobs_analysis_id` index already exists (created by 0001, where analysis_id was
    # index=True) — 0002 adds only the constraint.
    op.create_foreign_key("fk_jobs_analysis_id", "jobs", "protein_analyses", ["analysis_id"], ["id"])

    # pgvector, exercised for real (D-017/D-019). Idempotent on prod (D-014).
    op.execute("CREATE SCHEMA IF NOT EXISTS extensions")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector SCHEMA extensions")
    # Bare vector(384): resolves via env.py's search_path seam (public, extensions).
    op.execute(
        """
        CREATE TABLE analysis_embeddings (
            id SERIAL PRIMARY KEY,
            analysis_id INTEGER REFERENCES protein_analyses(id),
            embedding vector(384)
        )
        """
    )
    op.execute(
        "CREATE INDEX ix_analysis_embeddings_hnsw "
        "ON analysis_embeddings USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS analysis_embeddings")
    op.drop_constraint("fk_jobs_analysis_id", "jobs", type_="foreignkey")
    # ix_jobs_analysis_id is 0001's, not ours — 0001's downgrade drops it.
    op.drop_table("protein_analyses")
    op.drop_table("ranking_runs")
    # Extension/schema left intact — prod owns them independently (D-014).
