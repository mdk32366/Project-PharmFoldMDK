"""Tasks M / N / O of `ORDERS-Code-2026-08-19` — the three straddle rules, tested before they report.

⚠⚠ **THE THREE RULES ARE THREE, NOT TWO.** `admit_raw` had never been named anywhere in this
project, and it is the rule that produced `D-095`'s founding numbers. A two-rule test has already
lost it, which is why every test below asserts all three in one place.

⚠ **THE DISCRIMINATING FIXTURES, named so a later reader cannot weaken them by accident:**

- `test_the_three_rules_disagree_on_a_straddler` — a fixture built only from domains INSIDE the
  span **passes under all three rules**, because the rules differ only on features crossing a
  boundary. Only a straddler separates them, and the fixture carries one in each direction.
- `test_merge_rules_disagree_on_abutment` — a fixture built from OVERLAPPING intervals **passes
  under both merge rules**. Abutment is the only thing that separates them, and abutment is the
  phenomenon (`FAT1`'s cadherin repeats share exact boundaries).
- `test_the_misfiling_path_is_real` — ⚠⚠ the reporter's diagnostic is **expected to return 0 on
  real data**, so a test asserting 0 passes under a diagnostic hard-wired to 0. The fixture
  therefore constructs the row that does not exist today and asserts the diagnostic finds it,
  and asserts `classify_regime` really does misfile it. **The defect is documented by a passing
  test, not by a comment.**
- `test_overhang_is_bucketed_by_direction` — a fixture overhanging in ONE direction passes under a
  counter that ignores direction. Past `s1` and before `s0` are different mistakes, so the fixture
  carries one of each plus one that does both.

Cache-only, synthetic fixtures, no network, no database, no GPU.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.tranche6_domain_survey import domain_intervals as admit_raw_intervals  # noqa: E402
from scripts.tranche6_domain_survey import merge  # noqa: E402
from scripts.tranche6_runs import TRAINED_CONTEXT, classify_regime  # noqa: E402
from scripts.tranche6_runs import domain_intervals as drop_intervals  # noqa: E402
from scripts.tranche6_runs_clip_compare import (  # noqa: E402
    clip_intervals,
    merge_overlap_only,
    misfiled_single_run,
    straddle_overhang,
)

S0, S1 = 100, 1000


def _feature(a: int, b: int, desc: str = "d", typ: str = "Domain") -> dict:
    return {"type": typ,
            "description": desc,
            "location": {"start": {"value": a}, "end": {"value": b}}}


def _doc(*features: dict) -> dict:
    return {"features": list(features)}


# ─────────────────────────────────────────────────── the three rules are three different rules ──

def test_the_three_rules_disagree_on_a_straddler():
    """⚠ The discriminating case. An interior-only fixture cannot tell these three apart."""
    doc = _doc(
        _feature(50, 150, "before_s0"),    # crosses s0 — starts outside the span
        _feature(300, 400, "interior"),    # wholly inside — every rule keeps it unchanged
        _feature(900, 1200, "past_s1"),    # crosses s1 — ends outside the span
        _feature(2000, 2100, "outside"),   # wholly outside — every rule drops it
    )

    raw = [(a, b) for a, b, *_ in admit_raw_intervals(doc, S0, S1)]
    dropped = [(a, b) for a, b, *_ in drop_intervals(doc, S0, S1)]
    clipped = [(a, b) for a, b, *_ in clip_intervals(doc, S0, S1)]

    # admit_raw keeps the straddlers AT THEIR RAW COORDINATES — outside the span on both ends.
    assert raw == [(50, 150), (300, 400), (900, 1200)]
    # drop keeps only what is wholly inside.
    assert dropped == [(300, 400)]
    # clip keeps the straddlers, truncated to the span.
    assert clipped == [(100, 150), (300, 400), (900, 1000)]

    # ⚠ And the three are genuinely three: no two agree on this fixture.
    assert raw != dropped and raw != clipped and dropped != clipped
    # ⚠ The wholly-outside feature is admitted by NONE of them.
    assert all(b <= 1200 for _, b in raw)
    assert (2000, 2100) not in raw


def test_admit_raw_reports_residues_the_span_does_not_contain():
    """⚠ Why `admit_raw` is not a harmless third option: it lets a run leave the span entirely."""
    doc = _doc(_feature(900, 1200, "past_s1"))
    (a, b) = [(a, b) for a, b, *_ in admit_raw_intervals(doc, S0, S1)][0]
    assert b > S1                      # the interval ends beyond the span it is measured against
    assert (b - a + 1) == 301          # and its length counts 200 residues the span does not hold
    clipped_len = [(x, y) for x, y, *_ in clip_intervals(doc, S0, S1)][0]
    assert (clipped_len[1] - clipped_len[0] + 1) == 101


# ────────────────────────────────────────────────────────────── the merge rule is the phenomenon ──

def test_merge_rules_disagree_on_abutment():
    """⚠ An overlapping-only fixture passes under both rules. Abutment is the discriminator."""
    abutting = [(100, 200, "", ""), (201, 300, "", "")]
    gapped = [(400, 500, "", ""), (502, 600, "", "")]
    overlapping = [(700, 800, "", ""), (750, 900, "", "")]

    # shipped rule: `start <= prev_end + 1` — abutment joins.
    assert merge(abutting) == [[100, 300]]
    assert merge_overlap_only(abutting) == [[100, 200], [201, 300]]

    # ⚠ gap tolerance is ZERO UNCOVERED RESIDUES: one uncovered residue at 501 splits the run.
    assert merge(gapped) == [[400, 500], [502, 600]]

    # overlap is joined by both — this pair alone could not tell the rules apart.
    assert merge(overlapping) == merge_overlap_only(overlapping) == [[700, 900]]


def test_abutting_stack_collapses_only_under_the_shipped_rule():
    """The FAT1 shape in miniature: `35-149 | 150-257 | 258-370` is one molecule-continuous stack."""
    stack = [(35, 149, "", ""), (150, 257, "", ""), (258, 370, "", "")]
    assert merge(stack) == [[35, 370]]                 # one run of 336 aa
    assert len(merge_overlap_only(stack)) == 3         # three runs, and the stack is invisible


# ──────────────────────────────────────────────────────── the misfiling path, documented as real ──

def test_the_misfiling_path_is_real():
    """⚠⚠ `classify_regime` returns on `len(runs) == 1` BEFORE it counts oversized runs.

    Expected count on real data is 0, so this asserts the diagnostic on the row that does NOT
    exist today. A test asserting only the real-data 0 would pass under a diagnostic wired to 0.
    """
    oversized_single = [TRAINED_CONTEXT + 1]

    # The misfiling is real, not hypothetical: the row is filed as if it needed no cut.
    assert classify_regime(n_domains=1, runs=oversized_single) == "single_run_only"
    assert misfiled_single_run(oversized_single) is True

    # One run, inside context — correctly `single_run_only`, and NOT a misfiling.
    assert classify_regime(n_domains=1, runs=[TRAINED_CONTEXT]) == "single_run_only"
    assert misfiled_single_run([TRAINED_CONTEXT]) is False

    # Two runs, one oversized — correctly filed, so the diagnostic must stay silent.
    assert classify_regime(n_domains=2, runs=[TRAINED_CONTEXT + 1, 50]) == "one_oversized_run"
    assert misfiled_single_run([TRAINED_CONTEXT + 1, 50]) is False

    # ⚠ The boundary is strictly greater, matching `runs_over_context` and `past_context_rows`.
    assert misfiled_single_run([TRAINED_CONTEXT]) is False
    assert misfiled_single_run([TRAINED_CONTEXT + 1]) is True

    # No runs at all is `no_domains`, never a misfiling.
    assert misfiled_single_run([]) is False


# ─────────────────────────────────────────────────────────── overhang, bucketed by direction ──

def test_overhang_is_bucketed_by_direction():
    """⚠ A one-direction fixture passes under a counter that sums a single total."""
    doc = _doc(
        _feature(50, 150, "before_s0"),    # 50 residues before s0 (100..50 -> 50)
        _feature(900, 1200, "past_s1"),    # 200 residues past s1
        _feature(10, 2000, "both_ends"),   # 90 before AND 1000 past
        _feature(300, 400, "interior"),    # neither — must not appear in any bucket
        _feature(3000, 3100, "outside"),   # not admitted at all
    )
    o = straddle_overhang(doc, S0, S1)

    assert o["n_before_s0_only"] == 1
    assert o["n_past_s1_only"] == 1
    assert o["n_both_ends"] == 1
    assert o["n_wholly_inside"] == 1
    assert o["n_admitted"] == 4          # the wholly-outside feature is not admitted

    # ⚠ Residues, per direction, counted once each — `both_ends` contributes to both sums.
    assert o["residues_before_s0"] == 50 + 90
    assert o["residues_past_s1"] == 200 + 1000

    # ⚠ The buckets partition what was admitted — an unbucketed straddler would break this.
    assert (o["n_before_s0_only"] + o["n_past_s1_only"]
            + o["n_both_ends"] + o["n_wholly_inside"]) == o["n_admitted"]


def test_overhang_is_zero_when_nothing_straddles():
    """An empty category is a measurement: the zero is asserted, not assumed."""
    o = straddle_overhang(_doc(_feature(300, 400, "interior")), S0, S1)
    assert o["n_admitted"] == 1
    assert o["n_before_s0_only"] == o["n_past_s1_only"] == o["n_both_ends"] == 0
    assert o["residues_before_s0"] == o["residues_past_s1"] == 0


# ───────────────────────────────────────────────────────────────── the rules agree where they must ──

def test_all_three_rules_agree_when_nothing_straddles():
    """⚠ The control. If these ever disagree here, the difference is not the straddle rule."""
    doc = _doc(_feature(300, 400), _feature(500, 600))
    raw = [(a, b) for a, b, *_ in admit_raw_intervals(doc, S0, S1)]
    dropped = [(a, b) for a, b, *_ in drop_intervals(doc, S0, S1)]
    clipped = [(a, b) for a, b, *_ in clip_intervals(doc, S0, S1)]
    assert raw == dropped == clipped == [(300, 400), (500, 600)]
