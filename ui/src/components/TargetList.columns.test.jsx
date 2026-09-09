// D-143 — the Cancer association and Description columns, and the bound on column one.
//
// ⚠⚠ THE FIELD THAT LOOKED LIKE THE DESCRIPTION WAS THE GENE SYMBOL. `/api/analyses` carries
// `label`, and on THIS population `label` == `gene` on all 82 rows (`data/cohort_82_ecd.csv` keeps
// `label` and `protein_name` in separate columns). On the CENSUS — same key, other population —
// `label` really is the protein name. So the fixtures below deliberately set `label` to the gene
// symbol, the way the live route does, and a Description column reading `label` reddens here.
//
// ⚠⚠ AND THE ASSOCIATION VALUES ARE HPA CONTENT. D-100: Kathad's S3 is a verbatim extract of
// `pathology.tsv`, and the licence words citation as a PRECONDITION of display. So the tests
// below assert the fail-closed direction — no attribution block, no tumour types — as well as the
// presence of the citation, because "renders the value" and "renders it legally" are two claims.
//
// ⚠ The width tripwire reads the STYLESHEET, because `textContent` cannot see layout and jsdom has
// no layout at all. It parses non-comment declarations only: D-141 lost a guard to a check that
// read a whole file and was satisfied by a COMMENT containing the string it wanted (`F-044`'s
// shape), and the prose above `.rank-cause` in this very stylesheet contains `max-width`.
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import fs from 'node:fs'
import path from 'node:path'
import { stripComments } from '../stripComments.js'

vi.mock('../api.js', () => ({
  getCensusSummary: vi.fn(),
  listAnalyses: vi.fn(),
  getCoverage: vi.fn(),
  getRanking: vi.fn(),
  getAssociations: vi.fn(),
}))
import { getAssociations, getCoverage, getRanking, listAnalyses } from '../api.js'
import TargetList from './TargetList.jsx'

// ⚠ `label` is the GENE SYMBOL here, exactly as the live payload serves it.
const ANALYSES = [
  { id: 1, gene: 'NECTIN4', accession: 'Q92729', label: 'NECTIN4', mean_plddt: 77.26, tier: 'local' },
  { id: 5, gene: 'ADAM17', accession: 'P78536', label: 'ADAM17', mean_plddt: 66.4, tier: 'local' },
  { id: 57, gene: 'IGF2R', accession: 'P11717', label: 'IGF2R', mean_plddt: null, tier: 'rental' },
]

// ⚠ `protein_name` is the manifest column the Description column reads — added to /api/coverage by
// D-143 rather than to the light list, whose field set is exact by ruling (D-034 dec 1).
const COVERAGE = {
  rows: [
    { accession: 'Q92729', gene: 'NECTIN4', protein_name: 'Nectin-4', fold_status: 'folded' },
    {
      accession: 'P78536', gene: 'ADAM17', fold_status: 'folded',
      protein_name: 'Disintegrin and metalloproteinase domain-containing protein 17',
    },
    { accession: 'P11717', gene: 'IGF2R', fold_status: 'failed', protein_name: null,
      fail_reason: 'CUDA OOM folding 2491 aa at chunk_size=32' },
  ],
}

const ATTRIB = (gene, ensg) => ({
  primary_publication: {
    citation: 'Uhlén M et al., Tissue-based map of the human proteome, Science (2015)',
    doi: '10.1126/science.1260419',
    url: 'https://doi.org/10.1126/science.1260419',
  },
  website: { name: 'Human Protein Atlas', url: 'https://www.proteinatlas.org' },
  data_credit: 'Human Protein Atlas',
  deep_link: `https://v22.proteinatlas.org/${ensg}-${gene}/pathology`,
  deep_link_absent_reason: null,
})

// ⚠ cutoff 151, not the live 150, so a hardcoded literal in the component cannot pass (D-053 dec 5)
const ASSOCIATIONS = {
  source: 'Kathad S3 (fixture)', method: 'qh', cutoff: 151,
  pair_count: 7, targets_covered: 2, cohort_size: 3, unmatched_symbols: [],
  associations: {
    NECTIN4: [
      { cancer: 'Urothelial cancer', qh_score: 200 },
      { cancer: 'Thyroid cancer', qh_score: 160 },
    ],
    // a tie at the leading score — three of the 82 live targets are in this state
    ADAM17: [
      { cancer: 'Carcinoid', qh_score: 250 },
      { cancer: 'Stomach cancer', qh_score: 250 },
      { cancer: 'Liver cancer', qh_score: 180 },
    ],
    // IGF2R deliberately absent from the map: "no association recorded" must render as a claim
    // about the MAP, not as a blank and not as a dash.
  },
  attributions: {
    NECTIN4: ATTRIB('NECTIN4', 'ENSG00000143217'),
    ADAM17: ATTRIB('ADAM17', 'ENSG00000151694'),
  },
}

const draw = () => render(<MemoryRouter><TargetList /></MemoryRouter>)
const ready = () => waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument())
const headers = () => screen.getAllByRole('columnheader')
const header = (re) => headers().find((h) => re.test(h.textContent))
const rowFor = (gene) => screen.getByText(gene).closest('tr')
const cells = (gene) => [...rowFor(gene).querySelectorAll('td')]

const CSS = stripComments(
  fs.readFileSync(path.resolve(process.cwd(), 'src/styles.css'), 'utf8'),
)
/** Non-comment declarations for one selector, as `prop: value` strings. */
function declarations(selector) {
  const out = []
  const re = new RegExp(`(^|[},])\\s*${selector.replace(/[.\\]/g, '\\$&')}\\s*\\{([^}]*)\\}`, 'g')
  let m
  while ((m = re.exec(CSS)) !== null) {
    for (const d of m[2].split(';')) if (d.trim()) out.push(d.trim())
  }
  return out
}

beforeEach(() => {
  listAnalyses.mockReset()
  getCoverage.mockReset()
  getRanking.mockReset()
  getAssociations.mockReset()
  listAnalyses.mockResolvedValue(ANALYSES)
  getCoverage.mockResolvedValue(COVERAGE)
  getRanking.mockResolvedValue({ rows: [] })
  getAssociations.mockResolvedValue(ASSOCIATIONS)
})

// ── the Description column ───────────────────────────────────────────────────────────────────────
describe('the Description column, and the field it is NOT read from', () => {
  it('renders the manifest protein name, in a column of its own', async () => {
    draw()
    await ready()
    expect(header(/description/i)).toBeTruthy()
    await waitFor(() => expect(
      within(rowFor('NECTIN4')).getByText('Nectin-4')).toBeInTheDocument())
    expect(within(rowFor('ADAM17')).getByText(
      'Disintegrin and metalloproteinase domain-containing protein 17')).toBeInTheDocument()
  })

  it('⚠⚠ does NOT render the payload\'s `label`, which is the gene symbol on this population',
    async () => {
      const { container } = draw()
      await ready()
      await waitFor(() => expect(container.textContent).toMatch(/Nectin-4/))
      // ADAM17's gene cell says ADAM17 once; a Description column reading `label` would repeat it.
      const text = cells('ADAM17')[3].textContent
      expect(text).not.toMatch(/^ADAM17$/)
      expect(text).toMatch(/Disintegrin/)
    })

  it('states a cause when the manifest carries no name — never a bare dash', async () => {
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.textContent).toMatch(/Nectin-4/))
    const cell = cells('IGF2R')[3]
    expect(cell.textContent).not.toBe('—')
    expect(cell.textContent).toMatch(/no protein name/i)
  })

  it('distinguishes "the supplier could not be reached" from "no name recorded"', async () => {
    // ⚠⚠ unknown ≠ none. Collapsing the two would let an ignorance state render as a fact about
    // the target, which is the same class as `null` rendering as `0`.
    getCoverage.mockRejectedValue(new Error('coverage down'))
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.textContent).toMatch(/could not be reached/))
    expect(cells('NECTIN4')[3].textContent).toMatch(/\/api\/coverage could not be reached/)
    expect(container.textContent).not.toMatch(/no protein name for this accession/)
  })

  it('sorts, and the sort actually reorders — a caret over an unchanged order is a no-op', async () => {
    // ⚠⚠ THE REVERT THIS CATCHES: leaving the description inside the cell instead of joining it
    // onto the row. `sortRows` reads `r[key]`, so the header would render a caret and order by
    // `undefined` on every row.
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.textContent).toMatch(/Nectin-4/))
    const genes = () => [...container.querySelectorAll('tbody tr')]
      .map((r) => r.querySelectorAll('td')[1]?.textContent.trim())
    fireEvent.click(header(/description/i).querySelector('button'))
    expect(header(/description/i)).toHaveAttribute('aria-sort', 'ascending')
    // 'Disintegrin…' < 'Nectin-4', and IGF2R has no description so it TRAILS as a category
    expect(genes()).toEqual(['ADAM17', 'NECTIN4', 'IGF2R'])
    fireEvent.click(header(/description/i).querySelector('button'))
    expect(header(/description/i)).toHaveAttribute('aria-sort', 'descending')
    // ⚠ absence is off the axis, not at an end of it — IGF2R trails in BOTH directions
    expect(genes()).toEqual(['NECTIN4', 'ADAM17', 'IGF2R'])
  })

  it('is findable from the page\'s own search box (F-052)', async () => {
    // ⚠ A column of 82 protein names that the surface's search cannot match would be the same
    // finding one more time — the census has searched protein names all along.
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.textContent).toMatch(/Nectin-4/))
    fireEvent.change(screen.getByLabelText('Search'), { target: { value: 'metalloproteinase' } })
    const body = container.querySelector('tbody').textContent
    expect(body).toMatch(/ADAM17/)
    expect(body).not.toMatch(/NECTIN4/)
  })
})

// ── the Cancer association column ────────────────────────────────────────────────────────────────
describe('the Cancer association column', () => {
  it('names the leading tumour type and states how many the map holds', async () => {
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.textContent).toMatch(/Urothelial cancer/))
    const cell = cells('NECTIN4')[4].textContent
    expect(cell).toMatch(/Urothelial cancer/)
    expect(cell).toMatch(/2 tumour types/)
  })

  it('renders EVERY tied type — a tie has no single top', async () => {
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.textContent).toMatch(/Carcinoid/))
    const cell = cells('ADAM17')[4].textContent
    expect(cell).toMatch(/Carcinoid/)
    expect(cell).toMatch(/Stomach cancer/)
    expect(cell).toMatch(/3 tumour types/)
  })

  it('offers the full list on the target\'s own page rather than truncating in the cell', async () => {
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.textContent).toMatch(/Urothelial cancer/))
    const hrefs = [...cells('NECTIN4')[4].querySelectorAll('a')].map((a) => a.getAttribute('href'))
    expect(hrefs).toContain('/target/1')
  })

  it('says "no association recorded" for a target absent from the map, never a blank', async () => {
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.textContent).toMatch(/Urothelial cancer/))
    const cell = cells('IGF2R')[4].textContent
    expect(cell).toMatch(/no association recorded/i)
    expect(cell).not.toBe('—')
  })

  it('⚠⚠ distinguishes an unreachable supplier from an empty one', async () => {
    getAssociations.mockRejectedValue(new Error('associations down'))
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.textContent).toMatch(/\/api\/associations/))
    expect(cells('NECTIN4')[4].textContent).toMatch(/could not be reached/)
    // a failure must NOT be reported as a fact about the 82 targets
    expect(container.textContent).not.toMatch(/no association recorded/i)
  })


  it('degrades the column and never the list when the map is unreachable', async () => {
    getAssociations.mockRejectedValue(new Error('associations down'))
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.textContent).toMatch(/\/api\/associations/))
    expect(container.querySelectorAll('tbody tr').length).toBe(3)
  })

  it('survives an api module that has no getAssociations at all', async () => {
    // ⚠ `Promise.resolve().then(() => getAssociations())` so a supplier that throws SYNCHRONOUSLY
    // cannot take the page down — which is exactly what an older test double does.
    getAssociations.mockImplementation(() => { throw new TypeError('not a function') })
    const { container } = draw()
    await ready()
    expect(container.querySelectorAll('tbody tr').length).toBe(3)
  })

  it('has NO sort control, and the page says why', async () => {
    // ⚠⚠ Ordering the cohort by the leading score, or by how many types clear the cutoff, would
    // make an expression statistic the cell never shows into the order of the list — the de facto
    // ranking this surface was ruled against on 2026-08-21 for mean pLDDT.
    const { container } = draw()
    await ready()
    const h = header(/cancer association/i)
    expect(h).toBeTruthy()
    expect(h.querySelector('button')).toBeNull()
    expect(h.getAttribute('aria-sort')).toBe('none')
    // ⚠ An absent control with no stated reason reads as an oversight.
    expect(container.textContent).toMatch(/no sort control/i)
  })
})

// ── the claim boundary ───────────────────────────────────────────────────────────────────────────
describe('the expression claim boundary reaches the list, in D-053\'s own words', () => {
  it('states expression, and states what it is not', async () => {
    const { container } = draw()
    await ready()
    const text = container.textContent
    expect(text).toMatch(/expression/i)
    expect(text.toLowerCase()).toContain('causation')
    expect(text).toMatch(/not a clinical indication/i)
    expect(text).toMatch(/drives the disease/i)
  })

  it('interpolates the cutoff from the payload rather than hardcoding the paper\'s 150', async () => {
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.textContent).toMatch(/151/))
    expect(container.textContent).not.toMatch(/above 150/)
  })

  it('makes no causal, curative or recommendation claim anywhere', async () => {
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.textContent).toMatch(/Urothelial cancer/))
    for (const banned of [
      /\bcauses\b/i, /\bdriver of\b/i, /\bindicated for\b/i, /\btreats\b/i,
      /\bbiomarker for\b/i, /\bdiagnostic\b/i, /\bbest target for\b/i,
    ]) {
      expect(container.textContent, `list must not claim ${banned}`).not.toMatch(banned)
    }
  })
})

// ── HPA compliance ──────────────────────────────────────────────────────────────────────────────
describe('⚠⚠ the HPA citation is a PRECONDITION of display, not a footnote', () => {
  it('emits the source-level credit once, beneath the table', async () => {
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.textContent).toMatch(/Urothelial cancer/))
    expect(container.querySelectorAll('.hpa-attrib-credit')).toHaveLength(1)
    expect(container.textContent).toMatch(/10\.1126\/science\.1260419/)
    expect(container.textContent).toMatch(/Image\/data credit/)
  })

  it('makes the tumour type itself the per-datum link, so element 4 costs no width', async () => {
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.textContent).toMatch(/Urothelial cancer/))
    const link = [...cells('NECTIN4')[4].querySelectorAll('a')]
      .find((a) => /proteinatlas/.test(a.getAttribute('href') || ''))
    expect(link).toBeTruthy()
    expect(link.getAttribute('href')).toBe(
      'https://v22.proteinatlas.org/ENSG00000143217-NECTIN4/pathology')
    expect(link.textContent).toMatch(/Urothelial cancer/)
  })

  it('⚠⚠ WITHHOLDS the tumour types when no attribution block exists for that gene', async () => {
    // Fail-closed is the only direction a precondition allows. The row still states the count
    // and the reason, so nothing is silently dropped.
    getAssociations.mockResolvedValue({ ...ASSOCIATIONS, attributions: {} })
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.textContent).toMatch(/withheld/i))
    const cell = cells('NECTIN4')[4].textContent
    expect(cell).not.toMatch(/Urothelial cancer/)
    expect(cell).toMatch(/2 tumour types/)
    expect(cell).toMatch(/licence/i)
    expect(container.querySelectorAll('.hpa-attrib-credit')).toHaveLength(0)
  })

  it('suppresses the credit when no row on screen rendered a tumour type', async () => {
    // ⚠ A licence-required citation beside a table that drew nothing is attached to nothing,
    // which is the other half of the 2026-08-21 split-by-case ruling.
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.textContent).toMatch(/Urothelial cancer/))
    fireEvent.change(screen.getByLabelText('Search'), { target: { value: 'IGF2R' } })
    expect(container.textContent).toMatch(/IGF2R/)
    expect(container.querySelectorAll('.hpa-attrib-credit')).toHaveLength(0)
  })
})

// ── column one ──────────────────────────────────────────────────────────────────────────────────
describe('⚠⚠ column one is bounded and demoted, and no cause is truncated', () => {
  it('still renders the rank cause in full, every character of it', async () => {
    const { container } = draw()
    await ready()
    // no ranking is served in these fixtures, so every row carries the shared 34-char cause
    await waitFor(() => expect(container.textContent).toMatch(/no ranking run is currently served/))
    const cause = container.querySelector('.rank-cause')
    expect(cause.textContent).toBe('no ranking run is currently served')
  })

  it('bounds the column in the stylesheet — a RULE, never a comment mentioning one', () => {
    // ⚠⚠ D-141 lost a guard to exactly this: a check that read the whole file and was satisfied by
    // a comment containing the string it wanted (`F-044` — a reference that resolves, to the wrong
    // thing). The prose above `.rank-cause` here contains `max-width`, so this parses declarations.
    const cell = declarations('.target-list .col-rank')
    const inner = declarations('.rank-cause')
    expect(cell.some((d) => /^max-width:/.test(d)), `no max-width rule on .col-rank: ${cell}`)
      .toBe(true)
    expect(inner.some((d) => /^max-width:/.test(d)), `no max-width rule on .rank-cause: ${inner}`)
      .toBe(true)
    // the bound sits on a BLOCK, or the auto table algorithm is free to ignore it
    expect(inner.some((d) => /^display:\s*block/.test(d))).toBe(true)
  })

  it('bounds it to something narrower than the two columns it made room for', () => {
    const rem = (decls) => {
      const d = decls.find((x) => /^max-width:/.test(x))
      return parseFloat(d.split(':')[1])
    }
    expect(rem(declarations('.rank-cause'))).toBeLessThanOrEqual(10)
    expect(rem(declarations('.target-list .col-description'))).toBeLessThanOrEqual(18)
    expect(rem(declarations('.target-list .col-assoc'))).toBeLessThanOrEqual(14)
  })

  it('⚠⚠ CLIPS NOTHING — the bound is a bound, not a truncation', () => {
    // Demotion is not deletion. "The column is narrower" is not the property; "the column is
    // narrower AND the text is all still there" is, and only the second one is asserted here.
    for (const sel of ['.rank-cause', '.description-text', '.assoc-cell']) {
      const decls = declarations(sel)
      expect(decls.length, `${sel} has no rule at all`).toBeGreaterThan(0)
      for (const d of decls) {
        expect(d, `${sel} clips its content: ${d}`).not.toMatch(
          /^(text-overflow|max-height|-webkit-line-clamp)\s*:/)
        expect(d, `${sel} hides its content: ${d}`).not.toMatch(/^overflow\s*:\s*hidden/)
        expect(d, `${sel} forbids the wrap the bound depends on: ${d}`).not.toMatch(
          /^white-space\s*:\s*nowrap/)
      }
    }
  })

  it('⚠⚠ does NOT use `overflow-wrap: anywhere`, which collapses the column to a character', () => {
    // ⚠⚠ FOUND BY OPENING THE PAGE, NOT BY THIS SUITE. The first version of the bound used
    // `overflow-wrap: anywhere` with no `min-width`, and at 1440px the column rendered ~45px wide
    // with the cause broken MID-WORD — "no / ranking / run is / currentl / y served". `anywhere`
    // (unlike `break-word`) shrinks an element's min-content size to one character, so the auto
    // table algorithm was free to squeeze the column away. jsdom has no layout and could not see
    // it; this test bars the declaration that caused it, and requires the floor that prevents it.
    for (const sel of ['.rank-cause', '.description-text', '.assoc-cell']) {
      for (const d of declarations(sel)) {
        expect(d, `${sel} breaks words mid-word and collapses its own minimum: ${d}`)
          .not.toMatch(/^(overflow-wrap|word-wrap)\s*:\s*anywhere/)
        expect(d, `${sel} breaks words mid-word: ${d}`)
          .not.toMatch(/^word-break\s*:\s*break-all/)
      }
    }
    expect(declarations('.rank-cause').some((d) => /^min-width:/.test(d)),
      'the rank cause needs a floor, or seven other columns will squeeze it out').toBe(true)
    expect(declarations('.target-list .col-rank').some((d) => /^min-width:/.test(d))).toBe(true)
  })

  it('keeps the cause typographically secondary to the integer it stands in for', () => {
    const decls = declarations('.rank-cause')
    expect(decls.some((d) => /^font-size:/.test(d))).toBe(true)
    // ⚠ the cell is `.mono` for the rank INTEGER; a sentence rendered in a number's face is
    // neither readable nor honest about what it is
    expect(decls.some((d) => /^font-family:\s*inherit/.test(d))).toBe(true)
  })
})

// ── what must not have changed ──────────────────────────────────────────────────────────────────
describe('what the new columns must NOT have disturbed', () => {
  it('leaves Rank, Gene and Accession as columns one, two and three', async () => {
    // ⚠ Three suites read `td[1]` for the gene and `td[2]` for the accession; more importantly the
    // rank axis is the default order and the identity columns lead it by ruling.
    draw()
    await ready()
    const labels = headers().map((h) => h.textContent.trim())
    expect(labels[0]).toMatch(/^Rank/)
    expect(labels[1]).toMatch(/^Gene/)
    expect(labels[2]).toMatch(/^Accession/)
  })

  it('keeps identity before the new columns and the new columns before fold confidence', async () => {
    draw()
    await ready()
    const labels = headers().map((h) => h.textContent.trim())
    const at = (re) => labels.findIndex((l) => re.test(l))
    expect(at(/description/i)).toBeGreaterThan(at(/^Accession/))
    expect(at(/cancer association/i)).toBeGreaterThan(at(/description/i))
    expect(at(/fold confidence/i)).toBeGreaterThan(at(/cancer association/i))
  })

  it('spans the unranked heading across every column, including the two new ones', async () => {
    // ⚠ A `colSpan` that lags the column count leaves the partition's own explanation
    // mis-aligned with the table it explains.
    getRanking.mockResolvedValue({ rows: [{ accession: 'Q92729', rank: 1, gene: 'NECTIN4' }] })
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.querySelector('.unranked-heading')).not.toBeNull())
    const span = container.querySelector('.unranked-heading td').getAttribute('colspan')
    expect(Number(span)).toBe(headers().length)
  })

  it('renders the SAME cells in the unranked partition as in the ranked body', async () => {
    // ⚠⚠ The row markup used to be written twice. Two copies of eight cells is a divergence
    // waiting to happen: the next column added to one and forgotten in the other would render a
    // table whose partition shows different facts about the same cohort.
    getRanking.mockResolvedValue({ rows: [{ accession: 'Q92729', rank: 1, gene: 'NECTIN4' }] })
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.querySelector('.row-unranked')).not.toBeNull())
    for (const tr of container.querySelectorAll('.row-unranked')) {
      expect(tr.querySelectorAll('td').length).toBe(headers().length)
    }
    // ADAM17 is unranked here, and its association and description still render
    const adam = rowFor('ADAM17')
    expect(adam.classList.contains('row-unranked')).toBe(true)
    expect(adam.textContent).toMatch(/Disintegrin/)
    expect(adam.textContent).toMatch(/Carcinoid/)
  })

  it('adds no blended score and no suitability claim (D-028 / D-075)', async () => {
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.textContent).toMatch(/Urothelial cancer/))
    for (const banned of [
      /\bcombined score\b/i, /\bblended\b/i, /\bquality score\b/i, /\boverall score\b/i,
      /\bsuitability score\b/i, /\bgood target\b/i, /\bpromising\b/i, /\brecommended\b/i,
    ]) {
      expect(container.textContent, `must not claim ${banned}`).not.toMatch(banned)
    }
  })

  it('leaves the pre-registered pLDDT floor and the partition untouched', async () => {
    getRanking.mockResolvedValue({ rows: [{ accession: 'Q92729', rank: 1, gene: 'NECTIN4' }] })
    const { container } = draw()
    await ready()
    await waitFor(() => expect(container.querySelector('.unranked-heading')).not.toBeNull())
    const heading = container.querySelector('.unranked-heading').textContent
    expect(heading).toMatch(/no scorer rank/)
    expect(heading).toMatch(/not ranked last/)
  })
})
