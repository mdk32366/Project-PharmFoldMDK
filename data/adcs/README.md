# ADC catalog v1 (D-119 / ADC-A)

Checked-in roster of **FDA-approved** antibody-drug conjugates. Schema:
`adcs.v1.json`. Every field is `{value, source, as_of, confidence}`.

ADC-B (`/adcs` pages, **D-122**) consumes this file via `GET /api/adcs`.
Pipeline and Right-to-Try products are **ADC-C** — out of this file.

The scorer's Group B/C file (`data/adc_reference_mapping.csv`, D-029 / D-040)
is a **different object**. Do not merge them.

## How a row gets here

1. Drugs@FDA / openFDA is authority for **approval identity** (application
   number, brand, active ingredient, sponsor, marketing status, ORIG-AP date).
2. Antigen → UniProt is a **reviewed human assignment**. Drugs@FDA has no
   antigen field (D-029).
3. Two dates stay distinct: `approvals_reconciled_as_of` and
   `antigen_mapping_reviewed_as_of`.

A count of rows is a pin of **this file on that reconciliation date**, not a
scientific constant. Completeness is a **floor**, dated and detectable.

## Emma's weekly Drugs@FDA watch (hook — not built here)

Weekly drift detection is **Emma's ops lane**, not a CI check and not a
script in this PR (D-029: a live FDA query must not redden the gate).

When Emma runs the watch, the useful output is:

- new Drugs@FDA approvals that look like ADCs and are **absent** from
  `adcs.v1.json`;
- a v1 `application_number` that **no longer resolves**;
- a marketing-status change on a v1 row.

The watch **detects**. It does **not** assign an antigen or edit this file.
Assigning a target to a new approval is a human read every time (D-029 /
D-119). Open an issue; do not auto-merge rows.

Suggested query (ops, not the gate): brand or application lookup against
`https://api.fda.gov/drug/drugsfda.json`, then diff application numbers
against `adcs[].application_number.value`.
