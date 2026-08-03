// Example clinically-validated ADC targets that fall OUTSIDE the Kathad 82 (F-009).
//
// ⚠ THIS FILE IS NOT AUTHORITATIVE AND MUST NOT DRIFT. The authoritative source is
// `data/heldout_positives.csv`, whose accessions were resolved live from the UniProt REST API
// (never recalled — that discipline caught `TF` resolving to serotransferrin rather than tissue
// factor, and `PSMA`/`FOLH1` collapsing to one accession). `heldoutExamples.test.js` asserts every
// `gene_symbol` + `uniprot_accession` below appears in that CSV, so the UI and the verified data
// cannot silently disagree. If the CSV changes and this does not, the gate reddens.
//
// Four examples, not the whole set: the point is to show the comparator has blind spots, and four
// named targets a reader can check does that. The full 20-row set is the CSV.
//
// ⚠ `display` is the clinical name a reader will recognise (CD30, Trop-2); `gene_symbol` is UniProt's
// PRIMARY symbol, which is often different (TNFRSF8, TACSTD2). Both are carried because showing only
// the gene symbol would make these targets unrecognisable to a clinician, and showing only the
// clinical name would break the trace back to the verified source.
export const HELDOUT_EXAMPLES = [
  { display: 'CD30', gene_symbol: 'TNFRSF8', uniprot_accession: 'P28908', adc: 'brentuximab vedotin' },
  { display: 'CD33', gene_symbol: 'CD33', uniprot_accession: 'P20138', adc: 'gemtuzumab ozogamicin' },
  { display: 'CEACAM5', gene_symbol: 'CEACAM5', uniprot_accession: 'P06731', adc: 'tusamitamab ravtansine' },
  { display: 'Trop-2', gene_symbol: 'TACSTD2', uniprot_accession: 'P09758', adc: 'sacituzumab govitecan' },
]

/** "CD30 (brentuximab vedotin)" — the rendered form, so both placements read identically. */
export const exampleLabel = (e) => `${e.display} (${e.adc})`
