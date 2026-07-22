# PharmFoldMDK — Architecture

> **Living document.** This file is the single source of truth for how PharmFoldMDK
> is built and why. It MUST be updated **in the same change** that alters the
> architecture, and it MUST be brought current **before any PR is filed**. If a PR
> changes structure, data flow, dependencies, or deployment and does not touch this
> file, the PR is incomplete. See [`docs/README.md`](docs/README.md) for the
> chronological log of individual design decisions.

**Project**: PharmFoldMDK — an Antibody-Drug Conjugate (ADC) target exploration platform.
**Context**: Graded coursework for a **Deep Learning** class in an ML Master's program.
**Status (2026-07-22)**: Infrastructure complete and proven on real engines — the job queue
(D-009 §1, proven on Postgres 16 incl. `SKIP LOCKED`), migrations + pgvector (D-017/D-019), and
the GPU-tier **fold-runner** (`worker/runner.py`, D-018). Cohort measured (D-020); boundary/tier
decisions ruled (D-021/D-022). The **orchestrator manifest** (D-023, `core/manifest.py`) turns the measured cohort into a
deterministic, reviewable routing table plus the D-024 structured coverage object; the **enqueue**
(D-026, `core/enqueue.py`) turns each foldable row into a `protein_analyses` row (the exact
residues + UniProt release + folded span) and a `pending` `jobs` row carrying the tier's fold
recipe — 80 of 82 enqueue, the 2 named exclusions get none, idempotent per cohort version. The
**worker's job-pull loop** (D-030, `worker/orchestrator.py`) is built as a pure, transport-agnostic
loop over an injected client protocol (claim → fold → upload → complete, with server-side
done-ordering and the transport/fold-failure taxonomy). The **Fly transport** (D-031, `app/` +
`worker/http_client.py`) now realizes that protocol over HTTP: four routes (claim / artifacts /
complete / fail), one shared bearer token, the upload route writing the post-fold columns in a
compensated Volume+DB transaction, and `/complete` enforcing done-ordering server-side (409 until
`pdb_path` commits). It merged as the first PR under the now-**required** Postgres check (D-032).
The **deployment arc** (DEP-001…004) then wired the Fly serving tier: a runtime-only Docker image
(`app/` + `core/` + `db/`, hash-locked lock, **no `worker/`/CUDA** — DEP-001, enforced by an
image-contents test), a `fly.toml`, and a `deploy` job that runs `flyctl deploy --app pharmfoldmdk`
behind a doc-only guard on the job (DEP-002) with an app-scoped `FLY_API_TOKEN` (DEP-003). A green
deploy means **the transport API is up and the queue accepts work — not** that any fold has run
(DEP-004); the worker is hand-started on the GPU box. The UI was ruled **React**, superseding
D-004's Streamlit clause (D-033) — not yet built.
**Next (owner-gated):** the app-scoped token + Fly app/Postgres/secrets provisioning so the first
real deploy goes green; then starting the worker for the first end-to-end large rental fold — which
retires the PROVISIONAL 60-min lease threshold (D-030) and D-031's estimated PAE ratio with measured
values.

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
| **Worker transport** (D-031) | The four worker→Fly routes realizing the D-030 loop's protocol: claim → inline `FoldSpec`; artifacts → post-fold columns written in a compensated Volume+DB transaction (idempotent, PAE stored gzipped); complete → 409 until `pdb_path` commits; fail → terminal. Shared bearer token per route. Client-side is `worker/http_client.py` (gzips PAE, maps non-2xx → `TransportError`) | `app/` (FastAPI, on Fly) + `worker/http_client.py` (httpx, GPU tier); hermetic route/boundary/client tests + a real-Postgres seam-1 handler-write test |
| **Orchestration** (D-023, D-026) | `manifest.py`: measured cohort → deterministic routing table + D-024 coverage object, **reviewable before any job is created**. `enqueue.py`: foldable rows → `protein_analyses` (exact residues + UniProt release + folded span) + `pending` `jobs` (tier fold recipe); idempotent, 80/82 (2 named exclusions get none) | `core/manifest.py`, `core/enqueue.py` — CPU-side; hermetic on SQLite + a real-Postgres commit test |
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

- **`users`** — auth (username + hashed password), JSONB `preferences`. **Not built yet** (no
  auth code); this is why `protein_analyses.user_id` carries no FK yet (D-019).
- **`protein_analyses`** (D-019, `db.models.ProteinAnalysis`) — core durable record: input
  type/value, structure source, `pdb_path`, `mean_plddt`, `pae_json_path`, JSONB `metadata`
  (attr `meta` — "metadata" is reserved on the ORM Base), notes, and a nullable
  `ranking_run_id` FK → `ranking_runs` (D-015 §4). `user_id` is a nullable integer with **no FK
  yet** — deferred until `users` exists, the same pattern as the old `analysis_id` deferral.
- **`ranking_runs`** (D-019, `db.models.RankingRun`) — versions one cohort ranking
  (`target_list_version`, `scorer_version`, `created_at`), so a result ties to the target-list
  and scorer that produced it (D-015 §4, §7).
- **`analysis_embeddings`** — `vector(384)` + HNSW cosine index for semantic search
  (Iteration 3+). **Created in migration 0002 as raw SQL only — deliberately NOT an ORM model**
  (D-019), so the Postgres `vector` type never reaches SQLite `create_all` and no `pgvector`
  Python dep is added. This is the **first vector column, and it closes the last unproven point
  (D-017):** the migration runs `CREATE SCHEMA IF NOT EXISTS extensions; CREATE EXTENSION IF NOT
  EXISTS vector SCHEMA extensions;` then a **bare** `vector(384)` that resolves via env.py's
  `search_path` seam — exercised for real in the `postgres` CI job (now on a `pgvector/pgvector:pg16`
  image). Idempotent no-ops on prod (D-014). The **app-runtime** connection will need the same
  search_path — a separate seam in the engine config when the app queries embeddings (D-012 §5a).
- **`mutations`** / **`reports`** — 1:N from an analysis; **deferred** (Iteration 2/3, D-019).
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
  `created_at` (Amendment 3). **`analysis_id` FK → `protein_analyses` — CLOSED in D-019** (was
  deferred under Amendment 4; the migration that created `protein_analyses` added it in the same
  migration). This is the durable queue the local GPU worker (D-004) pulls from.

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
- **Postgres integration job (D-017) — the seam's other half.** A second CI job, `postgres`,
  stands up a real **Postgres 16** service container (matching prod, D-014), installs the same
  locked deps, applies migrations with **`alembic upgrade head`** (the real chain, *not*
  `create_all`), and runs the `@pytest.mark.postgres` tests. Those prove what the SQLite `test`
  job structurally cannot: that the migration chain builds the schema, that env.py's Postgres-only
  `search_path` SET runs without error, and that `PostgresJobQueue.claim`'s `FOR UPDATE SKIP
  LOCKED` is **atomic** (a locked row is skipped; all-locked yields None). `deploy` now
  **`needs: [test, postgres]`**. The postgres-marked tests auto-skip in the `test` job (no
  `DATABASE_URL`), so they are inert there and real only here.
  **Not yet a branch-protection required check** — that is an owner action (branch protection is
  owner-set, D-008), deliberately deferred until the service-container job proves stable, per the
  D-013 caution that a flaky *required* check with no admin bypass deadlocks every PR. Until it is
  required, `deploy: needs` is the gate: a broken migration cannot deploy even if a PR merged.
  **Still unexercised:** the service image is stock `postgres:16` and there is no vector column
  yet, so env.py's `search_path`→`extensions` *resolution* is proven only insofar as the SET does
  not error; it switches to a pgvector image when the vector-column migration lands (D-017).

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
| **2** | **Target ranking becomes the spine (D-015)** — a comparative view over the 82-target cohort (baseline evidence rank vs. structural rank, delta, movers), with single-target analysis as the drill-down. Plus mutation simulator, comparison views, pocket scoring | **The learned ADC-suitability scorer (D-015 §3)** — structure-derived features from our own ESMFold folds → a small trained model calibrated on the 22-positive labelled set, evaluation pre-registered (leave-one-out, fixed feature count, **two** named negatives incl. strong-correlation-is-null), with per-target fold/boundary/pLDDT diagnostics gating any ranking claim (D-015 §1a: disagreement is the expected outcome; the comparator is not an oracle). ESMFold stops being the deliverable and becomes the scorer's **input**. Also learned mutation-impact / druggability |
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
  ~~**Gap:** SQLite can't exercise pgvector/Postgres-specific paths~~ — **the Postgres
  integration job now exists (D-017):** a `postgres` CI job applies the real Alembic chain and
  exercises `SKIP LOCKED` against Postgres 16. The **fold-runner** adds a parallel split
  (D-018): its pure logic (provenance, pLDDT rescale, truncation recording) is unit-tested on
  the gate, while the GPU-bound `fold` auto-skips without torch+CUDA (`@pytest.mark.gpu`) and is
  validated on a GPU host — there is no GPU CI runner.
- **Reproducibility (course expectation):** pin model weights/versions, seed where
  relevant, and record any training/fine-tuning config so results can be reproduced.
  - Serving-tier deps are locked and hash-verified in CI (D-013 Amendment A).
  - **GPU-tier deps are a named, accepted gap (D-018):** `worker/requirements.txt`
    (`torch==2.11.0+cu128`, `transformers==5.14.1`, `bitsandbytes==0.49.2`, measured in S-003) is
    **never installed by CI** and so is **not covered by the lock-file guarantee** — a breaking
    release there is discovered at fold time, not by a red gate. Reproducibility of the GPU tier
    therefore rests on these pins plus the ESMFold weight revision pinned in `worker/runner.py`
    (`MODEL_REVISION`). `accelerate` has no measured pin yet (D-016: named, not invented) — pinned
    from the first GPU install.
  - **Every fold records its own provenance (D-018):** dtype, chunk_size, model revision,
    sliced-ECD-vs-whole, ECD bounds, and any length-cap truncation — written beside the artifacts.
    The truncation flag is load-bearing: D-015 §1a excludes truncated folds from ranking claims,
    which is unenforceable unless captured at fold time.

---

## 8. Repository Layout (target)

```
Project-PharmFoldMDK/
├── ARCHITECTURE.md          # this file — living source of truth
├── README.md                # how to run / deploy (kept current in Phase 6)
├── CLAUDE.md                # living-doc governance rules
├── app/                     # Fly serving tier (FastAPI): main.py (create_app factory),
│                            #   routes.py (D-031 four worker→Fly routes), artifacts.py (FoldSpec
│                            #   projection + compensated Volume+DB persist), deps.py, config.py
├── core/                    # queue.py (JobQueue seam + is_stale), manifest.py (D-023 routing
│                            #   table + D-024 coverage), enqueue.py (D-026 manifest → analyses+jobs),
│                            #   contracts.py (FoldSpec — tier-neutral claim contract, DEP-001)
├── worker/                  # GPU tier (NOT deployed to Fly): runner.py (D-018 fold-runner),
│                            #   orchestrator.py (D-030 job-pull loop, pure/transport-agnostic),
│                            #   http_client.py (D-031 concrete HTTP QueueClient, gzips PAE),
│                            #   main.py (entry point: wire client+loop+fold, `python -m worker.main`),
│                            #   ceiling_probe.py (D-022 A6000-ceiling bisection, owner-run),
│                            #   requirements.txt (CUDA deps + httpx, never installed by CI)
├── db/                      # models (db/models.py) + Alembic migrations (db/migrations/)
├── scripts/                 # ecd_lengths.py, map_genes_to_uniprot.py, deploy_guard.py (DEP-002)
├── tests/                   # pytest; SQLite test DB (D-005). doubles.py = test-only fakes
├── docs/                    # plans, notes, and the design-decision log (README.md)
├── .github/workflows/       # CI: test + postgres gates → Fly deploy job (D-005/DEP-002)
├── Dockerfile               # serving-tier image: runtime tier only, no worker/CUDA (DEP-001)
├── .dockerignore            # keeps worker/, venv, tests, docs out of the build context (DEP-001)
├── fly.toml                 # Fly serving-tier config: app pharmfoldmdk, always-on, Volume mount
├── alembic.ini              # migration config; URL from $DATABASE_URL (direct conn, D-014)
├── pytest.ini               # pythonpath=. so tests import core/ and db/ (PR A)
├── requirements.txt         # runtime deps — human-edited input, exact pins (D-013)
├── requirements-dev.txt     # runtime + test deps — human-edited input (D-013)
├── requirements.lock        # compiled: every transitive pinned + hashed (Amendment A)
└── requirements-dev.lock    # compiled; THIS is what the gate installs, --require-hashes
```

Today the repo holds the governance files, `docs/`, the **keel** (D-007), the **pinned +
locked dependency graph** (D-013), and — as of PR A (D-009 §1 implementation) — the **job
queue**: `core/queue.py` (the `JobQueue` seam, the pure `is_stale` predicate, and
`PostgresJobQueue`), `db/models.py` (`JobRecord`), and the first Alembic migration under
`db/migrations/`, plus the **fold-runner** (`worker/runner.py` + `worker/requirements.txt`,
D-018 — first GPU-tier code), the **job-pull loop** (`worker/orchestrator.py`, D-030), and the
**Fly transport** (`app/` + `worker/http_client.py`, D-031 — first application code on Fly). The
rest — the `Dockerfile` and real Fly deploy wiring, the Streamlit frontend, and the remaining
Database Plan tables — is created as iterations land, and this layout section is updated when it
changes.

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
