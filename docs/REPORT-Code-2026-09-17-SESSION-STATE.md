# REPORT — Code → Planner — 2026-09-17 · Consolidated session state, for the close-out that is still deferred

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Session:** **2026-09-17, America/Los_Angeles (PDT, UTC−7)** — opened **10:21 PDT / 17:21 UTC**,
measured (`Get-Date`). ⚠ **The `09-17` label is the real calendar date**, unlike 09-15/09-16.
**Base:** `origin/main` @ **`1e67954`** (the #331 merge). ⚠ **Not `f7d0a9d`** — that is Code's
prework's parent, and `main` moved twice after it.
**Branch:** `d167-r1r4-population-read` → PR **#332**, head **`9df612d`** — **26 commits, 65 files,
+8,901 / −58.**
**CI:** run **35287019818** — `test` **pass** · `postgres` **pass** · `deploy` skipped.
**Pointers now:** `D-169` · `F-083` · `A-032`. ⚠ Every spend moved its pointer **in the same commit**.

> ⚠ **This is a state report, not the close-out.** The orders defer the close-out until the owner
> calls the day. It is written so the close-out can be assembled from measurements rather than from
> recollection.

---

## 1. The day's result in one table

| # | what | outcome |
|---|---|---|
| 1 | **R1 · R2 · R3** | **MET** — 72 · 72 of 72 · 0 |
| 2 | **R4** | ⚠ **NOT MET at 2 of 3** → ruled a **mis-specified expectation**, recorded as **`F-082`** |
| 3 | **E1 · E2 · E3** | reported; **E3's stop did not fire** — the cohort account is now **proven** |
| 4 | **`C5`** | **all 2,690 v1 rows reached `protein_features`**, 50/50 sample equal |
| 5 | **`C1a`/`C1b`/`C1c`** | **776 / 45 / 731** — ⚠ **731 is the only true coverage gap** |
| 6 | **`C2` · `C3` · `C4`** | 0 · **0** · assembled 45 · mucin 3 · single-pass 728 · tiles_only 0 |
| 7 | **`P2`** | ⚠⚠ **CLOSED — OUT**, on `C3 = 0`. A measurement, not a judgement |
| 8 | **`D-168`** | **WRITTEN** — extraction unblocked next sitting; **ingest still barred** |
| 9 | **`F-081` · `F-082`** | **WRITTEN**; `F-` pointer 081 → 083, `D-` pointer 168 → 169 |
| 10 | **TASK D · T0** | both **delivered, CI green**, neither run against anything live |

---

## 2. Entries written (the log leads the code)

| entry | subject | where |
|---|---|---|
| **`D-168`** | assembled features are **stored tagged, never pooled**; extracting them **changes nothing any page displays**; commensurability is a property of **instrument and object together** | `docs/decisions.md:19` |
| **`F-081`** | tiles are enqueued with **no `run` key**, so a post-backfill tile is invisible to `keep_run_1` and to every R-reading. ⚠ **Real in source, ZERO instances in the database today, latent for the next tile emission** | `docs/findings.md:19` |
| **`F-082`** | **R4's expectation was mis-specified for MUC16** — a planned tiled rental span conflated with a protein actually folded as tiles | `docs/findings.md:82` |

⚠ **`F-081` was written because the orders moved the pointer past it.** A pointer moved over an
unwritten integer is the `D-062` shape; the Planner ruled the decision correct.

---

## 3. What was measured, and where the evidence is

**Two tunnels, both fully evidenced, each with its own open/close pastes, Direct-IP corroboration and
single-listener count. A third was not authorised and none exists.**

| artifact | sha256 (head) | what |
|---|---|---|
| `r1r4_read.json` | `aff81593…` | R1–R4, tunnel 1 |
| `e1_e3_read.json` | `6c1c634e…` | E1/E2/E3, tunnel 2 |
| `c5_read.json` | `0ff35dbd…` | C5 **alone**, before C1 was computed |
| `c1_read.json` | `2afed323…` | C1a/C1b/C1c |
| `c2_c3_c4_read.json` | `f10883cd…` | C2/C3/C4 |

**Each re-hashes on disk after its tunnel closed, and each is EOL-protected BY NAME** in
`.gitattributes` — the glob is not enough for a byte-for-byte guard. **Credential scan clean on every
commit.** ⚠ **No artifact was ever deleted or rewritten**, and no reading was re-run to improve a
number.

### 3.1 The coherence check (TASK K), from the artifacts

**3,466 − 776 = 2,690 = v1 ids = rows in the table, with `C2 = 0`.** The covered set **is** v1's set;
there is no unaccounted source. ⚠ **Corroboration across three independent readings — not a finding,
not an integer.** Bounded in §1.1 of the K/L/M report: it is about **census representatives**, not
the whole table, because `C3 = 0` proves cohort rows carry features too.

---

## 4. Instruments built today — four, all tests-first

| script | purpose | proven by |
|---|---|---|
| `d167_population_read.py` | R1–R4, population-aware | 9 postgres fixtures, each reading shown capable of failing |
| `feature_coverage_report.py` | C1–C5, modelling the profile short-circuit | the discriminating fixture: an assembled parent **with** features is still not a gap |
| `d167_enumerations.py` | E1/E2/E3 | E3's stop shown firing on a fourth missing accession |
| `pdb_coverage_census.py` | PDB coverage T0, **offline** | 39 tests; no live client can exist |

⚠ **Every one of them was CI-green before it read anything live**, and `feature_coverage_report.py`
and `pdb_coverage_census.py` **have never been run against live data at all.**

---

## 5. ⚠⚠ What the instruments caught in Code's own work — four times, and CI caught three

1. **A count taken from a list length** (`len(R4_ACCESSIONS)`) — the session's shared defect class,
   inside the instrument written to prevent it. Caught by Code's own test.
2. **Printed output was not ASCII** — `core.db_role.format_preamble`'s section sign. ⚠ **Caught only
   in CI**, by the assertion on the **printed bytes**.
3. **A `C4` branch vanished at zero** instead of reading `0` — `D-027` at the reporting surface.
   ⚠ Caught in CI.
4. **Rows and accessions conflated** in E2 — a test asserted a row count equalled the length of a
   list of names. ⚠ Caught in CI.
   ⚠⚠ **CORRECTED 2026-09-17 (TASK N), in place and openly.** This item originally read *"5
   non-complete rows resolve to 4 distinct accessions, because MUC16 holds one on each side."*
   **That described the postgres TEST FIXTURE, not production**, and stating it here presented a
   fixture's shape as a measurement. **In production `e1_e3_read.json` reads 5 rows → 5 DISTINCT
   accessions** (`failed` `P11717`, `P55073`; `pending` `Q685J3`, `Q8WXI7`, `Q9UKN1`), and **MUC16
   holds exactly ONE row in the whole database** (job 3073, tranche 5). **E1 was right.** See
   `REPORT-Code-2026-09-17-TASK-N-MUC16-reconciliation.md`.

⚠ **The reusable method note: *a source-only ASCII check is not an output ASCII check.*** It belongs
in the close-out as a **lesson**, not as a changelog line.

---

## 6. Open, carried, and owed

### 6.1 Open questions with an owner
| item | state |
|---|---|
| **`F-082` (b)** — is the never-folded state a **class property of mucins**? | ⚠ **OPEN.** E2's three pending accessions being exactly the three mucins is **evidence, not an answer** |
| **The mucin copy's queue claim** | ⚠ *"Rental is closed (pod Terminated)"* vs three enqueued `pending` rows. ⚠ **The tension is in the sentence, not the flag** — and retiring the rows would change **no** surface |
| The paper's **§4.3 loss statement** | owner's wording; now zero rows |
| **v2 timeline class dates** | owner supplies; the PDF is rebuilt around them |
| **Credential rotation** | ⚠ **deferred deliberately** — the literal-secret scan is the only guard and the repo is public |
| **`D-169` / `D-170`** | owed to `SPEC-A-032` §2.6 / §3.7, after `D-168` |

### 6.2 Ordered for the next tunnel
- **The cohort-account query** — what the three missing accessions hold **instead** (FAT2 has no
  complete cohort row **and** no non-complete run-1 row).
- ⚠ **`A-032` step 1**, whose pass criterion is pre-registered **before** the pull.
- **T1 / T2 / T3** of the PDB census. ⚠ **T1's stop condition needs a fresh head.**

### 6.3 Standing, recorded, not repaired
`F-079`'s three open exceptions · the citation-invariant residual · the **four stale `RESERVED.md`
rows** (`F-073`, `A-031`, `D-158`, `D-156`) — ⚠ **not struck** without checking the `re.search` pins ·
`core/db_role.py`'s section sign, on the existing "make printed output ASCII" item ⚠ **a shared
module is not a read-day edit** · the untracked `_tmp_c1_*` / `_tmp_c2_*` helpers, **not read, not
touched, not ruled on**, none landed.

---

## 7. The error ledger, as Code understands it

| party | count | today's additions |
|---|---|---|
| **Planner** | **15** | 9 (a second name for one refusal) · 11 (documents cited but undelivered) · 12 (R4's set built without checking fold state) · 13 (a Builder state asserted without verification) · 14 (`C4`'s three-branch vocabulary) · 15 (the `3,385` subtraction) |
| **Code** | ⚠ **8** | §5's four defects were caught **before** they reached a reading — that is the system working. ⚠⚠ **But a fifth was NOT: §5 item 4's original wording carried a test fixture's shape into a report as though it were a production measurement.** It reached two documents and would have reached the close-out. **Code's count is 8, not 7** |

⚠ **Code does not adjust the Planner's count**; it is recorded here as read from the orders so the
close-out can reconcile it in one place.

---

## 8. ⚠ Two things the Planner should decide before the next sitting

1. **Where PR #332 lands.** It carries the entire day — R1–R4 and its read, `D-168`, `F-081`,
   `F-082`, the coverage report, tunnel 2's four readings, T0, and every governing document. ⚠ **26
   commits, CI green, nothing deployable.** It has not been merged.
2. **Whether the close-out is written next**, and by whom. ⚠ Everything it needs is measured and
   committed; §§1–7 above are its raw material. **The orders defer it until the owner calls the day,
   and Code has not pre-empted that.**
