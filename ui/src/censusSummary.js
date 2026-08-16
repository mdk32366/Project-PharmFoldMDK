// The census surface — ⚠⚠ EXPLICITLY UNSCORED, AND THAT IS THE POINT OF THE PAGE.
//
// ⚠ `### D-079` decision 1 bars scoring any census row, and the scorer-import refusal enforces it
// in code. `app/reads.py` filters `cohort_tranche == COHORT_TRANCHE` so the ranked surface serves
// the 82 and only the 82 — **a census row appearing there is a named stop condition.**
//
// So this page shows the census as a POPULATION: how many proteins, how they were measured, and
// what was deliberately not done to them. ⚠ It shows NO score, NO rank, NO ordering by suitability,
// and NO per-protein row — because a per-protein list on a public surface is one sort control away
// from being read as a shortlist.
//
// ⚠ EVERY FIGURE IS COUNTED OFF data/census/census_manifest.v7.csv AND ITS PROVENANCE. Numbers are
// LITERALS here for the same reason the glossary's are (D-053 dec 5): a definition — or a frozen
// count — does not change because our data does, so it needs no route. When the census is re-parsed
// these are updated in the same commit that moves the artifact, or they are wrong.

export const CENSUS = {
  // ── the population ──
  manifestRevision: 7,
  manifestRows: 3467,
  seed: 20260807,
  spanDefinition: 'v2-ruled-vocabulary-2026-08-07',
  frozenDefinition: 'v1-extracellular-substring-2026-07-21',

  sources: [
    { label: 'surface class', rows: 2807, foldable: 2581 },
    { label: 'annex (non-surface)', rows: 2209, foldable: 886 },
  ],

  // ⚠ Tranches are EXECUTION BATCHES (D-083). Not a ranking, not a priority, not a quality signal.
  tranches: [
    { tranche: 1, span: '1–50 aa', rows: 1307 },
    { tranche: 2, span: '51–150 aa', rows: 535 },
    { tranche: 3, span: '151–300 aa', rows: 517 },
    { tranche: 4, span: '301–440 aa', rows: 332 },
    { tranche: 5, span: 'over 440 aa — rented GPU', rows: 776 },
  ],

  // ⚠ Absences, each with a CAUSE. Never a zero, never a bare null.
  notFoldable: [
    { reason: 'no extracellular span', rows: 1519,
      plain: 'UniProt describes no part of this protein as facing outward.' },
    { reason: 'never fetched (inactive UniProt entry)', rows: 26,
      plain: 'The entry was withdrawn, so it was never asked about — not measured and found empty.' },
    { reason: 'GPI anchor with no usable chain record', rows: 2,
      plain: 'Attached by a lipid anchor, but the record does not say where the mature protein starts.' },
    { reason: 'span boundary unknown', rows: 1,
      plain: 'The outward-facing part is described, and one end of it is recorded as unknown. No coordinate was invented.' },
    { reason: 'span contradicted by its own record', rows: 1,
      plain: 'The entry describes an outward-facing stretch that also contains a membrane-crossing helix. Excluded rather than trimmed to fit.' },
  ],
}

// ⚠⚠ THE LIMITATION BLOCK. It is not a footnote and it must never be trimmed to fit a layout.
// Each line is a thing this page's numbers do NOT mean.
export const CENSUS_LIMITS = [
  {
    head: 'Nothing here is scored, and nothing here is ranked.',
    body: 'These proteins have not been run through the ranking model, and they will not be ' +
      'without a separate decision. A count is not a shortlist. The ranked list of 82 targets ' +
      'elsewhere in this application is a different population, measured under a different span ' +
      'definition, and the two must not be compared.',
  },
  {
    head: 'Foldable is a statement about the annotation, not about the protein.',
    body: 'A protein counts as foldable here when a public database describes an outward-facing ' +
      'stretch of it precisely enough to cut out. Proteins with no such description are counted ' +
      'separately with the reason — they are not "not targets", they are not described.',
  },
  {
    head: 'For proteins that cross the membrane several times, only the largest outward stretch is used.',
    body: 'Just under half the measured rows have more than one outward-facing segment. The ' +
      'largest contiguous one is folded and the rest are discarded — so a protein with four short ' +
      'loops is represented by one of them, not by their sum.',
  },
  {
    head: 'The counts carry a known tilt, and nothing is adjusted for it.',
    body: 'Proteins with no described outward stretch skew very slightly towards older database ' +
      'entries. The effect is real but small — around 2% of the variation — and it is recorded ' +
      'rather than corrected, because correcting it would be a second decision resting on the first.',
  },
  {
    head: 'Two span definitions exist in this project, and every count states which produced it.',
    body: 'The 82-target cohort is frozen under the original definition permanently. The census ' +
      'uses the ruled vocabulary. A number from one is not comparable to a number from the other ' +
      'unless both are named.',
  },
]
