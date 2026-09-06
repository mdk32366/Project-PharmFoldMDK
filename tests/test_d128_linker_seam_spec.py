"""D-128 — Linker / seam honesty Spec. These must be able to go red.

Spec GO: the living-log heading exists, the Spec file exists, the goal
framing is *diagnose and refuse dishonest seams* (never solved), the §1a
per-path / per-seam honesty metric is required with 10.0 Å as the
dishonesty line, §1b's linker-local rigid is pinned (W = 32, ε = 1e-3, no
trim loop, no pieces, no linker-inherit), the seven signed must-hunt
linker parents are the primary inventory, 3432 stays accept-refuse,
3272 / 3394 are out of primary, hard stops are written, D-128-A/B are not
this PR, and ``hold48_*.py`` is not edited.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
SPEC_PATH = ROOT / "docs" / "SPEC-linker-seam-honesty.md"
SPEC = SPEC_PATH.read_text(encoding="utf-8")
INDEX = (ROOT / "docs" / "decisions.md").read_text(encoding="utf-8")
PLAN = (ROOT / "docs" / "PLAN-ui-post-wave2-endstate.md").read_text(encoding="utf-8")
TEST_PLAN = (ROOT / "docs" / "Test_Plan.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
STITCH = (ROOT / "core" / "hold48_stitch.py").read_text(encoding="utf-8")
KABSCH_PATH = ROOT / "core" / "hold48_kabsch.py"
KABSCH = KABSCH_PATH.read_text(encoding="utf-8")
CONF_PATH = ROOT / "core" / "hold48_confidence_kabsch.py"
CONF = CONF_PATH.read_text(encoding="utf-8")
PIECEWISE_PATH = ROOT / "core" / "hold48_piecewise_kabsch.py"
PIECEWISE = PIECEWISE_PATH.read_text(encoding="utf-8")

# The seven signed must-hunt linker parents: the D-127 OPS
# `linker_jump_gt_10` class, as recorded (Matt GO via Emma 2026-09-05 at tip
# `e49bf34`). ⚠ Not a Fly query, not re-measured, not a named-exclusion.
SEVEN_LINKER_PARENT_IDS = (2938, 2939, 3179, 3190, 3321, 3368, 3566)

# Accessions this log already carries for two of the seven. The other five are
# NOT on record — the Spec says so instead of inventing one (D-016).
RECORDED_ACCESSIONS = {2939: "Q7Z408", 3368: "Q5SZK8"}
UNRECORDED_ACCESSION_PARENT_IDS = (2938, 3179, 3190, 3321, 3566)

# Out of the primary inventory: other failure classes, not success targets.
OUT_OF_PRIMARY = {
    3272: ("Q6V0I7", "rmsd_gt_10"),
    3394: ("Q8TDW7", "rmsd_gt_10"),
    3432: ("Q8IZF6", "no_domain_pieces"),
}

# Modules on main at `de9a80e`. Must stay byte-identical: a moved hash means a
# `hold48_*.py` was edited (forbidden in this Spec PR).
D125_KABSCH_SHA256 = "4c7bb45d04507e2a67ba3600b35d6130d62843ca3bc99c15d3568d5cb105ff6e"
D126_CONF_SHA256 = "d526a856ec8f1ba978a3586f3dfcf4a0ee858da12132499f2db37368efc77f18"
D127_PIECEWISE_SHA256 = "ad48b2be577b987466274000c508a621792bc029bb9e087eec94ba7237f13e04"


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def _section(number: str, following: str) -> str:
    return SPEC.split(f"## {number}")[1].split(f"## {following}")[0]


def test_d128_heading_exists_in_the_living_log():
    """The check is the heading, not a citation of it (D-062 / method-note 7)."""
    assert re.search(
        r"^### D-128 — Linker / seam honesty Spec",
        LOG,
        re.M,
    ), "D-128 must be a real ### entry, not a citation of one"
    # The train it follows must still be real entries too.
    assert re.search(r"^### D-127 — Piecewise / domain-aware Kabsch Spec", LOG, re.M)
    assert re.search(r"^### D-127-A — Piecewise / domain-aware Kabsch core", LOG, re.M)
    assert re.search(r"^### D-127-B — UI four-path honesty", LOG, re.M)
    assert re.search(r"^### D-126 — Overlap-confidence Kabsch Spec", LOG, re.M)
    assert re.search(r"^### D-125 — Kabsch restitch Spec", LOG, re.M)
    assert re.search(
        r"^### D-128-A — Linker / seam honesty core",
        LOG,
        re.M,
    ), "D-128-A must be a real ### entry, not a citation of one"
    log_flat = _flat(LOG).lower()
    assert "docs spec only" in log_flat or "docs only" in log_flat
    assert "not d-128-a" in log_flat
    assert "not d-128-b" in log_flat
    # The Matt Phase 3 hard bar is bound in the log, not merely referenced.
    assert "phase 3" in log_flat
    assert "d-0043" in log_flat
    assert "single failure mode" in log_flat
    assert "hold48_*.py" in LOG


def test_spec_file_exists_and_names_algorithm_and_goal_framing():
    assert SPEC_PATH.is_file()
    assert "linker_local_kabsch_then_winning_tile" in SPEC
    assert "`decision`: `D-128`" in SPEC or "decision=`D-128`" in SPEC
    assert "winning_tile" in SPEC
    flat = _flat(SPEC).lower()
    # §1 goal framing, bound by Matt: diagnose and refuse dishonest seams.
    assert "diagnose and refuse dishonest seams" in flat
    assert "linker-local rigid" in flat
    assert "not a rebrand of d-127" in flat
    log_flat = _flat(LOG).lower()
    assert "diagnose and refuse dishonest seams" in log_flat
    assert "linker_local_kabsch_then_winning_tile" in LOG


def test_spec_never_says_seams_are_solved():
    """Method must never say solved. The Spec is the authority that binds it."""
    flat = _flat(SPEC).lower()
    assert "never seams solved" in flat or "never claim seams solved" in flat
    assert "never says solved" in flat
    assert "seams are not scientifically solved" in flat
    assert "recorded" in flat
    for banned in (
        "the seams are solved",
        "seams are now solved",
        "we solved the seam",
        "the seam is repaired",
        "full-length af-quality structure",
    ):
        assert banned not in flat, banned
    # Where "solved" appears at all, it is negated — spot-check the two forms.
    assert "not “the seam is solved.”" in _flat(SPEC)
    assert "is not a seam that is" in flat
    # Forbidden-language park is carried, not dropped.
    for parked in ("aligned", "superimposed", "seams solved", "seams fixed"):
        assert parked in flat, parked


def test_seam_honesty_metrics_are_required_per_path_per_seam():
    """§1a is the required half: measure every path's seam jump."""
    sec = _section("1a.", "1b.")
    assert "max_ca_jump_angstrom" in sec
    assert "linker_n" in sec
    assert "max_linker_ca_jump" in sec
    assert "seam_honesty" in SPEC
    for path in ("kabsch/", "confidence_kabsch/", "piecewise_kabsch/", "linker_seam/"):
        assert path in sec, path
    flat = _flat(sec).lower()
    assert "required" in flat
    assert "per seam" in flat
    assert "10.0" in sec
    assert "honest" in flat
    # Null is not zero; unknown is not honest.
    assert "null is not" in flat or "null is not `0.0`" in flat
    assert "unknown is not honest" in flat
    # Prior trees are read, never rewritten.
    assert "reading" in flat or "read" in flat
    assert "never rewritten" in flat or "must **not** rewrite" in sec
    assert "max_ca_jump_angstrom" in LOG


def test_dishonest_seam_is_fail_closed_and_no_success_pdb_is_honest():
    """> 10.0 Å at a seam = dishonest for that seam; nothing is presented as honest."""
    sec = _section("1a.", "1b.")
    flat = _flat(sec).lower()
    assert "dishonest" in flat
    assert "fail-closed" in flat or "fail closed" in flat
    assert "no success pdb" in flat
    assert "presented as honest" in flat
    log_flat = _flat(LOG).lower()
    assert "dishonest" in log_flat
    assert "no success pdb is presented as honest" in log_flat
    # A refuse is still a recorded outcome, not a dropped parent.
    assert "recorded outcome" in flat


def test_refuse_gate_stays_at_10_and_does_not_loosen():
    """10.0 Å STAYS. No RMSD / linker threshold loosen without Matt."""
    assert "10.0" in SPEC
    flat = _flat(SPEC).lower()
    assert "10.0 å stays" in flat or "10 å stays" in flat
    assert "do not raise" in flat
    assert "loosen" in flat
    assert "without matt" in flat
    assert "no threshold spec-as-fix" in flat
    log_flat = _flat(LOG).lower()
    assert "10.0 å stays" in log_flat
    assert "without matt" in log_flat


def test_refuse_table_names_the_four_reasons_and_all_or_nothing():
    sec = _section("2.", "3.")
    for reason in (
        "overlap_ca_lt_3",
        "rmsd_gt_10",
        "singular_covariance",
        "seam_jump_gt_10",
    ):
        assert reason in sec, reason
        assert reason in SPEC, reason
    assert "< 3" in sec or "`< 3`" in sec
    assert "10.0" in sec
    flat = _flat(sec).lower()
    assert "all-or-nothing" in flat
    assert "_clear_success_artifacts" in sec
    # seam_jump_gt_10 is a new name, not a rename of D-127's linker reason.
    assert "linker_jump_gt_10" in sec
    assert "must not be conflated" in flat or "not a renamed" in flat
    for reason in ("overlap_ca_lt_3", "rmsd_gt_10", "singular_covariance", "seam_jump_gt_10"):
        assert reason in LOG, reason


def test_window_half_width_is_pinned_at_32():
    """W = 32 is a pinned v1 default; A tests must be able to go red on it."""
    sec = _section("1b.", "2.")
    assert "W = 32" in sec or "**W = 32**" in sec
    assert "±32 aa" in sec
    assert "window_half_width_aa" in SPEC
    flat = _flat(sec).lower()
    assert "pinned" in flat
    assert "go red" in flat
    assert "32" in LOG
    assert "w = 32" in _flat(LOG).lower()
    # Not a knob to tune until a parent passes.
    assert "until a parent passes" in _flat(SPEC).lower()


def test_no_trim_loop_and_epsilon_and_weight_rule():
    """No trim loop (D-126 lie surface). ε = 1e-3. One weighted Kabsch."""
    sec = _section("1b.", "2.")
    assert "1e-3" in sec
    assert "1e-3" in LOG
    assert "NO trim loop" in SPEC or "No trim loop" in SPEC
    assert "no trim loop" in _flat(SPEC).lower()
    assert "D-126 lie surface" in SPEC
    assert "w_i" in sec
    assert "min(" in sec or r"\min" in sec
    assert "R p_i + t" in sec
    assert "q_i" in sec
    assert "svd" in _flat(sec).lower()
    # §1b must not authorise a trim loop or a piece list as a step.
    assert "trim loop" in _flat(sec).lower()
    assert "cap **5** rounds" not in sec
    assert "(c) trim loop" not in sec


def test_accept_feeds_existing_winning_tile_and_pae_stays_null():
    sec = _section("1b.", "2.")
    assert "winning_tile" in sec
    assert "write_stitched" in sec
    flat = _flat(sec).lower()
    assert "null, never 0" in flat
    assert "never 0" in SPEC
    assert "all-or-nothing" in flat
    assert "clear" in flat
    # Only the window's atoms move.
    assert "only to moving-tile atoms in that window" in flat


def test_seven_signed_linker_parents_are_the_primary_inventory():
    """Single failure mode: the linker / seam class, seven parents."""
    assert len(SEVEN_LINKER_PARENT_IDS) == 7
    sec = _section("3.", "4.")
    for pid in SEVEN_LINKER_PARENT_IDS:
        assert str(pid) in sec, pid
        assert str(pid) in SPEC, pid
        assert str(pid) in LOG, pid
    for pid, acc in RECORDED_ACCESSIONS.items():
        assert acc in SPEC, acc
        assert acc in LOG, acc
        assert str(pid) in SPEC, pid
    flat = _flat(SPEC).lower()
    assert "seven" in flat
    assert "primary evaluation" in flat
    assert "linker_jump_gt_10" in SPEC
    assert "must-hunt" in flat
    # A CLI may run the 27, but the other parents are not success targets.
    assert "27" in sec
    assert "success target" in flat
    assert "3356" in SPEC  # IGF2R named as out
    assert "IGF2R" in SPEC
    assert "F-004" in SPEC


def test_zero_of_seven_repaired_is_allowed():
    """Repairing zero of the seven is a valid experimental result."""
    flat = _flat(SPEC).lower()
    log_flat = _flat(LOG).lower()
    assert "0-of-7" in SPEC
    assert "0-of-7" in LOG
    assert "allowed outcome" in flat
    assert "allowed outcome" in log_flat
    assert "valid experimental result" in flat
    assert "do not loosen" in flat
    assert "blend" in flat
    assert "repaired_of_seven" in SPEC


def test_not_piecewise_v2_not_rmsd_spec_not_domain_spec():
    """Matt's fences: one failure mode only, and no bleed into the others."""
    flat = _flat(SPEC).lower()
    log_flat = _flat(LOG).lower()
    assert "not piecewise-v2" in flat
    assert "no piecewise-v2" in flat
    assert "not an rmsd spec" in flat
    assert "not a domain spec" in flat
    assert "not piecewise-v2" in log_flat
    assert "not an rmsd spec" in log_flat
    assert "not a domain spec" in log_flat
    # The specific mechanics that would make it D-127 again.
    assert "linker-inherit" in flat
    assert "no pieces" in flat or "no per-domain pieces" in flat
    # 3272 / 3394 are the RMSD class and are out of primary.
    for pid in (3272, 3394):
        acc, reason = OUT_OF_PRIMARY[pid]
        assert str(pid) in SPEC, pid
        assert acc in SPEC, acc
        assert reason in SPEC, reason
        assert str(pid) in LOG, pid
    assert "out of the primary inventory" in flat or "out of primary" in flat


def test_3432_stays_accept_refuse():
    """Signed triage: 3432 is not re-opened and is not a success target."""
    acc, reason = OUT_OF_PRIMARY[3432]
    assert "3432" in SPEC
    assert acc in SPEC
    assert reason in SPEC
    assert "3432" in LOG
    flat = _flat(SPEC).lower()
    log_flat = _flat(LOG).lower()
    assert "accept-refuse" in flat
    assert "accept-refuse" in log_flat
    assert "signed triage" in flat
    assert "signed triage" in log_flat
    assert "not re-opened" in flat or "not **re-opened**" in flat
    assert "reclassified" in flat
    assert "accept-refuse" in INDEX


def test_no_invented_accessions_for_unrecorded_parents():
    """D-016: name the artefact or say it is not on record. Never invent one."""
    flat = _flat(SPEC).lower()
    assert "not recorded in this log" in flat
    assert "do not invent" in flat
    log_flat = _flat(LOG).lower()
    assert "not recorded in this log" in log_flat
    # The five unrecorded parents are named as ids without an accession claim.
    for pid in UNRECORDED_ACCESSION_PARENT_IDS:
        assert str(pid) in SPEC, pid
    # Only the two on-record accessions of the seven appear.
    uniprot_like = set(re.findall(r"\b[OPQ][0-9][A-Z0-9]{3}[0-9]\b", SPEC))
    allowed = set(RECORDED_ACCESSIONS.values()) | {
        acc for acc, _ in OUT_OF_PRIMARY.values()
    } | {"Q9P273"}
    assert uniprot_like <= allowed, uniprot_like - allowed


def test_artifact_dir_is_sibling_linker_seam():
    assert "linker_seam/" in SPEC
    assert "linker_seam/{parent_id}" in SPEC
    assert "seams.jsonl" in SPEC
    assert "seam_honesty.jsonl" in SPEC
    assert "linker_local_kabsch_then_winning_tile" in SPEC
    assert "`decision`: `D-128`" in SPEC or "decision=`D-128`" in SPEC
    assert "offending_seam_source" in SPEC
    assert "window_half_width_aa" in SPEC
    flat = _flat(SPEC).lower()
    assert "do not overwrite" in flat
    assert "fifth sibling tree" in flat
    assert "linker_seam" in LOG


def test_prior_paths_stay_callable_and_are_not_overwritten():
    flat = _flat(SPEC).lower()
    for tree in ("kabsch/", "confidence_kabsch/", "piecewise_kabsch/"):
        assert tree in SPEC, tree
    assert "stay callable" in flat
    assert "keep prior paths callable" in flat
    assert "assembler" in flat
    assert "core/hold48_kabsch.py" in SPEC
    assert "core/hold48_confidence_kabsch.py" in SPEC
    assert "core/hold48_piecewise_kabsch.py" in SPEC
    assert "keep prior paths callable" in _flat(LOG).lower()


def test_served_stays_assembler_and_d126_stays_best_experimental():
    flat = _flat(SPEC).lower()
    log_flat = _flat(LOG).lower()
    index_flat = _flat(INDEX).lower()
    assert "served stays assembler" in flat
    assert "default served = assembler" in flat
    assert "matt swap go" in flat or "matt go names a swap" in flat
    assert "best experimental path" in flat
    assert "until proven otherwise" in flat
    assert "served stays assembler" in log_flat
    assert "best experimental path until proven otherwise" in log_flat
    assert "best experimental" in index_flat
    # No auto-flip on a pass count.
    assert "auto-flip" in flat


def test_d127_failed_experiment_stays_disclosed():
    """The negative D-127 OPS result is carried forward, not softened."""
    flat = _flat(SPEC).lower()
    log_flat = _flat(LOG).lower()
    assert "failed experiment stays disclosed" in flat
    assert "failed experiment stays disclosed" in log_flat
    for figure in ("17", "10", "0"):
        assert figure in SPEC, figure
    assert "recovered_of_primary_three" in SPEC
    assert "n_d125_pass_d127_refuse" in SPEC
    assert "n_d126_pass_d127_refuse" in SPEC
    assert "n_d126_refuse_d127_pass" in SPEC
    assert "not re-measured" in flat
    assert "as recorded" in flat
    # The 2-of-5 vs 0-of-3 comparison that made "D-126 is better" a number.
    assert "2 of its primary 5" in SPEC
    assert "0 of 3" in SPEC


def test_method_surface_is_mandatory_at_b_and_not_edited_here():
    """§7 is authority now; the addendum is a later B deliverable."""
    assert "## 7." in SPEC
    assert "Method / owner-facing" in SPEC
    flat = _flat(SPEC).lower()
    log_flat = _flat(LOG).lower()
    assert "mandatory" in flat
    assert "d-128-b" in flat
    assert "8th-grade" in flat
    assert "stitch-path train" in flat
    assert "silent code-only" in flat
    assert "this spec pr ships no method edit" in flat
    assert "no method edit" in log_flat
    assert "d-121" in flat and "d-125-b" in flat and "d-126-b" in flat and "d-127-b" in flat
    assert "methodnote" in flat or "/method" in SPEC
    assert "method-hold48-tiles.md" in SPEC
    # The Method excerpt must carry the honesty line, not just the algorithm.
    assert "dishonest" in flat
    assert "never claim seams solved" in flat or "never seams solved" in flat
    assert "mandatory" in log_flat


def test_ops_report_fields_name_honesty_and_confusion():
    """Ops report names the honesty counts and confusion vs D-125/126/127."""
    assert "## 11." in SPEC
    for field in (
        "n_seams_measured",
        "n_dishonest_kabsch",
        "n_dishonest_confidence_kabsch",
        "n_dishonest_piecewise_kabsch",
        "n_dishonest_linker_seam",
        "n_honesty_unknown",
        "n_d125_pass_d128_refuse",
        "n_d126_pass_d128_refuse",
        "n_d127_pass_d128_refuse",
        "n_d127_refuse_d128_pass",
        "repaired_of_seven",
    ):
        assert field in SPEC, field
    flat = _flat(SPEC).lower()
    assert "named finding" in flat
    assert "not a ci assert" in flat
    assert "confusion vs d-125" in flat or "vs d-125" in flat
    assert "d-126" in flat and "d-127" in flat


def test_ship_index_distinguishes_spec_from_ab_build():
    assert (
        "D-128 already shipped" in INDEX
        or "D-128 ships the linker / seam honesty Spec" in INDEX
    )
    assert "**Yes — this PR.**" in INDEX
    index_flat = _flat(INDEX)
    assert re.search(r"D-128 Spec.*Already shipped on `main`", index_flat)
    # A shipped at #247; B is the PR that ships the UI + mandatory Method.
    assert re.search(r"D-128-A.*Already shipped on `main`", index_flat)
    assert re.search(r"D-128-B.*\*\*Yes — this PR\.\*\*", index_flat)
    # A shipped code; it did not discharge the mandatory Method obligation,
    # and the index must still say which id does.
    lowered_index = INDEX.lower()
    assert "not** discharge" in INDEX or "not discharge" in lowered_index
    assert "discharges it" in lowered_index or "discharges the mandatory" in lowered_index
    assert re.search(r"D-127-B.*Already shipped on `main`", index_flat)
    assert re.search(r"D-127-A.*Already shipped on `main`", index_flat)
    assert "linker_seam" in INDEX
    assert "linker_local_kabsch_then_winning_tile" in INDEX
    lower = index_flat.lower()
    assert "cpu, no rent" in lower
    assert "kaylee does not build" in lower
    assert "mandatory" in lower


def test_plan_and_architecture_point_at_d128():
    assert "Kabsch park → **D-125**" in PLAN
    assert "**D-128**" in PLAN
    assert "SPEC-linker-seam-honesty.md" in PLAN
    assert "D-128 ships" in ARCH or "D-128:" in ARCH
    assert "SPEC-linker-seam-honesty.md" in ARCH
    assert "linker_seam" in ARCH
    assert "linker_local_kabsch_then_winning_tile" in ARCH
    arch_flat = _flat(ARCH).lower()
    assert "diagnose and refuse dishonest seams" in arch_flat
    assert "3432 stays accept-refuse" in arch_flat
    # Test plan carries the D-128 Spec T-ids.
    assert "T-1144" in TEST_PLAN
    assert "T-1152" in TEST_PLAN
    assert "test_d128_linker_seam_spec.py" in TEST_PLAN


def test_hard_stops_and_not_ab():
    assert "## 9." in SPEC
    flat = _flat(SPEC).lower()
    log_flat = _flat(LOG).lower()
    assert "no threshold spec-as-fix" in flat
    assert "no named-exclusion-as-fix" in flat
    assert "no invent" in flat
    assert "never 0" in SPEC
    assert "no f-004" in flat
    assert "no rent in a" in flat
    assert "never seams solved" in flat
    assert "keep prior paths callable" in flat
    assert "no trim loop" in flat
    assert "w = 32 stays" in flat
    assert "no stitch code in this pr" in flat
    assert "not d-128-a" in flat
    assert "not d-128-b" in flat
    assert "docs only" in flat
    assert "no rent in a" in log_flat
    assert "no f-004" in log_flat or "not f-004 ingest" in log_flat


def test_this_spec_pr_does_not_edit_hold48_modules():
    """Hard stop: D-128-A is a fifth sibling module. Prior paths stay byte-identical."""
    assert "def winning_tile" in STITCH
    assert "def kabsch" not in STITCH
    assert "linker_seam" not in STITCH
    assert "D-128" not in STITCH
    for name, text in (
        ("hold48_kabsch.py", KABSCH),
        ("hold48_confidence_kabsch.py", CONF),
        ("hold48_piecewise_kabsch.py", PIECEWISE),
    ):
        assert "linker_local_kabsch" not in text, name
        assert "linker_seam" not in text, name
        assert "seam_jump_gt_10" not in text, name
        assert "D-128" not in text, name
    assert "def fit_overlap_kabsch" in KABSCH
    assert "overlap_confidence_kabsch_then_winning_tile" in CONF
    assert "piecewise_domain_kabsch_then_winning_tile" in PIECEWISE
    assert "linker_jump_gt_10" in PIECEWISE  # D-127's reason name stays D-127's
    assert hashlib.sha256(KABSCH_PATH.read_bytes()).hexdigest() == D125_KABSCH_SHA256
    assert hashlib.sha256(CONF_PATH.read_bytes()).hexdigest() == D126_CONF_SHA256
    assert hashlib.sha256(PIECEWISE_PATH.read_bytes()).hexdigest() == D127_PIECEWISE_SHA256
    for path in (KABSCH, CONF, PIECEWISE):
        assert "import numpy" not in path
        assert "from numpy" not in path
    # D-128-A now exists as a fifth sibling module — and only as that.
    sibling = ROOT / "core" / "hold48_linker_seam.py"
    assert sibling.is_file()
    sib = sibling.read_text(encoding="utf-8")
    assert "linker_local_kabsch_then_winning_tile" in sib
    assert "def write_linker_seam_restitch" in sib
    assert "seam_jump_gt_10" in sib
    assert "import numpy" not in sib
    assert "from numpy" not in sib
    assert "trim_highest_residual" not in sib
    assert "DomainInterval" not in sib  # not piecewise-v2
    assert "inherit_piece_for_residue" not in sib
