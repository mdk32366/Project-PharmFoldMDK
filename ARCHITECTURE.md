# PharmFoldMDK — Architecture

> **Living document.** This file is the single source of truth for how PharmFoldMDK
> is built and why. It MUST be updated **in the same change** that alters the
> architecture, and it MUST be brought current **before any PR is filed**. If a PR
> changes structure, data flow, dependencies, or deployment and does not touch this
> file, the PR is incomplete. See [`docs/README.md`](docs/README.md) for the
> chronological log of individual design decisions.

**Project**: PharmFoldMDK — an Antibody-Drug Conjugate (ADC) target exploration platform.
**Context**: Graded coursework for a **Deep Learning** class in an ML Master's program.
**Status (2026-07-19)**: Pre-implementation. Planning docs are in `docs/`; no application code yet.

---

## 1. Prime Directive: Deep Learning Is the Core, Not a Wrapper

This is a **deep learning course project**. The grade depends on deep learning doing
**load-bearing work** — a neural network must be responsible for a primary output, not
merely calling an external service that happens to use ML internally.

Every architectural decision is evaluated against the question: **"Where is the deep
learning, and is *our* system running/using it in a defensible way?"**

- ✅ Running a protein language model (e.g. ESMFold) to fold sequences into 3D structure.
- ✅ A learned model that scores druggability / pocket suitability from structural features.
- ✅ Learned embeddings (from a neural encoder) powering semantic search over analyses.
- ✅ A model predicting mutation impact (ΔΔG / binding-site disruption).
- ⚠️ Pure retrieval from AlphaFold DB or UniProt lookups — acceptable as a *fallback or
  input*, but it cannot be the graded deliverable on its own.

**Rule:** at least one iteration's headline feature must be a deep-learning model that
this project runs or fine-tunes. This is recorded and defended in `docs/README.md`.

---

## 2. System Overview

PharmFoldMDK lets a user enter a cancer type or an overexpressed protein and returns
AI-driven structural analysis of that protein as a potential ADC target: predicted 3D
structure with confidence, druggable pockets, an ADC-suitability assessment, mutation
impact, and pharma-relevant reports.

```
                 ┌─────────────────────────────────────────────┐
                 │              Streamlit Frontend               │
                 │  Mission Briefing · New Analysis · Library ·  │
                 │            Reports · Settings                 │
                 └───────────────────┬───────────────────────────┘
                                     │ HTTP (internal)
                 ┌───────────────────▼───────────────────────────┐
                 │                FastAPI Backend                 │
                 │   auth · analyses API · inference orchestration │
                 └──────┬───────────────┬──────────────┬──────────┘
                        │               │              │
        ┌───────────────▼──┐   ┌────────▼────────┐   ┌─▼──────────────────┐
        │  DL / Inference   │   │  Postgres +     │   │  Fly Volume /data  │
        │  (core, neural)   │   │  pgvector       │   │  PDB/CIF, PAE,     │
        │  ESMFold, pocket, │   │  relational +   │   │  reports, uploads  │
        │  embeddings, etc. │   │  JSONB + vectors│   │  (paths in DB)     │
        └───────────────────┘   └─────────────────┘   └────────────────────┘
```

**Boundary rule:** the database stores structured data, JSONB metadata, and vectors;
**large binary artifacts (PDB/mmCIF, PAE JSON, generated reports, uploads) live on the
Fly Volume**, with only their paths recorded in Postgres.

---

## 3. Component Architecture

| Layer | Responsibility | Planned tech |
|-------|----------------|--------------|
| **Frontend** | Interactive UI, 3D visualization, onboarding | Streamlit; `py3Dmol`/`stmol` for 3D |
| **Backend API** | Auth, request handling, orchestration of inference | FastAPI + Uvicorn |
| **DL / Inference core** | The neural work: structure prediction, pocket/druggability scoring, embeddings, mutation impact | PyTorch + Hugging Face; `biopython` for parsing |
| **Data layer** | Persistence, relationships, vector search | Postgres + pgvector, SQLModel/SQLAlchemy, Alembic |
| **Object storage** | Large structure/report files | Fly Volume mounted at `/data`, organized `/data/analyses/{id}/` |

> **To be ratified in `docs/README.md`:** the exact DL model(s), whether we run ESMFold
> locally vs. fall back to AlphaFold DB, and where inference executes (in-process vs. a
> dedicated worker) are open decisions. Update this table once decided.

---

## 4. Data Model (from Database Plan v2)

Primary entities (full column detail in [`docs/Database_Plan_v2_Postgres.md`](docs/Database_Plan_v2_Postgres.md)):

- **`users`** — auth (username + hashed password), JSONB `preferences`.
- **`protein_analyses`** — core entity: input type/value, structure source, `pdb_path`,
  `mean_plddt`, `pae_json_path`, JSONB `metadata`, notes. ADC-specific fields
  (e.g. `adc_suitability_score`) to be added as extensions.
- **`mutations`** — 1:N from an analysis; position, original/new AA, impact score + notes.
- **`reports`** — 1:N from an analysis; report type, `content_path`, timestamps.
- **`analysis_embeddings`** — `vector(384)` with an HNSW cosine index for semantic search
  (Iteration 3+).

**Relationships:** `users` 1:N `protein_analyses` 1:N (`mutations`, `reports`).
**Migrations:** Alembic, versioned. Any schema change ships with a migration.

---

## 5. Storage & Deployment

- **Hosting:** Fly.io.
- **Database:** Fly Postgres addon with pgvector (`CREATE EXTENSION vector;`).
- **Files:** Fly Volume at `/data`; DB holds paths only.
- **Backups:** Fly Postgres automated backups + volume snapshots.
- **Migrations:** Alembic versioned scripts, applied on deploy.

> **Open decision (log in `docs/README.md`):** whether to prototype on SQLite-on-Volume
> first (Database Plan §5 offers this) or go straight to Postgres. Given pgvector is
> central to the DL semantic-search story, Postgres-first is the current lean.

---

## 6. Iteration Roadmap (DL mapped)

| Iter | Product goal | Deep-learning content |
|------|--------------|-----------------------|
| **1 (MVP)** | Mission Briefing tab + structure retrieval + 3D viewer + basic pocket + ADC summary | **Structure prediction via a protein LM (ESMFold) is the intended DL core** — TBD/ratify in `docs/README.md` |
| **2** | Mutation simulator, comparison views, pocket scoring | Learned mutation-impact and/or druggability model |
| **3** | Reports, semantic library search | Neural embeddings + pgvector semantic search; report synthesis |
| **4 (stretch)** | Epitope suggestion, ADC complex modeling, agentic workflows | Advanced/agentic DL |

---

## 7. Cross-Cutting Concerns

- **Security (MVP):** username + hashed password (bcrypt/passlib); protected API routes.
- **Confidence honesty:** pLDDT/PAE surfaced clearly; outputs framed with caveats.
- **Testing:** pytest (functional) + structured user-testing scenarios — see
  [`docs/Test_Plan.md`](docs/Test_Plan.md). External calls and model inference are mocked
  in unit tests for speed/determinism.
- **Reproducibility (course expectation):** pin model weights/versions, seed where
  relevant, and record any training/fine-tuning config so results can be reproduced.

---

## 8. Repository Layout (target)

```
Project-PharmFoldMDK/
├── ARCHITECTURE.md          # this file — living source of truth
├── README.md                # how to run / deploy (kept current in Phase 6)
├── CLAUDE.md                # living-doc governance rules
├── app/                     # Streamlit + FastAPI application code
├── core/                    # DL / inference + business logic
├── db/                      # models & Alembic migrations
├── tests/
├── docs/                    # plans, notes, and the design-decision log (README.md)
└── Dockerfile
```

Only `docs/` and the governance files exist today; the rest is created as iterations land,
and this layout section is updated when it changes.

---

## 9. Governance (how this doc stays true)

1. **Every PR that changes architecture updates this file in the same PR.** No exceptions.
2. **Every design decision is written into [`docs/README.md`](docs/README.md) *before*
   the work it describes is finished** — the decision log leads the code, not the reverse.
3. When a decision in the log changes the system's shape, fold the outcome into the
   relevant section here so this document never drifts from reality.
