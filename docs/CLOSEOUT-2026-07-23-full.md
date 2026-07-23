# Session Close-Out — 2026-07-23 (The Read API, the Rental Tier, and the First Rented Fold)

**Opened with:** `PREWORK-ui-arc.md` — step 2 of the UI arc.
**Closed with:** a live four-surface UI, the rental transport built *and exercised*, **80 folds
in production (up from 42)**, and the A6000-class ceiling measured for the first time.

**What did not happen, named first:** the scorer does not exist, so the **ranking table — the
demo's centrepiece — is still unbuilt**, deliberately and unmocked. Five folds failed. The
cohort is not complete.

---

## 1. What shipped

| PR | What |
|---|---|
| **#52** | **D-034** — the read API: four `GET /api` routes, unauthenticated |
| **#53/#54** | **D-035 + D-036** — httpx timeout, PAE out-of-band, the fifth route, retrieval script |
| **#55** | **D-038** — the coverage supplier, `GET /api/coverage` |
| **#56** | **DEP-006 + D-037** — two-stage image, React shell. **DEP-004's trigger fired: a green deploy now means a reachable UI** |
| **#57** | **D-039** — target view: 3Dmol.js, confidence bands, provenance panel |
| **#58** | Coverage view, method note, ADC context |
| **#59** | Parked items closed (`accelerate` pin, D-018 Amendment 1) |
| **#60** | **D-040** — evidence scores (17/82), Group B/C schema, reconciliation core |

Also ruled: **D-041** (the scorer model), **UI Plan v2** (superseding the 2026-07-16 plan in full).

---

## 2. The rental fold — what it produced and what it cost

**42 → 80 analyses. 38 rental folds landed. 5 failed.** Coverage moved **40 → ~63 ranked ∧
folded of 82**.

**The hardware was not what was ordered.** D-011 specified an A6000 (48 GB, ~$0.49/hr). The pod
provisioned was an **RTX PRO 6000 Blackwell, 95 GiB, at $2.00/hr** — 4× the budgeted rate. The
cost estimate in D-011 (~$0.25) is wrong by roughly an order of magnitude once the full evening
is counted; **actual spend was on the order of $10–14**, much of it wasted (§4).

### The measured ceiling — D-022's open question, closed

| Target | Residues | Result |
|---|---|---|
| JAG1 | 1,034 | **folded** |
| LRP6 (probable) | 1,351 | **OOM — asked 67.18 GiB, 37.24 GiB free** |
| PTPRZ1 | 1,612 | not folded |
| NOTCH2 | 1,652 | not folded |
| SDK1 | ~2,213 | not folded |
| IGF2R | ~2,491 | **OOM — asked 230.33 GiB on a 94.98 GiB card** |

**The unchunked ceiling on a 95 GiB card sits between 1,034 and ~1,350 residues.**

**And the reason is architectural, not a VRAM shortage.** The failure is in `tri_att_start` —
triangular attention over the pairwise representation, which is **O(L³)**, not O(L²). D-011's
rental recipe set `chunk_size=None` on the assumption that more VRAM made chunking unnecessary.
**That assumption is falsified.** No rentable card closes a 230 GiB gap; chunking is the only
mitigation, and it is the one the local tier already uses.

---

## 3. Four findings that only the rental tier could expose

**(a) ⚠ The loop crashes instead of failing the job.** `torch.OutOfMemoryError` propagates
through `fold()` → `fold_from_spec` → `run_worker` → `main()` and **kills the process**. D-030 §4
rules that a fold failure calls `fail()`, records the error, and continues. It does not. **One
oversized target took down the entire batch** and required manual restart — four times over the
evening. This is a real bug in the loop's error handling and it is invisible on the local tier,
where folds are too small to OOM.

**(b) ⚠ A silent hang mode that is worse than a crash.** The final stall was **not** an OOM: three
`nvidia-smi` samples ten seconds apart showed **identical 57,169 MiB held, 0% utilisation, 87 W**,
process alive, no traceback. A crashed worker is detectable; **a wedged one bills at $2/hr
indefinitely while appearing healthy.** This is a stronger argument for D-030's lease heartbeat
than anything in that entry — the heartbeat's trigger condition should be updated to include it.

**(c) The model reloads from scratch on every fold.** `Loading weights: 4498` appears once per
target — `fold_from_spec` constructs the model per call. Invisible on owned hardware; **a direct,
measurable cost on rented silicon**, roughly 10–20% overhead across 38 folds.

**(d) Memory fragmentation was material.** The 67 GiB OOM reported **35.34 GiB reserved by
PyTorch but unallocated** against a ~30 GiB shortfall. `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`
might have let that fold through. Untested; recorded as a candidate, not a claim.

---

## 4. The two operational failures, and what they cost

**(a) The worker was not detached.** Started in the foreground of a browser web terminal; when
the tab's connection dropped, the shell died and took the worker with it. **~1 hour of billing
for zero folds.** Fixed by `nohup … &`. **Planner error** — the guide said "leave the tab alone"
instead of specifying a detached process.

**(b) A truncated token failed silently for over an hour.** `WORKER_AUTH_TOKEN` pasted into bash
arrived as **12 characters instead of 69** — mangled by double-quote interpretation. The worker
polled and was rejected **401 every 5 seconds**, while *looking* perfectly healthy: process
alive, no errors on stdout, no crash. Diagnosed only by reading Fly's logs.

**⚠ The lesson is a design one, not an operational one.** The 401s were perfectly informative and
nobody was looking at them, because **the worker's own output gave no indication anything was
wrong.** A startup check that fails loudly on a rejected token — rather than polling silently —
would have caught this in 30 seconds instead of 70 minutes. **That is a real change to propose,
and it belongs in the log.**

---

## 5. The pattern, extended — corrections caught before they cost anything

The day's recurring finding, now at **eleven instances**, seven of them the Planner's own:

| Claim | Corrected by |
|---|---|
| `accession`/`gene_symbol`/`folded_at` columns exist | the schema |
| the batch landed 40 targets | the query — **42** |
| PAE gzips 5–10× | the artefact — **2.2×** |
| "API to a rented service" | D-011 — repo code on rented silicon |
| a full-meta list would be fine | the measurement — 9,360 B vs ~43 KB+ |
| the UI Plan needs a framework swap | reading it — a different product |
| **`runner.write_artifacts` persists PAE locally** | **the tree — no production caller** |
| **the rental cohort is 27** | **the manifest — 38 foldable, tier ≠ CSV bucket** |
| **the largest fold is NOTCH2 at 1,652** | **the manifest — IGF2R at ~2,491** |
| **"roughly a third" below pLDDT 60** | **the distribution — 45%** |
| `build_rows` | the source — `build_manifest` |

**Three of these were caught by the Builder checking a Planner premise against the tree rather
than building on it.** The `write_artifacts` catch alone prevented silent, unrecoverable PAE loss
on paid folds. The 27-vs-38 catch prevented a spend planned against the wrong cohort.

**And one was caught by nobody until the GPU said so:** the unchunked recipe. Every review passed
it because it was ruled in D-011 and never re-examined. **The artefact that corrected it was a
CUDA allocator error at 11 PM.**

---

## 6. What the UI shows tonight

`pharmfoldmdk.fly.dev` — four surfaces, all live, all reading from the database with no redeploy:

- **Targets** — 80 folds, confidence band inline per D-039
- **Coverage** — the honest line, **rendering the intersection and naming the two numbers it
  refuses**: *"Not the 67 ranked in the manifest… and not the 42 folded… Both would overstate the
  cohort."* MUC16 and FAT2 listed by name with reasons (D-022 satisfied)
- **Method** — D-028's commitments
- **About ADCs** — the mechanism, bounded outcome claims, NECTIN4 as worked example

**The coverage number climbed live during the rental run**, from 40 through the low 60s, with no
deploy and no cache invalidation. That is D-034/D-038's supplier/consumer split demonstrated
rather than asserted.

---

## 7. Carried hazards and open items

- **⚠ Five folds failed** — see §8 for the rerun list.
- **The loop's crash-on-OOM (§3a)** — unfixed, and it will recur on any rerun of the oversized
  targets.
- **D-030's lease** — still provisional at 3,600 s, justification weakened by the 2.2× measurement
  and now further by the silent-hang mode (§3b).
- **The network volume** — attached against D-011's ruling; **bills monthly even after pod
  termination.** Must be deleted separately.
- **`torch 2.8.0+cu128` on the pod vs `2.11.0+cu128` locally** — the rental folds ran on a
  different torch build. Real provenance difference; belongs in the D-011 amendment.
- **`tmp_dispo.py`, `tmp_state.py`, `tmp_nopae.py`** — throwaway query scripts; delete.

---

## 8. The rerun list — five targets, two different problems

| Target | Residues | Why it failed | Fix |
|---|---|---|---|
| **ADAM17** (P78536) | 457 | In flight when a crash took the worker | **Retry as-is** |
| **PTPRZ1** (P23471) | 1,612 | O(L³) attention OOM | **Needs `chunk_size=64`** |
| **NOTCH2** (Q04721) | 1,652 | same | same |
| **SDK1** (Q7Z5N4) | ~2,213 | same | same |
| **IGF2R** (P11717) | ~2,491 | same — asked 230 GiB | same |

**The four oversized targets need a `TIER_RECIPE` change** (`core/enqueue.py`: rental
`chunk_size: None` → `64`), which is a **one-line change with a decision entry**, justified by the
measured ceiling. Chunking trades speed for memory — those folds run slower and succeed.

**Sequencing recommendation:** make the recipe change, ship it through the gate, *then* rent once
more and run all five together. ~30–45 minutes, ~$2. **Coverage would reach 67 of 82** — the
entire ranked cohort except the two named exclusions.

**Not urgent.** The scorer can proceed at 63.

---

## 9. Amendments this session generated

- **D-011** — actual hardware (RTX PRO 6000, not A6000), actual rate ($2/hr, not $0.49), actual
  cost, the torch-build difference, and **the falsified unchunked assumption**.
- **D-022** — the ceiling is measured: **1,034 aa folds, ~1,350 aa does not**, unchunked at 95 GiB.
- **D-030** — the 5–10× gzip estimate falsified at 2.2×; the heartbeat's trigger extended to
  include the silent-hang mode.
- **D-035** — PAE size measured at scale (~10 MB average per rental fold, 340 MB across 33).

---

## 10. Definition of done — met, with exceptions named

- Read API, coverage supplier, React shell, target view, coverage view: **shipped, live, verified**.
- Rental transport: **built and exercised end to end on rented hardware.**
- PAE: **33/33 transferred and acknowledged before termination.**
- **Not met:** the cohort is not fully folded (5 failures); the scorer does not exist; the ranking
  table remains unbuilt and unmocked.
