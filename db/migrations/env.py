"""Alembic migration environment (D-012, D-014).

The one non-boilerplate part is the **search_path seam** (D-012 §5a): pgvector on
the `pharmfoldmdk` database lives in the `extensions` schema, not `public`, so a
migration emitting a bare `vector(384)` would fail with `type "vector" does not
exist`. We put `extensions` on the search_path for the whole migration connection,
`public` first so our own tables are created there.

This is decided NOW, in the first migration's env, even though PR A creates no
vector column — because env.py shapes every migration's connection, and retrofitting
a search_path into a chain that already ran is the ugly, error-prone thing D-012 §5a
exists to avoid. It is dialect-guarded to Postgres (SQLite has neither schemas nor
the type), and it is unexercised in CI until the Postgres integration job exists —
the same honest gap as the migration chain itself.

The RUNTIME (app) connection needs the same search_path; that is a SEPARATE seam set
in the app's engine config later. This env covers migrations only — do not read one
as handling the other (D-012 §5a).
"""

from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool, text

from db.models import Base

config = context.config

# DB URL from the environment (D-014: the DIRECT connection, not the pooler).
_url = os.environ.get("DATABASE_URL")
if _url:
    config.set_main_option("sqlalchemy.url", _url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _set_search_path(connection) -> None:
    """D-012 §5a: make the `extensions` schema (pgvector) resolvable for the whole
    migration. Postgres-only — a no-op on SQLite, which has no schemas or `vector`.

    MUST be called INSIDE alembic's ``context.begin_transaction()`` block, not before
    it. Running this ``SET`` before alembic begins its transaction auto-opens a
    separate SQLAlchemy-2.0 transaction that alembic does not own and never commits —
    the migration then logs "Running upgrade …", exits 0, and the DDL silently rolls
    back on connection close (caught by the D-017 postgres job on its first run:
    `relation "jobs" does not exist` after a "successful" upgrade). Kept as its own
    function with this note so it is not moved back out.
    """
    if connection.dialect.name == "postgresql":
        connection.execute(text("SET search_path TO public, extensions"))


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            # Inside alembic's owned transaction — see _set_search_path's note. The
            # SET and the DDL then commit together.
            _set_search_path(connection)
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
