import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import CensusTable from './CensusTable.jsx'

const FIXTURE = [
  {
    id: 1,
    accession: 'O75899',
    gene: 'GABBR2',
    label: 'Gabbr2',
    span_aa: 100,
    topology: 'contiguous',
    mean_plddt: 80.1,
    tranche: 1,
    folded: true,
    scored: false,
    structure_kind: 'oneshot',
    structure_kind_label: 'single-pass',
    structural_rank: 1,
    structural_score: 0.8443,
    structural_rank_status: 'valid',
  },
  {
    id: 2,
    accession: 'P00000',
    gene: 'NONE',
    label: 'None',
    span_aa: 50,
    topology: 'contiguous',
    mean_plddt: null,
    tranche: 2,
    folded: false,
    scored: false,
    structure_kind: 'none',
    structural_rank: null,
    structural_score: null,
    structural_rank_status: 'valid',
  },
]

describe('D-170 CensusTable structural columns', () => {
  it('shows STRUCTURAL_ONLY chrome and rank/score cells', () => {
    render(
      <MemoryRouter>
        <CensusTable rows={FIXTURE} />
      </MemoryRouter>,
    )
    expect(screen.getByTestId('structural-rank-columns-note').textContent).toMatch(/STRUCTURAL_ONLY/)
    expect(screen.getByTestId('structural-rank-columns-note').textContent).toMatch(/cohort-82/)
    const ranks = screen.getAllByTestId('structural-rank-cell')
    const scores = screen.getAllByTestId('structural-score-cell')
    expect(ranks[0].textContent).toBe('1')
    expect(scores[0].textContent).toBe('0.8443')
    expect(ranks[1].textContent).toBe('—')
  })
})
