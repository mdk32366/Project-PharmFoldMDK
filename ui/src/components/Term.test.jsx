// D-055: <Term> renders the expansion, and its definition is reachable by KEYBOARD FOCUS (not hover
// alone, orders §1c). An undefined term degrades to plain text — the contract test catches that.
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import Term from './Term.jsx'

describe('Term (D-055)', () => {
  it('renders the expansion for a known term', () => {
    const { container } = render(<Term name="pLDDT" />)
    expect(container.textContent).toContain('predicted Local Distance Difference Test')
  })

  it('exposes the definition via a focusable button, not hover alone', () => {
    render(<Term name="ESMFold" />)
    const btn = screen.getByRole('button', { name: 'ESMFold' })
    btn.focus()
    expect(document.activeElement).toBe(btn)                 // keyboard-focusable
    const descId = btn.getAttribute('aria-describedby')       // definition linked for AT on focus
    expect(descId).toBeTruthy()
    const desc = document.getElementById(descId)
    expect(desc).not.toBeNull()
    expect(desc.textContent).toContain('neural network we run ourselves')
  })

  it('renders an undefined term as plain text (the contract test is what flags it)', () => {
    const { container } = render(<Term name="ZZZ" />)
    expect(container.textContent).toBe('ZZZ')
    expect(screen.queryByRole('button')).toBeNull()
  })
})
