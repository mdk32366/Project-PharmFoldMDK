# Orders for Code — D-063: the leave-one-out runs first, and a fold that raises is recorded

> **⚠ SUPERSEDED — filed for the record, DO NOT EXECUTE (editorial banner added 2026-07-28).**
> These orders were superseded by `ORDERS-Code-2026-07-28-D-064-label-path` before they were built.
> Their substance shipped across two PRs: the LOO-first reorder + per-fold guard as **D-063 (#88)**,
> and the survivorship table (this doc's Decision 5) as **D-064 Decision (5) (#89)**.
> **This doc's Context and its Decision (4) are REFUTED/VOID:** the run it describes had **zero
> positives (a label-schema bug — D-064)**, not quasi-complete separation, so the λ-degeneracy-under-
> separation finding was struck and must not be cited. The corrected fit has since run once and
> **converged** (`ranking_run` id=2). Kept unedited below this banner as planning provenance.

---


> **⚠ Scope is small and the discipline around it is not.** This PR changes execution order and adds
> per-fold error handling. **It changes no model, no feature, no parameter, and no label.**
> **Base:** `main` @ `eacac0c`.
> **Scope:** `core/scorer.py`, `scripts/fit_scorer.py`, `tests/`, `docs/README.md`, `ARCHITECTURE.md`.
> **NOT in this PR:** `app/`, `ui/`, migrations, `core/features.py`, the label file.
>
> **⚠ THIS PR DOES NOT RUN THE FIT.** The run is a separate owner-authorised action after merge.
> Every test here is fixture work.

---

## 0. The entry

### D-063 — The leave-one-out runs first and independently; a non-convergent fold is recorded, not fatal

- **Date:** 2026-07-28
- **Status:** Proposed → Accepted on merge.
- **Relates:** D-041 (the pre-registered evaluation), D-060 (the operational parameters), D-027
  (null with a reason, never imputed), D-024 (the denominator travels with the claim), F-003
  (n=12, ~1.7 positives per parameter).
- **Corrects:** D-060, which specified a **build** order and never required the pre-registered
  statistic to **execute** independently of the full-data fit.

---

**Context — what the single authorised run produced.** `fit_scorer.py --run --persist` executed once
against 12 curated labels and 56 rankable folds. It raised:

```
ScorerNonConvergence: IRLS Hessian became singular at iteration 39 (lam=0.001)
  raised at core/scorer.py:422 — run_scorer → irls_fit (the FULL-DATA fit)
  core/scorer.py:425 — leave_one_out(...) — NEVER REACHED
```

**Prod remained clean:** `target_scores` 0 rows, `ranking_results` 0 rows, `ranking_runs.scorer_version`
empty. The raise occurred before any persist, so **no partial scientific artefact exists.** That is
the atomicity behaving correctly and it is worth stating.

**⚠ The raise itself is correct behaviour, verified, not assumed.** `irls_fit` adds `λ` to the six
coefficient diagonals and leaves the intercept unpenalized (`penalty = [0.0] + [1.0]*6`). Under
quasi-complete separation the IRLS weights `w = p(1−p) → 0`, so `XᵀWX → 0`; the six penalized
directions stay pinned at `λ > 0` and remain invertible, while **the unpenalized intercept diagonal
collapses to zero and the Hessian goes singular in exactly that one direction.** The MLE intercept
is genuinely at ±∞ under separation. **This is not a bug, and D-060 decision 1 built the raise so it
would surface rather than emit a silent estimate.**

---

#### Finding (1) — an ordering defect that couples the pre-registered result to a convenience fit

The full-data fit exists to score all 56 targets for the **ranking table**. **It is not the
pre-registered evaluation.** D-041 decision 3 fixes the reported object as *the distribution of
held-out percentiles across leave-one-out folds* — computed from **per-fold** models, which do not
depend on the full-data fit at all.

Ordering the full-data fit first made a **non-pre-registered convenience computation a hard
precondition for the pre-registered result.** A failure whose geometry was *expected* (F-003
Finding 8) therefore blocked the evaluation that did not depend on it.

**⚠ This is a Planner defect, recorded as one.** D-060 §2 listed a build order — *"the LOO loop
with nested CV"* after *"standardize → IRLS fit → predict"* — and never stated that the LOO must be
**executable independently**. The Builder implemented the orders as written. **A build order is not
an execution-dependency specification, and the orders conflated them.**

#### Decision (1) — the leave-one-out runs FIRST, and the full-data fit cannot abort it

`run_scorer` executes in this order, and no earlier step may be made conditional on a later one:

1. **Leave-one-out over the labelled positives** → the pre-registered distribution.
2. **The head-to-head** against the comparator, on the common reference set (D-060 decision 8).
3. **The full-data fit**, attempted last, **inside its own error boundary.**
4. **Persist** everything that was computed, whatever failed.

**A full-data non-convergence records a status and does not raise out of `run_scorer`.**

#### Decision (2) — a fold that raises produces no percentile; the distribution is over the folds that converged

D-041 and D-060 fixed the statistic and never said what happens when a **fold** fails to converge.
**Fixed here:**

- A non-convergent fold contributes **no percentile**. **It is never imputed** and never replaced by
  a neighbouring fold's value — D-027's null-with-a-reason, applied one layer down.
- **The reported distribution is over converged folds only**, and is reported **with the
  non-convergent count and the named held-out targets alongside it, always** — D-024's denominator
  discipline.
- **If every fold raises, there is no distribution**, and that is the reported result. It is not an
  error state and it is not a null result in D-041's sense — see decision (5).

**Why not all-or-nothing.** Discarding eleven converged folds because one failed destroys
information and would be chosen for exactly the reason it should not be: it produces a cleaner
sentence. **The partial distribution with its denominator stated is both more informative and more
honest.**

#### Decision (3) — ⚠ the provenance of decision (2), stated precisely because it was made late

**Decision (2) was made AFTER observing that the full-data fit raised at λ=0.001, and BEFORE
observing any leave-one-out fold outcome.**

This is recorded exactly rather than glossed, because a parameter fixed after seeing part of a
result is weaker than one fixed before seeing any of it, and **the difference must be visible to a
reader rather than inferred.** What was known at decision time: the geometry separates and the
full-data fit will not converge at the CV-selected λ. What was **not** known: whether any fold
converges, how many, or what any percentile is.

**No fold outcome informed this ruling. The ruling is dated before the run that produces them.**

#### Decision (4) — λ selection is degenerate under separation, and that is why the grid is NOT extended

The inner CV selected the grid's **low edge, λ=0.001**. D-060 decision 3 pre-registered that a
grid-edge selection is *"a finding to report — it means the grid was wrong"* and must not be fixed
by extending the grid.

**There is now an independent technical reason, and it points the same way.** Under quasi-complete
separation the least-regularized model also predicts the inner held-out folds near-perfectly, so it
maximises inner-CV log-likelihood **by construction**. **λ selection is degenerate whenever the data
separates, and it will select the low edge every time.** Extending the grid downward would therefore
make the situation *worse*, not better — it would select a still-smaller λ and separate harder.

**This converts "we did not tune" from a discipline claim into a technical one**, and both are now
on the record dated before any fold outcome exists.

#### Decision (5) — ⚠ which pre-registered statistics survive a full-data non-convergence, and which do not

Stated now so no one has to work it out from a half-populated result:

| Statistic | Depends on | Survives full-data raise? |
|---|---|---|
| **LOO percentile distribution** (D-041 dec. 3) | per-fold models | **YES** |
| **Head-to-head vs comparator** (D-041 dec. 3) | per-fold percentiles + evidence scores | **YES** |
| **Spearman vs evidence score** (D-041 dec. 4) | **full-data per-target scores** | **NO — blocked** |
| **Ranking table** (UI Plan v2 §6) | **full-data per-target scores** | **NO — blocked** |

So a full-data raise yields a **partial pre-registered result: one of D-041's two negative-outcome
tests is computable and the other is not.** That is the honest description and it must be the one
used. **The blocked half is reported as blocked, with the reason, not omitted.**

#### Decision (6) — what stays refused

Both are model changes after seeing a result, and both are more tempting now than before the run:

- **The intercept is NOT penalized.** Penalizing it would make the Hessian invertible and produce a
  converged fit — by changing the model after observing its failure. The unpenalized intercept is
  standard and was in place before any result existed.
- **The λ grid is NOT extended, in either direction** (D-060 dec. 3, and decision (4) above).

**Neither is a close call. Both are recorded because they are the two available fixes, and a reader
should see that they were considered and refused rather than never noticed.**

---

- **Deep-learning justification.** D-041's argument is that the small model's value lies in
  producing a falsifiable result at n≈12. **This entry is what makes the falsification reachable:**
  without it, an expected geometric failure in a computation D-041 never pre-registered silently
  suppresses the statistic D-041 did. The pre-registration is only meaningful if the pre-registered
  quantity can execute.

- **Consequences / test surface (written before the code, project rule):**
  - **LOO runs first**, asserted by an injected recorder proving `leave_one_out` is called before
    any full-data fit.
  - **A fixture that forces one fold to raise** — the loop completes, eleven percentiles are
    returned, the non-convergent fold is recorded **by name**, and nothing is imputed.
  - **A fixture that forces every fold to raise** — no distribution, an explicit status, no crash.
  - **A fixture that forces the full-data fit to raise** — the LOO result is still returned and
    still persisted; `spearman` and `scores` are recorded as **blocked with a reason**, not null and
    not zero.
  - **The distribution never appears without its denominator** — the converged-fold count and the
    non-convergent names travel with it in the persisted object.
  - **`ranking_results` carries**: the distribution, converged/non-convergent counts, the named
    non-convergent targets, per-fold λ, the head-to-head with its denominator, the full-data fit
    status, and `scorer_version`.
  - **Unchanged:** six features, seven parameters, the 13-point grid, 5-fold stratified inner CV,
    no RNG, the pLDDT floor. **A test asserting the λ grid is still exactly 13 points from 1e-3 to
    1e3 must remain green.**

---

## 1. Order of work

1. **Land D-063** — own commit, before code.
2. **Tests first, red before green** — the five fixtures above.
3. **`core/scorer.py`** — reorder `run_scorer`; add the per-fold error boundary and the full-data
   error boundary.
4. **`scripts/fit_scorer.py`** — persist the richer result object.
5. **`ARCHITECTURE.md`**, dry-diff, red-then-green audit, full gate, owner merge.

## 2. ⚠ Four things that will bite

1. **Do not run the fit.** Not to test, not to check the fix. Fixtures only. The run is
   owner-authorised, after merge, once.
2. **Do not change the model to make it converge.** No intercept penalty, no grid change, no feature
   drop, no target removal. If the fix seems to require one, **stop and report** — that is a finding,
   not an implementation detail.
3. **Do not impute a missing fold's percentile.** Not with a mean, not with a neighbour, not with
   the full-data value. D-027's rule, one layer down.
4. **A partial result must persist.** The failure mode to avoid is an all-or-nothing write that
   discards eleven converged folds because the twelfth raised.

## 3. What "done" means

`run_scorer` computes the pre-registered LOO distribution and the head-to-head **before** attempting
the full-data fit, records per-fold and full-data convergence status by name, and persists whatever
was computed with every denominator attached. Tests green and provably failable. **No fit run.**

## 4. If something is wrong with these orders

Say so before building — particularly if the persisted result object cannot carry every field in the
test surface, which would be a schema finding and outranks this PR.
