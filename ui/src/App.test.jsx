// D-051: the nav restructure to five surfaces is a behaviour change and nothing asserted what `/`
// renders before now. `/` → Story, `/targets` → the list, `/target/:id` → the target view. api.js
// is mocked (Story + TargetList fetch on mount); TargetView is stubbed so this test isolates
// ROUTING from that component's 3Dmol/jsdom rendering (its own untested-component debt, D-046 §5).
import { render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('./api.js', () => ({
  getCensusSummary: vi.fn(),
  listAnalyses: vi.fn().mockResolvedValue([]),
  getCoverage: vi.fn().mockResolvedValue({ coverage: { denominator: 0 }, rows: [] }),
  getAnalysis: vi.fn().mockResolvedValue({}),
  getPlddt: vi.fn().mockResolvedValue([]),
  listAdcs: vi.fn().mockResolvedValue({ adcs: [] }),
  getAdc: vi.fn().mockResolvedValue({}),
  structureUrl: (id) => `/api/analyses/${id}/structure`,
}))
vi.mock('./components/TargetView.jsx', () => ({
  default: ({ id }) => <div>STUB target view for {String(id)}</div>,
}))
vi.mock('./components/AdcsView.jsx', () => ({
  default: () => <div>STUB adcs index</div>,
}))
vi.mock('./components/AdcCard.jsx', () => ({
  default: ({ id }) => <div>STUB adc card for {String(id)}</div>,
}))

import App from './App.jsx'

const renderAt = (path) => render(<MemoryRouter initialEntries={[path]}><App /></MemoryRouter>)
const STORY = /We folded a cohort of ADC targets with ESMFold/
beforeEach(() => vi.clearAllMocks())

describe('App — five-surface nav (D-051)', () => {
  it('/ renders the Story, not the target list', async () => {
    const { container } = renderAt('/')
    await waitFor(() => expect(container.textContent).toMatch(STORY))
  })

  it('/targets renders the target list, not the Story', async () => {
    const { container } = renderAt('/targets')
    // ⚠ was /folded targets/i — the copy this test pinned was the DEFECT: it called all 80 rows
    // folded when 79 were. The assertion is that the target list rendered, not that a wrong
    // sentence is still present, so it pins the surface's own words instead.
    await waitFor(() => expect(container.textContent).toMatch(/cohort targets/i))
    expect(container.textContent).not.toMatch(STORY)
  })

  it('/target/1 still routes to the target view', async () => {
    renderAt('/target/1')
    await waitFor(() => expect(screen.getByText(/STUB target view for 1/)).toBeInTheDocument())
    expect(screen.queryByText(STORY)).toBeNull()
  })

  it('the nav exposes five destinations', async () => {
    renderAt('/')
    // Scope to the <nav> — the Story body also links to /coverage etc.; the nav is the contract.
    const nav = screen.getByRole('navigation')
    for (const name of ['Story', 'Targets', 'Coverage', 'Method', 'About ADCs']) {
      expect(within(nav).getByRole('link', { name })).toBeInTheDocument()
    }
    // Exact — a substring "ADCs" would also match "About ADCs".
    expect(within(nav).getByRole('link', { name: /^ADCs$/ })).toBeInTheDocument()
    await screen.findByText(/We folded a cohort of ADC targets/)  // let Story's fetch settle (act)
  })

  it('/adcs routes to the ADC-B index (D-122)', async () => {
    renderAt('/adcs')
    await waitFor(() => expect(screen.getByText(/STUB adcs index/)).toBeInTheDocument())
    expect(screen.queryByText(STORY)).toBeNull()
  })

  it('/adcs/:id routes to the baseball card (D-122)', async () => {
    renderAt('/adcs/enfortumab-vedotin')
    await waitFor(() => expect(screen.getByText(/STUB adc card for enfortumab-vedotin/)).toBeInTheDocument())
    expect(screen.queryByText(STORY)).toBeNull()
  })
})
