# Orders Addendum — 2026-07-27, correcting the intersection measurement

> **⚠ This does NOT displace the D-058 features PR.** That remains the critical path and the
> priority. This addendum is ~15 minutes of measurement, and it is measurement only — **no entry
> is written and no code is committed off the back of it yet.**
> **Report all output verbatim.** Do not summarise, do not interpret, do not act on the numbers.

---

## 1. A Planner error, recorded (D-016)

`intersection_check.py` as handed over **omitted the `disposition` filter.** It computed
`folded ∧ mean_plddt ≥ 50` and labelled the result "the ranking denominator." That is not the
ranking denominator.

`core/manifest.py` partitions all 82 into **`ranked` / `held_out` / `excluded`** — mutually
exclusive and exhaustive (D-024). **`held_out` is boundary-method incomparability** (D-021 §1a):
whole-method targets whose ECD was not sliced from a UniProt topological annotation. D-027 rules
feature 4 **cross-method incomparable** for exactly those targets, and requires that the extractor
*"must not silently compute it as though it were comparable."*

**How the error surfaced, because the mechanism is the point:** the script returned 67, and D-050
records `CoverageLine` correctly showing **67 = `ranked ∧ folded`** at the 79-fold era. Two
different quantities, same value. The collision is what prompted the check that found the missing
filter. **A number that matches a number you already trust is the most dangerous kind of wrong.**

---

## 2. The fix

`disposition` is already in the light list (`app/reads.py:_LIST_META_KEYS`). Change the folded map
to carry it, then partition:

```python
folded = {}
for r in rows:
    gene = r.get("gene")
    if gene:
        folded[gene] = (r.get("mean_plddt"), r.get("disposition"), r.get("held_out"))

def ok(v):
    plddt, disp, _ = v
    return plddt is not None and plddt >= FLOOR and disp == "ranked"

rankable = {g: v for g, v in folded.items() if ok(v)}
```

**Then report, separately and all of them:**

| Report | Definition |
|---|---|
| A | `folded` — total |
| B | `folded ∧ pLDDT < 50` — the floor cost, and as a % |
| C | `folded ∧ disposition == "ranked"` — before the floor |
| D | **`folded ∧ ranked ∧ pLDDT ≥ 50`** — **the real ranking denominator** |
| E | probable positives ∧ D — the provisional fit set, **named** |
| F | probable positives that are `held_out`, **named** — the set the old script silently included |
| G | evidence score ∧ D — D-059's denominator, **named** |
| H | E ∩ G — the D-041 decision-3 head-to-head denominator, **named** |
| I | `needs_literature_check` ∧ D — the owner's live curation headroom |

**B and the percentage supersede D-041 §5's ~24%** regardless of what else changes — that figure
was measured on 42 folds and has never been re-measured.

---

## 3. Second measurement: which targets are unfolded

`GET /api/coverage` — report the three-valued `fold_status` breakdown and **name every target that
is not `folded`.**

**Why it matters:** 82 − 80 = 2, and the two targets known to be unfoldable as single sequences on
any available hardware are **MUC16 (14,451 aa) and FAT2 (4,030 aa)**. If those are the two, **every
foldable target in the cohort is folded and the fold arc is complete.** That is a materially
stronger delivery statement than "80 of 82, 2 remaining" — but **it is an inference until the
endpoint says so**, and it must not be spoken aloud before it is measured.

---

## 4. What NOT to do

- **Do not write `F-002`.** The entry is drafted only after these numbers land, and the owner
  approves it.
- **Do not commit `intersection_check.py`.** It stays untracked until the D-058 features PR is
  merged and green. Then it moves to `scripts/` in its own small PR with tests over the pure set
  arithmetic and the fetch injected — the `scripts/curate_group_b.py` standard, scaled down.
- **Do not act on set membership.** Whether any given target is a Group B positive is an owner
  judgement (D-040 decision 1), unchanged by any of this.
- **Do not adjust the pLDDT floor.** 50 is ruled (D-041 §5). CXCR5 landing at 47.63 — just under —
  is the floor working, not an argument against it.

---

## 5. Back to the critical path

The D-058 features PR is the priority and nothing here changes its scope, its order, or its stop
points. If these measurements would delay the migration or the SASA timing gate, **do the features
work first and these after.**
