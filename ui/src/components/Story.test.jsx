// D-051 Constraint A: the Story's numbers derive from the payload, never literals. Distinctive
// fixture values (4 folded, max 88.00, 3-of-5) that cannot coincide with today's live cohort, so a
// green means the render tracked the payload — and the negative test reddens if a real number is
// ever pasted into the prose.
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../api.js', () => ({ listAnalyses: vi.fn(), getCoverage: vi.fn() }))
import { listAnalyses, getCoverage } from '../api.js'
import Story from './Story.jsx'

const ANALYSES = [
  { mean_plddt: 40.0 }, { mean_plddt: 55.0 }, { mean_plddt: 70.0 }, { mean_plddt: 88.0 },
  { mean_plddt: null }, // unfolded — excluded from the folded count
]
const COVERAGE = {
  coverage: { denominator: 5 },
  rows: [
    { disposition: 'ranked', fold_status: 'folded', gene: 'AAA' },
    { disposition: 'ranked', fold_status: 'folded', gene: 'BBB' },
    { disposition: 'ranked', fold_status: 'folded', gene: 'CCC' },
    { disposition: 'held_out', fold_status: 'failed', gene: 'FAKEIGF' },
    { disposition: 'excluded', fold_status: 'not_folded', gene: 'FAKEBIG' },
  ],
}
const LIVE_LITERALS = ['79', '82', '84.23', '30.68', '29%']
const renderStory = () => render(<MemoryRouter><Story /></MemoryRouter>)
beforeEach(() => vi.clearAllMocks())

describe('Story — derived numbers, never literals (D-051 / Constraint A)', () => {
  it('renders counts, range, and non-folded targets from the payload', async () => {
    listAnalyses.mockResolvedValue(ANALYSES); getCoverage.mockResolvedValue(COVERAGE)
    const { container } = renderStory()
    await waitFor(() => expect(container.textContent).toMatch(/4 targets folded/))
    expect(container.textContent).toMatch(/3 of them ranked-and-folded of 5/)
    expect(container.textContent).toContain('88.00')
    expect(container.textContent).toContain('FAKEIGF')
    expect(container.textContent).toContain('FAKEBIG')
  })

  it('does NOT hardcode any live cohort literal', async () => {
    listAnalyses.mockResolvedValue(ANALYSES); getCoverage.mockResolvedValue(COVERAGE)
    const { container } = renderStory()
    await waitFor(() => expect(container.textContent).toMatch(/4 targets folded/))
    for (const lit of LIVE_LITERALS) expect(container.textContent).not.toContain(lit)
  })

  it('names ESMFold and states we ran it', async () => {
    listAnalyses.mockResolvedValue(ANALYSES); getCoverage.mockResolvedValue(COVERAGE)
    const { container } = renderStory()
    await waitFor(() => expect(container.textContent).toMatch(/4 targets folded/))
    expect(container.textContent).toContain('ESMFold')
    expect(container.textContent.toLowerCase()).toContain('we ran the neural network ourselves')
  })

  it('links to /targets', async () => {
    listAnalyses.mockResolvedValue(ANALYSES); getCoverage.mockResolvedValue(COVERAGE)
    renderStory()
    const link = await screen.findByRole('link', { name: /folded targets/i })
    expect(link).toHaveAttribute('href', '/targets')
  })

  it('renders without numbers, not crashing, when both fetches reject', async () => {
    listAnalyses.mockRejectedValue(new Error('down')); getCoverage.mockRejectedValue(new Error('down'))
    const { container } = renderStory()
    await waitFor(() => expect(container.textContent).toContain('ESMFold'))
    for (const lit of LIVE_LITERALS) expect(container.textContent).not.toContain(lit)
    expect(container.textContent).toContain('See the folded targets')
  })
})
