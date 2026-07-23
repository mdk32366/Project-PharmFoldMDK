// pLDDT confidence bands (D-039). Boundaries 50/60/70: convention anchors 70 and 50, the cohort's
// own measured mass justifies 60 (45% of folds fall below it). The cohort max is 81.4 — there is
// NO high-confidence tier, surfaced in the top band's caveat where it is read, not only in the log.
//
// This is the single source of the band scheme; the confidence element, the per-residue plot, and
// the structure colouring all read it, so the structure and its legend cannot disagree.

export const COHORT_MAX_PLDDT = 81.4

export const BANDS = [
  {
    min: 70,
    label: 'Confident backbone',
    color: '#2b6cb0',
    caveat: `cohort max ${COHORT_MAX_PLDDT} — no target reaches the high-confidence range`,
  },
  { min: 60, label: 'Moderate', color: '#2f855a', caveat: null },
  { min: 50, label: 'Low — backbone unreliable', color: '#b7791f', caveat: null },
  { min: 0, label: 'Very low — not reliably interpretable', color: '#c53030', caveat: null },
]

const NO_FOLD = { min: null, label: 'not folded', color: '#718096', caveat: null }

// The band for a mean or per-residue pLDDT value. BANDS is high→low, so the first `>= min` wins.
export function bandFor(plddt) {
  if (plddt == null || Number.isNaN(plddt)) return NO_FOLD
  return BANDS.find((b) => plddt >= b.min) ?? BANDS[BANDS.length - 1]
}

export const colorFor = (plddt) => bandFor(plddt).color
