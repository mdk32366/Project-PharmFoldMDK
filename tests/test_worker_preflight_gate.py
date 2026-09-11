"""The DB-writing fold path gets the envelope gate the harness always had.

⚠⚠ THE ASYMMETRY THIS CLOSES, AND IT PREDATES TODAY. The only fold path that can write Run 2
rows (`worker/main.py` -> `fold_from_spec`) called `preflight` **nowhere**; the only path with
the gate (`scripts/rb_local_tile_folds.py`) **refuses to start if `db/` is imported**. So every
worker-path fold on this host has run **ungated** — on the card whose host bugchecked (`F-063`),
with `F-064`'s post-fold headroom collapse open beside it.

⚠ `preflight`'s own contract is the argument: *"`None` means no measurement exists, and that is a
REFUSAL, not a permission — a length with no curve is routed out rather than tried. Guessing it
is how a host gets rebooted."*

⚠⚠ A REFUSAL IS NOT A FAILURE, AND THE RECORD MUST SAY WHICH. *Routed out, no measurement* and
*attempted and failed* need different investigations — the same reason
`core/fold_persistence_check.py` returns four named outcomes rather than a boolean. An absent
measurement recorded as a fold failure is `F-018`'s shape.

⚠ `margin_mib=0` matches the harness exactly. A margin here that the harness does not have would
be `F-046`: divergent parameters under one name.
"""
from __future__ import annotations

import pytest

from core.vram_guard import (
    FIT,
    MEASURED_SUCCESS_PEAK_MIB,
    REFUSED_INSUFFICIENT_HEADROOM,
    REFUSED_NO_MEASUREMENT,
    Preflight,
    requirement_for_length,
)
from worker.main import FoldRefused, fold_from_spec
from worker.orchestrator import FoldError, FoldSpec
from worker.runner import MODEL_REVISION


def _spec(**kw) -> FoldSpec:
    base = dict(job_id=42, sequence="MKT", model_revision=MODEL_REVISION, dtype="int8",
                chunk_size=64, source="sliced_ecd", ecd_start=1, ecd_end=3)
    base.update(kw)
    return FoldSpec(**base)


class _Result:
    def __init__(self):
        self.pae = None


def _folds(*_a, **_k):
    return _Result()


def _must_not_fold(*_a, **_k):
    raise AssertionError("the gate let a refused fold through to the GPU")


def _preflight(outcome, detail="", **kw):
    def fn(length, dtype, chunk_size, *, requirement_mib, margin_mib, **_):
        fn.seen = dict(length=length, dtype=dtype, chunk_size=chunk_size,
                       requirement_mib=requirement_mib, margin_mib=margin_mib)
        return Preflight(outcome=outcome, length=length, dtype=dtype, chunk_size=chunk_size,
                         free_mib=kw.get("free_mib"), total_mib=kw.get("total_mib"),
                         required_mib=requirement_mib, margin_mib=margin_mib,
                         memory_fraction=0.85, layers={}, detail=detail)
    fn.seen = None
    return fn


# ── the gate REFUSES, which is the half a happy-path test would miss ─────────────────────────

def test_an_insufficient_headroom_refusal_stops_the_fold_before_the_gpu():
    """⚠⚠ THE ASSERTION THE WHOLE CHANGE EXISTS FOR. `F-062` is FIT-then-OOM: the fold was
    attempted on an envelope that did not apply. Refusing must happen BEFORE `fold_fn`."""
    pf = _preflight(REFUSED_INSUFFICIENT_HEADROOM, "needs 6357 + 0 = 6357 MiB, only 1649 free")
    with pytest.raises(FoldRefused) as e:
        fold_from_spec(_spec(), _must_not_fold, preflight_fn=pf)
    assert "1649" in str(e.value) or "6357" in str(e.value)


def test_an_absent_measurement_is_a_refusal_not_a_permission():
    """⚠ `preflight`'s contract, asserted: a length with no curve is routed out, not tried."""
    pf = _preflight(REFUSED_NO_MEASUREMENT, "no measured VRAM requirement for this length")
    with pytest.raises(FoldRefused):
        fold_from_spec(_spec(), _must_not_fold, preflight_fn=pf)


# ── a refusal must be DISTINGUISHABLE from a failure ─────────────────────────────────────────

def test_a_refusal_is_distinguishable_from_an_attempted_and_failed_fold():
    """⚠⚠ `FoldRefused` is a `FoldError` — so the loop's existing deterministic-failure taxonomy
    is unchanged — but it is its OWN type and its message carries a stable marker, so the
    recorded `jobs.error` says *routed out* rather than *tried and broke*. Those need different
    investigations; conflating them is `F-018`'s shape in the job record."""
    pf = _preflight(REFUSED_NO_MEASUREMENT, "no measurement")
    with pytest.raises(FoldRefused) as refused:
        fold_from_spec(_spec(), _must_not_fold, preflight_fn=pf)

    def explodes(*_a, **_k):
        raise FoldError("CUDA OOM folding 377 aa")

    with pytest.raises(FoldError) as failed:
        fold_from_spec(_spec(), explodes, preflight_fn=_preflight(FIT))

    assert isinstance(refused.value, FoldError), "the loop's taxonomy must still see a FoldError"
    assert not isinstance(failed.value, FoldRefused), "an OOM must NOT read as a refusal"
    assert FoldRefused.MARKER in str(refused.value)
    assert FoldRefused.MARKER not in str(failed.value)


# ── the parameters must match the harness exactly ────────────────────────────────────────────

def test_the_gate_uses_the_measured_requirement_and_a_zero_margin():
    """⚠ `margin_mib=0` is the harness's value. ⚠⚠ And the requirement is MEASURED — the climb
    peak at the exact length, else the F-063 hard envelope. **Never F-059**, which `F-061` bars
    as a law rather than a measurement of the case in front of it."""
    pf = _preflight(FIT)
    fold_from_spec(_spec(sequence="A" * 377, ecd_start=1, ecd_end=377), _folds, preflight_fn=pf)
    assert pf.seen["margin_mib"] == 0, "a margin the harness does not have is F-046's shape"
    assert pf.seen["length"] == 377
    assert pf.seen["dtype"] == "int8" and pf.seen["chunk_size"] == 64
    expected, source = requirement_for_length(377)
    assert pf.seen["requirement_mib"] == expected == MEASURED_SUCCESS_PEAK_MIB
    assert source == "hard_envelope_6357"


def test_a_fit_lets_the_fold_proceed():
    """⚠ The happy path, and it is the LEAST informative test here — a gate that never says no
    is decorative, which is why the refusals above come first."""
    out = fold_from_spec(_spec(), _folds, preflight_fn=_preflight(FIT))
    assert isinstance(out, _Result)


def test_without_a_preflight_fn_the_path_is_ungated_and_that_is_recorded():
    """⚠⚠ THE RESIDUAL, ASSERTED. An un-injected call still folds — CI has no CUDA, and
    `preflight` refuses when free VRAM cannot be read, so an unconditional gate would refuse
    every test fold. The guarantee is therefore the WIRING, asserted below, not the default."""
    assert fold_from_spec(_spec(), _folds) is not None


def test_run_wires_the_gate_into_the_fold_path():
    """⚠⚠ Same shape as the PAE-route wiring guard: a correct gate that production never calls
    is `F-054`. Asserted behaviourally by capturing what `run()` hands the loop."""
    from worker import main as worker_main

    captured: dict = {}
    tripped: list = []

    class _FakeClient:
        def persist_pae(self, job_id, pae_gz):
            pass

    def fake_run_worker(client, fold_callable, worker_id, **kw):
        captured["fold_callable"] = fold_callable

    def spy_preflight(length, dtype, chunk_size, *, requirement_mib, margin_mib, **_):
        tripped.append((length, requirement_mib, margin_mib))
        return Preflight(outcome=FIT, length=length, dtype=dtype, chunk_size=chunk_size,
                         free_mib=7043, total_mib=8151, required_mib=requirement_mib,
                         margin_mib=margin_mib, memory_fraction=0.85, layers={}, detail="")

    real_build = worker_main.build_client
    worker_main.build_client = lambda cfg: _FakeClient()          # noqa: E731
    try:
        cfg = worker_main.WorkerConfig(transport_url="http://unused", auth_token="t",
                                       worker_id="w", artifact_dir=None)
        worker_main.run(cfg, fold_fn=_folds, run_worker_fn=fake_run_worker,
                        preflight_fn=spy_preflight)
    finally:
        worker_main.build_client = real_build

    captured["fold_callable"](_spec(sequence="A" * 100, ecd_start=1, ecd_end=100))
    assert tripped, "run() does not hand the preflight gate to the fold path — folds run ungated"
    assert tripped[0][2] == 0, "the wired margin is not the harness's zero"
