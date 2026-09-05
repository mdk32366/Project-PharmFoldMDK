# Decision ship index

> **This is not the living log.** Authoritative `### D-NNN` entries live in
> [`README.md`](README.md). Write new decisions there first (append-at-top). This
> file is a thin index of which id **ships** which work, so a PR or review cannot
> treat a PLAN id as a BUILD GO.

## Active ship — D-124 (ADC-C-A data + API)

- **D-124 ships ADC-C-A** (pipeline catalog + access/RTT informational payload
  + thin read API). Files:
  [`data/adcs/adcs.pipeline.v1.json`](../data/adcs/adcs.pipeline.v1.json) and
  [`data/adcs/access.v1.json`](../data/adcs/access.v1.json). Routes:
  `GET /api/adcs/pipeline`, `GET /api/adcs/pipeline/{id}`,
  `GET /api/adcs/access`. Every field is `{value, source, as_of, confidence}`.
  Completeness is `floor_not_census`. Phase vocab is the Architect closed set.
  Access carries a required NOT-medical / NOT-legal / NOT-a-treatment-recommendation
  disclaimer.
- **Does not edit `adcs.v1.json`.** Approved catalog stays D-119
  (`b4f0b02` / #228). Approved routes `GET /api/adcs` + `GET /api/adcs/{id}`
  are unchanged.
- **Not ADC-C-B.** No `/adcs` React changes, no AdcContext / Method rewrite.
- **D-125 ships the Kabsch restitch Spec** (docs only) — already on `main`
  (`fbe8978` / #234). [`SPEC-kabsch-restitch.md`](SPEC-kabsch-restitch.md).
- **D-125-A / D-125-B are NOT this PR.** Those are later code BUILDs
  (A = core Kabsch + refuse + feed assembler, no UI; B = persist + UI
  dual-path honesty). They **wait until D-124 A+B is on `main`.**
- **D-122 is ADC-B**, already on `main` (`86f8a10` / #232).
- **D-121 is Method hold-48**, already on `main` (`ff51867` / #233).
- **D-123 is the Nectin Doc → `/about` follow-on**, already on `main`
  (`2ffd4f8` / #231).

Full entries: [`README.md` § D-124](README.md#d-124--adc-c-a-pipeline-catalog--accessrtt-payload-are-dated-json-contracts-not-a-ui-and-not-advice),
[`README.md` § D-125](README.md#d-125--kabsch-restitch-spec-overlap-cα-align-then-existing-winning_tile-stitch-docs-only).
Parent approved catalog: [`README.md` § D-119](README.md#d-119--adc-a-fda-approved-catalog-is-a-dated-json-contract-not-a-ui-and-not-a-science-invention).
Spec: [`SPEC-kabsch-restitch.md`](SPEC-kabsch-restitch.md).

## Nearby ids (do not conflate)

| Id | Role | Ships? |
| --- | --- | --- |
| **D-124** | ADC-C-A pipeline + access/RTT data + API BUILD GO | **Yes — this PR.** |
| **D-125 Spec** | Kabsch restitch Spec (docs only) | Already shipped on `main` (#234 / `fbe8978`). |
| **D-125-A** | Kabsch core BUILD (overlap Cα → transform → `winning_tile`) | **No.** Later Emma GO. Waits on D-124 A+B. |
| **D-125-B** | Kabsch persist + UI dual-path honesty | **No.** After A. |
| **D-123** | Nectin Doc → `/about` AdcContext BUILD GO | Already shipped on `main` (#231 / `2ffd4f8`). |
| **D-122** | ADC-B `/adcs` + `/adcs/:id` UI BUILD GO | Already shipped on `main` (#232 / `86f8a10`). |
| **D-121** | Method hold-48 8th-grade explainer BUILD GO | Already shipped on `main` (#233 / `ff51867`). |
| **D-120** | Phase 2 review UI BUILD GO | Already shipped on `main` (#229 / `04023a8`). |
| **D-119** | ADC-A catalog + thin read API BUILD GO | Already shipped on `main` (#228 / `b4f0b02`). |
| **D-118** | Phase 1 P0 honesty BUILD GO | Already shipped on `main` (#227). |
| **D-117** | Parent PLAN / evaluation stance | No. Plan only. Kabsch park now points at D-125. |
| ADC-C-B | Pipeline / RTT UI | No. Later GO. |
| F-004 ingest | Ranking-set expansion | No. Not this PR. |
