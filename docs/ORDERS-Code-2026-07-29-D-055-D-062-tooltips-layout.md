# Orders for Code — D-055 + D-062 amendments: in-situ tooltips, two-column scorer, glossary expansion

> **⚠ SUPERSEDES `ORDERS-Code-2026-07-29-D-062-amendment-layout.md`.** Banner that file in place;
> do not delete it.
> **Scope:** `ui/src/` — `ScorerView.jsx`, `Term.jsx`, the glossary source, `Glossary.jsx`, tests.
> **NOT in this PR:** `app/`, routes, `system-model.json`, migrations, `core/`, `scripts/`.
> **No new numbers, no new statistics, no re-run.**

---

## 0. The amendments

### D-055 — AMENDMENT (2026-07-29): `Term` renders in situ; the glossary page becomes a secondary index

**Provenance:** the deployed-surface walk, plus an owner ruling on reader cost. **Recorded because
the walk has now produced change twice** — D-050 from the 07-25 walk, this from 07-29.

**The ruling.** Sending a reader to another surface to decode a term they met mid-sentence costs a
full shift of focus, and readers frequently do not come back. **On a novice-facing surface that cost
is not worth paying.** `Term` renders an **in-situ tooltip**; the reader learns beside the data that
prompted the question.

**⚠ What does NOT change, and this is the load-bearing half.** D-055 shipped **two** things: a
glossary *surface* and a **contract test that reddens when an undefined term reaches the screen.**
The objection is to the surface; **the guard is what lets this project claim every term a reader
meets is decodable**, and it was a delivery-readiness item in the 07-26 closeout.

**The guard is retained unchanged. One definition source. Only the rendering changes.**

**The glossary page is retained as a secondary index** — already built, already tested, zero cost,
and some readers want the full list. It simply stops being the only route to a definition.

**⚠ Two failure modes this rendering introduces, both to be designed against:**

1. **Truncation.** A small popover invites trimming, and the sentence that gets trimmed is the last
   one — which is where claim boundaries live. **If a definition does not fit comfortably, the
   tooltip is wrong, not the definition.** Asserted by test (§2).
2. **Hover-only.** Hover excludes touch and keyboard users entirely, which silently breaks the same
   decodability claim the guard protects. **Click/tap to open, focusable, dismissible.**

### D-062 — AMENDMENT (2026-07-29): two-column scorer layout

**Explanation left, ranking right.** Sections A–D (cascade, labels, pre-registration, result) left;
the reduced ranking table right.

**⚠ The coverage line renders WITH the ranking table, in the right column.** D-024 exists to stop a
denominator drifting from the claim it qualifies, and a two-column split is the easiest way yet to
orphan one.

**⚠ Caveat (b) — the pLDDT-attention confound — stays WITH the result**, not in the explanatory
column.

---

## 1. What to do

### 1.1 First, audit and report — before writing any definition

**Report, do not act on:**

- Is `structural score` already in the glossary? If so, **quote the existing definition.**
- Are `backbone` and `accession` on screen anywhere, and are they defined?
- **⚠ If either is on screen and undefined while the contract test is GREEN, the guard's coverage is
  narrower than believed.** That is a finding about the instrument — same class as *a calibration
  set proves only the cases it contains* — and it outranks this PR's cosmetics. **Report it.**
- Which other terms on the scorer surface are undefined? Candidates: `percentile`, `held out`,
  `leave-one-out`, `Spearman`, `ranking set`, `comparator`, `evidence score`, `Group B`.
  **List them. Add nothing unasked** — each definition is a claim and the owner rules the list.

### 1.2 Definitions the owner has ruled in

**`structural score`** — ⚠ **a claim boundary, not copy.** The most over-claimable phrase on the
surface. Owner to approve or amend:

> How much a target's predicted shape resembles the shapes of targets people have already built ADCs
> against. It comes from six measurements of the folded structure. **It is not a prediction that a
> drug will work**: it says nothing about delivery, internalisation, or how much of the target a
> tumour makes.

**The final sentence does not get trimmed for length.** If it does not fit, fix the tooltip.

**`backbone`** —

> The chain of atoms running the length of a protein — nitrogen, alpha-carbon, carbonyl carbon,
> repeating once per residue. Side chains branch off it.

**`accession`** —

> The stable identifier UniProt gives a protein, like `P04626` for HER2. Gene names and symbols get
> renamed over time; accessions do not, which is why targets are matched on accession here rather
> than by name.

*(The second sentence earns its place: it teaches, in situ, why D-040 computes `in_cohort_82` by
accession join rather than by symbol.)*

### 1.3 Then build

Two-column layout · `Term` as in-situ tooltip · terms wrapped at first use **in each column** ·
glossary page retained.

---

## 2. ⚠ What must not break — asserted by tests, not by review

- **The D-055 contract test stays green.** It is the guard; this PR changes rendering, not coverage.
- **Claim-boundary text is present in the RENDERED tooltip** — assert `structural score`'s final
  sentence appears in the popover DOM, not merely in the glossary source. **This is the truncation
  guard and it is the most important test in the PR.**
- **Keyboard and touch reach every definition** — openable without hover, focusable, dismissible.
- **Readability tripwire (D-056)** — FK ceiling pinned at the measured 12.5. If new copy breaches
  it, **shorten explanation, never a claim boundary.**
- **Constraint-A absence** — no `12`, `22`, `56`, `8`, median or Spearman literal in a component.
  A layout change must not tempt a value into a heading.
- **All four `result_status` states still render.** Two columns must not assume `complete`.
- **D-062's claim boundaries** — no significance language; the mean/median reversal visible;
  caveat (b) with the result.
- **Narrow viewport:** columns stack, and **when stacked the coverage line still precedes its table
  and caveat (b) still follows the result.** Assert the stacked order.

## 3. Done

In-situ tooltips through the existing guard, glossary retained as index, two columns with the
coverage line and caveat (b) correctly attached, three new definitions, every prior claim-boundary
test green, readability under ceiling. **Gate green.**

## 4. If something is wrong

Say so before building. Specifically:

- **If the existing `structural score` definition conflicts with §1.2**, that conflict is the
  finding — one of them is wrong and the owner rules which.
- **If the contract test's coverage turns out narrower than believed** (§1.1), report it before
  building. That is a guard defect and it matters more than the layout.
