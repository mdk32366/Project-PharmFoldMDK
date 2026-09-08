import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getAdc } from '../api.js'
import { cancerTypeAbsenceCopy, fieldValue, isEnvelope } from '../adcCatalog.js'
import ProvenanceField from './ProvenanceField.jsx'
import Term from './Term.jsx'

// D-122 / ADC-B — baseball-card detail for one D-119 row.
// Brand is the title; every envelope shows value + source + as_of + confidence.
// D-136 — cancer type reads the same envelope the index reads, so the two
// surfaces cannot disagree, and the card adds the official label text the list
// was reduced from. Unknown id is not a guessed row.

const IDENTITY = [
  ['Active ingredient', 'active_ingredient'],
  ['INN', 'inn'],
  ['Catalog id', 'id'],
]
const TARGET = [
  ['Antigen', 'antigen'],
  ['UniProt accession', 'uniprot_accession'],
]
const APPROVAL = [
  ['Application', 'application_number'],
  ['Approval date (this application)', 'current_application_approval_date'],
  ['Marketing status', 'marketing_status'],
  ['Sponsor', 'sponsor'],
]

/**
 * D-136 — a field the payload does not carry at all. `ProvenanceField` renders
 * nothing for a non-envelope, which on this card would be a silent gap where a
 * clinical claim belongs. The catalog loader requires both indication fields,
 * so reaching this is a contract breach — and it says so rather than vanishing.
 */
function MissingField({ label }) {
  return (
    <div className="prov-field">
      <dt>{label}</dt>
      <dd>
        <span className="absent-reason">not in this payload</span>
      </dd>
    </div>
  )
}

/**
 * D-136 — the reviewed tumour-type list, or this row's own absence source.
 * The list is what the FDA label states; it is not a recommendation, and the
 * qualifiers it drops are recoverable from the label text directly below it.
 */
function cancerTypeValue(value, field) {
  const types = Array.isArray(value) ? value.filter((t) => typeof t === 'string' && t.trim()) : []
  if (types.length === 0) {
    return <span className="absent-reason">{cancerTypeAbsenceCopy(field)}</span>
  }
  return (
    <ul className="adcs-cancer-types">
      {types.map((t) => <li key={t}>{t}</li>)}
    </ul>
  )
}

/**
 * D-136 — FDA's own section 1 text, verbatim. This is what makes the reviewed
 * list above it auditable by the reader rather than taken on trust, so it is a
 * peer field on the card and not a tooltip. Collapsed because it is long, not
 * because it is secondary.
 */
function labelTextValue(value, field) {
  if (typeof value !== 'string' || !value.trim()) {
    return <span className="absent-reason">{cancerTypeAbsenceCopy(field)}</span>
  }
  return (
    <details className="adc-label-indications">
      <summary>Read the label text the cancer type was reduced from</summary>
      <blockquote className="label-verbatim">{value}</blockquote>
    </details>
  )
}

export default function AdcCard({ id }) {
  const [row, setRow] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setRow(null)
    setError(null)
    getAdc(id)
      .then((data) => { if (!cancelled) setRow(data) })
      .catch((e) => { if (!cancelled) setError(e.message) })
    return () => { cancelled = true }
  }, [id])

  if (error) {
    const unknown = /404/.test(error)
    return (
      <div className="adc-card">
        <p className="error">{unknown ? 'Unknown ADC' : error}</p>
        <p><Link to="/adcs">Back to the FDA-approved catalog</Link></p>
      </div>
    )
  }
  if (!row) return <p className="loading">Loading this ADC…</p>

  const brand = fieldValue(row.brand_name)
  const inn = fieldValue(row.inn)

  return (
    <article className="adc-card baseball-card">
      <p className="adc-card-nav">
        <Link to="/adcs">← FDA-approved catalog</Link>
      </p>
      <header className="baseball-head">
        <p className="baseball-kind">
          FDA-approved <Term name="ADC">ADC</Term>
        </p>
        <h2>{brand}</h2>
        {inn ? <p className="baseball-sub">{inn}</p> : null}
      </header>

      <section>
        <h3>Identity</h3>
        <dl className="baseball-stats">
          <ProvenanceField label="Brand" field={row.brand_name} />
          {IDENTITY.map(([label, key]) => (
            <ProvenanceField key={key} label={label} field={row[key]} />
          ))}
        </dl>
      </section>

      <section>
        <h3>Target</h3>
        <dl className="baseball-stats">
          {TARGET.map(([label, key]) => (
            <ProvenanceField key={key} label={label} field={row[key]} />
          ))}
        </dl>
      </section>

      {/* D-136 — a section of its own, not a line under Target. The antigen is a
          reviewed protein assignment; the cancer type is FDA's disease
          indication. Rendering them as one block is how staining and indication
          get confused (D-093), so the card keeps the seam visible. */}
      <section>
        <h3>Indication</h3>
        <dl className="baseball-stats">
          {isEnvelope(row.cancer_type) ? (
            <ProvenanceField
              label="Cancer type"
              field={row.cancer_type}
              renderValue={(value) => cancerTypeValue(value, row.cancer_type)}
            />
          ) : (
            <MissingField label="Cancer type" />
          )}
          {isEnvelope(row.label_indications_verbatim) ? (
            <ProvenanceField
              label="FDA label indications (section 1)"
              field={row.label_indications_verbatim}
              renderValue={(value) => labelTextValue(value, row.label_indications_verbatim)}
            />
          ) : (
            <MissingField label="FDA label indications (section 1)" />
          )}
        </dl>
      </section>

      <section>
        <h3>Approval</h3>
        <dl className="baseball-stats">
          {APPROVAL.map(([label, key]) => (
            <ProvenanceField key={key} label={label} field={row[key]} />
          ))}
        </dl>
      </section>

      {isEnvelope(row.brand_name) ? (
        <p className="note">
          Every number and name above is the catalog envelope for this row.
          Confidence tokens are official (a Drugs@FDA or FDA-label field as the
          endpoint returned it), reviewed (a human assignment — the antigen /
          UniProt join, and the reduction of the label text to a tumour type),
          or derived (id / INN). The cancer type is a reduction of the label
          text quoted above it, and every one of its entries has to appear in
          that text or the catalog refuses to load (D-136).
        </p>
      ) : null}
    </article>
  )
}
