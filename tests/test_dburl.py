"""DATABASE_URL scheme normalization (db/dburl.py) — the pre-merge blocker.

Fly's Postgres attach writes a bare `postgresql://` URL, but the project pins the psycopg 3
driver (D-012), which SQLAlchemy only selects via the `postgresql+psycopg://` scheme — a bare
`postgresql://` makes SQLAlchemy reach for psycopg2, which is not installed. Normalizing in one
shared helper, applied by BOTH the app (`app/config.py`) and alembic (`db/migrations/env.py`),
means a future re-attach (which rewrites the secret back to `postgresql://`) cannot silently
break either the serving tier or the migration path again.
"""

from __future__ import annotations

import pytest

from db.dburl import normalize_db_url


@pytest.mark.parametrize("raw,expected", [
    # the attach's bare scheme → the pinned psycopg 3 driver
    ("postgresql://u:p@host:5432/db", "postgresql+psycopg://u:p@host:5432/db"),
    # the `postgres://` alias some tools emit → same
    ("postgres://u:p@host:5432/db",   "postgresql+psycopg://u:p@host:5432/db"),
    # already correct → unchanged (idempotent, so re-normalizing never doubles the driver)
    ("postgresql+psycopg://u:p@host:5432/db", "postgresql+psycopg://u:p@host:5432/db"),
])
def test_normalizes_to_psycopg_driver(raw, expected):
    assert normalize_db_url(raw) == expected


def test_preserves_credentials_port_path_and_query():
    raw = "postgresql://user:p%40ss@ep.internal:5432/pharmfold?sslmode=require"
    assert normalize_db_url(raw) == \
        "postgresql+psycopg://user:p%40ss@ep.internal:5432/pharmfold?sslmode=require"


def test_leaves_an_explicit_driver_alone():
    # An explicitly-chosen driver is respected, not rewritten to psycopg.
    assert normalize_db_url("postgresql+asyncpg://u:p@h/db") == "postgresql+asyncpg://u:p@h/db"


def test_leaves_non_postgres_urls_alone():
    assert normalize_db_url("sqlite://") == "sqlite://"
    assert normalize_db_url("sqlite:///./x.db") == "sqlite:///./x.db"


def test_app_config_applies_normalization(monkeypatch):
    from app.config import settings_from_env

    monkeypatch.setenv("WORKER_AUTH_TOKEN", "tok")
    monkeypatch.setenv("ARTIFACT_ROOT", "/data/artifacts")
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@host:5432/db")
    s = settings_from_env()
    assert s.database_url == "postgresql+psycopg://u:p@host:5432/db"
