// D-048 §3.1 — the two-population provenance render (D-046 §3 spec).
//
// The panel exists to make the Prime Directive claim — "we ran ESMFold ourselves, at a named
// revision" — CHECKABLE. The one class of bug it cannot tolerate is rendering a missing field as
// present, which turns an honest gap into a false provenance claim (D-046 §4). These tests assert
// on rendered output as a reader encounters it (visible text/roles), not component internals.
//
// The cohort is two populations (D-045):
//   - pre-D-045 folds: fold_provenance lacks the four environment keys entirely.
//   - post-D-045 folds: torch_version / transformers_version / device_name / cuda_version populated.
// Fixtures use the REAL live values from the 2026-07-24 rerun pod (closeout §3): torch 2.8.0+cu128,
// transformers 5.14.1, NVIDIA RTX A6000, cuda 12.8.
import { describe, it, expect } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import Provenance from './Provenance.jsx'

// A post-D-045 fold (the rerun's PTPRZ1: sliced ECD, chunk-64, full environment).
const POST_D045 = {
  boundary_method: 'sliced_ecd',
  ecd_start: 25,
  ecd_end: 1637,
  uniprot_release: '2025_03',
  tier: 'rental',
  fold_provenance: {
    model_id: 'facebook/esmfold_v1',
    model_revision: 'a1b2c3d',
    dtype: 'float16',
    chunk_size: 64,
    input_length: 1612,
    ca_atom_count: 1612,
    truncated: false,
    folded_at: '2026-07-24T18:40:00Z',
    torch_version: '2.8.0+cu128',
    transformers_version: '5.14.1',
    device_name: 'NVIDIA RTX A6000',
    cuda_version: '12.8',
  },
}

// A pre-D-045 fold (a local int8 fold from before environment capture existed): the provenance
// dict is present but carries NONE of the four environment keys. This is the population whose
// honest statement is "this fold predates environment capture," not "—".
const PRE_D045 = {
  boundary_method: 'sliced_ecd',
  ecd_start: 30,
  ecd_end: 350,
  uniprot_release: '2025_02',
  tier: 'local',
  fold_provenance: {
    model_id: 'facebook/esmfold_v1',
    model_revision: 'a1b2c3d',
    dtype: 'int8',
    chunk_size: 64,
    input_length: 320,
    ca_atom_count: 320,
    truncated: false,
    folded_at: '2026-07-20T10:00:00Z',
    // no torch_version, transformers_version, device_name, cuda_version
  },
}

// A whole-chain fold: ecd_start is genuinely not-applicable (D-046 rule 1 — this stays an em-dash,
// distinct from not-captured).
const WHOLE_CHAIN = {
  boundary_method: 'whole',
  ecd_start: null,
  ecd_end: null,
  uniprot_release: '2025_03',
  tier: 'local',
  fold_provenance: { ...PRE_D045.fold_provenance, boundary_method: undefined },
}

describe('Provenance — two-population environment render (D-046 §3)', () => {
  describe('post-D-045 fold (environment captured)', () => {
    it('renders each real environment value verbatim', () => {
      render(<Provenance detail={POST_D045} />)
      expect(screen.getByText('2.8.0+cu128')).toBeInTheDocument()
      expect(screen.getByText('5.14.1')).toBeInTheDocument()
      expect(screen.getByText('NVIDIA RTX A6000')).toBeInTheDocument()
      expect(screen.getByText('12.8')).toBeInTheDocument()
    })

    it('does NOT show the pre-D-045 "predates capture" population note', () => {
      render(<Provenance detail={POST_D045} />)
      expect(screen.queryByText(/predates/i)).not.toBeInTheDocument()
      expect(screen.queryByText(/environment capture began/i)).not.toBeInTheDocument()
    })

    it('does NOT render any environment field as "not captured"', () => {
      render(<Provenance detail={POST_D045} />)
      expect(screen.queryByText(/not captured/i)).not.toBeInTheDocument()
    })
  })

  describe('pre-D-045 fold (environment NOT captured)', () => {
    it('reads each absent environment field as "not captured" — never a value, never a bare em-dash', () => {
      render(<Provenance detail={PRE_D045} />)
      // Rule 1: absent environment field is "not captured", not "—" (which reads as "none").
      const notCaptured = screen.getAllByText(/not captured/i)
      expect(notCaptured.length).toBeGreaterThanOrEqual(1)
      // It must never fabricate the live values on a fold that never recorded them.
      expect(screen.queryByText('2.8.0+cu128')).not.toBeInTheDocument()
      expect(screen.queryByText('NVIDIA RTX A6000')).not.toBeInTheDocument()
    })

    it('names the gap ONCE at the population level, with the reason (D-046 rule 2 — a boolean is not a reason)', () => {
      render(<Provenance detail={PRE_D045} />)
      const notes = screen.getAllByText(/predates environment capture|environment capture began at D-045/i)
      expect(notes).toHaveLength(1)
      // The reason, not just a flag: the record is written worker-side and cannot be reconstructed.
      expect(screen.getByText(/cannot be reconstructed|written worker-side/i)).toBeInTheDocument()
    })

    it('still renders the weights and recipe it DID record (revision, dtype, chunk)', () => {
      render(<Provenance detail={PRE_D045} />)
      expect(screen.getByText('a1b2c3d')).toBeInTheDocument()
      expect(screen.getByText('int8')).toBeInTheDocument()
    })
  })

  describe('rule 3 — environment / recipe / weights are visually grouped and labelled', () => {
    it('groups the three provenance classes into distinct labelled regions', () => {
      render(<Provenance detail={POST_D045} />)
      // "what it ran on" (environment), "how it ran" (recipe), "what ran" (weights) — three groups.
      const env = screen.getByRole('group', { name: /environment/i })
      const recipe = screen.getByRole('group', { name: /recipe|compute/i })
      const weights = screen.getByRole('group', { name: /model|weights/i })
      // Each value lands in its correct group (assert via scoping, not global text).
      expect(within(env).getByText('NVIDIA RTX A6000')).toBeInTheDocument()
      expect(within(recipe).getByText('64')).toBeInTheDocument()
      expect(within(weights).getByText('a1b2c3d')).toBeInTheDocument()
    })
  })

  describe('not-applicable stays distinct from not-captured (the D-024/D-043 distinction in miniature)', () => {
    it('a whole-chain fold shows its boundary note and does not mislabel N/A slice bounds as "not captured"', () => {
      render(<Provenance detail={WHOLE_CHAIN} />)
      expect(screen.getByText(/no sliceable extracellular domain/i)).toBeInTheDocument()
    })
  })

  describe('no provenance-completeness score (D-046 §3 "deliberately not done")', () => {
    it('renders no percentage / completeness badge that would read documentation as quality', () => {
      render(<Provenance detail={PRE_D045} />)
      expect(screen.queryByText(/%|complete(ness)?|\bscore\b|well.documented/i)).not.toBeInTheDocument()
    })
  })
})
