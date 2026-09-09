"""The SEER official-aggregate US cancer burden surface gets its own two tables — `D-149`.

⚠⚠ **ADDITIVE, AND IT REACHES THE SCORING TABLES NOWHERE.** `ranking_runs`, `target_scores`,
`ranking_results`, `census_structural_runs` and `census_structural_scores` are not altered, widened,
renamed or backfilled, and **neither new table carries a foreign key to any of them** — nor to
`protein_analyses`, `clinical_pathology` or `clinical_normal_tissue`. There is no accession column,
no gene column and no score column anywhere in this migration. **The absent join is the product
decision, not a gap to be closed later:** `D-093` decision 1 ruled burden a property of a
**disease**, attached by traversal, never a protein-level column, and a shared key would be one
`JOIN` away from a "cancer × structure" composite this project has refused three times
(`D-143`, `D-144`, `D-146`).

⚠ Two tables, not one, on the `0012` reasoning: a surface needs the release pin, the US-only
disclaimer and the NCI attribution **before** it needs 174 figures, and the per-figure rows carry a
UNIQUE `(run_id, statistic, seer_site_id, sex)` so the loader physically cannot do what `F-021`
recorded — a pure INSERT that took `protein_features` from 80 rows to 160 across two generations
with nothing red.

⚠⚠ `period` and `count_population` are columns on the FIGURE, not on the run, and both have already
earned it on the pinned release:

- `Kaposi Sarcoma` and `Mesothelioma` return mortality for **2019-2023** while the other 32 sites
  return **2020-2024**. A run-level period would have relabelled six rows.
- a `mortality` count is **national** (NCHS) and an `incidence` count covers the **SEER registry
  catchment areas only**. Lung and Bronchus carries 662,721 deaths against 434,448 new cases —
  impossible in one population, ordinary in two. A run-level population would have hidden it.

Revision ID: 0013_cancer_burden
Revises: 0012_census_structural_rank
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0013_cancer_burden"
down_revision: Union[str, None] = "0012_census_structural_rank"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# JSONB on Postgres, JSON elsewhere — the `db/models.py` JSON_VARIANT rule, so this chain applies
# identically under the SQLite fixture and under real Postgres.
JSON_VARIANT = sa.JSON().with_variant(JSONB, "postgresql")


def upgrade() -> None:
    # ── the run: which SEER release this is, and the two obligations that travel with it ──
    op.create_table(
        "cancer_burden_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        # ⚠⚠ THE SOURCE IS A COMMITTED FILE AND ITS HASH TRAVELS WITH THE RUN (D-016 / D-024).
        # The loader never touches the network, so a figure that CHANGED is distinguishable from a
        # figure that was merely re-loaded.
        sa.Column("source_file", sa.Text(), nullable=False, server_default=""),
        sa.Column("source_sha256", sa.String(length=64), nullable=False, server_default=""),
        # ⚠ A PRODUCT NAME IS NOT A VERSION. D-093 amendment 6 disqualified the Preliminary
        # Incidence Estimates because its registry selection is re-derived each year while its
        # name never changes, so the release and its application date are both pinned.
        sa.Column("release", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("release_updated", sa.String(length=32), nullable=False, server_default=""),
        # ⚠⚠ US-ONLY IS A COLUMN, NOT A TEMPLATE STRING. A row cannot reach a consumer without its
        # disclaimer, and the read route refuses to serve a run whose disclaimer is empty.
        sa.Column("geography", sa.String(length=32), nullable=False, server_default=""),
        sa.Column("geography_disclaimer", sa.Text(), nullable=False, server_default=""),
        # ⚠ NCI attribution survived the owner's 2026-09-09 closure of D-093 amendment 6's
        # data-vs-text gap. It is stored beside the figures rather than only rendered beside them.
        sa.Column("attribution", sa.Text(), nullable=False, server_default=""),
        # valid | superseded | invalid — the `census_structural_runs` vocabulary, and likewise NOT
        # a CHECK constraint: a database copy of the rule is a second source that drifts.
        sa.Column("run_status", sa.String(length=16), nullable=False, server_default="valid"),
        sa.Column("status_detail", sa.Text(), nullable=True),
        sa.Column("n_sites", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("n_stats", sa.Integer(), nullable=False, server_default="0"),
        # per-statistic counts, the distinct periods actually present, and how many rows had their
        # sex substituted by the source (method-note item 2: prefer the breakdown to the total)
        sa.Column("component_counts", JSON_VARIANT, nullable=False),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index("ix_cancer_burden_runs_status", "cancer_burden_runs", ["run_status"])

    # ── the figures: one (statistic, site, sex), each carrying its OWN period and population ──
    op.create_table(
        "cancer_burden_stat",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("cancer_burden_runs.id"), nullable=False),
        # mortality | incidence — vocabulary in `core.cancer_burden`, not a CHECK here
        sa.Column("statistic", sa.String(length=16), nullable=False),
        sa.Column("seer_site_id", sa.Integer(), nullable=False),
        # ⚠ SEER's OWN category name, verbatim. `Melanoma of the Skin` is never relabelled "skin
        # cancer": its recode group is literally *Skin excluding Basal and Squamous*, and basal-
        # and squamous-cell carcinoma are not in SEER at all.
        sa.Column("site_label", sa.String(length=96), nullable=False),
        sa.Column("recode_group", sa.String(length=96), nullable=False),
        # ⚠⚠ PARSED FROM THE SOURCE'S RESPONSE KEY, NEVER FROM THE REQUEST — see `sex_substituted`.
        sa.Column("sex", sa.String(length=8), nullable=False),
        sa.Column("rate_per_100k", sa.Float(), nullable=False),
        sa.Column("rate_se", sa.Float(), nullable=True),
        sa.Column("rate_lower_ci", sa.Float(), nullable=True),
        sa.Column("rate_upper_ci", sa.Float(), nullable=True),
        sa.Column("observed_count", sa.Integer(), nullable=False),
        # ⚠⚠ PER-ROW, NOT PER-RUN. `us_total_nchs` is national; `seer_registries` is the catchment
        # area only. Comparing the two counts is the defect this column exists to make visible.
        sa.Column("count_population", sa.String(length=32), nullable=False),
        # ⚠⚠ PER-ROW, NOT PER-RUN. Kaposi Sarcoma and Mesothelioma mortality is 2019-2023 while
        # the other 32 sites are 2020-2024.
        sa.Column("period", sa.String(length=16), nullable=False),
        sa.Column("rate_basis", sa.String(length=64), nullable=False),
        # ⚠ the source answered a different sex than was asked for on this row
        sa.Column("sex_substituted", sa.Boolean(), nullable=False,
                  server_default=sa.text("false")),
        # ⚠ *All Cancer Sites Combined* — a DENOMINATOR that contains every other site. Flagged so
        # no consumer ranks it beside its own components (F-031: two populations in one table).
        sa.Column("is_context_row", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        # ⚠ the row a per-site view shows: `both` where the source publishes one, otherwise every
        # sex-specific row, each labelled. No both-sexes rate is ever synthesised.
        sa.Column("is_primary_sex_stratum", sa.Boolean(), nullable=False,
                  server_default=sa.text("false")),
        # ⚠⚠ ONE ROW PER (run, statistic, site, sex) — F-021's guard, in the migration AND in the
        # ORM so the SQLite test path enforces what Postgres enforces.
        sa.UniqueConstraint("run_id", "statistic", "seer_site_id", "sex",
                            name="uq_cancer_burden_stat_grain"),
    )
    op.create_index("ix_cancer_burden_stat_run_statistic", "cancer_burden_stat",
                    ["run_id", "statistic"])
    op.create_index("ix_cancer_burden_stat_site", "cancer_burden_stat", ["seer_site_id"])


def downgrade() -> None:
    op.drop_index("ix_cancer_burden_stat_site", table_name="cancer_burden_stat")
    op.drop_index("ix_cancer_burden_stat_run_statistic", table_name="cancer_burden_stat")
    op.drop_table("cancer_burden_stat")
    op.drop_index("ix_cancer_burden_runs_status", table_name="cancer_burden_runs")
    op.drop_table("cancer_burden_runs")
