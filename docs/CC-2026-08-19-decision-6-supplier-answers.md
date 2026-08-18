# CC — 2026-08-19 — `D-093` decision 6, answered for HPA `pathology.tsv` and `normal_tissue.tsv`

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority.
>
> ⚠⚠ **THIS IS THE INPUT TO `D-093` AMENDMENT 2, NOT THE AMENDMENT.** Nothing here is ruled, nothing
> is built, no table is created and no row is written. **`D-093` is a pre-registration and is void if
> code precedes it.** Written by Code for the owner to rule on.
>
> ⚠ **The order asked for "decision 6's three questions". Decision 6 lists FIVE** (items 1–5). All
> five are answered; the discrepancy is reported rather than silently resolved to three.

---

## §0 — What is being confirmed, and against what

Decision 6: *"Supplier before contract. No schema is final until each supplier is confirmed to serve
what this entry assumes … A supplier that cannot answer (3) with a pinned mapping does not enter the
schema."*

Two suppliers, answered **separately** because they are different files with different shapes:
**`pathology.tsv`** (edge 1, protein → tumour) and **`normal_tissue.tsv`** (edge 2, protein → normal
tissue, co-equal under decision 5).

---

## §1 — `pathology.tsv`, HPA v22

### (1) What it actually serves, at what granularity

**Per (gene × cancer type): four patient COUNTS** — `High`, `Medium`, `Low`, `Not detected`. **20,090
genes × 20 cancer types, 401,800 rows.** ⚠ **Not per patient, not per stage.**

⚠ **Reproduction is already established — `D-100`, cited, not re-derived here:** convention A,
`qh = 100 × (Low/total + 2·Medium/total + 3·High/total)` with the denominator **including** *Not
detected*, reproduces Kathad's S3 grid **337 / 337** kept pairs and correctly excludes **1,303 /
1,303**, all four count columns identical over **1,640 / 1,640** rows.

**Facts about what the data IS, placed here rather than filed as caveats:**

- ⚠ **All four count columns are purely numeric.** Measured across the whole file: **zero
  non-numeric values** in any of them. **So `pathology.tsv` does NOT carry the non-ordinal
  vocabulary `normal_tissue.tsv` does** — the two files are different shapes and the comparison
  cannot be made directly.
- ⚠⚠ **THERE IS NO `Reliability` COLUMN.** `normal_tissue.tsv` has one; this file does not.
  **The modality that drives target selection is the one without the quality flag.**
- ⚠ **Panels are small.** `F-043`: median **11**, max **12**, and **246 of 1,640** Kathad rows sit at
  **n ≤ 4**. **The n must travel with every number.**
- ⚠⚠ **The file carries FOUR prognostic columns** — `prognostic - favorable`,
  `unprognostic - favorable`, `prognostic - unfavorable`, `unprognostic - unfavorable` — see §3.

### (2) Open tier or controlled tier

**Open.** Downloaded anonymously over HTTPS from the version-pinned host; no account, no token, no
authorisation step. **Licence CC BY 4.0**, read 2026-08-17 (`D-093` amendment 1 clause 1).

### (3) ⚠⚠ Does the identifier space join to UniProt accession without a lossy intermediate?

**It requires a mapping step, and the step is recorded with its own failure categories — never a
silent left-join.**

**The pinned instrument is already in the tree**: the UniProt entries cached in
`data/census/spancache/`. **No new supplier is introduced.** Each entry is read **two independent
ways**, and the two are compared:

- **Path A** — the `HPA` cross-reference, whose `id` **is** the unversioned `ENSG…`;
- **Path B** — the `Ensembl` cross-reference's `GeneId` property, versioned, suffix stripped.

| | |
|---|---|
| accessions with both paths present | **3,331** |
| the two paths **agree exactly** | **3,137** |
| ⚠ the two paths **disagree** | **289** |
| — of those, HPA a strict **subset** of Ensembl | **288** — multiplicity, not identity |
| — ⚠⚠ genuinely **disjoint** | **1 — `Q3MIW9` MUCL3**, HPA `ENSG00000168631` vs Ensembl `ENSG00000229284` / `ENSG00000232251` |

⚠ **Taking HPA over Ensembl is a CHOICE and is recorded as one**: Ensembl lists every locus a
protein maps to (haplotypes, patches); HPA lists the one it profiles. ⚠⚠ **`Q3MIW9` is left
UNRESOLVED** — two paths naming different genes is a finding, not a tie to break.

**Cardinality of the hop, summing to the manifest (key: one row per `census_accession` in
`census_manifest.v7.csv`):**

```
exactly_one_gene       3,351
accession_ambiguous       21     ⚠ KIR / HLA / OR loci — REPORTED, never resolved (P2)
hpa_absent                95
TOTAL                  3,467
```

**Failure categories, reported before any coverage figure (P1), each summing to its denominator:**

```
census manifest (3,467) × pathology.tsv
  ihc_present 2,328 · ihc_gene_absent 15 · ihc_panel_empty 1,008 · hpa_absent 95 · ambiguous 21
folded set (2,690) × pathology.tsv
  ihc_present 1,721 · ihc_gene_absent 13 · ihc_panel_empty  855 · hpa_absent 81 · ambiguous 20
```

⚠ **The two populations are not pooled.**

### (4) Stability: versioned release, and can a value be pinned to it?

**Yes.** `https://v22.proteinatlas.org/download/pathology.tsv.zip` — the version is in the **host
name**, so a pinned URL cannot silently serve a later release. ⚠ **v22 is pinned for two independent
reasons**: Kathad comparability, and HPA's own citation format.

### (5) The verbatim required attribution string

⚠⚠ **NOT ANSWERED, AND IT IS NOT ANSWERABLE FROM THE FILES.** The attribution string is a property
of HPA's licence page, not of the download. **Reading it is an unperformed step and is recorded as
one** rather than reconstructed from memory — ⚠ *`D-093` amendment 1 exists because a licence was
recalled rather than read.* **URL to read: `https://v22.proteinatlas.org/about/licence`.**

---

## §2 — `normal_tissue.tsv`, HPA v22

### (1) What it actually serves, at what granularity

**Per (gene × tissue × cell type): one ordinal `Level` plus a `Reliability` grade.**
**1,194,479 rows · 15,318 Ensembl gene ids · 15,313 gene names · 64 tissues · 266 (tissue, cell)
pairs.**

⚠⚠ **THERE ARE NO PATIENT COUNTS.** A quasi-H-score **cannot be computed on this file** — it has no
denominator. **A tumour-vs-normal difference would put two incomparable quantities either side of a
minus sign.** Decision 5's differential needs a ruling on what it actually compares.

**⚠⚠ `Level` IS NOT A CLEAN FOUR-VALUE ORDINAL.** Measured, every value named, none bucketed:

```
Not detected  565,839      N/A                 1,860
Medium        302,651      Ascending             172     ⚠ a GRADIENT, not a level
Low           183,677      Descending             73     ⚠ a GRADIENT, not a level
High          140,198      Not representative      9
```

⚠ **Any code treating `Level` as a 4-value ordinal silently mishandles 2,114 rows.**

**`Reliability`, which this file has and `pathology.tsv` does not:**
`Approved` 460,449 · `Enhanced` 390,450 · `Uncertain` **182,628** · `Supported` 160,952.
⚠ **182,628 rows are `Uncertain`.**

⚠⚠ **AN ABSENT ROW MEANS *NOT TESTED*, NOT *NOT DETECTED*.** `Not detected` is an **explicit** value,
and **0 of 15,313 genes cover all 266 (tissue, cell) pairs** — the grid is **ragged**. **Two
different facts, and the schema must store them separately.**

### (2) Open tier or controlled tier

**Open**, identical to §1(2). Same organisation, same CC BY 4.0 ruling, same version pin.

### (3) Does the identifier space join to UniProt accession without a lossy intermediate?

**Same instrument, same mapping, same categories as §1(3)** — the hop is a property of the census key
and HPA's key, not of which HPA file is on the other side. Coverage under this file:

```
census manifest (3,467) × normal_tissue.tsv
  ihc_present 2,008 · ihc_gene_absent 1,023 · ihc_panel_empty 320 · hpa_absent 95 · ambiguous 21
folded set (2,690) × normal_tissue.tsv
  ihc_present 1,472 · ihc_gene_absent   868 · ihc_panel_empty 249 · hpa_absent 81 · ambiguous 20
```

⚠⚠ **THE SAME UNDERLYING FACT ARRIVES AS A DIFFERENT CATEGORY IN THE TWO FILES.** No IHC for a gene
is **`ihc_panel_empty` (1,008)** in `pathology.tsv`, which lists nearly every gene, and
**`ihc_gene_absent` (1,023)** in `normal_tissue.tsv`, which simply omits it. **The surface must not
launder that into one word.**

### (4) Stability

**Yes**, `https://v22.proteinatlas.org/download/normal_tissue.tsv.zip`. ⚠ **Accepted by reproduction,
not by label**, against a bar pre-registered in its own commit `d0fd95e` **before the fetch**:

- **Three `sha256` values, one result** — two independent fetches and the copy already on the
  machine: `8453c46c6f4690428c029cf1d7e8dba289ae33b288f874b00105a008dbe62ff7`.
- **Five pre-registered gene expectations, all held**, including the two that could have failed:
  **`INS` resolves to exactly ONE detected row of 103 — pancreas, `High`**; **`ZZZ_NOT_A_GENE`
  returns zero**. `CLDN18`'s only `High` levels are `stomach 1` and `stomach 2`.

### (5) The verbatim required attribution string

⚠ **NOT ANSWERED**, identically to §1(5) and for the same reason. **Unperformed, recorded as such.**

---

## §3 — ⚠⚠ A finding the amendment must carry: the exclusion rule names a column that does not exist

`D-093` amendment 1 clause 2 excludes every **`Cancer prognostics — … (TCGA)`** column. **Measured
against HPA v22:**

```
columns beginning "Cancer prognostics"  :  0 in pathology.tsv,  0 in proteinatlas.tsv
columns whose name contains "TCGA"      :  0 in either file
what is ACTUALLY present:
  pathology.tsv    (4)  prognostic - favorable · unprognostic - favorable
                        prognostic - unfavorable · unprognostic - unfavorable
  proteinatlas.tsv (17) Pathology prognostics - <cancer>
```

⚠⚠ **A guard matching a string that never occurs passes forever while the thing it means to exclude
flows through under its real name.** This is KEEL-1 V9 Principle 6 clause (c) — *a guard has a
direction and it can point the wrong way* — and it is the same shape as the `## P-004` grep that
manufactures a false absence.

⚠ **Code's own first prohibition test inherited the defect**, matching the as-ruled prefix. It has
been retargeted to the token `prognos` and **proven red against both real v22 column names**; the
as-ruled prefix's failure to match them is now itself asserted, so a future restatement of the rule
reds the test and is re-derived deliberately.

⚠ **No number is taken for this.** Where it lands is the Planner's; it is reported here because
`D-093` amendment 2 is the entry it corrects.

---

## §4 — What decision 6 does NOT let us conclude

- ⚠ **Edge 3 has no supplier.** Decision 4 mandates a burden tuple; amendment 1 clause 2 removed the
  only redistributed survival data. **Nothing licensed can populate the field the schema mandates.**
- ⚠ **Four of five candidate suppliers are UNREAD** — SEER, GLOBOCAN/IARC, TCGA/GDC, CPTAC. **None is
  characterised here**, because *`D-093` amendment 1 exists because a licence was recalled rather
  than read.*
- ⚠⚠ **Item (5) is unanswered for both confirmed suppliers.** A supplier confirmed on four of five
  items is **not** a supplier confirmed. **Stated plainly so the amendment does not inherit a gap as
  a pass.**
