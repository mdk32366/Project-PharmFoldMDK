import { describe, it, expect } from 'vitest'
import { COLUMNS } from './CensusTable.jsx'

describe('D-173 census score headers', () => {
  it('Status header uses scored axis name, not score-as-number', () => {
    const status = COLUMNS.find((c) => c.key === 'status_structure')
    expect(status.headerLines.join(' ')).toContain('scored')
    expect(status.headerLines.join(' ')).not.toMatch(/\bscore\b/)
    expect(status.headerLines[0]).toBe('Status')
    expect(status.headerLines[1]).toBe('(structure · scored · seam)')
  })

  it('Struct. score / rank headers are short; sort keys unchanged', () => {
    const score = COLUMNS.find((c) => c.key === 'structural_score')
    const rank = COLUMNS.find((c) => c.key === 'structural_rank')
    expect(score.label).toBe('Struct. score')
    expect(rank.label).toBe('Struct. rank')
    expect(score.numeric).toBe(true)
    expect(rank.numeric).toBe(true)
  })

  it('Cost header keeps compute-not-suitability honesty', () => {
    const cost = COLUMNS.find((c) => c.key === 'cost')
    expect(cost.label).toMatch(/Cost to fold \(compute/)
    expect(cost.label).toMatch(/not suitability/)
  })

  it('default column order still leads with accession', () => {
    expect(COLUMNS[0].key).toBe('accession')
  })
})
