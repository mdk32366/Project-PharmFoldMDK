# SPEC — Overlap-confidence Kabsch (trimmed + pLDDT-weighted) (D-126)

> **COMMITTED to `docs/` as the overlap-confidence restitch Spec. CITED BY
> the log, not restated as authority — where this file and `docs/README.md`
> differ, THE LOG GOVERNS.** Confirm the `### D-126` header exists before
> citing.
>
> **Date:** 2026-09-05 · **Status:** Spec (algorithm authority). **D-126-A**
> (core BUILD) and **D-126-B** (UI triple-path honesty) are **later** Emma
> GOs. This PR does **not** implement them.
> ⚠ **Not a restitch run of the 27.** ⚠ **Not F-004 ingest.**
> ⚠ **Seams are not scientifically solved.**
> ⚠ **The 10.0 Å refuse gate STAYS.** Trim / weight change the fit set,
> not the gate.
> Where this file and `docs/README.md` differ, THE LOG GOVERNS.
> Production dual-path (**22** D-125 Kabsch / **5** assembler) stays until
> D-126 code + ops. D-125 `core/hold48_kabsch.py` and the assembler remain
> callable. This file does not overwrite that tree.

**Parents:** [`D-125` Spec](SPEC-kabsch-restitch.md) · D-125-A `26a40a8` /
#237 · D-125-B `aa8d3f1` / #238 · [`D-117`](PLAN-ui-post-wave2-endstate.md)
(PLAN / Kabsch park) · [`D-118`](README.md) (assembler-not-Kabsch honesty)
· [`D-120`](README.md) (Phase 2 review of the 27) · [`D-121`](method-hold48-tiles.md)
(Method: assembler ≠ Kabsch *today*). **Ship index:**
[`decisions.md`](decisions.md).

---

## 1. Algorithm — Overlap-confidence Kabsch, then existing winning_tile

Today's served stitch (`core/hold48_stitch.py`) is a **pLDDT winner-tile
assembler** (D-111 / D-117 / D-118 / D-121). D-125-A added a **pre-stitch
rigid transform** on overlap Cα (`core/hold48_kabsch.py`) that feeds the
same `winning_tile` / `write_stitched` path. That unweighted Kabsch
refused five seams under the v1 10.0 Å gate. This Spec does **not**
replace the assembler, and it does **not** overwrite the D-125 Kabsch
tree. It names a **sibling** pre-stitch: weight and trim the overlap
points, then the same refuse table, then the same assembler.

A later D-126-A BUILD must **not replace** `winning_tile` with a
confidence invent, and must **not** treat a named parent as excluded
from the algorithm. The Spec is still a **pre-stitch rigid transform**
of a tile's frame:

1. Take two adjacent tiles that already passed `stitch_readiness`
   (D-116). Chosen tile ids stay the D-118 preference (lower ids
   **3673/3674/3675**; spares **3693/3695/3696** unused). Same adjacency
   / stitch_readiness / prefer-lower-dups rule as D-125.
2. Overlap Cα from the **stored** tile windows (`tile_start` /
   `tile_end`). Planned geometry is still overlap **128** aa at the
   D-111 stride; a live window may differ after domain-snap — use what
   is stored. No other atom is used to *fit*.
3. Weight each overlap pair
   \(w_i = \min(\mathrm{pLDDT}_A, \mathrm{pLDDT}_B)/100\),
   clamped \(\ge \varepsilon\) (a small positive floor so a later A
   BUILD cannot drop a point with a silent zero weight). Fit =
   **weighted Kabsch** on those Cα (weighted centroids → weighted
   covariance \(H\) → SVD → rotation \(R\) with \(\det R = +1\)
   correction → translation \(t\)).
4. **Trim loop:** while \(n_{\mathrm{eff}} \ge 3\) and weighted RMSD
   \(\gt 10.0\) Å, drop the highest-residual **10%** of points
   (minimum 1), refit. Cap **5** rounds. Trim changes the fit set. It
   does **not** move the 10.0 Å gate.
5. **Optional pLDDT floor:** drop pairs with
   \(\min(\mathrm{pLDDT}) < 50\) **if** that leaves \(n \ge 3\);
   else keep the full (post-trim) set. The floor is a fit-set filter,
   not a second refuse threshold and not a named-exclusion of a parent.
6. Apply the refuse table in §2 to the **final** weighted fit. Fail
   closed. Record. Do not invent a pose. If the seam is accepted: apply
   \(R, t\) to **all atoms** of the moving tile. The N-terminal /
   earlier tile stays the reference frame; later tiles chain onto the
   last *accepted* frame. Feed the (possibly transformed) `TileFold`
   list into the **existing** `winning_tile` / `stitch_pdb` /
   `stitch_plddt` / `stitch_pae` / `write_stitched`. Winner selection
   stays per-residue pLDDT. Off-block PAE stays **null, never 0**
   (D-111). No atom is invented for a gap (`UncoveredResidue` still
   raises).
7. **Out of v1:** soft blend on refused seams; domain invent; MD / AF
   GPU refine. Those are later GOs. This Spec does not authorise them.

Overlap-confidence Kabsch does not jointly place domains. It does not
fill PAE. It does not make the chain one ESMFold forward pass. It does
not enter F-004 (D-109 ruling 7). It does not treat writing this Spec,
or naming the five refuse parents, as a scientific fix. A transformed
tile is still that tile's network output, in a different rigid frame.

---

## 2. Refuse (v1 — 10 Å STAYS; trim/weight change fit set not gate)

These thresholds are **v1 defaults**. D-126-A tests must be able to go
red against them. They are not a claim that any parent was re-measured
against them in this PR. **The 10.0 Å gate does not move.** Weighting
and trimming change *which points enter the fit*. They are not a
threshold Spec-as-fix.

| Condition | Threshold | Effect |
|---|---|---|
| Overlap **effective** Cα after weight / trim / floor | **`< 3`** | **Refuse align** (`overlap_ca_lt_3`). Weighted Kabsch still needs three corresponding points. |
| Final weighted RMSD on the fit set | **`> 10.0 Å`** | **Refuse that seam** (`rmsd_gt_10`). Record the RMSD. Do not invent a “fixed” pose. |
| Covariance of the (weighted) Cα sets | **singular / degenerate** (rank `< 2`, collinear or coincident points) | **Refuse align** (`singular_covariance`). |

Fail closed means: no `tileN_transformed.pdb`, no D-126-path
`stitched.pdb` for that parent, no silent fallback that looks like
success. The **assembler** path already on disk (D-118 / D-120) is
unchanged. The **D-125** sibling tree `kabsch/{parent_id}/` is
unchanged. A refuse is a **recorded outcome**, not a gap filled with
guessed coordinates, and not a named-exclusion of that parent from the
CLI.

The D-125 ops RMSDs on the primary five (Emma summary / Kaylee seams;
range **11.45–29.54 Å**) are **unweighted Kabsch measurements**, not a
licence to raise the gate or to mark those accessions “out.” A later
A BUILD that computes a *weighted / trimmed* RMSD on the same pair may
still refuse under 10.0 Å. That is fail-closed, not “the seam is
solved.”

---

## 3. Inventory — the primary five REFUSE (plus CLI of the 27)

Primary evaluation inventory is the **five** D-125 Kabsch REFUSE
parents. Same closed-out 27 as D-117 / D-118 / D-120 / D-125 /
`WAVE1_WAVE2_STITCHED_PARENT_IDS`. ⚠ **Not re-queried against Fly in
this Spec.** Do not invent a new science number. Do not treat naming
these five as a fix.

| parent job id | accession | Role |
|---|---|---|
| **2939** | `Q7Z408` | Primary REFUSE |
| **3272** | `Q6V0I7` | Primary REFUSE |
| **3368** | `Q5SZK8` | Primary REFUSE |
| **3394** | `Q8TDW7` | Primary REFUSE |
| **3432** | `Q8IZF6` | Primary REFUSE |

- Ops unweighted Kabsch RMSDs on these five: **11.45–29.54 Å** (Emma
  summary / Kaylee seams; not re-measured here). That range is why they
  are the primary five, not a per-parent headline and not a new
  threshold.
- **CLI must also re-run all 27** so accept / refuse counts stay
  comparable to D-125 (production dual-path **22** Kabsch / **5**
  assembler). The 22 are not excluded from the algorithm; they are not
  the primary evaluation set.
- IGF2R parent **3356** is a **different accession story** (cohort OOM
  vs census tiles) and is **not** one of the 27 (D-120). Out.
- These 27 stay **outside F-004** (D-109 ruling 7). Neither assembler,
  D-125 Kabsch, nor a future D-126 path ingests them into `/scorer`.
- Remaining ~18 tileable parents and the 3 mucins are **out of this
  Spec**.

Do not invent a new science number. Do not treat a named exclusion as
the algorithm.

---

## 4. PLAN pointer

Parent PLAN: [`PLAN-ui-post-wave2-endstate.md`](PLAN-ui-post-wave2-endstate.md)
(**D-117**). §5 was the Kabsch park → **D-125**. This Spec is the
follow-on `D-NNN` for **overlap-confidence** Kabsch after D-125 A+B
landed. D-126-A is the later Emma GO that implements §1–§3 and §5 as
code. It does **not** pre-authorise D-126-B UI, a live restitch run of
the 27, rental, a threshold change, or a named-exclusion.

---

## 5. Artifact dirs + provenance (D-126-A writes a *sibling* tree)

Assembler `write_stitched` already writes, beside an ops `out_dir`:
`stitched.pdb`, `stitched_plddt.json`, `stitched_pae.json`, `tileN.pdb`,
`tileN_plddt.json`, `tileN_pae.json`. Those names are the D-118 / D-120
served path.

D-125-A already writes:

```
<ops out_dir>/kabsch/{parent_job_id}/
```

**Do not overwrite** the assembler tree or the D-125 `kabsch/` tree
until a later Matt GO names the swap.

D-126-A writes a **third sibling tree**, outside the git repo (GUIDE:
do not `git add` `*.pdb` / PAE binaries):

```
<ops out_dir>/confidence_kabsch/{parent_job_id}/
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
- per seam: `n_ca`, `n_ca_eff`, `rmsd_angstrom` (null if refused before
  RMSD), `trim_rounds`, `refuse_reason` ∈ {`null`, `overlap_ca_lt_3`,
  `rmsd_gt_10`, `singular_covariance`}
- `algorithm`: `overlap_confidence_kabsch_then_winning_tile`
- `decision`: `D-126`
- accepted seams only: rotation \(R\) (3×3) and translation \(t\) (Å)

A refuse still writes the seam record. It does **not** write a
transformed PDB. No invented coordinates. Assembler + D-125
`kabsch/{id}/` stay on disk and stay callable.

---

## 6. UI triple-path honesty (D-126-B — later)

D-118 / D-120 / D-121 already disclose the **assembler** path.
D-125-B already names a **second** path when `kabsch/{parent}/` is on
disk. D-126-B is **UI only**, after A writes `confidence_kabsch/`.

When (and only when) D-126-path artifacts are on disk:

- The review card names **three** paths. Assembler remains the default
  **served** PDB until a Matt GO names a swap.
- Each D-126 seam shows `n_ca`, `n_ca_eff`, weighted RMSD (if
  computed), `trim_rounds`, and `refuse_reason`. Those are
  measurements, not a verdict that the holoprotein is aligned.
- A refused seam stays fail-closed — no “fixed” badge, no silent
  assembler or D-125 Kabsch PDB presented as a D-126 success.
- Forbidden language (same park as D-117 §5 / D-125 §6): “aligned,”
  “superimposed,” “seams solved,” “full-length AF-quality.”
- No invented RMSD. Honest empty when the sibling tree is missing.
- No alignment-box CTA. No F-004 ingest.

When the `confidence_kabsch/` tree is missing, the UI must not imply a
D-126 path exists and must not invent RMSD / trim counts. That absence
is not a solved seam.

---

## 7. PR split — Spec vs future A/B BUILD

| Id | What | This PR? | Gate |
|---|---|---|---|
| **D-126 Spec** | This file + `### D-126` + ship index + PLAN one-liner + hermetic docs pin tests | **Yes — this PR.** | Trinity review. Docs only. |
| **D-126-A** | Core: weighted + trimmed overlap Cα Kabsch + §2 refuse + transform tile + call existing `winning_tile`. No UI. Sibling §5 `confidence_kabsch/` tree. CLI re-runs all 27; primary eval is the five. | **No.** Later Emma GO. | After this Spec. No rent in A. |
| **D-126-B** | UI triple-path honesty (§6). Reads A's sibling tree. No persist rewrite. Default served = assembler until Matt swap GO. | **No.** Later Emma GO. | After A. |

**Out of this Spec PR:** any `.py` stitch change, any `hold48_kabsch.py`
edit, any UI, a live restitch run of the 27, F-004 ingest, ADC-C /
pipeline / `/adcs` bleed, rent / GPU / RunPod, replacing
`winning_tile`, overwriting assembler or D-125 `kabsch/`, claiming
seams solved, raising the 10.0 Å gate, treating the five as a
named-exclusion.

---

## 8. Hard stops (Spec + log)

- **No threshold Spec-as-fix.** Writing 10.0 Å again is not a repair of
  the five. The gate stays. Trim / weight are fit-set changes.
- **No named-exclusion-as-fix.** Listing 2939 / 3272 / 3368 / 3394 /
  3432 is the primary evaluation inventory, not an algorithm that skips
  them. CLI still runs the 27.
- **No invented coordinates.** Fail closed. No transformed PDB on
  refuse. No invented gap atoms.
- **No PAE zeros.** Off-block PAE stays null, never 0.
- **No F-004.** The 27 stay outside `/scorer` (D-109 ruling 7).
- **No rent in A.** D-126-A is CPU-side stdlib, same as D-125-A. No
  GPU / RunPod / MD / AF refine.
- **Never seams solved.** Forbidden language stands.
- **Keep assembler + D-125 Kabsch callable.** Production dual-path
  (22 Kabsch / 5 assembler) stays until D-126 code + ops. Do not
  overwrite `stitched.pdb` or `kabsch/{id}/`.

---

## 9. What this file is not

- Not D-126-A (core BUILD) and not D-126-B (UI).
- Not a licence to call seams solved or the chain one forward pass.
- Not a replacement of `winning_tile` by weighted Kabsch.
- Not an overwrite of D-125 `core/hold48_kabsch.py` or `kabsch/{id}/`.
- Not a threshold change and not a named-exclusion of the five.
- Not a Fly re-query of the 27. Not a restitch run.
- Not ADC-C (D-124). Not Method (D-121). Not ranking ingest.
- Not a repair of the `D-` next-free pointer.
- Not soft-blend / domain-invent / MD / AF GPU refine (out of v1).
