# Renting the A6000 — a step-by-step walkthrough

**For:** the owner, first time using RunPod. **Companion to:** `ORDERS-rental-fold.md`, which
says *what* to do; this says *how*, click by click.

**Before you start, the reassuring version of what this is:** you are renting one Linux machine
with a big GPU, by the second, opening a terminal in your browser, running the same worker you
already run at home, and then deleting the machine. There is no Kubernetes, no Docker to write,
no cluster. **Expected cost: a few dollars.** Expected wall-clock: an hour or two, mostly
unattended.

**The two things that actually cost money if you get them wrong:**
1. Leaving the pod running after the folds finish. (Set a reminder. Terminate when done.)
2. Terminating *before* pulling PAE off the box — that data is unrecoverable without paying to
   re-fold. **Step 9 exists entirely to prevent this.**

---

## Step 0 — Prerequisites (do these before opening RunPod)

- [ ] **Code's pre-flight is green** — 27 rows, MUC16/FAT2 absent, recipe `fp16`/`chunk_size=None`,
      and you have the `origin/main` short SHA written down.
- [ ] **Your repo is public, or you have a GitHub token.** The pod has to clone it. Public is
      simpler; if it is private, generate a fine-grained read-only PAT beforehand.
- [ ] **Have these values to hand** (you will paste them into a terminal):
      - `WORKER_AUTH_TOKEN` — the same value as the Fly secret, from your local `.env`
      - `TRANSPORT_URL` = `https://pharmfoldmdk.fly.dev`

---

## Step 1 — Account and payment

1. Sign up at `console.runpod.io/signup`, verify email, enable 2FA.
2. **Add a payment method and buy a small amount of credit.** RunPod is prepaid — if you skip
   this you will hit the prompt at deploy time anyway. **$10 is more than enough** for this job.

---

## Step 2 — Start a Pod

Click **+ New** in the top-right of the console and choose **Pod**. (Or **Pods** in the left
sidebar, then deploy.)

**Note:** RunPod is mid-rollout of a new deploy flow, so you may see either an "early access"
layout or the legacy one. The *fields* are the same in both; only the arrangement differs.

---

## Step 3 — Pick the template (the container image)

Choose an **official RunPod PyTorch template** — something like
`runpod/pytorch:...-cuda...-devel-ubuntu22.04`. Any recent PyTorch/CUDA image is fine.

**Why a PyTorch image rather than a bare Ubuntu one:** it already has CUDA, Python, and torch
installed, which is the slow, fiddly part. You will still `pip install` transformers and friends,
but the GPU stack is done.

**Two options to set here:**
- **Start Jupyter notebook** — leave it on (harmless, and it gives you a file browser).
- **SSH terminal access** — **you can leave this OFF.** You do not need SSH keys for this job;
  the browser web terminal is enough. Turning it on means generating and pasting a public key,
  which is the single most annoying part of RunPod for a first-timer. **Skip it.**

---

## Step 4 — Pick the GPU

Select **RTX A6000 (48 GB)**. D-011 ruled this: more VRAM for less money than a 4090, and
headroom matters more than speed for a one-time batch.

- Prefer **Secure Cloud** over Community Cloud — D-011's ruling; community hardware can be
  pre-empted mid-run, and this batch is too short and too cheap to accept interruption risk.
- **Region:** anything. Leave it on *Any region*.
- If the A6000 shows **Out of capacity**, either pick another ≥24 GB card (a 4090 or A5000 will
  fold 1,652 aa fine at fp16) or use *Deploy when available*. **Do not downgrade below 24 GB.**

---

## Step 5 — Storage

- **Container disk:** bump it to **50 GB**. The ESMFold weights are several GB and the PAE files
  will accumulate. The default is often too small and running out mid-batch is an avoidable
  failure.
- **Persistent storage:** **NO network volume.** D-011 rules this explicitly — network volumes
  bill $0.07/GB/month even while the pod is stopped, and this is a one-time batch.
  Volume disk is fine, or none.

---

## Step 6 — Deploy

Check the **Summary** panel: A6000, on-demand, ~$0.49/hr, no network volume. Click **Deploy Pod**.

Initialization takes **30 seconds to 5 minutes** while the image is pulled. When it is ready, the
**Connect** button becomes active.

---

## Step 7 — Open a terminal and set the machine up

Click your pod → **Connect** → **Web Terminal** (start it, then open it). You now have a root
shell in a browser tab.

Paste these in order. **Replace the two placeholder values with your real ones.**

```bash
# 1. Get the code — MUST be the merged main you verified in pre-flight
cd /workspace
git clone https://github.com/mdk32366/Project-PharmFoldMDK.git
cd Project-PharmFoldMDK
git log --oneline -1        # ← compare this SHA to the one from pre-flight. STOP if different.

# 2. Install the worker stack
pip install -r worker/requirements.txt

# 3. Environment — the third line is the one that prevents silent data loss
export WORKER_AUTH_TOKEN="<paste the same token as the Fly secret>"
export TRANSPORT_URL="https://pharmfoldmdk.fly.dev"
export WORKER_ARTIFACT_DIR="/workspace/rental_artifacts"
export WORKER_ID="rental-a6000"
mkdir -p "$WORKER_ARTIFACT_DIR"

# 4. Prove the GPU is what you paid for
nvidia-smi                  # ← should say RTX A6000, ~49 GB
```

**⚠ Do not skip `WORKER_ARTIFACT_DIR`.** Without it, PAE is never written to disk, exists only in
memory, and is discarded when the loop claims the next job. It is unrecoverable without a paid
re-fold. If you open a *second* terminal tab later, you must re-export these — env vars do not
carry across tabs.

---

## Step 8 — Enqueue, then start the worker

**Enqueue from your local machine, not the pod** (the pod has no DB tunnel):

```powershell
# On your Windows box, with the proxy up (.\scripts\dev-up.ps1 -NoWorker)
python -m core.enqueue --bucket rental
```

Expect 27 `created=1` lines. Idempotent — safe to re-run if the tunnel drops.

**Then, back in the pod terminal:**

```bash
python -m worker.main
```

It will go quiet after startup — that is healthy; it only logs on activity. Watch progress from
your local box:

```powershell
fly logs -a pharmfoldmdk
```

You want a repeating `claim → 200`, `artifacts → 204`, `complete → 204`. A `204` on claim means
the queue is empty (i.e. done).

**Now wait.** 27 folds, largest 1,652 aa. The first is slow (weight download + load); the rest
are warm. **Check back periodically rather than watching.**

---

## Step 9 — ⚠ BEFORE YOU TERMINATE: pull the PAE off the box

**This is the irreversible step. The container disk is destroyed on termination.**

Run the retrieval script Code built (`scripts/`, per D-036) from the pod, then **verify** it
landed:

```powershell
# From your local box
python -c "import os,sqlalchemy as sa; c=sa.create_engine(os.environ['DATABASE_URL']).connect(); print(c.execute(sa.text('SELECT count(*) total, count(pae_json_path) with_pae FROM protein_analyses')).fetchall())"
```

**`total` should be 69 and `with_pae` should be 69.** If `with_pae` lags, the transfer is
incomplete — **do not terminate.** Re-run the retrieval (it is idempotent).

---

## Step 10 — Verify, then terminate

```powershell
# All jobs complete?
python -c "import os,sqlalchemy as sa,collections; c=sa.create_engine(os.environ['DATABASE_URL']).connect(); print(collections.Counter(r[0] for r in c.execute(sa.text('SELECT status FROM jobs')).fetchall()))"
```

Then check the live coverage endpoint — it should now read **67 ranked ∧ folded of 82**, with no
code change:

```
https://pharmfoldmdk.fly.dev/api/coverage
```

**Then terminate the pod:** Pods page → your pod → **Terminate** (trash icon) → confirm.

> **Stop ≠ Terminate.** *Stop* keeps the disk and keeps billing you for storage. *Terminate*
> deletes it and stops all charges. **You want Terminate**, and only after Step 9 is verified.

---

## Step 11 — Record the four numbers

For the D-030 / D-011 / D-035 amendments:

1. **Wall clock for NOTCH2 (1,652 aa)** — claim to complete, from the Fly logs. *This is the
   measurement D-030's provisional 3600 s lease has never had.*
2. **Peak VRAM** — run `nvidia-smi` during a large fold, or note if anything OOM'd.
3. **PAE file size for the largest target** — `ls -l` in `$WORKER_ARTIFACT_DIR`. *Tests whether
   the 2.2× gzip ratio measured at 318 aa holds at 1,652.*
4. **Total pod cost** — from the RunPod billing page. *D-011 estimated ~$0.25 for a handful of
   targets; 27 is a different scope.*

---

## If something goes wrong

| Symptom | What it means | What to do |
|---|---|---|
| Worker logs `401` | Token mismatch | Re-check `WORKER_AUTH_TOKEN` against the Fly secret |
| Fly logs show only `204` | Queue is empty | The enqueue did not land — check the tunnel, re-run |
| A fold OOMs | The A6000 ceiling, at last measured | **This is a result** (D-022 left it open). Record it, let the loop continue |
| Pod dies mid-batch | Claimed jobs go stale | The lease reaps them; re-run the worker. Folds already complete are not repeated (D-026) |
| You are unsure whether to terminate | | **Do not.** Check Step 9's `with_pae` count first. An extra hour is $0.49; a lost PAE set is a paid re-fold |

---

## ⚠ Amendment — lessons from the first run (D-042, 2026-07-23)

The body above was written before the first rental run. What it taught, and what changed:

- **Chunk. The recipe now sets `chunk_size=64` for rental (D-042).** The unchunked assumption was
  falsified: the trunk's triangular attention is O(L³), so IGF2R (2,491 aa) asked **230 GiB** on a
  95 GiB card. No card closes that; chunking is the fix. The four oversized targets
  (PTPRZ1/NOTCH2/SDK1/IGF2R) fold under the new recipe.
- **Run the worker DETACHED — `nohup python -m worker.main &` — not in a browser terminal's
  foreground.** A dropped tab killed the shell and the worker, burning ~1 hr of billing for zero
  folds.
- **`WORKER_ARTIFACT_DIR` must be set** or rental PAE lives only in memory and is discarded on the
  next claim — recoverable only by a paid re-fold. The single most expensive omission.
- **A wrong/truncated token now fails LOUDLY in ~5 s** (D-042 §3): the worker stops on the first 401
  instead of polling silently. If you see it stop with "AUTH REJECTED", re-check the token length
  (69 chars) — shell quoting truncated it to 12 last time.
- **A fold that OOMs no longer crashes the worker (D-042 §2)** — it is failed and the batch
  continues. An OOM is a *result* (the ceiling), not a disaster.
- **`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`** — a candidate against fragmentation
  (a 67 GiB OOM held 35 GiB reserved-but-unallocated). Untested; try it if a borderline fold OOMs.
- **Cost reality:** the card was an RTX PRO 6000 at **$2/hr**, not an A6000 at $0.49. Budget
  accordingly, and **delete the network volume after termination** — it bills monthly even stopped.
