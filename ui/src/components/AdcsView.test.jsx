// D-122 — ADC-B index. D-124 — ADC-C-B Approved | Pipeline shelves.
// Red-capable: Approved rows come from GET /api/adcs; Pipeline from
// GET /api/adcs/pipeline; phase filter is the closed vocab; Access
// panel is wired to GET /api/adcs/access. No invented science keys.
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import {
  CANCER_TYPE_ABSENT_COPY,
  PHASE_VOCAB,
  PIPELINE_CANCER_TYPE_ABSENT_COPY,
  PIPELINE_DESCRIPTION_ABSENT_COPY,
} from '../adcCatalog.js'

vi.mock('../api.js', () => ({
  listAdcs: vi.fn(),
  listPipelineAdcs: vi.fn(),
  getAdcAccess: vi.fn(),
}))
import { listAdcs, listPipelineAdcs, getAdcAccess } from '../api.js'
import AdcsView from './AdcsView.jsx'

const env = (value, extras = {}) => ({
  value,
  source: extras.source ?? 'fixture',
  as_of: extras.as_of ?? '2026-09-05',
  confidence: extras.confidence ?? 'official',
})

const row = (id, brand, antigen, accession, cancerTypes = null) => ({
  id: env(id, { confidence: 'derived' }),
  inn: env(id.replace(/-/g, ' '), { confidence: 'derived' }),
  brand_name: env(brand),
  antigen: env(antigen, { confidence: 'reviewed' }),
  uniprot_accession: env(accession, { confidence: 'reviewed' }),
  cancer_type: env(cancerTypes, {
    confidence: 'reviewed',
    as_of: '2026-09-08',
    source: cancerTypes
      ? `reviewed reduction of FDA label section 1 for ${brand}; openFDA label.json 2026-09-08`
      : `openFDA label.json for ${brand} 2026-09-08 returned no indications_and_usage`,
  }),
})

// D-140 — `cancerTypes` / `description` default to a NAMED ABSENCE, because that
// is the shape of half the committed shelf and the shape a test can get wrong
// quietly. Each absence carries its own source, which is what the cell renders.
const pipeRow = (id, name, antigen, accession, phase, stage = 'clinical', extra = {}) => ({
  id: env(id, { confidence: 'derived' }),
  name: env(name, { confidence: 'reviewed' }),
  antigen: env(antigen, { confidence: 'reviewed' }),
  uniprot_accession: env(accession, { confidence: 'reviewed' }),
  development_stage: env(stage, { confidence: 'reviewed' }),
  phase: env(phase, { confidence: 'reviewed' }),
  source_citation: env('fixture citation', { confidence: 'reviewed' }),
  cancer_type: extra.cancerTypes
    ? env(extra.cancerTypes, { confidence: 'reviewed' })
    : {
      value: null,
      source: `ClinicalTrials.gov query.intr=${name} retrieved 2026-09-08 returned 0 studies`,
      as_of: '2026-09-08',
      confidence: 'reviewed',
    },
  conditions_verbatim: env(extra.conditions ?? 'fixture citation', { confidence: 'reviewed' }),
  description: extra.description
    ? env(extra.description, { confidence: 'reviewed' })
    : {
      value: null,
      source: `no maker named for ${name} on 2026-09-08`,
      as_of: '2026-09-08',
      confidence: 'reviewed',
    },
})

const CATALOG = {
  scope: env('fda_approved_only', { confidence: 'reviewed' }),
  completeness: env('floor_not_census', { confidence: 'reviewed' }),
  approvals_reconciled_as_of: env('2026-09-05'),
  antigen_mapping_reviewed_as_of: env('2026-09-05', { confidence: 'reviewed' }),
  indications_reviewed_as_of: env('2026-09-08', { confidence: 'reviewed' }),
  named_exclusions: env([
    { id: 'ifinatamab-deruxtecan', reason: 'not approved; ADC-C / mapping PDUFA' },
    { id: 'pipeline_and_right_to_try', reason: 'ADC-C' },
  ], { confidence: 'reviewed' }),
  adcs: [
    row('enfortumab-vedotin', 'PADCEV', 'NECTIN4', 'Q96NY8', ['Urothelial cancer']),
    // ⚠ One row with NO label indication on purpose: the mixed case is the one
    // that can go quietly wrong, and it is the only way to see that an absent
    // row trails the sort instead of leading it (D-136 / D-087).
    row('ado-trastuzumab-emtansine', 'KADCYLA', 'ERBB2', 'P04626'),
    row('fam-trastuzumab-deruxtecan', 'ENHERTU', 'ERBB2', 'P04626', ['Breast cancer']),
  ],
}

const PIPELINE = {
  scope: env('pipeline_investigational', { confidence: 'reviewed' }),
  completeness: env('floor_not_census', { confidence: 'reviewed' }),
  mapping_sourced_as_of: env('2026-07-27', { confidence: 'reviewed' }),
  catalog_assembled_as_of: env('2026-09-05', { confidence: 'derived' }),
  conditions_reviewed_as_of: env('2026-09-08', { confidence: 'reviewed' }),
  registry_artifact: env('data/adcs/artifacts/ctgov.pipeline.2026-09-08.json', { confidence: 'derived' }),
  pipeline: [
    pipeRow('ifinatamab-deruxtecan', 'ifinatamab deruxtecan', 'CD276', 'Q5ZPR3', 'BLA/NDA submitted', 'clinical', {
      cancerTypes: ['Small-cell lung cancer'],
      conditions: 'Extensive-stage Small-cell Lung Cancer',
      description: 'Daiichi Sankyo/Merck — I-DXd, a CD276-directed conjugate.',
    }),
    // ⚠ One clinical row with NO tumour type on purpose: the mixed case is the one
    // that can go quietly wrong, and it is the only way to see that an absent row
    // trails the sort instead of leading it (D-140 / D-087).
    pipeRow('ly3076226', 'LY3076226', 'FGFR3', 'P22607', 'Phase 1', 'clinical', {
      conditions: 'Advanced Cancer; Metastatic Cancer',
      description: 'Eli Lilly and Company — an FGFR3-directed conjugate.',
    }),
    pipeRow('depatuxizumab-mafodotin', 'depatuxizumab mafodotin', 'EGFR', 'P00533', 'Phase 3', 'clinical', {
      cancerTypes: ['Glioblastoma'],
      conditions: 'Glioblastoma; Gliosarcoma',
      description: 'AbbVie — ABT-414, an EGFR-directed conjugate.',
    }),
    // ⚠ And one row absent on BOTH new columns — the preclinical shape.
    pipeRow('ch10d7-mmae', 'ch10D7-MMAE', 'CDCP1', 'Q9H5V8', 'Other', 'preclinical'),
  ],
}

const ACCESS = {
  disclaimer: env(
    'This payload is informational only. It is NOT medical advice, NOT legal advice, and NOT a treatment recommendation.',
    { confidence: 'reviewed' },
  ),
  scope: env('trials_and_right_to_try_informational', { confidence: 'reviewed' }),
  completeness: env('floor_not_census', { confidence: 'reviewed' }),
  as_of: env('2026-09-05', { confidence: 'derived' }),
  clinical_trials_registry: env('https://clinicaltrials.gov/', { confidence: 'official' }),
  expanded_access_fda: env('https://www.fda.gov/news-events/public-health-focus/expanded-access', { confidence: 'official' }),
  right_to_try_statute: env('21 U.S.C. § 360bbb-0a', { confidence: 'official' }),
  right_to_try_public_law: env('Pub. L. 115-176', { confidence: 'official' }),
  right_to_try_fda: env('https://www.fda.gov/patients/learn-about-expanded-access-and-other-treatment-options/right-try', { confidence: 'official' }),
  named_nct_ids_from_pipeline: env(['NCT03310957', 'NCT02529553'], { confidence: 'reviewed' }),
}

const renderIndex = (initial = '/adcs') =>
  render(<MemoryRouter initialEntries={[initial]}><AdcsView /></MemoryRouter>)

const bodyFirstCells = () =>
  screen.getAllByRole('row').slice(1)
    .map((r) => r.querySelector('td')?.textContent ?? '')

beforeEach(() => {
  listAdcs.mockReset()
  listPipelineAdcs.mockReset()
  getAdcAccess.mockReset()
  listAdcs.mockResolvedValue(CATALOG)
  listPipelineAdcs.mockResolvedValue(PIPELINE)
  getAdcAccess.mockResolvedValue(ACCESS)
})

describe('AdcsView — D-122 index', () => {
  it('renders rows from the catalog payload and derives the count', async () => {
    const { container } = renderIndex()
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    expect(container.textContent).toMatch(/3 rows in this file/)
    expect(container.textContent).toMatch(/pin of the catalog/)
    expect(container.textContent).not.toMatch(/15 approved ADCs/)
    expect(screen.getByRole('link', { name: 'PADCEV' })).toHaveAttribute(
      'href', '/adcs/enfortumab-vedotin',
    )
    expect(container.textContent).toMatch(/NECTIN4/)
    expect(container.textContent).toMatch(/fda_approved_only/)
    expect(container.textContent).toMatch(/floor_not_census/)
    expect(listAdcs).toHaveBeenCalled()
    expect(listPipelineAdcs).not.toHaveBeenCalled()
  })

  it('D-136 — lists the tumour types the payload carries, and names the absence on the row that has none', async () => {
    const { container } = renderIndex()
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    expect(screen.getByText('Urothelial cancer')).toBeInTheDocument()
    expect(screen.getByText('Breast cancer')).toBeInTheDocument()
    // KADCYLA's row states no indication, and says so in its own words.
    expect(container.textContent).toMatch(/KADCYLA 2026-09-08 returned no indications_and_usage/)
    // ⚠ Nothing invented for the row that has none, and no staining anywhere.
    expect(screen.queryAllByText(CANCER_TYPE_ABSENT_COPY)).toHaveLength(0)
    expect(container.textContent).not.toMatch(/multiple myeloma/i)
    // ⚠ Scoped to the TABLE, not the page. The lede legitimately says the
    // column is "never a tissue-staining survey"; what must never appear is a
    // staining-derived value in a cell (D-093).
    expect(screen.getByRole('table').textContent)
      .not.toMatch(/quasi H-score|proteinatlas|staining/i)
  })

  it('D-136 — sorting by cancer type gives real categories, and the absent row trails BOTH ways', async () => {
    renderIndex()
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())

    fireEvent.click(screen.getByRole('button', { name: /Cancer type/ }))
    // ascending: Breast < Urothelial, and the row with no indication is last —
    // a category off the axis, not the alphabetically-first one.
    expect(bodyFirstCells()).toEqual([
      expect.stringMatching(/ENHERTU/),
      expect.stringMatching(/PADCEV/),
      expect.stringMatching(/KADCYLA/),
    ])

    fireEvent.click(screen.getByRole('button', { name: /Cancer type/ }))
    expect(bodyFirstCells()).toEqual([
      expect.stringMatching(/PADCEV/),
      expect.stringMatching(/ENHERTU/),
      expect.stringMatching(/KADCYLA/),
    ])
  })

  it('sorts by name and by protein', async () => {
    renderIndex()
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    // default: brand name ascending
    expect(bodyFirstCells()[0]).toMatch(/ENHERTU/)
    expect(bodyFirstCells()[2]).toMatch(/PADCEV/)

    fireEvent.click(screen.getByRole('button', { name: /Name/ }))
    expect(bodyFirstCells()[0]).toMatch(/PADCEV/)

    fireEvent.click(screen.getByRole('button', { name: /Protein/ }))
    const proteins = screen.getAllByRole('row').slice(1)
      .map((r) => r.querySelectorAll('td')[2]?.textContent)
    expect(proteins[0]).toMatch(/ERBB2/)
    expect(proteins[2]).toMatch(/NECTIN4/)
  })

  it('lists named exclusions without making them catalog rows', async () => {
    const { container } = renderIndex()
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    expect(container.textContent).toMatch(/Named exclusions/)
    expect(container.textContent).toMatch(/ifinatamab-deruxtecan/)
    expect(screen.queryByRole('link', { name: /ifinatamab/i })).toBeNull()
    expect(screen.queryByRole('link', { name: /Lumoxiti/i })).toBeNull()
  })

  it('has no phase filter on the Approved shelf', async () => {
    renderIndex()
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    expect(screen.queryByRole('combobox', { name: /phase/i })).toBeNull()
    expect(screen.getByRole('tab', { name: 'Approved' })).toHaveAttribute('aria-selected', 'true')
    expect(screen.getByRole('tab', { name: 'Pipeline' })).toHaveAttribute('aria-selected', 'false')
  })

  it('refuses invented science keys and does not mix pipeline rows into Approved', async () => {
    const { container } = renderIndex()
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    for (const banned of [/^\s*DAR\s*$/i, /^\s*IC50\s*$/i, /^\s*ORR\s*$/i, /^\s*PFS\s*$/i]) {
      expect(screen.queryByRole('columnheader', { name: banned })).toBeNull()
    }
    expect(container.textContent).not.toMatch(/\bDAR\b|\bIC50\b|\bORR\b|\bPFS\b/)
    expect(container.textContent).toMatch(/not mixed with investigational/)
    expect(screen.queryByRole('link', { name: /LY3076226/ })).toBeNull()
  })
})

describe('AdcsView — D-124 Pipeline shelf', () => {
  it('Pipeline shelf consumes GET /api/adcs/pipeline and not the approved catalog', async () => {
    const { container } = renderIndex()
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    fireEvent.click(screen.getByRole('tab', { name: 'Pipeline' }))
    await waitFor(() => expect(listPipelineAdcs).toHaveBeenCalled())
    await waitFor(() => expect(screen.getByRole('link', { name: 'ifinatamab deruxtecan' })).toBeInTheDocument())
    expect(screen.getByRole('link', { name: 'ifinatamab deruxtecan' })).toHaveAttribute(
      'href', '/adcs/pipeline/ifinatamab-deruxtecan',
    )
    expect(container.textContent).toMatch(/pipeline_investigational/)
    expect(container.textContent).toMatch(/4 rows in this file/)
    expect(screen.queryByRole('link', { name: 'PADCEV' })).toBeNull()
    expect(container.textContent).not.toMatch(/15 pipeline ADCs/)
    expect(container.textContent).not.toMatch(/\bDAR\b|\bIC50\b|\bORR\b/)
  })

  it('phase filter uses the Architect closed set and can empty the table', async () => {
    renderIndex('/adcs?shelf=pipeline')
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    const filter = screen.getByRole('combobox', { name: /phase/i })
    for (const token of PHASE_VOCAB) {
      expect(within(filter).getByRole('option', { name: token })).toBeInTheDocument()
    }
    expect(within(filter).queryByRole('option', { name: 'Phase 4' })).toBeNull()
    expect(within(filter).queryByRole('option', { name: 'preclinical' })).toBeNull()
    expect(within(filter).queryByRole('option', { name: 'approved' })).toBeNull()

    fireEvent.change(filter, { target: { value: 'Phase 1' } })
    expect(screen.getByRole('link', { name: 'LY3076226' })).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'ifinatamab deruxtecan' })).toBeNull()
    expect(screen.getByText(/Showing 1 of 4/)).toBeInTheDocument()

    fireEvent.change(filter, { target: { value: 'Phase 2' } })
    expect(screen.queryByRole('table')).toBeNull()
    expect(screen.getByText(/no row in this file matches that phase/)).toBeInTheDocument()
  })

  it('D-140 — the Pipeline index carries Cancer type and Description columns', async () => {
    const { container } = renderIndex('/adcs?shelf=pipeline')
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    for (const label of ['Name', 'Cancer type', 'Phase', 'Protein', 'Description']) {
      expect(screen.getByRole('columnheader', { name: new RegExp(label) })).toBeInTheDocument()
    }
    expect(screen.getByText('Small-cell lung cancer')).toBeInTheDocument()
    expect(screen.getByText('Glioblastoma')).toBeInTheDocument()
    expect(container.textContent).toMatch(/Daiichi Sankyo\/Merck/)
    expect(container.textContent).toMatch(/Eli Lilly and Company/)
    // ⚠ The rows that state neither say WHICH lookup came back empty, in their
    // own words — never a blank, and never the page-wide fallback (D-140).
    expect(container.textContent).toMatch(/query.intr=ch10D7-MMAE retrieved 2026-09-08 returned 0 studies/)
    expect(container.textContent).toMatch(/no maker named for ch10D7-MMAE/)
    expect(screen.queryAllByText(PIPELINE_CANCER_TYPE_ABSENT_COPY)).toHaveLength(0)
    expect(screen.queryAllByText(PIPELINE_DESCRIPTION_ABSENT_COPY)).toHaveLength(0)
  })

  it('D-140 — an absent cell is a short label with the row\'s own source inside it', async () => {
    // ⚠ D-135's defect, not re-shipped. Five of ten committed rows are absent on
    // cancer type and six on description; putting each ~300-character source
    // straight into a `<td>` made the table two columns of prose. The label is
    // short, and the row's own words are in the DOM inside the disclosure —
    // shortening must not become replacing (D-136 decision 6).
    renderIndex('/adcs?shelf=pipeline')
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    const table = screen.getByRole('table')

    const summaries = [...table.querySelectorAll('details.absent-why > summary')]
    expect(summaries.length).toBeGreaterThan(0)
    for (const summary of summaries) {
      expect(summary.textContent.length).toBeLessThan(40)
    }
    expect(within(table).getAllByText('none stated — why').length).toBe(2)
    expect(within(table).getAllByText('no maker named — why').length).toBe(1)

    // ⚠ The full source is not lost, it is one step away — and it is the ROW's,
    // not a sentence the page made up.
    const bodies = [...table.querySelectorAll('details.absent-why .absent-why-body')]
      .map((p) => p.textContent)
    expect(bodies.some((t) => /query.intr=ch10D7-MMAE .* returned 0 studies/.test(t))).toBe(true)
    expect(bodies.some((t) => /query.intr=LY3076226 .* returned 0 studies/.test(t))).toBe(true)
  })

  it('D-140 — the pipeline shelf says these are trials, not FDA indications', async () => {
    const { container } = renderIndex('/adcs?shelf=pipeline')
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    expect(container.textContent).toMatch(/studied in/)
    expect(container.textContent).toMatch(/not an FDA indication/)
    expect(container.textContent).toMatch(/Programme fields reviewed as of 2026-09-08/)
    // ⚠ Scoped to the TABLE: no staining-derived value may reach a cell (D-093).
    expect(screen.getByRole('table').textContent)
      .not.toMatch(/quasi H-score|proteinatlas|staining/i)
    expect(screen.getByRole('table').textContent).not.toMatch(/INDICATIONS AND USAGE/i)
  })

  it('D-140 — sorting by cancer type trails the absent rows in BOTH directions', async () => {
    renderIndex('/adcs?shelf=pipeline')
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    const header = screen.getByRole('columnheader', { name: /Cancer type/ })
    const button = within(header).getByRole('button')

    fireEvent.click(button)
    let names = bodyFirstCells()
    expect(names[0]).toMatch(/depatuxizumab mafodotin/)
    expect(names[1]).toMatch(/ifinatamab deruxtecan/)
    // The two absent rows are a CATEGORY, not the alphabetically-first value.
    expect(names.slice(2).join(' ')).toMatch(/LY3076226/)
    expect(names.slice(2).join(' ')).toMatch(/ch10D7-MMAE/)

    fireEvent.click(button)
    names = bodyFirstCells()
    expect(names[0]).toMatch(/ifinatamab deruxtecan/)
    expect(names.slice(2).join(' ')).toMatch(/LY3076226/)
    expect(names.slice(2).join(' ')).toMatch(/ch10D7-MMAE/)
  })

  it('Access panel surfaces the A disclaimer and named NCT ids', async () => {
    const { container } = renderIndex('/adcs?shelf=pipeline')
    await waitFor(() => expect(getAdcAccess).toHaveBeenCalled())
    await waitFor(() => expect(container.textContent).toMatch(/NOT medical advice/))
    expect(container.textContent).toMatch(/NOT legal advice/)
    expect(container.textContent).toMatch(/NOT a treatment recommendation/)
    expect(container.textContent).toMatch(/NCT03310957/)
    expect(container.textContent).toMatch(/NCT02529553/)
    expect(container.textContent).toMatch(/not an enrollment recommendation/)
    expect(container.textContent).toMatch(/clinicaltrials.gov/i)
  })
})
