"""D-082 layer 3 — fold in a child process, so a hard death becomes a job result.

⚠⚠ **IT DOES NOT SURVIVE A BUGCHECK. NOTHING DOES.** Layer 3 converts every failure *short* of a
host death — a segfault, a CUDA driver reset, an allocator abort, an OOM the process cannot recover
from — from **"the worker vanished at row 812"** into a **named, recorded job outcome** with the
crank still running. That is its whole claim, and it is stated narrowly on purpose.

## ⚠ Why a PERSISTENT child, and not a child per fold

`runner._MODEL_CACHE` is module-level and therefore **per-process**. A child spawned per fold would
reload **8.4 GB of weights every time** — the exact cost `_MODEL_CACHE` was added to remove (weights
were reloading once per target on the first rental run, `Loading weights: 4498` per fold). So the
child is **long-lived**: spawned once, model loaded on its first fold, reused for every fold after.

⚠ **And that means only ONE model copy exists.** The parent never imports torch, never touches CUDA,
and holds no weights — so this does **not** double VRAM the way a probe running beside a worker
would.

## ⚠ What it deliberately does NOT change

**The fold itself.** The child calls `runner.fold` with the same arguments the parent would have
passed, so the same recipe produces the same structure. ⚠ **A determinism verdict measured in-process
must still hold through the supervisor**, and `test_the_supervisor_does_not_change_the_fold` is the
guard — a layer that changed results would be a worse defect than the one it prevents.

## ⚠ The failure vocabulary, and why `died` is not `failed`

A fold that **raises** is a `FoldError` and the job fails normally — unchanged. A child that **dies**
returns `FoldChildDied` carrying the **exit code**, because *"the process is gone"* and *"the fold
returned an error"* are different facts, and D-024's rule that attempted-and-failed must be
distinguishable from never-attempted applies one level down. ⚠ **A death is not retried
automatically** — a crash loop that re-folds the thing that killed it is how one bad row takes a
whole tranche with it.
"""

from __future__ import annotations

import multiprocessing as mp
from dataclasses import dataclass
from typing import Any, Optional

#: ⚠ `spawn`, explicitly. Windows has no fork, and a forked CUDA context is undefined behaviour on
#: every platform — naming it here stops a future reader "fixing" it to the faster default.
_CTX = "spawn"

#: How long to wait for one fold before treating the child as hung. ⚠ Generous: a 440 aa int8 fold
#: measured ~75 s, and a timeout that fires on a slow fold would manufacture failures.
DEFAULT_TIMEOUT_S = 900.0


class FoldChildDied(RuntimeError):
    """⚠ The child process died rather than returning. Carries the exit code.

    **Distinct from `FoldError`**, which means the fold ran and raised. A death is evidence about
    the *process*, not about the protein — and conflating them would let a driver reset read as
    *"this sequence cannot be folded."*
    """


@dataclass
class ChildResult:
    """What the child sends back. ⚠ Exactly one of `payload` / `error` is set."""
    payload: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    error_type: Optional[str] = None

    def __post_init__(self) -> None:
        if (self.payload is None) == (self.error is None):
            raise ValueError("a ChildResult carries exactly one of payload or error")


def _child_main(req_q, res_q) -> None:  # pragma: no cover — runs only in the spawned process
    """The child loop. ⚠ Imports torch lazily, exactly as `runner.fold` does, so the PARENT never
    loads CUDA and only one process ever holds the weights."""
    from worker.runner import fold as _fold

    while True:
        req = req_q.get()
        if req is None:                       # ⚠ the only clean shutdown path
            return
        try:
            r = _fold(req["sequence"], dtype=req["dtype"], chunk_size=req["chunk_size"],
                      source=req["source"], ecd_start=req.get("ecd_start"),
                      ecd_end=req.get("ecd_end"))
            prov = r.provenance
            res_q.put(ChildResult(payload={
                "pdb": r.pdb, "plddt": list(r.plddt), "pae": r.pae,
                # ⚠ The provenance travels as a dict: a dataclass pickled across a spawn boundary
                # binds the child's class definition, and a schema change would then fail at
                # UNPICKLE time in the parent — far from the change that caused it.
                "provenance": prov.__dict__ if prov is not None else None,
            }))
        except BaseException as e:            # noqa: BLE001 — the child must never die on a fold
            res_q.put(ChildResult(error=f"{type(e).__name__}: {e}"[:600],
                                  error_type=type(e).__name__))


class FoldSupervisor:
    """Spawns the fold child on first use and keeps it. ⚠ Restart is EXPLICIT, never automatic."""

    def __init__(self, *, timeout_s: float = DEFAULT_TIMEOUT_S) -> None:
        self._timeout_s = timeout_s
        self._ctx = mp.get_context(_CTX)
        self._proc: Optional[Any] = None
        self._req: Optional[Any] = None
        self._res: Optional[Any] = None
        self.deaths = 0

    def start(self) -> None:
        if self._proc is not None and self._proc.is_alive():
            return
        self._req, self._res = self._ctx.Queue(), self._ctx.Queue()
        self._proc = self._ctx.Process(target=_child_main, args=(self._req, self._res), daemon=True)
        self._proc.start()

    def stop(self) -> None:
        if self._proc is None:
            return
        try:
            if self._proc.is_alive():
                self._req.put(None)
                self._proc.join(timeout=30)
                if self._proc.is_alive():
                    self._proc.terminate()
        finally:
            self._proc = None

    def fold(self, sequence: str, *, dtype: str, chunk_size: Optional[int], source: str,
             ecd_start: Optional[int] = None, ecd_end: Optional[int] = None) -> dict[str, Any]:
        """One fold, in the child. Returns the payload dict, or raises.

        ⚠ **`FoldChildDied` when the process is gone; the original exception type by name when the
        fold merely raised.** The caller can tell a driver reset from a bad sequence, which is the
        entire reason this layer exists.
        """
        self.start()
        self._req.put({"sequence": sequence, "dtype": dtype, "chunk_size": chunk_size,
                       "source": source, "ecd_start": ecd_start, "ecd_end": ecd_end})
        try:
            res: ChildResult = self._res.get(timeout=self._timeout_s)
        except Exception:                     # noqa: BLE001 — Empty, or the queue died with the child
            alive = self._proc is not None and self._proc.is_alive()
            code = None if alive else getattr(self._proc, "exitcode", None)
            self.deaths += 1
            self.stop()
            # ⚠ NOT retried here. A crash loop that re-folds the thing that killed it is how one
            # bad row takes a whole tranche with it. The caller records and moves on.
            raise FoldChildDied(
                f"the fold child {'is hung past ' + str(self._timeout_s) + 's' if alive else 'died'}"
                f"{'' if alive else f' with exitcode {code}'} — the fold produced no result. "
                f"⚠ This is a fact about the PROCESS, not about the sequence.")
        if res.error is not None:
            raise RuntimeError(f"{res.error}")     # the fold ran and raised — a normal job failure
        return res.payload
