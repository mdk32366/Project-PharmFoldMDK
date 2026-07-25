// D-048 §3.4 — per-residue pLDDT spread beside the mean (UI-depth §2.5).
//
// The mean HIDES the spread: NECTIN4 runs 50.1–93.4 per-residue on a mean of 77.26 (UI-depth §2.5).
// A single number cannot show that the model's own confidence varies across the molecule — which is
// precisely the deep-learning output the project claims to surface (D-015). This component states
// the spread (min / median / max) and the fraction of residues below the trust divider (60, D-039),
// so a reader sees how much of the chain is actually reliable, not just the average.
//
// "More informative, not more confident" (UI-depth trap c): this addition surfaces uncertainty, it
// never manufactures confidence — a wide spread on a high mean is shown as exactly that.
import { describe, it, expect } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import PlddtSpread from './PlddtSpread.jsx'

// NECTIN4-shaped: mean 77.26, per-residue 50.1..93.4 (the UI-depth §2.5 example).
const NECTIN4 = [50.1, 62.0, 71.5, 77.26, 84.0, 90.0, 93.4, 55.0, 68.0, 88.2]

describe('PlddtSpread — per-residue distribution (D-048 §3.4)', () => {
  it('renders nothing when there is no per-residue array (a failed/unfolded target)', () => {
    const { container } = render(<PlddtSpread plddt={null} />)
    expect(container).toBeEmptyDOMElement()
    const empty = render(<PlddtSpread plddt={[]} />)
    expect(empty.container).toBeEmptyDOMElement()
  })

  it('shows the min, median and max, so the spread the mean hides is visible', () => {
    render(<PlddtSpread plddt={NECTIN4} />)
    const min = screen.getByTestId('spread-min')
    const max = screen.getByTestId('spread-max')
    expect(min).toHaveTextContent('50.1')
    expect(max).toHaveTextContent('93.4')
    // median of the 10 sorted values = mean of the 5th/6th = (71.5+77.26)/2 = 74.38
    expect(screen.getByTestId('spread-median')).toHaveTextContent('74.4')
  })

  it('reports the fraction of residues below the trust divider (60), because that is what the mean buries', () => {
    render(<PlddtSpread plddt={NECTIN4} />)
    // 50.1 and 55.0 are < 60 → 2 of 10 → 20%.
    const belowNote = screen.getByTestId('spread-below-divider')
    expect(belowNote).toHaveTextContent('2')
    expect(belowNote).toHaveTextContent(/10|20%/)
  })

  it('renders a sparkline as an accessible image with a residue-count label (hand-rolled SVG, D-037)', () => {
    render(<PlddtSpread plddt={NECTIN4} />)
    const spark = screen.getByRole('img')
    expect(spark).toHaveAttribute('aria-label', expect.stringMatching(/10 residues/i))
  })

  it('does NOT restate a single headline confidence number that would re-hide the spread (trap c)', () => {
    render(<PlddtSpread plddt={NECTIN4} />)
    // No lone "mean"/"overall confidence" claim — this component's whole job is the spread, and the
    // Confidence element already owns the mean. Guard against re-collapsing to one number.
    expect(screen.queryByText(/overall confidence|single score/i)).not.toBeInTheDocument()
  })

  it('handles a flat high-confidence chain without inventing a spread', () => {
    render(<PlddtSpread plddt={[80, 80, 80, 80]} />)
    expect(screen.getByTestId('spread-min')).toHaveTextContent('80.0')
    expect(screen.getByTestId('spread-max')).toHaveTextContent('80.0')
    expect(screen.getByTestId('spread-below-divider')).toHaveTextContent('0')
  })
})
