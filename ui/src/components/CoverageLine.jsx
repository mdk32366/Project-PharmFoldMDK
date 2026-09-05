// The D-024 coverage line — the honest denominator that travels with every ranking.
//
// ⚠ CORRECTNESS REQUIREMENT (D-024, amendment §3). The headline is `ranked AND folded`, NEVER
// `coverage.ranked` alone (counts ranked targets not yet folded) and NEVER the folded count alone
// (counts held-out rows that are not in the ranking). Both are true numbers and both overstate the
// cohort in the direction of completeness — exactly what D-024 forbids. The rows carry both
// `disposition` and `fold_status`, so the intersection is computed here client-side; no route
// change was needed. (No literal counts in this comment — they rot as the cohort grows; D-050.)
//
// The three-cell partition (ranked/held_out/excluded) sums to the denominator; the two breakouts
// (unmeasured_tier ⊆ ranked, no_topology ⊆ held_out) are SUBSETS that cut across it and are shown
// as such, never summed in.
//
// ⚠ D-066. This component states the PARTITION; it does NOT claim what the RANKING covers. The
// ranking's membership is decided downstream by the pLDDT floor, which this component cannot see —
// so a "the ranking covers these N" claim is unverifiable here, and on /scorer it was false (67
// ranked & folded vs 56 above the floor). The forward-looking clause ("once the scorer exists —
// covers these N") was removed, not re-tensed; `ranked` here is the D-024 disposition, never
// "in the ranking". The scorer renders its own 67 → 56 reconciliation beside its own table.

function count(rows, disposition, foldStatus) {
  return rows.filter((r) => r.disposition === disposition && r.fold_status === foldStatus).length
}

export default function CoverageLine({ coverage, rows }) {
  const rankedFolded = count(rows, 'ranked', 'folded')          // the number that matters (D-024)
  const rankedUnfolded = count(rows, 'ranked', 'not_folded')    // ranked, awaiting a fold
  const heldFolded = count(rows, 'held_out', 'folded')          // folded but held out of ranking (D-021)
  const heldUnfolded = count(rows, 'held_out', 'not_folded')    // held out and not folded

  return (
    <section className="coverage-line panel">
      <p className="coverage-headline">
        <strong>{rankedFolded}</strong> ranked &amp; folded of <strong>{coverage.denominator}</strong> targets
      </p>
      <p className="coverage-sub">
        This intersection is the honest denominator.{' '}
        {rankedUnfolded > 0 ? (
          <>Not the {coverage.ranked} ranked in the manifest ({rankedUnfolded} of them not
          folded in the cohort), and not the {rankedFolded + heldFolded} folded ({heldFolded} are held out of
          ranking). Both would overstate the cohort.</>
        ) : (
          <>Not the {rankedFolded + heldFolded} folded ({heldFolded} are held out of ranking) — that
          would overstate the cohort.</>
        )}
      </p>
      <ul className="partition">
        <li>
          <span className="cell-n">{coverage.ranked}</span> ranked
          <span className="cell-detail">{rankedFolded} folded · {rankedUnfolded} not folded in the cohort</span>
          {/* F-049's third instance. `ranked` is the D-024 disposition and is ELIGIBILITY, not
              membership of the ranking set — /api/ranking's `n_ranking_set` is smaller because a
              pLDDT floor is applied downstream. ⚠ D-066 still binds: this component cannot see
              that floor, so it points at the page that does the arithmetic and states NO size. */}
          <span className="cell-detail">
            eligible to be ranked — a pLDDT floor removes more at scoring time; the scorer page
            reconciles the two
          </span>
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
