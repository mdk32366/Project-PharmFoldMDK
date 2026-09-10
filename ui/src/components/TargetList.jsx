import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getAssociations, getCensusSummary, getCoverage, getRanking, listAnalyses } from '../api.js'
import { bandFor } from '../plddt.js'
import { nextSort, sortRows } from '../sortRows.js'
import { filterRows } from '../searchRows.js'
import { count } from '../plural.js'
import { summariseAssociations } from '../associationSummary.js'
import { COHORT_PAPER_DOI, COHORT_PAPER_SHORT, COHORT_PAPER_URL } from '../cohortPaper.js'
import { HpaCredit } from './HpaAttribution.jsx'
// ⚠⚠ D-155 — THE THREE PIECES `/coverage` USED TO OWN. That route is gone: it listed the SAME 82
// rows this table lists, and one population with two tables is a reader asked to hold half a
// protein's story on each of two pages. `CoverageLine` is the honest denominator (D-024 am. §3),
// `CensusPopulationStrip` is the second population (D-135), and `coverageNote` / `censusBridge`
// are the per-row facts — all three arrive unchanged, and each one is a CLAIM rather than a
// layout, which is why none of them is inside a `<details>` here either.
import CoverageLine from './CoverageLine.jsx'
import CensusPopulationStrip from './CensusPopulationStrip.jsx'
import { coverageNote, hasCoverageNote } from './coverageNote.jsx'

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
  // ⚠ The scorer's ordering, and the default. An unranked row shows a DASH here and its cause in
  // the Status cell (D-155) — never a number, and never a position it does not hold.
  // ⚠⚠ THE CAUSE MOVED BECAUSE OF WHAT IT COST HERE, MEASURED. At 1,200 px this column was
  // **140 px** — 12% of the table — for content that is a one- or two-digit integer on 68 of 83
  // rows; the width was set by the 15 rows carrying a cause phrase and by one 435-character group
  // heading. `.col-rank`'s cap then wrapped those phrases over four lines, which is where the mean
  // row height came from. ⚠ **Demotion is not deletion**: every character of every cause still
  // renders, one cell to the right, beside the disposition it explains.
  { key: 'rank', label: 'Rank', className: 'col-rank-num' },
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
  // ⚠⚠ D-155 — ONE STATUS COLUMN WHERE THERE WERE FOUR FACTS ON TWO PAGES, and it is the D-150
  // census pattern applied to the cohort rather than a new invention. `/coverage` carried
  // **Disposition** and **Fold** as columns of their own; this list carried **Fold confidence** as a
  // third, and the *cause* of an absent rank sat in a fourth place again — the Rank cell. A reader
  // scanning for *"what happened to this target?"* had to read two pages and three columns.
  // ⚠ The four are orthogonal and stay orthogonal, stacked as separate lines in one cell:
  // *disposition* (ranked / held out / excluded — D-024's partition), *fold* (folded / failed /
  // not yet — D-043's three values, never a fourth), and *confidence* (the band, demoted, only
  // where a fold exists). Nothing is merged into a composite and nothing is dropped.
  // ⚠⚠ SORTS ON `disposition`, WHICH IS THE PARTITION AND NOT A QUALITY. The other two axes are
  // deliberately not sortable: `fold_status` would order a cohort by whether a card was free, and
  // the band is the demoted signal this surface spent D-048 refusing to lead with.
  { key: 'disposition', label: 'Status (disposition · fold · confidence)', className: 'col-status',
    order: ['excluded', 'held_out', 'ranked'] },
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
      {/* ⚠⚠ D-155 — THE INTEGER, OR THE WORD `unranked`, AND NEVER A BARE DASH. The cause moved to
          the Status cell in the same row so this column can be the width of the number it holds
          (measured: 140 px for a two-digit integer on 68 of 83 rows). The ROW stays self-sufficient
          (D-069); the COLUMN stops paying for a sentence.
          ⚠⚠ AND THE FIRST DRAFT OF THIS PUT AN EM DASH HERE, WHICH `TargetList.rank.test.jsx`
          REJECTED BY NAME — *"and never a bare dash"*. The guard was right and the draft was wrong:
          a dash is an absence with no name, which is the defect this project spends most of its
          copy avoiding, and the owner's TA2 ruling is that an unranked row is **not** a row with a
          missing number. So the cell states the category in a word, `title` carries the cause on
          hover, and the Status cell carries it in text for everyone else. */}
      <td className="mono col-rank-num">
        {row.rank != null
          ? row.rank
          : <span className="rank-absent" title={rankCause(row, rankingServed) || undefined}>unranked</span>}
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
      {/* ⚠⚠ D-155 — THE STATUS CELL: three orthogonal lines, and the disclosure that holds the
          long reasons. 1b's demotion is inherited and not undone — the band colour is still a
          secondary signal rather than the row's most eye-catching element. */}
      <td className="col-status">
        <StatusCell row={row} rankingServed={rankingServed} foldStatus={foldStatus}
                    absentLabel={absentLabel} band={band} absent={absent} />
      </td>
    </>
  )
}

/**
 * D-155 follow-up — drop a leading fold verdict from an absence label, keeping the reason.
 *
 * ⚠⚠ `absentLabel` builds *"not folded — oversize: 4030 aa …"* and *"fold failed — CUDA OOM …"*,
 * which are exactly right in a column of their own and say the fold verdict a SECOND time when
 * axis B is directly above them. This keeps the half axis B does not carry.
 * ⚠ It strips a known PREFIX and never searches for one: a label that does not start with a verdict
 * is returned whole, so a future wording cannot be silently truncated by a loose match. And it
 * never empties a cell — a label that is nothing but the verdict is left as it is, because *"not
 * folded"* twice is a repetition and a blank cell is an unnamed absence, which is worse (`D-154`).
 */
export function causeOnly(label) {
  const text = String(label ?? '')
  for (const verdict of ['not folded — ', 'fold failed — ']) {
    if (text.startsWith(verdict)) {
      const rest = text.slice(verdict.length).trim()
      return rest || text
    }
  }
  return text
}

//: The words for D-024's partition, spelled for a reader rather than for the payload. ⚠ `held_out`
//: is not a judgement about the protein — D-021 holds it out because its boundary method is not
//: comparable, which the disclosure below says in full.
const DISPOSITION_COPY = {
  ranked: 'in the ranking set',
  held_out: 'held out of ranking',
  excluded: 'excluded from the cohort',
}

//: Why a disposition is what it is, where the record has a reason that is a property of the
//: PARTITION rather than of the row. ⚠ `D-021` holds a target out because its boundary method is
//: not comparable — that is not a judgement about the protein, and a cell that says only "held out"
//: invites the reader to supply their own reason.
const DISPOSITION_WHY = {
  held_out: 'held out of ranking because its boundary method is not comparable (D-021) — not a '
    + 'judgement about the target',
  excluded: 'excluded from the cohort by name (D-022)',
}

/**
 * ⚠⚠ D-155 FOLLOW-UP 2 — DOES THE CAUSE ADD ANYTHING THE DISPOSITION HAS NOT ALREADY SAID?
 *
 * The first follow-up suppressed the cause wherever the FOLD axis already carried it, and the
 * deployed page then read *"held out of ranking · no rank — held out · folded · Confident
 * backbone"* — the same repetition, one axis over. ⚠ **Two rounds on one cell is the argument for
 * enumerating the branches instead of fixing the instance**, so every string `rankCause` can return
 * was checked against what the other axes say:
 *
 *   · `no ranking run is currently served` — nothing else says it            → SHOW
 *   · `excluded by the pre-registered mean pLDDT floor of 50` — nothing else → SHOW
 *   · `unranked — no cause recorded` — names an absence of cause             → SHOW
 *   · `held out` — axis A says exactly this                                  → SUPPRESS
 *   · `not folded — never attempted` / `fold attempted and failed` — axis B  → already suppressed
 *   · `held out; fold subsequently attempted and failed (CUDA OOM)…` — axis B + the `why`
 *                                                                            → already suppressed
 *
 * ⚠ An EQUALITY against a named restatement, never a substring test: *"excluded by the
 * pre-registered floor"* starts with the word `excluded` and must still show on a `ranked` row,
 * which a `startsWith` would have swallowed.
 */
const DISPOSITION_RESTATEMENT = { held_out: 'held out', excluded: 'excluded' }

export function causeAddsSomething(cause, disposition) {
  if (!cause) return false
  return cause !== DISPOSITION_RESTATEMENT[disposition]
}

/**
 * D-155 — one cell, three orthogonal answers, and every long reason one click away.
 *
 * ⚠⚠ THIS IS D-150's CENSUS PATTERN, NOT A NEW ONE. That entry split *structure served · scored ·
 * seam* into three lines on the census because one word (`Folded`) had been doing all three jobs
 * and **could not be wrong**. The cohort had the mirror-image defect: four facts spread across two
 * pages and four columns, so nothing was wrong anywhere and no single place answered *what
 * happened to this target*.
 *
 * ⚠ THE THREE AXES:
 *   A · disposition — `ranked` / `held_out` / `excluded`, D-024's partition. Sortable.
 *   B · fold — `folded` / `failed` / `not yet`, D-043's three values. **A census structure of the
 *       same accession never becomes a fourth value**; it renders as a labelled bridge chip in the
 *       disclosure and says it is a different population (D-135 / D-081).
 *   C · confidence — the band, and ONLY where a fold exists. An absent fold shows its cause here
 *       instead, which is where `/targets`' old Fold-confidence column already put it.
 *
 * ⚠⚠ THE DISCLOSURE IS A CONTROL OVER LENGTH, NEVER OVER A CLAIM. Every row's disposition, fold
 * and confidence are visible without opening anything. What collapses is the *prose*: a fold
 * failure's full text (IGF2R's is 765 characters), an exclusion reason, and the census bridge.
 * Measured on `/coverage` at 1,200 px: that prose was a column **58% of the table's width** with
 * content on **3 of 82 rows**. ⚠ It is not `open` by default and it is not rendered at all where
 * the row has nothing to disclose — a control that opens onto nothing promises a reason the record
 * does not hold.
 */
function StatusCell({ row, rankingServed, foldStatus, absentLabel, band, absent }) {
  const st = foldStatus[row.accession]
  const foldState = row.fold_status ?? st?.fold_status
  // ⚠⚠ D-155 FOLLOW-UP — THE CELL SAID `not folded` THREE TIMES, AND IT TOOK LOOKING AT IT TO SEE.
  // On the deployed merge `MUC16` and `FAT2` read: *"excluded from the cohort — not folded — never
  // attempted · not folded · not folded — oversize"*. Three axes, one fact, three spellings — the
  // exact defect `D-150` fixed on the census and the owner reported again at the D-150 follow-up.
  // ⚠ THE RULE: an axis states what the axis knows and never what the one beside it already said.
  //   · the CAUSE is shown only where the row HAS a fold — where it does not, axis B is the reason
  //     it has no rank, and repeating that as a cause adds a sentence and no fact;
  //   · axis C drops a leading fold verdict for the same reason, keeping only the reason itself.
  // ⚠ Nothing is lost: the full text is in the `why` disclosure, untruncated, on every row that has
  // one — and `IGF2R`'s CUDA-OOM sentence is exactly such a row.
  const rawCause = rankCause(row, rankingServed)
  const cause = foldState === 'folded' && causeAddsSomething(rawCause, row.disposition)
    ? rawCause
    : null
  // ⚠ The note reads the COVERAGE row's field names, which are already joined onto `row` upstream
  // (`fold_status`, `disposition`) plus the two the merge threads through — see the `all` map.
  const note = hasCoverageNote(row) ? coverageNote(row) : null
  return (
    <div className="status-cell">
      {/* A · the partition. ⚠ For an unranked row the CAUSE rides with it, because "held out" and
          "excluded by the pLDDT floor" answer the same question at two different depths. */}
      <span className={`status-line status-disposition disp-${row.disposition ?? 'unknown'}`}
            title={DISPOSITION_WHY[row.disposition] || undefined}>
        {row.disposition
          ? (DISPOSITION_COPY[row.disposition] ?? row.disposition)
          : <span className="unknown">disposition not recorded</span>}
      </span>
      {/* ⚠⚠ D-155 FOLLOW-UP — THE CAUSE IS ITS OWN LINE, PREFIXED `no rank`, AND THAT PREFIX FIXES A
          FLAT CONTRADICTION. Joined to the disposition by an em dash it read *"in the ranking set —
          excluded by the pre-registered mean pLDDT floor of 50"*, which says a row is in the set and
          excluded from it in one breath. Both halves are true and they are about DIFFERENT things:
          `ranked` is `D-024`'s partition of the cohort, and the floor decides membership of the
          SCORED set at fit time — the 67-versus-56 reconciliation `D-066` put on `/scorer`. The
          prefix names which question the sentence answers. */}
      {cause && (
        <span className="status-line status-cause">no rank — {cause}</span>
      )}
      {/* B · the fold. ⚠ Three values and never a fourth (D-043). */}
      <span className="status-line status-fold">
        {foldState === 'folded' ? <span className="folded">folded</span>
          : foldState === 'failed' ? <span className="failed">fold failed</span>
          : foldState === 'not_folded' ? <span className="not-folded">not folded</span>
          : <span className="unknown">fold state unavailable</span>}
      </span>
      {/* C · the confidence, demoted, and only where a fold exists. */}
      <span className="status-line status-confidence col-secondary">
        {absent ? (
          <span className="absent-reason" title={st?.fail_reason || undefined}>
            {causeOnly(absentLabel(row))}
          </span>
        ) : (
          <>
            <span className="dot dot-secondary" style={{ background: band.color }} /> {band.label}
          </>
        )}
      </span>
      {note && (
        <details className="status-note">
          <summary>why</summary>
          <div className="note-cell">{note}</div>
        </details>
      )}
    </div>
  )
}

export default function TargetList() {
  const [rows, setRows] = useState(null)
  const [error, setError] = useState(null)
  const [tierFilter, setTierFilter] = useState('all')
  const [sort, setSort] = useState(null)          // null = the default order
  const [foldStatus, setFoldStatus] = useState({}) // accession -> { fold_status, fail_reason }
  const [coverage, setCoverage] = useState([])     // the 82 manifest rows, for the members with no analysis
  // ⚠ D-155 — the two suppliers `/coverage` used to own, now consumed here. `coverageObj` is
  // D-024's partition object; `census` is the SECOND population (D-135) and is deliberately kept
  // apart from every cohort number on this page — it has no denominator and shares none.
  const [coverageObj, setCoverageObj] = useState(null)
  const [census, setCensus] = useState(null)
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
        // ⚠⚠ D-155: the `coverage` OBJECT, not just its rows. `CoverageLine` states D-024's
        // partition and reads `coverage.denominator` — the manifest's 82, computed by
        // `core/manifest.py` and never by counting what happened to be fetched. Storing the object
        // separately is what keeps that denominator a property of the cohort rather than of this
        // page's luck with a request.
        setCoverageObj(cov?.coverage ?? null)
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
      .catch(() => { setFoldStatus({}); setCoverage([]); setCoverageObj(null); setCovState(SUPPLIER_FAILED) })
  }, [])

  // ⚠⚠ D-155 / D-135 — THE SECOND POPULATION, GUARDED THE WAY `/coverage` GUARDED IT.
  // `Promise.resolve().then(...)` so a supplier that throws SYNCHRONOUSLY — or is not a promise at
  // all — costs this page the census strip and never the cohort table it exists for. ⚠ The strip
  // renders below the table and is NOT collapsed: D-135 exists because this project once described
  // 82 proteins and said nothing about the 3,467, and moving a block is not demoting it.
  useEffect(() => {
    Promise.resolve().then(() => getCensusSummary()).then(setCensus).catch(() => setCensus(null))
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
  // ⚠⚠ D-155 — THE WHOLE COVERAGE ROW, BY ACCESSION. `/coverage`'s Note cell read four fields this
  // list never joined (`excluded`, `exclusion_reason`, `fail_reason`, `census_sibling`), so the
  // merge threads them onto the row rather than reaching into a second map inside the cell. ⚠ The
  // cohort's own fields WIN on collision: `tier` and `tier_reason` fall back to coverage only where
  // the analyses row has none, which is exactly the two members that have no analyses row at all
  // (`FAT2`, `MUC16`) and rendered a bare `—` in the Tier column until now.
  const covByAccession = {}
  for (const c of coverage) if (c?.accession) covByAccession[c.accession] = c
  // ⚠ rank and the coverage facts join onto the row so one sort mechanism sees everything.
  const rankMap = ranks ?? {}
  const all = [...rows, ...missing].map((r) => ({
    ...r,
    ...(() => {
      const c = covByAccession[r.accession] ?? {}
      return {
        excluded: c.excluded ?? false,
        exclusion_reason: c.exclusion_reason ?? null,
        fail_reason: c.fail_reason ?? null,
        census_sibling: c.census_sibling ?? null,
        tier: r.tier ?? c.tier ?? null,
        tier_reason: r.tier_reason ?? c.tier_reason ?? null,
      }
    })(),
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
      {/* ⚠⚠ D-152 — THE CENSUS TREATMENT, APPLIED HERE, AND THE ORDER IS THE WHOLE CHANGE.
          Owner, 2026-09-09: *"Apply what was done for Census to the rest of the surfaces."* On this
          page the search box and the table sat beneath four paragraphs — the lede, the paper
          citation, the confidence-scope note and the ~700-character column-scope note — and the
          last of those is the longest block of prose on the surface.
          ⚠ THE REMEDY IS ORDER AND DISCLOSURE, NEVER OMISSION, which is D-151's rule inherited
          rather than re-derived. The column-scope note moves into ONE collapsed `<details>` that
          costs a line and sits directly above the header row it defines; every other block stays
          exactly where it was, in full, with the same words.
          ⚠ THE PAGE HAD NO HEADING AT ALL. It opened on a `<p>`, so the browser's own outline —
          and every screen reader that builds one — saw a table with no name. The `<h2>` carries the
          MENU's words (D-151 ruled the label *Initial Targets*), because a reader who clicked that
          entry must land on a page that agrees with it. */}
      <h2>Initial Targets — the cohort of {all.length}</h2>
      <p className="lede">
        The {all.length} cohort targets: <strong>{nFolded} folded</strong>
        {nFailed > 0 && <>, {nFailed} attempted and failed</>}
        {nNever > 0 && <>, {nNever} too large to attempt</>}. Start with{' '}
        <Link to="/target/1">NECTIN4 →</Link> (the target of a marketed ADC, enfortumab vedotin).
      </p>
      {/* ⚠⚠ D-155 — THE HONEST DENOMINATOR LEADS THIS PAGE NOW, AND IT IS NOT COLLAPSED. It was the
          headline of `/coverage`, which listed these same 82 rows; that route is gone and its claim
          came with it rather than being summarised. D-024 amendment §3 requires the intersection
          `ranked ∧ folded` — never the ranked count, never the folded count, both of which overstate
          the cohort toward completeness — and `CoverageLine` computes it from the rows, unchanged.
          ⚠ It sits ABOVE the lede's own counts on purpose: the lede says how many folded, and this
          says how many of those are actually in the ranking set. The reader meets the stricter
          number first.
          ⚠ ABSENT SUPPLIER, ABSENT LINE — never a zero. If `/api/coverage` could not be reached the
          panel does not render and `covState` already tells the columns below to say so; a
          denominator drawn from an empty fetch would read as a cohort that shrank. */}
      {coverageObj && <CoverageLine coverage={coverageObj} rows={all} />}
      {/* 1c — the one sentence that inoculates the glance, before any detail panel is opened.
          OWNER-COPY PLACEHOLDER: substance fixed, wording for the owner to finalise.
          ⚠⚠ D-152 MOVED IT UP AND REFUSED TO COLLAPSE IT. It is this surface's standing claim —
          the census's unscored bar, one page along — and a reader who stops at the first row must
          already have met it. That is the rule `CensusView`'s `.census-bar` has carried since
          D-079 dec 1, and the reason is the same: the defect this sentence exists to prevent is a
          green dot being read as a verdict on a target, and it cannot prevent it from behind a
          `<summary>`. */}
      <p className="note confidence-scope-note">
        Fold confidence is the model&rsquo;s certainty about the <em>predicted structure</em> — not a
        judgement of whether the target is a good ADC candidate. Scoring lives on{' '}
        <Link to="/scorer">Scorer</Link>.
      </p>
      {/* ⚠⚠ D-151 — THE PAPER THIS WHOLE LIST COMES FROM, AND IT IS NOW OPENABLE. This surface has
          named "Kathad et al." in prose since F-009 and never once linked it, so the single
          artefact that defines which 82 proteins appear here could not be reached from the page
          that renders them. A citation a reader cannot follow is an assertion, not a source.
          ⚠ ONE link, near the top, rather than an anchor on every mention: the Description and
          Cancer association columns below already carry their own per-datum HPA links (D-142 /
          D-100), and littering a third link through the same paragraphs makes all of them read as
          decoration.
          ⚠ It is deliberately NOT the HPA citation. D-100 records that Kathad's S3 is a verbatim
          extract of HPA's `pathology.tsv` — citing the paper is not citing HPA, so `HpaCredit`
          below is unchanged and still emits the licence's own four elements. */}
      <p className="note cohort-paper-cite">
        The cohort of record comes from one published paper:{' '}
        <a
          className="cohort-paper-link"
          href={COHORT_PAPER_URL}
          rel="noopener noreferrer"
          target="_blank"
        >
          {COHORT_PAPER_SHORT}
        </a>
        , PLOS ONE, CC-BY (DOI <code>{COHORT_PAPER_DOI}</code>). It is a{' '}
        <strong>comparator set</strong>, not a census of everything an ADC could target —{' '}
        <Link to="/about">what the 82 is, and is not</Link>.
      </p>
      {/* ⚠⚠ D-152 — THE SEARCH BOX AND THE TIER FILTER MOVE ABOVE THE COLUMN NOTE, NOT ABOVE THE
          TWO CLAIMS. The lede states the population, the confidence note is the standing claim and
          the paper citation is the primary source D-151 shipped precisely so it could be reached —
          those three are what a reader must pass. The ~700 characters that used to come after them
          and before the controls are now one summary line BELOW the controls. */}
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
          {/* ⚠⚠ D-155 — THE SENTENCE ARRIVED WITH THE HEADLINE, AND IT MATTERS MORE HERE THAN IT DID
              ON `/coverage`. A filtered table under an unqualified total was already the defect this
              line was written for; now there is a DENOMINATOR PANEL directly above the filter, so a
              reader who types `CA-125` sees one row beneath "67 ranked & folded of 82" and has to be
              told, in words, that the second number is a property of the cohort and not of their
              search. ⚠ `CoverageLine` computes from the UNFILTERED rows — this states what the code
              already does, which is the only kind of claim worth printing. */}
          {' '}The denominator above is unchanged: it is a property of the cohort, not of this filter.
        </p>
      )}
      {/* ⚠⚠ TA3 / D-102 — THE LENS IS STATED WHERE THE LENS IS APPLIED. pLDDT is still available as
          a sort the reader chooses; what it may not be is the order the page arrives in unlabelled.
          ⚠ D-152 does NOT collapse it, for D-102's reason rather than for balance: it appears only
          when that sort is in force, and it says what the order currently MEANS. A statement about
          the applied ordering behind a `<summary>` is a statement the reader can look at the
          ordering without having seen. */}
      {active.key === 'mean_plddt' && (
        <p className="note plddt-lens-note">{PLDDT_LENS_NOTE}</p>
      )}
      {/* ⚠⚠ D-152 — THE COLUMN NOTE, COLLAPSED AND NOT CUT, DIRECTLY ABOVE THE HEADER ROW IT
          DEFINES. This is `CensusTable`'s `.census-notes` move on the other list: a `<details>` is
          a disclosure control and not a filter — the text is in the DOM either way, the browser's
          own find-in-page reaches it, and every existing assertion in `TargetList.columns.test.jsx`
          reads it unchanged.
          ⚠ ADJACENCY IS THE POINT. D-069 requires this surface to be self-sufficient and D-142
          requires the association column's claim boundary to be on the page; both are satisfied by
          a block one click from the header row, and neither would be by a paragraph at the foot of
          the page or a link to a glossary.
          ⚠ It is NOT `open`: an `open` default restores the exact scroll it was collapsed to end
          while looking like a fix. */}
      <details className="surface-notes target-notes">
        <summary>
          How to read this table — what Description and Cancer association mean, and why one of
          them has no sort control
        </summary>
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
      </details>
      {/* ⚠⚠ D-152 — THE TABLE SCROLLS AND THE PAGE DOES NOT. ⚠ AND THE DEFECT HERE WAS **NOT** THE
          CENSUS'S DEFECT, WHICH IS WORTH RECORDING BECAUSE THE FIRST DRAFT OF THIS COMMENT SAID IT
          WAS. It claimed this table pushed the document 175 px past the right edge — the census's
          symptom, assumed rather than measured. The measurement says otherwise: at 1440×900 on
          `41b9b3b`, `/targets` reported a horizontal bleed of **0**. `.col-rank`, `.col-description`
          and `.col-assoc` already carry max-widths (D-142), so the table never overflowed.
          ⚠⚠ WHAT IT DID INSTEAD IS WORSE, AND IT IS WHAT THOSE MAX-WIDTHS COST: eight columns
          squeezed into a ~912 px content box wrapped nearly every cell, so the page ran to
          **16,409 px** — a mean row height of about **190 px** for a table of one-line facts, and
          nineteen screens of scrolling for 83 rows. The bound was doing exactly what D-142 designed
          it to do; it was the 60rem measure around it that was wrong.
          ⚠ So the port here is for the sticky `<thead>` and for the narrow viewport, and the wide
          measure is what actually pays: 16,409 px → 1,130 px with no column dropped, no cell
          truncated and `.col-rank`'s 144-character cause still rendered in full. A column removed
          to make a table fit is data withheld to flatter a layout.
          ⚠ `position: sticky` resolves against the nearest scrollport ancestor, so the shared
          `.table-scroll thead th` rule works because this wrapper exists and has a height bound. */}
      <div className="table-scroll">
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
      </div>
      {/* ⚠⚠ HPA ELEMENTS 1–3, ONCE, AND ONLY IF A TUMOUR TYPE ACTUALLY RENDERED (D-100 / D-142).
          The per-datum link (element 4) is the anchor on each cell's tumour type; these three are
          properties of the SOURCE and render once per page — the split-by-case ruling of
          2026-08-21, applied to a list instead of a card.
          ⚠ SUPPRESSED WHEN THE COLUMN SHOWED NOTHING: a licence-required citation beside a table
          of "loading…" or "could not be reached" is attached to nothing, which is the other half
          of that ruling.
          ⚠⚠ D-152 LEFT IT OUTSIDE EVERY DISCLOSURE CONTROL, and that is decided by the licence
          rather than by the layout: HPA words citation as a precondition of DISPLAY — *"be sure
          that our content is never displayed in the absence of such citation"* — so a credit the
          reader must open a `<summary>` to see is a credit that is not displayed. It is the same
          block, held out of the same control, for the same reason `D-151` held it out on the
          census. */}
      {assocCredit && <HpaCredit attribution={assocCredit} />}
      {/* ⚠⚠ D-155 / D-135 — THE SECOND POPULATION, BELOW THE TABLE AND OUTSIDE EVERY DISCLOSURE.
          It arrived here with `/coverage`, and every clause of D-135 still holds: it is below the
          coverage line, labelled *a different population*, carries no denominator and no fraction,
          and its chips keep the assembled caveat beside them (D-133 am. 1).
          ⚠ WHY IT MATTERS MORE ON THIS PAGE THAN ON THE ONE IT LEFT: this table is the cohort of
          82 with a rank column, and the census is 3,467 rows that are deliberately NOT ranked
          (D-079 dec 1). A reader who leaves this page believing the 82 is the whole of the work is
          the exact misreading D-135 was written to prevent, and they are more likely to form it
          here — beside a ranking — than they were beside a coverage table.
          ⚠ NOT a `<details>`, for that reason: a claim about the scale of the work is not an
          explanatory aside. Moving a block is not demoting it; hiding one is. */}
      <CensusPopulationStrip summary={census} />
    </div>
  )
}
