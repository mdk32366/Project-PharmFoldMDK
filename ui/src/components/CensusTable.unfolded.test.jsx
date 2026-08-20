import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import CensusTable from './CensusTable.jsx'

// ⚠⚠ THE OWNER'S CASE, AS A FIXTURE. Searching HER2 returned "no protein matches that search".
// HER2 is in the manifest and was never folded. The ruling: show it, with a status of NOT FOLDED.
const FOLDED = {
  id: 1, accession: 'P28908', gene: 'TNFRSF8', label: 'TNF receptor superfamily member 8',
  span_aa: 367, topology: 'contiguous', mean_plddt: 68.4, tranche: 4,
  profile_status: 'computed', folded: true,
}
const HER2 = {
  id: null, accession: 'P04626', gene: 'ERBB2', label: 'Receptor tyrosine-protein kinase erbB-2',
  span_aa: 630, topology: null, mean_plddt: null, tranche: null, profile_status: null,
  folded: false, not_folded_reason: 'above_local_ceiling',
  not_folded_copy: 'not folded — its extracellular stretch is longer than the local graphics card can fold, so it is waiting on rented capacity',
  staining: null, aliases: ['HER2'],
}
const draw = (rows) => render(<MemoryRouter><CensusTable rows={rows} /></MemoryRouter>)

describe('never-folded proteins are LISTED, not hidden', () => {
  it('finds HER2 by its alias and shows the row', () => {
    draw([FOLDED, HER2])
    expect(screen.getByText('P04626')).toBeTruthy()
    expect(screen.getByText('ERBB2')).toBeTruthy()
  })

  // ⚠⚠ the status, in the column the reader is already scanning — not in fine print
  it('shows NOT FOLDED as a status on the row itself', () => {
    const { container } = draw([FOLDED, HER2])
    const badge = container.querySelector('.badge-unfolded')
    expect(badge).not.toBeNull()
    expect(badge.textContent).toMatch(/NOT FOLDED/)
  })

  it('carries the REASON, not just the status', () => {
    const { container } = draw([FOLDED, HER2])
    expect(container.querySelector('.badge-unfolded').getAttribute('title'))
      .toMatch(/longer than the local graphics card/)
  })

  // ⚠ the row must be clickable — by accession, since it has no analysis id
  it('links a never-folded row by accession, not by a null id', () => {
    const { container } = draw([FOLDED, HER2])
    const hrefs = [...container.querySelectorAll('a')].map((a) => a.getAttribute('href'))
    expect(hrefs).toContain('/census/P04626')
    expect(hrefs.some((h) => h === '/census/null')).toBe(false)
  })

  // ⚠⚠ NO FOLD-DERIVED VALUE MAY APPEAR. There is no structure, so there is nothing to report.
  it('shows no pLDDT, no profile and no staining for a never-folded row', () => {
    const { container } = draw([HER2])
    const row = container.querySelector('tbody tr')
    expect(row.textContent).not.toMatch(/computed/)
    expect(row.textContent).not.toMatch(/\d+\.\d+\s*$/)
    expect(row.textContent).not.toMatch(/%/)
  })

  // ⚠ the count states BOTH populations; "N folded proteins" over a mixed table would be false
  it('states the folded and never-folded counts separately', () => {
    const t = draw([FOLDED, HER2]).container.textContent
    expect(t).toMatch(/1\s*folded/)
    expect(t).toMatch(/never folded/)
  })

  it('a row with no folded field is treated as folded, not as never folded', () => {
    // ⚠ legacy rows predate the field; `!r.folded` would have mislabelled every one of them
    const { container } = draw([{ ...FOLDED, folded: undefined }])
    expect(container.querySelector('.badge-unfolded')).toBeNull()
  })
})

describe('units are expanded on first use', () => {
  it('the span column says what aa means', () => {
    draw([FOLDED])
    // ⚠ "aa" is standard to a structural biologist and opaque to everyone else
    expect(screen.getByRole('button', { name: /amino acids/ })).toBeTruthy()
  })
})
