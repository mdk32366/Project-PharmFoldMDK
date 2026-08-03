// F-009 — the UI must say the 82 is a COMPARATOR, not a census.
//
// The honesty gap: `/about` and `/scorer` both present the Kathad 82 as "the cohort" without stating
// it is an expression-and-selectivity *selected* comparator, and that clinically-validated ADC targets
// fall outside it. A reader is therefore left to assume the ranking speaks to the whole ADC target
// space. It re-orders a fixed comparator set — a different, smaller claim.
//
// ⚠ THE OVER-CLAIM GUARD IS THE LOAD-BEARING TEST (F-009 §3). The note indicts the COMPARATOR's
// completeness. It must never imply the scorer would have caught these targets, or ranks them highly.
// They are unfolded and unscored, and CD30/CD33 are attention-rich — the very confound D-075 exists to
// test. Claiming they validate the axis would pre-empt a sealed pre-registration with a story.
// Making that a denylist test rather than an editorial habit is the whole point.
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

vi.mock('../api.js', () => ({
  listAnalyses: vi.fn(),
  getCoverage: vi.fn(),
  getRanking: vi.fn(),
}))
import { listAnalyses, getCoverage, getRanking } from '../api.js'
import AdcContext from './AdcContext.jsx'
import ScorerView from './ScorerView.jsx'
import { HELDOUT_EXAMPLES } from '../heldoutExamples.js'

const ANALYSES = [
  { id: 1, gene: 'NECTIN4', accession: 'Q92729', mean_plddt: 77.26, tier: 'local', disposition: 'ranked' },
  { id: 2, gene: 'SDK1', accession: 'A7Z5N4', mean_plddt: 58.01, tier: 'rental', disposition: 'ranked' },
]

const COVERAGE = {
  coverage: { denominator: 82, ranked: 67, held_out: 13, excluded: 2 },
  rows: [
    { accession: 'Q92729', gene: 'NECTIN4', fold_status: 'folded', disposition: 'ranked' },
    { accession: 'A7Z5N4', gene: 'SDK1', fold_status: 'folded', disposition: 'ranked' },
  ],
}

const RANKING = {
  result_status: 'complete',
  run: { id: 2, scorer_version: '91e646e4a289' },
  result: {
    n_ranking_set: 56, n_fit_positives: 12, headto_reference_n: 12, plddt_floor: 50,
    spearman: -0.0483, spearman_n: 12, paper_published_count: 22,
    loo_status: 'complete', fulldata_status: 'converged', lambda_at_grid_edge: false,
    distribution: [{ symbol: 'NECTIN4', percentile: 0.848, lam: 31.6, converged: true }],
    nonconvergent: [], headto_structural: [0.62], headto_evidence: [0.75], excluded: [],
  },
  rows: [{ rank: 1, accession: 'Q92729', gene: 'NECTIN4', score: 0.285, attributions: [0, 0, 0, 0, 0, 0] }],
}

// Copy that would be an over-claim: implying the SCORER catches, ranks or is validated by these
// targets. F-009 §3 indicts the comparator's completeness only.
//
// ⚠ These patterns are deliberately SPECIFIC to the scorer/axis/ranking. A first draft used the
// broad `/proves? (the|our)/i`, which fired on shipped, CORRECT copy — "Enfortumab vedotin proves
// the *mechanism*" is a true statement about the drug, not a claim about our model. A denylist that
// catches honest text is worse than none: it trains you to loosen the guard or edit good prose to
// appease it. Precision here is what keeps the guard trustworthy.
const OVER_CLAIM = [
  /would have (caught|found|identified|surfaced|ranked)/i,
  /ranks? (them|these) highly/i,
  /our (method|model|scorer) (identifies|finds|catches)/i,
  /correctly prioriti[sz]/i,
  /validates? the (axis|scorer|method|ranking)/i,
  /prov(e|es|en) (the |our )?(axis|scorer|ranking|approach)/i,
  /\bshould have been included\b/i,
  /\bconfirms? (the|our) (axis|scorer|method|ranking)/i,
]

beforeEach(() => {
  listAnalyses.mockReset(); getCoverage.mockReset(); getRanking.mockReset()
  listAnalyses.mockResolvedValue(ANALYSES)
  getCoverage.mockResolvedValue(COVERAGE)
  getRanking.mockResolvedValue(RANKING)
})

const renderAbout = () => render(<MemoryRouter><AdcContext /></MemoryRouter>)
const renderScorer = () => render(<MemoryRouter><ScorerView /></MemoryRouter>)

describe('/about — the primary cohort-boundary paragraph', () => {
  it('states the 82 is a comparator/selected cohort, NOT a census of ADC targets', async () => {
    const { container } = renderAbout()
    await waitFor(() => expect(container.textContent).toMatch(/comparator|not a census/i))
    const text = container.textContent
    expect(text).toMatch(/comparator/i)
    expect(text).toMatch(/not a (complete )?census|not a complete/i)
  })

  it('names clinically-validated ADC targets that fall outside it, derived from the verified CSV', async () => {
    const { container } = renderAbout()
    await waitFor(() => expect(container.textContent).toMatch(/comparator/i))
    // Every example must render — and they come from heldoutExamples.js, which is drift-tested
    // against data/heldout_positives.csv, so no accession here is hand-typed.
    for (const e of HELDOUT_EXAMPLES) {
      expect(container.textContent, `${e.display} missing from /about`).toContain(e.display)
    }
    expect(container.textContent).toMatch(/brentuximab vedotin/i)
  })

  it('attributes their absence to the expression filter, not to being poor targets', async () => {
    const { container } = renderAbout()
    await waitFor(() => expect(container.textContent).toMatch(/comparator/i))
    expect(container.textContent).toMatch(/expression/i)
  })

  it('⚠ makes no over-claim about the scorer catching or endorsing them (F-009 §3)', async () => {
    const { container } = renderAbout()
    await waitFor(() => expect(container.textContent).toMatch(/comparator/i))
    for (const banned of OVER_CLAIM) {
      expect(container.textContent, `/about must not claim ${banned}`).not.toMatch(banned)
    }
  })
})

describe('/scorer — the §A cascade qualifier', () => {
  it('qualifies the cohort line as a comparator, not a census', async () => {
    const { container } = renderScorer()
    await waitFor(() => expect(container.textContent).toMatch(/From the cohort to the fit set/i))
    expect(container.textContent).toMatch(/comparator/i)
    expect(container.textContent).toMatch(/not a census/i)
  })

  it('points at About rather than restating the paragraph (single source of the framing)', async () => {
    renderScorer()
    await waitFor(() => expect(screen.getByText(/From the cohort to the fit set/i)).toBeInTheDocument())
    const link = screen.getAllByRole('link').find((a) => /about/i.test(a.getAttribute('href') || ''))
    expect(link, 'the scorer qualifier should link to /about').toBeTruthy()
  })

  it('⚠ makes no over-claim there either', async () => {
    const { container } = renderScorer()
    await waitFor(() => expect(container.textContent).toMatch(/comparator/i))
    for (const banned of OVER_CLAIM) {
      expect(container.textContent, `/scorer must not claim ${banned}`).not.toMatch(banned)
    }
  })

  it('does not restate the four example targets — the framing lives in one place', async () => {
    const { container } = renderScorer()
    await waitFor(() => expect(container.textContent).toMatch(/comparator/i))
    // Duplicating the examples would give the claim two homes that can drift apart.
    expect(container.textContent).not.toMatch(/brentuximab/i)
  })
})

describe('the existing honesty layer is untouched', () => {
  it('/about still carries the "find me more NECTIN4s" confound caveat', async () => {
    const { container } = renderAbout()
    await waitFor(() => expect(container.textContent).toMatch(/comparator/i))
    expect(container.textContent).toMatch(/NECTIN4s/)
  })
})
