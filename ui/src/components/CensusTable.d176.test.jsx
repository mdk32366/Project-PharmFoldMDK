import { describe, it, expect } from 'vitest'
import { COLUMNS, COLUMN_TITLES } from './CensusTable.jsx'

const CRITICAL_TISSUES = [
  'heart muscle',
  'liver',
  'kidney',
  'lung',
  'cerebral cortex',
  'bone marrow',
]

describe('D-176 critical_n header tooltip', () => {
  it('keeps short Critical tissue label', () => {
    const col = COLUMNS.find((c) => c.key === 'critical_n')
    expect(col.label).toBe('Critical tissue')
  })

  it('tooltip names all six CRITICAL_TISSUES exact strings', () => {
    const tip = COLUMN_TITLES.critical_n
    for (const t of CRITICAL_TISSUES) {
      expect(tip, t).toContain(t)
    }
  })

  it('tooltip states Only High counts', () => {
    expect(COLUMN_TITLES.critical_n).toMatch(/Only High counts/i)
  })

  it('tooltip states lens/filter not a tumour÷normal ratio (D-093 honesty)', () => {
    const tip = COLUMN_TITLES.critical_n
    expect(tip).toMatch(/not a tumour÷normal ratio/i)
    expect(tip).toMatch(/lens/i)
    expect(tip).toMatch(/D-093/)
  })

  it('does not leave the thin Critical tissue count tip', () => {
    expect(COLUMN_TITLES.critical_n).not.toBe('Critical tissue count')
  })
})
