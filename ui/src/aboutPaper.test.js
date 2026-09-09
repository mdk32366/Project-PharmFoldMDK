// D-123 — every science string in aboutPaper.js is a substring of the owner Doc.
// ⚠ First assertion is presence of the Doc file: an error-red on a missing import
// is not a failure-red. Then each excerpt must appear in the file, so a paraphrase
// in this module fails at the substring expect, not at a crash.
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, it, expect } from 'vitest'
import {
  PAPER_SOURCE_PATH,
  STANDING_LINE,
  TWO_TRACKS_TITLE,
  EV_NOT_V_KEY_TITLE,
  VERBATIM_EXCERPTS,
  TRACK_A,
  TRACK_B,
  BOTTOM_LINE_2,
} from './aboutPaper.js'

const HERE = dirname(fileURLToPath(import.meta.url))
const PAPER = resolve(HERE, '../../', PAPER_SOURCE_PATH)

describe('D-123 — aboutPaper.js is a verbatim extract of the owner Doc', () => {
  it('the owner Doc is on disk at the cited path', () => {
    const text = readFileSync(PAPER, 'utf-8')
    expect(text.length).toBeGreaterThan(100)
    expect(text).toContain('## Part 2')
  })

  it('every VERBATIM_EXCERPTS member is a substring of the Doc (paraphrase goes red here)', () => {
    const paper = readFileSync(PAPER, 'utf-8')
    expect(VERBATIM_EXCERPTS.length).toBeGreaterThan(0)
    for (const excerpt of VERBATIM_EXCERPTS) {
      expect(paper, `excerpt not in ${PAPER_SOURCE_PATH}: ${excerpt.slice(0, 60)}`).toContain(excerpt)
    }
  })

  it('Track A is red without wet bind; Track B ranks; EV is not a universal V-key', () => {
    expect(TRACK_A).toContain('Wet binding assays — required')
    expect(TRACK_A).toContain('No bind → stop')
    expect(TRACK_B).toContain('structure only — membrane × ECD × fold confidence (pLDDT)')
    expect(BOTTOM_LINE_2).toContain('not a universal V-domain key')
  })

  // ⚠ D-142 (owner GO 2026-09-08) — the aspirational composite is retired as a description
  // of what we rank by. Presence and absence are asserted TOGETHER: a revert of the copy
  // reddens at the negative, and a Track B that stops saying what it ranks by reddens at the
  // positives, so this cannot pass on an empty string the way a pure absence guard would.
  it('D-142: Track B ranks structurally, names its exclusions, and does not claim the retired composite', () => {
    expect(TRACK_B).toContain('structure only — membrane × ECD × fold confidence (pLDDT)')
    expect(TRACK_B).toContain('excluded')
    expect(TRACK_B).toContain('0.5 neutrals')
    expect(TRACK_B).toContain('not** ADC readiness')
    expect(TRACK_B).toContain('Later, on its own GO')
    expect(TRACK_B).not.toContain('rank by (cancer × membrane × internalization × density) / normal risk')
    expect(TRACK_B).not.toContain('/ normal risk')
  })

  it('chrome asks whether and does not say shows that', () => {
    expect(STANDING_LINE).toContain('asks whether')
    expect(STANDING_LINE).not.toContain('shows that')
    expect(TWO_TRACKS_TITLE).toBe('Two tracks (Nectin-4 / ADC framing)')
    expect(EV_NOT_V_KEY_TITLE).toBe('EV is not a universal V-key')
  })
})
