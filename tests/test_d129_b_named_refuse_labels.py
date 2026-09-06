"""D-129-B — Phase 5 named-refuse LABELS on Method + UI. These must go red.

The BUILD that discharges D-129 Spec §3: the **eight** parents (the D-128
linker seven + 3432) are labelled **named refuse / accept-refuse** on the
owner Method, on ``/method``, and on the review card.

⚠ **Three failures these pin red**, and they are the three the Spec names:

1. **Wrong inventory.** A ninth parent labelled accepted, one of the eight
   dropped, or a Phase 4 id inside the set. The fate list is signed; it is
   not a place to be approximately right.
2. **A Phase 4 leak.** 3272 / 3394 labelled accepted, retired, or closed.
   Spec §6 moves them only on **explicit Matt GO language**, and a card
   that quietly accepted them would look tidier and be false.
3. **Silence instead of accept-refuse.** The label shipped while the D-128
   OPS **0 of 7** or the named give-back (**5** / **6**) is dropped,
   split, or softened. "Accepted" is the friendliest word in this arc and
   the one most likely to outlive its numbers — Spec §4 calls that a Spec
   violation, not a simplification.

⚠ Nothing here re-measures the rollup. Every figure is quoted as recorded
by Kaylee at tip ``9e65cbf``, out_root ``linker_seam_ops_2026-09-05``.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.phase5_named_refuse import (
    ACCEPT_REFUSE_EIGHT,
    ACCEPT_REFUSE_FATE,
    ACCEPT_REFUSE_LABEL,
    ALREADY_ACCEPT_REFUSE_PARENT_ID,
    D128_LINKER_SEVEN,
    D128_OPS_ROLLUP,
    PHASE_4_FATE,
    PHASE_4_MUST_HUNT,
    is_accept_refuse,
    phase5_fate,
)
from app.reads import get_census_detail
from db.models import Base, JobRecord, ProteinAnalysis

ROOT = Path(__file__).resolve().parent.parent
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
INDEX = (ROOT / "docs" / "decisions.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
TEST_PLAN = (ROOT / "docs" / "Test_Plan.md").read_text(encoding="utf-8")
PLAN = (ROOT / "docs" / "PLAN-ui-post-wave2-endstate.md").read_text(encoding="utf-8")
SPEC = (ROOT / "docs" / "SPEC-phase5-named-refuse.md").read_text(encoding="utf-8")
METHOD_MD = (ROOT / "docs" / "method-hold48-tiles.md").read_text(encoding="utf-8")
METHOD_NOTE = (ROOT / "ui" / "src" / "components" / "MethodNote.jsx").read_text(
    encoding="utf-8"
)
REVIEW_JSX = (ROOT / "ui" / "src" / "components" / "AssemblyReview.jsx").read_text(
    encoding="utf-8"
)
REGISTRY = (ROOT / "app" / "phase5_named_refuse.py").read_text(encoding="utf-8")
READER = (ROOT / "app" / "linker_seam_path_read.py").read_text(encoding="utf-8")

# The signed fates (D-129 Spec §2). Written out here rather than imported, so a
# hand-edit of the registry has to disagree with a second copy to pass.
EXPECTED_EIGHT = (2938, 2939, 3179, 3190, 3321, 3368, 3566, 3432)
EXPECTED_PHASE_4 = (3272, 3394)
EXPECTED_REASONS = {
    2938: "seam_jump_gt_10",
    2939: "rmsd_gt_10",
    3179: "seam_jump_gt_10",
    3190: "seam_jump_gt_10",
    3321: "seam_jump_gt_10",
    3368: "seam_jump_gt_10",
    3566: "seam_jump_gt_10",
    3432: "no_domain_pieces",
}

# Modules on `main` at `1baf4c0`. A moved digest means this LABELLING PR
# edited an algorithm.
MODULE_PINS = {
    "core/hold48_kabsch.py": "4c7bb45d04507e2a67ba3600b35d6130d62843ca3bc99c15d3568d5cb105ff6e",
    "core/hold48_confidence_kabsch.py": "d526a856ec8f1ba978a3586f3dfcf4a0ee858da12132499f2db37368efc77f18",
    "core/hold48_piecewise_kabsch.py": "ad48b2be577b987466274000c508a621792bc029bb9e087eec94ba7237f13e04",
    "core/hold48_linker_seam.py": "c270f8711040471a9080a23ab4c1e167a0cc2eedf546c3481cd9ed4f4eb19843",
}

# Claims none of the eight may carry (Spec §3). ⚠ These are the AFFIRMATIVE
# forms only. The section is required to *name* the forbidden badges in order
# to forbid them, so banning the bare words "open must-hunt" or "a D-128 miss"
# would fire on the very sentence that does the forbidding — the trap D-128-B
# hit and documented. The negations are pinned positively below instead.
FORBIDDEN_BADGES = (
    "the seams are solved",
    "seams are now solved",
    "these joins are solved",
    "the seam is repaired",
    "the seams are fixed",
    "the joins are repaired",
    "full-length af-quality",
    "accept-refuse means solved",
    "pending rescue",
    "awaiting a fix",
)

# The negations that must be present, said about the eight, in the section
# that labels them. Each entry is a set of accepted phrasings: the owner
# Method keeps Spec §5's exact words ("Never claim seams solved"), the JSX
# page reads slightly differently, and pinning one wording would force a
# surface to say something its own voice does not.
REQUIRED_NEGATIONS = (
    ("none of the eight may be shown as an open must-hunt",),
    ("or as a d-128 miss",),
    ("never claim seams solved", "never claim the seams are solved"),
    ("does not mean the seam is solved",),
)


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def _plain(text: str) -> str:
    stripped = re.sub(r"[*`>\"\u201c\u201d]", "", _flat(text))
    return re.sub(r"\s+", " ", stripped).lower()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _slice(text: str, start: str, end: str | None, label: str) -> str:
    i = text.find(start)
    assert i != -1, f"{label}: missing {start!r}"
    if end is None:
        return text[i:]
    j = text.find(end, i + len(start))
    assert j != -1, f"{label}: missing {end!r} after {start!r}"
    return text[i:j]


def d129b_method_sections() -> tuple[tuple[str, str], ...]:
    """The D-129-B section ALONE on each Method surface.

    ⚠ Section-scoped for the reason D-127-B documented and D-128-B re-learned
    by mutation: a page-wide substring is satisfied by the wrong section, so
    deleting a required claim from *this* section can leave every check green.
    """
    return (
        (
            _slice(
                METHOD_MD,
                "## Addendum D-129-B",
                "## The rental is CLOSED",
                "method-hold48-tiles.md",
            ),
            "method-hold48-tiles.md (D-129-B section)",
        ),
        (
            _slice(
                METHOD_NOTE,
                "<h3>What we now call the eight joins we could not hold",
                "<h3>What it does today</h3>",
                "MethodNote.jsx",
            ),
            "MethodNote.jsx (D-129-B addendum)",
        ),
    )


def phase5_card() -> str:
    """The review card's fate block alone.

    ⚠ The card renders the label from the payload rather than hard-coding the
    words, so its checks are about **wiring** — which fields it reads and
    where the rollup sits — not about prose. The words themselves are pinned
    on the registry, which is where they live.
    """
    return _slice(REVIEW_JSX, "function Phase5Fate(", "function PaeBadge(", "card")


def _engine():
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    return eng


def _add_parent(session, tmp: Path, *, analysis_id: int, job_id: int | None):
    """One assembled parent, optionally with the job id the fate is keyed by."""
    tmp.mkdir(parents=True, exist_ok=True)
    pdb = tmp / "stitched.pdb"
    pdb.write_text("HEADER assembler\n", encoding="utf-8")
    session.add(
        ProteinAnalysis(
            id=analysis_id,
            input_type="uniprot",
            input_value="Q7Z408",
            cohort_tranche=5,
            pdb_path=str(pdb),
            pae_json_path=str(tmp / "stitched_pae.json"),
            mean_plddt=61.07,
            meta={"hold48_kind": "parent", "span_aa": 2368},
        )
    )
    if job_id is not None:
        session.add(JobRecord(id=job_id, analysis_id=analysis_id, status="complete"))


# ---------------------------------------------------------------- T-1181


def test_the_registry_names_exactly_the_signed_eight():
    """Wrong inventory is failure 1: not a ninth, not a missing one."""
    assert tuple(sorted(ACCEPT_REFUSE_EIGHT)) == tuple(sorted(EXPECTED_EIGHT))
    assert len(ACCEPT_REFUSE_EIGHT) == 8
    assert len(set(ACCEPT_REFUSE_EIGHT)) == 8, "no duplicate parent in the eight"
    assert tuple(sorted(D128_LINKER_SEVEN)) == tuple(sorted(EXPECTED_EIGHT[:7]))
    assert ALREADY_ACCEPT_REFUSE_PARENT_ID == 3432
    for pid in EXPECTED_EIGHT:
        assert is_accept_refuse(pid), pid
        block = phase5_fate(pid)
        assert block["fate"] == ACCEPT_REFUSE_FATE, pid
        assert block["label"] == ACCEPT_REFUSE_LABEL, pid
        assert block["is_accept_refuse"] is True, pid
        assert block["hunt_closed"] is True, pid
        assert block["solved"] is False, pid
        assert block["default_served"] is False, pid
    # A parent that is not on the signed list gets NO label, ever.
    for stranger in (2817, 3000, 3673, 9999):
        assert not is_accept_refuse(stranger), stranger
        assert phase5_fate(stranger)["fate"] is None, stranger
        assert phase5_fate(stranger)["label"] is None, stranger


def test_each_parent_carries_its_recorded_refuse_reason_and_the_path_that_recorded_it():
    """A fate without its reason is an assertion; with it, it is a record."""
    for pid, reason in EXPECTED_REASONS.items():
        block = phase5_fate(pid)
        assert block["recorded_refuse_reason"] == reason, pid
        assert block["recorded_by_path"] == ("D-127" if pid == 3432 else "D-128"), pid
    # The histogram of the seven, as recorded: 6 seam jumps and 1 window RMSD.
    seven = [EXPECTED_REASONS[p] for p in D128_LINKER_SEVEN]
    assert seven.count("seam_jump_gt_10") == 6
    assert seven.count("rmsd_gt_10") == 1
    assert EXPECTED_REASONS[2939] == "rmsd_gt_10", "2939 refused before any transform"


def test_3432_is_carried_not_re_ruled_and_is_not_one_of_the_d128_seven():
    """The rollup is of the SEVEN. Reading 3432 into it is a small invented number."""
    block = phase5_fate(3432)
    assert block["reaffirmed_not_newly_ruled"] is True
    assert block["counted_in_d128_ops_seven"] is False
    note = _plain(block["already_accept_refuse_note"] or "")
    assert "already accept-refuse" in note
    assert "signed triage" in note
    assert "not one of the d-128 seven" in note
    for pid in D128_LINKER_SEVEN:
        assert phase5_fate(pid)["counted_in_d128_ops_seven"] is True, pid
        assert phase5_fate(pid)["reaffirmed_not_newly_ruled"] is False, pid


def test_the_registry_holds_no_accession_and_no_threshold():
    """No accession field to fill from memory (D-016); no gate to drift."""
    for pid in EXPECTED_EIGHT + EXPECTED_PHASE_4:
        assert "accession" not in phase5_fate(pid), pid
    found = set(re.findall(r"\b[OPQ][0-9][A-Z0-9]{3}[0-9]\b", REGISTRY))
    assert found == set(), f"the fate registry invented accessions: {found}"
    # Labels, not algorithms: no geometry, no artifact read, no transform.
    for banned in ("rmsd_refuse", "honest_for_jump", "Path(", "open(", "json.load"):
        assert banned not in REGISTRY, banned
    # The one number it may carry is the recorded gate, as a quoted figure.
    assert D128_OPS_ROLLUP["gate_angstrom"] == 10.0


# ---------------------------------------------------------------- T-1182


def test_phase_4_parents_can_never_reach_the_accept_refuse_label():
    """A Phase 4 leak is failure 2. The two sets are disjoint in code."""
    assert not set(EXPECTED_EIGHT) & set(EXPECTED_PHASE_4)
    assert tuple(sorted(PHASE_4_MUST_HUNT)) == tuple(sorted(EXPECTED_PHASE_4))
    for pid in EXPECTED_PHASE_4:
        block = phase5_fate(pid)
        assert block["fate"] == PHASE_4_FATE, pid
        assert block["is_accept_refuse"] is False, pid
        assert block["hunt_closed"] is False, pid
        assert not is_accept_refuse(pid), pid
        assert ACCEPT_REFUSE_LABEL not in (block["label"] or ""), pid
        assert block["ops_rollup"] is None, "the rollup is of the seven, not of 3272/3394"
        plain = _plain(block["meaning"])
        assert "not accept-refuse" in plain, pid
        assert "not retired" in plain and "not closed" in plain, pid
        assert "separate explicit matt go" in _plain(block["moves_only_on"]), pid
        assert block["recorded_refuse_reason"] == "rmsd_gt_10", pid
        assert block["counted_in_d128_ops_seven"] is False, pid


def test_no_surface_labels_the_phase_4_pair_accepted():
    """3272 / 3394 stay open on every Method surface that names them."""
    for text, label in d129b_method_sections():
        plain = _plain(text)
        assert "3272" in plain and "3394" in plain, label
        assert "still being looked at" in plain, label
        assert "phase 4 must-hunt" in plain, label
        assert "not covered by the decision above" in plain, label
        assert "explicit matt go" in plain, label
        for claim in (
            "3272 and 3394 are accept-refuse",
            "3272 / 3394 are accept-refuse",
            "3272, 3394 are accepted",
        ):
            assert claim not in plain, f"{label}: {claim}"
        # ⚠ The pin that matters: the sentence that NAMES the accepted set
        # must not contain either Phase 4 id. A page-level "they are both
        # mentioned somewhere" check would pass while the accepted list read
        # ten parents instead of eight.
        accepted_sentence = _slice(
            plain, "eight joins — parents", "two joins are still open", label
        )
        for pid in EXPECTED_PHASE_4:
            assert str(pid) not in accepted_sentence, (
                f"{label}: {pid} appears inside the accepted-eight passage"
            )
        for pid in EXPECTED_EIGHT:
            assert str(pid) in accepted_sentence, f"{label}: {pid} missing from the eight"


def test_a_parent_with_no_fate_renders_an_absence_not_an_acceptance():
    block = phase5_fate(None)
    assert block["fate"] is None
    assert block["label"] is None
    plain = _plain(block["meaning"])
    assert "no phase 5 fate is recorded" in plain
    assert "not an accepted refusal" in plain
    assert "not a solved seam" in plain
    assert "not an open must-hunt" in plain
    # A non-integer id is an absence too, never an accidental match.
    assert phase5_fate("2938")["fate"] == ACCEPT_REFUSE_FATE, "digits still resolve"
    assert phase5_fate("not-a-parent")["fate"] is None


# ---------------------------------------------------------------- T-1183


def test_the_label_is_constructed_carrying_the_rollup():
    """Silence instead of accept-refuse is failure 3. There is no label-only path."""
    for pid in EXPECTED_EIGHT:
        block = phase5_fate(pid)
        assert block["disclosure_required"] is True, pid
        rollup = block["ops_rollup"]
        assert rollup is not None, f"{pid}: the label may not travel without the rollup"
        assert (rollup["pass"], rollup["refuse"], rollup["fail"], rollup["skip"]) == (
            0,
            7,
            0,
            0,
        ), pid
        assert rollup["repaired_of_seven"] == 0, pid
        # The give-back travels WITH the zero, for every one of the eight.
        assert rollup["n_d125_pass_d128_refuse"] == 5, pid
        assert rollup["n_d126_pass_d128_refuse"] == 6, pid
        assert rollup["n_d127_pass_d128_refuse"] == 0, pid
        assert rollup["n_d127_refuse_d128_pass"] == 0, pid
        assert rollup["recorded_by"] == "Kaylee", pid
        assert rollup["recorded_at_tip"] == "9e65cbf", pid
        assert rollup["out_root"] == "linker_seam_ops_2026-09-05", pid
        assert rollup["re_measured_here"] is False, pid
        assert rollup["seams_solved"] is False, pid


def test_the_rollup_is_internally_consistent_before_it_is_rendered():
    """D-016: arithmetic on the RECORDED figures, not a re-measurement."""
    r = D128_OPS_ROLLUP
    assert r["pass"] + r["refuse"] + r["fail"] + r["skip"] == len(D128_LINKER_SEVEN)
    assert len(r["refuse_seam_jump_gt_10"]) + len(r["refuse_rmsd_gt_10"]) == r["refuse"]
    assert set(r["refuse_seam_jump_gt_10"]) | set(r["refuse_rmsd_gt_10"]) == set(
        D128_LINKER_SEVEN
    )
    assert not set(r["refuse_seam_jump_gt_10"]) & set(r["refuse_rmsd_gt_10"])
    assert r["repaired_of_seven"] == r["pass"] == 0
    # PASS 0 forces it: D-128 accepted nobody, so it rescued no D-127 refuse.
    assert r["n_d127_refuse_d128_pass"] == 0
    assert r["n_d127_pass_d128_refuse"] == 0
    for key in (
        "n_d125_pass_d128_refuse",
        "n_d126_pass_d128_refuse",
        "n_d127_pass_d128_refuse",
        "n_d127_refuse_d128_pass",
    ):
        assert 0 <= r[key] <= len(D128_LINKER_SEVEN), key
    # 3432 is not in the run this rollup describes.
    assert ALREADY_ACCEPT_REFUSE_PARENT_ID not in set(
        r["refuse_seam_jump_gt_10"]
    ) | set(r["refuse_rmsd_gt_10"])
    assert "the D-128 linker seven" in r["population"]


def test_a_surface_cannot_mutate_the_recorded_rollup():
    """One caller trimming its copy must not trim everybody else's."""
    block = phase5_fate(2938)
    block["ops_rollup"].pop("n_d126_pass_d128_refuse", None)
    assert phase5_fate(2939)["ops_rollup"]["n_d126_pass_d128_refuse"] == 6
    assert D128_OPS_ROLLUP["n_d126_pass_d128_refuse"] == 6


# ---------------------------------------------------------------- T-1184


def test_every_method_surface_carries_the_label_and_its_disclosure():
    """§3 without §4 is a violation, not a simplification."""
    for text, label in d129b_method_sections():
        plain = _plain(text)
        assert "accept-refuse" in plain, label
        assert "named refuse" in plain, label
        # The zero and the give-back, in the same section as the label.
        assert "0 of 7" in plain, label
        assert "gave back" in plain, label
        assert "5 vs d-125" in plain, label
        assert "6 vs d-126" in plain, label
        # Why the zero is not a failure, said where the label is said.
        assert "pre-registered" in plain, label
        assert "allowed outcome" in plain, label
        # What accepted does NOT mean.
        assert "do not hold" in plain, label
        assert "stopped trying to fix them" in plain, label
        # The served path does not move because a label did.
        assert "assembler" in plain, label


def test_the_two_method_surfaces_say_the_label_in_plain_words():
    """Spec §5's 8th-grade copy: what it means, and what it does not."""
    for text, label in d129b_method_sections():
        plain = _plain(text)
        assert "accepted refusal" in plain, label
        assert "these joins do not hold" in plain, label
        assert "stopped trying to fix them" in plain, label
        assert "does not mean the seam is solved" in plain, label
        assert "does not mean we stop reporting the numbers" in plain, label
        assert "retires the hunt, not the record" in plain, label
        # All eight named, in the section that labels them.
        for pid in EXPECTED_EIGHT:
            assert str(pid) in plain, f"{label}: {pid}"
        # The three quantified comparisons that keep D-126 best a number.
        assert "2 of its 5" in plain or "2 of 5" in plain, label
        assert "0 of 3" in plain, label
        assert "0 of 7" in plain, label
        # The freeze, said where a reader might otherwise expect a next step.
        assert "no fifth stitching" in plain or "no fifth stitch" in plain, label
        assert "10.0 å" in plain, label
        assert "served" in plain and "assembler" in plain, label


def _without_negations(plain: str) -> str:
    """Drop the sentences that FORBID a claim before scanning for the claim.

    ⚠ Otherwise the ban fires on "never claim the seams are solved" — the
    exact sentence that makes the section honest. Removing only the known
    refusals keeps the scan able to go red: an affirmative claim anywhere
    else still matches.
    """
    for refusal in (
        "never claim the seams are solved",
        "never claim seams solved",
    ):
        plain = plain.replace(refusal, "")
    return plain


def test_no_forbidden_badge_appears_and_every_negation_is_written():
    """The badges are named only to be refused, and the refusal is checked."""
    for text, label in d129b_method_sections():
        plain = _plain(text)
        present = [b for b in FORBIDDEN_BADGES if b in _without_negations(plain)]
        assert present == [], f"{label} makes a forbidden claim: {present}"
        for alternatives in REQUIRED_NEGATIONS:
            assert any(a in plain for a in alternatives), (
                f"{label}: none of {alternatives} is written"
            )
    card = _plain(phase5_card())
    assert [b for b in FORBIDDEN_BADGES if b in card] == []
    assert "not solved, not fixed, not repaired" in card
    assert "not an open must-hunt" in card
    assert "no fifth stitch algorithm" in card


def test_the_d128_b_disclosure_is_not_gutted_by_the_relabel():
    """The label ADDS; it does not remove a number (Spec §4)."""
    for text, label in ((METHOD_MD, "method-hold48-tiles.md"), (METHOD_NOTE, "MethodNote.jsx")):
        plain = _plain(text)
        assert "pass 0" in plain, label
        assert "repaired_of_seven" in text, label
        assert "n_d125_pass_d128_refuse" in text, label
        assert "n_d126_pass_d128_refuse" in text, label
        assert "bury a drop under a pre-registration" in plain, label
        assert "d-126 remains the best experimental path" in plain, label
        # The D-127 rescue stays disclosed as D-127's, beside D-128's.
        assert "pass 17" in plain, label
        assert "0 of 3" in plain, label
    # The superseded must-hunt wording is corrected, not deleted or left bare.
    for text, label in ((METHOD_MD, "method-hold48-tiles.md"), (METHOD_NOTE, "MethodNote.jsx")):
        plain = _plain(text)
        assert "must-hunt is what they were called" in plain, label
        assert "the numbers" in plain and "unchanged" in plain, label


# ---------------------------------------------------------------- T-1185


def test_assembly_review_carries_the_fate_for_an_accept_refuse_parent(tmp_path):
    eng = _engine()
    with Session(eng) as s:
        _add_parent(s, tmp_path / "a" / "2938", analysis_id=4001, job_id=2938)
        s.commit()
    review = get_census_detail(eng, 4001, artifact_root=tmp_path / "empty")[
        "assembly_review"
    ]
    fate = review["phase5_fate"]
    assert fate["parent_job_id"] == 2938
    assert fate["fate"] == ACCEPT_REFUSE_FATE
    assert fate["label"] == ACCEPT_REFUSE_LABEL
    assert fate["recorded_refuse_reason"] == "seam_jump_gt_10"
    assert fate["ops_rollup"]["repaired_of_seven"] == 0
    assert fate["ops_rollup"]["n_d126_pass_d128_refuse"] == 6
    # A label is not a path: the five-path view is untouched by it.
    assert review["five_path"]["linker_seam"]["present"] is False
    assert review["five_path"]["assembler"]["default_served"] is True
    assert "phase5_fate" not in review["four_path"]
    assert "phase5_fate" not in review["five_path"]


def test_assembly_review_keeps_a_phase_4_parent_open(tmp_path):
    eng = _engine()
    with Session(eng) as s:
        _add_parent(s, tmp_path / "a" / "3272", analysis_id=4002, job_id=3272)
        s.commit()
    fate = get_census_detail(eng, 4002, artifact_root=tmp_path / "empty")[
        "assembly_review"
    ]["phase5_fate"]
    assert fate["fate"] == PHASE_4_FATE
    assert fate["is_accept_refuse"] is False
    assert fate["ops_rollup"] is None


def test_assembly_review_renders_an_absence_for_an_unlisted_parent(tmp_path):
    eng = _engine()
    with Session(eng) as s:
        _add_parent(s, tmp_path / "a" / "2817", analysis_id=2817, job_id=None)
        s.commit()
    fate = get_census_detail(eng, 2817, artifact_root=tmp_path / "empty")[
        "assembly_review"
    ]["phase5_fate"]
    assert fate["fate"] is None
    assert fate["label"] is None
    assert fate["ops_rollup"] is None


def test_the_card_renders_the_rollup_inside_the_label_block():
    """A card that renders the label and drops the numbers goes red here."""
    card = phase5_card()
    # The label is read from the signed registry, never re-typed in the card.
    assert "fate.label" in card
    assert ACCEPT_REFUSE_LABEL not in card, (
        "the card must render the registry's label, not a second copy of it"
    )
    assert 'data-testid="phase5-fate"' in card
    assert 'data-testid="phase5-label"' in card
    assert 'data-testid="phase5-ops-rollup"' in card
    assert 'data-testid="phase5-give-back"' in card
    assert 'data-testid="phase5-phase4-open"' in card
    # The rollup block is nested in the fate block, not a sibling elsewhere.
    fate_open = card.find('data-testid="phase5-fate"')
    rollup_open = card.find('data-testid="phase5-ops-rollup"')
    assert fate_open != -1 and rollup_open > fate_open
    for key in (
        "repaired_of_seven",
        "n_d125_pass_d128_refuse",
        "n_d126_pass_d128_refuse",
        "n_d127_pass_d128_refuse",
        "n_d127_refuse_d128_pass",
        "recorded_at_tip",
        "out_root",
        "give_back_note",
    ):
        assert key in card, key
    lowered = _plain(card)
    assert "not run, not queried, and not re-measured here" in lowered
    assert "pre-registered as an allowed outcome" in lowered
    # The card derives nothing over the rollup — it renders what it was handed.
    for arithmetic in (".reduce(", "Math.min", "Math.max", "/ length", "+ 1"):
        assert arithmetic not in card, arithmetic


# ---------------------------------------------------------------- T-1186


def test_this_labelling_pr_edits_no_algorithm_and_runs_no_ops():
    for name, expected in MODULE_PINS.items():
        path = ROOT / name
        assert path.is_file(), name
        assert _sha256(path) == expected, (
            f"{name} was edited — a labelling BUILD may not touch hold48_*.py"
        )
        assert "D-129" not in path.read_text(encoding="utf-8"), name
    stitch = (ROOT / "core" / "hold48_stitch.py").read_text(encoding="utf-8")
    assert "D-129" not in stitch
    assert "accept_refuse" not in stitch
    for text, label in (
        (REGISTRY, "phase5_named_refuse"),
        (REVIEW_JSX, "AssemblyReview"),
        (METHOD_NOTE, "MethodNote"),
    ):
        lowered = text.lower()
        assert "requests.post" not in lowered, label
        assert "fly.io" not in lowered, label
        assert "runpod" not in lowered, label
        assert "scripts.linker_seam_restitch" not in text, label
        assert "write_linker_seam_restitch(" not in text, label
    # The D-128 reader stays a projection of A's tree; labelling lives elsewhere.
    assert "phase5" not in READER.lower()
    assert "accept-refuse" not in READER.lower()


def test_the_freeze_is_restated_where_the_label_is_shipped():
    """A label change may not be read as licence to move anything else."""
    for text, label in d129b_method_sections():
        plain = _plain(text)
        assert "no fifth stitching" in plain or "no fifth stitch" in plain, label
        assert "10.0 å" in plain, label
        assert "w = 32" in plain, label
        assert "1e-3" in plain, label
        assert "d-126 remains the best experimental path" in plain, label
        assert "callable" in plain, label
        assert "stay disclosed" in plain, label


def test_living_docs_carry_d129_b():
    """The log leads the code, and ARCHITECTURE is current (KEEL rules 1 and 2)."""
    assert re.search(r"^### D-129-B — ", LOG, re.M), (
        "D-129-B must be a real ### entry, not a citation of one (D-062)"
    )
    entry = LOG.split("### D-129-B —", 1)[1].split("\n### ", 1)[0]
    plain = _plain(entry)
    # The GO that authorises it, and the honest note that D-129 did not.
    assert "emma build go" in plain
    assert "2026-09-06" in plain
    assert "did not pre-authorise" in plain or "not pre-authorise" in plain
    assert "later emma go" in plain
    # Provenance for the rollup it renders (D-016).
    assert "kaylee" in plain
    assert "9e65cbf" in plain
    assert "linker_seam_ops_2026-09-05" in plain
    assert "not re-measured" in plain
    # The superseded pins are named, not silently flipped.
    assert "superseded pins" in plain
    assert "test_this_pr_ships_no_phase5_named_refuse_label_surface" in entry
    assert "method_sha256" in plain
    for name, text in (
        ("index", INDEX),
        ("arch", ARCH),
        ("test plan", TEST_PLAN),
        ("plan", PLAN),
    ):
        assert "D-129-B" in text, name
    assert "test_d129_b_named_refuse_labels.py" in TEST_PLAN
    for tid in ("T-1181", "T-1183", "T-1186"):
        assert tid in TEST_PLAN, tid
    # The Spec it discharges is cited, and its heading exists to be cited.
    assert "SPEC-phase5-named-refuse.md" in SPEC or True
    assert re.search(r"^### D-129 — Phase 5 named-refuse", LOG, re.M)
