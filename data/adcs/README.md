# ADC catalogs (D-119 / ADC-A, D-124 / ADC-C-A)

Three sibling files. Do **not** merge them.

| File | Scope | Ships |
| --- | --- | --- |
| `adcs.v1.json` | FDA-approved / currently marketed | D-119 / ADC-A |
| `adcs.pipeline.v1.json` | investigational (`pipeline_investigational`) | D-124 / ADC-C-A |
| `access.v1.json` | trials + Right-to-Try informational framing | D-124 / ADC-C-A |

Every field is `{value, source, as_of, confidence}`. Completeness is
`floor_not_census` — a dated pin, not a census.

Two openFDA endpoints back `adcs.v1.json` and they answer different
questions: `drugsfda.json` is **approval identity** (D-119) and `label.json`
is the **§1 indication text** (D-136). Neither runs in the gate.

ADC-B (`/adcs` Approved shelf, **D-122**) consumes `adcs.v1.json` via
`GET /api/adcs`. ADC-C-A serves the pipeline and access files via
`GET /api/adcs/pipeline`, `GET /api/adcs/pipeline/{id}`, and
`GET /api/adcs/access`. ADC-C-B (**D-124** UI) consumes those three
routes on `/adcs` (Pipeline shelf + Access panel + `/adcs/pipeline/:id`).

The scorer's Group B/C file (`data/adc_reference_mapping.csv`, D-029 / D-040)
is a **different object**. Pipeline v1 starts from that file's already-cited
non-approved rows and does not import the scorer module.

Access is **NOT medical advice, NOT legal advice, and NOT a treatment
recommendation.**

## How a row gets here

1. Drugs@FDA / openFDA `drugsfda.json` is authority for **approval identity**
   (application number, brand, active ingredient, sponsor, marketing status,
   ORIG-AP date).
2. Antigen → UniProt is a **reviewed human assignment**. Drugs@FDA has no
   antigen field (D-029).
3. openFDA `label.json` is authority for the **indication text** — §1
   INDICATIONS AND USAGE of the SPL (**D-136**). See below.
4. Three dates stay distinct: `approvals_reconciled_as_of`,
   `antigen_mapping_reviewed_as_of` and `indications_reviewed_as_of`.

A count of rows is a pin of **this file on that reconciliation date**, not a
scientific constant. Completeness is a **floor**, dated and detectable.

## Cancer type (D-136) — two fields, and the audit between them

Each approved row carries a pair:

| Field | Confidence | What it is |
| --- | --- | --- |
| `cancer_type` | `reviewed` | a **list** of tumour types, reduced by a human from §1 |
| `label_indications_verbatim` | `official` | FDA's §1 text **as the endpoint returned it** |

⚠ **`core/adc_catalog.py` refuses to load the file if any `cancer_type` token is
not a literal substring of that row's own `label_indications_verbatim`** (case
and punctuation folded). A tumour type typed from memory does not fail review —
it fails the gate. A non-null `cancer_type` therefore **requires** stored label
text to audit it against; there is no "trust me" path.

Other rules the loader enforces:

- The token names the **tumour**, never the stage, line of therapy, or
  biomarker. Those qualifiers stay in the verbatim text, which is why the text
  is stored rather than summarised away.
- ⚠ **No HPA / staining / census / `/api/associations` source, ever** (D-093:
  staining is not an FDA indication). The denylist reads `source`, never
  `value` — FDA's own text says *staining* where it describes a companion
  diagnostic, and rejecting a true label for quoting FDA would be a bug.
- `derived` confidence is refused: a cancer type cannot be computed from a slug.
- A missing indication is a **named absence** — `value: null` with a `source`
  naming the query that came back without text. Never a blank.
- Pipeline rows carry **no** indication field at all (D-124 schema; no Spec
  authorised one).

⚠ The label is the one **in force on the retrieval date**, not the ORIG-AP
indication. Several v1 labels are newer than `approvals_reconciled_as_of`, and
their indication sets have grown since first approval.

## Emma's weekly Drugs@FDA watch (hook — not built here)

Weekly drift detection is **Emma's ops lane**, not a CI check and not a
script in this PR (D-029: a live FDA query must not redden the gate).

When Emma runs the watch, the useful output is:

- new Drugs@FDA approvals that look like ADCs and are **absent** from
  `adcs.v1.json`;
- a v1 `application_number` that **no longer resolves**;
- a marketing-status change on a v1 row;
- **D-136:** an SPL whose `version` / `effective_time` has moved past the one
  cited in a row's `cancer_type.source`, which means the **indication set may
  have changed** even though approval identity has not.

The watch **detects**. It does **not** assign an antigen or edit this file.
Assigning a target to a new approval is a human read every time (D-029 /
D-119). Open an issue; do not auto-merge rows.

Suggested query (ops, not the gate): brand or application lookup against
`https://api.fda.gov/drug/drugsfda.json`, then diff application numbers
against `adcs[].application_number.value`.
