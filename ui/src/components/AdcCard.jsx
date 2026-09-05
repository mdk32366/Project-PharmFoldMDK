import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getAdc } from '../api.js'
import { CANCER_TYPE_ABSENT_COPY, fieldValue, isEnvelope } from '../adcCatalog.js'
import ProvenanceField from './ProvenanceField.jsx'
import Term from './Term.jsx'

// D-122 / ADC-B — baseball-card detail for one D-119 row.
// Brand is the title; every envelope shows value + source + as_of + confidence.
// Cancer type is the named v1 absence on the card as well as the index, so
// the two surfaces cannot disagree. Unknown id is not a guessed row.

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
          <div className="prov-field">
            <dt>Cancer type</dt>
            <dd>
              <span className="absent-reason">{CANCER_TYPE_ABSENT_COPY}</span>
            </dd>
          </div>
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
          Confidence tokens are official (Drugs@FDA field as returned),
          reviewed (human antigen / UniProt assignment), or derived (id / INN).
        </p>
      ) : null}
    </article>
  )
}
