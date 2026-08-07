# CAPTURE — 2026-08-06 — The lumenal bridge: F-011's annex is scoreable by the existing pipeline, and the case for it is commercial

> **CAPTURE, not a finding and not a decision. Nothing here is ruled.** It extends `### F-011`
> and does not amend it. Where this file and the log differ, **THE LOG GOVERNS.** ⚠ This file is
> not authority; it is a record of an argument made 2026-08-06 and the gates it must clear before
> any of it reaches a deck, a surface, or a paper.
>
> **Number: NOT TAKEN.** `F-025` is confirmed free but three findings are already queued for it.
> ⚠ **Taking a contested integer under pressure is the F-017 double-claim.** Owner rules.

> **Planner provenance (D-016).** Sections 1 and 2 are Planner-supplied reasoning from general
> knowledge. **No primary source was opened at first hand for either.** Section 3's clinical data
> was retrieved by web search 2026-08-06 and is cited. **Every claim below carries its status.**

---

## §1 — The technical bridge: lumenal IS extracellular

**Status: ⚠ PLANNER-SUPPLIED FROM GENERAL KNOWLEDGE. Textbook cell biology, not opened at first
hand. Must be sourced before it reaches a deck (§5).**

A membrane protein's topology is established at insertion into the ER membrane and **preserved
through the entire secretory pathway.** A protein residing in the ER, Golgi, endosomal or lysosomal
membrane has a **lumenal** domain. When a vesicle fuses with the plasma membrane, **the lumenal face
becomes the extracellular face.**

⚠ **The consequence, and it is the operative one:**

**UniProt has already annotated the ECD of these proteins. It calls the span something else.**

The topology feature exists. The domain boundaries exist. **The geometry the six features measure is
the same geometry.** So:

- `census_spans.py` reads the same topology block
- the ECD slicer takes the same `sequence.value[start:end]`
- ESMFold folds the same kind of soluble domain
- the six features compute unchanged
- `geom_proxy` scores it on the axis validated in `### F-017`

⚠ **This is what turns F-011 from a boundary condition into a runnable experiment.** F-011 says the
excluded class may contain the best targets; **it explicitly does not claim this project's scorer
recovers anything from it.** The bridge does not change that claim — **it changes the cost of
testing it from "build a new pipeline" to "point the existing one at a file we have already
pulled."**

**The annex is 2,209 proteins and its spans are being fetched today.**

---

## §2 — The commercial framing, which is stronger than the clinical one

**Status: ⚠ PLANNER-SUPPLIED STRUCTURAL ARGUMENT. No market figure below has been verified.
Every quantitative claim about the ADC landscape must be sourced before use (§5).**

**The argument:**

1. **Validated surface antigens are contested ground.** A small number of targets carry a large
   share of the ADC pipeline, with multiple programs per target. The consequences are IP crowding,
   parallel trials, and pricing pressure at launch. ⚠ **Shape asserted; magnitudes unverified.**
2. **The annex is uncontested.** Freedom to operate, composition-of-matter available, no race.
3. ⚠ **Conditional expression is not merely a differentiator — it lifts a ceiling.** A
   constitutively-expressed target caps the therapeutic window, and therefore caps combinability,
   duration, and how early in the treatment line a drug can move. **A conditionally-trafficked
   target does not carry that cap.** Not a better drug into the same market — **a different market.**
4. **The validation gap is the moat, not the obstacle.** Nobody has tumour-versus-normal surface
   proteomics at scale for this class. **That is why it is uncontested.** ⚠ **Whoever narrows the
   search space first captures most of the value, because the alternative is proteomics on all of
   them.**

⚠ **2,209 candidates is not a program. A ranked shortlist is.** That is what the pipeline sells —
not *"we rank ADC targets"*, which competes with everyone, but **"we rank the class nobody has
ranked."**

**And `### F-017` is what makes it credible:** the geometric axis was tested against an
interpretation frozen before the number existed, survived, **and reported its own confidence
correlation rather than hiding it.** A method that published a narrowing result about itself is one
a partner can believe about a class it cannot independently check.

---

## §3 — The three counterweights, recorded because a partner will raise them

1. ⚠ **Antigen copy number.** MMAE-class payloads generally require high antigen density per cell.
   A conditionally-trafficked protein may sit orders of magnitude below a constitutive one. **This
   is the real objection and it is not answerable computationally.** *(Less binding in an MRD
   setting — clearing micrometastatic cells rather than debulking — but that is a hypothesis, not a
   rebuttal.)*
2. **Some were written off correctly.** F-011 indicts the **classifier's scope**, not every protein
   in the class. ⚠ **The annex is enriched for candidates, not made of them.**
3. **No validation infrastructure exists.** See §2.4 — this is simultaneously the objection and the
   opportunity, and honest framing states both.

---

## §4 — Clinical adjacency, and why it is NOT the frame

**Status: ✅ RETRIEVED BY WEB SEARCH 2026-08-06. Cited, not opened at first hand.**

The prophylaxis question — dosing an ADC at a disease-free interval to clear micrometastatic disease
— has a name: **MRD-guided adjuvant therapy**, and it has read out.

**IMvigor011** (muscle-invasive bladder cancer, post-cystectomy, serial ctDNA surveillance,
ctDNA-positive patients randomised to atezolizumab vs placebo): 12-month DFS **44.7% vs 30.0%**,
12-month OS **85.1% vs 70.0%**. ⚠ **Among 357 persistently ctDNA-negative patients: 12-month DFS
95.4%, 12-month OS 100%.** NCCN has incorporated MRD guidance.

⚠ **Two implications, both against the unselected version of the idea:**

- **The sensitivity premise is now only half true.** Liquid biopsy detects MRD before radiographic
  recurrence. The open question moved to *what to give the people it flags.*
- **A population with 100% 12-month OS has almost no events to prevent.** Treating it prophylactically
  buys little at full toxicity cost.

**And EV specifically is the wrong drug for it.** NECTIN4 is constitutively expressed on normal
epithelium — which is *why* EV carries cumulative peripheral neuropathy, boxed-warning skin
reactions, and hyperglycemia. ⚠ **In a disease-free patient that arithmetic is unfavourable.**

⚠ **BUT the two ideas are one idea.** A conditionally-trafficked target means **there is nothing for
the antibody to bind in a cancer-free patient** — the target itself becomes the selectivity
mechanism, and prophylactic dosing stops being a toxicity gamble. **The prophylaxis idea requires the
non-surface idea; the non-surface idea's strongest clinical application is the prophylaxis idea.**

**This is a therapeutic hypothesis and belongs nowhere near the current paper.** ⚠ It wants an
oncologist's read, and the toxicity and trial-design judgments are real medicine. **Recorded here so
it is not lost, and gated out of the manuscript so it cannot weaken it.**

---

## §5 — ⚠ THE GATES. F-011's own rule binds this capture.

`### F-011` states: *the examples of condition-dependent surface translocation offered in
conversation — **GRP78/HSPA5, calreticulin, nucleolin, LAMP1** — are Planner-supplied from general
knowledge and have NOT been opened at first hand. **None may reach a surface, a deck, or a paper
until its primary source is opened.***

**That rule applies to this capture without modification.**

| Claim | Deck-ready? |
|---|---|
| Lumenal topology becomes extracellular on fusion | ⚠ **NO — source it first.** Textbook, and this project does not put unopened claims on slides |
| UniProt annotates these topology spans | ✅ **After measurement** — count how many annex rows carry topology, off the file. **Do not assert it; it is being measured today** |
| The pipeline scores the annex unmodified | ✅ **After it runs.** Until then it is a design claim, not a result |
| Any ADC market figure | ⚠ **NO — no number verified** |
| The four named proteins | ⚠ **NO — barred by F-011. This is P-002's subject** |
| IMvigor011 figures | ⚠ **Cited from search, not from the paper.** Open the NEJM entry before use |
| The commercial *structure* (§2.1–§2.4) | ⚠ **As an argument, attributed as an argument.** Never as established fact |

⚠ **The one thing that is unconditionally sayable today:** *the excluded class is scoreable by the
existing pipeline at no additional engineering cost, and no one has scored it.* **That is a
statement about this project's own capability and it needs nobody's permission.**

---

## §6 — THE SLIDE

**One slide. Placed after the F-009/F-011 boundary-conditions slide, because it is that slide's
answer.** ⚠ **The deck in the repository predates the 2026-08-05 revision; the revised deck and its
revision spec were never committed. Confirm which deck is current before editing.**

> ### Title
> **The excluded class is reachable — and nobody is looking**
>
> ### Body
>
> **The exclusion**
> SURFY's negative class = *not at the surface under normal conditions.*
> Not the same as *cannot be a target.* ⚠ Condition-dependent trafficking is the selectivity
> property an ADC exists to exploit.
>
> **The bridge**
> A lumenal domain and an extracellular domain are **the same topological face.**
> ⚠ **UniProt has already annotated these spans.**
> → same fetch · same slice · same fold · same six features · same scorer
>
> **The position**
> `<N>` annex proteins carry topology spans *(counted off the file, not estimated)*
> Contested surface antigens: many programs per target.
> This class: **none.**
>
> **The honest line**
> This ranks candidates. **It does not validate them.**
> Copy number and conditional expression need wet-lab confirmation this method cannot supply.
>
> ### Footer
> Extends F-011. Claims nothing about the scorer recovering targets from the negative class.

⚠ **`<N>` is filled from the annex pull, off the file. It is not estimated, not projected, and not
multiplied by anything.** If the annex has not been banded when the deck is needed, **the slide ships
without the number rather than with a guess.**

---

## §7 — What this changes today: nothing

**The crank is unaffected.** The annex pull was already ordered as its own invocation to its own
file. **This capture adds no task, blocks nothing, and authorises nothing.**

**Queued, in order:** source §1 · measure the annex's topology coverage · decide whether the annex
is scored at all *(⚠ owner-reserved, and it interacts with the standing "no scoring of census rows"
gate)* · then the slide.
