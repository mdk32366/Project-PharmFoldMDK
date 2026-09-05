# Decision ship index

> **This is not the living log.** Authoritative `### D-NNN` entries live in
> [`README.md`](README.md). Write new decisions there first (append-at-top). This
> file is a thin index of which id **ships** which work, so a PR or review cannot
> treat a PLAN id as a BUILD GO.

## Active ship — D-127-B (UI four-path honesty + the mandatory Method addendum)

- **D-127-B ships UI four-path honesty and the Spec §7 Method addendum**
  (this PR) — [`app/piecewise_kabsch_path_read.py`](../app/piecewise_kabsch_path_read.py)
  projects A's sibling `piecewise_kabsch/{parent_id}/` tree onto
  `assembly_review.four_path`; the review card names **four** paths
  (assembler / `kabsch/` / `confidence_kabsch/` / `piecewise_kabsch/`)
  with **one row per domain piece** and no seam average; the owner
  markdown [`method-hold48-tiles.md`](method-hold48-tiles.md) and the
  `/method` MethodNote gain the D-127-B addendum. B **reads** A's tree;
  B does **not** re-implement persist and does **not** edit
  `hold48_piecewise_kabsch.py`. Default served = assembler until a Matt
  swap GO. Cite D-127-A `e49bf34` + Spec §6 + §7.
  ⚠ **This PR discharges the mandatory Method obligation.** Spec §7
  forbids a silent code-only ship; D-127 is not “done” without the
  addendum, and the addendum is a deliverable of this PR rather than a
  follow-up. ⚠ **No ops restitch of the 27.** ⚠ **10.0 Å gate stays.**
- **D-127-A already shipped** the piecewise / domain-aware Kabsch core
  BUILD on `main` (`e49bf34` / #244) —
  [`core/hold48_piecewise_kabsch.py`](../core/hold48_piecewise_kabsch.py)
  + CLI [`scripts/piecewise_kabsch_restitch.py`](../scripts/piecewise_kabsch_restitch.py).
  Per-domain weighted Kabsch (no trim) → existing `winning_tile`.
  Sibling tree `piecewise_kabsch/{parent_id}/`.
  `hold48_kabsch.py` and `hold48_confidence_kabsch.py` are **not
  edited**. **CPU, no rent.** A does **not** discharge the Method
  obligation (Spec §7 — mandatory at B); D-127-B, above, does.
- **D-127 already shipped** the piecewise / domain-aware Kabsch Spec
  on `main` (`00fa76d` / #243) —
  [`SPEC-piecewise-domain-kabsch.md`](SPEC-piecewise-domain-kabsch.md).
  Multi-rigid per UniProt domain; **no trim loop**; 10.0 Å gate STAYS.
  Primary three: 2939 / 3272 / 3432. CLI of the 27 for confusion vs
  D-125 and D-126. 0-of-3 recovered allowed.
  ⚠ **Method obligation:** Method must surface D-127 and the
  stitch-path train when the path exists (Spec §7). The Method
  addendum is **mandatory** before calling D-127 “done.” No silent
  code-only. A does **not** discharge it.
  D-127-B (this PR) discharges it.
- **D-126-B already shipped** **UI triple-path honesty only** on
  `main` (`abbcd00` / #242): name assembler, D-125 Kabsch-path, and
  D-126 `confidence_kabsch/` artifacts as three populations when A's
  sibling tree is on disk; B **reads** it; B does **not** re-implement
  persist. Assembler remains the default served PDB until a Matt swap
  GO. When the tree is missing, do not imply a D-126 path exists and
  do not invent RMSD / trim counts. Cite Spec §6 +
  `#### D-126 amendment 1` + D-126-A `aa8aa02`.
- **D-126-A already shipped** the overlap-confidence Kabsch core BUILD
  on `main` (`aa8aa02` / #241) —
  [`core/hold48_confidence_kabsch.py`](../core/hold48_confidence_kabsch.py)
  + CLI [`scripts/confidence_kabsch_restitch.py`](../scripts/confidence_kabsch_restitch.py).
  Sibling tree `confidence_kabsch/{parent_id}/`. `hold48_kabsch.py` is
  **not edited** in this PR.
- **D-126 ships the overlap-confidence Kabsch Spec** (already on `main`,
  `d59be6b` / #239 + amendment 1 `b32f9db` / #240) —
  [`SPEC-overlap-confidence-kabsch.md`](SPEC-overlap-confidence-kabsch.md).
- **D-125 ships the Kabsch restitch Spec** (already on `main`,
  `fbe8978` / #234). [`SPEC-kabsch-restitch.md`](SPEC-kabsch-restitch.md).
- **D-125-A already shipped** on `main` (`26a40a8` / #237).
  `core/hold48_kabsch.py` is **not edited** in this PR.
- **D-125-B ships** **UI dual-path honesty only** (already on `main`,
  `aa8d3f1` / #238): name assembler and Kabsch-path artifacts as two
  populations; A already writes the sibling `kabsch/{parent_job_id}/`
  tree; B **reads** it; B does **not** re-implement persist. Assembler
  remains the default served PDB. Cite D-125-A `26a40a8` + Spec §6.
- **D-124 A+B already shipped** on `main` (`57f429d` / #236).
- ⚠ **Seams are not scientifically solved.** Piecewise Kabsch is a
  multi-rigid transform of already-emitted ESMFold tiles, not a
  jointly placed holoprotein. Production triple-path (assembler /
  D-125 Kabsch / D-126 confidence) stays until D-127 ops. Assembler
  + D-125 Kabsch + D-126 confidence stay callable. Default served =
  assembler.
- ⚠ **10.0 Å gate STAYS.** Do not raise it. No trim loop. No
  threshold Spec-as-fix. No named-exclusion-as-fix.
- **D-126 amendment 1** (already on `main`, same D-id): pins
  `rmsd_full_overlap_angstrom` + `max_ca_jump_angstrom`; ε = **1e-3**
  and the weighted RMSD formula; floor-then-Kabsch-then-trim;
  all-or-nothing parent refuse (`_clear_success_artifacts` spirit);
  ops confusion vs D-125 (`n_d125_pass_d126_refuse` is a **named
  finding**); **0-of-5** recovered is allowed.

Full entries: [`README.md` § D-127-B](README.md#d-127-b--ui-four-path-honesty--the-mandatory-d-127-method-addendum),
[`README.md` § D-127-A](README.md#d-127-a--piecewise--domain-aware-kabsch-core-per-domain-weighted-fit-no-trim-then-existing-winning_tile),
[`README.md` § D-127](README.md#d-127--piecewise--domain-aware-kabsch-spec-multi-rigid-fit-then-existing-winning_tile-docs-only),
[`README.md` § D-126-B](README.md#d-126-b--ui-triple-path-honesty-name-assembler-d-125-kabsch-path-and-d-126-confidence-kabsch-artifacts-without-colliding-them),
[`README.md` § D-126-A](README.md#d-126-a--overlap-confidence-kabsch-core-trimmed--plddt-weighted-fit-then-existing-winning_tile),
[`README.md` § D-126](README.md#d-126--overlap-confidence-kabsch-spec-trimmed--plddt-weighted-fit-then-existing-winning_tile-docs-only),
[`README.md` § D-125-B](README.md#d-125-b--ui-dual-path-honesty-name-assembler-and-kabsch-path-artifacts-without-colliding-them),
[`README.md` § D-125](README.md#d-125--kabsch-restitch-spec-overlap-cα-align-then-existing-winning_tile-stitch-d-125-a-core-build).
Spec: [`SPEC-piecewise-domain-kabsch.md`](SPEC-piecewise-domain-kabsch.md).

## Nearby ids (do not conflate)

| Id | Role | Ships? |
| --- | --- | --- |
| **D-127 Spec** | Piecewise / domain-aware Kabsch Spec (docs only) | Already shipped on `main` (#243 / `00fa76d`). |
| **D-127-A** | Core BUILD (per-domain weighted Kabsch → `winning_tile`; no trim; CPU, no rent) | Already shipped on `main` (#244 / `e49bf34`). |
| **D-127-B** | UI four-path honesty + **mandatory Method addendum** (reads `piecewise_kabsch/`) | **Yes — this PR.** Discharges Spec §7; D-127 is “done” only with it. |
| **D-126 Spec** | Overlap-confidence Kabsch Spec (docs only) | Already shipped on `main` (#239 / `d59be6b` + #240 / `b32f9db`). |
| **D-126-A** | Core BUILD (weighted + trimmed overlap Cα → `winning_tile`) | Already shipped on `main` (#241 / `aa8aa02`). |
| **D-126-B** | UI triple-path honesty (reads `confidence_kabsch/`) | Already shipped on `main` (#242 / `abbcd00`). |
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
| **D-117** | Parent PLAN / evaluation stance | No. Plan only. Kabsch park now points at D-125; D-126 is the overlap-confidence follow-on Spec; D-127 is the piecewise / domain-aware follow-on Spec. |
| ADC-C-A | Pipeline + access data + API | Already shipped on `main` (#235 / `b71bade`). |
| F-004 ingest | Ranking-set expansion | No. Not this PR. |
