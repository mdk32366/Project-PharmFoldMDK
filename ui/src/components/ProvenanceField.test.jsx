// D-122 / D-124 — ProvenanceField. Red-capable: four envelope keys render;
// a bare string is not data. Trinity C-B bar 5.
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ProvenanceField from './ProvenanceField.jsx'

const env = (value) => ({
  value,
  source: 'fixture source',
  as_of: '2026-09-05',
  confidence: 'reviewed',
})

describe('ProvenanceField', () => {
  it('renders value + source + as_of + confidence', () => {
    const { container } = render(
      <dl><ProvenanceField label="Phase" field={env('Phase 1')} /></dl>,
    )
    expect(screen.getByText('Phase')).toBeInTheDocument()
    expect(container.textContent).toMatch(/Phase 1/)
    expect(container.textContent).toMatch(/source: fixture source/)
    expect(container.textContent).toMatch(/as of 2026-09-05/)
    expect(container.textContent).toMatch(/reviewed/)
  })

  it('refuses a bare string as data', () => {
    const { container } = render(
      <dl><ProvenanceField label="Phase" field="Phase 1" /></dl>,
    )
    expect(container.textContent).toBe('')
  })
})
