# PRE-REGISTRATION — 2026-08-16 — Census ingest, tranche 1

> **Written BEFORE the ingest instrument exists.** Governed by `### D-079`, `### D-081`, `### D-082`,
> `### D-083` and `D-047`. Where this file and the log differ, **THE LOG GOVERNS.**
> ⚠ **VOID IF CODE PRECEDES IT.** At this commit there is no census ingest script.

**Provenance (D-016):** counts read off `data/census/census_manifest.v7.csv`; DB state from
`scripts/census_preflight.py`, re-run after the reboot.

---

## §1 — ⚠ THE LARGEST PRODUCTION WRITE THIS PROJECT HAS MADE, and it is bounded deliberately

**Scope: tranche 1 only — 1,307 rows, every one ≤50 aa.** Not the 3,467 foldable, not the 5,016
census rows. ⚠ **The remaining tranches are separate writes**, because a bounded write that can be
inspected beats one that cannot be undone.

**Tranche 1 is the cheapest possible place to be wrong**: against a measured 440 aa ceiling, a
50 aa fold has no plausible VRAM failure — which is exactly why `### D-083` put it first.

## §2 — What is written, per row

| Field | Value | Why |
|---|---|---|
| `input_type` / `input_value` | `uniprot` / accession | the join key every surface uses |
| `cohort_tranche` | **1** | ⚠ **never 0, never NULL** |
| `ranking_run_id` | ⚠ **NULL** | `fit_scorer` selects **by `ranking_run_id`** — a census row attached to a run could be scored, and `### D-079` dec 1 bars that |
| `meta["tier"]` | `local` | ⚠ **required**: `/claim` raises without it (D-047) |
| `meta["sequence"]` | the sliced ECD | what actually folds |
| `meta` census fields | class, span, coordinates, band, tranche, span_definition, guards | so a row explains itself |
| `inference_settings` | model id/revision, source, `ecd_start`, `ecd_end` | ⚠ **NO dtype/chunk_size as authority** — resolved from `TIER_RECIPE` at claim time |

⚠ **The recipe is NOT taken from the job.** `app/artifacts.py:77-86` resolves `dtype` and
`chunk_size` from `TIER_RECIPE[meta["tier"]]` at claim time — D-047. Storing them would create a
second source with nothing comparing them.

## §3 — ⚠ THE FORECAST, as a composition. Never a total.

```
BEFORE                                   AFTER
protein_analyses            80           1,387   (+1,307)
  cohort_tranche = 0        80              80   ⚠ UNCHANGED
  cohort_tranche = 1         0           1,307
  cohort_tranche NULL        0               0   ⚠ MUST STAY ZERO
jobs                        80           1,387   (+1,307, all `pending`)
ranking_runs           count 5, max 5     5, 5   ⚠ UNCHANGED
ranking_results              5               5   ⚠ UNCHANGED
target_scores              224             224   ⚠ UNCHANGED
protein_features       (untouched)   (untouched)  ⚠ nothing is scored or featurised
```

**Every ingested row:** `cohort_tranche == 1` · `ranking_run_id IS NULL` · `pdb_path IS NULL` ·
`mean_plddt IS NULL` · `span_aa` between **1 and 50** · `meta["tier"] == "local"` ·
`len(meta["sequence"]) == span_aa`.

⚠ **The slice is checked BEFORE the row is written** — `core/fold_reconcile.check_sliced_length`.
A slice disagreeing with its recorded length is a construction defect, and writing it would produce
1,307 plausible wrong artifacts.

## §4 — Idempotency, and what a re-run must not do

⚠ **Keyed on `(cohort_tranche, input_value)`.** A second run finds the existing rows and writes
nothing. **It must not create a second analysis for the same accession**, because 75 of the 82
cohort accessions also appear in the census and a duplicate would make `input_value` ambiguous on
the very join the leak guard just closed.

⚠ **A cohort row for the same accession is NOT a collision.** `P04626` may hold a tranche-0 row and
a tranche-1 row simultaneously — **that is the intended state**, and it is precisely why every
cohort surface is now tranche-filtered.

## §5 — ⚠ What would falsify this, and what halts the ingest

- **any change to the 80 tranche-0 rows** — count, `pdb_path`, `mean_plddt`, or `meta`
- **any row written with `cohort_tranche` 0 or NULL**
- **any row written with a non-NULL `ranking_run_id`**
- ⚠ **`ranking_runs`, `ranking_results` or `target_scores` moving at all** — nothing here scores
- **a sliced length disagreeing with `span_aa`**
- ⚠ **a span outside 1–50 aa appearing in tranche 1** — the partition would not be what D-083 says
- **a permission denial** → ⚠ stop-and-report with the command, the point, and the artifact's state

## §6 — Then, and only then: tranche 1 folds

**The worker is live and polling.** Once jobs exist it will claim them. ⚠ **The recipe is resolved
at claim time from `TIER_RECIPE['local']` = int8 / chunk 64**, and a fold completing without a
recorded recipe is a stop condition.

⚠ **Layer 2 is OFF by ruling** (uncapped, to get 440) and **layer 3 is not wired**, so the crank's
only protection is layer 1 — **which has never once been observed to fire.** Tranche 1's ≤50 aa
rows are where that exposure is smallest, and it is stated rather than assumed away.

**After the first 10 folds, reported before the rest run:** wall-clock per fold · peak VRAM
(`max_allocated` **and** `max_reserved`, neither standing for the other) · the recipe as recorded ·
and ⚠ **the three numbers — manifest `span_aa`, enqueue length, and the PDB's residue count.**

## §7 — ⚠ What must NOT move

**No fold of any of the 82** (`### D-081`) · **no census row scored, ranked or featurised**
(`### D-079` dec 1) · **no cross-recipe comparison read** (`### D-078` unwritten) · **the manifest is
not rebuilt** · **no hand-written SQL against production** — the ORM's models only.
