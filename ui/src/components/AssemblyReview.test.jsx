import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import AssemblyReview, { Igf2rTwoPopulation } from './AssemblyReview.jsx'

const REVIEW = {
  parent_analysis_id: 2817,
  parent_job_id: 2817,
  hold48_kind: 'parent',
  in_wave1_wave2_inventory: true,
  in_assembled_inventory: true,
  assembler_note: 'assembled by pLDDT overlap, not superimposed; seam not solved',
  seam_note: 'IGF2R ≈ 88.76 Å is a measured caveat, not a solved structure. Seams are not scientifically solved. Kabsch-path artifacts are not on disk for this parent.',
  dual_path: {
    assembler: {
      label: 'Assembler path (default served PDB) — pLDDT winner-tile, not a rigid-body transform',
      persist_stem: 'stitched',
      default_served: true,
    },
    kabsch: {
      present: false,
      persist_stem: 'kabsch/2817',
      empty_reason: 'no_kabsch_artifacts',
      empty_note: 'Kabsch-path artifacts are not on disk for this parent. No overlap RMSD and no max Cα jump to show. That absence is not a solved seam',
      seams: [],
    },
  },
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
    expect(t).not.toMatch(/superimposed holoprotein|seams solved|Kabsch GO|Kabsch aligned/)
    expect(t).toMatch(/Two paths/)
    expect(t).toMatch(/not on disk for this parent/)
    expect(t).toMatch(/kabsch\/2817/)
    expect(t).not.toMatch(/Kabsch \/ restitch remains PARKED/)
    expect(t).not.toMatch(/Three paths/)
    expect(t).not.toMatch(/confidence_kabsch/)
    expect(t).not.toMatch(/n_Cα_eff|Trim rounds|Weighted RMSD/)
  })

  it('names both paths and shows RMSD when Kabsch-path artifacts exist; jump stays empty if missing', () => {
    const review = {
      ...REVIEW,
      seam_note: 'A Kabsch-path sibling tree is named below as a second path.',
      dual_path: {
        assembler: REVIEW.dual_path.assembler,
        kabsch: {
          present: true,
          label: 'Kabsch-path (sibling tree) — overlap-Cα rigid transform, then the same winner-tile assembler. Not the default served PDB. Seams are not scientifically solved',
          persist_stem: 'kabsch/2817',
          accepted: true,
          empty_reason: null,
          seams: [{
            moving_tile_index: 2,
            reference_tile_index: 1,
            overlap_start: 1529,
            overlap_end: 1656,
            n_ca: 128,
            rmsd_angstrom: 1.25,
            max_ca_jump_angstrom: null,
            refuse_reason: null,
          }],
        },
      },
    }
    const { container, getByTestId } = render(
      <MemoryRouter><AssemblyReview review={review} /></MemoryRouter>,
    )
    const t = container.textContent
    expect(t).toMatch(/Two paths/)
    expect(t).toMatch(/stitched/)
    expect(t).toMatch(/kabsch\/2817/)
    expect(getByTestId('kabsch-seams').textContent).toMatch(/1\.25 Å/)
    expect(getByTestId('kabsch-seams').textContent).toMatch(/not computed on this path/)
    expect(t).not.toMatch(/seams solved|Kabsch aligned|fixed badge|full-length AF-quality/)
    expect(t).not.toMatch(/Three paths/)
  })

  it('names three paths and shows D-126 seam fields when confidence_kabsch artifacts exist', () => {
    const review = {
      ...REVIEW,
      seam_note: 'An overlap-confidence Kabsch sibling tree is named below as a third path.',
      triple_path: {
        assembler: REVIEW.dual_path.assembler,
        kabsch: {
          present: true,
          label: 'Kabsch-path (sibling tree) — overlap-Cα rigid transform, then the same winner-tile assembler. Not the default served PDB. Seams are not scientifically solved',
          persist_stem: 'kabsch/2817',
          accepted: true,
          empty_reason: null,
          seams: [{
            moving_tile_index: 2,
            reference_tile_index: 1,
            overlap_start: 1529,
            overlap_end: 1656,
            n_ca: 128,
            rmsd_angstrom: 1.25,
            max_ca_jump_angstrom: null,
            refuse_reason: null,
          }],
        },
        confidence_kabsch: {
          present: true,
          label: 'Overlap-confidence Kabsch-path (sibling tree) — weighted + trimmed overlap-Cα rigid transform, then the same winner-tile assembler. Not the default served PDB. Seams are not scientifically solved',
          persist_stem: 'confidence_kabsch/2817',
          accepted: true,
          empty_reason: null,
          seams: [{
            moving_tile_index: 2,
            reference_tile_index: 1,
            overlap_start: 1529,
            overlap_end: 1656,
            n_ca: 128,
            n_ca_eff: 96,
            rmsd_angstrom: 3.40,
            rmsd_full_overlap_angstrom: 8.10,
            max_ca_jump_angstrom: 4.20,
            trim_rounds: 2,
            refuse_reason: null,
          }],
        },
      },
    }
    const { container, getByTestId } = render(
      <MemoryRouter><AssemblyReview review={review} /></MemoryRouter>,
    )
    const t = container.textContent
    expect(t).toMatch(/Three paths/)
    expect(t).toMatch(/stitched/)
    expect(t).toMatch(/kabsch\/2817/)
    expect(t).toMatch(/confidence_kabsch\/2817/)
    expect(t).toMatch(/default served/)
    const seams = getByTestId('d126-seams').textContent
    expect(seams).toMatch(/3\.40 Å/)
    expect(seams).toMatch(/8\.10 Å/)
    expect(seams).toMatch(/4\.20 Å/)
    expect(seams).toMatch(/96/)
    expect(seams).toMatch(/2/)
    expect(t).not.toMatch(/seams solved|Kabsch aligned|fixed badge|full-length AF-quality/)
  })

  it('refused D-126 seam stays fail-closed and does not wear a fixed badge', () => {
    const review = {
      ...REVIEW,
      triple_path: {
        assembler: REVIEW.dual_path.assembler,
        kabsch: REVIEW.dual_path.kabsch,
        confidence_kabsch: {
          present: true,
          label: 'Overlap-confidence Kabsch-path (sibling tree). Not the default served PDB. Seams are not scientifically solved',
          persist_stem: 'confidence_kabsch/2817',
          accepted: false,
          seams: [{
            moving_tile_index: 2,
            reference_tile_index: 1,
            n_ca: 128,
            n_ca_eff: 40,
            rmsd_angstrom: 12.4,
            rmsd_full_overlap_angstrom: null,
            max_ca_jump_angstrom: null,
            trim_rounds: 5,
            refuse_reason: 'rmsd_gt_10',
          }],
        },
      },
    }
    const { container, getByTestId } = render(
      <MemoryRouter><AssemblyReview review={review} /></MemoryRouter>,
    )
    const t = container.textContent
    expect(getByTestId('d126-accepted').textContent).toMatch(/refused/)
    expect(t).toMatch(/rmsd_gt_10/)
    expect(t).not.toMatch(/fixed badge/)
    expect(t).not.toMatch(/seams solved|Kabsch aligned|full-length AF-quality/)
  })

  // D-127-B — four-path honesty. A D-127 seam holds k pieces; collapsing
  // them into one number would re-create the D-126 lie surface inside the
  // fix for it, so the card must show one row per piece.
  const D127_SEAM = {
    moving_tile_index: 2,
    reference_tile_index: 1,
    overlap_start: 1529,
    overlap_end: 1656,
    pieces: [
      { interval: [1540, 1600], n_ca: 61, rmsd_angstrom: 1.80, refuse_reason: null, accepted: true },
      { interval: [1610, 1650], n_ca: 41, rmsd_angstrom: 6.25, refuse_reason: null, accepted: true },
    ],
    pieces_empty_reason: null,
    linker_n: 12,
    max_linker_ca_jump: 3.05,
    rmsd_full_overlap_angstrom: 9.40,
    max_ca_jump_angstrom: 28.60,
    refuse_reason: null,
  }
  const fourPath = (piecewise) => ({
    assembler: REVIEW.dual_path.assembler,
    kabsch: { present: true, persist_stem: 'kabsch/2817', label: 'Kabsch-path (sibling tree)', seams: [] },
    confidence_kabsch: {
      present: true, persist_stem: 'confidence_kabsch/2817',
      label: 'Overlap-confidence Kabsch-path (sibling tree)', accepted: true, seams: [],
    },
    piecewise_kabsch: piecewise,
  })

  it('names four paths and shows one row per domain piece when piecewise_kabsch artifacts exist', () => {
    const review = {
      ...REVIEW,
      seam_note: 'A piecewise / domain-aware Kabsch sibling tree is named below as a fourth path.',
      four_path: fourPath({
        present: true,
        label: 'Piecewise / domain-aware Kabsch-path (sibling tree) — one weighted rigid transform per UniProt domain on the overlap Cα, then the same winner-tile assembler. Not the default served PDB. Seams are not scientifically solved',
        persist_stem: 'piecewise_kabsch/2817',
        accepted: true,
        empty_reason: null,
        seams: [D127_SEAM],
      }),
    }
    const { container, getByTestId } = render(
      <MemoryRouter><AssemblyReview review={review} /></MemoryRouter>,
    )
    const t = container.textContent
    expect(t).toMatch(/Four paths/)
    expect(t).toMatch(/stitched/)
    expect(t).toMatch(/kabsch\/2817/)
    expect(t).toMatch(/confidence_kabsch\/2817/)
    expect(t).toMatch(/piecewise_kabsch\/2817/)
    expect(t).toMatch(/default served/)
    const seams = getByTestId('d127-seams').textContent
    // BOTH pieces, with their own intervals and their own RMSD.
    expect(seams).toMatch(/1540–1600/)
    expect(seams).toMatch(/1610–1650/)
    expect(seams).toMatch(/1\.80 Å/)
    expect(seams).toMatch(/6\.25 Å/)
    expect(seams).toMatch(/61/)
    expect(seams).toMatch(/41/)
    // Parent cross-check + linkers sit beside the pieces, never instead.
    expect(seams).toMatch(/9\.40 Å/)
    expect(seams).toMatch(/28\.60 Å/)
    expect(seams).toMatch(/3\.05 Å/)
    expect(seams).toMatch(/12/)
    // No derived seam number: mean(1.80, 6.25) = 4.03, and neither a mean
    // nor a "seam RMSD" label may stand in for the per-piece rows.
    expect(seams).not.toMatch(/4\.03 Å/)
    expect(seams).not.toMatch(/Mean RMSD|Average RMSD|Seam RMSD|Pieces passing/i)
    expect(t).not.toMatch(/seams solved|Kabsch aligned|fixed badge|full-length AF-quality/)
  })

  it('renders a refused piece and a null parent measure as absences, never as 0.00 Å', () => {
    const review = {
      ...REVIEW,
      four_path: fourPath({
        present: true,
        label: 'Piecewise / domain-aware Kabsch-path (sibling tree). Not the default served PDB. Seams are not scientifically solved',
        persist_stem: 'piecewise_kabsch/2817',
        accepted: false,
        seams: [{
          ...D127_SEAM,
          pieces: [
            { interval: [1540, 1600], n_ca: 61, rmsd_angstrom: 12.40, refuse_reason: 'rmsd_gt_10', accepted: false },
            { interval: [1610, 1650], n_ca: 2, rmsd_angstrom: null, refuse_reason: 'overlap_ca_lt_3', accepted: false },
          ],
          linker_n: null,
          max_linker_ca_jump: null,
          rmsd_full_overlap_angstrom: null,
          max_ca_jump_angstrom: null,
          refuse_reason: 'rmsd_gt_10',
        }],
      }),
    }
    const { container, getByTestId } = render(
      <MemoryRouter><AssemblyReview review={review} /></MemoryRouter>,
    )
    const t = container.textContent
    expect(getByTestId('d127-accepted').textContent).toMatch(/refused/)
    const seams = getByTestId('d127-seams').textContent
    expect(seams).toMatch(/rmsd_gt_10/)
    expect(seams).toMatch(/overlap_ca_lt_3/)
    expect(seams).toMatch(/12\.40 Å/)
    // Refuse-before-transform has nothing to measure. Empty is not zero.
    expect(seams).toMatch(/not computed on this path/)
    expect(seams).not.toMatch(/0\.00 Å/)
    expect(t).not.toMatch(/fixed badge/)
    expect(t).not.toMatch(/seams solved|Kabsch aligned|full-length AF-quality/)
  })

  it('says a seam has no piece rows rather than reporting zero refused pieces', () => {
    const review = {
      ...REVIEW,
      four_path: fourPath({
        present: true,
        label: 'Piecewise / domain-aware Kabsch-path (sibling tree). Not the default served PDB.',
        persist_stem: 'piecewise_kabsch/2817',
        accepted: false,
        seams: [{
          ...D127_SEAM,
          pieces: [],
          pieces_empty_reason: 'no_piece_rows_recorded',
          rmsd_full_overlap_angstrom: null,
          max_ca_jump_angstrom: null,
          linker_n: null,
          max_linker_ca_jump: null,
          refuse_reason: 'no_domain_pieces',
        }],
      }),
    }
    const { getByTestId } = render(
      <MemoryRouter><AssemblyReview review={review} /></MemoryRouter>,
    )
    const seams = getByTestId('d127-seams').textContent
    expect(seams).toMatch(/No per-piece rows were recorded/)
    expect(seams).toMatch(/no_piece_rows_recorded/)
    expect(seams).toMatch(/not a count of zero refused pieces/)
    expect(seams).toMatch(/no_domain_pieces/)
  })

  it('does not imply a D-127 path when piecewise_kabsch artifacts are absent', () => {
    const review = {
      ...REVIEW,
      four_path: fourPath({
        present: false,
        persist_stem: 'piecewise_kabsch/2817',
        empty_reason: 'no_piecewise_kabsch_artifacts',
        empty_note: 'Piecewise / domain-aware Kabsch-path artifacts are not on disk for this parent.',
        seams: [],
      }),
    }
    const { container, queryByTestId } = render(
      <MemoryRouter><AssemblyReview review={review} /></MemoryRouter>,
    )
    const t = container.textContent
    expect(t).toMatch(/Three paths/)
    expect(t).not.toMatch(/Four paths/)
    expect(t).not.toMatch(/piecewise_kabsch\/2817/)
    expect(queryByTestId('d127-seams')).toBeNull()
    expect(queryByTestId('d127-accepted')).toBeNull()
  })

  // D-128-B — five-path honesty. A's §1a rows are CROSS-PATH, so the
  // collapse to guard against here is a mean jump per path or an
  // "N of M honest" tally: either hides which path is dishonest where.
  // The card renders one row per (path, seam) and derives nothing.
  const D128_HONESTY = [
    {
      path: 'kabsch', moving_tile_index: 2, reference_tile_index: 1,
      max_ca_jump_angstrom: 4.20, honest: true, honest_recorded: true,
      honest_disagrees_with_record: false, linker_fields_applicable: false,
      linker_n: null, max_linker_ca_jump: null,
      source: 'measured_from_path_artifacts', absence_reason: null, refuse_reason: null,
    },
    {
      path: 'confidence_kabsch', moving_tile_index: 2, reference_tile_index: 1,
      max_ca_jump_angstrom: 6.10, honest: true, honest_recorded: true,
      honest_disagrees_with_record: false, linker_fields_applicable: false,
      linker_n: null, max_linker_ca_jump: null,
      source: 'read_from_path_record', absence_reason: null, refuse_reason: null,
    },
    {
      path: 'piecewise_kabsch', moving_tile_index: 2, reference_tile_index: 1,
      max_ca_jump_angstrom: 28.60, honest: false, honest_recorded: false,
      honest_disagrees_with_record: false, linker_fields_applicable: true,
      linker_n: 12, max_linker_ca_jump: 3.05,
      source: 'read_from_path_record', absence_reason: null, refuse_reason: null,
    },
    {
      path: 'linker_seam', moving_tile_index: 2, reference_tile_index: 1,
      max_ca_jump_angstrom: null, honest: null, honest_recorded: null,
      honest_disagrees_with_record: false, linker_fields_applicable: false,
      linker_n: null, max_linker_ca_jump: null,
      source: 'absent', absence_reason: 'refused_before_transform',
      refuse_reason: 'seam_jump_gt_10',
    },
  ]
  const D128_SEAM = {
    moving_tile_index: 2, reference_tile_index: 1,
    overlap_start: 1529, overlap_end: 1656,
    offending_seam_source: 'from_d127_refuse', no_offending_seam: false,
    seam_centre: 1592, window_start: 1560, window_end: 1624,
    window_half_width_aa: 32, n_ca: 65, rmsd_angstrom: 2.75,
    max_ca_jump_angstrom: 7.40, pre_transform_max_ca_jump_angstrom: 31.20,
    honest: true, refuse_reason: null, accepted: true,
  }
  const fivePath = (linkerSeam) => ({
    ...fourPath({
      present: true,
      label: 'Piecewise / domain-aware Kabsch-path (sibling tree)',
      persist_stem: 'piecewise_kabsch/2817',
      accepted: true,
      seams: [D127_SEAM],
    }),
    linker_seam: linkerSeam,
  })

  it('names five paths and shows one honesty row per path per seam', () => {
    const review = {
      ...REVIEW,
      seam_note: 'A linker / seam honesty sibling tree is named below as a fifth path.',
      five_path: fivePath({
        present: true,
        label: 'Linker / seam honesty path (sibling tree) — per-path seam honesty rows. Not the default served PDB. Seams are not scientifically solved',
        persist_stem: 'linker_seam/2817',
        accepted: true,
        repaired: true,
        seams: [D128_SEAM],
        seam_honesty: D128_HONESTY,
        seam_honesty_empty_reason: null,
        window_half_width_aa: 32,
        success_pdb_on_disk: true,
        has_dishonest_or_unknown_seam: false,
      }),
    }
    const { container, getByTestId } = render(
      <MemoryRouter><AssemblyReview review={review} /></MemoryRouter>,
    )
    const t = container.textContent
    expect(t).toMatch(/Five paths/)
    expect(t).toMatch(/linker_seam\/2817/)
    expect(t).toMatch(/default served/)
    const honesty = getByTestId('d128-seam-honesty').textContent
    // Every path is named separately, with its own jump.
    expect(honesty).toMatch(/kabsch/)
    expect(honesty).toMatch(/confidence_kabsch/)
    expect(honesty).toMatch(/piecewise_kabsch/)
    expect(honesty).toMatch(/linker_seam/)
    expect(honesty).toMatch(/4\.20 Å/)
    expect(honesty).toMatch(/6\.10 Å/)
    expect(honesty).toMatch(/28\.60 Å/)
    expect(honesty).toMatch(/honest at this seam/)
    expect(honesty).toMatch(/dishonest at this seam/)
    // How each row is known travels with it.
    expect(honesty).toMatch(/measured_from_path_artifacts/)
    expect(honesty).toMatch(/read_from_path_record/)
    // ⚠ No derived number: mean(4.20, 6.10, 28.60) = 12.97 and the max is
    // 28.60. Neither a mean nor an "N of M honest" tally may stand in for
    // the per-path rows.
    expect(honesty).not.toMatch(/12\.97 Å/)
    expect(honesty).not.toMatch(/Mean jump|Average jump|Honesty score|seams honest|Best path/i)
    expect(t).not.toMatch(/seams solved|Kabsch aligned|fixed badge|full-length AF-quality/)
  })

  it('renders an unknown jump as not honest, never as 0.00 Å', () => {
    const review = {
      ...REVIEW,
      five_path: fivePath({
        present: true,
        label: 'Linker / seam honesty path (sibling tree). Not the default served PDB.',
        persist_stem: 'linker_seam/2817',
        accepted: false,
        repaired: false,
        seams: [{
          ...D128_SEAM,
          n_ca: 2,
          rmsd_angstrom: null,
          max_ca_jump_angstrom: null,
          honest: null,
          refuse_reason: 'overlap_ca_lt_3',
          accepted: false,
        }],
        seam_honesty: D128_HONESTY,
        success_pdb_on_disk: false,
        has_dishonest_or_unknown_seam: true,
      }),
    }
    const { container, getByTestId } = render(
      <MemoryRouter><AssemblyReview review={review} /></MemoryRouter>,
    )
    const honesty = getByTestId('d128-seam-honesty').textContent
    const seams = getByTestId('d128-seams').textContent
    // Unknown is spelled out, not left blank and not read as a pass.
    expect(honesty).toMatch(/unknown — not honest/)
    expect(honesty).toMatch(/refused_before_transform/)
    expect(seams).toMatch(/unknown — not honest/)
    expect(seams).toMatch(/overlap_ca_lt_3/)
    expect(honesty).toMatch(/not measured/)
    expect(seams).toMatch(/not computed on this path/)
    // The block's own prose says "never 0.00 Å"; what must never appear is
    // a RENDERED 0.00 Å where A wrote null. Drop the explanation, then look.
    expect(honesty.replace('never 0.00 Å', '')).not.toMatch(/0\.00 Å/)
    expect(seams).not.toMatch(/0\.00 Å/)
    // A dishonest or unknown seam never carries a success PDB.
    expect(getByTestId('d128-served-note').textContent)
      .toMatch(/No D-128-path stitched.pdb is presented as an honest result/)
    expect(getByTestId('d128-accepted').textContent).toMatch(/refused/)
    expect(container.textContent).not.toMatch(/fixed badge|seams solved/)
  })

  it('says linker fields are not defined on the paths that do not define them', () => {
    const review = {
      ...REVIEW,
      five_path: fivePath({
        present: true,
        label: 'Linker / seam honesty path (sibling tree).',
        persist_stem: 'linker_seam/2817',
        accepted: true,
        repaired: false,
        seams: [D128_SEAM],
        seam_honesty: D128_HONESTY,
        success_pdb_on_disk: false,
        has_dishonest_or_unknown_seam: false,
      }),
    }
    const { getByTestId } = render(
      <MemoryRouter><AssemblyReview review={review} /></MemoryRouter>,
    )
    const honesty = getByTestId('d128-seam-honesty').textContent
    expect(honesty).toMatch(/not defined on this path/)
    // D-127 is the one path that does define them, so its numbers show.
    expect(honesty).toMatch(/12/)
    expect(honesty).toMatch(/3\.05 Å/)
  })

  it('shows the window fit with the jump before and after, and how the seam was found', () => {
    const review = {
      ...REVIEW,
      five_path: fivePath({
        present: true,
        label: 'Linker / seam honesty path (sibling tree).',
        persist_stem: 'linker_seam/2817',
        accepted: true,
        repaired: true,
        seams: [D128_SEAM],
        seam_honesty: D128_HONESTY,
        window_half_width_aa: 32,
        success_pdb_on_disk: true,
        has_dishonest_or_unknown_seam: false,
      }),
    }
    const { getByTestId } = render(
      <MemoryRouter><AssemblyReview review={review} /></MemoryRouter>,
    )
    const seams = getByTestId('d128-seams').textContent
    expect(seams).toMatch(/1560–1624/)
    expect(seams).toMatch(/±32 aa/)
    expect(seams).toMatch(/2\.75 Å/)
    expect(seams).toMatch(/31\.20 Å/)
    expect(seams).toMatch(/7\.40 Å/)
    expect(seams).toMatch(/from_d127_refuse/)
    expect(seams).toMatch(/whole seam/)
    // A window transform is a recorded move, never a repaired seam.
    expect(getByTestId('d128-repaired').textContent).toMatch(/not a repaired seam/)
  })

  it('does not imply a D-128 path when linker_seam artifacts are absent', () => {
    const review = {
      ...REVIEW,
      five_path: fivePath({
        present: false,
        persist_stem: 'linker_seam/2817',
        empty_reason: 'no_linker_seam_artifacts',
        empty_note: 'Linker / seam honesty artifacts are not on disk for this parent.',
        seams: [],
        seam_honesty: [],
      }),
    }
    const { container, queryByTestId } = render(
      <MemoryRouter><AssemblyReview review={review} /></MemoryRouter>,
    )
    const t = container.textContent
    expect(t).toMatch(/Four paths/)
    expect(t).not.toMatch(/Five paths/)
    expect(t).not.toMatch(/linker_seam\/2817/)
    expect(queryByTestId('d128-seam-honesty')).toBeNull()
    expect(queryByTestId('d128-seams')).toBeNull()
    expect(queryByTestId('d128-accepted')).toBeNull()
  })

  it('renders nothing without a review block', () => {
    const { container } = render(<MemoryRouter><AssemblyReview /></MemoryRouter>)
    expect(container.textContent).toBe('')
  })

  // D-129-B — the Phase 5 fate block. ⚠ The card is where "accepted" is most
  // likely to read as resolution, so the rollup is asserted INSIDE the fate
  // block: a card that keeps the label and loses the numbers reddens here.
  it('labels an accept-refuse parent and renders the rollup inside the same block', () => {
    const review = {
      ...REVIEW,
      phase5_fate: {
        parent_job_id: 2938,
        fate: 'accept-refuse',
        label: 'named refuse / accept-refuse',
        is_accept_refuse: true,
        hunt_closed: true,
        meaning: 'accept-refuse is the recorded honest outcome of a refusal: the join is not held, we say it is not held, and we have stopped hunting it',
        not_a_miss: 'not a D-128 miss and not a D-128 failure: 0 of 7 repaired was pre-registered as an allowed outcome before the run',
        recorded_refuse_reason: 'seam_jump_gt_10',
        recorded_by_path: 'D-128',
        already_accept_refuse_note: null,
        disclosure_required: true,
        ops_rollup: {
          population: 'the D-128 linker seven',
          pass: 0, refuse: 7, fail: 0, skip: 0,
          repaired_of_seven: 0,
          pre_registered_at: 'D-128 Spec §1b / §3 / §11, before the run',
          refuse_seam_jump_gt_10: [2938, 3179, 3190, 3321, 3368, 3566],
          refuse_rmsd_gt_10: [2939],
          n_d125_pass_d128_refuse: 5,
          n_d126_pass_d128_refuse: 6,
          n_d127_pass_d128_refuse: 0,
          n_d127_refuse_d128_pass: 0,
          gate_angstrom: 10.0,
          recorded_by: 'Kaylee',
          recorded_at_tip: '9e65cbf',
          out_root: 'linker_seam_ops_2026-09-05',
          give_back_note: 'D-128 gave back 5 parents D-125 had accepted and 6 D-126 had accepted',
          best_experimental_path: 'D-126 remains the best experimental path until proven otherwise',
        },
      },
    }
    const { getByTestId } = render(
      <MemoryRouter><AssemblyReview review={review} /></MemoryRouter>,
    )
    const fate = getByTestId('phase5-fate').textContent
    expect(fate).toMatch(/named refuse \/ accept-refuse/)
    expect(fate).toMatch(/seam_jump_gt_10/)
    expect(fate).toMatch(/recorded by D-128/)
    expect(fate).toMatch(/not solved, not fixed, not repaired/)
    expect(fate).toMatch(/not an open must-hunt/)
    expect(fate).toMatch(/no fifth stitch algorithm/)
    // The rollup is INSIDE the fate block, not a sibling somewhere else.
    const rollup = getByTestId('phase5-ops-rollup').textContent
    expect(fate).toContain(rollup)
    expect(rollup).toMatch(/PASS 0 · REFUSE 7 · FAIL 0 · SKIP 0/)
    expect(rollup).toMatch(/repaired_of_seven/)
    expect(rollup).toMatch(/pre-registered as an allowed outcome/)
    expect(rollup).toMatch(/9e65cbf/)
    expect(rollup).toMatch(/linker_seam_ops_2026-09-05/)
    expect(rollup).toMatch(/not re-measured here/)
    // The give-back travels with the zero.
    const giveBack = getByTestId('phase5-give-back').textContent
    expect(giveBack).toMatch(/n_d125_pass_d128_refuse/)
    expect(giveBack).toMatch(/n_d126_pass_d128_refuse/)
    expect(giveBack).toMatch(/gave back 5 parents/)
    expect(giveBack).toMatch(/6 D-126 had accepted/)
    // Never solved, and the served path does not move because a label did.
    expect(fate).toMatch(/assembler/)
    expect(fate).not.toMatch(/seams solved|seam is repaired|full-length AF-quality/)
  })

  it('labels a Phase 4 parent accept-refuse with the Phase 4 0/2 rollup', () => {
    const review = {
      ...REVIEW,
      phase5_fate: {
        parent_job_id: 3272,
        fate: 'accept-refuse',
        label: 'named refuse / accept-refuse',
        is_accept_refuse: true,
        hunt_closed: true,
        phase: 'phase4',
        meaning: 'named refuse / accept-refuse after Phase 4 residual-RMSD OPS: this parent refused on the whole-overlap class, the hunt is stopped, and the 0 of 2 plus refuse class stay beside the label. It is not open must-hunt, not solved, and not an RMSD-v2 miss',
        not_a_miss: 'not a Phase 4 miss and not an RMSD-v2 miss: recovered_of_two = 0 was an allowed outcome written before the run, and both refuse classes landed beside the label',
        recorded_refuse_reason: 'rmsd_irreducible',
        recorded_by_path: 'D-130-A',
        moves_only_on: null,
        disclosure_required: true,
        ops_rollup: {
          population: 'the Phase 4 residual-RMSD pair (3272, 3394)',
          pass: 0, refuse: 2, fail: 0, skip: 0,
          recovered_of_two: 0,
          pre_registered_at: 'D-130 Spec / D-130-A (932292d / #253), before / with the run',
          refuse_rmsd_irreducible: [3272],
          refuse_rmsd_gt_10: [3394],
          notes: {
            3272: 'rmsd_irreducible; floor ≈ 12.63 Å (above the 10.0 Å gate)',
            3394: 'rmsd_gt_10; floor ≈ 4.77 Å; achieved RMSD ≈ 13.77 Å; correspondence offset = 0',
          },
          gate_angstrom: 10.0,
          recorded_by: 'recorded OPS',
          recorded_at_tip: '932292d',
          out_root: 'residual_rmsd_ops_2026-09-05',
          best_experimental_path: 'D-126 remains the best experimental path until proven otherwise; Phase 4 residual-RMSD recovered 0 of 2 at tip 932292d',
        },
      },
    }
    const { getByTestId, queryByTestId } = render(
      <MemoryRouter><AssemblyReview review={review} /></MemoryRouter>,
    )
    const fate = getByTestId('phase5-fate').textContent
    expect(fate).toMatch(/named refuse \/ accept-refuse/)
    expect(fate).toMatch(/rmsd_irreducible/)
    expect(fate).toMatch(/recorded by D-130-A/)
    expect(fate).toMatch(/not solved, not fixed, not repaired/)
    expect(fate).toMatch(/not an open must-hunt/)
    expect(fate).not.toMatch(/Phase 4 must-hunt/)
    expect(queryByTestId('phase5-phase4-open')).toBeNull()
    expect(queryByTestId('phase5-ops-rollup')).toBeNull()
    const rollup = getByTestId('phase4-ops-rollup').textContent
    expect(fate).toContain(rollup)
    expect(rollup).toMatch(/PASS 0/)
    expect(rollup).toMatch(/REFUSE 2/)
    expect(rollup).toMatch(/recovered_of_two/)
    expect(rollup).toMatch(/932292d/)
    expect(rollup).toMatch(/residual_rmsd_ops_2026-09-05/)
    expect(rollup).toMatch(/12\.63/)
    expect(rollup).toMatch(/13\.77/)
    expect(getByTestId('phase4-labelled').textContent).toMatch(/hunt stopped/)
    expect(fate).toMatch(/assembler/)
  })


  it('renders no fate block for a parent with no Phase 5 fate', () => {
    const { queryByTestId } = render(
      <MemoryRouter><AssemblyReview review={{ ...REVIEW, phase5_fate: {
        parent_job_id: 2817, fate: null, label: null, is_accept_refuse: false,
        meaning: 'No Phase 5 fate is recorded for this parent', ops_rollup: null,
      } }} /></MemoryRouter>,
    )
    expect(queryByTestId('phase5-fate')).toBeNull()
    expect(queryByTestId('phase5-ops-rollup')).toBeNull()
  })
})

// ⚠⚠ D-132 — the card carried ONE membership row ("in Wave1+Wave2 inventory of 27") and a
// note counting the same 27, so a parent assembled on the volume but outside the wave slice
// had no way to show as assembled at all. Two rows now, and the note counts the 45.
describe('D-132 — assembled inventory of 45 vs the Wave1+Wave2 slice of 27', () => {
  const renderCard = (review) => render(
    <MemoryRouter><AssemblyReview review={review} /></MemoryRouter>,
  ).container.textContent.replace(/\s+/g, ' ')

  it('shows both memberships and counts 45 out of the ranking, never 27', () => {
    const t = renderCard(REVIEW)
    expect(t).toMatch(/in assembled inventory of 45 \(measured 2026-09-08\)\s*yes/)
    expect(t).toMatch(/in Wave1\+Wave2 closeout slice of 27 \(2026-09-05\)\s*yes/)
    expect(t).toMatch(/45 unique assembled parents/)
    expect(t).toMatch(/F-004 ranking/)
    // ⚠ REDDENS ON REGRESSION: the disclosure may not go back to counting 27
    expect(t).not.toMatch(/27 unique/)
  })

  it('a parent in the 45 but outside the wave slice reads yes/no, not assembled-and-unknown', () => {
    const t = renderCard({
      ...REVIEW,
      parent_analysis_id: 3356,
      parent_job_id: 3356,
      in_wave1_wave2_inventory: false,
      in_assembled_inventory: true,
    })
    expect(t).toMatch(/in assembled inventory of 45 \(measured 2026-09-08\)\s*yes/)
    expect(t).toMatch(/in Wave1\+Wave2 closeout slice of 27 \(2026-09-05\)\s*no/)
  })

  it('does not let the amended count imply the OPS runs covered 45 or the seams are solved', () => {
    const t = renderCard(REVIEW)
    expect(t).toMatch(/OPS runs \(D-127 \/ D-128 \/ D-130\) were run on the 27/)
    expect(t).toMatch(/none of their numbers describe the other 18/)
    expect(t).not.toMatch(/seams solved|superimposed holoprotein|45\/45/)
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
