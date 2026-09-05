import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import Confidence from './Confidence.jsx'
import { COHORT_MAX_PLDDT } from '../plddt.js'

// ⚠ F-038: the top band's caveat is a statement about the COHORT ("cohort max 84.23"). It was
// rendered unchanged on census protein pages, where the max is 89.25 and six rows exceed it.
describe('Confidence caveat', () => {
  it('keeps the cohort note by default — target pages are unchanged', () => {
    render(<Confidence meanPlddt={80} plddt={[80]} />)
    expect(screen.getByText(new RegExp(String(COHORT_MAX_PLDDT)))).toBeInTheDocument()
  })

  it('accepts an override so a page can state its own population', () => {
    render(<Confidence meanPlddt={89.25} plddt={[89]} caveat="not the cohort's ceiling" />)
    expect(screen.getByText(/not the cohort's ceiling/)).toBeInTheDocument()
    expect(screen.queryByText(new RegExp(String(COHORT_MAX_PLDDT)))).not.toBeInTheDocument()
  })

  // ⚠ An empty string must SUPPRESS the note, not fall back to the cohort's. `caveat=""` is a
  // caller saying "this population has nothing to add", and defaulting it back would restate the
  // very claim the caller removed.
  it('suppresses the note entirely when given an empty caveat', () => {
    render(<Confidence meanPlddt={80} plddt={[80]} caveat="" />)
    expect(screen.queryByText(new RegExp(String(COHORT_MAX_PLDDT)))).not.toBeInTheDocument()
  })

  it('still calls pLDDT a self-report whatever the caveat says', () => {
    render(<Confidence meanPlddt={80} plddt={[80]} caveat="" />)
    expect(screen.getByText(/self-reported/i)).toBeInTheDocument()
  })

  it('renames the header on an assembled chain', () => {
    render(<Confidence meanPlddt={61.07} plddt={[61]} assembled caveat="" />)
    expect(screen.getByRole('heading', { name: /Assembled-chain pLDDT/ })).toBeInTheDocument()
    expect(screen.getByText(/winner tile per residue/)).toBeInTheDocument()
  })
})
