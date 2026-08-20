import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'

// ⚠⚠ TWO DEFECTS ON ONE SURFACE, both found by walking `/targets` on 2026-08-20.
//
// 1. **The header said "80 folded targets" above 80 rows of which 79 are folded.** `IGF2R` renders
//    its own *"fold failed — CUDA OOM folding 2491 aa"* ONE LINE BENEATH a header counting it as
//    folded. And 80 is not the cohort either: the cohort is **82**, because `FAT2` and `MUC16` have
//    no analysis row at all and were absent from the surface entirely — no row, no count, no cause.
//
// 2. **There was no search box.** `ERBB2` is folded and ranked here, and the owner searching for
//    `HER2` — the name on the drug label — found nothing, because there was nothing to type into.
//    ⚠ The alias index (`D-101`) existed and reached the census only: `F-052`'s exact shape.

vi.mock('../api.js', () => ({
  getCensusSummary: vi.fn(),
  listAnalyses: vi.fn(),
  getCoverage: vi.fn(),
  getRanking: vi.fn(),
}))
import { listAnalyses, getCoverage } from '../api.js'
import TargetList from './TargetList.jsx'

// 79 folded + IGF2R (attempted, failed) = the 80 rows the API actually returns
const ANALYSES = [
  { id: 1, gene: 'NECTIN4', accession: 'Q96NY8', label: 'Nectin-4', mean_plddt: 88.1, tier: 'local', aliases: ['PVRL4'] },
  { id: 52, gene: 'ERBB2', accession: 'P04626', label: 'Receptor tyrosine-protein kinase erbB-2', mean_plddt: 73.94, tier: 'rental', aliases: ['HER2', 'NEU', 'CD340'] },
  { id: 57, gene: 'IGF2R', accession: 'P11717', label: 'Cation-independent M6P receptor', mean_plddt: null, tier: 'rental', aliases: ['CD222'] },
]
// the manifest: the same three, plus the two that were never attempted
const COVERAGE = {
  rows: [
    { accession: 'Q96NY8', gene: 'NECTIN4', fold_status: 'folded' },
    { accession: 'P04626', gene: 'ERBB2', fold_status: 'folded' },
    { accession: 'P11717', gene: 'IGF2R', fold_status: 'failed', fail_reason: 'CUDA OOM folding 2491 aa at chunk_size=32' },
    { accession: 'Q9NYQ8', gene: 'FAT2', fold_status: 'not_folded', exclusion_reason: 'oversize: FAT2, 4030 aa — folds on no single card as one seq' },
    { accession: 'Q8WXI7', gene: 'MUC16', fold_status: 'not_folded', exclusion_reason: 'oversize: MUC16 (CA-125), 14451 aa — folds on no single card' },
  ],
}

const draw = () => render(<MemoryRouter><TargetList /></MemoryRouter>)

beforeEach(() => {
  listAnalyses.mockResolvedValue(ANALYSES)
  getCoverage.mockResolvedValue(COVERAGE)
})

describe('the count states its key', () => {
  it('never calls the whole list folded', async () => {
    const { container } = draw()
    await waitFor(() => expect(container.textContent).toMatch(/cohort targets/))
    const lede = container.querySelector('.lede').textContent
    // ⚠⚠ the exact false sentence, asserted absent
    expect(lede).not.toMatch(/5 folded targets/)
    expect(lede).toMatch(/The 5 cohort targets/)
    expect(lede).toMatch(/2 folded/)
  })

  it('separates attempted-and-failed from never-attempted', async () => {
    const { container } = draw()
    await waitFor(() => expect(container.textContent).toMatch(/cohort targets/))
    const lede = container.querySelector('.lede').textContent
    // ⚠ D-024: three states, three counts. A single "3 not folded" would merge a CUDA OOM with a
    // protein nobody ever put on a card.
    expect(lede).toMatch(/1 attempted and failed/)
    expect(lede).toMatch(/2 too large to attempt/)
  })

  it('shows the cohort members that have no analysis row', async () => {
    const { container } = draw()
    await waitFor(() => expect(container.textContent).toMatch(/FAT2/))
    expect(container.textContent).toMatch(/MUC16/)
    // ⚠ and with the CAUSE, not a bare dash — the reason lives in `exclusion_reason`
    expect(container.textContent).toMatch(/not folded — oversize/)
  })

  it('does not link a row that has no analysis to open', async () => {
    // ⚠⚠ `/target/null` would be a link that 404s: worse than no link, because it invites the click
    const { container } = draw()
    await waitFor(() => expect(container.textContent).toMatch(/FAT2/))
    const hrefs = [...container.querySelectorAll('a')].map((a) => a.getAttribute('href'))
    expect(hrefs.some((h) => h && h.includes('null'))).toBe(false)
    expect(hrefs).toContain('/target/52')
  })

  it('states the shown count whenever the table is narrowed', async () => {
    // ⚠ a filtered table under an unqualified total is the defect the header already had
    const { container } = draw()
    await waitFor(() => expect(container.textContent).toMatch(/cohort targets/))
    expect(container.querySelector('.filter-count')).toBeNull()
    fireEvent.change(screen.getByLabelText('Search'), { target: { value: 'HER2' } })
    expect(container.querySelector('.filter-count').textContent).toMatch(/Showing 1 of 5/)
  })
})

describe('the search box, and the name on the drug label', () => {
  it('finds ERBB2 by searching HER2', async () => {
    const { container } = draw()
    await waitFor(() => expect(container.textContent).toMatch(/ERBB2/))
    fireEvent.change(screen.getByLabelText('Search'), { target: { value: 'HER2' } })
    const body = container.querySelector('tbody').textContent
    expect(body).toMatch(/ERBB2/)
    expect(body).not.toMatch(/NECTIN4/)
  })

  it('matches punctuation-insensitively, so HER-2 and her 2 both land', async () => {
    const { container } = draw()
    await waitFor(() => expect(container.textContent).toMatch(/ERBB2/))
    for (const q of ['HER-2', 'her 2', 'CD340']) {
      fireEvent.change(screen.getByLabelText('Search'), { target: { value: q } })
      expect(container.querySelector('tbody').textContent).toMatch(/ERBB2/)
    }
  })

  it('still finds a row by gene and by accession', async () => {
    const { container } = draw()
    await waitFor(() => expect(container.textContent).toMatch(/ERBB2/))
    fireEvent.change(screen.getByLabelText('Search'), { target: { value: 'Q96NY8' } })
    expect(container.querySelector('tbody').textContent).toMatch(/NECTIN4/)
  })

  it('says so when nothing matches, rather than showing an empty table', async () => {
    const { container } = draw()
    await waitFor(() => expect(container.textContent).toMatch(/ERBB2/))
    fireEvent.change(screen.getByLabelText('Search'), { target: { value: 'ZZZZ' } })
    expect(container.querySelector('tbody').children.length).toBe(0)
    expect(container.querySelector('.filter-count').textContent).toMatch(/nothing here matches/)
  })

  // ⚠⚠ THE POPULATION BOUNDARY. `D-081`: the cohort and the census are measured under different
  // span definitions. A search box is a way to find what is HERE — it must not reach the census.
  it('does not find a census-only protein', async () => {
    const { container } = draw()
    await waitFor(() => expect(container.textContent).toMatch(/ERBB2/))
    fireEvent.change(screen.getByLabelText('Search'), { target: { value: 'CHST11' } })
    expect(container.querySelector('tbody').children.length).toBe(0)
  })
})

// ⚠ The surface must survive coverage being unreachable — F-054 is the entry for a guard that
// deletes rows when an optional enrichment fails.
describe('degradation', () => {
  it('renders the analyses when coverage cannot be reached', async () => {
    getCoverage.mockRejectedValue(new Error('nope'))
    const { container } = draw()
    await waitFor(() => expect(container.textContent).toMatch(/ERBB2/))
    // ⚠ the 3 analysis rows survive; only the 2 manifest-only rows and the reasons are lost
    expect(container.querySelector('tbody').children.length).toBe(3)
    expect(container.querySelector('.lede').textContent).toMatch(/The 3 cohort targets/)
  })
})
