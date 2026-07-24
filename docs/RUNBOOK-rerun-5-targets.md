# Runbook — the 5-target rerun, one pane at a time

**Purpose:** fold the five that failed on the first rental run (ADAM17, IGF2R, NOTCH2, PTPRZ1,
SDK1) and take coverage to the full ranked cohort. **Scope:** operational only — the code is
already shipped (D-042: chunking on, OOM fails cleanly). This runbook exists to make the run
**follow-the-numbers instead of improvise-across-windows**, which is what cost time on 2026-07-23.

**Companion docs:** `GUIDE-renting-the-a6000.md` (the RunPod console clicks, screen by screen) and
`RUNGUIDE-startup-and-local-batch.md` (the local proxy/worker mechanics). This runbook is the
*sequence*; those are the *reference*.

---

## ⚠ Read this first — the rerun is NOT "enqueue + start worker"

The pre-work said *"`core.enqueue` is idempotent; confirm it offers exactly 5."* **That is wrong,
and it would have wasted pod time.** Enqueue idempotency keys on the **`protein_analyses` row**
(`core/enqueue.py:123`), and all five already have one from the first attempt. So
`enqueue --bucket rental` will report them as **`existed`** and create **zero** new jobs.

Their **`jobs`** rows are stuck in whatever state they died in — almost certainly **`claimed`**
(the worker crashed mid-fold on the OOMs, before D-042's `fail()` path existed). The worker only
claims **`status='pending'`**, and there is **no production reaper and no requeue tool** to flip
them back (verified: `reap_stale` has no prod caller). **So the five must be requeued before
renting** — Phase 1 below, one guarded command (`--requeue`, D-044). Skip it and the worker rents,
polls, gets `204 empty`, and folds nothing.

---

## The three panes — name them, keep them open

| Pane | Where | What lives here | Rule |
|---|---|---|---|
| **A — LOCAL** | PowerShell on your Windows box | git, enqueue/requeue, DB queries, `fly logs` | your home base |
| **B — TUNNEL** | PowerShell on your box | the MPG proxy, port 16380 | **open it, then leave it alone** — closing it drops the DB |
| **C — POD** | RunPod web terminal (browser) | clone, install, the worker | opened last, closed (terminated) first |

Env vars do **not** cross panes. Pane C's exports live only in Pane C.

---

## Phase 0 — Preflight (Pane A, ~2 min, no cost)

```powershell
cd C:\Projects\Project-PharmFoldMDK
git pull
git log --oneline -1          # write this SHA down — Pane C must match it
python -c "from core.enqueue import TIER_RECIPE; print(TIER_RECIPE['rental'])"
#   → {'dtype': 'fp16', 'chunk_size': 64}   ← chunking MUST be on (D-042). If it says None, STOP.
```

Bring up the tunnel in **Pane B** and leave it running:

```powershell
# Pane B — leave this window open for the whole run
.\scripts\dev-up.ps1 -NoWorker
```

`dev-up.ps1 -NoWorker` opens the proxy on the fixed port 16380, sets `DATABASE_URL`, and verifies
the DB with a real query. If it fails loudly, fix `.env` before going further.

---

## Phase 1 — Requeue the five (Pane A, no cost) ⚠ the step that actually unblocks the rerun

Enqueue **cannot** re-offer these (idempotency keys on the analysis row, which exists), so use the
purpose-built requeue (D-044). It resets only the **non-`complete`** jobs to `pending`, clears the
stale claim/error, and **leaves any already-folded target untouched**:

```powershell
python -m core.enqueue --requeue P78536 P11717 Q04721 P23471 Q7Z5N4
#   → requeued: requeued=5 skipped_complete=0 not_found=[]
```

**`requeued=` is your "exactly N" check** — the number still needing a fold (5, or fewer if some
already landed; a `complete` one shows in `skipped_complete` and is safe). **`not_found` must be
`[]`** — a listed accession the command exits non-zero on, so a typo is loud, not silent.

Confirm they are `pending` and claimable before spending on a pod:

```powershell
@'
import os, sqlalchemy as sa
accs = ["P78536","P11717","Q04721","P23471","Q7Z5N4"]   # ADAM17 IGF2R NOTCH2 PTPRZ1 SDK1
e = sa.create_engine(os.environ["DATABASE_URL"])
q = sa.text("SELECT pa.input_value AS acc, j.status, j.attempts FROM jobs j "
            "JOIN protein_analyses pa ON j.analysis_id=pa.id WHERE pa.input_value IN :a "
            "ORDER BY acc").bindparams(sa.bindparam("a", expanding=True))
with e.connect() as c:
    for r in c.execute(q, {"a": accs}): print(dict(r._mapping))
'@ | python -
```

Expect five rows, each `status=pending`, `attempts=0`.

---

## Phase 2 — Rent and start the worker (Pane C, the browser terminal)

RunPod console steps are in `GUIDE-renting-the-a6000.md` (Steps 1–7). Two notes for *this* run:
- **With chunking on, VRAM need is far lower** — any secure ≥24 GB card folds these. An A6000
  (48 GB, ~$0.49/hr) is plenty and cheaper than the Blackwell that got auto-provisioned last time.
- Leave **SSH off**; the web terminal is enough. Container disk **50 GB**. **No network volume.**

Once the pod's web terminal is open, paste this block. **Match the SHA to Phase 0.**

```bash
cd /workspace
git clone https://github.com/mdk32366/Project-PharmFoldMDK.git
cd Project-PharmFoldMDK
git log --oneline -1        # ← MUST equal the Phase 0 SHA. STOP if not.
pip install -r worker/requirements.txt
```

**Environment — paste the token inside SINGLE quotes** (double quotes are what truncated it to 12
chars and cost 70 minutes last time), then let the box *prove* it before you spend anything:

```bash
export WORKER_AUTH_TOKEN='<paste the Fly-secret token here, single-quoted>'
export TRANSPORT_URL="https://pharmfoldmdk.fly.dev"
export WORKER_ARTIFACT_DIR="/workspace/rental_artifacts"
export WORKER_ID="rental-rerun"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True   # cheap insurance vs fragmentation
mkdir -p "$WORKER_ARTIFACT_DIR"

# ⚠ the token check that would have saved 70 minutes:
echo "token length = ${#WORKER_AUTH_TOKEN}  (must be 69)"
test ${#WORKER_AUTH_TOKEN} -eq 69 && echo "OK" || echo "STOP — re-paste the token, it is truncated"

nvidia-smi                  # confirm the card and that it is idle
```

**Start the worker DETACHED** so a dropped browser tab can't kill it, and confirm it's alive:

```bash
nohup python -m worker.main > /workspace/worker.log 2>&1 &
sleep 8 && tail -n 25 /workspace/worker.log
```

Healthy = it loads and goes quiet (it only logs on activity). If you see **`AUTH REJECTED`**, the
token is wrong — stop and re-export (D-042 made this loud and fatal on the first poll). You can now
**leave Pane C**; the worker survives the tab closing.

---

## Phase 3 — Watch from home (Pane A)

```powershell
fly logs -a pharmfoldmdk
```

Want: repeating `claim → 200`, `artifacts → 204`, `complete → 204`. A `claim → 204` means the
queue is empty — for the first ~30 s that's just startup; persistently, it means the requeue
didn't land (recheck Phase 1). Progress query, any time:

```powershell
@'
import os, sqlalchemy as sa
accs = ["P78536","P11717","Q04721","P23471","Q7Z5N4"]
e = sa.create_engine(os.environ["DATABASE_URL"])
q = sa.text("SELECT pa.input_value AS acc, j.status, pa.mean_plddt FROM jobs j "
            "JOIN protein_analyses pa ON j.analysis_id=pa.id WHERE pa.input_value IN :a "
            "ORDER BY acc").bindparams(sa.bindparam("a", expanding=True))
with e.connect() as c:
    for r in c.execute(q, {"a": accs}): print(dict(r._mapping))
'@ | python -
```

**Chunking trades speed for memory** — these are the biggest folds in the cohort (up to ~2,491 aa)
and will run slower per residue than the unchunked ones. Budget time, not just dollars. **If one
still OOMs, it now fails cleanly and the batch continues** (D-042) — that target's row will read
`failed` with the reason, which the coverage view now renders (D-043). That is an acceptable
outcome, not a disaster.

---

## Phase 4 — ⚠ Pull the PAE off the box BEFORE terminating (Pane C)

The container disk is destroyed on terminate; structure/pLDDT already uploaded during the fold,
**PAE did not**. Back in Pane C (re-export the three env vars if the tab was closed):

```bash
cd /workspace/Project-PharmFoldMDK
python -m scripts.retrieve_rental_pae
#   → "transferred N/N; failed: []   safe to terminate."   (exit 0) → good
#   → "⚠ INCOMPLETE ... do NOT terminate"                  (exit 1) → re-run, it is idempotent
```

**Do not proceed to Phase 5 until this exits 0.**

---

## Phase 5 — Verify, terminate, delete the volume (Pane A, then Pane C)

Confirm the five are done and coverage moved (Pane A):

```powershell
@'
import os, sqlalchemy as sa
accs = ["P78536","P11717","Q04721","P23471","Q7Z5N4"]
e = sa.create_engine(os.environ["DATABASE_URL"])
q = sa.text("SELECT pa.input_value AS acc, j.status, pa.pdb_path IS NOT NULL AS folded, "
            "pa.pae_json_path IS NOT NULL AS has_pae FROM jobs j "
            "JOIN protein_analyses pa ON j.analysis_id=pa.id WHERE pa.input_value IN :a "
            "ORDER BY acc").bindparams(sa.bindparam("a", expanding=True))
with e.connect() as c:
    for r in c.execute(q, {"a": accs}): print(dict(r._mapping))
'@ | python -
```

Then the live surface — the coverage endpoint should climb with no redeploy:

```
https://pharmfoldmdk.fly.dev/api/coverage
```

**Then, and only then:**
1. **Pane C / RunPod console → Terminate** the pod (trash icon, not "Stop" — Stop keeps billing).
2. **Delete the network volume** if one exists (it bills monthly even after terminate). It should
   read **$0.00/hr** afterward.
3. Close Pane B (the tunnel) and Pane C.

---

## If something goes wrong

| Symptom | Meaning | Do |
|---|---|---|
| `claim → 204` forever | No `pending` jobs | Phase 1 requeue didn't land — rerun it, check `requeued rows` |
| `AUTH REJECTED` on start | Truncated/wrong token | Re-export single-quoted; confirm length 69 |
| A fold OOMs | Still above even the chunked ceiling | **A result, not a crash** (D-042) — row goes `failed` with reason, batch continues |
| Worker gone after tab closed | Not detached | You skipped `nohup` — restart with the Phase 2 nohup line |
| Unsure whether to terminate | | **Don't.** Phase 4 must exit 0 first. An extra hour is cents; a lost PAE set is a paid re-fold |

---

## Reference

- App `pharmfoldmdk` (`sjc`) · Cluster `gjpkdonnmkeoyln4` · Transport `https://pharmfoldmdk.fly.dev`
- The five: **ADAM17** P78536 · **IGF2R** P11717 · **NOTCH2** Q04721 · **PTPRZ1** P23471 · **SDK1** Q7Z5N4
- Recipe for all five: `fp16` / **chunk-64** — a *third* provenance recipe, distinct from local
  (int8/chunk-64) and the other 38 rental folds (fp16/unchunked). `meta.fold_provenance` records it.
</content>
</invoke>
