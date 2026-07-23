"""The transport app factory (D-031) + the static UI mount (DEP-006).

``create_app`` takes its collaborators explicitly — engine, artifact root, auth token,
and (optionally) a queue and a built-UI directory — and wires them onto ``app.state``. That
is what lets the identical route code run against real Postgres + ``PostgresJobQueue`` + a Fly
Volume in prod and against SQLite + a stub + a tmp dir in the hermetic tests, with no
environment branching inside the handlers. Prod builds its collaborators from the environment
via ``app_from_env``; the Fly process serves that under uvicorn.

The React bundle (DEP-006) is served by this same app under ``/`` — but the API routers are
registered FIRST, so ``/api`` and ``/jobs`` always match before the SPA fallback. A catch-all
that swallowed ``/api`` would return ``index.html`` with a 200 and break the read API silently
(the trap DEP-006 and the React orders name); ``_mount_ui`` is added last, and it 404s an
unknown ``/api``/``/jobs`` path rather than masking it with the SPA.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings_from_env
from app.read_routes import read_router
from app.routes import router


def _mount_ui(app: FastAPI, ui_dir: str) -> None:
    """Serve the built React bundle under ``/`` (DEP-006), registered AFTER the API routers so
    route ordering holds. No-op when the directory has no ``index.html`` — dev and the hermetic
    tests run without an ``npm run build``, and the API must serve fine on its own."""
    dist = Path(ui_dir)
    index = dist / "index.html"
    if not index.is_file():
        return
    assets = dist / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa(full_path: str) -> FileResponse:
        # /api and /jobs are registered before this catch-all, so their real routes match first.
        # An UNKNOWN /api or /jobs path must 404 — never be masked by the SPA returning index.html
        # with a 200 (route ordering, DEP-006).
        if full_path == "api" or full_path == "jobs" or full_path.startswith(("api/", "jobs/")):
            raise HTTPException(status_code=404)
        return FileResponse(index)


def create_app(*, engine: Any, artifact_root: str, auth_token: str,
               queue: Optional[Any] = None, ui_dir: Optional[str] = None) -> FastAPI:
    """Build the transport app around explicit collaborators. ``queue`` defaults to the
    production ``PostgresJobQueue`` over ``engine``; tests inject a stub where SQLite cannot run
    ``claim``'s ``SKIP LOCKED`` (D-012 §3). ``ui_dir``, when given and built, is served under
    ``/`` (DEP-006); omitted (the API-only tests) leaves the app API-only."""
    if queue is None:
        from core.queue import PostgresJobQueue
        queue = PostgresJobQueue(engine)

    app = FastAPI(title="PharmFoldMDK transport", version="0.1.0")
    app.state.engine = engine
    app.state.queue = queue
    app.state.artifact_root = artifact_root
    app.state.auth_token = auth_token
    app.include_router(router)              # /jobs — bearer-guarded worker routes (D-031/D-036)
    app.include_router(read_router)         # /api  — public read routes (D-034/D-038)
    if ui_dir:
        _mount_ui(app, ui_dir)              # /     — static React bundle, LAST (DEP-006)
    return app


def app_from_env() -> FastAPI:
    """Production entrypoint: build collaborators from the environment (D-031/D-012/DEP-006)."""
    from sqlalchemy import create_engine

    s = settings_from_env()
    engine = create_engine(s.database_url, future=True)
    # UI_DIR is where the Dockerfile's stage-2 COPY --from lands the built bundle (/srv/ui_dist).
    return create_app(engine=engine, artifact_root=s.artifact_root, auth_token=s.auth_token,
                      ui_dir=os.environ.get("UI_DIR", "/srv/ui_dist"))
