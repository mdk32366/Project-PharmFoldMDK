// Confidence demotion — the list must not let a green dot read as "good target".
//
// The band vocabulary in `plddt.js` is already careful ("Confident BACKBONE", "backbone unreliable",
// "not reliably interpretable") and `Confidence.jsx` already carries its disclaimer. The trap was
// never the vocabulary — it was the LIST: a bare column header reading "Confidence" beside a
// traffic-light dot, rendered as prominently as the identity columns. A neophyte reads that as a
// verdict on the target, not a check on the fold.
//
// ⚠ DEMOTION IS NOT DELETION. Every confidence value, band and colour stays present and honest. What
// changes is the header's wording, the dot's visual rank, and the addition of one sentence saying
// what confidence is NOT. No confidence information is removed anywhere.
//
// ⚠ WHAT THIS FILE DELIBERATELY DOES NOT ASSERT: any specific pixel treatment. The order reserves the
// exact visual choice for the owner (§1b), because prominence was itself an owner ruling (D-039/D-048).
// So the tests below pin the PROPERTIES the honesty depends on — the header is qualified, the
// what-it-isn't line is present, identity precedes confidence, no suitability language appears — and
// leave the styling free to be re-ruled without reddening the suite.
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, within, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

// getCoverage is mocked too: TargetList now joins /api/coverage client-side for the
// absent-value reason (no route change). It is additive - the list renders without it.
vi.mock('../api.js', () => ({ listAnalyses: vi.fn(), getCoverage: vi.fn(), getRanking: vi.fn() }))
import { getCoverage, getRanking, listAnalyses } from '../api.js'
import TargetList from './TargetList.jsx'
import { BANDS, COHORT_MAX_PLDDT, bandFor } from '../plddt.js'

const ROWS = [
  { id: 1, gene: 'NECTIN4', accession: 'Q92729', mean_plddt: 77.26, tier: 'local', tier_reason: null },
  { id: 2, gene: 'SDK1', accession: 'Q7Z5N4', mean_plddt: 58.01, tier: 'rental', tier_reason: 'length 2213 > local ceiling' },
  // IGF2R-shaped: a REAL row on the deployed list (fold failed, null pLDDT). Present here so the
  // demotion work is exercised against the row that actually exists, not only the happy path.
  { id: 3, gene: 'IGF2R', accession: 'P11717', mean_plddt: null, tier: 'rental', tier_reason: 'fold failed' },
]

const renderList = () => render(<MemoryRouter><TargetList /></MemoryRouter>)

beforeEach(() => {
  listAnalyses.mockReset()
  getCoverage.mockReset()
  listAnalyses.mockResolvedValue(ROWS)
  getCoverage.mockResolvedValue({ rows: [] })
  // ⚠ no ranking in these fixtures: these suites test sorting/confidence, not the rank axis.
  getRanking.mockResolvedValue({ rows: [] })
})

describe('confidence demotion — the column header says what the band labels already say', () => {
  it('qualifies the confidence header as being about the FOLD/STRUCTURE, never a bare "Confidence"', async () => {
    renderList()
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    const headers = screen.getAllByRole('columnheader').map((h) => h.textContent.trim())
    const confidenceHeader = headers.find((h) => /confidence/i.test(h))
    expect(confidenceHeader, `no confidence column header found in ${JSON.stringify(headers)}`).toBeTruthy()
    // The whole fix: the header itself must carry the fold/structure qualifier, so the glance reads
    // "how good is the model's structure", not "how good is this target".
    expect(
      confidenceHeader,
      `header ${JSON.stringify(confidenceHeader)} is an unqualified verdict - it must name fold or structure`,
    ).toMatch(/fold|structure/i)
    // And it must not be the bare word alone.
    expect(confidenceHeader.toLowerCase()).not.toBe('confidence')
  })

  it('states once on the list what confidence is NOT, so the glance is inoculated before any detail panel', async () => {
    const { container } = renderList()
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    const text = container.textContent
    // The substance, not exact wording (copy is owner-reserved): confidence is about the structure,
    // and it is explicitly NOT a judgement about the target being a good ADC candidate.
    expect(text).toMatch(/not\b[^.]*\b(good|suitab|candidate|verdict|quality)/i)
    expect(text).toMatch(/structure|fold/i)
  })

  it('places the identity columns BEFORE confidence, so confidence is not the top-of-hierarchy signal', async () => {
    renderList()
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    const headers = screen.getAllByRole('columnheader').map((h) => h.textContent.trim())
    const geneAt = headers.findIndex((h) => /gene/i.test(h))
    const confAt = headers.findIndex((h) => /confidence/i.test(h))
    expect(geneAt).toBeGreaterThanOrEqual(0)
    expect(confAt).toBeGreaterThan(geneAt)
  })
})

describe('confidence demotion — the slot is RESERVED, not filled (D-075-gated)', () => {
  it('introduces no suitability / good-target / recommendation claim anywhere on the list', async () => {
    const { container } = renderList()
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    const text = container.textContent
    // Demotion removes an impersonation; it must not add the real thing. The structural-suitability
    // score is gated on the D-075 run and is NOT built here.
    for (const banned of [
      /\bsuitability score\b/i,
      /\bgood target\b/i,
      /\brecommended\b/i,
      /\bbest candidate\b/i,
      /\bclinical opportunity\b/i,
      /\bstructural suitability\b/i,
      /\bpromising\b/i,
    ]) {
      expect(text, `list must not claim ${banned}`).not.toMatch(banned)
    }
  })
})

describe('confidence demotion — what must NOT change', () => {
  it('leaves the D-039 band scale untouched: boundaries, labels and the cohort-max caveat', () => {
    // The scale is load-bearing in PlddtPlot, PlddtSpread, Confidence and StructureViewer colouring.
    // This order reframes the header and prominence on the LIST; it never touches the scheme.
    expect(BANDS.map((b) => b.min)).toEqual([70, 60, 50, 0])
    expect(BANDS[0].label).toBe('Confident backbone')
    expect(BANDS[2].label).toMatch(/backbone unreliable/i)
    expect(BANDS[3].label).toMatch(/not reliably interpretable/i)
    expect(BANDS[0].caveat).toContain(String(COHORT_MAX_PLDDT))
  })

  it('keeps the "backbone" qualifier in the rendered band label — that word IS the honesty', async () => {
    const { container } = renderList()
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    // NECTIN4 at 77.26 lands in the top band; its label must still say "backbone", not be
    // genericised to "Confident" (which would make it read as a verdict on the target).
    expect(container.textContent).toMatch(/confident backbone/i)
  })

  it('still renders every confidence value and band — demotion is not deletion', async () => {
    renderList()
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    expect(screen.getByText('77.26')).toBeInTheDocument()
    expect(screen.getByText('58.01')).toBeInTheDocument()
    // The band for each measured row is still shown.
    expect(screen.getAllByText(new RegExp(bandFor(58.01).label, 'i')).length).toBeGreaterThan(0)
  })

  it('renders the absent-pLDDT row as an em-dash and a stated reason, never as a low number', async () => {
    // IGF2R is real and live. This asserts the row is displayed honestly as ABSENT rather than as a
    // value, and that the absence carries a reason rather than being left blank.
    //
    // NOTE the exact reason wording is deliberately NOT pinned here. This test originally asserted
    // the band label "not folded"; the sortable-list order supersedes that with the row's REAL cause
    // (from /api/coverage's fold_status + fail_reason), because a generic label over a specific
    // failure is the kind of smoothing this project refuses. The INTENT — em-dash, a reason present,
    // never a coerced number — is what is pinned, so an improvement to the wording cannot redden it.
    renderList()
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    const row = screen.getByText('IGF2R').closest('tr')
    expect(within(row).getByText('—')).toBeInTheDocument()
    expect(row.textContent).toMatch(/not folded|fold failed|no measurement/i)
    expect(row.textContent).not.toMatch(/\b0\.00\b/)
  })
})
