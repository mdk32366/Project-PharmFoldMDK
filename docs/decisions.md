# Decision ship index

> **This is not the living log.** Authoritative `### D-NNN` entries live in
> [`README.md`](README.md). Write new decisions there first (append-at-top). This
> file is a thin index of which id **ships** which work, so a PR or review cannot
> treat a PLAN id as a BUILD GO.

## Active ship — D-119 (ADC-A)

- **D-119 ships ADC-A**: FDA-approved catalog JSON (`data/adcs/adcs.v1.json`)
  plus thin `GET /api/adcs` and `GET /api/adcs/{id}`. Every field is
  `{value, source, as_of, confidence}`. No ADC-B UI. No pipeline / RTT
  (ADC-C). No Emma watcher (hook only). No Kabsch. No F-004. No AdcContext.
- **Parent Spec** is the Trinity Architect ADC-A binding (2026-09-05), after
  D-118 P0 merge. Full entry: [`README.md` § D-119](README.md#d-119--adc-a-fda-approved-catalog-is-a-dated-json-contract-not-a-ui-and-not-a-science-invention).

## Nearby ids (do not conflate)

| Id | Role | Ships? |
| --- | --- | --- |
| **D-119** | ADC-A catalog + thin read API BUILD GO | **Yes — this PR.** |
| **D-118** | Phase 1 P0 honesty BUILD GO | Already shipped on `main` (#227). |
| **D-117** | Parent PLAN / evaluation stance | No. Plan only. |
| ADC-B | `/adcs` + `/adcs/:id` UI | No. Later GO. |
| ADC-C | Pipeline + Right-to-Try | No. Later GO. |
| Phase 2 / D-117 P1 | Wave2 review UI | Parallel PR train. Do not mix. |
| Kabsch / restitch | PARKED (D-117) | No. Not this PR. |
