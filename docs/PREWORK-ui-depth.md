# Session Pre-Work — Making the UI Informative (UI Arc, Step 3)

**Preceded by:** the UI shell and its three surfaces live; **80 folds** in production; the rental
transport exercised on rented hardware; D-041 ruling the scorer before any fitting code.
**Session type:** build-heavy, decision-light. **The suppliers already exist** — this session
spends what they serve.

---

## 0. Provenance (D-016)

Planner works from tree at **`#62` / `40a8fc9`** + live prod. **80 `protein_analyses` rows** (42
local + 38 rental), **5 failed folds** (§5), coverage ~**63 ranked ∧ folded of 82**. Confirm
against `GET /api/coverage` at session start — the numbers below are last night's and the rental
run landed late.

**⚠ Drafted at `#60`; updated after `#62`.** After this was written, the evening's fixes landed
(**D-042**, PR #62; docs PR #61). The rerun's *build* work — §5.1's recipe entry and §5.2's
OOM-crash fix — is **already shipped**; §5 below is updated to reflect that. The repo is clean and
`local == origin == 40a8fc9`.

---

## 1. The framing: the data got richer overnight and the UI has not caught up

Yesterday the UI was built against **42 local folds**, all `sliced_ecd` or small `whole`, all
int8/chunk-64, all from one machine. **That is no longer the cohort.** As of last night:

- **80 folds across two tiers**, with materially different provenance — `int8`/chunk-64 on owned
  hardware vs **`fp16`/unchunked on a rented RTX PRO 6000**, and **different torch builds**
  (2.11.0+cu128 local, 2.8.0+cu128 rental).
- **13 held-out whole-chain folds** now exist where there were 2 — a much larger set of targets
  the ranking will exclude and the UI must explain rather than hide.
- **5 targets failed**, four of them for a *reason the UI can state precisely* (the fold exceeded
  what the hardware could do unchunked).
- **The pLDDT distribution has shifted** — the rental folds are longer, and longer ESMFold
  predictions tend to score lower. **Recompute the bands' impact before assuming D-039 still
  fits.**

**So the honest framing for this session is not "add features."** It is: *the UI tells the truth
about 42 folds from one machine; it now has to tell the truth about 80 folds from two, five
failures, and a hardware ceiling.* That is more informative **and** more honest — which is the
only direction this project's UI is allowed to move.

---

## 2. What to build, in dependency order

### 2.1 — Failed targets are currently invisible. **This is a D-024 violation and it is first.**

Five targets have a `protein_analyses` row with **`mean_plddt = NULL`, `pdb_path = NULL`** —
ADAM17, IGF2R, NOTCH2, PTPRZ1, SDK1. **The coverage view counts them as `not_folded`, which is
true but not the whole truth:** *attempted and failed* is a different state from *never
attempted*, and D-024's entire discipline is that the reader can see what the system could not
do.

**Build:** a `fold_status` of `failed` distinct from `not_folded`, surfaced on the coverage view
with the reason. **The reason is knowable and specific** — four exceeded the unchunked memory
ceiling at >1,350 residues; one was interrupted.

**⚠ Supplier check first.** `GET /api/coverage` derives `fold_status` from whether a completed
`protein_analyses` row exists. **A three-state status may need a supplier change** (the `jobs`
table has `status` and `error`; `protein_analyses` has neither). **Rule it before building the
component** — this is the same supplier-before-contract discipline D-034 and D-038 were written
under, and the trap the coverage view already fell into once.

### 2.2 — The provenance panel must show *which machine folded this*

D-015's claim is *"we ran this ourselves."* With two tiers that claim needs a subject. The
`meta.fold_provenance` already carries `dtype` and `chunk_size`; the tier is in `meta.tier`.

**Surface, per target:** tier (`local` / `rental`), dtype, chunk size, model revision, and —
**if it is captured, which it may not be** — the torch build. **Check whether `fold_provenance`
records the torch version.** If it does not, that is a real provenance gap worth an entry: the
80 folds were produced by two different torch builds and nothing in the database says so.

### 2.3 — The two-tier cohort needs to be legible as two tiers

Today the target list is flat. **A reader cannot see that 42 folds came from one machine at int8
and 38 from another at fp16.** That is not a cosmetic distinction — it is exactly the kind of
methodological detail D-015 §3's diagnostics will care about, and a grader should not have to
open a JSON payload to find it.

**Build:** tier visible in the list, filterable. **Do not blend tiers into a single quality
score** — that would collapse a real distinction, the same failure mode D-028 forbids for
disagreement classes.

### 2.4 — Confidence: recompute the bands' fit against 80 folds

D-039 set bands at 50/60/70 justified by the **42-fold** distribution (24% / 45% / 57%).
**Recompute against 80.** If the shape has moved materially — and longer rental folds make that
plausible — the entry needs amending with the new numbers. **Do not silently keep bands justified
by a distribution that no longer exists.**

### 2.5 — Per-residue confidence is the most underused signal in the system

NECTIN4's per-residue pLDDT runs **50.1 to 93.4** on a target whose *mean* is 77.26. **The mean
hides that entirely.** The structure viewer already colours by it; the list and target views
report only the mean.

**Build:** a compact per-residue distribution (sparkline or small histogram) beside the mean.
**This is the single highest-information-per-pixel addition available** — it shows the model's
own uncertainty varying across the molecule, which is precisely the deep-learning output the
project claims to surface (D-015).

---

## 3. What NOT to build

- **No ranking table, no disagreement classes, no attribution.** The scorer does not exist. UI
  Plan v2 §9 and the pre-work before it both name this; it stays named.
- **No auto-refresh.** Deliberately deferred last session; nothing has changed.
- **No new dependencies without justification** (D-037) — hand-rolled SVG remains the right
  answer for a sparkline.
- **No inference on page load, ever.**

---

## 4. Traps

**(a) The supplier trap, twice burned.** §2.1's `failed` state and §2.2's torch build may both
need API changes. **Check what `/api/analyses` and `/api/coverage` actually serve before speccing
a component against it.** The coverage view was specced against data the API could not supply,
and it cost an entry to fix.

**(b) The bands may no longer fit** (§2.4). Recompute, do not assume.

**(c) "More informative" must not become "more confident."** Every addition here is about showing
*more of what the system does not know* — failures, uncertainty spread, provenance differences.
**A UI that looks more authoritative while the underlying cohort has five holes in it is worse
than the current one.**

---

## 5. THE RERUN — five targets, and it should come first

> **⚠ UPDATED — the build half of this section is DONE (D-042, PR #62).** §5.1's chunked-rental
> entry + recipe change (`chunk_size: None → 64`) and §5.2's OOM-crash fix (OOM→`FoldError` +
> batch resilience) landed tests-first and deployed. **What remains is the owner's rent-and-run
> (§5.3, from step 3) — no code.** If a fold still OOMs it now fails cleanly and the batch survives,
> so the manual-restart tax from last night is gone.

**Owner has balance available and wants these tonight-equivalent.** Coverage goes **63 → 67 of
82** — the entire ranked cohort except the two named exclusions. That is a materially better
number to present than 63 with unexplained holes.

**⚠ Two different problems. Only one is a retry.**

| Target | Residues | Problem | Fix |
|---|---|---|---|
| **ADAM17** (P78536) | 457 | Interrupted mid-fold by a worker crash | **Retry as-is** |
| **PTPRZ1** (P23471) | 1,612 | O(L³) attention OOM | `chunk_size=64` |
| **NOTCH2** (Q04721) | 1,652 | same | same |
| **SDK1** (Q7Z5N4) | ~2,213 | same | same |
| **IGF2R** (P11717) | ~2,491 | same — asked **230 GiB** | same |

### 5.1 — The recipe change needs an entry, not just a line — ✅ DONE (D-042)

`core/enqueue.py` `TIER_RECIPE["rental"]`: `chunk_size: None` → `64`.

**One line, but D-011 explicitly ruled unchunked for the rental tier**, on the reasoning that
more VRAM made the local mitigation stack unnecessary. **That reasoning is falsified** and the
reversal needs the measurement on the record: JAG1 folded at 1,034 aa; ~1,350 aa OOM'd asking
67.18 GiB with 37.24 GiB free; IGF2R asked **230.33 GiB on a 94.98 GiB card**. Triangular
attention is **O(L³)** — no rentable card closes that gap; chunking is the only mitigation, and
it is the one the local tier already uses successfully.

**⚠ Record the provenance consequence honestly:** the four reruns will fold under
`fp16`/**chunk-64**, which is a *third* recipe — distinct from local (`int8`/chunk-64) and from
the other 38 rental folds (`fp16`/unchunked). **`meta.fold_provenance` already captures
`chunk_size`, so this is visible rather than hidden** — but the UI's provenance panel (§2.2)
should make it legible, and any cross-target comparison needs to know three recipes exist.

### 5.2 — ⚠ Fix the OOM crash BEFORE renting again — ✅ DONE (D-042)

Close-out §3a: `torch.OutOfMemoryError` propagates through `fold()` → `fold_from_spec` →
`run_worker` → `main()` and **kills the process**, where D-030 §4 rules a fold failure should call
`fail()`, record the error, and continue.

**This will recur.** Chunking makes the four *likely* to fold, not certain — IGF2R at ~2,491 is
still enormous. If one OOMs, the crash takes the worker down and the rerun becomes manual
restarts at $2/hr, exactly like last night.

**Fixing it is cheap and it is a real bug**, not a convenience: catch the OOM at the fold
boundary, report `fail()` with the error, continue the loop. Worth an hour before spending money.

**Consider also:** a loud startup check that fails on a rejected token (close-out §4b — 70 minutes
lost to silent 401 polling), and `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` on the pod,
since the 67 GiB OOM reported **35.34 GiB reserved-but-unallocated** against a ~30 GiB shortfall.
The allocator setting is a **candidate, not a claim** — untested.

### 5.3 — Sequence

1. ~~**Entry** ruling the chunked rental recipe~~ — **DONE (D-042).**
2. ~~**Code:** recipe change + OOM-handling fix, tests-first, through the gate, deployed~~ — **DONE (PR #62).** Start here ↓
3. **Re-enqueue the five.** `core.enqueue` is idempotent (D-026); confirm it offers exactly 5.
4. **Rent** — ~30–45 minutes, ~$2. **Use `nohup … &`** (close-out §4a) and **verify the token
   length on the pod before starting** (§4b).
5. **PAE retrieval → verify → terminate pod → delete the network volume.** All four, in order.

**Chunking trades speed for memory** — expect these folds to run slower per residue than the
unchunked ones did. Budget the time, not just the dollars.

---

## 6. Also on the board

- **⚠ The silent-hang mode** (close-out §3b) — a wedged worker holding 57 GiB at 0% utilisation,
  billing indefinitely while appearing healthy. Strengthens the heartbeat case; watch for it on
  the rerun.
- **Amendments:** D-011 and D-022 **amended in place (D-042).** D-030 (heartbeat trigger extended
  to the silent-hang mode) and D-035 (PAE size at scale) **still queued** — recorded in D-042's
  body but not yet added as pointers on those two entries.
- ~~`tmp_dispo.py`, `tmp_state.py`, `tmp_nopae.py`~~ — **deleted.**
- **Network volume** — confirm deleted; spend rate should read $0.00/hr.

---

## 7. Definition of done

**The rerun (§5):**
- Chunked-rental entry landed; recipe change and OOM-handling fix through the gate.
- Five targets folded; **coverage reads 67 of 82**.
- PAE retrieved and verified; pod terminated; **network volume deleted**.

**The UI (§2):**
- Failed targets **visible with reasons**, supplier ruled if needed.
- Provenance shows **which tier and which recipe** produced each fold — now **three** recipes.
- Tier legible and filterable in the list.
- Confidence bands **re-justified against the full cohort**, or amended.
- Per-residue distribution rendered beside the mean.
- **Still not built, still not mocked:** the ranking table.

---

## 8. Sequencing note

**§5 before §2 if the GPU is available**, for one reason: the rerun changes the data the UI is
built against. Coverage moves to 67, five failed rows become folded, and a third recipe enters
`fold_provenance`. **Building §2.1's failed-target surface against five failures that are about
to become zero would be building against a state that is expiring** — the same mistake as
speccing a viewer against imagined data, which is why the first fold was sequenced before the UI
in the first place.

**If the GPU is not available**, §2 proceeds regardless — but §2.1's component must be built to
render *whatever* failures exist, including none, rather than to display these specific five.
