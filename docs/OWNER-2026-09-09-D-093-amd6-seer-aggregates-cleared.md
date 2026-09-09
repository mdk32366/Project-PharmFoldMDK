# OWNER RULING — 2026-09-09 — `D-093` amendment 6's data-vs-text gap is CLOSED, and the NCI email is a scar rather than a gate

- **Ruled by:** Matt, 2026-09-09 ~06:27 PT
- **Recorded by:** the `D-149` cancer-burden BUILD, in the PR that ships the surface
- **Status:** ACCEPTED and acted on. ⚠ This file is the artefact the entry's provenance names
  (D-016). It is a RECORD of a ruling, not a re-derivation of one.

---

## 1. What was held, and by what

`D-093 amendment 6` (2026-08-20) read NCI's reuse policy rather than recalling it, and got the
**first clear licence grant this project has obtained from any supplier**:

> *"Unless otherwise indicated, all text within National Cancer Institute (NCI) products is free of
> copyright and may be reused without our permission. Credit the National Cancer Institute as the
> source."*

It then recorded, honestly and against its own interest, a **narrow but real gap**:

> ⚠ **THE GAP, AND IT IS NARROW BUT REAL. The reuse policy never mentions DATA.** It governs
> *text, graphics, the NCI logo, patient education publications and translations* — an
> **information-products** policy. […] **That the DUA is about patient-record confidentiality
> rather than copyright, and so should not reach aggregate statistics, is an INFERENCE — the page
> does not say it.**

Amendment 6 named the instrument for closing it — `NCIinfo@nih.gov`, one question — and **held the
INGEST-versus-LINK choice for the owner**, explicitly refusing to take it by implementation:

> ⚠⚠ **Choosing between them is a decision about what the layer IS, and it is the owner's.** Code
> will not take it by implementation.

## 2. The ruling

**The gap is CLOSED in favour of Code's own prior language**, which predates amendment 6 and was
written three times in the tree before the gap was ever named:

| Where it was already written | The words |
|---|---|
| `docs/CROSSWALK-2026-08-21-hpa-tumour-to-registry.md:195` | *"SEER is **US Government, public domain**"* |
| `docs/ORDERS-Code-WE1-skin-confirmation-and-SEER-decision-6.md:74` | ⚠⚠ *"Thirteen rows are blocked by nothing but a fetch — **SEER is US Government, public domain**"* |
| `docs/CLOSEOUT-Code-2026-08-21.md:207` | *"⚠ SEER is public domain; nothing stands between them and an incidence figure but decision 6"* |

**Amendment 6's option 1 — INGEST the SEER official aggregates — is TAKEN**, and it is taken
**without waiting on `NCIinfo@nih.gov`**.

- ⚠ **Amendment 6's credit requirement SURVIVES the closure and is still binding.** The gap that
  closes is *does the policy reach DATA*. The obligation the same policy imposes — *"Credit the
  National Cancer Institute as the source"*, plus, for digital reproduction, a link to the original
  product by title — is **not** waived and is a shipped requirement of the surface, asserted by
  test.
- ⚠ **US-only.** Amendment 6 stated of option 1: *"after `NCIinfo@nih.gov` confirms the reuse policy
  reaches SEER data. **US-only.**"* The confirmation clause is what this ruling removes. **The
  US-only clause is not removed** and is carried on every figure and in the API `meta`.

## 3. ⚠⚠ Today's NCI email is a SCAR, and it is explicitly NOT a gate

An email from NCI arrived today, **message id `fcfc41c2`**. The ruling is that it is
**ignored as a gate**: the burden surface does not wait on it, is not conditioned on it, and does
not cite it as authority in either direction.

- ⚠ **It is recorded rather than discarded, and the distinction is the point.** *A deferral that
  leaves no trace reads as an oversight to the next reader* — `D-093 amendment 7`'s shape, which is
  why that amendment exists at all. So the email is named here, with its id, as a **scar**: a thing
  that happened, that bears on the question, and that was ruled non-load-bearing **by the owner and
  not by Code's convenience**.
- ⚠ **This file does not characterise the email's contents.** It was not read by the agent that
  wrote this record, and **summarising an artefact one has not read is the pointer-not-proof shape**
  the method note's item 7 exists about. What is recorded is the ruling *about* it.

## 4. What stays OUT, and it is not a formality

| Held out | Why, and by whose authority |
|---|---|
| **SEER Research Data / Research Plus microdata** | ⚠ **Still controlled, still out.** Amendment 6: *"Each person who will access the data must submit a separate request and acknowledge the data agreements and limitations."* Nothing in this ruling touches the DUA tier. **No case-level SEER data enters this repository.** |
| **GLOBOCAN / IARC** | ⚠ **Still out.** Amendment 6 read IARC's terms and found the opposite answer to NCI's: *"IARC **exercises copyright** over its Materials… **All rights are reserved**"*, three separate written-permission triggers, unilaterally mutable terms (clause 12A) and an indemnification (clause 8). **No GLOBOCAN figure is ingested and none is rendered.** Amendment 6's option 2 (link-only) remains available and is **not** exercised here. |

⚠ **The asymmetry is the finding amendment 6 already recorded, and this ruling does not soften it:**
*a government or intergovernmental publisher does not imply public-domain terms.* **NCI grants and
IARC reserves.** That this ruling clears NCI is not an argument that clears IARC, and the two must
not be cited together as though one licence review covered both.

## 5. What this ruling does NOT authorise

Recorded so the clearance is not read wider than it is:

- **No `structural_score` change**, and **no join** between a burden figure and any ranking,
  score or rank surface. Burden is a property of a **disease**; `D-093` decision 1 attaches it by
  **traversal**, never as a protein-level column, and `tests/test_clinical_layer_prohibitions.py`
  already forbids the column.
- **No protein-level burden column**, and no claim that a protein card gained incidence.
- **No new supplier.** TCGA/GDC and CPTAC remain unread for this purpose and — per amendment 6 —
  **cannot populate a burden tuple at all**, being case series rather than registers.
