import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import TargetScorerPanel from './TargetScorerPanel.jsx'

// Distinctive fixture values — the live literals (0.116/0.220/0.285 range, 56, 0.607 median, the LOO
// percentiles) must NEVER be typed into the panel; every number derives from the payload (D-068 dec 2).
const RANKING = {
  result_status: 'complete',
  result: {
    plddt_floor: 50,
    distribution: [{ symbol: 'ERBB2', percentile: 0.71 }],
  },
  rows: [
    { rank: 1, accession: 'A-TOP', gene: 'TOP1', score: 0.90, attributions: [0.01, -0.02, 0.30, 0.40, -0.05, 0.06] },
    { rank: 2, accession: 'A-ERBB2', gene: 'ERBB2', score: 0.70, attributions: [0.1, 0.1, 0.1, 0.1, 0.1, 0.1] },
    { rank: 3, accession: 'A-BOT', gene: 'BOT1', score: 0.40, attributions: [0, 0, 0, 0, 0, 0] },
  ],
}
const view = (detail) => render(<MemoryRouter><TargetScorerPanel detail={detail} ranking={RANKING} /></MemoryRouter>)

describe('TargetScorerPanel (D-068)', () => {
  it('ranked: score NEVER renders without rank and distribution context (dec 2)', () => {
    const { container } = view({ accession: 'A-TOP', gene: 'TOP1', mean_plddt: 70, disposition: 'ranked' })
    const t = container.textContent
    expect(t).toContain('0.900')            // the score, derived
    expect(t).toMatch(/rank\s*1\s*of\s*3/)  // rank of N — the context that makes the score legible
    expect(t).toMatch(/0\.400.?0\.900/)     // min–max range present
    expect(t).toMatch(/median 0\.700/)      // median of [0.4,0.7,0.9]
    // the driver feature (largest |β·x| = feature 4, membrane-proximal) surfaces, framed about the model
    expect(t).toContain('membrane-proximal confidence')
    expect(t).not.toMatch(/epitope|promising|likely to work|probability/i)  // dec 6 boundaries
  })

  it('ranked + labelled: shows BOTH the in-fit score and the out-of-sample LOO percentile (dec 4)', () => {
    const { container } = view({ accession: 'A-ERBB2', gene: 'ERBB2', mean_plddt: 82, disposition: 'ranked' })
    const t = container.textContent
    expect(t).toContain('0.700')                       // the in-fit score
    expect(t).toMatch(/not a prediction about it/)     // the distinction, in plain language
    expect(t).toMatch(/leave-one-out percentile/)
    expect(t).toContain('0.710')                       // the out-of-sample LOO number
  })

  it('F-005 ambiguity travels with the attributions, boundary intact (dec 3)', () => {
    const { container } = view({ accession: 'A-TOP', gene: 'TOP1', mean_plddt: 70, disposition: 'ranked' })
    const tip = [...container.querySelectorAll('[role="tooltip"]')].map((n) => n.textContent).join(' ')
    expect(tip).toMatch(/not supported/)               // the claim boundary — present, not trimmed
    expect(tip).toMatch(/order-versus-disorder/)
  })

  it('every no-score state renders a REASON, never a blank or bare em-dash (dec 1)', () => {
    const cases = [
      [{ accession: 'A-X', gene: 'IGF2R', mean_plddt: null, disposition: 'held_out' }, /attempted, but did not complete/],
      [{ accession: 'A-X', gene: 'LOW', mean_plddt: 40, disposition: 'ranked' }, /under 50.*floor/s],
      [{ accession: 'A-X', gene: 'HELD', mean_plddt: 58, disposition: 'held_out' }, /held out of the ranking, not scored low/],
      [{ accession: 'A-GHOST', gene: 'GHOST', mean_plddt: 70, disposition: 'ranked' }, /reason not determined/],
    ]
    for (const [detail, re] of cases) {
      const { container, unmount } = view(detail)
      const t = container.textContent
      expect(t).toMatch(/No score/)
      expect(t).toMatch(re)
      expect(t.trim()).not.toMatch(/^Scorer result—?$/)  // never just a heading + dash
      unmount()
    }
  })

  it('Constraint-A: no live production literal is typed into the panel', () => {
    const { container } = view({ accession: 'A-TOP', gene: 'TOP1', mean_plddt: 70, disposition: 'ranked' })
    const t = container.textContent
    for (const lit of ['0.116', '0.220', '0.285', '0.607', 'of 56']) expect(t).not.toContain(lit)
  })
})
