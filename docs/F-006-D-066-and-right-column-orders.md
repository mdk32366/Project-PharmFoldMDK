# F-006 + D-066 + orders — the score distribution, the `ranked` collision, and the right column

> **Scope:** `ui/src/`, `docs/`. **NOT in this PR:** `app/`, routes, `core/`, `scripts/`,
> migrations. **No re-run, no new statistic.**
> **Entries land first, in their own commits.** Log leads code.

---

## PART 1 — the entries

### F-006 — The fitted scores are compressed toward the base rate, and are not calibrated probabilities

- **Date:** 2026-07-29
- **Type:** A finding. Nothing ruled.
- **How known (D-016):** read-only SQL against `target_scores` where `ranking_run_id = 2`
  (the pre-registered run), over the live proxy.

| | |
|---|---|
| min | **0.116** |
| median | **0.220** |
| max | **0.285** |
| count | **56** |
| labelled fraction (12 / 56) | **0.214** |

#### Finding (1) — the median sits on the base rate, and nothing reaches 0.3

**Median 0.220 against a labelled fraction of 0.214.** The typical target is lifted almost nothing
off the prior. The whole field spans **0.116–0.285**; rank 1 is the ceiling and sits ~0.065 above
the median.

**⚠ A reader shown "rank 1 = 0.285" with no framing will read it as a middling probability**, when
it is the top of a field that never clears 0.3.

#### Finding (2) — ⚠ this is the expected signature of L2 shrinkage at n=12, not necessarily a weak ordering

**Compression of absolute scores toward the base rate is what an L2-penalized fit on twelve
positives is expected to produce.** D-041 chose L2 precisely to shrink unstable coefficients, and
shrunk coefficients yield outputs pulled toward the prior.

**The absolute spread is therefore weak evidence about the ordering, in either direction.** The
evidence about the ordering is **F-004's leave-one-out percentile distribution** — median 0.607,
8 of 12 above chance — which is computed on **positions, not values**, and is unaffected by
compression.

**Stated plainly: compressed scores do not by themselves make the ranking uninformative, and they
are not evidence that it is informative either.** The two questions are separate and only the
second was pre-registered.

#### Finding (3) — ⚠ the score is NOT a calibrated probability

A logistic model outputs a number in [0,1], **but calibration was never tested** and no calibration
claim was pre-registered. **Nothing on any surface may present 0.285 as "a 28.5% chance"**, and the
`Score` tooltip must say so explicitly.

**Recorded as a Planner correction:** an earlier draft of that tooltip read *"the model's estimated
probability that a target belongs to the labelled set."* **Withdrawn** — it implied calibration that
was never established.

#### Consequences

- The `Score` column tooltip carries **the scale, the observed range, the labelled fraction, and the
  non-calibration statement**, all derived from `/api/ranking`, none typed (D-050).
- **`COUNT(*) = 56` is what surfaced D-066** — the cross-check earned its place and is recorded as
  having done so.
- **No re-fit, no re-scaling, no calibration step.** Any of those would be a model change after
  seeing a result. If calibration is ever wanted it is a new entry, dated after this one.

---

### D-066 — `ranked` names two different quantities, and a shared component asserted a claim it cannot verify

- **Date:** 2026-07-29
- **Status:** Proposed → Accepted on merge.
- **Relates:** D-024 (the partition, and the denominator travelling with the claim), D-050 (derived,
  never hardcoded), F-002 (the cascade), F-006 (the count that exposed it).

**Context — the defect, on the deployed surface.** `CoverageLine.jsx` asserts *"The ranking … covers
these {rankedFolded}"*, which computes to **67**, **directly above a 56-row ranking table** on
`/scorer`. On `/coverage` the same 67 is correct.

**Root cause — one word, two referents:**

| Usage | Meaning | Value |
|---|---|---|
| `ranked` on `/coverage` | the **D-024 disposition** — ranked / held_out / excluded, over all 82 | **67** |
| `ranked` on `/scorer` | **membership in the actual ranking**, after the pLDDT-50 floor | **56** |

**⚠ Same class as the 67-vs-67 collision recorded in F-002** — two different quantities sharing a
word, and on that occasion sharing a *value*, which is what concealed it. **This is the fifth
instance of *two paths to one quantity, never compared*, and the first where the collision is
lexical rather than computational.**

**The tell was in the copy the whole time:** *"The ranking — once the scorer exists — covers these
67"* was written **before a ranking existed.** It was a forward-looking promise. It became a false
claim on one surface and an unverifiable one on the other the moment the scorer ran.

#### Decision (1) — `CoverageLine` states the partition and stops claiming what the ranking covers

**A coverage component cannot know what a ranking covers.** It knows the D-024 partition; the
ranking's membership is decided downstream by the pLDDT floor, which the component has no visibility
into. **The forward-looking clause is removed, not re-tensed.**

This fixes both surfaces at once: `/coverage` keeps a true partition statement, `/scorer` stops
carrying a false one.

#### Decision (2) — the scorer supplies the reconciliation beside its own table

Rendered in the right column, immediately above the table, **all three numbers derived**:

> **67** ranked · **56** above the pLDDT-50 floor · **these 56 are ranked below**

**The missing step was never wrong, only absent from where it was needed** — it exists in cascade A,
in the left column, disconnected from the box making the claim. **A denominator in another column is
a denominator that does not travel with its claim** (D-024).

#### Decision (3) — ⚠ REJECTED: a prop supplying the post-floor count to the shared component

It would work and it is the smaller diff. **Rejected because it preserves the defect's shape:** the
component would continue to assert what the ranking covers, using a number handed to it, with no way
to verify the claim. **The next surface that reuses it inherits the same trap.**

#### Decision (4) — the vocabulary is fixed

- **`ranked`** — the D-024 disposition. Over 82. **Never means "in the ranking."**
- **`rankable`** — folded ∧ ranked ∧ above the pLDDT floor. The set the ranking covers. Already the
  term used in F-002 and cascade A.

**Any surface using `ranked` to mean the ranking's membership is a defect.**

- **Deep-learning justification:** none directly; this is a denominator-honesty decision. It bears on
  the model's reporting because **a ranking presented over the wrong denominator overstates its own
  coverage**, which is the failure D-024 exists to prevent.

- **Consequences / test surface:**
  - `CoverageLine` **no longer contains a ranking-coverage claim** — asserted by absence, on both
    surfaces.
  - The scorer's reconciliation line renders all three numbers **derived**, and a fixture with
    distinctive values proves none is typed.
  - **`/coverage` is unchanged in meaning** — its partition test stays green.
  - **The stale tense disappears with the clause**, so no separate tense fix is needed.

---

## PART 2 — orders

### 1. Order of work

1. **F-006, then D-066** — own commits, before code.
2. **`CoverageLine`** — remove the ranking-coverage clause; absence test first, red.
3. **Scorer reconciliation line** — above the table, three derived numbers.
4. **Right-column reduction** — box + table only.
5. **`Score` column tooltip** — distinct from the `structural score` term tooltip.
6. Tests, `ARCHITECTURE.md`, gate, owner merge.

### 2. Placements — ruled, do not guess

| Element | Goes |
|---|---|
| Intro paragraph above the table | **removed** |
| pLDDT-driven note (F-005) | **into the `Score` tooltip** |
| Excluded-set `<details>` | **stays right, inside the coverage box** — it is part of the coverage statement, and D-062 requires the three named exclusions reachable |
| Deferred-columns note | **left column, under section D** |

### 3. The `Score` column tooltip — proposed, owner to approve

> **Score** — the model's output for each target, between 0 and 1; higher means more like the 12
> targets people have already built ADCs against. **It is not a calibrated probability** —
> calibration was never tested at this cohort size, so read it as a position in the ordering, not a
> percentage chance. In this run the 56 scores span **{min}–{max}**, median **{median}**, against a
> labelled fraction of **{labelled}/{ranked}**. The ordering is substantially pLDDT-driven (F-005).

**Every brace is derived from `/api/ranking`.** The non-calibration sentence is a claim boundary and
**does not get trimmed for length** — assert its presence in the rendered tooltip DOM, as with
`structural score`.

### 4. ⚠ What must not break

- **`/coverage` still renders a true partition** and its tests stay green.
- **Constraint-A absence extended** — no `0.116`, `0.220`, `0.285`, `56`, `67` literal in any
  component.
- **Caveat (b) stays with the result; the coverage line stays with its table**, both at desktop and
  **stacked** — the two orderings already walk-verified.
- **All four `result_status` states still render.**
- **Readability tripwire** under the pinned ceiling. If breached, **shorten explanation, never a
  claim boundary.**

### 5. Closeout — APPEND, do not edit in place

**⚠ The 07-26 closeout is a dated record of what was believed then.** Editing it in place makes the
log claim that was known on the 26th. **Append instead:**

> **Correction, 2026-07-29:** this overstated the guard. It polices a curated watchlist on scanned
> surfaces only. A later measurement found 8 of 11 ruled terms undefined and 5 surfaces unscanned.

**Also: it is six surfaces now, not five.**

### 6. Appendix — the 8 glossary definitions, drafted for owner domain check

For **guard part one**, which follows this PR. **Owner approves or amends each; add nothing unasked.**

- **percentile** — where something sits in an ordered list, as a fraction. 0.85 means it ranks above
  85% of the others.
- **leave-one-out** — a way of testing a model on data it has not seen. Each labelled target is
  removed in turn, the model is refitted on the rest, then asked to rank the one it never saw.
- **held out** — kept out of a comparison on purpose. Here: targets whose extracellular region could
  not be sliced the same way as the others, so their measurements are not comparable (D-021).
- **Spearman** — a measure of whether two rankings agree, from −1 (opposite) through 0 (unrelated)
  to +1 (identical). It compares positions, not values.
- **ranking set** — the 56 targets that are folded, comparable, and above the pLDDT floor. The only
  ones the ranking covers.
- **comparator** — the published evidence score from the source paper, used as a yardstick rather
  than a truth. It covers 17 of the 82 targets and takes only two values among those compared here.
- **evidence score** — the source paper's 1–5 rating of how much prior evidence supports a target.
  Only the 4s and 5s were published in its text.
- **Group B** — targets someone has already built an antibody-drug conjugate against, at any stage
  from preclinical onward. **This is the label the model is fitted to: it records what was
  attempted, not what worked.**

**⚠ Group B's final sentence is a claim boundary** (D-041's bounded claim). It does not get trimmed.
