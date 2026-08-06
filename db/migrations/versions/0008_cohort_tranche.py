"""protein_analyses.cohort_tranche: the census tranche tag (D-079)

⚠ ADDITIVE AND NULLABLE. The column is added nullable with **no server_default**, then existing
rows are backfilled to tranche zero **explicitly**. A `server_default=0` would be shorter and
wrong: it would make every future untagged row silently a cohort member, and a null is a CATEGORY
here — untagged means *unclassified*, not tranche zero and not a census member.

⚠ THE BACKFILL IS UNCONDITIONAL — every existing row, with no `WHERE pdb_path IS NOT NULL`.
`protein_analyses` IS the cohort today, and skipping the fold-failed row (IGF2R, 2,491 aa, CUDA OOM)
would leave it null-tagged, hence excluded from every tranche-zero read, hence **silently absent
from the target list**. The reported cohort would quietly become 79 of 80 with nothing red.

⚠ It calls `db.tranche_backfill.backfill_tranche_zero` rather than inlining the UPDATE, so the
migration and `test_backfill_tags_every_existing_row` exercise the SAME code. A test that
reimplements the backfill proves only that two implementations agree.

Revision ID: 0008_cohort_tranche
Revises: 0007_membrane_proximal_sasa
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008_cohort_tranche"
down_revision: Union[str, None] = "0007_membrane_proximal_sasa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "protein_analyses",
        sa.Column("cohort_tranche", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_protein_analyses_cohort_tranche", "protein_analyses", ["cohort_tranche"]
    )

    # Backfill through the shared helper — the same function the test exercises.
    from db.tranche_backfill import backfill_tranche_zero

    tagged = backfill_tranche_zero(op.get_bind().engine)
    print(f"[0008] backfilled cohort_tranche=0 on {tagged} existing protein_analyses rows")


def downgrade() -> None:
    op.drop_index("ix_protein_analyses_cohort_tranche", table_name="protein_analyses")
    op.drop_column("protein_analyses", "cohort_tranche")
