# ORDERS — Code — 2026-09-17 · R1–R4, one read-only tunnel

> ⚠⚠ **Where this file and the log differ, THE LOG GOVERNS.**
> ⚠ Landing header added by Code at landing, 2026-09-17. **The body below is the document as
> delivered, byte-for-byte**; no AUTHORED-SHA256 range is declared over it, so nothing is pinned
> by these lines.

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Issued:** 2026-09-17, America/Los_Angeles. The `09-17` label is the real calendar date, confirmed
against Code's `GROUNDING-Code-2026-09-17.md` (10:21 PDT / 17:21 UTC at session open).
**Grounded on:** `origin/main` @ **`1e67954`** (the #331 merge). Local is level with origin per Code's
`git fetch` + `git status -sb`.

**Companions, all three read before execution:**
- `PREWORK-Planner-2026-09-17.md`
- `docs/PREWORK-2026-09-17.md` (Code's, committed at `1b69b3d`)
- `RULING-2026-09-16-D-168-and-session-open.md`
- `GROUNDING-Code-2026-09-17.md` (Code's session-open read; its §6 raised the gaps this document answers)

---

## 0. What this document authorises, and what it does not

**AUTHORISED:** R1–R4 — four read-only readings, in one tunnel, with tests written first.

⚠⚠ **NOT AUTHORISED BY THIS DOCUMENT:**

| not authorised | why not |
|---|---|
| **Phase 1 C1–C5** | Blocked on `GROUNDING` §6.1 — the feature-coverage orders are not on the machine. See §6 below. |
| `scripts/feature_coverage_report.py` | Same block. It is specified by the missing orders. |
| **Any write of any kind** | This is a read-only day. `SET TRANSACTION READ ONLY` is not a courtesy. |
| The `RESERVED.md` stale rows | Real (see §7), but not a measurement-day edit. |
| `D-168`'s text | Written **after** the readings. Its content is already settled — §8. |
| Phase 2 extraction · Phase 3 ingest | Downstream of `D-168`. |
| `A-032` beyond its step-1 feasibility read | Per `SPEC-A-032` §5 and the prework's §9. |

---

## 1. Owner decisions, as ruled at session open

| # | decision | **RULED** |
|---|---|---|
| 1 | Fresh-session confirmation | **GIVEN.** Session is fresh. |
| 2 | Rotate `fly-user` + `WORKER_AUTH_TOKEN`, clear `DATABASE_URL` from `.env` | ⚠ **DEFERRED — deliberately, not pending.** Recorded as a choice, not an omission. |
| 3 | `D-168` commensurability | **ACCEPTED:** store tagged, **never pool**. |
| 4 | Coverage population (P1–P4) | still open — and moot until §6 resolves |
| 5 | Paper §4.3 loss statement | still open, owner's wording |
| 6 | v2 timeline months | still open, owner supplies class dates |

⚠ **On decision 2, stated once and not repeated in this document:** with rotation shelved, the
literal-secret scan before commit is the **only** guard, and the repository is public. That scan is
already a standing condition (§4) and it is not optional today.

---

## 2. Step 0 — the encoding fix and its probe. Before anything else.

Both lines, in this order, in the session that will run the read:

```powershell
$env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
```

Then the probe. **It must read `10003` with exit 0.**

⚠⚠ **The half-fix exits 0 and writes mojibake into the evidence.** A `10003` produced with only one of
the two lines set is a **FAIL**, not a pass with a caveat. Both lines, then the probe, then the paste.

**`.\.venv\Scripts\python.exe` everywhere**, `-m alembic` included. Not `python`, not `py`.

---

## 3. Step 1 — the tranche convention, from source only

Establish it from **`db/models.py` and the enqueue scripts.**

⚠ **Never from the amendment, and never from either prework.** Both preworks paraphrase it, and a
paraphrase is what §6 exists to refuse.

**Report:** what the convention is, and which file established it.
**Stop condition:** if `db/models.py` and the enqueue scripts disagree, **stop and report.** Do not
pick one and do not reconcile them.

---

## 4. Step 2 — tests first, RED at the assertion

Build on `scripts/d167_phase_e_read.py` (confirmed present by Code). The tests pin, at minimum:

1. ⚠⚠ **Every count reads its own `count(*)`.** A test must **fail** if any reading derives a count from
   the length of a list. **This is the session's shared defect class, in both parties' work**, and it is
   the defect the base instrument already carries (the `LIMIT 50` fix).
2. **Any list printed is labelled capped when capped.** A capped list printed as a count is a **FAIL**.
3. `SET TRANSACTION READ ONLY` is issued; the role preamble runs; `D-159`'s identity check is present.
4. Output is **write-once** and carries its **own sha256**.
5. **Output is ASCII.** A non-ASCII byte in the evidence is a **FAIL** — this is what makes the Step 0
   probe checkable *after the fact* rather than only at the time it was run.
6. ⚠⚠ **A fixture that discriminates (`A-017`).** The **R3 assertion must FAIL on a fixture that
   contains a same-population duplicate.** A test that passes on both an empty and a populated fixture
   has measured nothing. This applies to R1, R2 and R4 equally: each must be shown to be capable of
   failing.

**RED first, at the assertion**, then the script. No code before the failing test.

---

## 5. Step 3 — the tunnel · Step 4 — the four readings

### 5.1 The tunnel

- ⚠ **Check `.env` before building `$url`.** It still names the **dead port 16380**, and with rotation
  shelved it may or may not carry a working credential. Do not assume either.
- **Bound by cluster name.** Direct IP **corroborated against `fly mpg status`.**
- **One tunnel.** Closed after. **Both the open and the close evidence pasted.**

### 5.2 The readings — carried verbatim from `ORDERS-…-reattach-and-collapse` A9.2

| reading | what it counts | expectation |
|---|---|---|
| **R1** | groups of `(accession, tile_start, tile_end)` with > 1 complete `run '1'` row, **its own `count(*)`** | **72** |
| **R2** | each such group holds exactly **one** `cohort_tranche = 0` row and exactly **one** tranche ≥ 1 row | **72 of 72** |
| **R3** | the identity key **with** population: groups with > 1 complete row | **0** |
| **R4** | the three named exceptions — `P11717` (IGF2R), `Q8WXI7` (MUC16), `Q9NYQ8` (FAT2) — have no complete tranche-0 row and exactly one complete census row | **3 of 3** |

⚠⚠ **ANY MISS IS A FINDING AND STOPS THE WORK.** Report it; do not reconcile it.

⚠ **R3 ≠ 0 especially.** Nothing in the schema indexes whole-protein identity, so a nonzero R3 is a
**genuine same-population duplicate**, and it bears directly on the Run-2 identity design that blocks
slice 4.

---

## 6. ⚠⚠ The Phase 1 block, and how it resolves

`GROUNDING` §6.1 reports that **`ORDERS-Code-2026-09-16-feature-coverage.md` is not on the machine** —
not in the repo, not in `Downloads` (recursive), not in `Documents` — and neither is
`feature_coverage_census_v7_file_based.csv` (sha256 `f9104d4e…d50c4`).

**Code's refusal to build Phase 1 from a paraphrase is CORRECT and is adopted here.**

⚠⚠ **And the Planner's restatement of C1–C5 in chat does NOT cure it.** *A Planner chat message cannot
ratify what a committed document reserved* — `RULINGS-2026-08-07-span-definition.md` **R5**. That rule
binds the Planner here exactly as it binds anyone else. **The fix is procedural, not conversational.**

**Two paths, owner's choice:**

1. **The original is found.** Owner locates it and commits it. Code builds Phase 1 from the committed
   file.
2. **The original is gone.** The Planner **re-issues** it as a **new** orders document, dated **today**,
   whose header states plainly that it **reconstructs a lost original and is not the original.** Code
   builds from that.

⚠ **What is fully specified and NOT blocked:** R1–R4, carried verbatim in the close-out. **What is NOT
specified:** C2, C3, C5 and the P1–P4 population definitions.

**Until one path completes: R1–R4 only.**

---

## 7. `RESERVED.md`'s stale rows — recorded, not repaired today

**Planner error 10.** The Planner claimed these rows were the file's documented row-table behaviour and
not drift. **Code checked the entries; the Planner had not.** Verified:

| row | reads | actual state |
|---|---|---|
| `F-073` | *"Nothing yet — the next free `F-` integer"* | `### F-073` exists — `docs/findings.md:868` |
| `A-031` | *"Nothing yet — the next free `A-` integer"* | `### A-031` exists — `docs/assumptions.md:388` |
| `D-158` | *"Nothing yet — the next free `D-` integer"* | `### D-158` exists — `docs/decisions.md:1069` |
| `D-156` | *"Nothing yet — the next free `D-` integer"* | `### D-156` exists — `docs/decisions.md:1667` |

**Code found the fourth instance (`D-156`) the Planner had not seen at all. Credited.**

⚠ **Code's diagnosis is adopted over the Planner's:** this is the **`F-044` shape** — a pointer that
exists to prevent drift, itself drifted. It is **NOT** the close-out's §5.5 citation-invariant residual;
that residual concerns references resolving to the *wrong target*, whereas this is **reservation rows
outliving their reservation.** The row table is what the invariant reads, so a stale row is load-bearing
in a way the inline prose is not.

⚠⚠ **DO NOT STRIKE THESE ROWS TODAY.** `tests/_f062_pointer_invariant.py` parses the inline pointer with
`re.search`, and `tests/test_d129_phase5_named_refuse_spec.py` cites specific reserved integers by
number. Code's caution about `re.search` pins is correct. **Recommendation:** name it in the close-out as
its own finding under `F-081`, or defer it with the reason stated.

**Planner error count, carried: 10.**

---

## 8. `D-168` — content settled now, written after the readings

Per `RULING-2026-09-16` §1.2 and the owner's ruling at §1 above:

1. **Creates no new refusal category.** Cites `D-120` / `D-109` ruling 7 and reuses
   **`refused_assembled_incommensurable`**.
2. **States plainly that extracting features for assembled parents changes nothing any page displays** —
   `census_profile_statuses` short-circuits on `_incommensurable_assembly` before the feature row is
   consulted. ⚠ **Without this sentence the work will look like it failed.**
3. **The ruling:** store tagged, **never pool** assembled vectors into a fit or a support range with
   single-pass vectors.
4. **One general sentence on commensurability** — that it is a property of the **instrument and the
   object together**, and that any feature vector must carry enough provenance to establish both before
   it may enter a fit.

### 8.1 Answering `GROUNDING` §4 — the dual-tag question

Code asks whether `model` + `structure_kind` tagging belongs in `D-168` or in the v2 pre-registration,
having spotted that v2's *"never mix models"* and `D-168`'s *"never pool assembled with single-pass"* are
one principle on two axes.

**RULED: `D-168` states the principle; the v2 pre-registration states the mechanism.**

- §8 clause 4 is general, so `D-168` does **not** need re-ruling per model. **This is what Code's catch
  prevents.**
- ⚠ `D-168` must **NOT** specify the v2 artifact's schema. That reaches into a phase it does not govern
  and would make the v2 pre-registration look ratified before it is written. **The tag keys are named and
  pinned by the v2 pre-registration.**

**Code's observation is credited.**

---

## 9. Step 5 — the report

The report **opens** with:

1. **The true base commit — `1e67954`, not `f7d0a9d`.** Code's own prework states the parent; `main` has
   moved twice since. Not a defect in that document, but the true base is restated here.
2. **Confirmation that `RESERVED.md` still reads `D-168` · `F-081` · `A-032`.**
3. ⚠ **Restatement of the two lines that arrived truncated in Code's earlier chat message** — the `D-169`
   line and the `.env`/port line — so that neither party acts on a guess. ⚠ **This matters precisely
   because the session's shared defect class is a truncated read presented as a measurement.**

Then: Step 0's probe paste · the tranche convention and its source file · the RED-then-GREEN test
evidence · the tunnel open and close pastes · **R1–R4 each with its measured value against its
pre-registered expectation** · the output's sha256.

⚠ **Commits use explicit paths, never a broad `git add`.** The untracked `_tmp_c1_*` / `_tmp_c2_*`
helpers predate this session, and their names could be mistaken for today's C1/C2 readings. They must not
land. Code's instinct here is correct: **not read, not touched, not ruled on.**

**Logs scanned before commit:** literal secrets **stop** the commit; bare words are **listed** (A10.3).

---

## 10. What "done" looks like for these orders

- R1–R4 reported, each against its expectation, each with its own `count(*)`.
- One read-only tunnel, opened and closed, **both** evidence pastes present.
- ASCII output, write-once, sha256 recorded.
- Either a clean pass — in which case §6 decides whether Phase 1 opens today — or **a finding, and the
  work stops there.**
