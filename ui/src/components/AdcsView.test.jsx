// D-122 — ADC-B index. Red-capable: rows come from GET /api/adcs, sort is
// wired, cancer type is the named v1 absence, row count is derived, no
// invented science keys, no pipeline/RTT rows.
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { CANCER_TYPE_ABSENT_COPY } from '../adcCatalog.js'

vi.mock('../api.js', () => ({ listAdcs: vi.fn() }))
import { listAdcs } from '../api.js'
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

const renderIndex = () => render(<MemoryRouter><AdcsView /></MemoryRouter>)

const bodyBrands = () =>
  screen.getAllByRole('row').slice(1)
    .map((r) => r.querySelector('td')?.textContent ?? '')

beforeEach(() => {
  listAdcs.mockReset()
  listAdcs.mockResolvedValue(CATALOG)
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
    expect(bodyBrands()[0]).toMatch(/ENHERTU/)
    expect(bodyBrands()[2]).toMatch(/PADCEV/)

    fireEvent.click(screen.getByRole('button', { name: /Name/ }))
    expect(bodyBrands()[0]).toMatch(/PADCEV/)

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

  it('refuses invented science keys and pipeline-as-row language', async () => {
    const { container } = renderIndex()
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
    const text = container.textContent.toLowerCase()
    for (const banned of ['dar', 'ic50', 'orr', 'pfs', '"os"', 'payload', 'linker']) {
      expect(text).not.toContain(` ${banned} `)
    }
    expect(container.textContent).toMatch(/not.*pipeline or Right-to-Try/i)
  })
})
