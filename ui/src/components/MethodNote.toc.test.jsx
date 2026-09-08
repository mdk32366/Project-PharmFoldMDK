// D-138: `/method` is fourteen sections of prose with no way in. These pin the contents rail.
//
// ⚠ The failure worth guarding is not "the rail is missing" — it is a rail that names a section
// the page does not have, or stops naming one it does. The rail derives its entries from the
// rendered headings, so the first half cannot happen by construction; the second half can, if a
// heading loses its `id`, and that is what `no heading is missing from the rail` closes.
import { render, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../api.js', () => ({
  getCensusSummary: vi.fn(), getCoverage: vi.fn(),
}))
import { getCoverage } from '../api.js'
import MethodNote from './MethodNote.jsx'

const FIXTURE = {
  coverage: { denominator: 7, ranked: 4, held_out: 2, excluded: 1 },
  failed: 0,
  rows: [
    { disposition: 'ranked', fold_status: 'folded' },
    { disposition: 'ranked', fold_status: 'folded' },
    { disposition: 'ranked', fold_status: 'folded' },
    { disposition: 'ranked', fold_status: 'not_folded' },
    { disposition: 'held_out', fold_status: 'folded' },
    { disposition: 'held_out', fold_status: 'not_folded' },
    { disposition: 'excluded', fold_status: 'not_folded' },
  ],
}

async function renderMethod() {
  getCoverage.mockResolvedValue(FIXTURE)
  const view = render(<MemoryRouter><MethodNote /></MemoryRouter>)
  await waitFor(() => expect(view.getByTestId('method-toc')).toBeTruthy())
  return view
}

const tocLinks = (view) => Array.from(view.getByTestId('method-toc').querySelectorAll('a'))
const bodyHeadings = (view) =>
  Array.from(view.getByTestId('method-body').querySelectorAll('h2, h3'))

beforeEach(() => vi.clearAllMocks())

describe('MethodNote — the contents rail (D-138)', () => {
  it('renders one labelled navigation landmark for the contents, beside the prose', async () => {
    const view = await renderMethod()
    const toc = view.getByTestId('method-toc')
    expect(toc.tagName).toBe('NAV')
    // ⚠ Labelled, for the same reason D-135 labelled the site nav: two unnamed `nav` regions are
    // indistinguishable to a screen reader.
    expect(toc.getAttribute('aria-label')).toBe('Method contents')
    // Left rail, not a block dropped into the prose: the rail is a SIBLING of the body.
    expect(toc.parentElement.className).toContain('method-layout')
    expect(toc.parentElement).toBe(view.getByTestId('method-body').parentElement)
    expect(tocLinks(view).length).toBeGreaterThan(1)
  })

  it('lists the real sections a reader comes here for, by their own heading text', async () => {
    const view = await renderMethod()
    const labels = tocLinks(view).map((a) => a.textContent)
    for (const wanted of [
      'Where the deep learning runs (D-051)',
      'Long proteins: tiles, glue, and a winner-tile assembler (D-121)',
      'Kabsch-path restitch — what it does, and what it does not (D-125-B)',
      'Overlap-confidence Kabsch — what it does, and what it does not (D-126-B)',
      'Piecewise / domain-aware Kabsch, and the whole stitch-path train (D-127-B)',
      'Linker / seam honesty, and the five-step stitch-path train (D-128-B)',
      'What we now call the eight joins we could not hold (D-129-B)',
      'Phase 4 residual-RMSD OPS and named refuse (D-130-B / D-131)',
      'What it will never do — commitments (D-028)',
      'Glossary — every term on one page',
    ]) {
      expect(labels).toContain(wanted)
    }
  })

  it('gives every entry an href that resolves to a heading id present in the document', async () => {
    const view = await renderMethod()
    const links = tocLinks(view)
    expect(links.length).toBeGreaterThan(0)
    for (const link of links) {
      const href = link.getAttribute('href')
      expect(href).toMatch(/^#[a-z0-9-]+$/)
      const target = view.container.querySelector(`[id="${href.slice(1)}"]`)
      expect(target, `no element carries the id ${href}`).toBeTruthy()
      expect(['H2', 'H3']).toContain(target.tagName)
      // The rail says what the heading says — a shorter label would be a second copy of the
      // section names, free to drift from the page.
      expect(link.textContent).toBe(target.textContent.trim())
    }
  })

  it('names no ghost section: the rail is exactly the body headings, in document order', async () => {
    const view = await renderMethod()
    const headingIds = bodyHeadings(view).map((h) => h.id)
    // ⚠ The other direction, and the one that can actually break: a heading that loses its `id`
    // silently drops out of a derived rail. An empty string here means the page grew a section the
    // reader cannot jump to.
    expect(headingIds).not.toContain('')
    expect(tocLinks(view).map((a) => a.getAttribute('href'))).toEqual(
      headingIds.map((id) => `#${id}`),
    )
  })

  it('marks the sub-sections as sub-sections, so the rail reads as an outline', async () => {
    const view = await renderMethod()
    const items = Array.from(view.getByTestId('method-toc').querySelectorAll('li'))
    const levels = items.map((li) => li.className)
    expect(levels[0]).toBe('toc-h2')
    expect(levels.filter((c) => c === 'toc-h2')).toHaveLength(1)
    expect(levels.filter((c) => c === 'toc-h3').length).toBeGreaterThan(8)
  })

  it('does not disturb the prose the page already shipped', async () => {
    const view = await renderMethod()
    const body = view.getByTestId('method-body').textContent
    expect(body).toMatch(/3 ranked-and-folded of 7/)
    expect(body).toMatch(/What this system claims/)
    expect(body).toMatch(/D-126 remains the best experimental path/)
    expect(body).toMatch(/Never claim 27\/27 PASS/)
    expect(body).toMatch(/CLOSED/)
    // The rail is navigation, not a second surface for claims: it carries headings and nothing else.
    const toc = view.getByTestId('method-toc').textContent
    expect(toc).not.toMatch(/PASS|REFUSE|Å|F-004/)
  })
})
