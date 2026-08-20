import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'

// ⚠⚠ THE DEFAULT SORT WAS A DE FACTO RANKING BY A THIRD OF THE REAL ONE (owner ruling 2026-08-21).
//
// `/targets` defaulted to mean pLDDT descending while `CensusTable.jsx` explicitly refuses that on
// the census — *"a self-reported confidence into a de facto ranking."* Same reasoning, opposite
// behaviour, two surfaces. ⚠ And it is worse here: the cohort IS ranked, by the scorer, and `F-051`
// measures `membrane_proximal_plddt` at **32.2%** of the scorer's attribution. So the page was
// ordered by roughly a third of the real ranking while the real one sat one fetch away.
//
// ⚠⚠ TA2 — THE 26 UNRANKED ROWS ARE PARTITIONED, NOT POSITIONED. Sinking them would rank them 57th
// through 82nd. **They are not last; they are unranked, and a sort that sinks them is a ranking of
// scoreability** — the same defect in a new coat.

vi.mock('../api.js', () => ({
  listAnalyses: vi.fn(), getCoverage: vi.fn(), getRanking: vi.fn(),
}))
import { listAnalyses, getCoverage, getRanking } from '../api.js'
import TargetList, { rankCause, PLDDT_FLOOR } from './TargetList.jsx'

// Two ranked, and one row for each unranked cause that exists at v99.
const ROWS = [
  { id: 1, gene: 'NECTIN4', accession: 'Q92729', mean_plddt: 88.10, tier: 'local', disposition: 'ranked' },
  { id: 2, gene: 'FAM171A1', accession: 'Q5VUB5', mean_plddt: 61.20, tier: 'local', disposition: 'ranked' },
  // below_floor — ATP2B2 is the real nearest-miss: 49.46 against a floor of 50
  { id: 3, gene: 'ATP2B2', accession: 'Q01814', mean_plddt: 49.46, tier: 'rental', disposition: 'ranked' },
  { id: 4, gene: 'PTPRZ1', accession: 'P23471', mean_plddt: 30.68, tier: 'rental', disposition: 'ranked' },
  // held_out, folded
  { id: 5, gene: 'TMEM30A', accession: 'Q9NV96', mean_plddt: 70.10, tier: 'local', disposition: 'held_out' },
  // held_out AND the fold failed — the two-cause row
  { id: 57, gene: 'IGF2R', accession: 'P11717', mean_plddt: null, tier: 'rental', disposition: 'held_out' },
]
const COVERAGE = {
  rows: [
    ...ROWS.map((r) => ({
      accession: r.accession, gene: r.gene, disposition: r.disposition,
      fold_status: r.mean_plddt != null ? 'folded' : 'failed',
      fail_reason: r.mean_plddt != null ? null : 'CUDA OOM folding 2491 aa at chunk_size=32',
    })),
    // a cohort member with no analysis row at all
    { accession: 'Q8WXI7', gene: 'MUC16', disposition: 'excluded', fold_status: 'not_folded',
      exclusion_reason: 'oversize: MUC16 (CA-125), 14451 aa — folds on no single card' },
  ],
}
// ⚠ ranks deliberately DISAGREE with pLDDT order, so the two defaults are distinguishable
const RANKING = { rows: [
  { accession: 'Q5VUB5', rank: 1, gene: 'FAM171A1' },
  { accession: 'Q92729', rank: 2, gene: 'NECTIN4' },
] }

const draw = () => render(<MemoryRouter><TargetList /></MemoryRouter>)
const ready = () => waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
const genesIn = (tbody) =>
  [...tbody.querySelectorAll('tr')].map((r) => r.querySelectorAll('td')[1]?.textContent.trim())
    .filter(Boolean)

beforeEach(() => {
  listAnalyses.mockResolvedValue(ROWS)
  getCoverage.mockResolvedValue(COVERAGE)
  getRanking.mockResolvedValue(RANKING)
})

// ── TA1 / TA4 ────────────────────────────────────────────────────────────────────────────────────
describe('the default order is the scorer’s, not a proxy for it', () => {
  it('loads in scorer-rank order', async () => {
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.querySelector('tbody').textContent).toMatch(/FAM171A1/))
    // ⚠⚠ THE PROPERTY. FAM171A1 is rank 1 but has a LOWER pLDDT than NECTIN4 (61.20 vs 88.10), so
    // this ordering is impossible under the old pLDDT-descending default. One property, one test.
    expect(genesIn(container.querySelector('tbody'))).toEqual(['FAM171A1', 'NECTIN4'])
  })

  it('announces the rank column as the active sort', async () => {
    draw()
    await ready()
    const rankHeader = screen.getAllByRole('columnheader').find((h) => /rank/i.test(h.textContent))
    expect(rankHeader.getAttribute('aria-sort')).toBe('ascending')
  })
})

// ── TA2 — the partition ──────────────────────────────────────────────────────────────────────────
describe('the unranked are partitioned, never positioned', () => {
  it('keeps unranked rows out of the ranked body entirely', async () => {
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.querySelector('.unranked-group')).not.toBeNull())
    const ranked = genesIn(container.querySelector('tbody'))
    // ⚠ not rows 3..6 of the ranked table — absent from it
    for (const g of ['ATP2B2', 'PTPRZ1', 'TMEM30A', 'IGF2R', 'MUC16']) {
      expect(ranked).not.toContain(g)
    }
    expect(ranked).toEqual(['FAM171A1', 'NECTIN4'])
  })

  it('gives no unranked row a position number of any kind', async () => {
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.querySelector('.unranked-group')).not.toBeNull())
    const group = container.querySelector('.unranked-group')
    for (const tr of group.querySelectorAll('tr.row-unranked')) {
      const cell = tr.querySelector('.col-rank').textContent.trim()
      expect(cell).not.toMatch(/^\d+$/)      // never 3, 4, 5…
      expect(cell).not.toBe('—')             // and never a bare dash
      expect(cell.length).toBeGreaterThan(3) // it is a cause, in words
    }
  })

  it('says the group has no position rather than that it ranks last', async () => {
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.querySelector('.unranked-group')).not.toBeNull())
    const heading = container.querySelector('.unranked-heading').textContent
    expect(heading).toMatch(/no scorer rank/)
    expect(heading).toMatch(/not ranked last/)
  })

  it('orders the group by accession and says the order carries no judgement', async () => {
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.querySelector('.unranked-group')).not.toBeNull())
    const group = container.querySelector('.unranked-group')
    const accs = [...group.querySelectorAll('tr.row-unranked')]
      .map((r) => r.querySelectorAll('td')[2].textContent.trim())
    expect(accs).toEqual([...accs].sort())
    expect(container.querySelector('.unranked-heading').textContent).toMatch(/carries no judgement/)
  })

  it('is visible, never collapsed behind a control', async () => {
    // ⚠ a collapsed group is a filtered default wearing a disclosure control (owner ruling)
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.querySelector('.unranked-group')).not.toBeNull())
    expect(container.querySelector('.unranked-group').closest('details')).toBeNull()
    expect(container.querySelectorAll('tr.row-unranked').length).toBe(5)
  })

  // ⚠ the partition belongs to the RANK AXIS, not to the rows
  it('does not partition when the reader chooses another axis', async () => {
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.querySelector('.unranked-group')).not.toBeNull())
    const h = screen.getAllByRole('columnheader').find((x) => /mean pLDDT/i.test(x.textContent))
    fireEvent.click(h.querySelector('button'))
    expect(container.querySelector('.unranked-group')).toBeNull()
    expect(genesIn(container.querySelector('tbody'))).toContain('ATP2B2')
  })
})

// ── TA2 — the causes ─────────────────────────────────────────────────────────────────────────────
describe('every unranked row states its cause, and a two-cause row states both', () => {
  it('leads with held_out and still reports the failed fold', async () => {
    // ⚠⚠ held_out leads because it is a DECISION, not an event — ruled before a card was involved.
    // ⚠ A row with two causes showing one is an absence with a cause hiding an absence with a cause.
    const cause = rankCause({ rank: null, disposition: 'held_out', fold_status: 'failed' })
    expect(cause).toMatch(/held out/)
    expect(cause).toMatch(/failed/)
    expect(cause.indexOf('held out')).toBeLessThan(cause.indexOf('failed'))
  })

  it('names the pre-registered floor and does not move it', async () => {
    expect(PLDDT_FLOOR).toBe(50)
    const cause = rankCause({ rank: null, disposition: 'ranked', fold_status: 'folded', mean_plddt: 49.46 })
    expect(cause).toMatch(/pre-registered/)
    expect(cause).toMatch(/50/)
  })

  it('shows the nearest excluded value so the cutoff can be judged without moving it', async () => {
    // ⚠ ATP2B2 misses by 0.54. D-060 pre-registered the floor; moving it after seeing which rows
    // fall outside is exactly what pre-registration prevents. The page states it instead.
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.querySelector('.unranked-heading')).not.toBeNull())
    expect(container.querySelector('.unranked-heading').textContent).toMatch(/49\.46/)
  })

  it('never infers below_floor from the mere absence of a rank', async () => {
    // ⚠⚠ the bug caught during the build: a 77.26 fold labelled "excluded by the floor of 50"
    const good = rankCause({ rank: null, disposition: 'ranked', fold_status: 'folded', mean_plddt: 77.26 })
    expect(good).not.toMatch(/floor/)
  })

  it('says so when a row is unranked with no recorded cause', async () => {
    // ⚠ `unranked_unexplained` was EMPTY at v99. This is what must render if it ever fills — F-044
    // hides in a dash, so an absence with no cause must SAY it has no cause.
    expect(rankCause({ rank: null, disposition: 'ranked' })).toMatch(/no cause recorded/)
  })
})

// ── TA3 — the lens is stated where it is applied ─────────────────────────────────────────────────
describe('pLDDT stays available as a lens, and says what it is', () => {
  it('carries the census sentence when the reader chooses it', async () => {
    const { container } = draw()
    await ready()
    expect(container.querySelector('.plddt-lens-note')).toBeNull()
    const h = screen.getAllByRole('columnheader').find((x) => /mean pLDDT/i.test(x.textContent))
    fireEvent.click(h.querySelector('button'))
    const note = container.querySelector('.plddt-lens-note').textContent
    expect(note).toMatch(/self-reported/)
    expect(note).toMatch(/32\.2%/)          // ⚠ the figure that makes it a ruling, not a preference
    expect(note).toMatch(/not the scorer/i)
  })
})
