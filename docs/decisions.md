# Decision ship index

> **This is not the living log.** Authoritative `### D-NNN` entries live in
> [`README.md`](README.md). Write new decisions there first (append-at-top). This
> file is a thin index of which id **ships** which work, so a PR or review cannot
> treat a PLAN id as a BUILD GO.

## Active ship — D-121 (Method hold-48 8th-grade explainer)

- **D-121 ships** the owner-facing 8th-grade hold-48 Method write-up
  ([`method-hold48-tiles.md`](method-hold48-tiles.md)) plus an additive
  `/method` section in `MethodNote.jsx`. Tiles / overlap-as-glue / winner-tile
  assembler (not Kabsch); IGF2R ~88.76 Å disclosed not solved; rental CLOSED.
- **Parent honesty GO is D-118** — Phase 1 P0 (`7cc6238` / #227). D-121 does
  not reopen identity.
- **Parent Phase 2 review is D-120** — `04023a8` / #229. **#229 stays merged.
  Do not reopen it.**
- **Parent PLAN is D-117** — [`PLAN-ui-post-wave2-endstate.md`](PLAN-ui-post-wave2-endstate.md).
  D-117 is the evaluation stance. It is **not** an implementation GO and
  **not** a Kabsch GO.
- **D-122 is ADC-B**, already on `main` (`86f8a10` / #232). This PR does **not
  add** `/adcs` and must **not regress** those routes.
- **D-123 is the Nectin Doc → `/about` follow-on**, already on `main`
  (`2ffd4f8` / #231). This PR does not touch AdcContext.

Full entries: [`README.md` § D-121](README.md#d-121--method-hold-48-8th-grade-explainer-tiles-glue-winner-tile-assembler-not-kabsch),
[`README.md` § D-123](README.md#d-123--nectin-4adc-doc-follow-on-lands-on-about-adccontext-two-tracks-no-second-route),
[`README.md` § D-122](README.md#d-122--adc-b-adcs-index--adcsid-baseball-cards-consume-the-d-119-catalog),
[`README.md` § D-120](README.md#d-120--phase-2-review-ui-assembled-parent-censusid-is-auditable-without-sql).

## Nearby ids (do not conflate)

| Id | Role | Ships? |
| --- | --- | --- |
| **D-121** | Method hold-48 8th-grade explainer BUILD GO | **Yes — this PR.** |
| **D-123** | Nectin Doc → `/about` AdcContext BUILD GO | Already shipped on `main` (#231 / `2ffd4f8`). |
| **D-122** | ADC-B `/adcs` + `/adcs/:id` UI BUILD GO | Already shipped on `main` (#232 / `86f8a10`). |
| **D-120** | Phase 2 review UI BUILD GO | Already shipped on `main` (#229 / `04023a8`). |
| **D-119** | ADC-A catalog + thin read API BUILD GO | Already shipped on `main` (#228 / `b4f0b02`). |
| **D-118** | Phase 1 P0 honesty BUILD GO | Already shipped on `main` (#227). |
| **D-117** | Parent PLAN / evaluation stance | No. Plan only. |
| ADC-C | Pipeline + Right-to-Try | No. Later GO. |
| Kabsch / restitch | PARKED (D-117) | No. Not this PR. |
| F-004 ingest | Ranking-set expansion | No. Not this PR. |
