import { describe, expect, it } from 'vitest'
import {
  CANCER_TYPE_ABSENT_COPY,
  PHASE_VOCAB,
  PIPELINE_CANCER_TYPE_ABSENT_COPY,
  PIPELINE_DESCRIPTION_ABSENT_COPY,
  PIPELINE_INDEX_COLUMNS,
  absenceCopy,
  cancerTypeAbsenceCopy,
  cancerTypes,
  filterPipelineByPhase,
  flattenAdc,
  flattenCatalog,
  flattenPipeline,
  flattenPipelineRow,
  headerValue,
  isEnvelope,
  looksLikeUrl,
} from './adcCatalog.js'

const env = (value, extras = {}) => ({
  value,
  source: extras.source ?? 'fixture',
  as_of: extras.as_of ?? '2026-09-05',
  confidence: extras.confidence ?? 'official',
})

const padcev = {
  id: env('enfortumab-vedotin', { confidence: 'derived' }),
  inn: env('enfortumab vedotin', { confidence: 'derived' }),
  brand_name: env('PADCEV'),
  antigen: env('NECTIN4', { confidence: 'reviewed' }),
  uniprot_accession: env('Q96NY8', { confidence: 'reviewed' }),
}

describe('adcCatalog flatten (D-122)', () => {
  it('unwraps envelopes', () => {
    const flat = flattenAdc(padcev)
    expect(flat.id).toBe('enfortumab-vedotin')
    expect(flat.name).toBe('PADCEV')
    expect(flat.protein).toBe('NECTIN4')
    expect(flat.accession).toBe('Q96NY8')
  })

  it('does not treat a bare string as an envelope', () => {
    expect(isEnvelope('PADCEV')).toBe(false)
    expect(isEnvelope({ value: 'x' })).toBe(false)
    expect(isEnvelope(env('PADCEV'))).toBe(true)
  })

  it('row count is the payload length, not a typed constant', () => {
    const catalog = {
      scope: env('fda_approved_only'),
      adcs: [padcev, { ...padcev, id: env('ado-trastuzumab-emtansine'), brand_name: env('KADCYLA') }],
    }
    expect(flattenCatalog(catalog)).toHaveLength(2)
    expect(headerValue(catalog, 'scope')).toBe('fda_approved_only')
    expect(flattenCatalog({})).toHaveLength(0)
  })
})

describe('adcCatalog cancer type (D-136)', () => {
  const withTypes = (value, extras = {}) => ({
    ...padcev,
    cancer_type: env(value, { confidence: 'reviewed', ...extras }),
  })

  it('reads the tumour types off the envelope as a real sort key', () => {
    const flat = flattenAdc(withTypes(['Urothelial cancer', 'Muscle invasive bladder cancer']))
    expect(flat.cancer_types).toEqual(['Urothelial cancer', 'Muscle invasive bladder cancer'])
    expect(flat.cancer_type).toBe('Urothelial cancer; Muscle invasive bladder cancer')
  })

  it('⚠ an absent cancer type sorts as null, never as an empty string', () => {
    // '' would sort ahead of every real category — the `?? 0` mistake in a
    // different costume. `sortRows` only trails a row it can see is absent.
    const flat = flattenAdc(withTypes(null))
    expect(flat.cancer_type).toBeNull()
    expect(flat.cancer_types).toEqual([])
    expect(flattenAdc(padcev).cancer_type).toBeNull()
  })

  it('an absent row renders its OWN source, not one page-wide sentence', () => {
    const source = 'openFDA SPL label.json for FIXTURE returned no indications_and_usage'
    expect(cancerTypeAbsenceCopy(env(null, { source }))).toBe(source)
  })

  it('falls back to the shared copy only when there is no source at all', () => {
    expect(cancerTypeAbsenceCopy(null)).toBe(CANCER_TYPE_ABSENT_COPY)
    expect(cancerTypeAbsenceCopy(env(null, { source: '  ' }))).toBe(CANCER_TYPE_ABSENT_COPY)
    expect(CANCER_TYPE_ABSENT_COPY).not.toMatch(/urothelial|breast|myeloma/i)
  })

  it('a bare string is not a tumour-type list', () => {
    expect(cancerTypes(withTypes('Urothelial cancer'))).toEqual([])
    expect(cancerTypes({ ...padcev, cancer_type: ['Urothelial cancer'] })).toEqual([])
  })
})

describe('adcCatalog pipeline flatten (D-124)', () => {
  const ifina = {
    id: env('ifinatamab-deruxtecan', { confidence: 'derived' }),
    name: env('ifinatamab deruxtecan', { confidence: 'reviewed' }),
    antigen: env('CD276', { confidence: 'reviewed' }),
    uniprot_accession: env('Q5ZPR3', { confidence: 'reviewed' }),
    development_stage: env('clinical', { confidence: 'reviewed' }),
    phase: env('BLA/NDA submitted', { confidence: 'reviewed' }),
    source_citation: env('PDUFA 2026-10-10', { confidence: 'reviewed' }),
    cancer_type: env(['Small-cell lung cancer'], { confidence: 'reviewed' }),
    conditions_verbatim: env('Extensive-stage Small-cell Lung Cancer', { confidence: 'official' }),
    description: env('Daiichi Sankyo/Merck — I-DXd, a CD276-directed conjugate.', {
      confidence: 'reviewed',
    }),
  }
  const phase1 = {
    ...ifina,
    id: env('ly3076226', { confidence: 'derived' }),
    name: env('LY3076226', { confidence: 'reviewed' }),
    phase: env('Phase 1', { confidence: 'reviewed' }),
    cancer_type: {
      value: null,
      source: 'NCT02529553 Conditions name no tumour, 2026-09-08',
      as_of: '2026-09-08',
      confidence: 'reviewed',
    },
    description: {
      value: null,
      source: 'no maker named, 2026-09-08',
      as_of: '2026-09-08',
      confidence: 'reviewed',
    },
  }

  it('unwraps pipeline envelopes and keeps the closed phase token', () => {
    const flat = flattenPipelineRow(ifina)
    expect(flat.id).toBe('ifinatamab-deruxtecan')
    expect(flat.name).toBe('ifinatamab deruxtecan')
    expect(flat.protein).toBe('CD276')
    expect(flat.phase).toBe('BLA/NDA submitted')
    expect(PHASE_VOCAB).toEqual([
      'Phase 1', 'Phase 1/2', 'Phase 2', 'Phase 3', 'BLA/NDA submitted', 'Other',
    ])
  })

  it('D-140 — pipeline rows carry a cancer-type sort key and a description', () => {
    const flat = flattenPipelineRow(ifina)
    expect(flat.cancer_types).toEqual(['Small-cell lung cancer'])
    expect(flat.cancer_type).toBe('Small-cell lung cancer')
    expect(flat.description).toBe('Daiichi Sankyo/Merck — I-DXd, a CD276-directed conjugate.')
    expect(PIPELINE_INDEX_COLUMNS.map((c) => c.key)).toEqual([
      'name', 'cancer_type', 'phase', 'protein', 'description',
    ])
  })

  it('D-140 — a named absence sorts as null, never as the empty string', () => {
    const flat = flattenPipelineRow(phase1)
    // ⚠ `null`, not `''`. An empty string would sort as the alphabetically-first
    // real value instead of trailing as a category (D-087).
    expect(flat.cancer_type).toBeNull()
    expect(flat.description).toBeNull()
    expect(flat.cancer_types).toEqual([])
    // The cell renders the envelope's OWN source, not the page-wide fallback.
    expect(absenceCopy(flat.cancer_type_field, PIPELINE_CANCER_TYPE_ABSENT_COPY))
      .toMatch(/NCT02529553 Conditions name no tumour/)
    expect(absenceCopy(flat.description_field, PIPELINE_DESCRIPTION_ABSENT_COPY))
      .toMatch(/no maker named/)
    // …and falls back only when there is no envelope at all.
    expect(absenceCopy(null, PIPELINE_DESCRIPTION_ABSENT_COPY))
      .toBe(PIPELINE_DESCRIPTION_ABSENT_COPY)
  })

  it('filters by phase and treats all as the unfiltered set', () => {
    const rows = flattenPipeline({ pipeline: [ifina, phase1] })
    expect(filterPipelineByPhase(rows, 'all')).toHaveLength(2)
    expect(filterPipelineByPhase(rows, 'Phase 1').map((r) => r.id)).toEqual(['ly3076226'])
    expect(filterPipelineByPhase(rows, 'Phase 3')).toEqual([])
    expect(flattenPipeline({})).toHaveLength(0)
  })

  it('does not treat a bare string as an access URL', () => {
    expect(looksLikeUrl('https://clinicaltrials.gov/')).toBe(true)
    expect(looksLikeUrl('21 U.S.C. § 360bbb-0a')).toBe(false)
    expect(looksLikeUrl(null)).toBe(false)
  })
})
