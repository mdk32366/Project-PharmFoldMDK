import { describe, expect, it } from 'vitest'
import {
  CANCER_TYPE_ABSENT_COPY,
  flattenAdc,
  flattenCatalog,
  headerValue,
  isEnvelope,
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
