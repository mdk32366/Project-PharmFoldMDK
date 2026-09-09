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
  listPipelineAdcs: vi.fn().mockResolvedValue({ pipeline: [] }),
  getPipelineAdc: vi.fn().mockResolvedValue({}),
  getAdcAccess: vi.fn().mockResolvedValue({}),
  // ⚠ D-151: the census suppliers, added because this suite now renders `/census` and
  // `/census/:id` to assert which surfaces get the wide measure. Empty payloads on purpose —
  // the claim under test is the SHELL's class, not anything about census rows.
  getAssociations: vi.fn().mockResolvedValue({ associations: {}, attributions: {} }),
  getRanking: vi.fn().mockResolvedValue({ rows: [] }),
  listCensus: vi.fn().mockResolvedValue([]),
  getCensusDetail: vi.fn().mockResolvedValue({}),
  getCancerBurden: vi.fn().mockResolvedValue({}),
  getCancerBurdenMeta: vi.fn().mockResolvedValue({}),
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
vi.mock('./components/AdcPipelineCard.jsx', () => ({
  default: ({ id }) => <div>STUB pipeline card for {String(id)}</div>,
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
    // ⚠ D-135: scoped BY NAME, not by "the only navigation on the page". The Story grew a beat
    // contents of its own, so an unqualified `getByRole('navigation')` now finds two — and the
    // remedy is that both landmarks are named, which is the accessibility fix as well as the fix
    // here. The assertion is unchanged: these six links belong to the SITE nav.
    // ⚠ D-151: `Targets` became `Initial Targets`. RTL matches an accessible NAME exactly when it
    // is given a string, so this line went red on the rename rather than passing on a substring —
    // which is the guard working, and why the value is corrected here rather than loosened to a
    // regex that would accept either spelling for ever.
    const nav = screen.getByRole('navigation', { name: 'Site' })
    for (const name of ['Story', 'Initial Targets', 'Coverage', 'Method', 'About ADCs']) {
      expect(within(nav).getByRole('link', { name })).toBeInTheDocument()
    }
    // Exact — a substring "ADCs" would also match "About ADCs".
    expect(within(nav).getByRole('link', { name: /^ADCs$/ })).toBeInTheDocument()
    await screen.findByText(/We folded a cohort of ADC targets/)  // let Story's fetch settle (act)
  })

  // ── ⚠⚠ D-151 — THE MENU RENAME, AND THE DEEP LINKS IT MUST NOT BREAK ─────────────────────────
  // Owner ruling 2026-09-09: the menu entry reads **Initial Targets**. The 82 are the list this
  // project STARTS from — a published comparator it re-orders — and a bare "Targets" read as *the*
  // targets while `/census` holds 3,467 more.
  // ⚠ A LABEL IS NOT A ROUTE. `/targets` is already in the Story's CTA, in the census card's
  // dead-end note, and in every address anybody has shared; renaming the path would break all of
  // them to no benefit, so these assertions pin the label AND the unchanged path together. A test
  // that checked only the words would go green on a rename that broke every link.
  describe('D-151 — the menu says Initial Targets and the route does not move', () => {
    it('the site nav labels the cohort surface "Initial Targets"', async () => {
      renderAt('/')
      const nav = screen.getByRole('navigation', { name: 'Site' })
      const link = within(nav).getByRole('link', { name: 'Initial Targets' })
      expect(link).toHaveAttribute('href', '/targets')
      // ⚠ REDDENS ON REGRESSION: the bare label must not come back, and `name: 'Targets'` is an
      // exact match, so this cannot pass on "Initial Targets" by accident.
      expect(within(nav).queryByRole('link', { name: 'Targets' })).toBeNull()
      await screen.findByText(/We folded a cohort of ADC targets/)
    })

    it('spells Initial — the typo the owner named is barred by a test, not by care', async () => {
      renderAt('/')
      const nav = screen.getByRole('navigation', { name: 'Site' })
      expect(nav.textContent).toContain('Initial Targets')
      expect(nav.textContent).not.toMatch(/Inital/)
      await screen.findByText(/We folded a cohort of ADC targets/)
    })

    it('/targets still routes to the cohort list — the deep link is unbroken', async () => {
      const { container } = renderAt('/targets')
      await waitFor(() => expect(container.textContent).toMatch(/cohort targets/i))
    })
  })

  // ── ⚠⚠ D-151 — THE CENSUS GETS THE WHOLE WIDTH, AND THE SHELL IS WHERE THAT IS DECIDED ───────
  // Owner, 2026-09-09: *"we are not using the entire left side of the table real estate."*
  // `main { max-width: 60rem }` is a reading measure and the census is an eleven-column table.
  // ⚠ jsdom computes NO layout, so this asserts the STRUCTURE that carries the width — the class
  // on `<main>` — and never a rendered pixel. A test that claimed to measure the gutter here would
  // be measuring nothing at all.
  describe('D-151 — /census is granted the wide measure, and only /census', () => {
    it('puts the wide class on <main> for the census list', async () => {
      const { container } = renderAt('/census')
      await waitFor(() => expect(container.querySelector('main')).toBeTruthy())
      expect(container.querySelector('main').className).toContain('wide')
    })

    it('leaves every prose surface at the reading measure', async () => {
      for (const path of ['/', '/about', '/method', '/coverage']) {
        const { container, unmount } = renderAt(path)
        expect(container.querySelector('main').className ?? '').not.toContain('wide')
        unmount()
      }
      await Promise.resolve()
    })

    it('does not widen a census protein CARD — /census/:id is prose, one column', async () => {
      const { container } = renderAt('/census/P04626')
      expect(container.querySelector('main').className ?? '').not.toContain('wide')
    })
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

  it('/adcs/pipeline/:id routes to the pipeline card (D-124)', async () => {
    renderAt('/adcs/pipeline/ifinatamab-deruxtecan')
    await waitFor(() => expect(screen.getByText(/STUB pipeline card for ifinatamab-deruxtecan/)).toBeInTheDocument())
    expect(screen.queryByText(/STUB adc card/)).toBeNull()
    expect(screen.queryByText(STORY)).toBeNull()
  })
})
