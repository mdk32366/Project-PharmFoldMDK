// The census surface — ⚠⚠ EXPLICITLY UNSCORED, AND THAT IS THE POINT OF THE PAGE.
//
// ⚠ `### D-079` decision 1 bars scoring any census row, and the scorer-import refusal enforces it
// in code. `app/reads.py` filters `cohort_tranche == COHORT_TRANCHE` so the ranked surface serves
// the 82 and only the 82 — **a census row appearing there is a named stop condition.**
//
// So this page shows the census as a POPULATION: how many proteins, how they were measured, and
// what was deliberately not done to them. ⚠ It shows NO score, NO rank and NO ordering by
// suitability.
//
// ⚠⚠ TWO CLAUSES OF THIS COMMENT WENT STALE AND ARE CORRECTED HERE RATHER THAN DELETED, because
// they are the same defect the log records twice (F-049 amendment 2, instance 4): a sentence that
// keeps its wording while the world moves under it, with no diff and no failing test to mark the
// moment.
//   · It said "and NO per-protein row — because a per-protein list on a public surface is one sort
//     control away from being read as a shortlist." ⚠ REVERSED by the owner under D-087 —
//     "why hide it under a bushel?" — and CensusTable has shown per-protein rows since. The worry
//     was answered by construction (default order is accession; no score column; sorting is not
//     scoring), not by omission.
//   · "EXPLICITLY UNSCORED" is still true of the CENSUS PAGE and of the database — no census row
//     is scored or ranked — but as of D-079 amendment 1 (ruled by amendment 2) each protein's own
//     page carries a STRUCTURAL PROFILE: the pre-registered model applied to its measured
//     features. ⚠ Not a score by ruling 1, and this file must not pretend the output does not
//     exist merely because it is called something else.
//
// ⚠ EVERY FIGURE IS COUNTED OFF data/census/census_manifest.v7.csv AND ITS PROVENANCE. Numbers are
// LITERALS here for the same reason the glossary's are (D-053 dec 5): a definition — or a frozen
// count — does not change because our data does, so it needs no route. When the census is re-parsed
// these are updated in the same commit that moves the artifact, or they are wrong.

export const CENSUS = {
  // ── what was DONE to the population (D-079 amendment 3) ──
  // ⚠ Frozen literals like every figure here, and for the same reason (D-053 dec 5). Counted
  // 2026-08-19 by scripts/census_profile_report.py over census_features.v1.jsonl
  // (sha256 c08f9f1d…) with the model in data/census/run2_raw_scale_model.json. If the artifact
  // or the bar moves, these move in the same commit or they are wrong.
  profile: {
    measuredOn: '2026-08-19',
    // ⚠ D-094 amendment 1 dec 1: the figure is correct ABOUT ITS ARTIFACT, and the surface
    // must say which artifact. Rendered adjacent to the count, never only in this comment.
    artifact: 'census_features.v1.jsonl',
    folded: 2690,
    withFeatures: 2632,
    profiled: 1397,
    refused: 1293,
    refusedOutOfRange: 1225,
    refusedSpanBelowFloor: 58,
    refusedIncomplete: 10,
    // the span of the values that survive, and the cohort's own for comparison (F-006)
    bandMin: 0.1065,
    bandMax: 0.2927,
    cohortBandMin: 0.116,
    cohortBandMax: 0.285,
    // why the refusals happen, in one pair of numbers
    censusMedianPlddtEcd: 57.0,
    cohortMedianPlddtEcd: 72.4,
  },

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
  // ⚠⚠ D-094 amendment 1 dec 2. `rows` is what the MANIFEST PLANS; `inArtifact` is what
  // census_features.v1.jsonl actually contains. They are different populations and the page must
  // never render one as though it were the other. ⚠ A bare 776 is forbidden: it asserts that 776
  // structures exist, when 728 are folded and 48 are HELD.
  tranches: [
    { tranche: 1, span: '1–50 aa', rows: 1307, inArtifact: 1307 },
    { tranche: 2, span: '51–150 aa', rows: 535, inArtifact: 535 },
    // ⚠ 517 planned, 516 present. The one absence is named and its cause is NOT stated here —
    // P55073's disposition is contested and unruled, and naming a cause would be deciding it.
    { tranche: 3, span: '151–300 aa', rows: 517, inArtifact: 516, absent: ['P55073'] },
    { tranche: 4, span: '301–440 aa', rows: 332, inArtifact: 332 },
    {
      tranche: 5,
      span: 'over 440 aa — rented GPU',
      rows: 776,
      inArtifact: 0,
      complete: 728,
      held: 48,
      heldCause: 'held by D-090’s claim filter under D-109 — the 48 carry no tier',
      heldMeasuredOn: '2026-09-02',
    },
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
