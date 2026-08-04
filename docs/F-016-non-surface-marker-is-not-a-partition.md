# F-016 — The `Non_Surface` marker in the reconstructed Table S3 is a section heading, not a partition: everything below it is the **whole** membraneome, and splitting on row position mislabels all 2,886 surface identifiers as negatives

> **Type:** A finding about a file we were about to read positionally, caught before any census was
> built on it. Nothing is ruled here. No behaviour changed; one data artifact is written and one
> script default is removed.
> **Date:** 2026-08-04.
> **Number:** F-016. F-001–F-010 and F-012 are defined in `docs/README.md`; F-011 is staged;
> F-013/F-014/F-015 are reserved in `RESERVED.md`. F-016 is the next free integer, **written**.
>
> ⚠ **Conformed to `RULINGS-2026-08-04-F016-membraneome.md`** (§1 keys · §2 three classes ·
> §3 no implicit source · §4 CSV is the source of record · §5 buckets · §6 sequencing).
>
> ## ⛔ MERGE GATE — rulings §6.1, and it is currently CLOSED
>
> **`### F-011` is NOT in `docs/README.md`.** Checked by header grep, not by filename: F-011 exists
> only as a staged document. **F-016 discharges F-011's flags, and an entry cannot discharge flags
> in an entry that does not exist.** F-016 therefore merges **with F-011 or after it, never before.**

---

## Provenance of every number — ⚠ each with its key (rulings §1)

**A count with no key is incomplete.** *Identifiers* and *distinct proteins* are different
quantities, and only one of them is a denominator.

| Number | Key | Status | How known |
|---|---|---|---|
| **2,886** surface | identifiers | ✅ **VERIFIED THREE WAYS** | Counted from the file; set-identical to `surfaceome_ids.txt` (sha256 `8a7b7e68…`, 0 differences either direction); matches the figure published on `wollscheidlab.org/SURFY`. |
| **2,807** surface | **distinct accessions** | ✅ **COUNTED — the denominator** | Table accessions mapped to current UniProt primaries, 2026-08-04. |
| **2,216** non_surface | identifiers | ✅ **VERIFIED FROM THE FILE, and externally** | Counted off column `Surfy`; **exactly** the figure the SURFY site states. ⟡ **Discharges the F-011 flag** — F-011 could only cite it from a figure legend. |
| **2,801** unclassified | identifiers | ✅ **VERIFIED FROM THE FILE** | Rows whose `Surfy` cell is **blank** — neither class. Published nowhere. Newly counted. |
| **7,903** membraneome | identifiers | ✅ **VERIFIED FROM THE FILE** | Row count below the marker. ⚠ **No external corroboration** — the site publishes no total. |
| **7,811** membraneome | distinct accessions | ✅ **COMPUTED** | After collapsing merged accessions. |
| ~~**~5,102**~~ | — | ❌ **SUPERSEDED** | F-011's arithmetic (2,886 + 2,216). The *classified subset*, not the table. |
| **132-byte stub** | — | ✅ **RE-VERIFIED TODAY** | Both copies in `Downloads` hash to `f3df0fa8…`, magic bytes `vers` not `PK` — matching `data/census/PROVENANCE.md`. The upstream table is **still** unobtainable. |

---

## The finding

`Table S3 Surfaceome Reconstructed.xlsx` carries a single cell reading `Non_Surface` at row 2888,
followed by a blank row. It reads as a partition: surface above, non-surface below.

**It is not a partition. It is a section heading, and the section it heads is the entire table.**

| Rows | What is actually there | Count |
|---|---|---|
| 2 – 2887 | A surface-only extract — a preamble | 2,886 |
| **2888** | the cell `Non_Surface` | — |
| 2889 | blank | — |
| 2890 – 10792 | **the full human membraneome, all three classes** | 7,903 |

All 2,886 surface rows appear **again** below the marker — **field-for-field identical, zero
differences** across accession, gene, `Surfy`, and `Surfy Score`. The file is a 2,886-row extract
stacked on the complete 7,903-row table. That is exactly what the SURFY site says the artifact is:
*"Detailed table for the full human membraneome."*

### Why this bites

**Splitting on row position labels 2,886 surface proteins SURFY-negative** — the precise inversion
`core/census.py` and `scripts/census_spans.py` exist to prevent. F-011's annex rows must be
*ingested and flagged, never ranked*; a positional split fills the negative flag with the entire
positive class.

**And the negative class is not the complement.** It is **2,216** explicit `non_surface` plus
**2,801** rows with a **blank** `Surfy` cell. Those are different objects: one is the classifier
calling non-surface, the other is the classifier **not having spoken**. Treating "not positive" as
negative fuses them and **inflates the negative class by 126%** (5,017 vs 2,216).

⚠ **Three classes, always named: `surface` · `non_surface` · `unclassified`.** `unclassified` is
never merged into either and never dropped. **It is also not evidence for F-011** — those rows are
unexamined by a different mechanism, and recruiting them because a larger excluded set tells a
better story is the over-claim this project guards against.

**The rule this file needs: derive class from column `Surfy`, never from row number.**

---

## What UniProt says (2018 table vs 2026 UniProt)

Every accession was joined against the UniProt reviewed human proteome retrieved 2026-08-04
(20,431 entries); the 157 that did not resolve were each resolved individually against the live
entry endpoint.

| Outcome | Rows | Treatment (rulings §5) |
|---|---|---|
| active and reviewed | 7,746 | — |
| **merged** into another entry | 105 | Pre-merge identifier **kept alongside** the current accession, never overwritten — *"how many arrived through a merge?"* stays answerable. 89 merge onto an accession already in this table. |
| **inactive** / withdrawn | 52 | Retained, `foldable=no` (no current sequence), **never dropped**. |
| unaccounted for | **0** | every accession is explained |

**No accession is corrupt.** The divergence is eight years of upstream drift, not scrape error —
itself evidence the reconstruction is faithful to a 2018 snapshot.

### ⚠ 2,886 identifiers are 2,807 proteins

| Class | Identifiers | Distinct accessions | Collapsed |
|---|---|---|---|
| surface | 2,886 | **2,807** | 79 |
| non_surface | 2,216 | 2,211 | 5 |
| unclassified | 2,801 | 2,795 | 6 |
| **total** | **7,903** | **7,811** | 90 |

The surface collapse is **four HLA loci**, merged upstream from allele-level entries:

| Current entry | Identifiers collapsing into it |
|---|---|
| `P01889` HLA-B | 35 |
| `P04439` HLA-A | 21 |
| `P10321` HLA-C | 14 |
| `P01911` HLA-DRB1 | 13 |

**Every join in this project is keyed by accession.** An accession-keyed census over the 2,886 would
fold `HLA-B` once and count it up to 35 times. **The surface denominator is 2,807** — of which 2,800
have a live reviewed accession and 7 are inactive.

⟡ **A separate defect from the collapse: the classes are not disjoint by accession even before
deduplication.** `Q96PC5` and `P01764` each carry rows in two classes (4 rows total). They are
flagged `class_conflict=yes` and **resolved by neither** — picking a class would assert a judgement
SURFY did not make. ⚠ **The rule for this bucket is the owner's call and is not made here.**

⟡ **Also drifted:** 397 entry names and 452 primary gene symbols renamed upstream
(`ADCK4`→`COQ8B`, `FAM132A`→`C1QTNF12`, `ARSE`→`ARSL`, …). Recorded, not acted on — they are the
reason the census keys on accession. Any join on **gene symbol** silently loses those rows.

### ⟡ The F-011 mapping hazard is discharged

F-011 and scale-readiness §2 flagged that `surfaceome_ids.txt` holds **entry names**, not
accessions, making its 2,886 IDs unjoinable. **This table supplies the accession for all 2,886** —
closed, with the caveat above: 79 of them are no longer distinct.

---

## The artifacts

| File | Role | sha256 |
|---|---|---|
| `data/census/membraneome-reconstructed-2026-08-04.csv` | ✅ **machine-readable source of record** — diffable, greppable, reviewable in a PR. **Tests read the CSV.** | `5a705cc9165eb863f51116c31f2a5f56080bf8941bf994a612f9d85fc6944d37` |
| `data/census/membraneome-reconstructed-2026-08-04.xlsx` | human-readable copy; carries the `PROVENANCE` sheet | `39eb67e64e41d6b018250ad9c488de609d3ad22c1f78711423dcabf83321bd74` |

7,903 rows. The duplicated preamble is dropped; the nine source columns are kept **verbatim** and
eight added: `surfy_class`, `uniprot_status`, `uniprot_current_accession`,
`uniprot_current_entry_name`, `uniprot_primary_gene`, `gene_symbol_changed`, `foldable`,
`class_conflict`.

**Committed directly, not LFS** (rulings §4) — LFS is what cost this project a day; the pointer
looked like the file in two places, and adding LFS reproduces that failure for the next clone. This
artifact should never change; if it must, that is a **new dated file with a new name**.

⚠ **Deliberately not named `table_S3_surfaceome.xlsx`.** That name belongs to an artifact nobody has
obtained. **Consequently `scripts/census_spans.py --source` has had its default removed and is now
required** (rulings §3): a default naming a nonexistent file silently changes source the day that
file appears, with no diff and no signal — and defaulting to the reconstruction is the mirror of the
same problem. The script now also **records the source file's sha256 in its output**, so provenance
travels with the result rather than with the invocation.

---

## What is **not** established

- **7,903 has no external corroboration.** The SURFY page publishes 2,886 and 2,216 and no total.
- **The 2,801 unclassified rows are unexplained.** Blank may mean unscored, below threshold, or lost
  in the scrape. Nothing here distinguishes those, and nothing here recruits them.
- **The per-cell values of the non-surface rows are unvalidated** — there is no source to validate
  them against. Corroboration reaches the counts and the surface membership, no further.
- **This is a scrape.** If the upstream `.xlsx` is obtained (the LFS pointer declares
  `size 6864772`, oid `2f1b8262…`), it supersedes this file without argument.

---

## ⟡ Recorded

Two gaps were live in the census before a single row was loaded: **the classes do not partition the
table**, and **the identifier count is not the protein count.** Both would have shipped as a
denominator that looked authoritative — wrong by 126% in one direction and 79 proteins in the other.
**Neither was found by a test. Both were found by opening the file and counting.**
