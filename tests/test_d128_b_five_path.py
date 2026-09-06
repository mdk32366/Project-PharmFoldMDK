"""D-128-B — UI five-path honesty + the mandatory Method addendum. These must go red.

B reads A's sibling ``linker_seam/{parent}/`` tree. It does not persist,
does not implement any part of the algorithm, does not invent a jump / a
window / an RMSD / an honesty verdict, and must not collide persist stems
with assembler ``stitched``, D-125 ``kabsch/``, D-126
``confidence_kabsch/``, or D-127 ``piecewise_kabsch/``. Default served
PDB stays assembler. A missing tree must not imply a D-128 path exists.

⚠ The distinctive D-128 hazard these pin: A's §1a rows are
**cross-path** — four trees, every seam, the jump each path *ends* with.
Collapsing them into a mean jump per path, an "N of M seams honest"
tally, or a best-path badge would hide **which** path is dishonest
**where**, which is the entire content of §1a and the D-126 lie surface
re-created one level up. B renders one row per (path, seam) and derives
no average.

⚠ The second hazard: **unknown is not honest** and **null is not 0.0**.
A verdict is recomputed from A's own jump with A's own gate rather than
copied out of a file, so a recorded ``honest: true`` above 10.0 Å is
overridden fail-closed.

⚠ Spec §7 makes the Method addendum **mandatory** — D-128 is not "done"
without it. Those checks live here too, not in a follow-up, and they
include the **D-128 OPS result as recorded** (amendment 1).
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
from app.linker_seam_path_read import (
    EMPTY_REASON_MISSING,
    EMPTY_REASON_NO_HONESTY_ROWS,
    LINKER_SEAM_PERSIST_STEM_PREFIX,
    empty_linker_seam_block,
    five_path_payload,
    project_honesty_row,
    project_linker_seam_row,
    read_linker_seam_path,
    seam_note_for_five,
)
from app.piecewise_kabsch_path_read import PIECEWISE_KABSCH_PERSIST_STEM_PREFIX
from app.reads import get_census_detail
from db.models import Base, ProteinAnalysis

ROOT = Path(__file__).resolve().parent.parent
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
INDEX = (ROOT / "docs" / "decisions.md").read_text(encoding="utf-8")
PLAN_TEST = (ROOT / "docs" / "Test_Plan.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
READS = (ROOT / "app" / "reads.py").read_text(encoding="utf-8")
READER = (ROOT / "app" / "linker_seam_path_read.py").read_text(encoding="utf-8")
D128_WRITER_PATH = ROOT / "core" / "hold48_linker_seam.py"
D128_WRITER = D128_WRITER_PATH.read_text(encoding="utf-8")
D127_WRITER_PATH = ROOT / "core" / "hold48_piecewise_kabsch.py"
D126_WRITER_PATH = ROOT / "core" / "hold48_confidence_kabsch.py"
D125_WRITER_PATH = ROOT / "core" / "hold48_kabsch.py"
STITCH = (ROOT / "core" / "hold48_stitch.py").read_text(encoding="utf-8")
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

# The five modules on main (`9e65cbf`). B reads them; B edits none of them.
D128_WRITER_SHA256 = "c270f8711040471a9080a23ab4c1e167a0cc2eedf546c3481cd9ed4f4eb19843"
D127_WRITER_SHA256 = "ad48b2be577b987466274000c508a621792bc029bb9e087eec94ba7237f13e04"
D126_WRITER_SHA256 = "d526a856ec8f1ba978a3586f3dfcf4a0ee858da12132499f2db37368efc77f18"
D125_WRITER_SHA256 = "4c7bb45d04507e2a67ba3600b35d6130d62843ca3bc99c15d3568d5cb105ff6e"

FORBIDDEN = (
    "seams solved",
    "seams fixed",
    "kabsch aligned",
    "full-length af-quality",
    "we ran kabsch",
)


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def _slice(text: str, start_marker: str, end_marker: str, label: str) -> str:
    start = text.find(start_marker)
    assert start != -1, f"{label}: missing {start_marker!r}"
    end = text.find(end_marker, start + len(start_marker))
    assert end != -1, f"{label}: missing {end_marker!r} after {start_marker!r}"
    return text[start:end]


def d128_method_sections() -> tuple[tuple[str, str], ...]:
    """The D-128-B addendum ALONE, on both surfaces.

    ⚠ Whole-page substring checks are the trap D-127-B documented and this
    suite re-learned by mutation: deleting "the default served structure is
    still the assembler" from the D-128 passage left every whole-file
    assertion green, because the D-127-B section further up says it too. A
    claim this section is required to make must be found **in this
    section**.
    """
    return (
        (
            _slice(
                METHOD_MD,
                "## Addendum D-128-B",
                "## The rental is CLOSED",
                "method-hold48-tiles.md",
            ),
            "method-hold48-tiles.md (D-128-B section)",
        ),
        (
            _slice(
                METHOD_NOTE,
                "<h3>Linker / seam honesty, and the five-step stitch-path train",
                "<h3>What it does today</h3>",
                "MethodNote.jsx",
            ),
            "MethodNote.jsx (D-128-B addendum)",
        ),
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


def _honesty_rows(
    *,
    kabsch_jump=4.2,
    confidence_jump=6.1,
    piecewise_jump=28.6,
    linker_seam_jump=7.4,
    kabsch_honest_recorded=None,
):
    """The four §1a rows as A's ``SeamHonestyRow.to_json_row`` writes them."""

    def row(path, jump, source, **extra):
        payload = {
            "path": path,
            "moving_tile_index": 2,
            "reference_tile_index": 1,
            "max_ca_jump_angstrom": jump,
            "honest": None if jump is None else jump <= 10.0,
            "linker_n": None,
            "max_linker_ca_jump": None,
            "linker_fields_applicable": path == "piecewise_kabsch",
            "source": source,
            "absence_reason": None,
            "refuse_reason": None,
            "honesty_gate_angstrom": 10.0,
        }
        payload.update(extra)
        return payload

    kabsch = row("kabsch", kabsch_jump, "measured_from_path_artifacts")
    if kabsch_honest_recorded is not None:
        kabsch["honest"] = kabsch_honest_recorded
    return [
        kabsch,
        row("confidence_kabsch", confidence_jump, "read_from_path_record"),
        row(
            "piecewise_kabsch",
            piecewise_jump,
            "read_from_path_record",
            linker_n=12,
            max_linker_ca_jump=3.05,
        ),
        row("linker_seam", linker_seam_jump, "measured_from_path_artifacts"),
    ]


def _write_linker_seam_tree(
    root: Path,
    *,
    seams=None,
    honesty=None,
    accepted=True,
    repaired=True,
    include_honesty=True,
    include_seams=True,
    write_stitched=None,
):
    """A D-128 tree as A's writer lays it down."""
    dest = root / "linker_seam" / "2817"
    dest.mkdir(parents=True, exist_ok=True)
    if seams is None:
        seams = [
            {
                "moving_tile_index": 2,
                "reference_tile_index": 1,
                "overlap_start": 1529,
                "overlap_end": 1656,
                "offending_seam_source": "from_d127_refuse",
                "no_offending_seam": False,
                "seam_centre": 1592,
                "window_start": 1560,
                "window_end": 1624,
                "window_half_width_aa": 32,
                "n_ca": 65,
                "rmsd_angstrom": 2.75,
                "max_ca_jump_angstrom": 7.4,
                "pre_transform_max_ca_jump_angstrom": 31.2,
                "refuse_reason": None,
                "honest": True,
                "R": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                "t": [0.0, 0.0, 0.0],
            }
        ]
    if honesty is None:
        honesty = _honesty_rows()
    payload = {
        "algorithm": "linker_local_kabsch_then_winning_tile",
        "decision": "D-128",
        "parent_job_id": 2817,
        "accepted": accepted,
        "repaired": repaired,
        "seams": seams,
        "seam_honesty": honesty,
        "window_half_width_aa": 32,
        "weight_epsilon": 1e-3,
        "rmsd_refuse_angstrom": 10.0,
        "seam_honesty_gate_angstrom": 10.0,
        "no_trim_loop": True,
        "no_domain_pieces_fitted": True,
        "no_linker_inherit": True,
        "served_path": "assembler",
        "seams_solved": False,
    }
    (dest / "provenance.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    if include_seams:
        (dest / "seams.jsonl").write_text(
            "".join(json.dumps(s) + "\n" for s in seams), encoding="utf-8"
        )
    if include_honesty:
        (dest / "seam_honesty.jsonl").write_text(
            "".join(json.dumps(r) + "\n" for r in honesty), encoding="utf-8"
        )
    if write_stitched is None:
        write_stitched = accepted
    if write_stitched:
        (dest / "stitched.pdb").write_text("HEADER linker-seam-path\n", encoding="utf-8")
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


def _write_piecewise_tree(root: Path):
    dest = root / "piecewise_kabsch" / "2817"
    dest.mkdir(parents=True, exist_ok=True)
    seam = {
        "moving_tile_index": 2,
        "reference_tile_index": 1,
        "overlap_start": 1529,
        "overlap_end": 1656,
        "pieces": [
            {"interval": [1540, 1600], "n_ca": 61, "rmsd_angstrom": 1.8,
             "refuse_reason": None, "R": None, "t": None},
        ],
        "linker_n": 12,
        "max_linker_ca_jump": 3.05,
        "rmsd_full_overlap_angstrom": 9.4,
        "max_ca_jump_angstrom": 28.6,
        "refuse_reason": None,
    }
    payload = {
        "algorithm": "piecewise_domain_kabsch_then_winning_tile",
        "decision": "D-127",
        "parent_job_id": 2817,
        "accepted": True,
        "seams": [seam],
        "rmsd_refuse_angstrom": 10.0,
    }
    (dest / "provenance.json").write_text(json.dumps(payload) + "\n", encoding="utf-8")
    (dest / "seams.jsonl").write_text(json.dumps(seam) + "\n", encoding="utf-8")
    return dest


def _all_four_prior(root: Path):
    _write_kabsch_tree(root)
    _write_confidence_tree(root)
    _write_piecewise_tree(root)


# ── T-1161 · living log ───────────────────────────────────────────────────


def test_d128_b_heading_exists_in_the_living_log():
    """D-001 naming: the check is the heading, not a citation of one."""
    assert re.search(r"^### D-128-B — UI linker / seam path honesty", LOG, re.M)
    assert re.search(r"^### D-128-A — Linker / seam honesty core", LOG, re.M)
    assert re.search(r"^### D-128 — Linker / seam honesty Spec", LOG, re.M)
    assert "9e65cbf" in LOG


def test_emma_bar_cites_d128a_and_spec_sections_six_and_seven():
    """Emma GO bound: cite Spec §6 + §7; served path is assembler; B reads."""
    start = LOG.find("### D-128-B — UI linker / seam path honesty")
    end = LOG.find("### D-128-A —", start + 1)
    section = LOG[start:end] if start != -1 and end != -1 else ""
    assert section, "D-128-B heading must exist so the bar can be pinned"
    flat = _flat(section)
    lowered = flat.lower()
    assert "§6" in section
    assert "§7" in section
    assert "linker_seam" in section
    assert "9e65cbf" in section
    assert "seam_honesty.jsonl" in section
    assert "max_ca_jump_angstrom" in section
    assert "mandatory" in lowered
    assert "served stays the assembler" in lowered or "default served" in lowered
    assert "never solved" in lowered or "never claim seams solved" in lowered
    # The distinctive hazard is named, not merely implied.
    assert "average" in lowered
    assert "unknown is not honest" in lowered or "unknown is never honest" in lowered
    # Trinity's LOCKED bar is bound in the log, not merely referenced, and
    # the audit that found two unpinned clauses is recorded with it.
    assert "LOCKED" in section
    assert "clause by clause" in lowered
    assert "no test that could go red" in lowered or "could go red" in lowered
    for clause in ("3432", "10 Å", "auto-flip", "Trinity merges"):
        assert clause in section, clause
    # Ship index carries the same bar.
    assert "9e65cbf" in INDEX
    assert "five-path" in INDEX.lower() or "five paths" in INDEX.lower()
    assert "§7" in INDEX


# ── T-1162 · honest empty ─────────────────────────────────────────────────


def test_missing_linker_seam_tree_does_not_imply_d128_path_or_invent_metrics(tmp_path):
    block = read_linker_seam_path(tmp_path, parent_analysis_id=2817, parent_job_id=2817)
    assert block["present"] is False
    assert block["empty_reason"] == EMPTY_REASON_MISSING
    assert block["seams"] == []
    assert block["seam_honesty"] == []
    assert block["seam_honesty_empty_reason"] == EMPTY_REASON_NO_HONESTY_ROWS
    assert block["persist_stem"] == "linker_seam/2817"
    assert block["success_pdb_on_disk"] is False
    # An absent tree is not "no dishonest seams".
    assert block["has_dishonest_or_unknown_seam"] is None
    assert block["accepted"] is None
    assert block["repaired"] is None
    dumped = json.dumps(block["seams"]) + json.dumps(block["seam_honesty"])
    for token in ("jump", "rmsd", "window", "honest"):
        assert token not in dumped
    assert "not a solved seam" in block["empty_note"]
    note = seam_note_for_five({"present": False}, {"present": False}, {"present": False}, block)
    assert "88.76" in note
    assert "fifth path" not in note.lower()
    assert "linker" not in note.lower()
    for phrase in FORBIDDEN:
        assert phrase not in note.lower()


def test_seam_note_names_the_fifth_path_only_when_the_tree_is_on_disk(tmp_path):
    _all_four_prior(tmp_path)
    four_only = five_path_payload(tmp_path, parent_analysis_id=2817, parent_job_id=2817)
    note4 = seam_note_for_five(
        four_only["kabsch"],
        four_only["confidence_kabsch"],
        four_only["piecewise_kabsch"],
        four_only["linker_seam"],
    )
    assert "fourth path" in note4.lower()
    assert "fifth path" not in note4.lower()

    _write_linker_seam_tree(tmp_path)
    full = five_path_payload(tmp_path, parent_analysis_id=2817, parent_job_id=2817)
    note5 = seam_note_for_five(
        full["kabsch"],
        full["confidence_kabsch"],
        full["piecewise_kabsch"],
        full["linker_seam"],
    )
    assert "fifth path" in note5.lower()
    assert "per path and per seam" in note5
    assert "measurements" in note5
    assert "default served structure" in note5
    for phrase in FORBIDDEN:
        assert phrase not in note5.lower()


# ── T-1163 · five stems, no collision ─────────────────────────────────────


def test_present_tree_names_five_paths_and_stems_do_not_collide(tmp_path):
    _all_four_prior(tmp_path)
    _write_linker_seam_tree(tmp_path)
    payload = five_path_payload(tmp_path, parent_analysis_id=2817, parent_job_id=2817)
    asm = payload["assembler"]
    d128 = payload["linker_seam"]
    assert asm["persist_stem"] == ASSEMBLER_PERSIST_STEM == "stitched"
    assert asm["default_served"] is True
    assert d128["present"] is True
    assert d128["persist_stem"] == "linker_seam/2817"
    assert d128["persist_stem"].startswith(LINKER_SEAM_PERSIST_STEM_PREFIX)
    assert d128["default_served"] is False
    stems = {
        asm["persist_stem"],
        payload["kabsch"]["persist_stem"],
        payload["confidence_kabsch"]["persist_stem"],
        payload["piecewise_kabsch"]["persist_stem"],
        d128["persist_stem"],
    }
    assert len(stems) == 5
    for prefix in (
        KABSCH_PERSIST_STEM_PREFIX,
        CONFIDENCE_KABSCH_PERSIST_STEM_PREFIX,
        PIECEWISE_KABSCH_PERSIST_STEM_PREFIX,
    ):
        assert not d128["persist_stem"].startswith(f"{prefix}/")
    assert "not scientifically solved" in d128["label"]
    assert d128["algorithm"] == "linker_local_kabsch_then_winning_tile"
    assert d128["decision"] == "D-128"
    assert d128["seams_solved"] is False


def test_empty_block_stem_never_equals_an_earlier_path():
    empty = empty_linker_seam_block(parent_id=2817)
    assert empty["persist_stem"] == "linker_seam/2817"
    assert empty["persist_stem"] != ASSEMBLER_PERSIST_STEM
    for prefix in ("kabsch/", "confidence_kabsch/", "piecewise_kabsch/"):
        assert not empty["persist_stem"].startswith(prefix)


# ── T-1164 · one row per (path, seam), never an average ───────────────────


def test_seam_honesty_rows_render_per_path_and_are_never_averaged(tmp_path):
    _write_linker_seam_tree(tmp_path)
    block = read_linker_seam_path(tmp_path, parent_analysis_id=2817)
    rows = block["seam_honesty"]
    assert [r["path"] for r in rows] == [
        "kabsch",
        "confidence_kabsch",
        "piecewise_kabsch",
        "linker_seam",
    ]
    assert [r["max_ca_jump_angstrom"] for r in rows] == [4.2, 6.1, 28.6, 7.4]
    assert [r["honest"] for r in rows] == [True, True, False, True]
    # ⚠ No collapsed number anywhere: mean(4.2, 6.1, 28.6, 7.4) = 11.575 and
    # the max is 28.6. Either standing as a block-level field, or an
    # "N of M honest" tally, would be the D-126 lie surface one level up.
    dumped = json.dumps(block)
    assert "11.57" not in dumped
    for banned in (
        "mean_ca_jump",
        "mean_max_ca_jump_angstrom",
        "average_jump",
        "n_honest",
        "n_dishonest",
        "n_seams_honest",
        "honest_fraction",
        "honesty_score",
        "best_path",
        "worst_path",
    ):
        assert banned not in dumped, banned
        assert banned not in READER, banned
    # And the reader must not be able to compute one. (``sorted`` is
    # allowed on filenames; what is banned is arithmetic over the rows.)
    for arithmetic in ("mean(", "statistics", "sum(", "/ len(", "max(", "min("):
        assert arithmetic not in READER, arithmetic


def test_only_the_path_that_defines_linkers_shows_linker_fields(tmp_path):
    """A's PATHS_DEFINING_LINKERS is D-127 only. Elsewhere: absent, not 0."""
    _write_linker_seam_tree(tmp_path)
    rows = read_linker_seam_path(tmp_path, parent_analysis_id=2817)["seam_honesty"]
    by_path = {r["path"]: r for r in rows}
    d127 = by_path["piecewise_kabsch"]
    assert d127["linker_fields_applicable"] is True
    assert d127["linker_n"] == 12
    assert d127["max_linker_ca_jump"] == 3.05
    for path in ("kabsch", "confidence_kabsch", "linker_seam"):
        row = by_path[path]
        assert row["linker_fields_applicable"] is False, path
        assert row["linker_n"] is None, path
        assert row["max_linker_ca_jump"] is None, path
        # Absent, never zero.
        assert row["linker_n"] != 0, path
        assert row["max_linker_ca_jump"] != 0, path


def test_a_path_that_does_not_define_linkers_cannot_smuggle_them_in():
    """The applicability rule keys off the path name, not a file's boolean."""
    row = project_honesty_row(
        {
            "path": "kabsch",
            "max_ca_jump_angstrom": 3.0,
            "honest": True,
            "linker_fields_applicable": True,
            "linker_n": 9,
            "max_linker_ca_jump": 2.2,
        }
    )
    assert row["linker_fields_applicable"] is False
    assert row["linker_n"] is None
    assert row["max_linker_ca_jump"] is None


def test_null_jump_is_an_absence_with_a_reason_never_zero_and_never_honest(tmp_path):
    """Spec §1a: null is not 0.0 and unknown is not honest."""
    _write_linker_seam_tree(
        tmp_path,
        honesty=[
            {
                "path": "kabsch",
                "moving_tile_index": None,
                "reference_tile_index": None,
                "max_ca_jump_angstrom": None,
                "honest": None,
                "linker_n": None,
                "max_linker_ca_jump": None,
                "linker_fields_applicable": False,
                "source": "absent",
                "absence_reason": "tree_absent",
                "refuse_reason": None,
                "honesty_gate_angstrom": 10.0,
            },
            {
                "path": "confidence_kabsch",
                "moving_tile_index": 2,
                "reference_tile_index": 1,
                "max_ca_jump_angstrom": None,
                "honest": None,
                "linker_n": None,
                "max_linker_ca_jump": None,
                "linker_fields_applicable": False,
                "source": "absent",
                "absence_reason": "refused_before_transform",
                "refuse_reason": "rmsd_gt_10",
                "honesty_gate_angstrom": 10.0,
            },
        ],
    )
    rows = read_linker_seam_path(tmp_path, parent_analysis_id=2817)["seam_honesty"]
    for row in rows:
        assert row["max_ca_jump_angstrom"] is None
        assert row["max_ca_jump_angstrom"] != 0
        assert row["honest"] is None
        assert row["honest"] is not False  # unknown, not "measured dishonest"
        assert row["honest"] is not True  # and certainly not honest
        assert row["source"] == "absent"
        assert row["absence_reason"] in ("tree_absent", "refused_before_transform")
    assert rows[1]["refuse_reason"] == "rmsd_gt_10"


def test_recorded_honest_above_the_gate_is_overridden_fail_closed(tmp_path):
    """A boolean in a file may not outrank the 10.0 Å gate on the jump beside it."""
    _write_linker_seam_tree(
        tmp_path,
        honesty=_honesty_rows(kabsch_jump=42.0, kabsch_honest_recorded=True),
    )
    row = read_linker_seam_path(tmp_path, parent_analysis_id=2817)["seam_honesty"][0]
    assert row["path"] == "kabsch"
    assert row["max_ca_jump_angstrom"] == 42.0
    assert row["honest"] is False
    assert row["honest_recorded"] is True
    assert row["honest_disagrees_with_record"] is True


def test_honesty_verdict_is_the_existing_ten_angstrom_gate_exactly():
    """B reports the gate; B does not carry one. 10.0 is honest, 10.0000001 is not."""
    assert project_honesty_row({"path": "kabsch", "max_ca_jump_angstrom": 10.0})["honest"] is True
    assert (
        project_honesty_row({"path": "kabsch", "max_ca_jump_angstrom": 10.0000001})["honest"]
        is False
    )
    assert project_honesty_row({"path": "kabsch"})["honest"] is None
    # B must not declare or apply a threshold of its own — it imports A's
    # constant and A's comparison. Prose may name 10.0 Å; code may not.
    assert "RMSD_REFUSE_ANGSTROM = " not in READER
    assert "SEAM_HONESTY_GATE_ANGSTROM = " not in READER
    for comparison in ("> 10.0", ">= 10.0", "< 10.0", "<= 10.0", "10.0)", "10.0:"):
        assert comparison not in READER, comparison
    assert "from core.hold48_linker_seam import" in READER
    assert "honest_for_jump" in READER


# ── T-1165 · the D-128 window fit ─────────────────────────────────────────


def test_window_fit_row_renders_from_as_json(tmp_path):
    _write_linker_seam_tree(tmp_path)
    seam = read_linker_seam_path(tmp_path, parent_analysis_id=2817)["seams"][0]
    assert seam["window_start"] == 1560
    assert seam["window_end"] == 1624
    assert seam["window_half_width_aa"] == 32
    assert seam["seam_centre"] == 1592
    assert seam["n_ca"] == 65
    assert seam["rmsd_angstrom"] == 2.75
    assert seam["pre_transform_max_ca_jump_angstrom"] == 31.2
    assert seam["max_ca_jump_angstrom"] == 7.4
    assert seam["honest"] is True
    assert seam["offending_seam_source"] == "from_d127_refuse"
    assert seam["no_offending_seam"] is False
    assert seam["refuse_reason"] is None
    assert seam["accepted"] is True
    # The before/after pair must both survive: the "after" alone cannot show
    # whether the move did anything.
    assert seam["pre_transform_max_ca_jump_angstrom"] > seam["max_ca_jump_angstrom"]


def test_window_fit_row_stays_null_on_refuse_before_transform(tmp_path):
    _write_linker_seam_tree(
        tmp_path,
        accepted=False,
        repaired=False,
        seams=[
            {
                "moving_tile_index": 2,
                "reference_tile_index": 1,
                "overlap_start": 1529,
                "overlap_end": 1656,
                "offending_seam_source": "from_measured_jump",
                "no_offending_seam": False,
                "seam_centre": 1592,
                "window_start": 1560,
                "window_end": 1624,
                "window_half_width_aa": 32,
                "n_ca": 2,
                "rmsd_angstrom": None,
                "max_ca_jump_angstrom": None,
                "pre_transform_max_ca_jump_angstrom": 31.2,
                "refuse_reason": "overlap_ca_lt_3",
                "honest": None,
                "R": None,
                "t": None,
            }
        ],
    )
    seam = read_linker_seam_path(tmp_path, parent_analysis_id=2817)["seams"][0]
    assert seam["rmsd_angstrom"] is None
    assert seam["max_ca_jump_angstrom"] is None
    assert seam["honest"] is None
    assert seam["refuse_reason"] == "overlap_ca_lt_3"
    assert seam["accepted"] is False
    for key in ("rmsd_angstrom", "max_ca_jump_angstrom"):
        assert seam[key] != 0
        assert seam[key] is not False


def test_a_seam_that_offended_nothing_is_a_recorded_absence():
    row = project_linker_seam_row(
        {
            "moving_tile_index": 2,
            "reference_tile_index": 1,
            "offending_seam_source": None,
            "max_ca_jump_angstrom": 3.1,
            "refuse_reason": None,
        }
    )
    assert row["no_offending_seam"] is True
    assert row["offending_seam_source"] is None
    assert row["window_start"] is None
    assert row["window_end"] is None
    assert row["n_ca"] is None
    assert row["honest"] is True


def test_projection_drops_the_rigid_transform_itself():
    """R / t are A's record, not a card measurement mistakable for a pose."""
    row = project_linker_seam_row(
        {"R": [[1, 0, 0], [0, 1, 0], [0, 0, 1]], "t": [3.0, 4.0, 5.0]}
    )
    assert "R" not in row
    assert "t" not in row


# ── T-1166 · fail-closed ──────────────────────────────────────────────────


def test_dishonest_d128_seam_never_carries_a_success_pdb(tmp_path):
    """Spec §1a: no success PDB is presented as honest for a dishonest seam."""
    dest = _write_linker_seam_tree(
        tmp_path,
        accepted=False,
        repaired=False,
        seams=[
            {
                "moving_tile_index": 2,
                "reference_tile_index": 1,
                "overlap_start": 1529,
                "overlap_end": 1656,
                "offending_seam_source": "from_d127_refuse",
                "no_offending_seam": False,
                "seam_centre": 1592,
                "window_start": 1560,
                "window_end": 1624,
                "window_half_width_aa": 32,
                "n_ca": 65,
                "rmsd_angstrom": 3.4,
                "max_ca_jump_angstrom": 26.9,
                "pre_transform_max_ca_jump_angstrom": 31.2,
                "refuse_reason": "seam_jump_gt_10",
                "honest": False,
                "R": None,
                "t": None,
            }
        ],
        write_stitched=True,
    )
    assert (dest / "stitched.pdb").is_file()
    block = read_linker_seam_path(tmp_path, parent_analysis_id=2817)
    assert block["present"] is True
    assert block["accepted"] is False
    assert block["has_dishonest_or_unknown_seam"] is True
    assert block["success_pdb_on_disk"] is False
    assert block["seams"][0]["honest"] is False
    assert block["seams"][0]["refuse_reason"] == "seam_jump_gt_10"
    dumped = json.dumps(block).lower()
    assert "fixed" not in dumped
    assert "repaired_badge" not in dumped
    for phrase in FORBIDDEN:
        assert phrase not in dumped


def test_an_unknown_seam_also_withholds_the_success_pdb(tmp_path):
    """Unknown is not honest, so it cannot carry a success either."""
    _write_linker_seam_tree(
        tmp_path,
        accepted=True,
        seams=[
            {
                "moving_tile_index": 2,
                "reference_tile_index": 1,
                "max_ca_jump_angstrom": None,
                "refuse_reason": None,
                "honest": None,
            }
        ],
        write_stitched=True,
    )
    block = read_linker_seam_path(tmp_path, parent_analysis_id=2817)
    assert block["accepted"] is True
    assert block["seams"][0]["honest"] is None
    assert block["has_dishonest_or_unknown_seam"] is True
    assert block["success_pdb_on_disk"] is False


def test_an_all_honest_accepted_parent_may_name_its_own_pdb(tmp_path):
    """Fail-closed is not fail-always: the honest accept still reads as one."""
    _write_linker_seam_tree(tmp_path)
    block = read_linker_seam_path(tmp_path, parent_analysis_id=2817)
    assert block["accepted"] is True
    assert block["has_dishonest_or_unknown_seam"] is False
    assert block["success_pdb_on_disk"] is True
    assert block["repaired"] is True
    # ...and it is still not the served path.
    assert block["default_served"] is False


def test_a_d128_success_requires_d128s_own_pdb_on_disk(tmp_path):
    """Trinity bar 6: no prior path's `stitched.pdb` may stand in for D-128's.

    ⚠ Found by auditing the bar clause by clause: dropping the
    ``"stitched.pdb" in files`` condition left every other test green, so
    an accepted all-honest parent with **no D-128 file** would have been
    announced as carrying one — which is the door the clause closes. The
    assembler's own `stitched.pdb` sits one directory up.
    """
    _write_linker_seam_tree(tmp_path, write_stitched=False)
    dest = tmp_path / "linker_seam" / "2817"
    assert not (dest / "stitched.pdb").exists()
    # The assembler tree does have one; it must not be borrowed.
    (tmp_path / "2817").mkdir(parents=True, exist_ok=True)
    (tmp_path / "2817" / "stitched.pdb").write_text("HEADER assembler\n", encoding="utf-8")
    block = read_linker_seam_path(tmp_path, parent_analysis_id=2817)
    assert block["accepted"] is True
    assert block["has_dishonest_or_unknown_seam"] is False
    assert block["success_pdb_on_disk"] is False
    assert "stitched.pdb" not in block["files_on_disk"]


def test_gate_and_window_are_reported_not_redeclared(tmp_path):
    _write_linker_seam_tree(tmp_path)
    block = read_linker_seam_path(tmp_path, parent_analysis_id=2817)
    assert block["rmsd_refuse_angstrom"] == 10.0
    assert block["honesty_gate_angstrom"] == 10.0
    assert block["window_half_width_aa"] == 32
    empty = empty_linker_seam_block(parent_id=2817)
    assert empty["honesty_gate_angstrom"] == 10.0
    assert empty["window_half_width_aa"] == 32
    # The live constants A fits against are untouched at their values.
    from core.hold48_linker_seam import (
        SEAM_HONESTY_GATE_ANGSTROM,
        WINDOW_HALF_WIDTH_AA,
    )
    from core.hold48_confidence_kabsch import WEIGHT_EPSILON

    assert SEAM_HONESTY_GATE_ANGSTROM == 10.0
    assert WINDOW_HALF_WIDTH_AA == 32
    assert WEIGHT_EPSILON == 1e-3


def test_a_tree_without_honesty_rows_is_an_absence_not_zero_dishonest(tmp_path):
    _write_linker_seam_tree(tmp_path, include_honesty=False)
    block = read_linker_seam_path(tmp_path, parent_analysis_id=2817)
    assert block["present"] is True
    # provenance.json still carries them, so the fallback finds them; drop
    # those too and the absence must be stated rather than counted as zero.
    dest = tmp_path / "linker_seam" / "2817"
    prov = json.loads((dest / "provenance.json").read_text(encoding="utf-8"))
    prov["seam_honesty"] = []
    (dest / "provenance.json").write_text(json.dumps(prov), encoding="utf-8")
    block = read_linker_seam_path(tmp_path, parent_analysis_id=2817)
    assert block["seam_honesty"] == []
    assert block["seam_honesty_empty_reason"] == EMPTY_REASON_NO_HONESTY_ROWS


# ── T-1167 · assembly_review wiring ───────────────────────────────────────


def test_assembly_review_carries_five_path_empty_and_does_not_imply_d128(tmp_path):
    eng = _engine()
    assembler_dir = tmp_path / "assembler" / "2817"
    with Session(eng) as s:
        _add_parent(s, assembler_dir)
        s.commit()
    review = get_census_detail(eng, 2817, artifact_root=tmp_path / "empty-ops")[
        "assembly_review"
    ]
    assert review["five_path"]["linker_seam"]["present"] is False
    assert review["five_path"]["assembler"]["default_served"] is True
    # D-125-B / D-126-B / D-127-B views survive unchanged (anti-gut).
    assert review["dual_path"]["kabsch"]["present"] is False
    assert review["triple_path"]["confidence_kabsch"]["present"] is False
    assert review["four_path"]["piecewise_kabsch"]["present"] is False
    assert review["four_path"]["assembler"]["default_served"] is True
    assert "linker_seam" not in review["four_path"]
    names = [d["name"] for d in review["downloads"]["stitched"]]
    assert names == ["stitched.pdb", "stitched_plddt.json", "stitched_pae.json"]
    assert all(not n.startswith("linker_seam") for n in names)
    assert "fifth path" not in review["seam_note"].lower()


def test_assembly_review_reads_fifth_sibling_tree_beside_assembler_dir(tmp_path):
    """A's tree is {root}/linker_seam/{parent}/ — not assembler {root}/{parent}/."""
    eng = _engine()
    ops = tmp_path / "ops"
    with Session(eng) as s:
        _add_parent(s, ops / "2817")
        s.commit()
    _all_four_prior(ops)
    _write_linker_seam_tree(ops)
    review = get_census_detail(eng, 2817, artifact_root=ops)["assembly_review"]
    d128 = review["five_path"]["linker_seam"]
    assert d128["present"] is True
    assert d128["persist_stem"] == "linker_seam/2817"
    assert [r["path"] for r in d128["seam_honesty"]] == [
        "kabsch",
        "confidence_kabsch",
        "piecewise_kabsch",
        "linker_seam",
    ]
    assert d128["seams"][0]["window_half_width_aa"] == 32
    assert "fifth path" in review["seam_note"].lower()
    # Default served PDB is still the assembler one, under the assembler stem.
    assert review["five_path"]["assembler"]["default_served"] is True
    names = [d["name"] for d in review["downloads"]["stitched"]]
    assert "stitched.pdb" in names
    assert "linker_seam_stitched.pdb" not in names
    # The four earlier paths are untouched and still readable.
    assert review["four_path"]["piecewise_kabsch"]["present"] is True
    assert review["triple_path"]["confidence_kabsch"]["present"] is True
    assert review["dual_path"]["kabsch"]["present"] is True


# ── T-1168 · B does not write, does not restitch, does not edit A ─────────


def test_b_does_not_reimplement_persist_writer():
    assert "def write_linker_seam_restitch" not in READER
    assert "def write_provenance" not in READER
    assert "def write_piecewise_kabsch_restitch" not in READER
    assert "def write_confidence_kabsch_restitch" not in READER
    assert "def write_kabsch_restitch" not in READER
    assert "write_linker_seam_restitch" in D128_WRITER
    assert "five_path_payload" in READS


def test_b_implements_no_part_of_the_algorithm():
    """Emma pin: A already shipped the core. B reads it."""
    for symbol in (
        "def fit_seam_window",
        "def align_tiles",
        "def apply_window_transform_pdb",
        "def transform_tile_window",
        "def seam_max_ca_jump",
        "def collect_seam_honesty",
        "def build_ops_success_report",
        "weighted_kabsch_rotation_translation",
        "winning_tile",
        "write_stitched",
    ):
        assert symbol not in READER, symbol
    # A still owns every one of them.
    for symbol in (
        "def fit_seam_window",
        "def align_tiles",
        "def collect_seam_honesty",
        "def build_ops_success_report",
    ):
        assert symbol in D128_WRITER, symbol


def test_b_does_not_invoke_a_restitch_or_an_ops_run():
    """UI + Method only. No writer call, no CLI, no Fly."""
    routes = (ROOT / "app" / "read_routes.py").read_text(encoding="utf-8")
    for text, label in (
        (READER, "linker_seam_path_read"),
        (READS, "reads"),
        (routes, "read_routes"),
        (REVIEW_JSX, "AssemblyReview"),
        (METHOD_NOTE, "MethodNote"),
        (PROV_JSX, "Provenance"),
    ):
        assert "write_linker_seam_restitch(" not in text, label
        assert "write_piecewise_kabsch_restitch(" not in text, label
        assert "write_confidence_kabsch_restitch(" not in text, label
        assert "write_kabsch_restitch(" not in text, label
        assert "scripts.linker_seam_restitch" not in text, label
        lowered = text.lower()
        assert "requests.post" not in lowered, label
        assert "fly.io" not in lowered, label
        for phrase in FORBIDDEN:
            assert phrase not in lowered, f"{label}: {phrase}"


def test_no_d128_surface_rents_a_gpu_or_ingests_into_f004():
    """Trinity bar 7: no rent / F-004 from the surface this PR adds.

    ⚠ Word boundaries matter here: a bare "rent" substring matches every
    ``parent`` on the page, so the naive form of this guard would be
    green for a reason that has nothing to do with renting anything.
    """
    surfaces = [(READER, "linker_seam_path_read")]
    surfaces.extend(
        (text, label) for text, label in d128_method_sections()
    )
    surfaces.append(
        (
            _slice(
                REVIEW_JSX,
                'data-testid="d128-seam-honesty"',
                "function PaeBadge",
                "AssemblyReview.jsx",
            ),
            "AssemblyReview.jsx (D-128 blocks)",
        )
    )
    for text, label in surfaces:
        lowered = text.lower()
        assert not re.search(r"\brent\b|\brented\b|\brenting\b", lowered), label
        assert not re.search(r"\brunpod\b|\btorch\b|\bcuda\b", lowered), label
        assert "core.scorer" not in lowered, label
        assert "ingest" not in lowered, label


def test_algorithm_modules_are_not_edited_by_this_ui_pr():
    """Hard stop: B reads. All five paths' bytes stay as they landed on main."""
    for path, digest, label in (
        (D128_WRITER_PATH, D128_WRITER_SHA256, "hold48_linker_seam.py"),
        (D127_WRITER_PATH, D127_WRITER_SHA256, "hold48_piecewise_kabsch.py"),
        (D126_WRITER_PATH, D126_WRITER_SHA256, "hold48_confidence_kabsch.py"),
        (D125_WRITER_PATH, D125_WRITER_SHA256, "hold48_kabsch.py"),
    ):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, label
    assert "def winning_tile" in STITCH
    assert "D-128" not in STITCH
    assert "linker_seam" not in STITCH


def test_the_ui_pr_writes_nothing_to_any_path_tree(tmp_path):
    """Reading A's tree must not touch it, and must not touch the four before it."""
    _all_four_prior(tmp_path)
    _write_linker_seam_tree(tmp_path)

    def digest() -> dict[str, str]:
        out = {}
        for p in sorted(tmp_path.rglob("*")):
            if p.is_file():
                out[str(p.relative_to(tmp_path))] = hashlib.sha256(
                    p.read_bytes()
                ).hexdigest()
        return out

    before = digest()
    payload = five_path_payload(tmp_path, parent_analysis_id=2817, parent_job_id=2817)
    assert payload["linker_seam"]["present"] is True
    assert digest() == before


# ── T-1169 · the mandatory Method addendum (Spec §7) ──────────────────────


def test_d128_b_method_addendum_names_the_five_step_stitch_path_train():
    """Spec §7 is mandatory: the train, in order, on both surfaces."""
    for text, label in d128_method_sections():
        flat = _flat(text)
        lowered = flat.lower()
        assert "stitch-path train" in lowered, label
        assert "five" in lowered, label
        assert "D-125 Kabsch" in flat, label
        assert "D-126 confidence" in flat, label
        assert "D-127 piecewise" in flat, label
        assert "D-128 linker / seam honesty" in flat, label
        # D-128's own shape: measure first, optional small window second.
        assert "±32 aa" in flat, label
        assert "7 of 10" in flat, label
        assert "linker" in lowered, label


def test_d128_b_method_addendum_defines_dishonest_about_the_file():
    """"Dishonest" is a claim about a structure file, not about a person."""
    for text, label in d128_method_sections():
        flat = _flat(text)
        lowered = flat.lower()
        assert "dishonest" in lowered, label
        assert "structure file" in lowered, label
        assert "not about a person" in lowered, label
        assert "10.0 Å" in flat, label


# The only Å figures the D-128 addendum may carry: the gate (**10.0**),
# the null-rendering example (**0.00**), and the upper end of D-126's
# recorded 28–68 Å lesson. ⚠ A bare "10.0 Å" assertion does NOT pin the
# gate — mutation showed the refuse table could be moved to 12.0 Å while
# other sentences kept saying 10.0. Pinning the whole set is what goes red.
ANGSTROM_FIGURES_ALLOWED = {"10.0", "0.00", "68"}


def test_d128_b_method_addendum_names_the_refuse_table_and_keeps_the_gate():
    for text, label in d128_method_sections():
        flat = _flat(text)
        lowered = flat.lower()
        assert "fewer than three" in lowered, label
        assert "in a line" in lowered, label
        assert "10.0 Å" in flat, label
        assert "a refuse writes a record" in lowered, label
        assert "no threshold moved" in lowered, label
        assert "trim loop" in lowered, label
        assert "blend" in lowered, label
        # ⚠ No second threshold may appear anywhere in this section, in
        # either direction. A loosened refuse table is the failure Spec §9
        # names first, and it does not announce itself.
        figures = set(re.findall(r"(\d+(?:\.\d+)?)\s*Å", flat))
        assert figures <= ANGSTROM_FIGURES_ALLOWED, f"{label}: {figures}"
        assert "10.0" in figures, label


def test_d128_b_method_names_seam_disclosure_as_measurement_and_refuses_an_average():
    for text, label in d128_method_sections():
        flat = _flat(text)
        lowered = flat.lower()
        assert "measurements" in lowered, label
        assert "not a verdict" in lowered, label
        assert "one row per path per seam" in lowered, label
        assert "never an average" in lowered, label
        assert "unknown jump is not honest" in lowered, label
        assert "0.00" in flat, label
        assert "linker_seam" in lowered, label
        assert "does not invent" in lowered, label
        assert "not medical advice" in lowered, label
        assert "not scientifically solved" in lowered, label
        for phrase in FORBIDDEN:
            assert phrase not in lowered, f"{label}: {phrase}"
        # Trinity bar 3 names "aligned" and "superimposed" outright. The
        # D-128 section says "lined up" in its negation and never needs
        # either word, so ban them here rather than page-wide (D-118's
        # assembler note legitimately says "not superimposed").
        for parked in ("aligned", "superimposed", "full-length af-quality"):
            assert parked not in lowered, f"{label}: {parked}"


def test_method_addendum_does_not_gut_the_four_earlier_sections():
    """Additive. The earlier sections are the reader's context, not debris."""
    for text, label in ((METHOD_MD, "method-hold48-tiles.md"), (METHOD_NOTE, "MethodNote.jsx")):
        flat = _flat(text)
        assert "winner-tile assembler" in flat, label
        assert "not Kabsch" in flat, label
        assert "88.76" in flat, label
        assert "What Kabsch does" in flat, label
        assert "What overlap-confidence Kabsch does" in flat, label
        assert "per UniProt domain" in flat, label
        assert "CLOSED" in text, label
    # ⚠ Section anchors, not just phrases. Found by auditing the Trinity
    # bar: renaming the D-121 assembler heading left every phrase check
    # green, because "winner-tile assembler" and "not Kabsch" also appear
    # in the D-125-B addendum below it. A gutted section has to be missing
    # its own heading to be noticed.
    for heading in (
        "## The problem — a long protein does not fit in one gulp",
        "## The overlap is the glue",
        "## Assemble means pick a winner — not Kabsch",
        "## Seams can look ugly",
        "## Addendum D-125-B",
        "## Addendum D-126-B",
        "## Addendum D-127-B",
        "## Addendum D-128-B",
        "## The rental is CLOSED",
    ):
        assert heading in METHOD_MD, heading
    for heading in (
        "<h3>Kabsch-path restitch",
        "<h3>Overlap-confidence Kabsch",
        "<h3>Piecewise / domain-aware Kabsch",
        "<h3>Linker / seam honesty",
        "<h3>Long proteins: tiles, glue, and a winner-tile assembler (D-121)</h3>",
    ):
        assert heading in METHOD_NOTE, heading
    for testid in (
        "hold48-explainer",
        "kabsch-method-addendum",
        "confidence-kabsch-method-addendum",
        "piecewise-kabsch-method-addendum",
        "linker-seam-method-addendum",
    ):
        assert f'data-testid="{testid}"' in METHOD_NOTE, testid
    assert "#229" in METHOD_MD


def test_method_obligation_is_recorded_as_discharged_by_this_pr():
    """Spec §7: D-128 is not 'done' without Method. The log/index must say B did it."""
    log_flat = _flat(LOG).lower()
    index_flat = _flat(INDEX).lower()
    assert "mandatory" in log_flat
    assert "d-128-b" in index_flat
    assert "method" in index_flat
    assert "discharge" in index_flat


# ── T-1170 · the D-128 OPS result, disclosed as recorded ─────────────────
#
# MANDATORY Method §7 OPS honesty inject (Matt GO via Emma, 2026-09-06).
# These figures are NOT measured by this PR — they are recorded as handed
# over, with that attribution. What these tests pin is that the surface
# states them, states the give-back beside the allowed zero, and does not
# soften either.

OPS_TIP = "9e65cbf"
OPS_OUT_ROOT = "linker_seam_ops_2026-09-05"
OPS_REFUSE_HISTOGRAM = {
    "seam_jump_gt_10": (6, (2938, 3179, 3190, 3321, 3368, 3566)),
    "rmsd_gt_10": (1, (2939,)),
}
OPS_CONFUSION = {
    "n_d125_pass_d128_refuse": 5,
    "n_d126_pass_d128_refuse": 6,
    "n_d127_pass_d128_refuse": 0,
    "n_d127_refuse_d128_pass": 0,
}
SEVEN_LINKER_PARENT_IDS = (2938, 2939, 3179, 3190, 3321, 3368, 3566)


def test_ops_figures_are_internally_consistent_before_they_are_quoted():
    """A consistency check is not a measurement — but an inconsistent
    figure must not reach a surface that calls itself honest."""
    assert 0 + 7 + 0 + 0 == len(SEVEN_LINKER_PARENT_IDS)
    assert sum(n for n, _ in OPS_REFUSE_HISTOGRAM.values()) == 7
    covered: set[int] = set()
    for reason, (n, ids) in OPS_REFUSE_HISTOGRAM.items():
        assert len(ids) == n, reason
        assert len(set(ids)) == n, reason
        assert covered.isdisjoint(ids), reason  # no parent in two buckets
        covered |= set(ids)
    assert covered == set(SEVEN_LINKER_PARENT_IDS)
    # PASS 0 is what makes recovered_of_seven = repaired_of_seven = 0.
    assert OPS_CONFUSION["n_d127_pass_d128_refuse"] == 0
    assert OPS_CONFUSION["n_d127_refuse_d128_pass"] == 0
    # A give-back cannot exceed the inventory it is measured over.
    for key in ("n_d125_pass_d128_refuse", "n_d126_pass_d128_refuse"):
        assert 0 <= OPS_CONFUSION[key] <= len(SEVEN_LINKER_PARENT_IDS), key


def test_method_discloses_the_d128_ops_run_as_recorded():
    for text, label in d128_method_sections():
        flat = _flat(text)
        lowered = flat.lower()
        assert "PASS 0" in flat, label
        assert "REFUSE 7" in flat, label
        assert "FAIL 0" in flat, label
        assert "SKIP 0" in flat, label
        assert OPS_TIP in flat, label
        assert OPS_OUT_ROOT in flat, label
        assert "recovered_of_seven" in flat, label
        assert "repaired_of_seven" in flat, label
        # Full refuse histogram, counts and ids, each id beside its reason.
        for reason, (n, ids) in OPS_REFUSE_HISTOGRAM.items():
            assert reason in flat, f"{label}: {reason}"
            assert f"×{n}" in flat, f"{label}: {reason} count"
            for pid in ids:
                assert str(pid) in flat, f"{label}: {reason} {pid}"
        # As-recorded, never posed as our measurement.
        assert "as recorded" in lowered, label
        assert "not re-measured here" in lowered, label
        assert "emma" in lowered, label


def test_method_never_reports_the_allowed_zero_without_its_give_back():
    """0-of-7 was pre-registered — which is exactly why the regress travels with it.

    Goes red if either confusion figure, or the 'allowed outcome' framing,
    is dropped from the passage that carries the zero.
    """
    for text, label in d128_method_sections():
        flat = _flat(text)
        lowered = flat.lower()
        for key, value in OPS_CONFUSION.items():
            assert key in flat, f"{label}: {key}"
        assert "allowed outcome" in lowered, label
        assert "named finding" in lowered, label
        # ⚠ The give-back must sit in the passage that names the zero, not
        # merely somewhere on the page: a reader who stops after "0 of 7,
        # which we said was allowed" must already have seen the 5 and the 6.
        idx = lowered.find("n_d125_pass_d128_refuse")
        assert idx != -1, label
        passage = lowered[idx : idx + 700]
        assert "5" in passage, label
        assert "6" in passage, label
        assert "n_d126_pass_d128_refuse" in passage, label
        assert "bury" in passage or "hide" in passage, label


def test_method_keeps_d126_best_and_the_d127_failed_experiment_disclosed():
    """A D-128 result may not soften or replace either standing disclosure."""
    for text, label in d128_method_sections():
        flat = _flat(text)
        lowered = flat.lower()
        assert "d-126 remains the best experimental path" in lowered, label
        assert "so far" in lowered, label
        # D-127's own negative result stays, labelled as D-127's.
        assert "PASS 17" in flat, label
        assert "REFUSE 10" in flat, label
        assert "did not pay off" in lowered, label
        assert "0 of 3" in flat, label
        # The three-way comparison that makes "D-126 is better" a number.
        assert "2 of its primary 5" in lowered, label
        assert "0 of 7" in flat, label
        assert "3368" in flat, label
        assert "3394" in flat, label


def test_method_refuses_to_loosen_a_gate_flip_the_served_path_or_reopen_3432():
    for text, label in d128_method_sections():
        flat = _flat(text)
        lowered = flat.lower()
        assert "10.0 Å" in flat, label
        assert "no threshold moved" in lowered, label
        assert "default served structure is still the assembler" in lowered, label
        assert "never a pass count" in lowered, label
        assert "3432 stays accept-refuse" in lowered, label
        assert "not re-opened" in lowered or "not re-open" in lowered, label
        assert "w = 32" in lowered, label
        assert "not a measured optimum" in lowered, label
        # Recorded is not solved, said about these seven specifically.
        assert "seven recorded outcomes" in lowered, label
        assert "recorded is not a seam that was solved" in lowered, label
        for phrase in FORBIDDEN:
            assert phrase not in lowered, f"{label}: {phrase}"


def test_method_says_an_accepted_refusal_is_a_record_not_a_silence():
    """Matt SIGNED Phase 5 split: accept-refuse ≠ silence, in those terms."""
    for text, label in d128_method_sections():
        flat = _flat(text)
        lowered = flat.lower()
        assert "not a silence" in lowered, label
        assert "accept-refuse" in lowered, label
        assert "3432" in flat, label
        # The three things accept-refuse must NOT be read as.
        assert "dropped from the run" in lowered, label
        assert "skipped" in lowered, label
        assert "excluded from the inventory" in lowered, label
        assert "written row" in lowered, label
        # The negative result is owned, not narrated away.
        assert "measurement came out negative" in lowered, label


def test_method_refuses_a_linker_v2():
    """Matt SIGNED: 0-of-7 does not license another window family."""
    for text, label in d128_method_sections():
        flat = _flat(text)
        lowered = flat.lower()
        assert "no linker-v2" in lowered, label
        assert "d-126 is still the best of them" in lowered, label
        # Named as the D-127 failure repeating, not as a fresh idea.
        assert "wider one" in lowered and "narrower one" in lowered, label
        assert "until the count improves" in lowered, label
        assert "not a sixth" in lowered, label


# Phase 5 named-refuse labels are a LATER Spec (Trinity Phase 5 green +
# Emma GO). The inventory is recorded in the log for that Spec; writing a
# list down is not shipping a label, and this PR ships no label.
PHASE5_NAMED_REFUSE_INVENTORY = (2938, 2939, 3179, 3190, 3321, 3368, 3566, 3432)
PHASE4_NOT_YET_LABELLED = (3272, 3394)


def test_this_pr_ships_no_phase5_named_refuse_label_surface():
    """Disclosing a run's reasons is required; shipping a label vocabulary is not.

    ⚠ The line this guards: Method may say *what the run recorded*. It may
    not introduce a named-refuse **status** and apply it to an inventory —
    that is the Phase 5 Spec's, and naming an inventory has been mistaken
    for shipping the thing before (Spec §9, no named-exclusion-as-fix).
    """
    surfaces = list(d128_method_sections())
    surfaces.append((READER, "linker_seam_path_read"))
    surfaces.append((REVIEW_JSX, "AssemblyReview.jsx"))
    for text, label in surfaces:
        lowered = _flat(text).lower()
        for vocab in ("named refuse", "named-refuse", "named_refuse", "refuse label", "phase 5"):
            assert vocab not in lowered, f"{label}: {vocab}"
    # The log may (and must) carry the deferred inventory; the surfaces
    # may not. Recording it is how the later Spec inherits it.
    log_flat = _flat(LOG)
    assert "named-refuse" in log_flat.lower()
    assert "Trinity Phase 5 Spec" in log_flat
    for pid in PHASE5_NAMED_REFUSE_INVENTORY:
        assert str(pid) in log_flat, pid


def test_phase4_parents_are_not_labelled_with_a_d128_refuse():
    """3272 / 3394 are Phase 4, later still — not in any D-128 refuse listing.

    They stay legible where the record already carries them for a
    *different* path (D-127's histogram, D-126's recovered pair). What is
    forbidden is this PR attaching a **D-128** refuse to them.
    """
    for text, label in d128_method_sections():
        flat = _flat(text)
        lowered = flat.lower()
        idx = lowered.find("where the refuses came from")
        assert idx != -1, label
        passage = flat[idx : idx + 900]
        for pid in SEVEN_LINKER_PARENT_IDS:
            assert str(pid) in passage, f"{label}: {pid} missing from the D-128 refuse listing"
        for pid in PHASE4_NOT_YET_LABELLED:
            assert str(pid) not in passage, (
                f"{label}: {pid} is Phase 4 and must not be labelled with a D-128 refuse"
            )


def test_method_does_not_conflate_d128_reason_names_with_d127s():
    """`seam_jump_gt_10` is a new name, not a rename of `linker_jump_gt_10`."""
    for text, label in d128_method_sections():
        flat = _flat(text)
        lowered = flat.lower()
        assert "seam_jump_gt_10" in flat, label
        assert "linker_jump_gt_10" in flat, label
        # The distinction is stated, not left for the reader to infer.
        assert "measured after the single window move" in lowered, label


def test_living_log_records_the_ops_inject_with_its_provenance():
    log_flat = _flat(LOG)
    lowered = log_flat.lower()
    assert "d-128-b amendment 1" in lowered
    assert "ops honesty inject" in lowered
    assert OPS_TIP in log_flat
    assert OPS_OUT_ROOT in log_flat
    assert "not run, not queried, and not re-measured in this pr" in lowered
    for key, value in OPS_CONFUSION.items():
        assert key in log_flat, key
    for reason in OPS_REFUSE_HISTOGRAM:
        assert reason in log_flat, reason
    # The superseded draft claim is named rather than quietly overwritten.
    assert "supersedes an earlier claim" in lowered
    assert "there is no d-128 ops result" in lowered


def test_this_pr_ships_no_ops_run_no_new_spec_and_no_fly_post():
    """Emma hard stops: B only. Disclosure is not an ops lane."""
    stitch_specs = sorted(
        p.name for p in (ROOT / "docs").glob("SPEC-*.md") if "kabsch" in p.name or "seam" in p.name
    )
    assert stitch_specs == [
        "SPEC-kabsch-restitch.md",
        "SPEC-linker-seam-honesty.md",
        "SPEC-overlap-confidence-kabsch.md",
        "SPEC-piecewise-domain-kabsch.md",
    ], stitch_specs
    spec = (ROOT / "docs" / "SPEC-linker-seam-honesty.md").read_text(encoding="utf-8")
    flat = _flat(spec).lower()
    assert "10.0" in spec
    assert "do not raise" in flat
    assert "0-of-7 repaired is allowed" in flat or "0-of-7" in spec
    assert "never seams solved" in flat


def test_test_plan_and_architecture_record_d128_b():
    assert "T-1161" in PLAN_TEST
    assert "T-1171" in PLAN_TEST
    assert "D-128-B" in PLAN_TEST
    assert "linker_seam_path_read" in ARCH
    assert "D-128-B" in ARCH
    assert "five-path" in ARCH.lower() or "five paths" in ARCH.lower()


# ── UI wiring pins (the JSX can go red in vitest too) ─────────────────────


def test_review_card_renders_honesty_rows_and_derives_no_average():
    assert 'data-testid="d128-seam-honesty"' in REVIEW_JSX
    assert 'data-testid="d128-seams"' in REVIEW_JSX
    assert 'data-testid="d128-accepted"' in REVIEW_JSX
    assert "linker_seam" in REVIEW_JSX
    assert "seam_honesty" in REVIEW_JSX
    flat_jsx = _flat(REVIEW_JSX).lower()
    assert "one path at one seam" in flat_jsx
    assert "no average" in flat_jsx
    assert "unknown — not honest" in REVIEW_JSX
    assert "not defined on this path" in REVIEW_JSX
    assert "pre_transform_max_ca_jump_angstrom" in REVIEW_JSX
    assert "offending_seam_source" in REVIEW_JSX
    # No arithmetic over the honesty rows in the card.
    assert ".reduce(" not in REVIEW_JSX
    assert "Math.min" not in REVIEW_JSX
    assert "Math.max" not in REVIEW_JSX
    assert ".filter(" not in REVIEW_JSX.split("function DualPathHonesty")[1].split(
        "function PaeBadge"
    )[0]


def test_provenance_names_the_fifth_persist_stem():
    assert 'data-testid="d128-persist-stem"' in PROV_JSX
    assert "linker_seam" in PROV_JSX
    assert "five paths, not one population" in PROV_JSX
    assert "assembler until a later ops restitch GO names a swap" in PROV_JSX
