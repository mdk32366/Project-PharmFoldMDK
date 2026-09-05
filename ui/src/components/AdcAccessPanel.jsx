import { useEffect, useState } from 'react'
import { getAdcAccess } from '../api.js'
import { isEnvelope, looksLikeUrl } from '../adcCatalog.js'
import ProvenanceField from './ProvenanceField.jsx'

// D-124 / ADC-C-B — Access / RTT panel. The only source is GET /api/adcs/access.
// Sourced fields go through ProvenanceField (Trinity C-B bar 5). Honest empty /
// missing / failed states. Does not invent NCT ids, eligibility, or a treatment
// recommendation.

const ENVELOPE_FIELDS = [
  ['Disclaimer', 'disclaimer'],
  ['Scope', 'scope'],
  ['Completeness', 'completeness'],
  ['As of', 'as_of'],
  ['ClinicalTrials.gov', 'clinical_trials_registry'],
  ['FDA expanded access', 'expanded_access_fda'],
  ['FDA Right to Try page', 'right_to_try_fda'],
  ['Right-to-Try statute', 'right_to_try_statute'],
  ['Public law', 'right_to_try_public_law'],
]

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

function envelopeValue(value) {
  if (looksLikeUrl(value)) {
    return <a href={value} rel="noreferrer">{value}</a>
  }
  return <span className="prov-value">{String(value)}</span>
}

function nctValue(value) {
  const ids = Array.isArray(value) ? value.filter(Boolean) : []
  if (ids.length === 0) {
    return (
      <span className="absent-reason">
        This payload names no NCT identifiers. That is an absence in
        this file, not a claim that no trials exist.
      </span>
    )
  }
  return (
    <ul className="adc-nct-list">
      {ids.map((id) => (
        <li key={id}>
          <code>{id}</code>
          {' — identifier already cited in the mapping, not an enrollment recommendation'}
        </li>
      ))}
    </ul>
  )
}

export default function AdcAccessPanel() {
  const [payload, setPayload] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    getAdcAccess()
      .then((data) => { if (!cancelled) setPayload(data) })
      .catch((e) => { if (!cancelled) setError(e.message) })
    return () => { cancelled = true }
  }, [])

  if (error) {
    return (
      <section className="adc-access-panel" aria-labelledby="adc-access-heading">
        <h3 id="adc-access-heading">Access and Right-to-Try (informational)</h3>
        <p className="absent-reason">
          Access payload could not be loaded ({error}). This panel does
          not invent trial, expanded-access, or Right-to-Try claims.
        </p>
      </section>
    )
  }

  if (!payload) {
    return (
      <section className="adc-access-panel" aria-labelledby="adc-access-heading">
        <h3 id="adc-access-heading">Access and Right-to-Try (informational)</h3>
        <p className="loading">Loading the access payload…</p>
      </section>
    )
  }

  return (
    <section className="adc-access-panel" aria-labelledby="adc-access-heading">
      <h3 id="adc-access-heading">Access and Right-to-Try (informational)</h3>
      <p className="adc-access-floor">
        A pin of this file, not a census of trials or Right-to-Try uses.
        Not medical advice. Not legal advice. Not a treatment recommendation.
      </p>
      <dl className="baseball-stats">
        {ENVELOPE_FIELDS.map(([label, key]) => (
          isEnvelope(payload[key])
            ? (
              <ProvenanceField
                key={key}
                label={label}
                field={payload[key]}
                renderValue={envelopeValue}
              />
            )
            : <MissingField key={key} label={label} />
        ))}
        {isEnvelope(payload.named_nct_ids_from_pipeline) ? (
          <ProvenanceField
            label="Named NCT identifiers from the pipeline file"
            field={payload.named_nct_ids_from_pipeline}
            renderValue={nctValue}
          />
        ) : (
          <MissingField label="Named NCT identifiers from the pipeline file" />
        )}
      </dl>
    </section>
  )
}
