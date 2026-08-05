# CORRECTION — 2026-08-05 — The sequence is wrong: #1 must precede #2, and my own two documents disagree

> **COMMITTED 2026-08-05 with `### D-079` (`docs/README.md`). CITED BY the log, not restated in it —
> where this file and the log differ, THE LOG GOVERNS.** ⚠ This file is provenance for a decision that
> lives in the log; it is not itself authority. Check the `### D-079` header, not a reference to it.

> **Supersedes the execution sequence in `META-ORDER-2026-08-05-paste-into-Code.md`.**
> **Apply before the merge.** Planner error, found while answering an owner question, **not** by Code.

---

## §1 — The contradiction, in two documents I wrote the same morning

| Document | Says |
|---|---|
| `META-ORDER-2026-08-05-paste-into-Code.md` | **FIRST #2** (the D-075 run) → **SECOND #1** (docs-only commit) |
| `ORDERS-Code-2026-08-05-D-075-run.md` §5 | *"**Reserve `F-017`** for the D-075 result in `RESERVED.md` **before the run**, so the number is not contested mid-session."* |

**`RESERVED.md` is amended by #1's docs-only commit.** So the meta-order schedules #2 before the
commit that satisfies #2's own precondition. ⚠ **Fourteenth instance of the same family: two things
that must agree, written in one sitting, with nothing comparing them** — and this one is a
*sequence* rather than a quantity, which is why none of the eight document reviews caught it.

---

## §2 — RULING: the corrected sequence

```
1.  Owner instructs the merge of PR #122 at 83f8d32          ← explicit, by hash
2.  Confirmation block re-run AGAINST main                    ← checker · D-079/F-017 · migration state
3.  #1 — the docs-only commit                                 ← was fourth; now third
4.  #2 — the D-075 run, its own session                       ← was first; now fourth
5.  #3 Task 2 → Task 3 behind its tests
```

**Three reasons, and the first alone is sufficient:**

1. **#2's §5 precondition lives in #1.** `RESERVED.md` must hold `F-017` before the run. Anything
   else means reserving a number inside the commit that consumes it.
2. **⚠ Nine documents produced today exist only as untracked files in one working tree.** KEEL
   Principle 8 — *continuity lives in the repository, never in the conversation* — and the working
   tree is nearer to the conversation than to the repository. **D-080's own prompt was uncommitted
   work in a tree.**
3. **A docs-only commit cannot disturb the D-075 run.** It touches no feature, no model, no
   migration. The original ordering bought nothing and cost the precondition.

---

## §3 — What #1's docs-only commit carries

All nine documents delivered 2026-08-05, plus these amendments in the same commit:

- `RESERVED.md`: **`D-078`'s trigger** amended to *"the first census fold at a second precision"*;
  **`F-017`** reserved (D-075 result); **`F-018`** reserved (the `or "resolved"` default, three
  sites, the `categorise()` precedence failure, **and the four prose sites**); **`F-019`** reserved
  (the class-collision finding — ⚠ n=2, mechanism not magnitude, not F-011 evidence).
- `RULINGS-2026-08-05-task2-task3-contract.md` **§3.1's `census_accession` row replaced by a
  pointer** to `SPEC-2026-08-05-accession-map-schema.md` §3 — not by a corrected definition.
- **`D-079` merged** as `### D-079` in `docs/README.md`, number re-confirmed against the live log at
  merge time. **Check the header, not the reference to it.**

⚠ **The rulings are not applied to code in this commit.** Nothing is built. The commit makes today's
decisions repository state; F-018's fix, the schema constants, and the tests all belong to #3.

---

## §4 — What the owner instruction should say, and why the wording matters

**Mechanically either Code or the owner can merge. What is owner-reserved is the decision, not the
keystroke.** Delegating the keystroke is fine; **Code merging on its own reading of *"it's ready"* is
not**, because that is the role split dissolving at its one load-bearing point.

So the instruction names the hash:

> *"Merge PR #122 at `83f8d32`. Owner authorisation, 2026-08-05."*

⚠ **`084517a` stays unsquashed** — it is the only repository evidence that D-080 was applied
(`CLOSEOUT-2026-08-04.md`).

---

## §5 — Recorded

**The eight preceding checkpoints each caught a defect in a *quantity, name, or vocabulary*.** This
one is in a **sequence**, and it survived every one of them — because a review reads a document
against the data, and a sequence is only wrong against *another document*.

**Standing consequence, added:** where two artifacts state an ordering, one states it and the other
cites it. **A precondition and the schedule that satisfies it may not be written in separate
documents.**
