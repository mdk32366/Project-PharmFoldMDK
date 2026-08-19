# PASTE-READY — `D-093` amendment 2 — for `docs/README.md`

> ⚠ **TO BE COMMITTED.** ⚠⚠ **DOWNLOAD AND COMMIT THIS FILE. DO NOT RETYPE IT.** The paste is for
> reading; the file is the record. **AUTHORED-SHA256 range: first `####` header to EOF. Value in the
> delivering message.**
>
> ⚠ **A sub-entry, not a new integer** — the `D-099 amendment 1` / `D-093 amendment 1` precedent.
> **It sits at the end of `D-093`'s body, before the next `###` header**, not at the head of the log.
> **The next free top-level integers are unchanged. Confirm against the live log before merging.**
>
> **Predicted invariant: unchanged at `147 / 15 / 162`.** ⚠ **`cited` is a SET — every number below
> is already cited somewhere. It will not move, and predicting otherwise is what member 7 records.**

---

#### D-093 amendment 2 — ⚠⚠ The layer ships on two edges without survival; the exclusion rule named a column that does not exist; and the normal-tissue differential is NOT a subtraction

- **Date:** 2026-08-19 · **Status:** accepted. ⚠ **This entry is what discharges decision 6 for HPA
  and unblocks schema, ingest and surface.** Nothing was ingested before it.
- **Evidence:** `docs/CC-2026-08-19-decision-6-supplier-answers.md`, branch
  `census/clinical-edges-survey`, tip `392ba1d`. Bar pre-registered at `d0fd95e` **before the fetch**,
  so the ordering is checkable from history rather than asserted.

**⚠ Where the deep learning is.** The census exists as a structural instrument; this layer is what
lets a structure-derived ranking be *compared* against an expression-derived one — `P-001`'s whole
question. ⚠⚠ **It is also the point of maximum risk to that comparison: if the clinical edge is
built as an expression threshold, the structural axis is being validated against the thing `P-004`
argues is under-powered.** Ruling 4 exists for that reason.

---

**RULING 1 — The layer SHIPS WITHOUT SURVIVAL. Edge 3 is held and its absence is a visible category.**
Decision 4 mandates a burden tuple; amendment 1 clause 2 removed the only redistributed survival
data. ⚠⚠ **The schema mandates a field nothing licensed can populate.** `burden_supplier_unlicensed`
renders wherever a burden would have appeared — **never a blank, never a zero, never an omission.**
⚠ **SEER, GLOBOCAN/IARC, TCGA/GDC and CPTAC are UNATTEMPTED, not failed** — a category with a cause.

**RULING 2 — Edges 1 and 2 ship together.** `pathology.tsv` v22 (protein → tumour) and
`normal_tissue.tsv` v22 (protein → normal tissue). Decision 5 makes the second **co-equal, not an
appendix.**

**RULING 3 — `therapeutic_precedent` is a LABEL and may NEVER be a scoring feature.** ⚠⚠ *"Has been
developed as an ADC target"* used to rank ADC targets is circular — **the identical argument that
bars GPI status, and the identical argument `P-004` item 1 makes against Kathad's own validation
step.** The circularity warning renders **in the same frame as the label**, the GPI-badge pattern:
attribute and liability together, never as a positive signal.

**RULING 4 — ⚠⚠ THE NORMAL-TISSUE DIFFERENTIAL IS NOT A SUBTRACTION, AND CO-EQUAL DOES NOT MEAN
COMPARED.**
`pathology.tsv` serves **four patient COUNTS** per (gene × cancer). `normal_tissue.tsv` serves **one
ordinal LEVEL** per (gene × tissue × cell type) and ⚠⚠ **carries NO PATIENT COUNTS AT ALL.**
- **A quasi-H-score cannot be computed on the normal side — it has no denominator.**
- ⚠ **No tumour-normal ratio, difference, contrast or index is computed from these two suppliers.**
  **Putting them either side of a minus sign is two incomparable quantities in one expression.**
- **Decision 5 is satisfied by CO-EQUAL DISPLAY**: both edges rendered side by side, **each in its own
  units**, with the incomparability stated on the surface. ⚠ **The ratio is PRE-REGISTERED AS NOT
  COMPUTABLE FROM THIS SUPPLIER** — an absence with a cause, not an unfilled intention.
- ⚠ **Open, and named: does HPA publish a normal-tissue file carrying patient counts?** **Unchecked.
  If one exists, this ruling is revisited on the record.**

**RULING 5 — Absence is stored in TWO LAYERS, because the same fact arrives under two encodings.**
No IHC for a gene is `ihc_panel_empty` (**1,008**) in `pathology.tsv`, which lists nearly every gene,
and `ihc_gene_absent` (**1,023**) in `normal_tissue.tsv`, which omits it. ⚠ **One fact, two supplier
encodings.**
- **`supplier_encoding`** — `row_absent` · `row_present_panel_empty`. **What the supplier did.**
- **`derived_fact`** — `no_ihc_available`. **What is true of the protein.**
- **The surface renders the derived fact; the record keeps the encoding.** ⚠⚠ **Two paths to one
  quantity — in the DATA rather than in our code — compared once, on purpose, and kept.**

**RULING 6 — ⚠ An absent row means NOT TESTED, never NOT DETECTED.** `Not detected` is an **explicit**
value (565,839 rows), and **0 of 15,313 genes cover all 266 (tissue, cell) pairs** — the grid is
**ragged**. **Stored as separate facts.**

**RULING 7 — ⚠⚠ `Level` IS NOT A FOUR-VALUE ORDINAL and no code may treat it as one.** Beside
`Not detected` / `Low` / `Medium` / `High` there are **`N/A` 1,860 · `Ascending` 172 ·
`Descending` 73 · `Not representative` 9 = 2,114 rows.** ⚠ **`Ascending` and `Descending` are
GRADIENTS — they are not positions on a scale and no weighting can place them.** **A test asserts the
full value set and reds when an unhandled value appears.**

**RULING 8 — ⚠ The reliability asymmetry is disclosed and no asymmetric filter is applied.**
`normal_tissue.tsv` carries `Reliability` — **`Uncertain` on 182,628 rows** — and **`pathology.tsv`
carries none.** ⚠⚠ **Filtering normals on quality while being unable to filter tumours introduces a
DIRECTIONAL bias.** **Either side is filtered identically or neither is; if ever applied, the
asymmetry is stated in the same frame.** *`F-012`'s pattern: a bias of known direction is stated,
never corrected.*

---

**CORRECTION 1 — ⚠⚠ AMENDMENT 1 CLAUSE 2 NAMES A COLUMN THAT DOES NOT EXIST.**
It excludes every `Cancer prognostics — … (TCGA)` column. **Measured against v22: ZERO columns begin
`Cancer prognostics` and ZERO contain `TCGA`, in either `pathology.tsv` or `proteinatlas.tsv`.**
What is actually present: **four** `prognostic - favorable` / `unprognostic - …` columns in
`pathology.tsv`, and **seventeen** `Pathology prognostics - <cancer>` in `proteinatlas.tsv`.

⚠⚠ **A licence-compliance guard has been passing since 2026-08-17 by matching a string that never
occurs, while the data it means to exclude sits in the file accepted at `D-100` under its real name.**
**KEEL-1 V9 Principle 6 clause (c)**, and the same shape as the `## P-004` grep.

- **Clause 2 is corrected to match the token `prognos`**, case-insensitive, across **column names**.
- ⚠ **The as-ruled prefix's failure to match the real names is ITSELF asserted**, so a future
  restatement of the rule reds the test and is re-derived deliberately.
- ⚠ **Code's own prohibition test inherited the defect** and has been retargeted and proven RED
  against both real v22 names.
- ⚠ **One thing to measure and state rather than assume: is every cached artifact under `data/` free
  of a prognostic column?** **If the cached copy is clean, that is LUCK STANDING IN FOR PROCESS and
  is recorded as such, not as compliance.**
- **`F-047` member 9.** No new integer.

**CORRECTION 2 — ⚠ Decision 6 has FIVE questions across FIVE suppliers, and the Planner cited three.**
Repeated in the supplier survey and two orders. ⚠⚠ **`F-044`'s class — citing an entry by content it
does not have — third instance this week.** **`F-047` member 10 (Planner).**
- **HPA is answered on FOUR of five.** ⚠⚠ **Item 5 — *the verbatim required attribution string* —
  is UNANSWERED for both files.** **A supplier confirmed on four of five items is not a supplier
  confirmed**, and this entry does not record it as one.
- ⚠ **Item 5 is WRITING, not research** — the four-part obligation is already specified in amendment
  1 clause 3. **It is read from `https://v22.proteinatlas.org/about/licence` and recorded verbatim
  with the date read**, because *amendment 1 exists because a licence was recalled rather than read.*
- **HPA passes question 3** with a pinned mapping, so it enters the schema; ⚠ **the entry states the
  gap rather than inheriting it as a pass.**

**CORRECTION 3 — ⚠⚠ `D-093`'s five listed gate assertions never existed.** The entry describes them
under *"written before any code"*; **zero hits at `b7ecc2a`.** **A pre-registration asserting a test
surface that was never built is `F-047`'s class at the level of a decision entry** — well-formed,
confident, and unfalsifiable from inside itself. ⚠ **Found only because the order said *report whether
each exists* rather than *implement these*.** **`F-047` member 8 (Planner).** The five tests are now
written and each proven RED — **the remedy lands after the finding, not instead of it.**

---

**WHAT THIS ENTRY DOES NOT LICENSE**

- ⚠ **Not an association claim.** Every rendered edge carries its evidence type, and
  `differential_expression` is labelled as such — **never as *"associated with"*.** *Every surface
  protein is expressed somewhere.*
- ⚠⚠ **Not a coverage percentage ahead of its categories.** The bar changes the answer by a factor of
  22: **all-20 is 785 at any detection, 57 at `qh ≥ 150`, and 35 at any `High`.** **`23.4%` may not be
  quoted without the table.**
- ⚠ **Not a resolution of `Q3MIW9` MUCL3** — HPA and Ensembl name disjoint genes and it is left
  unresolved. **Not a resolution of the 21 `accession_ambiguous` KIR/HLA/OR loci.**
- ⚠ **Not a burden of any kind on a protein payload** — decision 1 stands unchanged. **The prohibition
  is on BURDEN, not on EXPRESSION**; an IHC edge is not barred.
- ⚠⚠ **Not a licence characterisation of any supplier other than HPA.**

**Assumptions relied on:** `A-014 (an upstream model's negative class is a prediction, not a fact)` —
⚠ **IHC is an assay, not a model, so `A-014` does NOT apply to these edges.** *Recorded because the
temptation to cite it here is exactly the class of error this entry catalogues.*
