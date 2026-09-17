# REPORT — Code → Planner — 2026-09-17 · R1–R4 readiness: steps 0–2 done, the read is owner-gated

**Governs:** `ORDERS-Code-2026-09-17-R1-R4.md` (Planner, 2026-09-17).
**Where this file lives:** `C:\Users\mdk32\Downloads\` for the owner, and branch
`d167-r1r4-population-read` as `docs/REPORT-Code-2026-09-17-R1-R4-readiness.md` (A4.8).

**Session:** **2026-09-17, America/Los_Angeles (PDT, UTC−7)** — session open measured at **10:21 PDT /
17:21 UTC** (`Get-Date`). The `09-17` label is the real calendar date.

**Status:** ⚠ **The read has NOT run.** Steps 0–2 are complete and CI is green. Step 3 (the tunnel) and
step 4 (the four readings) need the owner at the keyboard. **No database contact has occurred.**

---

## 0. The report opens as ORDERS §9 requires

1. **The true base commit is `1e67954`** (the #331 merge), **not `f7d0a9d`**. Code's own prework
   (`docs/PREWORK-2026-09-17.md`) states `f7d0a9d`, which is its parent; `main` moved twice after it —
   `1b69b3d` (the close-out and prework), then `1e67954`. Local was level with `origin/main` at session
   open (`git fetch` + `git status -sb` → `## main...origin/main`).
2. **`docs/RESERVED.md` still reads `D-168` · `F-081` · `A-032`** — the inline pointers, line 327. No
   `### D-168`, `### F-081` or `### A-032` exists in `docs/decisions.md`, `docs/findings.md` or
   `docs/assumptions.md`. Nothing in this branch spends an integer.
3. **The two lines that arrived truncated in Code's earlier chat message, restated in full:**
   - **The `D-169` line.** `SPEC-A-032-surface-and-tail-axes.md` §2.6 owes `D-169` (is a patch-chemistry
     inventory on an **assembled** structure commensurable with one on a single-pass fold?) and §3.7 owes
     `D-170` (does a **tail-derived**, annotation-based axis change what the project claims to be?). The
     Planner's recommendation on both is on the record; the prework's §6 item 5 rules **neither today**,
     after `D-168`. **Code acts on neither.**
   - **The `.env` line.** `.env` still carries `DATABASE_URL=postgresql+psycopg://pharmfoldmdk-app:<credential
     present, redacted>@127.0.0.1:**16380**/pharmfoldmdk`. The port is the **dead** one; the credential is
     **still present**, so rotation (owner decision 2) has **not** happened — which matches the orders'
     §1, where rotation is **deferred deliberately**. The literal-secret scan before commit is therefore
     the only guard, and it ran on every file committed here (§5).

---

## 1. Step 1 — the tranche convention, from source only (ORDERS §3)

⚠ Established from `db/models.py` and the enqueue scripts. **Not from either prework, and not from the
amendment.**

| population | value | established by |
|---|---|---|
| **cohort** (the 82 targets) | `cohort_tranche = 0` | `scripts/census_ingest.py:52` `COHORT_TRANCHE = 0`, and `:60` refuses to ingest tranche 0 as census: *"tranche 0 is the 82-target cohort and is never census"*. Migration `0008_cohort_tranche` backfilled **every** pre-census row to 0 through `db/tranche_backfill.py` (`TRANCHE_ZERO = 0`, `WHERE cohort_tranche IS NULL`). |
| **census** | `cohort_tranche >= 1` | `census_ingest.py:120,262` writes `int(r["tranche"])` from `census_manifest.v7.csv`, whose tranches are **1–5** (measured: 1×1,307 · 2×535 · 3×517 · 4×332 · 5×776 = 3,467). Run-2 enqueues (`task3_run2_folds.py:235`, `task4_slice1–4`) copy the manifest tranche and accept only 1–4. Tiles **inherit the parent's** tranche (`core/hold48.py:594`). |
| **untagged** | `NULL` | `db/models.py:141` — nullable, **no default and no server_default**, because *"a null is a CATEGORY … untagged means unclassified — not a census member and not tranche zero"*. |

**No disagreement between `db/models.py` and the enqueue scripts.** The §3 stop condition does not fire.

⚠ **One consequence, stated because R2 and R3 depend on it:** `NULL` is a **third** population. It is
never folded into either side. R3 groups on `cohort` / `census` / `untagged`, and a NULL-tranche partner
makes a group fail **R2** without making it a same-population duplicate under **R3**. A postgres test pins
exactly that.

**Also from source, and load-bearing for the key:** `scripts/backfill_run_label.py` stamped `run: 1` onto
**every** job then existing, cohort included — which is why one protein folded once per population shows
as two complete `run '1'` rows at one identity.

---

## 2. Step 2 — the instrument, tests first

**`scripts/d167_population_read.py`**, built on `scripts/d167_phase_e_read.py`; tests in
`tests/test_d167_population_read.py`.

### 2.1 RED, then GREEN
- **RED:** 13 failed at the `_module()` assertion, 9 postgres skipped locally
  (`data/control/d167/population_read/t1-tests-red.txt`), commit `cf38d22`.
- **GREEN:** the script, commit `61f7117`; local 27 passed / 15 skipped, full local suite **2,738 passed,
  57 skipped** (`t2-tests-green-local.txt`).

### 2.2 ⚠ The tests caught two defects in Code's own draft
1. **A count taken from a list length.** The first draft wrote R4's expectation as
   `len(R4_ACCESSIONS)` — the session's shared defect class, inside the instrument written to prevent it.
   `test_collect_derives_no_count_from_a_list_length` failed on it. It is now the written constant
   `EXPECTED_R4 = 3`.
2. **⚠⚠ Printed output was not ASCII, and the source-only test could not see it.** CI run
   **35255209176** (postgres job) failed at *"non-ASCII character in the printed output"*
   (`t3-ci-red-printed-ascii.txt`): the shared `core.db_role.format_preamble` header carries a section
   sign. **The fix is in this script, not in `core/db_role.py`** — a shared module is not a read-day edit,
   and the close-out already carries "make printed output ASCII" as its own item. Every printed line now
   goes through `ascii_line` (`backslashreplace`: escaped, never dropped), pinned by two tests.
   ⚠ **A source-only ASCII check is not an output ASCII check.** That is what the printed-output assertion
   in the postgres test bought.

### 2.3 What the tests pin (ORDERS §4)
| # | pinned | how |
|---|---|---|
| 1 | every reading is its own `count(*)` | `collect()` contains no `len(`; `R1_SQL`…`R4_SQL`, `UNTAGGED_SQL`, `R1_SIZES_SQL` each contain `count(*)` and **no `LIMIT`** |
| 2 | a capped list says so | `capped_list` carries the count it was not derived from; `format_capped` prints the count as the count and the length only as *"shown"*; capped whenever `count > rows_shown`, at the cap **or below it** |
| 3 | read-only, role, identity | `SET TRANSACTION READ ONLY` via `read_only_transaction`; `role_preamble` **then** `assert_campaign_target` **then** the first read, asserted by source order and by a statement spy |
| 4 | write-once + sha256 | `write_state`; a second run over an existing output raises |
| 5 | ASCII | source, evidence bytes, **and printed output** |
| 6 | **A-017 — each assertion can fail** | R3 fails on a same-population duplicate; R1 on a moved group count; R2 on an untagged partner (**and R3 stays met**); R4 when an exception loses its census row; **an empty database fails**; a list capped at 1 over 2 groups leaves R1 at 2 and prints `CAPPED` |

### 2.4 CI — green on `612536c`
Run **35255596709**: `test` **pass** (2,727 passed, 62 skipped, 1 xfailed; UI 858 passed) ·
`postgres` **pass** (**55 passed**, 1 skipped, 2,736 deselected) · `deploy` skipped
(`t4-ci-green.txt`). PR **#332**.

---

## 3. ⚠ One key Code had to choose, stated before the read rather than after it

**R4 says "exactly one complete census row". The orders carry it verbatim, and the phrase does not name a
key.** MUC16 (`Q8WXI7`, 14,451 aa), FAT2 (`Q9NYQ8`, 4,030 aa) and IGF2R (`P11717`, 2,264 aa) are all
tranche-5 rental rows in `census_manifest.v7.csv`, so a census **parent** may also own complete **tile**
rows, and the two readings differ.

**Code's choice, and why:** R4 counts at the **whole-protein identity** (`tile_start` and `tile_end`
absent) — the same identity R1–R3 group on, and the one that explains the 72. A parent's tiles are
separate identities, so they are reported as a **diagnostic** (`census_tile_complete`), never inside R4.

⚠ **This is a Code key choice on an ambiguous phrase, not a ruling.** It is recorded in the script's
docstring and in the evidence file's `keys` block. **If the Planner reads R4 the other way, say so before
the tunnel opens** — afterwards it is a re-read, not a reading.

---

## 4. What the read will report

**Expectations (A9.2, verbatim):** R1 **72** · R2 **72 of 72** · R3 **0** · R4 **3 of 3**.
Exit **0** when all four are met, **2** when any is not. ⚠ **A miss is a finding: the work stops, and the
script does not interpret it.**

**Diagnostics, none of which passes or stops anything:** the R1 group list (capped, labelled, with its own
count) with each group's job ids and `cohort_tranche`s · R1 groups by row count · the R3 group list ·
untagged complete run-1 rows · per-accession R4 detail (tranche-0 complete, census whole complete, census
tile complete, untagged complete).

⚠ **This is the reading the Phase E report could not take.** Its §3.4 named what was not established:
*"the un-truncated group list and each row's `cohort_tranche` were not read"*. R1–R4 read both.

---

## 5. Credential scan (A10.3)

Every file committed on this branch: **literal password absent**, **0 credentialed URLs**. Bare words:
two occurrences of `hide_password=False` in the test file (a SQLAlchemy call, listed not stopped).

---

## 6. Owed now

**Owner (the read is owner-gated):** `RUNBOOK-Owner-2026-09-17-R1-R4-read.md` in `Downloads` — window A
opens `fly mpg proxy kyzl60xz9zyrpj9g -p 16391`; window B runs the step-0 probe (must read **`10003`**),
builds `$url` from `.env` with **16391 named explicitly** and a shape check that prints
`placeholder=False` (calibrated both ways on fake input: `True` on a `<placeholder>`), then runs the read.

**Code, after the owner's pastes:** corroborate the proxy remote against `fly mpg status` Direct IP
`fdaa:62:76d9:0:1::9`, confirm exactly one listener, write the tunnel open/close evidence, re-hash
`r1r4_read.json` against the printed sha256, scan every log, commit with **explicit paths**, and report
R1–R4 each against its expectation.

⚠ **Not touched, not read, not ruled on:** the untracked `_tmp_c1_*` / `_tmp_c2_*` helpers and the other
pre-existing untracked files. No broad `git add` was used.

## 7. Still blocked, unchanged

**Phase 1 C1–C5 and `scripts/feature_coverage_report.py`** — `ORDERS-Code-2026-09-16-feature-coverage.md`
is still not on the machine (ORDERS §6). **R1–R4 only** until the original is found or the Planner
re-issues it as a document dated today that says it reconstructs a lost original.
