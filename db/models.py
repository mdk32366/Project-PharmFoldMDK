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

from sqlalchemy import JSON, DateTime, Index, Integer, String, Text, func
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

    # FK DEFERRED (D-009 §1 Amendment 4): a plain indexed integer until the migration
    # that creates `protein_analyses` adds the constraint IN THAT SAME MIGRATION.
    # Intentionally NOT a ForeignKey — `test_analysis_id_has_no_fk_yet` guards this and
    # goes red when the FK lands, forcing the amendment to be closed out deliberately.
    analysis_id: Mapped[int] = mapped_column(Integer, index=True)

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
