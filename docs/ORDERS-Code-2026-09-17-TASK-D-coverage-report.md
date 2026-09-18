# ORDERS — Code — 2026-09-17 · Rulings on the post-tunnel report, and TASK D: `feature_coverage_report.py`

> ⚠⚠ **Where this file and the log differ, THE LOG GOVERNS.**
> ⚠ Landing header added by Code at landing, 2026-09-17. **The body below is the document as
> delivered, byte-for-byte**; no AUTHORED-SHA256 range is declared over it.

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Issued:** 2026-09-17, America/Los_Angeles. The `09-17` label is the real calendar date.
**Grounded on:** branch `d167-r1r4-population-read`, PR **#332**, head **`222bcdb`**.
**Answers:** `REPORT-Code-2026-09-17-post-tunnel-A-B-C.md` §5 items 1, 2 and 3.
**Supersedes:** `ORDERS-Code-2026-09-17-post-tunnel-D168-F082-coverage-report.md` **§1 only** — see §1
below. The rest of that document stands.

> ⚠⚠ **NO DATABASE CONTACT. NO TUNNEL.** The day's tunnel account is closed at **one tunnel, one read**
> (§2). ⚠ **No further tunnel is authorised today.** If TASK D appears to need one, **stop and report** —
> it has been mis-scoped.

---

## 1. ⚠⚠ RULED — §1.1 ACCEPTED. Planner error 13, and it is worse than the delivery class alone.

`ORDERS-…-post-tunnel-…` **§1 is SUPERSEDED.** It recorded E1–E3 and Phase 1 C1–C5 as *"authorised and
did not run. No report came back."*

**Code measured that `ORDERS-Code-2026-09-17-AMENDMENT-2-phase1-and-enumerations.md` does not exist in
`Downloads`, in `Documents`, or anywhere in the repo. Code never received it.**

⚠ **The delivery failure is the fourth instance of that class. The worse fault is different:** the
Planner **asserted a state it had not verified** — a claim about the Builder's condition made from the
Planner's own record rather than from evidence. ⚠⚠ **That is the session's shared defect class, committed
in the very document that carries the list of it.**

**Planner error count, carried: 13.**

### 1.1 The corrected carry status — this wording, and not the old one

**E1, E2, E3 and Phase 1 `C5` → C1a/C1b/C1c → C2 → C3 → C4 are:**

> **authorised by the Planner, NOT YET DELIVERED to the Builder.**

⚠ **The close-out uses that phrasing and not *"authorised and did not run,"*** which implies a Builder
omission **that did not occur.** The absence of a report was **correct behaviour** on a document Code
never held.

**Nothing is reconstructed.** AMENDMENT 2 stands exactly as written and remains their governing document
once delivered. ⚠ **Until it is on the machine, Code builds no part of E1–E3 or Phase 1** — the refusal
to work from an undelivered document stands, and a Planner chat message cannot ratify it
(`RULINGS-2026-08-07` **R5**).

**Owner action, mechanical:** deliver `ORDERS-Code-2026-09-17-AMENDMENT-2-phase1-and-enumerations.md` to
`C:\Users\mdk32\Downloads\`; Code commits it to `docs/` with explicit paths.

---

## 2. RULED — TASK A accepted. **Case (i): one tunnel, one read.**

Established from **process evidence, not recollection**: one proxy (pid **20176**, opened 20:51Z, Direct
IP `fdaa:62:76d9:0:1::9` **MATCH**, `count: 1`), stopped ≈20:52:45Z, **0 listeners** at 20:52:51Z and
again at 21:23:51Z; one read (`r1r4_read.json`, `2026-09-17T20:52:25Z`), and the script refuses to
overwrite its output.

⚠ **`flyctl.exe agent run` (pid 14960) is named as the likely source of the "tunnel 2" impression** — it
is long-lived, predates the tunnel, **is not a proxy and holds no listener.** Identifying it is what
closes the account rather than leaving it ambiguous. **Credited.**

**The day's tunnel account is WHOLE: one tunnel, one read, both pastes.** ⚠ **The departure stands and is
not smoothed** — the orders said *owner at the keyboard*; the owner instructed Code to run it;
authorisation therefore held in substance, and it is recorded in `r1-tunnel-open.txt` itself.

⚠ **AMENDMENT 2 §4's "tunnel 2 declared" is void** — there was no tunnel 2. The close-out records **one**.

---

## 3. RULED — `D-168` and `F-082` accepted as written. `F-081` confirmed, with one verification.

### 3.1 `D-168` (`8005f27`) — accepted

All six required elements present. ⚠ **Extraction may proceed; ingest may not.**

**Both self-reported defects were handled correctly and are credited:**

1. ⚠⚠ **Refusing to whitelist to make a citation resolve.** The orders permitted **only** the pointer
   edit to `RESERVED.md`, so whitelisting was unavailable; **rewording the *Relates* line to describe the
   two owed rulings instead of numbering them was the only honest route.** ⚠ **Nothing was relaxed to
   turn a red invariant green.** That is the whole point of the invariant.
2. **The landing headers** added **above the body**, with **no body text edited** and no
   `AUTHORED-SHA256` range declared — so nothing is pinned by those lines.

**And the third, smaller catch is the same drift class as `RESERVED.md`'s stale rows:** guard prose
reading *"D-164 is the next free integer"* while the literal barred **168** — the bar had moved and its
sentence had not. **Found in passing, fixed in the same edit, named in the commit.** Credited.

### 3.2 `F-082` (`222bcdb`) — accepted

Carries the per-accession measurement, the cause (**a planned tiled rental span conflated with a protein
actually folded as tiles**), the four committed-record citations, that **`R1 = 72` STANDS** as a direct
`count(*)` not inheriting the Phase E reasoning, the warning that **the "75 overlap" figure is
re-derived before it is cited**, and the **two OPEN sub-questions.**

### 3.3 ⚠⚠ `F-081` — CONFIRMED as written, and the reasoning was better than the orders

**Code was right and the orders were not.** They moved the pointer to **`F-083`**, spending **two**
integers while only `F-082` had an entry. ⚠ **A pointer moved past an unwritten integer is the `D-062`
shape the whole `RESERVED.md` discipline exists to prevent.** Writing `F-081` rather than moving the
pointer over a hole was **correct, and the orders did not tell Code to do it.**

**Content stands:** the run-label blind spot — **OPEN as a latent code defect, CLOSED as a production
condition today** on the measured `(absent)` whole_protein **0** · tile **0** · partial_tile_keys **0**.

⚠ **ONE VERIFICATION, not a change:** confirm the entry states that **`app.reads.keep_run_1` shares the
blind spot.** That is what makes it a **read-path** defect and not merely an **emit-path** one — a
post-backfill tile is invisible to what the census surfaces select by, not just to the R-readings. **If
it is already there, nothing to do; say so.** If not, add that one sentence and nothing else.

---

## 4. ⚠ ORDERED — TASK D: `scripts/feature_coverage_report.py`, tests first. **TASK E deferred.**

**TASK D runs now.** No tunnel, nothing deployable, and **the tests are the hard part** — the best use of
what remains of the day.

**TASK E (`A-032` step 1) is DEFERRED to the next sitting.** ⚠ Its pass criterion must be pre-registered
**before** the pull, and that deserves a clear head rather than the end of a long day. **It gates a
November decision and carries no deadline pressure this week.**

### 4.1 Build from the committed document

⚠ Build from **`docs/ORDERS-RECONSTRUCTION-2026-09-17-feature-coverage.md`** as committed. **Never from a
chat restatement** (`RULINGS-2026-08-07` **R5**).

⚠⚠ **If Code's source reading turns up an architecture constraint that document does not state, that
constraint is REAL and the document is incomplete — REPORT IT.** §2.4.2 and §2.4.5 are **unrecovered and
were not reconstructed.** Silence is not evidence they were dropped deliberately.

### 4.2 What the tests pin — at minimum

1. ⚠⚠ **The `_incommensurable_assembly` short-circuit is modelled.** An **assembled parent with no
   feature row → C1b, NOT C1c.** A **single-pass row with no feature row → C1c.** Without this the script
   reproduces the Planner's CSV error.
2. **`C1c = C1a − C1b`, labelled the ONLY true coverage gap.**
3. ⚠ **Every count is its own `count(*)`.** A test **FAILS** if any count derives from a list length —
   the session's shared defect class, which the R1–R4 instrument already caught **inside its own draft**
   (`len(R4_ACCESSIONS)`).
4. **Every capped list says it is capped**, carrying a count it did **not** derive from its own length —
   capped at the cap **or below it.**
5. ⚠ **Printed output is ASCII, asserted on the PRINTED BYTES.** *A source-only ASCII check is not an
   output ASCII check* — only the printed-byte assertion caught `core.db_role.format_preamble`'s section
   sign, and **only in CI.**
6. **`choose_census_representative` is IMPORTED from `app/reads.py`** — one home, never re-implemented.
7. **Each reading states its key.** ⚠ **A bare number is not a C-reading.**
8. **A-017 discrimination:** every assertion is shown **capable of failing**, on a fixture that makes it
   fail. ⚠ An assertion that passes on both an empty and a populated fixture **has measured nothing.**
9. **`C2`** is a **named category** — stale representative — reporting **count AND ids**, with **no
   pre-set expectation**: the count is the measurement.
10. **`C4`** breaks **C1a** down by `structure_kind` — assembled parent / tiles-only / single-pass — each
    branch its **own `count(*)`**, never a subtraction from a total.

### 4.3 ⚠ There is no §1 table to reproduce or to differ from

The source CSV is gone (`RECONSTRUCTION` §1). **The script's output IS the measurement.**

⚠⚠ **The `777` figure is a HISTORICAL QUOTATION, not a live number.** The script **does not reconcile
against it**, does not cite it as an expectation, and does not print it as a comparison. ⚠ The original
expectation that survives is on **C1a ≥ 773**, and **a SMALLER number is a finding** — it would mean
features arrived from a source not yet accounted for.

### 4.4 Done means

**CI green — `test` AND `postgres` both.** ⚠ **No deploy.** This is not a deployable change: the script
**reads and reports only.**

⚠ **The script is NOT run against the database today.** It is built and proven by its tests. Its first
real execution belongs to Phase 1's tunnel, under AMENDMENT 2, **once that document is delivered.**

---

## 5. Not authorised

| not authorised | why |
|---|---|
| **E1, E2, E3 · Phase 1 `C1`–`C5`** | ⚠ AMENDMENT 2 **undelivered** (§1). Authorised by the Planner, not yet held by the Builder. |
| **Any tunnel** | The account is closed at one (§2). |
| **TASK E (`A-032` step 1)** | Deferred (§4). |
| **Phase 2 extraction** | `D-168` is written, so this is **unblocked for the next sitting** — but it is not authorised by this document and needs owner presence. |
| **Phase 3 ingest** | Additionally requires the §2.3 citation list and `census_ingest_features.py` carrying `D-159` + the role preamble. |
| **`D-169` / `D-170`** | After `D-168`, not today. |
| Re-reading R1–R4 | ⚠ Ruled and closed. **`r1r4_read.json` is never deleted or rewritten.** |
| `RESERVED.md`'s four stale rows | Recorded, not repaired. ⚠ **Not struck** without checking the `re.search` pins in `tests/_f062_pointer_invariant.py` and `tests/test_d129_phase5_named_refuse_spec.py`. |
| The other two mucins (`Q685J3`, `Q9UKN1`) | `F-082` sub-question 2 stays **open and unmeasured.** |

---

## 6. Hygiene, unchanged and binding

`.\.venv\Scripts\python.exe` everywhere, `-m alembic` included · **explicit paths on every `git add`** ·
literal secrets **stop** a commit, bare words are **listed** (A10.3) · evidence LF and ASCII ·
**`r1r4_read.json` never deleted or rewritten**, protected **by name** in `.gitattributes` · ⚠ the
untracked `_tmp_c1_*` / `_tmp_c2_*` helpers stay **not read, not touched, not ruled on** and must not
land · `.env` still carries a credential on the dead **16380**, consistent with rotation being **deferred
deliberately.**

---

## 7. The close-out carries all of this

1. **Today's result:** **R1, R2, R3 MET** (72 · 72 of 72 · 0); **R4 NOT MET at 2 of 3**, ruled a
   **mis-specified expectation**, recorded as **`F-082`**.
2. ⚠ **The tunnel account: ONE tunnel, ONE read, both pastes** (§2). **No tunnel 2 existed**;
   AMENDMENT 2 §4's declaration is **void**. `flyctl agent run` named as the likely source of the
   impression.
3. ⚠ **The owner-at-the-keyboard departure** — recorded in `r1-tunnel-open.txt`, **not smoothed.**
4. **`D-168` WRITTEN** (`8005f27`). Extraction unblocked for the next sitting; **ingest still barred.**
5. **`F-081` and `F-082` WRITTEN** (`222bcdb`); inline `F-` pointer **081 → 083**, `D-` pointer
   **168 → 169**, superseded values recorded rather than overwritten.
6. ⚠⚠ **`F-081`'s substance:** the run-label blind spot — `emit_tile_jobs` writes no `run` key — **real in
   source, ZERO instances in the database today**, **latent for the next tile emission**, and
   **`app.reads.keep_run_1` shares it.**
7. **`F-082`'s two OPEN sub-questions:** MUC16 by status; ⚠ **whether the never-folded state is a CLASS
   property of mucins.**
8. ⚠ **The "75 overlap" figure rests on the same conflation as R4's set — re-derive before citing.**
9. ⚠ **The reusable method note:** *a source-only ASCII check is not an output ASCII check.* A **LESSON**,
   not a changelog line.
10. **`core/db_role.py`'s section sign** stays on the existing "make printed output ASCII" item. ⚠ A
    shared module is not a read-day edit.
11. ⚠ **The stale guard prose** (*"D-164 is the next free integer"* while the literal barred 168) — fixed,
    and named as the same drift class as `RESERVED.md`'s four stale rows.
12. ⚠⚠ **`E1`–`E3` and Phase 1 `C1`–`C5`: AUTHORISED BY THE PLANNER, NOT YET DELIVERED TO THE BUILDER**
    (§1.1). ⚠ **`P2` undecidable until `C3`.**
13. ⚠ **The delivery failure class, FOUR instances**, and **Planner error 13** — a state asserted without
    verification, in the document listing the defect class.
14. **Planner error count 13. Code error count 7**, unchanged.
15. `F-079`'s three open exceptions · the citation-invariant residual · the four stale `RESERVED.md` rows.
16. **Owner decisions still open:** the paper's **§4.3 loss statement** (now zero rows, owner's wording) ·
    the **v2 timeline class dates** · **`D-169` / `D-170`** · **credential rotation** (deferred
    deliberately).
17. **The true calendar date: 2026-09-17.**
