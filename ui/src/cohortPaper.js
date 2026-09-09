// D-151 — the cohort paper's citation, in ONE place on the UI side.
//
// ⚠⚠ THE PAPER WAS NAMED ON THREE SURFACES AND HYPERLINKED ON NONE. `/targets`'s own copy, the
// Scorer cascade and `/about` all print "Kathad et al." as plain text, so the one artefact this
// project's whole cohort comes from was un-openable from the application that re-orders it. The
// DOI existed in the repository — `data/cohort_82.txt`, `data/cancer_associations.csv`,
// `core/cancer_associations.py`'s `SOURCE` — and in no rendered surface.
//
// ⚠ ONE CONSTANT, because the alternative is the shape this project keeps paying for: a DOI typed
// at each of three call sites is three strings free to disagree, and a citation that disagrees
// with itself is worse than an absent one — it cannot be told from a link to a different paper.
// `cohortPaper.test.js` pins these strings against `data/cohort_82.txt`, the committed source of
// truth for the cohort, so a drift here fails on a file read rather than on someone noticing.
//
// ⚠ NOT the HPA citation. `HpaAttribution.jsx` carries the Human Protein Atlas's four licence
// elements and this is a different obligation about a different source — D-100 records that
// Kathad's S3 is a verbatim extract of HPA's `pathology.tsv`, and citing the paper is expressly
// NOT citing HPA. Neither citation stands in for the other, and they are kept in separate modules
// so no later edit can quietly merge them.
export const COHORT_PAPER_DOI = '10.1371/journal.pone.0308604'
export const COHORT_PAPER_URL = `https://doi.org/${COHORT_PAPER_DOI}`
export const COHORT_PAPER_SHORT = 'Kathad et al. 2024'
export const COHORT_PAPER_CITATION =
  'Kathad et al. 2024, PLOS ONE 10.1371/journal.pone.0308604 (CC-BY)'
// ⚠ the committed file the strings above are pinned against — a path, so the test names its artefact
export const COHORT_SOURCE_PATH = 'data/cohort_82.txt'
