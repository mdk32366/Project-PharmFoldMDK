# Decision ship index

> **This is not the living log.** Authoritative `### D-NNN` entries live in
> [`README.md`](README.md). Write new decisions there first (append-at-top). This
> file is a thin index of which id **ships** which work, so a PR or review cannot
> treat a PLAN id as a BUILD GO.

## Active ship — D-120 (Phase 2 review UI)

- **D-120 ships Phase 2 review UI** (assembled-parent `/census/:id`: kind badge,
  stitch_readiness counts, tile table, chosen-vs-spare lower ids, PAE yes/no,
  `stitched.*` / `tileN.*` downloads, assembler/seam banner from D-118; IGF2R
  two-population copy; Scorer one-liner — 27 not in F-004; Method / Provenance /
  Explainer addenda; structural-profile refuse on assemblies).
- **Parent PLAN is D-117** — [`PLAN-ui-post-wave2-endstate.md`](PLAN-ui-post-wave2-endstate.md)
  §3.6–3.7 / §6 Phase 2. D-117 is the evaluation stance. It is **not** an
  implementation GO and **not** a Kabsch GO.
- **Parent honesty GO is D-118** — Phase 1 P0 (`7cc6238` / #227). D-120 does not
  reopen identity, rental-closed, or assembler-banner rulings.
- **D-119 is ADC-A**, already on `main` (`b4f0b02` / #228). Do not reuse that
  integer for Phase 2 (Trinity ruling 2026-09-05; D-062-class collision).

Full entries: [`README.md` § D-120](README.md#d-120--phase-2-review-ui-assembled-parent-censusid-is-auditable-without-sql),
[`README.md` § D-118](README.md#d-118--phase-1-p0-honesty-one-census-protein-per-accession-rental-closed-assembler-not-kabsch),
[`README.md` § D-117](README.md#d-117--after-wave2-stitch-the-ui-still-speaks-a-pre-tile-language-inventory-first-no-kabsch-no-implementation-go).
ADC-A: [`README.md` § D-119](README.md#d-119--adc-a-fda-approved-catalog-is-a-dated-json-contract-not-a-ui-and-not-a-science-invention).

## Nearby ids (do not conflate)

| Id | Role | Ships? |
| --- | --- | --- |
| **D-120** | Phase 2 review UI BUILD GO | **Yes — this PR.** |
| **D-119** | ADC-A catalog + thin read API BUILD GO | Already shipped on `main` (#228 / `b4f0b02`). |
| **D-118** | Phase 1 P0 honesty BUILD GO | Already shipped on `main` (#227). |
| **D-117** | Parent PLAN / evaluation stance | No. Plan only. |
| D-115 / D-116 | Wave2 hold-48 ship / stitch + tile-window contract | Already shipped on `main`. |
| ADC-B | `/adcs` + `/adcs/:id` UI | No. Later GO. |
| ADC-C | Pipeline + Right-to-Try | No. Later GO. |
| Kabsch / restitch | PARKED (D-117) | No. Not this PR. |
| F-004 ingest | Ranking-set expansion | No. Disclosure only (D-109). |
