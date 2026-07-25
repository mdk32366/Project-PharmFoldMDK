// D-050: AdcContext's cohort statistics must be DERIVED from /api/analyses, not hardcoded.
// The stale literals (42 folded / 34.78 to 81.40 / 45% below 60) rotted when the cohort grew
// 42->79 (D-045/D-049). These tests pin derivation: a fixture payload -> the rendered numbers
// match the payload, so a future cohort change can't silently reintroduce a stale literal.
import { render, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../api.js', () => ({ listAnalyses: vi.fn() }))
import { listAnalyses } from '../api.js'
import AdcContext from './AdcContext.jsx'

// DISTINCTIVE numbers that cannot coincide with the stale literals (42 / 34.78 / 81.40 / 45%):
// 4 folded, range 40.00-88.00, 2 of 4 = 50% below 60, one unfolded (null, excluded from stats).
const FIXTURE = [
  { id: 1, gene: 'AA', mean_plddt: 40.0, disposition: 'ranked' },
  { id: 2, gene: 'BB', mean_plddt: 55.0, disposition: 'ranked' },
  { id: 3, gene: 'CC', mean_plddt: 70.0, disposition: 'ranked' },
  { id: 4, gene: 'DD', mean_plddt: 88.0, disposition: 'held_out' },
  { id: 5, gene: 'EE', mean_plddt: null, disposition: 'held_out' }, // unfolded -> not a folded target
]

const renderAdc = () => render(<MemoryRouter><AdcContext /></MemoryRouter>)

beforeEach(() => vi.clearAllMocks())

describe('AdcContext — cohort stats derived from /api/analyses, not hardcoded (D-050)', () => {
  it('renders folded count / pLDDT range / below-60 fraction from the payload', async () => {
    listAnalyses.mockResolvedValue(FIXTURE)
    const { container } = renderAdc()
    await waitFor(() => expect(container.textContent).toMatch(/4 folded targets/))
    expect(container.textContent).toMatch(/40\.00 to 88\.00/)
    expect(container.textContent).toMatch(/50% fall below 60/)
  })

  it('does NOT render the stale 42-fold-era literals', async () => {
    listAnalyses.mockResolvedValue(FIXTURE)
    const { container } = renderAdc()
    await waitFor(() => expect(container.textContent).toMatch(/4 folded targets/))
    expect(container.textContent).not.toMatch(/42 folded targets/)
    expect(container.textContent).not.toMatch(/34\.78 to 81\.40/)
    expect(container.textContent).not.toMatch(/45% fall below 60/)
  })
})
