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

**End of Test Plan**