// ⚠⚠ D-151 — THE CENSUS SURFACE STOPS MAKING THE READER HUNT FOR THE LIST.
//
// Owner, 2026-09-09: *"The Census surface is a mess. You've got to scroll to get to the list and
// when you get there, we are not using the entire left side of the table real estate and the list
// scrolls off the right side."*
//
// ⚠⚠ WHAT A TEST IN THIS ENVIRONMENT CAN AND CANNOT SEE, STATED FIRST, BECAUSE THE HONEST LIMIT IS
// THE WHOLE REASON THESE ASSERTIONS TAKE THE SHAPE THEY DO. **jsdom computes no layout.** No
// element here has a width, a height, a scroll offset or a viewport, so nothing below measures a
// gutter, a fold or an overflow — and an assertion that claimed to would be measuring zero against
// zero and passing. `D-142` recorded the same limit and paid for it: a column bound that jsdom
// certified green collapsed to about 45 px in a real browser.
//
// ⚠ So these are STRUCTURAL GUARANTEES — the DOM order and the containers that the CSS attaches
// to. They cannot prove the page looks right. What they can do is redden the moment the structure
// that makes it look right is removed, which is the failure mode a later edit will actually have:
// somebody deletes the scroll wrapper, or moves a section back above the table, and the styling
// silently stops applying.
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

vi.mock('../api.js', () => ({ listCensus: vi.fn() }))
import { listCensus } from '../api.js'
import CensusView from './CensusView.jsx'
import CensusTable from './CensusTable.jsx'

const ROW = {
  id: 1, accession: 'P00001', gene: 'ALPHA', label: 'Alpha membrane protein', tranche: 4,
  span_aa: 111, mean_plddt: 77, topology: 'contiguous', profile_status: 'computed',
  structure_kind: 'single-pass', structure_kind_label: 'single-pass',
  cost: 'local', cost_label: 'local', cost_note: 'folds on owned hardware',
}
const ROWS = [ROW, { ...ROW, id: 2, accession: 'P00002', gene: 'BETA', label: 'Beta protein' }]

const drawTable = () => render(<MemoryRouter><CensusTable rows={ROWS} /></MemoryRouter>)
const drawPage = () => render(<MemoryRouter><CensusView /></MemoryRouter>)

beforeEach(() => {
  listCensus.mockReset()
  listCensus.mockResolvedValue(ROWS)
})

// ── 1 · The list is reachable without hunting ────────────────────────────────────────────────
describe('D-151 — the search and the table come before the explanations', () => {
  it('the page puts the browser above the long background sections', async () => {
    const { container } = drawPage()
    const browser = await screen.findByRole('table')
    // ⚠ every one of these blocks used to render ABOVE the table. That is the defect, in one line.
    for (const cls of ['.census-found', '.census-howread', '.census-limits']) {
      const block = container.querySelector(cls)
      expect(block, `${cls} is missing — this change moves sections, it deletes none`).toBeTruthy()
      expect(browser.compareDocumentPosition(block) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    }
  })

  it('the counts, the absences and the batches are collapsed into one disclosure, not deleted', async () => {
    const { container } = drawPage()
    const details = container.querySelector('details.census-background')
    expect(details, 'the background disclosure is gone').toBeTruthy()
    // ⚠⚠ COLLAPSED BY DEFAULT. An `open` default would restore the exact scroll the owner objected
    // to while looking like a fix, so the absence of `open` is the assertion, not a side effect.
    expect(details.hasAttribute('open')).toBe(false)
    // ⚠ and everything that used to stand above the list is INSIDE it, in full
    for (const cls of ['.census-counts', '.census-absences', '.census-tranches', '.lede']) {
      expect(details.querySelector(cls), `${cls} left the page instead of moving`).toBeTruthy()
    }
  })

  it('the unscored claim does NOT collapse — it stays above everything', async () => {
    const { container } = drawPage()
    const bar = container.querySelector('.census-bar')
    expect(bar).toBeTruthy()
    expect(bar.closest('details')).toBeNull()
    const details = container.querySelector('details.census-background')
    expect(bar.compareDocumentPosition(details) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(bar.textContent).toMatch(/None of these proteins has been scored or ranked/)
  })

  it('inside the table, the search box precedes the legend and the table follows both', () => {
    const { container } = drawTable()
    const search = container.querySelector('.census-search')
    const notes = container.querySelector('details.census-notes')
    const table = container.querySelector('table')
    expect(search).toBeTruthy()
    expect(notes).toBeTruthy()
    expect(search.compareDocumentPosition(notes) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(notes.compareDocumentPosition(table) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(notes.hasAttribute('open')).toBe(false)
  })

  // ⚠⚠ COLLAPSED IS NOT REMOVED, AND THIS IS THE ASSERTION THAT SAYS SO. Every legend entry is in
  // the DOM whether the disclosure is open or shut — findable by the browser's own page search,
  // read unchanged by every existing `.census-legend` assertion in the sibling suites.
  it('the legend keeps every category it had, inside the disclosure', () => {
    const { container } = drawTable()
    const legend = container.querySelector('details.census-notes .census-legend')
    expect(legend).toBeTruthy()
    expect(legend.textContent).toMatch(/What the Topology column says/)
    expect(legend.textContent).toMatch(/contiguous/)
    expect(legend.textContent).toMatch(/What the Cost column says/)
  })
})

// ── 2 · The controls that may not be hidden ──────────────────────────────────────────────────
describe('D-151 — what stays visible is decided by the rulings, not by the layout', () => {
  // ⚠⚠ D-102: the applied lens is part of what the Stained % column MEANS. A lens whose name sits
  // behind a `<summary>` is a lens a reader can look at a percentage without ever having seen.
  it('the lens control is not inside any disclosure', () => {
    const { container } = drawTable()
    const lens = container.querySelector('.lens-control')
    expect(lens).toBeTruthy()
    expect(lens.closest('details')).toBeNull()
    expect(lens.textContent).toMatch(/best single cancer/)
  })

  it('the standing unscored claim stays above the search, uncollapsed', () => {
    const { container } = drawTable()
    const scope = container.querySelector('.census-scope')
    expect(scope.closest('details')).toBeNull()
    expect(scope.textContent).toMatch(/Not scored, not ranked, not ordered by suitability/)
    const search = container.querySelector('.census-search')
    expect(scope.compareDocumentPosition(search) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
  })

  // ⚠⚠ THE LICENCE DECIDES THIS ONE. HPA words citation as a precondition of DISPLAY — "be sure
  // that our content is never displayed in the absence of such citation" — so a credit behind a
  // disclosure control is a credit that is not displayed. It is the only block on this surface
  // whose position is fixed by a licence rather than by layout.
  it('the HPA credit is never placed inside a disclosure', () => {
    const withStaining = {
      ...ROW,
      staining: {
        min_patients: 10,
        best_panel: { lens: 'best_panel', category: 'measured', patients_positive: 9,
          patients_tested: 10, cancer: 'ovarian cancer' },
        pooled: { lens: 'pooled', category: 'measured', patients_positive: 9, patients_tested: 30,
          cancer: null },
        critical_normal_high: [],
        critical_tissues_declared: ['liver'],
        critical_tissues_unknown: [],
        normal_basis: 'three individuals per tissue',
        attribution: {
          primary_publication: { citation: 'Uhlen et al. 2015', doi: '10.1126/science.1260419',
            url: 'https://doi.org/10.1126/science.1260419' },
          website: { name: 'Human Protein Atlas', url: 'https://www.proteinatlas.org' },
          data_credit: 'Image credit: Human Protein Atlas',
          deep_link: 'https://www.proteinatlas.org/ENSG1-ALPHA/pathology',
        },
      },
    }
    const { container } = render(
      <MemoryRouter><CensusTable rows={[withStaining]} /></MemoryRouter>,
    )
    const blocks = [...container.querySelectorAll('[data-hpa-attribution]')]
    expect(blocks.length).toBeGreaterThan(0)
    for (const b of blocks) expect(b.closest('details')).toBeNull()
  })
})

// ── 3 · The horizontal real estate, and the right-side bleed ────────────────────────────────
describe('D-151 — the table scrolls inside a port, and the page does not', () => {
  // ⚠ THE CONTAINER, not a measured overflow. jsdom cannot scroll; what it can hold is the element
  // the `overflow-x` rule is written against, and losing that element is how the bleed comes back.
  it('the table is wrapped in a bounded scroll port', () => {
    const { container } = drawTable()
    const port = container.querySelector('.census-table-scroll')
    expect(port, 'the scroll port is gone — the table can push the document wide again').toBeTruthy()
    expect(port.querySelector('table')).toBeTruthy()
  })

  // ⚠⚠ THE STICKY HEADER LIVES INSIDE THE PORT, AND THAT IS A REQUIREMENT RATHER THAN A DETAIL.
  // `position: sticky` resolves against the nearest scrollport ancestor, so a `<thead>` left
  // outside the new wrapper would stop sticking to anything the reader is scrolling.
  it('the sticky header is inside the scroll port with its own rows', () => {
    const { container } = drawTable()
    const port = container.querySelector('.census-table-scroll')
    const thead = port.querySelector('table thead')
    expect(thead).toBeTruthy()
    expect(thead.querySelectorAll('th').length).toBeGreaterThan(8)
    expect(port.querySelectorAll('tbody tr').length).toBe(ROWS.length)
  })

  // ⚠⚠ THE RETIRED HACK, BARRED BY NAME. `.census-table td:nth-child(3) { width: 100% }` asked the
  // protein-name cell to be as wide as the whole table; at thirteen columns the auto algorithm
  // resolved that by running the total past the container, which is the right-side bleed. It is
  // read out of the stylesheet rather than remembered, because the rule and the markup are in
  // different files and only one of them is under a component test.
  it('the width:100% third-column rule is gone from the stylesheet', async () => {
    const { readFileSync } = await import('node:fs')
    const { dirname, resolve } = await import('node:path')
    const { fileURLToPath } = await import('node:url')
    const css = readFileSync(
      resolve(dirname(fileURLToPath(import.meta.url)), '../styles.css'), 'utf-8',
    )
    expect(css.length).toBeGreaterThan(1000)          // the read reached real bytes, not an empty file
    expect(css).not.toMatch(/\.census-table\s+td:nth-child\(3\)\s*\{[^}]*width:\s*100%/)
    // ⚠ and the replacement is present — a pure absence assertion would pass on a deleted file
    expect(css).toMatch(/\.census-table-scroll\s*\{[^}]*overflow:\s*auto/)
    expect(css).toMatch(/\.census-table\s+\.protein-name\s*\{/)
    expect(css).toMatch(/main\.wide\s*\{/)
  })

  // ⚠ BOUNDED AND WRAPPED, NEVER TRUNCATED. The bound is on a block child because a `max-width` on
  // a `td` is advisory under the auto table algorithm — D-142's finding, applied here — and the
  // whole name still renders, which is what separates a bound from a truncation.
  it('the protein name is bounded by a block child and keeps every character', () => {
    const { container } = drawTable()
    const cell = container.querySelector('tbody td.protein-cell')
    expect(cell).toBeTruthy()
    const name = cell.querySelector('.protein-name')
    expect(name).toBeTruthy()
    expect(name.textContent).toBe('Alpha membrane protein')
  })
})

// ── 4 · Nothing was traded away to get the layout ───────────────────────────────────────────
describe('D-151 — the surface still does everything it did', () => {
  it('search still narrows the list', async () => {
    drawTable()
    expect(document.body.textContent).toMatch(/BETA/)
    fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'ALPHA' } })
    expect(document.body.textContent).not.toMatch(/Beta protein/)
    expect(document.body.textContent).toMatch(/Alpha membrane protein/)
  })

  it('every column header is still a sort control', () => {
    const { container } = drawTable()
    const headers = [...container.querySelectorAll('thead th button')]
    expect(headers.length).toBeGreaterThan(8)
    fireEvent.click(headers[0])
    expect(container.querySelector('thead th button[aria-sort]')).toBeTruthy()
  })

  it('the cap notice and the count still report what is on screen', () => {
    const { container } = drawTable()
    expect(container.querySelector('.census-count').textContent).toMatch(/Showing/)
  })
})
