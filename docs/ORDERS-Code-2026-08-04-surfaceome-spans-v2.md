# ORDERS — Code — 2026-08-04 — the surfaceome span census (RE-ISSUE v2)

> **Supersedes the first issue, which never reached the repository.**
>
> ## ⚠ Why v2 is much shorter: the Planner issued two orders for the same work
>
> The first issue told Code to fetch `table_S3_surfaceome.xlsx`, verify it, and read its counts.
> **So does `ORDERS-Code-2026-08-04-b-scale-readiness.md` §1 (Task A) and §2 (Task B).** Two orders,
> both claiming the download, the hashing, and the counts — **two paths to one quantity, never
> compared**, produced by the Planner on the same day the project catalogued that class's tenth
> instance. Had both shipped, Code would have had two authorities for one artifact and no rule for
> which wins.
>
> **Resolution: the scale-readiness order owns acquisition and identity. This order owns only the
> spans and the split, and it starts from that order's outputs.** Nothing is duplicated.

**Runs when Tasks A and B are green. Ungated on D-075** — no scorer, no ranking, no
`protein_analyses`, no surface. **If a change here reaches the database or `app/`, stop.**

---

## §1 — Inputs (produced by the scale-readiness order — do not re-derive)

| Input | From | What it carries |
|---|---|---|
| `data/census/table_S3_surfaceome.xlsx` | Task A | The full membraneome, **sha256-verified** against `2f1b8262…`, size `6864772` |
| `data/census/accession_map.csv` | Task B | entry name → accession, with `resolved / obsolete / multi / unresolved` |
| `data/census/PROVENANCE.md` | Task A | Source, hash, date, counts read off the file |

⚠ **`multi` and `unresolved` rows are NOT dropped.** They flow through as their own categories all
the way to the split. A census cost model that silently excludes the identifiers it could not
resolve is understating the census.

---

## §2 — Tests first (pure, on the gate)

| Test | Assertion | Prove it bites by |
|---|---|---|
| `test_split_is_measured_not_scaled` | The split takes a span list and returns counts; **no code path takes a ratio and a total** | Adding `scale_from(ratio, n)` → red. *The 82's 40/13/16/13 is an expression-filtered sample and is not evidence about the surfaceome — D-077 dec 6c.* |
| `test_split_reads_the_ceiling_structure` | Verdicts change when `LOCAL_CEILING` changes | Hardcoding 440 → red |
| `test_unstable_band_routes_conservatively` | An `unstable` band uses the low end | High end → red |
| `test_over_ceiling_is_distinct_from_rental` | Three categories, not two | Collapsing → red |
| `test_absent_span_is_a_category_not_a_zero` | No numeric ECD span → `no_topology`, **never** length 0 or `local` | Coercing to 0 → red |
| `test_unresolved_and_multi_survive_to_the_output` | Both appear as their own counts | Filtering either → red |
| `test_no_census_size_literal_in_the_module` | No `2886`, `2216`, `5102`, `2400` anywhere | Adding one → red |

**⚠ The absent-span test is load-bearing.** ~16% of the *82* had no sliceable topology. At census
scale a silent `0` would classify every unsliceable target as trivially free and understate the paid
half. This is the `?? 0` defect `TargetList.jsx` already records, in a new place.

---

## §3 — Then the code

- Extend `scripts/ecd_lengths.py` to take accessions from `accession_map.csv` and emit spans.
  **Rate-limit and cache to disk** — thousands of requests; a re-run reads the cache. Run date
  recorded either way.
- ⟡ **The constant duplication is already fixed** — Code bound `ecd_lengths.py` to the shared
  structure and added a test that fails if a bare literal reappears under `core/`, `scripts/`,
  `worker/`, or `app/`. **The span pull inherits that guard; add nothing.**
- Feed spans to `core/foldability.py::split` (D-077 Task 4).
- Emit `data/census/span_histogram.csv` plus a one-screen summary: counts per category, **the recipe
  triple `LOCAL_CEILING` was measured under**, the source file, the date.

⚠ **The artifact names the ceiling that produced it**, or two versions will circulate. `LOCAL_CEILING`
is still 440 (zero targets moved tier), so a split computed now is valid and simply gets recomputed
when Arm A lands. Cheap either way.

---

## §4 — What the split may claim

- ✅ **Cost:** *"Of the N rows on this list, M fall inside the measured local envelope at
  (int8, chunk 64); N−M need rented compute; K exceed every single-card ceiling; U were unresolvable
  identifiers."* Dated, recipe-named, derived.
- ✅ **Reproducibility:** *"M of these folds are reproducible on a consumer 8 GB GPU with no cloud
  spend."*
- ❌ **Not licensed:** coupling foldability to suitability · any census filtered by affordability
  (D-077 dec 1.3) · any statement about how many census rows are *good targets* — this measures
  sequence length and nothing else.

⚠ **A large unfoldable fraction is a finding, not a failure** — a measured limit of the method at
census scale, belonging in the paper's limitations at full strength.

---

## §5 — Out of scope

- **No database load, no enqueue, no folds, no UI.** The census build stays gated on D-075.
- **No selectivity, tumour-vs-normal, or disease stacking.** Owner-reserved and gated.
- ⟡ **No acquisition or identity work** — that is the scale-readiness order's, and duplicating it
  here is what v2 exists to prevent.
- ⟡ **The negative class is ingested and flagged, never ranked** (F-011). Spans are computed for it
  **only if** the annex is retained as its own category with a distinct label — a cost figure that
  silently merges annex and census members is wrong in both directions.

## §6 — Done when

Split runs from Task A/B outputs with no re-derivation · every §2 test observed red first · `multi`,
`unresolved`, and `no_topology` present as counts · histogram names its ceiling recipe and source
date · gate green · nothing in `app/`, `db/`, or `core/scorer.py` changed.
