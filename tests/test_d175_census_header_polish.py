"""D-175 — Census UI: header polish (PDB exp, tooltips, Status wrap)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = (ROOT / "docs" / "decisions.md").read_text(encoding="utf-8")
RESERVED = (ROOT / "docs" / "RESERVED.md").read_text(encoding="utf-8")
TABLE = (ROOT / "ui" / "src" / "components" / "CensusTable.jsx").read_text(encoding="utf-8")
CSS = (ROOT / "ui" / "src" / "styles.css").read_text(encoding="utf-8")
MDOT = "·"


def test_d175_entry_and_pointer():
    assert "\n### D-175 — Census UI: header polish (PDB exp, tooltips, Status wrap)" in LOG
    assert "Next free `D-` integer: **`D-176`**" in RESERVED
    assert "Next free `D-` integer: **`D-175`**" not in RESERVED
    assert "| **D-175**" in RESERVED and "Spent" in RESERVED.split("| **D-175**", 1)[1][:280]
    assert "| **D-176**" in RESERVED


def test_pdb_header_short_form_and_tooltip_honesty():
    assert "label: 'PDB (exp)'" in TABLE
    assert "label: 'PDB (experimental)'" not in TABLE
    assert "export const COLUMN_TITLES" in TABLE
    pdb_title = TABLE.split("pdb_best:")[1].splitlines()[0]
    assert "Experimental PDB metadata" in pdb_title
    assert "not the served fold" in pdb_title
    assert "STRUCTURAL_ONLY" in pdb_title


def test_every_column_key_has_title_map_entry_and_wired():
    body = TABLE.split("export const COLUMNS = [", 1)[1].split("export const COLUMN_TITLES", 1)[0]
    keys = re.findall(r"key: '([^']+)'", body)
    assert keys
    titles_body = TABLE.split("export const COLUMN_TITLES = {", 1)[1]
    titles_body = titles_body.split("}", 1)[0]
    for k in keys:
        assert f"{k}:" in titles_body, k
    assert "title={COLUMN_TITLES[c.key]}" in TABLE
    assert "aria-label={COLUMN_TITLES[c.key]}" in TABLE


def test_status_header_two_line_wrap_keeps_scored():
    assert "headerLines: ['Status', '(structure " + MDOT + " scored " + MDOT + " seam)']" in TABLE
    assert "(structure " + MDOT + " score " + MDOT + " seam)" not in TABLE
    assert 'className="th-line"' in TABLE
    block = CSS.split(".th-line")[1][:120]
    assert "display: block" in block
    assert "status_structure" in CSS


def test_protein_column_tightened():
    block = CSS.split(".census-table .protein-name")[1][:220]
    assert "max-width: 12rem" in block
    assert "max-width: 22rem" not in block


def test_cost_struct_tooltip_honesty_substrings():
    titles = TABLE.split("export const COLUMN_TITLES = {", 1)[1].split("}", 1)[0]
    assert "not suitability" in titles
    assert "STRUCTURAL_ONLY" in titles
    assert "cohort-82" in titles
