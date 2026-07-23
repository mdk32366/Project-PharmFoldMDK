// The D-024 coverage line — the honest denominator that travels with every ranking.
//
// ⚠ CORRECTNESS REQUIREMENT (D-024, amendment §3). The headline is `ranked AND folded` — 40 of 82.
// NEVER `coverage.ranked` alone (67, which counts 27 rental targets not yet folded) and NEVER the
// folded count alone (42, which counts 2 held-out rows that are not in the ranking). Both are true
// numbers and both overstate the cohort in the direction of completeness — exactly what D-024
// forbids. The rows carry both `disposition` and `fold_status`, so the intersection is computed
// here client-side; no route change was needed.
//
// The three-cell partition (ranked/held_out/excluded) sums to the denominator; the two breakouts
// (unmeasured_tier ⊆ ranked, no_topology ⊆ held_out) are SUBSETS that cut across it and are shown
// as such, never summed in.

function count(rows, disposition, foldStatus) {
  return rows.filter((r) => r.disposition === disposition && r.fold_status === foldStatus).length
}

export default function CoverageLine({ coverage, rows }) {
  const rankedFolded = count(rows, 'ranked', 'folded')          // 40 — the number that matters
  const rankedUnfolded = count(rows, 'ranked', 'not_folded')    // 27 — rental, awaiting the A6000
  const heldFolded = count(rows, 'held_out', 'folded')          // 2
  const heldUnfolded = count(rows, 'held_out', 'not_folded')    // 11

  return (
    <section className="coverage-line panel">
      <p className="coverage-headline">
        <strong>{rankedFolded}</strong> ranked &amp; folded of <strong>{coverage.denominator}</strong> targets
      </p>
      <p className="coverage-sub">
        The ranking — once the scorer exists — covers these {rankedFolded}. Not the {coverage.ranked}{' '}
        ranked in the manifest ({rankedUnfolded} of them await a rental fold), and not the{' '}
        {rankedFolded + heldFolded} folded ({heldFolded} are held out of ranking). Both would overstate
        the cohort.
      </p>
      <ul className="partition">
        <li>
          <span className="cell-n">{coverage.ranked}</span> ranked
          <span className="cell-detail">{rankedFolded} folded · {rankedUnfolded} awaiting fold (rental)</span>
        </li>
        <li>
          <span className="cell-n">{coverage.held_out}</span> held out
          <span className="cell-detail">{heldFolded} folded · {heldUnfolded} not · boundary-method incomparable (D-021)</span>
        </li>
        <li>
          <span className="cell-n">{coverage.excluded}</span> excluded
          <span className="cell-detail">named &amp; oversize (D-022)</span>
        </li>
      </ul>
      <p className="breakouts">
        Subsets, cutting across the partition (not added to it): <strong>{coverage.unmeasured_tier}</strong>{' '}
        of the ranked sit on an <em>unmeasured local ceiling</em>; <strong>{coverage.no_topology}</strong>{' '}
        of the held-out have <em>no extracellular topology</em> to slice.
      </p>
    </section>
  )
}
