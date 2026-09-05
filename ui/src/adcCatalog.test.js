import { describe, expect, it } from 'vitest'
import {
  CANCER_TYPE_ABSENT_COPY,
  PHASE_VOCAB,
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
  it('unwraps envelopes and leaves cancer_type null', () => {
    const flat = flattenAdc(padcev)
    expect(flat.id).toBe('enfortumab-vedotin')
    expect(flat.name).toBe('PADCEV')
    expect(flat.protein).toBe('NECTIN4')
    expect(flat.accession).toBe('Q96NY8')
    expect(flat.cancer_type).toBeNull()
    expect(CANCER_TYPE_ABSENT_COPY).toMatch(/not in catalog v1/)
    expect(CANCER_TYPE_ABSENT_COPY).not.toMatch(/urothelial|breast|myeloma/i)
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

describe('adcCatalog pipeline flatten (D-124)', () => {
  const ifina = {
    id: env('ifinatamab-deruxtecan', { confidence: 'derived' }),
    name: env('ifinatamab deruxtecan', { confidence: 'reviewed' }),
    antigen: env('CD276', { confidence: 'reviewed' }),
    uniprot_accession: env('Q5ZPR3', { confidence: 'reviewed' }),
    development_stage: env('clinical', { confidence: 'reviewed' }),
    phase: env('BLA/NDA submitted', { confidence: 'reviewed' }),
    source_citation: env('PDUFA 2026-10-10', { confidence: 'reviewed' }),
  }
  const phase1 = {
    ...ifina,
    id: env('ly3076226', { confidence: 'derived' }),
    name: env('LY3076226', { confidence: 'reviewed' }),
    phase: env('Phase 1', { confidence: 'reviewed' }),
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
