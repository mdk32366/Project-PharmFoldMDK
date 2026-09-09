// D-149 — the cancer burden surface. ⚠ Every test here is red-capable against a specific way the
// page could lie: dropping the US-only qualifier, relabelling melanoma as "skin cancer", ordering
// incidence by count, rendering a GLOBOCAN figure, or leaking a protein/score into a disease surface.
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, waitFor, screen, fireEvent } from '@testing-library/react'

vi.mock('../api.js', () => ({ getCancerBurden: vi.fn() }))
import { getCancerBurden } from '../api.js'
import CancerBurdenView from './CancerBurdenView.jsx'

const META = {
  us_only: 'United States only. These are US figures: SEER reports US cancer statistics and '
    + 'nothing here describes cancer burden in any other country.',
  us_only_short: 'US only — SEER/NCI',
  geography: 'united_states',
  attribution: 'Data source: SEER*Explorer, Surveillance Research Program, National Cancer '
    + 'Institute. Credit the National Cancer Institute as the source.',
  attribution_url: 'https://seer.cancer.gov/statistics-network/explorer/',
  release: 'SEER November 2025 Submission',
  release_updated: '2026-04-22',
  source_file: 'data/burden/seer_us_cancer_burden.v1.csv',
  source_sha256: 'ed4ad60975699ed74d6d5c1e18a0d3372e85c005e249dee7e6b11605cd070e60',
  site_vocabulary: 'SEER Site Recode ICD-O-3/WHO 2008',
  separation: 'This is a DISEASE-level surface and it is joined to nothing.',
  deep_learning_position: 'This surface runs no model and adds no deep learning.',
  skin_exclusion: "SEER's site-recode group is literally named 'Skin excluding Basal and "
    + "Squamous'. Basal-cell and squamous-cell carcinoma are NOT reportable to SEER.",
  globocan: 'No GLOBOCAN / IARC figure is ingested or rendered, and worldwide burden is therefore '
    + 'ABSENT rather than zero.',
  excluded_product: 'SEER Preliminary Incidence Estimates are NOT used.',
  excluded_tier: 'SEER Research Data / Research Plus (case-level microdata) is NOT used.',
  crosswalk_refused: 'No crosswalk from this surface to HPA tumour strings is offered.',
  count_population_key: {
    seer_registries: {
      text: 'New cases within the SEER registry catchment areas ONLY — not the whole United States.',
    },
  },
  population_key: {
    sex: { text: "The sex the SOURCE returned, never the sex requested." },
  },
}

const row = (over) => ({
  statistic: 'mortality',
  seer_site_id: 47,
  site_label: 'Lung and Bronchus',
  display_label: 'Lung and Bronchus',
  recode_group: 'Respiratory System',
  sex: 'both',
  sex_substituted: false,
  rate_per_100k: 30.230132,
  rate_lower_ci: 30.156369,
  rate_upper_ci: 30.304043,
  observed_count: 662721,
  count_population: 'us_total_nchs',
  period: '2020-2024',
  rate_basis: 'us_mortality_age_adjusted_per_100k',
  is_context_row: false,
  is_primary_sex_stratum: true,
  rank_within_statistic: 1,
  rank_basis: 'observed_count',
  disclaimer: 'US only — SEER/NCI',
  ...over,
})

const MORTALITY = {
  result_status: 'valid',
  meta: META,
  run: { id: 1 },
  n_stats: 4,
  rows: [
    row({}),
    row({ seer_site_id: 40, site_label: 'Pancreas', display_label: 'Pancreas',
          rate_per_100k: 11.26, observed_count: 243780, rank_within_statistic: 2 }),
    // ⚠ the sex-substituted row: breast is published per-sex and "Both Sexes" returns MALE
    row({ seer_site_id: 55, site_label: 'Breast', display_label: 'Breast (female)', sex: 'female',
          sex_substituted: true, rate_per_100k: 18.928734, observed_count: 212409,
          rank_within_statistic: 3 }),
    row({ seer_site_id: 53, site_label: 'Melanoma of the Skin',
          display_label: 'Melanoma of the Skin', rate_per_100k: 2.005706, observed_count: 41702,
          rank_within_statistic: 4 }),
    row({ seer_site_id: 1, site_label: 'All Cancer Sites Combined',
          display_label: 'All Cancer Sites Combined', rate_per_100k: 143.198025,
          observed_count: 3049139, is_context_row: true, rank_within_statistic: null,
          rank_basis: null, not_ranked_because: 'all_cancer_sites_combined_is_a_denominator' }),
  ],
}

const INCIDENCE = {
  result_status: 'valid',
  meta: META,
  run: { id: 1 },
  n_stats: 2,
  rows: [
    // ⚠⚠ THE ORDER THAT PROVES THE BASIS. Breast is FIRST on rate (132.5 vs 47.2) while lung has
    // the larger COUNT (434,448 vs 603,016 — no: lung's count is smaller here on purpose, so a
    // component that silently ranked incidence by count would produce a different first row).
    row({ statistic: 'incidence', seer_site_id: 55, site_label: 'Breast',
          display_label: 'Breast (female)', sex: 'female', sex_substituted: true,
          rate_per_100k: 132.529813, observed_count: 603016,
          count_population: 'seer_registries', period: '2019-2023',
          rate_basis: 'observed_seer_incidence_age_adjusted_per_100k',
          rank_within_statistic: 1, rank_basis: 'rate_per_100k' }),
    row({ statistic: 'incidence', rate_per_100k: 47.172044, observed_count: 434448,
          count_population: 'seer_registries', period: '2019-2023',
          rate_basis: 'observed_seer_incidence_age_adjusted_per_100k',
          rank_within_statistic: 2, rank_basis: 'rate_per_100k' }),
  ],
}

beforeEach(() => {
  getCancerBurden.mockReset()
})

describe('CancerBurdenView — D-149', () => {
  it('answers the deaths question first, ordered by national count', async () => {
    getCancerBurden.mockResolvedValue(MORTALITY)
    const { container } = render(<CancerBurdenView />)
    await waitFor(() => expect(container.textContent).toMatch(/Lung and Bronchus/))
    expect(getCancerBurden).toHaveBeenCalledWith('mortality')
    expect(container.textContent).toMatch(/Which cancers kill the most people in the US\?/)
    // 662,721 formatted with separators — the figure, not a rounded story about it
    expect(container.textContent).toMatch(/662,721/)
    const labels = [...container.querySelectorAll('.burden-table tbody tr td:nth-child(2)')]
      .map((td) => td.textContent.trim())
    expect(labels[0]).toMatch(/^Lung and Bronchus/)
    expect(labels[1]).toMatch(/^Pancreas/)
  })

  it('⚠ US-only rides on the banner, on every bar, and in the limits — never only a tooltip', async () => {
    getCancerBurden.mockResolvedValue(MORTALITY)
    const { container } = render(<CancerBurdenView />)
    await waitFor(() => expect(container.textContent).toMatch(/662,721/))
    expect(screen.getByTestId('burden-us-only').textContent).toMatch(/United States only/)
    // ⚠ EVERY bar carries the badge. A page-level banner alone is lost the moment one row is
    // screenshotted out of the list.
    const bars = [...container.querySelectorAll('.burden-bar-row')]
    expect(bars.length).toBeGreaterThan(0)
    // ⚠ A-016: assert PRESENCE before reading it, so deleting the badge fails at an assertion
    // rather than raising a TypeError. An error-red and a failure-red are different objects.
    const badges = bars.map((bar) => bar.querySelector('.burden-bar-badge'))
    expect(badges.filter(Boolean)).toHaveLength(bars.length)
    for (const badge of badges) {
      expect(badge.textContent).toMatch(/US only/)
    }
    expect(container.querySelector('.burden-table caption').textContent)
      .toMatch(/United States only/)
  })

  it('⚠⚠ never calls SEER melanoma "skin cancer", and names the BCC/SCC exclusion on that row',
     async () => {
    getCancerBurden.mockResolvedValue(MORTALITY)
    const { container } = render(<CancerBurdenView />)
    await waitFor(() => expect(container.textContent).toMatch(/Melanoma of the Skin/))
    const note = screen.getByTestId('burden-skin-note')
    expect(note.textContent).toMatch(/basal-? and squamous-cell/i)
    expect(note.textContent).toMatch(/most skin cancers/i)
    // ⚠⚠ THE PROPERTY THAT MATTERS: the LABEL is SEER's own name, and every occurrence of the
    // phrase "skin cancer" anywhere on the page lives inside the refusal note. Counting
    // occurrences would not have caught a relabelled header; locating them does.
    const labels = [...container.querySelectorAll('.burden-table tbody tr td:nth-child(2)')]
    const skinCell = labels.find((td) => /Melanoma of the Skin/.test(td.textContent))
    expect(skinCell).toBeTruthy()
    expect(skinCell.firstChild.textContent.trim()).toBe('Melanoma of the Skin')
    for (const el of container.querySelectorAll('*')) {
      if (el.children.length) continue          // leaf nodes only
      if (!/skin cancer/i.test(el.textContent)) continue
      expect(el.closest('.burden-skin-note, .burden-limits')).toBeTruthy()
    }
  })

  it('⚠⚠ per-row count population is rendered, so the two counts are never invited into a comparison',
     async () => {
    getCancerBurden.mockResolvedValue(MORTALITY)
    const { container } = render(<CancerBurdenView />)
    await waitFor(() => expect(container.textContent).toMatch(/662,721/))
    expect(container.textContent).toMatch(/whole US \(NCHS\)/)
    expect(container.querySelector('.burden-table thead').textContent).toMatch(/Counted in/)
  })

  it('the incidence toggle switches the statistic AND the stated ranking basis', async () => {
    getCancerBurden.mockImplementation((s) =>
      Promise.resolve(s === 'incidence' ? INCIDENCE : MORTALITY))
    const { container } = render(<CancerBurdenView />)
    await waitFor(() => expect(container.textContent).toMatch(/662,721/))
    fireEvent.click(screen.getByRole('button', { name: 'New cases' }))
    await waitFor(() => expect(container.textContent)
      .toMatch(/Which cancers are diagnosed most in the US\?/))
    expect(getCancerBurden).toHaveBeenCalledWith('incidence')
    // ⚠⚠ ordered by RATE, and the caption says why — a count order would rank a registry-area
    // number as though it were national.
    const caption = container.querySelector('.burden-table caption').textContent
    expect(caption).toMatch(/age-adjusted rate per 100,000/)
    expect(caption).toMatch(/registry catchment areas only/)
    const labels = [...container.querySelectorAll('.burden-table tbody tr td:nth-child(2)')]
      .map((td) => td.textContent.trim())
    expect(labels[0]).toMatch(/^Breast \(female\)/)
    expect(container.textContent).toMatch(/SEER registry areas only/)
  })

  it('⚠ breast is labelled with its sex and the substitution is disclosed', async () => {
    getCancerBurden.mockResolvedValue(MORTALITY)
    const { container } = render(<CancerBurdenView />)
    await waitFor(() => expect(container.textContent).toMatch(/212,409/))
    // never a bare "Breast" carrying the female-only figure
    expect(container.textContent).toMatch(/Breast \(female\)/)
    const disclosure = screen.getByTestId('burden-sex-substitution').textContent
    expect(disclosure).toMatch(/not from our question/i)
    expect(disclosure).toMatch(/never the sex requested/i)
    expect(disclosure).toMatch(/1 row\(s\) on this view carry a recorded substitution/)
  })

  it('⚠ All Cancer Sites Combined is shown apart from the sites it contains, never ranked', async () => {
    getCancerBurden.mockResolvedValue(MORTALITY)
    const { container } = render(<CancerBurdenView />)
    await waitFor(() => expect(container.textContent).toMatch(/662,721/))
    const ctx = screen.getByTestId('burden-context').textContent
    expect(ctx).toMatch(/not ranked above/i)
    expect(ctx).toMatch(/3,049,139/)
    // it must NOT be a row of the ranked table
    const labels = [...container.querySelectorAll('.burden-table tbody tr td:nth-child(2)')]
      .map((td) => td.textContent)
    expect(labels.some((l) => /All Cancer Sites Combined/.test(l))).toBe(false)
  })

  it('⚠⚠ GLOBOCAN appears only as a stated refusal, never as a figure', async () => {
    getCancerBurden.mockResolvedValue(MORTALITY)
    const { container } = render(<CancerBurdenView />)
    await waitFor(() => expect(container.textContent).toMatch(/662,721/))
    const globocan = screen.getByTestId('burden-globocan').textContent
    expect(globocan).toMatch(/No worldwide figures/)
    expect(globocan).toMatch(/ABSENT rather than zero/)
    // no worldwide figure anywhere on the page
    expect(container.textContent).not.toMatch(/world(wide)? (incidence|mortality|deaths) of/i)
  })

  it('⚠ NCI attribution and the pinned release are on the page', async () => {
    getCancerBurden.mockResolvedValue(MORTALITY)
    const { container } = render(<CancerBurdenView />)
    await waitFor(() => expect(container.textContent).toMatch(/662,721/))
    expect(screen.getByTestId('burden-attribution').textContent)
      .toMatch(/Credit the National Cancer Institute as the source/)
    expect(container.textContent).toMatch(/SEER November 2025 Submission/)
    expect(container.textContent).toMatch(/2026-04-22/)
  })

  it('⚠⚠ no protein, accession, gene, score or rank reaches this disease surface', async () => {
    getCancerBurden.mockResolvedValue(MORTALITY)
    const { container } = render(<CancerBurdenView />)
    await waitFor(() => expect(container.textContent).toMatch(/662,721/))
    const text = container.textContent
    expect(text).not.toMatch(/structural_score/)
    expect(text).not.toMatch(/\bplddt\b/i)
    // an accession-shaped token (P11717 / Q96NY8) must never appear here
    expect(text).not.toMatch(/\b[OPQ][0-9][A-Z0-9]{3}[0-9]\b/)
    expect(container.querySelector('a[href*="/census/"]')).toBeNull()
    expect(container.querySelector('a[href*="/target/"]')).toBeNull()
  })

  it('⚠ not_run is a stated category with the disclaimer still on screen, never a blank page',
     async () => {
    getCancerBurden.mockResolvedValue({
      result_status: 'not_run', meta: META, run: null, n_stats: 0, rows: [],
    })
    const { container } = render(<CancerBurdenView />)
    await waitFor(() => expect(container.textContent).toMatch(/No burden run is loaded/))
    expect(screen.getByTestId('burden-not-run').textContent)
      .toMatch(/Nothing is being estimated in its place/)
    expect(screen.getByTestId('burden-us-only').textContent).toMatch(/United States only/)
    expect(container.querySelector('.burden-table')).toBeNull()
  })
})
