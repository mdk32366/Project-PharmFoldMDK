"""Ceiling-probe bisection logic (D-022) — pure, runs on the CI gate.

The fold at each length is GPU-bound and owner-run on the A6000 (D-018 pattern); what
is testable without a GPU is the bisection and the crash-resume reconstruction, which
is where correctness that matters lives — a wrong resume would re-fold or skip lengths
and burn rental time, and a wrong ceiling would misroute the cohort.
"""

import pytest

from worker.ceiling_probe import (
    ERROR,
    OK,
    OOM,
    bounds_from_history,
    ceiling_from_history,
    next_probe_length,
)


# ── next_probe_length ─────────────────────────────────────────────────────────

def test_midpoint():
    assert next_probe_length(440, 1600, step=25) == 1020


def test_converged_returns_none():
    assert next_probe_length(600, 620, step=25) is None       # gap 20 <= step
    assert next_probe_length(600, 625, step=25) is None       # gap 25 <= step


def test_not_converged_just_over_step():
    assert next_probe_length(600, 626, step=25) == 613        # gap 26 > step


def test_requires_good_below_bad():
    with pytest.raises(ValueError):
        next_probe_length(700, 700, step=25)
    with pytest.raises(ValueError):
        next_probe_length(800, 700, step=25)


def test_a_full_bisection_converges_downward():
    # Simulate a true ceiling at 690: lengths <=690 fold, >690 fail. Converge with step 25.
    good, bad, step = 440, 1600, 25
    for _ in range(50):
        L = next_probe_length(good, bad, step)
        if L is None:
            break
        if L <= 690:
            good = L
        else:
            bad = L
    assert bad - good <= step
    assert good <= 690 < bad                                  # ceiling bracketed correctly


# ── resume / bounds reconstruction (crash-resilience) ─────────────────────────

def test_bounds_from_history_raises_floor_and_lowers_ceiling():
    hist = [{"length": 1020, "outcome": OOM}, {"length": 730, "outcome": OK},
            {"length": 875, "outcome": ERROR}]
    good, bad = bounds_from_history(hist, init_good=440, init_bad=1600)
    assert good == 730 and bad == 875


def test_bounds_ignore_malformed_and_torn_rows():
    # A crash can leave a partial/garbage row; it must not corrupt the bounds.
    hist = [{"length": 700, "outcome": OK}, {"length": None, "outcome": OK},
            {"outcome": OOM}, {"length": 900, "outcome": "weird"}, {}]
    good, bad = bounds_from_history(hist, 440, 1600)
    assert good == 700 and bad == 1600


def test_ceiling_is_largest_proven_foldable():
    hist = [{"length": 730, "outcome": OK}, {"length": 800, "outcome": OOM},
            {"length": 765, "outcome": OK}]
    assert ceiling_from_history(hist, init_good=440) == 765


def test_ceiling_defaults_to_init_when_nothing_folded():
    hist = [{"length": 500, "outcome": OOM}]
    assert ceiling_from_history(hist, init_good=440) == 440


def test_resume_then_continue_is_consistent():
    # Bounds reconstructed from history feed straight back into next_probe_length.
    hist = [{"length": 1020, "outcome": OOM}, {"length": 730, "outcome": OK}]
    good, bad = bounds_from_history(hist, 440, 1600)
    assert (good, bad) == (730, 1020)
    assert next_probe_length(good, bad, step=25) == 875       # resumes mid-bisection
