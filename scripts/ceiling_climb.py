#!/usr/bin/env python3
"""D-082 step 1 — re-measure the local ceiling by CLIMBING, under the allocator cap.

    python scripts/ceiling_climb.py --accession Q8WXD0 --tier local \
        --start 416 --stop 456 --step 8 --memory-fraction 0.85 --layer1-attested

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

⚠ **LAYER 3 IS OPT-IN via `--fold-in-child` / `WORKER_FOLD_IN_CHILD=1`.** Default remains
in-process (stated, not implied). When enabled, each step uses `FoldSupervisor` so a death is
`FoldChildDied`, not silent; the allocator cap and peak stats run **in the child** because both
are per-process. Durability (fsync per step) stays either way.

⚠ **`--layer1-attested` is REQUIRED to climb.** Without the owner's Prefer No Sysmem Fallback
attestation for this python.exe, the script refuses — a spill-to-sysmem path turns VRAM overflow
into a host bugcheck rather than a catchable exception.

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


def _append_fsync(path: Path, record: dict[str, Any]) -> None:
    """⚠ Durable BEFORE the next fold. `flush()` alone leaves the record in the page cache, which
    is precisely how the previous probe's results became 55 bytes of `\\0` after a hard reset."""
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def run(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="python scripts/ceiling_climb.py", description=__doc__)
    ap.add_argument("--accession", required=True)
    ap.add_argument("--tier", required=True, choices=("local", "rental"),
                    help="⚠ recipe RESOLVED from TIER_RECIPE, never hand-passed (D-047)")
    ap.add_argument("--start", type=int, required=True, help="a length already known to fold")
    ap.add_argument("--stop", type=int, required=True)
    ap.add_argument("--step", type=int, default=8,
                    help="⚠ 8 = REPEAT_STEP, D-077 dec 4's granularity — reused so the resolution "
                         "matches the bound being tested rather than being chosen here")
    ap.add_argument("--memory-fraction", type=float, required=True,
                    help="⚠ REQUIRED. The cap is the ceiling of the experiment; without it the "
                         "refusal is a bugcheck rather than an exception")
    ap.add_argument("--layer1-attested", action="store_true")
    ap.add_argument("--empty-cache", action="store_true",
                    help="⚠ release the caching allocator's retained pool after each fold. The "
                         "0.85 cap refused 424 aa at ALLOCATED 6,354 MiB because RESERVED had "
                         "already hit 6,916 — the cap binds on what the allocator HOLDS, and "
                         "nothing in the fold path ever gave it back")
    ap.add_argument("--fold-in-child", action="store_true",
                    help="⚠ D-082 layer 3: fold each step via FoldSupervisor. Also honored when "
                         "WORKER_FOLD_IN_CHILD=1 is set in the environment.")
    ap.add_argument("--out", default=str(CENSUS / "ceiling_climb.int8.jsonl"))
    args = ap.parse_args(argv)

    if args.step <= 0 or args.stop < args.start:
        raise SystemExit("⚠ the climb must ascend: require step > 0 and stop >= start")

    # ⚠ REQUIRED to climb. Recorded-only was the prior contract; F-062 / Emma now refuse without it.
    if not args.layer1_attested:
        raise SystemExit(
            "⚠ REFUSING TO CLIMB — --layer1-attested is required. "
            "Owner must attest Prefer No Sysmem Fallback for this python.exe first."
        )

    fold_in_child = bool(args.fold_in_child) or (os.environ.get("WORKER_FOLD_IN_CHILD") == "1")
    if args.fold_in_child and os.environ.get("WORKER_FOLD_IN_CHILD") != "1":
        # ⚠ Make the env match the flag so nested tooling sees the same switch RB requires.
        os.environ["WORKER_FOLD_IN_CHILD"] = "1"

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
        raise SystemExit(f"⚠ {out} already exists — refusing to append to a prior run's history. "
                         f"Move it aside deliberately.")

    # ⚠ Cap must bind the process that folds. In-process: apply here before weights load.
    # Fold-in-child: apply inside the child on first fold (FoldSupervisor memory_fraction).
    cap: dict[str, Any]
    if fold_in_child:
        cap = {
            "applied": False,
            "deferred_to_child": True,
            "fraction": args.memory_fraction,
            "covers": "the PyTorch caching allocator only (applied in FoldSupervisor child)",
            "does_not_cover": ("cuBLAS/cuDNN workspaces, the CUDA context, and any allocation "
                               "that bypasses the caching allocator"),
        }
        mem_before = None  # parent must not import torch when folding in a child
    else:
        cap = apply_allocator_cap(args.memory_fraction)
        mem_before = cuda_memory()

    header = {
        "kind": "header", "accession": args.accession, "tier": args.tier,
        "dtype": dtype, "chunk_size": chunk_size, "source_length": len(seq),
        "start": args.start, "stop": args.stop, "step": args.step,
        "memory_fraction": args.memory_fraction,
        "empty_cache": bool(args.empty_cache),
        "fold_in_child": fold_in_child,
        "card": {
            "name": "NVIDIA RTX PRO 2000 Blackwell Generation Laptop GPU",
            "total_mib_nominal": 8151,
            "driver": "610.88",
            "wddm": True,
            "rented": False,
        },
        "cuda_mem_get_info_before": ({"free_mib": mem_before[0], "total_mib": mem_before[1]}
                                     if mem_before else None),
        "layers": {
            "layer1_sysmem_fallback": {**sysmem_fallback_state(),
                                       "owner_attested_set": bool(args.layer1_attested)},
            "layer2_allocator_cap": cap,
            "layer3_child_process": (
                {"applied": True, "via": "FoldSupervisor",
                 "WORKER_FOLD_IN_CHILD": os.environ.get("WORKER_FOLD_IN_CHILD")}
                if fold_in_child else
                {"applied": False, "why": "folds run in THIS process — stated, not implied"}
            ),
        },
        "note": ("⚠ The 0.85 cap was RULED BY THE OWNER with max_allocated=6527 MiB already in "
                 "hand: the pre-registration's three rows did not cover 6,527, and no fourth row "
                 "was retrofitted to fit the answer (D-041 dec 4). Recorded as a post-measurement "
                 "ruling made in the open, not as a pre-registered row firing."),
        "climbs_not_bisects": ("the prior probe jumped 209 -> 313 aa and the host bugchecked on "
                               "that jump; every step here is +step from a measured length"),
    }
    _append_fsync(out, header)
    print(json.dumps(header, indent=2))

    from core.vram_guard import f059_peak_gib  # noqa: PLC0415 — recorder only; never requirement_mib

    supervisor = None
    fold_fn = None
    if fold_in_child:
        from worker.fold_supervisor import FoldSupervisor, FoldChildDied  # noqa: PLC0415
        supervisor = FoldSupervisor()
        supervisor.start()

        def fold_fn(sequence: str):  # type: ignore[misc]
            return supervisor.fold(
                sequence, dtype=dtype, chunk_size=chunk_size, source="whole",
                memory_fraction=args.memory_fraction, empty_cache=bool(args.empty_cache),
            )
    else:
        from worker import runner  # noqa: PLC0415

        def fold_fn(sequence: str):  # type: ignore[misc]
            return runner.fold(sequence, dtype=dtype, chunk_size=chunk_size, source=runner.WHOLE)

    lengths = list(range(args.start, args.stop + 1, args.step))
    print(f"\n⚠ climbing {lengths} at dtype={dtype} chunk_size={chunk_size} "
          f"cap={args.memory_fraction} fold_in_child={fold_in_child}\n", file=sys.stderr)

    ceiling: Optional[int] = None
    measured_success_peak_mib: Optional[int] = None
    try:
        for length in lengths:
            if not fold_in_child:
                reset_peak()
            t0 = time.time()
            rec: dict[str, Any] = {"kind": "attempt", "length": length}
            f059 = f059_peak_gib(length)
            rec["f059_peak_gib"] = round(f059, 6)
            rec["f059_peak_mib"] = round(f059 * 1024, 2)
            try:
                result = fold_fn(seq[:length])
                wall = round(time.time() - t0, 2)
                if fold_in_child:
                    # payload dict from FoldSupervisor
                    peak = result.get("peak_vram") or {}
                    prov = result.get("provenance") or {}
                    rec.update(
                        outcome=OK, wall_clock_s=wall,
                        mean_plddt=prov.get("mean_plddt"),
                        nvidia_driver_version=prov.get("nvidia_driver_version"),
                        free_before_mib=result.get("free_before_mib"),
                        empty_cache_applied=bool(args.empty_cache),
                        empty_cache_s=result.get("empty_cache_s"),
                        free_after_release_mib=result.get("free_after_release_mib"),
                    )
                else:
                    peak = peak_vram()
                    rec.update(
                        outcome=OK, wall_clock_s=wall,
                        ca_residues=len({(a.chain, a.res_seq) for a in
                                         __import__("core.features", fromlist=["parse_pdb"])
                                         .parse_pdb(result.pdb)}),
                        mean_plddt=(result.provenance.mean_plddt if result.provenance else None),
                        nvidia_driver_version=getattr(result.provenance, "nvidia_driver_version",
                                                      None),
                    )
                    rec["empty_cache_applied"] = bool(args.empty_cache)
                    if args.empty_cache:
                        import torch  # noqa: PLC0415
                        _t = time.time()
                        torch.cuda.empty_cache()
                        rec["empty_cache_s"] = round(time.time() - _t, 3)
                        m2 = cuda_memory()
                        rec["free_after_release_mib"] = m2[0] if m2 else None
                rec["peak_vram"] = peak
                alloc = peak.get("max_allocated_mib") if isinstance(peak, dict) else None
                if isinstance(alloc, (int, float)) and f059 > 0:
                    rec["pct_depart_f059"] = round(abs((alloc / 1024.0) - f059) / f059, 6)
                ceiling = length
                if isinstance(alloc, (int, float)):
                    measured_success_peak_mib = int(alloc)
            except Exception as e:  # noqa: BLE001
                msg = f"{type(e).__name__}: {e}"
                is_child_died = type(e).__name__ == "FoldChildDied" or "FoldChildDied" in type(e).__name__
                is_oom = ("out of memory" in str(e).lower()
                          or type(e).__name__ == "OutOfMemoryError"
                          or "OutOfMemoryError" in str(e))
                peak = getattr(e, "peak_vram", None)
                if peak is None and not fold_in_child:
                    peak = peak_vram()
                rec["peak_vram"] = peak if peak is not None else {}
                alloc = (peak or {}).get("max_allocated_mib") if isinstance(peak, dict) else None
                if isinstance(alloc, (int, float)) and f059 > 0:
                    rec["pct_depart_f059"] = round(abs((alloc / 1024.0) - f059) / f059, 6)
                outcome = "fold_child_died" if is_child_died else (OOM_CAUGHT if is_oom else ERROR)
                rec.update(outcome=outcome, wall_clock_s=round(time.time() - t0, 2),
                           detail=msg[:400])
                if fold_in_child:
                    rec["empty_cache_applied"] = bool(args.empty_cache)

            if not fold_in_child:
                m = cuda_memory()
                rec["cuda_mem_get_info_after"] = {"free_mib": m[0], "total_mib": m[1]} if m else None

            _append_fsync(out, rec)  # ⚠ durable BEFORE the next fold
            peak = rec.get("peak_vram") or {}
            print(f"  {length} aa -> {rec['outcome']} | {rec.get('wall_clock_s')}s | "
                  f"peak_alloc {peak.get('max_allocated_mib')} MiB | "
                  f"peak_reserved {peak.get('max_reserved_mib')} MiB | "
                  f"f059 {rec.get('f059_peak_mib')} MiB | "
                  f"pct_depart {rec.get('pct_depart_f059')}", file=sys.stderr)
            if rec["outcome"] != OK:
                print(f"  ⚠ stopping at the first non-ok outcome: {rec['outcome']}", file=sys.stderr)
                break
    finally:
        if supervisor is not None:
            supervisor.stop()

    summary = {
        "kind": "summary",
        "highest_ok_length": ceiling,
        "MEASURED_SUCCESS_PEAK_MIB": measured_success_peak_mib,
        "lengths_attempted": (
            lengths[: lengths.index(ceiling) + 2] if ceiling in lengths else lengths[:1]
        ),
        "fold_in_child": fold_in_child,
        "layer1_attested": bool(args.layer1_attested),
        "note": ("⚠ `highest_ok_length` is the largest length MEASURED to fold under this "
                 "cap and this stack. It is not a ceiling for any other recipe, driver, "
                 "protein or cap, and it says nothing about lengths never attempted. "
                 "MEASURED_SUCCESS_PEAK_MIB is peak_allocated_mib at highest_ok on THIS card."),
    }
    _append_fsync(out, summary)
    print(f"\n⚠ highest length measured to fold: {ceiling}")
    print(f"MEASURED_SUCCESS_PEAK_MIB: {measured_success_peak_mib}")
    print(f"wrote {out}")
    return 0



if __name__ == "__main__":
    raise SystemExit(run())
