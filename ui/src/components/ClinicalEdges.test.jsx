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
    // ⚠⚠ THE CLAIM HAS MOVED TWICE AND BOTH PREVIOUS VERSIONS WERE FALSE — IN OPPOSITE
    // DIRECTIONS. (1) "the tumour names cannot be matched up" generalised FOUR measured failures
    // of TWENTY into a total impossibility (owner ruling, WA). (2) ⚠⚠ **D-149: "we do not have
    // that data" became false the moment the SEER artefact landed.** US incidence and deaths ARE
    // held (`data/burden/seer_us_cancer_burden.v1.csv`) and ARE served on `/cancer-burden`; what is
    // missing is the JOIN from this atlas's tumour names to a registry category.
    // ⚠⚠ THIS TEST PINNED THE FALSE SENTENCE AND WOULD HAVE DEFENDED IT — the fourth time a
    // test in this repository has been caught doing that, after `App.test.jsx`,
    // `TargetList.sort.test.jsx` and this file's own `/no licensed source/` assertion. So the
    // assertion is REPLACED, and what it pins now is the distinction that matters: *not shown
    // here* is true; *we do not have it* is not.
    expect(t).toMatch(/not shown for this protein/i)
    expect(t).toMatch(/what is missing here is the join/i)
    expect(t).toMatch(/some tumour names/i)
    // ⚠⚠ THE FALSE CLAIM IS BARRED, NOT MERELY UNASSERTED. An unasserted string comes back in
    // the next copy edit and nothing reddens.
    expect(t).not.toMatch(/we do not have that data/i)
    // ⚠ and the stale progress claim goes with it: `D-093` amendment 6 MEASURED the failures, so
    // "how many is being measured" describes a measurement that already happened.
    expect(t).not.toMatch(/how many is being measured/i)
    // ⚠ still no total-impossibility claim
    expect(t).not.toMatch(/cannot be matched up/i)
    // ⚠⚠ THE BAR THAT USED TO SIT HERE ASSERTED NOTHING, AND IT IS RECORDED RATHER THAN QUIETLY
    // DROPPED. It read `not.toMatch(/<BS>(four|4|sixteen|16) of (twenty|20)<BS>/i)` with a LITERAL
    // BACKSPACE byte (0x08) where `\b` was intended — a pattern that cannot match ordinary text, so
    // the guard passed for the wrong reason on every run since it was written. That is precisely
    // the vacuity this repository's own `test_clinical_layer_prohibitions.py` docstring names of
    // itself. It is deleted rather than repaired because the count it barred is now measured and
    // the card no longer prints one; the sibling instance at `CensusView.test.jsx:228` WAS
    // repaired to a real `\b` and stays green.
  })

  // ⚠⚠ D-149 — THE LINK IS A POINTER, NEVER AN ATTACHED FIGURE. `D-093` decision 1 bars a
  // protein-level burden field, so this card must gain a ROUTE and not a NUMBER. A card printing an
  // incidence figure beside a protein would be asserting that a disease statistic is a property of
  // that protein, which is the exact claim the decision refuses.
  it('links to the burden surface WITHOUT putting any figure on the protein card', () => {
    const { container } = render(<ClinicalEdges block={PRESENT} />)
    const burden = container.querySelector('.clin-burden')
    const link = burden.querySelector('a[href="/cancer-burden"]')
    expect(link).not.toBeNull()
    expect(link.textContent).toMatch(/Cancer burden/i)
    // ⚠ no rate, no count, no per-100,000 figure anywhere in the slot
    expect(burden.textContent).not.toMatch(/per 100,000|\/100k/i)
    expect(burden.textContent).not.toMatch(/\d{1,3}(,\d{3})+/)   // no 662,721-shaped count
    expect(burden.textContent).not.toMatch(/\d+\.\d+/)          // no rate-shaped decimal
    // ⚠ survival is refused OUTRIGHT rather than linked: `/cancer-burden` holds deaths and
    // incidence and no survival statistic at all, so pointing there for survival would be a
    // pointer to something that is not there — D-062's shape, one layer down.
    expect(burden.textContent).toMatch(/survival is not held at all/i)
  })

  // ⚠⚠ THE SILENT-JOIN EXPLANATION HAS LEFT THE CARD, DELIBERATELY. ~150 words explaining an
  // absence, on 2,690 cards, outweighed the tumour panel below that HAS data — which is how a
  // reader concludes the protein has none. The skin case is real and is recorded in the crosswalk
  // document; what the CARD must not do is explain at length in place of showing.
  it('keeps the absence to one line and does not explain at card length', () => {
    // ⚠ measure THE BLOCK, not everything after its heading. A text slice ran on into the source
    // line and the licence quotation and reported 616 characters for a two-sentence paragraph.
    const { container } = render(<ClinicalEdges block={PRESENT} />)
    const burden = container.querySelector('.clin-burden')
    expect(burden).not.toBeNull()
    expect(burden.textContent.trim().length).toBeLessThan(320)
    expect(burden.textContent).not.toMatch(/Skin excluding Basal and Squamous/i)
    // ⚠ one paragraph of body, not a section
    expect(burden.querySelectorAll('p').length).toBe(1)
  })

  it('renders the burden slot even when the protein is NOT covered', () => {
    const t = text(ABSENT)
    expect(t).toMatch(/How common, how deadly/)
    // ⚠ ruling 1 — the slot renders, never omitted; the WORDING is the part that moved
    expect(t).toMatch(/not shown for this protein/i)
    expect(t).not.toMatch(/we do not have that data/i)
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
