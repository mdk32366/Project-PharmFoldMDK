// D-135 — `/coverage` carries TWO populations, and neither number is allowed to stand for the other.
//
// ⚠⚠ THE DEFECT THESE PIN, AND THE ONE THE FIX COULD HAVE INTRODUCED. The page described the cohort
// and said nothing about the census, so a reader who arrived at "the honest denominator" learned the
// shape of 82 proteins and left believing that was the whole of the work. But the obvious remedy —
// a bigger number in the headline — is the exact failure D-024 exists to forbid: a denominator that
// grows with how much work has happened. So the assertions come in pairs. One half says the census
// population is on the page; the other says it never touched the headline.
//
// ⚠ THE FIXTURE NUMBERS ARE CHOSEN SO THE TWO CANNOT BE CONFUSED. The cohort denominator is 9 with
// 4 ranked-and-folded; the census carries 3,468 / 2,691 / 46 assembled. Nothing in the cohort's
// range can coincide with the census's, so an assertion about which number the headline shows cannot
// pass by accident — and a literal pasted into the JSX could satisfy neither.
import { render as rtlRender, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi, beforeEach } from 'vitest'

vi.mock('../api.js', () => ({ getCoverage: vi.fn(), getCensusSummary: vi.fn() }))
import { getCoverage, getCensusSummary } from '../api.js'
import CoverageView from './CoverageView.jsx'

const render = (ui) => rtlRender(<MemoryRouter>{ui}</MemoryRouter>)

const COVERAGE = {
  coverage: {
    denominator: 9, ranked: 6, held_out: 2, excluded: 1, unmeasured_tier: 1, no_topology: 1,
  },
  rows: [
    { accession: 'Q00001', gene: 'AAA', disposition: 'ranked', fold_status: 'folded',
      analysis_id: 11, tier: 'local' },
    { accession: 'Q00002', gene: 'BBB', disposition: 'ranked', fold_status: 'folded',
      analysis_id: 12, tier: 'local' },
    { accession: 'Q00003', gene: 'CCC', disposition: 'ranked', fold_status: 'folded',
      analysis_id: 13, tier: 'local' },
    { accession: 'Q00004', gene: 'DDD', disposition: 'ranked', fold_status: 'folded',
      analysis_id: 14, tier: 'local' },
    // ⚠ the case the bridge exists for: attempted here, failed here, and a census assembly of the
    // same accession exists. IGF2R's own shape, with a fixture accession so the assertion is about
    // the RULE and not about one hard-coded protein.
    { accession: 'Q00005', gene: 'EEE', disposition: 'ranked', fold_status: 'failed',
      tier: 'rental', tier_reason: 'whole_sequence_fold', fail_reason: 'CUDA out of memory.',
      census_sibling: {
        structure_kind: 'assembled', structure_kind_label: 'assembled (provisional)', folded: true,
        assembler_note: 'assembled by pLDDT overlap, not superimposed; seam not solved',
      } },
    // ⚠ never attempted here, and its census representative is TILES — a window, not the protein
    // (D-118). No bridge may render for it.
    { accession: 'Q00006', gene: 'FFF', disposition: 'held_out', fold_status: 'not_folded',
      tier: 'rental', census_sibling: {
        structure_kind: 'tiles_only', structure_kind_label: 'tiles only', folded: false,
        assembler_note: null,
      } },
    { accession: 'Q00007', gene: 'GGG', disposition: 'held_out', fold_status: 'folded',
      analysis_id: 17, tier: 'local' },
    { accession: 'Q00008', gene: 'HHH', disposition: 'excluded', fold_status: 'not_folded',
      excluded: true, exclusion_reason: 'oversize', tier: 'none' },
  ],
}

const CENSUS = {
  manifest_rows: 3468,
  folded: 2691,
  max_mean_plddt: 89.25,
  structure_kinds: [
    { kind: 'assembled', label: 'assembled (provisional)', n: 46 },
    { kind: 'single-pass', label: 'single-pass', n: 2645 },
    { kind: 'tiles_only', label: 'tiles only', n: 17 },
    { kind: 'mucin', label: 'mucin — not folded', n: 3 },
  ],
}

const mounted = async () => {
  const out = render(<CoverageView />)
  await waitFor(() => expect(out.container.textContent).toMatch(/ranked & folded/))
  return out
}

beforeEach(() => {
  vi.clearAllMocks()
  getCoverage.mockResolvedValue(COVERAGE)
  getCensusSummary.mockResolvedValue(CENSUS)
})

describe('D-135 — the headline is still the cohort intersection, with the census on screen', () => {
  // ⚠⚠ THE LOAD-BEARING ASSERTION OF THE WHOLE PR. Prove it bites by passing the census summary
  // into `CoverageLine`, or by summing the two populations anywhere near this sentence.
  it('leads with ranked-and-folded of the COHORT denominator, never a census count', async () => {
    const { container } = await mounted()
    const headline = container.querySelector('.coverage-headline')
    expect(headline.textContent).toMatch(/4 ranked & folded of 9/)
    // ⚠ none of the census figures may appear in the headline, in any formatting
    for (const n of ['3,468', '3468', '2,691', '2691', '46']) {
      expect(headline.textContent).not.toContain(n)
    }
  })

  it('keeps the D-024 partition and its overstatement warning intact', async () => {
    const { container } = await mounted()
    const line = container.querySelector('.coverage-line')
    expect(line.textContent).toMatch(/overstate the cohort/)
    expect(line.textContent).toMatch(/honest denominator/)
    // ⚠ the partition still sums to the cohort denominator and knows nothing of the census
    expect(line.textContent).toMatch(/6 ranked/)
    expect(line.textContent).toMatch(/2 held out/)
    expect(line.textContent).toMatch(/1 excluded/)
    expect(line.textContent).not.toContain('2,691')
  })

  // ⚠ The census strip is a SIBLING of the coverage line, never inside it. A census count rendered
  // within `.coverage-line` would be one CSS change from reading as part of the headline.
  it('renders the census strip outside the coverage line, below it', async () => {
    const { container } = await mounted()
    expect(container.querySelector('.coverage-line .census-population')).toBeNull()
    const line = container.querySelector('.coverage-line')
    const strip = container.querySelector('.census-population')
    expect(strip).toBeTruthy()
    expect(line.compareDocumentPosition(strip) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
  })
})

describe('D-135 — the second strip says it is a different population before it says a number', () => {
  it('names it a different population and refuses the denominator', async () => {
    const { container } = await mounted()
    const strip = container.querySelector('.census-population')
    expect(strip.textContent).toMatch(/different population/i)
    expect(strip.textContent).toMatch(/not more of the cohort/i)
    expect(strip.textContent).toMatch(/do not extend the denominator/i)
    expect(strip.textContent).toMatch(/different span definition/i)
    expect(strip.textContent).toMatch(/not scored and not ranked/i)
  })

  // ⚠ The label must come BEFORE the figures — a reader who stops after the first number has to
  // have met the population already. Same rule as `/census`'s "not scored" bar sitting above its
  // counts.
  it('puts the population statement above the counts, not below them', async () => {
    const { container } = await mounted()
    const t = container.querySelector('.census-population').textContent
    expect(t.indexOf('different population')).toBeGreaterThan(-1)
    expect(t.indexOf('different population')).toBeLessThan(t.indexOf('3,468'))
  })

  it('states both population sizes with their own keys', async () => {
    const { container } = await mounted()
    const figures = container.querySelector('.census-population-figures').textContent
    expect(figures).toMatch(/3,468/)
    expect(figures).toMatch(/proteins in the census, folded or not/)
    expect(figures).toMatch(/2,691/)
    expect(figures).toMatch(/structure and a measured confidence/)
  })

  // ⚠⚠ CONSTRAINT A, AS AN ASSERTION. Every count and every label comes off the payload — so
  // changing the payload must change the render. Prove it bites by typing any of them into the JSX.
  it('takes every kind, label and count from the payload', async () => {
    const { container } = await mounted()
    const kinds = container.querySelector('.census-population-kinds').textContent
    expect(kinds).toMatch(/assembled \(provisional\) 46/)
    expect(kinds).toMatch(/single-pass 2,645/)
    expect(kinds).toMatch(/tiles only 17/)
    expect(kinds).toMatch(/mucin — not folded 3/)
  })

  it('moves when the payload moves, and renders a kind the component never heard of', async () => {
    getCensusSummary.mockResolvedValue({
      ...CENSUS,
      manifest_rows: 4001,
      folded: 3002,
      structure_kinds: [{ kind: 'brand-new-kind', label: 'a kind invented later', n: 7 }],
    })
    const { container } = await mounted()
    const strip = container.querySelector('.census-population').textContent
    expect(strip).toMatch(/4,001/)
    expect(strip).toMatch(/3,002/)
    expect(strip).toMatch(/a kind invented later 7/)
    // ⚠ and the old fixture's numbers are gone, so nothing was cached or typed
    expect(strip).not.toMatch(/3,468/)
    expect(strip).not.toMatch(/assembled \(provisional\)/)
  })

  // ⚠ A kind the census does not hold has no entry in the payload and must not be drawn as a zero.
  // `assembled 0` is exactly what the census truthfully showed for all 45 assembled parents before
  // D-134 repaired the identity check — a rendering nobody could tell from a finding.
  it('draws no chip and no caveat for a kind the payload does not carry', async () => {
    getCensusSummary.mockResolvedValue({
      ...CENSUS, structure_kinds: [{ kind: 'single-pass', label: 'single-pass', n: 12 }],
    })
    const { container } = await mounted()
    const strip = container.querySelector('.census-population').textContent
    expect(strip).not.toMatch(/assembled/)
    expect(strip).not.toMatch(/\b0\b/)
  })

  it('deep-links each chip at the filtered census list', async () => {
    const { container } = await mounted()
    const hrefs = [...container.querySelectorAll('.census-population-kinds a')]
      .map((a) => a.getAttribute('href'))
    expect(hrefs).toContain('/census?structure=assembled')
    expect(hrefs).toContain('/census?structure=tiles_only')
  })

  // ⚠⚠ THE CAVEAT ARRIVES WITH THE LINK (D-133 am. 1's rule, one surface along). Pointing a reader
  // at the assembled proteins from the honesty page without saying what an assembly is would spend
  // this page's credibility overstating them.
  it('says assembled is provisional wherever it links to the assemblies', async () => {
    const { container } = await mounted()
    const caveat = container.querySelector('.census-population .caveat').textContent
    expect(caveat).toMatch(/provisional/i)
    expect(caveat).toMatch(/not\s+superimposed/i)
    expect(caveat).toMatch(/recorded, not solved/i)
    expect(caveat).toMatch(/not in the\s+ranking/i)
  })

  // ⚠ ADDITIVE. `/coverage` exists to serve the honest denominator; the census is a bonus on it.
  it('renders the whole coverage page when the census summary is unavailable', async () => {
    getCensusSummary.mockRejectedValue(new Error('down'))
    const { container } = await mounted()
    expect(container.querySelector('.coverage-headline').textContent)
      .toMatch(/4 ranked & folded of 9/)
    expect(container.querySelector('.census-population')).toBeNull()
    expect(screen.getAllByRole('row').length).toBe(COVERAGE.rows.length + 1)
  })

  it('survives a census supplier that is not a promise at all', async () => {
    getCensusSummary.mockReturnValue(undefined)
    const { container } = await mounted()
    expect(container.querySelector('.coverage-headline')).toBeTruthy()
  })
})

describe('D-135 — the failed cohort row gets a bridge, and stays failed', () => {
  const bridgeRow = async () => {
    const { container } = await mounted()
    const row = [...container.querySelectorAll('tbody tr')]
      .find((tr) => tr.textContent.includes('Q00005'))
    return row
  }

  // ⚠⚠ THE WHOLE POINT: a census assembly of the same accession exists, and the cohort attempt
  // still FAILED. Prove it bites by letting the bridge change the fold cell.
  it('keeps the fold cell reading failed, with its reason', async () => {
    const row = await bridgeRow()
    expect(within(row).getByText('failed')).toBeInTheDocument()
    expect(row.textContent).toMatch(/CUDA out of memory/)
    expect(row.textContent).not.toMatch(/folded elsewhere/i)
  })

  it('links to the census representative BY ACCESSION', async () => {
    const row = await bridgeRow()
    const link = within(row).getByRole('link', { name: /census: assembled \(provisional\)/ })
    expect(link).toHaveAttribute('href', '/census/Q00005')
    expect(link).toHaveAttribute(
      'title', 'assembled by pLDDT overlap, not superimposed; seam not solved')
  })

  it('says the bridge is a different population and not this cohort fold', async () => {
    const row = await bridgeRow()
    expect(row.textContent).toMatch(/different population/i)
    expect(row.textContent).toMatch(/different span definition/i)
    expect(row.textContent).toMatch(/not this cohort fold/i)
  })

  // ⚠⚠ THE NAMED STOP CONDITION, ASSERTED (see tests/test_no_census_leak_on_tranche_zero.py).
  // 75 of the 82 cohort accessions are also census rows. The Gene cell's `/target/:id` link is the
  // COHORT's, and a census id reaching it would open a fold measured under the other span
  // definition with nothing on screen saying so.
  it('never puts a census target under the cohort Target link', async () => {
    const { container } = await mounted()
    const geneLinks = [...container.querySelectorAll('tbody tr td:first-child a')]
      .map((a) => a.getAttribute('href'))
    expect(geneLinks.length).toBeGreaterThan(0)
    for (const href of geneLinks) {
      expect(href).toMatch(/^\/target\/\d+$/)
      expect(href).not.toMatch(/census/)
    }
    // ⚠ and the failed row has NO gene link at all — it has no cohort fold to open
    const failed = [...container.querySelectorAll('tbody tr')]
      .find((tr) => tr.textContent.includes('Q00005'))
    expect(failed.querySelector('td:first-child a')).toBeNull()
  })

  // ⚠ A tile window is not the protein (D-118). `folded: false` on the sibling, so no bridge.
  it('draws no bridge for a tiles-only sibling', async () => {
    const { container } = await mounted()
    const row = [...container.querySelectorAll('tbody tr')]
      .find((tr) => tr.textContent.includes('Q00006'))
    expect(row.querySelector('.chip-census-sibling')).toBeNull()
    expect(row.textContent).not.toMatch(/tiles only/)
  })

  // ⚠ Where the cohort has its own fold, the census is not the interesting fact — a note on
  // sixty-odd rows is noise, and this page is already dense.
  it('draws no bridge on a row that folded here', async () => {
    const { container } = await mounted()
    const rows = [...container.querySelectorAll('tbody tr')]
      .filter((tr) => within(tr).queryByText('folded'))
    expect(rows.length).toBeGreaterThan(0)
    for (const tr of rows) expect(tr.querySelector('.chip-census-sibling')).toBeNull()
  })

  // ⚠ The bridge REPLACES the paragraph rather than joining it. 209 characters of two-population
  // prose in a `<td>` is the thing being fixed.
  it('drops the long prose once the bridge can point at a page', async () => {
    const row = await bridgeRow()
    expect(row.textContent).not.toMatch(/Neither substitutes for the other/)
  })

  // ⚠ …and keeps it when there is no assembled sibling to point at. An absent bridge must not
  // silently delete the honesty it replaced.
  it('keeps the prose when no census sibling exists for that accession', async () => {
    getCoverage.mockResolvedValue({
      ...COVERAGE,
      rows: [{ accession: 'P11717', gene: 'IGF2R', disposition: 'ranked', fold_status: 'failed',
        tier: 'rental', fail_reason: 'CUDA out of memory.' }],
    })
    const { container } = await mounted()
    expect(container.textContent).toMatch(/Neither substitutes for the other/)
    expect(container.querySelector('.chip-census-sibling')).toBeNull()
  })
})
