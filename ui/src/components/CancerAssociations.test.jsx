// D-053: all associations render, ranked, no truncation; the claim boundary and derivation-gap
// note are on screen; per-target/derived counts come ONLY from the payload (distinctive fixture
// values 9/4/5 so the live 337/82 cannot leak in); the absent case renders, never a blank/crash.
import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../api.js', () => ({ getAssociations: vi.fn() }))
import { getAssociations } from '../api.js'
import CancerAssociations from './CancerAssociations.jsx'

// distinctive derived counts (9/4/5) that cannot coincide with the live 337/82
const BASE = { source: 'Kathad S3 (fixture)', method: 'qh', cutoff: 150,
               pair_count: 9, targets_covered: 4, cohort_size: 5, unmatched_symbols: [] }
const payload = (associations) => ({ ...BASE, associations })
const renderFor = (symbol) => render(<CancerAssociations symbol={symbol} />)
beforeEach(() => vi.clearAllMocks())

describe('CancerAssociations (D-053)', () => {
  it('renders all three associations in descending score order', async () => {
    getAssociations.mockResolvedValue(payload({
      AAA: [
        { cancer: 'Alpha', qh_score: 290 },
        { cancer: 'Beta', qh_score: 200 },
        { cancer: 'Gamma', qh_score: 120 },
      ],
    }))
    renderFor('AAA')
    await waitFor(() => expect(screen.getByText('Alpha')).toBeInTheDocument())
    const items = screen.getAllByRole('listitem').map((li) => li.textContent)
    expect(items).toHaveLength(3)
    expect(items[0]).toContain('Alpha')
    expect(items[1]).toContain('Beta')
    expect(items[2]).toContain('Gamma')
  })

  it('renders all sixteen for a 16-association target — no truncation', async () => {
    const many = Array.from({ length: 16 }, (_, i) => ({ cancer: `C${i}`, qh_score: 300 - i }))
    getAssociations.mockResolvedValue(payload({ BTN3A3: many }))
    renderFor('BTN3A3')
    await waitFor(() => expect(screen.getByText('C0')).toBeInTheDocument())
    expect(screen.getAllByRole('listitem')).toHaveLength(16)
  })

  it('reads correctly for a single-association target', async () => {
    getAssociations.mockResolvedValue(payload({ SOLO: [{ cancer: 'Lung', qh_score: 210 }] }))
    renderFor('SOLO')
    await waitFor(() => expect(screen.getByText('Lung')).toBeInTheDocument())
    expect(screen.getAllByRole('listitem')).toHaveLength(1)
  })

  it('renders the expression claim boundary', async () => {
    getAssociations.mockResolvedValue(payload({ AAA: [{ cancer: 'Lung', qh_score: 200 }] }))
    const { container } = renderFor('AAA')
    await waitFor(() => expect(screen.getByText('Lung')).toBeInTheDocument())
    expect(container.textContent).toContain('expression')
    expect(container.textContent).toContain('not')
    expect(container.textContent.toLowerCase()).toContain('causation')
  })

  it('renders the derivation-gap note with derived counts from the payload, not live literals', async () => {
    const { container } = (getAssociations.mockResolvedValue(
      payload({ AAA: [{ cancer: 'Lung', qh_score: 200 }] })), renderFor('AAA'))
    await waitFor(() => expect(screen.getByText('Lung')).toBeInTheDocument())
    // the paper's 290/16 are literals (allowed, dec 5)
    expect(container.textContent).toContain('290')
    expect(container.textContent).toContain('16')
    // our statistics derive from the payload — the live 337/82 must not be hardcoded
    expect(container.textContent).toContain('9 pairs across 4 of 5 targets')
    expect(container.textContent).not.toContain('337')
    expect(container.textContent).not.toContain('82')
  })

  it('renders "no association recorded" for a target missing from the map — not a blank', async () => {
    getAssociations.mockResolvedValue(payload({ AAA: [{ cancer: 'Lung', qh_score: 200 }] }))
    const { container } = renderFor('NOTINMAP')
    await waitFor(() => expect(container.textContent).toContain('No association recorded'))
    expect(screen.queryAllByRole('listitem')).toHaveLength(0)
  })
})
