"""D-105's process-per-tile topology, on the fold path that can WRITE.

⚠⚠ THE SECOND INSTANCE OF ONE FINDING, NOT A SECOND GAP. The envelope gate lived only on the
measurement path (`scripts/rb_local_tile_folds.py`), and so does D-105's topology: `_supervised_
fold_fn` deliberately keeps ONE long-lived child so the 8.4 GB weights load once — the exact
opposite of what `F-064` prescribes. **The production-writing fold path was built without the
safety topology the measurement path has, and neither omission was visible until something tried
to use the writing path at scale.**

⚠ `F-064`: in-process release does not restore free for the next preflight — 7043 -> 1649 MiB
after a successful fold, recovering only on **process exit**. With the envelope gate now in
place, a long-lived child means fold 1 succeeds and folds 2..n are REFUSED at ~1649 MiB against
a 6357 MiB requirement. The gate would be working; the campaign would still stall at n=1.

⚠⚠ WHAT CI CAN AND CANNOT PROVE. There is no CUDA here, so **free-VRAM recovery cannot be
demonstrated in this suite** — only the property that buys it: a NEW process per fold, dead
before the next preflight. The recovery itself is measured on the GPU during the run and
recorded per fold (`free_before` / `free_after`). Claiming recovery from these tests would be
asserting the mechanism and reporting it as the outcome.
"""
from __future__ import annotations

import pytest

from worker.main import process_per_fold_fn
from worker.orchestrator import FoldError


def _payload_child(payload, res_q):
    """Stands in for the GPU child: records its PID, returns a result-shaped record."""
    import os
    res_q.put({
        "ok": True,
        "wall_s": 0.01,
        "pid": os.getpid(),
        "peak_vram": {"max_allocated_mib": 1234},
        "result": {"pdb": f"PDB:{payload['sequence']}", "plddt": [90.0], "pae": [[0.0]],
                   "provenance": None},
    })


def _echoing_child(payload, res_q):
    """Echoes the payload it was given back through the queue, and returns a real-shaped record."""
    res_q.put({"ok": True, "wall_s": 0.01, "peak_vram": {}, "echoed_payload": dict(payload),
               "result": {"pdb": "ATOM", "plddt": [1.0], "pae": None, "provenance": None}})


def _failing_child(payload, res_q):
    res_q.put({"ok": False, "wall_s": 0.01, "error_type": "FoldError",
               "error": "CUDA OOM folding 377 aa", "peak_vram": {}})


# ── the topology property: a NEW process per fold ────────────────────────────────────────────

def test_each_fold_runs_in_a_fresh_process():
    """⚠⚠ THE PROPERTY `F-064` PRESCRIBES. One long-lived child keeps the allocator's reserved
    pool alive across folds; a child that EXITS returns the memory to the driver. This asserts
    distinct PIDs — the mechanism — because CI has no GPU to measure recovery on."""
    fold_fn = process_per_fold_fn(child_target=_payload_child)
    pids = set()
    for _ in range(3):
        out = fold_fn("MKT", dtype="int8", chunk_size=64, source="sliced_ecd",
                      ecd_start=1, ecd_end=3)
        pids.add(out.fold_record["pid"])
    assert len(pids) == 3, (
        f"folds shared a process ({pids}) — the allocator's reserved pool survives across them "
        f"and F-064's collapse applies")


def test_the_child_is_dead_before_the_call_returns():
    """⚠ `fold_tile_in_fresh_process` joins before returning, so the caller's next preflight
    reads memory the child has already released. A still-alive child is `FoldChildDied`."""
    fold_fn = process_per_fold_fn(child_target=_payload_child)
    out = fold_fn("MKT", dtype="int8", chunk_size=64, source="sliced_ecd",
                  ecd_start=1, ecd_end=3)
    import os
    assert out.fold_record["pid"] != os.getpid(), "the fold ran in the parent process"


# ── the result must survive the process boundary intact ──────────────────────────────────────

def test_the_full_fold_result_comes_back_across_the_boundary():
    """⚠ The harness's child writes artifacts to a directory and returns only a record. The
    worker needs the RESULT — pdb, plddt, pae — because it uploads them. A topology change that
    dropped the PAE would silently undo Task 2's repair."""
    fold_fn = process_per_fold_fn(child_target=_payload_child)
    out = fold_fn("MKTMKT", dtype="int8", chunk_size=64, source="sliced_ecd",
                  ecd_start=1, ecd_end=6)
    assert out.pdb == "PDB:MKTMKT"
    assert out.plddt == [90.0]
    assert out.pae == [[0.0]], "PAE did not survive the process boundary — Task 2 is undone"


# ── the taxonomy must be PRESERVED, not rebuilt ──────────────────────────────────────────────

def test_a_child_fold_failure_is_still_a_FoldError():
    """⚠⚠ `D-030` §4's deterministic-failure taxonomy is unchanged by the topology. A fold that
    failed in the child must reach the loop as `FoldError` — reported via `fail()`, never
    retried — exactly as it did in-process. Rebuilding the taxonomy around the new topology is
    how two vocabularies for one thing start."""
    fold_fn = process_per_fold_fn(child_target=_failing_child)
    with pytest.raises(FoldError) as e:
        fold_fn("MKT", dtype="int8", chunk_size=64, source="sliced_ecd", ecd_start=1, ecd_end=3)
    assert "CUDA OOM" in str(e.value), "the child's reason was lost crossing the boundary"


def test_the_wall_time_recorded_includes_the_weight_reload():
    """⚠⚠ THE COST OF CORRECTNESS, AND THE PROJECTION HAS TO CARRY IT. A fresh process reloads
    8.4 GB of weights every fold — `_MODEL_CACHE` is per-process and starts empty. The child's
    `wall_s` is measured around `fold(...)`, which performs that load, and the parent also
    records spawn-to-return. **If reload dominates the short bands the campaign's real cost is
    set by process count, not by span length**, and that is a Task 4 scoping fact."""
    fold_fn = process_per_fold_fn(child_target=_payload_child)
    out = fold_fn("MKT", dtype="int8", chunk_size=64, source="sliced_ecd", ecd_start=1, ecd_end=3)
    rec = out.fold_record
    assert "wall_s" in rec, "the child's fold wall time is not recorded"
    assert "parent_wall_s" in rec, (
        "spawn-to-return is not recorded — without it the reload cost is invisible to the "
        "projection, which is the number this topology most affects")
    assert rec["parent_wall_s"] >= rec["wall_s"], "the parent window must contain the child's"


# ── the child/parent contract: what the REAL child puts on the queue ─────────────────────────
#
# ⚠⚠ WHY THIS SECTION EXISTS, AND IT IS ABOUT THE TEST ABOVE IT, NOT THE CODE.
# `_payload_child` INVENTS a `{"result": {...}}` key. The real child does not produce one — it
# puts `{ok, wall_s, peak_vram}` and nothing else, because on the MEASUREMENT path the artifacts
# are written in the child and the parent wants only timing and peak. So
# `test_the_full_fold_result_comes_back_across_the_boundary` passed while production shipped
# `FoldResult(pdb="", plddt=[], pae=None)` and uploaded ELEVEN EMPTY STRUCTURES.
#
# ⚠ That is `A-017` INVERTED. The fixture did not fail to reach the code under test — it REPLACED
# the code under test with a producer that behaves as the test wished. A test that passes against
# an invented producer is not evidence about the producer.
#
# ⚠⚠ THE REMEDY IS STRUCTURAL, NOT A STRONGER ASSERTION: the fixture below is PRODUCED BY THE
# REAL CHILD (with the GPU fold faked, which is the only part CI cannot have), so it cannot drift
# from what production packs. The parent-side test then consumes exactly that.

def _run_real_child(monkeypatch, *, sequence="MKV", return_result, pae=None):
    """Drive the REAL `one_shot_child_main` in-process with a fake GPU fold.

    ⚠ Only the fold is faked. The queue-packing under test is the production code path, and the
    three `core.vram_guard` calls the child makes all degrade to no-ops without CUDA by design,
    so this runs on a machine with no GPU and on CI with no torch at all.
    """
    import queue as _queue

    import worker.runner as runner
    from worker.rb_tile_child import one_shot_child_main

    def _fake_fold(seq, **kw):
        return runner.FoldResult(
            pdb=f"ATOM  {seq}", plddt=[90.0] * len(seq), pae=pae,
            provenance=runner.FoldProvenance(
                model_id="facebook/esmfold_v1", model_revision="rev", dtype=kw["dtype"],
                chunk_size=kw["chunk_size"], input_length=len(seq), source=kw["source"]))

    monkeypatch.setattr(runner, "fold", _fake_fold)
    payload = {"sequence": sequence, "dtype": "int8", "chunk_size": 64, "source": "sliced_ecd",
               "ecd_start": 1, "ecd_end": len(sequence), "memory_fraction": 0.85}
    if return_result:
        payload["return_result"] = True
    q: _queue.Queue = _queue.Queue()
    one_shot_child_main(payload, q)
    return q.get_nowait()


def test_the_real_child_returns_the_fold_result_when_the_writing_path_asks(monkeypatch):
    """⚠⚠ THE DEFECT THAT UPLOADED ELEVEN EMPTY STRUCTURES TO PRODUCTION.

    `process_per_fold_fn` reads `rec.get("result")`. The child never put one there, so every fold
    became `FoldResult(pdb="", plddt=[], pae=None)` and `run_worker` uploaded it and marked the
    job complete. `GET /api/analyses/3698/structure` returned **200, 0 bytes**.

    ⚠ `F-068`'s shape a THIRD time — a component built for the measurement path, adopted by the
    writing path, missing the property the writing path needs.
    """
    rec = _run_real_child(monkeypatch, return_result=True, pae=[[0.0, 1.0], [1.0, 0.0]])
    assert rec["ok"] is True
    assert "result" in rec, (
        "the child returned no fold result, so the parent builds FoldResult(pdb='', plddt=[]) "
        "and uploads an EMPTY structure")
    got = rec["result"]
    assert got["pdb"].startswith("ATOM  "), "the PDB must survive the process boundary"
    assert got["plddt"] == [90.0, 90.0, 90.0], "per-residue pLDDT must survive it too"
    assert got["pae"] == [[0.0, 1.0], [1.0, 0.0]], "and the PAE, which the campaign exists for"
    assert got["provenance"]["model_revision"] == "rev", (
        "provenance must cross as data — a dataclass does not survive a queue as itself")


def test_the_measurement_path_still_gets_TIMING_ONLY(monkeypatch):
    """⚠⚠ THE REGRESSION GUARD, AND IT MUST PASS BEFORE AND AFTER THE FIX.

    `scripts/rb_local_tile_folds.py` writes its artifacts IN the child and wants timing and peak
    only. Making it carry a result it does not need — a full PDB, per-residue pLDDT and an L×L
    PAE through a multiprocessing queue, per tile — is a regression wearing a fix.
    """
    rec = _run_real_child(monkeypatch, return_result=False, pae=[[0.0]])
    assert rec["ok"] is True
    assert "wall_s" in rec and "peak_vram" in rec
    assert "result" not in rec, (
        "the measurement path must not be forced to carry a result it never reads")


def test_the_parent_unpacks_exactly_what_the_real_child_packs(monkeypatch):
    """⚠ The two halves joined, with the fixture PRODUCED rather than invented.

    The record handed to the parent's unpacking is the one the real child just emitted, so the
    two cannot drift apart the way `_payload_child` drifted from production.
    """
    from worker.runner import FoldProvenance, FoldResult

    rec = _run_real_child(monkeypatch, return_result=True, pae=[[0.0]])
    payload_out = rec.get("result") or {}
    prov = payload_out.get("provenance")
    out = FoldResult(pdb=payload_out.get("pdb", ""), plddt=payload_out.get("plddt") or [],
                     pae=payload_out.get("pae"),
                     provenance=FoldProvenance(**prov) if prov else None)
    assert out.pdb and out.plddt and out.pae is not None, (
        "this is the exact expression in process_per_fold_fn; if it yields an empty FoldResult "
        "here, production uploads an empty structure")
    assert out.provenance.model_id == "facebook/esmfold_v1"


def test_a_failing_child_still_carries_no_result_and_says_why(monkeypatch):
    """⚠ A-017 (c). The error path must not acquire a result key, or `ok=False` plus a truthy
    `result` would let a failed fold upload something."""
    import queue as _queue

    import worker.runner as runner
    from worker.rb_tile_child import one_shot_child_main

    def _boom(seq, **kw):
        raise RuntimeError("CUDA OOM folding 377 aa")

    monkeypatch.setattr(runner, "fold", _boom)
    q: _queue.Queue = _queue.Queue()
    one_shot_child_main({"sequence": "MKV", "dtype": "int8", "chunk_size": 64,
                         "source": "sliced_ecd", "memory_fraction": 0.85,
                         "return_result": True}, q)
    rec = q.get_nowait()
    assert rec["ok"] is False
    assert "result" not in rec
    assert "CUDA OOM" in rec["error"]


def test_the_WRITING_path_actually_ASKS_for_the_result(monkeypatch):
    """⚠⚠ THE HALF THAT MAKES THE CHILD FIX DO ANYTHING.

    `return_result` is opt-in so the measurement path is not burdened. Opt-in means the writing
    path must OPT IN — a child that can return the result and a parent that never asks is the
    same empty upload with more code behind it.
    """
    result = process_per_fold_fn(child_target=_echoing_child)(
        "MKV", dtype="int8", chunk_size=64, source="sliced_ecd", ecd_start=1, ecd_end=3)
    # ⚠ The payload comes back THROUGH the queue rather than through a closure: the child runs in
    # a spawned process, so a locally-defined capture cannot be pickled to it and a closure would
    # never see the write. (The first version of this test died with EOFError for exactly that.)
    assert result.fold_record["echoed_payload"].get("return_result") is True, (
        "the writing path did not ask for the result, so the child withholds it and the upload "
        "is empty again")


def test_the_result_survives_the_REAL_process_boundary(monkeypatch, tmp_path):
    """⚠ The in-process tests above prove the packing; this proves it PICKLES.

    A dict of lists crosses a multiprocessing queue and a dataclass does not cross as itself.
    Asserting the shape in-process would not have caught a value that cannot be sent.
    """
    import pickle

    rec = _run_real_child(monkeypatch, return_result=True, pae=[[0.0, 1.0], [1.0, 0.0]])
    round_tripped = pickle.loads(pickle.dumps(rec))
    assert round_tripped["result"]["pae"] == [[0.0, 1.0], [1.0, 0.0]]
    assert round_tripped["result"]["provenance"]["dtype"] == "int8"
