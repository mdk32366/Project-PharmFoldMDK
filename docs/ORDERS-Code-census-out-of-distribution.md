# ORDERS — Code — the out-of-distribution measurement that decides whether the census gets a profile at all

**AUTHORED-SHA256** (range: **first `## §` header → EOF**, anchored to line starts, no newline
normalisation) = `a5be2730f985fc2de60b049302e1dd0eff802dfe22836affade1ef3eba2b73b1`
**bytes** = `6720`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE. No landing header.**
>
> ⚠⚠ **READ-ONLY. NO PROFILE IS COMPUTED UNDER THIS ORDER.** The accompanying `D-079` amendment is a
> **pre-registration and is void if code precedes it.** **This order measures whether the amendment's
> ruling 1 or its ruling 3 is the operative one — and both are already committed at equal
> prominence.**
>
> ⚠ Planner grounding `7011e24`. **No GPU, no rental, no fold, no fit, no refit, no new ranking run.**
> **Tranche 5 HELD** (`D-091` r2).

---

## §0 — What this decides, stated before any number exists (`F-022`)

**The standardizer's mean and `sd_k` were fit on 56 cohort targets. The census is 2,690 folded rows
from a surfaceome-wide population.**

⚠⚠ **If the census's feature values fall largely inside the cohort's fit range, a profile is a
defensible extrapolation under the amendment's mount preconditions. If they fall largely outside it,
the honest product is a REFUSAL AT SCALE and the amendment's ruling 1 becomes moot.**

**Both outcomes are pre-registered. Neither is a failure.** ⚠ **A finding that removes a reason to
build is worth as much as one that supplies it.**

⚠⚠ **AND THE PLANNER'S EXPECTATION IS RECORDED SO IT CANNOT BE ADJUSTED AFTERWARDS: I expect
`ecd_length` to be the worst offender and `mean_plddt_ecd` the mildest, and I expect a MINORITY of
the census to be out of range on the strict test. If the result contradicts that, the result stands
and this sentence is the evidence that it was not fitted to.**

---

## §1 — ⚠ Task KA — recover what the cohort's range actually IS

⚠⚠ **`sd_k` is not persisted** (`GE3`), **and computing `sd` over the fit set would be fitting.**
**So the range is characterised from the FIT POPULATION's raw features, not from the standardizer.**

**KA1 — For each of the six `FEATURE_NAMES`, over the 56 scored targets** — read from
`protein_features`, read-only — **report: min · p05 · p25 · median · p75 · p95 · max.**
⚠ **State the key: which 56, which run, which column.**

**KA2 — ⚠ The implied means from `FD1` are a cross-check, and use them as one.** `ecd_length` 413.27 ·
`radius_of_gyration` 0.15600094 · `mean_plddt_ecd` 69.002672 · `membrane_proximal_plddt` 66.002025 ·
`sasa_normalized` 71.020666 · `largest_patch_fraction` 0.73453592.
⚠⚠ **Compare each against the mean you compute directly from `protein_features` over the same 56.**
**They must agree to float precision. Two paths to one quantity, compared on the numbers.**
**If any disagrees, STOP AND REPORT** — it would mean the fit population is not the 56, and every
number in `F-050` would need re-keying.

## §2 — ⚠⚠ Task KB — the census distribution, per feature, against that range

**KB1 — Same six statistics over the census folded set.** ⚠ **State the key and state the
denominator** — **2,690 folded, not 3,467 manifest.** *Three denominators exist and a figure that
does not name which is not a measurement.*

**KB2 — ⚠⚠ THE OUT-OF-RANGE COUNT, AT THREE BARS, NOT ONE.** For each feature, how many census rows
fall outside:
- **the cohort's observed min–max** (the strict test);
- **p05–p95**;
- **±3 standardized units**, ⚠ **computable from the raw range without recovering `sd_k`** — state the
  method you use and why it is not fitting.

⚠ *A single setting is a dial wearing the costume of a measurement.* **`F-043`'s flip rates were
withdrawn the day they were published for exactly this.**

**KB3 — ⚠⚠ REPORT THE UNION, NOT ONLY THE PER-FEATURE COUNTS.** **How many census rows are out of
range on AT LEAST ONE feature, and how many on ALL SIX?** **A profile needs all six; a row failing
one feature fails.** ⚠ **Six per-feature percentages do not tell you the answer and will be misread
as if they did.**

**KB4 — Report the distribution of how many features each row fails**: 0, 1, 2 … 6, summing to 2,690.
⚠ **An empty bucket is printed with its zero.**

## §3 — ⚠ Task KC — the two populations the amendment already names

**KC1 — `F-048`'s 58.** ⚠ **Where do they fall?** **Amendment ruling 6 excludes them at computation,
so this is a check that the exclusion is doing work rather than duplicating `KB`.** ⚠⚠ **If the 58
are already out of range on `ecd_length` alone, ruling 6 and ruling 3 catch the same rows and the
entry should say so rather than imply two independent guards.**

**KC2 — ⚠ The 10 `JA6` rows — PODXL, CSPG5, EDNRB, CXCR5, ATP2B2, SCN9A, SLC26A6, SLC52A3, SLC12A4,
GPR34 — plus PTPRZ1.** **They are folded, have pLDDT, and have no `protein_features` row.** **Report
that as its own category**: ⚠⚠ **`no_features_row` is not `out_of_range` and must never be pooled
with it.** *`F-011` and `F-016` were different mechanisms and were never pooled.*

**KC3 — ⚠ How many of the 2,690 have a complete six-feature row at all?** **Report the shortfall by
cause.** **A profile cannot be computed on a partial vector, and *absent* is a category, never a zero.**

## §4 — ⚠ Task KD — the collision that is live on the surface right now

**`/api/coverage` `coverage.ranked = 67` · `/api/ranking` `n_ranking_set = 56`.** ⚠⚠ **Two live
endpoints, one word, an eleven-row gap, and no statement anywhere of which population either
describes.** **`D-016`: every claim names how it is known. Neither of these does.**

**KD1 — Report the definition of each, quoted from the code that computes it.**
**KD2 — ⚠ This joins `F-049` as a THIRD instance** — after `scorer_version` (same code, not same
parameters) and `run_kind='preregistered'` (carried by two runs). **`F-049` amendment ‹next›; no new
integer. Report the amendment number you take.**

## §5 — ⚠⚠ Task KE — settle `scorer_version` before `F-049` or `F-050` merge

**`/api/ranking` reports `scorer_version 91e646e4a289` for run 2. `F-005` records runs 3 and 4 at
`a927dc4532b7`.** **`F-049`'s whole evidence is one string spanning different parameter counts.**

**KE1 — Is `scorer_version` a STORED COLUMN on `ranking_runs`, or DERIVED AT READ TIME from the
current code?** ⚠⚠ **If derived, then `91e646e4a289` is today's code and the string on ANY historical
run is meaningless — which makes `F-049` stronger and also refutes how it is currently worded.**
**If stored, `F-049` stands as written and the two strings correctly differ.**

⚠ **`F-050` cites run 2. This must be settled before either entry merges.**

## §6 — ⚠ What is NOT ordered

**No profile computed. No standardizer reconstructed — that is fitting.** **No fit, no refit, no
ranking run, no ingest, no migration, no fold, no rental, no credential rotation.**
⚠⚠ **If any question here cannot be answered without fitting or writing, STOP AND REPORT.**

## §7 — Report

⚠ **`KB3`'s union first** — it is the number that decides the amendment.
Then branch and tip · **number and title of every entry landed, in the message that lands it** · the
invariant with its keys tested before any merge · the gate without `.env` sourced.
⚠ **And `F-050`'s two `‹PENDING RE-SEND›` values, restated from
`scripts/fd1_attribution_share.py`** — the Planner will not derive them by subtraction.
