import { useState } from 'react'
import { COHORT_MAX_PLDDT } from '../plddt.js'

// What pLDDT is, and — the question nobody thinks to ask until they've stared at the number for a
// while — whether it can be moved. Collapsed by default so it does not compete with the measurement
// it explains; the summary is a question because that is how a reader arrives at it.
//
// ⚠ The raisability answer is deliberately NOT a list of tricks. The honest answer is that pLDDT is
// two claims wearing one number — one about the method, one about the molecule — and the useful
// skill is telling which one you are looking at. A page that only listed levers would teach readers
// to push a number that, for a disordered region, cannot move and should not.
// ⚠ `showCohortMax` exists because this component was rendered on census pages while quoting the
// COHORT's measured ceiling — a fact about the 82, shown beside census structures that exceed it
// (F-038). The "why nothing reaches 90" explanation is about the METHOD and stays; only the
// population-specific number is conditional.
export default function PlddtExplainer({ showCohortMax = true }) {
  const [open, setOpen] = useState(false)
  return (
    <details className="plddt-explainer panel" open={open} onToggle={(e) => setOpen(e.target.open)}>
      <summary>What is pLDDT — and can it be improved?</summary>

      <h4>What the number is</h4>
      <p>
        <strong>pLDDT</strong> is the <em>predicted Local Distance Difference Test</em>: the model's
        prediction of <strong>its own accuracy</strong>, per residue, on a 0–100 scale.
      </p>
      <p>
        The underlying measure, lDDT, compares a structure to a known reference: for each atom, take
        its neighbours and ask what fraction of the distances between them match the reference within
        0.5, 1, 2 and 4 Å. It is <strong>superposition-free</strong> — the two structures are never
        aligned. That is the point: it asks whether the <em>local neighbourhood</em> is right,
        independent of whether the whole molecule is oriented correctly.
      </p>
      <p className="caveat">
        ⚠ pLDDT predicts that score <em>without having the reference</em>. It is the model grading
        its own work — reasonably calibrated, but a <strong>self-report, not a measurement</strong>.
      </p>

      <h4>What it does not tell you</h4>
      <ul>
        <li>
          <strong>Nothing about domain arrangement.</strong> Two domains can each score 90 while
          being placed wrongly relative to each other. That is what <strong>PAE</strong> (predicted
          aligned error) is for. High pLDDT with poor PAE is a real trap for multi-domain
          ectodomains — which is most of what is on this site.
        </li>
        <li>
          <strong>A mean hides its distribution.</strong> A folded domain at 90 beside a disordered
          linker at 30 averages to about 70 and reads as “confident”. The per-residue plot above the
          mean is not decoration; for deciding whether a <em>surface</em> is bindable it is the only
          part that matters.
        </li>
      </ul>

      <h4>Why the scores here run lower than you may expect</h4>
      <p>
        {showCohortMax && (
          <>The ranked cohort&rsquo;s maximum is <strong>{COHORT_MAX_PLDDT}</strong>. </>
        )}
        These folds come from{' '}
        <strong>ESMFold</strong>, which predicts from a <em>single sequence</em> using a protein
        language model. AlphaFold2 additionally reads a multiple sequence alignment — the
        evolutionary record of the protein family — and generally scores higher for it. A pLDDT of 74
        here is not the same claim as a 74 from an MSA-based method.
      </p>

      <h4>Can it be improved, or is it fixed?</h4>
      <p>
        <strong>Both — and separating the two is the useful part.</strong> pLDDT is two claims
        wearing one number: a statement about the <em>method</em>, and a statement about the{' '}
        <em>molecule</em>.
      </p>

      <p><strong>Method-limited — genuinely raisable:</strong></p>
      <ul>
        <li>
          <strong>Evolutionary information (MSAs).</strong> The largest single lever. Moving from a
          single-sequence model to an MSA-based one typically gains the most on proteins with deep,
          well-populated families.
        </li>
        <li>
          <strong>Structural templates.</strong> If a homolog has been solved experimentally, using
          it as a template raises confidence substantially.
        </li>
        <li>
          <strong>More recycling passes.</strong> The prediction is fed back through the network;
          more iterations help, with diminishing returns. Cheap to try.
        </li>
        <li>
          <strong>Folding a domain on its own.</strong> A well-defined domain often scores markedly
          higher alone than embedded in a long, partly disordered chain — the model is no longer
          trying to place regions that have no fixed position.
        </li>
        <li>
          <strong>Newer models.</strong> The field moves fast; successor models generally predict
          better and know it.
        </li>
      </ul>

      <p><strong>Molecule-limited — not raisable by any amount of compute:</strong></p>
      <p className="caveat">
        ⚠⚠ If a region is <strong>intrinsically disordered</strong>, it has no single structure to
        predict. No MSA depth, no template, no larger model and no longer run will produce a
        confident answer, <strong>because a confident answer would be wrong</strong>. Persistently
        low pLDDT is used in practice <em>as</em> a disorder predictor — the low number is the
        finding, not the failure.
      </p>

      <h4>Telling which one you are looking at</h4>
      <p>
        This is testable rather than a matter of opinion. If the same region scores well when folded
        alone, or a close homolog folds confidently, the limit was the method. If it stays low across
        methods and independent disorder predictors agree, the limit is the protein — and for an
        antibody target that is itself worth knowing, because a region with no fixed structure has no
        stable epitope to bind.
      </p>
      <p className="caveat">
        ⚠ Nothing on this site has been re-folded under an alternative method. Every number here
        comes from one recipe, and the “method-limited” routes above are described as available, not
        as attempted.
      </p>
    </details>
  )
}
