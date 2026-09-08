import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getPipelineAdc } from '../api.js'
import {
  PIPELINE_CANCER_TYPE_ABSENT_COPY,
  PIPELINE_DESCRIPTION_ABSENT_COPY,
  absenceCopy,
  fieldValue,
  isEnvelope,
} from '../adcCatalog.js'
import ProvenanceField from './ProvenanceField.jsx'
import AdcAccessPanel from './AdcAccessPanel.jsx'
import Term from './Term.jsx'

// D-124 / ADC-C-B — baseball-card detail for one pipeline row.
// Consumes GET /api/adcs/pipeline/{id}. Unknown id is not a guessed row.
// No DAR / efficacy fields — those are not in the A contract.
//
// D-140 — the card gains the same two envelopes the Pipeline index reads, so the
// two surfaces cannot disagree, plus the registry / citation text the tumour list
// was reduced from. ⚠ The section is "Programme", never "Indication": these agents
// are not approved and have no indication to state.

const IDENTITY = [
  ['Catalog id', 'id'],
  ['Development stage', 'development_stage'],
  ['Phase', 'phase'],
]
const TARGET = [
  ['Antigen', 'antigen'],
  ['UniProt accession', 'uniprot_accession'],
]

/**
 * D-140 — a field the payload does not carry at all. `ProvenanceField` renders
 * nothing for a non-envelope, which here would be a silent gap where a clinical
 * claim belongs. The loader requires all three programme fields, so reaching this
 * is a contract breach — and it says so rather than vanishing.
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

/** The reviewed tumour list, or this row's own absence source — never a blank. */
function cancerTypeValue(value, field) {
  const types = Array.isArray(value) ? value.filter((t) => typeof t === 'string' && t.trim()) : []
  if (types.length === 0) {
    return (
      <span className="absent-reason">
        {absenceCopy(field, PIPELINE_CANCER_TYPE_ABSENT_COPY)}
      </span>
    )
  }
  return (
    <ul className="adcs-cancer-types">
      {types.map((t) => <li key={t}>{t}</li>)}
    </ul>
  )
}

function descriptionValue(value, field) {
  if (typeof value !== 'string' || !value.trim()) {
    return (
      <span className="absent-reason">
        {absenceCopy(field, PIPELINE_DESCRIPTION_ABSENT_COPY)}
      </span>
    )
  }
  return <span className="prov-value">{value}</span>
}

/**
 * D-140 — the registry Conditions (or the citation quoted whole) that the tumour
 * list above was reduced from. This is what makes the reduction auditable by the
 * reader rather than taken on trust, so it is a peer field and not a tooltip.
 * Collapsed because it is long, not because it is secondary.
 */
function conditionsTextValue(value, field) {
  if (typeof value !== 'string' || !value.trim()) {
    return (
      <span className="absent-reason">
        {absenceCopy(field, PIPELINE_CANCER_TYPE_ABSENT_COPY)}
      </span>
    )
  }
  return (
    <details className="adc-label-indications">
      <summary>Read the text the cancer type was reduced from</summary>
      <blockquote className="label-verbatim">{value}</blockquote>
    </details>
  )
}

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

      {/* D-140 — a section of its own, not a line under Target. The antigen is a
          reviewed protein assignment; the cancer type is what a trial registry
          records this agent as being studied in. Rendering them as one block is
          how a target and a disease claim get confused (D-093). */}
      <section>
        <h3>Programme</h3>
        <dl className="baseball-stats">
          {isEnvelope(row.description) ? (
            <ProvenanceField
              label="Description"
              field={row.description}
              renderValue={(value) => descriptionValue(value, row.description)}
            />
          ) : (
            <MissingField label="Description" />
          )}
          {isEnvelope(row.cancer_type) ? (
            <ProvenanceField
              label="Cancer type (under study)"
              field={row.cancer_type}
              renderValue={(value) => cancerTypeValue(value, row.cancer_type)}
            />
          ) : (
            <MissingField label="Cancer type (under study)" />
          )}
          {isEnvelope(row.conditions_verbatim) ? (
            <ProvenanceField
              label="Trial registry conditions / citation text"
              field={row.conditions_verbatim}
              renderValue={(value) => conditionsTextValue(value, row.conditions_verbatim)}
            />
          ) : (
            <MissingField label="Trial registry conditions / citation text" />
          )}
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
          treatment recommendation. The cancer type is what the trial registry
          or this row's citation records the agent as being <em>studied in</em>
          {' '}— never an FDA indication, and every entry has to appear in the
          text quoted above it or the catalog refuses to load (D-140).
        </p>
      ) : null}

      <AdcAccessPanel />
    </article>
  )
}
