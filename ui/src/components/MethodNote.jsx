// Method note (UI Plan v2 §3.4, D-028): what the system claims and what it does not — the whole
// frame at once, for a reader who wants it. Non-goals are commitments, not omissions (§9). This
// does NOT replace the inline per-class tooltips the ranking will carry; it is the standing scope.
export default function MethodNote() {
  return (
    <div className="prose">
      <h2>What this system claims — and what it does not</h2>
      <p>
        PharmFoldMDK folds a fixed cohort of 82 candidate ADC targets with <strong>ESMFold, run
        in-project</strong>, and renders each structure with the model's own confidence (pLDDT) and
        full provenance. This is a deep-learning course project: the neural network is the
        deliverable, and every structure here was <em>produced by it</em>, not retrieved from a
        database.
      </p>

      <h3>What it does today</h3>
      <ul>
        <li>Renders the structures we folded, coloured by the model's <strong>per-residue</strong> confidence (D-039).</li>
        <li>Surfaces provenance — model revision, precision, boundary method — so "we ran this ourselves, at a named revision" is <strong>checkable</strong>, not asserted.</li>
        <li>Shows an honest coverage line: <strong>40 ranked-and-folded of 82</strong>, with what is held out and excluded, and why.</li>
      </ul>

      <h3>What it will do — not yet, and never mocked</h3>
      <p>
        The centrepiece is a comparative ranking: a learned scorer over structure-derived features,
        ranking the cohort against an evidence baseline, with the disagreements <strong>detected and
        classified</strong>. It waits on the scorer (the cohort's features and a fit). It is not
        built, and it is deliberately <strong>not stubbed</strong> — a mock ranking would be thrown away.
      </p>

      <h3>What it will never do — commitments (D-028)</h3>
      <ul>
        <li><strong>It classifies disagreement; it does not explain it.</strong> Attribution is a statement about the <em>model</em> ("feature 6 drives this rank"), never about the target's biology.</li>
        <li><strong>No causal biological claim</strong> — the system has no standing to make one.</li>
        <li><strong>No ordering of disagreements by "interestingness"</strong> — that is an explanation wearing a number.</li>
        <li>Where a disagreement is explicable by known homology (convergent folds, divergent sequences within a family), it is labelled a <strong>known confound where it is shown</strong>. The supportable finding is narrower, and therefore stronger.</li>
      </ul>
      <p className="note">
        A non-goal here is a commitment, not an omission: a later iteration adding one of these does
        so as a ruled change with its own decision entry — not because the UI had space for it.
      </p>
    </div>
  )
}
