# ORDERS — Code — 2026-08-06 — CENSUS TASK 1: migration 0008 and the tranche column

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority. Check the `### D-NNN` / `### F-NNN` header, not a reference to it.

## ONE TASK, WITH TWO AMENDMENTS TO THE GOVERNING ORDER FIRST.
**If this document does not end with `— END OF CENSUS TASK 1 (1 of 1) —`, it truncated. Report and request re-delivery.**

---

> **Governed by `ORDERS-Code-2026-08-05-census-ingest-and-tranches-v2.md` §1, as amended below.**
> ⚠ **This document reproduces none of §1's substance, deliberately.** §1 already specifies 1a, 1b, 1c and its test table. **Where this document and §1 differ, §1 governs, and where §1 and `### D-079` differ, the log governs.** The only thing here that §1 does not contain is the two amendments — one because §1's own §0 has gone stale, one because A-017 did not exist when §1 was written.
>
> **Planner provenance (D-016):** §1 read at first hand from the `4b7547c` snapshot, 2026-08-06, with `app/reads.py` and `db/models.py` grepped rather than recalled. **No connector, no `.git`, no database.**

---

## AUTHORISATION LIMITS — READ FIRST

**Authorises:** migration `0008` and the tranche column per §1 · the four tests in §1's table, upgraded per Amendment 2 · the `RESERVED.md` pagination deferral (§1c) · applying `0008` to production.

**Does NOT authorise:**
- ⚠ **Any census row.** §1 ships *before* any census row can exist. `protein_analyses` is still the 82-row cohort and stays that way until Task 5.
- ⚠ **Census Tasks 2, 3, 4, 4a, 4b or 5.** Task 2 gets written against what Task 1 actually builds, not ahead of it.
- ⚠ **Any fold, any enqueue, any scorer run, any ablation.** Not Run B. Not the wiring PR.
- any write to `ranking_runs`, `ranking_results`, `target_scores`, `protein_features`, or to `ranking_run` ids 2–5.

## STOP AND REPORT

- §0 as amended fails on any item
- the migration would be anything other than **additive and nullable**
- any test in §1's table cannot be made to red at its own assertion
- applying `0008` requires touching an existing row's data beyond the backfill §1b specifies

---

# AMENDMENT 1 — §0's confirmations have gone stale, and two of them now self-fail

⚠ **§0 as written will stop-and-report on its own confirmations.** Do not work around it; use the amended list.

**§0.1 — "Is PR #122 merged?"** ✅ Merged. **But `main` is now `1d0c91a` (#127)**, and #128 and #129 are open. **Amended:** confirm `main`'s hash and report it, and confirm that whichever base you branch from is **merged, not stacked** — a migration must not branch off an open chain. ⚠ **Do not merge #128 or #129 to satisfy this.** Branch from `main`.

**§0.2 — "Confirm `D-079` and `F-017` are free."** ⚠ **Both are now WRITTEN.** `### D-079` landed 2026-08-05; `### F-017` is landing today. **A confirmation that they are free is now guaranteed to fail and means the opposite of what it did when written.** **Amended:** confirm `### D-079` and `### F-017` **both resolve to real `###` entries**, and that the checker returns `UNRESOLVED AND UNRESERVED: none — invariant holds`. **Confirm the next free `F-` integer at the time and report it** — do not assume it.

**§0.3 — migration state, column by column.** ✅ Still correct as written and still required. **`alembic_version` and `membrane_proximal_sasa` read separately, disagreement is stop-and-report.** ⚠ **Amended addition:** report the head **before** `0008` and **after**, separately. §1a's *"apply 0007"* is already satisfied — 0007 was applied 2026-08-05 — so **1a becomes a verification, not an application.**

---

# AMENDMENT 2 — §1's test table predates A-017. It is A-016 only.

§1's table gives four tests, each with a *"prove it bites by"* revert. **That is A-016 — the revert must be a realistic mistake and must fail at the assertion.** ⚠ **A-017 did not exist when §1 was written.** It was earned on 2026-08-05, across five instances and two agents, and is now a **gate requirement**.

**Every test in §1's table additionally satisfies all three A-017 clauses:**

**(a) The fixture reaches the code under test.** A red can fire at exactly the right assertion and still prove nothing if the path was never entered. ⚠ The originating instance: a revert redded at `DID NOT RAISE` because the fixture had no positives, so `run_scorer` raised before reaching the code the test was about — **and it would have passed under a guard placed anywhere.** For `test_every_enumerating_route_filters`, assert the route walk finds a **non-zero** number of routes; **a walk that silently matches nothing passes everything.**

**(b) One property, one test.** A compound test proves only its first failing assertion. ⚠ `test_null_tag_is_a_category_not_a_default` carries **two** properties — that a null is excluded from tranche-zero reads, **and** that nothing coerces null → zero. **Split them.**

**(c) The fixture contains a case where correct and incorrect differ.** ⚠ This is the one that bites here. `test_backfill_tags_every_existing_row` reverts by backfilling `WHERE pdb_path IS NOT NULL` — **which only reds if the fixture contains a row with a null `pdb_path`.** In production that row is **IGF2R**. **The fixture must contain the equivalent, or the revert reds nowhere and the test reads as coverage.** State in the test which fixture row plays that part.

⚠ **Report the exact location each revert reds at** — file and line — **not that it redded.** An error-red and a failure-red are different objects and only the second proves the assertion ran.

---

# THE TASK

**Execute `ORDERS-Code-2026-08-05-census-ingest-and-tranches-v2.md` §1** — 1a (now a verification), 1b, 1c and the test table — **as amended above, and by nothing else.**

**Two standing constraints from §1 that carry the whole point of the task:**

- **`protein_analyses` *is* the cohort today.** `app/reads.py`'s `list_analyses` is unfiltered and unpaginated, and `TargetList.jsx` renders whatever it returns — **so an ingest without this migration makes the target list silently become the census.** Silently is the operative word.
- **The tag is nullable because a null is a CATEGORY.** Untagged is *unclassified*, not a census member and not tranche zero. ⚠ **An absent value is never a low number, never a default, never a bare null with no reason.**

**Tests first. No deploy to Fly on anything that has not passed the gate.**

---

## PRE-REGISTRATION (F-022)

⚠ **Write your expected post-state before you write the migration, and send it before the Planner's.** The Planner's is deliberately absent from this document — that ordering is the remedy for the F-022 defect you caught in #129, where a pre-registration and the instruction not to read it sat in one linear document.

⚠ **State a COMPOSITION, never only a total.** On 2026-08-06 a Planner prediction of *"22"* was numerically correct and **wrong in every underlying term** — a false exclusion and a self-contradicting count that happened to cancel. **A matching total concealed four defects.** Terms that can be checked term by term, or the prediction is unfalsifiable by the arithmetic that appears to confirm it.

**At minimum, state separately:** rows in `protein_analyses` before and after · rows carrying tranche zero · rows carrying null · `alembic_version` before and after · which tables are untouched.

## REPORT BACK

Plain lines, one item per line. **No box-drawing tables** — five consecutive reports have had their middle columns eaten.

1. §0 as amended — each item's literal value, including `main`'s hash and the next free `F-` integer
2. Your pre-registration, sent before the Planner's
3. The four (now five, after the split) tests, each with the **file and line its revert redded at**
4. `alembic_version` before and after `0008`, and the column verified separately
5. Row counts: `protein_analyses` total, tranche zero, null
6. Gate count before and after
7. Confirmation that `ranking_runs` is still **(5,5)** and no census row exists

⚠ **Then stop.** After Task 1 the obvious next command is Task 2. **It gets written against what Task 1 built.** Close the window.

---

## WHAT IS STILL OPEN AND DOES NOT BLOCK THIS

- **The scoring gate's reading** — *"no census row is scored before D-075 fires."* ⚠ **It gates scoring, not folding, so it does not hold Task 1 or the crank.** Owner ruling outstanding.
- **F-024 / findings numbering** — three queued for one integer.
- **KEEL v6 into the repository** — and the A- reconciliation, which still cannot be run: the register as delivered defines the schema but **does not enumerate the numbered items**, so `A-014`, `A-016` and `A-017` remain unreconciled.

— END OF CENSUS TASK 1 (1 of 1) —
