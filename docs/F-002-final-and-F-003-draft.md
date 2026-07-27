### F-003 — The Group B curation pass: 12 labels against 22, and what the instrument got wrong

- **Date:** 2026-07-27
- **Type:** Instrument/method finding (`F-NNN`). **Not a decision** — it records what the curation
  produced and what the tooling got wrong. The classification judgements themselves are the owner's
  (D-040 decision 1).
- **How known (D-016), by tier, because the tiers are not equal evidence:**
  1. **Registry pass** — `scripts/curate_group_b.py` against ClinicalTrials.gov, 2026-07-26, all 82
     symbols under UniProt aliases. Output: `data/derived/adc_reference_mapping_REVIEW-2026-07-26.csv`.
  2. **Targeted literature + patent pass** — 2026-07-27, **20 symbols**, one query minimum each,
     sources opened and read.
  3. **Landscape survey** — 2026-07-27, **19 symbols**, checked against ADC clinical-landscape
     reviews enumerating the **>50 antigens** in the **>200-candidate** clinical pipeline.
     **A survey-level negative is weaker evidence than a target-specific one** and is recorded as
     such in the file header.
- **Produces:** `data/adc_reference_mapping.csv` — the labels D-041's fit consumes.

---

#### Finding 1 — 12 label accessions against the paper's 22; the name check passes

Measured by running `core.adc_reference` against the curated file:

```
drug rows loaded ......... 13
group_b drug rows ........ 13
group_b ACCESSIONS ....... 12     <- two ERBB2 drug rows collapse to one label
group_c rows ............. 0      (deferred with reason)
stages: approved 3, clinical 4, preclinical 6
D-040 name check ERBB2/NECTIN4/EGFR present: True
D-040 count check: 12 derived vs 22 published -> -10
```

**⚠ Drugs are not targets.** Two approved ERBB2 ADCs are two rows and **one** label. The fit set
counts accessions, not rows, and an earlier Planner figure of 15 conflated them. Corrected here.

**The −10 gap is a finding, not a discrepancy reconciled away** (D-040 decision 1 pre-registered
exactly this). Candidate explanations, **named and not resolved**:

- **The roster is incomplete by three** — see Finding 6. The count is a floor.
- **The preclinical tail is registry-invisible by construction**, which the 07-26 closeout already
  predicted from PODXL.
- **Our exclusion set may be stricter than theirs.** The paper says 22 targets were "tested as
  ADCs" and does not publish its inclusion rule; this entry's rule excludes radioimmunoconjugates,
  peptide-drug conjugates, naked antibodies and family precedent explicitly.
- **They may hold information not in the public record.**

**No criterion was loosened toward 22.** Doing so would fit the labels to the comparator and
silently pre-decide D-041's result.

#### Finding 2 — the script's `review_as_probable_group_b` routing carried a 27% false-positive rate

**4 of 15 routed positives were wrong**, each falsified by a target-specific search:

| Target | Why it failed | Class |
|---|---|---|
| **SORT1** | TH1902 (sudocetaxel zendusortide) is a **peptide-drug conjugate** | excluded modality |
| **MCOLN1** | zero hits; a lysosomal channel is the wrong compartment for an ADC | no agent |
| **SMO** | small-molecule target; hits were patent boilerplate and a saporin **research reagent** | no agent |
| **FLT1** | icrucumab (IMC-18F1) is a **naked** blocking IgG1 | no payload |

**This is not a defect in the script** — D-057 built it to *gather evidence and refuse to draw the
conclusion*, and it did. **The rate is what "probable" was worth: roughly 4 in 5.** Recorded so the
next runner sizes their review effort against a measured number rather than the word.

**The misses clustered where the biology makes an ADC implausible**, and the owner's domain read
flagged all four before any search ran.

#### Finding 3 — the script's peptide-drug-conjugate exclusion did not fire

SORT1 routed positive because TH1902 is a registry-visible SORT1-targeting conjugate and **the PDC
exclusion never triggered.**

**This is the same defect class as D-057 decision 3** — the `radioimmunoconjugate ⊃ immunoconjugate`
substring bug, which the calibration test caught *before the script ever reached a network*. The
calibration covered the radio case and **not** the peptide case. **A calibration set proves the
cases it contains and nothing else.**

**⚠ Compounding factor, observed in the primary literature:** an OSMR paper describes a **⁶⁷Cu
radioimmunoconjugate** and calls its own construct "the ADC" in the methods. **Exclusion cannot rely
on the source's terminology; the payload must be checked.**

#### Finding 4 — seven contaminant classes, each observed, none hypothetical

1. **Radioimmunoconjugate** — CDCP1's ch10D7-**⁸⁹Zr**; OSMR's ⁶⁷Cu.
2. **Family-member ADC** — NOTCH2←Notch3, EPHA4←EphA2/EphA5, CDH11←P-cadherin, TSPAN15←TSPAN8,
   ITGB5←ITGB6.
3. **Research-reagent conjugate** — FITC/HRP/PE/agarose/saporin catalogue antibodies.
4. **Patent boilerplate** — a generic ADC-embodiment paragraph present in nearly every therapeutic
   antibody patent (LRP6). **The most dangerous, because it reads as a target-specific hit.**
5. **Naked antibody** — PCDH7 (mAb7), ENTPD1 (Phase I blockers), BTN3A3 (ICT01), FLT1 (icrucumab).
6. **Excluded conjugate modality** — SORT1's peptide-drug conjugate.
7. **Lexically similar symbol** — FGFR1 returned on FLT1; SLC34A2 (NaPi2b) returned on SLC3A2.
   **Distinct from (2): not a family member, a look-alike symbol.**

#### Finding 5 — the family-adjacency pattern, and why it makes the silence credible

Four families in the cohort have real ADC programs, **every one against a sibling gene**: EphA2 and
EphA5 but not EphA4; Notch3 but not Notch2; P-cadherin and CDH6 but not CDH11; TSPAN8 but not
TSPAN15; ITGB6 but not ITGB5.

**This is the Kathad cohort's selection method showing through.** Targets were selected on
expression, not ADC precedent — so where a family holds a validated ADC antigen, the cohort often
contains the other member. **It is a structural reason the registry-invisible tail is genuinely
empty rather than merely unsearched**, and it strengthens the negatives rather than weakening them.

#### Finding 6 — ⚠ the roster is incomplete by three, and the file says so

**CXCR5, MSLN and MUC16** were routed probable-positive by the registry pass and were **never
verified** — they fell outside both the 33-row headroom set and the 12-row verification set.

**They are absent from the file because unverified, NOT because negative.** The file's header
carries an explicit carve-out to that effect, because *"absence is a negative"* would otherwise
mislabel three probable positives by omission.

**Consequence: the count of 12 is a floor, not a total.** None of the three is in the ranking set
anyway — CXCR5 is below the pLDDT floor (47.63), MSLN is `held_out`, MUC16 is unfolded — **so the
fit set is unaffected**, but D-040's count check is not final until they are curated.

#### Finding 7 — GRIN1's tooling gap is closed

Its registry pass ran on reduced aliases (a `[NMDA]` bracket-syntax query returning HTTP 400), so
its silence was weaker evidence than its neighbours'. **Closed by a targeted literature pass:** the
GRIN1 literature is entirely neurology — epilepsy variants, stroke neuroprotection, anti-NMDAR
encephalitis autoantibodies. Anti-GluN1 antibodies exist, naked, non-oncology. **No conjugate.**

**A documented tooling defect converted into a documented closed gap**, rather than left as a silent
weakness in one row.

#### Finding 8 — the day's net effect: the fit set did not grow; its composition was corrected

**12 rankable positives before curation, 12 after.** Four removed (SORT1, MCOLN1, SMO, FLT1), four
added (CDCP1, JAG1, UPK1B, CDH11).

**That is the more valuable operation.** Four false positives in a twelve-positive set is **33%
label noise**, and noise in the positive class is precisely what a seven-parameter logistic
regression cannot absorb. **Removing four wrong labels improves the fit more than adding four right
ones would have.**

**⚠ D-041's sizing clause stands and is triggered:** 12 positives against seven parameters is ~1.7
per parameter, versus the ~3 D-041 called *"the upper end of what this labelled set supports."*
**Recorded as a finding, not absorbed.**

---

#### Owner rulings recorded (D-040 decision 1 reserves these; they are transcribed, not made here)

- **A target-specific patent claiming antibodies AND conjugates COUNTS**, even without a named
  clinical agent — applied to **UPK1B** (WO2017112829A1) and **CDH11** (US12522657). **A generic
  ADC-embodiment paragraph inside an antibody patent does NOT** — LRP6.
- **SORT1 is excluded**, resolving the one row where the hand draft and the script disagreed.
  **The hand draft was right.** The disagreement was settled by evidence, not by preference, and
  the instrument defect it exposed is Finding 3.
- **Accepted risk:** citations on **CDCP1** and **JAG1** were opened and verified by the owner;
  the remaining Planner-supplied citations were **not**, and the file header names them. Recorded,
  not silent; amendable.
- **A label cannot be deferred to the reader.** An earlier instruction to "state the disagreement
  and let the user decide" was withdrawn: Group B is the fit's binary target, D-041 pre-registers
  that labels are fixed before fitting, and the loader has no undecided state. **The disagreement is
  recorded here; the label is decided.**

#### Consequences

- **`test_the_committed_scaffold_loads_empty_and_valid` is RED** and must be **rewritten, never
  deleted** — it asserted the scaffold held no roster and fired the moment one landed, which is the
  tripwire working. Replace with a pin on the curated roster: 13 drug rows, 12 label accessions,
  the three named targets present, `group_c() == []`.
- **`application_number` is blank on both ERBB2 rows**, pending openFDA reconciliation (D-029). The
  repo already has that check; run it rather than type the numbers from recall.
- **Group C is absent with reason**, so `group_c()` returns `[]`. D-027's out-of-cohort probe
  (TROP2/HER3/CLDN18.2) additionally requires those targets to be **folded**, and they were never
  enqueued. Deferred with its trigger.
- **`scripts/curate_group_b.py` carries two known gaps** — the PDC exclusion (Finding 3) and the
  bracket-syntax alias failure (Finding 7). Both are cheap fixes and neither is blocking.
- **D-041's intersection requirement is still not discharged.** The labelled ∧ folded ∧ above-floor
  intersection must be **recomputed against this file** before the fit, and that recomputation is
  the recorded one. F-002's provisional figures are superseded by it.

---

### F-002 — Pre-fit cohort measurement: the folded set, the floor cost re-measured, and the four denominators the scorer depends on

- **Date:** 2026-07-27
- **Type:** Instrument/method finding. **Not a decision.**
- **How known (D-016):** `scripts/intersection_check.py` (untracked at time of measurement), run
  2026-07-27 against the live deployment `https://pharmfoldmdk.fly.dev` — `GET /api/analyses` and
  `GET /api/coverage` — joined to `data/derived/adc_reference_mapping_REVIEW-2026-07-26.csv` and
  `data/evidence_scores.csv`. Standard library only, no database credentials.

---

#### Two Planner errors this measurement found, recorded before the numbers because they change how the numbers read

1. **`/api/analyses` is the enqueued set, not the folded set.** `core/enqueue.py` creates a
   `protein_analyses` row at **enqueue** time; the list route returns those rows. A first pass read
   its 80 rows as 80 folds. **The folded count is 79** (`/api/coverage`, the D-038 supplier built to
   be the honest denominator). **80 was never a fold count.**
2. **A failed fold was absorbed into the below-floor bucket.** The script's predicate was
   `plddt is None or plddt < FLOOR`, so IGF2R — `fold_status=failed`, no pLDDT — counted as
   below-floor. **This is the D-043 error class reproduced inside the instrument used to measure
   it:** a failed fold is not an unattempted one, and it is not a low-confidence one either.

**A third, methodological:** the uncorrected pass returned **67**, and D-050 records `CoverageLine`
correctly showing **67 = `ranked ∧ folded`** in the 79-fold era. Two different quantities, identical
value. The collision prompted the check that found a missing `disposition` filter. **A number that
matches one you already trust is the most dangerous kind of wrong.**

#### The partition, which reconciles exactly

```
82  = 67 ranked + 13 held_out + 2 excluded          (/api/coverage)
79 folded     = 67 ranked∧folded + 12 held_out∧folded
 1 failed     = IGF2R  (held_out, rental, whole_sequence_fold)
 2 not_folded = MUC16, FAT2  (excluded, over_local_ceiling)
```

#### Finding 1 — every `ranked` target is folded: 67 of 67

The three gaps sit in `held_out` and `excluded` — partitions that were never entering a ranking.

**⚠ The claim "the fold arc is complete" is NOT supported and was withdrawn before it was spoken.**
The Planner drafted it from `82 − 80 = 2`; the endpoint returned three non-folded targets and the
Builder refused the sentence. **The supported claim is narrower and stronger**, and it is the one
that goes to the demo.

#### Finding 2 — the floor cost, re-measured on the right denominator

D-041 §5 recorded **~24% below pLDDT 50, measured on 42 folds**, never re-measured since.

**IGF2R's `mean_plddt` is null** (measured 2026-07-27), so the failed fold is reported separately
rather than absorbed:

> **12 of 79 = 15.2% below the pLDDT 50 floor, plus 1 failed fold, reported separately.**
> **This supersedes D-041 §5's ~24%.**

**The floor is cheaper than D-041 feared.** Recorded with the same rigour a movement against the
project would get.

#### Finding 3 — the four denominators the scorer depends on

| Quantity | Value | Status |
|---|---|---|
| **Ranking denominator** — folded ∧ `ranked` ∧ pLDDT ≥ 50 | **56** | final |
| **Comparator denominator** (D-059) — evidence score ∧ ranking set | **12** | final |
| Provisional fit set — probable positives ∧ ranking set | 12 | **superseded by F-003** |
| Provisional head-to-head — fit set ∩ comparator | 8 | **superseded by F-003** |

#### Finding 4 — the comparator's covered set is positive-enriched, and this is pre-registered

**8 of 12** scored-and-rankable targets were probable positives (**67%**) against **12 of 56**
across the ranking set (**21%**). Expected — the paper's high-evidence targets are the ones people
built ADCs against — but **every comparator statistic is computed on a small, non-random,
positive-enriched subsample.**

**Recorded before the fit**, so a correlation arriving later reads as anticipated rather than
explained away. D-041 decision 4 already warns that *"a high correlation arrives looking like
validation and is not."*

#### Finding 5 — three positives fall outside the ranking set, for three different reasons

| Target | pLDDT | Mechanism |
|---|---|---|
| **CXCR5** | 47.63 | **below floor** — folded, confidence under 50 |
| **MSLN** | 75.04 | **`held_out`** — whole-method, boundary-method incomparable (D-021 §1a). **A method exclusion, not a quality one.** |
| **MUC16** | — | **not folded** — `over_local_ceiling`, 14,451 aa |

**Three mechanisms, three named targets, none silent.** MSLN is the one worth saying aloud: the
cohort's most-attempted ADC antigen after HER2, folded well, excluded because our boundary method
cannot produce a comparable feature 4 for it.

**⚠ A real question raised and deliberately not resolved:** mesothelin is GPI-anchored, so "whole
sequence" is close to "ECD" and the incomparability argument may not bite for this target.
**Resolving it under deadline, for the one target that would add a valuable positive, would be
fitting the method to the desired outcome.** The principled version — *whole-method targets with no
cytoplasmic domain may be method-comparable* — needs its own entry and its own evidence. **Deferred
with its trigger (D-054 manner), not dismissed.**

#### Consequences

- **Every 42-fold-era statistic is stale**, as is *"79 of 82 with 3 remaining"* and D-041 §5's ~24%.
  Re-derive, never re-hardcode at today's value (D-050).
- **`/api/analyses` must not be used as a fold count anywhere.** `/api/coverage` is the D-038
  supplier for that question.
- **⚠ This measurement does NOT discharge D-041's requirement.** The labelled ∧ folded intersection
  must be **recomputed against `data/adc_reference_mapping.csv`** before the fit. See F-003.
