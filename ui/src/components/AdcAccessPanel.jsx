import { useEffect, useState } from 'react'
import { getAdcAccess } from '../api.js'
import { fieldValue, isEnvelope, looksLikeUrl } from '../adcCatalog.js'
import ProvenanceField from './ProvenanceField.jsx'

// D-124 / ADC-C-B — Access / RTT panel. The only source is GET /api/adcs/access.
// Honest empty / missing / failed states. Does not invent NCT ids, eligibility,
// or a treatment recommendation.

const LINK_FIELDS = [
  ['ClinicalTrials.gov', 'clinical_trials_registry'],
  ['FDA expanded access', 'expanded_access_fda'],
  ['FDA Right to Try page', 'right_to_try_fda'],
]

const TEXT_FIELDS = [
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

function LinkOrMissing({ label, field }) {
  if (!isEnvelope(field)) return <MissingField label={label} />
  const value = field.value
  return (
    <div className="prov-field">
      <dt>{label}</dt>
      <dd>
        {looksLikeUrl(value) ? (
          <a href={value} rel="noreferrer">{value}</a>
        ) : (
          <span className="prov-value">{String(value)}</span>
        )}
        <span className="prov-meta">
          source: {field.source}
          {' · '}
          as of {field.as_of}
          {' · '}
          {field.confidence}
        </span>
      </dd>
    </div>
  )
}

function NctList({ field }) {
  if (!isEnvelope(field)) {
    return <MissingField label="Named NCT identifiers from the pipeline file" />
  }
  const ids = Array.isArray(field.value) ? field.value.filter(Boolean) : []
  return (
    <div className="prov-field">
      <dt>Named NCT identifiers from the pipeline file</dt>
      <dd>
        {ids.length === 0 ? (
          <span className="absent-reason">
            This payload names no NCT identifiers. That is an absence in
            this file, not a claim that no trials exist.
          </span>
        ) : (
          <ul className="adc-nct-list">
            {ids.map((id) => (
              <li key={id}>
                <code>{id}</code>
                {' — identifier already cited in the mapping, not an enrollment recommendation'}
              </li>
            ))}
          </ul>
        )}
        <span className="prov-meta">
          source: {field.source}
          {' · '}
          as of {field.as_of}
          {' · '}
          {field.confidence}
        </span>
      </dd>
    </div>
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

  const disclaimer = fieldValue(payload.disclaimer)
  const completeness = fieldValue(payload.completeness)
  const scope = fieldValue(payload.scope)
  const asOf = fieldValue(payload.as_of)

  return (
    <section className="adc-access-panel" aria-labelledby="adc-access-heading">
      <h3 id="adc-access-heading">Access and Right-to-Try (informational)</h3>
      {disclaimer ? (
        <p className="adc-access-disclaimer">{disclaimer}</p>
      ) : (
        <p className="absent-reason">
          Disclaimer is missing from this payload. This panel still does
          not determine eligibility or recommend a treatment.
        </p>
      )}
      <p className="adc-access-floor">
        {scope ? <>Scope: <code>{scope}</code>. </> : null}
        {completeness ? <>Completeness: <code>{completeness}</code>. </> : null}
        {asOf ? <>As of {asOf}.</> : null}
        {' '}A pin of this file, not a census of trials or Right-to-Try uses.
      </p>
      <dl className="baseball-stats">
        {LINK_FIELDS.map(([label, key]) => (
          <LinkOrMissing key={key} label={label} field={payload[key]} />
        ))}
        {TEXT_FIELDS.map(([label, key]) => (
          isEnvelope(payload[key])
            ? <ProvenanceField key={key} label={label} field={payload[key]} />
            : <MissingField key={key} label={label} />
        ))}
        <NctList field={payload.named_nct_ids_from_pipeline} />
      </dl>
    </section>
  )
}
