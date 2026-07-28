import { describe, it, expect } from 'vitest'
import { targetStatus } from './targetScore.js'

// D-068: the four-valued (plus one defensive) status a target record resolves to. The owner's
// precedence ruling is the load-bearing part: FOLD STATE PRECEDES DISPOSITION. A target with no fold
// has no measurements, so no disposition can apply to it — IGF2R (fold failed, whole_sequence_fold,
// disposition=held_out) must read "not folded", NOT "held out" (which would imply measurements exist).
// Order: not folded → below floor → held out → ranked → (defensive) unranked-unexplained.

// A ranking payload shaped like /api/ranking, with distinctive values (Constraint-A: never the live ones).
const RANKING = {
  result_status: 'complete',
  result: {
    plddt_floor: 50,
    distribution: [{ symbol: 'ERBB2', percentile: 0.71 }, { symbol: 'NECTIN4', percentile: 0.63 }],
  },
  rows: [
    { rank: 1, accession: 'A-RANK1', gene: 'TOP1', score: 0.90, attributions: [0.1, -0.2, 0.3, 0.4, -0.5, 0.6] },
    { rank: 2, accession: 'A-ERBB2', gene: 'ERBB2', score: 0.70, attributions: [0.1, 0.1, 0.1, 0.1, 0.1, 0.1] },
    { rank: 3, accession: 'A-LAST', gene: 'BOT1', score: 0.40, attributions: [0, 0, 0, 0, 0, 0] },
  ],
}

describe('targetStatus — fold state precedes disposition (D-068)', () => {
  it('IGF2R case: no fold + disposition held_out → not_folded, never held_out', () => {
    const igf2r = { accession: 'A-IGF2R', gene: 'IGF2R', mean_plddt: null, disposition: 'held_out' }
    const s = targetStatus(igf2r, RANKING)
    expect(s.status).toBe('not_folded')
    // it has an analysis row (reachable via TargetView at all), so the D-043 category is "attempted"
    expect(s.category).toBe('attempted')
  })

  it('below the floor takes precedence over a ranked disposition', () => {
    const low = { accession: 'A-LOW', gene: 'LOW1', mean_plddt: 40, disposition: 'ranked' }
    const s = targetStatus(low, RANKING)
    expect(s.status).toBe('below_floor')
    expect(s.floor).toBe(50)   // derived from ranking.result.plddt_floor, never typed in the component
  })

  it('a folded, above-floor, held-out target reads held_out (the design target case)', () => {
    const held = { accession: 'A-HELD', gene: 'HELD1', mean_plddt: 58, disposition: 'held_out' }
    expect(targetStatus(held, RANKING).status).toBe('held_out')
  })

  it('D-068 amendment: a folded, held-out target BELOW the floor reads held_out, not below_floor (TMEM108)', () => {
    // held_out is pLDDT-independent, so it precedes below_floor. This is the fix for the two-surface
    // disagreement: the backend _exclusion_reason and the Scorer excluded-set already say held_out.
    const tmem108 = { accession: 'A-TMEM', gene: 'TMEM108', mean_plddt: 41.03, disposition: 'held_out' }
    expect(targetStatus(tmem108, RANKING).status).toBe('held_out')
  })

  it('the four statuses PARTITION the cohort — sum to total, unranked_unexplained empty (D-068)', () => {
    // The partition assertion (owner: "assert the partition, not just the absence" — D-024's shape).
    // A target landing in two states or none would break the sum; the fifth state falls out at 0.
    const cohort = [
      { accession: 'A-RANK1', gene: 'TOP1', mean_plddt: 70, disposition: 'ranked' },      // ranked
      { accession: 'A-ERBB2', gene: 'ERBB2', mean_plddt: 82, disposition: 'ranked' },     // ranked + labelled
      { accession: 'A-LOW', gene: 'LOW1', mean_plddt: 40, disposition: 'ranked' },        // below_floor
      { accession: 'A-HELD', gene: 'HELD1', mean_plddt: 58, disposition: 'held_out' },    // held_out (above floor)
      { accession: 'A-TMEM', gene: 'TMEM108', mean_plddt: 41, disposition: 'held_out' },  // held_out (below floor — amendment)
      { accession: 'A-IGF', gene: 'IGF2R', mean_plddt: null, disposition: 'held_out' },   // not_folded
    ]
    const counts = { ranked: 0, below_floor: 0, held_out: 0, not_folded: 0, unranked_unexplained: 0 }
    for (const t of cohort) counts[targetStatus(t, RANKING).status] += 1
    expect(counts.ranked + counts.below_floor + counts.held_out + counts.not_folded).toBe(cohort.length)
    expect(counts.unranked_unexplained).toBe(0)
    expect(counts).toMatchObject({ ranked: 2, below_floor: 1, held_out: 2, not_folded: 1 })
  })

  it('a folded, above-floor, ranked target present in the 56 reads ranked with its row', () => {
    const top = { accession: 'A-RANK1', gene: 'TOP1', mean_plddt: 70, disposition: 'ranked' }
    const s = targetStatus(top, RANKING)
    expect(s.status).toBe('ranked')
    expect(s.row.rank).toBe(1)
    expect(s.scores).toEqual([0.90, 0.70, 0.40])   // all 56 (here 3) scores, for min/median/max context
    expect(s.labelled).toBe(false)                 // TOP1 is not in the distribution
    expect(s.loo).toBeNull()
  })

  it('a ranked target that is also labelled carries its LOO percentile', () => {
    const erbb2 = { accession: 'A-ERBB2', gene: 'ERBB2', mean_plddt: 82, disposition: 'ranked' }
    const s = targetStatus(erbb2, RANKING)
    expect(s.status).toBe('ranked')
    expect(s.labelled).toBe(true)
    expect(s.loo.percentile).toBe(0.71)   // joined by symbol=gene
  })

  it('defensive fifth state: folded, above floor, ranked disposition, but ABSENT from the 56', () => {
    const ghost = { accession: 'A-GHOST', gene: 'GHOST1', mean_plddt: 70, disposition: 'ranked' }
    const s = targetStatus(ghost, RANKING)
    // never silently falls through — a named state, so the panel renders "reason not determined"
    expect(s.status).toBe('unranked_unexplained')
  })
})
