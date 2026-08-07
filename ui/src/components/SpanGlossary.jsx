import {
  COMPARTMENT_PROVENANCE, GPI_BADGE, GPI_SPAN_RULE, RANK_LIMITATION, SPAN_CATEGORY_TOOLTIPS,
  SPAN_DEFINITION_NOTE, SPAN_TERMS,
} from '../spanGlossary.js'

// R4 — the span-vocabulary surface. Sourced from spanGlossary.js so it cannot drift from the terms
// the extractor actually rules on.
//
// ⚠ EVERY TERM RENDERS, INCLUDING THE REJECTED ONES. A term simply absent reads as "nobody thought
// of it"; a term listed as rejected with a reason reads as "considered, and here is why not." The
// rejected rows are the point of this component, not filler in it.
const ORDER = { accepted: 0, held: 1, unruled: 2, rejected: 3 }

const RULING_LABEL = {
  accepted: 'Accepted — counts as reachable',
  held: 'Held — being checked, and gains nothing meanwhile',
  rejected: 'Rejected — cannot reach the cell surface',
  unruled: 'Not ruled — shown rather than dropped',
}

export default function SpanGlossary() {
  const terms = [...SPAN_TERMS].sort(
    (a, b) => ORDER[a.ruling] - ORDER[b.ruling] || a.term.localeCompare(b.term),
  )
  return (
    <section className="span-glossary">
      <h3>Which parts of a protein count as reachable — and which do not</h3>

      <p className="note">
        A protein’s topology is described by UniProt with a small controlled vocabulary. The
        question behind every one of these decisions is a single one:{' '}
        <strong>can this face ever reach the outside of the cell?</strong> Not <em>is it usually
        there</em>, and <strong>not how many candidates it adds</strong>. Accepting a term places a
        protein in the population we can fold — the ranking still happens afterwards.
      </p>
      <p className="note">{SPAN_DEFINITION_NOTE}</p>

      <dl>
        {terms.map((t) => (
          <div className={`span-term span-term--${t.ruling}`} key={t.term}>
            <dt>
              <code>{t.term}</code>{' '}
              <span className={`span-ruling span-ruling--${t.ruling}`}>{RULING_LABEL[t.ruling]}</span>
            </dt>
            <dd>
              <p className="span-plain">{t.plain}</p>
              <p className="span-compartment"><strong>Where it is:</strong> {t.compartment}</p>
              <p className="span-reason"><strong>Why it is ruled this way:</strong> {t.reason}</p>
            </dd>
          </div>
        ))}
      </dl>

      <p className="note span-provenance">{COMPARTMENT_PROVENANCE}</p>

      <h4>When no span could be measured, the reason is named</h4>
      <dl>
        {Object.entries(SPAN_CATEGORY_TOOLTIPS).map(([key, text]) => (
          <div className="span-category" key={key}>
            <dt><code>{key}</code></dt>
            <dd title={text}>{text}</dd>
          </div>
        ))}
      </dl>

      <h4>How a GPI-anchored protein&rsquo;s extracellular region is measured</h4>
      <p>{GPI_SPAN_RULE.rule}</p>
      <p className="note">{GPI_SPAN_RULE.whenUnavailable}</p>
      <p className="note gpi-rule-withdrawn">{GPI_SPAN_RULE.withdrawn}</p>

      <h4>{GPI_BADGE.label}</h4>
      <p className="gpi-badge-explainer" title={GPI_BADGE.tooltip}>{GPI_BADGE.tooltip}</p>
      <p className="note rank-limitation">{RANK_LIMITATION}</p>
    </section>
  )
}
