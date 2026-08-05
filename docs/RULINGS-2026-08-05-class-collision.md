# RULINGS — 2026-08-05 — The cross-tag accession collision: a SURFY class is a property of the identifier, not of the protein

> **COMMITTED 2026-08-05 with `### D-079` (`docs/README.md`). CITED BY the log, not restated in it —
> where this file and the log differ, THE LOG GOVERNS.** ⚠ This file is provenance for a decision that
> lives in the log; it is not itself authority. Check the `### D-079` header, not a reference to it.

> **Lands in #1's docs-only commit, alongside `AMENDMENT-2026-08-05-D-079-census-key.md`.**
> **Binding before Task 5.** Task 2 and the surface crank are unaffected.
>
> **Found by Code**, checkpoint 4, 2026-08-05, by applying the amendment's own collapse rule to the
> two tags the amendment extended it to. **Verified by the Planner** against
> `membraneome-reconstructed-2026-08-04.csv` (sha256 `5a705cc9…`) on 2026-08-05.

---

## §1 — Two things confirmed, one of them Code's, one of them new to the record

**1. The collapse is exactly four accessions and nothing else** — Code's observation, and it is worth
asserting rather than implying. **2,803 singleton rows + 4 collapsed rows = 2,807.** No fifth
accession absorbs even two source rows. **So the 83-fold HLA weighting is not a worst case among
many; it is the entire deviation from 1:1**, which is what makes the amendment's §2 argument
measurable rather than illustrative.

**2. The three tags are not disjoint under the new key.** Verified:

```
distinct current accessions:  surface 2807 · non_surface 2211 · unclassified 2795
sum of the three: 7813        distinct accessions overall: 7811
accessions under MORE THAN ONE tag: 2
```

| Entry | source acc | current acc | SURFY class | `class_conflict` |
|---|---|---|---|---|
| `CTGE5_HUMAN` | O15320 | **Q96PC5** | `non_surface` | yes |
| `MIA2_HUMAN` | Q96PC5 | **Q96PC5** | `unclassified` | yes |
| `HV304_HUMAN` | P01765 | **P01764** | `non_surface` | yes |
| `HV303_HUMAN` | P01764 | **P01764** | `unclassified` | yes |

**Four rows, two proteins.** ⚠ **The surface class is untouched** — neither accession appears in it.
**2,807 stands and the crank is unaffected.**

---

## §2 — RULING: the collision is a **category**, not a resolution

**Three ways to close this and two of them are forbidden by rules already on the books:**

- ❌ **First-wins** — would place a protein in one of two populations by row order. ⚠ Those two
  populations are precisely the ones **F-016 exists to keep apart**: the unclassified are excluded by
  a *different mechanism* and must not be recruited into F-011's thesis. First-wins is the
  smoothing rule applied to class instead of to accession. Code's read is correct.
- ❌ **Drop** — loses a protein to make a partition tidy.
- ✅ **A fourth tag.**

**Ruled: a protein whose source entries disagree on class has NO SURFY class.** It is ingested once,
tagged **`class_conflict`**, and belongs to **no class denominator**. The `class_conflict` column
already in the CSV is consumed, not recomputed.

**The four denominators, and they reconcile exactly:**

```
surface 2807 · non_surface 2209 · unclassified 2793 · class_conflict 2   =   7811
```

⚠ **Note what changed:** `non_surface` moves 2,211 → **2,209** and `unclassified` 2,795 → **2,793**.
Both figures appear in the amendment and in D-079 v2 and **both are superseded here**. The surface
2,807 is unchanged. **Four denominators, still never summed** — the total above is a reconciliation
check, not a reportable quantity.

---

## §3 — ⚠ The finding underneath it, stated carefully because it is small and tempting

Q96PC5 and P01764 each carry **two SURFY entries that disagree with each other about the protein's
class.** SURFY assigned a class per *identifier*; UniProt has since merged those identifiers; the
disagreement was always there and the merge made it visible.

**So the SURFY class is a property of the identifier, not of the protein.** That is a *measured*
instance of what `RESERVED.md` **A-014** states as an assumption — *an upstream model's negative
class is a prediction, not a fact* — and of F-011's argument that the boundary is a property of the
classifier rather than of target biology.

**Reserve `F-019`** (⚠ F-017 held for the D-075 result, F-018 for the `or "resolved"` default).

**⚠ Over-claim guard, and it binds — this is P-002's exact failure mode arriving early.**

- **n = 2.** It is a **mechanism illustration, not a magnitude.** It says the class *can* be
  identifier-scoped; it says nothing about how often.
- **It is not evidence for F-011's thesis.** F-011 is about *how the negative class is defined*
  (steady-state localization). This is about *how a class assignment is keyed*. **Adjacent, not the
  same** — and P-002's named failure mode is exactly the promotion of a compelling adjacent argument
  into evidence it does not have.
- **It must not be recruited into any count.** Two proteins do not bear on 2,216, on 2,801, or on
  any claim about the size of an excluded class.

---

## §4 — What ships

1. **Ingest consumes `class_conflict`** from the CSV. A collision is tagged, never resolved by
   preference, never dropped.
2. **Four tags, four denominators, each stating its key** (distinct current accession).
3. **Task 5.2's ingest rule is amended:** *"annex and unclassified under their own tags, never
   pooled"* becomes *"annex, unclassified, and class-conflict under their own tags, never pooled."*

| Test | Assertion | Prove it bites by |
|---|---|---|
| `test_the_three_class_tags_are_disjoint_by_census_accession` | No accession carries more than one of `surface` / `non_surface` / `unclassified` | Removing the conflict tag → red **on Q96PC5 and P01764**, not on the majority |
| `test_class_conflict_rows_are_ingested_not_dropped` | Both proteins present, tagged, in no class denominator | Filtering them → red |
| `test_denominators_reconcile_to_distinct_accessions` | 2807 + 2209 + 2793 + 2 == 7811 | Reverting to 2,211 / 2,795 → red |

⚠ **The first test must name the two accessions.** A disjointness test over 7,811 rows would pass
under first-wins, because first-wins produces a disjoint partition. **Disjointness is not the
property at issue; not-resolving-by-preference is.**

---

## §5 — Recorded

**This is F-016's concern arriving through the collapse** — the same shape as F-009 arriving through
a column name, one ruling earlier. ⚠ **Both were created by a Planner ruling that was correct in its
own frame**: keying by current accession is right, and it introduced a collision the identifier key
could not have. **A correct decision produced a new defect, and the defect was found by applying the
decision's own rule to the sets the decision extended it to.**

That is worth naming as a pattern: **the check on a ruling is to apply it everywhere it claims to
apply and see what it breaks** — not to re-examine the reasoning that produced it.
