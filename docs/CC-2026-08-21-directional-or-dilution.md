# `YA` / `YB` / `YC` — is the pooling DIRECTIONAL or DILUTION?

> ⚠⚠ **READ-ONLY.** No fold, no fit, no refit, no new ranking run, no new supplier, no ingest,
> no correlation coefficient, no prevalence figure.
> Produced under `ORDERS-Code-directional-or-dilution.md` (`9c5b3d52…`, verified).
> Answers `P-001 amendment 1` §4, pre-registered and landed **before** this ran.

---

## §1 — `YA1` — ⚠⚠ THE POWER, ABOVE THE NUMBERS

**n = 4, out of 82.** ⚠ **Four rows cannot establish a direction.**

`D-075` decision 0 established that **at n = 12 a median is not a stable anchor.** At **four**,
nothing is: no dispersion statistic, no rank correlation, no test of systematic position. ⚠⚠ **Any
"systematically high" or "systematically low" read off four rows is a description of four rows and
not a property of the population they come from.**

**What four rows CAN establish:** that a specific, named target sits at a specific position — a fact
about that target, reportable and checkable. ⚠ **What they CANNOT establish:** that the four share a
direction, that the direction generalises, or that its absence means dilution rather than
insufficient data.

**⚠⚠ THE ANSWER, STATED AT THE TOP: NEITHER BRANCH IS ESTABLISHED. The honest outcome is the third
one — UNDERPOWERED.** §4 of the order permits it and `P-001 amendment 1` §4 will carry it.
⚠ **The Planner's recorded expectation was `SCATTERED`, and more honestly *underpowered*. That is
what the data supports** — recorded here so it is visible that the expectation and the result agree,
which is a weaker form of evidence than disagreement would have been.

---

## §2 — `YA3` — does `EGFR` belong? ⚠ DECIDED BEFORE LOOKING, AND THE ANSWER TURNS ON OUR OWN FILE

**The order's exclusion argument:** *`EGFR` in NSCLC is defined by MUTATION, not surface abundance,
and this is an IHC arm.*

⚠⚠ **THAT ARGUMENT IS ABOUT AN INDICATION WE DID NOT CURATE.** `data/adc_reference_mapping.csv`
line 69 reads:

> `depatuxizumab mafodotin,,EGFR,P00533,"ABT-414 / Depatux-M; INTELLANCE-1 phase 3, glioblastoma",,clinical`

**Our curated `EGFR` row is GLIOBLASTOMA, not NSCLC**, and the matching HPA category is `glioma`.

**DECISION: `EGFR` is RETAINED. n = 4.** ⚠ Removing a row on a reason that does not apply to it would
be as arbitrary as keeping it for a reason that does not either.

⚠⚠ **AND THE PREMISE THAT WOULD JUSTIFY KEEPING IT IS ALSO UNSOURCED.** Whether EGFR-amplified
glioblastoma is an *IHC-defined* population is a clinical claim, and I have opened no source for it —
`unknown_to_code`, the same bar `XE` applied. **So `EGFR`'s inclusion is a decision made on the file
we hold, not on established biology.**

**⚠ n = 3 IS REPORTED ALONGSIDE THROUGHOUT so nothing depends on this call.** Both were fixed before
any expression number was read.

---

## §3 — `YB` — the four rows, individually, at three bars

**⚠ `YB3` — the comparison populations, named:**

| arm | population | key |
| --- | --- | --- |
| **structural ranking** | **56 scored** of the 82 cohort | `/api/ranking` rows, run `id=2` |
| **expression arm** | **337 pairs over 82 of 82** targets | the `D-053` quasi-H-score grid |

⚠⚠ **The `D-053` grid's own cutoff is `qh ≥ 150`, so ABSENCE FROM THE GRID MEANS BELOW CUTOFF, NOT
NO DATA.** That is bar 3 built into the source, and it must not be read as missingness.

### The four rows

| target | tumour type | structural rank | bar 1 · any detection | bar 2 · any `High` | bar 3 · `qh ≥ 150` |
| --- | --- | --- | --- | --- | --- |
| **`ERBB2`** P04626 | breast | **7 / 56** | ✅ 7/11 | ✅ High 4 | ✅ **154.55** |
| **`NECTIN4`** Q96NY8 | urothelial | **8 / 56** | ✅ 11/12 | ✅ High 3 | ✅ **200.00** |
| **`EGFR`** P00533 | glioma | **3 / 56** | ✅ 11/12 | ✅ High 6 | ✅ **216.67** |
| **`FGFR3`** P22607 | urothelial | **34 / 56** | ✅ 6/11 | ✅ High 2 | ⚠ **no — below cutoff** |

**⚠⚠ THE BARS DO NOT AGREE WITH EACH OTHER, AND THAT IS THE POINT OF REPORTING THREE.**
`FGFR3` clears bars 1 and 2 and fails bar 3. **At one bar it is present; at another it is absent** —
and `DB1` already measured these bars moving an all-20 figure **785 → 57 → 35**, a factor of 22.
⚠ *A single bar here would have been a dial wearing the costume of a measurement.*

### What the positions show — and do not

⚠ **Three of four sit high in the structural ranking** (3rd, 7th, 8th of 56); **one sits low** (34th).
**At n = 4 that is not a direction.** ⚠⚠ **One row out of four is 25% of the sample, and a single
target moving would invert the reading** — which is the whole of `YA1`'s point.

⚠ **At n = 3 (`EGFR` excluded) the picture is 7th, 8th, 34th** — *the same instability, from a
smaller sample.*

**⚠⚠ NO CORRELATION COEFFICIENT IS COMPUTED**, per `YB2` and §4. **Four points would produce a number
with a real number's shape and no content.**

---

## §4 — `YC` — is the dilution visible in the panel itself? ⚠ SUGGESTIVE, NEVER DEMONSTRATED

**⚠⚠ THIS SECTION IS WEAKER THAN IT LOOKS AND IS LABELLED SO.** `F-043`: panels are **median 11,
max 12**, and 246 of 1,640 rows sit at **n ≤ 4**. ***A panel of ~11 cannot distinguish bimodality
from noise.*** Nothing below is offered as demonstrated.

**The mechanism under test:** a category pooling a 15–20% high-expressing subset with a
low-expressing majority should look **bimodal or bottom-heavy**, not uniform.

| target · category | High | Medium | Low | Not detected | n | shape |
| --- | --- | --- | --- | --- | --- | --- |
| **`ERBB2` · breast** | **4** | 2 | 1 | **4** | 11 | ⚠ **High and Not-detected are the two largest cells, with the middle thin — the shape the mechanism predicts** |
| `NECTIN4` · urothelial | 3 | **7** | 1 | 1 | 12 | ⚠ middle-heavy — **not** the predicted shape |
| `FGFR3` · urothelial | 2 | 1 | 3 | **5** | 11 | bottom-heavy |
| `EGFR` · glioma | **6** | 3 | 2 | 1 | 12 | top-heavy |

**⚠⚠ `ERBB2` in breast is the one row consistent with the mechanism, and it is one row of eleven
patients.** 4 High and 4 Not-detected with 3 in between is what a mixed population would look like —
**and it is also what eleven samples of anything look like when they scatter.** ⚠ **The prediction
and the observation agree here, and that agreement is worth exactly what n = 11 makes it worth.**

⚠ **`NECTIN4` points the other way** — middle-heavy, which the mechanism does not predict — **and it
is reported at the same weight**, because a section that printed only the confirming row would be
the defect this project has an entry for.

---

## §5 — What this does NOT establish

- ⚠⚠ **Not DIRECTIONAL and not SCATTERED. UNDERPOWERED**, which §4 of the order and `P-001`
  amendment 1 §4 both permit as the true third outcome.
- **No correlation, no coefficient, no prevalence figure, no adjusted number.**
- ⚠ **`EGFR`'s inclusion rests on our own curated indication, not on sourced biology.**
- ⚠⚠ **`YC` is suggestive on one row of four and contradicted on another.** It is not evidence of
  dilution; it is a shape that is consistent with dilution and equally consistent with noise.
