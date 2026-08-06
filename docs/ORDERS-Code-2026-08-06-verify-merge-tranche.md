# ORDERS — Code — 2026-08-06 — VERIFY, MERGE, THEN THE TRANCHE COLUMN

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority. Check the `### D-NNN` / `### F-NNN` header, not a reference to it.

## THREE TASKS: 0, 1, 2. Sequential. Hard stop between each.
**If this document does not end with `— END OF ORDERS (3 of 3) —`, it truncated. Report and request re-delivery.**

---

> ## ⚠ THIS DOCUMENT SUPERSEDES `ORDERS-Code-2026-08-06-census-task-1.md`
>
> That file's §0 required confirming `### F-017` resolves — **and `F-017` is on the stack, not on `main`, which is the only base a migration may branch from.** A Planner defect: a stale confirmation amended into a differently-stale one.
>
> **Do not execute both documents. This one governs.** Two documents specifying one task is the defect class this project has spent three sessions on. Its Amendment 2 (the A-017 upgrade to the test table) is carried forward below **unchanged in substance**; nothing else from it survives.

> **Planner provenance (D-016):** all Planner-side counts computed by grep against the `4b7547c` snapshot, 2026-08-06. ⚠ **That snapshot is `#128`'s branch, not `main`.** **No connector, no `.git`, no database.** Every production and PR fact below is Code's or the owner's, never the Planner's.

---

## AUTHORISATION LIMITS — READ FIRST

**Authorises:** three read-only verifications (Task 0) · merging four already-gated PRs (Task 1) · migration `0008` and the tranche column per the governing census order §1 (Task 2), including applying `0008` to production.

**Does NOT authorise:**
- ⚠ **Any census row.** `protein_analyses` is still the 82-row cohort and stays so until census Task 5.
- ⚠ **Census Tasks 2, 3, 4, 4a, 4b, 5.** Task 2 gets written against what Task 1 actually builds.
- ⚠ **Run B. The wiring PR. The freeze.** Not started, not authorised here.
- any fold, any enqueue, any scorer run, any ablation
- any write to `ranking_runs`, `ranking_results`, `target_scores`, `protein_features`, or to `ranking_run` ids 2–5

## STOP AND REPORT — do not work around

- **Task 0's amendment query shows a ruling missing from `### D-075`** — this gates Task 1 and is the most serious outcome in this document
- the `e41ce85` diff is **not purely additive**
- any PR in Task 1 fails its own gate, or merging requires a force-push, a rebase over a merged commit, or a conflict resolution that edits a sealed document
- the migration would be anything other than **additive and nullable**
- any test in the governing §1 table cannot be made to red **at its own assertion**

---

# TASK 0 — Three verifications. Read-only. Minutes.

## 0a — ⚠ Did the Run B amendment commit in full?

**The arithmetic does not close.** `### D-075` in the Planner's snapshot, before any 2026-08-06 edit: **20,860 chars** LF-normalised (273 lines; 21,133 with CRLF). You report **22,794**.

```
20,860 + 4,858 (amendment, LF)   = 25,718     reported 22,794    short 2,924
21,133 + 4,923 (amendment, CRLF) = 26,056     reported 22,794    short 3,262
20,860 + 1,934                   = 22,794     exactly — about the size of Decision 6's two items alone
```

⚠ **Three candidates and the Planner cannot distinguish them:** the 22,794 measurement predates `e41ce85`; the amendment committed substantially shortened; or it landed outside `### D-075`. **Do not explain the gap — report the composition.**

**Report:**
1. the **byte length** of the committed amendment block, from `#### ⚠ RUN B PRE-REGISTRATION` to the end of its final paragraph
2. **grep inside `### D-075` for each of these four strings, hit or miss, one line each:** `Ruling 1 —` · `Ruling 2 —` · `Ruling 3 —` · `Ruling 4 —`
3. the commit at which 22,794 was measured

⚠ **Why this outranks everything else in this document.** The Run B pre-registration's entire value is its committed content, written in the one window where no proxy value existed. **If a ruling did not land, the free parameter it closed is open again and the window is gone.** ⚠ **If any of the four is a miss: STOP. Do not merge. Report.**

## 0b — Prove Decisions 0–6 untouched, properly this time

The header count could not have caught an edit — prose can change without moving a `####`. **Wrong population *and* wrong property; the population error was the survivable one.**

```
git diff e41ce85^ e41ce85 -- docs/README.md
```

**Confirm it is purely additive: no `-` lines.** Report the added/removed line counts. ⚠ **That proves the property the header count only appeared to.**

## 0c — The base, stated

Report `main`'s hash, and for each of **#128 · #129 · `4ad9b02` · `e41ce85`**: its branch name, its gate state, and whether it is ready to merge **on its own merits**. One line each.

**Then stop and report Task 0 before touching Task 1.**

---

# TASK 1 — Merge the stack, in order, on merits

⚠ **The ruling, and the reason it is not the thing refused twice.** Merging to make a forecast come true was refused for #128 and again for the entry counts. **The test is whether a merge changes a claim's truth value or only its location.** Nothing here changes a truth value: four finished, gated, docs-only PRs are open while a migration needs a clean base, and `main` currently lacks `F-020`, `F-017`, the landing headers, the header test, and the Run B pre-registration.

⚠ **And one thing that decays while it sits:** the pre-registration's force is *"committed before the data existed."* It is hashed and dated, so the claim survives on a branch — **but a pre-registration living only on an unmerged stack is one force-push from being arguable.** It should land.

**Merge in dependency order: #128 → #129 → `4ad9b02` → `e41ce85`.**

**Each merges on its own merits.** ⚠ **If any one fails its gate or conflicts in a way that would require editing a sealed document, STOP at that point and report.** Do not merge the rest around it, and do not resolve a conflict by rewriting a 2026-08-05 ruling — `RESERVED.md`'s forward-only rule stands.

**After the merges, report:**
- `main`'s new hash
- the checker's **literal output** and the reserved set size — expected `UNRESOLVED AND UNRESERVED: none — invariant holds`, set **14**
- gate count on main
- ⚠ **the seven-line entry breakdown on main** — `### D-` · `### F-` · `### S-` · `### DEP-` · `### A-` · all `###` · checker-defined set size. Expected `77 / 15 / 5 / 6 / 0 / 105 / 103`. **Report the literal values; if they differ, the difference is the finding.**
- confirmation that `### F-017` and `### D-079` both resolve **on main**

**Then stop and report Task 1 before touching Task 2.**

---

# TASK 2 — Census Task 1: migration 0008 and the tranche column

> **Governed by `ORDERS-Code-2026-08-05-census-ingest-and-tranches-v2.md` §1.**
> ⚠ **This document reproduces none of §1's substance, deliberately** — §1 already specifies 1a, 1b, 1c and its test table. **Where this document and §1 differ, §1 governs; where §1 and `### D-079` differ, the log governs.**

## 2a — §0 of the governing order, corrected against a merged base

⚠ **§0 as written has gone stale and self-fails. Use this list.**

**§0.1 — "Is #122 merged?"** ✅ Merged, and superseded: **branch from the `main` produced by Task 1.** Report the hash. ⚠ **A migration must not branch off an open chain** — after Task 1 there is no open chain, which is why Task 1 comes first.

**§0.2 — "Confirm `D-079` and `F-017` are free."** ⚠ **Both are now WRITTEN.** That confirmation is guaranteed to fail and means the opposite of what it did when authored. **Amended:** confirm both **resolve to real `###` entries on main**, that the checker returns `none — invariant holds`, and **report the next free `F-` integer confirmed against the live log — expected `F-024`, not assumed.**

**§0.3 — migration state, column by column.** ✅ Still required as written: `alembic_version` and `membrane_proximal_sasa` read **separately**; disagreement is stop-and-report. ⚠ **Addition:** report the head **before** and **after** `0008`, separately. **`0007` was applied 2026-08-05, so §1a is a verification, not an application.**

## 2b — The test table is A-016 only. It predates A-017 by a day.

§1's four tests each carry a *"prove it bites by"* revert — that is **A-016**: a realistic mistake, failing **at the assertion**. ⚠ **A-017 did not exist when §1 was written.** It was earned across five instances and two agents on 2026-08-05 and is now a **gate requirement**. **Every test in §1's table additionally satisfies all three clauses:**

**(a) The fixture reaches the code under test.** A red can fire at exactly the right assertion and prove nothing if the path was never entered. ⚠ The originating instance: a revert redded at `DID NOT RAISE` because the fixture had no positives, so `run_scorer` raised before reaching the code under test — **it would have passed under a guard placed anywhere.** For `test_every_enumerating_route_filters`, assert the route walk finds a **non-zero** number of routes; **a walk that silently matches nothing passes everything.**

**(b) One property, one test.** A compound test proves only its first failing assertion. ⚠ `test_null_tag_is_a_category_not_a_default` carries **two** properties — that a null is excluded from tranche-zero reads, **and** that nothing coerces null → zero. **Split them.**

**(c) The fixture contains a case where correct and incorrect differ.** ⚠ **This is the one that bites here.** `test_backfill_tags_every_existing_row` reverts by backfilling `WHERE pdb_path IS NOT NULL` — **which only reds if the fixture contains a row with a null `pdb_path`.** In production that row is **IGF2R**. **Without the equivalent in the fixture the revert reds nowhere and the test reads as coverage.** Name, in the test, which fixture row plays that part.

⚠ **Report the exact file and line each revert reds at — not that it redded.** An error-red and a failure-red are different objects; only the second proves the assertion ran.

## 2c — Execute

**Run the governing §1 — 1a (verification), 1b, 1c and the test table — as corrected above and by nothing else.**

**Two standing constraints from §1 that carry the point of the task:**

- **`protein_analyses` *is* the cohort today.** `app/reads.py`'s `list_analyses` is unfiltered and unpaginated and `TargetList.jsx` renders whatever it returns — **so an ingest without this migration makes the target list silently become the census.** *Silently* is the operative word.
- **The tag is nullable because a null is a CATEGORY.** Untagged is *unclassified* — not a census member, not tranche zero. ⚠ **An absent value is never a low number, never a default, never a bare null.**

**Tests first. Nothing deploys to Fly that has not passed the gate.**

## 2d — Pre-registration (F-022)

⚠ **Write your expected post-state before you write the migration, and send it before the Planner's.** The Planner's is deliberately absent from this document — the remedy for the F-022 defect you caught in #129, where a pre-registration and the instruction not to read it sat in one linear document.

⚠ **State a COMPOSITION, never only a total.** On 2026-08-06 a Planner prediction of *"22"* was numerically correct and **wrong in every underlying term** — a false exclusion and a self-contradicting count that happened to cancel. **A matching total concealed four defects.**

**State separately, at minimum:** rows in `protein_analyses` before · after · carrying tranche zero · carrying null · `alembic_version` before and after · which tables are untouched.

---

## REPORT BACK

Plain lines, `label | value`, one item per line. **No box-drawing tables** — six consecutive reports have lost their middle columns.

**Task 0:** amendment byte length · the four `Ruling N —` hits/misses · the commit 22,794 was measured at · the `e41ce85` diff's added/removed counts · the four PRs' branch, gate, readiness

**Task 1:** new `main` hash · checker literal output · reserved set size · gate count · the seven-line entry breakdown · `F-017` and `D-079` resolve on main

**Task 2:** amended §0's literal values incl. next free `F-` · your pre-registration (sent first) · each test with the **file and line its revert redded at** · `alembic_version` before and after · `protein_analyses` total / tranche-zero / null · gate before and after · confirmation `ranking_runs` is still **(5,5)** and **no census row exists**

⚠ **Then stop.** After Task 2 the obvious next command is census Task 2. **It gets written against what this built.** Close the window.

---

## STILL OPEN, AND NONE OF IT BLOCKS THIS

- **The scoring gate's reading** — *"no census row is scored before D-075 fires."* ⚠ **Gates scoring, not folding.** Does not hold the tranche column or the crank. Owner ruling outstanding.
- **F-024 and findings numbering** — three findings queued for one free integer. ⚠ **No number taken under pressure**; that is the F-017 double-claim seen coming.
- **KEEL v6 into the repository** — and the A- reconciliation, which **still cannot run**: the register as delivered defines the schema and the bar but **does not enumerate the numbered items**, so `A-014`, `A-016` and `A-017` remain unreconciled while `A-017` is a gate requirement.
- **KEEL-4 is a proposal for owner ruling**, not ratified — Principle 11 and the fifth document are both unruled.
- **The four-document migration** — ⚠ KEEL-3 §8 now **names the target**: `architecture.md` · `decisions.md` · `findings.md` · `testplan.md`. The repo has `ARCHITECTURE.md` and `docs/Test_Plan.md`; **`decisions.md` and `findings.md` both live inside `docs/README.md`.** No longer an unknown target — a known one, unscheduled.

— END OF ORDERS (3 of 3) —
