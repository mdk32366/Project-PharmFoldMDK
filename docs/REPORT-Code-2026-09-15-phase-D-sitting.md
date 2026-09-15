# REPORT — Code → Planner — 2026-09-15 · Phase D DONE: 37 re-attached (480 → 517), 3 duplicates collapsed, `0014` applied, tunnel closed

**Governs:** `ORDERS-Code-2026-09-16-reattach-and-collapse (6).md`, Amendments 1–7.

**Where this file lives:**
- `C:\Users\mdk32\Downloads\` (owner)
- branch **`d167-phase-d-sitting`** as `docs/REPORT-Code-2026-09-15-phase-D-sitting.md` (A4.8)

**Evidence:**
- Sitting logs and `capture.json` committed at **`63f0807`** on `d167-phase-d-sitting` (pushed).
- Every claim below names its log file or Code's independent measurement.

**Session date:** 2026-09-15, America/Los_Angeles (PDT, UTC−7).
- Owner stated: no enqueue running, and no model change this session.
- No tunnel and no worker at the start.

**How the sitting ran:** the owner at the keyboard in one Windows PowerShell 5.1 window ("B"), with the
tunnel in window "A". Code read each pasted output against `D-167` and gave the next step. **Code passed
no owner flag** (`F-075`).

---

## 1. Result

| step | log | result |
|---|---|---|
| 0 tunnel | `00-tunnel-open.txt` | `fly mpg proxy kyzl60xz9zyrpj9g -p 16391` → `remote [fdaa:62:76d9:0:1::9]:5432`; `fly mpg status` Direct IP `fdaa:62:76d9:0:1::9` → **MATCH**. Exactly one listener (pid 10376, bound by name). |
| 0 environment | (console) | `PYTHONUTF8=1` + console UTF-8; probe **`exit: 0`, `10003`** (A7.3) |
| 1 before-witness | `01-witness-before.txt` | **`witness: 480`**, exit 0 |
| 2 capture | `02-capture.txt` | on the machine: **`captured 40 of 40`**, 101,174 bytes, sha256 `88820b8240c0a777bb808b003b1dfbc0bbabf4de924c2ccb6e308eafb82f93bb`, `captured_at 2026-09-15T18:47:03.214691Z`; sftp transferred 101,174 bytes; local sha256 **identical** |
| 3a re-attach dry run | `03-reattach-dry.txt` | verify all met (identity 37/37, pLDDT 40/40); probe calibrated; `D-159: ACCEPTED`; siblings **`{'esmfold': 480}`**; 40 rows == `state_before.json`; `DRY RUN`, exit 0 |
| 3b re-attach write | `04-reattach-owner.txt` | **`✓ RE-ATTACHED 37 rows; every structure serves the captured bytes and provenance.`**, exit 0 |
| 3c after-witness | `05-witness-after.txt` | **`witness: 517`**, exit 0, same key |
| 4a collapse dry run | `06-collapse-dry.txt` | the three `F-077` pairs, no others; 0 referencing rows (5 FKs + JSON parent); all three **BYTE-IDENTICAL**; `DRY RUN`, exit 0 |
| 4b collapse write | `07-collapse-owner.txt` | **`✓ COLLAPSED 3 duplicate rows. No duplicate tile identity remains.`**, exit 0 |
| 5 `0014` | `08-alembic.txt` | target guard `127.0.0.1:16391/pharmfoldmdk`; current **`0013_cancer_burden`** → `Running upgrade 0013_cancer_burden -> 0014_enqueue_identity_unique` exit 0 → current **`0014_enqueue_identity_unique (head)`**; `DATABASE_URL still set: False` |
| 6 close | `09-tunnel-closed.txt` | owner: tunnel closed; `url` and `PYTHONUTF8` removed; Code at 19:03:25Z: **no listener** on 16300–16499; only the Fly agent remains |

**Byte identity re-measured in step 4:**

| pair | size | sha256 prefix | pLDDT |
|---|---|---|---|
| 3673 / 3693 | 1,035,465 B | `8e10627102bea252…` | 60.29 |
| 3674 / 3695 | 1,041,945 B | `87b4477d4ba26f3f…` | 64.27 |
| 3675 / 3696 | 1,011,732 B | `2c5a80c7126eccca…` | 59.66 |

The dropped rows' volume artifacts (`/data/artifacts/3693|3695|3696/structure.pdb`) were **left in place**.

**Timeline** (local PDT, from log write times): tunnel 11:37 · witness 11:44 · capture 11:47 · dry run 11:49 ·
**re-attach 11:51** · witness 11:53 · collapse dry 11:55 · **collapse 11:57** · **`0014` 12:01** ·
closed by 12:03. The re-attach was written **4 minutes** after capture, inside its 60-minute validity.

---

## 2. What Code measured independently, from outside the scripts

1. **Tunnel destination.** Code read `fly mpg status kyzl60xz9zyrpj9g` itself (metadata, no database) and
   the listener table: one process, `fly.exe mpg proxy kyzl60xz9zyrpj9g -p 16391`.
2. **Transfer.** Code re-hashed `data/control/d167/capture.json`: `88820b82…93bb`, 101,174 bytes.
3. **Dry-run plan, recomputed from committed files only** (volume dump + `progress.csv`). Jobs 4869,
   4870, 4871 and 4905: `mean_plddt` and `completed_at` = `folded_at + wall_seconds` **equal to the
   microsecond** (e.g. 4869: `15:24:37.429153 + 19.2 s = 15:24:56.629153Z`).
4. **Re-attach, via the public read API** (anonymous GETs, after step 3b):
   - **37/37** `GET /api/analyses/{job+1}/structure` → 200 with sha256 == capture; **0 mismatches**.
   - `fold_provenance` == captured `provenance.json` for jobs 4869, 4874, 4887, 4905; `structure_source`
     `esmfold`.
   - Job 4874 serves `mean_plddt 75.05`, the highest of the 37, as the committed dump placed it.
   - Control job 4866 unchanged.
5. **Collapse, via the public read API** (after step 4b):
   - analyses 3673/3674/3675 → **200** (record and structure);
   - analyses 3693/3695/3696 → **404** (record and structure).
6. **`0014` committed, not rolled back.** `alembic_version` is updated in the **same transaction** as the
   `CREATE UNIQUE INDEX` (transactional DDL). So a separate `alembic current` reading `0014 (head)` means
   the index committed. That is the `D-017` silent-rollback class, ruled out by a second read rather than
   by the upgrade's exit code. The index's existence also proves no duplicate tile identity remains.
7. **Evidence integrity in git.** The committed blob `63f0807:data/control/d167/capture.json` hashes to
   `88820b82…93bb`, identical to the verified file.

---

## 3. Findings from the sitting

1. **A3.2 resolved — the role mismatch is a role default, not the proxy.**
   - Every role preamble read `session_user 'pharmfoldmdk-app'`, `current_user 'schema_admin'`,
     `rolconfig ['role=schema_admin']`, `rolsuper False`.
   - The login role carries `SET role = schema_admin`, which is why Phase B's `current_user` was
     `schema_admin`.
   - **`jobs_owner 'schema_admin'`, `can_build_jobs_index True`,** so A4.2's wait did not trigger.
2. **A6.1's fix proven in production conditions.** The lines A6.1 and A7.2 named as crash-after-commit
   printed cleanly in the owner's real terminal:
   - `d167_reattach.py:594` (`✓ RE-ATTACHED`)
   - `d166_collapse_duplicate_tiles.py:303` (dry run's last line)
   - `:328` (`✓ COLLAPSED`, after the irreversible delete)
   - `:331`
3. **The `.env` `DATABASE_URL` still targets the stale port 16380.**
   - The sitting's `$url` took **only the credential** from it (user `pharmfoldmdk-app`); the owner named
     `127.0.0.1:16391` explicitly.
   - That is operator-named, not inferred: tunnel corroborated in step 0, `D-159` marker accepted in
     every script, alembic target guarded in step 5.
   - ⚠ For the close-out: `.env` pointing at a dead port is `D-162` amendment 1's hazard waiting for the
     next proxy on 16380.
4. **A placeholder URL reached step 1 once** (`01a-witness-attempt1-placeholder-url.txt`, **not
   committed**, §5).
   - `$url` was set to the literal instruction text `<user>:<password>`.
   - psycopg failed authentication **before any session existed**: no role preamble, no identity read,
     no count.
   - A shape check (`host / port / db / user / placeholder=False`, no password echoed) was added before
     the retry.
5. **Console paste hygiene.** The owner re-ran two log-write lines with a stale `$out`
   (`04-reattach-owner.txt`, `07-collapse-owner.txt`). Code confirmed both files still hold the owner-run
   output (`✓ RE-ATTACHED …`/`exit: 0`; `✓ COLLAPSED …`/`exit: 0`). One step's output arrived only via its
   log file (`05`), which Code read.
6. **Cosmetic (Code's bug):** the dry-run plan prints `{'job_id': '...'}` where a bare `...` was intended.
   No effect. Close-out.
7. **`capture.json` line endings.**
   - The committed blob is byte-exact (§2.7).
   - A **fresh Windows checkout** under `core.autocrlf` would rewrite it with CRLF and change its
     sha256.
   - Phase E verifies from the blob (`git show <rev>:data/control/d167/capture.json | sha256sum`).
     Close-out: add `data/control/d167/capture.json -text` to `.gitattributes`.

---

## 4. Proposal on E.1 — which witnesses still need a database read

| E.1 witness | status |
|---|---|
| `--witness` 517 (Phase B read 480 on the same key) | **done in the sitting** (`01`, `05`) |
| `f078_identity_check` on the capture, 37/37 | **met inside `verify()`** (`03`/`04` line 1). Code can re-run it disk-only from the committed `capture.json` in Phase E. |
| `DUPLICATES_SQL` returns 0 | **implied twice, not read directly.** The collapse re-read the duplicate set inside its transaction and refuses to commit if any remain, and `0014`'s unique index could not build over one. |
| `alembic current` = `0014` | **done** (`08`) |
| census untouched: complete run-1 rows **3,651** | ⚠ **NOT read.** Needs a database read. |

**Proposal:** one short **read-only** tunnel in Phase E. It would carry the census 3,651 count, and a
direct `DUPLICATES_SQL` read if the Planner wants the implication replaced by a measurement. It should be
a committed read-only script (the `d167_read_state.py` pattern, A1.8), not ad-hoc SQL. Or the Planner
rules §2.6 plus the collapse's in-transaction check sufficient for duplicates, and schedules only the
census read.

---

## 5. ⚠ Owed ruling — the A6.5 scan hit

**The pre-commit scan** covered every sitting log plus `capture.json`: credential patterns **and the
literal password**, read in-process from `.env` and never printed; length 32, so the probe could hit.

**Result:**
- **Literal password: 0 hits in every file.**
- Pattern hits: **one file**, `01a-witness-attempt1-placeholder-url.txt`, the word `password` ×2. Both are
  the psycopg line `FATAL:  password authentication failed for user "<user>"`, with the placeholder user
  and no credential.

**Action taken:** A6.5 reads *"Any hit stops the commit."* Code did not relax it.
- The **11 clean files are committed** (`63f0807`).
- `01a` is **held untracked** in the working tree.

**Ruling owed (owner/Planner):** commit `01a` as the record of the failed attempt, or keep it out. It
contains an 8 KB traceback and no secret.

---

## 6. Error accounting — Code, this sitting

1. **A commit command failed to parse** (PowerShell read `<user>` inside the message as an operator).
   Parse errors stop before the first statement, so nothing was scanned, staged or committed. Retried
   with the message in a file (`git commit -F`), staged set confirmed empty first.
2. **Code's tool blocked `Remove-Item` twice** (misparsed as a protected path). Worked around with
   `$env:X = $null` and timestamp checks. No effect on the owner's terminal.
3. **The first capture-command check** (Invoke-Expression with `--%` inserted by `-replace`) was tested
   against the argv stand-in before the owner ran it: argc 4, exact `-C` shape, payload byte-for-byte.
   **Carried in, not an error:** A5.4's limit (the real `flyctl` hop) was exercised for the first time by
   the owner, and it worked.

---

## 7. What remains

**Owner:**
- the §5 ruling on `01a`
- walk the live site for E.2 once Code names the URLs from the live route table

**Planner:**
- §4 (the E.1 census read)
- §3.3 and §3.7 into the close-out

**Code, Phase E:**
- E.1 disk-only witnesses (identity 37/37 from the committed capture blob)
- name the E.2 walk URLs
- the debt-paying commit:
  - delete `tests/test_f078_owed_restore.py` (its refusal test already lives in
    `test_f078_restore_refused.py`)
  - the `OWED_RESTORE` → PAID notice, keeping **DO NOT RE-FOLD**
  - `F-078` amendment 3, the `F-077` / `D-166` notes
- `CLOSEOUT-2026-09-16.md` in the tree

**Close-out list so far:**
- make printed output ASCII (`:328` first), with a cp1252-pipe test
- Code's PowerShell tool injects `PYTHONIOENCODING`
- the `{'job_id': '...'}` print
- `.env` stale port 16380
- `capture.json` `-text`
- no Fly health checks
- the date-label mismatch
- the NO ROW pointer residual
- the 13-file pointer pin
- `working_tree_clean` naming
- `esmfold_local` vs `esmfold`
- slice 4 scope ruling (A1.5)
- Phase B tunnel-evidence miss
- the stray `C:\tmp` file
- the `gh run watch` early exit
- Planner errors 1–6
