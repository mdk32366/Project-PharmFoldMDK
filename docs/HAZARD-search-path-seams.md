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
`search_path`. If the application's `search_path` does not include it, a query touching a
`vector` column fails to resolve the type.

**What D-026 does NOT prove about it.** `protein_analyses`, `jobs`, and `ranking_runs`
**reference no vector column**. So the enqueue tests exercise the connection/commit path on real
Postgres and say nothing whatever about type resolution. A green D-026 suite is *not* evidence
that the pgvector seam works.

**Status: OPEN.**

**Named trigger — the obligation is inherited, not floating.** The first application code that
writes or reads `analysis_embeddings` — expected to be the scorer's feature/embedding
persistence, downstream of D-027 — takes on this seam and must carry its own real-Postgres
test. Naming the trigger is what stops the hazard being silently outlived: whoever builds that
write inherits the obligation, rather than it remaining everyone's and no one's.

---

## The general principle this instance illustrates

**A green is a claim, and a claim has a scope.** The useful discipline is not "did the test
pass" but "what exactly does this passing test assert, and what does a reader
reasonably-but-wrongly infer from it passing." Here the wrong inference is available and
attractive: *the enqueue tests hit real Postgres, so the `search_path` thing is handled.*

This was caught by the Builder narrowing its own coverage claim about a test it had just
designed — which is harder than catching someone else's overclaim, and worth recording as a
practice rather than only as a finding.
