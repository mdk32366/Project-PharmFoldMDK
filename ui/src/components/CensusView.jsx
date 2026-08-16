import { useEffect, useState } from 'react'
import { CENSUS, CENSUS_LIMITS } from '../censusSummary.js'
import { listCensus } from '../api.js'
import CensusTable from './CensusTable.jsx'

// The census surface. ⚠⚠ UNSCORED BY CONSTRUCTION — no score, no rank, no order-by-suitability,
// because D-079 dec 1 bars scoring any census row.
//
// ⚠⚠ THE PER-PROTEIN LIST IS NEW, AND IT REVERSES THIS FILE'S OWN EARLIER RULE (D-087).
// This comment used to read "...no sort control and no per-protein row anywhere on this page,
// because a per-protein list is one sort away from being read as a shortlist." The owner overrode
// it — *"Why hide it under a bushel?"* — and the reversal is recorded rather than edited away.
//
// ⚠ The original worry was real and is answered by CONSTRUCTION, not by omission:
//   · default order is ACCESSION, never pLDDT — the page does not arrive having chosen
//   · there is no score column, because there is no score
//   · every row carries `scored: false` with its reason, from the API, not from the UI's memory
//   · sorting is not scoring: the reader orders the data, the project does not endorse an order
// ⚠ What the old rule bought was safety through invisibility, and that has its own cost —
// 2,500 measured structures nobody could look at.
export default function CensusView() {
  const foldable = CENSUS.sources.reduce((a, s) => a + s.foldable, 0)
  const rows = CENSUS.sources.reduce((a, s) => a + s.rows, 0)
  const notFoldableTotal = CENSUS.notFoldable.reduce((a, r) => a + r.rows, 0)

  return (
    <div className="census">
      <h2>The wider protein census</h2>

      <p className="lede">
        Alongside the 82 ranked targets, this project measured a much larger set of human membrane
        proteins to find out how many of them <em>could</em> be folded at all. <strong>That count is
        what this page reports.</strong>
      </p>

      {/* ⚠ The disclaimer sits ABOVE the numbers, not below them. A reader who stops after the
          headline figure must already have met the limit. */}
      <p className="census-bar">
        <strong>None of these proteins has been scored or ranked.</strong> This is a count of what
        is measurable, not a list of candidates — and it is not comparable to the ranked 82.
      </p>

      <section className="census-counts">
        <h3>What was measured</h3>
        <dl className="census-figures">
          <div><dt>{rows.toLocaleString()}</dt><dd>proteins examined</dd></div>
          <div><dt>{foldable.toLocaleString()}</dt><dd>have an outward-facing stretch precise enough to cut out</dd></div>
          <div><dt>{notFoldableTotal.toLocaleString()}</dt><dd>do not — each with a stated reason, below</dd></div>
        </dl>
        <ul>
          {CENSUS.sources.map((s) => (
            <li key={s.label}>
              <strong>{s.label}:</strong> {s.rows.toLocaleString()} examined,{' '}
              {s.foldable.toLocaleString()} with a usable outward-facing stretch
            </li>
          ))}
        </ul>
      </section>

      <section className="census-absences">
        <h3>Where there is no measurement, the reason is named</h3>
        <p className="note">
          ⚠ An absence is recorded as a <em>category with a cause</em> — never as a zero, and never
          as a blank. &quot;Not described&quot; and &quot;described and empty&quot; are different
          findings.
        </p>
        <dl>
          {CENSUS.notFoldable.map((r) => (
            <div className="census-absence" key={r.reason}>
              <dt>{r.rows.toLocaleString()} — {r.reason}</dt>
              <dd>{r.plain}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="census-tranches">
        <h3>How the folding is batched</h3>
        <p className="note">
          Folding runs in batches from the shortest to the longest, so that any problem with the
          hardware shows up on a cheap fold rather than an expensive one. ⚠ <strong>A batch is a
          running order, not a ranking</strong> — the position of a protein here says nothing
          whatever about it as a target.
        </p>
        <ul>
          {CENSUS.tranches.map((t) => (
            <li key={t.tranche}>
              <strong>Batch {t.tranche}</strong> — {t.span} — {t.rows.toLocaleString()} proteins
            </li>
          ))}
        </ul>
      </section>

      <CensusBrowser />

      <section className="census-limits">
        <h3>What these numbers do not mean</h3>
        {CENSUS_LIMITS.map((l) => (
          <div className="census-limit" key={l.head}>
            <h4>{l.head}</h4>
            <p>{l.body}</p>
          </div>
        ))}
      </section>

      <p className="note census-provenance">
        Counted off manifest revision {CENSUS.manifestRevision}, span definition{' '}
        <code>{CENSUS.spanDefinition}</code>, fold order seeded with{' '}
        <code>{CENSUS.seed}</code> recorded before the order was drawn. The ranked 82 remain frozen
        under <code>{CENSUS.frozenDefinition}</code>.
      </p>
    </div>
  )
}

// The browsable list (D-087). ⚠ Loads on mount; an error is stated, never rendered as an empty
// table — "nothing matched" and "the request failed" must not look the same.
function CensusBrowser() {
  const [rows, setRows] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let live = true
    listCensus()
      .then((r) => live && setRows(r))
      .catch((e) => live && setError(e.message ?? String(e)))
    return () => { live = false }
  }, [])


  if (error) {
    return (
      <section className="census-browser panel">
        <h3>Census — every folded protein</h3>
        <p className="caveat">⚠ The list could not be loaded: {error}. This is a failure to
          retrieve, <strong>not</strong> an empty census.</p>
      </section>
    )
  }
  if (rows === null) return <p className="note">Loading the folded census…</p>

  return (
    <>
      {/* ⚠ No inline panel any more — each protein has its own page (`/census/:id`), which the
          accession links to. A panel AND a page would be two surfaces describing one protein,
          free to drift apart. */}
      <CensusTable rows={rows} />
    </>
  )
}
