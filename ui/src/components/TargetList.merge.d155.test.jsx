// D-155 — the merged cohort surface, as a reader meets it.
//
// ⚠⚠ WHY THIS EXISTS BESIDE `TargetList.dual.test.jsx`. That file is D-135's, and it followed its
// claims here when `/coverage` was retired — two populations, the bridge, the denominator. This one
// is about what the MERGE itself produced: one Status cell where four facts used to live on two
// pages, a `why` that appears only where there is a why, and a Rank cell that names its absence.
//
// ⚠ jsdom computes no layout, so nothing here can assert a width. The column budget is a property
// of the stylesheet and is asserted in `tests/test_d155_surface_merge.py`; the RENDERED figures for
// this ship are owed and are declared as such in the entry rather than guessed at.
import { render as rtlRender, screen, waitFor, within, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi, beforeEach } from 'vitest'

vi.mock('../api.js', () => ({
  listAnalyses: vi.fn(), getCoverage: vi.fn(), getAssociations: vi.fn(),
  getRanking: vi.fn(), getCensusSummary: vi.fn(),
}))
import {
  listAnalyses, getCoverage, getAssociations, getRanking, getCensusSummary,
} from '../api.js'
import TargetList, { causeAddsSomething } from './TargetList.jsx'

const render = (ui) => rtlRender(<MemoryRouter>{ui}</MemoryRouter>)

// ⚠ Four shapes, because the Status cell has to be right about all four and they are the four the
// cohort actually contains: ranked+folded, ranked+failed (with a census sibling), held out, and an
// oversize exclusion that has no analyses row at all.
const COVERAGE = {
  coverage: { denominator: 4, ranked: 2, held_out: 1, excluded: 1, unmeasured_tier: 0, no_topology: 0 },
  rows: [
    { accession: 'Q00001', gene: 'AAA', protein_name: 'Alpha protein', disposition: 'ranked',
      fold_status: 'folded', analysis_id: 11, tier: 'local' },
    { accession: 'Q00002', gene: 'BBB', protein_name: 'Beta protein', disposition: 'ranked',
      fold_status: 'failed', tier: 'rental', tier_reason: 'whole_sequence_fold',
      fail_reason: 'CUDA out of memory. Tried to allocate 11.84 GiB on a card with 10.82 free.',
      census_sibling: {
        structure_kind: 'assembled', structure_kind_label: 'assembled (provisional)', folded: true,
        assembler_note: 'assembled by pLDDT overlap, not superimposed; seam not solved',
      } },
    { accession: 'Q00003', gene: 'CCC', protein_name: 'Gamma protein', disposition: 'held_out',
      fold_status: 'folded', analysis_id: 13, tier: 'local' },
    // ⚠ no analyses row: oversize, never attempted — the FAT2 / MUC16 shape
    { accession: 'Q00004', gene: 'DDD', protein_name: 'Delta protein', disposition: 'excluded',
      fold_status: 'not_folded', excluded: true, tier: 'rental',
      exclusion_reason: 'oversize: 4030 aa — folds on no single card as one sequence (D-022)' },
  ],
}

const ANALYSES = [
  { id: 11, accession: 'Q00001', gene: 'AAA', label: 'AAA', mean_plddt: 81.4, tier: 'local', aliases: null },
  { id: null, accession: 'Q00002', gene: 'BBB', label: 'BBB', mean_plddt: null, tier: 'rental', aliases: null },
  { id: 13, accession: 'Q00003', gene: 'CCC', label: 'CCC', mean_plddt: 66.2, tier: 'local', aliases: null },
]

const CENSUS = {
  manifest_rows: 3467, folded: 3463, max_mean_plddt: 89.25,
  structure_kinds: [{ kind: 'assembled', label: 'assembled (provisional)', n: 45 }],
}

const mounted = async () => {
  const out = render(<TargetList />)
  await screen.findByRole('table')
  await waitFor(() => expect(out.container.querySelector('.status-cell')).toBeTruthy())
  return out
}

const rowFor = (container, gene) =>
  [...container.querySelectorAll('tbody tr')].find((tr) => tr.textContent.includes(gene))

beforeEach(() => {
  vi.clearAllMocks()
  getCoverage.mockResolvedValue(COVERAGE)
  listAnalyses.mockResolvedValue(ANALYSES)
  getCensusSummary.mockResolvedValue(CENSUS)
  getAssociations.mockResolvedValue({ associations: {}, attributions: {}, cutoff: 100 })
  getRanking.mockResolvedValue({ rows: [{ accession: 'Q00001', rank: 1, gene: 'AAA' }] })
})

describe('D-155 · one table for one population', () => {
  it('renders every cohort member, including the one with no analyses row', async () => {
    const { container } = await mounted()
    for (const gene of ['AAA', 'BBB', 'CCC', 'DDD']) {
      expect(rowFor(container, gene), `${gene} is a cohort member and must have a row`).toBeTruthy()
    }
  })

  it('leads with the honest denominator and closes with the second population', async () => {
    const { container } = await mounted()
    await waitFor(() => expect(container.querySelector('.census-population')).toBeTruthy())
    const line = container.querySelector('.coverage-line')
    const table = container.querySelector('table')
    const strip = container.querySelector('.census-population')
    expect(line.compareDocumentPosition(table) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(table.compareDocumentPosition(strip) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    // ⚠ neither is inside a disclosure — both are claims, and D-152's rule is that claims stay open
    expect(line.closest('details')).toBeNull()
    expect(strip.closest('details')).toBeNull()
  })

  it('states the cohort denominator and leaves it alone when the table is filtered', async () => {
    const { container } = await mounted()
    const before = container.querySelector('.coverage-headline').textContent
    expect(before).toMatch(/1 ranked & folded of 4/)
    fireEvent.change(screen.getByLabelText('Search'), { target: { value: 'AAA' } })
    expect(container.querySelector('.coverage-headline').textContent).toBe(before)
    expect(container.querySelector('.filter-count').textContent)
      .toMatch(/denominator above is unchanged/)
  })
})

describe('D-155 · the Status cell answers three questions and keeps them apart', () => {
  it('gives a folded, ranked row its disposition, its fold and its band', async () => {
    const { container } = await mounted()
    const cell = rowFor(container, 'AAA').querySelector('.status-cell')
    expect(cell.querySelector('.status-disposition').textContent).toMatch(/in the ranking set/)
    expect(cell.querySelector('.status-fold').textContent.trim()).toBe('folded')
    expect(cell.querySelector('.status-confidence').textContent).toMatch(/Confident backbone/)
    // ⚠ no reason to disclose: the fold worked and the row is ranked
    expect(cell.querySelector('.status-note')).toBeNull()
  })

  it('keeps a failed fold FAILED even though a census structure of it exists', async () => {
    const { container } = await mounted()
    const cell = rowFor(container, 'BBB').querySelector('.status-cell')
    expect(cell.querySelector('.status-fold').textContent.trim()).toBe('fold failed')
    // ⚠⚠ D-043's three values, and the bridge is not a fourth
    expect(cell.textContent).not.toMatch(/folded elsewhere|partially folded/i)
    const note = cell.querySelector('.status-note')
    expect(note).toBeTruthy()
    expect(note.textContent).toMatch(/CUDA out of memory/)
    expect(within(note).getByRole('link', { name: /census: assembled \(provisional\)/ }))
      .toHaveAttribute('href', '/census/Q00002')
    expect(note.textContent).toMatch(/not this cohort fold/i)
  })

  it('says held out rather than excluded, because they are different facts', async () => {
    const { container } = await mounted()
    const cell = rowFor(container, 'CCC').querySelector('.status-cell')
    expect(cell.querySelector('.status-disposition').textContent).toMatch(/held out of ranking/)
    expect(cell.querySelector('.status-fold').textContent.trim()).toBe('folded')
  })

  it('discloses an exclusion reason in full, never truncated', async () => {
    const { container } = await mounted()
    const note = rowFor(container, 'DDD').querySelector('.status-note')
    expect(note.textContent).toContain(
      'oversize: 4030 aa — folds on no single card as one sequence (D-022)')
  })

  it('never renders a why control on a row with nothing to disclose', async () => {
    const { container } = await mounted()
    // ⚠ a disclosure that opens onto nothing promises a reason the record does not hold
    for (const gene of ['AAA', 'CCC']) {
      expect(rowFor(container, gene).querySelector('.status-note')).toBeNull()
    }
    for (const gene of ['BBB', 'DDD']) {
      const note = rowFor(container, gene).querySelector('.status-note')
      expect(note).toBeTruthy()
      expect(note.hasAttribute('open')).toBe(false)   // never open by default (D-152)
      expect(note.querySelector('summary').textContent.trim()).toBe('why')
    }
  })
})

// ⚠⚠ THE FOLLOW-UP, AND IT WAS FOUND BY LOOKING AT THE DEPLOYED PAGE RATHER THAN BY A TEST.
// The merged Status cell shipped saying `not folded` THREE TIMES on `MUC16` and `FAT2` — once as
// the rank cause, once as the fold axis, once inside the confidence axis's absence label — and it
// told a below-floor row it was *"in the ranking set — excluded by the pre-registered floor"* in a
// single em-dashed sentence. Both read as one claim contradicting itself. ⚠ These count occurrences
// rather than matching a fragment, because a fragment match passes on one copy or on five (the
// same reason `D-154`'s burden guard counts).
describe('D-155 follow-up · each axis says what only it knows', () => {
  const countOf = (haystack, needle) => haystack.split(needle).length - 1

  it('never says the fold verdict more than once in one cell', async () => {
    const { container } = await mounted()
    const cell = rowFor(container, 'DDD').querySelector('.status-cell').textContent
    expect(countOf(cell, 'not folded')).toBe(1)
    // and the REASON is still there — the repetition went, the fact did not
    expect(cell).toMatch(/oversize/)
  })

  it('does not repeat the fold verdict on a failed fold either', async () => {
    const { container } = await mounted()
    const cell = rowFor(container, 'BBB').querySelector('.status-cell').textContent
    expect(countOf(cell.replace('fold failed', 'FOLDVERDICT'), 'fold failed')).toBe(0)
    expect(cell).toMatch(/CUDA out of memory/)
  })

  it('never joins the disposition and the rank cause into one contradictory sentence', async () => {
    getRanking.mockResolvedValue({ rows: [] })
    getCoverage.mockResolvedValue({
      ...COVERAGE,
      rows: [{ ...COVERAGE.rows[0], disposition: 'ranked', fold_status: 'folded' }],
    })
    listAnalyses.mockResolvedValue([ANALYSES[0]])
    const { container } = await mounted()
    const cell = rowFor(container, 'AAA').querySelector('.status-cell')
    const disposition = cell.querySelector('.status-disposition').textContent
    // ⚠ the disposition line states the partition and NOTHING else
    expect(disposition.trim()).toBe('in the ranking set')
    const cause = cell.querySelector('.status-cause')
    expect(cause).toBeTruthy()
    // ⚠ and the cause names which question it answers, so "in the set" and "no rank" cannot read
    //   as one self-contradicting sentence
    expect(cause.textContent).toMatch(/^no rank — /)
  })
})

// ⚠⚠ FOLLOW-UP 2 — AND THE REASON IT IS A TABLE OF BRANCHES RATHER THAN A CASE. Follow-up 1
// suppressed the cause wherever the FOLD axis carried it, and the deployed page then read
// *"held out of ranking · no rank — held out · folded"* — the same repetition one axis over. Two
// rounds on one cell is the argument for enumerating what `rankCause` can return and checking each
// against what the other axes say.
describe('D-155 follow-up 2 · the cause shows only where it adds something', () => {
  it('drops a cause that merely restates the disposition', async () => {
    const { container } = await mounted()
    const cell = rowFor(container, 'CCC').querySelector('.status-cell')   // held out, folded
    expect(cell.querySelector('.status-disposition').textContent.trim()).toBe('held out of ranking')
    expect(cell.querySelector('.status-cause')).toBeNull()
    expect(cell.textContent.split('held out').length - 1).toBe(1)
  })

  it('keeps the reason for the hold on the row, as the axis title', async () => {
    const { container } = await mounted()
    const line = rowFor(container, 'CCC').querySelector('.status-disposition')
    // ⚠ "held out" with no reason invites the reader to supply one; D-021's is a property of the
    //   PARTITION, so it rides on the axis rather than becoming a fourth line.
    expect(line.getAttribute('title')).toMatch(/boundary method is not comparable \(D-021\)/)
    expect(line.getAttribute('title')).toMatch(/not a judgement about the target/)
  })

  it('keeps a cause that says something the other axes do not', async () => {
    // a ranked, folded row below the pre-registered floor: nothing else on the row explains it
    getRanking.mockResolvedValue({ rows: [] })
    getCoverage.mockResolvedValue({
      ...COVERAGE, rows: [{ ...COVERAGE.rows[0], disposition: 'ranked', fold_status: 'folded' }],
    })
    listAnalyses.mockResolvedValue([{ ...ANALYSES[0], mean_plddt: 44.1 }])
    const { container } = await mounted()
    const cause = rowFor(container, 'AAA').querySelector('.status-cause')
    expect(cause).toBeTruthy()
    expect(cause.textContent).toMatch(/^no rank — /)
  })

  it('never swallows a cause because it starts with the disposition word', () => {
    // ⚠⚠ THE TRAP THIS AVOIDS, AS A UNIT: "excluded by the pre-registered floor" begins with
    // `excluded` and belongs on a RANKED row. A `startsWith` gate would have deleted it.
    expect(causeAddsSomething('excluded by the pre-registered mean pLDDT floor of 50', 'ranked'))
      .toBe(true)
    expect(causeAddsSomething('held out', 'held_out')).toBe(false)
    expect(causeAddsSomething('excluded', 'excluded')).toBe(false)
    expect(causeAddsSomething('no ranking run is currently served', 'ranked')).toBe(true)
    expect(causeAddsSomething('unranked — no cause recorded', 'ranked')).toBe(true)
    expect(causeAddsSomething(null, 'ranked')).toBe(false)
  })
})

describe('D-155 · the Rank cell after the cause moved out of it', () => {
  it('shows the integer for a ranked row', async () => {
    const { container } = await mounted()
    expect(rowFor(container, 'AAA').querySelector('.col-rank-num').textContent.trim()).toBe('1')
  })

  it('names the category for an unranked row, and never shows a bare dash', async () => {
    const { container } = await mounted()
    const cell = rowFor(container, 'DDD').querySelector('.col-rank-num')
    expect(cell.textContent.trim()).toBe('unranked')
    expect(cell.textContent.trim()).not.toBe('—')
    // the cause is still on the row, one cell right, and still reachable on hover
    expect(cell.querySelector('.rank-absent').getAttribute('title')).toBeTruthy()
  })
})
