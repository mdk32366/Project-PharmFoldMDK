# PASTE-READY — `D-079 amendment ‹N›` — for `docs/README.md`

**AUTHORED-SHA256** (range: **first `####` header → EOF**, anchored to line starts, **SECOND
occurrence of the marker**) = `172e3b976a4070213e2e1c3d1de57c1458649e70d4c346db962421e28e15d54c`
**bytes** = `6417`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE.** Landing header **above** the first `## §`/`####` marker,
> **outside the hash range.** Sub-entry — **no integer.**
>
> ⚠⚠ **THE AMENDMENT NUMBER IS `‹N›` AND CODE DETERMINES IT.** At `b06d378` `D-079` carries
> amendments **1–5**. **Do not assume 6** — entries have landed since. **Report the number taken, and
> substitute it in the two self-references below**, declaring the substitution and the byte delta.

---

#### D-079 amendment ‹N› — ⚠⚠ The census splits: about half can carry a structural profile and about half must be REFUSED, which is neither branch amendment 1 committed to

- **Date:** 2026-08-20 · **Status:** ruled. ⚠ **`D-079` remains a pre-registration and remains void if
  code precedes it. No profile has been computed.**
- **Amends:** `D-079 amendment 1`, whose ruling 3 pre-registered a fork the measurement did not take.

---

**1 — ⚠⚠ THE MEASUREMENT, AND IT IS A THIRD STATE.**

Amendment 1 was written as a fork: **profile the census, or refuse at scale.** `KB` measured the
census feature artifact (`census_features.v1.jsonl`, 2,690/2,690, `sha256 c08f9f1d…591863`) against
the cohort's fit range:

| bar | refused | computable | of |
|---|---|---|---|
| **STRICT (cohort min–max)** | **1,225 — 46.7%** | **1,397 — 53.3%** | 2,622 |
| p05–p95 | 1,820 — 69.4% | 802 — 30.6% | 2,622 |
| ±3 sd *(ddof caveat)* | 638 — 24.3% | 1,984 — 75.7% | 2,622 |
| ⚠ **out of range on ALL SIX** | **0 at every bar** | | |

⚠ **Denominator is 2,622, not 2,690** — the **58** `refused_span_below_floor` (`F-048`) and **10**
`fewer than two CA atoms` account for 68. **State which, every time.**

**⚠⚠ RULING 1 AND RULING 3 ARE BOTH OPERATIVE, ON DIFFERENT HALVES OF ONE POPULATION.** **Refusal at
~47% is the common case, not an edge case, and amendment 1 did not anticipate a split.**

**2 — ⚠ THE BAR IS RULED: STRICT (cohort observed min–max), and the other two are REPORTED beside it.**

⚠⚠ **The bar changes the answer by a factor of nearly three and choosing one silently would be a dial
wearing the costume of a measurement.** **Strict is ruled because it is the only bar with no free
parameter: it is the range the standardizer was actually fit over.** ⚠ **p05–p95 discards real
observed values; ±3 sd inherits a `ddof` choice and `sd_k` is not persisted (`F-049` amendment 1).**

**⚠ All three render wherever the count is stated. The surface names which bar it is using, in frame.**

**3 — ⚠⚠ THE HARD PART IS THE SURFACE, NOT THE RULING.**

**Half the census showing a number and half showing a category is `D-089`'s hazard MIRRORED.**
`D-089`: *a census protein given a page that looks like a ranked target's page is how a reader
concludes wrongly.* ⚠⚠ **Now the inverse: a reader seeing `refused_out_of_distribution` beside a
neighbour's profile will conclude THE REFUSED ONE IS WORSE.** **It is not. It is unmeasurable by this
instrument.**

**Ruled, and each is a condition:**
- ⚠⚠ **The refusal is not rendered as a deficiency, an absence, or a low value.** **It states the
  CAUSE:** *this protein's ‹feature› falls outside the range the model was fitted over, so no profile
  is computed.* **Never a blank, never a zero, never a dash.**
- ⚠ **The refused rows are NOT sorted below the profiled ones, and NOT filtered out by default.**
  **Amendment 1 ruling 2 bars ranking including by sort order; a default sort that sinks refusals is
  a ranking of evidence availability.**
- ⚠⚠ **The refusal names WHICH feature or features put it out of range.** **A protein refused on
  `ecd_length` and one refused on `mean_plddt_ecd` are different facts** — and `KB4`'s distribution
  of how many features each row fails is the evidence.
- ⚠ **Both counts render together wherever either does** — **1,397 computable and 1,225 refused, of
  2,622, at the strict bar.** **A page showing only the profiled half is the flattering half**, which
  is `D-093` decision 5's argument applied here.

**4 — ⚠⚠ THE PLANNER'S PRE-REGISTERED EXPECTATION SCORED TWO MISSES, AND THE MISSES ARE THE RESULT.**

| predicted | measured |
|---|---|
| `ecd_length` **worst offender** | ⚠⚠ **MISSED** — 146 rows, **5.6%**, nearly the mildest |
| `mean_plddt_ecd` **mildest** | ⚠⚠ **MISSED** — 868 rows, **33.1%**, **the worst** |
| **a minority** out of range | **HELD**, at **46.7%** — *and only just* |

⚠⚠ **Amendment 1 ruling 4 predicted the MECHANISM while the Planner predicted the opposite OUTCOME
from it:** *"the feature doing the most work is the one most likely to misbehave out of
distribution."* **Confirmed — the two confidence features are offenders #1 and #2, they are `F-051`'s
pair carrying 38.6% of attribution, and the census sits far below the cohort on both.**

**⚠ THE CAUTION TRAVELS WITH THE NUMBER, WHEREVER IT APPEARS:** **the ranking set requires
`mean_plddt ≥ 50`, so 831 of the 868 strict failures fall below a floor the COHORT had and the CENSUS
does not.** **33.1% is a floor artefact as much as a distribution shift, and it must never be quoted
without that sentence.**

⚠ **This is scoreable only because it was written before the number existed.** **`F-022`, applied to
the Planner rather than to a run.**

**5 — ⚠ What is UNCHANGED from amendment 1, restated because a split invites erosion.**
- **`structural_profile`. Never `score`, never `rank`, never `suitability`.**
- ⚠ **No ranking, including by sort order.**
- **`F-048`'s 58 excluded AT COMPUTATION**, carrying `refused_span_below_floor` — ⚠ **and now
  measurably distinct from `refused_out_of_distribution`: two refusals, two causes, never pooled.**
- ⚠⚠ **The profile NEVER re-enters the cohort's arc, and the scorer is NEVER refit to improve census
  behaviour.** **`P-001` is unanswerable if it does.**
- **`FEATURE_NAMES` stays at six.**
- ⚠ **`D-089` unchanged: a census page still carries no scorer panel**, and a profile block must not
  become that page by another name.

**6 — ⚠ What this entry does NOT do.**
- **It does not authorise computing any profile.** ⚠ **The surface contract in §3 is a precondition,
  not a description of something built.**
- ⚠⚠ **It does not license reading the refused half as a negative result.** *Unmeasurable by this
  instrument* is not *worse*, and the entry says so in the frame the reader sees.
- **It does not change the bar later.** ⚠ **Strict is ruled here, before any profile exists; changing
  it after seeing which proteins fall out is the shape `D-075` decision 5 bars.**

**Assumptions relied on:** ⚠ `A-014` — **twice: the surfaceome filter that produced the census, and
the expression screen that produced the cohort whose range defines the bar.** **The fit range is a
property of a selected population, not of proteins.**
