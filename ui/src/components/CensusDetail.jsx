import { bandFor } from '../plddt.js'

// One census protein. Four questions, in the order a reader asks them: what is it, what did we
// fold, how confident is the model, and what is it associated with.
//
// ⚠⚠ EVERY ABSENCE HERE IS A CATEGORY WITH A CAUSE. "No cancer associations" is never printed,
// because it is not what the data says — the association source covers the 82 cohort targets only,
// so for a census protein the honest statement is "outside the source", which is a different fact
// with a different remedy.

function Segments({ detail }) {
  const { topology, segment_count: n, extracellular_total_aa: total,
          discarded_aa: discarded, span_aa: span, segments } = detail

  if (topology === 'no_accepted_segment') {
    return (
      <div className="segments">
        <h4>Extracellular topology</h4>
        <p>
          <strong>No annotated extracellular segment.</strong> This protein is GPI-anchored — it has
          no topological domains <em>by design</em>, and its span comes from the anchor rule rather
          than from a topology annotation.
        </p>
        <p className="caveat">
          ⚠ This is a different molecular architecture, <strong>not</strong> missing data and{' '}
          <strong>not</strong> an intermittent surface.
        </p>
      </div>
    )
  }

  if (topology === 'unknown') {
    return (
      <div className="segments">
        <h4>Extracellular topology</h4>
        {/* ⚠ "not derived" is not "contiguous". A surface that defaulted to the benign case would
            state a topology nobody measured. */}
        <p className="caveat">⚠ Segment structure has not been derived for this protein — unknown, not absent.</p>
      </div>
    )
  }

  const contiguous = topology === 'contiguous'
  return (
    <div className="segments">
      <h4>Extracellular topology</h4>
      {contiguous ? (
        <p>
          <strong>Contiguous.</strong> One extracellular region of {total} aa, and it is what was
          folded. The structure models the whole extracellular portion.
        </p>
      ) : (
        <>
          <p className="caveat">
            ⚠⚠ <strong>Intermittent — {n} separate extracellular segments.</strong> This protein
            crosses the membrane more than once, so its extracellular portion is several stretches
            rather than one.
          </p>
          <p>
            Extracellular in total: <strong>{total} aa</strong>. Folded here:{' '}
            <strong>{span} aa</strong> — the <em>largest single segment</em>.{' '}
            <strong>{discarded} aa across the remaining {n - 1} segment
            {n - 1 === 1 ? '' : 's'} was not folded.</strong>
          </p>
          <p className="caveat">
            ⚠ An antibody can bind an epitope formed by several loops together. A structure of one
            loop in isolation is <strong>not</strong> a model of that site — read this structure as
            one segment, not as the ectodomain.
          </p>
        </>
      )}
      {segments && <p className="segment-list">Segments (residue ranges): {segments.split(';').join(', ')}</p>}
    </div>
  )
}

function Associations({ assoc }) {
  if (!assoc) return null
  if (assoc.status !== 'covered') {
    return (
      <div className="associations">
        <h4>Cancer associations</h4>
        {/* ⚠⚠ NOT "no associations found". We did not look at this protein. */}
        <p className="caveat">
          ⚠ <strong>Not covered by the association source</strong> — so this is{' '}
          <strong>unknown</strong>, not <em>none</em>. {assoc.coverage_note}.
        </p>
        <p className="source">Source: {assoc.source}</p>
      </div>
    )
  }
  if (assoc.hits.length === 0) {
    return (
      <div className="associations">
        <h4>Cancer associations</h4>
        <p>
          <strong>Covered by the source, and no cancer met the threshold.</strong> This one <em>is</em>{' '}
          a measured absence.
        </p>
        <p className="source">Source: {assoc.source}</p>
      </div>
    )
  }
  return (
    <div className="associations">
      <h4>Cancer associations</h4>
      <ul>
        {assoc.hits.map((h) => (
          <li key={h.cancer}>
            {h.cancer} <span className="num">({h.qh_score})</span>
          </li>
        ))}
      </ul>
      <p className="source">Source: {assoc.source}</p>
    </div>
  )
}

export default function CensusDetail({ detail, onClose }) {
  if (!detail) return null
  const band = bandFor(detail.mean_plddt)
  return (
    <section className="census-detail panel">
      <button type="button" className="close" onClick={onClose}>Close</button>
      <h3>
        {detail.gene ?? detail.accession}{' '}
        <span className="accession">{detail.accession}</span>
      </h3>
      <p className="protein-name">{detail.label ?? <span className="unknown">name unknown</span>}</p>

      <h4>Status</h4>
      <ul className="status-list">
        <li>Folded — tranche {detail.tranche}</li>
        <li>
          Span {detail.span_aa} aa (residues {detail.span_start}–{detail.span_end} of{' '}
          {detail.full_length})
        </li>
        <li>Span definition: <code>{detail.span_definition}</code></li>
        <li>
          Confidence:{' '}
          <strong style={{ color: band.color }}>
            {detail.mean_plddt != null ? detail.mean_plddt.toFixed(2) : 'not measured'}
          </strong>{' '}
          — {band.label}
        </li>
        {/* ⚠ Stated on the row, not left to the absence of a score field to imply. */}
        <li className="caveat">
          ⚠ <strong>Not scored and not ranked.</strong> {detail.not_scored_reason}
        </li>
      </ul>

      <Segments detail={detail} />
      <Associations assoc={detail.cancer_associations} />
    </section>
  )
}
