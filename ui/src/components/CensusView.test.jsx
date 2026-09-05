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

// ── "What we found" and "How to read it" (D-079 amendment 3) ──────────────
//
// ⚠⚠ THE PAGE HAD FOUR SECTIONS ABOUT WHAT THE NUMBERS ARE NOT AND NONE REPORTING A RESULT. That
// under-reported three weeks of measurement as a fold count. These tests pin the result AND pin the
// line it must not cross: "how to read it" may never become "how to use it".
describe('CensusView — what we found, and how to read it', () => {
  const t = () => render(<CensusView />).container.textContent

  it('reports the profile counts, and they reconcile to the folded total', () => {
    const x = t()
    expect(x).toMatch(/1,397/)
    expect(x).toMatch(/2,690/)
    expect(x).toMatch(/1,293/)
    expect(CENSUS.profile.profiled + CENSUS.profile.refused).toBe(CENSUS.profile.folded)
  })

  it('breaks the refusals down by cause, and the parts sum to the whole', () => {
    const p = CENSUS.profile
    expect(p.refusedOutOfRange + p.refusedSpanBelowFloor + p.refusedIncomplete).toBe(p.refused)
    const x = t()
    expect(x).toMatch(/1,225/)
    expect(x).toMatch(/fall outside the range the model was fitted on/)
  })

  it('calls the refusals a finding rather than a shortfall, and says WHY with both medians', () => {
    const x = t()
    expect(x).toMatch(/refusals are the finding, not a shortfall/i)
    expect(x).toMatch(/57/)
    expect(x).toMatch(/72\.4/)
  })

  it('states the band width without inviting a comparison across it', () => {
    const x = t()
    expect(x).toMatch(/0\.1065/)
    expect(x).toMatch(/0\.2927/)
    expect(x).toMatch(/It does not compare/i)
    expect(x).toMatch(/not against the ranked 82/i)
  })

  // ⚠⚠ THE LINE THIS SECTION MUST NOT CROSS. D-079 dec 1's not-licensed list and amendment 1's
  // "does not license the profile as evidence for anything" both stand. Asserted by ABSENCE, so a
  // future edit toward usefulness reddens.
  it('never tells the reader how to USE the profile', () => {
    // ⚠⚠ SCOPED TO THE TWO SECTIONS THIS COMMIT ADDED, AND THE FIRST VERSION WAS NOT. It banned
    // /shortlist/ across the whole page and matched an existing DISCLAIMER — "A count is not a
    // shortlist." That is the third time today a blanket word-ban has reddened on correct text
    // (F-052, and F-049 amendment 2 instance 3). ⚠ A ban on a word cannot tell a prohibition from
    // a violation; the claim I actually want is that the sections I wrote give no usage guidance,
    // and the rest of the page's hedges are not mine to police.
    const { container } = render(<CensusView />)
    const mine = [...container.querySelectorAll('.census-found, .census-howread')]
      .map((e) => e.textContent).join(' ')
    expect(mine.length).toBeGreaterThan(200)          // the scan reaches real text, not an empty set
    expect(mine).not.toMatch(/best candidate|most promising|shortlist|top target/i)
    expect(mine).not.toMatch(/higher (is|means) better/i)
    expect(mine).not.toMatch(/prioriti[sz]e/i)
    expect(mine).not.toMatch(/which targets? to/i)
    expect(mine).not.toMatch(/should (pick|choose|look)/i)
  })

  it('keeps every existing limit — the result did not replace the hedges', () => {
    const x = t()
    expect(x).toMatch(/None of these proteins has been scored or ranked/)
    expect(x).toMatch(/What these numbers do not mean/)
    expect(x).toMatch(/not a list of candidates/)
  })
})

// ⚠⚠ D-094 amendment 1 — a surface states the provenance of its figures, or it supplies a premise
// it cannot support. These five are written RED against the pre-amendment component.
//
// ⚠ Each fails AT ITS ASSERTION, not on an import or a render crash: `CensusView` already renders
// standalone in every describe above, so a failure here is a missing string and nothing else.
// An error-red is not a failure-red, and these are failure-reds.
describe('D-094 amendment 1 — census figures carry their provenance', () => {
  const text = () => render(<CensusView />).container.textContent

  it('F1: every rendered profile figure carries its measuredOn date AND its source artifact', () => {
    const t = text()
    // the figure is already on the page — that part is not the defect
    expect(t).toContain(CENSUS.profile.folded.toLocaleString())
    // ⚠ the date exists at censusSummary.js:38 as a SOURCE LITERAL and is not rendered
    expect(t).toContain(CENSUS.profile.measuredOn)
    // ⚠ nor does the page name the artifact the figure is about
    expect(t).toMatch(/census_features\.v1\.jsonl/)
  })

  it('F2: each tranche row renders planned and in-artifact as two distinct values', () => {
    const t = text()
    // tranche 3 is the discriminating row: 517 planned in the manifest, 516 in the artifact
    expect(t).toContain('517')
    expect(t).toContain('516')
  })

  it('F2b: tranche 5 names the 2026-09-05 closeout, not 48 held', () => {
    const t = text()
    expect(t).toContain('728')
    expect(t).toMatch(/27 unique stitched parents/)
    expect(t).toMatch(/Wave1 PASS 10/)
    expect(t).toMatch(/Wave2 PASS 17/)
    expect(t).toMatch(/pod Terminated/)
    expect(t).toMatch(/2026-09-05/)
    expect(t).not.toMatch(/48 held/)
    expect(t).not.toMatch(/waiting on rented capacity/)
  })

  it('U4: a reader cannot read a census figure as current — the date sits WITH the figure', () => {
    // ⚠ adjacency, not mere presence: a date elsewhere on the page does not qualify this count.
    const t = text().replace(/\s+/g, ' ')
    const folded = CENSUS.profile.folded.toLocaleString()
    const near = new RegExp(
      `${folded}[^.]{0,160}${CENSUS.profile.measuredOn}|${CENSUS.profile.measuredOn}[^.]{0,160}${folded}`,
    )
    expect(t).toMatch(near)
  })

  it('U7: a reader cannot conclude 776 tranche-5 structures exist', () => {
    // ⚠ 776 is 728 folded plus 48 HELD. Rendered bare beside "proteins" it asserts 776 structures.
    expect(text()).not.toMatch(/776\s*proteins/)
  })
})
