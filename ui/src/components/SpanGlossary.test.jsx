import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import SpanGlossary from './SpanGlossary.jsx'
import {
  GPI_BADGE, GPI_SPAN_RULE, RANK_LIMITATION, SPAN_TERMS,
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
    // ⚠ The held category is now EMPTY — both terms were ruled accepted on 2026-08-07 after the
    // CSPA check. So the rejected terms are what makes the render test discriminate, and the
    // assertion says that rather than quietly dropping a control that no longer applies.
    expect(SPAN_TERMS.some((t) => t.ruling === 'held')).toBe(false)
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

  it('the two formerly-held terms are accepted, each carrying the evidence that decided it', () => {
    // ⚠ RULED 2026-08-07, and the two did NOT get the same answer — so neither may render as a
    // bare "accepted" with no reason. Prove it bites by trimming either reason to one clause.
    const mel = SPAN_TERMS.find((t) => t.term === 'Lumenal, melanosome')
    const vac = SPAN_TERMS.find((t) => t.term === 'Vacuolar')
    expect(mel.ruling).toBe('accepted')
    expect(vac.ruling).toBe('accepted')
    // melanosome: accepted on an orthogonal MEASUREMENT
    expect(mel.reason).toMatch(/Cell Surface Protein Atlas/i)
    expect(mel.reason).toMatch(/mass\s+spectrometry/i)
    // ⚠ vacuolar: accepted on COMPARTMENT BIOLOGY, and the n=2 caveat must travel with it, or the
    // surface would imply the two proteins carrying it are good targets. They are not.
    expect(vac.reason).toMatch(/compartment biology/i)
    expect(vac.reason).toMatch(/64 aa and 74 aa/)
    expect(vac.reason).toMatch(/sample of two/i)
  })

  it('the yeast term renders as ruled and rejected, not as an open question', () => {
    // ⚠ Rejected, NOT deleted. A term that vanishes reads as "nobody thought of it."
    const y = SPAN_TERMS.find((t) => t.term === 'Mother cell cytoplasmic')
    expect(y.ruling).toBe('rejected')
    render(<SpanGlossary />)
    expect(screen.getByText('Mother cell cytoplasmic')).toBeTruthy()
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

describe('the GPI span rule after the withdrawal of rule B', () => {
  it('shows the withdrawn fallback rather than quietly dropping it', () => {
    // ⚠ A rule that disappears silently is a rule someone re-invents. The surface says it existed,
    // what it did, and why it is gone. Prove it bites by deleting `withdrawn`.
    expect(GPI_SPAN_RULE.withdrawn).toMatch(/withdrawn/i)
    expect(GPI_SPAN_RULE.withdrawn).toMatch(/266 residues/)
    expect(GPI_SPAN_RULE.withdrawn).toMatch(/never produced a span/i)
    render(<SpanGlossary />)
    expect(screen.getByText(GPI_SPAN_RULE.withdrawn)).toBeTruthy()
  })

  it('says plainly that nothing is estimated when the anchor position is missing', () => {
    expect(GPI_SPAN_RULE.whenUnavailable).toMatch(/nothing is estimated/i)
    render(<SpanGlossary />)
    expect(screen.getByText(GPI_SPAN_RULE.whenUnavailable)).toBeTruthy()
  })
})
