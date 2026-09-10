// D-155 follow-up 3 — the two-column reading layout on the prose pages.
//
// ⚠⚠ WHAT THESE CAN AND CANNOT SEE. jsdom computes no layout, so nothing here asserts a column
// width or that anything is beside anything: the grid itself is a stylesheet property and is
// asserted in `tests/test_d155_surface_merge.py`. What jsdom CAN see is the structure the grid
// places — the rail exists, it is the shared component, and it lists exactly the sections the page
// renders — and that is the half where a rail actually goes wrong.
//
// ⚠ `D-138`'s rule, inherited with the component: the rail reads its entries off the rendered
// headings, so it can only fail in ONE direction — a heading with no `id` goes missing from it.
// That direction is closed here by requiring an `id` on every heading in the body.
import { render as rtlRender, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi, beforeEach } from 'vitest'

vi.mock('../api.js', () => ({
  listAnalyses: vi.fn(), getCoverage: vi.fn(), getCensusSummary: vi.fn(),
}))
import { listAnalyses, getCoverage, getCensusSummary } from '../api.js'
import AdcContext from './AdcContext.jsx'
import Story from './Story.jsx'

const render = (ui) => rtlRender(<MemoryRouter>{ui}</MemoryRouter>)

beforeEach(() => {
  vi.clearAllMocks()
  listAnalyses.mockResolvedValue([
    { id: 1, accession: 'Q96NY8', gene: 'NECTIN4', mean_plddt: 77.26, disposition: 'ranked' },
    { id: 2, accession: 'P04626', gene: 'ERBB2', mean_plddt: 73.94, disposition: 'ranked' },
  ])
  getCoverage.mockResolvedValue({
    coverage: { denominator: 82, ranked: 67, held_out: 13, excluded: 2 },
    rows: [{ accession: 'Q96NY8', gene: 'NECTIN4', disposition: 'ranked', fold_status: 'folded' }],
  })
  getCensusSummary.mockResolvedValue({
    manifest_rows: 3467, folded: 3463,
    structure_kinds: [{ kind: 'assembled', label: 'assembled (provisional)', n: 45 }],
  })
})

describe('D-155 follow-up 3 · /about gets the rail /method already had', () => {
  it('renders the shared contents rail, not a second one', async () => {
    const { container } = render(<AdcContext />)
    await waitFor(() => expect(container.querySelector('.method-toc')).toBeTruthy())
    // ⚠ the SAME class the /method rail uses — a second rail with its own class is the F-052 shape
    expect(container.querySelectorAll('.method-toc')).toHaveLength(1)
    expect(container.querySelector('.about-layout')).toBeTruthy()
    expect(container.querySelector('[data-testid="about-body"]')).toBeTruthy()
  })

  it('lists every section the page renders, and no section it does not', async () => {
    const { container } = render(<AdcContext />)
    await waitFor(() => expect(container.querySelector('.method-toc a')).toBeTruthy())
    const body = container.querySelector('[data-testid="about-body"]')
    const headings = [...body.querySelectorAll('h2[id], h3[id]')].map((h) => h.textContent.trim())
    const rail = [...container.querySelectorAll('.method-toc a')].map((a) => a.textContent.trim())
    // ⚠⚠ EQUALITY, NOT CONTAINMENT. A rail that lists a section the page does not carry is the
    // ghost entry D-138 forbids; a rail missing one is the direction an absent `id` fails in.
    expect(rail).toEqual(headings)
    expect(rail.length).toBeGreaterThan(5)
  })

  it('gives every heading in the body an id, which is the rail’s only failure direction', async () => {
    const { container } = render(<AdcContext />)
    await waitFor(() => expect(container.querySelector('.method-toc')).toBeTruthy())
    const body = container.querySelector('[data-testid="about-body"]')
    const all = [...body.querySelectorAll('h2, h3')]
    const withoutId = all.filter((h) => !h.id).map((h) => h.textContent.trim())
    expect(withoutId, 'a heading with no id is invisible to the rail').toEqual([])
  })

  it('every rail link resolves to a heading that exists on the page', async () => {
    const { container } = render(<AdcContext />)
    await waitFor(() => expect(container.querySelector('.method-toc a')).toBeTruthy())
    for (const a of container.querySelectorAll('.method-toc a')) {
      const id = a.getAttribute('href').slice(1)
      expect(container.querySelector(`[id="${id}"]`), `#${id} has no target`).toBeTruthy()
    }
  })

  it('does not disturb the order of the sections it now indexes', async () => {
    // ⚠ The layout is a GRID over the same DOM: the reading order a screen reader follows and the
    // order a narrow viewport stacks to are unchanged, which is the property D-152 dec 4 insisted
    // on when it refused a CSS `order` for the scorer table.
    const { container } = render(<AdcContext />)
    await waitFor(() => expect(container.querySelector('.method-toc')).toBeTruthy())
    const t = container.querySelector('[data-testid="about-body"]').textContent
    expect(t.indexOf('Why this project exists')).toBeLessThan(t.indexOf('What the 82 is'))
    expect(t.indexOf('What the 82 is')).toBeLessThan(t.indexOf('The questions this project'))
  })
})

describe('D-155 follow-up 3 · the Story keeps its own contents as the rail', () => {
  it('still renders its beats nav, which the grid places in the rail column', async () => {
    const { container } = render(<Story />)
    await waitFor(() => expect(container.querySelector('.story-toc')).toBeTruthy())
    const nav = container.querySelector('.story-toc')
    expect(within(nav).getAllByRole('link').length).toBeGreaterThan(2)
    // ⚠ no second rail: the Story's contents already existed, so this page needed a LAYOUT and not
    // a component — the rail column is CSS over the nav that was already there.
    expect(container.querySelectorAll('.method-toc')).toHaveLength(0)
  })

  it('every beat link resolves to a section that exists', async () => {
    const { container } = render(<Story />)
    await waitFor(() => expect(container.querySelector('.story-toc a')).toBeTruthy())
    for (const a of container.querySelectorAll('.story-toc a')) {
      const id = a.getAttribute('href').slice(1)
      expect(container.querySelector(`[id="${id}"]`), `#${id} has no target`).toBeTruthy()
    }
  })

  it('keeps the cold strip in the body, where three big numbers read as a band', async () => {
    const { container } = render(<Story />)
    await waitFor(() => expect(container.querySelector('.story-cold-strip')).toBeTruthy())
    const strip = container.querySelector('.story-cold-strip')
    // ⚠ D-135's clause survives the layout: it is not inside a disclosure and not inside the rail
    expect(strip.closest('details')).toBeNull()
    expect(strip.closest('.story-toc')).toBeNull()
  })
})
