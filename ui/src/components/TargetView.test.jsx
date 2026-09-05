import { render, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'

// D-068 fix / D-069: a failed fold (IGF2R: analysis row exists, but no structure and no plddt.json)
// must render its page with the honest "not folded" scorer panel — NEVER error the whole page on the
// pLDDT 404, which reads as a broken app for the one target whose truth is the project's best sentence.
// Fold-dependent fetches degrade INDEPENDENTLY; only getAnalysis is page-critical.
vi.mock('../api.js', () => ({
  getAnalysis: vi.fn(),
  getPlddt: vi.fn(),
  getRanking: vi.fn(),
}))
vi.mock('./StructureViewer.jsx', () => ({
  default: (props) => (
    <div data-testid="viewer-stub" data-assembled={String(Boolean(props.assembled))} />
  ),
}))
vi.mock('./CancerAssociations.jsx', () => ({ default: () => <div data-testid="assoc-stub" /> }))
import { getAnalysis, getPlddt, getRanking } from '../api.js'
import TargetView from './TargetView.jsx'

const FAILED_FOLD = {
  id: 57, gene: 'IGF2R', accession: 'P11717', label: 'held out',
  mean_plddt: null, disposition: 'held_out', boundary_method: 'whole', fold_provenance: {},
}
const RANKING = { result_status: 'complete', result: { plddt_floor: 50, distribution: [] }, rows: [] }

beforeEach(() => vi.clearAllMocks())

describe('TargetView resilience (D-068 fix)', () => {
  it('a failed fold renders the not-folded panel, not a page error, when pLDDT 404s', async () => {
    getAnalysis.mockResolvedValue(FAILED_FOLD)
    getPlddt.mockRejectedValue(new Error('/api/analyses/57/plddt -> HTTP 404'))  // no plddt.json
    getRanking.mockResolvedValue(RANKING)
    const { container } = render(<MemoryRouter><TargetView id={57} /></MemoryRouter>)
    await waitFor(() => expect(container.textContent).toMatch(/Scorer result/))
    const t = container.textContent
    // the page STANDS — the pLDDT rejection did not take it down
    expect(t).not.toMatch(/Could not load target/)
    // and the not-folded state renders its reason (dec 1), never a blank
    expect(t).toMatch(/No score/)
    expect(t).toMatch(/attempted, but did not complete/)
    // the header still renders from the analysis record
    expect(t).toContain('IGF2R')
  })

  it('D-118: a stitched detail forwards assembled=true so the 3D banner cannot be skipped', async () => {
    getAnalysis.mockResolvedValue({
      ...FAILED_FOLD, id: 2817, gene: 'TENM3', accession: 'Q9P273',
      mean_plddt: 61.07, assembled: true, hold48_kind: 'parent',
    })
    getPlddt.mockResolvedValue([61])
    getRanking.mockResolvedValue(RANKING)
    const { container } = render(<MemoryRouter><TargetView id={2817} /></MemoryRouter>)
    await waitFor(() => expect(container.querySelector('[data-testid="viewer-stub"]')).toBeTruthy())
    expect(container.querySelector('[data-testid="viewer-stub"]').getAttribute('data-assembled'))
      .toBe('true')
  })

  it('a real page error (analysis itself 404s) still surfaces — resilience is not silence', async () => {
    getAnalysis.mockRejectedValue(new Error('/api/analyses/999 -> HTTP 404'))
    getPlddt.mockResolvedValue([])
    getRanking.mockResolvedValue(RANKING)
    const { container } = render(<MemoryRouter><TargetView id={999} /></MemoryRouter>)
    await waitFor(() => expect(container.textContent).toMatch(/Could not load target 999/))
  })
})
