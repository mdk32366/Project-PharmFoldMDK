# SPEC — Phase 5 named-refuse (D-129)

> **COMMITTED to `docs/` as the Phase 5 named-refuse Spec. CITED BY the
> log, not restated as authority — where this file and `docs/README.md`
> differ, THE LOG GOVERNS.** Confirm the `### D-129` header exists
> before citing.
>
> **Date:** 2026-09-05 · **Status:** Spec (labelling authority).
> **Ruled by:** **`D-0043 Phase 5 named-refuse`, SIGNED 2026-09-05
> ~17:58 PT** — *"Matt: Sign Phase 5 as drafted. Architect support on
> file."* Routed via Emma, who confirmed the vault pin matches the
> Architect brief. **The full SIGNED source is quoted verbatim in §11**,
> and every clause below is bound to it.
> ⚠ **Vault `D-0043` is external numbering — NOT a project decision**
> (`D-109` ruling 1 / `F-065`), and **NOT** repo **`### D-043`** (the
> Coverage `fold_status` three-state entry, untouched). Same collision
> the log already disambiguates for vault `D-0036` vs `### D-036`
> (D-114). The vault lives in **Obsidian on the owner's laptop**; no
> vault file is on disk in this repo, and none is waited on.
>
> ⚠ **This Spec's authority is over LABELS, not over algorithms.** It
> governs what a surface may **call** a set of already-measured
> refusals. It specifies **no** geometry, **no** threshold, **no**
> artifact-tree change, and **no** new code path.
> ⚠ **Eight parents are `accept-refuse`:** **2938, 2939, 3179, 3190,
> 3321, 3368, 3566** (the D-128 linker seven) **+ 3432** (already
> accept-refuse under signed triage — re-affirmed, not newly ruled).
> ⚠ **`accept-refuse` is the recorded honest outcome of a refusal.**
> The join is **not held**, we **say** it is not held, and we **stop
> hunting it**. It is **not** a success, **not** a repair, and **not** a
> miss to chase with another stitch algorithm.
> ⚠ **`accept-refuse` ≠ Method silence.** **D-128-B** (`cd071d7` / #248)
> **already discloses** the D-128 OPS rollup — **0 of 7** repaired and
> the named give-back (**5** vs D-125, **6** vs D-126) — on the Method
> surface. This Spec makes that disclosure **STANDING**: it may never be
> softened, dropped, or split apart, and any surface that carries the
> §3 label must carry it too (§4). Labelling a refusal as accepted is
> **not** licence to bury it.
> ⚠ **One piece of B-side work is still OWED.** The Method D-128-B
> shipped still calls the seven **`must-hunt`** — true when it was
> written, superseded by this sign. Re-labelling them **named refuse /
> `accept-refuse`** is a later Method / UI PR and is **not** in this
> docs Spec PR (§5, §8).
> ⚠ **Seams are NOT solved. This Spec never says solved.** Accepting a
> refusal retires the **hunt**, not the **record**.
> ⚠ **3272 / 3394 remain Phase 4 must-hunt** (`rmsd_gt_10` class) and
> move only on a **separate Matt GO**. ⚠ **No RMSD Spec bleed** — this
> file does not spec, scope, or schedule Phase 4 (§6).
> ⚠⚠ **PHASE 4 (D-130): that separate Matt GO has ARRIVED**
> (**Emma/Matt GO Phase 4 RMSD 2026-09-05 ~20:39 PT**, *"Go phase 4"*),
> so the pair's hunt is now **Spec-governed** by
> [`SPEC-residual-rmsd-hunt.md`](SPEC-residual-rmsd-hunt.md)
> (**D-130**). Read §6's **Phase 4 amendment** before treating either
> parent's fate as settled. ⚠ **They are still NOT `accept-refuse`**,
> the §2 **eight** are **unchanged**, §4's disclosure stays
> **standing**, and §7's freeze is **not repealed** — only its *"Phase 4
> RMSD only on explicit Matt GO"* clause is **satisfied**.
> ⚠ **NO linker-v2.** The stitch-algorithm family **freezes**: no
> linker-v2, no piecewise-v3, no new decomposition, no second window
> size, no restitch (§7).
> ⚠ **The 10.0 Å refuse gate STAYS** and does not loosen. **W = 32** and
> **ε = 1e-3** stay. No per-parent exception, no named-exclusion.
> ⚠ **Served stays assembler.** **D-126 remains the best experimental
> path until proven otherwise.** The **D-127 and D-128 failed rescues
> stay disclosed** — both, unsoftened.
> ⚠ **Not D-128-B** (the UI / Method labelling BUILD — later Emma GO).
> ⚠ **No UI / React / `MethodNote.jsx` in this PR.** ⚠ **No
> `hold48_*.py` edit.** ⚠ **No Method file edit** — §5 is the required
> copy as **authority only**.
> ⚠ **Not an ops run. Nothing is re-measured here** — the D-128 OPS
> figures are quoted **as recorded**.
> ⚠ **Not F-004 ingest.** ⚠ **Not ADC-C.** ⚠ **No rent / GPU / RunPod /
> Fly POST.** ⚠ **Does not merge D-128-B.**
> Assembler, D-125 `core/hold48_kabsch.py`, D-126
> `core/hold48_confidence_kabsch.py`, D-127
> `core/hold48_piecewise_kabsch.py`, and D-128
> `core/hold48_linker_seam.py` all remain callable and **unedited**.

**Parents:** [`D-128` Spec](SPEC-linker-seam-honesty.md) (§1 / §1a / §1b
/ §2 / §3 / §9 / §11) · D-128 Spec `2004c5a` / #246 · D-128-A `9e65cbf`
/ #247 · **D-0043 roadmap Phase 5** (Phase 3 ruled D-128; Phase 4 is the
RMSD class; Phase 5 is this named-refuse sign) ·
[`D-127` Spec](SPEC-piecewise-domain-kabsch.md) · D-127-A `e49bf34` /
#244 · D-127-B `de9a80e` / #245 (four-path UI + mandatory Method + the
D-127 OPS result) ·
[`D-126` Spec](SPEC-overlap-confidence-kabsch.md) · D-126-A `aa8aa02` /
#241 · D-126-B `abbcd00` / #242 ·
[`D-125` Spec](SPEC-kabsch-restitch.md) · D-125-A `26a40a8` / #237 ·
D-125-B `aa8d3f1` / #238 ·
[`D-117`](PLAN-ui-post-wave2-endstate.md) (PLAN / Kabsch park) ·
[`D-118`](README.md) (assembler-not-Kabsch honesty) ·
[`D-120`](README.md) (Phase 2 review of the 27) ·
[`D-121`](method-hold48-tiles.md) (Method: assembler ≠ Kabsch *today*) ·
D-109 ruling 7 (not ranking-eligible) · D-062 / method-note item 7 (the
check is the entry, not the reference) · D-016 (provenance).
**Ship index:** [`decisions.md`](decisions.md).

---

## 1. Goal — name the refusal, accept it, and keep disclosing it

**This Spec does not try to hold a join. It decides what we call the
joins we could not hold.**

Four rigid-body hypotheses have now been pre-registered and run against
the model's own coordinates. D-125 fitted one unweighted rigid body to
the whole overlap. D-126 weighted and trimmed that same one body. D-127
cut the tile into one rigid body **per UniProt domain**. D-128 narrowed
to a single **±32 aa** window around the offending linker — the smallest
of the four — and made the per-path, per-seam honesty measurement
**required**.

The D-128 OPS run of the seven has come back and **the repair half
recovered nothing** (as recorded; §4). That outcome was
**pre-registered as allowed** in the D-128 Spec *before* the run (§1b,
§3, §11 — “**0-of-7 repaired is an allowed outcome**”), so it is a
**finding**, not a miss.

What remains is a labelling question, and every wrong answer is
available:

| Wrong label | Why it is wrong |
|---|---|
| **open must-hunt** | Advertises work nobody is doing and implies a fifth algorithm is coming. Nothing follows this sign. |
| **solved / fixed / repaired / aligned** | The joins are **not held**. Four Specs in a row forbid this, and so does this one. |
| **a D-128 miss / a D-128 failure** | **0-of-7 was pre-registered as allowed.** Reading it as failure is what manufactures a case for loosening a gate. |
| silently retired | Buries a **0 of 7** and a **named regress** behind a friendlier word. That is the D-127-disclosure mistake run again. |

**The Phase 5 sign takes the honest option: `accept-refuse`.** These
joins are **not held**; we **say** so; we **stop hunting** them; and we
keep saying **why** we stopped — including the numbers that make the
stopping honest.

**So the label and the disclosure are one obligation, not two.** §3
binds the label. §4 binds the disclosure. A surface that ships §3
without §4 has **violated** this Spec, not satisfied it.

**What does not change.** The **served** structure stays the
**assembler** (`core/hold48_stitch.py` `winning_tile`) until a Matt swap
GO. **D-126 remains the best experimental path among the stitch
algorithms tried so far, until proven otherwise** — it recovered **2 of
its primary 5** (parents 3368, 3394; as recorded) against D-127's **0 of
3** and D-128's **0 of 7**. Both the **D-127** and the **D-128** failed
rescues **stay disclosed**. The **10.0 Å** gate stays. Off-block PAE
stays **null, never 0** (D-111). The 27 stay outside F-004 (D-109
ruling 7).

---

## 2. Inventory — the eight `accept-refuse` parents

**Fates locked by the Matt Phase 5 sign.** These **eight** parents are
`accept-refuse`: the recorded honest outcome of a refusal, closed to
further hunting.

The pin's own words for the first seven are **"Linker class →
accept-refuse (**failed hunt**)"**, and for the eighth **"Already
accept-refuse: 3432 (`no_domain_pieces`) **unchanged**."** Both terms
are load-bearing: **failed hunt** says the hunt was real and it lost —
not that it was never tried, and not that it succeeded — and
**unchanged** says 3432's status is carried, not re-decided.

| parent job id | accession | Recorded refuse | Fate |
|---|---|---|---|
| **2938** | *not recorded in this log — do not invent* | D-128 `seam_jump_gt_10` | **accept-refuse** |
| **2939** | `Q7Z408` | D-128 `rmsd_gt_10` | **accept-refuse** |
| **3179** | *not recorded in this log — do not invent* | D-128 `seam_jump_gt_10` | **accept-refuse** |
| **3190** | *not recorded in this log — do not invent* | D-128 `seam_jump_gt_10` | **accept-refuse** |
| **3321** | *not recorded in this log — do not invent* | D-128 `seam_jump_gt_10` | **accept-refuse** |
| **3368** | `Q5SZK8` | D-128 `seam_jump_gt_10` | **accept-refuse** |
| **3566** | *not recorded in this log — do not invent* | D-128 `seam_jump_gt_10` | **accept-refuse** |
| **3432** | `Q8IZF6` | D-127 `no_domain_pieces` | **accept-refuse** (**already** accept-refuse under signed triage — **re-affirmed, not newly ruled**) |

The first **seven** are the D-128 linker seven (D-128 Spec §3 — itself
the D-127 OPS `linker_jump_gt_10` class, as recorded). **3432** is the
eighth: its accept-refuse status was already signed triage (D-128 Spec
§3 / §9 / §10) and **this Spec does not re-open, re-rule, or change
it** — it lists it so the fate set is complete and no surface has to
guess.

**Accessions are named only where the log already carries them**
(2939 `Q7Z408`, 3368 `Q5SZK8`, 3432 `Q8IZF6`). For **2938 / 3179 /
3190 / 3321 / 3566** the accession is **not on record in this log**; a
later B resolves it from the database rather than from prose, and
**nobody writes one here from memory** (D-016).

**Every D-127 refuse now carries exactly one fate.** D-127 OPS REFUSE
**10** = `linker_jump_gt_10` ×7 + `rmsd_gt_10` ×2 +
`no_domain_pieces` ×1. **8 + 2 = 10**: the eight above are
`accept-refuse`, and **3272 / 3394** are **Phase 4 must-hunt** (§6).
The two sets are **disjoint**, nothing is left unlabelled, and no parent
is in both. ⚠ Arithmetic on the recorded histogram, **not** a
re-measurement.

⚠ **Not an inventory of work.** Listing these eight is not a queue, not
a named-exclusion, and not an algorithm that skips anyone. It is a
**fate list** for labelling.

---

## 3. Label rules — what UI / Method (B) must and must not say

**Required label.** The pin's instruction is *"label linker seven +
3432 as named refuse."* So: for each of the eight parents of §2, a
surface that names the parent's stitch outcome at all must label it
**named refuse / `accept-refuse`**, and must make plain that this is a
**recorded refusal we accepted**, not a held join.

⚠ **This is the one clause D-128-B has not yet discharged.** Its
Method and review card still describe the seven as **`must-hunt`** —
correct when written, superseded by this sign. A later Method / UI PR
adds the label; §4's disclosure stays exactly as B shipped it.

**Forbidden labels.** None of the eight may be labelled or badged:

- **open must-hunt**, “to hunt,” “pending rescue,” “awaiting a fix,” or
  anything that implies a **fifth stitch algorithm** is coming. The
  hunt is **closed** (§7).
- **solved**, **fixed**, **repaired**, **aligned**, **superimposed**,
  **“seams solved,”** **“seams fixed,”** or **“full-length AF-quality.”**
  (Same forbidden-language park as D-117 §5 / D-125 §6 / D-126 §6 /
  D-127 §6 / D-128 §6 — it stands, unchanged.)
- **a D-128 miss**, **a D-128 failure**, or a **regression against
  D-128's own goal**. **0-of-7 was pre-registered as an allowed
  outcome** (D-128 §1b / §3 / §11); the diagnosis half **landed**, and
  it is the **repair** half that recovered nothing.

**Fail-closed stays fail-closed.** `accept-refuse` is a **label on a
refusal**, and it changes nothing about what may be served or shown:

- No **success PDB** may be presented as honest for a dishonest or
  unknown seam (D-128 §1a). A parent's fate being accepted does not
  make its `stitched.pdb` a good join.
- No assembler / D-125 / D-126 / D-127 / D-128 `stitched.pdb` may be
  badged as a D-128 success or as “the accepted result.” Those files
  stay on disk, stay callable, and stay labelled as what they are.
- A **null** metric renders as an **absence, never `0.00 Å`**. Unknown
  is **not** honest (D-128 §1a).
- **Default served = assembler**, until a Matt swap GO.

**`accept-refuse` is a fate, not a metric.** It does not overwrite,
recompute, or reinterpret any `seams.jsonl` / `seam_honesty.jsonl` row.
The rows say what the run measured; the label says what we decided to
call it.

---

## 4. Disclosure that stays mandatory (accept-refuse ≠ bury)

**The D-128 OPS rollup must be disclosed, as recorded, alongside the §3
labels.** This is the half that keeps §3 honest.

**Status: already discharged, and now standing.** **D-128-B**
(`cd071d7` / #248) shipped that disclosure on the Method surface
(§7 addendum, *"What happened when we actually ran it"*) and in the
five-path review card. It is already there, it is already correct, and
**this Spec does not restate it as a new obligation — it makes the
existing one permanent.** Concretely:

- **Do not gut it.** No later PR may soften, shorten, re-word into
  vagueness, or delete the **0 of 7** or the give-back. Removing it is
  a **Spec violation** (§9), not a cleanup.
- **Do not split it.** The zero and the give-back travel **together**.
  D-128-B's own wording is the standard to keep: *"Reporting '0 of 7,
  which we said was allowed' without the 5 and the 6 beside it would
  bury a drop under a pre-registration."*
- **Do not let the §3 label replace it.** A surface that adds
  `accept-refuse` and drops the numbers has moved backwards. The label
  is *why we stopped*; the rollup is *what we found*.
- **Anything new that names these parents inherits it.** A future
  card, page, or export that labels the eight must carry the rollup or
  link to the surface that does.

⚠ **What D-128-B did not do, and this Spec now requires:** its Method
still calls the seven **`must-hunt`** — accurate when written, and
superseded by the Phase 5 sign. §3's re-label is therefore **owed** to
a later Method / UI PR. That PR **adds** the label; it does **not**
touch the disclosure below.

**Recorded D-128 OPS rollup** — as recorded by **Kaylee** at tip
**`9e65cbf`** (D-128-A / #247), out_root
**`linker_seam_ops_2026-09-05`**. ⚠ **Not re-measured here. Do not
re-measure** — a second number from a second run would not be this one.

| Field | As recorded |
|---|---|
| outcome of the seven | **PASS 0 / REFUSE 7 / FAIL 0 / SKIP 0** |
| `repaired_of_seven` | **0** (**Spec-allowed** — pre-registered at D-128 §1b / §3 / §11) |
| refuse `seam_jump_gt_10` | **2938, 3179, 3190, 3321, 3368, 3566** (×6) |
| refuse `rmsd_gt_10` | **2939** (×1) |
| `n_d125_pass_d128_refuse` | **5** |
| `n_d126_pass_d128_refuse` | **6** |
| `n_d127_pass_d128_refuse` | **0** |
| `n_d127_refuse_d128_pass` | **0** |
| `n_seams_measured` | **35** |
| `n_dishonest_linker_seam` | **6** |
| `n_honesty_unknown` | **4** |
| gate | **10.0 Å** |

**The named regress is not optional copy.** `n_d125_pass_d128_refuse` =
**5** and `n_d126_pass_d128_refuse` = **6** mean D-128 **gave back**
five parents D-125 had accepted and six D-126 had accepted. Those
numbers go **beside** the accept count, **never buried under it** —
that is the mistake the D-127 OPS disclosure was written to avoid, and
`accept-refuse` is not a licence to make it.

**Both failed rescues stay disclosed.** The **D-127** result (PASS 17 /
REFUSE 10 / FAIL 0; `recovered_of_primary_three` = 0; regress 5 vs
D-125, 7 vs D-126 — as recorded) stays on the Method surface, and the
**D-128** result above joins it. B may not replace one with the other,
and may not soften either.

**D-126 stays named the best experimental path so far**, and the
comparison stays quantified: **2 of its primary 5** recovered (parents
3368, 3394) against D-127's **0 of 3** and D-128's **0 of 7** — as
recorded, ⚠ not re-measured.

**Internal consistency, checked before quoting (D-016).** Arithmetic on
the recorded figures, **not** a re-measurement: `0 + 7 + 0 + 0` = **7**
= the seven; the refuse histogram `6 + 1` = **7** = REFUSE;
`repaired_of_seven` = **0** = PASS; `n_d127_refuse_d128_pass` = **0** is
*forced* by PASS 0 (D-128 accepted nobody, so it rescued no D-127
refuse); `n_d127_pass_d128_refuse` = **0** is *forced* by the seven
being exactly D-127's `linker_jump_gt_10` refuse class; every confusion
count is **≤ 7**; and `n_dishonest_linker_seam` = **6** agrees in count
with the six `seam_jump_gt_10` refuses, with **2939** landing in
`n_honesty_unknown` instead because it refused **before any transform**
(post-apply jump null — null is not zero, unknown is not honest,
D-128 §1a).
⚠ **`n_seams_measured` = 35 and `n_honesty_unknown` = 4 are recorded
as-is and are NOT re-derived here.** This Spec does not hold the
per-seam row counts that would reproduce them, and inventing an
arithmetic story for them would be recording a belief rather than a
finding.

**Honest empty still applies.** When the `linker_seam/` tree is missing
for a parent, B does **not** imply a D-128 path exists and invents no
jumps / windows / RMSD. An absence is an absence — it is **not** an
accepted refusal and **not** a solved seam.

---

## 5. Method / owner-facing (D-128-B — later, and mandatory then)

Matt / Emma standing requirement (bound at D-127 §7, kept at D-128 §7,
kept here): **Method must surface the stitch-path train honestly**, and
a code-only ship is forbidden. **This Spec PR ships no Method edit** —
following the pattern the D-127 and D-128 Spec PRs actually shipped
(#243 `00fa76d`, #246 `2004c5a`: the 8th-grade excerpt lives in the
Spec; [`method-hold48-tiles.md`](method-hold48-tiles.md) and
`MethodNote.jsx` are edited in the **B** PR, #245 for D-127). §5 is
therefore **authority**, and the copy below is what a later B must
carry.

Same additive pattern as D-121 / D-125-B / D-126-B / D-127-B: do not gut
the assembler Method, do not rewrite #229, and keep the D-121 /
D-125-B / D-126-B / D-127-B sections — **including** the D-127 OPS
disclosure.

**Required Method copy (plain, 8th-grade):**

**What we tried, and what happened.** To join two overlapping tiles we
tried four different ways of **moving** one tile onto the other. All
four move coordinates the network already produced; none of them is a
new fold.

1. **D-125** — one rigid move fitted to the whole overlap.
2. **D-126** — the same one move, but weighted by the model's own
   confidence, and trimmed. Its lesson: a small **weighted** score can
   hide a big **whole-overlap** gap (gaps of **28–68 Å** on 2939 /
   3272 / 3432). **D-126 is still the best of the four** — it fixed
   **2 of its 5** target joins (parents 3368, 3394).
3. **D-127** — one rigid move **per protein domain**. **It did not pay
   off:** **0 of 3** target joins fixed, and it **gave back** 5 joins
   D-125 had accepted and 7 that D-126 had. **7 of its 10** failures
   were at the **linkers** — the floppy stretches between domains.
4. **D-128** — first **measure** every path's gap at every join and say
   plainly which are **dishonest** (a gap over **10.0 Å**). Then,
   optionally, try **one** small rigid move inside a **±32 aa** window
   around the bad linker. **The measuring worked. The fixing did not:
   0 of 7** joins were repaired, and D-128 also **gave back** 5 joins
   D-125 had accepted and 6 that D-126 had.

**Why 0 of 7 is a result and not a hidden failure.** Before that run,
we wrote down that **fixing zero of the seven was an allowed outcome**.
We said in advance what would count, and then we reported what
happened. That is the whole point of writing the plan first.

**What we decided to call these joins: “accepted refusal.”** Eight
joins — parents **2938, 2939, 3179, 3190, 3321, 3368, 3566** and
**3432** — are now marked **named refuse / accept-refuse**. In plain
words: **these joins do not hold, we say so, and we have stopped trying
to fix them.**

**“Accepted” does not mean fixed, and it does not mean quiet.** It does
**not** mean the seam is solved, aligned, or repaired — it is **not**.
And it does **not** mean we stop reporting the numbers: the **0 of 7**
and the joins D-128 **gave back** (5 vs D-125, 6 vs D-126) stay on this
page next to the label. Accepting a refusal retires the **hunt**, not
the **record**. **Never claim seams solved.**

**Two joins are still open.** Parents **3272** and **3394** failed for a
**different** reason (the whole-overlap distance, not the linker) and
are **still being looked at**. They are not covered by the decision
above, and nothing here changes them.

**What we are not doing next.** There is **no fifth stitching
algorithm**. We are not loosening the **10.0 Å** limit that decides
whether a join counts as honest, and we are not changing which
structure the site serves: the **served** structure is still the
**assembler** (the winner-tile method), as it has been all along.

**What Method does not do.** It does not replace the assembler story.
It does not make the long chain one ESMFold pass. It does not fill PAE.
It does not enter F-004. It is not medical advice.

---

## 6. Phase 4 boundary — 3272 / 3394 stay must-hunt

**3272** `Q6V0I7` and **3394** `Q8TDW7` refused `rmsd_gt_10` — the
**whole-overlap RMSD** class, not the linker / seam class. They are
**Phase 4 must-hunt** and are **out of this Spec**.

- **They are NOT `accept-refuse`.** They are **not** in the §2 eight,
  and a surface must **not** label them accepted, retired, or closed.
- **They move only on a separate Matt GO.** Reclassifying either one —
  into `accept-refuse` or into anything else — requires **explicit Matt
  GO language** naming Phase 4. A B PR, an ops run, a UI convenience,
  or a tidy-up may **not** reclassify them.
- **No RMSD Spec bleed.** This file does **not** spec, scope, schedule,
  design, or pre-authorise Phase 4. It does not name an algorithm for
  the RMSD class, does not set a target, and is **not** that GO.
- **3432 is not Phase 4.** It refused `no_domain_pieces`, and it is
  **accept-refuse** (§2) — already signed triage, re-affirmed here.

> ### ⚠ Phase 4 amendment (D-130) — the separate Matt GO arrived; the hunt is now Spec-governed
>
> **Emma/Matt GO Phase 4 RMSD, 2026-09-05 ~20:39 PT** — *"Go phase 4"* —
> against **vault `D-0043` roadmap Phase 4**. That is the **explicit
> Matt GO language** this section required, and it names Phase 4 and
> both parents. So the boundary above was **crossed on its own terms**,
> not eroded.
>
> **What changed:** **3272** `Q6V0I7` and **3394** `Q8TDW7` move from an
> **unspecced** Phase 4 must-hunt to a **Spec-governed** one. Authority:
> [`SPEC-residual-rmsd-hunt.md`](SPEC-residual-rmsd-hunt.md)
> (**D-130**) and `### D-130` in [`README.md`](README.md) — where that
> log and this file differ, **THE LOG GOVERNS**.
>
> **What did NOT change, and this is the whole point of the amendment:**
>
> - **They are still NOT `accept-refuse`.** They are still not in the
>   §2 eight, and no surface may label them accepted, retired, or
>   closed. A **governed** hunt is an **open** fate.
> - **The §2 eight are unchanged.** No parent joins or leaves them, and
>   **Phase 5 is not reopened**. **3432** stays `accept-refuse`.
> - **§4's disclosure stays standing.** The D-128 OPS **0 of 7** and the
>   give-back (**5** vs D-125, **6** vs D-126) may not be softened,
>   dropped, split apart, or replaced by a D-130 surface.
> - **§7's freeze is NOT repealed.** Only the pin's own *"Phase 4 RMSD
>   only on explicit Matt GO"* clause is **satisfied**. **10.0 Å
>   stays**, **served stays assembler**, **no auto-flip**, **no
>   F-004**, **no linker-v2**, and **D-126 remains the best
>   experimental path until proven otherwise, and callable**.
> - **This file is still not a Phase 4 Spec.** §6 does not spec, scope,
>   or schedule the hunt; D-130 does, in its own file under its own GO.
>
> ⚠ **D-130 introduces no new fit.** Its optional recovery reuses
> **D-125's** unweighted, untrimmed Kabsch on a correspondence
> corrected by **residue identity**; **no trim, no weights, no pieces,
> no window, no linker-inherit.** ⚠ **`recovered_of_two` = 0 is
> pre-registered as an allowed outcome**, and a **named refuse after a
> failed hunt** is a complete outcome. ⚠ **Seams are still NOT
> solved**, and nothing is called solved without measurement.

---

## 7. The freeze — no linker-v2

The stitch-algorithm family **stops here**.

**The pin's freeze clause, bound item for item.** The SIGNED source
(§11) says *"Freeze unchanged: served=assembler; D-126 best
experimental; no threshold loosen; no F-004; no auto-flip."* All five
hold, and **"unchanged" is the operative word** — none of them is a new
ruling this Spec invents, and none may be re-opened by a 0 of 7:

| Pin clause | Bound here |
|---|---|
| `served=assembler` | Default served structure stays the **assembler** `winning_tile`. A swap is a **Matt GO**, never a pass count. |
| `D-126 best experimental` | **D-126 remains the best experimental path until proven otherwise** — and stays **callable**, per the pin's *"D-126 remains best experimental callable."* |
| `no threshold loosen` | **10.0 Å stays**; **W = 32** and **ε = 1e-3** stay. No per-parent exception, no named-exclusion. |
| `no F-004` | The 27 stay **outside** `/scorer` (D-109 ruling 7). No ranking ingest. |
| `no auto-flip` | No surface flips the served path on any count, pass rate, or label change. |

And the pin's **Stop** clause: *"no linker-v2 without new Matt GO; no
gate loosen; Phase 4 RMSD only on explicit Matt GO."*

- **No linker-v2** — and the pin's qualifier is exact: **not without a
  new Matt GO**. A fifth algorithm is not forbidden forever; it is
  forbidden *by default*, and only an explicit new GO reopens it.
  No piecewise-v3. No new decomposition, no piece
  list, no domain intervals as a fit unit, no linker-inherit, no second
  window size, no trim loop, no soft invent blend, no joint placement.
  A later Spec that reintroduces any of those under a new decision id is
  **out of this Spec** and needs its own Matt GO.
- **No restitch.** No ops run of the 27 follows from this sign.
- **The 10.0 Å gate STAYS** and does **not loosen**. **W = 32** and
  **ε = 1e-3** stay. No per-parent exception. No named-exclusion. **No
  threshold Spec-as-fix** — and **0-of-7 does not license one**.
- **Served = assembler.** No auto-flip on any pass count. A swap is a
  **Matt GO**.
- **D-126 remains the best experimental path until proven otherwise** —
  and “proven otherwise” means a measured result, not a newer idea.
- **The D-127 and D-128 failed rescues stay disclosed** (§4). Freezing
  the family is what keeps the four recorded results interpretable;
  dropping their disclosures would spend that.
- **Prior paths stay callable and unedited:** assembler, D-125
  `core/hold48_kabsch.py`, D-126 `core/hold48_confidence_kabsch.py`,
  D-127 `core/hold48_piecewise_kabsch.py`, D-128
  `core/hold48_linker_seam.py`. All five trees stay on disk; none is
  overwritten.

---

## 8. PR split — Spec vs the labelling BUILD

| Id | What | This PR? | Gate |
|---|---|---|---|
| **D-129 Spec** | This file + `### D-129` + ship index + `ARCHITECTURE.md` one-liner + PLAN pointer + `Test_Plan.md` T-ids + hermetic docs pin tests + the D-128 Spec §3 / §9 cross-link. Includes the §5 Method excerpt as **authority**. | **Yes — this PR.** | Trinity reviewed. **Docs only.** |
| **D-128-B** | UI five-path honesty + the **mandatory** Method addendum, including the **§4 disclosure** (0 of 7 + the 5 / 6 give-back). Reads A's `linker_seam/` tree. Default served = assembler. | **No — already shipped** on `main` (`cd071d7` / #248). | Discharged Spec §7. §4 makes its disclosure **standing**: do not gut it. |
| **The §3 re-label** (later Method / UI PR) | Re-label the eight from **must-hunt** to **named refuse / `accept-refuse`** on `method-hold48-tiles.md`, `MethodNote.jsx`, and the review card, per §3 and the §5 copy. **Additive** — it does **not** touch D-128-B's §4 disclosure. | No. Later Emma GO. | After this Spec is on `main`. The one B-side item D-129 leaves **owed**. |
| **Phase 4 (RMSD class)** | 3272 / 3394 | No. **Separate Matt GO** (§6). | Not this family of PRs. |
| **linker-v2 / any fifth algorithm** | — | **No. Frozen** (§7). | Would need its own Matt GO. |

**Out of this Spec PR:** any UI / React file, any `MethodNote.jsx`
edit, any Method file edit (`method-hold48-tiles.md`), any
`hold48_*.py` or core algorithm edit, any `scripts/*restitch*.py` edit,
a restitch or ops run, an F-004 ingest, ADC-C / `/adcs` bleed, rent /
GPU / RunPod / Fly POST, a threshold change, a served-path swap, a
**linker-v2 Spec**, a **Phase 4 / RMSD Spec**, re-measuring the D-128
OPS figures, re-opening 3432, reclassifying 3272 / 3394, **merging
D-128-B**, inventing a D-129-B, claiming seams solved, or self-merging.

---

## 9. Hard stops (Spec + log)

- **`accept-refuse` is never “solved.”** Not solved, not fixed, not
  repaired, not aligned, not superimposed. **This Spec never says
  solved.** Forbidden language stands.
- **`accept-refuse` is never Method silence.** §4's disclosure — **0 of
  7** and the **5** / **6** named confusion — ships **with** the label.
  Dropping, softening, or burying it is a **Spec violation**, not a
  simplification.
- **Never “open must-hunt” for the eight.** The hunt is closed and no
  fifth algorithm is coming.
- **Never “a D-128 miss.”** **0-of-7 was pre-registered** as an allowed
  outcome before the run. The diagnosis half landed.
- **No linker-v2 without a new Matt GO**, and no fifth stitch algorithm
  by default (§7 — the pin's `Stop` clause).
- **No gate loosen** (pin `Stop`). **Phase 4 RMSD only on explicit Matt
  GO** (pin `Stop`).
- **No F-004** and **no auto-flip** (pin `Freeze unchanged`) — carried
  as unchanged standing rules, not re-decided here.
- **The scar candidate `S-20260905` stays a candidate.** This Spec does
  not create a scar registry, assign a repo id, or promote it.
- **No threshold Spec-as-fix.** **10.0 Å stays**, **W = 32** stays,
  **ε = 1e-3** stays. No loosen, no per-parent exception, no
  named-exclusion, no trim loop, no soft invent blend.
- **No RMSD Spec bleed.** **3272 / 3394 stay Phase 4 must-hunt** and
  are **not** `accept-refuse`. No reclassification **without explicit
  Matt GO language**.
- **3432 is re-affirmed, not re-ruled.** Its accept-refuse status was
  already signed triage; this Spec does not re-open it, reclassify it,
  or count it as a D-128 miss.
- **No invent.** Fail closed. No success PDB presented as honest for a
  dishonest or unknown seam. Null renders as an absence, **never
  `0.00 Å`**; unknown is **not** honest. No invented accession for the
  five parents this log does not carry.
- **No re-measure.** The D-128 OPS rollup is quoted **as recorded** at
  tip `9e65cbf`, out_root `linker_seam_ops_2026-09-05`. This Spec runs
  nothing and re-derives nothing — and does **not** reconstruct
  `n_seams_measured` / `n_honesty_unknown` from prose.
- **No PAE zeros.** Off-block PAE stays null, never 0 (D-111).
- **No F-004.** The 27 stay outside `/scorer` (D-109 ruling 7).
- **Served stays assembler.** No auto-flip on any count. A swap is a
  Matt GO.
- **D-126 remains the best experimental path until proven otherwise**,
  and **both** the D-127 and D-128 failed rescues **stay disclosed**.
  Neither may be softened or dropped by any surface.
- **Keep prior paths callable.** Assembler + D-125 + D-126 + D-127 +
  D-128 stay callable; no tree is overwritten.
- **No code, no UI, no Method edit in this PR.** No `hold48_*.py` edit,
  no `MethodNote.jsx`, no `method-hold48-tiles.md`.
- **No silent code-only.** The Method surface obligation (§5) is
  **mandatory at B**.
- **No self-merge.** Draft PR; **Trinity merges**.

---

## 10. What this file is not

- **Not D-128-B** (the UI / Method labelling BUILD). This file is the
  Spec, not a BUILD.
- **Not an algorithm Spec at all.** It changes no geometry, no
  threshold, no refuse reason, no artifact tree, and no served byte.
- **Not a linker-v2 Spec** and not a licence for a fifth stitch
  algorithm.
- **Not a Phase 4 / RMSD Spec**, not a Phase 4 GO, and not a schedule
  for one.
- **Not a re-opening of 3432**, which was already `accept-refuse`.
- **Not a reclassification of 3272 / 3394**, which stay Phase 4
  must-hunt.
- **Not a claim that seams are solved**, aligned, or that the chain is
  one forward pass.
- **Not a retraction** of the D-127 OPS disclosure, of the D-128 OPS
  rollup, or of D-126's standing as the best experimental path so far.
- **Not a threshold change** (up **or** down) and not a
  named-exclusion.
- **Not a served-path swap.**
- **Not an amendment** to D-128 Spec §1 / §1a / §1b / §2 / §5 / §11 —
  only §3's inventory note and §9's hard stops gain a **cross-link**.
- **Not an edit** of `core/hold48_kabsch.py`,
  `core/hold48_confidence_kabsch.py`,
  `core/hold48_piecewise_kabsch.py`, `core/hold48_linker_seam.py`, or
  `core/hold48_stitch.py`.
- **Not a Method file edit** and not a `MethodNote.jsx` edit — §5 is
  required copy as **authority only**.
- **Not an ops run**, not a restitch of the 27, not a Fly re-query, and
  not a re-measurement.
- **Not ADC-C** (D-124). Not ranking ingest. Not F-004.
- **Not a repair of the `D-` next-free pointer.**
- **Not a merge of D-128-B** and not an invention of D-129-B.
- **Not a CI assert against live ops** — §4's rollup is a required
  **disclosure** field set, quoted as recorded, not a gate test.

---

## 11. The SIGNED source, verbatim

Reproduced **verbatim** so every clause above can be checked against the
artefact rather than against a paraphrase of it (D-016). Supplied by
Emma, who confirmed the vault pin matches the Architect brief.
⚠ **Vault `D-0043` is external numbering, not a project decision**, and
**not** repo `### D-043`. ⚠ **Not re-measured here.**

**Cite as:** `D-0043 Phase 5 named-refuse, SIGNED 2026-09-05 ~17:58 PT`.

```text
# Phase 5 named-refuse — SIGNED (D-0043)
Status: SIGNED 2026-09-05 ~17:58 PT — Matt: Sign Phase 5 as drafted. Architect support on file.
Forced by: D-128 OPS tip 9e65cbf — PASS 0 / REFUSE 7 / recovered 0 on linker must-hunt seven. Architect: diagnosis yes, repair no.
Freeze unchanged: served=assembler; D-126 best experimental; no threshold loosen; no F-004; no auto-flip.

Linker class → accept-refuse (failed hunt): 2938 seam_jump_gt_10; 2939 rmsd_gt_10; 3179/3190/3321/3368/3566 seam_jump_gt_10.
Already accept-refuse: 3432 (no_domain_pieces) unchanged.
Still must-hunt Phase 4 later: 3272, 3394 (RMSD).

Method/UI: Disclose D-128 OPS 0/7 + confusion; label linker seven + 3432 as named refuse; never solved; D-126 remains best experimental callable.
Stop: no linker-v2 without new Matt GO; no gate loosen; Phase 4 RMSD only on explicit Matt GO.

Scar candidate S-20260905: linker/seam honesty diagnosed; did not repair; seven → named refuse.
```

**Where the pin lands in this Spec:**

| Pin clause | Section |
|---|---|
| `Linker class → accept-refuse (failed hunt)` + per-parent reasons | §2 (the eight), §4 (the rollup) |
| `Already accept-refuse: 3432 … unchanged` | §2 (re-affirmed, not newly ruled) |
| `Still must-hunt Phase 4 later: 3272, 3394 (RMSD)` | §6 |
| `Disclose D-128 OPS 0/7 + confusion` | §4 (standing; already discharged by D-128-B) |
| `label linker seven + 3432 as named refuse` | §3 (owed re-label) |
| `never solved` | §1, §3, §9, §10 |
| `D-126 remains best experimental callable` | §7 |
| `Freeze unchanged` (five clauses) | §7 |
| `Stop` (three clauses) | §6, §7, §9 |

**The pin's own framing of the result — *"Architect: diagnosis yes,
repair no"*** — is the sentence this whole Spec exists to keep legible.
D-128's required half (§1a honesty measurement) **worked**. Its optional
half (the ±32 aa repair) **recovered nothing**. `accept-refuse` names
the second without erasing the first, which is why §4's disclosure is
not optional decoration.

**Scar candidate `S-20260905`** — recorded **verbatim as a candidate**,
exactly as the pin words it: *"linker/seam honesty diagnosed; did not
repair; seven → named refuse."*
⚠ **This repo has no `S-NNNNNNNN` scar registry**, and this Spec does
**not** create one, promote the candidate to a ruled scar, or assign it
a repo id. It is carried so the candidate is not lost, and so a later
scar ruling has the wording it came from. Naming a candidate is not
ruling it.
