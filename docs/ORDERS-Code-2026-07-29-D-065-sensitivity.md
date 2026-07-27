# Orders for Code — D-065: the pLDDT sensitivity analysis

> **⚠ PRIORITY: this is SECOND. Do not start until D-062 is merged and green.** The pre-registered
> result must be *reported* before any sensitivity analysis runs — D-058 decision 2's condition.
> **Scope:** `core/scorer.py`, `scripts/fit_scorer.py`, `tests/`, `docs/README.md`, `ARCHITECTURE.md`.
> **NOT in this PR:** `app/`, `ui/`, migrations, the label file, `core/features.py`.
>
> **⚠ F-004 IS THE RESULT. Nothing in this PR replaces it, and no run here is a headline.**

---

## 0. The entry

### D-065 — Two pre-specified ablations to test whether the structural signal is carried by pLDDT

- **Date:** 2026-07-29
- **Status:** Proposed → Accepted on merge. **Ruled before either ablation runs.**
- **Relates:** F-004 caveat (b) — the confound this addresses; D-027 (the fixed six, and its
  anticipation of feature-level ablation); D-058 decision 2 (sensitivity analyses are permitted
  *after* the pre-registered result is reported and never replace it); D-041 (the model, unchanged).

**Context — the sharpest open question in F-004.** Two of the six features are pLDDT-derived
(feature 3, mean pLDDT over the folded ECD; feature 4, membrane-proximal pLDDT). **pLDDT is partly a
function of how well-represented a protein's family is in ESMFold's training data**, which tracks
research attention, which tracks having been attempted as an ADC. **So the modest above-chance shift
in F-004 could arise from the network's confidence proxying attention rather than from structure.**

F-004 records this as an **open** confound. It is also **testable**, and leaving a testable confound
untested when the test is one run is not a defensible position.

**D-027 anticipated exactly this**, before any result existed: *"the leave-one-out will show whether
any single feature is load-bearing or whether the set is redundant. Neither outcome invalidates the
pre-registration — both are informative."*

---

#### Decision (1) — exactly two ablations, named now, both reported regardless of outcome

| Set | Features | Parameters |
|---|---|---|
| **`no_plddt`** | 1 (ECD length), 2 (Rg), 5 (SASA), 6 (patch fraction) | 4 + intercept = **5** |
| **`plddt_only`** | 3 (mean pLDDT), 4 (membrane-proximal pLDDT) | 2 + intercept = **3** |

**Both run. Both are reported. Neither is chosen after seeing the other.**

**Why both rather than the complement alone.** `no_plddt` asks *does the shift survive without
pLDDT?* `plddt_only` asks *does pLDDT alone reproduce it?* **Either alone is weak; together they
triangulate.** A shift that survives `no_plddt` **and** is absent in `plddt_only` is strong evidence
against the confound. The reverse is strong evidence for it. Anything else is ambiguous, and that is
a legitimate outcome.

**⚠ No third ablation may be added after seeing these.** Running subsets until one is favourable is
fishing, and it is the specific failure this entry's structure prevents. **A further ablation
requires its own entry, dated after these results.**

#### Decision (2) — everything else is held identical

Same 12 labels · same 56-target ranking set · same 13-point λ grid · same 5-fold stratified inner CV
· same LOO folds · same pLDDT floor of 50 · no RNG · same convergence criterion and raise.
**Only the feature columns change.** A difference in outcome is then attributable to the features
and to nothing else.

#### Decision (3) — ⚠ the interpretation is fixed BEFORE either run

The point of this entry is that the reading cannot be chosen after the numbers arrive.

| Outcome | Reading |
|---|---|
| **`no_plddt` shift ≈ full-model shift, `plddt_only` ≈ chance** | **Confound weakened.** The signal is carried by geometry, not by the network's confidence. Caveat (b) moves from open to tested. |
| **`no_plddt` ≈ chance, `plddt_only` ≈ full-model shift** | **Confound strengthened.** The axis is substantially pLDDT-driven, and the attention pathway is a live explanation. **This would be reported as the finding, prominently.** |
| **Both below the full model** | The six features are **jointly informative**; neither subset carries it alone. Informative about redundancy, silent on the confound. |
| **Both ≈ full model** | The set is **redundant**; the result does not depend on which half is used. Silent on the confound. |
| **Either ablation raises** | Recorded as a raise with its status, per D-063 decision 2. **Fewer parameters make convergence more likely, not less** (5 and 3 parameters against 12 positives, versus 7). |

**"≈" is deliberately not thresholded.** D-041 decision 4 set the precedent: *"No threshold is set
for what counts as 'strong,' deliberately. Setting one now would be arbitrary; setting one later
would be after seeing it."* **The distributions are reported side by side and read in prose against
this table.**

#### Decision (4) — the ablations are structurally prevented from becoming the headline

- **A named set is REQUIRED.** `--ablate` accepts only `no_plddt` or `plddt_only`. **Arbitrary
  feature subsets are refused by the code**, so fishing is prevented by construction rather than by
  discipline.
- Each ablation writes **its own `ranking_run`**, tagged `run_kind='sensitivity'` with the set name.
  **The pre-registered run (id=2) is `run_kind='preregistered'`.**
- **Any surface serving a result must serve the pre-registered run as the result**, and may show
  sensitivity runs only as clearly-labelled sensitivity. **A route that returns the latest run
  regardless of kind is a defect** — D-062's route must filter on `run_kind`, not only validity.
- **F-004 is not amended by these results.** They land in a new finding entry (**F-005**), which
  cites F-004 and does not modify it.

#### Decision (5) — D-027's fixed six is NOT violated

D-027 fixed the count for **the pre-registered model**, and in the same entry anticipated
feature-level ablation as an expected diagnostic. **The pre-registered model remains six features
and seven parameters**, unchanged, already reported.

**The test asserting exactly six features on the pre-registered path must remain green.** If it
reddens, the ablation has leaked into the pre-registered path and the PR is wrong.

- **Deep-learning justification.** F-004's result is bounded by a confound about **what the network's
  own uncertainty is encoding.** pLDDT is a deep-learning output used as signal (D-041 §2 item 3),
  so whether it carries structure or carries training-set representation is a question *about the
  network*, not merely about the features. **This is the most directly deep-learning-relevant
  follow-up available**, and it is one run against an existing pipeline.

- **Consequences / test surface:**
  - `--ablate` **refuses any set not in the named two** — asserted; an arbitrary subset raises.
  - The six-feature assertion on the pre-registered path **stays green**.
  - Feature-count assertions for each ablation: **5 parameters** for `no_plddt`, **3** for
    `plddt_only`.
  - **`run_kind` is persisted** and a sensitivity run is never returned where the pre-registered run
    is expected — asserted with a fixture holding both kinds.
  - The three leakage guards (D-060) **re-assert on the ablation path**: scrambled comparator →
    identical coefficients; held-out features unchanged; λ-selector never sees the held-out index.
    **A narrower feature set does not exempt them.**
  - Determinism holds — same fixture, two runs, byte-identical coefficients.

---

## 1. Order of work

1. **Land D-065.** Own commit, before code.
2. **Tests red first** — the refusal of unnamed sets, the parameter counts, `run_kind` filtering.
3. `core/scorer.py` — accept a named feature set; **the default path is unchanged.**
4. `scripts/fit_scorer.py` — `--ablate {no_plddt,plddt_only}`, persisting `run_kind`.
5. Migration only if `run_kind` needs a column — **additive, zero-row impact on `ranking_runs`
   beyond two existing rows; verify by `information_schema` query.**
6. `ARCHITECTURE.md`, dry-diff, red-then-green audit, full gate, owner merge.

## 2. ⚠ Five things that will bite

1. **Do not re-run the pre-registered fit.** F-004 is recorded. Its numbers are read from the
   persisted row, never recomputed for comparison.
2. **Run each ablation exactly once**, after merge, owner-authorised — same discipline as the
   pre-registered run.
3. **Report both, whichever way they land.** If `plddt_only` reproduces the shift, **that is the
   finding and it goes on screen.** The entry exists so that outcome is as publishable as the
   comfortable one.
4. **Do not add a third ablation.** Not to clarify an ambiguous pair. That is a new entry.
5. **Do not change the model to make an ablation converge.** No intercept penalty, no grid change.
   D-060 decision 3 and D-063's refusals apply unchanged.

## 3. What "done" means

Two named ablations runnable, arbitrary subsets refused by the code, `run_kind` persisted and
filterable, all leakage guards re-asserted on the ablation path, the pre-registered six-feature
assertion still green. **Gate green. No run in this PR.**

## 4. If something is wrong with these orders

Say so before building — particularly if `run_kind` cannot be persisted without a migration the
scope forbids, which would be a schema finding and outranks the PR.
