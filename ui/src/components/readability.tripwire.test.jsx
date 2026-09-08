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

// ⚠⚠ D-135 — THE CENSUS SUMMARY NOW RESOLVES, AND THAT IS A TIGHTENING. It was a bare `vi.fn()`
// returning `undefined`, so `s.census` was falsy and the Story's census beat NEVER RENDERED under
// this tripwire. The measurement covered nine paragraphs of a page that ships eleven — and D-135
// adds the two densest of all, the hold-48 tiling beat, which would have escaped the ceiling
// entirely. A readability guard that cannot see the hardest prose on the page is a guard measuring
// the easy half. ⚠ The ceiling is UNCHANGED at 12.5 and the measured value went DOWN (11.94 → 11.06
// over 1,977 words / 103 sentences), because the new beats are deliberately short-sentenced. Had it
// gone up, the copy was the thing to fix — re-calibrating a ceiling to admit new prose is how a
// tripwire becomes a decoration.
vi.mock('../api.js', () => ({
  getCensusSummary: vi.fn().mockResolvedValue({
    manifest_rows: 3467,
    folded: 2690,
    max_mean_plddt: 89.25,
    structure_kinds: [
      { kind: 'assembled', label: 'assembled (provisional)', n: 45 },
      { kind: 'single-pass', label: 'single-pass', n: 2645 },
    ],
  }),
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
    // ⚠ D-135: wait for the ASYNC beats too. The 50-character gate above is met by the headline
    // alone, so the measurement could complete before the fetched beats mounted — and a tripwire
    // that races the copy it measures reports whichever half arrived first.
    await waitFor(() => expect(container.textContent.length).toBeGreaterThan(1500))
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
//
// ⚠ D-135 re-measured, and the CEILING DID NOT MOVE. With the census and hold-48 beats now inside
// the measurement (see the mock above), the grade is 11.06 over 1,977 words / 103 sentences — lower
// than the 2026-07-26 calibration, because the new beats are written in short sentences on purpose.
// The 12.5 is left exactly where it was: it is the pin, and lowering it to the new reading would
// re-calibrate a tripwire on the strength of one good day.
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
