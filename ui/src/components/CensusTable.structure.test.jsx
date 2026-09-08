// D-133 — the census Structure column: seam-assembled vs single-pass is a category you can group
// by, and it is NOT a rank.
//
// ⚠⚠ THE DEFECT THIS PINS. `structure_kind_label` was rendered as a badge in the accession cell and
// was absent from `COLUMNS` — so the one identity D-118 exists to serve was the only row property
// the table could not sort by, under a paragraph claiming a sort on every column (D-087). A badge
// that cannot be sorted is not the same feature as a column, and nothing went red about it.
import { fireEvent, render as rtlRender, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import CensusTable, { COLUMNS } from './CensusTable.jsx'

const render = (ui) => rtlRender(<MemoryRouter>{ui}</MemoryRouter>)

// ⚠ Deliberately NOT in kind order, and deliberately not in accession order either: a fixture that
// arrives already grouped cannot tell a working sort from no sort at all.
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
  { id: 5, accession: 'Q00005', gene: 'SINGLE2', label: 'single two', span_aa: 250, tranche: 3,
    mean_plddt: 74.9, topology: 'contiguous', segment_count: 1,
    structure_kind: 'single-pass', structure_kind_label: 'single-pass', folded: true },
]

const STRUCTURE_HEADER = /Structure \(single pass or assembled from tiles\)/

const accessions = () =>
  screen.getAllByRole('row').slice(1).map((r) => within(r).getAllByRole('cell')[0].textContent)

describe('D-133 — the census sorts on structure kind', () => {
  // ⚠⚠ THE TRIPWIRE. The column is a member of COLUMNS or it has no header button and no sort;
  // asserting only the rendered text would pass on a hard-coded <th> that sorts nothing.
  it('carries structure_kind as a real COLUMNS entry, not a hand-drawn header', () => {
    const col = COLUMNS.find((c) => c.key === 'structure_kind')
    expect(col).toBeTruthy()
    expect(col.label).toMatch(STRUCTURE_HEADER)
    // ⚠ a CATEGORY, not a magnitude — the same ruling as Profile. `numeric: true` here would make
    // `av - bv` over strings produce NaN and order nothing, and would claim a rank while doing it.
    expect(col.numeric).toBe(false)
  })

  it('renders the header as a sort button, like every other column', () => {
    render(<CensusTable rows={ROWS} />)
    expect(screen.getByRole('button', { name: STRUCTURE_HEADER })).toBeInTheDocument()
  })

  // ⚠⚠ MATT'S ASK, AS AN ASSERTION: click Structure and the seam-spliced proteins are together.
  it('groups the assembled rows together on one click, and reverses on a second', () => {
    render(<CensusTable rows={ROWS} />)
    fireEvent.click(screen.getByRole('button', { name: STRUCTURE_HEADER }))
    // ascending: assembled, assembled, single-pass, single-pass, tiles_only
    expect(accessions()).toEqual(['Q00002', 'Q00004', 'Q00001', 'Q00005', 'Q00003'])
    fireEvent.click(screen.getByRole('button', { name: STRUCTURE_HEADER }))
    expect(accessions()).toEqual(['Q00003', 'Q00001', 'Q00005', 'Q00002', 'Q00004'])
  })

  it('reports the sort direction to a screen reader on the header it sorted', () => {
    render(<CensusTable rows={ROWS} />)
    const head = screen.getByRole('button', { name: STRUCTURE_HEADER })
    expect(head).toHaveAttribute('aria-sort', 'none')
    fireEvent.click(head)
    expect(screen.getByRole('button', { name: STRUCTURE_HEADER }))
      .toHaveAttribute('aria-sort', 'ascending')
  })

  // ⚠⚠ D-102 / D-079: a sort the READER chooses is a lens; a page arriving pre-grouped is not.
  it('still arrives in accession order, not grouped by kind', () => {
    render(<CensusTable rows={ROWS} />)
    expect(accessions()).toEqual(['Q00001', 'Q00002', 'Q00003', 'Q00004', 'Q00005'])
  })

  it('sorts on the category, never on the label, so a copy edit cannot re-order the table', () => {
    // ⚠ `zzz relabelled` would sort LAST if the label drove the sort; the kind is still `assembled`.
    const relabelled = ROWS.map((r) => (
      r.accession === 'Q00002' ? { ...r, structure_kind_label: 'zzz relabelled' } : r
    ))
    render(<CensusTable rows={relabelled} />)
    fireEvent.click(screen.getByRole('button', { name: STRUCTURE_HEADER }))
    expect(accessions().slice(0, 2)).toEqual(['Q00002', 'Q00004'])
  })
})

describe('D-133 — the cell says what the kind is, and says when it has none', () => {
  it('renders the API label rather than a word of its own', () => {
    render(<CensusTable rows={ROWS} />)
    expect(screen.getAllByText('assembled (provisional)').length).toBe(2)
    expect(screen.getAllByText('single-pass').length).toBe(2)
    expect(screen.getByText('tiles only')).toBeInTheDocument()
  })

  it('carries the assembler note in the badge tooltip, so "assembled" is never bare', () => {
    const { container } = render(<CensusTable rows={ROWS} />)
    const titled = [...container.querySelectorAll('.badge-kind')]
      .map((b) => b.getAttribute('title'))
    expect(titled.some((t) => /not superimposed; seam not solved/.test(t ?? ''))).toBe(true)
  })

  // ⚠⚠ A BLANK WOULD READ AS "single-pass" — a fold that was never performed. 777-odd never-folded
  // manifest rows carry no kind at all.
  it('says "not recorded" for a row with no kind instead of leaving the cell empty', () => {
    const { container } = render(<CensusTable rows={[
      { id: 9, accession: 'P04626', gene: 'ERBB2', label: 'erbB-2', span_aa: 630,
        tranche: null, mean_plddt: null, topology: null, folded: false,
        not_folded_copy: 'not folded — longer than the local card can fold' },
    ]} />)
    const cell = container.querySelector('.kind-cell')
    expect(cell.textContent).toMatch(/not recorded/)
    expect(cell.textContent).not.toMatch(/single-pass/)
    expect(cell.querySelector('.unknown').getAttribute('title'))
      .toMatch(/never an implied single-pass fold/)
  })

  // ⚠ ONE PLACE TO READ IT. The badge used to sit in the accession cell; duplicating it would give
  // the reader two spellings of one fact with only one of them sortable.
  it('draws the kind once — in its own column, not beside the accession link', () => {
    const { container } = render(<CensusTable rows={[ROWS[1]]} />)
    expect(container.querySelectorAll('.badge-kind').length).toBe(1)
    const first = container.querySelector('tbody tr td')
    expect(first.querySelector('.badge-kind')).toBeNull()
    expect(first.textContent.trim()).toBe('Q00002')
  })

  // ⚠ the column reports how the structure was MADE. It must not acquire a number.
  it('renders no figure in the structure cell', () => {
    const { container } = render(<CensusTable rows={ROWS} />)
    const cells = [...container.querySelectorAll('.kind-cell')].map((c) => c.textContent)
    expect(cells.every((c) => !/\d/.test(c))).toBe(true)
  })
})

describe('D-133 — the assembled-only filter', () => {
  it('offers the filter with its own count and narrows to the assembled rows', () => {
    render(<CensusTable rows={ROWS} />)
    const box = screen.getByRole('checkbox', { name: /assembled from tiles/ })
    expect(screen.getByText(/Show only the/).textContent).toMatch(/2 proteins/)
    fireEvent.click(box)
    expect(accessions()).toEqual(['Q00002', 'Q00004'])
  })

  it('prints the assembler caveat beside the control, not in a tooltip', () => {
    render(<CensusTable rows={ROWS} />)
    expect(screen.getByText(/not superimposed/)).toBeInTheDocument()
    expect(screen.getByText(/seam is not solved/)).toBeInTheDocument()
  })

  // ⚠ a control that can only empty the table is a broken control
  it('does not offer the filter when nothing in the list is assembled', () => {
    render(<CensusTable rows={[ROWS[0], ROWS[4]]} />)
    expect(screen.queryByRole('checkbox', { name: /assembled from tiles/ })).toBeNull()
  })

  // ⚠⚠ THE COUNT STATES ITS OWN DENOMINATOR, and it counts census ROWS. D-132's 45 is a count of
  // assembled parent JOBS — a different object, and printing it here would be a false provenance.
  it('states the count against the rows it holds, never against the D-132 parent inventory', () => {
    render(<CensusTable rows={ROWS} />)
    const t = screen.getByText(/Show only the/).textContent
    expect(t).toMatch(/of 5 listed/)
    expect(t).not.toMatch(/45/)
  })
})
