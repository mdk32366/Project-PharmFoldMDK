// D-122 — flatten the D-119 catalog for the ADC-B index / baseball card.
//
// Every catalog field is a `{value, source, as_of, confidence}` envelope (D-119).
// A bare string is not data. This module unwraps envelopes for SORT KEYS only;
// the rendered surfaces still show the full envelope.
//
// ⚠ Cancer type is NOT a v1 field (D-119 decision 8). The Spec asked the index
// to sort name / cancer type / protein, so the column exists as an honest
// absence — never a guessed indication, never an HPA join (D-093: staining ≠
// FDA indication).

export const CANCER_TYPE_ABSENT_COPY =
  'not in catalog v1 — indication is not an ADC-A field (D-119)'

export const DEFAULT_SORT = { key: 'name', dir: 'asc' }

export const INDEX_COLUMNS = [
  { key: 'name', label: 'Name' },
  { key: 'cancer_type', label: 'Cancer type' },
  { key: 'protein', label: 'Protein' },
]

/** Is this a D-119 provenance envelope? */
export function isEnvelope(obj) {
  return Boolean(
    obj
    && typeof obj === 'object'
    && 'value' in obj
    && 'source' in obj
    && 'as_of' in obj
    && 'confidence' in obj,
  )
}

export function fieldValue(field) {
  return isEnvelope(field) ? field.value : null
}

/**
 * One index row. `cancer_type` is null so `sortRows` holds every row in the
 * absent cluster — a same-category sort, not a fabricated indication.
 */
export function flattenAdc(row) {
  if (!row) return null
  return {
    id: fieldValue(row.id),
    name: fieldValue(row.brand_name),
    inn: fieldValue(row.inn),
    protein: fieldValue(row.antigen),
    accession: fieldValue(row.uniprot_accession),
    cancer_type: null,
    row,
  }
}

export function flattenCatalog(catalog) {
  const rows = Array.isArray(catalog?.adcs) ? catalog.adcs : []
  return rows.map(flattenAdc).filter((r) => r && r.id)
}

export function headerValue(catalog, key) {
  return fieldValue(catalog?.[key])
}

export const INVENTED_SCIENCE = ['DAR', 'IC50', 'ORR', 'PFS', 'OS', 'payload', 'linker']
export const OUT_OF_SCOPE_ROW_IDS = [
  'lumoxiti',
  'moxetumomab-pasudotox',
  'ifinatamab-deruxtecan',
  'right-to-try',
  'pipeline',
]

// D-124 / ADC-C-A closed phase vocab. The Pipeline filter may use these
// tokens and an All-phases default — nothing else, and never a guessed
// "Phase 0" / "preclinical" / "approved" token.
export const PHASE_VOCAB = [
  'Phase 1',
  'Phase 1/2',
  'Phase 2',
  'Phase 3',
  'BLA/NDA submitted',
  'Other',
]

export const PIPELINE_INDEX_COLUMNS = [
  { key: 'name', label: 'Name' },
  { key: 'phase', label: 'Phase' },
  { key: 'protein', label: 'Protein' },
]

export const PIPELINE_SHELF = 'pipeline'
export const APPROVED_SHELF = 'approved'

export function flattenPipelineRow(row) {
  if (!row) return null
  return {
    id: fieldValue(row.id),
    name: fieldValue(row.name),
    protein: fieldValue(row.antigen),
    accession: fieldValue(row.uniprot_accession),
    stage: fieldValue(row.development_stage),
    phase: fieldValue(row.phase),
    citation: fieldValue(row.source_citation),
    row,
  }
}

export function flattenPipeline(catalog) {
  const rows = Array.isArray(catalog?.pipeline) ? catalog.pipeline : []
  return rows.map(flattenPipelineRow).filter((r) => r && r.id)
}

/** `all` (or empty) keeps every row. Any other token must be in PHASE_VOCAB. */
export function filterPipelineByPhase(rows, phase) {
  if (!phase || phase === 'all') return rows
  return rows.filter((r) => r.phase === phase)
}

export function looksLikeUrl(value) {
  return typeof value === 'string' && /^https?:\/\//i.test(value)
}
