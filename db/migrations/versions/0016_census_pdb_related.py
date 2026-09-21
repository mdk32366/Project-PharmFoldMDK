"""Additive pdb_related JSON on census_pdb_accessions — `D-172`.

Does not touch structural_score tables.

Revision ID: 0016_census_pdb_related
Revises: 0015_census_pdb_metadata
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0016_census_pdb_related"
down_revision: Union[str, None] = "0015_census_pdb_metadata"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSON_VARIANT = sa.JSON().with_variant(JSONB, "postgresql")


def upgrade() -> None:
    op.add_column(
        "census_pdb_accessions",
        sa.Column("pdb_related", JSON_VARIANT, nullable=False, server_default=sa.text("'[]'")),
    )


def downgrade() -> None:
    op.drop_column("census_pdb_accessions", "pdb_related")
