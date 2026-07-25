# Session Close-Out — 2026-07-24 (The Rerun That Fought Back — a Latent Recipe Bug, Found Live)

> Second session of 2026-07-24. The morning shipped D-043/D-044/D-045 and merged them (SHA
> `b7d5e4b`). This session ran the five-target rental rerun those merges were built to enable —
> and the rerun surfaced a latent bug that no test had reason to catch, cost most of the session
> to diagnose live, and ends with **4 of 5 folded** and a permanent cure ruled but not yet coded.

---

## 1. What shipped / merged this session

- **D-046 — UI test harness (merged, `b7d5e4b` lineage via #67).** vitest + @testing-library/react
  + jest-dom + jsdom as devDependencies; a CI Node step that *visibly runs and can fail* (proven
  red on first push); one `bandFor()` smoke test. Closes the "tests-first can't reach the UI" gap
  before UI-depth §3.1 builds on it. Blast radius verified nil at runtime (two-stage image;
  `test_image_contents.py` green). The `@esbuild` cross-platform lock gap was caught and fixed by
  regenerating the lock inside `node:20-alpine`.
- **The rerun itself — 4 of 5 folded.** See §3. This is operational, not a code merge, but it is
  the session's main deliverable and it (mostly) landed.

---

## 2. The finding that ate the session — requeue replays a frozen, stale recipe (→ D-047)

**Symptom.** The rerun produced zero folds on first attempt. All four large targets OOM'd with the
tell `at chunk_size=None` — i.e. **unchunked**, despite `TIER_RECIPE['rental']` reading
`chunk_size=64` since D-042. IGF2R (2491 aa) asked for **230 GiB**; the card has 44.

**Root cause.** The fold recipe is snapshotted into the job's `inference_settings` **at enqueue
time** and never refreshed. The five were first enqueued *before* D-042, when the rental recipe was
`chunk_size=None`. D-042 corrected the *recipe table* — not the *already-stamped jobs*.
`requeue_jobs` (D-044) resets status/claim/error/attempts but **does not re-read `TIER_RECIPE` or
refresh the recipe** — so it faithfully replayed the pre-D-042 config that had failed these targets
the first time. The requeue did exactly what it said and re-ran the exact failure.

**Why no test caught it.** Every recipe test asserts the *table* is correct (it is) and that
enqueue *stamps* it (it does). No test covered the seam where a recipe changes *after* jobs are
already enqueued — because that seam only matters on a requeue-after-recipe-change, which had never
happened until D-042's change met D-044's requeue on these specific pre-D-042 jobs. A genuinely
latent bug: correct components, an untested interaction.

**A second bug rode alongside it — the requeue/worker race.** While diagnosing, each manual
requeue flipped the jobs to `pending`; the still-running worker claimed them within its 5-second
poll and re-failed them before the recipe could be corrected — so the DB kept reading `failed`
seconds after a `requeued=N` success. Resolved by **stopping the worker before editing**, then
requeue → stamp → restart as an unraced sequence. Worth recording as an operational hazard: *never
edit a job a live worker can claim.*

---

## 3. The rerun result — 4 of 5, honestly

| Target | Acc | aa | Result | mean_pLDDT | Band (D-039) |
|---|---|---|---|---|---|
| ADAM17 | P78536 | — | ✅ complete | 72.78 | Confident backbone |
| SDK1 | Q7Z5N4 | 2213 | ✅ complete | 58.01 | Low |
| NOTCH2 | Q04721 | 1652 | ✅ complete | 57.89 | Low |
| PTPRZ1 | P23471 | 1612 | ✅ complete | 30.68 | **Very low** |
| IGF2R | P11717 | 2491 | ❌ documented ceiling | — | — |

- **ADAM17** folded even unchunked (small enough); it was the lone success of the broken first
  attempt. The other four required the recipe fix.
- **PTPRZ1 at 30.68** is a real result, not a failure — but it is **very low** and must be rendered
  as such (D-024): a 30.68 shown next to ADAM17's 72.78 without the band context would misread as
  comparable. The confidence panel / D-039 bands exist for exactly this.
- **IGF2R (2491 aa) — documented A6000 ceiling.** OOM'd at chunk-64 (needed 11.84 GiB, 10.82 free,
  33.59 resident — not fragmentation; `expandable_segments` was set), then OOM'd at **chunk-32 with
  byte-identical numbers**: 11.84 GiB tried, 10.82 free, 33.59 resident. **The failing allocation is
  invariant to chunk_size** — halving 64→32 moved nothing — which means it is *not* the
  chunk-mitigated triangular attention but a **length-driven cost D-042's chunking does not reach**.
  The precise finding: *IGF2R (2491 aa) exceeds the A6000 44 GiB ceiling; the failing 11.84 GiB
  allocation is chunk-invariant (64 and 32 fail identically), so no smaller chunk saves it.* chunk-16
  was **not attempted** — it would provably produce the same allocation. This is a legitimate
  measured result, rendered honestly by D-043, and it is a real characterization of where the
  triangular-attention chunking runs out for long sequences.

**The fix path, recorded for reproducibility.** Recipe reached the fold after a **guarded one-time
manual `UPDATE`** of `inference_settings.chunk_size` (None→64, later →32 for IGF2R) on the requeued
jobs — worker stopped first, only `pending` rows, only that key via `jsonb_set`, asserted row count.
Not a silent edit: recorded here and in D-047. It changes an *input* recipe; the fold records what
it *actually* ran (`fold_provenance`), so no provenance was faked.

**D-045 paid off, verified end-to-end.** `_capture_environment()` returned four populated values
live on the pod (`torch 2.8.0+cu128`, `transformers 5.14.1`, `NVIDIA RTX A6000`, `cuda 12.8`) — the
first time it ran under real CUDA anywhere, since CI has none. And the capture **persisted through
the upload path into Postgres**: all four folded records carry `metadata.fold_provenance.torch_version
= 2.8.0+cu128` and `device_name = NVIDIA RTX A6000`. The stored `chunk_size` is also accurate
per-target — `64` on the three that needed the recipe fix (PTPRZ1, NOTCH2, SDK1), `None` on ADAM17
(folded unchunked on the broken first attempt, before any fix, and honestly recorded as such). The
provenance is not just present but *true to what each fold actually did*. (Note: provenance lives in
`protein_analyses.metadata->'fold_provenance'`, not a top-level column — the runbook's
`meta.fold_provenance` shorthand points here.)

---

## 4. The environment reality vs. the docs (two stale-doc corrections owed)

- **torch pin mismatch.** `worker/requirements.txt` pins `torch==2.11.0+cu128` (the *local/Blackwell
  S-003* measurement). The A6000 pod ships **2.8.0**, and `pip install -r requirements.txt` hit
  plain PyPI (no `+cu128` wheels there) and failed. Resolved per the guide's own intent — *"any
  recent PyTorch image is fine; install the rest on top"* — by folding on the pod's 2.8.0 and
  installing only the non-torch stack (which resolved to the exact pins: transformers 5.14.1,
  accelerate 1.14.0). Consistent with the prior rental (closeout 2026-07-23 line 160). **The rent
  guide's Step 7 install line is stale and should be fixed.**
- **Token length check is wrong.** The runbook asserts `length == 69`; the real token is **64**.
  The check false-alarmed twice. Should read 64, or better, "matches the Fly secret length."

---

## 5. Corrections-caught pattern, extended

This session is a dense instance of the project's core discipline — *reason from the artefact, not
the summary*:

- The pod's torch was verified from `_capture_environment()` output, not the template label.
- The recipe bug was found by reading the OOM's `at chunk_size=None` string, not assuming the
  local `TIER_RECIPE` value reached the worker.
- The requeue/worker contradiction (`requeued=4` vs. DB `failed`) was resolved by reading
  `worker_id`/`claimed_at`, not by re-trusting the command's success message.
- FAT2/MUC16 "can we fold them" was answered from the manifest (D-022 named exclusions), not recall.

---

## 6. Carried hazards & open items

- **IGF2R resolved — documented ceiling** (chunk-invariant OOM at 64 and 32; chunk-16 not attempted
  as it would fail identically; see §3). Not an open item; a recorded result.
- **D-047 not coded.** The *cure* is ruled (recipe resolved at fold-time in `build_fold_spec`, not
  frozen at enqueue) and spec'd for Code, tests-first, but **not written, not merged.** Until it is,
  every failed-target rerun needs the manual recipe patch. This is the top of the next queue.
- **The manual DB edits are live in prod.** Four jobs (five counting IGF2R) had
  `inference_settings.chunk_size` hand-set. Correct and recorded, but they are hand-edits to
  production rows; D-047's fold-time cure makes such edits never necessary again.
- **Teardown complete.** PAE pulled (4/4, "safe to terminate", exit 0) *before* terminate; D-045
  provenance verified in stored records; pod terminated and 50 GB volume deleted; console confirmed
  **$0.00/hr**. No billing leak.
- **UI-depth §3.1** — provenance panel tests were to be written against the D-045 shape this
  session; deferred by the rerun firefight. Harness (D-046) is ready for them.
- **Cancer-association enrichment (ruled, not built)** — per-target disease context, curated CSV in
  `data/`, cited, no live retrieval, no CDC. MUC16 (CA-125) is the poster child. Needs its entry +
  the owner's curation pass.

---

## 7. Definition of done — met, with exceptions named

- **D-046 harness:** shipped, tests-first, merged, CI-enforced. ✅
- **The rerun:** **4 of 5 folded** ✅, all with verified persisted provenance. IGF2R = documented
  A6000 ceiling (chunk-invariant OOM). ✅ The bug that blocked it is found and a cure ruled.
- **Teardown:** **complete** — PAE secured, provenance verified, pod terminated, volume deleted,
  $0.00/hr confirmed. ✅
- **D-047 fold-time recipe cure:** ruled + spec'd. **Not coded.** ❌ — next session's first task.
- **UI-depth §3.1:** not started. ❌ — harness (D-046) ready for it.
