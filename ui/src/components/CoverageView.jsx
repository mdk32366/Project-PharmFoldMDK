import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getCoverage } from '../api.js'
import CoverageLine from './CoverageLine.jsx'

// The full cohort (UI Plan v2 §3.3): all 82 reachable — what is ranked, held out and why, excluded
// and why by name, folded and not-yet. Held-out and excluded rows are PRESENT, not silently absent
// (D-022: "MUC16 is CA-125; a reviewer who knows the field notices its absence immediately"). The
// data is served nowhere by the read list — it comes from GET /api/coverage (D-038).
const ORDER = { excluded: 0, held_out: 1, ranked: 2 }

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
              <td>{r.fold_status === 'folded'
                ? <span className="folded">folded</span>
                : <span className="not-folded">not yet</span>}</td>
              <td className="note-cell">{r.excluded ? r.exclusion_reason : ''}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
