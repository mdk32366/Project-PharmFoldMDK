# SPEC — Linker / seam honesty (D-128)

> **COMMITTED to `docs/` as the linker / seam honesty Spec. CITED BY
> the log, not restated as authority — where this file and `docs/README.md`
> differ, THE LOG GOVERNS.** Confirm the `### D-128` header exists before
> citing.
>
> **Date:** 2026-09-05 · **Status:** Spec (algorithm authority).
> **D-128-A** (core BUILD) is a later Emma GO. **D-128-B** (UI path
> honesty + Method) is a later Emma GO that **reads** that tree. This
> file is algorithm authority; it is **not** the A BUILD and **not** the
> UI / Method BUILD.
> ⚠ **Single failure mode: linker / seam only** — the D-127 OPS
> `linker_jump_gt_10` class (7 parents, as recorded). ⚠ **NOT
> piecewise-v2.** ⚠ **NOT an RMSD Spec** (3272 / 3394 are out of the
> primary inventory). ⚠ **NOT a domain Spec** (domain intervals are
> D-127's family and are not re-opened here).
> ⚠ **Not a restitch run of the 27.** ⚠ **Not F-004 ingest.**
> ⚠ **Seams are not scientifically solved. This Spec never says
> solved.** Goal framing is **diagnose and refuse dishonest seams.**
> ⚠ **The 10.0 Å refuse gate STAYS.** No RMSD / linker threshold
> loosen without Matt. Do not raise it, do not relax it, do not add a
> per-parent exception.
> ⚠ **Parent 3432 stays accept-refuse** (signed triage). It is not a
> success target of this Spec and its status is not re-opened.
> ⚠⚠ **PHASE 5 (D-129): the seven are now `accept-refuse`, NOT
> must-hunt.** **Matt SIGNED Phase 5 named-refuse 2026-09-05 ~17:58 PT
> via Emma**, on the recorded D-128 OPS **0 of 7**. Read §3's Phase 5
> amendment and §9 before treating any parent below as open work —
> authority is
> [`SPEC-phase5-named-refuse.md`](SPEC-phase5-named-refuse.md) (**D-129**).
> ⚠ **A label, not an algorithm change:** §1a / §1b / §2 / §5 / §11
> stand as shipped, the 10.0 Å gate stays, **the seams are still NOT
> solved**, and the D-128 OPS disclosure stays **mandatory at D-128-B**
> (accept-refuse ≠ Method silence). ⚠ **3272 / 3394 stay Phase 4
> must-hunt.** ⚠ **No linker-v2.**
> ⚠ **Served stays assembler.** **D-126 remains the best experimental
> path until proven otherwise**, and the **D-127 failed experiment
> stays disclosed** (PASS 17 / REFUSE 10 / FAIL 0;
> `recovered_of_primary_three` = 0; named regress 5 vs D-125, 7 vs
> D-126 — as recorded, ⚠ not re-measured here).
> ⚠ **No trim loop.** Trim was the D-126 lie surface.
> ⚠ **No `hold48_*.py` edit in this PR.**
> Where this file and `docs/README.md` differ, THE LOG GOVERNS.
> Assembler, D-125 `core/hold48_kabsch.py`, D-126
> `core/hold48_confidence_kabsch.py`, and D-127
> `core/hold48_piecewise_kabsch.py` remain callable. D-128-A writes a
> **fifth sibling tree**; it does not overwrite those paths.

**Parents:** [`D-127` Spec](SPEC-piecewise-domain-kabsch.md) · D-127-A
`e49bf34` / #244 · D-127-B `de9a80e` / #245 (four-path UI + mandatory
Method + the D-127 OPS result) ·
[`D-126` Spec](SPEC-overlap-confidence-kabsch.md) · D-126-A `aa8aa02` /
#241 · D-126-B `abbcd00` / #242 ·
[`D-125` Spec](SPEC-kabsch-restitch.md) · D-125-A `26a40a8` / #237 ·
D-125-B `aa8d3f1` / #238 ·
[`D-117`](PLAN-ui-post-wave2-endstate.md) (PLAN / Kabsch park) ·
[`D-118`](README.md) (assembler-not-Kabsch honesty) ·
[`D-120`](README.md) (Phase 2 review of the 27) ·
[`D-121`](method-hold48-tiles.md) (Method: assembler ≠ Kabsch *today*) ·
D-116 `stitch_readiness` · D-111 `winning_tile` / emit domain-snap ·
D-109 ruling 7 (not ranking-eligible) · D-016 (provenance).
**Ship index:** [`decisions.md`](decisions.md).

---

## 1. Goal — diagnose and refuse dishonest seams

**The goal of this Spec is not a better pose. It is an honest one.**
D-128 exists to **diagnose and refuse dishonest seams**: to measure,
per seam, whether the structure a path presents as a success actually
holds its join together, and to **refuse** — fail-closed — when it does
not. A seam that is *recorded* is not a seam that is *solved*, and a
`stitched.pdb` that exists is not, by existing, honest.

This is a narrowing, not an escalation. D-125 fitted one unweighted
rigid body to the whole overlap. D-126 weighted and trimmed that same
one rigid body. D-127 cut the tile into one rigid body **per UniProt
domain**. The D-127 OPS run (as recorded; Matt GO via Emma 2026-09-05
at tip `e49bf34`; ⚠ **not re-measured here**) answered that family:
**PASS 17 / REFUSE 10 / FAIL 0**, `recovered_of_primary_three` = **0**,
`n_d125_pass_d127_refuse` = **5**, `n_d126_pass_d127_refuse` = **7**,
`n_d126_refuse_d127_pass` = **0**. Its refuse histogram concentrates in
**one** place: `linker_jump_gt_10` **×7** (2938, 2939, 3179, 3190,
3321, 3368, 3566), against `rmsd_gt_10` ×2 (3272, 3394) and
`no_domain_pieces` ×1 (3432).

**So this Spec binds exactly one failure mode: the linker / seam.**
Seven parents, named in §3. Not the RMSD class. Not the
no-domain-pieces class. Not another rigid-body decomposition.

**Optional scoped repair is linker-local rigid only.** If — and only
if — a later D-128-A attempts a repair, it is a **single weighted
rigid** \(R, t\) fitted on Cα inside a **±32 aa window** around the
offending linker / seam centre, applied to **that window's** moving-tile
atoms only (§1b). That is deliberately smaller than D-127, not larger.

⚠ **This is not a rebrand of D-127.** D-127 fitted *k* rigid bodies
chosen by **UniProt domain annotation**, covering the whole tile, and
let linkers **inherit** a neighbouring domain's transform. D-128's
optional repair fits **one** rigid body chosen by **measured seam
geometry**, covering **one ±32 aa window**, and inherits nothing. A
later A BUILD that reintroduces per-domain pieces, a piece list, domain
intervals as the fit unit, or linker-inherit is building D-127 again
under a new decision id and is **out of this Spec**.

**Diagnosis is the deliverable; repair is optional.** A D-128-A that
records honest seam metrics for every path and repairs **zero** parents
has run this Spec. **0-of-7 repaired is an allowed outcome** and a
valid experimental result. It is **not** a licence to loosen the 10.0 Å
gate, to add a trim loop, to invent a blend, or to declare a seam
solved.

**What does not change.** The **served** structure stays the
**assembler** (`core/hold48_stitch.py` `winning_tile`) until a Matt swap
GO. **D-126 remains the best experimental path among the stitch
algorithms tried so far, until proven otherwise** — D-126 OPS recovered
**2 of its primary 5** (parents 3368, 3394; as recorded, ⚠ not
re-measured here) against D-127's **0 of 3**. The **D-127 failed
experiment stays disclosed** on the Method surface (D-127-B `de9a80e`);
this Spec does not soften, retire, or bury it. Off-block PAE stays
**null, never 0** (D-111). No atom is invented for a gap
(`UncoveredResidue` still raises). The 27 stay outside F-004 (D-109
ruling 7).

---

## 1a. Seam honesty metrics (required)

**This section is the part of the Spec that is not optional.**

For **each experimental path artifact tree** — D-125 `kabsch/{id}/`,
D-126 `confidence_kabsch/{id}/`, D-127 `piecewise_kabsch/{id}/`, and
D-128's own `linker_seam/{id}/` — a later D-128-A must record, **per
seam**:

| Field | Meaning |
|---|---|
| `max_ca_jump_angstrom` | max \(\lvert \mathrm{Cα}_{ref} - \mathrm{Cα}_{moved} \rvert\) on that seam after whatever transform that path applied. **Null** if that path refused before any transform — null is not `0.0`. |
| `linker_n` | linker Cα count on that seam, **when the path defines linkers** (D-127 does; D-125 / D-126 do not). Null / absent when not applicable. |
| `max_linker_ca_jump` | max linker Cα jump, **when applicable** (same restriction). Null / absent when not applicable. |
| `path` | which tree the row describes (`kabsch` / `confidence_kabsch` / `piecewise_kabsch` / `linker_seam`). |
| `honest` | `false` when `max_ca_jump_angstrom` **`> 10.0 Å`**; `true` when it is `≤ 10.0 Å`; **null** when the metric is null (unknown is not honest). |

**The honesty rule.** A path that **ends** with a seam
`max_ca_jump_angstrom` **`> 10.0 Å`** is **dishonest for that seam**.
Fail-closed follows immediately: **no success PDB may be presented as
honest** for a dishonest seam. Concretely, for a seam whose
`honest` is `false` or `null`:

- No D-128-path `stitched.pdb` is written or kept for that parent
  (§1b step 7, all-or-nothing).
- No existing path's `stitched.pdb` — assembler, D-125, D-126, or
  D-127 — may be surfaced, badged, or downloaded **as an honest
  D-128 result**. Those files stay on disk, stay callable, and stay
  labelled as what they are.
- The seam row is still written. A refuse is a **recorded outcome**,
  not a gap filled with guessed coordinates and not a parent quietly
  dropped from the run.

**The gate stays 10.0 Å.** The honesty threshold *is* the existing
refuse gate; §1a does not introduce a second number and must not be
read as licence to tune the first. No RMSD / linker threshold loosen
without Matt.

**Reading the prior trees is a read.** Honesty rows for D-125 / D-126 /
D-127 seams are computed by **reading** those trees and are written
**into the D-128 tree** (§5). A later A BUILD must **not** rewrite,
append to, or overwrite `kabsch/{id}/`, `confidence_kabsch/{id}/`, or
`piecewise_kabsch/{id}/`. If a prior tree is absent, the honesty row is
an **honest absence with a stated reason** — never a zero, never an
assumed pass, and never a number carried over from a different parent
or a different path.

**Why this is the load-bearing half.** D-126's lesson was that a small
*weighted* RMSD can hide a large *full-overlap* jump (ops jumps
**28–68 Å** on 2939 / 3272 / 3432, as recorded). D-127's OPS answer was
that cutting the tile into more rigid bodies moved the failure into the
**linkers** ×7 rather than removing it. Both lessons are the same
lesson: **a pass on a fit statistic is not a held join.** §1a makes
that measurable per path, per seam, once — so no future path can pass
by choosing a flattering statistic.

---

## 1b. Linker-local rigid — optional scoped repair (D-128-A)

**Inventory (primary evaluation):** the **seven** signed must-hunt
linker parents of §3 — and **only** those — are the primary evaluation
set. A CLI **may** also run all **27** (`WAVE1_WAVE2_STITCHED_PARENT_IDS`)
for confusion against the prior paths, but it must **not** treat
**3272**, **3394**, or **3432** as success targets of this Spec. Those
three are other failure classes: 3272 / 3394 are `rmsd_gt_10` (an RMSD
Spec, not this one) and 3432 is `no_domain_pieces` and **stays
accept-refuse** (§3).

**Pinned constants.** Window half-width **W = 32 aa**. Weight floor
\(\varepsilon\) = **1e-3**. Weighted RMSD on the window's fit set:

\[\mathrm{weighted\ RMSD}
= \sqrt{\sum_i w_i \,\lVert R p_i + t - q_i\rVert^2 / \sum_i w_i}\]

Gate for accept / refuse is that **weighted** RMSD **`≤ 10.0 Å`**
(refuse if \(\gt 10.0\) Å) **and** the post-apply seam
`max_ca_jump_angstrom` **`≤ 10.0 Å`**. Both are the same 10.0 Å. **No
trim loop.**

Steps:

1. **Identify the offending seam / linker.** Either from the **prior
   D-127 refuse record** (`refuse_reason` = `linker_jump_gt_10` on that
   seam, read from `piecewise_kabsch/{id}/seams.jsonl`) **or** from the
   **measured** §1a `max_ca_jump_angstrom` on that seam. Do not guess a
   seam, do not pick the seam that fits best, and do not invent a linker
   boundary that no record or measurement names. A parent with no
   identifiable offending seam is a **recorded absence**, not a silent
   skip.
2. **Window.** **±32 aa** around the linker / seam centre (**W = 32**,
   pinned in this Spec). The centre is span-relative and derived from
   the stored tile windows (`tile_start` / `tile_end`) and the
   identified seam of step 1. **A later A BUILD's tests must be able to
   go red against W = 32** — it is a pinned v1 default, not a knob to
   tune until a parent passes.
3. **Weighted Kabsch on Cα in that window only.** \(\varepsilon =
   1\mathrm{e}{-3}\); \(w_i = \min(\mathrm{pLDDT}_A,
   \mathrm{pLDDT}_B)/100\) clamped \(\ge \varepsilon\); weighted
   centroids → weighted covariance \(H\) → SVD → rotation \(R\) with
   \(\det R = +1\) correction → translation \(t\). **NO trim loop.** No
   pLDDT-floor-then-trim order. Weight + one Kabsch. Same
   adjacency / `stitch_readiness` (D-116) / prefer-lower-dups
   (**3673/3674/3675**; spares **3693/3695/3696** unused) /
   **N-terminal reference** as D-125 / D-126 / D-127.
4. **Apply \(R, t\) only to moving-tile atoms in that window.** Atoms
   outside the ±32 aa window are **not** moved and **do not** inherit a
   transform. There is no piece list, no per-domain fit, and no
   linker-inherit rule in this Spec — those are D-127's and stay
   D-127's. The N-terminal tile is not moved.
5. **Refuse (fail closed).** Window Cα count `< 3` → `overlap_ca_lt_3`;
   window weighted RMSD `> 10.0 Å` → `rmsd_gt_10`; singular /
   degenerate covariance (rank `< 2`) → `singular_covariance`;
   **post-apply** seam `max_ca_jump_angstrom` `> 10.0 Å` →
   `seam_jump_gt_10`. Full table in §2.
6. **On accept**, feed the (window-transformed) `TileFold` list into the
   **existing** `winning_tile` / `stitch_pdb` / `stitch_plddt` /
   `stitch_pae` / `write_stitched`. Winner selection stays per-residue
   pLDDT. Off-block PAE stays **null, never 0** (D-111). No atom is
   invented for a gap.
7. **All-or-nothing parent; clear partials.** If **any** seam of the
   parent refuses, parent outcome = refused: clear / do not leave a
   partial `tileN_transformed.pdb` or a D-128-path `stitched.pdb` (same
   fail-closed spirit as D-125 `_clear_success_artifacts` in
   `core/hold48_kabsch.py`). Seam rows are still recorded. Do not
   invent a pose.

**Out of v1:** soft invent blend; MD / AF GPU refine; a second window
size tried until a parent passes; per-domain pieces; linker-inherit;
any joint placement. Those are a **later phase, not A**. This Spec does
not authorise them. Recovering **0-of-7** does **not** license them, a
threshold change, or a named-exclusion.

**Disclosure required (anti pass-by-statistic):**

- **Per seam, per path:** the §1a honesty row (`path`,
  `max_ca_jump_angstrom`, `honest`, and the linker fields where
  applicable).
- **Per D-128 seam:** `window_start` / `window_end` (span-relative),
  `window_half_width_aa` (= 32), `n_ca`, weighted `rmsd_angstrom`
  (null if refused before RMSD), `refuse_reason`, and the post-apply
  `max_ca_jump_angstrom` (null if refused before any transform).
- **Per parent:** the identified offending seam and **how** it was
  identified (`from_d127_refuse` or `from_measured_jump`).

Those metrics do **not** move the 10.0 Å gate. A must write them; UI /
Method (B) later shows them.

Linker-local Kabsch does not jointly place anything in a new network
forward pass. It does not fill PAE. It does not make the chain one
ESMFold forward pass. It does not enter F-004 (D-109 ruling 7). It does
not treat writing this Spec, or naming the seven parents, as a
scientific fix. A transformed window is still that tile's network
output, moved.

---

## 2. Refuse (v1 — 10 Å STAYS — do not raise, do not loosen)

These thresholds are **v1 defaults**. D-128-A tests must be able to go
red against them. They are not a claim that any parent was re-measured
against them in this PR. **The 10.0 Å gate does not move**, and no
RMSD / linker threshold loosens without Matt. D-128 changes *how small
the fitted region is* and *what must be measured*. It is not a
threshold Spec-as-fix.

| Condition | Threshold | Effect |
|---|---|---|
| Window overlap Cα count | **`< 3`** | **Refuse** (`overlap_ca_lt_3`). Weighted Kabsch still needs three corresponding points. |
| Window weighted RMSD on the fit set | **`> 10.0 Å`** | **Refuse** (`rmsd_gt_10`). Record the RMSD. Do not invent a “fixed” pose. |
| Covariance of the (weighted) window Cα sets | **singular / degenerate** (rank `< 2`, collinear or coincident points) | **Refuse** (`singular_covariance`). |
| **Post-apply** seam max Cα jump | **`> 10.0 Å`** | **Refuse** (`seam_jump_gt_10`). The seam is **dishonest** (§1a); no success PDB is presented as honest. |

Fail closed means: no `tileN_transformed.pdb`, no D-128-path
`stitched.pdb` for that parent, no silent fallback that looks like
success. **All-or-nothing parent refuse:** if **any** seam refuses,
parent outcome = refused; clear / do not leave a partial
`tileN_transformed.pdb` or D-128-path `stitched.pdb` from an earlier
accepted seam of that same parent (same fail-closed spirit as D-125
`_clear_success_artifacts` in `core/hold48_kabsch.py`). Seam rows are
still recorded.

The **assembler** path already on disk (D-118 / D-120) is unchanged.
The **D-125** tree `kabsch/{parent_id}/`, the **D-126** tree
`confidence_kabsch/{parent_id}/`, and the **D-127** tree
`piecewise_kabsch/{parent_id}/` are unchanged. A refuse is a
**recorded outcome**, not a gap filled with guessed coordinates, and
not a named-exclusion of that parent from the CLI.

⚠ **`seam_jump_gt_10` is a new reason name, not a renamed
`linker_jump_gt_10`.** D-127's `linker_jump_gt_10` is a **parent**
refuse computed after **linker inherit** across domain pieces.
D-128's `seam_jump_gt_10` is computed after the **single window
transform** of §1b. They are different measurements of different
algorithms and must not be conflated in a report, a UI, or a test.

The D-127 OPS histogram (`linker_jump_gt_10` ×7) is **motivation, not a
threshold**. It explains why the failure mode this Spec hunts is the
linker / seam, not a licence to raise the gate or to mark any accession
“out.” A later A BUILD that fits a ±32 aa window on the same pair may
still refuse under 10.0 Å. That is fail-closed, not “the seam is
solved.”

---

## 3. Inventory — the seven signed must-hunt linker parents

Primary evaluation inventory is the **seven** parents that refused
**`linker_jump_gt_10`** in the D-127 OPS run, as recorded (Matt GO via
Emma 2026-09-05 at tip `e49bf34`; carried in `docs/README.md`
`#### D-127-B amendment 1` item 3, `ARCHITECTURE.md`, and
[`method-hold48-tiles.md`](method-hold48-tiles.md)). Same closed-out
**27** as D-117 / D-118 / D-120 / D-125 / D-126 / D-127 /
`WAVE1_WAVE2_STITCHED_PARENT_IDS`. ⚠ **Not re-queried against Fly in
this Spec.** ⚠ **Not re-measured here.** Do not invent a new science
number. Do not treat naming these seven as a fix.

| parent job id | accession | Role |
|---|---|---|
| **2938** | *not recorded in this log — do not invent* | Signed must-hunt linker parent (D-127 OPS `linker_jump_gt_10`) |
| **2939** | `Q7Z408` | Signed must-hunt linker parent (D-127 OPS `linker_jump_gt_10`) |
| **3179** | *not recorded in this log — do not invent* | Signed must-hunt linker parent (D-127 OPS `linker_jump_gt_10`) |
| **3190** | *not recorded in this log — do not invent* | Signed must-hunt linker parent (D-127 OPS `linker_jump_gt_10`) |
| **3321** | *not recorded in this log — do not invent* | Signed must-hunt linker parent (D-127 OPS `linker_jump_gt_10`) |
| **3368** | `Q5SZK8` | Signed must-hunt linker parent (D-127 OPS `linker_jump_gt_10`); also one of the **2 of 5** D-126 OPS recovered |
| **3566** | *not recorded in this log — do not invent* | Signed must-hunt linker parent (D-127 OPS `linker_jump_gt_10`) |

**Accessions are named only where the log already carries them**
(2939 `Q7Z408` and 3368 `Q5SZK8`, from D-127 Spec §3 / D-127-B). For
the other five the accession is **not on record in this log**; a later
A BUILD resolves it from the database rather than from prose, and
**nobody writes one here from memory** (D-016).

> ### ⚠ Phase 5 amendment (D-129) — these seven are no longer must-hunt
>
> **Matt SIGNED Phase 5 named-refuse 2026-09-05 ~17:58 PT, via Emma.**
> After that sign the seven parents in the table above — **2938, 2939,
> 3179, 3190, 3321, 3368, 3566** — are **no longer must-hunt**. They
> are **`accept-refuse`**: the recorded honest outcome of a refusal,
> **closed to further hunting**, together with **3432** (already
> accept-refuse). Authority:
> [`SPEC-phase5-named-refuse.md`](SPEC-phase5-named-refuse.md) (**D-129**)
> §2 / §3 / §4, and `### D-129` in [`README.md`](README.md) — where that
> log and this file differ, **THE LOG GOVERNS**.
>
> The basis was the D-128 OPS run of these seven: **PASS 0 / REFUSE 7 /
> FAIL 0 / SKIP 0**, `repaired_of_seven` = **0** (as recorded by Kaylee
> at tip `9e65cbf`, out_root `linker_seam_ops_2026-09-05`;
> ⚠ **not re-measured**). That zero was **pre-registered as an allowed
> outcome** by this Spec (§1b / §3 / §11) *before* the run, so it is a
> **finding, not a D-128 miss**.
>
> ⚠ **This changes a LABEL, not the algorithm.** §1a, §1b, §2, §5 and
> §11 stand exactly as shipped. The **10.0 Å** gate stays, **W = 32**
> stays, **ε = 1e-3** stays, and the refuse reason set is unchanged.
> ⚠ **The seams are NOT solved.** This Spec still never says solved;
> accept-refuse retires the **hunt**, not the **record**.
> ⚠ **`accept-refuse` ≠ Method silence.** D-129 §4 keeps the D-128 OPS
> disclosure **mandatory** at D-128-B — the **0 of 7** and the named
> confusion (`n_d125_pass_d128_refuse` = **5**,
> `n_d126_pass_d128_refuse` = **6**) ship **with** the label, never
> buried under it.
> ⚠ **3272 / 3394 are NOT covered** by that sign. They stay **Phase 4
> must-hunt** (D-129 §6) and move only on a **separate Matt GO**.
> ⚠ **No linker-v2** follows. The stitch-algorithm family **freezes**
> (D-129 §7): served stays **assembler**, **D-126 remains the best
> experimental path until proven otherwise**, and the **D-127 and D-128
> failed rescues stay disclosed**.

**Explicitly out of the primary inventory:**

| parent job id | D-127 OPS reason | Why it is out of *this* Spec |
|---|---|---|
| **3272** `Q6V0I7` | `rmsd_gt_10` | RMSD class. **This is not an RMSD Spec.** Not a success target. |
| **3394** `Q8TDW7` | `rmsd_gt_10` | RMSD class. Not a success target. Also one of the **2 of 5** D-126 OPS recovered. |
| **3432** `Q8IZF6` | `no_domain_pieces` | **Stays accept-refuse (signed triage).** Not a success target; its status is **not re-opened**, not reclassified, and not counted as a D-128 miss. |

- **3432 stays accept-refuse.** The signed triage accepted that refusal
  as the honest outcome. A later A BUILD must not attempt to convert it,
  must not report it as a D-128 failure, and must not use it to argue
  for a threshold change. It may appear in a CLI run of the 27 as a
  **recorded** row.
- **CLI may also re-run all 27** so accept / refuse counts stay
  comparable to D-125, D-126, and D-127. The other 20 are not excluded
  from the algorithm; they are not the primary evaluation set, and they
  are not success targets.
- **0-of-7 repaired is an allowed outcome.** Repairing zero of the seven
  is a valid experimental result. Do not loosen the 10.0 Å gate, invent
  a blend, or add a trim loop to force passes. A later A BUILD that
  repairs none of the seven has still run the Spec — the §1a honesty
  rows are the deliverable; that zero is a finding, not a licence to
  change the algorithm.
- IGF2R parent **3356** is a **different accession story** (cohort OOM
  vs census tiles) and is **not** one of the 27 (D-120). Out. The IGF2R
  seam ~**88.76 Å** is a join-jump disclosure, **not** a Kabsch RMSD and
  **not** a D-128 metric. ⚠ Not re-measured.
- These 27 stay **outside F-004** (D-109 ruling 7). Neither assembler,
  D-125 Kabsch, D-126 confidence Kabsch, D-127 piecewise, nor a future
  D-128 path ingests them into `/scorer`.
- Remaining ~18 tileable parents and the 3 mucins are **out of this
  Spec**.

Do not invent a new science number. Do not treat a named exclusion as
the algorithm.

---

## 4. PLAN pointer

Parent PLAN: [`PLAN-ui-post-wave2-endstate.md`](PLAN-ui-post-wave2-endstate.md)
(**D-117**). §5 was the Kabsch park → **D-125**. Overlap-confidence
follow-on was **D-126**. Piecewise / domain-aware follow-on was
**D-127**, and its OPS run answered that family negatively. This Spec is
the follow-on `D-NNN` for **linker / seam honesty** after D-127 A+B
landed. D-128-A is the Emma GO that implements §1a / §1b / §2 / §3 and
§5 as code (a later sibling module + CLI). It does **not** pre-authorise
D-128-B UI / Method, a live restitch run of the 27, rental, a threshold
change, a named-exclusion, a trim loop, a served-path swap, or MD / AF
GPU refine. The plan does not become a BUILD GO.

---

## 5. Artifact dirs + provenance (D-128-A writes a *sibling* tree)

Assembler `write_stitched` already writes, beside an ops `out_dir`:
`stitched.pdb`, `stitched_plddt.json`, `stitched_pae.json`, `tileN.pdb`,
`tileN_plddt.json`, `tileN_pae.json`. Those names are the D-118 / D-120
served path.

Already on disk from the earlier paths:

```
<ops out_dir>/kabsch/{parent_job_id}/               # D-125-A
<ops out_dir>/confidence_kabsch/{parent_job_id}/    # D-126-A
<ops out_dir>/piecewise_kabsch/{parent_job_id}/     # D-127-A
```

**Do not overwrite** the assembler tree, the D-125 `kabsch/` tree, the
D-126 `confidence_kabsch/` tree, or the D-127 `piecewise_kabsch/` tree
until a later Matt GO names the swap. Those four paths stay callable.

D-128-A writes a **fifth sibling tree**, outside the git repo (GUIDE:
do not `git add` `*.pdb` / PAE binaries):

```
<ops out_dir>/linker_seam/{parent_id}/
  provenance.json
  seams.jsonl               # D-128 seam rows (window fit + refuse)
  seam_honesty.jsonl        # §1a honesty rows, one per (path, seam)
  tile{n}_transformed.pdb   # only if that tile's inbound seam was accepted
  stitched.pdb              # via existing write_stitched, after transform
  stitched_plddt.json
  stitched_pae.json
```

`provenance.json` / each row must make a refuse reconstructible
(D-016):

- `parent_job_id`, chosen tile job ids, windows
- per D-128 seam: `refuse_reason` ∈ {`null`, `overlap_ca_lt_3`,
  `rmsd_gt_10`, `singular_covariance`, `seam_jump_gt_10`}
- per D-128 seam: `window_start`, `window_end`,
  `window_half_width_aa` (= **32**), `n_ca`, `rmsd_angstrom` (window
  weighted RMSD; null if refused before RMSD), post-apply
  `max_ca_jump_angstrom` (null if refused before any transform)
- per D-128 seam: `offending_seam_source` ∈ {`from_d127_refuse`,
  `from_measured_jump`}
- `seam_honesty.jsonl` rows (§1a): `path` ∈ {`kabsch`,
  `confidence_kabsch`, `piecewise_kabsch`, `linker_seam`},
  `max_ca_jump_angstrom`, `honest`, and `linker_n` /
  `max_linker_ca_jump` **where that path defines them**; an absent
  prior tree is an **honest absence with a reason**, never a zero
- `algorithm`: `linker_local_kabsch_then_winning_tile`
- `decision`: `D-128`
- accepted seams only: rotation \(R\) (3×3) and translation \(t\) (Å)

`max_ca_jump_angstrom` is recorded **after** apply. On
refuse-before-transform it may be null. It does **not** move the 10.0 Å
gate. A must write it; UI / Method (B) later shows it.

A refuse still writes the seam record. It does **not** write a
transformed PDB. **All-or-nothing:** if any seam refuses, clear / do not
leave partial `tileN_transformed.pdb` or D-128-path `stitched.pdb`.
No invented coordinates. Assembler + `kabsch/{id}/` +
`confidence_kabsch/{id}/` + `piecewise_kabsch/{id}/` stay on disk and
stay callable.

---

## 6. UI path honesty (D-128-B — later, not this PR)

D-118 / D-120 / D-121 already disclose the **assembler** path. D-125-B
names a second path, D-126-B a third, and D-127-B a fourth
(`assembly_review.four_path`, one row per domain piece, never a seam
average). D-128-B is **UI only**, after A writes `linker_seam/`.

When (and only when) D-128-path artifacts are on disk:

- The review card names the D-128 path **as a path**, and carries the
  §1a **honesty** read: per seam, per path, `max_ca_jump_angstrom` and
  whether that path is **honest** for that seam (`> 10.0 Å` →
  dishonest). Assembler remains the default **served** PDB until a
  Matt GO names a swap.
- Each D-128 seam shows `window_start` / `window_end` /
  `window_half_width_aa`, `n_ca`, weighted `rmsd_angstrom` (if
  computed), post-apply `max_ca_jump_angstrom`, `offending_seam_source`,
  and `refuse_reason`. Those are **measurements**, not a verdict that
  the holoprotein is aligned. A wrote the fields; B does not invent
  them. On refuse-before-transform they may be null (honest empty) —
  **null renders as an absence, never `0.00 Å`**.
- A dishonest seam (§1a) is **never** shown with a success PDB
  presented as honest. No “fixed” badge, no “repaired” badge, no silent
  assembler / D-125 / D-126 / D-127 PDB presented as a D-128 success.
- The **D-127 failed experiment stays disclosed** and **D-126 stays
  named as the best experimental path so far**. D-128-B must not quietly
  replace that disclosure with a fresh-hypothesis story.
- Forbidden language (same park as D-117 §5 / D-125 §6 / D-126 §6 /
  D-127 §6): “aligned,” “superimposed,” “seams solved,” “seams fixed,”
  “full-length AF-quality.”
- No invented metric. Honest empty when the sibling tree is missing.
- No alignment-box CTA. No F-004 ingest.

When the `linker_seam/` tree is missing, the UI must not imply a D-128
path exists and must not invent jumps / windows / RMSD. That absence is
not a solved seam. Default served = assembler.

---

## 7. Method / owner-facing (D-128-B — later, and mandatory then)

Matt / Emma standing requirement (2026-09-05, bound at D-127 §7 and
kept here): **Method must surface the stitch-path train honestly when a
path exists**, and a code-only ship is forbidden. D-128-B carries the
owner-facing addendum; a D-128-A that writes `linker_seam/` without one
is **not done**.

Same pattern as D-121 / D-125-B / D-126-B / D-127-B: an **additive**
`/method` addendum plus the owner markdown in
[`method-hold48-tiles.md`](method-hold48-tiles.md). Do not gut the
assembler Method. Do not rewrite #229. D-121 / D-125-B / D-126-B /
D-127-B sections **stay** — including the D-127 OPS disclosure.

**This Spec PR ships no Method edit.** §7 is the authority a later B
discharges, and this file carries the **8th-grade excerpt** it must
carry:

**Required Method copy (plain, 8th-grade):**

The stitch-path train, in order, is:

1. **Assembler** — winner-tile pLDDT. Default **served** PDB until a
   Matt swap GO.
2. **D-125 Kabsch** — one unweighted rigid move on overlap Cα, then the
   same assembler.
3. **D-126 confidence** — one weighted / trimmed rigid move on overlap
   Cα, then the same assembler. Its lesson: a small **weighted** RMSD
   can hide a large **full-overlap** jump (ops jumps 28–68 Å on
   2939 / 3272 / 3432). **D-126 is still the best experimental path we
   have tried** — it recovered **2 of its primary 5** (parents 3368,
   3394), as recorded.
4. **D-127 piecewise / domain** — one weighted rigid move per UniProt
   domain, then the same assembler. **The run says it did not pay
   off:** PASS 17 / REFUSE 10 / FAIL 0, **0 of 3** primary parents
   recovered, and it **gave back** 5 parents D-125 had accepted and 7
   D-126 had accepted. That failed experiment **stays disclosed.**
5. **D-128 linker / seam honesty** — first, **measure** every path's
   seam jump and say plainly which paths are **dishonest** at that seam
   (a jump over **10.0 Å**). Then, optionally, try **one** small rigid
   move inside a **±32 aa** window around the offending linker. Most of
   D-127's failures were at the linkers (**7 of 10** refuses), which is
   why the window is where it is.

**What “dishonest” means here.** It is a statement about the
**structure file**, not about a person. If a path's seam still jumps
more than **10.0 Å** after its own transform, then presenting that
path's `stitched.pdb` as a good join would be dishonest — so we refuse
it and record why. **The 10.0 Å gate stays.**

**Refuse table (high level, not a science headline).** A window refuses
if it has fewer than three Cα, if its weighted RMSD is above
**10.0 Å**, or if the points are collinear. The parent refuses if the
seam still jumps more than **10.0 Å** after the move. A refuse writes a
record. It does not write a “fixed” structure.

**Seam disclosure.** When the D-128 path exists, Method and the review
card name the per-path seam jumps and the D-128 window fit. Those are
measurements. They are **not** a verdict that the holoprotein is lined
up. **Never claim seams solved** — this Spec's goal is to **diagnose and
refuse dishonest seams**, not to solve them. Forbidden: “aligned,”
“superimposed,” “seams solved,” “seams fixed,” “full-length
AF-quality.”

**Default served = assembler** until a Matt swap GO. Method must say
so. Honest empty when `linker_seam/` is missing — do not invent the
fifth path.

**What Method does not do.** It does not replace the assembler story.
It does not make the long chain one ESMFold pass. It does not fill PAE.
It does not enter F-004. It is not medical advice.

---

## 8. PR split — Spec vs A/B BUILD

| Id | What | This PR? | Gate |
|---|---|---|---|
| **D-128 Spec** | This file + `### D-128` + ship index + ARCHITECTURE one-liner + PLAN pointer + Test_Plan T-ids + hermetic docs pin tests. Includes the Method excerpt as authority. | **Yes — this PR.** | Trinity reviewed. **Docs only.** |
| **D-128-A** | Core: §1a honesty rows for every path tree + optional linker-local weighted Kabsch in a ±32 aa window (no trim, no pieces, no inherit) + §2 refuse + call existing `winning_tile`. No UI. Sibling §5 `linker_seam/` tree. Primary eval is the seven; CLI may run the 27. **CPU, no rent.** | No. Later Emma GO. | After the Spec is on `main`. **No rent in A.** Not “done” without Method. |
| **D-128-B** | UI path honesty (§6) **and** Method owner markdown + MethodNote additive section (§7). Reads A's sibling tree. No persist rewrite. Default served = assembler until a Matt swap GO. | No. Later Emma GO. | After A. **Mandatory** before calling D-128 “done.” |
| **GPU refine** | Optional MD / AF GPU refine | No. Later phase, **not A**. | Not this family of PRs. |

**Kaylee does not BUILD** until this Spec is on `main` **and** an
Emma / Matt GO names D-128-A. CloudAgent is already Opus-pinned; that
pin is a fact of the build lane, not a licence to start A early.

**Out of this Spec PR:** any edit to `hold48_*.py`, any UI, any Method
edit, a live restitch run of the 27, F-004 ingest, ADC-C / pipeline /
`/adcs` bleed, rent / GPU / RunPod, replacing `winning_tile`,
overwriting assembler or `kabsch/` or `confidence_kabsch/` or
`piecewise_kabsch/`, claiming seams solved, raising **or loosening**
the 10.0 Å gate, re-opening 3432, treating the seven as a
named-exclusion, a trim loop, a soft invent blend, a piecewise-v2, an
RMSD Spec, a domain Spec.

**Out of the A PR:** any UI, any Method-only claim of done, a live
restitch run of the 27, F-004 ingest, rent / GPU / RunPod / MD / AF
refine, replacing `winning_tile`, overwriting the four existing trees,
claiming seams solved, raising or loosening the 10.0 Å gate, a trim
loop, per-domain pieces, linker-inherit, a second window size tried
until a parent passes. A does **not** discharge the Method obligation —
B (or a Method-bearing PR) must still ship §7.

---

## 9. Hard stops (Spec + log)

- **No threshold Spec-as-fix.** Writing 10.0 Å again is not a repair of
  the seven. The gate stays. **No RMSD / linker threshold loosen
  without Matt.**
- **No piecewise-v2.** No per-domain pieces, no piece list, no domain
  intervals as the fit unit, no linker-inherit. D-127's family is
  answered; this is not a rebrand of it.
- **No RMSD Spec bleed.** 3272 / 3394 are `rmsd_gt_10` and are **out of
  the primary inventory**. This Spec does not chase them.
- **No domain Spec bleed.** Domain annotation is not this Spec's fit
  unit and `no_domain_pieces` is not this Spec's failure mode.
- **3432 stays accept-refuse** (signed triage). Not re-opened, not
  reclassified, not a success target, not counted as a D-128 miss.
- ⚠ **After the Phase 5 sign, the seven are accept-refuse too — not
  must-hunt** (**D-129**;
  [`SPEC-phase5-named-refuse.md`](SPEC-phase5-named-refuse.md) §2 / §3;
  `### D-129` in [`README.md`](README.md)). **Matt SIGNED Phase 5
  named-refuse 2026-09-05 ~17:58 PT via Emma** on the recorded D-128
  OPS **0 of 7**. So: **eight** parents are `accept-refuse` (the seven
  **+ 3432**); none of the eight may be labelled **open must-hunt**,
  **solved / fixed / repaired**, or **a D-128 miss**; **0-of-7 was
  pre-registered** as allowed by this Spec, not discovered as a
  failure. ⚠ **A label, not an algorithm change** — §1a / §1b / §2 /
  §5 / §11 stand as shipped, the **10.0 Å** gate stays, and **the
  seams are still NOT solved**. ⚠ **Accept-refuse is not Method
  silence:** D-129 §4 keeps the D-128 OPS disclosure **mandatory at
  D-128-B** (**0 of 7** plus **5** vs D-125 / **6** vs D-126, never
  buried). ⚠ **3272 / 3394 stay Phase 4 must-hunt** and need a
  **separate Matt GO**. ⚠ **No linker-v2** — the family freezes.
- **No named-exclusion-as-fix.** Listing the seven is the primary
  evaluation inventory, not an algorithm that skips anyone. A CLI may
  still run the 27.
- **No invent.** Fail closed. No transformed PDB on refuse. No invented
  gap atoms. No soft invent blend. No invented accession for the five
  parents whose accession this log does not carry. All-or-nothing
  parent: no partial `tileN_transformed.pdb` / D-128 `stitched.pdb`
  when any seam refuses.
- **No PAE zeros.** Off-block PAE stays null, never 0.
- **No F-004.** The 27 stay outside `/scorer` (D-109 ruling 7).
- **No rent in A.** D-128-A is CPU-side stdlib, same as D-125-A /
  D-126-A / D-127-A. No GPU / RunPod / MD / AF refine. GPU refine is a
  later phase, not A.
- **Never seams solved.** This Spec never says solved. Goal framing is
  **diagnose and refuse dishonest seams.** Forbidden language stands.
- **Keep prior paths callable.** Assembler + D-125 Kabsch + D-126
  confidence + D-127 piecewise stay callable. Do not overwrite
  `stitched.pdb`, `kabsch/{id}/`, `confidence_kabsch/{id}/`, or
  `piecewise_kabsch/{id}/`.
- **Served stays assembler.** No auto-flip on any pass count. A swap is
  a Matt GO.
- **D-126 remains the best experimental path until proven otherwise**,
  and the **D-127 failed experiment stays disclosed.** Neither may be
  softened or dropped by a D-128 surface.
- **No trim loop.** Trim was the D-126 lie surface. This Spec does not
  reopen it.
- **W = 32 stays.** The window half-width is a pinned v1 default;
  D-128-A tests must be able to go red against it. Do not tune it until
  a parent passes.
- **0-of-7 repaired is allowed.** Do not loosen a gate or invent a
  blend to force passes. The §1a honesty rows are the deliverable.
- **ε = 1e-3.** Weight floor is pinned. One weighted Kabsch per window.
- **No stitch code in this PR.** No `hold48_*.py` edit.
- **No silent code-only.** Method must surface the D-128 path and the
  stitch-path train when the path exists (§7) — mandatory at B.

---

## 10. What this file is not

- **Not D-128-A** (core). **Not D-128-B** (UI + Method). This file is
  the Spec, not a BUILD.
- **Not piecewise-v2.** Not a second domain decomposition, not a piece
  list, not linker-inherit.
- **Not an RMSD Spec.** 3272 / 3394 are out of the primary inventory.
- **Not a domain Spec.** `no_domain_pieces` is not this failure mode.
- Not a re-opening of **3432**, which stays accept-refuse.
- Not a licence to call seams solved or the chain one forward pass.
- Not a replacement of `winning_tile` by a window Kabsch.
- Not an overwrite of `core/hold48_kabsch.py` / `kabsch/{id}/`,
  `core/hold48_confidence_kabsch.py` / `confidence_kabsch/{id}/`, or
  `core/hold48_piecewise_kabsch.py` / `piecewise_kabsch/{id}/`.
- Not a threshold change (up **or** down) and not a named-exclusion of
  the seven.
- Not a served-path swap and not a retraction of the D-127 OPS
  disclosure or of D-126's standing as best experimental path so far.
- Not a Fly re-query of the 27. Not a restitch run. Not an ops run.
- Not ADC-C (D-124). Not a rewrite of D-121 assembler Method, and not a
  Method edit at all in this PR (the D-128 Method addendum is
  **mandatory at B**).
- Not ranking ingest.
- Not a repair of the `D-` next-free pointer.
- Not soft-blend / MD / AF GPU refine (out of v1; later phase, not A).
- Not a licence to treat 0-of-7 repaired as a failure that moves the
  gate.
- Not a CI assert against live ops (the confusion vs D-125 / D-126 /
  D-127 is a required **report** field, not a gate test).

---

## 11. Ops success report (required fields; not a CI assert)

When a later D-128-A (or ops) run covers the seven — and, if run, the
27 — the **ops success report** MUST include the §1a honesty rows and
confusion vs D-125 **and** D-126 **and** D-127. This is documentation
of required report fields. It is **not** a CI assert against live ops
and not a restitch measurement in this Spec PR.

Required fields:

| Field | Meaning |
|---|---|
| `n_seams_measured` | seams with a §1a honesty row written |
| `n_dishonest_kabsch` | D-125 seams with `max_ca_jump_angstrom > 10.0 Å` |
| `n_dishonest_confidence_kabsch` | D-126 seams over the gate |
| `n_dishonest_piecewise_kabsch` | D-127 seams over the gate |
| `n_dishonest_linker_seam` | D-128 seams over the gate after the window move |
| `n_honesty_unknown` | seams whose jump is **null** (tree absent / refused before transform) — unknown is not honest |
| `n_d125_pass_d128_refuse` | D-125 PASS parents that D-128 refuses |
| `n_d126_pass_d128_refuse` | D-126 PASS parents that D-128 refuses |
| `n_d127_pass_d128_refuse` | D-127 PASS parents that D-128 refuses |
| `n_d127_refuse_d128_pass` | D-127 REFUSE parents that D-128 accepts |
| `repaired_of_seven` | 0..7; **0 is an allowed outcome** |

A non-zero `n_d125_pass_d128_refuse`, `n_d126_pass_d128_refuse`, or
`n_d127_pass_d128_refuse` is a **named finding**, not silent success.
Do not bury a drop inside an overall accept count — that is the mistake
the D-127 OPS disclosure was written to avoid. Repairing **0-of-7** is a
valid experimental result; do not loosen the 10.0 Å gate or invent a
blend to force passes. And if the honesty rows say a path is dishonest
at a seam, the report says so plainly — including for D-128's own path.
