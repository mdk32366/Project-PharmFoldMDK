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
  source: 'Human Protein Atlas v22 — pathology.tsv and normal_tissue.tsv.',
  licence_statement: {
    attributive: 'The Human Protein Atlas states, on its Licence & Citation page',
    quotation: 'The Human Protein Atlas is licensed under the Creative Commons ' +
      'Attribution-ShareAlike 3.0 International License for all copyrightable parts of our ' +
      // ⚠ the source's own text ends with an unbalanced quote; reproduced exactly
      `database, specifically indicated in the downloadable XML format with 'source="HPA".`,
    url: 'https://v22.proteinatlas.org/about/licence',
    date_read: '2026-08-20',
  },
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

  // ⚠⚠ CO-EQUAL IN POSITION, UNEQUAL IN EVIDENTIAL WEIGHT — and the surface must say so.
  // HPA stains THREE individuals per normal tissue. The tumour half prints its n on every row;
  // this half printed "2 of 3 cell types", which reads as a sample size and is not one.
  it('states that the normal-tissue half rests on three individuals', () => {
    const t = text(PRESENT)
    expect(t).toMatch(/three individuals per tissue/i)
    // ⚠ and that the cell-type figure is not a patient count
    expect(t).toMatch(/not.{0,6}a patient count/i)
    // ⚠ and that the source does not document how disagreement is resolved
    expect(t).toMatch(/not\s+documented at the source/i)
  })

  it('says WHY the healthy-tissue half matters, in plain words', () => {
    expect(text(PRESENT)).toMatch(/the payload cannot tell the two apart/i)
  })

  // ⚠⚠ ruling 1 — the slot renders, never omitted. And the copy is the COMPONENT's, because
  // D-093 decision 1 bars a burden field on a protein payload: the fixture carries none.
  it('renders the burden slot with its refusal, on a covered protein', () => {
    const t = text(PRESENT)
    expect(t).toMatch(/How common, how deadly/)
    // ⚠⚠ WAS /no licensed source/i — THE COPY THE OWNER RULED AGAINST on 2026-08-21, because it
    // gives a LICENSING reason for what `D-093` amendment 6 measured as a VOCABULARY problem. A
    // reader was being told the obstacle was permission, which obtaining a licence would not fix.
    // ⚠ Third test this week found pinning defective copy, after `App.test.jsx` and
    // `TargetList.sort.test.jsx`. A test asserting the wrong sentence defends it.
    expect(t).toMatch(/vocabulary, not permission/i)
    expect(t).toMatch(/two independent axes/i)
    expect(t).toMatch(/unattempted, not failed/i)
  })

  // ⚠⚠ The silent-join case, which is the reason the section exists at all: a string match on
  // "skin cancer" SUCCEEDS against a registry category named "Skin excluding Basal and Squamous"
  // and returns a number about a different population. `F-047`'s class, stated on the surface.
  it('names the join that would succeed and be wrong', () => {
    const t = text(PRESENT)
    expect(t).toMatch(/Skin excluding Basal and Squamous/i)
    expect(t).toMatch(/fails silently|quietly be about a different population/i)
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


  // ⚠⚠ NB4 — THREE SEPARATE ASSERTIONS, NOT ONE. Each declared property gets its own test, so a
  // regression names WHICH property was lost. KEEL-1 V9 Principle 6.
  it('quotes the page as REPORTED SPEECH, never adopting the licence', () => {
    const t = text(PRESENT)
    expect(t).toMatch(/The Human Protein Atlas states, on its Licence & Citation page/)
    // ⚠ adoption is exactly what the ruling refuses
    expect(t).not.toMatch(/this data is licensed under/i)
    expect(t).not.toMatch(/we are licensed/i)
  })

  it('renders a RESOLVABLE LINK with the quotation', () => {
    const { container } = render(<ClinicalEdges block={PRESENT} />)
    const a = container.querySelector('.clin-licence a')
    expect(a).not.toBeNull()
    expect(a.getAttribute('href')).toBe('https://v22.proteinatlas.org/about/licence')
    // ⚠ the v22 host, not www — they state DIFFERENT licences and v22 is what was ingested
    expect(a.getAttribute('href')).toMatch(/v22\./)
  })

  it('renders the DATE READ with the quotation', () => {
    expect(text(PRESENT)).toMatch(/read 2026-08-20/)
  })

  // ⚠⚠ VERBATIM, and the surface does NOT editorialise on someone else's page.
  it('quotes verbatim including "3.0 International" and does not correct it', () => {
    const t = text(PRESENT)
    expect(t).toMatch(/Attribution-ShareAlike 3\.0 International License/)
    expect(t).not.toMatch(/does not exist/i)
    expect(t).not.toMatch(/is not a licence/i)
  })

  it('renders nothing at all when the block is absent', () => {
    const { container } = render(<ClinicalEdges block={null} />)
    expect(container.textContent).toBe('')
  })
})
