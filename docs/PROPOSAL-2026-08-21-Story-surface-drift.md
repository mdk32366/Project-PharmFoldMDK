# PROPOSAL — the Story surface no longer describes this application

> ⚠⚠ **STAGED FOR APPROVAL. NOTHING IN `Story.jsx` HAS BEEN CHANGED.** Owner asked for an inspection
> and, if it had drifted, proposed changes staged rather than shipped.
> ⚠ Every number below was measured against production at `main @ e2234e0`, not read from the log.

---

## §1 — What the Story currently claims, and what is true

`Story.jsx` is `D-051` decision 1: the cold-open at `/`, and **the most-read screen on the site**.
Its numbers are derived, never literal (`D-050`), so nothing it prints is *stale*. ⚠ **The drift is
not in its numbers. It is in its scope.**

| the Story says | measured today | verdict |
| --- | --- | --- |
| *"{folded} targets folded"* → **79** | 79 of 82 cohort · **2,690 of 3,467 census** | ⚠⚠ **true and radically incomplete** |
| *"no target reaches the high-confidence range (≥90)"* | 0 of 79 cohort **and 0 of 2,690 census** | ✅ **still true — and now far better evidenced** |
| highest mean pLDDT **84.23** | cohort 84.23 · **census 89.25** | ⚠ true of the cohort; the site's real maximum is higher |
| *"we folded a cohort of ADC targets"* | the platform is a cohort **plus a 3,467-protein census with a clinical evidence layer** | ⚠⚠ **describes an earlier application** |

**⚠⚠ THE ONE-LINE FINDING: a reader is told this project folded 79 proteins. It has folded 2,769.**
The Story is a faithful account of the application as it stood on 2026-07-29, and the census, the
clinical layer, the alias index, the structural profile and the surface check have all landed since.

⚠ **`/census` is not linked from the Story at all**, although Census sits in the top navigation and
holds 97% of the folds.

---

## §2 — What is NOT wrong, and should not be touched

⚠ Beats 3–6 are the argument of the project and they still hold exactly:

- **Beat 3** — the pre-registration dates (`D-027`, `D-041`, `D-060`) are constants and correct.
- **Beat 4** — *"modest, above-chance ordering… not distinguishable from ranking by expression and
  prior evidence"* is still what the fit found.
- **Beat 5** — *"most of it comes from the model's own confidence"* is still true. ⚠ `F-051` has since
  **sharpened** it: the two confidence features are really one, `membrane_proximal_plddt` at
  **32.2%** of attribution against `mean_plddt_ecd` at 6.4%. That is an available improvement, not a
  correction.
- **Beat 6** — the open question is unchanged and is still the right ending.
- **The correction paragraph** (`D-064`, the zero-positive fit) must stay exactly as written.
- ⚠⚠ **The ≥90 claim gets STRONGER, not weaker**, and the proposal below strengthens it rather than
  restating it: 2,769 folds, none in the high-confidence band.

---

## §3 — Proposed change: ONE new beat, and two small edits

⚠ Deliberately minimal. `D-056`'s readability ceiling and `D-051`'s *"thirty-second answer"* both
argue against growing this page; the census is one paragraph's worth of fact, not a second essay.

### 3a — ⚠⚠ NEW BEAT, placed immediately after *"What came out"*

> **Then we asked it of everything else.** The cohort is 82 proteins chosen by somebody else's
> paper. To find out whether its results were a property of *those* targets or of the method, we
> built a **census of every human surface protein we could define a boundary for — {censusManifest}
> proteins — and folded {censusFolded} of them** on the same tier, under the same rules. ⚠ The census
> is **not scored and not ranked**: a fold is a measurement, a score is an interpretation, and
> nothing here ranks a census protein against a cohort target. [Browse the census →]
>
> ⚠ And the ceiling holds across all of it: of **{totalFolds}** structures, **none** reaches the
> high-confidence range.

**Derived, never literal** — `{censusManifest}`, `{censusFolded}` and `{totalFolds}` come from
`/api/census`, exactly as the existing beat derives from `/api/analyses` (Constraint A, `D-050`).

### 3b — ⚠ EDIT: scope the existing "what came out" sentence

Current: *"{folded} targets folded"* — reads as the project's total.
Proposed: *"{folded} of the {denominator} cohort targets folded"*, so the number carries its
population before the census paragraph widens it. ⚠ **Every count states its key.**

### 3c — ⚠ EDIT: one clause in Beat 5, adopting `F-051`

Current: *"most of it comes from the model's own confidence in each fold"*.
Proposed: append — *"and within that, from a single feature: the confidence in the membrane-proximal
region carries **32.2%** of the ranking, five times the whole-domain average."*
⚠ `F-051`'s own caveat must travel with the figure: **32.2% is predictor weight, not causal share.**

---

## §4 — ⚠⚠ What this proposal deliberately does NOT do

- **It does not mention the clinical/HPA layer.** That layer is real and large, but the Story's
  argument is *"where is the deep learning"* — `D-051` decision 1 — and immunohistochemistry is not
  deep learning. ⚠ Putting it here would widen the page into a feature tour, which is what `D-056`'s
  ceiling exists to prevent. **If the owner wants it, that is a separate ruling and a separate beat.**
- **It does not change the headline.** *"We folded a cohort of ADC targets with ESMFold"* remains
  accurate as the entry point; the new beat is what widens it.
- **It does not touch the correction paragraph, the pre-registration dates, or the open question.**
- ⚠ **It does not rank, score or order any census protein** — `D-079` decision 1 stands, and the
  proposed copy states the prohibition rather than relying on it.

---

## §5 — What the owner is being asked to rule

1. **Does the census beat land at all**, or does the Story stay a cohort-only account by design?
2. **3a's placement** — after *"what came out"*, or later, after the fit beats?
3. **3c** — adopt `F-051`'s 32.2%, or keep Beat 5 qualitative per the Constraint-A/readability
   argument that kept beats 4–5 qualitative in the first place?
4. ⚠ **§4's exclusion of the clinical layer** — right call, or is the Story now the wrong shape for
   this application entirely?

⚠⚠ **Nothing ships until these are answered.** The Story is the most-read screen on the site and the
one place where a wrong scope claim reaches every reader.
