import { render } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import SurfaceCheck from './SurfaceCheck.jsx'

const INSTRUMENTS = {
  census: 'UniProt topology annotation — sequence and curation',
  hpa_if: 'HPA immunofluorescence — antibodies imaged in fixed cells',
}
const base = (over) => ({
  main_locations: [], if_reliability: null, unreconciled_locations: [],
  instruments: INSTRUMENTS, unreconciled_causes: [], ...over,
})
const text = (b) => render(<SurfaceCheck check={b} />).container.textContent

describe('SurfaceCheck', () => {
  // ⚠⚠ THE POINT OF THE WHOLE SECTION: corroboration means nothing unless the reader can see the
  // two sources are different KINDS of evidence.
  it('names both instruments and says why that matters', () => {
    const t = text(base({ category: 'corroborated_membrane', main_locations: ['Plasma membrane'] }))
    expect(t).toMatch(/UniProt topology/)
    expect(t).toMatch(/immunofluorescence/)
    expect(t).toMatch(/wrong in different ways/i)
  })

  // ⚠⚠ THE TRAP. A Golgi/vesicle call must read as SUPPORT — it is the route to the surface.
  it('renders the secretory route as support, never as contradiction', () => {
    const t = text(base({ category: 'corroborated_route', main_locations: ['Golgi apparatus'] }))
    expect(t).toMatch(/Confirmed on the route to the surface/)
    expect(t).toMatch(/supports the surface assignment rather than contradicting/i)
    expect(t).not.toMatch(/do not line up/i)
    expect(t).not.toMatch(/\bfail(ed|s)?\b/i)
  })

  it('a membrane call reads as two kinds of evidence agreeing', () => {
    const t = text(base({ category: 'corroborated_membrane', main_locations: ['Plasma membrane'] }))
    expect(t).toMatch(/Confirmed at the cell surface/)
    expect(t).toMatch(/Two different kinds of evidence agree/)
  })

  // ⚠⚠ A DISAGREEMENT IS NOT A VERDICT ON THE PROTEIN — all three causes must show.
  it('never shows a disagreement without all three possible causes', () => {
    const t = text(base({
      category: 'unreconciled',
      main_locations: ['Mitochondria'],
      unreconciled_locations: ['Mitochondria'],
      unreconciled_causes: [
        'the UniProt topology annotation may be wrong',
        'the HPA antibody may be non-specific, or the cell line may not express the protein',
        'the protein may genuinely do both, at different times or in different tissues',
      ],
    }))
    expect(t).toMatch(/do not line up/i)
    expect(t).toMatch(/UniProt topology annotation may be wrong/)
    expect(t).toMatch(/antibody may be non-specific/)
    expect(t).toMatch(/genuinely do both/)
    // ⚠ and it must not convict the protein
    expect(t).not.toMatch(/not a surface protein/i)
    expect(t).not.toMatch(/\bwrong protein\b/i)
  })

  // ⚠⚠ "nobody looked" is not "failed a check" — and it is the most common case.
  it('states that no second opinion means nobody looked', () => {
    const t = text(base({ category: 'if_not_attempted' }))
    expect(t).toMatch(/nobody looked/i)
    expect(t).toMatch(/not that the surface assignment failed a check/i)
    expect(t).toMatch(/most common case/i)
  })

  it("carries HPA's own reliability, labelled as theirs", () => {
    const t = text(base({
      category: 'corroborated_membrane', main_locations: ['Plasma membrane'],
      if_reliability: 'Enhanced',
    }))
    expect(t).toMatch(/the atlas rates its own call/i)
    expect(t).toMatch(/Enhanced/)
  })

  // ⚠ no score, no grade, no ordering
  it('shows no score, confidence percentage or grade', () => {
    const t = text(base({ category: 'corroborated_membrane', main_locations: ['Plasma membrane'] }))
    expect(t).not.toMatch(/\bscore\b/i)
    expect(t).not.toMatch(/\d+%/)
    expect(t).not.toMatch(/\brank(ed|ing)?\b/i)
  })

  it('renders nothing when there is no check at all', () => {
    expect(text(null)).toBe('')
    expect(text(base({ category: 'not_a_real_category' }))).toBe('')
  })
})
