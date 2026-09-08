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
  cancer_type: env(['Small-cell lung cancer'], {
    source: 'reviewed reduction of this row\'s conditions_verbatim (NCT05280470, 2026-09-08)',
    as_of: '2026-09-08',
  }),
  conditions_verbatim: env('Extensive-stage Small-cell Lung Cancer', {
    source: 'ClinicalTrials.gov GET /studies/NCT05280470 retrieved 2026-09-08',
    as_of: '2026-09-08',
    confidence: 'official',
  }),
  description: env('Daiichi Sankyo/Merck — I-DXd, a CD276-directed conjugate.', {
    source: 'ClinicalTrials.gov NCT05280470 leadSponsor.name = Daiichi Sankyo, 2026-09-08',
    as_of: '2026-09-08',
  }),
}

// ⚠ The preclinical shape: both programme envelopes are a NAMED ABSENCE, and each
// carries the lookup that came back empty. This is half the committed shelf.
const CH10D7 = {
  ...IFINA,
  id: env('ch10d7-mmae', { confidence: 'derived' }),
  name: env('ch10D7-MMAE'),
  antigen: env('CDCP1'),
  development_stage: env('preclinical'),
  phase: env('Other'),
  source_citation: env('Theranostics 2022;12(15):6915; JCO 2023;41:e15012 (TNBC)'),
  cancer_type: {
    value: null,
    source: 'ClinicalTrials.gov query.intr=ch10D7-MMAE retrieved 2026-09-08 returned 0 studies',
    as_of: '2026-09-08',
    confidence: 'reviewed',
  },
  conditions_verbatim: env('Theranostics 2022;12(15):6915; JCO 2023;41:e15012 (TNBC)', {
    as_of: '2026-09-08',
  }),
  description: {
    value: null,
    source: 'no sponsor or assignee named in this row\'s citation, checked 2026-09-08',
    as_of: '2026-09-08',
    confidence: 'reviewed',
  },
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
    // ⚠ D-139 amended this line. It used to assert no tumour string appeared at
    // all, which was right while the pipeline schema admitted none. The claim that
    // survives is the one that mattered: this card must not present an APPROVED
    // indication, and must not borrow the FDA label surface (D-139 decision 6).
    expect(container.textContent).not.toMatch(/urothelial/i)
    expect(container.textContent).not.toMatch(/INDICATIONS AND USAGE/i)
    expect(container.textContent).not.toMatch(/FDA label indications/i)
    expect(container.textContent.toLowerCase()).not.toMatch(/\bdar\b|\bic50\b|\borr\b/)
    expect(screen.getByRole('link', { name: /Pipeline catalog/ })).toHaveAttribute(
      'href',
      '/adcs?shelf=pipeline',
    )
  })

  it('D-139 — the card shows cancer type, description, and the text they came from', async () => {
    getPipelineAdc.mockResolvedValue(IFINA)
    const { container } = renderCard()
    await waitFor(() => expect(container.textContent).toMatch(/ifinatamab deruxtecan/))
    expect(screen.getByRole('heading', { name: 'Programme' })).toBeInTheDocument()
    // ⚠ "Programme", never "Indication": this agent is not approved.
    expect(screen.queryByRole('heading', { name: 'Indication' })).toBeNull()
    expect(screen.getByText('Small-cell lung cancer')).toBeInTheDocument()
    expect(container.textContent).toMatch(/Daiichi Sankyo\/Merck — I-DXd/)
    expect(container.textContent).toMatch(/Extensive-stage Small-cell Lung Cancer/)
    expect(container.textContent).toMatch(/Cancer type \(under study\)/)
    expect(container.textContent).toMatch(/studied in/)
    expect(container.textContent).toMatch(/NCT05280470/)
    expect(container.textContent).not.toMatch(/proteinatlas|quasi.H|staining/i)
  })

  it('D-139 — a row with neither states which lookup came back empty, not a blank', async () => {
    getPipelineAdc.mockResolvedValue(CH10D7)
    const { container } = renderCard('ch10d7-mmae')
    await waitFor(() => expect(container.textContent).toMatch(/ch10D7-MMAE/))
    expect(container.textContent).toMatch(/query.intr=ch10D7-MMAE retrieved 2026-09-08 returned 0 studies/)
    expect(container.textContent).toMatch(/no sponsor or assignee named/)
    // ⚠ Scoped to the Programme section, not the page: the Access panel in this
    // fixture legitimately renders "not in this payload" for fields it was not
    // given, and a page-wide match would pass for the wrong reason.
    const programme = screen.getByRole('heading', { name: 'Programme' }).closest('section')
    expect(programme.textContent).not.toMatch(/not in this payload/)
  })

  it('D-139 — a payload missing a programme envelope says so instead of vanishing', async () => {
    const { cancer_type: _ct, ...withoutCancerType } = IFINA
    getPipelineAdc.mockResolvedValue(withoutCancerType)
    const { container } = renderCard()
    await waitFor(() => expect(container.textContent).toMatch(/ifinatamab deruxtecan/))
    expect(container.textContent).toMatch(/not in this payload/)
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
