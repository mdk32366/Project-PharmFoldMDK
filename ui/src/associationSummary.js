// D-143 — reducing one target's D-053 association list to a cell a reader can scan.
//
// The detail surface (`CancerAssociations.jsx`) renders EVERY pair with no truncation (D-053
// decision 4), and that is right for a card and impossible in a table cell: `BTN3A3` carries 16
// tumour types. So the list surface shows the highest-scoring tumour type(s) and says how many
// there are, with the full list one click away — **the count is what stops this being a
// truncation**, because a cell that shows one of sixteen without saying sixteen is a silent
// filter wearing a value.
//
// ⚠⚠ TIES ARE ALL SHOWN, AND THAT IS THE WHOLE REASON THIS IS A MODULE RATHER THAN A `rows[0]`.
// Three of the 82 targets tie at their top quasi H-score (`JAG1` three ways, `CD53` and `INSR` two
// each — measured with `core.cancer_associations.load_associations()`), so "the top one" is not a
// well-defined single row for them. Picking whichever the CSV happened to list first would be an
// arbitrary choice presented as a measurement.
//
// ⚠ THE SUPPLIER SORTS, AND THIS DOES NOT RE-SORT. `core/cancer_associations.py` orders each
// target's pairs by `qh_score` descending in the data contract — deliberately not in JSX. Sorting
// again here would be a second implementation of "which is highest", free to disagree with the
// one the detail card renders. So the leading RUN of equal scores is read off the order as given…
//
// ⚠⚠ …and the order is CHECKED rather than assumed. If any later row outscores the first, the
// payload did not arrive in the contracted order, and this reports `ordered: false` with no top
// named instead of captioning row 0 as "the highest". A false superlative is worse than an
// admitted unknown, and it is the sort of thing that would otherwise be discovered on screen.

/**
 * Summarise one target's association rows.
 *
 * @param rows the `/api/associations` `associations[symbol]` array — `[{ cancer, qh_score }]`,
 *   already sorted by `qh_score` descending by the supplier. Missing/`null` is treated as empty.
 * @returns `{ total, top, topScore, ordered }` — `total` every pair the payload holds for this
 *   target, `top` the tumour type(s) sharing the leading score, `topScore` that score, and
 *   `ordered` whether the payload actually arrived in the contracted order.
 */
export function summariseAssociations(rows) {
  const list = (Array.isArray(rows) ? rows : []).filter((a) => a && a.cancer)
  if (list.length === 0) return { total: 0, top: [], topScore: null, ordered: true }

  const scores = list.map((a) => Number(a.qh_score))
  const lead = scores[0]
  // ⚠ `!(s > lead)`, never `s <= lead`: a NaN score must not read as "out of order" and drag the
  // whole cell into the unknown branch. It simply fails the equality below and is not named top.
  const ordered = scores.every((s) => !(s > lead))
  if (!ordered) return { total: list.length, top: [], topScore: null, ordered: false }

  const top = []
  for (let i = 0; i < list.length && Number(list[i].qh_score) === lead; i += 1) {
    top.push(list[i].cancer)
  }
  return { total: list.length, top, topScore: lead, ordered: true }
}
