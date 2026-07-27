// D-051: the diagram must READ the model, not hard-code it. Proof = swapping the model changes the
// output, and no route string is typed in the JSX. Distinctive fixture paths that can't coincide
// with the real routes make the "reads the model" claim unambiguous.
import { render } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import ArchitectureDiagram from './ArchitectureDiagram.jsx'

const FIXTURE = {
  nodes: [
    { id: 'a', label: 'Alpha serving node', zone: 'fly', gpu: false },
    { id: 'b', label: 'Bravo GPU box', zone: 'external', gpu: true },
  ],
  edges: [{ from: 'b', to: 'a', label: 'pulls work' }],
  routes: {
    public_api: [{ path: '/api/zzz-distinctive', methods: ['GET'] }],
    worker_jobs: [{ path: '/jobs/qqq-distinctive', methods: ['POST'] }],
  },
}

describe('ArchitectureDiagram — rendered from the model, not hand-drawn (D-051)', () => {
  it('renders one node per model node', () => {
    const { container } = render(<ArchitectureDiagram model={FIXTURE} />)
    expect(container.textContent).toContain('Alpha serving node')
    expect(container.textContent).toContain('Bravo GPU box')
  })

  it('renders route labels FROM the model — swapping the model changes the output', () => {
    const { container, rerender } = render(<ArchitectureDiagram model={FIXTURE} />)
    expect(container.textContent).toContain('/api/zzz-distinctive')
    expect(container.textContent).toContain('/jobs/qqq-distinctive')

    const OTHER = {
      ...FIXTURE,
      routes: { public_api: [{ path: '/api/other-route', methods: ['GET'] }], worker_jobs: [] },
    }
    rerender(<ArchitectureDiagram model={OTHER} />)
    expect(container.textContent).toContain('/api/other-route')
    expect(container.textContent).not.toContain('/api/zzz-distinctive')
  })

  it('defaults to the real system-model.json (a live route renders)', () => {
    const { container } = render(<ArchitectureDiagram />)
    expect(container.textContent).toContain('/api/analyses')
    expect(container.textContent).toContain('/jobs/claim')
  })
})
