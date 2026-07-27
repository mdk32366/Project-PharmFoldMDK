### F-005 — The sensitivity analysis: the above-chance signal is carried by ESMFold's confidence, not by the geometry — and the attention explanation is not supported

- **Date:** 2026-07-29
- **Type:** A finding. **Nothing is ruled here.** The reading below follows D-065 decision 3's
  outcome table, which was fixed **before either ablation ran.**
- **⚠ This does NOT replace F-004.** D-058 decision 2 and D-065 decision 4: a sensitivity analysis
  is reported *after* the pre-registered result, presented as sensitivity, and never as the headline.
  **F-004 remains the result. This bounds it.**
- **Cites F-004; does not amend it** (D-065 decision 4).
- **How known (D-016):** two authorised runs of `scripts/fit_scorer.py --run --persist --ablate`,
  one each, after PR #91. Persisted as `ranking_run` **id=3** (`no_plddt`) and **id=4**
  (`plddt_only`), both `run_kind='sensitivity'`, `scorer_version=a927dc4532b7`. **Neither is served
  by `/api/ranking`**, which filters `valid ∧ run_kind='preregistered'` and continues to serve id=2.

---

#### The design held

**Denominators identical across all three runs** (D-065 decision 2): ranking set **56** · positives
**12** · head-to-head **8** · common reference **12**. All three: `loo_status=complete`, **12 of 12
folds converged**, `fulldata_status=converged`. **No raise in either ablation** — expected, since
fewer parameters make convergence more likely, and recorded because D-065 required a raise to be
reported as a finding had one occurred.

| Run | median | mean | ≥0.5 | Spearman | params |
|---|---|---|---|---|---|
| **FULL** (F-004, id=2) | **0.607** | 0.618 | **8/12** | −0.0483 | 7 |
| **`no_plddt`** (id=3) | **0.562** | 0.589 | **6/12** | −0.0483 | 5 |
| **`plddt_only`** (id=4) | **0.679** | 0.629 | **9/12** | **−0.2897** | 3 |

#### Finding (1) — D-065 decision 3, row 2, **first clause fires**

> *"`no_plddt` ≈ chance, `plddt_only` ≈ full-model shift → **the axis is substantially
> pLDDT-driven**."*

**`plddt_only`, on two features and three parameters, matches and slightly exceeds the full model.**
**`no_plddt`, on four features and five parameters, falls to 6 of 12 above chance — exactly even.**

**Two of the six features carry the result. The four geometry features are close to inert.**

This is consistent with predictions D-027 recorded before any data existed: **features 1 and 2 are
collinear by construction** (ECD length and length-normalised radius of gyration), and **feature 6
is the fragile one** (its SASA threshold and contiguity definition were the parameters D-058 had to
fix). A geometry set that contributes little is the anticipated shape, not a surprise.

#### Finding (2) — ⚠ row 2's **second clause is NOT supported**, and this is the substantive result

D-065 decision 3's row 2 continues: *"the attention pathway is a live explanation."* **The one
measurement bearing on that pathway points the other way.**

F-004 caveat (b) named a specific mechanism: pLDDT partly reflects how well-represented a family is
in ESMFold's training data → research attention → having been attempted as an ADC. **If that were
operating, `plddt_only` should align MORE closely with the evidence score**, which is the
project's available proxy for attention-and-precedent.

**It aligns less.** Spearman **−0.2897** for `plddt_only` against **−0.0483** for FULL and
`no_plddt`. Further from zero and in the negative direction — the opposite of what the attention
mechanism predicts.

**The pre-registered reading therefore half-fires**, and is reported as half-firing rather than
forced onto a row. **This is what a fixed outcome table is for:** the mismatch is visible because
the reading was written down before the numbers existed.

**⚠ Bound on this inference.** The evidence score is a weak attention proxy — **two values, twelve
targets** (F-004; D-060 decision 8). *"Not supported"* here means the one available test points
away, **not** that the pathway is excluded.

#### Finding (3) — what is now open, and it is a better question than the one it replaces

**ESMFold's own confidence about a protein predicts whether people have built an ADC against it
better than the geometry ESMFold predicts.** Two candidate explanations, both live, **neither
distinguishable by this design:**

1. **Training-set representation → research attention.** F-004's original confound. **Weakened by
   Finding (2), not eliminated.**
2. **Order versus disorder — a genuine structural mechanism.** pLDDT tracks predicted order;
   disordered regions make poor antibody epitopes; **a well-ordered extracellular domain is a real
   structural argument for antibody accessibility.** On this reading **pLDDT is a legitimate
   feature, not a confound at all** — and D-027's justification for features 3 and 4 as
   *epitope-region pLDDT* is the argument being borne out.

**Distinguishing them requires an instrument this project does not have** — a measure of research
attention independent of the evidence score, or a disorder predictor run independently of ESMFold.
**Named as the open question. Not resolved, and not narrated as if it were.**

#### Finding (4) — ⚠ `plddt_only` beating FULL is unremarkable and must not be over-read

**Three parameters against twelve positives generalises better than seven.** At this n that
ordering is expected and is **not evidence that pLDDT is superior** to the full set. It is evidence
that the geometry features are not adding enough to pay for their parameters **at this cohort size.**

#### Finding (5) — the three models disagree per target while agreeing on one coarse statistic

FULL and `no_plddt` return **identical Spearman to four decimal places (−0.0483)** while producing
substantially different per-target percentiles — NECTIN4 0.848 → 0.634, JAG1 0.580 → 0.830, CD276
0.562 → 0.330.

**Not a coincidence needing explanation, and checked rather than assumed.** Against a two-valued
comparator with six-and-six among the twelve, **Spearman depends only on the rank-sum of the
score-5 group**, so it is quantised in steps of roughly 0.024. Two models can agree on that one
statistic while disagreeing everywhere else — and these do. **`plddt_only`'s −0.2897 confirms the
statistic varies by run** and is not being read from the pre-registered scores.

**The lesson generalises:** a coarse statistic computed against a degenerate comparator can agree
across genuinely different models. **Agreement on it is not agreement between them.**

---

#### Consequences

- **F-004 caveat (b) is now tested rather than open**, and its status changes rather than its text:
  the **specific** attention mechanism it named is **not supported** by the one available test;
  a **new, better-posed** open question replaces it (Finding 3). **F-004 is not amended** — this
  entry is the update, and the ordering of the two entries is the record.
- **⚠ The ranking rendered by `/api/ranking` is substantially a pLDDT-driven ordering.** Any surface
  describing what the score measures must not imply the geometry features are doing the work. **The
  `structural score` definition should be read against this finding before it ships.**
- **The pre-registered result stands unchanged.** Six features, seven parameters, the reported
  distribution, both negative-outcome tests. **No parameter was altered after any result existed,
  and no third ablation was run** (D-065 decision 1).
- **The strongest available follow-up is now clear**, and it is not more parameters: an independent
  attention proxy, or an independent disorder measure, would separate Finding 3's two explanations.
  **That is a next-session arc with its own entry**, and D-041's line still governs — *the honest
  route is more labelled data, not more parameters.*
