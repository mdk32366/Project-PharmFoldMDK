# ORDERS — Code — 2026-08-06 — RELOCATE THE AMENDMENT, THEN RESUME

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority. Check the `### D-NNN` / `### F-NNN` header, not a reference to it.

## THREE TASKS: 0, 1, 2. Sequential. Hard stop between each.
**If this document does not end with `— END OF RELOCATION ORDERS (3 of 3) —`, it truncated. Report and request re-delivery.**

---

> ## ⚠ THIS DOES NOT SUPERSEDE `ORDERS-Code-2026-08-06-verify-merge-tranche.md`
>
> That document still governs **Task 0b, Task 0c, Task 1 (the merges) and Task 2 (the tranche column)**, unchanged. **This one is inserted in front of it**, because its Task 0a hit its own stop condition.
>
> **After Task 2 here, resume that document at its Task 0b.** ⚠ **Do not re-run its Task 0a** — it is answered. **And do not execute `ORDERS-Code-2026-08-06-census-task-1.md`; it is superseded and stays superseded.**

> **Planner provenance (D-016):** the misplacement, the offsets, and the byte counts below are **Code's readings**, reported 2026-08-06. The Planner's contribution was the arithmetic that exposed the gap — `20,860 + 4,858 = 25,718` against a reported `22,794` — computed by grep against the `4b7547c` snapshot. **No connector, no `.git`, no database.**

---

## AUTHORISATION LIMITS — READ FIRST

**Authorises:** one relocation commit to `docs/README.md` · disposition of the slice terminator per Task 1 · one `RESERVED.md` reservation.

**Does NOT authorise:**
- ⚠ **Any merge.** Not #128, not #129, not `4ad9b02`, not `e41ce85`. The merges resume in the prior document **after** this one completes.
- ⚠ **Any rewrite of `e41ce85`.** No rebase, no squash, no `--amend`, no force-push. See Task 0 constraint 1.
- ⚠ **Any edit to the amendment's text.** The content is correct and committed. **Only its location is wrong.**
- any census row · any migration · any fold · any scorer run · Run B · the wiring PR · the freeze
- any write to `ranking_runs`, `ranking_results`, `target_scores`, `protein_features`, or `ranking_run` ids 2–5

## STOP AND REPORT — do not work around

- `### D-071` does not hash byte-identical to its pre-`e41ce85` form after the move
- the amendment block does not appear **exactly once** in the file, before or after
- the relocated block's hash differs from the original by one byte
- placing the block requires computing an offset (see Task 0 constraint 3)

---

# TASK 0 — Relocate the block. Four constraints, and the third is the one that matters.

**The block is 4,920 bytes / 4,862 chars, committed in full at `e41ce85`, with all four rulings present. It sits inside `### D-071`, beginning at offset 144,177. Its correct home is the end of `### D-075` (spans 102,754 → 125,548).**

## Constraint 1 — Correct in the open. Do not make it disappear.

⚠ **No rebase, no squash, no amend, no force-push.** `e41ce85` is pushed; the misplacement is part of the record. **Both commits merge.** A reader sees the mistake and the correction, in that order.

The relocation commit **states what it is fixing in its own message**: that `e41ce85` appended the Run B pre-registration into `### D-071` instead of `### D-075`, by a slice terminator that matched the fifth `\n---\n\n### ` occurrence rather than the first.

⚠ **The standing rule is that corrections are recorded explicitly and never quietly patched.** A history where this never happened would be a cleaner record and a less true one.

## Constraint 2 — `### D-071` returns byte-identical, and it is hashed, not asserted.

```
git show e41ce85^:docs/README.md
```

Slice `### D-071`, hash it. Hash `### D-071` after the move. **Report both hashes and whether they match.**

⚠ **The claim under audit is that an unrelated sealed decision was disturbed and fully restored.** That claim gets a hash. A sentence saying it is fine is what the header count was.

## Constraint 3 — ⚠ Place it by unique-anchor text replacement. NOT by slice arithmetic.

**`4ad9b02` is the one method used today that did not fail**, and it succeeded because it anchored on text occurring once. **Every failure today came from matching a pattern that occurs more than once and taking the wrong occurrence.**

⚠ **Using an offset-based placement to fix an offset-based defect is the defect repairing itself.** If placing the block requires computing a character offset, **stop and report** rather than proceeding.

Anchor on text that is verifiably unique in the file. **Assert the anchor's uniqueness before using it** — `count == 1`, not `found`.

## Constraint 4 — The block appears exactly once, before and after.

Hash the 4,920 bytes. Assert **exactly one** occurrence in `docs/README.md` before the move, and **exactly one** after — same hash, different location. ⚠ **A move that leaves a copy behind is a duplication, and this project has catalogued that class more than any other.**

## Report

- `### D-071` hash before / after, and match ✅ or ❌
- amendment block hash before / after, and match ✅ or ❌
- occurrence count before / after — expected `1` and `1`
- the four `Ruling N —` greps, now **inside `### D-075`** — expected four HITs
- `### D-075`'s new span and char count — ⚠ **expected ≈ 22,794 + 4,862 ≈ 27,656.** Report the literal value; a difference is the finding
- the relocation commit's hash

**Then stop and report before Task 1.**

---

# TASK 1 — The terminator. D-074 binds, and the remedy depends on where it lives.

The regex `\n---\n\n### ` produced **both** of today's failures — Query 2's 46,281-char slice and this insertion point. ⚠ **D-074: a finding against an instrument is not closed until the instrument no longer exhibits it, or carries in itself a statement of what it gets wrong.**

**First, answer one question and report it, because it selects the remedy:**

## 1a — Is that regex in committed code, or in an ad-hoc session script?

**If COMMITTED** — fix it, and add a test that bites:

- ⚠ **The fixture must contain MULTIPLE `\n---\n\n### ` occurrences after the target entry**, so correct and incorrect return **different** offsets. **A single-entry fixture cannot discriminate and this task is not done** — A-017 clause (c).
- **(a)** assert the fixture reaches the code — a non-zero slice length, not merely "no exception"
- **(b)** one property, one test — *finds the first occurrence* and *does not overrun into the next entry* are two properties
- **Prove by revert:** restore the broken terminator, confirm red fires **at the assertion comparing the slice boundary**, and report the **file and line**. ⚠ An error-red and a failure-red are different objects.

**If AD-HOC** — it cannot be fixed, only retired. ⚠ **Then the remedy is not code.** Report that it is ad-hoc and **do not write a test for a script that will not exist tomorrow.** The lesson lands in the log instead, under Task 2's reservation.

⚠ **Either way, report which. The Planner will not assume.**

## 1b — The second defect, and keep it distinct

The check reported `appended INSIDE the D-075 entry: True` — **computed with the same broken terminator.** The verification and the defect shared an implementation, so they agreed.

⚠ **This is not the same finding as the terminator bug and must not be folded into it.** F-019's over-claim guard is exactly about not recruiting adjacent things into one count. **State it separately in your report; it lands separately in Task 2.**

---

# TASK 2 — Reserve `F-024`. Reserve, do not write.

⚠ **Reserving a number is not authorisation to do the work behind it.** It reserves the integer and records what would unblock it — which is the correct posture here, because **under D-074 this finding cannot be written until Task 1's disposition is known.**

Add to `docs/RESERVED.md`, in the established row form:

**`F-024`** — *A pattern that occurs more than once, matched without a uniqueness check, takes the wrong occurrence.* **Five dated instances, two agents, one day, one remedy:**

| Instance | Wrong occurrence taken |
|---|---|
| #123 header detection | the template **quoted inside** `RULING-2026-08-05-D-079-denominators-in-the-log.md` §3 |
| #129 header detection | the same file, the same way, again |
| Query 2's `15` | the fifth `\n---\n\n### `, four entries downstream — miscounted only |
| `e41ce85`'s insertion point | ⚠ **the same fifth occurrence — and this one WROTE** |
| The Planner's *"a different header by design"* | *"Short by design"* — the **adjacent** sentence, read as the intended one |

⚠ **Four of the five were false positives that looked like confirmations.** The remedy is identical across all of them: **assert the match is unique, or anchor on something that is** — which is why `4ad9b02`'s unique-anchor replacement landed correctly while everything else today did not.

**What unblocks it:** Task 1's disposition. ⚠ **Not closed until the instrument no longer exhibits it or carries a statement of what it gets wrong** (D-074).

**Also record, as a SEPARATE line in the same row and explicitly not counted as a sixth instance:** *a verification that shares an implementation with the thing it verifies will agree with it.* ⚠ **This is F-022's next level** — F-022 was two readers deriving from one artifact; this is a check importing the code under test. **Different remedy: F-022's was write the expectation down; this one's is the check must not share code with the code under test.** It stays unnumbered pending the owner's ruling on findings numbering.

**Then run the checker verbatim.** Read the output, not the exit code. Expected `UNRESOLVED AND UNRESERVED: none — invariant holds`, reserved set **14 → 15**.

---

## REPORT BACK

Plain lines, `label | value`. **No box-drawing tables** — seven consecutive reports have lost their middle columns.

**Task 0:** four hash comparisons · occurrence counts · four `Ruling N —` greps inside `### D-075` · D-075's new char count · relocation commit hash
**Task 1:** committed or ad-hoc · if committed, the test and the **file and line its revert redded at** · the 1b defect stated separately
**Task 2:** the checker's literal output · reserved set size

---

## THEN

⚠ **Resume `ORDERS-Code-2026-08-06-verify-merge-tranche.md` at its Task 0b.** Do not re-run its Task 0a.

**Sequence from there, unchanged:** 0b (the additive diff) → 0c (the four PRs' readiness) → **Task 1, the merges, in dependency order, each on its own merits** → **Task 2, migration `0008` and the tranche column.**

⚠ **After the relocation lands, the merges are unblocked** — the stack will carry the misplacement **and its correction**, which is the record this project keeps rather than the tidier one.

**Then the crank.**

— END OF RELOCATION ORDERS (3 of 3) —
