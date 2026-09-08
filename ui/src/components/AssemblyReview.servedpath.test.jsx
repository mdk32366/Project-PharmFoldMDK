import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import AssemblyReview from './AssemblyReview.jsx'

// D-139 — the review card must say WHICH path this parent is served, and WHY.
//
// ⚠ The reason is the load-bearing half. "Assembler" on its own cannot tell a
// reader that a parent was never eligible from that its D-126 run refused, and
// that is exactly the distinction the Phase 4 / Phase 5 vocabulary exists for.
// So every test below asserts the reason travels with the answer.

const BASE = {
  parent_analysis_id: 2817,
  parent_job_id: 2817,
  hold48_kind: 'parent',
  in_wave1_wave2_inventory: true,
  in_assembled_inventory: true,
  assembler_note: 'assembled by pLDDT overlap, not superimposed; seam not solved',
  seam_note: 'Seams are not scientifically solved.',
  readiness: {
    source: 'sibling_snapshot',
    expected_n: 2,
    present_complete_n: 2,
    missing: [],
    uncovered_n: 0,
    note: 'sibling snapshot — ops numbers, not a restitch GO.',
  },
  tiles: [],
  chosen_tile_ids: [],
  spare_tile_ids: [],
  downloads: { stitched: [], tiles: [] },
}

function servedBlock(overrides = {}) {
  return {
    decision: 'D-139',
    parent_job_id: 2817,
    served: 'assembler',
    persist_stem: 'stitched',
    eligible: true,
    flipped: false,
    not_flipped_reason: 'no_confidence_kabsch_artifacts',
    not_flipped_note:
      'This parent is eligible, but no overlap-confidence Kabsch tree is on disk for it, so there are no D-126 bytes to serve. The assembler is served. An absent tree is not a refusal and not a solved seam',
    pass_subset_n: 17,
    gate_angstrom: 10.0,
    gate_moved: false,
    auto_flip: false,
    solved: false,
    ...overrides,
  }
}

function renderReview(served) {
  render(
    <MemoryRouter>
      <AssemblyReview review={{ ...BASE, served_path: served }} />
    </MemoryRouter>,
  )
}

describe('D-139 served path on the review card', () => {
  it('names the assembler and the reason it was not flipped', () => {
    renderReview(servedBlock())
    expect(screen.getByTestId('served-path')).toBeTruthy()
    expect(screen.getByTestId('served-path-name').textContent).toContain('Assembler')
    expect(screen.getByTestId('served-path-flipped').textContent).toBe('no')
    expect(screen.getByTestId('served-path-eligible').textContent).toBe('yes')
    expect(screen.getByTestId('served-path-reason').textContent).toBe(
      'no_confidence_kabsch_artifacts',
    )
  })

  it('distinguishes never-eligible from the run refused it', () => {
    renderReview(
      servedBlock({
        eligible: false,
        not_flipped_reason: 'not_in_pass_subset',
        not_flipped_note:
          'This parent is not in the recorded D-126 PASS subset of 17, so the served path is the assembler. Artifacts on disk do not change that: the allowlist is the authority, never a pass count',
      }),
    )
    expect(screen.getByTestId('served-path-eligible').textContent).toBe('no')
    expect(screen.getByTestId('served-path-reason').textContent).toBe('not_in_pass_subset')
    expect(screen.getByTestId('served-path-note').textContent).toContain(
      'never a pass count',
    )
  })

  it('names D-126 as served, with no reason row, when the parent flipped', () => {
    renderReview(
      servedBlock({
        served: 'confidence_kabsch',
        persist_stem: 'confidence_kabsch/2817',
        flipped: true,
        not_flipped_reason: null,
        not_flipped_note: null,
      }),
    )
    expect(screen.getByTestId('served-path-name').textContent).toContain(
      'D-126 overlap-confidence Kabsch',
    )
    expect(screen.getByTestId('served-path-flipped').textContent).toBe('yes')
    expect(screen.queryByTestId('served-path-reason')).toBeNull()
    expect(screen.getByTestId('served-path-note').textContent).toContain(
      'stitched_confidence_kabsch.pdb',
    )
  })

  it('always carries the no-auto-flip clause and never says solved', () => {
    renderReview(servedBlock())
    const note = screen.getByTestId('served-path-note').textContent.toLowerCase()
    expect(note).toContain('no auto-flip')
    expect(note).toContain('never a pass count')
    expect(note).toContain('recorded')
    expect(note).toContain('not a solved seam')
    // ⚠ Every use of "solved" on this block must be a negation. A bare
    // affirmative one is the claim four earlier decisions exist to refuse.
    const solvedUses = note.match(/.{0,8}solved/g) || []
    expect(solvedUses.length).toBeGreaterThan(0)
    for (const use of solvedUses) expect(use).toContain('not a ')
  })

  it('renders nothing rather than guessing when the payload carries no decision', () => {
    renderReview(undefined)
    expect(screen.queryByTestId('served-path')).toBeNull()
  })
})
