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
