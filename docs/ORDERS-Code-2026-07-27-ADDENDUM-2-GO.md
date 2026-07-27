# Orders Addendum 2 — 2026-07-27, GO on D-058, and two traps the measurement exposed

> **START THE D-058 FEATURES PR.** `ORDERS-Code-2026-07-27-D-058-features.md` stands unchanged in
> scope, order, and stop points. This addendum adds two things that pass A–I surfaced, plus one
> one-line measurement.
>
> **Everything in §1 is a correctness requirement, not a preference.** Both traps are the same
> error class the Planner just made twice.

---

## 1. ⚠ The extraction driver will hit a row with no structure

`/api/analyses` returns **80 rows. Only 79 are folds.** `core/enqueue.py` creates a
`protein_analyses` row at **enqueue** time, so a row exists whether or not the fold ever succeeded.

**IGF2R is that row:** `fold_status=failed`, `reason=whole_sequence_fold`, rental tier. It has an
analysis id and no structure behind it.

**So `scripts/extract_features.py` must not assume a row implies a structure.**

- `/api/analyses/{id}/structure` for IGF2R will not return a usable PDB. **Handle it; do not crash
  the batch on it.**
- The row is recorded with **all six features null and `null_reasons` naming the fold failure** —
  D-027's null-with-a-reason, not a skipped row and **never an imputed value.**
- **A failed fold is a distinct state from a low-confidence fold.** D-043 ruled this for coverage;
  it applies identically here. Do not let a missing pLDDT fall into the same bucket as a low one.

**Why this is stated so heavily:** the Planner's own measurement script made exactly this mistake —
its predicate was `plddt is None or plddt < 50`, which silently counted the failed fold as
below-floor. **The instrument reproduced the error class it was measuring.** The extractor is the
same shape and will fail the same way if it is written the same way.

## 2. ⚠ Extract broadly, filter late

**Compute and store features for every folded row — including `held_out` targets.**

The `ranked` / `held_out` / `excluded` partition and the pLDDT floor are **scoring and display
filters, not extraction filters.** They are applied when the fit runs and when the ranking renders,
not when features are computed.

**Why:** a target filtered out at extraction time has no row, and a target with no row cannot be
*reported* as excluded — only be absent. D-024's whole discipline is that an exclusion is visible
and named. MSLN is the live case: a well-folded target (pLDDT 75.04) excluded from the fit for
method reasons, which is a sentence the project intends to say out loud on Wednesday. **It can only
say it if MSLN has a feature row.**

D-027 says the same thing from the other direction: Group C runs through the **identical**
extractor with no special-casing, *"otherwise the out-of-cohort probe is not a probe."*

**Every feature row carries `boundary_method`** (from the manifest), so feature 4's cross-method
incomparability travels with the data rather than living in someone's memory.

## 3. One measurement, one line

**Report `mean_plddt` for IGF2R from `/api/analyses`.**

If it is null, the corrected floor cost is **12 of 79 = 15.2% below floor, plus 1 failed fold
reported separately.** That number goes into F-002 and supersedes D-041 §5's ~24%. If it is *not*
null, say so — that would mean a failed fold carries a pLDDT, which is its own finding.

---

## 4. Unchanged

- **Do not commit `intersection_check.py`** until the features PR is merged and green.
- **Do not write F-002** — drafted by the Planner, approved by the owner.
- **Do not act on set membership.** Group B classification is the owner's (D-040 decision 1).
- **The pLDDT floor stays at 50.** CXCR5 at 47.63 is the floor working.
- **Do not filter, drop, or special-case MSLN** anywhere in the extractor.

## 5. Priority

§3 is one line and can go in the same breath as anything. **§1 and §2 are requirements on the
features PR itself.** Nothing else here outranks getting migration `0003` applied and the SASA
timing gate measured.
