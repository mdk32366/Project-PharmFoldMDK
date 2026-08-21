# PREWORK — 2026-08-23 — THE FOLD

**AUTHORED-SHA256** (range: **first `## §` header → EOF**, anchored to line starts, **SECOND
occurrence of the marker**) = `0e35907c15fd4f0b33f03f15db47c2e19cd595bd7069d3a141863f90581c7998`
**bytes** = `8966`

> Written by the Planner on the owner's ruling *"Rental, scoped. All remaining tranches priced,"*
> and *"fold everything we can, including the big ones — break them into pieces and fold those."*
> ⚠ **Both gates on tranche 5 are now open.** This says what folds, on what, in what order, and the
> three things that must land first.

---

## §0 — Where we are: the gates

| gate | state |
|---|---|
| `D-091` ruling 3 — the tranche 6 **design gate** | ✅ **DISCHARGED** by `D-095 amendment 1` (2026-08-19): `D-095` moved PROPOSED → RULED |
| `D-091` ruling 2 — **rental spend** on tranche 5's 776 rows | ✅ **LIFTED by the owner, 2026-08-22** |
| `F-035` — claim-time **tier filter** | ✅ **CLOSED** by `D-090` (2026-08-17). The worker declares its tier; the server filters inside the claim SQL |
| `F-035` remedy 3 — the independent **length guard** | ⚠ **OPEN** — see §2.3 |
| `tile_max_aa` | ⚠⚠ **UNRULED. A SPEND DECISION.** See §2.1 |
| `D-089` — no census row is scored | unchanged, and nothing below changes it |

**The tiling is not a plan to be made. It is already designed, ruled, and computed** —
`data/census/tranche6_runs.csv` carries all 141 rows. This prework re-derived its regime table
independently: **123 `all_runs_in_context` · 10 `no_domains` · 6 `one_oversized_run` ·
2 `single_run_only` · 0 `multiple_oversized_runs` = 141.** ⚠ **Identical to `D-095 amendment 1` item
9. Two paths to one quantity, compared on the numbers.**

## §1 — What folds, and on what

**Everything remaining is 636 single-pass folds plus 1,532 tiles across the 141.** ⚠ *Key:
777 rows remain unfolded — 776 in tranche 5 plus one local straggler. Of the 776, **635 are
at or inside the 1,026 aa trained context and fold as ONE sequence**; the other **141 are past
it and are tiled, not folded whole**. 635 + 1 = 636 single-pass.*

### A — LOCAL, FREE, and it is the largest block of work

| | |
|---|---|
| **93 proteins → 1,242 tiles** | **every tile ≤ 440 aa — under the measured local ceiling** |
| estimated mean tile | **88 aa** ⚠ *estimate: `residues_in_domains ÷ n_runs`, not a per-tile measurement* |
| estimated wall clock | **~1.3 – 1.6 h on the local card** |
| cost | **$0** |

⚠⚠ **The big proteins are the cheap ones.** Broken at their natural seams, most of the past-context
tail is a pile of ~88-residue domains that fold on the laptop for nothing.

### B — RENTAL, and it is one bill

| workload | folds | GPU-h @2× | cost |
|---|---|---|---|
| 635 single-pass rows, 441–1,026 aa | 635 | 17.3 – 28.6 | $9 – $23 |
| 243 tiles from the 32 proteins whose largest tile is 441–1,026 aa | 243 | 0.7 | **≈ $1** |
| **total** | **878** | **18.0 – 29.3** | **$9 – $23** |

⚠⚠ **Tiling the entire past-context tail adds about one dollar.** The bill is the 635, and it barely
moves.

### C — The 6 that need a cut

**One `run_interior` cut each**, per `D-095 amendment 1` item 8:

| gene | largest run |
|---|---|
| FAT4 | 3,037 |
| FAT3 | 2,291 |
| FAT1 | 2,289 |
| MUC16 | 1,977 |
| FAT2 | 1,674 |
| CDH23 | 1,175 |

⚠ **Under `D-094` the `run_interior` disclosure is a MOUNT PRECONDITION, not a caption.** The cut
must be legible from the artifact alone. ⚠ **MUC16 will fold and the result will not mean much** —
`D-085` / `D-076` Tier 3, intrinsically disordered. **Folding it is fine; presenting it as
informative is not.** *Tiling does not repair disorder.*

### D — The 10 that cannot be tiled at gaps

**OTOA · MAN2A1 · LCT · MUC22 · NOMO1 · NOMO2 · NOMO3 · CATSPERB · CATSPERG · CD109** — regime
`no_domains`. ⚠ **A category with a cause, not a failure: no domain annotation exists to tile at.**
They need a boundary source or a stated exclusion. **They are not folded tomorrow** unless the owner
rules a method for them.

### E — One local straggler

**2,691 local-tier rows, 2,690 folded.** One row is unfolded, under the ceiling, **$0**. ⚠ Its
identity needs a database read.

## §2 — ⚠⚠ Three things must land BEFORE the first fold

### 2.1 — `tile_max_aa` is UNRULED, and it is the owner's

`D-095 amendment 1` item 7: *"`tile_max_aa` is a SPEND DECISION and `D-095` nowhere says so… **The
number is measured, not proposed** — `1,000` was never folded."*

**It can now be a measured number.** `F-059` fits `incremental_GiB = 7.215e-06 · L^1.983`, and two
limits bracket it:

- **The model:** the trained context is **1,026 aa**. Past it there is no evidence a structure means
  anything. **This is the binding limit and no card relieves it** (`F-060`).
- **The card:** the law puts a 48 GB rental card at **~2,528 aa** and the local card at **431 aa**
  (measured: 432).

> **Planner's proposal, for the owner to rule: `tile_max_aa = 1,026`, routed at 440.**
> Tiles **≤ 440 aa → local, int8, free.** Tiles **441 – 1,026 aa → rental card.** **No tile above
> 1,026** — that is the modelling limit, not a budget one.

⚠ **This is a proposal. It is not ruled and I have not folded on it.**

### 2.2 — Per-tile coordinates are not persisted

`scripts/tranche6_runs.py` **computes** the runs and writes only per-protein aggregates —
`acc, gene, span_aa, n_domains, n_runs, largest_run, runs_over_context, regime`. ⚠⚠ **There is no
per-tile length anywhere in the tree**, which is why §1's tile figures are estimates and why tiles
cannot yet be routed to the right card.

**Needed: a per-tile manifest — one row per tile, with `start`, `end`, `length`, `tile_cut_kind`,
`merge_rule`, `straddle_handling` and the gap tolerance recorded on it.** ⚠ **A script change and a
re-run. No spend, no fold, no ruling.** ⚠ *`D-095 amendment 1` item 6: a run is a construction, not
an observation — every parameter travels on the artifact.*

### 2.3 — The length guard is still open, and now there is a right axis for it

`F-035` remedy item 3 remains **OPEN**. `vram_guard.preflight()` is **written, tested and consulted
by nothing** (`F-049`) **and it guards the LENGTH axis, not the memory one** (`F-053`).

⚠⚠ **This bites harder with tiles than without them.** The tier filter separates rental jobs from the
local worker, but **nothing checks that a tile handed to the local card fits on it.** `D-082`'s
failure mode is a **host bugcheck**, and this is the owner's laptop.

**`F-059` supplies the axis:** `peak_GiB = 5.24 + 7.215e-06 · L^1.983` against measured headroom.
⚠ **It does not license weakening `refused_no_measurement`** — a law is not a measurement of the case
in front of it.

## §3 — The order of operations

1. **Rule `tile_max_aa`** (§2.1). Ten minutes, and everything downstream depends on it.
2. **Emit the per-tile manifest** (§2.2). Script change, no spend.
3. **Wire the length guard on the memory axis** (§2.3), or state in the run record that it was not
   and why.
4. **Start the LOCAL tile folds — 1,242 tiles, ~1.5 h, $0.** ⚠ **They need no card and no decision
   beyond step 1.** *This is the work to start first because it is free and it is the bulk of it.*
5. **`ceiling_climb` on the rented card BEFORE queueing one row to it.** ⚠⚠ The ~2,528 aa figure is a
   **5.8× extrapolation** beyond `F-059`'s fitted range. **Planning, never permission.**
6. **Then the 878 rental folds** — 635 single-pass + 243 tiles, $9–23.
7. **The 6 cuts**, with `run_interior` disclosure carried on the artifact (`D-094`).

⚠ **Steps 4 and 6 run in parallel.** The local card works for free while the rented card bills, and
`D-090`'s claim-time tier filter is what makes that safe.

## §4 — ⚠ NOT in scope tomorrow

- ⚠⚠ **NO REFIT AND NO RESCORING.** The refit is **pre-registered** in
  `PRICING-2026-08-22-all-remaining-tranches.md` §6 — new `ranking_run_id`, runs never mixed, three
  branches named including **underpowered**. **It runs after the folds land, on the terms already
  written, and `D-089` still holds.**
- **The 141 past-context rows as SINGLE sequences.** They are tiled or they are not folded.
- **The 10 `no_domains` rows** — §1.D, pending a method or an exclusion.
- **The 25 rows above ~2,528 aa as single sequences** — beyond the rented card by the law.
- **No credential work, no migration, no production write.** ⚠ **Production writes require the owner
  at the keyboard.**

## §5 — ⚠⚠ Safety, and it is not optional

- **`preflight` will not save you** — unwired, and guarding the wrong axis until §2.3 lands.
- **Abort BEFORE a fold if headroom is gone. NEVER during one.**
- **Ground any threshold in a MEASURED SUCCESS**, not a guess. ⚠ *The last calibration took three
  attempts because it reasoned about the length-shaped quantity instead of the memory-shaped one.*
- ⚠ **A permission denial is stop-and-report.** Never a retry, never a workaround.
- **Every absence is a category with a cause. Every count states its key.**

⚠ **What this prework does NOT establish:** tile lengths are estimated from `residues_in_domains ÷
n_runs` and will change when §2.2 lands; the rental hour figures assume a **2–4× speedup that is an
assumption, not a measurement**; market rates are **not quotes**; and fold state is read from the
last committed live read, not from the database — **the proxy on 16380 was closed when this was
written.**
