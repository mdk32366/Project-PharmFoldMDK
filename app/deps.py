"""FastAPI dependencies for the transport routes (D-031).

The engine, queue, and artifact root are wired onto ``app.state`` by ``create_app`` so
the same route code serves prod (real Postgres + ``PostgresJobQueue`` + Fly Volume) and
the hermetic tests (SQLite + a stub queue + a tmp dir) with no branching in the handlers.

``require_token`` enforces the shared bearer token (D-031 §4) and is attached to EVERY
route via ``dependencies=[...]`` — asserted per route, so a route added later cannot
silently inherit no check (the property the auth test pins).
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import Header, HTTPException, Request


def get_engine(request: Request) -> Any:
    return request.app.state.engine


def get_queue(request: Request) -> Any:
    return request.app.state.queue


def get_artifact_root(request: Request) -> str:
    return request.app.state.artifact_root


def require_token(request: Request, authorization: Optional[str] = Header(default=None)) -> None:
    """Reject any request without exactly ``Authorization: Bearer <token>``. A label
    (`worker_id`) is not a credential (D-031 §4); this is the credential."""
    expected = request.app.state.auth_token
    if authorization != f"Bearer {expected}":
        raise HTTPException(status_code=401, detail="invalid or missing bearer token")
