// D-122 — flatten the D-119 catalog for the ADC-B index / baseball card.
//
// Every catalog field is a `{value, source, as_of, confidence}` envelope (D-119).
// A bare string is not data. This module unwraps envelopes for SORT KEYS only;
// the rendered surfaces still show the full envelope.
//
// D-136 — cancer type is now a v1 field, filled from FDA's own SPL §1
// INDICATIONS AND USAGE text and audited in `core/adc_catalog.py` against the
// official text stored on the same row. So the column carries real categories
// where the label states them. What has NOT changed: nothing here invents a
// tumour type, and nothing here joins HPA / census staining (D-093: staining ≠
// FDA indication). A row whose envelope is a named absence renders that
// absence's own source — never a blank, never a guess.

// D-136 — the fallback for a row whose `cancer_type` envelope is a named
// absence and carries no source of its own. Before D-136 this was every row.
export const CANCER_TYPE_ABSENT_COPY =
  'not stated on the FDA label text this catalog holds for this row (D-136)'

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
 * The tumour types on one row, as a list. `[]` when the envelope is a named
 * absence — never a placeholder string masquerading as a category.
 */
export function cancerTypes(row) {
  const value = fieldValue(row?.cancer_type)
  return Array.isArray(value) ? value.filter((t) => typeof t === 'string' && t.trim()) : []
}

/**
 * The `cancer_type` sort key: the tumour types joined, or `null` when absent.
 *
 * ⚠ `null`, not `''`. `sortRows` holds absent-valued rows out as a trailing
 * cluster in both directions; an empty string would sort them as the
 * alphabetically-first real category, which is the `?? 0` mistake in a
 * different costume (D-087).
 */
export function cancerTypeSortKey(row) {
  const types = cancerTypes(row)
  return types.length ? types.join('; ') : null
}

/**
 * One index row. `cancer_type` is a real sort key where the FDA label states a
 * tumour type (D-136) and `null` where it does not.
 */
export function flattenAdc(row) {
  if (!row) return null
  return {
    id: fieldValue(row.id),
    name: fieldValue(row.brand_name),
    inn: fieldValue(row.inn),
    protein: fieldValue(row.antigen),
    accession: fieldValue(row.uniprot_accession),
    cancer_type: cancerTypeSortKey(row),
    cancer_types: cancerTypes(row),
    cancer_type_field: row.cancer_type ?? null,
    row,
  }
}

/**
 * What to render where a row states no tumour type: the envelope's OWN source,
 * so the reader learns which query came back without indication text rather
 * than reading one page-wide sentence that cannot be wrong (D-136 decision 6).
 * Falls back to the shared copy only when the row carries no source at all.
 */
export function cancerTypeAbsenceCopy(field) {
  const source = isEnvelope(field) ? field.source : null
  return typeof source === 'string' && source.trim() ? source : CANCER_TYPE_ABSENT_COPY
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
