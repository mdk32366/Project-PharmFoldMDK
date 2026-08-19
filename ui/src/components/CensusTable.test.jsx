import { fireEvent, render as rtlRender, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import CensusTable, { filterRows } from './CensusTable.jsx'
import CensusDetail from './CensusDetail.jsx'

// ⚠ The accession cell is a react-router <Link> now — each protein has its own page, so it must be
// openable in a new tab and reachable by the back button. A Link outside a Router throws, so every
// render goes through one.
const render = (ui) => rtlRender(<MemoryRouter>{ui}</MemoryRouter>)

const ROWS = [
  { id: 1, accession: 'Q9UHC9', gene: 'NPC1L1', label: 'NPC1-like 1', span_aa: 272, tranche: 3,
    mean_plddt: 61.2, topology: 'intermittent', segment_count: 7, extracellular_total_aa: 830,
    discarded_aa: 558, segments: '1-30;60-90', span_definition: 'v2', scored: false,
    span_start: 1, span_end: 272, full_length: 1332, not_scored_reason: 'D-079 decision 1' },
  { id: 2, accession: 'A0AVI2', gene: 'FER1L5', label: 'Fer-1-like protein 5', span_aa: 75,
    tranche: 2, mean_plddt: 44.7, topology: 'contiguous', segment_count: 1,
    extracellular_total_aa: 75, discarded_aa: 0, segments: '1983-2057', scored: false },
  { id: 3, accession: 'P00000', gene: null, label: null, span_aa: 100, tranche: 2,
    mean_plddt: null, topology: 'no_accepted_segment', segment_count: 0, scored: false },
]

describe('CensusTable', () => {
  it('defaults to accession order, not pLDDT — an order is not a score (D-079)', () => {
    render(<CensusTable rows={ROWS} />)
    const first = within(screen.getAllByRole('row')[1]).getByRole('link')
    expect(first).toHaveTextContent('A0AVI2')
  })

  it('links each accession to its own page, not an onClick handler', () => {
    render(<CensusTable rows={ROWS} />)
    // ⚠ href, not a click handler: openable in a new tab, shareable, back-button reachable.
    expect(screen.getByRole('link', { name: 'Q9UHC9' })).toHaveAttribute('href', '/census/1')
    expect(screen.getByRole('link', { name: 'A0AVI2' })).toHaveAttribute('href', '/census/2')
  })

  it('searches accession, gene and protein name', () => {
    expect(filterRows(ROWS, 'npc1l1').map((r) => r.accession)).toEqual(['Q9UHC9'])
    expect(filterRows(ROWS, 'fer-1').map((r) => r.accession)).toEqual(['A0AVI2'])
    expect(filterRows(ROWS, 'Q9UHC9').map((r) => r.accession)).toEqual(['Q9UHC9'])
    expect(filterRows(ROWS, 'zzzz')).toEqual([])
  })

  it('sorts on click and reverses on a second click', () => {
    render(<CensusTable rows={ROWS} />)
    fireEvent.click(screen.getByRole('button', { name: /Span \(aa\)/ }))
    let cells = screen.getAllByRole('row')[1]
    expect(within(cells).getByRole('link')).toHaveTextContent('A0AVI2') // 75 aa
    fireEvent.click(screen.getByRole('button', { name: /Span \(aa\)/ }))
    cells = screen.getAllByRole('row')[1]
    expect(within(cells).getByRole('link')).toHaveTextContent('Q9UHC9') // 272 aa
  })

  // ⚠ A missing pLDDT is not a low one. Ascending by pLDDT must not put it first.
  it('sorts a null pLDDT LAST, not as the lowest value', () => {
    render(<CensusTable rows={ROWS} />)
    fireEvent.click(screen.getByRole('button', { name: /pLDDT/ }))
    const rows = screen.getAllByRole('row')
    const last = within(rows[rows.length - 1]).getByRole('link')
    expect(last).toHaveTextContent('P00000')
  })

  // ⚠⚠ The owner ruling: the badge is on the row, not only in the detail panel.
  it('badges intermittent rows in the table itself', () => {
    render(<CensusTable rows={ROWS} />)
    expect(screen.getByText(/intermittent \(7\)/)).toBeInTheDocument()
  })

  it('states on the surface that nothing here is scored or ranked', () => {
    render(<CensusTable rows={ROWS} />)
    expect(screen.getByText(/Not scored, not ranked, not ordered by suitability/i)).toBeInTheDocument()
  })

  it('says a search matched nothing rather than showing an empty table silently', () => {
    render(<CensusTable rows={ROWS} />)
    fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'zzzz' } })
    expect(screen.getByText(/no protein matches that search/i)).toBeInTheDocument()
  })
})

describe('CensusDetail', () => {
  it('says the extracellular portion is intermittent, and what was left out', () => {
    render(<CensusDetail detail={{ ...ROWS[0], cancer_associations: null }} />)
    expect(screen.getByText(/7 separate extracellular segments/i)).toBeInTheDocument()
    // ⚠ "segments WERE", not "was" — the first version agreed the verb with the aa count instead
    // of the segment count, and this assertion pinned the mistake.
    expect(screen.getByText(/558 aa across the remaining 6 segments were not folded/i)).toBeInTheDocument()
  })

  it('agrees the verb with the SEGMENT count, singular and plural', () => {
    const two = { ...ROWS[0], segment_count: 2, discarded_aa: 40, cancer_associations: null }
    const { unmount } = render(<CensusDetail detail={two} />)
    expect(screen.getByText(/40 aa across the remaining 1 segment was not folded/i)).toBeInTheDocument()
    unmount()
    render(<CensusDetail detail={{ ...ROWS[0], cancer_associations: null }} />)
    expect(screen.getByText(/remaining 6 segments were not folded/i)).toBeInTheDocument()
  })

  it('says a contiguous protein models the whole extracellular portion', () => {
    render(<CensusDetail detail={{ ...ROWS[1], cancer_associations: null }} />)
    expect(screen.getByText(/models the whole extracellular portion/i)).toBeInTheDocument()
  })

  // ⚠ "no extracellular component" — the owner asked for this said explicitly.
  it('says plainly when there is no annotated extracellular segment', () => {
    render(<CensusDetail detail={{ ...ROWS[2], cancer_associations: null }} />)
    expect(screen.getByText(/No annotated extracellular segment/i)).toBeInTheDocument()
    // ⚠ matched on the substantive claim; the 'not missing data' phrase is split across <strong>
    expect(screen.getByText(/different molecular architecture/i)).toBeInTheDocument()
  })

  // ⚠⚠ The one that matters most: unknown must never render as none.
  it('never says "no associations" for a protein outside the source', () => {
    render(<CensusDetail detail={{ ...ROWS[0], cancer_associations: {
      status: 'not_covered', hits: [], source: 'Kathad et al. 2024',
      coverage_note: 'the association source covers the 82 cohort targets only' } }} />)
    expect(screen.getByText(/Not covered by the association source/i)).toBeInTheDocument()
    expect(screen.getByText(/unknown/i)).toBeInTheDocument()
    expect(screen.queryByText(/no cancer associations found/i)).not.toBeInTheDocument()
  })

  it('distinguishes a measured absence from an unexamined one', () => {
    render(<CensusDetail detail={{ ...ROWS[0], cancer_associations: {
      status: 'covered', hits: [], source: 'Kathad et al. 2024', coverage_note: '' } }} />)
    expect(screen.getByText(/no cancer met the threshold/i)).toBeInTheDocument()
    expect(screen.getByText(/is.*a measured absence/i)).toBeInTheDocument()
  })

  it('lists associated cancers when the protein is covered', () => {
    render(<CensusDetail detail={{ ...ROWS[0], cancer_associations: {
      status: 'covered', hits: [{ cancer: 'Colorectal cancer', qh_score: 266.67 }],
      source: 'Kathad et al. 2024', coverage_note: '' } }} />)
    expect(screen.getByText(/Colorectal cancer/)).toBeInTheDocument()
  })
})

describe('stale derivation', () => {
  const STALE = { id: 9, accession: 'Q00000', gene: 'X', label: 'x', span_aa: 10, tranche: 2,
    mean_plddt: 60, topology: 'derivation_stale', derivation_status: 'derivation_stale',
    derivation_note: 'derived from census_manifest.v7.csv @ aaa…, but the file on disk is @ bbb…',
    scored: false }

  // ⚠ The old final branch labelled ANYTHING that was not intermittent/GPI as "contiguous".
  it('never labels a stale row contiguous', () => {
    render(<CensusTable rows={[STALE]} />)
    expect(screen.queryByText('contiguous')).not.toBeInTheDocument()
    expect(screen.getByText(/derivation out of date/i)).toBeInTheDocument()
  })

  it('distinguishes "not derived" from "derived against the wrong manifest"', () => {
    render(<CensusTable rows={[{ ...STALE, topology: 'unknown' }]} />)
    expect(screen.getByText(/not derived/i)).toBeInTheDocument()
  })

  // ⚠⚠ Withheld, not missing — and never the stale numbers.
  it('withholds stale segment numbers and says why', () => {
    render(<CensusDetail detail={{ ...STALE, cancer_associations: null }} />)
    expect(screen.getByText(/the segment derivation is out of date/i)).toBeInTheDocument()
    expect(screen.getByText(/withheld deliberately, not missing/i)).toBeInTheDocument()
  })
})

describe('the row cap', () => {
  const many = Array.from({ length: 250 }, (_, i) => ({
    id: 100 + i, accession: `Q${String(i).padStart(5, '0')}`, gene: `G${i}`, label: `Protein ${i}`,
    span_aa: 100 + i, tranche: 2, mean_plddt: 60, topology: 'contiguous', segment_count: 1,
    scored: false,
  }))

  // ⚠⚠ THE ONE THAT WOULD HAVE CAUGHT THE SHIPPED BUG. The page read "Showing 2,641 of 2,641"
  // above 200 rendered rows — a silent cap claiming completeness.
  it('never claims to show more rows than it draws', () => {
    render(<CensusTable rows={many} />)
    const drawn = screen.getAllByRole('row').length - 1   // minus the header
    expect(screen.getByText(/Showing/).textContent).toContain(String(drawn))
    expect(screen.getByText(/Showing/).textContent).not.toMatch(/Showing\s*250\s*of/)
  })

  it('announces the cap and offers to lift it', () => {
    render(<CensusTable rows={many} />)
    expect(screen.getByText(/Capped for the browser/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /render all 250/i })).toBeInTheDocument()
  })

  it('renders everything once the cap is lifted', () => {
    render(<CensusTable rows={many} />)
    fireEvent.click(screen.getByRole('button', { name: /render all 250/i }))
    expect(screen.getAllByRole('row').length - 1).toBe(250)
    expect(screen.queryByText(/Capped for the browser/i)).not.toBeInTheDocument()
  })

  it('does not cap a small list at all', () => {
    render(<CensusTable rows={ROWS} />)
    expect(screen.queryByText(/Capped for the browser/i)).not.toBeInTheDocument()
    expect(screen.getAllByRole('row').length - 1).toBe(ROWS.length)
  })
})

// ⚠ The same claim, the same drift risk. This table says "not scored, not ranked, not ordered by
// suitability" — all three still TRUE — but a reader is one click from a page carrying the model's
// output, so the sentence must say so rather than rely on ruling 1's naming.
describe('CensusTable — the unscored claim discloses the profile', () => {
  it('keeps all three true clauses and adds the disclosure', () => {
    const { container } = render(<CensusTable rows={ROWS} />)
    const t = container.textContent
    expect(t).toMatch(/Not scored, not ranked, not ordered by suitability/)
    expect(t).toMatch(/no judgement of target quality has been applied/)
    expect(t).toMatch(/structural profile/)
  })

  // ⚠ THIS ASSERTION CHANGED WITH THE CLAIM, AND THAT IS WHY IT WENT RED. It pinned "this table
  // neither shows it nor orders by it" — true until the Profile STATUS column landed. The table now
  // shows WHETHER a profile could be computed, never WHAT it was. The test tracks the new claim
  // rather than being deleted, and the substantive guarantee is asserted separately below: no
  // value ever appears in a row.
  it('says the column reports only WHETHER a profile exists, not what it was', () => {
    const { container } = render(<CensusTable rows={ROWS} />)
    const t = container.textContent
    expect(t).toMatch(/says only whether one could be computed, never what it was/)
    expect(t).toMatch(/A refusal is about range, not merit/)
  })

  it('and still renders no profile value in any row', () => {
    const { container } = render(<CensusTable rows={ROWS} />)
    // ⚠ the disclosure must not become the feature: no 0.xxxx figure anywhere in the table body
    const body = container.querySelector('tbody')
    if (body) expect(body.textContent).not.toMatch(/0\.\d{4}/)
  })
})

// ── the Profile STATUS column (D-079 amendment 1 ruling 2) ────────────────
//
// ⚠⚠ THE COLUMN EXISTS TO SURFACE THE FINDING WITHOUT HANDING ANYONE A RANKING. The table sorts on
// every column (D-087). A VALUE column would be one header click from 1,397 proteins ordered
// highest-first with the 1,293 refusals swept to the bottom. A CATEGORY sorts into groups, which
// orders nothing by suitability. These tests pin both halves: the status is shown, and no number is.
const STATUS_ROWS = [
  { ...ROWS[0], id: 1, accession: 'A0AVI2', profile_status: 'computed' },
  { ...ROWS[0], id: 2, accession: 'Q9UHC9', profile_status: 'refused_out_of_distribution' },
  { ...ROWS[0], id: 3, accession: 'Q9ULH0', profile_status: 'refused_span_below_floor' },
  { ...ROWS[0], id: 4, accession: 'P11111', profile_status: 'refused_features_incomplete' },
]

describe('CensusTable — the Profile status column', () => {
  it('renders a Profile header and a word per row, never a number', () => {
    const { container } = render(<CensusTable rows={STATUS_ROWS} />)
    const t = container.textContent
    expect(t).toMatch(/Profile/)
    expect(t).toMatch(/computed/)
    // ⚠⚠ THE LOAD-BEARING ASSERTION: no profile VALUE anywhere in the table body.
    const body = container.querySelector('tbody')
    expect(body.textContent).not.toMatch(/0\.\d{3,}/)
  })

  it('keeps the three refusal causes DISTINCT rather than pooling them into "n/a"', () => {
    const { container } = render(<CensusTable rows={STATUS_ROWS} />)
    const t = container.querySelector('tbody').textContent
    expect(t).toMatch(/outside fitted range/)
    expect(t).toMatch(/span too short to describe/)
    expect(t).toMatch(/measurements incomplete/)
  })

  it('renders an em dash, not a blank, when a row has no status at all', () => {
    const { container } = render(<CensusTable rows={[{ ...ROWS[0], id: 9 }]} />)
    expect(container.querySelector('tbody').textContent).toMatch(/—/)
  })

  it('the column is declared non-numeric, so sorting groups rather than orders a magnitude', () => {
    const { container } = render(<CensusTable rows={STATUS_ROWS} />)
    const heads = [...container.querySelectorAll('th')].map((h) => h.textContent)
    expect(heads.some((h) => /Profile/.test(h))).toBe(true)
    // sorting by it must not reorder into anything resembling a ranked value list: the visible
    // cells are words, and words are all we can sort.
    const cells = [...container.querySelectorAll('tbody tr')]
      .map((tr) => tr.lastElementChild.textContent)
    expect(cells.every((c) => !/\d/.test(c))).toBe(true)
  })
})
