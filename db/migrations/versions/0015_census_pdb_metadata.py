"""Census experimental PDB metadata tables — `D-171`.

⚠⚠ **ADDITIVE. DOES NOT TOUCH structural_score / census_structural_* / ranking_*.**
Offline load only (scripts/census_pdb_metadata.py). Per-request PDBe for /api/census
is forbidden.

Revision ID: 0015_census_pdb_metadata
Revises: 0014_enqueue_identity_unique
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0015_census_pdb_metadata"
down_revision: Union[str, None] = "0014_enqueue_identity_unique"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSON_VARIANT = sa.JSON().with_variant(JSONB, "postgresql")


def upgrade() -> None:
    op.create_table(
        "census_pdb_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_status", sa.String(16), nullable=False),
        sa.Column("source", sa.String(64), nullable=False),
        sa.Column("n_accessions", sa.Integer(), nullable=False),
        sa.Column("n_present", sa.Integer(), nullable=False),
        sa.Column("n_absent", sa.Integer(), nullable=False),
        sa.Column("n_absent_no_ecd", sa.Integer(), nullable=False),
        sa.Column("n_span_absent", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_census_pdb_runs_status", "census_pdb_runs", ["run_status"])

    op.create_table(
        "census_pdb_accessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("census_pdb_runs.id"), nullable=False),
        sa.Column("accession", sa.String(16), nullable=False),
        sa.Column("pdb_status", sa.String(48), nullable=False),
        sa.Column("pdb_ids", JSON_VARIANT, nullable=False),
        sa.Column("pdb_best", JSON_VARIANT, nullable=True),
        sa.Column("entries", JSON_VARIANT, nullable=False),
        sa.UniqueConstraint("run_id", "accession", name="uq_census_pdb_accessions_run_acc"),
    )
    op.create_index("ix_census_pdb_accessions_run", "census_pdb_accessions", ["run_id"])
    op.create_index("ix_census_pdb_accessions_acc", "census_pdb_accessions", ["accession"])


def downgrade() -> None:
    op.drop_table("census_pdb_accessions")
    op.drop_table("census_pdb_runs")
