# PRE-REGISTRATION — 2026-08-19 — the acceptance bar for HPA v22 `normal_tissue.tsv`

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.**
>
> ⚠⚠ **WRITTEN BEFORE THE FILE WAS FETCHED OR OPENED.** `CA2` requires the bar to be stated before it
> is run and the comparison genes to be chosen before fetching. **This file is that statement**, and
> it is committed in its own commit so the ordering is checkable from history rather than asserted.
>
> ⚠ **Nothing here ingests anything.** `D-093` is a pre-registration and is **void if code precedes
> it**; no table is created, no row is written, no schema is final.

---

## §1 — Why this file exists at all

`pathology.tsv` had an external comparator: it was accepted by reproducing Kathad's S3 grid
**1,640 / 1,640, all four count columns identical** (`D-100`). ⚠⚠ **`normal_tissue.tsv` has no such
comparator.** There is no published table to reproduce, so *"it parsed and the row count looked
plausible"* is the whole of the naive bar — and that is `F-047`'s class exactly: well-formed,
correctly-typed, plausibly-sized, and unverified.

**Five wrong files were rejected in one day on the way to `pathology.tsv`**, every one real,
well-formed data from the right organisation. **A version string is a claim.**

## §2 — The bar, in two independent paths

**PATH A — the transport is checked, not assumed.** Fetch the file **twice**, independently, and
compare `sha256`. ⚠ A single fetch cannot distinguish *a correct file* from *a truncated one that
parsed*. **Also hash the copy already on this machine** and state whether all three agree — three
paths, and any disagreement is reported rather than resolved by preferring one.

**PATH B — reproduce named genes against HPA's own v22 web pages**, chosen and written down here
**before fetching**. For each gene: the tissues reported, and the ordinal `Level` per tissue/cell
type, compared against `https://v22.proteinatlas.org/<ENSG>-<GENE>/tissue`.

### The genes, fixed now

| gene | why chosen | expectation, stated before looking |
|---|---|---|
| `CLDN18` | an ADC target with a **restricted** normal distribution; `F-043`'s CLDN18.2 case | present, and **concentrated in stomach** — a gene that is high everywhere would refute the file |
| `ERBB2` | HER2; the most-characterised ADC target here | present, broad epithelial |
| `TACSTD2` | TROP2; Task J subject | present, broad epithelial |
| `INS` | insulin — ⚠ **the tissue-specificity control** | present, and **essentially pancreas-only**; if this reads broad, the file's tissue axis is wrong |
| ⚠ `ZZZ_NOT_A_GENE` | **the negative case** | **ABSENT.** A bar with no negative case cannot fail — if the lookup returns rows for a name that does not exist, the join is matching on something other than identity |

⚠⚠ **A REAL negative is stronger than a synthetic one, and it is reported as a count rather than
guessed at as a name:** HPA IHC covers fewer genes than HPA RNA, so **some census genes will be
absent from this file**. The number of census genes absent is reported as `ihc_gene_absent` — and
**that count is the real negative control, because it cannot be zero if the file is what it claims
to be.** ⚠ If it *is* zero, the join is wrong, not the biology.

## §3 — What is reported regardless of outcome

- The **URL**, the **retrieval timestamp**, the **byte count** and the **`sha256`** (`CA1`).
- The **full column list**, with any column outside the IN set flagged — ⚠ **the ingest is
  COLUMN-scoped: a column present in a stored table is ingested whether or not anything reads it**
  (`D-093` amendment 1 clause 2). ⚠⚠ **In particular, any `Cancer prognostics` column is a violation
  by presence.**
- The **tissue taxonomy** — distinct tissues, distinct cell types — and ⚠ **whether an absence in
  this file means *not detected* or *not tested*. Those are two different facts** and the schema will
  need them separated.

## §4 — The outcome that is committed in advance

**If the bar fails, edge 1 does not ship alone without recording the deviation.** ⚠ `D-093` decision
5 makes the normal-tissue differential **co-equal, not an appendix**, so shipping half of a co-equal
pair **is a deviation from a ruling and is written as one** (`P3`). **Both outcomes are committed
here, at equal prominence, before either is known.**
