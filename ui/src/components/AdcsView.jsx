import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { listAdcs, listPipelineAdcs } from '../api.js'
import {
  APPROVED_SHELF,
  CANCER_TYPE_ABSENT_COPY,
  DEFAULT_SORT,
  INDEX_COLUMNS,
  PHASE_VOCAB,
  PIPELINE_INDEX_COLUMNS,
  PIPELINE_SHELF,
  filterPipelineByPhase,
  flattenCatalog,
  flattenPipeline,
  headerValue,
} from '../adcCatalog.js'
import { nextSort, sortRows } from '../sortRows.js'
import AdcAccessPanel from './AdcAccessPanel.jsx'
import Term from './Term.jsx'

// D-122 / ADC-B — sortable Approved index over the D-119 FDA-approved catalog.
// D-124 / ADC-C-B — Approved | Pipeline shelves on the same /adcs page.
// Default sort is name ascending: a reader-chosen order, not a ranking.
// Cancer type is the named v1 absence on Approved only (D-119 decision 8).
// Pipeline phase filter is the Architect closed vocab — nothing else.

function ApprovedShelf({ catalog }) {
  const [sort, setSort] = useState(DEFAULT_SORT)
  const rows = useMemo(() => flattenCatalog(catalog), [catalog])
  const ordered = useMemo(
    () => sortRows(rows, sort.key, sort.dir),
    [rows, sort],
  )

  const onSort = (key) => {
    const next = nextSort(sort, key)
    setSort(next ?? DEFAULT_SORT)
  }

  const n = rows.length
  const scope = headerValue(catalog, 'scope')
  const completeness = headerValue(catalog, 'completeness')
  const approvalsAsOf = headerValue(catalog, 'approvals_reconciled_as_of')
  const antigenAsOf = headerValue(catalog, 'antigen_mapping_reviewed_as_of')
  const exclusions = headerValue(catalog, 'named_exclusions')

  return (
    <div className="adcs-approved">
      <p className="lede">
        Currently marketed antibody–drug conjugates in the dated catalog this
        project consumes (D-119). Every cell that has a value also names its
        source, date, and confidence. This Approved shelf is not mixed with
        investigational rows — those live on the Pipeline shelf (D-124).
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

function PipelineShelf({ catalog }) {
  const [sort, setSort] = useState(DEFAULT_SORT)
  const [phase, setPhase] = useState('all')
  const rows = useMemo(() => flattenPipeline(catalog), [catalog])
  const filtered = useMemo(
    () => filterPipelineByPhase(rows, phase),
    [rows, phase],
  )
  const ordered = useMemo(
    () => sortRows(filtered, sort.key, sort.dir),
    [filtered, sort],
  )

  const onSort = (key) => {
    const next = nextSort(sort, key)
    setSort(next ?? DEFAULT_SORT)
  }

  const n = rows.length
  const shown = filtered.length
  const scope = headerValue(catalog, 'scope')
  const completeness = headerValue(catalog, 'completeness')
  const assembledAsOf = headerValue(catalog, 'catalog_assembled_as_of')
  const mappingAsOf = headerValue(catalog, 'mapping_sourced_as_of')

  return (
    <div className="adcs-pipeline">
      <p className="lede">
        Investigational antibody–drug conjugates in the dated pipeline
        catalog (D-124). Completeness is a floor, not a census. This
        shelf is not an approval list, not a trial listing, and not a
        treatment recommendation.
      </p>

      <p className="adcs-floor">
        <strong>{n} row{n === 1 ? '' : 's'} in this file</strong>
        {assembledAsOf ? ` — a pin of the catalog on ${assembledAsOf}` : ''}
        , not a scientific constant.
        {scope ? <> Scope: <code>{scope}</code>.</> : null}
        {completeness ? <> Completeness: <code>{completeness}</code>.</> : null}
        {mappingAsOf ? <> Mapping sourced as of {mappingAsOf}.</> : null}
      </p>

      <div className="list-controls">
        <label htmlFor="adc-phase-filter">Phase</label>
        <select
          id="adc-phase-filter"
          value={phase}
          onChange={(e) => setPhase(e.target.value)}
        >
          <option value="all">All phases</option>
          {PHASE_VOCAB.map((token) => (
            <option key={token} value={token}>{token}</option>
          ))}
        </select>
        {phase !== 'all' ? (
          <p className="note filter-count">
            Showing {shown} of {n}
            {shown === 0 ? (
              <> — no row in this file matches that phase. That is a filter
              result, not a claim that no such agents exist.</>
            ) : null}
          </p>
        ) : null}
      </div>

      {shown === 0 && phase === 'all' ? (
        <p className="absent-reason">
          This pipeline file has no rows. That is an absence in this
          file, not a census of the clinical ADC field.
        </p>
      ) : null}

      {shown > 0 ? (
        <table>
          <thead>
            <tr>
              {PIPELINE_INDEX_COLUMNS.map((col) => {
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
                  <Link to={`/adcs/pipeline/${r.id}`}>{r.name}</Link>
                  {r.stage ? <div className="adcs-inn">{r.stage}</div> : null}
                </td>
                <td>{r.phase}</td>
                <td>
                  <span>{r.protein}</span>
                  {r.accession ? <div className="mono adcs-acc">{r.accession}</div> : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}

      <AdcAccessPanel />
    </div>
  )
}

export default function AdcsView() {
  const [searchParams, setSearchParams] = useSearchParams()
  const shelf = searchParams.get('shelf') === PIPELINE_SHELF ? PIPELINE_SHELF : APPROVED_SHELF

  const [approved, setApproved] = useState(null)
  const [pipeline, setPipeline] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    const load = shelf === PIPELINE_SHELF ? listPipelineAdcs() : listAdcs()
    const set = shelf === PIPELINE_SHELF ? setPipeline : setApproved
    setError(null)
    load
      .then((data) => { if (!cancelled) set(data) })
      .catch((e) => { if (!cancelled) setError(e.message) })
    return () => { cancelled = true }
  }, [shelf])

  const setShelf = (next) => {
    if (next === PIPELINE_SHELF) {
      setSearchParams({ shelf: PIPELINE_SHELF })
    } else {
      setSearchParams({})
    }
  }

  const catalog = shelf === PIPELINE_SHELF ? pipeline : approved
  const loadingCopy = shelf === PIPELINE_SHELF
    ? 'Loading the investigational pipeline catalog…'
    : 'Loading the FDA-approved catalog…'

  return (
    <div className="adcs-index">
      <h2>
        <Term name="ADC">ADCs</Term>
      </h2>

      <div className="adcs-shelf" role="tablist" aria-label="ADC catalog shelf">
        <button
          type="button"
          role="tab"
          aria-selected={shelf === APPROVED_SHELF}
          className={shelf === APPROVED_SHELF ? 'adcs-shelf-tab active' : 'adcs-shelf-tab'}
          onClick={() => setShelf(APPROVED_SHELF)}
        >
          Approved
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={shelf === PIPELINE_SHELF}
          className={shelf === PIPELINE_SHELF ? 'adcs-shelf-tab active' : 'adcs-shelf-tab'}
          onClick={() => setShelf(PIPELINE_SHELF)}
        >
          Pipeline
        </button>
      </div>

      {error ? <p className="error">{error}</p> : null}
      {!error && !catalog ? <p className="loading">{loadingCopy}</p> : null}
      {!error && catalog && shelf === APPROVED_SHELF ? (
        <ApprovedShelf catalog={catalog} />
      ) : null}
      {!error && catalog && shelf === PIPELINE_SHELF ? (
        <PipelineShelf catalog={catalog} />
      ) : null}
    </div>
  )
}
