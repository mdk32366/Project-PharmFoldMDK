# PROPOSAL — `F-042` remediation, and PAE as a paper candidate

**AUTHORED-SHA256** (range: **first `## §` header → EOF**, anchored to line starts, **SECOND
occurrence of the marker**) = `0839631c6b9c975a597617376b772654505e11f3941b109243af64db6247b2c8`
**bytes** = `6116`

> ⚠ **A PROPOSAL. Nothing is ruled, nothing is built, no fold is scheduled.** For the owner to rule.
> Landing header **above** the first `## §` marker, outside the hash range.

---

## §0 — ⚠⚠ The finding that changes the cost: THIS DOES NOT COMPETE WITH RENTAL

**The census span range is 1–439 aa** (measured, `LA2`). **`CEILING_KNOWN_GOOD` is 440.**

⚠⚠ **EVERY CENSUS FOLD IS A LOCAL FOLD. `F-042`'s remediation is LOCAL GPU TIME, NOT RENTAL MONEY,
and it competes with NOTHING in the rental budget.**

⚠ **Same shape as the feature-extraction correction two days ago** — the Planner assumed a resource
class from the shape of the task, and one measured number refuted it. **Recorded rather than quietly
benefiting from it.**

**What it DOES compete with is local GPU wall-clock, and that is a measurement nobody has taken.**

---

## §1 — What `F-042` actually says, and its close condition is strict

> *"ESMFold emits PAE on every forward pass and the pipeline discards it: 2,690 of 2,690 census folds
> carry none."* **Status OPEN.** ⚠⚠ *"It closes when the local-tier persistence path is repaired **and**
> the 2,690 existing rows either carry PAE or carry the statement that they do not and why.
> **Repairing the path forward does not close it.**"*

**`pae_json_path` is NULL on all 2,690 and set on 79 of 80 cohort rows.** ⚠ **Established by
observation, not inference: `D-099`'s control ran 25 folds at the exact census recipe and PAE came out
25 of 25.**

## §2 — ⚠⚠ Why PAE is the improvement, and pLDDT is not

**pLDDT is PER-RESIDUE — *is this residue placed well locally?*
PAE is PAIRWISE — *is this domain placed correctly RELATIVE to that one?***

⚠⚠ **For a multi-domain ectodomain those are different questions, and the one an ADC cares about is
the PAE question:** **is the epitope where the model says it is, relative to the membrane?**
**A span can average 85 pLDDT with every domain individually crisp and the inter-domain geometry
entirely unconstrained — and pLDDT will not say so.**

⚠ **And pLDDT cannot be improved.** It is a second head predicting its own lDDT-Cα, same weights,
same forward pass. **We can change what we fold or which model folds it; both change the object.**
**PAE is not a better pLDDT — it is a DIFFERENT quantity we already compute and discard.**

## §3 — Three remediation paths, costed honestly

| | what it does | cost | closes `F-042`? |
|---|---|---|---|
| **A — repair forward only** | every future fold persists PAE | ⚠ small, a persistence path | **NO** — the entry says so explicitly |
| **B — repair + refold all 2,690** | full PAE coverage | ⚠⚠ **local GPU wall-clock × 2,690, UNMEASURED** | **yes** |
| **C — repair + carry the statement** | the 2,690 declare `pae_absent_local_tier` with its cause | small | ⚠ **yes, by the entry's own second limb** |

**⚠⚠ THE MEASUREMENT THAT DECIDES B vs C, AND IT IS TEN MINUTES: time ten census folds at the census
recipe — int8, chunk 64, local — spanning the length range, and project 2,690.**

⚠ **If it is hours, B is an overnight run like the extraction was — *an overnight job was provisioned
for something that fits in a coffee break.* If it is days of card time, C is the honest answer and
the absence is a category with a cause, which this project already accepts as a legitimate outcome.**

**⚠ And a fourth path worth costing: B restricted to a stratified SAMPLE**, so PAE exists for enough
rows to answer §4's question without refolding everything. ⚠⚠ **But a sample cannot close `F-042`,
because 2,690 rows would still lack it** — **it is a research path, not a remediation.**

## §4 — ⚠⚠ `P-006` — PAE as a paper candidate, and what it must NOT claim

**The claim is NOT *"we found PAE."*** ⚠ **The claim is a methods claim about what a structure-derived
target screen reports:**

> ⚠⚠ **For multi-domain extracellular domains, mean per-residue confidence is the wrong summary
> statistic, and pipelines that report it are reporting a number that cannot answer the question
> target selection asks.**

**Testable, on our own data:** **PAE exists on 79 cohort rows today.** ⚠ **Where do pLDDT and PAE
DISAGREE?** **A target with high mean pLDDT and poor inter-domain PAE is the case that makes the
argument — and if no such target exists in the 79, the argument is weak and must be reported as
weak.**

**⚠⚠ WHAT `P-006` MAY NOT CLAIM, AND THIS IS THE GATE:**
- ⚠⚠ **NOT that this is unnoticed in the field. PAE is well known and widely used in structural
  biology.** **The literature has NOT been searched, and *"nobody has noticed this"* is precisely the
  shape `F-047` catalogues.** **A literature search is a GATE CONDITION, not a caveat.**
- ⚠ **Not that PAE is accuracy.** **It is a second learned output, and `D-039`'s calibration
  disclaimer applies to it at least as much as to pLDDT** — ⚠⚠ **arguably more, since nothing in this
  project has ever compared a PAE matrix to anything.**
- **Not a claim about the census** until the census carries PAE at all.

**⚠ Where it sits relative to the others:** **`P-001` is the structural axis; `P-004` is the
comparator's method; `P-005` is evidence coverage.** ⚠⚠ **`P-006` is about the CONFIDENCE INSTRUMENT
itself, and it is the natural companion to `P-001`'s limitations section** — **`F-051` already
establishes that 38.6% of attribution rides on two confidence features and 32.2% on one.**

**Proposed gate:** ⚠ **a literature search that comes back with the claim unmade or unmeasured in
this application** · **at least one cohort target where pLDDT and PAE materially disagree** · **and
`F-042` resolved by path A, B or C so the paper can state what the census does and does not carry.**

## §5 — What the owner rules

1. **A, B, C, or B-as-sample.** ⚠ **The ten-fold timing runs first either way — it is ten minutes and
   it decides the rest.**
2. **Whether `P-006` is registered in `PAPERS-v2.md` as a candidate**, with the gate above.
3. ⚠ **Whether the PAE-vs-pLDDT disagreement measurement on the existing 79 runs now** — it needs no
   folds, no rental and no card, ⚠⚠ **and it is the measurement that tells us whether `P-006` has a
   paper in it at all.**
