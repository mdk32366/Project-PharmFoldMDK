"""The two clinical edges: protein → tumour (IHC) and protein → normal tissue.

`D-093` amendment 2 ruling 2: **edges 1 and 2 ship together.** Decision 5 makes the normal-tissue
differential **co-equal, not an appendix**, so one table without the other is a deviation from a
ruling and would have to be written as one.

⚠⚠ COLUMN-SCOPED, AND THE OMISSION IS THE POINT. `pathology.tsv` v22 carries ELEVEN columns; four
of them are `prognostic - favorable`, `unprognostic - favorable`, `prognostic - unfavorable`,
`unprognostic - unfavorable`. **They are not here.** `D-093` amendment 1 clause 2 makes a
prognostic column's PRESENCE the violation — HPA redistributes TCGA-derived prognostics under
bespoke User terms nobody on this project has read — and `tests/test_clinical_layer_prohibitions.py`
matches the token `prognos` against every stored delimited file. **Seven of eleven columns land;
the four that do not are the licence decision made structural.**

⚠⚠ ROW-SCOPED, AND THAT IS A SCOPE DECISION RATHER THAN A DETAIL.
Measured: `pathology.tsv` holds 401,800 rows over 20,082 genes and `normal_tissue.tsv` 1,194,479
over 15,313. Scoped to this project's genes that is **67,280 + 180,272 = 247,552 rows, 16% of the
source.**

⚠ THE SCOPE KEY IS THE CENSUS **MANIFEST**, NOT THE FOLDED CENSUS — 3,466 gene names from the
committed CSVs (manifest identity resolution ∪ labels ∪ the 82 cohort), against 2,687 gene names
on the 2,690 FOLDED rows. **Deliberately the wider set**, so a protein folded later (tranche 5's
776) already has its clinical edges rather than needing a second ingest. ⚠ An earlier draft of this
file said 2,726 genes and 187,087 rows — that was the folded figure, and it was wrong for what the
ingest actually does. Corrected against the measurement rather than left to be discovered.

⚠ **These tables do NOT answer questions about genes outside that union**, and a reader who forgets
it will read an absent gene as an absent measurement. The ingest records the scope and its key in
`ingest_markers.detail`; `ihc_gene_absent` is only meaningful against the same key.

⚠ The `Level` vocabulary is NOT a CHECK constraint. `core/clinical_layer.py` declares the eight
values and raises `UnhandledLevel` on a ninth — a database CHECK would be a second copy of that
rule, and the two would drift. The ingest validates against the module.

Revision ID: 0011_clinical_edges
Revises: 0010_feature_ingest
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0011_clinical_edges"
down_revision: Union[str, None] = "0010_feature_ingest"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── EDGE 1 — protein → tumour, by IHC panel counts ───────────────────────
    op.create_table(
        "clinical_pathology",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("gene", sa.String(length=24), nullable=False),          # ENSG
        sa.Column("gene_name", sa.String(length=48), nullable=False),
        sa.Column("cancer", sa.String(length=96), nullable=False),
        # the four IHC counts. ⚠ NOT NULL: a panel with no patients is 0/0/0/0, which is
        # `row_present_panel_empty` (a category), never a null.
        sa.Column("high", sa.Integer(), nullable=False),
        sa.Column("medium", sa.Integer(), nullable=False),
        sa.Column("low", sa.Integer(), nullable=False),
        sa.Column("not_detected", sa.Integer(), nullable=False),
        # ⚠ one row per (gene, cancer) — the grain D-100 reproduces against.
        sa.UniqueConstraint("gene_name", "cancer", name="uq_clinical_pathology_gene_cancer"),
    )
    op.create_index("ix_clinical_pathology_gene_name", "clinical_pathology", ["gene_name"])

    # ── EDGE 2 — protein → normal tissue, by IHC level ───────────────────────
    op.create_table(
        "clinical_normal_tissue",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("gene", sa.String(length=24), nullable=False),
        sa.Column("gene_name", sa.String(length=48), nullable=False),
        sa.Column("tissue", sa.String(length=64), nullable=False),
        sa.Column("cell_type", sa.String(length=96), nullable=False),
        # ⚠ one of the eight values core/clinical_layer.py declares. Four are ORDINAL
        # (Not detected < Low < Medium < High) and four are NOT (N/A, Ascending, Descending,
        # Not representative) — comparing across that boundary raises IncomparableEdges.
        sa.Column("level", sa.String(length=24), nullable=False),
        sa.Column("reliability", sa.String(length=24), nullable=False),
        # ⚠⚠ THE GRAIN IS (gene, tissue, cell type) AND THE RAGGEDNESS IS LOAD-BEARING.
        # 0 of 15,313 genes cover all 266 (tissue, cell) pairs, so a MISSING row means
        # `not_tested` while an explicit `Not detected` means `tested_not_detected`. Two
        # different facts (ruling 6); this constraint keeps the grain that distinguishes them.
        sa.UniqueConstraint("gene_name", "tissue", "cell_type",
                            name="uq_clinical_normal_tissue_grain"),
    )
    op.create_index("ix_clinical_normal_tissue_gene_name", "clinical_normal_tissue", ["gene_name"])
    op.create_index("ix_clinical_normal_tissue_tissue", "clinical_normal_tissue", ["tissue"])


def downgrade() -> None:
    op.drop_index("ix_clinical_normal_tissue_tissue", table_name="clinical_normal_tissue")
    op.drop_index("ix_clinical_normal_tissue_gene_name", table_name="clinical_normal_tissue")
    op.drop_table("clinical_normal_tissue")
    op.drop_index("ix_clinical_pathology_gene_name", table_name="clinical_pathology")
    op.drop_table("clinical_pathology")
