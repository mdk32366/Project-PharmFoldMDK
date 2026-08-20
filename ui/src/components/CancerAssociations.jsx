import { useEffect, useState } from 'react'
import { getAssociations } from '../api.js'

// D-053: per-target cancer associations, from /api/associations (derived from the Kathad S3 grid).
// An EXPRESSION claim by the paper's measure — NOT causation, not a clinical indication (stated on
// screen, orders §2b). Ranked by quasi H-score descending (the supplier sorts; no truncation, dec 4).
// Deliberately NOT the pLDDT band palette (orders §2a): a different quantity from a different source
// must not read as model confidence, so it imports nothing from plddt.js and uses its own classes.
// Every count here derives from the payload; the paper's 290/16 are the only literals (dec 5).
import HpaAttribution from './HpaAttribution.jsx'

export default function CancerAssociations({ symbol }) {
  const [data, setData] = useState(null)
  const [failed, setFailed] = useState(false)
  useEffect(() => {
    getAssociations().then(setData).catch(() => setFailed(true))
  }, [])

  if (failed) return null
  if (!data) {
    return <section className="assoc"><p className="loading">Loading associations…</p></section>
  }

  const rows = data.associations[symbol] || []
  return (
    <section className="assoc">
      <h3>Cancer associations</h3>
      <p className="assoc-boundary">
        Highly expressed in these tumour types, <strong>by the paper's measure</strong> (quasi
        H-score above {data.cutoff}). This is an <strong>expression</strong> claim — <em>not</em>{' '}
        causation, not a claim the target drives the disease, and not a clinical indication.
      </p>
      {rows.length === 0 ? (
        <p className="assoc-absent">No association recorded for this target.</p>
      ) : (
        <ol className="assoc-list">
          {rows.map((a) => (
            <li key={a.cancer}>
              <span className="assoc-cancer">{a.cancer}</span>
              <span className="assoc-score">quasi H-score {a.qh_score}</span>
            </li>
          ))}
        </ol>
      )}
      <p className="assoc-provenance note">
        Derived from {data.source}. This is <em>our</em> derivation from the paper's published
        scores — {data.pair_count} pairs across {data.targets_covered} of {data.cohort_size} targets.
        It reproduces the paper's OSMR figure exactly, but the paper's text states 290 combinations
        and 16 targets in more than 7 tumour types — a filtering step the published files do not
        expose — so it is labelled our derivation, never "the paper's 290."
      </p>
      {/* ⚠⚠ D-100: Kathad's S3 is a VERBATIM EXTRACT of pathology.tsv, 1,640/1,640.
          Citing the paper is not citing HPA. D-053 predates the clinical layer, so this
          surface rendered HPA data unattributed longer than any other. */}
      <HpaAttribution attribution={data.attribution} view="pathology" />

    </section>
  )
}
