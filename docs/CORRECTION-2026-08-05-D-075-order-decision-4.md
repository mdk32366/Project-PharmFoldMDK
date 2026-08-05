# CORRECTION — 2026-08-05 — `ORDERS-Code-2026-08-05-D-075-run.md` §4 reproduced the sealed interpretation, lossily

> **COMMITTED 2026-08-05 with `### D-079` (`docs/README.md`). CITED BY the log, not restated in it —
> where this file and the log differ, THE LOG GOVERNS.** ⚠ This file is provenance for a decision that
> lives in the log; it is not itself authority. Check the `### D-079` header, not a reference to it.

> **Apply this before executing #2.** It deletes content; it adds none. **Do not re-issue the order** —
> a second full copy is more delivery surface, and delivery has failed in both directions once already.
>
> **Caught by:** Code, checkpoint 1, 2026-08-05, while confirming §0.1 against `docs/README.md`.
> **Planner error. Twelfth premise correction; several have been in Planner-authored orders.**

---

## What was wrong

`ORDERS-Code-2026-08-05-D-075-run.md` §4 reproduced Decision 4 as a **five-row table**. The sealed
entry at `docs/README.md` §D-075 Decision (4) has **six rows**. Verified by the Planner against the
log on 2026-08-05.

**Two specific defects, and the second is worse than the first:**

1. **The `≈ chance` language was reintroduced.** The order's second row read
   *"`geom_proxy` ≈ `no_plddt` ≈ chance."* The log's corresponding row ends, in bold:
   ⚠ *"Note this is **not** '≈ chance' — the baseline itself is above 0.5 on median and mean."*
   D-041 decision 4 had already replaced every `≈ chance` cell in this entry. **The order put one back.**

2. **⚠ The row most likely to fire was missing entirely.** The log's third row —
   *"the three statistics disagree (e.g. median toward FULL, count at baseline)"* → **reported as a
   split, not resolved to one number** — was absent from the order. The log states that Decision 0.1–0.3
   make this **the *expected* case at n=12**: one target's rank moves the count, and ten of the finest
   increments span the whole median gap.

   **So the order's table omitted the expected outcome and offered two clean alternatives instead.**
   A reader working from it would have been pushed to force a split result into one of the two tidy
   rows. That is not a formatting loss; it is the pre-registration's central protection, removed.

**Also lost:** the three-against-three comparison is anchored on explicit numbers in the log —
`geom_proxy` toward FULL (**0.6071 / 0.6176 / 8-of-12**) versus at the `no_plddt` baseline
(**0.5625 / 0.5893 / 6-of-12**). The order carried none of them.

## How it happened, because the mechanism matters more than the instance

**The table was sourced from `ORDERS-Code-2026-08-01-D-075-ablation.md`, a staged order document —
not from `docs/README.md`.** The 08-01 order says so itself: *"two amendments were ruled on the same
date and are reflected in the landed entry, not here… where this order and `docs/README.md` differ,
the log governs."*

**The Planner read that sentence and then copied the table anyway.** This is the pointer-not-proof
shape — method-note item 7, *check the thing, not the reference to it* — committed inside a document
whose own §0.1 instructs Code to do the opposite. ⚠ **A sealed interpretation had two copies four days
apart, and they had already drifted.** That is the two-paths-to-one-quantity class applied to the
project's most load-bearing text.

---

## The correction — DELETE, do not fix

⚠ **Correcting the table would recreate the defect in corrected form.** A second copy of a sealed
interpretation is free to drift again, and this one demonstrably did within four days.

**Delete §4's outcome table in its entirety.** Replace the whole of §4 with:

---

> ## §4 — ⚠ Read the result against the sealed interpretation **in the log**, and against nothing else
>
> **Open `docs/README.md` §D-075 Decision (4). Read the rows there. Quote the row that fired from the
> log. Do not write prose first.**
>
> **⚠ This order reproduces none of those rows, deliberately.** An earlier draft did, and it dropped
> one row and softened another — see `CORRECTION-2026-08-05-D-075-order-decision-4.md`. **There is one
> copy of the frozen interpretation and it is in the log.**
>
> Three things about reading it, each with a specific prior failure behind it:
>
> 1. **Judge on the explicit triple — median, mean, and count ≥0.5 — never on one statistic**
>    (D-041 dec 4). The log anchors the comparison three-against-three with numbers; use the log's.
> 2. **⚠ The `no_plddt` baseline is not chance.** Any reading that treats it as chance is wrong before
>    it starts.
> 3. **A disagreement among the three statistics is a legitimate, reportable outcome** — the log
>    states it is the *expected* one at n=12. **It is not a failed run and it is not to be resolved to
>    one number.**
>
> **`≈` is deliberately not thresholded.** No tolerance invented after seeing the diff.

---

## Standing consequence

**No Planner order may reproduce a sealed pre-registered interpretation.** It cites the log's section
and instructs the reader to open it. This applies to D-075 Decision 4, D-077's outcome table, D-079's
decision 4 frozen readings, and any future frozen reading.

⚠ **Where an order and the log differ, the log governs — and the way to guarantee that is for the
order to contain nothing that could differ.**

Recommend this enters the close-out's Planner-error table and is proposed to the assumption register
as its own row when KEEL-4 lands against v6.
