"""D-125 — Kabsch restitch Spec + D-125-A core BUILD pins.

The heading exists, the Spec names the algorithm and refuse defaults, the
27-id inventory matches the existing census set, and ``hold48_stitch.py``
still has no Kabsch implementation (A is a new path that *feeds*
``winning_tile``).
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
KABSCH = (ROOT / "core" / "hold48_kabsch.py").read_text(encoding="utf-8")

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
    assert re.search(
        r"^### D-124 — ADC-C-A:",
        LOG,
        re.M,
    ), "D-124 is ADC-C; D-125 does not spend it"


def test_spec_names_algorithm_and_does_not_replace_the_assembler():
    flat = _flat(SPEC).lower()
    assert "kabsch on overlap" in flat
    assert "winning_tile" in SPEC
    assert "must **not replace**" in SPEC or "not replace" in flat
    assert "seams are not scientifically solved" in flat
    assert "seams solved" not in flat or "not scientifically solved" in flat
    assert "full-length af-quality" not in flat or "forbidden" in flat


def test_refuse_v1_defaults_are_named():
    """Named so A tests can go red. Not a measurement of the 27."""
    assert "< 3" in SPEC or "`< 3`" in SPEC
    assert "10.0" in SPEC
    assert "singular" in SPEC.lower() and "degenerate" in SPEC.lower()
    assert "refuse" in SPEC.lower()


def test_twenty_seven_ids_match_existing_inventory():
    from core.hold48_kabsch import KABSCH_RESTITCH_PARENT_IDS

    reads = (ROOT / "app" / "reads.py").read_text(encoding="utf-8")
    block = re.search(
        r"WAVE1_WAVE2_STITCHED_PARENT_IDS = frozenset\(\{([^}]+)\}\)",
        reads,
        re.S,
    )
    assert block, "WAVE1_WAVE2_STITCHED_PARENT_IDS must remain the census inventory"
    reads_ids = frozenset(int(x) for x in re.findall(r"\d+", block.group(1)))

    assert len(PARENT_IDS) == 27
    assert 3356 not in PARENT_IDS
    assert KABSCH_RESTITCH_PARENT_IDS == frozenset(PARENT_IDS)
    assert KABSCH_RESTITCH_PARENT_IDS == reads_ids
    for pid in PARENT_IDS:
        assert str(pid) in SPEC, pid
        assert str(pid) in LOG, pid


def test_ship_index_names_a_as_this_pr_and_b_as_later():
    assert "D-125 ships the Kabsch restitch Spec" in INDEX
    assert "D-125-A ships" in INDEX or "D-125-A** | Kabsch core BUILD" in INDEX
    assert "Yes — this PR." in INDEX
    assert re.search(r"D-125-A.*\*\*Yes — this PR\.\*\*", _flat(INDEX))
    assert re.search(r"D-125-B.*\*\*No\.\*\*", _flat(INDEX))
    assert "Not D-125-B" in INDEX or "D-125-B is NOT this PR" in INDEX


def test_plan_kabsch_park_points_at_d125():
    assert "Kabsch park → **D-125**" in PLAN


def test_assembler_is_not_replaced_kabsch_is_a_new_path():
    """A BUILD inverts the 'no Kabsch yet' pin by adding a sibling module."""
    assert "def winning_tile" in STITCH
    assert "def kabsch" not in STITCH
    assert "Kabsch" not in STITCH
    assert "def fit_overlap_kabsch" in KABSCH
    assert "write_stitched" in KABSCH
    assert "winning_tile" in KABSCH
    assert "import numpy" not in KABSCH
    assert "from numpy" not in KABSCH
