// D-050: MethodNote's coverage line must be DERIVED from /api/coverage, not hardcoded.
// The stale "40 ranked-and-folded of 82" contradicted the live-computed CoverageLine (67) on the
// deployed app. These tests pin derivation against a fixture coverage payload.
import { render, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../api.js', () => ({
  getCensusSummary: vi.fn(), getCoverage: vi.fn() }))
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

  it('names Blackwell hold-48 and assembler-only stitch, not A6000 as the only rental', async () => {
    getCoverage.mockResolvedValue(FIXTURE)
    const { container } = renderMethod()
    await waitFor(() => expect(container.textContent).toMatch(/3 ranked-and-folded of 7/))
    expect(container.textContent).toMatch(/Blackwell/)
    expect(container.textContent).toMatch(/assembler/)
    expect(container.textContent).toMatch(/not a Kabsch/)
    expect(container.textContent).toMatch(/A6000/)
  })
})

describe('MethodNote — D-121 hold-48 8th-grade explainer (additive, not a gut)', () => {
  it('renders tiles, glue, assembler-not-Kabsch, unsolved seam, and CLOSED rental', async () => {
    getCoverage.mockResolvedValue(FIXTURE)
    const { container, getByTestId } = renderMethod()
    await waitFor(() => expect(container.textContent).toMatch(/3 ranked-and-folded of 7/))
    const block = getByTestId('hold48-explainer')
    expect(block.textContent).toMatch(/overlapping tiles/)
    expect(block.textContent).toMatch(/glue/)
    expect(block.textContent).toMatch(/1656/)
    expect(block.textContent).toMatch(/128/)
    expect(block.textContent).toMatch(/winner-tile assembler/)
    expect(block.textContent).toMatch(/not Kabsch/)
    expect(block.textContent).toMatch(/88\.76/)
    expect(block.textContent).toMatch(/not scientifically solved/)
    expect(block.textContent).toMatch(/CLOSED/)
    expect(block.textContent).not.toMatch(/seams solved|Kabsch aligned|waiting on rented capacity/)
  })

  it('adds a D-125-B Kabsch does / does-not addendum without claiming seams solved', async () => {
    getCoverage.mockResolvedValue(FIXTURE)
    const { container, getByTestId } = renderMethod()
    await waitFor(() => expect(container.textContent).toMatch(/3 ranked-and-folded of 7/))
    const add = getByTestId('kabsch-method-addendum')
    expect(add.textContent).toMatch(/What Kabsch does/)
    expect(add.textContent).toMatch(/What Kabsch does not do/)
    expect(add.textContent).toMatch(/default served/)
    expect(add.textContent).toMatch(/does not run again/)
    expect(add.textContent).toMatch(/not medical advice/)
    expect(add.textContent).toMatch(/not scientifically solved/)
    expect(add.textContent).toMatch(/does not invent/)
    expect(add.textContent).not.toMatch(/seams solved|Kabsch aligned|we ran Kabsch|full-length AF-quality/)
  })

  it('adds a D-126-B weighted/trimmed Kabsch does / does-not addendum without claiming seams solved', async () => {
    getCoverage.mockResolvedValue(FIXTURE)
    const { container, getByTestId } = renderMethod()
    await waitFor(() => expect(container.textContent).toMatch(/3 ranked-and-folded of 7/))
    const add = getByTestId('confidence-kabsch-method-addendum')
    expect(add.textContent).toMatch(/What overlap-confidence Kabsch does/)
    expect(add.textContent).toMatch(/What overlap-confidence Kabsch does not do/)
    expect(add.textContent).toMatch(/default served/)
    expect(add.textContent).toMatch(/does not run again/)
    expect(add.textContent).toMatch(/not medical advice/)
    expect(add.textContent).toMatch(/not scientifically solved/)
    expect(add.textContent).toMatch(/does not invent/)
    expect(add.textContent).toMatch(/confidence_kabsch/)
    expect(add.textContent).not.toMatch(/seams solved|Kabsch aligned|we ran Kabsch|full-length AF-quality/)
  })

  it('keeps the standing MethodNote claims (does not gut D-028 / D-050 / D-051)', async () => {
    getCoverage.mockResolvedValue(FIXTURE)
    const { container } = renderMethod()
    await waitFor(() => expect(container.textContent).toMatch(/3 ranked-and-folded of 7/))
    expect(container.textContent).toMatch(/What this system claims/)
    expect(container.textContent).toMatch(/Where the deep learning runs/)
    expect(container.textContent).toMatch(/What it will never do/)
    expect(container.textContent).toMatch(/3 ranked-and-folded of 7/)
  })
})
