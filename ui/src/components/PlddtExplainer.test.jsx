import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import PlddtExplainer from './PlddtExplainer.jsx'
import { COHORT_MAX_PLDDT } from '../plddt.js'

describe('PlddtExplainer', () => {
  it('says pLDDT is a self-report, not a measurement', () => {
    render(<PlddtExplainer />)
    expect(screen.getByText(/self-report, not a measurement/i)).toBeInTheDocument()
  })

  // ⚠ The cohort max is read from the single source, never typed in. A hand-copied 84.23 would go
  // stale the moment another fold beat it, and the page would quietly assert an old ceiling.
  it('reads the cohort max from plddt.js rather than hard-coding it', () => {
    render(<PlddtExplainer />)
    expect(screen.getByText(String(COHORT_MAX_PLDDT))).toBeInTheDocument()
    const src = PlddtExplainer.toString()
    expect(src).not.toMatch(/84\.23/)
  })

  // ⚠⚠ The whole point of the section. A page that listed only levers would teach a reader to push
  // a number that, for a disordered region, cannot move and should not.
  it('states that a disordered region cannot be improved by any amount of compute', () => {
    render(<PlddtExplainer />)
    expect(screen.getByText(/intrinsically disordered/i)).toBeInTheDocument()
    expect(screen.getByText(/because a confident answer would be wrong/i)).toBeInTheDocument()
  })

  it('does not claim any alternative method was actually run', () => {
    render(<PlddtExplainer />)
    expect(
      screen.getByText(/described as available, not\s+as attempted/i),
    ).toBeInTheDocument()
  })

  it('distinguishes pLDDT from PAE rather than letting the reader conflate them', () => {
    render(<PlddtExplainer />)
    expect(screen.getByText(/predicted aligned error/i)).toBeInTheDocument()
  })

  it('adds the assembler addendum only on assembled pages', () => {
    const { rerender, container } = render(<PlddtExplainer />)
    expect(container.querySelector('[data-testid="assembled-explainer"]')).toBeNull()
    rerender(<PlddtExplainer assembled />)
    const add = container.querySelector('[data-testid="assembled-explainer"]')
    expect(add).toBeTruthy()
    expect(add.textContent).toMatch(/winner-tile/)
    expect(add.textContent).toMatch(/null, never 0/)
    expect(add.textContent).not.toMatch(/will be fixed by alignment/)
  })
})
