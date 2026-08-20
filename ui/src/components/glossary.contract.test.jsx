// D-055 contract test (orders §5.1 watchlist form): an undefined must-define term reaching a
// rendered surface reddens the gate. Scanning ALL acronym-shaped tokens proved impractical — rendered
// copy also carries decision refs (D-045, DEP-001), UniProt accessions (Q96NY8), cancer names and
// units, none glossary terms and none cleanly exemptible — so the contract is the curated MUST_DEFINE
// watchlist, not an open scan (reported in the PR). The gene-symbol exemption is DERIVED from
// data/cohort_82.txt, not typed.
import { render, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

vi.mock('../api.js', () => ({
  getCensusSummary: vi.fn(),
  listAnalyses: vi.fn().mockResolvedValue([{ id: 1, gene: 'NECTIN4', mean_plddt: 77.26 }]),
  getCoverage: vi.fn().mockResolvedValue({
    coverage: { denominator: 1 },
    rows: [{ disposition: 'ranked', fold_status: 'folded', gene: 'NECTIN4' }],
  }),
  getAssociations: vi.fn().mockResolvedValue({
    source: 'HPA IHC, per the paper', method: 'quasi H-score', cutoff: 150,
    pair_count: 1, targets_covered: 1, cohort_size: 1, unmatched_symbols: [],
    associations: { NECTIN4: [{ cancer: 'Lung', qh_score: 200 }] },
  }),
  getAnalysis: vi.fn(), getPlddt: vi.fn(), structureUrl: (id) => `/x/${id}`,
}))

import { GLOSSARY, MUST_DEFINE } from '../glossary.js'
import MethodNote from './MethodNote.jsx'
import Story from './Story.jsx'
import AdcContext from './AdcContext.jsx'
import CancerAssociations from './CancerAssociations.jsx'

const HERE = dirname(fileURLToPath(import.meta.url))
const COHORT = resolve(HERE, '../../../data/cohort_82.txt')

const surfaces = () => [
  ['MethodNote', <MethodNote />],
  ['Story', <Story />],
  ['AdcContext', <AdcContext />],
  ['CancerAssociations', <CancerAssociations symbol="NECTIN4" />],
]

beforeEach(() => vi.clearAllMocks())

describe('glossary contract (D-055)', () => {
  it('every must-define term the UI uses has a glossary entry', () => {
    const missing = MUST_DEFINE.filter((t) => !GLOSSARY[t])
    expect(missing, `must-define terms with no glossary entry: ${missing.join(', ')}`).toEqual([])
  })

  it('no must-define term reaches a rendered surface without a definition', async () => {
    for (const [label, el] of surfaces()) {
      const { container, unmount } = render(<MemoryRouter>{el}</MemoryRouter>)
      await waitFor(() => expect(container.textContent.length).toBeGreaterThan(0))
      const text = container.textContent
      for (const term of MUST_DEFINE) {
        if (text.includes(term)) {
          expect(GLOSSARY[term], `${label} renders "${term}" but it has no glossary entry`).toBeTruthy()
        }
      }
      unmount()
    }
  })

  it('the 82 gene symbols are exempt — derived from cohort_82.txt, never must-define', () => {
    const symbols = readFileSync(COHORT, 'utf-8')
      .split('\n').map((l) => l.trim()).filter((l) => l && !l.startsWith('#'))
    expect(symbols.length).toBe(82)
    const collide = symbols.filter((s) => MUST_DEFINE.includes(s))
    expect(collide, `gene symbols wrongly in MUST_DEFINE: ${collide.join(', ')}`).toEqual([])
  })
})
