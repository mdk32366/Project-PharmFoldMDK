import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { bandFor } from '../plddt.js'
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

const COLUMNS = [
  { key: 'accession', label: 'Accession', numeric: false },
  { key: 'gene', label: 'Gene', numeric: false },
  { key: 'label', label: 'Protein', numeric: false },
  { key: 'span_aa', label: 'Span (aa)', numeric: true },
  { key: 'topology', label: 'Topology', numeric: false },
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

// ⚠ The four statuses, rendered as words rather than as a token. The three REFUSAL causes stay
// distinct — pooling 1,225 + 58 + 10 into one "n/a" would lose the reason, and an absence is a
// category with a cause.
const PROFILE_LABEL = {
  computed: 'computed',
  refused_out_of_distribution: 'outside fitted range',
  refused_span_below_floor: 'span too short to describe',
  refused_features_incomplete: 'measurements incomplete',
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

// ⚠ null sorts LAST in both directions. A missing pLDDT is not a low one, and letting it float to
// the top of an ascending sort would put unmeasured rows where the worst rows belong.
function compare(a, b, key, numeric, dir) {
  const av = a[key]
  const bv = b[key]
  if (av == null && bv == null) return 0
  if (av == null) return 1
  if (bv == null) return -1
  const c = numeric ? av - bv : String(av).localeCompare(String(bv))
  return dir === 'asc' ? c : -c
}

// ⚠⚠ PUNCTUATION IS NOT DECORATION IN THIS DOMAIN. UniProt stores `PDL1`, `NECTIN4`, `HER2`;
// people type `PD-L1`, `NECTIN-4`, `HER-2`. Comparing raw strings answers "no protein matches that
// search" for a protein we hold, which is the worst answer a search can give — it reads as absence.
export function normalizeQuery(text) {
  return String(text ?? '').toUpperCase().replace(/[^A-Z0-9]+/g, '')
}

// ⚠⚠ AND THE NAME PEOPLE KNOW IS OFTEN NOT THE NAME WE STORE. The census is keyed on HGNC symbols;
// the ADC field speaks in CD numbers and receptor families. `CD30` is here as `TNFRSF8` and `HER2`
// is a target as `ERBB2` — both read as MISSING to anyone who searches the name on the label of the
// drug. Aliases come from the pinned UniProt cache (`core/protein_aliases.py`), never typed.
// ⚠ An alias is a way IN, not a second identity: matching one does not rename the row.
export function filterRows(rows, query) {
  const raw = query.trim().toLowerCase()
  if (!raw) return rows
  const q = normalizeQuery(query)
  return rows.filter((r) => {
    // the original substring behaviour is preserved for names with spaces and punctuation
    if ([r.accession, r.gene, r.label].some((v) => v && String(v).toLowerCase().includes(raw))) {
      return true
    }
    if (!q) return false
    return [r.accession, r.gene, r.label, ...(r.aliases ?? [])].some(
      (v) => v && normalizeQuery(v).includes(q),
    )
  })
}

// ⚠⚠ A CAP, AND IT IS STATED. The first version rendered all 2,629 rows: a 116,000px table body
// that no reader scrolls and every browser pays for. But a SILENT cap is worse than a slow page —
// it would show 200 rows above a count of 2,629 and let the reader assume they had seen the list.
// So the cap is announced, the full count stays visible, and there is a control to lift it.
const PAGE = 200

export default function CensusTable({ rows, onSelect }) {
  const [query, setQuery] = useState('')
  // ⚠⚠ DEFAULT SORT IS STILL ACCESSION. D-102 licenses a sort the READER chooses; it does not
  // license the page arriving already ordered. A default stained-% sort would be the ranking the
  // bar exists to prevent, delivered by a different route.
  const [sort, setSort] = useState({ key: 'accession', dir: 'asc' })
  const [showAll, setShowAll] = useState(false)
  const [lens, setLens] = useState('best_panel')
  const [excludeCritical, setExcludeCritical] = useState(false)

  const lensed = useMemo(() => withLens(rows, lens), [rows, lens])

  const shown = useMemo(() => {
    const col = COLUMNS.find((c) => c.key === sort.key) ?? COLUMNS[0]
    // ⚠ the critical-tissue exclusion is an INDEPENDENT criterion on its own edge — a filter, never
    // a subtraction from the tumour figure. D-093 ruling 4: nothing divides.
    const base = excludeCritical ? lensed.filter((r) => r.critical_n === 0) : lensed
    return filterRows(base, query)
      .slice()
      .sort((a, b) => compare(a, b, col.key, col.numeric, sort.dir))
  }, [lensed, query, sort, excludeCritical])

  const declared = rows.find((r) => r.staining)?.staining

  const toggle = (key) =>
    setSort((s) => ({ key, dir: s.key === key && s.dir === 'asc' ? 'desc' : 'asc' }))

  const intermittent = rows.filter((r) => r.topology === 'intermittent').length
  const capped = !showAll && shown.length > PAGE
  const visible = capped ? shown.slice(0, PAGE) : shown

  return (
    <section className="census-table panel">
      <h3>Census — every folded protein</h3>
      <p className="census-scope">
        <strong>{rows.length.toLocaleString()}</strong> folded proteins.{' '}
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
            {' — nothing in the FOLDED census matches that. '}
            <strong>That is not the same as &ldquo;no such protein&rdquo;:</strong> 3,467 proteins
            have a usable extracellular stretch and only 2,690 were folded. The rest sit above the
            local GPU ceiling and are awaiting rented capacity — <strong>HER2, HER3, EGFR and
            HER4 are all in that group</strong>, at 621–630 aa.
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
            return (
              <tr key={r.id}>
                <td>
                  {/* ⚠ A real Link, not a button: each protein has its own page, so it must be
                      openable in a new tab, shareable, and reachable by the back button. An
                      onClick handler is none of those things. */}
                  <Link className="link" to={`/census/${r.id}`} onClick={() => onSelect?.(r)}>
                    {r.accession}
                  </Link>
                </td>
                <td>{r.gene ?? <span className="unknown">unknown</span>}</td>
                <td>{r.label ?? <span className="unknown">unknown</span>}</td>
                <td className="num">{r.span_aa ?? '—'}</td>
                <td>
                  {r.topology === 'intermittent' ? (
                    <span className="badge badge-intermittent" title={`${r.segment_count} extracellular segments; ${r.discarded_aa} aa not folded`}>
                      intermittent ({r.segment_count})
                    </span>
                  ) : r.topology === 'no_accepted_segment' ? (
                    <span className="badge" title="GPI-anchored: no topological domains by design">
                      GPI / no segment
                    </span>
                  ) : r.topology === 'contiguous' ? (
                    <span className="badge badge-contiguous">contiguous</span>
                  ) : (
                    // ⚠ Anything else is NOT contiguous. The final branch used to swallow
                    // 'unknown' and every derivation verdict into the benign label — a default
                    // that asserts the safe case is how a surface states something nobody measured.
                    <span className="badge badge-unknown" title={r.derivation_note ?? undefined}>
                      {r.topology === 'unknown' ? 'not derived' : 'derivation out of date'}
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
                  {r.stained_pct == null ? (
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
