// D-142 — the association-cell reduction, tested away from the DOM (the `sortRows.js` precedent).
//
// ⚠ The values here are the SHAPES that exist in the live map, named where they come from:
// `NECTIN4` has 2 pairs led by Urothelial cancer at 200; `BTN3A3` has 16 led by Melanoma at 250;
// `CADM1` has exactly 1; and three targets tie at their leading score (`JAG1` three ways, `CD53`
// and `INSR` two each). All measured with `core.cancer_associations.load_associations()`.
import { describe, it, expect } from 'vitest'
import { summariseAssociations } from './associationSummary.js'

const NECTIN4 = [
  { cancer: 'Urothelial cancer', qh_score: 200 },
  { cancer: 'Thyroid cancer', qh_score: 150 },
]

describe('the leading tumour type(s), and the total that stops it being a truncation', () => {
  it('names the single highest and counts every pair the map holds', () => {
    const s = summariseAssociations(NECTIN4)
    expect(s.top).toEqual(['Urothelial cancer'])
    expect(s.topScore).toBe(200)
    expect(s.total).toBe(2)
    expect(s.ordered).toBe(true)
  })

  it('counts all sixteen for a BTN3A3-shaped target while showing one', async () => {
    // ⚠⚠ THE PROPERTY THE CELL DEPENDS ON. Showing 1 of 16 without saying 16 is a silent filter
    // wearing a value; the count is the whole difference between a summary and a truncation.
    const many = [{ cancer: 'Melanoma', qh_score: 250 },
      ...Array.from({ length: 15 }, (_, i) => ({ cancer: `C${i}`, qh_score: 240 - i }))]
    const s = summariseAssociations(many)
    expect(s.total).toBe(16)
    expect(s.top).toEqual(['Melanoma'])
  })

  it('reads correctly for a single-pair target', () => {
    const s = summariseAssociations([{ cancer: 'Colorectal cancer', qh_score: 180 }])
    expect(s).toEqual({ total: 1, top: ['Colorectal cancer'], topScore: 180, ordered: true })
  })
})

describe('⚠⚠ a tie has no single top, so every tied type renders', () => {
  it('returns all three of a JAG1-shaped tie', () => {
    // Picking whichever the CSV happened to list first would be an arbitrary choice presented as
    // a measurement. Three of the 82 live targets are in this state.
    const s = summariseAssociations([
      { cancer: 'Carcinoid', qh_score: 250 },
      { cancer: 'Stomach cancer', qh_score: 250 },
      { cancer: 'Thyroid cancer', qh_score: 250 },
      { cancer: 'Liver cancer', qh_score: 180 },
    ])
    expect(s.top).toEqual(['Carcinoid', 'Stomach cancer', 'Thyroid cancer'])
    expect(s.topScore).toBe(250)
    expect(s.total).toBe(4)
  })

  it('takes only the LEADING run, not every row that happens to equal the top score', () => {
    // ⚠ A repeat of the leading score further down the list is not part of the top group; if the
    // payload is in order it cannot happen, and if it is not, `ordered` is what reports that.
    const s = summariseAssociations([
      { cancer: 'A', qh_score: 200 },
      { cancer: 'B', qh_score: 180 },
      { cancer: 'C', qh_score: 200 },
    ])
    expect(s.top).toEqual(['A'])
  })
})

describe('⚠⚠ the contracted order is CHECKED, never assumed', () => {
  it('names no top when a later pair outscores the first', () => {
    // The supplier sorts descending in the data contract (D-053). If a payload arrives otherwise,
    // captioning row 0 as "the highest" would be a false superlative — worse than an admitted
    // unknown, and the sort of thing that would otherwise be discovered on screen.
    const s = summariseAssociations([
      { cancer: 'Low', qh_score: 160 },
      { cancer: 'High', qh_score: 300 },
    ])
    expect(s.ordered).toBe(false)
    expect(s.top).toEqual([])
    expect(s.topScore).toBeNull()
    expect(s.total).toBe(2)      // ⚠ the count survives: the pairs are still known
  })
})

describe('absence is a category, and nothing here throws', () => {
  it.each([[undefined], [null], [[]], ['not a list'], [{}]])(
    'treats %p as no association rather than an error', (input) => {
      expect(summariseAssociations(input)).toEqual(
        { total: 0, top: [], topScore: null, ordered: true },
      )
    })

  it('drops a row with no cancer name rather than rendering a blank type', () => {
    const s = summariseAssociations([{ cancer: '', qh_score: 300 },
      { cancer: 'Breast cancer', qh_score: 200 }])
    expect(s.total).toBe(1)
    expect(s.top).toEqual(['Breast cancer'])
  })

  it('a non-numeric score does not drag the cell into the unknown branch', () => {
    // ⚠ `!(s > lead)` rather than `s <= lead`: NaN fails both comparisons, so it must not read as
    // "out of order". It simply is not named top.
    const s = summariseAssociations([{ cancer: 'Named', qh_score: 210 },
      { cancer: 'Broken', qh_score: 'oops' }])
    expect(s.ordered).toBe(true)
    expect(s.top).toEqual(['Named'])
    expect(s.total).toBe(2)
  })
})
