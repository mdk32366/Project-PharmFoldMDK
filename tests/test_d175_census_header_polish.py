"""D-175 — Census header polish (PDB exp, tooltips, Status wrap)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = (ROOT / "docs" / "decisions.md").read_text(encoding="utf-8")
RESERVED = (ROOT / "docs" / "RESERVED.md").read_text(encoding="utf-8")
TABLE = (ROOT / "ui" / "src" / "components" / "CensusTable.jsx").read_text(encoding="utf-8")
CSS = (ROOT / "ui" / "src" / "styles.css").read_text(encoding="utf-8")
EM = "—"
MDOT = "·"


def test_d175_entry_and_pointer():
    assert "\n### D-175 — Census UI: header polish (PDB exp, tooltips, Status wrap)" in LOG
    assert "Next free `D-` integer: **`D-177`**" in RESERVED
    assert "Next free `D-` integer: **`D-175`**" not in RESERVED
    assert "| **D-175**" in RESERVED and "Spent" in RESERVED.split("| **D-175**", 1)[1][:280]
    assert "| **D-176**" in RESERVED


def test_pdb_header_short_with_experimental_tooltip():
    assert "label: 'PDB (exp)'" in TABLE
    assert "label: 'PDB (experimental)'" not in TABLE
    assert "COLUMN_TITLES" in TABLE
    assert "Experimental PDB" in TABLE or "experimental PDB" in TABLE.lower()


def test_column_titles_map_and_header_title_wiring():
    assert "export const COLUMN_TITLES" in TABLE
    assert "title={COLUMN_TITLES[c.key]" in TABLE
    assert "not suitability" in TABLE.lower() or "not a suitability" in TABLE.lower() or "not suitability" in TABLE
    assert "STRUCTURAL_ONLY" in TABLE
    assert "cohort-82" in TABLE


def test_status_header_wraps_two_lines_keeps_scored():
    assert "headerLines:" in TABLE
    assert "(structure · scored · seam)" in TABLE
    assert "(structure · score · seam)" not in TABLE
    assert "th-line" in CSS
    assert "status_structure" in CSS


def test_protein_column_tightened():
    block = CSS.split(".census-table .protein-name")[1].split("}")[0]
    assert "max-width: 12rem" in block
    assert "max-width: 22rem" not in block
