import { render } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import CoverageLine from './CoverageLine.jsx'

// D-066: CoverageLine states the D-024 partition and MUST NOT assert what the RANKING covers. The
// ranking's membership is decided downstream by the pLDDT floor, invisible to this component; a
// coverage component that claims "the ranking covers these N" makes an unverifiable claim — and on
// /scorer a false one (67 ranked & folded vs 56 above the floor). The claim is asserted by ABSENCE
// so any re-introduction reddens, on both surfaces (this component is the shared source).
//
// Distinctive fixture numbers (denominator 9, ranked-and-folded 4) cannot coincide with any live
// value, so a hardcoded literal could never satisfy the derived-headline assertion (D-050).
const COVERAGE = { denominator: 9, ranked: 6, held_out: 2, excluded: 1, unmeasured_tier: 1, no_topology: 1 }
const ROWS = [
  { disposition: 'ranked', fold_status: 'folded' },
  { disposition: 'ranked', fold_status: 'folded' },
  { disposition: 'ranked', fold_status: 'folded' },
  { disposition: 'ranked', fold_status: 'folded' },
  { disposition: 'ranked', fold_status: 'not_folded' },  // ranked but NOT folded -> excluded from the intersection
  { disposition: 'held_out', fold_status: 'folded' },
  { disposition: 'held_out', fold_status: 'not_folded' },
  { disposition: 'excluded', fold_status: 'folded' },
]

describe('CoverageLine', () => {
  it('states the ranked-and-folded partition headline, derived from the payload', () => {
    const { container } = render(<CoverageLine coverage={COVERAGE} rows={ROWS} />)
    // 4 ranked∧folded of 9 — both derived (count of ranked∧folded rows; denominator)
    expect(container.textContent).toMatch(/4 ranked & folded of 9/)
    // the D-024 partition-honesty statement stays — the alternatives would overstate the cohort
    expect(container.textContent).toMatch(/overstate the cohort/)
  })

  it('D-066: makes NO claim about what the ranking covers (absence, both surfaces)', () => {
    const { container } = render(<CoverageLine coverage={COVERAGE} rows={ROWS} />)
    const t = container.textContent
    expect(t).not.toMatch(/covers these/i)
    expect(t).not.toMatch(/once the scorer/i)
    expect(t).not.toMatch(/the ranking[^.]*covers/i)
  })
})
