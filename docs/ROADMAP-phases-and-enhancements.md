# ROADMAP — PharmFoldMDK: from validation study to target-prioritization platform, and the paper that gates the two

> **Status:** roadmap, not orders. Written 2026-08-01, after the demo, the Grok second opinion, and
> the cohort-boundary findings (F-009). **Context shift:** the semester is over; the graded-deliverable
> constraint is gone. The optimization target is now **a publishable result that survives peer
> review** — a higher and different bar than a course demo. This document phases the work, stack-ranks
> the enhancements by timing / effort / paper-necessity, and makes explicit which fork each depends on.
>
> **The one thing that governs everything below:** D-075 (the pLDDT-ablation) is not merely the top
> priority — **it is the fork that decides which paper exists.** Every item is tagged for which branch
> it serves. Do not invest in Phase-2 comprehensiveness before D-075 resolves; a census built on an
> unproven axis is built on sand.

---

## Part I — The two-phase architecture (what the project actually is)

The project has quietly been two projects. Naming them dissolves the "the 82 is incomplete" worry,
because incompleteness is a defect in one phase and a boundary condition in the other.

### Phase 1 — Validation study (where we are)
*Does a structure-derived axis measure something real and ADC-relevant, independent of confounds?*

- Fixed cohort (Kathad 82), used as **comparator, not census.** Incompleteness is correct here —
  you validate on a fixed, published, comparable set. Comprehensiveness would *break* the comparison.
- Pre-registered result (F-004), now under its sharpest test (D-075).
- **The 82 is FOR this phase. Its job is to be a fair test, not a complete list.**

### Phase 2 — Target-prioritization platform (the vision)
*Given a comprehensive census of ADC-targetable antigens, rank them by structural suitability, then
stack by the cancers they drive, prevalence, lethality, and delivery-axis constraints (BBB/CNS).*

- Census is now the **product**, so completeness is the entire value proposition — every missing
  CD33 is a real hole.
- The stacking layer (disease / prevalence / lethality / delivery) turns a suitability score into a
  **decision tool** — and is where domain expertise becomes the differentiator no pure-ML approach has.
- The delivery axis is **orthogonal** to structure: a target can be structurally perfect and
  therapeutically useless for glioblastoma because the ADC can't cross the BBB. Stacking makes that
  visible as a category ("structurally suitable, delivery-constrained"), not a hidden weakness.

### The gate between them
**Phase 2 is gated on D-075.** If the structural axis survives the ablation (signal isn't just
pLDDT/attention), the platform has a foundation and comprehensiveness is worth building. If it
collapses, Phase 2 pauses — you do not build a census on an axis that doesn't measure structure.
**This gate is the single most important line in the roadmap.**

---

## Part II — The paper, and the fork that decides it

The paper's shape depends entirely on D-075's outcome. Both are publishable; they are different papers.

### Branch A — D-075 survives (geometric signal persists without pLDDT features)
**Paper:** *"A structure-derived axis for ADC target prioritization is orthogonal to expression and
robust to confidence confounds."* A positive methods contribution. The novelty gap (F-009 + lit
review) + the pre-registered orthogonality result + the ablation that rules out the attention
artifact = a clean, defensible story. This is the paper you want.

### Branch B — D-075 collapses (signal was mostly pLDDT/attention)
**Paper:** *"Predicted-structure confidence confounds structure-based target prioritization: a
cautionary analysis."* A negative/methods contribution — still publishable, arguably *more* useful
to the field, but smaller and differently framed. The honesty apparatus (pre-registration, the
ablation, the confound named before testing) is what makes this publishable rather than embarrassing.

**Either way the paper exists.** But you cannot write either until D-075 resolves — which is why it
tops every stack below.

---

## Part III — Enhancements, stack-ranked

Each item tagged: **[timing]** (now / soon / later) · **[effort]** (S/M/L) · **[branch]** (which
paper it serves) · **[paper-critical?]** (does the paper fail without it).

### TIER 0 — Do first, blocks everything (the fork)

**0.1 · D-075 the pLDDT-ablation + popularity-matched control**
`[now] [effort M] [both branches] [PAPER-CRITICAL: it decides which paper]`
The pre-registered ablation. Build the confidence-blind proxy red-then-green, freeze it, run A then
B. Resolves the fork. Nothing else in the paper can be finalized until this lands. **This is the
whole ballgame.**

### TIER 1 — Paper-critical, do soon, needed for Branch A specifically

**1.1 · Held-out validation set of Kathad-excluded ADC targets (Trop-2, CD30, CD33, CEACAM5, + sweep)**
`[soon] [effort M–L] [Branch A] [PAPER-CRITICAL for a strong Branch A]`
This is the answer to Grok's sinking question and it partially escapes the circularity: these are
clinically-validated positives the expression filter *missed*, so "attention → pLDDT → rank" doesn't
automatically explain them. If the structural axis enriches on this independent set, Branch A goes
from "orthogonal but unproven" to "orthogonal AND generalizes to held-out clinical positives." **This
may be the difference between a workshop paper and a real one.** Effort: a curation pass (which
approved/late-stage ADC targets sit outside Kathad — partly done: 4 identified) + folding those ECDs
(they're sliceable; CD33's ECD is Asp18–Gly260). Gated on D-075 surviving — pointless if it collapses.

**1.2 · Expand the labelled positive set beyond n=12**
`[soon] [effort M] [Branch A] [PAPER-CRITICAL: n=12 is the binding constraint]`
Grok's "n=12 has no statistical leverage" is correct and it is the single most-cited weakness. The
roster floor of 12 (F-003) is *the* limiting factor on every result. Systematically curating more
labelled ADC-attempt positives (from clinical-trial registries, not just Kathad's 22) is the highest-
value statistical improvement. More labels beats more features or more model every time. **The paper's
power section lives or dies here.**

**1.3 · Systematic literature review (upgrade the 7-paper nearest-neighbour pass to defensible)**
`[soon] [effort M] [both] [PAPER-CRITICAL: novelty claim]`
The current lit review is a focused pass, explicitly not systematic (PRISMA). A paper's novelty claim
needs the systematic version — including the PNAS 2026 surfaceome paper Grok surfaced, and a verified
Site4Drug. Reviewers will check this. Elicit's systematic-review tool is built for exactly this if the
API access is sorted.

### TIER 2 — Strengthens the paper, do during writing, not blocking

**2.1 · Fold IGF2R (close the one honest coverage gap)**
`[now — it's cheap] [effort S] [both] [not paper-critical, but free]`
One rental block, same recipe, no asterisk. 79 → 80. Do it because it's nearly free and removes a
"why isn't this folded" question, not because the paper needs it. Already specified (D-072 Tier 1).

**2.2 · The confound section, written to Grok's steelman**
`[soon] [effort S] [both] [PAPER-CRITICAL: pre-empts reviewer 2]`
The paper must contain the confound analysis D-075 produces, written at full strength — not buried.
A reviewer who sees you named and tested the attention confound *before* they raised it is disarmed.
This is writing, not experiment, but it's load-bearing.

**2.3 · Address the feature-commensurability question for any non-sliced-ECD targets**
`[soon] [effort S] [both] [paper-critical if held-out set includes stitched folds]`
Grok's commensurability attack (stitched/partial folds aren't comparable to single-pass) applies to
the held-out set (1.1) if any of those targets need domain assembly. The held-out logic doc already
frames the four exit reasons; this extends it to "how folds from different methods can/can't share a
ranking." Matters only if 1.1 hits large targets.

### TIER 3 — Phase-2 platform, LATER, gated on D-075 surviving + paper submitted

**3.1 · Comprehensive census of ADC-targetable antigens**
`[later] [effort L] [Branch A only] [not paper-critical for Phase 1]`
The real census — systematic surfaceome + clinical-ADC sweep, not Kathad's 82. This is Phase 2's
foundation. **Do not start before D-075 survives and the Phase-1 paper is drafted.** A census is
months of curation; spending it on an unproven axis is the roadmap's cardinal error.

**3.2 · Disease-stacking layer (cancers caused / prevalence / lethality)**
`[later] [effort L] [Branch A / platform] [the platform's actual novelty]`
Turns suitability scores into a decision tool. Where domain expertise differentiates. Needs the
census (3.1) first, and disease-association data (COSMIC, TCGA, literature) mapped per target.

**3.3 · Delivery-axis flagging (BBB / CNS constraint)**
`[later] [effort M] [platform] [the sharpest domain contribution]`
Flag structurally-suitable-but-delivery-constrained targets (glio, CNS). Orthogonal to structure;
makes the multi-axis nature of ADC suitability explicit. Builds on D-041's existing claim boundary.
Smaller than 3.1/3.2 because it's a categorical overlay, not a new scoring model.

---

## Part IV — The recommended sequence (reading the stack as a path)

1. **D-075** (Tier 0) — resolve the fork. *Everything waits on this.*
2. **In parallel, cheap & non-blocking:** IGF2R fold (2.1), start the systematic lit review (1.3),
   write the confound section as D-075 produces it (2.2).
3. **If D-075 survives → Branch A:** build the held-out validation set (1.1) and expand positives
   (1.2) — these two are what make Branch A a strong paper rather than a weak one. Then write.
4. **If D-075 collapses → Branch B:** pivot to the cautionary-methods paper; 1.1/1.2 become less
   central (you're documenting a confound, not proving an axis); write sooner, smaller.
5. **Paper submitted → Phase 2 unlocked:** census (3.1), then disease-stacking (3.2) and
   delivery-flagging (3.3). Only if Branch A.

---

## Part V — The honest one-paragraph version

The semester ending changed the target from "defensible demo" to "publishable result," and today's
work exposed both the novelty (a real, empty niche, backed by F-009's false negatives and the lit
review) and the weakness (the pLDDT-attention confound Grok sharpened into D-075). **D-075 is the
fork: it decides whether the paper is "a structural axis that works" or "a confound that fooled us" —
both publishable, one much better.** The highest-value moves are all about *statistical and
independent-label strength* (D-075, the held-out set, more positives), not features or model
complexity — exactly what Grok said. The census-and-stacking platform is the real long-term vision
and the right framing for the paper's "future work," but it is **gated on D-075 surviving and must
not be built before the Phase-1 axis is proven.** Comprehensiveness is a Phase-2 virtue; chasing it
now, before the axis is validated, would be building a census on sand.
