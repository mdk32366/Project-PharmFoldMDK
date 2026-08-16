# PRE-REGISTRATION — 2026-08-16 — `empty_cache()` between folds, and what the local ceiling is worth

> **Written BEFORE the change and before the measurement.** Governed by `### D-082`. Where this file
> and the log differ, **THE LOG GOVERNS.** ⚠ This file is provenance, not authority.
>
> ⚠ **VOID IF CODE PRECEDES IT.** At this commit `empty_cache` appears **0 times** in
> `worker/runner.py`, `scripts/ceiling_climb.py` and `scripts/determinism_control.py`.

**Provenance (D-016):** every figure is Code's reading from
`data/census/ceiling_climb.int8.jsonl` (capped) and `.uncapped.jsonl`, both under driver **610.88**.

---

## §1 — What is being tested, and why it is not a tuning tweak

⚠ **The 0.85 cap refused 424 aa at `allocated` 6,354 MiB — far below the 6,928 MiB cap — because
`reserved` had already reached 6,916.** `set_per_process_memory_fraction` limits what the caching
allocator **holds**, and the retained pool counts.

```
                  allocated      reserved      cap 0.85 = 6,928
  440 aa            6,664         7,072        ⚠ UNDER on demand, OVER on cache
```

**So the capped ceiling of 416 was never a statement about what a fold needs.** ⚠ It was a statement
about what the allocator had not given back — and `empty_cache` appears **0 times** anywhere in the
fold path, while `free_after` read **0 MiB** on four of five uncapped steps.

⚠⚠ **THE CRANK IS THE WORST CASE FOR THIS: thousands of sequential folds in one process.**

## §2 — ⚠ Why this is the configuration that finds the ceiling SAFELY

**Neither existing configuration can:**

| | Protection | Can it find the ceiling? |
|---|---|---|
| capped, no release | layer 2 active | ⚠ **no** — binds on cache at 416 |
| uncapped | ⚠ **layer 2 inactive** | yes, but unprotected — and the last unprotected probe **bugchecked the host** |
| **capped + release** | layer 2 active | ⚠ **this is the question** |

⚠ **If the cap binds on demand once the pool is released, this becomes the only configuration that
measures the ceiling while protected.** That is the point of the exercise, not the milliseconds.

## §3 — ⚠ THE STAKE, measured off the manifest before the change

**3,467 foldable rows. What a higher local ceiling is worth, in rows that move off rental:**

```
ceiling 416 aa | local 2,641 | rental 826 |  −50 vs 440
ceiling 440 aa | local 2,691 | rental 776 |    0  (today's constant)
ceiling 456 aa | local 2,718 | rental 749 |  +27   ← measured to fold, uncapped
ceiling 480 aa | local 2,759 | rental 708 |  +68
ceiling 500 aa | local 2,800 | rental 667 | +109
ceiling 520 aa | local 2,852 | rental 615 | +161
ceiling 630 aa | local 3,042 | rental 425 | +351
```

⚠ **The prize is bounded and it is smaller than it looks.** Demand grew **~5.8 MiB/residue** over
416–456, so:

```
cap 0.85  = 6,928 MiB -> demand reaches it at ~485 aa
free VRAM = 7,043 MiB -> demand reaches it at ~505 aa
```

⚠⚠ **EXTRAPOLATION, NOT MEASUREMENT.** 5.8 MiB/residue was linear over a 40-residue window and the
trunk's triangular attention is **O(L³)**. **It is a forecast to be tested and it may be optimistic.**
If it holds, the realistic prize is **~+109 rows off rental (667 rather than 776)** — worthwhile,
**not transformative**, and nowhere near the 630 aa figure the untested band implies.

## §4 — THE FORECAST, as a composition, before the first fold

**Change:** `torch.cuda.empty_cache()` after each fold, in the climb instrument only.
⚠ **NOT in `worker/runner.py`** — the fold path is not touched by a measurement.

**Arm: capped 0.85 + release, climbing 416 → 520 in +8 steps.**

```
PREDICTED
  424-456 aa      ok        ⚠ these five already fold UNCAPPED; if the release works the cap
                            stops binding on cache and they fold capped too
  reserved        ⚠ falls toward allocated after each release — the DIRECT test
  first refusal   ~485 aa   ⚠ from the extrapolation above, and it is the number under test
  wall-clock      ⚠ DELIBERATELY NOT FORECAST — I have no basis for the re-allocation cost
```

**⚠ The reading on wall-clock is fixed now, since it is the rental-cost half:**

| Δ per fold | Over 3,467 folds | Reading |
|---|---|---|
| **< 2 s** | < 2 h | **free.** Adopt the release unconditionally |
| **2–10 s** | 2–10 h | ⚠ pays for itself if the ceiling rises enough to move >100 rows off rental |
| **> 10 s** | > 10 h | ⚠⚠ **the release costs more than the rental it saves.** Cap and rent instead |

**⚠ Three outcomes for the ceiling, and the reading is fixed:**

1. **capped+release reaches ≥456** → the cap was binding on cache; ⚠ **confirmed, and the safe
   configuration exists**
2. **capped+release still stops near 416** → ⚠ the retained pool was *not* the constraint and my
   diagnosis in `076a7f6` is **wrong** — the cap binds on something `empty_cache` does not release
3. **capped+release stops between 456 and 485** → the release works and the extrapolation is
   roughly right; the ceiling is the measurement

## §5 — ⚠ What would falsify this, and what halts it

- ⚠⚠ **A host bugcheck.** Layer 2 is active in this arm, so a host death means **the cap does not
  protect either** — and no further fold happens on this machine by any recipe.
- **An `OutOfMemoryError` that is not caught** — the process dies rather than raising.
- ⚠ **A ceiling that lands where the capped-no-release run already stopped (416)** — that refutes
  the `076a7f6` diagnosis, and the diagnosis is mine.
- **A determinism change.** ⚠ `empty_cache` must not alter the fold's output. **The 416 aa digest
  `b23f4210fcc6077f…` is on record and must reproduce**; if it does not, releasing the pool changes
  results and the change is abandoned, not tuned.

## §6 — ⚠ What must NOT move

**`worker/runner.py` is not touched** — this measures whether the release helps; wiring it into the
fold path is a separate ruling. **No database write, no enqueue, no census row, no fold of any of
the 82** (`### D-081`). **The manifest is not rebuilt and `known_good` is not changed** — both are
owner rulings held pending this number. **No cross-recipe comparison is read; `### D-078` is
unwritten.**

⚠ **And layer 1 remains UNTESTED.** The uncapped climb produced no OOM at all, so the sysmem
fallback policy has still never fired. **Absence of a failure is not evidence that a guard works**,
and nothing here changes that.
