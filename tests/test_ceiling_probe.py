"""Ceiling-probe bisection logic (D-022) — pure, runs on the CI gate.

The fold at each length is GPU-bound and owner-run on the A6000 (D-018 pattern); what
is testable without a GPU is the bisection and the crash-resume reconstruction, which
is where correctness that matters lives — a wrong resume would re-fold or skip lengths
and burn rental time, and a wrong ceiling would misroute the cohort.
"""

import ast
import inspect  # noqa: F401 - kept for the source-reading idiom below
from pathlib import Path

import pytest

from worker.ceiling_probe import (
    ERROR,
    K_REPEAT,
    OK,
    OOM,
    UNSTABLE,
    bounds_from_history,
    ceiling_from_history,
    next_probe_length,
    recipe_for_tier,
    repeat_bounds_from_history,
    unstable_lengths,
    verdict_at_length,
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


# ═══════════════════════════════════════════════════════════════════════════════
# D-077 — the repeat layer, the recipe binding, and the DB firewall
#
# NOTE ON WHAT IS AND IS NOT CHANGING. The tests above are untouched and stay
# green. `bounds_from_history` remains the raw k=1 resume reconstruction and
# `next_probe_length` still raises on `bad <= good` — D-077 decision 4 explicitly
# does NOT log that raise as a defect. What is added is a REPEAT LAYER ABOVE it,
# so a non-monotone history resolves to `unstable` and never reaches
# `next_probe_length` with inverted bounds. The existing invariant on the pure
# bisection stays true; it is simply no longer the only thing standing between a
# flaky boundary and a crash.
# ═══════════════════════════════════════════════════════════════════════════════


def _runs(length: int, outcomes: list[str]) -> list[dict]:
    return [{"length": length, "outcome": o} for o in outcomes]


# ── decision 4: k = 4, inherited from the 630-aa 4-for-4 precedent ────────────

def test_k_is_four_and_is_inherited_not_tuned():
    """630 aa was ruled fatal on 4-for-4 (ARCHITECTURE.md:598-599). D-077 dec 4
    inherits that k rather than inventing one. A future session that 'tunes' k is
    changing a frozen pre-registration and must write a new entry."""
    assert K_REPEAT == 4


def test_four_consecutive_ok_required_to_raise_the_floor():
    """3 x ok at L does NOT raise `good`; the 4th does. Setting k=1 reddens this.

    This is the whole point of k: 378 MiB from the wall, a single lucky fold is
    not evidence of a routing constant.
    """
    for n in (1, 2, 3):
        hist = _runs(500, [OK] * n)
        good, _ = repeat_bounds_from_history(hist, init_good=440, init_bad=630)
        assert good == 440, f"{n} x ok must not raise the floor"

    hist = _runs(500, [OK] * 4)
    good, _ = repeat_bounds_from_history(hist, init_good=440, init_bad=630)
    assert good == 500


def test_four_consecutive_fail_required_to_lower_the_ceiling():
    """Mirror of the above. A single OOM is not proof a length is unfoldable."""
    for n in (1, 2, 3):
        hist = _runs(560, [OOM] * n)
        _, bad = repeat_bounds_from_history(hist, init_good=440, init_bad=630)
        assert bad == 630, f"{n} x oom must not lower the ceiling"

    hist = _runs(560, [OOM] * 4)
    _, bad = repeat_bounds_from_history(hist, init_good=440, init_bad=630)
    assert bad == 560


def test_mixed_outcomes_at_one_length_report_unstable_and_do_not_raise():
    """⚠ THE LOAD-BEARING TEST (order §2a).

    `ok, oom, ok, ok` at L -> verdict `unstable`, NO ValueError, `good` unchanged.
    The pre-D-077 code path raises here: bounds_from_history would set good=L on
    the first ok and bad=L on the oom, and next_probe_length(L, L) raises. That
    crash is what D-077 decision 4 says must become a REPORTABLE RESULT instead.
    """
    hist = _runs(500, [OK, OOM, OK, OK])

    assert verdict_at_length(hist, 500) == UNSTABLE

    good, bad = repeat_bounds_from_history(hist, init_good=440, init_bad=630)
    assert good == 440, "an unstable length must not raise the floor"
    assert bad == 630, "an unstable length must not lower the ceiling"

    # and the bisection can still proceed, rather than dying on inverted bounds
    assert next_probe_length(good, bad, step=8) == 535
    assert unstable_lengths(hist) == [500]


def test_the_old_path_would_have_raised_on_this_history():
    """Proof the test above is biting, not decorative: the raw k=1 reconstruction
    really does invert the bounds on the same history, which is exactly the crash
    D-077 dec 4 predicted from a card 378 MiB from its wall."""
    hist = _runs(500, [OK, OOM, OK, OK])
    good, bad = bounds_from_history(hist, init_good=440, init_bad=630)
    assert good == 500 and bad == 500          # inverted: good is not < bad
    with pytest.raises(ValueError):
        next_probe_length(good, bad, step=8)


def test_interleaved_lengths_do_not_contaminate_each_others_verdicts():
    """Outcomes are grouped per length. A probe that flattened them would let an
    OOM at 600 poison the verdict at 500."""
    hist = _runs(500, [OK] * 4) + _runs(600, [OOM] * 4)
    interleaved = [hist[i // 2] if i % 2 == 0 else hist[4 + i // 2] for i in range(8)]

    good, bad = repeat_bounds_from_history(interleaved, init_good=440, init_bad=630)
    assert (good, bad) == (500, 600)


def test_a_run_of_four_need_not_be_the_whole_history():
    """ok, ok, ok, ok, oom is four consecutive clean folds followed by a failure.
    The four-run is real, but so is the failure — the length is unstable, and the
    conservative reading wins."""
    hist = _runs(500, [OK, OK, OK, OK, OOM])
    assert verdict_at_length(hist, 500) == UNSTABLE
    good, _ = repeat_bounds_from_history(hist, init_good=440, init_bad=630)
    assert good == 440


def test_repeat_bounds_are_deterministic_on_the_same_history():
    """D-077 dec 4: re-running with the same JSONL history must be deterministic."""
    hist = _runs(500, [OK] * 4) + _runs(560, [OOM] * 4) + _runs(520, [OK, OOM])
    first = repeat_bounds_from_history(hist, 440, 630)
    for _ in range(5):
        assert repeat_bounds_from_history(hist, 440, 630) == first


def test_error_outcomes_count_as_failures_like_oom():
    """A driver fault is a failure for routing purposes, same as an OOM — the
    existing k=1 path already treats them alike (bounds_from_history)."""
    hist = _runs(560, [ERROR] * 4)
    _, bad = repeat_bounds_from_history(hist, init_good=440, init_bad=630)
    assert bad == 560


def test_malformed_rows_are_ignored_by_the_repeat_layer_too():
    """A torn final line from a crash must not manufacture or destroy a verdict."""
    hist = _runs(500, [OK] * 4) + [{"length": None, "outcome": OK}, {}, {"outcome": OOM}]
    good, bad = repeat_bounds_from_history(hist, 440, 630)
    assert (good, bad) == (500, 630)


# ── decision 3: the recipe is resolved from TIER_RECIPE, never hand-passed ────

def test_probe_resolves_local_recipe_from_tier_recipe():
    """The local probe takes dtype/chunk_size from TIER_RECIPE['local'], not from
    the CLI default. Reverting to the fp16 default reddens this.

    The failure this prevents: a ceiling measured at fp16 written into the
    constant that routes int8 production folds.
    """
    from core.contracts import TIER_RECIPE

    assert recipe_for_tier("local") == TIER_RECIPE["local"]
    assert recipe_for_tier("local")["dtype"] == "int8"
    assert recipe_for_tier("local")["chunk_size"] == 64


def test_probe_refuses_a_recipe_that_contradicts_the_tier():
    """`--dtype fp16` with `--tier local` raises. Removing the check reddens it."""
    with pytest.raises(ValueError, match="contradict|fp16|local"):
        recipe_for_tier("local", dtype="fp16")
    with pytest.raises(ValueError, match="contradict|chunk"):
        recipe_for_tier("local", chunk_size=16)

    # restating the tier's own values is not a contradiction
    assert recipe_for_tier("local", dtype="int8", chunk_size=64)["dtype"] == "int8"


def test_probe_refuses_an_unknown_tier():
    with pytest.raises(ValueError):
        recipe_for_tier("laptop")


# ── decision 5: the probe cannot reach the reported cohort ───────────────────

def test_probe_module_imports_no_database_session():
    """⚠ Static assertion over the module's imports — no session, no persistence.

    If a probe fold ever landed in `protein_analyses`, `/api/coverage`'s folded
    count would move and F-004's denominator 56 would move with it, from a
    measurement that exists only to decide where to run things. That is D-075's
    Corruption 2 in a new costume.

    Proven by revert: add `from db.session import ...` to ceiling_probe and watch
    this redden. It is a static parse, not an import-time check, so it catches the
    import even if it sits inside a function.

    ⚠ WHAT THE REVERT PROOF ACTUALLY SHOWED, stated precisely (D-016). Reverting
    with `from db.session import SessionLocal` — a module that does not exist —
    produces a collection ERROR, because this test module imports
    `worker.ceiling_probe` at the top like every other test here. The gate goes
    red, but THIS test's assertion never runs, so that revert proves nothing about
    this guard. Re-proven with `from db import models`, which is importable and is
    the realistic mistake (someone reaching for the ORM to persist a probe result):
    the module imports cleanly, the static parse runs, and the assertion fails with
    "probe imports 'db'". That is the proof.

    The path is resolved from the REPO LAYOUT rather than by importing the module,
    so the parse does not depend on the module being importable — but an
    unimportable import still surfaces as a collection error rather than as this
    failure. Both are red; only one is this test speaking.
    """
    probe = Path(__file__).resolve().parent.parent / "worker" / "ceiling_probe.py"
    source = probe.read_text(encoding="utf-8")
    tree = ast.parse(source)

    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)

    banned = ("db", "sqlalchemy", "psycopg", "alembic")
    for mod in imported:
        root = mod.split(".")[0]
        assert root not in banned, f"probe imports {mod!r} — it must hold no database path"

    for helper in ("persist_results", "create_ranking_run", "SessionLocal", "get_session"):
        assert helper not in source, f"probe references {helper!r} — persistence must be unreachable"
