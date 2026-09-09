"""D-139 — the served PDB flips to D-126 for the recorded PASS 17. All of these must go red.

Phase 6 of the ``D-0043`` stitch honest-endpoint roadmap. ⚠ Vault ``D-0043``
is external numbering, **not** a project decision id.

The hard stops this suite exists to enforce, each written so it fails loudly
rather than quietly:

* **flipping without the allowlist must fail** — a parent outside the recorded
  seventeen keeps the assembler even with a perfect, accepted D-126 tree on
  disk beside it (``test_a_parent_outside_the_seventeen_never_flips_*``);
* **auto-flip must fail** — artifacts alone never flip anyone, and every one of
  the ten accept-refuse parents stays on the assembler with a full tree
  (``test_artifacts_alone_never_flip_*``);
* **no threshold loosen** — 10.0 Å and the three refuse reasons are unmoved;
* **no F-004 / rent / emit / other-44 fold**, and **no D-127 revival**;
* **the surfaces name which path is SERVED per parent, and never "solved"**.

⚠ **The count that could embarrass this decision is asserted, not omitted:**
no ``confidence_kabsch/`` tree is committed to this repository, so in this
tree seventeen parents are *eligible* and **zero** are *flipped*
(``test_no_confidence_kabsch_tree_is_committed_so_nothing_flips_here``).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.confidence_kabsch_path_read import (
    confidence_kabsch_sibling_path,
    confidence_kabsch_success_pdb_path,
)
from app.main import create_app
from app.phase5_named_refuse import ACCEPT_REFUSE_TEN, phase5_fate
from app.reads import (
    WAVE1_WAVE2_STITCHED_PARENT_IDS,
    get_census_detail,
    served_download_stem,
    served_path_block,
    served_plddt_path,
    served_structure_path,
)
from app.served_path_policy import (
    D126_OWN_PASS_N,
    D126_PASS_WITH_LATER_NAMED_REFUSE,
    D126_SERVED_PASS_SUBSET,
    NOT_IN_PASS_SUBSET,
    NO_ARTIFACTS,
    NO_SUCCESS_PDB,
    RUN_REFUSED,
    SERVED_ASSEMBLER,
    SERVED_CONFIDENCE_KABSCH,
    is_pass_subset,
    resolve_served_path,
)
from core.hold48_confidence_kabsch import (
    CONFIDENCE_RESTITCH_PARENT_IDS,
    RMSD_REFUSE_ANGSTROM,
)
from core.hold48_kabsch import REFUSE_REASONS
from db.models import Base, JobRecord, ProteinAnalysis

ROOT = Path(__file__).resolve().parent.parent
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
METHOD_MD = (ROOT / "docs" / "method-hold48-tiles.md").read_text(encoding="utf-8")
METHOD_NOTE = (ROOT / "ui" / "src" / "components" / "MethodNote.jsx").read_text(
    encoding="utf-8"
)
REVIEW_JSX = (ROOT / "ui" / "src" / "components" / "AssemblyReview.jsx").read_text(
    encoding="utf-8"
)
POLICY = (ROOT / "app" / "served_path_policy.py").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")

TOKEN = "test-secret-token"

# One in the seventeen, one outside it. 2817 is the first of the PASS list;
# 2939 is D-126's own refuse AND Phase 5 accept-refuse, so it is the parent a
# careless implementation is likeliest to flip.
PASS_PARENT = 2817
NON_PASS_PARENT = 2939

FORBIDDEN = (
    "seams solved",
    "seam solved",
    "seams fixed",
    "kabsch aligned",
    "full-length af-quality",
)


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


class _DummyQueue:
    def claim(self, worker_id, tier="local"):  # pragma: no cover - reads never queue
        raise AssertionError("a read route touched the queue")


def _engine():
    eng = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(eng)
    return eng


def _seed(engine, root: Path, parent_id: int) -> Path:
    """An assembled parent whose stored ``pdb_path`` is the assembler stitched.pdb."""
    home = root / str(parent_id)
    home.mkdir(parents=True, exist_ok=True)
    pdb = home / "stitched.pdb"
    pdb.write_text("HEADER assembler\nATOM      1  N   MET A   1\nEND\n", encoding="utf-8")
    (home / "stitched_plddt.json").write_text(json.dumps([70.0, 71.0]), encoding="utf-8")
    (home / "stitched_pae.json").write_text(json.dumps([[0.0]]), encoding="utf-8")
    with Session(engine) as s:
        s.add(
            ProteinAnalysis(
                id=parent_id,
                input_type="uniprot",
                input_value=f"Q{parent_id}",
                cohort_tranche=5,
                pdb_path=str(pdb),
                pae_json_path=str(home / "stitched_pae.json"),
                mean_plddt=61.07,
                meta={"hold48_kind": "parent", "span_aa": 2368},
            )
        )
        s.add(JobRecord(id=parent_id, analysis_id=parent_id, status="complete"))
        s.commit()
    return pdb


def _write_d126_tree(
    root: Path,
    parent_id: int,
    *,
    accepted: bool = True,
    with_pdb: bool = True,
    with_plddt: bool = True,
) -> Path:
    dest = root / "confidence_kabsch" / str(parent_id)
    dest.mkdir(parents=True, exist_ok=True)
    seam = {
        "moving_tile_index": 2,
        "reference_tile_index": 1,
        "overlap_start": 1529,
        "overlap_end": 1656,
        "n_ca": 128,
        "n_ca_eff": 96,
        "rmsd_angstrom": 2.5,
        "rmsd_full_overlap_angstrom": 8.0,
        "max_ca_jump_angstrom": 4.2,
        "trim_rounds": 2,
        "refuse_reason": None if accepted else "rmsd_gt_10",
    }
    (dest / "provenance.json").write_text(
        json.dumps(
            {
                "algorithm": "overlap_confidence_kabsch_then_winning_tile",
                "decision": "D-126",
                "parent_job_id": parent_id,
                "accepted": accepted,
                "seams": [seam],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (dest / "seams.jsonl").write_text(json.dumps(seam) + "\n", encoding="utf-8")
    if with_pdb:
        (dest / "stitched.pdb").write_text(
            "HEADER confidence-kabsch\nATOM      1  N   MET A   1\nEND\n", encoding="utf-8"
        )
    if with_plddt:
        (dest / "stitched_plddt.json").write_text(json.dumps([88.0, 89.0]), encoding="utf-8")
        (dest / "stitched_pae.json").write_text(json.dumps([[1.0]]), encoding="utf-8")
    return dest


def _client(engine, root: Path) -> TestClient:
    app = create_app(
        engine=engine, artifact_root=str(root), auth_token=TOKEN, queue=_DummyQueue()
    )
    return TestClient(app, raise_server_exceptions=True)


# ───────────────────────── the subset, and how it is known ─────────────────────

def test_the_pass_subset_is_exactly_the_recorded_seventeen():
    """⚠ The load-bearing enumeration. Two on-disk records must agree, parent for parent.

    This is not a restatement of the constant: it recomputes the subset from the
    27-parent inventory minus the accept-refuse ten, which is a different pair of
    files from the one the constant was typed out of.
    """
    assert len(D126_SERVED_PASS_SUBSET) == 17
    assert D126_SERVED_PASS_SUBSET == (
        frozenset(WAVE1_WAVE2_STITCHED_PARENT_IDS) - frozenset(ACCEPT_REFUSE_TEN)
    )
    assert D126_SERVED_PASS_SUBSET == (
        frozenset(CONFIDENCE_RESTITCH_PARENT_IDS) - frozenset(ACCEPT_REFUSE_TEN)
    )
    # And it is a subset of the 27 — never a parent from the other 18 of the 45.
    assert D126_SERVED_PASS_SUBSET < frozenset(WAVE1_WAVE2_STITCHED_PARENT_IDS)


def test_the_seventeen_are_the_ids_the_method_page_recorded():
    """⚠ D-016: the artefact behind the list, parsed back out rather than retyped.

    ``docs/method-hold48-tiles.md`` §"Inventory on the 27 (no silent holes)" is
    where the labels were recorded. If that section is edited, this fails — which
    is the point: the allowlist may not drift away from the record it came from.
    """
    marker = "- **17 PASS** (unchanged):"
    start = METHOD_MD.find(marker)
    assert start != -1, "the Method page must still carry the 17 PASS inventory line"
    end = METHOD_MD.find("- **10 accept-refuse:**", start)
    assert end != -1
    recorded = {int(n) for n in re.findall(r"\b\d{4}\b", METHOD_MD[start:end])}
    assert recorded == set(D126_SERVED_PASS_SUBSET), (
        "the served allowlist and the Method page's recorded 17 PASS disagree"
    )


def test_the_twenty_four_is_named_and_is_deliberately_not_the_subset():
    """⚠ 24 is the number the next reader reaches for first, and it is the wrong one.

    D-126's own run refused three of the 27. Seven of the remaining 24 later drew
    a named refuse from a *different* path, and serving those would hand out bytes
    we hold a recorded measurement against.
    """
    assert D126_OWN_PASS_N == 24
    assert len(D126_PASS_WITH_LATER_NAMED_REFUSE) == 7
    assert D126_OWN_PASS_N - 7 == 17
    # Each of the seven really is accept-refuse, and really is NOT in the subset.
    for pid in D126_PASS_WITH_LATER_NAMED_REFUSE:
        assert pid in ACCEPT_REFUSE_TEN, pid
        assert pid not in D126_SERVED_PASS_SUBSET, pid
    # 2939 / 3272 / 3432 are D-126's OWN refuses and are the rest of the ten.
    assert set(ACCEPT_REFUSE_TEN) - set(D126_PASS_WITH_LATER_NAMED_REFUSE) == {
        2939, 3272, 3432,
    }


def test_every_accept_refuse_parent_is_excluded_from_the_subset():
    for pid in ACCEPT_REFUSE_TEN:
        assert not is_pass_subset(pid), pid
        assert pid not in D126_SERVED_PASS_SUBSET, pid


def test_the_served_answer_agrees_with_the_label_registry_for_all_ten():
    """⚠ Two live surfaces may not contradict each other.

    ``phase5_fate()`` has shipped ``served_path: "assembler"`` for the ten since
    D-129-B. If the flip ever admitted one of them, the review card would say
    both things at once.
    """
    for pid in ACCEPT_REFUSE_TEN:
        assert phase5_fate(pid)["served_path"] == "assembler", pid
        block = resolve_served_path(
            "/nonexistent", parent_analysis_id=pid, parent_job_id=pid
        )
        assert block["served"] == SERVED_ASSEMBLER, pid


# ───────────────────────── HARD STOP: no allowlist, no flip ────────────────────

def test_a_parent_outside_the_seventeen_never_flips_even_with_a_perfect_tree(tmp_path):
    """⚠⚠ HARD STOP. A complete, accepted D-126 tree must NOT flip a non-PASS parent."""
    _write_d126_tree(tmp_path, NON_PASS_PARENT)
    block = resolve_served_path(
        tmp_path,
        parent_analysis_id=NON_PASS_PARENT,
        parent_job_id=NON_PASS_PARENT,
        assembler_pdb_path=str(tmp_path / str(NON_PASS_PARENT) / "stitched.pdb"),
    )
    assert block["served"] == SERVED_ASSEMBLER
    assert block["flipped"] is False
    assert block["eligible"] is False
    assert block["not_flipped_reason"] == NOT_IN_PASS_SUBSET


def test_a_parent_outside_the_seventeen_never_flips_over_http(tmp_path):
    """The same hard stop at the surface that actually hands out bytes."""
    engine = _engine()
    _seed(engine, tmp_path, NON_PASS_PARENT)
    _write_d126_tree(tmp_path, NON_PASS_PARENT)
    r = _client(engine, tmp_path).get(f"/api/analyses/{NON_PASS_PARENT}/structure")
    assert r.status_code == 200
    assert "assembler" in r.text
    assert "confidence-kabsch" not in r.text
    assert "stitched_confidence_kabsch" not in r.headers.get("content-disposition", "")


def test_a_parent_outside_the_twenty_seven_entirely_never_flips(tmp_path):
    """⚠ The other 18 of the 45 are claimed for nothing and are not eligible."""
    outsider = 9999
    assert outsider not in WAVE1_WAVE2_STITCHED_PARENT_IDS
    _write_d126_tree(tmp_path, outsider)
    block = resolve_served_path(
        tmp_path, parent_analysis_id=outsider, parent_job_id=outsider
    )
    assert block["served"] == SERVED_ASSEMBLER
    assert block["not_flipped_reason"] == NOT_IN_PASS_SUBSET


# ───────────────────────── HARD STOP: artifacts never auto-flip ────────────────

def test_artifacts_alone_never_flip_any_of_the_accept_refuse_ten(tmp_path):
    """⚠⚠ HARD STOP — the auto-flip guard, over the whole population that must not move.

    Every one of the ten gets a complete, accepted tree with a stitched.pdb in it.
    Not one may flip. This is the assertion that goes red if a future edit ever
    makes "the tree is on disk" sufficient.
    """
    for pid in ACCEPT_REFUSE_TEN:
        _write_d126_tree(tmp_path, pid)
        block = resolve_served_path(
            tmp_path, parent_analysis_id=pid, parent_job_id=pid
        )
        assert block["served"] == SERVED_ASSEMBLER, pid
        assert block["flipped"] is False, pid
        assert block["not_flipped_reason"] == NOT_IN_PASS_SUBSET, pid


def test_the_policy_declares_no_auto_flip_and_never_consults_a_pass_count(tmp_path):
    """⚠ The authority is the enumerated allowlist, never an accept count.

    A tree whose provenance claims a glowing rollup — including one that asserts
    it passed everything — still cannot admit a parent the allowlist excludes.
    """
    dest = _write_d126_tree(tmp_path, NON_PASS_PARENT)
    prov = json.loads((dest / "provenance.json").read_text(encoding="utf-8"))
    prov.update({"pass": 27, "n_pass": 27, "recovered_of_primary_five": 5})
    (dest / "provenance.json").write_text(json.dumps(prov), encoding="utf-8")
    block = resolve_served_path(
        tmp_path, parent_analysis_id=NON_PASS_PARENT, parent_job_id=NON_PASS_PARENT
    )
    assert block["served"] == SERVED_ASSEMBLER
    assert block["auto_flip"] is False


# ───────────────────────── fail-closed on each of the four yeses ───────────────

def test_an_eligible_parent_with_no_tree_stays_on_the_assembler(tmp_path):
    block = resolve_served_path(
        tmp_path, parent_analysis_id=PASS_PARENT, parent_job_id=PASS_PARENT
    )
    assert block["eligible"] is True
    assert block["served"] == SERVED_ASSEMBLER
    assert block["not_flipped_reason"] == NO_ARTIFACTS


def test_an_eligible_parent_whose_run_refused_stays_on_the_assembler(tmp_path):
    """⚠ A recorded refusal is honoured as recorded. No threshold is re-read to admit it."""
    _write_d126_tree(tmp_path, PASS_PARENT, accepted=False)
    block = resolve_served_path(
        tmp_path, parent_analysis_id=PASS_PARENT, parent_job_id=PASS_PARENT
    )
    assert block["eligible"] is True
    assert block["served"] == SERVED_ASSEMBLER
    assert block["not_flipped_reason"] == RUN_REFUSED


def test_a_leftover_pdb_beside_a_refusal_is_never_served(tmp_path):
    """⚠ Fail-closed, the same rule D-126-B's reader already applies to the card."""
    _write_d126_tree(tmp_path, PASS_PARENT, accepted=False, with_pdb=True)
    assert (tmp_path / "confidence_kabsch" / str(PASS_PARENT) / "stitched.pdb").is_file()
    block = resolve_served_path(
        tmp_path, parent_analysis_id=PASS_PARENT, parent_job_id=PASS_PARENT
    )
    assert block["served"] == SERVED_ASSEMBLER
    assert block["not_flipped_reason"] == RUN_REFUSED
    assert (
        confidence_kabsch_success_pdb_path(
            tmp_path, parent_analysis_id=PASS_PARENT, parent_job_id=PASS_PARENT
        )
        is None
    )


def test_an_accepted_tree_with_no_pdb_stays_on_the_assembler(tmp_path):
    _write_d126_tree(tmp_path, PASS_PARENT, accepted=True, with_pdb=False)
    block = resolve_served_path(
        tmp_path, parent_analysis_id=PASS_PARENT, parent_job_id=PASS_PARENT
    )
    assert block["served"] == SERVED_ASSEMBLER
    assert block["not_flipped_reason"] == NO_SUCCESS_PDB


def test_every_refusal_names_a_reason_and_carries_its_note(tmp_path):
    """⚠ "assembler" with no reason cannot tell 'never eligible' from 'the run refused'."""
    cases = [
        (NON_PASS_PARENT, lambda: None, NOT_IN_PASS_SUBSET),
        (PASS_PARENT, lambda: None, NO_ARTIFACTS),
        (PASS_PARENT, lambda: _write_d126_tree(tmp_path, PASS_PARENT, accepted=False),
         RUN_REFUSED),
    ]
    for pid, setup, expected in cases:
        setup()
        block = resolve_served_path(tmp_path, parent_analysis_id=pid, parent_job_id=pid)
        assert block["not_flipped_reason"] == expected, pid
        assert block["not_flipped_note"], expected
        assert block["solved"] is False


# ───────────────────────── the positive case, end to end ───────────────────────

def test_an_eligible_parent_with_an_accepted_tree_is_served_d126(tmp_path):
    _write_d126_tree(tmp_path, PASS_PARENT)
    block = resolve_served_path(
        tmp_path, parent_analysis_id=PASS_PARENT, parent_job_id=PASS_PARENT
    )
    assert block["served"] == SERVED_CONFIDENCE_KABSCH
    assert block["flipped"] is True
    assert block["eligible"] is True
    assert block["not_flipped_reason"] is None
    assert block["persist_stem"] == f"confidence_kabsch/{PASS_PARENT}"
    assert block["served_pdb_path"].endswith(
        f"confidence_kabsch/{PASS_PARENT}/stitched.pdb"
    )
    assert block["download_stem"] == "stitched_confidence_kabsch"
    assert block["solved"] is False


def test_the_route_hands_out_the_d126_bytes_under_a_name_that_says_so(tmp_path):
    """⚠ Never ``stitched.pdb``: two files, one name, different coordinates."""
    engine = _engine()
    _seed(engine, tmp_path, PASS_PARENT)
    _write_d126_tree(tmp_path, PASS_PARENT)
    r = _client(engine, tmp_path).get(f"/api/analyses/{PASS_PARENT}/structure")
    assert r.status_code == 200
    assert "confidence-kabsch" in r.text
    assert "HEADER assembler" not in r.text
    assert "stitched_confidence_kabsch.pdb" in r.headers["content-disposition"]


def test_the_plddt_and_pae_travel_with_the_served_structure(tmp_path):
    """⚠ D-126 runs its own winner-tile pass, so assembler pLDDT would mis-colour it."""
    engine = _engine()
    _seed(engine, tmp_path, PASS_PARENT)
    _write_d126_tree(tmp_path, PASS_PARENT)
    client = _client(engine, tmp_path)
    assert client.get(f"/api/analyses/{PASS_PARENT}/plddt").json() == [88.0, 89.0]
    assert client.get(f"/api/analyses/{PASS_PARENT}/pae").json() == [[1.0]]


def test_a_flipped_parent_with_no_sibling_confidence_keeps_the_assembler_plddt(tmp_path):
    """⚠ The fallback is INDEPENDENT and fail-closed: a missing sibling is not a 404."""
    engine = _engine()
    _seed(engine, tmp_path, PASS_PARENT)
    _write_d126_tree(tmp_path, PASS_PARENT, with_plddt=False)
    assert (
        confidence_kabsch_sibling_path(
            tmp_path / "confidence_kabsch" / str(PASS_PARENT) / "stitched.pdb",
            "stitched_plddt.json",
        )
        is None
    )
    r = _client(engine, tmp_path).get(f"/api/analyses/{PASS_PARENT}/plddt")
    assert r.status_code == 200
    assert r.json() == [70.0, 71.0]


def test_an_unflipped_parent_is_served_byte_for_byte_what_it_always_was(tmp_path):
    """⚠ The regression that matters: nothing changes for anyone the gate excludes."""
    engine = _engine()
    stored = _seed(engine, tmp_path, NON_PASS_PARENT)
    _write_d126_tree(tmp_path, NON_PASS_PARENT)
    assert served_structure_path(engine, NON_PASS_PARENT, artifact_root=tmp_path) == str(
        stored
    )
    assert served_download_stem(engine, NON_PASS_PARENT, artifact_root=tmp_path) == (
        "stitched"
    )
    assert served_plddt_path(engine, NON_PASS_PARENT, artifact_root=tmp_path) == str(
        stored.parent / "stitched_plddt.json"
    )


def test_an_unknown_id_resolves_to_nothing_rather_than_exploding(tmp_path):
    engine = _engine()
    assert served_path_block(engine, 424242, artifact_root=tmp_path) is None
    assert served_structure_path(engine, 424242, artifact_root=tmp_path) is None


# ───────────────────────── the review card names it per parent ─────────────────

def test_the_review_card_names_the_served_path_and_the_reason(tmp_path):
    engine = _engine()
    _seed(engine, tmp_path, PASS_PARENT)
    detail = get_census_detail(engine, PASS_PARENT, artifact_root=tmp_path)
    served = detail["assembly_review"]["served_path"]
    assert served["served"] == SERVED_ASSEMBLER
    assert served["eligible"] is True
    assert served["not_flipped_reason"] == NO_ARTIFACTS
    assert served["pass_subset_n"] == 17
    assert served["gate_angstrom"] == 10.0
    assert served["gate_moved"] is False
    assert served["solved"] is False


def test_the_review_card_marks_exactly_one_path_as_served(tmp_path):
    """⚠ `default_served` keeps its old meaning; the resolved answer rides separately."""
    engine = _engine()
    _seed(engine, tmp_path, PASS_PARENT)
    _write_d126_tree(tmp_path, PASS_PARENT)
    review = get_census_detail(engine, PASS_PARENT, artifact_root=tmp_path)[
        "assembly_review"
    ]
    five = review["five_path"]
    assert [name for name, block in five.items() if block.get("served")] == [
        "confidence_kabsch"
    ]
    # The four earlier decisions' meaning is untouched.
    assert five["assembler"]["default_served"] is True
    for name in ("kabsch", "confidence_kabsch", "piecewise_kabsch", "linker_seam"):
        assert five[name].get("default_served") is not True, name
    assert review["served_path"]["served"] == SERVED_CONFIDENCE_KABSCH


def test_an_accept_refuse_parent_card_says_assembler_beside_its_label(tmp_path):
    engine = _engine()
    _seed(engine, tmp_path, NON_PASS_PARENT)
    _write_d126_tree(tmp_path, NON_PASS_PARENT)
    review = get_census_detail(engine, NON_PASS_PARENT, artifact_root=tmp_path)[
        "assembly_review"
    ]
    assert review["served_path"]["served"] == SERVED_ASSEMBLER
    assert review["served_path"]["not_flipped_reason"] == NOT_IN_PASS_SUBSET
    assert review["phase5_fate"]["served_path"] == "assembler"
    assert review["phase5_fate"]["is_accept_refuse"] is True


# ───────────────────────── the disqualifying count, stated ─────────────────────

def test_no_confidence_kabsch_tree_is_committed_so_nothing_flips_here():
    """⚠⚠ D-016 — the count that could embarrass this decision, asserted rather than omitted.

    Seventeen parents are ELIGIBLE. **Zero** are FLIPPED in this repository,
    because the D-126 OPS output was never committed. If a tree is ever checked
    in, this test fails and whoever did it must say so in the log.
    """
    trees = [
        p for p in ROOT.rglob("confidence_kabsch")
        if p.is_dir() and ".git" not in p.parts
    ]
    assert trees == [], f"a confidence_kabsch tree is now committed: {trees}"
    # And the honesty surfaces say the number out loud.
    assert "zero are" in _flat(METHOD_MD).lower()
    assert "eligible and zero are" in _flat(METHOD_NOTE).lower()


# ───────────────────────── the hard stops, as properties ───────────────────────

def test_no_threshold_was_loosened_and_the_refuse_reasons_are_unmoved():
    assert RMSD_REFUSE_ANGSTROM == 10.0
    assert REFUSE_REASONS == frozenset(
        {"overlap_ca_lt_3", "rmsd_gt_10", "singular_covariance"}
    )
    # The policy module holds no geometry and no threshold of its own.
    for banned in ("import numpy", "def kabsch", "rotation", "sqrt(", "trim_"):
        assert banned not in POLICY, banned


def test_this_pr_ships_no_ops_no_rent_no_emit_and_no_f004():
    """Hard stops, checked against the TREE rather than against intent.

    ⚠ Deliberately not a ``git diff`` against ``origin/main``: the gate checks
    out a merge ref at depth 1, so that ref does not exist there and the check
    would have passed by erroring — or skipped, which is the same thing wearing
    a nicer word. These are properties of the files instead, so they hold on any
    checkout.
    """
    # No stitch-family core module was reached into. D-139 selects among
    # outcomes those modules already recorded; it writes no geometry, so none of
    # them may so much as name it (the convention D-129 / D-130 use for the same
    # hard stop, and the sha256 pins in those suites are the second half of it).
    for name in (
        "hold48.py", "hold48_stitch.py", "hold48_kabsch.py",
        "hold48_confidence_kabsch.py", "hold48_piecewise_kabsch.py",
        "hold48_linker_seam.py", "hold48_residual_rmsd.py",
    ):
        text = (ROOT / "core" / name).read_text(encoding="utf-8")
        assert "D-139" not in text, f"core/{name} names D-139 — this is not a geometry change"
        assert "served_path_policy" not in text, f"core/{name} imports the selector"

    # No migration, no queue, no worker change: nothing here touches the write path.
    for banned in ("alembic", "op.add_column", "JobRecord(", "requests.post", "fly.io"):
        assert banned not in POLICY, banned
    # No F-004 / ranking / rent / emit reached into by the selector.
    # ⚠ Word-bounded: a bare `in` check for "rent" matches every "parent" on the
    # page, which is a guard that reports its own good news and nothing else.
    routes = (ROOT / "app" / "read_routes.py").read_text(encoding="utf-8")
    lowered = POLICY.lower()
    for banned in ("f-004", "ranking_run", "runpod", "rent", "rental", "emit"):
        assert not re.search(rf"\b{re.escape(banned)}\b", lowered), (
            f"served_path_policy.py names {banned}"
        )
    assert "served_download_stem" in routes and "served_structure_path" in routes


def test_d127_piecewise_is_not_resurrected_as_this_campaign():
    """⚠ Hard stop. The flip serves D-126; D-127 is named only as excluded."""
    assert "piecewise" not in POLICY.lower()
    assert "SERVED_CONFIDENCE_KABSCH" in POLICY
    assert "piecewise_kabsch" not in _flat(POLICY)
    d139 = _d139_entry()
    lowered = _flat(d139).lower()
    assert "not d-127 piecewise resurrected" in lowered or (
        "d-127 piecewise is not resurrected" in lowered
    )


def test_no_surface_calls_a_served_structure_solved():
    surfaces = (
        (METHOD_MD, "method-hold48-tiles.md"),
        (METHOD_NOTE, "MethodNote.jsx"),
        (REVIEW_JSX, "AssemblyReview.jsx"),
        (POLICY, "served_path_policy.py"),
    )
    for text, label in surfaces:
        lowered = _flat(text).lower()
        for phrase in FORBIDDEN:
            assert phrase not in lowered, f"{label}: {phrase}"
        assert "not scientifically solved" in lowered or "not a solved" in lowered, label


def test_both_method_surfaces_name_the_served_path_rule_and_its_limits():
    for text, label in ((METHOD_MD, "method-hold48-tiles.md"), (METHOD_NOTE, "MethodNote.jsx")):
        flat = _flat(text)
        lowered = flat.lower()
        assert "d-139" in lowered, label
        assert "seventeen" in lowered, label
        assert "10.0 Å" in flat, label
        assert "no auto-flip" in lowered or "no <strong>auto-flip" in lowered, label
        assert "24 − 7 = 17" in flat, label
        assert "accept-refuse" in lowered, label
        assert "never claim 27/27 pass" in lowered, label
        # The four yeses are all named, so a reader can check the gate.
        for reason in (
            "not_in_pass_subset",
            "no_confidence_kabsch_artifacts",
            "confidence_kabsch_refused",
            "no_confidence_kabsch_success_pdb",
        ):
            assert reason in flat, f"{label}: {reason}"
        # The seventeen are enumerated on the page, not summarised.
        for pid in sorted(D126_SERVED_PASS_SUBSET):
            assert str(pid) in flat, f"{label}: {pid}"


def test_the_ui_review_card_renders_the_reason_not_just_the_answer():
    assert 'data-testid="served-path"' in REVIEW_JSX
    assert 'data-testid="served-path-reason"' in REVIEW_JSX
    assert 'data-testid="served-path-name"' in REVIEW_JSX
    assert "not_flipped_reason" in REVIEW_JSX
    assert "no auto-flip" in REVIEW_JSX


def test_the_method_page_registers_the_new_section_with_the_d138_rail():
    """D-138: a Method heading without an `id` drops out of the contents rail."""
    assert '<h3 id="served-path-d126">' in METHOD_NOTE
    assert "Which structure you are actually handed (D-139)" in METHOD_NOTE


def test_the_earlier_served_claims_do_not_stand_alone():
    """⚠ D-129-C's rule: a claim a later decision narrowed carries its supersession.

    Every "the default served structure is still the assembler" sentence predates
    D-139 and is now true only of the parents its own section is about. None of
    them may sit on the page without saying so.
    """
    for text, label in ((METHOD_MD, "method-hold48-tiles.md"), (METHOD_NOTE, "MethodNote.jsx")):
        flat = _flat(text)
        for m in re.finditer(
            r"default served structure is still the assembler", flat
        ):
            window = flat[m.start(): m.start() + 400]
            assert "D-139" in window, (
                f"{label}: a bare 'still the assembler' claim at offset {m.start()}"
            )


# ───────────────────────── the log leads the code ──────────────────────────────

def _d139_entry() -> str:
    """The D-139 entry only — anchored to a line start, bounded by its neighbour."""
    start = LOG.index("\n### D-139 —") + 1
    nxt = re.search(r"^### (?!D-139\b)", LOG[start + 1:], re.M)
    return LOG[start: start + 1 + nxt.start()] if nxt else LOG[start:]


def test_d139_entry_exists_in_the_living_log():
    """⚠ The check is the `### D-139` HEADING, never a citation of it (D-062 / item 7).

    ⚠⚠ **Widened at D-140 — by naming the successor, not by dropping the bar.**
    ``"### D-140" not in LOG`` reddened BY DESIGN when the ADC Pipeline
    programme-fields entry landed, and that redness is the whole point: **that entry
    was written as `### D-139` too.** Both branches were cut from ``dd06e9c``, both
    read ``gh pr list --state open``, both found no ``D-1NN`` spender, and neither
    could see the other because the pipeline branch was still local when this one
    looked. This work merged first and its commit message assigned the resolution
    (*"Pipeline #263 takes D-140."*), so 139 stays here and 140 is now spent — by a
    named entry, asserted below. A bare ``### D-141`` still reddens.
    """
    assert re.search(r"^### D-139 — The served PDB stops being a constant", LOG, re.M)
    assert len(re.findall(r"^### D-139", LOG, re.M)) == 1, "exactly one D-139 entry"
    assert re.search(r"^### D-140 — The ADC Pipeline shelf gets a cancer type", LOG, re.M), (
        "D-140 is the recorded successor id; it must be the ADC pipeline "
        "programme-fields entry, not some other entry that took the number"
    )
    # ⚠ Widened again at D-141 by ADDING, never by a `>=`. D-141 lands the D-126 OPS
    # trees on the volume so this decision's gate has bytes to answer with; it took
    # 141 because #263 already held 140, and #263 then merged at `578f5ac` — which
    # reddened this assertion by design and put both ids here rather than either out.
    assert re.search(r"^### D-141 — The gate had nothing to answer with", LOG, re.M), (
        "D-141 must be the confidence-Kabsch lander entry, not some other entry "
        "that took the number"
    )
    # ⚠ Widened again at D-142 by ADDING. The Track B structural-only copy entry claimed
    # 142 off `30f402f`; it changes no served path, no gate and no threshold.
    assert re.search(r"^### D-142 — Track B stops claiming a composite", LOG, re.M), (
        "D-142 must be the Track B structural-only copy entry, not some other entry "
        "that took the number"
    )
    assert "\n### D-143" not in LOG, "D-143 is the next free integer"


def test_the_entry_records_the_subset_its_provenance_and_the_zero():
    entry = _d139_entry()
    flat = _flat(entry)
    lowered = flat.lower()
    assert "d-0043" in lowered and "phase 6" in lowered
    assert "external numbering" in lowered
    assert "d-0037" in lowered
    # The subset, its two sources, and the arithmetic that rejects 24.
    assert "method-hold48-tiles.md" in flat
    assert "accept_refuse_ten" in lowered
    assert "24 − 7 = 17" in flat
    for pid in sorted(D126_SERVED_PASS_SUBSET):
        assert str(pid) in flat, pid
    # ⚠ The disqualifying count is in the entry, not only in the code.
    assert "zero parents" in lowered
    assert "flipped = 0" in lowered


def test_the_entry_keeps_every_hard_stop_from_the_go():
    entry = _flat(_d139_entry()).lower()
    for phrase in (
        "10.0 å",
        "no auto-flip",
        "no f-004",
        "no rent",
        "no emit",
        "no threshold moves",
        "never claim 27/27 pass",
        "rental stays **closed**",
    ):
        assert phrase in entry, f"the D-139 entry dropped: {phrase}"
    assert "d-127 piecewise is not resurrected" in entry


def test_the_entry_carries_a_deep_learning_justification():
    """⚠ ARCHITECTURE §1 / CLAUDE.md: a decision states how it serves the DL core."""
    entry = _d139_entry()
    assert "**Deep-learning justification.**" in entry
    lowered = _flat(entry).lower()
    assert "esmfold" in lowered
    assert "plddt" in lowered or "per-residue" in lowered


def test_architecture_records_the_shipped_shape():
    """⚠ CLAUDE.md rule 2: ARCHITECTURE.md is current before the PR is filed."""
    assert "D-139" in ARCH
    lowered = _flat(ARCH).lower()
    assert "served_path_policy" in lowered
    assert "served path" in lowered
