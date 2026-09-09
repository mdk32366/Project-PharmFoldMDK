// THREE ORTHOGONAL STATUS AXES for a census row (D-150).
//
// ⚠⚠ WHY THIS MODULE EXISTS. One badge was answering three different questions, and a reader had
// no way to tell which one it had answered. `folded` / `NOT FOLDED` conflates:
//   (A) is there a structure on disk, and what KIND of thing is being served,
//   (B) was this protein scored and ranked,
//   (C) if it was assembled from tiles, is the seam solved or is the artefact provisional.
//
// ⚠⚠ THE WITNESS THAT MADE IT A DEFECT RATHER THAN A TIDINESS COMPLAINT. `GET /api/census/Q9NYQ8`
// (FAT2, read live 2026-09-09) answers `folded: true`, `structure_kind: "assembled"`,
// `structure_kind_label: "assembled (provisional)"`, `hold48_kind: "parent_stitched"`,
// `scored: false`, `assembler_note: "assembled by pLDDT overlap, not superimposed; seam not
// solved"`, and `assembly_review.served_path.solved: false` with `not_flipped_reason:
// "not_in_pass_subset"`. FOUR different statuses, and one word — `Folded` — was standing for all
// of them. A single word cannot be wrong about one axis without being read as right about the
// other two.
//
// ⚠ EVERY AXIS IS ITS OWN FUNCTION, and the surfaces ask the function rather than re-deriving the
// rule. That is D-133 am. 1's discipline (`topologyBadgeKey`) applied to a harder case: the census
// LIST and the census DETAIL carry different payloads, so a re-derivation in two components is how
// one protein comes to have two structure statuses on two pages of one site.

// ── AXIS A · what structure is actually served ─────────────────────────────────────
export const STRUCTURE_NONE = 'none'
export const STRUCTURE_TILES_ONLY = 'tiles_only'
export const STRUCTURE_ONESHOT = 'oneshot'
export const STRUCTURE_ASSEMBLED_SERVED = 'assembled_served'

// ⚠ The order is NOT a ranking and there is nothing here to rank — it exists so the census table's
// status column can sort into GROUPS, the same ruling `KIND_ORDER` and `COST_ORDER` carry. It runs
// most-structure-first because that is the order a reader scans for, and a category orders nothing
// by suitability. D-079 dec 1 still bars scoring a census row.
export const STRUCTURE_SERVED_ORDER = [
  STRUCTURE_ASSEMBLED_SERVED, STRUCTURE_ONESHOT, STRUCTURE_TILES_ONLY, STRUCTURE_NONE,
]

// ⚠⚠ FAIL-CLOSED, and the branch order is the whole rule.
//
// 1. `tiles_only` FIRST, ahead of the `folded === false` denial. The census serves those rows with
//    `folded: false` because no PARENT was assembled — but tiles ARE on disk and the API says so
//    in `structure_kind`. Reading the denial first printed **NOT FOLDED** over a protein whose own
//    payload carries tile artefacts, which is the exact false claim this axis exists to stop.
// 2. Then `folded === false`: an explicit denial from the server outranks any kind label. A
//    `mucin` row is `folded: false` and takes this branch, which is correct — the label itself
//    says `mucin — not folded`. ⚠⚠ AND IT IS `=== false`, NEVER `!r.folded`: legacy rows predate
//    the field entirely, and treating an absent field as a denial would print NOT FOLDED over
//    every one of them. That is not a new caution — `CensusTable`'s folded count has read
//    `!== false` since the field arrived, and `CensusProteinView` gated its never-folded card the
//    same way. **A missing field is not a recorded `false`**, and this axis inherits that ruling
//    rather than re-litigating it.
// 3. `assembled` only when nothing has denied a structure. A parent whose kind says `assembled`
//    while `folded` says false is a contradiction, and the honest reading of a contradiction is
//    the WEAKER claim, never the stronger one.
// 4. Everything else is one forward pass — `folded === true`, and the legacy rows of branch 2.
//
// ⚠ Measured over `GET /api/census?limit=5000` (3,467 rows, 2026-09-09) this partitions the live
// census as: `oneshot` 3,418 · `assembled_served` 45 · `none` 4 (3 mucins + `P55073`, which
// carries no `structure_kind` at all) · `tiles_only` 0. The tiles branch has no live row today and
// is kept because the payload vocabulary and `unfoldedCopy` both still carry the category.
export function structureServed(r) {
  if (r.structure_kind === 'tiles_only') return STRUCTURE_TILES_ONLY
  if (r.folded === false) return STRUCTURE_NONE
  if (r.structure_kind === 'assembled') return STRUCTURE_ASSEMBLED_SERVED
  return STRUCTURE_ONESHOT
}

// ⚠⚠ NEVER A BARE `Folded`, and that is the copy rule this module was written to enforce. `Folded`
// is true of a single-pass fold, of a provisional assembly whose seam is not solved, and of a
// parent the D-139 gate refused — three artefacts a reader would treat very differently. The word
// is not wrong; it is unable to be wrong, which is worse.
export const TILES_ONLY_COPY = 'Tiles only — parent not assembled'
export const ONESHOT_COPY = 'Structure served (single-pass)'
// ⚠ The fallback when `structure_kind_label` is missing on an assembled row. `provisional` travels
// with it: an assembly whose label failed to arrive must not become the one assembly on the site
// that reads as finished.
export const ASSEMBLED_COPY = 'Structure served (assembled — provisional)'
// ⚠ The served label is PREFIXED rather than reprinted bare. `assembled (provisional)` already
// appears in the Structure column, and the same string twice in one row is two spellings of one
// fact — D-133's own complaint about the kind badge. The prefix makes this chip answer *what is
// served*, which is a different question from *how it was made*, and it keeps the API's own term
// intact inside it rather than re-spelling the category.
const servedPrefix = (label) => `Structure served — ${label}`
export const NOT_FOLDED_COPY = 'NOT FOLDED'
export const NOT_FOLDED_HERE_COPY = 'NOT FOLDED HERE'

// The word the surfaces print for axis A. ⚠ `structure_kind_label` is the API's own term and wins
// wherever there is one (D-133: the surface never re-spells a category it is served) — but only
// for the assembled case, where the served label already carries `(provisional)`.
export function structureServedLabel(r) {
  const axis = structureServed(r)
  if (axis === STRUCTURE_TILES_ONLY) return TILES_ONLY_COPY
  if (axis === STRUCTURE_ONESHOT) return ONESHOT_COPY
  if (axis === STRUCTURE_ASSEMBLED_SERVED) {
    return r.structure_kind_label ? servedPrefix(r.structure_kind_label) : ASSEMBLED_COPY
  }
  // ⚠ D-118's three-way never-folded distinction is preserved, not flattened: a protein folded
  // among the ranked 82 is NOT FOLDED **HERE**, which is a different fact from never folded at all.
  return r.cohort_fold ? NOT_FOLDED_HERE_COPY : NOT_FOLDED_COPY
}

// ── AXIS B · scored and ranked, or not ─────────────────────────────────────────────
//
// ⚠⚠ ALWAYS THE SAME ANSWER FOR A CENSUS ROW, AND SAYING IT ANYWAY IS THE POINT. D-079 decision 1
// bars scoring any census row, so `scored` is `false` for all 3,467 of them (measured over
// `GET /api/census?limit=5000`, 2026-09-09: `scored: false` × 3,467, no other value). A status
// that is constant is exactly the one a surface stops printing — and then the absence of a score
// has to be inferred from the absence of a number, which is how a reader concludes the fold failed.
export const NOT_SCORED_COPY = 'Not scored, not ranked'
// ⚠ The fallback reason. One live row (`P55073` / DIO3) carries `not_scored_reason: null`, so the
// surface must not render `Not scored, not ranked. null`.
export const NOT_SCORED_REASON_FALLBACK =
  'D-079 decision 1 — no census row is scored, and no census row is ranked against the 82'

export function scoreState(r) {
  return { label: NOT_SCORED_COPY, reason: r.not_scored_reason || NOT_SCORED_REASON_FALLBACK }
}

// ── AXIS C · the seam, and whether the served bytes are the gate's choice ──────────
//
// ⚠ ONLY MEANINGFUL WHEN AXIS A IS `assembled_served`. A single-pass fold has no seam, and saying
// `n/a` about a seam on a protein that was never tiled invents a question nobody asked.
export const SEAM_NOT_APPLICABLE = 'n/a'
export const SEAM_PROVISIONAL_ASSEMBLER = 'provisional_assembler'
export const SEAM_PASS_PATH_SERVED = 'pass_path_served'
export const SEAM_ARTIFACTS_ABSENT = 'artifacts_absent'

export const SEAM_PROVISIONAL_COPY = 'Seam not solved — provisional assembler'
export const SEAM_PASS_PATH_COPY = 'Seam recorded PASS — D-126 path served (still not solved)'
export const SEAM_ABSENT_COPY = 'Seam artefacts not on this payload'

// ⚠⚠ THE ABSENCE OF A SEAM MEASUREMENT IS NOT A SOLVED SEAM, and `artifacts_absent` is that
// sentence as a category. `assembly_review` rides on `/api/census/{id}` and NOT on `/api/census`
// (measured 2026-09-09: the list row carries 34 keys and `assembly_review` is not among them), so
// the list legitimately cannot answer axis C for most rows. It must say so rather than fall to
// `n/a`, which would read as *this assembly has no seam question*.
//
// ⚠ `pass_path_served` is read off `served_path.flipped`, the D-139 resolver's OWN answer, never
// re-derived from a pass count — D-139's rule is that the allowlist is the authority and artefacts
// on disk never flip a parent. And it still does not say `solved`: `served_path.solved` is `false`
// even for a flipped parent, so the copy carries `still not solved`.
export function seamState(r) {
  if (structureServed(r) !== STRUCTURE_ASSEMBLED_SERVED) {
    return { key: SEAM_NOT_APPLICABLE, label: null, note: null }
  }
  const review = r.assembly_review ?? null
  const served = review?.served_path ?? null
  // ⚠ THE NOTE IS ALWAYS THE SERVER'S OWN SENTENCE where there is one, and `assembler_note` is
  // preferred over `seam_note` because it is the shorter claim about THIS parent. `seam_note`
  // quotes the IGF2R ≈ 88.76 Å caveat, which is a measured fact about a DIFFERENT protein — a
  // reader who meets it beside FAT2 has been handed another parent's number.
  const note = r.assembler_note || review?.assembler_note || null
  if (served?.flipped === true) {
    return { key: SEAM_PASS_PATH_SERVED, label: SEAM_PASS_PATH_COPY, note, servedPath: served }
  }
  if (served) {
    return { key: SEAM_PROVISIONAL_ASSEMBLER, label: SEAM_PROVISIONAL_COPY, note, servedPath: served }
  }
  if (note) return { key: SEAM_PROVISIONAL_ASSEMBLER, label: SEAM_PROVISIONAL_COPY, note, servedPath: null }
  return { key: SEAM_ARTIFACTS_ABSENT, label: SEAM_ABSENT_COPY, note: null, servedPath: null }
}

// ⚠ The three axes as one object, so a surface that renders all three cannot render two.
export function statusAxes(r) {
  return { structure: structureServed(r), score: scoreState(r), seam: seamState(r) }
}

// ── the legend, defined beside the rule that produces it (D-133 am. 1's discipline) ─
//
// ⚠ Entries appear only for axis-A categories a row in the list actually wears; a legend that
// explains absent categories is the wall the owner ruled against on 2026-09-08.
export const STATUS_LEGEND = [
  { key: STRUCTURE_ASSEMBLED_SERVED, term: 'assembled (provisional)',
    meaning: 'a parent structure IS served for this protein, and it was joined from overlapping '
      + 'tile folds by per-residue confidence rather than superimposed. The seam is not solved, so '
      + 'the artefact stays provisional — it is not the same object as a single-pass fold.' },
  { key: STRUCTURE_ONESHOT, term: ONESHOT_COPY,
    meaning: 'one fold of the whole outward-facing span in a single pass — no tiles, no seam, and '
      + 'nothing assembled.' },
  { key: STRUCTURE_TILES_ONLY, term: TILES_ONLY_COPY,
    meaning: 'tile folds exist and were never joined into a parent. ⚠ This is NOT "not folded": '
      + 'structures are on disk. A tile window is also not the outward-facing region, so the '
      + 'viewer is withheld rather than showing a window as the protein.' },
  { key: STRUCTURE_NONE, term: `${NOT_FOLDED_COPY} / ${NOT_FOLDED_HERE_COPY}`,
    meaning: 'no structure was produced for this protein in the census, and none is served. NOT '
      + 'FOLDED HERE means it was folded among the 82 ranked targets and not here.' },
]

// ⚠⚠ THE SECOND AND THIRD LINES ARE UNCONDITIONAL, and that is deliberate. Axis B is the same for
// every census row, and axis C's warning is about a class of artefact rather than about a row —
// printing them only when something is wrong would teach a reader that silence means fine.
export const STATUS_AXIS_NOTE =
  'Three separate questions, and one badge used to answer all three: what structure is served · '
  + 'whether it was scored · whether its seam is solved. A protein can have a structure served and '
  + 'still be unscored, and it can be assembled and still have an unsolved seam.'

export function statusLegend(rows) {
  const present = new Set(rows.map((r) => structureServed(r)))
  return STATUS_LEGEND.filter((e) => present.has(e.key))
}
