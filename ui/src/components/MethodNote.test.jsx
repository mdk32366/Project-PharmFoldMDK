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

  // D-127-B — Spec §7 makes this section MANDATORY. D-127 is not "done"
  // without it, so these are ship checks, not documentation polish.
  it('adds the mandatory D-127-B addendum naming the whole four-step stitch-path train', async () => {
    getCoverage.mockResolvedValue(FIXTURE)
    const { container, getByTestId } = renderMethod()
    await waitFor(() => expect(container.textContent).toMatch(/3 ranked-and-folded of 7/))
    const add = getByTestId('piecewise-kabsch-method-addendum')
    const t = add.textContent
    expect(t).toMatch(/Assembler/)
    expect(t).toMatch(/D-125 Kabsch/)
    expect(t).toMatch(/D-126 confidence/)
    expect(t).toMatch(/D-127 piecewise/)
    expect(t).toMatch(/28–68 Å/)
    expect(t).toMatch(/2939/)
    expect(t).toMatch(/3272/)
    expect(t).toMatch(/3432/)
    expect(t).toMatch(/per UniProt domain/)
    expect(t).toMatch(/No trim loop/)
    expect(t).toMatch(/linkers|linker/)
    expect(t).toMatch(/N-terminal/)
    expect(t).toMatch(/default served/)
    expect(t).not.toMatch(/seams solved|Kabsch aligned|we ran Kabsch|full-length AF-quality/)
  })

  it('names the D-127 refuse table, keeps the 10.0 Å gate, and calls the numbers measurements', async () => {
    getCoverage.mockResolvedValue(FIXTURE)
    const { container, getByTestId } = renderMethod()
    await waitFor(() => expect(container.textContent).toMatch(/3 ranked-and-folded of 7/))
    const t = getByTestId('piecewise-kabsch-method-addendum').textContent
    expect(t).toMatch(/fewer than three Cα/)
    expect(t).toMatch(/10\.0 Å/)
    expect(t).toMatch(/in a line/)
    expect(t).toMatch(/no domain covers the glue/)
    expect(t).toMatch(/refuse writes a record/)
    expect(t).toMatch(/stays/)
    expect(t).toMatch(/measurements/)
    expect(t).toMatch(/not scientifically solved/)
    expect(t).toMatch(/not medical advice/)
    expect(t).toMatch(/does not invent/)
    expect(t).not.toMatch(/seams solved|Kabsch aligned|full-length AF-quality/)
  })

  // Matt GO via Emma 2026-09-05 — Method §7 must disclose the D-127 OPS
  // result as recorded. An accept count without its regress is the
  // softening the GO forbids, so these are ship checks.
  it('discloses the D-127 OPS run with its named regress, not an accept count alone', async () => {
    getCoverage.mockResolvedValue(FIXTURE)
    const { container, getByTestId } = renderMethod()
    await waitFor(() => expect(container.textContent).toMatch(/3 ranked-and-folded of 7/))
    const t = getByTestId('piecewise-kabsch-method-addendum').textContent
    expect(t).toMatch(/PASS 17/)
    expect(t).toMatch(/REFUSE 10/)
    expect(t).toMatch(/FAIL 0/)
    expect(t).toMatch(/e49bf34/)
    // recovered_of_primary_three = 0, each reason named.
    expect(t).toMatch(/recovered_of_primary_three/)
    expect(t).toMatch(/2939/)
    expect(t).toMatch(/linker_jump_gt_10/)
    expect(t).toMatch(/3272/)
    expect(t).toMatch(/rmsd_gt_10/)
    expect(t).toMatch(/3432/)
    expect(t).toMatch(/no_domain_pieces/)
    // The refuse histogram, counts and ids.
    expect(t).toMatch(/×7/)
    expect(t).toMatch(/×2/)
    expect(t).toMatch(/×1/)
    expect(t).toMatch(/2938/)
    expect(t).toMatch(/3179/)
    expect(t).toMatch(/3190/)
    expect(t).toMatch(/3321/)
    expect(t).toMatch(/3368/)
    expect(t).toMatch(/3566/)
    expect(t).toMatch(/3394/)
    // Named regress sits beside the accept count.
    expect(t).toMatch(/n_d126_refuse_d127_pass/)
    expect(t).toMatch(/named finding/)
    // Provenance: as-recorded, not our measurement.
    expect(t).toMatch(/as recorded/i)
    expect(t).toMatch(/not re-measured here/)
  })

  it('says plainly that D-126 remains the best path, keeps every gate, and never flips the served path', async () => {
    getCoverage.mockResolvedValue(FIXTURE)
    const { container, getByTestId } = renderMethod()
    await waitFor(() => expect(container.textContent).toMatch(/3 ranked-and-folded of 7/))
    const t = getByTestId('piecewise-kabsch-method-addendum').textContent
    expect(t).toMatch(/D-126 remains the best experimental path/)
    expect(t).toMatch(/so far/)
    expect(t).toMatch(/did not pay off/)
    // Trinity amend: the claim carries its number, as recorded.
    expect(t).toMatch(/D-126 OPS recovered 2 of its primary 5/)
    expect(t).toMatch(/3368/)
    expect(t).toMatch(/3394/)
    expect(t).toMatch(/0 of 3/)
    expect(t).toMatch(/not re-measured here/)
    // And that D-127 gave both of them back.
    expect(t).toMatch(/gave back/)
    expect(t).toMatch(/refuse list/)
    // Exact Spec §11 confusion keys, by name.
    expect(t).toMatch(/n_d125_pass_d127_refuse/)
    expect(t).toMatch(/n_d126_pass_d127_refuse/)
    expect(t).toMatch(/allowed outcome/)
    expect(t).toMatch(/No threshold moved/)
    expect(t).toMatch(/default served structure is still the assembler/)
    expect(t).toMatch(/never a pass count/)
    // 17 accepted parents are recorded outcomes, not solved joins.
    expect(t).toMatch(/17 recorded outcomes/)
    expect(t).toMatch(/not 17 solved joins/)
    expect(t).not.toMatch(/seams solved|Kabsch aligned|we ran Kabsch|full-length AF-quality/)
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
