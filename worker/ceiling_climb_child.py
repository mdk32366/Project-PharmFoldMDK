"""D-082 layer 3 — persistent child for `scripts/ceiling_climb.py`.

The climb's measurement (allocator cap, peak VRAM, empty-cache) MUST happen in the
process that folds. `FoldSupervisor` returns a structure, not those numbers, and the
0.85 cap is per-process — applying it in the parent would not cap the child.

⚠ **The parent never imports torch.** Cap, fold, peak, and empty-cache all run here.
A child per step would reload 8.4 GB of weights every length; this child is long-lived.

⚠ **It does not survive a bugcheck. Nothing does.** A hard child death becomes
`FoldChildDied` with the parent alive to fsync the record.
"""
from __future__ import annotations

import multiprocessing as mp
import time
from typing import Any, Optional

from worker.fold_supervisor import DEFAULT_TIMEOUT_S, FoldChildDied, _CTX

OK = "ok"
OOM_CAUGHT = "oom_caught"
ERROR = "error"


def _child_main(req_q, res_q) -> None:  # pragma: no cover — GPU child; CI has no CUDA
    """⚠ Imports torch lazily. The PARENT of this module never imports torch at
    module scope (same invariant as `worker.fold_supervisor`)."""
    from core.vram_guard import (  # noqa: PLC0415
        apply_allocator_cap, cuda_memory, peak_vram, reset_peak,
    )
    from worker import runner  # noqa: PLC0415

    while True:
        req = req_q.get()
        if req is None:
            return
        op = req.get("op")
        if op == "init":
            cap = apply_allocator_cap(req["memory_fraction"])
            mem = cuda_memory()
            res_q.put({
                "ok": True,
                "cap": cap,
                "cuda_mem_get_info_before": (
                    {"free_mib": mem[0], "total_mib": mem[1]} if mem else None
                ),
            })
            continue
        if op != "fold":
            res_q.put({"ok": False, "error": f"unknown op {op!r}"})
            continue

        reset_peak()
        t0 = time.time()
        rec: dict[str, Any] = {"kind": "attempt", "length": req["length"]}
        try:
            result = runner.fold(
                req["sequence"], dtype=req["dtype"], chunk_size=req["chunk_size"],
                source=runner.WHOLE,
            )
            from core.features import parse_pdb  # noqa: PLC0415
            rec.update(
                outcome=OK,
                wall_clock_s=round(time.time() - t0, 2),
                ca_residues=len({(a.chain, a.res_seq) for a in parse_pdb(result.pdb)}),
                mean_plddt=(result.provenance.mean_plddt if result.provenance else None),
                nvidia_driver_version=getattr(
                    result.provenance, "nvidia_driver_version", None,
                ),
            )
        except Exception as e:  # noqa: BLE001 — the child must never die on a fold
            msg = f"{type(e).__name__}: {e}"
            is_oom = (
                "out of memory" in str(e).lower()
                or type(e).__name__ == "OutOfMemoryError"
            )
            rec.update(
                outcome=(OOM_CAUGHT if is_oom else ERROR),
                wall_clock_s=round(time.time() - t0, 2),
                detail=msg[:400],
            )
        rec["peak_vram"] = peak_vram()
        rec["empty_cache_applied"] = bool(req.get("empty_cache"))
        if req.get("empty_cache"):
            import torch  # noqa: PLC0415
            _t = time.time()
            torch.cuda.empty_cache()
            rec["empty_cache_s"] = round(time.time() - _t, 3)
            m2 = cuda_memory()
            rec["free_after_release_mib"] = m2[0] if m2 else None
        m = cuda_memory()
        rec["cuda_mem_get_info_after"] = (
            {"free_mib": m[0], "total_mib": m[1]} if m else None
        )
        res_q.put({"ok": True, "record": rec})


class ClimbChild:
    """Persistent climb child. ⚠ Restart is EXPLICIT, never automatic."""

    def __init__(self, *, timeout_s: float = DEFAULT_TIMEOUT_S) -> None:
        self._timeout_s = timeout_s
        self._ctx = mp.get_context(_CTX)
        self._proc: Optional[Any] = None
        self._req: Optional[Any] = None
        self._res: Optional[Any] = None

    def start(self) -> None:
        if self._proc is not None and self._proc.is_alive():
            return
        self._req, self._res = self._ctx.Queue(), self._ctx.Queue()
        self._proc = self._ctx.Process(
            target=_child_main, args=(self._req, self._res), daemon=True,
        )
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

    def _call(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.start()
        self._req.put(payload)
        try:
            res = self._res.get(timeout=self._timeout_s)
        except Exception:  # noqa: BLE001 — Empty, or the queue died with the child
            alive = self._proc is not None and self._proc.is_alive()
            code = None if alive else getattr(self._proc, "exitcode", None)
            self.stop()
            raise FoldChildDied(
                f"the climb child {'is hung past ' + str(self._timeout_s) + 's' if alive else 'died'}"
                f"{'' if alive else f' with exitcode {code}'} — the fold produced no result. "
                f"⚠ This is a fact about the PROCESS, not about the sequence."
            ) from None
        if not res.get("ok"):
            raise RuntimeError(res.get("error") or "climb child returned not-ok")
        return res

    def init(self, *, memory_fraction: float) -> dict[str, Any]:
        """Apply the allocator cap BEFORE the first fold / weights load."""
        return self._call({"op": "init", "memory_fraction": memory_fraction})

    def fold_length(
        self, sequence: str, *, length: int, dtype: str, chunk_size: Optional[int],
        empty_cache: bool,
    ) -> dict[str, Any]:
        res = self._call({
            "op": "fold",
            "sequence": sequence,
            "length": length,
            "dtype": dtype,
            "chunk_size": chunk_size,
            "empty_cache": empty_cache,
        })
        return res["record"]
