# ORDERS — Code — is it the same antibody, and does a `mapped` category pool clinically distinct diseases?

**AUTHORED-SHA256** (range: **first `## §` header → EOF**, anchored to line starts, **SECOND
occurrence of the marker**) = `2ad63aa07a21b3a52071d6d73a6146dd9878a812719f8eb8e068ce03271f64a7`
**bytes** = `5646`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE.** Landing header **above** the marker, outside the range.
> ⚠⚠ **ADDITIVE to `ORDERS-Code-WE1-skin-confirmation-and-SEER-decision-6.md` (`5c625686…`), which
> STANDS.** **This adds `XD`, `XE` and `XF`. Everything there is unchanged.**
> ⚠⚠ **Documentation and one `SELECT`. No ingest, no fetch, no table, no page.**

---

## §0 — Why these three, and the third arrived last

**The owner asked whether relative abundance — tumour versus healthy — is derivable.** ⚠ **`D-093`
amendment 2 ruling 4 already says no: `normal_tissue.tsv` carries NO PATIENT COUNTS, so the ratio is
pre-registered as not computable from this supplier.**

**What may be derivable is an ORDINAL CONTRAST** — modal tumour level against normal level in the
matched tissue. ⚠ **Not a ratio. A comparison, stated as ordinal.** **Four things stand between us and
it, three already ruled** (`Level` is not a clean ordinal, ruling 7 · the reliability asymmetry,
ruling 8 · no cancer→normal-tissue crosswalk exists) — ⚠⚠ **and one nobody has asked, which is `XD`.**

---

## §1 — ⚠⚠ Task XD — SAME ANTIBODY? This is the ceiling on the whole line

**`P-004`'s standing observation, measured: 52.5% of HPA genes carry MORE THAN ONE antibody
(9,140 / 17,407).**

⚠⚠ **If a gene's TUMOUR staining and its NORMAL-TISSUE staining come from DIFFERENT antibodies, an
ordinal contrast compares TWO ASSAYS, not one protein across two tissues.** **Every downstream
statement inherits it.**

**XD1 — Read HPA's documentation: for a given gene, is `pathology.tsv` staining and
`normal_tissue.tsv` staining produced by the same antibody?** ⚠ **Quote it, URL and date read.**
**XD2 — ⚠ Do the FILES carry an antibody identifier at all?** **Report the column list of both,
verbatim.** ⚠⚠ **If neither file names an antibody, then the answer is unknowable from what we hold,
and THAT is the finding** — *not a caveat on a contrast we then compute anyway.*
**XD3 — ⚠ If HPA does not document it, say so. `hpa_antibody_provenance_undocumented`.** **Do not
infer it from consistency of the values** — *two antibodies agreeing is not one antibody.*

⚠⚠ **XD IS A DECISION 6 QUESTION (1) ITEM — *what the supplier actually serves* — and it belongs in
`CC`'s answers for HPA, which are currently four of five.**

## §2 — ⚠⚠ Task XE — a fifth crosswalk column: does the joined category POOL distinct diseases?

**`mapped` means THE NAMES AGREE. It does not mean FIT FOR PURPOSE.** ⚠ **Thirteen green rows will be
read as thirteen usable ones unless the crosswalk says otherwise.**

**XE1 — Add a column `pools_clinically_distinct_subtypes`, per row**, with the subdivision named.
⚠ **Report at three values: `yes` · `no` · `unknown_to_code` — the last is legitimate and preferred
over a guess.**

⚠⚠ **The Planner's list, offered as a STARTING POINT and explicitly NOT as authority — it is general
clinical knowledge from a non-clinician and MUST be checked against a citable source before it enters
any entry:**
**breast** (HER2+/−, ER/PR, triple-negative) · **lung** (EGFR, ALK, ROS1, KRAS G12C, PD-L1) ·
**colorectal** (KRAS/NRAS/BRAF, MSI-H vs MSS) · **stomach** (HER2, CLDN18.2, PD-L1) ·
**melanoma** (BRAF V600) · **prostate** (castration-sensitive/resistant, PSMA) ·
**ovarian** (BRCA/HRD, FRα) · **urothelial** (NECTIN4, FGFR3) · ⚠ **head and neck (HPV+/−)** ·
**endometrial** (four molecular classes) · ⚠ **glioma (IDH-mutant vs wild-type — WHO reclassified on
molecular grounds in 2021)** · **lymphoma** (CD20, CD30, CD79b).

**XE2 — ⚠ Cite a source per row.** ⚠⚠ **A clinical claim in this log with no citation is exactly what
`P-004` argues against in someone else's work.**

## §3 — ⚠⚠ Task XF — the one that reaches OUR OWN SCORING, not just burden

**Look at the subdividing biomarkers: HER2 · CLDN18.2 · PSMA · FRα · NECTIN4 · CD30 · CD79b · TROP2.**

⚠⚠ **THE BIOMARKER THAT SUBDIVIDES THE DISEASE IS OFTEN THE ADC TARGET ITSELF.** **NECTIN4 defines the
enfortumab-vedotin population; CLDN18.2 defines zolbetuximab's; FRα defines mirvetuximab's.**

⚠⚠ **So for a target that DEFINES a subtype, the tumour category pools exactly the split that target
creates.** **Score `ERBB2` against HPA's `breast cancer` and the denominator is ALL breast cancer,
while the population that matters is the 15–20% that is HER2+.** ⚠ **The panel dilutes the signal for
precisely the targets that work best.**

**XF1 — Of the 82 cohort targets, how many are the DEFINING biomarker of a subtype of a tumour type
present in HPA's twenty?** ⚠ **Report the rows.** **`data/adc_reference_mapping.csv` is 13 rows and
already in the tree — start there and say what it does not cover.**
**XF2 — ⚠⚠ For those, report their HPA staining in the pooled category alongside the published
prevalence of the subtype.** **Measure the dilution; do not estimate it.**
**XF3 — ⚠ State plainly whether this affects the SCORER.** **`F-051`, `F-005` and the cohort ranking
use structural features, not expression** — ⚠⚠ **so the honest answer may be *it affects the clinical
layer and not the score*, and if so SAY THAT.** **A finding that turns out to be narrower than feared
is reported at the same weight as one that widens.**

## §4 — ⚠ Not ordered

**No ratio computed. No contrast computed. No ingest, no fetch, no schema, no page.** ⚠⚠ **No
subdivision of any HPA category — HPA has no codes and cannot be subdivided; this order MEASURES the
pooling, it does not attempt to undo it.**
⚠ **If `XD` shows the antibody is undocumented, STOP on the contrast line and report** — *the ceiling
is the finding.*

## §5 — Report

⚠ **`XD1`/`XD2` first — they cap everything downstream.** Then `XE`'s column with sources ·
`XF1`'s rows · ⚠ **`XF3`'s plain answer either way** · branch and tip · both invariants with their
keys · the gate without `.env`.
