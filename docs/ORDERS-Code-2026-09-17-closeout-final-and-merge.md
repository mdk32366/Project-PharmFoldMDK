# ORDERS — Code — 2026-09-17 · TASK N accepted · the close-out, with its wording fixed · then the merge

> ⚠⚠ **Where this file and the log differ, THE LOG GOVERNS.**
> ⚠ Landing header added by Code at landing, 2026-09-17. **The body below is the document as
> delivered, byte-for-byte**; no AUTHORED-SHA256 range is declared over it.

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Issued:** 2026-09-17, America/Los_Angeles. The `09-17` label is the real calendar date.
**Grounded on:** branch `d167-r1r4-population-read`, PR **#332**, head at Code's latest commit.
**Amends:** `ORDERS-Code-2026-09-17-MUC16-reconciliation-closeout-and-merge.md` — **§1 is
DISCHARGED**; **§2 stands with the additions below**; **§3 stands unchanged.**

> ⚠⚠ **NO DATABASE. NO TUNNEL. NO NETWORK.** Nothing in this document deploys.

---

## 1. TASK N — ACCEPTED AND CLOSED. No integer spent.

**`E1` is right: MUC16 holds exactly ONE row** — `pending`, whole-protein, run `1`, tranche 5.

⚠ **The key does the work:** `E1` filters nothing, so `total: 1` is **every job row that exists for
that accession**, and the absence of a tranche-0 cell is the absence of a cohort-side row **in any
status**, not merely of a complete one. **`E2` corroborates from the other direction** — the only
tranche-0 row among the five non-complete rows is `P11717`, job 57, failed.

| ruling | |
|---|---|
| **"No cohort-side row at all"** | ⚠ **SURVIVES — and is now the STRONGER claim**, because it is about existence rather than completeness |
| **Its boundary** | ⚠ **KEPT IN THE RECORD:** this is `jobs` joined to `protein_analyses`. Whether a `protein_analyses` row exists for MUC16 **WITHOUT a job is UNMEASURED** by either reading — **the same question FAT2 raises**, already ordered for the next tunnel |
| **`F-082`** | ⚠ **NO AMENDMENT.** It asserts **complete**-row counts only (0 · 0 · 0 · 0), and the one row is `pending`, outside every figure it states. **Its counts may be stated as written.** |
| **MUC16's row count** | **may now be stated: ONE**, with `E1`'s key quoted alongside it |

### 1.1 ⚠⚠ The error's shape — recorded because it is the interesting part

**A correct total carried a false cause.** The number **5** was right; *"because MUC16 holds one on
each side"* was **fixture behaviour**, from `_seed` in `tests/test_d167_enumerations.py`. ⚠ **Nobody
checking the number would have caught it, because the number was fine.**

⚠ **The fixture is CORRECT and is not changed.** Seeding two rows for one accession is exactly what
makes rows and accessions differ, which is what lets CI prove the instrument reports them separately.
**The test was right; the report was wrong.** ⚠ **The fix is not to the fixture, and no script needs a
change** — both instruments were correct.

### 1.2 ⚠⚠ Code 8 — ACCEPTED, on Code's argument against the Planner's

The Planner proposed Code stays at **7**, on the ground that the four earlier defects were caught
before reaching a reading. **Code argued it up, and the argument is correct:** this one reached **two
documents and a commit message**, and was caught only by **cross-reading two of Code's own documents**
— a different class from an instrument catching its author before publication.

⚠ **Declining the flattering count when the Planner offered it is credited**, and it is the second
time today Code refused the easier record — the first being the refusal to whitelist a citation to
turn a red invariant green.

**The close-out states: Code 8 · Planner 15.**

---

## 2. TASK O — the close-out. Everything from the prior orders §2, plus these.

`docs/CLOSEOUT-2026-09-17.md`, written by **Code, from the artifacts.** True calendar date:
**2026-09-17.**

**Additions to the prior orders' eleven items:**

**A. The root cause, in CODE'S wording, not the Planner's.** Code's formulation is better and is
adopted:

> ⚠⚠ **A count stated without the population it counts over.**

**Three instances, both parties, one day:**

| instance | party |
|---|---|
| populations conflated — the cohort treated as a subset of the census | **Planner 12, 15** |
| **a fixture conflated with production** | **Code 8** |
| rows conflated with accessions — the framing that surfaced it | the family they share |

⚠ **Stated ONCE, in those terms.**

**B. ⚠ The guard that would actually have caught this one.** Reporting **rows and accessions
separately would NOT have caught it — both numbers were right.** The rule that would have is:

> ⚠⚠ **Every count names its SOURCE — production read, artifact, or fixture — and a number from a
> test fixture never appears in a report except as a statement about the test.**

**This is carried into the next session's prework as a sixth standing guard.**

**C. TASK N's outcome**, per §1 above: E1 right, the boundary kept, `F-082` untouched, no integer
spent, MUC16's count statable as one with its key.

**D. The corroboration**, stated as corroboration: **`C4`'s `mucin = 3`** and **`E2`'s three
pending** are the same three accessions — `Q685J3`, `Q8WXI7`, `Q9UKN1` — from **two independent
readings.** ⚠ **Evidence toward `F-082` (b), never an answer.** (b) stays **OPEN**; closing it needs
`Q685J3` and `Q9UKN1` looked at directly.

---

## 3. TASK P — merge PR #332

**Sequence, unchanged:** close-out committed → **CI green** → **merge.**

⚠ **Why the close-out goes first, stated once:** the close-out is the document the **next session
grounds on.** A merge whose branch carries four log entries, five artifacts and four instruments
**without the narrative tying them together** is a smaller version of the same base-commit trap that
produced two grounding errors this morning — **the state is there and the interpretation is not.**

**Three confirmations at merge time, none of them blocking:**

1. ⚠ **The merge commit's sha is named in the NEXT session's first report.** The prework says the base
   is *"the #332 merge commit"* precisely because the Planner cannot know it yet.
2. **`RESERVED.md` on `main` after the merge reads `D-169` · `F-083` · `A-032`.** ⚠ **TASK N spent
   nothing, so those pointers are unmoved** — if they have moved, say why before merging.
3. ⚠ **The untracked `_tmp_c1_*` / `_tmp_c2_*` helpers do NOT land.** Explicit paths throughout, as
   all day.

---

## 4. Not authorised

| not authorised | why |
|---|---|
| **Any tunnel** | Two exist for 2026-09-17, both fully evidenced. The cohort-account query is **next sitting's**. |
| **Changing the enumerations fixture** | ⚠ §1.1 — **it is correct and it is doing its job.** |
| **Amending `F-082`** | ⚠ §1 — no amendment is required. |
| **T1 / T2 / T3 · `A-032` step 1 · Phase 2 · Phase 3** | Next sitting, under their own conditions. |
| **`D-169` / `D-170`** | Owed to `SPEC-A-032` §2.6 / §3.7, after `A-032` step 1's result. |
| **Any change to the mucin copy, any label, any flag** | ⚠ Owner's call — *"Rental is closed (pod Terminated)"* beside three enqueued `pending` rows. **The tension is in the sentence, not the flag.** |
| **Editing SPEC v2's body** | The eighth outcome is **recorded as an amendment**, not edited in. |
| Re-running or re-reading any of the five artifacts | ⚠ **Never deleted, never rewritten.** |
| `RESERVED.md`'s four stale rows | ⚠ **Not struck** without checking the `re.search` pins. |
| **Any deploy** | Nothing today is deployable. |

---

## 5. What "done" looks like

- **`docs/CLOSEOUT-2026-09-17.md`** written from the artifacts, carrying the prior orders' eleven
  items **plus §2's A–D**, with the true date and **Code 8 · Planner 15.**
- **CI green**, then **PR #332 merged**, in that order.
- ⚠ **The next sitting grounds on the merge commit**, not on `1e67954`.
- The prework's standing guards carry **six** items, the sixth being §2 B.
