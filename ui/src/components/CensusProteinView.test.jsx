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
    // ⚠ the scope limit is stated, and it is stated as a limit of the SOURCE
    expect(await screen.findByText(/covers the 82 ranked targets only/i)).toBeInTheDocument()
    expect(screen.getByText(/not a statement about this protein/i)).toBeInTheDocument()
  })

  // ⚠⚠ THE OWNER'S RULING: the section a reader reads for cancer associations must be the one that
  // has data. Before this, "Cancer connection" (full) sat immediately above "Cancer associations"
  // (empty for every census protein), and the empty heading was the one readers stopped at.
  it('heads the HPA panel as the cancer-associations section', async () => {
    view()
    const heads = (await screen.findAllByRole('heading')).map((h) => h.textContent)
    expect(heads).toContain('Cancer associations')
    // ⚠ and there is no SECOND, empty cancer heading beneath it
    expect(heads.filter((h) => /cancer/i.test(h))).toHaveLength(1)
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

describe('the cohort ceiling must not leak onto a census page (F-038)', () => {
  // ⚠⚠ The census max is 89.25 and six rows exceed the cohort's 84.23. Printing "cohort max 84.23"
  // beside a 89.25 structure states another population's ceiling — one this protein beats.
  it('never shows the cohort maximum on a census protein page', async () => {
    vi.mocked(getCensusDetail).mockResolvedValue({ ...DETAIL, mean_plddt: 89.25 })
    view()
    await screen.findByRole('heading', { name: 'SLC5A10' })
    expect(screen.queryByText(/84\.23/)).not.toBeInTheDocument()
    expect(screen.queryByText(/cohort max/i)).not.toBeInTheDocument()
  })

  it('says instead that the cohort ceiling does not describe the census', async () => {
    vi.mocked(getCensusDetail).mockResolvedValue({ ...DETAIL, mean_plddt: 89.25 })
    view()
    expect(await screen.findByText(/does not describe the census/i)).toBeInTheDocument()
  })

  // ⚠ And no census maximum is quoted either — it moves every tranche, so a number baked into the
  // page would go stale in silence.
  it('quotes no census maximum, which would go stale each tranche', async () => {
    vi.mocked(getCensusDetail).mockResolvedValue({ ...DETAIL, mean_plddt: 89.25 })
    view()
    await screen.findByRole('heading', { name: 'SLC5A10' })
    expect(screen.queryByText(/89\.25 is the highest|census max/i)).not.toBeInTheDocument()
  })
})

// ── the structural profile ON THE BASEBALL CARD (D-079 amendment 1, ruled by amendment 2) ──
//
// ⚠⚠ THE PROFILE REACHES THIS PAGE THROUGH `CensusDetail`, WHICH IS EMBEDDED HERE. That is a real
// dependency and an invisible one: nothing else renders `CensusDetail`, so if it is ever un-embedded
// or the block stops being threaded through, the profile disappears from the only page that shows
// the protein in 3D — and no test of `CensusDetail` alone would notice. These pin it to the CARD.
const BLOCK = {
  kind: 'structural_profile', status: 'computed', structural_profile: 0.1876, refusal: null,
  out_of_range_features: [],
  mount_preconditions: ['unlabelled — there is no leave-one-out here.', 'not a probability — F-006.'],
  provenance: 'run 2 (scorer_version 91e646e4a289)',
  bar: 'cohort observed min-max. Not p05-p95; not +/-3 sd.',
  band_context: { cohort_fitted_min: 0.116, cohort_fitted_max: 0.285,
    note: 'This axis does not separate targets by much.' },
  support_used: {},
}

describe('CensusProteinView — the structural profile on the 3D page', () => {
  it('renders the profile on the SAME page as the structure viewer', async () => {
    vi.mocked(getCensusDetail).mockResolvedValue({ ...DETAIL, structural_profile_block: BLOCK })
    const { container } = view()
    await waitFor(() => expect(screen.getByTestId('structure')).toBeTruthy())
    expect(container.textContent).toMatch(/Structural profile/)
    expect(container.textContent).toMatch(/0\.1876/)
  })

  it('places the profile AFTER the "not scored, not ranked" statement (placement is the ruling)', async () => {
    vi.mocked(getCensusDetail).mockResolvedValue({ ...DETAIL, structural_profile_block: BLOCK })
    const { container } = view()
    await waitFor(() => expect(container.textContent).toMatch(/Structural profile/))
    const t = container.textContent
    // ⚠ The reader is told the protein is unscored BEFORE being shown a structure-derived number.
    expect(t.indexOf('Not scored')).toBeGreaterThan(-1)
    expect(t.indexOf('Not scored')).toBeLessThan(t.indexOf('Structural profile'))
  })

  it('still says "not scored, not ranked" WITH the profile present — the profile did not replace it', async () => {
    vi.mocked(getCensusDetail).mockResolvedValue({ ...DETAIL, structural_profile_block: BLOCK })
    const { container } = view()
    await waitFor(() => expect(container.textContent).toMatch(/Structural profile/))
    expect(container.textContent).toMatch(/Not scored, not ranked/)
    expect(container.textContent).toMatch(/not a score and not a rank/i)
  })

  it('carries no scorer panel even now (D-089) — the profile is not it under another name', async () => {
    vi.mocked(getCensusDetail).mockResolvedValue({ ...DETAIL, structural_profile_block: BLOCK })
    const { container } = view()
    await waitFor(() => expect(container.textContent).toMatch(/Structural profile/))
    expect(container.textContent).not.toMatch(/Scorer result/)
    expect(container.textContent).not.toMatch(/What moved this score/)
  })

  it('a page whose API response carries no block renders no empty panel', async () => {
    vi.mocked(getCensusDetail).mockResolvedValue(DETAIL)   // no structural_profile_block at all
    const { container } = view()
    await waitFor(() => expect(screen.getByTestId('structure')).toBeTruthy())
    expect(container.textContent).not.toMatch(/Structural profile/)
  })
})
