// D-135 — `/census?structure=<kind>` is an ADDRESS, not three clicks of setup.
//
// ⚠⚠ WHY THIS HAS TO WORK BEFORE ANYTHING LINKS TO IT. `/coverage`'s second-population strip and the
// Story's split CTA both point straight at the assembled proteins. A link that lands on an
// unfiltered 2,700-row table and asks the reader to find the chip has not arrived — and the failure
// is silent, because the page renders perfectly.
//
// ⚠ AND THE DEFECT THE FIX COULD INTRODUCE, pinned in the same file: a URL parameter is input from
// outside the application. A typo, a stale bookmark or a kind this census does not hold must fall
// closed to `all`, because an EMPTY table under a chip nobody pressed reads as "the census holds
// none of these" — a different and much stronger claim than "that word is not a category here".
import { fireEvent, render as rtlRender, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom'
import { describe, expect, it, vi, beforeEach } from 'vitest'

vi.mock('../api.js', () => ({ listCensus: vi.fn() }))
import { listCensus } from '../api.js'
import CensusView from './CensusView.jsx'

// ⚠ Deliberately not in accession order and not grouped by kind: a fixture that arrives sorted
// cannot tell a working filter from no filter at all.
const ROWS = [
  { id: 1, accession: 'Q00001', gene: 'SINGLE1', label: 'single one', span_aa: 300, tranche: 4,
    mean_plddt: 70.1, topology: 'contiguous', segment_count: 1,
    structure_kind: 'single-pass', structure_kind_label: 'single-pass', folded: true },
  { id: 2, accession: 'Q00002', gene: 'ASM1', label: 'assembled one', span_aa: 1200, tranche: 5,
    mean_plddt: 61.0, topology: 'contiguous', segment_count: 1,
    structure_kind: 'assembled', structure_kind_label: 'assembled (provisional)', folded: true,
    assembler_note: 'assembled by pLDDT overlap, not superimposed; seam not solved' },
  { id: 3, accession: 'Q00003', gene: 'TILES1', label: 'tiles one', span_aa: 1400, tranche: 5,
    mean_plddt: null, topology: null, structure_kind: 'tiles_only',
    structure_kind_label: 'tiles only', folded: false,
    not_folded_copy: 'tiles exist for this protein; they have not been assembled' },
  { id: 4, accession: 'Q00004', gene: 'ASM2', label: 'assembled two', span_aa: 900, tranche: 5,
    mean_plddt: 58.4, topology: 'contiguous', segment_count: 1,
    structure_kind: 'assembled', structure_kind_label: 'assembled (provisional)', folded: true },
]

// ⚠ The address bar, rendered — so an assertion about the query string is about what a reader could
// copy out of the browser, not about a component's internal state.
function Address() {
  const { pathname, search } = useLocation()
  return <span data-testid="address">{pathname}{search}</span>
}

const renderAt = (url) => rtlRender(
  <MemoryRouter initialEntries={[url]}>
    <Address />
    <Routes><Route path="/census" element={<CensusView />} /></Routes>
  </MemoryRouter>,
)

const address = () => screen.getByTestId('address').textContent
const chip = (re) => screen.getByRole('button', { name: re })
const accessions = () => screen.getAllByRole('row').slice(1)
  .map((r) => within(r).getAllByRole('cell')[0].textContent)

const loaded = async (url) => {
  const out = renderAt(url)
  await waitFor(() => expect(screen.queryAllByRole('row').length).toBeGreaterThan(1))
  return out
}

beforeEach(() => {
  vi.clearAllMocks()
  listCensus.mockResolvedValue(ROWS)
})

describe('D-135 — ?structure= selects the chip on arrival', () => {
  // ⚠⚠ THE ASSERTION THE DEEP LINKS DEPEND ON. Prove it bites by ignoring the parameter: the table
  // renders all four rows and nothing else complains.
  it('lands on the assembled chip and shows only the assembled rows', async () => {
    await loaded('/census?structure=assembled')
    expect(chip(/assembled \(provisional\) 2/)).toHaveAttribute('aria-pressed', 'true')
    expect(chip(/^all 4$/)).toHaveAttribute('aria-pressed', 'false')
    expect(accessions()).toEqual(['Q00002', 'Q00004'])
  })

  it('works for the other kinds too, not only for assembled', async () => {
    await loaded('/census?structure=tiles_only')
    expect(chip(/tiles only 1/)).toHaveAttribute('aria-pressed', 'true')
    expect(accessions()).toEqual(['Q00003'])
  })

  // ⚠⚠ THE CAVEAT ARRIVES WITH THE ACT, AND A LINK IS AN ACT (D-133 am. 1). A reader who arrives
  // already filtered to the assemblies must meet "provisional" at the same moment as the list —
  // otherwise the deep link is the one route into this page that skips the caveat.
  it('still states the assembler caveat when assembled arrived by URL', async () => {
    const { container } = await loaded('/census?structure=assembled')
    const caveat = container.querySelector('.census-kind-filter .caveat').textContent
    expect(caveat).toMatch(/assembled from tiles/i)
    expect(caveat).toMatch(/not superimposed/)
    expect(caveat).toMatch(/seam is not solved/)
    expect(caveat).toMatch(/provisional/)
  })

  // ⚠ D-102's bar: the page must not arrive having chosen. Absent means all.
  it('shows every row and the all chip when the parameter is absent', async () => {
    await loaded('/census')
    expect(chip(/^all 4$/)).toHaveAttribute('aria-pressed', 'true')
    expect(accessions()).toHaveLength(4)
  })
})

describe('D-135 — an unrecognised kind falls closed to all', () => {
  // ⚠⚠ FAIL CLOSED, AND THE REASON IS THE READER'S CONCLUSION, not tidiness. An empty table under
  // a chip nobody pressed cannot be told apart from "the census holds none of these".
  it('selects all rather than emptying the table', async () => {
    await loaded('/census?structure=not-a-real-kind')
    expect(chip(/^all 4$/)).toHaveAttribute('aria-pressed', 'true')
    expect(accessions()).toHaveLength(4)
  })

  it('falls closed for a REAL kind these rows do not hold', async () => {
    // ⚠ `mucin` is a genuine category (D-118) and this fixture has none. That is the harder case:
    // the word is valid, so a naive check on the vocabulary rather than on the DATA would pass it
    // through and draw an empty table.
    await loaded('/census?structure=mucin')
    expect(chip(/^all 4$/)).toHaveAttribute('aria-pressed', 'true')
    expect(accessions()).toHaveLength(4)
  })

  it('does not print the assembler caveat when it fell back to all', async () => {
    const { container } = await loaded('/census?structure=nonsense')
    expect(container.querySelector('.census-kind-filter .caveat')).toBeNull()
  })
})

describe('D-135 — pressing a chip writes the address', () => {
  it('puts the chosen kind into the query string', async () => {
    await loaded('/census')
    expect(address()).toBe('/census')
    fireEvent.click(chip(/assembled \(provisional\) 2/))
    expect(address()).toBe('/census?structure=assembled')
    expect(accessions()).toEqual(['Q00002', 'Q00004'])
  })

  // ⚠ `?structure=all` is noise in an address a reader may share — "all" is the absence of a
  // filter, so the parameter is DELETED rather than set to a word.
  it('removes the parameter again on all, rather than writing structure=all', async () => {
    await loaded('/census?structure=assembled')
    fireEvent.click(chip(/^all 4$/))
    expect(address()).toBe('/census')
    expect(accessions()).toHaveLength(4)
  })

  it('replaces one kind with the next rather than appending', async () => {
    await loaded('/census?structure=assembled')
    fireEvent.click(chip(/tiles only 1/))
    expect(address()).toBe('/census?structure=tiles_only')
  })

  // ⚠ The filter is the only thing it owns. A page that dropped a reader's other query parameters
  // when they clicked a chip would break every link anyone else ever adds to this route.
  it('leaves an unrelated query parameter alone', async () => {
    await loaded('/census?from=coverage')
    fireEvent.click(chip(/assembled \(provisional\) 2/))
    expect(address()).toMatch(/from=coverage/)
    expect(address()).toMatch(/structure=assembled/)
  })
})
