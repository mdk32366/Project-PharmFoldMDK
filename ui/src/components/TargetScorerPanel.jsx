import { Link } from 'react-router-dom'
import Term from './Term.jsx'
import PlddtAmbiguityNote from './PlddtAmbiguityNote.jsx'
import { targetStatus } from '../targetScore.js'

// D-068 — the scorer panel on the target record: the judgement the ranking made about THIS target, or
// — the common case — a reasoned "no score", never a blank (dec 1). Every number is derived from
// /api/ranking + the target's own record (dec 2 / §1: no route change). A score never renders without
// its rank and distribution context (dec 2); a labelled target shows both its in-fit score and its
// out-of-sample LOO percentile (dec 4); F-005's ambiguity travels with the attributions (dec 3).
// Bounded per D-028 / F-006 / D-041: no biology, no probability, no "promising", no "would work".

// Plain-language feature names, in β·x order (D-027). Neutral about the target's biology (D-028):
// "membrane-proximal confidence", never "accessible epitope".
const FEATURES = [
  'ECD length', 'compactness', 'mean confidence (pLDDT)',
  'membrane-proximal confidence', 'surface area', 'largest accessible patch',
]
const f3 = (x) => (x == null ? '—' : x.toFixed(3))
const median = (xs) => {
  if (!xs.length) return null
  const s = [...xs].sort((a, b) => a - b); const n = s.length
  return n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2
}

function Shell({ children }) {
  return (
    <section className="scorer-panel panel" aria-label="Scorer result">
      <h3>Scorer result</h3>
      {children}
    </section>
  )
}

export default function TargetScorerPanel({ detail, ranking }) {
  // The floor and the ranking membership both come from /api/ranking; without it the panel cannot
  // determine a status honestly, so it says so rather than guess (never a blank — dec 1).
  if (!ranking) {
    return <Shell><p className="no-score">The scorer result isn't loaded for this target yet.</p></Shell>
  }
  const s = targetStatus(detail, ranking)

  if (s.status === 'not_folded') {
    return (
      <Shell>
        <p className="no-score">
          No score — this target was never scored because it wasn't folded:{' '}
          <b>attempted, but did not complete</b>. <Link to="/coverage">Coverage</Link> gives the reason.
        </p>
      </Shell>
    )
  }
  if (s.status === 'below_floor') {
    return (
      <Shell>
        <p className="no-score">
          No score. The fold's average confidence (<Term name="pLDDT">pLDDT</Term>) is under {s.floor} —
          the floor fixed before the run (D-041). Below it, the shape measurements aren't reliable
          enough to rank on.
        </p>
      </Shell>
    )
  }
  if (s.status === 'held_out') {
    return (
      <Shell>
        <p className="no-score">
          No score. This target's outer region couldn't be marked off the same way as the others, so
          its measurements aren't comparable — it was <b>held out of the ranking, not scored low</b>{' '}
          (D-021).
        </p>
      </Shell>
    )
  }
  if (s.status === 'unranked_unexplained') {
    return (
      <Shell>
        <p className="no-score">
          No score — <b>reason not determined</b>. <Link to="/coverage">Coverage</Link> carries this
          target's disposition.
        </p>
      </Shell>
    )
  }

  // ranked — the full panel. A score NEVER appears without its rank and distribution context (dec 2).
  const { row, scores, loo, labelled } = s
  const n = scores.length
  const lo = Math.min(...scores), hi = Math.max(...scores), mid = median(scores)
  const contribs = row.attributions
    .map((v, i) => ({ label: FEATURES[i] || `feature ${i + 1}`, v }))
    .sort((a, b) => Math.abs(b.v) - Math.abs(a.v))

  return (
    <Shell>
      <p className="score-headline">
        Structural score <b>{f3(row.score)}</b> · rank <b>{row.rank}</b> of <b>{n}</b>
      </p>
      <p className="score-context">
        Across the {n} ranked targets the scores run {f3(lo)}–{f3(hi)} (median {f3(mid)}) — a bare
        score means little without that range.
      </p>

      {labelled && (
        <p className="labelled-note">
          This is a known ADC target — the model was trained partly on it, so its score above is{' '}
          <b>not a prediction about it</b>. The out-of-sample number is its{' '}
          <span className="term">
            <button type="button" className="term-trigger" aria-describedby="loo-depth">leave-one-out percentile</button>
            <span role="tooltip" id="loo-depth" className="term-def">
              The model is refitted with this one target removed, then asked to rank it — repeated for
              each known target in turn. Its percentile is where it landed: {f3(loo.percentile)} means
              above that fraction of the fit set. It's the pre-registered test (D-041), the only honest
              way to score a target the model wasn't allowed to learn from.
            </span>
          </span>: <b>{f3(loo.percentile)}</b>. That's where this target landed when the model was
          rebuilt from scratch without it, and it's the pre-registered result (D-041).
        </p>
      )}

      <div className="attributions">
        <h4>What moved this score</h4>
        <ul>
          {contribs.map(({ label, v }) => (
            <li key={label}>
              <span className="attr-feature">{label}</span>{' '}
              <span className={v >= 0 ? 'attr-pos' : 'attr-neg'}>{v >= 0 ? '+' : '−'}{Math.abs(v).toFixed(3)}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* dec 3: F-005 travels with the attributions — stated where the impression forms. Shared source. */}
      <PlddtAmbiguityNote />
    </Shell>
  )
}
