# ORDERS (AMENDMENT 1) — Code — 2026-09-17 · The identity split, the `(absent)` stop condition, and clearance for the tunnel

> ⚠⚠ **Where this file and the log differ, THE LOG GOVERNS.**
> ⚠ Landing header added by Code at landing, 2026-09-17. **The body below is the document as
> delivered, byte-for-byte**; no AUTHORED-SHA256 range is declared over it, so nothing is pinned
> by these lines.

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Issued:** 2026-09-17, America/Los_Angeles. The `09-17` label is the real calendar date.
**Grounded on:** `origin/main` @ **`1e67954`** · branch `d167-r1r4-population-read`, PR **#332**, head
**`7481a55`**.
**Amends:** `ORDERS-Code-2026-09-17-R1-R4.md`. That document otherwise stands in full.
**Answers:** `RESULTS-Code-2026-09-17-R1-R4-instrument.md` §9 items 1, 2 and 3.

⚠ **This amendment adds ONE diagnostic and ONE stop condition. It changes NONE of the four
pre-registered expectations:** R1 **72** · R2 **72 of 72** · R3 **0** · R4 **3 of 3**.

---

## 1. §5 acknowledged — the run-label finding stands, and it is the day's finding

Code established from source that `core/hold48.py`'s `emit_tile_jobs` (`:601–617`) **writes no `run` key
at all**. A tile emitted **after** `backfill_run_label.py` therefore sits outside the run-1 key entirely:
invisible to every R-reading **and to `app.reads.keep_run_1`**, which is what the census surfaces select
by. The tiles earlier phases counted (3693/3695/3696) were stamped only because they **pre-date** the
backfill.

**Accepted as measured, and credited.** ⚠ The consequence for `keep_run_1` is **wider than the orders
asked about** — the orders asked for a predicate statement and got a blind spot in the read path. That is
the finding of the day.

**Code's posture is also ruled correct:** whether such a row exists in production *"is a reading, not a
claim."* Code asserts nothing about it. That is the opposite of this session's shared defect class and it
is how the question stays answerable.

---

## 2. ⚠⚠ RULED — §9 item 1: `(absent)` is (a) **at tile identities** and a **STOP at whole-protein identities**

Code proposed (a): report a non-zero `(absent)`, carry it to the close-out under `F-081`, do not stop.
**Adopted, with one discriminator that decides when it becomes (b).**

| where `(absent)` is non-zero | ruling | why |
|---|---|---|
| at **tile** identities | **(a) — REPORT AND CARRY.** Close-out, under `F-081`. **Does not stop the work.** | Outside R1–R4's registered expectations. R1–R3 group at whole-protein identity; a tile identity is a different subject. |
| ⚠⚠ at **whole-protein** identities | **STOP. A finding in its own right.** Not a carry. | R1 and R3 group on whole-protein identity **and count only labelled rows.** An unlabelled complete whole-protein row could sit inside one of the 72 groups, or form a same-population pair, and **be invisible to both readings.** **`R3 = 0` would then be an artifact of the predicate, not a measurement** — the instrument reporting zero because it cannot see. That is exactly the defect class this session exists to eliminate. |

⚠ **The stop is on the whole-protein branch alone.** A non-zero tile `(absent)` with a zero whole-protein
`(absent)` is a clean day plus a carried finding.

---

## 3. ⚠ ORDERED — the diagnostic split that makes §2 actionable at the read

The two by-run-label diagnostics (`88d8fde`) currently break out **all tranches** and **tranche 0 alone**.

**They must ALSO break out `whole-protein identity` versus `tile identity`**, each branch with **its own
`count(*)`**.

**Why now and not after:** without the split, a non-zero `(absent)` at the read tells the owner and the
Planner **nothing about which branch of §2 it falls in**, and the ruling cannot be applied without a
second look at the database. ⚠ **A second look is a re-read, not a reading.**

**Conditions:**

1. **Identity branch defined as the readings already define it:** whole-protein = `tile_start` and
   `tile_end` **absent**; tile = both present. Same definition R1–R4 group on. **Not a new key.**
2. **Each branch its own `count(*)`.** ⚠ Never a subtraction of one branch from a total, and never a list
   length. This is the session's shared defect class and the instrument already caught it once inside its
   own draft (`len(R4_ACCESSIONS)`).
3. **`(absent)` named as `(absent)`**, as `88d8fde` already does. Not `null`, not blank, not zero.
4. ⚠ **Neither diagnostic applies the key it reports the outside of.** Already true of the existing pair;
   it must remain true of the split.
5. **Tests first**, and **A-017 discriminating**: a postgres test seeds an unlabelled **whole-protein**
   row and proves it appears under `(absent)` / whole-protein, **moves no R-reading**, and **is
   distinguishable from** the existing unlabelled-tile fixture. ⚠ A test that cannot tell the two branches
   apart has not tested the split.
6. **CI green** — `test` and `postgres` both — before the tunnel opens.

⚠ **This is a diagnostic addition. It changes no expectation, no key, and no exit code.** Exit **0** when
all four readings are met; exit **2** when any is not.

---

## 4. §9 item 2 — RULED: nothing else is owed before the tunnel

| obligation | state |
|---|---|
| R4's run-label predicate (`ORDERS` §5) | **DISCHARGED** by `RESULTS` §5 and commit `88d8fde` |
| R4's key — whole-protein identity, tiles as a diagnostic | **RULED CORRECT** (`RULING-Owner-2026-09-17` §6) |
| Tranche convention from source (`ORDERS` §3) | **DISCHARGED**; stop condition did not fire; `NULL` correctly named a **third** population |
| Step 0 encoding fix + probe | standing; **`10003`, exit 0, both lines.** ⚠ The half-fix prints `244` |
| A-017 discrimination on all four readings | **DISCHARGED** (57 postgres tests), **extended** by §3.5 |
| §3's identity split | ⚠ **OWED — the only thing between Code and the tunnel** |

**Once §3 is green, Code is CLEARED for `ORDERS` steps 3 and 4:** the tunnel and the four readings, per
`RUNBOOK-Owner-2026-09-17-R1-R4-read.md`, owner at the keyboard.

---

## 5. ORDERED — `.gitattributes`, adopted from `RESULTS` §8

**`r1r4_read.json` is added to `.gitattributes` BY NAME once it exists**, alongside the three `D-167`
hash-pinned files. ⚠ **The `data/control/d167/**` glob is not sufficient for a byte-for-byte guard.**

**Code raised this before the file existed rather than after. Credited** — that is the order in which this
kind of guard actually works.

---

## 6. ⚠⚠ §7 — Planner error 11. The two documents exist; they were never delivered.

`RESULTS` §7 reports that **`ORDERS-RECONSTRUCTION-2026-09-17-feature-coverage.md`** and
**`RULING-Owner-2026-09-17-population-P1-P4.md`** are absent from the repo, `Downloads` and `Documents`.

**They are. The Planner issued both as files in chat and gave neither a delivery path.**

⚠⚠ **This is the identical failure the Planner had written up as a finding earlier the same day** — a
document cited by filename that exists nowhere the Builder can read — **committed again, twice, inside the
documents that record it.** `F-081`'s question now has three instances, not one:

| document | status |
|---|---|
| `ORDERS-Code-2026-09-16-feature-coverage.md` | never committed to `docs/`; the original is **gone** |
| `ORDERS-RECONSTRUCTION-2026-09-17-feature-coverage.md` | **exists, complete, undelivered** |
| `RULING-Owner-2026-09-17-population-P1-P4.md` | **exists, complete, undelivered** |

**Planner error count, carried: 11.**

**The fix is the owner's and it is mechanical:** download the two documents from the chat into
`C:\Users\mdk32\Downloads\`, and Code commits them to `docs/` with explicit paths. ⚠ **Nothing is
reconstructed a second time.** Both documents are complete as issued; only delivery failed.

⚠ **Until they are on the machine, Code builds no part of Phase 1** — the refusal to build from a
paraphrase stands, and a Planner chat message still cannot ratify what a committed document specifies
(`RULINGS-2026-08-07` **R5**).

---

## 7. §9 item 3 — RULED: where the day ends

**Default: the day ends at R1–R4.**

| if | then |
|---|---|
| the owner drops §6's two files in | **Phase 1 MAY open in the SAME tunnel.** `C3` then resolves **P2**. ⚠ Not a second tunnel. |
| the owner does not | **R1–R4 alone is a clean stopping point.** Phase 1 opens next sitting. **No partial Phase 1.** |

⚠ **Either way: `P2` stays UNDECIDABLE until Phase 1 runs**, because `C3` is its condition and `C3` is a
tunnel reading. **`P1`, `P3` and `P4` are settled and are not contingent on it**
(`RULING-Owner-2026-09-17`).

---

## 8. Carried to the close-out — not optional, and one is reusable

1. ⚠⚠ **The run-label finding (§1)**, under `F-081`: `emit_tile_jobs` writes no `run` key, so
   post-backfill tiles are outside `keep_run_1` and outside every R-reading. **With whichever `(absent)`
   branch the read returns.**
2. ⚠ **The method note, which is reusable and not just this script's fix:** *a source-only ASCII check is
   not an output ASCII check.* Only the assertion on the **printed bytes** caught the section sign in
   `core.db_role.format_preamble`, and **only in CI**. This belongs in the close-out as a **lesson**, not
   merely as `612536c`'s changelog line.
3. **`core/db_role.py`'s section sign** stays on the close-out's existing "make printed output ASCII"
   item. ⚠ **A shared module is not a read-day edit.** Code's decision to fix it in the script was
   correct.
4. **Planner error 11 (§6)** and the three-instance form of `F-081`'s question.
5. `F-079`'s three open exceptions · the citation-invariant residual · the four stale `RESERVED.md` rows
   (`F-073`, `A-031`, `D-158`, `D-156`) — **recorded, not repaired today**, and **not struck** without
   checking the `re.search` pins in `tests/_f062_pointer_invariant.py` and
   `tests/test_d129_phase5_named_refuse_spec.py`.

---

## 9. Unchanged and binding

**One read-only tunnel**, bound by cluster name, Direct IP corroborated against `fly mpg status`
(`fdaa:62:76d9:0:1::9`), exactly one listener, closed after, **both pastes**. ⚠ **Check `.env` before
building `$url`** — it still carries a credential on the **dead port 16380**; **16391 is named in the
runbook, not trusted from the file.** `SET TRANSACTION READ ONLY`, role preamble, `D-159`. Every count its
own `count(*)`; every capped list labelled. Write-once output with its own sha256; ASCII output.
`.\.venv\Scripts\python.exe` everywhere. **Explicit paths on every `git add`** — the untracked
`_tmp_c1_*` / `_tmp_c2_*` helpers must not land, and remain **not read, not touched, not ruled on**.
Literal secrets **stop** a commit; bare words are **listed** (A10.3).

⚠ **A miss on any of the four is a finding. The work stops. Nothing is re-run, nothing is reconciled, and
`r1r4_read.json` is never deleted to re-run.**
