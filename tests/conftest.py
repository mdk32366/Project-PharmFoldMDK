"""Shared pytest fixtures for PharmFoldMDK.

Keel scaffolding (D-007): a dependency-free in-memory SQLite fixture that
proves the test-DB pattern from D-005. It uses the stdlib ``sqlite3`` module so
the suite stays green with only ``pytest`` installed; it will graduate to
SQLAlchemy / SQLModel sessions once database models exist. No application code
is imported here yet — see docs/README.md.
"""

import os
import re
import sqlite3

import pytest

# ⚠⚠ KEEL V8-a: the suite refuses to run against a database that is not disposable.
# The reasoning, the incident it comes from, and the loopback caveat live in
# `tests/_db_safety.py` — kept there because a guard nobody can test is a guard nobody can
# trust, and `refusal_reason()` is pure and env-injectable so it HAS tests.
from _db_safety import refusal_reason  # noqa: E402


def pytest_collection_modifyitems(config, items):
    reason = refusal_reason()
    if reason:
        # ⚠ A hard collection error, never a skip — a skip is what let a destructive suite
        # look harmless.
        raise pytest.UsageError(reason)


@pytest.fixture
def sqlite_conn():
    """A fresh in-memory SQLite database, isolated per test."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def pg_engine():
    """A real PostgreSQL engine for the D-017 integration tests.

    SKIPS unless ``DATABASE_URL`` names a reachable postgresql — so the normal
    ``test`` job (no DB, SQLite fixture) skips these, and only the ``postgres`` CI
    job (service container + ``alembic upgrade head``) runs them for real. The skip
    is the gate: a postgres-marked test cannot silently pass without a database.

    Assumes the schema already exists — the CI job applies migrations with
    ``alembic upgrade head`` (the real chain, NOT ``create_all``) before pytest, so
    these tests exercise the migrated schema. Each test gets a truncated table.
    """
    import os

    url = os.environ.get("DATABASE_URL", "")
    if not url.startswith("postgresql"):
        pytest.skip("no PostgreSQL DATABASE_URL — runs only in the `postgres` CI job (D-017)")

    from sqlalchemy import create_engine, text

    engine = create_engine(url, future=True)
    try:
        with engine.connect() as c:
            c.execute(text("SELECT 1"))
    except Exception as e:  # noqa: BLE001
        engine.dispose()
        pytest.skip(f"PostgreSQL not reachable: {e}")

    with engine.begin() as c:
        # CASCADE + all accumulating tables: jobs FK -> protein_analyses FK -> ranking_runs,
        # and analysis_embeddings FK -> protein_analyses (D-019). One clean slate per test.
        c.execute(text("TRUNCATE TABLE jobs, protein_analyses, ranking_runs RESTART IDENTITY CASCADE"))
    try:
        yield engine
    finally:
        engine.dispose()
