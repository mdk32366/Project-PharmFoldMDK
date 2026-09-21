"""D-174 — ADC sibling / administratively-closed BLA footnotes."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.adc_catalog import CatalogError, load_catalog

ROOT = Path(__file__).resolve().parents[1]
LOG = (ROOT / "docs" / "decisions.md").read_text(encoding="utf-8")
RESERVED = (ROOT / "docs" / "RESERVED.md").read_text(encoding="utf-8")
CATALOG = ROOT / "data" / "adcs" / "adcs.v1.json"
README = (ROOT / "data" / "adcs" / "README.md").read_text(encoding="utf-8")
CARD = (ROOT / "ui" / "src" / "components" / "AdcCard.jsx").read_text(encoding="utf-8")
EM = "—"


def test_d174_entry_and_pointer():
    assert "\n### D-174 — ADC catalog: sibling / administratively-closed BLA footnotes" in LOG
    assert "Next free `D-` integer: **`D-175`**" in RESERVED
    assert "Next free `D-` integer: **`D-174`**" not in RESERVED
    assert "| **D-174**" in RESERVED and "Spent" in RESERVED.split("| **D-174**", 1)[1][:280]
    assert "| **D-175**" in RESERVED
    assert "#338" in LOG or "338" in LOG


def test_catalog_still_fifteen_rows_with_footnotes():
    data = load_catalog(CATALOG)
    assert len(data['adcs']) == 15
    by = {r['brand_name']['value']: r for r in data['adcs']}
    d = by['DATROWAY']
    assert d['application_number']['value'] == 'BLA761394'
    rel = d['related_application_numbers']['value']
    assert any(x['application_number'] == 'BLA761464' for x in rel)
    a = by['ADCETRIS']
    assert a['application_number']['value'] == 'BLA125388'
    assert any(x['application_number'] == 'BLA125399' for x in a['related_application_numbers']['value'])
    # application_number remains a non-array envelope
    assert isinstance(d['application_number']['value'], str)


def test_related_rejects_unknown_relation_and_canonical_dup():
    data = json.loads(CATALOG.read_text(encoding='utf-8'))
    row = next(r for r in data['adcs'] if r['brand_name']['value'] == 'DATROWAY')
    bad = json.loads(json.dumps(data))
    brow = next(r for r in bad['adcs'] if r['brand_name']['value'] == 'DATROWAY')
    brow['related_application_numbers']['value'][0]['relation'] = 'invented_relation'
    with pytest.raises(CatalogError):
        load_catalog(_write_tmp(bad))
    bad2 = json.loads(json.dumps(data))
    brow2 = next(r for r in bad2['adcs'] if r['brand_name']['value'] == 'DATROWAY')
    brow2['related_application_numbers']['value'][0]['application_number'] = brow2['application_number']['value']
    with pytest.raises(CatalogError):
        load_catalog(_write_tmp(bad2))


def _write_tmp(data):
    path = ROOT / '.tmp' / 'd174_bad_catalog.json'
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(data), encoding='utf-8')
    return path


def test_ui_and_readme_honesty():
    assert "related_application_numbers" in CARD
    assert "not a second ADC" in CARD
    assert "sibling" in README.lower() or "closed" in README.lower()
    assert "auto-merge" in README.lower() or "detect-only" in README.lower() or "not an auto" in README.lower()

