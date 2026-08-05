# AMENDMENT to D-079 (v2) — 2026-08-05 — The census key, the three-site status vocabulary, and where the Task-2/3 ruling lands

> **COMMITTED 2026-08-05 with `### D-079` (`docs/README.md`). CITED BY the log, not restated in it —
> where this file and the log differ, THE LOG GOVERNS.** ⚠ This file is provenance for a decision that
> lives in the log; it is not itself authority. Check the `### D-079` header, not a reference to it.

> **Lands in #1's docs-only commit, alongside `RULINGS-2026-08-05-task2-task3-contract.md` and
> `D-078`'s trigger amendment.** Code's placement recommendation is adopted: the ruling and its
> standing consequence are repository text, not chat text, before Task 2 resumes.
>
> **Raised by Code**, checkpoint 3, 2026-08-05, from a re-count that reproduced every Planner figure
> and then found the figures could not both be keys. **Verified by the Planner against
> `membraneome-reconstructed-2026-08-04.csv` (sha256 `5a705cc9…`) on 2026-08-05.**

---

## §1 — The contradiction, and it is inside one unmerged entry

**D-079 v2 decision 5** says: *"The CSV's accession column is the source of record."*
**D-079 v2 §Denominator** says: *"the census is the 2,807 distinct current accessions."*

The CSV has **two** accession columns, and the entire 2,886 → 2,807 collapse lives in the difference:

| Column | surface | non_surface | unclassified |
|---|---|---|---|
| `UniProt Accession` (as SURFY published it) | **2,886** | 2,216 | 2,801 |
| `uniprot_current_accession` | **2,807** | 2,211 | 2,795 |

Read literally, decision 5 points at the first column and keys the census at 2,886. §Denominator
fixes it at 2,807. **They cannot both be `census_accession`.**

**⚠ The ambiguity is the Planner's and it is not a misreading.** What decision 5 *meant* was *the
CSV — rather than a fresh UniProt derivation — is the source of record for identity*, which is an
argument about **which artifact**, not about **which column**. It was written as though those were
the same statement. **Every count states its key; this key was never stated.** Fourteenth item in the
same family — two things that must agree, in one document, with nothing comparing them.

---

## §2 — RULING: the census row is a **protein**, keyed by the current accession

**`census_accession` = `uniprot_current_accession`.** The surface census is **2,807 rows**, not 2,886.

**Measured structure of the collapse** (Planner, 2026-08-05, off the CSV): **four** current
accessions absorb **83** source rows — `P01889` ×35, `P04439` ×21, `P10321` ×14, `P01911` ×13. All
four are HLA loci. 2,886 − 79 = 2,807.

**Why this way, and the reason is not tidiness:**

1. **A census keyed by identifier would fold HLA-B thirty-five times.** Same protein, same sequence,
   thirty-five identical folds — 79 wasted folds, which is the small part.
2. **⚠ The large part is the weighting.** Every census statistic would carry HLA-B at 35×, HLA-A at
   21×, HLA-C at 14×, HLA-DRB1 at 13× — **83 rows for four proteins, all of one family, with closely
   related ECD geometry.** The census's headline use is the confidence distribution at n in the
   thousands. **A single protein family silently weighted 83-fold sits directly inside that
   measurement.**
3. **A merged accession is not a reliable fetch key.** Sequence and topology are pulled by
   accession; the current accession is what UniProt serves today.
4. **"Identifiers are not proteins" is already the project's own ruling** (F-016). This applies it
   to the row rather than only to the count.

**Nothing is dropped.** Each census row carries **`source_identifiers`** — the list of SURFY entry
names and source accessions that map to it. The four HLA rows carry 35, 21, 14, and 13 respectively.
⚠ **A collapse that loses its inputs is a deletion**; the provenance back to SURFY's published table
must survive on the row.

**The same rule applies to the annex** (2,211) and to the unclassified set (2,795). Three tags,
three denominators, **never summed**.

**⟡ Decision 5 is amended to read:** *the reconstructed CSV — not a fresh UniProt derivation — is the
source of record for identity; the operative census key is its `uniprot_current_accession` column,
and `UniProt Accession` is retained as provenance.*

---

## §3 — RULING: two axes, named separately, never overloaded

Code's contract work exposed a second conflation. Task 2 produces two different kinds of fact and my
ruling gave them one column:

| Axis | Question | Nature |
|---|---|---|
| **`verification_bucket`** | Does the CSV's accession agree with UniProt's? | **A finding.** Reported, never acted on. `agrees` · `source_only` · `uniprot_only` · `disagrees` · `unresolvable` |
| **`census_identity_status`** | Can this protein be fetched and counted? | **Operational.** Consumed by the pipeline. |
| **`fetch_eligible`** | Boolean, derived by the producer from the two above | The fetch gate, and only the fetch gate |

⚠ **A verification bucket must never gate a fetch.** `disagrees` is a fact about our sources, not a
statement that the protein is unfetchable — and if it gated the pipeline, a disagreement would
silently shrink the census. That is the F-009 error arriving through a column name.

---

## §4 — RULING: one vocabulary, one constant, three sites

**Code found the third site and it is the worst one.** `core/census.py:97` also defaults a missing
status to `"resolved"`, and `categorise()`'s vocabulary is `{multi, unresolved, obsolete}` — **none
of the five new buckets match any key in it.**

⚠ **So under the new schema, `categorise()`'s identity-failure precedence stops firing silently.**
Its own docstring states *"identity failure wins — a multi row carrying a span is still multi"*, and
that rule would go quiet while the docstring continued to assert it. **A `disagrees` row would be
classified by span alone, called `local`, and folded.** ⚠ **This runs *after* the fetch, on the band
split Task 3 reports** — so `fetch_eligible` does not reach it. Code is right that it needs the same
treatment and that the ruling as issued did not cover it.

**Ruling:**

1. **`census_identity_status`'s vocabulary is a single module-level constant**, imported by
   `read_accession_map`, `census_spans.py`, and `core/census.py`. **Not three string comparisons
   agreeing by convention** — the two-vocabularies-in-three-places condition is removed
   structurally, not by care.
2. **All three sites refuse an unrecognised value.** No `or "resolved"` anywhere. **Deleted, not
   re-defaulted** — an absent status becoming an affirmative one is the defect, and a different
   default is the same defect at a different value.
3. **`F-018`'s scope widens to all three sites** and names the `categorise()` precedence failure
   specifically: *a precedence rule that stops firing because its vocabulary moved, while its
   docstring goes on asserting it.* Write it when the fix lands.

### Added to §3.3's contract tests

| Test | Assertion | Prove it bites by |
|---|---|---|
| `test_one_status_vocabulary_across_all_three_sites` | All three import the same constant; no site holds a literal status string | Re-introducing a literal → red |
| `test_identity_failure_still_wins_over_span` | A `disagrees`/`multi` row **carrying a valid span** is categorised by identity, not by span | Reverting precedence → red **on that row**, not on the majority |
| `test_census_row_count_equals_distinct_census_accessions` | Ingested surface rows == 2,807, and the four HLA rows carry 35/21/14/13 `source_identifiers` | Keying by identifier → red at 2,886 |

⚠ **The second test must name a specific row.** A test over the resolvable majority passes under both
the bug and the fix — the same reason F-010's test had to name IGF2R.

---

## §5 — Sequence

1. **Merge #122.** Then Code re-runs the confirmation block **against `main`**.
2. **#2, the D-075 run** — unaffected by any of this.
3. **#1's docs-only commit** carries: D-079 v2 · **this amendment** ·
   `RULINGS-2026-08-05-task2-task3-contract.md` · `CORRECTION-2026-08-05-D-075-order-decision-4.md`'s
   standing consequence · `D-078`'s amended trigger · `F-018`'s reservation.
4. **Task 2 resumes** under §2's key and §3's two axes.
5. **Task 3 starts** only after §4's and §3.3's tests are green and proven to bite.

---

## §6 — Recorded

**Three Planner defects in two days, all one family:** the F-017 double-claim, the producer/consumer
schema mismatch, and now a key that two sections of one entry defined differently. **All three were
found by Code reading the artifact rather than the reference to it, and all three were cheap because
nothing had merged.**

⚠ The standing consequence from the Task-2/3 ruling is extended: **an order or entry that names a
quantity must state its key, and where two sections name the same quantity, one of them must cite the
other rather than restate it.** Proposed to the assumption register when KEEL-4 lands against v6.
