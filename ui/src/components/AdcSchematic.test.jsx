// D-052: the load-bearing test asserts the MECHANISM, not just the words — with the entire api.js
// module mocked, the schematic must invoke NONE of its exports. An absent import is what makes the
// component structurally incapable of being a model output; a label alone could be edited away.
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
