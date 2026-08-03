// Sorting for the target list — with the absent-value rule that makes it compatible with the
// project's honesty rather than a quiet erosion of it.
//
// ⚠ THE LOAD-BEARING RULE: AN ABSENT VALUE IS A CATEGORY, NEVER A LOW NUMBER.
//
// The list previously sorted with `(b.mean_plddt ?? 0) - (a.mean_plddt ?? 0)`. That `?? 0` coerces a
// missing measurement to zero, so an unmeasured target sorts as though it scored the WORST. This was
// not hypothetical: IGF2R is on the deployed list right now with `mean_plddt: null` (its fold hit a
// CUDA OOM at 2,491 aa — verified: `pdb_path` is null, so there is no structure and no pLDDT to have
// lost; the null is honest). Under `?? 0` the app was rendering **"no measurement" as "the worst
// measurement"** — a live honesty defect, not a future one.
//
// So absent-valued rows are held out as a SEPARATE CLUSTER that always stays visible and labelled,
// appended after the measured rows in BOTH directions. They are never interleaved with real low
// scores and never dropped. Reversing the sort must not promote "unknown" to the top either — absence
// is not the maximum any more than it is the minimum; it is off the axis entirely.
//
// This lives in one tested module on purpose. The census will add cancer-association, prevalence,
// lethality and served-status columns; when it does, they become new sort keys in a mechanism where
// "unmeasured is a category" is already enforced, instead of the rule being retrofitted under
// pressure across several call sites.

/** Is this value absent for sorting purposes? `null`/`undefined`/`NaN` — NOT 0, NOT ''. */
export function isAbsent(value) {
  return value === null || value === undefined || (typeof value === 'number' && Number.isNaN(value))
}

/**
 * Compare two defined values of the same column. Numbers compare numerically; everything else
 * compares as a case-insensitive string, so gene/accession sort alphabetically without a separate
 * code path per column.
 */
function compareDefined(a, b) {
  if (typeof a === 'number' && typeof b === 'number') return a - b
  return String(a).localeCompare(String(b), undefined, { sensitivity: 'base' })
}

/**
 * Sort `rows` by `key` in `dir` ('asc' | 'desc'), holding absent-valued rows out as a trailing
 * cluster in both directions.
 *
 * Returns a NEW array — never mutates the input, because the caller renders from the same rows and
 * an in-place sort would make the filtered/unfiltered sets disagree.
 *
 * `{ present, absent }` ordering is preserved within the absent cluster (stable), so the absent rows
 * keep whatever order they arrived in rather than being shuffled unpredictably run to run.
 */
export function sortRows(rows, key, dir = 'asc') {
  const list = [...(rows || [])]
  if (!key) return list

  const present = list.filter((r) => !isAbsent(r?.[key]))
  const absent = list.filter((r) => isAbsent(r?.[key]))

  present.sort((a, b) => {
    const cmp = compareDefined(a[key], b[key])
    return dir === 'desc' ? -cmp : cmp
  })

  // Absent rows ALWAYS trail, in both directions. They are a category, not an extreme value.
  return [...present, ...absent]
}

/** The three-state header cycle: default → asc → desc → default. */
export const SORT_STATES = ['asc', 'desc', null]

/**
 * Next (key, dir) for a click on `clickedKey`, given the current state. Clicking a new column starts
 * at ascending; clicking the active column advances asc → desc → back to the default sort.
 * A `null` dir means "return to the default", which the caller supplies.
 */
export function nextSort(current, clickedKey) {
  if (!current || current.key !== clickedKey) return { key: clickedKey, dir: 'asc' }
  if (current.dir === 'asc') return { key: clickedKey, dir: 'desc' }
  return null // third click → caller restores its default
}
