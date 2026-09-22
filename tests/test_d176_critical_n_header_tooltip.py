"""D-176 — Census Critical / critical_n header tooltip (six HPA tissues, High-only, D-093)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = (ROOT / "docs" / "decisions.md").read_text(encoding="utf-8")
RESERVED = (ROOT / "docs" / "RESERVED.md").read_text(encoding="utf-8")
TABLE = (ROOT / "ui" / "src" / "components" / "CensusTable.jsx").read_text(encoding="utf-8")

CRITICAL_TISSUES = (
    "heart muscle",
    "liver",
    "kidney",
    "lung",
    "cerebral cortex",
    "bone marrow",
)


def test_d176_entry_and_pointer():
    assert "\n### D-176 — Census UI: Critical / critical_n header tooltip" in LOG
    assert "Next free `D-` integer: **`D-177`**" in RESERVED
    assert "Next free `D-` integer: **`D-176`**" not in RESERVED
    assert "| **D-176**" in RESERVED and "Spent" in RESERVED.split("| **D-176**", 1)[1][:280]
    assert "| **D-177**" in RESERVED


def test_critical_n_tooltip_six_tissues_high_only_d093():
    assert "export const COLUMN_TITLES" in TABLE
    assert "critical_n:" in TABLE
    for t in CRITICAL_TISSUES:
        assert t in TABLE
    assert "Only High counts" in TABLE
    assert "not a tumour÷normal ratio" in TABLE
    assert "D-093" in TABLE
    assert "Critical tissue count" not in TABLE.split("critical_n:", 1)[1].split("}", 1)[0]


def test_d175_title_vs_aria_scar_stands():
    assert "title={COLUMN_TITLES[c.key]" in TABLE
    # aria-label stays short COLUMNS label (D-175 scar) — not the long tooltip
    assert "aria-label={c.label}" in TABLE or "aria-label={c.label" in TABLE
