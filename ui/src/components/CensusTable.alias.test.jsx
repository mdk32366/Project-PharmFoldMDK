import { describe, it, expect } from 'vitest'
import { filterRows, normalizeQuery } from './CensusTable.jsx'

// ⚠⚠ The rows the owner actually searched for. CD30 is in the census as TNFRSF8 and read as absent.
const ROWS = [
  { accession: 'P28908', gene: 'TNFRSF8', label: 'Tumor necrosis factor receptor superfamily member 8',
    aliases: ['CD30', 'D1S166E', 'Ki-1 antigen', 'Lymphocyte activation antigen CD30'] },
  { accession: 'Q13421', gene: 'MSLN', label: 'Mesothelin', aliases: ['MPF', 'CAK1 antigen'] },
  { accession: 'Q96NY8', gene: 'NECTIN4', label: 'Nectin-4', aliases: ['LNIR', 'PRR4', 'PVRL4'] },
  { accession: 'P09758', gene: 'TACSTD2', label: 'Tumor-associated calcium signal transducer 2',
    aliases: ['TROP2', 'M1S1', 'GA733-1'] },
  { accession: 'P15391', gene: 'CD19', label: 'B-lymphocyte antigen CD19', aliases: null },
  // ⚠⚠ THE ROW THAT PROVES NORMALISATION. Neither the gene, the label nor the alias contains a
  // hyphen, so a search for `PD-L1` can ONLY match by stripping punctuation. The NECTIN-4 case
  // below does NOT prove this: its label is literally "Nectin-4", so the raw substring path matches
  // and the normalisation is never exercised — a revert proof caught it passing for that reason.
  { accession: 'Q9NZQ7', gene: 'CD274', label: 'Programmed cell death 1 ligand 1',
    aliases: ['PDL1', 'B7H1', 'PDCD1LG1'] },
]

describe('census search — the names people actually type', () => {
  const genes = (q) => filterRows(ROWS, q).map((r) => r.gene)

  // ⚠⚠ the reported defect, asserted directly
  it('finds TNFRSF8 when the user searches CD30', () => {
    expect(genes('CD30')).toEqual(['TNFRSF8'])
  })

  it('finds TACSTD2 when the user searches TROP2', () => {
    expect(genes('TROP2')).toEqual(['TACSTD2'])
  })

  it('is case-insensitive on aliases', () => {
    expect(genes('cd30')).toEqual(['TNFRSF8'])
  })

  // ⚠ punctuation — and note NECTIN4 is a PRIMARY symbol, so this is not the alias path.
  // ⚠⚠ This one does NOT prove normalisation: the label is "Nectin-4", so the raw substring path
  // already matches. It is kept as a regression on the behaviour, not as evidence for the feature.
  it('finds NECTIN4 when the user types the hyphenated NECTIN-4', () => {
    expect(genes('NECTIN-4')).toEqual(['NECTIN4'])
  })

  // ⚠⚠ THIS is the normalisation proof — nothing on the row carries a hyphen.
  it('finds CD274 when the user types PD-L1, which appears nowhere on the row', () => {
    const row = ROWS.find((r) => r.gene === 'CD274')
    expect(`${row.gene} ${row.label} ${row.aliases.join(' ')}`).not.toMatch(/-/)
    expect(genes('PD-L1')).toEqual(['CD274'])
  })

  it('still matches on accession, gene and full protein name', () => {
    expect(genes('P28908')).toEqual(['TNFRSF8'])
    expect(genes('MSLN')).toEqual(['MSLN'])
    expect(genes('Mesothelin')).toEqual(['MSLN'])
  })

  it('matches a multi-word alias with its spaces intact', () => {
    expect(genes('Ki-1 antigen')).toEqual(['TNFRSF8'])
  })

  it('a row with no aliases is unaffected and still searchable', () => {
    expect(genes('CD19')).toEqual(['CD19'])
  })

  it('an empty query returns everything, not nothing', () => {
    expect(filterRows(ROWS, '').length).toBe(ROWS.length)
    expect(filterRows(ROWS, '   ').length).toBe(ROWS.length)
  })

  it('a query that names nothing still matches nothing', () => {
    expect(filterRows(ROWS, 'zzzznotaprotein')).toEqual([])
  })

  // ⚠ an alias is a way IN, never a second identity — the row keeps its own name
  it('matching an alias does not change what the row is called', () => {
    const [row] = filterRows(ROWS, 'CD30')
    expect(row.gene).toBe('TNFRSF8')
    expect(row.label).toMatch(/Tumor necrosis factor receptor/)
  })

  it('normalizeQuery strips punctuation and case only', () => {
    expect(normalizeQuery('PD-L1')).toBe('PDL1')
    expect(normalizeQuery('  her 2 ')).toBe('HER2')
    expect(normalizeQuery('---')).toBe('')
  })
})
