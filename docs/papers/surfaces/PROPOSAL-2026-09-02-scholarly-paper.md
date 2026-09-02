# Proposal for a Scholarly Paper — PharmFoldMDK

> **Date drafted:** 2026-09-02
> **Type:** A summary document for a non-specialist reader. **Not an authority.**
> **Status:** Draft. The claim is not yet selected — see §6.
>
> **⚠ This document is derived, not authoritative.** Every substantive statement below traces to a
> log entry: **D-015 §1** (Kathad's filters, the comparator-not-oracle framing), **F-004** (the
> pre-registered result), **F-009** (the four false negatives and the over-claim guard), **D-075**
> (the outstanding ablation and its pre-committed interpretations), **PAPERS-v2.md** (P-001's two
> branches). Where this document and a log entry differ, **the log entry governs.** This is a
> reading surface, not a second source of truth.
>
> **⚠ Register:** written for a non-technical reader (a supervisor, a manager, a first conversation).
> Plain language is deliberate. It is not a licence to overstate — the honesty constraints in §6 bind
> this document exactly as they bind every other artefact.

---

## §1 — The problem

Right now, most people pick ADC targets by looking at expression — which proteins show up much more
often on tumor cells than on healthy ones. Rank by that, pick the top of the list.

But that method has a track record of missing good targets. Kathad et al. 2024 used expression
filters and left out **Trop-2, CD33, CD30, and CEACAM5**. All four are real ADC targets that made it
to patients. One of them, CD33, is the target of Mylotarg — the very first ADC ever approved. Four
misses is a pattern, not bad luck.

*(Source: F-009. Cohort absence checked by grep against `data/adc_reference_mapping.csv` and
`data/cohort_82.txt`; accessions verified against the UniProt REST API.)*

---

## §2 — The blind spots

Kathad's filters are published, so the kinds of holes the method has can be described directly.

**⚠ What is NOT established:** which specific filter dropped which specific target. The four
absences are confirmed. The per-target mechanism is not traced. That is checkable work, it has not
been done, and it is not guessed at here.

### 2.1 — A hard line through a smooth measurement

The method uses an expression score from 0 to 300 and keeps anything 150 or above. But expression
doesn't come in two flavors. A protein at 149 and one at 151 are basically the same protein, and one
is in the study and one is gone. You have to draw a line somewhere, so this isn't a mistake — but it
means the list has an arbitrary edge, and things near that edge fall out for no biological reason.

### 2.2 — Throwing out anything found in important healthy tissue

Any protein highly expressed in 13 critical normal tissues gets dropped. That sounds obviously right
— you don't want the drug attacking healthy organs. But the real question is whether the damage is
tolerable and manageable. Some approved ADCs hit targets that healthy cells carry too, and the side
effects are handled with dosing and monitoring. A filter this strict deletes drugs that work.

### 2.3 — Requiring the RNA and the protein to agree

Cells make RNA first, then build proteins from it. The method requires those two measurements to
line up. Usually they do. But sometimes a cell already has the protein built and simply moves it to
the surface when conditions change — under stress, low oxygen, or after treatment. Then the RNA
looks flat while the protein is sitting right there on the surface, and the filter throws it out.

*(This hole is the subject of a separate candidate paper, **P-002**. That candidate currently has a
question and no measurement, and is recorded as such.)*

### 2.4 — The scoring rewards proteins people already study

The evidence score counts things like how many papers exist, whether antibodies have already been
made, and whether the target has been in trials. So a protein nobody has looked at scores low
*because* nobody has looked at it, not because it's a bad target. That is circular — a popularity
score wearing a biology costume.

**⚠ The same trap applies to this project's own method.** The model here uses the folding model's
confidence score (pLDDT), and that score is also higher for well-studied proteins. Testing that is
the outstanding run (§6). This section does not point at a flaw in their method that this project
has already escaped.

### 2.5 — Nobody measured shape at all

The entire Kathad feature set is about *how much* protein is there. Nothing asks whether a drug can
physically reach it. Those are different questions. No structures were folded, so this axis isn't
measured — it's absent.

### 2.6 — Why this strengthens the argument rather than weakening it

Kathad et al. published their filters in full and openly recorded that those filters excluded
**TROP2, HER3, and CLDN18.2**. They flagged their own misses. That is a careful, transparent paper.

Which is the point: **these blind spots are not sloppiness. They are built into what expression-based
ranking is.** A more careful version of the same approach has the same holes. That is the case for
adding a second, independent axis rather than tightening the filters on the first one.

---

## §3 — The idea, and what was built

§2.5 is the blind spot this project can act on. An ADC has to physically attach to the part of the
protein sticking out of the cell, so the shape of that part should matter. Nobody has measured it
carefully across a whole set of targets, because nobody had the structures. Folding models make
getting them cheap now.

**What exists:** a pipeline that predicts the 3D shape of each candidate target's extracellular
segment using **ESMFold, run in-project** — not retrieved from a structure database. It derives
shape-based features from those predictions, fits a ranking model, and asks one question: *does the
shape-based ranking reorder the expression-based one in a way that means something?*

The pipeline now folds past the length limit ESMFold was trained on, which brings large targets into
range that would otherwise be skipped.

---

## §4 — Why this appears to be publishable

### 4.1 — The most interesting question is what is actually driving the result

Folding models report how confident they are in each prediction (**pLDDT**). Models are more
confident about proteins that have been studied heavily. Heavily studied proteins are also the ones
people already tried as ADC targets. So a shape-based ranking that appears to work might be
re-discovering which proteins are famous.

The test separating those two explanations was written down first, a feature that ignores the
confidence score entirely was built for it, and **both possible interpretations were committed in
writing before anything ran** (D-075 Decision 4). Results that deflate a popular assumption are
underreported precisely because they are not what anyone hopes to find — which is part of what makes
this one worth writing up.

### 4.2 — The critique of the existing method stands alone

The blind spots in §2 are documented and checkable. They say something about expression-based
ranking regardless of whether this project's scorer turns out to be any good.

### 4.3 — The method discipline is the differentiator

Predictions recorded before results. Stated denominators. Corrections written into the log rather
than quietly patched. Tests required to fail before they are trusted to pass. The
limitations-and-threats section is normally where papers are weakest; here it is the strongest part.

That is not the contribution. It is what makes the contribution trustworthy.

---

## §5 — Why it could matter: better, faster, cheaper ADCs

**⚠ None of this is demonstrated.** It is the case for why the work is worth doing, not a claim
about what it has achieved.

**Better.** Expression asks *is there a lot of this protein on the tumor?* It does not ask *can a
drug get to it?* A target can pass the first and fail the second. A shape-based check adds a second,
independent way to sort candidates. A wider net means pursuing targets nobody is working on, rather
than building the sixth ADC against the same well-known protein.

**Faster.** Testing a target in the lab means making an antibody, attaching a drug, and running cell
and animal experiments — months per target. Predicting a shape takes hours and a few dollars of
compute. A computational screen does not replace the experiments; it decides which experiments are
worth running.

**Cheaper.** ADC programs fail late and expensively. A target that looked good on paper can burn
years before the problem surfaces in a trial. Moving a *this will not work* signal from phase 2 back
to a computational screen saves everything in between. Cheap failures early are how expensive
successes later get funded.

**And the outcome that is easy to overlook:** if the outstanding run comes back the other way, that
saves money too. Telling the field *the confidence score is misleading you, do not build on it*
stops other groups from spending years on the same dead end. A clear negative result has real value
to everyone who would have tried it next.

---

## §6 — What must be said plainly

### 6.1 — The claim is not selected

One run is outstanding (**D-075**). Two papers were committed in advance, at equal prominence:

- **Branch A** — a structure-derived axis for ADC target prioritization is orthogonal to expression
  and robust to confidence confounds.
- **Branch B** — predicted-structure confidence confounds structure-based target prioritization: a
  cautionary analysis.

**Both are publishable. Neither is claimed until the run decides.** This document must be revised,
not merely appended to, once it does.

### 6.2 — The boundary that does not move (F-009 §3)

*The expression method has documented blind spots* is established.

*This project's scorer fills them* is **not** established, and is not asserted anywhere in this
document. The four targets in §1 are unfolded and unscored here. Two of them (CD30, CD33) are
attention-rich — the exact confound D-075 exists to test — so using them as validation would walk
straight into the problem the project is trying to measure.

These are separate claims. Only the first one is proven.

---

## §7 — Definition of done for this document

- [ ] Cross-checked against `docs/README.md` and `PAPERS-v2.md` before it is shown to anyone outside
      the project — a summary drafted from a snapshot can assert a stale state.
- [ ] §6.1 revised after D-075 rules; branch named, both-branches framing removed or retained as
      history with the outcome stated.
- [ ] §2 gains the per-target filter trace, or keeps its explicit "not established" marker.
- [ ] The §6.2 over-claim guard respected in any derived artefact (deck, abstract, email).
- [ ] Every cited entry (D-015, F-004, F-009, D-075, P-001, P-002) resolves in the log — the
      citation invariant applies to this file too.
