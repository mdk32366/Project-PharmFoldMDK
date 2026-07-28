import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listAnalyses, getCoverage } from '../api.js'
import Term from './Term.jsx'

// D-051 Decision 1: the cold-open Story at `/` — the thirty-second answer to "where is the deep
// learning." Every cohort number is DERIVED from /api/analyses + /api/coverage (Constraint A);
// none is a literal, because prose that quotes a fold count rots (D-050) and this is the most-read
// screen on the site. When the data can't be fetched, the narrative still renders — qualitatively,
// with no numbers, never stale ones.
//
// Freeze push (2026-07-29): the scorer shipped, so the story resolves. Beats 4-6 report the fit, the
// sensitivity reversal (F-004/F-005), and the open question; the correction records the zero-positive
// defect (D-064); the "deliberately not built" promise resolves (D-067 dec 1). Beats 4-5 stay
// QUALITATIVE — Constraint-A surface area + the D-056 readability ceiling — with the numbers one click
// away on /scorer. D-043 (D-067 dec 3): `failed` (attempted, did not complete) and `not_folded` (never
// attempted) stay distinct and neither carries a hardcoded reason; the per-target reason is derived on
// /coverage. (The prior copy hardcoded "hardware ceiling" for the failed group — wrong: IGF2R's
// tier_reason is whole_sequence_fold, and "ceiling" describes the over_local_ceiling not_folded set.)
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
        <strong>The question:</strong> if we rank these cancer targets by their 3D shape — shapes we
        folded ourselves — do we get a different answer than ranking them by how strongly they appear
        in tumours and how much they have already been studied? To find out, we start with the shapes,
        and{' '}
        <strong>we ran the neural network ourselves</strong>: every structure here is an{' '}
        <strong><Term name="ESMFold">ESMFold</Term></strong> prediction (<code>facebook/esmfold_v1</code>,
        at a pinned revision), computed on our own <Term name="GPU">GPU</Term> tier — <em>not</em>{' '}
        retrieved from a public database. Each carries the model's own per-residue confidence
        (<Term name="pLDDT">pLDDT</Term>) and full provenance, so "we ran this" is checkable, not
        asserted.
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
            <> What did <em>not</em> fold is named, never dropped silently:
            {s.failed.length > 0 && <> {s.failed.join(', ')} {s.failed.length > 1 ? 'were' : 'was'} attempted and did not complete</>}
            {s.failed.length > 0 && s.excluded.length > 0 && ';'}
            {s.excluded.length > 0 && <> {s.excluded.join(', ')} {s.excluded.length > 1 ? 'were' : 'was'} never attempted</>}
            . <Link to="/coverage">Coverage</Link> gives each target's reason.</>
          )}
        </p>
      ) : (
        <p>
          <strong>What came out:</strong> most of the cohort folded, each with the model's own
          confidence; a few did not, and the interface names each with its reason rather than hiding
          it. See <Link to="/coverage">Coverage</Link> for the honest denominator.
        </p>
      )}
      {/* Beat 3 — fixed before any result, dated (decision refs are constants, not live statistics) */}
      <p>
        <strong>Fixed before any result, and dated:</strong> the six shape-and-confidence features
        (D-027, 22 Jul), the model and both ways it could disappoint (D-041, 23 Jul), and every free
        setting of the evaluation (D-060, 27 Jul) were all settled before a single score existed.
      </p>

      {/* Beat 4 — what the fit found. QUALITATIVE (Constraint-A, readability); amendment 4 guard:
          "over the folds that clear the confidence floor" signals a subset, so nothing implies the
          ranking covers the 67 ranked-and-folded named above. Links to Scorer for the numbers. */}
      <p>
        <strong>What the fit found</strong> — over the folds that clear the confidence floor, not the
        whole cohort — is a <strong>modest, above-chance ordering</strong>: better than a coin flip,
        but not distinguishable from ranking the targets by expression and prior evidence, and not a
        stand-in for it. <Link to="/scorer">The Scorer page</Link> shows how modest, with the full
        result.
      </p>

      {/* Beat 5 — the reversal (amendment 1: "most of it" / "contributed little") */}
      <p>
        <strong>Then a sensitivity check asked which features carried the ordering</strong>, and the
        answer reversed the premise: <strong>most of it comes from the model's own confidence in each
        fold</strong> (<Term name="pLDDT">pLDDT</Term>), not from the geometry the study set out to
        test. The shape features contributed little at this cohort size.
      </p>

      {/* Beat 6 — what is open (ends on the question, not a claim) */}
      <p>
        <strong>So the real question is still open.</strong> That confidence could be reading genuine
        structural order — a well-formed, reachable outer region of the protein — or it could be
        reading how well-studied a protein is, since the folding model is more confident about proteins
        it saw more of. This design cannot separate the two. <em>Does structure-derived confidence rank
        these targets because of what the structure is, or because of what has already been looked
        at?</em>
      </p>

      {/* The correction — register: plain, not a triumph. Passive on the public surface; the decision
          log carries the attribution (D-064). */}
      <p className="correction">
        <strong>The correction:</strong> an early run fit the scorer on zero positives — the driver
        read a label schema the curated file never adopted, so no target counted as a known ADC
        target. The empty fit raised, and the raise was at first misread as a finding about the data
        rather than a defect in the pipeline. The defect was found and the reading withdrawn; the
        invalid run was kept and marked rather than overwritten, and the corrected run produced the
        result shown here.
      </p>

      {/* The resolved promise — resolves, not deleted (D-067 dec 1): a commitment met, not a boast. */}
      <p>
        <strong>What was deliberately not built, until it was:</strong> this page promised a comparison
        ranking and the learned scorer it needs, and refused to fake it in the meantime. The scorer now
        exists and has run — the ranking is real, at reduced scope, on the{' '}
        <Link to="/scorer">Scorer</Link> page, not a stand-in.
      </p>

      <p className="story-cta">
        <Link to="/targets">See the folded targets →</Link>
      </p>
    </div>
  )
}
