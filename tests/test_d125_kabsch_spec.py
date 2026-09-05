"""D-125 — Kabsch restitch Spec. These must be able to go red.

Docs-only GO: the living-log heading exists, the Spec names the algorithm
and the three refuse defaults, the 27-id inventory matches the existing
census set, and ``hold48_stitch.py`` still has no Kabsch implementation.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
SPEC = (ROOT / "docs" / "SPEC-kabsch-restitch.md").read_text(encoding="utf-8")
INDEX = (ROOT / "docs" / "decisions.md").read_text(encoding="utf-8")
PLAN = (ROOT / "docs" / "PLAN-ui-post-wave2-endstate.md").read_text(encoding="utf-8")
STITCH = (ROOT / "core" / "hold48_stitch.py").read_text(encoding="utf-8")

# Same 27 ids as D-117 / D-120 / WAVE1_WAVE2_STITCHED_PARENT_IDS — not a Fly query.
PARENT_IDS = (
    2817, 2917, 2929, 2938, 2939, 3027, 3097, 3153, 3179, 3188, 3190,
    3217, 3272, 3320, 3321, 3368, 3379, 3394, 3404, 3432, 3454, 3469,
    3516, 3541, 3566, 3569, 3575,
)


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def test_d125_heading_exists_in_the_living_log():
    """The check is the heading, not a citation of it (D-062 / method-note 7)."""
    assert re.search(
        r"^### D-125 — Kabsch restitch Spec",
        LOG,
        re.M,
    ), "D-125 must be a real ### entry, not a citation of one"
    assert "### D-121 — Method hold-48 8th-grade explainer" in LOG
    assert "### D-120 — Phase 2 review UI" in LOG
    assert "### D-118 — Phase 1 P0 honesty" in LOG
    # D-125 Spec reserved D-124; ADC-C-A (this PR) spends it. Both headings must exist.
    assert re.search(
        r"^### D-124 — ADC-C-A:",
        LOG,
        re.M,
    ), "D-124 is ADC-C-A's integer — the Spec did not spend it; this PR does"


def test_spec_names_algorithm_and_does_not_replace_the_assembler():
    flat = _flat(SPEC).lower()
    assert "kabsch on overlap" in flat
    assert "winning_tile" in SPEC
    assert "must **not replace**" in SPEC or "not replace" in flat
    assert "seams are not scientifically solved" in flat
    assert "seams solved" not in flat or "not scientifically solved" in flat
    assert "full-length af-quality" not in flat or "forbidden" in flat


def test_refuse_v1_defaults_are_named():
    """Named so a later A BUILD can go red. Not a measurement of the 27."""
    assert "< 3" in SPEC or "`< 3`" in SPEC
    assert "10.0" in SPEC
    assert "singular" in SPEC.lower() and "degenerate" in SPEC.lower()
    assert "refuse" in SPEC.lower()


def test_twenty_seven_ids_match_existing_inventory():
    assert len(PARENT_IDS) == 27
    assert 3356 not in PARENT_IDS
    for pid in PARENT_IDS:
        assert str(pid) in SPEC, pid
        assert str(pid) in LOG, pid


def test_ship_index_distinguishes_spec_from_future_ab_build():
    assert "D-125 ships the Kabsch restitch Spec" in INDEX
    assert "D-125-A / D-125-B are NOT this PR" in INDEX
    assert "wait until D-124 A+B" in INDEX
    assert "Yes — this PR." in INDEX
    assert re.search(r"D-125-A.*\*\*No\.\*\*", _flat(INDEX))


def test_plan_kabsch_park_points_at_d125():
    assert "Kabsch park → **D-125**" in PLAN


def test_this_spec_pr_does_not_implement_kabsch_in_the_stitcher():
    """Hard stop: no stitch-code bleed. A later A BUILD inverts this pin."""
    assert "def kabsch" not in STITCH
    assert "Kabsch" not in STITCH
    assert "def winning_tile" in STITCH
