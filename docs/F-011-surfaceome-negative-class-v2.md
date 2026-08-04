# F-011 (RE-ISSUE v2) — The surfaceome classifier's negative class is not "cannot be a target": localization is condition-dependent, and the excluded class may be the one with the best therapeutic window

> **Supersedes the 2026-08-04 first issue, which never reached the repository.** Changes in v2 are
> marked ⟡. **The number is confirmed:** `RESERVED.md` holds F-011 for this finding (F-012 taken by
> the Task 1c verdict; F-013/F-014/F-015 reserved).
>
> ⟡ **Why a re-issue rather than an edit:** the first issue stated three counts as though read from
> data. **Only one of them was.** That is a D-016 defect in a finding whose whole subject is not
> inheriting someone else's numbers uncritically, and it is corrected here rather than patched.
>
> **Type:** A finding about a boundary we were about to inherit, caught before inheriting it.
> Nothing is ruled. No code, no route, no result.
> **Date:** 2026-08-04.

---

## ⟡ Provenance of every number in this entry, stated first because v1 got this wrong

| Number | Status | How known |
|---|---|---|
| **2,886** positive class | ✅ **VERIFIED FROM THE FILE** | `surfaceome_ids.txt`, 2026-08-04: **2,886 lines, 2,886 unique**. Counted, not cited. |
| **2,216** negative class | ⚠ **NOT VERIFIED** | PNAS Fig. 2 legend only. **Not read off any file.** |
| **~5,102** total scored | ⚠ **PLANNER ARITHMETIC** | 2,886 + 2,216, from a figure legend. **Never a row count.** |
| **93.5%** accuracy | ⚠ Cited, source not opened at first hand | PNAS abstract |

⚠ **The membraneome table has not been read.** `table_S3_surfaceome.xlsx`, in Downloads *and* in
project context, is a **Git LFS pointer** — 132 bytes declaring
`oid sha256:2f1b8262463ce1c59a1f945d22f0e9638cb3bfbf5aabe197f43b562a62fb055a`, `size 6864772`.
**So the negative class, the class this entire finding is about, has never been counted.** The
finding's *argument* does not depend on its size; the finding's *numbers* do, and they are labelled
accordingly until Task A lands.

⟡ **Also verified, and not what anyone assumed:** `surfaceome_ids.txt` contains UniProt **entry
names** (`1A01_HUMAN`), not accessions. Every join in this project is keyed by accession. That is a
mapping hazard, tracked separately in the scale-readiness order §2; noted here so no future reader
takes 2,886 IDs as 2,886 joinable rows.

---

## The finding

The census universe was about to be defined as SURFY's positive class, with the negative class
treated as ineligible. That treatment rests on a proposition nobody had stated: **"a protein SURFY
calls non-surface cannot be an ADC target."**

**Mechanistically sound, empirically leaky — and every leak runs toward the targets ADCs most want.**

**Sound:** an IgG cannot reach an epitope inside the ER lumen. A protein genuinely confined to an
intracellular membrane is unreachable. Not disputed.

**Leak 1 — classifier error.** SURFY's reported accuracy is 93.5%. Across a negative class of the
order of two thousand, the implied misclassification count is in the hundreds — ⟡ *stated as an
order of magnitude, not a figure, because the denominator has not been read.*

**Leak 2 — steady-state localization is not "never at the surface."** SURFY's non-surface training
set comprises proteins localized to endoplasmic reticulum, endosome, Golgi apparatus, lysosome,
mitochondrion, nucleus, peroxisome, cytosol, and multiple locations (PNAS Fig. 1B). **Endosomal and
lysosomal membrane proteins traverse the plasma membrane as part of their transport cycle** — that
is their mechanism, not an exception to it.

**Leak 3 — the training labels encode normal conditions.** SURFY was trained on experimentally
verified high-confidence cell-surface proteins from the Cell Surface Protein Atlas, a
mass-spectrometry resource built from cultured human cell types. **A protein reaching the surface
only under disease conditions is labelled non-surface by construction.**

---

## ⚠ Why this is more than a caveat: the exclusion is anti-correlated with what ADCs want

**Condition-dependent surface trafficking is not a defect in a target — it is the selectivity
property an ADC exists to exploit.** Intracellular in normal tissue, surface-exposed in tumour, is a
*better* therapeutic window than surface-everywhere; on-target/off-tumour toxicity is the field's
central problem and this class is the structural answer to it.

**So the classifier that makes the census tractable may exclude, by construction, the class with the
strongest theoretical window.**

---

## The same shape a third time, and that is itself the finding

| Instance | The filter | What it excluded |
|---|---|---|
| **F-009** | Kathad's expression-and-selectivity filter | Trop-2, CD33, CD30, CEACAM5 — clinically validated ADC targets |
| **F-011** | SURFY's localization classifier | Potentially the condition-dependent-trafficking class |
| *(pattern)* | — | **The filter that makes a list tractable removes the interesting cases.** |

F-009's resolution applies unchanged: **name the boundary, do not inherit it silently, do not claim
to fill it.** The defensible statement indicts the *classifier's scope*. It does not assert that
this project's scorer recovers anything from the negative class.

---

## ⚠ Citation status, recorded not silent

Leaks 1–3 are sourced from the SURFY resource page and the PNAS abstract and figure legends, read
2026-08-04. The *examples* of condition-dependent surface translocation offered in conversation —
**GRP78/HSPA5, calreticulin, nucleolin, LAMP1** — are **Planner-supplied from general knowledge and
have NOT been opened at first hand.** Recorded as leads, not evidence, under the convention
`data/adc_reference_mapping.csv` uses. **None may reach a surface, a deck, or a paper until its
primary source is opened.** The finding stands without them.

⟡ **And the entry names its own weakest point:** this finding argues that an upstream model's
negative class should not be inherited as fact — while itself resting, for its magnitudes, on that
model's paper rather than its data. **That is not fatal to the argument and it is not hidden.** It
is discharged by Task A, and until then every magnitude here carries the label above.

---

## What this rules — nothing. What it changes — the ingest.

- ✅ **Ingest the full membraneome table, not the positive subset.** SURFY score and positive-class
  membership travel as columns. Costs nothing; keeps the question open.
- ✅ **The negative class is a labelled annex** — retained, flagged.
- ❌ **Annex members are NOT census members and are NOT ranked.** Each would need per-target
  surface-localization evidence, which does not exist here.
- ❌ **No claim that this project's method recovers them.** F-009's over-claim guard, verbatim.

- **Deep-learning justification.** The census universe is defined by *another team's classifier*,
  and this project was about to consume its output as ground truth. Every discipline this log
  applies to ESMFold's pLDDT — a model output used as signal, confounds named — applies to SURFY's
  score. **An upstream model's negative class is a prediction, not a fact.** Treating it as fact
  would be the pLDDT error one layer up the stack.

- **Consequences.** ⟡ Registers as **A-014** — *reserved in `RESERVED.md`, unwritten until KEEL-4
  lands against v6.* Feeds candidate paper **P-002**. Changes census ingest scope; changes no
  Phase-1 result, no feature, no route. ⟡ **Magnitudes pending Task A.**
