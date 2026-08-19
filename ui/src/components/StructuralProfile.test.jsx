import { render } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import StructuralProfile from './StructuralProfile.jsx'

// ⚠⚠ D-089: "a census page still carries no scorer panel", and D-079 amendment 1: "a profile block
// must not become that page by another name." These tests pin the differences that keep it from
// being one. Distinctive fixture numbers that cannot coincide with a live value (D-050).
const COMPUTED = {
  kind: 'structural_profile',
  status: 'computed',
  structural_profile: 0.1876,
  refusal: null,
  out_of_range_features: [],
  mount_preconditions: [
    'unlabelled — there is no leave-one-out here.',
    'out of the fit population — 56 targets from an expression-selected cohort (A-014).',
    'not a probability — F-006 records values compressed toward the base rate.',
    'confidence-dominated — F-051 measures membrane_proximal_plddt carrying 32.2%.',
    'the mean_plddt_ecd bound is partly a selection artefact.',
  ],
  provenance: 'run 2 (scorer_version 91e646e4a289), applied from thirteen recovered parameters',
  bar: 'refused where any feature falls outside the cohort observed min-max. Not p05-p95; not +/-3 sd.',
  band_context: {
    cohort_fitted_min: 0.116,
    cohort_fitted_max: 0.285,
    note: 'This axis does not separate targets by much.',
  },
  support_used: {},
}

const REFUSED = {
  ...COMPUTED,
  status: 'refused',
  structural_profile: null,
  refusal: {
    category: 'refused_out_of_distribution',
    detail: '1 of 6 features outside the fit population support: mean_plddt_ecd=31.2 outside [50.49, 81.4]',
  },
  out_of_range_features: ['mean_plddt_ecd'],
}

describe('StructuralProfile', () => {
  it('names it a profile and says outright that it is not a score or a rank (ruling 1)', () => {
    const { container } = render(<StructuralProfile block={COMPUTED} />)
    const t = container.textContent
    expect(t).toMatch(/Structural profile/)
    expect(t).toMatch(/not a score and not a rank/i)

    // ⚠⚠ THIS ASSERTION WAS WRONG BEFORE IT WAS RIGHT, and the correction belongs here rather than
    // in a commit message nobody re-reads. It first banned /\brank\b/ across the whole text — and
    // reddened on the DENIAL, "not a score and not a rank." A blanket ban on a word cannot tell a
    // prohibition from a violation; it is the same defect F-052 records, in a third form.
    //
    // The risk is not the word appearing. It is the word LABELLING the value. So: no heading and
    // no field label may use it.
    const headings = [...container.querySelectorAll('h1,h2,h3,h4,h5,summary')]
      .map((e) => e.textContent)
    expect(headings.join(' | ')).not.toMatch(/score|rank|suitab/i)
    expect(t).not.toMatch(/\b(score|rank|ranking|suitability)\s*[:=]/i)
  })

  it('never shows the value without the cohort band beside it (F-006, ruling 4)', () => {
    const t = render(<StructuralProfile block={COMPUTED} />).container.textContent
    expect(t).toMatch(/0\.1876/)
    expect(t).toMatch(/0\.116/)
    expect(t).toMatch(/0\.285/)
    expect(t).toMatch(/does not separate targets by much/)
  })

  it('renders every mount precondition, not a link to them (ruling 4)', () => {
    const t = render(<StructuralProfile block={COMPUTED} />).container.textContent
    for (const m of COMPUTED.mount_preconditions) expect(t).toContain(m)
  })

  // ⚠⚠ the refusal is the point of ruling 3 — it must be as prominent as a value, never a dash
  it('renders a refusal as a stated category with its cause, and shows NO number', () => {
    const t = render(<StructuralProfile block={REFUSED} />).container.textContent
    expect(t).toMatch(/Refused/)
    expect(t).toMatch(/refused out of distribution/)
    expect(t).toMatch(/mean_plddt_ecd/)
    expect(t).toMatch(/outside \[50\.49, 81\.4\]/)
    expect(t).not.toMatch(/0\.1876/)
    expect(t).toMatch(/No value is shown because none was computed/)
  })

  it('a refused protein still carries the preconditions — the frame does not vanish', () => {
    const t = render(<StructuralProfile block={REFUSED} />).container.textContent
    for (const m of REFUSED.mount_preconditions) expect(t).toContain(m)
  })

  it('renders nothing at all when the block is absent, rather than an empty panel', () => {
    const { container } = render(<StructuralProfile block={null} />)
    expect(container.textContent).toBe('')
  })

  it('states the bar and names the two settings it is not (F-043: the dial must be visible)', () => {
    const t = render(<StructuralProfile block={COMPUTED} />).container.textContent
    expect(t).toMatch(/p05-p95/)
    expect(t).toMatch(/sd/)
  })
})
