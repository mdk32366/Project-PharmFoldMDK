import { Link } from 'react-router-dom'

// D-155 — the two pieces `/coverage` owned that are facts about a ROW rather than about a page.
//
// ⚠⚠ MOVED, NOT REWRITTEN. `CoverageView.jsx` is gone: one population had two tables, and the
// merged surface is `/targets`. Everything below arrived from that file with its reasoning intact,
// because a comment explaining why a chip refuses to carry an id is the thing most likely to be
// lost in a merge and most expensive to re-derive. ⚠ `ui/src/searchRows.js` is the precedent — the
// matcher moved to a module when a second surface needed it rather than being pasted (`F-052`).
//
// ⚠ The one deliberate change is WHERE the output lands: on `/coverage` these rendered into a Note
// column that was **58% of the table's width with content on 3 of 82 rows** (measured 2026-09-10,
// 696 px of 1,200, one cell 765 characters long). On the merged table the same nodes render inside
// the row's Status cell disclosure, so the three rows that have a reason still show every character
// of it and the seventy-nine that do not stop paying for the column.

// D-120 / PLAN §3.4 — IGF2R two populations; FAT2 tileable vs MUC16 mucin.
//
// ⚠⚠ THE NOTE RETURNS A NODE, NOT A STRING (D-135). It used to return 209 characters of
// two-population prose for IGF2R — correct, and unreadable in a `<td>` between a tier and a fold
// status. Since D-134 that accession's census representative is finally visible as an ASSEMBLED
// parent rather than mis-served as single-pass, so the paragraph can be replaced by the thing it was
// gesturing at: one sentence and a link to the page that holds the other measurement.
export function coverageNote(r) {
  const sibling = censusBridge(r)
  if (r.accession === 'P11717' || r.gene === 'IGF2R') {
    const fail = r.fail_reason ? `${r.fail_reason} ` : ''
    // ⚠ The bridge does not replace the FACT that the cohort attempt failed — it follows it. The
    // fold chip still reads `failed` and the reason is still the first thing in this block.
    return <>{fail}{sibling ?? 'A later census tiling of this accession is a different span '
      + 'definition (D-081) — see Census. Neither substitutes for the other.'}</>
  }
  if (r.gene === 'FAT2') {
    // ⚠ FAT2's census representative is TILES, and tiles are windows rather than the protein
    // (D-118) — so `census_sibling.folded` is false, no bridge renders, and the existing sentence
    // stands. The bridge is for a different MEASUREMENT, never for a different queue position.
    return <>{r.exclusion_reason || ''} {sibling ?? 'FAT2 is tileable in the census; that is not this cohort row.'}</>
  }
  if (r.gene === 'MUC16') {
    return `${r.exclusion_reason || ''} MUC16 is a mucin — out of class; never ESMFold.`
  }
  if (r.excluded) return <>{r.exclusion_reason}{sibling}</>
  if (r.fold_status === 'failed') return <>{r.fail_reason}{sibling}</>
  return sibling ?? ''
}

// ⚠ Does this row have anything to disclose at all? The merged Status cell asks before it renders a
// control: a "why" toggle that opens onto nothing is worse than no toggle, because it promises a
// reason the record does not hold. ⚠ It asks the same questions `coverageNote` answers, in the same
// order, rather than testing the rendered output — a node is not a string and `''` is not falsy in
// JSX once it has been wrapped in a fragment.
export function hasCoverageNote(r) {
  if (!r) return false
  if (r.accession === 'P11717' || r.gene === 'IGF2R') return true
  if (r.gene === 'FAT2' || r.gene === 'MUC16') return true
  if (r.excluded && r.exclusion_reason) return true
  if (r.fold_status === 'failed' && r.fail_reason) return true
  return Boolean(censusBridge(r))
}

// ⚠⚠ THE BRIDGE, AND WHAT IT REFUSES TO SAY. `census_sibling` is present only on a cohort row that
// did NOT fold here and whose accession has a census representative — a DIFFERENT measurement of the
// same protein, under a different span definition (D-081). So the chip says *a structure of this
// protein exists over there*, and never *this target folded*: the Fold chip still reads `failed`
// or `not yet`, the tier and the reason are untouched, and no fourth `fold_status` was invented
// (D-043's three values stand — a census fact does not belong inside the cohort's vocabulary).
//
// ⚠⚠ THE LINK IS BUILT FROM THE ACCESSION, AND THE PAYLOAD CARRIES NO CENSUS `analysis_id` AT ALL.
// That is deliberate on both sides. 75 of the 82 cohort accessions are also census rows, and a
// census id reaching a cohort surface is a named stop condition — the Gene cell's own
// `/target/:analysis_id` link would then open a fold measured under the other span definition with
// nothing on screen saying so. `/census/:accession` has resolved accessions since D-118, so the id
// is not needed; not serving it means it cannot be rendered here by mistake.
// ⚠⚠ AND THE RULE SURVIVES THE MERGE UNCHANGED (D-155). The merged table renders BOTH links in one
// row — the cohort's `/target/:id` on the gene and this one on the accession — which makes the
// separation more load-bearing than it was on `/coverage`, not less. The labelled chip and the
// sentence after it are what keep them distinguishable.
export function censusBridge(r) {
  const s = r.census_sibling
  // ⚠ Only where the cohort has no fold of its own. Where it does, the census is not the
  // interesting fact and a note would be noise on sixty-odd rows.
  // ⚠⚠ AND ONLY WHERE A STRUCTURE ACTUALLY EXISTS. `folded` is served (never re-derived here) and
  // is false for `tiles_only` and `mucin`: pointing a reader at tile windows as though they were a
  // measurement of the protein is the D-118 confusion, and this is the honesty surface.
  if (!s || !s.folded || r.fold_status === 'folded' || !r.accession) return null
  return (
    <>
      {' '}
      <Link className="chip chip-census-sibling" to={`/census/${r.accession}`}
            title={s.assembler_note || undefined}>
        census: {s.structure_kind_label} →
      </Link>{' '}
      <span className="census-sibling-note">
        a different population, measured under a different span definition — not this cohort fold.
      </span>
    </>
  )
}
