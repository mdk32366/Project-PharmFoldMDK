# ORDERS — Code — 2026-08-23 — THE RENTAL RUN. Paste this whole file.

**AUTHORED-SHA256** (range: **first `## §` header → EOF**, anchored to line starts, **SECOND
occurrence of the marker**) = `b5c5c819678c5070f1a262931a53659ffb92dd7566eccf7ba90c34c8cb37cb9b`
**bytes** = `9397`

> ⚠⚠ **Where this file and `docs/README.md` differ, THE LOG GOVERNS.**
> ⚠ **Verify the hash on arrival; commit this file UNMODIFIED.** Any landing header goes ABOVE
> the first section marker, outside the range. ⚠⚠ *A landing header inside a hash range is a
> silent pin break* — and the marker is deliberately **not spelled out again above**, because
> writing it twice makes the body the THIRD occurrence and sends a literal reader to the wrong
> offset: the same silent pin break, in the sentence warning about it.
> **Companion: `PREWORK-2026-08-23-the-fold.md` (`0e35907c…`) carries the reasoning.**

---

## §0 — Who you are and what today is

**You are Code on PharmFoldMDK, an ADC target-exploration platform. You execute; the Planner rules
and orders; the owner (Matt) holds all judgement calls, merge authority, credentials and destructive
operations.**

**Today is THE RENTAL RUN — the first spend this project has made since 2026-07-24, and the day the
census finishes.**

⚠⚠ **BOTH GATES ARE OPEN.** `D-091` ruling 3 (design) was discharged by `D-095 amendment 1`.
`D-091` ruling 2 (rental spend) was **lifted by the owner on 2026-08-22.** ⚠ **One gate is NOT open:
`tile_max_aa` is unruled, and `RA1` is where that stops being true.**

## §1 — ⚠ The operating rules. All bought the hard way

1. ⚠⚠ **STOP AND REPORT beats guessing.** A scope denial, a permission error, an unexpected result —
   **report it. Never a retry, never a workaround.**
2. ⚠⚠ **Every absence is a CATEGORY WITH A CAUSE.** Never a zero, never a blank, never a dash.
3. ⚠ **Every count states its KEY** — which population, which filter, which column.
4. ⚠⚠ **Two paths to one quantity, compared ON THE NUMBERS.**
5. ⚠ **Name the target explicitly. NEVER accept a default** — `--database`, `PYTHONHASHSEED`, the
   interpreter, **the card**. *A default is a dial that does not announce itself.*
6. ⚠⚠ **Report what a result does NOT establish.**
7. ⚠ **Corrections are recorded, never patched away — including the Planner's.**
8. ⚠⚠ **Production writes and all credential/rental provisioning require the owner at the keyboard.**
   **You do not rent the card. You do not hold the key.**

## §2 — The numbers, stated so you need not go hunting

| fact | source |
|---|---|
| **`incremental_GiB = 7.215e-06 · L^1.983`**, model resident **5.24 GiB**, overhead **1.43 GiB** | `F-059` |
| it predicts the local ceiling at **431 aa**; measured **432** | `F-059` |
| ⚠⚠ **trained context = 1,026 aa**, and no card relieves it | `F-060` |
| a 48 GB card reaches **~2,528 aa** — ⚠ **a 5.8× extrapolation, planning not permission** | `F-059` |
| tranche 5 = **776** rows; **635 ≤ 1,026 aa**, **141 past it** | `census_manifest.v7.csv` |
| the 141 tile: **123 in-context · 10 no_domains · 6 one_oversized_run · 2 single_run_only · 0** | `D-095 am 1` item 9 |
| **1,532 tiles** total; **1,242 of them ≤ 440 aa** | `tranche6_runs.csv` |
| ⚠ `vram_guard.preflight()` is written, tested and **consulted by nothing** | `F-049` |
| ⚠⚠ **and it guards the LENGTH axis, not the memory one** | `F-053` |
| claim-time tier filter is **CLOSED** — the worker declares its tier | `D-090` |
| ⚠ **the independent length guard remains OPEN** | `F-035` remedy 3 |
| `D-082`'s failure mode is a **HOST BUGCHECK** from over-allocation | `D-082` |

⚠ **`F-050` is RESERVED for the guard-direction sweep. Do not take it.** **Next free `F-`: `F-061`.
Next free `D-`: `D-104`.**

## §3 — ⚠⚠ Task RA — THE THREE PRECONDITIONS. NOTHING FOLDS UNTIL THESE LAND

**RA1 — ⚠⚠ `tile_max_aa` IS THE OWNER'S RULING, NOT YOURS AND NOT THE PLANNER'S.**
`D-095 amendment 1` item 7: *"a SPEND DECISION… the number is measured, not proposed."*
**The Planner's proposal is on the table: `tile_max_aa = 1,026`, routed at 440** — ≤440 local,
441–1,026 rental, nothing above 1,026. ⚠ **Do not fold on a proposal. Get the ruling, record it, and
name it in every artifact the run produces.**

**RA2 — ⚠ EMIT THE PER-TILE MANIFEST. This is the real build task.**
`scripts/tranche6_runs.py` **computes the runs and writes only per-protein aggregates.** ⚠⚠ **No
per-tile length exists anywhere in the tree**, so tiles cannot be routed to a card today.
**One row per tile**, carrying at minimum: `census_accession · gene · tile_index · start · end ·
length · tile_cut_kind · merge_rule · straddle_handling · gap_tolerance · regime`.
⚠⚠ **Every parameter travels ON the artifact** — `D-095 am 1` item 6: *a run is a construction, not
an observation.* ⚠ **Report the change you intend BEFORE making it.**
⚠ **Two paths:** the new per-tile file must reproduce `tranche6_runs.csv`'s `n_runs` and
`largest_run` **exactly, per accession**. A disagreement is a defect, not a rounding difference.

**RA3 — ⚠⚠ WIRE THE LENGTH GUARD ON THE MEMORY AXIS, or state in the run record that you did not
and why.** `F-059` supplies the axis: `peak_GiB = 5.24 + 7.215e-06 · L^1.983`.
⚠ **It does NOT license weakening `refused_no_measurement`.** A law is not a measurement of the case
in front of it. **Refuse rather than attempt.**
⚠⚠ **This matters more with tiles than without them: the tier filter keeps rental jobs off the local
worker, but nothing checks that a TILE handed to the local card FITS on it.**

## §4 — Task RB — THE LOCAL TILE FOLDS. FREE, AND THE BULK OF THE WORK

**1,242 tiles, every one ≤ 440 aa, on the local card at int8 / chunk 64. Estimated ~1.5 h. $0.**

**RB1 — Fold them.** ⚠ **Start here.** It needs no card, no key and no decision beyond `RA1`.
**RB2 — ⚠ Report the KEY:** which tiles, which routing rule, and what `folded` means in your count.
**RB3 — ⚠⚠ Abort BEFORE a fold if headroom is gone. NEVER during one.** ⚠ **Ground the threshold in
a MEASURED SUCCESS, not a guess.** *The last calibration took three attempts because it reasoned
about the length-shaped quantity instead of the memory-shaped one.*
**RB4 — Report the first ten tiles' peak VRAM and wall clock** before continuing the rest. ⚠⚠ **If
the measured peak departs from `F-059`'s prediction by more than 10%, STOP AND REPORT — that is a
finding about the law and it outranks finishing the batch.**

## §5 — Task RC — `ceiling_climb` ON THE RENTED CARD, BEFORE ONE ROW IS QUEUED TO IT

⚠⚠ **The ~2,528 aa figure is an extrapolation 5.8× beyond `F-059`'s fitted range. It is planning,
never permission.** **`preflight()` returns `REFUSED_NO_MEASUREMENT` for an unmeasured length BY
DESIGN, and that is correct behaviour, not an obstacle.**

**RC1 — Name the card explicitly** — model, VRAM, driver, rate. ⚠ **NEVER accept what was
provisioned as what was ordered.** *`D-011` specified an A6000 at $0.49/h; an RTX PRO 6000 at $2.00/h
arrived, and the estimate was wrong by an order of magnitude.*
**RC2 — Climb, do not bisect.** *The prior probe jumped 209 → 313 aa and the host bugchecked.*
**RC3 — Report `highest_ok_length` with its recipe and its cap**, and ⚠ **state the allocator
fraction** — on the local card, releasing the cache did NOT raise the ceiling and lifting the 0.85
cap DID.
**RC4 — ⚠ Compare the measured curve against `F-059` on the numbers.** A 48 GB card is a different
stack; **agreement would extend the law and disagreement is a finding.** Either is worth the ten
minutes.

## §6 — Task RD — THE 878 RENTAL FOLDS

**635 single-pass rows (441–1,026 aa) + 243 tiles. 18–29 GPU-h at an assumed 2× speedup. $9–23.**

**RD1 — ⚠⚠ Do not queue a single row until `RC` has returned a measured ceiling for that card.**
**RD2 — The 6 `run_interior` cuts** — FAT4 3,037 · FAT3 2,291 · FAT1 2,289 · MUC16 1,977 ·
FAT2 1,674 · CDH23 1,175. ⚠ **Under `D-094` the `run_interior` disclosure is a MOUNT PRECONDITION,
not a caption: the cut must be legible from the artifact alone.**
**RD3 — ⚠ MUC16 will fold and the result will not mean much** — `D-085` / `D-076` Tier 3,
intrinsically disordered. **Folding it is ordered; presenting it as informative is not.** *Tiling
does not repair disorder.*
**RD4 — ⚠⚠ WATCH THE BILL, NOT THE CLOCK.** *A crashed worker is detectable; a wedged one bills.*
**Report spend against the $9–23 estimate as you go, and STOP AND REPORT if it passes $30.**
**RD5 — Terminate the pod. Confirm $0.00/h.** ⚠ **No network volumes** — they bill while stopped.

## §7 — ⚠ NOT ordered. This is the boundary

- ⚠⚠ **NO REFIT AND NO RESCORING.** It is pre-registered in
  `PRICING-2026-08-22-all-remaining-tranches.md` §6 — **new `ranking_run_id`, runs never mixed, three
  branches named including UNDERPOWERED.** **It runs after the folds land, on those terms.**
  ⚠ **`D-089` holds: no census row is scored.**
- **The 10 `no_domains` rows** — OTOA · MAN2A1 · LCT · MUC22 · NOMO1 · NOMO2 · NOMO3 · CATSPERB ·
  CATSPERG · CD109. ⚠ **No annotation exists to tile at. They need a boundary source or a stated
  exclusion — an owner ruling, not a task.**
- **The 141 as SINGLE sequences.** They are tiled or they are not folded.
- **The 25 rows above ~2,528 aa as single sequences.**
- **No credential work, no migration, no schema change, no production write.**
- ⚠ **No guard-direction sweep** — that is `F-050`, reserved and unwritten.

## §8 — Report

⚠ **`RA1`'s ruling and `RA2`'s two-path check FIRST** — nothing downstream is valid without them.
Then `RB`'s local count with its key · `RB4`'s ten-tile check against `F-059` · `RC`'s measured
ceiling with card, driver, cap and rate · `RD`'s counts and **the actual spend** · branch and tip ·
**both invariants with their keys** · the gate.

⚠⚠ **AND IF ANYTHING MEASURED TODAY CONTRADICTS `F-059` OR `F-060`, SAY SO PLAINLY AND FIRST.**
**Both are one day old and both are OPEN. A refutation on day two is the cheapest one available, and
this project's record is that the catch rate runs both ways.**
