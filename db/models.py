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
    # ⚠ F-035: the tier a worker must MATCH to claim this job. Nullable with no server_default —
    # a default of 'local' would make every untagged job silently claimable by the local worker,
    # which is the defect this column closes. A null is a category: *declares no tier*, claimable
    # by nobody, and counted by `pending_jobs_with_no_tier` so it cannot hide.
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


# NOTE: `analysis_embeddings` (embedding vector(384) + HNSW) is intentionally NOT an ORM model
# — it is created in migration 0002 as raw SQL only (D-019). Keeping the Postgres `vector` type
# out of Base.metadata is what lets the SQLite create_all test path stay clean and avoids adding
# a pgvector Python dependency. The pgvector path is exercised by the migration in the `postgres`
# CI job, which is where it should be proven.
