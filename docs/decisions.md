# Decision ship index

> **This is not the living log.** Authoritative `### D-NNN` entries live in
> [`README.md`](README.md). Write new decisions there first (append-at-top). This
> file is a thin index of which id **ships** which work, so a PR or review cannot
> treat a PLAN id as a BUILD GO.

## Active ship — D-125-A (Kabsch core)

- **D-125-A ships** the Kabsch restitch **core BUILD**: overlap Cα Kabsch
  → refuse v1 defaults → transform the moving tile → feed the existing
  `winning_tile` / `write_stitched` assembler. No UI. New path
  (`core/hold48_kabsch.py` + `scripts/kabsch_restitch.py`); the assembler
  stays callable. Sibling `kabsch/{parent_job_id}/` artifacts with
  provenance. CLI limited to the 27 inventory ids — not a Fly re-query.
- **D-125 ships the Kabsch restitch Spec** (already on `main`,
  `fbe8978` / #234). [`SPEC-kabsch-restitch.md`](SPEC-kabsch-restitch.md).
  This A PR implements that Spec; where they differ, the log governs.
- **D-125-B is NOT this PR.** B is **UI dual-path honesty only**.
  A already writes the sibling `kabsch/{parent_job_id}/` tree
  (`provenance.json`, `seams.jsonl`, transformed tiles on accept,
  then existing `write_stitched` names).
- **D-124 A+B already shipped** on `main` (`57f429d` / #236). The wait
  that gated A is discharged.
- ⚠ **Seams are not scientifically solved.** Kabsch is a rigid transform
  of already-emitted ESMFold tiles, not a jointly placed holoprotein.

Full entries: [`README.md` § D-125](README.md#d-125--kabsch-restitch-spec-overlap-cα-align-then-existing-winning_tile-stitch-d-125-a-core-build),
[`README.md` § D-124](README.md#d-124--adc-c-a-pipeline-catalog--accessrtt-payload-are-dated-json-contracts-adc-c-b-is-the-adcs-consumer).
Spec: [`SPEC-kabsch-restitch.md`](SPEC-kabsch-restitch.md).

## Nearby ids (do not conflate)

| Id | Role | Ships? |
| --- | --- | --- |
| **D-125-A** | Kabsch core BUILD (overlap Cα → transform → `winning_tile`) | **Yes — this PR.** |
| **D-125 Spec** | Kabsch restitch Spec (docs only) | Already shipped on `main` (#234 / `fbe8978`). |
| **D-125-B** | UI dual-path honesty only (A already writes `kabsch/{parent}/`) | **No.** After A. |
| **D-124** | ADC-C-B `/adcs` Pipeline + Access UI BUILD GO (A already on `main`) | Already shipped on `main` (#236 / `57f429d`). |
| **D-123** | Nectin Doc → `/about` AdcContext BUILD GO | Already shipped on `main` (#231 / `2ffd4f8`). |
| **D-122** | ADC-B `/adcs` + `/adcs/:id` UI BUILD GO | Already shipped on `main` (#232 / `86f8a10`). |
| **D-121** | Method hold-48 8th-grade explainer BUILD GO | Already shipped on `main` (#233 / `ff51867`). |
| **D-120** | Phase 2 review UI BUILD GO | Already shipped on `main` (#229 / `04023a8`). |
| **D-119** | ADC-A catalog + thin read API BUILD GO | Already shipped on `main` (#228 / `b4f0b02`). |
| **D-118** | Phase 1 P0 honesty BUILD GO | Already shipped on `main` (#227). |
| **D-117** | Parent PLAN / evaluation stance | No. Plan only. Kabsch park now points at D-125. |
| ADC-C-A | Pipeline + access data + API | Already shipped on `main` (#235 / `b71bade`). |
| F-004 ingest | Ranking-set expansion | No. Not this PR. |
