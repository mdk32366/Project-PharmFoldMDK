"""D-126 — Overlap-confidence Kabsch Spec. These must be able to go red.

Docs-only GO: the living-log heading exists, the Spec file exists, the
algorithm name and 10.0 Å refuse gate are pinned, the primary five are
named, hard stops are written, this PR is not D-126-A/B, and
``hold48_kabsch.py`` is not edited.
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

# D-125-A module on main (`26a40a8`, unchanged at D-125-B `aa8d3f1`).
# A later D-126-A BUILD updates this pin when it adds a sibling module.
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
    assert re.search(r"^### D-125 — Kabsch restitch Spec", LOG, re.M)
    assert re.search(r"^### D-125-B — UI dual-path honesty", LOG, re.M)


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
    assert "not d-126-a" in flat or "**not d-126-a**" in flat
    assert "not d-126-b" in flat or "**not d-126-b**" in flat
    assert "docs spec only" in log_flat or "docs only" in log_flat
    assert "not d-126-a" in log_flat
    assert "not d-126-b" in log_flat


def test_ship_index_distinguishes_spec_from_future_ab_build():
    assert "D-126 ships the overlap-confidence Kabsch Spec" in INDEX
    assert "D-126-A / D-126-B are NOT this PR" in INDEX
    assert "Yes — this PR." in INDEX
    assert re.search(r"D-126 Spec.*\*\*Yes — this PR\.\*\*", _flat(INDEX))
    assert re.search(r"D-126-A.*\*\*No\.\*\*", _flat(INDEX))
    assert re.search(r"D-126-B.*\*\*No\.\*\*", _flat(INDEX))
    assert "confidence_kabsch" in INDEX or "overlap-confidence" in INDEX.lower()


def test_plan_and_architecture_point_at_d126():
    assert "Kabsch park → **D-125**" in PLAN
    assert "**D-126**" in PLAN
    assert "SPEC-overlap-confidence-kabsch.md" in PLAN
    assert "D-126 ships" in ARCH or "D-126:" in ARCH
    assert "SPEC-overlap-confidence-kabsch.md" in ARCH
    assert "D-125 Kabsch + assembler remain" in ARCH or "assembler remain" in ARCH.lower()


def test_this_spec_pr_does_not_edit_hold48_kabsch_or_the_assembler():
    """Hard stop: no stitch-code bleed. A later A BUILD inverts the D-126 pins only."""
    assert "def winning_tile" in STITCH
    assert "def kabsch" not in STITCH
    assert "overlap_confidence_kabsch" not in KABSCH
    assert "confidence_kabsch" not in KABSCH
    assert "D-126" not in KABSCH
    assert "def fit_overlap_kabsch" in KABSCH
    assert hashlib.sha256(KABSCH_PATH.read_bytes()).hexdigest() == D125_KABSCH_SHA256
