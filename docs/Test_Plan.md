# Test Plan: PharmFoldMDK

**Project**: PharmFoldMDK – AI-Powered Protein Structure Prediction & Pharmaceutical Analysis Platform  
**Date**: July 16, 2026

---

## Overview

This test plan covers two complementary approaches as requested:

1. **Functional Tests** — Automated Python tests (primarily pytest) for backend logic, data layer, inference modules, and API endpoints.
2. **User Testing** — Structured human interaction scenarios focused on end-to-end flows and the perceived value of the system’s outputs.

**Scope Focus**: PharmFoldMDK is scoped around **Antibody-Drug Conjugate (ADC) target exploration**. All testing prioritizes features that help evaluate overexpressed proteins in cancer as potential ADC targets.

The plan is aligned with the ADC-focused value outputs defined in TDD v3 (highest value: protein structure of cancer targets, druggable pocket identification, ADC suitability assessment, mutation impact, comparison to known targets, and therapeutic reports).

---

## Section A: Functional Tests (Python / pytest)

### Recommended Test Structure

```
tests/
├── conftest.py                 # Shared fixtures (test DB, sample data, mocks)
├── test_auth.py                # Authentication & authorization
├── test_db.py                  # Database CRUD, relationships, JSONB handling
├── test_inference.py           # Structure retrieval, model fallback, confidence parsing
├── test_analysis_service.py    # Mutation impact, pocket detection, report generation
├── test_api.py                 # FastAPI endpoint tests (with TestClient)
└── test_vector_search.py       # Semantic search (Iteration 3+)
```

### Key Test Areas & Example Ideas

**1. Authentication & Security**
- User registration creates account with hashed password
- Login returns valid session / token
- Protected routes require authentication
- Password reset / change flows (if implemented)

**2. Database Layer**
- Create analysis record with correct metadata and file path
- Mutation records correctly linked to parent analysis
- Report generation creates DB record + file on volume
- JSONB fields (metadata, preferences) store and retrieve correctly
- Cascade deletes or soft-delete behavior works as designed

**3. Inference & Analysis Modules**
- UniProt ID lookup returns valid structure + confidence scores
- On-demand fallback (e.g., ESMFold) produces usable output when primary source unavailable
- PDB file is correctly saved to volume and path is recorded
- Mutation impact calculation produces reasonable delta (stability or pocket change)
- Pocket detection returns list of plausible binding sites with scores

**4. API Endpoints**
- POST /analyses accepts valid input and returns analysis ID + summary
- GET /analyses/{id} returns full details including file paths
- Mutation simulation endpoint correctly links to parent analysis
- Report generation endpoint produces downloadable artifact
- Error handling for invalid sequences, missing files, low-confidence results

**5. Vector / Semantic Search (Iteration 3+)**
- Embedding generation and storage works
- Semantic search returns relevant prior analyses for a user
- Hybrid queries (user filter + semantic similarity) function correctly

**Testing Approach**
- Use mocks and fixtures heavily for external calls (AlphaFold DB, model inference) to keep tests fast and deterministic.
- Use an in-memory or temporary SQLite/Postgres test database.
- Run with `pytest` + coverage reporting.
- Integration tests can use a real lightweight model or cached responses.

**Coverage Goals**
- High coverage on data layer, business logic, and API contracts.
- Specific tests for confidence metric handling and graceful fallback behavior.
- Performance smoke tests for inference paths (even if mocked).

---

## Section B: User Testing (Human Interaction Scenarios)

These are manual or lightly scripted tests performed by the developer, classmates, or beta users. Focus is on real-world usability and whether users can derive the high-value outputs defined in the TDD.

### Core User Testing Scenarios

**Scenario 1: First-Time User – High-Value Structure Output (Iteration 1)**
- **Steps**:
  1. Register / log in
  2. Input a known drug target (e.g., UniProt ID for EGFR or a viral protein)
  3. Run analysis
  4. Inspect 3D viewer and confidence score
  5. Export PDB
- **Success Criteria**:
  - User quickly obtains a usable 3D structure with clear confidence communication
  - 3D viewer is intuitive
  - Export works without friction
- **Evaluation**: Time to first insight, clarity of confidence display, any confusion around sources (AlphaFold vs. on-demand)

**Scenario 2: Mutation Impact Exploration (Iteration 2)**
- **Steps**:
  1. Load or create a base analysis
  2. Use mutation simulator to introduce a disease-associated or user-chosen mutation
  3. Observe visual and quantitative changes (pocket geometry, confidence shifts, impact notes)
  4. Compare wild-type vs. mutant views
- **Success Criteria**:
  - User gains actionable insight into how the mutation affects structure or druggability
  - Comparison view is clear and useful
- **Evaluation**: Perceived value of mutation output for pharma/precision medicine context

**Scenario 3: Report Generation & Export (Iteration 3)**
- **Steps**:
  1. Perform analysis with mutations and/or pockets identified
  2. Generate a report (structure summary + mutation impact or pharma context)
  3. Review report content for usefulness and accuracy of caveats
  4. Export as PDF or Markdown
- **Success Criteria**:
  - Report feels like a decision-support artifact rather than raw data dump
  - Key outputs (confidence, pockets, mutation effects) are clearly summarized
- **Evaluation**: Usefulness for communication or downstream work

**Scenario 4: Library & Semantic Search (Iteration 3)**
- **Steps**:
  1. Create several analyses on related targets
  2. Use history/search to retrieve prior work
  3. Test semantic search for conceptually related analyses
- **Success Criteria**:
  - Library is easy to navigate
  - Semantic search returns relevant results
- **Evaluation**: Long-term usability and reuse value

### Additional Testing Areas

- **Edge Cases**: Very long sequences, invalid input, low-confidence results, upload failures, missing files on volume.
- **Performance / Responsiveness**: Loading times for 3D viewer and any on-demand inference (with progress indicators).
- **Accessibility & Polish**: Labels, contrast, error messages, mobile responsiveness (secondary priority).
- **Pharma Framing**: Do labels and help text make the outputs feel relevant to drug discovery / precision medicine?

### Execution & Documentation

- Create a shared document (Notion, Google Doc, or Markdown) with the scenarios above.
- Testers record pass/fail + qualitative notes + screenshots where helpful.
- Run user testing at the end of each major iteration (especially after 1, 2, and 3).
- Include “think-aloud” sessions for early UX feedback.
- Simple rubric: “How valuable was the [pocket / mutation / report] output?” (1–5 scale) + open comments.

---

## Summary

| Test Type          | Focus                              | Tools / Approach                  | When to Run          |
|--------------------|------------------------------------|-----------------------------------|----------------------|
| **Functional**     | Backend logic, data, inference, API | pytest + mocks + TestClient      | Continuously + CI   |
| **User Testing**   | End-to-end value & usability      | Human scenarios + feedback form  | End of major iterations |

This balanced approach ensures both technical correctness and that the system delivers on the high-value pharmaceutical outputs it was designed for.

---

## ⚠ ADDENDUM 2026-08-16 — what a test has to do here, learned by writing bad ones

**The suite is 637 passing / 15 skipped.** ⚠ **Count is not the property.** Every rule below was
earned by a test that passed while guarding nothing.

### A-017, three clauses, each asserted SEPARATELY

**(a) the fixture must reach the code under test.** ⚠ A revert proof performed the `setattr` loop
*inside the test*, so it exercised the loop in the test and not the one in `fold()` — reverting the
code left it **green**. **A scan that matches nothing, or a fixture the code never sees, passes
perfectly.** Assert the scan **finds** things: `assert len(found) >= 3`.

**(b) one property, one test.**

**(c) ⚠ the fixture must contain a case where correct and incorrect DIFFER.** A date test only
discriminates on a row whose span actually changes. A grain test needs a protein reached by **two**
identifiers. A leak test needs the two populations to actually **overlap** — so the overlap itself
is asserted, because if it collapsed, every other assertion would pass for the wrong reason.

### ⚠ Prove by revert, and read WHERE it reds

**An error-red and a failure-red are different objects.** A test that reds at *collection* proves
nothing about the assertion. Every guard in this project is reverted deliberately and the **file and
line** recorded — ⚠ and one revert proof **did not red at all**, which is how it was found to be
testing itself.

### ⚠⚠ Test the PROPERTY, not the prose

The census "unscored" check banned the substring `score` — and flagged the page's own *"has not been
scored"*. Rewritten to require a negation, it flagged *"the 82 **ranked** targets"*. **Both were
policing wording.** It is now **structural**: the data objects carry no score field, so the page
cannot render one however it is worded. ⚠ **Fitting a test to a page until it goes green is how a
guard becomes a decoration.**

### ⚠ Guard the CLASS, not the instance

Two unfiltered reads leaked; the test **enumerates every `select(ProteinAnalysis…)` in `app/`** so
the next one reds too. Two shapes drifted apart; the test **reads the required keys out of the
consumer's source**, never from a hand-kept list — ⚠ **a hand-kept list is the thing that drifts.**

### ⚠ Exemptions must be narrow, stated, and justified in the test

The leak guard first flagged `artifacts_present` — correctly — and **filtering it would have made
every census fold un-completable.** The exemption (primary-key lookups) is written into the
docstring **with the reason**, because an unexplained exemption is indistinguishable from an
oversight.

### ⚠⚠ A guard downstream of the filter it guards watches nothing

A VRAM guard placed **after** the selector stopped watching exactly the rows the selector excluded —
the rows it existed for. A `check_sliced_length` that only ran on the sliced branch would have gone
green on 3,468 whole-sequence folds. **Both branches are checked.**

### ⚠ No `assert` in a guard path

`assert` vanishes under `python -O`. **Any check whose failure would produce a wrong artifact raises
an explicit exception.** ⚠ Four `assert`s doing guard work remain in `scripts/` — **reported, ruled
for conversion, and latent rather than live** since nothing in the repo passes `-O`.

### ⚠ The gate's exit code is pytest's, or it is nothing

`pytest -q > file; GATE=$(tail -1 file); RC=$?` captures **`tail`'s** status. ⚠ **A commit landed
with 4 failures this way.** Capture `$?` on the line **immediately** after the command, with nothing
between — and **copy the count from the run, never recall it.**

### ⚠ A dry run that does not exercise the consumer's contract is not a dry run

The census ingest validated slices, spans and DB invariants — and omitted a key `/claim` subscripts.
Ten jobs were marked `claimed`, then stranded with `attempts=0` and no error. **The dry run now
builds the consumer's object before any write.**

---

## Addendum 2026-09-02 — D-107 `/about` not-built msa path

Acceptance tests for the About page (`/about`, `AdcContext.jsx`). Implemented in
`ui/src/components/AdcContext.test.jsx`. Each AT must be able to go red.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1071** | `/about` still contains `antibody–drug conjugate` (existing ADC copy; en-dash as rendered) | `T-1071: /about still contains the existing ADC copy (antibody–drug conjugate)` |
| **T-1072** | `/about` contains `What’s next (not built)` and `MSA` and `ESMFold stays` | `T-1072: /about contains “What’s next (not built)” and “MSA” and “ESMFold stays”` |
| **T-1073** | `/about` does not contain the three forbidden product-edition strings (negative assertions in the test only) | `T-1073: /about does not contain forbidden product-edition strings` |

---

## Addendum 2026-09-02 — D-107 amendment 1 msa-tier plumbing

Acceptance tests for slice B (queue plumbing). Implemented in
`tests/test_msa_tier_plumbing.py` against `UnlockedFakeJobQueue` / SQLite. Each AT
must be able to go red. No live Postgres integration job. About copy is slice A;
MSA worker image is slice C.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1074** | Seed pending rental + pending msa; `claim(..., tier='rental')` returns the rental job only | `test_rental_claim_returns_the_rental_job_only_when_msa_is_also_pending` |
| **T-1075** | Same seed; `claim(..., tier='msa')` returns the msa job only | `test_msa_claim_returns_the_msa_job_only_when_rental_is_also_pending` |
| **T-1076** | `build_fold_spec` for an msa job raises (does not return an ESMFold FoldSpec) | `test_build_fold_spec_for_an_msa_job_raises_not_an_esmfold_foldspec` |
| **T-1077** | local/rental `TIER_RECIPE` unchanged; `msa` is not a key | `test_local_and_rental_tier_recipe_unchanged` |

---

## Addendum 2026-09-04 — D-116 `stitch_readiness` gate (wave1 false-ready)

Acceptance tests for the hold-48 stitch-ready gate. Implemented in
`tests/test_hold48_stitch_readiness.py` against SQLite + the same `plan_tiles` /
`emit_tile_jobs` path as D-111. Each AT must be able to go red **without the gate**
(import/`ready` contract). No GPU. No Fly. `hold48_stitch.py` is not the subject.
Cite: D-111 UncoveredResidue refuse · wave1 FAIL 17 · parent 2817 · Architect ruling
2026-09-04.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1078** | Long parent with only 1 complete tile (Wave A / parent-2817 class) → `ready=False`, `missing` includes the rest | `test_long_parent_with_one_complete_tile_is_not_ready` |
| **T-1079** | Full cover, every expected tile complete + PDB + PAE → `ready=True` | `test_full_cover_complete_with_pae_is_ready` |
| **T-1080** | Full cover but one tile missing PAE → `ready=False` | `test_full_cover_missing_one_pae_is_not_ready` |
| **T-1081** | Mucin / no tiles → not ready, empty expected | `test_mucin_or_no_tiles_is_not_ready` |

---

## Addendum 2026-09-05 — D-124 / ADC-C-B `/adcs` Pipeline + Access

Acceptance tests for the ADC-C-B UI slice. Implemented in
`ui/src/adcCatalog.test.js`, `ui/src/components/AdcsView.test.jsx`,
`ui/src/components/AdcAccessPanel.test.jsx`,
`ui/src/components/AdcPipelineCard.test.jsx`, and
`ui/src/App.test.jsx`. Each AT must be able to go red. Prefers the A
APIs + fixtures — does not invent pipeline JSON rows.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1082** | `/adcs` default shelf is Approved and still consumes `listAdcs` / D-119 | `renders rows from the catalog payload and derives the count` |
| **T-1083** | Approved \| Pipeline tablist switches the index to `listPipelineAdcs` | `Pipeline shelf consumes GET /api/adcs/pipeline and not the approved catalog` |
| **T-1084** | Phase filter is the closed vocab and can empty the table honestly | `phase filter uses the Architect closed set and can empty the table` |
| **T-1085** | Access panel consumes `/api/adcs/access` and shows the required disclaimer as a ProvenanceField envelope | `sourced fields render ProvenanceField envelopes, including the disclaimer` |
| **T-1086** | Missing / failed access is an empty state, not invented trials | `failed access fetch is an honest miss, not invented NCT copy` |
| **T-1087** | `/adcs/pipeline/:id` consumes `getPipelineAdc`; unknown id is not a guess | `pipeline card renders a D-124 row; unknown id is not a 200-with-a-guess` |

---

## Addendum 2026-09-05 — D-125-A Kabsch restitch core

Acceptance tests for the Kabsch pre-stitch path. Implemented in
`tests/test_d125_kabsch.py` + updates to `tests/test_d125_kabsch_spec.py`.
Each AT must be able to go red **without** a live Fly query, GPU, or
restitch run. Fixtures stand in for tile PDBs. Cite: D-125 Spec
`docs/SPEC-kabsch-restitch.md` · D-111 `winning_tile` · refuse v1
defaults (`n_ca < 3`, RMSD `> 10.0 Å`, singular/degenerate covariance).
⚠ Kabsch feeds the existing assembler; it does not replace it. ⚠ Seams
are not scientifically solved.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1088** | Overlap Cα count `< 3` refuses align; `rmsd_angstrom` is null; no transformed PDB / no Kabsch `stitched.pdb` | `test_overlap_ca_lt_3_refuses_align` |
| **T-1089** | Kabsch RMSD `> 10.0 Å` refuses that seam and records the RMSD; no invented pose | `test_rmsd_gt_10_refuses_seam_and_records_rmsd` |
| **T-1090** | Singular / degenerate covariance (rank `< 2`) refuses align | `test_singular_covariance_refuses_align` |
| **T-1091** | Accepted seam transforms the moving tile and still calls `winning_tile` / `write_stitched` | `test_accepted_seam_transforms_and_feeds_winning_tile` |
| **T-1092** | Assembler `write_stitched` stays callable on untransformed tiles (A/B compare path) | `test_assembler_path_stays_callable_without_kabsch` |
| **T-1093** | CLI / writer refuse a parent id outside the 27-id inventory (not a Fly re-query) | `test_cli_refuses_parent_id_outside_inventory` |
| **T-1094** | Kabsch artifacts land under `kabsch/{parent_job_id}/` and do not overwrite an assembler `stitched.pdb` | `test_kabsch_dir_does_not_overwrite_assembler_pdbs` |

---

## Addendum 2026-09-05 — D-125-B UI dual-path honesty

Acceptance tests for the Kabsch-path review / Method addendum. Implemented
in `tests/test_d125_b_dual_path.py`, `tests/test_method_hold48_explainer.py`,
`ui/src/components/AssemblyReview.test.jsx`, and
`ui/src/components/MethodNote.test.jsx`. Each AT must be able to go red
**without** a live Fly query, GPU, or restitch run. Fixtures stand in for
A's `kabsch/{parent}/` tree. ⚠ B reads; it does not persist. ⚠ Seams are
not scientifically solved.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1095** | `### D-125-B —` exists in the living log | `test_d125_b_heading_exists_in_the_living_log` |
| **T-1096** | Missing sibling tree → honest empty; no invented RMSD / max Cα jump | `test_missing_sibling_tree_is_honest_empty_no_invented_rmsd` |
| **T-1097** | Present tree names both paths; persist stems `stitched` vs `kabsch/{parent}` do not collide | `test_present_tree_names_both_paths_and_stems_do_not_collide` |
| **T-1098** | Max Cα jump renders only if A wrote it; otherwise null | `test_max_ca_jump_is_honest_empty_unless_a_wrote_it` |
| **T-1099** | `assembly_review` carries `dual_path`; assembler downloads stay `stitched.*` | `test_assembly_review_carries_dual_path_empty_and_does_not_collide_stems` |
| **T-1100** | Method addendum names what Kabsch does / does not; forbids seams-solved language | `test_d125_b_method_addendum_names_does_and_does_not` |
| **T-1101** | Review card + MethodNote UI can go red for dual-path honesty | `names both paths and shows RMSD when Kabsch-path artifacts exist; jump stays empty if missing` · `adds a D-125-B Kabsch does / does-not addendum without claiming seams solved` |

---

## Addendum 2026-09-05 — D-126 overlap-confidence Kabsch Spec (docs pins) + future A

Hermetic **docs pin tests** for this Spec PR live in
`tests/test_d126_confidence_kabsch_spec.py`. They must be able to go
red **without** a live Fly query, GPU, restitch run, or any edit to
`core/hold48_kabsch.py`. Cite: D-126 Spec
`docs/SPEC-overlap-confidence-kabsch.md`.
⚠ The 10.0 Å refuse gate stays. ⚠ Trim / weight change the fit set,
not the gate. ⚠ Assembler + D-125 `kabsch/` stay callable.

**D-126-A** acceptance tests (this PR) must be able to go red for the
weighted fit, the trim loop, the refuse table, the no-overwrite rule,
full-overlap disclosure, all-or-nothing parent refuse, and the ops
report fields. Cite: `core/hold48_confidence_kabsch.py`.
⚠ The 10.0 Å refuse gate stays. ⚠ Assembler + D-125 `kabsch/` stay
callable. ⚠ `hold48_kabsch.py` is not edited.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1102** | `### D-126 —` exists; Spec file exists; algorithm name `overlap_confidence_kabsch_then_winning_tile`; 10.0 Å gate pinned; inventory of the five; hard stops; D-126-B later | `test_d126_heading_exists_in_the_living_log` · `test_spec_file_exists_and_names_algorithm` · `test_refuse_gate_stays_at_10` · `test_primary_five_inventory` · `test_hard_stops_and_not_ab` |
| **T-1103** | Weighted Kabsch uses \(w_i = \min(\mathrm{pLDDT}_A, \mathrm{pLDDT}_B)/100\) (clamp \(\ge \varepsilon\), **ε = 1e-3**) | `test_weighted_fit_uses_min_plddt_weights` · `test_pair_weight_is_min_plddt_over_100_clamped_at_epsilon` |
| **T-1104** | Trim loop: while \(n_{\mathrm{eff}} \ge 3\) and weighted RMSD \(> 10.0\) Å, drop highest-residual 10% (min 1), refit; cap 5 rounds | `test_trim_loop_drops_highest_residual_decile` |
| **T-1105** | Refuse table still gates at 10.0 Å after weight/trim (`overlap_ca_lt_3` / `rmsd_gt_10` / `singular_covariance`); fail closed | `test_refuse_table_stays_at_10_after_trim` |
| **T-1106** | Artifacts land under `confidence_kabsch/{parent_job_id}/` and do **not** overwrite assembler `stitched.pdb` or D-125 `kabsch/{id}/` | `test_confidence_kabsch_dir_does_not_overwrite_assembler_or_d125_tree` |

### Addendum — D-126 amendment 1 (Trinity red-team pins; same D-id)

Hermetic **docs pin tests** for the amendment live in the same
`tests/test_d126_confidence_kabsch_spec.py`. They must be able to go
red **without** a live Fly query, GPU, restitch run, or any edit to
`core/hold48_kabsch.py` / `hold48_stitch.py`. Cite: D-126 amendment 1
in `docs/README.md` + Spec §§1–3, §5, §8, §10.
⚠ The 10.0 Å refuse gate stays. ⚠ 0-of-5 recovered is allowed.
⚠ Confusion vs D-125 is a required **report** field, not a CI assert
against live ops.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1107** | Post-transform disclosure: `rmsd_full_overlap_angstrom` (unweighted, all overlap Cα) + `max_ca_jump_angstrom`; may be null on refuse-before-transform; A writes, B shows | `test_post_transform_full_overlap_disclosure` |
| **T-1108** | ε = **1e-3**; weighted RMSD = sqrt(Σ w_i ‖R p_i + t − q_i‖² / Σ w_i) on the fit set | `test_epsilon_and_weighted_rmsd_formula` |
| **T-1109** | Floor-then-Kabsch-then-trim order is fixed: (a) pLDDT floor 50 first if n≥3 remains; (b) weighted Kabsch; (c) trim loop | `test_floor_then_weighted_kabsch_then_trim_order` |
| **T-1110** | All-or-nothing parent refuse; cite `_clear_success_artifacts`; no partial `tileN_transformed.pdb` / D-126 `stitched.pdb` | `test_all_or_nothing_parent_refuse` |
| **T-1111** | Ops report must include confusion vs D-125 (`n_d125_pass_d126_refuse`); a drop is a **named finding**; not a CI assert against live ops | `test_no_regress_ops_report_fields` |
| **T-1112** | 0-of-5 recovered is an allowed outcome; do not loosen the gate or invent a blend | `test_zero_of_five_recovered_is_allowed` · `test_ops_success_report_names_a_drop_on_the_22_and_allows_zero_of_five` |

D-126-A **code** pins for amendment 1 (same ids; now executable, not
docs-only): `test_accepted_trim_still_discloses_full_overlap_rmsd_and_max_jump`
(T-1107) · `test_floor_then_kabsch_then_trim_order_floor_clears_outliers_before_trim`
(T-1109) · `test_all_or_nothing_parent_refuse_clears_partial_success`
(T-1110). `hold48_kabsch.py` sha256 stays pinned.

---

## Addendum 2026-09-05 — D-126-B UI triple-path honesty

Acceptance tests for the overlap-confidence review / Method addendum.
Implemented in `tests/test_d126_b_triple_path.py`,
`tests/test_method_hold48_explainer.py`,
`ui/src/components/AssemblyReview.test.jsx`, and
`ui/src/components/MethodNote.test.jsx`. Each AT must be able to go red
**without** a live Fly query, GPU, or restitch run. Fixtures stand in for
A's `confidence_kabsch/{parent}/` tree. ⚠ B reads; it does not persist.
⚠ Seams are not scientifically solved. ⚠ Default served PDB is assembler.
Cite: D-001 naming (`### D-126-B —` heading exists); D-126 Spec §6;
D-126-A `aa8aa02` / #241.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1113** | `### D-126-B —` exists in the living log (D-001 naming) | `test_d126_b_heading_exists_in_the_living_log` |
| **T-1114** | Missing `confidence_kabsch/` tree → do not imply a D-126 path; no invented RMSD / `n_ca_eff` / trim counts | `test_missing_confidence_tree_does_not_imply_d126_path_or_invent_metrics` |
| **T-1115** | Present tree names three paths; persist stems `stitched` vs `kabsch/{parent}` vs `confidence_kabsch/{parent}` do not collide; default served = assembler | `test_present_tree_names_three_paths_and_stems_do_not_collide` |
| **T-1116** | D-126 seam fields render from A's JSON (`n_ca`, `n_ca_eff`, weighted RMSD, full-overlap RMSD, max Cα jump, `trim_rounds`, `refuse_reason`); honest null when missing | `test_d126_seam_fields_are_honest_empty_unless_a_wrote_them` |
| **T-1117** | Refused seam stays fail-closed — no "fixed" badge; assembler / D-125 PDB is not a D-126 success | `test_refused_seam_is_fail_closed_and_not_presented_as_d126_success` |
| **T-1118** | Method addendum names what D-126 does / does not vs assembler vs D-125; forbids seams-solved language | `test_d126_b_method_addendum_names_does_and_does_not` |
| **T-1119** | Review card + MethodNote UI can go red for triple-path honesty | `names three paths and shows D-126 seam fields when confidence_kabsch artifacts exist` · `adds a D-126-B weighted/trimmed Kabsch does / does-not addendum without claiming seams solved` |

---

## Addendum 2026-09-05 — D-127 piecewise / domain-aware Kabsch Spec (docs pins) + future A

Hermetic **docs pin tests** for this Spec PR live in
`tests/test_d127_piecewise_kabsch_spec.py`. They must be able to go
red **without** a live Fly query, GPU, restitch run, or any edit to
`hold48_*.py`. Cite: D-127 Spec
`docs/SPEC-piecewise-domain-kabsch.md`.
⚠ The 10.0 Å refuse gate stays. Do not raise it. ⚠ No trim loop
(D-126 lie surface). ⚠ Assembler + D-125 `kabsch/` + D-126
`confidence_kabsch/` stay callable. ⚠ Method must surface D-127
when the path exists — not a silent code-only ship.

**D-127-A** acceptance tests (this PR) must be able to
go red for the per-piece weighted fit (no trim), the refuse table
including `no_domain_pieces` and `linker_jump_gt_10`, domain-snap
source identity, all-or-nothing parent refuse, and the no-overwrite
rule. Cite: `core/hold48_piecewise_kabsch.py` +
`scripts/piecewise_kabsch_restitch.py`.
⚠ The 10.0 Å refuse gate stays. ⚠ No rent in A. ⚠ `hold48_kabsch.py`
and `hold48_confidence_kabsch.py` are not edited. ⚠ Method / UI
remain D-127-B (A does not discharge Spec §7).

| ID | Check | Test name |
|----|-------|-----------|
| **T-1120** | `### D-127 —` exists; Spec file exists; algorithm name `piecewise_domain_kabsch_then_winning_tile`; 10.0 Å gate pinned; inventory of the three; hard stops; D-127-A/B later | `test_d127_heading_exists_in_the_living_log` · `test_spec_file_exists_and_names_algorithm` · `test_refuse_gate_stays_at_10` · `test_primary_three_inventory` · `test_hard_stops_and_not_ab` |
| **T-1121** | No trim loop; ε = 1e-3; per-piece weighted Kabsch uses \(w_i = \min(\mathrm{pLDDT}_A, \mathrm{pLDDT}_B)/100\) clamped \(\ge \varepsilon\) | `test_no_trim_loop_and_epsilon` |
| **T-1122** | Refuse table: piece `n_ca < 3` → `overlap_ca_lt_3`; piece weighted RMSD `> 10.0` → `rmsd_gt_10`; singular → `singular_covariance`; `no_domain_pieces`; linker jump `> 10.0` → `linker_jump_gt_10` | `test_refuse_table_names_piece_and_parent_reasons` |
| **T-1123** | Domain ends / intervals from the same emit domain-snap source (`domain_ends_span_relative` / UniProt Domain/Repeat) | `test_domain_snap_source_is_emit_source` |
| **T-1124** | Disclosure: per-piece `n_ca` / RMSD; parent `rmsd_full_overlap_angstrom` + `max_ca_jump_angstrom` after piecewise apply (null if refused before any transform); `linker_n` + `max_linker_ca_jump` | `test_disclosure_per_piece_and_parent_after_apply` |
| **T-1125** | Artifacts land under `piecewise_kabsch/{parent_job_id}/`; `algorithm=piecewise_domain_kabsch_then_winning_tile`; `decision=D-127`; do **not** overwrite assembler / D-125 `kabsch/` / D-126 `confidence_kabsch/` | `test_artifact_dir_is_sibling_piecewise_kabsch` |
| **T-1126** | Ship index distinguishes Spec vs future A/B; PLAN + ARCHITECTURE point at D-127 | `test_ship_index_distinguishes_spec_from_ab_build` · `test_plan_and_architecture_point_at_d127` |
| **T-1133** | Spec requires Method surface (stitch-path train; 8th-grade excerpt; never seams solved; default served = assembler); Method addendum is **mandatory** before calling D-127 “done”; forbids silent code-only | `test_method_surface_is_mandatory_not_silent_code_only` |

### D-127-A (this PR; T-1127–T-1132 now code)

Hermetic fixtures in `tests/test_d127_piecewise_kabsch.py`. No Fly.
No GPU. No restitch run of the 27. Cite Spec §1–§3 / §5 and existing
`winning_tile`. D-125 `write_kabsch_restitch`, D-126
`write_confidence_kabsch_restitch`, and the assembler stay
independently callable.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1127** | Piece `n_ca < 3` refuses (`overlap_ca_lt_3`); no transformed PDB | `test_piece_n_ca_lt_3_refuses` |
| **T-1128** | Piece weighted RMSD `> 10.0 Å` refuses (`rmsd_gt_10`) and records the RMSD | `test_piece_rmsd_gt_10_refuses` |
| **T-1129** | Singular / degenerate piece covariance refuses (`singular_covariance`) | `test_piece_singular_covariance_refuses` |
| **T-1130** | Zero domain pieces covering the overlap refuses parent (`no_domain_pieces`) | `test_no_domain_pieces_refuses_parent` |
| **T-1131** | Linker max Cα jump `> 10.0 Å` refuses parent (`linker_jump_gt_10`) | `test_linker_jump_gt_10_refuses_parent` |
| **T-1132** | Accepted pieces apply \(R, t\) only to moving-tile atoms in that domain; linkers inherit nearest N-terminal accepted piece; full accept feeds `winning_tile`; PAE null never 0; `piecewise_kabsch/` does not overwrite the three existing trees; no trim loop; CLI runs the 27; 0-of-3 allowed | `test_accepted_piece_applies_only_to_its_domain` · `test_linker_inherits_n_terminal_piece` · `test_full_accept_feeds_winning_tile` · `test_piecewise_dir_does_not_overwrite_assembler_d125_or_d126` |

### D-127-B (this PR; T-1134–T-1142) — UI four-path honesty + mandatory Method

Hermetic fixtures in `tests/test_d127_b_four_path.py`, plus vitest cases
in `ui/src/components/AssemblyReview.test.jsx` and
`ui/src/components/MethodNote.test.jsx`. No Fly. No GPU. No restitch run
of the 27. B **reads** A's `piecewise_kabsch/{parent}/` tree; B does not
persist and does not edit `hold48_piecewise_kabsch.py` (its bytes are
sha256-pinned by the suite). Cite Spec §6 (UI) and §7 (Method).

⚠ The D-127-specific hazard these exist for: a seam holds *k* domain
pieces, so a card that printed one seam number would re-create the D-126
lie surface — a flattering average hiding the per-domain disagreement —
inside the fix for it. **B renders per-piece rows and derives no
average.** ⚠ Spec §7 makes the Method addendum **mandatory**: D-127 is
not “done” without it, so T-1141 is a ship gate, not documentation
polish. ⚠ Default served = assembler. ⚠ 10.0 Å gate is reported, never
moved.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1134** | `### D-127-B —` exists in the living log (the check is the heading, not a citation of one); Trinity's LOCKED bar cites Spec §6 + §7 and D-127-A `e49bf34`; ship index carries the same bar | `test_d127_b_heading_exists_in_the_living_log` · `test_trinity_locked_bar_cites_d127a_and_spec_sections_six_and_seven` |
| **T-1135** | Missing `piecewise_kabsch/` tree → no D-127 path implied; no invented RMSD / piece counts / linker counts; the seam note names a fourth path only when the tree is on disk | `test_missing_piecewise_tree_does_not_imply_d127_path_or_invent_metrics` · `test_seam_note_names_the_fourth_path_only_when_the_tree_is_on_disk` |
| **T-1136** | Present tree → four paths named; persist stems do not collide (`stitched` vs `kabsch/{parent}` vs `confidence_kabsch/{parent}` vs `piecewise_kabsch/{parent}`); default served = assembler | `test_present_tree_names_four_paths_and_stems_do_not_collide` · `test_empty_block_stems_never_equal_assembler_d125_or_d126` |
| **T-1137** | Per-piece rows (`interval` / `n_ca` / weighted `rmsd_angstrom` / piece `refuse_reason`) render from A's JSON and are **never** collapsed into a seam average; parent `rmsd_full_overlap_angstrom` / `max_ca_jump_angstrom` / `linker_n` / `max_linker_ca_jump` render beside them; refuse-before-transform stays **null, never 0.00 Å**; a missing `pieces` list is an absence with a reason, not “0 pieces refused”; `R` / `t` are not surfaced as measurements | `test_per_piece_rows_render_from_as_json_and_are_not_averaged` · `test_parent_disclosure_and_linker_fields_render_when_a_wrote_them` · `test_refuse_before_transform_stays_null_never_zero` · `test_missing_piece_list_is_an_absence_with_a_reason_not_zero_pieces` · `test_project_seam_does_not_invent_numbers` · `test_projection_drops_the_rigid_transform_itself` |
| **T-1138** | Refused parent stays fail-closed: no “fixed” badge, and a leftover D-127 `stitched.pdb` is not a success (all-or-nothing); the 10.0 Å gate is reported, not re-declared by B | `test_refused_parent_is_fail_closed_and_not_presented_as_d127_success` · `test_ten_angstrom_gate_is_reported_not_moved` |
| **T-1139** | `assembly_review.four_path` carries the honest empty block and the read tree; D-125-B `dual_path` and D-126-B `triple_path` survive unchanged; assembler download stem stays `stitched` | `test_assembly_review_carries_four_path_empty_and_does_not_imply_d127` · `test_assembly_review_reads_fourth_sibling_tree_beside_assembler_dir` |
| **T-1140** | B does not re-implement persist, does not invoke A's writer or CLI, and does not edit A's module (`core/hold48_piecewise_kabsch.py` sha256-pinned); forbidden language stays parked across reader / reads / routes / JSX | `test_b_does_not_reimplement_persist_writer` · `test_b_does_not_invoke_a_restitch_of_the_twenty_seven` · `test_algorithm_modules_are_not_edited_by_this_ui_pr` |
| **T-1142** | **D-127 OPS honesty (Matt GO via Emma, amendment 1).** Method discloses the run **as recorded** — PASS 17 / REFUSE 10 / FAIL 0 at tip `e49bf34`; `recovered_of_primary_three` = **0** with 2939 `linker_jump_gt_10` / 3272 `rmsd_gt_10` / 3432 `no_domain_pieces`; the refuse histogram (`linker_jump_gt_10` ×7 · `rmsd_gt_10` ×2 · `no_domain_pieces` ×1) with its parent ids; the **named regress** (5 vs D-125, 7 vs D-126, `n_d126_refuse_d127_pass` = 0) beside the accept count, never buried under it; **D-126 named plainly as the best experimental path so far**; no gate loosened and the served path never auto-flipped; 17 accepted = 17 **recorded** outcomes, not solved joins; provenance names the GO and disclaims re-measurement; and this PR ships no ops run, no revised stitch Spec, and no Fly POST | `test_ops_figures_are_internally_consistent_before_they_are_quoted` · `test_method_discloses_the_d127_ops_run_and_its_named_regress` · `test_method_says_plainly_that_d126_remains_the_best_path_so_far` · `test_method_refuses_to_loosen_a_gate_or_flip_the_served_path` · `test_ops_disclosure_names_its_provenance_and_disclaims_measurement` · `test_this_pr_ships_no_ops_run_no_revised_spec_and_no_fly_post` · `discloses the D-127 OPS run with its named regress, not an accept count alone` · `says plainly that D-126 remains the best path, keeps every gate, and never flips the served path` |
| **T-1141** | **Mandatory Method (Spec §7).** Addendum names the four-step stitch-path train in order, the D-126 full ≫ weighted lesson (28–68 Å on 2939 / 3272 / 3432), per-UniProt-domain fit with no trim loop and linker inherit, the refuse table with the **10.0 Å gate staying**, seam numbers as measurements rather than a verdict, default served = assembler, and honest empty when the tree is missing — without claiming seams solved and **without gutting** the D-121 / D-125-B / D-126-B sections | `test_d127_b_method_addendum_names_the_stitch_path_train` · `test_d127_b_method_addendum_names_the_refuse_table_and_keeps_the_gate` · `test_d127_b_method_addendum_names_seam_disclosure_as_measurement` · `test_method_addendum_does_not_gut_d121_d125b_or_d126b` · `test_method_obligation_is_recorded_as_discharged_by_this_pr` · `names four paths and shows one row per domain piece when piecewise_kabsch artifacts exist` · `adds the mandatory D-127-B addendum naming the whole four-step stitch-path train` |

---

**End of Test Plan**

