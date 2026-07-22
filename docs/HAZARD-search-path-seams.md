# Carried hazard — the `search_path` seams are TWO seams, and only one is being closed

**Recorded:** 2026-07-22
**Raised by:** the Builder, while scoping D-026's enqueue test suite
**Status:** one seam closing with D-026; one remains open with a named future trigger

---

## Why this is a separate document

"The `search_path` seam" has been carried as a single line item since the 07-21 close-out. It
is **two different seams that share a name**, and the D-026 enqueue work closes one of them
while leaving the other untouched. Left as one line, the first seam's green would read as
coverage of both — which is the precise failure this project's test discipline exists to
prevent.

---

## Seam 1 — the app-runtime connection/commit path

**What it is.** `env.py`'s connection sets `search_path` and is proven against real Postgres.
The **application's** connection is a different connection with its own configuration, and had
never run.

**The bug class it guards.** A write that appears to succeed and silently rolls back — a green
insert with no row behind it. This is the `env.py` bug class that the Postgres integration job
has already caught twice in the migration chain.

**How D-026 closes it.** The real-Postgres track (`pytestmark = pytest.mark.postgres`, the
`pg_engine` fixture) writes `protein_analyses` / `jobs` / `ranking_runs`, then **re-reads in a
fresh connection** to prove the rows actually committed. A fresh connection is the whole point:
reading back on the writing connection would pass on a transaction that never committed.

**Why this cannot be hermetic.** SQLite has no schemas, so the seam does not exist there. A
hermetic test of this behaviour would pass and prove nothing.

**Status after D-026: CLOSED**, for this bug class.

---

## Seam 2 — pgvector's `extensions`-schema type resolution

**What it is.** The `vector` type lives in the `extensions` schema and resolves through
`search_path`. If a connection's `search_path` does not include it, a statement touching a
`vector` column fails to resolve the type.

**Correction (2026-07-22, DEP-005): the CI image is pgvector, not stock `postgres:16`.** An
earlier version of this note (and D-032) implied the `postgres` job runs a stock image with no
vector column. That is **wrong**: D-019 switched the CI image to `pgvector/pgvector:pg16`, and
migration `0002` creates `analysis_embeddings` with a bare `vector(384)` column that resolves
only through env.py's `SET search_path TO public, extensions`. So the extension/type-resolution
path **is exercised in the `postgres` job at migration time** — a failure to resolve would red
`alembic upgrade head`. Seam 2 is therefore better covered than this note originally claimed.

**What is therefore still OPEN — and it is not CI coverage of type resolution.** Two things:
1. **Production role privileges.** `CREATE EXTENSION vector` commonly needs elevated rights, and
   the Fly managed cluster's role is not CI's. The first production migration is where this is
   discovered — which is exactly why DEP-005 runs it **supervised, by hand, before the first
   deploy**, rather than via an unattended `release_command`.
2. **The application's runtime read/write of a vector column.** `protein_analyses`, `jobs`, and
   `ranking_runs` reference no vector column, so D-026's enqueue tests and the D-031 transport
   tests say nothing about the *app connection* resolving `vector` at query time. That is the
   original runtime half of this seam.

**Status: OPEN**, on both counts above — while the DDL/type-resolution path is now CI-covered.

**Named trigger — unchanged.** The first application code that writes or reads
`analysis_embeddings` — expected to be the scorer's feature/embedding persistence, downstream of
D-027 — takes on the runtime half of this seam and must carry its own real-Postgres test. Naming
the trigger is what stops the hazard being silently outlived: whoever builds that write inherits
the obligation, rather than it remaining everyone's and no one's.

---

## The general principle this instance illustrates

**A green is a claim, and a claim has a scope.** The useful discipline is not "did the test
pass" but "what exactly does this passing test assert, and what does a reader
reasonably-but-wrongly infer from it passing." Here the wrong inference is available and
attractive: *the enqueue tests hit real Postgres, so the `search_path` thing is handled.*

This was caught by the Builder narrowing its own coverage claim about a test it had just
designed — which is harder than catching someone else's overclaim, and worth recording as a
practice rather than only as a finding.
