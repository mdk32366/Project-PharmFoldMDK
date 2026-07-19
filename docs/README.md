# PharmFoldMDK — Design Decision Log

> **This file is mandatory reading and mandatory writing.**
>
> **THE RULE:** *Every design decision we make gets written in this file **before** the
> work it describes is finished.* The log leads the code. If you are about to build,
> change, or discard something and the reasoning is not yet here, stop and record it
> first. A PR whose work is not reflected in a decision entry is incomplete.
>
> Companion documents:
> - [`../ARCHITECTURE.md`](../ARCHITECTURE.md) — the current-state architecture (must be
>   updated in the same PR as any architectural change, and before any PR is filed).
> - The planning docs in this folder (TDD, DB plan, UI plan, test plan, checklist) — the
>   *original* intent. Where a decision below diverges from them, **this log wins**.

## How to add a decision

Add a new `### D-NNN` entry at the **top** of the log (newest first). Use the template:

```
### D-NNN — <short title>
- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Superseded by D-XXX | Rejected
- **Context:** why this came up.
- **Decision:** what we are doing.
- **Deep-learning justification:** how this serves (or is neutral to) the DL-core mandate.
- **Consequences:** trade-offs, follow-ups, what it touches.
```

Every substantive decision must state its **deep-learning justification** — this is a
deep learning course project and the neural core is the graded deliverable (see
ARCHITECTURE §1).

---

## Log (newest first)

### S-002 — Spike: host stability under sustained GPU load, and a resident-footprint fix
- **Date:** 2026-07-19
- **Status:** Open
- **Type:** Spike (time-boxed investigation). Produces measurements and a decision input.
- **Why it exists:** S-001 ended in **three identical host bugchecks** (`0x00020001`
  HYPERVISOR_ERROR, byte-identical parameters, 16:32 / 16:44 / 16:48) during a 630 aa fold run
  under VRAM spill. Two questions are now open and they gate everything downstream.

**Q1 — Is the local inference tier viable at all?** (the decisive one)
- **The distinguishing test:** run a workload that fits *comfortably* in VRAM (well under
  7043 MiB free — e.g. a small model or a short sequence with the trunk sized to fit) under
  **sustained** GPU load for several minutes, and see whether the host stays up.
  - **Runs clean for several minutes → memory-pressure cascade.** The crash is a consequence of
    spilling past physical VRAM; fixing the resident footprint (Q2) plausibly fixes stability.
  - **Crashes anyway → hardware/driver problem.** Then the local GPU tier is not viable as
    designed, D-004's topology needs rework (not just its mitigation stack), and cache
    generation has to happen somewhere else entirely.
- **Record:** wall-clock survived under load, peak VRAM, GPU clocks/temperature, and any new
  Event-Viewer bugcheck (ID 41 / 1001) with its code and parameters.
- **Also worth doing:** read the existing minidumps (`071926-18656-01`, `071926-21093-01`,
  `071926-20781-01`) — the faulting module would separate "WDDM/shared-memory path" from
  "driver/hardware" cheaply, before any new run.

**Q2 — Which resident-footprint reduction actually fits 8 GB?** (bounded by D-004 §5)
- Candidates, each needing its own measurement (none is free):
  1. **Quantize the ESM-2 trunk** (e.g. 8-bit/4-bit) — cheapest to try; measure resident MiB,
     fold time, and **mean pLDDT vs the fp16 baseline (70.7 on Trop-2 248 aa)** to detect
     quality loss.
  2. **CPU-offload the language-model stack, keep the folding head resident** — trades VRAM for
     PCIe traffic; measure the wall-time cost honestly (this is the configuration D-004's stack
     never assumed).
  3. **Smaller ESM-2 backbone + folding head** — flagged as a **research project, not a config
     change**: `esmfold_v1` is the only released ESMFold checkpoint.
- **Out of bounds (restating D-004 §5):** making AlphaFold retrieval the deliverable. That is
  not a memory fix, it is abandoning D-003's graded DL claim.
- **Note:** warm-cache load is 15–16 s, so *load-per-job* is a live option and the worker need
  not hold the model resident.
- **Decides:** whether D-004's local tier survives; the D-006 replacement ladder (new rung one);
  and the D-009 §3 length cap, which stays unmeasured until a clean configuration exists.
- **Time box:** Q1 first — it is cheap and it can invalidate Q2 entirely. Do not spend effort
  choosing between quantization strategies for a host that cannot stay up under load.
- **Deliverable:** results appended here; then the D-006 ladder is rewritten and the D-009 §3
  cap is set (or the topology is reopened).

### D-009 — Iteration 1 scope, job queue shape, and ECD boundary selection
- **Date:** 2026-07-19
- **Status:** **Accepted (2026-07-19)** — §1 and §2 accepted as originally logged; **§3 resolved
  by S-001 to (A) cache-first**, with the length cap explicitly left unmeasured. Note that
  Iteration-1 application work remains blocked, now on **S-002** rather than on §3: (A) is
  chosen but not executable until a folding configuration exists that fits and does not crash
  the host.
- **Context:** D-004 ratified the two-tier topology and carried three items forward: the
  job queue schema and claim mechanism, extracellular-domain boundary selection, and the
  Iteration-1 scope question (cache-first vs. live-first). The first two are resolvable
  from known constraints. The third depends on measured ESMFold performance on 8 GB VRAM,
  which does not yet exist. Per the log-leads-the-code rule, the resolvable parts are
  ratified here and the unresolved part is stubbed explicitly rather than guessed.

---

#### §1 — Job queue: dedicated `jobs` table (Accepted)

- **Decision:** Fold jobs live in a **dedicated `jobs` table**, not as additional columns
  on `protein_analyses`.
- **Rationale:** `protein_analyses` rows are durable scientific records; job state is
  transient operational state with retries, failures, and worker ownership. Merging them
  would (a) attach permanently-dead queue columns to every historical analysis, (b) make
  retry semantics awkward, since a retry is a new attempt against the same analysis, and
  (c) conflate "this analysis exists" with "this fold is in flight."
- **Shape (initial):**

  | Column | Type | Notes |
  |---|---|---|
  | `id` | SERIAL PK | |
  | `analysis_id` | INTEGER FK → `protein_analyses(id)` | the record this fold produces |
  | `status` | VARCHAR(20) | `pending` \| `claimed` \| `complete` \| `failed` |
  | `claimed_at` | TIMESTAMPTZ NULL | set at claim; used for stale-claim reaping |
  | `completed_at` | TIMESTAMPTZ NULL | |
  | `worker_id` | VARCHAR(64) NULL | which worker holds it |
  | `attempts` | INTEGER DEFAULT 0 | retry budget |
  | `error` | TEXT NULL | last failure message |
  | `inference_settings` | JSONB | dtype, `chunk_size`, model revision, sequence length — the reproducibility record (D-004) |
  | `created_at` | TIMESTAMPTZ | |

- **Claim mechanism:** `SELECT ... FOR UPDATE SKIP LOCKED` — the standard Postgres
  queue-claim pattern. Correct with a single worker and remains correct without change if
  a second worker is ever added.
- **Indexes:** `jobs(status, created_at)` for the claim query; `jobs(analysis_id)`.
- **Stale claims:** a `claimed` job older than a threshold (initially 30 min) is returned
  to `pending` and `attempts` incremented. Covers the laptop-sleeps-mid-fold case, which
  D-004 accepted as a normal operating condition rather than an error.
- **Deep-learning justification:** indirect but load-bearing — this is the mechanism that
  lets neural inference run on hardware that can actually hold the model. Without a
  durable queue, the local-GPU tier from D-004 is not viable and the graded DL work has
  nowhere to execute.

---

#### §2 — ECD boundary selection from UniProt topology (Accepted)

- **Decision:** For each target protein, fold **only the extracellular domain**, with
  boundaries taken from **UniProt's `Topological domain` feature annotations** where the
  description is `Extracellular`.
- **Method:** Query the UniProt REST API for the accession, read `features` of type
  `Topological domain`, select extracellular spans, slice the canonical sequence to that
  residue range, and submit only the slice to ESMFold.
- **Persistence:** store the selected range and its provenance on the analysis row
  (`metadata` JSONB: `ecd_start`, `ecd_end`, `ecd_source`) so the 3D viewer can label
  precisely what is being displayed, and so results are reproducible.
- **Fallback:** when no extracellular topological annotation exists, fall back to the full
  canonical sequence **and surface a visible warning in the UI** — the user should know
  they are looking at a whole-protein fold, which for a long target may fail the
  length cap. Absence of annotation is scientifically informative, not merely an error.
- **Multiple extracellular spans:** where a target has more than one, select the longest
  by default and record the choice; per-span selection is a later enhancement.
- **Deep-learning justification:** this is what makes the D-003 model choice tractable on
  D-004 hardware, and it is *scientifically* correct rather than merely convenient — ADC
  antibody binding occurs at the ECD, so the domain we fold is the domain that matters.
  Reference sizes: HER2 ECD ~630 aa, Trop-2 ECD ~250 aa, Nectin-4 ECD ~350 aa, against
  full lengths of 1255 / 323 / 510 aa respectively.

---

#### §3 — Iteration 1 scope — **RESOLVED 2026-07-19: (A) cache-first**

- **Status:** **Accepted.** Resolved by S-001. The pre-registered branch that fired was
  *"600 aa OOMs / won't load cleanly in fp16 → **(A) cache-first**, and escalate."*
- **Decision:** **(A) cache-first.** Iteration 1 ships the Mission Briefing plus the curated
  ADC target database served from cached PDB/pLDDT/PAE artifacts. User-submitted live folding
  is deferred. The demo does not depend on the laptop being awake — which, given three host
  bugchecks under load, is now a hard requirement rather than a convenience.
- **The length cap is deliberately NOT set.** D-009 §3 originally expected the cap to fall out
  of the bisection. It cannot: **no configuration ran clean**, and the 630 aa fold was never
  measured (3/3 host crashes). A cap derived from a spilling, crashing configuration would be
  fiction. **The cap stays unmeasured until a working configuration exists (S-002).**
- **The binding condition on (A) still applies** (from the original stub): cache-first does not
  weaken the graded DL content **only if the folding pipeline is real, committed, reproducible
  code in this repo** that produces the cache — not a one-off script. That condition is now
  *doubly* binding, because the cache is the only path to a demo.
- **Blocked downstream:** the cache cannot be built until S-002 yields a configuration that both
  fits and does not crash the host. **(A) is chosen, but not yet executable.**

*(Original stub text retained below for the record.)*

- **Status (superseded):** UNRESOLVED. This clause is deliberately incomplete. Iteration-1
  application work MUST NOT begin until it is filled in.
- **The fork:**
  - **(A) Cache-first.** Iteration 1 ships the Mission Briefing plus the curated ADC
    target database, folded offline by the real pipeline and served from cached
    PDB/pLDDT/PAE artifacts. The worker and `jobs` table exist and are exercised by the
    offline folding run, but user-submitted live folding is deferred to Iteration 1.5.
    Demo is independent of the laptop being awake.
  - **(B) Live-first.** Iteration 1 ships the full loop: user submits a sequence → job
    queues → local worker folds → result renders. More moving parts; demo depends on the
    inference tier being online at presentation time.
- **What decides it:** spike **S-001** (below). The threshold, set in advance so the
  result is not rationalized after the fact:
  - 600 aa fold completes in **under ~2 minutes** at acceptable peak VRAM → **(B) viable**
  - 600 aa fold takes materially longer, or OOMs at `chunk_size=32` in fp16 → **(A)**,
    and the length cap is revised downward to whatever 8 GB actually sustains.
- **Note on the DL claim under (A):** cache-first does not weaken the graded deep-learning
  content **provided the folding pipeline is real, committed, reproducible code in this
  repo** — invoked to produce the cache — and not a one-off script run once by hand. If
  (A) is chosen, that condition is binding.

---

#### Follow-ups
- Alembic migration for `jobs` (blocked on §3 only in timing, not in content).
- Worker credential handling — Fly secrets, referenced by name (Principle 4).
- Authenticated artifact-upload endpoint (D-004 consequence, still open).
- ARCHITECTURE.md §4 (data model) gains `jobs`; §6 Iteration-1 row updates once §3 resolves.

### S-001 — Spike: measure ESMFold fp16 performance on 8 GB Blackwell
- **Date:** 2026-07-19
- **Status:** **CLOSED 2026-07-19** — answer: **no, not in this configuration** (see RESULTS).
- **Type:** Spike (time-boxed investigation, not a feature). Produces a measurement and a
  decision input, not shipped functionality.
- **Question:** Does `facebook/esmfold_v1` in fp16 fold ADC-relevant extracellular domains
  on an 8 GB Blackwell laptop GPU, and how fast?
- **Method:**
  1. Load `esmfold_v1` with `torch_dtype=torch.float16` on the local GPU.
  2. Set `chunk_size=64`. Fold a ~300 aa sequence (Trop-2 ECD scale). Record peak VRAM
     (`torch.cuda.max_memory_allocated`) and wall time.
  3. Fold a ~600 aa sequence (HER2 ECD scale). Same measurements.
  4. If either OOMs, retry at `chunk_size=32` and record.
  5. If 600 aa OOMs at 32, bisect downward to find the actual sustainable ceiling.
- **Record:** peak VRAM and wall time per sequence length and chunk size; mean pLDDT of
  each output as a sanity check that fp16 has not degraded quality; model revision hash
  and torch version.
- **Decides:** D-009 §3 (cache-first vs. live-first) and the final API sequence-length cap
  in D-004.
- **Time box:** one afternoon. If the model will not load at all in fp16, stop and
  escalate — that invalidates the D-004 mitigation stack and D-003 needs revisiting.
- **Deliverable:** results appended to this entry, then D-009 §3 filled in and promoted
  to Accepted.

---

#### RESULTS (2026-07-19) — **Status: CLOSED.** Escalation branch fired.

**Reproducer pin (what actually ran):**

| Item | Value |
|---|---|
| torch | `2.11.0+cu128` (CUDA build 12.8) |
| transformers | `5.14.1` |
| model | `facebook/esmfold_v1`, revision **`75a3841ee059df2bf4d56688166c8fb459ddd97a`** |
| precision | `esm.half()` → fp16 LM trunk + fp32 folding trunk |
| GPU | NVIDIA RTX PRO 2000 Blackwell Laptop, capability sm_120 |
| **on-disk weights** | **9,581,481,414 B ≈ 9.58 GB** (`du`); the in-run tree walk reported 9.78 GB — Windows lacks symlink support so HF duplicates blobs into `snapshots/`. **Not the ~2.5 GB originally assumed.** Disk ≠ VRAM, but it is the worker's deployment footprint. |

**Unit correction (load-bearing, applies to every figure below):** `nvidia-smi` reports
**MiB**; torch reports **decimal GB**. `8151 MiB` = 8.55 GB decimal (≠ "8.15 GB").
All memory figures below are normalized to **MiB**.

**Memory — the model does not fit at rest:**

| Quantity | MiB |
|---|---|
| Physical VRAM | **8151** |
| Free at start (desktop using the rest) | 7043 (run 2/3); 7799 (run 1) |
| **Resident after fp16 load** | **8116** |
| Peak during 248 aa fold | **8545** |

`params_all_on_cuda = True` (all 4498 params on CUDA — no accelerate/`device_map` offload),
**but resident (8116) exceeds free VRAM (7043)**, so Windows WDDM silently spilled to shared
system RAM rather than raising OOM. Peak (8545) exceeds even *total* physical (8151).
**Conclusion: fp16 alone does not fit `esmfold_v1` in 8 GB.** The absence of an OOM is a
Windows artifact, not evidence of a fit; on Linux this would have raised `CUDA out of memory`.

**Load time — run 1's 631 s was WRONG as a load figure.** It was download-dominated. From a
warm cache, **load = 15–16 s** (runs 2 and 3, consistent). Relevant to D-004 worker design:
loading per job is cheap; holding resident is what does not fit.

**Folds actually measured:**

| Target | Len | Chunk | Time | Peak | mean pLDDT | Verdict |
|---|---|---|---|---|---|---|
| Trop-2/TACSTD2 ECD (23–274→27–274) | 248 | 64 | 48.8 s | 8545 MiB | 70.7 | **NOT-CLEAN — `vram-spill`** (run 1 logged `CLEAN` *before* spill detection existed; superseded) |
| **HER2/ERBB2 ECD (23–652)** | **630** | — | — | — | — | **NEVER MEASURED — host bugchecked, 3/3 attempts** |

**pLDDT scale trap fired for real:** raw B-factors came back on the **0–1 scale** and were
rescaled ×100 (`rescaled-x100(raw was 0-1 scale)`) to 70.7. Unrescaled, the guard would have
read 0.707 and wrongly flagged it as suspect/zero. The check is honest only because the
rescale is explicit.

**Host instability — the run never completed:** three attempts at the 630 aa fold, three
hard crashes, all with the **identical bugcheck `0x00020001` (HYPERVISOR_ERROR)**, byte-identical
parameters `(0x28, 0x1, 0x29b92701, 0xfc801000)`:

| # | Kernel-Power 41 (crash) | BugCheck 1001 (reboot) | Minidump |
|---|---|---|---|
| 1 | 2026-07-19 16:32:19 | 16:32:32 | `071926-18656-01.dmp` |
| 2 | 2026-07-19 16:44:28 | 16:44:44 | `071926-21093-01.dmp` |
| 3 | 2026-07-19 16:48:00 | 16:48:15 | `071926-20781-01.dmp` |

Identical signatures across three independent runs indicate a **reproducible fault**, not random
corruption. Whether it is a memory-pressure cascade (VRAM spill thrashing the WDDM/shared-memory
path) or an underlying hardware/driver problem is **not determined by this spike** → **S-002**.

**Decides:** D-009 §3 → **(A) cache-first** (the pre-registered "won't load cleanly in fp16 →
cache-first + escalate" branch). Length cap **remains unmeasured** — a cap cannot be set from a
configuration that never ran clean. D-004's mitigation stack is invalidated at rung one (amended
below). **The local inference tier's viability is now itself unproven** pending S-002.

### D-008 — Gate proven; branch protection required; paths-ignore removed
- **Date:** 2026-07-19
- **Status:** Accepted (supersedes the "doc-only commits bypass the test gate" clause of
  D-005 and the `paths-ignore` choice in D-007)
- **Context:** The CI gate (D-005/D-007) was only half a gate. `push: branches: [main]`
  makes the main-push run a **post-hoc check** — it runs on a commit *already on main*, so
  nothing is physically blocked; the keel run went green because the code was clean, not
  because a gate stood in the way. **The PR path is the real gate**, and it only blocks if
  `main` is *protected* and merging is the only route in. Proven empirically below.
- **Evidence (all on 2026-07-19):**
  - **Red gate on a PR:** PR #1 (`break-it`, deliberately broken assert) → gate run
    **`test` = failure, `deploy` = skipped** (`deploy: needs: test` did its job):
    https://github.com/mdk32366/Project-PharmFoldMDK/actions/runs/29706935765
  - **Advisory-only before protection:** PR #1 read `MERGEABLE / UNSTABLE` — a failing
    check did **not** block merge on its own.
  - **Blocking after protection:** same PR flipped to `MERGEABLE / BLOCKED` once `test`
    was required.
  - **Direct push refused:** `git push origin main` (empty commit) →
    `GH006: Protected branch update failed ... Changes must be made through a pull
    request ... Required status check "test" is expected.`
- **Decision:**
  1. **Branch protection on `main` is a hard prerequisite** and is now set: require a pull
     request (0 approvals), require the **`test`** status check, **`enforce_admins: true`**
     (no bypass — including the owner), no direct pushes. Direct pushes to `main` (like the
     keel commit `d656b63`, which predated protection) are no longer possible.
  2. **Remove `paths-ignore` from `gate.yml`.** With `test` now a *required* check, a
     doc-only PR that never triggered the workflow would leave the required check
     unreported and the PR **unmergeable forever**. Dropping `paths-ignore` makes the ~20s
     suite run on every PR, so the check always reports; docs pay a trivial always-green
     cost instead of deadlocking.
- **Deep-learning justification:** Neutral (process), but this is the difference between a
  gate that *looks* enforced and one that actually is — the guarantee that no untested
  inference code can reach prod now holds against a tired 11pm `git push origin main`.
- **Consequences / follow-ups:**
  - Doc-only commits now run the test suite (they pass trivially and are never blocked) —
    this is the accepted reversal of the earlier doc-bypass intent.
  - When the real Fly deploy replaces the placeholder, **guard the `deploy` job** (not the
    workflow trigger) against doc-only changes, so docs still run tests but don't redeploy.
  - `enforce_admins: true` means even the owner merges via PR with `test` green — by design.

### D-007 — Lay the keel: `tests/` + CI deploy gate scaffold
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** Realize the D-005 deploy gate as actual repo scaffolding **before** any
  application code exists, so the "no untested code to prod" discipline is in place from
  the first line of real code.
- **Decision:**
  - **`tests/`** with `conftest.py` exposing an **in-memory SQLite fixture** and one trivial
    passing smoke test. The fixture uses the **stdlib `sqlite3`** module (zero extra deps →
    CI green with only `pytest`); it will graduate to SQLAlchemy/SQLModel sessions when
    models land.
  - **`.github/workflows/gate.yml`**: `deploy` job `needs: test`; **native `paths-ignore`
    filter** (`**.md`, `docs/**`) so doc-only commits never trigger the workflow (that is
    how they "bypass the gate" per D-005). CI pins **Python 3.11**, `actions/checkout@v5`,
    `actions/setup-python@v6`.
  - The **`deploy` job is a placeholder** (echo) — real Fly deploy (flyctl + `FLY_API_TOKEN`)
    is wired in a later decision once the app exists. **No application code written.**
- **Deep-learning justification:** Neutral (scaffolding), but it stands up the gate that
  will protect the DL pipeline's correctness before any inference code can reach prod.
- **Consequences:** The SQLite fixture is stdlib-only for now; pgvector/Postgres paths still
  need the separate integration job flagged in D-005. Deploy is inert until wired.

### D-006 — ESMFold fold-path strategy for the 8 GB VRAM budget
- **Date:** 2026-07-19
- **Status:** ⚠ **INVALIDATED AT RUNG ONE (2026-07-19) by S-001** — see the amendment on D-004.
  The ladder below assumes fp16 makes the model *fit at rest*; measurement shows it does not
  (resident 8116 MiB vs 7043 MiB free). Rungs 2–6 reduce **activation** memory and cannot fix a
  **resident-weight** overrun. Do not implement this ladder as written; the first rung must
  become a resident-footprint reduction (quantization / CPU-offload / smaller backbone — S-002).
  Retained verbatim below for the record.
- **Context:** The local inference GPU has **8 GB VRAM** (D-004). Full `esmfold_v1`
  (ESM-2 3B) wants ~16 GB+ for long sequences, so it will OOM on large proteins without a
  deliberate memory strategy. ADC targets are often large, but ADCs bind **cell-surface
  epitopes**, so the extracellular region is the scientifically relevant part to fold.
- **Decision — a layered strategy, applied in order:**
  1. **Half precision:** run the ESM-2 language-model trunk in fp16 on the GPU to roughly
     halve activation memory.
  2. **Axial-attention chunking:** set a `chunk_size` (start **128**, step down to 64/32 on
     OOM) to cap peak attention memory at a modest speed cost.
  3. **Extracellular-domain folding:** for a UniProt input, parse topology
     (`TRANSMEM` / `TOPO_DOM` features), extract the **extracellular domain(s)**, and fold
     those rather than the full chain — both ADC-appropriate and VRAM-friendly. If topology
     is unavailable, fall back to a length-capped full fold.
  4. **Interactive length cap:** the live "bring-your-own-sequence" path caps at
     **~400 residues** (starting value); longer inputs are routed to the offline pipeline
     or folded domain-only.
  5. **Graceful OOM degradation on the worker:** catch CUDA OOM → retry smaller
     `chunk_size` → **CPU-offload** the trunk (using the 31.5 GB system RAM, slow but
     completes) → else mark the job `needs_offline`.
  6. **Offline pre-compute pipeline:** a non-interactive worker mode folds the **curated
     ADC target database** ahead of time (CPU-offload allowed, no time pressure); results
     are cached as Volume artifacts + DB rows so the class demo path is always instant.
- **Deep-learning justification:** These are the model-execution decisions themselves —
  precision, attention chunking, and input truncation are standard neural-inference
  engineering, and folding the extracellular domain aligns the model's compute with the ADC
  biology. This is exactly the "how we actually run the deep model" reasoning the course
  expects, not an API wrapper.
- **Consequences / follow-ups:**
  - The 400-residue cap and `chunk_size=128` are **estimates**; measure real peak memory vs.
    sequence length on the 8 GB card and update this entry with the validated numbers.
  - Domain extraction needs a UniProt topology parser; proteins lacking topology annotation
    fall back to length-capped full folding.
  - fp16 may slightly reduce coordinate accuracy vs. fp32 — acceptable for exploration;
    note it in output caveats.
  - Adds an **offline pre-compute worker mode** to the `worker/` component (D-004).

### D-005 — CI/CD deploy gate + testing strategy (no untested code to prod)
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** Deployment to Fly.io must be rock-solid — **no untested code reaches prod.**
- **Decision:**
  - **GitHub Actions gate:** on PRs and pushes to `main`, run a `test` job; the Fly
    **deploy job runs only if tests pass** (`deploy: needs: [test]`).
  - **All tests live in `tests/`** (plural — matches the existing Test Plan and pytest
    convention; if you want the literal singular `test/`, say so and I'll rename).
  - **Two kinds of tests:** (1) **functional** — `pytest`, `*.py`, covering data layer,
    inference logic, API contracts (per Test Plan §A); (2) **user-based** — structured
    human scenarios (per Test Plan §B), run at iteration boundaries, gating iteration
    sign-off rather than each push.
  - **Test database is SQLite** (in-memory / temp file): fast, deterministic, no external
    DB in CI. All external calls — ESMFold inference, AlphaFold DB, UniProt — are mocked.
  - **Doc-only commits bypass the test gate:** a path filter treats changes limited to
    `docs/**`, `**/*.md`, `ARCHITECTURE.md`, `LICENSE`, etc. as non-code and skips the
    `test` job. Any change touching code runs the full gate.
- **Deep-learning justification:** Neutral (process), but it guards the DL pipeline's
  correctness — pLDDT/PAE parsing, fallback behavior, and the job-queue contract get
  tested before they can reach prod.
- **Consequences / known gaps:**
  - **SQLite ≠ Postgres/pgvector.** Vector search and Postgres-specific SQL cannot run on
    SQLite, so those paths must be mocked or covered by a **separate Postgres integration
    job** later (flag for Iteration 3). *(Same class of gap JARVIS hit: SQLite `create_all`
    never exercises real Postgres/migration behavior.)*
  - Deploy needs `FLY_API_TOKEN` in GitHub Actions secrets.
  - The local GPU worker (D-004) is out of the prod deploy path but its contract with the
    app (job schema, artifact upload) must be covered by functional tests.

### D-004 — Deployment & inference topology: Fly serving tier + local GPU worker (pull-based)
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** ESMFold (D-003) is GPU-heavy and Fly.io GPU is uncertain/expensive. The
  developer has a local machine with an **NVIDIA RTX PRO 2000 Blackwell Laptop GPU (8 GB
  VRAM)** and **31.5 GB system RAM**, and wants the app web-accessible but the model on
  local hardware.
- **Decision:** Split into two tiers.
  - **Serving tier — Fly.io:** Streamlit + FastAPI + Postgres/pgvector + Volume. Always-on,
    **no GPU**. Accepts analyses, stores data/artifacts, serves the UI.
  - **Inference tier — local machine:** a worker process running **ESMFold on the local
    NVIDIA GPU**.
  - **Coupling = pull-based job queue.** The web app enqueues an analysis job (a Postgres
    row, `status=pending`). The local worker **polls Fly over an authenticated outbound
    HTTPS connection**, claims pending jobs, folds, uploads artifacts (PDB / pLDDT / PAE)
    back to the Fly Volume, and sets `status=done|error`. **No inbound exposure of the home
    machine; no tunnel required.**
- **Deep-learning justification:** This is what makes running our own ESMFold feasible on a
  student budget — the neural inference runs on capable local hardware while the app stays
  web-accessible. The deep learning is still *ours*, executed by our worker.
- **Why pull-based over a tunnel (the ratified recommendation):** a laptop GPU sleeps,
  changes networks, and a fold takes seconds–minutes; pull-based tolerates intermittent
  connectivity, requeues on worker death/OOM, needs no open inbound port, and matches the
  async nature of folding. A synchronous tunnel (Tailscale/Cloudflare) would require the
  machine to be reachable and hold long HTTP requests open — kept only as a fallback.
- **Consequences / follow-ups (each becomes its own entry before we act):**
  - **8 GB VRAM is the binding constraint.** Full `esmfold_v1` (ESM-2 3B) wants ~16 GB+ for
    long sequences → OOM risk on large proteins. Mitigations to design: axial-attention
    `chunk_size`, a **live sequence-length cap**, folding only the **ADC-relevant
    extracellular domain**, and **pre-computing the curated ADC target DB offline** (can
    CPU-offload using the 31.5 GB system RAM and be patient).
  - **Availability:** if the local worker is offline, live jobs **queue** (no loss) but
    don't complete; pre-computed curated targets keep the class demo always-live.
  - **Worker plumbing needed:** an API token for the worker, job claim/lease semantics to
    avoid double-processing, and stale-job requeue on worker death (cf. JARVIS
    `recover_stale_jobs`).
  - **New repo component `worker/`** — runs locally, **not** deployed to Fly.

---

#### ⚠ AMENDMENT (2026-07-19, on S-001 results) — the mitigation stack is invalid at rung one

- **What broke.** The stack above (and its expansion in D-006) was ordered **fp16 → chunking →
  length cap → ECD scoping → caching**. Every rung *after the first* assumed the model **fits at
  rest** and that the remaining problem is activations. S-001 measured the opposite: the fp16
  model is resident at **8116 MiB against 7043 MiB free / 8151 MiB physical** — it spills to
  shared system RAM *before a single fold begins*. **fp16 alone does not get `esmfold_v1` into
  8 GB.** Chunking, caps, and ECD scoping all reduce *activation* memory; none of them reduce
  the *resident weight* footprint that is already over budget. The stack therefore needs
  **restructuring, not tuning**: the first rung must become a *resident-footprint* reduction.
- **Consequence for the topology.** D-004's two-tier design is not refuted, but the **local
  inference tier's viability is now unproven** — three attempts at a 630 aa fold ended in an
  identical host bugcheck (`0x00020001`). Whether the local GPU can sustain this work at all is
  **S-002**, and it gates the tier.
- **Bounded option space (restating §5 so the boundary is visible when the fix is picked).** A
  non-fit points to a **smaller/lighter folding configuration or narrower targets** — explicitly
  **NOT** a retreat to AlphaFold retrieval. Inside the boundary: **(a)** quantize the ESM-2
  trunk, **(b)** CPU-offload the language-model stack while keeping the folding head resident,
  **(c)** pair a smaller ESM-2 backbone with a folding head. Outside the boundary: making
  retrieval the deliverable (that would gut D-003's graded DL claim).
- **Reality check on (c):** `esmfold_v1` is the **only released ESMFold checkpoint**, so
  "just use a smaller variant" mostly is not a thing — (c) is a research project, not a config
  change. None of (a)/(b)/(c) is free and each needs its own measurement → **S-002**, not a
  guess made here.
- **Corrected worker input:** warm-cache load is **15–16 s**, not the 631 s recorded in run 1
  (that figure was download-dominated). Cheap loads make *load-per-job* viable, which matters
  precisely because *holding resident* is what does not fit.

### D-003 — Run ESMFold ourselves as the Iteration-1 deep-learning core
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** The course grade depends on a neural network doing load-bearing work
  (ARCHITECTURE §1). Structure prediction is the tool's foundational output, so it is the
  natural home for the graded DL. The two candidates were (a) run a protein-folding model
  ourselves vs. (b) retrieve pre-computed structures from AlphaFold DB with a smaller
  neural component elsewhere. Option (b) risks reading as "just an API wrapper."
- **Decision:** PharmFoldMDK will **run ESMFold in-project** to predict 3D structure
  directly from an amino-acid sequence. ESMFold (Meta AI) is a transformer stack: the
  ESM-2 protein language model produces residue representations that a folding head turns
  into 3D coordinates, **from a single sequence with no MSA required**. We load it via
  Hugging Face (`facebook/esmfold_v1`, `EsmForProteinFolding`) / PyTorch. It emits
  per-residue **pLDDT** and **PAE**, which map straight onto our data model
  (`protein_analyses.mean_plddt`, `pae_json_path`). AlphaFold DB / UniProt retrieval is
  demoted to an **optional fast path for already-solved canonical proteins and a
  fallback**, not the deliverable — ESMFold is what we run and defend.
- **Deep-learning justification:** This is the strongest available DL story: our system
  performs neural inference (a ~3B-parameter transformer language model + folding head) to
  produce the primary output. It gives us genuine DL substance to present and analyze —
  the ESM-2/transformer architecture, single-sequence inference vs. MSA-based AlphaFold2,
  pLDDT confidence calibration, and behavior on cancer-target variants that may not exist
  in AlphaFold DB. It also uniquely enables Iteration 2's **mutation impact** (fold the
  wild-type and the mutant and compare) — retrieval alone cannot fold an arbitrary mutant.
- **Consequences / follow-ups (each becomes its own decision entry before we act):**
  - **Compute & memory is the primary risk.** Full `esmfold_v1` is GPU-hungry
    (multi-GB weights; long sequences can exceed ~16 GB GPU RAM). Fly.io GPU availability
    is uncertain and the TDD flagged GPU deprecation. **Open D-00X:** where inference runs
    (in-process vs. dedicated worker/queue) and on what Fly compute (CPU-only tolerated for
    short sequences vs. GPU). Mitigations to evaluate: axial-attention `chunk_size`,
    sequence-length caps for the demo, and **pre-computing + caching** structures for the
    curated ADC target database so the live demo path is fast.
  - **Sequence-length limit** for the graded demo (ADC targets are often large; may fold
    only the extracellular domain relevant to ADC binding) — to be set in a later entry.
  - **Dockerfile / dependency weight** grows (torch, transformers, model weights); cold
    start includes model load — plan a warm-load path.
  - **Reproducibility:** pin the model revision and torch version; record device and any
    `chunk_size`/length settings with each analysis (course reproducibility expectation).
  - Updates `ARCHITECTURE.md` §3 (DL core ratified), §5 (compute now an active concern),
    and §6 (Iter-1 DL content confirmed).

### D-002 — Governance: living architecture doc + this decision log
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** The project must be maintainable and sustainable long-term, and its design
  rationale must be traceable for grading and for future work.
- **Decision:** Maintain `ARCHITECTURE.md` (repo root) as the single source of truth for
  system shape, updated in the same PR as any architectural change and brought current
  before any PR is filed. Maintain this `docs/README.md` as an append-at-top decision log
  where every design decision is written **before** its implementing work is finished.
  Both rules are encoded in `CLAUDE.md` so every working session is bound by them.
- **Deep-learning justification:** Neutral (process). Indirectly protects the DL mandate
  by forcing each decision to state where the deep learning is before code lands.
- **Consequences:** Slight up-front writing overhead per change; in exchange the project
  stays auditable and the DL story stays front-and-center.

### D-001 — Planning docs live in the repo under `docs/`
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** Planning docs (TDD v3, DB plan, UI plan, test plan, checklist, proposal)
  were sitting in a non-git sibling folder, unversioned.
- **Decision:** Moved all six into `docs/` with flattened filenames and committed
  (`6ea1e7e`). They are the reference intent; ratified changes are logged here.
- **Deep-learning justification:** Neutral (housekeeping).
- **Consequences:** Single versioned home for project intent; the `.docx` proposal is
  tracked as binary.

---

## Open questions awaiting a decision entry

These are known forks in the road. Each becomes a `D-NNN` entry **before** we act on it.

- ~~**DL core for Iteration 1**~~ — **resolved in D-003: run ESMFold ourselves.**
- ~~**Where inference runs + Fly compute**~~ — **resolved in D-004: local GPU worker,
  pull-based; Fly serving tier has no GPU.**
- ~~**Sequence-length cap / domain selection**~~ and ~~**pre-compute & cache pipeline**~~ —
  **resolved in D-006** (fp16 + `chunk_size` + extracellular-domain fold + 400-residue live
  cap + OOM degradation + offline pre-compute). Caps still need empirical validation.
- **Worker ↔ app contract:** job schema, claim/lease semantics, artifact upload, auth token.
- **Prod DB choice:** Postgres-first vs. SQLite-on-Volume prototype (Database Plan §5).
  *(Note: this is the **prod** DB; the **test** DB is SQLite per D-005 regardless.)*
- **Embedding model** for semantic search (which encoder, `vector(384)` assumed).
- **Postgres integration test job** for pgvector/Postgres-specific paths (D-005 gap).
