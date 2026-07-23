# Amendment 1 to `ORDERS-Code-react-bundle.md`

**Date:** 2026-07-23, after D-038 shipped. **Applies to:** the React bundle orders, which
otherwise stand unchanged. Read the base orders first; this only records what D-038's landing
changed.

---

## 1. There are now TWO API surfaces the route-ordering trap can break

Base orders §2(a) named one. The suite must assert **both**:

- `GET /api/analyses` returns the API's JSON, not `index.html`
- `GET /api/coverage` returns the API's JSON, not `index.html`

A SPA catch-all that swallows `/api` returns `index.html` with a **200** — no error, no red test,
and the UI silently receives HTML where it expected JSON. With two surfaces, a partial mount is
also possible (one works, one doesn't), so assert them separately rather than assuming one
implies the other.

## 2. Step 4 (coverage view) is UNBLOCKED — fold it into PR C

Base orders §1 listed PR C as "coverage + method note" with the coverage view still gated. D-038
is live and verified on prod, so the supplier exists. PR C is now: **coverage view +
coverage-line component + method note + ADC context.**

## 3. ⚠ The coverage component renders an INTERSECTION, and this is a precision requirement

Computed from the live `/api/coverage`:

| disposition × fold_status | n |
|---|---|
| `ranked` × `folded` | **40** |
| `ranked` × `not_folded` | 27 |
| `held_out` × `folded` | 2 |
| `held_out` × `not_folded` | 11 |
| `excluded` × `not_folded` | 2 |

**The coverage line renders `ranked ∧ folded` — 40 of 82.** Never `ranked` alone (67, which
counts 27 rental targets that have not been folded) and never `folded` alone (42, which counts 2
held-out rows that are not in the ranking).

**Why this is a correctness requirement and not a display preference:** both 67 and 42 are true
numbers, and both overstate the cohort in the direction of completeness. D-024 exists because
*"N ranked, M held out" travels with every ranking* — a coverage line reading "67 of 82" beside a
ranking built on 40 folded structures is the precise failure the entry forbids. **The rows carry
both `disposition` and `fold_status`, so the intersection is computable client-side; no route
change is needed.**

The breakouts (`unmeasured_tier` 13, `no_topology` 13) are **subsets cutting across the
partition** and must never be summed into it. The partition itself sums to the denominator:
67 + 13 + 2 = 82.

## 4. Confidence bands — propose at 50/60/70, justified by the measured split

The distribution over all 42 folded rows: **24% below 50, 45% below 60, 57% below 70**. Those
boundaries are where this cohort actually divides, which is a stronger justification than
convention alone. Propose them in the PR with that reasoning; the Planner rules on review.

They gate step 3 — the target view cannot render confidence without them.

## 5. Log tidy

D-038's provenance line names `build_rows`; the actual function is `build_manifest` (`coverage()`
at :185 was correct). Fold the one-line correction into PR A's doc changes.
