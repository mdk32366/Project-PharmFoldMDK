"""D-126-B — UI triple-path honesty. These must be able to go red.

B reads A's sibling ``confidence_kabsch/{parent}/`` tree. It does not
persist, does not invent RMSD / n_ca_eff / trim counts, and must not
collide persist stems with assembler ``stitched`` or D-125 ``kabsch/``.
Default served PDB stays assembler. Missing tree must not imply a
D-126 path exists.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.confidence_kabsch_path_read import (
    CONFIDENCE_KABSCH_PERSIST_STEM_PREFIX,
    empty_confidence_kabsch_block,
    project_confidence_seam,
    read_confidence_kabsch_path,
    seam_note_for_triple,
    triple_path_payload,
)
from app.kabsch_path_read import ASSEMBLER_PERSIST_STEM, KABSCH_PERSIST_STEM_PREFIX
from app.reads import get_census_detail
from db.models import Base, ProteinAnalysis

ROOT = Path(__file__).resolve().parent.parent
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
INDEX = (ROOT / "docs" / "decisions.md").read_text(encoding="utf-8")
READS = (ROOT / "app" / "reads.py").read_text(encoding="utf-8")
D126_WRITER = (ROOT / "core" / "hold48_confidence_kabsch.py").read_text(encoding="utf-8")
D125_WRITER = (ROOT / "core" / "hold48_kabsch.py").read_text(encoding="utf-8")
FORBIDDEN = (
    "seams solved",
    "kabsch aligned",
    "full-length af-quality",
    "we ran kabsch",
)


def _engine():
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    return eng


def _add_parent(session, tmp: Path):
    tmp.mkdir(parents=True, exist_ok=True)
    pdb = tmp / "stitched.pdb"
    pdb.write_text("HEADER assembler\n", encoding="utf-8")
    session.add(
        ProteinAnalysis(
            id=2817,
            input_type="uniprot",
            input_value="Q9P273",
            cohort_tranche=5,
            pdb_path=str(pdb),
            pae_json_path=str(tmp / "stitched_pae.json"),
            mean_plddt=61.07,
            meta={"hold48_kind": "parent", "span_aa": 2368},
        )
    )
    session.add(
        ProteinAnalysis(
            id=3673,
            input_type="uniprot",
            input_value="Q9P273",
            cohort_tranche=5,
            pdb_path="/tmp/tile3673.pdb",
            pae_json_path="/tmp/tile3673_pae.json",
            mean_plddt=70.0,
            meta={
                "hold48_kind": "tile",
                "parent_job_id": 2817,
                "tile_start": 1,
                "tile_end": 1656,
                "tile_index": 0,
                "span_aa": 1656,
            },
        )
    )
    session.add(
        ProteinAnalysis(
            id=3630,
            input_type="uniprot",
            input_value="Q9P273",
            cohort_tranche=5,
            pdb_path="/tmp/tile3630.pdb",
            pae_json_path="/tmp/tile3630_pae.json",
            mean_plddt=55.0,
            meta={
                "hold48_kind": "tile",
                "parent_job_id": 2817,
                "tile_start": 1529,
                "tile_end": 2368,
                "tile_index": 1,
                "span_aa": 840,
            },
        )
    )


def _write_kabsch_tree(root: Path, *, rmsd=1.25, accepted=True):
    dest = root / "kabsch" / "2817"
    dest.mkdir(parents=True, exist_ok=True)
    seam = {
        "moving_tile_index": 2,
        "reference_tile_index": 1,
        "overlap_start": 1529,
        "overlap_end": 1656,
        "n_ca": 128,
        "rmsd_angstrom": rmsd,
        "refuse_reason": None,
    }
    payload = {
        "algorithm": "kabsch_ca_then_winning_tile",
        "decision": "D-125",
        "parent_job_id": 2817,
        "accepted": accepted,
        "seams": [seam],
    }
    (dest / "provenance.json").write_text(json.dumps(payload) + "\n", encoding="utf-8")
    (dest / "seams.jsonl").write_text(json.dumps(seam) + "\n", encoding="utf-8")
    return dest


def _write_confidence_tree(
    root: Path,
    *,
    rmsd=2.5,
    n_ca_eff=96,
    full_overlap=8.0,
    jump=4.2,
    trim_rounds=2,
    refuse_reason=None,
    accepted=True,
    include_optional=True,
):
    dest = root / "confidence_kabsch" / "2817"
    dest.mkdir(parents=True, exist_ok=True)
    seam = {
        "moving_tile_index": 2,
        "reference_tile_index": 1,
        "overlap_start": 1529,
        "overlap_end": 1656,
        "n_ca": 128,
        "rmsd_angstrom": rmsd,
        "refuse_reason": refuse_reason,
    }
    if include_optional:
        seam["n_ca_eff"] = n_ca_eff
        seam["rmsd_full_overlap_angstrom"] = full_overlap
        seam["max_ca_jump_angstrom"] = jump
        seam["trim_rounds"] = trim_rounds
    payload = {
        "algorithm": "overlap_confidence_kabsch_then_winning_tile",
        "decision": "D-126",
        "parent_job_id": 2817,
        "accepted": accepted,
        "seams": [seam],
    }
    (dest / "provenance.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (dest / "seams.jsonl").write_text(json.dumps(seam) + "\n", encoding="utf-8")
    if accepted:
        (dest / "stitched.pdb").write_text("HEADER confidence-kabsch-path\n", encoding="utf-8")
    return dest


def test_d126_b_heading_exists_in_the_living_log():
    """D-001 naming: the check is the heading, not a citation of one."""
    assert re.search(r"^### D-126-B — UI triple-path honesty", LOG, re.M)
    assert "does **not** re-implement persist" in LOG
    assert "Seams are not scientifically solved" in LOG
    assert "Spec §6" in LOG
    assert "aa8aa02" in LOG
    assert "served path = assembler" in LOG
    assert "do not pretend D-125 or D-126 is live-served" in LOG


def test_trinity_locked_bar_cites_d126a_and_spec_section_six():
    assert "aa8aa02" in LOG
    assert "Spec §6" in LOG
    assert "LOCKED" in LOG
    assert "served path = assembler" in LOG
    assert "aa8aa02" in INDEX
    assert "Spec §6" in INDEX
    assert "UI triple-path honesty only" in INDEX


def test_missing_confidence_tree_does_not_imply_d126_path_or_invent_metrics(tmp_path):
    block = read_confidence_kabsch_path(
        tmp_path, parent_analysis_id=2817, parent_job_id=2817
    )
    assert block["present"] is False
    assert block["empty_reason"] == "no_confidence_kabsch_artifacts"
    assert block["seams"] == []
    assert block["persist_stem"] == "confidence_kabsch/2817"
    assert block["success_pdb_on_disk"] is False
    dumped = json.dumps(block["seams"])
    assert "rmsd" not in dumped
    assert "n_ca_eff" not in dumped
    assert "trim_rounds" not in dumped
    note = seam_note_for_triple({"present": False}, block)
    assert "88.76" in note
    assert "third path" not in note.lower()
    assert "confidence_kabsch" not in note.lower()
    assert "solved seam" in note.lower() or "not a solved" in note.lower()
    for phrase in FORBIDDEN:
        assert phrase not in note.lower()


def test_present_tree_names_three_paths_and_stems_do_not_collide(tmp_path):
    _write_kabsch_tree(tmp_path, rmsd=2.5)
    _write_confidence_tree(tmp_path, rmsd=3.4)
    payload = triple_path_payload(tmp_path, parent_analysis_id=2817, parent_job_id=2817)
    asm = payload["assembler"]
    kabsch = payload["kabsch"]
    d126 = payload["confidence_kabsch"]
    assert asm["persist_stem"] == ASSEMBLER_PERSIST_STEM == "stitched"
    assert asm["default_served"] is True
    assert kabsch["present"] is True
    assert kabsch["persist_stem"] == "kabsch/2817"
    assert kabsch["persist_stem"].startswith(KABSCH_PERSIST_STEM_PREFIX)
    assert d126["present"] is True
    assert d126["persist_stem"] == "confidence_kabsch/2817"
    assert d126["persist_stem"].startswith(CONFIDENCE_KABSCH_PERSIST_STEM_PREFIX)
    stems = {asm["persist_stem"], kabsch["persist_stem"], d126["persist_stem"]}
    assert len(stems) == 3
    assert "not scientifically solved" in d126["label"]
    assert d126["seams"][0]["rmsd_angstrom"] == 3.4
    assert d126["seams"][0]["n_ca"] == 128
    assert d126["seams"][0]["n_ca_eff"] == 96
    assert d126["success_pdb_on_disk"] is True


def test_d126_seam_fields_are_honest_empty_unless_a_wrote_them(tmp_path):
    _write_confidence_tree(tmp_path, include_optional=False, rmsd=None, accepted=False)
    missing = read_confidence_kabsch_path(tmp_path, parent_analysis_id=2817)
    seam = missing["seams"][0]
    assert seam["rmsd_angstrom"] is None
    assert seam["n_ca_eff"] is None
    assert seam["rmsd_full_overlap_angstrom"] is None
    assert seam["max_ca_jump_angstrom"] is None
    assert seam["trim_rounds"] is None

    root2 = tmp_path / "with-fields"
    _write_confidence_tree(root2, rmsd=1.1, n_ca_eff=80, full_overlap=9.5, jump=3.3, trim_rounds=1)
    present = read_confidence_kabsch_path(root2, parent_analysis_id=2817)
    row = present["seams"][0]
    assert row["rmsd_angstrom"] == 1.1
    assert row["n_ca_eff"] == 80
    assert row["rmsd_full_overlap_angstrom"] == 9.5
    assert row["max_ca_jump_angstrom"] == 3.3
    assert row["trim_rounds"] == 1


def test_project_seam_does_not_invent_numbers():
    row = project_confidence_seam(
        {"n_ca": 3, "rmsd_angstrom": None, "refuse_reason": "overlap_ca_lt_3"}
    )
    assert row["rmsd_angstrom"] is None
    assert row["rmsd_full_overlap_angstrom"] is None
    assert row["max_ca_jump_angstrom"] is None
    assert row["n_ca_eff"] is None
    assert row["trim_rounds"] is None
    assert row["n_ca"] == 3
    assert row["refuse_reason"] == "overlap_ca_lt_3"


def test_refused_seam_is_fail_closed_and_not_presented_as_d126_success(tmp_path):
    dest = _write_confidence_tree(
        tmp_path, rmsd=12.4, accepted=False, refuse_reason="rmsd_gt_10", include_optional=True
    )
    # A leftover stitched.pdb must not become a D-126 success.
    (dest / "stitched.pdb").write_text("HEADER leftover\n", encoding="utf-8")
    block = read_confidence_kabsch_path(tmp_path, parent_analysis_id=2817)
    assert block["present"] is True
    assert block["accepted"] is False
    assert block["success_pdb_on_disk"] is False
    assert block["seams"][0]["refuse_reason"] == "rmsd_gt_10"
    dumped = json.dumps(block).lower()
    assert "fixed" not in dumped
    for phrase in FORBIDDEN:
        assert phrase not in dumped


def test_assembly_review_carries_triple_path_empty_and_does_not_imply_d126(tmp_path):
    eng = _engine()
    assembler_dir = tmp_path / "assembler" / "2817"
    with Session(eng) as s:
        _add_parent(s, assembler_dir)
        s.commit()
    detail = get_census_detail(eng, 2817, artifact_root=tmp_path / "empty-ops")
    review = detail["assembly_review"]
    assert review["dual_path"]["assembler"]["persist_stem"] == "stitched"
    assert review["dual_path"]["assembler"]["default_served"] is True
    assert review["triple_path"]["confidence_kabsch"]["present"] is False
    assert review["triple_path"]["assembler"]["default_served"] is True
    names = [d["name"] for d in review["downloads"]["stitched"]]
    assert names == ["stitched.pdb", "stitched_plddt.json", "stitched_pae.json"]
    assert all(not n.startswith("confidence_kabsch") for n in names)
    assert all(not n.startswith("kabsch_") for n in names)
    assert "third path" not in review["seam_note"].lower()
    assert "not on disk" in review["seam_note"]


def test_assembly_review_reads_third_sibling_tree_beside_assembler_dir(tmp_path):
    """A's tree is {root}/confidence_kabsch/{parent}/ — not assembler {root}/{parent}/."""
    eng = _engine()
    ops = tmp_path / "ops"
    assembler_dir = ops / "2817"
    with Session(eng) as s:
        _add_parent(s, assembler_dir)
        s.commit()
    _write_kabsch_tree(ops, rmsd=3.1)
    _write_confidence_tree(ops, rmsd=4.4, jump=11.0, trim_rounds=3)
    detail = get_census_detail(eng, 2817, artifact_root=ops)
    d126 = detail["assembly_review"]["triple_path"]["confidence_kabsch"]
    assert d126["present"] is True
    assert d126["persist_stem"] == "confidence_kabsch/2817"
    assert d126["seams"][0]["rmsd_angstrom"] == 4.4
    assert d126["seams"][0]["max_ca_jump_angstrom"] == 11.0
    assert d126["seams"][0]["trim_rounds"] == 3
    assert "third path" in detail["assembly_review"]["seam_note"].lower()
    names = [d["name"] for d in detail["assembly_review"]["downloads"]["stitched"]]
    assert "stitched.pdb" in names
    assert "confidence_kabsch_stitched.pdb" not in names
    assert detail["assembly_review"]["triple_path"]["assembler"]["default_served"] is True


def test_b_does_not_reimplement_persist_writer():
    reader = (ROOT / "app" / "confidence_kabsch_path_read.py").read_text(encoding="utf-8")
    assert "def write_confidence_kabsch_restitch" not in reader
    assert "def write_provenance" not in reader
    assert "def write_kabsch_restitch" not in reader
    assert "write_confidence_kabsch_restitch" in D126_WRITER
    assert "triple_path_payload" in READS
    assert "WAVE1_WAVE2_STITCHED_PARENT_IDS" not in (ROOT / "core" / "scorer.py").read_text(
        encoding="utf-8"
    )


def test_empty_block_stems_never_equal_assembler_or_d125():
    empty = empty_confidence_kabsch_block(parent_id=2817)
    assert empty["persist_stem"] != ASSEMBLER_PERSIST_STEM
    assert empty["persist_stem"].startswith("confidence_kabsch/")
    assert not empty["persist_stem"].startswith("kabsch/")


def test_b_does_not_invoke_a_restitch_of_the_twenty_seven():
    """Emma pin: UI-only. B must not call the A writer or the restitch CLI."""
    reader = (ROOT / "app" / "confidence_kabsch_path_read.py").read_text(encoding="utf-8")
    reads = (ROOT / "app" / "reads.py").read_text(encoding="utf-8")
    routes = (ROOT / "app" / "read_routes.py").read_text(encoding="utf-8")
    ui_review = (ROOT / "ui" / "src" / "components" / "AssemblyReview.jsx").read_text(
        encoding="utf-8"
    )
    for text, label in (
        (reader, "confidence_kabsch_path_read"),
        (reads, "reads"),
        (routes, "read_routes"),
        (ui_review, "AssemblyReview"),
    ):
        assert "write_confidence_kabsch_restitch(" not in text, label
        assert "write_kabsch_restitch(" not in text, label
        assert "scripts.confidence_kabsch_restitch" not in text, label
        assert "python -m scripts.confidence_kabsch_restitch" not in text, label
        lowered = text.lower()
        for phrase in FORBIDDEN:
            assert phrase not in lowered, f"{label}: {phrase}"


def test_algorithm_modules_are_not_edited_by_this_ui_pr():
    """Hard stop: B reads; it does not rewrite A or D-125 algorithm."""
    assert "def write_confidence_kabsch_restitch" in D126_WRITER
    assert "def write_kabsch_restitch" in D125_WRITER
    assert "overlap_confidence_kabsch" not in D125_WRITER
