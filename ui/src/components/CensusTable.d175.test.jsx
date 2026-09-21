import { describe, it, expect } from 'vitest'
import { COLUMNS, COLUMN_TITLES } from './CensusTable.jsx'

describe('D-175 census header polish', () => {
  it('PDB header is short form PDB (exp)', () => {
    const pdb = COLUMNS.find((c) => c.key === 'pdb_best')
    expect(pdb.label).toBe('PDB (exp)')
  })

  it('every COLUMNS key has a COLUMN_TITLES entry', () => {
    for (const c of COLUMNS) {
      expect(COLUMN_TITLES[c.key], c.key).toBeTruthy()
    }
  })

  it('Status uses headerLines with scored (not score)', () => {
    const status = COLUMNS.find((c) => c.key === 'status_structure')
    expect(status.headerLines).toEqual(['Status', '(structure · scored · seam)'])
    expect(status.label).toBe('Status')
  })

  it('tooltips stay honest for Cost, Struct. score, PDB', () => {
    expect(COLUMN_TITLES.cost).toMatch(/not suitability/i)
    expect(COLUMN_TITLES.structural_score).toMatch(/STRUCTURAL_ONLY/)
    expect(COLUMN_TITLES.structural_score).toMatch(/cohort-82/)
    expect(COLUMN_TITLES.pdb_best).toMatch(/experimental/i)
    expect(COLUMN_TITLES.pdb_best).toMatch(/not the served fold/i)
  })

  it('default column order still leads with accession', () => {
    expect(COLUMNS[0].key).toBe('accession')
  })
})
