import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import AssemblyReview, { Igf2rTwoPopulation } from './AssemblyReview.jsx'

const REVIEW = {
  parent_analysis_id: 2817,
  parent_job_id: 2817,
  hold48_kind: 'parent',
  in_wave1_wave2_inventory: true,
  assembler_note: 'assembled by pLDDT overlap, not superimposed; seam not solved',
  seam_note: 'IGF2R ≈ 88.76 Å is a measured caveat, not a solved structure. Kabsch / restitch remains PARKED.',
  readiness: {
    source: 'sibling_snapshot',
    expected_n: 2,
    present_complete_n: 2,
    missing: [],
    uncovered_n: 0,
    note: 'sibling snapshot — ops numbers, not a restitch GO.',
  },
  tiles: [
    {
      analysis_id: 3673, job_id: 3673, start: 1, end: 1656, span_aa: 1656,
      status: 'complete', has_pae: true, role: 'chosen',
      named_spare: false, preferred_lower_id: true, download_stem: 'tile1',
    },
    {
      analysis_id: 3630, job_id: 3630, start: 1529, end: 2368, span_aa: 840,
      status: 'complete', has_pae: true, role: 'chosen',
      named_spare: false, preferred_lower_id: false, download_stem: 'tile2',
    },
    {
      analysis_id: 3693, job_id: 3693, start: 1, end: 1656, span_aa: 1656,
      status: 'complete', has_pae: true, role: 'spare',
      named_spare: true, preferred_lower_id: false, download_stem: 'spare3693',
    },
  ],
  chosen_tile_ids: [3673, 3630],
  spare_tile_ids: [3693],
  downloads: {
    stitched: [
      { name: 'stitched.pdb', href: '/api/analyses/2817/structure', available: true },
      { name: 'stitched_plddt.json', href: '/api/analyses/2817/plddt', available: true },
      { name: 'stitched_pae.json', href: '/api/analyses/2817/pae', available: true },
    ],
    tiles: [
      { name: 'tile1.pdb', href: '/api/analyses/3673/structure', available: true, role: 'chosen' },
      { name: 'spare3693.pdb', href: '/api/analyses/3693/structure', available: true, role: 'spare' },
    ],
  },
}

describe('AssemblyReview', () => {
  it('shows readiness counts, chosen vs spare, PAE, and named downloads', () => {
    const { container } = render(
      <MemoryRouter><AssemblyReview review={REVIEW} /></MemoryRouter>,
    )
    const t = container.textContent
    expect(t).toMatch(/expected_n/)
    expect(t).toMatch(/present_complete_n/)
    expect(t).toMatch(/uncovered_n/)
    expect(t).toMatch(/not a restitch/)
    expect(t).toMatch(/3673/)
    expect(t).toMatch(/chosen/)
    expect(t).toMatch(/spare/)
    expect(t).toMatch(/named unused spare/)
    expect(t).toMatch(/PAE yes/)
    expect(screen.getByRole('link', { name: 'stitched.pdb' })).toHaveAttribute(
      'href', '/api/analyses/2817/structure',
    )
    expect(screen.getByRole('link', { name: 'tile1.pdb' })).toHaveAttribute(
      'href', '/api/analyses/3673/structure',
    )
    expect(t).not.toMatch(/superimposed holoprotein|seams solved|Kabsch GO/)
    expect(t).toMatch(/Kabsch \/ restitch remains PARKED/)
  })

  it('renders nothing without a review block', () => {
    const { container } = render(<MemoryRouter><AssemblyReview /></MemoryRouter>)
    expect(container.textContent).toBe('')
  })
})

describe('Igf2rTwoPopulation', () => {
  it('names both measurements and refuses substitution', () => {
    const { container } = render(
      <Igf2rTwoPopulation copy={{
        cohort: 'Cohort IGF2R (tranche 0, job 57) is a CUDA OOM failure.',
        census: 'Census tiles are a later span definition (D-081). Neither substitutes for the other.',
      }} />,
    )
    expect(container.textContent).toMatch(/CUDA OOM/)
    expect(container.textContent).toMatch(/Neither substitutes/)
    expect(container.textContent).toMatch(/Two populations/)
  })
})
