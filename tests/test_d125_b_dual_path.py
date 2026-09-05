"""D-125-B — UI dual-path honesty. These must be able to go red.

B reads A's sibling ``kabsch/{parent}/`` tree. It does not persist, does
not invent RMSD / max Cα jump, and must not collide persist stems with
the assembler ``stitched`` path.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.kabsch_path_read import (
    ASSEMBLER_PERSIST_STEM,
    KABSCH_PERSIST_STEM_PREFIX,
    dual_path_payload,
    empty_kabsch_block,
    project_seam,
    read_kabsch_dual_path,
    seam_note_for,
)
from app.reads import get_census_detail
from db.models import Base, ProteinAnalysis

ROOT = Path(__file__).resolve().parent.parent
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
INDEX = (ROOT / "docs" / "decisions.md").read_text(encoding="utf-8")
READS = (ROOT / "app" / "reads.py").read_text(encoding="utf-8")
KABSCH_WRITER = (ROOT / "core" / "hold48_kabsch.py").read_text(encoding="utf-8")


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


def _write_kabsch_tree(root: Path, *, rmsd=1.25, jump=None, accepted=True):
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
        "R": None,
        "t": None,
    }
    if jump is not None:
        seam["max_ca_jump_angstrom"] = jump
    payload = {
        "algorithm": "kabsch_ca_then_winning_tile",
        "decision": "D-125",
        "parent_job_id": 2817,
        "tile_job_ids": [3673, 3630],
        "windows": [[1, 1656], [1529, 2368]],
        "accepted": accepted,
        "seams": [seam],
    }
    (dest / "provenance.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (dest / "seams.jsonl").write_text(json.dumps(seam) + "\n", encoding="utf-8")
    if accepted:
        (dest / "stitched.pdb").write_text("HEADER kabsch-path\n", encoding="utf-8")
    return dest


def test_d125_b_heading_exists_in_the_living_log():
    assert re.search(r"^### D-125-B — UI dual-path honesty", LOG, re.M)
    assert "does **not** re-implement persist" in LOG
    assert "Seams are not scientifically solved" in LOG


def test_missing_sibling_tree_is_honest_empty_no_invented_rmsd(tmp_path):
    block = read_kabsch_dual_path(
        tmp_path, parent_analysis_id=2817, parent_job_id=2817
    )
    assert block["present"] is False
    assert block["empty_reason"] == "no_kabsch_artifacts"
    assert block["seams"] == []
    assert block["persist_stem"] == "kabsch/2817"
    assert "rmsd" not in json.dumps(block["seams"])
    note = seam_note_for(block)
    assert "88.76" in note
    assert "not on disk" in note
    assert "PARKED" not in note
    assert "solved seam" in note.lower() or "not a solved" in note.lower()


def test_present_tree_names_both_paths_and_stems_do_not_collide(tmp_path):
    _write_kabsch_tree(tmp_path, rmsd=2.5)
    payload = dual_path_payload(tmp_path, parent_analysis_id=2817, parent_job_id=2817)
    asm = payload["assembler"]
    kabsch = payload["kabsch"]
    assert asm["persist_stem"] == ASSEMBLER_PERSIST_STEM == "stitched"
    assert kabsch["present"] is True
    assert kabsch["persist_stem"] == "kabsch/2817"
    assert kabsch["persist_stem"].startswith(KABSCH_PERSIST_STEM_PREFIX)
    assert asm["persist_stem"] != kabsch["persist_stem"]
    assert asm["default_served"] is True
    assert "not scientifically solved" in kabsch["label"]
    assert kabsch["seams"][0]["rmsd_angstrom"] == 2.5
    assert kabsch["seams"][0]["n_ca"] == 128


def test_max_ca_jump_is_honest_empty_unless_a_wrote_it(tmp_path):
    _write_kabsch_tree(tmp_path, rmsd=0.4, jump=None)
    missing = read_kabsch_dual_path(tmp_path, parent_analysis_id=2817)
    assert missing["seams"][0]["rmsd_angstrom"] == 0.4
    assert missing["seams"][0]["max_ca_jump_angstrom"] is None

    root2 = tmp_path / "with-jump"
    _write_kabsch_tree(root2, rmsd=0.4, jump=7.75)
    present = read_kabsch_dual_path(root2, parent_analysis_id=2817)
    assert present["seams"][0]["max_ca_jump_angstrom"] == 7.75


def test_project_seam_does_not_invent_numbers():
    row = project_seam({"n_ca": 3, "rmsd_angstrom": None, "refuse_reason": "overlap_ca_lt_3"})
    assert row["rmsd_angstrom"] is None
    assert row["max_ca_jump_angstrom"] is None
    assert row["n_ca"] == 3
    assert row["refuse_reason"] == "overlap_ca_lt_3"


def test_assembly_review_carries_dual_path_empty_and_does_not_collide_stems(tmp_path):
    eng = _engine()
    assembler_dir = tmp_path / "assembler" / "2817"
    with Session(eng) as s:
        _add_parent(s, assembler_dir)
        s.commit()
    detail = get_census_detail(eng, 2817, artifact_root=tmp_path / "empty-ops")
    review = detail["assembly_review"]
    assert review["dual_path"]["assembler"]["persist_stem"] == "stitched"
    assert review["dual_path"]["kabsch"]["present"] is False
    names = [d["name"] for d in review["downloads"]["stitched"]]
    assert names == ["stitched.pdb", "stitched_plddt.json", "stitched_pae.json"]
    assert all(not n.startswith("kabsch_") for n in names)
    assert "PARKED" not in review["seam_note"]
    assert "not on disk" in review["seam_note"]


def test_assembly_review_reads_sibling_tree_beside_assembler_dir(tmp_path):
    """A's tree is {root}/kabsch/{parent}/ — not the assembler {root}/{parent}/."""
    eng = _engine()
    ops = tmp_path / "ops"
    assembler_dir = ops / "2817"
    with Session(eng) as s:
        _add_parent(s, assembler_dir)
        s.commit()
    _write_kabsch_tree(ops, rmsd=3.1, jump=12.0)
    detail = get_census_detail(eng, 2817, artifact_root=ops)
    kabsch = detail["assembly_review"]["dual_path"]["kabsch"]
    assert kabsch["present"] is True
    assert kabsch["persist_stem"] == "kabsch/2817"
    assert kabsch["seams"][0]["rmsd_angstrom"] == 3.1
    assert kabsch["seams"][0]["max_ca_jump_angstrom"] == 12.0
    # Assembler downloads are still the assembler stem.
    names = [d["name"] for d in detail["assembly_review"]["downloads"]["stitched"]]
    assert "stitched.pdb" in names
    assert "kabsch_stitched.pdb" not in names


def test_b_does_not_reimplement_persist_writer():
    reader = (ROOT / "app" / "kabsch_path_read.py").read_text(encoding="utf-8")
    assert "def write_kabsch_restitch" not in reader
    assert "def write_provenance" not in reader
    assert "write_kabsch_restitch" in KABSCH_WRITER
    assert "dual_path_payload" in READS
    assert "WAVE1_WAVE2_STITCHED_PARENT_IDS" not in (ROOT / "core" / "scorer.py").read_text(
        encoding="utf-8"
    )


def test_empty_block_stems_never_equal_assembler_stitched():
    empty = empty_kabsch_block(parent_id=2817)
    assert empty["persist_stem"] != ASSEMBLER_PERSIST_STEM
    assert empty["persist_stem"].startswith("kabsch/")
