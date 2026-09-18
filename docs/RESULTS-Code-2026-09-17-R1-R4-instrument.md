# RESULTS — Code → Planner — 2026-09-17 · R1–R4: the instrument is built and green; the four readings are NOT taken

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Session date:** **2026-09-17, America/Los_Angeles (PDT, UTC−7)** — open measured 10:21 PDT / 17:21 UTC
(`Get-Date`). The `09-17` label is the real calendar date.
**Base:** `origin/main` @ **`1e67954`** (the #331 merge). ⚠ **Not `f7d0a9d`** — that is Code's prework's
parent; `main` moved twice after it (`1b69b3d`, then `1e67954`). Local was level with origin at open.
**Branch:** `d167-r1r4-population-read` → PR **#332**, head **`7481a55`**.
**Governs:** `ORDERS-Code-2026-09-17-R1-R4.md`; `RULING-Owner-2026-09-17-population-P1-P4.md`.

> ⚠⚠ **READ THIS FIRST. There are no R1–R4 values in this document.** No database was contacted today.
> What follows is the instrument, its calibration, and three things found while building it. **R1, R2, R3
> and R4 remain unmeasured**, and every expectation below is pre-registered, not observed.

**Reserved integers, unchanged and unspent:** `D-168` · `F-081` · `A-032` (`docs/RESERVED.md`, inline
pointers at line 327). No `### D-168`, `### F-081` or `### A-032` exists in any of the three logs.

---

## 1. What was produced

| # | commit | what |
|---|---|---|
| 1 | `cf38d22` | `tests/test_d167_population_read.py` — **RED**, 13 failed at the `_module()` assertion |
| 2 | `61f7117` | `scripts/d167_population_read.py` — **GREEN** |
| 3 | `612536c` | printed output escaped to ASCII, after **CI RED at the assertion** |
| 4 | `7c5a71b` | the readiness report (A4.8) + CI-green evidence |
| 5 | `88d8fde` | the **run-label predicate** stated, and what falls outside it measured |
| 6 | `7481a55` | report updated: §2.5, the R4 key ruled, §6a |

**974 insertions, 8 files, no deletions.** Evidence under `data/control/d167/population_read/`:
`t1-tests-red.txt` · `t2-tests-green-local.txt` · `t3-ci-red-printed-ascii.txt` · `t4-ci-green.txt` ·
`t5-ci-green-run-label.txt`.

**CI, PR #332:**

| run | commit | `test` | `postgres` |
|---|---|---|---|
| 35255209176 | `61f7117` | pass | ⚠ **FAIL** — non-ASCII in printed output (1 failed, 54 passed) |
| 35255596709 | `612536c` | pass | pass — 55 passed, 1 skipped |
| **35267676543** | **`88d8fde`** | **pass** | **pass — 57 passed, 1 skipped** |

Full local suite on the branch: **2,738 passed, 57 skipped, 0 failed.**

---

## 2. Step 1 — the tranche convention, from source only (ORDERS §3)

| population | value | established by |
|---|---|---|
| **cohort** (the 82) | `cohort_tranche = 0` | `scripts/census_ingest.py:52` `COHORT_TRANCHE = 0`, and `:60` refuses tranche 0 as census; migration `0008_cohort_tranche` backfilled every pre-census row to 0 through `db/tranche_backfill.py` |
| **census** | `>= 1` | `census_ingest.py:120,262` writes the manifest tranche; `census_manifest.v7.csv` measured **1×1,307 · 2×535 · 3×517 · 4×332 · 5×776 = 3,467**; Run-2 enqueues copy it, restricted to 1–4; tiles inherit the parent's (`core/hold48.py:594`) |
| **untagged** | `NULL` | `db/models.py:141` — nullable, no default, no server_default: *"a null is a CATEGORY … not a census member and not tranche zero"* |

**`db/models.py` and the enqueue scripts do not disagree.** §3's stop condition does not fire.

⚠ **Consequence R2 and R3 depend on:** `NULL` is a **third** population, never folded into either side. A
NULL partner makes a group fail **R2** without being a same-population duplicate under **R3** — pinned by
a postgres test.

---

## 3. What the instrument will report, and what it refuses to do

**Pre-registered (A9.2 verbatim):** R1 **72** · R2 **72 of 72** · R3 **0** · R4 **3 of 3**.
Exit **0** when all four are met, **2** when any is not. ⚠ **A miss is a finding: the work stops and the
script does not interpret it.**

**Keys, written into the evidence file's `keys` block so no reading is ambiguous:**
- *complete run '1' row* = `jobs.status = 'complete' AND inference_settings->>'run' = '1'`, joined to its
  `protein_analyses` row.
- *identity* = `(accession, tile_start, tile_end)`.
- *population* = `0 → cohort` · `>= 1 → census` · `NULL → untagged`.
- *R4's census row* = `cohort_tranche >= 1` at the **whole-protein** identity.

**Diagnostics — none passes or stops anything:** the R1 group list (capped, labelled, carrying its own
`count(*)`, with each group's job ids and tranches) · R1 groups by row count · the R3 group list ·
untagged complete run-1 rows · per-accession R4 detail · **complete rows by run label and complete
tranche-0 rows by run label, both naming `(absent)`** (§5).

---

## 4. ⚠ Two defects the tests caught in Code's own draft

1. **A count taken from a list length.** The first draft wrote R4's expectation as `len(R4_ACCESSIONS)` —
   the session's **shared defect class**, inside the instrument written to prevent it.
   `test_collect_derives_no_count_from_a_list_length` failed on it; it is now the written constant
   `EXPECTED_R4 = 3`.
2. **⚠⚠ Printed output was not ASCII, and the source-only test could not see it.** CI run **35255209176**
   failed at *"non-ASCII character in the printed output"*: the shared `core.db_role.format_preamble`
   header carries a section sign. **Fixed in the script, not in `core/db_role.py`** — a shared module is
   not a read-day edit, and the close-out already carries "make printed output ASCII" as its own item.
   ⚠ **The method note: a source-only ASCII check is not an output ASCII check.** Only the assertion on
   the *printed* bytes caught it, and only in CI.

**What the A-017 fixtures prove (in the 57):** R3 fails on a same-population duplicate · R1 on a moved
group count · R2 on an untagged partner **while R3 stays met** · R4 when an exception loses its census
row · **an empty database fails** · a list capped at 1 over 2 groups leaves R1 reading 2 and prints
`CAPPED`.

---

## 5. ⚠⚠ The one substantive finding of the day — the run-label predicate

Owed by `RULING-Owner-2026-09-17` §5, and it did not come back empty.

**Stated:** every reading, R4 included, counts only `->>'run' = '1'`. The label is a **JSON integer**
(`backfill_run_label.py` `RUN_1 = 1`; `census_ingest.py:279` `"run": 1`; `task3_run2_folds.py`
`RUN_LABEL = 2`), read as text through `->>`, which is why `'1'` matches. An **absent** label is **not**
Run 1 — `census_ingest.py:270–275` says so outright (*"Run 1 must be POSITIVELY DECLARED rather than
inferred from a key's absence"*, `F-018`).

⚠⚠ **`core/hold48.py`'s `emit_tile_jobs` (`:601–617`) writes no `run` key at all.** A tile emitted
**after** the backfill is therefore outside the run-1 key entirely — invisible to every R-reading **and to
`app.reads.keep_run_1`**, which is what the census surfaces select by. The tiles the earlier phases counted
(3693/3695/3696) were stamped only because they pre-dated `backfill_run_label.py`.

**Measured, not assumed:** two diagnostics count complete rows by run label with `(absent)` named, all
tranches and tranche 0 alone, each its own `count(*)`, neither applying the key it reports the outside of.
A postgres test seeds an unlabelled tile and proves it moves **no** R-reading and appears only under
`(absent)`.

⚠ **Whether such a row exists in production is a reading, not a claim.** Code asserts nothing about it.
**If `(absent)` is non-zero, that is a finding for the Planner — rows the census surfaces cannot see — and
it belongs to `F-081`'s question, not to R1–R4's four expectations.**

---

## 6. Rulings consumed, and one that changed nothing

| item | ruling | effect on the instrument |
|---|---|---|
| **R4's key** (whole-protein identity, tiles as a diagnostic) | ⚠ Code raised it **before** the tunnel as an ambiguity in a verbatim phrase; **RULED correct** (`RULING-Owner-2026-09-17` §6): *"the only key under which 3 of 3 is satisfiable"* | none — the choice was already implemented and documented |
| **P1–P4 population** | P1 in unscoped · P2 only if `C3` > 0 · P3 ≤100 stratified instrument sample, tagged, never pooled · P4 out | **none today.** It gates Phase 2; Code took no step on it |
| Credential rotation | **deferred deliberately**, recorded as a choice | the literal-secret scan is the only guard and it ran on every commit (§8) |

---

## 7. ⚠⚠ Still blocked — and the block now covers TWO missing documents

- `ORDERS-Code-2026-09-16-feature-coverage.md` — cited by the 09-16 ruling, both preworks and the
  close-out. **Never committed to `docs/`** (the ruling's §6 item 4 records this as owed under `F-081`).
- `ORDERS-RECONSTRUCTION-2026-09-17-feature-coverage.md` — the document
  `RULING-Owner-2026-09-17-population-P1-P4.md` answers in its header and §2.1. **Also absent** from the
  repo, `Downloads` and `Documents`.
- `feature_coverage_census_v7_file_based.csv` (sha256 `f9104d4e…d50c4`) — absent, so Code's prework §3.1
  re-derivation cannot be re-checked this session.

⚠ **R1–R4 are fully specified and are NOT blocked.** **C2, C3, C5 and the P1–P4 operational definitions
are.** ⚠ `C3` in particular gates P2 and is measured in the same tunnel — so **P2 is not decidable until
Phase 1 opens**, which needs one of these documents on the machine.

---

## 8. Hygiene

- **Credential scan before every commit:** literal password **absent**, **0** credentialed URLs in all
  eight files. Bare words: two `hide_password=False` (a SQLAlchemy call) — listed, not stopped.
- **Explicit paths on every `git add`.** ⚠ The untracked `_tmp_c1_*` / `_tmp_c2_*` helpers and the other
  pre-existing untracked files were **not read, not touched, not ruled on**, and none of them landed.
- `.env` still holds a credential for `pharmfoldmdk-app` on the **dead port 16380** — consistent with
  rotation being deferred.
- Evidence written LF and ASCII; `data/control/d167/**` is already `-text` protected in `.gitattributes`.
  ⚠ **`r1r4_read.json` must be added to `.gitattributes` BY NAME once it exists**, as the three `D-167`
  hash-pinned files are — the glob is not enough for the byte-for-byte guard.

---

## 8a. ADDENDUM, after `ORDERS-Code-2026-09-17-AMENDMENT-1-identity-split.md`

**Executed:** the identity split (AMENDMENT 1 §3), commit **`e4a300b`**. `IDENTITY_BRANCH_SQL` is the
readings' own definition — whole-protein = both tile keys absent, tile = both present — and
⚠ **one key present with the other absent is named `partial_tile_keys`**, not folded into either. Both
by-run-label diagnostics now `GROUP BY label, branch`, **every cell its own `count(*)`**; a test fails on
any `-` in `collect()`, so no branch can be a subtraction from a total. The printed output names the
`whole_protein` count as the **STOP** branch and the `tile` count as a **carry**.
A postgres fixture seeds an unlabelled **whole-protein** row **and** an unlabelled tile, and proves
neither moves any of the four readings while `(absent)` reads `{whole_protein: 1, tile: 1}` — the two
branches told apart, which §3 condition 5 requires.
Local: 18 passed, 12 skipped; full suite **2,743 passed, 60 skipped**.

### ⚠ One correction to AMENDMENT 1 §6 — a delivery claim that overstates the loss

§6 states that **both** `ORDERS-RECONSTRUCTION-2026-09-17-feature-coverage.md` and
`RULING-Owner-2026-09-17-population-P1-P4.md` are absent, and attributes that report to `RESULTS` §7.

**Measured just now** (`Get-ChildItem` over `Downloads`, `Documents` and the repo):

| document | actually |
|---|---|
| `RULING-Owner-2026-09-17-population-P1-P4.md` | ⚠ **PRESENT** — `C:\Users\mdk32\Downloads\`, 2026-09-17 12:52 PDT. Code read it and acted on it; `RESULTS` §6 records its rulings and §6a names it. **`RESULTS` never reported it missing.** |
| `ORDERS-RECONSTRUCTION-2026-09-17-feature-coverage.md` | **absent**, as reported |
| `ORDERS-Code-2026-09-16-feature-coverage.md` | **absent**, as reported |

**So `F-081`'s question has two undelivered instances, not three**, and the ruling that closed P1–P4 is
not one of them. ⚠ **Code does not adjust the Planner's error count** — that is the Planner's to keep.
The record is corrected here because a close-out entry built on §6 as written would claim a loss that the
filesystem contradicts, and *"a written record does not make a claim true"* (`D-016`).

**Unchanged by this correction:** Phase 1 stays blocked on the **one** missing reconstruction, and the
refusal to build from a paraphrase stands.

## 9. What Code asks the Planner for

1. ✅ **RULED** (AMENDMENT 1 §2): `(absent)` is a **carry** at tile identities and a **STOP** at
   whole-protein ones. Code's (a) adopted, with the discriminator. Implemented at `e4a300b`; the runbook
   now carries the stop at the keyboard, because **exit 0 alone no longer means a clean day.**
2. ✅ **RULED** (AMENDMENT 1 §4): nothing else was owed but §3's split, which is now done.
3. ✅ **RULED** (AMENDMENT 1 §7): the day ends at R1–R4 unless the missing reconstruction lands before the
   tunnel closes, in which case Phase 1 may open **in the same tunnel**. ⚠ See §8a's correction: **one**
   document is missing, not two.

**The read itself is owner-gated:** `RUNBOOK-Owner-2026-09-17-R1-R4-read.md`, two windows, step-0 probe
reading `10003`, `$url` with **16391 named explicitly** and a shape check calibrated both ways
(`placeholder=False` on a real URL, `True` on a `<placeholder>` — the remedy for Code error 1 of the last
session).
