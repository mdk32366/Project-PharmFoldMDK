"""D-119 / D-124 — thin ADC catalog read routes. Hermetic TestClient; no network, no Postgres."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.main import create_app
from db.models import Base


class _DummyQueue:
    def claim(self, worker_id, tier="local"):  # pragma: no cover
        raise AssertionError("ADC catalog reads must not touch the queue")


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


def test_list_pipeline_is_open_and_equals_the_file():
    from core.adc_catalog import load_pipeline

    r = _client().get("/api/adcs/pipeline")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/json")
    body = r.json()
    assert body == load_pipeline()
    assert body["scope"]["value"] == "pipeline_investigational"
    assert body["scope"]["value"] != "fda_approved_only"
    assert "ifinatamab-deruxtecan" in [row["id"]["value"] for row in body["pipeline"]]


def test_get_pipeline_by_id_and_unknown_404s():
    r = _client().get("/api/adcs/pipeline/ifinatamab-deruxtecan")
    assert r.status_code == 200
    row = r.json()
    assert row["id"]["value"] == "ifinatamab-deruxtecan"
    assert row["antigen"]["value"] == "CD276"
    assert set(row["id"]) == {"value", "source", "as_of", "confidence"}

    missing = _client().get("/api/adcs/pipeline/enfortumab-vedotin")
    assert missing.status_code == 404
    assert missing.json()["detail"] == "unknown pipeline ADC"

    missing2 = _client().get("/api/adcs/pipeline/not-a-drug")
    assert missing2.status_code == 404


def test_get_access_is_open_and_carries_disclaimer():
    from core.adc_catalog import load_access

    r = _client().get("/api/adcs/access")
    assert r.status_code == 200
    body = r.json()
    assert body == load_access()
    disclaimer = body["disclaimer"]["value"].lower()
    assert "not medical advice" in disclaimer
    assert "not legal advice" in disclaimer
    assert "not a treatment recommendation" in disclaimer
    assert set(body["disclaimer"]) == {"value", "source", "as_of", "confidence"}


def test_approved_detail_still_404s_pipeline_ids():
    """Approved /api/adcs/{id} is unchanged: ifinatamab is not a v1 row."""
    r = _client().get("/api/adcs/ifinatamab-deruxtecan")
    assert r.status_code == 404
    assert r.json()["detail"] == "unknown ADC"
