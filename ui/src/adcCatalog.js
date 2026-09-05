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
