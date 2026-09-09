// D-144: the `/method` section for the census structural rank.
//
// ⚠⚠ The failure worth guarding is not a missing paragraph — it is a paragraph that describes a
// TRACTABILITY order and lets a reader take it for a SUITABILITY one. So the checks are the four
// statements that keep the two apart: STRUCTURAL_ONLY (not HPA-weighted, not ADC-ready), this is
// not the learned cohort-82 scorer, the API is the source of truth and the sheet is a lens, and
// the census table itself still carries no score and no rank column.
import { render, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../api.js', () => ({
  getCensusSummary: vi.fn(), getCoverage: vi.fn(),
}))
import { getCoverage } from '../api.js'
import MethodNote from './MethodNote.jsx'

const FIXTURE = {
  coverage: { denominator: 7, ranked: 4, held_out: 2, excluded: 1 },
  failed: 0,
  rows: [
    { disposition: 'ranked', fold_status: 'folded' },
    { disposition: 'ranked', fold_status: 'not_folded' },
    { disposition: 'held_out', fold_status: 'folded' },
    { disposition: 'excluded', fold_status: 'not_folded' },
  ],
}

async function renderMethod() {
  getCoverage.mockResolvedValue(FIXTURE)
  const view = render(<MemoryRouter><MethodNote /></MemoryRouter>)
  await waitFor(() => expect(view.getByTestId('method-body')).toBeTruthy())
  return view
}

beforeEach(() => vi.clearAllMocks())

describe('MethodNote — the census structural rank (D-144)', () => {
  it('registers the section with an id so D-138 rail can reach it', async () => {
    const view = await renderMethod()
    const heading = view.container.querySelector('#census-structural-rank')
    expect(heading).toBeTruthy()
    expect(heading.tagName).toBe('H3')
    expect(heading.textContent).toMatch(/census structural rank/i)
    expect(heading.textContent).toMatch(/D-144/)
  })

  it('states the banner in full: structural only, not HPA-weighted, not ADC-ready', async () => {
    const view = await renderMethod()
    const banner = view.getByTestId('census-structural-only').textContent
    expect(banner).toMatch(/STRUCTURAL_ONLY/)
    expect(banner).toMatch(/not HPA-weighted/)
    expect(banner).toMatch(/not ADC-ready/)
    // ⚠ the four excluded factors are named, so their absence is a statement rather than a gap
    for (const excluded of [/tumour expression/i, /normal-tissue risk/i, /internalisation/i,
      /antigen\s+density/i]) {
      expect(banner).toMatch(excluded)
    }
    // ⚠⚠ the sentence that keeps a tractability order from reading as a suitability one
    expect(banner).toMatch(/does\s+not\s+mean/i)
    expect(banner).toMatch(/good drug target/i)
  })

  it('says it is not the learned cohort-82 scorer, and why the two are not comparable', async () => {
    const view = await renderMethod()
    const text = view.getByTestId('census-structural-not-the-scorer').textContent
    expect(text).toMatch(/not the learned scorer/i)
    expect(text).toMatch(/D-041/)
    expect(text).toMatch(/82/)
    expect(text).toMatch(/not comparable/i)
  })

  it('says the API is the source of truth and the spreadsheet is a lens', async () => {
    const view = await renderMethod()
    const text = view.getByTestId('census-structural-source-of-truth').textContent
    expect(text).toMatch(/source of\s+truth/i)
    expect(text).toMatch(/review lens/i)
    expect(text).toMatch(/api\/census-structural-ranking/)
    // ⚠ the direction of authority is stated, not implied
    expect(text).toMatch(/the API is right/i)
  })

  it('keeps the census table out of it: no score column, no rank column, unscored rows', async () => {
    const view = await renderMethod()
    const section = view.getByTestId('census-structural-rank-addendum').textContent
    expect(section).toMatch(/no score and no rank\s+column/i)
    expect(section).toMatch(/unscored/i)
    expect(section).toMatch(/default order is still the\s+accession/i)
  })

  // ⚠⚠ D-147. The failure worth guarding is not a missing paragraph either — it is a paragraph
  // that explains the multi-loop topology and lets a reader take it for a score adjustment or a
  // trafficking claim. So the three denials are asserted INDIVIDUALLY: a copy pass that keeps
  // "does not change the score" and drops "not internalisation" is exactly the plausible edit,
  // and one blob assertion would not see it.
  it('explains that the reported span is the largest segment, not the total', async () => {
    const view = await renderMethod()
    const text = view.getByTestId('census-structural-intermittent').textContent
    expect(text).toMatch(/several separate segments/i)
    expect(text).toMatch(/largest single segment/i)
    expect(text).toMatch(/not the total/i)
    expect(text).toMatch(/ecd_intermittent/)
    // ⚠ the ADC-specific reason it matters at all, in the reader's terms rather than F-037's
    expect(text).toMatch(/several loops/i)
    expect(text).toMatch(/D-147/)
  })

  it('denies the score, the trafficking claim and the GPI category — each on its own', async () => {
    const view = await renderMethod()
    const text = view.getByTestId('census-structural-intermittent-limits').textContent
    expect(text).toMatch(/does not change the score/i)
    expect(text).toMatch(/no protein moves up or down the list/i)
    expect(text).toMatch(/not internalisation/i)
    expect(text).toMatch(/GPI \/ no segment/)
    expect(text).toMatch(/by design/i)
  })

  it('points at where the count lives instead of typing it (Constraint A)', async () => {
    const view = await renderMethod()
    const text = view.getByTestId('census-structural-intermittent-limits').textContent
    // ⚠⚠ D-050 / D-051 Constraint A: a number on a surface is derived from a payload or it is not
    // on the surface at all. No component fetches /api/census-structural-ranking, so there is no
    // payload for this paragraph to derive from — it names the field and says why.
    expect(text).toMatch(/component_counts\.by_flag\.ecd_intermittent/)
    expect(text).toMatch(/not typed/i)
    expect(text).not.toMatch(/\b\d{1,3},\d{3}\b|\b\d{4,}\b/)
  })

  it('names no count of its own — the page types no census denominator here', async () => {
    const view = await renderMethod()
    const section = view.getByTestId('census-structural-rank-addendum').textContent
    // ⚠ D-050 / D-051 Constraint A: a number on a surface is derived from a payload or it is not
    // there at all. This section describes the population instead of typing 3,467 into the prose,
    // which is why it cannot come to disagree with the run it describes.
    // ⚠ The pattern is a POPULATION-SIZED number — `3,467` or `3467` — not any digit: the
    // section legitimately names decision ids (D-041 / D-060 / D-081) and the cohort's 82.
    expect(section).not.toMatch(/\b\d{1,3},\d{3}\b|\b\d{4,}\b/)
    expect(section).toMatch(/measured extracellular span/i)
  })
})
