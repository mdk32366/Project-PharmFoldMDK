// D-051 Constraint A: the Story's numbers derive from the payload, never literals. Distinctive
// fixture values (4 folded, max 88.00, 3-of-5) that cannot coincide with today's live cohort, so a
// green means the render tracked the payload — and the negative test reddens if a real number is
// ever pasted into the prose.
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../api.js', () => ({
  getCensusSummary: vi.fn(), listAnalyses: vi.fn(), getCoverage: vi.fn() }))
import { listAnalyses, getCoverage, getCensusSummary } from '../api.js'
import Story from './Story.jsx'

const ANALYSES = [
  { mean_plddt: 40.0 }, { mean_plddt: 55.0 }, { mean_plddt: 70.0 }, { mean_plddt: 88.0 },
  { mean_plddt: null }, // unfolded — excluded from the folded count
]
const COVERAGE = {
  coverage: { denominator: 5 },
  rows: [
    { disposition: 'ranked', fold_status: 'folded', gene: 'AAA' },
    { disposition: 'ranked', fold_status: 'folded', gene: 'BBB' },
    { disposition: 'ranked', fold_status: 'folded', gene: 'CCC' },
    { disposition: 'held_out', fold_status: 'failed', gene: 'FAKEIGF' },
    { disposition: 'excluded', fold_status: 'not_folded', gene: 'FAKEBIG' },
  ],
}
const LIVE_LITERALS = ['79', '82', '84.23', '30.68', '29%']
const renderStory = () => render(<MemoryRouter><Story /></MemoryRouter>)
beforeEach(() => vi.clearAllMocks())

describe('Story — derived numbers, never literals (D-051 / Constraint A)', () => {
  it('renders counts, range, and non-folded targets from the payload', async () => {
    listAnalyses.mockResolvedValue(ANALYSES); getCoverage.mockResolvedValue(COVERAGE)
    const { container } = renderStory()
    await waitFor(() => expect(container.textContent).toMatch(/4 of the 5 cohort targets folded/))
    expect(container.textContent).toMatch(/3 of them ranked-and-folded/)
    expect(container.textContent).toContain('88.00')
    expect(container.textContent).toContain('FAKEIGF')
    expect(container.textContent).toContain('FAKEBIG')
  })

  it('does NOT hardcode any live cohort literal', async () => {
    listAnalyses.mockResolvedValue(ANALYSES); getCoverage.mockResolvedValue(COVERAGE)
    const { container } = renderStory()
    await waitFor(() => expect(container.textContent).toMatch(/4 of the 5 cohort targets folded/))
    for (const lit of LIVE_LITERALS) expect(container.textContent).not.toContain(lit)
  })

  it('names ESMFold and states we ran it', async () => {
    listAnalyses.mockResolvedValue(ANALYSES); getCoverage.mockResolvedValue(COVERAGE)
    const { container } = renderStory()
    await waitFor(() => expect(container.textContent).toMatch(/4 of the 5 cohort targets folded/))
    expect(container.textContent).toContain('ESMFold')
    expect(container.textContent.toLowerCase()).toContain('we ran the neural network ourselves')
  })

  it('links to /targets', async () => {
    listAnalyses.mockResolvedValue(ANALYSES); getCoverage.mockResolvedValue(COVERAGE)
    renderStory()
    const link = await screen.findByRole('link', { name: /folded targets/i })
    expect(link).toHaveAttribute('href', '/targets')
  })

  it('renders without numbers, not crashing, when both fetches reject', async () => {
    listAnalyses.mockRejectedValue(new Error('down')); getCoverage.mockRejectedValue(new Error('down'))
    const { container } = renderStory()
    await waitFor(() => expect(container.textContent).toContain('ESMFold'))
    for (const lit of LIVE_LITERALS) expect(container.textContent).not.toContain(lit)
    expect(container.textContent).toContain('See the folded targets')
  })
})

// ⚠⚠ THE STORY DESCRIBED AN 82-TARGET STUDY AND THE APPLICATION IS NO LONGER ONE.
// It told a reader this project had folded 79 proteins. It has folded 2,769. That was a faithful
// account on 2026-07-29; the census landed after. Owner ruling 2026-08-21: the census beat lands,
// the clinical layer is not excluded, and beat 5 stays qualitative with 32.2% in its right context.
const CENSUS = { manifest_rows: 3467, folded: 2690, max_mean_plddt: 89.25 }

describe('Story — the census beat (owner ruling 2026-08-21)', () => {
  const withCensus = async () => {
    listAnalyses.mockResolvedValue(ANALYSES)
    getCoverage.mockResolvedValue(COVERAGE)
    getCensusSummary.mockResolvedValue(CENSUS)
    const { container } = renderStory()
    await waitFor(() => expect(container.textContent).toMatch(/everything else/i))
    return container
  }

  it('states the census counts, derived and not literal', async () => {
    const c = await withCensus()
    expect(c.textContent).toMatch(/3,467/)
    expect(c.textContent).toMatch(/2,690/)
  })

  // ⚠⚠ D-079 decision 1, STATED rather than relied upon: a bigger pile of folds must not read as a
  // bigger shortlist.
  it('says the census is not scored and not ranked', async () => {
    const c = await withCensus()
    expect(c.textContent).toMatch(/not scored and not ranked/i)
    expect(c.textContent).toMatch(/a fold is a measurement, a score is an interpretation/i)
  })

  it('links to the census, which the Story never did', async () => {
    const c = await withCensus()
    const hrefs = [...c.querySelectorAll('a')].map((a) => a.getAttribute('href'))
    expect(hrefs).toContain('/census')
  })

  // ⚠ EVERY COUNT STATES ITS KEY. "79 targets folded" read as the project's total.
  it('scopes the cohort count to the cohort', async () => {
    const c = await withCensus()
    expect(c.textContent).toMatch(/cohort targets folded/)
  })

  // ⚠⚠ ADDITIVE, NEVER LOAD-BEARING. A census fetch that fails costs the census sentence and
  // nothing else — the rest of the page is the argument of the project.
  it('renders the whole story when the census summary is unavailable', async () => {
    listAnalyses.mockResolvedValue(ANALYSES)
    getCoverage.mockResolvedValue(COVERAGE)
    getCensusSummary.mockRejectedValue(new Error('down'))
    const { container } = renderStory()
    await waitFor(() => expect(container.textContent).toMatch(/cohort targets folded/))
    expect(container.textContent).not.toMatch(/everything else/i)
    expect(container.textContent).toMatch(/ESMFold/)
    expect(container.textContent).toMatch(/the real question is still open/i)
  })

  it('survives a supplier that is not a promise at all', async () => {
    // ⚠ my first version called .catch on the return value and crashed the entire page
    listAnalyses.mockResolvedValue(ANALYSES)
    getCoverage.mockResolvedValue(COVERAGE)
    getCensusSummary.mockReturnValue(undefined)
    const { container } = renderStory()
    await waitFor(() => expect(container.textContent).toMatch(/cohort targets folded/))
  })
})

describe('Story — where the evidence led (owner ruling: do not exclude the clinical layer)', () => {
  it('carries the tissue evidence, and both edges of it', async () => {
    listAnalyses.mockResolvedValue(ANALYSES)
    getCoverage.mockResolvedValue(COVERAGE)
    getCensusSummary.mockResolvedValue(CENSUS)
    const { container } = renderStory()
    await waitFor(() => expect(container.textContent).toMatch(/Human Protein Atlas/))
    // ⚠ D-093 decision 5 — the tumour panel alone is the flattering half
    expect(container.textContent).toMatch(/healthy/i)
    expect(container.textContent).toMatch(/expression measurement, not a claim/i)
  })

  // ⚠ Beat 5 stays QUALITATIVE; the figure appears only in its correct context, and F-051's caveat
  // travels with it — an attribution share is predictor weight, not a causal role.
  it('gives 32% its context rather than as a bare statistic', async () => {
    listAnalyses.mockResolvedValue(ANALYSES)
    getCoverage.mockResolvedValue(COVERAGE)
    getCensusSummary.mockResolvedValue(CENSUS)
    const { container } = renderStory()
    await waitFor(() => expect(container.textContent).toMatch(/32%/))
    expect(container.textContent).toMatch(/membrane-proximal/i)
    expect(container.textContent).toMatch(/not a claim that the region causes anything/i)
  })
})

// ⚠⚠ THE STORY'S PROSE CARRIES NO WARNING GLYPHS, and the first census/32% draft broke that.
// Found by walking `/` after deploy: exactly ONE paragraph of eleven had a `⚠`, the one I had just
// written. The glyph is the CARD convention — a caveat interrupting a table of numbers — and this
// page is continuous narrative, where one glyph in eleven paragraphs reads as an error message.
describe('Story — the narrative carries its caution in sentences, not glyphs', () => {
  it('renders no warning glyph in any paragraph', async () => {
    listAnalyses.mockResolvedValue(ANALYSES)
    getCoverage.mockResolvedValue(COVERAGE)
    getCensusSummary.mockResolvedValue(CENSUS)
    const { container } = renderStory()
    await waitFor(() => expect(container.textContent).toMatch(/32%/))
    const offenders = [...container.querySelectorAll('.story p')]
      .map((p, i) => ({ i, text: p.textContent.trim().slice(0, 60) }))
      .filter((_, i) => /⚠/.test(container.querySelectorAll('.story p')[i].textContent))
    expect(offenders).toEqual([])
  })

  // ⚠ and the caution itself must survive removing the glyph — the sentence carries it
  it('still says the 32% is not a causal claim', async () => {
    listAnalyses.mockResolvedValue(ANALYSES)
    getCoverage.mockResolvedValue(COVERAGE)
    getCensusSummary.mockResolvedValue(CENSUS)
    const { container } = renderStory()
    await waitFor(() => expect(container.textContent).toMatch(/32%/))
    expect(container.textContent).toMatch(/not a claim that the region causes anything/i)
  })
})

