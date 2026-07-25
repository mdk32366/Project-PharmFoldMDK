// D-050: MethodNote's coverage line must be DERIVED from /api/coverage, not hardcoded.
// The stale "40 ranked-and-folded of 82" contradicted the live-computed CoverageLine (67) on the
// deployed app. These tests pin derivation against a fixture coverage payload.
import { render, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../api.js', () => ({ getCoverage: vi.fn() }))
import { getCoverage } from '../api.js'
import MethodNote from './MethodNote.jsx'

// DISTINCTIVE: ranked-and-folded = 3, denominator = 7 — cannot coincide with "40 of 82".
// The ranked-but-not-folded row must be excluded from the intersection (D-024).
const FIXTURE = {
  coverage: { denominator: 7, ranked: 4, held_out: 2, excluded: 1 },
  failed: 0,
  rows: [
    { disposition: 'ranked', fold_status: 'folded' },
    { disposition: 'ranked', fold_status: 'folded' },
    { disposition: 'ranked', fold_status: 'folded' },
    { disposition: 'ranked', fold_status: 'not_folded' }, // ranked but NOT folded -> excluded
    { disposition: 'held_out', fold_status: 'folded' },
    { disposition: 'held_out', fold_status: 'not_folded' },
    { disposition: 'excluded', fold_status: 'not_folded' },
  ],
}

const renderMethod = () => render(<MemoryRouter><MethodNote /></MemoryRouter>)

beforeEach(() => vi.clearAllMocks())

describe('MethodNote — coverage line derived from /api/coverage, not hardcoded (D-050)', () => {
  it('renders ranked-and-folded of denominator from the payload', async () => {
    getCoverage.mockResolvedValue(FIXTURE)
    const { container } = renderMethod()
    await waitFor(() => expect(container.textContent).toMatch(/3 ranked-and-folded of 7/))
  })

  it('does NOT render the stale "40 ranked-and-folded of 82" literal', async () => {
    getCoverage.mockResolvedValue(FIXTURE)
    const { container } = renderMethod()
    await waitFor(() => expect(container.textContent).toMatch(/3 ranked-and-folded of 7/))
    expect(container.textContent).not.toMatch(/40 ranked-and-folded of 82/)
  })
})
