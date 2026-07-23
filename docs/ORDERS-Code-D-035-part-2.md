# Orders for Code — D-035 Part 2: local persist + the fifth route + the upload change

**Session:** 2026-07-23. **Planner:** Claude. **Builder:** Code.
**Prerequisite:** D-035 part 1 merged (timeout, amendments, ARCHITECTURE row).
**Entry:** `D-036` — the fifth route needs its own entry (D-030's discipline). Land it first.

**⚠ These three changes are ONE PR. They do not land separately.**
Removing PAE from the upload before the local write and the transfer route exist *is* the
silent-drop window — a rental fold's PAE would live only in `FoldResult.pae` and be discarded on
the next claim. The Planner's original §4 asserted local persistence already happened; **it does
not** (verified: `runner.write_artifacts` has no production caller). That false premise is the
reason this is an atomic unit rather than three tidy commits.

---

## 0. `D-036` — the PAE transfer route, ruled before the code

D-030: *"a fifth route, not by widening an existing one."* The entry must settle:

- **Route:** `POST /jobs/{job_id}/pae`, bearer-guarded like the other four.
- **Body:** the gzipped PAE, same wire form the upload route used to accept.
- **Semantics:** writes the Volume file **and** `pae_json_path` in the compensated
  transaction boundary `persist_fold` already establishes (D-031 (a)) — file first, DB row,
  compensate by deleting the file if the DB write fails. **File and column cannot diverge.**
- **Idempotent:** a retried transfer converges (D-031's obligation, unchanged).
- **Auth:** bearer, `/jobs` prefix — so **D-034's prefix property holds unchanged**
  (`/jobs` guarded, `/api` open, no third category). The introspecting test must still pass
  with the new route present; that it does is worth asserting rather than assuming.
- **Why a route rather than sftp** (record the tradeoff, it was weighed): reuses the compensated
  boundary, hermetically testable, keeps file and column consistent. The cost is a permanent
  surface for a one-time batch — accepted, because an untestable transfer that silently
  half-completes is the worse failure.
- **Deep-learning justification:** indirect. PAE is the retained artifact that keeps a future
  PAE-derived feature (D-027, deferred-not-dismissed) reachable without a **paid re-fold** of
  the cohort.

---

## 1. Local persistence — rental-scoped, opt-in, PAE only

**Wire `write_artifacts`'s production caller** — it has been defined and tested since D-018 and
never called outside tests.

- **Trigger:** persist only when `WORKER_ARTIFACT_DIR` is set in the environment. Unset (the
  local tier, today) → behaviour and disk cost **unchanged**.
- **Keying:** `{WORKER_ARTIFACT_DIR}/{job_id}/`.
- **PAE only.** `structure.pdb`, `plddt.json`, and `provenance.json` already persist server-side
  via upload; duplicating them on the pod buys nothing. Use a PAE-only write rather than the
  full four-file `write_artifacts` if that is cleaner — **but if you reuse `write_artifacts`,
  say so and keep its existing tests green.**
- **Placement:** the `fold_from_spec` wrapper in `worker/main.py` is the Planner's suggestion,
  not a ruling. **The loop must stay pure** (`worker/orchestrator.py` is transport-agnostic and
  fully testable with doubles — that property is not negotiable). If a different seam preserves
  it better, take it and say why.

**⚠ Ordering:** the local write must land **before** the upload strips PAE, in the same PR.

---

## 2. The upload change

`worker/http_client.py:46-59` — stop gzipping `artifacts.pae` into the multipart body. The
route's `pae` parameter is already `Optional[UploadFile] = File(None)`; **verify that, don't
assume it.**

**Do not remove PAE from `FoldResult` or from `runner.py`.** The runner still produces it and
must — it is what the local write persists.

---

## 3. Test surface — first, as always

1. **The new route** — happy path (file on Volume + `pae_json_path` populated), idempotent
   retry, 404 on unknown job, 401 unauthenticated.
2. **Compensation** — a DB failure after the file write leaves **no orphaned file**, mirroring
   `persist_fold`'s existing test.
3. **D-034's prefix property still holds** with five `/jobs` routes and four `/api` routes.
4. **Local persist fires only when `WORKER_ARTIFACT_DIR` is set** — and writes PAE at the
   expected path when it is.
5. **`upload` omits PAE**; multipart carries `pdb`, `plddt`, `provenance` only.
6. **The runner still produces PAE** — `FoldResult.pae` populated, `runner.py` untouched.
7. **The loop's guarantees are unchanged** — fold once per claim, upload before complete,
   transport failure retries the report not the fold. Existing tests; confirm green.

---

## 4. The retrieval script (`scripts/`)

Committed, reproducible code — **not a shell one-liner** (D-009 §3's binding condition).

Walks `WORKER_ARTIFACT_DIR`, POSTs each `pae.json` gzipped to the new route, reports what
transferred and what did not. Idempotent; a re-run after a partial transfer converges.

**⚠ The run-guide text must state the blocking property in these terms:** D-011 rules **no
network volumes** — *"download weights, fold, upload artifacts, terminate."* PAE on container
disk is **destroyed on pod termination.** The batch is not done when the last fold completes; it
is done when PAE is off the box **and verified**. The failure is silent and costs a paid re-fold.

---

## 5. Definition of done

- `D-036` landed; `ARCHITECTURE.md` updated (fifth route, the rental artifact path).
- Tests first, failing for the right reason, then green; both required checks; **PR, not a
  direct commit to main**.
- Run-guide section for the rental batch including the blocking pre-termination step.
- **Report:** whether `write_artifacts` was reused or a PAE-only write was written, and which
  seam took the local persist.

---

## 6. Standing instruction

Part 2 exists because Code checked a Planner premise against the tree instead of building on it,
and that check was worth more than a paid re-fold of 29 targets. **Same standard here.** If the
seam in §1 is wrong, or the route cannot reuse the compensated boundary as cleanly as the
Planner assumes, surface it. An entry before code, never a workaround.
