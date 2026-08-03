// Sortable column headers on the target list, and the absent-value rule in the rendered table.
//
// The pure rule is unit-tested in `src/sortRows.test.js`; this file asserts the WIRING — that clicking
// a header actually reorders rows, that the active sort is visible, that the default load order is
// unchanged, that filtering and sorting compose, and that the absent row survives sorting with its
// REAL reason rather than a bare dash.
//
// ⚠ The absent row here is not a fixture invention. IGF2R is on the deployed list with
// `mean_plddt: null` — its fold hit a CUDA OOM at 2,491 aa, verified at the DB (`pdb_path` null, so
// no structure and no pLDDT to have lost; 79 of 80 rows are structure+pLDDT, 1 is neither, and zero
// are in either bug shape). The null is honest, and `?? 0` was rendering it as the worst score.
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, within, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

vi.mock('../api.js', () => ({ listAnalyses: vi.fn(), getCoverage: vi.fn() }))
import { listAnalyses, getCoverage } from '../api.js'
import TargetList from './TargetList.jsx'

// Distinct values so every ordering is unambiguous.
const ROWS = [
  { id: 1, gene: 'NECTIN4', accession: 'Q92729', mean_plddt: 77.26, tier: 'local', tier_reason: null },
  { id: 2, gene: 'SDK1', accession: 'A7Z5N4', mean_plddt: 58.01, tier: 'rental', tier_reason: 'length 2213 > local ceiling' },
  { id: 3, gene: 'PTPRZ1', accession: 'P23471', mean_plddt: 30.68, tier: 'rental', tier_reason: 'length 1612 > local ceiling' },
  { id: 57, gene: 'IGF2R', accession: 'P11717', mean_plddt: null, tier: 'rental', tier_reason: 'whole_sequence_fold' },
]

// /api/coverage carries fold_status + fail_reason; /api/analyses does not. Joined client-side by
// accession (the D-068 TargetScorerPanel pattern) so the absent cluster can state its real reason
// with NO route change.
const COVERAGE = {
  rows: [
    { accession: 'Q92729', gene: 'NECTIN4', fold_status: 'folded', fail_reason: null },
    { accession: 'A7Z5N4', gene: 'SDK1', fold_status: 'folded', fail_reason: null },
    { accession: 'P23471', gene: 'PTPRZ1', fold_status: 'folded', fail_reason: null },
    {
      accession: 'P11717', gene: 'IGF2R', fold_status: 'failed',
      fail_reason: "CUDA OOM folding 2491 aa at chunk_size=32 — the trunk's triangular attention is O(L^3)",
    },
  ],
}

const renderList = () => render(<MemoryRouter><TargetList /></MemoryRouter>)
const bodyGenes = () =>
  screen.getAllByRole('row').slice(1).map((r) => r.querySelector('td')?.textContent.trim())

const header = (re) => screen.getAllByRole('columnheader').find((h) => re.test(h.textContent))
const clickHeader = (re) => {
  const h = header(re)
  fireEvent.click(h.querySelector('button') || h)
}

beforeEach(() => {
  listAnalyses.mockReset()
  getCoverage.mockReset()
  listAnalyses.mockResolvedValue(ROWS)
  getCoverage.mockResolvedValue(COVERAGE)
})

async function ready() {
  await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
  await waitFor(() => expect(screen.getAllByRole('row').length).toBeGreaterThan(1))
}

describe('default order is unchanged (the ceiling-at-a-glance story depends on it)', () => {
  it('loads sorted by mean pLDDT descending, with the absent row trailing', async () => {
    renderList()
    await ready()
    expect(bodyGenes()).toEqual(['NECTIN4', 'SDK1', 'PTPRZ1', 'IGF2R'])
  })
})

describe('every existing column sorts, asc → desc → back to default', () => {
  it('sorts by Gene alphabetically, then reverses, then restores the default', async () => {
    renderList()
    await ready()
    clickHeader(/gene/i)
    expect(bodyGenes()).toEqual(['IGF2R', 'NECTIN4', 'PTPRZ1', 'SDK1'])
    clickHeader(/gene/i)
    expect(bodyGenes()).toEqual(['SDK1', 'PTPRZ1', 'NECTIN4', 'IGF2R'])
    clickHeader(/gene/i)
    expect(bodyGenes()).toEqual(['NECTIN4', 'SDK1', 'PTPRZ1', 'IGF2R'])   // default restored
  })

  it('sorts by Accession alphabetically', async () => {
    renderList()
    await ready()
    clickHeader(/accession/i)
    expect(bodyGenes()).toEqual(['SDK1', 'IGF2R', 'PTPRZ1', 'NECTIN4'])   // A7 < P11 < P23 < Q92
  })

  it('sorts by mean pLDDT ascending on first click', async () => {
    renderList()
    await ready()
    clickHeader(/mean pLDDT/i)
    expect(bodyGenes()).toEqual(['PTPRZ1', 'SDK1', 'NECTIN4', 'IGF2R'])
  })
})

describe('⚠ the absent-value rule, in the rendered table', () => {
  it('keeps the null-pLDDT row present and labelled in BOTH directions, never as the lowest number', async () => {
    renderList()
    await ready()
    clickHeader(/mean pLDDT/i)                     // ascending
    let order = bodyGenes()
    expect(order).toContain('IGF2R')
    expect(order.indexOf('IGF2R')).toBeGreaterThan(order.indexOf('PTPRZ1'))
    clickHeader(/mean pLDDT/i)                     // descending
    order = bodyGenes()
    expect(order).toContain('IGF2R')
    expect(order[0]).not.toBe('IGF2R')             // absence is not the maximum either
  })

  it('renders the absent row with an em-dash, never a coerced 0.00', async () => {
    renderList()
    await ready()
    const row = screen.getByText('IGF2R').closest('tr')
    expect(within(row).getByText('—')).toBeInTheDocument()
    expect(row.textContent).not.toMatch(/\b0\.00\b/)
  })

  it('states the absent row\'s REAL reason, not a generic dash (owner ruling)', async () => {
    // A pretty label over a wrong null would paper over a data bug. This null is honest — the fold
    // OOM'd — so the row must say so rather than leaving the reader to guess.
    renderList()
    await ready()
    const row = screen.getByText('IGF2R').closest('tr')
    expect(row.textContent).toMatch(/fold failed|failed/i)
    expect(row.textContent).toMatch(/OOM|memory|2491/i)
  })
})

describe('the active sort is visible — an unlabelled sort is a silent reordering', () => {
  it('marks the active column and its direction via aria-sort', async () => {
    renderList()
    await ready()
    clickHeader(/gene/i)
    expect(header(/gene/i)).toHaveAttribute('aria-sort', 'ascending')
    clickHeader(/gene/i)
    expect(header(/gene/i)).toHaveAttribute('aria-sort', 'descending')
    // and the other columns are not marked
    expect(header(/accession/i)).toHaveAttribute('aria-sort', 'none')
  })
})

describe('sorting composes with the tier filter, and adds no new axis', () => {
  it('filters to one tier, then sorts within it', async () => {
    renderList()
    await ready()
    fireEvent.change(screen.getByLabelText(/tier/i), { target: { value: 'rental' } })
    expect(bodyGenes()).toEqual(['SDK1', 'PTPRZ1', 'IGF2R'])
    clickHeader(/gene/i)
    expect(bodyGenes()).toEqual(['IGF2R', 'PTPRZ1', 'SDK1'])
  })

  it('⚠ introduces no blended/composite sort key (D-028)', async () => {
    const { container } = renderList()
    await ready()
    for (const banned of [/\bcombined score\b/i, /\bblended\b/i, /\bquality score\b/i, /\boverall score\b/i]) {
      expect(container.textContent).not.toMatch(banned)
    }
  })

  it('sorting by Tier implies no quality order — it stays a label', async () => {
    renderList()
    await ready()
    const tierHeader = header(/tier/i)
    if (tierHeader?.querySelector('button')) {
      fireEvent.click(tierHeader.querySelector('button'))
      expect(bodyGenes()).toHaveLength(ROWS.length)     // nothing dropped
    }
    expect(screen.getByRole('table').textContent).not.toMatch(/better|worse|higher quality/i)
  })
})

describe('resilience — the coverage join is additive, never load-bearing for the list', () => {
  it('still renders every row if /api/coverage fails', async () => {
    // The list is the primary surface; a failed secondary fetch must degrade the reason text, not
    // the list. Coverage supplies WHY a value is absent, never WHETHER the row exists.
    getCoverage.mockRejectedValue(new Error('coverage down'))
    renderList()
    await ready()
    expect(bodyGenes()).toEqual(['NECTIN4', 'SDK1', 'PTPRZ1', 'IGF2R'])
  })
})
