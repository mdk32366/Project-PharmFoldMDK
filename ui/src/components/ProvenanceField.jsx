import { isEnvelope } from '../adcCatalog.js'

// D-122: one D-119 envelope on screen. All four keys render. A bare string
// is not data — the caller must pass an envelope or this returns nothing.

export default function ProvenanceField({ label, field }) {
  if (!isEnvelope(field)) return null
  return (
    <div className="prov-field">
      <dt>{label}</dt>
      <dd>
        <span className="prov-value">{String(field.value)}</span>
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
