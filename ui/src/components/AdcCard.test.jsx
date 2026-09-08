// D-122 — baseball-card detail. Red-capable: all four envelope keys render,
// cancer type stays the v1 absence, unknown id is not a guessed row.
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { CANCER_TYPE_ABSENT_COPY } from '../adcCatalog.js'

vi.mock('../api.js', () => ({ getAdc: vi.fn() }))
import { getAdc } from '../api.js'
import AdcCard from './AdcCard.jsx'

const env = (value, extras = {}) => ({
  value,
  source: extras.source ?? 'openFDA Drugs@FDA brand search 2026-09-05',
  as_of: extras.as_of ?? '2026-09-05',
  confidence: extras.confidence ?? 'official',
})

const PADCEV = {
  id: env('enfortumab-vedotin', { confidence: 'derived', source: 'derived INN slug' }),
  inn: env('enfortumab vedotin', { confidence: 'derived' }),
  active_ingredient: env('ENFORTUMAB VEDOTIN'),
  brand_name: env('PADCEV'),
  application_number: env('BLA761137'),
  current_application_approval_date: env('2019-12-18'),
  marketing_status: env('Prescription'),
  sponsor: env('ASTELLAS'),
  antigen: env('NECTIN4', {
    confidence: 'reviewed',
    source: 'data/adc_reference_mapping.csv 2026-07-27',
    as_of: '2026-07-27',
  }),
  uniprot_accession: env('Q96NY8', {
    confidence: 'reviewed',
    source: 'data/adc_reference_mapping.csv 2026-07-27',
    as_of: '2026-07-27',
  }),
  cancer_type: env(['Urothelial cancer', 'Muscle invasive bladder cancer'], {
    confidence: 'reviewed',
    source: 'reviewed reduction of FDA label section 1; openFDA label.json 2026-09-08',
    as_of: '2026-09-08',
  }),
  label_indications_verbatim: env(
    '1 INDICATIONS AND USAGE PADCEV, in combination with pembrolizumab, is indicated '
    + 'for the treatment of adult patients with muscle invasive bladder cancer (MIBC) '
    + 'and locally advanced or metastatic urothelial cancer (la/mUC).',
    { source: 'openFDA SPL label.json 2026-09-08', as_of: '2026-09-08' },
  ),
}

const renderCard = (id = 'enfortumab-vedotin') =>
  render(
    <MemoryRouter>
      <AdcCard id={id} />
    </MemoryRouter>,
  )

beforeEach(() => {
  getAdc.mockReset()
})

describe('AdcCard — D-122 baseball card', () => {
  it('renders every envelope key for a D-119 row', async () => {
    getAdc.mockResolvedValue(PADCEV)
    const { container } = renderCard()
    await waitFor(() => expect(container.textContent).toMatch(/PADCEV/))
    expect(getAdc).toHaveBeenCalledWith('enfortumab-vedotin')
    expect(container.textContent).toMatch(/enfortumab vedotin/)
    expect(container.textContent).toMatch(/BLA761137/)
    expect(container.textContent).toMatch(/NECTIN4/)
    expect(container.textContent).toMatch(/Q96NY8/)
    expect(container.textContent).toMatch(/2019-12-18/)
    expect(container.textContent).toMatch(/ASTELLAS/)
    expect(container.textContent).toMatch(/source: openFDA/)
    expect(container.textContent).toMatch(/as of 2026-09-05/)
    expect(container.textContent).toMatch(/official/)
    expect(container.textContent).toMatch(/reviewed/)
    expect(container.textContent).toMatch(/derived/)
    expect(container.textContent.toLowerCase()).not.toMatch(/\bdar\b|\bic50\b|\borr\b/)
  })

  it('D-136 — renders the tumour types and the label text they were reduced from', async () => {
    getAdc.mockResolvedValue(PADCEV)
    const { container } = renderCard()
    await waitFor(() => expect(container.textContent).toMatch(/PADCEV/))
    expect(screen.getByText('Urothelial cancer')).toBeTruthy()
    expect(screen.getByText('Muscle invasive bladder cancer')).toBeTruthy()
    // ⚠ The list is only trustworthy if the reader can check it. The official
    // text ships on the same card, with its own source / as_of / confidence.
    expect(container.textContent).toMatch(/1 INDICATIONS AND USAGE PADCEV/)
    expect(container.textContent).toMatch(/as of 2026-09-08/)
    expect(container.textContent).not.toMatch(CANCER_TYPE_ABSENT_COPY)
  })

  it('D-136 — a row whose cancer type is a named absence shows that row\'s own reason', async () => {
    const source = 'openFDA SPL label.json for FIXTURE 2026-09-08 returned no indications_and_usage'
    getAdc.mockResolvedValue({
      ...PADCEV,
      cancer_type: env(null, { confidence: 'reviewed', source, as_of: '2026-09-08' }),
      label_indications_verbatim: env(null, { source, as_of: '2026-09-08' }),
    })
    const { container } = renderCard()
    await waitFor(() => expect(container.textContent).toMatch(/PADCEV/))
    expect(container.textContent).toMatch(/returned no indications_and_usage/)
    // The absence is stated, and no tumour type is guessed in its place.
    expect(container.textContent).not.toMatch(/Urothelial cancer/)
  })

  it('D-136 — a payload missing the field entirely says so rather than rendering nothing', async () => {
    const { cancer_type, label_indications_verbatim, ...withoutIndication } = PADCEV
    getAdc.mockResolvedValue(withoutIndication)
    const { container } = renderCard()
    await waitFor(() => expect(container.textContent).toMatch(/PADCEV/))
    expect(container.textContent).toMatch(/Cancer type/)
    expect(container.textContent).toMatch(/not in this payload/)
    expect(container.textContent).not.toMatch(/urothelial/i)
  })

  it('unknown id is not a 200-with-a-guess', async () => {
    getAdc.mockRejectedValue(new Error('/api/adcs/ifinatamab-deruxtecan -> HTTP 404'))
    const { container } = renderCard('ifinatamab-deruxtecan')
    await waitFor(() => expect(container.textContent).toMatch(/Unknown ADC/))
    expect(container.textContent).not.toMatch(/PADCEV|BLA761137|NECTIN4/)
    expect(screen.getByRole('link', { name: /Back to the FDA-approved catalog/ })).toHaveAttribute(
      'href',
      '/adcs',
    )
  })
})
