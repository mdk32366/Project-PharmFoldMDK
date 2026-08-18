# PAPERS — the claim register (RE-ISSUE v2, 2026-08-04)

> **Supersedes the first issue, which never reached the repository.** ⟡ marks v2 changes.
>
> **What this is.** Two candidate papers with different claims, different gates, and different
> evidence. Without a register, F-entries get silently recruited to whichever paper is being written
> that week, and a finding written to *bound* one paper's scope becomes load-bearing for another's
> thesis without anyone deciding it should.
>
> **Entry bar:** a paper enters when it has a **stated claim** and a **named gate**. An interesting
> topic is not a paper; ideas live in the roadmap until they have both.

---

## P-001 — The structural axis (Phase 1)

- **Status:** Evidence complete pending one run. **Branch undecided.**
- **The gate:** **D-075.** The run selects the claim; the claim has not been made.
- **The claim, both branches, pre-committed at equal prominence (D-075 Decision 4):**
  - **Branch A** — a structure-derived axis for ADC target prioritization is orthogonal to
    expression and robust to confidence confounds.
  - **Branch B** — predicted-structure confidence confounds structure-based target prioritization:
    a cautionary analysis.
- **Draws on:** F-004 · F-005 · F-006 · F-008 · F-009 · D-075 · D-041/D-060.
- **⚠ Reserved:** F-009's over-claim guard is P-001's and it binds. *The comparator has blind spots*
  stays strictly separate from *our scorer fills them.*

### ⟡ Two additions from 2026-08-04, both about the method rather than the result

**⟡ Commensurability is now a named open question (F-012, F-015).** `fold_provenance` shows the 80
folded rows span **three recipes** — `('int8',64)×42`, `('fp16',None)×34`, `('fp16',64)×3`, one
unrecorded — and Task 1c measured that **chunk size changes ESMFold's output** (64≡32; 64≠16 at
45/342 coordinates, max 1.0e-3 Å, and 111/114 pLDDT, max 2.08e-3, on a 114 aa fixture at int8).

**This does not invalidate F-004** and no claim is made in either direction: the cohort's actual
variable is **chunked-versus-not** (`None` vs `64`), which is a different question from the one
measured and is untested at fp16 and at cohort lengths. **"Those 34 folds are fine" is exactly as
unsupported as the opposite.**

⚠ **What it does mean for the paper:** Grok's commensurability attack now has *evidence behind it*,
and it will be raised. **D-075 Decision 6's "what this design cannot separate" gains a fourth item,
and the limitations section must carry it at full strength** — the F-005 treatment, not a footnote.
Found by us, before review.

**⟡ The methods section's honesty claim needs its corrected form (A-016).** Red-then-green is a
stated strength of both branches, and it rested on an unstated assumption: *any red proves the
assertion bites.* It does not — an error-red and a failure-red are different objects, and Code
caught one guard "reddening" as a **collection error** with the assertion never executing. **No
F-004 or F-005 guard was proven by a fake red**, and the one affected guard was re-proven. But if
either branch claims red-then-green, it claims the corrected version: *the revert must be a
realistic mistake and must fail at the assertion.*

- **Open before submission:** the D-075 run · systematic lit review (PRISMA-grade) · Site4Drug and
  PNAS 2026 verified · the n=12 power section · method-novelty language dropped in favour of *"first
  honest measurement of an under-explored axis"* · ⟡ the commensurability limitation written to
  Grok's steelman · ⟡ the corrected red-then-green formulation.

---

## P-002 — The surfaceome negative class (candidate)

- **Status:** **Candidate.** One finding, no evidence, no method. **Not started.**
- **The gate:** *unset — owner ruling needed.* Candidates: P-001 submitted; or a curated set of
  condition-dependent-trafficking targets with opened primary sources.
- **The claim, provisional:** the standard in-silico surfaceome's negative class is defined by
  steady-state localization under normal conditions, which excludes condition-dependent surface
  trafficking — plausibly the class with the strongest ADC therapeutic window. **The boundary is a
  property of the classifier's training data, not of target biology.**
- **Draws on:** **F-011** · F-009 (the same shape one level down — the *pattern* claim needs both) ·
  SURFY/PNAS and CSPA as primary sources.
- **⟡ Evidence state, corrected:** the positive class (**2,886**) is now verified by counting
  `surfaceome_ids.txt`. **The negative class has never been counted** — the membraneome table is an
  unresolved LFS pointer. So the paper's *subject* is currently a number from a figure legend.
  Discharged by scale-readiness Task A.
- **What it does NOT have:** any measurement · any curated candidate list · any opened primary
  source for the four trafficking examples · a method for establishing condition-dependent surface
  exposure.
- **⚠ The failure mode, named now:** P-002 is *one good question and four unverified protein names.*
  The argument is compelling enough to write before the evidence exists. **A compelling argument
  with no measurement is an opinion piece.** If P-002 proceeds, its first work is curation and
  sourcing, not drafting.

---

## ⟡ P-003 — ESMFold's chunked trunk is not output-invariant (candidate, and possibly not a paper)

- **Status:** **Candidate, deliberately under-promoted.**
- **The gate:** none needed — F-012 is measured and landed. The gate is on *whether it deserves
  standing at all.*
- **The claim:** chunked attention in ESMFold's trunk changes predicted coordinates and per-residue
  confidence; folds produced under different `chunk_size` are not byte-commensurable, which matters
  for any pipeline computing geometric features across a heterogeneous compute fleet.
- **Draws on:** F-012 · F-015 · the determinism control Code added.
- **⚠ Honest assessment, recorded so it is not inflated later:** this is **probably a paragraph in
  P-001's methods, not a paper.** The magnitude is tiny, it is one dtype at one short length, and
  the *reason* it matters here is specific to this project's fleet. **It is listed because
  practitioners do not report it and someone at scale would want to know — not because it currently
  clears the bar.** ⟡ If it grows, it grows on measurement (fp16, cohort lengths, `None` vs `64`),
  not on enthusiasm.

---

## ⟡ P-004 — What an expression-threshold target screen can and cannot support (candidate)

- **Registered:** 2026-08-17 · **Status:** candidate. ⚠ **No gate set — owner ruling needed.**
- **Subject:** ⚠⚠ **the method CLASS, not the paper.** Kathad et al. 2024 is the worked instance
  because it is fully published *with its underlying data*; the funnel's early steps are credited
  by its own Methods to Razzaghdoust et al. **Framing it as a critique of one paper makes it
  perishable and adversarial; framing it as an appraisal of a screen design makes it durable and
  constructive.**

### ⚠⚠ THE BAR — what makes this a paper rather than an opinion piece

**Every item states whether it is reproducible from published material alone.** A reviewer holding
the paper and its S3 must be able to check it **without us**. ⚠ **An item that fails this bar is
recorded here and is NOT part of the argument** — it is a question for the authors.

**And the honest frame, which must lead and never be softened:** *the arithmetic is correct.*
`D-100` reproduces all **337 kept pairs exactly** and correctly excludes all **1,303** below the
cutoff, under a denominator convention **read off the published file**, not recovered by matching.
⚠⚠ **This paper does not claim an error. It claims that the measure carries less than it is read
to carry, and that the funnel's shape guarantees part of its own conclusion.**

### The items

| # | item | status | reviewer-checkable? |
|---|---|---|---|
| 1 | Validation is circular | reasoned | ⚠ **yes — needs no data at all** |
| 2 | The score conflates prevalence with intensity | **measured** | **yes, from S3** |
| 3 | The ordinal weights are arbitrary and the result is sensitive to them | **measured** | **yes, from S3** |
| 4 | Therapeutic index is two thresholds, never a ratio | reasoned | yes |
| 5 | The cutoff sits on the modal value of a ~11-patient estimator (`F-043`) | **measured** | **yes, from S3** |
| 6 | Consistency step 6b may be unfirable | ⚠ **hypothesis** | ⚠⚠ **NO — see below** |

---

**1 — ⚠⚠ The validation is guaranteed by the filter.** The Discussion reads: *"22 ADC targets have
already undergone evaluation in clinical trials or preclinical contexts … demonstrating the validity
of our approach."* **But the final stage filters on five evidence criteria, of which #4 is "targets
tested in preclinical setting" and #5 is "targets tested in clinical setting," and genes with none
of the five were removed.** ⚠ **"Has been tested as an ADC target" is therefore an inclusion
criterion.** The 22 could not have been absent. **The screen was not validated by recovering them;
it was constrained to contain them.** *(Reasoned from Methods against Discussion. No data required.)*

**2 — The score collapses two different clinical propositions into one number.** `qh = %low +
2·%medium + 3·%high` cannot distinguish *how many patients express it* from *how strongly*.
Measured on the 337: **JAG1/stomach = 200.0 with 11 of 11 patients at medium and none high;
MERTK/thyroid = 200.0 with 2 high, 1 medium, 1 not detected.** ⚠ **151 of 337 surviving pairs have
ZERO patients scoring high. 36 have ≥25% of patients at *not detected*.** For an ADC these are
different problems — payload potency versus patient selection — and **target selection is where that
distinction is decided.**

**3 — The 1-2-3 weights are a linear scale on a roughly logarithmic quantity, and the answer moves
a long way.** IHC intensity tracks antigen density approximately logarithmically. Rescaling the
cutoff proportionally so the comparison is fair: **1-2-3 → 337 pairs · 1-2-4 → 226 · 1-3-9 → 131.**
⚠ **A 61% reduction under a defensible alternative.** The weights are not stated as a choice and no
sensitivity is reported.

**4 — Therapeutic index is computed as two independent thresholds and never as a ratio.** Stage 3
removes anything highly expressed in 13 critical normal tissues; stage 4 keeps anything above 150 in
tumour. ⚠ **The two are never divided.** A target with excellent tumour-to-normal contrast in one
indication is dropped for a normal-tissue level that the contrast would have justified — and **the
13 tissues are fixed and indication-agnostic**, when ADC toxicity depends on payload and linker as
much as on target.

**5 — `F-043`, and it leads.** ⚠⚠ **52 pairs sit at exactly 150.0** — the cutoff lands on the modal
discrete value its own estimator can take. `≥150` gives **337**; `>150` gives **285**. **The
inequality sign is worth 52 pairs.** Panels are median **11**, max **12**; **246 of 1,640 rows have
n ≤ 4.** ⚠ **This item leads the paper because it depends on no perturbation rule and reproduces
from the published table in a spreadsheet.** *(The flip-rate figures are WITHDRAWN — `F-043`
amendment 1 — pending re-derivation under five pre-registered rules.)*

**6 — ⚠⚠ RECORDED, NOT ARGUED.** Consistency step 6b requires `qh > 150` computed on mRNA with
categories set by quartiles. **If those quartiles are per-gene across samples, roughly 25/50/25 of
samples fall in each band for every gene, giving `qh = 200` mechanically — a filter that passes
everything while appearing to validate.** The text does not say whether the quartiles are per-gene
or global; a later step's wording (*"we used entire gene expression data to identify the first and
third quartile"*) reads global, which would make 6b meaningful. ⚠ **348 → 123 is the steepest drop
in the funnel and the paper does not report how many genes 6a and 6b removed separately.**
⚠⚠ **This is the most damaging item if true and the least defensible as written. It is a question
for the authors, not a claim — and mixing it into the argument is how a strong paper acquires a soft
flank.**

### ⚠ Standing methodological observations, not yet items

- **A modality substitution nobody can see.** *"In certain cases IHC data was missing … and we
  computed target levels using corresponding mRNA expression levels."* ⚠ **4,771 of 20,082 genes
  (23.8%) have no IHC in any cancer**, and nothing marks which rows were substituted. `F-031`'s
  shape: two populations in one table. **⚠ Measured clean on the 82 — zero S3 rows are
  mRNA-derived — so the contamination sits upstream, in the 1,731 → 763 step.**
- **The antibody choice is undocumented.** ⚠ **52.5% of HPA genes carry more than one antibody**
  (9,140 / 17,407, measured). S3 does not say which was used. **Additive to item 5, not included in
  it.**
- ⚠ **Stage 3 does not reproduce** (`4,875 → 1,731`), so the population the cutoff actually acted on
  cannot be assembled. **`1,731` is a NAMED GAP in every downstream number and must never be
  approximated.**
- **The membrane and surface filters are both model outputs** — HPA *"Predicted membrane proteins"*
  and SURFY. `A-014` applies twice: **a model's positive class is a prediction, not a fact.**

### ⚠ What this paper does NOT claim

- **Not that the arithmetic is wrong.** It is right, and we say so first.
- **Not that the 82 are bad targets.** Nothing here evaluates any target.
- ⚠ **Not that `F-009`'s four validated targets are false negatives of the qh cutoff.** Kathad name
  **TROP2, HER3 and CLDN18.2 as omitted themselves**, and offer three candidate reasons without
  testing which. **Measured (Task J): TROP2 max 118.18 and CLDN18.2 max 133.33 — both 0 of 20
  indications ≥150, so both die at or before the cutoff, presence at stage 4 unconfirmed.
  ⚠ HER3 reaches 277.78 in 19 of 20 and provably did NOT die there.**
- ⚠ **Not that our own numbers are independent of theirs.** The denominator convention came from
  their file. `F-022`: independence of source is not independence of inference.

### The case that is not a mechanism argument

⚠⚠ **`CLDN18.2` in stomach cancer: 4 high, 2 medium, 0 low, 6 not detected, n = 12 → qh 133.33.**
Step size 8.33. **Two available moves — six *not detected* patients exist — lands it on exactly
150.00 and inside the filter.** **CLDN18.2 is the target of zolbetuximab, an approved gastric cancer
therapy, in the indication it was approved for.** *Re-derived independently by Code from a
separately-downloaded v22 file.*

### Relationship to the other papers

⚠ **This is a robustness analysis of P-001's COMPARATOR, and it must stay standalone.**
`PAPERS-v2`'s own rule binds: *one paper's scope bound must not become another's thesis.* Folding
this into P-001 makes P-001 argue two things; **as a separate paper it makes P-001 stronger by
citation rather than by length.** ⚠ **And P-001 may not cite it as established until it publishes.**

### Open

⚠ **Read Kathad's limitations section into the framing, verbatim.** *Done 2026-08-17:* they state
the small-IHC-sample caveat and the cutoff caveat **separately and never connect them.**
**So the contribution is the join and the quantification, not the observation** — and the paper must
say that in its own introduction rather than let a reviewer say it first.

**Gate, unset:** ⚠ candidate conditions — item 5's re-derivation lands under all five rules · item 6
is either resolved or explicitly demoted to a question · a full-grid denominator replaces the
survivorship-conditioned 337 · and the owner rules on whether this precedes or follows P-001.

---

## The rules that make several papers safe

**Every F-entry names which paper(s) it serves, and a finding written for one paper may not silently
become another's thesis.** F-009 is P-001's *scope bound*; in P-002 it is *supporting evidence for a
pattern claim*. Same finding, two loads — fine when written down, and how a caveat gets promoted to
a headline when not.

**No paper cites another's unpublished result as established.** P-002's pattern claim leans on
P-001's F-009; if P-001 has not published, P-002 carries the finding with its own provenance.

**⟡ A candidate may be demoted.** P-003 exists partly to be honest about a finding that is
interesting and probably too small. **Demotion is a normal outcome and is recorded, not deleted** —
a register that only ever grows is a wish list.
