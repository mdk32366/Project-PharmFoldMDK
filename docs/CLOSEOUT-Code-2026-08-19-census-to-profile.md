# CLOSEOUT — Code — 2026-08-19 — from "nothing but folds" to a ruled, surfaced structural profile

> ⚠ `CLOSEOUT-2026-08-19.md` is the Planner's and covers a different arc. This is Code's, named
> for its subject so the two do not collide.
> **Scope:** merges `#143` → `#155`, `main` `b7ecc2a` → the tip of this branch. Releases v72 → v81.

---

## §1 — What now exists that did not this morning

**A census protein has a number, and about half of them are refused one.**

| | |
|---|---|
| `data/census/census_features.v1.jsonl` | 2,690 rows, hash-pinned, protected from git's checkout filter |
| migration `0010` | unique constraint · `extraction_outcome` · `ingest_markers` |
| `protein_features` in production | **2,770 rows** — 80 cohort + 2,690 census |
| `core/structural_profile.py` | the model applied from **13 recovered parameters**, no fitter import |
| `/census/:id` | the profile on the page that shows the 3D structure |
| `/census` | *what we found* · *how to read a profile* · a **status** column |

**The headline measurement:** **1,397 carry a profile, 1,293 are refused** — 1,225 out of range, 58
span-below-floor, 10 incomplete. ⚠⚠ **The refusals are the finding.** The census is systematically
less confidently modelled than the cohort (median `mean_plddt_ecd` **57.0 vs 72.4**), and **the two
features carrying most of the model's weight are the two that leave its range first.**

⚠ **The values that survive sit in a band 0.19 wide**, essentially where the cohort's own sit. *This
axis does not separate targets by much*, and that is now stated on the page rather than inferable.

---

## §2 — The governance work, and why it took as long as the code

**`D-079` amendment 1 was ruled** (amendment 2), **implemented** (amendment 3), **corrected**
(amendment 4), and **audited** (amendment 5). ⚠ Each is a sub-entry; **no integer was consumed by
any of them.**

**⚠⚠ THE MEASUREMENT CAME BACK AS A THIRD OUTCOME.** Ruling 3 pre-registered a disjunction — *most
inside* or *most outside*. It is **46.7% refused on the strict bar**, so **ruling 1 and ruling 3 are
both operative, on different halves of one population.** Recorded as a third state rather than
rounded to the nearer branch.

**Ruling 8 fixed the bar at the cohort's observed support**, and named why not the other two: `±3 sd`
rests on a standard deviation `F-049 amendment 1` proves is **not recoverable**; `p05–p95` **fires
inside the training support.** ⚠ All three counts stay recorded so the dial is visible.

**Entries landed:** `F-021` (written, integer spent) · `F-052` · `F-047 am 2` · `F-049 am 2` ·
`D-079 am 2/3/4/5`. **Invariant closed at 151 defined / 14 reserved / 165 cited.**

---

## §3 — ⚠⚠ What went wrong, and it is the most useful section here

**Three failures on the production host, all mine, all the same shape:** *a convention that existed,
was documented, and was obeyed by every caller except the newest one.* Recorded as **`F-052`**.

1. a **transitive** `scripts/` import — my test checked direct imports only
2. an engine built from a **raw `DATABASE_URL`** — five callers used the helper; mine was the sixth
3. `.gitattributes` scoped to `docs/` while a pinned artifact landed under `data/`

⚠ **In two of the three I had written a test for it and the test passed on the broken code.**

**⚠⚠ AND EACH REMEDY WAS, ON ITS FIRST ATTEMPT, SCOPED THE SAME WAY THE DEFECT WAS.** A scan
reporting 3 files where deriving found 6. A test checking direct imports against a transitive
defect. **Five separate tests that reddened on correct code** — banning a word that appeared in the
*denial*, or scanning prose that could not tell *"I am one"* from *"that one is one"*.

**The fix that worked every time: derive the set rather than enumerate it, and put meaning in a
field rather than in a string.**

⚠ **Two claimed guards turned out to be fiction.** `D-079` dec 1 asserted a census→scorer import bar
*"asserted by test and proven by revert"* — **the only such test ran the other direction.** And the
no-refit clause was true **by packaging**, not by any check. Both are now real.

⚠ **Four stale claims, all in one page family**, all true when written, **none caught by a test** —
the census thesis sentence, its disclaimer, the constants-file header, and one of my own assertions
from the previous day.

---

## §4 — The residuals, named rather than closed

- ⚠⚠ **1,397 numbers in a 0.19-wide band.** Every guard is in place and **none stops a reader
  opening two tabs and subtracting.** Two mitigations are recorded as *identified and not taken* —
  band position without digits, and a gated reveal.
- ⚠ **`F-021` clause 1 is contained, not repaired.** `--load` is still a pure insert; the database
  refuses it. **A reader learns the wrong rule from the code and finds out at the constraint.**
- ⚠ **`load_features()` still carries the latest-run default** as dead code, reachable by direct
  call, and the newest run is now id=5 — a `sensitivity` run.
- ⚠ **Clause A of `D-079` dec 1 can never be enforced by a test.** *No census statistic as evidence
  in any artifact, deck, or briefing* governs an **act**. The audit covers version-controlled files;
  a deck shown and never committed is outside every instrument this project can build.
- ⚠ **Seven pre-existing `CensusView` CSS classes have no rule.** Observed, not fixed.

---

## §5 — What is ready for the next session

**Unblocked and waiting on a decision, not on work:**

- **The rental tranche.** ⚠⚠ `JA` re-keyed it and **the ceiling climb buys nothing**: the
  441–629 band is empty — 0 targets, 0 positives, where `FC` said 13 and 3. **Two targets remain
  unfolded, at 4,030 and 14,451 residues.** That is a tiling question, not a ceiling question.
- **Confidence.** `F-051` establishes `membrane_proximal_plddt` alone carries **32.2%** of
  attribution against `mean_plddt_ecd`'s **6.4%** — *"the two confidence features" is one feature* —
  and today's out-of-range measurement **confirms ruling 4's prediction by measurement**: the
  dominant feature is the one that leaves the fitted range first. ⚠ `D-075`'s `geom_proxy` ablation
  is the instrument that separates the two readings, and `F-017` already records it firing.
- **Tranche 5's 776 rows** are released from the design gate (`D-095` ruled) and held by rental
  spend alone.

⚠ **Nothing is blocked on Code.** Every branch is merged; production is at v81 and answering.
