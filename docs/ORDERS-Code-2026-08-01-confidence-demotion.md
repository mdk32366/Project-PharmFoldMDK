# Orders for Code — demote & reframe "Confidence" so it can't be misread as target quality (un-gated honesty fix)

> **⚠ WHY NOW, UN-GATED.** This changes nothing about what confidence IS or how it's computed — it
> changes how prominently it's presented and how it's labeled, so a neophyte cannot read a green
> "Confidence" dot as "good target." It is pure honesty-of-presentation over existing data. No census,
> no D-075 result, no scorer change. It also *prepares the slot* the structural-suitability score
> lands in later (`SPEC-two-scores-suitability.md`).
>
> **Scope:** `ui/src/components/TargetList.jsx`, `ui/src/plddt.js` (band-label framing only, NOT the
> band boundaries or colors), possibly `ui/src/components/Confidence.jsx` (framing), their tests.
> **NOT** `core/`, `db/`, the API, the scorer.
>
> **⚠ DEMOTION IS NOT DELETION.** Confidence stays fully present and honest in the fold detail
> (`Confidence.jsx`, `PlddtPlot`, `PlddtSpread` — all already good, D-039/D-048). This order changes
> its RANK in the visual hierarchy and its LABEL on the list, so it reads as a fold-quality check, not
> a target verdict. No confidence information is removed.

---

## 0. What the Planner found (the exact trap)

- `ui/src/plddt.js` band labels are ALREADY careful and honest: "Confident **backbone**", "backbone
  **unreliable**", "**not reliably interpretable**" — every label is about *fold quality*, never target
  quality. **The vocabulary is correct; do not weaken it.**
- `ui/src/components/Confidence.jsx` ALREADY carries the honest disclaimer ("self-reported confidence
  in local backbone geometry — not a measure of whether the fold is correct"). **Correct; leave it.**
- **The trap is in `TargetList.jsx`:** the band renders under a column header that says only
  **"Confidence"** beside a traffic-light dot. The careful "backbone" qualifier lives in the band
  label, but the *column header + color* say "good/bad" at a glance — a neophyte reads green
  Confidence as "good target." Confidence is the most prominent per-target signal on the list, and
  nothing more relevant sits above it, so the reader promotes it into a suitability verdict.
- Also honest and to be preserved: `PlddtAmbiguityNote.jsx` already says the scores "lean most on the
  model's own confidence… might track real structural order — or just how much the protein" is studied.
  This order is consistent with that; do not touch it.

---

## 1. The fix — three surgical moves on the LIST

### 1a — Relabel the column so the header says what the band labels already say
The `TargetList` column currently headed **"Confidence"** (or "mean pLDDT" / "Confidence" pair) is
reframed so the header itself signals *fold quality*, not target quality. Owner-final copy, but the
substance: **"Fold confidence"** or **"Structure confidence (pLDDT)"** — a header a neophyte reads as
"how good is the *model's structure*," not "how good is the *target*." The word "Confidence" standing
alone as a column head is the problem; qualify it.

### 1b — Demote its visual prominence
Confidence is currently a headline column with a color dot — as prominent as gene/accession. Demote
it so it does not read as *the* signal:
- De-emphasize the color treatment on the list (keep the band color available on hover / in detail,
  but the list dot should not be the most eye-catching element in the row), OR
- move it rightward / make it visually secondary to the identity columns.
- **Owner rules the exact visual treatment** — the requirement is that confidence stops being the
  top-of-hierarchy per-target signal, not a specific pixel choice.

### 1c — State, once on the list, what confidence is and isn't
A short lede or column tooltip on the list: **"Confidence is the model's certainty about the *folded
structure* — not a measure of whether the target is a good ADC candidate."** This is the sentence that
inoculates the neophyte at the glance, before they open any detail panel. Reuse the existing honest
vocabulary; do not invent a new claim.

### ⚠ 1d — Reserve the slot, don't fill it
Where a target-quality signal WOULD go (the structural-suitability score, `SPEC-two-scores-suitability.md`),
leave it visibly absent-with-a-reason if natural — e.g. the list may note "suitability scoring: see
Scorer" or simply not imply confidence is standing in for it. **Do NOT build a suitability column
here** — that is D-075-gated. This order only stops confidence from *impersonating* it.

---

## 2. ⚠ What must NOT change

1. **Band boundaries and colors in `plddt.js`** (50/60/70, D-039) — the confidence *scale* is correct
   and load-bearing elsewhere (`PlddtPlot`, `PlddtSpread`, `Confidence`, `StructureViewer` coloring).
   This order reframes the LABEL/PROMINENCE on the list, never the scale.
2. **`Confidence.jsx`'s disclaimer and the per-residue plot** — already honest, D-039/D-048. Untouched
   except optional framing consistency.
3. **`PlddtAmbiguityNote.jsx`** — the confound disclosure. Untouched (D-075-gated territory).
4. **The band labels' "backbone" honesty** — do not genericize "Confident backbone" to "Confident";
   the backbone qualifier is exactly what makes it about fold-not-target.

---

## 3. Tests (red first)

- **List column header no longer reads as a bare "Confidence" verdict** — asserts the header carries
  a fold/structure qualifier (matches /fold|structure/i, not "Confidence" alone).
- **The what-it-isn't statement (1c) renders** on the list.
- **Confidence is not the sole/top prominent signal** — a structural assertion appropriate to the
  chosen treatment (e.g. the identity columns precede it, or the dot is not the headline element).
- **Band scale unchanged** — `plddt.bands.test.js` and any band test stay green (this order must not
  touch boundaries/colors).
- **No suitability claim introduced** — denylist test: the list does not contain "suitability",
  "good target", "recommended", "best candidate" language attached to the confidence column (it must
  not fill the slot it's being demoted out of).
- **Existing `TargetList.test.jsx`** (tier legibility, filter) stays green.

## 4. Order of work

1. Tests red first (header-reframe, what-it-isn't present, no-suitability-claim, band-scale-unchanged).
2. `TargetList.jsx` — relabel (1a), demote (1b), add the statement (1c), reserve-don't-fill (1d).
3. Optional framing consistency in `Confidence.jsx` (no disclaimer change).
4. Confirm band tests + tier tests green; gate; dry-diff; owner copy; owner merge. Deploys — verify
   live that the list no longer reads confidence as a verdict.

## 5. ⚠ Three things that will bite

1. **Do not weaken the band vocabulary.** "Confident backbone" stays "backbone" — that qualifier is
   the honesty. Reframe the column header and prominence, not the band labels' careful wording.
2. **Do not build a suitability column.** The slot is reserved (1d), not filled — that is D-075-gated.
   Confidence demotion removes an impersonation; it does not add the real thing.
3. **Do not touch the band scale or the confound note.** Boundaries, colors, `PlddtAmbiguityNote` are
   out of scope — changing them risks the confound-disclosure work that is D-075-result-gated.

## 6. What "done" means

On the list, confidence reads unmistakably as a *fold-quality* check (qualified header, demoted
prominence, a one-line "what this isn't"), the neophyte cannot mistake a green dot for a good target,
the band scale and confound disclosures are untouched, no suitability claim is introduced, existing
tests green, verified live post-deploy. The target-quality slot is reserved for the gated suitability
score, not filled.

## 7. If something is wrong with these orders

Say so before building. Specifically: if demoting confidence's prominence on the list genuinely
removes information a reader needs at the glance (a UI-depth finding — the owner rulings on confidence
prominence, D-039/D-048, may conflict), surface the tension rather than silently overriding a prior
owner ruling on how prominent confidence should be.
