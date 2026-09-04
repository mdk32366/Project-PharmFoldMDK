# Renting hold-48 — RTX PRO 6000 Blackwell runbook

**For:** the owner, folding D-111 tiles on a rented Blackwell card. **Decision:** `D-113`, amended by `D-114`.
**Cite:** D-111 · D-112 · D-113 · D-114 · D-115 · vault **D-0036** (amended; external, not repo D-036) · issue **#210** · PR **#213**.

**This is not a rewrite of** [`GUIDE-renting-the-a6000.md`](GUIDE-renting-the-a6000.md). That
guide is the 2026-07 A6000 / `--bucket rental` path. Hold-48 emit, the D-112 import pin, the
cu128 torch trio, and accession-requeue hazards are different scars. Use this file.

**Companion:** [`BUDGET-hold48-tiers-2026-09-04.md`](BUDGET-hold48-tiers-2026-09-04.md) (measured
IGF2R-pilot walls, length→wall model, tier waves). [`RUNBOOK-rerun-5-targets.md`](RUNBOOK-rerun-5-targets.md)
is the 5-target accession-requeue sequence — **do not follow its `--requeue P11717` line.**

**This PR / this session does not enqueue jobs, does not touch Fly, and does not commit PDB/PAE
binaries.**

**Money pin (Matt/Trinity, this pilot):** card **$2.19/hr** (not $2.00). Fold-only IGF2R
**$0.31** (0.142 GPU-h × $2.19). Setup scars priced separately — not in the other-44
length-weighted forecast. RunPod balance remaining after Terminate: **$14.17** (measured,
not a forecast). ⚠ **D-114:** `$14.17` is **historical**. It does **not** authorize C2.
Matt **tops up before** Wave 0 / other-44 emit. Account ceiling ≈ **$50** for completing
the rental (fold-only + Wave 0 cold-start + expected scars) — **not** a new prediction of
tile hours. D-113 forecasts **stand** (C2 fold-only **$17.97**; all-remaining **$21.16**;
rate **$2.19/hr**; Peak VRAM **UNKNOWN** until Step 5). **Peak VRAM is a named unknown:
UNKNOWN** — do not invent a number. Step 5 (`nvidia-smi` logger) is required on every
cold start. Still not an enqueue GO. Gates unchanged: **3356 persist** → cold **Step 5
`nvidia-smi`** → **Matt GO** before emit.

---

## Process rule (read before any click)

**Cold start on a clean card.** Do not emit from a pod that already burned hours on
pip/ABI/import scars. A clean card is the test that the runbook, not the hot-fixes, is
what works. You do **not** need to be mid a named decision to run this — type the
commands below; scar ids live in the why/non-negotiables, not in the paste.

```
Step 0 — glance RunPod balance (top up if the tank is on E)
        ↓
rent a CLEAN card          (Terminate any scarred pod first — not Stop)
        ↓
setup                      (clone origin/main, cu128 trio, env, nvidia-smi logger)
        ↓
start worker               (nohup)
        ↓
empty-queue prove          (claim → 204; do not emit)
        ↓
retrieve_rental_pae        (must exit 0)  + copy nvidia-smi CSV
        ↓
Terminate
        ↓
only then emit             (Matt GO; balance glance before each wave)
```

Historical (why, not what to type): IGF2R tiles **3589** / **3590** already folded on a
scarred pod. That invoice is Terminate-history. Wave 0 is this general cold start, not a
"re-test after D-NNN."

---

## ⚠ Step 0 — RunPod balance glance (mandatory, D-114)

**Do not start the family vacation with the gas tank on E.**

Check the RunPod **account balance** as a procedure step, not as optional hygiene:

1. **Before renting / deploying a pod** (before Step 1 Deploy).
2. **Before each wave** — Wave **0**, **A**, **B**, **C1**, **C2**.
3. **During long waves** (C2 is the money: 15 h cap, 60 full windows).

This is a **glance** at the console balance. It is **not** a new dashboard, not a
per-second invoice parser, and not fake precision. **"Too cheap to meter"** means **no
extra metering theater** beyond D-113 wave caps / kill switches **plus this glance**.
It does **NOT** authorize skipping the balance check.

`$14.17` at Terminate does not cover C2. If the glance shows the tank on E, **stop** —
top up; do not Deploy, do not emit.

---

## ⚠ Non-negotiables (scars from the IGF2R pilot session)

1. **Never** `python -m core.enqueue --bucket rental`. Hold-48 tiles are `emit_tile_jobs` on
   **one parent**. Census parents stay `jobs.tier` NULL until stitch (D-111). A bucket enqueue
   is the oneshot path the claim guard raises on.
2. **Never** `python -m core.enqueue --requeue P11717`. D-109 ruling 6: IGF2R exists twice.
   Accession requeue walks **every** `jobs` row for that accession — including historical
   **job 57** (`failed`, 2,491 aa, `tier='rental'`) and parent **job 3356** (`jobs.tier` NULL,
   D-047). Requeue a failed **tile** by **job id** only. **Stop the worker first** (5 s claim
   poll will grab a `pending` row mid-edit — D-047).
3. **Never** add SQLAlchemy to `worker/requirements.txt` (D-112). The GPU process must not
   import `core.hold48`.
4. **`retrieve_rental_pae` must exit 0 before Terminate.** Stop ≠ Terminate. Stop keeps
   billing the disk; Terminate destroys PAE on the container disk (D-011 / D-036).
5. **`fly secrets list` does not reveal `WORKER_AUTH_TOKEN`.** Fly lists **names only**.
   Print the value on the **laptop** (Pane A PowerShell in Step 4 / the cheat sheet), paste
   on Pane C **single-quoted**. Length check = **the actual secret length** (**64** in the
   2026-07-24 correction — `CLOSEOUT-2026-07-24-rerun.md` — **not 69**). Confirm with
   `echo ${#WORKER_AUTH_TOKEN}` against the laptop print's length, not against Fly.
   Last resort: `fly ssh console -a pharmfoldmdk -C "printenv WORKER_AUTH_TOKEN"` — do
   **not** invent a `fly secrets` reveal.
6. **Glance the RunPod account balance** before rent, before each wave, and during long
   waves (Step 0). Do not vacation on E. "Too cheap to meter" does **not** skip this.
   (D-114 envelope ≈ $50; `$14.17` at Terminate is historical.)
7. **The git pin is the AST `ImportFrom` assert (D-115), not a file substring and not a
   decision id to hunt.** Abort only on a real `from core.hold48 …`. `1d48d1d` is the crash
   SHA. A `"from core.hold48" not in text` check false-alarms on the D-112 comment.

---

## The three panes

| Pane | Where | What | Rule |
|---|---|---|---|
| **A — LOCAL** | laptop | print `WORKER_AUTH_TOKEN` from `.env`, `fly logs -a pharmfoldmdk`, DB tunnel, emit/stitch | home base; **emit happens here**, never on the pod. Fly cannot print the token. Watch: Fly claim stream (cheat sheet / Step 8) |
| **B — TUNNEL** | laptop | MPG proxy / `DATABASE_URL` | open it, leave it; closing it drops the DB |
| **C — POD** | RunPod web terminal | clone, pip, worker, `tail -f /workspace/worker.log`, PAE retrieve | opened last; **Terminate** (not Stop) when PAE is off the box. Watch: worker log only — a new tab does **not** inherit exports |

Env vars do **not** cross panes. Pane C exports live only in Pane C. A second web-terminal tab
is a new shell — re-export or the worker starts without `WORKER_ARTIFACT_DIR` and rental PAE
exists only in memory (D-036).

---

## Step 1 — Card and pod (RunPod console)

**Card:** RTX PRO 6000 Blackwell class (the IGF2R pilot was **NVIDIA RTX PRO 6000 Blackwell
Workstation Edition**). **This pilot's card rate is $2.19/hr** (Matt/Trinity pin — **not $2.00**).
Dollar figures in [`BUDGET-hold48-tiers-2026-09-04.md`](BUDGET-hold48-tiers-2026-09-04.md) use
that pin. RunPod balance remaining after Terminate of the scarred pod: **$14.17** (measured,
not a forecast). ⚠ **D-114:** `$14.17` is historical; it does **not** authorize C2. Matt
tops up **before** Wave 0 / emit. Account ceiling ≈ **$50**. **Balance glance (Step 0)
before Deploy** — do not start the family vacation with the gas tank on E.

**Image:** official RunPod **PyTorch CUDA** template (`runpod/pytorch:…-cuda…`). Do not start
from bare Ubuntu.

**Storage / tenancy:**

- **Container disk ≥ 50 GB.** ESMFold weights + PAE (tile0 `pae.json.gz` was **18,908,543 B**).
- **NO network volume.** D-011: network volumes bill monthly even while the pod is stopped.
- **Secure Cloud** (not Community). Community can pre-empt mid-fold.
- **SSH optional / off is OK.** The browser web terminal is enough. Turning SSH on is extra
  key-paste with no gain for this job.

**Summary check before Deploy:** Blackwell-class card, on-demand, no network volume, ≥50 GB
container disk. **RunPod balance glanced (Step 0)** — enough for Wave 0 inside the ≈$50
envelope; not the Terminate snapshot of $14.17 treated as a C2 license. Initialization is
30 s–several minutes. Connect → **Web Terminal**.

---

## Pane C — web terminal cheat sheet (copy-paste)

**Cold start on a clean card**, after Step 1 Deploy → **Web Terminal**.
Transcribe **top to bottom**. Why-not, scar tables, and money pins stay in Steps 2–6 and in
D-112 / D-113 / D-114 / D-115 — this section does not rewrite them and does **not** require
hunting those ids to know what to type.

Flow: **rent clean card → setup → worker → empty-queue prove → retrieve → Terminate.**
During a live fold wave, keep the **Watch** paste (Pane A `fly logs` + Pane C `tail -f`) up.

**Never** `pip install -r worker/requirements.txt` first. **Never** pip-install sqlalchemy.
**Never** invent a `WORKER_AUTH_TOKEN`. Token = laptop `.env`, **single-quoted**.

### Pane A — print WORKER_AUTH_TOKEN (laptop, before the Pane C export)

`fly secrets list` names secrets only; it **cannot print values**. Run this in PowerShell at
the repo root, then paste the printed line into Pane C.

```powershell
cd C:\Projects\Project-PharmFoldMDK
(Get-Content .env | Where-Object { $_ -match '^WORKER_AUTH_TOKEN=' }) -replace '^WORKER_AUTH_TOKEN=','' -replace '^["'']|["'']$',''
```

Then Pane C: `export WORKER_AUTH_TOKEN='…'` **single-quoted**. `echo ${#WORKER_AUTH_TOKEN}`
must match the laptop length (**64** in the 2026-07-24 correction, **not 69**).

Last resort (does **not** invent a `fly secrets` reveal):

```powershell
fly ssh console -a pharmfoldmdk -C "printenv WORKER_AUTH_TOKEN"
```

### Tab 1 — clone through card check

```bash
cd /workspace
git clone https://github.com/mdk32366/Project-PharmFoldMDK.git
cd Project-PharmFoldMDK
git fetch origin main
git checkout origin/main
git log --oneline -1
# STOP if this SHA is 1d48d1d — that checkout imports hold48 (sqlalchemy) and will crash.
# origin/main is the pin. The AST block below is the check — do not hunt a decision id.
# Walk ImportFrom nodes only. Do not grep file text (a comment contains the substring).

python - <<'PY'
import ast
from pathlib import Path
tree = ast.parse(Path("worker/main.py").read_text(encoding="utf-8"))
imps = [n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
assert not any(n.module == "core.hold48" for n in imps), "real hold48 import — abort"
assert any(
    n.module == "core.contracts"
    and any(a.name == "TILE_WINDOW_AA" for a in n.names)
    for n in imps
), "missing TILE_WINDOW_AA from core.contracts — abort"
print("ok: worker imports TILE_WINDOW_AA from core.contracts only")
PY

pip install \
  torch==2.11.0+cu128 \
  torchvision==0.26.0+cu128 \
  torchaudio==2.11.0+cu128 \
  --index-url https://download.pytorch.org/whl/cu128

pip install \
  transformers==5.14.1 \
  bitsandbytes==0.49.2 \
  accelerate==1.14.0 \
  httpx==0.28.1

python - <<'PY'
import torch, torchvision, torchaudio, transformers
print("torch", torch.__version__)
print("torchvision", torchvision.__version__)
print("torchaudio", torchaudio.__version__)
print("transformers", transformers.__version__)
assert torch.__version__.startswith("2.11.0") and "+cu128" in torch.__version__
assert torchvision.__version__.startswith("0.26.0")
assert torchaudio.__version__.startswith("2.11.0")
assert transformers.__version__ == "5.14.1"
# D-112 live: worker.main must import with sqlalchemy absent
import sys
sys.modules.pop("sqlalchemy", None)
import worker.main  # noqa: F401
print("ok: worker.main imported; device", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NO CUDA")
PY

export WORKER_AUTH_TOKEN='<paste the Pane A print — single-quoted>'
export TRANSPORT_URL=https://pharmfoldmdk.fly.dev
export WORKER_ARTIFACT_DIR=/workspace/rental_artifacts
export WORKER_ID=rental-hold48-blackwell
export WORKER_TIER=rental
export WORKER_FOLD_IN_CHILD=1
# optional — cheap insurance vs allocator fragmentation (D-042); untested as a fix, not a requirement:
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

mkdir -p "$WORKER_ARTIFACT_DIR"

echo "token length = ${#WORKER_AUTH_TOKEN}  (must equal the Pane A print; 64 in the 2026-07-24 correction, not 69)"

nvidia-smi   # must name an RTX PRO 6000 Blackwell class card
```

### Tab 2 — VRAM CSV logger (Step 5; required on every cold start)

A second web-terminal tab is a new shell. **Do not re-export here** — this is just `nvidia-smi`
(D-036: a second tab that starts a worker without `WORKER_ARTIFACT_DIR` loses PAE).

```bash
nvidia-smi --query-gpu=timestamp,name,memory.used,memory.total,utilization.gpu \
  --format=csv -l 10 | tee /workspace/nvidia-smi-hold48.csv
```

### Tab 1 — detached worker

```bash
cd /workspace/Project-PharmFoldMDK
nohup python -m worker.main > /workspace/worker.log 2>&1 &
sleep 8 && tail -n 40 /workspace/worker.log
```

### Watch — live fold wave (copy-paste; keep both panes up)

**Pane A (laptop)** — Fly claim stream:

```powershell
fly logs -a pharmfoldmdk
```

Want repeating `claim → 200` then `artifacts` / `complete`. Persistent `claim → 204` = empty rental queue (or `WORKER_TIER` wrong). `401` = token. Do not redeploy Fly to "fix" a worker problem.

**Pane C (pod web terminal)** — worker log. After the `nohup` above. **A new tab does not inherit exports — do not start a second worker; only tail.**

```bash
tail -f /workspace/worker.log
```

Snapshot (same one-liner as after `nohup` / Step 6):

```bash
tail -n 40 /workspace/worker.log
```

### Tab 1 — empty-queue prove, then retrieve, then Terminate

Cold start: do **not** emit from Pane A. Same Pane A command as **Watch**. Persistent
`claim → 204` on Fly logs is success (empty queue).

When done — even if `$WORKER_ARTIFACT_DIR` is empty, confirm the script's report — then
Terminate. Re-export the env block if this tab was closed.

```bash
cd /workspace/Project-PharmFoldMDK
python -m scripts.retrieve_rental_pae
#   → "transferred N/N; failed: []" and "safe to terminate."   (exit 0) → good
#   → "⚠ INCOMPLETE ... do NOT terminate"                        (exit 1) → re-run (idempotent)
# Copy /workspace/nvidia-smi-hold48.csv off the box too.
```

Then RunPod console → **Terminate** (trash), not Stop.

---

## Step 2 — Git pin (Pane C)

**Transcribe from the cheat sheet above.** Checkout `origin/main`. The AST assert is the pin
— you do not hunt a decision id to know what to type.

**Why (D-112 / D-115):** `1d48d1d` is the D-111 worker. That commit's `worker/main.py` does
`from core.hold48 import TILE_WINDOW_AA`. `core.hold48` imports sqlalchemy at module top. The
GPU image does not have sqlalchemy → `ModuleNotFoundError: sqlalchemy` on
`python -m worker.main`. D-112 moved the integer to `core.contracts`; the worker imports it
**from there only**. Minimum live pin was PR **#213** (`733c41f`); later `main` tips are fine
if the AST assert prints ok.

⚠ **D-115 / #217 scar:** a raw `"from core.hold48" not in text` **false-alarms** on current
`main`. Line 29 is `from core.contracts import TILE_WINDOW_AA  # D-111 cap; D-112: never from core.hold48`
— the substring lives in the **comment**. The paste check below is AST `ImportFrom` only.

```bash
cd /workspace
git clone https://github.com/mdk32366/Project-PharmFoldMDK.git
cd Project-PharmFoldMDK
git fetch origin main
git checkout origin/main
git log --oneline -1
# STOP if this SHA is 1d48d1d — that checkout imports hold48 (sqlalchemy) and will crash.
# origin/main is the pin. The AST block below is the check — do not hunt a decision id.
# Walk ImportFrom nodes only. Do not grep file text (a comment contains the substring).

python - <<'PY'
import ast
from pathlib import Path
tree = ast.parse(Path("worker/main.py").read_text(encoding="utf-8"))
imps = [n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
assert not any(n.module == "core.hold48" for n in imps), "real hold48 import — abort"
assert any(
    n.module == "core.contracts"
    and any(a.name == "TILE_WINDOW_AA" for a in n.names)
    for n in imps
), "missing TILE_WINDOW_AA from core.contracts — abort"
print("ok: worker imports TILE_WINDOW_AA from core.contracts only")
PY
```

---

## Step 3 — Pip (Pane C) ⚠ order is load-bearing

**Transcribe from the cheat sheet above.** This step is the cu128-trio / `-r` scar.

The official template's torch is **not** automatically our pin. Align the CUDA trio from the
**same** PyTorch index **first**, then the non-torch worker pins.

```bash
pip install \
  torch==2.11.0+cu128 \
  torchvision==0.26.0+cu128 \
  torchaudio==2.11.0+cu128 \
  --index-url https://download.pytorch.org/whl/cu128

pip install \
  transformers==5.14.1 \
  bitsandbytes==0.49.2 \
  accelerate==1.14.0 \
  httpx==0.28.1
```

**Why not `pip install -r worker/requirements.txt` first:** that file pins
`torch==2.11.0+cu128`. On a fresh venv pip hits **plain PyPI**, which has no `+cu128` wheel,
and the install fails. Documented `CLOSEOUT-2026-07-24-rerun.md` §4. After the cu128 trio is
present, a careful `-r worker/requirements.txt` can satisfy the remaining pins — but the
**trio must already be the cu128 builds**. `worker/requirements.txt` does **not** pin
torchvision/torchaudio; they still have to come from that index.

**HOT scars (this session):**

| # | Symptom | Cause | Do |
|---|---|---|---|
| (a) | `ModuleNotFoundError: transformers` (or bitsandbytes / accelerate / httpx) | incomplete `worker/requirements` install — torch-only, or `-r` aborted | install the four non-torch pins above |
| (b) | torchvision ABI / `nms` error at import or fold | torchvision **not** from the cu128 index | reinstall the trio from `--index-url …/cu128` |
| (c) | torchaudio `c10_cuda_check` (or mixed-build CUDA runtime error) | torchaudio not matched to `torch 2.11.0+cu128` | same trio reinstall; do not mix template torchaudio with cu128 torch |
| (d) | `ModuleNotFoundError: sqlalchemy` on `import worker.main` | D-111 import, **or** someone "fixed" it by adding SQLAlchemy to the GPU reqs | checkout D-112+; **do not** pip-install sqlalchemy on the worker |

Prove the stack before spending on a fold:

```bash
python - <<'PY'
import torch, torchvision, torchaudio, transformers
print("torch", torch.__version__)
print("torchvision", torchvision.__version__)
print("torchaudio", torchaudio.__version__)
print("transformers", transformers.__version__)
assert torch.__version__.startswith("2.11.0") and "+cu128" in torch.__version__
assert torchvision.__version__.startswith("0.26.0")
assert torchaudio.__version__.startswith("2.11.0")
assert transformers.__version__ == "5.14.1"
# D-112 live: worker.main must import with sqlalchemy absent
import sys
sys.modules.pop("sqlalchemy", None)
import worker.main  # noqa: F401
print("ok: worker.main imported; device", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NO CUDA")
PY
```

Recipe at fold-time is `TIER_RECIPE['rental']` = **fp16 / chunk 64** (D-047). Do not hand-edit
`inference_settings` to change it.

---

## Step 4 — Environment (Pane C)

**Transcribe from the cheat sheet above.** Token = **Pane A print**, pasted **single-quoted**.

`fly secrets list` names secrets only; it **cannot print values**. On the laptop (Pane A),
PowerShell at the repo root:

```powershell
cd C:\Projects\Project-PharmFoldMDK
(Get-Content .env | Where-Object { $_ -match '^WORKER_AUTH_TOKEN=' }) -replace '^WORKER_AUTH_TOKEN=','' -replace '^["'']|["'']$',''
```

That command **displays** the value for copy. Then Pane C:

Paste the token inside **SINGLE quotes**. Double quotes + a `$` or history expansion truncated
it to 12 characters on 2026-07-23 and burned ~70 minutes of silent 401s. D-042 made a 401 fatal
in ~5 s; the length check is still the thing that catches the paste **before** the worker
starts.

```bash
export WORKER_AUTH_TOKEN='<paste the Pane A print — single-quoted>'
export TRANSPORT_URL=https://pharmfoldmdk.fly.dev
export WORKER_ARTIFACT_DIR=/workspace/rental_artifacts
export WORKER_ID=rental-hold48-blackwell
export WORKER_TIER=rental
export WORKER_FOLD_IN_CHILD=1
# optional — cheap insurance vs allocator fragmentation (D-042); untested as a fix, not a requirement:
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

mkdir -p "$WORKER_ARTIFACT_DIR"

echo "token length = ${#WORKER_AUTH_TOKEN}  (must equal the Pane A print; 64 in the 2026-07-24 correction, not 69)"
# Do not proceed until Pane C length == Pane A length.
```

Last resort (does **not** invent a `fly secrets` reveal):

```powershell
fly ssh console -a pharmfoldmdk -C "printenv WORKER_AUTH_TOKEN"
```

⚠ **`WORKER_TIER` defaults to `local`.** A rental worker that forgets this export claims
nothing (claim SQL is `AND tier = :tier`, never NULL — F-035 / D-090). Hold-48 **parents** are
NULL-tier on purpose and stay unclaimable. Tiles are `tier='rental'`.

⚠ **`WORKER_FOLD_IN_CHILD=1`** is D-082 layer 3. It changes process topology (fold in a
persistent child so a segfault does not kill the crank). Print at start must read
`D-082 layer 3 ENABLED`. ASCII-only banners — an em dash on the wrong codepage kills the
worker at startup.

⚠ **`WORKER_ARTIFACT_DIR` is the D-036 switch.** Unset → PAE never hits disk → destroyed on
the next claim, recoverable only by a paid re-fold.

---

## Step 5 — Prove the card and start a VRAM log (Pane C) ⚠ required on every cold start

**Transcribe from the cheat sheet above** (tab 1 `nvidia-smi`, then tab 2 logger).

**Peak VRAM is a named unknown (D-113 budget).** It is **UNKNOWN**. Do not invent a GiB from
"L=1608 fitted" or from the card's advertised capacity.

This step is **not optional on a cold-start pod.** Start the logger **before**
`python -m worker.main`, even if the cold start emits nothing: an empty queue will not produce a
peak, but the logger must already be running when the first later fold starts. Copy the CSV
off the box with PAE (Step 9). Until that file exists, Wave C2 has no VRAM kill switch, only
a wall-time one.

```bash
nvidia-smi   # must name an RTX PRO 6000 Blackwell class card

# second web-terminal tab (re-export nothing here — this is just nvidia-smi):
nvidia-smi --query-gpu=timestamp,name,memory.used,memory.total,utilization.gpu \
  --format=csv -l 10 | tee /workspace/nvidia-smi-hold48.csv
```

Record `memory.used` peak against the job id that was in-flight. That recorded peak is the
only way this unknown stops being unknown. Until then: treat every L≈1656 tile as able to
OOM.

---

## Step 6 — Start the worker DETACHED (Pane C)

**Transcribe from the cheat sheet above.** `nohup` is not optional.

A dropped **browser tab** kills a foreground shell and the worker with it (D-042: ~1 hr billed,
zero folds). `nohup` is not optional.

```bash
cd /workspace/Project-PharmFoldMDK
nohup python -m worker.main > /workspace/worker.log 2>&1 &
sleep 8 && tail -n 40 /workspace/worker.log
```

Healthy startup prints (ASCII):

- `[worker] D-082 layer 3 ENABLED - folding in a child process`
- `[worker] tier=rental - claims ONLY jobs of this tier (F-035)`
- then quiet until a claim (it logs on activity)

If you see **`AUTH REJECTED`**: token wrong or truncated — stop, re-print on Pane A, re-export
single-quoted, re-check length. If you see **`ModuleNotFoundError: sqlalchemy`**: you are on
`1d48d1d` — go back to Step 2. If you see **`ModuleNotFoundError: transformers`**: Step 3 scar (a).

You can now leave Pane C. The worker survives the tab closing. **Re-open later** with the
Pane C Watch command (cheat sheet / Step 8): `tail -f /workspace/worker.log`. A new tab
does **not** inherit exports; don't start a second worker in that tab — only tail.

---

## Step 7 — Emit (Pane A only) ⚠ library, IGF2R-pilot shape, not the CLI

**Cold start:** do **not** emit. An empty queue (`claim → 204`) on a clean card is a
successful **runbook** test: clone, pip, import, env, worker start. Then retrieve (Step 9)
and Terminate. Retrieve is a no-op if `$WORKER_ARTIFACT_DIR` is empty — confirm the
script's report, then Terminate. Historical: IGF2R tiles (jobs **3589** / **3590**) already
exist; do not re-emit them.

**IGF2R pilot emit (already done; do not repeat):** `core.hold48.emit_tile_jobs(session, parent_job, parent_analysis)`
against parent **job 3356** / tranche-5 analysis. Parent `jobs.tier` stays NULL. Children are
`pending` + `tier='rental'`. Domain-snap (UniProt cache, gitignored) produced **L=1608 + L=797**,
not the unsnapped planner's 1656 + 736.

**Never:**

```bash
python -m core.enqueue --bucket rental          # oneshot path — FORBIDDEN for hold-48
python -m core.enqueue --requeue P11717         # hits job 57 + parent 3356
```

**If a tile fails, requeue that job id only, worker STOPPED:**

```python
# Pane A — worker on the pod must be stopped first (kill the nohup PID).
# Replace TILE_JOB_ID. Never pass P11717.
import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from db.dburl import normalize_db_url
from db.models import JobRecord

TILE_JOB_ID = 3589  # example — the failed TILE, not 57, not 3356
engine = create_engine(normalize_db_url(os.environ["DATABASE_URL"]))
with Session(engine) as s:
    job = s.get(JobRecord, TILE_JOB_ID)
    assert job is not None, TILE_JOB_ID
    assert job.tier == "rental", job.tier
    assert job.status == "failed", job.status
    assert job.inference_settings.get("parent_job_id") == 3356
    job.status = "pending"
    job.claimed_at = None
    job.worker_id = None
    job.error = None
    job.attempts = 0
    s.commit()
    print("requeued job", TILE_JOB_ID)
```

Then restart the worker (Step 6).

**After a successful cold start**, emit the other 44 the same way: one parent per
`emit_tile_jobs` call, never a bucket enqueue, never a mucin (`Q8WXI7` / `Q9UKN1` / `Q685J3`
→ `[]` / `out_of_class`). Follow the budget doc's waves and kill switches. **Glance the
RunPod balance before each wave (0 / A / B / C1 / C2)** — Step 0; do not vacation on E.
There is no `python -m core.hold48` CLI on purpose.

Sketch for one remaining parent (do not run in this session):

```python
import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from db.dburl import normalize_db_url
from db.models import JobRecord, ProteinAnalysis
from core.hold48 import emit_tile_jobs, is_mucin, MUCIN_ACCESSIONS

engine = create_engine(normalize_db_url(os.environ["DATABASE_URL"]))
ACCESSION = "…"  # one of the 44, never a mucin, never a second IGF2R emit
assert ACCESSION not in MUCIN_ACCESSIONS and not is_mucin(ACCESSION)
with Session(engine) as s:
    parent_a = s.execute(
        select(ProteinAnalysis).where(
            ProteinAnalysis.input_value == ACCESSION,
            ProteinAnalysis.cohort_tranche == 5,
        )
    ).scalar_one()
    parent_job = s.execute(
        select(JobRecord).where(JobRecord.analysis_id == parent_a.id)
    ).scalar_one()
    assert parent_job.tier is None, parent_job.tier  # D-111 hold
    specs = emit_tile_jobs(s, parent_job, parent_a)
    s.commit()
    print(ACCESSION, [(sp.tile_index, sp.start, sp.end, sp.length) for sp in specs])
```

---

## Step 8 — Watch (Pane A + Pane C)

Keep both streams up during a live fold wave. Same commands as the cheat sheet **Watch**
section — they are here so they are not only in that sheet and not only narrative.

**Pane A (laptop)** — Fly claim stream:

```powershell
fly logs -a pharmfoldmdk
```

Want repeating `claim → 200` then `artifacts` / `complete`. Persistent `claim → 204` = empty
rental queue (or `WORKER_TIER` not `rental`). `401` = token. Do not redeploy Fly to "fix" a
worker problem.

**Pane C (pod web terminal)** — worker log. After
`nohup python -m worker.main > /workspace/worker.log 2>&1 &`. **A new tab does not inherit
exports — do not start a second worker; only tail.**

```bash
tail -f /workspace/worker.log
```

Snapshot (same as Step 6 after `nohup`):

```bash
tail -n 40 /workspace/worker.log
```

**During a long wave (especially C2):** glance the RunPod account balance again (Step 0).
A kill switch stops the wave; an empty tank mid-wave stops the card. Same rule: do not
vacation on E.

Progress is in the DB (tunnel up in Pane B), keyed on **tile job ids**, not accession:

```python
import os
from sqlalchemy import create_engine, text
from db.dburl import normalize_db_url
e = create_engine(normalize_db_url(os.environ["DATABASE_URL"]))
q = text(
    "SELECT j.id, j.status, j.tier, pa.mean_plddt, "
    "j.inference_settings->>'tile_index' AS tile, "
    "j.inference_settings->>'parent_job_id' AS parent "
    "FROM jobs j JOIN protein_analyses pa ON j.analysis_id = pa.id "
    "WHERE j.id = ANY(:ids) ORDER BY j.id"
)
with e.connect() as c:
    for r in c.execute(q, {"ids": [3589, 3590]}):
        print(dict(r._mapping))
```

---

## Step 9 — ⚠ Pull PAE BEFORE Terminate (Pane C)

Structure / pLDDT upload during the fold. **PAE does not.** It lives under
`$WORKER_ARTIFACT_DIR/{job_id}/pae.json` until this script POSTs it (D-036). The container
disk is destroyed on Terminate.

Re-export the env block (Step 4) if the tab was closed.

```bash
cd /workspace/Project-PharmFoldMDK
python -m scripts.retrieve_rental_pae
#   → "transferred N/N; failed: []" and "safe to terminate."   (exit 0) → good
#   → "⚠ INCOMPLETE ... do NOT terminate"                        (exit 1) → re-run (idempotent)
```

**Do not go to Step 10 until this exits 0.** Copy `/workspace/nvidia-smi-hold48.csv` off the
box too if you captured it — that file is how peak VRAM stops being unknown.

---

## Step 10 — Terminate (not Stop)

1. Pane C / RunPod console → **Terminate** (trash), not **Stop**. Stop keeps the disk and
   keeps billing storage.
2. Delete a network volume if one was created by accident (it bills monthly stopped).
3. Close Pane B (tunnel) after the laptop stitch, not before.

---

## Step 11 — Stitch on the laptop (Pane A)

Stitch is **local** (`core.hold48_stitch.write_stitched`). It is not a Fly route and does not
set parent `jobs.tier`. Parent **3356** stays NULL until a later GO writes the stitched
artifacts — **local stitch only so far** (IGF2R pilot).

Do **not** `git add` `*.pdb` / `pae.json` / `pae.json.gz`. Those are binaries; they stay on
disk outside the repo.

```python
import json
from pathlib import Path
from core.hold48_stitch import TileFold, write_stitched

# Load the two IGF2R tile folds from retrieved artifacts (paths local to the laptop).
# Tile 0: job 3589 L=1608; tile 1: job 3590 L=797. Parent ECD length = 2264 (D-111).
# Coordinates: use each tile's inference_settings tile_start / tile_end (1-based inclusive).

def load_tile(start, end, pdb_text, plddt, pae) -> TileFold:
    return TileFold(start=start, end=end, pdb=pdb_text, plddt=plddt, pae=pae)

# tiles = [load_tile(...), load_tile(...)]
# paths = write_stitched(tiles, 2264, Path("artifacts/igf2r_stitch"))  # outside the repo

def prove_off_block_is_null_not_zero(pae_path: Path) -> None:
    pae = json.loads(pae_path.read_text(encoding="utf-8"))
    cells = [v for row in pae for v in row]
    nulls = sum(v is None for v in cells)
    zeros = sum(v == 0 for v in cells)
    print(f"cells={len(cells)} nulls={nulls} literal_zeros={zeros}")
    assert zeros == 0, "off-block PAE must be null, never 0 (D-111)"
    # IGF2R pilot stitch: 2,131,551 null cells, 0 literal zeros.

# prove_off_block_is_null_not_zero(Path(paths["pae"]))
```

A **literal 0** in an off-block cell would assert measured pair-confidence for residues that
never shared a forward pass. The pilot stitch proved nulls, not zeros. Re-run the assertion
on every later stitch.

---

## If something goes wrong

| Symptom | Meaning | Do |
|---|---|---|
| `ModuleNotFoundError: sqlalchemy` | D-111 checkout, or hold48 imported from the worker | `git log -1` must not be `1d48d1d`; worker imports `TILE_WINDOW_AA` from `core.contracts` only. Do **not** pip-install sqlalchemy |
| `ModuleNotFoundError: transformers` | scar (a) | install the four non-torch pins |
| torchvision `nms` / ABI | scar (b) | reinstall cu128 trio from the PyTorch index |
| torchaudio `c10_cuda_check` | scar (c) | match torchaudio to torch `2.11.0+cu128` |
| `AUTH REJECTED` | truncated/wrong token | Pane A PowerShell print; Pane C single quotes; length = laptop print (64, not 69). Fly cannot reveal the value |
| `claim → 204` forever | no pending rental tiles, or `WORKER_TIER` unset (defaults `local`) | export `WORKER_TIER=rental`; do not `--requeue P11717` |
| Worker gone after tab close | not detached | Step 6 `nohup`; do not run `python -m worker.main` in the foreground |
| Unsure whether to Terminate | | **Don't.** Step 9 must exit 0. An extra hour is **$2.19**; lost PAE is a paid re-fold |
| RunPod balance on E (or unknown) | skipped Step 0 glance | **Stop.** Do not Deploy / do not emit. Top up into the ≈$50 envelope. "Too cheap to meter" does **not** skip this |
| Fold OOM | ceiling is a named unknown (peak VRAM UNKNOWN) | D-042: job `failed`, batch continues — **a result**. Record `nvidia-smi`. Do not invent a GiB. Do not raise the 1656 cap |

---

## What the IGF2R pilot already proved (do not re-fold to learn this)

See [`BUDGET-hold48-tiers-2026-09-04.md`](BUDGET-hold48-tiers-2026-09-04.md) for the numbers.
Short version: tile0 L=1608 wall **452.4 s**, tile1 L=797 wall **59.9 s**, recipe fp16 / chunk 64,
torch `2.11.0+cu128`, transformers `5.14.1`, card = RTX PRO 6000 Blackwell Workstation Edition
at **$2.19/hr**. Fold-only IGF2R **$0.31**. Stitch off-block PAE null (2,131,551 null cells,
0 literal zeros) — PASS, **Trinity accepted**. Parent 3356 still NULL-tier. Peak VRAM is a
**named unknown: UNKNOWN** (do not invent a GiB; Step 5 on every cold start).

---

## Reference

- App `pharmfoldmdk` · Transport `https://pharmfoldmdk.fly.dev`
- Geometry: window **1656** / overlap **128** / stride **1528** (`core.contracts`, D-111 / D-112)
- IGF2R `P11717` parent job **3356** (tranche 5, pending, `jobs.tier` NULL). Historical failed
  oneshot = job **57** (tranche 0, 2,491 aa) — retain and mark, never requeue (D-109 ruling 6)
- IGF2R tiles already folded: job **3589** (tile0 L=1608), job **3590** (tile1 L=797)
- Mucins, never ESMFold: MUC16 `Q8WXI7` · MUC12 `Q9UKN1` · MUC17 `Q685J3`
- Recipe: `fp16` / chunk **64**, resolved at claim (D-047)
