# PharmFoldMDK — Architecture

> **Living document.** This file is the single source of truth for how PharmFoldMDK
> is built and why. It MUST be updated **in the same change** that alters the
> architecture, and it MUST be brought current **before any PR is filed**. If a PR
> changes structure, data flow, dependencies, or deployment and does not touch this
> file, the PR is incomplete. See [`docs/README.md`](docs/README.md) for the
> chronological log of individual design decisions.

**Project**: PharmFoldMDK — an Antibody-Drug Conjugate (ADC) target exploration platform.
**Context**: Graded coursework for a **Deep Learning** class in an ML Master's program.
**Status (2026-07-21)**: First application code landed — the job queue (D-009 §1) in `core/`
+ `db/`. Serving-tier app (`app/`) and GPU worker (`worker/`) not yet built.

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
| **Local GPU worker** | Polls Fly for jobs, runs **ESMFold** on the local NVIDIA GPU for targets **under the length ceiling**, uploads artifacts back (D-004) — **not deployed to Fly** | Python worker; PyTorch + Hugging Face (`facebook/esmfold_v1`), int8 trunk |
| **Rented-GPU batch** (D-011) | One-time offline fold of **above-ceiling** targets (HER2-class ~630 aa); artifacts uploaded to the Fly Volume | RunPod RTX A6000 48 GB, fp16 unquantised/unchunked; committed repo code, not a one-off script |
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
  (Iteration 3+). ⚠️ pgvector lives in the **`extensions`** schema (D-014), so the migration
  that creates this column must resolve the type via `search_path`, not a bare `vector(384)`.
  The migration-side seam is already in place: `db/migrations/env.py` sets `search_path TO
  public, extensions` on Postgres (D-012 §5a). The **app-runtime** connection needs the same
  search_path — a *separate* seam in the engine config, not handled by env.py (D-012 §5a).
- **`jobs`** (D-009 §1, **implemented in PR A** as `db.models.JobRecord`) — **transient**
  fold-queue state, kept **separate** from the durable `protein_analyses` record: `analysis_id`
  (see FK note), `status` (`pending`/`claimed`/`complete`/`failed`), `claimed_at`, `worker_id`,
  `attempts`, `error`, and `inference_settings` JSONB (dtype / `chunk_size` / model revision —
  the reproducibility record). Reached through the `JobQueue` **seam** (`core/queue.py`):
  claimed via `SELECT … FOR UPDATE SKIP LOCKED` (the one Postgres-only, unproven-in-CI
  operation), while `complete`/`fail`/`reap_stale` are portable and tested for real on SQLite.
  Stale `claimed` jobs (age **strictly** > 30 min) are requeued, `attempts++`, up to
  **`MAX_ATTEMPTS = 3`** then terminal `[reaped-out]` (D-009 §1 Amendment 1); an explicit `fail`
  is terminal and leaves `attempts` untouched (Amendment 2); claim order is explicit FIFO by
  `created_at` (Amendment 3). **`analysis_id` carries no FK yet** — a plain indexed integer
  until the migration that creates `protein_analyses` adds the constraint in that same migration
  (Amendment 4). This is the durable queue the local GPU worker (D-004) pulls from.

**Relationships:** `users` 1:N `protein_analyses` 1:N (`mutations`, `reports`, `jobs`).
**Migrations:** Alembic, versioned. Any schema change ships with a migration.

**Anticipated — `ranking_runs` (D-015 §4).** Iteration 2 makes cohort ranking the spine, so the
schema must anticipate it now: a `ranking_runs` row (target-list version, scorer version,
timestamp) with a **nullable** `ranking_run_id` FK on `protein_analyses` — cheap to establish
up front, expensive to retrofit into an applied migration chain. **This is not yet built**
(PR A created neither table). The load-bearing consequence for whoever writes the
`protein_analyses` migration: that single migration must, together, (a) create
`protein_analyses`, (b) add the deferred `jobs.analysis_id` FK that closes D-009 §1 Amendment 4,
and (c) create `ranking_runs` + the nullable `ranking_run_id` FK. Because `protein_analyses`
does not exist yet, all of this is a clean first-cut, not a retrofit.

**Engine — Postgres from the first migration (D-012); host is the existing Fly **MPG** cluster
`sentinel-holy-rain-4562`, database `pharmfoldmdk`, pgvector **v0.8.2** (D-014).** "Fly
Postgres" is **not** precise enough: it spans two products, and the **unmanaged** one cannot run
pgvector at all — measured, `pg_available_extensions` returns zero rows for `vector`, so the
extension is absent from the image rather than merely disabled. Prod is **Postgres 16**; keep
local dev and any Postgres CI container on 16.

⚠️ **pgvector is installed in the `extensions` schema, not `public`** — a migration emitting a
bare `vector(384)` fails with `type "vector" does not exist`. The first migration that creates a
vector column must schema-qualify the type or set `search_path`, and record which (D-012 §5a,
D-014). Alembic uses the **direct** connection (transaction-mode poolers break DDL); the app
uses the pooled one.

The SQLite-on-Volume prototype path
is closed, not deferred: pgvector hosts the learned embeddings, and the queue-claim mechanism
is Postgres-specific. **The test DB remains SQLite (D-005), so prod and test run different
engines** — and `SELECT … FOR UPDATE SKIP LOCKED` is a **syntax error** on SQLite, not an
unsupported feature that degrades (measured on SQLite 3.45.1: `near "FOR": syntax error`;
`FOR UPDATE` alone is rejected too). The claim path therefore **cannot execute in the suite at
all**. It is reached through a repository seam — a `JobQueue` protocol with `PostgresJobQueue`
(real, never run in CI) and a test double named `UnlockedFakeJobQueue` so no reader mistakes it
for coverage. **The seam is an honesty mechanism, not coverage**: only a Postgres integration
job in the gate will ever exercise the real claim path, and that job does not yet exist. This
is the same shape as the JARVIS `create_all`-vs-migration-chain gap, which was invisible to a
green suite until a Postgres CI job exposed it.

---

## 5. Storage, Deployment & Inference Topology

### Topology — serving tier + **split compute** (D-004, amended by D-011)

- **Serving tier — Fly.io (always-on, no GPU):** Streamlit + FastAPI, Postgres + pgvector,
  Fly Volume. Hosts the app, the data, and the **job queue**.
  **Fly GPU is eliminated, not deprioritised (D-011):** Fly deprecated GPU Machines and they become
  **unavailable after 2026-08-01**. Fly is the serving tier only.
- **Inference tier A — local machine (NVIDIA Blackwell, 8 GB VRAM):** a **`worker/`** process that
  **pulls** pending jobs from Fly over an authenticated **outbound** connection, runs
  ESMFold (int8 trunk / bf16 base, `chunk 64`) on the local GPU, uploads PDB/pLDDT/PAE back, and
  marks the job done/error. **Not deployed to Fly.** No inbound exposure; jobs queue when offline.
  **Scope: every target under the measured length ceiling** — Trop-2 (~250 aa), Nectin-4 (~350 aa),
  the 440 aa class. **0 crashes in ~94 folds.**
- **Inference tier B — rented GPU, one-time batch (D-011):** targets **above** the ceiling
  (HER2-class, ~630 aa). **RunPod RTX A6000 48 GB @ $0.49/hr**, Secure Cloud, per-second billing,
  no egress fees, **container disk only** (network volumes bill $0.07/GB/month even when stopped).
  A ≥24 GB card runs fp16 `esmfold_v1` **unquantised and unchunked**, so the entire local
  mitigation stack stops binding. **Estimated total for the Iteration-1 large-ECD cache: ~$0.25.**
  The batch must be **committed, reproducible code in this repo**, not a one-off script
  (binding condition of D-009 §3).

### Fly serving-tier specifics

- **Database (D-014):** the existing **Fly MPG** cluster `sentinel-holy-rain-4562`, own database
  `pharmfoldmdk`, **Postgres 16**, pgvector **v0.8.2** enabled per-database from the dashboard.
  **Narrowed from "Fly Postgres addon" deliberately** — that phrase spans two products, and the
  **unmanaged** one cannot run pgvector at all (measured: `pg_available_extensions` returns zero
  rows for `vector`, i.e. absent from the image, not merely disabled). No `CREATE EXTENSION`
  step is needed here; the extension is already on, **in the `extensions` schema** — see §4.
- **Compute isolation — a named coupling, not a safety assumption (D-014):** the cluster is
  Basic / Shared×2 / 1 GB RAM across *all* its databases, shared with JARVIS's `fly-db`.
  Logical isolation is real (separate database, separate extension state, a bad migration is
  contained); **CPU and memory are not**. A runaway query in one database can starve the other,
  and a cluster-level incident takes both down.
- **Connections (D-014):** Alembic on the **direct** string (transaction-mode poolers break DDL
  and session-level operations), the app on the **pooled** string. Both in secrets, never in the
  repo.
- **Files:** Fly Volume at `/data`; DB holds paths only.
- **Backups:** MPG managed backups + volume snapshots.
- **Migrations:** Alembic versioned scripts, applied on deploy.
- **Region:** SJC, matching the cluster and existing apps — since Feb 2026 inter-region private
  networking bills at Machine rates, so the serving tier should not drift out of SJC.

### Deploy gate (D-005 → proven & hardened in D-008) — no untested code to prod

- **GitHub Actions:** PRs and pushes to `main` run a `test` job; the **Fly deploy job runs
  only if tests pass** (`deploy: needs: [test]`). Needs `FLY_API_TOKEN` in Actions secrets.
- **Branch protection on `main` is the actual enforcement (D-008):** require a PR, require
  the **`test`** check, **`enforce_admins: true`** (no bypass, owner included), no direct
  pushes. Without it the gate is advisory — a failing check does not block a merge, and
  `git push origin main` walks straight past it.
- **No `paths-ignore` (D-008):** since `test` is a *required* check, it must report on every
  PR or a doc-only PR hangs unmergeable; the ~20s suite therefore runs on everything. When
  real deploy is wired, guard the **deploy job** (not the trigger) against doc-only changes.
- **Locked dependency graph (D-013 + Amendment A):** the gate installs
  **`requirements-dev.lock`** with **`--require-hashes`**. The `.txt` manifests are the
  human-edited inputs (what we want); the `.lock` files are what those resolved to — every
  transitive pinned and hashed, compiled by `uv pip compile --generate-hashes --universal
  --python-version 3.11`. **uv is a local authoring tool and is not installed in CI**; the lock
  is plain hashed-requirements format, so the gate uses stock pip.
  **Why the lock and not just exact pins:** four direct pins resolved to *thirteen* installed
  packages, so pinning the manifest left nine transitives floating — a breaking upstream release
  could redden the gate with no commit in this repo. The requirement is that a red gate is
  always attributable to a commit here, and only the lock delivers that. It is the
  environment-level counterpart of the pinned model revision recorded per-fold in
  `inference_settings` (D-004), and §7's reproducibility commitment needs both.
  **Install and test are independently breakable:** when the check goes red, read which step
  failed. Pip caching is deliberately **off** (D-013 §3). The CUDA stack
  (`torch`/`transformers`/`bitsandbytes`) is **never** installed in CI; it belongs to the GPU
  tier and gets its own manifest with `worker/`.
  *Residual:* the lock fixes versions and hashes, not index availability — a PyPI outage still
  reddens the gate and is not attributable to a commit.

### ⚠ VRAM constraint (8 GB) — fold path is UNRESOLVED (D-006 invalidated by S-001)

**Measured 2026-07-19 (S-001):** the fp16 model is resident at **8116 MiB** against **7043 MiB
free / 8151 MiB physical** — it spills to shared system RAM *before any fold*. **fp16 alone does
not fit `esmfold_v1` in 8 GB.** The D-006 ladder (fp16 → chunking → cap → ECD → caching) is
**invalid at rung one**: rungs 2+ reduce *activation* memory and cannot fix a *resident-weight*
overrun. Weights are **9.58 GB on disk** (not ~2.5 GB). Warm-cache load is **15–16 s**.

**The local GPU tier is BLOCKED ON HARDWARE (S-002 Q1, 2026-07-19).** Three 630 aa attempts each
ended in an identical host bugcheck (`0x00020001`). Windows event logs (**not** the minidumps —
unreadable without admin) identify the component: **PCIe Advanced Error Reporting faults on the
inference GPU itself** (`PCI\VEN_10DE&DEV_2D39` = RTX PRO 2000 Blackwell), with 3 fatal WHEA
errors matching the 3 crashes 1:1 and **no** display-driver TDR. VBS/HVCI is running, which is why
a fatal hardware error surfaces as HYPERVISOR_ERROR.

**Latent fault, workload-triggered — neither "unrelated bad hardware" nor "we broke it."**
Corrected AER errors on this exact device predate the project (148 across 7 days since
2026-05-27, on days with no ESMFold), and a May 27 fatal proves the link can go fatal without us.
But the `0x00020001` signature has **zero** occurrences before today. One fatal in eight weeks vs
**three in twenty minutes** ≈ four orders of magnitude — the workload is an **accelerant**.

**Mechanism — TESTED 2026-07-19 AND NOT SUPPORTED.** The hypothesis was *spill → sustained PCIe
traffic → corrected errors escalate*. Both arms were run under the new driver: **int8 non-spilling
(600 s, 83 folds) and fp16 spilling (368 s, 5 folds) each logged 0 corrected, 0 fatal, 0 bugchecks.**
Restoring spill did **not** restore errors, so spill is **not sufficient** to trigger the fault at
248 aa under driver 596.72. The **NVIDIA driver update (595.71 → 596.72)** is now the leading
explanation — but is **not established**: the original crash condition (**HER2, 630 aa**) was never
reproduced, and a 6-minute clean window has weak power against a fault that historically appeared on
8 days out of ~54. **Absence of errors is not evidence the fault is gone.**

**HER2 WAS TESTED (S-004, 2026-07-19) — IT CRASHED THE HOST.** int8, `chunk 64`, **no spill at rest**
(resident 5351 MiB vs 7043 free), bugcheck `0x00020001` at **19:02:28**, ~56 s into the first fold.
**Fourth crash of the day; fourth on HER2.** Driver 596.72 and other GPU apps are eliminated — it
reproduced with the new driver and an empty GPU process list.

**Sequence length is the discriminator; duration is not.** The fp16 control had just run five
individual folds of **73–74 s each without crashing**; S-004 died at **~56 s** — a *shorter* fold.
Spill is eliminated independently, since int8 does not spill and crashed anyway.

**The strongest, instrument-free evidence:**
> **4 crashes in 4 HER2 (630 aa) attempts. 0 crashes in ~93 Trop-2 (248 aa) folds** — both
> precisions, spilling and not, including 83 consecutive folds under sustained load.

**⚠ WHEA corrected-error rate is NOT a valid leading indicator (F-001).** The fatal is logged in the
same second as the corrected errors in all four crashes, and six burst days produced 65/40/31
corrected errors with **zero** fatals. Judge stability by **crash count**, never by corrected-error
rate.

**Length ceiling bisected (S-005, 2026-07-19): it lies in (440, 630).** HER2 ECD truncated to
**440 aa folded clean** — 28.6 s at `chunk 64`, peak **6665 MiB** (no spill), pLDDT 84.27,
440/440 CA atoms, **zero WHEA events, zero bugchecks**.

**Consequence — a far narrower constraint than S-004 alone implied.** The local tier **can** fold
most of the curated ADC set: Trop-2 (~250 aa), Nectin-4 (~350 aa), and anything up to at least
**440 aa**. **Only HER2-class targets (>440 aa) need external compute.** Still inside D-004 §5,
still **not** retrieval.

> *Inference, not measurement:* peak at 440 aa left only **378 MiB** of headroom against 7043 MiB
> free, so 630 aa at `chunk 64` would plausibly have spilled mid-fold — meaning **HER2 might yet
> fold at `chunk 16/32`**, which S-004 crashed before reaching. S-004's peak was lost with its
> corrupted JSON, so this is untested.

**Consequence:** cache generation *may* move to **different compute** (cloud GPU / Colab / cluster)
to de-risk the schedule — a ≥16 GB GPU also makes the fp16 non-fit stop binding — but that is
de-risking, **not** a verdict against the local tier. Inside the D-004 §5 boundary either way, and
**not** a retreat to retrieval.

**Replacement rung one is now MEASURED (S-003, 2026-07-19): quantize the ESM-2 LM trunk to int8
(`bitsandbytes`), folding head at full precision.** On the Trop-2 ECD (248 aa): resident
**5351 MiB**, peak **5779 MiB** — comfortably under both the 7799 MiB target and the 7043 MiB
actually free — **no spill**, and ~1.8× faster than fp16. Mean pLDDT 74.7 vs the 70.7 fp16 baseline —
**verified reproducible** (two folds: pLDDT delta 0.000, CA-RMSD 0.0000 Å, so the shift is a real
precision effect, not variance) and **verified non-degenerate** (248/248 CA atoms, zero NaN coords,
Rg 18.74 Å against a 17.9 Å compact-globular expectation). *Accuracy is still unproven: pLDDT is
self-confidence, so a cross-precision TM-score/RMSD comparison remains the outstanding follow-up.* **bf16 is rung two**
— same footprint as fp16 so it cannot fix the fit, but it costs nothing and holds quality (+0.2).
CPU-offload is **excluded by design**: it trades VRAM for the PCIe traffic implicated in the link
fault. Per D-004 §5 this stays inside "smaller model / narrower targets" and explicitly **does not**
mean retreating to AlphaFold retrieval.

**Still unconfirmed:** whether a non-spilling configuration stops the host crashes — that is
S-002 Q1, now testable against a config that genuinely fits.

> **Resolved — D-012 (engine) + D-014 (host).** Prod is **Postgres-first** from the first
> migration; the SQLite-on-Volume prototype path is closed, not deferred. Host is the existing
> **MPG** cluster with pgvector v0.8.2 (see §5). *(The **test** DB remains SQLite — D-005 — and
> D-012 §3–§5 turns that split from a footnote into a named structural exposure: the
> `SKIP LOCKED` claim path is a **syntax error** on SQLite and has never executed.)*

---

## 6. Iteration Roadmap (DL mapped)

| Iter | Product goal | Deep-learning content |
|------|--------------|-----------------------|
| **1 (MVP)** | **Cache-first (D-009 §3)**: Mission Briefing + curated ADC target DB served from pre-folded cached artifacts; live user folding deferred. **Two caps, not one (D-009 §3 amendment):** the **cache-build cap** is bounded by *memory fit + host stability only* — wall time is **not** a criterion, so `chunk 16/8` and multi-minute folds are acceptable; the **interactive cap** (Iteration 1.5+) is latency-bounded (`chunk ≥32`, `<120 s`). This is what makes large ECDs such as **HER2 (630 aa)** reachable for the cache even if never viable interactively | **ESMFold run in-project (D-003)** — the pipeline that *produces* the cache must be real, committed, reproducible code (binding condition of D-009 §3) |
| **2** | **Target ranking becomes the spine (D-015)** — a comparative view over the 82-target cohort (baseline evidence rank vs. structural rank, delta, movers), with single-target analysis as the drill-down. Plus mutation simulator, comparison views, pocket scoring | **The learned ADC-suitability scorer (D-015 §3)** — structure-derived features from our own ESMFold folds → a small trained model calibrated on the 22-positive labelled set, evaluation pre-registered (leave-one-out, fixed feature count, named negative outcome). ESMFold stops being the deliverable and becomes the scorer's **input**. Also learned mutation-impact / druggability |
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
├── app/                     # Streamlit + FastAPI application code (deployed to Fly) — later
├── core/                    # queue contract + pure logic + PostgresJobQueue (core/queue.py)
├── worker/                  # LOCAL GPU worker: pulls jobs, runs ESMFold (NOT deployed to Fly) — later
├── db/                      # models (db/models.py) + Alembic migrations (db/migrations/)
├── tests/                   # pytest; SQLite test DB (D-005). doubles.py = test-only fakes
├── docs/                    # plans, notes, and the design-decision log (README.md)
├── .github/workflows/       # CI: test gate → Fly deploy (D-005)
├── alembic.ini              # migration config; URL from $DATABASE_URL (direct conn, D-014)
├── pytest.ini               # pythonpath=. so tests import core/ and db/ (PR A)
├── requirements.txt         # runtime deps — human-edited input, exact pins (D-013)
├── requirements-dev.txt     # runtime + test deps — human-edited input (D-013)
├── requirements.lock        # compiled: every transitive pinned + hashed (Amendment A)
├── requirements-dev.lock    # compiled; THIS is what the gate installs, --require-hashes
└── Dockerfile               # serving tier image (Fly) — later
```

Today the repo holds the governance files, `docs/`, the **keel** (D-007), the **pinned +
locked dependency graph** (D-013), and — as of PR A (D-009 §1 implementation) — the **job
queue**: `core/queue.py` (the `JobQueue` seam, the pure `is_stale` predicate, and
`PostgresJobQueue`), `db/models.py` (`JobRecord`), and the first Alembic migration under
`db/migrations/`. The rest — `app/`, `worker/`, `Dockerfile`, and the remaining Database Plan
tables — is created as iterations land, and this layout section is updated when it changes.

The GPU tier's dependencies (`torch`, `transformers`, `bitsandbytes`) are **not** in these
manifests and will live in a separate one under `worker/` — CI runs on a CPU runner and must
never install a CUDA stack.

---

## 9. Governance (how this doc stays true)

1. **Every PR that changes architecture updates this file in the same PR.** No exceptions.
2. **Every design decision is written into [`docs/README.md`](docs/README.md) *before*
   the work it describes is finished** — the decision log leads the code, not the reverse.
3. When a decision in the log changes the system's shape, fold the outcome into the
   relevant section here so this document never drifts from reality.
