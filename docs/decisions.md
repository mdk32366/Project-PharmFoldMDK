# Decision ship index

> **This is not the living log.** Authoritative `### D-NNN` entries live in
> [`README.md`](README.md). Write new decisions there first (append-at-top). This
> file is a thin index of which id **ships** which work, so a PR or review cannot
> treat a PLAN id as a BUILD GO.

## Active ship — D-122 (ADC-B UI)

- **D-122 ships ADC-B** (`/adcs` sortable index + `/adcs/:id` baseball cards;
  nav **ADCs**; every field rendered as `{value, source, as_of, confidence}`;
  cancer type is the named v1 absence — indication is not an ADC-A field).
- **Parent data is D-119** — [`data/adcs/adcs.v1.json`](../data/adcs/adcs.v1.json)
  + `GET /api/adcs` + `GET /api/adcs/{id}` (`b4f0b02` / #228). D-122 does not
  rewrite the catalog or invent a field D-119 refused.
- **D-120 is Phase 2 review UI**, already on `main` (`04023a8` / #229). Do not
  reuse that integer for ADC-B.
- **D-121 is Method hold-48**, out of this GO. Do not spend it here.

Full entry: [`README.md` § D-122](README.md#d-122--adc-b-adcs-index--adcsid-baseball-cards-consume-the-d-119-catalog).
Parent data: [`README.md` § D-119](README.md#d-119--adc-a-fda-approved-catalog-is-a-dated-json-contract-not-a-ui-and-not-a-science-invention).

## Nearby ids (do not conflate)

| Id | Role | Ships? |
| --- | --- | --- |
| **D-122** | ADC-B `/adcs` + `/adcs/:id` UI BUILD GO | **Yes — this PR.** |
| **D-121** | Method hold-48 | No. Later GO. Not written here. |
| **D-120** | Phase 2 review UI BUILD GO | Already shipped on `main` (#229 / `04023a8`). |
| **D-119** | ADC-A catalog + thin read API BUILD GO | Already shipped on `main` (#228 / `b4f0b02`). |
| **D-118** | Phase 1 P0 honesty BUILD GO | Already shipped on `main` (#227). |
| **D-117** | Parent PLAN / evaluation stance | No. Plan only. |
| ADC-C | Pipeline + Right-to-Try | No. Later GO. |
| Nectin-4 `/about` | AdcContext / ABOUT-COPY | No. Separate PR. |
| Kabsch / restitch | PARKED (D-117) | No. Not this PR. |
| F-004 ingest | Ranking-set expansion | No. Not this PR. |
