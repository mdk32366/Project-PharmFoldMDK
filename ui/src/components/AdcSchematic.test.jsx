// D-052 / D-096: the load-bearing test asserts the MECHANISM, not just the words — with the entire
// api.js module mocked, the schematic must invoke NONE of its exports. An absent import is what
// makes the component structurally incapable of being a model output; a label alone could be edited
// away.
//
// ⚠ D-096 changed the MEDIUM (hand-rolled SVG -> imported raster) and NOT that property. A static
// imported asset takes no props and calls no API, so the guarantee survives the swap for exactly the
// same reason it always held. The test below is unchanged in intent and is why the swap is safe.
//
// ⚠⚠ D-096's new blind spot, asserted here because nothing else can: the graphic's words are now
// PIXELS. No test in this repo can read them. The `alt` transcription is the only version-controlled
// record of what the image says, so these tests pin it — if the asset is ever replaced, the alt must
// be revisited deliberately rather than inherited.
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi } from 'vitest'

const spies = {
  listAnalyses: vi.fn(),
  getCoverage: vi.fn(),
  getAnalysis: vi.fn(),
  getPlddt: vi.fn(),
  structureUrl: vi.fn(),
}
vi.mock('../api.js', () => spies)

import AdcSchematic from './AdcSchematic.jsx'

const renderIt = () => render(<MemoryRouter><AdcSchematic /></MemoryRouter>)

describe('AdcSchematic — an illustration, structurally not a model output (D-052)', () => {
  it('renders the "not a structure produced by this system" label', () => {
    const { container } = renderIt()
    expect(container.textContent).toContain(
      'Schematic illustration — not a structure produced by this system',
    )
  })

  it('invokes NO api.js export — it cannot be a model output', () => {
    renderIt()
    for (const [name, spy] of Object.entries(spies)) {
      expect(spy, `AdcSchematic must not call api.${name}`).not.toHaveBeenCalled()
    }
  })

  it('links to a real folded target', () => {
    renderIt()
    const link = screen.getByRole('link', { name: /real folded structure/i })
    expect(link).toHaveAttribute('href', '/target/1')
  })
})

describe('AdcSchematic — the D-096 raster asset and its transcription', () => {
  it('renders the imported illustration as an <img> with a resolved src', () => {
    renderIt()
    const img = screen.getByRole('img')
    expect(img.tagName).toBe('IMG')
    expect(img.getAttribute('src')).toBeTruthy()
    expect(img.getAttribute('src')).toMatch(/adc-mechanism-padcev-nectin4/)
  })

  it('⚠ transcribes every panel in alt text — the only version-controlled record of the pixels', () => {
    renderIt()
    const alt = screen.getByRole('img').getAttribute('alt')
    for (const step of ['Binding', 'Internalization', 'Lysosome', 'Payload Release', 'Cell Death']) {
      expect(alt, `alt must transcribe the "${step}" panel`).toContain(step)
    }
  })

  it('⚠ names the right cancer — the transcription must not reintroduce the thyroid error', () => {
    renderIt()
    const alt = screen.getByRole('img').getAttribute('alt')
    expect(alt).toMatch(/urothelial/i)
    expect(alt).toMatch(/bladder/i)
    // ⚠⚠ THE REGRESSION, named. Two rejected versions of this asset said "thyroid"; PADCEV
    // targets NECTIN-4 in urothelial carcinoma, and AdcContext says "bladder cancer" on the
    // same screen. If a future asset swap brings the error back, the alt must not carry it.
    expect(alt).not.toMatch(/thyroid/i)
  })

  it('⚠ spells the payload correctly, where the shipped pixels do not (D-096)', () => {
    renderIt()
    const alt = screen.getByRole('img').getAttribute('alt')
    expect(alt).toContain('MMAE')
    // ⚠ DELIBERATE DIVERGENCE, recorded in D-096: the shipped image reads "cyttoxic" and
    // "conjugation". The alt says "cytotoxic" and "conjugate" — a transcription exists to convey
    // the meaning to a reader who cannot see the pixels, and propagating a typo to a screen
    // reader serves nobody. The divergence is the decision, so it is pinned here.
    expect(alt).toContain('cytotoxic')
    expect(alt).not.toContain('cyttoxic')
  })

  it('keeps the disclosure adjacent to the artwork — D-094 mount precondition', () => {
    const { container } = renderIt()
    const figure = container.querySelector('figure')
    expect(figure).not.toBeNull()
    expect(figure.querySelector('img')).not.toBeNull()
    expect(figure.querySelector('figcaption')).not.toBeNull()
    // ⚠ A glossy rendered cell reads as a depiction of real structure far more readily than a
    // line drawing did, so the caption matters MORE after D-096, not less.
    expect(figure.querySelector('figcaption').textContent).toContain('not a structure produced by this system')
  })
})
