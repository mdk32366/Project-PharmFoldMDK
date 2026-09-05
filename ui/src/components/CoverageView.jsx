import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getCoverage } from '../api.js'
import CoverageLine from './CoverageLine.jsx'

// The full cohort (UI Plan v2 §3.3): all 82 reachable — what is ranked, held out and why, excluded
// and why by name, folded, failed (with reason), and not-yet. Held-out and excluded rows are PRESENT,
// not silently absent (D-022: "MUC16 is CA-125; a reviewer who knows the field notices its absence
// immediately"). fold_status is three-valued (D-043): attempted-and-failed is shown as distinct from
// never-attempted, with jobs.error as the reason. Served by GET /api/coverage (D-038), not the list.
const ORDER = { excluded: 0, held_out: 1, ranked: 2 }

// D-120 / PLAN §3.4 — IGF2R two populations; FAT2 tileable vs MUC16 mucin.
function coverageNote(r) {
  if (r.accession === 'P11717' || r.gene === 'IGF2R') {
    const fail = r.fail_reason ? `${r.fail_reason} ` : ''
    return `${fail}Cohort CUDA OOM is one measurement; a later census tiling of this accession is a different span definition (D-081) — see Census. Neither substitutes for the other.`
  }
  if (r.gene === 'FAT2') {
    return `${r.exclusion_reason || ''} FAT2 is tileable in the census; that is not this cohort row.`
  }
  if (r.gene === 'MUC16') {
    return `${r.exclusion_reason || ''} MUC16 is a mucin — out of class; never ESMFold.`
  }
  if (r.excluded) return r.exclusion_reason
  if (r.fold_status === 'failed') return r.fail_reason
  return ''
}

export default function CoverageView() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getCoverage().then(setData).catch((e) => setError(e.message))
  }, [])

  if (error) return <p className="error">Could not load coverage: {error}</p>
  if (!data) return <p className="loading">Loading coverage…</p>

  const rows = [...data.rows].sort(
    (a, b) => ORDER[a.disposition] - ORDER[b.disposition] || (a.gene || '').localeCompare(b.gene || ''),
  )

  return (
    <div className="coverage">
      <h2>Coverage — the honest denominator</h2>
      <CoverageLine coverage={data.coverage} rows={data.rows} />
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
  )
}
