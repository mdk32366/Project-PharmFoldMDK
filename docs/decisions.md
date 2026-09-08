# Decision ship index

> **This is not the living log.** Authoritative `### D-NNN` entries live in
> [`README.md`](README.md). Write new decisions there first (append-at-top). This
> file is a thin index of which id **ships** which work, so a PR or review cannot
> treat a PLAN id as a BUILD GO.

## Active ship — D-130-A (Phase 4 residual-RMSD core BUILD)

- **D-130-A ships the Phase 4 residual-RMSD core BUILD** (**this PR**, off
  `854c2ab`) — `core/hold48_residual_rmsd.py` +
  `scripts/residual_rmsd_restitch.py`, under the **Emma BUILD GO Phase 4
  residual RMSD 2026-09-06** (Matt via Emma; the **#252 merge is the GO**,
  and no second GO is waited on). It implements D-130 Spec §1a / §1b / §2 /
  §3 / §5 / §11 as a **sixth sibling path**.
  ⚠ **Core only.** **D-130-B** (UI path honesty + the **mandatory** Spec §7
  Method addendum) is a **later PR after A is on `main`**, and it needs its
  own GO. **A does not discharge the Method obligation**, so D-130 is not
  "done" here.
  ⚠ **§1a is the deliverable.** Per seam, per path (`kabsch` /
  `confidence_kabsch` / `piecewise_kabsch` / `linker_seam` /
  `residual_rmsd`), a row records `n_overlap_ca`, the achieved
  **full-overlap** `rigid_rmsd_angstrom`, the rigid-invariant
  `internal_drmsd_angstrom`, the **proved floor**
  `rmsd_floor_angstrom = dRMSD / 2`, the three-valued `residual_class` and
  `floor_exceeds_gate` — plus **how each is known**, per field.
  ⚠ **A prior path's recorded `rmsd_angstrom` is NEVER copied into that
  column**: only D-125's is a full-overlap unweighted number, so the achieved
  RMSD is **measured** from each path's own artifacts and an absent tree is an
  **honest absence with a reason** (never a zero, never an assumed pass).
  ⚠ **The floor is measured once per seam from the PRE-transform input
  tiles** — D-127 and D-128 do not move a tile rigidly, so measuring off their
  outputs would make a path-independent quantity look path-dependent.
  ⚠ **`irreducible` is evaluated before `unknown`** — the Spec's table leaves
  the precedence open, and §2 refuses on the floor *before* any fit, so the
  other order would make the certificate unreachable.
  ⚠ **§1b is an audit, not a search.** It runs **only** on a `placement`
  seam; a correction is accepted **only** when exactly one integer register
  offset makes every corrected pair's **residue identities** agree; none or
  more than one refuses `correspondence_unverifiable`; a pairing that was
  already right is **not** refitted. The fit is **D-125's, imported
  unchanged** — unweighted, untrimmed, full corrected overlap, whole moving
  tile → existing `winning_tile`. **No trim, no weights, no pieces, no
  window, no linker-inherit, no blend, no RMSD-v2.**
  ⚠ **Refuse names:** `overlap_ca_lt_3` / `rmsd_gt_10` /
  `singular_covariance` are **D-125's, unchanged**; `rmsd_irreducible` and
  `correspondence_unverifiable` are **D-130's own** and are never conflated
  with D-127's `linker_jump_gt_10` or D-128's `seam_jump_gt_10`. Fail closed,
  **all-or-nothing parent**, and a refuse clears any earlier success artifact.
  ⚠ **Sixth tree `residual_rmsd/{parent}/`**, overwriting none of the five;
  prior trees are opened **read-only** and stay byte-identical.
  ⚠ **`recovered_of_two` = 0 stays a pre-registered ALLOWED outcome**, and an
  accept with **no** register correction is **not** a recovery — it is
  D-125's result.
  ⚠ **Phase 5 is not reopened:** the **eight** stay **`accept-refuse`**, may
  be **recorded** by a CLI run of the 27, and are **never** success targets or
  a D-130 miss; D-129 §4's **standing** disclosure stays **ungutted**.
  ⚠ **10.0 Å stays; served stays assembler; no auto-flip; no F-004; D-126
  remains best experimental and callable; both failed rescues stay
  disclosed.** ⚠ **Never solved — and never solved without measurement.**
  ⚠ **No `hold48_*.py` edit** (five modules sha256-pinned), **no UI, no
  Method file edit, no ops run, no re-measurement, no Fly / RunPod / rent.**
  Guarded by `tests/test_d130_residual_rmsd.py` (hermetic, stdlib;
  **T-1200**–**T-1209**). Draft PR; **no self-merge**; **Trinity merges**.
  Full entry: `### D-130-A` in [`README.md`](README.md).
- **D-130 already shipped the Phase 4 residual-RMSD hunt Spec** on `main`
  (`854c2ab` / #252) — [`SPEC-residual-rmsd-hunt.md`](SPEC-residual-rmsd-hunt.md),
  under the **Emma/Matt GO Phase 4 RMSD 2026-09-05 ~20:39 PT**
  (*"Go phase 4"*) that **D-129 §6 required** before either parent could
  move. ⚠ **Algorithm authority for D-130-A** — that Spec PR was
  **docs only**.
  ⚠ **One failure mode: residual RMSD** (the `rmsd_gt_10` whole-overlap
  class). ⚠ **Two parents only: 3272** `Q6V0I7` **and 3394** `Q8TDW7`,
  both **Phase 4 must-hunt** and both **absent from the D-128 OPS
  seven**. ⚠ **NOT a linker Spec, NOT a domain-partition Spec, NOT
  both, NOT a kitchen sink.**
  **§1a (required)** decomposes the residual: per `(path, seam)` it
  records the achieved full-overlap RMSD **beside** the
  rigid-invariant internal **dRMSD** and the **proved floor**
  `dRMSD / 2` under *every* rigid transform, classing each row
  `irreducible` / `placement` / `unknown`.
  ⚠ **The floor is one-directional:** above **10.0 Å** it **certifies**
  that no rigid move can pass; below it, it **proves nothing** — never
  a recovery forecast and never an argument to loosen a gate. Reading
  it backwards is a **Spec violation**.
  **§1b (optional)** is a **residue-identity correspondence audit**
  followed by **D-125's fit unchanged** (unweighted, untrimmed, full
  overlap) — a correction must be **unique and identity-determined**,
  never chosen by score. ⚠ **No trim** (the **D-126 lie surface**,
  which hid a **28–68 Å** gap on **3272** itself), **no weights, no
  pieces, no window, no linker-inherit, no blend.**
  ⚠ **Pre-registered, before any run: `recovered_of_two` = 0 is an
  ALLOWED outcome**, and a **named refuse after a failed hunt** is a
  complete outcome (the Phase 3 / Phase 5 pattern).
  Sixth sibling tree `residual_rmsd/{parent}/` +
  `core/hold48_residual_rmsd.py`, **colliding with no earlier tree or
  module**.
  ⚠ **Phase 5 is NOT reopened:** the **eight** stay **`accept-refuse`**,
  **3432** included, and D-129 §4's **standing** D-128 OPS disclosure
  (**0 of 7** with the give-back **5** / **6**) stays **ungutted**.
  ⚠ **D-129 §7's freeze is not repealed** — only its own *"Phase 4 RMSD
  only on explicit Matt GO"* clause is **satisfied**. **10.0 Å stays;
  served stays assembler; no auto-flip; no F-004; D-126 remains best
  experimental and callable; both failed rescues stay disclosed.**
  ⚠ **Never solved — and never solved without measurement.**
  ⚠ **Docs only: no `hold48_*.py` edit** (five modules sha256-pinned),
  **no UI / React / `MethodNote.jsx`, no Method file edit** (§7 carries
  the 8th-grade excerpt as **authority only**, the #243 / #246 / #249
  pattern), **no ops run, no re-measurement, no Fly / RunPod / rent, no
  F-004.** Guarded by `tests/test_d130_residual_rmsd_spec.py`
  (hermetic, stdlib; **T-1191**–**T-1199**), which reddens if the
  inventory bleeds into the linker or domain classes or if the gate
  loosens. ⚠ **That Spec PR pre-authorised neither A nor B** — each
  needed its own Emma / Matt GO. **A's arrived** (2026-09-06, above);
  **B's has not**, and the **OPS** run of the two is a third. Full entry:
  `### D-130` in [`README.md`](README.md).
- **D-129-C already shipped the `must-hunt` supersession hygiene patch
  on the LIVE surfaces** on `main` (`544e821` / #251) — **copy and one
  test only**,
  under the **Emma GO 2026-09-06** (*"hygiene patch ONLY"*). `### D-129-B`
  corrected the superseded `must-hunt` wording **in place**, but only on
  the narrative sentence: the **MANDATORY §7 provenance inject** two
  sentences above it still read *"a D-128 OPS restitch of the must-hunt
  **seven** at tip `9e65cbf`"* on
  [`method-hold48-tiles.md`](method-hold48-tiles.md) and on
  `MethodNote.jsx`, with the supersession four lines away in the **next
  paragraph**. A qualifier in the neighbourhood is not qualification of
  the claim — **D-062's shape one size down**.
  The rule now enforced: on a **live** surface, every occurrence of
  `must-hunt` is **Phase-4-scoped**, **a negation**, or
  **supersession-carrying**, and the qualifier is in **the same sentence
  as the occurrence** — adjacency does not count.
  **Twelve** bare occurrences at `cbcb47d` were qualified by **adding** a
  clause: 2 on the Method surfaces, 4 in
  [`../ARCHITECTURE.md`](../ARCHITECTURE.md), 2 in the **living header**
  of [`README.md`](README.md), 3 here, and 1 in
  [`PLAN-ui-post-wave2-endstate.md`](PLAN-ui-post-wave2-endstate.md).
  Guarded by `tests/test_d129_c_must_hunt_supersession.py` (hermetic,
  stdlib), which also re-pins that the rule was **not** satisfied by
  deletion.
  ⚠ **Phase 5 is NOT reopened.** No label inventory is re-taken, no fate
  moves, no id joins or leaves the **eight**, and no Spec clause is
  re-argued. ⚠ **Phase 4 is NOT touched:** **3272 / 3394** stay **Phase 4
  must-hunt** — one of the three qualified forms — and their wording is
  left exactly as it was. ⚠ **Nothing is gutted:** the **0 of 7**, the
  give-back (**5** / **6**), *"bury a drop under a pre-registration"*,
  the never-solved refusals and the accept-refuse copy all stay.
  ⚠ **No geometry, no threshold, no registry field, no route, no payload
  key, no served byte** — `core/hold48_*.py`,
  `app/phase5_named_refuse.py` and `app/linker_seam_path_read.py` are all
  **sha256-pinned and untouched**. ⚠ **No linker-v2, no ops run, no
  re-measurement, no Fly / RunPod / rent, no F-004.** Draft PR; **no
  self-merge**; **Trinity merges**. Full entry: `### D-129-C` in
  [`README.md`](README.md).
- **D-129-B already shipped the Phase 5 named-refuse LABELS on Method +
  UI** on `main` (`cbcb47d` / #250) — the **§3 re-label** that
  `### D-129` left **owed**,
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
  both failed rescues stay disclosed. Never solved.** ⚠ **It corrected
  the superseded `must-hunt` wording in place on the narrative sentence
  and not on the §7 provenance inject above it** — the hole `D-129-C`
  closes. Full entry: `### D-129-B` in [`README.md`](README.md).
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
  **seven** — ⚠ **`must-hunt` is what they were called when that run was
  chosen; the Phase 5 sign has since superseded that name (D-129 /
  D-129-B)** — at tip `9e65cbf`, out_root `linker_seam_ops_2026-09-05`;
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
  signed must-hunt linker parents (⚠ **`must-hunt` is what they were
  called then; the Phase 5 sign has since superseded that name —
  D-129 / D-129-B**); the CLI still runs the 27, and
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
  3566** — the D-127 OPS `linker_jump_gt_10` class, as recorded; ⚠
  **`must-hunt` is what they were called when D-128 was written, and
  the Phase 5 sign has since superseded that name — D-129 / D-129-B**).
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

Full entries: [`README.md` § D-130](README.md#d-130--phase-4-residual-rmsd-hunt-certify-the-floor-before-claiming-a-fit--3272--3394-only-recover-with-honesty-or-refuse-by-name-docs-only),
[`README.md` § D-129](README.md#d-129--phase-5-named-refuse-the-eight-linker--seam-parents-are-accept-refuse-the-d-128-rescues-0-of-7-stays-disclosed-and-the-stitch-family-freezes-docs-only),
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
Spec: [`SPEC-residual-rmsd-hunt.md`](SPEC-residual-rmsd-hunt.md)
(D-130) · [`SPEC-phase5-named-refuse.md`](SPEC-phase5-named-refuse.md)
(D-129) · [`SPEC-linker-seam-honesty.md`](SPEC-linker-seam-honesty.md)
(D-128) · [`SPEC-piecewise-domain-kabsch.md`](SPEC-piecewise-domain-kabsch.md)
(D-127).

## Nearby ids (do not conflate)

| Id | Role | Ships? |
| --- | --- | --- |
| **D-140** | **ADC Pipeline `cancer_type` + `description` fill** — the Spec **D-136 decision 8** said it was waiting for. Each of the 10 pipeline rows gains `cancer_type` (a **list**, **`reviewed` only**), `conditions_verbatim` (the registry's Conditions as returned, `official`, or the row's own citation quoted whole, `reviewed`) and `description` (`maker — one line`, `reviewed`), plus a **third** header date `conditions_reviewed_as_of` and a `registry_artifact` pointer. ⚠⚠ Every token must be a **literal substring of that row's own stored text** or `load_pipeline` raises. ⚠⚠ **The authority is ClinicalTrials.gov, and an FDA label authority is DISQUALIFYING here** — these agents are not approved. ⚠ No HPA / staining / census source, ever (D-093). ⚠ **Pipeline shelf only**; `adcs.v1.json` is not touched and `label_indications_verbatim` is still refused on a pipeline row. No new route; no promotion, no invented NCT, no ranking / F-004 / ops | **Yes — this PR.** Catalog + validator + Pipeline index columns + pipeline baseball card + dated offline registry artefact + tests. **`cancer_type` 5 of 10** sourced (14 tokens) / **5** named absences; **`description` 4 of 10** sourced / **6** named absences. **Amends D-136 decision 8** (recorded in D-136's own entry). ⚠ **Shipped as `D-139` and renumbered.** It and the served-path flip were cut from the same `dd06e9c`, each read `gh pr list --state open`, each found no `D-1NN` spender, and each wrote `### D-139` — an open-PR check cannot see a branch that is still local. The served-path work merged first (`1e9777c`) and assigned this one **D-140** in its commit message. The id guards carry **both** ids with **both** named assertions, widened by enumeration and never by a `>=`; that enumeration is what caught the duplicate. Draft; **Trinity merges**. |
| **D-136** | **ADC Approved `cancer_type` fill** — D-122 decision 3's *"later GO that adds a reviewed indication envelope"*. Each of the 15 approved rows gains `cancer_type` (a **list** of tumour types, `reviewed`) **and** `label_indications_verbatim` (FDA SPL §1 text as returned, `official`) from openFDA `label.json`, plus a **third** header date `indications_reviewed_as_of`. ⚠⚠ Every token must be a **literal substring of that row's own stored label text** or `load_catalog` raises — the invented-string guard. ⚠ No HPA / staining / census source, ever (D-093). ⚠ **Approved shelf only**; the pipeline schema admits no indication. No new route; no ranking / F-004 / ops | **Yes — this PR.** Catalog + validator + `/adcs` index + baseball card + tests. **15 of 15** rows filled, **0** named absences. Does not amend D-119 approval identity, the antigen confidences, or D-122's default sort. Draft; **Trinity merges**. ⚠ **D-135 is Kaylee's in-flight Coverage dual-pop work and is not in this diff** — whichever lands second widens the `next_free_decision_id` guards in `tests/test_d129_*` / `tests/test_d130_*`. |
| **D-130 Spec** | **Phase 4 residual-RMSD hunt** Spec (docs only) — **algorithm authority**, one failure mode (`rmsd_gt_10`, whole overlap), two parents (**3272** `Q6V0I7` / **3394** `Q8TDW7`). §1a's required decomposition puts the **proved floor** `dRMSD / 2` beside every path's achieved RMSD and classes it `irreducible` / `placement` / `unknown`; the floor is **one-directional** and never an argument to loosen a gate. §1b's optional recovery is a **residue-identity** correspondence audit plus **D-125's fit unchanged** — **no trim, no weights, no pieces, no window, no linker-inherit**. **`recovered_of_two` = 0 is pre-registered as allowed.** The **eight** stay `accept-refuse` and Phase 5 is **not** reopened; 10.0 Å stays; served = assembler | Already shipped on `main` (#252 / `854c2ab`). Docs only there; no `hold48_*.py` edit (five modules sha256-pinned), no UI, no Method file edit, no ops run. |
| **D-130-A** | Core BUILD (§1a decomposition rows for every path tree + optional §1b correspondence audit and D-125 refit → `winning_tile`; sixth sibling `residual_rmsd/`; CPU, no rent) | **Yes — this PR.** Sixth sibling module + CLI; no `hold48_*.py` edit (five sha256-pinned), no UI, no Method file edit, no ops run. It does **not** discharge the mandatory Spec §7 Method obligation — that is B's. Draft; **Trinity merges**. |
| **D-130-B** | UI path honesty + **mandatory Method addendum** (reads `residual_rmsd/`; the floor never rendered without its direction) | No. **Later Emma / Matt GO**, after A. The **OPS** run of the two is a third GO. |
| **D-129 Spec** | **Phase 5 named-refuse** Spec (docs only) — **labels, not algorithms**. The **eight** parents **2938 / 2939 / 3179 / 3190 / 3321 / 3368 / 3566 + 3432** are **`accept-refuse`**; a surface labels them **named refuse**, never **open must-hunt** / **solved** / **a D-128 miss**. The D-128 OPS **0 of 7** + confusion (**5** vs D-125, **6** vs D-126) stays a **mandatory, standing** disclosure — **already discharged** by D-128-B (`cd071d7` / #248) and **not to be softened or dropped**. **3272 / 3394 stay Phase 4 must-hunt** (separate Matt GO). **No linker-v2**; 10.0 Å stays; served = assembler | Already shipped on `main` (#249 / `1baf4c0`). Docs only there; the **§3 re-label** it left owed shipped at **D-129-B**. ⚠ Its **§6** now carries the **D-130 Phase 4 cross-link**: the separate Matt GO **arrived**, so the pair's hunt is **Spec-governed** — still **not** `accept-refuse`, and §4 / §7 stand. |
| **D-129-B** | **Phase 5 named-refuse LABELS** — the §3 re-label onto the owner Method, `/method`, and the review card, from one signed fate registry (`app/phase5_named_refuse.py` → `assembly_review.phase5_fate`). The **eight** are **named refuse / `accept-refuse`**; the block is **constructed carrying** the D-128 OPS **0 of 7** and the give-back (**5** / **6**), so the label cannot ship without the numbers. **3272 / 3394** render an **open** Phase 4 fate; **3432** is carried, not re-ruled | Already shipped on `main` (#250 / `cbcb47d`). Labels only; no `hold48_*.py` edit (sha256-pinned), no threshold, no artifact tree, no served byte, no ops run. Its hygiene gap on the retired name was closed at **D-129-C** (#251 / `544e821`). |
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
