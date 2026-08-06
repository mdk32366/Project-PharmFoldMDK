# ORDERS — Code — 2026-08-06 — RECONCILIATION QUERIES. Read-only. Two questions.

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority. Check the `### D-NNN` / `### F-NNN` header, not a reference to it.

## ONE TASK, TWO QUERIES.
**If this document does not end with `— END OF RECONCILIATION QUERIES (1 of 1) —`, it truncated. Report and request re-delivery.**

---

> **Planner provenance (D-016):** counts below were computed by the Planner from the `4b7547c` snapshot on 2026-08-06, by grep against `docs/README.md`. ⚠ **That snapshot is `#128`'s branch, not `main`** — which is itself one of the candidate explanations for the discrepancy. **No connector, no `.git`, no database.**

---

## AUTHORISATION LIMITS — READ FIRST

**Authorises:** running the read-only commands below and reporting their literal output.

**Does NOT authorise:** any file created, edited, committed, merged, or rebased · any migration · any fold · any scorer run · any production write. ⚠ **Not Run B. Not the wiring PR. Not the freeze.**

⚠ **This document does not restate `ORDERS-Code-2026-08-06-census-task-1.md` and does not supersede it.** That file governs Task 1. **Two documents specifying one task is the defect class this project has spent two sessions on** — this one is queries only.

## STOP AND REPORT

- either query requires editing anything to answer
- Query 1's answer is `PENDING` — that is a real finding, see below

---

# QUERY 1 — Did the Pearson land, or did a placeholder commit?

**The situation.** The `RESERVED.md` checker now reports the reserved set at **14**, down from 15. The only way that happens is **`F-017` was struck**, which means `### F-017` was committed. **No report on the F-017 orders has reached the Planner** — no Task 0 result, no commit hash, no Decision 6 items.

**The specific risk.** `ORDERS-Code-2026-08-06-F017-and-decision-6.md` Task 1 contains the literal string `[PENDING — TASK 0]` in the correlation table, and Task 0 — the feature 7 × feature 4 **Pearson** over the 56 ranking-set rows — was the thing that was supposed to replace it. **The order forbade committing with a placeholder.** ⚠ **A placeholder inside a written log entry is the shape that gets read as complete six weeks later**, and it sits in the one table whose job is to state a limitation honestly.

**Answer both parts:**

**1a.** Grep the committed `### F-017` entry for `PENDING`. Report the literal result — the matching line, or `no match`.

**1b.** If no match: report the **Pearson coefficient and its n** as committed. If it matched: ⚠ **report that and stop working on anything else** — F-017 must be corrected before it is cited, and the correction is recorded in the open, never quietly patched.

**Also report, one line each, since none of it has arrived:**
- `### F-017`'s commit hash
- whether **Decision 6's two additions** (fold-recipe heterogeneity; the coordinate-mediated correlation) are committed, and where
- whether the **wiring PR** (Task 4) has been started, and if so, its state

---

# QUERY 2 — The entry count: 97 against 101

**The report said `97 log entries unchanged` and `15 decision headers unchanged`. The Planner computes neither number from the snapshot.**

**Planner's measurement, `docs/README.md`, `4b7547c`:**

```
### D-    77
### F-    13
### S-     5
### DEP-   6
### A-     0
                                    -> 101 by the checker's own regex
all ### entries, any prefix          -> 103
#### sub-headers, whole file         -> 225
#### sub-headers inside ### D-075    ->   8   (9 after the Run B amendment)
```

⚠ **97 matches no population the Planner can construct** — not 101, not 103, not 101 minus the entries that changed. **15 does not match D-075's sub-header count either.**

⚠ **Do not explain the gap. Send the composition and let the arithmetic settle it.** Two competing stories were constructed in this arc and **both were wrong**; what closed it was a list of names, not a better story.

**Report exactly this, computed on your current branch:**

```
### D-      <n>
### F-      <n>
### S-      <n>
### DEP-    <n>
### A-      <n>
all ###     <n>
checker-defined set size  <n>
```

**And in one line: what population `97` counted, and what population `15` counted.**

⚠ **Both of your numbers may be perfectly correct measurements of something the Planner has not identified.** That is the likeliest explanation and it is not a criticism — **it is precisely why a count cannot be checked against a count.** If the breakdowns close, they close in one line.

**Note the branch difference explicitly:** the Planner's figures are from `#128`'s branch; yours are from `main` plus whatever is stacked. ⚠ **If that is the explanation, say so with the diff** — and **do not merge anything to make the numbers agree.** Merging to reconcile a figure is fitting the world to the forecast, refused twice already in this arc and refused again here.

---

## REPORT BACK

Plain lines, one item per line. **No box-drawing tables** — five consecutive reports have had their middle columns eaten. `label | value` on one line survives.

1. Query 1a — the literal grep result
2. Query 1b — the Pearson and its n, **or** the placeholder finding
3. `### F-017` hash · Decision 6 state · wiring PR state
4. Query 2 — the seven-line breakdown
5. What `97` and `15` counted

---

## THEN

⚠ **Neither query blocks the migration.** `ORDERS-Code-2026-08-06-census-task-1.md` governs Task 1 and is ready to run — it touches no file either query reads.

**Its amended §0 asks for `main`'s hash and the next free `F-` integer confirmed at the time rather than assumed.** ⚠ **That confirmation answers part of Query 2 for free** — if `F-` is at 15 by your count and 13+2 by the Planner's, the two land on the same line and the discrepancy resolves without a separate investigation.

**Order of work: these two queries (minutes), then Task 1.** After Task 1 the obvious next command is Task 2 — **it gets written against what Task 1 actually built. Close the window.**

---

## STILL OPEN, AND NONE OF IT BLOCKS THE CRANK

- **The scoring gate's reading** — *"no census row is scored before D-075 fires."* ⚠ Gates **scoring**, not folding. Owner ruling outstanding.
- **F-024 and findings numbering** — three findings queued for one free integer. ⚠ **No number is taken under pressure**; that is the F-017 double-claim seen coming.
- **KEEL v6 into the repository** — and the A- reconciliation, which **still cannot run**: the register as delivered defines the schema and the bar but **does not enumerate the numbered items**, so `A-014`, `A-016` and `A-017` remain unreconciled and `A-017` remains provisional while being a gate requirement.
- **KEEL-4 is a proposal for owner ruling**, not a ratified document — Principle 11 and the fifth document are both unruled.

— END OF RECONCILIATION QUERIES (1 of 1) —
