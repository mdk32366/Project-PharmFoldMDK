import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getCoverage, listAnalyses } from '../api.js'
import { bandFor } from '../plddt.js'
import { nextSort, sortRows } from '../sortRows.js'

// The picker over the folded targets (light list, D-034). mean pLDDT carries its band inline, so the
// list tells the confidence story before a structure is opened. Default sort is pLDDT desc so the most-
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
// so a neophyte promoted fold quality into ADC suitability. Three changes, none of which removes a
// value: the header names the fold explicitly, the dot is visually secondary to identity, and one
// line states what confidence is NOT.
//
// ⚠ DEMOTION IS NOT DELETION. Every value, band and colour is still rendered here, and the detail
// view's confidence layer (Confidence.jsx, PlddtPlot, PlddtSpread — D-039/D-048) is untouched.
// ⚠ THE TARGET-QUALITY SLOT IS RESERVED, NOT FILLED. The structural-suitability score is gated on
// the D-075 ablation result. This change stops confidence IMPERSONATING it; it does not supply it.
// ⚠ The exact visual treatment is OWNER-RESERVED (prominence was itself an owner ruling, D-039/D-048),
// so the demotion is expressed as one semantic class rather than a pixel choice baked into markup.
//
// ── Sortable headers, and the absent-value rule ───────────────────────────────────────────────────
// Every existing column is click-to-sort (asc → desc → back to default), with the active column and
// direction announced via `aria-sort` — an unlabelled sort is a silent reordering. The ordering logic
// lives in `../sortRows.js`, tested in isolation, so the census's future columns become new sort keys
// in a proven mechanism rather than a retrofit.
//
// ⚠ THE `?? 0` COERCION IS GONE. It sorted a missing measurement as though it scored the WORST, and
// that was live: IGF2R is on this list with `mean_plddt: null` because its fold hit a CUDA OOM at
// 2,491 aa. Absent values are now a trailing CATEGORY in both directions, never a low number, and the
// row states its REAL reason (from /api/coverage's fold_status + fail_reason, joined client-side by
// accession — the D-068 TargetScorerPanel pattern, so no route changes). A pretty dash over a wrong
// null would paper over a data bug; this null is honest, and the row says why.
//
// ⚠ Fold confidence has NO sort control of its own: it is a band OF mean pLDDT, so sorting it
// separately would be a second axis for one quantity. Sort by mean pLDDT instead.
const DEFAULT_SORT = { key: 'mean_plddt', dir: 'desc' }

const COLUMNS = [
  { key: 'gene', label: 'Gene' },
  { key: 'accession', label: 'Accession' },
  { key: 'tier', label: 'Tier' },
  { key: 'mean_plddt', label: 'mean pLDDT' },
  // Not sortable by design (see above); demoted per the confidence-demotion order.
  { key: null, label: 'Fold confidence', className: 'col-secondary' },
]

const ARIA = { asc: 'ascending', desc: 'descending' }

export default function TargetList() {
  const [rows, setRows] = useState(null)
  const [error, setError] = useState(null)
  const [tierFilter, setTierFilter] = useState('all')
  const [sort, setSort] = useState(null)          // null = the default order
  const [foldStatus, setFoldStatus] = useState({}) // accession -> { fold_status, fail_reason }

  useEffect(() => {
    listAnalyses().then(setRows).catch((e) => setError(e.message))
  }, [])

  // Additive only: coverage explains WHY a value is absent. A failure here must degrade the reason
  // text, never the list — so it is caught and dropped, not surfaced as a list error.
  useEffect(() => {
    // `Promise.resolve(...)` so a supplier that throws SYNCHRONOUSLY (or returns a non-promise)
    // cannot take the list down with it. The reason text is secondary; the list is not.
    Promise.resolve()
      .then(() => getCoverage())
      .then((cov) => {
        const map = {}
        for (const r of cov?.rows ?? []) {
          if (r?.accession) map[r.accession] = { fold_status: r.fold_status, fail_reason: r.fail_reason }
        }
        setFoldStatus(map)
      })
      .catch(() => setFoldStatus({}))
  }, [])

  if (error) return <p className="error">Could not load targets: {error}</p>
  if (!rows) return <p className="loading">Loading targets…</p>

  const tiers = [...new Set(rows.map((r) => r.tier).filter(Boolean))].sort()
  const filtered = tierFilter === 'all' ? rows : rows.filter((r) => r.tier === tierFilter)
  const active = sort ?? DEFAULT_SORT
  const sorted = sortRows(filtered, active.key, active.dir)

  const onHeaderClick = (key) => {
    if (!key) return
    // ⚠ Advance from the EXPLICIT state (`sort`), not from the effective default. On load `sort` is
    // null, so a first click on ANY column — including mean pLDDT, which the default happens to
    // order by — starts at ascending. Passing the default in instead made the first click on
    // mean pLDDT jump straight back to the default, i.e. do nothing visible.
    setSort(nextSort(sort, key))
  }

  // The absent cluster's label: the real reason, or an honest "reason not available" if coverage
  // could not be reached. Never a bare dash, and never a fabricated cause.
  const absentLabel = (row) => {
    const st = foldStatus[row.accession]
    if (st?.fold_status === 'failed') {
      const why = (st.fail_reason || '').split(/[:.]\s|—/)[0].trim()
      return why ? `fold failed — ${why.slice(0, 70)}` : 'fold failed'
    }
    if (st?.fold_status === 'not_folded') return 'not folded — never attempted'
    return 'no measurement (reason unavailable)'
  }

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
          <tr>
            {COLUMNS.map((col) => {
              const isActive = col.key && active.key === col.key
              return (
                <th
                  key={col.label}
                  className={col.className}
                  aria-sort={isActive ? ARIA[active.dir] : 'none'}
                >
                  {col.key ? (
                    <button type="button" className="sort-header" onClick={() => onHeaderClick(col.key)}>
                      {col.label}
                      <span aria-hidden="true" className="sort-caret">
                        {isActive ? (active.dir === 'asc' ? ' ▲' : ' ▼') : ''}
                      </span>
                    </button>
                  ) : (
                    col.label
                  )}
                </th>
              )
            })}
          </tr>
        </thead>
        <tbody>
          {sorted.map((r) => {
            const band = bandFor(r.mean_plddt)
            const absent = r.mean_plddt == null
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
                  {absent ? (
                    <span className="absent-reason" title={foldStatus[r.accession]?.fail_reason || undefined}>
                      {absentLabel(r)}
                    </span>
                  ) : (
                    <>
                      <span className="dot dot-secondary" style={{ background: band.color }} /> {band.label}
                    </>
                  )}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
