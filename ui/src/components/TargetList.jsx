import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listAnalyses } from '../api.js'
import { bandFor } from '../plddt.js'

// The picker over the 42 folded targets (light list, D-034). mean pLDDT carries its band inline, so
// the list already tells the confidence story before a structure is opened. Sorted by pLDDT desc so
// the most-interpretable folds lead — and the reader sees the ceiling (nothing above 81.4) at a glance.
export default function TargetList() {
  const [rows, setRows] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    listAnalyses().then(setRows).catch((e) => setError(e.message))
  }, [])

  if (error) return <p className="error">Could not load targets: {error}</p>
  if (!rows) return <p className="loading">Loading targets…</p>

  const sorted = [...rows].sort((a, b) => (b.mean_plddt ?? 0) - (a.mean_plddt ?? 0))
  return (
    <div className="target-list">
      <p className="lede">
        {rows.length} folded targets. Start with{' '}
        <Link to="/target/1">NECTIN4 →</Link> (the target of a marketed ADC, enfortumab vedotin).
      </p>
      <table>
        <thead>
          <tr><th>Gene</th><th>Accession</th><th>mean pLDDT</th><th>Confidence</th></tr>
        </thead>
        <tbody>
          {sorted.map((r) => {
            const band = bandFor(r.mean_plddt)
            return (
              <tr key={r.id}>
                <td><Link to={`/target/${r.id}`}>{r.gene}</Link></td>
                <td className="mono">{r.accession}</td>
                <td className="mono">{r.mean_plddt != null ? r.mean_plddt.toFixed(2) : '—'}</td>
                <td><span className="dot" style={{ background: band.color }} /> {band.label}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
