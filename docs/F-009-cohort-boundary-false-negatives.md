# F-009 — The 82 is the Kathad comparator, not a target census; four clinically-validated ADC targets it excludes (including the target of the first ADC ever)

> **Number — CONFIRMED 2026-08-01** as **F-009** against `docs/README.md` (highest merged finding was
> F-008, the two-precision confound). A finding, not a decision
> — it records a property of the cohort and a checkable list, and reframes an anticipated "gotcha"
> into a supporting data point. **How known (D-016):** cohort membership checked against
> `data/adc_reference_mapping.csv` (CD30/TNFRSF8, CEACAM5, CD33/SIGLEC3 all absent — grep, this
> session); clinical status and accessions confirmed by web search (this session, sources below).

---

## §0 — The question, asked before the room asks it

"You claim to rank ADC targets, but CD30 isn't in your 82 — CD30 has had an ADC (brentuximab
vedotin / Adcetris) since 2011. CEACAM5 isn't there either, and it reached **phase 3** (tusamitamab
ravtansine). And CD33 — the target of **Mylotarg, the first ADC ever approved (2000)** — isn't
there. Isn't your list incomplete?"

Left unstated, this reads as an oversight. Stated first, it is a supporting data point. This entry
records the honest answer.

---

## §1 — The 82 is a comparator cohort, not a census

The research question is *does a structure-derived axis reorder an **expression-based** ranking* —
and the expression-based ranking is **Kathad et al. 2024's.** The 82 is therefore *Kathad's cohort*,
inherited whole so the two rankings are of the same targets and the delta between them is meaningful.
It was never claimed to be "the list of overexpressed proteins" or "all ADC targets." Adding a target
to the fold set without it being in Kathad's ranking would have nothing to compare against — it would
break the comparison, not complete it.

**So "why isn't CD30 in the 82" has a clean answer: because CD30 is not in Kathad's cohort.** The
boundary is a property of the comparator, not of this project's biology judgement.

---

## §2 — Three documented false negatives of the comparator (the finding)

The sharper point: CD30, CEACAM5, **CD33**, and **Trop-2** are all clinically-validated ADC targets
that Kathad's expression-and-selectivity filters **excluded.** Trop-2 was already on record as a
checkable baseline false negative (target of two FDA-approved ADCs, excluded by Kathad's filters).
CD30, CEACAM5, and CD33 now join it:

| Target | Accession | ADC | Furthest status | In Kathad 82? |
|---|---|---|---|---|
| **Trop-2** | (TACSTD2) | sacituzumab govitecan, datopotamab deruxtecan | **FDA-approved** (2 ADCs) | **No** |
| **CD33** | P20138 (SIGLEC3) | gemtuzumab ozogamicin (**Mylotarg**) | **FDA-approved 2000 — the FIRST ADC ever** | **No** |
| **CD30** | TNFRSF8 / P28908 | brentuximab vedotin (Adcetris) | **FDA-approved 2011** (Seagen's first ADC) | **No** |
| **CEACAM5** | P06731 | tusamitamab ravtansine (SAR408701) | **Phase 3** (CARMEN-LC03) | **No** |

Four is a strong pattern. **Expression-and-selectivity filtering drops clinically-validated targets
— including the target of the first ADC ever approved (CD33 / Mylotarg, 2000).** That is a concrete
demonstration that the expression axis is incomplete, and therefore that stress-testing it against a
different axis is worth doing at all. **The false negatives motivate the project; they do not
undermine it.** CD33 is the most rhetorically stark of the four: *the expression cohort excludes the
target of the first ADC.*

**A correction embedded here (D-016), because it is why CD33 matters:** Adcetris (brentuximab
vedotin, 2011) was **Seagen's first ADC**, but **not the first ADC** — that is Mylotarg (gemtuzumab
ozogamicin, CD33, FDA-approved 2000, eleven years earlier). The two claims share the word "first"
and fuse in memory; only "Seagen's first" survives the record. Mylotarg's 2000 approval, 2010
voluntary withdrawal, and 2017 re-approval at lower dose partly erased it from the popular ADC
narrative, which is why "Adcetris was first" is a common slip. **Any deck or talk must not call
Adcetris "the first ADC"** — a pharma-literate audience (exactly whom the Razzak introductions
target) will catch it, and a wrong historical claim in the setup is disproportionately costly for a
project whose credibility rests on how-known discipline. (The staged deck was checked: no "first
ADC" or brand phrasing appears in it — the claim lived only in conversation.)

Sources (this session): CD33/Mylotarg 2000 first-ADC approval and the withdrawal/re-approval history
(Nature Sig Transduct Target Ther 2022; AACR Clin Cancer Res 2018; Knobbe Martens 2026). CD33
accession P20138 / SIGLEC3 (UniProt via Reactome, R&D Systems, multiple). CD30/Adcetris 2011
(Seattle Genetics/Seagen). CEACAM5/tusamitamab ravtansine phase-3 CARMEN-LC03 (NCT04154956; Annals
of Oncology 2022; OncLive 2026; J Thorac Oncol 2025).

---

## §3 — The over-claim to avoid (connects to D-075)

**Do NOT claim "our structural method would have caught CD30/CEACAM5."** Three reasons:
1. They have not been folded or scored — there is no such result.
2. CD30 has a **2011 approval** → maximally attention-rich → its pLDDT would be inflated for exactly
   the reason D-075 interrogates. Using it to validate the scorer would walk straight into the
   confound.
3. The defensible claim indicts the **comparator**, not this project's scorer: *the expression axis
   has documented false negatives, therefore expression alone is insufficient, therefore an orthogonal
   axis is worth measuring.* Keep "the comparator has blind spots" strictly separate from "our scorer
   fills them" — conflating them hands the critic (D-075 / Grok) the next punch.

---

## §4 — The future-work item this surfaces (a possible answer to Grok's sinking question)

A **held-out validation set of known-positive ADC targets that Kathad excluded** (Trop-2, CD30,
CEACAM5, + whatever a systematic sweep of approved/phase-2-3 ADCs finds) would be a materially better
label than "attempted as ADC," because:
- it is closer to **clinical validation** than attempt-history;
- it is a set the expression filter **already failed on**, which partially breaks the
  attention-confound D-075 targets (these are positives the "attention → pLDDT → rank" story does not
  automatically explain, since Kathad's attention-adjacent filter missed them);
- it directly answers Grok's demand for "an independent biological label (clinical success, not
  attempt history) on which the structural ranks enrich beyond expression."

**Recorded as future work, not committed, and explicitly NOT claimed as done.** Building it means a
curation pass (which approved/late-stage ADC targets sit outside Kathad) and folding those ECDs —
scope for after the D-075 ablation, and a natural companion to it.

---

## §5 — Definition of done

- [ ] Number confirmed against `docs/README.md`.
- [ ] The comparator-not-census framing lands in the deck (a line on the cohort/methods slide) and the
      held-out-logic doc, so the "why isn't CD30 here" question is answered before it is asked.
- [ ] The four false negatives recorded with accessions; Trop-2's prior note cross-referenced.
- [ ] **Accessions verified, not recalled:** CD33 = P20138 (confirmed this session, UniProt via
      Reactome/R&D Systems). **Still to verify against UniProt before merge: CD30/TNFRSF8 (P28908?),
      CEACAM5 (P06731?), Trop-2/TACSTD2.** Same discipline that caught the "first ADC" slip — check,
      don't recall.
- [ ] **Deck guard:** no artifact calls Adcetris "the first ADC" (that is Mylotarg, 2000). Deck
      checked clean this session; re-check if the ADC-context slide is edited.
- [ ] The over-claim guard (§3) respected in every artifact — no "we'd have caught them."
- [ ] Held-out-positive label set logged as future work, unbuilt, uncommitted. (CD33's ECD is
      sliceable — Asp18–Gly260 region documented — so it is a viable member if that set is built.)
