import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getCoverage } from '../api.js'
import ArchitectureDiagram from './ArchitectureDiagram.jsx'
import Glossary from './Glossary.jsx'
import SpanGlossary from './SpanGlossary.jsx'
import Term from './Term.jsx'

// Method note (UI Plan v2 §3.4, D-028): what the system claims and what it does not — the whole
// frame at once, for a reader who wants it. Non-goals are commitments, not omissions (§9). This
// does NOT replace the inline per-class tooltips the ranking will carry; it is the standing scope.
export default function MethodNote() {
  // D-050: the coverage line is DERIVED from /api/coverage (the authoritative denominator, D-038),
  // computed the same way CoverageLine does — ranked AND folded, never a hardcoded literal (this
  // copy once read "40 ranked-and-folded of 82", stale once the cohort reached 67 ranked∧folded).
  const [cov, setCov] = useState(null)
  useEffect(() => {
    getCoverage().then(setCov).catch(() => setCov(null))
  }, [])
  const rankedFolded = cov
    ? cov.rows.filter((r) => r.disposition === 'ranked' && r.fold_status === 'folded').length
    : null
  const denominator = cov?.coverage?.denominator

  return (
    <div className="prose">
      <h2>What this system claims — and what it does not</h2>
      <p>
        PharmFoldMDK folds a fixed cohort of {denominator != null ? <>{denominator} </> : null}candidate{' '}
        <Term name="ADC">ADC</Term> targets with{' '}
        <strong><Term name="ESMFold">ESMFold</Term>, run in-project</strong>, and renders each
        structure with the model's own confidence (<Term name="pLDDT">pLDDT</Term>) and
        full provenance. This is a deep-learning course project: the neural network is the
        deliverable, and every structure here was <em>produced by it</em>, not retrieved from a
        database.
      </p>

      <h3>Where the deep learning runs (D-051)</h3>
      <p>
        Inference runs on a GPU tier <strong>outside Fly</strong> (D-004): the local worker and the
        rented GPU (A6000 for the cohort-29 batch; RTX PRO 6000 Blackwell for
        hold-48 tiles) pull jobs over outbound HTTPS, fold, and upload results. Hold-48
        stitch is a <strong>pLDDT-overlap assembler</strong>, not a Kabsch
        superimposer — seams are not scientifically solved. The always-on Fly
        serving tier holds <strong>no <code>worker/</code> and no CUDA</strong> (DEP-001). The diagram
        is rendered from a committed system model and pinned to the live route table by a test, so it
        cannot drift from the running system.
      </p>
      <ArchitectureDiagram />

      <h3>What it does today</h3>
      <ul>
        <li>Renders the structures we folded, coloured by the model's <strong>per-residue</strong> confidence (D-039).</li>
        <li>Surfaces provenance — model revision, precision, boundary method — so "we ran this ourselves, at a named revision" is <strong>checkable</strong>, not asserted.</li>
        <li>Shows an honest coverage line: <strong>{rankedFolded != null
          ? `${rankedFolded} ranked-and-folded of ${denominator}`
          : 'ranked-and-folded, out of the full cohort'}</strong>, with what is held out and excluded, and why.</li>
      </ul>

      <h3>What it does now — the ranking, at reduced scope</h3>
      <p>
        The centrepiece shipped: a learned scorer over structure-derived features ranks the cohort
        against an evidence baseline. The pre-registered leave-one-out result and the per-target scores
        are on the <Link to="/scorer">Scorer</Link> page.
      </p>
      <p>
        <strong>Deferred, and named rather than mocked:</strong> classifying the disagreements,
        baseline rank, and delta. <strong>Per-feature attribution now renders on each target's
        page</strong> (D-068), bounded as a statement about the model. It was never stubbed: a mock
        ranking would have been thrown away.
      </p>

      <h3>What it will never do — commitments (D-028)</h3>
      <ul>
        <li><strong>When it classifies disagreement, it will not explain it.</strong> Attribution is a statement about the <em>model</em> ("the model's confidence in the membrane-proximal region drives this rank"), never about the target's biology.</li>
        <li><strong>No causal biological claim</strong> — the system has no standing to make one.</li>
        <li><strong>No ordering of disagreements by "interestingness"</strong> — that is an explanation wearing a number.</li>
        <li>Some disagreements have a known explanation — two proteins can fold into similar shapes without sharing much of their sequence. Where that is the case, it is <strong>labelled as a known confound</strong>. The claim we can stand behind is narrower, and so it is stronger.</li>
      </ul>
      <p className="note">
        A non-goal here is a commitment, not an omission: a later iteration adding one of these does
        so as a ruled change with its own decision entry — not because the UI had space for it.
      </p>

      <SpanGlossary />
      <Glossary />
    </div>
  )
}
