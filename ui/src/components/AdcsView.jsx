import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { listAdcs } from '../api.js'
import {
  CANCER_TYPE_ABSENT_COPY,
  DEFAULT_SORT,
  INDEX_COLUMNS,
  flattenCatalog,
  headerValue,
} from '../adcCatalog.js'
import { nextSort, sortRows } from '../sortRows.js'
import Term from './Term.jsx'

// D-122 / ADC-B — sortable index over the D-119 FDA-approved catalog.
// Default sort is name ascending: a reader-chosen order, not a ranking.
// Cancer type is the named v1 absence (D-119 decision 8). Row count is
// derived from the payload — never typed as "N approved ADCs."

export default function AdcsView() {
  const [catalog, setCatalog] = useState(null)
  const [error, setError] = useState(null)
  const [sort, setSort] = useState(DEFAULT_SORT)

  useEffect(() => {
    let cancelled = false
    listAdcs()
      .then((data) => { if (!cancelled) setCatalog(data) })
      .catch((e) => { if (!cancelled) setError(e.message) })
    return () => { cancelled = true }
  }, [])

  const rows = useMemo(() => flattenCatalog(catalog), [catalog])
  const ordered = useMemo(
    () => sortRows(rows, sort.key, sort.dir),
    [rows, sort],
  )

  const onSort = (key) => {
    const next = nextSort(sort, key)
    setSort(next ?? DEFAULT_SORT)
  }

  if (error) return <p className="error">{error}</p>
  if (!catalog) return <p className="loading">Loading the FDA-approved catalog…</p>

  const n = rows.length
  const scope = headerValue(catalog, 'scope')
  const completeness = headerValue(catalog, 'completeness')
  const approvalsAsOf = headerValue(catalog, 'approvals_reconciled_as_of')
  const antigenAsOf = headerValue(catalog, 'antigen_mapping_reviewed_as_of')
  const exclusions = headerValue(catalog, 'named_exclusions')

  return (
    <div className="adcs-index">
      <h2>
        FDA-approved <Term name="ADC">ADCs</Term>
      </h2>
      <p className="lede">
        Currently marketed antibody–drug conjugates in the dated catalog this
        project consumes (D-119). Every cell that has a value also names its
        source, date, and confidence. This is <strong>not</strong> a pipeline
        or Right-to-Try list (ADC-C).
      </p>

      <p className="adcs-floor">
        <strong>{n} row{n === 1 ? '' : 's'} in this file</strong>
        {approvalsAsOf ? ` — a pin of the catalog on ${approvalsAsOf}` : ''}
        , not a scientific constant.
        {scope ? <> Scope: <code>{scope}</code>.</> : null}
        {completeness ? <> Completeness: <code>{completeness}</code>.</> : null}
        {approvalsAsOf ? <> Approvals reconciled as of {approvalsAsOf}.</> : null}
        {antigenAsOf ? <> Antigen mapping reviewed as of {antigenAsOf}.</> : null}
      </p>

      {Array.isArray(exclusions) && exclusions.length > 0 && (
        <section className="adcs-exclusions">
          <h3>Named exclusions (not rows)</h3>
          <ul>
            {exclusions.map((ex) => (
              <li key={ex.id}>
                <code>{ex.id}</code>
                {ex.reason ? ` — ${ex.reason}` : ''}
              </li>
            ))}
          </ul>
        </section>
      )}

      <table>
        <thead>
          <tr>
            {INDEX_COLUMNS.map((col) => {
              const active = sort.key === col.key
              const ariaSort = active ? (sort.dir === 'asc' ? 'ascending' : 'descending') : 'none'
              return (
                <th key={col.key} aria-sort={ariaSort}>
                  <button
                    type="button"
                    className="sort-header"
                    onClick={() => onSort(col.key)}
                  >
                    {col.label}
                    {active ? <span className="sort-caret"> {sort.dir === 'asc' ? '↑' : '↓'}</span> : null}
                  </button>
                </th>
              )
            })}
          </tr>
        </thead>
        <tbody>
          {ordered.map((r) => (
            <tr key={r.id}>
              <td>
                <Link to={`/adcs/${r.id}`}>{r.name}</Link>
                {r.inn ? <div className="adcs-inn">{r.inn}</div> : null}
              </td>
              <td className="absent-reason">{CANCER_TYPE_ABSENT_COPY}</td>
              <td>
                <span>{r.protein}</span>
                {r.accession ? <div className="mono adcs-acc">{r.accession}</div> : null}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
