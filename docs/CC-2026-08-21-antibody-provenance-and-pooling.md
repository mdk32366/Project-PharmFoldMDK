# `XD` / `XE` / `XF` — antibody provenance, and whether a `mapped` category pools distinct diseases

> ⚠⚠ **DOCUMENTATION ONLY.** No ratio computed, no contrast computed, no ingest, no fetch of data, no
> schema, no page, and **no subdivision of any HPA category**.
> Produced under `ORDERS-Code-antibody-provenance-and-pooling.md` (`2ad63aa0…`, verified).
> **All pages read 2026-08-21.**

---

## §1 — `XD` — SAME ANTIBODY? ⚠⚠ **UNDOCUMENTED. This is the ceiling, and it is the finding.**

### `XD2` — do the files carry an antibody identifier? **NO. Neither does.**

Read from the tree, not from recollection — `scripts/clinical_ingest_edges.py` and
`docs/CC-2026-08-19-decision-6-supplier-answers.md`:

| file | columns | antibody id? |
| --- | --- | --- |
| `pathology.tsv` | **11**: `Gene` · `Gene name` · `Cancer` · `High` · `Medium` · `Low` · `Not detected` · `prognostic - favorable` · `unprognostic - favorable` · `prognostic - unfavorable` · `unprognostic - unfavorable` | ⚠⚠ **none** |
| `normal_tissue.tsv` | **6**: `Gene` · `Gene name` · `Tissue` · `Cell type` · `Level` · `Reliability` | ⚠⚠ **none** |

**⚠ So the question is not answerable from what we hold, at any level of care.** Both files key on
gene; neither names the reagent that produced the value.

### `XD1` — does HPA document it? **Not on the pages that would carry it.**

Read directly, 2026-08-21:
- `v22.proteinatlas.org/about/assays+annotation`
- `v22.proteinatlas.org/humanproteome/pathology`
- `www.proteinatlas.org/humanproteome/tissue/method/ih+imaging`

**None states whether a given gene's `pathology.tsv` value and its `normal_tissue.tsv` value come
from the same antibody.** What the assays page does say, verbatim:

> *"Tissue microarrays are used to show antibody staining in samples from 144 individuals
> corresponding to 44 different normal tissue types, and samples from 216 cancer patients
> corresponding to 20 different types of cancer"*

> *"For independent antibodies, the immunohistochemical data from all the different antibodies are
> taken into consideration."*

⚠⚠ **THE SECOND SENTENCE IS WORSE THAN SILENCE.** It says data from **different antibodies are
combined** in HPA's annotation. **So a single reported value is not guaranteed to be one antibody
even within one file** — and `P-004`'s measured 52.5% (9,140 / 17,407 genes carry more than one
antibody) is the population that can be affected.

⚠ **A NEGATIVE RESULT ABOUT MY OWN SEARCH, RECORDED.** A web-search summary attributed to the
pathology page a sentence reading *"all proteomics data has been generated in-house using the same
antibodies as in protein expression profiling in normal human tissues."* **I fetched that page and
the sentence is not on it.** It is not quoted as evidence here. *A search summary is not a source,
and this one would have answered the question in the convenient direction.*

### `XD3` — verdict

**`hpa_antibody_provenance_undocumented`.** ⚠ **Not inferred from consistency of the values** — two
antibodies agreeing is not one antibody, and the order named that trap explicitly.

### ⚠⚠ What this caps

**Per §4 of the order, the contrast line STOPS HERE.** An ordinal tumour-vs-normal contrast would
compare a value of unknown reagent provenance against another value of unknown reagent provenance.
That is **two assays, possibly, not one protein across two tissues** — and every downstream statement
would inherit it.

⚠ **This belongs in `D-093` decision 6 question (1) for HPA** — *what the supplier actually serves* —
where HPA currently stands at **four of five**. **This makes question (1) materially less complete
than "answered" implied**, and item (5) is still open, so HPA is now short on two counts, not one.

---

## §2 — `XE` — does a `mapped` category pool clinically distinct subtypes?

**⚠⚠ `mapped` MEANS THE NAMES AGREE. IT DOES NOT MEAN FIT FOR PURPOSE**, and thirteen green rows
would be read as thirteen usable ones without this column.

⚠ **The Planner's list was offered as a starting point and explicitly not as authority.** Per `XE2`
every `yes` needs a citable source. **I have verified two rows against sources I actually opened, and
everything else is `unknown_to_code`** — which the order names as legitimate and preferred over a
guess. ⚠⚠ **I am not converting general clinical knowledge into log entries**, which is the exact
thing `P-004` argues against in other people's work and which `WD` caught the Planner doing.

| HPA category | pools distinct subtypes? | basis |
| --- | --- | --- |
| `breast cancer` | **yes** | ⚠ HPA's own documentation: *"breast cancer includes both ductal and lobular cancer"* (`v22.proteinatlas.org/about/assays+annotation`, read 2026-08-21). **A supplier-documented subdivision, not a clinical claim of mine** |
| `lung cancer` | **yes** | ⚠ same source: *"lung cancer includes both squamous cell carcinoma and adenocarcinoma"* |
| `liver cancer` | **yes** | ⚠ same source: *"liver cancer includes both hepatocellular and cholangiocellular carcinoma"* |
| the other **17** | ⚠ **`unknown_to_code`** | **no source opened.** The Planner's list names plausible splits for most of them; **none is cited here, and none should enter an entry until it is** |

⚠ **The three `yes` rows are the three HPA itself documents** (§1 of the `XB` document). **That is not
a coincidence — it is the only evidence I have that does not require me to assert clinical fact.**

---

## §3 — `XF` — the one that reaches our own scoring

### `XF1` — cohort targets that are, or may be, subtype-defining

`data/adc_reference_mapping.csv` carries **13 data rows over 12 distinct antigens**, all in-cohort:

| antigen | agent | HPA category it would be scored in |
| --- | --- | --- |
| **`ERBB2`** | ado-trastuzumab emtansine · trastuzumab deruxtecan | `breast cancer`, `stomach cancer` |
| **`NECTIN4`** | enfortumab vedotin | `urothelial cancer` |
| **`EGFR`** | depatuxizumab mafodotin | `glioma`, `lung cancer` |
| **`FGFR3`** | LY3076226 | `urothelial cancer` |
| `CD276` · `SLC39A6` · `CDCP1` · `MERTK` · `SLC3A2` · `JAG1` · `UPK1B` · `CDH11` | 8 further agents | various |

⚠ **What the file does NOT cover, stated because the order asked:**
- ⚠⚠ **Group C is empty** — no approved out-of-cohort ADC targets are curated, so **TROP2, CLDN18.2,
  FRα, PSMA, CD79b are absent from this file entirely**. Half the biomarkers `XF` names to look at
  are not in our tree.
- **`CD30`/`TNFRSF8` is a census protein, not one of the 82**, so it is outside this roster too.
- The roster's own header calls the count **"a floor, not a total"**: `CXCR5`, `MSLN` and `MUC16` are
  routed probable-positive and **unverified**.

**⚠ So `XF1`'s honest answer is: at most 4 of the 82 are plausibly subtype-defining in an HPA
category — `ERBB2`, `NECTIN4`, `EGFR`, `FGFR3` — and only `ERBB2` is one I would assert without a
source I have not opened.** The rest are `unknown_to_code` for the same reason as `XE`.

### `XF2` — ⚠ NOT REPORTED, and the reason is `XE`

Measuring dilution requires the **published prevalence of each subtype**, and `XE2` requires a
citation per row. **I have not opened those sources**, and the order says *measure it, do not
estimate it*. ⚠⚠ **An uncited prevalence multiplied by a measured staining fraction is a fabricated
number with a real number's shape.** Reported as not done.

### `XF3` — ⚠ does this affect the SCORER? **NO. Plainly no, and the finding is narrower than feared.**

Read from `core/scorer.py`, not assumed. The six pre-registered features (`D-027`) are:

```
ecd_length · radius_of_gyration · mean_plddt_ecd · membrane_proximal_plddt
sasa_normalized · largest_patch_fraction
```

**All six are structural or confidence quantities.** `core/scorer.py` imports `core.features` and
nothing from the clinical or expression layer. ⚠ **There is no expression term in the model, so a
pooled tumour category cannot dilute a score that never reads tumour staining.**

**⚠⚠ WHERE IT DOES REACH, AND THIS IS THE PART WORTH KEEPING:**
1. **The clinical layer on every card** — the tumour panel a reader uses to judge a target. Pooling
   is fully in force there.
2. ⚠ **The COMPARATOR, not the model.** The project's headline claim is that the structural ranking
   is *"not distinguishable from ranking the targets by expression and prior evidence"*. **The
   evidence comparator is Kathad's 1–5 score, published for only 17 of 82** — and `D-053`'s
   expression grid is quasi-H-score over HPA's pooled categories. **If the comparison arm is diluted
   for exactly the targets that work best, the comparison is affected even though the model is not.**

⚠ **That is a narrower finding than "the scorer is wrong", and it is reported at the same weight**,
per the order's own instruction. **The score is untouched. The thing the score is compared against
may not be.**

---

## §4 — What this document does NOT do

- ⚠⚠ **No contrast, no ratio** — `XD` stopped that line, per §4 of the order.
- **No subdivision of any HPA category.** HPA has no codes and cannot be subdivided.
- ⚠ **No clinical claim without a source I opened.** 17 of 20 `XE` rows and 3 of 4 `XF1` rows are
  `unknown_to_code`, deliberately.
- **`XF2` not computed.**
