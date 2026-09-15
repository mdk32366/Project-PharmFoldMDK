# REPORT — Code → Planner — 2026-09-15 · Phase D readiness: #328 merged and deployed, capture quoting checked, sitting branch ready

**Governs:** `ORDERS-Code-2026-09-16-reattach-and-collapse (4).md` (Amendments 1–5).

**Where this file lives:**
- `C:\Users\mdk32\Downloads\REPORT-Code-2026-09-15-phase-D-readiness.md`, at the owner's request
- `docs/REPORT-Code-2026-09-15-phase-D-readiness.md` on branch **`d167-phase-d-sitting`** (A4.8)

**Session date:** 2026-09-15, America/Los_Angeles (PDT, UTC−7).

**Production access by Code:** none to the database. The reads were Fly control-plane metadata
(`flyctl status`, `flyctl releases`) and two anonymous GETs on the public read API.

**Owner decision:** the sitting runs **together, step by step**. The owner runs every production
command; Code reads each pasted output against `D-167` and says continue or stop. The runbook is fixed
before it is followed where it is wrong.

---

## 1. PR #328 — MERGED, and deployed

| item | value | how known |
|---|---|---|
| authorisation | owner: *"You are authorized to merge 328. Execute"* | owner message |
| pre-merge state | head `5e8f25e`, `OPEN MERGEABLE CLEAN`; checks `test` pass, `postgres` pass, `deploy` skipping | `gh pr view` / `gh pr checks` |
| merge | **merge commit `ee55298b6db8c01e42b080811c4b6d5099c29a18`**, `2026-09-15T17:46:58Z` | `gh pr merge --merge --match-head-commit 5e8f25e…` |
| gate run on `main` | [35003405643](https://github.com/mdk32366/Project-PharmFoldMDK/actions/runs/35003405643), head `ee55298`, **success** | `gh run view` |
| · `postgres` | success, 17:47:07Z → 17:47:54Z | same |
| · `test` | success, 17:47:07Z → 17:50:01Z | same |
| · `deploy` | success, 17:50:04Z → 17:50:54Z | same |
| Fly release | **v235 complete**; v234 was 1h57m earlier | `flyctl releases -a pharmfoldmdk` |
| Fly machine | `807135a6493338`, `sjc`, version 235, **`started`**, last updated 17:50:40Z | `flyctl status -a pharmfoldmdk` |
| local clone | `main` fast-forwarded to `ee55298` | `git log` |

**Health checks:** ⚠ the `CHECKS` column is **empty**, so the app defines no Fly health checks. "Healthy"
here means `started` and serving (below), not a check that passed.

**The public read API on v235** (Code's reading, not the in-sitting calibration the script performs):

| request | result |
|---|---|
| `GET /api/analyses/4867/structure` (control, job 4866) | **200**, 19,239 bytes. Equals `progress.csv` `served_structure_bytes` for job 4866. |
| `GET /api/analyses/4870/structure` (owed, job 4869) | **404** |

**Procedural note:** Code's first deploy watcher (`gh run watch`) exited 1 while both jobs were still
in progress, with no conclusion. It was replaced by a polling loop, and the result above is from
`gh run view` after `status: completed`. No step was taken on the watcher's exit.

---

## 2. Owner preconditions — as stated, and as still owed

| precondition | state |
|---|---|
| #328 merged; deploy finished; machine started | **met** (§1) |
| no tunnel ("bridge") open | **owner confirmed** |
| no worker on the GPU box | **owner confirmed** |
| no enqueue running anywhere | ⚠ **not stated explicitly** by the owner; owed at step 0 |
| A4.4 session question | see below |

The owner asked what "model switch" meant. Code explained: the A4.4 rule is about a session restarted
midway, by **context compaction** (the conversation summarised) or by **changing the model**.

**Code's side:** this conversation began this morning with "resume". No compaction has occurred in it,
and one model (Claude Opus 5) has run throughout.

⚠ **Owed from the owner at step 0:** a plain statement that the model was not changed during the
session. The owner's question implies not, but it has not been stated.

---

## 3. ⚠ A5.4 — the capture's quoting, checked as far as it can be without production

**Method:**
- Print the capture line with the committed script (`--print-capture-command`, at `ee55298`).
- Substitute a stand-in for `flyctl`: the venv Python running a script that records its argv to JSON.
- Run the result as a `.ps1` in **Windows PowerShell 5.1**: once exactly as A5's runbook says (`--%`
  inserted after the executable), and once without `--%`.

### 3.1 Results

| check | result |
|---|---|
| printed line 1 | `flyctl ssh console -C "python -c \"import base64;exec(base64.b64decode('…'))\""`, 4,550 chars |
| printed line 2 | `flyctl ssh sftp get /tmp/d167_capture.json data/control/d167/capture.json` |
| **with `--%`**: argv received | `['ssh', 'console', '-C', 'python -c "import base64;exec(base64.b64decode(\'<b64>\'))"']`, **argc 4** |
| **with `--%`**: `-C` argument shape | **exactly** `python -c "import base64;exec(base64.b64decode('<b64>'))"` |
| **with `--%`**: payload | base64 **decodes to `scripts/d167_volume_capture.py` byte for byte** (3,354 bytes; 4,472 base64 chars) |
| **without `--%`** | ⚠⚠ **BROKEN.** PowerShell reads the `;` inside the line as a statement separator and tries to run `base64.b64decode` as a cmdlet (`CommandNotFoundException`). The argument `flyctl` would receive is a fragment ending `…import base64`. |
| POSIX `sh -c "<received argument>"` | **executes**: `captured 0 of 40 directories under /data/artifacts`, writes `/tmp/d167_capture.json`, prints a sha256 last line, exit 0 |
| **no shell** (POSIX word splitting, `shlex.split`) | argc 3: `['python', '-c', <source>]`, source exactly `import base64;exec(base64.b64decode('<b64>'))` |
| payload line endings | the payload carries **CRLF** (the committed file as checked out on Windows). `compile()` accepts it, and Python's tokenizer normalises line endings identically on every platform. |

### 3.2 What this establishes

- **`--%` is required, not optional.** A plain PowerShell paste of the printed line cannot work.
  A5's runbook instruction is **confirmed by measurement**.
- With `--%`, PowerShell hands the executable the exact `-C` string, with a byte-exact payload.
- That string gives the same three-word command whether the machine runs it **through a POSIX shell**
  or **splits it without one**.
- `flyctl ssh console --help` (v0.4.102) documents `-C` only as *"command to run on SSH session"*, and
  does not say which of those two it does. Both were checked.
- `python` exists on the machine: the runtime image is `python:3.11-slim` (`Dockerfile:23`).

### 3.3 What this does NOT establish

- **The stand-in is not `flyctl`.** Python and Go use Windows argv parsing that agrees on `\"` inside
  double quotes, but `flyctl.exe`'s own parse was **not** exercised.
- **The remote hop was not exercised:** the SSH session, the machine's `/tmp`, and the sftp transfer.
- **A5.4's stop rule stands:** if the capture does not run, stop and report; no hand-typed or edited
  capture.

### 3.4 ⚠ Error — Code wrote a stray file on the owner's machine

- **What happened:** the `sh -c` test was expected to fail at its only write, because `/tmp` resolves
  to `C:\tmp` for Windows Python. **`C:\tmp` existed**, so the capture wrote
  `C:\tmp\d167_capture.json` (3,008 bytes, `captured 0 of 40`).
- **Cleanup:** identified by its `captured_at` (`2026-09-15T17:57:06.267860+00:00`) and
  `root: /data/artifacts`, then removed. The 3 other items in `C:\tmp` were pre-existing and untouched.
- **Lesson:** a test that "expects a failure to contain it" is not containment. The run should have
  been sandboxed, or `/tmp` checked first.
- **Relevance to the sitting:** none. The production capture writes on the machine, and
  `sftp get` targets `data/control/d167/capture.json`. It goes into error accounting.

---

## 4. The sitting branch

- **Branch:** `d167-phase-d-sitting`, from `main` @ `ee55298`.
  - `cdfba1b` adds `data/control/d167/phase_d/README.md`.
  - This report adds `docs/REPORT-Code-2026-09-15-phase-D-readiness.md`.
- **The README** names one log file per step, each holding that step's full console output (A4.8 and
  A5's stop rules):
  - `00-tunnel-open.txt`
  - `01-witness-before.txt` (expect `witness: 480`)
  - `02-capture.txt`
  - `03-reattach-dry.txt`
  - `04-reattach-owner.txt` (exit 3 means report before any revert)
  - `05-witness-after.txt` (expect 517)
  - `06-collapse-dry.txt` (waits if the role cannot build `0014`)
  - `07-collapse-owner.txt`
  - `08-alembic.txt`
  - `09-tunnel-closed.txt`
- **`capture.json`:** committed at `data/control/d167/capture.json` in Phase E.3.

---

## 5. Proposed corrections to the A5 runbook, before it is followed

1. **Python:** use `.\.venv\Scripts\python.exe` everywhere the runbook says `python`, including
   `-m alembic`.
   - `python` on the owner's PATH is `C:\Python314\python.exe` (3.14.3), with SQLAlchemy 2.0.49 and
     psycopg 3.3.5.
   - The venv is Python 3.11 with the locked 2.0.51 / 3.3.4 / alembic 1.18.5 that CI tested.
   - All import under both; only the venv is the tested environment.
2. **`--%`:** keep it (§3). The paste is `flyctl --% ssh console -C "…"`, and nothing may follow it on
   the line.
3. **Working directory:** run every step from `C:\Projects\Project-PharmFoldMDK`. The `sftp get` target
   and the `--capture` path are relative.
4. **`DATABASE_URL` hygiene** (A5.3, supporting evidence): `DATABASE_URL` is **not** persisted at User
   or Machine level, so only the session variable set in step 5 needs removing. Alembic reads
   **only** `os.environ["DATABASE_URL"]` (`db/migrations/env.py:38`, no dotenv), so the `$env:` form
   is what it will use.
5. **Logging in PowerShell 5.1:** do **not** use `Tee-Object` or `>` for the step logs. PS 5.1 writes
   UTF-16, the defect that made the `F-078` volume dump need `decode()`. Proposed form per step:

   ```powershell
   $out = & $py scripts\d167_reattach.py --url $url --witness; "exit: $LASTEXITCODE"; $out
   $out | Out-File -Encoding utf8 data\control\d167\phase_d\01-witness-before.txt
   ```

   ⚠ `$url` holds the tunnel credential. No command echoes it, and it must not be pasted into any log.

**Step 1, ready to run** once the tunnel is bound and its Direct IP is pasted:

```powershell
Set-Location C:\Projects\Project-PharmFoldMDK
$py  = ".\.venv\Scripts\python.exe"
$url = "<tunnel url with 127.0.0.1>"
$out = & $py scripts\d167_reattach.py --url $url --witness; "exit: $LASTEXITCODE"; $out
```

**Expected:** a role preamble, then `witness: 480`, exit 0. Anything else stops the sitting.

---

## 6. Owed

**Owner, at step 0:**
- no enqueue running
- the model was not changed this session
- tunnel bound by name; Direct IP vs `fly mpg status` pasted

**Planner:**
- rule on §5's corrections (or amend)
- note §3.3's limits on A5.4

**Code:** read each step's output live against `D-167`; commit the logs to `d167-phase-d-sitting`;
Phase E after the sitting.

**Close-out additions:**
- §3.4, Code's stray-file error
- §1, the `gh run watch` early exit
- no Fly health checks defined (§1)
