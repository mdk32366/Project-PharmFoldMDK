// The drift guard (order §2, non-negotiable): the UI's example targets must trace to the
// UniProt-verified source, `data/heldout_positives.csv`.
//
// Why this test rather than a build step: four names is too little to justify a generator, but a
// hand-typed accession is exactly the recall error this project has already been bitten by. So the
// constant is hand-maintained and the DRIFT is what is mechanised — if the CSV changes and the UI
// does not, this reddens. The order permits either method and fixes the guard as mandatory.
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

import { describe, it, expect } from 'vitest'
import { HELDOUT_EXAMPLES, exampleLabel } from './heldoutExamples.js'

const CSV = resolve(dirname(fileURLToPath(import.meta.url)), '../../data/heldout_positives.csv')

function readRows() {
  const text = readFileSync(CSV, 'utf-8')
  const lines = text.split(/\r?\n/).filter((l) => l.trim() && !l.startsWith('#'))
  const header = lines[0].split(',')
  return lines.slice(1).map((l) => {
    // The source_url field has no commas and no quoted fields are used, so a plain split is safe.
    const cells = l.split(',')
    return Object.fromEntries(header.map((h, i) => [h.trim(), (cells[i] ?? '').trim()]))
  })
}

describe('heldout examples trace to the verified CSV', () => {
  const rows = readRows()

  it('the CSV is readable and non-trivial', () => {
    expect(rows.length).toBeGreaterThanOrEqual(4)
    expect(Object.keys(rows[0])).toContain('uniprot_accession')
  })

  it.each(HELDOUT_EXAMPLES)(
    '$display ($gene_symbol / $uniprot_accession) appears in data/heldout_positives.csv',
    (example) => {
      const match = rows.find((r) => r.gene_symbol === example.gene_symbol)
      expect(match, `no row with gene_symbol ${example.gene_symbol} - the UI has drifted from the CSV`).toBeTruthy()
      // The accession is the load-bearing identifier: a wrong one silently misidentifies the protein.
      expect(match.uniprot_accession).toBe(example.uniprot_accession)
    },
  )

  it.each(HELDOUT_EXAMPLES)('$display names an ADC that the CSV also attributes to it', (example) => {
    const match = rows.find((r) => r.gene_symbol === example.gene_symbol)
    expect(match.adc_name.toLowerCase()).toContain(example.adc.toLowerCase())
  })

  it('every example is genuinely OUTSIDE the 82 — that is what makes it an example', () => {
    // The CSV's own build asserts disjointness from the cohort by accession; this asserts the UI is
    // drawing from that file and not from some other list.
    const csvAccessions = new Set(rows.map((r) => r.uniprot_accession))
    for (const e of HELDOUT_EXAMPLES) expect(csvAccessions.has(e.uniprot_accession)).toBe(true)
  })

  it('renders a recognisable label pairing the clinical name with its ADC', () => {
    expect(exampleLabel(HELDOUT_EXAMPLES[0])).toBe('CD30 (brentuximab vedotin)')
  })

  it('⚠ carries no unverified superlative — no "first", no date claim', () => {
    // The project has already been bitten by a "first ADC" slip. Gemtuzumab ozogamicin's 2000
    // approval, 2010 withdrawal and 2017 re-approval make any "the first ADC" phrasing a claim that
    // needs its own source, so the constant deliberately carries none.
    const blob = JSON.stringify(HELDOUT_EXAMPLES)
    expect(blob).not.toMatch(/first/i)
    expect(blob).not.toMatch(/\b(19|20)\d{2}\b/)
  })
})
