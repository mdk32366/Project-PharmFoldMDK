# PharmFoldMDK — Design Decision Log

> **This file is mandatory reading and mandatory writing.**
>
> **THE RULE:** *Every design decision we make gets written in this file **before** the
> work it describes is finished.* The log leads the code. If you are about to build,
> change, or discard something and the reasoning is not yet here, stop and record it
> first. A PR whose work is not reflected in a decision entry is incomplete.
>
> **THE SECOND RULE (provenance, D-016):** *Every claim names how it is known.* A written
> record fixes a claim in place; it does not make it true. Before a number or a status enters
> this log, ARCHITECTURE, or a PR, name the artefact it came from — the raw log line, the query
> output, the run URL. If you cannot name it, you are recording a belief, not a finding. A
> summary is not knowing: prefer the breakdown to the total, and **prefer the query whose answer
> could disqualify you** (`pg_available_extensions` tells you a thing *exists*; `pg_extension`
> only that it is *on* — a zero from the second cannot distinguish *absent* from *off*).
>
> Companion documents:
> - [`../ARCHITECTURE.md`](../ARCHITECTURE.md) — the current-state architecture (must be
>   updated in the same PR as any architectural change, and before any PR is filed).
> - The planning docs in this folder (TDD, DB plan, UI plan, test plan, checklist) — the
>   *original* intent. Where a decision below diverges from them, **this log wins**.

## How to add a decision

> **Numbering note: there is no D-010.** The sequence runs D-001…D-009 then D-011. Nothing was
> deleted — the number was simply skipped. Not renumbered, because commit `c07b95b` already
> references D-011 by name. Spike entries use `S-NNN` and instrument/method findings use `F-NNN`.

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

## Method note: state a check precisely enough that its inadequacy is discoverable

Learned the hard way on 2026-07-19 (see S-001 and S-002, where two confidently-stated claims were
caught and reversed):

- **`params_all_on_cuda=True`** was a *true* summary that missed **spill** — every parameter really
  was on CUDA, while the allocation silently exceeded physical VRAM.
- **"217 WHEA events since May"** was a *true* summary that missed **severity** — 213 were
  corrected, only 4 fatal, and the fatal signature had no history at all.

Both errors came from **accepting a summary instead of returning to the raw records**, and both
were caught only because the check had been stated specifically enough to be *shown* inadequate.
So the rule is not "be careful" — it is:

1. **Write the check as a concrete assertion with units and a threshold**, so a later reader can
   test whether it actually covers the claim ("resident MiB vs *free* MiB", not "does it fit").
2. **Bucket before you count.** A total is compatible with more hypotheses than a breakdown is;
   prefer rates and severity splits to raw counts.
3. **Label inference status explicitly** — *measured* / *predicted* / *assumed* — and never let a
   *predicted* mechanism be cited later as a finding.
4. **Record the provenance chain when a claim changes**, including the wrong intermediate versions.
   The reversal is itself evidence about how much the current version should be trusted.
5. **Before using a metric as a *leading indicator*, verify its events actually PRECEDE the thing
   it predicts.** (Added 2026-07-19 after **F-001**.) WHEA corrected-error rate was used for hours
   as an early-warning signal for host crashes; per-second timestamps then showed the fatal is
   logged *in the same second* as the corrected errors, and that six burst days with 65/40/31
   corrected errors produced **zero** crashes. The metric was **anti-correlated** with its target.
   A metric can be real, well-defined, correctly queried — and still measure the *aftermath* of the
   event you meant to predict. **Check the time-ordering, not just the correlation.**
6. **Prefer the instrument-free comparison when one exists.** The strongest result in this whole
   investigation needs no event log at all: *4 crashes in 4 HER2 attempts, 0 in ~93 Trop-2 folds.*
   When a raw outcome count is available, it outranks any derived telemetry.

---

## Log (newest first)

### DEP-004 — What a green deploy means, and what it does not
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)**
- **Series note:** first entries under the `DEP-NNN` prefix — deployment/operations, same log,
  appended at top, monotonic within series (D-002's single-log discipline unchanged). The
  precedent is `S-NNN` for spikes: a prefix that says which arc an entry belongs to, so a reader
  tracing the graded scientific claim can skip `DEP-*` and a reader debugging a deploy can find
  them together. **No deployment TDD** — considered and rejected as disproportionate; the
  coherent picture is D-004 plus these entries.
- **Context:** Deployment is about to produce a green "deploy succeeded" signal on every
  main-push. That signal is easy to over-read, and two facts make the honest reading narrower
  than the word "deployed" implies:
  - **The worker is not deployed** (D-004): `worker/` runs on the local GPU box and is started
    **by hand**. Nothing in the deploy pipeline starts it.
  - **There is no UI yet.** D-004 plans Streamlit as the serving tier's front end, but **it does
    not exist** — verified against the tree at `6792c21`: no `streamlit` dependency, no Streamlit
    code. `app/` is the FastAPI transport only (the four worker→Fly routes from D-031).
- **Decision — a green deploy means exactly this: the transport API is up on Fly and the queue
  is accepting work.** It does **not** mean:
  - that any fold has run, or can run without the owner starting the worker;
  - that a user-facing UI is reachable — there is none to reach;
  - that the full system is "live" in any sense a reader might assume from a green checkmark.

  Stated so the signal is not over-read — by the owner, or by a grader seeing a passing deploy.
- **Deep-learning justification:** neutral — operational honesty, not a model decision. Recorded
  because an over-read green is the deployment-arc version of the failure the whole log guards
  against: a signal that claims more than it demonstrates.
- **Consequences:**
  - When Streamlit is built, it is its own entry and it changes what a green deploy means — at
    which point this entry is amended, not silently outgrown. *(Superseded in part by D-033: the
    UI is React, not Streamlit — but the shape of this consequence is unchanged: the first UI to
    ship amends what a green deploy means.)*
  - **Starting the worker on the GPU box is an owner action**, and it is the precondition for the
    first end-to-end fold (the measurement that retires D-030's provisional lease and D-031's PAE
    ratio).

---

### DEP-003 — `FLY_API_TOKEN`: an app-scoped deploy token, not an account token
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)**
- **Context:** The deploy job authenticates to Fly with a token held as a GitHub Actions secret.
  A GitHub Actions secret is readable by any workflow run on the repo, so its blast radius on
  compromise is the question, not merely its convenience.
- **Decision — an app-scoped deploy token (`fly tokens create deploy`), scoped to
  `pharmfoldmdk` alone.** Not an account/org-wide token.
  - **Rationale, owner's ruling:** there are **four other apps on the account**. An account-wide
    token in CI means a compromised workflow could redeploy or disrupt all five; an app-scoped
    token can touch only this one. The scope cost is nil — the deploy job only ever deploys this
    app — so there is no reason to hold more authority than the job uses.
  - **Rotation is an owner action, not automated.** If the token is rotated or revoked, the
    GitHub secret is updated by hand. No rotation automation is built; naming it here is what
    keeps "who can redeploy prod" an answerable question rather than an assumed one.
- **Deep-learning justification:** neutral — least-privilege on a deploy credential.
- **Consequences:**
  - The token grants deploy on `pharmfoldmdk` only; a second app would need its own.
  - Stored as the `FLY_API_TOKEN` GitHub Actions secret; referenced by the deploy job, never
    echoed.
  - **Owner action, precondition for the first green deploy:** create the token
    (`fly tokens create deploy -a pharmfoldmdk`) and set it as the `FLY_API_TOKEN` repo secret.
    Until it exists, the deploy step authenticates to nothing — the Builder cannot create it
    (it is a credential), and says so rather than stubbing around it.

---

### DEP-002 — The deploy guard lives on the job, never on the trigger
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)** — forced by D-008; ruled explicitly so the shape is not
  gotten backwards.
- **Context:** `gate.yml`'s own header carries the instruction:
  > *"When real Fly deploy is wired, guard the DEPLOY JOB (not the trigger) against doc-only
  > changes so docs still run tests but don't redeploy."*

  Without a guard, every docs-only PR merged to main would trigger a production deploy. The
  tempting fix — a `paths-ignore` on the workflow — is **the exact thing D-008 removed**, because
  a required status check that does not report on every PR leaves that PR unmergeable forever.
  `test` and `postgres` are both required (D-032); they must run on docs PRs too.
- **Decision — the deploy JOB is conditional on the change not being docs-only; the workflow
  TRIGGER is untouched.** `test` and `postgres` run on every PR and push, as now. The `deploy`
  job additionally checks whether the push changed anything outside `docs/**` and `*.md`, and
  **skips the Fly deploy step when it did not.** Docs still run the full required suite; they
  just do not redeploy.
- **Why this exact split, restated because it is easy to invert:** guarding the *trigger* would
  make the required checks stop reporting on docs PRs → deadlock (D-008). Guarding the *job*
  keeps the checks universal and makes only the *deploy* conditional. The first is a
  reintroduced bug; the second is the fix.
- **Deep-learning justification:** neutral — CI topology.
- **Consequences / test surface:**
  - **Testable, and tested first (project rule):** a docs-only change must not run the deploy
    step; a code change must. The doc-only detection (diff of changed paths against the previous
    main commit, matched against `docs/**` / `*.md`) is the unit under test.
  - The deploy job stays `needs: [test, postgres]` — it cannot run until both required checks are
    green, unchanged from the placeholder.

---

### DEP-001 — What the Fly image contains, and what it must never contain
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)**
- **Context:** The Fly image serves the transport tier. What goes into it is a decision because
  the failure mode of getting it wrong is silent: an image that includes the worker's CUDA stack
  would be multi-gigabyte, slow to build and deploy, and **would still work** — so nothing would
  flag it. D-004 (worker not deployed) and D-018 (the CUDA stack is a separate, unlocked
  dependency world) both bear on it, and neither is self-enforcing in a Dockerfile.
- **Decision — the image contains the runtime tier and nothing GPU:**
  - **Installs `requirements.lock`** — the hash-locked runtime file (D-013), which as of #47
    carries FastAPI/uvicorn/python-multipart. **Not** `requirements-dev.lock`, **not**
    `worker/requirements.txt`.
  - **Copies `app/` and `core/`.** `app/` is the FastAPI transport; `core/` because the `/claim`
    route calls `core.queue.PostgresJobQueue` (verified in `app/main.py`) and the routes import
    the queue/manifest primitives.
  - **Does NOT copy `worker/`** and **does NOT install any `torch`/`transformers` stack.** The
    worker runs on the GPU box (D-004); its `torch==2.11.0+cu128` build is a CUDA dependency world
    D-018 deliberately keeps out of the locked environment.
  - **No Streamlit** — it does not exist yet (verified against the tree). When it is built, this
    entry is amended to add it and its dependency.
- **Why explicit rather than left to whoever writes the `COPY` lines:** the image-bloat failure
  is invisible (it works), and the correct contents are dictated by two prior entries a Dockerfile
  author might not have in view. Ruling it makes the Dockerfile a transcription of a decision
  rather than a judgement call.
- **Deep-learning justification:** indirect — keeping the CUDA stack out of the serving image is
  the deployment face of D-018's separation, which is what makes the runtime environment a
  function of a committed lock file (D-013) rather than of an unpinned GPU toolchain.
- **Consequences / test surface:**
  - **Assertable and tested first:** the built image (or the Dockerfile's install/copy set) must
    contain no `torch` and no `worker/`. A test/CI check that greps the image or the Dockerfile
    for `torch` guards the invisible failure.
  - When Streamlit lands, both this entry and the image change together. *(Now React, per D-033 —
    a build step + static-serve path, a DEP-001 amendment when the UI is built, not before.)*
  - **Builder note (verified against the import graph at `6792c21`, 2026-07-22):** the COPY list
    above is corrected in two ways the ruling did not trace, **both preserving its intent** (no
    CUDA/worker world in the serving image):
    1. **The image also copies `db/`** (the SQLAlchemy ORM models). `app/artifacts.py` imports
       `db.models`; `db/` is serving-tier with no GPU dependency. DEP-001 under-listed it — an
       image of `app/` + `core/` alone would fail at import.
    2. **`FoldSpec` was relocated to `core/contracts.py`.** `app/artifacts.py` imported it from
       `worker/orchestrator.py`, which would have forced `worker/` into the image **against this
       very ruling**. `FoldSpec` is the claim contract — the route produces it, the loop consumes
       it — tier-neutral by nature; it now lives in `core/` and `worker.orchestrator` **re-exports**
       it, so the loop's tests are unchanged (D-031 rule) and the image ships `app/` + `core/` +
       `db/`, no `worker/`. The image-contents test enforces the "no `worker/`, no torch"
       property, so this correction is self-guarding rather than a promise.

---

### D-033 — The serving-tier UI is React, superseding D-004's Streamlit choice
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)**
- **Supersedes:** D-004's *"Serving tier — Fly.io: **Streamlit** + FastAPI…"* — that clause only.
  D-004's two-tier topology, pull-based coupling, and no-inbound-exposure constraints are
  **unchanged and still binding**.
- **Context:** D-004 named Streamlit on 2026-07-19, before the UI's actual requirements existed.
  Those requirements arrived later and are now specific:
  - **D-015 §1a** — disagreement classes must be **visually distinct**; a class-1 and a class-2
    that render identically in a sorted table mean entirely different things and would read the
    same.
  - **D-024** — a coverage line rendered *with* every ranking, held-out and excluded rows
    reachable from it, boundary method visible per target, fold provenance surfaced.
  - **D-028** — per-class **quality tooltips** carrying what each disagreement class can and
    cannot support, inline rather than on a separate methods page; plus feature attribution
    rendered as a statement about the model, never about the target.

  **Nothing is built.** There is no Streamlit dependency and no Streamlit code in the tree
  (verified at `6792c21`). So this supersession costs one entry and no code — which is precisely
  why it is made now rather than after a UI exists.

- **Decision — the serving-tier UI is a React application consuming the FastAPI API.**

  **Why, in terms of what the ruled entries actually require:** every UI commitment above is an
  *interaction* requirement — conditional styling per disagreement class, inline tooltips whose
  content varies by class, drill-down from a coverage line into held-out and excluded rows.
  Streamlit rations exactly that layer: it excels at rapid server-rendered dashboards and
  fights per-element styling and hover state. **The UI is the vehicle for D-028's claim
  discipline; a framework that makes tooltips awkward makes that discipline awkward.**

  **It also fits the architecture better than it did in July.** D-031 built `app/` as FastAPI
  routes — the serving tier is *already* an API. Streamlit would sit beside that API as a second
  Python server rendering server-side; React consumes it as a client. The serving tier becomes
  **FastAPI + a static React bundle**, which is one process serving two things rather than two
  processes.

- **3D visualization — the one real dependency of this switch, resolved not deferred.**
  `ARCHITECTURE.md` and `docs/UI_Plan.md` specify `py3Dmol`/`stmol`, which are Streamlit-bound.
  **`py3Dmol` is a Python wrapper around 3Dmol.js**, so React uses **3Dmol.js directly** and
  every capability the UI Plan lists survives intact: PDB load from path or string, residue
  highlighting and selection, surface/cartoon/stick representations, **colour-by-pLDDT**, pocket
  surface rendering, mutation highlighting. Nothing is lost; a wrapper is removed.

- **The tradeoff, recorded because it is real and was weighed rather than waved past.**
  Streamlit's advantage was **speed to a defensible demo** — a working data app in an afternoon,
  no bundler, no JS toolchain, for a solo builder on a course deadline. That advantage is
  genuine and this entry gives it up. It is given up because the UI is not incidental here: it
  is where D-015 §1a's class distinction, D-024's coverage line, and D-028's tooltips either
  become legible **to a grader** or do not. A UI that renders the ranking correctly but flattens
  the disagreement classes would satisfy the letter of those entries and defeat their purpose.
  **If the deadline later forces a retreat, that is a decision to make explicitly in an entry —
  not by quietly shipping a flatter UI.**

- **Deep-learning justification:** direct, via D-015 §3 and D-028. The scorer's contribution is
  only assessable if a reader can see *which* targets moved, *by how much*, in *which*
  disagreement class, and *what that class supports*. D-024 already ruled that the honest
  reading travels with the result; **this entry is about the surface that makes that possible
  rather than aspirational.** A learned scorer whose output is rendered indistinguishably from a
  heuristic's has had its deep-learning contribution made invisible.

- **Consequences / follow-ups:**
  - **`docs/UI_Plan.md` is now substantially wrong** — it names Streamlit as primary technology
    (§ header and §1) and `py3Dmol`/`stmol` for 3D (§3). It predates D-015, D-024 and D-028 and
    has no coverage or limitations surface at all. **It needs superseding or rewriting**, and
    that is its own task — not folded into this entry.
  - **`ARCHITECTURE.md` needs updating in three places** (the diagram at :63, the component
    table at :105, the serving-tier description at :205, and the roadmap note at :461).
  - **`docs/TDD_v3_ADC_Focused.md:103`** names "Streamlit frontend + FastAPI backend" — same
    correction.
  - **DEP-001 is affected when the UI is built, not before.** The image today ships `app/` +
    `core/` + the runtime lock. A React UI adds a **build step** (bundle) and a **static-serve
    path**, which is a DEP-001 amendment at that time. **Today's deploy is unchanged** — there is
    still no UI to ship.
  - **DEP-004's meaning is unchanged**: a green deploy means the transport API is up and the
    queue accepts work. It did not include a UI before this entry and does not now.
  - **No new runtime Python dependency.** React is a build-time toolchain producing static
    assets; it does not enter `requirements.lock`. The JS toolchain's own pinning is a question
    for the entry that builds the UI, and it is **outside D-013's guarantee** in the same way
    `worker/requirements.txt` is (D-018) — stated now so it is not discovered later.

---

### D-032 — Promoting the Postgres job to a required check: the D-017 bar, met
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)** — criterion 2 confirmed by the Builder against the
  job's run history (see below). The promotion itself is an owner-only repo-settings change
  (D-008) and is the owner's to apply.
- **Context:** D-025 authorized merge-on-green. Its own consequences named the constraint on its
  value: *"merge-on-green is only as strong as the set of required checks, and the Postgres
  integration job is still not one of them… until it is promoted, a migration bug can merge
  green."* Every merge on 2026-07-22 — including `core/enqueue.py` and `worker/orchestrator.py` —
  rode that authorization with the guard advisory.

  **A correction to how this item has been described, recorded because it was repeated all day.**
  Several documents in this session — the pre-work, the close-out draft, and the Planner's
  summaries — called the D-017 promotion bar *"still a vibe, not a number."* **That was wrong.**
  D-017 §"How far" sets an explicit, falsifiable three-part bar:

  1. the job completes on **≥ 5 consecutive PRs** since D-017;
  2. on every one, any red was attributable to a **genuine code/migration fault** and
     **never to service-container infrastructure** (startup timeout, `pg_isready` failure,
     connection-refused);
  3. **any infra-attributable failure resets the count to zero.**

  D-017 even says why the bar is shaped that way: *"the counter measures the thing that matters
  (would 'required' have blocked honest work?), not elapsed time."* **The item was not missing a
  number; nobody had checked the number against the runs.** That is a different failure — and a
  more embarrassing one, since the artefact was in the repo the whole time.

---

- **The bar, checked (D-016 — this is the part that needs an artefact, not an assertion):**

  **Criterion 1 — ≥ 5 consecutive PRs.** D-017 landed at PR #30. Since then: **#31 through #45**,
  fifteen PRs. `paths-ignore` was removed by D-008 precisely so **every** PR triggers the
  workflow, including docs-only ones — so all fifteen are countable, not just the code PRs.
  **Criterion 1 is met roughly threefold.**

  **Criterion 2 — no infra-attributable reds. CONFIRMED by the Builder, 2026-07-22.** This
  criterion cannot be established from the tree: the distinction D-017 draws — a red that was the
  job *doing its work* versus a red from a flaking service container — lives in **GitHub Actions
  run logs, not in the repository.** The Builder pulled the failed step and log for each red
  rather than inferring from branch names, which is the distinction the bar actually turns on.

  **42 runs across #31–#45** (the job's entire history since D-017 added it). **Exactly two
  reds, both genuine faults, zero infra flakes:**

  | Run | Branch | Failed step | Nature |
  |---|---|---|---|
  | 29879472591 | `postgres-integration-job` (D-017) | Postgres integration tests | **code** — caught the env.py transaction bug (a migration silently rolling back) |
  | 29882471328 | `protein-analyses-migration` (D-019) | Apply migrations (`alembic upgrade head`) | **migration** — caught 0002 re-creating an existing index |

  In both, `Initialize containers` succeeded, `pg_isready` health checks ran, and there was no
  startup timeout, connection-refused, or health failure. **The failure was strictly downstream,
  in the migration or test step** — the job doing its work.

  **Criterion 3 — reset on infra flake.** Not triggered; the count is intact.

  **Additional evidence beyond the bar, and it is stronger than the bar itself:** the two reds
  above are not merely *not-flakes* — they are the **two production-grade bugs the close-outs
  credit this job with catching**, now traced to their run IDs rather than recalled. The job also
  confirmed the re-anchored reap boundaries on real PG (#43). **A check that has fired correctly
  twice and falsely zero times in 42 runs is better evidenced than one that has merely been green
  five times.** D-017's bar measures the absence of flakes; this measures the presence of value.
  Both point the same way, which is the comfortable case.

---

- **Decision: add `postgres` to branch protection's required checks, effective BEFORE the
  transport PR.**

  **The timing is the substance of this entry, not a detail.** The alternative — naming a future
  threshold ("promote after N more clean runs") — would mean the transport PR merges first. That
  PR creates `app/`, the first FastAPI route handlers, and is the **largest new
  database-touching surface the project has produced**. It is precisely what the job exists to
  guard. Promoting after it inverts the point of having a guard.

  **What promotion changes:** a red `postgres` job blocks merge, with **no admin bypass**
  (D-008's `enforce_admins`). That is the intended cost. D-017 declined to promote early for a
  specific, still-valid reason — *"a required job with a service container that flakes would
  deadlock every PR with no admin bypass"* — which is exactly why criterion 2 is the one that
  matters and why it is the Builder's to confirm rather than the Planner's to assume.

- **What this does NOT change, stated so promotion is not mistaken for wider coverage:**
  - **The pgvector `extensions`-schema resolution is still unproven.** D-017 says so directly:
    the service image is stock `postgres:16`, there is no vector column, so `search_path`
    → `extensions` is proven only insofar as the SET executes without error. Per
    `docs/HAZARD-search-path-seams.md` this is **seam 2**, and its trigger is unchanged — the
    first `analysis_embeddings` write, downstream of D-027. **A required Postgres job does not
    close it.**
  - **`worker/requirements.txt` remains outside the lock-file guarantee** (D-018, by design;
    `accelerate` unpinned). No CI job reddens on a breaking upstream release there.
  - **`--require-hashes` tamper rejection remains asserted, not demonstrated.**

- **Deep-learning justification:** indirect, and the same shape D-017 gave. The queue dispatches
  every neural inference; a broken migration or a silently-non-atomic claim corrupts the fold
  cache the deliverable is served from, invisibly, under a green SQLite suite. Making the guard
  *required* is what converts D-025's merge-on-green from a throughput convenience into a safe
  one.

- **Consequences / follow-ups:**
  - **Closes the standing constraint D-025 named on itself.** D-025's consequence block should be
    updated to reference this entry rather than leaving the promotion open.
  - **The transport PR (D-031) is held until this lands** — the owner's sequencing, and the point
    of the entry.
  - ~~If criterion 2 fails…~~ **Criterion 2 passed.** Retained as a note on method: the check was
    run against logs with the answer genuinely open, not to ratify a decision already taken. Had
    a red been infra-attributable, the count would have reset per D-017 (3) and this entry would
    have become a dated record of a bar checked and not met.
  - **The image switches to `pgvector/pgvector:pg16`** when the first vector-column migration
    lands (D-017). That is a change to a *required* check and therefore must be proven
    RED→GREEN per D-008, not merged on the strength of a passing run (D-025).

---

### D-031 — The Fly transport: HTTP realization of the loop's discovered protocol
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)**
- **Context:** D-030 ruled the topology and deliberately deferred the transport, sequencing the
  loop first so the protocol would be *discovered by construction* rather than designed in the
  abstract. That worked: `worker/orchestrator.py` is built and green against an injected client,
  and the interface it needed is now known rather than imagined.

  **The contract the loop defined, reported untidied by the Builder:**
  - `claim()` → job **with the fold spec inline** (sequence, slice coords, tier params) or `None`
  - `upload(job, artifacts)` → returns nothing; **must be idempotent**
  - `complete(job)` / `fail(job, err)` — separate calls, *mergeable with upload* (flagged)
  - `TransportError` is the retry signal
  - **no `renew`** — the heartbeat D-030 flagged does not exist yet
  - route handlers **inherit the seam-1 obligation** (`docs/HAZARD-search-path-seams.md`)

  This entry rules the HTTP realization of exactly that. **It adds no capability the loop did
  not ask for.**

---

- **Decision — four routes, one auth scheme, one idempotency rule:**

  | Route | Method | Body | Returns |
  |---|---|---|---|
  | `/jobs/claim` | POST | `{worker_id}` | job + fold spec, or 204 |
  | `/jobs/{id}/artifacts` | POST | multipart: pdb, plddt, pae?, provenance | 204 |
  | `/jobs/{id}/complete` | POST | — | 204 |
  | `/jobs/{id}/fail` | POST | `{error}` | 204 |

  **(1) Claim carries the fold spec inline, as the loop requires.** The worker never queries for
  its input. This preserves D-026's guarantee that the job is self-contained against UniProt
  changing: the sequence the worker folds is the sequence the manifest reviewed, delivered with
  the claim. The route delegates to `PostgresJobQueue.claim()` — **FIFO and `SKIP LOCKED`
  atomicity are the primitive's, unchanged, and D-017's proof stands** (D-030 §1).

  **(2) Artifact upload is idempotent, as the loop requires.** A retried upload after a
  transport failure must not duplicate or corrupt. Idempotency key is the job id: **re-uploading
  overwrites** rather than appending or erroring, because the worker cannot distinguish "upload
  failed" from "upload succeeded but the response was lost," and the safe reading of an
  ambiguous failure is to retry.

  **(3) Upload and complete stay SEPARATE — this entry rules against merging them.**
  The Builder flagged them as mergeable. They should not be merged, for a reason D-030 §3
  already ruled and merging would quietly reverse: **status flips server-side only after
  artifacts are persisted.** A single call that accepts artifacts *and* flips status makes the
  ordering an implementation detail of one handler rather than a property of the protocol —
  and the forbidden state (a `complete` job with no structure behind it) becomes reachable by a
  handler bug rather than by protocol violation. Two calls make the ordering **externally
  observable and testable**. The extra round-trip is cheap against a fold measured in minutes.

  **(4) Authentication: a single shared bearer token, worker→Fly only.**
  D-004's requirement is no inbound exposure of the home machine; the Fly tier is already public.
  A shared secret in the `Authorization` header is sufficient at **single-worker scale (D-004)**
  and is the smallest thing that works. **`worker_id` is a label, not a credential** — it
  identifies which worker holds a lease, and D-030 already flagged that under HTTP it drifts
  toward being an auth concern. **This entry keeps them separate deliberately**: the token
  authenticates, the id labels. The shared bearer token is **RULED
  TERMINAL (2026-07-22), not a placeholder** — sufficient by design at single-worker scale
  (D-004), not an interim step toward something more. **Reopening conditions, named:** a second
  worker, or any need to attribute or revoke access per-worker, reopens this as its own entry;
  absent those, the shared token stands.

---

- **RULED (2026-07-22) — PAE is compressed (worker-side gzip) and stored; not discarded, not
  uploaded raw.** `worker/runner.py:200` emits PAE for **every** fold — `esmfold_v1` always
  returns `predicted_aligned_error`; `dtype`/`chunk_size` do not gate it (verified by the Builder
  against `main`) — so what to do with PAE was a ruling to make, not an outcome the model would
  spare us.

  Raw, a 2213 aa PAE is L×L ≈ 4.9M floats ≈ **75–100 MB of JSON**, which over a residential
  uplink is plausibly 30–80 minutes on its own and could exceed the 3600 s provisional lease
  (D-030) *before the fold is even counted*. A larger body limit does not fix that; **gzip
  does** — gzip on float-heavy JSON typically achieves 5–10×, putting a 75–100 MB PAE at roughly
  **10–20 MB — an estimate, not a measurement**. The actual ratio is observed on the first large
  fold, the same measurement that makes D-030's threshold interpretable. At that size the upload
  is a few minutes, inside the lease. So the **worker compresses** PAE and the **endpoint stores the compressed bytes**
  (the compression is client-side work, not a route concern).

  **Store rather than discard:** nothing consumes PAE today (see the Builder note), so discard
  was viable and free — but D-027 deferred-not-dismissed a PAE-derived feature, and recovering a
  discarded PAE means a **paid re-fold** of the cohort. Compress-and-store buys that optionality
  cheaply. This also **settles what was upstream of D-030's threshold measurement:** a large-
  target upload is now bounded (~compressed PAE), so claim-stamp → upload-complete is
  interpretable.

  > **Builder note (verified against `main`, 2026-07-22): nothing downstream consumes PAE.** The
  > only references in the tree are the producer (`worker/runner.py`) and a nullable
  > `pae_json_path` column (`db/models.py:100`) that **no code reads**; D-027 rejected the one
  > PAE-derived feature considered. So "discard at the worker" does not merely make the item
  > *nearly* free — it **dissolves** the transfer, the lease interaction, and the compression
  > question at once, because there is no consumer to serve. The residual decision is only
  > whether to preserve PAE against a *future* consumer: D-027 deferred-not-dismissed a PAE
  > feature, and recovering a discarded PAE means a **paid re-fold**, so compress-and-store (PAE
  > gzips well) buys that optionality cheaply. But nothing today needs the bytes on the wire.

- **RULED (2026-07-22) — the upload route writes `protein_analyses`, not only the Volume; both
  in one transaction; provenance projects to columns and the remainder into `meta`.** The Builder
  surfaced this as the one thing the loop's protocol did not settle, and it is forced, not chosen:
  D-026 filled the **pre-fold** half of `protein_analyses` and assigned the **post-fold** half
  (`pdb_path`, `mean_plddt`, `pae_json_path`) to *"the worker."* But D-030 gave the worker **no
  database connection** — it holds only the injected `QueueClient`. So the actor D-026 named
  cannot do the write. The **only** actor with both the artifacts and a DB connection is the
  `/artifacts` route. This entry corrects D-026's assignment: **the upload route writes the
  post-fold columns.** `upload(job, artifacts)` was never "persist files"; it was always
  "persist the fold," and the durable record is half of that.

  **(a) One transaction spanning a non-transactional filesystem, with a defined ordering and a
  compensating delete.** The route touches two stores — a Fly Volume (files) and Postgres (the
  row) — and a partial write is the failure to design against: a DB row whose `pdb_path` names a
  file that was never written, or files on the Volume that no analysis points at. Neither is
  acceptable, so the ordering is fixed and the endpoint compensates:
  1. **Write the Volume files first**, to `{ARTIFACT_ROOT}/{job_id}/` (`structure.pdb`,
     `plddt.json`, `pae.json.gz` if present, `provenance.json`).
  2. **Then** update `protein_analyses` in a single DB transaction that stamps the paths.
  3. **If the file write fails, the DB is never touched** — no orphaned row (the pre-fold columns
     stay as enqueue left them, post-fold columns stay `NULL`).
  4. **If the DB transaction fails, the written files are deleted** before the error propagates —
     no orphaned files. The Volume is not transactional, so the route makes it *look* transactional
     by compensating; this is the honest bound, not a true 2-phase commit, and single-writer scale
     (D-004) is why the simple compensation is sufficient.
  The worker's retry (D-030 §4) then re-drives the whole `upload`, which is why **idempotency
  (§(2)) and this boundary are the same guarantee seen from two sides**: a retried upload
  re-writes the same paths and re-stamps the same row, converging, never duplicating.

  **(b) Provenance projection — columns where they exist, the whole record into `meta`, nothing
  dropped.** `FoldProvenance` (`worker/runner.py`) carries more than `protein_analyses` has
  columns for. The projection:
  - `mean_plddt` → the `mean_plddt` column (0–100 scale, already rescaled at fold time);
  - the `structure.pdb` Volume path → `pdb_path`;
  - the `pae.json.gz` Volume path → `pae_json_path` (**`NULL` when the fold emitted no PAE** — the
    column is nullable and stays honest about absence);
  - `structure_source` → `"esmfold"` (this structure came from our ESMFold runner, as opposed to
    `alphafold_db` or `user_upload` — the compute *tier* is not this column's job; it already
    lives in the job's `inference_settings` and in the provenance record);
  - **the full provenance dict → `meta["fold_provenance"]`**, so `ca_atom_count`, `truncated`,
    `original_length`, `input_length`, `dtype`, `chunk_size`, `folded_at`, and the ECD bounds are
    preserved verbatim — the §1a truncation/sanity flags (D-015) must survive to be queryable, and
    a column-only projection would silently drop them.

  **(c) `/complete` enforces the ordering against this write, server-side.** §(3) ruled upload and
  complete stay separate so the ordering is *externally observable*; this makes it observable
  concretely: **`/complete` rejects (HTTP 409) unless the job's analysis has `pdb_path IS NOT
  NULL`** — i.e. unless the upload's DB transaction actually committed. The forbidden state (a
  `complete` job with no structure behind it, D-030 §3) is now unreachable by a client that calls
  the routes out of order, not merely by a well-behaved loop. This is the concrete test behind
  §"Ordering is protocol-observable."

- **⚠ The route handlers are new application code touching the database — seam 1 applies
  again.** D-026's real-Postgres test closed the commit/rollback seam for the *enqueue* entry
  point. **The route handlers are a different entry point and inherit the obligation to prove it
  for themselves** — a write through a handler, re-read on a **fresh connection**. Per
  `docs/HAZARD-search-path-seams.md`, this is seam 1 only: no route here touches a vector
  column, so **seam 2 remains open with its trigger unchanged** (the first
  `analysis_embeddings` write, downstream of D-027).

- **No `renew` route.** D-030 ruled the heartbeat as a later entry; adding the route now would
  be building against an unruled design. When the heartbeat is ruled, it lands as a fifth route
  and the loop gains a renewal call — **not as a widening of `complete`.**

---

- **Test surface, written before the transport (project rule):**
  - **The loop's tests do not change.** If wiring the real client requires editing
    `worker/orchestrator.py`'s tests, the client does not implement the protocol the loop
    defined — that is the signal, and the client is wrong, not the tests.
  - **Idempotent upload** — the same artifacts posted twice leaves one set of files and no error.
  - **Ordering is protocol-observable** — a test posting `complete` for a job with no artifacts
    persisted **fails at the endpoint**, not merely in the loop. This is what makes §(3)'s
    separation load-bearing rather than stylistic.
  - **Auth** — an unauthenticated or wrong-token request is rejected on every route, asserted
    per route rather than once, so a route added later cannot silently inherit no check.
  - **Seam 1 for handlers** — a write through a real handler, re-read on a fresh connection,
    against real Postgres. **Marked `pytest.mark.postgres`; it cannot be hermetic** — SQLite has
    no schemas, so a hermetic version would pass and prove nothing.
  - **`TransportError` mapping** — non-2xx and connection failures both surface as the loop's
    retry signal, so the loop's already-proven failure taxonomy (D-030 §4) keeps working
    unchanged across the real transport.
  - **Claim returns the fold spec inline**, asserted explicitly — a route that returned a bare
    job id would compile and would silently reintroduce the worker-fetches-input design that
    D-026 ruled against.
  - **Transaction boundary (ruled above)** — a failed Volume write leaves the post-fold columns
    `NULL` (no orphaned row); a failed DB transaction leaves no files on the Volume (the
    compensating delete ran). Both directions asserted, hermetically, on the `persist_fold` seam.
  - **Provenance projection (ruled above)** — after an upload the columns hold what they should
    (`mean_plddt`, `pdb_path`, `pae_json_path`) and `meta["fold_provenance"]` holds the full
    record, so the §1a truncation/sanity flags are provably not dropped.

- **Deep-learning justification:** indirect and structural, same as D-030. This is the last
  component between a reviewable manifest and executed inference; its correctness is what makes
  fold provenance trustworthy downstream. A job marked complete with no structure behind it
  corrupts the coverage line (D-024) and the extractor's inputs (D-027) at once, and neither
  would show as an error — only as a target that quietly has no data.

- **Consequences / follow-ups:**
  - **`app/` is created by this entry** — the first application code on Fly. It is also the
    first component the `search_path` seam applies to *as a service* rather than as a script.
  - **D-026's post-fold assignment is corrected here (ruled above):** it named "the worker" as
    the writer of the post-fold columns before D-030 removed the worker's DB connection. The
    upload route is the writer. No change to D-026's pre-fold work; only the unreachable
    assignment is superseded.
  - **First web-framework dependency (D-013 change).** `app/` needs FastAPI; `requirements.txt`
    gains `fastapi` + `uvicorn` + `python-multipart` and `requirements-dev.txt` gains `httpx`
    (the `TestClient` transport, also the worker client's HTTP library). The hash-locked
    `requirements.lock` / `requirements-dev.lock` are regenerated with `uv pip compile
    --generate-hashes` and the addition is proven RED→GREEN per D-013 — the transport tests do
    not import before the lock carries FastAPI, and do after.
  - **PAE is compressed and stored (ruled above)** — settled before the first large rental fold,
    which also unblocks D-030's threshold measurement (a large-target upload is now bounded to a
    compressed PAE, so claim-stamp → upload-complete becomes interpretable).
  - **Per-worker credentials** when a second worker exists.
  - **Lease heartbeat** (D-030's flag) lands as a fifth route, not by widening an existing one.
  - **Nothing here is deployed to Fly until the full suite passes**, functional and user tests
    both.

---

### D-030 — The worker's job-pull orchestration: HTTP transport over the proven claim primitive
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)** — topology ruled; the pure orchestration loop is built
  here against an injected protocol; the concrete HTTP client + Fly endpoint API is deferred to
  D-031 (see §Consequences). The stale-threshold open item is ruled below: **raised
  provisionally**, not left unexamined.
- **Context:** D-026 built the enqueue and explicitly deferred what consumes it: *"the worker's
  job-pull orchestration (claim → the input is already stored → fold → upload) is the next
  build; D-004's pull contract governs it."* This entry rules it and re-opens nothing.

  Two facts read as a contradiction and are not one. `PostgresJobQueue.claim()` takes a
  **SQLAlchemy engine** and runs `UPDATE jobs … WHERE id = (SELECT … FOR UPDATE SKIP LOCKED
  LIMIT 1)`; D-004 specifies the worker **polls Fly over authenticated outbound HTTPS**, with
  *"no inbound exposure of the home machine; no tunnel required."* **Different layers:** the
  first is the atomic claim *primitive*, the second the *transport* by which a worker reaches
  it. A direct worker→Fly-Postgres connection would need the DB exposed or a tunnel — both
  rejected in that same D-004 sentence.

  **Ground truth on `main` (verified by the Builder):** no `app/` directory exists, and
  `PostgresJobQueue.claim()` is referenced only by `core/queue.py` and the test suite — never a
  worker or a route. The primitive is real and proven (D-017); the HTTP wrapper D-004 implies
  has never been built.
- **Decision — the topology:**

        worker (home GPU box)
          └── authenticated outbound HTTPS ──▶ Fly serving tier (FastAPI)
                                                └── PostgresJobQueue.claim() ──▶ Postgres
                                                └── Fly Volume (artifacts)

  **The engine lives on Fly, never on the worker.** The worker holds no database connection, no
  Volume mount, no inbound port.

  **(1) Claim is an authenticated HTTP call onto the existing SQL — not a re-implementation.**
  The endpoint invokes `PostgresJobQueue.claim(worker_id)` server-side. FIFO ordering (D-009 §1
  Amendment 3) and `SKIP LOCKED` atomicity live entirely in the primitive and are preserved
  unchanged; D-017's proof stays valid because the SQL it proved is the SQL that runs. Any
  future re-implementation of claim logic in the route rather than delegating to the primitive
  invalidates that proof and needs its own entry.

  **(2) Artifact transport is the same channel.** The worker uploads `structure.pdb`,
  `plddt.json`, `pae.json`, `provenance.json` over HTTPS; the endpoint writes the Volume.
  `runner.write_artifacts` keeps writing locally and knowing nothing about the DB (D-018).

  **(3) Done-ordering — the correctness heart.** The worker uploads artifacts, then calls
  complete; the status flip happens **server-side in complete, and only after the upload has
  persisted** — `upload → persist → complete`, never the reverse. A worker that dies between a
  persisted upload and complete leaves a `claimed` job that reaps and re-folds — wasteful but
  safe. The forbidden state is a `complete` job with no structure behind it, which no later
  process can detect as missing. **The loop encodes this by calling complete only after upload is
  confirmed** — the test that inverts it (upload raises ⟹ complete never called) is the guard.

  **(4) Failure taxonomy, split along the transport boundary:**

  | Failure | Handled by | DB state |
  |---|---|---|
  | Transport / connectivity (claim or submit fails) | worker's poll loop retries | none — job stays as it was |
  | Fold failure (deterministic: CUDA OOM, malformed) | worker reports → `fail()` | terminal `failed`, `attempts` untouched (D-009 §1 Amendment 2) |
  | Vanished worker (claimed, then silent) | `reap_stale()` + `MAX_ATTEMPTS`, already built | requeued, or terminal with `REAPED_OUT_REASON` |

  A submit that fails on transport is **retried, not re-folded** — re-uploading is cheap; a
  rental-tier re-fold is *paid*. This requires the submit to be **idempotent server-side**
  (completing an already-complete job is a no-op) — a route-contract obligation carried to D-031.
- **⚠ The stale threshold — RULED: `DEFAULT_STALE_SECONDS` is raised to 3600 (60 min),
  PROVISIONAL.** It was `30*60`, chosen when the implied topology was a worker holding a DB
  connection. Under HTTP the lease clock starts when the endpoint stamps `claimed_at` — before
  the worker has received the response, folded, or uploaded.

  The asymmetry is one-directional: too short requeues live work and pays to fold a rental-tier
  target twice; too long delays recovery from a rare vanish, on a workload that is offline batch
  cache-generation (D-011) and not latency-sensitive. 60 min sits above the worst plausible
  end-to-end for the largest folds (1652–2213 aa plus a large PAE upload over residential
  bandwidth) while the cost of the raise stays negligible.

  Labelled **`PROVISIONAL — unmeasured under HTTP transport`** in the D-023 (iii) manner, retired
  by the named measurement: first end-to-end large-rental fold, claim-stamp → upload-complete.
  This is not a claim about the right number — it is a safe upper bound chosen on the cost
  asymmetry.

  **⚠ The measurement will not settle this, and the entry should not imply it will.** A fixed
  timeout has no correct value once fold durations are long or variable: a timeout large enough
  never to reap a live fold is necessarily large enough to make a genuine vanish slow to recover.
  The two constraints pull opposite ways and no constant satisfies both. The structural fix is a
  lease **heartbeat** — the worker renews `claimed_at` while folding — which decouples "is this
  fold alive" from "how long do we wait before recovering." Flagged for its own entry. The
  provisional 60 min covers immediate safety; it does not make the design correct.
- **⚠ The worker is the first component that spends money.** Every fold dispatched to the rented
  A6000 is billed; a retry bug re-folds NOTCH2 (1652 aa) up to three times on a paid card. The
  failure taxonomy is a cost-control decision as much as a correctness one.
- **Test surface (written before the loop):** the loop is **pure given injected collaborators**
  (a fake queue-client and a fake fold); a successful fold submits a result and never a failure;
  a deterministic fold failure routes to `fail()` and never submits a result; a transport
  failure at claim touches no DB state and is retried by the loop alone; a transport failure at
  submit is retried **without re-folding** (fold called once, submit called more than once); no
  GPU in the suite (`fold` injected, real fold owner-validated on the GPU host as
  `ceiling_probe.py` already is); and the claim seam stays where D-012 §5 put it — a hermetic
  test asserting the route "claims correctly" against SQLite would prove nothing about
  `SKIP LOCKED` and is not written.
- **Deep-learning justification:** this is the component that turns a reviewable manifest into
  executed inference — where *"we run ESMFold ourselves"* (D-003) becomes artifacts on a Volume.
  A job marked complete with no structure behind it would corrupt the coverage line (D-024) and
  the extractor's inputs (D-027) at once, so its correctness properties are what make fold
  provenance trustworthy downstream.
- **Consequences / follow-ups:**
  - **D-031 (the Fly endpoint) is deliberately sequenced AFTER this entry's loop.** The loop is
    transport-agnostic — it operates on a minimal client protocol (`claim() → job|None`,
    `upload(job, artifacts)`, `complete(job)`, `fail(job, err)`) and is fully buildable against
    injected doubles. The protocol the loop defines *by needing it* becomes the route list D-031
    must expose, so D-031 arrives as the HTTP realization of a proven interface rather than a
    design from scratch. **This is the reverse of D-023/D-024's supplier-before-contract
    ordering, and deliberately so:** there the manifest could not know the coverage line's shape
    without a ruling; here the loop discovers its own contract by construction. Auth, worker
    identity, route shape, upload size limits, and the §(4) idempotency obligation are all D-031.
  - **Lease heartbeat — its own entry,** triggered by the threshold measurement or by any
    observed reap of live work, whichever comes first.
  - **`app/` does not exist.** Creating it (the route handlers) is a new entry point that
    inherits the app-runtime `search_path` obligation (`docs/HAZARD-search-path-seams.md`): the
    claim/submit routes touch no vector column, so it is seam 1 again, proven for the route
    handlers on their own real-Postgres test — a D-031 concern.
  - **Worker identity (`worker_id`)** is free-form today; under HTTP it becomes an
    authentication concern, not a label. Flagged, ruled in D-031.
  - **The stale-threshold measurement** is an owner action, gated on the first end-to-end
    rental-tier fold.

---

### D-029 — The approved-ADC reference: openFDA for approval, a reviewed file for antigens, and two freshness dates
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)**
- **Context:** D-015 §2 leaves an item marked **blocking §2's completeness**:

  > **Open, blocking §2's completeness:** the reconciliation of the full approved-ADC target set
  > against the 82 has **not been run**. Group C is currently the three exclusions the authors
  > named; there may be others they did not. A mechanical reconciliation script closes this and
  > must run before the cohort is called final.

  Group C is the sharpest test the project has — targets the baseline pipeline filtered out
  that turned out to be validated. It is currently **three targets the paper itself named**
  (TROP2, HER3, CLDN18.2). Whether there are others the paper did not name is unknown, and
  "unknown" is doing load-bearing work in a claim the project intends to make.

  Closing it requires answering: *which UniProt accessions are targeted by approved ADCs?*
  **That question has no single authoritative source**, and this entry rules how it is answered.

---

- **Finding: the FDA database answers half the question, and the half it answers is not the
  hard half.**

  `https://api.fda.gov/drug/drugsfda.json` — free, no authentication required, updated daily
  Monday–Friday, full bulk download available. Its **five searchable top-level fields** are
  `application_number`, `openfda`, `products`, `sponsor_name`, `submissions`
  (verified 2026-07-22 against openFDA's own field reference).

  **There is no target-antigen field. There is no ADC flag.** Drugs@FDA records that a
  product was approved; it does not record what the molecule binds. So the query the project
  actually needs — accession-level — is **not answerable from FDA data alone**, and no amount
  of query construction changes that. This is a structural property of the dataset, not a gap
  to be worked around.

  **A second, narrower boundary:** Drugs@FDA excludes products regulated by CBER. Most
  oncology ADCs sit with CDER, so the practical impact is small — but it is a stated coverage
  limit, not an assumed-complete list.

  **The secondary literature disagrees with itself, and is stale by construction.** Reviews
  surveyed 2026-07-22 variously report 14 or 15 approved ADCs and describe belantamab
  mafodotin as withdrawn — but it was re-approved in October 2025 in combination, and a
  CD123-directed ADC was approved in May 2026. **Any count taken from a review paper is wrong
  the moment the field moves, and the field has moved twice in the last year.** A single-paper
  source is therefore rejected: it is simpler, but it inherits a cutoff with no way to detect
  that it has passed.

---

- **Decision — a three-part reference, with the seam between the parts stated:**

  **(1) openFDA is the authority for APPROVAL STATUS.** Queried by application number,
  recorded with the query date. Reproducible, citable, and refreshable.

  **(2) A checked-in mapping file is the authority for DRUG → TARGET ANTIGEN → UniProt
  ACCESSION.** Roughly 16 rows. **Each row cites its own source** for the antigen assignment —
  label, primary literature, or reference database — and the file is reviewed by hand.

  **Its smallness is a feature, not an embarrassment.** Sixteen rows can be read in full by a
  reviewer, which is the correct level of scrutiny for a set that determines what counts as a
  Group C finding. A computed mapping at this scale would be less trustworthy, not more.

  **(3) The mapping is NOT FDA-sourced, and the reference must say so wherever it is used.**
  This is the seam. Part (1) is authoritative and dated; part (2) is a reviewed human judgement.
  Presenting them as one "FDA-derived target list" would attribute to the FDA a claim it does
  not make — the same error class as the two `search_path` seams sharing a name
  (`docs/HAZARD-search-path-seams.md`), and as D-024's `tier=rental` needing `tier_reason` so a
  conservative routing could not read as a measured one.

---

- **Detection is automatable; assignment is not. The refresh is built accordingly.**

  A scheduled job queries openFDA and **diffs against the checked-in file**, reporting: new
  approvals absent from the mapping, withdrawals or marketing-status changes, and rows whose
  application number no longer resolves.

  **What it cannot do is extend the mapping** — assigning a target antigen to a new approval is
  a human read every time. So the job's output is *"the mapping is stale, and here is exactly
  which rows are missing,"* which is the useful half:

  > **The failure mode being guarded against is not INCOMPLETE — it is SILENTLY incomplete.**
  > A file with a freshness date and a job that detects drift is a materially different artefact
  > from a file someone compiled once and stopped thinking about. This entry does not claim the
  > list will be complete. It claims its incompleteness will be **dated and detectable.**

- **⚠ The refresh job is ADVISORY and MUST NOT be able to redden the gate.** It runs as a
  separate scheduled workflow that **opens an issue**; it is not a required check and not part
  of the test suite.

  **Rationale, and it is the same argument D-018 made** about `worker/requirements.txt` sitting
  outside the lock-file guarantee: a check that depends on an external service can go red for
  reasons unrelated to any change in this repository. If openFDA is unreachable, rate-limits, or
  renames a field, a gating check would redden the build on a day nobody touched the code —
  which trains everyone to ignore red, and a gate that is routinely ignored is worse than no
  gate. **The gate stays hermetic. Freshness is advisory.**

- **Two dates are surfaced in the UI, never collapsed into one.** They go stale at different
  rates and conflating them would overstate the weaker one:

  | Date | Meaning | Refresh |
  |---|---|---|
  | **Approvals reconciled** | last successful openFDA diff | automated, could be days old |
  | **Antigen mapping reviewed** | last human review of drug → accession | manual, will lag, and is the genuinely incomplete one |

  A single "last updated" stamp would take the automated date and imply it covers the manual
  one. **The mapping's review date is the honest one to show most prominently**, because it
  bounds what the reference can actually support.

---

- **Test surface, written before the script (project rule):**
  - **The reconciliation is pure given a fixture** — the openFDA response and the mapping file
    in, the diff out. **No network in the test suite.** A recorded fixture response is checked
    in; the live query happens only in the scheduled workflow.
  - **A new approval absent from the mapping is DETECTED**, and the diff names it. This is the
    job's entire purpose and it is the test that proves it works.
  - **A stale application number is detected** rather than silently dropped.
  - **Every mapping row has a non-empty source citation** — a row without one fails, so an
    uncited antigen assignment cannot enter the file.
  - **Accessions in the mapping resolve against the cohort** — a Group C candidate is either in
    the 82 or explicitly outside it, never ambiguous.
  - **The two dates are distinct fields** and no code path writes one from the other.

- **Deep-learning justification:** indirect but real. Group C is the project's sharpest
  evaluation instrument — a target the baseline filtered out and the world subsequently
  validated is worth more than any aggregate correlation. **The instrument is only as good as
  the set that defines it**, and D-015 §2 already carries the caveat that three named
  exclusions are *a single instance and not a demonstrated pattern*. This entry is what would
  let that caveat ever be lifted or strengthened by evidence rather than by assertion.

- **Consequences / follow-ups:**
  - **Closes D-015 §2's blocking item** once the reconciliation runs — the cohort cannot be
    called final before it does.
  - **Group C may grow.** If reconciliation finds approved-ADC targets among the 82 that the
    baseline did not name, Group C expands and D-015 §2's single-instance caveat weakens in the
    project's favour. **If it finds none, that is also a result** and must be reported as such
    rather than quietly leaving Group C at three.
  - **RULED (2026-07-22): the mapping file's owner is the project owner; the review cadence is
    diff-triggered with a floor of one review per iteration.** The scheduled openFDA diff is the
    trigger — a detected new approval prompts a review — and even with no trigger, the mapping is
    reviewed at least once per project iteration, so the "antigen mapping reviewed" date cannot
    silently outlive an iteration.
  - **This entry does not rule the antigen sources themselves** — which label, which database,
    which paper per row. That is per-row and belongs in the file's own citations, not here.

---

### D-028 — The system detects and classifies disagreement; it does not explain it
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)**
- **Numbering note:** drafted as D-027, renumbered to D-028 when the Builder claimed D-026 for
  the enqueue step and the feature-set entry moved to D-027.
- **Context:** D-015 §1 asks *which disagreements are checkable against outcomes the world has
  already decided, and which are hypotheses.* D-015 §1a requires disagreement classes to be
  visually distinct. D-024 makes coverage a first-class surface.

  **None of them says what the system may claim about WHY two rankings disagree** — and the
  gap is not neutral. A comparative ranking view showing baseline rank, structural rank, and
  delta invites exactly one question from any reader, grader included: *why?* Left unruled,
  that question gets answered by whatever the UI happens to render next to the delta, and
  the most natural thing to render is the feature that moved most. **That would be a causal
  claim the system cannot support.**

  D-027's six features are *interpretable* — a disagreement can be attributed to a feature.
  **Attribution is not explanation, and the gap between them is one sentence wide in a UI.**
  *"Feature 6 accounts for most of this target's structural rank"* is a statement about the
  model, and true. *"This target ranks higher because its epitope is more accessible"* is a
  statement about biology, and the system has no standing to make it. The second is what a
  reader will write in their notes after reading the first, unless the interface is explicit
  about which one it is asserting.

- **Decision:** The system's claim is bounded at **detection and classification**.

  **In scope:**
  - **Detect** disagreement between the structural ranking and the comparator's evidence
    score — the delta, the movers, the direction.
  - **Classify** it per D-015 §1a: **class-1** (checkable against decided outcomes) or
    **class-2** (hypothesis on an axis never measured), rendered visually distinct.
  - **Attribute** it to features — which of the six moved this target, and by how much. A
    statement about the model, labelled as such.

  **Explicitly OUT of scope, as a named non-goal:**
  - Any claim about the **biological cause** of a disagreement.
  - Any ranking, scoring, or ordering of disagreements by "interestingness" or "promise" —
    which is an explanation wearing a number.
  - Any generated prose that narrates a disagreement into a mechanism.

  **A non-goal is a commitment, not an omission.** It is recorded here so that a later
  iteration adding explanation does so as a ruled change with its own entry, rather than as a
  feature that arrived because the UI had space for it.

  **This is a scope ruling, not a modesty clause.** The system is *more* defensible for
  stopping here, not less ambitious: a detected, classified, feature-attributed disagreement is
  a claim that can be checked. An explained one cannot be, at this cohort size, on this
  evidence. The boundary is drawn where the artefact's support ends — which is the same
  discipline D-016 applies to documents, applied to the product's output.

- **The quality of each disagreement class travels with the result.** Per owner's ruling, and
  in the same discipline as D-024's coverage line: the honest reading is rendered *with* the
  finding, not on a separate page a reader may not reach. Every disagreement class carries an
  inline explanation of **what that class can and cannot support**:

  | Class | What it supports | What it does not |
  |---|---|---|
  | **Class-1 — checkable** | The comparator's ranking can be tested against an outcome already decided (e.g. an approved ADC target the baseline filtered out). A disagreement here is **evidence about the comparator**. | It is a *single instance*, not a demonstrated pattern (D-015 §2's own caveat about Trop-2). |
  | **Class-2 — hypothesis** | The structural axis orders this target differently. That is a **generated hypothesis**, on an axis no one has measured against outcome. | Nothing about whether the structural ordering is *right*. There is no outcome to check it against. |

  Rendered as inline tooltips or equivalent, not as a footnote or a separate methods page.

- **A third quality note is required, and it is the one most likely to be omitted: structure
  and sequence disagree for well-understood reasons that have nothing to do with this
  project's question.** Convergent folds, divergent sequences within a family, domain
  shuffling — all produce structure/annotation divergence, and all predate this work by
  decades. A disagreement explicable by known homology relationships is **class-2 with a
  known confound**, and the UI must say so where the disagreement is shown.

  **Why this note specifically:** the headline *"structure and sequence disagree"* invites the
  response *"yes, and?"* — because that is the premise of structural biology, not a result of
  this project. The finding this project can support is narrower and therefore stronger:
  *these particular targets are ordered differently on a structural axis, here is the class of
  that difference, and here is what the class supports.* Without the confound note, the
  system's most eye-catching output is a rediscovery presented as a finding, and a reader who
  knows the field will notice — the same failure mode D-022 avoided by making MUC16's absence
  visible rather than silent.

- **Deep-learning justification:** This entry is about the boundary of the model's claim,
  which is part of understanding the model. D-015 §3 pre-registered two negative results
  precisely so the project could report a null honestly; D-027 does the same work one level
  up, by preventing the *presentation layer* from upgrading a detected difference into an
  explained one. A system that says "these disagree, here is the class, here is what the
  class supports" is making a defensible claim. One that says "these disagree because…" is
  making an indefensible one with the same data.

- **Consequences / follow-ups:**
  - **The UI Plan needs this**, alongside D-024's coverage surface. Both are Iteration-1
    scope; neither is in `docs/UI_Plan.md`, which predates both.
  - **A future "analyse disagreement" affordance is anticipated and deliberately deferred.**
    The owner's framing: an LLM with domain grounding could *suggest* why a disagreement
    exists and what axes of investigation it opens. **That is a different system making a
    different kind of claim**, and it needs: its own entry, a clear visual separation from
    the structural result, and explicit labelling as generated suggestion rather than
    finding. Recorded now so that when it is built it is built as a ruled addition — and so
    that its absence in this version is a **decision**, not an oversight.
  - **This entry constrains D-027's attribution output.** Feature attribution is in scope and
    must be rendered as a statement about the model ("feature 6 accounts for most of this
    target's structural rank"), never as a statement about the target ("this target has a
    more accessible epitope").

---

### D-027 — The scorer's feature set, fixed before fitting; and the extractor that computes it
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)**
- **Numbering note:** drafted as D-026, renumbered to D-027 when the Builder claimed D-026 for
  the enqueue step. Recorded because a renumbered entry is otherwise indistinguishable from a
  misfiled one.
- **Context:** D-015 §3 ruled the scorer — *a learned model over structure-derived features,
  fit against Group B* — and named four features: **pocket geometry, surface accessibility,
  epitope-region pLDDT, ECD size/shape**. It then imposed a pre-registration condition it did
  not itself discharge:

  > **Feature count fixed before fitting**, and recorded in this entry when chosen. Growing the
  > feature set after seeing results is how 22 positives get overfit.

  That count has never been recorded. Until it is, the pre-registration is incomplete and any
  fit is unfalsifiable in the specific way D-015 §3 was written to prevent — because "we used
  the structural features" can absorb any number of additions after the fact.

  `docs/TDD_v3_ADC_Focused.md` **predates D-015 and does not specify feature computation.** It
  names `adc_suitability_score` and `surface_accessibility_notes` as schema fields and
  describes pocket identification as a product capability, but contains no method. So this is
  open, not a restatement.

  **Provenance of this entry's scope (D-016).** Before drafting, the Planner proposed an
  alternative framing — a composite structural axis with the ranking target left open — over
  several exchanges. **That framing contradicted D-015 §3, which had already ruled the scorer,
  named the four features, and pre-registered the evaluation.** The error was inferring what
  the log was building toward rather than reading what it says; it is the same class as the
  three errors recorded in `docs/PREWORK-2026-07-22.md`, and the only one that a single
  existing entry would have prevented outright. Recorded here because this entry's *narrowness*
  is the finding: **the open question was never "what should the scorer rank by," it was only
  "how many features, computed how."**

  **What the fold actually yields** (`worker/runner.py`, `FoldResult` / `write_artifacts`):
  `structure.pdb`, per-residue `plddt` (0–100, rescaled), and `pae` when the model returns it.
  Every feature below must be computable from those three artefacts plus the D-023 manifest
  row. **A feature that needs anything else is out of scope for this entry**, because it would
  need a data source the project has not ruled.

---

- **Decision — the feature set is SIX features, fixed as of this entry:**

  | # | Feature | Computed from | Which D-015 §3 name it discharges |
  |---|---|---|---|
  | 1 | **ECD length** (residues folded) | manifest row | ECD size/shape |
  | 2 | **Radius of gyration**, normalised by length | `structure.pdb` CA coords | ECD size/shape |
  | 3 | **Mean pLDDT over the folded ECD** | `plddt.json` | epitope-region pLDDT |
  | 4 | **Membrane-proximal pLDDT** — mean over the C-terminal 25% of the ECD | `plddt.json` + manifest boundary | epitope-region pLDDT |
  | 5 | **Solvent-accessible surface area**, normalised by length | `structure.pdb` | surface accessibility |
  | 6 | **Largest contiguous accessible surface patch**, as a fraction of total SASA | `structure.pdb` | pocket geometry + surface accessibility |

  **Six, and the count is now fixed.** Adding a seventh after any fit has been run
  invalidates the pre-registration and must be recorded as such in a new entry — not folded
  in silently.

- **Why six, argued rather than asserted.** Group B is 22 positives. Six features is ~3.7
  positives per feature, which is already generous and is the upper end of what this labelled
  set supports. Fewer would be defensible; more would not. **The number is a judgement, not a
  derivation** — there is no threshold that makes six correct and seven wrong. What makes it
  binding is that it is fixed *now*, before any result exists to be tempted by, which is
  precisely the condition D-015 §3 imposed and did not discharge. The four D-015 names
  map to six computed quantities because two of them (ECD size/shape, epitope-region pLDDT)
  are each naturally two numbers — a size and a shape, a global and a regional pLDDT — and
  collapsing either pair would discard the distinction that makes it informative.

- **Why these and not a learned embedding.** Ruled in D-015 §3 and restated here because it
  is the entry's load-bearing constraint: *interpretability is what lets a disagreement be
  attributed to a feature rather than shrugged at.* An embedding-distance model could rank
  well and would leave every disagreement unexplainable, which would make D-015 §1's actual
  research question unanswerable.

- **Two features that were considered and REJECTED, recorded so they are not quietly added
  later:**
  - **Predicted pocket volume via a pocket-detection algorithm** (fpocket-style). Rejected for
    this iteration: it introduces a third-party tool with its own parameters and failure
    modes, and feature 6 captures the ADC-relevant part (is there a large contiguous surface
    an antibody can reach) without it. *An antibody binds a surface patch, not a cavity* —
    small-molecule pocket detection is answering a different question.
  - **PAE-derived domain-boundary confidence.** Genuinely informative, and `pae` is already
    persisted — but it is not returned by every model path (`runner.py` guards it as
    optional), so a feature depending on it would be **absent for some targets and present
    for others**, which is a coverage problem D-024 would then have to express. Deferred, not
    dismissed.

---

- **The extractor's contract:**

  **Pure given `(structure.pdb, plddt, manifest_row)`.** No network, no GPU, no database. This
  is deliberate and matches the D-023 manifest's design: it makes the extractor **fully
  fixture-testable**, which for a component that feeds a 22-positive fit is not a convenience
  but a correctness requirement.

  **Output:** one row per target — six named floats, plus the `target_id`, the fold's
  provenance hash, and an explicit `feature_version`. The version exists so that a refit
  against changed feature code is detectable rather than silent.

  **Failure is explicit, never imputed.** If a feature cannot be computed for a target (a
  malformed PDB, a zero-length span), the row records `null` **with a reason**, in the same
  discipline as D-024's `tier_reason`. **Imputing a mean would be the worst available
  option** — it manufactures a plausible number for a target we failed on, and the fit would
  never know.

- **Test surface, written before the extractor (project rule):**
  - **Determinism** — the same PDB and pLDDT yield byte-identical features across runs. The
    fit is only reproducible if this holds.
  - **A hand-checkable fixture** — a small synthetic structure with known geometry, so radius
    of gyration and SASA are verified against a computed expectation rather than against
    whatever the code happened to emit first.
  - **Feature count is SIX** — an explicit test asserting the extractor emits exactly six
    features, so the pre-registration is enforced by the gate rather than by memory. **This is
    the test that makes this entry real.**
  - **Null-with-reason, never imputed** — a malformed input produces a null and a reason
    string, and no test fixture anywhere substitutes a mean.
  - **Membrane-proximal region is derived from the manifest boundary**, not from a fixed
    residue count, so a `whole`-method target and a `sliced_ecd` target are not silently
    treated alike.
  - **`feature_version` changes when feature code changes** — pinned by a test over the
    extractor's own source hash, in the D-009 §1 red-on-change manner.

- **Properties the leave-one-out is expected to expose (appended at ruling, 2026-07-22).**
  Named now, before the fit, so a result that reveals them reads as anticipated rather than
  excused after the fact:
  - **The count is a judgement, not a derivation.** Six is ~3.7 positives per feature; the
    leave-one-out will show whether any single feature is load-bearing or whether the set is
    redundant. Neither outcome invalidates the pre-registration — both are informative.
  - **Feature 6 is the fragile one.** The largest-contiguous-accessible-patch fraction depends
    on a SASA threshold and a contiguity definition; it is the feature most sensitive to those
    choices, and the leave-one-out is where that sensitivity should surface.
  - **Features 1 and 2 are collinear.** ECD length and length-normalised radius of gyration are
    geometrically related; expect overlapping signal — dropping one may barely move the fit,
    which is a finding about the feature set, not a failure of it.
  - **Feature 4 is cross-method incomparable.** Membrane-proximal pLDDT means a different thing
    for a `whole`-method target than for a `sliced_ecd` one (D-021); the leave-one-out over the
    held-out whole set may behave differently and must not be read as though comparable.

- **Deep-learning justification:** This entry is what makes D-015 §3's pre-registration
  binding rather than aspirational. A fixed feature count, enforced by a test, is the
  difference between a small-sample fit that can produce a falsifiable negative result and one
  that can absorb any outcome. D-015 §3 named **two** negative results — including the
  non-obvious one, that a strong correlation with the comparator's evidence score is *also*
  null, because it means the features proxy attention-and-precedent rather than structure.
  Neither negative is interpretable if the feature set moved during fitting.

- **Consequences / follow-ups:**
  - **The extractor needs folds**, and folds need the enqueue step and worker. This entry is
    rulable now and buildable only after the pipeline runs end to end. Ruling it now is
    deliberate: the feature count must be fixed **before** any fit, and the cheapest moment to
    fix it is before there is a result to be tempted by.
  - **Feature 4 depends on the boundary method.** For `whole`-method targets (the 13 held out
    per D-024) the "membrane-proximal 25%" is a different thing than for a sliced ECD. Those
    targets are already held out of cross-method ranking claims (D-021), so this is consistent
    — but the extractor must not silently compute it as though it were comparable.
  - **`feature_version` should be persisted alongside `inference_settings`**, so a stored score
    can always be traced to both the fold that produced it and the feature code that read it.
  - **Group C (TROP2, HER3, CLDN18.2) runs through the identical extractor**, with no
    special-casing — otherwise the out-of-cohort probe is not a probe.

---

### D-026 — Enqueue: the manifest becomes protein_analyses + jobs (the pull queue is fed)
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)** — ruled by the Builder; the three forks below decided
  here with justification, not inherited.
- **Context:** D-023's manifest produces a reviewable routing table but writes nothing. D-004's
  pull queue can be *claimed* but has no `enqueue` — the seam is claim/complete/fail/reap_stale
  only. This entry is the step between: turn each foldable manifest row into a `protein_analyses`
  row (WHAT to fold) plus a `jobs` row (a pending unit the local worker claims). It is **the first
  code in the project to write application rows** — which makes it the first exercise of a seam
  named-but-never-run (see Hazard).
- **Decision — who is enqueued.** The 80 targets with disposition `ranked` or `held_out` are
  folded; the 2 `excluded` (MUC16 `Q8WXI7`, FAT2 `Q9NYQ8`) get **no job** (D-022 — they fold on no
  card). **Held-out means held out of the RANKING, not of folding** (D-021/D-024): the 13
  `whole`-method targets are folded — they populate the coverage surface and the single-target
  view — but do not enter cross-method ranking claims.

  **Named as a deliberate spend:** those 13 held-out folds run on rented hardware
  (whole-sequence, mostly rental-tier) and contribute **nothing to the ranking**. That is the
  intended cost of an honest coverage surface and a working single-target view, recorded so it is
  not a surprise on the invoice. If cost ever forces a cut, the held-out folds are the first
  candidates — never the ranked ones.
- **Ruling (2026-07-22), forks decided by the Builder with justification:**

  **(i) The sequence and its UniProt release are fetched and STORED at enqueue — the job is
  self-contained.** Not "store the accession and let the worker fetch at fold time."
  Reproducibility is this project's differentiator, and **UniProt revises sequences**: a worker
  fetching months later could fold a *different molecule* than the manifest reviewed, silently.
  The analysis records the exact residues folded **and the release they came from**, so provenance
  names *which* UniProt. Cost: 80 one-time REST fetches — cheap, and it keeps new network code out
  of the not-yet-built worker orchestration. The fetcher is injected, so tests stay hermetic.

  **(ii) The fold target is the LARGEST extracellular span — inherited, not a fresh choice.**
  `largest_span_aa` is what the whole cohort was bucketed on (D-020) and what every routing and
  coverage decision keys on (D-024). Folding any *other* span would make the routing and the fold
  disagree about what was measured, so this is consistent-by-construction, not a new rule. The
  span folded (`[start,end]`, or `whole`) is **recorded on each row**, so the deferred
  ADC-relevant-span refinement can later identify exactly what changed. Multi-span selection beyond
  "largest" is out of scope here.

  **(iii) One `ranking_runs` row per enqueue; idempotent on (cohort version, accession).** Each
  enqueue mints a `ranking_runs` row stamped with the cohort's `target_list_version` (the
  Kathad-82 revision, D-020). Analyses/jobs are keyed idempotently, so a **second run reports
  "exists" and writes nothing new** — the enqueue is the irreversible step D-023's manifest-first
  guard existed to protect, so re-running it must be safe.
- **`inference_settings` per tier (D-018 / S-003 — recorded, not re-decided):** `local` →
  `int8`/`chunk_size=64`; `rental` → `fp16`/`chunk_size=None`; `MODEL_REVISION` pinned
  (`75a3841…`), `source ∈ {sliced_ecd, whole}`, and the ECD `[start,end]` when sliced. These are
  the reproducibility fields D-004/D-015 §1a require; the worker fills the post-fold half (pLDDT,
  CA count, folded_at).
- **Deep-learning justification:** this is the plumbing that turns a reviewed routing table into
  actual neural-inference work — where "we run ESMFold ourselves" (D-003/D-004) becomes jobs a GPU
  claims. Storing the exact input + release + fold parameters is what makes each fold
  **reproducible and legible to a grader** (D-015/D-016).
- **⚠ HAZARD — the app-runtime `search_path` seam, first exercised here.** env.py's `search_path`
  is proven on real Postgres (D-017); the **app-runtime connection is a different connection and
  has never written a row.** The enqueue is the first to do so. Its writes
  (`protein_analyses`/`jobs`/`ranking_runs`) do **not** reference the `vector` type, so they do not
  by themselves exercise the pgvector `extensions`-schema resolution — that specific seam stays
  unproven until vector-touching app code runs, stated so it is not mistaken for covered. What IS
  newly exercised is the app-runtime **write/commit path on real Postgres**, and it is tested on a
  **real connection, not a mock** (`test_enqueue_commits_on_real_postgres` re-reads on a fresh
  connection — the env.py-bug class: a green insert that silently rolled back).

  **Related, owner's call:** the Postgres integration job is **still not a required check**. Under
  D-025 merge-on-green, a migration bug can merge green — in the session most likely to produce
  one. **This PR writes no migration** (the tables exist, D-019), so it adds no such exposure; but
  the promotion decision remains the owner's, and it is the live constraint on D-025's value.
- **Test surface (written before the code):** 80 enqueued / the 2 excluded get no job; a re-run is
  idempotent (reports "exists", counts unchanged, one `ranking_run`); `inference_settings` is
  tier-correct (int8/64 local, fp16/None rental, revision pinned); slice provenance recorded
  (source + ECD bounds, or whole) and the UniProt release stored; every `jobs.analysis_id` FKs a
  real `protein_analyses` row; and — on a **real** connection — the rows commit.
- **Provenance (D-016).** Ruled against `db/models.py` (the jobs/protein_analyses/ranking_runs
  schema), `worker/runner.py` (`FoldProvenance` fields + `MODEL_REVISION`), `core/manifest.py` (the
  dispositions + slice bounds), and D-004/D-018/D-019/D-020/D-021/D-022/D-024 — read from HEAD.
- **Consequences / follow-ups:**
  - The worker's job-pull orchestration (claim → the input is already stored → fold → upload) is
    the next build; D-004's pull contract governs it.
  - `analysis_embeddings` (the vector path) is written later, by the scorer — that is when the
    app-runtime `search_path` seam finally bites and must be handled.
  - Group C reconciliation and any approved-ADC-list authority are out of scope here (owner-named
    source pending).

---

### D-025 — Merge-on-green authorization, and what it does not authorize
- **Date:** 2026-07-22
- **Status:** Accepted
- **Context:** The Builder (Code) asked whether the standing merge-on-green authorization from
  the JARVIS project carries over to PharmFoldMDK. The question was asked in chat, where an
  answer would have been invisible to every future session. Governance that lives only in a
  conversation is not governance (D-002).
- **Decision:** **Merge on green is authorized.** A PR whose required checks pass may be merged
  without waiting for owner review.
- **What green means here, stated because the phrase is doing real work:** the D-008 gate —
  the full suite, functional and user tests, plus the D-013 hash-locked install. Nothing
  reaches Fly.io that has not passed it first. Merge-on-green is an authorization to *not
  wait*; it is not a lowering of the bar, and it does not make an unproven check sufficient
  merely because it is green.
- **What it does NOT authorize:**
  - **Merging work whose decision entry does not exist.** THE RULE is unchanged: the log leads
    the code. A green PR that implements an unruled decision is still incomplete, and green
    does not substitute for a ruling. D-024's ordering fight this morning is the live example —
    the manifest could have been built green against an unratified contract.
  - **Changes to the gate itself.** Under D-008, a change to the required status check is
    exactly the class of change that gets *proven* RED→GREEN, not merged on the strength of a
    passing run.
  - **Silent scope growth.** A PR that grows beyond its entry needs the entry amended, in the
    same PR (governance rule 2).
- **Deep-learning justification:** neutral — this is a throughput decision. Recorded because
  its *absence* from the log was the defect: the Builder was blocked on an unwritten rule, and
  the next session would have been blocked identically.
- **Consequences:**
  - The **D-017 promotion bar was the live constraint on this entry's value — now CLOSED by
    D-032 (2026-07-22).** Merge-on-green is only as strong as the set of *required* checks, and
    the Postgres integration job was not one of them, so until it was promoted a migration bug
    could merge green. D-032 checked the D-017 bar against the job's actual run history (criterion
    2 confirmed by the Builder, not assumed) and promotes the job to a required check, effective
    before the transport PR — lifting the cap this consequence named on itself. *(The bar was
    never "a vibe without a number": D-017 §"How far" stated it explicitly; it had simply gone
    unchecked. See D-032.)*
  - Two seams remain outside any gate and are unaffected by this entry: the **app-runtime
    `search_path`** (never run) and **`worker/requirements.txt`** (outside the lock-file
    guarantee by design, D-018; `accelerate` unpinned).

### D-024 — Coverage and limitations are a first-class UI surface, not a footnote
- **Date:** 2026-07-21
- **Status:** **Accepted (2026-07-22)** — ruled with a **structured coverage object**: a
  three-cell disposition partition (`ranked` / `held_out` / `excluded`) plus two breakout
  subsets (`unmeasured_tier`, `no_topology`); `untested` routed to **rental with its reason
  recorded** and **ranked, not held out**; SDK1 bucketed but **pinned by a named test**. See
  "Ruling" below, including the §(i) correction of 2026-07-22.
- **Context:** Four separate decisions have now each produced a constraint that **must be
  visible in the interface**, and they have been accumulating as scattered consequences
  rather than as a designed surface:
  - **D-015 §1a** — disagreement classes must be visually distinct; a class-1 (checkable
    against decided outcomes) and a class-2 (hypothesis on an axis never measured) look
    identical in a sorted table and mean entirely different things.
  - **D-021** — *"N ranked, M held out"* travels with **every** ranking, as part of the
    result. A cohort of 82 that quietly becomes 69 invalidates the comparison.
  - **D-022** — named exclusions must be **visible, not silently missing**. MUC16 is CA-125;
    a reviewer who knows the field notices its absence immediately.
  - **D-020 / the ECD measurement** — 16% of the cohort has no sliceable topological domain
    and is folded by a different method.

  Left as consequences of four entries, these will be implemented as caveats if they are
  implemented at all. **They are the honest reading of the result and belong in the same
  screen as the result.**

  There is also a finding here that is genuinely interesting rather than merely
  disqualifying, and it would be lost as an apology: **two targets cannot be folded by this
  method on any hardware that exists.**

- **Decision:** The application carries a **Coverage & Limitations surface** as a designed,
  first-class deliverable — not a disclaimer block. It has two homes:

  **(a) Inline, wherever a ranking is shown.** The coverage line is rendered with the
  ranking itself: *"82 targets · N ranked · M held out (whole-chain method) · K excluded
  (named)."* Held-out and excluded rows are reachable from that line, not hidden. Boundary
  method (`sliced_ecd` / `gpi_predicted` / `whole`) is visible per target, and disagreement
  class is visually distinct per D-015 §1a.

  **(b) A dedicated Limitations page**, written as findings with their reasoning — the
  measured constraints of this approach, discovered rather than assumed.

- **The write-up that makes this worth doing — "What we cannot fold, and what it would
  take":**

  **MUC16 (Q8WXI7, 14,451 aa — CA-125) and FAT2 (Q9NYQ8, 4,030 aa)** cannot be folded as a
  single sequence. This is stated as a **property of the method**, with three routes
  addressed honestly:

  1. **Bigger hardware does not solve it.** ESMFold's memory scales roughly quadratically
     with sequence length. An 80 GB card buys perhaps 1.5× the length over a 48 GB one;
     MUC16 is ~30× the measured local ceiling. **There is no card.** *This is the point most
     readers will assume their way past, so it is stated first.*
  2. **Domain decomposition is the real answer, and may be the more correct method
     anyway.** MUC16 is a tandem-repeat mucin — dominated by ~60 repeats of a ~156-residue
     SEA domain plus a C-terminal membrane-proximal region. Folding the repeat unit once and
     the C-terminal domain separately is arguably **better science** than folding 14,451
     residues as a unit, because the global arrangement of a repeat array is not something
     single-sequence prediction recovers meaningfully. **For ADC purposes the relevant
     epitope region is the membrane-proximal portion** — the part an antibody can reach.
     Decomposition is therefore not a compromise here; it is plausibly the right method,
     deferred for scope rather than rejected on merit (D-022).
  3. **A different predictor changes the claim.** Models with different memory
     characteristics exist, but D-003's graded claim is that **we run ESMFold**, and mixing
     predictors across a cohort breaks the comparability D-021 exists to protect.

  **Why this is a finding and not an apology:** it demonstrates something a purely
  computational reader would miss — that **protein size is a real constraint on
  structure-based screening, and the constraint is biological rather than budgetary.**
  Tandem-repeat mucins are an entire class. CA-125 is the most-used ovarian-cancer biomarker
  in clinical practice, and it lies outside what single-sequence folding can reach. That is a
  genuine limitation of the whole approach, **discovered by measurement rather than
  anticipated** — and for a deep-learning course it is arguably the most instructive item on
  the page: *here is where the method stops working, here is why, and here is what it would
  cost to extend it.*

- **Deep-learning justification:** Direct, in two ways. First, the limits of a model are part
  of understanding the model; a system that reports its own coverage honestly is doing more
  DL-relevant work than one that silently drops what it cannot handle. Second, this surface
  is what makes D-015's claim discipline **enforceable** rather than aspirational — the
  class-1/class-2 distinction and the coverage line are worthless if the interface renders
  them identically.

- **Ruling (2026-07-22):** Ruled against the measured cohort in `data/cohort_82_ecd.csv`, not
  against this entry's own prose. The distribution the ruling is made on — recomputed from the
  CSV, 82 rows, partitioning cleanly:

  | `bucket_by_largest` | n | Meaning |
  |---|---|---|
  | `local` | **40** | largest sliceable span ≤ 440 aa (measured local ceiling, S-004/S-005) |
  | `rental` | **16** | ≥ 630 aa — includes the two named exclusions |
  | `untested` | **13** | in the **(440, 630) aa** band — unmeasured against the **local** ceiling |
  | `unknown` | **13** | 12 no-topology + SDK1 |
  | | **82** | |

  **(i) The coverage line is STRUCTURED, not prose — a THREE-CELL partition plus TWO
  BREAKOUTS.** The drafted line (`82 · N ranked · M held out · K excluded`) is right about the
  partition and wrong to stop there: it cannot express that 13 targets are routed on an
  unmeasured ceiling, or that 13 have no parseable topology. The ruled shape is a structured
  object the UI renders — a string cannot be asserted against an invariant, an object can:

      { denominator:      82,
        # DISPOSITION PARTITION — mutually exclusive, exhaustive, sums to denominator
        ranked:           N,
        held_out:         M,
        excluded:         K,
        # BREAKOUTS — subsets that CUT ACROSS the partition; they do NOT sum into it
        unmeasured_tier:  U,   # routed to rental on an unmeasured local ceiling; these are RANKED
        no_topology:      T }  # no parseable extracellular span; these are HELD OUT

  **The binding invariant is `ranked + held_out + excluded == denominator`, and only that.**
  Measured: **82 = 67 ranked + 13 held out + 2 excluded**, with `unmeasured_tier = 13` (a
  subset of `ranked`) and `no_topology = 13` (a subset of `held_out`). The prose rendering is a
  view of this object, never a separately-maintained sentence.

  **Correction, 2026-07-22, raised by the Builder against the entry rather than around it.**
  This clause first read *"the coverage line has FIVE states… the states sum to the
  denominator,"* listing all five alongside `denominator`. That is **not consistent with
  §(iii) or with test-surface item #7**: if `unmeasured_tier` were a partition cell, the 13
  would not be in `ranked`, which is precisely what §(iii) rules they must be. The error was
  the Planner's — the word *state* was used for two different things (a disposition and a
  reason-flag) in a single object, and an implementer could reasonably have built the strict
  five-cell version and produced a coverage line that silently understates ranked coverage by
  16%. **The distinction being drawn is the one D-024 exists to protect:** *disposition* is
  what a target contributes to a ranking claim; *tier* and *topology* are why it was routed as
  it was. They are orthogonal, per §(iv), and flattening them into one partition re-introduces
  exactly the tier/comparability conflation §(iv) forbids.

  **(ii) The denominator is 82 — and 79/3 was never a competing number.**
  `data/cohort_82_accessions.txt` records *79 clean single-hit + 3 resolved by the primary-match
  rule (ATP2B2/LRRN1/SMO)*. That is **mapping confidence**, not cohort size; both the ECD and
  mapping CSVs carry 82 rows. The 3 primary-match resolutions travel into the manifest as a
  **provenance flag on those rows**, per D-020 — visible, not averaged away.

  **(iii) The 13 `untested` targets route to RENTAL, with the reason recorded in the row.**
  Owner's ruling: completeness over thrift; the rented GPU is available and the 13 are not to
  be excluded. But the manifest **must not render this indistinguishable from a measured
  routing.** The row carries `tier=rental, tier_reason=unmeasured_local_ceiling` — the same
  discipline as D-023 (iii)'s self-labelling `UNMEASURED, conservative` config value, and for
  the same reason: *an unlabelled `rental` looks measured.* `scripts/ecd_lengths.py:46-52`
  deliberately buckets against **both** bounds rather than pretending to a single number
  ("The exact ceiling within (440, 630) is UNMEASURED"); routing these to rental without the
  reason would spend that honesty silently.

  **They are folded by `sliced_ecd` and are therefore RANKED, not held out.** This is the
  correction to the first pass of this ruling, and it matters: *held-out* is a
  **method-comparability** category (D-021), not a tier category. A target folded by the same
  boundary method as the local 40 is comparable to them regardless of which card did the
  arithmetic. Holding out 13 `sliced_ecd` targets would drop real, comparable data points from
  the ranking for no methodological reason — and would understate coverage by 16%.

  **(iv) `held_out` means boundary-method incomparability, and nothing else.** The
  `whole`-method targets are held out of cross-method ranking claims per D-021 §1a. Tier is
  orthogonal: a rental-tier `sliced_ecd` fold is ranked; a local-tier `whole` fold is held out.
  Conflating the two is what produced the error corrected in (iii).

  **(v) SDK1 (`Q7Z5N4`) is bucketed with the no-topology set, and PINNED BY A NAMED TEST.**
  Owner's ruling: bucketed, not given its own state — but not buried either. Its span is
  `None-2009(None)`: **a null start and a null width**, i.e. an extracellular annotation that
  exists but carries no numeric bounds. The hazard is specific and mechanical: it **passes** an
  `n_spans == 0` check and **fails** a `has_numeric_bounds` check, so a natural implementation
  admits it as annotated and then slices on `None`. A test naming `Q7Z5N4` explicitly asserts
  its null-bounds span is never parsed as a boundary — the same shape as
  `test_analysis_id_has_no_fk_yet`, so the case cannot be silently outlived if the bucketing
  is ever revisited.

  **(vi) The inline coverage line ships in Iteration 1. The Limitations page ships in
  Iteration 1 as well.** Owner's ruling. Both homes from the Decision above are Iteration-1
  scope; the page's per-target numbers are populated from the manifest rather than written by
  hand, so it is buildable as soon as the manifest exists.

  **What this ruling deliberately does NOT decide:** the exact local ceiling within
  (440, 630) aa. Routing the 13 to rental makes that measurement *unnecessary for coverage*,
  not *unnecessary*. It remains open and cheap (~535 aa bisection, local hardware, logic
  already unit-tested in `worker/ceiling_probe.py`), and if run, it moves some of the 13 from
  `tier_reason=unmeasured_local_ceiling` to a measured `local` — a cost reduction, not a
  correctness fix. Recorded, not scheduled.

- **Test surface fixed by this ruling** (written before the manifest, per the project rule):
  - **Partition invariant** — every accession has exactly one **disposition**, and
    `ranked + held_out + excluded == 82` (measured: 67 / 13 / 2). Asserted on the disposition
    partition **only**; `unmeasured_tier` and `no_topology` are breakout subsets and must NOT
    be summed into it. A test that adds all five fields and expects 82 encodes the ambiguity
    corrected in §(i) and would force the 13 out of `ranked`.
  - **Breakout containment** — `unmeasured_tier` ⊆ `ranked` and `no_topology` ⊆ `held_out`,
    asserted as set containment rather than count equality, so the relationship survives a
    change in either number.
  - **Source-bucket distribution** — the `bucket_by_largest` tally in `cohort_82_ecd.csv` is
    40 / 16 / 13 / 13. This is the **input** measurement, distinct from the disposition
    partition above; pinned so a change in the CSV reddens rather than silently re-routes.
  - **Named exclusions present, not absent** — MUC16 (`Q8WXI7`) and FAT2 (`Q9NYQ8`) appear as
    **excluded rows with a stated reason**. A test asserting they are *missing* would encode
    the exact bug D-022 exists to prevent.
  - **`tier_reason` is populated for all 13 `untested`→rental rows**, and a bare `rental` with
    no reason is a failure.
  - **GPI subset routes to `whole`, held out** — MSLN (`Q13421`) and GPC1 (`P35052`) route to
    `whole`, **not** `gpi_predicted`, per D-023 (ii)'s deferral. Pinned because an implementer
    reading D-021 first will reach for a method that does not yet exist.
  - **SDK1 (`Q7Z5N4`)** — null-bounds span never parsed as a numeric boundary.
  - **Primary-match provenance** — ATP2B2, LRRN1, SMO carry their D-020 mapping flag.
  - **Ranked ≠ local-tier** — a test asserting the 13 rental-tier `sliced_ecd` targets are in
    `ranked`, so a future refactor cannot quietly re-conflate tier with comparability.

- **Provenance of this ruling (D-016).** Made against `data/cohort_82_ecd.csv`,
  `data/cohort_82_accessions.txt`, `scripts/ecd_lengths.py:46-52`, and
  `worker/ceiling_probe.py`'s docstring — read from the tracked tree at HEAD, not from the
  decision entries' narrative. **Two Planner errors were caught this way while preparing it,
  both of the same class**, and both are recorded in `docs/PREWORK-2026-07-22.md` rather than
  quietly fixed: (1) the borderline set was first taken from D-022's prose (NOTCH2, PTPRZ1,
  LRP6, JAG1) when the CSV shows those are oversize-rental; (2) the corrected 13-target band
  was then attributed to the **A6000** probe when `ecd_lengths.py` shows the (440, 630) bounds
  are the **local** ceiling and `ceiling_probe.py` is measuring a different ceiling for a
  different set. *A decision entry's prose describes a measurement; it is not the measurement.*

- **Consequences / follow-ups:**
  - **The UI Plan (`docs/UI_Plan.md`) predates all of this** and has no limitations surface.
    It needs updating, or superseding, when the application is scoped.
  - **The coverage line must be computed, not hand-written.** It comes from the orchestrator
    manifest (D-023), so it is always current with the actual routing rather than a number
    someone remembered to update.
  - **If decomposition is ever built (D-022), this page changes** — MUC16 moves from
    "cannot" to "folded by decomposition," and the finding becomes a *method extension*
    rather than a limit. Written so that change is an edit, not a rewrite.
  - **Fold provenance belongs on the same surface**: model revision, dtype, `chunk_size`,
    mean pLDDT, boundary method, and whether the sequence was truncated — surfaced from
    `inference_settings` rather than left in JSONB. Per D-015, this is also what makes the
    "we ran this ourselves" claim legible to a reader, including a grader.
  - **Numbers to fill in once the orchestrator manifest exists:** exact ranked / held-out /
    excluded counts. Stated here as pending rather than estimated.

---

### D-023 — The orchestrator: cohort → boundary → tier → job (Accepted)
- **Date:** 2026-07-21
- **Status:** **Accepted (2026-07-21)** — all three choices ruled; the orchestrator emits a
  reviewable manifest first, defers the `gpi_predicted` predictor, and treats the A6000 ceiling
  as config with a self-labelling default. See "Ruling" below.
- **Context:** D-018 split the **runner** (folds one sequence) from the **orchestrator** (selects
  the right sequences, slices them at the right boundaries, routes them to the right tier) on
  correctness-condition grounds. Every input the orchestrator needs now exists: the cohort of
  record (D-020), the three-way boundary methods (D-021), the routing tiers incl. named
  exclusions and the ceiling-as-measurement (D-022), and the queue + `protein_analyses` (D-019).
  This scopes the orchestrator; it is not built until the choices below are ruled.
- **Correctness condition (D-018, restated):** the orchestrator is right iff the *right set* of
  sequences is selected, each sliced at the *right boundary by the right method*, and routed to
  the *right tier* — independently of whether any fold succeeds (that is the runner's condition).
- **Pieces:**
  1. Load the cohort of record (`data/cohort_82_accessions.txt`).
  2. Per target: fetch UniProt (sequence + `Topological domain` features) — reuse
     `scripts/ecd_lengths.py`'s fetch/parse rather than re-derive it.
  3. **Boundary method (D-021, three-way):** an extracellular topological span → `sliced_ecd`;
     the GPI-anchored subset → `gpi_predicted` (**predictor deferred — see choice (ii)**);
     otherwise → `whole`.
  4. **Route to tier (D-020/D-022):** largest sliceable span ≤ 440 → **local**; the named
     oversize (MUC16, FAT2) → **excluded**; between the local ceiling and the A6000 ceiling →
     **rental**; borderline decided by the **A6000 ceiling config** (iii); `whole`/unsliceable →
     folded but **held out of cross-method ranking claims** (D-021's binding constraint).
  5. Emit the result — **choice (i)**.
- **Choices for a ruling:**
  - **(i) Output: a routing MANIFEST first, or enqueue jobs directly?** *Recommend: manifest
    first* — a deterministic, reviewable table (target → method, span, tier, held-out flag,
    exclusion reason) that is **fully testable with UniProt fixtures, no queue/GPU/DB needed**,
    and can be reviewed before a single job is created. A thin enqueue step (into the D-019 queue
    + `protein_analyses`) and the worker↔app pull contract (D-004) are a *separate* build on top.
    The manifest is also where D-021's "N ranked, 13 held out" coverage line is computed.
  - **(ii) The `gpi_predicted` predictor: in scope, or deferred?** *Recommend: deferred* — D-021
    ruled it a separate scoped build (a SignalP/GPI DL component). Until it lands, the orchestrator
    routes the GPI subset (MSLN, GPC1, …) as `whole` (held out of ranking), and **upgrades** them
    to `gpi_predicted` when the predictor exists. This keeps the orchestrator shippable without
    blocking on a new model.
  - **(iii) The A6000 ceiling is config, not hard-coded.** Default conservative until
    `worker/ceiling_probe.py` (D-022, owner-run) measures it; borderline targets route on the
    config value, and the manifest records which ceiling produced the routing.
- **Testing:** the routing/slicing **decision** is pure and deterministic given a UniProt
  response, so it is fixture-tested on the gate — no live UniProt, no GPU, no DB for the manifest
  path. This is the whole payoff of the D-018 split: the orchestrator's correctness surface is
  exactly the part CI can cover.
- **Deferred / depends on:** the A6000 ceiling (probe, owner-run) for exact borderline routing;
  the SignalP/GPI predictor (D-021) for `gpi_predicted`; the worker↔app pull contract (D-004) +
  the enqueue step for the manifest→fold path.
- **Ruling (2026-07-21):**
  - **(i) Manifest first, not direct enqueue.** The orchestrator emits a deterministic routing
    table — target → boundary method, span, tier, held-out flag, exclusion reason — **reviewable
    before anything irreversible happens**. Enqueueing directly means the first sight of the
    routing decisions is when jobs already exist. This is also where D-021's coverage line
    ("N ranked, M held out, 82 minus named exclusions") is computed. The enqueue step + D-004
    pull contract are a separate build on top.
  - **(ii) The `gpi_predicted` predictor is deferred.** Route the GPI subset as `whole`/held-out
    and upgrade once SignalP/GPI is built as its own scoped piece. Blocking the orchestrator on a
    new model would repeat the runner/orchestrator conflation D-018 was written to avoid.
  - **(iii) The A6000 ceiling is config, defaulting conservative and labelled `UNMEASURED,
    conservative` in the config itself — not in a comment.** An unlabelled `2000` looks measured;
    the label must ride in the value a reader sees, so the routing cannot be mistaken for having
    been calibrated against a real fold. The probe (D-022) replaces the label with a measured
    number when it runs.
- **Deep-learning justification:** it is the mechanism that turns the 82 into the folds the D-015
  scorer consumes; its correctness (right boundary method per target, held-out set reported) is
  what keeps the ranking comparing like with like rather than mixing domain slices and whole
  chains.

---

> **D-021 and D-022 are a PAIR, logged together on purpose (D-020's measurement raised both).**
> They interact: decomposition (D-022) and the no-topology boundary rule (D-021) are both "this
> protein needs boundaries UniProt topology does not give us," so a decomposition mechanism, if
> built, would serve both — it supersedes D-022's first-pass exclusions and part of D-021's
> `whole` subset. Scope them together, not sequentially. **Both were ruled Accepted 2026-07-21**
> (see each entry's Ruling). Routing is now defined for every target — `local` / `gpi_predicted` /
> `whole` / rental / **named-excluded** — closing the gap that "route to a tier" assumed every
> target had a tier when MUC16 did not. **Remaining prerequisite before the orchestrator's rental
> routing is exact:** the A6000 single-fold ceiling (D-022), a GPU-host measurement.

### D-022 — Oversize targets: decompose or exclude
- **Date:** 2026-07-21
- **Status:** **Accepted (2026-07-21)** — exclude the definitively-oversize for the first pass,
  **named in this entry**; measure the A6000 ceiling to route the borderline; defer decomposition.
  See "Ruling" below.
- **Context:** D-020 measured the rental bucket (16 targets, largest ECD span ≥ 630 aa) and found
  it **non-uniform**. Two targets exceed single-sequence ESMFold feasibility on **any** card —
  **MUC16 (14 451 aa; CA-125)** and **FAT2 (4 030 aa)** — because the limit is **sequence length,
  not model weights**, so a 48 GB A6000 does not help. Several more sit near the edge
  (NOTCH2 1652, PTPRZ1 1612, LRP6 1351, JAG1 1034). D-011's ~$0.25 rental estimate, scoped to a
  handful of HER2-class targets, does not survive this.
- **Unmeasured prerequisite (same shape as the local ceiling once was):** the **A6000
  single-fold ceiling** is unknown. MUC16/FAT2 are over any plausible ceiling (decide regardless);
  the borderline targets cannot be routed until it is measured.
- **Options:**
  - **(a) Domain decomposition** — fold sub-domains separately. Real work, and it introduces a
    boundary-selection problem of its own (which is also D-021's problem — see the pairing note).
  - **(b) Exclusion** — drop the oversize targets from the folded set. Cheap. **The exclusions
    must be named and reported as coverage** — a cohort of 82 that silently becomes 78 is exactly
    the quiet drift that invalidates a comparison.
- **Recommendation (for a ruling):** for the first ranking pass, **exclude the definitively-
  oversize (MUC16, FAT2), named**, and **measure the A6000 ceiling** to route the borderline ones;
  treat decomposition as a later enhancement rather than a blocker. Coverage is then reported as
  "82 minus the named exclusions," never a silently smaller number.
- **Deep-learning justification:** indirect — this determines which targets have folds at all, and
  therefore which the D-015 scorer can rank; an unnamed exclusion would silently bias the ranking.

#### Ruling (2026-07-21)

**First-pass exclusions, named here so they are visible in the record, not silently missing:**

| Accession | Gene | Largest ECD span | Why excluded (first pass) |
|---|---|---|---|
| `Q8WXI7` | **MUC16** | 14 451 aa | Oversize — unfoldable as one sequence on any card. **This is CA-125, the most-used ovarian-cancer biomarker in clinical practice**; a field reviewer will notice its absence immediately, so it is named "excluded, oversize, first pass" rather than left quietly missing. |
| `Q9NYQ8` | **FAT2** | 4 030 aa | Oversize — beyond single-sequence fold feasibility. |

- **The A6000 single-fold ceiling is measured next** (same shape and method as the local ceiling,
  S-004/S-005; cheap on per-second billing) to route the borderline targets (NOTCH2 1652,
  PTPRZ1 1612, LRP6 1351, JAG1 1034, …). Until it is known, only the two definitely-oversize are
  excluded; the borderline are unrouted, not assumed.
- **Coverage is always reported as "82 minus the named exclusions"** — never a silently smaller
  ranked cohort (this ties to D-021's reporting constraint).
- **Decomposition is deferred, not rejected.** It is real work with its own boundary-selection
  problem, and — per the pairing note — a decomposition mechanism would also subsume part of
  D-021's `whole` subset (the multi-domain giants). So if it is ever built, it is scoped to serve
  **both** D-021 and D-022, and it supersedes both the first-pass exclusions here and the `whole`
  method there.

### D-021 — A second ECD-boundary method for the no-topology targets
- **Date:** 2026-07-21
- **Status:** **Accepted (2026-07-21)** — ruled with a **three-way method distinction** (not the
  two-way lean originally proposed) and a hard reporting constraint. See "Ruling" below.
- **Context:** D-020 measured **13 of 82 (16%)** with no usable extracellular topological-domain
  annotation, so D-009 §2 cannot slice them. At 16% this is a **routine path, not an edge case** —
  D-009 §2's "fold whole sequence + warn" fallback was written for a rarity. The 13 are **not
  homogeneous:**
  - **GPI-anchored ADC targets** — **MSLN** (mesothelin), **GPC1** (glypican-1) — whose ECD is
    essentially the whole mature chain (signal peptide trimmed, GPI-attachment signal removed);
  - **large multi-domain proteins UniProt does not annotate topologically** (IGF2R 2491, TLR3 904);
  - **multi-pass transporters** whose extracellular parts are small loops, not an ADC epitope
    domain (SLC44A3, UGT8);
  - **SDK1** — an extracellular annotation with **no numeric bounds**: neither sliceable nor
    cleanly unsliceable. Named separately so it is not silently bucketed with the others.
- **The stakes (same class as §1a's truncation exclusion):** a fold produced by a *different
  boundary method* is a different **kind of input** — a whole chain rather than a domain. If 16%
  of the cohort's structural features are computed on a different kind of input, **D-015's ranking
  is comparing two things.** Whether that is acceptable, correctable, or grounds for exclusion is
  the decision.
- **Options:**
  - **(a) Predicted boundary** — signal-peptide prediction (SignalP/Phobius) plus TM / GPI-anchor
    prediction (DeepTMHMM/NetGPI) to derive an ECD. For the GPI-anchored subset, mature-chain-
    minus-signal-peptide *is* a legitimate, domain-comparable ECD. Adds a prediction step (more DL,
    its own error), and does not fit the transporters (small loops) or the giants cleanly.
  - **(b) Whole-sequence with a provenance flag** — fold the whole mature chain, `source=whole`
    (the runner already records this), and **exclude from cross-method ranking claims** per §1a.
    Cheap, no new model, but produces folds not comparable to domain slices.
- **Binding requirement whichever is chosen (§1a):** the ranking **must know which boundary method
  produced each fold** (`source ∈ {sliced_ecd, predicted_ecd, whole, …}`), and a cross-method
  comparison must be visibly flagged — the same discipline as truncation exclusion. The runner's
  provenance field is where this is recorded.
- **Recommendation (for a ruling):** treat the 13 as the heterogeneous set they are —
  **predicted-boundary (a) for the GPI-anchored subset** (a real domain-comparable ECD),
  **whole-sequence-flag (b) elsewhere**, all provenance-tagged and held out of cross-method
  ranking claims until validated. This needs a ruling: it introduces a new predictor (a DL
  component, which the Prime Directive welcomes but which is its own work) and a per-fold
  provenance class the scorer must respect.
- **Deep-learning justification:** direct if (a) — a learned signal-peptide/GPI predictor is
  itself load-bearing neural work; and either way this governs whether 16% of the cohort produces
  comparable structural features, which is a precondition for the D-015 ranking meaning anything.

#### Ruling (2026-07-21)

**A three-way method distinction, not two.** The 13 are not one class, and a GPI-anchored ECD is
not a whole-chain fold — it is a **domain slice by a different route** (mature chain after signal-
peptide and GPI-anchor-signal removal), closer to a topology slice than to folding a whole
multi-domain protein. So the boundary **method** each fold used is recorded three ways, not two —
free to record and more informative for §1a:

| `source` | method | comparability |
|---|---|---|
| `sliced_ecd` | UniProt `Topological domain` = Extracellular (D-009 §2) | the reference class |
| `gpi_predicted` | SignalP + GPI-anchor prediction → mature-chain ECD (the GPI subset: MSLN, GPC1, …) | a domain slice; **comparable** to `sliced_ecd`, pending validation |
| `whole` | whole mature chain, no domain boundary available (IGF2R, TLR3, transporters, SDK1) | **not** comparable to a domain slice |

- The GPI-predicted method is its **own** method with its own name — not a variant of "predicted
  boundary." Building the SignalP/GPI predictor is a separate scoped piece (a DL component the
  Prime Directive welcomes).
- **`whole` is the CURRENT method for its subset, not the permanent one.** If domain decomposition
  is ever built (D-022), it likely **supersedes** part of the `whole` subset — the multi-domain
  giants especially. Written as current-not-permanent so that supersession is expected, not a
  reversal.
- SDK1 (extracellular annotation, no numeric bounds) is `whole` for now and flagged as its own
  small case.

**The reporting constraint — the real cost, and it is binding.** Holding `whole` folds out of
cross-method ranking claims means **D-015's ranking runs on a reduced cohort**, and that reduction
is **part of the result, not a footnote.** Wherever a ranking is reported — UI, report, or log —
it states the split explicitly, e.g. *"N ranked, 13 held out (whole-chain method)."* "82 targets"
silently becoming a smaller ranked set is exactly the drift that invalidates a comparison. The
exact N is whatever the GPI-predicted method recovers into the comparable set; it belongs next to
every ranking.

---

### D-020 — The 82-target cohort of record, gene→accession mapping, and the measured ECD distribution
- **Date:** 2026-07-21
- **Status:** Accepted (data provenance + method); the ECD distribution below is measured.
- **Context:** D-015 fixed the cohort (Group A = Kathad et al.'s 82 prioritised targets) and §4
  required measuring the ECD-length distribution before scoping the D-011 rental. The 82 lived
  in a downloaded XLSX; the reproducibility claim (§7) had a hole until the cohort was committed
  and the accessions derived by a recorded method.

- **Data provenance (D-015 §4: pin the version, not just the URL):**
  - **Source:** Kathad et al. 2024, *PLOS ONE* `10.1371/journal.pone.0308604`, **CC-BY**.
    Supplementary **S3**, sheet **`Target_expression_in_normal`** — its unique `Gene name`
    column is exactly **82** symbols. Retrieved **2026-07-21** from the PLOS file endpoint.
  - **Committed as the cohort of record:** `data/cohort_82.txt` (the 82 **gene symbols** — the
    supplementary carries no UniProt accessions), so the cohort no longer lives only in a
    downloaded binary.
  - **The comparator arrived with the cohort.** S3 also carries the `Clinical` / `Preclinical` /
    `Antibody generated` / `Literature evidence` columns — i.e. the evidence-score inputs D-015 §1
    needs as the comparator ranking. It is *obtainable from the same file*, not reconstructed.
    (Computing the 1–5 score from them is a later comparator task, not this entry.)
  - **Mapping:** `scripts/map_genes_to_uniprot.py` (stdlib; reads the committed symbol list) →
    UniProtKB REST search, **reviewed (SwissProt) only, taxon 9606 pinned**, retrieved 2026-07-21.
    Output committed: `data/cohort_82_mapping.csv`, resolved accessions `data/cohort_82_accessions.txt`.

- **Why a programmatic mapping is trusted — and it is NOT because it is automated.** A
  hand-curated list carries the same error rate with none of the flags; the 10-seed's confident
  MUC4 (for CLDN18.2) and PTPRU (for NECTIN4) are the proof. This mapping is trusted **because it
  reports what it cannot resolve.** An unresolved or renamed symbol is a visible flag, never a
  silent guess.
  - **The census runs on all 82, not a sample:** requested symbol in, returned **primary** gene
    out, asserted equal. That comparison — against the gene symbol, not the protein name — is
    exactly what would have caught both seed errors.
  - **Primary-match disambiguation:** a synonym-only hit is a *different gene*, never a
    candidate; among multiple reviewed hits, the one whose primary gene equals the requested
    symbol wins. **0 or ≥2 primary-matches would flag a genuine ambiguity** rather than paper
    over one — that is what makes the rule safe.

- **Result (observed): 79 clean + 3 resolved-by-primary-match = 82; 0 renamed, 0 ambiguous, 0
  absent.** Zero renames means the 2024 paper's symbols are all still current (staleness concern
  retired). The three resolved-from-ambiguity cases are recorded here so a future reader need not
  re-derive that the method worked — the flags are the evidence:

  | Symbol | resolved → (primary match) | discarded (synonym-only, a different gene) |
  |---|---|---|
  | ATP2B2 | `Q01814` | `P23634` (ATP2B4) |
  | LRRN1  | `Q6UXK5` | `O75427` (LRCH4) |
  | SMO    | `Q99835` | `Q9NWM0` (SMOX) |

- **Independently anchored, not just internally consistent.** The mapping was checked against the
  10-seed's already-verified accessions for the Group B symbols present in the 82 — **4/4 exact**
  (`ERBB2`→P04626, `EGFR`→P00533, `CD276`→Q5ZPR3, `NECTIN4`→Q96NY8). Verification against
  known-good values, the census applied to the mapping itself.

- **Cohort observation for the D-015 §2 reconciliation (a HYPOTHESIS, not established):** three
  symbols the 10-seed labelled Group B — **MET, TNFRSF17 (BCMA), FOLR1** — are **not in the 82**.
  TROP2 and FOLR1 absence is expected (TROP2 is a named author omission; FOLR1 is the GPI-anchored
  Group C case). BCMA's absence is **consistent with** the paper's haematopoietic-expression
  exclusion filter (BCMA is a plasma-cell antigen) — *plausible from the filter's presence, not
  verified against the paper's intermediate lists.* Belongs in the §2 approved-vs-82
  reconciliation as a check, not a conclusion. The seed's B-labels were illustrative, not
  authoritative on membership.

#### Measured ECD-length distribution (D-015 §4 — "report the size of the icebreaker, measured")

`scripts/ecd_lengths.py` over the 82 accessions (UniProt `Topological domain` = `Extracellular`,
per D-009 §2), bucketed against the **measured** local ceiling. Backing data:
`data/cohort_82_ecd.csv`.

| Bucket (by largest extracellular span) | n | % |
|---|---|---|
| **local** (≤440 aa) | 40 | 48.8 |
| **untested** (441–629 aa) | 13 | 15.9 |
| **rental** (≥630 aa) | 16 | 19.5 |
| **unsliceable** (no usable extracellular span) | 13 | 15.9 |

Three findings, each reportable in its own right:

1. **The GPI-anchored / no-topology class is a SECOND METHOD, not an edge case: 13 of 82 (16%).**
   FOLR1 established that D-009 §2's `Topological domain` method cannot slice GPI-anchored
   proteins; at 16% of the cohort this is not a fallback to bolt on but a real second boundary
   problem. Composition: **12** have no extracellular topological domain at all — including
   GPI-anchored ADC targets **MSLN** (mesothelin) and **GPC1** (glypican-1), plus proteins UniProt
   simply annotates without topology (IGF2R, TLR3, transporters) — and **1** (SDK1) has an
   extracellular annotation with **no numeric bounds**, unsliceable as measured. *Which of the 12
   are specifically GPI-anchored is a follow-up lookup, not asserted here.*
2. **The rental bucket is not uniform, and D-011's ~$0.25 estimate does not survive.** 16 targets
   exceed the local ceiling, but two — **MUC16** (14 451 aa; CA-125, a real giant mucin, anchor-
   confirmed not a parse artifact) and **FAT2** (4 030 aa) — are **too large to fold as a single
   sequence even on the rented A6000**, and several more (NOTCH2 1652, PTPRZ1 1612, LRP6 1351)
   approach that limit. "Rental" therefore splits again into *foldable-on-rental* vs
   *needs-domain-decomposition-or-exclusion* — a real refinement to D-011's scope, to be scoped
   before renting.
3. **Just under half (40/82, 49%) fold locally** on the 8 GB GPU with the S-003 int8 recipe — so
   the local tier carries the plurality of the cohort, and the expensive/hard remainder is now a
   measured ~35% (untested + rental) plus the 16% that needs a different boundary method.

- **Deep-learning justification:** the cohort is the labelled substrate the D-015 scorer is
  trained and evaluated on; without a provenance-pinned, accession-verified 82 there is nothing to
  fit or rank. The ECD measurement turns the compute requirement for cohort-scale structure
  prediction into an empirical finding (§4), which for an ML course is itself a result.

- **Consequences / follow-ups:** the §2 no-topology count (13) needs a second ECD-boundary rule
  before those targets can be folded (own decision later); the oversize rental targets need a
  decomposition-or-exclude call before the rental is scoped; the evidence-score comparator is
  ready to extract from the same S3 file; the BCMA hypothesis feeds the §2 reconciliation.
  `openpyxl` was used locally to read S3 but is **not** a project dependency — the committed
  `cohort_82.txt` is the reproducible artefact, and the stdlib mapping script reads it.

---

### D-019 — protein_analyses + ranking_runs + FK closure + pgvector: the last unproven point
- **Date:** 2026-07-21
- **Status:** Accepted; implemented in this PR (migration `0002`).
- **Context:** Three deferred obligations converge on exactly this migration: D-009 §1
  Amendment 4 (the `jobs.analysis_id` FK lands *in the migration that creates
  `protein_analyses`*), D-015 §4 (`ranking_runs` + a nullable `protein_analyses.ranking_run_id`
  FK, created in that same migration), and D-017 (pgvector `extensions`-schema resolution — the
  **single remaining unproven point in the system**). This PR discharges all three in one
  migration, because Amendment 4 requires the FK and its target in the same migration.

- **Decisions:**
  - **Scope.** `protein_analyses` (Database Plan §2.2 columns) and `ranking_runs` (D-015 §4:
    `target_list_version`, `scorer_version`, `created_at`) become ORM models — both
    SQLite-creatable, so the `create_all` test path is unaffected. `analysis_embeddings`
    (`embedding vector(384)` + HNSW) is created **in the migration only, as raw SQL** — kept out
    of `Base.metadata` so SQLite `create_all` never sees a Postgres vector type and **no
    `pgvector` Python dependency is added**. `mutations`/`reports` are **deferred** (Iteration
    2/3 children, nothing to do with FK-closure or pgvector).
  - **FK closure (Amendment 4).** `jobs.analysis_id` gains its FK → `protein_analyses(id)`.
    Per the standing "fail on the event" discipline, `test_analysis_id_has_no_fk_yet` was run
    *after* adding the FK and **confirmed to fail specifically on the FK-exists assertion** (not
    a collateral schema error) before being replaced with a positive test asserting the FK is
    present and references `protein_analyses`. Same for the postgres job's `fks == 0` assertion.
  - **A SECOND deferred FK, named not hidden.** `protein_analyses.user_id` is a nullable integer
    with **no FK yet** — `users`/auth is unbuilt, so the FK would have no target. Deferred
    exactly as `analysis_id` was (Amendment 4), and closes in the migration that creates
    `users`. The column matches the plan so it is forward-compatible; only the constraint waits.
  - **pgvector — D-012 §5a's tabled choice, finally made.** Rely on the env.py `search_path`
    seam (already in place): the migration runs `CREATE SCHEMA IF NOT EXISTS extensions;
    CREATE EXTENSION IF NOT EXISTS vector SCHEMA extensions;` then a **bare** `vector(384)`,
    which resolves because `extensions` is on the migration's search_path. Both statements are
    idempotent on prod, where D-014 measured the schema and the v0.8.2 extension already present
    — so this is a no-op there and a create in CI. NOT schema-qualifying every column and NOT
    `ALTER DATABASE` (D-012 §5a's rejected options).
  - **CI image switch.** The `postgres` job moves `postgres:16` → `pgvector/pgvector:pg16` so
    `CREATE EXTENSION vector` succeeds and the pgvector path is exercised **for real** — which
    is what closes the last unproven point rather than merely asserting it closed.

- **Deep-learning justification:** direct on two axes. `analysis_embeddings` is where learned
  embeddings become a load-bearing capability (D-015's semantic axis), and pgvector is what
  makes that a real deliverable rather than a lookup — the exact thing the unmanaged Postgres
  product could not host (D-014). `protein_analyses` is the durable record every fold and score
  attaches to; `ranking_runs` versions the ranking the D-015 scorer produces, so a result can be
  tied to the target-list and scorer that produced it (reproducibility, §7).

- **Consequences:**
  - Migration `0002_protein_analyses`; `ARCHITECTURE.md` §4 updated.
  - **The last unproven point is closed** — the pgvector `extensions` resolution now runs in the
    `postgres` job against a pgvector-enabled Postgres 16.
  - New deferred obligation logged: the `protein_analyses.user_id` FK, closing with `users`.
  - `mutations`/`reports` remain to come; the orchestrator (cohort → UniProt → ECD slice → tier
    route) and the D-015 scorer are the multi-day builds after this. The orchestrator's
    prerequisite — the 82's measured ECD-length distribution + GPI-anchored count (cheap, no GPU)
    — is slotted before/alongside it.

---

### D-018 — PR B is a pure fold-runner: sequence in, structure + provenance out
- **Date:** 2026-07-21
- **Status:** Accepted; scopes PR B. Implements the D-011 cache-generation entry point, narrowed.
- **Context:** PR B was defined (session pre-work) as "the cache-generation entry point:
  host-agnostic, dtype and chunk_size as parameters, local defaults int8/chunk 64" — *before*
  D-015 turned single-target folding into the input to a cohort ranking. That raises the
  question of how much PR B should take on: just fold a sequence, or select/slice/route the
  whole 82-target cohort?

- **Decision: PR B is the pure fold-runner only.** Sequence + parameters in → structure
  artifacts (PDB, pLDDT, PAE) + an `inference_settings`/provenance record out. It does **not**
  select the cohort, query UniProt, choose ECD boundaries, or route to a compute tier — that is
  the *orchestrator*, a later step. It does **not** touch the database — artifacts go to files,
  and the DB wiring lands with the `protein_analyses` migration (see below).

  **Why split runner from orchestrator — the argument is correctness conditions, not tidiness.**
  The two are right about different things and fail in different places:
  - the **runner** is correct iff *a sequence in produces a valid structure out with an accurate
    provenance record*;
  - the **orchestrator** is correct iff *the right set of sequences is selected, sliced at the
    right boundaries, and routed to the right tier* (D-009 §2, D-011).

  Those are separately testable, and welding them means neither can fail cleanly. There is also
  a hard operational reason: the runner is what executes on the **rented A6000 where every minute
  bills** (D-011). That surface must be small, proven, and unable to need cohort data it cannot
  reach from a rental box.

- **Why no `protein_analyses` / no DB (this matters more than it looks).** The pgvector
  `extensions`-schema resolution is the **single remaining unproven point in the system** (D-017).
  The migration that creates `protein_analyses` is already scoped to do four things at once —
  create it, add the deferred `jobs.analysis_id` FK (D-009 §1 Amendment 4), create `ranking_runs`,
  add the nullable `ranking_run_id` FK (D-015 §4) — and it is where that last risk gets exercised.
  Dragging any of it into a standalone runner PR inherits the one remaining risk for **no
  benefit**. Artifacts to files now; paths recorded in the DB when that migration lands.

- **The CUDA manifest is a new, named, ACCEPTED gap — not an oversight.** PR B introduces
  `worker/requirements.txt` (torch, transformers, bitsandbytes, accelerate) — the GPU tier's
  dependencies, which D-013 §4 deliberately kept out of CI. Stated plainly: **the worker's
  dependencies are NOT covered by the lock-file guarantee** (D-013 Amendment A). A breaking
  release there reddens no gate and is discovered at fold time, on a GPU host. That is accepted
  because CI has no GPU and installing a CUDA stack there would be slow, fragile, and pointless.
  But because ARCHITECTURE §7 makes reproducibility a graded expectation, the manifest carries
  **exact pins** measured in the S-003 spike — `torch==2.11.0+cu128`, `transformers==5.14.1`,
  `bitsandbytes==0.49.2` — and the fold records the **model revision**
  (`75a3841ee059df2bf4d56688166c8fb459ddd97a`). Honest hole (D-016): `accelerate` has **no
  measured pin yet** (it was present but unrecorded in the spike venv); it is listed to be pinned
  from the first successful GPU install and the resolved version recorded here.

- **Truncation and slice-provenance are recorded at fold time — a D-015 §1a enforceability
  requirement, not a nicety.** §1a's diagnostics require that a fold on a **truncated** ECD be
  flagged and excluded from ranking claims (a truncated fold is a different molecule), and that
  the ECD boundary be known. The runner cannot know the cohort's intent, but it records what it
  was handed: whether the input was a **sliced ECD** or a **whole sequence** (the GPI-anchored /
  FOLR1 fallback case, D-009 §2), the ECD start/end when sliced, and whether any **length cap**
  truncated the input. If the runner does not capture this at fold time, it cannot be
  reconstructed later and the §1a diagnostic becomes unenforceable.

- **Testing split (the postgres-job pattern again).** The runner's **pure logic** — provenance
  construction, the pLDDT rescale (S-001 gotcha: ESMFold B-factor pLDDT returns on the 0–1 scale
  and must be ×100), length-cap/truncation recording, artifact layout — is unit-tested on the
  normal gate with no GPU (torch imported lazily, inside the fold call, so the module imports
  without it). The **actual fold** is GPU-bound: it cannot run in CI (no GPU runner) and is
  validated on a GPU host by the owner. The int8 recipe is already measured (S-003/S-005); a
  `@pytest.mark.gpu` test marks the boundary and skips without torch+CUDA, exactly as the
  postgres tests skip without a database.

- **Deep-learning justification: this is the neural core itself.** Every other decision has been
  scaffolding around it; PR B is the code that runs ESMFold and emits the structure every
  downstream feature (the D-015 scorer, pockets, embeddings) consumes. The provenance record it
  writes is what lets a later ranking claim be checked — D-016's principle applied at the point
  the numbers are born.

- **Consequences:**
  - New `worker/` package (`worker/runner.py`, `worker/requirements.txt`), first GPU-tier code.
  - `ARCHITECTURE.md` §7 (reproducibility) and §8 (layout) updated in this PR.
  - Deferred, explicitly: cohort selection / UniProt / ECD-boundary slicing / tier routing (the
    orchestrator); the DB wiring and the `protein_analyses`+`ranking_runs` migration; the
    worker↔app pull contract (D-004). Each is its own step.

---

### D-017 — Postgres integration CI job: the seam's other half
- **Date:** 2026-07-21
- **Status:** Accepted; implemented in this PR. Implements the job named as required by D-012 §5
  and D-014, not a new decision about *whether* — a decision about *how* and *how far*.
- **Context:** Since PR A this has been the single largest coverage hole. The `test` job builds
  schema with `create_all` and never runs the Alembic chain, and `FOR UPDATE SKIP LOCKED` is a
  **syntax error** on SQLite (D-012 §3) — so the migration chain and `PostgresJobQueue.claim`'s
  atomicity are provable by nothing in the repo. D-012 §4's seam made that gap *legible*; it did
  not close it. This closes it. (The shape is exactly JARVIS audit H2: a green SQLite suite that
  proved nothing about a fresh Postgres, closed only by a real-Postgres CI job.)
- **Decision:** A `postgres` CI job (`.github/workflows/gate.yml`) runs a **Postgres 16** service
  container (matching prod, D-014), installs the locked deps (D-013), applies migrations with
  `alembic upgrade head` — **the real chain, not `create_all`** — and runs the
  `@pytest.mark.postgres` tests. They prove three things the SQLite suite cannot:
  1. the chain builds the schema on real PG (and env.py's Postgres-only `search_path` SET ran
     without error, or `upgrade` would have failed);
  2. `claim`'s `SELECT … FOR UPDATE SKIP LOCKED` is **atomic** — a row locked in one open
     transaction is *skipped* by a claim on another connection, which takes the next row;
     all-locked yields `None`;
  3. `complete` / `fail` / `reap_stale` (incl. the cap → terminal `[reaped-out]`) behave
     identically on real PG.

  The postgres-marked tests **auto-skip** without a postgresql `DATABASE_URL` (the `pg_engine`
  fixture), so they are inert in the `test` job and run for real only here. `deploy` now
  `needs: [test, postgres]`.

- **How far — required-vs-advisory, decided explicitly (D-016 discipline: name what is *not* yet
  true).** The job runs on every PR and push, but is **not yet a branch-protection required
  check**. Two reasons: branch protection is owner-set (D-008 established it, `enforce_admins`),
  and a *required* job with a service container that flakes would deadlock every PR with no admin
  bypass — the exact hazard D-013 §3 declined pip caching to avoid. Interim gate: `deploy: needs
  postgres`, so a broken migration cannot **deploy** even if a PR merged.

  **Promotion criterion — a specific bar, not a vibe.** The owner adds `postgres` to branch
  protection's required checks once **all** of the following hold, so "stable" is falsifiable:
  1. The job has completed on **≥ 5 consecutive PRs** since this one.
  2. On every one of those, any red was **attributable to a genuine code/migration fault** — the
     job doing its work (like the env.py bug on run one) — and **never to service-container
     infrastructure**: container-startup timeout, `pg_isready` health-check failure, or
     connection-refused. An infra flake is the precise signal that a *required* version would
     have deadlocked a PR with no bypass.
  3. **Any infra-attributable failure resets the count to zero.** One flake in five PRs means
     not yet — the counter measures the thing that matters (would "required" have blocked
     honest work?), not elapsed time.

  Recorded as a recommendation with a bar, not silently done: it is a repo-settings change
  (owner-only, like branch protection itself, D-008) with a real downside if promoted early.

- **Still unexercised, stated not hidden:** the service image is stock `postgres:16`. There is no
  vector column yet, so env.py's `search_path`→`extensions` *resolution* is proven only insofar
  as the SET executes without error — the SET targeting a real populated `extensions` schema, and
  a `vector(384)` actually resolving through it, is exercised when the first vector-column
  migration lands and the image switches to `pgvector/pgvector:pg16`.

- **Deep-learning justification:** Indirect, and the strongest kind available for infrastructure.
  The queue runs every neural inference (D-009 §1); a silently-broken claim (double-dispatch,
  lost job) or a migration that fails on real PG would corrupt the cache the DL deliverable is
  served from, and would do so *invisibly* under a green SQLite suite. This is D-016's provenance
  principle applied to the queue: the claim path now has an artefact — a passing real-Postgres CI
  run — behind the assertion that it works.

- **It earned its keep on its first run.** The job immediately caught a real bug that a green
  SQLite suite could never have: env.py ran the `search_path` SET *before*
  `context.begin_transaction()`, auto-opening a SQLAlchemy-2.0 transaction alembic did not own,
  so `alembic upgrade head` logged "Running upgrade → 0001_create_jobs", exited 0, and the
  CREATE TABLE **silently rolled back** (`relation "jobs" does not exist` at the first test).
  Every production migration would have no-op'd invisibly. Fixed by moving the SET inside
  alembic's committed transaction; the artefact (run `29879472591`) is cited in env.py so it is
  not reintroduced. This is precisely the JARVIS-H2 class of failure the job exists to catch.

- **Consequences:**
  - The D-012 §4 seam is now proven on **both** sides. The unproven surface is no longer "claim
    atomicity" but only the narrower "pgvector type resolution," gated to the vector-column PR.
  - `ARCHITECTURE.md` §5 (deploy gate) updated in this PR.
  - The open-questions "largest coverage hole" item is closed (see below), with the pgvector
    caveat carried forward.

---

### D-016 — The provenance principle: every claim names how it is known
- **Date:** 2026-07-21
- **Status:** Accepted (standing rule)
- **Context:** THE RULE at the top of this file governs **durability** — a decision made in a
  chat window and never written down does not exist. Today exposed a different failure the rule
  did not cover: **every claim that got reversed was already written down.** The record was
  faithful; the record was the problem, because it preserved a claim nobody had checked in a
  form indistinguishable from one that had been. A durable record of an unverified claim is
  *worse* than no record — it reads like evidence.

  Four cases in two days, each a written claim **true as stated and wrong in what it implied**,
  each overturned only by returning to the raw artefact:

  | Written claim | Artefact that overturned it |
  |---|---|
  | `params_all_on_cuda=True` | resident 8116 MiB vs **7043 MiB free** — spilled before folding (S-001) |
  | "217 WHEA events since May" | 213 corrected / **4 fatal** — severity hidden by the total (F-001) |
  | "pgvector isn't enabled" (`pg_extension` → 0 rows) | `pg_available_extensions` → 0 rows: **not on the image at all** (D-014) |
  | placeholder commit SHAs in D-013 §6 | invented to fill a template before the runs existed — caught pre-merge, corrected in `8e177ad` |

  This is the discipline the *Method note* above already gestured at, now made a first-class
  standing rule rather than a lesson buried mid-file. It is also KEEL's proposed 8th principle
  (drafted from this session); the KEEL documents themselves live in the Keel project and are
  updated there separately.

- **Decision:** A **second standing rule**, added beneath THE RULE at the top of this file and
  mirrored as a living-documentation rule in `CLAUDE.md`:

  > **Every claim names how it is known.** Before a number or a status enters the log,
  > ARCHITECTURE, or a PR, name the artefact it came from — the raw log line, the query output,
  > the run URL. If you cannot name it, you are recording a belief, not a finding. A summary is
  > not knowing: prefer the breakdown to the total, and **prefer the query whose answer could
  > disqualify you** (`pg_available_extensions` answers "does it exist?"; `pg_extension` only
  > "is it on?" — a zero from the second cannot tell *absent* from *off*).

- **Deep-learning justification:** Indirect but load-bearing. The graded deliverable rests
  entirely on *measured* claims — `inference_settings` reproducibility (D-004), the int8 fit and
  length-ceiling findings (S-003/S-004/S-005), and the scorer's pre-registered evaluation
  (D-015 §1a/§3). Every one of those is a number that will be trusted later. A fabricated or
  unverified figure in this log corrupts the exact record the DL evaluation is judged against —
  the D-015 §1a diagnostics (rule out "our pipeline is wrong" before any claim) are this
  principle applied to the science. Protecting claim provenance protects the deliverable.

- **Consequences:**
  - Applies as a **standard going forward**, not a retroactive rewrite. Existing entries that
    already cite artefacts (S-00x, D-014, D-013 §6) are the model.
  - `CLAUDE.md` gains a fourth living-documentation rule; the top-of-file RULE block gains its
    second rule. No code change.
  - The KEEL provenance-principle draft and the `KEEL-*-v5` documents are **Keel-project**
    artefacts, deferred to a Keel-focused pass (not migrated into this repo).

---

### D-015 — Research question, target cohort, and the learned scorer
- **Date:** 2026-07-21
- **Status:** Accepted (scope); the scorer's feature set and evaluation are **pre-registered
  below and not yet run**
- **Context:** Until now the project's deliverable was single-target analysis: enter a
  protein, get structure, pockets, an ADC-suitability summary. That satisfies the Prime
  Directive only weakly — ESMFold is the headline, but nothing *uses* its output to produce
  a judgement that could be right or wrong. This entry commits the project to a research
  question with a control, a labelled set, and a falsifiable claim.

  **Prior art was surveyed before scoping, and it is substantial.** This is a settled field,
  not an empty one:
  - **Open Targets Platform** (EMBL-EBI/GSK) scores target–disease associations across 20+
    data sources with a prioritisation layer covering tractability, safety, and expression.
    Free REST API and bulk downloads.
  - **Kathad et al. 2024, PLOS ONE** (`10.1371/journal.pone.0308604`, Lantern Pharma) is the
    closest analogue: an *in silico* ADC-target prioritisation from 20,090 protein-coding
    genes down to **82 prioritised targets**, filtered on HPA v22 membrane annotation,
    critical-normal-tissue exclusion, a quasi-H-score ≥150 tumour-expression cutoff, the
    *in silico* human surfaceome, mRNA/IHC consistency, and haematopoietic-expression
    exclusion. **CC-BY licensed**; the target list and expression matrices are published as
    supplementary files (S2, S3).
  - Consensus ADC target-selection criteria across the literature are stable: high
    tumour-specific surface expression, minimal normal-tissue expression, efficient
    internalisation.

  **The gap this project occupies.** Every scheme above ranks on **expression, mutation,
  genetics, and internalisation**. None ranks on **predicted structural properties of the
  extracellular domain**, because none of them folds anything. That is the axis we add, and
  we add it by running our own ESMFold (D-003) rather than retrieving structures.

  There is a documented problem the structural axis plausibly bears on: clinical activity in
  solid tumours **often does not scale with antigen abundance** — an affinity–efficacy
  disconnect that abundance-based ranking cannot explain by construction. Whether a
  bindable, accessible epitope exists is a candidate explanation. *This is a motivating
  hypothesis, not a claim this project has established.*

---

> **REVISED 2026-07-21 (§1 and §3 replaced).** The original framing treated the Kathad
> result as a *baseline to recover*. It is not ground truth — it is another analysis, with
> stated filters, commercial authorship, and named omissions. Treating it as an oracle would
> make *agreement* the success condition and quietly turn this project into a reimplementation.
> §2, §4, context, and consequences stand as first drafted.

#### §1 — The research question (Accepted)

> **Does an ADC-suitability ranking built on structural features — computed from folds this
> project runs — differ from a ranking built on expression and evidence? Where the two
> disagree, which disagreements are checkable against outcomes the world has already decided,
> and which are hypotheses?**

Note what is *not* asked: whether our ranking matches theirs. **Agreement is not the success
condition and disagreement is not failure.** A structural axis that merely reproduces an
expression-based ranking has added nothing — it would mean structure carries no information
beyond abundance, which is itself a reportable (and surprising) negative result.

**The comparator is a comparator, not an oracle.** Kathad et al.'s 82 prioritised targets and
1–5 evidence scores are a **published, reproducible, independently derived** ranking — which is
exactly what makes them useful. They are not a gold standard:

- The filters are **explicit and consequential**: a quasi-H-score ≥150 cutoff on a 0–300 scale,
  exclusion of anything highly expressed in 13 critical normal tissues, mRNA/IHC consistency.
  The authors themselves record that these filters **excluded TROP2, HER3, and CLDN18.2**.
- The 1–5 evidence score is built from literature, antibody existence, protein family,
  preclinical, and clinical criteria — i.e. it substantially measures *how much attention a
  target has already received*. A popularity-and-precedent score as much as a biology score; a
  target nobody has studied scores low by construction.
- The work is authored by a commercial pharma company using a proprietary platform. Not an
  accusation of bad faith — the method is published in full and CC-BY, which is more than most.
  It is a reason not to treat the output as neutral ground truth.

**Our position is differently biased, not unbiased.** No commercial stake and no prior
commitment to any target is real — but inexperience is not neutrality; it also means not
knowing which failure modes the field has already understood and discarded. The defensible
claim is narrow and sufficient: **we are looking at an axis they did not measure at all.**
Structural accessibility of the extracellular domain appears nowhere in their feature set,
because they folded nothing.

**Two axes, kept orthogonal and never blended into one number:**

| Axis | Measures | Source |
|---|---|---|
| **ADC suitability** | Is this a good ADC target? | Structure-derived features (ours) + expression/evidence comparator |
| **Urgency / unmet need** | Does it matter clinically if it is? | Cancer-type survival, incidence, existing options |

Survival rate is a property of the *cancer*, not the *target*. A highly exploitable thyroid
target and a mediocre pancreatic target should both surface, for different reasons. Collapsing
them destroys the information a researcher needs. Urgency **ranks**; it does not **score**.

---

#### §1a — Disagreement is the expected outcome, and it is pre-registered (Accepted)

**Written before any result exists**, per the log's method note: *name the outcome that would
overturn the favoured hypothesis, and state a check precisely enough that its inadequacy is
discoverable.*

If our ranking disagrees with the comparator, there are exactly **three** explanations. They
are not equally likely, and they are not equally interesting. **The honest prior for a first
implementation is that (3) is most probable for any given disagreement.** A disagreement
claimed without ruling out (3) is worthless.

| # | Explanation | Checkable against | Status of a claim |
|---|---|---|---|
| **1** | **Their pipeline has a blind spot we can see.** A target their filters excluded or scored low that the world has since validated. | **Outcomes already decided** — approved ADCs, trials that succeeded. Group C exists for this. | **Checkable finding.** The strongest claim available, and the rarest. |
| **2** | **We measured an axis they did not.** A target we promote on structural grounds that they never evaluated structurally. | **Nothing — by construction.** They did not fold. Orthogonal information, not contradiction. | **Hypothesis.** Reportable as a generated candidate, never as a correction. |
| **3** | **Our pipeline is wrong.** Bad ECD boundaries, degenerate folds, a scorer fitting noise on 22 positives, a length-truncation artefact. | **Internal diagnostics** — below. | **A bug.** Reported as a finding about method, which for an ML course is a legitimate result. |

**Ruling out (3) is a precondition for claiming (1) or (2).** The diagnostics, fixed in advance:

- **Fold sanity per target**: CA-atom count matches sequence length, zero NaN coordinates,
  radius of gyration consistent with a compact globular expectation. (The S-003 checks; they
  generalise.)
- **Boundary sanity**: the ECD span came from a UniProt `Topological domain` annotation and was
  not silently truncated by a length cap. Any target folded on a truncated ECD is **flagged and
  excluded from ranking claims** — a truncated fold is a different molecule.
- **pLDDT floor**: targets whose ECD folds below a pre-set mean-pLDDT threshold are reported
  separately, not silently ranked. *ESMFold's own uncertainty is a feature of the pipeline, not
  noise to average over.*
- **Score stability**: a disagreement that vanishes under leave-one-out refitting is a scorer
  artefact, not a finding.

**A disagreement surviving all four diagnostics is interesting whichever way it falls.** One
that does not is a bug report — still a result, and for a DL course arguably a more instructive
one than a ranking that happened to work.

**Pre-registered negative outcome, stated so it cannot be quietly abandoned:** if the
structural ranking's disagreements with the comparator are **entirely** explained by (3), the
honest conclusion is that this pipeline, at this cohort size, with these features, does not add
measurable signal over expression-based prioritisation. That is the result, and it gets written
up as the result.

**Claim discipline, binding on the UI:** a class-(1) disagreement may be stated as evidence
about the comparator; a class-(2) disagreement may be stated **only** as a hypothesis. The
interface must make the class visible — the two look identical in a sorted table and mean
entirely different things.

---

#### §2 — The cohort (Accepted)

Three groups, kept **structurally distinct in the data model and visually distinct in the
UI**. Conflating them would be the same error as a test double that reads as coverage.

| Group | n | Role |
|---|---|---|
| **A — the 82** | 82 | Baseline cohort. Kathad et al.'s prioritised targets, with their published 1–5 evidence score as the **baseline ranking to compare against**. |
| **B — in-cohort positives** | 22 | Targets within A already tested as ADCs preclinically or clinically (incl. ERBB2, NECTIN4, EGFR). **The labelled set.** |
| **C — baseline exclusions** | ≥3 | Approved/advanced targets the baseline pipeline **filtered out** — TROP2, HER3, CLDN18.2. Folded and scored as an **out-of-cohort probe**, never mixed into A. |

**Why B is better than "the 23 approved ADCs":** the labels sit *inside* the same cohort, so
evaluation is a within-cohort comparison rather than a join across two differently-derived
datasets. 60 of the 82 are unexplored for ADC development — that is the prediction set.

**Group C is the sharpest test available, and its provenance must be stated precisely,
because two different claims are involved:**

- **Theirs (cited):** Kathad et al. explicitly name TROP2, HER3, and CLDN18.2 as omitted by
  their filters, and offer the likely causes — the 150 quasi-H-score cutoff, the
  critical-normal-tissue rule, and missing IHC data. They record it as a limitation.
- **Ours (derived here, 2026-07-21):** that at least one of those omissions is the target of
  **two FDA-approved ADCs** (sacituzumab govitecan; datopotamab deruxtecan), making it a
  **false negative of the baseline** rather than a neutral methodological gap. The paper
  does not make this connection.

**Trop-2 is already folded** (248 aa ECD, int8 trunk, verified deterministic and
structurally sane — S-003). If the structural score ranks it well, that is a concrete
instance of the structural axis recovering something expression-based filtering discarded —
far sharper than an aggregate correlation.

**⚠ Stated as a limit, not buried:** three named exclusions, at least one approved, is a
**single instance and not a demonstrated pattern**. "The baseline has blind spots" is the
hypothesis this project tests, **not a finding inherited from the paper**. If the structural
score fails to recover Trop-2, that is a result, and no part of the UI may have promised
otherwise.

**Open, blocking §2's completeness:** the reconciliation of the full approved-ADC target set
against the 82 has **not been run**. Group C is currently the three exclusions the authors
named; there may be others they did not. A mechanical reconciliation script closes this and
must run before the cohort is called final.

---

#### §3 — Where the deep learning does load-bearing work (Accepted)

**A learned scorer**, not a weighted heuristic. Structure-derived features from our own ESMFold
folds → a small trained model → an ADC-suitability score, fit against Group B.

- **Trained**, per explicit ruling. A hand-weighted sum over literature numbers would make the
  neural network decorative — ARCHITECTURE §1's exact failure mode.
- **Small, interpretable feature set.** 22 positives cannot support many parameters. A handful
  of structural features (pocket geometry, surface accessibility, epitope-region pLDDT, ECD
  size/shape) — **not** a learned embedding over structure. Interpretability is not decoration
  here: it is what lets a disagreement be attributed to a feature rather than shrugged at.
- ESMFold stops being the deliverable and becomes the **input to** one. The network's output is
  now a judgement that can be wrong — which is the point.

**⚠ 22 positives is a small labelled set, and early stopping is not sufficient mitigation.**
Pre-registered here, **before any result exists**:

1. **Leave-one-out at the target level.** Hold out one Group B target at a time; ask whether
   the model still ranks it highly. Reported as a **distribution**, never a single CV number.
2. **Feature count fixed before fitting**, and recorded in this entry when chosen. Growing the
   feature set after seeing results is how 22 positives get overfit.
3. **Named negative outcome:** if leave-one-out ranking of held-out positives is
   indistinguishable from the comparator's evidence score, the structural axis adds nothing
   measurable at this cohort size. That is the result.
4. **A second named negative, easily missed:** if the structural score correlates *strongly*
   with the comparator's evidence score, that is **also** a null result — it means our features
   are proxying for attention-and-precedent rather than measuring structure. **Check this
   explicitly.** A high correlation would feel like validation and would not be.

**⚠ Group B is not a clean positive set, and the fit inherits its bias.** These targets were
pursued partly *because* they were tractable, and their tractability was assessed by people who
could see things we cannot. The honest claim is **"does our score recover targets already known
to be viable"** — never **"does our score predict clinical success."** Group B is small,
non-random, and survivorship-selected, and any model fit to it inherits all three properties.
Stated here so no downstream summary can quietly upgrade the claim.

---

#### §4 — Compute consequence: the cohort is measured before it is rented (Accepted)

Folding all 82 ECDs (plus Group C) against a **measured local ceiling in (440, 630) aa**
(S-004/S-005) means an unknown fraction goes to the D-011 rented GPU. The original D-011
estimate (~$0.25, HER2-class only) was scoped to a handful of targets and **does not survive
this decision unexamined**.

**Decision: measure the length distribution before scoping the rental.** A script queries
UniProt for each cohort accession, extracts `Topological domain` features with description
`Extracellular` (per D-009 §2), and reports the ECD-length distribution and the
above/below-ceiling split. Cheap, runs locally, needs no GPU.

**This is a reportable finding, not just planning.** For an ML course, the empirical
relationship between model memory footprint, sequence length, and required compute is at
least as germane as the biology. The deliverable includes: how many targets fit an 8 GB
consumer GPU, how many did not, what the overflow cost, and what that implies about the
hardware floor for structure-based screening at cohort scale. **We report the size of the
icebreaker, measured.**

- **Deep-learning justification:** §3 is the entry's core — a trained model producing a
  primary output from features derived from inference this project runs. §4 makes the
  compute requirement an empirical finding rather than an assumption. §2 supplies the
  control and the labels without which §3's output could not be evaluated at all.

- **Consequences / follow-ups:**
  - **Iteration 1 stays single-target; ranking is Iteration 2 and becomes the spine**, with
    single-target analysis as the drill-down. Per ruling.
  - **Schema anticipates ranking now.** A `ranking_runs` concept (target-list version,
    scorer version, timestamp) with a nullable FK from `protein_analyses`. Costs almost
    nothing today; retrofitting it into an applied migration chain is expensive. **Touches
    PR A's neighbourhood — coordinate before the migration lands.**
  - **UI must surface the DL contribution or it is invisible**, including to a grader. Named
    now, specified in its own entry: a comparative ranking view (baseline rank, structural
    rank, delta, movers), per-target fold provenance (model revision, dtype, chunk_size,
    pLDDT, date — surfaced from `inference_settings`, not left in JSONB), Group C marked
    visually distinct, and the Mission Briefing carrying the research question and the
    Trop-2 reasoning **with both attributions and the single-instance caveat**.
  - **Attribution:** Kathad et al. is CC-BY. The 82, the evidence scores, and the expression
    matrices are reused **with citation**, and the UI says so.
  - **Trop-2 sits outside Group A** — a real limitation of the baseline worth commenting on,
    and the reason Group C exists.
  - **Data sources to pin with retrieval dates**, since all are living resources: HPA v22,
    the surfaceome, UniProt, Open Targets. Reproducibility (ARCHITECTURE §7) requires the
    version, not just the URL.

---

### D-014 — Production Postgres is the existing Fly MPG cluster, own database
- **Date:** 2026-07-21
- **Status:** Accepted
- **Context:** D-012 committed the project to Postgres-first and named "the Fly Postgres
  addon" as the host. Provisioning it revealed that phrase covers **two different products
  with different capabilities and separate CLI surfaces**, and that the assumption behind
  it was wrong in both directions — first about capability, then about cost.

  **Measured on 2026-07-21. Every claim below is an observation, not documentation:**

  1. **Unmanaged Fly Postgres cannot run pgvector at all.** On the existing unmanaged
     cluster `jarvis-db2` (Postgres 17.7):
     - `SELECT extname FROM pg_extension WHERE extname='vector'` → **0 rows**
     - `SELECT name FROM pg_available_extensions WHERE name='vector'` → **0 rows**

     The second query is decisive: pgvector is not merely disabled, it is **absent from the
     image**. No `CREATE EXTENSION` can ever succeed. Enabling it there requires building a
     custom image on `flyio/postgres-flex`, compiling pgvector, publishing to a registry,
     recreating the cluster from a volume snapshot, and maintaining that image across every
     version bump.

  2. **An MPG cluster already exists and is already being paid for.**
     `sentinel-holy-rain-4562` (`gjpkdonnmkeoyln4`) — Basic, Shared×2, 1 GB RAM,
     **Postgres 16**, region **SJC**, pooling enabled, **10 GB provisioned / 2.5 GB used**,
     created 28 days ago. Cost Explorer month-to-date: **$8.55 MPG Cluster + $0.62 MPG
     Cluster Storage**, projecting to ~$38/month — which accounts for the account's jump
     from a $38.11 last invoice to a $66.57 upcoming one.

  3. **pgvector enables per-database on MPG, from the dashboard, with no app attached.**
     Database `pharmfoldmdk` created on that cluster; `vector` **v0.8.2** toggled on and
     reported as **enabled**, **installed in the `extensions` schema**.

  **The cost premise of the original draft was wrong.** That draft rejected Fly on the
  grounds that MPG meant a *new* $38/month plan and moved the database to Neon's free tier.
  With the cluster already provisioned and billed, the marginal cost of hosting
  PharmFoldMDK is **storage only** — pennies against 7.5 GB free — and the entire case for
  a second vendor evaporates.

- **Decision:** Production Postgres is the **existing MPG cluster
  `sentinel-holy-rain-4562`**, with PharmFoldMDK in its **own database (`pharmfoldmdk`)**,
  not sharing `fly-db`. pgvector v0.8.2 enabled on that database. Fly remains the serving
  tier and the Volume host; ARCHITECTURE §5's "Fly Postgres addon with pgvector" is
  **narrowed to MPG specifically** — the unmanaged product cannot satisfy it.

  **Rejected alternatives:**

  | Option | Rejected because |
  |---|---|
  | Share `jarvis-db2` | pgvector absent from the image (measured). Also no isolation — PharmFoldMDK migrations would run against the database JARVIS depends on daily. |
  | New unmanaged Fly cluster | Custom pgvector image to build, publish, and maintain; DR is ours. Recurring work, zero graded output — to obtain what MPG provides as a toggle. |
  | Neon free tier | Genuinely viable and was the recommendation until the sunk MPG cost surfaced. Costs private networking, adds a second vendor, adds free-tier schedule risk, and adds a 500 ms–2 s cold start — to save ~$0.28/month. |
  | Supabase free tier | Free projects **pause after 7 days** without database activity and need **manual unpause** (~30 s resume). A worker polling intermittently plus an irregularly-opened demo makes a 7-day quiet stretch plausible. The standard mitigation is a keep-alive cron whose failure is silent — the class of thing D-008 exists to eliminate. |
  | Share `fly-db` on the MPG cluster | No isolation, for no saving. MPG supports multiple databases per cluster and enables extensions **per-database**, so a separate database costs nothing and contains a bad migration. |

- **Deep-learning justification:** Direct. pgvector is what makes `analysis_embeddings` —
  learned embeddings powering semantic search — a real deliverable rather than a decorative
  one (ARCHITECTURE §1). The measured finding is that the originally-named host **cannot
  run pgvector at all**, so this entry is the difference between a named DL deliverable
  being possible and being quietly dropped at Iteration 3.

- **Consequences / follow-ups:**
  - **⚠ pgvector is installed in the `extensions` schema, not `public`.** A migration
    emitting `vector(384)` will fail with *type does not exist* unless `extensions` is on
    the `search_path` or the type is schema-qualified. **This must be handled in the first
    migration that creates a vector column**, and the chosen approach recorded here.
  - **Postgres 16** (MPG's default; the cluster predates this project). Pin local dev and CI
    to 16 so behavior matches; do not let tooling drift to 17.
  - **Shared compute with `fly-db`.** Basic is Shared×2 / 1 GB RAM across all databases on
    the cluster. Logical isolation is real (separate database, separate extension state, a
    bad migration is contained) but **CPU and memory are not isolated** — a runaway query in
    one database can starve the other, and a cluster-level incident takes both down. Load is
    expected to be light (a polling worker, occasional queries), but this is a **named
    coupling**, not an assumption of safety.
  - **Region SJC**, consistent with existing apps. Since February 2026 inter-region private
    network usage bills at Machine rates, so the serving tier should stay in SJC.
  - **Connection string is not yet obtainable** — the Connect page wants an app attached,
    and no PharmFoldMDK app exists. Not blocking: nothing connects until the first Alembic
    run. Consequence for sequencing: **the Fly app is created before the database is
    reachable**, inverting the usual order. Whether `flyctl mpg` can yield credentials
    without an attachment is unverified.
  - **Pooling is enabled.** Use the **direct** connection for Alembic (transaction-mode
    poolers break DDL and session-level operations) and the pooled connection for the app at
    runtime. Both strings recorded in secrets, never in the repo.
  - **D-005's Postgres integration CI job** should run a Postgres **service container**, not
    connect to this cluster — CI must not depend on an external service, live credentials,
    or shared compute. Per D-012 this remains the only thing that will ever prove the
    D-009 §1 `SKIP LOCKED` claim path.
  - **Unrelated but surfaced:** `jarvis-db2` (unmanaged) and the MPG cluster now both exist
    and both bill. Whether JARVIS should migrate is **out of scope here** and is not
    decided by this entry.

---

### D-012 — Prod DB is Postgres-first; the test-DB split and the job-queue seam it forces
- **Date:** 2026-07-21
- **Status:** Accepted. Authorizes PR A (`jobs` table, queue functions, migration).
- **Resolves:** the open question *"Prod DB choice: Postgres-first vs. SQLite-on-Volume
  prototype (Database Plan §5)."*
- **Depends on:** D-013 (the gate can now install SQLAlchemy/Alembic/psycopg).

#### §1 — Decision

**Postgres is the production database, from the first migration.** The SQLite-on-Volume
prototype path from Database Plan §5 is closed, not deferred.

There is no serious counter-case, and the entry is short on this point because the reasoning
is already load-bearing elsewhere in the log:

- **pgvector** is required for the semantic-search embeddings (Database Plan; D-004's serving
  tier). SQLite has no equivalent, so the prototype path ends in a rewrite the moment
  embeddings land — and embeddings are part of the graded DL claim, not an optional extra.
- **`SELECT … FOR UPDATE SKIP LOCKED`** is the claim mechanism D-009 §1 already ratified. It
  is Postgres-specific.
- **A managed Postgres host is already the topology** in D-004 §"serving tier". Choosing SQLite
  now would contradict a ratified decision to save work that has not started.

> **Host: see D-014, and do not reuse the phrase this entry originally used.** An earlier draft
> of this section named *"the Fly Postgres addon"* as the host. **That phrase covers two
> different Fly products with different capabilities and separate CLI surfaces, and only one of
> them can run pgvector at all** — measured, not documentation: on the unmanaged cluster
> `jarvis-db2`, `pg_available_extensions` returns **zero rows** for `vector`, so pgvector is
> absent from the image entirely and no `CREATE EXTENSION` could ever succeed. The host is
> resolved in **D-014**: the existing **MPG** cluster `sentinel-holy-rain-4562`, database
> `pharmfoldmdk`, pgvector **v0.8.2** enabled. This entry defers to D-014 for the host and does
> not restate it.

What makes this entry worth writing is not the choice. It is **what the choice forces**, in
§3–§5.

#### §2 — The test database stays SQLite (D-005), and that is now a real split

D-005 fixed the test DB as SQLite: fast, deterministic, no external service, no container in
CI. That still holds. But with §1 settled, prod and test are now **different engines**, and
the gap between them is no longer theoretical.

**Named precedent — JARVIS, same class of failure, observed twice.** In the JARVIS project the
pytest suite built its schema with SQLite `create_all` and never ran the Alembic chain, so
migration-bootstrap bugs were structurally invisible to the tests: a green suite proved
nothing about whether a fresh database could actually be built. That was audit finding H2,
and it was fixed by adding a CI job that runs `alembic upgrade head` against a throwaway
Postgres. The gate earned its keep the same day it was cited here — an unguarded column rename
passed the full local suite and failed immediately against fresh Postgres.

The lesson transfers exactly: **a green SQLite suite is not evidence about Postgres.** D-005
already flagged this; §3–§5 make it structural rather than a note.

#### §3 — CORRECTION: `FOR UPDATE SKIP LOCKED` is a **syntax error** on SQLite, not an
untested path

The session pre-work stated that today's suite "proves the claim function's behavior, not its
concurrency." That is **true and misleading**, in precisely the way this log's *Method note*
warns about — an accurate summary that conceals the failure mode. It reads as though the
statement runs on SQLite and merely fails to exercise contention. It does not run at all.

**Measured, not assumed** (stdlib `sqlite3`, library version **3.45.1**):

```
SELECT id FROM jobs WHERE status='pending' ORDER BY created_at LIMIT 1 FOR UPDATE SKIP LOCKED
  -> OperationalError: near "FOR": syntax error
```

Narrowing it, because "SKIP LOCKED is unsupported" would itself have been an imprecise claim:

| Fragment | SQLite 3.45.1 |
|---|---|
| `FOR UPDATE` | `OperationalError: near "UPDATE": syntax error` |
| `FOR UPDATE SKIP LOCKED` | `OperationalError: near "UPDATE": syntax error` |

**`FOR UPDATE` itself is rejected**, not just the `SKIP LOCKED` modifier. SQLite has no
row-level locking to express, so there is no clause to degrade gracefully.

**Why the distinction changes the design.** "Unverified concurrency" invites one function with
a dialect branch, tested on the SQLite arm and assumed on the Postgres arm. "Syntax error"
makes that impossible to do honestly: the Postgres arm cannot execute in the suite *at all*,
so any structure that presents the two arms as one tested function is a coverage claim the
tests do not support. Recorded as a correction rather than silently designed around, per the
Method note's provenance rule.

#### §4 — The claim-function seam: a repository interface

**Decision.** The queue is reached through a narrow interface, not a function with an engine
branch inside it:

```
core/queue.py
    class JobQueue(Protocol):          # claim / complete / fail / reap_stale
    class PostgresJobQueue:            # the real one — SELECT … FOR UPDATE SKIP LOCKED
                                       # NEVER executed by the SQLite suite
tests/doubles.py
    class UnlockedFakeJobQueue:        # in-memory. Name says what it is not.
```

**The argument for the seam is coverage honesty, not scale.** Worth stating plainly because
the obvious objection is right on its own terms: at D-004's single-worker scale the
indirection buys **nothing operationally**. One worker cannot contend with itself, and if that
were the whole argument, the seam would be premature abstraction and should be skipped.

The actual argument is about what the test report claims. A dialect branch inside one function
appears in coverage as *one function, exercised*, with a small variation — when the Postgres
arm has never run a single time. Not under-tested: never executed. A separate implementation
class makes that visible in the shape of the code, and a double named `UnlockedFakeJobQueue`
(rather than `InMemoryJobQueue` or `TestJobQueue`) makes it visible at every call site. The
name is doing real work: it is the difference between a reader concluding "the queue is
tested" and "the queue's *callers* are tested against a fake that does no locking."

**Consequence, stated so it cannot be mistaken later:** the suite will prove the claim
function's *callers* handle claim/complete/fail/stale-reap correctly. It will prove **nothing
whatsoever** about `FOR UPDATE SKIP LOCKED` — not its syntax, not its semantics, not its
behaviour under contention. The seam does not test the queue. It stops the tests from
*claiming* to.

#### §5 — The seam is an honesty mechanism, not coverage

Explicit because it is the easy mistake to make next session: **§4 closes no gap.** It makes an
existing gap legible. The only thing that will actually exercise `PostgresJobQueue` is a
**Postgres integration job in CI** — a service container running the real engine, the item
already sitting in this log's open questions as *"Postgres integration test job for
pgvector/Postgres-specific paths (D-005 gap)."*

That job is **not** built in PR A. Until it exists, the honest statement of coverage is:

> The claim path has never executed. Its callers are tested against a fake that does no
> locking, and the fake is named to say so.

It remains an open question with a named owner-decision pending, not a solved problem. When it
is built, the JARVIS precedent in §2 is the template: a throwaway Postgres service in the gate,
migrations applied, the real implementation exercised. **D-014 adds a constraint on how:** that
job must use a **service container**, not a connection to the production MPG cluster — CI must
not depend on an external service, live credentials, or compute shared with JARVIS.

#### §5a — Constraint inherited from D-014: pgvector lives in `extensions`, not `public`

Recorded here because it lands on **PR A's migration work**, not at Iteration 3 when the vector
column is finally written.

pgvector v0.8.2 on the `pharmfoldmdk` database is installed in the **`extensions` schema**. A
migration emitting a bare `vector(384)` therefore fails with **`type "vector" does not exist`**
— the type is real and enabled, just not on the default `search_path`.

Three ways to handle it, and the choice is deliberately **not** made here:

| Approach | Trade-off |
|---|---|
| Schema-qualify the type (`extensions.vector(384)`) | Explicit and local; every vector column must remember it |
| Set `search_path` in the Alembic env / connection | One place; invisible at the call site, and a future connection that forgets it fails confusingly |
| `ALTER DATABASE … SET search_path` | Outside the migration chain — the exact class of environment state that is not reproducible from the repo |

**PR A does not create a vector column**, so it does not have to resolve this. It is written
down now so the first migration that *does* is designed rather than debugged, and so the
approach is chosen with the trade-off visible. **D-014 requires the chosen approach to be
recorded back into that entry.**

**Postgres version:** D-014 pins prod to **Postgres 16** (the MPG cluster's version, which
predates this project). Local dev and any future Postgres CI service container should match —
do not let tooling drift to 17, or the suite starts proving things about an engine prod does
not run.

#### §6 — Deep-learning justification

Inherited from D-009 §1 and still load-bearing: the queue is the mechanism that lets neural
inference run on hardware that can actually hold the model. D-011 split compute across a local
tier (≤440 aa) and rented GPU (>440 aa); **both** pull work through this queue, so a queue that
loses or double-claims jobs corrupts the cache that Iteration 1's entire demo is served from.

The Postgres choice specifically carries the DL work in a second way: **pgvector is where the
learned embeddings live.** Semantic search over ADC targets is a place a neural model does
primary work rather than decorating a database lookup, and SQLite cannot host it. Choosing
SQLite for prod would have meant either dropping that capability or rewriting the storage layer
to reintroduce it.

#### §7 — Consequences

- `db/` is created in PR A, and `ARCHITECTURE.md` §8 repo layout is updated in that same PR
  (governance rule 2).
- Alembic migrations target Postgres. The SQLite suite does **not** run the migration chain —
  the exact JARVIS H2 shape from §2. Mitigation is the §5 integration job; until it exists,
  this is a known, named exposure and not an oversight.
- `psycopg[binary]` is already pinned and hash-locked into CI (D-013 + Amendment A), so PR A
  adds no new dependency risk to the gate.
- The `sqlite_conn` fixture from D-007 stays for tests that genuinely only need a scratch
  database. It is not the queue's test path.
- **Alembic connects on the DIRECT string, not the pooled one** (D-014): transaction-mode
  poolers break DDL and session-level operations. The app uses the pooled string at runtime.
  Both live in secrets, never in the repo.
- **The host is D-014's, and this entry's host claim was wrong before it was corrected.** The
  original draft named "the Fly Postgres addon" — a phrase spanning two products, only one of
  which can run pgvector. Left as a marker: a plausible name for a dependency is not the same
  as a verified capability of it, and the difference was only found by querying the actual
  cluster.

---

### D-013 — Pinned dependency manifest + gate install step
- **Date:** 2026-07-21
- **Status:** Accepted — proven, not asserted (see §5).
- **Sequenced before D-012 and before any model code.** This entry modifies the **required
  status check**. Under D-008 that is exactly the class of change that gets *proven*, and it
  gets proven *first*, because everything after it depends on the gate still working.

#### §1 — The problem

The gate installs `pip install --upgrade pip pytest` and nothing else. That was correct for
the keel (D-007), whose fixture deliberately used stdlib `sqlite3` so the suite needed no
dependencies at all. It stops being correct the moment any application code imports
SQLAlchemy or Alembic: the suite would fail to import, and there is no manifest for the gate
to install.

**Why this is not a trivial plumbing change.** `test` is a required check on a
branch-protected `main` with `enforce_admins: true` and no bypass — for the owner either.
Adding an install step introduces failure modes the gate did not previously have:

| New failure mode | Effect while it lasts |
|---|---|
| Resolution failure (bad pin, yanked release, conflicting constraints) | every PR red |
| Version drift (unpinned dep ships a breaking release) | every PR red, with no repo change to explain it |
| Index flake / network failure | every PR red, intermittently |

Each of these blocks **every PR in the repo, including the PR that would fix it**, because
there is no admin bypass. That is the same deadlock shape D-008 removed when it deleted
`paths-ignore` — a required check that cannot report leaves PRs unmergeable forever. The
mitigation is different here (the check *can* report; it just reports red), but the blast
radius is the same and it deserves the same care.

#### §2 — Decision

- **Two manifests, both pinned to exact versions (`==`).**
  - `requirements.txt` — runtime dependencies (what prod needs).
  - `requirements-dev.txt` — `-r requirements.txt` plus test-only tooling.
- **The gate installs `requirements-dev.txt`**, which transitively installs the runtime
  manifest. Deliberate: installing only dev dependencies would let a broken *runtime* pin
  reach deploy untested, which is precisely what D-005 exists to prevent.
- **Exact pins, not ranges.** A range means the gate's behaviour can change with no commit
  in this repo — a red `main` with an empty `git log` to explain it. Reproducibility is also
  a standing requirement of this project: D-004 records `inference_settings` (dtype, chunk
  size, model revision) per job so a fold can be reproduced. A floating dependency set
  undermines that at the environment level. Pins are upgraded deliberately, in a PR, where
  the gate proves them.

Initial pins:

| Package | Pin | Why now |
|---|---|---|
| `SQLAlchemy` | `2.0.51` | models + queue functions (D-012, PR A) |
| `alembic` | `1.18.5` | migrations (D-009 §1) |
| `psycopg[binary]` | `3.3.4` | Postgres driver for prod (D-012). psycopg **3**, not psycopg2 — actively developed and the current SQLAlchemy 2.0 recommendation. `[binary]` avoids needing libpq headers at install time. |
| `pytest` | `9.1.1` | the suite. Previously unpinned and floating. |

`psycopg` is unused by the SQLite test suite and is installed anyway — the manifest describes
what **prod** needs, and proving it resolves is the point.

#### §3 — Caching: **NO**, deliberately

`actions/setup-python` can cache the pip download directory keyed on a hash of the manifest.
**We are not enabling it yet.**

- The saving is small: this dependency set installs in roughly 10–20 s against a suite that
  runs in ~20 s.
- The cost is a new failure mode on a check that has no bypass. A cache is another thing that
  can be stale, poisoned, or partially restored, and its failures are intermittent —
  the hardest kind to diagnose while every PR is blocked.
- Reinstating it is a one-line change with an obvious trigger: install time becoming a real
  cost as `app/`, `core/`, and `worker/` acquire dependencies.

Recorded as a decision rather than an omission so the absence is legible later.

#### §4 — Explicitly NOT in this manifest

`torch`, `transformers`, `bitsandbytes`, and the ESMFold model weights. They belong to the
**local/rented GPU tier** (D-004, D-011), not the Fly serving tier and not CI. The gate must
never attempt to install a CUDA stack — it would be slow, fragile, and pointless on a CPU
runner. The worker acquires its own manifest when `worker/` is built, and it is a separate
file by design.

#### §5 — Proof (D-008 pattern: demonstrate, do not assert)

A gate change is proven by watching it behave, in both directions:

1. **RED first.** The manifest was pushed with a deliberately invalid pin
   (`SQLAlchemy==2.0.99999`, a version that does not exist). Expected: `test` fails at the
   install step with a resolution error, before pytest runs — confirming the gate actually
   installs the manifest rather than silently ignoring it.
2. **GREEN second.** Pin corrected to `2.0.51`, same PR. Expected: install succeeds, suite
   green, check reports pass.

Both observations are recorded in this entry when they land, and the PR is not merged until
green is witnessed. *Result: see §6.*

#### §6 — Observed result

- **RED — observed.** Commit `93dc215`, run `29867026923`. `test` failed in **8 s** at the
  `Install dependencies` step:

  ```
  ERROR: Could not find a version that satisfies the requirement SQLAlchemy==2.0.99999
  ERROR: No matching distribution found for SQLAlchemy==2.0.99999
  ```

  **pytest never ran** — verified by grepping the failed job's log for
  `passed`/`failed`/`collected` and getting zero matches, rather than inferring it from the
  step ordering. `deploy` reported `skipping`, confirming `needs: test` still holds.

  This is the load-bearing observation. It proves the gate genuinely *resolves* the manifest
  rather than installing it best-effort and continuing, so a future bad pin fails loudly here
  instead of reaching deploy.

- **GREEN — observed.** Commit `3bc3a8f`, run `29867598394`. Pin corrected to `2.0.51`;
  install succeeded, `test` passed in **20 s**, pytest reported `1 passed in 0.01s`.

  Full resolved set, transitives included, so a later drift is diagnosable rather than
  mysterious — the pins name four packages, the environment actually contains thirteen:

  ```
  Mako-1.3.12  MarkupSafe-3.0.3  SQLAlchemy-2.0.51  alembic-1.18.5
  greenlet-3.5.3  iniconfig-2.3.0  packaging-26.2  pluggy-1.6.0
  psycopg-3.3.4  psycopg-binary-3.3.4  pygments-2.20.0  pytest-9.1.1
  typing-extensions-4.16.0
  ```

  **The nine unpinned transitives are the residual exposure.** Exact pins on direct
  dependencies do not freeze the environment; a breaking release of `greenlet` or `pluggy`
  can still turn the gate red with no commit in this repo. Fully closing that needs a lock
  file (`pip-compile` / `uv lock`) and is deliberately deferred — it is a real cost in
  maintenance for a risk that has not yet bitten. Recorded here so the gap is known rather
  than assumed away, and so that when an unexplained red does appear, this is the first place
  to look.

#### §7 — Deep-learning justification

Indirect, and honest about being indirect. No neural network runs in CI and none should. What
this buys the DL work is **reproducibility of the environment around it**: D-004 requires each
fold to record its `inference_settings` so a result can be reproduced, and that guarantee is
worth less if the surrounding library versions drift underneath it. Pinning the serving-tier
manifest is the environment-level half of the same commitment. It also protects the *ability
to ship* the DL work at all — an unbypassable gate stuck red halts every subsequent PR,
including the ones that carry the model.

#### §8 — Consequences

- `ARCHITECTURE.md` §5 (deploy gate) and §8 (repo layout) updated in this PR.
- The gate's install step is now a thing that can break independently of the tests. When it
  does, read the *install* step, not the pytest output.
- Upgrading any pin is a PR that the gate proves. There is no other supported route.
- A **Postgres integration job** is still absent (D-005's known gap, restated in D-012). This
  entry does not address it and must not be read as having done so.

---

#### AMENDMENT A (2026-07-21) — exact pins did not close the gap; a lock file does

**Recorded as an amendment rather than an edit to §1**, because the reasoning that led to
deferring was correct on the information available at the time, and overwriting it would
destroy the evidence of *why* the gap was missed. §1 stands as written.

**What §1 claimed and what was actually true.** §1 identified "version drift (unpinned dep
ships a breaking release) → every PR red, with no repo change to explain it" as a failure mode
the exact pins would close. **That claim is true of the four direct dependencies and false of
the environment.** The green run resolved them to **thirteen** installed packages; nine were
unpinned transitives (`greenlet`, `pluggy`, `Mako`, `MarkupSafe`, `packaging`, `iniconfig`,
`pygments`, `typing-extensions`, `psycopg-binary`). A breaking release in any of them still
reddened the gate with no commit in this repo — precisely the failure mode §1 named as
addressed.

This is the same error shape the *Method note* describes and the same one that produced the
fabricated SHAs in §6 the same afternoon: **a true statement about the part that was checked,
read as a statement about the whole.** "Direct dependencies are pinned" was accurate. "The
environment is pinned" was not, and only the second one is what §1 needed.

**Decision — lock the full graph.**

- `requirements.lock` and `requirements-dev.lock`, compiled with **`uv pip compile
  --generate-hashes --universal --python-version 3.11`** (uv 0.11.30). Every transitive is
  pinned and hashed; `--universal` resolves across platforms so the same lock serves Linux CI
  and a Windows dev machine.
- **The gate installs the lock with `--require-hashes`**, so pip refuses any artifact whose
  hash does not match. The installed environment is now a function of a committed file, which
  is the actual requirement: *a red gate is attributable to a commit in this repo.*
- The `.txt` manifests remain the **human-edited inputs** — they say what we want; the locks
  say what that resolved to. Changing a dependency means editing the `.txt`, recompiling, and
  committing both.

**Why now rather than later, and it is not maintenance appetite.** Two reasons:

1. **Cost curve.** `app/`, `core/`, and `worker/` are about to land, and the worker's tree is
   the heavy one — PyTorch, transformers, bitsandbytes. Locking four direct dependencies is
   cheap; locking after that arrives is not.
2. **It is the same discipline this project already applies to model weights.**
   `ARCHITECTURE.md` §7 commits to reproducibility as a *graded* expectation, and D-004
   records per-fold `inference_settings` including the model revision so a result can be
   reproduced. An environment with nine floating packages undermines that claim for exactly
   the reason a floating model revision would. **A lock file is the environment-level version
   of a pinned checkpoint.** That argument outweighs the maintenance cost in a way that
   general engineering hygiene, on its own, would not have.

**Tool choice.** `uv` over `pip-compile`: faster resolution, and it handles the two-manifest
split cleanly (`requirements-dev.txt` includes `requirements.txt`, and the compiled dev lock
correctly attributes each entry). **uv is a local authoring tool only — it is NOT installed in
CI.** The lock is plain hashed requirements format, so the gate uses stock pip and gains no new
dependency. That keeps the required check's toolchain as small as possible.

**Residual exposure, stated so it is not assumed away in turn:** the lock fixes *versions and
artifact hashes*, not the index's availability. A PyPI outage still reddens the gate and is not
attributable to a commit here. That is a network-availability problem, not a reproducibility
one, and no lock file addresses it.

**Proof:** the gate must go green installing from the lock with `--require-hashes` before this
merges. *Result recorded below on observation.*

- **Observed.** Commit `f569a45`, run `29868958805`. `test` green in **15 s**, installing via
  `python -m pip install --require-hashes -r requirements-dev.lock`, then `1 passed in 0.01s`.
  **13 packages installed**, all hash-verified:

  ```
  alembic-1.18.5  greenlet-3.5.3  iniconfig-2.3.0  mako-1.3.12
  markupsafe-3.0.3  packaging-26.2  pluggy-1.6.0  psycopg-3.3.4
  psycopg-binary-3.3.4  pygments-2.20.0  pytest-9.1.1
  sqlalchemy-2.0.51  typing-extensions-4.16.0
  ```

  Note the lock contains **15** entries but CI installed **13**: `colorama` and `tzdata` carry
  `sys_platform == 'win32'` markers from the `--universal` resolution and are correctly skipped
  on the Linux runner. That difference is expected and is the marker mechanism working — worth
  recording so a future reader does not read it as the lock being partially applied.

  **Not proven here:** that a *tampered* artifact is rejected. `--require-hashes` is asserted to
  do that and is standard pip behaviour, but this run only demonstrates the happy path. A
  negative arm would require serving a mismatched artifact, which is not worth building; the
  load-bearing red arm for this gate was already taken in §6.

---

### D-011 — Split compute: local tier under the ceiling, rented GPU for large-ECD cache generation
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** S-004/S-005 bracketed the local sequence-length ceiling to **(440, 630) aa**.
  440 aa folds clean at chunk 64 (28.6 s, peak 6665 MiB, no spill, host stable);
  630 aa is **4-for-4 fatal host crashes**. HER2's full ECD (~630 aa) — the flagship ADC
  target — cannot be folded locally. D-004 §5 bounded the response to smaller model /
  narrower targets / different compute, explicitly **not** retrieval. This selects
  **"different compute."**
- **Decision — two paths, one pipeline:**
  - **Local tier** (Blackwell 8 GB, int8 trunk / bf16 base, chunk 64): every target
    under the measured ceiling. Trop-2 (~250), Nectin-4 (~350), and the 440 aa class.
    **0 crashes in ~94 folds.**
  - **Rented GPU, one-time batch:** targets above the ceiling. A ≥24 GB card runs fp16
    `esmfold_v1` unquantized and unchunked, so **the entire local mitigation stack stops
    binding.**
- **Provider: RunPod.** Per-second billing, no minimum commitment, zero egress fees.
  - **Card: RTX A6000 48 GB at $0.49/hr** (Secure Cloud). Chosen over the RTX 4090 24 GB
    at $0.69/hr — more VRAM for less money; **headroom matters more than speed** for a
    one-time batch. Community Cloud is ~50% cheaper but uses community-contributed
    hardware with reduced reliability; not worth the interruption risk on a job this
    short and this cheap.
  - **No network volumes.** Storage bills at $0.07/GB/month even while the pod is
    stopped. Use container disk; download weights, fold, upload artifacts, terminate.
  - **Estimated total cost for the full Iteration-1 large-ECD cache: ~$0.25.**
    (~5 min weight download + ~10 min folding at $0.49/hr.)
- **Fly.io GPU is eliminated, not deprioritized.** Fly deprecated GPU Machines; they
  become **unavailable after 2026-08-01**. D-003's "GPU deprecation on Fly.io" risk and
  D-004's Fly-compute framing are superseded — the option ceases to exist in 13 days.
  Fly remains the **serving tier** (CPU-only app + Postgres/pgvector + Volume), unchanged.
- **Deep-learning justification:** D-003's core is preserved intact — we run ESMFold
  ourselves on both paths.† Renting a GPU changes *whose silicon* executes the model, not
  *who runs it*: we still control the checkpoint, the precision, the chunking and the code,
  and we still perform the inference. That is categorically different from calling a hosted
  inference API or retrieving pre-computed structures, which is what D-004 §5 rules out.
  The graded DL claim is unaffected — arguably strengthened, since the project now
  demonstrates a measured hardware constraint and a reasoned compute split rather than a
  single-machine assumption.

  > † **The source text for this justification was truncated mid-sentence** at *"we run
  > ESMFold ourselves on both"*. The completion above is the obvious reading and is
  > flagged so it can be corrected if it misstates the intent.

- **Superseded by this entry (verified by grep across `docs/`, `ARCHITECTURE.md`, `CLAUDE.md`):**
  - `docs/README.md` D-004 context — *"Fly.io GPU is uncertain/expensive"* → now **eliminated**,
    with a date.
  - `docs/README.md` D-006 context — *"Fly.io GPU availability is uncertain"* → same.
  - `docs/TDD_v3_ADC_Focused.md` §7 — *"GPU deprecation on Fly.io: Handled by preferring
    pre-computed structures and lightweight models."* The **risk has materialised**; the stated
    mitigation is superseded by this split-compute decision. *(Planning docs are historical
    intent — per this log's preamble, the log wins where they diverge. Not edited.)*
  - `ARCHITECTURE.md` lines asserting Fly has **no** GPU are **correct and unchanged** — they
    already agree with this decision.
- **Follow-ups:** build the rented-GPU batch as **committed, reproducible code in this repo**
  (the binding condition of D-009 §3 — the cache pipeline must not be a one-off script);
  decide where rented-run artifacts land (Fly Volume upload path, D-004 consequence, still open);
  and note the untested possibility from S-005 that HER2 may yet fold locally at `chunk 16/32`,
  which would shrink the rented batch but does not block it.

### S-005 — bisect the length ceiling at 440 aa
- **Date:** 2026-07-19
- **Status:** **CLOSED 2026-07-19 — 440 aa FOLDED CLEAN (reading 1).** 28.6 s at `chunk 64`,
  peak 6665 MiB (no spill), pLDDT 84.27, 440/440 CA, zero WHEA events, zero bugchecks.
  **⇒ the ceiling is in (440, 630).** Most of the curated ADC set is locally foldable; only
  HER2-class targets (>440 aa) need external compute.
- **Type:** Spike — a single bisection step. **One run, then stop.**

**The bracket.** Length is the discriminator (S-004). The evidence, instrument-free:
- **248 aa (Trop-2): 0 crashes in ~93 folds** — both precisions, spilling and not.
- **630 aa (HER2): 4 crashes in 4 attempts.**

The ceiling lies somewhere in **(248, 630)**. **440 aa is the closest integer to the true midpoint**
(439), so a single run halves the remaining bracket **whichever way it goes** — maximum information
per crash, which matters when each observation costs a host.

**Sequence — hold everything constant except length.** Take the **HER2 ECD (`P04626`, 23–652) and
truncate to its first 440 residues**. Same protein, same amino-acid composition, same code path,
same UniProt-derived source. **Deliberately NOT a different protein at ~440 aa** — that would
reintroduce composition and fold-difficulty as confounds, and this run only has budget for one
variable.

**Configuration:** int8 (S-003 recipe), `chunk_size` 64 descending on OOM, driver 596.72,
GPU process list verified empty, WHEA window recorded from a noted T0.

**Expect JSON corruption on a crash.** S-004's results file was truncated to NUL bytes by the
unflushed mid-write. **That is now the known signature of a host loss, not a surprise or a bug** —
stdout is the surviving record, so read it first.

**THE THREE READINGS — fixed in advance:**

| # | Observation | Reading |
|---|---|---|
| **1** | **Completes clean** | Ceiling is in **(440, 630)**. Most of the curated ADC set is **locally foldable**; only HER2-class targets need external compute. |
| **2** | **Crashes** | Ceiling is in **(248, 440)**. The constraint is **broad**, and external compute does **most** of the cache work. |
| **3** | **Completes, with corrected errors but no fatal** | The **burst-without-crash** pattern seen on six historical days (F-001). **Treat as a PASS.** Interesting, but **uninformative about the ceiling** — corrected errors do not predict crashes. |

**Reading 3 exists because of F-001:** without it, corrected errors during a successful fold would
have been misread as a near-miss or a partial failure. They are neither.

- **Deep-learning justification:** the ceiling determines how much of the curated ADC target
  database the local tier can fold, and therefore how much of the graded DL pipeline runs on
  owned hardware versus rented compute.
- **Stop condition:** **one run.** Do not bisect further tonight regardless of outcome.

---

#### RESULTS (2026-07-19) — **CLOSED. Completed clean. READING 1 fired.**

**HER2 ECD truncated to 440 aa folded successfully on the first attempt.** Host alive; last reboot
remains 19:02:08 (the S-004 crash), i.e. **no new reboot**.

| Measure | Value |
|---|---|
| Chunk | **64** — first attempt, no descent needed |
| Wall time | **28.6 s** |
| Peak VRAM | **6665 MiB**, `spilled = False` (free was 7043 MiB) |
| mean pLDDT | **84.27** *(rescaled ×100 per the scale trap)* |
| CA count | **440 / 440** — exact |
| NaN/inf coords | **0** |
| Radius of gyration | **24.64 Å** (compact-globular reference for N=440 ≈ 22.2 Å) |
| **WHEA in window** | **0 corrected, 0 fatal** (window 19:22:23→19:24:50 contains folds 19:23:49→19:24:17) |
| **Bugchecks** | **0** |

Null verified against a same-day control (78 WHEA events today, last at 19:02:29 — the S-004 crash).
This is **reading 1, not reading 3**: there were no corrected errors at all.

**⇒ THE CEILING IS IN (440, 630).** The bracket is halved. Structure is sane (exact residue count,
no NaN, Rg slightly above the compact-globular estimate as expected for a multi-domain elongated
ECD), and pLDDT 84.27 is **notably higher** than Trop-2's 74.68.

**Product consequence:** **most of the curated ADC target set is locally foldable.** Typical ADC
target ECDs — Trop-2 ~250 aa, Nectin-4 ~350 aa, and now anything up to at least 440 aa — run on this
machine. **Only HER2-class targets (>440 aa) need external compute.** That is a far narrower
constraint than S-004 alone implied.

**⚠ Observation, labelled as inference not measurement — a memory-adjacent reading of the 630 aa
crash.** Peak at 440 aa was **6665 MiB against 7043 MiB free — only 378 MiB of headroom** at
`chunk 64`. Activation memory grows steeply with length, so **630 aa at `chunk 64` would very
plausibly have exceeded free VRAM and spilled during the fold**, even though it did *not* spill at
rest (`resident 5351 MiB`). S-004's peak was **destroyed with the corrupted JSON**, so this cannot
be confirmed. If it is right, **HER2 might still fold at `chunk 16/32`** — the descent existed but
S-004 crashed at `chunk 64` before reaching it. **Not tested; one run was the budget.** This does
not resurrect the spill mechanism generally (the fp16 control showed sustained spill at 248 aa
causes no crash), but it is a live possibility specifically for the 630 aa case.

**Next bisection step if resumed:** ~535 aa, same truncation method.

### F-001 — INSTRUMENT CORRECTION: WHEA corrected-error rate was **inverted**, not merely invalid
- **Date:** 2026-07-19
- **Status:** Accepted. **This retroactively restates evidence in S-001, S-002 and S-003.**
- **Type:** Finding about the *measuring instrument*, not about the system under test. Logged
  separately because it invalidates reasoning across multiple prior entries.

**The claim:** WHEA **Id 17 (corrected)** errors are **crash debris, not a precursor ramp.** Every
comparison in this investigation that used corrected-error *rate* was measuring the wrong quantity.

**Evidence 1 — corrected errors are logged *with* the fatal, never *before* it.** Per-second
grouping of all WHEA events today:

| Second | Events |
|---|---|
| 16:32:33 | **Id1 ×1** + Id17 ×13 *(same second)* |
| 16:32:34 | Id17 ×18 |
| 16:44:45 | **Id1 ×1** + Id17 ×31 *(same second)* |
| 16:48:16 | **Id1 ×1** + Id17 ×3 *(same second)* |
| 18:04:51 | Id17 ×3 *(no fatal)* |
| 18:06:27 | Id17 ×3 *(no fatal)* |
| 19:02:29 | **Id1 ×1** + Id17 ×3 *(same second)* |

In **all four** crashes the fatal is logged **first or simultaneously** with the corrected errors.
There is no gradual ramp preceding a fatal. The corrected errors are what the machine emits *as it
dies*.

**Evidence 2 — six burst days produced zero fatals.** Corrected-error volume does not predict crashes:

| Date | corrected | fatal |
|---|---|---|
| 2026-05-27 | 3 | **1** ← crash on only 3 corrected |
| 2026-06-09 | **65** | **0** ← 65 corrected, no crash at all |
| 2026-06-13 | 3 | 0 |
| 2026-06-15 | 3 | 0 |
| 2026-07-04 | 3 | 0 |
| 2026-07-10 | 31 | 0 |
| 2026-07-14 | 40 | 0 |
| 2026-07-19 | 74 | **4** |

**65 corrected errors with no crash (06-09), versus a crash on only 3 (05-27).** The instrument is
not just noisy — it is **anti-correlated with the thing we were using it to predict.**

**RESTATEMENTS forced by this finding:**

1. **S-002's rate comparison is void.** *"65 corrected in the crashing window vs 0 in clean runs"*
   was **three crash events versus zero crash events, double-counted** — the corrected errors were
   debris from those same three crashes. **The valid measure was always the fatal count: now 4 vs 0.**
2. **The fp16 control's "zero corrected errors" is weaker than recorded.** It reduces to
   **"no crash"** — which host survival had already established independently. **The refutation of
   the spill mechanism still stands, but it stands on the fatal count, not the corrected count.**
3. **"217 corrected errors since May, pre-existing" was true and largely irrelevant.** It does not
   describe a steadily degrading link. It describes a fault that **fires in bursts and usually
   recovers**. The 18:04/18:06 events previously attributed to the driver install **may equally have
   been a spontaneous burst — that is now unknowable, and is recorded as unknowable.**
4. **What survives with no instrument at all — and it is the strongest evidence in the
   investigation:**
   > **4 crashes in 4 HER2 (630 aa) attempts. 0 crashes in ~93 Trop-2 (248 aa) folds today** —
   > across **both precisions**, **spilling and not**, including 83 consecutive folds under
   > sustained load.

   This correlation depends on no event log, no severity bucketing, and no interpretation of WHEA
   semantics. Everything else in S-002 is weaker than this one line.

- **Deep-learning justification:** neutral (instrumentation), but it protects every downstream
  decision — the local tier's viability was being judged against a metric that was measuring
  crash aftermath.
- **Method note connection:** this is the same failure as `params_all_on_cuda` and the WHEA counts —
  **a true summary that answered a different question than the one asked.** Extend the method note:
  before using a metric as a *leading indicator*, verify its events actually **precede** the thing
  it is meant to predict.

### S-004 — int8 + HER2 (630 aa), the untested crash condition
- **Date:** 2026-07-19
- **Status:** **CLOSED 2026-07-19 — HOST CRASHED (4th bugcheck, `0x00020001`, 19:02:28).
  Pre-registered READING 4 fired: escalation is not gradual and the corrected-error instrument is
  invalid as a leading indicator.** Duration eliminated as the trigger; **sequence length** is the
  discriminator. See RESULTS and **F-001** below.
- **Type:** Spike. **This entry is a pre-registration** — the four readings below are fixed *now*
  so the result cannot be rationalised after the fact.

**Why this run:** every host bugcheck (3/3) occurred on **HER2, 630 aa**. Both S-002 Q1 arms used
**Trop-2, 248 aa**, so **the actual crash condition has never been reproduced**, and sequence length
changed alongside the driver update — neither the spill hypothesis nor the driver hypothesis is
cleanly isolated. HER2 is also the **flagship ADC target** the curated cache needs, so this is the
product requirement and the decisive experiment at once.

**Configuration:** **int8** (S-003) — deliberately the *lower-risk* option, since it does not spill;
`chunk_size` descending from 64 as needed; driver **596.72** held constant; WHEA counted against
recorded ISO windows (harness already emits per-fold timestamps).

**Read against the two-cap amendment (D-009 §3):** a fold completing at **`chunk 16` in four
minutes is a PASS for the cache path**, and simultaneously a FAIL for the interactive path. Do not
record a slow-but-successful fold as a failure.

**THE FOUR READINGS — fixed in advance:**

| # | Observation | Reading |
|---|---|---|
| **1** | Errors **escalate** (corrected → fatal), crash or not | **Spill/load mechanism supported**; driver hypothesis weakened |
| **2** | **Zero errors** across the run | **Mechanism substantially weakened**; driver becomes the leading explanation |
| **3** | Errors appear but **stay corrected** | Link *is* stressed by this workload, but **the new driver handles it** — both hypotheses partially right |
| **4** | **Host crashes with no prior corrected errors** | **Neither story is complete — escalation is not gradual.** This would invalidate our use of corrected-error rate as a leading indicator |

**Reading #4 is the one neither hypothesis anticipated.** Our entire model has assumed corrected
errors are the early-warning signal that precedes a fatal. If a crash arrives with a clean WHEA log,
that assumption is wrong and the monitoring approach in S-002 needs rebuilding, not just its
conclusion.

**Preconditions to record (verify, do not assert):** driver version, free VRAM, GPU compute-process
list, HVCI state, WHEA Id-17/Id-1 counts immediately before, and ISO start/end per fold.
**Everything committed and pushed before the run** — a host loss takes the session with it.
**Risk:** lower than the fp16 control (no spill), but this is the exact sequence length that
crashed the host three times. Host loss remains a plausible outcome.

- **Deep-learning justification:** HER2 is the flagship ADC target; folding its 630 aa ECD is the
  headline capability of the curated cache. This run decides whether the local tier can produce it.

---

#### RESULTS (2026-07-19) — **CLOSED. The host crashed. Pre-registered READING 4 fired.**

**Outcome: reading 4, not reading 3.** Reading 3 required errors to *"appear but stay corrected"* —
i.e. **no fatal**. A fatal occurred, and the corrected errors arrived **in the same second as the
fatal, not before it**. That is reading 4 verbatim: *"host crashes with no prior corrected errors →
neither story is complete; escalation is not gradual."* **The reading that neither hypothesis
anticipated is the one that fired** — which is precisely what pre-registering it was for.

**Fourth crash of the day, same signature:**

| # | Bugcheck | Code |
|---|---|---|
| 1 | 16:32:32 | `0x00020001` |
| 2 | 16:44:44 | `0x00020001` |
| 3 | 16:48:15 | `0x00020001` |
| **4** | **19:02:28** | **`0x00020001`** |

**What S-004 got before it died** (stdout survived; the results JSON was **corrupted to NUL bytes** —
an unflushed mid-write file, itself a signature of abrupt power loss rather than clean exit):

| | Value |
|---|---|
| Run start | 19:01:17 |
| Config | **int8**, `resident 5351 MiB`, **`spills_at_rest = False`** |
| Target | HER2 ECD `(23, 652)`, **630 aa** |
| **Chunk size** | **64** — the *first* attempt; it never reached the descent to 32/16/8 |
| **Peak VRAM** | **UNKNOWN — the record was destroyed by the crash.** No `OK` line was ever printed. |
| **Time into the fold** | **≈56 s** (fold began ≈19:01:32 after load; bugcheck 19:02:28) |
| PDB saved | none — no fold completed |

**Driver 596.72 and LM Studio are ELIMINATED as explanations** — the crash reproduced with the new
driver installed and with the GPU compute-process list verified empty at T0.

**⭐ Duration is NOT the trigger — sequence length is.** This is the one open mechanism question, and
the data now answers it:
- The **fp16 Trop-2 control** ran **five individual folds of 73.4–74.1 s each** — and **did not crash**.
- **S-004 crashed ≈56 s into a single fold** — *shorter* than folds the machine had just tolerated
  five times in a row.

**A shorter fold killed it while longer folds survived.** Single-fold duration up to ~74 s is
tolerated, so duration is eliminated. What differs is **sequence length / activation geometry**
(630 aa vs 248 aa). Spill is eliminated too: int8 does not spill at rest, and it crashed anyway.

**Cache-path verdict:** **FAIL** — but *not* on the two-cap latency criterion. It never produced a
structure at any chunk size, because the host died mid-fold. The two-cap amendment (which would have
scored a slow `chunk 16` fold as a PASS) never got the chance to apply.

### S-003 — Spike: find a configuration of `esmfold_v1` that fits under 7799 MiB
- **Date:** 2026-07-19
- **Status:** **CLOSED 2026-07-19 — PASS ON FIT** (int8 ESM-2 trunk quantization: peak 5779 MiB, no
  spill, all params on GPU). **Quality anomaly (+4.0 pLDDT) verified as real and non-degenerate**
  — deterministic across repeat folds and structurally sane — **but accuracy remains unproven**
  pending a cross-precision TM-score/RMSD comparison. Logged before the work per D-002; results and
  verification appended below.
- **Type:** Spike (time-boxed measurement). Produces a candidate configuration, not shipped code.
- **Question:** Is there a configuration of `facebook/esmfold_v1` whose **peak VRAM stays under
  7799 MiB** while **fold quality holds within a few points of the Trop-2 ECD baseline of
  mean pLDDT 70.7** (S-001)?
- **Why now:** S-001 measured the fp16 model resident at **8116 MiB** — over budget before any
  fold. S-002's (predicted, unmeasured) mechanism says the resulting spill traffic across PCIe is
  what escalates this GPU's long-standing corrected link errors into fatal ones. **S-003 produces
  the fitting configuration; S-002 Q1 then tests whether it stops the crashes.** Order matters:
  fit first, then sustained load.

**Method — test in this order, each against the same target:**
- **Baseline target:** Trop-2 / TACSTD2 ECD (`P09758`, topological range 27–274, **248 aa**),
  `chunk_size=64`, compared to **mean pLDDT 70.7** from S-001.
  1. **bfloat16** — same footprint as fp16, better numerical headroom. **Expected NOT to fit**
     (bf16 and fp16 are both 2 bytes/param); run it regardless, as a one-line change, for the
     numerical-stability/quality comparison.
  2. **8-bit quantization of the ESM-2 trunk** via `bitsandbytes`, **folding head left at full
     precision**. This is the real candidate: the ESM-2 LM is the bulk of the ~3B params, so int8
     roughly halves the dominant term.
  3. **4-bit** — only if 8-bit is insufficient. More quality risk; measure rather than assume.
- **EXCLUDED BY DESIGN — do not test CPU-offload of the trunk.** It trades VRAM for **PCIe
  traffic**, which is precisely the mechanism suspected (S-002) of escalating the link fault.
  Deprioritized *because of* what S-002 found, not for cost.

**Record per configuration:** resident VRAM after load; peak VRAM during fold; wall time; mean
pLDDT; and the pass flag **peak < 7799 MiB**. *(Note: 7799 MiB was free in S-001 run 1; runs 2–3
saw only 7043 MiB free because the desktop held more. The fixed 7799 MiB target is used as
specified, and actual free-at-start is recorded alongside so the margin is visible.)*

**Harness:** reuse the S-001 harness unchanged — parameter **placement assertion**, **spill
detection** against physical/free VRAM, **JSON written after every step** (so a host crash cannot
destroy partial results), and **pLDDT scale-trap handling** (0–1 → ×100, stated explicitly).
Each configuration runs in a **fresh process** so resident VRAM is measured clean.

- **Stop condition:** halt at the **first configuration that fits cleanly and holds pLDDT within a
  few points of 70.7**. **Do NOT proceed to HER2 (630 aa) or sustained load** — that is S-002 Q1
  and a separate, riskier test.
- **Deep-learning justification:** this *is* the model-execution engineering, and it strengthens
  the graded story rather than weakening it: *"we measured VRAM constraints on real hardware,
  quantized the LM trunk, and validated that fold quality held"* is substantially more interesting
  than *"we ran the model as shipped."* Quantization with a measured quality check against a
  baseline is legitimate DL inference work.
- **Decides:** the candidate configuration handed to S-002 Q1, and the **replacement rung one** of
  the invalidated D-006 ladder (which must be a *resident-footprint* reduction).
- **Deliverable:** results appended here; then D-006's ladder is rewritten with the measured rung
  one, and S-002 Q1 runs against the winning configuration.

---

#### RESULTS (2026-07-19) — **Status: CLOSED. A fitting configuration exists: int8 trunk quantization.**

All runs: Trop-2 / TACSTD2 ECD (`P09758`, 27–274, **248 aa**), `chunk_size=64`, fresh process each,
`physical=8151 MiB`, `free_at_start=7043 MiB`. Pass = peak < 7799 MiB **and** no spill **and**
pLDDT within 5 pts of 70.7.

| Config | resident | peak | fits <7799 | spilled | wall time | mean pLDDT | Δ vs 70.7 | verdict |
|---|---|---|---|---|---|---|---|---|
| fp16 (S-001 baseline) | 8116 MiB | 8545 MiB | ❌ | **yes** | 48.8 s | 70.7 | — | baseline |
| **bf16** | **8116 MiB** | 8544 MiB | ❌ | **yes** | 45.4 s | **70.9** | **+0.2** | **FAIL (fit)** |
| **int8 ESM-2 trunk** | **5351 MiB** | **5779 MiB** | ✅ | **no** | **26.6 s** | **74.7** | **+4.0** | **✅ PASS** |
| 4-bit | — | — | — | — | — | — | — | **NOT RUN** (stop condition met) |

**Winning configuration (reproducible recipe):**
- `BitsAndBytesConfig(load_in_8bit=True, llm_int8_skip_modules=['trunk', 'distogram_head',
  'ptm_head', 'lm_head', 'lddt_head', 'esm_s_mlp', 'esm_s_combine', 'af2_to_esm'])`,
  `device_map={"": 0}` — i.e. **quantize the ESM-2 LM only; the folding head stays full precision.**
- `bitsandbytes 0.49.2`, `torch 2.11.0+cu128`, `transformers 5.14.1`,
  revision `75a3841ee059df2bf4d56688166c8fb459ddd97a`, `chunk_size=64`.
- **Blackwell note:** bnb blockwise quantization verified working on **sm_120** before the run —
  this was a genuine feasibility risk worth checking ahead of a long job.

**Findings:**
1. **bf16 behaved exactly as predicted** — resident identical to fp16 *to the megabyte* (8116 MiB),
   because both are 2 bytes/param. It cannot fit by construction. **Keep it anyway** for numerical
   headroom: quality was unchanged (+0.2) at no cost.
2. **int8 is the fit remedy.** Resident drops **2765 MiB** (8116 → 5351) and peak lands
   **5779 MiB — comfortably under both the 7799 MiB target and the 7043 MiB actually free.**
   `spilled=False` for the first time in this project.
3. **It is also ~1.8× faster** (26.6 s vs 45–49 s). This is *indirect support* for S-002's
   spill-overhead mechanism — removing spill nearly halved wall time — but it is **not
   confirmation**; confirmation still requires the sustained-load test (S-002 Q1).

**⚠ Caveat on the +4.0 pLDDT — do not read this as "quantization improved quality."**
- **pLDDT is the model's self-confidence, not accuracy.** A higher pLDDT means the model is more
  confident, which is *not* the same as more correct. A +4.0 shift means the int8 run produced a
  **different** prediction, not a demonstrably better one.
- What the data *does* support: **quality did not degrade** by the agreed proxy, so the pass
  criterion is met honestly.

---

#### QUALITY VERIFICATION (2026-07-19) — the anomalous number, checked before it gets cited

Two holes were open in the +4.0 result: it could have been **run variance**, and a fold that
**collapses to something trivial** can score deceptively well on per-residue confidence while being
structurally wrong. Both are now closed. *(Same discipline as the WHEA correction: the surprising
number gets checked, not celebrated.)*

**1. Reproducibility — identical sequence folded twice under int8:**

| Run | wall time | mean pLDDT | CA count | NaN/inf coords | Rg |
|---|---|---|---|---|---|
| 1 | 11.9 s | **74.68** | 248 / 248 | 0 | 18.74 Å |
| 2 | 7.3 s | **74.68** | 248 / 248 | 0 | 18.74 Å |

**pLDDT run-to-run delta = 0.000; CA-RMSD between runs = 0.0000 Å.** The model is **fully
deterministic**, so **the +4.0 shift vs the fp16 baseline is a real effect of the precision change,
not run variance.** *(Hole closed.)*

**2. Non-degeneracy — the structure is genuinely folded, not trivial:**
- **Residue count exact:** 248 CA atoms for a 248 aa input — no truncation, no padding artifacts.
- **No NaN/inf coordinates** anywhere in the file (all ATOM records parsed and checked).
- **Radius of gyration 18.74 Å**, against reference bands for N=248:
  compact globular `2.2·N^0.38` = **17.9 Å** (expected) vs random coil `2.0·N^0.60` = **54.7 Å**.
  Measured sits **essentially on the compact-globular expectation** — not collapsed (which would be
  ≪12 Å) and not extended. *(Hole closed — the "confidently wrong garbage" failure mode is ruled
  out.)*
- PDBs saved (`trop2_int8_run{1,2}.pdb`, byte-identical) so the cross-precision comparison below is
  cheap to run later.

**What is now established:** the int8 configuration produces a **deterministic, structurally sane,
compact fold**, and its higher pLDDT is a genuine consequence of the precision change.

**What remains open — and why the quality claim is still bounded:** pLDDT is *still* self-confidence.
A sane, compact, confident structure can nonetheless differ from the truth. Settling *accuracy*
requires **TM-score / CA-RMSD between the fp16, bf16, and int8 structures**, ideally against an
experimental Trop-2 ECD structure. The fp16/bf16 PDBs were **not saved** during S-003, so this needs
one short re-run per precision. **Outstanding follow-up; do not claim accuracy until then.**
A plausible-but-untested reading of the direction: fp16's narrow exponent range can underflow in a
3B LM trunk, so the fp16 baseline may itself be the mildly degraded one. **Hypothesis, not finding.**

**Observation (weak, recorded as such):** the bf16 run spilled (peak 8544 > 8151 physical) for
~45 s and produced **no new WHEA errors**. Weakly consistent with S-002's mechanism being about
*sustained* traffic volume rather than spill per se — a 45-second fold may not accumulate enough.
Suggestive only; the three crashes were all on the 630 aa fold, a far longer job.

**Scope discipline:** stopped at the first passing configuration, as specified. **4-bit not run.
HER2 (630 aa) not run. Sustained load not run** — that is S-002 Q1, deliberately separate and
riskier.

**Hands off to:**
- **S-002 Q1** — run sustained load against the int8 configuration. The falsifiable prediction is
  now testable with a config that genuinely does not spill.
- **D-006** — replacement **rung one is measured**: *quantize the ESM-2 trunk to int8 (folding head
  full precision)*, with bf16 retained for the unquantized parts.
- **Follow-up:** structural comparison (TM-score/RMSD) across precisions to convert the pLDDT
  proxy into a real quality claim.

### S-002 — Spike: host stability under sustained GPU load, and a resident-footprint fix
- **Date:** 2026-07-19
- **Status:** **BOTH ARMS MEASURED 2026-07-19 — the spill mechanism is TESTED AND NOT SUPPORTED.**
  Non-spilling int8 (600 s, 83 folds) and **spilling fp16 (368 s, 5 folds)** each produced
  **0 corrected, 0 fatal, 0 bugchecks**. Restoring spill did not restore errors, so spill is not
  sufficient to trigger the fault under driver 596.72 at 248 aa. The **driver update is the leading
  explanation but is not established** — the original crash condition (HER2, 630 aa) was never
  reproduced, and a 6-minute clean window has weak power against a fault that historically appeared
  on 8 days out of ~54. Q2 superseded by S-003, which found the fitting config.
- **Type:** Spike (time-boxed investigation). Produces measurements and a decision input.
- **Why it exists:** S-001 ended in **three identical host bugchecks** (`0x00020001`
  HYPERVISOR_ERROR, byte-identical parameters, 16:32 / 16:44 / 16:48) during a 630 aa fold run
  under VRAM spill. Two questions are now open and they gate everything downstream.

**Q1 — Is the local inference tier viable at all?** (the decisive one)
> **REFRAMED after the Q1 results below.** This is no longer a generic "does it survive load"
> test — it is a **specific falsifiable prediction with a mechanism**: *spill traffic across the
> PCIe bus is what escalates this GPU's long-standing corrected link errors into fatal ones.*
> Therefore **a configuration that fits within VRAM should crash far less, or not at all.**
> Measure the fatal rate as a function of whether the workload spills — not merely whether one
> run survives.
- **The distinguishing test:** run a workload that fits *comfortably* in VRAM (well under
  7043 MiB free — e.g. a small model or a short sequence with the trunk sized to fit) under
  **sustained** GPU load for several minutes, and see whether the host stays up. Watch WHEA
  Id-17 corrected-error *rate* as the leading indicator, not just the crash/no-crash outcome.
  - **Runs clean, corrected-error rate stays low → spill-mediated escalation confirmed.** The
    resident-footprint fix (Q2) becomes the remedy that keeps the local tier alive.
  - **Crashes anyway, or corrected errors spike without spill → the link fails under GPU load
    generally.** Then the local GPU tier is not viable as designed, D-004's topology needs rework
    (not just its mitigation stack), and cache generation must happen elsewhere.
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

---

#### Q1 ANSWERED (2026-07-19) — **hardware fault: the GPU's PCIe link.** Not a memory-pressure cascade.

**Source discipline: the minidumps were NEVER READ.** `C:\Windows\Minidump` is inaccessible
without an elevated shell (we are not admin) and no debugger (`cdb`/`kd`/WinDbg) is installed.
Every finding below comes from **Windows event-log records** — WHEA-Logger (hardware errors) and
BugCheck/Kernel-Power (crashes). WHEA names the failing component directly, so it answers "what
faulted" better than `!analyze -v` would have; it does **not** by itself answer "since when",
which is why the history below is checked separately.

**What faulted — identified, not inferred:**
- All corrected errors are **PCI Express Advanced Error Reporting (AER)**, component
  *"PCI Express Legacy Endpoint"*, at bus:dev:fn `0x1:0x0:0x0`, device
  **`PCI\VEN_10DE&DEV_2D39&SUBSYS_234917AA&REV_A1`** — confirmed via `Get-PnpDevice` to be the
  **NVIDIA RTX PRO 2000 Blackwell Laptop GPU** (the inference GPU itself).
- **65 corrected AER errors today**, in bursts: **31 @ 16:32, 31 @ 16:44, 3 @ 16:48**.
- **3 × WHEA `Id 1` FATAL hardware errors** at **16:32:33, 16:44:45, 16:48:16** — one per
  bugcheck, matching the three `0x00020001` crashes 1:1.
- **No display-driver TDR** (no Event 4101 / `nvlddmkm` reset). So this is **not** a driver hang
  under memory pressure — it is link-level hardware error escalation.
- **VBS/HVCI is running** (`VirtualizationBasedSecurityStatus=2`, services `2,3,4`), which is why
  a fatal hardware error surfaces as **HYPERVISOR_ERROR**: the hypervisor is the reporting layer,
  not the culprit.

**History — checked, and it splits in two. A first-pass claim that "the fault predates the
project" was PARTLY REFUTED on inspection; both halves are recorded here.**

*Half that survives — the corrected link errors DO predate the project:*

| Date | Id 17 (corrected) | Id 1 (fatal) |
|---|---|---|
| 2026-05-27 | 3 | 1 |
| 2026-06-09 | 65 | – |
| 2026-06-13 | 3 | – |
| 2026-06-15 | 3 | – |
| 2026-07-04 | 3 | – |
| 2026-07-10 | 31 | – |
| 2026-07-14 | 40 | – |
| **2026-07-19** | **65** | **3** |

All **148 pre-today** corrected events are the *same component on the same device*:
`17 | PCI Express Legacy Endpoint | PCI\VEN_10DE&DEV_2D39&SUBSYS_234917AA&REV_A1`. So a
**corrected PCIe link problem on this GPU genuinely predates PharmFoldMDK** (7 days spanning
~7 weeks). That much is solid.

> ⚠ **Restated by F-001: true, but largely irrelevant.** This is **not** a steadily degrading link.
> It is a fault that **fires in bursts and usually recovers** — six of those seven days produced
> **zero** fatals (including 65 corrected on 06-09 with no crash). Corrected-error history says
> almost nothing about crash risk. The **18:04 / 18:06** events attributed above to the driver
> install **may equally have been a spontaneous burst — now unknowable, recorded as unknowable.**

*Half that was REFUTED — the CRASH does not predate it:*

All bugchecks in 90 days (only four):

| When | Bugcheck | Parameters |
|---|---|---|
| 2026-05-27 19:44 | **`0x00000133`** (DPC_WATCHDOG_VIOLATION) | `0x0, 0x500, 0x500, 0xfffff800c77c53c8` |
| 2026-07-19 16:32 | `0x00020001` | `0x28, 0x1, 0x29b92701, 0xfc801000` |
| 2026-07-19 16:44 | `0x00020001` | *(identical)* |
| 2026-07-19 16:48 | `0x00020001` | *(identical)* |

**The `0x00020001` signature has ZERO occurrences before today** — three today, all during
ESMFold runs. The single earlier fatal (May 27) came with a *different* bugcheck and mechanism.

**The clean split (213 corrected / 4 fatal out of 217):**

| | Corrected (Id 17) | Fatal (Id 1) |
|---|---|---|
| **Before today** | **148** across 7 days | **1** (May 27) |
| **Today** | **65** | **3** |

**Synthesis — three parts, all load-bearing:**

1. **The link fault is pre-existing and independently evidenced.** Corrected AER errors on this
   exact device occur on 7 days back to 2026-05-27 — including 65 on 06-09 and 40 on 07-14, days
   with no ESMFold anywhere near this machine. **The May 27 fatal is the key corroboration: the
   link can go fatal without ESMFold**, so the weakness is real and independent of us.
2. **The workload is an accelerant, not the cause. ⚠ THE RATE IS THE EVIDENCE — NOT THE RAW
   COUNTS.** **One fatal in eight weeks of ordinary use versus three in under twenty minutes**
   ≈ **four orders of magnitude**. Read the counts alone ("217 errors, going back to May →
   pre-existing, unrelated to us") and you reach the wrong conclusion — *which is exactly what
   happened in the first draft of this entry.* The counts are compatible with both hypotheses;
   only the **rate under load**, bucketed by **severity**, separates them. Neither "pre-existing
   hardware, unrelated to our workload" nor "our workload broke the machine" is correct: this is
   the **latent-fault-triggered** reading.
3. **Mechanism — ⛔ TESTED AND NOT SUPPORTED (2026-07-19; both arms measured, see Q1 CONTROL
   RESULTS).** Restoring spill did **not** restore the errors, so this chain is *undermined*, not
   confirmed; the driver update is now the leading explanation, though itself unestablished.
   The proposed chain was
   *spill → sustained PCIe traffic → corrected errors escalate to uncorrected*: the fp16 model
   overruns VRAM (resident 8116 MiB vs 7043 MiB free; peak 8545 MiB vs 8151 MiB physical — i.e.
   **~0.4 GB beyond total physical, ~1.1–1.5 GB beyond what was actually free**), and WDDM services
   that overrun by shuttling memory across the PCIe bus. This is **plausible and fits the data, but
   it is not established** — it connects S-001 to the crash rather than competing with it, and
   **S-002 Q1 is what confirms or refutes it.** Do not cite it as a finding until then; when
   measured, update this clause from *predicted* to *measured*.

**Falsifiable prediction (this is now S-002 Q1, with a mechanism instead of a generic load test):**
*a configuration that fits within VRAM should crash far less — or not at all — because it does not
generate the spill traffic.* If it holds, the resident-footprint fix is not merely a performance
optimization; it is the thing that keeps the local tier alive. If it fails, the link fails under
GPU load generally and the tier is done on this machine.

---

#### Q1 RESULTS — non-spilling arm (2026-07-19) — **prediction held; attribution confounded**

**Test:** int8 configuration (S-003), **Trop-2 ECD 248 aa only — deliberately NOT HER2**, folded
repeatedly under continuous load.

**Windows stated explicitly — containment, not assumed alignment:**

| Window | Start | End | Source |
|---|---|---|---|
| **WHEA query window** | **18:14:27** (T0, recorded to file) | **18:33:30** (T1, query clock) | recorded |
| **Fold window** | **≈18:17:05** | **≈18:27:05** (600.1 s) | **reconstructed** |

The WHEA window **strictly contains** the fold window, with ~2.6 min of margin before and ~6.4 min
after. Zero events across the *superset* therefore implies zero during folding — a stronger claim
than aligning two windows, and it needs no alignment assumption.

⚠ **Harness gap (fix before the fp16 control):** `s002_q1.py` recorded **only relative elapsed
times** (`elapsed_s`, `time_s`) and **no absolute timestamps**. The fold window above is therefore
*reconstructed* from file mtimes — the results JSON is rewritten after every fold, so its last write
(18:27:04.86) marks the end of the final fold, minus `total_elapsed_s = 600.1 s` for the start.
That reconstruction is sound but it is an inference, not a record. **The control harness must emit
ISO-8601 start/end timestamps per fold** so the fold and WHEA windows are *shown* to correspond.

| Measure | Value |
|---|---|
| Folds completed | **83 consecutive** |
| Sustained duration | **600.1 s** (10 min), GPU 99% util, 2190 MHz, 81 °C, ~75 W |
| Resident / peak VRAM | 5351 / **5779 MiB** — pinned, `spills_at_rest = False` |
| mean pLDDT | 74.68 on **every** fold (deterministic, as S-003 verification found) |
| **WHEA Id 17 (corrected) in window** | **0** |
| **WHEA Id 1 (fatal) in window** | **0** |
| **Bugchecks / unexpected shutdowns** | **0** — host survived |

**Null result verified, not assumed:** `Get-WinEvent` throws when it matches nothing, so an empty
result is indistinguishable from a broken query. A **control query over the same day returned 74
events** (71 corrected + 3 fatal), confirming the query works; the **last WHEA event of any kind was
18:06:27, before the window opened.**

> ⛔ **VOID — see F-001 (instrument correction).** The corrected-error comparison below measures
> **crash debris, not precursors**: the fatal is logged in the *same second* as the corrected errors
> in all four crashes, and six historical burst days produced 65/40/31 corrected errors with **zero**
> fatals. *"65 corrected in the crashing window vs 0 in clean runs"* is **three crash events versus
> zero, double-counted.* **The valid measure was always the fatal count: 4 vs 0.** Text retained
> for provenance.

**Rate contrast — phrased to what the data supports:** *the crashing window* (16:32–16:48) logged
**65 corrected + 3 fatal**; the int8 non-spilling arm logged **0 + 0** across 10 min of heavier,
*continuous* utilisation.

⚠ **Do not phrase the baseline as "the fp16 workload produced 65."** That 16-minute window contains
**three hard reboots and their recovery**, and device re-enumeration at boot plausibly generates
corrected AER events of its own. The per-minute clustering (31 @ 16:32, 31 @ 16:44, 3 @ 16:48) sits
right on the crash timestamps and is equally consistent with errors *preceding* the crash (fold
traffic escalating) or *following* it (reboot artifacts) — the log cannot separate those.
**"The crashing window logged 65" is defensible; "the fp16 workload produced 65" is not.** The
direction of the contrast is unaffected; its attribution is weaker than a raw reading suggests.

**⚠ CONFOUND — this does NOT yet establish causation.** The **NVIDIA driver was updated during this
session** (`595.71 / 32.0.15.9571` → **`596.72 / 32.0.15.9672`**), and PCIe link handling is driver
territory. Worse for attribution, the timing is adjacent: the last 6 corrected errors occurred at
**18:04 and 18:06** — plausibly the device reset from the driver installation itself — and **nothing
at all** afterwards. So the zero-event window begins essentially *at* the driver change. **Two
explanations remain live: (a) no spill ⇒ no escalation, or (b) the new driver fixed the link
handling.** The observed data cannot separate them.

---

#### Q1 CONTROL RESULTS (2026-07-19) — ⛔ **THE MECHANISM PREDICTION FAILED**

**Test:** sustained **fp16** (the spilling configuration), **new driver 596.72 held constant**,
Trop-2 ECD 248 aa, 5-minute window. Windows **recorded, not reconstructed** (harness gap fixed):
WHEA **18:44:41 → 18:52:12** strictly contains folds **18:45:31 → 18:51:39**.

| | int8 arm | **fp16 CONTROL arm** |
|---|---|---|
| Spilling | no — peak 5779 MiB | **yes — resident 8116 > 7043 free; peak 8544 > 8151 physical** |
| Duration | 600 s, 83 folds | **368 s, 5 folds** |
| Per-fold time | 7.2 s | **73–74 s** (10× penalty from thrashing) |
| mean pLDDT | 74.68 | 70.69 (matches the 70.7 fp16 baseline) |
| **WHEA corrected (Id 17)** | **0** | **0** |
| **WHEA fatal (Id 1)** | **0** | **0** |
| **Bugchecks** | **0** | **0** — host survived |

**The prediction was:** restoring spill should restore the corrected errors. **It did not.**
Continuous spill — a *larger* dose of the suspected trigger than the intermittent spill that
preceded three host bugchecks — produced **zero events of any severity**.

> ⚠ **Restated by F-001:** this arm's "zero corrected errors" reduces to **"no crash"**, which host
> survival already established independently. **The refutation below still stands — but on the
> fatal count, not the corrected count.** S-004 later strengthened it: HER2 crashed at int8 with
> **no spill at rest**, eliminating spill again by a different route.

**Therefore: the spill → PCIe-traffic → escalation mechanism is NOT SUPPORTED by this test.**
It moves from *predicted* to **tested and undermined** — not to *confirmed*. The leading explanation
for the cessation is now the **NVIDIA driver update (595.71 → 596.72)**, which is driver-side PCIe
link handling, exactly where such a fix would live.

**⚠ But "the driver fixed it" is NOT established either. Two limits:**
1. **The original crash condition was not reproduced.** All three bugchecks were on **HER2, 630 aa**.
   Both arms today used **Trop-2, 248 aa**. Sequence length changed *alongside* the driver, so this
   pair of runs cannot isolate the driver any more cleanly than it isolates spill.
2. **Weak power against a bursty fault.** Corrected errors historically appeared on **8 days out of
   ~54**, in clusters — most days logged zero. A 6-minute clean window is thin evidence of absence.
   *Absence of errors here is not evidence the fault is gone.*

**What this does and does not change:**
- **The S-003 int8 result stands entirely on its own merits** — it fits (5779 MiB peak), it is
  **10× faster** than fp16 under these conditions (7.2 s vs 73–74 s), and quality holds. None of
  that depended on the crash hypothesis.
- **The local tier looks better than feared** — ~16 minutes of combined sustained GPU load today
  with zero errors and no host loss — but that is *encouraging*, not *cleared*.
- **The decisive remaining test is HER2 (630 aa) under the new driver**, since that is the untested
  condition and the one that actually crashed. Under the **two-cap amendment** (D-009 §3) the
  sensible next run is **int8 + HER2**: it is simultaneously the *product* requirement (the flagship
  ADC target for the cache) and the *lower-risk* option (no spill), and a multi-minute fold at
  `chunk 16` would be a **PASS** for the cache path.

**Superseded:** the paragraph below was written before the control ran and predicted that errors
would return. Retained for provenance — it is the hypothesis this control tested and undermined.

**What was expected to close it — the fp16 sustained control** (now run, result above): hold the
**new driver constant**, restore **spill** by running sustained fp16, and see whether corrected
errors return. Errors return ⇒ spill is the mechanism (a). Still clean ⇒ the driver was the fix (b).
**Risk priced in:** sustained fp16 is *continuous* spill, a larger dose of the suspected trigger than
the intermittent spill of the HER2 folds that preceded the three crashes — **this experiment is
designed to reproduce the fault, so host loss is a likely outcome, not a surprise.** Mitigations:
**5-minute window rather than 10** (halves exposure, should discriminate as well), and the harness
writes per-fold JSON incrementally so a crash cannot destroy the record.

**Precondition deviations recorded (verified, not asserted):** free VRAM at start was **7899 MiB**,
not 8151 (8151 is *total*; 252 MiB reserved). GPU **compute** process list was empty (0 MiB) and
only our python held the GPU during the run — but **`ollama` and `ollama app` were running as
processes** throughout; they never claimed GPU memory, so they did not confound this arm.
HVCI/VBS confirmed still enabled (`VirtualizationBasedSecurityStatus = 2`, services `2,3,4`).

**Reliability floor (a design input, not a disqualifier).** The May 27 fatal happened in ordinary
use with no ESMFold involved. So **even a perfectly-fitting configuration will occasionally take
this machine down** — the floor is roughly *one host loss per several weeks of normal use*, and it
is now **measured rather than hypothetical**. This is precisely what D-009 §1's `jobs` table,
`claimed_at` + `worker_id`, `attempts`, and **30-minute stale-claim reaping** were designed for:
a worker that dies mid-job without warning. That design was written against an assumed unreliable
worker; it now has a number behind the assumption. **No redesign needed — the assumption was
right.**

**Named unknowns (not glossed):** what workload produced the 06-09 / 07-10 / 07-14 error bursts is
unknown; whether repair or replacement resolves it is unknown; whether a fitting configuration
drops the fatal rate to zero (versus merely reducing it) is **exactly what Q1 must measure**; the
minidumps remain unread.

**Provenance of this claim — it reversed direction twice, and the intermediate versions were
stated confidently and were wrong. A future reader should see the path, not just the destination:**

| Version | Source claimed | Conclusion | Why it was wrong |
|---|---|---|---|
| v1 | "read the minidumps" | GPU PCIe fault | **The minidumps were never read** — no admin, no debugger. The source was the Windows event log. |
| v2 | WHEA event **counts** (217 over 90 days) | "Pre-existing hardware, unrelated to our workload" | Counts were not bucketed by **severity**. 213 were *corrected*; only 4 were *fatal*. The fatal signature had zero prior occurrences. |
| v3 (current) | WHEA events **bucketed by severity**, plus all 4 bugcheck codes/params | Latent fault + workload accelerant; mechanism predicted, not measured | — |

**The failure mode both times was accepting a summary instead of returning to the raw data.**
`params_all_on_cuda=True` was a true summary that missed spill; "217 WHEA events since May" was a
true summary that missed severity. Each was caught only by re-deriving from the underlying records.

**⚠ Git history carries a superseded claim that cannot be rewritten.** PR #5 squash-merged as
commit **`5ad4c9b`** with the title:

> `docs: S-002 Q1 answered — GPU PCIe link fault (pre-existing hardware) (#5)`

That title was written **before** the correction, and its parenthetical **"(pre-existing hardware)"
is superseded by this entry** — the accurate reading is *latent pre-existing link weakness that this
workload accelerates*, per the provenance table above.

Two details matter for anyone auditing history:
- The squash **body** does contain all four constituent commit messages *including* the retractions,
  so a reader who opens the full commit sees the correction sequence. But **`git log --oneline`
  shows only the title**, and the body's *first* message also states the superseded
  "the fault predates the project / our load did not cause it" framing before later messages walk
  it back. History read top-down is therefore misleading in isolation.
- It **cannot be corrected in place**: `main` is branch-protected (D-008 — required `test` check,
  PR-only, `enforce_admins`), so rewriting history would require a force-push that protection
  forbids, and rewriting merged history would be the wrong remedy regardless.

**Authority rule: where commit metadata and this log disagree, THIS ENTRY WINS.** Commit titles are
not decision records; `docs/README.md` is.

**Adjacent audit (2026-07-19):** `git log -p --all -- .vscode/settings.json` confirms the file
existed in exactly two commits — added in `5ad4c9b`, removed in `a317a73` — and only ever contained
a 10-line `files.exclude` block (`.git`, `.svn`, `.hg`, `.DS_Store`, `Thumbs.db`, `.mule`).
**No credentials, tokens, or sensitive paths entered history.** No remediation required.

**Suggestive but NOT conclusive:** at idle the link reports `pcie.link.gen.current=1` (max 5) and
`width=8` (max 16). Consistent with AER-driven downtraining — **but confounded**, because NVIDIA
GPUs idle at low link speed for power management and some laptops are wired x8. Not offered as
proof; the 217 AER records are the solid evidence.

**Conclusions:**
1. **The local tier is NOT killed outright — it is conditional.** The mechanism in §3 above is what
   keeps it alive: if spill traffic mediates the escalation, then a configuration that fits in VRAM
   may not trigger the fault at all. **A resident-footprint fix is therefore not just an
   optimization — it is the candidate remedy**, and it must be measured before writing the tier
   off. (An earlier draft of this entry concluded "not viable regardless of the memory fix"; that
   inference was wrong — "a memory fix cannot repair a link" does not imply "a memory fix cannot
   avoid triggering it.")
2. **This is still also a platform problem.** Owner actions worth taking in parallel: update NVIDIA
   driver (595.71 current) and BIOS/EC firmware, and open a vendor support conversation — 148
   corrected PCIe AER errors over seven weeks plus a fatal on a machine this new is warranty
   territory. **Whether repair/replacement resolves it is UNKNOWN**; do not plan the project around
   that outcome either way.
3. **Project consequence — de-risk without abandoning.** Cache generation (D-009 §3 (A)) can move
   to **different compute** (cloud GPU / Colab / cluster) to remove the schedule dependency on
   both the hardware outcome *and* the Q1 result; a rented ≥16 GB GPU additionally makes the S-001
   fp16 non-fit stop binding, collapsing two problems into one. But this is **de-risking, not a
   verdict on the local tier** — Q1 may well restore it. Either way this stays **inside the
   D-004 §5 boundary** and is **not** a retreat to AlphaFold retrieval; D-003's graded DL claim is
   unaffected, since ESMFold still runs.
4. **Q2 (resident-footprint fix) is deferred, not cancelled** — whatever compute hosts the cache
   build still needs a configuration that fits, and the fp16-does-not-fit finding (S-001) travels
   with us to any 8 GB-class device. On a ≥16 GB device it may simply not bind.
5. **Minidumps remain unread** (need an elevated shell). Now low value — WHEA already identified
   the component. Only worth revisiting if the vendor asks for them.

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

##### AMENDMENTS (2026-07-21) — settled while implementing §1 in PR A

The original §1 shape left three things underspecified. They surfaced when the queue
semantics were written as tests (log-leads-code checkpoint), and are settled here **before**
the implementing code. Each is expressed in code as an assertion of the chosen behaviour, so
a later change to any of them turns a test red rather than passing silently.

**Amendment 1 — retry budget is 3, then terminal `failed` with a distinguishable reason.**
§1 called `attempts` a "retry budget" but never stated the budget, so a job whose worker keeps
vanishing would be reaped and re-dispatched without limit. The cap is **3 attempts**
(`MAX_ATTEMPTS = 3`), derived from measured host behaviour, not a round number:

- The host reliability floor is roughly **one fatal bugcheck per several weeks** of ordinary
  use (S-002/F-001), independent of this project. A job must survive one host loss and still
  complete — one retry does that, two is comfortable margin.
- A **630 aa fold is 4-for-4 fatal** (S-004): a deterministic host-crasher. Every dispatch of
  such a job costs a host crash, so the cap must be low enough that a bad job cannot take the
  machine down repeatedly. Three attempts = the original dispatch plus **at most two
  retry-induced crashes** before the job stops asking.

  The two failure classes pull in opposite directions (survive transient loss vs. don't feed a
  deterministic crasher); 3 is the smallest cap that serves the first without over-serving the
  second.
- **The reaped-out terminal state must be distinguishable from an explicit failure.** Same
  `failed` status, but the `error` carries a machine-greppable marker (`[reaped-out] …`)
  stating the budget was exhausted with no error ever reported. A job that died three times
  without a worker ever reporting why is a different diagnostic situation, at 3 a.m., from one
  that reported a real exception — the record has to tell them apart.

  Mechanics: on each reap, `attempts` increments; if it reaches `MAX_ATTEMPTS` the job goes
  terminal `[reaped-out]` instead of returning to `pending`. So a persistently-vanishing job is
  dispatched at most 3 times.

**Amendment 2 — an explicit `fail` is terminal and does not touch `attempts`, and the
asymmetry with reaping is principled, not incidental.** An explicit fail means the worker
**caught its own error and survived to report it** — and a caught error is usually
deterministic (bad sequence, malformed input, OOM on an oversized target), so retrying
reproduces it. A stale reap means the worker **vanished** — usually environmental (sleep,
network, host bugcheck), where retrying is exactly right because absence is uninformative.
Therefore reaping retries and explicit failure does not: *reaping retries because absence tells
you nothing; explicit failure doesn't because the worker already told you what's wrong.* If
explicit failures were retried, an above-ceiling sequence would trigger three host crashes
instead of one.

  Consequence for the record, not just for retry semantics: `attempts` is **preserved, never
  zeroed**, on an explicit fail. A job reaped twice and then failing explicitly must read
  `attempts = 2` — that history is part of the diagnosis.

**Amendment 3 — FIFO is contract, stated, not inferred from an index.** §1 gave
`jobs(status, created_at)` as an index "for the claim query." An index makes an ordering cheap;
it does not guarantee one — a claim query with no explicit `ORDER BY` returns whatever the plan
yields, and that can change silently under a plan change. The claim query therefore **must
carry an explicit `ORDER BY created_at`** (with `id` as a deterministic tiebreak), and
oldest-pending-first is now a promised behaviour of `claim`, not a hopeful consequence of
index choice.

**Amendment 4 — the `analysis_id` FK is deferred, and what closes the gap is stated in
enforceable terms.** §1 specifies `analysis_id INTEGER FK → protein_analyses(id)`, but
`protein_analyses` does not exist and PR A is scoped to the queue. It is **not** created here.
The reason is not only PR size: a `protein_analyses` built now, in a queue PR, would be shaped
*for the FK's convenience* rather than from Database Plan v2's column-level decisions — and once
a table exists in an applied migration its shape is inertial, so the result would be a real FK
pointing at a wrong-for-the-wrong-reason table, then a later migration spent correcting it. A
named gap in a small PR is cheaper than a wrong table in the chain. The single-writer point also
holds: nothing enqueues jobs yet, so no code path can currently orphan an `analysis_id`.

So in PR A `jobs.analysis_id` is a **plain indexed integer with no FK constraint**.

- **Closure condition, in enforceable terms:** the migration that creates `protein_analyses`
  **adds the `analysis_id` FK constraint in that same migration**. Not "later," not "when
  convenient" — a deferred constraint with no stated closure is how a nominal integer becomes a
  permanent one.
- **Detectable, per the standing pattern:** `test_analysis_id_has_no_fk_yet` asserts the column
  currently carries no foreign key. When the FK lands, that test goes **red** and forces this
  amendment to be closed out deliberately rather than the gap being left open or silently
  half-satisfied — the same discipline as the `[reaped-out]` marker: name the transition and
  make it detectable.

**Seam note carried from D-012 §4, made sharper by these amendments.** The staleness *decision*
(`is_stale`) is pure arithmetic and is really covered. Amendments 1–3 make `complete`, `fail`,
and `reap_stale` (including the budget cap and the terminal-vs-requeue branch) **portable
status-transition logic** with no Postgres-specific construct — so they execute, for real,
against the SQLite test fixture. That shrinks the unproven surface to exactly one thing:
`claim`'s **atomicity** under `SELECT … FOR UPDATE SKIP LOCKED`. The seam stops being "where the
queue lives" and becomes specifically **where `SKIP LOCKED` lives** — the honest irreducible
minimum, provable only by the still-absent Postgres integration job (D-012 §5).

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

---

##### STRUCTURAL AMENDMENT (2026-07-19): there are **TWO caps**, not one

**The problem this fixes:** D-006 and S-001 used a single sequence-length cap, and treated
**`chunk ≤16` as a FAIL** (*"severe chunking ⇒ ceiling below this length"*), alongside a
**`time < 120 s`** criterion. Those encoded an **interactive-latency assumption** — a user waiting
on a live fold cannot tolerate minutes, and heavy chunking means slow. **Cache-first (this section)
makes that assumption irrelevant for Iteration 1.** An offline cache build does not care whether a
fold takes four minutes; it runs unattended.

**Decision — split the cap into two numbers with two different criteria:**

| | **Interactive cap** | **Cache-build cap** |
|---|---|---|
| **Applies to** | live user-submitted folding (deferred to Iteration 1.5+) | offline pre-fold of the curated ADC target DB (**Iteration 1**) |
| **Bounded by** | **latency** — the user is waiting | **memory fit + host stability** only |
| **Criteria** | `chunk ≥ 32` **and** wall time `< 120 s` **and** no spill | **no spill** **and** host survives. Wall time is **not** a criterion. `chunk = 16` or `8` is **acceptable**. |
| **Status** | unmeasured | unmeasured |

**Consequence — read HER2 correctly when it is finally folded:** a HER2 ECD (630 aa) fold that
completes at `chunk 16` in four minutes without spilling is a **PASS for the cache path**, and
simultaneously a **FAIL for the interactive path**. Under the old single-cap criteria it would have
been recorded as a plain failure. **This is logged before HER2 runs precisely so the result is not
misread when it arrives.**

**Why this changes the product, not just the diagnosis:** it means the curated target database can
include **large ECDs that would never be viable interactively** — HER2 (630 aa) is the flagship ADC
target, and cache-first is what makes it reachable. The two-cap split converts a latency constraint
into a *scope* decision instead of an exclusion.

**Scoping note for D-006/S-001 criteria:** their `chunk ∈ {64,32}` and `time < 120 s` conditions are
hereby scoped to the **interactive** cap only. They were never valid criteria for the cache path.
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
- **Status:** ⚠ **INVALIDATED AT RUNG ONE (2026-07-19) by S-001 — REPLACEMENT RUNG ONE NOW MEASURED
  (S-003).** The ladder below assumes fp16 makes the model *fit at rest*; it does not
  (resident 8116 MiB vs 7043 MiB free). Rungs 2–6 reduce **activation** memory and cannot fix a
  **resident-weight** overrun. Do not implement this ladder as written.
  **New rung one (measured, S-003): quantize the ESM-2 LM trunk to int8 via `bitsandbytes`, leaving
  the folding head at full precision** → resident 5351 MiB, peak 5779 MiB, **no spill**, ~1.8×
  faster, pLDDT 74.7 vs 70.7 baseline. **Rung two: bf16** for the unquantized parts (same footprint
  as fp16, better numerical headroom, quality unchanged at +0.2). Chunking / length caps / ECD
  scoping remain valid as *activation*-memory rungs **below** these. Ladder retained verbatim below
  for the record; rewrite pending S-002 Q1 confirmation under sustained load.
  **⚠ ALSO RE-SCOPED (D-009 §3 two-cap amendment, 2026-07-19): this entry's `chunk ≥ 32` and
  `time < 120 s` conditions are INTERACTIVE-path criteria only.** They encoded a latency assumption
  that cache-first makes irrelevant. For the **offline cache build**, `chunk = 16` or `8` and a
  multi-minute fold are **acceptable**; the only criteria there are *no spill* and *host survives*.
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
- ~~**Prod DB choice**~~ — **resolved in D-012: Postgres-first**, from the first migration;
  the SQLite-on-Volume prototype path is closed, not deferred. The **test** DB remains SQLite
  per D-005, which D-012 §3–§5 turns from a footnote into a named, structural exposure.
- **Embedding model** for semantic search (which encoder, `vector(384)` assumed).
- ~~**Postgres integration test job**~~ — **BUILT in D-017.** The `postgres` CI job stands up a
  real Postgres 16 service container, applies migrations with `alembic upgrade head` (not
  `create_all`), and exercises `claim`'s `FOR UPDATE SKIP LOCKED` atomicity for the first time.
  What was "the single largest coverage hole" is closed. **Residual, narrower:** the job is not
  *yet* a branch-protection required check (owner action, deferred until proven stable — D-017),
  and pgvector **type resolution** through the `extensions` schema is still unexercised (no vector
  column yet; the job switches to a pgvector image when the first vector-column migration lands).
- **pgvector `extensions`-schema resolution** — a `vector(384)` column actually resolving via
  env.py's `search_path` seam, against a populated `extensions` schema, on real PG. Deferred to
  the first vector-column migration (D-017 residual; env.py seam already in place, D-012 §5a).
