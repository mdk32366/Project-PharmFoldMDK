import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getPipelineAdc } from '../api.js'
import { fieldValue, isEnvelope } from '../adcCatalog.js'
import ProvenanceField from './ProvenanceField.jsx'
import AdcAccessPanel from './AdcAccessPanel.jsx'
import Term from './Term.jsx'

// D-124 / ADC-C-B — baseball-card detail for one pipeline row.
// Consumes GET /api/adcs/pipeline/{id}. Unknown id is not a guessed row.
// No indication / DAR / efficacy fields — those are not in the A contract.

const IDENTITY = [
  ['Catalog id', 'id'],
  ['Development stage', 'development_stage'],
  ['Phase', 'phase'],
]
const TARGET = [
  ['Antigen', 'antigen'],
  ['UniProt accession', 'uniprot_accession'],
]

export default function AdcPipelineCard({ id }) {
  const [row, setRow] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setRow(null)
    setError(null)
    getPipelineAdc(id)
      .then((data) => { if (!cancelled) setRow(data) })
      .catch((e) => { if (!cancelled) setError(e.message) })
    return () => { cancelled = true }
  }, [id])

  if (error) {
    const unknown = /404/.test(error)
    return (
      <div className="adc-card">
        <p className="error">{unknown ? 'Unknown pipeline ADC' : error}</p>
        <p>
          <Link to="/adcs?shelf=pipeline">Back to the pipeline catalog</Link>
        </p>
      </div>
    )
  }
  if (!row) return <p className="loading">Loading this pipeline ADC…</p>

  const name = fieldValue(row.name)

  return (
    <article className="adc-card baseball-card">
      <p className="adc-card-nav">
        <Link to="/adcs?shelf=pipeline">← Pipeline catalog</Link>
      </p>
      <header className="baseball-head">
        <p className="baseball-kind">
          Investigational <Term name="ADC">ADC</Term>
        </p>
        <h2>{name}</h2>
      </header>

      <section>
        <h3>Identity</h3>
        <dl className="baseball-stats">
          <ProvenanceField label="Name" field={row.name} />
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

      <section>
        <h3>Source</h3>
        <dl className="baseball-stats">
          <ProvenanceField label="Citation" field={row.source_citation} />
        </dl>
      </section>

      {isEnvelope(row.name) ? (
        <p className="note">
          Every name above is the pipeline envelope for this row (D-124).
          This card is not an approval, not a trial listing, and not a
          treatment recommendation.
        </p>
      ) : null}

      <AdcAccessPanel />
    </article>
  )
}
