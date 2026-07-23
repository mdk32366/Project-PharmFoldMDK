# Orders for Code — Rental-run pre-flight (three checks, zero cost)

**Session:** 2026-07-23. **Planner:** Claude. **Builder:** Code.
**Context:** The owner is about to rent an A6000 and fold the rental-tier cohort. **The rental
itself is owner-executed** (it is a spend and a credential). These three checks run **before**
the pod is rented, cost nothing, and de-risk the spend.

**No code changes. No PRs. Verify and report.**

---

## Check 1 — the enqueue set is 27, and the two exclusions are absent

```
python -m core.enqueue --bucket rental --dry-run
```

**Expected: 27 foldable rows. MUC16 and FAT2 must NOT appear.**

**Why this specific check.** The rental *tier* contains 29 rows (16 `rental` +
13 `untested` routing to rental per D-024), but **MUC16 and FAT2 are named exclusions**
(D-022) and `core/enqueue.py` gives named exclusions no jobs (D-026). So the correct
enqueue set is **27**.

**This is not a formality — those two are the monsters.** From
`data/cohort_82_ecd.csv`: **MUC16 is 14,451 aa** (~8.7× the next-largest target; at L² PAE
scaling, roughly 200 GB raw) and **FAT2 is 4,030 aa**. With them correctly excluded, the largest
fold attempted is **NOTCH2 at 1,652 aa**, then PTPRZ1 (1,612), LRP6 (1,351), JAG1 (1,034);
everything else is under 1,000 aa.

**If either appears in the dry-run, STOP and report.** That is a D-022/D-026 regression, and
finding it here costs nothing while finding it on a running A6000 costs a paid fold of a
14,451-residue sequence.

---

## Check 2 — the rental recipe prints as fp16 / unchunked

From the same dry-run output, confirm the per-row recipe is **`dtype=fp16`, `chunk_size=None`**.

**Planner verified against the tree** (`core/enqueue.py:55` sets
`"rental": {"dtype": "fp16", "chunk_size": None}`; `worker/runner.py` halves `model.esm` on the
fp16 branch and skips `set_chunk_size` when `chunk_size is None`). **Confirm it in the actual
output rather than trusting this note** — the whole point of D-011's rental tier is that the
local mitigation stack stops binding, and a rental job carrying int8/chunk-64 would silently
fold under the local recipe.

---

## Check 3 — name the commit the pod must clone

Report the current `origin/main` short SHA.

**Why it matters.** The pod must run **merged** code — D-035's httpx timeout, D-036's
`POST /jobs/{id}/pae` route, and the PAE-out-of-band upload. **A pod cloned from a stale commit
silently reintroduces the 5 s default timeout and the in-lease PAE upload**, which is the exact
paid-retry-loop failure D-035 was written to prevent. The owner needs the SHA to check against
on the pod before starting the worker.

---

## Report back

1. Dry-run row count, and explicit confirmation MUC16/FAT2 are absent.
2. The recipe as printed (`dtype`, `chunk_size`).
3. `origin/main` short SHA.

**Then hold.** The run itself is owner-executed; nothing further is Code's until the folds land,
at which point the coverage endpoint should read **67 ranked ∧ folded of 82** with no code change
(the property D-034/D-038 were built for, and worth spot-checking then).

---

## ⚠ One thing to flag to the owner if it comes up

The single step whose omission loses data **silently and unrecoverably** is
**`WORKER_ARTIFACT_DIR`** on the pod. Without it the rental-scoped local persist never fires,
PAE exists only in the in-memory `FoldResult`, and it is discarded when the loop claims the next
job — recoverable only by a paid re-fold. It is in the owner's orders, but it is the one worth
repeating.
