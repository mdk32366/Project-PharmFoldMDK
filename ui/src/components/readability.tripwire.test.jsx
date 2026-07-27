// D-056: a readability REGRESSION tripwire (not a comprehension measure — see the entry's caveat).
// Flesch–Kincaid grade over the rendered narrative prose, numerals stripped, glossary terms and gene
// symbols exempted from the syllable count (unavoidable jargon shouldn't be penalised). The ceiling
// is calibrated from the measured value + a small margin (D-049: pin to what is observably true).
import { render, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

vi.mock('../api.js', () => ({
  listAnalyses: vi.fn().mockResolvedValue([{ id: 1, gene: 'NECTIN4', mean_plddt: 77.26 }]),
  getCoverage: vi.fn().mockResolvedValue({ coverage: { denominator: 1 }, rows: [{ disposition: 'ranked', fold_status: 'folded', gene: 'NECTIN4' }] }),
  getAssociations: vi.fn().mockResolvedValue({ source: 'the source paper', method: 'quasi H-score', cutoff: 150, pair_count: 1, targets_covered: 1, cohort_size: 1, unmatched_symbols: [], associations: { NECTIN4: [{ cancer: 'Lung', qh_score: 200 }] } }),
  getAnalysis: vi.fn(), getPlddt: vi.fn(), structureUrl: (id) => `/x/${id}`,
}))

import Story from './Story.jsx'
import AdcContext from './AdcContext.jsx'
import { GLOSSARY } from '../glossary.js'

const HERE = dirname(fileURLToPath(import.meta.url))
const COHORT = resolve(HERE, '../../../data/cohort_82.txt')

// exempt from syllable count: glossary term words + the 82 gene symbols (unavoidable jargon)
const geneSymbols = readFileSync(COHORT, 'utf-8').split('\n').map((l) => l.trim())
  .filter((l) => l && !l.startsWith('#'))
const EXEMPT = new Set(
  [...Object.keys(GLOSSARY).flatMap((t) => t.split(/[^A-Za-z0-9]+/)), ...geneSymbols]
    .map((w) => w.toLowerCase()).filter(Boolean),
)

function syllables(w) {
  w = w.toLowerCase().replace(/[^a-z]/g, '')
  if (w.length <= 3) return w ? 1 : 0
  w = w.replace(/(?:[^laeiouy]es|ed|[^laeiouy]e)$/, '').replace(/^y/, '')
  const m = w.match(/[aeiouy]{1,2}/g)
  return m ? m.length : 1
}
function fkGrade(text) {
  const clean = text.replace(/[0-9]+(\.[0-9]+)?/g, ' ')      // strip numerals (dec 2)
  const sentences = Math.max((clean.match(/[.!?]+/g) || []).length, 1)
  const words = clean.split(/\s+/).map((w) => w.replace(/[^A-Za-z-]/g, '')).filter(Boolean)
  const wc = Math.max(words.length, 1)
  let syl = 0
  for (const w of words) syl += EXEMPT.has(w.toLowerCase()) ? 1 : syllables(w)
  return { grade: 0.39 * (wc / sentences) + 11.8 * (syl / wc) - 15.59, words: wc, sentences }
}

async function renderedProse() {
  let text = ''
  for (const el of [<Story />, <AdcContext />]) {
    const { container, unmount } = render(<MemoryRouter>{el}</MemoryRouter>)
    await waitFor(() => expect(container.textContent.length).toBeGreaterThan(50))
    text += ' ' + container.textContent
    unmount()
  }
  return text
}

// Calibrated 2026-07-26 AFTER the plain-language rewrite: the narrative prose (Story + AdcContext)
// measured Flesch–Kincaid grade 11.94 (down from 13.15 pre-rewrite). Ceiling = measured + ~0.5
// margin (D-049: pin to the observed value, not an aspiration). This is a REGRESSION tripwire, not a
// clarity proof (see D-056) — it reddens if the copy drifts back toward density. The mixed prose
// carries peer-level ML copy that is deliberately not simplified, so ~12 is the honest floor here.
const CEILING = 12.5

beforeEach(() => vi.clearAllMocks())

describe('readability tripwire (D-056)', () => {
  it('the narrative prose stays at or below the calibrated grade ceiling', async () => {
    const { grade, words, sentences } = fkGrade(await renderedProse())
    // eslint-disable-next-line no-console
    console.log(`[D-056] Flesch–Kincaid grade = ${grade.toFixed(2)} over ${words} words / ${sentences} sentences (ceiling ${CEILING})`)
    expect(grade).toBeLessThanOrEqual(CEILING)
  })
})
