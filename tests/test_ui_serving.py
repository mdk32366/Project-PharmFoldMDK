"""DEP-006 static-UI serving + route-ordering tests, written against the ruling.

The trap (orders §2a, amendment §1): a SPA catch-all that matches ``/api`` returns ``index.html``
with a 200 — no error, no red test, and the UI silently gets HTML where it expected JSON. With
D-038 there are now TWO API surfaces to break, so both are asserted separately (a partial mount
could serve one and swallow the other). Hermetic: a fake built-bundle dir (an ``index.html`` +
``assets/``) handed to ``create_app`` — no ``npm run build`` needed to prove the ordering.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.main import create_app
from db.models import Base

TOKEN = "test-secret-token"


class _DummyQueue:
    def claim(self, worker_id):  # pragma: no cover - reads never touch the queue
        raise AssertionError("a read route touched the queue")


@pytest.fixture
def engine():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False},
                        poolclass=StaticPool)
    Base.metadata.create_all(eng)
    return eng


@pytest.fixture
def ui_dir(tmp_path):
    """A fake built bundle — the shape `npm run build` produces (index.html + assets/)."""
    d = tmp_path / "ui_dist"
    (d / "assets").mkdir(parents=True)
    (d / "index.html").write_text(
        "<!doctype html><title>PharmFoldMDK</title><div id=root></div>", encoding="utf-8")
    (d / "assets" / "index-abc123.js").write_text("console.log('pharmfold ui')", encoding="utf-8")
    return str(d)


def _client(engine, ui_dir) -> TestClient:
    app = create_app(engine=engine, artifact_root="/tmp", auth_token=TOKEN,
                     queue=_DummyQueue(), ui_dir=ui_dir)
    return TestClient(app)


# ── route ordering: BOTH API surfaces return JSON, not index.html ─────────────

def test_api_analyses_returns_json_not_index_html(engine, ui_dir):
    r = _client(engine, ui_dir).get("/api/analyses")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/json")
    assert isinstance(r.json(), list)                    # the API's payload, not the SPA


def test_api_coverage_returns_json_not_index_html(engine, ui_dir):
    r = _client(engine, ui_dir).get("/api/coverage")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/json")
    assert r.json()["coverage"]["denominator"] == 82     # the API's payload, not the SPA


def test_unknown_api_path_404s_not_masked_by_spa(engine, ui_dir):
    # An unknown /api path must 404 — the SPA must NOT return index.html with a 200 and hide it.
    r = _client(engine, ui_dir).get("/api/does-not-exist")
    assert r.status_code == 404
    assert "PharmFoldMDK" not in r.text


def test_jobs_still_guarded_with_ui_mounted(engine, ui_dir):
    # the SPA catch-all must not swallow /jobs either — a real write route still 401s unauthed
    assert _client(engine, ui_dir).post("/jobs/claim", json={"worker_id": "w"}).status_code == 401


# ── the SPA itself ─────────────────────────────────────────────────────────────

def test_root_serves_the_spa(engine, ui_dir):
    r = _client(engine, ui_dir).get("/")
    assert r.status_code == 200 and "text/html" in r.headers["content-type"]
    assert "PharmFoldMDK" in r.text


def test_client_side_route_serves_index_html(engine, ui_dir):
    # a deep link the React router will own — index.html, not a 404 (SPA fallback)
    r = _client(engine, ui_dir).get("/target/1")
    assert r.status_code == 200 and "PharmFoldMDK" in r.text


def test_assets_are_served(engine, ui_dir):
    r = _client(engine, ui_dir).get("/assets/index-abc123.js")
    assert r.status_code == 200 and "pharmfold ui" in r.text


# ── no built bundle → API-only (dev + the hermetic API tests) ─────────────────

def test_no_bundle_means_api_only(engine):
    app = create_app(engine=engine, artifact_root="/tmp", auth_token=TOKEN,
                     queue=_DummyQueue(), ui_dir=None)
    client = TestClient(app)
    assert client.get("/api/analyses").status_code == 200    # API works with no UI
    assert client.get("/").status_code == 404                # nothing mounted at /
