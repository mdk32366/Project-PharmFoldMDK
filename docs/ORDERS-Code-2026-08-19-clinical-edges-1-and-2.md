# ORDERS — Code — clinical association layer, edges 1 and 2 — supplier confirmation, the pinned mapping, and the prohibitions

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority.
>
> ⚠ **LANDED BY CODE, 2026-08-19, from `b7ecc2a`.** Received as chat text, not as a file.
>
> ⚠⚠ **NO `AUTHORED-SHA256` IS DECLARED, AND THAT IS DELIBERATE.** The document's own header says
> *"AUTHORED-SHA256 range: first `## §` header to EOF … Value in the delivering message"* — **no
> value was delivered, in this message or the companion survey.** Declaring the block with a hash of
> Code's own transcription would make the contract's `HASH-MATCH` verdict meaningless, so the block
> is omitted and the gap is recorded instead. ⚠ **`F-047` member 3's remedy assumes a file changes
> hands; this is the second consecutive landing where its precondition was not met** — the first is
> recorded in `F-047` itself.
>
> ⚠ **This copy is reflowed**, not byte-preserved: `BB4` measured that reflowing a hard-wrapped
> document costs 142–284 bytes and makes an authored-hash comparison uninformative. **Stated so a
> later reader does not mistake this for a verbatim artefact.**

---

## §0 — Owner rulings carried in (2026-08-19)

**R1 — The layer SHIPS WITHOUT SURVIVAL.** `D-093 (the clinical association layer)` decision 4 mandates a burden tuple; amendment 1 clause 2 excluded every `Cancer prognostics — … (TCGA)` column. ⚠⚠ **The schema mandates a field nothing licensed can populate, so edge 3 is HELD and its absence is a VISIBLE CATEGORY — `burden_supplier_unlicensed` — never a blank, never a zero, never a quiet omission.**

**R2 — Edges 1 and 2 together.** protein → tumour (HPA `pathology.tsv` v22) and protein → normal tissue (HPA `normal_tissue.tsv` v22). ⚠ **Decision 5 makes the normal-tissue differential CO-EQUAL, not an appendix** — they ship as a pair.

**R3 — `therapeutic_precedent` is ingested as a LABEL and can NEVER be a scoring feature.** ⚠⚠ *"Has been developed as an ADC target"* used to rank ADC targets is circular — **the identical argument that bars GPI status, and the identical argument `P-004` item 1 makes against Kathad's own validation step.** **The circularity warning renders in the same frame as the label, the way GPI's does.**

## §1 — ⚠⚠ THE GATE. Read this before starting anything

**`D-093` is a PRE-REGISTRATION and is VOID IF CODE PRECEDES IT.** Decision 6: *no schema is final until each supplier is confirmed to serve what this entry assumes*, and *a supplier that cannot answer question (3) with a pinned mapping does not enter the schema.*

⚠⚠ **NOTHING IN THIS ORDER INGESTS ANYTHING.** Every task below is one of two kinds: **read-only measurement** — fetch to cache, verify, count, report; **prohibition tests** — assertions that constrain the layer rather than implement it.

**No table is created. No row is written. No schema is final.** ⚠ **`D-093` amendment 2 — carrying R1, R2 and R3 — is written and ruled BEFORE any ingest**, and the Planner writes it from §5's answers. **This is the `D-091` ruling 3 shape, and we spent a day on it in the other direction.**

## §2 — ⚠ Pre-registration, committed before any number exists

**P1 — The four absence categories are reported BEFORE any coverage figure, and no percentage may absorb them.** `ihc_gene_absent` · `ihc_panel_empty` · `hpa_absent` · `accession_ambiguous` (`PREWORK §2b`). ⚠ **A coverage percentage stated ahead of its categories is the number that gets quoted.**

**P2 — `accession_ambiguous` is a CATEGORY, not a resolution rule.** If one UniProt accession maps to more than one gene, **it is reported as ambiguous and NOT silently resolved** — no first-match, no longest-match, no alphabetical. ⚠ *Absent values are categories, never low numbers*, and a tie-break invented at ingest is a dial nobody recorded.

**P3 — If `normal_tissue.tsv` fails verification, edge 1 DOES NOT SHIP ALONE without recording the deviation.** ⚠ Decision 5 makes edge 2 co-equal; shipping half of a co-equal pair is a deviation from a ruling and is written as one. **Both outcomes committed now, at equal prominence.**

**P4 — Every count states its key**: which population, which filter, which column. ⚠ **`3,467` is the census manifest; `2,690` is the folded set; `20,090` is HPA's gene count. Three denominators, and a figure that does not name which is not a measurement.**

## §3 — Task CA — `normal_tissue.tsv` v22, accepted by reproduction and not by label

⚠ **`scripts/hpa_v22_verify.py` already exists in the tree at `7011e24`. EXTEND IT — do not write a second verifier.** Two paths to one quantity is this project's most-repeated defect class and it would be self-inflicted here.

**CA1 — Fetch from the version-pinned host**, `https://v22.proteinatlas.org/about/download`. **Report the URL, the retrieval timestamp, the byte count and the `sha256`.** ⚠ **Five wrong files were rejected in one day on the way to `pathology.tsv`, every one real, well-formed data from the right organisation. A version string is a claim.**

**CA2 — The acceptance bar, and it is NOT a row count.** `pathology.tsv` was accepted by reproducing Kathad's S3 grid **1,640 / 1,640**. ⚠⚠ **There is no external comparator for `normal_tissue.tsv`, so state the bar you adopt BEFORE you run it** and make it two independent paths: **fetch twice and hash-compare** — the transport is checked, not assumed; **reproduce a named handful of genes against the v22 web pages for those genes**, chosen and written down before fetching. ⚠ **Include at least one gene expected to be absent** — a bar with no negative case cannot fail.

**CA3 — Assert the column set EXACTLY.** ⚠⚠ **The ingest is COLUMN-scoped** (amendment 1 clause 2): **a column present in a stored table is ingested regardless of whether anything reads it.** **Report the full column list and flag any column not in the IN set.**

**CA4 — Report the tissue taxonomy**: distinct tissues, distinct cell types, and ⚠ **whether an absence in this file means *not detected* or *not tested*.** **Those are two different facts and the schema will need them separated.**

## §4 — Task CB — the pinned mapping. ⚠⚠ This is where it fails silently

**The census keys on UniProt accession. HPA keys on Ensembl gene ID plus gene name. That is a TWO-HOP mapping**, and *a case-mismatched join returning a clean zero three times* is a catalogued `F-047` member.

**CB1 — Name the mapping instrument and pin it** — which file, which version, retrieved when, with its `sha256`. ⚠ **Decision 6 question (3) is not answered by "we join on gene symbol."**

**CB2 — Report BOTH directions** (Part C Step 19): census accessions with no HPA gene, **and** HPA genes reached by no census accession. ⚠ **A one-directional check cannot see orphans.**

**CB3 — Report the cardinality of the hop**: accessions mapping to exactly one gene · to more than one (`accession_ambiguous`, per **P2**) · to none. **Counts must sum to 3,467 with the key stated.**

**CB4 — ⚠ Prove the join is case- and whitespace-safe by a fixture that would fail if it were not.** **A join test that passes on clean data is testing nothing** — KEEL-1 V9 Principle 6 clause (c).

## §5 — Task CC — decision 6's three questions, answered in decision 6's own format

**For `pathology.tsv` and `normal_tissue.tsv` separately.** ⚠ **`pathology.tsv` is already validated at `D-100` — restate its answers rather than re-deriving them, and cite `D-100` for the reproduction.**

**This is the input the Planner needs to write `D-093` amendment 2. Nothing is built from it here.**

## §6 — Task CD — coverage across the census, categories first

**Of 3,467 census manifest rows** (key stated), how many reach at least one HPA IHC row — ⚠ **reported as the four P1 categories with counts, and only then, if at all, as a figure.**

**Report the same for the 2,690 folded rows separately.** ⚠ **Do not pool them.** *`F-011` and `F-016` were different mechanisms and were never pooled; the same rule applies to two denominators on one surface.*

**CD3 — ⚠ Report how many census proteins reach ALL 20 cancer types, and how many reach exactly one.** **That distribution is the empirical test of §0's warning**, and it should be measured before anyone argues about it.

## §7 — Task CE — `therapeutic_precedent`, and the test that keeps it out of the scorer

**`data/adc_reference_mapping.csv` is already in the tree.** Load it as a **label**, keyed to protein and indication.

**CE1 — Report its coverage against the census** and against the folded set, both keys stated.

**CE2 — ⚠⚠ WRITE THE PROHIBITION TEST FIRST, AND PROVE IT RED.** An assertion that no `therapeutic_precedent` field is reachable from the scorer's feature path. **Add it to the feature vector deliberately and watch the gate redden**, then remove it. ⚠ **A prohibition that has never been seen to fire is decoration** — Principle 9.

**CE3 — The circularity warning is a MOUNT PRECONDITION under `D-094`**, in the same frame as the label, not a footnote. **Same treatment as the GPI badge: the attribute and its liability together, never as a positive signal.**

## §8 — Task CF — the prohibitions, and check before building

⚠ **`D-093` lines 360–362 already list these gate assertions. Report whether each EXISTS at `HEAD` before writing anything** — *never assert absence from a stale copy*, and the Planner's reading is from `7011e24`.

1. **No protein-level model or payload carries a burden field** — add one, watch the gate redden.
2. **The burden statistic is unreachable from the protein path by iteration.**
3. **`/api/ranking`, `/api/analyses`, `/api/coverage` payloads asserted burden-free.**
4. ⚠⚠ **NEW, and it is amendment 1 clause 2 made structural: assert that NO `Cancer prognostics` column is present in any ingested or cached table.** **Column-scoped means the column's presence is the violation, not its use.**
5. **`burden_supplier_unlicensed` renders as a named category** wherever a burden would have appeared — ⚠ **and a test that the surface never renders a blank there.**

## §9 — What the Planner writes, and when

**`D-093` amendment 2** — carrying R1, R2, R3, and §5's supplier answers. ⚠ **It is written and ruled BEFORE any ingest. `D-093` is void if code precedes it, and that clause is the entry's own.**

⚠ **If any task above cannot be done without creating a table or writing a row, STOP AND REPORT.** **That is the boundary of this order, and a permission or scope denial is stop-and-report — never a retry, never a workaround.**
