// D-050: AdcContext's cohort statistics must be DERIVED from /api/analyses, not hardcoded.
// The stale literals (42 folded / 34.78 to 81.40 / 45% below 60) rotted when the cohort grew
// 42->79 (D-045/D-049). These tests pin derivation: a fixture payload -> the rendered numbers
// match the payload, so a future cohort change can't silently reintroduce a stale literal.
import { render, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../api.js', () => ({ listAnalyses: vi.fn() }))
import { listAnalyses } from '../api.js'
import AdcContext from './AdcContext.jsx'

// DISTINCTIVE numbers that cannot coincide with the stale literals (42 / 34.78 / 81.40 / 45%):
// 4 folded, range 40.00-88.00, 2 of 4 = 50% below 60, one unfolded (null, excluded from stats).
const FIXTURE = [
  { id: 1, gene: 'AA', mean_plddt: 40.0, disposition: 'ranked' },
  { id: 2, gene: 'BB', mean_plddt: 55.0, disposition: 'ranked' },
  { id: 3, gene: 'CC', mean_plddt: 70.0, disposition: 'ranked' },
  { id: 4, gene: 'DD', mean_plddt: 88.0, disposition: 'held_out' },
  { id: 5, gene: 'EE', mean_plddt: null, disposition: 'held_out' }, // unfolded -> not a folded target
]

const renderAdc = () => render(<MemoryRouter><AdcContext /></MemoryRouter>)

beforeEach(() => vi.clearAllMocks())

describe('AdcContext — cohort stats derived from /api/analyses, not hardcoded (D-050)', () => {
  it('renders folded count / pLDDT range / below-60 fraction from the payload', async () => {
    listAnalyses.mockResolvedValue(FIXTURE)
    const { container } = renderAdc()
    await waitFor(() => expect(container.textContent).toMatch(/4 folded targets/))
    expect(container.textContent).toMatch(/40\.00 to 88\.00/)
    expect(container.textContent).toMatch(/50% fall below 60/)
  })

  it('does NOT render the stale 42-fold-era literals', async () => {
    listAnalyses.mockResolvedValue(FIXTURE)
    const { container } = renderAdc()
    await waitFor(() => expect(container.textContent).toMatch(/4 folded targets/))
    expect(container.textContent).not.toMatch(/42 folded targets/)
    expect(container.textContent).not.toMatch(/34\.78 to 81\.40/)
    expect(container.textContent).not.toMatch(/45% fall below 60/)
  })
})

// D-107 — /about names the future msa path as not-built. These three ATs are self-contained and
// must go red if the section is missing, if the existing ADC copy was replaced, or if a forbidden
// product-edition string appears on the page. Negative assertions below are the only place those
// strings are allowed to appear in this change.
const ADC_COPY = 'antibody\u2013drug conjugate' // en-dash, as AdcContext.jsx renders it
const WHATS_NEXT = 'What\u2019s next (not built)' // curly apostrophe, as the heading renders it

describe('AdcContext — What’s next (not built) (D-107)', () => {
  beforeEach(() => {
    listAnalyses.mockResolvedValue(FIXTURE)
  })

  it('T-1071: /about still contains the existing ADC copy (antibody–drug conjugate)', () => {
    const { container } = renderAdc()
    expect(container.textContent).toContain(ADC_COPY)
  })

  it('T-1072: /about contains “What’s next (not built)” and “MSA” and “ESMFold stays”', () => {
    const { container } = renderAdc()
    const text = container.textContent
    expect(text).toContain(WHATS_NEXT)
    expect(text).toContain('MSA')
    expect(text).toContain('ESMFold stays')
  })

  it('T-1073: /about does not contain forbidden product-edition strings', () => {
    const { container } = renderAdc()
    const text = container.textContent
    // Negative assertions: these three strings must be absent from the rendered page.
    expect(text).not.toContain('v2')
    expect(text).not.toContain('version 2')
    expect(text).not.toContain('PharmFold 2')
  })
})

// ⚠⚠ D-094 amendment 1 decision 3 — /about names the paper QUESTIONS, never a result.
// Copy is owner-supplied (ABOUT-COPY-owner-supplied-2026-09-03.md) and transcribed verbatim.
//
// ⚠ F7 and U3 are failure-reds against the pre-amendment component: the section is absent, so the
// first assertion in each fails on a missing string, not on an import or a crash.
// ⚠⚠ F8 is DIFFERENT and is called out rather than hidden: it is a pure ABSENCE guard, so it
// PASSES before the section exists. It is not testing what it claims until the copy is there.
describe('D-094 amendment 1 — the paper questions on /about', () => {
  beforeEach(() => {
    listAnalyses.mockResolvedValue(FIXTURE)
  })

  it('F7: renders both questions from one source list, each carrying its status', () => {
    const t = renderAdc().container.textContent.replace(/\s+/g, ' ')
    expect(t).toContain('The questions this project is trying to answer')
    expect(t).toMatch(/Does the shape of a protein/)
    expect(t).toMatch(/What can an expression-threshold screen actually support\?/)
    // ⚠ ONE list, one standing line: the status belongs to the section and renders exactly once.
    expect(t.match(/nothing has been peer-reviewed/g) || []).toHaveLength(1)
  })

  it('F8: the paper section RENDERS, and carries no result figure', () => {
    // ⚠⚠ REVISED. The first version asserted absence only, so it passed against a page with no
    // paper section at all — it could not tell "no numbers" from "no section", and it went green
    // before the copy existed. ⚠ A guard that cannot distinguish those two states is a decoration.
    //
    // Presence and absence are now asserted TOGETHER, in one test:
    //   · remove the section  → the first expect fails
    //   · add a result figure → one of the loop's expects fails
    // ⚠ Shown to bite before this was committed: a temporary `0.6607` in the copy failed it AT the
    // assertion, and reverting the copy returned it to green. The revert was never committed.
    const t = renderAdc().container.textContent
    expect(t).toContain('The questions this project is trying to answer')
    for (const forbidden of ['0.6607', '0.6786', '8 of 12', '9 of 12', '0.49', '0.62']) {
      expect(t).not.toContain(forbidden)
    }
  })

  it('U3: a reader cannot conclude any paper is published, submitted, or peer-reviewed', () => {
    const t = renderAdc().container.textContent.replace(/\s+/g, ' ')
    // the disclaimer is present, unhedged and not a footnote
    expect(t).toMatch(/nothing has been peer-reviewed/)
    expect(t).toMatch(/has been submitted for publication/)
    // and no affirmative publication claim anywhere on the page
    expect(t).not.toMatch(/under review|accepted (at|by)|in press|published in/i)
  })
})
