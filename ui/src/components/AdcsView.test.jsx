// D-122 — ADC-B index. D-124 — ADC-C-B Approved | Pipeline shelves.
// Red-capable: Approved rows come from GET /api/adcs; Pipeline from
// GET /api/adcs/pipeline; phase filter is the closed vocab; Access
// panel is wired to GET /api/adcs/access. No invented science keys.
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { CANCER_TYPE_ABSENT_COPY, PHASE_VOCAB } from '../adcCatalog.js'

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

const row = (id, brand, antigen, accession) => ({
  id: env(id, { confidence: 'derived' }),
  inn: env(id.replace(/-/g, ' '), { confidence: 'derived' }),
  brand_name: env(brand),
  antigen: env(antigen, { confidence: 'reviewed' }),
  uniprot_accession: env(accession, { confidence: 'reviewed' }),
})

const pipeRow = (id, name, antigen, accession, phase, stage = 'clinical') => ({
  id: env(id, { confidence: 'derived' }),
  name: env(name, { confidence: 'reviewed' }),
  antigen: env(antigen, { confidence: 'reviewed' }),
  uniprot_accession: env(accession, { confidence: 'reviewed' }),
  development_stage: env(stage, { confidence: 'reviewed' }),
  phase: env(phase, { confidence: 'reviewed' }),
  source_citation: env('fixture citation', { confidence: 'reviewed' }),
})

const CATALOG = {
  scope: env('fda_approved_only', { confidence: 'reviewed' }),
  completeness: env('floor_not_census', { confidence: 'reviewed' }),
  approvals_reconciled_as_of: env('2026-09-05'),
  antigen_mapping_reviewed_as_of: env('2026-09-05', { confidence: 'reviewed' }),
  named_exclusions: env([
    { id: 'ifinatamab-deruxtecan', reason: 'not approved; ADC-C / mapping PDUFA' },
    { id: 'pipeline_and_right_to_try', reason: 'ADC-C' },
  ], { confidence: 'reviewed' }),
  adcs: [
    row('enfortumab-vedotin', 'PADCEV', 'NECTIN4', 'Q96NY8'),
    row('ado-trastuzumab-emtansine', 'KADCYLA', 'ERBB2', 'P04626'),
    row('fam-trastuzumab-deruxtecan', 'ENHERTU', 'ERBB2', 'P04626'),
  ],
}

const PIPELINE = {
  scope: env('pipeline_investigational', { confidence: 'reviewed' }),
  completeness: env('floor_not_census', { confidence: 'reviewed' }),
  mapping_sourced_as_of: env('2026-07-27', { confidence: 'reviewed' }),
  catalog_assembled_as_of: env('2026-09-05', { confidence: 'derived' }),
  pipeline: [
    pipeRow('ifinatamab-deruxtecan', 'ifinatamab deruxtecan', 'CD276', 'Q5ZPR3', 'BLA/NDA submitted'),
    pipeRow('ly3076226', 'LY3076226', 'FGFR3', 'P22607', 'Phase 1'),
    pipeRow('depatuxizumab-mafodotin', 'depatuxizumab mafodotin', 'EGFR', 'P00533', 'Phase 3'),
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

  it('shows the named cancer-type absence and does not invent an indication', async () => {
    const { container } = renderIndex()
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    const absences = screen.getAllByText(CANCER_TYPE_ABSENT_COPY)
    expect(absences.length).toBe(3)
    expect(container.textContent).not.toMatch(/urothelial|breast cancer|multiple myeloma/i)
    expect(container.textContent).not.toMatch(/quasi H-score/)
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
