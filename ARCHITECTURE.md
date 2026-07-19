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
   ┌─────────────── FLY.IO (serving tier, always-on, NO GPU) ───────────────┐
   │   ┌─────────────────────────────────────────────┐                       │
   │   │              Streamlit Frontend               │                      │
   │   │  Mission Briefing · New Analysis · Library ·  │                      │
   │   │            Reports · Settings                 │                      │
   │   └───────────────────┬───────────────────────────┘                     │
   │                       │ HTTP (internal)                                  │
   │   ┌───────────────────▼───────────────────────────┐                     │
   │   │                FastAPI Backend                 │                     │
   │   │   auth · analyses API · job queue · results    │                     │
   │   └──────────────┬──────────────────┬──────────────┘                    │
   │                  │                   │                                   │
   │        ┌─────────▼────────┐   ┌──────▼──────────────┐                    │
   │        │  Postgres +      │   │  Fly Volume /data   │                    │
   │        │  pgvector        │   │  PDB/CIF, PAE,      │                     │
   │        │  relational +    │   │  reports, uploads   │                    │
   │        │  JSONB + vectors │   │  (paths in DB)      │                    │
   │        │  + job queue     │   └─────────────────────┘                    │
   │        └─────────▲────────┘                                              │
   └──────────────────┼──────────────────────────────────────────────────────┘
                      │  authenticated OUTBOUND poll / upload (pull-based)
                      │  (worker claims pending jobs, folds, uploads results)
   ┌──────────────────┴──────────────────────────────────────────────────────┐
   │           LOCAL MACHINE (inference tier — NVIDIA GPU, 8 GB VRAM)          │
   │   Worker: poll → ESMFold (ESM-2 + folding head) → pLDDT/PAE → upload      │
   │   No inbound exposure. Queues gracefully when offline. (D-004)            │
   └──────────────────────────────────────────────────────────────────────────┘
```

**Boundary rule:** the database stores structured data, JSONB metadata, vectors, and the
**job queue**; **large binary artifacts (PDB/mmCIF, PAE JSON, generated reports, uploads)
live on the Fly Volume**, with only their paths recorded in Postgres.

**Topology rule (D-004):** deep-learning inference does **not** run on Fly. The Fly serving
tier is GPU-free and always on; a **local GPU worker** pulls jobs from Fly, runs ESMFold,
and uploads results back over an authenticated outbound connection. No inbound port is
opened on the local machine.

---

## 3. Component Architecture

| Layer | Responsibility | Planned tech |
|-------|----------------|--------------|
| **Frontend** | Interactive UI, 3D visualization, onboarding | Streamlit; `py3Dmol`/`stmol` for 3D |
| **Backend API** | Auth, request handling, **job queue** management, results | FastAPI + Uvicorn (on Fly) |
| **Local GPU worker** | Polls Fly for jobs, runs **ESMFold** on the local NVIDIA GPU, uploads artifacts back (D-004) — **not deployed to Fly** | Python worker; PyTorch + Hugging Face (`facebook/esmfold_v1`) |
| **DL / Inference core** | The neural work: **ESMFold structure prediction (D-003)**, plus pocket/druggability scoring, embeddings, mutation impact | PyTorch + Hugging Face; `biopython` for parsing |
| **Data layer** | Persistence, relationships, vector search | Postgres + pgvector, SQLModel/SQLAlchemy, Alembic |
| **Object storage** | Large structure/report files | Fly Volume mounted at `/data`, organized `/data/analyses/{id}/` |

> **Ratified (D-003 + D-004):** we **run ESMFold ourselves** — the ESM-2 protein language
> model + folding head predicting 3D structure from a single sequence, emitting pLDDT and
> PAE — **on a local GPU worker, not on Fly** (see §5). AlphaFold DB / UniProt retrieval is
> demoted to an optional fast path + fallback, not the deliverable.

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

## 5. Storage, Deployment & Inference Topology

### Two-tier topology (D-004)

- **Serving tier — Fly.io (always-on, no GPU):** Streamlit + FastAPI, Postgres + pgvector,
  Fly Volume. Hosts the app, the data, and the **job queue**.
- **Inference tier — local machine (NVIDIA GPU, 8 GB VRAM):** a **`worker/`** process that
  **pulls** pending jobs from Fly over an authenticated **outbound** connection, runs
  ESMFold on the local GPU, uploads PDB/pLDDT/PAE back, and marks the job done/error. **Not
  deployed to Fly.** No inbound exposure of the local machine; jobs queue when it is offline.

### Fly serving-tier specifics

- **Database:** Fly Postgres addon with pgvector (`CREATE EXTENSION vector;`).
- **Files:** Fly Volume at `/data`; DB holds paths only.
- **Backups:** Fly Postgres automated backups + volume snapshots.
- **Migrations:** Alembic versioned scripts, applied on deploy.

### Deploy gate (D-005) — no untested code to prod

- **GitHub Actions:** PRs and pushes to `main` run a `test` job; the **Fly deploy job runs
  only if tests pass** (`deploy: needs: [test]`). Needs `FLY_API_TOKEN` in Actions secrets.
- **Doc-only commits bypass the test gate** via a path filter (`docs/**`, `**/*.md`,
  `ARCHITECTURE.md`, `LICENSE`, …). Any code change runs the full gate.

### VRAM constraint (8 GB) — design implications

Full `esmfold_v1` (ESM-2 3B) wants ~16 GB+ for long sequences, so on 8 GB VRAM we must:
axial-attention `chunk_size`, a **live sequence-length cap**, fold only the **ADC-relevant
extracellular domain**, and **pre-compute the curated target DB offline** (CPU-offload with
the 31.5 GB system RAM). These are follow-up decisions in `docs/README.md`.

> **Open decision (log in `docs/README.md`):** **prod** DB — SQLite-on-Volume prototype
> (Database Plan §5) vs. Postgres-first. pgvector is central to the DL semantic-search
> story, so Postgres-first is the current lean. *(The **test** DB is SQLite regardless —
> D-005.)*

---

## 6. Iteration Roadmap (DL mapped)

| Iter | Product goal | Deep-learning content |
|------|--------------|-----------------------|
| **1 (MVP)** | Mission Briefing tab + structure prediction + 3D viewer + basic pocket + ADC summary | **ESMFold run in-project (ratified, D-003)** — protein LM + folding head predicting structure + pLDDT/PAE from sequence |
| **2** | Mutation simulator, comparison views, pocket scoring | Learned mutation-impact and/or druggability model; ESMFold folds wild-type vs. mutant for comparison |
| **3** | Reports, semantic library search | Neural embeddings + pgvector semantic search; report synthesis |
| **4 (stretch)** | Epitope suggestion, ADC complex modeling, agentic workflows | Advanced/agentic DL |

---

## 7. Cross-Cutting Concerns

- **Security (MVP):** username + hashed password (bcrypt/passlib); protected API routes.
- **Confidence honesty:** pLDDT/PAE surfaced clearly; outputs framed with caveats.
- **Testing (D-005):** all tests live in **`tests/`**. Two kinds — **functional** (`pytest`,
  `*.py`: data layer, inference logic, API, worker contract) and **user-based** (structured
  human scenarios) — see [`docs/Test_Plan.md`](docs/Test_Plan.md). The **test DB is SQLite**
  (in-memory/temp); external calls and ESMFold inference are **mocked** for speed/determinism.
  **Gap:** SQLite can't exercise pgvector/Postgres-specific paths — those are mocked now and
  get a separate Postgres integration job at Iteration 3.
- **Reproducibility (course expectation):** pin model weights/versions, seed where
  relevant, and record any training/fine-tuning config so results can be reproduced.

---

## 8. Repository Layout (target)

```
Project-PharmFoldMDK/
├── ARCHITECTURE.md          # this file — living source of truth
├── README.md                # how to run / deploy (kept current in Phase 6)
├── CLAUDE.md                # living-doc governance rules
├── app/                     # Streamlit + FastAPI application code (deployed to Fly)
├── core/                    # shared business logic + inference contracts
├── worker/                  # LOCAL GPU worker: pulls jobs, runs ESMFold (NOT deployed to Fly)
├── db/                      # models & Alembic migrations
├── tests/                   # functional (pytest) + user-based; SQLite test DB (D-005)
├── docs/                    # plans, notes, and the design-decision log (README.md)
├── .github/workflows/       # CI: test gate → Fly deploy (D-005)
└── Dockerfile               # serving tier image (Fly)
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
