# RB — local tile folds, first ten (RB4)

- **Date:** 2026-08-31 · **Status:** operational note for Task RB / RB4
- **Does not take `F-050`.** The guard-direction sweep stays RESERVED and unwritten.
- **Names:** `D-104` (routing), measured-success gate **6665 MiB** (S-005 / 2026-07-19), `F-061` (law ≠ measurement).

## What this pass is

Fold the **route=local** tiles from `data/census/tranche6_tiles.csv` on the **laptop GPU**,
recipe **int8 / chunk 64**, under `D-104`. Population: **1,482** local tiles.

**RB4** folds the first **ten**, longest-first — order key descending
`(length, census_accession, tile_index)` — and reports peak VRAM + wall clock before any
continuation. Continuation past ten requires `--continue-after-rb4` (Emma/Matt clear only).
No silent full run.

## The gate (and what it is not)

`preflight(length, "int8", 64, requirement_mib=None)` refuses everything — an absent measurement
is a category, not a green light.

The requirement this pass passes is a **MEASURED SUCCESS**, not a law:

| fact | value | where |
|---|---|---|
| measured success | 440 aa, int8, chunk 64, peak **6665 MiB** | `ARCHITECTURE.md` S-005 / 2026-07-19 |
| `requirement_mib` | **6665** | `scripts/rb_local_tile_folds.py` |
| `margin_mib` | **0** | same |
| `f059_peak_gib` | recorded on every row | tile CSV + summary |
| `f059` as `requirement_mib` | **forbidden** (`F-061`) | tests pin the call site |

Abort **BEFORE** a fold if `preflight` outcome ≠ `fits`. Never mid-fold. The batch **stops**
(non-zero); it does not skip.

If any of the ten has `|measured_peak − f059| / f059 > 0.10`, **STOP AND REPORT** — that is a
finding about the law and it outranks finishing the batch.

## KEY (for the report)

| term | meaning |
|---|---|
| which tiles | `route=local`, n=**1482** |
| routing | **D-104** (`tile_max_aa=1026`, `route_at=440`) |
| folded | structure returned under int8/chunk64 with measured peak + wall, and preflight **FIT** under the **6665 MiB** envelope |

## Hard bans (unchanged)

No rental, no RunPod, no spend, no Sentinel, no DB writes, no enqueue / sqlalchemy job queue,
no credentials paste, no merge, no push to main. Owner holds merge. **Do not take `F-050`.**

## How to run

```text
WORKER_FOLD_IN_CHILD=1 python scripts/rb_local_tile_folds.py --limit 10
```

Summary: `data/control/rb_local/rb_local_summary.csv`.

## RB4 run note (2026-08-31, laptop)

Card: NVIDIA RTX PRO 2000 Blackwell laptop GPU, 8151 MiB, driver 610.88, WDDM.
`WORKER_FOLD_IN_CHILD=1`, `apply_allocator_cap(0.85)`, gate `requirement_mib=6665`, `margin_mib=0`.

First tile under the order key: **Q96QU1 PCDH15 tile 1, 440 aa**. Preflight **FIT**. Fold raised
`FoldError: CUDA OOM` under int8/chunk 64 (allocator allowed 6.77 GiB; physical free fell to
~327 MiB mid-fold). Batch **stopped** (non-zero); did not skip.

This collides with two already-recorded facts and does not take `F-050`:

- S-005 measured success at **440 aa / 6665 MiB** was on an earlier stack/day.
- `F-059` / rental orders cite a **measured local ceiling of 432 aa** under the census recipe.

`f059` was not passed as `requirement_mib`. No rental, no spend, no DB write.

## Re-gate (F-063 envelope, L≤384)

The script now gates on this card's last OK climb peak, not S-005's 6665 MiB.
D-104 / `route_at=440` is untouched. Filter only: `route=local` AND `length≤384`.

| fact | value |
|---|---|
| local population (assert) | **1482** (`tranche6_tiles.csv`, D-104) |
| re-gate filter | **L≤384** → **1478** tiles |
| hard envelope | **`MEASURED_SUCCESS_PEAK_MIB=6357`** (F-063 last OK `peak_alloc`) |
| per-tile `requirement_mib` | climb jsonl `peak_vram.max_allocated_mib` at exact OK length (`climb_exact_L`), else 6357 (`hard_envelope_6357`) |
| `f059` as `requirement_mib` | **forbidden** (`F-061`) |
| summary (D-105) | `data/control/rb_local/rb_local_summary.regate384.procpertile.csv` |
| do **not** overwrite | `rb_local_summary.regate384.csv` (PR #201 early-stop evidence) or `rb_local_summary.csv` (RB4) |
| process | **one OS process per tile that exits** before the next parent preflight (D-105). Parent then `gc` + `empty_cache`, then preflight. STOP if free cannot meet requirement — do not skip. |

Kaylee, on MDKDevLaptop only:

```text
WORKER_FOLD_IN_CHILD=1 python scripts/rb_local_tile_folds.py --limit 10
```

Do not pass `--continue-after-rb4`. No climb. No rent. Do not take `F-050`.
Kaylee re-runs `--limit 10` only after Trinity review of the process-per-tile PR. No GPU folds in that PR.
