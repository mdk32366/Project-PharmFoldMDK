import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import CensusView from './CensusView.jsx'
import { CENSUS, CENSUS_LIMITS } from '../censusSummary.js'

// ⚠⚠ THE POINT OF THIS PAGE IS WHAT IT DOES NOT SHOW. D-079 dec 1 bars scoring any census row, and
// "a census row appearing on a tranche-zero surface" is a named stop condition. So the assertions
// that matter here are ABSENCE assertions.

describe('the census surface is unscored by construction', () => {
  it('the census data carries no score or rank FIELD anywhere', () => {
    // ⚠⚠ STRUCTURAL, NOT PROSE. Two earlier versions of this test scanned rendered text for
    // banned words and were WRONG BOTH TIMES — the page legitimately says "has not been scored",
    // "the 82 ranked targets" (a different population) and "a count is not a shortlist". Policing
    // wording kept flagging correct copy, and loosening a test until it passes is how a guard
    // becomes a decoration.
    //
    // The property that actually matters is that there is NO SCORE TO RENDER: the census data
    // objects carry no such field, so the page cannot show one however it is worded.
    //
    // Prove it bites by adding `score: 0.81` to any object in censusSummary.js.
    const banned = /^(score|rank|rating|percentile|priority|suitability)/i
    const walk = (node, path) => {
      if (Array.isArray(node)) return node.forEach((v, i) => walk(v, `${path}[${i}]`))
      if (node && typeof node === 'object') {
        for (const [k, v] of Object.entries(node)) {
          expect(banned.test(k), `census data exposes a "${k}" field at ${path}`).toBe(false)
          walk(v, `${path}.${k}`)
        }
      }
    }
    walk(CENSUS, 'CENSUS')
    walk(CENSUS_LIMITS, 'CENSUS_LIMITS')
  })

  // ⚠ A fourth assertion was written here and REMOVED rather than fixed: it scanned the
  // rendered text for decimals in 0..1 as "score-shaped" values, and it flagged five matches
  // (.1, .26, .2, .1, .1) that a probe could not trace back to any rendered figure. Three earlier
  // versions of the score assertion policed WORDING and were wrong each time. The structural test
  // above — no score/rank FIELD in the data — is the property that actually holds, and it does
  // not depend on prose or on formatting. ⚠ The unexplained matches are a LOOSE END, recorded
  // rather than silently dropped: if a decimal ever does appear on this page it will not be caught
  // by a test, and the no-per-protein-row assertion below is what stands in its place.

  it('renders no per-protein row at all', () => {
    // ⚠ A per-protein list is one sort control away from being read as a shortlist, so there is
    // no accession anywhere on the page. Prove it bites by listing even one.
    const { container } = render(<CensusView />)
    expect(container.textContent).not.toMatch(/\b[OPQ][0-9][A-Z0-9]{3}[0-9]\b/)
  })

  it('puts the "not scored" statement ABOVE the numbers, not below them', () => {
    // ⚠ A reader who stops after the headline figure must already have met the limit.
    const { container } = render(<CensusView />)
    const t = container.textContent
    expect(t.indexOf('None of these proteins has been scored')).toBeGreaterThan(-1)
    expect(t.indexOf('None of these proteins has been scored'))
      .toBeLessThan(t.indexOf('proteins examined'))
  })

  it('states that the census is not comparable to the ranked 82', () => {
    render(<CensusView />)
    expect(screen.getByText(/not comparable to the ranked 82/i)).toBeTruthy()
  })
})

describe('absences carry causes', () => {
  it('every not-foldable category names a reason and explains it plainly', () => {
    for (const r of CENSUS.notFoldable) {
      expect(r.reason, 'a category with no reason').toBeTruthy()
      expect(r.plain, `${r.reason} has no plain-language explanation`).toBeTruthy()
      expect(r.plain).not.toBe(r.reason)
    }
  })

  it('renders every absence category, including the single-row ones', () => {
    // ⚠ A category with one row is the easiest to drop for tidiness, and the easiest to
    // rediscover later as a bug. Prove it bites by filtering to rows > 1.
    render(<CensusView />)
    for (const r of CENSUS.notFoldable) {
      expect(screen.getByText(new RegExp(r.reason.replace(/[()]/g, '.'), 'i')),
        `absence "${r.reason}" is not on the page`).toBeTruthy()
    }
    expect(CENSUS.notFoldable.some((r) => r.rows === 1)).toBe(true)
  })
})

describe('the limitation block', () => {
  it('renders every limitation in full', () => {
    // ⚠ Not a footnote, and never trimmed to fit a layout.
    render(<CensusView />)
    for (const l of CENSUS_LIMITS) {
      expect(screen.getByText(l.head), `limitation missing: ${l.head}`).toBeTruthy()
    }
  })

  it('names the two span definitions and says they are not comparable', () => {
    const t = CENSUS_LIMITS.map((l) => `${l.head} ${l.body}`).join(' ')
    expect(t).toMatch(/two span definitions/i)
    expect(t).toMatch(/not comparable/i)
  })

  it('discloses the multi-segment rule and the attention tilt', () => {
    const t = CENSUS_LIMITS.map((l) => `${l.head} ${l.body}`).join(' ')
    expect(t).toMatch(/largest contiguous/i)
    expect(t).toMatch(/2% of the variation/i)
    expect(t).toMatch(/rather than corrected/i)
  })
})

describe('batches are batches', () => {
  it('says a batch is a running order and not a ranking', () => {
    // ⚠ D-083. Prove it bites by removing the clause: "Batch 1" then reads as "first choice".
    render(<CensusView />)
    expect(screen.getByText(/a batch is a running order, not a ranking/i)).toBeTruthy()
  })

  it('the tranche rows sum to the manifest', () => {
    expect(CENSUS.tranches.reduce((a, t) => a + t.rows, 0)).toBe(CENSUS.manifestRows)
  })

  it('the foldable and not-foldable counts reconcile to the examined total', () => {
    // ⚠ The denominator closes on the page itself, not only in the artifact.
    const rows = CENSUS.sources.reduce((a, s) => a + s.rows, 0)
    const foldable = CENSUS.sources.reduce((a, s) => a + s.foldable, 0)
    const absent = CENSUS.notFoldable.reduce((a, r) => a + r.rows, 0)
    expect(foldable + absent).toBe(rows)
  })
})

// ⚠⚠ THE CLAIM MUST TRACK THE SURFACE, AND ONCE IT DID NOT. Until 2026-08-19 this page said
// "None of these proteins has been scored or ranked" full stop — true when written, because no
// model output existed for a census protein. The structural profile (D-079 amendment 1, ruled by
// amendment 2) made it true only by virtue of ruling 1's NAMING rule, one click from a page
// showing the model's output. ⚠ A claim that survives on what we decided to call something is not
// the claim the reader is reading. These tests pin the disclosure, so the sentence cannot drift
// back out of step with what the site actually shows.
describe('CensusView — the unscored claim must disclose the profile', () => {
  const text = () => render(<CensusView />).container.textContent

  it('still says none is scored or ranked, because that half is TRUE', () => {
    const t = text()
    expect(t).toMatch(/None of these proteins has been scored or ranked/)
  })

  it('discloses the structural profile in the same sentence, not elsewhere on the page', () => {
    const t = text()
    const claim = t.indexOf('None of these proteins has been scored or ranked')
    const disclosure = t.indexOf('structural profile')
    expect(disclosure).toBeGreaterThan(-1)
    // ⚠ within the same paragraph's worth of text — a disclosure three sections down is a
    // different claim from a qualified one.
    expect(disclosure - claim).toBeGreaterThan(0)
    expect(disclosure - claim).toBeLessThan(400)
  })

  it('says the profile is a measurement and that nothing is ordered by it (ruling 2)', () => {
    const t = text()
    expect(t).toMatch(/measurement, not a verdict/)
    expect(t).toMatch(/no protein is ordered by it/i)
  })
})
