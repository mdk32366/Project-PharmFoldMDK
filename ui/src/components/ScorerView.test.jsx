import { render, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../api.js', () => ({
  getCensusSummary: vi.fn(), getRanking: vi.fn(), getCoverage: vi.fn() }))
import { getRanking, getCoverage } from '../api.js'
import ScorerView from './ScorerView.jsx'

// Distinctive fixture numbers that cannot coincide with the live run (F-004). The live literals
// (0.607 median, -0.0483 Spearman, 56 rankable, 12 positives, 22 published, N=8 head-to-head) must
// NEVER be typed into the component — every one is derived from the payload (Constraint-A, D-062).
const RANKING = {
  result_status: 'complete',
  run: { id: 999, target_list_version: 'fixture', scorer_version: 'fixture-sv' },
  result: {
    loo_status: 'complete', fulldata_status: 'converged',
    status_detail: 'all pre-registered statistics produced',
    spearman: 0.309, spearman_n: 5,
    n_ranking_set: 7, n_fit_positives: 3, headto_reference_n: 5,
    plddt_floor: 50,
    distribution: [
      { symbol: 'ERBB2', percentile: 0.71 },
      { symbol: 'NECTIN4', percentile: 0.63 },
      { symbol: 'EGFR', percentile: 0.44 },
    ],
    nonconvergent: [],
    headto_structural: [0.71, 0.44],
    headto_evidence: [0.75, 0.25],
    excluded: [['CXCR5', 'below_floor'], ['MSLN', 'held_out'], ['MUC16', 'not_folded']],
    paper_published_count: 99,          // distinctive; the live 22 must not be typed
  },
  rows: [
    { rank: 1, accession: 'A1', gene: 'ERBB2', score: 0.91, attributions: [0.1, -0.2, 0.3, 0.4, -0.5, 0.6] },
    { rank: 2, accession: 'A2', gene: 'NECTIN4', score: 0.63, attributions: [0.1, -0.2, 0.3, 0.4, -0.5, 0.6] },
    { rank: 3, accession: 'A3', gene: 'EGFR', score: 0.44, attributions: [0.1, -0.2, 0.3, 0.4, -0.5, 0.6] },
  ],
}
const COVERAGE = {
  coverage: { denominator: 9, ranked: 5, held_out: 2, excluded: 1, unmeasured_tier: 0, no_topology: 0 },
  rows: [{ fold_status: 'folded', disposition: 'ranked' }, { fold_status: 'folded', disposition: 'ranked' }],
}

const renderView = () => render(<MemoryRouter><ScorerView /></MemoryRouter>)
beforeEach(() => vi.clearAllMocks())

describe('ScorerView', () => {
  it('renders the distribution, head-to-head, Spearman and ranking table from the payload', async () => {
    getRanking.mockResolvedValue(RANKING)
    getCoverage.mockResolvedValue(COVERAGE)
    const { container } = renderView()
    await waitFor(() => expect(container.textContent).toMatch(/The result/))
    const t = container.textContent
    // distribution median of [0.44,0.63,0.71] = 0.630; Spearman 0.309; head-to-head N = 2
    expect(t).toContain('0.630')
    expect(t).toContain('0.309')
    expect(t).toMatch(/N = 2/)
    // 3 curated positives vs the served 99 published; 7 rankable
    expect(t).toMatch(/3 curated Group B/)
    expect(t).toContain('99')
    expect(t).toMatch(/7\b/)
    // the three named antigens show present; ranking table rows in rank order
    expect(t).toMatch(/ERBB2 ✓ present/)
    expect(t).toMatch(/NECTIN4 ✓ present/)
    // the excluded set with its reasons
    expect(t).toMatch(/CXCR5 — below_floor/)
    expect(t).toMatch(/MSLN — held_out/)
    expect(t).toMatch(/27 unique stitched parents/)
    expect(t).toMatch(/not in this ranking \(D-109\)/)
  })

  it('does NOT hardcode any live literal — every number derives from the payload', async () => {
    getRanking.mockResolvedValue(RANKING)
    getCoverage.mockResolvedValue(COVERAGE)
    const { container } = renderView()
    await waitFor(() => expect(container.textContent).toMatch(/0\.309/))
    const t = container.textContent
    // D-066 §4 extends the absence set to the F-006 numbers and the 67/56 collision values
    for (const lit of ['0.607', '-0.0483', '56', '67', '0.116', '0.220', '0.285']) expect(t).not.toContain(lit)
    // 12 and 8 collide with the section-C dates; assert their live composites are absent instead
    expect(t).not.toMatch(/12 curated Group B/)
    expect(t).not.toMatch(/N = 8/)
  })

  it('names both negative outcomes and which fired, and carries caveat (b) WITH the result', async () => {
    getRanking.mockResolvedValue(RANKING)
    getCoverage.mockResolvedValue(COVERAGE)
    const { container } = renderView()
    await waitFor(() => expect(container.textContent).toMatch(/First negative outcome/))
    const t = container.textContent
    expect(t).toMatch(/First negative outcome — FIRES/)
    expect(t).toMatch(/Second negative outcome — DOES NOT FIRE/)
    // the mean/median reversal is rendered (both summaries present), not smoothed
    expect(t).toMatch(/mean/)
    expect(t).toMatch(/median/)
    // caveat (b) now tested (F-005): the specific attention mechanism is NOT supported, with the result
    expect(t).toMatch(/Now tested, not open/)
    expect(t).toMatch(/not supported/)
    expect(t).toMatch(/order-versus-disorder/)
  })

  it('uses no significance language (claim boundary, pinned)', async () => {
    getRanking.mockResolvedValue(RANKING)
    getCoverage.mockResolvedValue(COVERAGE)
    const { container } = renderView()
    await waitFor(() => expect(container.textContent).toMatch(/The result/))
    expect(container.textContent).not.toMatch(/significant|p-value|p <|demonstrates/i)
  })

  it('renders the structural-score tooltip with its claim boundary in the DOM (truncation guard)', async () => {
    getRanking.mockResolvedValue(RANKING)
    getCoverage.mockResolvedValue(COVERAGE)
    const { container } = renderView()
    await waitFor(() => expect(container.textContent).toMatch(/structural score/))
    // the definition renders in a role="tooltip" node (Term), and its FINAL sentence — the claim
    // boundary — must be present in the DOM, not trimmed (D-055 amendment §2, the key test)
    const tips = [...container.querySelectorAll('[role="tooltip"]')].map((n) => n.textContent)
    const structural = tips.find((t) => t.includes('four of shape and size, two of how confident'))
    expect(structural).toBeTruthy()
    expect(structural).toMatch(/not a prediction that a drug will work/)
    expect(structural).toMatch(/how much of the target a tumour makes/)   // the final sentence, intact
  })

  it('every definition is reachable by keyboard/tap, not hover alone', async () => {
    getRanking.mockResolvedValue(RANKING)
    getCoverage.mockResolvedValue(COVERAGE)
    const { container } = renderView()
    await waitFor(() => expect(container.textContent).toMatch(/structural score/))
    // the trigger is a real focusable <button>, the definition a role="tooltip" linked by aria
    const trigger = [...container.querySelectorAll('button.term-trigger')]
      .find((b) => b.textContent.includes('structural score'))
    expect(trigger).toBeTruthy()
    expect(trigger.getAttribute('aria-describedby')).toBeTruthy()
  })

  it('when stacked, the coverage line precedes its table and caveat (b) follows the result (DOM order)', async () => {
    getRanking.mockResolvedValue(RANKING)
    getCoverage.mockResolvedValue(COVERAGE)
    const { container } = renderView()
    await waitFor(() => expect(container.textContent).toMatch(/The result/))
    const t = container.textContent
    // caveat (b) comes after the distribution/Spearman (it is the last thing in the result section)
    expect(t.indexOf('leave-one-out distribution')).toBeLessThan(t.indexOf('Now tested, not open'))
    // coverage box → reconciliation → table: the coverage line stays with its table even stacked
    // (D-066 §4). Asserted on DOM position, not text order, so it is layout-proof.
    const box = container.querySelector('.coverage-line')
    const recon = container.querySelector('.ranking-reconciliation')
    const table = container.querySelector('.ranking-table')
    const before = (a, b) => Boolean(a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING)
    expect(before(box, recon)).toBe(true)
    expect(before(recon, table)).toBe(true)
    // the deferred-columns note moved OUT of the ranking column into section D (left), so it now
    // precedes the E heading in source order (D-066 §2)
    expect(t.indexOf('Deferred columns')).toBeLessThan(t.indexOf('E · The ranking table'))
  })

  it('reconciles 67 → 56 immediately above the table, every number derived (D-066 dec 2)', async () => {
    getRanking.mockResolvedValue(RANKING)
    getCoverage.mockResolvedValue(COVERAGE)
    const { container } = renderView()
    await waitFor(() => expect(container.textContent).toMatch(/rankable after the pLDDT-50 floor/))
    const recon = container.querySelector('.ranking-reconciliation').textContent
    // rankedFolded from coverage.rows (2 folded∧ranked), ranking set 7, floor 50 — none typed
    expect(recon).toMatch(/2 ranked/)
    expect(recon).toMatch(/7 rankable after the pLDDT-50 floor/)
    expect(recon).toMatch(/the table below shows those 7/)
    // A2 (D-066 amendment): 'ranked' is no longer used in the membership sense decision 4 forbids
    expect(recon).not.toMatch(/ranked below/)
  })

  it('the Score column carries the non-calibration boundary in its tooltip, derived, distinct from `structural score`', async () => {
    getRanking.mockResolvedValue(RANKING)
    getCoverage.mockResolvedValue(COVERAGE)
    const { container } = renderView()
    await waitFor(() => expect(container.textContent).toMatch(/The result/))
    // a focusable Score trigger with its OWN tooltip, separate from the structural-score Term
    const trigger = [...container.querySelectorAll('button.term-trigger')].find((b) => b.textContent.trim() === 'Score')
    expect(trigger).toBeTruthy()
    expect(trigger.getAttribute('aria-describedby')).toBe('gloss-score-column')
    const def = container.querySelector('#gloss-score-column')
    expect(def.getAttribute('role')).toBe('tooltip')
    // the non-calibration sentence is a claim boundary — present in the DOM, not trimmed (F-006 Finding 3)
    expect(def.textContent).toMatch(/not a calibrated probability/)
    expect(def.textContent).toMatch(/not a percentage chance/)
    // the F-005 pLDDT-driven note lives here now, not as a standalone intro paragraph (D-066 §2)
    expect(def.textContent).toMatch(/pLDDT-driven \(F-005\)/)
    expect(container.querySelector('.ranking-intro')).toBeNull()
    // derived distribution: fixture scores [0.91,0.63,0.44] -> span 0.440–0.910, median 0.630
    expect(def.textContent).toMatch(/0\.440/)
    expect(def.textContent).toMatch(/0\.910/)
    expect(def.textContent).toMatch(/median 0\.630/)
    // labelled fraction 3/7 derived (n_fit_positives / n_ranking_set), never the literal 0.214
    expect(def.textContent).toMatch(/3\/7/)
    expect(def.textContent).not.toContain('0.214')
  })

  it('renders the not_run state', async () => {
    getRanking.mockResolvedValue({ result_status: 'not_run', run: null, result: null, rows: [] })
    getCoverage.mockResolvedValue(COVERAGE)
    const { container } = renderView()
    await waitFor(() => expect(container.textContent).toMatch(/No pre-registered result/))
  })

  it('renders the raised state with its reason', async () => {
    getRanking.mockResolvedValue({
      result_status: 'raised',
      run: { id: 3, scorer_version: 'x' },
      result: { status_detail: 'full-data fit did not converge at lam=0.001' },
      rows: [],
    })
    getCoverage.mockResolvedValue(COVERAGE)
    const { container } = renderView()
    await waitFor(() => expect(container.textContent).toMatch(/produced no distribution/))
    expect(container.textContent).toMatch(/did not converge/)
  })

  it('renders the partial state with a banner and the available sections', async () => {
    getRanking.mockResolvedValue({ ...RANKING, result_status: 'partial' })
    getCoverage.mockResolvedValue(COVERAGE)
    const { container } = renderView()
    await waitFor(() => expect(container.textContent).toMatch(/Partial result/))
    expect(container.textContent).toContain('0.630')   // the distribution still renders
  })
})
