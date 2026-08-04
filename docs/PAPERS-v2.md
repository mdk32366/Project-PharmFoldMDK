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
