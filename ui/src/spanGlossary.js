// R4 — the span-vocabulary glossary. D-016 applied to the UI: this turns sixteen invisible string
// comparisons into sixteen stated, defensible, auditable decisions.
//
// ⚠ EVERY TERM APPEARS — accepted, held AND rejected alike. A term simply absent reads as "nobody
// thought of it." A term listed as rejected WITH A REASON reads as "considered, and here is why
// not." Same distinction as an empty band key versus an omitted one, and the reason this file
// carries the six rejected terms rather than only the seven that do something.
//
// ⚠ PLAIN LANGUAGE BESIDE THE TECHNICAL, BOTH PRESENT. "The inside of a lysosome is, topologically,
// the outside of the cell" does work that "lumenal domains are topologically equivalent to
// extracellular domains" does not. Neither replaces the other.
//
// ⚠ PROVENANCE IS PART OF EVERY ENTRY. The compartment reasoning is Planner-supplied general
// knowledge and was NOT sourced at first hand; the ruling says so and so does the surface. A reader
// who cannot tell a sourced claim from an unsourced one has been given confidence, not information.

// The provenance string every compartment claim carries. ⚠ Do not soften it.
export const COMPARTMENT_PROVENANCE =
  'Compartment reasoning is general knowledge supplied during the ruling and was not read from a ' +
  'primary source. It is recorded that way on purpose (D-016).'

export const SPAN_TERMS = [
  // ── ACCEPTED ──────────────────────────────────────────────────────────────
  {
    term: 'Extracellular', ruling: 'accepted',
    compartment: 'the outside of the cell',
    reason: 'The original definition, unchanged. This is the term the extractor always looked for.',
    plain: 'The part of the protein that sticks out of the cell, where an antibody can reach it.',
  },
  {
    term: 'Lumenal', ruling: 'accepted',
    compartment: 'the lumen of the ER, Golgi, an endosome or a lysosome',
    reason:
      'The core case. A membrane protein’s topology is fixed when it is inserted into the ER ' +
      'and is preserved all the way through the secretory pathway, so when a vesicle fuses with ' +
      'the cell surface the lumenal face becomes the extracellular face.',
    plain:
      'The inside of a lysosome is, topologically, the outside of the cell. A protein sitting in ' +
      'that membrane has the same face pointing outward — it is just parked somewhere else ' +
      'until the cell brings it to the surface.',
  },
  {
    term: 'Lumenal, vesicle', ruling: 'accepted',
    compartment: 'the lumen of a secretory or transport vesicle',
    reason: 'A secretory vesicle fuses with the plasma membrane by definition — that is what it is for.',
    plain: 'Same as lumenal, on a bubble whose whole job is to travel to the surface and open.',
  },
  {
    term: 'Vesicular', ruling: 'accepted',
    compartment: 'a vesicle lumen, generic',
    reason: 'The same compartment as `Lumenal, vesicle`, written without the qualifier.',
    plain: 'The inside of a transport bubble.',
  },
  {
    term: 'Intragranular', ruling: 'accepted',
    compartment: 'the lumen of a secretory granule',
    reason: 'Exocytosis empties the granule through the plasma membrane and exposes this face.',
    plain: 'Inside a storage packet that the cell later dumps out through its own surface.',
  },
  {
    term: 'Exoplasmic loop', ruling: 'accepted',
    compartment: 'the exoplasmic — that is, non-cytoplasmic — face',
    reason:
      '⚠ *Exoplasmic* MEANS the non-cytoplasmic face. It is a third word for the same thing, ' +
      'and a search for "lumenal" would have missed it just as a search for "extracellular" did.',
    plain: 'A different word for the same outward-facing side.',
  },
  {
    term: 'Perinuclear space', ruling: 'accepted',
    compartment: 'the space between the inner and outer nuclear membranes',
    reason:
      '⚠ It is CONTINUOUS with the ER lumen — the same compartment under a different ' +
      'name. And it is a trap: the word contains "nuclear", so a widening written as "not ' +
      'cytoplasmic and not nuclear" silently drops every one of them. The test is set membership ' +
      'on the exact term, never a substring.',
    plain:
      'The gap inside the double wall around the nucleus. It is not the nucleus — it opens ' +
      'directly into the same space as the ER.',
  },

  // ── HELD ──────────────────────────────────────────────────────────────────
  {
    term: 'Lumenal, melanosome', ruling: 'held',
    compartment: 'the lumen of a melanosome, a lysosome-related organelle',
    reason:
      'Held pending a check, and NOT accepted in the meantime — so it gains nothing today. ' +
      'Melanosomal membrane proteins do reach the cell surface, but that is a specialised lineage ' +
      'and the reasoning behind it was not sourced at first hand.',
    plain:
      'The inside of the pigment packet in a pigment cell. Probably reaches the surface, but it is ' +
      'a special case and it is being checked rather than assumed.',
  },
  {
    term: 'Vacuolar', ruling: 'held',
    compartment: 'a vacuolar or lysosomal lumen',
    reason:
      'Held pending the same check. In human entries this is usually lysosome-like, and lysosomal ' +
      'exocytosis is real — but the case is weaker than `Lumenal` and it is not being ' +
      'accepted on a resemblance.',
    plain: 'The inside of a storage or digestion compartment. Less certain than the lysosome case.',
  },

  // ── REJECTED ──────────────────────────────────────────────────────────────
  {
    term: 'Cytoplasmic', ruling: 'rejected',
    compartment: 'the cytosol — inside the cell',
    reason: 'The inward-facing side. An antibody given to a patient never reaches it.',
    plain: 'The part tucked inside the cell. A drug delivered through the bloodstream cannot touch it.',
  },
  {
    term: 'Mitochondrial intermembrane', ruling: 'rejected',
    compartment: 'the space between the two mitochondrial membranes',
    reason:
      '⚠ Mitochondria do not fuse with the plasma membrane, on any mechanism. This face ' +
      'cannot become a cell-surface face.',
    plain:
      'Inside the cell’s power plant. It has no route to the outside — unlike a ' +
      'lysosome, it never travels to the surface and opens.',
  },
  {
    term: 'Mitochondrial matrix', ruling: 'rejected',
    compartment: 'the innermost mitochondrial compartment',
    reason: 'The same reason, one membrane further in.',
    plain: 'Deeper inside the power plant. Also unreachable.',
  },
  {
    term: 'Nuclear', ruling: 'rejected',
    compartment: 'the nucleoplasm',
    reason:
      'The nucleus does not traffic to the plasma membrane. ⚠ Note this is a DIFFERENT term ' +
      'from `Perinuclear space`, which is accepted — the two are not variants of one word.',
    plain: 'Inside the nucleus, where the DNA is. No route to the outside.',
  },
  {
    term: 'Peroxisomal', ruling: 'rejected',
    compartment: 'the peroxisome',
    reason: 'Peroxisomes do not fuse with the plasma membrane.',
    plain: 'Inside a small waste-processing compartment. It stays inside.',
  },
  {
    term: 'Peroxisomal matrix', ruling: 'rejected',
    compartment: 'the peroxisomal interior',
    reason: 'The same reason.',
    plain: 'Deeper inside that same compartment.',
  },
  {
    term: 'Mother cell cytoplasmic', ruling: 'unruled',
    compartment: 'cytoplasm — a sporulation term from yeast biology',
    reason:
      '⚠ Not ruled, and deliberately not guessed at. It appears once, on a human, reviewed ' +
      'entry (a mitochondrial pyruvate carrier), between two mitochondrial domains and citing the ' +
      'same single source as both — the shape of a term carried across from a yeast study. ' +
      'It changes no count either way, because cytoplasmic and mitochondrial faces are rejected ' +
      'regardless. It is listed here rather than dropped, because a term nobody can see is a term ' +
      'nobody can question.',
    plain:
      'A word borrowed from yeast biology that appears once, in a human entry, where it does not ' +
      'belong. It affects nothing, and it is shown rather than quietly deleted.',
  },
]

// ⚠ Tooltips wherever a band, a category or a count is displayed. Each of these used to be part of
// one band called `no_topology` that meant five different things.
export const SPAN_CATEGORY_TOOLTIPS = {
  no_extracellular_span:
    'No topological domain with an accepted description, and no GPI anchor. ⚠ This now means ' +
    'only that. It used to be called "no topology" and covered five different situations, four of ' +
    'which have their own category below.',
  span_boundary_unknown:
    'The domain IS annotated as reachable — and one end of it is recorded as unknown, so its ' +
    'length cannot be computed. ⚠ It is neither "no reachable domain" nor a usable ' +
    'measurement, so it is neither counted as foldable nor filed as an absence. No coordinate is ' +
    'invented to fill the gap.',
  term_unruled:
    'The domain carries a description that has not been ruled accepted, held or rejected. ' +
    '⚠ Named and shown rather than silently dropped or silently accepted — that ' +
    'silence is the defect this whole vocabulary came from.',
  absent_with_reason:
    'A feature the rule requires is missing from the source record, so no span could be computed. ' +
    '⚠ Named, and still counted in the denominator — an absence with a cause is not the ' +
    'same as a row that was never there.',
  'fetch_ineligible:':
    'This protein was never fetched, so nothing was ever measured about it. ⚠ An unfetched ' +
    'protein is not a protein with no domain — it was not asked. The reason is part of the ' +
    'category name.',
}

// ⚠⚠ 4a — THE GPI BADGE. It shows the attribute AND the limitation TOGETHER and must never read as
// a score, a rank, or a positive signal. GPI status is a DISCLOSED ATTRIBUTE and is not among the
// features; there is no GPI-anchored protein in the ranking set to have learned a coefficient from,
// so any apparent association would be an artifact of the exclusion that kept them out.
export const GPI_BADGE = {
  label: 'GPI-anchored',
  isScore: false,
  tooltip:
    'This protein is attached to the outside of the cell by a lipid anchor rather than by crossing ' +
    'the membrane, so its whole mature chain is extracellular. ⚠ It has no cytoplasmic tail ' +
    '— which means it lacks the internal signals that normally pull a bound antibody into the ' +
    'cell and on to the lysosome, where an ADC’s payload is released. GPI-anchored targets ' +
    'tend to recycle back to the surface instead. Approved ADCs against this class exist (folate ' +
    'receptor alpha), but the field engineers around the problem. This ranking measures ' +
    'extracellular shape and is blind to internalisation, so a high score here does not predict ' +
    'payload delivery.',
}

// The standing limitation line, wherever a rank or a score is displayed.
export const RANK_LIMITATION =
  'Ranks on extracellular geometry. Blind to internalisation, expression level, and antigen copy number.'

export const SPAN_DEFINITION_NOTE =
  'Two span definitions exist in this project and every span states which one produced it. The ' +
  '82-target cohort is frozen under the original definition permanently; the census uses the ' +
  'ruled vocabulary above. ⚠ A count under one definition is not comparable to a count under ' +
  'the other unless both are named.'

export const spanTerm = (term) => SPAN_TERMS.find((t) => t.term === term) || null
export const RULINGS = ['accepted', 'held', 'rejected', 'unruled']
