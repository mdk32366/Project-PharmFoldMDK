"""The census feature ingest's three preconditions: uniqueness, an outcome, and a marker.

⚠⚠ THE UNIQUE CONSTRAINT IS THE POINT AND IT IS NOT COSMETIC. `F-021`'s first clause: the loader
is `session.add(ProteinFeatures(...))` — a pure INSERT, no upsert, no delete — and today NOTHING
stops it running twice. Measured against production before writing this: `protein_features`
carries a PK on `id` and two FKs and **no unique constraint**, and `ix_protein_features_
analysis_id` is NOT unique. A second ingest would have taken 80 rows to 160, then 240, silently,
and `fit_scorer`'s join would have started returning duplicate targets with nothing red.

⚠ Safe to enforce, checked rather than assumed: production holds **0** analyses with more than
one feature row, so the constraint can be added without a de-duplication step. If that is ever
false the migration FAILS LOUDLY at `create_unique_constraint`, which is the correct outcome — a
migration that silently drops rows to satisfy a constraint is worse than one that stops.

⚠ Features are a property of the STRUCTURE, not of a ranking run: one fold, one feature vector.
`ranking_run_id` stays on the row as provenance for which run loaded it, never as part of the
key — making it part of the key is what would license the second generation this constraint
exists to prevent.

⚠⚠ `extraction_outcome` GIVES THE REFUSAL A HOME. `D-079` amendment 1 ruling 6 requires the
`F-048` set to carry `refused_span_below_floor` as a **category, not a number, not a clamp, not
a None** — and before this column a refused row and a failed row were both just nulls with
reasons, indistinguishable. ⚠ *A value computed and then hidden is a value that will eventually
be exported*; so is a refusal recorded only as an absence.

⚠ ADDITIVE AND NULLABLE, then backfilled EXPLICITLY — the `0008` pattern, for the same reason. A
`server_default='ok'` would be shorter and wrong: it would make every future untagged row
silently a success, and the 80 existing cohort rows are `ok` as a matter of FACT (they were
extracted and their values verified reproducible), not as a matter of default.

⚠ `ingest_markers` is `GC4` idempotency, and it is GENERIC on purpose — keyed by
(ingest_name, source_path) so the clinical ingest reuses it rather than growing a second one.
`D-089` ruling 7's pattern: a second table for one artifact is a second source with nothing
comparing them.

Revision ID: 0010_feature_ingest
Revises: 0009_job_tier
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0010_feature_ingest"
down_revision: Union[str, None] = "0009_job_tier"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. one fold, one feature vector ──────────────────────────────────────
    op.create_unique_constraint(
        "uq_protein_features_analysis_id", "protein_features", ["analysis_id"]
    )

    # ── 2. the outcome vocabulary gets a column ──────────────────────────────
    op.add_column(
        "protein_features",
        sa.Column("extraction_outcome", sa.String(length=40), nullable=True),
    )
    # ⚠ UNCONDITIONAL backfill of every existing row. They are the 80 cohort rows, all extracted
    # successfully — re-extraction with current code reproduced them to a byte-identical whole-set
    # digest (82bec835…), so `ok` is measured, not assumed.
    op.execute(
        "UPDATE protein_features SET extraction_outcome = 'ok' "
        "WHERE extraction_outcome IS NULL"
    )
    op.create_index(
        "ix_protein_features_extraction_outcome", "protein_features", ["extraction_outcome"]
    )

    # ── 3. GC4: the ingest records its own completion, keyed to the SOURCE hash ──
    op.create_table(
        "ingest_markers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ingest_name", sa.String(length=80), nullable=False),
        sa.Column("source_path", sa.String(length=400), nullable=False),
        sa.Column("source_sha256", sa.String(length=64), nullable=False),
        sa.Column("rows_written", sa.Integer(), nullable=False),
        sa.Column("code_revision", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("completed_at", sa.DateTime(timezone=True),
                  server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("detail", sa.Text(), nullable=False, server_default=""),
        # ⚠ One marker per (ingest, source). A re-run against the SAME sha256 is a no-op; against a
        # DIFFERENT one it is a NEW ingest and must say so rather than silently appending.
        sa.UniqueConstraint("ingest_name", "source_path", name="uq_ingest_markers_name_path"),
    )


def downgrade() -> None:
    op.drop_table("ingest_markers")
    op.drop_index("ix_protein_features_extraction_outcome", table_name="protein_features")
    op.drop_column("protein_features", "extraction_outcome")
    op.drop_constraint("uq_protein_features_analysis_id", "protein_features", type_="unique")
