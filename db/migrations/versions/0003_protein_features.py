"""protein_features: the six D-027 structure-derived features, persisted (D-058 dec 3)

Purely ADDITIVE (D-058): one new table, no `ALTER` on a populated table, no backfill, no
data movement — the lowest-risk migration class. `ranking_runs` and `protein_analyses`
already exist (0002) and are NOT touched here.

⚠ VERIFY BY QUERY, NOT BY EXIT CODE. `docs/HAZARD-search-path-seams.md` records
`alembic upgrade head` silently rolling back while exiting zero (a `search_path SET` before
`context.begin_transaction()` — fixed in env.py). A green exit is exactly what that failure
looked like. Confirm the table exists via `information_schema.tables` after the upgrade; the
`postgres` CI job exercises the whole chain end to end (D-017).

No pgvector, no exotic types — all plain columns — so unlike `analysis_embeddings` this table
is also an ORM model (`db.models.ProteinFeatures`) and builds under the SQLite `create_all`
test path (D-005).

Revision ID: 0003_protein_features
Revises: 0002_protein_analyses
Create Date: 2026-07-27
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_protein_features"
down_revision: Union[str, None] = "0002_protein_analyses"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "protein_features",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "analysis_id",
            sa.Integer(),
            sa.ForeignKey("protein_analyses.id"),
            nullable=False,
        ),
        sa.Column(
            "ranking_run_id",
            sa.Integer(),
            sa.ForeignKey("ranking_runs.id"),
            nullable=True,
        ),
        # D-027's six features (fixed count); nullable — a failed target records null + reason.
        sa.Column("ecd_length", sa.Float(), nullable=True),               # 1 ECD length
        sa.Column("radius_of_gyration", sa.Float(), nullable=True),       # 2 Rg, length-normalised
        sa.Column("mean_plddt_ecd", sa.Float(), nullable=True),           # 3 mean pLDDT over ECD
        sa.Column("membrane_proximal_plddt", sa.Float(), nullable=True),  # 4 C-terminal 25% pLDDT
        sa.Column("sasa_normalized", sa.Float(), nullable=True),          # 5 SASA, length-normalised
        sa.Column("largest_patch_fraction", sa.Float(), nullable=True),   # 6 largest accessible patch
        # Why any feature is null (D-027 null-with-a-reason — never an imputed mean). JSONB on PG.
        sa.Column(
            "null_reasons",
            sa.JSON().with_variant(
                sa.dialects.postgresql.JSONB(), "postgresql"
            ),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        # The D-041 §5 floor, stored as read from the fold, not recomputed (D-058 dec 3).
        sa.Column("mean_plddt", sa.Float(), nullable=True),
        sa.Column("below_plddt_floor", sa.Boolean(), nullable=True),
        sa.Column("feature_version", sa.String(length=64), nullable=False, server_default=""),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_protein_features_analysis_id", "protein_features", ["analysis_id"])
    op.create_index("ix_protein_features_ranking_run_id", "protein_features", ["ranking_run_id"])


def downgrade() -> None:
    op.drop_table("protein_features")
