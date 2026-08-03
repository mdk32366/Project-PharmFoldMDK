// The absent-value rule, unit-tested without rendering — because it is the part of sortability that
// the project's honesty depends on, and it must be provable in isolation before it is wired to a table.
//
// The rule exists against a LIVE defect, not a hypothetical: IGF2R sits on the deployed list with
// `mean_plddt: null` (fold failed, CUDA OOM at 2,491 aa; no pdb_path, so the null is honest). The old
// `?? 0` coercion sorted it as the worst-scoring target — "no measurement" rendered as "the worst
// measurement". These tests fail against any implementation that coerces absence to a number.
import { describe, it, expect } from 'vitest'
import { isAbsent, nextSort, sortRows } from './sortRows.js'

const ROWS = [
  { gene: 'NECTIN4', mean_plddt: 77.26 },
  { gene: 'IGF2R', mean_plddt: null },      // the real absent row
  { gene: 'PTPRZ1', mean_plddt: 30.68 },
  { gene: 'SDK1', mean_plddt: 58.01 },
]

const genes = (rows) => rows.map((r) => r.gene)

describe('isAbsent — absence is null/undefined/NaN, and NOTHING else', () => {
  it('treats null, undefined and NaN as absent', () => {
    expect(isAbsent(null)).toBe(true)
    expect(isAbsent(undefined)).toBe(true)
    expect(isAbsent(NaN)).toBe(true)
  })

  it('⚠ does NOT treat 0 or empty string as absent — a real zero is a measurement', () => {
    // This is the inverse of the `?? 0` bug: conflating "measured zero" with "not measured" in
    // either direction destroys the distinction the rule exists to protect.
    expect(isAbsent(0)).toBe(false)
    expect(isAbsent('')).toBe(false)
    expect(isAbsent(false)).toBe(false)
  })
})

describe('sortRows — absent values are a trailing category in BOTH directions', () => {
  it('sorts ascending with the absent row last, not first', () => {
    expect(genes(sortRows(ROWS, 'mean_plddt', 'asc'))).toEqual(['PTPRZ1', 'SDK1', 'NECTIN4', 'IGF2R'])
  })

  it('sorts descending with the absent row STILL last — absence is not the maximum either', () => {
    // A naive implementation that sorts absent-as-0 would put IGF2R last ascending but FIRST
    // descending once the comparator flips. Absence is off the axis, not at an end of it.
    expect(genes(sortRows(ROWS, 'mean_plddt', 'desc'))).toEqual(['NECTIN4', 'SDK1', 'PTPRZ1', 'IGF2R'])
  })

  it('⚠ never places the absent row as if it were the lowest measured value', () => {
    // The precise failure of `?? 0`: IGF2R would land immediately below PTPRZ1 (30.68) as a 0.
    const asc = genes(sortRows(ROWS, 'mean_plddt', 'asc'))
    expect(asc.indexOf('IGF2R')).toBeGreaterThan(asc.indexOf('PTPRZ1'))
    expect(asc[0]).not.toBe('IGF2R')
  })

  it('never drops a row for lacking the active sort key', () => {
    // The coverage discipline (every target present with its reason) must survive sorting.
    for (const dir of ['asc', 'desc']) {
      expect(sortRows(ROWS, 'mean_plddt', dir)).toHaveLength(ROWS.length)
      expect(genes(sortRows(ROWS, 'mean_plddt', dir))).toContain('IGF2R')
    }
  })

  it('holds the rule when EVERY value is absent', () => {
    const allNull = [{ gene: 'A', mean_plddt: null }, { gene: 'B', mean_plddt: null }]
    expect(genes(sortRows(allNull, 'mean_plddt', 'desc'))).toEqual(['A', 'B'])
  })

  it('distinguishes a measured 0 from an absent value', () => {
    const withZero = [...ROWS, { gene: 'ZERO', mean_plddt: 0 }]
    const asc = genes(sortRows(withZero, 'mean_plddt', 'asc'))
    expect(asc[0]).toBe('ZERO')                       // a real 0 IS the lowest measurement
    expect(asc[asc.length - 1]).toBe('IGF2R')         // absence still trails
  })
})

describe('sortRows — the other columns', () => {
  it('sorts strings alphabetically, case-insensitively', () => {
    const rows = [{ gene: 'zeta' }, { gene: 'Alpha' }, { gene: 'mid' }]
    expect(genes(sortRows(rows, 'gene', 'asc'))).toEqual(['Alpha', 'mid', 'zeta'])
    expect(genes(sortRows(rows, 'gene', 'desc'))).toEqual(['zeta', 'mid', 'Alpha'])
  })

  it('does not mutate the input array', () => {
    const original = [...ROWS]
    sortRows(ROWS, 'mean_plddt', 'desc')
    expect(ROWS).toEqual(original)
  })

  it('returns the list unchanged when no key is given', () => {
    expect(genes(sortRows(ROWS, null))).toEqual(genes(ROWS))
  })
})

describe('nextSort — the three-state header cycle', () => {
  it('a new column starts ascending', () => {
    expect(nextSort(null, 'gene')).toEqual({ key: 'gene', dir: 'asc' })
    expect(nextSort({ key: 'mean_plddt', dir: 'desc' }, 'gene')).toEqual({ key: 'gene', dir: 'asc' })
  })

  it('the active column goes asc → desc → default (null)', () => {
    expect(nextSort({ key: 'gene', dir: 'asc' }, 'gene')).toEqual({ key: 'gene', dir: 'desc' })
    expect(nextSort({ key: 'gene', dir: 'desc' }, 'gene')).toBeNull()
  })
})
