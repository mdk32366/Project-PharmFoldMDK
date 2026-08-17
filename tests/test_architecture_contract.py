"""D-051 — the architecture diagram is pinned to the running system, or it is decoration.

`ui/src/system-model.json` is the source `ArchitectureDiagram` renders. This functional test walks
the live FastAPI route table and asserts SET EQUALITY IN BOTH DIRECTIONS against the model's declared
routes: every live `/api`+`/jobs` route appears in the model, and every modelled route is live. A
route added (or removed) without updating the model reddens the gate — which is what converts the
diagram from a hand-drawn claim with no provenance into an artefact under the same discipline as
everything else here (D-016). Precedent for a Python test reading a non-Python artefact as its
subject: `tests/test_image_contents.py` reads the `Dockerfile`.

It also pins the load-bearing TOPOLOGY claim (D-004/DEP-001): inference runs on a GPU/worker tier
*outside* the Fly serving tier, and the Fly tier is GPU-free. A diagram that gets the routes right
and the topology backwards is worse than no diagram.

App built the way `tests/test_ui_serving.py` does (SQLite StaticPool + a dummy queue); no Postgres.
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.routing import APIRoute
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.main import create_app
from db.models import Base

MODEL_PATH = Path(__file__).resolve().parents[1] / "ui" / "src" / "system-model.json"


class _DummyQueue:
    def claim(self, worker_id, tier="local"):  # pragma: no cover - the contract test never touches the queue
        raise AssertionError("contract test must not touch the queue")


def _app():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False},
                        poolclass=StaticPool)
    Base.metadata.create_all(eng)
    return create_app(engine=eng, artifact_root="/tmp", auth_token="t",
                      queue=_DummyQueue(), ui_dir=None)


def _live_routes() -> set[tuple[str, frozenset]]:
    """Every `/api` + `/jobs` APIRoute as (path_template, methods). Path *templates*
    (`/api/analyses/{analysis_id}`), not resolved paths. Excludes `/openapi.json`, `/docs`,
    `/redoc`, the `/assets` mount and the SPA catch-all — none is an APIRoute under `/api`/`/jobs`."""
    out: set[tuple[str, frozenset]] = set()
    for r in _app().routes:
        if isinstance(r, APIRoute) and (r.path.startswith("/api") or r.path.startswith("/jobs")):
            methods = frozenset(m for m in r.methods if m not in ("HEAD", "OPTIONS"))
            out.add((r.path, methods))
    return out


def _model() -> dict:
    return json.loads(MODEL_PATH.read_text(encoding="utf-8"))


def _model_routes() -> set[tuple[str, frozenset]]:
    out: set[tuple[str, frozenset]] = set()
    for group in ("public_api", "worker_jobs"):
        for entry in _model()["routes"][group]:
            out.add((entry["path"], frozenset(entry["methods"])))
    return out


def test_every_live_route_is_modelled():
    """Adding a route without drawing it reddens here (the model omits a live route)."""
    missing = _live_routes() - _model_routes()
    assert not missing, (
        "live /api|/jobs routes MISSING from ui/src/system-model.json (draw them, D-051):\n  "
        + "\n  ".join(f"{p} {sorted(m)}" for p, m in sorted(missing))
    )


def test_every_modelled_route_is_live():
    """A modelled route that does not exist reddens here (the diagram claims fiction)."""
    fictional = _model_routes() - _live_routes()
    assert not fictional, (
        "FICTIONAL routes in ui/src/system-model.json (no live route — remove or fix):\n  "
        + "\n  ".join(f"{p} {sorted(m)}" for p, m in sorted(fictional))
    )


def test_topology_gpu_worker_is_outside_the_fly_serving_tier():
    """Pin the topology itself, not just the routes (D-004/DEP-001): inference runs on a GPU tier
    OUTSIDE Fly, and the Fly serving tier is GPU-free (no CUDA in the serving image)."""
    nodes = _model()["nodes"]
    gpu_nodes = [n for n in nodes if n.get("gpu")]
    fly_nodes = [n for n in nodes if n.get("zone") == "fly"]
    assert gpu_nodes, "the model must contain at least one GPU/worker node"
    inside = [n["id"] for n in gpu_nodes if n.get("zone") == "fly"]
    assert not inside, f"GPU node(s) drawn INSIDE the Fly serving tier (D-004 violated): {inside}"
    assert fly_nodes, "the model must contain the Fly serving tier"
    gpu_in_fly = [n["id"] for n in fly_nodes if n.get("gpu")]
    assert not gpu_in_fly, f"Fly serving tier must be GPU-free (DEP-001): {gpu_in_fly}"
