# DRAFT — `D-093 amendment ‹N›` — the pooling surface contract — REWRITE, sourced

**AUTHORED-SHA256** (range: **first `####` header → EOF**, anchored to line starts, **SECOND
occurrence of the marker**) = `d1466e00696a47f114e24de572984861d25b94f6ef65b24ca728011036effed1`
**bytes** = `7611`

> ⚠⚠ **SUPERSEDES the 2026-08-21 draft (`f9da826f…`, 6,396 B). DO NOT LAND THAT ONE.** **Its §1
> asserted that `breast cancer` pools HER2+/HER2−; the only source opened says HPA's category pools
> DUCTAL and LOBULAR — morphology, not receptor status.** ⚠ **The Planner's claim was uncited, and
> head-and-neck HPV± and glioma IDH-mutant were uncited entirely.** **`XE`'s gate stopped it. The
> gate did its job and the thing it stopped was mine.**
>
> ⚠⚠ **OWNER-RULED 2026-08-21: LANDS AT THREE ROWS.** **The seventeen render nothing.** ⚠ **This
> revision also carries the SETTLED KEY (§1), which the previous version got wrong in both
> directions.**
>
> ⚠ **DOWNLOAD AND COMMIT WHEN RULED. DO NOT RETYPE.** Sub-entry — **no integer.** Three greps.

---

#### D-093 amendment ‹N› — ⚠⚠ HPA's tumour categories pool populations that are clinically distinct, the count is unsourced, and the marker renders only where a citation exists

- **Date:** 2026-08-21 · **Status:** ⚠ **RULED — lands at three rows** (owner, 2026-08-21). §4's
  marker contract awaits confirmation only.
- **Owner ruling (2026-08-21):** *"It does not affect the score, but it impacts the understanding of
  the tumour, the treatment possibilities… on a general surface, and then in the specific surface
  raise the fact that these nuances exist and explain it."*

---

**1 — ⚠⚠ WHAT IS ESTABLISHED, AND IT IS THREE ROWS, NOT TWENTY.**

**HPA's `Cancer` column carries twenty free-text names and no codes.**

⚠⚠ **THE SETTLED KEY, and it took a correction OF a correction to reach:**
**`hpa_composition_undocumented` = 20 of 20.** ***Separately***, **3 rows carry a PARTIAL SUBTYPE
STATEMENT sufficient to source a pooling claim.** ⚠ **TWO FACTS, ONE TOKEN EACH** — *they do not
compete and they are not two counts of one thing.*

⚠ **HPA says breast *"includes both ductal and lobular."* It never says that is the COMPLETE
contents, nor in what proportion.** ⚠⚠ ***A partial subtype statement sources a pooling claim without
documenting a composition.***

⚠⚠ **How this was reached, because the path is the finding.** **Code's crosswalk said all twenty
undocumented. Code then corrected it to *"HPA documents three of the twenty."* ⚠ THAT CORRECTION
OVER-CORRECTED — the original line was closer to right than the correction that replaced it.**
**Both corrections stand, in order, with pointers between them.** ⚠ **And the Planner, shown the
contradiction, proposed a SECOND CODE (`hpa_subtypes_partially_named`) to reconcile a contradiction
that was not one** — **inventing a category rather than reading what HPA actually said.**

⚠⚠ **The Planner asserted `breast cancer` pools HER2+/HER2−. The source says DUCTAL and LOBULAR.**
**Both are real subdivisions; they are not the same subdivision, and one was invented by analogy.**
⚠ **What is established: HPA's categories pool SOMETHING in at least three cases, sourced. Whether it
extends to twenty is UNMEASURED and this entry does not claim it.**

⚠ **Row 8 survives the reconciliation intact:** **HPA names cholangiocellular carcinoma for liver,
which is the bile duct SEER's category also carries.**

**⚠⚠ THE GENERAL CLAIM THAT DOES SURVIVE, because it needs no per-row source:** **HPA assigns a
free-text tumour NAME and documents no category's contents** (`hpa_composition_undocumented`, 20 of
20). ***A reader cannot know what population a figure describes.*** **That is a property of the
supplier, measured, and it is enough to justify the marker.**

**2 — ⚠⚠ THE SHARP END, AND IT IS SMALLER THAN THE PLANNER FRAMED IT.**

**For a target that DEFINES a subtype, the tumour category pools exactly the split that target
creates.** ⚠ **`XF1`: at most FOUR of 82 are plausibly subtype-defining — `ERBB2`, `NECTIN4`, `EGFR`,
`FGFR3`.**

⚠⚠ **AND GROUP C IS EMPTY: `TROP2`, `CLDN18.2`, `FRα`, `PSMA`, `CD79b` ARE NOT IN THE COHORT AT ALL** —
**half the biomarkers the Planner named.** **So the effect is real, narrow, and its absence is itself
a fact about what the cohort is a sample of** (`F-009`).

**3 — ⚠⚠ IT DOES NOT AFFECT THE SCORE — ENFORCED, NOT ASSERTED — AND IT DOES REACH THE COMPARATOR.**

**`core/scorer.py` imports nothing clinical; the six pre-registered features are structural and
confidence.** **`EE-0` widened `test_the_scorers_feature_path_is_closed` to EVERY clinical-layer
field, proven RED four ways INCLUDING the rename route.** ⚠ **So the pooling cannot reach the score.
A structural guarantee.**

⚠⚠ **BUT IT REACHES THE COMPARATOR, AND THAT IS BIGGER THAN WHAT THIS ENTRY WAS OPENED FOR.**
***`P-001`'s headline is that the structural ranking is "not distinguishable from ranking by
expression and prior evidence" — and that arm is POOLED.*** ⚠ **The score being clean does not make
the comparison clean.** **Recorded here; ⚠⚠ it is a `PAPERS-v2` matter and the owner rules it, not
this entry.**

**4 — RULING: the row marker, self-sufficient, and ONLY where sourced.**

⚠ **The caveat is a property of a (protein × tumour type) PAIR. It renders ON THE ROW, never as a
card banner** — *a warning that fires on everything is boilerplate within a week, and the burden
section proved that at ~150 words × 2,690 cards.*

⚠⚠ **A FLAG THAT REQUIRES A CLICK TO MEAN ANYTHING IS NOT A DISCLOSURE.**

- ⚠ **NOT** `⚠ pooled`
- **YES, where sourced** — `Breast cancer · 11/11 · ⚠ pooled — INCLUDES ductal and lobular`
  ⚠⚠ ***INCLUDES, never COMPRISES.*** **One word, and it is the whole difference between a sourced
  claim and an inferred one** — **HPA names two members and does not claim the set is complete.**
- ⚠⚠ **Where NOT sourced — 17 of 20 today — the marker RENDERS NOTHING.** **`unknown_to_code` is
  silence, not a hedge.** *A marker saying "this may pool something" on seventeen rows is the
  boilerplate this ruling exists to avoid.*

**5 — ⚠ The subtype-defining rows, and the claim is about the POPULATION.**

> `Urothelial · 8/12 · ⚠ NECTIN4 defines the enfortumab-vedotin population; this panel does not
> separate it`

**One sentence: what is pooled, and that a therapy exists for exactly that population.** ⚠ **`D-093`
amendment 2 ruling 3 permits `therapeutic_precedent` as a LABEL and bars it as a FEATURE; the feature
path is closed by test.**
⚠⚠ **Ruling 3's circularity condition is INHERITED AND ALTERED: on this row the claim is about the
POPULATION, not the target.** ***"Has been developed as an ADC target" is not evidence the target is
good*** — **here it is evidence the pooled category contains a clinically actioned subset, and it must
read as that.**
⚠ **These four rows need the same citation gate as everything else.**

**6 — Where the general argument lives.**
- ⚠ **The CROSSWALK PAGE** — the pooling column with its source per row, ⚠⚠ **and the seventeen
  `unknown_to_code` rows shown AS SUCH**, because *what we have not sourced is as much the state of
  play as what we have.*
- ⚠⚠ **The METHOD PAGE**, as a stated limitation, in the form that survives citation:
  ***HPA documents no tumour category's contents, so a reader cannot know what population a staining
  figure describes; where we have been able to source it, the category pools clinically distinct
  populations.***

**7 — ⚠ What this does NOT do.**
- ⚠⚠ **It does not claim twenty categories pool. It claims three do and seventeen are unknown.**
- **It does not subdivide any HPA category** — **HPA has no codes.**
- ⚠⚠ **It does not adjust any figure.** ***The honest move is to say what the number is OF, not to
  change it.***
- **It does not touch the scorer, `FEATURE_NAMES` or any ranking.**
- ⚠ **It does not rule on `P-001`'s comparator arm** — §3, owner's.

**8 — ⚠⚠ THE GATE, RESTATED, BECAUSE IT ALREADY CAUGHT THE PLANNER ONCE.**
**No source, no marker.** ⚠ **The Planner's subtype list was general clinical knowledge from a
NON-CLINICIAN, one item of it was wrong, and it was offered as a starting point and treated as a
finding.** ⚠⚠ **A clinical claim on a public surface with no citation is precisely what `P-004`
argues against in someone else's work.**

**Assumptions relied on:** ⚠ `A-014` — **HPA's tumour type assignment is a curated classification, not
a fact about the sample.**
