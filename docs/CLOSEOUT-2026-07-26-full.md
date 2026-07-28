# Close-Out — 2026-07-26 (delivery eve, the UI layer closed and the scorer arc staged)

> **main:** `3154c00` (`3154c004a12aa4fdbc6803cb05e6109c88177304`) — single main, in sync, zero open
> PRs, `.venv` restored to the lock.
> **Verified on merged main:** pytest **267 passing / 11 skipped**; UI vitest **60 passing / 15
> files**; image and build green.
> **Session type:** code-and-UI, no fold / worker / rental. The last session before delivery.
> **Delivery:** tomorrow.

---

## §0 — What shipped

Seven decisions, four PRs of code plus their docs, across one long session.

| PR | What | SHA |
|---|---|---|
| — | D-051 narrative surfaces (Story, architecture diagram pinned to routes, nav → 5, §5 fixes) | `c5efa2e` |
| — | D-052 ADC mechanism schematic (no-API-call boundary) | `d64752c` |
| — | D-053 + D-054 cancer associations + evidence-baseline deferral | `125c763` |
| #81 | D-057 orders → `docs/` | — |
| — | D-055 glossary + term contract test | *(in the D-055 PR)* |
| #… | D-056 plain-language pass + readability tripwire | `001fb88` |
| #83 | D-057 curation script + 24 tests + review outputs | `dfbae9f` |

Decisions landed: **D-051 through D-057.** Next number is **D-058.**

Suites across the session: pytest **232 → 267**; UI **30 / 6 files → 60 / 15 files.**

---

## §1 — The result of the day, said once: three tests caught live changes on the day they were written

This is the through-line and it is worth stating as one fact, because it happened three times with
three independent mechanisms:

1. **D-051's architecture contract test** went red when D-053 added `/api/associations` hours later
   — an unrelated change caught by a route-table pin written that morning.
2. **D-051's / D-053's Constraint-A absence tests** stayed green through the entire D-056 rewrite —
   a prose pass across nine components, the single most likely moment to type a cohort literal into
   a sentence, and the guard held.
3. **D-057's calibration test** caught the `radioimmunoconjugate ⊃ immunoconjugate` substring bug
   *before the script ran*, and the fix then **held against live registry data** — IGF2R routed as
   a probable exclusion when queried against the real ClinicalTrials.gov.

Every honesty claim in this project used to be an assertion about a mechanism. Today three of them
became observations of the mechanism firing against changes nobody staged for it. That is the
demonstrable form of the argument the whole project rests on, and it is reproducible in front of a
grader in under a minute (add a route, watch the gate redden).

---

## §2 — Corrections recorded (two against the Planner)

- **The Python baseline: the Planner's 227 was the wrong measurement.** Pre-work reported 227
  (static `def test_` count, labelled *inferred*) against the inherited 232 (labelled *unverified*).
  `pytest -q` settled it at **232**; the static count omitted parametrized expansions. The inherited
  figure won, and the provenance labels are what made the disagreement cheap to settle.
- **The associations method was reversed, not refined.** The 07-25 pre-work scoped associations as a
  hand-curated literature roster needing an owner pass. D-053 superseded it with derivation from the
  cohort's own source paper. Recorded as an amendment in the entry, not shipped quietly.
- **There is still no premise-correction counter in this repository, and none was invented.** Both
  Planner and Builder nearly wrote "the twelfth premise correction" into the record; a grep found no
  running count anywhere. The ordinal was dropped. Corrections are recorded where they happen. If a
  count is ever wanted it must be made checkable first — a named register a grep can verify.

---

## §3 — The scorer arc is now staged, and exactly one thing blocks it

D-041 has specified the model completely for three sessions: L2-regularized logistic regression, six
features (D-027), λ by nested CV inside each LOO fold, percentile distribution as the reported
statistic, negative outcome pre-registered. **None of that is the blocker.**

The blocker is labels, and only labels. D-040's Group B roster —
`data/adc_reference_mapping.csv` — is still owner-reserved and still uncurated. Today built the
tooling that makes curating it a review task rather than a search task:

- **D-057's script** ran a full offline pass: **31 of 82** targets got ≥1 candidate trial;
  **51** came back `needs_literature_check`; **15** routed `review_as_probable_group_b`.
- **The count is a finding, not a shortfall** (paper: 22; first hand pass: 10; script: 15). The
  spread is the result: the clinical-stage tail is query-findable, the preclinical tail is
  registry-invisible **by construction** — PODXL, a preclinical-only positive, predicted exactly
  this. The number was not adjusted toward 22, which would have been fitting the labels to the
  comparator.
- **The review sheet** — `data/derived/adc_reference_mapping_REVIEW-2026-07-26.csv` — is the
  evidence for the owner's labelling pass, dated because ADC pipelines move monthly.

**What stands between the project and a fitted scorer:** one owner curation pass over that sheet,
then `core/features.py` (the six D-027 features, does not yet exist), then `core/scorer.py`
(transcription of D-041), then the ranking table (UI Plan v2 §8). The judgement is reserved to the
owner; everything after it is code against a finished spec.

---

## §4 — Open items carried to the next pre-work (see the pre-work doc for the full list)

- **SORT1 disagreement — the top of the Group B pass.** The hand draft ruled SORT1 *no*
  (peptide-drug conjugate); the script routed it a *candidate positive* from live data. The two
  passes disagree on exactly one high-value row, and disagreement is where errors hide. Owner
  resolves it first.
- **GRIN1 coverage is soft.** Its `[NMDA]` alias threw a CTG 400 (bracket syntax); its search ran on
  fewer aliases than intended, so its `needs_literature_check` is weaker than its neighbours'.
- **D-057 script portability.** The ⚠ glyph crashes on Windows cp1252; tonight's run used
  `PYTHONIOENCODING=utf-8`. Latent defect for the next runner — ASCII-fold the warning glyphs.
- **Negative-test fragility (from the morning session, still standing).** The Constraint-A absence
  checks are substring `.not.toContain('82')` on short literals — brittle in both directions. If one
  false-fails, tighten to a word-boundary or specific-node match; **never delete it.**
- **Standing debt, unchanged by delivery:** the evidence baseline (D-054, deferred with a trigger);
  the untested components `TargetView` / `StructureViewer` / `CoverageView`; the 07-25 §5 doc fixes;
  D-045 Phase-2 pod CUDA verification (needs a GPU).

---

## §5 — Delivery readiness (the honest inventory for tomorrow)

**Done and defensible:**

- Five surfaces; every acronym a reader meets is decodable, pLDDT in both registers.
- Domain copy at ~eighth grade, ML copy left at peer level (the reader is an ML expert); readability
  moved **13.15 → 11.94 FK grade**, ceiling pinned to the measured value at 12.5, not an aspiration.
- Every cohort number on every surface is derived from `/api/*`, proven by absence tests.
- The architecture diagram is pinned to the live route table; the schematic cannot be mistaken for a
  model output; the associations state their claim boundary and their derivation gap on screen.

**Deliberately absent, and stronger for being so:**

- **The ranking table is not built and not mocked.** Fourth closeout carrying that commitment
  (07-23, 07-24, 07-25, 07-26). It waits on the scorer, which waits on the owner's labels. An ML
  grader will read *"pre-registered, then halted rather than fit badly"* as a more sophisticated
  result than a model fit to 22 hand-assembled labels the night before — which is the alternative
  that was available every session and declined every session, including tonight.

**The one line to walk in with:** a test written in the morning caught a change made in the
afternoon. Everything else is features; that is the argument.

---

## §6 — State handed forward

main `3154c00`, clean. pytest 267 / 11 skipped, UI 60 / 15. Seven decisions closed. The scorer is
one owner-reserved judgement away from being pure code against a three-session-old spec. Tomorrow is
a delivery, not a build.

---

## Corrections (appended 2026-07-29 — D-066 §5, NOT edited in place)

**⚠ This section is dated after the closeout.** Everything above is the record of what was believed
on 2026-07-26; editing it in place would make the log claim these corrections were known then. They
were not — they are appended.

**Correction, 2026-07-29** (on §5's *"every acronym a reader meets is decodable"*): this overstated
the guard. It polices a curated watchlist on scanned surfaces only. A later measurement found **8 of
11 ruled terms undefined and 11 prose-bearing surfaces unscanned** (measured mechanically: components
rendering user-visible prose, minus the four in `surfaces()`; 2 of the 11 — `Term` and `Glossary` —
render definitions themselves, so the effective copy-sweep target is ~9). The earlier "5" here was a
Planner estimate, not a measurement, and was wrong — a correction about unmeasured claims that itself
carried an unmeasured number.

**Also: it is six surfaces now, not five** — the `Scorer` surface (D-062) was added after this closeout.

**Discharged, 2026-07-29 (measurement, not CI):** the deferred item above — *"D-045 Phase-2 pod CUDA
verification (needs a GPU)"* — is **discharged by measurement.** The 2026-07-25 pod folds carry the
full environment provenance: `torch_version 2.8.0+cu128`, `transformers_version 5.14.1`,
`device_name NVIDIA RTX A6000`, `cuda_version 12.8` (4 of 80 rows captured; pre-D-045 folds honestly
show "not captured", and the `Provenance` panel's post-D-045 test renders these exact keys). The
verification that was waiting on a GPU CI runner the project never had, the pod supplied by running.
Read from stored provenance — **no backfill** (D-016).
