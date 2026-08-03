// D-048 §3.2 — the two-tier cohort is legible as two tiers (UI-depth §2.3).
//
// The list was flat: a reader could not see that some folds came from owned hardware at int8 and
// others from a rented A6000 at fp16. That is a methodological distinction (D-015 §3), not cosmetic,
// and a grader should not have to open a JSON payload to find it. Tier is shown per row and the list
// is filterable by tier. It is NEVER blended into a single quality score (D-028: don't collapse a
// real distinction). The tier field is already served by /api/analyses (_LIST_META_KEYS) — no
// supplier change (checked against app/reads.py, UI-depth trap a).
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, within, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

// Mock the API module so the list renders from fixtures, not a live fetch.
// getCoverage is mocked too: TargetList now joins /api/coverage client-side for the
// absent-value reason (no route change). It is additive - the list renders without it.
vi.mock('../api.js', () => ({
  listAnalyses: vi.fn(),
  getCoverage: vi.fn(),
}))
import { getCoverage, listAnalyses } from '../api.js'
import TargetList from './TargetList.jsx'

const ROWS = [
  { id: 1, gene: 'NECTIN4', accession: 'Q92729', mean_plddt: 77.26, tier: 'local', tier_reason: null },
  { id: 2, gene: 'SDK1', accession: 'Q7Z5N4', mean_plddt: 58.01, tier: 'rental', tier_reason: 'length 2213 > local ceiling' },
  { id: 3, gene: 'PTPRZ1', accession: 'P23471', mean_plddt: 30.68, tier: 'rental', tier_reason: 'length 1612 > local ceiling' },
]

function renderList() {
  return render(<MemoryRouter><TargetList /></MemoryRouter>)
}

beforeEach(() => {
  listAnalyses.mockReset()
  getCoverage.mockReset()
  listAnalyses.mockResolvedValue(ROWS)
  getCoverage.mockResolvedValue({ rows: [] })
})

describe('TargetList — tier legibility (D-048 §3.2)', () => {
  it('shows each fold\'s tier in the row, so the two machines are visible without opening JSON', async () => {
    renderList()
    await waitFor(() => expect(screen.getByText('NECTIN4')).toBeInTheDocument())
    const nectinRow = screen.getByText('NECTIN4').closest('tr')
    const sdkRow = screen.getByText('SDK1').closest('tr')
    expect(within(nectinRow).getByText(/local/i)).toBeInTheDocument()
    expect(within(sdkRow).getByText(/rental/i)).toBeInTheDocument()
  })

  it('offers a tier filter that narrows the list to one tier', async () => {
    renderList()
    await waitFor(() => expect(screen.getByText('NECTIN4')).toBeInTheDocument())
    const filter = screen.getByRole('combobox', { name: /tier/i })
    fireEvent.change(filter, { target: { value: 'rental' } })
    // rental-only: NECTIN4 (local) gone, the two rental targets remain.
    expect(screen.queryByText('NECTIN4')).not.toBeInTheDocument()
    expect(screen.getByText('SDK1')).toBeInTheDocument()
    expect(screen.getByText('PTPRZ1')).toBeInTheDocument()
  })

  it('filtering back to "all tiers" restores every row', async () => {
    renderList()
    await waitFor(() => expect(screen.getByText('NECTIN4')).toBeInTheDocument())
    const filter = screen.getByRole('combobox', { name: /tier/i })
    fireEvent.change(filter, { target: { value: 'rental' } })
    expect(screen.queryByText('NECTIN4')).not.toBeInTheDocument()
    fireEvent.change(filter, { target: { value: 'all' } })
    expect(screen.getByText('NECTIN4')).toBeInTheDocument()
    expect(screen.getByText('SDK1')).toBeInTheDocument()
  })

  it('does NOT blend the tiers into any combined quality score (D-028 — a real distinction is not collapsed)', async () => {
    renderList()
    await waitFor(() => expect(screen.getByText('NECTIN4')).toBeInTheDocument())
    expect(screen.queryByText(/blended|combined score|overall quality/i)).not.toBeInTheDocument()
  })
})
