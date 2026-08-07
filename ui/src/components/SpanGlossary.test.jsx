import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import SpanGlossary from './SpanGlossary.jsx'
import {
  GPI_BADGE, RANK_LIMITATION, SPAN_TERMS,
} from '../spanGlossary.js'

// R4, and every assertion here is about a distinction that has already cost this project something.
//
// ⚠ A-017 clause (c) applies to a UI test too: the fixture must contain a case where the correct
// and the incorrect implementation differ. A glossary that rendered only its accepted terms would
// pass "the accepted terms are on screen" — so the discriminating assertion is that the REJECTED
// ones are on screen, with their reasons.

describe('the span vocabulary surface (R4)', () => {
  it('renders every term — accepted, held, unruled AND rejected alike', () => {
    render(<SpanGlossary />)
    // ⚠ THE DISCRIMINATING ASSERTION. Prove it bites by filtering the list to accepted terms: a
    // term simply absent reads as "nobody thought of it", and this reds naming the missing one.
    for (const t of SPAN_TERMS) {
      expect(screen.getByText(t.term), `"${t.term}" (${t.ruling}) is not on the page`).toBeTruthy()
    }
  })

  it('the fixture actually contains rejected terms, so the test above can discriminate', () => {
    // ⚠ A-017 clause (c), asserted rather than assumed. With an all-accepted vocabulary the
    // assertion above passes under an implementation that hides rejections.
    const rejected = SPAN_TERMS.filter((t) => t.ruling === 'rejected')
    expect(rejected.length).toBeGreaterThan(0)
    expect(SPAN_TERMS.some((t) => t.ruling === 'held')).toBe(true)
  })

  it('every term states a compartment, a reason and a plain-language sentence', () => {
    // ⚠ Plain language BESIDE the technical, both present. One does work the other does not.
    for (const t of SPAN_TERMS) {
      expect(t.compartment, `${t.term} has no compartment`).toBeTruthy()
      expect(t.reason, `${t.term} has no reason`).toBeTruthy()
      expect(t.plain, `${t.term} has no plain-language sentence`).toBeTruthy()
      expect(t.plain).not.toBe(t.reason)
    }
  })

  it('Perinuclear space is accepted and Nuclear is rejected, and both are shown', () => {
    // ⚠ THE TRAP, ON THE SURFACE. A reader who sees only "nuclear terms are rejected" would
    // reasonably assume Perinuclear space went with them. Both rulings are visible so the
    // distinction is checkable rather than trusted.
    const peri = SPAN_TERMS.find((t) => t.term === 'Perinuclear space')
    const nuc = SPAN_TERMS.find((t) => t.term === 'Nuclear')
    expect(peri.ruling).toBe('accepted')
    expect(nuc.ruling).toBe('rejected')
    render(<SpanGlossary />)
    expect(screen.getByText('Perinuclear space')).toBeTruthy()
    expect(screen.getByText('Nuclear')).toBeTruthy()
  })

  it('the held terms are not presented as accepted', () => {
    // Prove it bites by relabelling `held` as `accepted`: five surface proteins would read as
    // foldable on a surface, before the check that governs them has run.
    const held = SPAN_TERMS.filter((t) => t.ruling === 'held').map((t) => t.term)
    expect(held).toContain('Vacuolar')
    expect(held).toContain('Lumenal, melanosome')
    render(<SpanGlossary />)
    for (const term of held) {
      const dt = screen.getByText(term).closest('dt')
      expect(dt.textContent).toMatch(/Held/)
      expect(dt.textContent).not.toMatch(/^.*Accepted/)
    }
  })

  it('the compartment reasoning discloses that it was not sourced at first hand', () => {
    // ⚠ D-016 on the surface. A reader who cannot tell a sourced claim from an unsourced one has
    // been given confidence, not information.
    render(<SpanGlossary />)
    expect(screen.getByText(/not read from a primary source/i)).toBeTruthy()
  })
})

describe('the GPI badge (4a)', () => {
  it('is not a score, a rank or a positive signal', () => {
    expect(GPI_BADGE.isScore).toBe(false)
  })

  it('shows the attribute AND the limitation together, never the attribute alone', () => {
    // ⚠ READ TWICE. The badge exists to disclose a delivery liability. A badge that said only
    // "GPI-anchored" would read as a feature of the target rather than a caveat about it.
    // Prove it bites by trimming the tooltip to its first sentence: the limitation clauses vanish
    // and this reds on each one.
    const t = GPI_BADGE.tooltip
    expect(t).toMatch(/whole mature chain is extracellular/i)   // the attribute
    expect(t).toMatch(/no cytoplasmic tail/i)                   // why it matters
    expect(t).toMatch(/recycle back to the surface/i)           // the mechanism
    expect(t).toMatch(/lysosome/i)                              // where the payload comes off
    expect(t).toMatch(/blind to internalisation/i)              // the method's own limit
    expect(t).toMatch(/does not predict payload delivery/i)     // the claim boundary
  })

  it('names the counter-example rather than overstating the liability', () => {
    // Not disqualifying — folate receptor alpha is GPI-anchored and an approved ADC targets it.
    expect(GPI_BADGE.tooltip).toMatch(/folate receptor alpha/i)
  })

  it('renders the whole tooltip, so no clause can be lost between the store and the screen', () => {
    render(<SpanGlossary />)
    expect(screen.getByText(GPI_BADGE.tooltip)).toBeTruthy()
  })
})

describe('the standing limitation line', () => {
  it('names all three blind spots, not just internalisation', () => {
    expect(RANK_LIMITATION).toMatch(/internalisation/i)
    expect(RANK_LIMITATION).toMatch(/expression level/i)
    expect(RANK_LIMITATION).toMatch(/antigen copy number/i)
  })

  it('renders wherever the span surface does', () => {
    render(<SpanGlossary />)
    expect(screen.getByText(RANK_LIMITATION)).toBeTruthy()
  })
})
