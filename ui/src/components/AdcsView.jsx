import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { listAdcs, listPipelineAdcs } from '../api.js'
import {
  APPROVED_SHELF,
  DEFAULT_SORT,
  INDEX_COLUMNS,
  PHASE_VOCAB,
  PIPELINE_CANCER_TYPE_ABSENT_COPY,
  PIPELINE_DESCRIPTION_ABSENT_COPY,
  PIPELINE_INDEX_COLUMNS,
  PIPELINE_SHELF,
  absenceCopy,
  cancerTypeAbsenceCopy,
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
// D-136 — Cancer type on Approved lists the tumour types FDA's own label states,
// audited in the catalog loader against that row's stored label text. A row that
// states none renders its own absence source.
// D-140 — Pipeline gets Cancer type and Description of its own, from the trial
// registry / the row's citation and never from an FDA label. ⚠ Same column name
// on the two shelves, different authority behind it, so each shelf states which
// one it is rather than letting the reader assume a pipeline row is approved.
// Pipeline phase filter is the Architect closed vocab — nothing else.

// ⚠⚠ D-152 — THE SHELF SEARCH, AND WHY IT IS NOT `../searchRows.js`. The shared protein matcher
// reads `accession`, `gene`, `label`, `description` and `aliases`; an ADC row's identity is its
// DRUG NAME (`name`) and its `inn`, neither of which that matcher looks at, and its `gene` field
// does not exist. Pointing the shared function at these rows would have matched on `accession` and
// `description` only — a search box that silently cannot find `Enhertu` is worse than none, because
// a miss then reads as *this drug is not in the catalog*.
// ⚠ So this matcher names the four fields an ADC row actually carries, and it stays here rather
// than being bolted onto the protein matcher as a fifth optional key: two populations, two
// identities, one behaviour each.
function matchesAdc(row, query) {
  const q = query.trim().toLowerCase()
  if (!q) return true
  return [row.name, row.inn, row.protein, row.accession, row.stage, row.phase, row.description]
    .concat(row.cancer_types ?? [])
    .some((v) => v && String(v).toLowerCase().includes(q))
}

function ApprovedShelf({ catalog }) {
  const [sort, setSort] = useState(DEFAULT_SORT)
  const [query, setQuery] = useState('')
  const rows = useMemo(() => flattenCatalog(catalog), [catalog])
  const ordered = useMemo(
    () => sortRows(rows, sort.key, sort.dir),
    [rows, sort],
  )
  const shown = useMemo(() => ordered.filter((r) => matchesAdc(r, query)), [ordered, query])

  const onSort = (key) => {
    const next = nextSort(sort, key)
    setSort(next ?? DEFAULT_SORT)
  }

  const n = rows.length
  const scope = headerValue(catalog, 'scope')
  const completeness = headerValue(catalog, 'completeness')
  const approvalsAsOf = headerValue(catalog, 'approvals_reconciled_as_of')
  const antigenAsOf = headerValue(catalog, 'antigen_mapping_reviewed_as_of')
  const indicationsAsOf = headerValue(catalog, 'indications_reviewed_as_of')
  const exclusions = headerValue(catalog, 'named_exclusions')

  return (
    <div className="adcs-approved">
      {/* ⚠⚠ D-152 — THE FLOOR CLAIM STAYS ABOVE THE TABLE AND DOES NOT COLLAPSE. It is this
          shelf's standing claim — *this is a dated pin of a file, not a census of the field* — and
          it is the one sentence that stops a reader counting these rows as *the* approved ADCs.
          The census's unscored bar occupies the same slot for the same reason (D-151 dec 4).
          ⚠ What moved into the disclosure below is the SOURCING METADATA that used to trail it on
          the same line: scope, completeness and the four as-of dates. Every one of them is still
          rendered, in full, one click away — they are provenance for the file rather than a claim
          about what the reader is looking at. */}
      <p className="adcs-floor">
        <strong>{n} row{n === 1 ? '' : 's'} in this file</strong>
        {approvalsAsOf ? ` — a pin of the catalog on ${approvalsAsOf}` : ''}
        , not a scientific constant.
      </p>

      {/* ⚠⚠ D-152 — SEARCH FIRST, THEN THE TABLE. Owner, 2026-09-09: *"Apply what was done for
          Census to the rest of the surfaces."* This shelf had a sortable table and no way to find a
          row in it; on the Pipeline shelf the phase `<select>` was the only control, so the only
          way to answer *is Enhertu here* was to read the list. */}
      <div className="list-controls">
        <label htmlFor="adc-approved-search">Search</label>
        <input
          id="adc-approved-search"
          type="search"
          className="row-search"
          value={query}
          placeholder="drug, INN, antigen, accession or tumour type"
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      {shown.length !== n && (
        <p className="note filter-count">
          Showing {shown.length} of {n} rows matching &ldquo;{query.trim()}&rdquo;
          {shown.length === 0 && <> — nothing in this file matches. <strong>That is a fact about
            this dated file, not about the field</strong>: the catalog is a floor, and the named
            exclusions below say which known agents were deliberately left out and why.</>}
        </p>
      )}

      {/* ⚠⚠ D-152 — THE LONG-FORM BLOCKS, COLLAPSED AND NOT CUT, DIRECTLY ABOVE THE TABLE THEY
          QUALIFY. The lede, the file's provenance, the D-136 Cancer-type sourcing note and the
          named-exclusions list are ~1,400 characters that stood between the shelf tabs and the
          first row. All four are inside this `<details>`, in the DOM, findable by the browser's own
          page search, and read unchanged by every assertion in `AdcsView.test.jsx`.
          ⚠ THE NAMED EXCLUSIONS ARE THE ONE THAT NEEDED THINKING ABOUT, because an exclusion list
          is an honesty block: it is what stops a reader treating fifteen rows as the whole field.
          It stays because the FLOOR CLAIM above it is uncollapsed and points at it — the claim a
          reader must meet is *this file is a floor*, and the list is the evidence for that claim,
          one click from it. A claim behind a summary would have been the wrong half to hide.
          ⚠ Not `open`: an `open` default restores the scroll it was collapsed to end. */}
      <details className="surface-notes adcs-notes">
        <summary>
          What this shelf is, where its dates come from, and which known agents are deliberately
          not rows
        </summary>

      <p className="lede">
        Currently marketed antibody–drug conjugates in the dated catalog this
        project consumes (D-119). Every cell that has a value also names its
        source, date, and confidence. This Approved shelf is not mixed with
        investigational rows — those live on the Pipeline shelf (D-124).
      </p>

      <p className="adcs-provenance">
        {scope ? <>Scope: <code>{scope}</code>. </> : null}
        {completeness ? <>Completeness: <code>{completeness}</code>. </> : null}
        {approvalsAsOf ? <>Approvals reconciled as of {approvalsAsOf}. </> : null}
        {antigenAsOf ? <>Antigen mapping reviewed as of {antigenAsOf}. </> : null}
        {indicationsAsOf ? <>Label indications reviewed as of {indicationsAsOf}.</> : null}
      </p>

      {indicationsAsOf ? (
        <p className="note">
          Cancer type is the tumour type named in FDA's own section 1 INDICATIONS
          AND USAGE text for the label in force on {indicationsAsOf} — not the
          original approval's indication, and never a tissue-staining survey
          (D-136). Stage, line of therapy and biomarker qualifiers are not
          dropped; they stay in the label text on each ADC's card.
        </p>
      ) : null}

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
      </details>

      {/* ⚠ D-152: the bounded port, so the antigen and accession columns cannot push the document
          sideways, and the `<thead>` has a scrollport to stick to. */}
      <div className="table-scroll">
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
          {shown.map((r) => (
            <tr key={r.id}>
              <td>
                <Link to={`/adcs/${r.id}`}>{r.name}</Link>
                {r.inn ? <div className="adcs-inn">{r.inn}</div> : null}
              </td>
              <td>
                {r.cancer_types.length > 0 ? (
                  <ul className="adcs-cancer-types">
                    {r.cancer_types.map((t) => <li key={t}>{t}</li>)}
                  </ul>
                ) : (
                  <span className="absent-reason">
                    {cancerTypeAbsenceCopy(r.cancer_type_field)}
                  </span>
                )}
              </td>
              <td>
                <span>{r.protein}</span>
                {r.accession ? <div className="mono adcs-acc">{r.accession}</div> : null}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>
    </div>
  )
}

/**
 * D-140 — a named absence in a TABLE CELL, which is not the same problem as a
 * named absence on a card.
 *
 * ⚠ The first render of this shelf put each absence envelope's whole source —
 * ~300 characters naming the query and what it returned — straight into the
 * `<td>`. Five of ten rows are absent on cancer type and six on description, so
 * the table became two columns of paragraphs with the sourced rows lost between
 * them. That is **D-135's defect exactly** (`coverageNote()` returned 209
 * characters of prose into a `<td>`, "correct, and unreadable"), and it is fixed
 * the way D-135 fixed it: short in the cell, the full text one step away.
 *
 * ⚠ What is NOT done here: replacing the row's own source with a page-wide
 * sentence. D-136 decision 6 exists because one sentence that covers every
 * absent row cannot be wrong and therefore says nothing. The summary is a
 * LABEL for the disclosure; the row's own words are inside it, in the DOM,
 * unabridged — and on the baseball card they are not collapsed at all.
 */
function AbsenceCell({ field, fallback, summary }) {
  return (
    <details className="absent-why">
      <summary className="absent-reason">{summary}</summary>
      <p className="absent-reason absent-why-body">{absenceCopy(field, fallback)}</p>
    </details>
  )
}

function PipelineShelf({ catalog }) {
  const [sort, setSort] = useState(DEFAULT_SORT)
  const [phase, setPhase] = useState('all')
  const [query, setQuery] = useState('')
  const rows = useMemo(() => flattenPipeline(catalog), [catalog])
  const filtered = useMemo(
    () => filterPipelineByPhase(rows, phase).filter((r) => matchesAdc(r, query)),
    [rows, phase, query],
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
  const conditionsAsOf = headerValue(catalog, 'conditions_reviewed_as_of')

  return (
    <div className="adcs-pipeline">
      {/* ⚠ D-152 — same split as the Approved shelf: the floor claim stays, the sourcing dates move
          into the disclosure below. */}
      <p className="adcs-floor">
        <strong>{n} row{n === 1 ? '' : 's'} in this file</strong>
        {assembledAsOf ? ` — a pin of the catalog on ${assembledAsOf}` : ''}
        , not a scientific constant.
      </p>

      <div className="list-controls">
        <label htmlFor="adc-pipeline-search">Search</label>
        <input
          id="adc-pipeline-search"
          type="search"
          className="row-search"
          value={query}
          placeholder="drug, sponsor, antigen, accession or tumour type"
          onChange={(e) => setQuery(e.target.value)}
        />
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
      </div>
      {/* ⚠⚠ THE COUNT MOVED OUT OF `.list-controls` AND ITS CONDITION WIDENED (D-152). It used to
          render only when a PHASE was chosen, so the new search box could narrow ten rows to one
          under an unqualified header with nothing saying so. It now appears whenever the view is
          narrowed by either control — the rule the other four surfaces follow.
          ⚠ A `<p>` inside a flex row of controls was also laying out as a fourth control; it is a
          statement about the table and now sits with it. */}
      {shown !== n ? (
        <p className="note filter-count">
          Showing {shown} of {n}
          {phase !== 'all' ? <> in {phase}</> : null}
          {query.trim() ? <> matching &ldquo;{query.trim()}&rdquo;</> : null}
          {/* ⚠ THE SENTENCE NAMES WHICH CONTROL EMPTIED THE TABLE. "No row matches" over two live
              filters leaves the reader to guess which one did it, and the phase wording is the one
              `AdcsView.test.jsx` pins — so it is preserved exactly and the search clause is added
              beside it rather than replacing it. */}
          {shown === 0 ? (
            <>
              {' '}— no row in this file matches
              {phase !== 'all' ? ' that phase' : ''}
              {query.trim() ? `${phase !== 'all' ? ' and' : ''} that search` : ''}
              . That is a filter result, not a claim that no such agents exist.
            </>
          ) : null}
        </p>
      ) : null}

      {/* ⚠ D-152: the same disclosure as the Approved shelf, carrying the same kinds of block — the
          lede, the file's provenance dates and the D-140 sourcing note. Nothing is deleted and
          nothing that makes a CLAIM about the rows is inside it. */}
      <details className="surface-notes adcs-notes">
        <summary>
          What this shelf is, where its dates come from, and what &ldquo;Cancer type&rdquo; means on
          an investigational row
        </summary>

      <p className="lede">
        Investigational antibody–drug conjugates in the dated pipeline
        catalog (D-124). Completeness is a floor, not a census. This
        shelf is not an approval list, not a trial listing, and not a
        treatment recommendation.
      </p>

      <p className="adcs-provenance">
        {scope ? <>Scope: <code>{scope}</code>. </> : null}
        {completeness ? <>Completeness: <code>{completeness}</code>. </> : null}
        {mappingAsOf ? <>Mapping sourced as of {mappingAsOf}. </> : null}
        {conditionsAsOf ? <>Programme fields reviewed as of {conditionsAsOf}.</> : null}
      </p>

      {conditionsAsOf ? (
        <p className="note">
          Cancer type here is what the trial registry records this investigational
          agent as being <em>studied in</em> on {conditionsAsOf}, or what this row's
          own citation states — <strong>not</strong> an FDA indication, because none
          of these agents has one. Description names the sponsor or maker behind the
          programme. Where a row states neither, it says which lookup came back
          empty rather than showing a blank (D-140).
        </p>
      ) : null}
      </details>

      {shown === 0 && phase === 'all' && !query.trim() ? (
        <p className="absent-reason">
          This pipeline file has no rows. That is an absence in this
          file, not a census of the clinical ADC field.
        </p>
      ) : null}

      {shown > 0 ? (
        <div className="table-scroll">
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
                <td>
                  {r.cancer_types.length > 0 ? (
                    <ul className="adcs-cancer-types">
                      {r.cancer_types.map((t) => <li key={t}>{t}</li>)}
                    </ul>
                  ) : (
                    <AbsenceCell
                      field={r.cancer_type_field}
                      fallback={PIPELINE_CANCER_TYPE_ABSENT_COPY}
                      summary="none stated — why"
                    />
                  )}
                </td>
                <td>{r.phase}</td>
                <td>
                  <span>{r.protein}</span>
                  {r.accession ? <div className="mono adcs-acc">{r.accession}</div> : null}
                </td>
                <td className="adcs-description">
                  {r.description ? (
                    <span>{r.description}</span>
                  ) : (
                    <AbsenceCell
                      field={r.description_field}
                      fallback={PIPELINE_DESCRIPTION_ABSENT_COPY}
                      summary="no maker named — why"
                    />
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        </div>
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
