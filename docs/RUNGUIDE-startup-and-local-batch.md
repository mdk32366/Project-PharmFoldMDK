# Run Guide — Starting the App, and Folding the Local Cohort

Two parts: **(A)** how to bring the system up from cold tomorrow, and **(B)** how to fold the
42 local-tier targets tonight. Both assume the deploy is live on Fly (it is — it stays up).

---

## A. Cold start — one command

The Fly app stays running between sessions — you don't redeploy to use it. What you re-establish
each session is the **local side** (proxy, env, worker), and `dev-up.ps1` does all of it:

```powershell
cd C:\Projects\Project-PharmFoldMDK
git pull                            # get any overnight Code merges
.\scripts\dev-up.ps1                # proxy + verify + worker (a folding session)
.\scripts\dev-up.ps1 -NoWorker      # proxy + verify only (enqueue / UI-arc days)
```

**One-time prerequisite:** copy `.env.example` to `.env` and fill in the real `WORKER_AUTH_TOKEN`
(the *same* value as the Fly secret — not the DB password) and the DB password in `DATABASE_URL`.
`.env` is gitignored and must never be committed.

`dev-up.ps1` loads `.env`, opens the MPG proxy on the **fixed port 16380**, waits for it, verifies
the DB with a real query (not just the port) and prints the job counter, verifies the worker's
token against the live transport, then launches the worker — each in its own window. It **fails
loudly and does not start the worker** if `.env` still has placeholders, the tunnel is dead, or
the token is wrong — the two silent failures from the first-fold night, both now caught up front.

**Why the port is pinned to 16380:** `fly mpg proxy` takes `--local-port` and defaults to 16380,
so the port is stable, not random. That is the fact that makes `DATABASE_URL` fully static in
`.env` with nothing to probe or prompt for. Don't change it without changing `.env` to match.

**Watching a fold:** `fly logs -a pharmfoldmdk`. `204` = idle; `200` = claimed; then `/artifacts`
and `/complete`. The worker window shows the fold itself (weight load, the int8 `MatMul8bitLt`
notice — both normal).

### Manual fallback (if the script misbehaves)

The by-hand sequence, kept for when the script needs bypassing. Three terminals:

**1. Terminal 1 — venv:**
```powershell
cd C:\Projects\Project-PharmFoldMDK
& .\.venv\Scripts\Activate.ps1
git pull
```
**2. Terminal 2 — proxy on the fixed port, LEAVE IT OPEN:**
```powershell
fly mpg proxy gjpkdonnmkeoyln4 --local-port 16380
```
Closing this window drops the tunnel.

**3. Terminal 1 — point at the tunnel** (password comes from your `.env`, never written here):
```powershell
$env:DATABASE_URL="postgresql+psycopg://fly-user:<DB_PASSWORD_FROM_YOUR_ENV>@localhost:16380/pharmfoldmdk"
```

**4. Verify the connection BEFORE trusting it** (the tunnel drops silently — not optional):
```powershell
python -c "import os,sqlalchemy as sa; print('jobs:', sa.create_engine(os.environ['DATABASE_URL']).connect().execute(sa.text('SELECT count(*) FROM jobs')).scalar())"
```
A number = live. A hang or error = the tunnel isn't up; redo step 2.

**5. (When folding) Terminal 3 — start the worker:**
```powershell
cd C:\Projects\Project-PharmFoldMDK
& .\.venv\Scripts\Activate.ps1
$env:WORKER_AUTH_TOKEN="<the token from your .env — same as the Fly secret>"
python -m worker.main
```
It goes quiet after startup — that is healthy (it only logs on activity). Confirm it's polling
from the app side: `fly logs -a pharmfoldmdk` should show `POST /jobs/claim ... 204` every ~5 s.

---

## B. Fold the 42 local-tier targets (tonight)

**42 `local`-tier rows.** `--bucket local` filters on **tier**, and tier is orthogonal to
disposition (D-024 iv, as `core/manifest.py`'s own docstring states): the bucket is 40 `ranked`
(`sliced_ecd`) **plus 2 `held_out` (`whole`)** — verified
`Counter({('ranked','local','sliced_ecd'): 40, ('held_out','local','whole'): 2})`. The guide
previously said 40; that counted only *ranked-and-local* and dropped the two held-out local rows
(`Q9NV96`/TMEM30A, `O14798`). NOT all 82 — the 13 `untested` (440–630 aa) route to rental (D-024)
and could exceed the local ceiling and take the host down (S-004); the 16 rental and 13
no-topology are not for local hardware. Idempotency (D-026 iii) means NECTIN4 (already folded) is
skipped automatically.

**The one command** (#50's enqueue CLI has a tier filter, confirmed — the flag is `--bucket`):
```powershell
python -m core.enqueue --bucket local        # enqueues the 42 local targets; --dry-run to preview
```
Each foldable row prints `created=1` (or `existed=1` for NECTIN4, already folded). Run
`python -m core.enqueue --help` to see all flags (`--accession`, `--bucket`, `--limit`, `--dry-run`).

**Fallback — enqueue the 42 explicitly** (if you'd rather list them; NECTIN4 harmlessly skipped).
The first 40 are the `ranked` local rows; the last two (`Q9NV96`/TMEM30A, `O14798`) are the
`held_out` local rows `--bucket local` also lands:
```
Q5BKX6 P55064 Q8TDU6 Q8IYL9 P51810 Q3KNW5 Q9NRM0 Q01814 Q9BXS9 O95832
P32302 Q9UPC5 Q9NQ40 P19397 P24530 Q15858 P09693 O75954 O60637 O95858
Q9UP95 O75841 Q8ND94 Q53GD3 Q99835 Q14CZ8 Q9GZU1 O00478 P42081 Q9BXP2
Q5VUB5 Q13433 Q96NY8 Q9BY67 P22607 O95196 P08195 P50281 Q5ZPR3 O00592
Q9NV96 O14798
```
PowerShell loop:
```powershell
$local = "Q5BKX6 P55064 Q8TDU6 Q8IYL9 P51810 Q3KNW5 Q9NRM0 Q01814 Q9BXS9 O95832 P32302 Q9UPC5 Q9NQ40 P19397 P24530 Q15858 P09693 O75954 O60637 O95858 Q9UP95 O75841 Q8ND94 Q53GD3 Q99835 Q14CZ8 Q9GZU1 O00478 P42081 Q9BXP2 Q5VUB5 Q13433 Q96NY8 Q9BY67 P22607 O95196 P08195 P50281 Q5ZPR3 O00592 Q9NV96 O14798".Split(" ")
foreach ($a in $local) { python -m core.enqueue --accession $a }
```
Each prints `created=1` (or `existed=1` for NECTIN4). All 42 land as `pending` jobs.

**Then let the worker chew through them.** With the worker running, it claims and folds them
one at a time, FIFO (D-009). 42 folds × ~1–2 min each (cold weights on the first, warm after)
≈ **about an hour**, unattended. Watch progress:
```powershell
python -c "import os,sqlalchemy as sa; c=sa.create_engine(os.environ['DATABASE_URL']).connect(); import collections; print(collections.Counter(r[0] for r in c.execute(sa.text('SELECT status FROM jobs')).fetchall()))"
```
`Counter({'complete': 42})` = done.

**⚠ The tunnel must stay up for the whole batch** — the enqueue writes need it, though the
*folds* run worker↔Fly and don't. If the tunnel drops mid-enqueue, some targets won't land;
re-run the loop (idempotent, safe) once it's back.

**Leave the worker and tunnel running** until the counter shows all complete, then Ctrl+C both.
Tomorrow you wake to 42 real structures for the UI to render.

---

## C. The rental batch (A6000) — and the ⚠ BLOCKING PAE retrieval (D-035 / D-036)

The 29 above-ceiling targets (13 `unmeasured_local_ceiling` + 16 `over_local_ceiling`) fold on a
rented A6000 — the **same worker loop**, differing only in the FoldSpec (fp16, unquantised,
unchunked). Enqueue them with `python -m core.enqueue --bucket rental`.

**On the rented box, set `WORKER_ARTIFACT_DIR`** — this is the D-036 rental switch. Unset (the
local tier) the worker persists nothing locally; set, each fold's **PAE** is written to
`{WORKER_ARTIFACT_DIR}/{job_id}/pae.json` so it can be transferred out-of-band. The upload no
longer carries PAE (D-035 part 2), so **without this the rental cohort's PAE is never persisted
anywhere.**

```bash
export WORKER_AUTH_TOKEN=<same as the Fly secret>
export TRANSPORT_URL=https://pharmfoldmdk.fly.dev
export WORKER_ARTIFACT_DIR=/workspace/pae          # any pod-local path
python -m worker.main                               # folds; writes each PAE under $WORKER_ARTIFACT_DIR/{job_id}/
```

### ⚠ The batch is NOT done when the last fold completes — it is done when PAE is off the box

D-011 rules **no network volumes** (*"download weights, fold, upload artifacts, terminate"*), so
**PAE on the pod's container disk is destroyed the moment the pod terminates.** structure/plddt/
provenance are already safe on the Fly Volume (they uploaded during the fold); **PAE is not.**
Retrieval is a **blocking pre-termination step**, and the failure is silent and costs a paid
re-fold:

```bash
# still on the rented box, WORKER_ARTIFACT_DIR / TRANSPORT_URL / WORKER_AUTH_TOKEN set:
python -m scripts.retrieve_rental_pae
# → "[pae] transferred 29/29; failed: []"  and  "safe to terminate."   (exit 0)
# → "[pae] ⚠ INCOMPLETE ... do NOT terminate the pod"                   (exit 1)
```

It POSTs each `pae.json` gzipped to `POST /jobs/{job_id}/pae` (D-036), which lands it on the
Volume and sets `pae_json_path` in the same compensated boundary the fold upload uses.
**Idempotent** — re-run until it exits `0`. **Only then terminate the pod.** Gate termination on
that exit code; a partial transfer that is silently dropped is the one failure in this design that
costs real money.

---

## Reference

- App: `pharmfoldmdk` (`sjc`) · Cluster: `gjpkdonnmkeoyln4` / `sentinel-holy-rain-4562`
- Transport: `https://pharmfoldmdk.fly.dev`
- A green deploy = transport up + queue accepting work. **Not** a UI, **not** folds (DEP-004).
- Artifacts land on the Fly Volume at `/data/artifacts/<analysis_id>/`.
