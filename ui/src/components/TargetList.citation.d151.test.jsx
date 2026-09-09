// ⚠⚠ D-151 — THE PAPER THIS SURFACE IS BUILT ON BECOMES REACHABLE FROM IT.
//
// `/targets` has named "Kathad et al." in prose since F-009 and hyperlinked it never. The DOI has
// been in this repository the whole time — `data/cohort_82.txt`, `data/cancer_associations.csv`,
// `core/cancer_associations.py`'s `SOURCE` — and in no rendered surface, so a reader could see
// which paper the 82 came from and had no way to open it. **A citation nobody can follow is an
// assertion, not a source.**
//
// ⚠ These assertions are written against the STRUCTURE of the link, not against the sentence
// around it: the href, the target, and the `rel` that must accompany `target="_blank"`. Copy is
// the owner's to edit; a link that opens a tab with `window.opener` still attached is not.
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

vi.mock('../api.js', () => ({
  listAnalyses: vi.fn(),
  getCoverage: vi.fn(),
  getRanking: vi.fn(),
  getAssociations: vi.fn(),
}))
import { getAssociations, getCoverage, getRanking, listAnalyses } from '../api.js'
import TargetList from './TargetList.jsx'
import { COHORT_PAPER_DOI, COHORT_PAPER_URL } from '../cohortPaper.js'

const ROWS = [
  { id: 1, gene: 'NECTIN4', accession: 'Q92729', mean_plddt: 77.26, tier: 'local', tier_reason: null },
]

beforeEach(() => {
  listAnalyses.mockReset(); getCoverage.mockReset(); getRanking.mockReset(); getAssociations.mockReset()
  listAnalyses.mockResolvedValue(ROWS)
  getCoverage.mockResolvedValue({ rows: [] })
  getRanking.mockResolvedValue({ rows: [] })
  getAssociations.mockResolvedValue({ associations: {}, attributions: {} })
})

const draw = () => render(<MemoryRouter><TargetList /></MemoryRouter>)

describe('D-151 — the Kathad citation is a link, and it points at the DOI', () => {
  it('renders an anchor named for the paper on the Initial Targets surface', async () => {
    draw()
    const link = await screen.findByRole('link', { name: /Kathad et al\.? 2024/i })
    expect(link).toHaveAttribute('href', COHORT_PAPER_URL)
  })

  it('the href is the DOI resolver over the repository\u2019s own DOI, not a publisher landing page', async () => {
    draw()
    const link = await screen.findByRole('link', { name: /Kathad et al\.? 2024/i })
    const href = link.getAttribute('href')
    expect(href).toBe('https://doi.org/10.1371/journal.pone.0308604')
    expect(href).toContain(COHORT_PAPER_DOI)
  })

  // ⚠⚠ `target="_blank"` WITHOUT `rel` HANDS THE NEW TAB A HANDLE ON THIS ONE. Every external
  // anchor already in this tree carries both (the HPA deep links, the atlas credit); this is the
  // same rule applied to the citation, asserted rather than remembered.
  it('opens in a new tab and severs the opener', async () => {
    draw()
    const link = await screen.findByRole('link', { name: /Kathad et al\.? 2024/i })
    expect(link).toHaveAttribute('target', '_blank')
    const rel = link.getAttribute('rel') ?? ''
    expect(rel).toContain('noopener')
    expect(rel).toContain('noreferrer')
  })

  // ⚠ ONE citation link near the top, not an anchor on every occurrence of the word. Three links
  // to one DOI in one paragraph read as decoration and teach a reader to skip all of them.
  it('links the paper once, not on every mention', async () => {
    const { container } = draw()
    await screen.findByRole('link', { name: /Kathad et al\.? 2024/i })
    const doiLinks = [...container.querySelectorAll('a')]
      .filter((a) => (a.getAttribute('href') ?? '').includes(COHORT_PAPER_DOI))
    expect(doiLinks).toHaveLength(1)
  })

  // ⚠⚠ NEAR THE TOP, AND MEASURED STRUCTURALLY BECAUSE jsdom HAS NO LAYOUT. The claim a test can
  // actually make is DOM ORDER: the citation precedes the table it explains the population of.
  it('sits above the table, where a reader meets it before the rows', async () => {
    const { container } = draw()
    const link = await screen.findByRole('link', { name: /Kathad et al\.? 2024/i })
    const table = container.querySelector('table')
    expect(table).toBeTruthy()
    expect(link.compareDocumentPosition(table) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
  })

  // ⚠⚠ THE CITATION IS NOT THE HPA CREDIT AND MUST NOT COME TO STAND IN FOR IT (D-100 / D-094).
  // Kathad's S3 is a verbatim extract of HPA's `pathology.tsv`, so the paper link discharges the
  // paper's attribution and none of the atlas licence's four elements. This fixture renders no
  // tumour type, so no HPA credit should appear — and the paper link must not have summoned one.
  it('does not present itself as the Human Protein Atlas citation', async () => {
    const { container } = draw()
    await screen.findByRole('link', { name: /Kathad et al\.? 2024/i })
    expect(container.querySelector('[data-hpa-attribution]')).toBeNull()
  })
})
