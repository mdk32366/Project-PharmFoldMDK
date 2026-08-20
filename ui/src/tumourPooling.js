// `D-093 amendment 10` §4 and §5 — the row marker, and the citation gate that governs it.
//
// ⚠⚠ THE RULING: the caveat is a property of a (protein × tumour type) PAIR. It renders ON THE ROW,
// never as a card banner — *a warning that fires on everything is boilerplate within a week, and the
// burden section proved that at ~150 words × 2,690 cards.*
//
// ⚠⚠ NO SOURCE, NO MARKER. `XE` sourced the pooling for **3 of 20** categories. The other 17 are
// `unknown_to_code` and **render NOTHING** — silence, not a hedge. *A marker saying "this may pool
// something" on seventeen rows is the boilerplate the ruling exists to avoid.*
//
// ⚠ AND `INCLUDES`, NEVER `COMPRISES`. HPA names two members and does not claim the set is complete.
// One word, and it is the whole difference between a sourced claim and an inferred one.

/**
 * The three categories HPA itself documents, quoted from
 * `v22.proteinatlas.org/about/assays+annotation` (read 2026-08-21):
 *
 *   "breast cancer includes both ductal and lobular cancer, lung cancer includes both squamous cell
 *    carcinoma and adenocarcinoma and liver cancer includes both hepatocellular and cholangiocellular
 *    carcinoma"
 *
 * ⚠ The `source` travels WITH the claim rather than sitting in a footnote, so a row cannot be
 * rendered without the thing that licenses it.
 */
export const SOURCED_POOLING = {
  'breast cancer': {
    includes: 'ductal and lobular',
    source: 'Human Protein Atlas, Assays and annotation (v22), read 2026-08-21',
  },
  'lung cancer': {
    includes: 'squamous cell carcinoma and adenocarcinoma',
    source: 'Human Protein Atlas, Assays and annotation (v22), read 2026-08-21',
  },
  'liver cancer': {
    includes: 'hepatocellular and cholangiocellular carcinoma',
    source: 'Human Protein Atlas, Assays and annotation (v22), read 2026-08-21',
  },
}

/**
 * §5 — the subtype-defining rows. ⚠ These need the SAME citation gate as everything else.
 *
 * ⚠⚠ THE CLAIM IS ABOUT THE POPULATION, NOT THE TARGET. `D-093` amendment 2 ruling 3's circularity
 * condition is inherited and altered: *"has been developed as an ADC target"* is not evidence the
 * target is good — here it is evidence the pooled category contains a clinically actioned subset.
 *
 * ⚠⚠ AND THE WORDING IS WEAKER THAN THE ENTRY'S EXAMPLE, DELIBERATELY. The entry writes
 * *"NECTIN4 DEFINES the enfortumab-vedotin population"*. What `data/adc_reference_mapping.csv`
 * sources is that an approved ADC TARGETS NECTIN4 (Padcev, BLA 761137) — **not that patients are
 * selected by NECTIN4 expression.** Those are different claims and only the first is in our tree,
 * so only the first is rendered. *Reported to the owner rather than softened silently.*
 */
export const SOURCED_ADC_TARGET = {
  'NECTIN4|urothelial cancer': {
    agent: 'enfortumab vedotin',
    source: 'Padcev US label (BLA 761137) — data/adc_reference_mapping.csv',
  },
  'ERBB2|breast cancer': {
    agent: 'trastuzumab deruxtecan / ado-trastuzumab emtansine',
    source: 'Enhertu and Kadcyla US labels — data/adc_reference_mapping.csv',
  },
}

/** ⚠ Case- and space-insensitive, because HPA free text is the key and it is not normalised. */
const norm = (s) => String(s ?? '').trim().toLowerCase()

/**
 * The marker for one (gene × tumour type) row, or `null` where nothing is sourced.
 *
 * ⚠⚠ Returns SELF-SUFFICIENT text. *A flag that requires a click to mean anything is not a
 * disclosure* — so the sentence says what is pooled, not that something is.
 */
export function poolingMarker(gene, cancer) {
  const pooled = SOURCED_POOLING[norm(cancer)]
  const adc = SOURCED_ADC_TARGET[`${String(gene ?? '').trim().toUpperCase()}|${norm(cancer)}`]
  if (!pooled && !adc) return null              // ⚠ 17 of 20 land here, and render nothing

  const parts = []
  // ⚠ INCLUDES, never COMPRISES — HPA does not claim the set is complete
  if (pooled) parts.push(`pooled — includes ${pooled.includes}`)
  if (adc) parts.push(`an approved ADC targets ${gene} (${adc.agent}); this panel does not separate the treated population`)
  return {
    text: parts.join('; '),
    sources: [pooled?.source, adc?.source].filter(Boolean),
  }
}
