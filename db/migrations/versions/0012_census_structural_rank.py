"""The census STRUCTURAL rank gets its own two tables — `D-144`.

⚠⚠ **ADDITIVE, AND IT TOUCHES THE LEARNED SCORER'S TABLES NOWHERE.** `ranking_runs`,
`target_scores` and `ranking_results` hold the cohort-82 pre-registered result (`D-041` /
`D-060` / `D-061`) and are not altered, widened, renamed or backfilled by this migration. There
is **no new `run_kind`** on `ranking_runs` either: `run_kind` distinguishes `preregistered` from
`sensitivity` *within one experiment on one population of 56 scored targets*, and reusing it for
3,467 census proteins under a fixed arithmetic formula would put a product and a fitted
probability in one `score` column, one careless `ORDER BY` from being served as each other.

⚠ Two tables, not one: a run's metadata is read on its own (a surface needs the disclaimer and
the denominators before it needs 3,467 rows), and the per-protein rows carry a UNIQUE
`(run_id, accession)` so the loader physically cannot do what `F-021` recorded — a pure INSERT
that took `protein_features` from 80 rows to 160 across two generations with nothing red.

⚠ `census_structural_scores.analysis_id` is a NULLABLE FK to `protein_analyses`: 777 manifest
proteins have never been folded and have no analysis row. The null is the fact, stated again on
the same row by `has_fold = false` and the `no_fold` flag.

Revision ID: 0012_census_structural_rank
Revises: 0011_clinical_edges
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0012_census_structural_rank"
down_revision: Union[str, None] = "0011_clinical_edges"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# JSONB on Postgres, JSON elsewhere — the `db/models.py` JSON_VARIANT rule, so this chain
# applies identically under the SQLite fixture and under real Postgres.
JSON_VARIANT = sa.JSON().with_variant(JSONB, "postgresql")


def upgrade() -> None:
    # ── the run: one computation of the rank, with its population and its denominators ──
    op.create_table(
        "census_structural_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        # a hash of `core/census_structural.py`'s source (D-027's pin), never a typed "v1"
        sa.Column("formula_version", sa.String(length=64), nullable=False, server_default=""),
        # ⚠ the span definition the population was measured under (D-081): census is V2
        sa.Column("span_definition", sa.String(length=64), nullable=False, server_default=""),
        # ⚠⚠ THE DENOMINATOR IS A FILE (D-024). Its path and its hash travel with the run, so a
        # later reader can tell a re-run of the same population from a run over a new one.
        sa.Column("population_source", sa.Text(), nullable=False, server_default=""),
        sa.Column("population_sha256", sa.String(length=64), nullable=False, server_default=""),
        # valid | superseded | invalid. ⚠ A vocabulary in `core.census_structural`, NOT a CHECK
        # constraint here — a database copy of the rule would be a second source that drifts
        # (the `clinical_normal_tissue.level` precedent, 0011).
        sa.Column("run_status", sa.String(length=16), nullable=False, server_default="valid"),
        sa.Column("status_detail", sa.Text(), nullable=True),
        # ⚠ candidates and references are SEPARATE counts: "3,467 candidates" would count twelve
        # antigens that already have an ADC pointed at them as things to go after.
        sa.Column("n_candidates", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("n_reference", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("n_with_fold", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("n_without_fold", sa.Integer(), nullable=False, server_default="0"),
        # the per-class / per-tranche / per-flag breakdown (method-note item 2: prefer the
        # breakdown to the total)
        sa.Column("component_counts", JSON_VARIANT, nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index("ix_census_structural_runs_status", "census_structural_runs", ["run_status"])

    # ── the rows: one protein, one run, the product AND its three factors ──────
    op.create_table(
        "census_structural_scores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.Integer(),
                  sa.ForeignKey("census_structural_runs.id"), nullable=False),
        sa.Column("accession", sa.String(length=24), nullable=False),
        sa.Column("gene", sa.String(length=48), nullable=True),
        sa.Column("census_class", sa.String(length=24), nullable=True),
        sa.Column("tranche", sa.Integer(), nullable=True),
        sa.Column("span_aa", sa.Integer(), nullable=True),
        # ⚠ the three factors are STORED, not recoverable by division: a span-unrecorded row has
        # score_ecd = 0, so `structural_score / score_ecd` divides by zero on 0-span rows.
        sa.Column("score_membrane", sa.Float(), nullable=False),
        sa.Column("score_ecd", sa.Float(), nullable=False),
        sa.Column("score_model", sa.Float(), nullable=False),
        sa.Column("structural_score", sa.Float(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("has_fold", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("mean_plddt", sa.Float(), nullable=True),
        # ⚠ an ORDERING fact, never a scoring one — a reference row's score is computed the same
        # way as a candidate's and stays comparable to it.
        sa.Column("is_reference", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("flags", JSON_VARIANT, nullable=False),
        # ⚠ NULLABLE: 777 manifest proteins have no analysis row at all (never folded).
        sa.Column("analysis_id", sa.Integer(),
                  sa.ForeignKey("protein_analyses.id"), nullable=True),
        # ⚠⚠ ONE ROW PER PROTEIN PER RUN — F-021's guard, declared in the migration AND in the
        # ORM so the SQLite test path enforces what Postgres enforces.
        sa.UniqueConstraint("run_id", "accession",
                            name="uq_census_structural_scores_run_accession"),
    )
    op.create_index("ix_census_structural_scores_run_rank", "census_structural_scores",
                    ["run_id", "rank"])
    op.create_index("ix_census_structural_scores_accession", "census_structural_scores",
                    ["accession"])


def downgrade() -> None:
    op.drop_index("ix_census_structural_scores_accession",
                  table_name="census_structural_scores")
    op.drop_index("ix_census_structural_scores_run_rank",
                  table_name="census_structural_scores")
    op.drop_table("census_structural_scores")
    op.drop_index("ix_census_structural_runs_status", table_name="census_structural_runs")
    op.drop_table("census_structural_runs")
