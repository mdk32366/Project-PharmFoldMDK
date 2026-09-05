// D-124 — pipeline baseball card. Red-capable: GET /api/adcs/pipeline/{id}.
// Unknown id is not a guessed row. No invented indication / DAR.
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

vi.mock('../api.js', () => ({
  getPipelineAdc: vi.fn(),
  getAdcAccess: vi.fn(),
}))
import { getPipelineAdc, getAdcAccess } from '../api.js'
import AdcPipelineCard from './AdcPipelineCard.jsx'

const env = (value, extras = {}) => ({
  value,
  source: extras.source ?? 'data/adc_reference_mapping.csv 2026-07-27',
  as_of: extras.as_of ?? '2026-07-27',
  confidence: extras.confidence ?? 'reviewed',
})

const IFINA = {
  id: env('ifinatamab-deruxtecan', { confidence: 'derived' }),
  name: env('ifinatamab deruxtecan'),
  antigen: env('CD276'),
  uniprot_accession: env('Q5ZPR3'),
  development_stage: env('clinical'),
  phase: env('BLA/NDA submitted'),
  source_citation: env('Daiichi Sankyo/Merck BLA Priority Review 2026-04-13, PDUFA 2026-10-10'),
}

const ACCESS = {
  disclaimer: env(
    'This payload is informational only. It is NOT medical advice, NOT legal advice, and NOT a treatment recommendation.',
    { as_of: '2026-09-05' },
  ),
  named_nct_ids_from_pipeline: env([], { as_of: '2026-07-27' }),
}

const renderCard = (id = 'ifinatamab-deruxtecan') =>
  render(
    <MemoryRouter>
      <AdcPipelineCard id={id} />
    </MemoryRouter>,
  )

beforeEach(() => {
  getPipelineAdc.mockReset()
  getAdcAccess.mockReset()
  getAdcAccess.mockResolvedValue(ACCESS)
})

describe('AdcPipelineCard — D-124 baseball card', () => {
  it('pipeline card renders a D-124 row; unknown id is not a 200-with-a-guess', async () => {
    getPipelineAdc.mockResolvedValue(IFINA)
    const { container } = renderCard()
    await waitFor(() => expect(container.textContent).toMatch(/ifinatamab deruxtecan/))
    expect(getPipelineAdc).toHaveBeenCalledWith('ifinatamab-deruxtecan')
    expect(container.textContent).toMatch(/CD276/)
    expect(container.textContent).toMatch(/Q5ZPR3/)
    expect(container.textContent).toMatch(/BLA\/NDA submitted/)
    expect(container.textContent).toMatch(/clinical/)
    expect(container.textContent).toMatch(/source:/)
    expect(container.textContent).toMatch(/as of 2026-07-27/)
    expect(container.textContent).not.toMatch(/urothelial|small.cell lung/i)
    expect(container.textContent.toLowerCase()).not.toMatch(/\bdar\b|\bic50\b|\borr\b/)
    expect(screen.getByRole('link', { name: /Pipeline catalog/ })).toHaveAttribute(
      'href',
      '/adcs?shelf=pipeline',
    )
  })

  it('unknown id is not a 200-with-a-guess', async () => {
    getPipelineAdc.mockRejectedValue(new Error('/api/adcs/pipeline/enfortumab-vedotin -> HTTP 404'))
    const { container } = renderCard('enfortumab-vedotin')
    await waitFor(() => expect(container.textContent).toMatch(/Unknown pipeline ADC/))
    expect(container.textContent).not.toMatch(/ifinatamab|CD276|PADCEV/)
    expect(screen.getByRole('link', { name: /Back to the pipeline catalog/ })).toHaveAttribute(
      'href',
      '/adcs?shelf=pipeline',
    )
  })
})
