import { render } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import ClinicalEdges from './ClinicalEdges.jsx'

// Distinctive fixture numbers that cannot coincide with a live value (D-050).
const PRESENT = {
  status: 'ihc_present',
  layers: ['mapped_one_gene', 'row_present_with_data', 'ihc_available'],
  gene: 'TESTGENE',
  tumours: [
    { cancer: 'ovarian cancer', patients_tested: 13, patients_positive: 11,
      high: 3, medium: 7, low: 1, not_detected: 2 },
    { cancer: 'stomach cancer', patients_tested: 9, patients_positive: 4,
      high: 1, medium: 2, low: 1, not_detected: 5 },
  ],
  normal_tissues: [
    { tissue: 'bronchus', highest: 'High', cell_types: 3, detected_in: 2 },
    { tissue: 'colon', highest: 'Medium', cell_types: 4, detected_in: 1 },
  ],
  source: 'Human Protein Atlas v22 — pathology.tsv and normal_tissue.tsv. CC BY-SA 3.0.',
  boundary: 'Immunohistochemistry: how many patient samples stained for this protein.',
}

const ABSENT = { ...PRESENT, status: 'ihc_gene_absent', tumours: [], normal_tissues: [] }

describe('ClinicalEdges', () => {
  const text = (b) => render(<ClinicalEdges block={b} />).container.textContent

  // ⚠⚠ the point of the whole layer: a sentence a person can read
  it('states patient COUNTS, not a score', () => {
    const t = text(PRESENT)
    expect(t).toMatch(/11/)
    expect(t).toMatch(/13/)
    expect(t).toMatch(/samples stained/)
    // a bare percentage would hide whether it is 11-of-13 or 110-of-130
    expect(t).not.toMatch(/\b8[45]%/)
  })

  // ⚠ D-093 decision 5 / amendment 2 ruling 2 — co-equal, same section, never hidden
  it('renders the normal-tissue half in the SAME section as the tumour half', () => {
    const { container } = render(<ClinicalEdges block={PRESENT} />)
    const section = container.querySelector('section.clin')
    const t = section.textContent
    expect(t).toMatch(/Where it appears in tumours/)
    expect(t).toMatch(/Where it also appears in healthy tissue/)
    expect(t).toMatch(/bronchus/)
    // ⚠ and it must not be behind a fold — no <details> in this component
    expect(section.querySelector('details')).toBeNull()
  })

  it('says WHY the healthy-tissue half matters, in plain words', () => {
    expect(text(PRESENT)).toMatch(/the payload cannot tell the two apart/i)
  })

  // ⚠⚠ ruling 1 — the slot renders, never omitted. And the copy is the COMPONENT's, because
  // D-093 decision 1 bars a burden field on a protein payload: the fixture carries none.
  it('renders the burden slot with its refusal, on a covered protein', () => {
    const t = text(PRESENT)
    expect(t).toMatch(/How common, how deadly/)
    expect(t).toMatch(/no licensed source/i)
    expect(t).toMatch(/unattempted, not failed/i)
  })

  it('renders the burden slot even when the protein is NOT covered', () => {
    const t = text(ABSENT)
    expect(t).toMatch(/How common, how deadly/)
    expect(t).toMatch(/unattempted, not failed/i)
  })

  // ⚠ an absent gene is a category, not an empty panel
  it('distinguishes "nobody looked" from "looked and found nothing"', () => {
    const t = text(ABSENT)
    expect(t).toMatch(/Not covered by the antibody atlas/)
    expect(t).toMatch(/nobody looked/i)
    expect(t).not.toMatch(/no association|found none/i)
  })

  it('an empty tumour panel reads as empty, not absent', () => {
    const t = text({ ...PRESENT, tumours: [] })
    expect(t).toMatch(/an empty panel, not an absent one/i)
  })

  // ⚠⚠ ruling 4 — the two edges are not commensurable; nothing divides them
  it('computes no ratio and shows no combined figure', () => {
    const t = text(PRESENT)
    expect(t).not.toMatch(/ratio/i)
    expect(t).not.toMatch(/tumour[^.]*÷|\/\s*normal/i)
    expect(t).not.toMatch(/\bscore\b/i)
  })

  // ⚠⚠ it must not be mistakable for the D-053 expression grid it sits beside
  it('never borrows the expression grid\'s language', () => {
    const t = text(PRESENT)
    expect(t).not.toMatch(/quasi H-score/i)
    expect(t).not.toMatch(/Highly expressed in these tumour types/i)
    expect(t).toMatch(/Immunohistochemistry/i)
  })

  it('renders nothing at all when the block is absent', () => {
    const { container } = render(<ClinicalEdges block={null} />)
    expect(container.textContent).toBe('')
  })
})
