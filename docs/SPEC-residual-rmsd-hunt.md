# SPEC — Phase 4 residual-RMSD hunt (D-130)

> **COMMITTED to `docs/` as the Phase 4 residual-RMSD Spec. CITED BY the
> log, not restated as authority — where this file and `docs/README.md`
> differ, THE LOG GOVERNS.** Confirm the `### D-130` header exists
> before citing.
>
> **Date:** 2026-09-06 · **Status:** Spec (algorithm authority).
> **D-130-A** (core BUILD) is a later Emma / Matt GO. **D-130-B** (UI +
> Method) is a later Emma / Matt GO that **reads** that tree. The
> **OPS** run of the two is a third. This file is authority; it is
> **not** the A BUILD and **not** the B BUILD.
> **Ruled by:** **Emma/Matt GO Phase 4 RMSD must-hunt, 2026-09-05
> ~20:39 PT** — *"Go phase 4"* — against **vault `D-0043` roadmap
> Phase 4**, quoted **verbatim in §12**, with every clause below bound
> to it.
> ⚠ **Vault `D-0043` is external numbering — NOT a project decision**
> (`D-109` ruling 1 / `F-065`), and **NOT** repo **`### D-043`** (the
> Coverage `fold_status` three-state entry, untouched). Same collision
> the log already disambiguates at D-114 and D-129. The vault lives in
> **Obsidian on the owner's laptop**; no vault file is on disk in this
> repo, and none is waited on.
>
> ⚠ **SINGLE FAILURE MODE: residual RMSD.** The `rmsd_gt_10` class —
> the **whole-overlap** corresponded Cα distance. ⚠ **NOT a linker /
> seam Spec** (D-128's family; **closed** at Phase 5 — D-129). ⚠ **NOT
> a domain-partition Spec** (D-127's family; not re-opened). ⚠ **NOT
> both. NOT dual-mode. NOT a kitchen sink.**
> ⚠ **TWO PARENTS, and only two: 3272** `Q6V0I7` **and 3394**
> `Q8TDW7` (§3) — both still **Phase 4 must-hunt**, and neither is
> `accept-refuse`. No third id joins them.
> ⚠ **This GO is the one `D-129 §6` required.** That section held the
> pair open behind *"explicit Matt GO language"*; the GO arrived, so
> their hunt is now **Spec-governed** rather than unspecced. **D-129 §6
> now carries the matching Phase 4 amendment.** ⚠ **Nothing else in
> D-129 moves:** §2's **eight** are unchanged, §4's disclosure stays
> **standing**, and §7's freeze is **not repealed** — only its own
> *"Phase 4 RMSD only on explicit Matt GO"* clause is **satisfied**.
> ⚠ **The eight stay `accept-refuse`.** **2938, 2939, 3179, 3190,
> 3321, 3368, 3566 + 3432** are **not** re-opened, **not** re-hunted,
> and **not** in this Spec's inventory (D-129 §2 / §3). **Phase 5 is
> not reopened.**
> ⚠ **Both outcomes are pre-registered, before any run: recover with
> honesty OR named refuse after a failed hunt.** **`recovered_of_two`
> = 0 is an ALLOWED outcome** and a valid experimental result (§1b,
> §3, §11) — the D-128 §1b / §3 / §11 pattern applied in advance again.
> ⚠ **The 10.0 Å refuse gate STAYS.** No loosen, no raise, no
> per-parent exception, no named-exclusion, **no threshold
> Spec-as-fix**. A `0 of 2` licenses none of it.
> ⚠ **No trim.** Trim was the **D-126 lie surface** — and 3272 is one
> of the parents where it hid a **28–68 Å** full-overlap gap behind a
> small weighted score (as recorded). ⚠ **No weights-as-fix.** ⚠ **No
> pieces / domain intervals as the fit unit.** ⚠ **No window.** ⚠ **No
> linker-inherit.** ⚠ **No blend.** ⚠ **No linker-v2, no piecewise-v2,
> no RMSD-v2.**
> ⚠ **Seams are NOT solved. This Spec never says solved**, and it never
> says solved **without measurement**.
> ⚠ **Served stays assembler.** No auto-flip on any count; a swap is a
> **Matt GO**. **D-126 remains the best experimental path until proven
> otherwise, and callable.** The **D-127 and D-128 failed rescues stay
> disclosed** — both, unsoftened. ⚠ **No F-004** (D-109 ruling 7).
> ⚠ **Not an ops run. Nothing is re-measured here** — every D-125 /
> D-126 / D-127 / D-128 figure below is quoted **as recorded**.
> ⚠ **No UI / React / `MethodNote.jsx` in this PR.** ⚠ **No
> `hold48_*.py` edit.** ⚠ **No Method file edit** — §7 is the required
> copy as **authority only**. ⚠ **Not F-004 ingest. Not ADC-C. No rent
> / GPU / RunPod / Fly POST.**
> Assembler, D-125 `core/hold48_kabsch.py`, D-126
> `core/hold48_confidence_kabsch.py`, D-127
> `core/hold48_piecewise_kabsch.py` and D-128
> `core/hold48_linker_seam.py` all remain callable and **unedited**.
> D-130-A writes a **sixth sibling tree**; it overwrites none of them.

**Parents:** [`D-129` Spec](SPEC-phase5-named-refuse.md) (§2 / §6 / §7 —
the Phase 4 boundary this GO crosses, and the freeze it does not
repeal) · D-129 `1baf4c0` / #249 · D-129-B `cbcb47d` / #250 · D-129-C
`544e821` / #251 · [`D-128` Spec](SPEC-linker-seam-honesty.md) (§1a
honesty rows / §2 refuse / §11 ops report) · D-128-A `9e65cbf` / #247 ·
D-128-B `cd071d7` / #248 ·
[`D-127` Spec](SPEC-piecewise-domain-kabsch.md) · D-127-A `e49bf34` /
#244 · D-127-B `de9a80e` / #245 (the OPS histogram that names both
Phase 4 parents) ·
[`D-126` Spec](SPEC-overlap-confidence-kabsch.md) · D-126-A `aa8aa02` /
#241 · D-126-B `abbcd00` / #242 ·
[`D-125` Spec](SPEC-kabsch-restitch.md) (**the fit unit this Spec
reuses unchanged**) · D-125-A `26a40a8` / #237 · D-125-B `aa8d3f1` /
#238 · [`D-117`](PLAN-ui-post-wave2-endstate.md) (PLAN / Kabsch park) ·
[`D-118`](README.md) (assembler-not-Kabsch honesty) ·
[`D-120`](README.md) (Phase 2 review of the 27) ·
[`D-121`](method-hold48-tiles.md) (Method: assembler ≠ Kabsch *today*) ·
D-116 `stitch_readiness` · D-111 `winning_tile` / off-block PAE null ·
D-109 ruling 7 (not ranking-eligible) · D-062 / method-note item 7 (the
check is the entry, not the reference) · D-016 (provenance).
**Ship index:** [`decisions.md`](decisions.md).

---

## 1. Goal — certify the floor before claiming a fit

**This Spec does not look for a better transform. It asks whether a
better transform can exist at all, and reports the answer either way.**

Four rigid-body hypotheses have been pre-registered and run against the
model's own coordinates, and each reported **the RMSD it achieved**:

- **D-125** — one unweighted rigid body on the whole overlap.
- **D-126** — the same one body, **weighted** by pLDDT and **trimmed**.
  Its recorded lesson is that a small **weighted** RMSD can hide a large
  **full-overlap** jump — ops jumps **28–68 Å** on **2939 / 3272 /
  3432**, as recorded.
- **D-127** — one rigid body **per UniProt domain**. **PASS 17 / REFUSE
  10 / FAIL 0**, `recovered_of_primary_three` = **0**, give-back **5**
  vs D-125 and **7** vs D-126, as recorded.
- **D-128** — one weighted rigid body in a **±32 aa** window around the
  offending linker, plus the **required** per-path seam honesty
  measurement. **PASS 0 / REFUSE 7 / FAIL 0 / SKIP 0**,
  `repaired_of_seven` = **0**, give-back **5** vs D-125 and **6** vs
  D-126, as recorded.

**Not one of them reported the smallest RMSD any rigid motion could
have achieved.** That number is different, and it is computable
**without fitting anything**.

**The observation this Spec is built on.** A rigid motion preserves
every internal distance of the set it moves. So the disagreement
between the **two overlap copies' own internal Cα distances** is a
property of the two shapes alone — it survives every rotation and
translation, including the best one. It therefore places a **floor**
under the RMSD of **all** rigid transforms at once (§1a proves it), and
the floor is worth exactly one thing:

> **If the floor is already over 10.0 Å, no rigid transform whatsoever
> can pass the gate on that correspondence.** The refusal is
> **certified**, not merely observed.

**Why that is the honest hunt for this class, and a fifth knob is not.**
The family's whole recorded history is that each new knob bought a pass
count somewhere and gave one back somewhere else — D-126's trim hid a
gap, D-127's pieces moved the failure into the linkers, D-128's window
recovered nothing. A fifth knob aimed at the RMSD class would be the
same move a fifth time, and worse, because it would be chosen **after**
seeing which two parents refuse: a threshold-and-hypothesis search
dressed as a hypothesis test. **D-129 §7 froze the family to stop
exactly that, and this Spec does not reopen it.** No new geometry is
introduced anywhere below.

**So the two allowed outcomes are both honest, and both are written
here before any run:**

| Outcome | What it means | Allowed? |
|---|---|---|
| **Recover with honesty** | The **correspondence** was wrong — the wrong Cα paired to the wrong Cα — and residue identity determines the correction uniquely. Re-pair, refit with **D-125's exact fit**, disclose every metric and the identity evidence (§1b, §11). | **Yes** |
| **Named refuse after a failed hunt** | The correspondence is verified and the fit still refuses — with a **certificate** where the floor clears the gate. Record it, name it, stop. | **Yes** (the Phase 3 / Phase 5 pattern) |
| **`recovered_of_two` = 0** | Both parents refuse. | **Yes — pre-registered here, before the run** |
| A gate loosened, a trim added, a blend invented, an RMSD-v2 written | — | **No** (§9) |

**What does not change.** The **served** structure stays the
**assembler** (`core/hold48_stitch.py` `winning_tile`) until a Matt swap
GO. **D-126 remains the best experimental path among the stitch
algorithms tried so far, until proven otherwise, and stays callable** —
it recovered **2 of its primary 5** (parents 3368, 3394; as recorded)
against D-127's **0 of 3** and D-128's **0 of 7**. **Both** failed
rescues stay disclosed. The **eight** stay `accept-refuse` and D-129
§4's disclosure stays **standing**. The **10.0 Å** gate stays.
Off-block PAE stays **null, never 0** (D-111). No atom is invented for
a gap (`UncoveredResidue` still raises). The 27 stay outside F-004
(D-109 ruling 7).

---

## 1a. Residual decomposition (required)

**This section is the part of the Spec that is not optional.** A
D-130-A that writes these rows and recovers **zero** parents has run
this Spec.

### The measurement

For each parent of §3, for each seam, and for **each** path artifact
tree — D-125 `kabsch/{id}/`, D-126 `confidence_kabsch/{id}/`, D-127
`piecewise_kabsch/{id}/`, D-128 `linker_seam/{id}/` and D-130's own
`residual_rmsd/{id}/` — a later D-130-A must record:

| Field | Meaning |
|---|---|
| `path` | which tree the row describes (`kabsch` / `confidence_kabsch` / `piecewise_kabsch` / `linker_seam` / `residual_rmsd`). |
| `n_overlap_ca` | corresponded Cα count on the **full declared overlap**. **No trim, no subset, no window.** |
| `rigid_rmsd_angstrom` | the **full-overlap** Cα RMSD that path **ends** with, after whatever transform it applied. **Null** if that path refused before any transform — null is not `0.0`. |
| `internal_drmsd_angstrom` | the rigid-invariant internal distance RMSD between the two overlap copies (defined below). Computed from coordinates **before any transform**; it does not depend on one. |
| `rmsd_floor_angstrom` | `internal_drmsd_angstrom / 2` — a **proved** lower bound on the RMSD of **every** rigid transform of that correspondence. |
| `residual_class` | `irreducible` / `placement` / `unknown` (below). **Three-valued. Unknown is neither.** |
| `floor_exceeds_gate` | `true` when `rmsd_floor_angstrom > 10.0`; `false` when `≤ 10.0`; **null** when the floor is null. |

**Definitions.** On the corresponded overlap Cα pairs
\((a_i, b_i)_{i=1..n}\), \(n \ge 3\), with \(d^A_{ij} = \lVert a_i -
a_j \rVert\) and \(d^B_{ij} = \lVert b_i - b_j \rVert\):

\[\mathrm{dRMSD} = \sqrt{\tfrac{2}{n(n-1)}\textstyle\sum_{i<j}\bigl(d^A_{ij}-d^B_{ij}\bigr)^2},
\qquad
\mathrm{RMSD}(R,t) = \sqrt{\tfrac{1}{n}\textstyle\sum_i \lVert R a_i + t - b_i\rVert^2}\]

### The floor, and why it holds

**Claim.** For **every** rigid \((R, t)\):
\(\;\mathrm{RMSD}(R,t) \;\ge\; \mathrm{dRMSD}/2\).

**Proof.** Write \(e_i = R a_i + t - b_i\). A rigid motion preserves
internal distances, so \(d^A_{ij} = \lVert (Ra_i + t) - (Ra_j + t)
\rVert\). The triangle inequality then gives \(\lvert d^A_{ij} -
d^B_{ij} \rvert \le \lVert e_i \rVert + \lVert e_j \rVert\), hence
\(\bigl(d^A_{ij}-d^B_{ij}\bigr)^2 \le 2\bigl(\lVert e_i\rVert^2 +
\lVert e_j\rVert^2\bigr)\). Summing over the \(n(n-1)/2\) pairs,
\(\sum_{i<j}\bigl(d^A_{ij}-d^B_{ij}\bigr)^2 \le 2(n-1)\sum_i \lVert
e_i\rVert^2\). Dividing by \(n(n-1)/2\) gives \(\mathrm{dRMSD}^2 \le
\tfrac{4}{n}\sum_i \lVert e_i \rVert^2 = 4\,\mathrm{RMSD}(R,t)^2\). ∎

⚠ **This is mathematics, not a measurement.** It is a proved
inequality about any two corresponded point sets. **No parent's floor
is computed, asserted, or estimated in this Spec PR** (D-016). A later
A BUILD's tests must be able to go red against the identity on
constructed point sets.

### The three-valued class

| `residual_class` | When | What it licenses |
|---|---|---|
| **`irreducible`** | `rmsd_floor_angstrom > 10.0` | **A certified refuse.** No rigid transform can pass the gate on this correspondence — so this is not "our fit was bad," it is "the two tiles disagree about this region's shape." Refuse reason `rmsd_irreducible` (§2). |
| **`placement`** | floor `≤ 10.0` **and** the path's achieved `rigid_rmsd_angstrom > 10.0` | **Only a question, never a promise.** Impossibility was **not** certified; the gate failure is not *forced* by shape. The correspondence audit of §1b may run. |
| **`unknown`** | either input is null (tree absent, refused before transform, `n_overlap_ca < 3`) | **Nothing.** Unknown is **not** irreducible and **not** placement, and it is **never** rendered as a number. |

### ⚠ The floor is one-directional, and reading it backwards is a violation

The bound runs **one way only**, and its constant is **not tight**:

- `floor > 10.0 Å` **proves** the gate is unreachable. **Sufficient.**
- `floor ≤ 10.0 Å` **proves nothing.** It does **not** mean a passing
  fit exists, does **not** predict one, and does **not** make a parent
  "recoverable." It means impossibility was **not certified**.
  **`irreducible` is sufficient and never necessary** — a parent may be
  unfittable without the floor detecting it.

So none of the following may be written, badged, computed, or implied
by any surface, and each is a **Spec violation** (§9):

- "`placement` means this parent can be fixed."
- "The floor is only *x* Å, so the 10.0 Å gate is too strict here."
- a per-parent gate exception, a named-exclusion, or any threshold move
  argued from a floor.
- a count of `placement` parents presented as a recovery forecast.

**The floor's job is to make a refusal defensible, not to make a
recovery plausible.**

### Reading the prior trees is a read

Rows for the D-125 / D-126 / D-127 / D-128 seams are computed by
**reading** those trees and are written **into the D-130 tree** (§5). A
later A BUILD must **not** rewrite, append to, or overwrite
`kabsch/{id}/`, `confidence_kabsch/{id}/`, `piecewise_kabsch/{id}/` or
`linker_seam/{id}/`. If a prior tree is absent, the row is an **honest
absence with a stated reason** — never a zero, never an assumed pass,
and never a number carried over from a different parent or path. Each
row names **how it is known** (`read_from_path_record` /
`measured_from_path_artifacts` / an absence with a reason), the D-128
§1a contract carried forward unchanged.

### Why this is the load-bearing half

D-126 taught that **a pass on a fit statistic is not a held join**, and
it taught it on 3272. D-128 answered that by making the per-seam jump
**required** for every path. §1a is the same discipline pointed one
level deeper: it makes the **unreachable-by-construction** case
measurable, so a later refusal is a statement about the model's
coordinates rather than about our patience — and so no sixth path can
pass by choosing a flattering statistic.

---

## 1b. Correspondence audit — optional scoped recovery (D-130-A)

**The only recovery this Spec permits is one where the previous fits
were solving the wrong pairing.** If the correspondence is right and
the floor is honoured, D-125's fit already achieves the optimum for
that correspondence — so a re-fit on the same pairs would recover
nothing **by construction**, and pretending otherwise would be a knob
in disguise.

**The audit is decided by residue identity, never by RMSD.** That
distinction is the whole difference between fixing an indexing bug and
tuning until the number improves.

Steps:

1. **Gate on §1a.** The audit runs **only** where `residual_class` is
   **`placement`**. An `irreducible` parent refuses
   `rmsd_irreducible` — auditing it could not help, and running the
   audit anyway to see what happens is a search. An `unknown` parent
   refuses `correspondence_unverifiable`.
2. **Audit the declared correspondence against residue identity.** Read
   the residue name and span-relative numbering of every overlap Cα
   from the tile artifacts each path already wrote, and check that the
   pairing the prior paths used maps identical residues to each other.
   Record `correspondence_verified` (bool) and `register_offset_aa`
   (integer; **0** when verified).
3. **A correction must be UNIQUE and identity-determined.** If exactly
   one integer register offset makes the overlap residue identities
   agree, that offset is the correction. If **none** does, or if **more
   than one** does, the audit result is **ambiguous** and the parent
   **refuses** `correspondence_unverifiable`. **Do not** choose among
   candidate offsets by RMSD, by pLDDT, by seam jump, or by which one
   passes. **Do not** scan a window of offsets and keep the best.
4. **Re-pair on the corrected register only.** The corrected
   correspondence is the **full** identity-agreeing overlap. **It is
   not a subset chosen for fit quality** — dropping pairs to improve a
   number is **trim**, and trim is forbidden (§9).
5. **Fit: exactly D-125's fit, unchanged.** **One unweighted,
   untrimmed** Kabsch on the **full** corrected overlap Cα: centroids →
   covariance \(H\) → SVD → rotation \(R\) with \(\det R = +1\)
   correction → translation \(t\). \(\varepsilon\) = **1e-3** is the
   degeneracy floor only. **No weights** (that is D-126). **No trim
   loop** (that is the D-126 lie surface). **No pieces** (D-127). **No
   window** (D-128). **No linker-inherit.** Same adjacency /
   `stitch_readiness` (D-116) / prefer-lower-dups (**3673/3674/3675**;
   spares **3693/3695/3696** unused) / **N-terminal reference** as
   D-125 through D-128.
6. **Apply \(R, t\) to the whole moving tile** — D-125's apply unit. The
   N-terminal tile is not moved. There is no piece list and no window.
7. **Refuse (fail closed).** Overlap Cα count `< 3` →
   `overlap_ca_lt_3`; floor over the gate → `rmsd_irreducible`;
   ambiguous / unverifiable identity → `correspondence_unverifiable`;
   post-fit full-overlap RMSD `> 10.0 Å` → `rmsd_gt_10`; singular /
   degenerate covariance (rank `< 2`) → `singular_covariance`. Full
   table in §2.
8. **On accept**, feed the transformed `TileFold` list into the
   **existing** `winning_tile` / `stitch_pdb` / `stitch_plddt` /
   `stitch_pae` / `write_stitched`. Winner selection stays per-residue
   pLDDT. Off-block PAE stays **null, never 0** (D-111). No atom is
   invented for a gap.
9. **All-or-nothing parent; clear partials.** If **any** seam of the
   parent refuses, parent outcome = refused: clear / do not leave a
   partial `tileN_transformed.pdb` or a D-130-path `stitched.pdb` (same
   fail-closed spirit as D-125 `_clear_success_artifacts` in
   `core/hold48_kabsch.py`). Rows are still recorded.

**Out of v1:** any weighting scheme; any trim; any subset selection;
any second correspondence tried until a parent passes; per-domain
pieces; a window; linker-inherit; a soft invent blend; MD / AF GPU
refine; joint placement. Those are **not a later phase of this Spec** —
they are the frozen family (D-129 §7). Recovering **0 of 2** does
**not** license any of them, a threshold change, or a named-exclusion.

**Cost.** The decomposition is \(O(n^2)\) in the overlap Cα count,
bounded by the hold-48 tile size, and the fit is D-125's. **CPU-side,
zero third-party imports**, the same footprint as D-125-A / D-126-A /
D-127-A / D-128-A. **No rent, no GPU, no RunPod.**

**Disclosure required (anti pass-by-statistic):**

- **Per (path, seam):** the §1a row — `path`, `n_overlap_ca`,
  `rigid_rmsd_angstrom`, `internal_drmsd_angstrom`,
  `rmsd_floor_angstrom`, `residual_class`, `floor_exceeds_gate`, and
  how each is known.
- **Per D-130 seam:** `correspondence_verified`, `register_offset_aa`,
  `identity_evidence` (what made the correction unique — or why none
  was), `n_ca`, post-fit `rmsd_angstrom` (null if refused before RMSD),
  post-fit `max_ca_jump_angstrom` (null if refused before any
  transform), and `refuse_reason`.
- **Per parent:** `residual_class`, whether the audit ran, and
  **`recovered_of_two`** across the pair.

Those metrics do **not** move the 10.0 Å gate. A writes them; UI /
Method (B) later shows them.

A correspondence-corrected Kabsch does not jointly place anything in a
new network forward pass. It does not fill PAE. It does not make the
chain one ESMFold forward pass. It does not enter F-004 (D-109
ruling 7). It does not treat writing this Spec, or naming these two
parents, as a scientific fix. A transformed tile is still that tile's
network output, moved.

---

## 2. Refuse (v1 — 10 Å STAYS — do not raise, do not loosen)

These thresholds are **v1 defaults**. D-130-A tests must be able to go
red against them. They are not a claim that any parent was measured
against them in this PR. **The 10.0 Å gate does not move**, and no
threshold loosens without Matt. D-130 changes *what is measured before
the fit*, not *what counts as a pass*. **It is not a threshold
Spec-as-fix.**

| Condition | Threshold | Effect |
|---|---|---|
| Full-overlap corresponded Cα count | **`< 3`** | **Refuse** (`overlap_ca_lt_3`). Kabsch still needs three corresponding points. |
| `rmsd_floor_angstrom` (§1a) | **`> 10.0 Å`** | **Refuse** (`rmsd_irreducible`). **Certified:** no rigid transform can pass on this correspondence. Record the floor and the dRMSD. |
| Residue-identity audit (§1b step 3) | **none or more than one** offset agrees | **Refuse** (`correspondence_unverifiable`). Ambiguity is a refusal, **not** an invitation to pick by score. |
| Post-fit **full-overlap** RMSD | **`> 10.0 Å`** | **Refuse** (`rmsd_gt_10`). Record the RMSD. Do not invent a "fixed" pose. |
| Covariance of the overlap Cα sets | **singular / degenerate** (rank `< 2`) | **Refuse** (`singular_covariance`). |

Fail closed means: no `tileN_transformed.pdb`, no D-130-path
`stitched.pdb` for that parent, no silent fallback that looks like
success. **All-or-nothing parent refuse.** Rows are still recorded — a
refuse is a **recorded outcome**, not a gap filled with guessed
coordinates and not a parent quietly dropped from the run.

The **assembler** path already on disk (D-118 / D-120) is unchanged, as
are `kabsch/{id}/`, `confidence_kabsch/{id}/`, `piecewise_kabsch/{id}/`
and `linker_seam/{id}/`.

⚠ **`rmsd_irreducible` and `correspondence_unverifiable` are NEW reason
names, not renames.** They are **not** D-127's `linker_jump_gt_10`
(a parent refuse computed after linker inherit across domain pieces)
and **not** D-128's `seam_jump_gt_10` (computed after the ±32 aa window
transform). Different algorithms measuring different things; they must
never be conflated in a report, a UI, or a test. `rmsd_gt_10`,
`overlap_ca_lt_3` and `singular_covariance` are **D-125's names,
carried unchanged**.

⚠ **The D-127 OPS histogram `rmsd_gt_10` ×2 is motivation, not a
threshold.** It explains why the failure mode this Spec hunts is the
whole-overlap residual. It is not a licence to move the gate, and not a
named-exclusion of anyone. A later A BUILD may still refuse both
parents under 10.0 Å. That is fail-closed, **not** "the seam is
solved."

---

## 3. Inventory — the Phase 4 residual-RMSD pair

Primary evaluation inventory is **exactly two** parents: the ids the
Phase 4 GO named, which are the **`rmsd_gt_10`** class of the D-127 OPS
refuse histogram, as recorded (Matt GO via Emma 2026-09-05 at tip
`e49bf34`; carried in `docs/README.md` `#### D-127-B amendment 1`
item 3, `ARCHITECTURE.md` and [`method-hold48-tiles.md`](method-hold48-tiles.md)).
Same closed-out **27** as D-117 / D-118 / D-120 / D-125 / D-126 /
D-127 / D-128 / `WAVE1_WAVE2_STITCHED_PARENT_IDS`. ⚠ **Not re-queried
against Fly.** ⚠ **Not re-measured here.** Do not invent a new science
number. Do not treat naming these two as a fix.

| parent job id | accession | Recorded refuse | Recorded history — why it is in this Spec |
|---|---|---|---|
| **3272** | `Q6V0I7` | D-127 OPS `rmsd_gt_10` | **The hard mismatch.** One of D-126's primary **five** and **not** among the **2** it recovered; named in the recorded D-126 OPS surface as one of the parents where the **full-overlap** jump ran **28–68 Å** while the weighted score looked small (2939 / 3272 / 3432); one of D-127's primary **three**, which recovered **0 of 3**. ⚠ **Not in the D-128 OPS seven** — no linker-window hunt has ever been run against it. |
| **3394** | `Q8TDW7` | D-127 OPS `rmsd_gt_10` | **The give-back.** One of the **2 of 5** D-126 OPS **recovered** (with 3368) — one of only two parents any stitch path has recovered — and D-127 then **gave it back** under `rmsd_gt_10`. ⚠ **Not in the D-128 OPS seven.** A passing rigid fit is **known to have existed** on one path's terms, which makes its refusal the sharper of the two. |

⚠ **Both accessions are on record in this log** (D-127 Spec §3, D-128
Spec §3, D-129 Spec §6) and are named here for that reason only.
**Nobody writes an accession from memory** (D-016), and this Spec adds
none.

⚠ **Every history claim in that table is a read of the record, not a
re-measurement.** That 3272 is in D-126's non-recovered set is derived
from two recorded lists — D-126's primary five (2939, 3272, 3368, 3394,
3432) and its recovered two (3368, 3394). **Checking that two records
agree is not a measurement** and does not upgrade the provenance.

**Explicitly out of the primary inventory:**

| parent job id(s) | Fate | Why it is out of *this* Spec |
|---|---|---|
| **2938, 2939** `Q7Z408`**, 3179, 3190, 3321, 3368** `Q5SZK8`**, 3566** | **`accept-refuse`** (D-129 Phase 5) | The linker / seam class. **Closed to further hunting.** Not success targets, not re-opened, not re-hunted, and **not** a D-130 miss. |
| **3432** `Q8IZF6` | **`accept-refuse`** (signed triage; re-affirmed at D-129 §2) | `no_domain_pieces`. Not a success target; its status is **not re-opened** and not reclassified. |
| IGF2R **3356** | out | A different accession story (cohort OOM vs census tiles); **not** one of the 27 (D-120). The IGF2R seam ~**88.76 Å** is a join-jump disclosure, **not** a Kabsch RMSD and **not** a D-130 metric. ⚠ Not re-measured. |
| the remaining ~18 tileable parents and the 3 mucins | out | Not this Spec. |

- **CLI may also re-run all 27** so accept / refuse counts stay
  comparable to D-125, D-126, D-127 and D-128. The other 25 are not
  excluded from the algorithm; they are **not** the primary evaluation
  set and **not** success targets. Rows for them are **recorded**, and
  a pass among them is **not** a Phase 4 recovery.
- **`recovered_of_two` = 0 is an allowed outcome**, pre-registered
  here **before** any run. A later A BUILD that recovers neither parent
  has still run the Spec — the §1a decomposition is the deliverable.
  Do not loosen the 10.0 Å gate, invent a blend, or add a trim loop to
  force a pass.
- **A named refuse after a failed hunt is a full completion** of this
  Spec, not a shortfall — the Phase 3 / Phase 5 pattern.
- These 27 stay **outside F-004** (D-109 ruling 7).

Do not invent a new science number. Do not treat a named exclusion as
the algorithm.

---

## 4. PLAN pointer

Parent PLAN: [`PLAN-ui-post-wave2-endstate.md`](PLAN-ui-post-wave2-endstate.md)
(**D-117**). §5 was the Kabsch park → **D-125**. Overlap-confidence
follow-on was **D-126**; piecewise / domain-aware was **D-127**;
linker / seam honesty was **D-128**, whose OPS run answered that family
negatively; **D-129** named the eight `accept-refuse` and froze the
family, leaving **Phase 4** as the one class explicitly held open
behind a separate Matt GO. **This Spec is that follow-on `D-NNN`**,
under the GO that arrived. **D-130-A** is the later GO that implements
§1a / §1b / §2 / §3 and §5 as code (a sixth sibling module + CLI). It
does **not** pre-authorise D-130-B UI / Method, an OPS run, rental, a
threshold change, a named-exclusion, a trim loop, a served-path swap, a
reopening of Phase 5, or MD / AF GPU refine. **The plan does not become
a BUILD GO.**

---

## 5. Artifact dirs + provenance (D-130-A writes a *sixth* sibling tree)

Assembler `write_stitched` already writes, beside an ops `out_dir`:
`stitched.pdb`, `stitched_plddt.json`, `stitched_pae.json`, `tileN.pdb`,
`tileN_plddt.json`, `tileN_pae.json`. Those names are the D-118 / D-120
served path.

Already on disk from the earlier paths:

```
<ops out_dir>/kabsch/{parent_job_id}/               # D-125-A
<ops out_dir>/confidence_kabsch/{parent_job_id}/    # D-126-A
<ops out_dir>/piecewise_kabsch/{parent_job_id}/     # D-127-A
<ops out_dir>/linker_seam/{parent_job_id}/          # D-128-A
```

**Do not overwrite** the assembler tree or any of those four until a
later Matt GO names a swap. All five paths stay callable.

D-130-A writes a **sixth sibling tree**, outside the git repo (GUIDE:
do not `git add` `*.pdb` / PAE binaries):

```
<ops out_dir>/residual_rmsd/{parent_job_id}/
  provenance.json
  seams.jsonl               # D-130 audit + fit rows (or refuse)
  residual_decomposition.jsonl   # §1a rows, one per (path, seam)
  tile{n}_transformed.pdb   # only if that tile's inbound seam was accepted
  stitched.pdb              # via existing write_stitched, after transform
  stitched_plddt.json
  stitched_pae.json
```

⚠ **The tree name `residual_rmsd/` and the module name
`core/hold48_residual_rmsd.py` collide with none of `kabsch/`,
`confidence_kabsch/`, `piecewise_kabsch/`, `linker_seam/`,
`hold48_kabsch.py`, `hold48_confidence_kabsch.py`,
`hold48_piecewise_kabsch.py`, `hold48_linker_seam.py` or
`hold48_stitch.py`** — and the persist stem `residual_rmsd/{parent}`
collides with none of `stitched`, `kabsch/{parent}`,
`confidence_kabsch/{parent}`, `piecewise_kabsch/{parent}` or
`linker_seam/{parent}`. A later A BUILD may not reuse an earlier name.

`provenance.json` / each row must make a refuse reconstructible
(D-016):

- `parent_job_id`, chosen tile job ids, windows
- per D-130 seam: `refuse_reason` ∈ {`null`, `overlap_ca_lt_3`,
  `rmsd_irreducible`, `correspondence_unverifiable`, `rmsd_gt_10`,
  `singular_covariance`}
- per D-130 seam: `correspondence_verified`, `register_offset_aa`,
  `identity_evidence`, `n_ca`, post-fit `rmsd_angstrom` (null if
  refused before RMSD), post-fit `max_ca_jump_angstrom` (null if
  refused before any transform)
- `residual_decomposition.jsonl` rows (§1a): `path` ∈ {`kabsch`,
  `confidence_kabsch`, `piecewise_kabsch`, `linker_seam`,
  `residual_rmsd`}, `n_overlap_ca`, `rigid_rmsd_angstrom`,
  `internal_drmsd_angstrom`, `rmsd_floor_angstrom`, `residual_class`,
  `floor_exceeds_gate`, and how each is known; an absent prior tree is
  an **honest absence with a reason**, never a zero
- `algorithm`: `residual_rmsd_decomposition_then_winning_tile`
- `decision`: `D-130`
- accepted seams only: rotation \(R\) (3×3) and translation \(t\) (Å)

A refuse still writes the rows. It does **not** write a transformed
PDB. **All-or-nothing:** if any seam refuses, clear / do not leave
partial `tileN_transformed.pdb` or D-130-path `stitched.pdb`. No
invented coordinates. All five earlier trees stay on disk and callable.

---

## 6. UI path honesty (D-130-B — later, not this PR)

D-118 / D-120 / D-121 already disclose the **assembler** path; D-125-B
names a second, D-126-B a third, D-127-B a fourth and D-128-B a fifth
(one row per `(path, seam)`, never an average). D-129-B added the
Phase 5 fate label. D-130-B is **UI only**, after A writes
`residual_rmsd/`.

When (and only when) D-130-path artifacts are on disk:

- The review card names the D-130 path **as a path**, and carries the
  §1a decomposition: per `(path, seam)`, the achieved RMSD, the
  internal dRMSD, the **floor**, and the three-valued `residual_class`.
  **No average, no per-path score, no "N of M" tally, no best-path
  badge** — the D-128-B rule, carried forward.
- **The floor renders with its direction attached.** A surface that
  shows `rmsd_floor_angstrom` must, in the same place, say that a floor
  **over** the gate proves the gate is unreachable and a floor **under**
  it **proves nothing**. A `placement` badge alone, or a floor shown as
  a "distance to recovery," is a **Spec violation** (§1a, §9).
- Each D-130 seam shows `correspondence_verified`,
  `register_offset_aa`, `identity_evidence`, `n_ca`, post-fit
  `rmsd_angstrom`, post-fit `max_ca_jump_angstrom` and `refuse_reason`.
  Those are **measurements**, not a verdict that the holoprotein is
  aligned. A wrote the fields; B does not invent them. Null renders as
  an **absence, never `0.00 Å`**; **`unknown` is never honest and never
  irreducible.**
- A refused parent is **never** shown with a success PDB presented as
  honest. No "fixed" badge, no "repaired" badge, no silent assembler /
  D-125 / D-126 / D-127 / D-128 PDB presented as a D-130 success.
- **Phase 5 is not touched by this surface.** The **eight** stay
  labelled **named refuse / `accept-refuse`** from D-129-B's registry,
  and D-129 §4's **standing** disclosure (the D-128 OPS **0 of 7** and
  the give-back **5** / **6**) stays exactly as shipped. A D-130 surface
  may not gut, soften, split, or replace it.
- **D-126 stays named the best experimental path so far**, and **both**
  the D-127 and D-128 failed rescues **stay disclosed**. D-130-B must
  not quietly replace them with a fresh-hypothesis story.
- Forbidden language (same park as D-117 §5 / D-125 §6 / D-126 §6 /
  D-127 §6 / D-128 §6): "aligned," "superimposed," "seams solved,"
  "seams fixed," "full-length AF-quality."
- No invented metric. Honest empty when the sibling tree is missing.
- No alignment-box CTA. No F-004 ingest. Default served = **assembler**.

When the `residual_rmsd/` tree is missing, the UI must not imply a
D-130 path exists and must not invent floors / dRMSDs / offsets. That
absence is not a solved seam and not a certified refusal.

---

## 7. Method / owner-facing (D-130-B — later, and mandatory then)

Matt / Emma standing requirement (bound at D-127 §7, kept at D-128 §7
and D-129 §5, kept here): **Method must surface the stitch-path train
honestly**, and a code-only ship is forbidden. **This Spec PR ships no
Method edit** — following the pattern #243 (`00fa76d`), #246
(`2004c5a`) and #249 (`1baf4c0`) actually shipped: the 8th-grade
excerpt lives in the Spec, and
[`method-hold48-tiles.md`](method-hold48-tiles.md) + `MethodNote.jsx`
are edited in the **B** PR. §7 is therefore **authority**, and the copy
below is what a later B must carry.

Same additive pattern as D-121 / D-125-B / D-126-B / D-127-B / D-128-B /
D-129-B: do not gut the assembler Method, do not rewrite #229, and keep
every earlier section — **including** the D-127 and D-128 OPS
disclosures and the D-129-B accept-refuse labels.

**Required Method copy (plain, 8th-grade):**

**Where we are.** To join two overlapping tiles we have now tried
**four** different ways of **moving** one tile onto the other, and we
have written down what each one did. All four move coordinates the
network already produced; none of them is a new fold.

1. **D-125** — one rigid move fitted to the whole overlap.
2. **D-126** — the same one move, but weighted by the model's own
   confidence, and trimmed. Its lesson: a small **weighted** score can
   hide a big **whole-overlap** gap (gaps of **28–68 Å** on 2939 /
   3272 / 3432). **D-126 is still the best of them** — it fixed **2 of
   its 5** target joins (parents 3368, 3394).
3. **D-127** — one rigid move **per protein domain**. **It did not pay
   off:** **0 of 3** target joins fixed, and it **gave back** 5 joins
   D-125 had accepted and 7 that D-126 had.
4. **D-128** — measure every path's gap at every join, then optionally
   try one small rigid move in a **±32 aa** window around the bad
   linker. **The measuring worked. The fixing did not: 0 of 7**, and it
   **gave back** 5 joins from D-125 and 6 from D-126.

**Eight of those joins are closed.** Parents **2938, 2939, 3179, 3190,
3321, 3368, 3566** and **3432** are marked **named refuse /
accept-refuse**: these joins do not hold, we say so, and we have
stopped trying to fix them. That decision does **not** hide the
numbers — the **0 of 7** and the joins D-128 gave back stay on this
page. **Nothing on this page changes that.**

**Two joins were deliberately left open, and this is their turn.**
Parents **3272** and **3394** failed for a **different** reason: not
the floppy linker between domains, but the **whole overlap** — the two
tiles simply do not sit on top of each other. That is the **residual
RMSD** class, and Phase 4 is the hunt for it.

**What we are doing differently, in one idea.** Every attempt so far
reported *how good a fit it managed*. None reported *how good the best
possible fit could ever have been*. It turns out you can work the
second one out **without fitting anything**: sliding and turning a
shape never changes the distances **inside** it, so if the two copies
of the overlap disagree about their **own internal** distances, no
amount of sliding and turning will ever line them up. That
disagreement gives us a **floor** — a number the best possible fit
cannot beat.

**Why the floor is worth having.** If the floor is already **above**
our **10.0 Å** limit, then we have **proved** that no rigid move can
ever pass for that pair of tiles. Saying *"this cannot be fixed by
moving, and here is why"* is a much more useful and much more honest
answer than *"the fifth thing we tried also failed."*

**⚠ The floor only works in one direction.** A floor **above** the
limit proves the join is out of reach. A floor **below** the limit
proves **nothing at all** — it does **not** mean the join can be fixed,
and it is **never** a reason to move the 10.0 Å limit. We will say so
wherever we show the number.

**The one repair we allow.** If the floor does not rule a join out, the
only thing left that could explain a bad fit is that we were comparing
the **wrong residues to each other** — an off-by-some bookkeeping
mistake. So we check the pairing against the actual **residue
identities**, and we only correct it if the residues themselves say so,
never because a correction happens to score better. If the pairing was
already right, there is nothing to fix and we refuse. **We are not
adding a fifth way of moving tiles.**

**What we said in advance.** **Fixing zero of the two is an allowed
outcome**, and we wrote that down **before** running anything. We also
wrote down that a **named refusal after a real hunt** is a complete
answer, not a failure. Saying in advance what will count is the whole
point of writing the plan first.

**What we are not doing.** We are **not** loosening the **10.0 Å**
limit that decides whether a join counts as honest. We are **not**
re-opening the eight closed joins. We are **not** changing which
structure the site serves: the **served** structure is still the
**assembler** (the winner-tile method), as it has been all along.
**We never claim seams solved** — and we never claim anything is solved
without measuring it.

**What Method does not do.** It does not replace the assembler story.
It does not make the long chain one ESMFold pass. It does not fill PAE.
It does not enter F-004. It is not medical advice.

---

## 8. PR split — Spec vs A vs B

| Id | What | This PR? | Gate |
|---|---|---|---|
| **D-130 Spec** | This file + `### D-130` + ship index + `ARCHITECTURE.md` one-liner + PLAN pointer + `Test_Plan.md` T-ids + hermetic docs pin tests + the D-129 Spec §6 Phase 4 cross-link. Includes the §7 Method excerpt as **authority**. | **Yes — this PR.** | Trinity reviewed. **Docs only.** |
| **D-130-A** | Core: §1a residual decomposition rows for every path tree + optional §1b correspondence audit and D-125 refit (no weights, no trim, no pieces, no window) + §2 refuse + call existing `winning_tile`. No UI. Sibling §5 `residual_rmsd/` tree. Primary eval is the two; CLI may run the 27. **CPU, no rent.** | No. Later Emma / Matt GO. | After the Spec is on `main`. **No rent in A.** Not "done" without Method. |
| **D-130-B** | UI path honesty (§6) **and** Method owner markdown + MethodNote additive section (§7). Reads A's sibling tree. No persist rewrite. Default served = assembler. | No. Later Emma / Matt GO. | After A. **Mandatory** before calling D-130 "done." |
| **OPS of the two** | The run of 3272 / 3394, disclosed **as recorded** | No. A third GO, after A and B. | Never solved without measurement. |
| **Phase 5 (the eight)** | 2938, 2939, 3179, 3190, 3321, 3368, 3566 + 3432 | **No. `accept-refuse` and closed** (D-129). | Would need its own new Matt GO. |
| **linker-v2 / piecewise-v2 / RMSD-v2** | — | **No. Frozen** (§9; D-129 §7). | Would need its own new Matt GO. |

**Kaylee does not BUILD** until this Spec is on `main` **and** an Emma /
Matt GO names D-130-A. CloudAgent is already Opus-pinned (**D-0037**);
that pin is a fact of the build lane, not a licence to start A early.

**Out of this Spec PR:** any `hold48_*.py` or core algorithm edit, any
UI / React file, any `MethodNote.jsx` edit, any Method file edit
([`method-hold48-tiles.md`](method-hold48-tiles.md)), any
`scripts/*restitch*.py` edit, a restitch or ops run, an F-004 ingest,
ADC-C / `/adcs` bleed, rent / GPU / RunPod / Fly POST, a threshold
change, a served-path swap, a **linker Spec**, a **domain-partition
Spec**, a **dual-mode Spec**, a **linker-v2 / piecewise-v2 / RMSD-v2**,
re-opening any of the eight, re-measuring the D-125 / D-126 / D-127 /
D-128 figures, inventing an accession, claiming seams solved, or
self-merging.

**Out of the A PR:** any UI, any Method-only claim of done, an ops run,
F-004 ingest, rent / GPU / RunPod / MD / AF refine, replacing
`winning_tile`, overwriting any of the five existing trees, claiming
seams solved, raising **or loosening** the 10.0 Å gate, a trim loop,
weights, per-domain pieces, a window, linker-inherit, or a second
correspondence tried until a parent passes. A does **not** discharge
the Method obligation — B (or a Method-bearing PR) must still ship §7.

---

## 9. Hard stops (Spec + log)

- **No gate loosen.** **10.0 Å stays.** No raise, no per-parent
  exception, no named-exclusion, **no threshold Spec-as-fix**. Writing
  10.0 Å again is not a repair of these two, and **`0 of 2` does not
  license one**.
- **The floor is one-directional.** `floor > 10.0 Å` certifies
  impossibility; `floor ≤ 10.0 Å` **proves nothing** and is **never** a
  recovery forecast or an argument that the gate is too strict.
  **`irreducible` is sufficient and never necessary.** Reading it
  backwards is a **Spec violation**, not an interpretation.
- **No trim, and no trim-as-fix.** Trim was the **D-126 lie surface**:
  it produced a small weighted score while the full overlap ran
  **28–68 Å** — **on 3272 itself**, one of this Spec's two parents. Any
  subset selection that improves a number is trim, whatever it is
  called. Dropping pairs from the corrected correspondence (§1b step 4)
  is trim.
- **No weights-as-fix.** Confidence weighting is D-126's family. §1b's
  fit is **unweighted**.
- **No pieces.** No per-domain pieces, no piece list, **no domain
  intervals as the fit unit**. D-127's family is answered and is not
  re-opened.
- **No window and no linker-inherit.** D-128's family is answered, and
  after Phase 5 it is **closed**.
- **No linker-v2, no piecewise-v2, no RMSD-v2**, and no sixth stitch
  algorithm by default — **not without a new Matt GO** (D-129 §7's
  freeze, unrepealed; the pin's `Stop` clause).
- **No dual-mode Spec.** One failure mode: residual RMSD. A later A
  BUILD that also hunts linker or domain-partition is out of this Spec.
- **No kitchen sink.** Every field in §1a / §1b exists to make a refusal
  or a recovery reconstructible. Nothing else may be added to buy a
  pass.
- **Phase 5 is not reopened.** The **eight** stay `accept-refuse`, are
  **not** this Spec's inventory, are **not** re-hunted, and are **not**
  a D-130 miss. **3432** stays `accept-refuse`.
- **D-129 §4's disclosure stays standing.** The D-128 OPS **0 of 7** and
  the give-back (**5** vs D-125, **6** vs D-126) may not be softened,
  dropped, split apart, or replaced by a D-130 surface.
- **Never solved, and never solved without measurement.** This Spec
  never says solved. Forbidden language stands (D-117 §5 / D-125 §6 /
  D-126 §6 / D-127 §6 / D-128 §6 / D-129 §3).
- **`recovered_of_two` = 0 is allowed**, and **a named refuse after a
  failed hunt is a complete outcome.** Do not loosen a gate or invent a
  blend to force a pass. The §1a decomposition is the deliverable.
- **Failures do not escalate.** On a failed hunt the route is
  **accept-refuse or a dual-path disclose**, **not** another RMSD-v2
  without a **new Matt GO** (the pin's `Stop` clause).
- **No invent.** Fail closed. No transformed PDB on refuse. No invented
  gap atoms. No invented accession. All-or-nothing parent: no partial
  `tileN_transformed.pdb` / D-130 `stitched.pdb` when any seam refuses.
- **No re-measure.** Every D-125 / D-126 / D-127 / D-128 figure here is
  quoted **as recorded**. This Spec runs nothing, computes no parent's
  floor, and re-derives nothing.
- **No PAE zeros.** Off-block PAE stays null, never 0 (D-111). Null
  renders as an absence, **never `0.00 Å`**; **unknown is not honest.**
- **No F-004.** The 27 stay outside `/scorer` (D-109 ruling 7).
- **Served stays assembler.** No auto-flip on any count, pass rate, or
  class label. A swap is a **Matt GO**.
- **D-126 remains the best experimental path until proven otherwise,
  and callable**, and **both** the D-127 and D-128 failed rescues
  **stay disclosed**.
- **Keep prior paths callable.** Assembler + D-125 + D-126 + D-127 +
  D-128 stay callable; **no tree and no module name is overwritten**.
- **No rent in A.** CPU-side, zero third-party imports. No GPU /
  RunPod / MD / AF refine.
- **No code, no UI, no Method edit in this PR.** No `hold48_*.py` edit,
  no `MethodNote.jsx`, no `method-hold48-tiles.md`.
- **No silent code-only.** The Method surface obligation (§7) is
  **mandatory at B**.
- **No self-merge.** Draft PR; **Trinity merges**.

---

## 10. What this file is not

- **Not D-130-A** (core). **Not D-130-B** (UI + Method). **Not the OPS
  run.** This file is the Spec, not a BUILD and not a result.
- **Not a linker / seam Spec** and not a linker-v2. That class is
  D-128's and is **closed** at Phase 5.
- **Not a domain-partition Spec** and not a piecewise-v2. Domain
  intervals are not this Spec's fit unit.
- **Not a dual-mode Spec** and not a kitchen sink. One failure mode.
- **Not an RMSD-v2.** It introduces no new geometry: the only fit it
  permits is **D-125's, unchanged**, on a correspondence corrected by
  **residue identity**.
- **Not a re-opening of the eight** `accept-refuse` parents, and not a
  reclassification of any of them.
- **Not a repeal of D-129 §7's freeze.** Only the pin's own *"Phase 4
  RMSD only on explicit Matt GO"* clause is **satisfied** by the GO
  that authorises this file; every other freeze clause stands.
- **Not a retraction** of the D-127 OPS disclosure, of the D-128 OPS
  rollup, of D-129 §4's standing obligation, or of D-126's standing as
  the best experimental path so far.
- **Not a claim that seams are solved**, aligned, or that the chain is
  one forward pass — and **not a claim of anything without
  measurement**.
- **Not a threshold change** (up **or** down) and not a
  named-exclusion.
- **Not a served-path swap** and not an auto-flip.
- **Not a measurement.** No parent's floor, dRMSD, correspondence or
  RMSD is computed, asserted, or estimated here. The **inequality** of
  §1a is proved mathematics, not a result about any parent.
- **Not an edit** of `core/hold48_kabsch.py`,
  `core/hold48_confidence_kabsch.py`,
  `core/hold48_piecewise_kabsch.py`, `core/hold48_linker_seam.py`, or
  `core/hold48_stitch.py`.
- **Not a Method file edit** and not a `MethodNote.jsx` edit — §7 is
  required copy as **authority only**.
- **Not an ops run**, not a restitch of the 27, not a Fly re-query.
- **Not ADC-C** (D-124). Not ranking ingest. Not F-004.
- **Not a repair of the `D-` next-free pointer.**
- **Not a CI assert against live ops** — §11's fields are a required
  **report** field set, not a gate test.

---

## 11. Ops success report (required fields; not a CI assert)

When a later D-130-A (or ops) run covers the two — and, if run, the
27 — the **ops success report** MUST include the §1a decomposition rows
and confusion vs D-125 **and** D-126 **and** D-127 **and** D-128. This
is documentation of required report fields. It is **not** a CI assert
against live ops and **not** a measurement in this Spec PR.

Required fields:

| Field | Meaning |
|---|---|
| `n_overlap_pairs_measured` | `(path, seam)` pairs with a §1a decomposition row written |
| `n_irreducible` | rows with `rmsd_floor_angstrom > 10.0 Å` — **certified** unreachable |
| `n_placement` | rows with floor `≤ 10.0 Å` and achieved RMSD `> 10.0 Å`. ⚠ **Not a recovery forecast** |
| `n_residual_unknown` | rows whose floor or achieved RMSD is **null** (tree absent / refused before transform) — unknown is neither irreducible nor placement |
| `n_correspondence_audited` | parents where the §1b identity audit ran |
| `n_correspondence_corrected` | parents where identity determined a **unique** non-zero register offset |
| `n_correspondence_unverifiable` | parents where **no** or **more than one** offset agreed — an ambiguity, refused |
| `recovered_of_two` | 0..2; **0 is an allowed outcome**, pre-registered |
| `n_d125_pass_d130_refuse` | D-125 PASS parents that D-130 refuses |
| `n_d126_pass_d130_refuse` | D-126 PASS parents that D-130 refuses |
| `n_d127_pass_d130_refuse` | D-127 PASS parents that D-130 refuses |
| `n_d128_pass_d130_refuse` | D-128 PASS parents that D-130 refuses |
| `n_d126_recovered_d130_refuse` | of the **2** D-126 recovered (3368, 3394), how many D-130 refuses. ⚠ **3394 is in this Spec's inventory**, so this count is the one most likely to embarrass the run — which is why it is named |

A non-zero `n_d125_pass_d130_refuse`, `n_d126_pass_d130_refuse`,
`n_d127_pass_d130_refuse` or `n_d128_pass_d130_refuse` is a **named
finding**, not silent success. **Do not bury a drop inside an overall
accept count** — the mistake the D-127 OPS disclosure was written to
avoid and the D-128 disclosure repeated on purpose. Recovering
**0 of 2** is a valid experimental result; **do not** loosen the 10.0 Å
gate or invent a blend to force a pass. And where the decomposition
certifies a parent `irreducible`, the report says so plainly —
**including that the certificate is a refusal, not a fix.**

⚠ **The report must state which figures were measured by that run and
which are quoted as recorded from an earlier one** (D-016). A D-130 run
measures D-130's rows; it does **not** re-measure D-125 / D-126 /
D-127 / D-128 OPS.

---

## 12. The Phase 4 pin, verbatim

Reproduced **verbatim** so every clause above can be checked against the
artefact rather than against a paraphrase of it (D-016). Supplied by
Emma with the GO.
⚠ **Vault `D-0043` is external numbering, not a project decision**, and
**not** repo `### D-043`. ⚠ **Not re-measured here.**

**Cite as:** `D-0043 roadmap Phase 4 — Emma/Matt GO 2026-09-05 ~20:39 PT`.

```text
# Phase 4 RMSD must-hunt — GO (D-0043)
Status: Emma/Matt GO 2026-09-05 ~20:39 PT — "Go phase 4"
Scope:
- Parents: 3272, 3394 (Phase 2 triage: residual RMSD must-hunt)
- Mode: residual RMSD only — never dual with linker/domain-partition
- Tip base: main (hygiene #251 landed as 544e821)
Notes:
- 3272: hard mismatch; not in D-128 OPS seven
- 3394: D-126 recover gave-back; not hunted in D-128
- Allowed outcomes: recover with honesty OR named refuse after failed hunt (Phase 3/5 pattern)
Freeze: served=assembler; gate 10Å (no loosen); D-126 best experimental callable; no linker-v2; no F-004 / no auto-flip; no kitchen-sink Spec
Train: Trinity Spec → Kaylee A then B → OPS of the two → Method discloses as-recorded; never solved without measurement
Stop: Failures → accept-refuse or dual-path disclose — not another RMSD-v2 without new Matt GO
```

**Where the pin lands in this Spec:**

| Pin clause | Section |
|---|---|
| `Parents: 3272, 3394 (Phase 2 triage: residual RMSD must-hunt)` | §3 (the inventory, exactly two) |
| `Mode: residual RMSD only — never dual with linker/domain-partition` | §1 (goal), §9 (no dual-mode), §10 |
| `Tip base: main (hygiene #251 landed as 544e821)` | the log's Provenance — ⚠ **confirmed against `origin/main` before citing**, not taken from the pin |
| `3272: hard mismatch; not in D-128 OPS seven` | §3 (row), §1 |
| `3394: D-126 recover gave-back; not hunted in D-128` | §3 (row), §11 (`n_d126_recovered_d130_refuse`) |
| `Allowed outcomes: recover with honesty OR named refuse after failed hunt` | §1 (the outcome table), §3, §9, §11 |
| `Freeze` (six clauses) | §9, and D-129 §7 unrepealed |
| `Train: Trinity Spec → Kaylee A then B → OPS of the two` | §8 |
| `Method discloses as-recorded; never solved without measurement` | §7, §9, §11 |
| `Stop: … accept-refuse or dual-path disclose — not another RMSD-v2 without new Matt GO` | §9 |

**The pin's sharpest clause is `no kitchen-sink Spec`**, and it is the
one a reader should check this file against hardest. Four algorithm
families are now on disk, each with its own knobs, and the cheapest way
to look busy on Phase 4 would be to combine them. This Spec instead
**removes** a degree of freedom: it adds **no new fit**, reuses
**D-125's**, and spends its novelty on a quantity — the floor — whose
whole purpose is to tell us when to **stop**.
