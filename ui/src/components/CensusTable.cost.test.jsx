// D-137 — the census Cost column: what a protein costs to FOLD, sortable, with a legend that
// says in the same frame that this is NOT a suitability axis.
//
// ⚠⚠ THE GAP THIS PINS. `core/foldability.py` has held the cost envelope since D-077 dec 6 and
// no served surface read it: the census printed every protein's span and said nothing about what
// that span costs. D-077's licensed ✅ Reproducibility claim was unreadable from the page holding
// the data.
//
// ⚠⚠ AND THE ONE THESE TESTS EXIST FOR IS THE REFUSAL. D-077 dec 1 refusal 3 bars filtering the
// census by cost, and D-133 am. 1 has already shipped fold-type CHIPS — so a `local` / `rental` /
// `over ceiling` chip set is the obvious next control and is exactly the forbidden one. Several
// assertions below fail if one appears.
import { fireEvent, render as rtlRender, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import CensusTable, { COLUMNS, COST_ORDER, costBadgeKey } from './CensusTable.jsx'

const render = (ui) => rtlRender(<MemoryRouter>{ui}</MemoryRouter>)

// The server-owned strings, as the API sends them. ⚠ Abridged, but the load-bearing clauses are
// verbatim: a fixture that paraphrases the caveat cannot prove the caveat reached the screen.
const AXIS = 'COMPUTE COST, NOT SUITABILITY. This column says where this protein\'s '
  + 'extracellular span can be folded at the measured recipe — what it costs to compute. It says '
  + 'nothing about whether the protein is a good ADC target, and nothing here is a score or a '
  + 'rank. It also filters nothing: every census row stays in the census, whatever it costs '
  + '(D-077 dec 1).'
const RECIPE = 'local NVIDIA Blackwell, 8 GB VRAM at dtype=int8, chunk_size=64: '
  + 'local <= 440 aa, over-ceiling >= 630 aa'
const NOTE = {
  local: 'its extracellular span is inside the measured local envelope, so this fold costs no '
    + 'rented compute — it is reproducible by any reader with the same consumer card and no '
    + 'cloud spend.',
  rental: 'its span is above the measured local bound but below the point where a single card '
    + 'definitively fails, so folding it would need rented compute. ⚠ A COST CLASS, NOT A QUEUE '
    + 'POSITION: rental for the hold-48 remainder closed 2026-09-05 (pod Terminated), so this is '
    + 'what the fold would have cost, never a fold that is being waited on.',
  over_ceiling: 'its span is at or above the length that is measured to fail, so it folds on no '
    + 'single card as one sequence. ⚠ Deliberately NOT the same class as rental: "costs money" '
    + 'and "cannot be bought at any price on one card" are different facts. ⚠ It is also not a '
    + 'statement about tiles or assembly — how a structure was MADE is the Structure column, and '
    + 'a protein assembled from tiles is still over the single-pass ceiling.',
  span_unrecorded: 'no extracellular span is recorded on this row, so it has no envelope and no '
    + 'cost. ⚠ A named absence, never counted as affordable — an unmeasured target bucketed as '
    + 'cheap is how a cost estimate becomes a fiction (D-024).',
}
const LABEL = {
  local: 'local',
  rental: 'rental',
  over_ceiling: 'over ceiling',
  span_unrecorded: 'span not recorded',
}

const costed = (cost) => (cost == null
  ? {}
  : { cost, cost_label: LABEL[cost], cost_note: NOTE[cost], cost_axis: AXIS, cost_recipe: RECIPE })

// ⚠ Deliberately NOT in cost order and not in accession order: a fixture that arrives already
// grouped cannot tell a working sort from no sort at all.
// ⚠ The spans agree with the cost they carry (300 local, 500 rental, 1200 over-ceiling) so the
// fixture cannot pass by asserting a contradiction the real API would never send.
const ROWS = [
  { id: 1, accession: 'Q00001', gene: 'MID1', label: 'rental one', span_aa: 500, tranche: 4,
    mean_plddt: 70.1, topology: 'contiguous', segment_count: 1, folded: true,
    structure_kind: 'single-pass', structure_kind_label: 'single-pass', ...costed('rental') },
  { id: 2, accession: 'Q00002', gene: 'BIG1', label: 'over one', span_aa: 1200, tranche: 5,
    mean_plddt: 61.0, topology: 'contiguous', segment_count: 1, folded: true,
    structure_kind: 'assembled', structure_kind_label: 'assembled (provisional)',
    ...costed('over_ceiling') },
  { id: 3, accession: 'Q00003', gene: 'CHEAP1', label: 'local one', span_aa: 300, tranche: 3,
    mean_plddt: 74.9, topology: 'contiguous', segment_count: 1, folded: true,
    structure_kind: 'single-pass', structure_kind_label: 'single-pass', ...costed('local') },
  { id: 4, accession: 'Q00004', gene: 'NOSPAN1', label: 'unmeasured one', span_aa: null,
    tranche: 5, mean_plddt: null, topology: null, folded: false,
    not_folded_copy: 'not folded', ...costed('span_unrecorded') },
  { id: 5, accession: 'Q00005', gene: 'CHEAP2', label: 'local two', span_aa: 120, tranche: 1,
    mean_plddt: 80.2, topology: 'contiguous', segment_count: 1, folded: true,
    structure_kind: 'single-pass', structure_kind_label: 'single-pass', ...costed('local') },
]

const COST_HEADER = /Cost to fold \(compute — not suitability\)/

const accessions = () =>
  screen.getAllByRole('row').slice(1).map((r) => within(r).getAllByRole('cell')[0].textContent)

describe('D-137 — the census sorts on what a protein costs to fold', () => {
  // ⚠⚠ THE TRIPWIRE. Out of COLUMNS the header button and the sort both vanish, and an
  // assertion on rendered text would pass on a hand-drawn <th> that sorts nothing.
  it('carries cost as a real COLUMNS entry declaring its cost order', () => {
    const col = COLUMNS.find((c) => c.key === 'cost')
    expect(col).toBeTruthy()
    expect(col.label).toMatch(COST_HEADER)
    // ⚠ no magnitude in the CELL — the order carries it. `numeric: true` over category strings
    // would compute NaN and order nothing while claiming a rank.
    expect(col.numeric).toBe(false)
    expect(col.order).toEqual(COST_ORDER)
    expect(COST_ORDER).toEqual(['local', 'rental', 'over_ceiling'])
  })

  // ⚠⚠ THE HEADER ITSELF DENIES THE SUITABILITY READING. A column called only 'Cost' beside an
  // unscored census invites the reader to read cheap as good — D-077 dec 1 refusal 2 exactly.
  it('names the axis in the header, not only in the legend', () => {
    render(<CensusTable rows={ROWS} />)
    const head = screen.getByRole('button', { name: COST_HEADER })
    expect(head).toBeInTheDocument()
    expect(head.textContent).toMatch(/not suitability/)
  })

  it('groups the cheap rows together on one click — cheapest compute first', () => {
    render(<CensusTable rows={ROWS} />)
    fireEvent.click(screen.getByRole('button', { name: COST_HEADER }))
    // local, local, rental, over_ceiling, then the unrecorded span LAST
    expect(accessions()).toEqual(['Q00003', 'Q00005', 'Q00001', 'Q00002', 'Q00004'])
  })

  // ⚠⚠ THE NULL RULE, AND IT IS THE ONE THAT MATTERS ON THIS COLUMN. An unrecorded span is not
  // an expensive one. If `span_unrecorded` sat at the end of COST_ORDER it would lead a
  // descending sort — an absence rendered as the dearest row, which is the same defect as
  // counting it affordable wearing the opposite sign.
  it('sorts the unrecorded span LAST in both directions, never first when reversed', () => {
    render(<CensusTable rows={ROWS} />)
    const head = screen.getByRole('button', { name: COST_HEADER })
    fireEvent.click(head)
    expect(accessions().at(-1)).toBe('Q00004')
    fireEvent.click(head)
    expect(accessions()).toEqual(['Q00002', 'Q00001', 'Q00003', 'Q00005', 'Q00004'])
    expect(accessions().at(-1)).toBe('Q00004')
    expect(accessions()[0]).not.toBe('Q00004')
  })

  it('reports the sort direction to a screen reader on the header it sorted', () => {
    render(<CensusTable rows={ROWS} />)
    const head = screen.getByRole('button', { name: COST_HEADER })
    expect(head).toHaveAttribute('aria-sort', 'none')
    fireEvent.click(head)
    expect(screen.getByRole('button', { name: COST_HEADER }))
      .toHaveAttribute('aria-sort', 'ascending')
  })

  // ⚠⚠ D-102 / D-079: a sort the READER chooses is a lens; a page arriving ordered by our own
  // compute budget is the most misreadable default this table could have.
  it('still arrives in accession order, not ordered by cost', () => {
    render(<CensusTable rows={ROWS} />)
    expect(accessions()).toEqual(['Q00001', 'Q00002', 'Q00003', 'Q00004', 'Q00005'])
  })

  it('sorts on the category, never on the label, so a copy edit cannot re-order the table', () => {
    // ⚠ 'aaa relabelled' would sort FIRST if the label drove the sort; the cost is still
    // `over_ceiling`, so the row stays where the cost order puts it.
    const relabelled = ROWS.map((r) => (
      r.accession === 'Q00002' ? { ...r, cost_label: 'aaa relabelled' } : r
    ))
    render(<CensusTable rows={relabelled} />)
    fireEvent.click(screen.getByRole('button', { name: COST_HEADER }))
    expect(accessions()).toEqual(['Q00003', 'Q00005', 'Q00001', 'Q00002', 'Q00004'])
  })

  // ⚠ the other columns must keep sorting exactly as they did — `compare` changed shape
  it('leaves the existing sorts alone', () => {
    render(<CensusTable rows={ROWS} />)
    fireEvent.click(screen.getByRole('button', { name: /^pLDDT/ }))
    expect(accessions()).toEqual(['Q00002', 'Q00001', 'Q00003', 'Q00005', 'Q00004'])
    fireEvent.click(screen.getByRole('button', { name: /Span \(aa/ }))
    expect(accessions()).toEqual(['Q00005', 'Q00003', 'Q00001', 'Q00002', 'Q00004'])
  })
})

describe('D-137 — the cell says the class, and says which absence it is', () => {
  // ⚠ scoped to the body: the legend carries the same terms by design, so a page-wide count
  // would measure the legend rather than the rows.
  it('renders the API term rather than a word of its own', () => {
    const { container } = render(<CensusTable rows={ROWS} />)
    const body = within(container.querySelector('tbody'))
    expect(body.getAllByText('local').length).toBe(2)
    expect(body.getByText('rental')).toBeInTheDocument()
    expect(body.getByText('over ceiling')).toBeInTheDocument()
    expect(body.getByText('span not recorded')).toBeInTheDocument()
  })

  // ⚠⚠ `rental` NEVER TRAVELS BARE. Rental closed 2026-09-05 (pod Terminated); a bare badge on
  // 349 rows would re-open the "waiting on rented capacity" claim the tree already refuses.
  it('carries the rental closure in the badge tooltip, so rental is never a queue position', () => {
    const { container } = render(<CensusTable rows={ROWS} />)
    const badge = [...container.querySelectorAll('tbody .badge-cost')]
      .find((b) => b.textContent === 'rental')
    expect(badge.getAttribute('title')).toMatch(/closed 2026-09-05/)
    expect(badge.getAttribute('title')).toMatch(/NOT A QUEUE POSITION/)
  })

  // ⚠ over_ceiling is about single-pass fold LENGTH; assembled is about how a structure was
  // MADE. Q00002 is both, and the tooltip says the two columns are allowed to disagree.
  it('keeps over ceiling apart from rental and apart from assembly', () => {
    const { container } = render(<CensusTable rows={ROWS} />)
    const badge = [...container.querySelectorAll('tbody .badge-cost')]
      .find((b) => b.textContent === 'over ceiling')
    expect(badge.getAttribute('title')).toMatch(/NOT the same class as rental/)
    expect(badge.getAttribute('title')).toMatch(/still over the single-pass ceiling/)
    // and the same row is `assembled` in the Structure column — the two coexist
    const row = [...container.querySelectorAll('tbody tr')]
      .find((r) => r.textContent.includes('Q00002'))
    expect(row.textContent).toMatch(/assembled \(provisional\)/)
    expect(row.textContent).toMatch(/over ceiling/)
  })

  // ⚠⚠ TWO ABSENCES, AND NEITHER IS `local`. `span not recorded` is the server saying it looked;
  // `not recorded` is the row carrying no cost field at all.
  it('says "span not recorded" when the server found no span', () => {
    const { container } = render(<CensusTable rows={ROWS} />)
    const cell = [...container.querySelectorAll('.cost-cell')]
      .find((c) => /span not recorded/.test(c.textContent))
    expect(cell).toBeTruthy()
    expect(cell.querySelector('.badge').getAttribute('title'))
      .toMatch(/never counted as affordable/)
    expect(cell.textContent).not.toMatch(/^local$/)
  })

  it('says "not recorded" — never local — when the row carries no cost field', () => {
    const { container } = render(<CensusTable rows={[{
      id: 9, accession: 'P04626', gene: 'ERBB2', label: 'erbB-2', span_aa: 630,
      tranche: null, mean_plddt: null, topology: null, folded: false,
      not_folded_copy: 'not folded — longer than the local card can fold',
    }]} />)
    const cell = container.querySelector('.cost-cell')
    expect(cell.textContent).toMatch(/not recorded/)
    expect(cell.textContent).not.toMatch(/local/)
    expect(cell.querySelector('.unknown').getAttribute('title'))
      .toMatch(/never an implied local fold/)
  })

  // ⚠ the column reports a CLASS. A number in it is a magnitude a reader will compare, and
  // comparing budgets across an unscored census is a ranking arriving by another route.
  it('renders no figure in the cost cell', () => {
    const { container } = render(<CensusTable rows={ROWS} />)
    const cells = [...container.querySelectorAll('.cost-cell')].map((c) => c.textContent)
    expect(cells.every((c) => !/\d/.test(c))).toBe(true)
  })

  // ⚠ drawn once, in its own column — the D-133 lesson: two spellings of one fact, only one of
  // them sortable, teaches a reader to distrust the surface.
  it('draws the cost badge once per row', () => {
    const { container } = render(<CensusTable rows={[ROWS[0]]} />)
    expect(container.querySelectorAll('.badge-cost').length).toBe(1)
  })
})

// ── the legend: the axis statement, in the same visual frame (D-077 dec 1 refusal 2) ──────
describe('D-137 — the cost legend', () => {
  it('prints the axis statement against the table, at full size and not in a tooltip', () => {
    const { container } = render(<CensusTable rows={ROWS} />)
    const legend = container.querySelector('.census-legend')
    expect(legend.textContent).toMatch(/COMPUTE COST, NOT SUITABILITY/)
    expect(legend.textContent).toMatch(/nothing about whether the protein is a good ADC target/)
    // ⚠ refusal 3, stated to the reader and not only to the reviewer
    expect(legend.textContent).toMatch(/filters nothing/)
    expect(container.querySelector('.cost-axis')).toBeTruthy()
  })

  // ⚠ D-050 / D-077 dec 3: the same span is affordable at int8 and not at fp16, so a cost claim
  // without its recipe is not checkable. It comes off the wire — there is no ceiling in the JSX.
  it('names the ceiling and the recipe it was measured under, from the payload', () => {
    const { container } = render(<CensusTable rows={ROWS} />)
    const legend = container.querySelector('.census-legend')
    expect(legend.textContent).toMatch(/dtype=int8/)
    expect(legend.textContent).toMatch(/chunk_size=64/)
    expect(legend.textContent).toMatch(/440 aa/)
  })

  it('defines every cost category the rows actually wear, in the API\'s own words', () => {
    const { container } = render(<CensusTable rows={ROWS} />)
    const t = container.querySelector('.census-legend').textContent
    expect(t).toMatch(/inside the measured local envelope/)
    expect(t).toMatch(/closed 2026-09-05/)
    expect(t).toMatch(/folds on no single card as one sequence/)
    expect(t).toMatch(/never counted as affordable/)
  })

  // ⚠ readable, not a wall — the same rule D-133 am. 1 set for topology.
  it('does not define a cost category no row wears', () => {
    const { container } = render(<CensusTable rows={[ROWS[2], ROWS[4]]} />)
    const t = container.querySelector('.census-legend').textContent
    expect(t).toMatch(/inside the measured local envelope/)
    expect(t).not.toMatch(/closed 2026-09-05/)
    expect(t).not.toMatch(/folds on no single card/)
  })

  // ⚠⚠ THE LEGEND IS THE PAYLOAD'S, NOT THE COMPONENT'S. An older API that sends no cost fields
  // must produce no legend rather than a legend the rows cannot support.
  it('renders nothing at all when the payload carries no cost', () => {
    const bare = ROWS.map(({ cost, cost_label, cost_note, cost_axis, cost_recipe, ...r }) => r)
    const { container } = render(<CensusTable rows={bare} />)
    const legend = container.querySelector('.census-legend')
    expect(legend.textContent).not.toMatch(/COMPUTE COST/)
    expect(legend.textContent).not.toMatch(/What the Cost column says/)
    // ⚠ and the column still renders — as a stated absence, never as `local`
    expect(container.querySelector('.cost-cell').textContent).toMatch(/not recorded/)
  })

  it('re-spells nothing: a relabelled category shows the server\'s word in the legend too', () => {
    const relabelled = ROWS.map((r) => (
      r.cost === 'local' ? { ...r, cost_label: 'no rented compute' } : r
    ))
    const { container } = render(<CensusTable rows={relabelled} />)
    const legend = container.querySelector('.census-legend')
    expect(legend.textContent).toMatch(/no rented compute/)
  })
})

// ── refusal 3: there is no cost filter, and there must never be one ───────────────────────
describe('D-137 — the cost axis filters nothing', () => {
  it('offers no cost chip beside the fold-type chips', () => {
    render(<CensusTable rows={ROWS} />)
    // the fold-type group is present, so the absence below is a real absence and not an
    // empty render
    expect(screen.getByRole('group', { name: /fold type/i })).toBeInTheDocument()
    expect(screen.queryByRole('group', { name: /cost/i })).toBeNull()
    for (const term of [/^local \d/, /^rental \d/, /^over ceiling \d/]) {
      expect(screen.queryByRole('button', { name: term })).toBeNull()
    }
  })

  // ⚠ `queryAllByRole`, not `getAllByRole`: with no staining in the fixture the critical-tissue
  // checkbox does not render either, and `getAllBy*` THROWS on an empty match — an assertion
  // about an absence must not fail because a *different* control is also absent.
  it('offers no checkbox that hides expensive rows', () => {
    render(<CensusTable rows={ROWS} />)
    const boxes = screen.queryAllByRole('checkbox')
      .map((b) => b.closest('label')?.textContent ?? '')
    expect(boxes.some((t) => /cost|rental|ceiling|afford/i.test(t))).toBe(false)
  })

  // ⚠⚠ THE ROW COUNT IS THE ASSERTION. Every narrowing control on this table is exercised and
  // the unaffordable rows survive all of them — including `span not recorded`, the row an
  // affordability filter would drop first.
  it('keeps every row on screen through a cost sort and through the other filters', () => {
    render(<CensusTable rows={ROWS} />)
    expect(accessions()).toHaveLength(5)
    fireEvent.click(screen.getByRole('button', { name: COST_HEADER }))
    expect(accessions()).toHaveLength(5)
    fireEvent.click(screen.getByRole('button', { name: /single-pass 3/ }))
    // the fold-type chip narrows by KIND and by nothing else: the rental and unrecorded
    // single-pass rows are still there
    expect(accessions()).toEqual(expect.arrayContaining(['Q00001', 'Q00003', 'Q00005']))
    fireEvent.click(screen.getByRole('button', { name: /^all 5$/ }))
    expect(accessions()).toHaveLength(5)
  })

  // ⚠ searching by an accession must not be answered by cost — the search matches names, and a
  // cost word must not become a hidden query term.
  it('does not make the cost category searchable as if it were a name', () => {
    render(<CensusTable rows={ROWS} />)
    fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'over ceiling' } })
    expect(screen.getAllByRole('row')).toHaveLength(1)     // header only
  })
})

// ⚠⚠ ONE RULE DECIDES THE BADGE, so the legend cannot explain a category the cell never renders.
describe('D-137 — costBadgeKey is the single rule', () => {
  it('agrees with the badge the row wears, case by case', () => {
    expect(costBadgeKey({ cost: 'local' })).toBe('local')
    expect(costBadgeKey({ cost: 'rental' })).toBe('rental')
    expect(costBadgeKey({ cost: 'over_ceiling' })).toBe('over_ceiling')
    expect(costBadgeKey({ cost: 'span_unrecorded' })).toBe('span_unrecorded')
  })

  // ⚠⚠ THREE ABSENCES, AND THEY STAY THREE. No cost field is not the same claim as no span, and
  // neither is the same as a word the server grew and this page has not learnt.
  it('keeps a missing field apart from a missing span apart from an unknown word', () => {
    expect(costBadgeKey({})).toBe('not_served')
    expect(costBadgeKey({ cost: null })).toBe('not_served')
    expect(costBadgeKey({ cost: 'span_unrecorded' })).not.toBe('not_served')
    expect(costBadgeKey({ cost: 'quantum_ceiling' })).toBe('unknown_verdict')
  })

  // ⚠ an unknown verdict is rendered VERBATIM rather than coerced into a word we understand —
  // a vocabulary that grew on the server must not arrive silently relabelled.
  it('renders an unknown verdict as the server spelt it', () => {
    const { container } = render(<CensusTable rows={[{
      ...ROWS[2], cost: 'quantum_ceiling', cost_label: 'quantum ceiling',
      cost_note: 'a category this page has never met',
    }]} />)
    const cell = container.querySelector('.cost-cell')
    expect(cell.textContent).toMatch(/quantum ceiling/)
    expect(cell.textContent).not.toMatch(/local/)
  })
})
