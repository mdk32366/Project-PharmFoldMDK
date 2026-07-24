# Session Pre-Work — Land the Branch, Run the Rerun, Finish UI Depth (UI Arc, Step 3 cont.)

**Preceded by:** `CLOSEOUT-2026-07-24.md`. The failed-state surface (D-043) and the re-fold path
(D-044) are built, tested, and **pushed but not merged**. The rerun is code-ready and runbook-ready
but **has not run**. UI-depth items §2.2–§2.5 are untouched. **Session type:** finish-what-was-
started — one merge, one rent-and-run, three-plus UI components. Decision-light; the suppliers for
most of it already exist.

---

## 0. Provenance (D-016)

Planner works from branch **`feat/coverage-failed-state` @ `320a616`** (PR pending) + live prod.
Live at close of 2026-07-24: **75 of 82 folded**, the **five rerun targets `failed`** (ADAM17,
IGF2R, NOTCH2, PTPRZ1, SDK1) — *unless the owner has already run `--requeue`, in which case they are
`pending`*. **Confirm both at session start:** `GET /api/coverage` for the fold counts, and the
Phase-1 status query in `RUNBOOK-rerun-5-targets.md` for the five's job state.

---

## 1. First: land the branch (it gates everything the UI shows)

`feat/coverage-failed-state` carries D-043 + D-044. Until it merges, prod's coverage view still
renders the two-state `fold_status` and the failed rows read `not yet`. **Open the PR, take it
through the gate (D-005/D-008), merge, confirm the deploy is green.** The read API is a supplier/
consumer split (D-034/D-038) — a green deploy means the new `fold_status` is live with no data
migration.

**⚠ One reconciliation to check on merge:** if the rerun (§2) has already run, the five will be
`folded` and the failed surface will correctly show *nothing* for them. If it has not, they will
render `failed` with whatever the crash left in `jobs.error` (likely a reaped marker, not the OOM
text — D-043 §context). Both are correct; just know which you are looking at.

---

## 2. The rerun — now genuinely one command from ready

The build half is done twice: D-042 (chunking + clean OOM) and D-044 (the re-offer path). What
remains is `RUNBOOK-rerun-5-targets.md`, followed exactly. The short version:

1. **Pane A / LOCAL:** `python -m core.enqueue --requeue P78536 P11717 Q04721 P23471 Q7Z5N4` →
   expect `requeued=5` (or fewer if any already landed), `not_found=[]`. Confirm all five `pending`.
2. **Pane C / POD:** rent (any secure ≥24 GB card now that chunking is on — an A6000 is plenty and
   cheaper than the Blackwell), paste the env block **token single-quoted**, run the **length==69**
   assertion, start the worker **`nohup … &`**.
3. **Pane A:** watch `fly logs`; these are the biggest folds in the cohort and run slower per residue.
4. **Pane C:** `python -m scripts.retrieve_rental_pae` **must exit 0** before terminating.
5. Terminate the pod; **delete the network volume**; confirm spend reads $0.00/hr.

**Payoff:** coverage **75 → the full ranked cohort** (67 ranked, minus the two named exclusions).
The four chunked reruns land under a **third** provenance recipe — `fp16`/chunk-64, distinct from
local (`int8`/chunk-64) and the other 38 rental (`fp16`/unchunked). This matters for §2.2 below.

**Sequence note:** §2 before §2.4/§2.5, because the rerun changes the distribution those recompute
against (five longer folds enter the cohort). Building the confidence recompute against a cohort
that is about to grow is the expiring-state trap again.

---

## 3. UI depth — the four items still open (dependency order)

Carried verbatim from `PREWORK-ui-depth.md` §2.2–§2.5; §2.1 (failed targets) is now done.

### 3.1 — Provenance panel: *which machine, which recipe* (was §2.2)
Two tiers, soon three recipes. Surface per target: tier (`local`/`rental`), dtype, chunk size, model
revision. **⚠ Supplier check first:** `meta.fold_provenance` carries `dtype`/`chunk_size`; the tier
is `meta.tier`. **Check whether the torch build is captured — it is not, and that is a real
provenance gap** (80 folds from two torch builds, 2.11.0 local vs 2.8.0 rental, and nothing in the
DB says so). If absent, that is an entry worth writing, not a field to invent.

### 3.2 — Make the two-tier cohort legible (was §2.3)
Tier visible in the target list, filterable. **Do not blend tiers into one quality score** — that
collapses a real methodological distinction (D-028's rule against collapsing disagreement classes,
one surface over).

### 3.3 — Recompute the confidence bands against the full cohort (was §2.4)
D-039 set 50/60/70 on the **42-fold** distribution (24% / 45% / 57%). Recompute against 80 (soon 85).
Longer rental folds pull pLDDT down; **if the shape has moved materially, amend D-039 with the new
numbers — do not silently keep bands justified by a distribution that no longer exists.**

### 3.4 — Per-residue confidence beside the mean (was §2.5)
The mean hides the spread (NECTIN4: 50.1–93.4 on a 77.26 mean). A compact per-residue sparkline/
histogram beside the mean — **the highest-information-per-pixel addition available**, and D-037's
answer stands: hand-rolled SVG, no new dependency.

---

## 4. Traps (unchanged, and still binding)

- **(a) Supplier-before-contract, thrice-burned.** §3.1's torch build may need an API/schema change.
  Check what `/api/analyses/{id}` actually serves before speccing the panel against it.
- **(b) The bands may no longer fit** (§3.3) — recompute, do not assume.
- **(c) "More informative" must not become "more confident."** Every addition shows *more of what
  the system does not know* — provenance differences, uncertainty spread. The failed state (D-043)
  was in this spirit; keep the rest there.

---

## 5. What NOT to build

- **No ranking table, no disagreement classes, no attribution** — the scorer does not exist (D-041,
  UI Plan v2 §9). Still named, still not mocked.
- **No auto-refresh. No inference on page load, ever. No new dependencies without an entry (D-037).**

---

## 6. Definition of done

- **Branch merged**, deploy green, failed-state live on prod.
- **The rerun run:** five folded, PAE retrieved and verified, pod terminated, **network volume
  deleted**; coverage reads the full ranked cohort.
- **Provenance** shows tier + recipe (now three) per fold; the torch-build gap ruled (surfaced or
  entered).
- **Tier legible and filterable**; bands **re-justified against the full cohort** or amended;
  **per-residue distribution** rendered beside the mean.
- **Still not built, still not mocked:** the ranking table.

---

## 7. If the GPU is unavailable

§3 proceeds regardless — it does not depend on the rerun, only benefits from sequencing after it.
Build §3.3/§3.4 to render *whatever* cohort exists (80 or 85), not these specific counts. The merge
(§1) is unconditional and comes first either way.
