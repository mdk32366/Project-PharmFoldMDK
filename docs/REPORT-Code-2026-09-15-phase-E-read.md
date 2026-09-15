# REPORT — Code → Planner — 2026-09-15 · Phase E read: census 3,648 as expected; STOPPED on expectation 3 (identity-keyed), explained 72-for-72 from committed files

**Governs:** `ORDERS-Code-2026-09-16-reattach-and-collapse (7).md` / `(8).md` (identical), Amendment 8.

**Where this file lives:**
- `C:\Users\mdk32\Downloads\`, for the owner
- branch **`d167-phase-e-evidence`** as `docs/REPORT-Code-2026-09-15-phase-E-read.md` (A4.8), committed
  after the tunnel closes and the credential scan passes

**Session:** 2026-09-15, America/Los_Angeles (PDT). The owner ran every production command; Code read
the output.

**Status:** ⚠ **STOPPED per A8.3.** One expectation is NOT MET. No interpretation was acted on. **The
Planner rules.**

---

## 1. What was done, in order

1. **PR #329 merged** by the owner's authorisation: merge commit `d892c96`, 2026-09-15T21:57:40Z.
   - Before merging, CI was green on both jobs: `postgres` 46 passed (40 + the 6 new read tests), 1 skip
     pre-existing.
2. **Owner ruled A8.4: commit `01a`.**
   - Branch `d167-phase-e-evidence` from `main`.
   - `2085cad` committed `01a` + its README line, after a re-scan: literal password absent, no
     credentialed URL, both `password` matches the named psycopg line.
   - `66b7ca1` corrected the README line: Code's PowerShell string had expanded `$url` away.
3. **Tunnel** (`e2-tunnel-open.txt`):
   - proxy remote `[fdaa:62:76d9:0:1::9]:5432` == `fly mpg status kyzl60xz9zyrpj9g` Direct IP;
   - one listener, pid 22464, `fly.exe mpg proxy kyzl60xz9zyrpj9g -p 16391`.
4. **Step 0, owner's terminal:**
   - encoding probe `exit: 0`, `10003`;
   - `$url` shape `127.0.0.1:16391/pharmfoldmdk`, user `pharmfoldmdk-app`, no placeholder;
   - branch `d167-phase-e-evidence`.
5. **The read** (`e3-read-console.txt`; `data/control/d167/phase_e_read.json`, sha256
   `4d8b48861743f2e7804b937b89a81a45081ffed80ec0c524cb4612b7b69d10ec`, re-hashed by Code: match).
   - **Provenance:** commit `66b7ca1`, branch `d167-phase-e-evidence`, `tracked_files_clean: true`, read
     `2026-09-15T22:10:21Z`.
   - **Role:** `pharmfoldmdk-app` → `schema_admin` (unchanged).
   - **Identity:** marker `kyzl60xz9zyrpj9g`, `transaction_read_only: on`.
   - **Exit 2.**

## 2. The readings

| # | expectation | measured | verdict |
|---|---|---|---|
| 1 | `DUPLICATES_SQL` returns no row | `{}` | **MET** |
| 2 | census row-keyed (`run '1'` AND complete) vs the pre-registered table | **3,648**, verdict **expected** | **MET** |
| 3 | census identity-keyed == row-keyed | **3,576** vs 3,648 | ⚠ **NOT MET** |
| 4 | every complete run-1 row holds a `pdb_path` | 3,648 | **MET** |
| 4 | run-1 rows not complete, by status | `{failed: 2, pending: 3}` | **MET** |
| 4 | failed run-1 accessions | `P11717`, `P55073` | **MET** |
| 5 | keep rows 3673/3674/3675 complete with a `pdb_path` | all three | **MET** |
| 6 | `alembic_version` | `0014_enqueue_identity_unique` | **MET** |
| 7 | drop rows 3693/3695/3696 absent from both tables | absent | **MET** |

**A8.2 is now measured.** Row-keyed 3,648 = 3,651 − 3, so **3693 and 3695 were in the key as well** as the
sampled 3696. The census count moved exactly by the collapse, and the identity-keyed count is what it
was before the collapse.

## 3. ⚠ Expectation 3 — analysis, disk-only (`e4-identity-gap-analysis.txt`)

### 3.1 What the diagnostic returned

- The 50 groups listed by the read are **all exactly 2 rows, all whole-protein** (`tile_start`/`tile_end`
  NULL), with **no tile groups**.
- Each pair joins a **low job id (2–78)** to a **high one (138–3,587)**, e.g. `O00478` [4, 2027],
  `O00592` [24, 2496], `O14798` [38, 2100].

### 3.2 The prediction from committed population files: exact

| quantity | value | source |
|---|---|---|
| cohort-82 accessions | 82 | `data/cohort_82_accessions.txt` |
| census accessions (0 repeated) | 3,467 | `data/census/census_manifest.v7.csv` |
| in both | **75** | computed |
| minus overlap accessions with a recorded non-complete cohort-side row | **3** | `P11717` (job 57, tranche 0, failed; `decisions.md:14426`), `Q8WXI7` MUC16 and `Q9NYQ8` FAT2 (tranche 0, not folded; `decisions.md:16683–16684`) |
| **predicted gap** | **72** | |
| **observed gap** | **72** | the read |

All 50 listed groups are inside the cohort ∩ census overlap; none is outside it.

### 3.3 Reading (inference, labelled)

- Each group is **one protein folded twice by design**: once for the 82-target cohort (tranche 0, the
  July folds, hence the low job ids), and once for the census. Both are labelled `run '1'` by
  `backfill_run_label.py`.
  - That the tranche-0 rows carry `run '1'` is corroborated: `P11717` job 57, the cohort fold, is among
    this read's failed run-1 rows.
- **These are not duplicate folds of one identity, and not a data defect.**
- **Expectation 3's key** `(accession, tile_start, tile_end)` omits the population, so it **cannot** equal
  the row count while the cohort and census overlap.
- Code named this exact risk before the read, in the chat on 2026-09-15: *"if run 1 ever held two
  complete whole-protein rows for one accession …"*. Code kept A8.3's expectation as written, added the
  diagnostic, and did not adapt the design.

### 3.4 What is NOT established

- **The un-truncated group list and each row's `cohort_tranche` were not read.** The 72-for-72 match
  assumes the only non-complete rows in the overlap are the three named.
- It does not establish that every pair is tranche 0 + census. Only the low/high job-id split was
  measured, and only for the 50 listed groups.

## 4. ⚠ Code's defect in the read script

`d167_phase_e_read.py` runs its diagnostic query with **`LIMIT 50`**, and prints
*"identities holding more than one complete run-1 row: 50"*.

- **50 is the limit, not a count.** The true number of groups is not in the output; the gap implies 72.
- This is A7.2's class (Planner error 6/7: an absence or size asserted from a truncated read), committed
  by Code in the instrument written to prevent it.
- **Fix:** read the group count with its own `count(*)`, keep the list capped and label it as capped,
  and have a test that a capped list is never printed as a count.

## 5. Rulings owed (Planner)

1. **Expectation 3.** Options:
   - **(a)** Accept §3.2's 72-for-72 derivation from committed files as sufficient, and record
     expectation 3 as a mis-specified key. This needs no further read.
   - **(b)** Specify a population-aware identity key (e.g. adding `cohort_tranche`), and order a
     **second read-only read** through a revised script. It would carry the un-truncated group count
     and each group's tranches, with outcomes pre-registered again.
   - Code does not choose.
2. **The script defect (§4):** fix it in the next PR, or in the close-out.
3. **Next A8.7 step:** whether the E.2 walk and the debt-paying commit proceed on §2's met expectations
   while expectation 3 is ruled.

## 6. Owed now

- **Owner:**
  - close the tunnel (still open at 22:13:44Z, pid 22464);
  - `Remove-Variable url; Remove-Item Env:PYTHONUTF8`.
- **Code, after the closure is confirmed:**
  - verify no listener;
  - write `e5-tunnel-closed.txt`;
  - scan every Phase E log + `phase_e_read.json` for credentials, including the literal password;
  - commit to `d167-phase-e-evidence` with this report.
  - No PR until the Planner rules.

**Unchanged and later:** rotate `fly-user` and `WORKER_AUTH_TOKEN`, then drop `DATABASE_URL` from `.env`
(A8.6, owner's timing).
