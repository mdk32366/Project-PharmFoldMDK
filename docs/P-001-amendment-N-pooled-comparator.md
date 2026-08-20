# PASTE-READY — `P-001 amendment ‹N›` — APPEND inside `docs/PAPERS-v2.md`, under P-001

**AUTHORED-SHA256** (range: **first `###` header → EOF**, anchored to line starts, **SECOND
occurrence of the marker**) = `2d4edbc93aaf695f6c84037e11239b998aad642a33bf4d0f696c502dcb14abd4`
**bytes** = `4825`

> ⚠⚠ **`PAPERS-v2.md` IS THE CLAIM REGISTER AND THIS BELONGS INSIDE IT, UNDER `P-001`.** **Not a
> standalone file** — *a second home for claims is how `D-062` happened, and `P-004`'s own header
> says so.*
>
> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE.** Landing header **above** the marker, outside the range.
> ⚠ **`PAPERS-v2.md` uses `##` for papers.** **Confirm the level this file's `###` should take on
> landing, and declare the substitution with its byte delta** — *`F-053` went out at the wrong level
> and Code caught it.*

---

### P-001 amendment ‹N› — ⚠⚠ The comparator arm is POOLED, and the paper must say so before a reviewer does

- **Date:** 2026-08-21 · **Status:** ⚠ a **limitation recorded against `P-001`**, not a change to its
  claim or its gate.
- **Found by:** `XF3`, which was ordered to establish whether tumour-category pooling affects the
  SCORER. ⚠ **It answered no — and then found the edge the order had not scoped.**

---

**1 — THE FINDING.**

**`P-001`'s headline is that the structural ranking is *"not distinguishable from ranking by
expression and prior evidence."*** ⚠⚠ **The expression arm is built on HPA tumour categories, and
those categories POOL populations that are clinically distinct.**

**`XE`, measured: HPA documents no tumour category's contents — `hpa_composition_undocumented`, 20 of
20.** ⚠ **Three are sourced as pooling** (HPA's own documents); **seventeen are `unknown_to_code`.**
⚠⚠ **So a reader — and this paper — cannot say what population any expression figure describes.**

**⚠ THE SCORE IS UNAFFECTED AND THAT IS ENFORCED, NOT ASSERTED.** `core/scorer.py` imports nothing
clinical; the six pre-registered features are structural and confidence; **`EE-0` widened
`test_the_scorers_feature_path_is_closed` to every clinical-layer field, proven RED four ways
including the rename route.** ⚠⚠ ***The score being clean does not make the COMPARISON clean.***

**2 — ⚠⚠ IT CUTS AGAINST US, AND THAT IS WHY IT LEADS.**

**A pooled comparator is a BLURRIER TARGET than an unpooled one.** ⚠⚠ **So *"not distinguishable"* is
being claimed against a weaker opponent than the sentence implies** — **and a weaker opponent makes
indistinguishability easier to achieve and less interesting to report.**

⚠ **This is not a refutation. `P-001`'s comparison stands and its numbers are unchanged.** **What
changes is what the comparison is a comparison TO, and the paper states it in its own words rather
than letting a reviewer supply them.**

**3 — ⚠⚠ AND IT JOINS `P-001` TO `P-004` IN A WAY NEITHER ENTRY CURRENTLY HAS.**

**`P-004` argues the comparator's METHOD carries less than it is read to carry** — the score conflates
prevalence with intensity, the weights are arbitrary, the cutoff sits on a modal value.
⚠⚠ **This says the comparator's DATA does too: the categories the method operates over pool
populations oncology treats as different diseases.**

**⚠ The same argument, one layer down, measured on our own copy of the data.** ⚠⚠ **And it strengthens
`P-004` by citation rather than by length — which is `PAPERS-v2`'s own rule about not letting one
paper's scope bound become another's thesis.**

**4 — ⚠ AN UNASKED MEASUREMENT THAT DECIDES HOW SERIOUS THIS IS.**

⚠⚠ **Is the pooling UNIFORM NOISE, or is it DIRECTIONAL?**

**`XF1`: at most four of 82 are plausibly subtype-defining — `ERBB2`, `NECTIN4`, `EGFR`, `FGFR3`.**
⚠ **If those four sit systematically HIGH or LOW in the expression arm, the pooling is not noise —
it biases the comparator in a direction, and the paper must say which.** **If they are scattered, the
effect is dilution and the limitation is milder.**

**⚠ Nobody has asked this. It needs no new supplier and no fold.** ⚠⚠ **Pre-registered here, both
outcomes at equal prominence, BEFORE the measurement exists:** **directional → a stated bias with its
sign; scattered → a stated dilution.** ***Neither is a failure and the entry will report whichever
lands.***

**5 — ⚠ And a fact about the cohort that this exposed sideways.**

**`XF1` found Group C EMPTY: `TROP2`, `CLDN18.2`, `FRα`, `PSMA` and `CD79b` are NOT IN THE 82 AT
ALL** — ⚠ **half the subtype-defining ADC biomarkers named.** **`F-009` already records that Kathad
name TROP2, HER3 and CLDN18.2 as omitted themselves.**
⚠⚠ **So the cohort under-represents exactly the class of target where the pooling matters most** —
**which is a fact about what the cohort is a sample of, and belongs in `P-001`'s population
description rather than in its limitations.**

**6 — ⚠ What this amendment does NOT do.**
- ⚠⚠ **It does not change `P-001`'s claim, its numbers, or its gate.**
- **It does not propose un-pooling anything** — **HPA has no codes and cannot be subdivided.**
- ⚠ **It does not claim twenty categories pool.** **Three are sourced; seventeen are unknown; and
  *unknown* is reported as unknown.**
- ⚠⚠ **It does not assert the effect is material.** **§4's measurement decides that, and it has not
  run.**

**⚠ Where this goes in the paper:** **the LIMITATIONS section, before any reviewer reaches it** — and
⚠⚠ **§5 goes in the POPULATION description, because a cohort that under-represents a class of target
is a fact about the sample, not a caveat on the result.**
