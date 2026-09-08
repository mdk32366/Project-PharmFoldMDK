import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { bandFor } from '../plddt.js'
import { plural } from '../plural.js'
import { normalizeQuery, filterRows } from '../searchRows.js'
import { KIND_ORDER, kindCounts, resolveKind } from '../structureKinds.js'
import HpaAttribution from './HpaAttribution.jsx'

// The census surface (D-087). Searchable, sortable, and deliberately UNRANKED.
//
// ⚠⚠ DEFAULT ORDER IS ACCESSION, and that is a decision, not a fallback. D-079 bars scoring census
// rows, and a default sort by pLDDT would make a self-reported confidence into a de facto ranking —
// the thing the bar exists to prevent. The user may sort by anything; what the page must not do is
// arrive already having chosen.
//
// ⚠ The `intermittent` badge is on the ROW, not only in the detail panel (owner ruling). 1,557 of
// these spans are one loop of several (F-037); a reader scanning the table would otherwise see
// 1,557 spans that look like ectodomains and never learn otherwise.

// ⚠⚠ THE COST ORDER, AND IT IS A COST ORDER (D-137). Cheapest compute first — the order the
// API's `COST_ORDER` declares, mirrored here because the sort has to run before any row has been
// fetched. It orders nothing by suitability, and `span_unrecorded` is **not in it**: an
// unrecorded span has no place in a cost order, so it falls to the null branch and sorts LAST in
// both directions rather than becoming the dearest row on one click.
// ⚠ DECLARED ABOVE `COLUMNS` because `COLUMNS` reads it at module evaluation. A `const` below it
// would be in scope and uninitialised — a TDZ throw at import, not a lint warning.
export const COST_ORDER = ['local', 'rental', 'over_ceiling']

// ⚠ EXPORTED so a test can pin a key rather than infer the column set from rendered text. A
// column that quietly leaves this array takes its sort with it and the table still renders.
export const COLUMNS = [
  { key: 'accession', label: 'Accession', numeric: false },
  { key: 'gene', label: 'Gene', numeric: false },
  { key: 'label', label: 'Protein', numeric: false },
  // ⚠ 'aa' expanded on FIRST USE. It is standard notation to a structural biologist and
  // opaque to everyone else, and the owner spent a long while resolving it.
  { key: 'span_aa', label: 'Span (aa = amino acids)', numeric: true },
  { key: 'topology', label: 'Topology', numeric: false },
  // ⚠⚠ HOW THE FOLD WAS PRODUCED, AND SORTABLE (D-133). The kind was rendered as a badge in the
  // accession cell and was the one row property the table could NOT sort by — while the paragraph
  // above it claimed a sort on every column (D-087). The badge moved here rather than being
  // copied: one place to read it, one header to click.
  // ⚠ Sorts on `structure_kind`, the API's CATEGORY, never on `structure_kind_label` — the label
  // is prose that already changed once ('assembled' → 'assembled (provisional)') and a copy edit
  // must not silently re-order the table.
  // ⚠ `numeric: false` on purpose, and it is the same ruling as Profile: four kinds with no
  // magnitude sort into GROUPS. Ascending happens to put `assembled` first; that is alphabetical
  // happenstance and not a suitability order, and nothing here ranks a census row.
  { key: 'structure_kind', label: 'Structure (single pass or assembled from tiles)', numeric: false },
  // ⚠⚠ WHAT THIS PROTEIN COSTS TO FOLD, AND THE HEADER SAYS SO IN THE HEADER (D-137). The axis
  // is `core.foldability`'s envelope against the measured ceiling — a **cost / tractability**
  // reading and **not** a suitability one, which D-077 dec 1 refusal 2 requires be stated in the
  // same visual frame. The header carries the short form; the legend below carries the long one.
  // ⚠⚠ SORTABLE, AND THAT IS THE WHOLE LICENSED SURFACE. Refusal 3 bars filtering the census by
  // cost, so there are deliberately NO cost chips beside the fold-type chips — see the comment on
  // the chip row. A header click groups the rows; it removes none of them.
  // ⚠ `order` rather than `numeric`: a cost HAS a magnitude (local is cheaper than rental is
  // cheaper than over-ceiling) and alphabetical would file `over_ceiling` between them, which
  // orders nothing a reader asked for. The order is CHEAPEST-FIRST COMPUTE COST and it ranks no
  // protein — `span_unrecorded` is absent from it on purpose and sorts last both ways.
  { key: 'cost', label: 'Cost to fold (compute — not suitability)', numeric: false,
    order: COST_ORDER },
  { key: 'mean_plddt', label: 'pLDDT', numeric: true },
  { key: 'tranche', label: 'Tranche', numeric: true },
  // ⚠⚠ A STATUS, NOT A VALUE, AND THAT IS RULING 2. This table sorts on every column (D-087), so a
  // profile VALUE here would be one header click from a ranked shortlist of 1,397 proteins. A
  // category sorts into GROUPS, which orders nothing by suitability. `numeric: false` on purpose:
  // there is no magnitude to compare.
  { key: 'profile_status', label: 'Profile', numeric: false },
  // ⚠⚠ SORTABLE, AND THAT IS RULED (D-102): "the ability to sort by a stained fraction is just
  // another way of looking at data, and it's not a rank either." The column header states the
  // lens, and the n rides in the cell — a percentage without its denominator is barred by the
  // ruling's own condition.
  { key: 'stained_pct', label: 'Stained %', numeric: true },
  { key: 'critical_n', label: 'Critical tissue', numeric: true },
]

// ⚠⚠ ONE FUNCTION DECIDES WHICH TOPOLOGY BADGE A ROW WEARS (D-133 am. 1). It used to be a nested
// ternary inside the JSX, which is not a thing another part of the surface can ask a question of —
// so a legend could not know which categories the table is actually showing without re-deriving
// them, and a re-derivation is a second definition waiting to disagree with the first.
export function topologyBadgeKey(r) {
  if (r.folded === false) return r.cohort_fold ? 'not_folded_here' : 'not_folded'
  if (r.topology === 'intermittent') return 'intermittent'
  if (r.topology === 'no_accepted_segment') return 'gpi'
  if (r.topology === 'contiguous') return 'contiguous'
  // ⚠ anything else is NOT contiguous — see the badge below. `unknown` means nobody derived it;
  // anything else means it was derived against a manifest that has since moved.
  return r.topology === 'unknown' ? 'not_derived' : 'derivation_stale'
}

// ⚠⚠ THE ACRONYM, SPELT OUT (owner ruling, 2026-09-08). "GPI-anchored" is four letters that mean
// nothing to a reader who does not already know them, and the badge said only that. The expansion
// lives HERE, once, and both the badge tooltip and the legend read it — a second copy is how a
// tooltip and a legend come to define the same word differently.
export const GPI_EXPANSION = 'glycosylphosphatidylinositol'
export const GPI_MEANING =
  `GPI-anchored — held on the outside of the cell by a ${GPI_EXPANSION} lipid anchor instead of by `
  + 'crossing the membrane, so the whole mature chain is outward-facing. UniProt records no '
  + 'topological domains for these BY DESIGN, so the absence is a different molecular architecture '
  + '— not missing data, and not an intermittent surface.'

// ⚠⚠ THE TOPOLOGY LEGEND (D-133 am. 1). The column has said `contiguous` / `intermittent (7)` /
// `GPI / no segment` / `not derived` / `derivation out of date` since D-087 and defined none of
// them on the page. Every one of those is a category with a cause, and a badge whose cause is only
// in a tooltip is a badge most readers meet as jargon.
// ⚠ `always: true` for the three standing categories; the rest appear only when a row actually
// wears the badge — a legend that explains absent categories is the wall the owner ruled against.
export const TOPOLOGY_LEGEND = [
  { key: 'contiguous', term: 'contiguous', always: true,
    meaning: 'the outward-facing part is one unbroken stretch, and that whole stretch is what was '
      + 'folded.' },
  { key: 'intermittent', term: 'intermittent (n)', always: true,
    meaning: 'the outward-facing part arrives in n separate segments. Only the LARGEST of them was '
      + 'folded; the others were left out, and the row says how many amino acids that was.' },
  { key: 'gpi', term: 'GPI / no segment', always: true, meaning: GPI_MEANING },
  { key: 'not_derived', term: 'not derived',
    meaning: 'the segment derivation has not been run for this protein. Nothing about its shape is '
      + 'claimed here.' },
  { key: 'derivation_stale', term: 'derivation out of date',
    meaning: 'the segments were derived against an older manifest than the file on disk, so the '
      + 'stale numbers are withheld rather than shown.' },
  { key: 'not_folded', term: 'NOT FOLDED / NOT FOLDED HERE',
    meaning: 'no structure was produced for this protein in the census. NOT FOLDED HERE means it '
      + 'was folded among the 82 ranked targets and not here — the row says which of the three '
      + 'reasons applies.' },
]

// ⚠ The Structure column's four kinds, defined in the same block (D-133 am. 1). The TERM is the
// API's own label, read off the rows — this list carries the meaning and never a second spelling.
export const STRUCTURE_LEGEND = [
  { kind: 'assembled',
    meaning: 'several folds of overlapping tile windows, joined where they overlap by per-residue '
      + 'confidence. ⚠ Not superimposed, and the seam is not solved — so it stays provisional.' },
  { kind: 'single-pass',
    meaning: 'one fold of the whole outward-facing span in a single pass — no tiles, no seam.' },
  { kind: 'tiles_only',
    meaning: 'tile folds exist for this protein and have not been assembled into a parent '
      + 'structure. A tile window is not the outward-facing region.' },
  { kind: 'mucin',
    meaning: 'out of class for this pipeline and never folded here.' },
  { kind: 'none', term: 'not recorded',
    meaning: 'no structure kind is recorded on the row. A blank is a missing field, never an '
      + 'implied single pass.' },
]

// ⚠ The order the fold-type chips appear in, and it is NOT a ranking — the two folded kinds first
// because they are what a reader came for, then the two absences, then the unrecorded rows.
// ⚠⚠ MOVED to `../structureKinds.js` at D-135 and re-exported here, because `/coverage`'s
// second-population strip reads the same vocabulary and a second copy of this order is how two
// pages come to state one population in two orders. Re-exported rather than relocated silently:
// existing callers and tests import `KIND_ORDER` from this module.
export { KIND_ORDER }

// ⚠⚠ ONE RULE DECIDES THE COST BADGE (D-137), the same shape as `topologyBadgeKey`. The legend
// asks it too, so the badge a row wears and the entry that explains it cannot come from two
// rules — which is the defect D-133 am. 1 had to extract a nested ternary to fix.
//
// ⚠⚠ THREE ABSENCES, AND THEY ARE NOT THE SAME ABSENCE:
//   `span_unrecorded` — the API looked, and the row carries no span. A named absence.
//   `not_served`      — the API sent no cost verdict at all. A missing FIELD, not a missing span,
//                       and rendering it as `span_unrecorded` would assert something about the
//                       protein that only the server is in a position to say.
//   an unknown word   — a category this page has never heard of. Rendered verbatim rather than
//                       coerced into one of ours: a vocabulary that grew on the server must not
//                       arrive here silently relabelled as something already understood.
export function costBadgeKey(r) {
  if (!r.cost) return 'not_served'
  return COST_ORDER.includes(r.cost) || r.cost === 'span_unrecorded' ? r.cost : 'unknown_verdict'
}

// ⚠ The four statuses, rendered as words rather than as a token. The three REFUSAL causes stay
// distinct — pooling 1,225 + 58 + 10 into one "n/a" would lose the reason, and an absence is a
// category with a cause.
const PROFILE_LABEL = {
  computed: 'computed',
  refused_out_of_distribution: 'outside fitted range',
  refused_span_below_floor: 'span too short to describe',
  refused_features_incomplete: 'measurements incomplete',
  refused_assembled_incommensurable: 'assembly — not a single-pass measurement',
  // ⚠ no fold exists, so there is nothing to profile — distinct from the refusals
  not_folded: 'no structure yet',
}

// ⚠⚠ THE TWO LENSES (D-102). Named on the surface because naming them IS the owner's ruling:
// "as long as you state what it is, it is neither judgement nor measurement". Over the same 1,727
// census genes, "stains in 100% of patients" is 728 proteins by best-panel and 16 pooled — a
// factor of 45 from identical data. An unlabelled figure here would be actively misleading.
export const LENSES = {
  best_panel: {
    label: 'best single cancer',
    meaning: 'the one cancer type where this protein stained in the largest share of patients',
    caveat: 'a maximum over ~20 small panels, so a high figure is partly a selection effect',
  },
  pooled: {
    label: 'all cancers pooled',
    meaning: 'every panel added together — one fraction over all patients examined',
    caveat: 'a protein strong in one cancer and absent elsewhere reads low here, correctly',
  },
}

// ⚠ Derived onto the row so the existing sort can see it. The lens is applied HERE and once, so a
// column can never show one lens while a caption names another.
export function withLens(rows, lens) {
  return rows.map((r) => {
    const s = r.staining?.[lens]
    const f = s && s.patients_tested ? s.patients_positive / s.patients_tested : null
    return {
      ...r,
      stained_pct: f == null ? null : Math.round(f * 1000) / 10,
      stained_n: s?.patients_tested ?? null,
      stained_cancer: s?.cancer ?? null,
      stained_category: s?.category ?? (r.staining ? 'never_scored' : 'not_covered'),
      critical_n: r.staining ? (r.staining.critical_normal_high?.length ?? 0) : null,
    }
  })
}

// ⚠⚠ THREE OUTCOMES, NOT ONE. "Waiting on rented capacity" was shown for 29 proteins whose fold
// ALREADY EXISTS among the ranked 82 — same span, rental hardware — and for IGF2R, which was tried
// there and died of CUDA OOM. A queue position, an existing result and a failed attempt are three
// different facts, and the row said the same thing for all of them.
export function notFoldedTitle(r) {
  if (r.cohort_fold) {
    const c = r.cohort_fold.mean_plddt
    return 'not folded in the census — but folded among the 82 ranked targets'
      + (c != null ? ` at mean confidence ${c}` : '')
  }
  if (r.cohort_attempt_failed) {
    const why = r.cohort_attempt_failed.reason
    return 'not folded — attempted among the 82 and failed'
      + (why ? `: ${why.slice(0, 70)}` : '')
  }
  return r.not_folded_copy
}

// ⚠⚠ D-137: a column may declare an explicit `order`, and a value outside it is a NULL. The Cost
// column is the case: `local` / `rental` / `over_ceiling` have a real magnitude that alphabetical
// order scrambles, while `span_unrecorded` has no place in a cost order at all. Putting it at the
// end of the array instead would make it the dearest row on a descending click — an absence
// rendered as the worst value, which is precisely what the null rule below exists to prevent.
function sortValue(r, col) {
  if (!col.order) return r[col.key]
  const i = col.order.indexOf(r[col.key])
  return i < 0 ? null : i
}

// ⚠ null sorts LAST in both directions. A missing pLDDT is not a low one, and letting it float to
// the top of an ascending sort would put unmeasured rows where the worst rows belong.
function compare(a, b, col, dir) {
  const av = sortValue(a, col)
  const bv = sortValue(b, col)
  if (av == null && bv == null) return 0
  if (av == null) return 1
  if (bv == null) return -1
  // ⚠ an `order` index is a number, so it compares like one — `numeric: false` stays true of the
  // COLUMN (there is no magnitude in the cell) while the rank it maps to sorts arithmetically.
  const c = (col.numeric || col.order) ? av - bv : String(av).localeCompare(String(bv))
  return dir === 'asc' ? c : -c
}

// ⚠⚠ PUNCTUATION IS NOT DECORATION IN THIS DOMAIN. UniProt stores `PDL1`, `NECTIN4`, `HER2`;
// people type `PD-L1`, `NECTIN-4`, `HER-2`. Comparing raw strings answers "no protein matches that
// search" for a protein we hold, which is the worst answer a search can give — it reads as absence.
// ⚠⚠ MOVED TO `../searchRows.js`, and re-exported here so existing callers and tests keep working.
// The census could find `HER2` and `/targets` could not, because the matcher lived in this file
// rather than beside `sortRows.js`. One matcher, both surfaces — `F-052`'s remedy, not its shape.
// ⚠ imported (this file calls `filterRows` itself) AND re-exported (existing tests import it here).
// A bare `export … from` would have re-exported the names without binding them in this module's
// scope, and line ~147 would throw at render — caught by reading the use, not by the edit.
export { normalizeQuery, filterRows }

// ⚠⚠ A CAP, AND IT IS STATED. The first version rendered all 2,629 rows: a 116,000px table body
// that no reader scrolls and every browser pays for. But a SILENT cap is worse than a slow page —
// it would show 200 rows above a count of 2,629 and let the reader assume they had seen the list.
// So the cap is announced, the full count stays visible, and there is a control to lift it.
const PAGE = 200

// ⚠⚠ `kindFilter` / `onKindFilter` ARE OPTIONAL, and the default stays uncontrolled (D-135).
// `/census` now keeps the fold-type filter in the QUERY STRING so `?structure=assembled` is a
// shareable address, which means the state has to be able to live above this component. But the
// table is also rendered on its own (in tests, and anywhere a caller has rows and no router), and a
// component that only works inside a URL is a component with a hidden dependency. So: controlled
// when a caller passes the pair, self-managed otherwise, and the SAME code path renders both.
export default function CensusTable({ rows, onSelect, kindFilter: controlledKind, onKindFilter }) {
  const [query, setQuery] = useState('')
  // ⚠⚠ DEFAULT SORT IS STILL ACCESSION. D-102 licenses a sort the READER chooses; it does not
  // license the page arriving already ordered. A default stained-% sort would be the ranking the
  // bar exists to prevent, delivered by a different route.
  const [sort, setSort] = useState({ key: 'accession', dir: 'asc' })
  const [showAll, setShowAll] = useState(false)
  const [lens, setLens] = useState('best_panel')
  const [excludeCritical, setExcludeCritical] = useState(false)
  // ⚠ D-133 am. 1: the fold-type filter, 'all' by default. A default of 'assembled' would be the
  // page arriving having chosen, which is the same bar the default SORT answers to (D-102).
  const [ownKind, setOwnKind] = useState('all')

  const lensed = useMemo(() => withLens(rows, lens), [rows, lens])

  // ⚠⚠ THE CHIPS ARE DERIVED FROM THE ROWS, not typed. Each chip carries its own count, and the
  // LABEL is the API's (`assembled (provisional)`, `tiles only`, …) so the filter cannot come to
  // spell a category differently from the column it filters. A kind absent from the data has no
  // chip: a control that can only empty the table is a broken control.
  // ⚠ D-135: the derivation moved to `../structureKinds.js` so the /coverage strip reads one rule.
  const kinds = useMemo(() => kindCounts(rows), [rows])

  // ⚠⚠ RESOLVED AGAINST THE ROWS, AND IT FALLS CLOSED (D-135). A controlled value arrives from the
  // URL, so it can be a typo or a stale bookmark; selecting it anyway would draw an EMPTY table
  // under a chip nobody pressed, which a reader cannot distinguish from "the census holds none of
  // these". Resolution needs the kinds actually present, which is why it happens HERE and not in
  // the caller — the caller does not have the rows yet when the URL is read.
  const kindFilter = resolveKind(controlledKind ?? ownKind, kinds)
  const chooseKind = (key) => {
    setOwnKind(key)
    onKindFilter?.(key)
  }

  const shown = useMemo(() => {
    const col = COLUMNS.find((c) => c.key === sort.key) ?? COLUMNS[0]
    // ⚠ the critical-tissue exclusion is an INDEPENDENT criterion on its own edge — a filter, never
    // a subtraction from the tumour figure. D-093 ruling 4: nothing divides.
    const base = excludeCritical ? lensed.filter((r) => r.critical_n === 0) : lensed
    // ⚠ D-133: the same shape — an independent criterion on its own edge. It narrows the list and
    // subtracts from no figure, and it is a CATEGORY filter, so it orders nothing.
    const kinded = kindFilter === 'all'
      ? base
      : base.filter((r) => (r.structure_kind ?? 'none') === kindFilter)
    // ⚠⚠ D-137: `kinded` is the LAST filter, and there is no cost filter after it. D-077 dec 1
    // refusal 3 bars narrowing the census by what we can afford to fold, so the cost axis
    // contributes to the SORT and to nothing else.
    return filterRows(kinded, query)
      .slice()
      .sort((a, b) => compare(a, b, col, sort.dir))
  }, [lensed, query, sort, excludeCritical, kindFilter])

  const declared = rows.find((r) => r.staining)?.staining
  // ⚠ counted, not assumed: the table holds two populations and each count states which
  const folded = rows.filter((r) => r.folded !== false).length
  const unfolded = rows.length - folded

  const toggle = (key) =>
    setSort((s) => ({ key, dir: s.key === key && s.dir === 'asc' ? 'desc' : 'asc' }))

  const intermittent = rows.filter((r) => r.topology === 'intermittent').length
  // ⚠ D-133: a count of census ACCESSIONS whose representative is an assembled parent. It is not
  // the 45 assembled parent JOBS of D-132 and must never be printed as that figure.
  const assembled = rows.filter((r) => r.structure_kind === 'assembled').length
  // ⚠ D-133 am. 1: the legend explains what the table SHOWS. A badge the rows never wear is not
  // explained — `always` marks the three categories that are properties of the census itself.
  const badgesPresent = new Set(rows.map(topologyBadgeKey))
  const topologyLegend = TOPOLOGY_LEGEND.filter((t) => t.always || (
    t.key === 'not_folded'
      ? badgesPresent.has('not_folded') || badgesPresent.has('not_folded_here')
      : badgesPresent.has(t.key)
  ))
  const structureLegend = STRUCTURE_LEGEND
    .map((s) => ({ ...s, chip: kinds.find((k) => k.key === s.kind) }))
    .filter((s) => s.chip)
  // ⚠⚠ D-137: THE COST LEGEND IS READ OFF THE ROWS, NOT TYPED HERE. `app/census_cost_read.py`
  // owns every term (`COST_LABEL`) and every meaning (`COST_MEANING`), so this page cannot come
  // to define `rental` differently from the module that assigns it — and `rental` in particular
  // MUST arrive carrying its closure, because a bare `rental` badge reads as a live queue
  // position and that copy is refused elsewhere in the tree.
  // ⚠ A category no row wears gets no entry — the same wall D-133 am. 1 built for topology: a
  // legend that explains absent categories is a wall the owner ruled against.
  const costLegend = useMemo(() => {
    const seen = new Map()
    for (const r of rows) {
      const key = costBadgeKey(r)
      if (key === 'not_served' || seen.has(key) || !r.cost_note) continue
      seen.set(key, { key, term: r.cost_label ?? r.cost, meaning: r.cost_note })
    }
    return [...COST_ORDER, 'span_unrecorded', 'unknown_verdict']
      .filter((k) => seen.has(k))
      .map((k) => seen.get(k))
  }, [rows])
  // ⚠⚠ THE AXIS STATEMENT AND THE CEILING RECIPE COME OFF THE WIRE TOO, and both are required
  // rather than decorative. The axis is D-077 dec 1 refusal 2's own words — a cost class sitting
  // beside a census of ADC targets is an invitation to read cheap as good unless the frame says
  // otherwise. The recipe carries the measured numbers, and a copy typed here would be a second
  // ceiling: the same span is affordable at int8 and not at fp16 (D-050 / D-077 dec 3).
  const costAxis = rows.find((r) => r.cost_axis)?.cost_axis
  const costRecipe = rows.find((r) => r.cost_recipe)?.cost_recipe
  const capped = !showAll && shown.length > PAGE
  const visible = capped ? shown.slice(0, PAGE) : shown

  return (
    <section className="census-table panel">
      <h3>Census — every folded protein</h3>
      <p className="census-scope">
        {/* ⚠⚠ THE COUNT AND ITS KEY. The table now holds BOTH populations, so "N folded proteins"
            over rows.length would be false the moment the never-folded rows joined. Each half
            states its own number. */}
        <strong>{folded.toLocaleString()}</strong> folded, plus{' '}
        <strong>{unfolded.toLocaleString()}</strong> listed but{' '}
        <strong>never folded</strong> — shown so a protein you can name is never simply missing.{' '}
        <strong>Not scored, not ranked, not ordered by suitability.</strong> These are structures
        and their measured properties; no judgement of target quality has been applied to any of
        them. Each protein&rsquo;s page carries a <strong>structural profile</strong> — a
        measurement derived from its structure, never a verdict. The <strong>Profile</strong> column
        below says only whether one could be computed, never what it was.{' '}
        <strong>A refusal is about range, not merit</strong>: it means the protein sits outside the
        span of values the model was fitted on, which is a fact about the model&rsquo;s reach and not
        about the protein.
      </p>

      <label className="census-search">
        <span className="sr-only">Search by accession, gene, protein name or alias</span>
        <input
          type="search"
          placeholder="Search accession, gene, protein name or alias (CD30, TROP2, PD-L1)…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </label>

      {/* ⚠⚠ THE FOLD-TYPE FILTER (D-133, required by the owner follow-up 2026-09-08). Chips rather
          than a hunt through 2,700 badges: one click gets the seam-spliced proteins on their own.
          ⚠ It is a CATEGORY filter — it narrows the list and orders nothing, and 'all' is the
          default because a page arriving pre-narrowed has chosen for the reader.
          ⚠ Each chip states its own count, and the labels come off the rows rather than being
          typed here, so the filter cannot spell a kind differently from the column it filters.
          ⚠⚠ AND THERE IS NO COST CHIP ROW BESIDE THIS ONE, ON PURPOSE (D-137 / D-077 dec 1
          refusal 3). Once fold type has chips, a `local` / `rental` / `over ceiling` chip set is
          the obvious next control — and it is exactly the one that is refused: a census that
          hides the rows it cannot afford to fold is a census of **our budget**, biased by span
          length, which is **feature 1** of the pre-registered six. Cost gets a sortable column
          and a legend; it never gets to remove a row. */}
      {kinds.length > 1 && (
        <div className="census-kind-filter" role="group" aria-label="Filter by fold type">
          <span className="kind-filter-legend">Fold type</span>
          <button
            type="button"
            className={`chip${kindFilter === 'all' ? ' chip-on' : ''}`}
            aria-pressed={kindFilter === 'all'}
            onClick={() => chooseKind('all')}
          >
            all {rows.length.toLocaleString()}
          </button>
          {kinds.map((k) => (
            <button
              key={k.key}
              type="button"
              className={`chip${kindFilter === k.key ? ' chip-on' : ''}`}
              aria-pressed={kindFilter === k.key}
              onClick={() => chooseKind(k.key)}
            >
              {k.label} {k.n.toLocaleString()}
            </button>
          ))}
          {/* ⚠⚠ THE CAVEAT ARRIVES WITH THE ACT. Narrowing to the assemblies must not read as
              promoting them, so the moment the reader is looking at nothing but assemblies the
              surface says what an assembly is. The legend below carries it unconditionally. */}
          {kindFilter === 'assembled' && (
            <p className="caveat">
              ⚠ These {assembled.toLocaleString()} {plural(assembled, 'protein')} are{' '}
              <strong>assembled from tiles</strong>: joined by pLDDT overlap, not superimposed. The
              seam is not solved, so &ldquo;assembled&rdquo; is provisional — it says how the
              structure was made, never how good it is.
            </p>
          )}
        </div>
      )}

      {/* ⚠⚠ THE LENS CONTROL. D-102's condition is "state what it is", and this is where it is
          stated. The control is not a preference — it changes what the Stained % column MEANS, so
          the meaning is printed under it rather than hidden in a tooltip. */}
      {/* ⚠ The publication, website reference and data credit for the whole staining column.
          The per-datum LINK is on each cell above; these three are properties of the source. */}
      <HpaAttribution attribution={declared?.attribution} view="pathology" />

      <div className="lens-control">
        <fieldset>
          <legend>How to read &ldquo;stained&rdquo;</legend>
          {Object.entries(LENSES).map(([key, l]) => (
            <label key={key} className="lens-option">
              <input
                type="radio"
                name="stain-lens"
                value={key}
                checked={lens === key}
                onChange={() => setLens(key)}
              />
              <span className="lens-name">{l.label}</span>
            </label>
          ))}
        </fieldset>
        <p className="lens-meaning">
          <strong>{LENSES[lens].label}:</strong> {LENSES[lens].meaning}.{' '}
          <span className="lens-caveat">⚠ {LENSES[lens].caveat}.</span>
        </p>
        {/* ⚠⚠ THE NUMBER THAT MAKES THIS CONTROL NECESSARY RATHER THAN DECORATIVE. */}
        <p className="lens-why">
          The same 1,727 proteins read very differently: <strong>728</strong> stain in 100% of
          patients under <em>best single cancer</em>, and <strong>16</strong> do under{' '}
          <em>all cancers pooled</em>. Neither is wrong — they answer different questions.
        </p>

        {declared && (
          <label className="lens-critical">
            <input
              type="checkbox"
              checked={excludeCritical}
              onChange={(e) => setExcludeCritical(e.target.checked)}
            />{' '}
            Hide proteins staining <strong>High</strong> in tissue you cannot afford to hit
            {/* ⚠⚠ THE LIST IS DECLARED, NOT IMPLIED. The owner ruled a named list is a lens and
                not a judgement — but only because it is STATED. A reader who cannot see the list
                cannot disagree with it, and a list nobody can disagree with is a verdict. */}
            <span className="lens-tissues">
              {' '}— {declared.critical_tissues_declared.join(', ')}
            </span>
            {declared.critical_tissues_unknown?.length > 0 && (
              <span className="caveat">
                {' '}⚠ named but absent from the source vocabulary:{' '}
                {declared.critical_tissues_unknown.join(', ')} — these exclude nothing
              </span>
            )}
            <span className="lens-basis">
              {' '}⚠ Normal tissue is {declared.normal_basis}; this is a flag, not a safety
              measurement.
            </span>
          </label>
        )}
      </div>

      {/* ⚠⚠ THE COUNT REPORTS WHAT IS ON SCREEN, not what matched. The first version printed
          `shown.length` while the table rendered `visible.length` — so the page read
          "Showing 2,641 of 2,641" above 200 rows. **A silent cap that claims completeness is
          worse than no cap at all**, and it is the precise failure the notice below exists to
          prevent — shipped anyway, because the edit that was meant to add the notice silently
          did not apply and nothing checked. */}
      <p className="census-count">
        Showing <strong>{visible.length.toLocaleString()}</strong> of{' '}
        {rows.length.toLocaleString()}
        {/* ⚠⚠ "no protein matches" READS AS "this protein does not exist", and for the census
            that is usually FALSE. HER2 and HER3 are in the manifest and were never folded — they
            are rental-tier, above the local ceiling — so the honest answer is "not folded", not
            "not found". A search that answers absence when the truth is unmeasured manufactures
            a gap, which is the defect D-101 was written about, one level along. */}
        {query && shown.length === 0 && (
          <>
            {' — nothing here matches that. '}
            <strong>Every protein in the manifest is listed</strong>, folded or not, so a name that
            returns nothing is genuinely outside this census rather than merely unfolded.
          </>
        )}
      </p>

      {capped && (
        <p className="caveat">
          ⚠ <strong>Capped for the browser&rsquo;s sake.</strong> {shown.length.toLocaleString()}{' '}
          rows match; the first <strong>{PAGE}</strong> are drawn. Search to narrow, or{' '}
          <button type="button" className="link" onClick={() => setShowAll(true)}>
            render all {shown.length.toLocaleString()}
          </button>{' '}
          — slow, but nothing is being withheld.
        </p>
      )}

      {intermittent > 0 && (
        <p className="caveat">
          ⚠ <strong>{intermittent.toLocaleString()}</strong> of these are marked{' '}
          <em>intermittent</em>: the folded span is the <strong>largest</strong> extracellular
          segment, not the whole extracellular region. Open a protein for its segment breakdown.
        </p>
      )}

      {/* ⚠⚠ THE LEGEND (D-133 am. 1), and it sits HERE — against the header row the words appear
          in, not in a glossary elsewhere on the site. Every one of these badges is a category with
          a cause, and until now the page printed the category and kept the cause in a tooltip.
          ⚠ Same spirit as the staining lens block above: state what a word means where it is read.
          ⚠ It lists only the badges these rows actually wear (plus the three standing topology
          categories), because a legend for absent categories is the wall it must not become. */}
      <div className="census-legend">
        {/* ⚠⚠ THE COST AXIS, IN THE SAME VISUAL FRAME AS THE COLUMN (D-137 / D-077 dec 1
            refusal 2). It leads the legend deliberately: `local` beside a census of ADC targets
            reads as *good* to anyone who has not been told otherwise, and being told in a tooltip
            is not being told. The recipe rides with it because a cost claim without its recipe is
            not checkable, and both strings are the API's rather than this file's. */}
        {(costAxis || costLegend.length > 0) && (
          <>
            <h4>What the Cost column says — and what it does not</h4>
            {costAxis && <p className="cost-axis">⚠ {costAxis}</p>}
            {costRecipe && (
              <p className="cost-recipe">
                <strong>Measured at:</strong> {costRecipe}
              </p>
            )}
            <dl className="legend-list">
              {costLegend.map((c) => (
                <div className="legend-row" key={c.key}>
                  {/* ⚠ the TERM is the API's, exactly as in the Structure block above */}
                  <dt>{c.term}</dt>
                  <dd>{c.meaning}</dd>
                </div>
              ))}
            </dl>
          </>
        )}
        {structureLegend.length > 0 && (
          <>
            <h4>What the Structure column says</h4>
            <dl className="legend-list">
              {structureLegend.map((s) => (
                <div className="legend-row" key={s.kind}>
                  {/* ⚠ the TERM is the API's own label wherever there is one — this block defines
                      the categories and never re-spells them. */}
                  <dt>{s.term ?? s.chip.label}</dt>
                  <dd>{s.meaning}</dd>
                </div>
              ))}
            </dl>
          </>
        )}
        <h4>What the Topology column says</h4>
        <dl className="legend-list">
          {topologyLegend.map((t) => (
            <div className="legend-row" key={t.key}>
              <dt>{t.term}</dt>
              <dd>{t.meaning}</dd>
            </div>
          ))}
        </dl>
      </div>

      <table>
        <thead>
          <tr>
            {COLUMNS.map((c) => (
              <th key={c.key}>
                <button
                  type="button"
                  onClick={() => toggle(c.key)}
                  aria-sort={sort.key === c.key ? (sort.dir === 'asc' ? 'ascending' : 'descending') : 'none'}
                >
                  {c.label}
                  {sort.key === c.key && <span aria-hidden="true">{sort.dir === 'asc' ? ' ▲' : ' ▼'}</span>}
                </button>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {visible.map((r) => {
            const band = bandFor(r.mean_plddt)
            // ⚠ D-133 am. 1: the SAME function the legend asks, so the badge a row wears and the
            // entry that explains it can never come from two different rules.
            const topo = topologyBadgeKey(r)
            // ⚠ D-137: same discipline, same reason.
            const costKey = costBadgeKey(r)
            return (
              <tr key={r.id ?? r.accession} className={r.folded === false ? 'row-unfolded' : undefined}>
                <td>
                  {/* ⚠ A real Link, not a button: each protein has its own page, so it must be
                      openable in a new tab, shareable, and reachable by the back button. An
                      onClick handler is none of those things.
                      ⚠⚠ A NEVER-FOLDED row links by ACCESSION — it has no analysis id, and the
                      route resolves accessions since it was fixed. Rendering it unlinked would
                      make a dead end of the one row a reader most wants to click. */}
                  <Link className="link" to={`/census/${r.accession ?? r.id}`}
                        onClick={() => onSelect?.(r)}>
                    {r.accession}
                  </Link>
                  {/* ⚠ D-133: the structure-kind badge MOVED to its own sortable column. It is not
                      also drawn here — two spellings of one fact, only one of them sortable, is
                      how a surface teaches a reader to distrust it. */}
                </td>
                <td>{r.gene ?? <span className="unknown">unknown</span>}</td>
                <td>{r.label ?? <span className="unknown">unknown</span>}</td>
                <td className="num">{r.span_aa ?? '—'}</td>
                <td>
                  {/* ⚠⚠ NOT FOLDED, said plainly and in a column the reader is already scanning.
                      The reason travels with it: "above the ceiling" and "never tested" are
                      different claims, and one row is neither — nothing records its reason at all,
                      which is a defect rather than a category. */}
                  {/* ⚠ The row carries the same three-way distinction as the card. A tooltip saying
                      "waiting on rented capacity" over a protein whose fold exists is the same
                      false claim, just smaller and harder to notice. */}
                  {topo === 'not_folded' || topo === 'not_folded_here' ? (
                    <span className="badge badge-unfolded" title={notFoldedTitle(r)}>
                      {topo === 'not_folded_here' ? 'NOT FOLDED HERE' : 'NOT FOLDED'}
                    </span>
                  ) : topo === 'intermittent' ? (
                    <span className="badge badge-intermittent" title={`${r.segment_count} extracellular segments; ${r.discarded_aa} aa not folded`}>
                      intermittent ({r.segment_count})
                    </span>
                  ) : topo === 'gpi' ? (
                    // ⚠⚠ THE TOOLTIP SPELLS THE ACRONYM (owner ruling 2026-09-08). It read
                    // "GPI-anchored: no topological domains by design" — four letters explaining
                    // four letters. It now carries the expansion, from the same constant the
                    // legend reads.
                    <span className="badge" title={GPI_MEANING}>
                      GPI / no segment
                    </span>
                  ) : topo === 'contiguous' ? (
                    <span className="badge badge-contiguous">contiguous</span>
                  ) : (
                    // ⚠ Anything else is NOT contiguous. The final branch used to swallow
                    // 'unknown' and every derivation verdict into the benign label — a default
                    // that asserts the safe case is how a surface states something nobody measured.
                    <span className="badge badge-unknown" title={r.derivation_note ?? undefined}>
                      {topo === 'not_derived' ? 'not derived' : 'derivation out of date'}
                    </span>
                  )}
                </td>

                {/* ⚠⚠ HOW THE FOLD WAS PRODUCED (D-133), in the column that sorts on it. The label
                    is the API's (`assembled (provisional)`, `single-pass`, `tiles only`,
                    `mucin — not folded`) so the surface never re-spells a category it is served,
                    and the assembler note rides in the tooltip.
                    ⚠⚠ AND A MISSING KIND IS SAID, NOT ASSUMED. Never-folded manifest rows carry
                    no kind (only the 3 mucins do), and a blank cell here would read as
                    "single-pass" — a fold that was never performed. It is a stated absence
                    instead, the same rule the topology column's final branch learned. */}
                <td className="kind-cell">
                  {r.structure_kind_label ? (
                    <span
                      className={`badge badge-kind badge-kind-${r.structure_kind || 'unknown'}`}
                      title={r.assembler_note || undefined}
                    >
                      {r.structure_kind_label}
                    </span>
                  ) : (
                    <span
                      className="unknown"
                      title="no structure kind on this row — a blank is a missing field, never an implied single-pass fold"
                    >
                      not recorded
                    </span>
                  )}
                </td>

                {/* ⚠⚠ WHAT THIS PROTEIN COSTS TO FOLD (D-137), in the column that sorts on it.
                    A COST class and never a verdict on the protein — the header says so, and the
                    legend above the table says so at length rather than in a tooltip.
                    ⚠⚠ `rental` NEVER TRAVELS BARE. The tooltip is the API's `cost_note`, which
                    carries the closure (rental for the hold-48 remainder closed 2026-09-05, pod
                    Terminated) — because a bare `rental` badge reads as a queue position, which
                    is the same false claim `core/census_unfolded.py` already refuses in words.
                    ⚠⚠ AND TWO ABSENCES STAY TWO. `not recorded` is a missing FIELD on the row;
                    `span not recorded` is the server saying it looked and found no span. Neither
                    is `local`: an unmeasured target counted as affordable is how a cost estimate
                    becomes a fiction (D-024). */}
                <td className="cost-cell">
                  {costKey === 'not_served' ? (
                    <span
                      className="unknown"
                      title="no cost verdict on this row — a blank is a missing field, never an implied local fold"
                    >
                      not recorded
                    </span>
                  ) : (
                    <span
                      className={`badge badge-cost badge-cost-${costKey}`}
                      title={r.cost_note || undefined}
                    >
                      {r.cost_label ?? r.cost}
                    </span>
                  )}
                </td>

                <td className="num" style={{ color: band.color }}>
                  {r.mean_plddt != null ? r.mean_plddt.toFixed(1) : <span className="unknown">not measured</span>}
                </td>
                <td className="num">{r.tranche}</td>
                {/* ⚠ The status is a word, never a number. `profile-refused` and `profile-computed`
                    are styled at the SAME weight: a refusal is an outcome (ruling 3), not a gap. */}
                <td>
                  {r.profile_status ? (
                    <span className={r.profile_status === 'computed'
                      ? 'profile-computed' : 'profile-refused'}>
                      {PROFILE_LABEL[r.profile_status] ?? r.profile_status}
                    </span>
                  ) : '—'}
                </td>

                {/* ⚠⚠ THE PERCENTAGE NEVER TRAVELS ALONE. D-102's condition, enforced in the cell:
                    the n rides with it, and under the best-panel lens so does the cancer it came
                    from. A bare "100%" over 4 patients and over 40 are different facts. */}
                <td className="num stained-cell">
                  {r.folded === false ? (
                    <span className="unknown">—</span>
                  ) : r.stained_pct == null ? (
                    <span className="unknown">
                      {r.stained_category === 'not_covered' ? 'not covered'
                        : r.stained_category === 'never_scored' ? 'never scored'
                        : 'no panel ≥ floor'}
                    </span>
                  ) : (
                    <>
                      {/* ⚠⚠ THE PER-DATUM LINK. This cell renders an HPA-derived value, so the
                          citation precondition attaches to the CELL, not to the page. */}
                      {r.staining?.attribution?.deep_link ? (
                        <a href={r.staining.attribution.deep_link} rel="noopener noreferrer"
                           target="_blank" className="stained-link">
                          <strong>{r.stained_pct}%</strong>
                        </a>
                      ) : (
                        <strong>{r.stained_pct}%</strong>
                      )}
                      <span className="stained-n"> of {r.stained_n}</span>
                      {r.stained_cancer && (
                        <span className="stained-where"> · {r.stained_cancer}</span>
                      )}
                    </>
                  )}
                </td>

                {/* ⚠ a COUNT of declared tissues hit, not a verdict. 0 is a real result. */}
                <td className="num">
                  {r.critical_n == null ? '—'
                    : r.critical_n === 0 ? <span className="crit-none">none</span>
                    : <span className="crit-hit">{r.critical_n}</span>}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </section>
  )
}
