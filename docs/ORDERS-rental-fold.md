# Orders — The A6000 Rental Fold (owner-executed, Code-supported)

**Session:** 2026-07-23. **Planner:** Claude. **Executor:** owner (the rental is a spend and a
credential; Code cannot provision it). **Code's role:** the pre-flight checks in §2 and standing
by during the run.

**Entries in force:** D-011 (rented GPU, one-time batch), D-030 (lease), D-035/D-036 (PAE
out-of-band, timeout, the fifth route), D-026 (enqueue idempotency).
**Everything the run needs is already built and deployed.** This is execution, not construction.

---

## 0. What this buys, stated so the spend is justified before it happens

- **Coverage moves 40/82 → 67/82 ranked-and-folded.** The coverage line stops reading as a
  half-finished cohort.
- **The labelled ∧ folded intersection grows** — the number D-041's sizing argument is thinnest
  on. More Group B positives inside the folded set is the single biggest improvement available
  to the fit.
- **D-030's provisional 3600 s lease finally gets measured** against a large fold, which is the
  measurement that entry named and has never had.

---

## 1. ⚠ The cohort is 27, not 29 — and the two excluded rows are why

Computed from `data/cohort_82_ecd.csv`, 2026-07-23:

| | |
|---|---|
| `bucket_by_largest = rental` | 16 |
| `bucket_by_largest = untested` (440–630, routes to rental per D-024) | 13 |
| **Total rental-tier** | **29** |
| **Named exclusions among them (D-022): MUC16, FAT2** | **2** |
| **Actually enqueued and folded** | **27** |

**This matters for cost and for expectations**, because the two exclusions are the monsters:

- **MUC16 — 14,451 aa.** Roughly 8.7× the next-largest target. At L² PAE scaling this alone
  would be ~200 GB raw.
- **FAT2 — 4,030 aa.**

`core/enqueue.py` gives named exclusions no jobs (D-026), so **they will not be attempted and
must not be forced.** The largest fold actually attempted is **NOTCH2 at 1,652 aa**, with
PTPRZ1 (1,612), LRP6 (1,351) and JAG1 (1,034) behind it. Everything else is under 1,000 aa.

**Verify this before spending** — §2.1.

---

## 2. Pre-flight, all zero-cost, all before the pod is rented

### 2.1 Confirm the enqueue set (Code or owner)

```powershell
python -m core.enqueue --bucket rental --dry-run
```

**Expect 27 foldable rows, MUC16 and FAT2 absent.** If either appears, **stop** — that is a
D-022/D-026 regression and it is cheaper to find now than on a paid card.

### 2.2 Confirm the fold recipe is fp16/unchunked

`core/enqueue.py:55` sets `rental → {"dtype": "fp16", "chunk_size": None}` and
`worker/runner.py` handles both (fp16 halves `model.esm`; `chunk_size=None` skips
`set_chunk_size`). **Verified by the Planner against the tree — confirm it survives in the
dry-run's printed recipe rather than trusting this note.**

### 2.3 Confirm the transport is current

The pod must run the **merged** code — D-035's timeout, D-036's `/jobs/{id}/pae` route, and the
PAE-out-of-band upload. A pod cloned from a stale commit silently reintroduces the 5 s timeout
and the in-lease PAE upload. **`git log --oneline -1` on the pod, checked against `origin/main`.**

### 2.4 Set `WORKER_ARTIFACT_DIR`

**This is the step whose omission loses data silently.** Without it the rental-scoped local
persist does not fire, PAE exists only in memory, and it is discarded on the next claim. **PAE
is not recoverable without a paid re-fold.**

---

## 3. The run

1. **Rent the A6000** (RunPod Secure Cloud, per-second billing, **no network volume** — D-011).
2. **Clone at `origin/main`**, install the worker stack, set `WORKER_AUTH_TOKEN`,
   `TRANSPORT_URL=https://pharmfoldmdk.fly.dev`, `WORKER_ARTIFACT_DIR`, and a distinct
   `WORKER_ID` (e.g. `rental-a6000`) so the run is identifiable in the logs.
3. **Enqueue 27** — `python -m core.enqueue --bucket rental` from the local box, tunnel up.
   Idempotent (D-026); a re-run is safe.
4. **Start the worker on the pod.** Watch `fly logs -a pharmfoldmdk`: `claim → 200`,
   `artifacts → 204`, `complete → 204`, repeating.
5. **⚠ Before terminating the pod — transfer PAE.** `scripts/` has the retrieval step (D-036).
   **The batch is not done when the last fold completes; it is done when PAE is off the box and
   verified.** Container disk is destroyed on termination and PAE costs a paid re-fold to
   recover.
6. **Verify, then terminate.** Job counter all `complete`, `protein_analyses` row count up by
   27, `pae_json_path` populated for the new rows.

---

## 4. What to watch, and what each observation means

**The first fold is the measurement D-030 has been waiting for.** Record for the amendment:

| Observation | Why it matters |
|---|---|
| **Claim-stamp → complete, wall clock, for NOTCH2 (1,652 aa)** | The measurement that retires or revises D-030's provisional 3600 s |
| **Peak VRAM** | 48 GB unquantised/unchunked at 1,652 aa is expected to fit; if it does not, that is a finding about the A6000 ceiling D-022 left open |
| **PAE file size on the pod** | Tests the 2.2×-at-small-lengths assumption at large L. D-035 flagged this as *assumed*, not measured |
| **Total pod time** | D-011 budgeted ~$0.25 for a handful of targets; 27 folds is a different scope and the real number belongs in the log |

**If a fold fails:** the loop reports `fail()` and moves on (D-030 §4). A deterministic failure
(CUDA OOM on the largest target) is a **result**, not a disaster — it measures the A6000 ceiling,
which D-022 explicitly left open. Record it and continue; do not hand-tune the recipe mid-run,
because a target folded under a different recipe than the manifest reviewed is a provenance
break (`fold_from_spec` already refuses a model-revision mismatch for exactly this reason).

---

## 5. Definition of done

- 27 rental targets `complete`; `protein_analyses` up by 27; `pae_json_path` populated.
- **PAE transferred off the pod and verified before termination.**
- Coverage endpoint reports **67 ranked ∧ folded of 82** (spot-check `GET /api/coverage`).
- The four §4 numbers recorded for the D-030/D-011 amendments.
- Pod terminated.

---

## 6. After the run — what changes

- **D-030 amendment** — the measured large-fold wall clock against the provisional lease.
- **D-011 amendment** — actual rental cost against the ~$0.25 estimate.
- **D-035 amendment** — the measured PAE ratio at large L, confirming or correcting the assumption.
- **The coverage line and every UI surface update with no code change** — they read from the
  database, which is the property D-034/D-038 were built for.
- **D-041's sizing improves** — recompute the labelled ∧ folded intersection immediately.
