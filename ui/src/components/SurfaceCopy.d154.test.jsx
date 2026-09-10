// D-154 — the three copy defects the live-surface review found, pinned by what a READER SEES.
//
// ⚠⚠ WHY THIS FILE IS BEHAVIOURAL AND `tests/test_d154_live_surface_review.py` IS SOURCE-LEVEL.
// Every one of these shipped behind a green gate, and each got past a suite that was asserting the
// right words in the wrong shape: `CancerBurdenView.test.jsx` asserts `toMatch(/United States
// only/)`, which passes on one copy of the sentence or on five, and nothing rendered `DIO3`'s card
// at all. So these count occurrences and read whole strings rather than matching a fragment.
//
// ⚠ The burden fixture's `us_only` is the REAL served constant (`core/cancer_burden.py`
// `US_ONLY_DISCLAIMER`, copied verbatim), because the defect lives in the JOIN between that string
// and the component's own lead-in — a shortened fixture would hide it exactly as the D-152 fixture
// hid the missing aliases.
import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

vi.mock('../api.js', () => ({
  getCancerBurden: vi.fn(),
  getCensusDetail: vi.fn(),
  getPlddt: vi.fn(),
  listCensus: vi.fn(),
  getCensusSummary: vi.fn(),
  structureUrl: (id) => `/api/analyses/${id}/structure`,
}))
import { getCancerBurden, getCensusDetail, getPlddt } from '../api.js'
import CancerBurdenView, { leadSentence } from './CancerBurdenView.jsx'
import CensusProteinView from './CensusProteinView.jsx'
import CensusTable from './CensusTable.jsx'

// ⚠ VERBATIM from `core/cancer_burden.py`. If the served constant changes, this fixture must be
// re-copied — that is the point of pinning it here rather than paraphrasing it.
const US_ONLY = 'United States only. These are US figures: SEER reports US cancer statistics and '
  + 'nothing here describes cancer burden in any other country. Do not read a US rate as a world rate.'

const BURDEN = {
  result_status: 'valid',
  meta: { us_only: US_ONLY, us_only_short: 'US only — SEER/NCI', geography: 'united_states' },
  rows: [],
}

const countOf = (haystack, needle) => haystack.split(needle).length - 1

describe('D-154 · the burden page prints its geography sentence once', () => {
  it('does not prefix the served sentence with a second copy of itself', async () => {
    getCancerBurden.mockResolvedValue(BURDEN)
    render(<CancerBurdenView />)
    const banner = await screen.findByTestId('burden-us-only')
    // ⚠⚠ THE DEFECT, AS THE LIVE SITE RENDERED IT:
    //    "United States only. United States only. These are US figures…"
    expect(countOf(banner.textContent, 'United States only.')).toBe(1)
    // ⚠ and the served sentence is still there IN FULL — the fix removes a copy, never a claim
    expect(banner.textContent).toContain('Do not read a US rate as a world rate.')
  })

  it('keeps the geography emphasised, because D-149 put it in bold on purpose', async () => {
    getCancerBurden.mockResolvedValue(BURDEN)
    render(<CancerBurdenView />)
    const banner = await screen.findByTestId('burden-us-only')
    const strong = banner.querySelector('strong')
    expect(strong).not.toBeNull()
    expect(strong.textContent).toBe('United States only.')
  })

  it('still says something when the payload carries no qualifier at all', async () => {
    getCancerBurden.mockResolvedValue({ ...BURDEN, meta: {} })
    render(<CancerBurdenView />)
    const banner = await screen.findByTestId('burden-us-only')
    // ⚠ the fallback is the component's OWN words and has no sentence to duplicate
    expect(countOf(banner.textContent, 'United States only.')).toBe(1)
    expect(banner.textContent).toContain('These are US figures and describe no other country.')
  })

  it('leadSentence splits on the first sentence and never drops text', () => {
    const { head, rest } = leadSentence(US_ONLY)
    expect(head).toBe('United States only.')
    expect(`${head} ${rest}`).toBe(US_ONLY)
    // a string with no sentence break renders whole, inside the emphasis
    expect(leadSentence('One clause only')).toEqual({ head: 'One clause only', rest: '' })
    expect(leadSentence(undefined)).toEqual({ head: '', rest: '' })
  })
})

// ─────────────────────────────────────────────────────────────────────────────

const NEVER_FOLDED = {
  id: null,
  accession: 'P55073',
  gene: 'DIO3',
  label: 'Thyroxine 5-deiodinase',
  aliases: ['ITDI3', 'TXDI3'],
  span_aa: 237,
  folded: false,
  structure_kind: null,
  not_folded_reason: 'reason_unrecorded',
  not_folded_copy: 'not folded — and ⚠ nothing records why. It was assigned to the local tier and '
    + 'should have folded',
  scored: false,
  // ⚠ `null`, not `[]` — the live payload for a never-folded row carries no segments at all, and
  // `CensusDetail` reads this as a STRING of residue ranges. A `[]` here would be a fixture shape
  // the API never sends, which is the D-152 mistake this entry exists to correct.
  segments: null,
}

describe('D-154 · the never-folded card claims no length the record does not support', () => {
  it('tells DIO3 its span and nothing more — 237 aa is not a reason', async () => {
    getCensusDetail.mockResolvedValue(NEVER_FOLDED)
    getPlddt.mockRejectedValue(new Error('no structure'))
    render(<MemoryRouter><CensusProteinView id="P55073" /></MemoryRouter>)
    await waitFor(() => expect(screen.getByText(/Thyroxine 5-deiodinase/)).toBeTruthy())
    const text = document.body.textContent
    // ⚠⚠ THE CONTRADICTION THIS FIXES: the card said "should have folded" and then explained the
    // failure by a length the local tier folds comfortably (NECTIN4 at 318 aa; S-005 clean at 440).
    expect(text).not.toMatch(/long by the standards/)
    expect(text).not.toMatch(/longer than the local graphics card can fold/)
    expect(text).toMatch(/237 aa/)
    expect(text).toMatch(/should have folded/)
  })

  it('still says it plainly when the record DOES support it', async () => {
    getCensusDetail.mockResolvedValue({
      ...NEVER_FOLDED,
      accession: 'Q9NYQ8', gene: 'FAT2', label: 'Protocadherin Fat 2', span_aa: 4030,
      not_folded_reason: 'above_local_ceiling',
      not_folded_copy: 'not folded — its extracellular stretch is longer than the local graphics '
        + 'card can fold',
    })
    getPlddt.mockRejectedValue(new Error('no structure'))
    render(<MemoryRouter><CensusProteinView id="Q9NYQ8" /></MemoryRouter>)
    await waitFor(() => expect(screen.getByText(/Protocadherin Fat 2/)).toBeTruthy())
    expect(document.body.textContent).toMatch(/longer than the local graphics card can fold/)
  })

  it('makes no length claim for a mucin, which is unfolded by ruling and not by size', async () => {
    getCensusDetail.mockResolvedValue({
      ...NEVER_FOLDED,
      accession: 'Q8WXI7', gene: 'MUC16', label: 'Mucin-16', span_aa: 14451,
      structure_kind: 'mucin', not_folded_reason: 'mucin_out_of_class',
      not_folded_copy: 'mucin — out of class; never ESMFold (D-111)',
    })
    getPlddt.mockRejectedValue(new Error('no structure'))
    render(<MemoryRouter><CensusProteinView id="Q8WXI7" /></MemoryRouter>)
    await waitFor(() => expect(screen.getByText(/Mucin-16/)).toBeTruthy())
    const text = document.body.textContent
    expect(text).toMatch(/14451 aa/)
    expect(text).not.toMatch(/longer than the local graphics card can fold/)
    expect(text).toMatch(/out of class/)
  })
})

// ─────────────────────────────────────────────────────────────────────────────

const censusRow = (over) => ({
  id: 1, accession: 'A0AVI2', gene: 'FER1L5', label: 'Fer-1-like protein 5',
  span_aa: 75, topology: 'contiguous', tranche: 3, mean_plddt: 44.7,
  structure_kind: 'single-pass', structure_kind_label: 'single-pass', folded: true,
  cost: 'local', cost_label: 'local', profile_status: 'refused', scored: false,
  ...over,
})

describe('D-154 · the census Tranche cell names its absence', () => {
  it('never renders an empty cell for the one row with no tranche', () => {
    render(<MemoryRouter><CensusTable rows={[censusRow({ tranche: null })]} /></MemoryRouter>)
    const cells = [...document.querySelectorAll('tbody tr td')]
    const blank = cells.filter((c) => c.textContent.trim() === '')
    // ⚠⚠ A BLANK CELL IS THE ONE ABSENCE ON THIS TABLE A READER CANNOT TELL FROM A BROKEN RENDER.
    expect(blank).toHaveLength(0)
    expect(document.body.textContent).toMatch(/not batched/)
  })

  it('renders tranche 0 as 0 — `??` and never `||`, because 0 is the cohort', () => {
    render(<MemoryRouter><CensusTable rows={[censusRow({ tranche: 0 })]} /></MemoryRouter>)
    expect(document.body.textContent).not.toMatch(/not batched/)
    const nums = [...document.querySelectorAll('tbody td.num')].map((c) => c.textContent.trim())
    expect(nums).toContain('0')
  })
})
