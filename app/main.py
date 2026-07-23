"""The transport app factory (D-031).

``create_app`` takes its collaborators explicitly — engine, artifact root, auth token,
and (optionally) a queue — and wires them onto ``app.state``. That is what lets the
identical route code run against real Postgres + ``PostgresJobQueue`` + a Fly Volume in
prod and against SQLite + a stub + a tmp dir in the hermetic tests, with no environment
branching inside the handlers. Prod builds its collaborators from the environment via
``app_from_env``; the Fly process serves that under uvicorn.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI

from app.config import settings_from_env
from app.read_routes import read_router
from app.routes import router


def create_app(*, engine: Any, artifact_root: str, auth_token: str,
               queue: Optional[Any] = None) -> FastAPI:
    """Build the transport app around explicit collaborators. ``queue`` defaults to the
    production ``PostgresJobQueue`` over ``engine``; tests inject a stub where SQLite
    cannot run ``claim``'s ``SKIP LOCKED`` (D-012 §3)."""
    if queue is None:
        from core.queue import PostgresJobQueue
        queue = PostgresJobQueue(engine)

    app = FastAPI(title="PharmFoldMDK transport", version="0.1.0")
    app.state.engine = engine
    app.state.queue = queue
    app.state.artifact_root = artifact_root
    app.state.auth_token = auth_token
    app.include_router(router)              # /jobs — bearer-guarded worker routes (D-031)
    app.include_router(read_router)         # /api  — public read routes (D-034)
    return app


def app_from_env() -> FastAPI:
    """Production entrypoint: build collaborators from the environment (D-031/D-012)."""
    from sqlalchemy import create_engine

    s = settings_from_env()
    engine = create_engine(s.database_url, future=True)
    return create_app(engine=engine, artifact_root=s.artifact_root, auth_token=s.auth_token)
