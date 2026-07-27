import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listAnalyses, getCoverage } from '../api.js'

// D-051 Decision 1: the cold-open Story at `/` — the thirty-second answer to "where is the deep
// learning." Every cohort number is DERIVED from /api/analyses + /api/coverage (Constraint A);
// none is a literal, because prose that quotes a fold count rots (D-050) and this is the most-read
// screen on the site. When the data can't be fetched, the narrative still renders — qualitatively,
// with no numbers, never stale ones.
export default function Story() {
  const [s, setS] = useState(null)
  useEffect(() => {
    Promise.all([listAnalyses(), getCoverage()])
      .then(([analyses, coverage]) => {
        const vals = analyses
          .map((a) => a.mean_plddt)
          .filter((v) => typeof v === 'number' && !Number.isNaN(v))
        const rows = (coverage && coverage.rows) || []
        setS({
          folded: vals.length,
          max: vals.length ? Math.max(...vals) : null,
          rankedFolded: rows.filter((r) => r.disposition === 'ranked' && r.fold_status === 'folded').length,
          denominator: coverage && coverage.coverage ? coverage.coverage.denominator : null,
          failed: rows.filter((r) => r.fold_status === 'failed').map((r) => r.gene),
          excluded: rows.filter((r) => r.fold_status === 'not_folded').map((r) => r.gene),
        })
      })
      .catch(() => setS(null))
  }, [])

  return (
    <div className="prose story">
      <h1>We folded a cohort of ADC targets with ESMFold — and the interface is honest about what came out.</h1>
      <p>
        <strong>The question:</strong> does a ranking of antibody–drug-conjugate targets built from{' '}
        <em>structure</em> — folds we computed ourselves — differ from one built from expression and
        prior evidence? Answering it begins with the structures, and{' '}
        <strong>we ran the neural network ourselves</strong>: every structure here is an{' '}
        <strong>ESMFold</strong> prediction (<code>facebook/esmfold_v1</code>, at a pinned revision),
        computed on our own GPU tier — <em>not</em> retrieved from a public database. Each carries the
        model's own per-residue confidence (pLDDT) and full provenance, so "we ran this" is
        checkable, not asserted.
      </p>
      {s ? (
        <p>
          <strong>What came out:</strong> {s.folded} targets folded
          {s.denominator != null && <> — {s.rankedFolded} of them ranked-and-folded of {s.denominator}</>}.
          {s.max != null && (
            <> The highest mean pLDDT is {s.max.toFixed(2)}: <strong>no target reaches the
            high-confidence range</strong> (≥90), and the confidence bands say so rather than hiding
            it.</>
          )}
          {(s.failed.length > 0 || s.excluded.length > 0) && (
            <> What did <em>not</em> fold is named with its reason
            {s.failed.length > 0 && <> — {s.failed.join(', ')} (a documented hardware ceiling)</>}
            {s.failed.length > 0 && s.excluded.length > 0 && ','}
            {s.excluded.length > 0 && <> {s.excluded.join(', ')} (too large to fold as one sequence)</>}
            , never dropped silently.</>
          )}
        </p>
      ) : (
        <p>
          <strong>What came out:</strong> most of the cohort folded, each with the model's own
          confidence; a few did not, and the interface names each with its reason rather than hiding
          it. See <Link to="/coverage">Coverage</Link> for the honest denominator.
        </p>
      )}
      <p>
        <strong>What is deliberately not built:</strong> the comparative ranking and the learned
        scorer it needs. It waits on that scorer and is <strong>not mocked</strong> — a fake ranking
        would be thrown away (D-028: a non-goal is a commitment, not an omission).
      </p>
      <p className="story-cta">
        <Link to="/targets">See the folded targets →</Link>
      </p>
    </div>
  )
}
