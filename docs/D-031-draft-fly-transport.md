### D-031 — The Fly transport: HTTP realization of the loop's discovered protocol
- **Date:** 2026-07-22
- **Status:** **Proposed**
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
  authenticates, the id labels. Per-worker credentials are a change to make when a second worker
  exists, with its own entry.

---

- **⚠ OPEN — upload size, and it is not a detail.** PAE is an **L×L matrix**. For the largest
  cohort targets (1652–2213 aa) a JSON-encoded PAE is on the order of **tens of megabytes**,
  over a residential uplink, inside the 60-minute provisional lease (D-030). Three things follow
  and none is ruled:
  - whether PAE is uploaded **at all** for large targets, or computed-and-discarded
  - whether artifacts are **compressed** in transit (they are highly compressible text)
  - the endpoint's **max body size**, and what a rejection does to the loop

  **This is the item most likely to surface as a surprise during the first large rental fold** —
  it is simultaneously a cost question (lease expiry → re-fold), a correctness question (partial
  upload), and a coverage question (a target whose PAE is absent is not identical to one whose
  PAE was never produced — `worker/runner.py` already treats `pae` as optional, and D-027
  rejected a PAE-derived feature for exactly this heterogeneity). **Ruling it needs a measured
  PAE size, which the first large fold will produce.** Recorded as blocking nothing today and
  named so it cannot arrive unexamined.

  > **Builder note (verified against the code, 2026-07-22).** PAE is **not** optional-in-practice
  > for this cohort: `worker/runner.py:200` emits it whenever the model output contains
  > `predicted_aligned_error`, which `facebook/esmfold_v1` (the pinned revision) always does —
  > `dtype`/`chunk_size` do not gate it. So "computed-and-discarded" is a real *choice* to rule,
  > not a possibility the model might spare us. And the size is **understated**: an L×L Python
  > list for a 2213 aa target is ~4.9M floats ≈ **75–100 MB** of JSON, not tens. This strengthens
  > the item toward compression or a large-target PAE policy rather than a bigger body limit.

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

- **Deep-learning justification:** indirect and structural, same as D-030. This is the last
  component between a reviewable manifest and executed inference; its correctness is what makes
  fold provenance trustworthy downstream. A job marked complete with no structure behind it
  corrupts the coverage line (D-024) and the extractor's inputs (D-027) at once, and neither
  would show as an error — only as a target that quietly has no data.

- **Consequences / follow-ups:**
  - **`app/` is created by this entry** — the first application code on Fly. It is also the
    first component the `search_path` seam applies to *as a service* rather than as a script.
  - **Upload size ruling** is deferred to a measurement, named above.
  - **Per-worker credentials** when a second worker exists.
  - **Lease heartbeat** (D-030's flag) lands as a fifth route, not by widening an existing one.
  - **Nothing here is deployed to Fly until the full suite passes**, functional and user tests
    both.
