// D-124 — Access panel. Red-capable: the only source is GET /api/adcs/access.
// Failed / empty payloads stay empty. No invented NCT or eligibility copy.
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, waitFor } from '@testing-library/react'

vi.mock('../api.js', () => ({ getAdcAccess: vi.fn() }))
import { getAdcAccess } from '../api.js'
import AdcAccessPanel from './AdcAccessPanel.jsx'

const env = (value, extras = {}) => ({
  value,
  source: extras.source ?? 'fixture',
  as_of: extras.as_of ?? '2026-09-05',
  confidence: extras.confidence ?? 'official',
})

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
  named_nct_ids_from_pipeline: env(['NCT03310957'], { confidence: 'reviewed' }),
}

beforeEach(() => {
  getAdcAccess.mockReset()
})

describe('AdcAccessPanel — D-124', () => {
  it('Access panel surfaces the A disclaimer and named NCT ids', async () => {
    getAdcAccess.mockResolvedValue(ACCESS)
    const { container } = render(<AdcAccessPanel />)
    await waitFor(() => expect(container.textContent).toMatch(/NOT medical advice/))
    expect(getAdcAccess).toHaveBeenCalled()
    expect(container.textContent).toMatch(/NOT legal advice/)
    expect(container.textContent).toMatch(/NOT a treatment recommendation/)
    expect(container.textContent).toMatch(/NCT03310957/)
    expect(container.textContent).toMatch(/360bbb-0a/)
    expect(container.textContent).toMatch(/Pub. L. 115-176/)
    expect(container.textContent.toLowerCase()).not.toMatch(/\benroll now\b|\byou are eligible\b/)
  })

  it('sourced fields render ProvenanceField envelopes, including the disclaimer', async () => {
    getAdcAccess.mockResolvedValue(ACCESS)
    const { container } = render(<AdcAccessPanel />)
    await waitFor(() => expect(container.textContent).toMatch(/Disclaimer/))
    expect(container.textContent).toMatch(/source: fixture/)
    expect(container.textContent).toMatch(/as of 2026-09-05/)
    expect(container.textContent).toMatch(/reviewed/)
    expect(container.textContent).toMatch(/official/)
    expect(container.textContent).toMatch(/derived/)
    const disclaimerDt = [...container.querySelectorAll('dt')]
      .find((el) => el.textContent === 'Disclaimer')
    expect(disclaimerDt).toBeTruthy()
    const disclaimerDd = disclaimerDt.nextElementSibling
    expect(disclaimerDd.textContent).toMatch(/NOT medical advice/)
    expect(disclaimerDd.textContent).toMatch(/source:/)
    expect(disclaimerDd.textContent).toMatch(/as of/)
    expect(disclaimerDd.textContent).toMatch(/reviewed/)
  })

  it('failed access fetch is an honest miss, not invented NCT copy', async () => {
    getAdcAccess.mockRejectedValue(new Error('/api/adcs/access -> HTTP 500'))
    const { container } = render(<AdcAccessPanel />)
    await waitFor(() => expect(container.textContent).toMatch(/could not be loaded/))
    expect(container.textContent).not.toMatch(/NCT03310957|NCT04032704|NCT02529553/)
    expect(container.textContent).not.toMatch(/you should request|eligible patients must/i)
  })

  it('empty NCT list is an absence in this file, not a census of trials', async () => {
    getAdcAccess.mockResolvedValue({
      ...ACCESS,
      named_nct_ids_from_pipeline: env([], { confidence: 'reviewed' }),
    })
    const { container } = render(<AdcAccessPanel />)
    await waitFor(() => expect(container.textContent).toMatch(/names no NCT identifiers/))
    expect(container.textContent).not.toMatch(/NCT0/)
  })

  it('missing link fields render as not-in-this-payload, not guessed URLs', async () => {
    getAdcAccess.mockResolvedValue({
      disclaimer: ACCESS.disclaimer,
      named_nct_ids_from_pipeline: env([], { confidence: 'reviewed' }),
    })
    const { container } = render(<AdcAccessPanel />)
    await waitFor(() => expect(container.textContent).toMatch(/not in this payload/))
    expect(container.textContent).not.toMatch(/clinicaltrials.gov/)
    expect(container.querySelector('a[href*="clinicaltrials.gov"]')).toBeNull()
  })
})
