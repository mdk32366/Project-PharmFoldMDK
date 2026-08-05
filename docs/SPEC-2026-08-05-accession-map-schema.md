# SPEC — 2026-08-05 — Task 2's output schema: one table, one home, and the grain question it exposed

> **COMMITTED 2026-08-05 with `### D-079` (`docs/README.md`). CITED BY the log, not restated in it —
> where this file and the log differ, THE LOG GOVERNS.** ⚠ This file is provenance for a decision that
> lives in the log; it is not itself authority. Check the `### D-079` header, not a reference to it.

> **Lands in #1's docs-only commit.** ⚠ **This document supersedes every column definition scattered
> across the four sources below.** Where it and any of them differ, **this governs** — until §4 lands
> the schema in code, after which **the code constant governs and this document is a description.**
>
> **Raised by Code**, checkpoint 5, 2026-08-05: *"Task 2's output header does not exist as a single
> artifact… a schema spread across four documents with one internal contradiction is the two-paths
> shape at the level of the spec rather than the code."* Correct, and it could not be closed without
> answering a question none of the four documents had asked.

---

## §1 — The contradiction, closed, and the pointer §3.1 wants

| Source | Said |
|---|---|
| `ORDERS-…-census-ingest-…-v2.md` §2 | `entry_name, source_accession, uniprot_accession, status, bucket, resolved_on` |
| `RULINGS-…-task2-task3-contract.md` §3.1 | `+ census_accession` — *"the CSV's, per D-079 dec 5"* ⚠ **superseded** |
| `AMENDMENT-…-D-079-census-key.md` §2 | `census_accession = uniprot_current_accession`; census is 2,807 |
| `AMENDMENT-…-D-079-census-key.md` §3 | buckets split into two axes + `census_identity_status` |

**Chronology settles it and Code was right not to treat it as open: the amendment governs.**
`census_accession = uniprot_current_accession`.

**⚠ The contract ruling §3.1's `census_accession` row is replaced by a pointer**, not by a corrected
definition — the standing consequence from the amendment (*where two sections name the same quantity,
one cites the other*) applies to the document that consequence was written in:

> | `census_accession` | ⚠ **Defined in `SPEC-2026-08-05-accession-map-schema.md` §3. Not restated here.** |

**⚠ The contract ruling was re-presented unchanged and that was correct** — a sealed document is not
edited to look as though it never said the wrong thing. The supersession is recorded in the open,
here and there.

---

## §2 — ⚠ The question the four documents never asked: **what is a row?**

Assembling the schema exposed it. **Task 2's output has two natural grains and they differ by 92 rows:**

| Grain | Rows | Because |
|---|---|---|
| **Per identifier** | 7,903 | It is a *mapping*. Verification is per identifier — a `disagrees` finding names an entry name, and D-079 dec 5 requires reporting that list. |
| **Per protein** | 7,811 | It is the *census*. Ingest, fetch, and every denominator are keyed by `census_accession`. |

**⚠ This is not academic. `census_spans.py` fetches a span per row.** At identifier grain it would
fetch **HLA-B thirty-five times** — the same 83-fold weighting the amendment ruled against, arriving
through the file's shape instead of through the key. **The collapse must happen before the fetch,
not after it.**

**And the two grains cannot be merged into one file.** `verification_bucket` is a fact about an
identifier; a protein with 35 identifiers may carry 35 different buckets. Flattening it either loses
the finding or invents a summary nobody ruled.

---

## §3 — RULING: two files, **parent and child, not siblings**

This is the pattern already proven in this repository for
`membraneome-reconstructed-2026-08-04.csv` → `.xlsx`: *two paths to one quantity with nothing
comparing them* was closed by making one **derived** from the other, with a test reddening on
disagreement. ⚠ **Two sibling files would be the two-paths class. A parent and a proven derivation
are not.**

### 3.1 — `data/census/accession_map.csv` — **per identifier, 7,903 rows.** The verification record.

| Column | Meaning | Vocabulary |
|---|---|---|
| `entry_name` | SURFY entry name | `1A01_HUMAN` … |
| `source_accession` | `UniProt Accession` as SURFY published it | provenance only — **never a fetch key** |
| `uniprot_accession` | What UniProt returns for this entry today | — |
| `uniprot_status` | UniProt's own | `active_reviewed` · `merged` · `inactive` |
| `surfy_class` | As published | `surface` · `non_surface` · `unclassified` |
| `class_conflict` | Consumed from the CSV, **not recomputed** | `yes` · `no` |
| `verification_bucket` | ⚠ **A FINDING. Never gates anything.** | `agrees` · `source_only` · `uniprot_only` · `disagrees` · `unresolvable` |
| `census_accession` | The protein this identifier belongs to = `uniprot_current_accession` | — |
| `resolved_on` | Date | — |

### 3.2 — `data/census/census_roster.csv` — **DERIVED, per protein, 7,811 rows.** What the pipeline reads.

| Column | Meaning | Vocabulary |
|---|---|---|
| `census_accession` | **The operative key.** Primary key of this file. | — |
| `source_identifiers` | Every `entry_name` collapsing here. ⚠ **A collapse that loses its inputs is a deletion.** | HLA rows carry 35 / 21 / 14 / 13 |
| `source_accessions` | Same, for accessions | — |
| `census_class` | After the collision rule | `surface` · `non_surface` · `unclassified` · **`class_conflict`** |
| `census_identity_status` | **Operational.** Single vocabulary, one constant, three sites (contract ruling §4). | `resolved` · `merged` · `multi` · `obsolete` · `unresolved` |
| `fetch_eligible` | Boolean, **computed once by the producer** | `true` · `false` |
| `fetch_ineligible_reason` | ⚠ Present iff `fetch_eligible=false`. **An absence with a cause, never a bare false.** | e.g. `uniprot_inactive` |
| `parent_sha256` | sha256 of the `accession_map.csv` this was derived from | — |
| `resolved_on` | Date | — |

**⚠ `verification_bucket` does not appear here, deliberately.** A verification bucket must never gate
a fetch (amendment §3): `disagrees` is a fact about our sources, not a statement that a protein is
unfetchable, and if it reached the pipeline a disagreement would silently shrink the census.

**Expected roster composition** — `surface` 2,807 · `non_surface` 2,209 · `unclassified` 2,793 ·
`class_conflict` 2 · **reconciling to 7,811.** ⚠ Four denominators, **never summed** — the
reconciliation is a check, not a reportable quantity.

---

## §4 — RULING: on landing, the schema moves into **code**, and this document stops being authoritative

⚠ **A schema that lives in a document and a writer that emits a header are two paths.** Code's own
contract test — *"the header Task 2 **actually emits**"* — cannot be written against prose.

1. **Both headers become module-level constants**, imported by the writer, by
   `read_accession_map`, and by the derivation step. **No literal header list anywhere else.**
2. **`census_identity_status`'s vocabulary is the same single constant** the contract ruling §4
   already requires across all three sites. **One vocabulary, one definition, four consumers.**
3. **This document then describes the constants; it does not define them.** Same relationship as
   `ui/src/system-model.json` and the architecture-contract test: a non-code artifact read as its
   subject, never as its source.

| Test | Assertion | Prove it bites by |
|---|---|---|
| `test_writer_emits_exactly_the_schema_constant` | Emitted header == the constant, both directions | Adding a column to the writer only → red |
| `test_reader_accepts_the_writer_s_header` | `read_accession_map` accepts the roster header with every required field populated | Renaming one column in the writer → red |
| `test_roster_is_derived_from_the_map_and_nothing_else` | `parent_sha256` matches the map actually read; roster row count == distinct `census_accession` in the map | Building the roster independently → red |
| `test_no_literal_header_survives_in_the_tree` | No hardcoded header list under `core/`, `scripts/` | Re-introducing one → red |
| `test_fetch_ineligible_rows_carry_a_reason` | Every `fetch_eligible=false` row has a non-empty reason | Emitting a bare `false` → red |

⚠ **`test_roster_is_derived_from_the_map_and_nothing_else` is the guard that matters.** The
membraneome pair's lesson, quoted from `PROVENANCE.md`: *a test comparing two files only to each
other stays green while both drift together.* The row-count assertion against the map's distinct keys
is what pins it to something outside the pair.

---

## §5 — Recorded

**Three of the last four Planner defects were found by Code assembling something the Planner had left
distributed** — a sealed table reproduced from the wrong source, a producer and consumer specified
apart, a key defined twice. **This one is the same class at the level of the spec:** no single
document held the header, so no single document could be wrong, and the contradiction survived four
readings because nobody was reading it all at once.

⚠ **And the grain question in §2 had gone unasked through four documents and three rulings.** It was
not hidden; it was never anybody's section. **The fix for a distributed spec is not more careful
reading — it is one artifact that fails to compile when it is incoherent**, which is why §4 exists.
