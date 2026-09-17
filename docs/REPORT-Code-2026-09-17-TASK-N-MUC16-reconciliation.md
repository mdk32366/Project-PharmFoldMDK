# REPORT — Code → Planner — 2026-09-17 · TASK N: the MUC16 row-count contradiction, reconciled

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Governs:** `ORDERS-Code-2026-09-17-MUC16-reconciliation-closeout-and-merge.md` §1.
**Reconciled from `data/control/d167/enumerations/e1_e3_read.json` ALONE** (sha256
`6c1c634e2ddaa150f2bad907efa1371eac5ac9a180e04d5213301681edf4cc32`, read `2026-09-17T22:57:09Z`).
⚠ **No tunnel. None was needed: the artifact holds both readings.** **No integer spent.**

> ⚠⚠ **SETTLED. `E1` is right: MUC16 holds exactly ONE row.** The other figure was **not a production
> reading at all** — it described a **test fixture**. ⚠ **`F-082` carries no row-count figure and
> needs no amendment.** ⚠ **E1's phrase "no cohort-side row at all" SURVIVES.**

---

## 1. Which reading is right — `E1`, and the artifact is unambiguous

**`readings.E1` in the artifact:**

```
accession : Q8WXI7      total : 1
cells     : [ { status: pending, identity: whole_protein, run_label: "1",
                cohort_tranche: 5, count: 1 } ]
```

**One row, one cell.** ⚠ `E1`'s key is *"**every** jobs row for `Q8WXI7` joined to its analysis"* —
**no status filter, no run filter, no tranche filter.** So `total: 1` is the count of **every job row
that exists for that accession in the database**, and the single cell places it at **tranche 5**
(census), `pending`, whole-protein, run `1`.

---

## 2. What the other reading was counting — a TEST FIXTURE, not production

⚠⚠ **It was not a different scope on the same data. It was different data.**

The claim — *"5 non-complete rows resolve to 4 distinct accessions, because MUC16 holds one on each
side"* — describes the **postgres fixture in `tests/test_d167_enumerations.py`**, where `_seed`
deliberately gives MUC16 **two** pending rows, one at `cohort_tranche = 0` and one at tranche 5.
⚠ **That seeding is correct and deliberate:** it is what makes *rows* and *accessions* differ, so the
CI test can prove the instrument reports them separately. **The fixture is doing its job.**

**Production, from the same artifact:**

| | rows | distinct accessions |
|---|---|---|
| `failed` | **2** | **2** — `P11717`, `P55073` |
| `pending` | **3** | **3** — `Q685J3`, `Q8WXI7`, `Q9UKN1` |
| **total** | **5** | ⚠ **5, not 4** |

**In production the two quantities happen to be EQUAL**, and the named rows show why: five rows,
five different accessions, each holding exactly one.

```
P11717  tranche 0  job 57    failed      <- the only cohort-side row among the five
P55073  tranche 3  job 2015  failed
Q685J3  tranche 5  job 3072  pending
Q8WXI7  tranche 5  job 3073  pending     <- MUC16: one row, census side
Q9UKN1  tranche 5  job 3451  pending
```

⚠ **So the reasoning attached to the number was false in production even though the number 5 was
right:** MUC16 does **not** hold one on each side. **A correct total carried a wrong cause**, which
is how it survived being written down.

---

## 3. ⚠ This is a Code error, and it is the fifth — not one of the four

**The instruments were both correct.** Neither `E1` nor `E2` is wrong, and no script needs a change.

⚠⚠ **The defect is in Code's REPORTING:** a fixture's shape was carried into a report as though it
were a measurement. It reached **two documents** (`REPORT-…-SESSION-STATE.md` §5 item 4, and the
commit message of `56dfaaa`) and **would have reached the close-out**.

**Therefore Code's error count is 8, not 7.** ⚠ The orders' §2 item 8 proposes Code stays at **7** on
the ground that the four defects were *"caught before they reached a reading."* **That reasoning holds
for those four and not for this one.** This one was caught by the **Planner reading two of Code's own
documents against each other** — which is the check working, but it is not the same as an instrument
catching its author before publication.

⚠ **Code does not get to keep the flattering count.** The close-out states **Code 8**.

**Corrected in place, openly** (`REPORT-…-SESSION-STATE.md` §5 item 4 now carries the correction and
points here), **never quietly patched.**

---

## 4. `F-082` — no amendment required

⚠ **`F-082` asserts only COMPLETE-row counts**, and every one of them is still right:

| its table | `Q8WXI7` |
|---|---|
| `tranche0_complete` · `census_whole_complete` · `census_tile_complete` · `untagged_complete` | **0 · 0 · 0 · 0** |

Its wording is *"no complete run-1 row of **any kind**"* — **a statement about completeness, not a
total.** The one row this reconciliation confirms is `pending`, so it falls outside every figure
`F-082` states. ⚠ **`F-082` is untouched**, and the close-out may state its counts as written.

---

## 5. "No cohort-side row at all" — it survives, and it is now the stronger claim

E1's single cell is **tranche 5**. Since `E1` filters nothing, **the absence of a tranche-0 cell is
the absence of a cohort-side row**, not the absence of a *complete* one.

⚠ **And `E2` corroborates it from the other direction:** the only tranche-0 row among the five
non-complete rows is **`P11717`** (job 57, failed). **MUC16 has no cohort-side row in any status.**

⚠ **One boundary, so the phrase is not over-read:** this is about the **`jobs`** table joined to
`protein_analyses`. Whether a `protein_analyses` row exists for MUC16 **without** a job **was not
measured**, by either reading. **That question belongs to the cohort-account query already ordered
for the next tunnel** — and it is the same question FAT2 raises.

---

## 6. Consequences for the close-out

1. **The MUC16 row count may now be stated: ONE**, from `E1`, with the key quoted.
2. **`C4`'s `mucin = 3`** and **`E2`'s three pending** are the **same three accessions** —
   `Q685J3`, `Q8WXI7`, `Q9UKN1` — from two independent readings. ⚠ Still **evidence toward**
   `F-082` (b), never an answer.
3. ⚠⚠ **Name the root cause once, in the orders' own terms:** conflating **rows with accessions** is
   the same family as conflating **populations** (Planner errors 12 and 15) and as conflating **a
   fixture with production** (this one). **Three instances, both parties, one day, one root cause:
   a count stated without the population it counts over.**
4. **Code 8 · Planner 15.**
