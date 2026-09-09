import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getCoverage, getCensusSummary } from '../api.js'
import { filterRows } from '../searchRows.js'
import CoverageLine from './CoverageLine.jsx'
import CensusPopulationStrip from './CensusPopulationStrip.jsx'

// The full cohort (UI Plan v2 §3.3): all 82 reachable — what is ranked, held out and why, excluded
// and why by name, folded, failed (with reason), and not-yet. Held-out and excluded rows are PRESENT,
// not silently absent (D-022: "MUC16 is CA-125; a reviewer who knows the field notices its absence
// immediately"). fold_status is three-valued (D-043): attempted-and-failed is shown as distinct from
// never-attempted, with jobs.error as the reason. Served by GET /api/coverage (D-038), not the list.
//
// ⚠⚠ TWO POPULATIONS, TWO STRIPS, AND NEVER ONE NUMBER STANDING FOR THE OTHER (D-135). The page
// used to describe the cohort and say nothing about the census, so a reader who arrived at "the
// honest denominator" learned the shape of 82 proteins and left believing that was the whole of the
// work. The remedy is a SECOND, LABELLED population below the coverage line — not a bigger figure
// inside it. `CoverageLine` keeps its own math untouched and its headline is still the cohort
// intersection alone; the census strip carries no denominator and no fraction at all.
const ORDER = { excluded: 0, held_out: 1, ranked: 2 }

// D-120 / PLAN §3.4 — IGF2R two populations; FAT2 tileable vs MUC16 mucin.
//
// ⚠⚠ THE NOTE RETURNS A NODE, NOT A STRING (D-135). It used to return 209 characters of
// two-population prose for IGF2R — correct, and unreadable in a `<td>` between a tier and a fold
// status. Since D-134 that accession's census representative is finally visible as an ASSEMBLED
// parent rather than mis-served as single-pass, so the paragraph can be replaced by the thing it was
// gesturing at: one sentence and a link to the page that holds the other measurement.
function coverageNote(r) {
  const sibling = censusBridge(r)
  if (r.accession === 'P11717' || r.gene === 'IGF2R') {
    const fail = r.fail_reason ? `${r.fail_reason} ` : ''
    // ⚠ The bridge does not replace the FACT that the cohort attempt failed — it follows it. The
    // fold cell still reads `failed` and the reason is still the first thing in this cell.
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

// ⚠⚠ THE BRIDGE, AND WHAT IT REFUSES TO SAY. `census_sibling` is present only on a cohort row that
// did NOT fold here and whose accession has a census representative — a DIFFERENT measurement of the
// same protein, under a different span definition (D-081). So the chip says *a structure of this
// protein exists over there*, and never *this target folded*: the Fold column still reads `failed`
// or `not yet`, the tier and the reason are untouched, and no fourth `fold_status` was invented
// (D-043's three values stand — a census fact does not belong inside the cohort's vocabulary).
//
// ⚠⚠ THE LINK IS BUILT FROM THE ACCESSION, AND THE PAYLOAD CARRIES NO CENSUS `analysis_id` AT ALL.
// That is deliberate on both sides. 75 of the 82 cohort accessions are also census rows, and a
// census id reaching a cohort surface is a named stop condition — the Gene cell's own
// `/target/:analysis_id` link would then open a fold measured under the other span definition with
// nothing on screen saying so. `/census/:accession` has resolved accessions since D-118, so the id
// is not needed; not serving it means it cannot be rendered here by mistake.
function censusBridge(r) {
  const s = r.census_sibling
  // ⚠ Only where the cohort has no fold of its own. Where it does, the census is not the
  // interesting fact and a note would be noise on sixty-odd rows.
  // ⚠⚠ AND ONLY WHERE A STRUCTURE ACTUALLY EXISTS. `folded` is served (never re-derived here) and
  // is false for `tiles_only` and `mucin`: pointing a reader at tile windows as though they were a
  // measurement of the protein is the D-118 confusion, and this page is the honesty page.
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

// ⚠⚠ D-152 — THE CENSUS TREATMENT ON `/coverage`, AND THE ONE THING THIS PAGE WAS MISSING ENTIRELY
// WAS A WAY TO FIND A ROW. Owner, 2026-09-09: *"Apply what was done for Census to the rest of the
// surfaces. 100 percent better and easier to navigate."* `/census` has had a search box since D-087
// and `/targets` since the owner searched `HER2` and found nothing; `/coverage` lists the same 82
// proteins and had none, so the only way to answer *"is MUC16 in here, and what does it say?"* was
// to read 82 rows. ⚠ **A surface that lists proteins and cannot find one is the F-052 shape** — a
// convention every list obeys except this one.
//
// ⚠ The matcher is the SHARED one (`../searchRows.js`), never a third copy: it already reaches
// aliases, so `CA-125` finds `MUC16` here exactly as it does on the other two lists. A local
// `filter(r => r.gene.includes(q))` would have been four lines and a fourth behaviour.
export default function CoverageView() {
  const [data, setData] = useState(null)
  const [census, setCensus] = useState(null)
  const [error, setError] = useState(null)
  const [query, setQuery] = useState('')

  useEffect(() => {
    getCoverage().then(setData).catch((e) => setError(e.message))
    // ⚠ ADDITIVE, and guarded the way the Story's census fetch is: `Promise.resolve().then(...)`
    // so a supplier that throws synchronously — or is not a promise at all — costs the second strip
    // and never the honest-denominator page this route exists to serve.
    Promise.resolve().then(() => getCensusSummary()).then(setCensus).catch(() => setCensus(null))
  }, [])

  if (error) return <p className="error">Could not load coverage: {error}</p>
  if (!data) return <p className="loading">Loading coverage…</p>

  const sorted = [...data.rows].sort(
    (a, b) => ORDER[a.disposition] - ORDER[b.disposition] || (a.gene || '').localeCompare(b.gene || ''),
  )
  const rows = filterRows(sorted, query)
  const narrowed = rows.length !== sorted.length

  return (
    <div className="coverage">
      <h2>Coverage — the honest denominator</h2>
      {/* ⚠⚠ THE COHORT HEADLINE, AND IT IS NOT SHARED. `CoverageLine` receives the cohort payload
          and only the cohort payload; the census summary is not threaded into it and must not be.
          The one number this page leads with is `ranked ∧ folded` of the cohort denominator
          (D-024 am. §3), and it stays that number however large the population below it is.
          ⚠ D-152 does not touch it and does not collapse it. It is the claim the route exists to
          make, and a headline behind a `<summary>` is a headline the page has decided the reader
          may skip. */}
      <CoverageLine coverage={data.coverage} rows={data.rows} />
      {/* ⚠⚠ D-152 — THE SEARCH SITS DIRECTLY UNDER THE HEADLINE AND DIRECTLY OVER THE TABLE, which
          is the whole of D-151's first rule: the thing the reader came for comes first. */}
      <div className="list-controls">
        <label htmlFor="coverage-search">Search</label>
        <input
          id="coverage-search"
          type="search"
          className="row-search"
          value={query}
          placeholder="gene, accession, or a name like CA-125"
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      {/* ⚠⚠ THE COUNT REPORTS WHAT IS ON SCREEN, AND IT NAMES THE DENOMINATOR IT IS A FRACTION OF.
          On THIS page that matters more than on any other: the surface exists to defend one
          denominator (D-024), so a filtered table under an unqualified total would undercut the
          exact claim above it. ⚠ It appears only when the two differ — a permanent
          "Showing 82 of 82" is noise that teaches a reader to stop reading the line. */}
      {narrowed && (
        <p className="note filter-count">
          Showing {rows.length} of {sorted.length} cohort rows matching &ldquo;{query.trim()}&rdquo;
          {rows.length === 0 && <> — nothing here matches. <strong>Every one of the {sorted.length}{' '}
            cohort targets is in this table</strong>, held out and excluded rows included (D-022), so
            a name that returns nothing is outside the cohort rather than merely unfolded.</>}
          {' '}The denominator above is unchanged: it is a property of the cohort, not of this filter.
        </p>
      )}
      {/* ⚠⚠ D-152 — THE BOUNDED PORT. The Note column holds prose (a fold failure reason, an
          exclusion reason, and for IGF2R a census bridge chip with a sentence after it), so six
          columns are wider than they look. The port keeps the widest row from setting the width of
          the DOCUMENT, and it is what the shared `.table-scroll thead th` sticky rule resolves
          against — 82 rows scroll past a header that stays put.
          ⚠ No column is dropped and no cell is truncated: the held-out and excluded rows and their
          named reasons are the reason this page exists (D-022). */}
      <div className="table-scroll">
      <table className="cohort-table">
        <thead>
          <tr>
            <th>Gene</th><th>Accession</th><th>Disposition</th><th>Tier</th><th>Fold</th><th>Note</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.accession} className={`disp-${r.disposition}`}>
              <td>
                {/* ⚠⚠ THE COHORT'S OWN FOLD, OR NO LINK. This cell links to `/target/:analysis_id`
                    and the id is the COHORT's; a census id must never reach it (D-135). The census
                    sibling is reachable only from the Note cell, by accession, and labelled. */}
                {r.fold_status === 'folded' && r.analysis_id != null
                  ? <Link to={`/target/${r.analysis_id}`}>{r.gene}</Link>
                  : r.gene}
              </td>
              <td className="mono">{r.accession}</td>
              <td>{r.disposition}</td>
              <td>{r.tier}{r.tier_reason ? ` · ${r.tier_reason}` : ''}</td>
              <td>{
                r.fold_status === 'folded' ? <span className="folded">folded</span>
                : r.fold_status === 'failed' ? <span className="failed">failed</span>
                : <span className="not-folded">not yet</span>}</td>
              <td className="note-cell">{coverageNote(r)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>
      {/* ⚠⚠ D-152 MOVED THE SECOND POPULATION BELOW THE TABLE, AND DID NOT COLLAPSE IT.
          D-135's requirement is that this page states TWO populations, labels the second one, gives
          it no denominator and never lets one number stand for the other — and every clause of that
          still holds here: it is still below the coverage line, still labelled *a different
          population*, still fraction-free, and its chips still carry the assembled caveat beside
          them (D-133 am. 1, *the caveat arrives with the act*).
          ⚠ What it is NOT is a `<details>`. A collapsed strip would put a claim about scale behind
          a control, and D-135 exists precisely because this page once said nothing about the census
          and so under-reported three weeks of measurement. **Moving a block is not demoting it;
          hiding one is.**
          ⚠ The cost of the old position, measured rather than argued: at 1440×900 the strip was
          ~470 px tall and stood between the headline and the first cohort row, so the table this
          route is named for began below the fold. */}
      <CensusPopulationStrip summary={census} />
    </div>
  )
}
