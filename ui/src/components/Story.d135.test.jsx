// D-135 — the Story becomes skimmable, and stops being silent about how the longest folds were made.
//
// ⚠⚠ THE THREE COMPLAINTS THESE PIN. (1) Eleven paragraphs with no way in: no contents, no summary
// strip, one CTA. (2) No cold-open figure a reader could take away in ten seconds. (3) Not one word
// about the hold-48 tiling — three weeks of work, six stitch algorithms and a rental that opened and
// closed, and a reader of this page would infer one forward pass per protein. That third one is the
// same shape as beat 2b's own recorded lapse, one arc further along: the page stopped describing the
// application and nothing objected.
//
// ⚠ FIXTURE VALUES THAT CANNOT COINCIDE WITH ANY LIVE FIGURE, and they are driven to two different
// sets in the Constraint-A test below — a literal in the JSX could satisfy at most one of them.
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../api.js', () => ({
  getCensusSummary: vi.fn(), listAnalyses: vi.fn(), getCoverage: vi.fn(),
}))
import { listAnalyses, getCoverage, getCensusSummary } from '../api.js'
import Story from './Story.jsx'

const ANALYSES = [
  { mean_plddt: 40.0 }, { mean_plddt: 55.0 }, { mean_plddt: 70.0 }, { mean_plddt: 88.0 },
  { mean_plddt: null },
]
const COVERAGE = {
  coverage: { denominator: 5 },
  rows: [
    { disposition: 'ranked', fold_status: 'folded', gene: 'AAA' },
    { disposition: 'ranked', fold_status: 'folded', gene: 'BBB' },
    { disposition: 'ranked', fold_status: 'folded', gene: 'CCC' },
    { disposition: 'held_out', fold_status: 'folded', gene: 'DDD' },   // folded, NOT ranked
    { disposition: 'held_out', fold_status: 'failed', gene: 'FAKEIGF' },
    { disposition: 'excluded', fold_status: 'not_folded', gene: 'FAKEBIG' },
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
  ],
}

const mounted = async () => {
  const out = render(<MemoryRouter><Story /></MemoryRouter>)
  await waitFor(() => expect(out.container.textContent).toMatch(/cohort targets folded/))
  return out
}

beforeEach(() => {
  vi.clearAllMocks()
  listAnalyses.mockResolvedValue(ANALYSES)
  getCoverage.mockResolvedValue(COVERAGE)
  getCensusSummary.mockResolvedValue(CENSUS)
})

describe('D-135 — the cold strip, and every figure in it is derived', () => {
  // ⚠⚠ THE SAME RULE AS CoverageLine, NOT THE FOLDED TOTAL. The fixture has 4 folded rows and only
  // 3 of them ranked, so a strip printing 4 has quietly used the flattering number D-024 forbids.
  it('states the cohort ranked-and-folded intersection, not the folded count', async () => {
    const { container } = await mounted()
    const strip = container.querySelector('.story-cold-strip')
    expect(strip).toBeTruthy()
    const cohort = strip.querySelectorAll('div')[0]
    expect(cohort.querySelector('dt').textContent).toBe('3')
    expect(cohort.textContent).toMatch(/ranked and folded/i)
  })

  it('states the census population as its own, separate figure', async () => {
    const { container } = await mounted()
    const strip = container.querySelector('.story-cold-strip').textContent
    expect(strip).toMatch(/2,691/)
    expect(strip).toMatch(/wider census/i)
    expect(strip).toMatch(/different population/i)
    expect(strip).toMatch(/different span rule/i)
  })

  // ⚠ Read out of the payload's own `structure_kinds` breakdown — never counted here, never typed.
  it('states the tile-assembled count out of the structure_kinds breakdown', async () => {
    const { container } = await mounted()
    const strip = container.querySelector('.story-cold-strip').textContent
    expect(strip).toMatch(/46/)
    expect(strip).toMatch(/overlapping tiles/i)
    expect(strip).toMatch(/provisional/i)
  })

  // ⚠⚠ CONSTRAINT A, AS A MOVING TARGET. Two payloads, two renders, no literal can satisfy both.
  // Prove it bites by typing any of these six numbers into Story.jsx.
  it('every figure moves when the payload moves', async () => {
    // ⚠ the `dt` elements, not the concatenated text: the figures sit against their labels with no
    // whitespace between them, so a word-boundary match on `textContent` reads "3cohort".
    const figures = (c) => [...c.querySelectorAll('.story-cold-strip dt')].map((d) => d.textContent)
    expect(figures((await mounted()).container)).toEqual(['3', '2,691', '46'])

    vi.clearAllMocks()
    listAnalyses.mockResolvedValue(ANALYSES)
    getCoverage.mockResolvedValue({
      coverage: { denominator: 7 },
      rows: [
        { disposition: 'ranked', fold_status: 'folded', gene: 'AAA' },
        { disposition: 'ranked', fold_status: 'folded', gene: 'BBB' },
        { disposition: 'ranked', fold_status: 'not_folded', gene: 'CCC' },
      ],
    })
    getCensusSummary.mockResolvedValue({
      ...CENSUS,
      folded: 1234,
      structure_kinds: [{ kind: 'assembled', label: 'assembled (provisional)', n: 99 }],
    })
    const second = (await mounted()).container
    expect(figures(second)).toEqual(['2', '1,234', '99'])
    expect(second.querySelector('.story-cold-strip').textContent).not.toMatch(/2,691/)
  })

  // ⚠ A kind absent from the payload has no entry, and `assembled 0` is not a finding — it is what
  // the census truthfully showed for all 45 assembled parents before D-134 repaired the identity
  // check. The chip simply does not render.
  it('draws no tile chip when the payload carries no assembled kind', async () => {
    getCensusSummary.mockResolvedValue({
      ...CENSUS, structure_kinds: [{ kind: 'single-pass', label: 'single-pass', n: 12 }],
    })
    const { container } = await mounted()
    const strip = container.querySelector('.story-cold-strip').textContent
    expect(strip).not.toMatch(/overlapping tiles/i)
    expect(strip).toMatch(/2,691/)          // the census figure still stands
  })

  // ⚠ Additive, like the census beat: a failed summary costs the two census chips, never the page.
  it('renders the cohort chip alone when the census summary is unavailable', async () => {
    getCensusSummary.mockRejectedValue(new Error('down'))
    const { container } = await mounted()
    const strip = container.querySelector('.story-cold-strip')
    expect(strip.querySelectorAll('div').length).toBe(1)
    expect(strip.textContent).toMatch(/ranked and folded/i)
  })
})

describe('D-135 — the beat contents, and its anchors resolve', () => {
  // ⚠⚠ EVERY ANCHOR MUST HAVE A TARGET. A contents entry that scrolls nowhere is worse than none,
  // and the failure is silent — a renamed section leaves a dead link and nothing renders red.
  // Prove it bites by changing one `id` in Story.jsx without changing BEATS.
  it('every contents link points at a section that exists on the page', async () => {
    const { container } = await mounted()
    const toc = container.querySelector('.story-toc')
    const anchors = [...toc.querySelectorAll('a')]
    expect(anchors.length).toBeGreaterThanOrEqual(5)
    for (const a of anchors) {
      const id = a.getAttribute('href').replace('#', '')
      expect(id).not.toBe('')
      expect(container.querySelector(`section#${id}`), `no section for #${id}`).toBeTruthy()
    }
  })

  it('every section on the page is reachable from the contents', async () => {
    const { container } = await mounted()
    const hrefs = new Set([...container.querySelectorAll('.story-toc a')]
      .map((a) => a.getAttribute('href')))
    for (const s of container.querySelectorAll('section[id]')) {
      expect(hrefs.has(`#${s.id}`), `section #${s.id} is in no contents entry`).toBe(true)
    }
  })

  it('names the beats a reader is looking for, including the tiling one', async () => {
    const { container } = await mounted()
    const toc = container.querySelector('.story-toc').textContent
    expect(toc).toMatch(/cohort/i)
    expect(toc).toMatch(/everything else/i)
    expect(toc).toMatch(/tiles/i)
    expect(toc).toMatch(/seams/i)
    expect(toc).toMatch(/still open/i)
  })

  // ⚠ A contents entry for a beat that did not render is a dead anchor. Both come off one list.
  it('drops the census beats from the contents when the census summary is unavailable', async () => {
    getCensusSummary.mockRejectedValue(new Error('down'))
    const { container } = await mounted()
    const toc = container.querySelector('.story-toc')
    expect(toc.textContent).not.toMatch(/tiles/i)
    for (const a of toc.querySelectorAll('a')) {
      const id = a.getAttribute('href').replace('#', '')
      expect(container.querySelector(`section#${id}`), `no section for #${id}`).toBeTruthy()
    }
  })

  // ⚠ The site nav and this contents are two navigation landmarks now, so both are NAMED — an
  // unlabelled landmark is ambiguous to a screen reader, and there used to be only one.
  it('exposes the contents as a named navigation landmark', async () => {
    await mounted()
    expect(screen.getByRole('navigation', { name: /what this page covers/i })).toBeInTheDocument()
  })
})

describe('D-135 — the hold-48 beat says what was done and what was not', () => {
  const beat = async () => {
    const { container } = await mounted()
    return container.querySelector('#beat-hold48').textContent
  }

  it('says the long spans were cut into overlapping tiles and joined by confidence', async () => {
    const t = await beat()
    expect(t).toMatch(/too long to fold in one go/i)
    expect(t).toMatch(/overlapping tiles/i)
    expect(t).toMatch(/more confident/i)
  })

  // ⚠⚠ EVERY ONE OF THESE HEDGES IS LOAD-BEARING AND NONE IS OPTIONAL. Drop any single one and the
  // beat becomes the overstatement six decisions have refused to make. Prove each bites by deleting
  // the clause: D-133/D-134 (provisional), D-118/D-121 (assembler, not superimposed), D-127/D-128
  // OPS (best so far, and it did not fix most seams), D-129 (recorded, not solved), D-118 (rental
  // CLOSED), D-109 ruling 7 (not in the ranking).
  it('keeps the assembly provisional and says the label is about method, not quality', async () => {
    const t = await beat()
    expect(t).toMatch(/provisional/i)
    expect(t).toMatch(/how the structure was made, never how good it is/i)
  })

  it('says the seams are recorded rather than solved', async () => {
    const t = await beat()
    expect(t).toMatch(/recorded, not solved/i)
    expect(t).toMatch(/did not repair most of the seams/i)
  })

  it('states that the join is not the same thing as folding the whole span', async () => {
    const t = await beat()
    expect(t).toMatch(/not the same thing as folding the whole span/i)
  })

  it('says these structures are not in the ranking (D-109 ruling 7)', async () => {
    const t = await beat()
    expect(t).toMatch(/not\s+in the ranking/i)
  })

  it('says the rented hardware is closed (D-118)', async () => {
    const t = await beat()
    expect(t).toMatch(/closed/i)
    // ⚠ and it must never read as an invitation to re-open it
    expect(t).not.toMatch(/rent a|deploy/i)
  })

  // ⚠⚠ NO SEAM CLAIM, ASSERTED BY ABSENCE. The one thing this beat must never say.
  it('never claims a seam was solved, fixed or repaired', async () => {
    const t = await beat()
    expect(t).not.toMatch(/seams? (are|were) (now )?(solved|fixed|repaired)/i)
    expect(t).not.toMatch(/superimposed(?!.{0,12}\bnot\b)/i)
  })

  // ⚠ Constraint A: no fold count is baked into this copy. The counts live in the derived strip.
  it('bakes no count into the tiling copy', async () => {
    const t = await beat()
    expect(t).not.toMatch(/\d/)
  })

  it('sits after the census widen, not before it', async () => {
    const { container } = await mounted()
    const census = container.querySelector('#beat-census')
    const hold48 = container.querySelector('#beat-hold48')
    expect(census.compareDocumentPosition(hold48) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
  })

  it('points at the filtered census and at the Method page', async () => {
    const { container } = await mounted()
    const hrefs = [...container.querySelectorAll('#beat-hold48 a')]
      .map((a) => a.getAttribute('href'))
    expect(hrefs).toContain('/census?structure=assembled')
    expect(hrefs).toContain('/method')
  })
})

describe('D-135 — the CTA splits, and the narrative keeps its register', () => {
  it('offers both populations, and neither as the better one', async () => {
    const { container } = await mounted()
    const hrefs = [...container.querySelectorAll('.story-cta a')].map((a) => a.getAttribute('href'))
    expect(hrefs).toEqual(['/targets', '/census?structure=assembled'])
    const cta = container.querySelector('.story-cta').textContent
    expect(cta).not.toMatch(/best|recommend|start here|instead/i)
  })

  // ⚠ The existing ruling, re-asserted over the new prose: `⚠` is the CARD convention, and one glyph
  // in eleven paragraphs of continuous narrative reads as an error message. The strip and the
  // contents are not paragraphs, and the new beats carry their caution in sentences.
  it('renders no warning glyph anywhere on the page, including the new beats', async () => {
    const { container } = await mounted()
    expect(container.textContent).not.toMatch(/⚠/)
  })
})
