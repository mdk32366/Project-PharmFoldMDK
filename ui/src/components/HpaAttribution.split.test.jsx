import { render } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import fs from 'node:fs'
import path from 'node:path'
import { stripComments } from '../stripComments.js'
import { HpaCreditProvider, HpaDeepLink } from './HpaAttribution.jsx'
import ClinicalEdges from './ClinicalEdges.jsx'
import SurfaceCheck from './SurfaceCheck.jsx'

// ⚠⚠ ONE BLOCK, RENDERED FOUR TIMES, ON 79% OF CENSUS CARDS.
//
// Measured across 100 census cards before this change: **79 rendered FOUR attribution blocks and 21
// rendered none.** There was no middle case — LAMP1, the card the owner reported, was the 79% case.
// All four read identically on the page.
//
// ⚠ But they were NOT identical underneath: the payloads differ in exactly one field, `deep_link`,
// and **75 of the 79 carry THREE DISTINCT deep links.** So "keep the first, drop the rest" would
// silently discard two working per-datum links — and element 4 is the one the licence describes
// per-datum. Hence a split BY CASE, not a de-duplication.
//
// ⚠⚠ AND THE SUPPRESSION HALF, WHICH IS LARGER THAN THE REPETITION HALF. Blocks rendering a
// licence-required citation while carrying NO HPA VALUE of their own, among those 79 cards:
//   cancer_assoc 78 · surface_check 51 · clin_normal 39 · clin_tumour 4
// A citation attached to nothing is not compliance.

const ATTRIB = (deep) => ({
  primary_publication: {
    citation: 'Uhlén M et al., Tissue-based map of the human proteome, Science (2015)',
    doi: '10.1126/science.1260419',
    url: 'https://doi.org/10.1126/science.1260419',
  },
  website: { name: 'Human Protein Atlas', url: 'https://www.proteinatlas.org' },
  data_credit: 'Human Protein Atlas',
  deep_link: deep,
  deep_link_absent_reason: null,
})

const TUMOUR_LINK = 'https://v22.proteinatlas.org/ENSG00000185896-LAMP1/pathology'
const NORMAL_LINK = 'https://v22.proteinatlas.org/ENSG00000185896-LAMP1/tissue'

const FULL_BLOCK = {
  status: 'ihc_present', gene: 'LAMP1', layers: [],
  tumours: [{ cancer: 'breast cancer', patients_tested: 11, patients_positive: 11,
              high: 10, medium: 1, low: 0, not_detected: 0 }],
  normal_tissues: [{ tissue: 'skin 1', highest: 'High', cell_types: 13, detected_in: 11 }],
  source: 'HPA v22.', boundary: 'Immunohistochemistry.',
  attribution_tumour: ATTRIB(TUMOUR_LINK), attribution_normal: ATTRIB(NORMAL_LINK),
}

const creditsIn = (c) => c.querySelectorAll('.hpa-attrib-credit')
const linksIn = (c) => [...c.querySelectorAll('.hpa-attrib-link')].map((a) => a.getAttribute('href'))

describe('the source-level elements render ONCE per page', () => {
  it('emits one credit for a page carrying several HPA blocks', () => {
    const { container } = render(
      <HpaCreditProvider>
        <ClinicalEdges block={FULL_BLOCK} />
        <SurfaceCheck check={{
          category: 'corroborated_membrane', main_locations: ['Plasma membrane'],
          if_reliability: 'Enhanced', unreconciled_locations: [], unreconciled_causes: [],
          instruments: { census: 'UniProt topology', hpa_if: 'HPA immunofluorescence' },
          attribution: ATTRIB('https://v22.proteinatlas.org/ENSG00000185896-LAMP1/subcellular'),
        }} />
      </HpaCreditProvider>,
    )
    expect(creditsIn(container)).toHaveLength(1)
    // ⚠ the publication and website reference travel WITH the credit, once
    expect(container.textContent).toMatch(/10\.1126\/science\.1260419/)
  })

  // ⚠⚠ THE CLAUSE THAT STOPS THE OBVIOUS WRONG FIX. De-duplicating by keeping the first block would
  // have thrown away two working per-datum links on 75 of 79 cards.
  it('keeps EVERY distinct per-datum link', () => {
    const { container } = render(
      <HpaCreditProvider><ClinicalEdges block={FULL_BLOCK} /></HpaCreditProvider>,
    )
    const links = linksIn(container)
    expect(links).toContain(TUMOUR_LINK)
    expect(links).toContain(NORMAL_LINK)
    expect(new Set(links).size).toBe(2)
    expect(creditsIn(container)).toHaveLength(1)   // …while the credit still appears once
  })
})

describe('suppression — a citation is never attached to nothing', () => {
  it('renders no attribution when the tumour and normal panels are both empty', () => {
    const { container } = render(
      <HpaCreditProvider>
        <ClinicalEdges block={{ ...FULL_BLOCK, tumours: [], normal_tissues: [] }} />
      </HpaCreditProvider>,
    )
    expect(linksIn(container)).toHaveLength(0)
    expect(creditsIn(container)).toHaveLength(0)
  })

  it('renders the tumour link only, when only tumours have rows', () => {
    // ⚠ `normal_tissues` was empty on 39 of 79 sampled cards while still carrying a citation
    const { container } = render(
      <HpaCreditProvider><ClinicalEdges block={{ ...FULL_BLOCK, normal_tissues: [] }} /></HpaCreditProvider>,
    )
    expect(linksIn(container)).toEqual([TUMOUR_LINK])
    expect(creditsIn(container)).toHaveLength(1)
  })

  it('renders nothing for a surface check that never attempted IF', () => {
    // ⚠ 51 of 79 sampled cards were in this state and cited HPA anyway
    const { container } = render(
      <HpaCreditProvider>
        <SurfaceCheck check={{
          category: 'if_not_attempted', main_locations: [], if_reliability: null,
          unreconciled_locations: [], unreconciled_causes: [],
          instruments: { census: 'UniProt topology', hpa_if: 'HPA immunofluorescence' },
          attribution: ATTRIB('https://v22.proteinatlas.org/x/subcellular'),
        }} />
      </HpaCreditProvider>,
    )
    expect(creditsIn(container)).toHaveLength(0)
  })
})

// ⚠⚠ THE PRECONDITION, PRESERVED BY CONSTRUCTION. HPA words citation as a condition of display:
// "be sure that our content is never displayed in the absence of such citation."
describe('the mount precondition still binds after the split', () => {
  it('a page that renders an HPA value renders the citation', () => {
    const { container } = render(
      <HpaCreditProvider><ClinicalEdges block={FULL_BLOCK} /></HpaCreditProvider>,
    )
    expect(container.textContent).toMatch(/breast cancer/)          // the value
    expect(creditsIn(container)).toHaveLength(1)                    // …and the citation
    expect(container.textContent).toMatch(/Image\/data credit:/)
  })

  // ⚠⚠ FORGETTING THE PROVIDER MUST COST REDUNDANCY, NEVER COMPLIANCE.
  it('falls back to the full block outside a provider', () => {
    const { container } = render(<HpaDeepLink attribution={ATTRIB(TUMOUR_LINK)} view="pathology" />)
    expect(creditsIn(container)).toHaveLength(1)
    expect(linksIn(container)).toEqual([TUMOUR_LINK])
  })
})

// ⚠ The licence asks for a credit by name; restyling its case is not ours to do.
describe('the credit is not restyled', () => {
  it('does not uppercase the licence-required label', () => {
    // ⚠⚠ `textContent` IGNORES CSS case transforms, so the existing assertion on
    // /Image\/data credit:/ passed while the page rendered "IMAGE/DATA CREDIT:". The only way to
    // see it from a test is to read the stylesheet.
    const css = stripComments(
      fs.readFileSync(path.resolve(process.cwd(), 'src/styles.css'), 'utf8'),
    )
    const rule = css.split('\n').find((l) => l.includes('.hpa-attrib-credit-label'))
    expect(rule).toBeTruthy()
    expect(rule).not.toMatch(/text-transform/)
  })
})

// ⚠⚠ THE INVERSION: the citation sat on the branch with NO value and was ABSENT from the branch
// that renders `qh_score`. The PC3 guard could not see it — it asserts the FILE imports the
// attribution, and the file did. A file-level guard cannot see which BRANCH renders the value.
describe('the census association block cites the branch that has data', () => {
  const CARD = stripComments(
    fs.readFileSync(path.resolve(process.cwd(), 'src/components/CensusDetail.jsx'), 'utf8'),
  )
  const branchAfter = (marker) => CARD.slice(CARD.indexOf(marker))

  it('the qh_score branch carries the attribution', () => {
    const seg = branchAfter('assoc.hits.map')
    expect(seg).toMatch(/HpaDeepLink/)
  })

  it('the not-covered branch does not', () => {
    const start = CARD.indexOf("assoc.status !== 'covered'")
    const seg = CARD.slice(start, CARD.indexOf('assoc.hits.length === 0'))
    expect(seg).not.toMatch(/HpaDeepLink|HpaAttribution/)
  })

  it('and it names the wider panel rather than leaving "unknown" to read as "none"', () => {
    const start = CARD.indexOf("assoc.status !== 'covered'")
    const seg = CARD.slice(start, CARD.indexOf('assoc.hits.length === 0'))
    expect(seg).toMatch(/not the only tumour evidence/i)
  })
})

// ⚠⚠ TWO LINKS, IDENTICAL TEXT, DIFFERENT DESTINATIONS — reported from the LAMP1 card.
// The tumour link goes to /pathology and the normal-tissue link to /tissue, and both rendered
// "View this protein on the Human Protein Atlas (v22)", one after the other. The page showed what
// looked like the same link twice.
// ⚠ This is the same defect as the four repeated credit blocks, ONE LEVEL DOWN: the split by case
// put element 4 beside its datum and then left it describing the PROTEIN rather than the DATUM.
// **A per-datum element labelled per-protein is not per-datum.**
describe('each per-datum link names the datum it cites', () => {
  const labels = (c) => [...c.querySelectorAll('.hpa-attrib-link')].map((a) => a.textContent.trim())

  it('gives the tumour and normal-tissue links different text', () => {
    const { container } = render(
      <HpaCreditProvider><ClinicalEdges block={FULL_BLOCK} /></HpaCreditProvider>,
    )
    const seen = labels(container)
    expect(seen).toHaveLength(2)
    expect(new Set(seen).size).toBe(2)          // ⚠ the assertion the shipped page failed
    expect(seen.some((t) => /tumour/i.test(t))).toBe(true)
    expect(seen.some((t) => /normal-tissue/i.test(t))).toBe(true)
  })

  it('keeps each label attached to the right destination', () => {
    const { container } = render(
      <HpaCreditProvider><ClinicalEdges block={FULL_BLOCK} /></HpaCreditProvider>,
    )
    for (const a of container.querySelectorAll('.hpa-attrib-link')) {
      const href = a.getAttribute('href')
      if (/tumour/i.test(a.textContent)) expect(href).toBe(TUMOUR_LINK)
      if (/normal-tissue/i.test(a.textContent)) expect(href).toBe(NORMAL_LINK)
    }
  })
})

