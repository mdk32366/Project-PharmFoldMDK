# REPORT — Code → Planner — 2026-09-17 · TASK A (the tunnel account), TASK C (`D-168`), TASK B (`F-082`, and `F-081`)

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Session:** 2026-09-17, America/Los_Angeles (PDT). **Governs:**
`ORDERS-Code-2026-09-17-post-tunnel-D168-F082-coverage-report.md`.
**Branch:** `d167-r1r4-population-read`, PR #332. **No database contact.** No tunnel was opened for any
task in this report.

---

## 1. ⚠⚠ TASK A — the tunnel account. **Case (i): there was exactly ONE tunnel today.**

**Code states, with evidence, that no second tunnel was ever opened.** `r3-tunnel-closed.txt` is accurate.

| # | evidence | reading |
|---|---|---|
| 1 | Only one proxy process was ever started in this session: **pid 20176**, `fly.exe mpg proxy kyzl60xz9zyrpj9g -p 16391`, opened **20:51Z**, recorded in `r1-tunnel-open.txt` with its own open line, its own Direct-IP corroboration (`fdaa:62:76d9:0:1::9` — **MATCH**) and its own single-listener confirmation (`count: 1`). | one tunnel, fully evidenced |
| 2 | It was stopped at **≈20:52:45Z**; `r3-tunnel-closed.txt` records **0 listeners** on 16300–16499 at **20:52:51Z**, and pid 20176 gone. | closed, with its own close line |
| 3 | Re-checked at **21:23:51Z** on the owner's question *"is there a tunnel open?"*: **0 listeners** in that range, **no listener of any port** owned by a `fly`/`flyctl` process. | still closed |
| 4 | The only surviving Fly process is **pid 14960, `flyctl.exe agent run`** — the background agent, present **before** the tunnel was opened and noted the same way in the 2026-09-15 close evidence. ⚠ **It is not a proxy and holds no listener.** | not a tunnel |
| 5 | Exactly **one** read was taken, and it is the one in `r1r4_read.json` (`read_at_utc 2026-09-17T20:52:25Z`). The script **refuses to overwrite** its output, so a second read would have had to be written elsewhere; no such file exists. | one read |

⚠ **The most likely source of a "tunnel 2" impression is item 4** — `flyctl agent run` is long-lived and
looks like Fly activity in a process list while holding nothing open.

**So the day's account is whole: one tunnel, one read, both pastes present.** ⚠ **The departure stands
and is not smoothed:** the orders said *owner at the keyboard*, and the owner instructed Code to run it;
that is recorded in `r1-tunnel-open.txt` itself.

### 1.1 ⚠ A correction the account requires — AMENDMENT 2 was never delivered

The orders' §1 records **E1, E2, E3 and Phase 1 C1–C5** as *"authorised and did not run. No report came
back,"* governed by `ORDERS-Code-2026-09-17-AMENDMENT-2-phase1-and-enumerations.md`.

**Measured:** that document **does not exist** in `Downloads`, in `Documents`, or anywhere in the repo.
**Code never received it.** So those tasks were never authorised *to the Builder*, and the absence of a
report is not a Builder omission — **it is the delivery failure class again, a fourth instance.**

⚠ **This does not dispute the authorisation; it dates it.** If the Planner re-delivers AMENDMENT 2, E1–E3
and Phase 1 are executable next sitting exactly as written. **Nothing is reconstructed.**

---

## 2. TASK C — `D-168` written. Commit `8005f27`.

`### D-168 — Features measured on an assembled chain are STORED AND TAGGED, never pooled into a fit or a
support range with single-pass vectors — and extracting them changes nothing any page displays`
(`docs/decisions.md`, at the top, newest-first).

**It carries all six required elements:** no new refusal category (reuses
`refused_assembled_incommensurable`, cites `D-120` / `D-109` ruling 7, records the orders' §2.2 as
superseded — **Planner error 9, found by Code reading source** — and supersedes
`no_protein_level_structure` as a profile category while keeping `structure_kind` as a non-refusal tag) ·
the plain statement that the profile short-circuit means **extraction changes nothing any page displays**,
with `C1b` named as the figure that sizes it · the ruling **store tagged, never pool** · the general
commensurability sentence (*a property of the instrument and the object together*) so it needs no re-rule
per model · and an explicit refusal to specify the v2 artifact's schema.

⚠ **Extraction may proceed; ingest may not.**

### 2.1 The pointer and the guards moved in the same commit

`RESERVED.md`'s **inline** `D-` pointer: **168 → 169**, superseded value recorded rather than overwritten.
⚠ **That was the only edit to that file.** The four stale row entries were **not** struck.

**Nine guard files** now **NAME** `### D-168` and bar `### D-169`; **two enumerations ADD 168**; the two
meta-guards and **ten pointer pins** move to 169. **A name was ADDED and nothing became a `>=`.**

### 2.2 ⚠ Two things the suite caught — both mine, both reported rather than worked around

1. **The citation invariant reddened.** My first draft's *Relates* line named two
   reserved-but-unwritten integers, and the invariant resolves only written entries and whitelisted rows.
   ⚠ The orders permit **only** the pointer edit to `RESERVED.md`, so **whitelisting was not available and
   was not done.** The entry was **reworded** to describe those two owed rulings instead of numbering
   them. **Nothing was relaxed to make a citation resolve.**
2. **The five documents landed at `00badb9` carried no landing header** — `test_docs_landing_headers.py`
   failed. A header was added to each **above the body**, at landing, and **no body text was edited**;
   none of the five declares an `AUTHORED-SHA256` range, so nothing is pinned by those lines.

⚠ **A third, smaller thing, corrected rather than left:** the bar prose in those guards read *"D-164 is
the next free integer"* while the literal barred **168** — the bar had been moved and its sentence had
not. Fixed in the same edit and named in the commit.

---

## 3. TASK B — `F-082` written, **and `F-081` with it**. Commit `222bcdb`.

**`F-082`** — R4's expectation was mis-specified for MUC16 — carries the per-accession measurement, the
cause (*a planned tiled rental span conflated with a protein actually folded as tiles*), the four
committed-record citations, the statement that **`R1 = 72` STANDS** as a direct `count(*)` that does not
inherit the Phase E reasoning, the warning that **the "75 overlap" figure is re-derived before it is
cited**, and the two OPEN sub-questions (MUC16 by status; whether this is a class property of mucins).

⚠⚠ **`F-081` had to be written in the same commit.** The orders move the pointer to **`F-083`**, which
spends **two** integers — but **no `### F-081` existed.** Moving a pointer past an integer with no entry
is precisely the `D-062` shape this project restored `RESERVED.md` to prevent. So `F-081` is now written:
the run-label blind spot, **OPEN as a latent code defect, closed as a production condition today** on the
measured `(absent)` = 0 / 0 / 0.

⚠ **If the Planner intended `F-081` to be written later or differently, say so** — it is one entry and it
can be amended. **What it cannot be is cited and absent.**

The inline `F-` pointer moved **081 → 083** in that commit, and
`tests/test_f062_ceiling_climb.py`'s pin moved **by name** (81 → 83; highest spent heading 80 → 82),
never relaxed.

---

## 4. State

- **Local suite: 2,744 passed, 60 skipped, 1 xfailed, 0 failed.** CI running on `222bcdb`.
- **Not started:** **TASK D** (`scripts/feature_coverage_report.py`) and **TASK E** (`A-032` step 1).
  ⚠ Per the orders' §7 priority, C → A → B came first and they are complete.
- **Unchanged:** `r1r4_read.json` never deleted or rewritten, EOL-protected by name · explicit paths on
  every `git add` · the untracked `_tmp_c1_*` / `_tmp_c2_*` helpers **not read, not touched, not ruled
  on** · `.env` still carries a credential on the dead 16380.

## 5. What Code asks the Planner for

1. **Accept or correct §1.1** — AMENDMENT 2's non-delivery, and whether E1–E3 and Phase 1 carry as
   *authorised* or as *not yet delivered*. It changes what the close-out claims, not what is owed.
2. **Confirm `F-081`'s content** (§3), since Code wrote it to keep the pointer honest rather than because
   the orders specified its text.
3. **Whether TASK D and TASK E run next**, or whether the day closes here and they open the next sitting.
