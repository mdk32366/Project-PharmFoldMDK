"""The stranger guard, shared by every slice runner.

⚠⚠ WHY THIS EXISTS. `run_worker` claims the next job of its TIER, not "one of mine". Task 3's
runner refuses to start when a claimable job sits outside its population; neither slice runner
inherited that, and slice 2's 517-row campaign was bounded only by a MANUAL check run at 05:42.

> ⚠ A manual check before a 517-row campaign is the discipline the guard exists to replace. It
> was the structural check that caught the three `tier: None` mucins — not someone remembering.

⚠⚠ AND THE PREDICATE MUST BE TIER-STRICT, NOT NULL-ONLY. That was the original error, corrected
in the Task 3 runner: a pending `rental` job is exactly as unclaimable by a local worker as a
NULL-tier one, for the same three-valued-logic reason `core/queue.py`'s claim documents.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts import task4_slice1 as S1   # noqa: E402
from scripts import task4_slice2 as S2   # noqa: E402


def _queue(jobs):
    """(job_id, accession, tier, status) rows through the real models."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from db.models import Base, JobRecord, ProteinAnalysis

    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with Session(eng) as s:
        for jid, acc, tier, status in jobs:
            a = ProteinAnalysis(id=jid * 10, input_type="uniprot", input_value=acc, meta={})
            s.add(a)
            s.flush()
            s.add(JobRecord(id=jid, analysis_id=a.id, status=status, tier=tier,
                            inference_settings={}))
        s.commit()
    return eng


def _call(eng, allowed, tier="local"):
    from sqlalchemy.orm import Session

    with Session(eng) as s:
        return S1.strangers(s, set(allowed), tier)


def test_a_claimable_job_outside_the_population_BLOCKS():
    """⚠⚠ THE WHOLE POINT. `run_worker` would claim this and fold it into a bounded campaign."""
    eng = _queue([(1, "MINE", "local", "pending"), (2, "STRANGER", "local", "pending")])
    assert _call(eng, {1}) == {2: "STRANGER"}


def test_a_NULL_tier_pending_job_does_NOT_block():
    """⚠ The three mucins. `core/queue.py`: a NULL-tier job is claimed by NOBODY, deliberately —
    refusing on one refuses on a job that could never have been folded."""
    eng = _queue([(1, "MINE", "local", "pending"), (2, "Q685J3", None, "pending")])
    assert _call(eng, {1}) == {}


def test_a_pending_job_of_ANOTHER_TIER_does_not_block_either():
    """⚠⚠ NULL-only was the original error. A rental job is as unreachable from a local worker as
    a NULL-tier one, and blocking on it would stop a campaign that was never at risk."""
    eng = _queue([(1, "MINE", "local", "pending"), (2, "RENTALJOB", "rental", "pending")])
    assert _call(eng, {1}) == {}


def test_a_non_pending_stranger_does_not_block():
    eng = _queue([(1, "MINE", "local", "pending"), (2, "DONE", "local", "complete")])
    assert _call(eng, {1}) == {}


def test_the_fixture_REACHED_the_guard():
    """⚠ `A-017`. Without this the three tests above could all pass against a guard that never
    queried anything — the population row must be visible to it and deliberately not reported."""
    eng = _queue([(1, "MINE", "local", "pending"), (2, "STRANGER", "local", "pending")])
    from sqlalchemy.orm import Session

    from scripts.task3_run2_folds import _claimable_pending

    with Session(eng) as s:
        seen = _claimable_pending(s, "local")
    assert seen == {1: "MINE", 2: "STRANGER"}, "the guard's own query must see both rows"
    assert _call(eng, {1}) == {2: "STRANGER"}, "and report only the one outside the population"


def test_the_guard_lives_in_ONE_place_and_slice_2_inherits_it():
    """⚠⚠ Shared machinery, not a copy — the same requirement `SliceRun` carries."""
    assert S2.strangers is S1.strangers
    src = (REPO / "scripts" / "task4_slice2.py").read_text(encoding="utf-8")
    assert "def strangers" not in src


@pytest.mark.parametrize("mod", ["task4_slice1", "task4_slice2"])
def test_both_slice_runners_actually_CALL_the_guard(mod):
    """⚠⚠ A guard that exists and is never called is the manual check with extra steps. This is
    the assertion that would have failed for slice 2's 517-row run."""
    import inspect
    import importlib

    src = inspect.getsource(importlib.import_module(f"scripts.{mod}").fold)
    assert "strangers(" in src, f"{mod}.fold does not call the stranger guard"
