# Decision ship index

> **This is not the living log.** Authoritative `### D-NNN` entries live in
> [`README.md`](README.md). Write new decisions there first (append-at-top). This
> file is a thin index of which id **ships** which work, so a PR or review cannot
> treat a PLAN id as a BUILD GO.

## Active ship — D-126 Spec (overlap-confidence Kabsch docs)

- **D-126 ships the overlap-confidence Kabsch Spec** (docs only) —
  [`SPEC-overlap-confidence-kabsch.md`](SPEC-overlap-confidence-kabsch.md):
  pLDDT-weighted + residual-trimmed Kabsch on overlap Cα → transform
  tile → existing `winning_tile` stitch. Refuse v1 defaults stay
  (`n_ca_eff < 3`, weighted RMSD `> 10.0 Å`, singular/degenerate
  covariance). Primary inventory is the five D-125 REFUSE parents;
  CLI still re-runs the 27. Seams are **not** scientifically solved.
- **D-126-A / D-126-B are NOT this PR.** Those are later code BUILDs
  (A = core weighted + trimmed Kabsch + refuse + feed assembler, no UI,
  no rent; B = UI triple-path honesty). Default served = assembler
  until a Matt swap GO.
- **D-125 ships the Kabsch restitch Spec** (already on `main`,
  `fbe8978` / #234). [`SPEC-kabsch-restitch.md`](SPEC-kabsch-restitch.md).
- **D-125-A already shipped** on `main` (`26a40a8` / #237).
- **D-125-B ships** **UI dual-path honesty only** (already on `main`,
  `aa8d3f1` / #238): name assembler and Kabsch-path artifacts as two
  populations; A already writes the sibling `kabsch/{parent_job_id}/`
  tree; B **reads** it; B does **not** re-implement persist. Assembler
  remains the default served PDB. Cite D-125-A `26a40a8` + Spec §6.
- **D-124 A+B already shipped** on `main` (`57f429d` / #236).
- ⚠ **Seams are not scientifically solved.** Weighted Kabsch is a
  rigid transform of already-emitted ESMFold tiles, not a jointly
  placed holoprotein. Production dual-path (22 D-125 Kabsch / 5
  assembler) stays until D-126 code + ops.
- ⚠ **10.0 Å gate STAYS.** Trim / weight change the fit set, not the
  gate. No threshold Spec-as-fix. No named-exclusion-as-fix.

Full entries: [`README.md` § D-126](README.md#d-126--overlap-confidence-kabsch-spec-trimmed--plddt-weighted-fit-then-existing-winning_tile-docs-only),
[`README.md` § D-125-B](README.md#d-125-b--ui-dual-path-honesty-name-assembler-and-kabsch-path-artifacts-without-colliding-them),
[`README.md` § D-125](README.md#d-125--kabsch-restitch-spec-overlap-cα-align-then-existing-winning_tile-stitch-d-125-a-core-build).
Spec: [`SPEC-overlap-confidence-kabsch.md`](SPEC-overlap-confidence-kabsch.md).

## Nearby ids (do not conflate)

| Id | Role | Ships? |
| --- | --- | --- |
| **D-126 Spec** | Overlap-confidence Kabsch Spec (docs only) | **Yes — this PR.** |
| **D-126-A** | Core BUILD (weighted + trimmed overlap Cα → `winning_tile`) | **No.** Later Emma GO. No rent in A. |
| **D-126-B** | UI triple-path honesty (reads `confidence_kabsch/`) | **No.** After A. |
| **D-125-B** | UI dual-path honesty only (A already writes `kabsch/{parent}/`) | Already shipped on `main` (#238 / `aa8d3f1`). |
| **D-125-A** | Kabsch core BUILD (overlap Cα → transform → `winning_tile`) | Already shipped on `main` (#237 / `26a40a8`). |
| **D-125 Spec** | Kabsch restitch Spec (docs only) | Already shipped on `main` (#234 / `fbe8978`). |
| **D-124** | ADC-C-B `/adcs` Pipeline + Access UI BUILD GO (A already on `main`) | Already shipped on `main` (#236 / `57f429d`). |
| **D-123** | Nectin Doc → `/about` AdcContext BUILD GO | Already shipped on `main` (#231 / `2ffd4f8`). |
| **D-122** | ADC-B `/adcs` + `/adcs/:id` UI BUILD GO | Already shipped on `main` (#232 / `86f8a10`). |
| **D-121** | Method hold-48 8th-grade explainer BUILD GO | Already shipped on `main` (#233 / `ff51867`). |
| **D-120** | Phase 2 review UI BUILD GO | Already shipped on `main` (#229 / `04023a8`). |
| **D-119** | ADC-A catalog + thin read API BUILD GO | Already shipped on `main` (#228 / `b4f0b02`). |
| **D-118** | Phase 1 P0 honesty BUILD GO | Already shipped on `main` (#227). |
| **D-117** | Parent PLAN / evaluation stance | No. Plan only. Kabsch park now points at D-125; D-126 is the overlap-confidence follow-on Spec. |
| ADC-C-A | Pipeline + access data + API | Already shipped on `main` (#235 / `b71bade`). |
| F-004 ingest | Ranking-set expansion | No. Not this PR. |
