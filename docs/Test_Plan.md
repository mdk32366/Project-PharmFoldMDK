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

**End of Test Plan**

