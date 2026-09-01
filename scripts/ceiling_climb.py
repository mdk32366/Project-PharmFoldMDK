#!/usr/bin/env python3
"""D-082 step 1 — re-measure the local ceiling by CLIMBING, under the allocator cap.

    python scripts/ceiling_climb.py --accession Q8WXD0 --tier local \
        --start 248 --stop 456 --step 8 --memory-fraction 0.85 --empty-cache \
        --fold-in-child --layer1-attested

    WORKER_FOLD_IN_CHILD=1 python scripts/ceiling_climb.py --accession Q8WXD0 \
        --layer1-attested

⚠⚠ **IT CLIMBS. IT DOES NOT BISECT — and that is the lesson of the crash, not a preference.**
`worker/ceiling_probe.py` bisects, and on 2026-08-16 it jumped **209 → 313 aa**, a 50% increase with
nothing measured in between, and the host bugchecked on that jump. **Bisection's entire value is
large jumps into unmeasured territory, which is exactly what cannot be afforded here.** A climb
costs more folds; every step is bounded by the one before it.

⚠ **AND IT CANNOT RUN BEHIND `vram_guard.preflight`.** The guard refuses any length with no measured
requirement, and this is the run that *builds* those requirements — gated by them it would refuse
everything, forever. It is bounded instead by:

  1. **the allocator cap** — `set_per_process_memory_fraction` makes PyTorch raise
     `OutOfMemoryError` **in Python** at the cap, so the refusal is catchable rather than fatal;
  2. **the climb** — every step is +`--step` aa from a length already measured;
  3. ⚠ **durability** — each step is `fsync`ed **before** the next begins, because the last probe's
     append-only file came back as **55 bytes of `\\0`**: a hard reset does not flush the page cache.
  4. ⚠ **layer 3 (opt-in)** — `--fold-in-child` or `WORKER_FOLD_IN_CHILD=1` folds in a persistent
     child (D-082 / rb_local_tile_folds pattern). Cap, peak, and empty-cache run in THAT process.

⚠ `--layer1-attested` is REQUIRED. Layer 1 is owner action and cannot be read from code. Without
the flag this script refuses to climb (non-zero). Emma confirmed Matt Layer-1 ATTESTED
(2026-09-01); Kaylee passes the flag on the laptop GPU. ⚠ This script does not climb on a cloud VM.

⚠ **F-062.** A measured-success envelope is card-bound. This climb writes a *fresh* jsonl under
`data/census/` so a prior card's history cannot seed this one.

⚠⚠ **A HOST BUGCHECK FALSIFIES THE WHOLE DESIGN.** One occurrence means the three layers do not
work, and **no further fold happens on this host by any recipe** until that is understood.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Optional

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from core.contracts import TIER_RECIPE  # noqa: E402
from core.vram_guard import (  # noqa: E402
    apply_allocator_cap, cuda_memory, peak_vram, reset_peak, sysmem_fallback_state,
)

CENSUS = REPO / "data" / "census"
CACHE = CENSUS / "spancache"

OK = "ok"
OOM_CAUGHT = "oom_caught"
ERROR = "error"

#: F-062 Blackwell climb bounds (usable defaults; Kaylee may still pass them explicitly).
DEFAULT_START = 248
DEFAULT_STOP = 456
DEFAULT_STEP = 8
DEFAULT_MEMORY_FRACTION = 0.85
DEFAULT_TIER = "local"
DEFAULT_OUT = CENSUS / "ceiling_climb.int8.blackwell.jsonl"


def fold_in_child_enabled(cli_flag: bool) -> bool:
    """D-082 layer 3: `--fold-in-child` OR `WORKER_FOLD_IN_CHILD=1` (rb_local / worker.main)."""
    return bool(cli_flag) or os.environ.get("WORKER_FOLD_IN_CHILD") == "1"


def assert_layer1_attested(attested: bool) -> None:
    """⚠ Refuse rather than climb. Layer 1 cannot be verified from code (D-082)."""
    if not attested:
        raise SystemExit(
            "⚠ REFUSING TO CLIMB — --layer1-attested is required. "
            "Layer 1 (NVIDIA Sysmem Fallback Policy = Prefer No Sysmem Fallback) is owner "
            "action and cannot be read from code. Matt attested (Emma confirmed 2026-09-01); "
            "pass --layer1-attested to record that attestation on this run. Without it this "
            "script will not climb."
        )


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="python scripts/ceiling_climb.py", description=__doc__)
    ap.add_argument("--accession", required=True)
    ap.add_argument(
        "--tier", default=DEFAULT_TIER, choices=("local", "rental"),
        help="⚠ recipe RESOLVED from TIER_RECIPE, never hand-passed (D-047). "
             f"Default {DEFAULT_TIER} (F-062 Blackwell climb).",
    )
    ap.add_argument(
        "--start", type=int, default=DEFAULT_START,
        help=f"a length already known to fold (default {DEFAULT_START})",
    )
    ap.add_argument(
        "--stop", type=int, default=DEFAULT_STOP,
        help=f"last length attempted (default {DEFAULT_STOP})",
    )
    ap.add_argument(
        "--step", type=int, default=DEFAULT_STEP,
        help="⚠ 8 = REPEAT_STEP, D-077 dec 4's granularity — reused so the resolution "
             f"matches the bound being tested rather than being chosen here (default {DEFAULT_STEP})",
    )
    ap.add_argument(
        "--memory-fraction", type=float, default=DEFAULT_MEMORY_FRACTION,
        help="⚠ The cap is the ceiling of the experiment; without it the "
             f"refusal is a bugcheck rather than an exception (default {DEFAULT_MEMORY_FRACTION})",
    )
    ap.add_argument(
        "--layer1-attested", action="store_true",
        help="⚠ REQUIRED. Records the owner's Layer-1 attestation. Refuses to climb if omitted.",
    )
    ap.add_argument(
        "--empty-cache", action=argparse.BooleanOptionalAction, default=True,
        help="⚠ release the caching allocator's retained pool after each fold (default ON). "
             "The 0.85 cap refused 424 aa at ALLOCATED 6,354 MiB because RESERVED had "
             "already hit 6,916 — the cap binds on what the allocator HOLDS, and "
             "nothing in the fold path ever gave it back. --no-empty-cache to disable.",
    )
    ap.add_argument(
        "--fold-in-child", action="store_true",
        help="⚠ D-082 layer 3. Fold in a persistent child. Also honored when "
             "WORKER_FOLD_IN_CHILD=1 (same switch as rb_local_tile_folds / worker.main).",
    )
    ap.add_argument(
        "--out", default=str(DEFAULT_OUT),
        help="fresh jsonl under data/census/ (default ceiling_climb.int8.blackwell.jsonl). "
             "Refuses to append to an existing file.",
    )
    return ap


def _append_fsync(path: Path, record: dict[str, Any]) -> None:
    """⚠ Durable BEFORE the next fold. `flush()` alone leaves the record in the page cache, which
    is precisely how the previous probe's results became 55 bytes of `\\0` after a hard reset."""
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def _attempt_in_process(
    seq: str, length: int, dtype: str, chunk_size: Optional[int], empty_cache: bool,
) -> dict[str, Any]:
    from worker import runner  # noqa: PLC0415 — in-process path only

    reset_peak()
    t0 = time.time()
    rec: dict[str, Any] = {"kind": "attempt", "length": length}
    try:
        result = runner.fold(
            seq[:length], dtype=dtype, chunk_size=chunk_size, source=runner.WHOLE,
        )
        rec.update(
            outcome=OK, wall_clock_s=round(time.time() - t0, 2),
            ca_residues=len({(a.chain, a.res_seq) for a in
                             __import__("core.features", fromlist=["parse_pdb"])
                             .parse_pdb(result.pdb)}),
            mean_plddt=(result.provenance.mean_plddt if result.provenance else None),
            nvidia_driver_version=getattr(
                result.provenance, "nvidia_driver_version", None,
            ),
        )
    except Exception as e:  # noqa: BLE001
        msg = f"{type(e).__name__}: {e}"
        is_oom = (
            "out of memory" in str(e).lower()
            or type(e).__name__ == "OutOfMemoryError"
        )
        rec.update(
            outcome=(OOM_CAUGHT if is_oom else ERROR),
            wall_clock_s=round(time.time() - t0, 2), detail=msg[:400],
        )
    rec["peak_vram"] = peak_vram()
    rec["empty_cache_applied"] = bool(empty_cache)
    if empty_cache:
        # ⚠ AFTER the peak is read, or the release would erase the number it is meant to
        # explain. Timed separately: the re-allocation cost lands on the NEXT fold's
        # wall-clock, so this measures only the release itself.
        import torch  # noqa: PLC0415
        _t = time.time()
        torch.cuda.empty_cache()
        rec["empty_cache_s"] = round(time.time() - _t, 3)
        m2 = cuda_memory()
        rec["free_after_release_mib"] = m2[0] if m2 else None
    m = cuda_memory()
    rec["cuda_mem_get_info_after"] = {"free_mib": m[0], "total_mib": m[1]} if m else None
    rec["fold_in_child"] = False
    return rec


def run(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    # ⚠ FIRST. Before cache, CUDA, or any jsonl write. A missing attestation is not a climb.
    assert_layer1_attested(bool(args.layer1_attested))

    if args.step <= 0 or args.stop < args.start:
        raise SystemExit("⚠ the climb must ascend: require step > 0 and stop >= start")

    in_child = fold_in_child_enabled(bool(args.fold_in_child))

    p = CACHE / f"{args.accession}.json"
    if not p.exists():
        raise SystemExit(f"⚠ no cache entry for {args.accession} — NOT fetched; report and stop")
    seq = (json.loads(p.read_text(encoding="utf-8")).get("sequence") or {}).get("value", "")
    if len(seq) < args.stop:
        raise SystemExit(f"⚠ source is {len(seq)} aa, shorter than --stop {args.stop}")

    recipe = TIER_RECIPE[args.tier]
    dtype, chunk_size = recipe["dtype"], recipe["chunk_size"]

    out = Path(args.out)
    if out.exists():
        # ⚠ No silent resume. The previous probe resumed from a file and moved its bounds from
        # prior attempts; a stale file would seed this climb with someone else's history.
        raise SystemExit(
            f"⚠ {out} already exists — refusing to append to a prior run's history. "
            f"Move it aside deliberately."
        )

    child = None
    if in_child:
        # ⚠ Cap / peak / empty-cache in the CHILD. Applying the cap here would not bound
        # the folding process, and reading peak here would measure the wrong process.
        from worker.ceiling_climb_child import ClimbChild  # noqa: PLC0415
        child = ClimbChild()
        init = child.init(memory_fraction=args.memory_fraction)
        cap = init["cap"]
        cuda_before = init.get("cuda_mem_get_info_before")
        layer3 = {
            "applied": True,
            "how": "--fold-in-child or WORKER_FOLD_IN_CHILD=1",
            "WORKER_FOLD_IN_CHILD": os.environ.get("WORKER_FOLD_IN_CHILD"),
            "cli_fold_in_child": bool(args.fold_in_child),
        }
    else:
        # ⚠ THE CAP IS APPLIED BEFORE THE WEIGHTS LOAD. Applied after, the model is already
        # resident and the cap would bound only what remained — a cap that arrives late is not a cap.
        cap = apply_allocator_cap(args.memory_fraction)
        mem = cuda_memory()
        cuda_before = {"free_mib": mem[0], "total_mib": mem[1]} if mem else None
        layer3 = {
            "applied": False,
            "why": "folds run in THIS process — pass --fold-in-child or "
                   "WORKER_FOLD_IN_CHILD=1 (D-082 layer 3)",
            "WORKER_FOLD_IN_CHILD": os.environ.get("WORKER_FOLD_IN_CHILD"),
            "cli_fold_in_child": bool(args.fold_in_child),
        }

    header = {
        "kind": "header", "accession": args.accession, "tier": args.tier,
        "dtype": dtype, "chunk_size": chunk_size, "source_length": len(seq),
        "start": args.start, "stop": args.stop, "step": args.step,
        "memory_fraction": args.memory_fraction,
        "empty_cache": bool(args.empty_cache),
        "fold_in_child": in_child,
        "cuda_mem_get_info_before": cuda_before,
        "layers": {
            "layer1_sysmem_fallback": {
                **sysmem_fallback_state(),
                "owner_attested_set": True,
            },
            "layer2_allocator_cap": cap,
            "layer3_child_process": layer3,
        },
        "finding": "F-062",
        "note": ("⚠ The 0.85 cap was RULED BY THE OWNER with max_allocated=6527 MiB already in "
                 "hand: the pre-registration's three rows did not cover 6,527, and no fourth row "
                 "was retrofitted to fit the answer (D-041 dec 4). Recorded as a post-measurement "
                 "ruling made in the open, not as a pre-registered row firing. "
                 "⚠ F-062: a measured envelope is card-bound; this jsonl is a fresh file."),
        "climbs_not_bisects": ("the prior probe jumped 209 -> 313 aa and the host bugchecked on "
                               "that jump; every step here is +step from a measured length"),
    }
    _append_fsync(out, header)
    print(json.dumps(header, indent=2))

    lengths = list(range(args.start, args.stop + 1, args.step))
    print(f"\n⚠ climbing {lengths} at dtype={dtype} chunk_size={chunk_size} "
          f"cap={args.memory_fraction} fold_in_child={in_child}\n", file=sys.stderr)

    ceiling: Optional[int] = None
    try:
        for length in lengths:
            rec: dict[str, Any]
            try:
                if child is not None:
                    rec = child.fold_length(
                        seq[:length], length=length, dtype=dtype,
                        chunk_size=chunk_size, empty_cache=bool(args.empty_cache),
                    )
                    rec["fold_in_child"] = True
                else:
                    rec = _attempt_in_process(
                        seq, length, dtype, chunk_size, bool(args.empty_cache),
                    )
            except Exception as e:  # noqa: BLE001 — child death or unexpected
                from worker.fold_supervisor import FoldChildDied as _Died  # noqa: PLC0415
                is_death = isinstance(e, _Died) or type(e).__name__ == "FoldChildDied"
                rec = {
                    "kind": "attempt", "length": length,
                    "outcome": ERROR,
                    "detail": f"{type(e).__name__}: {e}"[:400],
                    "peak_vram": {"unavailable": "child died before reporting peak"},
                    "empty_cache_applied": False,
                    "fold_in_child": in_child,
                    "child_died": is_death,
                }
            if rec.get("outcome") == OK:
                ceiling = length
            _append_fsync(out, rec)  # ⚠ durable BEFORE the next fold
            peak = rec.get("peak_vram") or {}
            print(
                f"  {length} aa -> {rec['outcome']} | {rec.get('wall_clock_s')}s | "
                f"peak_alloc {peak.get('max_allocated_mib')} MiB | "
                f"peak_reserved {peak.get('max_reserved_mib')} MiB",
                file=sys.stderr,
            )
            if rec["outcome"] != OK:
                print(
                    f"  ⚠ stopping at the first non-ok outcome: {rec['outcome']}",
                    file=sys.stderr,
                )
                break
    finally:
        if child is not None:
            child.stop()

    summary = {
        "kind": "summary", "highest_ok_length": ceiling,
        "lengths_attempted": (
            lengths[: lengths.index(ceiling) + 2] if ceiling else lengths[:1]
        ),
        "fold_in_child": in_child,
        "note": ("⚠ `highest_ok_length` is the largest length MEASURED to fold under this "
                 "cap and this stack. It is not a ceiling for any other recipe, driver, "
                 "protein or cap, and it says nothing about lengths never attempted. "
                 "⚠ F-062: it is not a licence for a different card."),
    }
    _append_fsync(out, summary)
    print(f"\n⚠ highest length measured to fold: {ceiling}")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
