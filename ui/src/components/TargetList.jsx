import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listAnalyses } from '../api.js'
import { bandFor } from '../plddt.js'

// The picker over the folded targets (light list, D-034). mean pLDDT carries its band inline, so the
// list tells the confidence story before a structure is opened. Sorted by pLDDT desc so the most-
// interpretable folds lead — and the reader sees the ceiling (no target reaches the high-confidence
// range) at a glance. (No literal max here — that rots as the cohort grows; see D-049/D-050.)
//
// D-048 §3.2 (UI-depth §2.3): tier is shown per row and filterable, so the two-machine cohort
// (local int8 vs rental fp16) is legible without opening a JSON payload. Tiers are NOT blended into a
// combined score (D-028): the distinction is methodological (D-015 §3), not a quality axis.
//
// ── Confidence demotion (un-gated honesty fix) ────────────────────────────────────────────────────
// The band vocabulary was always careful — "Confident BACKBONE", "backbone unreliable" — but the LIST
// undid it: a bare "Confidence" header beside a traffic-light dot, as prominent as the identity
// columns. At a glance that reads as a verdict on the TARGET, and nothing more relevant sat above it,
// so a neophyte promoted fold quality into ADC suitability. Three changes, none of which remove a
// value: the header names the fold explicitly, the dot is visually secondary to identity, and one
// line states what confidence is NOT.
//
// ⚠ DEMOTION IS NOT DELETION. Every value, band and colour is still rendered here, and the detail
// view's confidence layer (Confidence.jsx, PlddtPlot, PlddtSpread — D-039/D-048) is untouched.
// ⚠ THE TARGET-QUALITY SLOT IS RESERVED, NOT FILLED. The structural-suitability score is gated on
// the D-075 ablation result. This change stops confidence IMPERSONATING it; it does not supply it.
// ⚠ The exact visual treatment is OWNER-RESERVED (prominence was itself an owner ruling, D-039/D-048),
// so the demotion is expressed as one semantic class rather than a pixel choice baked into markup.
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
      {/* 1c — the one sentence that inoculates the glance, before any detail panel is opened.
          OWNER-COPY PLACEHOLDER: substance fixed, wording for the owner to finalise. */}
      <p className="note confidence-scope-note">
        Fold confidence is the model&rsquo;s certainty about the <em>predicted structure</em> — not a
        judgement of whether the target is a good ADC candidate. Scoring lives on{' '}
        <Link to="/scorer">Scorer</Link>.
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
          {/* 1a — the header carries the fold qualifier the band labels already carry. "Confidence"
              standing alone was the trap; a reader must see this is about the STRUCTURE. */}
          <tr>
            <th>Gene</th><th>Accession</th><th>Tier</th><th>mean pLDDT</th>
            <th className="col-secondary">Fold confidence</th>
          </tr>
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
                {/* 1b — demoted: the band colour is retained (no information removed) but rendered
                    as a secondary signal rather than the row's most eye-catching element. */}
                <td className="col-secondary">
                  <span className="dot dot-secondary" style={{ background: band.color }} /> {band.label}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
