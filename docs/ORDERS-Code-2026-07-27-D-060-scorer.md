# Orders for Code — the scorer: D-060, then `core/scorer.py`

> **⚠ PRIORITY: this is SECOND.** Do not start until the D-058 features PR is merged and green.
> **Base:** `main`, after D-058.
> **Scope:** `core/scorer.py`, `scripts/fit_scorer.py`, `tests/`, `docs/README.md`, `ARCHITECTURE.md`.
> **NOT in this PR:** `app/`, `ui/`, the Dockerfile, `requirements*.txt`, `requirements*.lock`.
>
> **⚠ THIS PR DOES NOT RUN THE FIT.** It ships a tested scorer and a driver. The fit itself is a
> separate, owner-authorised run against the owner's curated labels, which do not exist yet.
> **Every test in this PR is fixture work and needs no real label.** If you find yourself reading
> `data/adc_reference_mapping.csv`, stop.

---

## 0. The entry — land this before any code

### D-060 — The scorer's remaining free parameters, fixed before the fit

- **Date:** 2026-07-27
- **Status:** Proposed → Accepted on merge. **Ruled before any fitting code exists and before the
  labels are curated** (D-015 §3's pre-registration discipline).
- **Discharges:** the operational choices D-041 delegated. D-041 fixed the architecture, the loss,
  the regularizer, the evaluation statistic and both negative outcomes. **It did not fix the
  optimizer, the λ grid, the inner-CV shape, the percentile's reference set, or tie handling** —
  and the reported result is sensitive to all five. Left open, they get chosen after seeing the
  leave-one-out distribution, which is what pre-registration exists to prevent.

**Context — what F-002 changed.** D-041 was written when the ranking set and the folded set were
not yet distinguished, and when the labelled∧folded intersection was unknown. F-002 measured both:
the ranking set is **56** (`folded ∧ ranked ∧ pLDDT ≥ 50`), the provisional fit set is **12**, and
the head-to-head denominator is **8**. Two of the decisions below exist because those numbers are
now known.

**Decision (1) — Optimizer: Newton–Raphson (IRLS) on the L2-penalized log-likelihood, pure Python.**
The penalized objective is strictly convex, so Newton converges; a step-halving guard handles the
early iterations. **Convergence criterion: maximum absolute coefficient change < 1e-8, or 100
iterations.** ⚠ **Non-convergence raises. It never returns a silent estimate.** A quietly
unconverged fit is a result that looks like a result.

**Decision (2) — No RNG anywhere in the scorer.** Fold assignment is deterministic: targets sorted
by symbol, assigned round-robin within stratum. **This is stronger than D-041's "deterministic given
a fixed seed"** and deliberately so — a seed-dependent result can move silently when a seed changes
for an unrelated reason. **Determinism here is structural, and a test asserts no `random` import.**

**Decision (3) — The λ grid is fixed: 13 log-spaced points from 1e-3 to 1e3.** Pinned by a test.
**Not widened, shifted, or re-centred after any fit.** If the selected λ lands at a grid edge, that
is a **finding to report** — it means the grid was wrong — and it is reported, not silently fixed by
extending the grid.

**Decision (4) — Inner CV: 5-fold, stratified on the label, on the LOO training remainder only.**
If the remainder holds fewer than 5 positives, fall back to leave-one-positive-out inner CV and
**record which was used in the run's provenance.** At 12 positives the remainder is 11, so 5-fold
holds — but the fallback is specified now rather than improvised if curation moves the count.

**Decision (5) — The percentile's reference set is the ranking set (56), not "the folded cohort."**
D-041 said *"rank percentile among the folded cohort"* when the two were not distinguished.
**Ranking claims are made on `ranked ∧ folded ∧ pLDDT ≥ 50` (D-041 §5, D-021, F-002)**, so that is
the reference set. Recorded as a clarification of D-041, not a change to it.

**Decision (6) — Ties take average rank.** Stated because it is load-bearing — see (8).

**Decision (7) — The score is the fitted model's predicted probability**, ranked descending.

**Decision (8) — ⚠ The head-to-head is computed on a common reference set, and the comparator is
two-valued.**

Measured 2026-07-27 from `data/evidence_scores.csv`: the evidence score takes **exactly two
values across all 17 targets** — nine 4s and eight 5s — and **six 4s and six 5s** among the 12 that
fall in the ranking set. **The comparator is not a ranking. It is a two-tier grouping.**

Two consequences, both fixed here:

- **Both percentiles in the head-to-head are computed within the same reference set** — the 12
  targets carrying a structural score *and* an evidence score — over the 8 held-out positives in
  that set. A structural percentile computed among 56 and an evidence percentile computed among 12
  are not comparable quantities, and comparing them would be a bug that reads as a result.
  **The primary structural distribution (reported as the headline) is separately computed on the
  full ranking set of 56. Two statistics, both reported, never conflated.**
- **⚠ The comparator's percentile distribution is degenerate by construction.** With two values and
  average-rank ties, every held-out positive receives one of two percentiles. **D-041's first
  negative outcome — "not distinguishable from the comparator" — must be read against a comparator
  that can only sort targets into two bins over twelve targets.** That bound is recorded **before
  the result exists**, so it reads as a property of the source rather than an excuse for an
  outcome. **The pre-registered comparison is unchanged; only its interpretation is bounded.**

- **Deep-learning justification.** Every parameter above, left unfixed, is one that would otherwise
  be chosen after seeing the leave-one-out distribution. D-041's two pre-registered negative
  outcomes are falsifiable only if nothing in the procedure moves once a result exists. **This
  entry is the difference between a pre-registration and the appearance of one.**

- **Consequences / test surface:** each of (1)–(8) pinned by a test; non-convergence raises; no
  `random` import (source assertion, in D-027's feature-count manner); `scorer_version` alongside
  `feature_version`.

---

## 1. ⚠ No third-party math either — same constraint as D-058

**Verified 2026-07-27:** `numpy`, `scipy` and `scikit-learn` are in **neither** `requirements.lock`
**nor** `requirements-dev.lock`. The gate installs `requirements-dev.lock --require-hashes` and
nothing else.

**So the logistic regression is written by hand, in pure standard library.** Everything needed:

- Standardization — mean and standard deviation, training rows only.
- IRLS — reweighted least squares, **7×7** normal equations.
- A linear solver — Gaussian elimination with partial pivoting, ~30 lines.
- Spearman — rank transform with average ties, then Pearson on the ranks.

**The problem is genuinely tiny:** six features, at most 56 rows, seven parameters. A 7×7 solve is
not a numerical challenge. **And it is on-message rather than in spite of the constraint** — D-041's
central argument is that the model's smallness is what makes it defensible. A model small enough to
implement from scratch and read end to end is the strongest version of that claim.

**Do not add a dependency to solve this.** If you believe one is genuinely required, stop and report
— it is an owner decision with a hash-lock regeneration attached, exactly as in D-058 §2.1.

---

## 2. Order of work

1. **Land D-060.** Its own commit, before any code. Log leads code.
2. **`tests/test_scorer.py` — write it and watch it go red.** Red-then-green is mandatory; a test
   that has never failed is not confirmed to bite.
3. **`core/scorer.py`** — standardize → IRLS fit → predict.
4. **The LOO loop with nested CV** for λ.
5. **The four D-041 §5 diagnostics** (see §4).
6. **Spearman** (D-041 decision 4) and the head-to-head (D-060 decision 8).
7. **`scripts/fit_scorer.py`** — reads `protein_features`, reads the labels, fits, writes the
   `ranking_run` and per-target scores plus attributions. **Written, not run.**

---

## 3. ⚠ Six things that will bite

### 3.1 The label and the comparator must stay different quantities — **this is the one that invalidates silently**

**Label = Group B membership. Comparator = the evidence score.** If the evidence score is ever used
as the label, or leaks into the feature matrix, **the comparator predicts the label by construction
and D-041's negative-outcome test goes degenerate** — while producing output that looks entirely
normal.

There is a sharp test for this and it is required: **a fixture where the evidence scores are
scrambled must produce byte-identical coefficients.** If scrambling the comparator changes the fit,
the comparator is in the fit.

### 3.2 Standardization statistics come from the training fold only

Computing mean and standard deviation over all rows leaks the held-out target into its own
evaluation. **Invisible in the output.** Test: change the held-out row's feature value to something
extreme; the fitted coefficients must not move.

### 3.3 λ is selected inside each LOO fold, never on full data

Same leakage class, same invisibility. Test with an injected recording λ-selector: **assert the data
it received never contains the held-out index.**

### 3.4 Perfect separation is likely, and is not a bug

Twelve positives, six features, 56 rows. Quasi-complete separation is a realistic outcome. **L2 keeps
the coefficients finite — that is one of the reasons D-041 chose it.** If the optimizer struggles,
**report it as a finding.** Do not respond by dropping the penalty, adding features, or removing
targets. All three would break D-027's fixed count or D-041's pre-registration.

### 3.5 Below-floor and `held_out` targets are excluded from ranking claims and **reported separately**

Never silently dropped. F-002 named the three live cases — CXCR5 (below floor), MSLN (held out,
pLDDT 75.04), MUC16 (not folded) — **three mechanisms, three names.** The scorer's output carries the
excluded set with its reason, so the surface can render it.

### 3.6 Every reported statistic carries its denominator

The headline distribution is over the ranking set (**56**). The head-to-head is over **12** with
**8** held-out positives. The Spearman is over **12**. **A statistic without its denominator is not
reportable** (D-024, D-041 decision 3's explicit warning about a comparison over a handful).

---

## 4. Test surface — written first, red before green

**The pre-registration, enforced by the gate**
- **Exactly seven parameters** — six coefficients and an intercept. The D-041 analogue of D-027's
  feature-count test.
- **The λ grid is 13 points, 1e-3 to 1e3**, asserted as a named constant.
- **No `random` import** in `core/scorer.py` — source assertion.
- **Inner CV is 5-fold stratified**, with the documented fallback, asserted.

**Leakage — the invisible failures**
- **Scrambling the evidence scores leaves coefficients byte-identical** (§3.1).
- **Changing a held-out row's features leaves coefficients unchanged** (§3.2).
- **The λ selector never receives the held-out index** (§3.3), via an injected recorder.

**Correctness**
- **Determinism** — same fixture, two runs, byte-identical coefficients.
- **A hand-checkable fit** — a tiny separable fixture whose coefficient signs are predictable by
  inspection, asserted by sign and ordering rather than by whatever the code first emitted.
- **Non-convergence raises**, proven with a fixture that will not converge in 100 iterations.
- **Spearman on a hand-computed fixture**, including a tie block, checked against a value computed
  by hand.
- **Average-rank ties** asserted directly.

**Shape of the result**
- **LOO returns a distribution, not a scalar** — a sequence whose length equals the positive count.
- **Percentiles are computed against the ranking set**, asserted with a fixture whose ranking set
  and folded set deliberately differ in size.
- **The head-to-head uses one common reference set** — asserted with a fixture where the two
  reference sets differ, so a naive implementation fails.
- **Excluded targets appear in a separate reported set with reasons**, never absent.

**Fixture discipline**
- **Distinctive values throughout.** No round numbers, no zeros, no repeated values across features.
  A false green in a scorer test is invisible and propagates into the reported result.

**Unchanged guards**
- `test_image_contents.py` passes — no new dependency.
- The D-051 architecture contract test passes — **no route in this PR.**

---

## 5. Before you merge

1. **Dry-diff first.** Report the intended change set before touching the repo.
2. **Red-then-green audit** for every test — what it looked like red, what made it green. A test
   green on first write gets flagged, not accepted.
3. **Full gate green** — pytest, UI vitest, image, postgres.
4. `ARCHITECTURE.md` updated **in this PR**.
5. **Owner authorises the merge.**
6. **Do not run the fit.** Not against real labels, not "just to see." The first fit is an
   owner-authorised run and its output is a recorded result the moment it exists.

---

## 6. What "done" means for this PR

`core/scorer.py` fits, predicts, runs leave-one-out with nested-CV λ selection, computes both
percentile distributions and the Spearman, and reports every statistic with its denominator and
every exclusion with its reason. `scripts/fit_scorer.py` written and able to run end to end against
**fixture** labels. Tests green and provably failable.

**Not in this PR:** the fit, the ranking table, the route.

---

## 7. If something is wrong with these orders

Say so before building. Three specific invitations:

- **If you believe a dependency is genuinely required**, stop and report — owner decision.
- **If the optimizer will not converge on realistic fixtures**, that is a finding, not a failure.
- **If any test in §4 cannot be written as specified**, say which and why. A leakage test that
  cannot be written is a design problem in the scorer, not a reason to skip the test.
