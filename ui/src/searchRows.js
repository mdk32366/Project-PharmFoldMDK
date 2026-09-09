// Free-text row search, shared by every surface that lists proteins.
//
// ⚠⚠ WHY THIS IS A MODULE AND NOT A SECOND COPY. These two functions lived inside `CensusTable.jsx`,
// so the census could find `HER2` and `/targets` could not — `ERBB2` is folded and ranked there, and
// the owner searched for it by the name on the drug label and found nothing. **`F-052` is exactly
// this shape**: a convention that exists, is documented, and is obeyed by every caller except the
// newest one. Copying the matcher into `TargetList.jsx` would have closed the symptom and widened
// the finding, so the matcher moved here and both surfaces import it.
//
// ⚠ `sortRows.js` is the precedent — ordering logic extracted, tested in isolation, imported by the
// surfaces. This is the same move for matching.

// Fold a typed name to its comparable core: upper-case, punctuation and spaces removed. So `CD-30`,
// `cd 30` and `CD30` are one query, and `HER-2` reaches `HER2`.
export function normalizeQuery(text) {
  return String(text ?? '').toUpperCase().replace(/[^A-Z0-9]+/g, '')
}

// ⚠⚠ THE NAME PEOPLE KNOW IS OFTEN NOT THE NAME WE STORE. Both populations are keyed on HGNC
// symbols; the ADC field speaks in CD numbers and receptor families. `CD30` is stored as `TNFRSF8`
// and `HER2` as `ERBB2` — both read as MISSING to anyone who searches the name on the drug label.
// Aliases come from the pinned UniProt cache (`core/protein_aliases.py`), never typed.
// ⚠ An alias is a way IN, not a second identity: matching one does not rename the row.
// ⚠ `aliases` absent (a payload that never carried them) degrades to accession/gene/label matching.
// It does NOT throw, and it does not claim the protein has no other names.
// ⚠⚠ `description` IS MATCHED TOO (D-143), and it is the same finding one more time. The census
// searches protein names already — its `label` IS the protein name — while `/targets`, whose
// `label` is the gene symbol, could not. So the surface that just gained a Description column would
// have rendered 82 protein names that its own search box could not find: `F-052`'s shape, in the
// PR that created the values. ⚠ A row without the key is unaffected (census rows carry no
// `description`), so this widens one population's reach and changes the other's behaviour not at
// all — and it is a way IN, never a second identity.
export function filterRows(rows, query) {
  const raw = String(query ?? '').trim().toLowerCase()
  if (!raw) return rows
  const q = normalizeQuery(query)
  return rows.filter((r) => {
    // the original substring behaviour is preserved for names with spaces and punctuation
    if ([r.accession, r.gene, r.label, r.description].some(
      (v) => v && String(v).toLowerCase().includes(raw))) {
      return true
    }
    if (!q) return false
    return [r.accession, r.gene, r.label, r.description, ...(r.aliases ?? [])].some(
      (v) => v && normalizeQuery(v).includes(q),
    )
  })
}
