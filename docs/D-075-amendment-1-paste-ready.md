# PASTE-READY — `D-075 amendment 1` — for `docs/README.md`

**AUTHORED-SHA256** (range: **first `####` header → EOF**, anchored to line starts) = `681e415eaaa7a1b15a8a1026dfd60a3f6f1bbc0a2fb20e4f7110429685a6f55a`
**bytes** = `7312`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE. No landing header.**
>
> ⚠ Sub-entry — **no integer.** Placed at the end of `D-075`'s body, before the next `###`.
> **Three greps on merge: `#### D-075 amendment 1` once · `### D-075 amendment 1` ZERO · `### D-075`
> once.**
>
> ⚠⚠ **`D-075` IS NOT RE-DATED, and the precedent is inside the entry itself.** It is dated
> **2026-08-01** and already carries *"⟡ **Second item, added 2026-08-06 with `### F-017`**"* and
> *"⟡ **Third item, added 2026-08-06 with `### F-017`**"* — **items added five days later, attributed
> to the finding that prompted them, with the entry's date untouched.** **`§5` item 5 of the proposal
> is answered by the precedent, not by a new convention.**

---

#### D-075 amendment 1 — ⚠⚠ A FOURTH confound, and it is upstream of the other three: which sequence was folded at all

- **Date:** 2026-08-20 · **Status:** ruled. ⚠⚠ **`D-075` remains a pre-registration and remains void
  if code precedes it. `geom_proxy` is unbuilt and unrun, and nothing below may be run until this
  amendment is merged.**
- **Prompted by:** `D-103 (a second instrument on the claim the whole census rests on)` and
  `D-103 amendment 1`.
- **Drafted by Code** as `docs/PROPOSAL-Planner-2026-08-20-D-075-amendment-1-span-selection-confound.md`;
  ⚠ **ruled here with three changes, each named below rather than folded in.**

---

**⟡ Fourth item, added 2026-08-20 with `### D-103` — the span-selection confound.**

Feature 7 is computed over a **membrane-proximal window whose position is fixed by the extracellular
span boundary.** ⚠ **That boundary is supplied by UniProt topology annotation for every row in the
cohort** — `boundary_method: sliced_ecd`, `span_rule: vocabulary` or `gpi_rule_A` — **with no
alternative source anywhere in the pipeline.** `D-103` supplies a second instrument for the first
time and finds, **on `D-075`'s own 82**: `corroborated_membrane` **25** · `corroborated_route` **14**
· `mixed` **10** · `unreconciled` **2** · ⚠⚠ `if_not_attempted` **31 (37.8%)**. **Corroborated: 39 of
82, 47.6%.**

⚠⚠ **So this design cannot separate *"membrane-proximal geometry carries the signal"* from
*"membrane-proximal geometry reflects how the span was CHOSEN."*** If the boundary rule is
systematically off — even slightly, even for a subset — feature 7 measures the geometry of a window
placed by **annotation** rather than by **biology**, and a `geom_proxy` result in **either direction**
inherits it.

⚠ **Distinct from the three items above, which all concern the FOLD** — its precision, its recipe,
its coordinates. **This concerns the INPUT to the fold.** **A confidence-blind feature set does not
become boundary-blind:** `geom_proxy` was designed to remove **confidence** information, not
**annotation dependence.**

⚠ **No claim in either direction.** *"The 31 unexamined spans are fine"* is exactly as unsupported as
the opposite. `D-103 amendment 1` measured corroboration as **flat** across span length
(73.7 / 75.8 / 73.9 / 75.4 / 72.4%) and across how well-studied a protein is (73.9% vs 76.4%) —
⚠⚠ **which licenses *"no bias detected"* and NOT *"the corroborated rate applies to the
unexamined."*** **The limit is irreducible: corroboration is measurable only where corroboration
exists.**

---

**RULING (a) — ACCEPTED AS PROPOSED, and made structural rather than documentary.**
Every `geom_proxy` output row carries its `D-103` category **alongside** the value.
⚠⚠ **It MUST NOT enter the model — not as a feature, not as a sample weight, not as a filter.**
**Evidence availability is a property of HPA's ANTIBODY CATALOGUE, not of the protein**, and
`D-103` defines **no ordering** over its categories, deliberately.
⚠ **Code's addition to the proposal: a prohibition test, proven RED, on the `EE-0` pattern —
INCLUDING THE RENAME ROUTE.** Wiring a `D-103` category into the feature path must redden, **and so
must renaming it first**; *a token scan is defeated by renaming, and the pre-registered six are
pinned by name.*

**RULING (b) — ACCEPTED, AND WIDENED TO THREE ARMS. All three pre-registered here; all three reported
unconditionally.**

| arm | n | status |
|---|---|---|
| **all 82** | 82 | ⚠⚠ **AUTHORITATIVE** |
| corroborated only | **39** | robustness read-out |
| ⚠ **all 82 minus the two `unreconciled`** | **80** | sensitivity read-out |

⚠⚠ **THE FULL 82 IS AUTHORITATIVE, AND THE REASON IS RULING (a).** **Making the corroborated subset
authoritative would let evidence availability select the analysis population — the same
antibody-catalogue artifact that (a) bars from the model, arriving through the back door as a
sampling frame.** ⚠ **A property that may not be a feature may not be a filter either.**

⚠ **`n = 39` is small and this entry says so BEFORE the run, not after.** `D-075` Decision (0)
establishes that at `n = 12` a median is not a stable anchor; **39 is better and is still not large,
and the stratified arm carries wider intervals by construction.**

**⚠⚠ AND THE INTERPRETATION OF DISAGREEMENT IS FIXED NOW, BOTH WAYS:**
- **Arms AGREE** → ⚠ **this weakens the fourth item and does not eliminate it.** **The 31 unexamined
  cannot be checked in either direction, so agreement is evidence about the 39, not about the 82.**
- **Arms DISAGREE** → ⚠⚠ **that is a RESULT, not a reconciliation problem.** It would mean the axis
  behaves differently where the span carries independent corroboration — **which is direct evidence
  about the span-selection confound itself, and is more interesting than either arm alone.**

**RULING — ⚠ THE TWO `unreconciled` PROTEINS ARE KEPT** (owner, 2026-08-20). **They are not dropped,
and `D-075` Decision (5)'s anti-fishing discipline is satisfied because this is ruled BEFORE the
run.**
**"Accounted for" is given a measurable meaning rather than a rhetorical one:**
1. ⚠ **Both are NAMED in the result entry, with their conflict described** — not summarised as *"two
   unreconciled."*
2. **They are included in the authoritative arm and in the corroborated-only arm's complement.**
3. ⚠⚠ **The 80-row sensitivity arm exists precisely so their contribution is VISIBLE rather than
   argued.** **It is pre-registered, reported unconditionally, and is NOT authoritative** — *a third
   arm chosen after seeing the first two would be fishing; declared before the run, it is
   `D-065`'s report-at-several-settings discipline.*

**RULING (c) — ACCEPTED.** `D-075` Decision (6)'s closing sentence gains a fourth clause: ⚠ **a
`geom_proxy` survival excludes neither precision, nor recipe, nor coordinate-mediated correlation,
NOR SPAN SELECTION.**

---

**⚠ WHAT THIS AMENDMENT DOES NOT DO**

- ⚠⚠ **It does not license reuse of `D-075`'s correlation coefficients.** The entry's own scope note
  binds any later citation: they were measured **on the 56 ranking-set rows, at one recipe
  composition, on this cohort as folded** — **a property of this instrument's output on this cohort,
  not a constant of the features, and not transferable to the census.**
- ⚠ **It does not resolve the confound.** **It names it, measures it on the actual cohort, and fixes
  how the result must be read.** *`D-074` decision 3: name the check, do not build a framework.*
- ⚠ **It does not claim the observation is novel to the field.** **The literature has not been
  searched, and *"nobody has noticed this"* is the exact shape `F-047` catalogues.** **What is
  established is narrower and solid: it is true of THIS pipeline, it is now measured, and the
  measurement is on the record.**
- **It does not build, run or schedule `geom_proxy`.**

**Assumptions relied on:** `A-014` — ⚠ **twice, and in opposite directions**: UniProt topology
annotation is a curated model of the protein, **and** HPA immunofluorescence localisation is an
assay-plus-interpretation. **Neither instrument is ground truth, which is why corroboration is the
claim and confirmation is not.**
