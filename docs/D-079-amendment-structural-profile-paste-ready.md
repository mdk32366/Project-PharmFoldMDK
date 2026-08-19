# PASTE-READY — `D-079` amendment — for `docs/README.md`

**AUTHORED-SHA256** (range: **first `####` header → EOF**, anchored to line starts, no newline
normalisation) = `bb6dcbee929cc70f318ee19a2d5f1d71a4dd2ebecbb3a274923e54d55f68bd1c`
**bytes** = `6641`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE. No landing header.**
>
> ⚠⚠ **AMENDMENT NUMBER UNKNOWN TO THE PLANNER.** `D-079` already carries at least
> `AMENDMENT-2026-08-05-D-079-census-key.md`. **Code determines the next amendment number from the
> live entry and states it in the message that lands it.** ⚠ **Do not assume 1.** *A number assigned
> before its content is checked is `F-044`.*
>
> ⚠ Sub-entry — **no integer.** Placed at the end of `D-079`'s body, before the next `###`.
> **Test the invariant from the SET before merging.**

---

#### D-079 amendment ‹N› — ⚠⚠ The census may carry a STRUCTURAL PROFILE, which is not a score, is never ranked, and is REFUSED where the standardizer is out of range

- **Date:** 2026-08-19 · **Status:** ⚠⚠ **PRE-REGISTRATION. Void if code precedes it.** `D-079`'s own
  clause, inherited deliberately. **No census profile is computed before this entry is ruled.**
- **Amends:** `D-079`'s bar on scoring census rows, which `D-089` cites as *"`D-079` bars scoring any
  census row."* ⚠ **The bar is NARROWED, not lifted.**
- **Owner ruling, 2026-08-19:** the census should carry a structure-derived value. **This entry rules
  what that value may be and what it may never become.**

---

**⚠⚠ WHY THE BAR EXISTED, RESTATED SO NARROWING IT IS A DECISION AND NOT AN EROSION.**

`D-079`'s title is *"…and spend none of the pre-registration on it."* **`P-001` asks whether a
structure-derived ranking reorders an expression-derived one, on the 82.** ⚠⚠ **If census values are
ever compared back into that question — or if the scorer is refit to behave better on the census —
the comparison is contaminated and `P-001` is unanswerable.** **Ruling 5 is the wall.**

---

**RULING 1 — ⚠⚠ IT IS NOT CALLED A SCORE, AND THE NAME IS THE RULING.**
The census value is **`structural_profile`**. **Never `score`. Never `rank`. Never `suitability`.**
⚠ **`D-068`'s discipline is that a number carries its status; `F-049`'s family is a word meaning two
things on two surfaces, and it bit three times on 2026-08-19** — `scorer_version`, `run_kind`, and
`ranked` at **67 on `/api/coverage` against 56 on `/api/ranking`.** **A fourth is not acceptable.**

**RULING 2 — ⚠⚠ NO RANKING, ANYWHERE, INCLUDING BY SORT ORDER.**
**A value is a measurement; a rank is a recommendation.** ⚠ **The census has no labels, so nothing
justifies one.** **No `rank` column, no default sort by profile, no "top N".** ⚠ **A sortable column
is a ranking with extra steps** — if the surface permits sorting on it, the mount preconditions
travel with the sorted view.

**RULING 3 — ⚠⚠ REFUSAL IS AN OUTCOME, AND IT IS THE POINT OF THIS ENTRY.**
The standardizer's mean and `sd_k` were fit on **56 targets**. ⚠ **Applying them to a
surfaceome-wide population puts standardized values wherever the census distribution happens to
fall, and values far from zero produce extreme logits from small raw coefficients.**
- **Per feature, a census value outside the cohort's fit range yields
  `refused_out_of_distribution` — a CATEGORY, not a number, not a clamp, not a `None`.**
- ⚠ **The `preflight()` pattern**: *a case with no ruling is a stop, not a green light.*
  ⚠⚠ **And `F-049`'s lesson applies — a refusal that is written but unwired is decoration.** **It is
  wired at the call site or it does not exist.**
- **The range test is pre-registered in the order accompanying this entry and is measured BEFORE any
  profile is computed.** ⚠ **If most of the census falls outside range, the honest product is a
  refusal at scale and this entry's ruling 1 becomes moot** — **both outcomes are committed here, at
  equal prominence, before the measurement exists** (`F-022`).

**RULING 4 — ⚠ THE MOUNT PRECONDITIONS, IN FRAME, NOT IN A FOOTNOTE.** `D-094`. **Every rendered
profile carries, in the same frame:**
- **unlabelled** — ⚠⚠ **there is no leave-one-out out here.** `D-041`'s whole defence of the small
  model is that **LOO exposes overfitting as noise**; on 2,690 unlabelled proteins **that instrument
  does not exist.**
- **out of the fit population** — 56 targets from an **expression-selected** cohort (`A-014`,
  `F-011`: an upstream screen's positive class is a prediction, not a fact).
- **not a probability** — `F-006`: the cohort's own values span **0.116 to 0.285**, compressed toward
  the base rate. ⚠ **Whatever the census yields will be narrower and will be read as a probability
  by everyone who sees it unless the frame says otherwise.**
- ⚠⚠ **`F-050`: `membrane_proximal_plddt` carries 32.2% of attribution** — **the dominant feature is
  a confidence value, and confidence is precisely what differs most between a studied cohort and the
  unstudied two-thirds of the membraneome.** **The feature doing the most work is the one most
  likely to misbehave out of distribution.**

**RULING 5 — ⚠⚠ THE WALL. The profile may NEVER re-enter the cohort's arc.**
- **No census profile is compared to, merged with, or ranked against any cohort score.**
- ⚠⚠ **The scorer is NEVER refit to improve census behaviour.** **A refit is not pre-committed
  anywhere** (`FC3`, measured) and one made after seeing census output is post-hoc by construction.
- **`FEATURE_NAMES` stays at six.** ⚠ `D-027`'s six IS the pre-registration and the gate asserts
  `len == 6`.
- ⚠ **A test enforces this, proven RED**: wire a census profile into anything the cohort ranking
  reads, and the gate stops it. **The `EE-0` pattern, including the RENAME route** — *pin by name, a
  token scan is defeated by renaming.*

**RULING 6 — ⚠ `F-048`'s 58 are excluded at the point of computation, not filtered at display.**
**Geometric features on a five-residue fold are not a weak signal.** ⚠⚠ **`Q9ULH0` is a 5-residue
span and `min span_aa` across the 58 is 5.** **They carry `refused_span_below_floor` as a category.**
**A value computed and then hidden is a value that will eventually be exported.**

**RULING 7 — the surface reuses, never duplicates.** ⚠ `D-089`'s pattern: `get_structure_path` is not
tranche-filtered and already serves any analysis id. **A second route for one artifact is a second
source with nothing comparing them.**

---

**⚠ WHAT THIS AMENDMENT DOES NOT DO**
- **It does not lift `D-079`'s bar on SCORING.** ⚠ **It rules that a differently-named,
  never-ranked, refusable quantity is permitted. The bar on scoring stands.**
- ⚠⚠ **It does not license the profile as evidence for anything.** **Not for `P-001`, not for
  `P-002`, not for target selection, not for the atlas business case.** **What it is for is a
  separate decision that has not been made.**
- ⚠ **It does not touch `D-089`.** **A census page still carries no scorer panel** — *a census
  protein given a page that looks like a ranked target's page is how a reader concludes wrongly*, and
  a profile block must not become that page by another name.
- ⚠ **It does not pre-commit a refit at any n**, on the census or on rental folds.

**Assumptions relied on:** `A-014` (twice — the surface filter and the cohort's labels are both model
outputs) · `A-016`.
