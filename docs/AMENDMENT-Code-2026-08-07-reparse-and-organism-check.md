# AMENDMENT — Code — 2026-08-07 — Re-parse, not re-extract; and the yeast term becomes its own finding

> **AMENDS `ORDERS-Code-2026-08-07-span-implementation.md` — Task 3f and Task 5b only.**
> Supersedes nothing and restates none of it. Where this file and that order differ on anything
> other than the two items below, **that order governs**; where either differs from the log,
> **THE LOG GOVERNS.** ⚠ This file is an amendment, not authority.

## TWO AMENDMENTS. Both apply to work already in flight.
**If this document does not end with `— END OF AMENDMENT (2 of 2) —`, it truncated. Report and request re-delivery.**

> ⚠ **Code is in flight on the superseding order.** **A1 changes how Task 3f is executed — apply it
> before 3f runs.** **A2 changes what Task 5b produces — it is read-only and can be picked up
> whenever 5b is reached.** **Nothing already done needs undoing.**

> **Planner provenance (D-016):** A1's data-flow claim was derived from `scripts/ecd_lengths.py`
> read at first hand in the `4b7547c` snapshot — `fetch_cached` writes the whole UniProt response;
> `parse()` filters before the CSV is written. A2's identification of the term as *S. cerevisiae*
> sporulation vocabulary is **Planner general knowledge, NOT sourced at first hand.**

---

# AMENDMENT 1 — Task 3f: re-parse the cache. Do not re-extract, and do not re-classify the CSV.

## A1.1 — Where the information lives

```
network fetch  →  cache (full UniProt JSON)  →  parse() filter  →  spans_*.csv
                  ↑ everything survives here      ↑ information is destroyed here
```

⚠ **The dropped domains are not in `spans_surface.csv` or `spans_annex.csv`. `parse()` filtered them
out before the CSV was written — a `Lumenal` domain never became a row, and the output carries no
record that anything was rejected.**

**So the saving is real but it is one stage further back than "reclassify" implies:**

- ✅ **The network fetch is not repeated.** ~30 minutes and 5,016 rate-limited requests, saved —
  **because the cache holds the full JSON rather than the parsed output.**
- ⚠ **The CSV cannot be reclassified.** It has no rows to reclassify.
- ✅ **Re-parse the cache.** A local pass over files already on disk. **Minutes.**

⚠ **If any cache entry is missing, that protein is `absent_with_reason`, named — do NOT re-fetch it
without a separate word.** A partial re-fetch would put two fetch dates in one file.

## A1.2 — ⚠ THE BINDING CONSTRAINT: two facts, never one date

**The data was fetched 2026-08-06 at a specific UniProt release. Only the parse changed.**

| Field | Source | Rule |
|---|---|---|
| `fetched_on` | **the cache entry** | ⚠ **PRESERVED, unchanged. Never restamped** |
| `uniprot_release` | **the cache entry** | ⚠ **PRESERVED, unchanged** |
| `parsed_under` | **new** | The span definition version and the commit that produced this row |

⚠ **A re-parse that overwrites the fetch date manufactures a provenance for data that did not
move.** It would turn a one-day pull into a two-day pull as an artifact of housekeeping — **the
exact thing the date rule exists to catch, tripped by its own maintenance.**

**Same shape as the two provenance files written by different splitter versions**, and that one was
handled correctly by naming both. ⚠ **Do the same here: the artifact says when it was fetched AND
under which definition it was parsed.**

## A1.3 — A test, because a preserved date is a claim

⚠ **Assert `fetched_on` is byte-identical before and after the re-parse**, on at least one row whose
span changes. **Prove by revert: restamp the date, confirm red fires at that assertion** — not at a
row count, which would move under either implementation. **Report the file and line.**

---

# AMENDMENT 2 — Task 5b: the yeast term becomes its own finding, and the organism check comes first

**`Mother cell cytoplasmic`, n=1.** ⚠ **Planner reading, unsourced: this is *Saccharomyces
cerevisiae* sporulation vocabulary — prospore-membrane topology during ascospore formation. There is
no mother cell in a human cell line.**

## A2.1 — ⚠ Three hypotheses, and they are NOT equally serious

| | Hypothesis | Severity |
|---|---|---|
| 1 | Ortholog annotation transfer — a human entry inherited a yeast curator's term | **Cosmetic.** A word, wrong |
| 2 | UniProt curation error in a human entry | **Cosmetic.** Report upstream |
| 3 | ⚠⚠ **The row is not a human protein** | **SERIOUS — a non-human entry inside the census** |

⚠ **Hypothesis 3 is a DENOMINATOR problem, not a vocabulary problem.** *"7,811 human proteins"* has
been stated in the deck, the literature review and `P-003`. **If one row is non-human, that number
is wrong in three published artifacts.**

## A2.2 — Check the organism first. It is one field.

**Report, from the cache:** accession · gene · **`organism` / `taxonId` verbatim** · the full
`Topological domain` feature block · the entry's review status (reviewed / unreviewed) · and which
census class it sits in.

**⚠ STOP CONDITION.** **If the organism is anything other than *Homo sapiens*:**

- **STOP. Do not continue to the rest of Task 5, and do not proceed to the manifest.**
- ⚠ **Run a census-wide organism sweep** — every accession in the roster, `organism` / `taxonId`
  tabulated, **counts by organism, every value present including the expected one.**
- **Report the count of non-human rows by class.** ⚠ **Do not remove them.** Removal changes four
  denominators stated in three artifacts, and that is an owner ruling.

**If the organism is human:** hypotheses 1 or 2. **Cosmetic, reported, and ruled — never dropped
silently.**

## A2.3 — Reserve, do not write

⚠ **Reserve the finding in `RESERVED.md`. Do not write a `### ` entry, and do NOT take an integer.**

**Reservation text, in substance:** *a topological-domain term from a non-human organism's
vocabulary appears in the human membraneome census; the organism of the carrying row determines
whether this is a cosmetic annotation artifact or a denominator error affecting counts already
published.*

**What unblocks it:** the organism check, and — if non-human — the sweep.

⚠ **Four findings are already queued for one free integer.** *(the KEEL absence · a verification
sharing an implementation with its subject · derive-from-source-not-context · an order asking for
confirmation invites confirmation.)* **No number is taken under momentum. The owner rules.**

## A2.4 — What does NOT change

⚠ **`Cytoplasmic` is rejected regardless, so no count moves either way** — this is a data-quality
question, not a scoring one. **Task 5a (`Lumenal, melanosome` and `Vacuolar`) is unaffected and
proceeds as ordered.**

---

## REPORT BACK

Plain lines, `label | value`. **No box-drawing tables.**

**A1** — the re-parse method used · ⚠ **`fetched_on` preserved, asserted and revert-proven, with the
file and line** · rows gained by mechanism · `parsed_under` present on every row · any missing cache
entry named as `absent_with_reason`

**A2** — accession · gene · **organism verbatim** · taxonId · review status · census class · the
feature block · ⚠ **and if non-human, the sweep and a full stop**

⚠ **Everything else in the superseding order is unchanged**, including the absolute bar on
re-extracting, re-fitting, re-scoring or re-folding the 82 under D-081.

— END OF AMENDMENT (2 of 2) —
