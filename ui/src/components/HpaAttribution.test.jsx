import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import fs from 'node:fs'
import path from 'node:path'
import HpaAttribution from './HpaAttribution.jsx'
import ClinicalEdges from './ClinicalEdges.jsx'
import SurfaceCheck from './SurfaceCheck.jsx'
import CensusTable from './CensusTable.jsx'

const ATTRIB = {
  primary_publication: {
    citation: 'Uhlén M et al., Tissue-based map of the human proteome, Science (2015)',
    doi: '10.1126/science.1260419',
    url: 'https://doi.org/10.1126/science.1260419',
  },
  website: { name: 'Human Protein Atlas', url: 'https://www.proteinatlas.org' },
  data_credit: 'Human Protein Atlas',
  deep_link: 'https://v22.proteinatlas.org/ENSG00000120949-TNFRSF8/pathology',
  deep_link_absent_reason: null,
  ensg: 'ENSG00000120949',
}

// ⚠⚠ PA's FULL LIST — four surfaces, and two of them were built AFTER the audit that found the gap.
// The test is parameterised over the list precisely because the last audit was scoped to its
// author's field of view, which is F-052's subject.
const SURFACES = [
  {
    name: 'ClinicalEdges (pathology.tsv + normal_tissue.tsv)',
    render: () => render(<ClinicalEdges block={{
      status: 'ihc_present', gene: 'TNFRSF8', layers: [],
      tumours: [{ cancer: 'ovarian cancer', patients_tested: 12, patients_positive: 10,
                  high: 4, medium: 4, low: 2, not_detected: 2 }],
      normal_tissues: [{ tissue: 'bronchus', highest: 'High', cell_types: 3, detected_in: 2 }],
      source: 'HPA v22.', boundary: 'Immunohistochemistry.',
      attribution_tumour: ATTRIB, attribution_normal: ATTRIB,
    }} />),
  },
  {
    name: 'SurfaceCheck (proteinatlas.tsv subcellular)',
    render: () => render(<SurfaceCheck check={{
      category: 'corroborated_membrane', main_locations: ['Plasma membrane'],
      if_reliability: 'Enhanced', unreconciled_locations: [], unreconciled_causes: [],
      instruments: { census: 'UniProt topology', hpa_if: 'HPA immunofluorescence' },
      attribution: ATTRIB,
    }} />),
  },
  {
    name: 'CensusTable (the staining lens)',
    render: () => render(<MemoryRouter><CensusTable rows={[{
      id: 1, accession: 'P28908', gene: 'TNFRSF8', label: 'TNF receptor 8', tranche: 4,
      span_aa: 367, mean_plddt: 80, topology: 'single', profile_status: 'computed',
      staining: {
        attribution: ATTRIB, min_patients: 10,
        best_panel: { lens: 'best_panel', category: 'measured', patients_positive: 11,
                      patients_tested: 12, cancer: 'ovarian cancer', panels_considered: 1,
                      panels_excluded_small: 0 },
        pooled: { lens: 'pooled', category: 'measured', patients_positive: 11,
                  patients_tested: 12, cancer: null, panels_considered: 1,
                  panels_excluded_small: 0 },
        critical_normal_high: [], critical_tissues_declared: ['liver'],
        critical_tissues_unknown: [], normal_basis: 'three individuals per tissue',
      },
    }]} /></MemoryRouter>),
  },
]

// ⚠⚠ PC1 — THE MOUNT PRECONDITION, over PA's list rather than one component.
// HPA words it as a precondition: "be sure that our content is never displayed in the absence of
// such citation." D-094's shape, written by HPA.
describe.each(SURFACES)('$name', ({ render: draw }) => {
  it('renders the per-datum v22 link', () => {
    const { container } = draw()
    const links = [...container.querySelectorAll('a')].map((a) => a.getAttribute('href'))
    expect(links.some((h) => h && h.includes('v22.proteinatlas.org'))).toBe(true)
  })

  it('renders the primary publication', () => {
    expect(draw().container.textContent).toMatch(/10\.1126\/science\.1260419/)
  })

  it('renders the website reference', () => {
    const { container } = draw()
    const links = [...container.querySelectorAll('a')].map((a) => a.getAttribute('href'))
    expect(links.some((h) => h === 'https://www.proteinatlas.org')).toBe(true)
  })

  it('renders the image/data credit as its own element', () => {
    const { container } = draw()
    const el = container.querySelector('.hpa-attrib-credit')
    expect(el).not.toBeNull()
    expect(el.textContent).toMatch(/Image\/data credit:\s*Human Protein Atlas/)
  })

  // ⚠⚠ PD — every link renders v22. www beside v22 data cites a source that is not the source AND
  // points at different terms: amendment 8 measured BY-SA 3.0 on v22 and BY 4.0 on www.
  it('never deep-links to the current release beside v22 data', () => {
    const { container } = draw()
    const atlas = [...container.querySelectorAll('a')]
      .map((a) => a.getAttribute('href') || '')
      .filter((h) => h.includes('proteinatlas.org') && h !== 'https://www.proteinatlas.org')
    expect(atlas.length).toBeGreaterThan(0)
    for (const h of atlas) expect(h).toMatch(/^https:\/\/v22\.proteinatlas\.org\//)
  })
})

describe('the absent link is a category, not a broken anchor', () => {
  it('states why no link could be built', () => {
    const t = render(<HpaAttribution attribution={{
      ...ATTRIB, deep_link: null,
      deep_link_absent_reason: 'no Ensembl gene id resolves for FOO in the ingested HPA files',
    }} />).container.textContent
    expect(t).toMatch(/No direct atlas link/)
    expect(t).toMatch(/no Ensembl gene id resolves/)
    // ⚠ and the other three elements still render — the precondition is not waived
    expect(t).toMatch(/10\.1126\/science\.1260419/)
    expect(t).toMatch(/Image\/data credit/)
  })
})

// ⚠⚠ PC3 — THE TEST THAT FAILS WHEN A NEW HPA-RENDERING SURFACE APPEARS UNCOVERED.
// Without this, the next component repeats the whole defect: a convention obeyed by every caller
// except the newest one is F-052, and this order is its second instance in three days.
describe('no HPA-rendering surface escapes the audit', () => {
  const COVERED = new Set([
    'ClinicalEdges.jsx', 'SurfaceCheck.jsx', 'CensusTable.jsx', 'CancerAssociations.jsx',
    'HpaAttribution.jsx',
    // ⚠⚠ Added because PC3 FOUND IT on its first run. CensusDetail renders qh_score inline, in its
    // own list, separately from the Associations component it also mounts. NC missed it, the
    // Planner's count of two missed it, and my own enumeration missed it — all three stopped at
    // the component boundary. This is the fifth surface.
    'CensusDetail.jsx',
  ])
  // fields whose presence means the component renders a value ORIGINATING in HPA
  const HPA_FIELDS = [
    'patients_tested', 'patients_positive', 'normal_tissues', 'qh_score',
    'main_locations', 'if_reliability', 'stained_pct', 'critical_normal_high',
  ]

  it('every component touching an HPA-derived field is in the covered set', () => {
    const dir = path.resolve(__dirname)
    const offenders = []
    for (const f of fs.readdirSync(dir)) {
      if (!f.endsWith('.jsx') || f.includes('.test.')) continue
      const src = fs.readFileSync(path.join(dir, f), 'utf8')
      const touches = HPA_FIELDS.filter((k) => src.includes(k))
      if (touches.length && !COVERED.has(f)) offenders.push(`${f} (${touches.join(', ')})`)
    }
    expect(offenders).toEqual([])
  })

  it('every covered component actually imports the attribution', () => {
    const dir = path.resolve(__dirname)
    const missing = []
    for (const f of COVERED) {
      if (f === 'HpaAttribution.jsx') continue
      const src = fs.readFileSync(path.join(dir, f), 'utf8')
      if (!src.includes('HpaAttribution')) missing.push(f)
    }
    expect(missing).toEqual([])
  })
})
