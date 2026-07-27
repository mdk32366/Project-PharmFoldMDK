// D-055: the term glossary. Definitions are LITERALS (D-053 dec 5: a definition doesn't change if
// our data does, so it needs no route). Two registers (D-055 dec 1): biology/oncology/chemistry in
// plain ~8th-grade language for a reader who has no background there; machine-learning terms at peer
// level (the reader teaches ML). pLDDT sits on the boundary and gets both — the precise form in
// `expansion`, the plain one in `plain`.
//
// Each entry: `expansion` (what the letters stand for / the precise name) and `plain` (one
// jargon-free sentence). The register split is a HUMAN judgement — no test enforces which register
// a term got (D-055 dec 1, stated so the green contract test is not over-read).
export const GLOSSARY = {
  pLDDT: {
    expansion: 'per-residue predicted confidence (predicted Local Distance Difference Test)',
    plain: "the model's own score, 0–100, for how sure it is about each piece of the structure it predicted",
  },
  PAE: {
    expansion: 'Predicted Aligned Error',
    plain: 'the model’s estimate of how far two parts of the structure could be misplaced relative to each other',
  },
  ESMFold: {
    expansion: 'Evolutionary Scale Modeling — the folding model',
    plain: 'the neural network we run ourselves to predict a protein’s 3D shape from its amino-acid sequence',
  },
  ECD: {
    expansion: 'extracellular domain',
    plain: 'the part of a protein that sticks out of the cell, where an antibody can reach it',
  },
  ADC: {
    expansion: 'antibody–drug conjugate',
    plain: 'a cancer drug that uses an antibody to carry a toxic payload straight to a tumour cell',
  },
  'quasi H-score': {
    expansion: 'quasi histochemical score (0–300)',
    plain: 'a 0–300 score for how strongly a protein shows up in a tumour type, taken from the source paper',
  },
  TCGA: {
    expansion: 'The Cancer Genome Atlas',
    plain: 'a large public dataset of molecular measurements from real tumours',
  },
  IHC: {
    expansion: 'immunohistochemistry',
    plain: 'a lab technique that stains tissue to show how much of a protein is present',
  },
  HPA: {
    expansion: 'the Human Protein Atlas',
    plain: 'a public database of where proteins appear across human tissues',
  },
  int8: {
    expansion: '8-bit integer precision',
    plain: 'a compact number format that shrinks the model so it fits in limited GPU memory',
  },
  fp16: {
    expansion: '16-bit floating-point precision',
    plain: 'a half-size number format the rented GPU uses to fold larger proteins',
  },
  GPU: {
    expansion: 'graphics processing unit',
    plain: 'the accelerator hardware the neural network runs on',
  },
  '3Dmol': {
    expansion: '3Dmol.js',
    plain: 'the in-browser viewer that draws the folded 3D structure',
  },
}

// The contract-test watchlist (D-055 dec 3, via the orders §5.1 fallback): the acronyms a reader
// actually meets that MUST be decodable. Scanning ALL rendered tokens is impractical here — rendered
// copy also carries decision references (D-045, DEP-001, …), UniProt accessions (Q96NY8), cancer
// names and units, none of which are glossary terms and none cleanly exemptible without weakening
// the assertion. So the contract is this curated set, not an open scan. Every term here MUST have a
// GLOSSARY entry, and any that reaches a rendered surface MUST be defined there.
// Independent of GLOSSARY on purpose: this is "the acronyms the UI puts on screen," and GLOSSARY is
// "the acronyms we've defined." The contract test reddens when a MUST_DEFINE term is rendered but
// absent from GLOSSARY — so this list must NOT be derived from GLOSSARY's keys, or it could never
// disagree with them and the test could never bite.
export const MUST_DEFINE = [
  'pLDDT', 'PAE', 'ESMFold', 'ECD', 'ADC', 'quasi H-score',
  'TCGA', 'IHC', 'HPA', 'int8', 'fp16', 'GPU', '3Dmol',
]

export const lookup = (term) => GLOSSARY[term] || null
