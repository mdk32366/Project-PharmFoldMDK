# REPORT — Code → Planner — 2026-09-15 · Phase C: C.0 quoted, `D-167` + `F-080` written

> ⚠ **Committed per `ORDERS` A4.8** (reports travel through the repository). The body is the file the
> owner uploaded, byte for byte below this note. ⚠ It was written against orders `(2)` and **predates
> Amendment 4**; A4.2 (ownership), A4.3 (tunnel), A4.4 (session) supersede its §1.7, §3 and §6 where
> they differ, and `D-167` amendment 1 records them.

**Governs:** `ORDERS-Code-2026-09-16-reattach-and-collapse (2).md` (Amendments 1–3) and the owner's C.0
instruction.
**Branch:** `d167-reattach`, pushed, **no PR yet**.
- `540848a`: `state_before.json` (B.3)
- `2634ca3`: `D-167` + `F-080`, pointers and guards

**Parent:** `main` @ `51fea11`, which is PR #326 + PR #327 merged.
**Session date:** 2026-09-15, America/Los_Angeles (PDT, UTC−7). `date` read `2026-09-15T09:06:57-0700` /
`2026-09-15T16:06:57Z`.

**Summary:** C.0 found nothing that contradicts §3.4 or Amendment 3. `D-167` is written from the quoted
values. The C.2/C.3 code has **not** been started; Code stopped here so the Planner can read §3 (role and
ownership) first.

---

## 0. Orders check

- **Newest orders:** `ORDERS-Code-2026-09-16-reattach-and-collapse (2).md` (Downloads, 09:08 PDT).
- **Change from `(1)`:** a diff shows one addition only, **Amendment 3** (body lines 126–175). No line of
  the earlier text changed.

---

## 1. C.0 — quoted from `data/control/d167/state_before.json`

`sha256 b825065d79fff36bf8d3fa9f0ec9e9100d7aebc4cead86e11b4f7f25d38580b7`. Expectations: **16 / 16 met.**

### 1.1 Provenance

```
commit              51fea11914d95042edb0799d1d31b110c5ca6572
branch              main
working_tree_clean  true
read_at_utc         2026-09-15T15:59:27.090389+00:00
script              scripts/d167_read_state.py
target              127.0.0.1:16391/pharmfoldmdk as pharmfoldmdk-app
```

- **`working_tree_clean` is true, so there is no D-162 rule 6 stop.**
  - ⚠ It is computed with `git status --porcelain --untracked-files=no`. It states that tracked files
    matched the commit. It says nothing about the untracked scratch in the working tree.
- **`target` is a label, not a measurement.**
  - `as pharmfoldmdk-app` is the URL's username.
  - `identity.current_user` (what Postgres answered) is `schema_admin`, with `transaction_read_only: on`
    and cluster marker `kyzl60xz9zyrpj9g`.
  - The file is not rewritten (`D-129-C`). The field becomes `url_username` in the script (A3.2), and
    `D-167` notes the label.

### 1.2 Controls, jobs 4866–4868

| field | job 4866 (analysis 4867) | job 4867 (analysis 4868) | job 4868 (analysis 4869) |
|---|---|---|---|
| `status` | `complete` | `complete` | `complete` |
| `tier` | `local` | `local` | `local` |
| `attempts` | 0 | 0 | 0 |
| `worker_id` | `local-gpu` | `local-gpu` | `local-gpu` |
| `claimed_at` | `2026-09-13T15:23:36.736005Z` | `2026-09-13T15:23:56.735935Z` | `2026-09-13T15:24:16.755386Z` |
| `completed_at` | `2026-09-13T15:23:56.669599Z` | `2026-09-13T15:24:16.681806Z` | `2026-09-13T15:24:36.578268Z` |
| `error` | NULL | NULL | NULL |
| `pdb_path` | `/data/artifacts/4866/structure.pdb` | `/data/artifacts/4867/structure.pdb` | `/data/artifacts/4868/structure.pdb` |
| `pae_json_path` | `/data/artifacts/4866/pae.json.gz` | `/data/artifacts/4867/pae.json.gz` | `/data/artifacts/4868/pae.json.gz` |
| `structure_source` | `esmfold` | `esmfold` | `esmfold` |
| `mean_plddt` | 66.14 | 58.37 | 58.37 |
| `metadata.fold_provenance.folded_at` | `2026-09-13T15:23:37.539455Z` | `2026-09-13T15:23:57.506865Z` | `2026-09-13T15:24:17.555447Z` |

**Metadata top-level keys** are identical on all three: `band`, `boundary_method`, `census_class`,
`cohort_tranche`, `ecd_end`, `ecd_start`, `fold_length`, `fold_order`, **`fold_provenance`**,
`full_length`, `guards`, `is_census`, `not_scored_reason`, `scored`, `sequence`, `source`, `span_aa`,
`span_definition`, `span_rule`, `tier`, `tier_reason`.

### 1.3 The 37, jobs 4869–4905: distinct values (count)

| column | distinct values |
|---|---|
| `status` | `pending` (37) |
| `tier` | NULL (37) |
| `attempts` | 0 (37) |
| `worker_id` | NULL (37) |
| `claimed_at` | NULL (37) |
| `completed_at` | NULL (37) |
| `error` | NULL (37) |
| `pdb_path` | NULL (37) |
| `pae_json_path` | NULL (37) |
| `structure_source` | `esmfold_local` (37) |
| `mean_plddt` | NULL (37) |
| metadata top-level keys | the controls' 20 keys **without** `fold_provenance` (37) |

- **`fold_provenance` present:** 0 of 37.
- **`analysis_id = job_id + 1`:** 37 of 37 (and 40 of 40 across B.1 item 3).

### 1.4 Residual per control (A1.4)

Residual = `completed_at` − (`fold_provenance.folded_at` + `progress.csv wall_seconds`). Both terms are
UTC, so no conversion is made. `progress.csv`'s local `at` is not read.

The two clocks:
- **`folded_at`: the worker's clock** (the GPU laptop). Stamped at `worker/runner.py:143`,
  `datetime.now(timezone.utc)`, and carried in provenance at `:150`.
- **`completed_at`: the Fly server's clock.** `core/queue.py:184` (`_clock = datetime.now(timezone.utc)`),
  stamped at `:218`.

| job | `completed_at` (server) | `folded_at` (worker) | `wall_seconds` | residual |
|---|---|---|---|---|
| 4866 | 15:23:56.669599 | 15:23:37.539455 | 19.17 | **−0.039856 s** |
| 4867 | 15:24:16.681806 | 15:23:57.506865 | 19.11 | **+0.064941 s** |
| 4868 | 15:24:36.578268 | 15:24:17.555447 | 19.10 | **−0.077179 s** |

**Spread: 0.142120 s**, against the 5 s stop line. **Not exceeded.**

### 1.5 Path format

`pdb_path == /data/artifacts/{job_id}/structure.pdb` and `pae_json_path == /data/artifacts/{job_id}/pae.json.gz`
are **True for all three**.

The format is identical across the controls and equal to `_write_files` (`app/artifacts.py:133`,
`Path(artifact_root) / str(job_id)`).

⚠⚠ **The directory is the JOB id, not the analysis id.** Job 4866's analysis is 4867, and its path
is `/4866/`. A re-attach keyed by `analysis_id` would point each row at its neighbour's structure.
`D-167` states this explicitly.

### 1.6 Secrets (A2.4)

Regex scan of the committed file. Every pattern returned **0 matches**:

```
password  passwd  postgres(ql)?(+driver)?://  ://user:pass@  token  secret  FlyV1  @127.0.0.1
```

The file holds `host:port/database` and a username label, and no credential.

### 1.7 Tunnel evidence — ⚠ STILL OWED BY THE OWNER

Code **cannot** supply the Phase B **Direct IP versus `fly mpg status`**. It must come from the owner.

What Code measured locally is **not** a substitute:
- At `2026-09-15T16:06:57Z`, **nothing was listening on local port 16391**.
- The only `flyctl` process was `flyctl.exe agent run` (PID 14960, started 06:08 PDT), which is the
  agent and not a proxy.
- That shows the tunnel is closed **now**. It says nothing about which cluster the tunnel was bound to
  **during** the read.

---

## 2. Against §3.4 and Amendment 3 — no contradiction found

| clause | measured | verdict |
|---|---|---|
| `structure_source` = the controls' value | controls `esmfold` (3/3); `app/artifacts.py:45` `STRUCTURE_SOURCE = "esmfold"`, written at `:175`; the 37 carry the enqueue value `esmfold_local` (`scripts/task4_slice2.py:211` and siblings) | consistent. A3.1 rules the change; `D-167` states it |
| path format from the controls | §1.5 | consistent |
| `tier = 'local'` | controls `local` | consistent |
| `attempts` preserved | 0 | consistent |
| `worker_id`, `claimed_at` preserved NULL | 37 are NULL; controls carry values | consistent with A3.5, and named as a category |
| `WHERE status = ‹measured›` | `pending` (37) | consistent |
| a read that assumes a complete row has `claimed_at` (grep) | only `core/queue.py:245` stale reaping, `WHERE status = 'claimed'`; none in `app/`, `core/`, `ui/src` | none found |
| a consumer that enumerates metadata keys (grep) | none. `app/reads.py:205` and `:1842` serve `fold_provenance` by name; `core/hold48.py:575` copies meta excluding `fold_provenance` | none found |
| a reader filtering on `structure_source` | `app/reads.py:200` and `:1843` display only | none found |
| §3.4's "~+1–2 s" residual | measured ±0.08 s | a labelled prediction, not a clause. `D-167` records the measurement (A3.3) |

---

## 3. ⚠ One point for the Planner: `0014` needs table OWNERSHIP, not a `CREATE` grant

A3.2 says: *"Migration `0014` needs `CREATE` on `jobs`."*

In PostgreSQL 16, `CREATE INDEX` requires **ownership of the table**. A `CREATE` grant on the schema or
database does not suffice.
- The owner of `jobs` is **UNREAD**.
- If Phase D's effective role (predicted `schema_admin`) does not own `jobs`, `alembic upgrade`
  refuses. That refusal is the check, and it is reported, not worked around.

`D-167` §5 records it this way. **Planner:** confirm, or add `pg_tables.tableowner` for `jobs` to the Phase D
preamble.

### Role per Phase D write, as recorded in `D-167` §5

| step | writes | effective role |
|---|---|---|
| 3 — re-attach | `protein_analyses` ×37, `jobs` ×37 | **predicted `schema_admin`** |
| 4 — collapse | DELETE 3 `jobs` + 3 `protein_analyses` | **predicted `schema_admin`** |
| 5 — `0014` | `CREATE UNIQUE INDEX` on `jobs` | **predicted `schema_admin`** (must own `jobs`) |

**Measured once only:** Phase B's `current_user` was `schema_admin` through a URL naming `pharmfoldmdk-app`.
- `session_user`, `current_setting('role')` and `rolconfig` were not read, so the cause is
  **unestablished**.
- `docs/SPEC-2026-08-19-readonly-role.md` §0 records `fly-user` with role `schema_admin`. That is
  consistent with proxy mapping, and it is not proof of it.

Every Phase D script prints the preamble before its first write. A role different from this table stops
the sitting.

---

## 4. What landed (`2634ca3`)

### `D-167` in `docs/decisions.md`
- The owner ruling, the deep-learning justification, and the superseded re-fold option recorded as weighed.
- §1.2–1.3 quoted as tables.
- The design with every ‹measured› slot filled.
- Precondition 9: the A3.4 check, `round(mean(plddt.json), 2)` == provenance `mean_plddt` for all 40,
  using the runner's rounding (`worker/runner.py:354`). If 4867 or 4868 fails, stop.
- Write step 1: the A3.2 role preamble.
- Write step 4: the A3.1 in-transaction check that the 480 siblings read `{'esmfold': 480}`.
- The two named clocks and the measured residual.
- The role table (§3 above).
- The owner-owed items.
- A "does NOT claim" section.

### `F-080` in `docs/findings.md`
- **Evidence:** `task4_slice2.py:300` (*"Reads the progress file only"*); `progress.csv` holds 517 rows,
  all `ok`, ids 4389–4905, including 37 in 4869–4905; the database reads 480 on keys 1 and 2.
- **Witness:** a database count keyed by id range 4389–4905, reading 480 before and 517 after.
- The third key reads 488 because of `task3_overlap` (3698–3705), so it is **not** the witness.

### Pointers and guards
- **`docs/RESERVED.md`:** `D-167` → `D-168` and `F-080` → `F-081`, with rows added and the superseded
  values recorded (`D-129-C`).
- **Guards:** next-free guards in 13 test files moved **by name** (167 added, 168 barred; `F-` pin 80 → 81,
  highest spent 79 → 80). Nothing was relaxed to a `>=`.
- **Red first, at the assertion:** 20 failed. Then green.

### Suites
- **Guard and D-167 tests:** 461 passed, 3 skipped, 1 xfailed.
- **Full local suite on the staged tree:** **2,677 passed, 0 failed**, 27 skipped, 1 xfailed.
- **CI:** not run yet (no PR).

### Citation invariant
- `UNRESOLVED AND UNRESERVED: ['D-168']`, cited by the bars and without a row. This is the same shape
  `main` had for `D-167` before this commit.
- The `D-`, `F-` and `A-` pointers all report **NO ROW**. This predates this commit (the baseline run on
  `main` showed the same), and it is **not** fixed here.

---

## 5. Error accounting — Code, this session

1. **The first guard sweep silently half-applied.**
   - **Cause:** the test files are CRLF on disk (`autocrlf`), so every multi-line replacement matched
     nothing, while single-line ones applied.
   - **Detected** by the guard tests staying red, not by the sweep's own counts. The counts were printed,
     and the zeros were not read as a failure before the tests ran.
   - **Side effect:** one file (`test_d166_enqueue_idempotency.py`) briefly had mixed line endings.
   - **Corrected:** the sweep was redone after normalising endings. The one remaining pattern (a
     backslash-escaped `\n### D-167`) was fixed by a regex, and each hit was printed before the write.
   - **Final state:** the full suite is green on the staged tree, and git normalises endings on commit.
     `git diff --stat` shows only content changes.

---

## 6. Owed, and by whom

**Owner, before Phase D:**
- The Phase B tunnel evidence (Direct IP versus `fly mpg status`; the tunnel closed).
- Fresh-session confirmation (§0.4). This session is 2026-09-15 PDT.
- The slice 4 scope ruling (A1.5), which stays blocked on the Run-2 identity.

**Planner:**
- §3, the ownership point.

**Code, next (Phase C remainder):**
- **C.2, tests first:** `tests/test_d167_reattach.py` (the mutation set, including the A3.4 pLDDT and
  A3.1 population checks). Move `test_restore_refuses_even_for_the_owner` into
  `tests/test_f078_restore_refused.py`.
- **C.3:** `scripts/d167_reattach.py` and `scripts/d167_volume_capture.py`, with the role preamble in
  all three Phase D scripts including the collapse. Relabel `target` → `url_username` in
  `d167_read_state.py`. Bring `ARCHITECTURE.md` current.
- **PR-2:** CI green on both jobs, then STOP for the owner merge.

**Close-out observations:**
- `db/models.py:120` names `esmfold_local` while the app writes `esmfold` (A3.1).
- The pre-existing NO ROW pointer state (§4).
