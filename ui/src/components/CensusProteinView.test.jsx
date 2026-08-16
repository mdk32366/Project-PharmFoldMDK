import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('../api.js', () => ({
  getCensusDetail: vi.fn(),
  getPlddt: vi.fn(),
  structureUrl: (id) => `/api/analyses/${id}/structure`,
}))
// ⚠ 3Dmol is a large dynamic import and irrelevant to what this page must SAY.
vi.mock('./StructureViewer.jsx', () => ({ default: () => <div data-testid="structure" /> }))

import { getCensusDetail, getPlddt } from '../api.js'
import CensusProteinView from './CensusProteinView.jsx'

const DETAIL = {
  id: 42, accession: 'A0PJK1', gene: 'SLC5A10', label: 'Sodium/mannose cotransporter',
  tranche: 1, span_aa: 43, span_start: 222, span_end: 264, full_length: 596,
  mean_plddt: 54.14, topology: 'intermittent', segment_count: 7,
  extracellular_total_aa: 135, discarded_aa: 92, segments: '1-15;94-99',
  span_definition: 'v2-ruled-vocabulary-2026-08-07', scored: false,
  not_scored_reason: 'D-079 decision 1 — no census row is scored',
  cancer_associations: { status: 'not_covered', hits: [], source: 'Kathad et al. 2024',
    coverage_note: 'the association source covers the 82 cohort targets only' },
}

const view = (id = 42) => render(<MemoryRouter><CensusProteinView id={id} /></MemoryRouter>)

beforeEach(() => {
  vi.mocked(getCensusDetail).mockResolvedValue(DETAIL)
  vi.mocked(getPlddt).mockResolvedValue([50, 60, 70])
})

describe('CensusProteinView', () => {
  it('is a page per protein: identity, structure and measured properties', async () => {
    view()
    expect(await screen.findByRole('heading', { name: 'SLC5A10' })).toBeInTheDocument()
    // ⚠ ONCE. The page header and the embedded panel both used to print it.
    expect(screen.getAllByText(/A0PJK1/)).toHaveLength(1)
    expect(screen.getByTestId('structure')).toBeInTheDocument()
  })

  // ⚠⚠ THE ONE THAT MATTERS. A census protein given a page that looks like a ranked target's page
  // is how a reader concludes it IS one. TargetView carries a scorer panel; this must not, and the
  // absence must not be left to imply itself.
  it('says it is unscored at the top, and carries no scorer panel', async () => {
    view()
    await screen.findByRole('heading', { name: 'SLC5A10' })
    expect(screen.getByText(/Not scored, not ranked\./)).toBeInTheDocument()
    expect(screen.getByText(/not comparable to the ranked 82/i)).toBeInTheDocument()
    // ⚠ A real absence check: TargetView's scorer panel must not appear here.
    expect(document.querySelector('.scorer-panel')).toBeNull()
    expect(document.querySelector('.target-scorer')).toBeNull()
  })

  it('carries the F-037 topology warning on the page, not only in the list', async () => {
    view()
    expect(await screen.findByText(/7 separate extracellular segments/i)).toBeInTheDocument()
    expect(screen.getByText(/92 aa across the remaining 6 segments were not folded/i)).toBeInTheDocument()
  })

  it('says associations are not covered rather than absent', async () => {
    view()
    expect(await screen.findByText(/Not covered by the association source/i)).toBeInTheDocument()
  })

  // ⚠ A page whose plddt.json is missing must still render its identity and reasons.
  it('stands when the per-residue pLDDT is unavailable', async () => {
    vi.mocked(getPlddt).mockRejectedValue(new Error('404'))
    view()
    expect(await screen.findByRole('heading', { name: 'SLC5A10' })).toBeInTheDocument()
    expect(screen.getByText(/7 separate extracellular segments/i)).toBeInTheDocument()
  })

  // ⚠ A cohort id 404s here by design (D-081). The error must point at the right surface rather
  // than leaving a reader thinking the protein does not exist.
  it('points a cohort id at Targets instead of dead-ending', async () => {
    vi.mocked(getCensusDetail).mockRejectedValue(new Error('unknown census analysis'))
    view(1)
    expect(await screen.findByText(/Could not load census protein 1/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Targets/ })).toHaveAttribute('href', '/targets')
  })

  it('offers a way back to the census', async () => {
    view()
    await screen.findByRole('heading', { name: 'SLC5A10' })
    await waitFor(() =>
      expect(screen.getByRole('link', { name: /the wider protein census/i }))
        .toHaveAttribute('href', '/census'))
  })

  it('has no Close button — the panel IS the page here', async () => {
    view()
    await screen.findByRole('heading', { name: 'SLC5A10' })
    expect(screen.queryByRole('button', { name: /close/i })).not.toBeInTheDocument()
  })
})
