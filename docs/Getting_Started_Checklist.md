# PharmFoldMDK – Getting Started Checklist

**Goal**: Get the project set up and deliver a working Iteration 1 MVP focused on **ADC Target Exploration**, including the educational “Mission Briefing” experience.

---

## Phase 1: Project Setup (Do this first)

- [ ] Create a new GitHub repository (or local folder) named `pharmfold-mdk`
- [ ] Initialize with a clean `README.md` stating the scope:  
  > “PharmFoldMDK – Tool for exploring overexpressed proteins as Antibody-Drug Conjugate (ADC) targets using protein structure prediction.”
- [ ] Set up a Python virtual environment (`venv` or `uv`)
- [ ] Create basic folder structure:
  ```
  pharmfold-mdk/
  ├── app/                  # Main Streamlit + FastAPI code
  ├── core/                 # Business logic (inference, analysis)
  ├── db/                   # Database models & migrations
  ├── tests/
  ├── docs/                 # Plans and notes
  └── Dockerfile
  ```
- [ ] Add key dependencies (start minimal):
  - `streamlit`
  - `fastapi` + `uvicorn`
  - `sqlmodel` (or `sqlalchemy`)
  - `pydantic`
  - `py3Dmol` or `stmol`
  - `biopython`
  - `pytest`

---

## Phase 2: Database & Infrastructure

- [ ] Decide on initial DB approach:
  - **Recommended for long-term**: Start with **Postgres + pgvector** (Fly.io addon)
  - Or start with **SQLite on Fly Volume** for faster prototyping (easy to migrate later)
- [ ] Create initial database models (`users`, `protein_analyses`, `mutations`, `reports`)
- [ ] Set up Alembic for migrations
- [ ] Create a Fly.io app + Volume (or Postgres addon)
- [ ] Get basic database connection working locally and deployed on Fly.io

---

## Phase 3: ADC Mission Briefing Tab (High Priority)

- [ ] Create a new Streamlit page/tab called **“ADC Mission Briefing”**
- [ ] Build the static content:
  - Exciting header (e.g. “Operation: Precision Strike”)
  - Clear explanation of the **three ADC components** (Antibody, Linker, Payload) in a table with simple analogies
  - Strong **Mission Statement** for PharmFoldMDK
  - Section introducing a future **Cancer Target Database**
- [ ] Add a prominent “Begin Mission – Analyze a Target” button that links to the New Analysis page

---

## Phase 4: Core Analysis Flow (Iteration 1 MVP)

- [ ] Build the **New Analysis** page with input options:
  - UniProt ID lookup
  - Paste FASTA sequence
  - (Later) Upload PDB file
- [ ] Implement basic structure retrieval:
  - Prefer AlphaFold DB
  - Lightweight fallback if needed
- [ ] Display:
  - Mean pLDDT / confidence score with color coding
  - Basic interactive 3D viewer
  - Simple druggable pocket detection
  - Basic ADC suitability summary
- [ ] Save analysis to the database and show in History/Library

---

## Phase 5: Testing Foundation

- [ ] Set up `pytest` folder structure
- [ ] Write basic tests for:
  - Database models and CRUD
  - Core analysis functions (use mocks for external calls)
- [ ] Add a simple health check

---

## Phase 6: Polish & Deployment

- [ ] Add basic user authentication (username + hashed password)
- [ ] Deploy to Fly.io
- [ ] Test the full user flow:
  1. Mission Briefing
  2. New Analysis
  3. View results + 3D viewer
  4. History / saved analyses
- [ ] Update `README.md` with how to run locally and deploy

---

## Recommended Order to Start Knocking Out

| Priority | Task                                      | Why It Matters                     | Effort |
|----------|-------------------------------------------|------------------------------------|--------|
| 1        | Repo + basic folder structure             | Foundation                         | Low    |
| 2        | ADC Mission Briefing tab                  | Sets tone and educates users       | Medium |
| 3        | Database models + migrations              | Required for persistence           | Medium |
| 4        | Basic structure retrieval + 3D viewer     | Core value of the tool             | High   |
| 5        | Simple pocket detection + ADC summary     | Makes it feel ADC-focused          | Medium |
| 6        | History / save analyses                   | Makes the tool usable              | Low    |
| 7        | Deploy to Fly.io                          | Gets it live                       | Low    |

---

## Quick Tips

- **Start small**: Get the Mission Briefing tab + a basic structure viewer working first. Everything else builds on that.
- Use the **TDD v3** and **UI Plan** as your main references.
- Keep the Mission Briefing professional but engaging.
- Don’t over-engineer the first version of pocket detection or ADC scoring — improve it in later iterations.

---

**You're ready to start tomorrow.** Good luck — this is shaping up to be a strong, focused project!