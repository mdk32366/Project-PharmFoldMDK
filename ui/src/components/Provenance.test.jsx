// D-048 / D-070 / D-071 — the THREE-valued provenance render, ordered by strength:
//   state 1 (measured at fold time): fold_provenance carries env keys → four fields, UNqualified.
//   state 2 (measured later, same tier): tier_environment present → four fields, WITH the qualifier.
//   state 3 (absent): neither → one "not recorded" statement + D-070's "what we can say" block.
// The bugs it cannot tolerate: rendering an inferred/absent value as measured, or letting a reader
// mistake a later measurement (state 2) for fold-time capture (state 1). Assertions are on rendered
// text/roles as a reader meets them, not component internals.
import { describe, it, expect } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import Provenance from './Provenance.jsx'

// STATE 1 — full environment captured AT fold time (a rental fold from the 07-25 pod).
const STATE1 = {
  boundary_method: 'sliced_ecd', ecd_start: 25, ecd_end: 1637, uniprot_release: '2025_03', tier: 'rental',
  fold_provenance: {
    model_id: 'facebook/esmfold_v1', model_revision: 'a1b2c3d', dtype: 'float16', chunk_size: 64,
    input_length: 1612, ca_atom_count: 1612, truncated: false, folded_at: '2026-07-24T18:40:00Z',
    torch_version: '2.8.0+cu128', transformers_version: '5.14.1',
    device_name: 'NVIDIA RTX A6000', cuda_version: '12.8',
  },
}
// STATE 2 — an uncaptured LOCAL fold; the tier was measured later (D-071). Distinct values from STATE1
// so a leak between the two would be caught.
const STATE2 = {
  boundary_method: 'sliced_ecd', ecd_start: 30, ecd_end: 350, uniprot_release: '2025_02', tier: 'local',
  fold_provenance: {
    model_id: 'facebook/esmfold_v1', model_revision: 'a1b2c3d', dtype: 'int8', chunk_size: 64,
    input_length: 320, ca_atom_count: 320, truncated: false, folded_at: '2026-07-20T10:00:00Z',
    // no environment keys — not captured at fold time
  },
  tier_environment: {
    torch_version: '2.11.0+cu128', transformers_version: '5.14.1',
    device_name: 'NVIDIA RTX PRO 2000 Blackwell Generation Laptop GPU', cuda_version: '12.8',
    measured_at: '2026-07-29',
  },
}
// STATE 3 — an uncaptured RENTAL fold with NO tier record (the pods are gone — D-071 dec 3). Whole-chain.
const STATE3 = {
  boundary_method: 'whole', ecd_start: null, ecd_end: null, uniprot_release: '2025_03', tier: 'rental',
  fold_provenance: { ...STATE2.fold_provenance, folded_at: '2026-07-23T00:00:00Z' },
  // no tier_environment
}

describe('Provenance — three-valued strength (D-071)', () => {
  describe('state 1 — measured at fold time', () => {
    it('renders each captured value verbatim, UNqualified (no later-measurement caveat)', () => {
      const { container } = render(<Provenance detail={STATE1} />)
      expect(screen.getByText('2.8.0+cu128')).toBeInTheDocument()
      expect(screen.getByText('NVIDIA RTX A6000')).toBeInTheDocument()
      const t = container.textContent
      expect(t).not.toMatch(/not recorded at fold time/i)
      expect(t).not.toMatch(/What we can say/)
    })
  })

  describe('state 2 — measured later, same tier', () => {
    it('renders the tier values, ALWAYS with the qualifier and its date (never unqualified)', () => {
      const { container } = render(<Provenance detail={STATE2} />)
      expect(screen.getByText('2.11.0+cu128')).toBeInTheDocument()
      expect(screen.getByText('NVIDIA RTX PRO 2000 Blackwell Generation Laptop GPU')).toBeInTheDocument()
      const t = container.textContent
      expect(t).toMatch(/tier environment, measured 2026-07-29.*not recorded at fold time/)
      // not dressed as fold-time capture, not collapsed to the state-3 statement
      expect(t).not.toMatch(/Not recorded at fold time/)
      expect(t).not.toMatch(/What we can say/)
    })
    it('does NOT leak state-1 fold-time values into a later-measured fold', () => {
      render(<Provenance detail={STATE2} />)
      expect(screen.queryByText('2.8.0+cu128')).not.toBeInTheDocument()
      expect(screen.queryByText('NVIDIA RTX A6000')).not.toBeInTheDocument()
    })
  })

  describe('state 3 — absent', () => {
    it('renders ONE clear statement (not a four-field "not captured" grid) plus the D-070 block', () => {
      const { container } = render(<Provenance detail={STATE3} />)
      const t = container.textContent
      expect(t).toMatch(/Not recorded at fold time.*not recoverable/)
      // the four-"not captured"-fields grid is gone (the polish); no version or device rendered
      expect(t).not.toMatch(/not captured/i)
      expect(t).not.toMatch(/2\.11\.0|2\.8\.0/)
      expect(t).not.toMatch(/RTX PRO 2000|A6000/)
      // D-070's block still travels, reason preserved, manifest named not shown
      expect(t).toMatch(/What we can say/)
      expect(t).toMatch(/rental tier/)
      expect(t).toMatch(/worker\/requirements\.txt/)
      expect(t).toMatch(/capture began later \(D-045\)/)
      expect(t).toMatch(/cannot be reconstructed/)
    })
    it('a LOCAL uncaptured fold is state 2, not state 3 — the tier record fills it', () => {
      const { container } = render(<Provenance detail={STATE2} />)
      expect(container.textContent).not.toMatch(/Not recorded at fold time/)
    })
  })

  describe('the asymmetry stays legible — measured tier vs vanished pod', () => {
    it('state 2 shows version values; state 3 shows none — tellable without effort', () => {
      const two = render(<Provenance detail={STATE2} />)
      expect(two.container.textContent).toMatch(/\d+\.\d+\.\d+\+cu/)   // versions present
      two.unmount()
      const three = render(<Provenance detail={STATE3} />)
      expect(three.container.textContent).not.toMatch(/\d+\.\d+\.\d+\+cu/)  // no version at all
    })
  })

  describe('rule 3 — environment / recipe / weights grouped and labelled (state 1)', () => {
    it('groups the three provenance classes into distinct labelled regions', () => {
      render(<Provenance detail={STATE1} />)
      const env = screen.getByRole('group', { name: /environment/i })
      const recipe = screen.getByRole('group', { name: /recipe|compute/i })
      const weights = screen.getByRole('group', { name: /model|weights/i })
      expect(within(env).getByText('NVIDIA RTX A6000')).toBeInTheDocument()
      expect(within(recipe).getByText('64')).toBeInTheDocument()
      expect(within(weights).getByText('a1b2c3d')).toBeInTheDocument()
    })
  })

  describe('not-applicable stays distinct; no completeness score', () => {
    it('a whole-chain fold shows its boundary note (state 3)', () => {
      render(<Provenance detail={STATE3} />)
      expect(screen.getByText(/no sliceable extracellular domain/i)).toBeInTheDocument()
    })
    it('renders no percentage / completeness badge (D-046 §3)', () => {
      render(<Provenance detail={STATE3} />)
      expect(screen.queryByText(/%|complete(ness)?|well.documented/i)).not.toBeInTheDocument()
    })
  })
})
