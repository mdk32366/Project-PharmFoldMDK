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

## Addendum 2026-09-09 — D-147 `ecd_intermittent` on the census structural ranking surface

### D-147 (this PR; T-1254) — the span that is one loop of several, said on the surface that ranks it

Acceptance tests in `tests/test_d147_ecd_intermittent_flag.py`, with
`tests/test_d144_census_structural_rank.py`'s `flag_meaning` assertion **widened in place** (it
read `== set(cs.FLAG_MEANING)`, which was right while one module owned every flag), the two
sha256 pin tables in `tests/test_d145_bake_structural_loader.py` /
`tests/test_d146_track_b_live_api_copy.py` **moved for two files and left alone for the other
eight**, and `ui/src/components/MethodNote.censusStructural.test.jsx` extended. Hermetic: every
assertion is a property of the tree. Cite `### D-147`.

⚠⚠ **What these tests CANNOT establish, first rather than last: no test here contacts the deployed
application.** The served flag and the served count are proved against a seeded SQLite run plus the
committed `data/census/span_segments.csv`; the deployed answer becomes true on release, not on
merge. The bridge between the fixture-sized proof and the 3,467-row population is the **bijection**
check and the **content-hash** check — properties of two committed files, not observations of Fly.
No `DATABASE_URL` and no Fly credential exist in this build, so nothing here could have read or
written the live route.

⚠⚠ **THE FIXTURE POPULATION IS FIVE REAL ACCESSIONS, AND THAT IS `A-017` RATHER THAN CONVENIENCE.**
A fixture of invented ids (`P00001`…, as `D-144`'s own suite uses) has **no row in the committed
`span_segments.csv`**, so the join would answer `unknown` for every one of them and **every flag
assertion would pass against a payload in which the flag never appears.** The population is
therefore `O75899` (intermittent, 4 segments — and **rank 1 of the live rank**), `P51677`
(intermittent, and its 34 aa span is **below** the 200 aa cap, so a penalty on the flag would move
its score where a saturated row would hide it), `P05362` (contiguous), `Q9Y2I2`
(`no_accepted_segment`, never folded) and `Q96NY8` (contiguous, the NECTIN4 reference sink).

⚠ **The score-immobility pins are computed BY HAND from `membrane × ecd × model`**, never read back
out of the code under test — a pin derived from the implementation cannot detect the implementation
changing (`F-026`).

⚠⚠ **ONE TEST HERE EXISTS BECAUSE A REVERT PROOF FOUND THE HOLE IT FILLS, and that is recorded in
`### D-147` rather than smoothed over.** The suite originally proved score-immobility two ways —
hand-computed pins on the served rows, and `D-144`'s AST guard on the **formula's** product
expression. A revert that multiplied `score_ecd` by `0.9` **in the reader**, for flagged rows only,
was caught by the pins and by two sha256 pins and by **nothing else**: the AST guard reads
`core/census_structural.py`, which that revert never touched, and
`test_the_flag_does_not_reach_the_score_for_the_real_population` calls the formula directly rather
than the route. **A serve-time join is a serve-time place to apply a penalty**, so
`test_the_served_score_is_the_persisted_score_for_every_factor_and_the_rank` was added at that
seam: served score, three factors, span, rank, pLDDT and class must equal the persisted row's,
field by field, over rows that actually wear the flag.

⚠ **And one guard that a revert proved does NOT bite, recorded here because a green test read as
proof is worse than no test.** `D-144`'s `test_the_scored_product_is_exactly_the_three_factors_and_
nothing_else` pins the expression `membrane * ecd * model`; a penalty applied *inside* `score_ecd`
leaves that expression untouched and the guard **stays green**. The formula-side revert was caught
by this addendum's own AST parameter-list pin and by the `formula_version` pin instead. Widening
D-144's guard belongs to that entry's ruling, not this one.

⚠ **T-1254 is the next id above the highest spent (`T-1253`, D-146), and `T-1231` / `T-1232` are
left UNSPENT rather than back-filled**, on the reasoning D-144, D-145 and D-146 all recorded: a hole
is cheap, a second claim on an id is not.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1254** | **The census structural ranking surface stops presenting a loop as an ectodomain, and the score does not move.** An `intermittent` row carries `ecd_intermittent`, a `contiguous` row does not, and ⚠⚠ a `no_accepted_segment` row does **not** — the GO's hard stop, asserted as a count that moves by exactly **125** if the GPI rows are collapsed in; the three topology words are counted **separately** and reconcile to **3,467** (1,649 / 1,693 / 125) with no fourth word in the artifact; the derivation is a **bijection** with `census_manifest.v7.csv` (0 either way) and is **stamped against the same population by content hash** — `fd80d65df8b3…3f970d07`, the `population_sha256` `D-146` recorded from the live run — with `core.derived_freshness.check` returning `fresh`; the served row carries the **same four `F-037` field names** as `/api/census/{id}` (`topology`, `segment_count`, `extracellular_total_aa`, `discarded_aa`), read off `app/reads.py`'s source rather than retyped; `component_counts.by_flag.ecd_intermittent` **equals the rows that wear the flag** and is **counted from the served rows, not read from `span_segments.provenance.json`** (whose own `"intermittent": 1649` is asserted to be the tempting shortcut, and `1649` is asserted to be no integer constant in either module — `F-026`); the flags overlay is **additive only** — persisted flags survive as a prefix, proved on `O75899`, which keeps `ecd_saturated` **and** gains the new flag — and a persisted duplicate is **not emitted twice**; ⚠⚠ **every pinned `structural_score` is unchanged and so is the rank order**, **the SERVED score / three factors / span / rank / pLDDT / class equal the PERSISTED row's field by field** over rows that wear the flag (the guard a revert proof found missing), `structural_score` is unchanged over **all 1,649** flagged rows of the real population, `core/census_structural.py` never learns the word `topology` (AST: no import of the supplier, `structural_score`'s parameter list pinned, no `topology` name in the body, and the flag not declared there), and **`formula_version()` is still `c859da97f73d`** with the module's sha256 unmoved; the loader is **byte-identical**, **no migration** is added (`0012` still the head) and the loader never learns the flag; the segment supplier's import set is **pinned** and cannot reach `core.scorer` / the fitter / the three cohort-82 tables (`D-079` am. 1 ruling 5); the served `flag_meaning` is the **union** of both suppliers with every flag that can reach a row present, and the `ecd_intermittent` meaning denies **score composition** and **internalization** by name while `formula.excluded_factors` still reads *"never measured by this project for any protein"*; `segment_topology` names its `source`, its `posture` (committed file, `--load`, supersede, deployed tree), the verdict, `by_topology`, both counts and `agrees_with_persisted`, and is present on a **`not_run`** payload too; a **stale** and an **unstamped** derivation each withhold every topology and flag nothing — reporting the **verdict** rather than `unknown`, and ⚠ **still serving every score**; `0` is admitted as a measurement where the formula's `_whole_residues` refuses it; the MethodNote paragraph carries three denials individually (does not change the score · not internalisation · not `GPI / no segment`) and ⚠⚠ **types no population-sized number**, naming `component_counts.by_flag.ecd_intermittent` instead — `D-050` / `D-051` **Constraint A**, and `### D-147` records that this reversed the entry's own first draft (D-129-C); `CensusTable.jsx` still has **no rank column** and the ranking route still has **no UI consumer** (three non-test files name it, none fetches it), so no badge shipped; `### D-147` exists **exactly once** and leads the log (**the check is the heading, not a citation of one** — D-062 / method-note item 7), leads with the disqualifying fact that **rank 1 is intermittent**, records the composition / bijection / content hash / 92,709 discarded residues, keeps every hard stop, carries a **deep-learning justification** naming ESMFold / pLDDT / `score_model` while stating it adds no deep learning, and states what this build could not verify; the **ten** id guards **name** `### D-147` and **bar** `### D-148` (bar-or-name, never neither, never a `>=`), with the three cross-guard checks that held the D-147 bar **as data** widened to require *names 146, names 147, bars 148*; the `D-147` RESERVED row is retired **marker-safe** (another suite locates it by literal marker) with a `D-148` row added and the next-free pointer moved in the same commit; the citation invariant still returns `['D-131', 'F-067']`; `ARCHITECTURE.md` and this Test Plan are current | `test_an_intermittent_row_carries_the_flag` · `test_a_contiguous_row_carries_no_flag` · `test_a_no_accepted_segment_row_is_not_intermittent_and_wears_no_flag` · `test_the_three_topologies_are_counted_separately_and_reconcile` · `test_the_committed_derivation_is_a_bijection_with_the_population` · `test_the_derivation_is_stamped_against_the_same_population_the_run_serves` · `test_the_top_of_the_live_rank_is_an_intermittent_row` · `test_zero_is_a_measurement_and_a_blank_cell_is_not` · `test_the_flag_rides_on_the_served_ranking_row` · `test_the_served_row_carries_the_same_four_field_names_as_the_census_card` · `test_the_by_flag_count_equals_the_rows_that_wear_the_flag` · `test_the_by_flag_count_is_counted_from_the_rows_and_not_read_from_the_provenance_file` · `test_the_served_count_matches_the_committed_csv_over_the_real_population` · `test_the_join_never_drops_or_reorders_a_persisted_flag` · `test_the_flag_is_never_emitted_twice_if_a_loader_ever_persists_it` · `test_the_payload_names_the_source_and_the_posture_of_the_join` · `test_the_not_run_payload_still_carries_the_segment_topology_block` · `test_the_structural_score_is_unchanged_for_every_pinned_row` · `test_the_served_score_is_the_persisted_score_for_every_factor_and_the_rank` · `test_the_flag_does_not_reach_the_score_for_the_real_population` · `test_the_formula_module_never_learns_what_a_topology_is` · `test_the_formula_version_pin_did_not_move_and_matches_the_live_run` · `test_no_load_no_migration_and_no_loader_edit_ships_here` · `test_the_learned_cohort_82_scorer_is_not_reachable_from_the_segment_supplier` · `test_the_flag_meaning_denies_score_composition_and_internalization` · `test_the_excluded_factors_still_call_internalization_never_measured` · `test_every_flag_that_can_reach_a_served_row_has_a_meaning_in_the_payload` · `test_the_method_note_paragraph_carries_the_denials_and_types_no_count` · `test_the_census_table_still_has_no_rank_column_and_no_ranking_table_shipped` · `test_a_stale_derivation_withholds_the_flag_rather_than_guessing` · `test_an_unstamped_derivation_is_neither_fresh_nor_stale_and_still_flags_nothing` · `test_a_stale_derivation_is_reported_on_the_payload_and_flags_nothing` · `test_the_log_entry_exists_exactly_once_and_leads_the_log` · `test_the_entry_leads_with_the_disqualifying_fact_about_its_own_surface` · `test_the_entry_records_the_measured_composition_and_the_join_it_rests_on` · `test_the_entry_keeps_the_hard_stops_from_the_go` · `test_the_entry_carries_a_deep_learning_justification_that_names_the_model` · `test_the_entry_states_what_this_build_could_not_verify` · `test_the_entry_records_the_reversed_decision_rather_than_rewriting_it` · `test_the_next_free_integer_is_named_and_barred_across_every_guard` · `test_the_reserved_row_is_retired_marker_safe_and_148_has_a_row` · `test_the_citation_invariant_holds_on_this_branch` · `test_the_architecture_doc_records_the_shipped_shape` · `test_the_test_plan_carries_the_d147_addendum_on_an_id_nobody_else_holds` · UI: `MethodNote.censusStructural.test.jsx` (`the intermittent paragraph`, `the three denials`, `types no count`) |

---

## Addendum 2026-09-09 — D-146 Track B stops denying the live census rank surface

### D-146 (this PR; T-1253) — the copy contradiction between `/about` and `/method`

Acceptance tests in `tests/test_d146_track_b_live_api_copy.py`, with
`tests/test_d143_track_b_structural_only.py` **flipped in one clause** (T-1226's offline
requirement), `tests/test_about_paper_extract.py` widened, and the two UI suites
(`ui/src/aboutPaper.test.js`, `ui/src/components/AdcContext.test.jsx`) flipped the same way.
Hermetic: every assertion is a property of the tree. Cite `### D-146`.

⚠⚠ **What these tests CANNOT establish, first rather than last: no test here contacts the deployed
application.** The amended sentence asserts something about a running system; the suite asserts an
agreement between two documents. **If Fly began answering `result_status: not_run` tomorrow, every
test would stay green and the copy would be false again.** That is deliberate — a test that curls
production is a monitor, reddens for reasons no commit caused, and trains its readers to re-run it.
The live read that authorises the amendment is recorded in `### D-146` with its fields
(`result_status: valid`, 3,467 rows, run 1 at `2026-09-09T06:02:08Z`, GABBR2 `O75899` at 0.8443)
and is explicitly **one unauthenticated GET at one minute**.

⚠ **The defect being repaired is a REQUIRED-STRING assertion that had become a required lie.**
T-1226 listed *"it runs offline: it is not a ranked surface in this application"* among the clauses
Track B must carry. `D-144` and `D-145` made it false, and the test went on defending it — green,
specific, and pointed at the wrong thing. The clause is **flipped in place**, not deleted, so the
thread back to what it used to require survives.

⚠ **T-1253 is the next id above the highest spent (`T-1252`, D-145), and `T-1231` / `T-1232` are
left UNSPENT rather than back-filled**, on the reasoning D-144 and D-145 both recorded: a hole is
cheap, a second claim on an id is not.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1253** | **Track B agrees with MethodNote, in both directions and in both files.** The retired clause is **absent** from the owner Doc's Track B sentence and from `ui/src/aboutPaper.js` entirely (including its comments), and survives **exactly once** — inside the Doc's dated amendment note, marked false and pointing at what replaced it; the sentence in **both** files names `served live by this application`, `/api/census-structural-ranking`, *the database and that route are the record*, `review lens` / *never the source of truth*, `STRUCTURAL_ONLY`, *not a shortlist* and *not the cohort-82 learned scorer*; `TRACK_B` is still a **character substring** of the Doc (D-123 dec 4); **the guard is proved to bite against a counterfeit** — the shipped sentence with the denial re-inserted, and with the route deleted, are both rejected by the same function that passes the shipped one (`A-016` / `A-017`); everything D-143 pinned is **unchanged** (no `cancer ×`, no `/ normal risk`, `0.5 neutrals` still refused, the four exclusions, the 3,467-row scope, the Later GO); `MethodNote.jsx` is **byte-identical** and still carries its source-of-truth paragraph; Track B appears on **no scorer surface** and `/census` gains **no rank column**; **ten files are sha256-pinned** on LF-normalised bytes (formula, reader, loader, migration `0012`, `read_routes`, `models`, `Dockerfile`, `.dockerignore`, `MethodNote.jsx`, `core/scorer.py`), so *"copy amend only"* is a property rather than an intention; `### D-146` exists **exactly once** and leads the log (**the check is the heading, not a citation of one** — D-062 / method-note item 7), leads with what the gate cannot check, records the live read **and** what that read is not, quotes the contradiction from **both** surfaces, keeps every hard stop, and carries a **deep-learning justification** naming ESMFold / pLDDT / `score_model` while stating it adds no deep learning; the nine id guards **name** `### D-146` and **bar** `### D-147` (bar-or-name, never neither, never a `>=`); the `D-146` RESERVED row is retired **marker-safe** (two other suites locate it by literal marker) with a `D-147` row added and the next-free pointer moved in the same commit; the citation invariant still returns `['D-131', 'F-067']`; `ARCHITECTURE.md` and this Test Plan are current | `test_the_offline_denial_is_gone_from_both_files` · `test_both_files_name_the_live_route_and_the_review_lens` · `test_the_extract_is_still_a_character_substring_of_the_owner_doc` · `test_the_guard_catches_a_restored_denial_and_a_deleted_route` · `test_method_note_still_carries_the_source_of_truth_paragraph_it_was_right_about` · `test_track_b_is_not_pasted_into_a_scorer_surface` · `test_the_census_table_still_has_no_rank_column` · `test_no_formula_schema_route_loader_or_image_byte_moved` · `test_the_retired_biology_composite_did_not_come_back_with_the_route` · `test_the_paper_carries_a_dated_amendment_note_for_this_entry` · `test_the_d143_amendment_note_is_left_standing` · `test_the_retired_clause_survives_only_as_the_docs_dated_quotation` · `test_the_log_entry_exists_exactly_once_and_leads_the_log` · `test_the_entry_leads_with_what_the_gate_cannot_check` · `test_the_entry_records_the_live_read_that_authorises_the_amendment` · `test_the_entry_states_the_contradiction_it_repairs_from_both_sides` · `test_the_entry_keeps_the_hard_stops_from_the_go` · `test_the_entry_carries_a_deep_learning_justification_that_names_the_served_output` · `test_the_next_free_integer_is_named_and_barred_across_every_guard` · `test_the_reserved_row_is_retired_marker_safe_and_147_has_a_row` · `test_the_citation_invariant_holds_on_this_branch` · `test_the_architecture_doc_no_longer_says_the_track_b_order_is_offline` · `test_the_test_plan_carries_the_d146_addendum_on_an_id_nobody_else_holds` · `test_the_sentence_names_its_exclusions_rather_than_defaulting_them` (flipped clause) |

---

## Addendum 2026-09-09 — D-145 the D-144 loader is baked into the serving image

### D-145 (this PR; T-1252) — image permanence for the structural-rank loader

Acceptance tests in `tests/test_d145_bake_structural_loader.py`, with the pre-existing
image suites widened in place (`tests/test_image_contents.py`,
`tests/test_serving_image_contents.py`). Hermetic and **artefact-reading**: every
assertion is a property of the `Dockerfile`, `.dockerignore`, `fly.toml` or the tree —
**no GPU, no fold, no network, no database, no docker build**. Cite `### D-145` and
Trinity Spec `@0.0` (Matt / Kaylee ops scar).

⚠⚠ **What these tests CANNOT establish, and it is the first thing in the addendum
rather than a caveat at the end: there is no docker daemon in the gate**, so nothing
here proves the *built image* contains the file. They assert the **declaration** — the
`Dockerfile` names it, the build context admits it, the file exists so the `COPY` is not
a typo. **The build is the other half of the proof**, and a `COPY` of a path
`.dockerignore` excludes fails it loudly. This is the same limit
`tests/test_serving_image_contents.py` has stated about the ingest since `b2196e9`;
restated because inheriting a caveat silently is how it stops being read.

⚠ **T-1252 is the next id above the highest spent (`T-1251`, D-144), and `T-1231` /
`T-1232` are left UNSPENT rather than back-filled** — D-144's addendum declined the same
gap for the same reason: this branch cannot tell whether an in-flight lane holds them,
and filling a hole left by a branch it cannot see is precisely the collision this repo
has recorded four times in six days. A hole is cheap; a second claim on an id is not.

⚠⚠ **The revert the pre-existing suite could NOT catch, which is why this addendum
exists.** `test_only_the_allowed_scripts_are_copied` is a subset assertion, and **the
empty set is a subset of everything** — delete the loader's `COPY` line and it stays
green. That is exactly the failure the ops scar was: a rebuild drops a hand-placed file,
the deploy is green, the gate is green, and the script is simply not there. The property
the GO asks for needed a **positive** assertion, and the revert now reddens
`test_the_loader_is_baked_in_and_this_is_the_assertion_the_scar_needed` and both
parametrised `COPY`-line checks.

⚠ **Revert proof, three guards, each red read at the assertion (`A-016`).** Delete the
loader `COPY` → the two presence tests fail on the missing instruction, and the subset
guard stays green (confirmed, not assumed). Broaden to `COPY scripts/ ./scripts/` →
**four** guards fail on the directory bar. ⚠⚠ **And two that read as the relevant ones
stay GREEN:** `test_no_writing_script_reaches_the_image` and
`test_the_fitter_is_named_and_absent` both pass, because a directory COPY yields the
source token `scripts/` and never `scripts/fit_scorer.py`, so the by-name intersection
against `WRITERS` is empty. **The fitter is protected by the directory bar, not by the
guard that names it** — measured under revert and recorded in `### D-145`, unnumbered,
because `F-050` is reserved for the guard-direction sweep. Remove
`!scripts/census_structural_rank.py` from `.dockerignore` → the context test fails on
the set difference, which is the closest a daemon-less gate gets to reproducing the
build failure itself.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1252** | **The loader is IN the image, the directory is still OUT, and nothing was run.** Both `COPY scripts/…` lines are present in the runtime stage **verbatim and per file**; `scripts/` is never copied wholesale and `fit_scorer` appears in no instruction (`D-079` dec 1); `.dockerignore` still excludes `scripts/` and re-includes **exactly the two named files** — never a pattern; `data/` is copied **exactly once** as the whole directory, so no CSV is re-copied (`F-014`); the machine paths are **derived, not asserted as prose** — `WORKDIR /srv` plus the loader's own two-parents rule gives `/srv/scripts/census_structural_rank.py` and `/srv/data/census/census_manifest.v7.csv`, and `fly.toml`'s mount stays `/data/artifacts` so the image dir and the Volume cannot be confused; **six D-144 files are sha256-pinned** on LF-normalised bytes (formula, loader, reader, migration `0012`, `read_routes`, `models`), so *"no formula/schema/route change"* is a property rather than an intention; **no `RUN`/`CMD`/`ENTRYPOINT` and no workflow executes the loader** and `CMD` is still uvicorn; no torch/transformers/worker entered the image; each shipped script's **transitive** first-party import graph reaches no unshipped `scripts.` module (the `ModuleNotFoundError` production found once already); `### D-145` exists **exactly once** and leads the log (**the check is the heading, not a citation of one** — D-062 / method-note item 7), leads with the absent docker daemon and the absent Fly credential, labels the ops scar **reported** rather than observed and names `2170bd8`, names `b2196e9` as the two-line precedent, carries a **deep-learning justification** that names ESMFold / pLDDT / `score_model` **and states it adds no deep learning**, and **records that its own citation-invariant prediction was wrong**; the eight id guards **name** `### D-145` and **bar** `### D-146` (bar-or-name, never neither, never a `>=`); the `D-145` RESERVED row is retired **marker-safe** (not struck — `tests/test_d144_…py:916` locates it by literal marker) with a `D-146` row added; the citation invariant returns `['D-131', 'F-067']`; `ARCHITECTURE.md` and this Test Plan are current | `test_the_runtime_stage_names_each_baked_script_as_its_own_copy` · `test_the_loader_is_baked_in_and_this_is_the_assertion_the_scar_needed` · `test_the_scripts_directory_is_never_copied_and_the_fitter_never_ships` · `test_the_build_context_re_includes_exactly_the_two_named_files` · `test_no_csv_is_re_copied_for_the_loader` · `test_the_loader_and_its_population_resolve_under_srv_without_a_path_constant_moving` · `test_the_fly_volume_is_not_the_images_data_directory` · `test_no_formula_schema_or_route_byte_moved` · `test_nothing_in_this_pr_runs_the_loader` · `test_no_gpu_world_and_no_worker_entered_the_image` · `test_the_log_entry_exists_exactly_once_and_leads_the_log` · `test_the_entry_leads_with_what_this_build_could_not_verify` · `test_the_entry_records_the_ops_scar_as_reported_rather_than_observed` · `test_the_entry_states_the_two_line_shape_and_its_precedent` · `test_the_entry_carries_a_deep_learning_justification` · `test_the_entry_states_the_hard_stops_from_the_go` · `test_the_entry_records_that_its_own_invariant_prediction_was_wrong` · `test_the_next_free_integer_is_named_and_barred_across_every_guard` · `test_the_reserved_row_is_retired_marker_safe_and_146_has_a_row` · `test_the_citation_invariant_holds_on_this_branch` · `test_the_architecture_doc_records_the_baked_paths` · `test_the_test_plan_carries_the_d145_addendum_on_an_id_nobody_else_holds` · `test_the_runtime_stage_copies_both_permitted_scripts_by_name` · `test_the_scripts_directory_is_still_never_copied_wholesale` · `test_only_the_allowed_scripts_are_copied` · `test_dockerignore_excludes_scripts_and_re_includes_only_the_allowed` · `test_the_allowed_scripts_exist_so_a_copy_cannot_silently_be_a_typo` · `test_a_shipped_script_needs_nothing_from_scripts_that_is_not_shipped` |

---

## Addendum 2026-09-09 — D-144 census STRUCTURAL rank in the DB and on its own route

### D-144 (this PR; T-1243–T-1251) — the offline census ranking stops being a spreadsheet

Acceptance tests in `tests/test_d144_census_structural_rank.py`. Hermetic — SQLite
`create_all` + a dummy queue, every fixture under `tmp_path`; **no GPU, no fold, no
network, no real database, and no scorer refit**. Cite `### D-144` and the **Matt GO
2026-09-08 ~21:35 PT via Emma** (*"Spreadsheet = review lens only, NOT source of
truth"*).

⚠⚠ **RENUMBERED T-1225–T-1233 → T-1243–T-1251, and the collision is recorded rather
than tidied away** (method-note item 4: record the provenance chain, including the
version that was wrong). This addendum was written against `main` at `30f402f`, where
**T-1218 was the highest spent id**, and took the next nine. Three PRs then merged while
it was open — **D-143** (`f243f93`) taking **T-1225–T-1229**, its collision amendment
(`22ce1d7`) taking **T-1234**, and **D-142** (`b7d933f`) taking **T-1235–T-1242** — so
the original range was spent **twice over** by the time this branch rebased. The nine ids
move to the first clear run above the highest spent id. ⚠ **T-1230–T-1233 are left
UNSPENT rather than back-filled:** this branch cannot tell whether an in-flight lane
holds them, and filling a gap left by a branch it cannot see is precisely the collision
this repo has now recorded four times in six days (D-139/#263, D-140, D-143/#267, and
this). A hole is cheap; a second claim on an id is not.

⚠ **The live state these tests do NOT change: `result_status: not_run`.** No
`DATABASE_URL` reached this build (`env | grep -iE 'DATABASE|FLY|POSTGRES|PGHOST'`
returns nothing; `which fly flyctl psql` returns nothing), so no run has been loaded
and the route serves the not-run payload — with its disclaimer — until an operator runs
`scripts/census_structural_rank.py --load`.

⚠⚠ **The load-bearing negative: `/api/ranking` and the cohort-82 tables are
untouched.** T-1249 captures the ranking payload **before** any census structural run
exists and asserts it **equal** afterwards, which is the regression the GO asks for
stated as a property rather than as an intention.

⚠ **Revert proof: four of five guards bit; the fifth is recorded.** Wiring
`is_reference` into the score as a no-op multiplication left **50 passed** — the test
compared two products and a `× 1.0` leaves them equal. Fixed by also asserting the
three components individually and that the flag reaches only the flag list; the same
revert now reddens T-1244.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1243** | **The locked formula at its edges.** `surface` → 1.0 and everything else (incl. `unclassified` / `class_conflict`) → 0.2; `score_ecd` saturates at **200 aa** as a **cap not a cutoff** (199 → 0.995, 442 → 1.0) and is **0** for a missing/zero/unusable span; `score_model` has **three** cases (`plddt/100`, **0.8** for a fold whose pLDDT was not persisted — F-042, **0.3** for no fold — a PENALTY, and the two are never pooled); the **golden** GABBR2/`O75899` row reproduces **0.8443** with `census_class` and `span_aa` **read from the committed manifest**, and its docstring states that `mean_plddt = 84.43` is **not on disk here** | `test_surface_earns_the_full_membrane_factor_and_everything_else_earns_02` · `test_the_ecd_factor_saturates_at_200_and_is_a_cap_not_a_threshold` · `test_a_missing_or_zero_span_scores_zero_and_is_never_imputed` · `test_score_model_has_three_cases_and_no_fold_is_a_penalty_not_a_neutral` · `test_the_golden_row_reproduces_the_offline_value_for_gabbr2` |
| **T-1244** | **No invented factor, and the reference sink never enters the score.** No numeric constant **0.5** survives in the formula module, the loader or the reader — checked on the **AST**, because all three *discuss* the neutrals they refuse and a grep is satisfied by that prose (F-044); the four excluded factors are named **with a reason each** and none is a component of `StructuralScore`; `is_reference` changes neither the product nor any of the three factors | `test_no_half_neutral_is_a_numeric_constant_anywhere_in_the_formula_or_the_loader` · `test_the_four_excluded_factors_are_named_with_reasons_and_are_not_computed` · `test_the_reference_flag_never_enters_the_score` |
| **T-1245** | **The sink is a JOIN, and it bites.** The 12 reference antigens come from `data/adc_reference_mapping.csv` via `core.adc_reference.load_mapping()`, **no accession is typed into the module** (checked over its string constants), **12 of 12** are present in the population, and a reference row sorts **after every candidate** however high it scores — in the end-to-end load, NECTIN4 holds the **top score in the population** and ranks **last** | `test_the_reference_sink_is_joined_from_the_curated_file_and_never_typed_here` · `test_every_reference_antigen_is_actually_in_the_population` · `test_references_sink_below_every_candidate_however_high_they_score` |
| **T-1246** | **Population from a file, folds from the database.** The population is the manifest's **3,467** rows with class, span and tranche on every one; the fold half is the `protein_analyses` join at `cohort_tranche > 0`, so a **cohort** row for the same accession supplies **no** fold (D-081), a `tiles_only` representative is **not** a fold (D-118 / D-134), and a never-folded protein is **ranked at 0.3, not dropped**; ties break by accession so two runs agree | `test_the_population_is_the_manifest_and_carries_class_span_and_tranche` · `test_the_load_computes_from_the_db_join_and_ranks_the_whole_population` · `test_a_tiles_only_representative_is_not_counted_as_a_fold` · `test_a_fold_with_no_persisted_plddt_is_08_and_not_pooled_with_no_fold` · `test_ties_are_broken_by_accession_so_two_runs_agree` |
| **T-1247** | **Idempotent replace, and a refusal instead of a fabricated score.** Two loads leave **exactly one `valid`** run, the same ranks, one row per protein per run (the UNIQUE grain — F-021), and the superseded run **names its replacement**; the run row records the population's **path and sha256**, the source-hash `formula_version` and the breakdown beside the totals; a pLDDT the formula cannot read **stops the run naming the accession** rather than scoring it as unfolded (F-020); pruning is **explicit** and a load never deletes | `test_persisting_twice_leaves_exactly_one_valid_run_and_the_same_ranks` · `test_the_run_row_records_its_population_by_path_and_hash` · `test_an_unreadable_plddt_refuses_the_run_instead_of_scoring_it_as_unfolded` · `test_a_zero_to_one_plddt_is_refused_rather_than_divided_again` · `test_pruning_is_explicit_and_a_load_never_deletes_a_superseded_run` · `test_the_summary_separates_candidates_from_references_and_carries_breakdowns` |
| **T-1248** | **The route: disclaimer, `n_candidates`, three factors, and `not_run` that still says it.** `GET /api/census-structural-ranking` is open (D-034), serves the latest **`valid`** run in rank order with `STRUCTURAL_ONLY` on the **header and every row**, `n_candidates` at the top level **and** on the run, the three factors on every row whose product is checked against the total, **no `analysis_id`** on the wire (the cohort-leak stop), the formula **with its exclusions**; a `superseded` or `invalid` run is **never** served; and with no run at all the payload is `not_run` with `n_candidates: 0`, the disclaimer and the separation statement **still present** | `test_the_route_is_open_and_serves_the_latest_valid_run` · `test_the_payload_carries_the_disclaimer_and_n_candidates` · `test_every_served_row_carries_its_three_factors` · `test_the_formula_and_its_exclusions_are_served_not_typed_on_a_surface` · `test_no_run_reports_not_run_with_the_disclaimer_still_present` · `test_a_superseded_run_is_never_served` · `test_an_invalid_run_is_never_served` · `test_the_population_key_names_the_other_route_by_name` |
| **T-1249** | **⚠⚠ HARD STOP — the cohort-82 learned scorer is untouched.** The `/api/ranking` payload is captured **before** any census structural run exists and asserted **equal** after one is loaded; `ranking_runs` / `target_scores` / `ranking_results` keep their row counts; no census row acquires a `ranking_run_id`; the three new files **name none of those tables as a value**, import none of their models, type no `run_kind`, and import neither `core.scorer` nor the fitter; `core/scorer.py` and `core/features.py` never reach the census formula; `app/reads.py` never learns it | `test_the_cohort_82_ranking_route_is_unchanged_by_a_census_structural_run` · `test_a_census_structural_row_never_reaches_the_cohort_82_tables` · `test_neither_the_formula_nor_the_loader_nor_the_reader_names_the_scorer_tables` · `test_no_census_structural_path_imports_the_learned_scorer_or_the_fitter` · `test_the_learned_scorer_cannot_reach_the_census_structural_formula` · `test_app_reads_and_the_census_structural_reader_do_not_import_each_other` |
| **T-1250** | **The migration is additive and the chain stays linear.** `0012`'s alembic **operations** (read off its AST, not grepped) contain no `alter_column`, `drop_column`, `rename_table` or `execute`; the only tables it creates or drops are the two new ones and **none of the three scorer tables appears in either list**; the UNIQUE grain is declared in the migration **and** in the ORM; `down_revision` is `0011_clinical_edges`, no two migrations share a parent, and `0012` is the single head | `test_the_migration_is_additive_and_rewrites_nothing` · `test_the_migration_declares_the_unique_grain_the_orm_declares` · `test_the_migration_chain_is_linear_and_this_is_its_head` |
| **T-1251** | **The living log and the docs.** `### D-144` exists **exactly once** and leads the log (**the check is the heading, not a citation of one** — D-062 / method-note item 7), carries the locked formula with `0.2` / `200` / `0.8` / `0.3`, names the four exclusions **and the 0.5 it refuses**, states *Sheet is a lens, DB/API is the source of truth*, names the Matt GO and the date, cites `D-041` / `D-060` / `/api/ranking` / `preregistered`, states the **`D-079` dec 1 narrowing** clause-by-clause (what was **LIFTED**, what **STANDS**), carries a **deep-learning justification** naming ESMFold and pLDDT, and states what this build could **not** verify (no database, `not_run`, and that `PQR` resolves to nothing). `D-144` is in the id enumeration; `### D-142`, `### D-143` and `### D-145` stay **barred by name** with rows in `docs/RESERVED.md`; `ARCHITECTURE.md` and this Test Plan are current. ⚠ **T-1218's next-free clause is amended in place** (D-129-C) | `test_the_log_entry_exists_and_leads_the_log` · `test_the_log_entry_carries_the_locked_formula_and_its_exclusions` · `test_the_log_entry_names_the_go_and_the_separation_from_the_learned_scorer` · `test_the_log_entry_states_the_d079_supersession_precisely` · `test_the_log_entry_carries_a_deep_learning_justification` · `test_the_log_entry_states_what_it_could_not_verify` · `test_the_next_free_integer_is_named_and_barred` · `test_the_architecture_doc_records_the_shipped_shape` · `test_the_test_plan_carries_the_d144_addendum` |

---

## Addendum 2026-09-08 — D-143 Track B structural-only ranking copy

### D-143 (this PR; T-1225–T-1229) — the sentence stops claiming a composite it cannot compute

⚠ **Shipped first as `D-142` and renumbered to `D-143` by owner instruction (2026-09-09)**, with
**142 held** and registered in [`RESERVED.md`](RESERVED.md) — nothing visible in the tree spends it,
so the six enumerated id guards keep its bar and add 143 beside it rather than dropping either.

⚠⚠ **143 was claimed twice, and merge order settled it.** [#267](https://github.com/mdk32366/Project-PharmFoldMDK/pull/267)
(branch `cursor/d-142-targets-cancer-description-columns-d08d` — the *name* says 142) writes
`### D-143` in its **diff** and adds `tests/test_d143_targets_columns.py`. #266 merged to `main` at
`f243f93` first, so 143 is spent there and **142 is still free for the Targets agent**. The
renumber of #267 belongs to that agent and to Trinity; the guards here redden against a second
`### D-143` **by design**, and the fix on either side is to **ADD** ids, never a `>=`.

Acceptance tests in `tests/test_d143_track_b_structural_only.py`, plus the updated
D-123 pins in `tests/test_about_paper_extract.py`, `ui/src/aboutPaper.test.js` and
`ui/src/components/AdcContext.test.jsx` (T-1234). Cite `### D-143` and the **owner GO
2026-09-08 (Matt)** — *honest structural ranking only; no fake cancer scores*.
Docs + UI copy only: no route, no component, no payload field, no migration, no ops.

⚠ **The carve-out is a test, not a promise.** The cohort-82 **D-041/D-060** learned
scorer, its `Rank` column and MethodNote's prose about it are a different ranking
surface over a different population, and T-1227 pins them as untouched.

⚠ **D-056 readability, measured both ways rather than reported as a pass:** the
retired sentence printed `grade = 10.83 over 2343 words / 119 sentences`; the
structural sentence prints `grade = 10.84 over 2453 words / 124 sentences`. **The
ceiling stays at 12.5** and was not re-calibrated (D-135).

| Id | Assertion | Test |
|----|-----------|------|
| **T-1225** | **The retired composite is gone as a live claim, and the one surviving copy is named.** Every file under `docs/` and `ui/src` is enumerated (flattened, so a re-wrap cannot smuggle the sentence past a line-oriented search) and exactly three may still carry the words: `docs/README.md` — D-123's historical quotation, which must sit within 2,000 characters of an `AMENDED BY `D-143`` note that says **RETIRED as a description of what we rank by** (D-129-C: a superseded claim never stands alone, and is never quietly deleted) — and the two UI test files, where every occurrence must be on a `.not.toContain(` line. ⚠ The log may hold that quotation **once**; a second copy is a live claim wearing a citation's clothes. Neither the Doc nor the extract may match `rank(ed) by ((cancer|membrane)` or contain `/ normal risk` | `test_the_retired_composite_appears_nowhere_in_docs_or_ui_as_a_live_claim` · `test_the_one_surviving_copy_is_d123s_record_and_carries_its_supersession` · `test_no_live_file_names_the_composite_terms_as_what_is_ranked` |
| **T-1226** | **What the sentence says now, in both files, identically.** `structure only — membrane × ECD × fold confidence (pLDDT)` is in the Doc **and** in `aboutPaper.js`, and `TRACK_B` parsed out of the module is still a **character substring of the Doc** (D-123 dec 4 — the Doc is edited first and the extract follows). The sentence carries all seven load-bearing clauses as separate assertions, so a partial rewrite names the clause it dropped: the four **excluded** terms, `not filled in as 0.5 neutrals`, `explicitly **not** ADC readiness`, `not a shortlist`, the scope (`whole census of outward-facing spans (3,467 rows), not one tranche`), ⚠ **AMENDED IN PLACE BY D-146 (2026-09-09), and the superseded requirement is kept rather than deleted (D-129-C):** this clause read `it runs offline: it is not a ranked surface in this application` — true when D-143 shipped, **false once `D-144` served the rank at `/api/census-structural-ranking` and `D-145` baked its loader in** — and now requires `served live by this application** at /api/census-structural-ranking` plus `review lens** — an export for reading, never the source of truth`, **with the retired denial asserted ABSENT beside them**; and `**Later, on its own GO:**` + `real HPA/TCGA expression plus wet assays`. Track A's `Wet binding assays — required` / `No bind → stop` are untouched, and the Doc records the amendment with its date and id rather than swapping the line silently | `test_the_paper_and_the_extract_carry_the_same_structural_sentence` · `test_the_sentence_names_its_exclusions_rather_than_defaulting_them` · `test_the_paper_records_the_amendment_instead_of_silently_swapping_the_line` · `aboutPaper.test.js` (D-143 case) · `test_aboutpaper_excerpts_are_substrings_of_the_doc` |
| **T-1227** | **⚠⚠ HARD STOP — the cohort-82 learned scorer is untouched, as a property of the tree.** `core/scorer.py` still fits the logistic and names no copy decision; MethodNote still carries *"a learned scorer over structure-derived features ranks the cohort"*; `TargetList.jsx` still declares `{ key: 'rank', label: 'Rank' }`. ⚠ **And the structural sentence may not appear on any scorer surface** (`MethodNote.jsx`, `TargetList.jsx`, `ScorerView.jsx`, `TargetScorerPanel.jsx`, `targetScore.js`) — a copy that put it there would merge the two rankings again, which is the confusion this entry exists to end. No `core/`, `app/` or `scripts/` file names D-143, and no structural-ranking script is added | `test_the_cohort_82_learned_scorer_is_untouched_by_this_entry` · `test_this_entry_ships_no_code_path_and_no_artefact` |
| **T-1229** | **⚠ The `/method` rail suite stops racing the copy it measures.** `MethodNote.toc.test.jsx`'s helper awaited only `method-toc` — static headings, first paint — then asserted synchronously on copy that arrives with `getCoverage()`; **two gate runs on byte-identical test and component bytes disagreed** ([34312365044](https://github.com/mdk32366/Project-PharmFoldMDK/actions/runs/34312365044) green, [34312428832](https://github.com/mdk32366/Project-PharmFoldMDK/actions/runs/34312428832) red). The helper now also waits on a coverage-**derived** string (`folds a fixed cohort of 7 candidate`), chosen as a *different* beat from the same `cov` state so `/3 ranked-and-folded of 7/` still fails at its own assertion rather than as a helper timeout; and a new case holds the promise open to assert the **fallback first, then the numbers**, with the fallback gone afterwards. ⚠ **The assertion was not relaxed to the pre-fetch fallback** — that would pin the loading state as the contract (D-050: the line is computed, never a literal). **Shown to bite:** with `getCoverage` delayed 60 ms the pre-fix helper reproduces the runner's exact red (1 failed / 6 passed) and the fixed helper passes 7 of 7 | `MethodNote.toc.test.jsx` (7 cases, incl. `carries the fallback coverage line until getCoverage resolves, then the derived numbers`) · `test_the_method_toc_suite_waits_for_the_async_coverage_beat` |
| **T-1228** | **The log leads it, and the id guards were widened by ADDING.** Exactly one `### D-143` heading, leading the log, `### D-144` barred, and **`### D-142` still barred as held** (registered in `RESERVED.md`, with the ruling and the absence of a discoverable holder named) — in this suite and in the six enumerated guards (`test_d129_*`, `test_d130_*`, `test_d136_*`, `test_d139_*`, `test_d140_*`, `test_d141_*`), each of which now names 142 by its heading. The entry carries the cohort-82 hard stop with its ids, the GO and its owner, the rejected `0.5 neutral`, the scope `full census (3467), not T5-only`; a deep-learning justification that survives the cut (ESMFold / D-003, pLDDT now **one of three** factors, and no claim that the network answered a biology question); and a D-016 provenance that **names the artefact it does not have** — `no run log, csv or notebook` for the offline order — beside the two it does (`census_manifest.v6.provenance.json` `"manifest_rows": 3467`, `censusSummary.js` `manifestRows: 3467`), the tip `30f402f`, `gh pr list --state open`, and that check's known weakness. D-123's `**Amended by:**` names D-143, and `ARCHITECTURE.md` describes the extract as structural-only | `test_the_log_entry_exists_exactly_once_and_leads_the_log` · `test_the_entry_carries_the_cohort_82_hard_stop_and_the_go_that_authorised_it` · `test_the_entry_carries_a_deep_learning_justification_that_survives_the_cut` · `test_the_entry_names_the_artefact_behind_every_claim_including_the_missing_one` · `test_d123_points_forward_at_this_entry` · `test_the_architecture_doc_describes_the_extract_as_structural_only` |

---

## Addendum 2026-09-09 — D-142 the `/targets` Cancer association + Description columns

### D-142 (this PR; T-1235–T-1242) — the field that looked like the description was the gene symbol

Acceptance tests in `tests/test_d142_targets_columns.py` (47),
`ui/src/components/TargetList.columns.test.jsx` (33) and
`ui/src/associationSummary.test.js` (13). Hermetic — no network, no GPU, no ops, no
fold, no migration; the FastAPI checks run against in-memory SQLite with a queue stub
that raises if a read path ever reaches it. Cite `### D-142`, the **Matt GO 2026-09-08
~8:02 AM PT via Emma** (*"column one is massively wide"* + the two columns), and
**`D-0037`** (model pin).

⚠ **The claim these tests exist to make falsifiable is a negative one:** `label` is
**not** the description on this population. It is measured (`label == gene` on all 82
rows of `data/cohort_82_ecd.csv`), and the **other** meaning of the same key is pinned
too (`data/census/census_labels.csv` + `CensusTable.jsx`'s `Protein` header), because a
test that checked only the cohort would leave the next reader free to make the same
inference from the census. `F-049`'s family.

| ID | Property | Test |
|---|---|---|
| **T-1235** | **`label` is the gene symbol, and the description is `protein_name`.** The committed CSV keeps both columns; `label == gene` on **all 82** rows; every row has a non-blank `protein_name` that differs from the gene; `ManifestRow` carries it **read, never derived**, and a blank cell stays `None` and never `""` (an empty string is a *value* to `sortRows.isAbsent`); the census's `label` is a protein NAME on >100 rows and `CensusTable` renders it as `Protein` | `test_the_committed_manifest_keeps_label_and_protein_name_as_separate_columns` · `test_label_equals_gene_on_every_cohort_row_so_it_is_not_a_description` · `test_every_cohort_row_has_a_protein_name_and_it_differs_from_the_gene` · `test_the_manifest_row_carries_the_protein_name_and_never_derives_it` · `test_a_blank_protein_name_stays_an_absence_and_never_becomes_an_empty_string` · `test_the_census_uses_the_same_key_for_the_other_meaning_and_that_is_the_trap` |
| **T-1236** | **The description travels on `/api/coverage` and the light list is untouched.** All **82** rows serve a `protein_name`, including `FAT2` and `MUC16`, which have no `protein_analyses` row at all — the reason it is this supplier; `/api/analyses` gains **no** field (`protein_name` / `description` absent, `sequence` / `fold_provenance` still absent, `label` still the gene); the projection names the field rather than computing one | `test_coverage_serves_a_protein_name_for_every_one_of_the_82` · `test_the_two_rows_with_no_analysis_still_get_a_description` · `test_the_light_lists_exact_field_set_is_untouched` · `test_the_projection_reads_the_manifest_and_computes_no_name` |
| **T-1237** | **The D-053 supplier is consumed, not re-derived.** 337 pairs / 82 covered / 82 cohort / cutoff 150 / no unmatched symbols, unchanged; **every** target's pairs are descending in the data contract (which is what lets the cell read the leading run off the order as given); the tie set is exactly `JAG1` / `CD53` / `INSR` and at most three-wide; the committed CSV still holds 337 pairs, so **no association was added or removed** | `test_the_association_map_still_covers_the_cohort_unchanged` · `test_every_target_pairs_are_sorted_descending_in_the_data_contract` · `test_the_ties_the_cell_renders_in_full_are_real_and_bounded` · `test_this_pr_ships_no_ops_no_fold_and_no_new_cancer_datum` |
| **T-1238** | **⚠⚠ The HPA citation, which the route never served.** `/api/associations` carries one block **per covered symbol** (82); each carries **all four** elements, the IHC DOI `10.1126/science.1260419` (not the 2017 transcriptome paper — a filename is not a modality) and a real `v22.proteinatlas.org/<ENSG>-<GENE>/pathology` link for **82 of 82**; the payload keeps every D-053 key; a supplier failure degrades to `{}` so the consumer must **withhold the value**; the detail card reads `attributions[symbol]` and no longer reads the key that never existed; the growth is **measured** (17,952 → 56,498 raw / 2,148 → 4,039 gzipped) and the log carries the numbers | `test_the_route_serves_one_attribution_block_per_covered_symbol` · `test_every_block_carries_all_four_elements_and_a_real_atlas_link` · `test_the_live_route_carries_the_attributions` · `test_a_supplier_failure_degrades_to_no_blocks_so_the_consumer_fails_closed` · `test_the_detail_card_now_reads_the_per_symbol_block_and_not_the_key_that_never_existed` · `test_the_added_payload_is_measured_rather_than_waved_through` |
| **T-1239** | **The two columns, as properties of the surface.** `Description` is a real `COLUMNS` entry reading `description` and never `label`; `Cancer association` has `key: null` and the refusal is **rendered**, not commented; the claim boundary (expression / not causation / not driving the disease / not a clinical indication) is on the list; the cutoff is interpolated and `above 150` appears nowhere; the component never touches `qh_score` and the cell never sorts; the reduction lives in its own tested module and **checks** the contracted order; the row markup is **one** `RowCells` used twice; `description` joins the shared matcher | `test_the_description_column_is_a_real_columns_entry_and_not_a_hand_drawn_header` · `test_the_description_column_does_not_read_the_payloads_label` · `test_the_association_column_has_no_sort_key_and_the_reason_is_rendered` · `test_the_claim_boundary_is_rendered_on_the_list_in_d053s_own_vocabulary` · `test_the_cutoff_is_interpolated_and_never_typed_on_this_surface` · `test_the_surface_consumes_the_association_supplier_and_re_derives_nothing` · `test_the_reduction_lives_in_its_own_tested_module` · `test_the_row_markup_is_written_once_for_both_bodies` · `test_the_shared_matcher_can_find_a_description` |
| **T-1240** | **⚠⚠ Column one is bounded and NOTHING is clipped.** `.col-rank` / `.rank-cause` / `.col-description` / `.col-assoc` each carry a `max-width` **declaration** — comments stripped before matching, because D-141 lost a guard to a whole-file check satisfied by a *comment* holding the string it wanted (`F-044`) and the prose above `.rank-cause` contains the literal `max-width`; `.rank-cause` carries no `text-overflow` / `max-height` / `line-clamp` / `overflow: hidden` / `white-space: nowrap`; all **seven** `rankCause` strings are byte-identical; the bound sits on a `display: block` inner element, and the cause is `font-family: inherit` because the cell is `.mono` for the integer | `test_the_bounds_are_declarations_and_the_cause_is_not_clipped` · `test_no_rank_cause_string_was_reworded_or_dropped` · UI: `bounds the column in the stylesheet — a RULE, never a comment mentioning one` · `⚠⚠ CLIPS NOTHING — the bound is a bound, not a truncation` |
| **T-1241** | **The rendered surface, in jsdom.** The manifest name renders and `label` does not; an absent name and an unreachable supplier are **different sentences** and neither is a dash; the header sorts and the order **actually changes** (a caret that reorders nothing is the revert this catches) with absence trailing in **both** directions; the leading tumour type(s) render with the total, ties render in full, the target page is reachable from the cell; `no association recorded` never appears when the supplier merely failed; the map failing costs the column and never the list, even when the api module has no `getAssociations` at all; the association header has **no button**; `HpaCredit` renders **once**, the tumour type **is** the atlas anchor, the value is **withheld** with no block, and the credit is **suppressed** when no row drew one; `colSpan` tracks the column count and the partition renders the **same** cells | `ui/src/components/TargetList.columns.test.jsx` (33 tests) |
| **T-1242** | **What must not have moved.** No new route reaches the app that `system-model.json` does not declare (D-051 fires on route *sets*); coverage's `ranked + held_out + excluded == denominator == 82`; `PLDDT_FLOOR` is **50** and the default sort is still `rank` asc; Rank / Gene / Accession are still columns one, two and three (three suites read `td[1]` and `td[2]`); identity precedes the new columns and the new columns precede Fold confidence; no blended score, no suitability / good-target / promising / recommended language; `TargetList.jsx` is **enrolled in PC3's covered set** rather than exempt from it; the `### D-142` entry exists exactly once, leads the log, records both findings with their measurements, states the refused sort and its 2026-08-21 ruling, names what is not shipped, carries a deep-learning justification, records the reverts including the `recommended` bite, and pins the numbering provenance (`30f402f`, `D-142` barred, never a `>=`); `ARCHITECTURE.md` is current | `test_no_new_route_reaches_the_app` · `test_the_coverage_partition_and_its_invariant_are_untouched` · `test_no_scorer_ranking_or_floor_moved` · `test_the_new_surface_is_in_the_pc3_covered_set` · `test_the_d142_entry_exists_and_leads_the_log` · `test_the_entry_records_the_label_finding_as_a_measurement` · `test_the_entry_records_the_uncited_card_rather_than_quietly_fixing_it` · `test_the_entry_measures_column_one_before_it_changed_it` · `test_the_entry_states_the_refused_sort_and_its_reason` · `test_the_entry_names_what_is_not_shipped` · `test_the_entry_carries_a_deep_learning_justification` · `test_the_entry_records_the_reverts_including_the_one_that_bit_unprompted` · `test_the_numbering_provenance_is_recorded_not_assumed` · `test_the_architecture_doc_records_the_shipped_shape` |

⚠ **T-1218's next-free clause is amended in place at D-142 rather than replaced**
(D-129-C: a superseded claim never stands alone). It read *"bars `### D-142`"*; it now
requires `### D-142` to be the target-list columns entry by name and bars `### D-142`.
**Nothing was relaxed to a `>=`** — the seventh widening, the seventh resolution by
adding.

---


---

## Addendum 2026-09-08 — D-141 landing the D-126 OPS trees on the serving volume

### D-141 (this PR; T-1219–T-1224) — the gate had nothing to answer with

Acceptance tests in `tests/test_d141_land_confidence_kabsch.py`. Hermetic — every
fixture writes under `tmp_path`; **no Fly, no GPU, no ops run, no network, and no
re-measurement of any parent**. Cite `### D-141`, the **Matt BUILD GO 2026-09-08
~4:04 PM PT via Emma** (`D-0043` stitch honest-endpoint, Phase 6a; ⚠ external
numbering, not a project decision id), and **`D-0037`** (model pin).

⚠ **The live count these tests do NOT change: eligible 17 / flipped 0.** This PR
ships the lander, not a landing; no Fly credential and no `flyctl` exist on the
build that wrote it, and the source ops `out_root` is not reachable from here.

⚠ **Four reverts were run against these guards, and TWO of them exposed a guard
that did not bite** — recorded because a green suite is evidence about the tests
until each one has been shown to fail:

1. **the allowlist refusal removed** → 3 tests fail, including T-1219;
2. **`provenance.json` written first** → red **at collection**, from a
   module-level `assert` that `python -O` deletes, so T-1222's own test never
   ran. **Fixed** (the pins now `raise`), and the re-run reddens T-1222;
3. **the post-copy gate verification removed** → red at T-1223;
4. **the `.gitignore` rule deleted** → **all 34 passed.** The check read the whole
   file and was satisfied by the *comment* naming the rule — F-044's shape.
   **Fixed** (rule lines only), and the re-run reddens T-1224.

| Id | Assertion | Test |
|----|-----------|------|
| **T-1219** | **⚠ HARD STOP — the allowlist is the authority, and it is IMPORTED.** A parent outside `D126_SERVED_PASS_SUBSET` is refused with `LandRefused` **even with a perfect accepted tree in the source root** (the fixture uses **3394** — one of the only two parents D-126 OPS recovered, still barred by Phase 4 `rmsd_gt_10`), a sweep never copies a non-allowlisted tree that merely *sits* in the source, the script types **no parent id of its own**, and nothing is written to the destination | `test_a_parent_outside_the_seventeen_is_refused_even_with_a_perfect_tree` · `test_a_sweep_never_copies_a_non_allowlisted_tree_sitting_in_the_source` · `test_every_id_the_lander_will_write_is_in_the_policy_subset` · `test_the_allowlist_is_imported_not_retyped` · `test_the_cli_exits_nonzero_on_a_refusal_and_says_so_on_stderr` |
| **T-1220** | **A refused or incomplete run never lands, under D-139's OWN vocabulary.** `accepted: false` → `confidence_kabsch_refused`; accepted with no `stitched.pdb` → `no_confidence_kabsch_success_pdb`; missing/unparseable provenance → `unreadable_provenance`; no directory → `no_source_tree`, which is **not** the refusal word. A provenance naming another parent is `LandRefused`. In every case the destination stays empty and the gate still answers `assembler` | `test_a_recorded_refusal_is_a_named_skip_and_writes_nothing` · `test_an_accepted_run_with_no_stitched_pdb_is_a_named_skip_and_writes_nothing` · `test_an_unreadable_provenance_is_a_named_skip_not_a_crash_and_not_a_pass` · `test_an_absent_source_tree_is_a_skip_that_names_absence_not_refusal` · `test_a_tree_whose_provenance_names_another_parent_is_refused` · `test_a_parent_named_on_the_command_line_must_land_or_the_run_fails` |
| **T-1221** | **The positive case, end to end, through the shipped gate.** Before: `eligible: true`, `flipped: false`, `no_confidence_kabsch_artifacts`. After one land: `served == confidence_kabsch`, `flipped: true`, no reason, stem `stitched_confidence_kabsch`, `served_pdb_path` inside the landed dir, and the PDB bytes identical to the source. pLDDT and PAE travel with it (D-139 dec 5). A dry run writes **nothing at all** | `test_the_happy_path_lands_the_tree_and_the_d139_gate_flips` · `test_the_confidence_arrays_travel_with_the_pdb` · `test_a_dry_run_writes_nothing_at_all` · `test_the_cli_prints_landed_and_skip_per_parent_and_exits_zero` |
| **T-1222** | **⚠ A partial copy reads as *not yet landed*, never as *landed wrong*.** `provenance.json` is written **last** and each file lands via one `os.replace`; a copy killed midway leaves a directory that resolves to `assembler`. The two file lists cannot drift, and the pins that hold the ordering `raise` rather than `assert` (D-082: `python -O` deletes an `assert`) | `test_an_interrupted_copy_leaves_a_tree_that_does_not_flip` · `test_provenance_is_written_last_and_the_two_file_lists_cannot_drift` |
| **T-1223** | **"Landed" is VERIFIED through the production resolver, and the count is read off the destination.** A copy whose parent the gate still answers `assembler` for is `LandRefused`; the run's flipped count re-reads the whole allowlist, so a second run reports **both** parents rather than the one it just copied. An already-landed parent is not clobbered without `--overwrite`; source and destination may not be the same directory | `test_landed_is_verified_through_the_production_resolver_not_recounted` · `test_the_flipped_count_includes_parents_an_earlier_run_landed` · `test_an_already_landed_parent_is_not_clobbered_without_overwrite` · `test_source_and_destination_may_not_be_the_same_root` |
| **T-1224** | **The hard stops as properties, and the trees stay out of git.** The assembler dir and `kabsch/{parent}/` are byte-identical after a real land; only the five named files travel and the rest are reported left behind; the destination default is the Fly `artifacts` mount; the script's **imports are an enumerated allowlist** (no torch / numpy / requests / SQLAlchemy / alembic) and it names no geometry, while its docstring states every stop an operator must read; `.gitignore` carries `confidence_kabsch/` as a **rule line**, no such tree exists in the repository, and nothing calls a seam solved. The `### D-141` entry exists exactly once, leads the log, names the blocker and records why **140** was skipped **and that #263 then merged mid-flight at `578f5ac`** (amended in place, D-129-C); `ARCHITECTURE.md` is current | `test_landing_never_writes_the_assembler_dir_or_the_d125_kabsch_tree` · `test_only_the_named_files_land_and_the_rest_are_reported_left_behind` · `test_the_cli_defaults_the_destination_to_the_serving_artifact_root` · `test_the_lander_imports_nothing_that_could_fold_queue_or_rank` · `test_the_hard_stops_are_stated_where_an_operator_will_read_them` · `test_the_lander_moves_no_threshold_and_computes_no_geometry` · `test_no_confidence_kabsch_tree_is_created_inside_the_repository_by_this_suite` · `test_the_lander_never_claims_a_seam_is_solved` · `test_the_log_entry_exists_and_leads_the_log` · `test_the_log_entry_records_why_140_was_not_taken_and_that_263_then_merged` · `test_the_log_entry_states_the_blocker_rather_than_implying_a_land_happened` · `test_the_architecture_doc_names_the_lander` |

---

## Addendum 2026-09-08 — D-139 served-path flip (PASS subset only)

### D-139 (this PR; T-1210–T-1218) — the served PDB stops being a constant

Acceptance tests in `tests/test_d139_served_path_flip.py` and
`ui/src/components/AssemblyReview.servedpath.test.jsx`. Hermetic — SQLite +
`tmp_path` trees, **no Fly, no GPU, no ops run, and no re-measurement of any
parent**. Cite `### D-139`, the **Matt BUILD GO 2026-09-08 ~2:57 PM PT via
Emma** (`D-0043` stitch honest-endpoint, Phase 6; ⚠ external numbering, not a
project decision id), and **`D-0037`** (model pin).

⚠ **Two defects these exist to redden**, both verified red before this PR was
filed by breaking the policy on purpose and re-running:

1. **the allowlist removed** (flip on artifacts alone) → **8** tests fail,
   including T-1211 and T-1212;
2. **D-126's own 24 used as the subset** instead of the 17 → **6** tests fail,
   including T-1210 and T-1212.

| Id | Assertion | Test |
|----|-----------|------|
| **T-1210** | **The subset is the recorded seventeen, and it is known from two artefacts that agree.** `D126_SERVED_PASS_SUBSET` equals the Wave1+Wave2 **27** minus `phase5_named_refuse.ACCEPT_REFUSE_TEN`, equals `CONFIDENCE_RESTITCH_PARENT_IDS` minus the ten, is a strict subset of the 27 (never one of D-132's other 18), and equals the ids **parsed back out of** `docs/method-hold48-tiles.md` §"Inventory on the 27" — so the allowlist cannot drift from the record it came from. The import-time assertion in `app/served_path_policy.py` re-checks it on every run | `test_the_pass_subset_is_exactly_the_recorded_seventeen` · `test_the_seventeen_are_the_ids_the_method_page_recorded` · `test_every_accept_refuse_parent_is_excluded_from_the_subset` |
| **T-1211** | **⚠ HARD STOP — flipping without the allowlist fails.** A complete, **accepted** D-126 tree with a `stitched.pdb` in it does **not** flip a non-PASS parent, at the resolver **and** over HTTP (`/api/analyses/{id}/structure` still returns the assembler bytes under the `stitched` stem); a parent outside the 27 entirely is likewise refused, reason `not_in_pass_subset` | `test_a_parent_outside_the_seventeen_never_flips_even_with_a_perfect_tree` · `test_a_parent_outside_the_seventeen_never_flips_over_http` · `test_a_parent_outside_the_twenty_seven_entirely_never_flips` |
| **T-1212** | **⚠ HARD STOP — auto-flip fails.** Every one of the **ten** accept-refuse parents is given a complete accepted tree and **not one flips**; a provenance carrying a glowing rollup (`pass: 27`, `recovered_of_primary_five: 5`) still cannot admit an excluded parent — **the allowlist is the authority, never a pass count** — and the served block asserts `auto_flip: False` | `test_artifacts_alone_never_flip_any_of_the_accept_refuse_ten` · `test_the_policy_declares_no_auto_flip_and_never_consults_a_pass_count` |
| **T-1213** | **⚠ 17, not D-126's own 24.** `D126_OWN_PASS_N` = 24, the seven later-named-refuse parents are enumerated, `24 − 7 = 17`, each of the seven really is in `ACCEPT_REFUSE_TEN` and really is out of the subset, and the remaining three of the ten are D-126's own refuses (2939 / 3272 / 3432). ⚠ **Two live surfaces may not contradict:** `phase5_fate()` already answers `served_path: "assembler"` for all ten, and the resolver agrees for all ten | `test_the_twenty_four_is_named_and_is_deliberately_not_the_subset` · `test_the_served_answer_agrees_with_the_label_registry_for_all_ten` |
| **T-1214** | **Fail-closed on each of the four yeses, with a NAMED reason.** No tree → `no_confidence_kabsch_artifacts`; a refused run → `confidence_kabsch_refused`, **including when a leftover `stitched.pdb` sits beside the refusal**; accepted-but-no-PDB → `no_confidence_kabsch_success_pdb`; not eligible → `not_in_pass_subset`. Every refusal carries its note and `solved: False`, because "assembler" alone cannot tell *never eligible* from *the run refused it* | `test_an_eligible_parent_with_no_tree_stays_on_the_assembler` · `test_an_eligible_parent_whose_run_refused_stays_on_the_assembler` · `test_a_leftover_pdb_beside_a_refusal_is_never_served` · `test_an_accepted_tree_with_no_pdb_stays_on_the_assembler` · `test_every_refusal_names_a_reason_and_carries_its_note` |
| **T-1215** | **The positive case, end to end.** An eligible parent with an accepted tree resolves to `confidence_kabsch` with stem `confidence_kabsch/{parent}`; the route streams the **D-126** bytes under `stitched_confidence_kabsch.pdb` and **never** `stitched.pdb`; pLDDT and PAE come from the **same** tree; a flipped parent whose tree lacks a sibling keeps the assembler's **independently** (a missing sibling is not a 404); an **unflipped** parent is served byte-for-byte what it always was; an unknown id resolves to `None` rather than raising | `test_an_eligible_parent_with_an_accepted_tree_is_served_d126` · `test_the_route_hands_out_the_d126_bytes_under_a_name_that_says_so` · `test_the_plddt_and_pae_travel_with_the_served_structure` · `test_a_flipped_parent_with_no_sibling_confidence_keeps_the_assembler_plddt` · `test_an_unflipped_parent_is_served_byte_for_byte_what_it_always_was` · `test_an_unknown_id_resolves_to_nothing_rather_than_exploding` |
| **T-1216** | **The card names the served path per parent.** `assembly_review.served_path` carries the answer, the eligibility, the named reason, `pass_subset_n` = 17, `gate_angstrom` = 10.0, `gate_moved: False`, `solved: False`; **exactly one** of the five path blocks carries `served: true`; `default_served` keeps its old meaning (assembler `True`, siblings not `True`) so no earlier decision is silently rewritten; an accept-refuse parent's card says assembler **beside** its label. The UI renders the reason, not just the answer, and every use of "solved" on the block is a negation | `test_the_review_card_names_the_served_path_and_the_reason` · `test_the_review_card_marks_exactly_one_path_as_served` · `test_an_accept_refuse_parent_card_says_assembler_beside_its_label` · `test_the_ui_review_card_renders_the_reason_not_just_the_answer` · `AssemblyReview.servedpath.test.jsx` (5 cases) |
| **T-1217** | **⚠ The disqualifying count is asserted, not omitted (D-016).** No `confidence_kabsch/` tree is committed to this repository, so **seventeen are eligible and ZERO are flipped**; both Method surfaces say that number out loud. If a tree is ever checked in this goes red and whoever did it must say so in the log | `test_no_confidence_kabsch_tree_is_committed_so_nothing_flips_here` |
| **T-1218** | **The hard stops from the GO, as properties.** `RMSD_REFUSE_ANGSTROM` = **10.0** and the three refuse reasons are unmoved; the policy module holds no geometry, no threshold and no numpy; the **diff** touches no `worker/`, `notebooks/`, `db/versions/`, alembic or `core/hold48*` path (no ops / rent / emit / F-004 / geometry); **D-127 piecewise is not resurrected** (the policy never names it); no surface calls a served structure solved; both Method surfaces carry D-139, the seventeen enumerated, `24 − 7 = 17`, the four named reasons, 10.0 Å, no-auto-flip and "never claim 27/27 PASS"; the new `/method` heading carries an `id` for D-138's rail; **every** pre-existing "default served structure is still the assembler" sentence names D-139 within 400 chars (D-129-C: a narrowed claim never stands alone); the `### D-139` entry exists exactly once with its provenance, its zero, its DL justification and every hard stop, and `ARCHITECTURE.md` is current. ⚠ **Next-free clause widened in place at D-141 (D-129-C: a superseded claim never stands alone):** it read *"`### D-140` does not exist"*; it now also requires `### D-141` to be the lander entry and bars `### D-143`. **140 is skipped, not free** — #263 spends it on an unmerged branch, so the bar on it stands and is ADDED to, never relaxed to a `>=`. ⚠ **Widened in place again at D-143** (same discipline, seventh pass): the clause now also requires `### D-143` to be the Track B structural-only copy entry and bars `### D-144`. **D-143 changes no served path, no gate and no threshold** — it is named in this guard only because this is one of the enumerated id checks. ⚠⚠ **Widened in place AGAIN at D-142, the eighth pass, and this one is a RESERVED integer being SPENT:** the clause now also requires `### D-142` to be the `/targets` Cancer association + Description columns entry, so **both 142 and 143 are named** and `### D-144` keeps the bar. **The 142 bar reddened exactly as its own failure message pre-committed** — *"if a holder writes it, this reddens BY DESIGN and 142 is ADDED beside 143"* — and `docs/RESERVED.md`'s row is retired in the open. **Nothing was relaxed to a `>=`**: eight widenings, eight resolutions by adding. ⚠ D-142 changes no served path, no gate and no threshold either ⚠⚠ **Widened in place AGAIN at D-144, the ninth pass:** the clause now also requires `### D-144` to be the census structural-rank entry — so **142, 143 and 144 are all named** — and **`### D-145`** takes the bar. ⚠ **D-144's own first draft barred `### D-142` and `### D-143`**, because at `30f402f` neither had a heading, an open PR or a branch; both then merged (`f243f93` / `22ce1d7` / `b7d933f`) while it was open, those bars reddened **exactly as they said they would**, and the rebase ADDED all three names. **Nothing was relaxed to a `>=`**: nine widenings, nine resolutions by adding. | `test_no_threshold_was_loosened_and_the_refuse_reasons_are_unmoved` · `test_this_pr_ships_no_ops_no_rent_no_emit_and_no_f004` · `test_d127_piecewise_is_not_resurrected_as_this_campaign` · `test_no_surface_calls_a_served_structure_solved` · `test_both_method_surfaces_name_the_served_path_rule_and_its_limits` · `test_the_method_page_registers_the_new_section_with_the_d138_rail` · `test_the_earlier_served_claims_do_not_stand_alone` · `test_d139_entry_exists_in_the_living_log` · `test_the_entry_records_the_subset_its_provenance_and_the_zero` · `test_the_entry_keeps_every_hard_stop_from_the_go` · `test_the_entry_carries_a_deep_learning_justification` · `test_architecture_records_the_shipped_shape` |

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

### D-127-B (this PR; T-1134–T-1143) — UI four-path honesty + mandatory Method

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
| **T-1143** | **D-126 comparison is quantified (Trinity merge-gate amend).** Both Method surfaces carry, beside the best-path sentence and within 400 chars of it, **D-126 OPS recovered 2 of its primary 5** — parents **3368** and **3394** — against D-127's **0 of 3**, as recorded and marked not re-measured; both recovered parents are named as **given back** in D-127's refuse histogram (3368 `linker_jump_gt_10`, 3394 `rmsd_gt_10`); exact Spec §11 keys `n_d125_pass_d127_refuse` = 5 / `n_d126_pass_d127_refuse` = 7 / `n_d126_refuse_d127_pass` = 0 are visible on both surfaces and valued in the log; the living log records the amend with its provenance | `test_method_quantifies_the_d126_comparison_with_recovered_2_of_5` · `test_method_names_that_d127_gave_back_both_parents_d126_recovered` · `test_method_shows_the_exact_confusion_keys` · `test_living_log_records_the_d126_recovered_2_of_5_amend` · `says plainly that D-126 remains the best path, keeps every gate, and never flips the served path` |
| **T-1142** | **D-127 OPS honesty (Matt GO via Emma, amendment 1).** Method discloses the run **as recorded** — PASS 17 / REFUSE 10 / FAIL 0 at tip `e49bf34`; `recovered_of_primary_three` = **0** with 2939 `linker_jump_gt_10` / 3272 `rmsd_gt_10` / 3432 `no_domain_pieces`; the refuse histogram (`linker_jump_gt_10` ×7 · `rmsd_gt_10` ×2 · `no_domain_pieces` ×1) with its parent ids; the **named regress** (5 vs D-125, 7 vs D-126, `n_d126_refuse_d127_pass` = 0) beside the accept count, never buried under it; **D-126 named plainly as the best experimental path so far**; no gate loosened and the served path never auto-flipped; 17 accepted = 17 **recorded** outcomes, not solved joins; provenance names the GO and disclaims re-measurement; and this PR ships no ops run, no revised stitch Spec, and no Fly POST | `test_ops_figures_are_internally_consistent_before_they_are_quoted` · `test_method_discloses_the_d127_ops_run_and_its_named_regress` · `test_method_says_plainly_that_d126_remains_the_best_path_so_far` · `test_method_refuses_to_loosen_a_gate_or_flip_the_served_path` · `test_ops_disclosure_names_its_provenance_and_disclaims_measurement` · `test_this_pr_ships_no_ops_run_no_revised_spec_and_no_fly_post` · `discloses the D-127 OPS run with its named regress, not an accept count alone` · `says plainly that D-126 remains the best path, keeps every gate, and never flips the served path` |
| **T-1141** | **Mandatory Method (Spec §7).** Addendum names the four-step stitch-path train in order, the D-126 full ≫ weighted lesson (28–68 Å on 2939 / 3272 / 3432), per-UniProt-domain fit with no trim loop and linker inherit, the refuse table with the **10.0 Å gate staying**, seam numbers as measurements rather than a verdict, default served = assembler, and honest empty when the tree is missing — without claiming seams solved and **without gutting** the D-121 / D-125-B / D-126-B sections | `test_d127_b_method_addendum_names_the_stitch_path_train` · `test_d127_b_method_addendum_names_the_refuse_table_and_keeps_the_gate` · `test_d127_b_method_addendum_names_seam_disclosure_as_measurement` · `test_method_addendum_does_not_gut_d121_d125b_or_d126b` · `test_method_obligation_is_recorded_as_discharged_by_this_pr` · `names four paths and shows one row per domain piece when piecewise_kabsch artifacts exist` · `adds the mandatory D-127-B addendum naming the whole four-step stitch-path train` |

### D-128 Spec (T-1144–T-1152) — linker / seam honesty

Hermetic docs tests in `tests/test_d128_linker_seam_spec.py`. **Docs
only** in the Spec PR. No Fly. No GPU. No ops run. No restitch of the
27. No `hold48_*.py` edit — the D-125, D-126, and D-127 Kabsch modules
stay sha256-pinned by the suite. Since **D-128-A** landed, these pins
also require `### D-128-A —` in the log and A's sibling module on disk
(the module is a fifth sibling, never an edit of the prior three).
Cite [`SPEC-linker-seam-honesty.md`](SPEC-linker-seam-honesty.md) §1 /
§1a / §1b / §2 / §3 / §5 / §7 / §8 / §9 and `### D-128` in the log.

⚠ The hazard these exist for: the D-127 OPS run refused **7 of 10**
parents at the **linkers**, and the two cheap answers to that — another
rigid-body decomposition (**piecewise-v2**) or a **looser gate** — both
buy a pass count with a claim nobody measured. So the Spec's primary
deliverable is a **measurement** (§1a per-path / per-seam
`max_ca_jump_angstrom`, with `> 10.0 Å` = **dishonest** for that seam),
its repair is optional and smaller than D-127 (**±32 aa**, W = 32, no
pieces, no linker-inherit, no trim loop), **3432 stays accept-refuse**,
3272 / 3394 are **out of primary**, and the Spec **never says solved**.
⚠ Served stays assembler. ⚠ **D-126 remains the best experimental path
until proven otherwise; the D-127 failed experiment stays disclosed.**

| ID | Check | Test name |
|----|-------|-----------|
| **T-1144** | `### D-128 —` exists in the living log (the check is the heading, not a citation of one); the Spec file exists and names `linker_local_kabsch_then_winning_tile` + `decision`/`D-128`; goal framing is **diagnose and refuse dishonest seams** and the Spec never says solved; the Matt Phase 3 bar is bound in the log | `test_d128_heading_exists_in_the_living_log` · `test_spec_file_exists_and_names_algorithm_and_goal_framing` · `test_spec_never_says_seams_are_solved` |
| **T-1145** | **§1a is required, not optional:** per seam, per path (`kabsch` / `confidence_kabsch` / `piecewise_kabsch` / `linker_seam`) record `max_ca_jump_angstrom` (+ `linker_n` / `max_linker_ca_jump` where applicable); `> 10.0 Å` → **dishonest** for that seam; fail-closed so **no success PDB is presented as honest**; null ≠ 0 and unknown ≠ honest; prior trees are read, never rewritten | `test_seam_honesty_metrics_are_required_per_path_per_seam` · `test_dishonest_seam_is_fail_closed_and_no_success_pdb_is_honest` |
| **T-1146** | **Gate stays 10.0 Å and does not loosen:** no RMSD / linker threshold loosen without Matt; no threshold Spec-as-fix; the four refuse reasons are `overlap_ca_lt_3` / `rmsd_gt_10` / `singular_covariance` / **`seam_jump_gt_10`**; `< 3` Cα floor; all-or-nothing parent with cleared partials | `test_refuse_gate_stays_at_10_and_does_not_loosen` · `test_refuse_table_names_the_four_reasons_and_all_or_nothing` |
| **T-1147** | **§1b pins the algorithm:** identify the offending seam from the prior D-127 refuse **or** the measured jump; **±32 aa** window with **W = 32**; ε = **1e-3**; \(w_i = \min(\mathrm{pLDDT}_A, \mathrm{pLDDT}_B)/100\); **NO trim loop**; apply \(R, t\) only to moving-tile atoms in that window; on accept feed the existing `winning_tile` / `write_stitched` with off-block PAE **null, never 0** | `test_window_half_width_is_pinned_at_32` · `test_no_trim_loop_and_epsilon_and_weight_rule` · `test_accept_feeds_existing_winning_tile_and_pae_stays_null` |
| **T-1148** | **Single failure mode:** the **seven** signed must-hunt linker parents (**2938, 2939, 3179, 3190, 3321, 3368, 3566**) are named in the Spec **and** the log as the primary inventory; a CLI may run the 27 but 3272 / 3394 / 3432 are **not success targets**; **0-of-7 repaired is an allowed outcome**; IGF2R 3356 out; the 27 stay outside F-004 | `test_seven_signed_linker_parents_are_the_primary_inventory` · `test_zero_of_seven_repaired_is_allowed` |
| **T-1149** | **Scope fences:** **not piecewise-v2** (no pieces / domain intervals as the fit unit / linker-inherit), **not an RMSD Spec** (3272 / 3394 out of primary), **not a domain Spec**; **3432 stays accept-refuse** (signed triage — not re-opened, not reclassified, not a D-128 miss); no invented accession for the five parents this log does not carry | `test_not_piecewise_v2_not_rmsd_spec_not_domain_spec` · `test_3432_stays_accept_refuse` · `test_no_invented_accessions_for_unrecorded_parents` |
| **T-1150** | **Artifacts are a fifth sibling tree:** `linker_seam/{parent_id}/` with `seams.jsonl` + `seam_honesty.jsonl`; `algorithm=linker_local_kabsch_then_winning_tile`; `decision=D-128`; do **not** overwrite assembler / `kabsch/` / `confidence_kabsch/` / `piecewise_kabsch/`; prior paths stay callable | `test_artifact_dir_is_sibling_linker_seam` · `test_prior_paths_stay_callable_and_are_not_overwritten` |
| **T-1151** | **Standing honesty carried forward:** served stays **assembler** (no auto-flip); **D-126 remains the best experimental path until proven otherwise**; the **D-127 failed experiment stays disclosed** (PASS 17 / REFUSE 10 / FAIL 0, 0 of 3 recovered, regress 5 vs D-125 and 7 vs D-126); §7 Method is **mandatory at B** and this PR ships no Method edit; ops report fields name the honesty counts and confusion vs D-125 / D-126 / D-127 (**not a CI assert**) | `test_served_stays_assembler_and_d126_stays_best_experimental` · `test_d127_failed_experiment_stays_disclosed` · `test_method_surface_is_mandatory_at_b_and_not_edited_here` · `test_ops_report_fields_name_honesty_and_confusion` |
| **T-1152** | **PR split + hard stops:** ship index and Spec §8 distinguish the **Spec** (on `main`) from **D-128-A** (this PR; **CPU, no rent**) and **D-128-B** (later Emma GO); PLAN + ARCHITECTURE point at D-128; hard stops are written; **no `hold48_*.py` edit** (D-125 / D-126 / D-127 modules sha256-pinned; D-128-A is a fifth sibling module with no pieces and no trim) | `test_ship_index_distinguishes_spec_from_ab_build` · `test_plan_and_architecture_point_at_d128` · `test_hard_stops_and_not_ab` · `test_this_spec_pr_does_not_edit_hold48_modules` |

### D-128-A (this PR; T-1153–T-1160) — linker / seam honesty core

Hermetic fixture tests in `tests/test_d128_linker_seam.py`. No Fly. No
GPU. **No ops run, no restitch of the 27, no Fly POST** — this PR
measures no parent and claims no `repaired_of_seven`. The D-125, D-126
and D-127 modules stay sha256-pinned and `core/hold48_stitch.py` is
untouched; D-128-A is a **fifth sibling** module plus its CLI.

⚠ What these tests are for. The failure this BUILD can most easily
commit is the one it exists to catch: reporting a **flattering
statistic** as honesty. Three concrete forms of it are pinned red here.
(1) Measuring the post-apply jump only inside the window that was just
fitted — that is the D-126 lie surface rebuilt inside the fix for it, so
`seam_jump_gt_10` is computed across the **whole** seam. (2) Writing an
unknown as `0.0` or reporting it as honest — a null jump stays null and
`honest` stays null. (3) Quietly exempting the one path whose tree does
not record the metric: **D-125 records no jump at all**, so its row is
**measured from the artifacts D-125 itself wrote**, and falls back to a
stated absence rather than a number. ⚠ Prior trees are **reads** —
a byte-digest of all four is compared before and after a run.
⚠ **0-of-7 repaired is an allowed outcome**, so nothing here rewards a
pass count.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1153** | Window refuse table (Spec §2): window Cα `< 3` → `overlap_ca_lt_3` with a null RMSD; window weighted RMSD `> 10.0 Å` → `rmsd_gt_10` with the RMSD recorded and a **null** post-apply jump; degenerate / collinear covariance → `singular_covariance`. No transformed PDB, no D-128 `stitched.pdb`, seam + honesty rows still written | `test_window_n_ca_lt_3_refuses` · `test_window_rmsd_gt_10_refuses` · `test_window_singular_covariance_refuses` |
| **T-1154** | **`seam_jump_gt_10` is the D-128 refuse and is measured across the whole seam.** A window whose weighted RMSD passes still refuses when overlap residues outside the ±32 aa window keep their displacement; the seam's honesty row reads `honest = false`; the reason name is **not** D-127's `linker_jump_gt_10` and that name is not in D-128's reason set | `test_post_apply_whole_seam_jump_gt_10_refuses` · `test_seam_jump_reason_is_not_d127s_linker_reason` |
| **T-1155** | **W = 32 is pinned and only the window moves.** Centre is derived from the stored tile windows; `window_start` / `window_end` / `window_half_width_aa` are centre ± 32; the Cα at centre + 32 lands on the reference frame while centre + 33 is **byte-unchanged** and inherits nothing; a wider half-width is never the writer's default | `test_window_half_width_is_32_and_only_that_window_moves` · `test_window_bounds_are_not_tuned_per_parent` |
| **T-1156** | **Accept feeds the existing assembler.** Full accept calls `winning_tile` / `write_stitched`, keeps all-atom records, and leaves off-block PAE **null, never 0**; provenance carries `algorithm` / `decision` / `window_half_width_aa` / ε / gate / `no_trim_loop` / `no_domain_pieces_fitted` / `no_linker_inherit` / `served_path=assembler` / `seams_solved=false`. The offending seam may be identified `from_d127_refuse` **or** `from_measured_jump`, and a seam with neither is a **recorded absence** that is accepted without a transform and is **not** counted as repaired | `test_full_accept_feeds_winning_tile_and_pae_stays_null` · `test_offending_seam_can_come_from_the_prior_d127_refuse` · `test_no_offending_seam_is_a_recorded_absence_not_a_repair` |
| **T-1157** | **§1a rows exist for all four paths and name how each is known.** D-125's row is `measured_from_path_artifacts` (its `seams.jsonl` carries no jump); D-126 / D-127 rows are `read_from_path_record`; only D-127 carries linker fields, the others are absent rather than `0`; an absent tree is one row with `tree_absent`; a path that refused before any transform is `refused_before_transform` with `honest = null`; `honest` always equals the gate applied to the jump, and **`honest_for_jump(10.0)` is true while `10.0000001` is false** | `test_honesty_rows_exist_for_every_path_and_name_their_source` · `test_absent_tree_is_an_honest_absence_with_a_reason_never_a_zero` · `test_refused_prior_path_is_unknown_not_honest` · `test_honesty_gate_is_the_existing_ten_angstrom_gate_and_does_not_loosen` · `test_seam_max_ca_jump_is_null_when_there_is_nothing_to_measure` |
| **T-1158** | **Fifth sibling tree; prior trees are reads.** A D-128 run changes only files under `linker_seam/`; byte digests of the assembler, `kabsch/`, `confidence_kabsch/` and `piecewise_kabsch/` trees are identical before and after, and none gains a `seam_honesty.jsonl`; `refuse_sibling_overwrite` raises for each of the four **and** — the catch-all — for any destination not under a `linker_seam/` path even when **no** prior dir is passed in; D-125 / D-126 / D-127 writers, their CLIs and the assembler stay independently callable; the three prior modules stay sha256-pinned and `hold48_stitch.py` names no D-128; all-or-nothing clears stale partials | `test_linker_seam_dir_does_not_overwrite_the_four_existing_paths` · `test_only_a_linker_seam_directory_may_receive_d128_artifacts` · `test_d128_writes_nothing_outside_its_own_tree` · `test_reading_prior_trees_never_writes_to_them` · `test_prior_paths_and_the_assembler_stay_independently_callable` · `test_sibling_modules_bytes_stay_pinned` · `test_all_or_nothing_parent_refuse_clears_partial_success` |
| **T-1159** | **Inventory.** The seven are the primary set and a subset of the 27; IGF2R 3356 is refused by both the writer and the CLI; **3272 / 3394 / 3432 are runnable and recorded but are not success targets**, and **3432 is never counted in `repaired_of_seven`**; the CLI runs a must-hunt parent and prints the §1a honesty report | `test_seven_signed_linker_parents_are_the_primary_inventory` · `test_3432_stays_accept_refuse_and_the_rmsd_class_is_out_of_primary` · `test_3432_is_recorded_by_the_cli_and_is_never_a_d128_miss` · `test_cli_refuses_parent_ids_outside_the_inventory_including_igf2r` · `test_cli_runs_a_must_hunt_linker_parent_and_reports_honesty` |
| **T-1160** | **Ops report + the fences.** §11 fields are emitted, a drop against any prior path is a **named finding**, `repaired_of_seven` counts only recorded repairs among the seven and names its own source (`none_supplied` vs `repair_records`), and `0` is allowed; the module carries **no trim symbols and no piecewise-v2 symbols** (no `DomainInterval`, `domain_intervals`, `fit_domain_piece`, `inherit_piece_for_residue`, `PieceFit`, `UNIPROT_CACHE`, no `core.hold48` import) and no third-party import; ε = 1e-3; **neither module nor CLI claims a seam is solved, fixed, or superimposed** | `test_ops_report_names_drops_and_allows_zero_of_seven` · `test_repaired_of_seven_counts_only_recorded_repairs` · `test_confusion_report_cli_reads_outcome_files` · `test_no_trim_loop_and_no_piecewise_v2_in_the_module` · `test_neither_module_nor_cli_claims_a_seam_is_solved` · `test_epsilon_and_weight_rule_are_pinned` |

### D-128-B (already on `main`, `cd071d7` / #248; T-1161–T-1171) — UI five-path honesty + the mandatory Method addendum

Hermetic fixture tests in `tests/test_d128_b_five_path.py`, plus the
vitest suites for `AssemblyReview.jsx` / `MethodNote.jsx`. No Fly. No
GPU. **No ops run, no restitch, no Fly POST** — this PR measures no
parent. B **reads** A's `linker_seam/{parent}/` tree; it implements no
part of the algorithm and edits none of the five stitch modules, whose
bytes are sha256-pinned by the suite. Cite Spec §6 (UI) and §7 (Method).

⚠ The D-128-specific hazard these exist for: A's §1a rows are
**cross-path** — four trees, every seam, the jump each path *ends* with —
so the tempting collapse is a **mean jump per path**, an **“N of M seams
honest” tally**, or a **best-path badge**. Any of them would hide
**which** path is dishonest **where**, which is the entire content of
§1a, and would be the D-126 lie surface re-created one level up inside
the fix for it. **B renders one row per `(path, seam)` and derives no
average.** ⚠ **Unknown is not honest** and **null is not `0.00 Å`**;
the verdict is recomputed from A's jump with A's gate, so a recorded
`honest: true` above **10.0 Å** is overridden fail-closed. ⚠ Spec §7
makes the Method addendum **mandatory**: D-128 is not “done” without it,
so T-1169 is a ship gate, not documentation polish. ⚠ Default served =
assembler. ⚠ 10.0 Å gate is reported, never moved.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1161** | `### D-128-B —` exists in the living log (the check is the heading, not a citation of one); the Emma bar cites Spec §6 + §7 and D-128-A `9e65cbf`, names the no-average hazard and “unknown is not honest”, and keeps served = assembler; the ship index carries the same bar | `test_d128_b_heading_exists_in_the_living_log` · `test_emma_bar_cites_d128a_and_spec_sections_six_and_seven` |
| **T-1162** | Missing `linker_seam/` tree → no D-128 path implied; no invented jump / window / RMSD / honesty verdict; an absent tree is **not** “no dishonest seams”; the seam note names a fifth path only when the tree is on disk | `test_missing_linker_seam_tree_does_not_imply_d128_path_or_invent_metrics` · `test_seam_note_names_the_fifth_path_only_when_the_tree_is_on_disk` |
| **T-1163** | Present tree → **five** paths named; persist stems do not collide (`stitched` vs `kabsch/{parent}` vs `confidence_kabsch/{parent}` vs `piecewise_kabsch/{parent}` vs `linker_seam/{parent}`); default served = assembler and the D-128 block is never `default_served` | `test_present_tree_names_five_paths_and_stems_do_not_collide` · `test_empty_block_stem_never_equals_an_earlier_path` |
| **T-1164** | **One row per `(path, seam)`, never an average.** All four paths' §1a rows render with their own jump, three-valued `honest`, and `source`; **no mean / tally / score / best-path field exists in the payload or is computable in the reader**; linker fields appear **only** on the path that defines linkers and are absent (not `0`) elsewhere, keyed off A's `PATHS_DEFINING_LINKERS` rather than a file's boolean; a null jump is an absence with a reason, **never `0`** and **never honest**; a recorded `honest: true` above the gate is overridden **fail-closed** and the disagreement is surfaced; the gate is exactly A's (`10.0` honest, `10.0000001` not) and B declares none of its own | `test_seam_honesty_rows_render_per_path_and_are_never_averaged` · `test_only_the_path_that_defines_linkers_shows_linker_fields` · `test_a_path_that_does_not_define_linkers_cannot_smuggle_them_in` · `test_null_jump_is_an_absence_with_a_reason_never_zero_and_never_honest` · `test_recorded_honest_above_the_gate_is_overridden_fail_closed` · `test_honesty_verdict_is_the_existing_ten_angstrom_gate_exactly` |
| **T-1165** | **D-128's own window fit renders from A's JSON:** `window_start` / `window_end` / `window_half_width_aa` = 32 / `seam_centre` / `n_ca` / weighted `rmsd_angstrom` / the jump **before and after** / `offending_seam_source`; a refuse-before-transform stays **null, never 0**; a seam that offended nothing is a recorded absence with no window; `R` / `t` are not surfaced as measurements | `test_window_fit_row_renders_from_as_json` · `test_window_fit_row_stays_null_on_refuse_before_transform` · `test_a_seam_that_offended_nothing_is_a_recorded_absence` · `test_projection_drops_the_rigid_transform_itself` |
| **T-1166** | **Fail-closed.** A dishonest seam withholds the D-128 success PDB even with `stitched.pdb` on disk; an **unknown** seam withholds it too; an all-honest accept still reads as one and is still not served; the 10.0 Å gate and W = 32 are reported, not re-declared, and the live constants stay `10.0` / `32` / `1e-3`; a tree with no honesty rows is an absence with a reason, not “0 dishonest seams” | `test_dishonest_d128_seam_never_carries_a_success_pdb` · `test_an_unknown_seam_also_withholds_the_success_pdb` · `test_an_all_honest_accepted_parent_may_name_its_own_pdb` · `test_gate_and_window_are_reported_not_redeclared` · `test_a_tree_without_honesty_rows_is_an_absence_not_zero_dishonest` |
| **T-1167** | `assembly_review.five_path` carries the honest empty block and the read tree; D-125-B `dual_path`, D-126-B `triple_path`, and D-127-B `four_path` survive unchanged and gain no fifth key; assembler download stem stays `stitched` | `test_assembly_review_carries_five_path_empty_and_does_not_imply_d128` · `test_assembly_review_reads_fifth_sibling_tree_beside_assembler_dir` |
| **T-1168** | B does not re-implement persist, **implements no part of the algorithm** (no window fit / align / transform / honesty collection / ops report in the reader — all still A's), does not invoke A's writer or CLI, and edits none of the five modules (`hold48_linker_seam.py`, `hold48_piecewise_kabsch.py`, `hold48_confidence_kabsch.py`, `hold48_kabsch.py` sha256-pinned; `hold48_stitch.py` names no D-128); a byte-digest of all five trees is identical before and after a read; forbidden language stays parked across reader / reads / routes / JSX | `test_b_does_not_reimplement_persist_writer` · `test_b_implements_no_part_of_the_algorithm` · `test_b_does_not_invoke_a_restitch_or_an_ops_run` · `test_algorithm_modules_are_not_edited_by_this_ui_pr` · `test_the_ui_pr_writes_nothing_to_any_path_tree` |
| **T-1169** | **Mandatory Method (Spec §7).** Both surfaces name the **five**-step stitch-path train in order with D-128's ±32 aa window and the 7-of-10 linker motivation; define **dishonest** as a claim about the **structure file, not about a person**; carry the refuse table with the **10.0 Å gate staying**; name seam numbers as **measurements, not a verdict**, with **one row per path per seam and never an average** and “unknown jump is not honest”; keep honest-empty and “does not invent”; and **do not gut** the D-121 / D-125-B / D-126-B / D-127-B sections | `test_d128_b_method_addendum_names_the_five_step_stitch_path_train` · `test_d128_b_method_addendum_defines_dishonest_about_the_file` · `test_d128_b_method_addendum_names_the_refuse_table_and_keeps_the_gate` · `test_d128_b_method_names_seam_disclosure_as_measurement_and_refuses_an_average` · `test_method_addendum_does_not_gut_the_four_earlier_sections` · `test_method_obligation_is_recorded_as_discharged_by_this_pr` · `adds the mandatory D-128-B addendum naming the whole five-step stitch-path train` |
| **T-1171** | **Phase 5 scope split (Matt SIGNED, via Emma).** **IN:** both Method surfaces say **accept-refuse ≠ silence** in those terms — an accepted refusal is a **record**, not a parent dropped / skipped / excluded from the inventory (3432 named as the standing example, every one of the seven carrying a written row), and the negative result is owned (“the measurement came out negative”); and both refuse a **linker-v2** — another window family after 0-of-7 is D-127's mistake repeating, named as *decompose differently until the count improves*, with **D-126 still the best of them**. **OUT:** this PR ships **no Phase 5 named-refuse label vocabulary** on any surface (reader / card / both Method sections), while the log **does** carry the deferred inventory (2938, 2939, 3179, 3190, 3321, 3368, 3566, 3432) for the later Trinity Phase 5 Spec — recording a list is not shipping a label. **Phase 4 (3272 / 3394) is not labelled with a D-128 refuse:** the D-128 refuse listing contains exactly the seven, and neither Phase 4 parent, though both stay legible where D-127's histogram and D-126's recovered pair already carry them | `test_method_says_an_accepted_refusal_is_a_record_not_a_silence` · `test_method_refuses_a_linker_v2` · `test_this_pr_ships_no_phase5_named_refuse_label_surface` · `test_phase4_parents_are_not_labelled_with_a_d128_refuse` · `says an accepted refusal is a record rather than a silence, and refuses a linker-v2` |
| **T-1170** | **D-128 OPS honesty (MANDATORY §7 inject, Matt GO via Emma).** Method discloses the run **as recorded** — PASS 0 / REFUSE 7 / FAIL 0 / SKIP 0 at tip `9e65cbf`, out_root `linker_seam_ops_2026-09-05`; `recovered_of_seven` = `repaired_of_seven` = **0**; the refuse histogram (`seam_jump_gt_10` ×6 · `rmsd_gt_10` ×1) with its parent ids; **the allowed zero never appears without the named give-back beside it** (`n_d125_pass_d128_refuse` = 5, `n_d126_pass_d128_refuse` = 6, both D-127 counts 0), position-checked so it cannot drift to another part of the page; **D-126 still named the best experimental path** (2 of 5 vs 0 of 3 vs 0 of 7) and the **D-127 failed experiment still disclosed as D-127's**; no gate loosened, served path never flipped, **3432 stays accept-refuse**, W = 32 named as a pinned default rather than a measured optimum; D-128's `seam_jump_gt_10` never conflated with D-127's `linker_jump_gt_10`; seven refuses = seven **recorded** outcomes; the log records the inject with its provenance **and names the superseded draft claim**; and this PR ships no ops run, no new Spec, and no Fly POST | `test_ops_figures_are_internally_consistent_before_they_are_quoted` · `test_method_discloses_the_d128_ops_run_as_recorded` · `test_method_never_reports_the_allowed_zero_without_its_give_back` · `test_method_keeps_d126_best_and_the_d127_failed_experiment_disclosed` · `test_method_refuses_to_loosen_a_gate_flip_the_served_path_or_reopen_3432` · `test_method_does_not_conflate_d128_reason_names_with_d127s` · `test_living_log_records_the_ops_inject_with_its_provenance` · `test_this_pr_ships_no_ops_run_no_new_spec_and_no_fly_post` · `discloses the D-128 OPS run and never states the allowed zero without its give-back` |

### D-130-A (this PR; T-1200–T-1209) — Phase 4 residual-RMSD core

Hermetic fixture tests in `tests/test_d130_residual_rmsd.py`. **Stdlib only**
— constructed tiles in `tmp_path`, **no Fly, no GPU, no ops run, no
re-measurement of any parent**. Cite D-130 Spec §1a / §1b / §2 / §3 / §5 /
§11, `### D-130-A`, and the **Emma BUILD GO Phase 4 residual RMSD
2026-09-06** (Matt via Emma; the **#252 merge is the GO**).

⚠ **Four failures these exist to redden**, and they are the ones this Spec
spent its whole length fencing.

**The floor read backwards** (T-1200 / T-1201). `floor ≤ 10.0 Å` proves
*nothing* — not that a passing fit exists, not that a parent is recoverable,
and never that the gate is too strict. T-1200 exercises
`RMSD(R, t) ≥ dRMSD / 2` as **arithmetic** over real rigid transforms
including far-from-optimal ones, checks the quantity is **rigid-invariant**,
and pins that the bound is **not tight** — which is exactly why `irreducible`
is *sufficient and never necessary*. T-1201 pins that the certificate is
issued **before any fit** and that no identifier in the module computes a
"distance to recovery", a per-parent exception, or a named exclusion.

**A search dressed as an audit** (T-1204). §1b's correction is decided by
**residue identity**. Ambiguity — **none** *or* **more than one** agreeing
offset — must **refuse** rather than pick, a pairing that was already right
must **not** be refitted, and the audit must never reach for an RMSD, a
pLDDT, or a seam jump to break a tie.

**A fifth knob smuggled in** (T-1206). The only permitted fit is D-125's, so
the test compares this module's `R`, `t` and RMSD against
`core.hold48_kabsch.kabsch_rotation_translation` **on the same pairs** rather
than trusting a docstring, and the module may define no window, no piece, no
weight and no trim — checked against **AST identifiers**, not a substring
hunt, because D-128-B learned that banning bare words fires on the very copy
that forbids them.

**A statistic laundered across paths** (T-1203). A prior path's recorded
`rmsd_angstrom` is a *different statistic* in four of the five trees, so
`rigid_rmsd_angstrom` is **measured** from that path's own artifacts, an
absence stays an absence with a reason, and the five prior trees are
**byte-identical** after a D-130 run.

⚠ **Never solved.** No test here rewards a pass count; `recovered_of_two` = 0
is asserted to be an **allowed** outcome that names its own source, and an
accept with no register correction is asserted **not** to be a recovery.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1200** | **The floor is a proved bound, it is the Spec's constant, and it is not tight.** `RMSD(R, t) >= dRMSD / 2` holds for **every** rigid transform on constructed point sets (five rotations × three translations, including a far-from-optimal one); the dRMSD is **rigid-invariant** under motion of either copy; a **zero** floor coexists with an achieved RMSD over **50 Å**; fewer than two pairs is **null**, never `0.0`, while mismatched set sizes raise. ⚠ **Added after a mutation audit found the divisor unpinned:** the inequality above is satisfied by `dRMSD / 4` and by `dRMSD / 400` — *a weaker claim passes a weaker test* — so the constant is pinned as an **identity** (`rmsd_floor(x) == x / 2`, with the `2 / (n(n-1))` normalisation hand-computed at n = 2 and n = 3) **and** as **attained**: on two corresponded points the optimal rigid placement achieves *exactly* `dRMSD / 2`, so `/ 2` is the greatest lower bound the proof gives rather than a safer guess | `test_the_floor_bounds_every_rigid_transform` · `test_the_floor_constant_is_the_specs_and_is_attained` · `test_the_floor_is_rigid_invariant` · `test_the_bound_is_not_tight_so_irreducible_is_sufficient_never_necessary` · `test_an_unmeasurable_drmsd_is_null_and_never_zero` |
| **T-1201** | **One-directional, and certified before any fit.** A floor over the gate refuses **`rmsd_irreducible`** with `rmsd_angstrom` / `pre_fit_rmsd_angstrom` / `max_ca_jump_angstrom` all **null** and **no** audit run; `floor_exceeds_gate` is three-valued (`True` above 10.0, `False` **at** 10.0 — the gate does not loosen at the boundary — and **null** for a null floor) against the **existing** `RMSD_REFUSE_ANGSTROM`; and no module identifier computes a distance-to-recovery, a recovery forecast, a per-parent gate, or a named exclusion | `test_a_floor_over_the_gate_refuses_before_anything_is_fitted` · `test_floor_exceeds_gate_is_three_valued_and_uses_the_existing_gate` · `test_the_module_computes_no_distance_to_recovery` |
| **T-1202** | **The three-valued class and its precedence.** The class set is exactly `{irreducible, placement, unknown}`; **unknown** takes a null floor, a null achieved RMSD, or `n < 3`; **`irreducible` wins over `unknown`** when the floor is known and over the gate — without which §2's certificate would be unreachable — while a **null** floor still cannot certify; and a **passing** seam is `placement` yet lands in `n_placement_within_gate`, so §11's `n_placement` keeps the Spec's own condition and a pass never inflates a count the Spec calls *not a recovery forecast* | `test_unknown_is_neither_irreducible_nor_placement` · `test_irreducible_wins_over_unknown_when_the_floor_is_known` · `test_a_pass_is_placement_and_is_never_counted_as_a_recovery_forecast` |
| **T-1203** | **§1a rows for every path, with per-field provenance.** Rows exist for all **five** paths; an absent tree is **one** row with `absence_reason = tree_absent`, every number **null** and the class **unknown** (never a zero, never an assumed pass); an empty tree says `no_seam_rows`; a path that **refused** carries a null achieved RMSD with `refused_before_transform` while its **floor is still known** (the floor is a property of the two tiles); the achieved RMSD's source is `measured_from_path_artifacts` and the module never reads `row["rmsd_angstrom"]` from a prior record; the floor's source is `measured_pre_transform_from_input_tiles`; every written row carries the **direction** of the bound; and all prior trees are **byte-identical** before and after a D-130 run | `test_rows_are_written_for_every_path_even_when_a_tree_is_absent` · `test_a_prior_path_that_refused_carries_a_null_achieved_rmsd` · `test_the_achieved_rmsd_is_measured_not_copied_from_a_prior_record` · `test_a_d130_run_leaves_every_prior_tree_byte_unchanged` · `test_an_empty_prior_tree_reports_its_own_reason` |
| **T-1204** | **The audit is decided by identity, never by score.** A **verified** declared pairing yields `register_offset_aa = 0`, is **not refitted**, and refuses on D-125's own `rmsd_gt_10`; a **unique** identity-agreeing offset is the correction and, refitted, accepts with `recovered` **True**; **no** agreeing offset refuses `correspondence_unverifiable` with `identity_evidence = no_offset_agrees_…`; **more than one** refuses with `multiple_offsets_agree_…` and `register_offset_aa` **None** (no tie is broken); an unreadable / `UNK` residue name refuses rather than matching two blanks; and `audit_correspondence`'s body contains no rmsd / pLDDT / jump / min / max / sorted | `test_a_verified_declared_pairing_is_not_refitted` · `test_a_unique_identity_determined_offset_is_the_correction` · `test_no_agreeing_offset_refuses_rather_than_guessing` · `test_more_than_one_agreeing_offset_refuses_instead_of_picking_one` · `test_unreadable_residue_identity_refuses` · `test_the_audit_never_reads_a_score` |
| **T-1205** | **The corrected correspondence is the FULL identity-agreeing overlap.** `paired_ca_for_offset` returns **every** pair the two spans admit at that offset — a trimmed subset reddens — and no module identifier names a trim, a prune, a `drop_worst`, a `keep_best` or a subset; the candidate offset range is **derived from the two tile spans** (each candidate carrying at least `OVERLAP_CA_MIN` pairs) with no scan-width constant to widen | `test_the_corrected_correspondence_is_the_full_overlap_and_is_never_trimmed` · `test_candidate_offsets_are_derived_from_the_spans_not_tuned` |
| **T-1206** | **The fit is D-125's, unchanged.** `fit_correspondence`'s `R`, `t` and RMSD are **identical** to `kabsch_rotation_translation` on the same pairs and agree with D-125's `fit_overlap_kabsch`; the **whole** moving tile is transformed (no atom keeps its coordinates, which a window fit would leave behind); and the module defines no `WINDOW_HALF_WIDTH_AA`, `WEIGHT_EPSILON`, `pair_weight`, weighted Kabsch, `DomainInterval`, piece inherit, or window helper | `test_the_fit_is_d125s_transform_on_the_same_pairs` · `test_the_whole_moving_tile_is_transformed_not_a_window` · `test_the_module_defines_no_window_no_piece_no_weight` |
| **T-1207** | **Refuse table, fail closed, all-or-nothing.** Overlap Cα `< 3` refuses `overlap_ca_lt_3` with a **null** floor and class **unknown**; a degenerate covariance refuses `singular_covariance`; a refuse **after a prior accept** deletes the earlier `stitched.pdb` and `tile*_transformed.pdb` while **keeping** `seams.jsonl` and `residual_decomposition.jsonl`, and `provenance.json` records `accepted` / `recovered` **False**, `served_path = assembler`, `seams_solved = False`, `zero_of_two_recovered_is_allowed = True`; one refusing seam refuses the **parent** with no partial transformed tile; and the reason set is exactly the Spec's five, containing **neither** `linker_jump_gt_10` **nor** `seam_jump_gt_10` | `test_overlap_ca_lt_3_refuses` · `test_singular_covariance_refuses` · `test_a_refuse_writes_its_rows_and_clears_a_prior_success` · `test_the_parent_is_all_or_nothing` · `test_the_refuse_reason_set_is_the_specs_and_conflates_no_prior_name` |
| **T-1208** | **The sixth tree, no overwrite, the inventory.** `residual_rmsd/{parent}/` collides with none of the five sibling dirs or the assembler dir; a write onto the assembler or any of the four prior trees is **refused**, and so is a destination nobody named that is outside `residual_rmsd/`; a parent outside D-125's **27** is refused and writes nothing; the Phase 4 pair is exactly `{3272, 3394}`, **disjoint** from the eight `accept-refuse` parents, both sets inside the runnable 27; and an `accept-refuse` parent can be **recorded** without becoming a Phase 4 recovery | `test_the_sixth_tree_name_collides_with_none_of_the_five` · `test_a_write_onto_any_prior_tree_is_refused` · `test_a_parent_outside_the_27_is_refused` · `test_the_phase_4_pair_is_the_inventory_and_phase_5_is_not_reopened` · `test_an_accept_refuse_parent_can_be_recorded_without_becoming_a_target` |
| **T-1209** | **The §11 report, the CLI, and module hygiene.** Every required §11 field is emitted with the standing flags (`zero_of_two_recovered_is_allowed`, *named refuse after a failed hunt is a complete outcome*, *unknown is neither*, `served_path = assembler`, `seams_solved = False`); `recovered_of_two` = 0 names its source as `none_supplied` vs `recovery_records`, so a zero is never read as a measured zero; a drop on a prior path's PASS set is a **named finding**, and `n_d126_recovered_d130_refuse` fires on **3394**; the module's **import graph** contains only stdlib and `core` (checked against `sys.stdlib_module_names`, not a hand-kept allowlist); the five prior modules are **sha256-pinned**; the assembler is imported, never re-implemented; and the CLI writes the sixth tree, refuses a parent outside the 27, **refuses a decomposition report with no manifest** (the floor comes from the pre-transform tiles), writes nothing in report mode, and prints the give-back beside the allowed zero | `test_the_ops_report_carries_every_required_field` · `test_zero_recovered_names_its_source_and_is_never_a_measured_zero` · `test_a_drop_on_a_prior_paths_pass_set_is_a_named_finding` · `test_the_module_imports_no_third_party_package` · `test_the_prior_modules_stay_byte_identical` · `test_the_assembler_is_called_and_never_replaced` · `test_cli_restitches_into_the_sixth_tree` · `test_cli_refuses_a_parent_outside_the_inventory` · `test_cli_decomposition_report_needs_the_input_tiles` · `test_cli_decomposition_report_reads_without_writing` · `test_cli_confusion_report_names_the_drop` |

### D-130 Spec (already on `main`, `854c2ab` / #252; T-1191–T-1199) — Phase 4 residual-RMSD hunt

Hermetic docs pin tests in `tests/test_d130_residual_rmsd_spec.py`. **Stdlib
only** — they read `docs/README.md`, `docs/SPEC-residual-rmsd-hunt.md`,
`docs/SPEC-phase5-named-refuse.md`, `docs/SPEC-linker-seam-honesty.md`,
`docs/decisions.md`, `docs/PLAN-ui-post-wave2-endstate.md`,
`docs/Test_Plan.md`, `ARCHITECTURE.md` and the `core/hold48_*.py` bytes.
**No DB, no Fly, no GPU, no artifact read, no ops run, no re-measurement.**
Cite: **Emma/Matt GO Phase 4 RMSD 2026-09-05 ~20:39 PT** (*"Go phase 4"*)
against **vault `D-0043` roadmap Phase 4**; `### D-130`; `### D-129` §6 (the
boundary this GO crosses); the D-125 / D-126 / D-127 / D-128 figures **as
recorded**.

⚠ **Three failures these exist to redden.** **Inventory bleed** (T-1193):
the hunt quietly grows a linker half, a domain half, or a third parent. The
pin says *"residual RMSD only — never dual with linker/domain-partition"*,
and a Spec that hunts everything has **pre-registered nothing** — whichever
half happens to pass gets reported as the result. T-1192 pins the §3
inventory table to **exactly** {3272, 3394} and keeps the **eight**
`accept-refuse` parents out of it; T-1193 pins the mode fences by name.
**Gate erosion** (T-1194): a `0 of 2` read as evidence the **10.0 Å**
threshold is too strict. Every loosening route is fenced — no per-parent
exception, no named-exclusion, **no trim-as-fix**, no threshold Spec-as-fix
— and the **D-126 lie surface** is cited on **3272 itself**, so the trim ban
rests on an artefact rather than on a preference. **The floor read
backwards** (T-1195): treating `rmsd_floor_angstrom ≤ 10.0 Å` as a promise
that a parent is recoverable, or as an argument against the gate.

⚠ **The bound is checked as arithmetic, not asserted as prose** (T-1195).
`RMSD(R, t) ≥ dRMSD / 2` is exercised on constructed point sets under real
rigid transforms — including transforms far from optimal, because the claim
is about **every** rigid motion — plus rigid-invariance of the floor, and a
fixture where a **zero** floor coexists with a **> 50 Å** achieved RMSD.
That last one is the pin behind *"`irreducible` is **sufficient and never
necessary**"*: a Spec asserting a bound its own tests cannot reproduce would
be the pointer-is-not-proof failure again (D-062 / method-note item 7).

⚠ **Docs only** (T-1198): the five `core/hold48_*.py` modules are
**sha256-pinned** and must name no D-130, `docs/method-hold48-tiles.md` is
**byte-pinned** (the Method edit belongs to D-130-B, the #243 / #246 / #249
pattern), and no `ui/src/` path appears.
⚠ **Phase 5 is not spent to buy Phase 4** (T-1199): the D-129 §6 cross-link
must say **Spec-governed** *and* **still not `accept-refuse`** — *a governed
hunt is an open fate* — while §4's standing disclosure and §7's freeze
survive intact.

⚠ **Two D-129 pins were amended, not loosened, by this PR** — named here so
the change is a recorded choice. `test_d129_is_the_next_free_decision_id`
asserted `max(ids) == 129`; spending D-130 reddened it **by design**, and it
now enumerates the successor (`[130]`, exactly) **and** requires D-130 to be
this Spec's heading, so a stray `### D-131` still reddens.
`test_ship_index_plan_architecture_and_test_plan_carry_d129` asserted
*"Active ship — D-129"* and *"D-129 Spec … **Yes — this PR.**"*, both true
in flight and false now that #249 / #250 / #251 have landed; they now pin
the D-129 Spec as **shipped, with its PR number**, so dropping or
renumbering it still fails.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1191** | `### D-130 —` exists in the living log (**the check is the heading, not a citation of one** — D-001 / D-062 / method-note item 7), and so do the `### D-129` / `### D-129-B` / `### D-129-C` / `### D-128` / `### D-128-A` / `### D-127` / `### D-126` / `### D-125` headings it cites; the Spec file exists and names itself **algorithm authority**; the **Emma/Matt GO Phase 4 RMSD 2026-09-05 ~20:39 PT** is bound with its route, its date and **vault `D-0043`** (external numbering, **not** repo `### D-043`); the pin is quoted **verbatim** in §12 with every clause mapped to the section that binds it; no vault prose is invented and the vault's absence from this repo is stated; **D-130 collides with nothing** (highest `### D-NNN` is 130, exactly one entry, and **no `### D-130-A/B` exists** — A and B are unauthorised) | `test_d130_heading_exists_in_the_living_log` · `test_spec_file_exists_and_names_its_authority` · `test_the_phase_4_go_is_bound_with_provenance` · `test_the_pin_is_quoted_verbatim_and_every_clause_is_placed` · `test_no_vault_prose_is_invented` · `test_d130_is_the_next_free_decision_id` |
| **T-1192** | **The inventory is exactly the pair.** §3's table holds **exactly** 3272 and 3394 — a third row reddens — each with its accession (`Q6V0I7` / `Q8TDW7`) and its recorded `rmsd_gt_10` refuse; the **eight** `accept-refuse` parents are **absent** from the inventory and **present** in the out-of-inventory table with their fate, the two sets are **disjoint**, and **Phase 5 is not reopened** (3432 unchanged, nothing re-hunted, nothing called a D-130 miss); **no accession is invented** — every UniProt-shaped token in §3 is one this log already carries; and the §3 histories are marked **reads of the record**, not re-measurements | `test_the_primary_inventory_is_exactly_the_phase_4_pair` · `test_the_accept_refuse_eight_are_out_and_phase_5_is_not_reopened` · `test_no_invented_accessions` · `test_recorded_history_is_marked_as_read_not_re_measured` |
| **T-1193** | **One failure mode, and bleed is written as forbidden.** The Spec, the log, the index and `ARCHITECTURE.md` all name a **single** failure mode — **residual RMSD**, the `rmsd_gt_10` **whole-overlap** class — and bind the pin's *"never dual with linker/domain-partition"*; **not a linker Spec / not a domain-partition Spec / not both / not a kitchen sink** are each written, along with **no dual-mode Spec** and **no linker-v2 / piecewise-v2 / rmsd-v2**; the earlier families' fit units (**pieces**, **window**, **linker-inherit**, **domain intervals as the fit unit**) are refused in §9; a CLI run of the 27 is allowed **only** as confusion (*not success targets*, *not a Phase 4 recovery*); and the Spec and its log entry **never say solved** | `test_the_failure_mode_is_singular_and_named` · `test_inventory_and_mode_bleed_are_written_as_forbidden` · `test_a_third_parent_cannot_be_added_by_the_cli_run` · `test_spec_never_says_solved` |
| **T-1194** | **The gate stays and cannot be argued down.** **10.0 Å stays** on all four surfaces; **no gate loosen**, **no per-parent exception**, **no named-exclusion**, **no threshold Spec-as-fix**, **not a threshold change**, and *"`0 of 2` does not license one"*; **trim is forbidden with the D-126 lie surface named on 3272** (the **28–68 Å** full-overlap gap behind a small weighted score) and *"any subset selection that improves a number is trim"*; and §1b's fit is pinned as **exactly D-125's, unchanged** — unweighted, untrimmed, full corrected overlap, feeding the **existing** `winning_tile`, with **no new geometry** | `test_the_gate_stays_at_ten_and_every_loosening_route_is_fenced` · `test_trim_is_forbidden_and_the_d126_lie_surface_is_named` · `test_the_only_permitted_fit_is_d125s_unchanged` |
| **T-1195** | **The floor is one-directional, proved, and not tight.** §1a writes the bound as **one-directional** — over the gate it *certifies*, under it, it **proves nothing** — with **`irreducible` sufficient and never necessary**, the three backwards readings (*this parent can be fixed*, *the gate is too strict here*, *a recovery forecast*) each named a **Spec violation**; the inequality is labelled **mathematics, not a measurement**, and **no parent's floor is computed here**; the three-valued class (`irreducible` / `placement` / `unknown`) is written with **unknown belonging to neither**; and the claim is **exercised as arithmetic** — `RMSD ≥ dRMSD / 2` holds across five rotations × three translations, the floor is **rigid-invariant**, and a **zero** floor coexists with a **> 50 Å** achieved RMSD | `test_the_floor_is_written_as_one_directional` · `test_the_floor_is_labelled_mathematics_and_not_a_measurement` · `test_the_claimed_inequality_actually_holds_and_is_not_tight` |
| **T-1196** | **The recovery is an audit, not a search.** §1b is decided by **residue identity**, **never by RMSD** / never chosen by score; a correction must be **unique and identity-determined**, an **ambiguous** result **refuses**, and both *"do not choose among candidate offsets by RMSD"* and *"do not scan a window of offsets and keep the best"* are written; the re-pairing **is not a subset chosen for fit quality**; the audit runs **only** where §1a said `placement` (*running the audit anyway to see what happens is a search*), and an `irreducible` row refuses `rmsd_irreducible`; §1a's **required** rows cover **all five** path trees with `n_overlap_ca` / `rigid_rmsd_angstrom` / `internal_drmsd_angstrom` / `rmsd_floor_angstrom` / `residual_class` / `floor_exceeds_gate`, **no trim / no subset / no window**, **null is not `0.0`**, prior trees **read never rewritten**, each row naming **how it is known**, and *"recovers zero parents has run this Spec"* | `test_the_correspondence_audit_is_decided_by_identity_never_by_score` · `test_the_audit_is_gated_on_the_required_half` · `test_required_half_records_every_path_and_names_how_it_is_known` |
| **T-1197** | **Refuse names, pre-registration, and the report.** §2 carries `overlap_ca_lt_3` / `rmsd_irreducible` / `correspondence_unverifiable` / `rmsd_gt_10` / `singular_covariance`, states the two new names are **new reason names, not renames**, and names D-127's `linker_jump_gt_10` and D-128's `seam_jump_gt_10` as the measurements they **must never be conflated with** (D-125's three are **carried unchanged**), with fail-closed / all-or-nothing / *a refuse is a recorded outcome*; **`recovered_of_two` = 0 is pre-registered before any run** on all four surfaces and a **named refuse after a failed hunt** is a **complete outcome**, with the escalation route closed (*accept-refuse or a dual-path disclose*, **not another RMSD-v2 without a new Matt GO**); §11's thirteen report fields exist, are **not a CI assert**, forbid burying a drop in an accept count, mark `n_placement` as **not a recovery forecast**, name `n_d126_recovered_d130_refuse` as **the count most likely to embarrass the run**, and require the report to separate **measured** from **quoted as recorded** | `test_the_new_refuse_names_are_new_and_are_not_conflated` · `test_zero_of_two_is_pre_registered_and_a_named_refuse_completes_the_spec` · `test_the_ops_report_fields_are_required_and_name_the_embarrassing_one` |
| **T-1198** | **A sixth tree, and a docs-only PR.** `residual_rmsd/` and `core/hold48_residual_rmsd.py` are named as the **sixth sibling**, collide with **none** of `kabsch/` / `confidence_kabsch/` / `piecewise_kabsch/` / `linker_seam/`, and all four are named as **not overwritten** (*may not reuse an earlier name*), with `algorithm=residual_rmsd_decomposition_then_winning_tile` and `decision=D-130`; the five `core/hold48_*.py` modules are **sha256-pinned** and **name no D-130**, `docs/method-hold48-tiles.md` is **byte-pinned**, no `ui/src/` path appears, and the Spec says **no Method file edit** / **no `hold48_*.py` edit** / names `MethodNote.jsx`; §7 is **8th-grade authority** naming its #243 / #246 / #249 precedent, all four prior paths with **0 of 7** / **0 of 3** / **2 of its 5**, the Phase 5 label with its numbers, both Phase 4 parents, the floor with *"proves nothing at all"* and *"never a reason to move the 10.0 Å limit"*, *"we are not adding a fifth way of moving tiles"*, *"fixing zero of the two is an allowed outcome"*, served = **assembler**, and the standing Method limits; and §8's out-of-scope fences are written | `test_the_sixth_tree_and_module_names_collide_with_nothing` · `test_this_spec_pr_edits_no_module_no_method_and_no_ui` · `test_the_method_excerpt_is_authority_and_is_eighth_grade` · `test_out_of_scope_fences_are_written` |
| **T-1199** | **The cross-link moves the hunt, not the fate.** D-129 Spec §6 carries a **Phase 4 amendment (D-130)** naming the GO, pointing at `SPEC-residual-rmsd-hunt.md` and `### D-130`, saying **Spec-governed** *and* **still not `accept-refuse`** (*a governed hunt is an open fate*), **Phase 5 is not reopened**, the **freeze is not repealed**, **the log governs**, 3432 unchanged, and §4's disclosure *may not be softened, dropped, split apart* — and it makes **no** seams-solved claim; D-128's own **Phase 5 amendment (D-129)** survives; the **0 of 7**, **standing**, served = **assembler**, **no auto-flip**, **no F-004** and **D-126 best experimental / callable** are carried on all four surfaces with only the *"Phase 4 RMSD only on explicit Matt GO"* clause **satisfied**; `decisions.md` / PLAN / `ARCHITECTURE.md` / this Test Plan carry D-130 (with `D-130-A` and `D-130-B` marked **later Emma / Matt GO**); and the PR **runs no ops and re-measures nothing**, recording that the tip `544e821` was **confirmed against the remote** rather than taken from the brief (the local checkout was at `cbcb47d`) | `test_the_d129_crosslink_moves_the_hunt_without_moving_the_fate` · `test_the_standing_disclosure_and_the_freeze_survive` · `test_ship_index_plan_architecture_and_test_plan_carry_d130` · `test_this_pr_runs_no_ops_and_re_measures_nothing` |

### D-129-C (already on `main`, `544e821` / #251; T-1187–T-1190) — `must-hunt` hygiene on the live surfaces

Hermetic tests in `tests/test_d129_c_must_hunt_supersession.py`. **Stdlib
only** — no DB, no network, no artifact read, no ops run, no
re-measurement. They read the seven **live** surfaces
(`docs/method-hold48-tiles.md`, `ui/src/components/MethodNote.jsx`,
`ui/src/components/AssemblyReview.jsx`, `ARCHITECTURE.md`, the **living
header** of `docs/README.md` above `## Log (newest first)`,
`docs/decisions.md`, `docs/PLAN-ui-post-wave2-endstate.md`) plus the
sha256 bytes of `core/hold48_*.py`, `app/phase5_named_refuse.py` and
`app/linker_seam_path_read.py`. Cite: **Emma GO 2026-09-06** (*"hygiene
patch ONLY"*); `### D-129-C`; the rollup as recorded by Kaylee at tip
`9e65cbf`, out_root `linker_seam_ops_2026-09-05`.

⚠ **The failure this exists to redden** (T-1187): a live surface names the
accept-refuse **eight** `must-hunt` with **no qualifier in that sentence**.
At `cbcb47d` the MANDATORY §7 provenance inject did exactly that on both
Method surfaces, with the supersession four lines away in the **next
paragraph** — and the page-wide assertion `"must-hunt is what they were
called" in text` was **green** the whole time. A qualifier in the
neighbourhood is not qualification of the claim.

⚠ **The rule is three-valued, not a ban** (T-1189). `must-hunt` stays
available **Phase-4-scoped** (3272 / 3394, for whom it is the *current*
status), as **a negation** (the copy that forbids the badge — banning the
bare words would fire on the sentence that does the forbidding, the trap
D-128-B documented), and **supersession-carrying**. T-1189 asserts all
three forms still occur, so the rule cannot be satisfied by **deletion**.

⚠ **The checker must be able to fail** (T-1188): a bare fixture, an
adjacent-paragraph fixture (the exact `cbcb47d` shape), a JSX
inline-vs-block fixture, and a mixed sentence where a true Phase-4 clause
must not launder a bare one.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1187** | **No live surface carries a bare `must-hunt`.** Every occurrence on the seven enforced surfaces classifies as **Phase-4-scoped**, **a negation**, or **supersession-carrying**, judged **per occurrence** in **its own sentence**; the two surfaces the GO named stay in the enforced set and still contain the token (deletion is not qualification); on both Method surfaces the **§7 provenance inject's own sentence** carries the supersession **and** keeps its tip `9e65cbf` and out_root `linker_seam_ops_2026-09-05`; the `## Log (newest first)` marker that separates the living header from the dated record still exists | `test_no_live_surface_carries_a_bare_must_hunt` · `test_every_go_named_hole_is_actually_in_the_enforced_set` · `test_the_provenance_inject_carries_the_supersession_itself` |
| **T-1188** | **The classifier can go red.** A bare fixture is **BARE**; a fixture whose supersession sits in the **next paragraph** is **BARE** while the same clause **in the same sentence** passes; JSX **inline** tags (`<strong>`, `<code>`) do **not** split a sentence while **block** tags (`</p>`) do; a sentence holding a true `Phase 4 must-hunt` clause **and** a bare one yields **two** verdicts, not one | `test_the_checker_reddens_on_a_bare_occurrence` · `test_adjacent_paragraph_supersession_does_not_count` · `test_the_jsx_reader_splits_on_block_elements_not_inline_ones` · `test_a_true_half_sentence_cannot_carry_a_bare_half` |
| **T-1189** | **Qualifying is not deleting.** All three qualified forms still occur across the live surfaces; both Method surfaces still carry **PASS 0** / **REFUSE 7** / **0 of 7**, `repaired_of_seven`, `n_d125_pass_d128_refuse`, `n_d126_pass_d128_refuse`, *bury a drop under a pre-registration*, the standing **0 of 3** and *D-126 remains the best experimental path*, **accept-refuse** / **named refuse**, *never claim the seams are solved*, *retires the hunt, not the record*, and D-129-B's *must-hunt is what they were called*; **3272 / 3394** stay **Phase 4 must-hunt** and *still being looked at*, with no surface calling them accepted or retired | `test_the_rule_is_three_valued_and_all_three_forms_survive` · `test_qualifying_is_not_deleting` · `test_the_phase_4_pair_is_left_exactly_where_it_was` |
| **T-1190** | **Copy and one test — nothing that computes anything moves.** `hold48_kabsch.py` / `hold48_confidence_kabsch.py` / `hold48_piecewise_kabsch.py` / `hold48_linker_seam.py` / `hold48_stitch.py` / `app/phase5_named_refuse.py` / `app/linker_seam_path_read.py` are **sha256-pinned**; both Method surfaces still say **as recorded**, name the tip and out_root, and say **not run** / **re-measured**; the living docs carry `### D-129-C` **as a heading** (checked, not cited — D-062) with its GO, its *does not reopen Phase 5* boundary, its deep-learning line, its D-016 provenance and its **twelve**-occurrence breakdown, and `decisions.md` / `Test_Plan.md` / `ARCHITECTURE.md` each name the id | `test_this_hygiene_pr_edits_no_algorithm_no_registry_and_no_reader` · `test_this_pr_runs_no_ops_and_re_measures_nothing` · `test_living_docs_carry_d129_c` |

### D-129-B (already on `main`, `cbcb47d` / #250; T-1181–T-1186) — Phase 5 named-refuse LABELS

Hermetic tests in `tests/test_d129_b_named_refuse_labels.py`. They read the
fate registry `app/phase5_named_refuse.py`, build an in-memory SQLite
`assembly_review`, and read `docs/method-hold48-tiles.md`,
`ui/src/components/MethodNote.jsx`, `ui/src/components/AssemblyReview.jsx`,
the living docs, and the `core/hold48_*.py` bytes. **No Fly, no GPU, no ops
run, no re-measurement.** Cite: **Emma BUILD GO 2026-09-06** (*"Matt: Go"*)
discharging **D-129 Spec §3**; the rollup as recorded by Kaylee at tip
`9e65cbf`, out_root `linker_seam_ops_2026-09-05`.

⚠ **Three failures these exist to redden**, and they are the ones the Spec
names. **Wrong inventory** (T-1181): a ninth parent accepted, one of the
eight dropped, or a Phase 4 id inside the set — the fate list is signed,
not a place to be approximately right. **A Phase 4 leak** (T-1182):
3272 / 3394 labelled accepted, retired, or closed, which Spec §6 allows
only under **explicit Matt GO language**, and which would make the card
look tidier and be false. **Silence instead of accept-refuse** (T-1183 /
T-1184): the label shipped while the **0 of 7** or the **5 / 6** give-back
is dropped, split, or softened — "accepted" is the friendliest word in
this arc and the one most likely to outlive its numbers, which Spec §4
calls a **violation**, not a simplification.
⚠ **A label is not an algorithm** (T-1186): the four `hold48_*.py` modules
are sha256-pinned, the registry carries no threshold, no geometry, and no
artifact read, and the D-128 reader keeps no Phase 5 vocabulary at all.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1181** | **The signed inventory, exactly.** The registry names **exactly** the eight (2938, 2939, 3179, 3190, 3321, 3368, 3566 + 3432) against a second copy of the list, with no duplicate and no stranger; each parent carries its **recorded** refuse reason and the path that recorded it (`seam_jump_gt_10` ×6 · `rmsd_gt_10` ×1 by D-128; **3432** `no_domain_pieces` by **D-127**); **3432** is `reaffirmed_not_newly_ruled` and `counted_in_d128_ops_seven` = **False**; the registry holds **no accession field** and invents none, and carries no threshold, no artifact read, and no transform | `test_the_registry_names_exactly_the_signed_eight` · `test_each_parent_carries_its_recorded_refuse_reason_and_the_path_that_recorded_it` · `test_3432_is_carried_not_re_ruled_and_is_not_one_of_the_d128_seven` · `test_the_registry_holds_no_accession_and_no_threshold` |
| **T-1182** | **Phase 4 stays cold.** 3272 / 3394 resolve to `phase-4-must-hunt` with `is_accept_refuse` **False**, `hunt_closed` **False**, no rollup, and copy that says **not accept-refuse / not retired / not closed** and *moves only on a separate explicit Matt GO*; the two id sets are **disjoint**; no Method surface puts either id inside the accepted-eight passage (checked **inside that sentence**, not page-wide), while both stay named as still-open; a parent with **no** fate renders an **absence** that is not an acceptance and not a solved seam | `test_phase_4_parents_can_never_reach_the_accept_refuse_label` · `test_no_surface_labels_the_phase_4_pair_accepted` · `test_a_parent_with_no_fate_renders_an_absence_not_an_acceptance` |
| **T-1183** | **The label is constructed carrying the rollup.** For **each** of the eight (not once in aggregate): `disclosure_required` is True and `ops_rollup` holds PASS 0 / REFUSE 7 / FAIL 0 / SKIP 0, `repaired_of_seven` = **0**, `n_d125_pass_d128_refuse` = **5**, `n_d126_pass_d128_refuse` = **6**, both `n_d127_*` = **0**, recorded by **Kaylee** at `9e65cbf` / `linker_seam_ops_2026-09-05`, `re_measured_here` **False**; the rollup is **internally consistent** before it is rendered (`0+7+0+0` = 7; histogram `6+1` = 7; PASS 0 forces both D-127 counts; 3432 is **not** in it); and one caller mutating its copy cannot trim anyone else's | `test_the_label_is_constructed_carrying_the_rollup` · `test_the_rollup_is_internally_consistent_before_it_is_rendered` · `test_a_surface_cannot_mutate_the_recorded_rollup` |
| **T-1184** | **Every surface says the label with its disclosure.** Both Method sections carry **accept-refuse** / **named refuse**, the **0 of 7**, **gave back**, **5 vs D-125** and **6 vs D-126**, *pre-registered / allowed outcome*, *these joins do not hold*, *stopped trying to fix them*, *does not mean the seam is solved*, *does not mean we stop reporting the numbers*, *retires the hunt, not the record*, all **eight** ids, **2 of its 5** / **0 of 3** / **0 of 7**, and the served **assembler** — all **inside the D-129-B section**; no forbidden badge appears in affirmative form and every required negation is written; **D-128-B's disclosure is not gutted** (its numbers, its *bury a drop under a pre-registration* sentence, and the standing D-127 figures survive) and the superseded `must-hunt` wording is **corrected in place**, not deleted | `test_every_method_surface_carries_the_label_and_its_disclosure` · `test_the_two_method_surfaces_say_the_label_in_plain_words` · `test_no_forbidden_badge_appears_and_every_negation_is_written` · `test_the_d128_b_disclosure_is_not_gutted_by_the_relabel` |
| **T-1185** | **The payload and the card.** `assembly_review.phase5_fate` carries the fate for an accept-refuse parent (keyed by `parent_job_id`) with its reason and rollup, keeps a Phase 4 parent **open**, and renders an **absence** for an unlisted parent; `dual_path` / `triple_path` / `four_path` / `five_path` are unchanged and gain no fate key; the card nests `phase5-ops-rollup` **inside** `phase5-fate`, reads `fate.label` from the registry rather than re-typing it, names every confusion key with the recorded tip / out_root, and derives **no** arithmetic over the rollup | `test_assembly_review_carries_the_fate_for_an_accept_refuse_parent` · `test_assembly_review_keeps_a_phase_4_parent_open` · `test_assembly_review_renders_an_absence_for_an_unlisted_parent` · `test_the_card_renders_the_rollup_inside_the_label_block` |
| **T-1186** | **A label is not an algorithm, and the freeze is restated where the label ships.** `hold48_kabsch.py` / `hold48_confidence_kabsch.py` / `hold48_piecewise_kabsch.py` / `hold48_linker_seam.py` are **sha256-pinned** and name no D-129; `hold48_stitch.py` is untouched; no surface POSTs to Fly, names RunPod, or invokes A's writer / CLI; the D-128 reader keeps **no** Phase 5 vocabulary; both Method sections restate **no fifth stitching algorithm**, **10.0 Å**, **W = 32**, **ε = 1e-3**, **D-126 best experimental and callable**, and **both failed rescues stay disclosed**; and the living docs carry `### D-129-B` with its GO, its provenance, and its **named** superseded pins | `test_this_labelling_pr_edits_no_algorithm_and_runs_no_ops` · `test_the_freeze_is_restated_where_the_label_is_shipped` · `test_living_docs_carry_d129_b` |

### D-129 Spec (already on `main`, `1baf4c0` / #249; T-1172–T-1180) — Phase 5 named-refuse

Hermetic docs pin tests in `tests/test_d129_phase5_named_refuse_spec.py`.
Stdlib only — they read `docs/README.md`, `docs/SPEC-phase5-named-refuse.md`,
`docs/SPEC-linker-seam-honesty.md`, `docs/decisions.md`,
`docs/PLAN-ui-post-wave2-endstate.md`, `docs/Test_Plan.md`,
`ARCHITECTURE.md` and the `core/hold48_*.py` bytes. **No Fly, no GPU, no
ops run, no re-measurement.** Cite: **Matt SIGNED Phase 5 named-refuse
2026-09-05 ~17:58 PT via Emma**; D-128 Spec + `### D-128` + `### D-128-A`;
D-0043 roadmap Phase 5.

⚠ **These tests exist for one failure and its mirror image.** The first
is **relabel-and-forget**: mark the eight `accept-refuse` and quietly
drop the D-128 OPS **0 of 7** and the named regress, so the surface
reads like success. **T-1175 goes red on exactly that** — the
disclosure is pinned as a *requirement of the label*, not as adjacent
prose. The second is **relabel-as-defeat**: read a **pre-registered
allowed outcome** as a *D-128 miss*, which is how a project talks
itself into loosening a gate. **T-1174** pins that label as forbidden.
Between them sit the two boundaries a tidy-up would erode:
**T-1176** keeps **3272 / 3394** out of the accepted eight and behind
**explicit Matt GO** language, and **T-1177** keeps the family frozen —
**no linker-v2**, gate **10.0 Å**, served = **assembler**, **D-126**
best experimental, and **both** failed rescues disclosed.
⚠ **A label is not an algorithm:** T-1178 requires the D-128 Spec
cross-link to say so and pins all five `hold48_*.py` modules by
sha256, so this Spec cannot become a code change.
⚠ **Never solved.** No test here rewards a pass count, and every
`accept-refuse` claim is checked against the seams-solved park.

| ID | Check | Test name |
|----|-------|-----------|
| **T-1172** | `### D-129 —` exists in the living log (**the check is the heading, not a citation of one** — D-001 / D-062 / method-note item 7), and so do the `### D-128` and `### D-128-A` headings it cites; the Spec file exists; the log binds **Matt SIGNED Phase 5 named-refuse** with its date and the Emma route, and names **D-0043** Phase 5; the log records that **no vault file is on disk** and invents no vault prose; **D-129 collides with nothing** (highest `### D-NNN` in the log is 129 and there is exactly one) | `test_d129_heading_exists_in_the_living_log` · `test_spec_file_exists_and_names_its_authority` · `test_matt_signed_phase_5_is_bound_with_provenance` · `test_no_vault_prose_is_invented` · `test_d129_is_the_next_free_decision_id` |
| **T-1173** | **The eight are `accept-refuse`.** All of **2938, 2939, 3179, 3190, 3321, 3368, 3566** and **3432** are named in the Spec **and** the log and are labelled `accept-refuse`; the set has exactly **eight** members; **3432** is marked **already** accept-refuse / **re-affirmed, not newly ruled**; `accept-refuse` is defined as **the recorded honest outcome of a refusal** (the join is **not held**), never as a success; no accession is invented for the five parents this log does not carry | `test_the_eight_parents_are_accept_refuse` · `test_3432_is_reaffirmed_not_newly_ruled` · `test_accept_refuse_is_defined_as_a_recorded_refusal` · `test_no_invented_accessions_for_unrecorded_parents` |
| **T-1174** | **Forbidden labels are written as forbidden:** **open must-hunt** (and “pending rescue” / “awaiting a fix” / any implied fifth algorithm), **solved / fixed / repaired / aligned / superimposed / “seams solved” / “seams fixed” / “full-length AF-quality”**, and **a D-128 miss / a D-128 failure**; the Spec states that **0-of-7 was pre-registered** as allowed by D-128 §1b / §3 / §11 **before** the run; the Spec **never says solved** and carries the forbidden-language park forward | `test_forbidden_labels_are_named_as_forbidden` · `test_zero_of_seven_is_pre_registered_not_a_miss` · `test_spec_never_says_seams_are_solved` |
| **T-1175** | **`accept-refuse` ≠ Method silence — the disclosure ships with the label.** Spec §4 and the log carry the recorded rollup **PASS 0 / REFUSE 7 / FAIL 0 / SKIP 0**, `repaired_of_seven` = **0**, the per-parent refuse reasons (`seam_jump_gt_10` ×6 / `rmsd_gt_10` ×1 on **2939**), and the exact §11 confusion keys `n_d125_pass_d128_refuse` = **5**, `n_d126_pass_d128_refuse` = **6**, `n_d127_pass_d128_refuse` = **0**, `n_d127_refuse_d128_pass` = **0**, plus `n_seams_measured` = 35 / `n_dishonest_linker_seam` = 6 / `n_honesty_unknown` = 4 and the **10.0 Å** gate; the **named regress** sits **beside** the accept count and burying it is called a **Spec violation**; provenance names **Kaylee**, tip **`9e65cbf`** and out_root **`linker_seam_ops_2026-09-05`** and disclaims re-measurement; the **D-127** disclosure stays too | `test_b_must_still_disclose_the_d128_ops_rollup` · `test_confusion_keys_are_exact_and_valued` · `test_burying_the_regress_is_named_a_spec_violation` · `test_ops_disclosure_names_its_provenance_and_disclaims_measurement` · `test_both_failed_rescues_stay_disclosed` |
| **T-1176** | **Phase 4 boundary.** **3272** `Q6V0I7` and **3394** `Q8TDW7` are labelled **Phase 4 must-hunt** in the Spec and the log, are **NOT** in the accept-refuse eight (the two sets are disjoint), and may be reclassified only with **explicit Matt GO** language; **no RMSD Spec bleed** — the Spec does not spec / scope / schedule Phase 4 and is not that GO | `test_phase_4_pair_stays_must_hunt` · `test_phase_4_pair_is_not_in_the_accept_refuse_eight` · `test_reclassifying_phase_4_requires_matt_go_language` · `test_no_rmsd_spec_bleed` |
| **T-1177** | **The freeze.** **No linker-v2** (and no piecewise-v3 / new decomposition / second window size / restitch); the **10.0 Å** gate **stays** and does not loosen, with **W = 32** and **ε = 1e-3** unchanged; **served = assembler** with no auto-flip; **D-126 remains the best experimental path until proven otherwise**, quantified **2 of its primary 5** against D-127's **0 of 3** and D-128's **0 of 7**; no named-exclusion, no trim loop, no soft invent blend | `test_no_linker_v2_and_the_family_freezes` · `test_gate_stays_at_10_and_does_not_loosen` · `test_served_stays_assembler_and_d126_stays_best_experimental` |
| **T-1178** | **A label, not an algorithm.** The D-128 Spec's **§3 Phase 5 amendment** and **§9 hard stop** exist, cross-link D-129 and `### D-129`, say the seven are **`accept-refuse`, no longer must-hunt**, state that §1a / §1b / §2 / §5 / §11 **stand as shipped**, and make **no** seams-solved claim; the D-128 Spec keeps its own accept-refuse / signed-triage / must-hunt language and invents no new accession; `core/hold48_kabsch.py`, `core/hold48_confidence_kabsch.py`, `core/hold48_piecewise_kabsch.py`, `core/hold48_linker_seam.py` are **sha256-pinned** and `core/hold48_stitch.py` names no D-129 | `test_d128_spec_carries_the_phase5_crosslink_in_section_3_and_9` · `test_crosslink_changes_a_label_not_the_algorithm` · `test_d128_spec_still_never_says_solved` · `test_this_spec_pr_does_not_edit_hold48_modules` |
| **T-1179** | **Docs-only scope.** This PR ships **no** Method file edit (`docs/method-hold48-tiles.md` is byte-pinned and names no D-129) and **no** UI file (no `ui/` path, no `MethodNote.jsx`); Spec §5 carries the **8th-grade** Method excerpt as **authority** a later B discharges, naming all four paths, the **0 of 7**, what “accepted refusal” does and does **not** mean, the two still-open parents, and **default served = assembler** — without claiming solved; the Spec forbids merging D-128-B, inventing D-129-B, and self-merging | `test_no_method_file_edit_in_this_spec_pr` · `test_no_ui_file_in_this_spec_pr` · `test_method_excerpt_is_authority_and_is_eighth_grade` · `test_out_of_scope_fences_are_written` |
| **T-1180** | **Rollup is internally consistent before it is quoted (D-016).** `0 + 7 + 0 + 0` = **7** = the seven; refuse histogram `6 + 1` = **7** = REFUSE; `repaired_of_seven` = **0** = PASS; `n_d127_refuse_d128_pass` = **0** is *forced* by PASS 0; `n_d127_pass_d128_refuse` = **0** is *forced* by the seven being D-127's `linker_jump_gt_10` class; every confusion count is **≤ 7**; `n_dishonest_linker_seam` = **6** agrees with the six `seam_jump_gt_10` refuses while **2939** is `n_honesty_unknown` (refused **before any transform** — null is not zero, unknown is not honest); **eight + two = D-127's ten refuses**, disjoint and exhaustive; and `n_seams_measured` = 35 / `n_honesty_unknown` = 4 are marked **recorded, not re-derived** | `test_ops_figures_are_internally_consistent_before_they_are_quoted` · `test_eight_plus_phase4_pair_exhaust_the_d127_refuses` · `test_unreproducible_counts_are_marked_recorded_not_rederived` · `test_ship_index_plan_architecture_and_test_plan_carry_d129` |

---

**End of Test Plan**

