# PREWORK — Planner — next session · Phase 2 extraction, the cohort account, and the two public-API gates

> ⚠⚠ **Where this file and the log differ, THE LOG GOVERNS.**
> ⚠ Landing header added by Code at landing, 2026-09-17. **The body below is the document as
> delivered, byte-for-byte**; no AUTHORED-SHA256 range is declared over it.

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Written:** 2026-09-17, America/Los_Angeles, at the end of that session.
⚠ **This document has no calendar date in its title on purpose.** The last prework's `09-17` label
happened to be right; the two before it were not. **Code states the real date at the top of its first
report, from `date -u` and local, naming each frame.**

**Grounded on:** the **merge commit of PR #332** — ⚠ **not `1e67954`, and not `9df612d`.** The Planner
has not seen the merge commit's sha; **Code names it in its first report.** If #332 did **not** merge,
that is the session's first finding and §1 changes.

**Read both:** this document and Code's own prework, if it writes one. ⚠ **Where they disagree, STOP
AND REPORT — do not pick one.**

---

## 0. First five minutes

1. **Grounding.** `git log --oneline -1`, branch, `git status -sb`. ⚠ Confirm the base is the **#332
   merge commit** and that `main` carries `D-168`, `F-081`, `F-082`, all five read artifacts, all four
   instruments and every governing document.
2. **State both dates**, naming each frame. The real date goes in every document written.
3. **Confirm `RESERVED.md`.** Expected: **`D-169` · `F-083` · `A-032`** — ⚠ **unless TASK N spent an
   integer**, in which case `F-` has moved and Code says so.
4. **Fresh-session confirmation** from the owner before anything owner-gated.
5. ⚠ **Read the close-out first**, `docs/CLOSEOUT-2026-09-17.md`, and **TASK N's outcome**. §1 below
   depends on it.

---

## 1. ⚠⚠ The one thing that must be settled before Phase 2: TASK N

**Two readings disagreed about how many rows MUC16 holds** — E1 said one, the session-state report's
§5 item 4 implied two. ⚠ **Two paths to one quantity, on the accession `F-082` is about.**

| if TASK N closed it | then |
|---|---|
| **resolved — two correct readings of different quantities** | ⚠ **No integer.** It is a **keying clarification**, and the fix is that **both readings state their key.** Phase 2 proceeds. |
| **resolved — one instrument was wrong** | ⚠ **A Code finding**, next free integer, spent in the commit that writes it. `F-082` **amended openly** if it carried the overturned figure. Phase 2 still proceeds — ⚠ **the instrument in question does not touch extraction.** |
| **NOT resolved** | ⚠⚠ **The close-out says so plainly and asserts NO count.** Phase 2 **still proceeds** — extraction does not depend on MUC16's row count — but ⚠ **`F-082` stays unamended and nothing cites a MUC16 row figure.** |

⚠ **In no case does this block the day.** It bounds what may be *written*, not what may be *run*.

---

## 2. What is settled, so no time is spent re-deciding it

| question | settled |
|---|---|
| **Population** | **P1 in, unscoped · P2 OUT** (closed on `C3 = 0`, a measurement) **· P3 a ≤100 stratified instrument sample, tagged, never pooled · P4 out** |
| **`D-168`** | **WRITTEN.** Store tagged, **never pool**. ⚠ **Extraction may proceed; ingest may not.** |
| **The instrument** | `feature_version() == e67a8cf30c1c`; `core/features.py` untouched since `8db7345`. **v2 is the same instrument** — this is what makes v1-equality calibration meaningful rather than circular |
| **The coverage picture** | **C1a 776 · C1b 45 · C1c 731.** ⚠ **731 is the only true coverage gap**; the 45 assembled gain **nothing visible** |
| **C5** | **all 2,690 v1 rows reached `protein_features`**, 50/50 sample equal. The covered set **is** v1's set |
| **The cohort** | **proven**, not merely consistent: exactly `P11717`, `Q8WXI7`, `Q9NYQ8` lack a complete tranche-0 row |
| **`C4`'s vocabulary** | **four branches** — assembled · tiles_only · single-pass · **mucin** |
| **SPEC v2** | **eight outcomes** — `overlap_identity_below_minimum` added. T4's sum checks are against eight |
| **Tunnels** | two on 2026-09-17, both fully evidenced. ⚠ **A new day gets a new allowance; state it before opening one** |

---

## 3. THE ORDER OF WORK — do not reorder

1. **Grounding, dates, close-out, TASK N's outcome** (§0, §1).
2. ⚠ **One read-only tunnel: the cohort-account query** (§4). Small, and it closes a question already
   open.
3. **Phase 2 extraction v2** (§5). ⚠ **Local. No tunnel, no production access.** This is the day's
   prize.
4. **`A-032` step 1** and **PDB census T1** (§6) — public-API reads, ⚠ **each with its criterion
   pre-registered before its pull.**
5. **Phase 3 ingest** — ⚠ **almost certainly NOT today.** §7.

⚠ **Steps 3 and 4 do not compete for the tunnel** — neither needs one. If step 2 stops, **3 and 4
still stand.**

---

## 4. The cohort-account query — one tunnel, read-only

**For each of `P11717`, `Q8WXI7`, `Q9NYQ8`: what rows exist AT ALL, by status and by identity**
(whole-protein / tile), with the run label named including `(absent)`.

⚠ **Why it is worth a tunnel:** FAT2 has **no complete cohort row AND no non-complete run-1 row**, so
what a missing cohort accession holds *instead* is unestablished. **The enumeration to date was of
complete rows only.**

- Each count its **own `count(*)`**; ⚠ **every reading states its key** — the day's root-cause defect
  was **rows conflated with accessions** and **populations conflated with each other.**
- ⚠ **Report rows AND distinct accessions separately, always both.** That is the direct guard against
  this session's shared error.
- Standing tunnel conditions unchanged: step-0 encoding probe reads **`10003`**; `.env` still names
  the dead **16380** so the live port is named explicitly; bound by cluster name; Direct IP
  corroborated; one listener; **both pastes**; `SET TRANSACTION READ ONLY`; role preamble; `D-159`.
- ⚠ **Owner at the keyboard, or the departure recorded** — as on both of 09-17's reads.

---

## 5. ⚠⚠ Phase 2 extraction v2 — the day's prize

**Governed by the committed `ORDERS-RECONSTRUCTION-2026-09-17-feature-coverage.md` §4.** ⚠ **Build
from the committed file, never from a chat restatement.** ⚠ §2.4.2 and §2.4.5 remain **unrecovered** —
**if source reading turns up a constraint that document does not state, that constraint is REAL and
the document is incomplete. Report it.**

### 5.1 Tests first

- the `--out` / `--manifest` override;
- ⚠⚠ **refusal to write to any path whose basename is `census_features.v1*`**;
- the outcome categories and the **`structure_kind`** tag — ⚠ **four values, mucin included**;
- the per-protein timeout producing `extraction_timeout`;
- **`PYTHONHASHSEED` pinned in the manifest**;
- the v1/v2 comparator: **equality passes · a one-float change fails on exactly that accession and
  feature · a changed `analysis_id` goes to its CATEGORY, not to a difference.**

### 5.2 The bracketing run — **10 largest first, REPORT BEFORE THE FULL PASS**

### 5.3 The full pass, **owner's go-ahead**, locally

⚠ Run with `PYTHONUTF8=1` if the console is piped — **better: the extractor writes its own log file.**
**Cost reference: v1's 2,690 rows took 38 minutes.** P1 is **3,463**.

### 5.4 Pre-registered outcomes — all four at equal prominence

| # | outcome |
|---|---|
| **a** | v1's rows reproduce **EXACTLY** |
| **b** | ⚠⚠ v1's rows **DIFFER — STOP. A finding.** Two paths to one quantity, and the instrument is supposedly unchanged |
| **c** | the category sums equal `/api/census` rows **exactly** |
| **d** | the gap resolves into `ok` **plus named categories only** — ⚠ **no blank, no skip** |

⚠ **Expected shape, stated so it can be wrong:** roughly **776** representatives gain a feature row,
of which **731** would gain a rendered profile and **45 will not** — their page short-circuits.
⚠⚠ **`D-168` says this in terms, and the report must repeat it, or the work will look like it
failed.**

### 5.5 Commit the comparator report and the v2 artifact **with sha256 in the manifest**

---

## 6. The two public-API gates — pre-registration BEFORE the pull, both

**`A-032` step 1 — UniProt topology feasibility over 3,467 accessions.** ⚠ **A GATE, not a build:** it
**sizes Axis B or kills it.** Write the pass criterion down **first**. Report three keyed numbers with
their own counts — usable tail annotation · none · **unresolved**. ⚠ **A partial pull is reported AS
PARTIAL.** Commit the raw pull with its sha256. ⚠ It **scores nothing and ranks nothing** (`D-079`
dec 1).

**PDB census T1 — the cohort 82**, per committed **SPEC v2**. ⚠⚠ **T1 is INSTRUMENT CALIBRATION, NOT A
RESULT.** Its stop conditions fire if: **HER2 (`P04626`) returns `no_pdb_entry`** (an instrument
failure, not a finding) · **two paths disagree on presence/absence** · **the eight outcomes do not sum
to 82** · **more than 5 land in `accession_unresolved` or `span_unknown`.** ⚠ **A low but coherent hit
rate is NOT a stop — that is the measurement.**

⚠ **Two sum checks, never one: 82 for the cohort pass, 3,467 for the census pass. NEVER 3,474.**

---

## 7. Phase 3 ingest — the conditions, and why it is probably not today

**All three required:** `D-168` written ✅ · the **§2.3 citation list** produced and reviewed ❌ ·
`census_ingest_features.py` carrying **`D-159` and the role preamble** ❌.

⚠ **And it is a WRITE day** — owner at the keyboard, not a read-only tunnel. **Seven documents cite v1
by sha256 (`c08f9f1d…`); v2 is additive and no sealed analysis is re-pointed without a ruling.**

---

## 8. Owner decisions open at the start of the day

| # | decision | Planner recommendation |
|---|---|---|
| 1 | The paper's **§4.3 loss statement**, now zero rows | owner's wording |
| 2 | **v2 timeline class dates** | owner supplies; the proposal PDF is rebuilt around them |
| 3 | ⚠ **The mucin copy sentence** — *"Rental is closed (pod Terminated)"* beside three enqueued `pending` rows | **the tension is in the SENTENCE, not the flag.** One honest sentence: the rental is closed and the rows remain enqueued. **No code. Retiring the rows would change no surface.** |
| 4 | **Credential rotation** | ⚠ still **deferred deliberately** — the literal-secret scan is the only guard and the repo is **public** |
| 5 | **`D-169` / `D-170`** (`SPEC-A-032` §2.6, §3.7) | **after** `A-032` step 1's result, not before |
| 6 | **Phase 2 go-ahead** after the bracketing run | the go/no-go is the owner's, on the 10-largest report |
| 7 | ⚠ **`F-082` (b)** — is the never-folded state a **class property of mucins**? | **stays OPEN.** `C4` mucin = 3 and E2's three pending are **evidence, not an answer.** Closing it needs `Q685J3` and `Q9UKN1` looked at directly |
| 8 | **The v2 proposal's "the fair judge"** phrase | ⚠ sits close to promoting deposited structures to **ground truth**. **They are models fit to experimental data.** Suggest *"the best available check"* before the class presentation |

---

## 9. ⚠⚠ The standing guard for this session, from 09-17's root cause

**One root cause produced three of the day's errors, across both parties:**

- Planner error 12 — R4's set built from the manifest **without checking fold state**;
- Planner error 15 — **`3,467 − 82`**, treating the cohort as a subset of the census when **only 75 of
  82** are members;
- Code's §5 item 4 — **rows conflated with accessions** (5 rows, 4 accessions).

⚠⚠ **All three are the same mistake: a population arithmetic done from the SHAPE of the numbers rather
than from the SETS.**

**Therefore, binding on every reading this session:**

1. **Every count states its key** — population, identity, status, run label. ⚠ **A bare number is not
   a reading.**
2. **Rows and distinct accessions are reported SEPARATELY, always both**, wherever both exist.
3. **Overlapping populations get one sum check each**, never one across both.
4. **Every count is its own `count(*)`** — never a list length, never a subtraction from a total.
5. ⚠ **Any set arithmetic is re-derived from the files, not quoted** — the **75** was re-derived twice
   today and that is why it is trusted.

---

## 10. What "done" looks like

- The base commit stated and confirmed as the **#332 merge**; the real date in every document.
- **TASK N's outcome reflected** in what may be written (§1).
- The **cohort-account query** reported, ⚠ **rows and accessions both**, keys stated.
- **Phase 2:** tests green · the **10-largest bracketing run reported** · owner go-ahead · the full
  pass · ⚠ **the four pre-registered outcomes reported at equal prominence** · artifact and comparator
  committed with sha256.
- **`A-032` step 1** and **T1** reported, ⚠ **each against a criterion written before its pull.**
- A close-out with the true date, carrying everything still open.

## 11. Out of scope

Slice 4 (blocked on the Run-2 identity) · refitting, re-standardising or widening the support ·
scoring census rows (`D-079` dec 1) · re-folding · PAE-dependent features (`F-042`) · `core/scorer.py`
· ⚠ **`RESERVED.md`'s four stale rows** (`F-073`, `A-031`, `D-158`, `D-156`) — **not struck** without
checking the `re.search` pins · ⚠ the untracked `_tmp_c1_*` / `_tmp_c2_*` helpers — **not read, not
touched, not ruled on** · the other two mucins, except where §8 item 7 is explicitly taken up · the v2
model-comparison build.
