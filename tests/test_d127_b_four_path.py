"""D-127-B — UI four-path honesty + the mandatory Method addendum. These must go red.

B reads A's sibling ``piecewise_kabsch/{parent}/`` tree. It does not
persist, does not invent per-piece RMSD / piece counts / linker counts,
and must not collide persist stems with assembler ``stitched``, D-125
``kabsch/``, or D-126 ``confidence_kabsch/``. Default served PDB stays
assembler. A missing tree must not imply a D-127 path exists.

⚠ The distinctive D-127 hazard these pin: a seam holds *k* pieces, and
collapsing them into one number would re-create the D-126 lie surface
inside the fix for it. B renders per-piece rows and derives no average.

⚠ Spec §7 makes the Method addendum **mandatory** — D-127 is not "done"
without it. Those checks live here too, not in a follow-up.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.confidence_kabsch_path_read import CONFIDENCE_KABSCH_PERSIST_STEM_PREFIX
from app.kabsch_path_read import ASSEMBLER_PERSIST_STEM, KABSCH_PERSIST_STEM_PREFIX
from app.piecewise_kabsch_path_read import (
    EMPTY_REASON_NO_PIECE_ROWS,
    PIECEWISE_KABSCH_PERSIST_STEM_PREFIX,
    empty_piecewise_kabsch_block,
    four_path_payload,
    project_piecewise_seam,
    read_piecewise_kabsch_path,
    seam_note_for_four,
)
from app.reads import get_census_detail
from db.models import Base, ProteinAnalysis

ROOT = Path(__file__).resolve().parent.parent
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
INDEX = (ROOT / "docs" / "decisions.md").read_text(encoding="utf-8")
PLAN_TEST = (ROOT / "docs" / "Test_Plan.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
READS = (ROOT / "app" / "reads.py").read_text(encoding="utf-8")
READER = (ROOT / "app" / "piecewise_kabsch_path_read.py").read_text(encoding="utf-8")
D127_WRITER_PATH = ROOT / "core" / "hold48_piecewise_kabsch.py"
D127_WRITER = D127_WRITER_PATH.read_text(encoding="utf-8")
D126_WRITER = (ROOT / "core" / "hold48_confidence_kabsch.py").read_text(encoding="utf-8")
D125_WRITER = (ROOT / "core" / "hold48_kabsch.py").read_text(encoding="utf-8")
METHOD_MD = (ROOT / "docs" / "method-hold48-tiles.md").read_text(encoding="utf-8")
METHOD_NOTE = (ROOT / "ui" / "src" / "components" / "MethodNote.jsx").read_text(
    encoding="utf-8"
)
REVIEW_JSX = (ROOT / "ui" / "src" / "components" / "AssemblyReview.jsx").read_text(
    encoding="utf-8"
)
PROV_JSX = (ROOT / "ui" / "src" / "components" / "Provenance.jsx").read_text(
    encoding="utf-8"
)

# A's module on main (`e49bf34`). B reads it; B does not edit it.
D127_WRITER_SHA256 = "ad48b2be577b987466274000c508a621792bc029bb9e087eec94ba7237f13e04"

FORBIDDEN = (
    "seams solved",
    "kabsch aligned",
    "full-length af-quality",
    "we ran kabsch",
)


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


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
    for aid, start, end, idx, span in (
        (3673, 1, 1656, 0, 1656),
        (3630, 1529, 2368, 1, 840),
    ):
        session.add(
            ProteinAnalysis(
                id=aid,
                input_type="uniprot",
                input_value="Q9P273",
                cohort_tranche=5,
                pdb_path=f"/tmp/tile{aid}.pdb",
                pae_json_path=f"/tmp/tile{aid}_pae.json",
                mean_plddt=70.0,
                meta={
                    "hold48_kind": "tile",
                    "parent_job_id": 2817,
                    "tile_start": start,
                    "tile_end": end,
                    "tile_index": idx,
                    "span_aa": span,
                },
            )
        )


def _write_piecewise_tree(
    root: Path,
    *,
    pieces=None,
    linker_n=6,
    max_linker_ca_jump=2.4,
    full_overlap=7.5,
    jump=9.1,
    refuse_reason=None,
    accepted=True,
    include_pieces=True,
    include_parent_fields=True,
):
    """A D-127 seam as A's ``PiecewiseSeamRecord.to_json_row`` writes it."""
    dest = root / "piecewise_kabsch" / "2817"
    dest.mkdir(parents=True, exist_ok=True)
    if pieces is None:
        pieces = [
            {
                "interval": [1540, 1600],
                "n_ca": 61,
                "rmsd_angstrom": 1.8,
                "refuse_reason": None,
                "R": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                "t": [0.0, 0.0, 0.0],
            },
            {
                "interval": [1610, 1650],
                "n_ca": 41,
                "rmsd_angstrom": 6.25,
                "refuse_reason": None,
                "R": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                "t": [0.0, 0.0, 0.0],
            },
        ]
    seam = {
        "moving_tile_index": 2,
        "reference_tile_index": 1,
        "overlap_start": 1529,
        "overlap_end": 1656,
        "refuse_reason": refuse_reason,
    }
    if include_pieces:
        seam["pieces"] = pieces
    if include_parent_fields:
        seam["linker_n"] = linker_n
        seam["max_linker_ca_jump"] = max_linker_ca_jump
        seam["rmsd_full_overlap_angstrom"] = full_overlap
        seam["max_ca_jump_angstrom"] = jump
    payload = {
        "algorithm": "piecewise_domain_kabsch_then_winning_tile",
        "decision": "D-127",
        "parent_job_id": 2817,
        "accepted": accepted,
        "seams": [seam],
        "rmsd_refuse_angstrom": 10.0,
        "no_trim_loop": True,
    }
    (dest / "provenance.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (dest / "seams.jsonl").write_text(json.dumps(seam) + "\n", encoding="utf-8")
    if accepted:
        (dest / "stitched.pdb").write_text("HEADER piecewise-kabsch-path\n", encoding="utf-8")
    return dest


def _write_kabsch_tree(root: Path, *, rmsd=1.25):
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
        "accepted": True,
        "seams": [seam],
    }
    (dest / "provenance.json").write_text(json.dumps(payload) + "\n", encoding="utf-8")
    (dest / "seams.jsonl").write_text(json.dumps(seam) + "\n", encoding="utf-8")
    return dest


def _write_confidence_tree(root: Path, *, rmsd=2.5):
    dest = root / "confidence_kabsch" / "2817"
    dest.mkdir(parents=True, exist_ok=True)
    seam = {
        "moving_tile_index": 2,
        "reference_tile_index": 1,
        "overlap_start": 1529,
        "overlap_end": 1656,
        "n_ca": 128,
        "n_ca_eff": 96,
        "rmsd_angstrom": rmsd,
        "rmsd_full_overlap_angstrom": 8.0,
        "max_ca_jump_angstrom": 4.2,
        "trim_rounds": 2,
        "refuse_reason": None,
    }
    payload = {
        "algorithm": "overlap_confidence_kabsch_then_winning_tile",
        "decision": "D-126",
        "parent_job_id": 2817,
        "accepted": True,
        "seams": [seam],
    }
    (dest / "provenance.json").write_text(json.dumps(payload) + "\n", encoding="utf-8")
    (dest / "seams.jsonl").write_text(json.dumps(seam) + "\n", encoding="utf-8")
    return dest


# ── T-1134 · living log ───────────────────────────────────────────────────


def test_d127_b_heading_exists_in_the_living_log():
    """D-001 naming: the check is the heading, not a citation of one."""
    assert re.search(r"^### D-127-B — UI four-path honesty", LOG, re.M)
    assert re.search(r"^### D-127-A — Piecewise / domain-aware Kabsch core", LOG, re.M)
    assert "does **not** re-implement persist" in LOG
    assert "Seams are not scientifically solved" in LOG
    assert "e49bf34" in LOG


def test_trinity_locked_bar_cites_d127a_and_spec_sections_six_and_seven():
    """Trinity bar LOCKED: cite Spec §6 + §7; served path is assembler."""
    start = LOG.find("### D-127-B — UI four-path honesty")
    end = LOG.find("### D-127-A —", start + 1)
    section = LOG[start:end] if start != -1 and end != -1 else ""
    assert section, "D-127-B heading must exist so the LOCKED bar can be pinned"
    flat = _flat(section)
    assert "LOCKED" in section
    assert "Spec §6" in section
    assert "§7" in section
    assert "piecewise_kabsch" in section
    assert "Default served = assembler" in section
    assert "rmsd_full_overlap_angstrom" in section
    assert "max_ca_jump_angstrom" in section
    assert "linker_n" in section
    assert "max_linker_ca_jump" in section
    assert "refuse-before-transform" in flat
    assert "mandatory" in flat.lower()
    assert "not “done” without Method" in flat or "not \u201cdone\u201d without Method" in flat
    assert "No ops restitch" in flat or "no ops restitch" in flat.lower()
    assert "e49bf34" in section
    # Ship index carries the same bar.
    assert "e49bf34" in INDEX
    assert "four-path" in INDEX.lower()
    assert "Spec §7" in INDEX or "§7" in INDEX


# ── T-1135 · honest empty ─────────────────────────────────────────────────


def test_missing_piecewise_tree_does_not_imply_d127_path_or_invent_metrics(tmp_path):
    block = read_piecewise_kabsch_path(
        tmp_path, parent_analysis_id=2817, parent_job_id=2817
    )
    assert block["present"] is False
    assert block["empty_reason"] == "no_piecewise_kabsch_artifacts"
    assert block["seams"] == []
    assert block["persist_stem"] == "piecewise_kabsch/2817"
    assert block["success_pdb_on_disk"] is False
    dumped = json.dumps(block["seams"])
    assert "rmsd" not in dumped
    assert "pieces" not in dumped
    assert "linker" not in dumped
    note = seam_note_for_four({"present": False}, {"present": False}, block)
    assert "88.76" in note
    assert "fourth path" not in note.lower()
    assert "piecewise" not in note.lower()
    assert "not a solved seam" in note.lower()
    for phrase in FORBIDDEN:
        assert phrase not in note.lower()


def test_seam_note_names_the_fourth_path_only_when_the_tree_is_on_disk(tmp_path):
    _write_kabsch_tree(tmp_path)
    _write_confidence_tree(tmp_path)
    triple_only = four_path_payload(tmp_path, parent_analysis_id=2817, parent_job_id=2817)
    note3 = seam_note_for_four(
        triple_only["kabsch"],
        triple_only["confidence_kabsch"],
        triple_only["piecewise_kabsch"],
    )
    assert "third path" in note3.lower()
    assert "fourth path" not in note3.lower()

    _write_piecewise_tree(tmp_path)
    full = four_path_payload(tmp_path, parent_analysis_id=2817, parent_job_id=2817)
    note4 = seam_note_for_four(
        full["kabsch"], full["confidence_kabsch"], full["piecewise_kabsch"]
    )
    assert "fourth path" in note4.lower()
    assert "per UniProt domain" in note4
    assert "default served structure" in note4
    for phrase in FORBIDDEN:
        assert phrase not in note4.lower()


# ── T-1136 · four stems, no collision ─────────────────────────────────────


def test_present_tree_names_four_paths_and_stems_do_not_collide(tmp_path):
    _write_kabsch_tree(tmp_path, rmsd=2.5)
    _write_confidence_tree(tmp_path, rmsd=3.4)
    _write_piecewise_tree(tmp_path)
    payload = four_path_payload(tmp_path, parent_analysis_id=2817, parent_job_id=2817)
    asm = payload["assembler"]
    kabsch = payload["kabsch"]
    d126 = payload["confidence_kabsch"]
    d127 = payload["piecewise_kabsch"]
    assert asm["persist_stem"] == ASSEMBLER_PERSIST_STEM == "stitched"
    assert asm["default_served"] is True
    assert kabsch["persist_stem"] == "kabsch/2817"
    assert kabsch["persist_stem"].startswith(KABSCH_PERSIST_STEM_PREFIX)
    assert d126["persist_stem"] == "confidence_kabsch/2817"
    assert d126["persist_stem"].startswith(CONFIDENCE_KABSCH_PERSIST_STEM_PREFIX)
    assert d127["present"] is True
    assert d127["persist_stem"] == "piecewise_kabsch/2817"
    assert d127["persist_stem"].startswith(PIECEWISE_KABSCH_PERSIST_STEM_PREFIX)
    stems = {
        asm["persist_stem"],
        kabsch["persist_stem"],
        d126["persist_stem"],
        d127["persist_stem"],
    }
    assert len(stems) == 4
    # A D-127 stem must not read as assembler or as a D-125 / D-126 success.
    assert not d127["persist_stem"].startswith("kabsch/")
    assert not d127["persist_stem"].startswith("confidence_kabsch/")
    assert "not scientifically solved" in d127["label"]
    assert d127["algorithm"] == "piecewise_domain_kabsch_then_winning_tile"
    assert d127["decision"] == "D-127"
    assert d127["success_pdb_on_disk"] is True


def test_empty_block_stems_never_equal_assembler_d125_or_d126():
    empty = empty_piecewise_kabsch_block(parent_id=2817)
    assert empty["persist_stem"] != ASSEMBLER_PERSIST_STEM
    assert empty["persist_stem"].startswith("piecewise_kabsch/")
    assert not empty["persist_stem"].startswith("kabsch/")
    assert not empty["persist_stem"].startswith("confidence_kabsch/")


# ── T-1137 · per-piece rows are the unit of disclosure ────────────────────


def test_per_piece_rows_render_from_as_json_and_are_not_averaged(tmp_path):
    _write_piecewise_tree(tmp_path)
    block = read_piecewise_kabsch_path(tmp_path, parent_analysis_id=2817)
    seam = block["seams"][0]
    pieces = seam["pieces"]
    assert len(pieces) == 2
    assert pieces[0]["interval"] == [1540, 1600]
    assert pieces[0]["n_ca"] == 61
    assert pieces[0]["rmsd_angstrom"] == 1.8
    assert pieces[0]["refuse_reason"] is None
    assert pieces[0]["accepted"] is True
    assert pieces[1]["interval"] == [1610, 1650]
    assert pieces[1]["rmsd_angstrom"] == 6.25
    # ⚠ No collapsed seam number anywhere in the projection: the mean of
    # 1.8 and 6.25 is 4.025 and the max is 6.25. Either appearing as a
    # seam-level field would be the D-126 lie surface re-created.
    assert "rmsd_angstrom" not in seam
    assert "pieces_mean_rmsd" not in seam
    assert "pieces_accepted_n" not in seam
    assert "n_pieces_passing" not in seam
    dumped = json.dumps(seam)
    assert "4.02" not in dumped
    # And the reader must not compute one either.
    assert "mean(" not in READER
    assert "statistics" not in READER
    assert "sum(" not in READER


def test_parent_disclosure_and_linker_fields_render_when_a_wrote_them(tmp_path):
    _write_piecewise_tree(
        tmp_path, full_overlap=12.75, jump=31.4, linker_n=9, max_linker_ca_jump=3.05
    )
    seam = read_piecewise_kabsch_path(tmp_path, parent_analysis_id=2817)["seams"][0]
    assert seam["rmsd_full_overlap_angstrom"] == 12.75
    assert seam["max_ca_jump_angstrom"] == 31.4
    assert seam["linker_n"] == 9
    assert seam["max_linker_ca_jump"] == 3.05
    assert seam["overlap_start"] == 1529
    assert seam["overlap_end"] == 1656


def test_refuse_before_transform_stays_null_never_zero(tmp_path):
    """Spec §1 / §5: a refuse before any transform has nothing to measure."""
    _write_piecewise_tree(
        tmp_path,
        pieces=[
            {"interval": [1540, 1545], "n_ca": 2, "rmsd_angstrom": None,
             "refuse_reason": "overlap_ca_lt_3", "R": None, "t": None},
        ],
        include_parent_fields=False,
        refuse_reason="overlap_ca_lt_3",
        accepted=False,
    )
    seam = read_piecewise_kabsch_path(tmp_path, parent_analysis_id=2817)["seams"][0]
    assert seam["rmsd_full_overlap_angstrom"] is None
    assert seam["max_ca_jump_angstrom"] is None
    assert seam["linker_n"] is None
    assert seam["max_linker_ca_jump"] is None
    assert seam["pieces"][0]["rmsd_angstrom"] is None
    assert seam["pieces"][0]["n_ca"] == 2
    assert seam["pieces"][0]["refuse_reason"] == "overlap_ca_lt_3"
    assert seam["pieces"][0]["accepted"] is False
    # A null is not a zero.
    for key in (
        "rmsd_full_overlap_angstrom",
        "max_ca_jump_angstrom",
        "max_linker_ca_jump",
    ):
        assert seam[key] != 0
        assert seam[key] is not False


def test_missing_piece_list_is_an_absence_with_a_reason_not_zero_pieces(tmp_path):
    _write_piecewise_tree(tmp_path, include_pieces=False, accepted=False, refuse_reason="no_domain_pieces")
    seam = read_piecewise_kabsch_path(tmp_path, parent_analysis_id=2817)["seams"][0]
    assert seam["pieces"] == []
    assert seam["pieces_empty_reason"] == EMPTY_REASON_NO_PIECE_ROWS
    assert seam["refuse_reason"] == "no_domain_pieces"


def test_project_seam_does_not_invent_numbers():
    row = project_piecewise_seam(
        {"refuse_reason": "no_domain_pieces", "moving_tile_index": 2}
    )
    assert row["pieces"] == []
    assert row["pieces_empty_reason"] == EMPTY_REASON_NO_PIECE_ROWS
    assert row["rmsd_full_overlap_angstrom"] is None
    assert row["max_ca_jump_angstrom"] is None
    assert row["linker_n"] is None
    assert row["max_linker_ca_jump"] is None
    assert row["refuse_reason"] == "no_domain_pieces"


def test_projection_drops_the_rigid_transform_itself():
    """R / t are A's record, not a card measurement a reader could mistake for a pose."""
    row = project_piecewise_seam(
        {
            "pieces": [
                {
                    "interval": [1, 10],
                    "n_ca": 8,
                    "rmsd_angstrom": 1.0,
                    "refuse_reason": None,
                    "R": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                    "t": [3.0, 4.0, 5.0],
                }
            ]
        }
    )
    assert "R" not in row["pieces"][0]
    assert "t" not in row["pieces"][0]


# ── T-1138 · fail-closed ──────────────────────────────────────────────────


def test_refused_parent_is_fail_closed_and_not_presented_as_d127_success(tmp_path):
    dest = _write_piecewise_tree(
        tmp_path,
        pieces=[
            {"interval": [1540, 1600], "n_ca": 61, "rmsd_angstrom": 12.4,
             "refuse_reason": "rmsd_gt_10", "R": None, "t": None},
        ],
        accepted=False,
        refuse_reason="rmsd_gt_10",
    )
    # All-or-nothing: a leftover stitched.pdb must not become a D-127 success.
    (dest / "stitched.pdb").write_text("HEADER leftover\n", encoding="utf-8")
    block = read_piecewise_kabsch_path(tmp_path, parent_analysis_id=2817)
    assert block["present"] is True
    assert block["accepted"] is False
    assert block["success_pdb_on_disk"] is False
    assert block["seams"][0]["pieces"][0]["refuse_reason"] == "rmsd_gt_10"
    assert block["seams"][0]["pieces"][0]["accepted"] is False
    dumped = json.dumps(block).lower()
    assert "fixed" not in dumped
    for phrase in FORBIDDEN:
        assert phrase not in dumped


def test_ten_angstrom_gate_is_reported_not_moved(tmp_path):
    _write_piecewise_tree(tmp_path)
    block = read_piecewise_kabsch_path(tmp_path, parent_analysis_id=2817)
    assert block["rmsd_refuse_angstrom"] == 10.0
    assert empty_piecewise_kabsch_block(parent_id=2817)["rmsd_refuse_angstrom"] == 10.0
    # B must not carry its own threshold constant.
    assert "RMSD_REFUSE_ANGSTROM = " not in READER
    assert "from core.hold48_piecewise_kabsch import" in READER


# ── T-1139 · assembly_review wiring ───────────────────────────────────────


def test_assembly_review_carries_four_path_empty_and_does_not_imply_d127(tmp_path):
    eng = _engine()
    assembler_dir = tmp_path / "assembler" / "2817"
    with Session(eng) as s:
        _add_parent(s, assembler_dir)
        s.commit()
    detail = get_census_detail(eng, 2817, artifact_root=tmp_path / "empty-ops")
    review = detail["assembly_review"]
    assert review["four_path"]["piecewise_kabsch"]["present"] is False
    assert review["four_path"]["assembler"]["default_served"] is True
    # D-125-B / D-126-B views survive unchanged (anti-gut).
    assert review["dual_path"]["assembler"]["persist_stem"] == "stitched"
    assert review["dual_path"]["kabsch"]["present"] is False
    assert review["triple_path"]["confidence_kabsch"]["present"] is False
    names = [d["name"] for d in review["downloads"]["stitched"]]
    assert names == ["stitched.pdb", "stitched_plddt.json", "stitched_pae.json"]
    assert all(not n.startswith("piecewise_kabsch") for n in names)
    assert "fourth path" not in review["seam_note"].lower()
    assert "not on disk" in review["seam_note"]


def test_assembly_review_reads_fourth_sibling_tree_beside_assembler_dir(tmp_path):
    """A's tree is {root}/piecewise_kabsch/{parent}/ — not assembler {root}/{parent}/."""
    eng = _engine()
    ops = tmp_path / "ops"
    assembler_dir = ops / "2817"
    with Session(eng) as s:
        _add_parent(s, assembler_dir)
        s.commit()
    _write_kabsch_tree(ops, rmsd=3.1)
    _write_confidence_tree(ops, rmsd=4.4)
    _write_piecewise_tree(ops, full_overlap=9.4, jump=28.6, linker_n=12)
    review = get_census_detail(eng, 2817, artifact_root=ops)["assembly_review"]
    d127 = review["four_path"]["piecewise_kabsch"]
    assert d127["present"] is True
    assert d127["persist_stem"] == "piecewise_kabsch/2817"
    seam = d127["seams"][0]
    assert [p["interval"] for p in seam["pieces"]] == [[1540, 1600], [1610, 1650]]
    assert seam["rmsd_full_overlap_angstrom"] == 9.4
    assert seam["max_ca_jump_angstrom"] == 28.6
    assert seam["linker_n"] == 12
    assert "fourth path" in review["seam_note"].lower()
    # Default served PDB is still the assembler one, under the assembler stem.
    assert review["four_path"]["assembler"]["default_served"] is True
    names = [d["name"] for d in review["downloads"]["stitched"]]
    assert "stitched.pdb" in names
    assert "piecewise_kabsch_stitched.pdb" not in names
    # The three earlier paths are untouched.
    assert review["four_path"]["kabsch"]["seams"][0]["rmsd_angstrom"] == 3.1
    assert review["four_path"]["confidence_kabsch"]["seams"][0]["rmsd_angstrom"] == 4.4
    assert review["triple_path"]["confidence_kabsch"]["present"] is True


# ── T-1140 · B does not write, does not restitch, does not edit A ─────────


def test_b_does_not_reimplement_persist_writer():
    assert "def write_piecewise_kabsch_restitch" not in READER
    assert "def write_provenance" not in READER
    assert "def write_confidence_kabsch_restitch" not in READER
    assert "def write_kabsch_restitch" not in READER
    assert "write_piecewise_kabsch_restitch" in D127_WRITER
    assert "four_path_payload" in READS


def test_b_does_not_invoke_a_restitch_of_the_twenty_seven():
    """Emma pin: UI + Method only. B must not call the A writer or the CLI."""
    routes = (ROOT / "app" / "read_routes.py").read_text(encoding="utf-8")
    for text, label in (
        (READER, "piecewise_kabsch_path_read"),
        (READS, "reads"),
        (routes, "read_routes"),
        (REVIEW_JSX, "AssemblyReview"),
        (METHOD_NOTE, "MethodNote"),
        (PROV_JSX, "Provenance"),
    ):
        assert "write_piecewise_kabsch_restitch(" not in text, label
        assert "write_confidence_kabsch_restitch(" not in text, label
        assert "write_kabsch_restitch(" not in text, label
        assert "scripts.piecewise_kabsch_restitch" not in text, label
        lowered = text.lower()
        for phrase in FORBIDDEN:
            assert phrase not in lowered, f"{label}: {phrase}"


def test_algorithm_modules_are_not_edited_by_this_ui_pr():
    """Hard stop: B reads. A's bytes stay exactly as they landed on main."""
    assert hashlib.sha256(D127_WRITER_PATH.read_bytes()).hexdigest() == D127_WRITER_SHA256
    assert "def write_piecewise_kabsch_restitch" in D127_WRITER
    assert "def write_confidence_kabsch_restitch" in D126_WRITER
    assert "def write_kabsch_restitch" in D125_WRITER
    assert "piecewise" not in D125_WRITER.lower()
    assert "piecewise" not in D126_WRITER.lower()


# ── T-1141 · the mandatory Method addendum (Spec §7) ──────────────────────


def test_d127_b_method_addendum_names_the_stitch_path_train():
    """Spec §7 is mandatory: the train, in order, on both surfaces."""
    for text, label in ((METHOD_MD, "method-hold48-tiles.md"), (METHOD_NOTE, "MethodNote.jsx")):
        flat = _flat(text)
        lowered = flat.lower()
        assert "stitch-path train" in lowered, label
        # All four steps, named.
        assert "assembler" in lowered, label
        assert "D-125 Kabsch" in flat, label
        assert "D-126 confidence" in flat, label
        assert "D-127 piecewise" in flat, label
        # The D-126 lesson is the reason the family is multi-rigid.
        assert "28–68" in flat or "28-68" in flat, label
        assert "2939" in flat and "3272" in flat and "3432" in flat, label
        assert "full-overlap" in lowered, label
        # D-127's own shape.
        assert "per UniProt domain" in flat or "per uniprot domain" in lowered, label
        assert "no trim loop" in lowered, label
        assert "linker" in lowered, label
        assert "N-terminal" in flat, label


def test_d127_b_method_addendum_names_the_refuse_table_and_keeps_the_gate():
    for text, label in ((METHOD_MD, "method-hold48-tiles.md"), (METHOD_NOTE, "MethodNote.jsx")):
        flat = _flat(text)
        lowered = flat.lower()
        assert "10.0" in flat, label
        assert "fewer than three" in lowered, label
        assert "in a line" in lowered or "collinear" in lowered, label
        assert "no domain covers the glue" in lowered, label
        assert "gate" in lowered, label
        assert "stays" in lowered, label
        assert "a refuse writes a record" in lowered, label
        # A refuse is not a repair, and 0-of-3 does not move the bar.
        assert "not" in lowered and "fixed" in lowered, label


def test_d127_b_method_addendum_names_seam_disclosure_as_measurement():
    for text, label in ((METHOD_MD, "method-hold48-tiles.md"), (METHOD_NOTE, "MethodNote.jsx")):
        flat = _flat(text)
        lowered = flat.lower()
        assert "measurement" in lowered, label
        assert "not a verdict" in lowered, label
        assert "default served" in lowered, label
        assert "not scientifically solved" in lowered, label
        assert "not medical advice" in lowered, label
        assert "does not invent" in lowered, label
        assert "piecewise_kabsch" in lowered, label
        for phrase in FORBIDDEN:
            assert phrase not in lowered, f"{label}: {phrase}"


def test_method_addendum_does_not_gut_d121_d125b_or_d126b():
    """Additive. The earlier sections are the reader's context, not debris."""
    for text, label in ((METHOD_MD, "method-hold48-tiles.md"), (METHOD_NOTE, "MethodNote.jsx")):
        flat = _flat(text)
        assert "winner-tile assembler" in flat, label
        assert "not Kabsch" in flat, label
        assert "88.76" in flat, label
        assert "What Kabsch does" in flat, label
        assert "What Kabsch does not do" in flat, label
        assert "What overlap-confidence Kabsch does" in flat, label
        assert "What overlap-confidence Kabsch does not do" in flat, label
        assert "CLOSED" in text, label
    assert "Addendum D-125-B" in METHOD_MD
    assert "Addendum D-126-B" in METHOD_MD
    assert "Addendum D-127-B" in METHOD_MD
    assert 'data-testid="hold48-explainer"' in METHOD_NOTE
    assert 'data-testid="kabsch-method-addendum"' in METHOD_NOTE
    assert 'data-testid="confidence-kabsch-method-addendum"' in METHOD_NOTE
    assert 'data-testid="piecewise-kabsch-method-addendum"' in METHOD_NOTE
    assert "#229" in METHOD_MD


# ── T-1142 · the D-127 OPS result, disclosed as recorded ─────────────────
#
# Matt GO via Emma 2026-09-05: Method §7 must carry the ops facts. These
# figures are NOT measured by this PR — they are recorded as handed over,
# with that attribution. What these tests pin is that the surface states
# them, states the regress beside the accept count, and does not soften.

OPS_REFUSE_HISTOGRAM = {
    "linker_jump_gt_10": (7, (2938, 2939, 3179, 3190, 3321, 3368, 3566)),
    "rmsd_gt_10": (2, (3272, 3394)),
    "no_domain_pieces": (1, (3432,)),
}
OPS_PRIMARY_THREE_REFUSALS = {
    2939: "linker_jump_gt_10",
    3272: "rmsd_gt_10",
    3432: "no_domain_pieces",
}


def test_ops_figures_are_internally_consistent_before_they_are_quoted():
    """A consistency check is not a measurement — but an inconsistent
    figure must not reach a surface that calls itself honest."""
    assert 17 + 10 + 0 == 27
    assert sum(n for n, _ in OPS_REFUSE_HISTOGRAM.values()) == 10
    for reason, (n, ids) in OPS_REFUSE_HISTOGRAM.items():
        assert len(ids) == n, reason
        assert len(set(ids)) == n, reason
    for pid, reason in OPS_PRIMARY_THREE_REFUSALS.items():
        assert pid in OPS_REFUSE_HISTOGRAM[reason][1], pid
    # recovered_of_primary_three = 0 means none of the three is a PASS.
    assert len(OPS_PRIMARY_THREE_REFUSALS) == 3


def test_method_discloses_the_d127_ops_run_and_its_named_regress():
    """PASS 17 / REFUSE 10 / FAIL 0 never ships without the regress beside it."""
    for text, label in ((METHOD_MD, "method-hold48-tiles.md"), (METHOD_NOTE, "MethodNote.jsx")):
        flat = _flat(text)
        lowered = flat.lower()
        assert "17" in flat, label
        assert "10" in flat, label
        assert "PASS" in flat and "REFUSE" in flat and "FAIL" in flat, label
        assert "27" in flat, label
        assert "e49bf34" in flat, label
        # Named regress (Spec §11): a drop is never buried in an accept count.
        assert "5" in flat and "D-125" in flat, label
        assert "7" in flat and "D-126" in flat, label
        assert "n_d126_refuse_d127_pass" in flat, label
        assert "named finding" in lowered, label
        # recovered_of_primary_three = 0, with each reason named.
        assert "recovered_of_primary_three" in flat, label
        for pid, reason in OPS_PRIMARY_THREE_REFUSALS.items():
            assert str(pid) in flat, f"{label}: {pid}"
            assert reason in flat, f"{label}: {reason}"
        # Full refuse histogram, counts and ids.
        for reason, (n, ids) in OPS_REFUSE_HISTOGRAM.items():
            assert reason in flat, f"{label}: {reason}"
            assert f"{n}" in flat, f"{label}: {reason} count"
            for pid in ids:
                assert str(pid) in flat, f"{label}: {reason} {pid}"


def test_method_says_plainly_that_d126_remains_the_best_path_so_far():
    """Matt GO: say it plainly. A hedge here is the softening the GO forbids."""
    for text, label in ((METHOD_MD, "method-hold48-tiles.md"), (METHOD_NOTE, "MethodNote.jsx")):
        lowered = _flat(text).lower()
        assert "d-126 remains the best experimental path" in lowered, label
        assert "so far" in lowered, label
        # The negative result is stated, not implied.
        assert "did not pay off" in lowered, label


def test_method_refuses_to_loosen_a_gate_or_flip_the_served_path():
    for text, label in ((METHOD_MD, "method-hold48-tiles.md"), (METHOD_NOTE, "MethodNote.jsx")):
        flat = _flat(text)
        lowered = flat.lower()
        assert "no threshold moved" in lowered, label
        assert "10.0 Å" in flat, label
        assert "trim loop" in lowered, label
        assert "blend" in lowered, label
        assert "allowed outcome" in lowered, label
        assert "default served structure is still the assembler" in lowered, label
        assert "never a pass count" in lowered, label
        # Recorded is not solved, said about the 17 specifically.
        assert "recorded outcomes" in lowered, label
        assert "not 17 solved joins" in lowered, label
        for phrase in FORBIDDEN:
            assert phrase not in lowered, f"{label}: {phrase}"


def test_ops_disclosure_names_its_provenance_and_disclaims_measurement():
    """D-016: as-recorded ops numbers must carry the artefact, not pose as ours."""
    for text, label in ((METHOD_MD, "method-hold48-tiles.md"), (METHOD_NOTE, "MethodNote.jsx")):
        lowered = _flat(text).lower()
        assert "as recorded" in lowered, label
        assert "emma" in lowered, label
        assert "not re-measured here" in lowered, label
    log_flat = _flat(LOG).lower()
    assert "not run, not queried, and not re-measured in this pr" in log_flat
    assert "d-127-b amendment 1" in log_flat
    assert "recovered_of_primary_three" in LOG
    assert "n_d126_refuse_d127_pass" in LOG


def test_this_pr_ships_no_ops_run_no_revised_spec_and_no_fly_post():
    """Matt GO hard stops: B only. Disclosure is not an ops lane."""
    for text, label in (
        (READER, "piecewise_kabsch_path_read"),
        (READS, "reads"),
        (REVIEW_JSX, "AssemblyReview"),
        (METHOD_NOTE, "MethodNote"),
    ):
        lowered = text.lower()
        assert "requests.post" not in lowered, label
        assert "fly.io" not in lowered, label
        assert "scripts.piecewise_kabsch_restitch" not in lowered, label
    # No revised stitch-algorithm Spec was written by this PR: the family
    # is still exactly D-125 / D-126 / D-127, and D-127's §1–§5 are intact.
    stitch_specs = sorted(
        p.name
        for p in (ROOT / "docs").glob("SPEC-*.md")
        if "kabsch" in p.name
    )
    assert stitch_specs == [
        "SPEC-kabsch-restitch.md",
        "SPEC-overlap-confidence-kabsch.md",
        "SPEC-piecewise-domain-kabsch.md",
    ], stitch_specs
    spec = (ROOT / "docs" / "SPEC-piecewise-domain-kabsch.md").read_text(encoding="utf-8")
    assert "10.0" in spec
    assert "do not raise" in _flat(spec).lower()
    assert "0-of-3 recovered is allowed" in _flat(spec).lower()
    # And the gate constants A fits against are untouched at their live
    # values, not merely unedited in one file (see also the sha pin).
    from core.hold48_piecewise_kabsch import RMSD_REFUSE_ANGSTROM, WEIGHT_EPSILON

    assert RMSD_REFUSE_ANGSTROM == 10.0
    assert WEIGHT_EPSILON == 1e-3


def test_method_obligation_is_recorded_as_discharged_by_this_pr():
    """Spec §7: D-127 is not 'done' without Method. The log/index must say B did it."""
    log_flat = _flat(LOG).lower()
    index_flat = _flat(INDEX).lower()
    assert "mandatory" in log_flat
    assert "silent code-only" in log_flat
    assert "d-127-b" in index_flat
    assert "method" in index_flat
    assert "discharge" in index_flat


# ── UI wiring pins (the JSX can go red in vitest too) ─────────────────────


def test_review_card_renders_pieces_and_never_derives_a_seam_average():
    assert 'data-testid="d127-seams"' in REVIEW_JSX
    assert 'data-testid="d127-accepted"' in REVIEW_JSX
    assert "piecewise_kabsch" in REVIEW_JSX
    assert "one row per piece" in REVIEW_JSX
    assert "rmsd_full_overlap_angstrom" in REVIEW_JSX
    assert "max_ca_jump_angstrom" in REVIEW_JSX
    assert "linker_n" in REVIEW_JSX
    assert "max_linker_ca_jump" in REVIEW_JSX
    # No arithmetic over the piece list in the card.
    assert ".reduce(" not in REVIEW_JSX
    assert "Math.min" not in REVIEW_JSX
    assert "Math.max" not in REVIEW_JSX


def test_provenance_names_the_fourth_persist_stem():
    assert 'data-testid="d127-persist-stem"' in PROV_JSX
    assert "piecewise_kabsch" in PROV_JSX
    assert "four paths, not one population" in PROV_JSX
    assert "assembler until a later ops restitch GO names a swap" in PROV_JSX


def test_test_plan_and_architecture_record_d127_b():
    assert "T-1134" in PLAN_TEST
    assert "T-1141" in PLAN_TEST
    assert "D-127-B" in PLAN_TEST
    assert "piecewise_kabsch_path_read" in ARCH
    assert "D-127-B" in ARCH
    assert "four-path" in ARCH.lower()
