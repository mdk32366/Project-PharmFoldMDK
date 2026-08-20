// Agreement between a count and the noun it counts.
//
// ⚠⚠ WHY THIS IS A MODULE. The LAMP1 card rendered **"1 of 1 cell types" twenty-six times** in one
// normal-tissue list — 26 of its 49 rows — because the noun was hard-coded plural and the singular
// case was never considered. It is small, and it was on screen more often than any other sentence
// on the card.
//
// ⚠ The failure is systematic rather than local: every count on these surfaces is interpolated
// beside a fixed noun, so the same defect exists wherever a count can reach 1. Fixing the one site
// that was reported would leave the rest, and the next report would be the same defect at a
// different address — which is `F-052`'s shape. One helper, every caller.
//
// ⚠ English irregulars are NOT guessed. A caller with an irregular plural passes it explicitly;
// this appends "s" and nothing cleverer, because a surface that silently invents "tissuess" or
// "analysises" is worse than one that spells it out.

/** The noun agreeing with `n`: `plural(1, 'cell type')` → `'cell type'`, `plural(3, …)` → `'cell types'`. */
export function plural(n, singular, pluralForm) {
  return Number(n) === 1 ? singular : (pluralForm ?? `${singular}s`)
}

/** The count and its noun together: `count(1, 'cell type')` → `'1 cell type'`. */
export function count(n, singular, pluralForm) {
  return `${n} ${plural(n, singular, pluralForm)}`
}

/**
 * The `a of b noun` form these cards use throughout — and the noun agrees with **b**, the total,
 * because that is the noun being counted: *"1 of 1 cell type"*, *"1 of 3 cell types"*.
 * ⚠ Agreeing with `a` instead would give "1 of 3 cell type", which is the same bug mirrored.
 */
export function ofCount(a, b, singular, pluralForm) {
  return `${a} of ${b} ${plural(b, singular, pluralForm)}`
}
