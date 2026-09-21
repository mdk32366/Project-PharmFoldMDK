"""D-170 — structural_rank + structural_score on census list/detail surfaces."""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LOG = (REPO / "docs" / "decisions.md").read_text(encoding="utf-8")
RESERVED = (REPO / "docs" / "RESERVED.md").read_text(encoding="utf-8")
READS = (REPO / "app" / "reads.py").read_text(encoding="utf-8")
CSR = (REPO / "app" / "census_structural_read.py").read_text(encoding="utf-8")
CT = (REPO / "ui" / "src" / "components" / "CensusTable.jsx").read_text(encoding="utf-8")
CD = (REPO / "ui" / "src" / "components" / "CensusDetail.jsx").read_text(encoding="utf-8")


def test_d170_entry_exists_and_pointer_moved():
    assert re.search(r"^### D-170\b", LOG, re.M)
    assert "Next free `D-` integer: **`D-176`**" in RESERVED
    assert "Next free `D-` integer: **`D-170`**" not in RESERVED
    assert re.search(r"^\| \*\*D-170\*\* \|", RESERVED, re.M)
    assert re.search(r"^\| \*\*D-171\*\* \|", RESERVED, re.M)
    assert re.search(r"^\| \*\*D-172\*\* \|", RESERVED, re.M)
    assert re.search(r"^### D-171\b", LOG, re.M)  # spent
    assert re.search(r"^### D-173\b", LOG, re.M)
    assert re.search(r"^### D-174\b", LOG, re.M)
    assert re.search(r"^### D-175\b", LOG, re.M)
    assert not re.search(r"^### D-176\b", LOG, re.M)


def test_server_exposes_attach_helper_and_list_calls_it():
    assert "def structural_rank_index" in CSR
    assert "def attach_structural_rank_fields" in CSR
    assert "attach_structural_rank_fields" in READS


def test_census_table_has_structural_only_columns_and_label():
    assert "structural_rank" in CT
    assert "structural_score" in CT
    assert "STRUCTURAL_ONLY" in CT
    assert "Struct. rank" in CT
    assert "Struct. score" in CT
    # D-173: STRUCTURAL_ONLY moved out of th into legend chrome
    assert "structural-rank-cell" in CT
    assert "cohort-82" in CT


def test_census_detail_has_structural_only_disclaimer():
    assert "structural-rank-detail" in CD
    assert "STRUCTURAL_ONLY" in CD
    assert "cohort-82 learned scorer" in CD
    assert "StructuralProfile" in CD


def test_d170_names_targets_na():
    """Contract 3: Targets is cohort-82; no census protein primary surface there at tip."""
    m = re.search(r"^### D-170\b.*?(?=^### |\Z)", LOG, re.M | re.S)
    assert m, "### D-170 missing"
    body = m.group(0)
    assert re.search(r"Targets|N/A|no census accession", body, re.I)
