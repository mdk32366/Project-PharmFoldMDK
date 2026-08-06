# ORDERS — Code — 2026-08-06 (amendment) — Resume the merge sequence; the stack is five

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority. Check the `### D-NNN` / `### F-NNN` header, not a reference to it.

> **AMENDS `ORDERS-Code-2026-08-06-verify-merge-tranche.md`. Does NOT supersede it, and restates none of it.** Where this file and that one differ on anything other than the three items below, **that one governs**; where either differs from `### D-079` or the governing census order §1, **the log and §1 govern.** ⚠ This file is an amendment, not authority. **Two documents specifying one task is the defect class this project has spent three sessions on** — nothing here is a second copy of anything there.

## THREE AMENDMENTS, THEN THE UNCHANGED SEQUENCE.
**If this document does not end with `— END OF AMENDMENT (3 of 3) —`, it truncated. Report and request re-delivery.**

> **Planner provenance (D-016):** written 2026-08-06 after Task 0 of `ORDERS-Code-2026-08-06-relocate-and-resume.md` completed at `eab1d63`. The block hash `363e5b3c…` and byte count `4916` were **computed independently by the Planner from the order document** and match Code's reading of the committed block — **two artifacts, neither derived from the other.** All PR states, gate counts, and database readings below are **Code's or the owner's**, never the Planner's. **No connector, no `.git`, no database.**

---

## AUTHORISATION LIMITS — READ FIRST

**Authorises:** exactly what `ORDERS-Code-2026-08-06-verify-merge-tranche.md` authorises — its Tasks 0b, 0c, 1 (the merges) and 2 (migration `0008` and the tranche column) — **as amended below and by nothing else.**

**Does NOT authorise:** ⚠ any census row · census Tasks 2–5 · Run B · the wiring PR · the freeze · any fold, enqueue, scorer run or ablation · any write to `ranking_runs`, `ranking_results`, `target_scores`, `protein_features`, or `ranking_run` ids 2–5.

⚠ **Do not re-run Task 0a of the amended document. It is answered.** ⚠ **Do not execute `ORDERS-Code-2026-08-06-census-task-1.md`; it is superseded and stays superseded.**

## STOP AND REPORT

- any PR fails its own gate, or a conflict resolution would require editing a sealed 2026-08-05 or 2026-08-06 document
- merging requires a force-push, a squash across the `e41ce85` / `eab1d63` pair, or a rebase over an already-merged commit
- the checker's output on the merged `main` is anything other than `UNRESOLVED AND UNRESERVED: none — invariant holds`
- the seven-line entry breakdown on `main` differs from the expectation in Amendment 3

---

# AMENDMENT 1 — The stack is five, not four, and two of them merge as a pair

`ORDERS-Code-2026-08-06-verify-merge-tranche.md` Task 0c and Task 1 name four: **#128 · #129 · `4ad9b02` · `e41ce85`.** **`eab1d63` — the relocation — is now on the stack.**

**Merge order, dependency order, each on its own merits:**

```
#128  →  #129  →  4ad9b02  →  e41ce85  →  eab1d63
```

⚠ **`e41ce85` and `eab1d63` merge as a PAIR, in that order, and neither is squashed into the other.** `e41ce85` appended the Run B pre-registration into `### D-071` by a slice terminator that matched the fifth `\n---\n\n### ` occurrence; `eab1d63` moved it to `### D-075` and restored `### D-071` byte-identical. **Both land. A reader sees the mistake and the correction, in order.**

⚠ **The temptation is to squash them so the record is clean. Refuse it.** Corrections are recorded explicitly and never quietly patched — a history where this never happened would be tidier and less true. **This is the same rule that kept `ranking_run` id=1 marked rather than overwritten.**

**Task 0c's report accordingly covers five, not four:** branch name, gate state, and readiness on its own merits — one line each.

---

# AMENDMENT 2 — Landing headers arrive with the document. This is a Planner fix, not yours.

⚠ **The gate has redded four times on documents placed without landing headers.** The header test enforces the convention on any dated artifact at or after `CONVENTION_FLOOR = 2026-08-05`, and every order, ruling, correction and amendment handed over since matches that pattern.

**The cause is upstream of the Builder: the Planner writes these documents and was not writing the header into them.** ⚠ **Four reds in a row is a Planner defect surfacing in the Builder's terminal.**

**From now on:** every Planner-authored document arrives with its landing header already in it — **this document included, as the block above the task list.** **You should not have to add one at commit.**

⚠ **If a document arrives without one, that is a Planner defect: report it and add the header rather than being blocked by it.** Do not treat a missing header as a reason to hold a commit.

---

# AMENDMENT 3 — The expected breakdown on the merged `main`, and one boundary ruling

**Task 1's report expects, on the merged `main`:**

```
### D-       77
### F-       15
### S-        5
### DEP-      6
### A-        0
all ###     105
checker-defined set size  103
checker output            UNRESOLVED AND UNRESERVED: none — invariant holds
reserved set size          15
```

⚠ **Reserved is 15, not 14** — `F-024` was reserved at Task 2 of the relocation order. **Report the literal values. A difference is the finding, not a formatting issue.**

**Also confirm on the merged `main`:** `### F-017` and `### D-079` both resolve · `### D-075`'s char count is **27,654** · the four `Ruling N —` strings are inside `### D-075` · `### D-071` matches `371e7127…`.

## ⚠ The boundary ruling, so it is not decided under pressure later

The first relocation attempt failed its hash because the block extraction scanned to the next `\n### ` and **swallowed the trailing `\n---` separator belonging to `### D-071`** — a four-character difference that an assertion reading *"D-071 is restored"* would have called success.

**Ruling: that is NOT a sixth instance of `F-024` and does not enter its row.** F-024 is *a pattern occurring more than once, matched without a uniqueness check, takes the wrong occurrence.* **This scan found the right occurrence and took the wrong boundary** — a delimiter between two entries belongs to one of them, and the slice claimed the neighbour's. ⚠ **Adjacent mechanism, different remedy. F-019's over-claim guard binds:** recruiting it would inflate F-024 with something that is not the same defect.

**What it does earn, recorded here and carried into the close-out unnumbered:** *derive from source, not from context.* The fix that worked was **re-extracting the block from the order document — the authoritative text — rather than inferring it from file boundaries.** That is the generalisation of derive-don't-inscribe, and it is what made the second attempt hash clean.

---

# THE SEQUENCE, UNCHANGED

**Resume `ORDERS-Code-2026-08-06-verify-merge-tranche.md` at Task 0b.** Everything below is that document's, not restated here:

1. **0b** — `git diff e41ce85^ e41ce85 -- docs/README.md`, confirm purely additive, report added/removed counts
2. **0c** — readiness of the five, one line each
3. **Task 1** — the merges, in the order at Amendment 1, each on its own merits, then the Amendment 3 report
4. **Task 2** — migration `0008` and the tranche column, per the governing census order §1, with that document's amended §0 and its A-017 upgrade to the test table

⚠ **Its Task 2 requirements stand unchanged and are not repeated here** — in particular clause **(c)**: `test_backfill_tags_every_existing_row`'s revert only reds if the fixture contains a row with a **null `pdb_path`** (IGF2R's equivalent), and **without it the revert reds nowhere and the test reads as coverage.**

⚠ **And its pre-registration requirement stands: a COMPOSITION, never only a total.** Rows before · after · tranche zero · null · `alembic_version` before and after · tables untouched. **A matching total concealed four defects this morning.**

## REPORT BACK

Plain lines, `label | value`. **No box-drawing tables** — seven consecutive reports have lost their middle columns.

⚠ **Then stop.** After the tranche column the obvious next command is census Task 2. **It gets written against what this built. Close the window.**

---

## STILL OPEN, AND NONE OF IT BLOCKS THIS

- **The scoring gate's reading** — *"no census row is scored before D-075 fires."* ⚠ **Gates scoring, not folding.** Owner ruling outstanding; does not hold the crank.
- **Findings numbering** — `F-024` reserved. **Two remain unnumbered:** the KEEL absence, and *a verification that shares an implementation with the code under test will agree with it.* Owner ruling outstanding. ⚠ **No number taken under pressure.**
- **`F-024`'s write** — now unblocked: the terminator was ad-hoc and is retired, so the instrument cannot exhibit the defect (D-074 satisfied). **Queued behind the tranche column, not before it.**
- **KEEL v6 into the repository**, and the A- reconciliation, which still cannot run — the register defines the schema and the bar but **does not enumerate the numbered items**, so `A-014`, `A-016`, `A-017` remain unreconciled while `A-017` is a gate requirement. **KEEL-4 is a proposal for owner ruling, not ratified.**
- **The four-document migration** — target now **known** from KEEL-3 §8 (`architecture.md · decisions.md · findings.md · testplan.md`); the repo has two, with `decisions.md` and `findings.md` both inside `docs/README.md`. Unscheduled.

— END OF AMENDMENT (3 of 3) —
