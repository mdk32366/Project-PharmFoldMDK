# ORDERS — Code — 2026-08-06 (amendment) — Census Tasks 2 → 5: to the crank

> **AMENDS `ORDERS-Code-2026-08-05-census-ingest-and-tranches-v2.md` §2 through §5. Supersedes
> nothing and restates none of it.** Where this file and that one differ on anything other than the
> items below, **that one governs**; where either differs from `### D-079`, **THE LOG GOVERNS.**
> ⚠ This file is an amendment, not authority. **Check the `### D-079` header, not a reference to it.**

## FOUR AMENDMENTS, THEN THE UNCHANGED SEQUENCE.
**If this document does not end with `— END OF CENSUS AMENDMENT (4 of 4) —`, it truncated. Report and request re-delivery.**

> **Planner provenance (D-016):** §2–§5 read at first hand from the `4b7547c` snapshot, 2026-08-06.
> **No connector, no `.git`, no database.** All production state below is **Code's or the owner's.**

---

## AUTHORISATION LIMITS — READ FIRST

**Authorises:** census **Tasks 2, 3, 4, 4a, 4b and 5** per the governing order, as amended below — including ingest of the census rows and **enqueuing and folding tranche 1**.

**Does NOT authorise:**
- ⚠ **Any scoring, ranking, refitting, or feature extraction over census rows.** D-079 dec 1. **The scorer-import refusal test is what enforces it.**
- ⚠ **Reading the overlap comparison.** Fold the arms; `D-078` interprets them and is unwritten.
- **Run B · the wiring PR · the freeze.** Separate orders.
- **No re-fold of the 82.** F-008 forbids touching the reported cohort.
- **No UI work. No KEEL migration. No Arm A bisection** without the owner at the keyboard.

## STOP AND REPORT — any one halts the crank

- a fold completing **without a recorded recipe**
- a **VRAM failure below 440 aa at int8** — contradicts the known-good bound; gets its own F-entry
- a **census row appearing on a tranche-zero surface**
- a **pooled statistic emitted without its recipe composition**
- Task 2's buckets not partitioning the input
- ⚠ **the Task 2 → Task 3 contract test failing** (Amendment 3)

---

# AMENDMENT 1 — §0's confirmations, corrected once for all four tasks

⚠ **Do not re-run §0 per task. Run it once, here, and report.**

1. **Base:** branch from `main` **after `#130` (`c5df8b3`) and the tranche-column PR have merged.** Report the hash. ⚠ **A migration and an ingest must not branch off an open chain.**
2. **`### D-079` and `### F-017` both resolve on main** — ⚠ **§0.2's original "confirm they are free" is now guaranteed to fail and means its own opposite.** Checker returns `none — invariant holds`.
3. ⚠ **The next free `F-` integer, confirmed against the live log, not assumed.** `F-024` is reserved as of `0a719da`, so **expect `F-025`** — **report the literal value.** The Task 5 stop conditions need it and *"`F-017` is claimed by the D-075 result"* is now history rather than a caution.
4. **Migration state:** `alembic_version` **and** the tranche column, read **separately**. Disagreement is stop-and-report.
5. **`protein_analyses` is 80 rows, all tranche zero, none null. `ranking_runs` (5,5). Zero census rows.**

---

# AMENDMENT 2 — §2's counts are superseded. Use the ruled denominators.

§2 quotes Planner counts of **2,886 / 2,216 / 2,801** by identifier and **2,807 / 2,211 / 2,795** by accession. ⚠ **The by-accession figures are superseded by `RULINGS-2026-08-05-class-collision.md` and the D-079 key amendment.**

**The census key is `uniprot_current_accession`. The ruled denominators:**

```
surface          2,807
non_surface      2,209
unclassified     2,793
class_conflict       2
                 -----
                 7,811
```

⚠ **Four denominators. NEVER summed into a headline. Every count states its key.** The `class_conflict` bucket exists because a SURFY class is a property of the identifier, not of the protein — **F-019, n=2, a mechanism illustration and not a magnitude. It must not be recruited into any count, and it is not evidence for F-011.**

**§2's instruction stands unchanged: re-count before trusting.** ⚠ **Report what you measure. If your count differs from the ruled figures, that difference is the finding and the ingest stops** — these numbers reached the log through a correction and must not drift back.

---

# AMENDMENT 3 — ⚠ The Task 2 → Task 3 contract test. Named here, in the same order as both sides.

**This is the one thing I will not collapse, and it is the reason this is an amendment rather than a green light.**

On 2026-08-05 Task 2's output schema broke Task 3's consumer **silently** — no `accession` column, no bucket equal to `resolved` — so every span fetch would have been skipped and **the band split would have read `no_topology` for the entire census.** ⚠ **A resolvable target recorded as having no topology is fabrication, not smoothing.** It was found in committed code, by inspection, while executing something else.

**The contract, stated once and tested once:**

| Producer — Task 2 emits | Consumer — Task 3 requires |
|---|---|
| `data/census/accession_map.csv` | reads that path |
| columns `entry_name, source_accession, uniprot_accession, status, bucket, resolved_on` | reads `uniprot_accession` for the fetch key |
| bucket vocabulary, enumerated | matches against that **exact** vocabulary |
| the input CSV's **sha256** | records it in the span output |

**`tests/test_census_task2_task3_contract.py` — and it ships in the SAME PR as whichever side lands first.**

- **(a)** the fixture reaches the code — assert the consumer processes a **non-zero** number of rows. ⚠ **A consumer that silently skips everything passes every other assertion.**
- **(b)** one property, one test: *columns present* · *bucket vocabulary matches* · *non-zero rows fetched* are three tests.
- **(c)** ⚠ **the fixture contains a row the correct consumer fetches and the broken one skips.** Without it the contract test passes under the exact defect it exists to catch.
- **Prove by revert:** rename the accession column, or change one bucket value. **Red must fire at the assertion naming the missing column or the unmatched vocabulary — not at a collection error, and not at a row count that would drop under either implementation.** Report the **file and line**.

⚠ **F-018 is live in this path and its scope is exact:** `core/census.py:97` and `scripts/ecd_lengths.py:128` (`or "resolved"`), `scripts/census_spans.py:112` (the `== "resolved"` gate), plus `categorise()`'s precedence failure and four prose sites. **A CSV lacking a status column would have had every row treated as resolved.** ⚠ **Fix it in this PR, and the F-018 entry lands when the fix lands.** **Status wins over span. An absent status is a CATEGORY, never an affirmative one.**

---

# AMENDMENT 4 — A-017 across every test table in §2, §3, §4, §4a, §4b

Every table in the governing order gives a *"prove it bites by"* revert. **That is A-016.** ⚠ **A-017 did not exist when they were written and is now a gate requirement.** **Every test in every one of those tables additionally satisfies all three clauses:**

**(a) The fixture reaches the code.** A red can fire at the right assertion and prove nothing if the path was never entered. **Assert non-zero rows, non-zero routes, non-zero folds — as applicable — before asserting anything about them.**

**(b) One property, one test.** A compound test proves only its first failing assertion. ⚠ **`test_every_row_lands_in_exactly_one_bucket` carries two** — *partition* and *counts sum to the row count*. **Split them.**

**(c) The fixture contains a case where correct and incorrect differ.** ⚠ **Three that need naming explicitly:**
- `test_no_row_is_dropped_at_ingest` — the fixture **must** contain an `above_local` **and** a `no_topology` row. Without both, filtering by band at ingest reds nowhere.
- `test_igf2r_folded_analysis_id_is_null_and_that_is_correct` — ⚠ **§4b already says this and it is the model for the rest.** A test over the folded majority passes under both the bug and the fix; **IGF2R at 2,491 aa, CUDA OOM, is the row that separates them.** That is why F-010 survived this long.
- `test_pooled_statistic_carries_its_recipe_composition` — the fixture needs **two recipes present**, or a pooled mean is indistinguishable from a single-recipe mean.

**Report the file and line each revert reds at — not that it redded.** An error-red and a failure-red are different objects.

---

# THE SEQUENCE, UNCHANGED FROM THE GOVERNING ORDER

**Nothing below is restated here. Execute §2 → §3 → §4 → §4a/§4b → §5 as written.**

1. **Task 2** — accession verification. Five buckets, empties asserted at zero, disagreements reported not resolved. ⚠ **Owner-reserved: how `disagrees` and `multi` resolve. Report the list; do not pick.**
2. **Task 3** — spans over the **2,807**, disk-cached, rate-limited, run date and UniProt release recorded. ⚠ **`no_topology` is a CATEGORY, never a length, never `0`.** Annex (2,209) as a **separate file**. ⚠ **Do not pull the 2,793 unclassified** — different exclusion mechanism, and pulling them alongside invites their recruitment into F-011's thesis. **Band split counted off the file, ceiling recipe named. No proportion of the 82 multiplied by anything.**
3. **Task 4** — manifest: seed recorded **before the first shuffle**, source sha256, span run date, release, bands, tier assignment, seeded fold order. ⚠ **Bands choose the TIER, never whether a target folds.**
4. **Task 4a** — fp16 ceiling probe (`--dtype fp16` passed explicitly), overlap sample drawn beneath the measured ceiling, **sample size and seed recorded before the first overlap fold**. ⚠ **Determinism control FIRST and it is mandatory** — two folds at the same recipe, both arms, before any comparison. Without it, *"int8 differs from fp16"* and *"folding is nondeterministic"* are the same observation. ⚠ **Fold the arms; do not read the comparison. D-078 is unwritten.**
5. **Task 4b** — close F-010 by rename to `folded_analysis_id`, IGF2R named in the test, `ARCHITECTURE.md` updated in the same PR.
6. **Task 5** — ingest **2,807** with class, accession, span, band, tranche tag, **all of them including `above_local` and `no_topology`, flagged**. Annex and unclassified under their own tags, **never pooled**. **Enqueue tranche 1 = the `local` band**, seeded order, **recipe resolved at fold time from `TIER_RECIPE[tier]`, never from stored `inference_settings` (D-047)**. **Then start the crank.**

**After the first 10 folds, report:** wall-clock per fold · peak VRAM · recipe as recorded · any resolution failure. **Then run.**

## REPORT BACK

Plain lines, `label | value`. **No box-drawing tables** — nine consecutive reports have lost their middle columns.

**Amendment 1's five items · your measured denominators against the ruled four · the contract test's revert location · each test table's reverts by file and line · the manifest's seed and source hash before the first fold · the band split off the file · the first-10-folds report.**

⚠ **Pre-registration: yours, before you build, as a COMPOSITION never a total. The Planner's is deliberately absent and is not coming** — it added a wrong column count to the last one and nothing else.

---

## STILL OPEN, AND NONE OF IT BLOCKS THE CRANK

- **The scoring gate's reading** — *"no census row is scored before D-075 fires."* ⚠ **Gates scoring, not folding.** The scorer-import refusal enforces it either way. Owner ruling outstanding.
- **Findings numbering** — `F-024` reserved. **Four unnumbered:** the KEEL absence · a verification sharing an implementation with its subject · derive-from-source-not-context · **an order that asks for confirmation invites confirmation, where one stating an expected value invites comparison.**
- ⚠ **`fit_scorer.py:220-221` enumerates `protein_analyses` outside the route layer** — named, not fixed, and it bites the first time a census row gets features.
- **KEEL v6 into the repository** · the A- reconciliation, still impossible — the register defines the schema but **does not enumerate the numbered items.**

— END OF CENSUS AMENDMENT (4 of 4) —
