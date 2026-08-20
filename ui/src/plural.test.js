import { describe, it, expect } from 'vitest'
import { plural, count, ofCount } from './plural.js'

// ⚠⚠ "1 of 1 cell types" rendered TWENTY-SIX TIMES on the LAMP1 card — 26 of its 49 normal-tissue
// rows. The noun was hard-coded plural and the singular case was never considered.
describe('agreement between a count and its noun', () => {
  it('is singular at one', () => {
    expect(ofCount(1, 1, 'cell type')).toBe('1 of 1 cell type')
    expect(count(1, 'target')).toBe('1 target')
    expect(plural(1, 'sample')).toBe('sample')
  })

  it('is plural at everything else, including zero', () => {
    // ⚠ zero takes the plural in English — "0 cell types", not "0 cell type"
    expect(ofCount(0, 0, 'cell type')).toBe('0 of 0 cell types')
    expect(ofCount(11, 13, 'cell type')).toBe('11 of 13 cell types')
    expect(count(3, 'target')).toBe('3 targets')
  })

  // ⚠⚠ THE NOUN AGREES WITH THE TOTAL, NOT THE NUMERATOR. "1 of 3 cell type" is the same defect
  // mirrored, and it is the one an obvious fix produces.
  it('agrees with the total in an "a of b" phrase', () => {
    expect(ofCount(1, 3, 'cell type')).toBe('1 of 3 cell types')
    expect(ofCount(3, 1, 'cell type')).toBe('3 of 1 cell type')
  })

  it('never invents an irregular plural', () => {
    // ⚠ the caller supplies it; this appends "s" and nothing cleverer
    expect(plural(2, 'analysis', 'analyses')).toBe('analyses')
    expect(plural(1, 'analysis', 'analyses')).toBe('analysis')
  })

  it('treats a numeric string the same as a number', () => {
    expect(ofCount('1', '1', 'cell type')).toBe('1 of 1 cell type')
  })
})
