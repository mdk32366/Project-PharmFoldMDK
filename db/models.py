"""SQLAlchemy models (D-012: Postgres prod, SQLite test DB).

Only the ``jobs`` table (D-009 §1) exists here for now. `protein_analyses` and the
rest of Database Plan v2 land in later PRs — see D-009 §1 Amendment 4 for why
`jobs.analysis_id` deliberately carries **no** foreign key yet.

The ORM class is ``JobRecord`` (the persistent row) to keep it distinct from
``core.queue.Job`` (the lightweight DTO the queue hands to callers) — two layers,
two names, no collision.

Cross-dialect note: ``inference_settings`` renders **JSONB on Postgres** and plain
JSON on SQLite via ``with_variant``, so the same model creates cleanly under the
SQLite test fixture (D-005) and under real Postgres.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# JSONB where it exists, JSON elsewhere. Keeps create_all working on SQLite.
JSON_VARIANT = JSON().with_variant(JSONB, "postgresql")


class Base(DeclarativeBase):
    pass


class JobRecord(Base):
    """A fold-queue row (D-009 §1). Transient operational state, deliberately kept
    separate from the durable ``protein_analyses`` record."""

    __tablename__ = "jobs"
    __table_args__ = (
        # D-009 §1: the claim query filters on status and orders by created_at.
        Index("ix_jobs_status_created", "status", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # FK CLOSED (D-009 §1 Amendment 4 → D-019): now that `protein_analyses` exists, the
    # constraint lands in the same migration that creates it (0002). The guard test that
    # asserted no-FK was confirmed to fail on the FK-exists assertion, then replaced with a
    # positive test.
    analysis_id: Mapped[int] = mapped_column(ForeignKey("protein_analyses.id"), index=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pending")
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    # ⚠ F-035 / D-107: the tier a worker must MATCH to claim this job. Values: local | rental |
    # msa | NULL. Nullable with no server_default — a default of 'local' would make every untagged
    # job silently claimable by the local worker, which is the defect this column closes. A null
    # is a category: *declares no tier*, claimable by nobody, and counted by
    # `pending_jobs_with_no_tier` so it cannot hide. `msa` is claimable; it is NOT a TIER_RECIPE
    # key (that table is ESMFold).
    tier: Mapped[str | None] = mapped_column(String(20), index=True)
    worker_id: Mapped[str | None] = mapped_column(String(64))
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error: Mapped[str | None] = mapped_column(Text)
    inference_settings: Mapped[dict] = mapped_column(JSON_VARIANT, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class RankingRun(Base):
    """One execution of the cohort ranking (D-015 §4). Versions the ranking a result
    belongs to, so a promoted/demoted target can be tied to the target-list and scorer
    that produced it (reproducibility, ARCHITECTURE §7). Created here so the schema
    anticipates ranking without retrofitting a live migration chain."""

    __tablename__ = "ranking_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    target_list_version: Mapped[str] = mapped_column(String(64))   # e.g. Kathad-82 revision
    scorer_version: Mapped[str] = mapped_column(String(64))        # the learned scorer's version
    # preregistered | sensitivity (D-065). The pre-registered run and the two ablation runs are
    # distinguished so the surface never serves a sensitivity run as the result (D-065 dec 4).
    # Defaults preregistered so migration 0006 backfills the existing runs correctly.
    run_kind: Mapped[str] = mapped_column(String(16), nullable=False, server_default="preregistered")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class ProteinAnalysis(Base):
    """The durable scientific record for one target's analysis (Database Plan §2.2) —
    distinct from the transient `jobs` row that produces it (D-009 §1)."""

    __tablename__ = "protein_analyses"
    __table_args__ = (
        Index("ix_protein_analyses_structure_source", "structure_source"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # FK DEFERRED, second instance (D-019): `users`/auth is unbuilt, so this stays a plain
    # nullable integer with no FK until the migration that creates `users` adds it — the same
    # pattern as analysis_id under Amendment 4. Column matches the plan so it is
    # forward-compatible; only the constraint waits.
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    input_type: Mapped[str] = mapped_column(String(20))            # uniprot | fasta | pdb_upload
    input_value: Mapped[str] = mapped_column(Text, default="")
    structure_source: Mapped[str] = mapped_column(String(30), default="")  # esmfold_local | alphafold_db | user_upload
    pdb_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    mean_plddt: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0–100
    pae_json_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    # "metadata" is reserved on the declarative Base, so the attribute is `meta` mapped to the
    # column name "metadata" (length, organism, gene, ECD bounds, UniProt provenance, …).
    meta: Mapped[dict] = mapped_column("metadata", JSON_VARIANT, nullable=False, default=dict)
    notes: Mapped[str] = mapped_column(Text, default="")
    ranking_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("ranking_runs.id"), nullable=True, index=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    # ⚠ THE COHORT TAG (D-079, migration 0008). NULLABLE BECAUSE A NULL IS A CATEGORY.
    # Untagged means *unclassified* — not a census member and **not** tranche zero. It carries no
    # `default` and no `server_default` on purpose: either would turn an absent value into a low
    # number, silently promoting an untagged row into the reported cohort. Existing rows are
    # backfilled to 0 explicitly by the migration, never by a default.
    # `protein_analyses` IS the cohort today, so every enumerating read filters on this column —
    # without it an ingest makes the target list silently become the census.
    cohort_tranche: Mapped[int | None] = mapped_column(
        Integer, nullable=True, index=True, default=None
    )


class ProteinFeatures(Base):
    """The six D-027 structure-derived features for one fold, computed offline by
    `core.features` and loaded by `scripts/extract_features.py` (D-058 decision 3).

    An ORM model (not migration-only like `analysis_embeddings`) because every column is a
    plain type — no pgvector — so it builds cleanly under both the SQLite `create_all` test
    path (D-005) and the real `0003` migration on Postgres.

    Six named nullable Float columns hold the features; `null_reasons` records **why** any of
    them is null (D-027's null-with-a-reason — *never* an imputed mean). `mean_plddt` and
    `below_plddt_floor` store the D-041 §5 floor decision as read from the fold, not recomputed.
    `feature_version` is D-027's source-hash pin, so a refit against changed feature code is
    detectable rather than silent. A row can exist with all six features null and a reason (a
    failed fold with an analysis row but no structure, e.g. IGF2R — D-058 Addendum 2 §1)."""

    __tablename__ = "protein_features"
    __table_args__ = (
        Index("ix_protein_features_analysis_id", "analysis_id"),
        Index("ix_protein_features_ranking_run_id", "ranking_run_id"),
        Index("ix_protein_features_extraction_outcome", "extraction_outcome"),
        # ⚠⚠ One fold, one feature vector (0010). Without this the loader's pure INSERT took 80
        # rows to 160 in two generations (F-021) and nothing was red. Declared HERE as well as in
        # the migration so the SQLite `create_all` test path enforces what Postgres enforces —
        # a constraint that exists only in the migration is untested by every test we run.
        UniqueConstraint("analysis_id", name="uq_protein_features_analysis_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("protein_analyses.id"), nullable=False
    )
    ranking_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("ranking_runs.id"), nullable=True, default=None
    )

    # D-027's six features (fixed count). Nullable — a target we failed on records null + reason.
    ecd_length: Mapped[float | None] = mapped_column(Float, nullable=True)                # 1
    radius_of_gyration: Mapped[float | None] = mapped_column(Float, nullable=True)        # 2 (length-normalised)
    mean_plddt_ecd: Mapped[float | None] = mapped_column(Float, nullable=True)            # 3
    membrane_proximal_plddt: Mapped[float | None] = mapped_column(Float, nullable=True)   # 4
    sasa_normalized: Mapped[float | None] = mapped_column(Float, nullable=True)           # 5
    largest_patch_fraction: Mapped[float | None] = mapped_column(Float, nullable=True)    # 6

    # Feature 7 (D-075, migration `0007`) — membrane-proximal SASA, coordinate-only. NOT one of
    # D-027's six and never on the pre-registered path; it exists for the named `geom_proxy`
    # ablation. Nullable, and null on every row written before D-075 — an honest "not computed
    # yet", never backfilled with a value (D-070 dec 2: a measurement may enter a field, an
    # inference never can).
    membrane_proximal_sasa: Mapped[float | None] = mapped_column(Float, nullable=True)   # 7

    # Why any feature is null (D-027): {feature_name: reason}. Empty when all six computed.
    null_reasons: Mapped[dict] = mapped_column(JSON_VARIANT, nullable=False, default=dict)

    # The D-041 §5 floor, stored as read from the fold — not recomputed (D-058 dec 3).
    mean_plddt: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0–100
    below_plddt_floor: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # ⚠ Why the extraction outcome is a COLUMN and not an entry in `null_reasons` (0010): a row
    # REFUSED at computation (D-079 amendment 1 ruling 6) and a row that FAILED to compute are
    # different facts that both present as nulls. Pooling them loses the one the ruling requires
    # be a category. Vocabulary lives in `scripts/census_extract_features.py::OUTCOMES`.
    extraction_outcome: Mapped[str | None] = mapped_column(String(40), nullable=True)

    feature_version: Mapped[str] = mapped_column(String(64), nullable=False, server_default="")
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class TargetScore(Base):
    """One ranked target's scorer output for one run (D-061 decision 1). The predicted probability
    (`score`), the six `β_k·x_k` attributions (`attributions`, JSON, D-041 dec 1), and the
    descending `rank`. Only ranking-set targets get a row — an excluded target is carried on the
    run result with its reason, never given a fabricated score."""

    __tablename__ = "target_scores"
    __table_args__ = (
        Index("ix_target_scores_ranking_run_id", "ranking_run_id"),
        Index("ix_target_scores_analysis_id", "analysis_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ranking_run_id: Mapped[int] = mapped_column(ForeignKey("ranking_runs.id"), nullable=False)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("protein_analyses.id"), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)              # predicted probability
    attributions: Mapped[list] = mapped_column(JSON_VARIANT, nullable=False, default=list)  # six β_k·x_k
    rank: Mapped[int] = mapped_column(Integer, nullable=False)               # 1 = highest score
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class RankingResult(Base):
    """The run-level pre-registered result for one scoring run (D-061 decision 2). D-041's headline
    is a *distribution*, so `structural_percentiles` (the LOO percentiles) is JSON, not a scalar;
    the head-to-head lives on one common reference set (D-060 dec 8); every denominator travels with
    the claim (D-024/D-041); and the excluded set carries its reasons (D-060 §3.5)."""

    __tablename__ = "ranking_results"
    __table_args__ = (
        Index("ix_ranking_results_ranking_run_id", "ranking_run_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ranking_run_id: Mapped[int] = mapped_column(ForeignKey("ranking_runs.id"), nullable=False)
    structural_percentiles: Mapped[list] = mapped_column(JSON_VARIANT, nullable=False, default=list)
    headto_structural_percentiles: Mapped[list] = mapped_column(JSON_VARIANT, nullable=False, default=list)
    headto_evidence_percentiles: Mapped[list] = mapped_column(JSON_VARIANT, nullable=False, default=list)
    spearman: Mapped[float | None] = mapped_column(Float, nullable=True)
    spearman_n: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    n_ranking_set: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    n_fit_positives: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    headto_reference_n: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    plddt_floor: Mapped[float | None] = mapped_column(Float, nullable=True)
    lambda_per_fold: Mapped[list] = mapped_column(JSON_VARIANT, nullable=False, default=list)
    lambda_at_grid_edge: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    excluded: Mapped[list] = mapped_column(JSON_VARIANT, nullable=False, default=list)  # [[symbol, reason], ...]
    scorer_version: Mapped[str] = mapped_column(String(64), nullable=False, server_default="")
    feature_version: Mapped[str] = mapped_column(String(64), nullable=False, server_default="")
    # survivorship status (D-064 dec 5) + the invalid-artifact marker (D-064 dec 3). Nullable so the
    # pre-D-064 row (id=1) reads NULL until the owner marks it, and migration 0005 adds them additively.
    loo_status: Mapped[str | None] = mapped_column(String(16), nullable=True)        # complete | partial | none
    fulldata_status: Mapped[str | None] = mapped_column(String(16), nullable=True)   # converged | raised
    status_detail: Mapped[str | None] = mapped_column(Text, nullable=True)           # reason for a blocked/invalid result
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class CensusStructuralRun(Base):
    """One computation of the CENSUS structural rank (D-144, migration 0012).

    ⚠⚠ **A SEPARATE STORE, AND THE SEPARATION IS THE DECISION.** `ranking_runs` /
    `target_scores` / `ranking_results` hold the **learned** cohort-82 scorer's pre-registered
    result (D-041 / D-060 / D-061, `run_kind='preregistered'`) and are **not touched** by this
    path — no new `run_kind`, no widened column, no 3,467 rows glued into a store shaped for 56.
    A shared table would have put a fixed arithmetic product and a fitted probability in one
    `score` column, one careless `ORDER BY` from being served as each other.

    ⚠ `run_status` is the served predicate: `valid` is served, `superseded` is what the previous
    valid run becomes when a new one lands (the idempotent replace), and `invalid` is a run the
    loader refused to certify. A run row always states which, so an unserved run is a category
    rather than an absence a reader has to explain.
    """

    __tablename__ = "census_structural_runs"
    __table_args__ = (
        Index("ix_census_structural_runs_status", "run_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # ⚠ `core.census_structural.formula_version()` — a hash of the formula module's SOURCE
    # (the D-027 `feature_version` pattern), never a hand-typed "v1". A run persisted under a
    # formula that has since changed is then detectable rather than silent.
    formula_version: Mapped[str] = mapped_column(String(64), nullable=False, server_default="")
    # The span definition the population's `span_aa` was measured under (D-081). The census is
    # V2; the cohort 82 is V1, and a row of one measured under the other is not comparable.
    span_definition: Mapped[str] = mapped_column(String(64), nullable=False, server_default="")
    # The committed file the POPULATION came from, and its hash (D-016 / D-024). The denominator
    # is a file, never a query against `protein_analyses` — that would make the population a
    # function of how much folding has happened.
    population_source: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    population_sha256: Mapped[str] = mapped_column(String(64), nullable=False, server_default="")
    run_status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="valid")
    status_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    # ⚠ CANDIDATES EXCLUDES THE REFERENCE SINK, and the two are stored separately because
    # "3,467 candidates" would count twelve already-taken antigens as things to go after.
    n_candidates: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    n_reference: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    n_with_fold: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    n_without_fold: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    # ⚠ The breakdown, not just the totals (method-note item 2): per-class, per-tranche and
    # per-flag counts, so a reader can see WHICH rows moved rather than that the total did.
    component_counts: Mapped[dict] = mapped_column(JSON_VARIANT, nullable=False, default=dict)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class CensusStructuralScore(Base):
    """One census protein's structural score for one run (D-144) — the product **and its three
    factors**, so a consumer never has to divide the total back apart (a span-unrecorded row
    would divide by zero) and so a reader can see which factor put a row where it is.

    ⚠ `analysis_id` is a NULLABLE FK: 777 manifest proteins have no `protein_analyses` row at
    all, and a null here is *never folded*, which is exactly what `has_fold: false` and the
    `no_fold` flag say on the same row. It is not a defect and it is not backfilled.

    ⚠ `is_reference` is an ORDERING fact, not a scoring one. `structural_score` on a reference
    row is computed the same way as on a candidate; the flag only sinks it below every candidate
    so a yardstick is never read as a next target.
    """

    __tablename__ = "census_structural_scores"
    __table_args__ = (
        Index("ix_census_structural_scores_run_rank", "run_id", "rank"),
        Index("ix_census_structural_scores_accession", "accession"),
        # ⚠⚠ ONE ROW PER PROTEIN PER RUN. Declared HERE as well as in migration 0012 so the
        # SQLite `create_all` test path enforces what Postgres enforces — F-021's lesson: a
        # loader's pure INSERT took `protein_features` from 80 rows to 160 and nothing was red.
        UniqueConstraint("run_id", "accession", name="uq_census_structural_scores_run_accession"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(
        ForeignKey("census_structural_runs.id"), nullable=False
    )
    accession: Mapped[str] = mapped_column(String(24), nullable=False)
    gene: Mapped[str | None] = mapped_column(String(48), nullable=True)
    census_class: Mapped[str | None] = mapped_column(String(24), nullable=True)
    tranche: Mapped[int | None] = mapped_column(Integer, nullable=True)
    span_aa: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_membrane: Mapped[float] = mapped_column(Float, nullable=False)
    score_ecd: Mapped[float] = mapped_column(Float, nullable=False)
    score_model: Mapped[float] = mapped_column(Float, nullable=False)
    structural_score: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)     # 1 = highest, references last
    has_fold: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
    mean_plddt: Mapped[float | None] = mapped_column(Float, nullable=True)   # 0–100, as read
    is_reference: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
    # `core.census_structural`'s row flags — every one a stated category, never an inference
    # from an absent value.
    flags: Mapped[list] = mapped_column(JSON_VARIANT, nullable=False, default=list)
    analysis_id: Mapped[int | None] = mapped_column(
        ForeignKey("protein_analyses.id"), nullable=True, default=None
    )


# NOTE: `analysis_embeddings` (embedding vector(384) + HNSW) is intentionally NOT an ORM model
# — it is created in migration 0002 as raw SQL only (D-019). Keeping the Postgres `vector` type
# out of Base.metadata is what lets the SQLite create_all test path stay clean and avoids adding
# a pgvector Python dependency. The pgvector path is exercised by the migration in the `postgres`
# CI job, which is where it should be proven.


class ClinicalPathology(Base):
    """EDGE 1 — protein → tumour, HPA v22 `pathology.tsv` IHC panel counts (`D-093`).

    ⚠⚠ SEVEN COLUMNS OF ELEVEN. The source carries four `prognostic-*` columns and they are
    deliberately absent: `D-093` amendment 1 clause 2 makes a prognostic column's PRESENCE the
    violation, because HPA redistributes TCGA-derived prognostics under bespoke User terms nobody
    here has read. The omission is the licence decision made structural, not an oversight.

    ⚠ Row-scoped to 3,466 gene names — the census MANIFEST ∪ the 82 cohort, not the folded
    census — so a protein folded later already has its edges. 67,280 of 401,800 source rows. This
    table does NOT answer questions about genes outside that union.
    """

    __tablename__ = "clinical_pathology"
    __table_args__ = (
        Index("ix_clinical_pathology_gene_name", "gene_name"),
        UniqueConstraint("gene_name", "cancer", name="uq_clinical_pathology_gene_cancer"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gene: Mapped[str] = mapped_column(String(24), nullable=False)          # ENSG
    gene_name: Mapped[str] = mapped_column(String(48), nullable=False)
    cancer: Mapped[str] = mapped_column(String(96), nullable=False)
    # ⚠ NOT NULL: an empty panel is 0/0/0/0 — `row_present_panel_empty`, a CATEGORY — never a null.
    high: Mapped[int] = mapped_column(Integer, nullable=False)
    medium: Mapped[int] = mapped_column(Integer, nullable=False)
    low: Mapped[int] = mapped_column(Integer, nullable=False)
    not_detected: Mapped[int] = mapped_column(Integer, nullable=False)


class ClinicalNormalTissue(Base):
    """EDGE 2 — protein → normal tissue, HPA v22 `normal_tissue.tsv` (`D-093` decision 5).

    ⚠ CO-EQUAL WITH EDGE 1, NOT AN APPENDIX. Amendment 2 ruling 2 ships them together; a tumour
    signal without its normal-tissue differential is the half that flatters a target.

    ⚠⚠ THE GRAIN CARRIES A DISTINCTION THE SURFACE NEEDS. `Not detected` is an explicit level;
    a MISSING (gene, tissue, cell type) row means the pair was never tested. Measured: 0 of 15,313
    genes cover all 266 pairs, so the grid is ragged and *tested-and-negative* vs *not tested* is a
    real difference (`TESTED_STATE`, ruling 6).
    """

    __tablename__ = "clinical_normal_tissue"
    __table_args__ = (
        Index("ix_clinical_normal_tissue_gene_name", "gene_name"),
        Index("ix_clinical_normal_tissue_tissue", "tissue"),
        UniqueConstraint("gene_name", "tissue", "cell_type",
                         name="uq_clinical_normal_tissue_grain"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gene: Mapped[str] = mapped_column(String(24), nullable=False)
    gene_name: Mapped[str] = mapped_column(String(48), nullable=False)
    tissue: Mapped[str] = mapped_column(String(64), nullable=False)
    cell_type: Mapped[str] = mapped_column(String(96), nullable=False)
    #: ⚠ one of `core.clinical_layer.LEVEL_VALUES`. Validated by the ingest against that module —
    #: a database CHECK here would be a second copy of the rule, and the two would drift.
    level: Mapped[str] = mapped_column(String(24), nullable=False)
    reliability: Mapped[str] = mapped_column(String(24), nullable=False)


class CancerBurdenRun(Base):
    """One ingest of the SEER official-aggregate US cancer burden artefact (`D-149`, migration
    0013).

    ⚠⚠ **THIS TABLE CARRIES NO PROTEIN, NO ACCESSION, NO GENE AND NO SCORE, AND THAT IS THE
    DECISION RATHER THAN AN OMISSION.** `D-093` decision 1 ruled burden a property of a **disease**,
    attached by traversal — never a protein-level column — and
    `tests/test_clinical_layer_prohibitions.py` already forbids the column on the protein path.
    There is **no foreign key from here to `protein_analyses`, to `census_structural_scores` or to
    `target_scores`**, so no `ORDER BY` can compose a cancer's death rate with a structural rank
    into one number. The absent join is the product decision.

    ⚠ `release` and `release_updated` pin WHICH SEER release this is — *SEER November 2025
    Submission*, application updated *2026-04-22*. A product name is not a version: `D-093`
    amendment 6 disqualified the Preliminary Incidence Estimates precisely because *the registry
    selection is re-derived each year while the product name never changes*.

    ⚠ `run_status` is the served predicate, on the `census_structural_runs` vocabulary: `valid` is
    served, `superseded` is what a previous valid run becomes when a new one lands, `invalid` is a
    run the loader refused to certify.
    """

    __tablename__ = "cancer_burden_runs"
    __table_args__ = (
        Index("ix_cancer_burden_runs_status", "run_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # ⚠⚠ THE SOURCE IS A COMMITTED FILE AND ITS HASH TRAVELS WITH THE RUN (D-016 / D-024). The
    # loader never touches the network; a figure that changed can therefore be told from a figure
    # that was re-loaded.
    source_file: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    source_sha256: Mapped[str] = mapped_column(String(64), nullable=False, server_default="")
    release: Mapped[str] = mapped_column(String(64), nullable=False, server_default="")
    release_updated: Mapped[str] = mapped_column(String(32), nullable=False, server_default="")
    # ⚠ US-ONLY, STORED. Not a UI string and not a template default — the disclaimer is a column so
    # a row cannot reach a consumer without it, and the API refuses to serve a run whose
    # geography_disclaimer is empty.
    geography: Mapped[str] = mapped_column(String(32), nullable=False, server_default="")
    geography_disclaimer: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    # ⚠ NCI attribution is a REQUIREMENT that survived the owner's 2026-09-09 closure of D-093
    # amendment 6's data-vs-text gap, so it is stored beside the figures rather than rendered
    # beside them.
    attribution: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    run_status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="valid")
    status_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    n_sites: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    n_stats: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    # ⚠ The breakdown, not the total (method-note item 2): per-statistic row counts, the distinct
    # periods actually present, and the count of rows whose sex the source substituted.
    component_counts: Mapped[dict] = mapped_column(JSON_VARIANT, nullable=False, default=dict)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class CancerBurdenStat(Base):
    """One SEER figure: one **(statistic, site, sex)** (`D-149`).

    ⚠⚠ **`period` AND `count_population` ARE PER-ROW COLUMNS, NOT RUN HEADERS, AND BOTH HAVE
    ALREADY EARNED IT.**

    - **`count_population`.** `observed_count` for `mortality` is a **national NCHS** count;
      for `incidence` it is a count **within the SEER registry catchment areas only**. Measured on
      the pinned release: Lung and Bronchus carries **662,721 deaths** and **434,448 new cases** —
      more deaths than cases, which is impossible in one population and merely two populations.
      **The two counts must never be compared to each other**; the age-adjusted rates are the
      comparable quantities. A run-level population field would have made that error invisible.
    - **`period`.** 81 of 87 mortality rows are 2020-2024; **`Kaposi Sarcoma` and `Mesothelioma`
      are 2019-2023**, which is what the source's own `year_range` code says for those sites. A
      header period would have relabelled six rows with a period they do not have.

    ⚠⚠ **`sex` IS PARSED FROM THE SOURCE'S RESPONSE, NEVER FROM THE REQUEST**, and
    `sex_substituted` records where the two differed. SEER*Explorer answers a Breast *"Both
    Sexes"* request with the **MALE** figure — rate 0.261793 / 2,457 deaths instead of 18.928734 /
    212,409 — so a pipeline that trusted its own request would have ranked breast cancer near the
    bottom of US cancer deaths on a rate 72x too small, with six decimal places and a confidence
    interval. `F-047`'s class.

    ⚠ `is_context_row` marks *All Cancer Sites Combined*, which is a **denominator** and contains
    every other site. It is stored so a consumer can show it and is flagged so no consumer ranks
    it beside its own components (`F-031`: two populations in one table).

    ⚠ `is_primary_sex_stratum` is the row a per-site view should show: the `both` row where the
    source publishes one, and otherwise every sex-specific row, each labelled. **No both-sexes
    rate is synthesised** — age-adjusted rates cannot be summed across sexes, and inventing one
    would be a number with no source.
    """

    __tablename__ = "cancer_burden_stat"
    __table_args__ = (
        Index("ix_cancer_burden_stat_run_statistic", "run_id", "statistic"),
        Index("ix_cancer_burden_stat_site", "seer_site_id"),
        # ⚠⚠ ONE ROW PER (run, statistic, site, sex) — F-021's guard, declared HERE as well as in
        # migration 0013 so the SQLite `create_all` test path enforces what Postgres enforces.
        UniqueConstraint("run_id", "statistic", "seer_site_id", "sex",
                         name="uq_cancer_burden_stat_grain"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("cancer_burden_runs.id"), nullable=False)
    #: `mortality` | `incidence` — the vocabulary lives in `core.cancer_burden`, not in a CHECK
    #: constraint here; a database copy of the rule is a second source that drifts.
    statistic: Mapped[str] = mapped_column(String(16), nullable=False)
    seer_site_id: Mapped[int] = mapped_column(Integer, nullable=False)
    #: SEER's OWN category name, carried verbatim. ⚠ `Melanoma of the Skin` is never relabelled
    #: "skin cancer": its recode group is literally *Skin excluding Basal and Squamous*, and BCC
    #: and SCC are not in SEER at all.
    site_label: Mapped[str] = mapped_column(String(96), nullable=False)
    recode_group: Mapped[str] = mapped_column(String(96), nullable=False)
    sex: Mapped[str] = mapped_column(String(8), nullable=False)
    rate_per_100k: Mapped[float] = mapped_column(Float, nullable=False)
    rate_se: Mapped[float | None] = mapped_column(Float, nullable=True)
    rate_lower_ci: Mapped[float | None] = mapped_column(Float, nullable=True)
    rate_upper_ci: Mapped[float | None] = mapped_column(Float, nullable=True)
    observed_count: Mapped[int] = mapped_column(Integer, nullable=False)
    count_population: Mapped[str] = mapped_column(String(32), nullable=False)
    period: Mapped[str] = mapped_column(String(16), nullable=False)
    rate_basis: Mapped[str] = mapped_column(String(64), nullable=False)
    sex_substituted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
    is_context_row: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
    is_primary_sex_stratum: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="0"
    )
