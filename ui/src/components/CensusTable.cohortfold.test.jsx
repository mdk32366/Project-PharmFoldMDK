import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import CensusTable, { notFoldedTitle } from './CensusTable.jsx'
import { unfoldedCopy } from './CensusProteinView.jsx'

// ⚠⚠ THE DEFECT, FOUND BY WALKING THE TARGETS SURFACE. The census card said "waiting on rented
// capacity" for 29 proteins whose fold ALREADY EXISTS among the ranked 82 — same span, same
// boundary_method, folded on rental hardware. ERBB2 is the case the owner originally asked about:
// told a fold was pending when it was one click away.
//
// ⚠ The STATUS was never wrong. `above_local_ceiling` is true — 630 aa does exceed the local
// ceiling of 440. The COPY was wrong, and only the copy.
//
// ⚠⚠ AND THERE ARE THREE OUTCOMES, NOT TWO. The thirtieth overlapping row is IGF2R: in the cohort,
// and never folded THERE either — attempted on rental and killed by CUDA OOM at 2,491 aa. A queue
// position, an existing result and a failed attempt are three different facts.

const ERBB2 = {
  id: null, accession: 'P04626', gene: 'ERBB2', label: 'Receptor tyrosine-protein kinase erbB-2',
  span_aa: 630, folded: false, not_folded_reason: 'above_local_ceiling',
  not_folded_copy: 'not folded — its extracellular stretch is longer than the local graphics card can fold, so it is waiting on rented capacity',
  cohort_fold: { analysis_id: 52, mean_plddt: 73.94, fold_length: 630, census_span_aa: 630 },
}
const IGF2R = {
  id: null, accession: 'P11717', gene: 'IGF2R', label: 'Cation-independent M6P receptor',
  span_aa: 2264, folded: false, not_folded_reason: 'above_local_ceiling',
  not_folded_copy: 'not folded — … waiting on rented capacity',
  cohort_attempt_failed: { analysis_id: 57, reason: 'CUDA OOM folding 2491 aa at chunk_size=32' },
}
const PLAIN = {
  id: null, accession: 'Q9NPF2', gene: 'CHST11', label: 'Carbohydrate sulfotransferase 11',
  span_aa: 315, folded: false, not_folded_reason: 'ceiling_unmeasured',
  not_folded_copy: 'not folded — it sits in a size band nobody has tested yet',
}

describe('notFoldedTitle — three outcomes, never one', () => {
  // ⚠⚠ the exact false claim, asserted absent
  it('never says a fold is awaited when the fold exists', () => {
    const t = notFoldedTitle(ERBB2)
    expect(t).not.toMatch(/waiting on rented capacity/)
    expect(t).toMatch(/folded among the 82 ranked targets/)
    expect(t).toMatch(/73\.94/)
  })

  it('an attempt that FAILED is neither a queue position nor an existing fold', () => {
    const t = notFoldedTitle(IGF2R)
    expect(t).toMatch(/attempted among the 82 and failed/)
    expect(t).toMatch(/CUDA OOM/)
    expect(t).not.toMatch(/waiting on rented capacity/)
    // ⚠ and it must not claim a fold exists
    expect(t).not.toMatch(/folded among the 82 ranked targets/)
  })

  it('a protein folded nowhere keeps the original wording', () => {
    // ⚠ the fix must not rewrite the 747 rows that were always described correctly
    expect(notFoldedTitle(PLAIN)).toBe(PLAIN.not_folded_copy)
  })
})

describe('the row itself', () => {
  const draw = (rows) => render(<MemoryRouter><CensusTable rows={rows} /></MemoryRouter>)

  it('labels a protein folded elsewhere as NOT FOLDED HERE', () => {
    const { container } = draw([ERBB2])
    expect(container.querySelector('.badge-unfolded').textContent).toMatch(/NOT FOLDED HERE/)
  })

  it('labels a protein folded nowhere as plain NOT FOLDED', () => {
    const { container } = draw([PLAIN])
    const b = container.querySelector('.badge-unfolded')
    expect(b.textContent).toMatch(/NOT FOLDED/)
    expect(b.textContent).not.toMatch(/HERE/)
  })

  // ⚠⚠ D-081 — the two populations are measured separately and the row must not merge them
  it('does not link the census row to the cohort analysis', () => {
    const { container } = draw([ERBB2])
    const hrefs = [...container.querySelectorAll('a')].map((a) => a.getAttribute('href'))
    expect(hrefs.some((h) => h && h.includes('/targets/'))).toBe(false)
    expect(hrefs.some((h) => h === '/census/P04626')).toBe(true)
  })
})

// ⚠⚠ THE WHOLE CARD, NOT ONE SENTENCE. Fixing the banner and leaving its neighbours saying
// "nothing has been measured from a structure" put a false sentence one line from the true one —
// the exact defect the banner fix had just removed. This asserts NO sentence on the card contradicts
// the cohort fold, by reading the source rather than one rendered string.
describe('the whole unfolded card is consistent, not just the banner', () => {
  // ⚠⚠ AGAINST THE FUNCTION, NOT THE SOURCE TEXT. Two earlier versions scanned CensusProteinView
  // for "no structure yet" and looked for a nearby `cohort_fold`: at a wide window it reached the
  // BANNER's guard and passed while the paragraph was unguarded — the revert proof stayed green
  // and would have certified a fix that was not there; at a narrow window it reddened on correct
  // code. A character window is the wrong instrument for a branching question.
  const FOLD = { folded: false, span_aa: 630,
    cohort_fold: { analysis_id: 52, mean_plddt: 73.94, fold_length: 630 } }
  const NONE = { folded: false, span_aa: 315 }

  it('claims NO structure exists only when none exists anywhere', () => {
    const c = unfoldedCopy(FOLD)
    // ⚠ the two sentences that were left contradicting the banner
    expect(c.bar).not.toMatch(/nothing has been measured from a structure/)
    expect(c.body).not.toMatch(/there is no structure yet/)
    expect(c.body).not.toMatch(/there is no confidence score/)
  })

  it('keeps the original wording when the protein is folded nowhere', () => {
    const c = unfoldedCopy(NONE)
    expect(c.bar).toMatch(/nothing has been measured from a structure/)
    expect(c.body).toMatch(/there is no structure yet/)
  })

  // ⚠ D-081 — separate measurements, said rather than implied
  it('states that the ranked fold is not substituted here', () => {
    expect(unfoldedCopy(FOLD).body).toMatch(/not substituted here/)
    expect(unfoldedCopy(FOLD).bar).toMatch(/different span rule/)
  })

  it('returns nothing for a folded protein', () => {
    expect(unfoldedCopy({ folded: true })).toBeNull()
  })
})
