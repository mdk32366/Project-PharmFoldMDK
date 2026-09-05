# Decision ship index

> **This is not the living log.** Authoritative `### D-NNN` entries live in
> [`README.md`](README.md). Write new decisions there first (append-at-top). This
> file is a thin index of which id **ships** which work, so a PR or review cannot
> treat a PLAN id as a BUILD GO.

## Active ship — D-125 Spec (Kabsch restitch docs)

- **D-125 ships the Kabsch restitch Spec** (docs only) —
  [`SPEC-kabsch-restitch.md`](SPEC-kabsch-restitch.md): Kabsch on overlap
  Cα → transform tile → existing `winning_tile` stitch. Refuse v1 defaults
  named (`n_ca < 3`, RMSD `> 10.0 Å`, singular/degenerate covariance).
  27-id inventory is the existing census (not a Fly re-query). Seams are
  **not** scientifically solved.
- **D-125-A / D-125-B are NOT this PR.** Those are later code BUILDs
  (A = core Kabsch + refuse + feed assembler, no UI; B = persist + UI
  dual-path honesty). They **wait until D-124 A+B is on `main`.**
- **Parent PLAN is D-117** —
  [`PLAN-ui-post-wave2-endstate.md`](PLAN-ui-post-wave2-endstate.md)
  §5 Kabsch park → D-125. D-117 is not a BUILD.
- **Parent honesty is D-118.** Parent review is D-120. Parent Method
  (assembler ≠ Kabsch *today*) is D-121. All already on `main`.
- **D-124 is ADC-C** (pipeline / Right-to-Try), a parallel lane. This
  Spec does not spend that integer and does not edit ADC-C files.

Full entry: [`README.md` § D-125](README.md#d-125--kabsch-restitch-spec-overlap-cα-align-then-existing-winning_tile-stitch-docs-only).
Spec: [`SPEC-kabsch-restitch.md`](SPEC-kabsch-restitch.md).

## Nearby ids (do not conflate)

| Id | Role | Ships? |
| --- | --- | --- |
| **D-125 Spec** | Kabsch restitch Spec (docs only) | **Yes — this PR.** |
| **D-125-A** | Kabsch core BUILD (overlap Cα → transform → `winning_tile`) | **No.** Later Emma GO. Waits on D-124 A+B. |
| **D-125-B** | Kabsch persist + UI dual-path honesty | **No.** After A. |
| **D-124** | ADC-C (pipeline / Right-to-Try) | **No.** Parallel lane. Not this PR. Reserved until that GO writes `### D-124`. |
| **D-123** | Nectin Doc → `/about` AdcContext BUILD GO | Already shipped on `main` (#231 / `2ffd4f8`). |
| **D-122** | ADC-B `/adcs` + `/adcs/:id` UI BUILD GO | Already shipped on `main` (#232 / `86f8a10`). |
| **D-121** | Method hold-48 8th-grade explainer BUILD GO | Already shipped on `main` (#233 / `ff51867`). |
| **D-120** | Phase 2 review UI BUILD GO | Already shipped on `main` (#229 / `04023a8`). |
| **D-119** | ADC-A catalog + thin read API BUILD GO | Already shipped on `main` (#228 / `b4f0b02`). |
| **D-118** | Phase 1 P0 honesty BUILD GO | Already shipped on `main` (#227). |
| **D-117** | Parent PLAN / evaluation stance | No. Plan only. Kabsch park now points at D-125. |
| F-004 ingest | Ranking-set expansion | No. Not this PR. |
