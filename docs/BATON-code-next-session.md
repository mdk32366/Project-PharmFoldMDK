# BATON — Code, next session

> **Paste this to open the session.** It is a handoff, not a summary: everything here is either a
> constraint on what you may do or a pointer to the thing that governs.

---

You are resuming **PharmFoldMDK** (`C:\Projects\Project-PharmFoldMDK`, branch `census/task3-spans`),
an ADC target-exploration platform built as graded Deep Learning coursework.

**Read first, in this order:**
1. `docs/PREWORK-2026-08-18.md` — what to do, and what not to run.
2. `docs/CLOSEOUT-2026-08-17.md` — state, and §5, which is an incident report.
3. `docs/README.md` — **the decision log. It GOVERNS.** Where anything disagrees with it, it wins.

---

## ⚠⚠ Four things that will bite before anything else

**1. NEVER run `pytest` in a shell where `.env` has been sourced.** `tests/test_queue_postgres.py`
opens every test with `TRUNCATE TABLE jobs, protein_analyses, ranking_runs RESTART IDENTITY
CASCADE`. On 2026-08-17 that destroyed production — **2,771 rows to 1** — and was recovered from a
Fly backup **nobody had verified existed**. A guard now refuses non-disposable hosts (KEEL V8-a),
but ⚠ **a tunnel to production looks exactly like `localhost`, and `localhost:16380` is one.**

**2. The local proxy dies with its shell.** `fly mpg proxy zp2wjrej9lwodn4q -p 16380`.
⚠ **Do NOT run `dev-up.ps1`** — second proxy, same fixed port.

**3. For prose containing backticks or markup, write a script FILE.** A shell one-liner executes
backticks as command substitution and silently empties them.

**4. Confirm every `D-`/`F-` integer against the live log before claiming one.** Next free:
**`D-095`, `F-041`.**

---

## Where the work stands

**The entire local-tier census is folded: 2,690 rows, tranches 1–4, two failures — both named.**
The site is live and serves a searchable, sortable per-protein surface. Nothing in the census is
scored (D-079 bars it), and every row says so.

**Your first job is `docs/PREWORK-2026-08-18.md` §3 — the tranche 6 design document.** The owner
ruled it in front of everything, including 566 rental rows that would cost about $12–20 to fold.
⚠ **No GPU, no rental, no ingest until it is written and ruled.**

Its cheapest first move is stated there: **count the domains each of the 10 proteins has under
UniProt / Pfam / InterPro and check whether they agree.** Cache-only. ⚠ That answers whether the
boundary source is even a live question before you design around it.

---

## How this project works — the parts that are not obvious

- ⚠ **The log leads the code.** A decision is written before the work it authorises.
- ⚠ **Every absence is a CATEGORY with a cause** — never a zero, never a bare null, never a low
  number. This has found more real defects than any test.
- ⚠ **State a composition, never only a total.** *"2,690"* says nothing; the per-tranche breakdown
  does.
- ⚠ **A filename is not an identity** — record the sha256. Two different documents arrived under one
  filename on 2026-08-17 and copying one in would have destroyed the other silently.
- ⚠ **Corrections are recorded, never patched away.** No row is retrofitted to make numbers agree.
- ⚠ **A revert proof, or the test proves nothing.** Break the code deliberately and confirm the test
  reds.
- ⚠ **Capture `$?` on the line immediately after the command** — an assignment in between captures
  the wrong exit code, and that shipped a red gate once.
- ⚠ **Assert that a string replacement applied.** An unasserted `.replace()` shipped a silent row
  cap that claimed to show 2,641 rows while drawing 200.
- ⚠ **Verify a deploy keyed on the commit SHA.** `gh run list --limit 1` right after a merge returns
  the *previous* run.
- ⚠⚠ **A rule applied to one shape and not another is not a rule.** *"No hand-written SQL against
  production"* was honoured for `SELECT`s while a test suite — which does far worse — was treated
  as safe.

**The owner's standing prohibitions:** no hand-written SQL against production · a permission denial
is **STOP AND REPORT**, never a retry or a workaround · do not merge anything to make numbers agree
· no rebase, squash, amend or force-push on this history.

---

## Open, and blocked on the owner

`P55073` substitution (ruled, not implemented) · KEEL V8-b (proposed, not adopted) · `reap_stale` is
never called — a `claimed` job has **no automatic recovery path** · the DB credential is unrotated ·
the three merged entries (`D-093`, `D-094`, `F-040`) were **merged but not reviewed against current
code**, and each bears on surfaces built after it was written.

⚠ **F-040 is open by design** — a finding against the instrument stays open until the instrument
stops exhibiting it.
