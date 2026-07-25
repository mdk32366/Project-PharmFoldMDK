import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listAnalyses } from '../api.js'
import { bandFor } from '../plddt.js'

// The picker over the folded targets (light list, D-034). mean pLDDT carries its band inline, so the
// list tells the confidence story before a structure is opened. Sorted by pLDDT desc so the most-
// interpretable folds lead — and the reader sees the ceiling (nothing above 81.4) at a glance.
//
// D-048 §3.2 (UI-depth §2.3): tier is shown per row and filterable, so the two-machine cohort
// (local int8 vs rental fp16) is legible without opening a JSON payload. Tiers are NOT blended into a
// combined score (D-028): the distinction is methodological (D-015 §3), not a quality axis.
export default function TargetList() {
  const [rows, setRows] = useState(null)
  const [error, setError] = useState(null)
  const [tierFilter, setTierFilter] = useState('all')

  useEffect(() => {
    listAnalyses().then(setRows).catch((e) => setError(e.message))
  }, [])

  if (error) return <p className="error">Could not load targets: {error}</p>
  if (!rows) return <p className="loading">Loading targets…</p>

  const tiers = [...new Set(rows.map((r) => r.tier).filter(Boolean))].sort()
  const filtered = tierFilter === 'all' ? rows : rows.filter((r) => r.tier === tierFilter)
  const sorted = [...filtered].sort((a, b) => (b.mean_plddt ?? 0) - (a.mean_plddt ?? 0))

  return (
    <div className="target-list">
      <p className="lede">
        {rows.length} folded targets. Start with{' '}
        <Link to="/target/1">NECTIN4 →</Link> (the target of a marketed ADC, enfortumab vedotin).
      </p>
      <div className="list-controls">
        <label htmlFor="tier-filter">Tier</label>
        <select id="tier-filter" value={tierFilter}
                onChange={(e) => setTierFilter(e.target.value)}>
          <option value="all">all tiers</option>
          {tiers.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>
      <table>
        <thead>
          <tr><th>Gene</th><th>Accession</th><th>Tier</th><th>mean pLDDT</th><th>Confidence</th></tr>
        </thead>
        <tbody>
          {sorted.map((r) => {
            const band = bandFor(r.mean_plddt)
            return (
              <tr key={r.id}>
                <td><Link to={`/target/${r.id}`}>{r.gene}</Link></td>
                <td className="mono">{r.accession}</td>
                <td>
                  <span className={`tier-tag tier-${r.tier}`} title={r.tier_reason || undefined}>
                    {r.tier ?? '—'}
                  </span>
                </td>
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
