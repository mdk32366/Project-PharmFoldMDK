# FINDING — Code → Planner — 2026-09-17 · R4 reads 2 of 3: MUC16 has no complete run-1 row of any kind

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Session:** **2026-09-17, America/Los_Angeles (PDT)**. Read taken **2026-09-17T20:52:25Z**.
**Governs:** `ORDERS-Code-2026-09-17-R1-R4.md` §5.2 · `ORDERS-Code-2026-09-17-AMENDMENT-1-identity-split.md`
**Status:** ⚠ **STOPPED at the reading, per ORDERS §5.2.** Nothing was re-run, nothing reconciled, no
second read taken, and `r1r4_read.json` was neither deleted nor rewritten. **The Planner rules.**

⚠ **This document spends no integer.** It is a finding *report*, not a `### F-NNN` entry. `docs/RESERVED.md`
still reads `D-168` · `F-081` · `A-032`, and `F-081` is already spoken for by the run-label carry
(AMENDMENT 1 §8 item 1). **The Planner assigns the number.**

---

## 1. The reading, with its provenance

| | |
|---|---|
| script | `scripts/d167_population_read.py` at commit **`00badb9`**, `tracked_files_clean: true` |
| target | `127.0.0.1:16391/pharmfoldmdk` as `pharmfoldmdk-app` → role `schema_admin` |
| identity | marker `kyzl60xz9zyrpj9g`, `current_database pharmfoldmdk`, `transaction_read_only: on` |
| evidence | `data/control/d167/population_read/r1r4_read.json`, sha256 **`aff8159330cbd280b8cd0905c968a8b9d18f4188e855e1434d13409fe8e15935`** — printed by the read, re-derived on disk after the tunnel closed, protected by name in `.gitattributes` |
| tunnel | one, bound by cluster name, remote corroborated against `fly mpg status` Direct IP `fdaa:62:76d9:0:1::9`, exactly one listener, **closed**; 0 listeners after |
| ⚠ who ran it | the orders say *"owner at the keyboard"*; **the owner directed Code to run it** in-session. Recorded in `r1-tunnel-open.txt` as a departure, not smoothed. |

| reading | expected | measured | |
|---|---|---|---|
| **R1** | 72 | **72** | MET — the list is **complete at 72 shown**, not capped; every group holds exactly 2 rows |
| **R2** | 72 of 72 | **72 of 72** | MET |
| **R3** | 0 | **0** | MET |
| **R4** | 3 of 3 | **2** | ⚠ **NOT MET** |

---

## 2. ⚠⚠ R3 = 0 is a measurement, not a predicate artifact — AMENDMENT 1 §2 answered

The `(absent)` run label reads **whole_protein 0 · tile 0 · partial_tile_keys 0**.

- **The STOP branch did not fire.** No unlabelled complete whole-protein row exists, so `R3 = 0` cannot be
  the instrument reporting zero because it cannot see.
- **The carry branch is empty too.** So the run-label blind spot Code found in source
  (`core/hold48.py` `emit_tile_jobs` writes no `run` key) is **real in the code and has no instance in the
  database today.** ⚠ It remains a latent defect for the *next* tile emission, which is why AMENDMENT 1
  §8 item 1 carries it regardless.

---

## 3. The miss, exactly

`R4` asks, per accession: **no complete tranche-0 row**, and **exactly one complete census row** at the
whole-protein identity (the key ruled correct in `RULING-Owner-2026-09-17` §6).

| accession | tranche0 complete | census whole complete | census tile complete | untagged complete | R4 |
|---|---|---|---|---|---|
| `P11717` IGF2R | 0 | **1** | 2 | 0 | ✅ as pre-registered |
| `Q9NYQ8` FAT2 | 0 | **1** | 3 | 0 | ✅ as pre-registered |
| ⚠ **`Q8WXI7` MUC16** | 0 | **0** | **0** | 0 | ❌ **no complete run-1 row of any kind** |

**MUC16 satisfies R4's first clause and fails its second.** It is not a case of too many rows; it is a
case of **none**.

⚠ **Q8WXI7 appears in none of the 72 R1 groups** (checked against the complete, uncapped group list).

---

## 4. What the same read also measured, stated because it bounds the question

| quantity | value |
|---|---|
| complete run-1 rows, whole-protein identity | **3,542** |
| complete run-1 rows, tile identity | **106** |
| complete **run-2** rows, whole-protein identity | **1,976** |
| complete run-1 rows, tranche 0 (cohort) | **79** |
| complete run-1 rows with a NULL tranche | **0** |
| R1 groups by row count | `{2: 72}` — no group holds 3 or more |

⚠ **79 tranche-0 complete rows out of 82** is consistent with the three cohort-side gaps the Phase E
analysis named (`P11717` failed; `Q8WXI7`, `Q9NYQ8` not folded). **Consistent is not proven** — this read
did not enumerate which three are missing.

---

## 5. ⚠ The pre-registration's premise, against the committed record

**A9.2 wrote R4 as:** *"the three named overlap exceptions each have no complete tranche-0 row and exactly
one complete census row."* The **second clause is measured false for MUC16.**

**The committed record already says MUC16 is not folded — on the census side as well:**

| source | says |
|---|---|
| `docs/decisions.md:2860` | the four `none` structure rows are the **3 mucins** (`Q685J3`, `Q8WXI7`, `Q9UKN1` — `structure_kind: mucin`, **`folded: false`**) and `P55073`/DIO3 |
| `docs/decisions.md:3041` | on the live surface `Q8WXI7` (MUC16) **"still wears NOT FOLDED"**, while `Q9NYQ8` renders *assembled (provisional)* |
| `docs/decisions.md:6883` | the **3** mucins *"stay `out_of_class`"* |
| `data/census/census_manifest.v7.csv` | `Q8WXI7` **is** in the census: tranche **5**, rental, span **14,451 aa** |

⚠ **So a census row was planned for MUC16 and no completed fold was ever recorded for it.** Whether that
makes R4's expectation **mis-specified** (the same shape as Phase E's expectation 3) or makes the *absence*
itself the finding is **the Planner's ruling, and Code does not choose.**

---

## 6. ⚠ What this read did NOT establish — the limits, named

1. **Every reading counts `status = 'complete'` only.** ⚠ Whether MUC16 has a census row in **another**
   status (`pending`, `failed`, anything else) is **not established by this read**. F-078 recorded five
   non-complete run-1 rows — 2 failed (`P11717`, `P55073`) and 3 pending — and **this read did not
   enumerate which accessions the three pending are.** MUC16 may or may not be among them. **Code asserts
   nothing.**
2. **Nothing about `protein_analyses` rows without a job**, or about artifacts on the volume.
3. **Whether R1's 72 is disturbed by §5.** The count reads 72 and each group holds exactly 2 rows. The
   Phase E derivation reached 72 as `75 overlap − 3 named exceptions`, and MUC16 is excluded from the
   pairs under either reading of its census state — but **whether the derivation's total survives the
   falsification of its premise is a ruling, not a measurement**, and it is the Planner's.
4. **Nothing about the other two mucins** (`Q685J3`, `Q9UKN1`) — they are not in R4's set, and no reading
   today touched them. ⚠ If MUC16's state is a class property of mucins rather than a fact about one
   protein, **that is a wider question than R4** and it is unmeasured.

---

## 7. Rulings owed (Planner)

1. **R4's verdict.** Options, and Code does not choose:
   - **(a)** R4's expectation was **mis-specified** for MUC16 — it assumed a completed census fold the
     committed record says never existed. Record it as such (the Phase E expectation-3 shape) and treat
     R1–R3 as the session's clean result. **Needs no further read.**
   - **(b)** The **absence itself is the finding** — a census row was planned at tranche 5 and no complete
     fold exists — and it is recorded against the census accounting rather than against R4's wording.
   - **(c)** Neither is decidable without §6 item 1, in which case a **second read-only read** is ordered,
     pre-registered again, to enumerate MUC16's rows **by status** and to name the three pending
     accessions. ⚠ That is a new tunnel and a new sitting; **today's tunnel is closed.**
2. **Whether R1's 72 stands** on a derivation whose premise §5 falsifies for one of three terms.
3. **The number.** This report spends no integer; `F-081` is already spoken for by the run-label carry.
4. **Whether Phase 1 opens** next sitting. ⚠ `ORDERS-RECONSTRUCTION-2026-09-17-feature-coverage.md` **has
   now been delivered** and is committed at `docs/`, so the delivery block is cleared — but **the R4 miss
   stopped the work** and the tunnel is closed, so **no part of Phase 1 was built or read today.**

---

## 8. State at close

- **Branch** `d167-r1r4-population-read`, PR **#332**, head **`f0be03a`**. CI green on `e4a300b`
  (`test` 2,732 passed · `postgres` 58 passed, 1 skipped); the read landed after it.
- **Evidence committed:** `r1-tunnel-open.txt` · `r2-read-console.txt` · `r3-tunnel-closed.txt` ·
  `r1r4_read.json` (+ `.gitattributes` by name; the EOL guard passes 37) · `t1`–`t6` test and CI logs.
- **Credential scan** clean on every file: literal password absent, 0 credentialed URLs.
- **All four governing documents are now committed to `docs/`**, so `F-081`'s delivery question has **no
  open instance**: the two orders, the two rulings, and the reconstruction.
- ⚠ **Untouched, unread, unruled:** the untracked `_tmp_c1_*` / `_tmp_c2_*` helpers. Every `git add` named
  explicit paths.
