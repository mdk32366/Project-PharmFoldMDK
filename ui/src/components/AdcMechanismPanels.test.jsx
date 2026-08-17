// D-097 / D-052: the cartoon is the PROCESS half of the ADC explanation, and like the schematic it
// must be structurally incapable of reading as a model output. With api.js entirely mocked it must
// invoke none of its exports — an absent import is the enforcement; a caption could be edited away.
//
// ⚠⚠ These tests exist because NOTHING ELSE CAN READ THIS GRAPHIC. Its words are pixels (D-096), so
// the over-claim denylist tests are blind to it. The `alt` transcription is the only
// version-controlled record of what the artwork claims, and pinning it here is what stops a future
// asset swap from silently changing the claim on an educational surface.
import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'

const spies = {
  listAnalyses: vi.fn(),
  getCoverage: vi.fn(),
  getAnalysis: vi.fn(),
  getPlddt: vi.fn(),
  structureUrl: vi.fn(),
}
vi.mock('../api.js', () => spies)

import AdcMechanismPanels from './AdcMechanismPanels.jsx'

const renderIt = () => render(<AdcMechanismPanels />)

describe('AdcMechanismPanels — the process half, structurally not a model output (D-097)', () => {
  it('invokes NO api.js export — it cannot be a model output', () => {
    renderIt()
    for (const [name, spy] of Object.entries(spies)) {
      expect(spy, `AdcMechanismPanels must not call api.${name}`).not.toHaveBeenCalled()
    }
  })

  it('renders the imported illustration with a resolved src', () => {
    renderIt()
    const img = screen.getByRole('img')
    expect(img.tagName).toBe('IMG')
    expect(img.getAttribute('src')).toMatch(/adc-mechanism-padcev-nectin4/)
  })

  it('⚠ transcribes every panel in alt — the only version-controlled record of the pixels', () => {
    const alt = (renderIt(), screen.getByRole('img').getAttribute('alt'))
    for (const step of ['Binding', 'Internalization', 'Lysosome', 'Payload Release', 'Cell Death']) {
      expect(alt, `alt must transcribe the "${step}" panel`).toContain(step)
    }
  })

  it('⚠ names the right cancer — the transcription must not reintroduce the thyroid error', () => {
    const alt = (renderIt(), screen.getByRole('img').getAttribute('alt'))
    expect(alt).toMatch(/urothelial/i)
    expect(alt).toMatch(/bladder/i)
    // ⚠⚠ THE REGRESSION, named. Two rejected versions of this asset said "thyroid"; PADCEV targets
    // NECTIN-4 in urothelial carcinoma, and AdcContext says "bladder cancer" on the same screen.
    expect(alt).not.toMatch(/thyroid/i)
  })

  it('⚠ spells the payload correctly, where the shipped pixels do not (D-096)', () => {
    const alt = (renderIt(), screen.getByRole('img').getAttribute('alt'))
    expect(alt).toContain('MMAE')
    expect(alt).toContain('cytotoxic')
    expect(alt).not.toContain('cyttoxic')
  })

  it('⚠ reserves its aspect-ratio box so lazy loading cannot collapse the figure', () => {
    renderIt()
    const img = screen.getByRole('img')
    // ⚠ Found on the DEPLOYED site, not locally: without intrinsic dimensions the browser cannot
    // reserve space, `loading="lazy"` leaves a 0-height line, and the caption jumps up under the
    // heading until the 707 KB fetch resolves. A fast dev server hides this entirely.
    expect(img.getAttribute('width'), 'intrinsic width must be declared').toBe('2128')
    expect(img.getAttribute('height'), 'intrinsic height must be declared').toBe('912')
    expect(img.getAttribute('loading')).toBe('lazy')
  })

  it('carries its OWN disclosure — D-094, not inherited from the schematic', () => {
    const { container } = renderIt()
    const figure = container.querySelector('figure')
    expect(figure).not.toBeNull()
    expect(figure.querySelector('img')).not.toBeNull()
    const caption = figure.querySelector('figcaption')
    expect(caption).not.toBeNull()
    expect(caption.textContent).toContain('not a structure produced by this system')
    // ⚠ A glossy rendered cell reads as a depiction of real structure far more readily than a line
    // drawing does, so this caption must also disown the SCALE, not merely the provenance.
    expect(caption.textContent).toMatch(/no real scale/i)
  })
})
