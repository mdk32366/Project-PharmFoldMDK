# DRAFT — `D-093 amendment ‹N›` — the pooling surface contract

**AUTHORED-SHA256** (range: **first `####` header → EOF**, anchored to line starts, **SECOND
occurrence of the marker**) = `f9da826fe17cf8713be070f100eca233e4e8ec67fffe62d1aa1dc8596c6cca59`
**bytes** = `6396`

> ⚠⚠ **A DRAFT, GATED. It is not landable until `XE`'s sourced column and `XF1`'s rows report** —
> **the row marker cannot name what a category pools until the crosswalk says so, per row, with a
> citation.** **Three placeholders below are marked `‹from XE›` / `‹from XF1›`.**
>
> ⚠ **DOWNLOAD AND COMMIT WHEN GATED-OPEN. DO NOT RETYPE.** Landing header above the marker, outside
> the range. Sub-entry — **no integer.** Three greps.

---

#### D-093 amendment ‹N› — ⚠⚠ HPA's tumour categories pool populations oncology treats as distinct diseases, and for several targets the defining biomarker IS the target

- **Date:** 2026-08-21 · **Status:** ⚠ **DRAFT, gated on `XE` and `XF1`.**
- **Owner ruling (2026-08-21):** *"It does not affect the score, but it impacts the understanding of
  the tumour, the treatment possibilities… This needs to be on a general surface, and then in the
  specific surface raise the fact that these nuances exist and explain it."*

---

**1 — ⚠⚠ THE FINDING, AND ITS SHARP END IS NOT THE POOLING.**

**HPA's `Cancer` column carries twenty free-text names and no codes.** ⚠ **`‹from XE›` of the twenty
pool populations that oncology treats as clinically distinct** — different eligibility, different
therapy, different survival. **`breast cancer` pools HER2+, HER2−, ER/PR and triple-negative;
`head and neck` pools HPV+ and HPV−; `glioma` pools IDH-mutant and wild-type**, ⚠ *and WHO
reclassified glioma on molecular grounds in 2021.*

⚠⚠ **BUT THE SHARP END IS THIS: THE BIOMARKER THAT SUBDIVIDES THE DISEASE IS OFTEN THE ADC TARGET
ITSELF.** **`NECTIN4` defines the enfortumab-vedotin population. `CLDN18.2` defines zolbetuximab's.
`FRα` defines mirvetuximab's. `CD30` defines brentuximab's. `HER2` defines trastuzumab's.**

⚠⚠ **So *which cancer* and *which target* are NOT INDEPENDENT AXES. For a target that DEFINES a
subtype, the tumour category pools exactly the split that target creates** — **and the panel dilutes
the signal for precisely the targets that work best.** **`‹from XF1›` cohort targets are in that
state.**

⚠ **This is worse than the SEER crosswalk problem in one respect: that was a JOIN failure, visible as
a failure. This is a GRANULARITY failure inside categories that join CLEANLY** — ⚠⚠ **`breast cancer`
maps to SEER `Breast` without complaint, and both sides pool the same three diseases.** ***`mapped`
means the names agree. It does not mean fit for purpose.***

**2 — ⚠⚠ IT DOES NOT AFFECT THE SCORE, AND THAT IS ENFORCED RATHER THAN ASSERTED.**

**`EE-0` widened `test_the_scorers_feature_path_is_closed` from one field to EVERY clinical-layer
field — expression counts, levels, `qh`, evidence types, reliability — proven RED four ways,
INCLUDING the rename route** (`mean_plddt_ecd → mean_expression_ecd` reddens).

⚠ **So *the pooling cannot reach the score* is a structural guarantee, not a judgement.** ⚠⚠ **That is
what permits the marker to sit beside the tumour panel: there is no false adjacency to create,
because the adjacency is closed by test.** *`D-102` amendment ‹N› records what a false adjacency
costs — two true statements side by side producing an untrue impression.*

**3 — RULING: THE ROW MARKER, AND IT MUST EXPLAIN ITSELF.**

⚠⚠ **The caveat is a property of a (protein × tumour type) PAIR, not of the protein. It renders ON THE
ROW.** **Never a card banner** — ⚠ *nearly all twenty pool something, so a card-level warning fires
almost always, and a warning that fires on everything is read as boilerplate within a week.* **The
burden section proved that at ~150 words × 2,690 cards.**

⚠⚠ **THE MARKER IS SELF-SUFFICIENT FOR *WHAT* IS POOLED. A flag that requires a click to mean
anything is not a disclosure.**

- ⚠ **NOT** `⚠ pooled`
- ⚠⚠ **YES** — `Breast cancer · 11/11 · ⚠ pooled — HER2+/−, ER/PR, TNBC not distinguished`

**A reader who never clicks understands the number in front of them.** ⚠ **The link carries *why it
matters*, not *what it is*.**

**4 — ⚠⚠ THE SUBTYPE-DEFINING ROWS GET THE SHARPER LINE, AND IT DOUBLES AS THE PRECEDENT LABEL.**

> `Urothelial · 8/12 · ⚠ NECTIN4 defines the enfortumab-vedotin population; this panel does not
> separate it`

⚠ **One sentence saying both what is pooled AND that a therapy exists for exactly that population.**
**`D-093` amendment 2 ruling 3 permits `therapeutic_precedent` as a LABEL and bars it as a FEATURE —
and the feature path is closed by test, so this is what that ruling allows.**

⚠⚠ **AND IT INHERITS RULING 3'S CONDITION: the circularity warning renders in the same frame.**
**But note the claim is DIFFERENT here and must read as different:** *"has been developed as an ADC
target"* is **not evidence the target is good** — ⚠ **on this row it is evidence about the
POPULATION**, i.e. that the pooled category contains a clinically actioned subset. **A reader must not
take it as a recommendation.**

**5 — Where the general argument lives, and it is two surfaces.**

- ⚠ **The CROSSWALK PAGE** carries the fifth column — *what this category pools*, per row, with its
  source — **and the paragraph on why it matters for ADC target selection.**
- ⚠⚠ **The METHOD PAGE carries it as a STATED LIMITATION OF THE APPROACH**, because that is where a
  reviewer looks: ***tumour categories in this atlas pool populations that oncology treats as
  distinct diseases, and for several targets the defining biomarker IS the target.***
  **That sentence is the one that goes in the paper.**

**6 — ⚠ What this does NOT do.**
- ⚠⚠ **It does not subdivide any HPA category.** **HPA has no codes and cannot be subdivided; this
  ruling MEASURES the pooling and does not attempt to undo it.**
- ⚠⚠ **It does not adjust any figure.** **Anything resembling a corrected number would be invented.**
  ***The honest move is to say what the number is OF, not to change it.***
- ⚠ **It does not touch the scorer, `FEATURE_NAMES`, or any ranking.**
- ⚠ **It does not claim the pooled figures are wrong** — **they are correct counts of a population
  that is broader than a reader may assume.**

**7 — ⚠⚠ GATE, and it is not decorative.**
**`XE`'s column must be SOURCED PER ROW before any marker renders** — ⚠ **the Planner's subtype list
is general clinical knowledge from a NON-CLINICIAN and is a starting point, not authority.**
⚠⚠ **A clinical claim on a public surface with no citation is precisely what `P-004` argues against
in someone else's work.** **No source, no marker: `unknown_to_code` renders nothing.**

**Assumptions relied on:** ⚠ `A-014` — **HPA's tumour type assignment is a curated classification, not
a fact about the sample**, and this ruling is about what that classification contains.
