import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import CensusStructuralRank, { STRUCTURAL_RANK_BANNER } from './CensusStructuralRank.jsx'
import * as api from '../api.js'

vi.mock('../api.js', async () => {
  const actual = await vi.importActual('../api.js')
  return {
    ...actual,
    getCensusStructuralRanking: vi.fn(),
  }
})

const FIXTURE = {
  result_status: 'valid',
  n_candidates: 2,
  rows: [
    { rank: 1, gene: 'GABBR2', accession: 'O75899', structural_score: 0.8443, flags: ['ecd_intermittent'] },
    { rank: 2, gene: 'DEMO', accession: 'P00000', structural_score: 0.5, flags: [] },
  ],
}

describe('D-169 CensusStructuralRank', () => {
  beforeEach(() => {
    vi.mocked(api.getCensusStructuralRanking).mockReset()
  })

  it('exports getCensusStructuralRanking from api.js', async () => {
    expect(typeof api.getCensusStructuralRanking).toBe('function')
  })

  it('shows STRUCTURAL_ONLY banner and rows from the client', async () => {
    vi.mocked(api.getCensusStructuralRanking).mockResolvedValue(FIXTURE)
    render(
      <MemoryRouter>
        <CensusStructuralRank />
      </MemoryRouter>,
    )
    await waitFor(() => expect(screen.getByTestId('structural-only-banner')).toBeTruthy())
    const banner = screen.getByTestId('structural-only-banner').textContent
    expect(banner).toMatch(/STRUCTURAL_ONLY/i)
    expect(banner).toMatch(/Not ADC readiness/i)
    expect(banner).toMatch(/Not the cohort-82 learned scorer/i)
    expect(banner).toBe(STRUCTURAL_RANK_BANNER)
    expect(api.getCensusStructuralRanking).toHaveBeenCalled()
    expect(screen.getByText('GABBR2')).toBeTruthy()
    expect(screen.getByText('O75899')).toBeTruthy()
    expect(screen.getByText('0.8443')).toBeTruthy()
    expect(screen.getByText(/ecd_intermittent/)).toBeTruthy()
  })

  it('does not invent ranks when result_status is not valid', async () => {
    vi.mocked(api.getCensusStructuralRanking).mockResolvedValue({
      result_status: 'not_run',
      rows: [{ rank: 1, gene: 'FAKE', accession: 'X', structural_score: 1 }],
    })
    render(
      <MemoryRouter>
        <CensusStructuralRank />
      </MemoryRouter>,
    )
    await waitFor(() => expect(screen.getByRole('alert')).toBeTruthy())
    expect(screen.queryByText('FAKE')).toBeNull()
  })
})
