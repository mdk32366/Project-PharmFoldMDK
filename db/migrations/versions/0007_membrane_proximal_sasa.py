"""protein_features.membrane_proximal_sasa: feature 7, the confidence-blind proxy (D-075)

One ADDITIVE, NULLABLE column on `protein_features`. No `ALTER` of an existing column, no data
movement, **and deliberately no backfill** — every row written before D-075 stays NULL, which is the
honest "not computed yet". Feature 7 is derived from stored coordinates, so it *could* be recomputed
for the existing rows, but that is a job for `scripts/extract_features.py` (a measurement), never for
a migration inventing a value (D-070 dec 2: a measurement may enter a field, an inference never can).

⚠ **NULLABLE, unlike `0006`'s NOT NULL DEFAULT, and for a reason.** A server_default here would
backfill all 79 folded rows with a number that was never measured, and `scripts/fit_scorer.py` would
then fit `geom_proxy` on it as though it were data. NULL forces the extractor to run first; the
assembler prints a loud warning if a ranking-set row reaches it without feature 7.

⚠ **This column is NOT on the pre-registered path.** D-027's six features are the pre-registration
and D-075 dec 5 keeps the graded fit at six features / seven parameters. Feature 7 exists only for
the named `geom_proxy` ablation, and `core.features.FEATURE_NAMES` still has exactly six entries —
asserted by the gate, so this column cannot drift into the graded model by being added here.

⚠ VERIFY BY QUERY, NOT BY EXIT CODE (`docs/HAZARD-search-path-seams.md`): a `SET search_path` before
`begin_transaction()` once let a rolled-back upgrade exit 0. Confirm via
`information_schema.columns` after the upgrade; the `postgres` CI job runs the chain end to end.

⚠ DEPLOY ORDERING: the serving tier never reads or computes a feature (D-058 dec 3), so no deployed
route touches this column. It is safe to apply to prod at any time, before or after the code merges.

Revision ID: 0007_membrane_proximal_sasa
Revises: 0006_run_kind
Create Date: 2026-08-01
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007_membrane_proximal_sasa"
down_revision: Union[str, None] = "0006_run_kind"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "protein_features",
        sa.Column("membrane_proximal_sasa", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("protein_features", "membrane_proximal_sasa")
