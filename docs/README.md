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
- **Postgres integration test job** for pgvector/Postgres-specific paths (D-005 gap).
  **Sharpened by D-012 §5 and now the single largest coverage hole in the project:** the
  queue-claim path (`SELECT … FOR UPDATE SKIP LOCKED`) *cannot* execute on SQLite — it is a
  syntax error, not an unsupported feature — so it has never run and will not run until this
  job exists. D-012's repository seam makes that legible; it does not fix it. Template is the
  JARVIS precedent: a throwaway Postgres service container in the gate, migrations applied,
  the real implementation exercised.
