"""D-119 — thin ADC-A read routes. Hermetic TestClient; no network, no Postgres."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.main import create_app
from db.models import Base


class _DummyQueue:
    def claim(self, worker_id, tier="local"):  # pragma: no cover
        raise AssertionError("ADC-A reads must not touch the queue")


def _client():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(eng)
    app = create_app(
        engine=eng, artifact_root="/tmp", auth_token="t",
        queue=_DummyQueue(), ui_dir=None,
    )
    return TestClient(app)


def test_list_adcs_is_open_and_equals_the_file():
    from core.adc_catalog import load_catalog

    r = _client().get("/api/adcs")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/json")
    body = r.json()
    assert body == load_catalog()
    assert body["scope"]["value"] == "fda_approved_only"
    assert len(body["adcs"]) == 15


def test_get_adc_by_id_and_unknown_404s():
    r = _client().get("/api/adcs/enfortumab-vedotin")
    assert r.status_code == 200
    row = r.json()
    assert row["id"]["value"] == "enfortumab-vedotin"
    assert row["application_number"]["value"] == "BLA761137"
    assert row["antigen"]["value"] == "NECTIN4"
    assert set(row["id"]) == {"value", "source", "as_of", "confidence"}

    missing = _client().get("/api/adcs/ifinatamab-deruxtecan")
    assert missing.status_code == 404
    assert missing.json()["detail"] == "unknown ADC"

    missing2 = _client().get("/api/adcs/not-a-drug")
    assert missing2.status_code == 404
