// ⚠⚠ D-152 — THE CENSUS TREATMENT ON THE OTHER FIVE LIST SURFACES.
//
// Owner, 2026-09-09: *"Apply what was done for Census to the rest of the surfaces. 100 percent
// better and easier to navigate."*
//
// ⚠⚠ THE SAME LIMIT `CensusLayout.d151.test.jsx` OPENS WITH, AND IT IS WHY THESE ASSERTIONS TAKE
// THE SHAPE THEY DO. **jsdom computes no layout.** Nothing here has a width, a height, a scroll
// offset or a viewport, so no assertion below measures a gutter, a fold or an overflow — one that
// claimed to would be comparing zero with zero and passing. The before/after figures live in
// `### D-152` and come from a headless-Chrome run that no gate re-runs.
//
// ⚠ So these are STRUCTURAL GUARANTEES: the DOM order, the containers the CSS attaches to, and the
// blocks a ruling forbids from collapsing. They cannot prove a page looks right. They redden the
// moment the structure that makes it look right is removed — a scroll port deleted, a disclosure
// defaulted to `open`, a claim moved inside one, a table left outside a port.
//
// ⚠⚠ AND ONE THING THEY GUARD THAT IS NOT LAYOUT AT ALL: **a filter must not be able to move a
// number.** Three of these surfaces gained a search box in this ship, and on each of them there was
// a statistic a naive filter would have rewritten — the scorer's published score distribution, the
// burden chart's bar scale, and the burden table's rank. Those are the cases that would ship a lie
// rather than an ugly page, so they are asserted first among the behaviour tests.
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

vi.mock('../api.js', () => ({
  listAnalyses: vi.fn(),
  getCoverage: vi.fn(),
  getAssociations: vi.fn(),
  getRanking: vi.fn(),
  getCensusSummary: vi.fn(),
  getCancerBurden: vi.fn(),
  listAdcs: vi.fn(),
  listPipelineAdcs: vi.fn(),
  getAdcAccess: vi.fn(),
}))
import {
  listAnalyses, getCoverage, getAssociations, getRanking, getCensusSummary,
  getCancerBurden, listAdcs, listPipelineAdcs, getAdcAccess,
} from '../api.js'

import TargetList from './TargetList.jsx'
import CoverageView from './CoverageView.jsx'
import ScorerView from './ScorerView.jsx'
import CancerBurdenView from './CancerBurdenView.jsx'
import AdcsView from './AdcsView.jsx'

const CSS = readFileSync(
  resolve(dirname(fileURLToPath(import.meta.url)), '../styles.css'), 'utf-8',
)

// ── fixtures ────────────────────────────────────────────────────────────────────────────────────
const ANALYSES = [
  // ⚠ `aliases` is what `/api/analyses` actually serves (the pinned UniProt cache), and it is what
  // makes `HER2` reach `ERBB2` — the search this list exists because of.
  { id: 1, accession: 'P04626', gene: 'ERBB2', mean_plddt: 77.26, tier: 'local',
    aliases: ['HER2', 'NEU', 'CD340'] },
  { id: 2, accession: 'Q96NY8', gene: 'NECTIN4', mean_plddt: 71.1, tier: 'local',
    aliases: ['PVRL4'] },
]
const COVERAGE = {
  coverage: { denominator: 3, ranked: 2, held_out: 1, excluded: 0, unmeasured_tier: 0, no_topology: 0 },
  rows: [
    { accession: 'P04626', gene: 'ERBB2', protein_name: 'Receptor tyrosine-protein kinase erbB-2',
      disposition: 'ranked', fold_status: 'folded', tier: 'local', analysis_id: 1 },
    { accession: 'Q96NY8', gene: 'NECTIN4', protein_name: 'Nectin-4',
      disposition: 'ranked', fold_status: 'folded', tier: 'local', analysis_id: 2 },
    { accession: 'Q8WXI7', gene: 'MUC16', protein_name: 'Mucin-16', aliases: ['CA-125'],
      disposition: 'held_out', fold_status: 'not_folded', tier: 'rental' },
  ],
}
const ASSOCIATIONS = { cutoff: 150, associations: {}, attributions: {} }
const RANKING = {
  result_status: 'valid',
  result: {
    n_fit_positives: 2, n_ranking_set: 2, plddt_floor: 50, spearman: 0.04, spearman_n: 2,
    distribution: [{ symbol: 'ERBB2', percentile: 0.8 }],
    headto_structural: [0.8], headto_evidence: [0.75],
    excluded: [['MUC16', 'mucin, out of class']],
    loo_status: 'complete', paper_published_count: 22,
  },
  rows: [
    { accession: 'P04626', gene: 'ERBB2', rank: 1, score: 0.28 },
    { accession: 'Q96NY8', gene: 'NECTIN4', rank: 2, score: 0.21 },
  ],
}
const BURDEN = {
  result_status: 'valid',
  meta: {
    release: 'SEER Nov 2025', release_updated: '2026-04-22', site_vocabulary: 'ICD-O-3',
    us_only: 'US figures only.', skin_exclusion: 'melanoma only',
    globocan: 'not served', excluded_product: 'n/a', excluded_tier: 'n/a',
    separation: 'joined to nothing', deep_learning_position: 'none here',
    crosswalk_refused: 'refused', attribution: 'SEER', attribution_url: 'https://seer.cancer.gov',
    count_population_key: { seer_registries: { text: 'registry areas only' } },
    population_key: { rate_denominator: { text: 'per 100k of that sex' }, sex: { text: 'source sex' } },
  },
  rows: [
    { seer_site_id: 1, sex: 'both', display_label: 'Lung and Bronchus', rank_within_statistic: 1,
      rank_basis: 'count', observed_count: 662721, rate_per_100k: 47.17, period: '2020-2024',
      count_population: 'us_total_nchs', rate_denominator_label: 'all persons', disclaimer: 'US only' },
    { seer_site_id: 2, sex: 'both', display_label: 'Pancreas', rank_within_statistic: 3,
      rank_basis: 'count', observed_count: 243780, rate_per_100k: 11.2, period: '2020-2024',
      count_population: 'us_total_nchs', rate_denominator_label: 'all persons', disclaimer: 'US only' },
  ],
}
// ⚠ The catalog's real envelope shape — `{ value, source, as_of, confidence }` per field, and the
// field NAMES the loader reads (`brand_name`, `antigen`, `uniprot_accession`). A fixture that
// invented flatter keys would render two empty rows and every assertion below would be about
// nothing, which is `F-054`'s shape in a test file.
const env = (value) => ({ value, source: 'fixture', as_of: '2026-09-05', confidence: 'official' })
const adcRow = (id, brand, antigen, accession, cancerTypes) => ({
  id: env(id), inn: env(id.replace(/-/g, ' ')), brand_name: env(brand),
  antigen: env(antigen), uniprot_accession: env(accession), cancer_type: env(cancerTypes),
})
const ADCS = {
  scope: env('fda_approved_only'),
  completeness: env('floor_not_census'),
  approvals_reconciled_as_of: env('2026-09-05'),
  indications_reviewed_as_of: env('2026-09-08'),
  named_exclusions: env([{ id: 'lumoxiti', reason: 'radioimmunoconjugate — not an ADC' }]),
  adcs: [
    adcRow('brentuximab-vedotin', 'ADCETRIS', 'TNFRSF8', 'P28908', ['Classical Hodgkin lymphoma']),
    adcRow('fam-trastuzumab-deruxtecan', 'ENHERTU', 'ERBB2', 'P04626', ['Breast cancer']),
  ],
}

const draw = (el) => render(<MemoryRouter>{el}</MemoryRouter>)

beforeEach(() => {
  vi.clearAllMocks()
  listAnalyses.mockResolvedValue(ANALYSES)
  getCoverage.mockResolvedValue(COVERAGE)
  getAssociations.mockResolvedValue(ASSOCIATIONS)
  getRanking.mockResolvedValue(RANKING)
  getCensusSummary.mockResolvedValue(null)
  getCancerBurden.mockResolvedValue(BURDEN)
  listAdcs.mockResolvedValue(ADCS)
  listPipelineAdcs.mockResolvedValue({ header: {}, pipeline: [] })
  getAdcAccess.mockResolvedValue({})
})

const follows = (a, b) =>
  Boolean(a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING)

// ── 1 · The primitives are shared, not copied ───────────────────────────────────────────────────
describe('D-152 — one disclosure and one scroll port, defined once', () => {
  // ⚠⚠ THE POINT OF READING THE STYLESHEET RATHER THAN THE MARKUP: five copies of these
  // declarations would look identical on the day they were written and diverge on the first tweak.
  // That is `F-052` — a convention obeyed everywhere except the newest caller — and it is exactly
  // what a component test cannot see, because every surface would still render correctly.
  it('the shared classes exist and the census names ride in the same rules', () => {
    expect(CSS.length).toBeGreaterThan(1000)      // the read reached real bytes
    expect(CSS).toMatch(/\.surface-notes, \.census-background, \.census-notes \{/)
    expect(CSS).toMatch(/\.table-scroll,\s*\n\.census-table-scroll \{/)
    // ⚠ and D-151's own rule is still readable exactly as its guards read it
    expect(CSS).toMatch(/\.census-table-scroll \{[^}]*overflow:\s*auto/)
    expect(CSS).toMatch(/\.census-table-scroll \{[^}]*max-height/)
  })

  it('the sticky header is written against the shared port, so a sixth list inherits it', () => {
    expect(CSS).toMatch(/\.table-scroll thead th \{[^}]*position:\s*sticky/)
    expect(CSS).toMatch(/\.table-scroll thead th \{[^}]*top:\s*0/)
  })

  // ⚠ `.row-search` had NO rule at all on `41b9b3b` — `TargetList` rendered the class and the
  // stylesheet never mentioned it, so the box drew as a native browser default on a dark page.
  it('the list search box is styled, on every surface that has one', () => {
    expect(CSS).toMatch(/^\.row-search \{/m)
    expect(CSS).toMatch(/\.row-search \{[^}]*background/)
  })

  // ⚠⚠ THE TOOLTIP FIX, BARRED BY NAME RATHER THAN REMEMBERED. `visibility: hidden` still LAYS THE
  // BOX OUT, so 320px of closed tooltip was enlarging the document — measured at 144px of standing
  // horizontal overflow on `/scorer` once the page was wide enough to expose it.
  it('a closed term tooltip is not laid out, so it cannot widen the document', () => {
    const block = CSS.match(/\.term-def \{([^}]*)\}/)[1]
    expect(block).toMatch(/display:\s*none/)
    expect(block).not.toMatch(/visibility:\s*hidden/)
    expect(CSS).toMatch(/\.term:hover \.term-def[^{]*\{[^}]*display:\s*block/)
  })
})

// ── 2 · Every list route puts its table in a port ───────────────────────────────────────────────
describe('D-152 — the table scrolls, the page does not', () => {
  const cases = [
    ['/targets', () => draw(<TargetList />)],
    ['/coverage', () => draw(<CoverageView />)],
    ['/scorer', () => draw(<ScorerView />)],
    ['/cancer-burden', () => draw(<CancerBurdenView />)],
    ['/adcs', () => draw(<AdcsView />)],
  ]

  for (const [route, mount] of cases) {
    it(`${route} wraps its primary table in a bounded scroll port`, async () => {
      const { container } = mount()
      // ⚠ `findAllByRole`: `/scorer` renders three tables (the distribution, the head-to-head and
      // the ranking), and only the last of them is a LIST. A singular query would throw there for
      // a reason that has nothing to do with the claim under test.
      await screen.findAllByRole('table')
      const port = container.querySelector('.table-scroll')
      expect(port, `${route} lost its scroll port — the table can widen the document again`)
        .toBeTruthy()
      const table = port.querySelector('table')
      expect(table, `${route}'s table is outside the port`).toBeTruthy()
      // ⚠ the header must be INSIDE the port: `position: sticky` resolves against the nearest
      // scrollport ancestor, so a `<thead>` outside it sticks to nothing.
      expect(port.querySelector('thead th')).toBeTruthy()
    })
  }
})

// ── 3 · The search comes before the prose, and the prose is collapsed not cut ───────────────────
describe('D-152 — the search and the table come before the explanations', () => {
  it('/targets — the controls precede the column note, which is a collapsed disclosure', async () => {
    const { container } = draw(<TargetList />)
    await screen.findByRole('table')
    const controls = container.querySelector('.list-controls')
    const notes = container.querySelector('details.surface-notes')
    const table = container.querySelector('table')
    expect(controls && notes && table).toBeTruthy()
    expect(follows(controls, notes)).toBe(true)
    expect(follows(notes, table)).toBe(true)
    // ⚠⚠ COLLAPSED BY DEFAULT. An `open` default restores the exact scroll it was collapsed to end
    // while looking like a fix, so the ABSENCE of the attribute is the assertion.
    expect(notes.hasAttribute('open')).toBe(false)
    // ⚠ and the note MOVED rather than being deleted — every word is still rendered
    expect(notes.querySelector('.column-scope-note')).toBeTruthy()
    expect(notes.textContent).toMatch(/no sort control/)
    expect(notes.textContent).toMatch(/not causation/)
  })

  it('/targets — the page finally has a heading, and it agrees with the menu', async () => {
    draw(<TargetList />)
    await screen.findByRole('table')
    // ⚠ D-151 ruled the nav label; a page reached from that entry must not disagree with it.
    expect(screen.getByRole('heading', { level: 2 }).textContent).toMatch(/Initial Targets/)
  })

  it('/adcs — the lede, the dates and the named exclusions moved into one disclosure', async () => {
    const { container } = draw(<AdcsView />)
    await screen.findByRole('table')
    const notes = container.querySelector('details.surface-notes.adcs-notes')
    expect(notes).toBeTruthy()
    expect(notes.hasAttribute('open')).toBe(false)
    expect(notes.querySelector('.lede')).toBeTruthy()
    expect(notes.querySelector('.adcs-provenance')).toBeTruthy()
    // ⚠⚠ THE NAMED EXCLUSIONS ARE STILL RENDERED IN FULL. They are what stops a reader treating
    // this file as the whole field, so the assertion is on the text, not on the container.
    expect(notes.textContent).toMatch(/Named exclusions/)
    expect(notes.textContent).toMatch(/radioimmunoconjugate/)
  })

  it('/scorer — A, B and C collapse and the ranking table leads in source order', async () => {
    const { container } = draw(<ScorerView />)
    await screen.findByText(/E · The ranking table/)
    const notes = container.querySelector('details.surface-notes.scorer-background')
    expect(notes).toBeTruthy()
    expect(notes.hasAttribute('open')).toBe(false)
    for (const cls of ['.scorer-cascade', '.scorer-labels', '.scorer-prereg']) {
      expect(notes.querySelector(cls), `${cls} left the page instead of moving`).toBeTruthy()
    }
    // ⚠⚠ SOURCE ORDER, NOT A CSS `order`. A grid `order` moves the box and leaves the reading
    // order — the one a screen reader follows and the one a narrow viewport stacks to — untouched,
    // which is the version of this change that looks fixed and is not.
    const cols = container.querySelector('.scorer-cols')
    expect(cols.children[0].className).toMatch(/scorer-ranking/)
    expect(cols.children[1].className).toMatch(/scorer-explain/)
  })
})

// ── 4 · What may NOT collapse is decided by the rulings ─────────────────────────────────────────
describe('D-152 — the standing claims stay outside every disclosure', () => {
  it('/targets — the fold-confidence claim and the D-151 paper citation are uncollapsed', async () => {
    const { container } = draw(<TargetList />)
    await screen.findByRole('table')
    // ⚠ this surface's version of the census unscored bar: a green dot must not read as a verdict
    // on a target, and a sentence behind a `<summary>` cannot stop it.
    const claim = container.querySelector('.confidence-scope-note')
    expect(claim).toBeTruthy()
    expect(claim.closest('details')).toBeNull()
    // ⚠⚠ AND THE CITATION D-151 SHIPPED PRECISELY SO IT COULD BE REACHED. Collapsing the paper link
    // would undo that entry's whole finding one release later — the primary source of the cohort
    // put back behind a control.
    const cite = container.querySelector('.cohort-paper-cite')
    expect(cite).toBeTruthy()
    expect(cite.closest('details')).toBeNull()
    expect(cite.querySelector('a.cohort-paper-link')).toBeTruthy()
    // ⚠ both are above the disclosure in source order, which is the property that breaks if
    // somebody moves one inside it
    expect(follows(claim, container.querySelector('details.surface-notes'))).toBe(true)
  })

  it('/coverage — the honest denominator leads and the census strip is moved, never collapsed', async () => {
    getCensusSummary.mockResolvedValue({
      manifest_rows: 3467, folded: 2690,
      structure_kinds: [{ kind: 'assembled', label: 'assembled (provisional)', n: 45 }],
    })
    const { container } = draw(<CoverageView />)
    await screen.findByRole('table')
    await waitFor(() => expect(container.querySelector('.census-population')).toBeTruthy())
    const line = container.querySelector('.coverage-line')
    const strip = container.querySelector('.census-population')
    const table = container.querySelector('table')
    // ⚠ D-135's clauses, each still true: below the coverage line, labelled, and not inside a
    // disclosure. What changed is only that the TABLE now comes between them.
    expect(follows(line, strip)).toBe(true)
    expect(follows(table, strip)).toBe(true)
    expect(strip.closest('details')).toBeNull()
    expect(line.closest('details')).toBeNull()
    // ⚠ and the assembled caveat still travels with the chips it qualifies (D-133 am. 1)
    expect(strip.querySelector('.caveat')).toBeTruthy()
  })

  it('/cancer-burden — the US-only bar and the SEER attribution never collapse', async () => {
    const { container } = draw(<CancerBurdenView />)
    await screen.findByRole('table')
    for (const sel of ['.burden-us-only', '.burden-attribution', '.burden-limits']) {
      const el = container.querySelector(sel)
      expect(el, `${sel} left the page`).toBeTruthy()
      expect(el.closest('details'), `${sel} was moved inside a disclosure`).toBeNull()
    }
  })

  it('/adcs — the floor claim stays above the table, uncollapsed', async () => {
    const { container } = draw(<AdcsView />)
    await screen.findByRole('table')
    const floor = container.querySelector('.adcs-floor')
    expect(floor).toBeTruthy()
    expect(floor.closest('details')).toBeNull()
    expect(floor.textContent).toMatch(/not a scientific constant/)
    expect(follows(floor, container.querySelector('details.surface-notes'))).toBe(true)
  })

  it('/scorer — section D, its negative outcomes and its three caveats stay visible', async () => {
    const { container } = draw(<ScorerView />)
    await screen.findByText(/E · The ranking table/)
    const result = container.querySelector('.scorer-result')
    expect(result).toBeTruthy()
    expect(result.closest('details')).toBeNull()
    expect(container.querySelector('.caveats').closest('details')).toBeNull()
    expect(result.textContent).toMatch(/First negative outcome/)
    expect(result.textContent).toMatch(/Second negative outcome/)
  })
})

// ── 5 · A filter narrows a view and may never move a number ─────────────────────────────────────
describe('D-152 — the new search boxes cannot rewrite a statistic', () => {
  it('/scorer — filtering the table does not touch the run it reports', async () => {
    const { container } = draw(<ScorerView />)
    await screen.findByText(/E · The ranking table/)
    const recon = () => container.querySelector('.ranking-reconciliation').textContent
    const before = recon()
    fireEvent.change(screen.getByLabelText('Search'), { target: { value: 'ERBB2' } })
    expect(container.querySelectorAll('.ranking-table tbody tr')).toHaveLength(1)
    // ⚠⚠ THE PUBLISHED NUMBERS DO NOT MOVE. `n_ranking_set` and the score distribution are
    // properties of the pre-registered RUN; a filter that could move them would make the F-004
    // result a function of a text input.
    expect(recon()).toBe(before)
    expect(recon()).toMatch(/the table below shows those 2/)
    // ⚠ and the surface says which of the two numbers is which, rather than leaving the reader to
    // reconcile a table of one row against a line that says two.
    expect(container.querySelector('.filter-count').textContent)
      .toMatch(/The ranking itself is unchanged/)
  })

  it('/cancer-burden — filtering hides bars and never rescales them', async () => {
    const { container } = draw(<CancerBurdenView />)
    await screen.findByRole('table')
    const widths = () => [...container.querySelectorAll('.burden-bar-fill')]
      .map((el) => el.style.width)
    // Lung is the maximum (662,721) and Pancreas is 243,780 of it
    expect(widths()).toEqual(['100%', `${(243780 / 662721) * 100}%`])
    fireEvent.change(screen.getByLabelText('Search'), { target: { value: 'pancreas' } })
    // ⚠⚠ ONE BAR LEFT, AND IT IS STILL 36.8% WIDE. Re-normalising to the filtered maximum would
    // draw a rare cancer at full width the moment a reader typed its name, and a bar chart's whole
    // claim is that length is comparable.
    expect(widths()).toEqual([`${(243780 / 662721) * 100}%`])
  })

  it('/cancer-burden — a filtered table keeps the rank within the statistic', async () => {
    const { container } = draw(<CancerBurdenView />)
    await screen.findByRole('table')
    fireEvent.change(screen.getByLabelText('Search'), { target: { value: 'pancreas' } })
    const cells = [...container.querySelectorAll('tbody tr td:first-child')]
    // ⚠ Pancreas is #3 by deaths and it is the only row on screen. Renumbering the visible rows
    // 1,2,3 would invent a ranking of the reader's search string.
    expect(cells.map((c) => c.textContent)).toEqual(['3'])
    expect(container.querySelector('[data-testid="burden-filter-count"]').textContent)
      .toMatch(/keep the full ranking/)
  })

  it('/coverage — the count states the filter and the denominator refuses to move', async () => {
    const { container } = draw(<CoverageView />)
    await screen.findByRole('table')
    const headline = container.querySelector('.coverage-headline').textContent
    // ⚠ the shared matcher reaches aliases, so the name on the drug label finds the row
    fireEvent.change(screen.getByLabelText('Search'), { target: { value: 'CA-125' } })
    expect(container.querySelectorAll('tbody tr')).toHaveLength(1)
    expect(container.textContent).toMatch(/MUC16/)
    expect(container.querySelector('.coverage-headline').textContent).toBe(headline)
    expect(container.querySelector('.filter-count').textContent)
      .toMatch(/The denominator above is unchanged/)
  })

  it('/adcs — the search finds a row by its drug name, and the count says so', async () => {
    const { container } = draw(<AdcsView />)
    await screen.findByRole('table')
    fireEvent.change(screen.getByLabelText('Search'), { target: { value: 'Enhertu' } })
    expect(container.querySelectorAll('tbody tr')).toHaveLength(1)
    expect(container.textContent).toMatch(/ENHERTU/)
    expect(container.querySelector('.filter-count').textContent).toMatch(/Showing 1 of 2/)
  })

  it('/targets — search and the tier filter both still work above the disclosure', async () => {
    const { container } = draw(<TargetList />)
    await screen.findByRole('table')
    fireEvent.change(screen.getByLabelText('Search'), { target: { value: 'HER2' } })
    // ⚠ the alias index: `HER2` is stored as `ERBB2`, which is the whole reason this box exists.
    // ⚠ Asserted on the TABLE BODY, not on the page text: the lede's own "Start with NECTIN4 →"
    // link is above the controls and is not a row, so a whole-page assertion would have been
    // measuring the wrong thing and passing or failing for the wrong reason.
    const body = container.querySelector('tbody').textContent
    expect(body).toMatch(/ERBB2/)
    expect(body).not.toMatch(/NECTIN4/)
    expect(container.querySelector('.filter-count').textContent).toMatch(/Showing 1 of 3/)
  })
})

// ── 6 · The failure states stay legible ─────────────────────────────────────────────────────────
describe('D-152 — a failed supplier is a statement, not a blank page', () => {
  // ⚠⚠ `/api/cancer-burden` IS 500ING ON THE DEPLOYED APP AS THIS SHIPS. Fixing that is a load/ops
  // matter held elsewhere and deliberately out of scope; what this ship owes it is that the failure
  // renders AS a failure, with the page around it intact.
  it('/cancer-burden keeps its heading, its US-only bar and its toggle when the route fails', async () => {
    getCancerBurden.mockRejectedValue(new Error('/api/cancer-burden -> HTTP 500'))
    const { container } = draw(<CancerBurdenView />)
    await screen.findByText(/HTTP 500/)
    expect(container.querySelector('h2').textContent).toMatch(/US cancer burden/)
    expect(container.querySelector('.burden-us-only')).toBeTruthy()
    expect(container.querySelector('.burden-toggle')).toBeTruthy()
    // ⚠ and it says the request failed rather than rendering an empty table, which would read as
    // "there is no cancer burden data"
    expect(container.querySelector('.error').textContent).toMatch(/Could not load cancer burden/)
    expect(container.querySelector('table')).toBeNull()
  })

  it('/scorer states an unrecognised ranking status instead of throwing', async () => {
    // ⚠ this exact payload — `rows` with no `result` — took the route to a blank page before this
    // ship, and it was what `App.test.jsx`'s fixture was handing it.
    getRanking.mockResolvedValue({ result_status: 'something-new', rows: [] })
    const { container } = draw(<ScorerView />)
    await screen.findByTestId('scorer-unrecognised')
    expect(container.querySelector('h2').textContent).toMatch(/The scorer result/)
    expect(container.textContent).toMatch(/something-new/)
    // ⚠ it reports what it does not know rather than claiming `not_run`, which would be a claim
    expect(container.textContent).toMatch(/not.*a statement that no result exists/s)
  })
})
