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
import CensusTable, { COLUMNS, topologyBadgeKey } from './CensusTable.jsx'

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
  // ⚠ scoped to the body: the legend and the fold-type chips carry the same labels by design, so a
  // page-wide count would measure the legend rather than the rows.
  it('renders the API label rather than a word of its own', () => {
    const { container } = render(<CensusTable rows={ROWS} />)
    const body = within(container.querySelector('tbody'))
    expect(body.getAllByText('assembled (provisional)').length).toBe(2)
    expect(body.getAllByText('single-pass').length).toBe(2)
    expect(body.getByText('tiles only')).toBeInTheDocument()
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

// ── the fold-type filter (D-133 am. 1: bonus → required by the owner follow-up) ─────
describe('D-133 am. 1 — the fold-type chips', () => {
  const chip = (re) => screen.getByRole('button', { name: re })

  it('offers one chip per kind present, each with its own count, defaulting to all', () => {
    render(<CensusTable rows={ROWS} />)
    expect(chip(/^all 5$/)).toHaveAttribute('aria-pressed', 'true')
    expect(chip(/assembled \(provisional\) 2/)).toBeInTheDocument()
    expect(chip(/single-pass 2/)).toBeInTheDocument()
    expect(chip(/tiles only 1/)).toBeInTheDocument()
  })

  // ⚠⚠ MATT'S ASK: the stitched proteins on their own, without hunting badges.
  it('narrows to the assembled rows on one click, and back again', () => {
    render(<CensusTable rows={ROWS} />)
    fireEvent.click(chip(/assembled \(provisional\) 2/))
    expect(accessions()).toEqual(['Q00002', 'Q00004'])
    expect(chip(/assembled \(provisional\) 2/)).toHaveAttribute('aria-pressed', 'true')
    fireEvent.click(chip(/^all 5$/))
    expect(accessions()).toHaveLength(5)
  })

  it('filters on the other kinds too, not only on assembled', () => {
    render(<CensusTable rows={ROWS} />)
    fireEvent.click(chip(/tiles only 1/))
    expect(accessions()).toEqual(['Q00003'])
  })

  // ⚠ D-102's bar, one control along: a page arriving pre-narrowed has chosen for the reader.
  it('does not arrive filtered', () => {
    render(<CensusTable rows={ROWS} />)
    expect(accessions()).toHaveLength(5)
  })

  // ⚠⚠ THE CAVEAT ARRIVES WITH THE ACT. Isolating the assemblies must not read as promoting them.
  it('states what an assembly is once the reader is looking at nothing else', () => {
    render(<CensusTable rows={ROWS} />)
    fireEvent.click(chip(/assembled \(provisional\) 2/))
    const caveat = screen.getByText(/not superimposed/)
    expect(caveat.textContent).toMatch(/seam is not solved/)
    expect(caveat.textContent).toMatch(/provisional/)
    // ⚠ census ROWS, never D-132's 45 assembled parent JOBS — a different object.
    expect(caveat.textContent).toMatch(/2 proteins/)
    expect(caveat.textContent).not.toMatch(/45/)
  })

  // ⚠ a control whose only option is 'all' is not a control
  it('does not render the chip row when every row is the same kind', () => {
    render(<CensusTable rows={[ROWS[0], ROWS[4]]} />)
    expect(screen.queryByRole('group', { name: /fold type/i })).toBeNull()
  })
})

// ── the badge legend (D-133 am. 1, owner follow-up 2026-09-08) ──────────────────────
//
// ⚠⚠ The column has printed `contiguous` / `intermittent (7)` / `GPI / no segment` since D-087 and
// defined none of them. A badge whose cause lives only in a tooltip is jargon to most readers.
describe('D-133 am. 1 — the topology legend', () => {
  const LEGEND_ROWS = [
    { ...ROWS[0], id: 11, accession: 'Q10001', topology: 'contiguous' },
    { ...ROWS[0], id: 12, accession: 'Q10002', topology: 'intermittent', segment_count: 7,
      discarded_aa: 558 },
    { ...ROWS[0], id: 13, accession: 'Q10003', topology: 'no_accepted_segment' },
  ]

  it('defines the three standing topology categories in plain words', () => {
    const { container } = render(<CensusTable rows={LEGEND_ROWS} />)
    const legend = container.querySelector('.census-legend')
    expect(legend.textContent).toMatch(/one unbroken stretch/)
    expect(legend.textContent).toMatch(/Only the LARGEST of them was folded/)
    expect(legend.textContent).toMatch(/no topological domains for these BY DESIGN/)
  })

  // ⚠⚠ THE OWNER'S RULING: four letters must not be explained with the same four letters.
  it('spells the GPI acronym out', () => {
    const { container } = render(<CensusTable rows={LEGEND_ROWS} />)
    expect(container.querySelector('.census-legend').textContent)
      .toMatch(/glycosylphosphatidylinositol/)
  })

  // ⚠ by design ≠ missing. The census holds 125 of these and they are a different architecture.
  it('says the GPI absence is by design and not missing data', () => {
    const { container } = render(<CensusTable rows={LEGEND_ROWS} />)
    const t = container.querySelector('.census-legend').textContent
    expect(t).toMatch(/BY DESIGN/)
    expect(t).toMatch(/not missing data/)
  })

  it('puts the same spelt-out meaning on the GPI badge tooltip, not just in the legend', () => {
    const { container } = render(<CensusTable rows={LEGEND_ROWS} />)
    const badge = [...container.querySelectorAll('tbody .badge')]
      .find((b) => /GPI \/ no segment/.test(b.textContent))
    expect(badge.getAttribute('title')).toMatch(/glycosylphosphatidylinositol/)
    expect(badge.getAttribute('title')).toMatch(/BY DESIGN/)
  })

  // ⚠ readable, not a wall: a legend entry for a badge no row wears explains nothing.
  it('explains the derivation badges only when a row actually wears one', () => {
    const { container, unmount } = render(<CensusTable rows={LEGEND_ROWS} />)
    expect(container.querySelector('.census-legend').textContent)
      .not.toMatch(/derived against an older manifest/)
    unmount()
    const stale = render(<CensusTable rows={[{ ...LEGEND_ROWS[0], topology: 'derivation_stale' }]} />)
    expect(stale.container.querySelector('.census-legend').textContent)
      .toMatch(/derived against an older manifest/)
  })

  it('explains NOT FOLDED only when the list holds a never-folded row', () => {
    const { container, unmount } = render(<CensusTable rows={LEGEND_ROWS} />)
    expect(container.querySelector('.census-legend').textContent).not.toMatch(/NOT FOLDED HERE/)
    unmount()
    const mixed = render(<CensusTable rows={[
      LEGEND_ROWS[0],
      { id: null, accession: 'P04626', gene: 'ERBB2', label: 'erbB-2', folded: false,
        not_folded_copy: 'not folded — above the local ceiling' },
    ]} />)
    expect(mixed.container.querySelector('.census-legend').textContent).toMatch(/NOT FOLDED HERE/)
  })

  // ⚠ the legend defines the NEW column too, and 'tiles only' / 'mucin' are opaque without it
  it('defines the structure kinds that are present, and not the ones that are absent', () => {
    const { container } = render(<CensusTable rows={ROWS} />)
    const t = container.querySelector('.census-legend').textContent
    expect(t).toMatch(/joined where they overlap by per-residue confidence/)
    expect(t).toMatch(/A tile window is not the outward-facing region/)
    expect(t).not.toMatch(/out of class for this pipeline/)   // no mucin row in this fixture
  })

  it('keeps the assembler caveat in the legend unconditionally, not only under the filter', () => {
    const { container } = render(<CensusTable rows={ROWS} />)
    const t = container.querySelector('.census-legend').textContent
    expect(t).toMatch(/Not superimposed, and the seam is not solved/)
    expect(t).toMatch(/provisional/)
  })
})

// ⚠⚠ ONE RULE DECIDES THE BADGE, so the legend cannot explain a category the cell never renders.
describe('D-133 am. 1 — topologyBadgeKey is the single rule', () => {
  it('agrees with the badge the row wears, case by case', () => {
    expect(topologyBadgeKey({ topology: 'contiguous' })).toBe('contiguous')
    expect(topologyBadgeKey({ topology: 'intermittent' })).toBe('intermittent')
    expect(topologyBadgeKey({ topology: 'no_accepted_segment' })).toBe('gpi')
    expect(topologyBadgeKey({ topology: 'unknown' })).toBe('not_derived')
    expect(topologyBadgeKey({ topology: 'derivation_stale' })).toBe('derivation_stale')
    // ⚠ null is NOT 'not derived': nothing recorded a verdict, so it takes the stale branch the
    // cell takes, rather than the benign one.
    expect(topologyBadgeKey({ topology: null })).toBe('derivation_stale')
    expect(topologyBadgeKey({ folded: false })).toBe('not_folded')
    expect(topologyBadgeKey({ folded: false, cohort_fold: { mean_plddt: 70 } }))
      .toBe('not_folded_here')
  })
})
