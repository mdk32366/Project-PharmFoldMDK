# PROPOSAL to the Planner — `D-075 amendment 1`: a FOURTH item for Decision (6), and what `geom_proxy` must carry because of it

> ⚠⚠ **DRAFTED BY CODE, NOT RULED. `D-075` is the Planner's pre-registration and it is void if code
> precedes it.** Nothing here has been run, no feature has been computed, and `geom_proxy` remains
> unbuilt. This document is written in the form the log expects **so the Planner can rule it, edit
> it, or reject it** — not so it can be pasted unread.
>
> ⚠ **Written 2026-08-20 against `D-103` and `D-103 amendment 1`, both merged.**

---

## §0 — Why this exists

`D-075` Decision (6) names **three** things the design cannot separate: F-008's two-precision
confound, fold-recipe heterogeneity, and the coordinate-mediated correlation between feature 7 and
pLDDT.

⚠⚠ **All three are about the FOLDING — the precision it ran at, the recipe it used, the coordinates
it produced. A fourth exists and it is UPSTREAM of all of them: which sequence was folded at all.**

`geom_proxy` computes feature 7 over a **membrane-proximal window of the extracellular span**. That
window's position is defined by the span boundary. **The span boundary comes from UniProt topology
annotation — one instrument, and until 2026-08-20 it had never been independently checked.**

---

## §1 — The measurement, on `D-075`'s own cohort

`D-103` provides an independent reading of the surface assignment from HPA immunofluorescence.
Applied to the **82-protein cohort `D-075` actually runs on**:

| Category | n | % |
| --- | --- | --- |
| `corroborated_membrane` | 25 | 30.5% |
| `corroborated_route` | 14 | 17.1% |
| `mixed` | 10 | 12.2% |
| ⚠ `unreconciled` | **2** | 2.4% |
| ⚠⚠ `if_not_attempted` — **nobody looked** | **31** | **37.8%** |

- **Corroborated: 39 of 82 (47.6%).**
- ⚠⚠ **For 31 of the 82 — 37.8% — no second instrument has ever examined the assumption that the
  folded span is extracellular.** The confound is **live on this cohort**, not hypothetical.
- ⚠ **Two proteins carry an active conflict.** Under `D-075` Decision (5)'s anti-fishing discipline
  they may not be dropped after seeing a result; if they are to be excluded, **it must be ruled
  now, before the run, or not at all.**

---

## §2 — Proposed **fourth item** for Decision (6)

> ⟡ **Fourth item, added 2026-08-20 with `D-103` — the span-selection confound.**
>
> Feature 7 is computed over a membrane-proximal window whose position is fixed by the extracellular
> span boundary. **That boundary is supplied by UniProt topology annotation for every row in the
> cohort** — `boundary_method: sliced_ecd`, `span_rule: vocabulary` or `gpi_rule_A`, with no
> alternative source anywhere in the pipeline. `D-103` supplies a second instrument for the first
> time and finds **39 of 82 corroborated, 31 never examined, 2 unreconciled.**
>
> ⚠⚠ **So this design cannot separate *"membrane-proximal geometry carries the signal"* from
> *"membrane-proximal geometry reflects how the span was CHOSEN."*** If the boundary rule is
> systematically off — even slightly, and even for a subset — feature 7 measures the geometry of a
> window placed by the annotation rather than by the biology, and a `geom_proxy` result in **either
> direction** inherits that.
>
> ⚠ **This is distinct from the three items above.** They concern the fold; this concerns the input
> to the fold. **A confidence-blind feature set does not become boundary-blind**, and `geom_proxy`
> was designed to remove confidence information, not annotation dependence.
>
> ⚠ **No claim in either direction.** *"The 31 unexamined spans are fine"* is exactly as unsupported
> as the opposite. `D-103 amendment 1` measured the corroboration rate as **flat** across span length
> and across how well-studied a protein is — **which detects no bias but does not prove absence**,
> and cannot, because corroboration is only measurable where corroboration exists.

---

## §3 — What Code proposes `geom_proxy` must CARRY (three items, each rulable separately)

**⚠ These are proposals. Each can be accepted, modified or refused independently.**

### (a) The evidence state travels with the result — it is NOT a covariate, NOT a weight, NOT a filter

Every `geom_proxy` output row carries its `D-103` category alongside the value.

- ⚠⚠ **It must NOT enter the model.** Adding it as a feature or a sample weight would make an
  evidence-availability artifact into a term of the structural axis — **and evidence availability is
  a property of HPA's antibody catalogue, not of the protein.** `D-079` decision 1 bars scoring
  census rows; `D-103` defines **no ordering** over its categories, deliberately.
- **It travels so the result can be READ conditionally**, which is the only honest form: *"the axis
  was measured over a cohort where 47.6% of span assignments carry independent corroboration."*

### (b) A pre-registered stratified read-out — decided now, reported whichever way it falls

Report the `geom_proxy` result **twice**: over all 82, and over the **39 corroborated** only.

- ⚠⚠ **Both numbers are reported unconditionally.** Pre-registering this is the entire point: a
  stratified analysis chosen *after* seeing the full-cohort result is fishing, and `D-075` Decision
  (5) already bars exactly that shape.
- ⚠ **n=39 is small and the entry must say so before the run**, not after. `D-075` Decision (0)
  already establishes that at n=12 a median is not a stable anchor; **n=39 is better and is still
  not large**, and the stratified arm carries wider intervals by construction.
- **If the two arms disagree, that is a RESULT, not a problem to reconcile.** Which arm is
  authoritative is the Planner's ruling and **must be fixed before the run.**

### (c) An explicit statement of what a survival result would and would not exclude

`D-075` Decision (6) exists so a survival result is *"not over-read as excluding all confounds, only
the confidence one."* ⚠ **That sentence now needs a fourth clause**: a `geom_proxy` survival excludes
neither precision, nor recipe, nor coordinate-mediated correlation, **nor span selection.**

---

## §4 — ⚠⚠ THE BROADER POINT, AND CODE IS DELIBERATELY UNDERSTATING IT

The owner observed that a single scalar is being used to say two things that cannot both be said
about one protein. **Stated precisely and defensibly:**

- **pLDDT is a per-residue confidence in a predicted structure, conditioned on the input sequence.**
  That is what its authors say it is.
- **When the input is a FRAGMENT — an ectodomain slice — pLDDT is confidence about that fragment's
  geometry given that sequence. It carries no information about whether the fragment boundary was
  correct.** Those are different claims.
- ⚠⚠ **A composite confidence would therefore multiply a measured quantity by an unmeasured
  assumption, and produce a number that LOOKS like it accounts for uncertainty while hiding the
  larger source of it.**

⚠ **What Code has NOT established, and will not claim:** that this is unrecognised in the wider
field. The literature has not been searched, and *"nobody has noticed this"* is precisely the shape
of confident-but-wrong finding `F-047` catalogues. **What is established is narrower and solid: it
is true of THIS pipeline, it is now measured, and the measurement is on the record.** Whether it
generalises is an empirical question about the literature, and answering it is a search, not an
assertion. **`P-005` states the same limit.**

---

## §5 — What the Planner is asked to rule

1. **Accept, modify or reject the fourth item** for Decision (6).
2. **Rule (a), (b) and (c)** — separately; they are not a package.
3. ⚠ **Rule the two `unreconciled` proteins now**, before any run: kept, or excluded with the
   exclusion stated as a rule rather than a list.
4. **Rule which arm is authoritative** if the stratified arms disagree.
5. ⚠ **Decide whether `D-075` needs a fresh pre-registration date.** The design has not changed, but
   a confound named after the entry was accepted may or may not, under this project's conventions,
   require the entry to be re-dated. **Code does not know the precedent and is not guessing.**

**Nothing is built. Nothing is run. `geom_proxy` remains unwritten.**
