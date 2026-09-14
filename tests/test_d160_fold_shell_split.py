"""D-160 — the armed shell and the long-running shell are never the same shell.

⚠⚠ **THE HAZARD, AND IT IS THE ONE BOTH INCIDENTS REQUIRED.** `fold()` called
`refuse_on_strangers` → `_engine()` → `os.environ["DATABASE_URL"]` — a **subscript**, so without a
tunnel the fold raised `KeyError` and never started. The fold therefore had to be launched from a
tunnel-armed shell, **and that shell then stayed armed for the ten hours of unattended folding.**

⚠ **And the script header said the opposite.** *"The fold needs NO TUNNEL"* was written before
PR #306 added the stranger guard to the fold path on 2026-09-13 and was never updated. An operator
following it hits the `KeyError`, and the nearest fix to hand is `source .env` — which re-arms the
shell. **A safety instruction that is false in the direction of the hazard is worse than none.**

⚠ `os.environ.pop` was considered and rejected as the whole answer: it protects the *process*, and
the *shell* is the hazard. The invocation is split instead.
"""

from __future__ import annotations

import importlib
import inspect
import json
from pathlib import Path

import pytest

from scripts.task4_slice1 import (
    CLEARANCE_MAX_AGE_S,
    clearance_path,
    clearance_refusal,
    fold_shell_refusal,
    verify_clearance,
    write_clearance,
)

REPO = Path(__file__).resolve().parent.parent
IDS = [101, 102, 103]
TIER = "local"


def _record(ids=IDS, tier=TIER):
    return {"cleared_at": 0.0, "tier": tier, "job_ids": sorted(ids)}


# ── ⚠⚠ RED 1: the fold shell must not be armed ──────────────────────────────────────────────────

def test_a_fold_shell_carrying_DATABASE_URL_is_REFUSED():
    """⚠⚠ The condition both truncation incidents required, refused at the first opportunity."""
    reason = fold_shell_refusal({"DATABASE_URL": "postgresql://u:p@127.0.0.1:16380/pharmfoldmdk"})
    assert reason is not None
    assert "REFUSING" in reason
    assert "2026-08-17" in reason and "2026-09-13" in reason


def test_a_clean_fold_shell_proceeds():
    assert fold_shell_refusal({"WORKER_AUTH_TOKEN": "x"}) is None
    assert fold_shell_refusal({}) is None


def test_an_empty_DATABASE_URL_is_not_treated_as_armed():
    """⚠ `DATABASE_URL=` exports an empty string. Refusing on that would teach the operator that
    the guard is noise, which is how a guard gets worked around rather than obeyed."""
    assert fold_shell_refusal({"DATABASE_URL": ""}) is None


def test_the_refusal_tells_the_operator_what_to_do_INSTEAD_of_sourcing_dot_env():
    """⚠⚠ This is the sentence that prevents the recovery move that caused the incident. A refusal
    with no alternative is a refusal that gets solved with `source .env`."""
    reason = fold_shell_refusal({"DATABASE_URL": "x"})
    assert "WORKER_AUTH_TOKEN" in reason
    assert "preflight" in reason
    assert "source .env" in reason and "Do NOT" in reason


def test_the_shell_check_is_the_FIRST_thing_fold_does():
    """⚠ Order matters: an armed shell is the defect itself, so it must be reported before three
    other refusals send the operator looking somewhere else."""
    src = inspect.getsource(importlib.import_module("scripts.task4_slice3").fold)
    assert src.index("fold_shell_refusal") < src.index("ENQUEUED_JSON.is_file"), (
        "the fold checks its enqueue file before it checks whether the shell is armed")


# ── ⚠⚠ RED 2/3/4: the clearance must exist, be fresh, and match ─────────────────────────────────

def test_a_missing_clearance_REFUSES():
    reason = verify_clearance(None, IDS, TIER, 0.0)
    assert reason is not None and "preflight" in reason


def test_a_STALE_clearance_REFUSES():
    """⚠⚠ **A stale clear is not a clear.** `run_worker` claims the next job of its TIER, not
    'one of mine', so a stranger enqueued between the check and the fold is precisely what the
    guard exists to catch."""
    assert verify_clearance(_record(), IDS, TIER, CLEARANCE_MAX_AGE_S + 1) is not None
    assert verify_clearance(_record(), IDS, TIER, CLEARANCE_MAX_AGE_S - 1) is None


def test_a_clearance_for_a_DIFFERENT_POPULATION_REFUSES():
    reason = verify_clearance(_record(ids=[101, 102]), IDS, TIER, 0.0)
    assert reason is not None and "different population" in reason


def test_a_clearance_taken_at_a_DIFFERENT_TIER_REFUSES():
    """⚠ `F-046`: a guard that checks `local` while the run claims `rental` is protecting a queue
    that will not be drained."""
    reason = verify_clearance(_record(tier="rental"), IDS, TIER, 0.0)
    assert reason is not None and "tier" in reason


def test_a_fresh_matching_clearance_PROCEEDS():
    assert verify_clearance(_record(), IDS, TIER, 10.0) is None


# ── the round trip, on disk ─────────────────────────────────────────────────────────────────────

def test_the_clearance_round_trips_and_is_refused_once_stale(tmp_path):
    path = write_clearance(tmp_path, TIER, IDS)
    assert path == clearance_path(tmp_path) and path.is_file()
    rec = json.loads(path.read_text(encoding="utf-8"))
    assert rec["tier"] == TIER and rec["job_ids"] == sorted(IDS)
    assert "cleared_at_iso" in rec, "a clearance a human cannot date is one nobody audits"

    assert clearance_refusal(tmp_path, IDS, TIER) is None
    stale = clearance_refusal(tmp_path, IDS, TIER, now=rec["cleared_at"] + CLEARANCE_MAX_AGE_S + 60)
    assert stale is not None


def test_a_missing_clearance_file_refuses_rather_than_raising(tmp_path):
    """⚠ Fail closed and legibly. A traceback is not a refusal — an operator reads a traceback as
    a broken tool and reaches for the thing that made it work last time."""
    assert clearance_refusal(tmp_path, IDS, TIER) is not None


# ── ⚠ the split is real: the fold path no longer touches a database ─────────────────────────────

def test_the_fold_does_NOT_call_the_stranger_guard_and_the_PREFLIGHT_does():
    """⚠⚠ **The guard was not dropped — it MOVED.** Asserting only that the fold stopped calling it
    would be satisfied by deleting the check altogether, which is the failure this pair prevents."""
    slice3 = importlib.import_module("scripts.task4_slice3")
    fold_src = inspect.getsource(slice3.fold)
    pre_src = inspect.getsource(slice3.preflight)

    assert "refuse_on_strangers" not in fold_src, (
        "the fold still calls the stranger guard, which reaches _engine() and therefore "
        "DATABASE_URL — the fold shell would have to be armed again")
    assert "refuse_on_strangers" in pre_src, "the stranger check was dropped, not moved"
    assert "write_clearance" in pre_src, "the preflight does not record its verdict"
    assert "clearance_refusal" in fold_src, "the fold does not consume the preflight's verdict"


def test_the_fold_reaches_no_engine_at_all():
    """⚠ The property in one assertion: nothing on the fold path can build a database engine."""
    fold_src = inspect.getsource(importlib.import_module("scripts.task4_slice3").fold)
    assert "_engine(" not in fold_src
    assert "DATABASE_URL" not in fold_src.replace("fold_shell_refusal", "")


def test_the_cli_exposes_preflight():
    src = (REPO / "scripts" / "task4_slice3.py").read_text(encoding="utf-8")
    assert '"--preflight"' in src and "return preflight()" in src


# ── ⚠⚠ the stale header, corrected in the same PR ───────────────────────────────────────────────

@pytest.mark.parametrize("rel", ["scripts/task4_slice1.py", "scripts/task4_slice3.py"])
def test_no_script_header_still_claims_the_fold_needs_no_tunnel_without_qualifying_it(rel):
    """⚠⚠ **The header is the defect that nearly reconstructed the incident**, so it is asserted
    rather than trusted. Both files carried the bare claim; PR #306 made it false in both and
    updated neither.

    ⚠ The claim is allowed to survive *qualified* — the fold LOOP really does need no tunnel, and
    deleting that fact would be its own kind of false. What must not survive is the bare form.
    """
    head = (REPO / rel).read_text(encoding="utf-8").split('"""')[1]
    if "NO TUNNEL" in head.upper():
        # ⚠⚠ The qualification must name `--preflight`, THE FLAG. The bare word "preflight"
        # is not enough and this assertion was written that way first: slice 1's header already
        # says "the preflight and the GPU are local", meaning the VRAM preflight, so the loose
        # check passed on a header that was still false. A guard satisfied by an unrelated word
        # is a guard that reports success — the exact shape this entry exists to close.
        assert "--preflight" in head, (
            f"{rel}'s header repeats the unqualified no-tunnel claim. The fold LOOP needs none; "
            f"the STRANGER preflight does, and an operator who hits that KeyError reaches for "
            f"`source .env` — which re-arms the shell for the whole unattended run.")
