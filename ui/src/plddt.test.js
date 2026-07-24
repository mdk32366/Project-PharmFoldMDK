// D-046 smoke test — the ONE test that proves the harness runs and can fail. It asserts the
// existing pure bandFor() (ui/src/plddt.js, D-039) against its band boundaries. Deliberately
// scoped: no component render, no jsdom, nothing else. Component tests (starting with the
// provenance panel) are built on this harness separately; the ten existing components are known,
// named debt (D-046 §5), not retro-tested here.
import { describe, it, expect } from 'vitest'
import { bandFor } from './plddt.js'

describe('bandFor', () => {
  it('maps a high value (>= 70) to the confident-backbone band', () => {
    expect(bandFor(70).label).toBe('Confident backbone')
    expect(bandFor(81.4).label).toBe('Confident backbone')
  })

  it('maps null (and NaN) to the not-folded band, never a value band', () => {
    expect(bandFor(null).label).toBe('not folded')
    expect(bandFor(undefined).label).toBe('not folded')
    expect(bandFor(NaN).label).toBe('not folded')
  })

  it('lands each boundary value in the correct band (first `>= min` wins, high→low)', () => {
    // 70 / 60 / 50 are inclusive lower bounds; just-below falls to the next band down.
    expect(bandFor(69.9).label).toBe('Moderate')
    expect(bandFor(60).label).toBe('Moderate')
    expect(bandFor(59.9).label).toBe('Low — backbone unreliable')
    expect(bandFor(50).label).toBe('Low — backbone unreliable')
    expect(bandFor(49.9).label).toBe('Very low — not reliably interpretable')
    expect(bandFor(0).label).toBe('Very low — not reliably interpretable')
  })
})
