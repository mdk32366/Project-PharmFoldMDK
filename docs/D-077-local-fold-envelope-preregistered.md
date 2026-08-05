# D-077 — The local fold envelope: measure it, bind it to its recipe, and slice the census by it — as a **cost and reproducibility** axis, never as a suitability axis

> **STAGED ENTRY — merge into `docs/README.md` before any probe runs.** This is a
> pre-registration. **It is void if code precedes it** (D-075 precedent).
>
> **⚠ Confirm the number against the live log before merging.** In the 2026-08-04 project
> snapshot the highest `### D-` entry is **D-075** and the highest `### F-` is **F-010**.
> `D-076` is **claimed by a staged file** (`docs/D-076-last-three-fold-plan.md`, renumbered
> 2026-08-03) but **has no `### D-076` entry in the log** — which is exactly the D-062 shape.
> So `D-077` is the next free integer *if* D-076 lands as written. **Check the thing, not the
> reference to it** (method note item 7).

- **Date:** 2026-08-04
- **Status:** Proposed → Accepted on merge. **Ruled before any probe.**
- **Type:** A **decision**. It rules a measurement design, freezes two interpretations, and — the
  load-bearing half — **rules what the resulting axis may and may not be used for.** Its results
  land later as their own F-entries.
- **Relates:** **D-024** (which left the local ceiling inside (440, 630) *deliberately open and
  cheap* — this closes that item); **S-004/S-005** (the original bisection and its anchors);
  **D-022** (the A6000 ceiling probe, whose instrument this reuses); **D-047** (recipe resolved at
  fold-time, not frozen at enqueue); **D-042** (rental chunking, after O(L³) falsified the
  no-chunk assumption); **F-008** (the two-precision confound this creates the overlap to test);
  **D-075 decision 6** (which names F-008 as unresolved and not a prerequisite); **D-027**
  (the fixed six features — this entry adds none); **D-050** (derive, don't hardcode).
- **Provenance (D-016):** owner observation, 2026-08-04 — *"we can slice the census by one more
  dimension: ability to fold on the laptop. All that costs is power."*

---

## Context — what is actually unmeasured, and what it is costing

**How known (D-016):** read directly from the 2026-08-04 repository snapshot.

| Fact | Source |
|---|---|
| `CEILING_KNOWN_GOOD = 440`, `CEILING_KNOWN_BAD = 630`, band **UNMEASURED** | `core/manifest.py:51-54` |
| 13 cohort targets route to rental with `tier_reason=unmeasured_local_ceiling` | `core/manifest.py:16-17,129-130` |
| Local recipe **int8 / chunk 64**; rental recipe **fp16 / chunk 64** — the tiers differ **only in dtype** | `core/contracts.py` `TIER_RECIPE` |
| 440 aa folded clean at chunk 64: 28.6 s, peak **6665 MiB**, **378 MiB** headroom against 7043 MiB free | `ARCHITECTURE.md:607-609,616` |
| 630 aa is **4-for-4 fatal** | `ARCHITECTURE.md:598-599` |
| *"HER2 might yet fold at chunk 16/32 … this is **untested**"* | `ARCHITECTURE.md:616-618` |

**Derived this session from `data/cohort_82_ecd.csv` (2026-07-21 snapshot), 13 targets with
`largest_span_aa` strictly inside (440, 630):**

`ENTPD1 441 · SCNN1A 456 · ADAM17 457 · MERTK 485 · CSF1R 498 · PDGFRB 500 · LRFN4 502 ·
LRFN3 523 · EPHA4 528 · GRIN1 541 · CDH11 564 · LRRN1 606 · EGFR 621`

**ENTPD1 was routed to paid compute for being one residue over a bound nobody has measured.**

> ⚠ **That CSV is a 2026-07-21 snapshot and 13 of its 82 rows carry an empty `largest_span_aa`
> (`bucket_by_largest='unknown'`, IGF2R among them).** No census claim in this entry may be
> derived from it. Every count that reaches a surface, a deck, or the paper **re-derives from
> `/api/coverage` and `/api/analyses`** (D-050 stale-literal discipline). The list above is
> *orientation for the probe's bounds*, not a reportable statistic.

---

## Decision (1) — ⚠ **What this axis IS, and what it is NOT.** The load-bearing ruling.

**Local-foldability is a monotone step function of ECD length.** ECD length is **feature 1** of the
pre-registered six (D-027). Tier was assigned *by* length. Precision was assigned *by* tier.
Therefore **length, tier, precision, and local-foldability are, on the current cohort, four names
for one partition with no overlap** — which is precisely the confound F-008 recorded and D-075
decision 6 declines to resolve.

**Rulings, binding on every downstream artifact:**

1. **Local-foldability MUST NOT become a model feature.** No seventh (or eighth) feature. The
   `--ablate` named-set refusal (D-075 decision 5) stands unamended; adding a foldability feature
   requires a new dated entry and would re-import F-008 under a new name.
2. **It MUST NOT be presented as a census axis alongside suitability without its label.** It is a
   **cost / tractability / reproducibility** axis. It says what a target costs to *compute*, and
   **nothing whatsoever** about whether it is a good ADC target. Any surface placing the two side
   by side must state that in the same visual frame (D-069, every surface self-sufficient).
3. **It MUST NOT be used to filter the census.** A comprehensive census (roadmap 3.1) that silently
   drops the targets it cannot afford to fold is a census of *our budget*, not of the surfaceome —
   and it would bias the census by length, i.e. by feature 1. Unaffordable targets stay in the
   census, flagged, unfolded. **This is the F-009 error one level out and it is refused here in
   advance.**
4. **The one thing it legitimately is:** a *pre-fold, sequence-only* predicate. It can be computed
   for an arbitrary census **without folding anything**, which makes it the only cost instrument
   available before the money is spent.

**Why this ruling is written before the measurement:** the measurement is cheap and the temptation
after it will be to promote a satisfying new number to an axis. Naming what it is now removes that
option later.

---

## Decision (2) — the chunk-invariance question runs FIRST, because it decides whether "the ceiling" is a number or a curve

`ARCHITECTURE.md:616-618` records, as *inference not measurement*, that HER2 at 630 aa might fold
at chunk 16/32 — **untested.** If true, the local envelope is not a single length; it is a
length-per-chunk_size curve, and the "free" envelope is much larger than 440.

But a fold produced at a different `chunk_size` is only usable if **chunk_size does not change the
output.** Chunking is a tiling of the trunk's triangular attention; it *should* be
output-invariant. **Should is not measured.**

**The test, frozen before it runs.** On the local box, at `dtype=int8`, fold one fixed sequence
(the existing test fixture's source, or Trop-2 at ~248 aa — short enough that every chunk_size
fits) at **chunk_size 64, 32, and 16**. Compare the three outputs.

| Outcome | Reading — **fixed now** |
|---|---|
| All three produce **byte-identical CA coordinates and pLDDT** | `chunk_size` is a **memory/time knob only**. The ceiling is a curve, folds across chunk sizes are commensurable, and probing at chunk 16/32 is legitimate. |
| Outputs differ **at all**, by any margin | `chunk_size` is a **recipe dimension**. The ceiling is then defined **only at chunk 64**, folds across chunk sizes are **not** commensurable, and the extended-envelope branch (decision 4) is **abandoned, not deferred**. The difference is reported as a finding in its own right — *ESMFold's chunked trunk is not output-invariant* is a publishable methods note nobody reports. |

**No third reading. No tolerance threshold invented after seeing the diff** (D-041 decision 4).
"Nearly identical" is the *differ* branch. If a tolerance is ever wanted, it is a new dated entry.

---

## Decision (3) — the ceiling is measured at the production recipe, and the constant is BOUND to it

**The failure this prevents:** `worker/ceiling_probe.py` takes `--dtype` and `--chunk-size` as free
CLI arguments and **defaults `--dtype` to `fp16`** (written for the A6000, D-022). A local run that
forgets `--dtype int8` measures a ceiling for a recipe **the local tier does not use**, and that
number would then be written into `CEILING_KNOWN_GOOD`, which routes production folds at int8. That
is the project's recurring shape: **two paths to one quantity, never compared** — the routing
constant and the recipe that measured it, free to drift.

**Ruled:**

- The bisection runs at **`dtype=int8, chunk_size=64`** — resolved from `TIER_RECIPE["local"]`,
  **not** passed by hand (D-047's principle, applied to the probe).
- **The measured ceiling is recorded as a triple `(hardware, dtype, chunk_size) → length`, never as
  a bare integer.** `CEILING_KNOWN_GOOD` acquires a named recipe alongside it, and a test asserts
  the constant and the recipe cannot be updated independently.
- A ceiling measured under any other recipe **may not** update the routing constant.

---

## Decision (4) — the repeat rule, frozen before the probe, and the outcome the current instrument cannot express

**⚠ The existing probe assumes a sharp, monotone boundary, and cannot report that it isn't one.**
Read from `worker/ceiling_probe.py`: `bounds_from_history` raises the floor on **any single** `ok`
and lowers the ceiling on **any single** failure; `next_probe_length` **raises `ValueError` when
`bad <= good`** (asserted as correct by `tests/test_ceiling_probe.py::test_requires_good_below_bad`);
`ceiling_from_history` reports `max(ok)` and **ignores `bad` entirely**. So a sequence like
*ok@560 then oom@500* — entirely plausible 378 MiB from the wall — makes the probe **crash rather
than report the flakiness.** The instrument has no vocabulary for *"the boundary is a band."*

This is **not** logged as a defect in the probe. It is a design assumption that was correct for the
A6000 (far from its wall) and is **not obviously correct for a card with 378 MiB of headroom.**
Recorded here so a `ValueError` during the run is read as **a result**, not a bug.

**The repeat rule, frozen:**

- A length is **known-good** only if it folds clean **4 times consecutively.** A length is
  **known-bad** only if it fails **4 times.** *k = 4 is inherited from the existing record —
  630 aa was ruled fatal on 4-for-4 (`ARCHITECTURE.md:598-599`) — not invented here.*
- Anything else at a given length is **`unstable`**, a **pre-registered, legitimate, reportable
  outcome**: the ceiling is then a **band**, reported as `(highest 4-for-4 good, lowest 4-for-4
  bad)`, and **routing uses the conservative end.**
- **A single lucky fold never raises the routing constant.** This is the whole point of k.
- **Stopping rule frozen:** the bisection stops when `bad - good <= step`, `step = 8`. No "one more
  try" after a satisfying success. Re-running with the same JSONL history must be deterministic.

---

## Decision (5) — the probe must not be able to touch the reported cohort

**Structurally true today, and asserted anyway (D-074).** `worker/ceiling_probe.py` writes only to
an append-only JSONL file and holds no database session; probe folds cannot enter
`protein_analyses`. But this is a property of the current call path, not a guarantee — the same
distinction D-075 decision 5 drew about `persist_results()`.

**Ruled:** probe artifacts live under `data/derived/`, never in the analysis tables. A test asserts
the probe module imports no database session and no persistence helper, **proven by revert** (add
the import, watch it redden). **If a probe fold ever lands in `protein_analyses`, `/api/coverage`'s
folded count moves and F-004's denominator 56 moves with it** — from a measurement that exists only
to decide where to run things. That is D-075's Corruption 2 in a new costume, and it is guarded
before it can happen rather than after.

---

## Decision (6) — the census cost model, and what it may claim

A pure function over ECD span → `{local | rental | over-ceiling}` at the measured recipe, plus a
script that reports the split for an arbitrary list of spans. **No GPU, no network, fully unit
tested.** This is Phase 2's actual instrument: it answers *"what does a census of N targets cost?"*
before a dollar is spent.

**Two claims it licenses, and one it does not:**

- ✅ **Cost:** *"Of these N targets, M fold at zero marginal cost on an 8 GB consumer card; N−M need
  rented compute."* Derived, dated, recipe-named.
- ✅ **Reproducibility (paper-relevant):** *"M of the folds underlying this result are reproducible
  by any reader with a consumer 8 GB GPU and no cloud spend."* This is a real strength of the
  single-sequence / no-MSA design and it costs nothing to state — **provided M is derived from the
  live endpoints and carries its recipe.**
- ❌ **Not licensed:** any statement that couples foldability to suitability, or any census that has
  been filtered by it (decision 1).

---

## Decision (7) — what this entry does NOT do

- **It does not run the F-008 precision A/B.** If the measured ceiling exceeds 440, some targets
  become foldable **locally at int8** that were folded **on rental at fp16** — creating, for the
  first time, **overlap in a partition F-008 recorded as having none.** That is F-008's own named
  resolution path and it becomes nearly free. **It is a separate, separately-pre-registered entry
  (D-078), written before any such fold runs, because its outcome can move F-004.** Naming it here
  is not authorising it.
- **It does not fold IGF2R, FAT2, or MUC16.** IGF2R remains D-076 Tier 1 (rental); FAT2/MUC16 stay
  on ice behind their trigger.
- **It does not change the six features, the scorer, the pre-registered run, or any reported
  result.** Nothing in this entry has a path to F-004.

---

- **Deep-learning justification.** The ceiling is a property of **quantized ESMFold inference** —
  how the trunk's O(L³) triangular attention scales against 8 GB under int8 with chunked attention.
  Measuring it measures the neural core's operating envelope, and it determines what fraction of any
  future census the network can process without external compute. Decision 2 is the sharper DL
  question: **is ESMFold's chunked trunk output-invariant?** That is a statement about the model's
  numerics, it is cheap to test, and its answer is load-bearing for whether folds produced under
  different memory settings may share a ranking at all.

- **Consequences / test surface.** Chunk-invariance fixture reds on a deliberately perturbed
  comparison and greens on identical output · the probe resolves its recipe from
  `TIER_RECIPE["local"]` and a hand-passed dtype is refused · `CEILING_KNOWN_GOOD` cannot change
  without its recipe changing (test proven by revert) · a single `ok` does not raise the routing
  constant (k=4 asserted) · `unstable` is representable and does not raise · the probe module
  imports no DB session (proven by revert) · the census cost function is pure and derives its
  ceiling from the named constant, never from a literal (D-050).
