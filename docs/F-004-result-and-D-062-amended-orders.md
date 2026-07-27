# F-004 (the result) + amended D-062 orders (the surface)

> **Sequencing: F-004 lands FIRST, in its own commit, before the route or the UI.** Log leads code,
> and the result is the thing being rendered. One PR carries both.
> **Base:** `main` after #89. **Scope:** `app/`, `ui/src/`, `ui/src/system-model.json`, `tests/`,
> `docs/README.md`, `ARCHITECTURE.md`.
> **⚠ DO NOT RE-RUN THE FIT.** The result is recorded. This PR renders it.

*(F-004's full text is landed in `docs/README.md` as the top log entry; this file is the handover
provenance for the result + the amended surface orders. PART 2 below is the actionable spec.)*

---

## PART 2 — amended orders for D-062, the scorer surface

**Two amendments to `ORDERS-Code-2026-07-28-D-062-scorer-surface.md`. Everything else stands.**

### Amendment 1 — `result_status` is `complete`, and a fourth value exists
`result_status` ∈ `complete` | `partial` | `raised` | `not_run`. **The live value is `complete`.**
Build all four states — the fixtures are cheap and the `raised`/`partial` panels are what make the
surface honest if a future refit fails. **The route must filter on validity** — `ranking_results`
id=1 is marked invalid (D-064 dec 3) and **must never be served.** Serve the latest **valid** run.
A test asserts the invalid row is excluded.

### Amendment 2 — the ranking table is IN, at reduced scope
**IN:** rank · symbol · structural score · the excluded set reachable, with its three named reasons
(CXCR5 below floor 47.63, MSLN held out, MUC16 unfolded) · the coverage line rendered **with** the
table (D-024). **OUT, named on screen as deferred:** baseline rank, delta, disagreement classes,
per-feature attribution. `target_scores` carries the attributions — stored, not yet rendered: a
display gap, not a data gap. Say so rather than let a reader infer they don't exist.

### The surface, section by section
- **A — the cascade.** 82 → folded → ranked → above floor → rankable → fit set → head-to-head. Each
  step names what it removes and why. All three named exclusions reachable.
- **B — the labels.** 12 accessions · the paper's 22 · ERBB2/NECTIN4/EGFR present · the three
  unverified symbols named as unverified-not-negative (F-003 Finding 6) · one line on exclusion classes.
- **C — the pre-registration.** What was fixed before the run and **when** — D-027, D-041, D-060,
  D-063/D-064. Dated, so the ordering is visible.
- **D — the result.** The distribution (all 12, median and spread) · the head-to-head with its
  denominator of 8 and the comparator's two-valued degeneracy stated · the Spearman with N=12 · both
  negative-outcome tests named with which fired · all three caveats.
- **E — the ranking table**, reduced, with its coverage line.

### ⚠ Claim boundaries — pinned by tests, not by copy review
- No significance language. No "significant," no p-value, no "demonstrates."
- The mean/median reversal in the head-to-head is rendered, not smoothed.
- Caveat (b), the pLDDT-attention confound, appears WITH the result — not a footnote, not another page.
- The top-of-distribution targets are not narrated as validation.
- No per-target claims.
- Every number derived from `/api/ranking` — no `12`, `22`, `56`, `8`, `0.607`, `−0.0483` typed into
  a component. Constraint-A absence tests extended to the new literals.

### Order of work
1. F-004 — own commit, first.
2. `tests/test_ranking_route.py` red → route → `system-model.json` in the same PR (contract test
   reddens; fourth firing).
3. `ScorerView.jsx` + tests — four states, five sections.
4. Reduced ranking table + coverage line.
5. Nav to six surfaces · `ARCHITECTURE.md` · full gate · owner merge.

### What will bite
1. Do not re-run the fit. Read the persisted row.
2. Do not mock the deferred columns. Absent and labelled deferred beats present and fake.
3. The invalid row must not be served. Test it.
4. Do not write interpretive copy. F-004's wording is the interpretation; the surface renders it.
