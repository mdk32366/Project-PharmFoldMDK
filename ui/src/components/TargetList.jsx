import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getAssociations, getCoverage, getRanking, listAnalyses } from '../api.js'
import { bandFor } from '../plddt.js'
import { nextSort, sortRows } from '../sortRows.js'
import { filterRows } from '../searchRows.js'
import { count } from '../plural.js'
import { summariseAssociations } from '../associationSummary.js'
import { HpaCredit } from './HpaAttribution.jsx'

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

// ── ⚠⚠ COLUMN ONE WAS THE WIDEST COLUMN ON THE PAGE, AND IT WAS HOLDING PROSE (owner, 2026-09-08)
// The Rank cell renders an integer for a ranked row and its CAUSE — a sentence — for an unranked
// one, and nothing bounded it: `grep -n 'rank-cause\|col-rank' ui/src/styles.css` returned **zero
// rules** before this change, so the auto table layout sized the column to the longest cause on
// one line. The causes `rankCause` can emit are 8, 25, 28, 28, 34, 53 and **144** characters long
// against a four-character header, and the 144 is live (IGF2R is held out AND OOM'd). ⚠ Worse in
// the state the page is actually in: with no ranking served, EVERY row renders the 34-character
// shared cause, so the widest column was also the least informative one.
// ⚠⚠ THE FIX IS A BOUND AND A DEMOTION, NEVER A TRUNCATION. Every cause string is unchanged and
// rendered in full — `.col-rank`/`.rank-cause` cap the column and let it wrap, and the cause is
// typographically secondary to the integer it stands in for. **Demotion is not deletion** is the
// standing rule on this surface (see the confidence block above), and it governs here too.
const COLUMNS = [
  // ⚠ The scorer's ordering, and the default. Unranked rows carry their CAUSE here, never a number.
  { key: 'rank', label: 'Rank' },
  { key: 'gene', label: 'Gene' },
  { key: 'accession', label: 'Accession' },
  // ⚠⚠ THE DESCRIPTION, AND IT IS **NOT** THE LIST PAYLOAD'S `label` (D-142). `/api/analyses`
  // carries `label`, which reads like a name and IS THE GENE SYMBOL on this population: the
  // committed manifest keeps `label` and `protein_name` in separate columns and they are equal on
  // all 82 rows. The census's `label` — same key, other population — really is the protein name
  // (`data/census/census_labels.csv`), which is what makes the wrong guess so easy; F-049's family.
  // ⚠ So this sorts and renders `description`, joined from `/api/coverage`'s manifest-derived
  // `protein_name` by accession (the D-068 pattern), and the light list's exact field set is
  // untouched.
  { key: 'description', label: 'Description', className: 'col-description' },
  // ⚠⚠ AN EXPRESSION CLAIM, AND DELIBERATELY NOT SORTABLE (D-142). The cell holds a SET of tumour
  // types. Every scalar that could order it — the leading quasi H-score, or how many types clear
  // the cutoff — would order the cohort by an expression statistic the cell never shows, which is
  // the de facto ranking this list already refused for mean pLDDT (owner ruling 2026-08-21), by a
  // quantity that is not even a third of the real one. The reason is printed on the page, not
  // just here: an absent control with no stated reason reads as an oversight.
  { key: null, label: 'Cancer association', className: 'col-assoc' },
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

// ⚠⚠ THREE STATES, NOT TWO, ON BOTH NEW COLUMNS. "still loading", "the supplier could not be
// reached" and "the supplier has nothing for this row" are three different facts, and collapsing
// them would let an ignorance state render as a claim about the target. `unknown ≠ none` is the
// standing rule (D-128 §1a's wording; `null ≠ 0` in the same breath), and it costs one enum here.
export const SUPPLIER_LOADING = 'loading'
export const SUPPLIER_FAILED = 'failed'
export const SUPPLIER_LOADED = 'loaded'

// ⚠ The description is a NAME, so its absence is never a finding — but it is still never a bare
// dash, because a dash cannot distinguish "no name recorded" from "we could not ask".
function DescriptionCell({ row, state }) {
  if (row.description) return <span className="description-text">{row.description}</span>
  if (state === SUPPLIER_FAILED) {
    return <span className="absent-reason">no description — /api/coverage could not be reached</span>
  }
  if (state === SUPPLIER_LOADING) return <span className="absent-reason">loading…</span>
  return <span className="absent-reason">no protein name for this accession in the cohort manifest</span>
}

/**
 * The compact association cell: the highest-scoring tumour type(s), the total, and the way to the
 * full list. See `../associationSummary.js` for why ties are all shown and why nothing re-sorts.
 *
 * ⚠⚠ THE HPA CITATION IS A PRECONDITION OF DISPLAY, SO A ROW WITH NO ATTRIBUTION BLOCK SHOWS NO
 * VALUE. D-100: Kathad's S3 is a verbatim extract of `pathology.tsv`, so these tumour types are
 * HPA content however they reached us, and the licence words citation as a condition — "be sure
 * that our content is never displayed in the absence of such citation." Fail-closed is therefore
 * the only direction available: no block, no tumour types, and the row says why.
 * ⚠ The per-datum link is the CensusTable staining-cell pattern — **the value itself is the
 * anchor**, so element 4 costs no extra real estate in a table. Elements 1–3 render once beneath
 * the table (`HpaCredit`), which is the split-by-case ruling of 2026-08-21 applied to a list.
 */
function AssociationCell({ row, assoc, state }) {
  if (state === SUPPLIER_FAILED) {
    return <span className="absent-reason">no associations — /api/associations could not be reached</span>
  }
  if (state !== SUPPLIER_LOADED || !assoc) {
    return <span className="absent-reason">loading…</span>
  }
  const summary = summariseAssociations((assoc.associations ?? {})[row.gene])
  if (summary.total === 0) {
    // ⚠ D-053's own sentence, and it is a claim about the MAP, not about the tumour biology.
    return <span className="assoc-absent">no association recorded for this target</span>
  }
  const attribution = assoc.attributions?.[row.gene]
  if (!attribution) {
    return (
      <span className="absent-reason">
        {count(summary.total, 'tumour type')} recorded, withheld here — no Human Protein Atlas
        citation is available for this gene, and the licence makes the citation a condition of
        display
      </span>
    )
  }
  const total = (
    <>
      {count(summary.total, 'tumour type')} above the cutoff
    </>
  )
  return (
    <span className="assoc-cell">
      {/* ⚠⚠ THE ORDER IS NOT ASSERTED WHEN IT WAS NOT DELIVERED. `ordered: false` means a later
          pair outscored the first, so no row here is "the highest" and the cell says so rather
          than captioning row 0 with a superlative it did not earn. */}
      {summary.ordered ? (
        <span className="assoc-top">
          {attribution.deep_link ? (
            <a
              className="assoc-hpa-link"
              href={attribution.deep_link}
              rel="noopener noreferrer"
              target="_blank"
              title="View the tumour staining behind this on the Human Protein Atlas (v22)"
            >
              {summary.top.join(' · ')}
            </a>
          ) : (
            <>
              {summary.top.join(' · ')}
              {/* ⚠ An absent link is a CATEGORY with a cause, never a broken anchor. */}
              <span className="hpa-attrib-nolink"> (no atlas link — {attribution.deep_link_absent_reason})</span>
            </>
          )}
        </span>
      ) : (
        <span className="assoc-top assoc-unordered">
          highest not named — the association map did not arrive in score order
        </span>
      )}
      {/* ⚠ `\u00a0→` — a NON-BREAKING space before the arrow. With an ordinary space the arrow
          wrapped onto a line of its own in the bounded column, which reads as a stray glyph. */}
      <span className="assoc-rest col-secondary">
        {row.id != null
          ? <Link to={`/target/${row.id}`}>{total}{'\u00a0→'}</Link>
          : <>{total} — no target page to open</>}
      </span>
    </span>
  )
}

/**
 * Every `<td>` of one target row, in one place.
 *
 * ⚠⚠ EXTRACTED BECAUSE THE ROW MARKUP WAS WRITTEN TWICE — once for the ranked `<tbody>` and once
 * for the unranked partition — and two copies of eight cells is a divergence waiting to happen:
 * the next column added to one and forgotten in the other renders a table whose partition shows
 * different facts about the same cohort. The `<tr>` differs between the two (key, class, and the
 * rank cell never shows an integer in the partition), so only the cells move here.
 */
function RowCells({ row, rankingServed, foldStatus, absentLabel, covState, assoc, assocState }) {
  const band = bandFor(row.mean_plddt)
  const absent = row.mean_plddt == null
  return (
    <>
      {/* ⚠⚠ THE RANK CELL. A ranked row shows its integer. An unranked row shows its CAUSE —
          never a number, never a dash, and never a position it does not hold.
          ⚠ `.col-rank` bounds the column and `.rank-cause` demotes the sentence; every character
          of the cause is still rendered (see the block above `COLUMNS`). */}
      <td className="mono col-rank">
        {row.rank != null
          ? row.rank
          : <span className="rank-cause">{rankCause(row, rankingServed)}</span>}
      </td>
      {/* ⚠⚠ A cohort member with no analysis row has no card to open. `/target/null` would be a
          link that 404s, which is worse than no link — it invites a click and then denies it. The
          gene renders as plain text and the reason column says why. */}
      <td>
        {row.id != null
          ? <Link to={`/target/${row.id}`}>{row.gene}</Link>
          : <span className="gene-unlinked" title="no fold was attempted, so there is no structure page">{row.gene}</span>}
      </td>
      <td className="mono">{row.accession}</td>
      <td className="col-description"><DescriptionCell row={row} state={covState} /></td>
      <td className="col-assoc"><AssociationCell row={row} assoc={assoc} state={assocState} /></td>
      <td>
        <span className={`tier-tag tier-${row.tier}`} title={row.tier_reason || undefined}>
          {row.tier ?? '—'}
        </span>
      </td>
      <td className="mono">{row.mean_plddt != null ? row.mean_plddt.toFixed(2) : '—'}</td>
      {/* 1b — demoted: the band colour is retained (no information removed) but rendered as a
          secondary signal rather than the row's most eye-catching element. */}
      <td className="col-secondary">
        {absent ? (
          <span className="absent-reason" title={foldStatus[row.accession]?.fail_reason || undefined}>
            {absentLabel(row)}
          </span>
        ) : (
          <>
            <span className="dot dot-secondary" style={{ background: band.color }} /> {band.label}
          </>
        )}
      </td>
    </>
  )
}

export default function TargetList() {
  const [rows, setRows] = useState(null)
  const [error, setError] = useState(null)
  const [tierFilter, setTierFilter] = useState('all')
  const [sort, setSort] = useState(null)          // null = the default order
  const [foldStatus, setFoldStatus] = useState({}) // accession -> { fold_status, fail_reason }
  const [coverage, setCoverage] = useState([])     // the 82 manifest rows, for the members with no analysis
  const [query, setQuery] = useState('')
  const [ranks, setRanks] = useState(null)         // accession -> rank, from the pre-registered run
  // ⚠ D-142: the two new columns each track their supplier's state explicitly — see the enum above.
  const [covState, setCovState] = useState(SUPPLIER_LOADING)
  const [assoc, setAssoc] = useState(null)         // the whole /api/associations payload (D-053)
  const [assocState, setAssocState] = useState(SUPPLIER_LOADING)

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
        setCovState(SUPPLIER_LOADED)
      })
      .catch(() => { setFoldStatus({}); setCoverage([]); setCovState(SUPPLIER_FAILED) })
  }, [])

  // ⚠⚠ D-142 — THE ASSOCIATION MAP, FROM THE SUPPLIER THAT ALREADY SERVES IT (D-053). The grid is
  // consumed, never re-derived: `core/cancer_associations.py` validates the rows, applies the
  // paper's cutoff and sorts each target's pairs, and a second ordering here would be free to
  // disagree with the detail card that renders the same target.
  // ⚠ Additive in the same posture as coverage: the map failing costs the column its values and
  // costs the list nothing. `Promise.resolve()` first so a supplier that throws synchronously —
  // which is exactly what a test double without this method does — cannot take the page down.
  useEffect(() => {
    Promise.resolve()
      .then(() => getAssociations())
      .then((payload) => {
        // ⚠ A response with no `associations` object is not a loaded map. Treating it as one would
        // print "no association recorded" — a claim about 82 targets — from a malformed payload.
        if (!payload?.associations) throw new Error('no associations in payload')
        setAssoc(payload)
        setAssocState(SUPPLIER_LOADED)
      })
      .catch(() => { setAssoc(null); setAssocState(SUPPLIER_FAILED) })
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
  // ⚠ D-142: accession -> the manifest's UniProt protein name, the Description column's only
  // source. Built from the coverage rows already fetched above — no second request.
  const descriptions = {}
  for (const c of coverage) {
    if (c?.accession && c.protein_name) descriptions[c.accession] = c.protein_name
  }
  // ⚠ rank and the coverage facts join onto the row so one sort mechanism sees everything.
  const rankMap = ranks ?? {}
  const all = [...rows, ...missing].map((r) => ({
    ...r,
    rank: rankMap[r.accession] ?? null,
    // ⚠⚠ JOINED ONTO THE ROW, not read inside the cell, and that is what makes the header sortable:
    // `sortRows` reads `r[key]`, so a description that lived only in JSX would render a sort
    // control that ordered by `undefined` on every row — a silent no-op wearing a caret.
    // ⚠ `?? null`, never `?? ''`: an empty string is a VALUE to `sortRows.isAbsent` and would sort
    // the un-named rows to the front alphabetically instead of holding them out as a category.
    description: descriptions[r.accession] ?? null,
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

  // ⚠⚠ THE CITATION IS EMITTED IF AND ONLY IF A ROW ON SCREEN RENDERED A TUMOUR TYPE. Elements 1–3
  // are properties of the source, so ANY covered symbol's block carries the same three strings —
  // what matters is that a value was drawn. Reading it off the FILTERED rows rather than the whole
  // cohort is the suppression half of the ruling: filter to a tier whose rows have no association
  // and the credit goes with them, because a citation attached to nothing is not compliance.
  const assocCredit = (assocState === SUPPLIER_LOADED && assoc)
    ? (filtered
        .map((r) => (summariseAssociations((assoc.associations ?? {})[r.gene]).total > 0
          ? assoc.attributions?.[r.gene]
          : null))
        .find(Boolean) ?? null)
    : null

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
      {/* ⚠⚠ D-142 — THE TWO NEW COLUMNS STATE WHAT THEY ARE, ON THE PAGE. D-069's self-sufficient
          surfaces, and for the association column the claim boundary is not optional: it is the
          same sentence the detail card carries (D-053 orders §2b), because a reader who never
          opens a card must not be able to read "cancer association" as causation.
          ⚠ The cutoff is INTERPOLATED from the payload, never typed — D-053 decision 5: our
          statistics derive, and only the paper's own 290/16 are literals (and they live on the
          card, not here). */}
      {/* ⚠⚠ "the protein name UniProt records", NOT UniProt's own term of art *recommended name* —
          and the change was forced by a guard, which is the guard working. The D-039/F-009 denylist
          bans `\brecommended\b` anywhere on this list, and it fired on this sentence. It cannot
          tell a UniProt field name from a recommendation of a target, and per the F-009 §3 lesson
          the copy AVOIDS the banned vocabulary outright rather than negating it. */}
      <p className="note column-scope-note">
        <strong>Description</strong> is the protein name UniProt records for that accession, from
        the committed cohort manifest — a name, not a finding.{' '}
        <strong>Cancer association</strong> is an{' '}
        <em>expression</em> claim by the source paper&rsquo;s own measure (quasi H-score above{' '}
        {assocState === SUPPLIER_LOADED && assoc?.cutoff != null
          ? assoc.cutoff
          : 'the paper\u2019s stated cutoff'}, from Human Protein Atlas immunohistochemistry):{' '}
        <em>not</em> causation, <em>not</em> a claim the target drives the disease, and <em>not</em>{' '}
        a clinical indication. The cell names the tumour type(s) with the highest score and how many
        the map holds for that target; every pair, with its score, is on the target&rsquo;s own page.{' '}
        ⚠ That column has <strong>no sort control</strong>, deliberately: the cell holds a set of
        tumour types, and ordering the cohort by the leading score — or by how many types clear the
        cutoff — would make an expression statistic the page never shows into the order of the list.
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
          {sorted.map((r) => (
            <tr key={r.accession ?? r.id}>
              <RowCells
                row={r}
                rankingServed={rankingServed}
                foldStatus={foldStatus}
                absentLabel={absentLabel}
                covState={covState}
                assoc={assoc}
                assocState={assocState}
              />
            </tr>
          ))}
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
            {/* ⚠ `rank` is null on every row here, so `RowCells` renders the cause in column one
                by the same branch the ranked body uses — one rank cell, not two that can drift. */}
            {unranked.map((r) => (
              <tr key={r.accession ?? r.id} className="row-unranked">
                <RowCells
                  row={r}
                  rankingServed={rankingServed}
                  foldStatus={foldStatus}
                  absentLabel={absentLabel}
                  covState={covState}
                  assoc={assoc}
                  assocState={assocState}
                />
              </tr>
            ))}
          </tbody>
        )}
      </table>
      {/* ⚠⚠ HPA ELEMENTS 1–3, ONCE, AND ONLY IF A TUMOUR TYPE ACTUALLY RENDERED (D-100 / D-142).
          The per-datum link (element 4) is the anchor on each cell's tumour type; these three are
          properties of the SOURCE and render once per page — the split-by-case ruling of
          2026-08-21, applied to a list instead of a card.
          ⚠ SUPPRESSED WHEN THE COLUMN SHOWED NOTHING: a licence-required citation beside a table
          of "loading…" or "could not be reached" is attached to nothing, which is the other half
          of that ruling. */}
      {assocCredit && <HpaCredit attribution={assocCredit} />}
    </div>
  )
}
