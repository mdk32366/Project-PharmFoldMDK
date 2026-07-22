# Session Pre-Work — Deployment Arc

**Preceded by:** the 2026-07-22 session, which built the pipeline end to end
(D-023 manifest → D-026 enqueue → D-030 loop → D-031 transport, PR #47).
**Session type:** first session of a new arc. Decision session, then build session.
**Status: DEP-001…004 RULED and Accepted (2026-07-22); D-033 (React UI) ruled alongside.**
This document is the arc's standing reference, updated as it was executed rather than left as
a snapshot of its own morning.

---

## 0. Provenance (D-016)

| Source | Can observe | Cannot observe |
|---|---|---|
| **Planner** | `PharmFoldMDK-20260722d-6792c21.zip` — the tree at `6792c21`, **including #47** | Anything after `6792c21` |
| **Builder** | `main` at HEAD | — |

**Both open questions from this document's first draft are now CLOSED against the tree:**

1. **No `Dockerfile`, no `fly.toml`** — verified absent at `6792c21`. #47 did not add them.
2. **The deploy job is still the placeholder** — `needs: [test, postgres]`, `if:` push-to-main,
   a single `echo`. Confirmed.

**And one assumption this document made was WRONG, corrected here rather than quietly:** the
first draft assumed Streamlit existed. **It does not** — no `streamlit` dependency, no Streamlit
code anywhere in the tree. `app/` is the FastAPI transport only (D-031's four routes). D-004
*planned* Streamlit; nothing built it. That correction is what surfaced the UI question at all,
and it is the sixth instance in two days of the same error class: **a plan read as a fact until
the tree corrected it.**

---

## 1. Why this arc gets its own designator

The decision log already distinguishes series: `D-NNN` for decisions, `S-NNN` for
spikes/measurements (S-001 the fp16 residency finding, S-003 the int8 recipe, S-004/S-005 the
local ceiling). That precedent is the model here.

**Deployment entries take the `DEP-NNN` prefix**, in the **same log file**, appended at top,
monotonic within the series. Not a second log — D-002's single-source-of-truth discipline is
unchanged, and a reader still sees one document.

**Why separate the series at all:** the D-series carries the graded scientific argument — the
research question, the cohort, the scorer, the coverage discipline. Deployment answers *how it
is operated*, not *what it claims*. Interleaving Fly tokens and Docker layers into that
narrative would cost the D-series its legibility for no gain. A reader tracing the scientific
claim can skip `DEP-*` entirely; a reader debugging a deploy can find them together.

**Deliberately NOT written: a deployment TDD.** Considered and rejected as disproportionate.
`docs/TDD_v3_ADC_Focused.md` is a *product* spec and predates D-015. Deployment here is a
Dockerfile, a `fly.toml`, a token, and a CI step — with the topology **already ruled by
D-004** (two tiers: Fly serving, local GPU worker, pull-based coupling). A design document
would be assembling decisions that already exist rather than making new ones. **The coherent
picture is D-004 plus the DEP entries.** If the arc turns out larger than scoped, that
judgement gets revisited in an entry rather than silently.

---

## 2. What is already ruled — state, do not re-decide

- **D-004** — two-tier topology. Fly serving tier: Streamlit + FastAPI + Postgres/pgvector +
  Volume, **always-on, no GPU**. Inference tier: the local machine. Coupling is the pull queue.
  **`worker/` runs locally and is NOT deployed to Fly.**
- **D-005 / D-008** — no untested code reaches prod; the gate is a required check with no admin
  bypass.
- **D-032** — `postgres` is now a **required** check alongside `test`
  (`required_status_checks = ["test","postgres"]`, verified 2026-07-22).
- **D-013** — runtime deps are hash-locked; the installed environment is a function of a
  committed file. #47 added FastAPI/uvicorn/python-multipart to the runtime lock.
- **D-014** — production Postgres is the existing Fly MPG cluster, own database.
- **The deploy job's shape** — `needs: [test, postgres]`, push-to-main only. That structure is
  correct and stays; only its body changes.

---

## 3. The forks — to be ruled as DEP entries before any wiring

### RULED — the four entries below were Accepted on 2026-07-22. Retained as the forks they
were, because the reasoning is the entry's, and the pre-work is where the alternatives were
visible.

**DEP-001 — What gets built into the image, and what is deliberately left out.** ✅ **Accepted.**
The Fly image serves `app/` (FastAPI) and Streamlit. **It must not contain `worker/`'s CUDA
stack** — D-018 kept `worker/requirements.txt` outside the lock guarantee precisely because
torch/transformers are a different dependency world, and D-004 says the worker is not
deployed. So the Dockerfile installs the **runtime lock only**. Worth ruling explicitly rather
than leaving to whoever writes the `COPY` lines, because the failure mode is a multi-gigabyte
image that silently works.

**DEP-002 — The deploy job's guard.** ✅ **Accepted** — guard on the JOB, never the trigger. `gate.yml`'s own header flags this:

> *"When real Fly deploy is wired, guard the DEPLOY JOB (not the trigger) against doc-only
> changes so docs still run tests but don't redeploy."*

Every docs PR today would otherwise trigger a production deploy. The guard belongs on the job,
never on the workflow trigger — D-008 removed `paths-ignore` because a required check that
does not report on every PR deadlocks that PR forever. **The distinction is the entry's whole
content**, and it is easy to get backwards.

**DEP-003 — `FLY_API_TOKEN`: scope, storage, rotation.** ✅ **Accepted** — app-scoped deploy
token (`fly tokens create deploy`), `pharmfoldmdk` only. Owner's reasoning: four other apps on
the account, and the deploy job never needs more authority than one app. Rotation is a named
owner action. A GitHub Actions secret. Open:
whether it is a deploy-scoped token or an org-wide one, and what happens on rotation. Small,
but it is the credential that can redeploy production and it should be named rather than
pasted.

**DEP-004 — What "deployed" means.** ✅ **Accepted**, and *narrower* than this draft first
framed it: a green deploy means **the transport API is up and the queue accepts work**. Not a
UI — there is none. Not folds — the worker is hand-started. D-004 is
explicit that `worker/` runs locally. So the deploy pipeline ships the serving tier only, and
**the worker is started by hand on the GPU box.** That asymmetry is correct but currently
unwritten, and a reader seeing a green deploy could reasonably assume the whole system is
running. It is not: **a green deploy means the serving tier is up and the queue is accepting
work — folds happen only when the owner starts the worker.** Worth one entry so the
green-deploy signal is not over-read.

---

## 4. Carried hazards — deployment-relevant subset

- **pgvector seam 2 remains OPEN** (`docs/HAZARD-search-path-seams.md`). Seam 1 (app-runtime
  commit path) was closed by D-026 and again by #47's handler test. Seam 2 — the `vector` type
  resolving through `extensions` on `search_path` — is **unproven**, and its named trigger is
  unchanged: the first `analysis_embeddings` write, downstream of D-027. **Deploying does not
  close it**, and D-032 says so explicitly: the CI service image is stock `postgres:16` with no
  vector column.
- **`worker/requirements.txt` is outside the lock guarantee** (D-018, by design; `accelerate`
  unpinned). Not a deploy concern — the worker is not deployed — but it *is* a concern the
  first time the owner starts the worker on the GPU box after an upstream release.
- **`--require-hashes` tamper rejection is asserted, not demonstrated.** Unchanged.

---

## 5. Two provisional numbers awaiting one measurement

Both retire on **the first end-to-end large rental fold**, and neither can be measured until
deployment exists:

| Number | Entry | Status |
|---|---|---|
| **3600 s lease** | D-030 | `PROVISIONAL — unmeasured under HTTP transport` |
| **PAE gzip ratio (5–10× est.)** | D-031 | estimate, not a measurement |

D-030 records the sharper point and it should not be lost: **the measurement will not settle
the lease question.** A fixed timeout has no correct value once fold durations are long and
variable — large enough never to reap a live fold is large enough to make a real vanish slow to
recover. **The structural answer is a lease heartbeat**, flagged for its own entry. The
measurement tells us whether 3600 is *safe*, not whether it is *right*.

---

## 5a. The UI decision that this arc surfaced — D-033

Discovering that Streamlit was never built (§0) made its framework an open question rather than
a settled one. **Ruled the same session: D-033 — the serving-tier UI is React, superseding
D-004's Streamlit clause only.** D-004's topology, pull coupling, and no-inbound-exposure
constraints stand.

Why it belongs in this arc's record: every UI commitment the log has made is an *interaction*
requirement — D-015 §1a's visually-distinct disagreement classes, D-024's coverage line with
drill-down, D-028's per-class quality tooltips. Those are the layer Streamlit rations. **3Dmol.js
is used directly**, since `py3Dmol` was only ever a wrapper around it, so nothing in the UI Plan's
3D capability list is lost.

**Consequence for THIS arc: none today.** DEP-001's image ships `app/` + `core/` + the runtime
lock; there is still no UI to ship, so DEP-004's meaning is unchanged. React adds a bundle build
and a static-serve path to the image **when the UI is built**, as a DEP-001 amendment at that
time. The JS toolchain sits **outside D-013's lock guarantee**, the same way `worker/`'s CUDA
stack does under D-018 — stated now rather than discovered later.

**Paperwork debt this creates**, tracked so it is not lost: `docs/UI_Plan.md` (Streamlit as
primary technology, `py3Dmol`/`stmol` for 3D, and no coverage/limitations surface at all — it
predates D-015/D-024/D-028), `ARCHITECTURE.md` (four places: :63, :105, :205, :461), and
`docs/TDD_v3_ADC_Focused.md:103`. **Its own task, not folded into D-033.**

---

## 6. Sequence

1. ~~**Rule DEP-001 … DEP-004.**~~ ✅ **Done** — all four Accepted 2026-07-22, plus D-033.
2. **Write the tests first** — per the project rule, including for deployment: the deploy job's
   doc-only guard is testable (a docs-only change must not trigger the deploy step), and the
   image contents are assertable (no torch in the runtime image).
3. **Build:** `Dockerfile`, `fly.toml`, the deploy job body, the token wired.
4. **Prove it RED→GREEN.** The deploy job is downstream of two *required* checks (D-032), so a
   change to the deploy path is exactly the class D-008 says gets proven, not merged on the
   strength of a passing run.
5. **Then, owner action:** start the worker on the GPU box and run the first end-to-end fold —
   which is §5's measurement.

---

## 7. Definition of done

- ✅ `DEP-001`–`DEP-004` **ruled**; to be placed in `docs/README.md` under the new prefix.
- ✅ `D-033` ruled — React supersedes D-004's Streamlit clause.
- ⬜ The paperwork debt (§5a) cleared — `UI_Plan.md`, `ARCHITECTURE.md`, `TDD` — as its own task.
- Tests written red first, including the doc-only deploy guard.
- `Dockerfile`, `fly.toml`, deploy job wired; suite green through both required checks.
- **A real deploy to Fly**, from a main-push, with the serving tier reachable.
- Close-out written — drafted **after** the final merge, and discarded rather than updated if
  work continues past it (the ritual amendment from 2026-07-22, where a close-out written
  mid-session went stale and was correctly held by the Builder).
