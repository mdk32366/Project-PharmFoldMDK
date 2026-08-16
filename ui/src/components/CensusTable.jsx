import { useMemo, useState } from 'react'
import { bandFor } from '../plddt.js'

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
]

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

export function filterRows(rows, query) {
  const q = query.trim().toLowerCase()
  if (!q) return rows
  return rows.filter((r) =>
    [r.accession, r.gene, r.label].some((v) => v && String(v).toLowerCase().includes(q)),
  )
}

// ⚠⚠ A CAP, AND IT IS STATED. The first version rendered all 2,629 rows: a 116,000px table body
// that no reader scrolls and every browser pays for. But a SILENT cap is worse than a slow page —
// it would show 200 rows above a count of 2,629 and let the reader assume they had seen the list.
// So the cap is announced, the full count stays visible, and there is a control to lift it.
const PAGE = 200

export default function CensusTable({ rows, onSelect }) {
  const [query, setQuery] = useState('')
  const [sort, setSort] = useState({ key: 'accession', dir: 'asc' })
  const [showAll, setShowAll] = useState(false)

  const shown = useMemo(() => {
    const col = COLUMNS.find((c) => c.key === sort.key) ?? COLUMNS[0]
    return filterRows(rows, query)
      .slice()
      .sort((a, b) => compare(a, b, col.key, col.numeric, sort.dir))
  }, [rows, query, sort])

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
        them.
      </p>

      <label className="census-search">
        <span className="sr-only">Search by accession, gene or protein name</span>
        <input
          type="search"
          placeholder="Search accession, gene or protein name…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </label>

      {/* ⚠⚠ THE COUNT REPORTS WHAT IS ON SCREEN, not what matched. The first version printed
          `shown.length` while the table rendered `visible.length` — so the page read
          "Showing 2,641 of 2,641" above 200 rows. **A silent cap that claims completeness is
          worse than no cap at all**, and it is the precise failure the notice below exists to
          prevent — shipped anyway, because the edit that was meant to add the notice silently
          did not apply and nothing checked. */}
      <p className="census-count">
        Showing <strong>{visible.length.toLocaleString()}</strong> of{' '}
        {rows.length.toLocaleString()}
        {query && shown.length === 0 && ' — no protein matches that search'}
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
                  <button type="button" className="link" onClick={() => onSelect?.(r)}>
                    {r.accession}
                  </button>
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
              </tr>
            )
          })}
        </tbody>
      </table>
    </section>
  )
}
