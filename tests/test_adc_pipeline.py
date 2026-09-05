"""D-124 — ADC-C-A pipeline + access tests, written so they can go red.

Hermetic: the committed files and tmp fixtures. No network. No Postgres.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.adc_catalog import (
    ACCESS_V1,
    CATALOG_V1,
    CONFIDENCES,
    DEVELOPMENT_STAGES,
    FIELD_KEYS,
    PHASE_VOCAB,
    PIPELINE_FIELDS,
    PIPELINE_V1,
    CatalogError,
    get_pipeline_adc,
    load_access,
    load_catalog,
    load_pipeline,
)

ROOT = Path(__file__).resolve().parents[1]


def _envelope(**overrides):
    base = {
        "value": "x",
        "source": "fixture",
        "as_of": "2026-09-05",
        "confidence": "reviewed",
    }
    base.update(overrides)
    return base


def _minimal_pipeline_row(adc_id="fixture-pipeline"):
    return {
        "id": _envelope(value=adc_id, confidence="derived"),
        "name": _envelope(value=adc_id),
        "antigen": _envelope(value="X"),
        "uniprot_accession": _envelope(value="P00000"),
        "development_stage": _envelope(value="clinical"),
        "phase": _envelope(value="Phase 1"),
        "source_citation": _envelope(value="fixture citation"),
    }


def _minimal_pipeline(rows=None):
    return {
        "catalog_id": _envelope(value="adcs.pipeline.v1", confidence="derived"),
        "schema_version": _envelope(value="1", confidence="derived"),
        "scope": _envelope(value="pipeline_investigational"),
        "completeness": _envelope(value="floor_not_census"),
        "mapping_sourced_as_of": _envelope(value="2026-07-27"),
        "catalog_assembled_as_of": _envelope(value="2026-09-05", confidence="derived"),
        "pipeline": rows if rows is not None else [_minimal_pipeline_row()],
    }


def _write(path, obj):
    path.write_text(json.dumps(obj), encoding="utf-8")
    return path


def test_d124_entry_exists_in_the_living_log():
    """The check is the heading, not a citation of it (D-062 / method-note item 7)."""
    log = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    assert "### D-124 — ADC-C-A:" in log
    assert "pipeline_investigational" in log
    assert "NOT medical advice" in log or "NOT medical" in log


def test_committed_pipeline_every_field_is_an_envelope():
    data = load_pipeline()
    for name in (
        "catalog_id", "schema_version", "scope", "completeness",
        "mapping_sourced_as_of", "catalog_assembled_as_of",
    ):
        assert set(data[name].keys()) == set(FIELD_KEYS)
        assert data[name]["confidence"] in CONFIDENCES
    for row in data["pipeline"]:
        assert set(row) == set(PIPELINE_FIELDS)
        for name, field in row.items():
            assert set(field.keys()) == set(FIELD_KEYS), name
            assert field["confidence"] in CONFIDENCES, name
            assert field["value"] not in (None, "")
            assert field["source"] and field["as_of"]


def test_committed_pipeline_scope_is_not_approved():
    data = load_pipeline()
    assert data["scope"]["value"] == "pipeline_investigational"
    assert data["scope"]["value"] != "fda_approved_only"
    assert data["completeness"]["value"] == "floor_not_census"
    approved = {r["id"]["value"] for r in load_catalog()["adcs"]}
    pipeline_ids = [r["id"]["value"] for r in data["pipeline"]]
    assert "ifinatamab-deruxtecan" in pipeline_ids
    assert not (set(pipeline_ids) & approved)
    for row in data["pipeline"]:
        assert row["development_stage"]["value"] in DEVELOPMENT_STAGES
        assert row["development_stage"]["value"] != "approved"
        assert row["phase"]["value"] in PHASE_VOCAB


def test_committed_catalogs_are_separate_files():
    """v1 is not the pipeline file; pipeline is not merged into v1."""
    assert CATALOG_V1 != PIPELINE_V1
    assert CATALOG_V1.name == "adcs.v1.json"
    assert PIPELINE_V1.name == "adcs.pipeline.v1.json"
    assert ACCESS_V1.name == "access.v1.json"
    v1 = json.loads(CATALOG_V1.read_text(encoding="utf-8"))
    pipe = json.loads(PIPELINE_V1.read_text(encoding="utf-8"))
    assert v1["scope"]["value"] == "fda_approved_only"
    assert pipe["scope"]["value"] == "pipeline_investigational"
    assert "pipeline" not in v1
    assert "adcs" not in pipe
    v1_ids = [r["id"]["value"] for r in v1["adcs"]]
    assert "ifinatamab-deruxtecan" not in v1_ids


def test_committed_pipeline_refuses_invented_science_keys():
    raw = json.loads(PIPELINE_V1.read_text(encoding="utf-8"))
    text = json.dumps(raw).lower()
    for banned in (
        '"dar"', '"ic50"', '"orr"', '"pfs"', '"os"',
        '"payload"', '"linker"', '"indication"', '"efficacy"', '"response_rate"',
    ):
        assert banned not in text, banned


def test_committed_access_disclaimer_is_present():
    data = load_access()
    for name, field in data.items():
        assert set(field.keys()) == set(FIELD_KEYS), name
        assert field["confidence"] in CONFIDENCES, name
    disclaimer = data["disclaimer"]["value"].lower()
    assert "not medical advice" in disclaimer
    assert "not legal advice" in disclaimer
    assert "not a treatment recommendation" in disclaimer
    assert data["scope"]["value"] == "trials_and_right_to_try_informational"
    assert data["completeness"]["value"] == "floor_not_census"
    assert "clinicaltrials.gov" in data["clinical_trials_registry"]["value"].lower()
    assert "360bbb-0a" in data["right_to_try_statute"]["value"]


def test_get_pipeline_adc_unknown_is_none():
    assert get_pipeline_adc("not-an-adc") is None
    assert get_pipeline_adc("enfortumab-vedotin") is None
    row = get_pipeline_adc("ifinatamab-deruxtecan")
    assert row["antigen"]["value"] == "CD276"
    assert row["phase"]["value"] == "BLA/NDA submitted"


def test_bare_string_field_is_rejected(tmp_path):
    pipe = _minimal_pipeline()
    pipe["pipeline"][0]["name"] = "not-an-envelope"
    with pytest.raises(CatalogError, match="not a"):
        load_pipeline(_write(tmp_path / "p.json", pipe))


def test_phase_vocab_is_rejected(tmp_path):
    pipe = _minimal_pipeline()
    pipe["pipeline"][0]["phase"] = _envelope(value="Phase 4")
    with pytest.raises(CatalogError, match="closed vocab"):
        load_pipeline(_write(tmp_path / "p.json", pipe))
    pipe["pipeline"][0]["phase"] = _envelope(value="preclinical")
    with pytest.raises(CatalogError, match="closed vocab"):
        load_pipeline(_write(tmp_path / "p.json", pipe))
    pipe["pipeline"][0]["phase"] = _envelope(value="approved")
    with pytest.raises(CatalogError, match="closed vocab"):
        load_pipeline(_write(tmp_path / "p.json", pipe))


def test_approved_development_stage_is_rejected(tmp_path):
    pipe = _minimal_pipeline()
    pipe["pipeline"][0]["development_stage"] = _envelope(value="approved")
    with pytest.raises(CatalogError, match="development_stage"):
        load_pipeline(_write(tmp_path / "p.json", pipe))


def test_approved_v1_id_cannot_merge_into_pipeline(tmp_path):
    pipe = _minimal_pipeline([_minimal_pipeline_row("enfortumab-vedotin")])
    with pytest.raises(CatalogError, match="must not merge approved"):
        load_pipeline(_write(tmp_path / "p.json", pipe))


def test_scope_approved_bleed_is_rejected(tmp_path):
    pipe = _minimal_pipeline()
    pipe["scope"] = _envelope(value="fda_approved_only")
    with pytest.raises(CatalogError, match="pipeline_investigational"):
        load_pipeline(_write(tmp_path / "p.json", pipe))


def test_dar_key_is_rejected_on_pipeline(tmp_path):
    pipe = _minimal_pipeline()
    pipe["pipeline"][0]["dar"] = _envelope(value=4)
    with pytest.raises(CatalogError, match="invented-science"):
        load_pipeline(_write(tmp_path / "p.json", pipe))


def test_indication_key_is_rejected_on_pipeline(tmp_path):
    pipe = _minimal_pipeline()
    pipe["pipeline"][0]["indication"] = _envelope(value="invented")
    with pytest.raises(CatalogError, match="invented-science"):
        load_pipeline(_write(tmp_path / "p.json", pipe))


def test_access_missing_disclaimer_token_is_rejected(tmp_path):
    access = load_access()
    access["disclaimer"] = _envelope(value="informational only")
    with pytest.raises(CatalogError, match="disclaimer"):
        load_access(_write(tmp_path / "a.json", access))


def test_pipeline_ui_on_adcs_routes():
    """ADC-C-B: D-122 paths stay; pipeline card is declared before :id."""
    app = (ROOT / "ui" / "src" / "App.jsx").read_text(encoding="utf-8")
    assert 'path="/adcs"' in app
    assert 'path="/adcs/:id"' in app
    assert 'path="/adcs/pipeline/:id"' in app
    assert "AdcPipelineCard" in app
    pipeline_at = app.index('path="/adcs/pipeline/:id"')
    approved_at = app.index('path="/adcs/:id"')
    assert pipeline_at < approved_at
