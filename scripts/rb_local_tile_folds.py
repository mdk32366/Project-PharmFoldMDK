"""RB re-gate — local tile folds under the F-063 Blackwell envelope, L≤384.

LOCAL GPU, NO INGEST, NO RENTAL. Kaylee runs this on MDKDevLaptop; CI is code+tests only.

⚠⚠ THIS SCRIPT CANNOT WRITE THE DATABASE. It imports nothing from `db/` or `core.enqueue`,
and a start-up assert refuses to run if those modules are already loaded. No Sentinel, no
job queue, no spend.

⚠⚠ F-061: `f059_peak_gib` is RECORDED on every row. It is NEVER passed as
`preflight(..., requirement_mib=...)`. The gate is a MEASURED SUCCESS on this card —
F-063 last OK `peak_alloc` 6357 MiB at 384 aa — not the F-059 law, and not S-005's
6665 MiB (F-062: that envelope is card-bound and produced FIT-then-OOM on Blackwell).

⚠ D-082 layer 3: `WORKER_FOLD_IN_CHILD=1` must be set in the environment or this script
refuses to start. ⚠ D-105: that switch is not a persistent worker. **Each tile fold
runs in a fresh OS process that exits before the next preflight.** Peak VRAM is read
**in the child** via `reset_peak` / `max_memory_allocated` (nvidia-smi alone is not
the instrument). The parent then `gc` + `empty_cache` and preflights the next tile.

⚠ Filter is `route=local` AND `length≤384`. D-104 / `route_at=440` / `tranche6_tiles`
routing is untouched. Population assert is still 1482 local tiles; the re-gate then
drops L>384.

⚠ Default `--limit 10` folds the ten longest L≤384 local tiles and STOPS. Continuing
past that requires `--continue-after-rb4` (Emma/Matt clear only). The re-gate run
itself is `--limit 10` only — do not pass `--continue-after-rb4` for this batch.
If any tile's |measured - f059| / f059 exceeds 10%, the batch STOPS (non-zero) and does
not skip.

    WORKER_FOLD_IN_CHILD=1 python scripts/rb_local_tile_folds.py
    WORKER_FOLD_IN_CHILD=1 python scripts/rb_local_tile_folds.py --limit 10

Artifact: `data/control/rb_local/rb_local_summary.regate384.procpertile.csv`
(does NOT overwrite `rb_local_summary.regate384.csv` or `rb_local_summary.csv`).
"""
from __future__ import annotations

import argparse
import csv
import gc
import json
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
CLIMB_JSONL = REPO / "data" / "census" / "ceiling_climb.blackwell.int8.20260831.jsonl"
ARTIFACT_DIR = REPO / "data" / "control" / "rb_local"
#: D-105 path — do not overwrite the RB4 summary or the PR #201 early-stop CSV.
SUMMARY = ARTIFACT_DIR / "rb_local_summary.regate384.procpertile.csv"

#: F-063 last OK peak_alloc on Blackwell (L=384, int8/chunk 64). NOT F-059. NOT S-005 6665.
MEASURED_SUCCESS_PEAK_MIB = 6357
RECIPE_DTYPE = "int8"
RECIPE_CHUNK = 64
F059_DEPARTURE_STOP = 0.10
RB4_DEFAULT_LIMIT = 10
LOCAL_POPULATION = 1482
LOCAL_REGATE_MAX_LENGTH = 384
ALLOCATOR_FRACTION = 0.85
REQUIREMENT_SOURCE_CLIMB = "climb_exact_L"
REQUIREMENT_SOURCE_ENVELOPE = "hard_envelope_6357"

SUMMARY_FIELDS = [
    "census_accession", "gene", "tile_index", "start", "end", "length",
    "tile_cut_kind", "merge_rule", "straddle_handling", "gap_tolerance",
    "protein_regime", "route", "tile_max_aa", "route_at", "ruling",
    "trained_context", "f059_peak_gib",
    "requirement_mib", "requirement_source",
    "preflight_outcome", "preflight_why", "preflight_free_mib",
    "preflight_required_mib", "preflight_margin_mib",
    "peak_allocated_mib", "peak_reserved_mib", "pct_depart_f059",
    "wall_s", "folded", "stop_reason", "folded_at",
    "gpu_name", "nvidia_driver_version", "vram_total_mib",
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
    path = CACHE / f"{acc}.json"
    if not path.is_file():
        raise SystemExit(f"⚠ STOP — missing spancache for {acc}: {path}")
    doc = json.loads(path.read_bytes().decode("utf-8"))
    return doc["sequence"]["value"][start - 1:end]


def load_climb_ok_peaks(path: Optional[pathlib.Path] = None) -> dict[int, int]:
    """Map length → peak_vram.max_allocated_mib for each outcome=ok climb row.

    ⚠ Uses the measured allocated peak, never `f059_peak_mib` / `f059_peak_gib`.
    """
    src = path if path is not None else CLIMB_JSONL
    if not src.is_file():
        raise SystemExit(f"⚠ STOP — missing F-063 climb jsonl: {src}")
    peaks: dict[int, int] = {}
    with src.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("outcome") != "ok":
                continue
            length = rec.get("length")
            peak = rec.get("peak_vram") or {}
            alloc = peak.get("max_allocated_mib")
            if length is None or alloc is None:
                continue
            peaks[int(length)] = int(alloc)
    return peaks


def requirement_for_length(length: int, climb_peaks: dict[int, int]) -> tuple[int, str]:
    """Prefer the climb jsonl peak at the exact OK length; else the F-063 hard envelope.

    Never consults F-059. Returns (requirement_mib, requirement_source).
    """
    if length in climb_peaks:
        return int(climb_peaks[length]), REQUIREMENT_SOURCE_CLIMB
    return MEASURED_SUCCESS_PEAK_MIB, REQUIREMENT_SOURCE_ENVELOPE


def load_local_tiles() -> list[dict[str, str]]:
    """route=local, assert n=1482 (D-104), then L≤384 re-gate filter, longest-first."""
    with TILES.open(encoding="utf-8") as fh:
        local = [r for r in csv.DictReader(fh) if r.get("route") == "local"]
    if len(local) != LOCAL_POPULATION:
        raise SystemExit(
            f"⚠ STOP — expected {LOCAL_POPULATION} route=local tiles, found {len(local)}. "
            "D-104 population must match tranche6_tiles.csv."
        )
    # Re-gate filter only. Does not rewrite D-104 / route_at / tranche6_tiles routing.
    rows = [r for r in local if int(r["length"]) <= LOCAL_REGATE_MAX_LENGTH]
    # KEY: descending (length, census_accession, tile_index)
    rows.sort(
        key=lambda r: (int(r["length"]), r["census_accession"], int(r["tile_index"])),
        reverse=True,
    )
    return rows


def capture_card_identity() -> dict[str, Any]:
    """gpu_name, nvidia_driver_version, vram_total_mib. Never raises (CI has no GPU).

    Same probes as `worker.runner._capture_environment` (nvidia-smi for driver,
    torch for device name) plus `mem_get_info` total like `vram_guard.cuda_memory`.
    """
    identity: dict[str, Any] = {
        "gpu_name": None,
        "nvidia_driver_version": None,
        "vram_total_mib": None,
    }
    try:
        import subprocess  # noqa: PLC0415
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=15,
        )
        if out.returncode == 0 and out.stdout.strip():
            identity["nvidia_driver_version"] = out.stdout.strip().splitlines()[0].strip()
    except Exception:  # noqa: BLE001
        pass
    try:
        import torch  # noqa: PLC0415
        if torch.cuda.is_available():
            identity["gpu_name"] = torch.cuda.get_device_name(0)
            _free, total = torch.cuda.mem_get_info()
            identity["vram_total_mib"] = total // 2 ** 20
    except Exception:  # noqa: BLE001
        pass
    return identity


def parent_reclaim_after_child() -> None:
    """Parent-side reclaim AFTER the tile child has exited (D-105).

    The child process exiting drops that process's ESMFold + CUDA context. This
    then runs `gc` + `empty_cache` in the parent before the next preflight.
    ⚠ Does not load or clear `worker.runner._MODEL_CACHE` — the parent never
    held the weights. Not F-050.
    """
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
    ap = argparse.ArgumentParser(
        description="RB re-gate local tile folds (F-063 envelope, L≤384; D-104 routing untouched)",
    )
    ap.add_argument(
        "--limit", type=int, default=RB4_DEFAULT_LIMIT,
        help=f"fold at most N tiles (default {RB4_DEFAULT_LIMIT})",
    )
    ap.add_argument(
        "--continue-after-rb4", action="store_true",
        help="allow folding past the ten-tile check (Emma/Matt clear only); not this re-gate run",
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

    climb_peaks = load_climb_ok_peaks()
    tiles = load_local_tiles()
    batch = tiles[: args.limit]
    card = capture_card_identity()

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        import torch  # noqa: PLC0415
    except ImportError as e:
        raise SystemExit(f"⚠ STOP — torch unavailable: {e}") from e
    if not torch.cuda.is_available():
        raise SystemExit("⚠ STOP — CUDA unavailable. RB local folds require the laptop GPU.")

    from core.vram_guard import FIT, preflight  # noqa: PLC0415 — after DB guard
    from worker.fold_supervisor import FoldChildDied  # noqa: PLC0415
    from worker.rb_tile_child import fold_tile_in_fresh_process  # noqa: PLC0415

    # ⚠⚠ Never pass f059 as requirement_mib. Pin the call site in tests.
    # ⚠ D-105: the 0.85 cap is applied IN EACH TILE CHILD (per-process). Applying it
    # here would not cap the folder.
    print(
        f"subjects        : {len(batch)} of {len(tiles)} L≤{LOCAL_REGATE_MAX_LENGTH} "
        f"(from {LOCAL_POPULATION} route=local; D-104 route_at untouched)"
    )
    print("order           : descending (length, census_accession, tile_index)")
    print(f"recipe          : {RECIPE_DTYPE} / chunk {RECIPE_CHUNK}")
    print(
        f"gate            : F-063 MEASURED_SUCCESS_PEAK_MIB={MEASURED_SUCCESS_PEAK_MIB} MiB "
        f"(last OK peak_alloc); exact-L climb peak preferred; margin_mib=0"
    )
    print(
        f"allocator_cap   : fraction={ALLOCATOR_FRACTION} applied in each tile child "
        f"(D-105 process-per-tile; parent does not hold ESMFold)"
    )
    print("process         : one OS process per tile; child exits before next preflight")
    print(f"artifact        : {SUMMARY}")
    print(
        f"card            : gpu_name={card['gpu_name']} "
        f"driver={card['nvidia_driver_version']} "
        f"vram_total_mib={card['vram_total_mib']}"
    )
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
        requirement_mib, requirement_source = requirement_for_length(length, climb_peaks)

        seq = sliced_sequence(acc, start, end)
        if len(seq) != length:
            raise SystemExit(
                f"⚠⚠ STOP — {acc} tile {tile_index}: sliced {len(seq)} residues but "
                f"manifest says {length}. Folding this would fold a different molecule."
            )

        if i > 1:
            parent_reclaim_after_child()

        pf = preflight(
            length, RECIPE_DTYPE, RECIPE_CHUNK,
            requirement_mib=requirement_mib,
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
            "requirement_mib": requirement_mib,
            "requirement_source": requirement_source,
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
            "gpu_name": card["gpu_name"],
            "nvidia_driver_version": card["nvidia_driver_version"],
            "vram_total_mib": card["vram_total_mib"],
        }

        print(
            f"[{i}/{len(batch)}] {acc} {gene} tile={tile_index} len={length} "
            f"req={requirement_mib} ({requirement_source}) "
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

        out = ARTIFACT_DIR / f"{acc}_t{tile_index}"
        payload = {
            "sequence": seq,
            "dtype": RECIPE_DTYPE,
            "chunk_size": RECIPE_CHUNK,
            "source": "sliced_ecd",
            "ecd_start": start,
            "ecd_end": end,
            "out_dir": str(out),
            "memory_fraction": ALLOCATOR_FRACTION,
        }
        t0 = time.time()
        try:
            rec = fold_tile_in_fresh_process(payload)
        except FoldChildDied as e:
            stop_reason = f"fold_error:{type(e).__name__}"
            base["stop_reason"] = stop_reason
            base["wall_s"] = round(time.time() - t0, 2)
            rows.append(base)
            exit_code = 1
            print(
                f"          -> STOP on fold error: FoldChildDied: {e}",
                flush=True,
            )
            break

        peak = rec.get("peak_vram") or {}
        alloc = peak.get("max_allocated_mib")
        reserved = peak.get("max_reserved_mib")
        wall = rec.get("wall_s")
        if wall == "" or wall is None:
            wall = round(time.time() - t0, 2)
        depart = pct_depart(alloc if isinstance(alloc, (int, float)) else None, f059)

        if not rec.get("ok"):
            err_type = rec.get("error_type") or "FoldError"
            stop_reason = f"fold_error:{err_type}"
            base["stop_reason"] = stop_reason
            base["wall_s"] = wall
            base["peak_allocated_mib"] = alloc if alloc is not None else ""
            base["peak_reserved_mib"] = reserved if reserved is not None else ""
            base["pct_depart_f059"] = round(depart, 6) if depart is not None else ""
            rows.append(base)
            exit_code = 1
            print(
                f"          -> STOP on fold error: {err_type}: {rec.get('error')} "
                f"(peak_alloc={alloc} MiB reserved={reserved} MiB)",
                flush=True,
            )
            break

        base.update({
            "peak_allocated_mib": alloc if alloc is not None else "",
            "peak_reserved_mib": reserved if reserved is not None else "",
            "pct_depart_f059": round(depart, 6) if depart is not None else "",
            "wall_s": wall,
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
    print(
        f"RB KEY: tiles = route=local n={LOCAL_POPULATION} then L≤{LOCAL_REGATE_MAX_LENGTH} "
        f"n={len(tiles)}; routing = D-104 (untouched)"
    )
    print(
        "folded means structure returned under int8/chunk64 with measured peak+wall "
        f"and preflight FIT under per-tile requirement (envelope {MEASURED_SUCCESS_PEAK_MIB} MiB)"
    )
    print(f"folded {n_folded}/{len(batch)}; stop_reason={stop_reason or '(none)'}")
    print(f"summary -> {SUMMARY}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
