# REPORT — Code → Planner — 2026-09-17 · TASK D delivered, the `F-081` verification answered, and the session's state

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Written:** 2026-09-17, **15:13 PDT** (`Get-Date`). The `09-17` label is the real calendar date.
**Governs:** `ORDERS-Code-2026-09-17-TASK-D-coverage-report.md`.
**Branch:** `d167-r1r4-population-read`, PR **#332**, head **`2cd1c16`**.
**CI:** run **35280187184** — `test` **pass** (2,745 passed, 76 skipped, 1 xfailed) ·
`postgres` **pass** (**69 passed**, 1 skipped) · `deploy` skipped.

> ⚠ **No database contact since the one read.** The tunnel account is unchanged: **one tunnel, one
> read**, closed at 20:52:45Z and re-verified closed at 21:23:51Z.

---

## 1. §3.3's verification — answered: **already there, nothing to do**

The orders asked Code to confirm that `F-081` states that **`app.reads.keep_run_1` shares the blind
spot**. ⚠ **It does, in four places**, and it was written that way before the verification was asked
for:

| where | text |
|---|---|
| the heading | *"…invisible to **`keep_run_1`** and to every reading that selects Run 1…"* |
| *How known* | source read of *"`app/reads.py`'s `keep_run_1`"* |
| THE FINDING | *"…including **`app.reads.keep_run_1`**, which is what the census surfaces select by"* |
| §3 item 2 | *"⚠ **`app.reads.keep_run_1` shares the blind spot** and is the reason this is a surface defect and not only a bookkeeping one"* |

**No edit made.** ⚠ A one-sentence addition would have duplicated a claim already stated, and a second
copy of a claim is the drift this project keeps finding.

---

## 2. TASK D — `scripts/feature_coverage_report.py`, delivered

**Commits `522cebe`** (tests RED at the assertion, then the script) and **`2cd1c16`** (the CI-caught
defect, §4). Built from **`docs/ORDERS-RECONSTRUCTION-2026-09-17-feature-coverage.md` as committed** —
never from a chat restatement.

### 2.1 What it measures, and the question it asks

⚠⚠ **It never asks "does a feature row exist?" alone. It asks the page's question.**

| reading | what it counts |
|---|---|
| **C5** — *reported first* | v1 artifact `analysis_id`s present in the `protein_features` **table**, plus a capped equality sample. The panel reads the table and v1's manifest records `wrote_database_rows: false`, so this decides whether v1 ever arrived |
| **C1a** | census representatives with **no** `protein_features` row |
| **C1b** | of those, how many `_incommensurable_assembly` already refuses — **extraction changes nothing visible for them** |
| **C1c** | `C1a − C1b`, labelled **the only true coverage gap** |
| **C2** | representatives whose accession's feature row hangs off a **different** `analysis_id` — count **and** ids, **no pre-set expectation** |
| **C3** | cohort tranche-0 rows with no feature row — ⚠ **this decides `P2`** |
| **C4** | `C1a` by `structure_kind`, each branch its **own** count |

**Every reading carries its key** in a `KEYS` block that ships in the output — a bare number is not a
C-reading, and a test fails if a key is missing or trivial.

### 2.2 One home, asserted by identity

`choose_census_representative` is imported from `app.reads` and `_incommensurable_assembly` from
`app.census_profile_read`. ⚠ The tests assert **`r.fn is app_fn`** and that the script defines neither.
A copy of either would describe a site that does not exist.

### 2.3 The discriminating test — the CSV error, refused

⚠⚠ **An assembled parent *with* a feature row is still not a coverage gap.** A report that counted
feature rows would move that row out of `C1b`; the page never consults it. That fixture is pinned, and
so is its converse (a single-pass row with no feature row → `C1c`).

### 2.4 No table to reproduce, and the floor that survives

⚠ Per `RECONSTRUCTION` §1 the source CSV is gone, so **the output is the measurement**. The old gap
figure appears **nowhere in the script**, and **a test fails if it ever does** — it is a historical
quotation, not a live number, and nothing reconciles against it. The one surviving expectation is
**`C1a ≥ 773`**; a **smaller** reading is a **finding** and exits 2. ⚠ **A-017:** the floor is shown
firing in **both** directions, on fixtures built to make it fire.

### 2.5 The rest of §4.2, pinned

No count from a list length (a test fails on `len(` inside the reading functions) · no `C4` branch by
subtraction (a test fails on `-` there) · capped lists labelled capped **at the cap or below it** ·
**printed output asserted ASCII on the PRINTED BYTES** · `SET TRANSACTION READ ONLY` proven by a
statement spy over every statement the engine issues · role preamble before `D-159` · write-once output
with its sha256.

⚠ **The script was NOT run against the database.** Its first execution belongs to Phase 1's tunnel,
under AMENDMENT 2, once that document is delivered.

---

## 3. ⚠⚠ §4.1's report — the reconstruction is incomplete on `C4`'s vocabulary

**The orders name three branches. `choose_census_representative` returns FOUR.**

`app/reads.py:980–997` returns `assembled` · `tiles_only` · `single-pass` · **`mucin`**.

- **`mucin` is kept as its own branch and is never folded into `single-pass`.** Folding it would be
  precisely the defect `D-168` §3 names and `2.4.3` forbids.
- ⚠ **It is not academic: `mucin` is exactly MUC16's case** — the accession behind `F-082`, whose
  never-folded state `F-082` §5(b) leaves open as a possible **class property of mucins**. A C4 that
  had no `mucin` branch would have made that question invisible in the very report meant to size it.

**Reported, not assumed dropped**, as §4.1 requires. ⚠ §2.4.2 and §2.4.5 remain unrecovered; nothing in
today's source reading bore on them.

---

## 4. ⚠ The defect CI caught, which was in the script and not the tests

CI run **35279811497** (postgres) failed two of the new tests: `KeyError: 'assembled'` and the `mucin`
assertion. **One cause, in the script:** `by_kind` was built only from the kinds that happened to
appear, so **a branch with no rows vanished from `C4` instead of reading `0`.**

⚠⚠ **That is `D-027` at the reporting surface.** A key that disappears when its count is zero reads as
*"not measured"* rather than *"measured none"* — and `decisions.md:2860` records that exact reasoning
for the census partition: *"a four-way breakdown that does not reconcile with the population is how a
fifth silent category hides."*

**Fixed:** `STRUCTURE_KINDS` names all four, every branch initialises to `0`, and a kind the picker
returns that is not listed is **added, never folded into another**. A new test pins the
zero-rather-than-absent rule on a fixture where the assembled branch is empty.

⚠ **Found by the postgres fixtures, not by reading.** The local half is green on a machine with no
database; this is the third time today CI has been the instrument that caught something — the first
two being the printed-ASCII assertion and this.

---

## 5. Session state at this report

| item | state |
|---|---|
| **R1 · R2 · R3** | **MET** — 72 · 72 of 72 · 0 |
| **R4** | ⚠ **NOT MET at 2 of 3** — ruled a mis-specified expectation, recorded as **`F-082`** |
| `D-168` | **WRITTEN** (`8005f27`). Extraction unblocked next sitting; **ingest still barred** |
| `F-081`, `F-082` | **WRITTEN** (`222bcdb`). `F-` pointer **081 → 083**, `D-` pointer **168 → 169**, both moved in the commits that spent them |
| TASK A | the tunnel account is **whole**: one tunnel, one read, both pastes |
| **TASK D** | **delivered, CI green** |
| TASK E | **deferred** by the orders |
| **E1–E3, Phase 1 C1–C5** | ⚠ **authorised by the Planner, NOT YET DELIVERED to the Builder** — AMENDMENT 2 is still absent from `Downloads`, `Documents` and the repo |
| `P2` | ⚠ **undecidable until `C3` is read** |

**The branch:** 41 files, +5,005 / −58, across 12 commits from `1e67954`.
**Hygiene:** explicit paths on every `git add` · credential scan clean on every commit · the untracked
`_tmp_c1_*` / `_tmp_c2_*` helpers **not read, not touched, not ruled on**, and none has landed ·
`r1r4_read.json` never deleted or rewritten, EOL-protected by name.

---

## 6. What Code asks the Planner for

1. **Accept or correct §3** — `C4` carrying a fourth branch, `mucin`, against the orders' three. Code
   implemented the four-branch form because folding is forbidden; **if the Planner wants `mucin`
   reported differently, it is one constant and one test.**
2. **Deliver AMENDMENT 2** if E1–E3 and Phase 1 are to run next sitting. Until it is on the machine
   Code builds no part of them.
3. **Say where PR #332 should land** — it now carries R1–R4, the read and its evidence, `D-168`,
   `F-081`, `F-082`, TASK D, and the session's documents. ⚠ **Nothing in it deploys**, and it has not
   been merged.
