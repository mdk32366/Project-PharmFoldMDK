# ORDERS — Code — 2026-09-17 · Tunnel 2 AUTHORISED · E1–E3 · Phase 1 with mandatory pauses · then T0

> ⚠⚠ **Where this file and the log differ, THE LOG GOVERNS.**
> ⚠ Landing header added by Code at landing, 2026-09-17. **The body below is the document as
> delivered, byte-for-byte**; no AUTHORED-SHA256 range is declared over it.

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Issued:** 2026-09-17, America/Los_Angeles, afternoon. The `09-17` label is the real calendar date.
**Grounded on:** branch `d167-r1r4-population-read`, PR **#332**, head **`a9e8f50`**, CI green.
**Owner instruction:** *"Fresh tunnel, then the T0 work."*

---

## 1. ⚠⚠ REVOKED — the Planner's own no-further-tunnel ruling

`ORDERS-Code-2026-09-17-TASK-D-coverage-report.md` said *"No further tunnel is authorised today."*
**That was the Planner's ruling, not a standing condition of the project, and the Planner REVOKES it
here.**

⚠ **Revoking it explicitly matters.** The alternative — proceeding as though the constraint had come
from somewhere else — would be the Planner editing its own record by implication. **It came from the
Planner and it is withdrawn by the Planner, on the record.**

⚠ **Planner note, recorded:** the close-out was proposed because the Planner deferred to the Builder's
read of the day's state instead of checking it against what was available. **That is the same habit
behind Planner errors 13 and 15** — reasoning from the record rather than from the state. It is named
here so the close-out carries it.

**AUTHORISED: tunnel 2 of 2026-09-17. A third is NOT authorised.**

---

## 2. TASK H — deliver and commit AMENDMENT 2. First, before the tunnel.

`ORDERS-Code-2026-09-17-AMENDMENT-2-phase1-and-enumerations.md` is being delivered to `Downloads` with
this document. **Commit it to `docs/` with explicit paths.**

⚠ **It stands exactly as written and nothing in it is reconstructed.** It remains the governing document
for **E1–E3 and Phase 1 C1–C5**, with two corrections from later rulings, which Code applies:

| corrected | ruling |
|---|---|
| its §4's *"tunnel 2 declared"* | ⚠ **VOID for the morning** — no tunnel 2 existed then (case (i), established from process evidence). **This afternoon's tunnel is the real tunnel 2.** |
| its §3 `C4` three-branch vocabulary | ⚠ **SUPERSEDED — `C4` has FOUR branches**, `mucin` included (Planner error 14), with **`C4` mucin = 3** pre-registered **as a weak expectation**. |

---

## 3. TASK I — tunnel 2. Its own evidence, not the morning's.

- **Own open paste** · **own Direct-IP corroboration** against `fly mpg status`
  (`fdaa:62:76d9:0:1::9`) · **own single-listener confirmation** · **own close paste.**
- ⚠ **Recorded as tunnel 2 of 2**, never merged into tunnel 1's account. The morning's account stays
  **one tunnel, one read**, and this one is additive.
- ⚠ **Step 0 first:** both encoding lines, probe reads **`10003`**, exit 0. The half-fix prints `244`.
- ⚠ **Check `.env` before building `$url`** — it still carries a credential on the dead **16380**; **the
  live port is named explicitly in the runbook, never trusted from the file.** Rotation remains
  **deferred deliberately**, so the literal-secret scan is the only guard and the repo is public.
- `SET TRANSACTION READ ONLY` · role preamble · `D-159` · `.\.venv\Scripts\python.exe` everywhere.
- ⚠ **Owner at the keyboard.** If the owner directs Code to run it instead, **that is recorded as a
  departure in the tunnel-open evidence, not smoothed** — as it was this morning.

---

## 4. ⚠⚠ THE ORDER OF READS, AND THE PAUSES ARE MANDATORY

**Read in this order. Stop and report at each ⏸. Do not push through to the end.**

1. **E1 · E2 · E3** → **⏸ REPORT.** ⚠ **E3's stop condition is intact:** if the three cohort accessions
   lacking a complete tranche-0 row are **not** `P11717`, `Q8WXI7`, `Q9NYQ8`, **that is a finding and
   Phase 1 does not start in this tunnel.**
2. **`C5`** → **⚠⚠ ⏸ REPORT BEFORE `C1` RUNS.** Not negotiable. **`C5` can invalidate `C1`'s
   expectation**: if v1's **2,690** rows never reached `protein_features`, then `C1a ≥ 773` no longer
   means what it was registered to mean, and the Planner re-registers it **before** `C1` is read rather
   than reinterpreting it after.
3. **`C1a` · `C1b` · `C1c`** → **⏸ REPORT.** ⚠ Three keyed readings, never one number. **`C1c` is the
   only true coverage gap.** ⚠ **A SMALLER `C1a` than 773 is a finding** — features from an unaccounted
   source.
4. **`C2` · `C3` · `C4`** → **⏸ REPORT.** **`C3` resolves `P2`.** **`C4` has four branches**; its
   `mucin` branch is **evidence toward `F-082` (b)**, never an answer to it.
5. **Close tunnel 2**, both pastes.

⚠ **Why the pauses:** this is a sequence where an early reading can change what a later one means, and
**the day has already produced four Planner errors** — two of them population arithmetic. ⚠ **Fatigue is
where that arithmetic goes wrong.** The pauses exist so a bad expectation is caught before it is
measured against, not after.

⚠ **Every count its own `count(*)`. Every capped list labelled capped. Every reading states its key — a
bare number is not a C-reading.** Write-once output with its own sha256; **ASCII on the printed bytes.**

⚠ **`scripts/feature_coverage_report.py` (`2cd1c16`) gets its FIRST real execution here.** It was built
and proven by tests only. ⚠ **If its output and a direct read disagree on any C-reading, that is two
paths to one quantity — stop and report. Do not pick one.**

---

## 5. TASK J — T0 of the PDB coverage census, AFTER the tunnel closes

**Build from `SPEC-PDB-coverage-census-step1-tranches-v2.md`**, delivered with this document and
**committed before T0 starts.** ⚠ **v2 supersedes v1 in full** — v1 carried **Planner error 15**, the
`3,385` subtraction that treated the cohort as a subset of the census when only **75 of 82** are census
members.

⚠⚠ **T0 is OFFLINE. No SIFTS read, no PDBe read, no network in any test.** Tests first, RED at the
assertion. Its instrument rules are the ones today's two instruments already carry, including the one the
coverage report **failed CI on**: ⚠ **every category present at zero, never vanishing** (`D-027` at the
reporting surface).

⚠ **Two sum checks, not one** — the seven outcomes sum to **82** for the cohort pass and to **3,467** for
the census pass. **Never to 3,474**, which double-counts the 75.

**T1 is NOT authorised today.** T0 ends at CI green.

---

## 6. Not authorised

| not authorised | why |
|---|---|
| **A third tunnel** | Two are authorised (§1). |
| **T1 / T2 / T3** of the PDB spec | T0 only. T1's stop condition needs a fresh head. |
| **`A-032` step 1** | ⚠ Still deferred. Its pass criterion is pre-registered **before** the pull, and that is next sitting's work. |
| **Phase 2 extraction** | `D-168` is written so it is unblocked, but it needs owner presence and its own orders. |
| **Phase 3 ingest** | Additionally needs the §2.3 citation list and `census_ingest_features.py` carrying `D-159` + the role preamble. |
| **`D-169` / `D-170`** | Owed to `SPEC-A-032` §2.6 / §3.7. Not today, not this spec's. |
| Re-reading R1–R4 | ⚠ Ruled and closed. **`r1r4_read.json` never deleted or rewritten.** |
| `RESERVED.md`'s four stale rows | Recorded, not repaired. ⚠ **Not struck** without checking the `re.search` pins. |
| `Q685J3` · `Q9UKN1` | `F-082` (b) stays open. |
| **Any deploy** | Nothing today is deployable. |
| **The close-out** | ⚠ **Deferred.** The day is not over. It is written when the work stops, not before. |

---

## 7. Hygiene, unchanged

**Explicit paths on every `git add`** · literal secrets **stop** a commit, bare words **listed**
(A10.3) · evidence LF and ASCII · ⚠ the untracked `_tmp_c1_*` / `_tmp_c2_*` helpers stay **not read, not
touched, not ruled on** and must not land · new read artifacts added to `.gitattributes` **by name**, as
`r1r4_read.json` was — ⚠ **the glob is not enough for a byte-for-byte guard.**

---

## 8. What "done" looks like

- **AMENDMENT 2 and SPEC v2 committed** to `docs/`.
- **Tunnel 2 opened and closed**, with its own four pieces of evidence, recorded as **tunnel 2 of 2**.
- **E1 · E2 · E3** reported, keys stated, **E3's stop condition checked.**
- **`C5` reported and PAUSED ON** before `C1` ran.
- **`C1a`/`C1b`/`C1c`, `C2`, `C3`, `C4`** reported, each with its key. **`P2` resolved by `C3`**, or
  explicitly left open with the reason.
- **T0 delivered, CI green on both jobs**, offline, **T1 not run.**
- ⚠ **The close-out is NOT written today unless the owner calls the day.**
