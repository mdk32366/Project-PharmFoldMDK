# AMENDMENT — 2026-08-05 — Task C stop condition 2 was not evaluable, and the hash discipline needs a line-ending rule

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority. Check the `### D-NNN` / `### F-NNN` header, not a reference to it.

> **Amends `RULING-2026-08-05-A017-and-task-C-protocol.md` §4.2 only.** Binding before Task C runs.
> **Raised by Code**, checkpoint 3, before execution. **Both items are the Planner's.**

---

## §1 — ⚠ Stop condition 2 was wrong as written, not merely unreportable

The condition read: *"Proposed write count ≠ 56 ranking-set rows covered."*

**Code is right that the dry run will print 80, and right that 80 is correct.** `protein_features`
holds 80 rows; the ranking set is 56 of them; **the fill deliberately covers all 80, because dropping
the other 24 would filter the feature table by a fit-time predicate.**

**But the defect is worse than the output's granularity.** ⚠ **The condition as written would have
halted on the correct outcome.** It conflated **the fill's population** (every row with coordinates)
with **the guard's population** (the 56 the ablation refuses over). Those are different sets by
design, and the Planner wrote a gate that treated them as one.

**Corrected condition — two clauses, both checkable:**

| Clause | Halts when |
|---|---|
| **Fillable count < 80** | The fill's population is short of the feature table |
| **Ranking-set rows covered ≠ 56** | The guard's population is not wholly inside the fill |

## §2 — RULING: option 1. Make it evaluable before Task C runs.

**Code's reasoning is adopted verbatim:** *the point of a stop condition is that the owner can
evaluate it without a second source.*

⚠ **A gate the owner cannot read is not a gate; it is a post-hoc check wearing one.** The owner is at
the keyboard for this specific write *because* an independent halt is wanted before the bytes land —
and "Code will verify the coverage afterward" moves the check to the wrong side of the write. **Today
has produced three artifacts whose failure mode was plausibility; a coverage number confirmed after
the fact is exactly that shape.**

**Small follow-up PR:** the dry run reports **the ranking-set breakdown alongside the totals**, with a
test. Task C runs after it merges.

**Cost is one merge and nothing is blocked but time. Option 2 is defensible and is not taken.**

## §3 — The CRLF hash delta: a standing rule, because it will recur

Code found the delivered and committed hashes of the protocol document differ — **0 CRLFs delivered,
106 committed** — with the content byte-identical after normalising. **Git's `LF→CRLF` conversion on
checkout, not a delivery fault.**

⚠ **This matters beyond tonight.** The *"hash before use, a mismatch is stop-and-report"* discipline
is load-bearing on a channel that has failed three times today. **A rule that produces false alarms
on every text document trains people to ignore it** — and that is how a real mismatch gets waved
through.

**Ruled:** hash comparison for text documents is performed **on normalised line endings** (`LF`), and
a raw-byte mismatch that resolves under normalisation is **recorded, not escalated**. A mismatch that
survives normalisation is stop-and-report, unchanged.

**Lands with the other two environment findings** in the F-017 commit: `fly-user` cannot read
`pg_stat_activity` on Managed Postgres · `db/migrations/env.py` sets no `connect_timeout`.

## §4 — Still outstanding: the write invocation

⚠ **It has now been truncated twice in delivery and answered once from the wrong source.** Code
quoted `RULING-…-task-C-protocol.md` §C.3, which by design does not name flags — so the loop closed
on itself.

**What is needed is the CLI string from Code's own Task B work**, restated verbatim: the dry run
(understood to be `--all --fill-feature-7 --dry-run`, to be confirmed) **and the write.**

**No one infers it.** ⚠ The plausible guesses differ in whether `--ranking-run` becomes mandatory,
and the Planner reasoned its way to an obvious-looking production write command once today that
would have duplicated the table.
