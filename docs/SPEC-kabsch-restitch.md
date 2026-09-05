# SPEC — Kabsch restitch (D-125)

> **COMMITTED to `docs/` as the restitch Spec. CITED BY the log, not restated
> as authority — where this file and `docs/README.md` differ, THE LOG
> GOVERNS.** Confirm the `### D-125` header exists before citing.
>
> **Date:** 2026-09-05 · **Status:** Spec (algorithm authority). **D-125-A**
> (core BUILD) implements §1–§3 and §5 as code (`26a40a8` / #237).
> **D-125-B** is the UI dual-path honesty BUILD of §6 (this later PR).
> ⚠ **Not a restitch run of the 27.** ⚠ **Not F-004 ingest.**
> ⚠ **Seams are not scientifically solved.**
> Where this file and `docs/README.md` differ, THE LOG GOVERNS.
> A-ship note: Kabsch lives in `core/hold48_kabsch.py` and feeds existing
> `winning_tile` / `write_stitched`. The assembler is not replaced.

**Parents:** [`D-117`](PLAN-ui-post-wave2-endstate.md) (PLAN / Kabsch park) ·
[`D-118`](README.md) (assembler-not-Kabsch honesty) · [`D-120`](README.md)
(Phase 2 review of the 27) · [`D-121`](method-hold48-tiles.md) (Method:
assembler ≠ Kabsch *today*). **Ship index:** [`decisions.md`](decisions.md).

---

## 1. Algorithm — Kabsch on overlap Cα, then the existing assembler

Today's stitch (`core/hold48_stitch.py`) is a **pLDDT winner-tile assembler**
(D-111 / D-117 / D-118 / D-121). For each parent residue, `winning_tile`
keeps the covering tile with higher per-residue pLDDT (tie → earlier tile).
`stitch_pdb` copies that tile's atoms, remapped to parent residue numbers.
**No rigid-body transform.** That is why a join can jump — the IGF2R pilot
seam ≈ **88.76 Å** is a measured disclosure (D-117 / D-118), not a Kabsch
RMSD and **not a solved structure**.

A later Kabsch BUILD must **not replace** that assembler with a Kabsch
invent. The Spec is a **pre-stitch rigid transform** of a tile's frame:

1. Take two adjacent tiles that already passed `stitch_readiness` (D-116).
   Chosen tile ids stay the D-118 preference (lower ids **3673/3674/3675**;
   spares **3693/3695/3696** unused).
2. Overlap = parent residues in both windows (D-111 geometry: overlap
   **128** aa at the planned stride; a live window may differ after
   domain-snap — use the stored `tile_start` / `tile_end`).
3. Extract **Cα** coordinates for those overlap residues from each tile
   PDB (ESMFold local numbering). No other atom is used to *fit*.
4. Apply the refuse table in §2 **before** writing a transform. Fail
   closed. Record. Do not invent a pose.
5. If the seam is accepted: Kabsch (centroid both Cα sets → covariance
   \(H = P^{\mathsf{T}} Q\) → SVD → rotation \(R\) with \(\det R = +1\)
   correction → translation \(t\)). Apply \(R, t\) to **all atoms** of
   the moving tile. The N-terminal / earlier tile stays the reference
   frame; later tiles chain onto the last *accepted* frame.
6. Feed the (possibly transformed) `TileFold` list into the **existing**
   `winning_tile` / `stitch_pdb` / `stitch_plddt` / `stitch_pae` /
   `write_stitched`. Winner selection stays per-residue pLDDT. Off-block
   PAE stays **null, never 0** (D-111). No atom is invented for a gap
   (`UncoveredResidue` still raises).

Kabsch does not jointly place domains. It does not fill PAE. It does not
make the chain one ESMFold forward pass. It does not enter F-004
(D-109 ruling 7). A transformed tile is still that tile's network output,
in a different rigid frame.

---

## 2. Refuse (v1 defaults — named so tests can go red)

These thresholds are **v1 defaults**. D-125-A tests must be able to go
red against them. They are not a claim that any parent was measured
against them in this PR.

| Condition | Threshold | Effect |
|---|---|---|
| Overlap Cα count | **`< 3`** | **Refuse align.** Kabsch needs three corresponding points. |
| Kabsch RMSD on overlap Cα | **`> 10.0 Å`** | **Refuse that seam.** Record the RMSD. Do not invent a “fixed” pose. |
| Covariance of the Cα sets | **singular / degenerate** (rank `< 2`, collinear or coincident points) | **Refuse align.** |

Fail closed means: no `tileN_transformed.pdb`, no Kabsch-path `stitched.pdb`
for that parent, no silent fallback that looks like success. The assembler
path already on disk (D-118 / D-120) is unchanged. A refuse is a
**recorded outcome**, not a gap filled with guessed coordinates.

The IGF2R ≈ 88.76 Å figure is a **join-jump disclosure**, not a Kabsch
RMSD. A later A BUILD that computes overlap-Cα RMSD on that pair may
refuse the seam under the 10.0 Å default. That is fail-closed, not
“the seam is solved.”

---

## 3. Inventory — the 27 assembled parents (not a Fly re-query)

Same closed-out set as D-117 / D-118 / D-120 / `WAVE1_WAVE2_STITCHED_PARENT_IDS`
in `app/reads.py`. **27 unique** = Wave1 PASS **10** + Wave2 PASS **17**.
⚠ **Not re-queried against Fly in this Spec.** A later session that needs
them live must name a query or log line.

| parent job id (sorted) |
|---|
| 2817, 2917, 2929, 2938, 2939, 3027, 3097, 3153, 3179, 3188, 3190, 3217, 3272, 3320, 3321, 3368, 3379, 3394, 3404, 3432, 3454, 3469, 3516, 3541, 3566, 3569, 3575 |

- First named parent: **2817** `Q9P273`, tiles `[3673, 3630]` (D-117).
- IGF2R parent **3356** is a **different accession story** (cohort OOM vs
  census tiles) and is **not** one of the 27 (D-120).
- Remaining ~18 tileable parents and the 3 mucins are **out of this Spec**.
- These 27 stay **outside F-004** (D-109 ruling 7). Neither assembler nor
  a future Kabsch path ingests them into `/scorer`.

Do not invent a new science number. Do not treat Wave2-only 17 as the
closed-out parent count.

---

## 4. PLAN pointer

Parent PLAN: [`PLAN-ui-post-wave2-endstate.md`](PLAN-ui-post-wave2-endstate.md)
(**D-117**). §5 was the Kabsch park. This Spec is the `D-NNN` that park
pointed at. D-125-A is the Emma GO that implements §1–§3 and §5 as
code. It does **not** pre-authorise D-125-B UI, a live restitch run of
the 27, or rental.

---

## 5. Artifact dirs + provenance (D-125-A writes the sibling tree)

Assembler `write_stitched` already writes, beside an ops `out_dir`:
`stitched.pdb`, `stitched_plddt.json`, `stitched_pae.json`, `tileN.pdb`,
`tileN_plddt.json`, `tileN_pae.json`. Those names are the D-118 / D-120
served path. **Do not overwrite them in a Kabsch BUILD until a later GO
names the swap.**

D-125-A writes a **sibling tree**, outside the git repo (GUIDE:
do not `git add` `*.pdb` / PAE binaries):

```
<ops out_dir>/kabsch/{parent_job_id}/
  provenance.json
  seams.jsonl
  tile{n}_transformed.pdb   # only if that tile's inbound seam was accepted
  stitched.pdb              # via existing write_stitched, after transform
  stitched_plddt.json
  stitched_pae.json
```

`provenance.json` / each `seams.jsonl` row must make a refuse reconstructible
(D-016):

- `parent_job_id`, chosen tile job ids, windows
- per seam: `n_ca`, `rmsd_angstrom` (null if refused before RMSD),
  `refuse_reason` ∈ {`null`, `overlap_ca_lt_3`, `rmsd_gt_10`,
  `singular_covariance`}
- `algorithm`: `kabsch_ca_then_winning_tile`
- `decision`: `D-125`
- accepted seams only: rotation \(R\) (3×3) and translation \(t\) (Å)

A refuse still writes the seam record. It does **not** write a transformed
PDB. No invented coordinates.

---

## 6. UI dual-path honesty (D-125-B)

D-118 / D-120 / D-121 already disclose the **assembler** path: winner-tile
pLDDT, not Kabsch; seam not solved; IGF2R ≈ 88.76 Å is a caveat.

Trinity amend (A tip): B is **UI only**. A already writes the sibling
`kabsch/{parent}/` tree. B reads it; B does not re-implement persist.

When (and only when) Kabsch-path artifacts are on disk:

- The review card names **both** paths. Assembler remains the default
  served PDB until a GO names a swap.
- Each seam shows `n_ca`, RMSD (if computed), and `refuse_reason`.
  Those are measurements, not a verdict that the holoprotein is aligned.
- A refused seam stays fail-closed — no “fixed” badge, no silent
  assembler PDB presented as a Kabsch success.
- Forbidden language (same park as D-117 §5): “aligned,” “superimposed,”
  “seams solved,” “full-length AF-quality.”
- No alignment-box CTA. No F-004 ingest.

When the sibling tree is missing, the UI must not imply a Kabsch path
exists and must not invent RMSD / max Cα jump. That absence is not a
solved seam.

---

## 7. PR split — Spec vs future A/B BUILD

| Id | What | This PR? | Gate |
|---|---|---|---|
| **D-125 Spec** | This file + `### D-125` + ship index + PLAN one-liner | Already on `main` (`fbe8978` / #234) | Trinity reviewed. |
| **D-125-A** | Core: overlap Cα Kabsch + §2 refuse + transform tile + call existing `winning_tile` stitch. No UI. Sibling §5 tree. CLI limited to the 27. | Already on `main` (`26a40a8` / #237) | Emma GO after D-124 A+B. |
| **D-125-B** | UI dual-path honesty (§6). Reads A's sibling tree. No persist rewrite. | **Yes — the B PR** | After A. Emma GO. |

**Out of the B PR:** a live restitch run of the 27, F-004 ingest,
ADC-C / pipeline / `/adcs` bleed, rent / GPU / RunPod, replacing
`winning_tile`, claiming seams solved, re-implementing persist.

---

## 8. What this file is not

- Not a licence to call seams solved or the chain one forward pass.
- Not a replacement of `winning_tile` by Kabsch.
- Not a Fly re-query of the 27.
- Not ADC-C (D-124). Not Method (D-121). Not ranking ingest.
- Not a repair of the `D-` next-free pointer.
