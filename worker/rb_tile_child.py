"""D-105 — one-shot tile fold child for the RB re-gate.

Unlike `FoldSupervisor` / `ClimbChild`, this process folds **ONE tile and EXITS**.
There is no `while True` request loop. Persistent ESMFold / allocator reserved pool
across tiles is the defect this exists to prevent (live `--limit 10` early-stop:
tile 1 `peak_reserved=6900`, tile 2 free ~1649 MiB — PR #201).

⚠ Cap, fold, peak, and artifact write happen HERE. Applying the 0.85 cap in the
parent would not cap the child; reading peak in the parent would measure the
wrong process (same invariant as `worker/ceiling_climb_child.py`).

⚠ **It does not survive a bugcheck. Nothing does.** A hard child death becomes
`FoldChildDied` with the parent alive to record the row and STOP.
"""
from __future__ import annotations

import multiprocessing as mp
import time
from typing import Any, Optional

from worker.fold_supervisor import DEFAULT_TIMEOUT_S, FoldChildDied, _CTX


def one_shot_child_main(payload: dict[str, Any], res_q) -> None:  # pragma: no cover — GPU child; CI has no CUDA
    """Fold exactly once, put one result, return. ⚠ No request loop — the process exits.

    Imports torch lazily so a parent that never calls this never loads CUDA weights.
    """
    from core.vram_guard import apply_allocator_cap, peak_vram, reset_peak  # noqa: PLC0415
    from worker.runner import fold, write_artifacts  # noqa: PLC0415

    apply_allocator_cap(float(payload["memory_fraction"]))
    reset_peak()
    t0 = time.time()
    rec: dict[str, Any] = {"ok": False}
    try:
        result = fold(
            payload["sequence"],
            dtype=payload["dtype"],
            chunk_size=payload["chunk_size"],
            source=payload["source"],
            ecd_start=payload.get("ecd_start"),
            ecd_end=payload.get("ecd_end"),
        )
        out_dir = payload.get("out_dir")
        if out_dir:
            write_artifacts(result, out_dir)
        rec.update(ok=True, wall_s=round(time.time() - t0, 2))
    except Exception as e:  # noqa: BLE001 — the child must never die on a fold
        rec.update(
            ok=False,
            error_type=type(e).__name__,
            error=f"{type(e).__name__}: {e}"[:600],
            wall_s=round(time.time() - t0, 2),
        )
    rec["peak_vram"] = peak_vram()
    res_q.put(rec)


def fold_tile_in_fresh_process(
    payload: dict[str, Any],
    *,
    target: Optional[Any] = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """Spawn a process, fold one tile, wait until that process has exited.

    `target` is the child entrypoint (default `one_shot_child_main`). Tests inject a
    stub so CI can assert a new PID per call without CUDA.

    ⚠ Returns only after `join`: the child is not alive when the caller preflights
    the next tile. A still-alive child after join is terminated and raised as
    `FoldChildDied`.
    """
    child_target = one_shot_child_main if target is None else target
    ctx = mp.get_context(_CTX)
    res_q = ctx.Queue()
    proc = ctx.Process(target=child_target, args=(payload, res_q), daemon=True)
    proc.start()
    child_pid = proc.pid
    try:
        try:
            rec = res_q.get(timeout=timeout_s)
        except Exception:  # noqa: BLE001 — Empty, or the queue died with the child
            alive = proc.is_alive()
            code = None if alive else proc.exitcode
            if alive:
                proc.terminate()
                proc.join(timeout=30)
            raise FoldChildDied(
                f"the tile child {'is hung past ' + str(timeout_s) + 's' if alive else 'died'}"
                f"{'' if alive else f' with exitcode {code}'} — the fold produced no result. "
                f"⚠ This is a fact about the PROCESS, not about the sequence."
            ) from None
    finally:
        if proc.is_alive():
            proc.join(timeout=30)
        if proc.is_alive():
            proc.terminate()
            proc.join(timeout=10)

    if proc.is_alive():
        raise FoldChildDied(
            f"the tile child pid={child_pid} did not exit after the fold — "
            f"⚠ process-per-tile requires the child to be dead before the next preflight."
        )

    if not isinstance(rec, dict):
        raise RuntimeError(f"tile child returned a non-dict: {type(rec)!r}")
    rec = dict(rec)
    rec["child_pid"] = child_pid
    rec["child_exitcode"] = proc.exitcode
    rec["child_alive"] = False
    return rec
