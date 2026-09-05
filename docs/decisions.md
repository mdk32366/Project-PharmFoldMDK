# Decision ship index

> **This is not the living log.** Authoritative `### D-NNN` entries live in
> [`README.md`](README.md). Write new decisions there first (append-at-top). This
> file is a thin index of which id **ships** which work, so a PR or review cannot
> treat a PLAN id as a BUILD GO.

## Active ship — D-123 (Nectin Doc → AdcContext)

- **D-123 ships** the Nectin-4/ADC Doc follow-on on existing `/about`
  (`AdcContext.jsx` only). Additive section: two tracks (Track A
  red-without-wet-bind; Track B ranking) and explicit
  "EV is not a universal V-key". Science copy is a verbatim extract of
  [`pharmfold-adc-nectin4-paper.md`](pharmfold-adc-nectin4-paper.md) Part 2
  via `ui/src/aboutPaper.js`. D-094 ABOUT-COPY / `PAPER_QUESTIONS` stay
  byte-identical. No second About route. No F-004 expand. No Kabsch.
  Does **not** edit `/adcs` (D-122 already shipped ADC-B on `main` at
  `86f8a10` / #232). Stays **draft** until Matt clears the two
  result-sounding Doc lines.
- **Parent Phase 2 review is D-120** — already on `main` (#229). D-120 named
  this as a later GO (*"Not Nectin-4 AdcContext"*).
- **D-094 amendment 1 dec 3 still governs** `/about`: questions, never a
  result; "asks whether", never "shows that".

Full entry: [`README.md` § D-123](README.md#d-123--nectin-4adc-doc-follow-on-lands-on-about-adccontext-two-tracks-no-second-route).
Owner Doc: [`pharmfold-adc-nectin4-paper.md`](pharmfold-adc-nectin4-paper.md).

## Nearby ids (do not conflate)

| Id | Role | Ships? |
| --- | --- | --- |
| **D-123** | Nectin Doc → `/about` AdcContext BUILD GO | **Yes — this PR.** Draft until Matt clears two Doc lines. |
| **D-122** | ADC-B `/adcs` + `/adcs/:id` UI BUILD GO | Already shipped on `main` (#232 / `86f8a10`). |
| **D-121** | Method hold-48 | No. Later GO. Not written here. |
| **D-120** | Phase 2 review UI BUILD GO | Already shipped on `main` (#229 / `04023a8`). |
| **D-119** | ADC-A catalog + thin read API BUILD GO | Already shipped on `main` (#228 / `b4f0b02`). |
| **D-118** | Phase 1 P0 honesty BUILD GO | Already shipped on `main` (#227). |
| **D-117** | Parent PLAN / evaluation stance | No. Plan only. |
| ADC-C | Pipeline + Right-to-Try | No. Later GO. |
| Kabsch / restitch | PARKED (D-117) | No. Not this PR. |
| F-004 ingest | Ranking-set expansion | No. Not this PR. |
