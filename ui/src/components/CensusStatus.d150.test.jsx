// D-150 — the three orthogonal status axes, pinned against the protein that made them necessary.
//
// ⚠⚠ THE FIXTURE IS FAT2, AND IT IS SHAPED FROM THE LIVE PAYLOAD RATHER THAN INVENTED.
// `GET https://pharmfoldmdk.fly.dev/api/census/Q9NYQ8`, read 2026-09-09, answers:
//   folded              : true
//   structure_kind      : "assembled"
//   structure_kind_label: "assembled (provisional)"
//   hold48_kind         : "parent_stitched"
//   scored              : false
//   not_scored_reason   : "D-079 decision 1 — no census row is scored"
//   assembler_note      : "assembled by pLDDT overlap, not superimposed; seam not solved"
//   assembly_review.served_path.solved            : false
//   assembly_review.served_path.flipped           : false
//   assembly_review.served_path.not_flipped_reason: "not_in_pass_subset"
//
// **Four statuses, and the surface had one word for them.** A reader who saw `Folded` learned
// nothing about the seam and nothing about scoring, and a reader who saw `NOT FOLDED` — which is
// what a `tiles_only` row got, and what the pLDDT band said for every absent number — learned
// something false.
//
// ⚠ WHAT THIS FILE PINS THAT A COPY CHECK WOULD NOT. Asserting the new wording appears is the weak
// half; the strong half is asserting that the OLD reading is unavailable — that a folded,
// assembled, unscored protein cannot be rendered as NOT FOLDED, and cannot be rendered as
// finished either. Both directions are here, because a surface can acquire the new sentence and
// keep the old one beside it.
import { render, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import CensusTable from './CensusTable.jsx'
import CensusDetail from './CensusDetail.jsx'
import { unfoldedCopy } from './CensusProteinView.jsx'
import {
  STRUCTURE_ASSEMBLED_SERVED, STRUCTURE_NONE, STRUCTURE_ONESHOT, STRUCTURE_TILES_ONLY,
  scoreState, seamState, structureServed, structureServedLabel,
} from '../structureStatus.js'
import { bandFor } from '../plddt.js'

// ── the witness ────────────────────────────────────────────────────────────────────
const FAT2 = {
  id: 2837, accession: 'Q9NYQ8', gene: 'FAT2', label: 'Protocadherin Fat 2',
  span_aa: 4030, span_start: 19, span_end: 4048, full_length: 4349, tranche: 5,
  mean_plddt: 67.03, topology: 'contiguous', segment_count: 1,
  extracellular_total_aa: 4030, discarded_aa: 0, segments: '19-4048',
  span_definition: 'v2-ruled-vocabulary-2026-08-07',
  folded: true,
  hold48_kind: 'parent_stitched',
  structure_kind: 'assembled',
  structure_kind_label: 'assembled (provisional)',
  scored: false,
  not_scored_reason: 'D-079 decision 1 — no census row is scored',
  assembler_note: 'assembled by pLDDT overlap, not superimposed; seam not solved',
  assembly_review: {
    parent_job_id: 2837,
    assembler_note: 'assembled by pLDDT overlap, not superimposed; seam not solved',
    seam_note: 'IGF2R ≈ 88.76 Å is a measured caveat, not a solved structure. Seams are not '
      + 'scientifically solved. Kabsch-path artifacts are not on disk for this parent.',
    served_path: {
      decision: 'D-139', served: 'assembler', eligible: false, flipped: false,
      not_flipped_reason: 'not_in_pass_subset',
      not_flipped_note: 'This parent is not in the recorded D-126 PASS subset of 17, so the served '
        + 'path is the assembler. Artifacts on disk do not change that: the allowlist is the '
        + 'authority, never a pass count',
      gate_angstrom: 10.0, auto_flip: false, solved: false,
    },
  },
}

// A single-pass census row, for the axis the assembled case must stay distinct from.
const SINGLE = {
  id: 1901, accession: 'A0AVI2', gene: 'FER1L5', label: 'Fer-1-like protein 5',
  span_aa: 300, topology: 'contiguous', segment_count: 1, mean_plddt: 71.2, tranche: 3,
  folded: true, structure_kind: 'single-pass', structure_kind_label: 'single-pass',
  scored: false, not_scored_reason: 'D-079 decision 1 — no census row is scored',
}

// A never-folded row. ⚠ The card for these is NOT softened by D-150 and this fixture is here to
// prove it: NOT FOLDED must still be said, plainly, where it is true.
const HER2 = {
  id: null, accession: 'P04626', gene: 'ERBB2', label: 'Receptor tyrosine-protein kinase erbB-2',
  span_aa: 630, topology: null, mean_plddt: null, tranche: null, folded: false,
  not_folded_copy: 'not folded — its extracellular stretch is longer than the local graphics card '
    + 'can fold, so it is waiting on rented capacity',
}

// A tiles-only row. ⚠ The census serves no such row TODAY (measured 2026-09-09 over
// `/api/census?limit=5000`: 3,418 single-pass · 45 assembled · 3 mucin · 1 unrecorded · 0
// tiles_only), but the category is live in the payload vocabulary and in `unfoldedCopy`, and it is
// the case whose old rendering was flatly false.
const TILES = {
  id: 3, accession: 'Q00003', gene: 'TILES1', label: 'tiles one', span_aa: 1400, tranche: 5,
  mean_plddt: null, topology: null, folded: false,
  structure_kind: 'tiles_only', structure_kind_label: 'tiles only',
  not_folded_copy: 'tiles exist for this protein; they have not been assembled',
}

const MUCIN = {
  id: 4, accession: 'Q8WXI7', gene: 'MUC16', label: 'Mucin-16', span_aa: 22152, tranche: 5,
  mean_plddt: null, topology: 'contiguous', segment_count: 1, folded: false,
  structure_kind: 'mucin', structure_kind_label: 'mucin — not folded',
  not_folded_copy: 'mucin — out of class for this pipeline',
}

const table = (rows) => render(<MemoryRouter><CensusTable rows={rows} /></MemoryRouter>)
const card = (detail) => render(<MemoryRouter><CensusDetail detail={detail} /></MemoryRouter>)

const rowFor = (container, accession) =>
  [...container.querySelectorAll('tbody tr')]
    .find((tr) => tr.querySelector('td').textContent.includes(accession))

// ── axis A · the rule ──────────────────────────────────────────────────────────────
describe('D-150 axis A — what structure is served, as its own question', () => {
  it('reads FAT2 as an assembled parent that IS served, not as a fold verdict', () => {
    expect(structureServed(FAT2)).toBe(STRUCTURE_ASSEMBLED_SERVED)
  })

  it('separates the four categories the one badge used to merge', () => {
    expect(structureServed(SINGLE)).toBe(STRUCTURE_ONESHOT)
    expect(structureServed(TILES)).toBe(STRUCTURE_TILES_ONLY)
    expect(structureServed(HER2)).toBe(STRUCTURE_NONE)
    expect(structureServed(MUCIN)).toBe(STRUCTURE_NONE)
  })

  // ⚠⚠ THE NAMED FORBIDDEN CASE. A `tiles_only` row is served `folded: false` because no PARENT
  // was assembled — tile structures are on disk. Reading the denial first printed NOT FOLDED over
  // a payload that says the opposite, so the tiles branch runs AHEAD of it.
  it('never reads a tiles_only row as not folded, however the folded flag is set', () => {
    expect(structureServed(TILES)).toBe(STRUCTURE_TILES_ONLY)
    expect(structureServed({ ...TILES, folded: true })).toBe(STRUCTURE_TILES_ONLY)
    expect(structureServedLabel(TILES)).not.toMatch(/NOT FOLDED/)
    expect(structureServedLabel(TILES)).toMatch(/[Tt]iles only/)
  })

  // ⚠⚠ NEVER A BARE `Folded`. The word is true of a single-pass fold, of a provisional assembly
  // whose seam is not solved, and of a parent the D-139 gate refused — it cannot be wrong, which
  // is exactly why it told a reader nothing.
  it('refuses a bare "Folded" as the whole status of an assembled parent', () => {
    const label = structureServedLabel(FAT2)
    expect(label).not.toBe('Folded')
    expect(label).toMatch(/provisional/)
    expect(label).toMatch(/assembled/)
  })

  // ⚠ Even with the served label missing, `provisional` travels. An assembly whose label failed to
  // arrive must not become the one assembly on the site that reads as finished.
  it('keeps "provisional" when the API label is absent', () => {
    expect(structureServedLabel({ ...FAT2, structure_kind_label: null })).toMatch(/provisional/)
  })

  // ⚠ Not softened where it is true, and the three-way D-118 distinction survives.
  it('still says NOT FOLDED, and NOT FOLDED HERE, where those are the facts', () => {
    expect(structureServedLabel(HER2)).toBe('NOT FOLDED')
    expect(structureServedLabel({ ...HER2, cohort_fold: { mean_plddt: 70.2 } }))
      .toBe('NOT FOLDED HERE')
  })

  // ⚠⚠ A MISSING FIELD IS NOT A RECORDED `false` — the ruling `CensusTable`'s folded count and
  // `CensusProteinView`'s card gate have both carried since the field arrived. Legacy rows predate
  // it, and `!r.folded` would print NOT FOLDED over every one of them.
  it('does not read an absent folded field as a denial', () => {
    expect(structureServed({ ...SINGLE, folded: undefined })).toBe(STRUCTURE_ONESHOT)
    expect(structureServedLabel({ ...SINGLE, folded: undefined })).not.toMatch(/NOT FOLDED/)
  })
})

// ── axis B · scored ────────────────────────────────────────────────────────────────
describe('D-150 axis B — unscored is said, and never in fold language', () => {
  it('says the same thing for a folded assembly as for a never-folded row', () => {
    expect(scoreState(FAT2).label).toBe('Not scored, not ranked')
    expect(scoreState(HER2).label).toBe('Not scored, not ranked')
  })

  it('carries the reason, and names one when the row does not', () => {
    expect(scoreState(FAT2).reason).toMatch(/D-079 decision 1/)
    // ⚠ P55073 / DIO3 is live with `not_scored_reason: null`. `Not scored, not ranked. null` is
    // how an absence becomes a typo on a page.
    expect(scoreState({ not_scored_reason: null }).reason).toMatch(/D-079 decision 1/)
    expect(scoreState({ not_scored_reason: null }).reason).not.toMatch(/null/)
  })

  // ⚠⚠ THE FORBIDDEN VOCABULARY. "Not scored" must never be expressed as "not folded" or "no
  // structure" — those are claims about an artefact, and this axis is about a decision (D-079
  // dec 1) that applies to every census row regardless of what is on disk.
  it('uses no fold language and no missing-structure language to mean unscored', () => {
    for (const row of [FAT2, SINGLE, HER2, TILES]) {
      const { label, reason } = scoreState(row)
      expect(label).not.toMatch(/fold/i)
      expect(label).not.toMatch(/structure/i)
      expect(`${label} ${reason}`).not.toMatch(/NOT FOLDED/)
    }
  })
})

// ── axis C · the seam ──────────────────────────────────────────────────────────────
describe('D-150 axis C — the seam, and whose measurement it is', () => {
  it('reads FAT2 as a provisional assembler parent, not a solved one', () => {
    const seam = seamState(FAT2)
    expect(seam.key).toBe('provisional_assembler')
    expect(seam.label).toMatch(/not solved/i)
    expect(seam.label).not.toMatch(/\bsolved seam\b/i)
  })

  // ⚠⚠ THE IGF2R NUMBER IS A MEASUREMENT ON A DIFFERENT PROTEIN. `seam_note` quotes ≈ 88.76 Å, and
  // the census card used to print that sentence inline for every assembly — handing a reader of
  // FAT2 a true figure that was never about FAT2. The per-parent note is `assembler_note`.
  it('takes this parent\'s own note and does not paste IGF2R\'s angstroms onto it', () => {
    expect(seamState(FAT2).note).toBe(FAT2.assembler_note)
    expect(seamState(FAT2).note).not.toMatch(/88\.76/)
    expect(seamState(FAT2).note).not.toMatch(/IGF2R/)
  })

  // ⚠ A single-pass fold has no seam. Answering `n/a` about one invents a question nobody asked.
  it('asks nothing about a seam on a protein that was never tiled', () => {
    expect(seamState(SINGLE).key).toBe('n/a')
    expect(seamState(SINGLE).label).toBeNull()
    expect(seamState(HER2).key).toBe('n/a')
  })

  // ⚠⚠ AN ABSENT MEASUREMENT IS NOT A SOLVED SEAM. `assembly_review` rides on
  // `/api/census/{id}` and NOT on `/api/census` (measured 2026-09-09: the list row carries 34 keys
  // and that is not one of them), so the list must say the artefacts are absent rather than fall
  // to `n/a`, which reads as "this assembly has no seam question".
  it('names the absence when the payload carries no review, rather than falling silent', () => {
    const listRow = { ...FAT2, assembly_review: undefined, assembler_note: undefined }
    expect(seamState(listRow).key).toBe('artifacts_absent')
    expect(seamState(listRow).label).toMatch(/not on this payload/i)
    expect(seamState(listRow).label).not.toMatch(/solved/i)
  })

  // ⚠ `flipped` is the D-139 resolver's OWN answer, never re-derived from a pass count — and even
  // a flipped parent is not a solved one (`served_path.solved` is false for every parent).
  it('reads a D-139 flip off the resolver, and still refuses to call it solved', () => {
    const flipped = {
      ...FAT2,
      assembly_review: {
        ...FAT2.assembly_review,
        served_path: { ...FAT2.assembly_review.served_path, flipped: true, solved: false },
      },
    }
    expect(seamState(flipped).key).toBe('pass_path_served')
    expect(seamState(flipped).label).toMatch(/not solved/i)
  })
})

// ── the census LIST ────────────────────────────────────────────────────────────────
describe('D-150 — the census row states three statuses, not one', () => {
  it('gives FAT2 a structure chip, an unscored chip and a seam chip', () => {
    const { container } = table([FAT2, SINGLE])
    const cell = rowFor(container, 'Q9NYQ8').querySelector('.status-cell')
    expect(cell.textContent).toMatch(/assembled \(provisional\)/)
    expect(cell.textContent).toMatch(/Not scored, not ranked/)
    expect(cell.textContent).toMatch(/[Ss]eam/)
  })

  // ⚠⚠ THE EXIT CRITERION, AS AN ASSERTION. A folded, assembled parent cannot read as NOT FOLDED
  // anywhere on its row — not in the status column, not in the topology column, not in a tooltip.
  it('cannot be read as NOT FOLDED while folded is true and the kind is assembled', () => {
    const { container } = table([FAT2, SINGLE])
    const row = rowFor(container, 'Q9NYQ8')
    expect(row.textContent).not.toMatch(/NOT FOLDED/)
    const titles = [...row.querySelectorAll('[title]')].map((n) => n.getAttribute('title'))
    expect(titles.every((t) => !/NOT FOLDED/.test(t ?? ''))).toBe(true)
  })

  // ⚠ …and it cannot read as finished either. Both directions, because a surface can acquire the
  // honest sentence and keep the dishonest one next to it.
  it('never presents that row as a plain "Folded"', () => {
    const { container } = table([FAT2])
    const cell = rowFor(container, 'Q9NYQ8').querySelector('.status-cell')
    expect(cell.textContent).not.toMatch(/\bFolded\b/)
    expect(cell.textContent).toMatch(/provisional/)
  })

  // ⚠⚠ THE OTHER HALF OF "DO NOT SOFTEN". A never-folded row keeps the words it had.
  it('still shouts NOT FOLDED on a row that genuinely has no structure', () => {
    const { container } = table([FAT2, HER2])
    const row = rowFor(container, 'P04626')
    expect(row.textContent).toMatch(/NOT FOLDED/)
    expect(row.querySelector('.badge-unfolded')).not.toBeNull()
    // the reason still travels with the status (D-118's three outcomes)
    expect(row.querySelector('.badge-unfolded').getAttribute('title'))
      .toMatch(/longer than the local graphics card/)
  })

  // ⚠ The tiles copy is a fact about the tiles, so it does not ask the fold verdict first. Before
  // D-150 `unfoldedCopy` returned null for anything not `folded === false`, which would have left
  // the page's tiles card — gated on axis A, not on the flag — rendering two empty paragraphs.
  it('supplies the tiles copy without first requiring a fold denial', () => {
    expect(unfoldedCopy(TILES)?.bar).toMatch(/have not been assembled/)
    expect(unfoldedCopy({ ...TILES, folded: true })?.bar).toMatch(/have not been assembled/)
    expect(unfoldedCopy({ ...TILES, folded: true })?.body).toBeTruthy()
  })

  it('says "tiles only" and not "NOT FOLDED" anywhere on a tiles row', () => {
    const { container } = table([FAT2, TILES])
    const row = rowFor(container, 'Q00003')
    expect(row.textContent).not.toMatch(/NOT FOLDED/)
    expect(row.textContent).toMatch(/[Tt]iles only/)
    expect(row.querySelector('.badge-unfolded')).toBeNull()
  })

  // ⚠ The unscored chip is on EVERY row, including the ones with a good structure. A status that
  // appears only when something is wrong teaches a reader that silence means fine.
  it('carries the unscored chip on a folded row as well as an unfolded one', () => {
    const { container } = table([FAT2, SINGLE, HER2])
    for (const acc of ['Q9NYQ8', 'A0AVI2', 'P04626']) {
      expect(rowFor(container, acc).querySelector('.status-cell').textContent)
        .toMatch(/Not scored, not ranked/)
    }
  })

  it('names the three questions in the legend before it names the categories', () => {
    const { container } = table([FAT2, SINGLE, HER2])
    const legend = container.querySelector('.census-legend').textContent
    expect(legend).toMatch(/Three separate questions/)
    expect(legend).toMatch(/still be unscored/)
    expect(legend).toMatch(/never means/)
    expect(legend).toMatch(/not a solved seam/i)
  })

  // ⚠ D-087: the table sorts on every column, and a status column that did not would be the
  // defect D-133 had to repair for Structure.
  it('offers the status column as a real sortable header', () => {
    table([FAT2, SINGLE])
    expect(screen.getByRole('button', { name: /Status \(structure · score · seam\)/ }))
      .toBeInTheDocument()
  })
})

// ── the census CARD ────────────────────────────────────────────────────────────────
describe('D-150 — the census card states three statuses, not one', () => {
  it('renders a structure line, a seam line and an unscored line for FAT2', () => {
    const { container } = card(FAT2)
    const status = within(container.querySelector('.status-list'))
    expect(status.getByText(/Structure:/).closest('li').textContent)
      .toMatch(/assembled \(provisional\)/)
    expect(status.getByText(/Seam:/).closest('li').textContent).toMatch(/not solved/i)
    expect(container.querySelector('.status-unscored').textContent)
      .toMatch(/Not scored, not ranked/)
  })

  it('cannot be read as NOT FOLDED, and cannot be read as finished', () => {
    const { container } = card(FAT2)
    const status = container.querySelector('.status-list').textContent
    expect(status).not.toMatch(/NOT FOLDED/)
    expect(status).not.toMatch(/\bFolded\b/)
    expect(status).toMatch(/provisional/)
    expect(status).toMatch(/not solved/i)
  })

  // ⚠⚠ THE FIXTURE THE REVERT PROOF DEMANDED, AND IT WAS MISSING. Restoring the bare-`Folded`
  // fallback on the card left every vitest case GREEN — because the old expression was
  // `structure_kind_label ?? (folded === false ? 'NOT FOLDED' : 'Folded')`, and **every fixture in
  // this file carries a label**, so the branch that says `Folded` was never entered (`A-017`: a
  // guard that does not enter the path is not a guard). Only the Python source guard caught it.
  // ⚠ This case removes the label, which is the ONLY state in which the defect was ever visible.
  it('says provisional rather than "Folded" when the API label is missing from an assembly', () => {
    const { container } = card({ ...FAT2, structure_kind_label: null })
    const line = container.querySelector('.status-structure').textContent
    expect(line).not.toMatch(/\bFolded\b/)
    expect(line).toMatch(/provisional/)
  })

  // ⚠ …and the same hole on the LIST. A row whose label failed to arrive must not become the one
  // assembly on the site that reads as finished.
  it('says provisional on a list row whose assembled label is missing', () => {
    const { container } = table([{ ...FAT2, structure_kind_label: null }])
    const cell = rowFor(container, 'Q9NYQ8').querySelector('.status-cell')
    expect(cell.textContent).not.toMatch(/\bFolded\b/)
    expect(cell.textContent).toMatch(/provisional/)
  })

  // ⚠⚠ THE INLINE IGF2R FIGURE IS GONE FROM THE CARD. It read "Seam not solved (IGF2R ≈ 88.76 Å is
  // a measured caveat, not a solved structure)" on every assembly — another protein's measurement,
  // rendered as part of this protein's status.
  it('quotes this parent\'s own seam note and not IGF2R\'s angstroms', () => {
    const { container } = card(FAT2)
    const status = container.querySelector('.status-list').textContent
    expect(status).toMatch(/not superimposed; seam not solved/)
    expect(status).not.toMatch(/88\.76/)
    expect(status).not.toMatch(/IGF2R/)
  })

  it('states unscored as a status about scoring, not as a statement about structure', () => {
    const { container } = card(FAT2)
    const line = container.querySelector('.status-unscored').textContent
    expect(line).toMatch(/D-079 decision 1/)
    expect(line).toMatch(/not.*about whether a structure exists/i)
  })

  it('gives a single-pass fold no seam line at all', () => {
    const { container } = card(SINGLE)
    expect(container.querySelector('.status-seam')).toBeNull()
    expect(container.querySelector('.status-structure').textContent).toMatch(/single-pass/)
  })

  it('keeps NOT FOLDED on the card of a protein that has no structure', () => {
    const { container } = card(HER2)
    expect(container.querySelector('.status-structure').textContent).toMatch(/NOT FOLDED/)
  })

  // ⚠ The page-level companion to this — *the fold verdict is said once, not three times* — lives
  // in `CensusProteinView.test.jsx`, which already carries the api / viewer mocks a whole page
  // needs. Duplicating those here would make this file's fixtures answer to a second harness.
})

// ── the pLDDT band ─────────────────────────────────────────────────────────────────
describe('D-150 — an absent pLDDT is not an absent fold', () => {
  // ⚠⚠ FAT2 HAS A pLDDT (67.03) AND ITS PER-RESIDUE ARRAY STILL HAS GAPS. `bandFor` is the colour
  // function 3Dmol calls for every residue of a structure that is on disk and rendering; returning
  // `not folded` there said the fold did not happen, inside the drawing of the fold.
  it('does not say "not folded" for a null value', () => {
    expect(bandFor(null).label).toBe('no pLDDT')
    expect(bandFor(null).label).not.toMatch(/fold/i)
  })

  it('leaves the value bands untouched, so FAT2\'s own mean still lands where it did', () => {
    expect(bandFor(FAT2.mean_plddt).label).toBe('Moderate')
  })
})
