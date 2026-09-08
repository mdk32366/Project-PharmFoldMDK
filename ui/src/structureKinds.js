// How a census fold was PRODUCED, as a shared vocabulary (D-118 / D-133 / D-135).
//
// ⚠⚠ WHY THIS MODULE EXISTS. Three surfaces now read the same four categories — the census table's
// fold-type chips, `/coverage`'s second-population strip, and the Story's cold strip — and the
// order they appear in was typed inside `CensusTable.jsx`. A second copy of that order in a second
// component is how one page comes to show `assembled · single-pass` and another `single-pass ·
// assembled`, which reads as two different facts about one population.
//
// ⚠ THE ORDER IS NOT A RANKING and there is nothing here to rank: the two folded kinds first
// because they are what a reader came for, then the two absences, then the unrecorded rows.
// D-079 dec 1 bars scoring a census row; this orders CATEGORIES, and a category orders nothing by
// suitability.
//
// ⚠ It mirrors `app/reads.py::STRUCTURE_KIND_ORDER`, which is what `/api/census/summary` serves in.
// The API's order is authoritative where a payload supplies one — a surface reading
// `summary.structure_kinds` iterates the payload and never re-sorts it. This list is for the
// surfaces that hold ROWS rather than a summary (the census table), where nothing else carries one.
export const KIND_ORDER = ['assembled', 'single-pass', 'tiles_only', 'mucin', 'none']

// ⚠ The bucket a row with no `structure_kind` falls into. A blank cell reads as `single-pass` — a
// forward pass that never happened (D-133) — so the absence is named, here and once.
export const KIND_NONE = 'none'
export const KIND_NOT_RECORDED_LABEL = 'not recorded'

// ⚠ One `{key, n, label}` per kind PRESENT in `rows`, in `KIND_ORDER`. Counts and labels are
// DERIVED from the rows — the label is the API's own (`assembled (provisional)`, `tiles only`, …)
// so a filter can never spell a category differently from the column it filters (Constraint A).
// ⚠ A kind with no rows gets no entry: a control that can only empty the table is a broken
// control, and `assembled 0` printed as a finding is what the census truthfully showed for all 45
// assembled parents before D-134 repaired the identity check.
export function kindCounts(rows) {
  const n = new Map()
  const labels = new Map()
  for (const r of rows) {
    const k = r.structure_kind ?? KIND_NONE
    n.set(k, (n.get(k) ?? 0) + 1)
    if (!labels.has(k) && r.structure_kind_label) labels.set(k, r.structure_kind_label)
  }
  return KIND_ORDER.filter((k) => n.has(k)).map((k) => ({
    key: k,
    n: n.get(k),
    label: labels.get(k) ?? KIND_NOT_RECORDED_LABEL,
  }))
}

// ⚠⚠ FALLS CLOSED TO `all` (D-135 decision 7). `/census?structure=<kind>` is a shareable address,
// so the value arrives from outside the application and may be a typo, a stale bookmark, or a kind
// this census does not hold. Selecting it anyway would render an EMPTY table under a chip nobody
// pressed — the reader cannot tell that from "the census holds none of these", which is a different
// and much stronger claim. So an unrecognised kind resolves to `all`, and D-102's bar is honoured
// in the same breath: absent means `all` too, because a page must not arrive having chosen.
export function resolveKind(requested, present) {
  if (!requested || requested === 'all') return 'all'
  return present.some((k) => k.key === requested) ? requested : 'all'
}
