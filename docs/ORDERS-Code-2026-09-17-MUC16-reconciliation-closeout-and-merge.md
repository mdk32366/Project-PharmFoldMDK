# ORDERS — Code — 2026-09-17 · The MUC16 reconciliation, the close-out, and the merge of PR #332

> ⚠⚠ **Where this file and the log differ, THE LOG GOVERNS.**
> ⚠ Landing header added by Code at landing, 2026-09-17. **The body below is the document as
> delivered, byte-for-byte**; no AUTHORED-SHA256 range is declared over it.

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Issued:** 2026-09-17, America/Los_Angeles. The `09-17` label is the real calendar date.
**Grounded on:** branch `d167-r1r4-population-read`, PR **#332**, head **`9df612d`** — 26 commits, 65
files, +8,901 / −58. CI run **35287019818** green on both jobs.
**Answers:** `REPORT-Code-2026-09-17-SESSION-STATE.md` §8 items 1 and 2.

> ⚠⚠ **NO DATABASE. NO TUNNEL. NO NETWORK.** Two tunnels exist for 2026-09-17, both fully evidenced;
> **a third is not authorised and TASK N does not need one.** ⚠ **Nothing in this document deploys.**

---

## 1. ⚠⚠ TASK N — FIRST, and nothing else proceeds until it is settled

**Two readings in the same session disagree about how many rows MUC16 holds.**

| source | says |
|---|---|
| **E1** (§3.3 of the tunnel-2 report) | **`Q8WXI7`: 1 row in total** — `pending`, whole-protein, run `1`, tranche 5 — and **"no cohort-side row at all"** |
| **§5 item 4** (session-state report) | the 5 non-complete rows resolve to **4 distinct accessions, "because MUC16 holds one on each side"** — i.e. **2 rows** |

⚠⚠ **Both cannot be true. This is TWO PATHS TO ONE QUANTITY** — this project's most-repeated defect
class — **in one session, on the accession `F-082` is about.**

**Reconcile from `e1_e3_read.json` ALONE.** ⚠ It holds both readings, so **no tunnel is needed and
none is authorised.** Report:

1. **Which is right**, with the key each reading actually used — population, identity, status filter,
   run-label predicate.
2. **What the other was counting**, named precisely. ⚠ *"An error"* is not an answer; **a reading that
   was correct about a different quantity is the likely shape**, and it is the shape that must be
   stated.
3. **Whether `F-082` already carries the one-row figure.** ⚠ **If it does and E1's figure is wrong,
   `F-082` is AMENDED** — openly, in place, with the correction recorded, **never quietly patched.**
4. ⚠ **Whether E1's phrase "no cohort-side row at all" survives** the reconciliation, or needs
   rewording.

⚠⚠ **UNTIL THIS IS SETTLED: neither the close-out nor `F-082` states any MUC16 row count.** A number
that two readings disagree about is not a measurement, and **a finding carrying a wrong count gets
cited for a year.**

**This spends no integer** — it is a reconciliation of existing readings. ⚠ If it turns out one
instrument was wrong rather than differently scoped, **that is a Code finding and it takes the next
free integer**, confirmed from `RESERVED.md` in the commit that spends it.

---

## 2. TASK O — `docs/CLOSEOUT-2026-09-17.md`. Code writes it, from the artifacts.

⚠ **Code assembles it from measurements, not the Planner from the conversation.** That is deliberate:
assembling from recollection is the habit behind **Planner errors 13 and 15**, and §§1–7 of the
session-state report are already the raw material.

**It states the true calendar date: 2026-09-17.** It carries §§1–7 of the session-state report, plus:

1. ⚠⚠ **TASK N's reconciliation** — and if unresolved, **that fact, plainly**, with both readings and
   no count asserted.
2. **`C4` mucin = 3** — the weak pre-registration and its result, ⚠ noting it is **evidence toward
   `F-082` (b), never an answer.**
3. **SPEC v2's eighth outcome, `overlap_identity_below_minimum`**, recorded as a **Planner amendment**
   to the committed spec's §1 — ⚠ **the spec's body is NOT edited.** T4's sum checks are against
   **eight**.
4. **TASK M's finding** on the folded-flag provenance, and ⚠ the mucin copy tension: *"Rental is
   closed (pod Terminated)"* beside three enqueued `pending` rows. **The tension is in the SENTENCE,
   not the flag**; retiring the rows would change **no** surface. ⚠ **A copy question, owner's call,
   no code.** Nothing changed.
5. **The tunnel account: TWO tunnels, both fully evidenced, no third.** ⚠ `AMENDMENT 2` §4's
   "tunnel 2 declared" is **VOID for the morning** — case (i) stands, `flyctl agent run` named as the
   likely source of that impression. ⚠ **The owner-at-the-keyboard departure on BOTH reads is
   recorded, not smoothed.**
6. ⚠⚠ **CI was the instrument for THREE of the four defects Code's own work produced** — printed
   ASCII, the vanishing `C4` branch, rows-versus-accessions. **All three invisible locally, because
   the local machine has no database.** ⚠ **Record as a standing fact about the project's test
   topology, not as a run of bad luck.**
7. ⚠ **The reusable method note: *a source-only ASCII check is not an output ASCII check.*** A
   **LESSON**, not a changelog line.
8. **The error ledger: Planner 15 · Code 7.** ⚠ **Code stays at 7 deliberately** — the four defects in
   §5 were caught **before they reached a reading**, by the instruments' own tests and by CI. **An
   instrument catching its own author is the system working, not an error escaping it.**
9. ⚠ **One root cause, three instances, across both parties, in one day:** conflating rows with
   accessions (§5 item 4) is the same family as conflating populations (Planner errors 12 and 15).
   **Name it once, in those terms.**
10. **Everything in §6.1, §6.2 and §6.3** of the session-state report, unchanged — open owner
    questions, what is ordered for the next tunnel, and what is standing-and-not-repaired.
11. **Next sitting, in order:** the cohort-account query (what the three missing accessions hold
    **instead** — FAT2 has no complete cohort row **and** no non-complete run-1 row) → **`A-032`
    step 1**, pass criterion pre-registered **before** the pull → **T1** of the PDB census, ⚠ whose
    stop condition **needs a fresh head** → **Phase 2 extraction**, owner present.

---

## 3. TASK P — merge PR #332

**Sequence, not to be reordered:**

1. **TASK N settled** (or its irreducible state recorded).
2. **Close-out committed to the branch.**
3. **CI green.**
4. **Merge.**

**Why merge:** 26 commits, CI green, **nothing deployable.** ⚠⚠ **And the standing reason, stronger
now than this morning:** a branch carrying **four log entries, five read artifacts, four instruments
and every governing document** is exactly the base-commit trap that produced **two grounding errors
today** — Code's prework grounded on `f7d0a9d` while `main` had moved twice, and the Planner asserting
a Builder state from its own record.

⚠ **The next sitting grounds on the MERGE COMMIT**, so `main` already carries `D-168`, `F-081`,
`F-082`, all five artifacts, all four instruments and every document.

⚠ **Explicit paths on every `git add`.** The untracked `_tmp_c1_*` / `_tmp_c2_*` helpers stay **not
read, not touched, not ruled on**, and **none lands in the merge.**

---

## 4. Not authorised

| not authorised | why |
|---|---|
| **A third tunnel** | Two exist, both evidenced. ⚠ **TASK N does not need one** — `e1_e3_read.json` holds both readings. |
| **T1 / T2 / T3** | ⚠ T1's stop condition needs a fresh head. Next sitting. |
| **`A-032` step 1** | Pass criterion pre-registered **before** the pull. Next sitting. |
| **The cohort-account query** | Ordered for the next tunnel. |
| **Phase 2 extraction** | Unblocked by `D-168`; needs owner presence and its own orders. |
| **Phase 3 ingest** | Additionally needs the §2.3 citation list and `census_ingest_features.py` carrying `D-159` + the role preamble. |
| **`D-169` / `D-170`** | Owed to `SPEC-A-032` §2.6 / §3.7. |
| **Any change to the mucin copy, any label, any flag** | ⚠ Owner's call. §2 item 4. |
| **Editing the committed SPEC v2's body** | §2 item 3 — the amendment is **recorded**, not edited in. |
| Re-running or re-reading any of the five artifacts | ⚠ **Never deleted, never rewritten.** They are read, not re-run. |
| `RESERVED.md`'s four stale rows | ⚠ **Not struck** without checking the `re.search` pins in `tests/_f062_pointer_invariant.py` and `tests/test_d129_phase5_named_refuse_spec.py`. |
| **Any deploy** | Nothing today is deployable. |

---

## 5. Hygiene

`.\.venv\Scripts\python.exe` everywhere · **explicit paths on every `git add`** · literal secrets
**stop** a commit, bare words **listed** (A10.3) · evidence LF and ASCII · printed output ASCII **on
the printed bytes** · artifacts EOL-protected **by name**, ⚠ the glob is not enough · `.env` still
carries a credential on the dead **16380**, consistent with rotation being **deferred deliberately** —
⚠ **the literal-secret scan is the only guard and the repository is public.**

---

## 6. What "done" looks like

- **TASK N reported** — which reading is right, what the other counted, and `F-082` amended **if and
  only if** it carries a figure the reconciliation overturns. ⚠ **No MUC16 row count anywhere until
  then.**
- **`docs/CLOSEOUT-2026-09-17.md`** written from the artifacts, carrying §2's eleven items.
- **CI green**, then **PR #332 merged**, in that order.
- **The next sitting grounds on the merge commit**, not on `1e67954`.
