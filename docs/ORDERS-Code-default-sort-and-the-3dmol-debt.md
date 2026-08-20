# ORDERS — Code — the default sort is a de facto ranking by a third of the real one; and a walk ordered five days ago has never reported

**AUTHORED-SHA256** (range: **first `## §` header → EOF**, anchored to line starts, **SECOND
occurrence of the marker**) = `3924d9ea3ec07c71b577ddd7adf8eb1dafd96cc31652fc71c3db008668b775f3`
**bytes** = `4928`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE.** Landing header **above** the marker, outside the range.
> ⚠ Grounding: `main @ d3591d3` plus your report on PR #178. **No GPU, no rental, no fold, no fit,
> no ingest. Tranche 5 HELD** — `D-091` r2.

---

## §0 — Owner ruling (2026-08-21), and the reasoning is the ruling

**`/targets` defaults to sorting by pLDDT. `CensusTable.jsx` explicitly refuses that on the census as
*"turning self-reported confidence into a de facto ranking."*** ⚠ **Same reasoning, opposite
behaviour, two surfaces — and you flagged it rather than quietly matching them.**

**RULED: default to the SCORER RANK where one exists. pLDDT becomes an explicit sort the reader
chooses.**

⚠⚠ **The reason, and it must travel with the change: the cohort IS ranked — by the scorer, not by
pLDDT — and `F-051` measures `membrane_proximal_plddt` at 32.2% of attribution.** **So a pLDDT default
sort is a de facto ranking BY A THIRD OF THE REAL RANKING, presented as though it were the ranking.**
⚠ **Arguably worse than on the census, where nothing else is competing to be the order.**

⚠ **`D-102` covers what remains permitted: a reader CHOOSING a lens is neither judgement nor
measurement. The system choosing it and calling it the order is.**

---

## §1 — Task TA — the default sort

**TA1 — Default `/targets` to the scorer rank** from the pre-registered run, ⚠ **`valid ∧
run_kind='preregistered'`** — **and `F-049` applies: `run_kind` alone does not identify it, because
`id=1` carries the same value with zero scored rows.**

**TA2 — ⚠⚠ WHAT ABOUT THE ROWS WITH NO RANK?** **56 of 82 are scored.** **The unscored — `below_floor`,
`held_out`, `not_folded`, `unranked_unexplained` — have no position in a scorer ordering.**
⚠ **They are NOT sorted to the bottom as though ranked last.** **Report how you intend to place them
BEFORE building it** — *a sort that sinks unranked rows is a ranking of scoreability*, and it is the
same defect in a new coat.

**TA3 — pLDDT remains available as an explicit sort**, ⚠ **and when chosen it carries the same
sentence `CensusTable.jsx` uses.** **The lens is stated where the lens is applied** — `D-102`.

**TA4 — ⚠ Prove it red**: assert the default ordering is the scorer's, and watch it fail when the
default is set back to pLDDT. **One property, one test.**

## §2 — ⚠ Task TB — the entries this needs

**TB1 — Draft `D-102 amendment ‹N›`** — ⚠ **Code drafts, the Planner rules, as with the `D-075`
proposal.** It carries: the two surfaces disagreeing · the owner's ruling · ⚠⚠ **the 32.2% figure,
which is what makes it a ruling rather than a preference** · and `TA2`'s placement of the unranked.

**TB2 — `F-052` gains another instance and it is user-visible.** ⚠⚠ **The alias index reached the
census only, so HER2 found nothing while ERBB2 sat in the list folded and ranked.** **Report it for
the Planner to write; ⚠ the durable half is that `searchRows.js` is now SHARED rather than copied —
*the enumeration was a snapshot; shared code is what survives the session.***

**TB3 — ⚠ Report `D-034 amendment 1` and the `App.test.jsx` repoint as landed**, with the
distinction you drew: **the test asserted the enumeration, the decision asserted a principle, and the
test was the thing that was wrong.** ⚠⚠ **A test pinning defective copy DEFENDS it.**

## §3 — ⚠⚠ Task TC — the 3Dmol viewer walk, ordered 2026-08-19, NEVER REPORTED

**`ORDERS-Code-2026-08-19f-ADDENDUM-viewer-defect.md`, tasks `BF1`–`BF4`.** ⚠ **Five days. No report,
no refusal, no *cannot do this*.** **It is item 12 on `PREWORK-2026-08-20`'s holder table and the
reason that table has a holder column at all.**

**TC1 — ⚠ State plainly whether it ran.** **If it did not, say so — that is a category with a cause
and it is not a criticism.** **If it ran and the report was lost in a truncated message, re-send it.**

**TC2 — If it did not run, run `BF1` only**: ⚠ `curl -sI` the chunk, **report status AND
content-type**, since the status alone cannot separate the first two rows of that table.
⚠⚠ **Do not fix anything. Three causes, three remedies, and applying the wrong one destroys the
evidence that identifies it.**

**TC3 — ⚠ And report whether the defect is still live at v95.** **Five days of deploys may have moved
it in either direction, and *"it was broken on 08-19"* is not a statement about today.**

## §4 — ⚠ Not ordered

**No rental, no climb, no `preflight` wiring.** **No census scoring, no profile computation.**
**No fix to the `/api/census/1970` 500** — ⚠ that is its own order once the traceback exists.
⚠⚠ **If `TA2` cannot be answered without a ruling, STOP AND REPORT.** **Placement of the unranked is
a decision, not a default.**

## §5 — Report

⚠ **`TC1` first — one sentence, and it clears five days of silence either way.**
Then `TA2`'s intended placement **before** you build it · `TA4`'s red · `TB1`'s draft · branch and tip
· **number and title of any entry landed in the message that lands it** · both invariants with their
keys · the gate without `.env`.
