// D-048 §3.3 — the pLDDT band scheme, re-pinned against the now-larger cohort (UI-depth §2.4).
//
// D-039 set boundaries 50/60/70, justified two ways: convention anchors 70 and 50; the 60 line was
// justified by THIS cohort's measured mass (over the 42 folds: 24%/45%/57% below 50/60/70, from live
// /api/analyses). The cohort has since grown (rental rerun added ADAM17 72.78, SDK1 58.01, NOTCH2
// 57.89, PTPRZ1 30.68 — closeout 2026-07-24 §3). The prework's rule (trap b): recompute, do not
// assume the 42-fold justification still fits.
//
// PROVENANCE (D-016): the individual mean_plddt values live in production Postgres, not in the repo,
// so the *new distribution percentages* cannot be recomputed from any artefact available here. This
// file therefore pins what IS verifiable from the code — the band CONTRACT and the cohort-max caveat
// as a single source of truth every view reads — and leaves the numeric re-justification as a named
// owner action (a live `/api/analyses` query), rather than fabricating a distribution (D-016: name
// the artefact, or you are recording a belief).
//
// It also RE-HOMES the bandFor coverage that the D-046 smoke test held, so that smoke test can be
// deleted in this PR (owner ruling, prework §3) without losing the boundary assertions.
import { describe, it, expect } from 'vitest'
import { bandFor, BANDS, COHORT_MAX_PLDDT, colorFor } from './plddt.js'

describe('bandFor — boundary contract (re-homed from the D-046 smoke test)', () => {
  it('maps a high value (>= 70) to the confident-backbone band', () => {
    expect(bandFor(70).label).toBe('Confident backbone')
    expect(bandFor(81.4).label).toBe('Confident backbone')
  })

  it('maps null / undefined / NaN to the not-folded band, never a value band', () => {
    expect(bandFor(null).label).toBe('not folded')
    expect(bandFor(undefined).label).toBe('not folded')
    expect(bandFor(NaN).label).toBe('not folded')
  })

  it('lands each boundary value in the correct band (first `>= min` wins, high→low)', () => {
    expect(bandFor(69.9).label).toBe('Moderate')
    expect(bandFor(60).label).toBe('Moderate')
    expect(bandFor(59.9).label).toBe('Low — backbone unreliable')
    expect(bandFor(50).label).toBe('Low — backbone unreliable')
    expect(bandFor(49.9).label).toBe('Very low — not reliably interpretable')
    expect(bandFor(0).label).toBe('Very low — not reliably interpretable')
  })

  it('the four new rerun folds land where their means say they should (closeout 2026-07-24 §3)', () => {
    // A concrete check that the scheme still classifies the enlarged cohort sensibly.
    expect(bandFor(72.78).label).toBe('Confident backbone')            // ADAM17
    expect(bandFor(58.01).label).toBe('Low — backbone unreliable')     // SDK1
    expect(bandFor(57.89).label).toBe('Low — backbone unreliable')     // NOTCH2
    expect(bandFor(30.68).label).toBe('Very low — not reliably interpretable') // PTPRZ1
  })
})

describe('band scheme is a single source of truth (D-039: structure and legend cannot disagree)', () => {
  it('boundaries are exactly 50 / 60 / 70 and there is a not-folded sentinel', () => {
    const mins = BANDS.map((b) => b.min)
    expect(mins).toEqual([70, 60, 50, 0])
    expect(bandFor(null).min).toBeNull()
  })

  it('colorFor is derived from the same bands (per-residue plot and structure share one scheme)', () => {
    expect(colorFor(75)).toBe(BANDS[0].color)
    expect(colorFor(30)).toBe(BANDS[3].color)
  })

  it('the cohort-max caveat lives ONLY on the top band and names 84.23 (no high-confidence tier)', () => {
    expect(COHORT_MAX_PLDDT).toBe(84.23)
    // The caveat travels in the band a reader sees (D-039), and only there.
    expect(BANDS[0].caveat).toMatch(/84\.23/)
    expect(BANDS.slice(1).every((b) => b.caveat == null)).toBe(true)
  })
})
