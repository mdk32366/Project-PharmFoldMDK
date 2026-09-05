# SPEC — Piecewise / domain-aware Kabsch (multi-rigid) (D-127)

> **COMMITTED to `docs/` as the piecewise / domain-aware restitch Spec. CITED BY
> the log, not restated as authority — where this file and `docs/README.md`
> differ, THE LOG GOVERNS.** Confirm the `### D-127` header exists before
> citing.
>
> **Date:** 2026-09-05 · **Status:** Spec (algorithm authority).
> **D-127-A** (core BUILD) is a later Emma GO. **D-127-B** (UI four-path
> honesty) is a later Emma GO that **reads** that tree. This file is
> algorithm authority; it is **not** the A BUILD and **not** the UI BUILD.
> ⚠ **Not a restitch run of the 27.** ⚠ **Not F-004 ingest.**
> ⚠ **Seams are not scientifically solved.**
> ⚠ **The 10.0 Å refuse gate STAYS.** Do not raise it.
> ⚠ **Another weight / trim knob is forbidden.** Family = multi-rigid
> piecewise by UniProt domain ends (same domain-snap source as tile
> planning). **No trim loop** (D-126 lie surface).
> ⚠ **Method must surface D-127** (and the stitch-path train) when
> the path exists. The Method addendum is **mandatory** before
> calling D-127 “done.” **No silent code-only.**
> Where this file and `docs/README.md` differ, THE LOG GOVERNS.
> Production triple-path (assembler / D-125 `kabsch/` / D-126
> `confidence_kabsch/`) stays until D-127 code + ops. Assembler,
> D-125 `core/hold48_kabsch.py`, and D-126
> `core/hold48_confidence_kabsch.py` remain callable. D-127-A writes a
> fourth sibling tree; it does not overwrite those paths.

**Parents:** [`D-126` Spec](SPEC-overlap-confidence-kabsch.md) · D-126-A
`aa8aa02` / #241 · D-126-B `abbcd00` / #242 · [`D-125` Spec](SPEC-kabsch-restitch.md)
· D-125-A `26a40a8` / #237 · D-125-B `aa8d3f1` / #238 ·
[`D-117`](PLAN-ui-post-wave2-endstate.md) (PLAN / Kabsch park) ·
[`D-118`](README.md) (assembler-not-Kabsch honesty) ·
[`D-120`](README.md) (Phase 2 review of the 27) ·
[`D-121`](method-hold48-tiles.md) (Method: assembler ≠ Kabsch *today*) ·
D-111 emit domain-snap / `domain_ends_span_relative`. **Ship index:**
[`decisions.md`](decisions.md).

---

## 1. Algorithm — Piecewise / domain-aware Kabsch, then existing winning_tile

Today's served stitch (`core/hold48_stitch.py`) is a **pLDDT winner-tile
assembler** (D-111 / D-117 / D-118 / D-121). D-125-A added a **single
rigid** pre-stitch on overlap Cα (`core/hold48_kabsch.py`). D-126-A
added a **sibling** single rigid that weights and trims the same overlap
(`core/hold48_confidence_kabsch.py`). D-126 ops then left **2939 /
3272 / 3432** REFUSE with **full-overlap RMSD ≫ weighted RMSD** and
max Cα jumps **28–68 Å** (task brief 2026-09-05 naming that ops
surface; ⚠ **not re-measured here**; ⚠ **motivation, not a new
threshold**). Another weight / trim knob on one rigid body is
**forbidden**. The family this Spec names is **multi-rigid piecewise**
by UniProt domain intervals from the **same domain-snap source** tile
planning already uses.

A later D-127-A BUILD must **not replace** `winning_tile` with a
piecewise invent, must **not** treat a named parent as excluded from
the algorithm, must **not** run a trim loop, and must **not** overwrite
assembler / D-125 `kabsch/` / D-126 `confidence_kabsch/`. The Spec is
still a **pre-stitch transform** of a tile's already-emitted atoms —
one rigid \(R, t\) **per domain piece**, not one rigid for the whole
tile.

**Pinned constants.** Weight floor \(\varepsilon\) = **1e-3**. Per-piece
weighted RMSD on that piece's fit set:

\[\mathrm{weighted\ RMSD}
= \sqrt{\sum_i w_i \,\lVert R p_i + t - q_i\rVert^2 / \sum_i w_i}\]

Gate for accept / refuse is that per-piece **weighted** RMSD
**`≤ 10.0 Å`** (refuse the piece if \(\gt 10.0\) Å). Parent
full-overlap unweighted RMSD and max Cα jump after piecewise apply
are **disclosure**, not a second gate. **No trim loop.** Trim was the
D-126 lie surface (a small fit-set RMSD hiding a 28–68 Å jump).
Piecewise does not reopen it.

1. Take two adjacent tiles that already passed `stitch_readiness`
   (D-116). Chosen tile ids stay the D-118 preference (lower ids
   **3673/3674/3675**; spares **3693/3695/3696** unused). Same adjacency
   / stitch_readiness / prefer-lower-dups / **N-terminal reference**
   as D-125 / D-126. The N-terminal / earlier tile stays the reference
   frame; later tiles chain onto the last *accepted* parent frame.
2. **Domain ends / intervals from the same source used for emit
   domain-snap.** Do not invent a second annotation. Use the UniProt
   `Domain` / `Repeat` feature records that
   `core.hold48.domain_ends_span_relative` / `plan_tiles` /
   `emit_tile_jobs` already read (`data/census/spancache/{accession}.json`,
   same `domain_ends` / `cache_dir` contract as D-116: emit-time snap
   must match). Emit snap uses those features' **ends** (±64 aa).
   Piecewise fit uses those same features' **span-relative intervals**.
   A missing cache is a category (empty ends), not a fetch.
3. Overlap Cα from the **stored** tile windows (`tile_start` /
   `tile_end`). Planned geometry is still overlap **128** aa at the
   D-111 stride; a live window may differ after domain-snap — use what
   is stored. **Per seam: domain pieces = domains intersecting the
   overlap with ≥3 Cα.** A piece is one UniProt Domain/Repeat interval
   whose intersection with the overlap has at least three corresponding
   Cα. Pieces that miss that count are not fitted (they are not a
   silent skip of the parent — see `no_domain_pieces` when **zero**
   pieces remain).
4. **Per piece:** \(\varepsilon = 1\mathrm{e}{-3}\);
   \(w_i = \min(\mathrm{pLDDT}_A, \mathrm{pLDDT}_B)/100\) clamped
   \(\ge \varepsilon\); **weighted Kabsch** on that piece's overlap Cα
   (weighted centroids → weighted covariance \(H\) → SVD → rotation
   \(R\) with \(\det R = +1\) correction → translation \(t\)).
   **NO trim loop** (D-126 lie surface). No pLDDT-floor-then-trim
   order. Weight + one Kabsch. Apply the refuse table in §2 to **that
   piece**.
5. Apply that piece's \(R, t\) **only** to moving-tile atoms in that
   domain. Do not apply piece \(k\)'s transform to piece \(j\)'s
   residues. The N-terminal tile is not moved.
6. **Linker residues** (moving-tile residues not in any fitted piece):
   inherit the transform of the **nearest N-terminal accepted piece**.
   If a linker sits N-terminal of every accepted piece, inherit the
   N-terminal-most accepted piece (the first fitted domain in N→C
   order). Record `linker_n` and `max_linker_ca_jump`.
   `max_linker_ca_jump` is the max \(|\mathrm{Cα}_{ref} -
   \mathrm{Cα}_{moved}|\) on **overlap** linker Cα after inherit
   (same units / spirit as D-126 `max_ca_jump_angstrom`, restricted
   to linkers). If `max_linker_ca_jump` **`> 10.0 Å`** → refuse the
   parent (`linker_jump_gt_10`). If no accepted piece exists to
   inherit from, the parent is already refused (piece refuse or
   `no_domain_pieces`).
7. **All-or-nothing parent.** If **any** piece refuses, or the seam
   has **`no_domain_pieces`**, parent outcome = refused; clear / do
   not leave partial `tileN_transformed.pdb` or D-127-path
   `stitched.pdb` (same fail-closed spirit as D-125
   `_clear_success_artifacts`). Seam rows are still recorded. Do not
   invent a pose.
8. On **full accept** (every seam's every piece accepted, and no
   linker-jump refuse): feed the (piecewise-transformed) `TileFold`
   list into the **existing** `winning_tile` / `stitch_pdb` /
   `stitch_plddt` / `stitch_pae` / `write_stitched`. Winner selection
   stays per-residue pLDDT. Off-block PAE stays **null, never 0**
   (D-111). No atom is invented for a gap (`UncoveredResidue` still
   raises).
9. **Out of v1:** soft invent blend; MD / AF GPU refine. Those are a
   **later phase, not A**. This Spec does not authorise them.
   Recovering **0-of-3** of the primary three does **not** license
   those inventions, a threshold raise, or a named-exclusion.

**Disclosure required (anti one-rigid / trim-to-pass lie):**

- **Per piece:** `n_ca`, weighted `rmsd_angstrom` (null if that piece
  refused before RMSD).
- **Parent / seam after piecewise apply:**
  `rmsd_full_overlap_angstrom` (unweighted RMSD on **all** overlap
  Cα after the piecewise transforms) and `max_ca_jump_angstrom`
  (max \(|\mathrm{Cα}_{ref} - \mathrm{Cα}_{moved}|\) on full overlap
  after piecewise apply). **Null if refused before any transform.**
- **Linkers:** `linker_n`, `max_linker_ca_jump` (null if refused
  before inherit).

Those metrics do **not** move the 10.0 Å piece gate. A must write
them; UI / B later shows them.

Piecewise Kabsch does not jointly place domains in a new network
forward pass. It does not fill PAE. It does not make the chain one
ESMFold forward pass. It does not enter F-004 (D-109 ruling 7). It
does not treat writing this Spec, or naming the three refuse parents,
as a scientific fix. A transformed tile is still that tile's network
output, in several rigid frames instead of one.

---

## 2. Refuse (v1 — 10 Å STAYS — do not raise)

These thresholds are **v1 defaults**. D-127-A tests must be able to go
red against them. They are not a claim that any parent was re-measured
against them in this PR. **The 10.0 Å gate does not move.** Piecewise
changes *which rigid body is fitted to which domain*. It is not a
threshold Spec-as-fix and not another weight / trim knob.

| Condition | Threshold | Effect |
|---|---|---|
| Piece overlap Cα count | **`< 3`** | **Refuse that piece** (`overlap_ca_lt_3`). Weighted Kabsch still needs three corresponding points. |
| Piece weighted RMSD on that piece's fit set | **`> 10.0 Å`** | **Refuse that piece** (`rmsd_gt_10`). Record the RMSD. Do not invent a “fixed” pose. |
| Covariance of the (weighted) piece Cα sets | **singular / degenerate** (rank `< 2`, collinear or coincident points) | **Refuse that piece** (`singular_covariance`). |
| No domain pieces covering the overlap (zero Domain/Repeat intervals intersect the overlap with ≥3 Cα) | — | **Refuse the parent** (`no_domain_pieces`). |
| Linker max Cα jump after inherit | **`> 10.0 Å`** | **Refuse the parent** (`linker_jump_gt_10`). |

Fail closed means: no `tileN_transformed.pdb`, no D-127-path
`stitched.pdb` for that parent, no silent fallback that looks like
success. **All-or-nothing parent refuse:** if **any** piece refuses,
or the seam is `no_domain_pieces`, or `linker_jump_gt_10`, parent
outcome = refused. Clear / do not leave a partial
`tileN_transformed.pdb` or D-127-path `stitched.pdb` from an earlier
accepted piece or seam of that same parent (same fail-closed spirit
as D-125 `_clear_success_artifacts` in `core/hold48_kabsch.py`). Seam
rows are still recorded. The **assembler** path already on disk
(D-118 / D-120) is unchanged. The **D-125** sibling tree
`kabsch/{parent_id}/` is unchanged. The **D-126** sibling tree
`confidence_kabsch/{parent_id}/` is unchanged. A refuse is a
**recorded outcome**, not a gap filled with guessed coordinates, and
not a named-exclusion of that parent from the CLI.

The D-126 ops RMSDs / jumps on the primary three (full-overlap RMSD
≫ weighted RMSD; max Cα jumps **28–68 Å**; task brief 2026-09-05
naming the D-126 OPS surface) are **motivation, not thresholds**.
They explain why the family is multi-rigid, not a licence to raise
the gate or to mark those accessions “out.” A later A BUILD that
computes a *per-piece* weighted RMSD on the same pair may still
refuse under 10.0 Å. That is fail-closed, not “the seam is solved.”

---

## 3. Inventory — the primary three REFUSE (plus CLI of the 27)

Primary evaluation inventory is the **three** D-126 ops parents that
still REFUSE with full ≫ weighted (jumps 28–68 Å). Same closed-out
27 as D-117 / D-118 / D-120 / D-125 / D-126 /
`WAVE1_WAVE2_STITCHED_PARENT_IDS`. ⚠ **Not re-queried against Fly in
this Spec.** Do not invent a new science number. Do not treat naming
these three as a fix. D-126's other two of the primary five
(**3368** `Q5SZK8`, **3394** `Q8TDW7`) are **not** this Spec's
primary three; they stay in the CLI of the 27.

| parent job id | accession | Role |
|---|---|---|
| **2939** | `Q7Z408` | Primary REFUSE (D-126 ops; full ≫ weighted) |
| **3272** | `Q6V0I7` | Primary REFUSE (D-126 ops; full ≫ weighted) |
| **3432** | `Q8IZF6` | Primary REFUSE (D-126 ops; full ≫ weighted) |

- D-126 ops on these three: full-overlap RMSD ≫ weighted RMSD; max
  Cα jumps **28–68 Å** (task brief 2026-09-05 naming the D-126 OPS
  surface; not re-measured here). That surface is why they are the
  primary three and why the family is multi-rigid — **not** a
  per-parent headline and **not** a new threshold.
- **CLI must also re-run all 27** so accept / refuse counts stay
  comparable to D-125 and to D-126. The other 24 are not excluded
  from the algorithm; they are not the primary evaluation set.
- **0-of-3 recovered is an allowed outcome.** Recovering zero of the
  primary three is a valid experimental result. Do not loosen the
  10.0 Å gate, invent a blend, or add a trim loop to force passes.
  A later A BUILD that recovers none of 2939 / 3272 / 3432 has still
  run the Spec; that zero is a finding, not a licence to change the
  algorithm.
- IGF2R parent **3356** is a **different accession story** (cohort OOM
  vs census tiles) and is **not** one of the 27 (D-120). Out.
- These 27 stay **outside F-004** (D-109 ruling 7). Neither assembler,
  D-125 Kabsch, D-126 confidence Kabsch, nor a future D-127 path
  ingests them into `/scorer`.
- Remaining ~18 tileable parents and the 3 mucins are **out of this
  Spec**.

Do not invent a new science number. Do not treat a named exclusion as
the algorithm.

---

## 4. PLAN pointer

Parent PLAN: [`PLAN-ui-post-wave2-endstate.md`](PLAN-ui-post-wave2-endstate.md)
(**D-117**). §5 was the Kabsch park → **D-125**. Overlap-confidence
follow-on was **D-126**. This Spec is the follow-on `D-NNN` for
**piecewise / domain-aware** Kabsch after D-126 A+B landed. D-127-A
is the Emma GO that implements §1–§3 and §5 as code (a later sibling
module + CLI). It does **not** pre-authorise D-127-B UI, a live
restitch run of the 27, rental, a threshold change, a named-exclusion,
a trim loop, or MD / AF GPU refine.

---

## 5. Artifact dirs + provenance (D-127-A writes a *sibling* tree)

Assembler `write_stitched` already writes, beside an ops `out_dir`:
`stitched.pdb`, `stitched_plddt.json`, `stitched_pae.json`, `tileN.pdb`,
`tileN_plddt.json`, `tileN_pae.json`. Those names are the D-118 / D-120
served path.

D-125-A already writes:

```
<ops out_dir>/kabsch/{parent_job_id}/
```

D-126-A already writes:

```
<ops out_dir>/confidence_kabsch/{parent_job_id}/
```

**Do not overwrite** the assembler tree, the D-125 `kabsch/` tree, or
the D-126 `confidence_kabsch/` tree until a later Matt GO names the
swap.

D-127-A writes a **fourth sibling tree**, outside the git repo (GUIDE:
do not `git add` `*.pdb` / PAE binaries):

```
<ops out_dir>/piecewise_kabsch/{parent_job_id}/
  provenance.json
  seams.jsonl
  tile{n}_transformed.pdb   # only if that tile's inbound seam was accepted
  stitched.pdb              # via existing write_stitched, after transform
  stitched_plddt.json
  stitched_pae.json
```

`provenance.json` / each `seams.jsonl` row must make a refuse
reconstructible (D-016):

- `parent_job_id`, chosen tile job ids, windows
- per seam: `refuse_reason` ∈ {`null`, `overlap_ca_lt_3`,
  `rmsd_gt_10`, `singular_covariance`, `no_domain_pieces`,
  `linker_jump_gt_10`}
- per piece: `n_ca`, `rmsd_angstrom` (piece weighted RMSD; null if
  refused before RMSD), domain interval
- `linker_n`, `max_linker_ca_jump`
- `rmsd_full_overlap_angstrom` (unweighted RMSD on **all** overlap
  Cα after piecewise apply), `max_ca_jump_angstrom` (max
  \(|\mathrm{Cα}_{ref} - \mathrm{Cα}_{moved}|\) on full overlap after
  piecewise apply). **Null if refused before any transform.**
- `algorithm`: `piecewise_domain_kabsch_then_winning_tile`
- `decision`: `D-127`
- accepted pieces only: rotation \(R\) (3×3) and translation \(t\) (Å)

`rmsd_full_overlap_angstrom` and `max_ca_jump_angstrom` are recorded
after piecewise apply. On refuse-before-transform they may be null.
They do **not** move the 10.0 Å piece gate. A must write them; UI / B
later shows them.

A refuse still writes the seam record. It does **not** write a
transformed PDB. **All-or-nothing:** if any piece refuses or
`no_domain_pieces` / `linker_jump_gt_10`, clear / do not leave
partial `tileN_transformed.pdb` or D-127-path `stitched.pdb` (same
spirit as D-125 `_clear_success_artifacts`). No invented coordinates.
Assembler + D-125 `kabsch/{id}/` + D-126 `confidence_kabsch/{id}/`
stay on disk and stay callable.

---

## 6. UI four-path honesty (D-127-B)

D-118 / D-120 / D-121 already disclose the **assembler** path.
D-125-B already names a **second** path when `kabsch/{parent}/` is on
disk. D-126-B already names a **third** path when
`confidence_kabsch/{parent}/` is on disk. D-127-B is **UI only**,
after A writes `piecewise_kabsch/`.

When (and only when) D-127-path artifacts are on disk:

- The review card names **four** paths. Assembler remains the default
  **served** PDB until a Matt GO names a swap.
- Each D-127 seam shows per-piece `n_ca` / weighted RMSD (if
  computed), `rmsd_full_overlap_angstrom`, `max_ca_jump_angstrom`,
  `linker_n`, `max_linker_ca_jump`, and `refuse_reason`. Those are
  measurements, not a verdict that the holoprotein is aligned. A
  wrote the fields; B does not invent them. On
  refuse-before-transform they may be null (honest empty).
- A refused seam stays fail-closed — no “fixed” badge, no silent
  assembler / D-125 / D-126 PDB presented as a D-127 success.
- Forbidden language (same park as D-117 §5 / D-125 §6 / D-126 §6):
  “aligned,” “superimposed,” “seams solved,” “full-length AF-quality.”
- No invented RMSD. Honest empty when the sibling tree is missing.
- No alignment-box CTA. No F-004 ingest.

When the `piecewise_kabsch/` tree is missing, the UI must not imply a
D-127 path exists and must not invent RMSD / piece counts. That
absence is not a solved seam. Default served = assembler.

**Method is not optional.** Four-path review-card honesty without a
`/method` addendum is still a silent code-only ship. See §7.

---

## 7. Method / owner-facing (mandatory — not a silent code-only ship)

Matt / Emma standing requirement (2026-09-05): **Method must surface
D-127** (and the stitch-path train) honestly when the path exists.
A later A BUILD that writes `piecewise_kabsch/` without an owner-facing
Method addendum is **not done**. Silent code-only is forbidden.

Same pattern as D-121 / D-125-B / D-126-B: an **additive** `/method`
addendum plus the owner markdown in
[`method-hold48-tiles.md`](method-hold48-tiles.md). Do not gut the
assembler Method. Do not rewrite #229. D-121 / D-125-B / D-126-B
sections stay.

This Spec carries the **8th-grade excerpt** as algorithm / honesty
authority. **D-127-B** ships the Method owner markdown addendum and
the MethodNote additive section (with the four-path UI). Calling
D-127 “done” before that Method surface exists is a miss — not a
later nice-to-have.

**Required Method copy (plain, 8th-grade):**

The stitch-path train, in order, is:

1. **Assembler** — winner-tile pLDDT. Default **served** PDB until a
   Matt swap GO.
2. **D-125 Kabsch** — one unweighted rigid move on overlap Cα, then
   the same assembler.
3. **D-126 confidence** — one weighted / trimmed rigid move on
   overlap Cα, then the same assembler. The D-126 lesson: a small
   **weighted** RMSD can hide a large **full-overlap** jump
   (**full ≫ weighted**; ops jumps 28–68 Å on 2939 / 3272 / 3432).
   That is why a trim-to-pass number is not a solved seam.
4. **D-127 piecewise / domain** — one weighted rigid move **per
   UniProt domain** that overlaps the glue, then the same assembler.
   No trim loop. Linkers inherit the nearest N-terminal accepted
   piece.

**Refuse table (high level, not a science headline).** A piece can
refuse if it has fewer than three Cα, if its weighted RMSD is above
**10.0 Å**, or if the points are collinear. The parent can refuse if
no domain covers the glue, or if a linker Cα jumps more than
**10.0 Å**. A refuse writes a record. It does not write a “fixed”
structure. The **10.0 Å gate stays.**

**Seam disclosure.** When the D-127 path exists, Method and the
review card name per-piece counts / RMSD and the parent
full-overlap RMSD + max Cα jump after the piecewise moves. Those
are measurements. They are **not** a verdict that the holoprotein
is lined up. **Never claim seams solved.** Forbidden: “aligned,”
“superimposed,” “seams solved,” “full-length AF-quality.”

**Default served = assembler** until a Matt swap GO. Method must
say so. Honest empty when `piecewise_kabsch/` is missing — do not
invent the fourth path.

**What Method does not do.** It does not replace the assembler
story. It does not make the long chain one ESMFold pass. It does
not fill PAE. It does not enter F-004. It is not medical advice.

---

## 8. PR split — Spec vs A/B BUILD

| Id | What | This PR? | Gate |
|---|---|---|---|
| **D-127 Spec** | This file + `### D-127` + ship index + PLAN one-liner + hermetic docs pin tests. Includes this Method excerpt as authority. | **Yes — this PR.** | Trinity reviewed. Docs only. |
| **D-127-A** | Core: per-domain weighted Kabsch (no trim) + §2 refuse + apply \(R, t\) per domain + linker inherit + call existing `winning_tile`. No UI. Sibling §5 `piecewise_kabsch/` tree. CLI re-runs all 27; primary eval is the three. **CPU, no rent.** | No. Later Emma GO. | After the Spec. No rent in A. **Not “done” without Method.** |
| **D-127-B** | UI four-path honesty (§6) **and** Method owner markdown + MethodNote additive section (§7). Reads A's sibling tree. No persist rewrite. Default served = assembler until Matt swap GO. | No. Later Emma GO. | After A. **Mandatory** before calling D-127 “done.” |
| **GPU refine** | Optional MD / AF GPU refine | No. Later phase, **not A**. | Not this family of PRs. |

**Out of this Spec PR:** any edit to `hold48_*.py`, any UI, a live
restitch run of the 27, F-004 ingest, ADC-C / pipeline / `/adcs`
bleed, rent / GPU / RunPod, replacing `winning_tile`, overwriting
assembler or D-125 `kabsch/` or D-126 `confidence_kabsch/`, claiming
seams solved, raising the 10.0 Å gate, treating the three as a
named-exclusion, a trim loop, a soft invent blend.

**Out of the A PR:** any UI, a live restitch run of the 27, F-004
ingest, rent / GPU / RunPod / MD / AF refine, replacing
`winning_tile`, overwriting the three existing trees, claiming seams
solved, raising the 10.0 Å gate, a trim loop. A does **not**
discharge the Method obligation — B (or a Method-bearing PR) must
still ship §7.

---

## 9. Hard stops (Spec + log)

- **No threshold Spec-as-fix.** Writing 10.0 Å again is not a repair of
  the three. The gate stays. Do not raise it.
- **No named-exclusion-as-fix.** Listing 2939 / 3272 / 3432 is the
  primary evaluation inventory, not an algorithm that skips them.
  CLI still runs the 27.
- **No invent.** Fail closed. No transformed PDB on refuse. No
  invented gap atoms. No soft invent blend. All-or-nothing parent:
  no partial `tileN_transformed.pdb` / D-127 `stitched.pdb` when any
  piece refuses.
- **No PAE zeros.** Off-block PAE stays null, never 0.
- **No F-004.** The 27 stay outside `/scorer` (D-109 ruling 7).
- **No rent in A.** D-127-A is CPU-side stdlib, same as D-125-A /
  D-126-A. No GPU / RunPod / MD / AF refine. GPU refine is a later
  phase, not A.
- **Never seams solved.** Forbidden language stands.
- **Keep assembler + D-125 Kabsch + D-126 confidence callable.**
  Production triple-path stays until D-127 code + ops. Do not
  overwrite `stitched.pdb`, `kabsch/{id}/`, or
  `confidence_kabsch/{id}/`.
- **No trim loop.** Trim was the D-126 lie surface. Piecewise does
  not reopen it. Another weight / trim knob is forbidden.
- **0-of-3 recovered is allowed.** Do not loosen the gate or invent
  a blend to force passes.
- **ε = 1e-3.** Weight floor is pinned. Per-piece weighted Kabsch
  only.
- **No stitch code in this PR.** No `hold48_*.py` edit.
- **No silent code-only.** Method must surface D-127 and the
  stitch-path train when the path exists. The Method addendum is
  **mandatory** before calling D-127 “done,” not optional.

---

## 10. What this file is not

- **Not D-127-A** (core). **Not D-127-B** (UI). This file is the
  Spec, not a BUILD.
- Not a licence to call seams solved or the chain one forward pass.
- Not a replacement of `winning_tile` by piecewise Kabsch.
- Not an overwrite of D-125 `core/hold48_kabsch.py` /
  `kabsch/{id}/` or D-126 `core/hold48_confidence_kabsch.py` /
  `confidence_kabsch/{id}/`.
- Not a threshold change and not a named-exclusion of the three.
- Not another weight / trim knob. Not a trim loop.
- Not a Fly re-query of the 27. Not a restitch run.
- Not ADC-C (D-124). Not a rewrite of D-121 assembler Method.
  The D-127 Method addendum (§7) is **mandatory**, not optional.
  Not ranking ingest.
- Not a repair of the `D-` next-free pointer.
- Not soft-blend / MD / AF GPU refine (out of v1; later phase, not A).
- Not a licence to treat 0-of-3 recovered as a failure that moves
  the gate.
- Not a CI assert against live ops (the confusion vs D-125 and vs
  D-126 is a required **report** field, not a gate test).

---

## 11. Ops success report (required fields; not a CI assert)

When a later D-127-A (or ops) run covers the 27, the **ops success
report** MUST include confusion vs D-125 **and** vs D-126. This is
documentation of required report fields. It is **not** a CI assert
against live ops and not a restitch measurement in this Spec PR.

Required fields:

| Field | Meaning |
|---|---|
| `n_d125_pass_d127_pass` | D-125 PASS parents that D-127 also accepts |
| `n_d125_pass_d127_refuse` | D-125 PASS parents that D-127 REFUSE |
| `n_d126_pass_d127_pass` | D-126 PASS parents that D-127 also accepts |
| `n_d126_pass_d127_refuse` | D-126 PASS parents that D-127 REFUSE |
| `n_d126_refuse_d127_pass` | recovered of the primary three (and any other D-126 REFUSE) |
| `n_d126_refuse_d127_refuse` | D-126 REFUSE that still refuse |
| `recovered_of_primary_three` | 0..3; **0 is an allowed outcome** |

A non-zero `n_d125_pass_d127_refuse` or `n_d126_pass_d127_refuse` is
a **named finding**, not silent success. Do not bury a drop inside
an overall accept count. Recovering **0-of-3** of the primary three
is a valid experimental result; do not loosen the 10.0 Å gate or
invent a blend to force passes.
