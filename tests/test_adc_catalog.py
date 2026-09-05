"""D-119 — ADC-A catalog tests, written so they can go red.

Hermetic: the committed file and tmp fixtures. No network. The live openFDA
query dated the file; it is not this suite (D-029 / D-119).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.adc_catalog import (
    ADC_FIELDS,
    CATALOG_V1,
    CONFIDENCES,
    FIELD_KEYS,
    CatalogError,
    get_adc,
    load_catalog,
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


def _minimal_row(adc_id="fixture-adc"):
    return {name: _envelope(value=f"{adc_id}-{name}" if name != "id" else adc_id)
            for name in ADC_FIELDS} | {
        "marketing_status": _envelope(value="Prescription", confidence="official"),
    }


def _minimal_catalog(rows=None):
    header = {
        "catalog_id": _envelope(value="adcs.v1", confidence="derived"),
        "schema_version": _envelope(value="1", confidence="derived"),
        "scope": _envelope(value="fda_approved_only"),
        "completeness": _envelope(value="floor_not_census"),
        "approvals_reconciled_as_of": _envelope(value="2026-09-05", confidence="official"),
        "antigen_mapping_reviewed_as_of": _envelope(value="2026-09-05"),
        "emma_watch": _envelope(value="documented_hook_not_built"),
        "named_exclusions": _envelope(value=[{"id": "pipeline_and_right_to_try", "reason": "ADC-C"}]),
        "adcs": rows if rows is not None else [_minimal_row()],
    }
    return header


def _write(path, obj):
    path.write_text(json.dumps(obj), encoding="utf-8")
    return path


def test_committed_catalog_every_field_is_an_envelope():
    data = load_catalog()
    for name in (
        "catalog_id", "schema_version", "scope", "completeness",
        "approvals_reconciled_as_of", "antigen_mapping_reviewed_as_of",
        "emma_watch", "named_exclusions",
    ):
        assert set(data[name].keys()) == set(FIELD_KEYS)
        assert data[name]["confidence"] in CONFIDENCES
    for row in data["adcs"]:
        assert set(row) == set(ADC_FIELDS)
        for name, field in row.items():
            assert set(field.keys()) == set(FIELD_KEYS), name
            assert field["confidence"] in CONFIDENCES, name
            assert field["value"] not in (None, "")
            assert field["source"] and field["as_of"]


def test_committed_catalog_is_fda_approved_only():
    data = load_catalog()
    assert data["scope"]["value"] == "fda_approved_only"
    ids = [r["id"]["value"] for r in data["adcs"]]
    assert "ifinatamab-deruxtecan" not in ids
    assert "lumoxiti" not in ids
    assert "moxetumomab-pasudotox" not in ids
    blob = CATALOG_V1.read_text(encoding="utf-8").lower()
    assert "right-to-try" not in blob
    assert "right to try" not in blob
    for row in data["adcs"]:
        assert row["marketing_status"]["value"] == "Prescription"
        assert row["application_number"]["value"].startswith("BLA")
        assert row["current_application_approval_date"]["as_of"] == "2026-09-05"


def test_committed_catalog_refuses_invented_science_keys():
    raw = json.loads(CATALOG_V1.read_text(encoding="utf-8"))
    text = json.dumps(raw).lower()
    for banned in ("\"dar\"", "\"ic50\"", "\"orr\"", "\"pfs\"", "\"os\"",
                   "\"payload\"", "\"linker\""):
        assert banned not in text, banned


def test_committed_v1_pins_the_fifteen_openfda_hits_from_2026_09_05():
    """Pin of THIS file on the reconciliation date — not a scientific constant."""
    data = load_catalog()
    ids = [r["id"]["value"] for r in data["adcs"]]
    assert ids == [
        "gemtuzumab-ozogamicin",
        "brentuximab-vedotin",
        "ado-trastuzumab-emtansine",
        "inotuzumab-ozogamicin",
        "polatuzumab-vedotin",
        "enfortumab-vedotin",
        "fam-trastuzumab-deruxtecan",
        "sacituzumab-govitecan",
        "belantamab-mafodotin",
        "loncastuximab-tesirine",
        "tisotumab-vedotin",
        "mirvetuximab-soravtansine",
        "datopotamab-deruxtecan",
        "telisotuzumab-vedotin",
        "pivekimab-sunirine",
    ]
    by_id = {r["id"]["value"]: r for r in data["adcs"]}
    assert by_id["enfortumab-vedotin"]["application_number"]["value"] == "BLA761137"
    assert by_id["enfortumab-vedotin"]["uniprot_accession"]["value"] == "Q96NY8"
    assert by_id["ado-trastuzumab-emtansine"]["application_number"]["value"] == "BLA125427"
    assert by_id["pivekimab-sunirine"]["application_number"]["value"] == "BLA761460"
    assert by_id["pivekimab-sunirine"]["uniprot_accession"]["value"] == "P26951"
    assert by_id["belantamab-mafodotin"]["application_number"]["value"] == "BLA761440"


def test_get_adc_unknown_is_none():
    assert get_adc("not-an-adc") is None
    assert get_adc("enfortumab-vedotin")["brand_name"]["value"] == "PADCEV"


def test_bare_string_field_is_rejected(tmp_path):
    cat = _minimal_catalog()
    cat["adcs"][0]["inn"] = "not-an-envelope"
    with pytest.raises(CatalogError, match="not a"):
        load_catalog(_write(tmp_path / "c.json", cat))


def test_unknown_confidence_is_rejected(tmp_path):
    cat = _minimal_catalog()
    cat["adcs"][0]["antigen"] = _envelope(value="X", confidence="high")
    with pytest.raises(CatalogError, match="confidence"):
        load_catalog(_write(tmp_path / "c.json", cat))


def test_dar_key_is_rejected(tmp_path):
    cat = _minimal_catalog()
    cat["adcs"][0]["dar"] = _envelope(value=4)
    with pytest.raises(CatalogError, match="invented-science"):
        load_catalog(_write(tmp_path / "c.json", cat))


def test_pipeline_row_id_is_rejected(tmp_path):
    cat = _minimal_catalog([_minimal_row("ifinatamab-deruxtecan")])
    with pytest.raises(CatalogError, match="ADC-C"):
        load_catalog(_write(tmp_path / "c.json", cat))


def test_withdrawn_status_is_rejected(tmp_path):
    row = _minimal_row()
    row["marketing_status"] = _envelope(value="Discontinued", confidence="official")
    with pytest.raises(CatalogError, match="Prescription"):
        load_catalog(_write(tmp_path / "c.json", _minimal_catalog([row])))


def test_d122_entry_exists_in_the_living_log():
    """The check is the heading, not a citation of it (D-062 / method-note item 7)."""
    log = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    assert "### D-122 —" in log


def test_react_app_has_adcs_routes():
    """D-122 / ADC-B: the catalog UI is in App.jsx. Inverts the D-119 absence pin."""
    app = (ROOT / "ui" / "src" / "App.jsx").read_text(encoding="utf-8")
    assert 'path="/adcs"' in app
    assert 'path="/adcs/:id"' in app
    assert "AdcsView" in app
    assert "AdcCard" in app
    assert ">ADCs<" in app
