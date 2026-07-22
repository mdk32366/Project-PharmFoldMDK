"""Transport settings, read from the environment on Fly (D-031).

Kept tiny and explicit: the shared bearer token (D-031 §4 — RULED terminal at
single-worker scale, not a placeholder), the Volume mount the artifacts are written
under, and the database URL. Nothing is defaulted that would let a missing secret pass
silently — the token has no default, so a mis-provisioned deploy fails loudly rather
than serving unauthenticated.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from db.dburl import normalize_db_url


@dataclass(frozen=True)
class Settings:
    auth_token: str        # shared bearer secret, worker→Fly (D-031 §4)
    artifact_root: str     # Fly Volume mount for fold artifacts
    database_url: str      # postgresql+psycopg://… (D-012), normalized from the raw secret


def settings_from_env() -> Settings:
    """Build settings from the process environment. Raises ``KeyError`` if the auth
    token or database URL is absent — a deliberate loud failure over a silent default.

    ``DATABASE_URL`` is normalized to the psycopg 3 scheme (D-012): Fly's attach writes a bare
    ``postgresql://``, which SQLAlchemy would route to the uninstalled psycopg2 — so a re-attach
    cannot silently break the serving tier."""
    return Settings(
        auth_token=os.environ["WORKER_AUTH_TOKEN"],
        artifact_root=os.environ.get("ARTIFACT_ROOT", "/data/artifacts"),
        database_url=normalize_db_url(os.environ["DATABASE_URL"]),
    )
