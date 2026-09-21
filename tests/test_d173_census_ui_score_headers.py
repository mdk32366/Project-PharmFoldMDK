"""D-173 — Census UI: numeric structural_score primary + header wrap."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = (ROOT / "docs" / "decisions.md").read_text(encoding="utf-8")
RESERVED = (ROOT / "docs" / "RESERVED.md").read_text(encoding="utf-8")
TABLE = (ROOT / "ui" / "src" / "components" / "CensusTable.jsx").read_text(encoding="utf-8")
CSS = (ROOT / "ui" / "src" / "styles.css").read_text(encoding="utf-8")
DETAIL = (ROOT / "ui" / "src" / "components" / "CensusDetail.jsx").read_text(encoding="utf-8")
PROTEIN = (ROOT / "ui" / "src" / "components" / "CensusProteinView.jsx").read_text(encoding="utf-8")
MDOT = "·"
EM = "—"


def test_d173_entry_and_pointer():
    assert "\n### D-173 — Census UI: numeric structural_score primary + header wrap" in LOG
    assert "Next free `D-` integer: **`D-174`**" in RESERVED
    assert "Next free `D-` integer: **`D-173`**" not in RESERVED
    assert "| **D-173**" in RESERVED and "Spent" in RESERVED.split("| **D-173**", 1)[1][:280]
    assert "| **D-174**" in RESERVED


def test_status_header_says_scored_not_score():
    assert f"Status (structure {MDOT} scored {MDOT} seam)" in TABLE
    assert f"Status (structure {MDOT} score {MDOT} seam)" not in TABLE


def test_struct_headers_short_structural_only_in_legend():
    assert "label: 'Struct. score'" in TABLE
    assert "label: 'Struct. rank'" in TABLE
    assert "label: 'Struct. score (STRUCTURAL_ONLY)'" not in TABLE
    assert "STRUCTURAL_ONLY" in TABLE


def test_cost_header_keeps_honesty_phrase_and_css_allows_wrap():
    assert f"Cost to fold (compute {EM} not suitability)" in TABLE
    thead = CSS.split(".census-table thead th")[1].split(".census-table thead th button")[0]
    assert "white-space: nowrap" not in thead
    assert "white-space: normal" in CSS
    assert "data-col={c.key}" in TABLE


def test_table_min_width_tightened():
    assert "min-width: 62rem" in CSS


def test_detail_caveat_scopes_cohort_denial():
    assert "cohort-82 learned scorer" in DETAIL
    assert 'data-testid="census-detail-cohort-scorer"' in DETAIL
    block = DETAIL.split("status-unscored")[1].split("</li>")[0]
    assert "STRUCTURAL_ONLY" in block
    assert "ADC" in block


def test_protein_view_bar_affirms_structural_only_when_present():
    assert 'data-testid="census-cohort-scorer-bar"' in PROTEIN
    assert "structure-only rank and score (STRUCTURAL_ONLY) are still on this card" in PROTEIN

