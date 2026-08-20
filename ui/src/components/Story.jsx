import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listAnalyses, getCoverage, getCensusSummary } from '../api.js'
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
    // ⚠ The census summary is ADDITIVE: a failure there must cost the census sentence and nothing
    // else, so it resolves to null rather than rejecting the pair the rest of the page depends on.
    // ⚠ `Promise.resolve(...)` so a supplier that throws SYNCHRONOUSLY, or returns a non-promise,
    // cannot take the page down with it — the same guard `TargetList` already uses for coverage.
    // ⚠⚠ My first version called `.catch` directly on the return value and crashed the whole Story
    // whenever the supplier was not a promise. The census sentence is additive; the page is not.
    const censusOnce = Promise.resolve().then(() => getCensusSummary()).catch(() => null)
    Promise.all([listAnalyses(), getCoverage(), censusOnce])
      .then(([analyses, coverage, census]) => {
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
          census,
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
          {/* ⚠ EVERY COUNT STATES ITS KEY. This read as the project's total; it is the cohort's.
              The census beat below is what widens it, and the two must not be confusable. */}
          <strong>What came out:</strong> {s.folded} of the {s.denominator ?? 82} cohort targets folded
          {s.denominator != null && <> — {s.rankedFolded} of them ranked-and-folded</>}.
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
      {/* ⚠⚠ BEAT 2b — THE CENSUS (owner ruling, 2026-08-21: it lands, and it lands HERE).
          The Story described an 82-target study and told a reader this project had folded 79
          proteins. It has folded 2,769. That was a faithful account of the application on
          2026-07-29 and the census has landed since.
          ⚠ The census is a CONTINUATION OF THE EXPERIMENT, not a feature: the cohort is 82 proteins
          somebody else's paper chose, and the question of whether the result is a property of THOSE
          targets or of the METHOD cannot be asked inside it.
          ⚠ Derived, never literal (D-050 / Constraint A) — from /api/census/summary, which exists
          because /api/census is 7.1 MB and this is the cold-open. */}
      {s?.census && (
        <p>
          <strong>Then we asked it of everything else.</strong> The cohort is 82 proteins chosen by
          somebody else&rsquo;s paper, so it cannot tell us whether the result is a property of{' '}
          <em>those</em> targets or of the method. So we built a census of every human surface
          protein we could define a boundary for — <strong>{s.census.manifest_rows.toLocaleString()}</strong>{' '}
          proteins — and folded <strong>{s.census.folded.toLocaleString()}</strong> of them on the
          same tier, under the same rules.{' '}
          {/* ⚠⚠ D-079 decision 1, STATED rather than relied upon. A reader must not infer that a
              bigger pile of folds is a bigger shortlist. */}
          <strong>The census is not scored and not ranked</strong> — a fold is a measurement, a score
          is an interpretation, and nothing here ranks a census protein against a cohort target.{' '}
          <Link to="/census">Browse the census →</Link>
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
        test. The shape features contributed little at this cohort size.{' '}
        {/* ⚠⚠ QUALITATIVE, PER THE OWNER'S RULING — the same Constraint-A and D-056 argument that
            kept beats 4–5 qualitative. The 32.2% appears only IN ITS CORRECT CONTEXT, which is what
            F-051 actually measured: not "confidence matters" but that ONE confidence feature carries
            it. ⚠ And F-051's own caveat travels with the figure — an attribution share is PREDICTOR
            WEIGHT, not a causal role — because the defect being described is a fraction standing in
            for the whole, and repeating that error in the sentence about it would be worse. */}
        Narrower still: of the two confidence features, it is really one — the confidence in the
        membrane-proximal region alone accounts for about <strong>32%</strong> of what the ranking
        weighs, five times the whole-domain figure. ⚠ That is how much the model <em>leans</em> on
        it, not a claim that the region causes anything.
      </p>

      {/* ⚠⚠ BEAT 5b — WHERE THE EVIDENCE LED (owner ruling, 2026-08-21: do not exclude the
          clinical layer — "it's just a reflection of where the information has taken us").
          ⚠ It sits AFTER the reversal on purpose. The reversal is what sent us looking for evidence
          that is not the model's own confidence, so this reads as consequence rather than as a
          feature tour — which is the D-056 readability risk the earlier draft worried about. */}
      <p>
        <strong>Which sent us looking for evidence the model could not supply.</strong> If the
        ordering rests on the network&rsquo;s confidence in its own output, the thing it most needs
        is a measurement made by somebody else, on tissue. So the cards now carry
        immunohistochemistry from the Human Protein Atlas — <em>of twelve tumour samples tested,
        eleven stained</em> — and, beside it, the same protein&rsquo;s staining in{' '}
        <strong>healthy</strong> tissue, because a target that lights up in tumours and in heart
        muscle is a different proposition from one that does not.{' '}
        {/* ⚠ Both edges or neither (D-093 decision 5): the tumour panel alone is the flattering half. */}
        <strong>It is an expression measurement, not a claim that the protein drives the disease.</strong>
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
