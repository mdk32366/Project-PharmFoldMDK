# REPORT — Code → Planner — 2026-09-17 · `SPEC-PDB-coverage-census-step1-tranches.md` read; **no new orders found**; two population figures do not reconcile

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Written:** 2026-09-17, **15:4x PDT**. **Branch:** `d167-r1r4-population-read`, PR #332, head `a9e8f50`.
**Read:** `SPEC-PDB-coverage-census-step1-tranches.md` (delivered to `Downloads` 15:32 PDT).

> ⚠ **Nothing was built from this document.** It states in its own §0/§Status that it is a
> **pre-registration** that **authorises nothing on its own**, and that its work runs **next sitting**
> alongside `A-032` step 1 — which the TASK D orders **deferred**. **No T0 code was written.**
> **No network read was made. No database contact.**

---

## 1. What arrived — a SPEC, not orders

**The Planner's latest delivery is a specification, and Code read it as one.** There is **no new orders
file** in `Downloads`. The most recent orders remain
`ORDERS-Code-2026-09-17-TASK-D-coverage-report.md`, which is **complete** (`a9e8f50`, CI green).

⚠ **So the correct state is: nothing is authorised right now.** The spec's T0 is *"tests first, offline
fixtures, no network"* — cheap and attractive — but it is **explicitly next sitting's work**, and Code
does not start it on the strength of a document that says it authorises nothing.

---

## 2. ⚠⚠ Two population figures in the spec do not reconcile — and one is `F-082`'s conflation again

### 2.1 The overlap, **re-derived** rather than quoted

`F-082` §4 requires it: *"the '75 overlap' figure rests on the same conflation. Nothing cites 75 as a
measured overlap without re-deriving it."* **So Code re-derived it, offline, from the committed files:**

| quantity | measured |
|---|---|
| cohort accessions (`data/cohort_82_accessions.txt`, `ACCESSION SYMBOL`, comments skipped) | **82** distinct |
| census accessions (`data/census/census_manifest.v7.csv`, column `census_accession`) | **3,467** distinct |
| **cohort ∩ census** | **75** |
| **cohort NOT in the census** | **7** — `P51801`, `Q16880`, `Q6UXF1`, `Q6ZNA5`, `Q7Z5N4`, `Q8N4M1`, `Q9UJA9` |
| **census NOT in the cohort** | **3,392** |
| **union — distinct proteins across both populations** | **3,474** |

⚠ **The 75 is confirmed, and now it is a measurement with its method named rather than an inherited
number.** The seven cohort-only accessions are named because *"75 of 82"* is the half of the statement
that usually travels; the other half is that **7 cohort targets are not census members at all.**

### 2.2 ⚠⚠ §4's "the remaining 3,385" assumes the 82 are a subset of the 3,467. They are not.

**`3,385 = 3,467 − 82`.** That subtraction is only valid if every cohort accession is a census
accession. **Measured: only 75 are.**

- After T1 reads the 82, the census accessions **not yet read** number **3,392**, not 3,385.
- The **distinct proteins** across T1 ∪ census is **3,474**, not 3,467.
- ⚠ **This is exactly the shape `F-082` recorded** — the cohort and the census treated as one
  population when they overlap partially. It is arithmetically small (7) and structurally the same
  error, **inside the document whose §1 forbids a breakdown that does not reconcile with its
  population.**

### 2.3 ⚠ §2's T3 row sums to the whole census, not to a remainder

T3 is described as **"remainder"**, but its stated tranches — **1,307 + 535 + 517 + 332 + 776 = 3,467**
(Code's count from the manifest, which matches) — are the **entire** census, including T2's 300 and
T1's 75 overlapping accessions.

**So T3 is specified two ways at once:** *"the balance of 3,467"* and *"the full per-tranche
population."* ⚠ Code **cannot** compute the true balance yet, for a reason that is itself worth stating:
**the v2 sample of 300 does not exist.** It is drawn in v2 Stage 0, so T3's size is **not computable
until T2's population is defined**, and any number for it today would be a guess.

**Neither §2.2 nor §2.3 is a defect in the science.** Both are the kind of arithmetic that decides
whether the seven outcomes *"sum to 3,467"* — which §1 makes a hard requirement and §4 item 3 makes a
stop condition. ⚠ **A pipeline built to the current wording would fail its own sum check.**

---

## 3. What Code did NOT do, and why

| not done | why |
|---|---|
| T0's tests or script | ⚠ The spec authorises nothing; the orders that would point at it do not exist yet |
| any SIFTS / PDBe read | no network read is authorised, and T0 is offline-only in any case |
| reserving an `F-` or `D-` integer | ⚠ §8: integers are taken **at write time**, in the commit that spends them. `RESERVED.md` reads `D-169` · **`F-083`** · `A-032` |
| touching `A-032` step 1 | deferred by the TASK D orders |

---

## 4. Code's reading of the spec, where it bears on work already done

Stated because these are the places the spec and today's record touch, not as a review of the science:

1. ⚠ **§5 items 1, 2, 4, 5, 6 and 9 are the instrument rules today's two instruments already carry** —
   no count from a list length, every category present at zero, capped lists labelled, **ASCII asserted
   on the printed bytes**, write-once with sha256, and A-017 discrimination. **The coverage report
   (`2cd1c16`) failed CI on exactly item 2** — a branch that vanished at zero — so the rule has a live
   instance from today to point at.
2. **§1's category list has the property `C4` needed:** `accession_unresolved` and `span_unknown` are
   **never folded into `no_pdb_entry`**. ⚠ That is the same rule that kept `mucin` its own `C4` branch,
   and the spec states it better than the TASK D orders did.
3. ⚠ **§7's second limit is the one that matters for v2's wording:** deposited structures are *"models
   fit to experimental data … not ground truth."* The v2 proposal's phrase **"the fair judge"** sits
   close to promoting them, and the proposal is the owner's document — **flagged, not edited.**

---

## 5. What Code asks the Planner for

1. **Correct §2.3 and §4's `3,385`**, or state that T1's 82 and the census are read as **overlapping
   populations** with the sum stated per population rather than once. ⚠ **Code will not reconcile this
   silently at build time** — it changes what the sum check means.
2. **Say whether T3's population is the full per-tranche census or the balance after T1/T2**, noting
   that the balance is **not computable until the 300 are drawn**.
3. **Issue the orders file** if T0 is to be built, or confirm the day ends here. ⚠ Code's read is that
   **the day ends here**: R1–R4 reported, `D-168` / `F-081` / `F-082` written, TASK D delivered and
   green, and the remaining work is blocked on **AMENDMENT 2** (still undelivered) and on next
   sitting's orders.
