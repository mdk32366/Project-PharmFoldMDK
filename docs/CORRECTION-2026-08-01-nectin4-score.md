# Correction — 2026-08-01 — A superseded score and its narrative were spoken to the grader; both are corrected against F-004

**How known (D-016):** the Razzak meeting summary (AI-notetaker transcript, 2026-07-30 demo) reports NECTIN4 as *"scored 20.2655 and ranked 8 out of 56 ... top 20% percentile."* Read against the committed result `F-004-result-and-D-062-amended-orders.md` (`ranking_run` id=2, `scorer_version=91e646e4a289`) and the curated label file `data/adc_reference_mapping.csv` (12 in-cohort positives, NECTIN4 = Q96NY8, verified this session).

**Part 1 — the number was a fusion of three real figures into one wrong one.** The committed F-004 value is **NECTIN4 at LOO percentile 0.848, ranked 4th of the 12 labelled positives** (behind EGFR 0.955, CDCP1 0.902, ERBB2 0.866). The spoken *"rank 8 of 56"* collapsed three distinct quantities:

- **8** is the head-to-head denominator (held-out positives carrying an evidence score, F-002), not NECTIN4's rank;
- **56** is the full ranking set (`target_scores`), a different reference frame from the 12-positive LOO fold the percentile is computed in;
- **20.2655** appears nowhere in F-004 and does not transform to 0.848 — it is a **stale artifact of a pre-F-004 exploratory scoring pass** the committed fit superseded.

No integrity failure: the number came from a model that had been *replaced*, not one that didn't exist. It is a memory-drift error, recorded here rather than quietly forgotten (correction discipline: never a silent fix).

**Part 2 — the narrative was the pre-F-004 one, which F-004 explicitly forbids.** In the room, NECTIN4 was framed as validation: top-percentile, effective, minimal side effects. F-004 caveat (c) bars exactly this — NECTIN4 sitting in the top four is *"consistent with signal and equally consistent with"* the pLDDT-attention confound (caveat b), and *"is not narrated as validation."* The committed headline is the opposite of a per-target win: the structural axis is **orthogonal to the comparator but cannot be shown to add anything at n=12** — a pre-registered null that fired.

**Standing consequence.** The number is a one-time slip with no downstream artifact (nothing on a deployed surface carries 20.2655; every rendered figure derives from `/api/ranking`). The **frame**, however, is a live risk for the deck and the researcher introductions Razzak offered. The correct claim to carry forward is *"we pre-registered two negative outcomes; one fired, one didn't; orthogonal-but-unproven is a cleaner result than either alone"* — not *"the model liked the famous target."* Any deck or write-up leading with NECTIN4-ranks-high reintroduces the confound F-004 was built to hold.

**Trap flagged for the miniature notebook (07-30 orders, Step 5):** NECTIN4's **0.848 is LOO-within-12**; a placement against the **56-row** `target_scores` is a *different* number. Print both with denominators labelled, never a bare rank — the exact error corrected here.
