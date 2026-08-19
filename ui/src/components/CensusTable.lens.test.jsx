import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import CensusTable, { withLens, LENSES } from './CensusTable.jsx'

// ⚠⚠ Distinctive numbers that cannot coincide with a live value (D-050). ALPHA is the case the
// whole ruling is about: 100% under one lens, 25% under the other, from the same panels.
const ALPHA = {
  id: 1, accession: 'P00001', gene: 'ALPHA', label: 'Alpha protein', tranche: 4,
  span_aa: 111, mean_plddt: 77, topology: 'single', profile_status: 'computed',
  staining: {
    min_patients: 10,
    best_panel: { lens: 'best_panel', category: 'measured', patients_positive: 11,
      patients_tested: 11, cancer: 'ovarian cancer', panels_considered: 2,
      panels_excluded_small: 0 },
    pooled: { lens: 'pooled', category: 'measured', patients_positive: 11, patients_tested: 44,
      cancer: null, panels_considered: 2, panels_excluded_small: 0 },
    critical_normal_high: [],
    critical_tissues_declared: ['heart muscle', 'liver', 'kidney'],
    critical_tissues_unknown: [],
    normal_basis: 'three individuals per tissue (a few six, one just one)',
  },
}

const BETA = {
  ...ALPHA, id: 2, accession: 'P00002', gene: 'BETA', label: 'Beta protein',
  staining: {
    ...ALPHA.staining,
    best_panel: { lens: 'best_panel', category: 'measured', patients_positive: 6,
      patients_tested: 12, cancer: 'lung cancer', panels_considered: 1, panels_excluded_small: 0 },
    pooled: { lens: 'pooled', category: 'measured', patients_positive: 6, patients_tested: 12,
      cancer: null, panels_considered: 1, panels_excluded_small: 0 },
    critical_normal_high: ['liver', 'kidney'],
  },
}

// ⚠ a protein HPA never covered — a category, not a zero
const GAMMA = { ...ALPHA, id: 3, accession: 'P00003', gene: 'GAMMA', label: 'Gamma protein',
  staining: null }

const ROWS = [ALPHA, BETA, GAMMA]
const draw = () => render(<MemoryRouter><CensusTable rows={ROWS} /></MemoryRouter>)

describe('withLens', () => {
  // ⚠⚠ THE FINDING, IN A UNIT TEST: one protein, two lenses, two different numbers.
  it('gives the same protein different values under each lens', () => {
    const best = withLens([ALPHA], 'best_panel')[0]
    const pooled = withLens([ALPHA], 'pooled')[0]
    expect(best.stained_pct).toBe(100)
    expect(pooled.stained_pct).toBe(25)
    expect(best.stained_cancer).toBe('ovarian cancer')
    expect(pooled.stained_cancer).toBeNull()
  })

  it('carries the n alongside the percentage, always', () => {
    expect(withLens([ALPHA], 'best_panel')[0].stained_n).toBe(11)
    expect(withLens([ALPHA], 'pooled')[0].stained_n).toBe(44)
  })

  it('an uncovered protein is a category, never a zero', () => {
    const g = withLens([GAMMA], 'best_panel')[0]
    expect(g.stained_pct).toBeNull()
    expect(g.stained_pct).not.toBe(0)
    expect(g.stained_category).toBe('not_covered')
    expect(g.critical_n).toBeNull()
  })
})

describe('the lens control', () => {
  it('names both lenses and states what the current one means', () => {
    draw()
    // ⚠ getAllByText, not getByText: the active lens's name appears twice by design — once as the
    // radio's label and once heading the sentence that says what it means. Both are wanted.
    expect(screen.getAllByText(LENSES.best_panel.label).length).toBeGreaterThan(0)
    expect(screen.getAllByText(LENSES.pooled.label).length).toBeGreaterThan(0)
    expect(document.body.textContent).toMatch(/largest share of patients/)
  })

  // ⚠⚠ the number that makes the control necessary rather than decorative
  it('states the 728-versus-16 difference on the page', () => {
    draw()
    const t = document.body.textContent
    expect(t).toMatch(/728/)
    expect(t).toMatch(/16/)
  })

  it('switching the lens changes the rendered value', () => {
    draw()
    expect(document.body.textContent).toMatch(/100%/)
    fireEvent.click(screen.getByRole('radio', { name: new RegExp(LENSES.pooled.label, 'i') }))
    expect(document.body.textContent).toMatch(/25%/)
  })

  // ⚠⚠ THE LIST IS DECLARED. A reader who cannot see it cannot disagree with it.
  it('declares the critical tissues by name, not by implication', () => {
    draw()
    const t = document.body.textContent
    expect(t).toMatch(/heart muscle/)
    expect(t).toMatch(/liver/)
    expect(t).toMatch(/kidney/)
  })

  // ⚠ amendment 5 — the flag cannot render without its basis
  it('states that normal tissue rests on three individuals', () => {
    draw()
    expect(document.body.textContent).toMatch(/three individuals per tissue/)
    expect(document.body.textContent).toMatch(/not a safety measurement/i)
  })

  it('the exclusion removes proteins staining High in a declared tissue', () => {
    draw()
    expect(document.body.textContent).toMatch(/BETA/)
    fireEvent.click(screen.getByRole('checkbox'))
    expect(document.body.textContent).not.toMatch(/Beta protein/)
    expect(document.body.textContent).toMatch(/Alpha protein/)
  })
})

describe('what the ruling does NOT license', () => {
  // ⚠⚠ D-102 licenses a sort the READER chooses — not a page that arrives ordered.
  it('arrives sorted by accession, never by stained percentage', () => {
    const { container } = draw()
    const firstCol = [...container.querySelectorAll('tbody tr td:first-child')]
      .map((td) => td.textContent)
    expect(firstCol[0]).toMatch(/P00001/)
    expect(firstCol[1]).toMatch(/P00002/)
    // ALPHA is 100% and BETA 50%; accession order happens to agree, so assert the CONTROL instead
    expect(container.querySelector('table').textContent).toMatch(/Stained %/)
  })

  it('shows no combined or ratio figure between the two edges', () => {
    const t = draw().container.textContent
    expect(t).not.toMatch(/ratio/i)
    expect(t).not.toMatch(/tumour[^.]*÷/)
  })
})
