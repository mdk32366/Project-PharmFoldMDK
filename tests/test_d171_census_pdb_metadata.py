"""D-171 — census experimental PDB metadata (selection, API attach, UI honesty)."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
LOG = (REPO / "docs" / "decisions.md").read_text(encoding="utf-8")
RESERVED = (REPO / "docs" / "RESERVED.md").read_text(encoding="utf-8")
READS = (REPO / "app" / "reads.py").read_text(encoding="utf-8")
CPR = (REPO / "app" / "census_pdb_read.py").read_text(encoding="utf-8")
CORE = (REPO / "core" / "census_pdb.py").read_text(encoding="utf-8")
CT = (REPO / "ui" / "src" / "components" / "CensusTable.jsx").read_text(encoding="utf-8")
CD = (REPO / "ui" / "src" / "components" / "CensusDetail.jsx").read_text(encoding="utf-8")
FIXTURE = json.loads(
    (REPO / "tests" / "fixtures" / "d171_pdbe_best_structures.json").read_text(encoding="utf-8")
)
SEG_O75899 = "42-483;544-551;619-654;713-720"


def test_d171_entry_exists_and_pointer_moved():
    assert re.search(r"^### D-171\b", LOG, re.M)
    assert "Next free `D-` integer: **`D-177`**" in RESERVED
    assert "Next free `D-` integer: **`D-171`**" not in RESERVED
    assert "Next free `D-` integer: **`D-172`**" not in RESERVED
    assert re.search(r"^\| \*\*D-171\*\* \|", RESERVED, re.M)
    assert re.search(r"^\| \*\*D-172\*\* \|", RESERVED, re.M)
    assert re.search(r"^### D-173\b", LOG, re.M)
    assert re.search(r"^### D-174\b", LOG, re.M)
    assert re.search(r"^### D-175\b", LOG, re.M)
    assert not re.search(r"^### D-177\b", LOG, re.M)
    assert "0.50" in LOG[LOG.find("### D-171") : LOG.find("### D-171") + 2000]
    assert "ABSENT_NO_ECD_COVERING_STRUCTURE" in LOG[LOG.find("### D-171") : LOG.find("### D-171") + 2500]


def test_selection_module_pins_threshold_and_statuses():
    assert "ECD_COVER_THRESHOLD = 0.50" in CORE
    assert "ABSENT_NO_ECD_COVERING_STRUCTURE" in CORE
    assert "def select_pdb_for_accession" in CORE


def test_o75899_selects_ecd_covering_best():
    from core.census_pdb import STATUS_PRESENT, select_pdb_for_accession

    painted = select_pdb_for_accession(
        accession="O75899",
        candidates_raw=FIXTURE["O75899"],
        ecd_segments=SEG_O75899,
    )
    assert painted["pdb_status"] == STATUS_PRESENT
    assert painted["pdb_best"] is not None
    assert painted["pdb_best"]["ecd_coverage_frac"] >= 0.50
    assert painted["pdb_best"]["ecd_covers"] is True
    assert painted["pdb_best"]["attribution"]["source"] == "PDBe/SIFTS"
    assert "rcsb.org" in painted["pdb_best"]["attribution"]["rcsb_url"]
    assert "pdbe" in painted["pdb_best"]["attribution"]["pdbe_url"]


def test_absent_and_absent_no_ecd_are_distinct():
    from core.census_pdb import (
        STATUS_ABSENT,
        STATUS_ABSENT_NO_ECD,
        select_pdb_for_accession,
    )

    none = select_pdb_for_accession(
        accession="SYNNONE1", candidates_raw=[], ecd_segments="1-100"
    )
    assert none["pdb_status"] == STATUS_ABSENT
    assert none["pdb_best"] is None

    no_ecd = select_pdb_for_accession(
        accession="SYNABS01",
        candidates_raw=FIXTURE["SYNABS01"],
        ecd_segments="1-100",
    )
    assert no_ecd["pdb_status"] == STATUS_ABSENT_NO_ECD
    assert no_ecd["pdb_best"] is None
    assert "1abc" in no_ecd["pdb_ids"]


def test_short_peptide_on_gabbr2_is_not_pdb_best():
    """4pas covers intracellular peptide — must not win when ECD-covering X-rays exist."""
    from core.census_pdb import select_pdb_for_accession

    painted = select_pdb_for_accession(
        accession="O75899",
        candidates_raw=FIXTURE["O75899"],
        ecd_segments=SEG_O75899,
    )
    assert painted["pdb_best"]["pdb_id"] != "4pas"
    # 4pas should still be listed
    assert "4pas" in painted["pdb_ids"]


def test_one_way_wall_pdb_read_does_not_import_reads():
    assert "from app.reads import" not in CPR
    # Docstring may name the wall; imports must not cross it.
    body = CPR.split('"""', 2)[-1] if CPR.count('"""') >= 2 else CPR
    assert "import app.reads" not in body
    assert "from app.reads" not in body
    assert "attach_pdb_fields" in READS
    assert "attach_pdb_fields" in CPR


def test_ui_honesty_forbids_ranked_fold_labeling():
    assert "experimental-pdb-detail" in CD
    assert "PDBe/SIFTS" in CD
    assert "not</strong> the served predicted fold" in CD or "not the served predicted fold" in CD.lower() or "not</strong> the served predicted fold" in CD
    assert "STRUCTURAL_ONLY" in CD
    assert "cohort-82" in CD
    # table
    assert "PDB (experimental)" in CT
    assert "pdb-experimental-columns-note" in CT
    assert "pdb-best-cell" in CT
    for banned in ("the ranked fold", "cohort Rank column"):
        assert banned not in CD.lower()


def test_migration_and_loader_exist_and_do_not_touch_structural():
    mig = (REPO / "db" / "migrations" / "versions" / "0015_census_pdb_metadata.py").read_text(
        encoding="utf-8"
    )
    assert "census_pdb_runs" in mig
    assert "census_pdb_accessions" in mig
    assert "down_revision" in mig and "0014_enqueue_identity_unique" in mig
    loader = (REPO / "scripts" / "census_pdb_metadata.py").read_text(encoding="utf-8")
    assert "structural_score" in loader  # named as hard stop in docstring
    assert "Never mutates structural_score" in loader or "never mutates structural_score" in loader.lower()
