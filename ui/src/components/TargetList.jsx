import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getCoverage, getRanking, listAnalyses } from '../api.js'
import { bandFor } from '../plddt.js'
import { nextSort, sortRows } from '../sortRows.js'
import { filterRows } from '../searchRows.js'
import { count } from '../plural.js'

// The picker over the folded targets (light list, D-034). mean pLDDT carries its band inline, so the
// list tells the confidence story before a structure is opened, and the reader sees the ceiling (no
// target reaches the high-confidence range) at a glance. (No literal max here — that rots as the
// cohort grows; see D-049/D-050.)
// ⟡ SUPERSEDED 2026-08-21: this paragraph said "Default sort is pLDDT desc so the most-interpretable
// folds lead." That default is now ruled against — see the block above `DEFAULT_SORT`. The sentence
// is corrected rather than deleted, because it records what the surface used to claim and why.
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
//
// ── ⚠⚠ THE DEFAULT SORT WAS A DE FACTO RANKING BY A THIRD OF THE REAL ONE (owner ruling 2026-08-21)
// This list defaulted to mean pLDDT descending while `CensusTable.jsx` explicitly REFUSES that on the
// census — "a self-reported confidence into a de facto ranking". Same reasoning, opposite behaviour,
// two surfaces, neither file mentioning the other.
//
// ⚠⚠ And it is worse here than on the census, not better. The cohort IS ranked — by the scorer — and
// `F-051` measures `membrane_proximal_plddt` at 32.2% of the scorer's attribution. So ordering by
// pLDDT was a ranking BY ROUGHLY A THIRD OF THE REAL RANKING, presented as though it were the order,
// while the real one existed and was one fetch away. On the census nothing else competes to be the
// order; here something did.
//
// ⚠ `D-102` licenses a reader CHOOSING a lens. It does not license the SYSTEM choosing one and
// presenting it as the order — a default sort is the one lens the page never labels.
const DEFAULT_SORT = { key: 'rank', dir: 'asc' }

// ⚠⚠ The sentence the census uses, rendered HERE, where the lens is actually applied (D-102, TA3).
const PLDDT_LENS_NOTE =
  'You are sorting by the model’s self-reported confidence in its own structure. It is not the ' +
  'scorer’s ranking: membrane_proximal_plddt carries 32.2% of the scorer’s attribution (F-051), so ' +
  'this orders the cohort by roughly a third of the ranking. Sort by Rank for the ranking itself.'

const COLUMNS = [
  // ⚠ The scorer's ordering, and the default. Unranked rows carry their CAUSE here, never a number.
  { key: 'rank', label: 'Rank' },
  { key: 'gene', label: 'Gene' },
  { key: 'accession', label: 'Accession' },
  { key: 'tier', label: 'Tier' },
  { key: 'mean_plddt', label: 'mean pLDDT' },
  // Not sortable by design (see above); demoted per the confidence-demotion order.
  { key: null, label: 'Fold confidence', className: 'col-secondary' },
]

// ⚠⚠ WHY THE UNRANKED ARE PARTITIONED AND NOT SORTED TO THE BOTTOM (owner ruling, TA2).
// 56 of the 82 are scored. The other 26 have NO POSITION in a scorer ordering — sinking them would
// rank them 57th through 82nd, and they are not last, they are unranked. **A sort that sinks
// unranked rows is a ranking of scoreability**, which is the same defect in a new coat.
//
// ⚠ The partition belongs to the RANK AXIS, not to the rows. Under any other sort the reader has
// chosen an axis every row has a value (or a stated absence) on, so all 82 order together under
// `sortRows`' existing absent-is-a-category rule. Quarantining them permanently would say they are
// outside every ordering, which is a different and equally false claim.
// ⚠⚠ THE PRE-REGISTERED FLOOR, NAMED. `D-060` decision 5 fixed it at 50 BEFORE the data was seen.
// ⚠ It is not moved to admit `ATP2B2` at 49.46. Moving a threshold after seeing which rows fall
// outside it is precisely what pre-registration exists to prevent. The page states the floor and
// the nearest excluded value instead, so a reader can judge the cutoff without us changing it.
export const PLDDT_FLOOR = 50

export function rankCause(row, rankingServed = true) {
  if (row.rank != null) return null
  // ⚠⚠ NO RANKING RUN IS NOT A PROPERTY OF THE ROW. If no valid pre-registered run is served, every
  // row is unranked for ONE shared reason, and none of the per-row causes below apply. An earlier
  // version fell through to the floor branch here and would have labelled a row at 77.26 pLDDT
  // "excluded by the pre-registered pLDDT floor of 50" — a false statement about a good fold,
  // produced by inferring a cause from the absence of a rank.
  if (!rankingServed) return 'no ranking run is currently served'
  // ⚠⚠ BOTH CAUSES RENDER (owner ruling). IGF2R is held_out AND its fold failed. A row with two
  // causes showing one is an absence with a cause hiding an absence with a cause.
  // ⚠ `held_out` LEADS because it is a DECISION, not an event: the row was ruled out before a card
  // was ever involved. The OOM is what happened afterwards.
  if (row.disposition === 'held_out') {
    return row.fold_status === 'failed'
      ? 'held out; fold subsequently attempted and failed (CUDA OOM). A later census tiling of this accession is a different span definition — see Census'
      : 'held out'
  }
  if (row.never_attempted || row.fold_status === 'not_folded') return 'not folded — never attempted'
  if (row.fold_status === 'failed') return 'fold attempted and failed'
  // ⚠ TESTED, NOT INFERRED. "Has a pLDDT and is not held out" is not the same claim as "is under the
  // floor", and only the second one is what `below_floor` means.
  if (row.mean_plddt != null && row.mean_plddt < PLDDT_FLOOR) {
    return `excluded by the pre-registered mean pLDDT floor of ${PLDDT_FLOOR}`
  }
  // ⚠ The fourth bucket was EMPTY at v99 and this is what must render if it ever fills. `F-044`'s
  // shape hides in a dash: an absence with no cause must SAY it has no cause.
  return 'unranked — no cause recorded'
}

const ARIA = { asc: 'ascending', desc: 'descending' }

export default function TargetList() {
  const [rows, setRows] = useState(null)
  const [error, setError] = useState(null)
  const [tierFilter, setTierFilter] = useState('all')
  const [sort, setSort] = useState(null)          // null = the default order
  const [foldStatus, setFoldStatus] = useState({}) // accession -> { fold_status, fail_reason }
  const [coverage, setCoverage] = useState([])     // the 82 manifest rows, for the members with no analysis
  const [query, setQuery] = useState('')
  const [ranks, setRanks] = useState(null)         // accession -> rank, from the pre-registered run

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
              // ⚠ disposition decides which CAUSE leads for an unranked row, so it must travel
              disposition: r.disposition,
            }
          }
        }
        setFoldStatus(map)
        // ⚠ the manifest rows themselves, so a cohort member with no analysis row still gets a row
        setCoverage(rows_)
      })
      .catch(() => { setFoldStatus({}); setCoverage([]) })
  }, [])

  // ⚠⚠ THE SCORER'S ORDERING, FROM THE EXISTING SUPPLIER. `/api/ranking` is served by
  // `_latest_valid_result`, which already implements `valid ∧ run_kind='preregistered'`
  // (`D-064` dec 3 for valid, `D-065` dec 4 for pre-registered).
  // ⚠ `F-049`'s trap is REAL and already closed there: `run_kind='preregistered'` ALONE does not
  // identify the run, because `id=1` carries that value with ZERO scored rows. Re-deriving the
  // predicate here would be `F-052` again, in the exact place the orders warned about it — so this
  // consumes the supplier and computes nothing.
  useEffect(() => {
    Promise.resolve()
      .then(() => getRanking())
      .then((r) => {
        const map = {}
        for (const row of r?.rows ?? []) {
          if (row?.accession && row.rank != null) map[row.accession] = row.rank
        }
        setRanks(map)
      })
      // ⚠ `{}` not null: the ranking being unreachable means NO row is ranked, which is a knowable
      // state the surface can state. It must not leave rows in "still loading" forever.
      .catch(() => setRanks({}))
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
      disposition: c.disposition ?? null, never_attempted: true,
    }))
  // ⚠ rank and the coverage facts join onto the row so one sort mechanism sees everything.
  const rankMap = ranks ?? {}
  const all = [...rows, ...missing].map((r) => ({
    ...r,
    rank: rankMap[r.accession] ?? null,
    disposition: r.disposition ?? foldStatus[r.accession]?.disposition ?? r.disposition,
    fold_status: foldStatus[r.accession]?.fold_status
      ?? (r.never_attempted ? 'not_folded' : r.mean_plddt != null ? 'folded' : undefined),
  }))

  const tiers = [...new Set(rows.map((r) => r.tier).filter(Boolean))].sort()
  const tiered = tierFilter === 'all' ? all : all.filter((r) => r.tier === tierFilter)
  // ⚠ One matcher, shared with the census (`../searchRows.js`) — see `F-052`.
  const filtered = filterRows(tiered, query)
  const active = sort ?? DEFAULT_SORT

  // ⚠⚠ IS A RANKING SERVED AT ALL? `/api/ranking` returns `result_status: not_run` with zero rows
  // when no valid pre-registered run exists (`D-062`). Partitioning then would put all 82 rows in a
  // group headed "have no scorer rank" — true, useless, and it would imply 82 individual exclusions
  // where there is one shared cause. So the surface says the ranking is unavailable and falls back
  // to a STATED order instead of pretending to one.
  const rankingServed = ranks != null && Object.keys(rankMap).length > 0

  // ⚠⚠ THE PARTITION, AND IT APPLIES TO THE RANK AXIS ONLY. Sorting BY RANK splits the list, because
  // 26 rows have no position on that axis. Sorting by any other column does not, because every row
  // has a value or a stated absence there — see the note above `rankCause`.
  const partitioned = active.key === 'rank' && rankingServed
  const rankedRows = partitioned ? filtered.filter((r) => r.rank != null) : filtered
  const unrankedRows = partitioned ? filtered.filter((r) => r.rank == null) : []
  // ⚠ with no ranking served, `rank` is null on every row and sorting by it would be a no-op with an
  // implied order. Fall back to accession — stated in the note, not silent.
  const effectiveKey = active.key === 'rank' && !rankingServed ? 'accession' : active.key
  const effectiveDir = active.key === 'rank' && !rankingServed ? 'asc' : active.dir
  const sorted = sortRows(rankedRows, effectiveKey, effectiveDir)
  // ⚠ Accession ascending, and the arbitrariness is STATED below. It is the only ordering available
  // that is not a ranking of something — any quality-adjacent key would smuggle an order back in.
  const unranked = [...unrankedRows].sort((a, b) =>
    String(a.accession).localeCompare(String(b.accession)))

  // ⚠ the nearest excluded value, so a reader can judge the pre-registered floor without us moving it
  const nearestBelowFloor = unranked
    .filter((r) => r.mean_plddt != null && r.disposition !== 'held_out')
    .reduce((best, r) => (best == null || r.mean_plddt > best ? r.mean_plddt : best), null)

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
      {/* ⚠⚠ TA3 / D-102 — THE LENS IS STATED WHERE THE LENS IS APPLIED. pLDDT is still available as
          a sort the reader chooses; what it may not be is the order the page arrives in unlabelled. */}
      {active.key === 'mean_plddt' && (
        <p className="note plddt-lens-note">{PLDDT_LENS_NOTE}</p>
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
                {/* ⚠⚠ THE RANK CELL. A ranked row shows its integer. An unranked row shows its
                    CAUSE — never a number, never a dash, and never a position it does not hold. */}
                <td className="mono col-rank">
                  {r.rank != null
                    ? r.rank
                    : <span className="rank-cause">{rankCause(r, rankingServed)}</span>}
                </td>
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
        {/* ⚠⚠ THE UNRANKED GROUP — A PARTITION, NOT POSITIONS 57–82.
            It is a second `tbody` inside the same table so the columns stay aligned, with a heading
            row that states what the group IS. These rows are NOT numbered, and nothing here implies
            an order relative to the ranked rows above.
            ⚠ VISIBLE, NOT COLLAPSED (owner ruling): a collapsed group is a filtered default wearing
            a disclosure control, and 26 of 82 hidden by default would be a silent exclusion. */}
        {partitioned && unranked.length > 0 && (
          <tbody className="unranked-group">
            <tr className="unranked-heading">
              <td colSpan={COLUMNS.length}>
                <strong>{count(unranked.length, 'target')} {unranked.length === 1 ? 'has' : 'have'} no scorer rank.</strong>{' '}
                They are not ranked last — they have no position in this ordering at all, and each
                row states why.{' '}
                {nearestBelowFloor != null && (
                  <>
                    ⚠ Rows excluded by the pre-registered mean pLDDT floor of <strong>50</strong>{' '}
                    (<abbr title="pre-registered before the data was seen, in D-060 decision 5">
                      pre-registered
                    </abbr>) come closest at <strong>{nearestBelowFloor.toFixed(2)}</strong> — the
                    floor is not moved to admit it, and the nearest value is shown so you can judge
                    the cutoff yourself.{' '}
                  </>
                )}
                Listed by accession, which carries no judgement; any other order would be a ranking
                of something.
              </td>
            </tr>
            {unranked.map((r) => {
              const band = bandFor(r.mean_plddt)
              const absent = r.mean_plddt == null
              return (
                <tr key={r.accession ?? r.id} className="row-unranked">
                  <td className="col-rank"><span className="rank-cause">{rankCause(r, rankingServed)}</span></td>
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
        )}
      </table>
    </div>
  )
}
