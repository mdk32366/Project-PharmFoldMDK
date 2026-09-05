import { isEnvelope } from '../adcCatalog.js'

// D-122 / D-124: one catalog envelope on screen. All four keys render.
// A bare string is not data — the caller must pass an envelope or this
// returns nothing. Optional `renderValue` is for URL / list values that
// still owe the same source / as_of / confidence line (Trinity C-B bar 5).

export default function ProvenanceField({ label, field, renderValue }) {
  if (!isEnvelope(field)) return null
  const shown = renderValue
    ? renderValue(field.value)
    : <span className="prov-value">{String(field.value)}</span>
  return (
    <div className="prov-field">
      <dt>{label}</dt>
      <dd>
        {shown}
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
