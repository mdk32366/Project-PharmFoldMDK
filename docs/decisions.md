# Decision ship index

> **This is not the living log.** Authoritative `### D-NNN` entries live in
> [`README.md`](README.md). Write new decisions there first (append-at-top). This
> file is a thin index of which id **ships** which work, so a PR or review cannot
> treat a PLAN id as a BUILD GO.

## Active ship — D-129-B (BUILD: Phase 5 named-refuse labels)

- **D-129-B ships the Phase 5 named-refuse LABELS on Method + UI**
  (**this PR**) — the **§3 re-label** that `### D-129` left **owed**,
  under the **Emma BUILD GO 2026-09-06** (*"Matt: Go"*) that Spec §8
  gated it on. ⚠ **D-129 did not pre-authorise this id**; the GO did.
  The **eight** parents — **2938, 2939, 3179, 3190, 3321, 3368, 3566**
  **+ 3432** — are labelled **named refuse / `accept-refuse`** on
  [`method-hold48-tiles.md`](method-hold48-tiles.md), on `/method`
  (`MethodNote.jsx`) and on the review card (`AssemblyReview.jsx`),
  from one signed fate registry
  ([`app/phase5_named_refuse.py`](../app/phase5_named_refuse.py))
  projected onto `assembly_review.phase5_fate`.
  ⚠ **The label is constructed carrying the disclosure.** The
  accept-refuse block holds the recorded D-128 OPS rollup — **PASS 0 /
  REFUSE 7 / FAIL 0 / SKIP 0**, `repaired_of_seven` = **0**, and the
  give-back `n_d125_pass_d128_refuse` = **5** /
  `n_d126_pass_d128_refuse` = **6** — so **no code path hands a surface
  the label without the numbers**. D-128-B's shipped disclosure is
  **untouched** and still guarded by content.
  ⚠ **Phase 4 stays cold:** **3272 / 3394** resolve to an **open**
  `phase-4-must-hunt` fate (`is_accept_refuse` **False**) and are never
  labelled accepted, retired, or closed.
  ⚠ **3432** is carried, **not re-ruled**, and is **not** counted into
  the D-128 seven. ⚠ **No accession field** exists in the registry —
  five of the seven have none on record (D-016).
  ⚠ **Labels only:** no `hold48_*.py` edit (four modules sha256-pinned),
  no threshold, no refuse reason, no artifact tree, no served byte, no
  ops run, no Fly / rent, no F-004. **10.0 Å / W = 32 / ε = 1e-3 stay;
  served stays assembler; D-126 remains best experimental and callable;
  both failed rescues stay disclosed. Never solved.** Draft PR; **no
  self-merge**; **Trinity merges**. Full entry: `### D-129-B` in
  [`README.md`](README.md).
- **D-129 already shipped the Phase 5 named-refuse Spec** on `main`
  (`1baf4c0` / #249) —
  [`SPEC-phase5-named-refuse.md`](SPEC-phase5-named-refuse.md).
  **Ruled by Matt SIGNED Phase 5 named-refuse 2026-09-05 ~17:58 PT, via
  Emma.** ⚠ **Its authority is over LABELS, not algorithms** — no
  geometry, no threshold, no artifact tree, no served byte changes.
  **Eight** parents are **`accept-refuse`**: **2938, 2939, 3179, 3190,
  3321, 3368, 3566** (the D-128 linker seven) **+ 3432** (already
  accept-refuse under signed triage — re-affirmed, not newly ruled).
  `accept-refuse` = **the recorded honest outcome of a refusal**: the
  join is **not held**, we say so, and we **stop hunting it**.
  UI / Method (**B**) must **label** those eight **named refuse /
  accept-refuse** and must **never** label them **open must-hunt**,
  **solved / fixed / repaired / aligned**, or **a D-128 miss** —
  **0-of-7 was pre-registered** as allowed by D-128 §1b / §3 / §11
  *before* the run.
  ⚠ **`accept-refuse` ≠ Method silence.** **B still must disclose** the
  recorded D-128 OPS rollup — **PASS 0 / REFUSE 7 / FAIL 0 / SKIP 0**,
  `repaired_of_seven` = **0**, and the **named confusion**
  `n_d125_pass_d128_refuse` = **5** / `n_d126_pass_d128_refuse` = **6**
  (`n_d127_pass_d128_refuse` = 0, `n_d127_refuse_d128_pass` = 0) — as
  recorded by Kaylee at tip `9e65cbf`, out_root
  `linker_seam_ops_2026-09-05`. ⚠ **Not re-measured; do not
  re-measure.** The label and the disclosure ship **together**.
  ⚠ **3272 / 3394 stay Phase 4 must-hunt** (`rmsd_gt_10` class), are
  **out of this Spec**, and move only on a **separate Matt GO** — **no
  RMSD Spec bleed**.
  ⚠ **NO linker-v2.** The stitch-algorithm family **freezes**: served
  stays **assembler**, the **10.0 Å** gate **stays** (W = 32, ε = 1e-3
  stay), **D-126 remains the best experimental path until proven
  otherwise**, and the **D-127 and D-128 failed rescues stay
  disclosed**.
  ⚠ **Seams are NOT solved** — accepting a refusal retires the
  **hunt**, not the **record**.
  ⚠ **Docs only in that PR: no UI / React, no `MethodNote.jsx`, no
  Method file edit** (§5 carried the 8th-grade excerpt as **authority
  only**, the same Spec-PR pattern as #243 / #246), **no `hold48_*.py`
  edit, no core algorithm change, no restitch / ops run / Fly / rent**.
  ⚠ **The §3 re-label it left owed is discharged by D-129-B above.**
  Full entry: `### D-129` in [`README.md`](README.md).
- **D-128-B already shipped UI linker / seam path honesty and the Spec
  §7 Method addendum** on `main` (`cd071d7` / #248) —
  [`app/linker_seam_path_read.py`](../app/linker_seam_path_read.py)
  projects A's sibling `linker_seam/{parent_id}/` tree onto
  `assembly_review.five_path`; the review card names **five** paths
  (assembler / `kabsch/` / `confidence_kabsch/` / `piecewise_kabsch/` /
  `linker_seam/`) and renders A's §1a rows **one per `(path, seam)`** —
  the max Cα jump that path **ends** with and whether it is therefore
  **honest** there. **No mean, no per-path score, no “N of M seams
  honest” tally, no best-path badge**: an average would hide the single
  seam that flies apart, and a tally would hide **which** path is
  dishonest **where**. **Null is not `0.00 Å`; unknown is not honest**,
  and a recorded `honest: true` above the gate is overridden
  **fail-closed** — B applies A's own `honest_for_jump` to A's own jump
  and carries **no threshold constant of its own**. A dishonest or
  unknown seam never carries a D-128 success PDB, and no assembler /
  D-125 / D-126 / D-127 file stands in for one. The owner markdown
  [`method-hold48-tiles.md`](method-hold48-tiles.md) and the `/method`
  MethodNote gain the D-128-B addendum. B **reads** A's tree; B does
  **not** re-implement persist, does **not** implement any part of the
  algorithm, and does **not** edit `hold48_linker_seam.py` (all five
  modules sha256-pinned). Default served = assembler until a Matt swap
  GO. Cite D-128-A `9e65cbf` + Spec §6 + §7.
  ⚠ **This PR discharges the mandatory Method obligation.** Spec §7
  forbids a silent code-only ship; D-128 is not “done” without the
  addendum, and the addendum is a deliverable of this PR rather than a
  follow-up.
  ⚠ **It also discloses the D-128 OPS result** (MANDATORY Method §7 OPS
  honesty inject, Matt GO via Emma 2026-09-06; restitch of the must-hunt
  **seven** at tip `9e65cbf`, out_root `linker_seam_ops_2026-09-05`;
  ⚠ **not run, not queried, and not re-measured in this PR**):
  **PASS 0 / REFUSE 7 / FAIL 0 / SKIP 0**; `recovered_of_seven` = **0**;
  `repaired_of_seven` = **0** (**the pre-registered allowed outcome**);
  `seam_jump_gt_10` **×6** (2938, 3179, 3190, 3321, 3368, 3566) and
  `rmsd_gt_10` **×1** (2939); and the **named give-back**
  `n_d125_pass_d128_refuse` = **5**, `n_d126_pass_d128_refuse` = **6**,
  with `n_d127_pass_d128_refuse` = **0** and `n_d127_refuse_d128_pass` =
  **0**. **The allowed zero never ships without that give-back beside
  it** — a pre-registration is not a place to bury a drop.
  ⚠ **No ops restitch, no Fly POST, and no gate change in this PR.**
  ⚠ **10.0 Å gate stays.** ⚠ **3432 stays accept-refuse.**
  ⚠ **D-126 remains the best experimental path until proven otherwise**
  (2 of its primary 5, against D-127's 0 of 3 and D-128's 0 of 7) and the
  **D-127 failed experiment stays disclosed**, labelled as D-127's.
  ⚠ **Seams recorded ≠ seams solved.**
- **D-128-A already shipped the linker / seam honesty core BUILD** on
  `main` (`9e65cbf` / #247) —
  [`core/hold48_linker_seam.py`](../core/hold48_linker_seam.py) + CLI
  [`scripts/linker_seam_restitch.py`](../scripts/linker_seam_restitch.py).
  The **required** half is Spec §1a: per seam, per path (`kabsch/`,
  `confidence_kabsch/`, `piecewise_kabsch/`, `linker_seam/`), the
  `max_ca_jump_angstrom` that path **ends** with and whether it is
  therefore **honest** at that seam (`> 10.0 Å` → dishonest). Each row
  names how it is known — `read_from_path_record`,
  `measured_from_path_artifacts`, or an **absence with a stated
  reason**; **null is not `0.0`** and **unknown is not honest**. Prior
  trees are opened **read-only**; the rows land in the D-128 tree.
  The optional §1b repair is **linker-local rigid only**: one weighted
  Kabsch on Cα inside a **±32 aa** window (**W = 32**, ε = **1e-3**,
  **no trim loop**, **no pieces**, **no linker-inherit**) around the
  offending seam centre, applied to that window's moving-tile atoms
  only → existing `winning_tile` / `write_stitched`. Refuse on
  `overlap_ca_lt_3` / `rmsd_gt_10` / `singular_covariance` /
  **`seam_jump_gt_10`**, the last measured across the **whole** seam
  after apply, not just the fitted window. Fail-closed and
  all-or-nothing; a dishonest or unknown seam carries no D-128 success
  PDB and no other path's `stitched.pdb` is presented as one.
  Fifth sibling tree `linker_seam/{parent_id}/`
  (`provenance.json`, `seams.jsonl`, `seam_honesty.jsonl`;
  `algorithm=linker_local_kabsch_then_winning_tile`, `decision=D-128`);
  `hold48_kabsch.py`, `hold48_confidence_kabsch.py`,
  `hold48_piecewise_kabsch.py` and `hold48_stitch.py` are **not
  edited** (all sha256-pinned). Primary inventory is the **seven**
  signed must-hunt linker parents; the CLI still runs the 27, and
  **3272 / 3394 / 3432 are recorded rows, not success targets**
  (**3432 stays accept-refuse** and is never counted as a D-128 miss).
  **CPU, no rent.** **0-of-7 repaired is an allowed outcome** — and
  **that PR measured nothing**: no ops run, no restitch of the 27, no
  Fly POST, no `repaired_of_seven` claimed for any parent.
  ⚠ **The BUILD gate was discharged, not waived:** Spec §8 says
  **Kaylee does not BUILD** until the Spec is on `main` **and** an
  Emma / Matt GO names D-128-A. Both held at that PR — Spec `2004c5a` /
  #246 was on `main`, and the Emma BUILD GO (Matt GO NOW) is recorded
  at `### D-128-A` in [`README.md`](README.md).
  ⚠ **A did not discharge the Method obligation** (Spec §7 —
  **mandatory** at D-128-B); **D-128-B** (`cd071d7` / #248) discharged
  it.
  ⚠ **The D-128 OPS run is recorded** (by Kaylee, at that same tip
  `9e65cbf`, out_root `linker_seam_ops_2026-09-05`): **PASS 0 /
  REFUSE 7 / FAIL 0 / SKIP 0**, `repaired_of_seven` = **0** — the
  pre-registered allowed outcome — and **D-128-B's Method §7 already
  discloses it** with the **5** / **6** give-back beside the zero.
  **Matt SIGNED Phase 5 named-refuse** on that result, so the **seven
  are no longer must-hunt**: they are **`accept-refuse`** with **3432**
  (**eight** total). Authority is **D-129**
  ([`SPEC-phase5-named-refuse.md`](SPEC-phase5-named-refuse.md)), which
  keeps that disclosure **mandatory and standing** and adds the
  **named-refuse label rules** the shipped Method does not carry yet.
  ⚠ **Not re-measured.**
  ⚠ **Served stays assembler**; **D-126 remains the
  best experimental path until proven otherwise**; the **D-127 failed
  experiment stays disclosed**. ⚠ **Seams recorded ≠ seams solved.**
- **D-128 already shipped the linker / seam honesty Spec** on `main`
  (`2004c5a` / #246) —
  [`SPEC-linker-seam-honesty.md`](SPEC-linker-seam-honesty.md).
  §1 goal framing is **diagnose and refuse dishonest seams** — the Spec
  never says solved. §1a makes a per-path / per-seam
  `max_ca_jump_angstrom` **required** for every experimental path tree
  (`kabsch/`, `confidence_kabsch/`, `piecewise_kabsch/`, `linker_seam/`);
  a path that **ends** over **10.0 Å** at a seam is **dishonest** for
  that seam and **no success PDB is presented as honest** (null is not
  zero; unknown is not honest). §1b's optional repair is **linker-local
  rigid only**: one weighted Kabsch on Cα in a **±32 aa** window
  (**W = 32**, ε = **1e-3**, **NO trim loop**, no pieces, no
  linker-inherit) → apply \(R, t\) inside that window only → existing
  `winning_tile` / `write_stitched`; refuse on `overlap_ca_lt_3` /
  `rmsd_gt_10` / `singular_covariance` / **`seam_jump_gt_10`**;
  all-or-nothing parent. Primary inventory is the **seven** signed
  must-hunt linker parents (**2938, 2939, 3179, 3190, 3321, 3368,
  3566** — the D-127 OPS `linker_jump_gt_10` class, as recorded).
  Sibling tree `linker_seam/{parent_id}/`,
  `algorithm=linker_local_kabsch_then_winning_tile`,
  `decision=D-128`. **0-of-7 repaired is an allowed outcome.**
  ⚠ **NOT piecewise-v2. NOT an RMSD Spec** (**3272** / **3394** out of
  primary). **NOT a domain Spec.** ⚠ **3432 stays accept-refuse**
  (signed triage) — not re-opened, not a success target.
  ⚠ **10.0 Å stays; no RMSD / linker threshold loosen without Matt.**
  ⚠ **Served stays assembler**; **D-126 remains the best experimental
  path until proven otherwise**; the **D-127 failed experiment stays
  disclosed**.   ⚠ **No `hold48_*.py` edit; no UI; no Method edit; no ops
  run.** **D-128-A** (core, **CPU, no rent**) already shipped
  (`9e65cbf` / #247); **D-128-B** (UI five-path honesty + the
  **mandatory** Method addendum, including the D-128 OPS disclosure) is
  the PR above, and D-128 is “done” only with it.
- **D-127-B already shipped UI four-path honesty and the Spec §7 Method
  addendum** on `main` (`de9a80e` / #245) —
  [`app/piecewise_kabsch_path_read.py`](../app/piecewise_kabsch_path_read.py)
  projects A's sibling `piecewise_kabsch/{parent_id}/` tree onto
  `assembly_review.four_path`; the review card names **four** paths
  (assembler / `kabsch/` / `confidence_kabsch/` / `piecewise_kabsch/`)
  with **one row per domain piece** and no seam average; the owner
  markdown [`method-hold48-tiles.md`](method-hold48-tiles.md) and the
  `/method` MethodNote gain the D-127-B addendum. B **reads** A's tree;
  B does **not** re-implement persist and does **not** edit
  `hold48_piecewise_kabsch.py`. Default served = assembler until a Matt
  swap GO. Cite D-127-A `e49bf34` + Spec §6 + §7.
  ⚠ **That PR discharged the mandatory Method obligation.** Spec §7
  forbids a silent code-only ship; D-127 is not “done” without the
  addendum, and the addendum was a deliverable of that PR rather than a
  follow-up. It also disclosed the **D-127 OPS result** (PASS 17 /
  REFUSE 10 / FAIL 0; `recovered_of_primary_three` = 0; named regress 5
  vs D-125, 7 vs D-126) and named **D-126 as the best experimental path
  so far** — both of which **stay disclosed** under D-128.
  ⚠ **No ops restitch of the 27.** ⚠ **10.0 Å gate stays.**
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
  D-127-B (already on `main`, `de9a80e` / #245) discharges it.
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
  jointly placed holoprotein; a linker-local rigid move (D-128) is a
  smaller one. Assembler + D-125 Kabsch + D-126 confidence + D-127
  piecewise + D-128 linker / seam stay callable. Default served =
  assembler. **D-128's goal framing is diagnose / refuse dishonest
  seams — never solved**, and its own OPS run repaired **0 of 7**.
  ⚠ **And `accept-refuse` (D-129) does not change that:** the eight
  accepted parents' joins are **not held** — accepting a refusal
  retires the **hunt**, not the **record**, and **never** means
  solved / fixed / repaired.
- ⚠ **The stitch-algorithm family is FROZEN (D-129 §7).** **No
  linker-v2**, no piecewise-v3, no new decomposition, no second window
  size, no restitch. A fifth algorithm needs its own Matt GO. **D-126
  remains the best experimental path until proven otherwise**, and the
  **D-127 and D-128 failed rescues stay disclosed** — both.
- ⚠ **10.0 Å gate STAYS.** Do not raise it **and do not loosen it** —
  no RMSD / linker threshold change without Matt. No trim loop. No
  threshold Spec-as-fix. No named-exclusion-as-fix. **W = 32** is a
  pinned D-128 v1 default, not a knob.
- **D-126 amendment 1** (already on `main`, same D-id): pins
  `rmsd_full_overlap_angstrom` + `max_ca_jump_angstrom`; ε = **1e-3**
  and the weighted RMSD formula; floor-then-Kabsch-then-trim;
  all-or-nothing parent refuse (`_clear_success_artifacts` spirit);
  ops confusion vs D-125 (`n_d125_pass_d126_refuse` is a **named
  finding**); **0-of-5** recovered is allowed.

Full entries: [`README.md` § D-129](README.md#d-129--phase-5-named-refuse-the-eight-linker--seam-parents-are-accept-refuse-the-d-128-rescues-0-of-7-stays-disclosed-and-the-stitch-family-freezes-docs-only),
[`README.md` § D-128-B](README.md#d-128-b--ui-linker--seam-path-honesty--the-mandatory-d-128-method-addendum),
[`README.md` § D-128-A](README.md#d-128-a--linker--seam-honesty-core-1a-per-path-seam-honesty-rows--optional-32-aa-linker-local-rigid-then-existing-winning_tile),
[`README.md` § D-128](README.md#d-128--linker--seam-honesty-spec-diagnose-and-refuse-dishonest-seams-optional-linker-local-rigid-docs-only),
[`README.md` § D-127-B](README.md#d-127-b--ui-four-path-honesty--the-mandatory-d-127-method-addendum),
[`README.md` § D-127-A](README.md#d-127-a--piecewise--domain-aware-kabsch-core-per-domain-weighted-fit-no-trim-then-existing-winning_tile),
[`README.md` § D-127](README.md#d-127--piecewise--domain-aware-kabsch-spec-multi-rigid-fit-then-existing-winning_tile-docs-only),
[`README.md` § D-126-B](README.md#d-126-b--ui-triple-path-honesty-name-assembler-d-125-kabsch-path-and-d-126-confidence-kabsch-artifacts-without-colliding-them),
[`README.md` § D-126-A](README.md#d-126-a--overlap-confidence-kabsch-core-trimmed--plddt-weighted-fit-then-existing-winning_tile),
[`README.md` § D-126](README.md#d-126--overlap-confidence-kabsch-spec-trimmed--plddt-weighted-fit-then-existing-winning_tile-docs-only),
[`README.md` § D-125-B](README.md#d-125-b--ui-dual-path-honesty-name-assembler-and-kabsch-path-artifacts-without-colliding-them),
[`README.md` § D-125](README.md#d-125--kabsch-restitch-spec-overlap-cα-align-then-existing-winning_tile-stitch-d-125-a-core-build).
Spec: [`SPEC-phase5-named-refuse.md`](SPEC-phase5-named-refuse.md)
(D-129) · [`SPEC-linker-seam-honesty.md`](SPEC-linker-seam-honesty.md)
(D-128) · [`SPEC-piecewise-domain-kabsch.md`](SPEC-piecewise-domain-kabsch.md)
(D-127).

## Nearby ids (do not conflate)

| Id | Role | Ships? |
| --- | --- | --- |
| **D-129 Spec** | **Phase 5 named-refuse** Spec (docs only) — **labels, not algorithms**. The **eight** parents **2938 / 2939 / 3179 / 3190 / 3321 / 3368 / 3566 + 3432** are **`accept-refuse`**; a surface labels them **named refuse**, never **open must-hunt** / **solved** / **a D-128 miss**. The D-128 OPS **0 of 7** + confusion (**5** vs D-125, **6** vs D-126) stays a **mandatory, standing** disclosure — **already discharged** by D-128-B (`cd071d7` / #248) and **not to be softened or dropped**. **3272 / 3394 stay Phase 4 must-hunt** (separate Matt GO). **No linker-v2**; 10.0 Å stays; served = assembler | Already shipped on `main` (#249 / `1baf4c0`). Docs only there; the **§3 re-label** it left owed ships at **D-129-B**. |
| **D-129-B** | **Phase 5 named-refuse LABELS** — the §3 re-label onto the owner Method, `/method`, and the review card, from one signed fate registry (`app/phase5_named_refuse.py` → `assembly_review.phase5_fate`). The **eight** are **named refuse / `accept-refuse`**; the block is **constructed carrying** the D-128 OPS **0 of 7** and the give-back (**5** / **6**), so the label cannot ship without the numbers. **3272 / 3394** render an **open** Phase 4 fate; **3432** is carried, not re-ruled | **Yes — this PR.** Labels only; no `hold48_*.py` edit (sha256-pinned), no threshold, no artifact tree, no served byte, no ops run. Draft; **Trinity merges**. |
| **D-128 Spec** | Linker / seam honesty Spec (docs only) — §1a required per-path seam honesty metric; §1b optional linker-local rigid (±32 aa window, no pieces, no trim) | Already shipped on `main` (#246 / `2004c5a`). §3 / §9 carry the **D-129 Phase 5 cross-link** (the seven are accept-refuse, not must-hunt); the algorithm stays as shipped. |
| **D-128-A** | Core BUILD (honesty rows for every path tree + optional ±32 aa window weighted Kabsch → `winning_tile`; CPU, no rent) | Already shipped on `main` (#247 / `9e65cbf`). Fifth sibling `linker_seam/`; no `hold48_*.py` edit; no ops run. Did **not** discharge Spec §7 Method. Its OPS run has since been recorded: **0 of 7** (→ **D-129**). |
| **D-128-B** | UI five-path honesty (one row per `(path, seam)`, never an average) + **mandatory Method addendum** (reads `linker_seam/`) | Already shipped on `main` (#248 / `cd071d7`). Discharged Spec §7 and disclosed the D-128 OPS result (PASS 0 / REFUSE 7 / FAIL 0; `repaired_of_seven` = 0; give-back 5 vs D-125, 6 vs D-126) **as recorded**. No ops run there. ⚠ Its Method still called the seven **must-hunt**; **D-129** re-labelled them **accept-refuse**, and **D-129-B** (this PR) lands that re-label on the surfaces. Its §4 disclosure is **untouched** and still guarded by content. |
| **D-127 Spec** | Piecewise / domain-aware Kabsch Spec (docs only) | Already shipped on `main` (#243 / `00fa76d`). |
| **D-127-A** | Core BUILD (per-domain weighted Kabsch → `winning_tile`; no trim; CPU, no rent) | Already shipped on `main` (#244 / `e49bf34`). |
| **D-127-B** | UI four-path honesty + **mandatory Method addendum** (reads `piecewise_kabsch/`) | Already shipped on `main` (#245 / `de9a80e`). Discharged Spec §7 and disclosed the D-127 OPS result. |
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
| **D-117** | Parent PLAN / evaluation stance | No. Plan only. Kabsch park now points at D-125; D-126 is the overlap-confidence follow-on Spec; D-127 is the piecewise / domain-aware follow-on Spec; D-128 is the linker / seam honesty follow-on Spec. |
| ADC-C-A | Pipeline + access data + API | Already shipped on `main` (#235 / `b71bade`). |
| F-004 ingest | Ranking-set expansion | No. Not this PR. |
