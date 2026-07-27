// D-055: every glossary entry is complete, and the /method glossary block renders every term.
import { render } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import Glossary from './Glossary.jsx'
import { GLOSSARY } from '../glossary.js'

describe('Glossary (D-055)', () => {
  it('every entry has a non-empty term, expansion, and plain sentence', () => {
    for (const [term, e] of Object.entries(GLOSSARY)) {
      expect(term.trim().length, `${term}: term`).toBeGreaterThan(0)
      expect((e.expansion || '').trim().length, `${term}: expansion`).toBeGreaterThan(0)
      expect((e.plain || '').trim().length, `${term}: plain`).toBeGreaterThan(0)
    }
  })

  it('renders every glossary term', () => {
    const { container } = render(<Glossary />)
    for (const term of Object.keys(GLOSSARY)) {
      expect(container.textContent).toContain(term)
    }
  })
})
