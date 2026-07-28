import Term from './Term.jsx'

// D-069 dec 2 + D-068 dec 3 — the F-005 ambiguity, as ONE shared component. The same finding appears
// on the Scorer surface (caveat (b)) and on the target scorer panel; writing it twice is the prose-
// drift defect D-069 exists to prevent (two paths to one claim). This is the single source; each
// surface wraps its own framing around it. Layered per D-069 dec 3: the BODY carries the bounded
// claim (self-sufficient without interaction), a TOOLTIP carries the depth (how F-005 tested it).
// The claim boundary — "not supported" — lives in the tooltip and must not be trimmed.
export default function PlddtAmbiguityNote() {
  const id = 'f005-ambiguity-depth'
  return (
    <p className="ambiguity-note">
      These scores lean most on the model's own confidence (<Term name="pLDDT">pLDDT</Term>), not the
      shape features. That confidence might track real structural order — or just how much the protein
      has been studied; this analysis can't tell which.{' '}
      <span className="term">
        <button type="button" className="term-trigger" aria-describedby={id}>How F-005 tested this</button>
        <span role="tooltip" id={id} className="term-def">
          F-004's worry was that pLDDT proxies research attention through <Term name="ESMFold">ESMFold</Term>'s
          training-set representation. Tested (F-005): that attention mechanism is <b>not supported</b> —
          the pLDDT-only model aligns <i>less</i> with the evidence comparator, not more, the opposite of
          what it predicts. What stays open is whether pLDDT reflects attention or a genuine
          order-versus-disorder structural signal, which this design can't separate.
        </span>
      </span>
    </p>
  )
}
