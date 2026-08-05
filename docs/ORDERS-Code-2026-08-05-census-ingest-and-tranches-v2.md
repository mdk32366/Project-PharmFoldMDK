# ORDERS — Code — 2026-08-05 (v2) — Ingest the census, tranche it, close F-010, turn the crank

> **COMMITTED 2026-08-05 with `### D-079` (`docs/README.md`). CITED BY the log, not restated in it —
> where this file and the log differ, THE LOG GOVERNS.** ⚠ This file is provenance for a decision that
> lives in the log; it is not itself authority. Check the `### D-079` header, not a reference to it.

> ⟡ **SUPERSEDES the v1 issue of 2026-08-05.** ⚠ **If you hold a v1 copy, hash both and discard v1.**
> Changes: §4 recipe rule replaced by owner ruling · §4a fp16 ceiling probe + overlap set added ·
> §4b F-010 rename added · a v1 §6 exclusion removed.
>
> **Planner provenance (D-016):** the `feafeff` snapshot, unzipped and read at first hand
> 2026-08-05, plus counts computed against `membraneome-reconstructed-2026-08-04.csv` in that
> session. **No GitHub connector.** No branch, PR, prod, or test-count claim below is Planner-verified.
>
> **`D-079-census-ingest-tranches-and-recipe-v2.md` merges before Task 2.** These orders are void if
> code precedes it.

---

## §0 — Confirm before doing anything

1. `git log --oneline -1` on `main` and `d077-local-fold-envelope`. **Is PR #122 merged?** If not,
   report and stop — Task 1 authors a migration and must not branch off an open chain.
2. **Run the `RESERVED.md` checker; read its output, not its exit code.** Confirm `D-079` and `F-017`
   are free.
3. **Migration state, column by column.** Report `alembic_version` **and** the presence/absence of
   `membrane_proximal_sasa` **separately**. Disagreement is stop-and-report.

---

## §1 — TASK 1 · Apply 0007, then ship the tranche column

**Ships before any census row can exist.** Not the same PR as an ingest; earlier.

**How known (D-016):** `app/reads.py:110-116` — `list_analyses` is
`select(ProteinAnalysis).order_by(ProteinAnalysis.id)`, unfiltered and unpaginated;
`ui/src/components/TargetList.jsx` renders whatever it returns. **`protein_analyses` *is* the cohort
today**, so an ingest without this makes the target list silently become the census.

**1a.** Apply **0007**. Verify by inspecting the column, then separately the `alembic_version` row.
Report both. ⚠ Alembic's exit code is not evidence.

**1b.** Migration **0008**: `protein_analyses` gains a **nullable** cohort/tranche tag, additive,
backfilling existing rows to **tranche zero**. Nullable because a null is a *category* — untagged is
unclassified, not a census member.

### Tests first (A-016: a realistic mistake, failing **at the assertion**, not at collection)

| Test | Assertion | Prove it bites by |
|---|---|---|
| `test_list_analyses_filters_to_tranche_zero` | A foreign-tranche fixture row does **not** appear | Removing the `.where(...)` |
| `test_every_enumerating_route_filters` | Route-table walk: every route returning a collection filters | Adding an unfiltered enumerating route |
| `test_backfill_tags_every_existing_row` | Zero null tags among the pre-existing 82 | Backfilling `WHERE pdb_path IS NOT NULL` → red on the fold-failed row |
| `test_null_tag_is_a_category_not_a_default` | An untagged row is excluded from tranche-zero reads | Coercing null → tranche zero |

**1c.** **Pagination is named, not built** — record in `RESERVED.md` as a known deferral.

---

## §2 — TASK 2 · Verify the accession column; do not re-derive it (D-079 dec 5)

⚠ **Supersedes §2 of `ORDERS-Code-2026-08-04-b-scale-readiness.md`**, which predates the
reconstructed membraneome and would create a second accession source with nothing comparing them.

**Planner counts, 2026-08-05 — re-count before trusting:** 7,903 rows · by identifier `surface`
2,886 / `non_surface` 2,216 / `unclassified` 2,801 · **by distinct current accession 2,807 / 2,211 /
2,795** · accession blank on **0** rows · `uniprot_status` `active_reviewed` 7,746 / `merged` 105 /
`inactive` 52.

| Test | Assertion | Prove it bites by |
|---|---|---|
| `test_every_row_lands_in_exactly_one_bucket` | `agrees ∪ source_only ∪ uniprot_only ∪ disagrees ∪ unresolvable` partitions the input; counts sum to the row count | Dropping a bucket |
| `test_disagreement_is_reported_not_resolved` | A seeded disagreement appears in `disagrees` with **both** values | Preferring either side |
| `test_empty_bucket_is_asserted_empty` | Every bucket key present at count 0 | Omitting a zero-count key |
| `test_no_accession_is_synthesized` | No path builds an accession from a string pattern | Adding a regex derivation |
| `test_rerun_is_byte_identical` | Second run reads cache | Re-querying |

Extend `scripts/accession_map.py`. Emit `data/census/accession_map.csv` with `entry_name,
source_accession, uniprot_accession, status, bucket, resolved_on`, plus a five-count summary and
**the input CSV's sha256** — a filename is not an identity. **Owner-reserved:** how `disagrees` and
`multi` resolve. Report the list; do not pick.

---

## §3 — TASK 3 · Pull census spans

Run `scripts/census_spans.py` over the **2,807 surface accessions**, disk-cached, rate-limited.

- Record **run date and UniProt release** in the output. Spans are versioned data.
- **`no_topology` is a category, never a length, never `0`.**
- Pull the **annex** (2,211 non_surface) as a **separate output file**. ⚠ **Do not pull the 2,795
  unclassified this session** — a different exclusion mechanism (F-016); pulling them alongside
  invites their later recruitment into F-011's thesis.

**Report the band split** — `local` / `unmeasured_band` / `above_local` / `no_topology` /
`unresolvable` — **counted off the file**, ceiling recipe named, run date named. **No proportion of
the 82 is multiplied by anything** (`core/census.py`'s standing refusal; a test asserts no
ratio-and-total path exists).

---

## §4 — TASK 4 · The census manifest ⟡ *(recipe rule replaced by owner ruling)*

⟡ **The v1 one-recipe rule is withdrawn.** The census folds every target it can reach, at whichever
tier reaches it, **with the recipe recorded on every fold** and the composition reported beside every
statistic (D-079 v2 dec 2).

```
seed:              <integer, recorded before the first shuffle>
source_sha256:     <membraneome CSV>
span_run_date:     <Task 3>
uniprot_release:   <Task 3>
bands:             {local, unmeasured_band, above_local, no_topology, unresolvable}
tier_assignment:   {band -> tier}          # bands choose the TIER, never whether a target folds
fold_order:        <seeded permutation, per band>
overlap:           {sample_size, seed, fp16_local_ceiling}   # §4a
```

| Test | Assertion | Prove it bites by |
|---|---|---|
| `test_fold_fails_without_a_recorded_recipe` | A fold path with no resolved recipe **raises**; it does not complete | Defaulting inside the fold |
| `test_recipe_is_resolved_at_fold_time_not_from_the_job` | The recipe comes from `TIER_RECIPE[tier]`, never from stored `inference_settings` (D-047) | Reading the job's hint |
| `test_fold_order_is_reproducible_from_the_seed` | Same seed → identical permutation | Unseeded `random` |
| `test_no_census_path_imports_the_scorer` | Neither ingest nor fold imports `core/scorer.py` or the fitter | Adding the import |
| `test_no_row_is_dropped_at_ingest` | An `above_local` and a `no_topology` row are both present, flagged | Filtering by band at ingest |
| ⟡ `test_pooled_statistic_carries_its_recipe_composition` | A combined confidence statistic without a per-recipe breakdown **raises** | Returning the pooled mean alone |

⚠ The last three are the D-079 decision-1, decision-3, and decision-2.5 guards. **They are what stop
this task spending the pre-registration, biasing the census, or publishing a pooled number**, and
they are the ones most likely to look redundant to a reader in a hurry.

---

## ⟡ §4a — TASK 4a · The fp16 local ceiling probe and the precision overlap set (D-079 v2 dec 7)

**Why:** under the owner's ruling the census spans two dtypes, and dtype is assigned by tier, which is
assigned by length, which is feature 1 — **perfectly confounded, no overlap.** Disclosure makes it
visible; only an overlap makes it separable. **This is not a gate on the crank; it runs alongside.**

1. **Probe the fp16 length ceiling on the local box** using `worker/ceiling_probe.py`. ⚠ **The probe
   defaults `--dtype fp16`** (it was written for the A6000) — that default is *correct* here and
   wrong everywhere else; pass it explicitly anyway so the invocation states its own recipe.
   The int8/chunk-64 reference is 440 aa at 6,665 MiB peak. **Report the fp16 ceiling; do not assume
   it.**
2. **Draw the overlap sample** from the `local` band **beneath the measured fp16 ceiling**, by the
   manifest seed, **sample size and seed recorded before the first overlap fold.**
3. **Fold each sampled target at both `(int8, 64)` and `(fp16, 64)`.** Same sequence, same chunking,
   **dtype as the only variable.**
4. ⚠ **Determinism control first, and it is mandatory** — two folds at the *same* recipe, both arms,
   before any comparison is read. Without it, *"int8 differs from fp16"* and *"folding is
   nondeterministic"* are the same observation. This was missing from the Task 1c order and it is not
   missing again.
5. **Do not read the comparison in this session.** Its design and frozen interpretation land as
   **`D-078`** — whose `RESERVED.md` trigger is amended from *"a raised local ceiling"* to *"the first
   census fold at a second precision."* Folding the arms is permitted; interpreting them is not,
   until D-078 is written and merged.

---

## ⟡ §4b — TASK 4b · Close F-010 by rename (owner ruling 3)

**Owner ruling:** option (b). Rename to **`folded_analysis_id`**, so the field states its own
population rule — D-074's own remedy. **Free now; impossible once the census consumes the field.**

⚠ **The test names IGF2R specifically.** A test over the folded majority passes under both the bug
and the fix, which is exactly why F-010 survived this long. IGF2R is fold-failed at 2,491 aa
(CUDA OOM) and is the row that separates them.

| Test | Assertion | Prove it bites by |
|---|---|---|
| `test_igf2r_folded_analysis_id_is_null_and_that_is_correct` | The renamed field is null for IGF2R, and the surface reads it as *not folded*, never as missing data | Reverting the rename → the assertion fails on the semantics, not on the column name |
| `test_no_consumer_reads_the_old_name` | Grep-equivalent over `app/`, `core/`, `ui/` finds no `analysis_id` consumer for this field | Leaving one call site |

Update `ARCHITECTURE.md` in the same PR — F-010's closure is a claim change, not a cosmetic one, and
D-074 keeps a finding open until the instrument stops exhibiting it.

---

## §5 — TASK 5 · Ingest, then turn the crank

1. Ingest the **2,807** with class, accession, span, band, tranche tag. **All of them**, including
   `above_local` and `no_topology`, flagged.
2. Ingest the **annex 2,211** and the **2,795 unclassified** under their own tags. **Never pooled.**
3. Enqueue **tranche 1 = the `local` band**, in seeded order, recipe resolved at fold time.
4. **Start the crank.** Report after the first 10 folds: wall-clock per fold, peak VRAM, recipe as
   recorded, and any resolution failure. Then run.

**Stop conditions — any one halts the crank and reports:** a fold completing without a recorded
recipe · a VRAM failure below 440 aa at int8 (contradicts the known-good bound → its own F-entry;
⚠ **`F-017` is claimed by the D-075 result** — confirm the next free number against `RESERVED.md` at
the time, do not assume) · a
census row appearing on a tranche-zero surface · a pooled statistic emitted without its recipe
composition.

---

## §6 — Out of scope, explicitly

- **No scoring, ranking, refitting, or feature extraction over census rows.** D-079 dec 1.
- **No reading of the overlap comparison.** Fold the arms; D-078 interprets them.
- ⟡ **No D-075 run in this session** — it has **its own orders**
  (`ORDERS-Code-2026-08-05-D-075-run.md`) and its own window.
- **No Task 3 Arm A bisection** (440–630, F-013) unless the owner is at the keyboard.
- **No re-fold of the 82.** F-008 forbids touching the reported cohort.
- **No KEEL Principle 7 migration** — owner ruled it a cleanup task after feature value, or
  tomorrow's pre-work.
- **No UI work.** The census does not reach a surface this session.

## §7 — Done when

0007 applied and column-verified · tranche column shipped, filtering revert-proven · accession
verification run, five buckets, empties asserted · spans pulled with run date and release, band split
read off the file · manifest written with seed and source hash **before** the first fold · recipe
recorded at fold time or the fold fails, revert-proven · scorer-import refusal green · pooled-statistic
guard green · F-010 closed by rename with IGF2R named in the test · fp16 ceiling probed, overlap
sample and seed recorded · 2,807 + 2,211 + 2,795 ingested with nothing dropped or pooled · tranche 1
folding in seeded order · gate green · **nothing scored, nothing ranked, nothing deployed.**
