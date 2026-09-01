"""RB — first local tile folds under D-104. LOCAL GPU, NO INGEST, NO RENTAL.

⚠⚠ THIS SCRIPT CANNOT WRITE THE DATABASE. It imports nothing from `db/` or `core.enqueue`,
and a start-up assert refuses to run if those modules are already loaded. No Sentinel, no
job queue, no spend.

⚠⚠ F-061: `f059_peak_gib` is RECORDED on every row. It is NEVER passed as
`preflight(..., requirement_mib=...)`. The gate is a MEASURED SUCCESS — S-005 /
2026-07-19: 440 aa int8 chunk 64 peaked at 6665 MiB — not the F-059 law.

⚠ D-082 layer 3: `WORKER_FOLD_IN_CHILD=1` must be set in the environment or this script
refuses to start. Peak VRAM is read in-process via `reset_peak` /
`max_memory_allocated` (nvidia-smi alone is not the instrument).

⚠⚠ RB4: the default `--limit 10` folds the ten longest local tiles and STOPS. Continuing
past RB4 requires `--continue-after-rb4` (Emma/Matt clear only). No silent full run.
If any tile's |measured - f059| / f059 exceeds 10%, the batch STOPS (non-zero) and does
not skip.

    WORKER_FOLD_IN_CHILD=1 python scripts/rb_local_tile_folds.py
    WORKER_FOLD_IN_CHILD=1 python scripts/rb_local_tile_folds.py --limit 10
"""
from __future__ import annotations

import argparse
import csv
import gc
import os
import pathlib
import sys
import time
from datetime import datetime, timezone
from typing import Any, Optional

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

TILES = REPO / "data" / "census" / "tranche6_tiles.csv"
CACHE = REPO / "data" / "census" / "spancache"
ARTIFACT_DIR = REPO / "data" / "control" / "rb_local"
SUMMARY = ARTIFACT_DIR / "rb_local_summary.csv"

#: S-005 / 2026-07-19 measured success: 440 aa int8 chunk 64 peak 6665 MiB. NOT F-059.
MEASURED_SUCCESS_MIB = 6665
RECIPE_DTYPE = "int8"
RECIPE_CHUNK = 64
F059_DEPARTURE_STOP = 0.10
RB4_DEFAULT_LIMIT = 10
LOCAL_POPULATION = 1482
ALLOCATOR_FRACTION = 0.85

SUMMARY_FIELDS = [
    "census_accession", "gene", "tile_index", "start", "end", "length",
    "tile_cut_kind", "merge_rule", "straddle_handling", "gap_tolerance",
    "protein_regime", "route", "tile_max_aa", "route_at", "ruling",
    "trained_context", "f059_peak_gib",
    "preflight_outcome", "preflight_why", "preflight_free_mib",
    "preflight_required_mib", "preflight_margin_mib",
    "peak_allocated_mib", "peak_reserved_mib", "pct_depart_f059",
    "wall_s", "folded", "stop_reason", "folded_at",
]


def assert_no_db_reachable() -> None:
    """⚠ The guard is structural: these modules are never imported."""
    banned = [m for m in ("db.models", "core.enqueue", "sqlalchemy") if m in sys.modules]
    if banned:
        raise SystemExit(f"⚠ REFUSING TO RUN — database modules already imported: {banned}")


def assert_worker_fold_in_child() -> None:
    """⚠ D-082 layer 3. Refuse rather than fold without the switch set."""
    if os.environ.get("WORKER_FOLD_IN_CHILD") != "1":
        raise SystemExit(
            "⚠ REFUSING TO RUN — WORKER_FOLD_IN_CHILD is not 1. "
            "D-082 layer 3 requires the switch; set WORKER_FOLD_IN_CHILD=1."
        )


def sliced_sequence(acc: str, start: int, end: int) -> str:
    """1-based inclusive -> 0-based slice. Same rule as d099_control_fold."""
    import json
    path = CACHE / f"{acc}.json"
    if not path.is_file():
        raise SystemExit(f"⚠ STOP — missing spancache for {acc}: {path}")
    doc = json.loads(path.read_bytes().decode("utf-8"))
    return doc["sequence"]["value"][start - 1:end]


def load_local_tiles() -> list[dict[str, str]]:
    with TILES.open(encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("route") == "local"]
    if len(rows) != LOCAL_POPULATION:
        raise SystemExit(
            f"⚠ STOP — expected {LOCAL_POPULATION} route=local tiles, found {len(rows)}. "
            "D-104 population must match tranche6_tiles.csv."
        )
    # KEY: descending (length, census_accession, tile_index)
    rows.sort(
        key=lambda r: (int(r["length"]), r["census_accession"], int(r["tile_index"])),
        reverse=True,
    )
    return rows


def release_resident_model() -> None:
    """Restore device free toward the cold-start envelope S-005 measured under.

    Without this, preflight(requirement_mib=6665) refuses every fold after the first:
    ESMFold residency leaves ~1.5 GiB free (SB timings). The guard is unchanged
    (not F-050); only the measurement context the 6665 MiB gate assumes is restored.
    """
    import worker.runner as wr  # noqa: PLC0415
    wr._MODEL_CACHE.clear()
    gc.collect()
    try:
        import torch  # noqa: PLC0415
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
    except Exception:  # noqa: BLE001
        pass


def pct_depart(measured_mib: Optional[float], f059_gib: float) -> Optional[float]:
    if measured_mib is None or f059_gib <= 0:
        return None
    measured_gib = float(measured_mib) / 1024.0
    return abs(measured_gib - f059_gib) / f059_gib


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="RB local tile folds (D-104 / measured-success gate)")
    ap.add_argument(
        "--limit", type=int, default=RB4_DEFAULT_LIMIT,
        help=f"fold at most N tiles (default {RB4_DEFAULT_LIMIT} = RB4)",
    )
    ap.add_argument(
        "--continue-after-rb4", action="store_true",
        help="allow folding past the RB4 ten-tile check (Emma/Matt clear only)",
    )
    args = ap.parse_args(argv)

    assert_no_db_reachable()
    assert_worker_fold_in_child()

    if args.limit <= 0:
        raise SystemExit("⚠ REFUSING — --limit must be a positive integer (no silent full run)")
    if args.limit > RB4_DEFAULT_LIMIT and not args.continue_after_rb4:
        raise SystemExit(
            f"⚠ REFUSING — --limit {args.limit} exceeds RB4 default {RB4_DEFAULT_LIMIT} "
            "without --continue-after-rb4 (Emma/Matt clear only). No silent full run."
        )

    tiles = load_local_tiles()
    batch = tiles[: args.limit]

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        import torch  # noqa: PLC0415
    except ImportError as e:
        raise SystemExit(f"⚠ STOP — torch unavailable: {e}") from e
    if not torch.cuda.is_available():
        raise SystemExit("⚠ STOP — CUDA unavailable. RB local folds require the laptop GPU.")

    from core.vram_guard import (  # noqa: PLC0415 — after DB guard
        FIT, apply_allocator_cap, peak_vram, preflight, reset_peak,
    )
    from worker.runner import fold, write_artifacts  # noqa: PLC0415

    # ⚠⚠ Never pass f059 as requirement_mib. Pin the call site in tests.
    cap = apply_allocator_cap(ALLOCATOR_FRACTION)
    print(f"subjects        : {len(batch)} of {LOCAL_POPULATION} route=local (D-104)")
    print("order           : descending (length, census_accession, tile_index)")
    print(f"recipe          : {RECIPE_DTYPE} / chunk {RECIPE_CHUNK}")
    print(f"gate            : measured success {MEASURED_SUCCESS_MIB} MiB (S-005); margin_mib=0")
    print(f"allocator_cap   : {cap}")
    print(f"artifact_dir    : {ARTIFACT_DIR}")
    print(f"WORKER_FOLD_IN_CHILD={os.environ.get('WORKER_FOLD_IN_CHILD')}")
    print("ingest          : NONE — no database module is imported\n")

    rows: list[dict[str, Any]] = []
    stop_reason = ""
    exit_code = 0

    for i, t in enumerate(batch, 1):
        acc = t["census_accession"]
        gene = t["gene"]
        tile_index = int(t["tile_index"])
        start, end = int(t["start"]), int(t["end"])
        length = int(t["length"])
        f059 = float(t["f059_peak_gib"])

        seq = sliced_sequence(acc, start, end)
        if len(seq) != length:
            raise SystemExit(
                f"⚠⚠ STOP — {acc} tile {tile_index}: sliced {len(seq)} residues but "
                f"manifest says {length}. Folding this would fold a different molecule."
            )

        if i > 1:
            release_resident_model()

        pf = preflight(
            length, RECIPE_DTYPE, RECIPE_CHUNK,
            requirement_mib=MEASURED_SUCCESS_MIB,
            margin_mib=0,
            apply_cap=False,
        )
        base = {
            "census_accession": acc,
            "gene": gene,
            "tile_index": tile_index,
            "start": start,
            "end": end,
            "length": length,
            "tile_cut_kind": t.get("tile_cut_kind", ""),
            "merge_rule": t.get("merge_rule", ""),
            "straddle_handling": t.get("straddle_handling", ""),
            "gap_tolerance": t.get("gap_tolerance", ""),
            "protein_regime": t.get("protein_regime", ""),
            "route": t.get("route", "local"),
            "tile_max_aa": t.get("tile_max_aa", ""),
            "route_at": t.get("route_at", ""),
            "ruling": t.get("ruling", "D-104"),
            "trained_context": t.get("trained_context", ""),
            "f059_peak_gib": f059,
            "preflight_outcome": pf.outcome,
            "preflight_why": pf.detail,
            "preflight_free_mib": pf.free_mib,
            "preflight_required_mib": pf.required_mib,
            "preflight_margin_mib": pf.margin_mib,
            "peak_allocated_mib": "",
            "peak_reserved_mib": "",
            "pct_depart_f059": "",
            "wall_s": "",
            "folded": "no",
            "stop_reason": "",
            "folded_at": "",
        }

        print(
            f"[{i}/{len(batch)}] {acc} {gene} tile={tile_index} len={length} "
            f"f059={f059:.4f} GiB preflight={pf.outcome} ...",
            flush=True,
        )

        if pf.outcome != FIT:
            stop_reason = f"preflight_{pf.outcome}"
            base["stop_reason"] = stop_reason
            rows.append(base)
            exit_code = 1
            print(f"          -> STOP before fold: {pf.outcome}: {pf.detail}", flush=True)
            break

        reset_peak()
        t0 = time.time()
        try:
            result = fold(
                seq, dtype=RECIPE_DTYPE, chunk_size=RECIPE_CHUNK,
                source="sliced_ecd", ecd_start=start, ecd_end=end,
            )
        except Exception as e:  # noqa: BLE001
            stop_reason = f"fold_error:{type(e).__name__}"
            peak = peak_vram()
            alloc = peak.get("max_allocated_mib")
            reserved = peak.get("max_reserved_mib")
            depart = pct_depart(alloc if isinstance(alloc, (int, float)) else None, f059)
            base["stop_reason"] = stop_reason
            base["wall_s"] = round(time.time() - t0, 2)
            base["peak_allocated_mib"] = alloc if alloc is not None else ""
            base["peak_reserved_mib"] = reserved if reserved is not None else ""
            base["pct_depart_f059"] = round(depart, 6) if depart is not None else ""
            rows.append(base)
            exit_code = 1
            print(
                f"          -> STOP on fold error: {type(e).__name__}: {e} "
                f"(peak_alloc={alloc} MiB reserved={reserved} MiB)",
                flush=True,
            )
            break
        wall = time.time() - t0
        peak = peak_vram()
        alloc = peak.get("max_allocated_mib")
        reserved = peak.get("max_reserved_mib")
        depart = pct_depart(alloc if isinstance(alloc, (int, float)) else None, f059)

        out = ARTIFACT_DIR / f"{acc}_t{tile_index}"
        write_artifacts(result, out)

        base.update({
            "peak_allocated_mib": alloc if alloc is not None else "",
            "peak_reserved_mib": reserved if reserved is not None else "",
            "pct_depart_f059": round(depart, 6) if depart is not None else "",
            "wall_s": round(wall, 2),
            "folded": "yes",
            "folded_at": datetime.now(timezone.utc).isoformat(),
        })

        if depart is not None:
            print(
                f"          -> folded peak_alloc={alloc} MiB reserved={reserved} MiB "
                f"wall={wall:.1f}s pct_depart_f059={depart:.4f}",
                flush=True,
            )
        else:
            print(f"          -> folded peak_alloc={alloc} wall={wall:.1f}s", flush=True)

        if depart is not None and depart > F059_DEPARTURE_STOP:
            stop_reason = "f059_departure_gt_10pct"
            base["stop_reason"] = stop_reason
            rows.append(base)
            exit_code = 1
            print(
                f"⚠⚠ STOP — |measured-f059|/f059 = {depart:.4f} > {F059_DEPARTURE_STOP} "
                f"on {acc} tile {tile_index}. Finding about the law; outranks finishing the batch.",
                flush=True,
            )
            break

        rows.append(base)

    with SUMMARY.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=SUMMARY_FIELDS)
        w.writeheader()
        w.writerows(rows)

    n_folded = sum(1 for r in rows if r["folded"] == "yes")
    print(f"\n{'=' * 70}")
    print(f"RB KEY: tiles = route=local n={LOCAL_POPULATION}; routing = D-104")
    print(
        "folded means structure returned under int8/chunk64 with measured peak+wall "
        f"and preflight FIT under {MEASURED_SUCCESS_MIB} MiB envelope"
    )
    print(f"folded {n_folded}/{len(batch)}; stop_reason={stop_reason or '(none)'}")
    print(f"summary -> {SUMMARY}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
