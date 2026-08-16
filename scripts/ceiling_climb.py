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

⚠ **LAYER 3 IS ABSENT.** Folds run in THIS process, not a child. A process death loses only the
step in flight — the earlier steps are already on disk — but it is stated rather than implied.

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
    ap.add_argument("--out", default=str(CENSUS / "ceiling_climb.int8.jsonl"))
    args = ap.parse_args(argv)

    if args.step <= 0 or args.stop < args.start:
        raise SystemExit("⚠ the climb must ascend: require step > 0 and stop >= start")

    p = CACHE / f"{args.accession}.json"
    if not p.exists():
        raise SystemExit(f"⚠ no cache entry for {args.accession} — NOT fetched; report and stop")
    seq = (json.loads(p.read_text(encoding="utf-8")).get("sequence") or {}).get("value", "")
    if len(seq) < args.stop:
        raise SystemExit(f"⚠ source is {len(seq)} aa, shorter than --stop {args.stop}")

    recipe = TIER_RECIPE[args.tier]
    dtype, chunk_size = recipe["dtype"], recipe["chunk_size"]

    # ⚠ THE CAP IS APPLIED BEFORE THE WEIGHTS LOAD. Applied after, the model is already resident
    # and the cap would bound only what remained — a cap that arrives late is not a cap.
    cap = apply_allocator_cap(args.memory_fraction)

    out = Path(args.out)
    if out.exists():
        # ⚠ No silent resume. The previous probe resumed from a file and moved its bounds from
        # prior attempts; a stale file would seed this climb with someone else's history.
        raise SystemExit(f"⚠ {out} already exists — refusing to append to a prior run's history. "
                         f"Move it aside deliberately.")

    header = {
        "kind": "header", "accession": args.accession, "tier": args.tier,
        "dtype": dtype, "chunk_size": chunk_size, "source_length": len(seq),
        "start": args.start, "stop": args.stop, "step": args.step,
        "memory_fraction": args.memory_fraction,
        "cuda_mem_get_info_before": (lambda m: {"free_mib": m[0], "total_mib": m[1]} if m else None)(
            cuda_memory()),
        "layers": {
            "layer1_sysmem_fallback": {**sysmem_fallback_state(),
                                       "owner_attested_set": bool(args.layer1_attested)},
            "layer2_allocator_cap": cap,
            "layer3_child_process": {"applied": False,
                                     "why": "folds run in THIS process — stated, not implied"},
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

    from worker import runner

    lengths = list(range(args.start, args.stop + 1, args.step))
    print(f"\n⚠ climbing {lengths} at dtype={dtype} chunk_size={chunk_size} "
          f"cap={args.memory_fraction}\n", file=sys.stderr)

    ceiling: Optional[int] = None
    for length in lengths:
        reset_peak()
        t0 = time.time()
        rec: dict[str, Any] = {"kind": "attempt", "length": length}
        try:
            result = runner.fold(seq[:length], dtype=dtype, chunk_size=chunk_size,
                                 source=runner.WHOLE)
            rec.update(outcome=OK, wall_clock_s=round(time.time() - t0, 2),
                       ca_residues=len({(a.chain, a.res_seq) for a in
                                        __import__("core.features", fromlist=["parse_pdb"])
                                        .parse_pdb(result.pdb)}),
                       mean_plddt=(result.provenance.mean_plddt if result.provenance else None),
                       nvidia_driver_version=getattr(result.provenance, "nvidia_driver_version",
                                                     None))
            ceiling = length
        except Exception as e:                                    # noqa: BLE001
            msg = f"{type(e).__name__}: {e}"
            # ⚠ The catch that the bugcheck proved impossible without layers 1 and 2. If this
            # branch is reached at all, the design worked: the failure is an exception.
            is_oom = ("out of memory" in str(e).lower()
                      or type(e).__name__ == "OutOfMemoryError")
            rec.update(outcome=(OOM_CAUGHT if is_oom else ERROR),
                       wall_clock_s=round(time.time() - t0, 2), detail=msg[:400])
        rec["peak_vram"] = peak_vram()
        m = cuda_memory()
        rec["cuda_mem_get_info_after"] = {"free_mib": m[0], "total_mib": m[1]} if m else None
        _append_fsync(out, rec)                    # ⚠ durable BEFORE the next fold
        print(f"  {length} aa -> {rec['outcome']} | {rec.get('wall_clock_s')}s | "
              f"peak_alloc {rec['peak_vram'].get('max_allocated_mib')} MiB | "
              f"peak_reserved {rec['peak_vram'].get('max_reserved_mib')} MiB", file=sys.stderr)
        if rec["outcome"] != OK:
            print(f"  ⚠ stopping at the first non-ok outcome: {rec['outcome']}", file=sys.stderr)
            break

    summary = {"kind": "summary", "highest_ok_length": ceiling,
               "lengths_attempted": lengths[:lengths.index(ceiling) + 2] if ceiling else lengths[:1],
               "note": ("⚠ `highest_ok_length` is the largest length MEASURED to fold under this "
                        "cap and this stack. It is not a ceiling for any other recipe, driver, "
                        "protein or cap, and it says nothing about lengths never attempted.")}
    _append_fsync(out, summary)
    print(f"\n⚠ highest length measured to fold: {ceiling}")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
