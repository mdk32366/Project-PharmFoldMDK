# DRAFT — `P-001` results section, 2026-09-15

> ⚠⚠ **DRAFT, companion to `DRAFT-P-001-methods-2026-09-15.md`.** Nothing here is a ruling.
> Written during slice 3's unattended fold.
>
> **Two ordering rules are obeyed throughout and are stated here so a reader can check them:**
> **(1)** `F-004` is **the** result; `F-005` is sensitivity, reported *after* it and never as the
> headline (`D-058` dec 2, `D-065` dec 4). **(2)** `D-041` dec 3 fixes the reported object as *the
> full distribution with median and spread* and **bars a single summary number as the headline.**

---

## R1. The pre-registered result

**One authorised run.** `ranking_run` id=2, `scorer_version=91e646e4a289`, 56 `target_scores`.
⚠ **Run exactly once. No re-run, and no parameter changed after the result existed.**

Everything fixed before it ran: six features (`D-027`) · L2 logistic regression, seven parameters
(`D-041`) · 13-point λ grid, 5-fold stratified inner CV, **no RNG** (`D-060`) · pLDDT floor 50 ·
12 curated label accessions (`F-003`) · ranking set **56** · comparator **12** · head-to-head **8**.

⚠ **An earlier run under the `D-064` defect produced a zero-positive label set. That row is retained
and marked invalid, not overwritten** (`D-064` dec 3). The provenance chain is legible rather than
tidy.

### R1.1 The object: the leave-one-out percentile distribution

`loo_status = complete`. **12 of 12 folds converged.** No non-convergent targets.

| target | percentile | | target | percentile |
|---|---|---|---|---|
| EGFR | 0.955 | | SLC3A2 | 0.634 |
| CDCP1 | 0.902 | | JAG1 | 0.580 |
| ERBB2 | 0.866 | | CD276 | 0.562 |
| NECTIN4 | 0.848 | | CDH11 | 0.384 |
| MERTK | 0.812 | | FGFR3 | 0.384 |
| | | | UPK1B | 0.312 |
| | | | SLC39A6 | 0.170 |

**Median 0.607 · mean 0.617 · 8 of 12 above 0.5**, against a null expectation of 0.5.
**A modest upward shift.**

⚠⚠ **No significance test was pre-registered and none is computed.** At n = 12 one would be
underpowered, and **choosing a test after seeing the distribution is precisely the degree of freedom
pre-registration exists to remove.** The distribution is the object; the median is not the headline.

### R1.2 First pre-registered negative outcome — **FIRES**

On the 8 held-out positives carrying an evidence score, within the common reference set of 12:

| | structural | comparator |
|---|---|---|
| mean | **0.573** | **0.5625** |
| median | **0.625** | **0.750** |

**Not distinguishable — and the direction reverses between mean and median.**

⚠ That reversal is the cleanest available statement of the finding: *which axis looks better depends
on which summary you choose*, which is what **not distinguishable** means at this size. `D-041`'s
own words for this case: *"the structural axis adds nothing measurable at this cohort size. That is
the result."*

⚠⚠ **The comparator's degeneracy was predicted and it held.** The evidence percentiles returned
**exactly two values, 0.75 and 0.25**, because the published evidence score takes only two values
(nine 4s and eight 5s across 17 targets). `D-060` dec 8 recorded this **before any number existed**,
and it bounds what this comparison could ever have shown **in either direction**.

### R1.3 Second pre-registered negative outcome — **DOES NOT FIRE**

**Spearman(structural, evidence) = −0.0483 over N = 12.**

`D-015` §3 pre-registered that a *strong* correlation would **also** be a null — it would mean the
features proxy attention-and-precedent rather than measuring structure. **Near-zero says they do
not.**

### R1.4 The finding is the two together

> **The structural score ranks attempted-ADC targets modestly above chance, is not distinguishable
> from an expression-and-attention comparator, and is not a proxy for it. At twelve positives the
> axis measures something different and cannot be shown to add anything.**

⚠ That combination is more informative than either null alone. **Orthogonal but unproven** is a
different result from *"the features just re-learned the comparator"* — **and the second was the
more likely prior.**

---

## R2. Sensitivity — which features carry it

⚠ **Reported after `F-004`, presented as sensitivity, never as the headline.** Two authorised
ablations, `ranking_run` id=3 and id=4, `run_kind='sensitivity'`. ⚠ **Neither is served** —
`/api/ranking` filters `valid ∧ run_kind='preregistered'` and continues to serve id=2.

**Denominators identical across all three runs** (`D-065` dec 2): ranking set 56 · positives 12 ·
head-to-head 8 · common reference 12. All three `loo_status=complete`, 12 of 12 folds converged.

| run | median | mean | ≥ 0.5 | Spearman | params |
|---|---|---|---|---|---|
| **FULL** (`F-004`, id=2) | **0.607** | 0.618 | **8/12** | −0.0483 | 7 |
| `no_plddt` (id=3) | 0.562 | 0.589 | 6/12 | −0.0483 | 5 |
| `plddt_only` (id=4) | **0.679** | 0.629 | **9/12** | **−0.2897** | 3 |

### R2.1 The axis is substantially pLDDT-driven

`plddt_only`, on **two features and three parameters**, matches and slightly exceeds the full model.
`no_plddt`, on four features and five parameters, falls to **6 of 12 — exactly even**.
**Two of the six features carry the result; the four geometry features are close to inert.**

⚠ This is the *anticipated* shape, not a surprise: `D-027` recorded before any data existed that
features 1 and 2 are **collinear by construction** (ECD length and length-normalised radius of
gyration) and that feature 6 is the fragile one.

### R2.2 ⚠⚠ And the attention explanation is NOT supported — the substantive part

The pre-registered outcome table continued: *"the attention pathway is a live explanation."*
**The one measurement bearing on that pathway points the other way.**

`F-004`'s caveat (b) named a specific mechanism: pLDDT partly reflects training-set representation →
research attention → having been attempted as an ADC. **If that were operating, `plddt_only` should
align MORE closely with the evidence score.** It aligns **less**: Spearman **−0.2897** against
**−0.0483** for both FULL and `no_plddt` — further from zero, and in the **negative** direction,
the opposite of what the attention mechanism predicts.

---

## R3. The attention control

Three frozen proxies, each run separately, **each confirmed byte-identical on re-run**. Triples and
the arm-by-arm reading are in **methods §3**; the result is stated here.

**The structural enrichment survives popularity-matching on all three proxies.** `pdb_present` moves
toward the anchor on **all three** statistics (10-of-12 on the count). The two PubMed arms disagree
by 2-of-12.

⚠⚠ **The ruling is QUALIFIED and the qualification is not a footnote.** The disagreement is a
finding about **the proxy's construction**, not an objection to the call — and because the mechanism
that would have said which arm is conservative was **refuted before the freeze** (rho = +0.026),
**the disagreement's sign carries no warrant.** `Decision 0`'s fragility properties travel with
every cell.

⚠ **And the `pub_count_atm` arm is *mixed* in a specific, measured sense** (methods §3.1): of its
three margins against the `no_plddt` baseline, **only one is resolvable** — the median, **6.0 × the
median's own 1/224 increment, below**. The mean's margin is **0.34 of a single target's percentile
step** and the count's is **one rank step**. ⚠⚠ **Two of the three are at or under the instrument's
resolution**, so the arm must not be scored by counting how many statistics point which way.

---

## R4. What the three results establish together

| | |
|---|---|
| `F-004` | modestly above chance · not distinguishable from the comparator · **not a proxy for it** |
| `F-005` | the signal is **pLDDT-carried**, the geometry near-inert, **and the attention explanation is unsupported** |
| `F-072` | the enrichment **survives popularity-matching** on all three frozen proxies |

> **Branch A — a structure-derived axis for ADC target prioritization is orthogonal to expression
> and robust to confidence confounds.** Ruled by the owner, 2026-09-12.

⚠ **Both branches were pre-committed at equal prominence** (`D-075` dec 4) and Branch B is retained
in the register as written — *"predicted-structure confidence confounds structure-based target
prioritization: a cautionary analysis."* ⚠⚠ **Which branch was pre-committed is part of the
evidence that the ruling is a reading rather than a rationalisation**, and the paper keeps both
visible for that reason.

---

## R5. ⚠⚠ What is NOT claimed — the over-claim guard

**`F-009`'s guard is `P-001`'s and it binds:**

> ***The comparator has blind spots*** stays **strictly separate from** ***our scorer fills them.***

Four clinically-validated ADC targets sit **outside** Kathad's 82 — that is what motivates the
project, and it is a property of **the comparator**. It is **not** evidence that this axis would
have found them. The paper states the first and does not imply the second.

Also not claimed:

- ⚠ **No calibrated probability.** `F-006`: the fitted scores are **compressed toward the base
  rate** and are not calibrated probabilities. Ranks, never risks.
- ⚠ **No added value over the comparator.** At n = 12 the axis **cannot be shown to add anything**;
  R1.2 is a null and is reported as one.
- ⚠ **No significance claim.** None pre-registered, none computed — see R1.1.
- ⚠ **No commensurability claim.** Methods §7: `P-001` amendment 2 returned the **third** outcome,
  `underpowered` at n = 4. **Still the owner's ruling.**

---

## R6. ⚠ Reader's route to the raw objects

Every number above is served or committed, and none is recomputed for the paper:

- `ranking_run` **id=2** — the pre-registered result, `run_kind='preregistered'`, **never
  recomputed**, read from its row (`D-062`).
- ids **3 / 4** — the ablations, `run_kind='sensitivity'`, **not served**.
- `data/attention_proxies.json` — the Run B proxies, frozen 2026-09-12.
- ⚠ `ranking_results` **id=1** — retained and marked **invalid** (the `D-064` defect). Kept so the
  provenance chain is legible.
