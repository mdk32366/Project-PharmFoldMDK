import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getCoverage, listAnalyses } from '../api.js'
import { bandFor } from '../plddt.js'
import { nextSort, sortRows } from '../sortRows.js'
import { filterRows } from '../searchRows.js'

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
  const [coverage, setCoverage] = useState([])     // the 82 manifest rows, for the members with no analysis
  const [query, setQuery] = useState('')

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
        const rows_ = cov?.rows ?? []
        const map = {}
        for (const r of rows_) {
          if (r?.accession) {
            // ⚠ `fail_reason` is the reason an ATTEMPT failed; `exclusion_reason` is the reason
            // there was never an attempt. Both are causes, and a row must never fall back to a
            // bare dash when one of them exists.
            map[r.accession] = {
              fold_status: r.fold_status,
              fail_reason: r.fail_reason || r.exclusion_reason,
            }
          }
        }
        setFoldStatus(map)
        // ⚠ the manifest rows themselves, so a cohort member with no analysis row still gets a row
        setCoverage(rows_)
      })
      .catch(() => { setFoldStatus({}); setCoverage([]) })
  }, [])

  if (error) return <p className="error">Could not load targets: {error}</p>
  if (!rows) return <p className="loading">Loading targets…</p>

  // ⚠⚠ TWO COHORT MEMBERS HAVE NO ANALYSIS ROW AT ALL, so `listAnalyses()` returns 80 where the
  // cohort is 82. `FAT2` (4,030 aa) and `MUC16` (14,451 aa) fold on no single card as one sequence,
  // were therefore never attempted, and were absent from this surface entirely — no row, no count,
  // no cause. The owner's census ruling settles it: *"just show it in the list, and show the status
  // as NOT FOLDED."* ⚠ **A rule applied to one shape and not the other is not a rule.**
  // ⚠ The rows come from coverage, which is already fetched for the reason text — no new endpoint.
  const missing = coverage
    .filter((c) => c.fold_status === 'not_folded' && !rows.some((r) => r.accession === c.accession))
    .map((c) => ({
      id: null, accession: c.accession, gene: c.gene, label: c.label ?? null,
      mean_plddt: null, tier: null, tier_reason: null, aliases: c.aliases ?? null,
      never_attempted: true,
    }))
  const all = [...rows, ...missing]

  const tiers = [...new Set(rows.map((r) => r.tier).filter(Boolean))].sort()
  const tiered = tierFilter === 'all' ? all : all.filter((r) => r.tier === tierFilter)
  // ⚠ One matcher, shared with the census (`../searchRows.js`) — see `F-052`.
  const filtered = filterRows(tiered, query)
  const active = sort ?? DEFAULT_SORT
  const sorted = sortRows(filtered, active.key, active.dir)

  // ⚠⚠ EVERY COUNT STATES ITS KEY. This line said "{rows.length} folded targets" — wrong three ways
  // at once: 80 is not the folded count (79 is), 80 is not the cohort (82 is), and it reported the
  // UNFILTERED total while the table below showed a filtered subset. `IGF2R` renders its own CUDA
  // OOM failure one line beneath a header that counted it as folded.
  const nFolded = all.filter((r) => r.mean_plddt != null).length
  const nFailed = all.filter((r) => r.mean_plddt == null && !r.never_attempted).length
  const nNever = missing.length
  const narrowed = filtered.length !== all.length

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
    // ⚠ never-attempted has a CAUSE too, and it was being dropped: `FAT2` and `MUC16` are oversize,
    // which is why no attempt exists. "Never attempted" alone states the absence without the reason.
    if (st?.fold_status === 'not_folded') {
      const why = (st.fail_reason || '').split(/[:.]\s|—/)[0].trim()
      return why ? `not folded — ${why.slice(0, 70)}` : 'not folded — never attempted'
    }
    return 'no measurement (reason unavailable)'
  }

  return (
    <div className="target-list">
      <p className="lede">
        The {all.length} cohort targets: <strong>{nFolded} folded</strong>
        {nFailed > 0 && <>, {nFailed} attempted and failed</>}
        {nNever > 0 && <>, {nNever} too large to attempt</>}. Start with{' '}
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
        {/* ⚠⚠ The search box this surface never had. `ERBB2` is folded and ranked here, and the
            owner searching `HER2` found nothing — because there was nothing to type into. */}
        <label htmlFor="target-search">Search</label>
        <input
          id="target-search"
          type="search"
          className="row-search"
          value={query}
          placeholder="gene, accession, or a name like HER2"
          onChange={(e) => setQuery(e.target.value)}
        />
        <label htmlFor="tier-filter">Tier</label>
        <select id="tier-filter" value={tierFilter}
                onChange={(e) => setTierFilter(e.target.value)}>
          <option value="all">all tiers</option>
          {tiers.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>
      {/* ⚠⚠ A FILTERED TABLE UNDER AN UNQUALIFIED TOTAL IS THE DEFECT THIS PAGE ALREADY HAD. The
          lede counts the cohort; this line counts what is actually on screen, and appears only when
          the two differ. A reader who filters must never have to assume which number they are
          looking at. */}
      {narrowed && (
        <p className="note filter-count">
          Showing {filtered.length} of {all.length}
          {query.trim() && <> matching &ldquo;{query.trim()}&rdquo;</>}
          {filtered.length === 0 && <> — nothing here matches. The alias index covers names like
            HER2 and CD30; a protein absent from the cohort will not appear here even so.</>}
        </p>
      )}
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
              <tr key={r.accession ?? r.id}>
                {/* ⚠⚠ A cohort member with no analysis row has no card to open. `/target/null` would
                    be a link that 404s, which is worse than no link — it invites a click and then
                    denies it. The gene renders as plain text and the reason column says why. */}
                <td>
                  {r.id != null
                    ? <Link to={`/target/${r.id}`}>{r.gene}</Link>
                    : <span className="gene-unlinked" title="no fold was attempted, so there is no structure page">{r.gene}</span>}
                </td>
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
