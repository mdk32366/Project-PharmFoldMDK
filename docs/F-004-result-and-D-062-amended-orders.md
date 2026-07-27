# F-004 (the result) + amended D-062 orders (the surface)

> **Sequencing: F-004 lands FIRST, in its own commit, before the route or the UI.** Log leads code,
> and the result is the thing being rendered. One PR carries both.
> **Base:** `main` after #89. **Scope:** `app/`, `ui/src/`, `ui/src/system-model.json`, `tests/`,
> `docs/README.md`, `ARCHITECTURE.md`.
> **⚠ DO NOT RE-RUN THE FIT.** The result is recorded. This PR renders it.

---

## PART 1 — the entry

### F-004 — The pre-registered result: the structural axis is modestly above chance, indistinguishable from the comparator, and not a proxy for it

- **Date:** 2026-07-28
- **Type:** The pre-registered result (D-041). **A finding, not a decision** — nothing is ruled here.
- **How known (D-016):** one authorised run of `scripts/fit_scorer.py --run --persist` against
  `main` after #89 (D-064's label fix). Persisted as **`ranking_run` id=2**,
  `scorer_version=91e646e4a289`, `ranking_results` id=2, 56 `target_scores`.
  **Run exactly once. No re-run, no parameter changed after the result existed.**
- **Provenance chain:** an earlier run under the D-064 defect produced `ranking_results` id=1 with
  a **zero-positive label set**. That row is **retained and marked invalid**, not overwritten
  (D-064 decision 3). `ranking_runs` id=1 is the enqueue's anchor for 80 folds and is untouched.

---

#### The inputs, all fixed before the run

Six features (D-027) · L2 logistic regression, seven parameters (D-041) · 13-point λ grid, 5-fold
stratified inner CV, no RNG (D-060) · pLDDT floor 50 (D-041 §5) · **12 curated label accessions**
(F-003) · ranking set **56** · comparator **12** · head-to-head **8** (F-002, recomputed against the
curated file).

#### Result (1) — the pre-registered object: the leave-one-out percentile distribution

**`loo_status = complete`. 12 of 12 folds converged. No non-convergent targets.**

| Target | Percentile | | Target | Percentile |
|---|---|---|---|---|
| EGFR | 0.955 | | SLC3A2 | 0.634 |
| CDCP1 | 0.902 | | JAG1 | 0.580 |
| ERBB2 | 0.866 | | CD276 | 0.562 |
| NECTIN4 | 0.848 | | CDH11 | 0.384 |
| MERTK | 0.812 | | FGFR3 | 0.384 |
| | | | UPK1B | 0.312 |
| | | | SLC39A6 | 0.170 |

**Median 0.607 · mean 0.617 · 8 of 12 above 0.5**, against a null expectation of 0.5.

**A modest upward shift.** D-041 decision 3 fixed the reported object as *the full distribution with
median and spread* and barred a single summary number as the headline. **No significance test was
pre-registered and none is computed** — at n=12 one would be underpowered, and choosing a test after
seeing the distribution is the degree of freedom pre-registration exists to remove.

#### Result (2) — D-041 decision 3's first negative outcome: **FIRES**

On the 8 held-out positives carrying an evidence score, percentiles computed within the common
reference set of 12 (D-060 decision 8):

| | structural | comparator |
|---|---|---|
| mean | **0.573** | **0.5625** |
| median | **0.625** | **0.750** |

**Not distinguishable — and the direction reverses between mean and median.** That reversal is the
cleanest possible statement of the finding: which axis looks better depends on which summary you
choose, which is what *"not distinguishable"* means at this size. D-041's own words for this case:

> *"the structural axis adds nothing measurable at this cohort size. That is the result."*

**⚠ The comparator's degeneracy was predicted and held.** The evidence percentiles came back as
**exactly two values, 0.75 and 0.25** — because the published evidence score takes only two values
(nine 4s, eight 5s across 17 targets). D-060 decision 8 recorded this **before any number existed**,
and it bounds what this comparison could ever have shown in either direction.

#### Result (3) — D-041 decision 4's second negative outcome: **DOES NOT FIRE**

**Spearman(structural, evidence) = −0.0483 over N=12.**

D-015 §3 pre-registered that a **strong** correlation with the evidence score would *also* be a null
— it would mean the features proxy attention-and-precedent rather than measuring structure.
**Near-zero says they do not.** The structural axis is measuring something largely orthogonal to the
comparator.

#### Result (4) — the two together, which is the finding

> **The structural score ranks attempted-ADC targets modestly above chance, is not distinguishable
> from an expression-and-attention comparator, and is not a proxy for it. At twelve positives, the
> axis measures something different and cannot be shown to add anything.**

That combination is more informative than either null alone: **orthogonal but unproven** is a
different result from *"the features just re-learned the comparator,"* and the second was the more
likely prior.

---

#### ⚠ Three caveats that travel with this result, always

**(a) The design is conservative and biases toward the null.** Each held-out positive is ranked
among a pool that still contains the eleven training positives the model was fit to score highly.
That pushes held-out percentiles **down**. Five targets nonetheless exceeded 0.80, so the training
positives do not uniformly dominate — but **the bias runs toward understating, not overstating.**

**(b) An open confound: pLDDT may carry attention.** Two of the six features are pLDDT-derived, and
**pLDDT is partly a function of how well-represented a protein's family is in ESMFold's training
data — which tracks research attention, which tracks having been attempted as an ADC.** That is a
path by which the score could proxy attention *through the network's own confidence* rather than
through structure. Result (3) argues against it, **but the evidence score is a weak stand-in for
attention** (two values, 17 targets). **Recorded as an open confound, not as resolved.**

**(c) The top of the distribution is the famous targets.** EGFR, ERBB2 and NECTIN4 sit in the top
four. **Consistent with signal and equally consistent with (b).** It is not narrated as validation.

#### What this result does NOT claim

- **Not** that the score predicts clinical success. The label is *attempted*, not *viable* (D-041).
- **No per-target biological or clinical claim** (D-028). The delivery-agnostic framing appears once
  in the method note, never on a row.
- **Not** agreement with the paper: 12 derived labels against 22 published, with the gap recorded as
  a finding and its explanations named-but-unresolved (F-003 Finding 1).
- **Not** a significance claim. None was pre-registered; none is made.

#### Consequences

- **`fulldata_status = converged`**, 56 `target_scores` exist. **Both of D-041's negative-outcome
  tests are computable; neither is blocked** (D-064 decision 5's blocked branch does not apply).
- **The ranking table is buildable on real scores** — the first time in the project's history that
  has been true. It is still not mocked and still not required to be complete.
- **The honest route to a stronger result is more labelled data, not more parameters** (D-041).
  The roster's floor of 12 (F-003 Finding 6) is the binding constraint.

---

## PART 2 — amended orders for D-062, the scorer surface

**Two amendments to `ORDERS-Code-2026-07-28-D-062-scorer-surface.md`. Everything else stands.**

### Amendment 1 — `result_status` is `complete`, and a fourth value exists

`result_status` ∈ `complete` | `partial` | `raised` | `not_run`. **The live value is `complete`.**

**Build all four states** — the fixtures are cheap and the `raised`/`partial` panels are what make
the surface honest if a future refit fails. **But the panel that must be right tonight is
`complete`.**

**The route must filter on validity** — `ranking_results` id=1 is marked invalid (D-064 decision 3)
and **must never be served.** Serve the latest **valid** run. A test asserts the invalid row is
excluded.

### Amendment 2 — the ranking table is IN, at reduced scope

UI Plan v2 §3.1's full spec is **not** tonight's build. **Reduced scope, on real scores, not mocked:**

**IN:** rank · symbol · structural score · **the excluded set reachable, with its three named
reasons** (CXCR5 below floor 47.63, MSLN held out, MUC16 unfolded) · the coverage line rendered
**with** the table (D-024).

**OUT, deliberately, and named on screen as deferred:** baseline rank, delta, disagreement classes,
per-feature attribution. **`target_scores` carries the attributions** — they are stored and not yet
rendered, which is a display gap, not a data gap. **Say so rather than let a reader infer they
don't exist.**

### The surface, section by section

**A — the cascade.** 82 → folded → ranked → above floor → rankable → fit set → head-to-head. Each
step names **what it removes and why.** All three named exclusions reachable.

**B — the labels.** 12 accessions · the paper's 22 · ERBB2/NECTIN4/EGFR present · **the three
unverified symbols named as unverified-not-negative** (F-003 Finding 6) · one line on exclusion
classes.

**C — the pre-registration.** What was fixed before the run and **when** — D-027 (features), D-041
(model, both negative outcomes), D-060 (operational parameters), D-063/D-064 (the corrections).
**Dated, so the ordering is visible.**

**D — the result.** The distribution (all 12, median and spread) · the head-to-head **with its
denominator of 8 and the comparator's two-valued degeneracy stated** · the Spearman **with N=12** ·
**both negative-outcome tests named with which fired** · **all three caveats.**

**E — the ranking table**, reduced, with its coverage line.

### ⚠ Claim boundaries — pinned by tests, not by copy review

Extending D-062 decision 3, now that a real result exists:

- **No significance language.** No "significant," no p-value, no "demonstrates." None was
  pre-registered.
- **The mean/median reversal in the head-to-head is rendered**, not smoothed to whichever favours us.
- **Caveat (b), the pLDDT-attention confound, appears WITH the result** — not in a footnote, not on
  another page.
- **The top-of-distribution targets are not narrated as validation.**
- **No per-target claims.** No row says why it ranks where it does.
- **Every number derived from `/api/ranking`** — no `12`, `22`, `56`, `8`, `0.607` or `−0.0483`
  typed into a component. Constraint-A absence tests extended to the new literals.

### Order of work

1. **F-004** — own commit, first.
2. `tests/test_ranking_route.py` red → route → **`system-model.json` in the same PR** (the contract
   test reddens; fourth firing).
3. `ScorerView.jsx` + tests — four states, five sections.
4. Reduced ranking table + coverage line.
5. Nav to six surfaces · `ARCHITECTURE.md` · full gate · owner merge.

### What will bite

1. **Do not re-run the fit.** Not to check a number. Read the persisted row.
2. **Do not mock the deferred columns.** Absent and labelled deferred beats present and fake.
3. **The invalid row must not be served.** Test it.
4. **Do not write interpretive copy.** F-004's wording is the interpretation; the surface renders
   it. New sentences about what the result means are the owner's, in the log.
