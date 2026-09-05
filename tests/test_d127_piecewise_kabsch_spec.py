"""D-127 — Piecewise / domain-aware Kabsch Spec. These must be able to go red.

Spec GO: the living-log heading exists, the Spec file exists, the
algorithm name and 10.0 Å refuse gate are pinned, the primary three
are named, hard stops are written, D-127-A/B are not this PR, and
``hold48_*.py`` is not edited.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
SPEC_PATH = ROOT / "docs" / "SPEC-piecewise-domain-kabsch.md"
SPEC = SPEC_PATH.read_text(encoding="utf-8")
INDEX = (ROOT / "docs" / "decisions.md").read_text(encoding="utf-8")
PLAN = (ROOT / "docs" / "PLAN-ui-post-wave2-endstate.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
STITCH = (ROOT / "core" / "hold48_stitch.py").read_text(encoding="utf-8")
HOLD48 = (ROOT / "core" / "hold48.py").read_text(encoding="utf-8")
KABSCH_PATH = ROOT / "core" / "hold48_kabsch.py"
KABSCH = KABSCH_PATH.read_text(encoding="utf-8")
CONF_PATH = ROOT / "core" / "hold48_confidence_kabsch.py"
CONF = CONF_PATH.read_text(encoding="utf-8")

# Primary three D-126 OPS REFUSE parents — not a Fly query, not a named-exclusion.
PRIMARY_THREE = (
    (2939, "Q7Z408"),
    (3272, "Q6V0I7"),
    (3432, "Q8IZF6"),
)

# D-125-A module on main (`26a40a8`). Must stay. If it moves, hold48_kabsch.py
# was edited (forbidden in this Spec PR).
D125_KABSCH_SHA256 = "4c7bb45d04507e2a67ba3600b35d6130d62843ca3bc99c15d3568d5cb105ff6e"


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def test_d127_heading_exists_in_the_living_log():
    """The check is the heading, not a citation of it (D-062 / method-note 7)."""
    assert re.search(
        r"^### D-127 — Piecewise / domain-aware Kabsch Spec",
        LOG,
        re.M,
    ), "D-127 must be a real ### entry, not a citation of one"
    assert re.search(r"^### D-126 — Overlap-confidence Kabsch Spec", LOG, re.M)
    assert re.search(r"^### D-126-A — Overlap-confidence Kabsch core", LOG, re.M)
    assert re.search(r"^### D-126-B — UI triple-path honesty", LOG, re.M)
    assert re.search(r"^### D-125 — Kabsch restitch Spec", LOG, re.M)
    assert re.search(
        r"^### D-127-A — Piecewise / domain-aware Kabsch core",
        LOG,
        re.M,
    ), "D-127-A must be a real ### entry, not a citation of one"
    assert "Docs Spec only" in LOG or "docs only" in LOG.lower()
    assert "Not D-127-A" in LOG or "not d-127-a" in LOG.lower()
    assert "Not D-127-B" in LOG or "not d-127-b" in LOG.lower()


def test_spec_file_exists_and_names_algorithm():
    assert SPEC_PATH.is_file()
    assert "piecewise_domain_kabsch_then_winning_tile" in SPEC
    flat = _flat(SPEC).lower()
    assert "piecewise" in flat and "domain-aware" in flat
    assert "winning_tile" in SPEC
    assert "must **not replace**" in SPEC or "not replace" in flat
    assert "seams are not scientifically solved" in flat
    assert "multi-rigid" in flat
    assert "no trim loop" in flat


def test_refuse_gate_stays_at_10():
    """10.0 Å STAYS. Do not raise. Piecewise is not a threshold Spec-as-fix."""
    assert "10.0" in SPEC
    assert "10 Å STAYS" in SPEC or "10.0 Å" in SPEC
    assert "do not raise" in _flat(SPEC).lower()
    assert "overlap_ca_lt_3" in SPEC
    assert "rmsd_gt_10" in SPEC
    assert "singular_covariance" in SPEC
    assert "no_domain_pieces" in SPEC
    assert "linker_jump_gt_10" in SPEC
    assert "< 3" in SPEC or "`< 3`" in SPEC


def test_primary_three_inventory():
    assert len(PRIMARY_THREE) == 3
    for pid, acc in PRIMARY_THREE:
        assert str(pid) in SPEC, pid
        assert acc in SPEC, acc
        assert str(pid) in LOG, pid
        assert acc in LOG, acc
    assert "3356" in SPEC  # named as out
    assert "IGF2R" in SPEC
    assert "28–68" in SPEC or "28-68" in SPEC
    assert "F-004" in SPEC
    assert "0-of-3" in SPEC
    # D-126's other two of the five are not this Spec's primary three.
    assert "3368" in SPEC
    assert "3394" in SPEC
    assert "primary three" in _flat(SPEC).lower()
    assert "3368" in SPEC and "not" in _flat(SPEC).lower()


def test_hard_stops_and_not_ab():
    flat = _flat(SPEC).lower()
    log_flat = _flat(LOG).lower()
    assert "no threshold spec-as-fix" in flat
    assert "no named-exclusion-as-fix" in flat
    assert "no invent" in flat
    assert "never 0" in SPEC
    assert "no f-004" in flat
    assert "no rent in a" in flat
    assert "never seams solved" in flat or "seams are not scientifically solved" in flat
    assert "keep assembler" in flat
    assert "d-125" in flat and "d-126" in flat
    assert "not d-127-a" in flat or "**not d-127-a**" in flat
    assert "not d-127-b" in flat or "**not d-127-b**" in flat
    assert "docs spec only" in log_flat or "docs only" in log_flat
    assert "not d-127-a" in log_flat
    assert "not d-127-b" in log_flat
    assert "no hold48_*.py" in log_flat or "no `hold48_*.py`" in LOG.lower() or "hold48_*.py" in LOG


def test_no_trim_loop_and_epsilon():
    """Another weight/trim knob is forbidden. ε = 1e-3. No trim loop."""
    sec1 = SPEC.split("## 2.")[0]
    assert "1e-3" in sec1
    assert "1e-3" in LOG
    assert "NO trim loop" in SPEC or "No trim loop" in SPEC
    assert "D-126 lie surface" in SPEC
    assert "another weight / trim knob is forbidden" in _flat(SPEC).lower()
    assert "w_i" in sec1
    assert "min(" in sec1 or r"\min" in sec1
    assert "R p_i + t" in sec1
    assert "q_i" in sec1
    flat1 = _flat(sec1).lower()
    assert "trim loop" in flat1
    # §1 must not authorise a trim loop as a step.
    assert "cap **5** rounds" not in sec1
    assert "(c) trim loop" not in sec1


def test_refuse_table_names_piece_and_parent_reasons():
    sec2 = SPEC.split("## 2.")[1].split("## 3.")[0]
    assert "overlap_ca_lt_3" in sec2
    assert "rmsd_gt_10" in sec2
    assert "singular_covariance" in sec2
    assert "no_domain_pieces" in sec2
    assert "linker_jump_gt_10" in sec2
    assert "10.0" in sec2
    assert "all-or-nothing" in _flat(sec2).lower()
    assert "_clear_success_artifacts" in sec2


def test_domain_snap_source_is_emit_source():
    """Same UniProt Domain/Repeat source as emit domain-snap."""
    sec1 = SPEC.split("## 2.")[0]
    assert "domain_ends_span_relative" in sec1
    assert "emit" in _flat(sec1).lower()
    assert "Domain" in sec1 and "Repeat" in sec1
    assert "spancache" in sec1 or "domain-snap" in sec1
    assert "domain_ends_span_relative" in HOLD48
    assert "def domain_ends_span_relative" in HOLD48
    assert "def plan_tiles" in HOLD48


def test_disclosure_per_piece_and_parent_after_apply():
    """Per-piece n_ca/rmsd; parent full-overlap + max jump after piecewise apply."""
    assert "n_ca" in SPEC
    assert "rmsd_full_overlap_angstrom" in SPEC
    assert "max_ca_jump_angstrom" in SPEC
    assert "linker_n" in SPEC
    assert "max_linker_ca_jump" in SPEC
    assert "rmsd_full_overlap_angstrom" in LOG
    assert "max_ca_jump_angstrom" in LOG
    flat = _flat(SPEC).lower()
    assert "per piece" in flat or "per-piece" in flat
    assert "refused before any transform" in flat
    assert "after piecewise apply" in flat
    assert "null" in flat


def test_artifact_dir_is_sibling_piecewise_kabsch():
    assert "piecewise_kabsch/" in SPEC
    assert "piecewise_kabsch/{parent_job_id}" in SPEC or "piecewise_kabsch/{parent_id}" in SPEC
    assert "piecewise_domain_kabsch_then_winning_tile" in SPEC
    assert "`decision`: `D-127`" in SPEC or "decision=`D-127`" in SPEC or "decision`: `D-127`" in SPEC
    flat = _flat(SPEC).lower()
    assert "do not overwrite" in flat
    assert "kabsch/" in SPEC
    assert "confidence_kabsch/" in SPEC
    assert "assembler" in flat


def test_ship_index_distinguishes_spec_from_ab_build():
    assert "D-127 already shipped" in INDEX or "D-127 ships the piecewise / domain-aware Kabsch Spec" in INDEX
    assert "Yes — this PR." in INDEX
    assert re.search(r"D-127 Spec.*Already shipped on `main`", _flat(INDEX))
    assert re.search(r"D-127-A.*Already shipped on `main`", _flat(INDEX))
    assert re.search(r"D-127-B.*\*\*Yes — this PR\.\*\*", _flat(INDEX))
    assert re.search(r"D-126-B.*Already shipped on `main`", _flat(INDEX))
    assert "piecewise_kabsch" in INDEX
    assert "four-path" in INDEX.lower() or "four-path" in INDEX
    assert "does **not** discharge" in INDEX or "does not discharge" in INDEX.lower()


def test_plan_and_architecture_point_at_d127():
    assert "Kabsch park → **D-125**" in PLAN
    assert "**D-127**" in PLAN
    assert "SPEC-piecewise-domain-kabsch.md" in PLAN
    assert "D-127 ships" in ARCH or "D-127:" in ARCH
    assert "SPEC-piecewise-domain-kabsch.md" in ARCH
    assert "piecewise_kabsch" in ARCH


def test_this_spec_pr_does_not_edit_hold48_modules():
    """Hard stop: D-127-A is a sibling module. D-125 / D-126 bytes stay pinned."""
    assert "def winning_tile" in STITCH
    assert "def kabsch" not in STITCH
    assert "piecewise_domain_kabsch" not in KABSCH
    assert "piecewise_kabsch" not in KABSCH
    assert "D-127" not in KABSCH
    assert "piecewise_domain_kabsch" not in CONF
    assert "piecewise_kabsch" not in CONF
    assert "D-127" not in CONF
    assert "def fit_overlap_kabsch" in KABSCH
    assert hashlib.sha256(KABSCH_PATH.read_bytes()).hexdigest() == D125_KABSCH_SHA256
    assert hashlib.sha256(CONF_PATH.read_bytes()).hexdigest() == (
        "d526a856ec8f1ba978a3586f3dfcf4a0ee858da12132499f2db37368efc77f18"
    )
    assert CONF_PATH.is_file()
    assert "overlap_confidence_kabsch_then_winning_tile" in CONF
    assert "import numpy" not in KABSCH
    assert "from numpy" not in KABSCH
    sibling = ROOT / "core" / "hold48_piecewise_kabsch.py"
    assert sibling.is_file()
    sib = sibling.read_text(encoding="utf-8")
    assert "piecewise_domain_kabsch_then_winning_tile" in sib
    assert "def write_piecewise_kabsch_restitch" in sib
    assert "import numpy" not in sib
    assert "from numpy" not in sib
    assert "trim_highest_residual" not in sib


def test_zero_of_three_recovered_is_allowed():
    """Recovering zero of the primary three is a valid experimental result."""
    flat = _flat(SPEC).lower()
    log_flat = _flat(LOG).lower()
    assert "0-of-3" in SPEC or "0-of-3" in LOG
    assert "allowed outcome" in flat
    assert "allowed outcome" in log_flat
    assert "valid experimental result" in flat
    assert "do not loosen" in flat
    assert "blend" in flat
    assert "recovered_of_primary_three" in SPEC


def test_ops_confusion_vs_d125_and_d126():
    """Ops report must name confusion vs D-125 and vs D-126; not a CI assert."""
    assert "n_d125_pass_d127_refuse" in SPEC
    assert "n_d126_pass_d127_refuse" in SPEC
    assert "n_d126_refuse_d127_pass" in SPEC
    assert "recovered_of_primary_three" in SPEC
    flat = _flat(SPEC).lower()
    assert "named finding" in flat
    assert "not a ci assert" in flat
    assert "confusion vs d-125" in flat
    assert "confusion vs d-126" in flat or "vs d-126" in flat
    assert "## 11." in SPEC


def test_gpu_refine_is_later_phase_not_a():
    flat = _flat(SPEC).lower()
    assert "later phase" in flat
    assert "not a" in flat
    assert "gpu refine" in flat or "md / af" in flat
    assert "no rent in a" in flat


def test_method_surface_is_mandatory_not_silent_code_only():
    """Matt/Emma: Method must surface D-127. Not a silent code-only ship."""
    assert "## 7." in SPEC
    assert "Method / owner-facing" in SPEC
    flat = _flat(SPEC).lower()
    log_flat = _flat(LOG).lower()
    index_flat = _flat(INDEX).lower()
    assert "mandatory" in flat
    assert "silent code-only" in flat
    assert "no silent code-only" in flat or "not a silent code-only" in flat
    assert "method addendum is **mandatory**" in SPEC.lower() or "method addendum is **mandatory**" in LOG.lower() or "mandatory** before calling d-127" in flat
    assert "stitch-path train" in flat
    assert "assembler" in flat and "d-125" in flat and "d-126" in flat
    assert "piecewise" in flat
    assert "8th-grade" in flat or "8th-grade" in SPEC
    assert "full ≫ weighted" in SPEC or "full >> weighted" in SPEC
    assert "never claim seams solved" in flat or "never seams solved" in flat
    assert "default served" in flat and "assembler" in flat
    assert "methodnote" in flat or "method note" in flat or "/method" in SPEC
    assert "d-121" in flat and "d-125-b" in flat and "d-126-b" in flat
    # Living log + ship index cite the Method obligation.
    assert "method must surface d-127" in log_flat
    assert "silent code-only" in log_flat
    assert "mandatory" in log_flat
    assert "method obligation" in index_flat or "mandatory method" in index_flat
    assert "silent code-only" in index_flat
    # B ships Method; A does not discharge it.
    assert "d-127-b" in flat
    assert "does **not** discharge the method obligation" in index_flat or "does not discharge" in index_flat
    # D-127-B discharges the obligation: the owner markdown now carries the
    # addendum, and it cites §7 as the authority that made it mandatory.
    method_md = (ROOT / "docs" / "method-hold48-tiles.md").read_text(encoding="utf-8")
    assert "Addendum D-127-B" in method_md
    assert "§7" in method_md
    assert "mandatory" in method_md.lower()
