// pLDDT confidence bands (D-039). Boundaries 50/60/70: convention anchors 70 and 50, the cohort's
// own measured mass justifies 60 (D-039 measured 45% below it on 42 folds; D-049 re-justified at
// 29.1% on the 79-fold cohort — the divider holds, the number moved). The cohort max is 84.23
// (D-049; was 81.4 on 42 folds) — there is still NO high-confidence tier (nothing ≥90), surfaced in
// the top band's caveat where it is read, not only in the log.
//
// This is the single source of the band scheme; the confidence element, the per-residue plot, and
// the structure colouring all read it, so the structure and its legend cannot disagree.

export const COHORT_MAX_PLDDT = 84.23

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

// ⚠⚠ THE ABSENCE OF A NUMBER IS NOT THE ABSENCE OF A STRUCTURE (D-150). This sentinel read
// `not folded` and was returned for **every** null pLDDT — including a folded protein whose
// `plddt.json` failed to load, and every per-residue gap inside a structure that is on disk and
// rendering. `bandFor` is asked by the confidence headline, the per-residue plot and the 3Dmol
// colour function; none of those is in a position to know whether a fold exists, and two of them
// only run when one does. So the band says what it actually knows — *there is no pLDDT here* —
// and the question *was this protein folded* is answered by `structureStatus.js` axis A, on rows
// that carry `folded` / `structure_kind`.
// ⚠ `label` is the pinned wording; `min: null` is unchanged and is what distinguishes the sentinel
// from a value band.
export const NO_PLDDT_LABEL = 'no pLDDT'
const NO_PLDDT = { min: null, label: NO_PLDDT_LABEL, color: '#718096', caveat: null }

// The band for a mean or per-residue pLDDT value. BANDS is high→low, so the first `>= min` wins.
export function bandFor(plddt) {
  if (plddt == null || Number.isNaN(plddt)) return NO_PLDDT
  return BANDS.find((b) => plddt >= b.min) ?? BANDS[BANDS.length - 1]
}

export const colorFor = (plddt) => bandFor(plddt).color
