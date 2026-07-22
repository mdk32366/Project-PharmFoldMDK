"""DATABASE_URL scheme normalization (D-012 — psycopg 3).

Fly's Postgres attach writes a bare ``postgresql://`` secret, but the project installs the
psycopg 3 driver only (``psycopg[binary]``, D-012), which SQLAlchemy selects via the
``postgresql+psycopg://`` scheme — a bare ``postgresql://`` makes SQLAlchemy default to
psycopg2, which is not installed, and the connection fails at import.

This one helper is applied by BOTH the serving tier (``app/config.py``) and the migration
environment (``db/migrations/env.py``), so a future re-attach that rewrites the secret back to
``postgresql://`` cannot silently break either path again. Lives in ``db/`` — the natural home
for a connection concern, imported by both tiers without an app↔alembic coupling.
"""

from __future__ import annotations

# Bare schemes the attach (or common tooling) emits, which must carry the pinned driver.
_BARE_SCHEMES = ("postgresql://", "postgres://")
_TARGET_SCHEME = "postgresql+psycopg://"


def normalize_db_url(url: str) -> str:
    """Force the psycopg 3 driver onto a bare Postgres URL; leave everything else untouched.

    Idempotent: a URL that already names a driver (``postgresql+psycopg://``, or any explicit
    ``postgresql+...``) is returned unchanged, so re-normalizing never doubles the driver, and
    a non-Postgres URL (e.g. the SQLite test DSN) passes straight through.
    """
    if url.startswith("postgresql+"):     # an explicit driver was chosen — respect it
        return url
    for bare in _BARE_SCHEMES:
        if url.startswith(bare):
            return _TARGET_SCHEME + url[len(bare):]
    return url
