"""create jobs table (D-009 §1 + Amendments 1-4)

The fold queue. Transient operational state, separate from the durable
`protein_analyses` record (D-009 §1).

NOT EXERCISED IN CI. The SQLite test suite builds schema with create_all (D-005),
not this chain, so this migration and db/models.py can drift undetected — the exact
JARVIS H2 shape D-012 §2 names. It is hand-written to match `JobRecord` and will be
verified only when the Postgres integration job exists (D-012 §5). Targets Postgres
16 (D-014).

`analysis_id` carries NO foreign key (D-009 §1 Amendment 4). The FK is added in the
same migration that creates `protein_analyses` — stated closure, not "later".

Revision ID: 0001_create_jobs
Revises:
Create Date: 2026-07-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0001_create_jobs"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        # FK DEFERRED (Amendment 4): plain indexed integer, no ForeignKey yet.
        sa.Column("analysis_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("worker_id", sa.String(length=64), nullable=True),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("inference_settings", JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_jobs_status_created", "jobs", ["status", "created_at"])
    op.create_index("ix_jobs_analysis_id", "jobs", ["analysis_id"])


def downgrade() -> None:
    op.drop_index("ix_jobs_analysis_id", table_name="jobs")
    op.drop_index("ix_jobs_status_created", table_name="jobs")
    op.drop_table("jobs")
