# PRE-REGISTRATION — 2026-08-07 — The span re-parse post-state, forecast before a line changed

> **Written BEFORE any change to the extraction rules**, per `ORDERS-Code-2026-08-07-span-implementation.md`
> Task 3 and `AMENDMENT-Code-2026-08-07-reparse-and-organism-check.md` A1. Governed by
> `RULINGS-2026-08-07-span-definition.md`. Where this file and the log differ, **THE LOG GOVERNS.**
> ⚠ This file is provenance; it is not authority.
>
> ⚠ **It is void if the implementation precedes it** (D-075 / D-077 / D-079 precedent).
>
> **Provenance (D-016):** every figure is Code's reading, computed with the primitives in
> `scripts/span_extraction_audit.py` — **committed unchanged at `f40d76e` and not the implementation
> under forecast.** Source: `data/census/spancache` (**0 fetches**), `data/census/spans_annex.csv`,
> `data/census/spans_surface.csv`. ⚠ **If the implementation disagrees with a number below, one of
> the two is wrong and that is a finding, not a discrepancy to reconcile after the fact.**

---

## §1 — The rules being implemented, stated so a mismatch is attributable

**ACCEPTED** (7): `Extracellular` · `Lumenal` · `Lumenal, vesicle` · `Vesicular` · `Intragranular` ·
`Exoplasmic loop` · `Perinuclear space`
**HELD, NOT ACCEPTED** (2): `Lumenal, melanosome` · `Vacuolar` — Task 5, and **they gain nothing here**
**REJECTED** (6): `Mitochondrial intermembrane` · `Mitochondrial matrix` · `Nuclear` ·
`Peroxisomal matrix` · `Peroxisomal` · `Cytoplasmic`
⚠ **Anything else is `term_unruled`** — named and reported, never silently dropped, never silently
accepted. **That is the defect this whole arc came from.**

**GPI:** rule **A** primary `Chain` start → (`Lipidation` − 1); rule **B** fallback when `Lipidation`
is absent, `Chain` start → `Chain` end. Missing a required feature is `absent_with_reason`, named.
**`span_boundary_unknown`:** the SDK1 shape — out of the bands, named, recording the coordinate it
does have, ⚠ **no coordinate invented.**

---

## §2 — ⚠ THE FORECAST, AS A COMPOSITION. Never a total.

**Denominators, each stating its key. Never summed across classes.**
`spans_annex.csv` **2,209** rows = 2,190 fetched + 19 never-fetched + 0 failed ·
`spans_surface.csv` **2,807** rows = 2,800 fetched + 7 never-fetched + 0 failed.
⚠ **The never-fetched are not re-parsed and do not enter any band** — they were never asked.

### ANNEX — over its 2,190 fetched rows

```
mechanism                      forecast
vocabulary        → span          885     (332 already had one; 553 GAIN)
gpi_rule_A        → span            1     (GAIN)
gpi_rule_B        → span            0
gpi_absent_with_reason              0
span_boundary_unknown               0
term_unruled                        1     ⚠ P0DKB6 MPC1L, 'Mother cell cytoplasmic'
no_extracellular_span           1,303
                               ------
sum                             2,190     = the declared fetched denominator
```
**foldable 332 → 886.** Rows gaining a span: **554** = 553 vocabulary + 1 GPI.

### SURFACE — over its 2,800 fetched rows

```
mechanism                      forecast
vocabulary        → span        2,453     (2,352 already had one; 101 GAIN)
gpi_rule_A        → span          124     (GAIN)
gpi_rule_B        → span            0
gpi_absent_with_reason              2     ⚠ P25063, P31358 — GPI anchor, no `Chain` feature
span_boundary_unknown               1     ⚠ Q7Z5N4 SDK1
term_unruled                        0
no_extracellular_span             220
                               ------
sum                             2,800     = the declared fetched denominator
```
**foldable 2,352 → 2,577.** Rows gaining a span: **225** = 101 vocabulary + 124 GPI.

### ⚠ THE SHARPEST PREDICTION, AND THE EASIEST TO FALSIFY

**Rows whose EXISTING span changes: `0` in both classes.** The widening is **purely additive** — no
protein that already had a span gets a different one. ⚠ **If any existing span moves, the
implementation has changed what it was not asked to change, and that is a stop.**

### Reconciliation against the independent audit (`f40d76e`)

Annex vocabulary gain **553** equals the audit's annex reachable count exactly. Surface vocabulary
gain **101** equals the audit's surface reachable **107** less the 3 `Lumenal, melanosome`, the 2
`Vacuolar` (both held, gaining nothing) and the 1 `span_boundary_unknown`. ⚠ **Stated as a
reconciliation of two independently computed figures — not as a residual. A residual is not a
measurement.**

---

## §3 — ⚠ What must NOT move. Named, so silence is not evidence.

**Zero database writes.** `protein_analyses` · `protein_features` · `ranking_runs` ·
`ranking_results` · `target_scores` — ⚠ **untouched, and no connection is opened at all.**

**`data/cohort_82_ecd.csv` untouched.** ⚠ **`### D-081` freezes the 82 permanently.** The extraction
change must be **opt-in and named**, so the frozen definition stays reproducible: a re-run of the
cohort under the old definition must still produce the old file, byte for byte.

**No fold, no score, no rank.** D-079 dec 1 stands. **No network call** — the cache holds everything.

---

## §4 — A1: the re-parse, and the two facts that are never one date

⚠ **The dropped domains are not in the CSVs.** `parse()` filtered them before the CSV was written,
so there is nothing to reclassify. **The cache is re-parsed; the network fetch is not repeated.**

| Field | Source | Rule |
|---|---|---|
| `fetched_on` | the cache entry / the existing row | ⚠ **PRESERVED, byte-identical. Never restamped** |
| `uniprot_release` | the cache entry / the existing row | ⚠ **PRESERVED** |
| `parsed_under` | **new** | the span-definition version and the commit that produced the row |

⚠ **A re-parse that overwrites the fetch date manufactures provenance for data that did not move** —
it would turn a one-day pull into a two-day pull as an artifact of housekeeping, which is the date
rule tripped by its own maintenance. **Asserted by test, proven by revert.**

---

## §5 — ⚠ A FINDING ALREADY, BEFORE THE IMPLEMENTATION: rule B over-reads

The order asks where A and B diverge by more than one residue and says a larger divergence means a
`Chain` annotation that does not mean what was assumed. **Measured over all 130 GPI-anchored fetched
census rows: 6 diverge, and every one diverges in the same direction — B longer than A.**

```
Q6UWB4  A=306 B=334  +28   chain 19-352   lipidation 325   Propeptide 'Removed in mature form' 326-352
P08571  A=325 B=348  +23   chain 20-367   lipidation 345   Propeptide 'Removed in mature form' 346-375
P06731  A=641 B=651  +10   chain 35-685   lipidation 676   Propeptide 'Removed in mature form' 677-702
P22303  A=556 B=583  +27   chain 32-614   lipidation 588   ⚠ no Propeptide feature
P13591  A=721 B=839  +118  chain 20-858   lipidation 741   ⚠ no Propeptide feature
Q96GW7  A=623 B=889  +266  chain 23-911   lipidation 646   ⚠ no Propeptide feature
```

**The mechanism is the C-terminal GPI signal sequence**, which is cleaved and replaced by the anchor.
Three of the six have it annotated as `Propeptide` *"Removed in mature form"* beginning at
`Lipidation + 1`; ⚠ **three do not have it annotated at all, and `Chain` runs straight through it.**
`Q96GW7` over-reads by **266 residues**.

⚠ **So rule B systematically over-reads, and rule A is right to be primary.** ⚠ **And this changes no
output: rule B fires ZERO times in this census** — all 130 carry `Lipidation`. **It is a check on the
rule, not an input to it,** exactly as ordered.

⚠ **One methodological note, because it nearly became an error.** A first pass took `Chain` features
`[0]` and reported **7** divergences including one of **−195** (`P51654`). That negative was an
artifact of picking the first of two `Chain` records on a proteolytically processed protein, not a
property of the data. Re-derived over the full mature-chain bounds — `min(start)`, `max(end)` — it
disappears and the count is **6, all positive.** The first number is recorded because a forecast that
quietly drops its own wrong figure is not a forecast.

---

## §6 — What would falsify this

- any existing span changes → **stop**
- a mechanism count differs from §2 → **stop and attribute it before proceeding**
- the mechanism counts do not sum to the declared fetched denominator → rows lost or double-counted
- `fetched_on` differs on any row before and after → the date rule tripped by its own maintenance
- a term appears that is neither accepted, held, rejected nor reported as `term_unruled`
- any write to a database table, or any network call
