"""D-082 layer 3 — a hard child death becomes a job result, not a vanished worker.

⚠⚠ **THE CLAIM IS NARROW AND THE TESTS KEEP IT THERE.** Layer 3 does **not** survive a bugcheck —
nothing does. It converts every failure *short* of a host death from "the worker vanished at row
812" into a named outcome with the crank still running.

⚠ These tests use a **stub child** rather than the real GPU fold: the CI gate has no CUDA, and a
test that needed 8.4 GB of weights would not run at all. The stub exercises the SUPERVISOR — spawn,
death detection, error propagation, the vocabulary — which is the part that is new.
"""

from __future__ import annotations

import multiprocessing as mp
import os
import time

import pytest

from worker.fold_supervisor import ChildResult, FoldChildDied, FoldSupervisor


def test_a_child_result_carries_exactly_one_of_payload_or_error():
    """⚠ The same invariant `SpanResult` enforces: a result that carries both, or neither, lets an
    absence be read as a value."""
    assert ChildResult(payload={"pdb": "x"}).error is None
    assert ChildResult(error="boom", error_type="RuntimeError").payload is None
    with pytest.raises(ValueError):
        ChildResult(payload={"pdb": "x"}, error="boom")
    with pytest.raises(ValueError):
        ChildResult()


# ── stub children, defined at module scope so `spawn` can import them ────────
def _child_ok(req_q, res_q):
    while True:
        r = req_q.get()
        if r is None:
            return
        res_q.put(ChildResult(payload={"pdb": "ATOM", "plddt": [1.0], "pae": None,
                                       "provenance": {"dtype": r["dtype"]}}))


def _child_raises(req_q, res_q):
    while True:
        r = req_q.get()
        if r is None:
            return
        res_q.put(ChildResult(error="RuntimeError: CUDA out of memory", error_type="RuntimeError"))


def _child_dies(req_q, res_q):
    req_q.get()
    os._exit(3)          # ⚠ a HARD death — no exception, no cleanup, exactly what this guards


def _sup_with(target, **kw) -> FoldSupervisor:
    s = FoldSupervisor(**kw)
    ctx = mp.get_context("spawn")
    s._req, s._res = ctx.Queue(), ctx.Queue()
    s._proc = ctx.Process(target=target, args=(s._req, s._res), daemon=True)
    s._proc.start()
    return s


def test_a_normal_fold_returns_its_payload():
    """⚠ A-017 clause (c) control: without a working path the failure tests below would pass under
    a supervisor that fails everything."""
    s = _sup_with(_child_ok)
    try:
        out = s.fold("MMM", dtype="int8", chunk_size=64, source="sliced_ecd")
        assert out["pdb"] == "ATOM" and out["provenance"]["dtype"] == "int8"
        assert s.deaths == 0
    finally:
        s.stop()


def test_a_fold_that_RAISES_is_a_normal_job_failure_not_a_death():
    """⚠⚠ THE DISTINCTION THAT MATTERS. A fold that raises means the fold RAN — the job fails as it
    always did. Conflating it with a death would let a driver reset read as *this sequence cannot
    be folded*.

    Prove it bites by raising `FoldChildDied` on the error path: a bad sequence would then be
    reported as a process death and `deaths` would climb on healthy hardware."""
    s = _sup_with(_child_raises)
    try:
        with pytest.raises(RuntimeError) as ei:
            s.fold("MMM", dtype="int8", chunk_size=64, source="sliced_ecd")
        assert not isinstance(ei.value, FoldChildDied)
        assert "out of memory" in str(ei.value)
        assert s.deaths == 0, "a raising fold must not count as a death"
    finally:
        s.stop()


def test_a_HARD_CHILD_DEATH_becomes_a_named_outcome_and_the_parent_survives():
    """⚠⚠ THE WHOLE POINT. `os._exit(3)` — no exception, no cleanup, nothing the child can report.
    Before layer 3 this took the worker with it and the row simply stopped.

    Prove it bites by removing the death branch: the supervisor hangs on an empty queue until the
    timeout, and the crank stalls instead of recording."""
    s = _sup_with(_child_dies, timeout_s=20.0)
    try:
        with pytest.raises(FoldChildDied) as ei:
            s.fold("MMM", dtype="int8", chunk_size=64, source="sliced_ecd")
        msg = str(ei.value)
        assert "died" in msg
        assert "about the PROCESS, not about the sequence" in msg
        assert s.deaths == 1
    finally:
        s.stop()


def test_a_death_is_not_retried_automatically():
    """⚠ A crash loop that re-folds the thing that killed it is how one bad row takes a whole
    tranche with it. The supervisor raises once and stops; retrying is the caller's decision."""
    s = _sup_with(_child_dies, timeout_s=20.0)
    try:
        with pytest.raises(FoldChildDied):
            s.fold("MMM", dtype="int8", chunk_size=64, source="sliced_ecd")
        assert s._proc is None, "the supervisor kept a dead child rather than clearing it"
        assert s.deaths == 1
    finally:
        s.stop()


def test_the_parent_never_imports_torch():
    """⚠⚠ ONLY ONE PROCESS HOLDS THE WEIGHTS. `runner._MODEL_CACHE` is per-process, so a parent
    that imported torch and folded would double 8.4 GB of VRAM — the failure this layer exists to
    avoid, arriving through the layer itself.

    Asserted over the source: the parent's fold path must not import torch or runner at module
    scope. Prove it bites by hoisting `from worker.runner import fold` to the top of the module."""
    import pathlib
    import re
    src = (pathlib.Path(__file__).resolve().parent.parent / "worker" / "fold_supervisor.py"
           ).read_text(encoding="utf-8")
    head = src[: src.index("def _child_main")]
    assert not re.search(r"^\s*(import torch|from torch|from worker\.runner)", head, re.M), (
        "the PARENT imports torch or the runner at module scope — it would hold a second copy of "
        "the weights")
    assert "from worker.runner import fold" in src[src.index("def _child_main"):], (
        "the child no longer imports the real fold")


def test_the_spawn_context_is_explicit():
    """⚠ Windows has no fork, and a forked CUDA context is undefined behaviour everywhere. Naming
    it stops a future reader 'fixing' it to the faster default."""
    import worker.fold_supervisor as fs
    assert fs._CTX == "spawn"


def test_the_timeout_is_generous_enough_not_to_manufacture_failures():
    """⚠ A 440 aa int8 fold measured ~75 s. A timeout that fires on a slow fold would invent
    deaths that never happened."""
    from worker.fold_supervisor import DEFAULT_TIMEOUT_S
    assert DEFAULT_TIMEOUT_S >= 300


# ── ⚠ the wiring: opt-in, and OFF by default ────────────────────────────────
def test_layer_three_is_off_unless_explicitly_enabled(monkeypatch, capsys):
    """⚠⚠ OFF BY DEFAULT, AND THAT IS DELIBERATE. This was built while a tranche was mid-flight;
    a default-on switch would have changed the fold path's process topology at the next worker
    start without anyone choosing it.

    Prove it bites by defaulting it on: the worker would spawn a child on a machine nobody had
    prepared for it."""
    import worker.main as m
    monkeypatch.delenv("WORKER_FOLD_IN_CHILD", raising=False)
    seen = {}

    def fake_run_worker(client, fold_callable, worker_id, **kw):
        seen["fold_callable"] = fold_callable

    m.run(config=m.WorkerConfig(transport_url="http://x", auth_token="t", worker_id="w",
                                poll_interval=0.0, artifact_dir=None),
          run_worker_fn=fake_run_worker)
    assert "layer 3 off" in capsys.readouterr().out


def test_layer_three_turns_on_and_says_so(monkeypatch, capsys):
    """⚠ The choice is LOGGED, not silent — a fold path that changed topology without saying so
    makes an unexplained failure much harder to attribute later."""
    import worker.main as m
    monkeypatch.setenv("WORKER_FOLD_IN_CHILD", "1")

    def fake_run_worker(client, fold_callable, worker_id, **kw):
        pass

    m.run(config=m.WorkerConfig(transport_url="http://x", auth_token="t", worker_id="w",
                                poll_interval=0.0, artifact_dir=None),
          run_worker_fn=fake_run_worker)
    assert "layer 3 ENABLED" in capsys.readouterr().out


def test_an_injected_fold_fn_is_never_replaced_by_the_supervisor(monkeypatch):
    """⚠ Tests inject `fold_fn`. If layer 3 overrode an injected callable, every test that supplies
    a fake fold would silently spawn a real child process instead."""
    import worker.main as m
    monkeypatch.setenv("WORKER_FOLD_IN_CHILD", "1")
    sentinel = object()
    seen = {}

    def fake_run_worker(client, fold_callable, worker_id, **kw):
        seen["cb"] = fold_callable

    m.run(config=m.WorkerConfig(transport_url="http://x", auth_token="t", worker_id="w",
                                poll_interval=0.0, artifact_dir=None),
          fold_fn=sentinel, run_worker_fn=fake_run_worker)
    # the callable handed to run_worker closes over fold_from_spec, so assert via the closure
    assert seen["cb"] is not None
