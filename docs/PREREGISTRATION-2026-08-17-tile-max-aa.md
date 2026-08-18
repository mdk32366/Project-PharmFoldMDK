# PRE-REGISTRATION — `tile_max_aa` is measured, not proposed

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision would be reached;
> it is not itself authority.
>
> ⚠⚠ **DESIGN ONLY. NOTHING HERE HAS BEEN RUN.** Ordered by ORDERS-Code-2026-08-17 (third) §2 and
> **held by ruling 3**: `D-095` is `PROPOSED`, `D-091` ruling 3's gate is shut, and this measurement
> needs its own log entry on the `D-099` control-fold pattern before it executes. **No GPU, no
> rental, no ingest.**

---

## §0 — Why the existing instrument answers the wrong question

`D-095` proposed **`tile_max_aa = 1,000`** and marked it *proposed, not measured*. The obvious
instrument is `ceiling_climb`, and ⚠⚠ **it measures the wrong ceiling.**

`ceiling_climb` measures **what fits in VRAM** — the length at which an int8 fold stops completing
on an 8,150 MiB card. But `D-095`'s own deep-learning justification says the binding constraint is
the **1,026-residue trained context, a property of the MODEL, not of the hardware.**

⚠ **A tile sized at the VRAM ceiling is a tile past the trained context — which is the thing tiling
exists to avoid.** The two ceilings are different quantities and the smaller one binds. **Nobody
here has measured the second.**

⚠ Recorded so it is not re-derived: **the local card's measured `known_good` is 440 aa at int8**,
which is already *below* 1,026. So on this hardware the VRAM ceiling binds first and the context
curve may be unobservable locally at all — **which is itself a result, and is one of the outcomes
this pre-registration must be willing to report.**

---

## §1 — The two ceilings, both reported

**Both are reported even when one clearly binds.** ⚠ Reporting only the binding one makes the
non-binding one unfalsifiable later.

| ceiling | instrument | question it answers | status |
|---|---|---|---|
| **hardware** | `ceiling_climb`, local int8 | at what length does the fold stop completing? | existing instrument, known shape |
| ⚠⚠ **context degradation** | **does not exist** | at what length does the model stop being confident about what it produces? | **never run here** |

---

## §2 — The context-degradation curve

**Fold the SAME sequence at increasing tile lengths and watch pLDDT.** If confidence degrades
before the hardware ceiling, **`tile_max_aa` comes from that curve and not from VRAM.**

### 2a — Which sequence, by a stated rule, ⚠ NEVER by pLDDT

⚠⚠ **Selecting the probe sequence by its confidence would choose the subject on the variable under
test** — the `D-087` defect, and the same error `D-099 amendment 1` corrected in the control fold's
sampling. The rule is stated here, before any candidate is scored:

- **From the 141** (`D-098` scope), so the measurement is about the population it will govern.
- **Regime `all_runs_in_context`** — 123 of the 141 (Task L). ⚠ A probe drawn from an oversized-run
  protein would confound *tile length* with *cut placement*, which is a separate pre-registration.
- **The single longest span in that regime**, so the ladder has the most rungs before the hardware
  ceiling. Ties broken by `census_accession` ascending.
- ⚠ **The probe is named and committed BEFORE the first fold**, exactly as
  `data/census/d099_control_sample.csv` was.

### 2b — The ladder

- Lengths from the span's N-terminus: **200, 300, 400, 440, 500, 600, 800, 1000, 1026, 1100**.
- ⚠ **Prefix slices of one sequence**, not different proteins — the point is to vary length while
  holding the molecule constant. **A ladder across proteins measures proteins.**
- ⚠ **440 and 1026 are on the ladder deliberately**: the measured hardware `known_good` and the
  trained-context boundary. **The two ceilings must be observable in the same series.**
- ⚠⚠ **A rung that fails to fold is a DATUM, not a gap.** It is recorded as
  `hardware_ceiling_reached` with its error, and the ladder stops there rather than being retried
  at a smaller step to manufacture a longer curve.

### 2c — What counts as degradation, ⚠ defined in advance

**Stated before any number is seen, because a threshold chosen after the curve is a threshold
chosen for the answer it gives.**

- **Primary:** mean pLDDT over the **first 200 residues** — the region present at *every* rung, so
  the comparison is within-region and not confounded by the added tail. ⚠ **Comparing whole-tile
  means across rungs would measure the tail, not the degradation.**
- **Degradation is declared** when that windowed mean falls **more than 5.0 points** below the
  200 aa rung, **and the fall is monotone across two consecutive rungs.** ⚠ The two-rung condition
  is there because one rung is noise.
- ⚠ **The null result is pre-committed and publishable:** if the windowed mean does **not** fall by
  5.0 before the hardware ceiling, the finding is *"the context limit was not observable on this
  hardware"* — **not** *"there is no context limit."* **Unmeasured is not zero.**
- ⚠ **`D-099`'s determinism note applies:** `determinism_control.int8.610.88` shows the kernel is
  deterministic at this recipe, so a re-fold reproduces and a difference between rungs is the tile
  length rather than run-to-run variation. **This is asserted from an existing artifact, not
  assumed.**

---

## §3 — What this pre-registration does NOT authorise

- ⚠ **No fold.** It executes only when its own log entry is written **and ruled**, per ruling 3.
- **No tiling, no `RECOGNISED_BOUNDARY_METHODS` change, no ingest**, and no artifact enters
  `protein_analyses` — the `D-099` condition-3 pattern, enforced by importing no database module.
- ⚠ **No decision on where inside a run to cut.** Separate pre-registration, separate entry.
- ⚠⚠ **No setting of `tile_max_aa`.** This measures the two ceilings. **Choosing the value from
  them is a ruling**, and if the curve and the VRAM ceiling disagree, *which one governs* is the
  owner's call and not a consequence of the data.

---

## §4 — The outcome table, written before the run

⚠ Every outcome has a name and a consequence **now**, so none can be discovered as convenient later.

| outcome | `tile_max_aa` comes from | ⚠ note |
|---|---|---|
| degradation observed **below** the hardware ceiling | the **context curve** | the model's limit binds; `D-095`'s justification is confirmed by measurement |
| hardware ceiling reached **with no degradation** | ⚠ **neither, yet** | on this card the VRAM limit binds first (`known_good = 440`), so the context limit is **unobserved, not absent** — and a rental card would be needed to see it |
| degradation observed **at** 1,026 ± one rung | the **context curve**, confirming the trained-context boundary | the strongest possible result for `D-095`'s framing |
| pLDDT **rises** with length | ⚠⚠ **nothing — the design's premise is wrong** | tiling would be *harming* confidence, and `D-095` needs rewriting, not amending |
