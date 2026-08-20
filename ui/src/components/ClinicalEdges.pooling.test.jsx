import { render } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import ClinicalEdges from './ClinicalEdges.jsx'
import { poolingMarker, SOURCED_POOLING } from '../tumourPooling.js'

// `D-093 amendment 10` §4 and §5 — the row marker.
//
// ⚠⚠ THE RULING'S THREE HARD EDGES, each with a test:
//   1. it renders ON THE ROW, never as a card banner
//   2. where NOT sourced — 17 of 20 — it renders NOTHING. Silence, not a hedge
//   3. `INCLUDES`, never `COMPRISES` — one word, and it is the whole difference between a sourced
//      claim and an inferred one, because HPA does not claim its set is complete

const block = (gene, tumours) => ({
  status: 'ihc_present', gene, layers: [], tumours,
  normal_tissues: [{ tissue: 'skin 1', highest: 'High', cell_types: 3, detected_in: 2 }],
  source: 'HPA v22.', boundary: 'Immunohistochemistry.',
})
const T = (cancer, pos, n) => ({ cancer, patients_tested: n, patients_positive: pos,
                                 high: 1, medium: 1, low: 0, not_detected: n - pos })
const draw = (b) => render(<ClinicalEdges block={b} />).container

describe('§4 — the marker is a property of the ROW', () => {
  it('renders inside the tumour row, not as a card banner', () => {
    const c = draw(block('ERBB2', [T('breast cancer', 11, 11)]))
    const li = c.querySelector('.clin-tumours li')
    expect(li.querySelector('.clin-pooled')).not.toBeNull()
    // ⚠ nothing outside the list carries it — a banner would fire on everything
    const outside = [...c.querySelectorAll('.clin-pooled')].filter((e) => !e.closest('li'))
    expect(outside).toEqual([])
  })

  it('is self-sufficient — it says WHAT is pooled, not that something is', () => {
    // ⚠⚠ "A flag that requires a click to mean anything is not a disclosure."
    const c = draw(block('ERBB2', [T('breast cancer', 11, 11)]))
    const t = c.querySelector('.clin-pooled').textContent
    expect(t).toMatch(/ductal and lobular/)
    expect(t.trim()).not.toBe('⚠ pooled')
  })

  it('⚠⚠ says INCLUDES and never COMPRISES', () => {
    // HPA names two members and does not claim the set is complete. One word.
    for (const cancer of Object.keys(SOURCED_POOLING)) {
      const m = poolingMarker('ANY', cancer)
      expect(m.text).toMatch(/includes/i)
      expect(m.text).not.toMatch(/comprises|consists of|is made up of/i)
    }
  })

  it('carries its source with the claim', () => {
    const c = draw(block('ERBB2', [T('breast cancer', 11, 11)]))
    expect(c.querySelector('.clin-pooled').getAttribute('title')).toMatch(/Human Protein Atlas/)
  })
})

describe('§4 — where nothing is sourced, the marker renders NOTHING', () => {
  // ⚠⚠ 17 of 20 land here. `unknown_to_code` is silence, not a hedge.
  const UNSOURCED = ['glioma', 'head and neck cancer', 'skin cancer', 'carcinoid',
                     'thyroid cancer', 'ovarian cancer', 'stomach cancer']

  it.each(UNSOURCED)('is silent on %s', (cancer) => {
    expect(poolingMarker('SOMEGENE', cancer)).toBeNull()
    const c = draw(block('SOMEGENE', [T(cancer, 5, 11)]))
    expect(c.querySelector('.clin-pooled')).toBeNull()
  })

  it('never hedges — no "may pool" anywhere on an unsourced row', () => {
    const c = draw(block('SOMEGENE', [T('glioma', 5, 11)]))
    expect(c.textContent).not.toMatch(/may pool|possibly pooled|might pool/i)
  })

  it('leaves the unsourced row otherwise untouched', () => {
    const c = draw(block('SOMEGENE', [T('glioma', 5, 11)]))
    expect(c.querySelector('.clin-tumours li').textContent).toMatch(/5 of 11 samples stained/)
  })
})

describe('§5 — the subtype-defining row claims about the POPULATION', () => {
  it('names the therapy and says the panel does not separate it', () => {
    const c = draw(block('NECTIN4', [T('urothelial cancer', 8, 12)]))
    const t = c.querySelector('.clin-pooled').textContent
    expect(t).toMatch(/enfortumab vedotin/)
    expect(t).toMatch(/does not separate the treated population/)
  })

  // ⟡ THE ENTRY MOVED TO MATCH THIS, not the other way round (owner, 2026-08-21).
  // §5 was first written as "NECTIN4 DEFINES the enfortumab-vedotin population". That claim is not
  // sourced in this tree — `adc_reference_mapping.csv` sources that an approved ADC TARGETS NECTIN4,
  // not that patients are selected by its expression. The surface rendered only the sourced claim,
  // the divergence was reported, and §5 was amended with its original wording preserved.
  // ⚠⚠ This assertion is therefore not a concession to a weaker source — it PINS the ruling.
  it('does not claim the target DEFINES the treated population', () => {
    const t = poolingMarker('NECTIN4', 'urothelial cancer').text
    expect(t).not.toMatch(/defines the/i)
    expect(t).toMatch(/an approved ADC targets/i)
  })

  it('⚠ the claim is about the population, not a verdict on the target', () => {
    // D-093 amendment 2 ruling 3: therapeutic_precedent is a LABEL, never a FEATURE, and
    // "has been developed as an ADC target" is not evidence the target is good.
    const t = poolingMarker('NECTIN4', 'urothelial cancer').text
    expect(t).not.toMatch(/good|promising|validated|strong candidate/i)
  })

  it('is silent for a gene with no sourced ADC in that tumour type', () => {
    // ⚠ FGFR3 is in the crosswalk's four but its urothelial ADC row is clinical, not approved —
    // and no population claim is sourced, so the pair renders nothing on that axis.
    const m = poolingMarker('FGFR3', 'urothelial cancer')
    expect(m).toBeNull()
  })
})

describe('the two markers compose on one row without repeating', () => {
  it('ERBB2 in breast carries the pooling AND the ADC clause, once each', () => {
    const t = poolingMarker('ERBB2', 'breast cancer').text
    expect(t).toMatch(/includes ductal and lobular/)
    expect(t).toMatch(/an approved ADC targets ERBB2/)
    expect(t.match(/includes/gi)).toHaveLength(1)
  })
})
