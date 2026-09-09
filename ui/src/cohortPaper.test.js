// D-151 — the cohort paper's citation, pinned to the committed source of truth.
//
// ⚠⚠ THE CLAIM UNDER TEST IS PROVENANCE, NOT SPELLING. `cohortPaper.js` exists so one DOI serves
// every surface, and a constant that drifts from the repository's own record is worse than no
// constant at all: it renders as a confident link to a paper nobody checked. So the DOI is
// asserted against `data/cohort_82.txt` — the file that defines which 82 proteins this project
// ranks and names the paper they came from — rather than against a second copy typed here.
//
// ⚠ The first assertion is that the file EXISTS. An error-red on a missing read is not a
// failure-red (A-016), so the read is proved to have reached real bytes before anything is
// concluded from it.
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, it, expect } from 'vitest'
import {
  COHORT_PAPER_CITATION,
  COHORT_PAPER_DOI,
  COHORT_PAPER_SHORT,
  COHORT_PAPER_URL,
  COHORT_SOURCE_PATH,
} from './cohortPaper.js'

const HERE = dirname(fileURLToPath(import.meta.url))
const SOURCE = resolve(HERE, '../../', COHORT_SOURCE_PATH)

describe('D-151 — the cohort paper citation is the repository\u2019s, not the UI\u2019s', () => {
  it('the cited source file is on disk and names the cohort', () => {
    const text = readFileSync(SOURCE, 'utf-8')
    expect(text.length).toBeGreaterThan(100)
    expect(text).toContain('82 prioritised ADC targets')
  })

  it('the DOI is a substring of the committed source — a typo here goes red on a file read', () => {
    const text = readFileSync(SOURCE, 'utf-8')
    expect(text).toContain(COHORT_PAPER_DOI)
    // ⚠ and the source names the paper the same way, so the short form is not an invention either
    expect(text).toContain('Kathad et al. 2024')
    expect(text).toContain('PLOS ONE')
    expect(text).toContain('CC-BY')
  })

  it('the URL is the DOI resolver over that DOI, derived and never typed twice', () => {
    expect(COHORT_PAPER_URL).toBe(`https://doi.org/${COHORT_PAPER_DOI}`)
    expect(COHORT_PAPER_URL).toBe('https://doi.org/10.1371/journal.pone.0308604')
  })

  it('the short form and the full citation agree with each other', () => {
    expect(COHORT_PAPER_CITATION).toContain(COHORT_PAPER_SHORT)
    expect(COHORT_PAPER_CITATION).toContain(COHORT_PAPER_DOI)
  })

  // ⚠⚠ NOT THE HPA CITATION, AND THE SEPARATION IS THE POINT. D-100 records that Kathad's S3 is a
  // verbatim extract of HPA's `pathology.tsv`, so citing the paper is expressly NOT citing HPA and
  // neither block may stand in for the other. This reddens if someone ever routes the HPA
  // publication through this module to save a file.
  it('carries no Human Protein Atlas DOI — the two obligations stay two modules', () => {
    const all = [COHORT_PAPER_DOI, COHORT_PAPER_URL, COHORT_PAPER_CITATION].join(' ')
    expect(all).not.toContain('10.1126/science.1260419')
    expect(all).not.toMatch(/proteinatlas/i)
  })
})
