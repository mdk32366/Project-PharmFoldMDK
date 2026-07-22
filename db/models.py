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

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Index, Integer, String, Text, func
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

# NOTE: `analysis_embeddings` (embedding vector(384) + HNSW) is intentionally NOT an ORM model
# — it is created in migration 0002 as raw SQL only (D-019). Keeping the Postgres `vector` type
# out of Base.metadata is what lets the SQLite create_all test path stay clean and avoids adding
# a pgvector Python dependency. The pgvector path is exercised by the migration in the `postgres`
# CI job, which is where it should be proven.
