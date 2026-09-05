# Decision ship index

> **This is not the living log.** Authoritative `### D-NNN` entries live in
> [`README.md`](README.md). Write new decisions there first (append-at-top). This
> file is a thin index of which id **ships** which work, so a PR or review cannot
> treat a PLAN id as a BUILD GO.

## Active ship — D-118

- **D-118 ships Phase 1 P0 honesty** (one census protein per accession; parent/assembled
  resolve; no tile-inflated `census_summary`; closed-rental / no "48 held" copy;
  GUIDE CLOSED; assembler / seam-not-solved on any stitched 3D; `stitched_plddt.json`
  sibling; unused spare tiles 3693/3695/3696 never a second protein).
- **Parent PLAN is D-117** — [`PLAN-ui-post-wave2-endstate.md`](PLAN-ui-post-wave2-endstate.md).
  D-117 is the evaluation stance and the three-phase map. It is **not** an
  implementation GO and **not** a Kabsch GO.
- **Do not rename D-118 mid-flight.** Trinity 2026-09-05: keep D-118 as the
  implement/ship decision id; cite D-117 as the parent PLAN.

Full entries: [`README.md` § D-118](README.md#d-118--phase-1-p0-honesty--one-census-protein-per-accession-post-wave2)
and [`README.md` § D-117](README.md#d-117--post-wave2-ui-endstate-plan--evaluation-stance-not-a-kabsch-go).

## Nearby ids (do not conflate)

| Id | Role | Ships? |
| --- | --- | --- |
| **D-117** | Parent PLAN / evaluation stance | No. Plan only. |
| **D-118** | Phase 1 P0 honesty BUILD GO | **Yes — this PR.** |
| D-115 / D-116 | Wave2 hold-48 ship / stitch + tile-window contract | Already shipped on `main`. |
| Kabsch / restitch | PARKED (D-117 §Phase 2) | No. Not this PR. |
