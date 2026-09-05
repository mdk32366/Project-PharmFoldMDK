"""D-126 — Overlap-confidence Kabsch Spec. These must be able to go red.

Spec GO: the living-log heading exists, the Spec file exists, the
algorithm name and 10.0 Å refuse gate are pinned, the primary five are
named, hard stops are written, D-126-B is not this PR, and
``hold48_kabsch.py`` is not edited (D-126-A is a sibling module).

Amendment 1 (same D-id) additionally pins: full-overlap RMSD + max Cα
jump; ε = 1e-3 and the weighted RMSD formula; floor-then-Kabsch-then-trim;
all-or-nothing parent refuse; ops confusion vs D-125; 0-of-5 allowed.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
SPEC_PATH = ROOT / "docs" / "SPEC-overlap-confidence-kabsch.md"
SPEC = SPEC_PATH.read_text(encoding="utf-8")
INDEX = (ROOT / "docs" / "decisions.md").read_text(encoding="utf-8")
PLAN = (ROOT / "docs" / "PLAN-ui-post-wave2-endstate.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
STITCH = (ROOT / "core" / "hold48_stitch.py").read_text(encoding="utf-8")
KABSCH_PATH = ROOT / "core" / "hold48_kabsch.py"
KABSCH = KABSCH_PATH.read_text(encoding="utf-8")

# Primary five D-125 REFUSE parents — not a Fly query, not a named-exclusion.
PRIMARY_FIVE = (
    (2939, "Q7Z408"),
    (3272, "Q6V0I7"),
    (3368, "Q5SZK8"),
    (3394, "Q8TDW7"),
    (3432, "Q8IZF6"),
)

# D-125-A module on main (`26a40a8`, unchanged at D-125-B `aa8d3f1`
# and through D-126 Spec + A). D-126-A is a sibling module — this pin
# must stay. If it moves, hold48_kabsch.py was edited.
D125_KABSCH_SHA256 = "4c7bb45d04507e2a67ba3600b35d6130d62843ca3bc99c15d3568d5cb105ff6e"


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def test_d126_heading_exists_in_the_living_log():
    """The check is the heading, not a citation of it (D-062 / method-note 7)."""
    assert re.search(
        r"^### D-126 — Overlap-confidence Kabsch Spec",
        LOG,
        re.M,
    ), "D-126 must be a real ### entry, not a citation of one"
    assert re.search(
        r"^#### D-126 amendment 1 — Trinity red-team pins",
        LOG,
        re.M,
    ), "amendment 1 must be a real #### sub-entry under D-126, not a new D-NNN"
    assert re.search(r"^### D-125 — Kabsch restitch Spec", LOG, re.M)
    assert re.search(r"^### D-125-B — UI dual-path honesty", LOG, re.M)
    assert re.search(
        r"^### D-126-A — Overlap-confidence Kabsch core",
        LOG,
        re.M,
    ), "D-126-A must be a real ### entry, not a citation of one"
    assert re.search(
        r"^### D-127 — Piecewise / domain-aware Kabsch Spec",
        LOG,
        re.M,
    ), "D-127 is the later piecewise Spec; do not treat D-126 amend as forbidding it"


def test_spec_file_exists_and_names_algorithm():
    assert SPEC_PATH.is_file()
    assert "overlap_confidence_kabsch_then_winning_tile" in SPEC
    flat = _flat(SPEC).lower()
    assert "overlap-confidence kabsch" in flat
    assert "winning_tile" in SPEC
    assert "must **not replace**" in SPEC or "not replace" in flat
    assert "seams are not scientifically solved" in flat
    assert "plddt-weighted" in flat or "pLDDT-weighted" in SPEC
    assert "trim" in flat


def test_refuse_gate_stays_at_10():
    """10.0 Å STAYS. Trim/weight change the fit set, not the gate."""
    assert "10.0" in SPEC
    assert "10 Å STAYS" in SPEC or "10.0 Å" in SPEC
    assert "overlap_ca_lt_3" in SPEC
    assert "rmsd_gt_10" in SPEC
    assert "singular_covariance" in SPEC
    assert "< 3" in SPEC or "`< 3`" in SPEC
    assert "fit set" in _flat(SPEC).lower()
    assert "not the gate" in _flat(SPEC).lower() or "not gate" in _flat(SPEC).lower()


def test_primary_five_inventory():
    assert len(PRIMARY_FIVE) == 5
    for pid, acc in PRIMARY_FIVE:
        assert str(pid) in SPEC, pid
        assert acc in SPEC, acc
        assert str(pid) in LOG, pid
        assert acc in LOG, acc
    assert "3356" in SPEC  # named as out
    assert "IGF2R" in SPEC
    assert "11.45" in SPEC and "29.54" in SPEC
    assert "F-004" in SPEC


def test_hard_stops_and_not_ab():
    flat = _flat(SPEC).lower()
    log_flat = _flat(LOG).lower()
    assert "no threshold spec-as-fix" in flat
    assert "no named-exclusion-as-fix" in flat
    assert "no invented" in flat or "no invent" in flat
    assert "never 0" in SPEC
    assert "no f-004" in flat
    assert "no rent in a" in flat
    assert "never seams solved" in flat or "seams are not scientifically solved" in flat
    assert "keep assembler" in flat and "d-125" in flat
    assert "not d-126-b" in flat or "**not d-126-b**" in flat
    assert "docs spec only" in log_flat or "docs only" in log_flat
    assert "not d-126-b" in log_flat
    # Spec file remains algorithm authority; A is a sibling module, not a
    # replacement of hold48_kabsch.py / winning_tile.
    assert "hold48_confidence_kabsch.py" in SPEC or "sibling" in flat


def test_ship_index_distinguishes_spec_from_ab_build():
    assert "D-126 ships the overlap-confidence Kabsch Spec" in INDEX
    assert "D-126-A already shipped" in INDEX
    assert "Yes — this PR." in INDEX
    assert re.search(r"D-126 Spec.*Already shipped on `main`", _flat(INDEX))
    assert re.search(r"D-126-A.*Already shipped on `main`", _flat(INDEX))
    assert re.search(r"D-126-B.*Already shipped on `main`", _flat(INDEX))
    assert "confidence_kabsch" in INDEX or "overlap-confidence" in INDEX.lower()


def test_plan_and_architecture_point_at_d126():
    assert "Kabsch park → **D-125**" in PLAN
    assert "**D-126**" in PLAN
    assert "SPEC-overlap-confidence-kabsch.md" in PLAN
    assert "D-126 ships" in ARCH or "D-126:" in ARCH
    assert "SPEC-overlap-confidence-kabsch.md" in ARCH
    assert "D-125 Kabsch + assembler remain" in ARCH or "assembler remain" in ARCH.lower()


def test_this_spec_pr_does_not_edit_hold48_kabsch_or_the_assembler():
    """Hard stop: D-126-A is a sibling module. hold48_kabsch.py bytes stay pinned."""
    assert "def winning_tile" in STITCH
    assert "def kabsch" not in STITCH
    assert "overlap_confidence_kabsch" not in KABSCH
    assert "confidence_kabsch" not in KABSCH
    assert "D-126" not in KABSCH
    assert "def fit_overlap_kabsch" in KABSCH
    assert hashlib.sha256(KABSCH_PATH.read_bytes()).hexdigest() == D125_KABSCH_SHA256
    sibling = ROOT / "core" / "hold48_confidence_kabsch.py"
    assert sibling.is_file()
    sib = sibling.read_text(encoding="utf-8")
    assert "overlap_confidence_kabsch_then_winning_tile" in sib
    assert "def write_confidence_kabsch_restitch" in sib
    assert "import numpy" not in sib
    assert "from numpy" not in sib


def test_post_transform_full_overlap_disclosure():
    """Anti trim-to-pass lie: full-overlap unweighted RMSD + max Cα jump."""
    assert "rmsd_full_overlap_angstrom" in SPEC
    assert "max_ca_jump_angstrom" in SPEC
    assert "rmsd_full_overlap_angstrom" in LOG
    assert "max_ca_jump_angstrom" in LOG
    flat = _flat(SPEC).lower()
    assert "unweighted" in flat
    assert "all overlap" in flat or "all** overlap" in SPEC.lower() or "**all** overlap" in SPEC
    assert "not only the trimmed fit set" in flat
    assert "refuse-before-transform" in flat
    assert "may be null" in flat
    assert "a must write them" in flat
    assert "b later shows them" in flat or "ui / b later shows them" in flat
    # Gate stays weighted-on-fit-set, not full-overlap.
    assert "weighted" in flat and "fit set" in flat
    assert "≤ 10.0" in SPEC or "`≤ 10.0 Å`" in SPEC


def test_epsilon_and_weighted_rmsd_formula():
    """ε = 1e-3; weighted RMSD = sqrt(Σ w_i ||R p_i + t − q_i||² / Σ w_i)."""
    sec1 = SPEC.split("## 2.")[0]
    assert "1e-3" in sec1
    assert "1e-3" in LOG
    assert "R p_i + t" in sec1
    assert "q_i" in sec1
    assert "w_i" in sec1
    # Formula is a weighted root-mean-square on the current fit set.
    assert "sqrt" in sec1.lower() or r"\sqrt" in sec1
    assert "fit set" in _flat(sec1).lower()
    assert "weight floor" in _flat(sec1).lower() or r"\varepsilon" in sec1


def test_floor_then_weighted_kabsch_then_trim_order():
    """(a) pLDDT floor 50 first if n≥3 remains; (b) weighted Kabsch; (c) trim loop."""
    sec1 = SPEC.split("## 2.")[0]
    a = sec1.find("(a) pLDDT floor")
    b = sec1.find("(b) weighted Kabsch")
    c = sec1.find("(c) trim loop")
    assert a != -1 and b != -1 and c != -1, "Spec §1 must label (a)/(b)/(c) in that wording"
    assert a < b < c
    assert "50" in sec1[a:b]
    assert "n \\ge 3" in sec1 or r"n \ge 3" in sec1 or "n ≥ 3" in sec1
    assert "fixed, not optional-in-time" in sec1
    assert "post-trim" not in sec1.lower()
    assert "(a) pLDDT floor 50 first" in LOG
    assert "(b) weighted Kabsch" in LOG
    assert "(c) trim loop" in LOG


def test_all_or_nothing_parent_refuse():
    """If any seam refuses, parent is refused; no partial D-126 success artifacts."""
    flat = _flat(SPEC).lower()
    log_flat = _flat(LOG).lower()
    assert "all-or-nothing" in flat
    assert "all-or-nothing" in log_flat
    assert "if any seam refuses" in flat
    assert "parent outcome" in flat and "refused" in flat
    assert "_clear_success_artifacts" in SPEC
    assert "_clear_success_artifacts" in LOG
    assert "tileN_transformed.pdb" in SPEC or "tile{n}_transformed.pdb" in SPEC
    assert "stitched.pdb" in SPEC
    assert "partial" in flat
    assert "seam rows still recorded" in flat or "seam rows are still recorded" in flat


def test_no_regress_ops_report_fields():
    """Ops report must name D-125 PASS → D-126 REFUSE; not a CI assert on live ops."""
    assert "n_d125_pass_d126_refuse" in SPEC
    assert "n_d125_pass_d126_pass" in SPEC
    assert "n_d125_refuse_d126_pass" in SPEC
    assert "n_d125_refuse_d126_refuse" in SPEC
    assert "recovered_of_primary_five" in SPEC
    assert "n_d125_pass_d126_refuse" in LOG
    flat = _flat(SPEC).lower()
    assert "named finding" in flat
    assert "not silent success" in flat or "not silent success" in _flat(LOG).lower()
    assert "not a ci assert" in flat
    assert "confusion vs d-125" in flat
    assert "## 10." in SPEC


def test_zero_of_five_recovered_is_allowed():
    """Recovering zero of the primary five is a valid experimental result."""
    flat = _flat(SPEC).lower()
    log_flat = _flat(LOG).lower()
    assert "0-of-5" in SPEC or "0-of-5" in LOG
    assert "allowed outcome" in flat
    assert "allowed outcome" in log_flat
    assert "valid experimental result" in flat
    assert "do not loosen" in flat
    assert "blend" in flat
    assert "force passes" in flat
    assert "recovered_of_primary_five" in SPEC
