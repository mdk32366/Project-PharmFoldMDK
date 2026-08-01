# Orders for Code — 1.1: the held-out validation set of Kathad-excluded ADC targets (curate now, fold on D-075 survival)

> **⚠ PRIORITY: TIER 1, and GATED.** This order has two phases with a hard gate between them:
> **Phase A (curation) executes now** — it has no fold dependency and no fork dependency.
> **Phase B (fold + validate) does NOT execute until D-075 survives** (Branch A). If D-075 collapses,
> Phase B is abandoned, not deferred — see §0.
> **Scope, Phase A:** `data/heldout_positives.csv` (new), `scripts/curate_heldout.py` (new), `tests/`,
> `docs/README.md`. **Scope, Phase B (later):** the fold pipeline, `core/scorer.py` (read-only use),
> a new validation script, `tests/`.
> **NOT in this PR:** the label file `data/adc_reference_mapping.csv` (the 12 stay the 12), the
> pre-registered fit, `app/`, `ui/`.
>
> **⚠ This does NOT modify F-004, D-041, or the 12-positive training set. It builds an INDEPENDENT
> validation set, used only to TEST generalization — never to train, never to re-rank the cohort.**

---

## 0. ⚠ The gate — read this before anything

**Phase B is gated on D-075 surviving (roadmap Branch A).** The logic is not bureaucratic:

- If D-075 shows the structural axis is confidence-independent and survives attention-matching, then
  testing whether it **generalizes to held-out clinical positives** is the move that turns
  "orthogonal but unproven" into a real result. Phase B is worth folding for.
- If D-075 collapses (signal was pLDDT/attention), the axis does not measure structure, so validating
  its "generalization" is meaningless — you would be measuring the generalization of a confound.
  **Phase B is abandoned.** Phase A's curated list still has value (it documents the comparator's
  false negatives, F-009), but the fold-and-validate work stops.

**So: Phase A runs now regardless. Phase B waits for D-075's result and is authorised only on
survival.** This order is written in full so Phase B is ready the moment the gate opens — but the
Builder does not execute Phase B without explicit owner authorisation citing D-075's survival.

---

## 1. The entry

### D-0NN (or F-009 sub-entry) — An independent held-out validation set: Kathad-excluded, clinically-validated ADC targets

- **Date:** 2026-08-01
- **Status:** Proposed → Accepted on merge. **Phase A only; Phase B gated (§0).**
- **Relates:** **F-009** (the four false negatives this set extends and systematizes); F-004 / D-041
  (the trained model, which this set TESTS and never modifies); the roadmap (Tier 1, Branch A);
  Grok's sinking question (this set is its answer).
- **Confirm the number** against `docs/README.md` — may be a standalone D/F entry or an F-009
  sub-entry; owner's call on merge.

**Context — why this set partially escapes the circularity.** F-004's label is "attempted as ADC,"
which Grok showed is entangled with attention (attention → pLDDT → the label). **The held-out set is
different in kind:** these are clinically-validated ADC targets that Kathad's expression filter
**excluded** — positives the "attention → pLDDT → rank" story does *not* automatically explain,
because the attention-adjacent expression filter *missed* them. If the structural axis enriches on
this set, that is evidence the axis captures something the expression-attention pathway does not.
**This is the independent biological label Grok demanded** ("clinical success, not attempt history").

---

#### Decision (1) — Phase A: the curation (runs now)

Build `data/heldout_positives.csv`: clinically-validated ADC targets **absent from the Kathad 82**.

- **Seed (from F-009, accessions to be verified — see Decision 3):** Trop-2 (TACSTD2), CD30
  (TNFRSF8), CD33 (SIGLEC3, P20138 confirmed), CEACAM5 (P06731 to confirm).
- **Systematic sweep** for the rest: every FDA-approved and phase-2/3 ADC, mapped to its target
  antigen, filtered to those **not in the 82.** Sources: FDA approvals list, ClinicalTrials.gov
  phase-2/3 ADC trials, a recent ADC-landscape review. **Each target: gene symbol, UniProt accession,
  the ADC, furthest clinical status, and the source URL** (D-016: how each is known).
- **Verification is mandatory per row** — accession checked against UniProt, not recalled. The
  project already caught two recall errors this cycle (NECTIN4 score, "first ADC"); this file is
  exactly where that discipline applies.

**Columns:** `gene_symbol, uniprot_accession, adc_name, clinical_status, source_url, verified_date`.

**⚠ Phase A produces a verified list and nothing else.** No folding, no scoring. Its immediate value:
it completes F-009's false-negative census and is inspectable today.

#### Decision (2) — Phase B: fold + validate (GATED on D-075 survival)

When and only when D-075 survives and the owner authorises:

- **Fold each held-out target's ECD** through the existing pipeline — **same sliced-ECD recipe, same
  pLDDT floor, same boundary method** as the 82. Targets needing a different boundary method (whole,
  domain-assembly) carry that method label and the commensurability caveat (Grok's point; the
  held-out-logic doc's four-exit framing applies) — or are held out of the validation comparison for
  the same reason cohort targets are.
- **Score them with the FROZEN F-004 model** (id=2) — **read-only, no refit.** The held-out set is
  scored by the model trained on the 12; it never enters training. This is the definition of a
  held-out test.
- **The validation question:** do the held-out clinical positives score **above the cohort median /
  above matched negatives** on the structural axis? Report the distribution, not a single number.
- **⚠ Interpretation frozen before Phase B runs** (same discipline as D-075):

| Outcome | Reading |
|---|---|
| Held-out positives enrich high on the structural axis | **The axis generalizes to independent clinical positives the expression filter missed.** Branch A's strongest result. |
| Held-out positives score at chance | **The axis does not generalize beyond the training cohort.** A real limit, reported — the axis may be fitting cohort-specific structure, not ADC-suitability. |
| Split / attention-rich subset enriches, others don't | **Reported honestly**, and cross-checked against D-075's attention proxies — if only the attention-rich held-outs (CD30, CD33) enrich, the confound is back and it is said. |

**⚠ The attention trap, restated for Phase B:** CD30 and CD33 are maximally attention-rich (approved
ADCs, CD33 the first ever). If enrichment is driven by *them*, that is the confound, not
generalization. **Phase B must report the held-out result with the attention proxies (D-075 Decision
3) attached per target**, so "generalizes" cannot be claimed on the back of the most-studied targets.

#### Decision (3) — verification discipline (both phases)

- Every accession UniProt-verified, `verified_date` recorded. No recalled identifiers.
- The seed four re-verified even though F-009 lists them — F-009 flagged CD30/CEACAM5/Trop-2 as
  *still to verify.* This order closes that.
- **No over-claim.** This set tests generalization; it does **not** retroactively validate the scorer
  on the cohort, and no artifact may say "our method would have caught these" (F-009 §3).

---

## 2. Order of work

**Phase A (now):**
1. Confirm the entry number.
2. `tests/` red first — the CSV schema, the "all accessions verified" assertion, the "none of these
   is in the 82" assertion (the defining property — a held-out target that IS in the cohort is a bug).
3. `scripts/curate_heldout.py` — the sweep; emits `data/heldout_positives.csv`.
4. Manual verification pass on every accession (owner or Builder, against UniProt).
5. `docs/README.md` entry, dry-diff, gate, owner merge. **Phase A done: a verified list, no folds.**

**Phase B (only on D-075 survival + owner authorisation):**
6. Fold held-out ECDs; score with frozen F-004 model; run the validation with interpretation frozen.
7. Report per-target with attention proxies attached. Land as its own result entry.

## 3. ⚠ Five things that will bite

1. **Do not fold in Phase A.** Phase A is curation only. Folding before D-075 survives is the
   sequencing error the gate exists to prevent.
2. **Do not let a held-out target enter the training set.** The 12 stay the 12. This set is test-only,
   scored by the frozen model. If it ever touches `fit_scorer`'s training path, the validation is void.
3. **Verify every accession.** This file is the recall-error trap; check against UniProt.
4. **Attach attention proxies to the Phase-B result.** "Generalizes" claimed on CD30/CD33 enrichment
   alone is the confound wearing a validation costume.
5. **If D-075 collapses, abandon Phase B — do not soften it into "exploratory."** A validation of a
   confounded axis is not exploratory, it is meaningless. Phase A's list survives as F-009 evidence.

## 4. What "done" means

**Phase A:** a UniProt-verified CSV of Kathad-excluded clinical ADC targets, every row sourced and
dated, asserted disjoint from the 82, gate green. **Phase B:** deferred — ready to execute, not
executed, pending D-075.

## 5. If something is wrong with these orders

Say so before building. Specifically: if the sweep surfaces a target whose cohort membership is
ambiguous (in the 82 under a different symbol), resolve it before it lands; and if D-075's result is
not yet known, **Phase B does not start** — confirm Phase A only.
