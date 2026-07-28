// D-068 — resolve a target record to its scorer status. A target page must say SOMETHING true about
// the score that ranked it (or about why there is none); "no score" is always a rendered state with a
// reason, never a blank (D-068 dec 1). Every number the panel shows is derived here from the target's
// own record + the /api/ranking payload — no route change was needed (D-068 §1).
//
// ⚠ PRECEDENCE (owner ruling, D-068 dec 3-mapping): FOLD STATE PRECEDES DISPOSITION. A target with no
// fold has no measurements, so no disposition can apply to it. Order:
//   not folded → below floor → held out → ranked → (defensive) unranked-unexplained.
// This is why IGF2R (fold failed; disposition happens to be held_out) reads "not folded": rendering
// "held out because its measurements aren't comparable" would imply measurements that do not exist.

// Every target reachable via TargetView has an analysis row (it was enqueued, therefore attempted).
// So a missing fold here is always D-043 "attempted, did not complete" — never "never attempted",
// which has no analysis row and no target page to land on.
export function targetStatus(detail, ranking) {
  // (1) no fold at all — attempted, did not complete (D-043). Precedes everything: no fold, no
  // measurements, no disposition applies (IGF2R).
  if (detail.mean_plddt == null) {
    return { status: 'not_folded', category: 'attempted' }
  }

  // (2) held out of cross-method ranking (D-021) — a STRUCTURAL, pLDDT-INDEPENDENT reason: a whole-
  // method target is incomparable whatever its confidence (even folded to 95 it is held out). So
  // held_out precedes below_floor.
  // ⚠ D-068 precedence amendment (2026-07-29): this SUPERSEDES the original below_floor-before-held_out
  // sub-order. That order gave a folded, held-out, below-floor target (TMEM108) "below floor" on its
  // page while the backend `_exclusion_reason` and the Scorer excluded-set said "held out" — two
  // surfaces, one target, two reasons. Realigning the UI to held_out-first (what the backend already
  // does) closes that disagreement. `not_folded` still leads, so IGF2R is unaffected.
  if (detail.disposition === 'held_out') {
    return { status: 'held_out' }
  }

  // (3) folded, comparable, but below the pre-registered confidence floor (D-041 §5 / D-060). Floor is
  // DERIVED from the ranking payload, never typed (Constraint-A).
  const floor = ranking?.result?.plddt_floor
  if (floor != null && detail.mean_plddt < floor) {
    return { status: 'below_floor', floor }
  }

  // (4) folded, above floor, ranked disposition → it should be in the 56. Join by accession.
  const rows = ranking?.rows || []
  const row = rows.find((r) => r.accession === detail.accession)
  if (row) {
    const scores = rows.map((r) => r.score)                                   // for min/median/max context (dec 2)
    const dist = ranking?.result?.distribution || []
    const loo = dist.find((d) => d.symbol === detail.gene) || null            // labelled targets only (dec 4)
    return { status: 'ranked', row, scores, loo, labelled: loo != null }
  }

  // (5) defensive: folded, above floor, ranked by disposition, yet ABSENT from the 56. Never a silent
  // fall-through — a named state the panel renders as "reason not determined" (owner ruling). If this
  // set is empty in production, the panel's test asserts it so.
  return { status: 'unranked_unexplained' }
}
