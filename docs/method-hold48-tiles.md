# How we fold long proteins: tiles, glue, and an assembler

*An eighth-grade write-up for the owner. Decision: [`D-121`](README.md)
(confirm the `### D-121` header exists before citing). Parents: **D-118**
(honesty — rental closed, assembler not Kabsch) and **D-120** (Phase 2 review
UI). #229 stays merged; this file does not reopen it.*

Facts come from entries that already exist. If those entries did not say it,
this file does not say it. ⚠ **Not a restitch run of the 27. Not F-004. Not `/adcs`.**
A D-125-B addendum names what a Kabsch-path restitch does and does not.
A D-126-B addendum names what weighted / trimmed Kabsch does and does not
versus the assembler and versus D-125. A **D-127-B** addendum names the
whole four-step stitch-path train and what piecewise / domain-aware
Kabsch does and does not — **mandatory** under D-127 Spec §7, not a
later nice-to-have. A **D-128-B** addendum names the **five**-step train,
what *dishonest* means about a structure file, and the D-128 OPS result
as recorded — **mandatory** under D-128 Spec §7 on the same terms.

---

## The problem — a long protein does not fit in one gulp

Our folding network, ESMFold, predicts a 3D shape from a protein's letter
string. It has a hard size cap. **D-111** already named that cap: a window of
**1656** amino acids, with a **128**-amino-acid overlap between neighboring
windows (stride **1528**). Those integers were not invented here.

Some census proteins are longer than 1656. The network cannot swallow those
in one forward pass. So we cut each long chain into **overlapping tiles** —
shorter stretches, like shingles on a roof. Each tile is its own ESMFold run.
The network never sees the whole long chain at once.

## The overlap is the glue

Where two tiles cover the same stretch, that shared stretch is the **glue**.
It is not a chemical glue. It is the same residues, predicted twice, so the
two pieces have a place they both talk about.

The glue is how we *choose* which tile wins in the shared stretch. It is
**not** a trick that twists one piece until it sits on the other.

## Assemble means pick a winner — not Kabsch

When we "assemble" a long protein, we walk residue by residue. At each spot,
if more than one tile covers it, we keep the tile with the higher **pLDDT**
(the model's own confidence score, 0–100) at that residue. Ties go to the
earlier tile. That is a **pLDDT winner-tile assembler**
(`core/hold48_stitch.py`).

This is **not Kabsch**. Kabsch is a math move that rotates and slides one 3D
piece onto another so they line up. We did not do that. Each residue keeps
the coordinates the winning tile's network pass already had. No atom is
invented. Off-block pair-confidence (PAE) stays empty — never filled with a
fake zero.

A stitched chain is therefore an **overlap of several ESMFold passes**, not
one new network output, and not a superimposed holoprotein. It is not
ranking-eligible (**D-109** ruling 7).

## Seams can look ugly — ~88.76 Å is a disclosure, not a fix

Because we did not line the tiles up in 3D, the join can jump. On the IGF2R
pilot, that jump was measured at about **88.76 Å**. That number is a
**disclosure**, not a solved structure. The seam is **not scientifically solved**.
What a Kabsch-path restitch does — and does not do — is named in the
D-125-B addendum below. This section is still the assembler story.
There is no button that heals the join.

## Addendum D-125-B — what a Kabsch-path restitch does (and does not)

The assembler path above is still the **default served structure**. A
later GO (**D-125-A**) wrote a second, sibling tree of files under
`kabsch/{parent}/`. This page does not swap that tree in as "the"
structure. ⚠ **Scoped by D-139:** the assembler is still the default and
still what the **D-125 Kabsch-path** tree is measured against — the one
swap that has since been signed hands out the **D-126** structure, and
only for the recorded PASS seventeen. See the D-139 addendum below.

**What Kabsch does.** After the tiles are already folded by ESMFold,
Kabsch is a math move. It rotates and slides one tile so the shared
stretch (the glue residues' Cα atoms) sits closer to the other tile's
shared stretch. Then the same winner-tile assembler still picks which
tile wins each residue. The network does not run again. No atom is
invented. A refused seam writes a record and does not write a
"fixed" structure.

**What Kabsch does not do.** It does not make the long chain one ESMFold
pass. It does not fill empty pair-confidence (PAE) between tiles. It
does not mean the joins are scientifically solved. Seams are
**not scientifically solved**. It does not put
these chains into the ranking (**D-109**). It is not medical advice and
it is not a holoprotein the model jointly placed.

When both trees are on disk, the review card names them as two paths
with different persist stems (`stitched` vs `kabsch/{parent}`) so they
cannot be read as one population. Overlap RMSD and max Cα jump are
shown only if A's provenance/seams files already computed them. If
those numbers are missing, the card says so — it does not invent them.

## Addendum D-126-B — what overlap-confidence Kabsch does (and does not)

The assembler path above is still the **default served structure**.
D-125-A wrote a second sibling tree under `kabsch/{parent}/`.
D-126-A wrote a **third** sibling tree under
`confidence_kabsch/{parent}/`. This page does not swap either tree
in as "the" structure. A later Matt GO would have to name that swap.
⚠ **That GO has since arrived, and it is D-139** — for the **seventeen**
parents carrying a recorded PASS and no later named refuse, the
`confidence_kabsch/{parent}/` structure **is** what the site hands out.
Every other parent keeps the assembler. The swap is by allowlist and
gate, never automatic; the D-139 addendum below is the whole of it.

**What overlap-confidence Kabsch does.** After the tiles are already
folded by ESMFold, this third path is still a math move. It rotates
and slides one tile so the shared stretch sits closer to the other
tile's shared stretch. The difference is which glue atoms it listens
to: it down-weights shaky residues (low pLDDT) and can drop the
worst-fitting 10% of overlap points, then measures a **weighted**
RMSD. The **10.0 Å refuse gate stays**. Then the same winner-tile
assembler still picks which tile wins each residue. The network does
not run again. No atom is invented. A refused seam writes a record
and does not write a "fixed" structure.

**What overlap-confidence Kabsch does not do.** It does not replace
the assembler. It does not overwrite the D-125 Kabsch-path files.
It does not make the long chain one ESMFold pass. It does not fill
empty pair-confidence (PAE) between tiles. It does **not** mean the
joins are scientifically solved. Seams are **not scientifically
solved**. It does not put these chains into the ranking (**D-109**).
It is not medical advice and it is not a holoprotein the model
jointly placed. It does not invent RMSD or trim counts when the
third tree is missing.

When the third tree is on disk, the review card names **three**
paths with different persist stems (`stitched` vs `kabsch/{parent}`
vs `confidence_kabsch/{parent}`) so they cannot be read as one
population. Weighted RMSD, full-overlap RMSD, max Cα jump, effective
Cα count, and trim rounds are shown only if A's provenance/seams
files already computed them. If those numbers are missing, the card
says so — it does not invent them. When the third tree is missing,
the card does not pretend the D-126 path exists.

## Addendum D-127-B — piecewise / domain-aware Kabsch, and the whole stitch-path train

*Spec authority: [`SPEC-piecewise-domain-kabsch.md`](SPEC-piecewise-domain-kabsch.md)
§6 (UI) and §7 (Method). ⚠ **§7 makes this section mandatory** — D-127 is
**not "done"** without it, and a code-only ship is forbidden by name.*

There are now **four** ways this project has put two folded tiles next to
each other. They are not four answers to one question. They are four
different moves, and only the first one is served.

**The stitch-path train, in order.**

1. **Assembler** — pick the winner tile by pLDDT at each residue. This is
   the **default served** structure and stays that way until a Matt swap GO.
   ⚠ **The swap GO arrived at D-139** and moved exactly seventeen parents
   onto path 3; every parent this section is about still gets path 1.
2. **D-125 Kabsch** — one unweighted rigid move on the glue Cα, then the
   same assembler.
3. **D-126 confidence** — one weighted / trimmed rigid move on the same
   glue, then the same assembler. The D-126 lesson: a small **weighted**
   RMSD can hide a large **full-overlap** jump. On 2939 / 3272 / 3432 the
   full-overlap RMSD was far larger than the weighted one, with max Cα
   jumps of about **28–68 Å** (D-126 ops surface, named in the task brief
   2026-09-05; ⚠ **not re-measured here**). A number obtained by dropping
   the points that disagreed with you is not a solved seam.
4. **D-127 piecewise / domain** — one weighted rigid move **per UniProt
   domain** that overlaps the glue, then the same assembler. **No trim
   loop.** Linker residues — the ones between domains — inherit the
   transform of the nearest accepted domain on their N-terminal side.

**The refuse table, in plain terms.** A domain piece can refuse if it has
fewer than three Cα to fit, if its weighted RMSD comes out above
**10.0 Å**, or if its points sit in a line. The whole parent refuses if no
domain covers the glue at all, or if a linker Cα jumps more than
**10.0 Å**. A refuse writes a record. It does **not** write a "fixed"
structure. The **10.0 Å gate stays** — recovering none of those three
parents is an allowed result, not a reason to move the bar.

**Seam disclosure.** When the fourth tree is on disk, the review card
names each piece separately: its domain interval, how many Cα it fitted,
its weighted RMSD, and whether it refused. Beside those rows sit the
parent full-overlap RMSD and max Cα jump after the piecewise moves, plus
the linker count and its worst jump. Those are **measurements**. They are
not a verdict that the holoprotein is lined up. Never claim the seams are
solved. Seams are **not scientifically solved**.

The card shows **one row per piece** and never a seam average. Averaging
several domain pieces into one number would hide exactly the per-domain
disagreement multi-rigid exists to expose — the D-126 lie surface wearing
new clothes.

**What piecewise Kabsch does not do.** It does not replace the assembler;
the served PDB is still the assembler one — for **every** parent, including
after D-139, which serves **D-126** and never this path. It does not overwrite the
D-125 `kabsch/{parent}/` or D-126 `confidence_kabsch/{parent}/` files. It
does not make the long chain one ESMFold pass. It does not fill empty
pair-confidence (PAE) between tiles. It does not put these chains into the
ranking (**D-109**). It is not medical advice and it is not a holoprotein
the model jointly placed.

### What happened when we actually ran it (D-127 OPS, 2026-09-05)

*⚠ These are ops numbers **as recorded** and handed to this write-up
(Matt GO via Emma, 2026-09-05, naming a D-127 OPS restitch of the Spec 27
at tip `e49bf34`). ⚠ **Not run, not queried, and not re-measured here.***

We ran piecewise / domain-aware Kabsch over the 27 stitched parents:
**PASS 17 · REFUSE 10 · FAIL 0**.

Seventeen accepted is not the headline, and here is why.

- **It recovered none of the three parents it was built for.**
  `recovered_of_primary_three` = **0**. Parent **2939** refused
  `linker_jump_gt_10`, **3272** refused `rmsd_gt_10`, and **3432**
  refused `no_domain_pieces`. Those three were the whole reason the
  multi-rigid family was proposed.
- **It lost ground the earlier paths had held.**
  `n_d125_pass_d127_refuse` = **5** — five parents D-125 accepted now
  refuse. `n_d126_pass_d127_refuse` = **7** — seven parents D-126
  accepted now refuse. And `n_d126_refuse_d127_pass` = **0** —
  piecewise did not rescue a single parent that D-126 had already
  refused. That is a **named finding**, not a footnote under an accept
  count.
- **Where the refuses came from.** `linker_jump_gt_10` **×7** (2938,
  2939, 3179, 3190, 3321, 3368, 3566); `rmsd_gt_10` **×2** (3272,
  3394); `no_domain_pieces` **×1** (3432). Most failures are at the
  **linkers** — the stretches between domains — which is exactly where
  cutting one rigid body into several creates new joins.

**So: D-126 remains the best experimental path among the stitch
algorithms we have tried so far.** Plainly. And the comparison is a
number, not an opinion: **D-126 OPS recovered 2 of its primary 5** —
parents **3368** and **3394** — against D-127's **0 of 3**. (Those two
figures are ops results as recorded and handed to this write-up; ⚠ **not
re-measured here**.)

Worse than "no gain": **both parents D-126 recovered are back in
D-127's refuse list** — **3368** under `linker_jump_gt_10` and
**3394** under `rmsd_gt_10`, as the histogram above shows. Piecewise
gave back the ground the previous path had won.

D-127 was a reasonable hypothesis — fit each domain in its own frame
instead of forcing one frame on the whole tile — and the run says it did
not pay off.

Recovering zero of the three was **pre-registered as an allowed
outcome** before the run (Spec §3). It is a result, not a failure of
nerve, and it is **not** a reason to raise the 10.0 Å gate, relax the
linker gate, add a trim loop, or invent a blend. No threshold moved
because of this run. Nothing here flips the served path either: the
**default served structure is still the assembler**, and only a Matt GO
can change that — never a pass count. ⚠ **Scoped by D-139:** that Matt GO
has since arrived and flipped the recorded PASS **seventeen** onto D-126.
It changed nothing here — **all ten** parents D-127 refused, these three
included, are excluded from it by name and keep the assembler.

And 17 accepted parents are **17 recorded outcomes**, not 17 solved
joins. A seam that was recorded is not a seam that was solved.

When the fourth tree is on disk, the review card names **four** paths with
different persist stems (`stitched` vs `kabsch/{parent}` vs
`confidence_kabsch/{parent}` vs `piecewise_kabsch/{parent}`) so they cannot
be read as one population. Per-piece Cα counts and RMSD, the parent
full-overlap RMSD and max Cα jump, and the linker fields are shown only if
A's provenance / seams files already computed them — a refuse-before-
transform leaves them empty, and empty is not zero. If those numbers are
missing, the card says so; it does not invent them. When the fourth tree
is missing, the card does not pretend the D-127 path exists, and that
absence is not a solved seam.

## Addendum D-128-B — linker / seam honesty, and the five-step stitch-path train

*Spec authority: [`SPEC-linker-seam-honesty.md`](SPEC-linker-seam-honesty.md)
§6 (UI) and §7 (Method). ⚠ **§7 makes this section mandatory** — D-128 is
**not "done"** without it, and a code-only ship is forbidden by name.*

There are now **five** ways this project has put two folded tiles next to
each other. Only the first one is served, and the fifth one is not really
another way of joining tiles at all — it is a way of **checking** the
other four.

**The stitch-path train, in order.**

1. **Assembler** — pick the winner tile by pLDDT at each residue. This is
   the **default served** structure and stays that way until a Matt swap GO.
   ⚠ **The swap GO arrived at D-139** and moved exactly seventeen parents
   onto path 3; every parent this section is about still gets path 1.
2. **D-125 Kabsch** — one unweighted rigid move on the glue Cα, then the
   same assembler.
3. **D-126 confidence** — one weighted / trimmed rigid move on the same
   glue, then the same assembler. Its lesson: a small **weighted** RMSD
   can hide a large **full-overlap** jump (ops jumps about **28–68 Å** on
   2939 / 3272 / 3432, as recorded; ⚠ **not re-measured here**).
   **D-126 is still the best experimental path we have tried** — it
   recovered **2 of its primary 5**, parents **3368** and **3394**.
4. **D-127 piecewise / domain** — one weighted rigid move **per UniProt
   domain**, then the same assembler. **The run says it did not pay
   off:** PASS 17 / REFUSE 10 / FAIL 0, **0 of 3** primary parents
   recovered, and it **gave back** 5 parents D-125 had accepted and 7
   D-126 had accepted. That failed experiment **stays disclosed** above,
   and none of D-128's numbers stand in for it.
5. **D-128 linker / seam honesty** — first, **measure** every path's seam
   jump and say plainly which paths are **dishonest** at that seam (a
   jump over **10.0 Å**). Then, optionally, try **one** small rigid move
   inside a **±32 aa** window around the offending linker. Most of
   D-127's failures were at the linkers (**7 of 10** refuses), which is
   why the window is where it is.

**What "dishonest" means here.** It is a statement about the **structure
file**, not about a person. If a path's seam still jumps more than
**10.0 Å** after that path's own transform, then presenting that path's
`stitched.pdb` as a good join would be dishonest — so we refuse it and
record why. **The 10.0 Å gate stays.**

**The refuse table, in plain terms.** A window refuses if it has fewer
than three Cα to fit, if its weighted RMSD comes out above **10.0 Å**, or
if its points sit in a line. The parent refuses if the seam still jumps
more than **10.0 Å** after the move. A refuse writes a record. It does
**not** write a "fixed" structure.

**Seam disclosure.** When the fifth tree is on disk, the review card
names, for **each path and each seam**, the max Cα jump that path
**ends** with and whether it is therefore honest there — plus, for D-128
itself, the window it fitted, how many Cα were in it, the weighted RMSD,
the jump before and after, and how the offending seam was identified.
Those are **measurements**. They are not a verdict that the holoprotein
is lined up. Never claim the seams are solved.
Seams are **not scientifically solved**.

The card shows **one row per path per seam** and never an average across
them. A mean jump would hide the single seam that flies apart, and an
"N of M seams honest" score would hide **which** path is dishonest
**where** — which is the whole content of the check. A missing jump is an
absence, never `0.00 Å`, and an **unknown jump is not honest**.

**What linker / seam honesty does not do.** It does not replace the
assembler; the served PDB is still the assembler one — for **every**
parent, including after D-139, which serves **D-126** and never this path. It does not
overwrite the D-125 `kabsch/{parent}/`, D-126
`confidence_kabsch/{parent}/`, or D-127 `piecewise_kabsch/{parent}/`
files. It does not make the long chain one ESMFold pass. It does not fill
empty pair-confidence (PAE) between tiles. It does not put these chains
into the ranking (**D-109**). It is not medical advice and it is not a
holoprotein the model jointly placed. When the fifth tree is missing, the
card says so — it does not invent a jump, a window, or an honesty verdict,
and that absence is not a solved seam.

### What happened when we actually ran it (D-128 OPS, 2026-09-06)

*⚠ These are ops numbers **as recorded** and handed to this write-up
(MANDATORY Method §7 OPS honesty inject, Matt GO via Emma, 2026-09-06,
naming a D-128 OPS restitch of the must-hunt **seven** — **"must-hunt" is
what they were called when that run was chosen, and the Phase 5 sign has
since superseded that name; see the D-129-B addendum below** — at tip
`9e65cbf`, out_root `linker_seam_ops_2026-09-05`). ⚠ **Not run, not
queried, and not re-measured here.***

We ran the linker / seam path over the seven signed must-hunt linker
parents (**"must-hunt" is what they were called when this run was
chosen**; the Phase 5 sign has since re-labelled them **named refuse /
accept-refuse** — see the D-129-B addendum below. The numbers in this
section are unchanged): **PASS 0 · REFUSE 7 · FAIL 0 · SKIP 0**.

- **It repaired none of the seven.** `recovered_of_seven` = **0** and
  `repaired_of_seven` = **0**. That zero was **pre-registered as an
  allowed outcome** before the code existed, so it is a result rather
  than a failure of nerve — and it is **not** a reason to raise the
  10.0 Å gate, relax it, add a trim loop, invent a blend, try a second
  window size, or re-open 3432.
- **Where the refuses came from.** `seam_jump_gt_10` **×6** (2938, 3179,
  3190, 3321, 3368, 3566) — the ±32 aa window fitted, and the **whole
  seam** still jumped more than **10.0 Å** afterwards. `rmsd_gt_10`
  **×1** (2939) — the window's own weighted RMSD was above the gate, so
  nothing was applied at all. ⚠ These are **D-128's** reason names:
  `seam_jump_gt_10` is measured after the single window move and is
  **not** D-127's `linker_jump_gt_10`, and this `rmsd_gt_10` is the
  **window weighted** RMSD, not D-127's full-overlap class.
- **It lost ground the earlier paths had held — and a zero is not a place
  to hide that.** `n_d125_pass_d128_refuse` = **5** — five parents D-125
  accepted now refuse. `n_d126_pass_d128_refuse` = **6** — six parents
  D-126 accepted now refuse. `n_d127_pass_d128_refuse` = **0** and
  `n_d127_refuse_d128_pass` = **0**, because D-127 had already refused
  all seven; there was no D-127 ground to win or lose here. **That is a
  named finding**, and it ships in the same breath as the allowed zero.
  Reporting "0 of 7, which we said was allowed" without the 5 and the 6
  beside it would bury a drop under a pre-registration.

**So: D-126 remains the best experimental path among the stitch
algorithms we have tried so far.** This run points the same way rather
than disturbing it: **2 of its primary 5** for D-126, against **0 of 3**
for D-127 and **0 of 7** for D-128. And **3368** — one of the two parents
D-126 recovered — sits in this refuse list too, under `seam_jump_gt_10`.
Both later paths gave back ground D-126 had won.

D-128 was a reasonable hypothesis — if the break is at the linkers, fit a
small rigid window right there instead of cutting the whole tile up — and
the run says it did not pay off. On **six of the seven** the window
*fitted* and the seam broke anyway, which is evidence about that
hypothesis and **not** evidence that the joins are closer to being
solved. It is also **one run, as recorded, at one window size**: **W = 32**
stays a pinned v1 default, not a measured optimum, and a second window
size tried until a parent passes is forbidden by Spec §1b.

**And no linker-v2.** The obvious move after 0 of 7 is to go round again
with a different window — a wider one, a narrower one, two of them, a
linker boundary picked some other way — and call it the next version.
That is D-127's mistake wearing D-128's clothes: decompose differently
until the count improves, and buy a pass with a claim nobody measured.
Three rigid-body families have now been tried on these joins and **D-126
is still the best of them**. The honest next move is not a sixth one.

**An accepted refusal is a record, not a silence.** *Accept-refuse* means
we accepted the refusal as the honest outcome for that parent — parent
**3432**'s signed triage is the standing example. It does **not** mean
the parent was dropped from the run, quietly skipped, excluded from the
inventory, or left unmentioned. Every one of the seven has a written row
naming its reason, and so does 3432. A refusal we can point at is the
opposite of silence, and it is the whole product of this path: **the
deliverable was the measurement, and the measurement came out negative.**

**No threshold moved because of this run.** Nothing here flips the served
path either: the **default served structure is still the assembler**, and
only a Matt GO can change that — never a pass count. ⚠ **Scoped by
D-139:** that Matt GO has since arrived and flipped the recorded PASS
**seventeen** onto D-126. **None of these seven is in it** — a parent
D-128 measured as `seam_jump_gt_10` is precisely a parent whose D-126 pose
we hold a measurement against, so all seven keep the assembler. **3432 stays
accept-refuse** (signed triage): it is not a success target of this path,
not re-opened, and not counted as a D-128 miss.

And seven recorded refuses are **seven recorded outcomes**, not seven
diagnosed-and-repaired joins. A seam that was recorded is not a seam that
was solved.

When the fifth tree is on disk, the review card names **five** paths with
five persist stems (`stitched` vs `kabsch/{parent}` vs
`confidence_kabsch/{parent}` vs `piecewise_kabsch/{parent}` vs
`linker_seam/{parent}`) so they cannot be read as one population. The
served download is still the assembler `stitched` one **for the parents
this section is about**. ⚠ **D-139** changed that for the recorded PASS
seventeen only, and their download is named `stitched_confidence_kabsch`
so the two files can never be confused.

## Addendum D-129-B — what we now call the eight joins we could not hold

*Spec authority: [`SPEC-phase5-named-refuse.md`](SPEC-phase5-named-refuse.md)
§3 (the label), §4 (the disclosure that ships with it), §5 (this copy),
§6 (Phase 4 stays out) and §7 (the freeze). Ruled by **Matt SIGNED Phase 5
named-refuse, 2026-09-05 ~17:58 PT via Emma**. ⚠ **Labels only** — this
section changes no geometry, no threshold, and no served byte, and it
**adds nothing to and removes nothing from** the D-128 numbers above.*

**What we tried, and what happened.** To join two overlapping tiles we
tried four different ways of **moving** one tile onto the other. All four
move coordinates the network already produced; none of them is a new
fold. **D-125** fitted one rigid move to the whole overlap. **D-126**
fitted the same one move, but weighted by the model's own confidence, and
trimmed — its lesson is that a small **weighted** score can hide a big
**whole-overlap** gap (gaps of **28–68 Å** on 2939 / 3272 / 3432), and it
is **still the best of the four**, because it fixed **2 of its 5** target
joins (parents 3368 and 3394). **D-127** fitted one rigid move **per
protein domain**, and **it did not pay off**: **0 of 3** target joins
fixed, and it **gave back** 5 joins D-125 had accepted and 7 that D-126
had. **7 of its 10** failures were at the **linkers** — the floppy
stretches between domains. **D-128** first **measured** every path's gap
at every join and said plainly which are **dishonest** (a gap over
**10.0 Å**), then optionally tried **one** small rigid move inside a
**±32 aa** window around the bad linker. **The measuring worked. The
fixing did not: 0 of 7** joins were repaired, and D-128 also **gave
back** 5 joins D-125 had accepted and 6 that D-126 had.

**Why 0 of 7 is a result and not a hidden failure.** Before that run, we
wrote down that **fixing zero of the seven was an allowed outcome**. We
said in advance what would count, and then we reported what happened.
That is the whole point of writing the plan first.

**What we decided to call these joins: "accepted refusal."** Eight joins
— parents **2938, 2939, 3179, 3190, 3321, 3368, 3566** and **3432** —
are now marked **named refuse / accept-refuse**. In plain words: **these
joins do not hold, we say so, and we have stopped trying to fix them.**
Parent **3432** was **already** accept-refuse under signed triage; the
Phase 5 sign re-affirms it rather than newly ruling it, and it is **not**
one of the seven the D-128 run covered.

**"Accepted" does not mean fixed, and it does not mean quiet.** It does
**not** mean the seam is solved, aligned, or repaired — it is **not**.
And it does **not** mean we stop reporting the numbers: the **0 of 7**
and the joins D-128 **gave back** (**5** vs D-125, **6** vs D-126) stay
on this page next to the label, exactly as the section above records
them. Accepting a refusal retires the **hunt**, not the **record**.
**Never claim the seams are solved.** None of the eight may be shown as an
**open must-hunt**, as **solved / fixed / repaired**, or as **a D-128
miss** — the zero was pre-registered, and the diagnosis half landed.

**Phase 4 pair — now labelled.** Parents **3272** and **3394** failed for
a **different** reason (the whole-overlap / residual-RMSD class, not the
linker). They are **no longer** open must-hunt. After Phase 4 OPS
(`932292d`, 0 of 2 recovered) and Matt's Phase 4 named-refuse sign, both
are **named refuse / accept-refuse**. See **Addendum D-130-B / D-131**
below for the OPS table and inventory. The Phase 5 eight above are
unchanged.


**What we are not doing next.** There is **no fifth stitching
algorithm**. We are not loosening the **10.0 Å** limit that decides
whether a join counts as honest, we are not moving **W = 32** or
ε = 1e-3, and we are not changing which structure the site serves: the
**served** structure is still the **assembler** (the winner-tile method),
as it has been all along. ⚠ **Scoped by D-139:** the site later did change
which structure it serves — for the recorded PASS **seventeen**, and by
allowlist, not by a new algorithm. **All eight parents named in this
section are excluded from it** and keep the assembler with their
accept-refuse label intact. **D-126 remains the best experimental path
until proven otherwise**, and stays **callable**. Both the **D-127** and
the **D-128** failed rescues **stay disclosed** above — neither replaces
nor softens the other.

**What this addendum does not do.** It does not replace the assembler
story, does not make the long chain one ESMFold pass, does not fill PAE,
does not enter F-004 / the ranking, and is not medical advice. It is not
a re-measurement: every number it names is quoted from the run recorded
at tip `9e65cbf`, out_root `linker_seam_ops_2026-09-05`, and nothing here
ran, queried, or re-derived it.

## Addendum D-130-B / D-131 — Phase 4 residual-RMSD OPS and named refuse

Ruled by **Matt SIGNED Phase 4 named-refuse** (2026-09-05 ~22:32 PT) after
D-130-A OPS at tip `932292d`. Freeze unchanged: served = **assembler**;
gate **10.0 Å**; **D-126** best experimental callable; no RMSD-v2; no
F-004; no auto-flip. ⚠ **Amended in scope by D-139:** `served =
assembler` still holds for **3272 and 3394** — both are accept-refuse and
both are excluded from the flip by name — but it is no longer the whole
picture, because the recorded PASS seventeen are now served **D-126**.
The rest of the freeze stands untouched: **10.0 Å**, no RMSD-v2, no
F-004, **and still no auto-flip**.

### Phase 4 OPS (as recorded)

We ran the Phase 4 **residual-RMSD** path on the signed pair — parents
**3272** and **3394** — at tip `932292d`, out_root
`residual_rmsd_ops_2026-09-05`.

**Rollup as recorded:** PASS **0** / REFUSE **2** / FAIL **0** /
`recovered_of_two` = **0**. Recovering zero of the two was an **allowed
outcome** written before the run.

| parent | refuse reason | notes (as recorded) |
|--------|---------------|---------------------|
| **3272** | `rmsd_irreducible` | floor ≈ **12.63** Å (above the 10.0 Å gate — no rigid superposition holds the join) |
| **3394** | `rmsd_gt_10` | floor ≈ **4.77** Å; achieved RMSD ≈ **13.77** Å; correspondence offset = 0 |

These numbers are **quoted from the recorded run**. Nothing in this
addendum re-ran, queried, or re-derived them.

### What we now call these two joins

Parents **3272** and **3394** are marked **named refuse /
accept-refuse**. In plain words: **these joins do not hold, we say so,
and we have stopped trying to fix them on this path.**

They failed for the **whole-overlap / residual-RMSD** class (not the
linker/seam class that Phase 5 retired). Accepting the refusal retires
the **hunt**, not the **record**: the **0 of 2** and both refuse classes
stay on this page beside the label.

**Accepted does not mean fixed.** It does not mean quiet. Neither parent
may be shown as an open must-hunt, as solved / fixed / repaired, or as
an RMSD-v2 miss — the zero was allowed, and the diagnosis half landed.

### Inventory on the 27 (no silent holes)

After this sign + label:

- **17 PASS** (unchanged): 2817, 2917, 2929, 3027, 3097, 3153, 3188,
  3217, 3320, 3379, 3404, 3454, 3469, 3516, 3541, 3569, 3575
- **10 accept-refuse:** the Phase 5 eight (2938, 2939, 3179, 3190, 3321,
  3368, 3566, 3432) **plus** Phase 4 **3272** and **3394**

**Never claim 27/27 PASS.** Never claim the seams are solved.

### ⚠ "The 27" is the run population, not the volume (D-132 amend, 2026-09-08)

Everything above was measured on the **2026-09-05 Wave1+Wave2 closeout
slice** — **27** parents, Wave1 PASS **10** + Wave2 PASS **17**. Those
figures describe that slice and nothing else, and they are not restated
here.

A **read-only** Fly DB query on **2026-09-08** (parent jobs with tile
children **and** a non-null `protein_analyses.pdb_path`, path shape
`/data/artifacts/{parent_job_id}/structure.pdb` with `pae.json.gz` beside
it) counted **45** unique assembled parents on the volume: the **27**
above **plus 18** more. ⚠ Those 18 are **not** a new persist — they
already carried a stored structure path at inventory time; the
2026-09-05 closeout simply counted the wave, not the volume. The figure
is recorded here **as handed** by owner ops; this file ran no query.

⚠ **None of the OPS runs above touched those 18.** No D-127, D-128 or
Phase 4 number is claimed for them. **Never claim 45/45 PASS** either.
The rental stays **CLOSED** (D-118) — a recount is not a card.

### What we are not doing next

There is **no residual-RMSD-v2** and **no fifth stitching algorithm** in
this addendum. We are not loosening the **10.0 Å** gate, not flipping
served off **assembler**, and not entering F-004. ⚠ **Scoped by D-139:**
served was later flipped off the assembler — for the recorded PASS
**seventeen only**, onto the **existing** D-126 path. Still no sixth
algorithm, still no gate move, still no F-004. **D-126** remains the
best experimental path until proven otherwise. D-127, D-128, and this
Phase 4 OPS disclosure **all stay on the page** — none softens another.

### Provenance

Matt SIGNED Phase 4 named-refuse 2026-09-05 ~22:32 PT. Architect support
on file. OPS tip `932292d` / out_root `residual_rmsd_ops_2026-09-05`.
This addendum ships **no** new ops run and **no** Fly POST by itself.

## Addendum D-139 — which structure you are actually handed

Ruled by **Matt BUILD GO 2026-09-08 ~2:57 PM PT via Emma** — Phase 6 of
the `D-0043` stitch honest-endpoint roadmap. ⚠ Vault `D-0043` is external
numbering, **not** a project decision id.

Everything above this section was written while the answer to *"which of
these paths do I actually download?"* was the same for all 27 parents:
**the assembler**. Four alternative fits ran beside it and none of them
could change the file. That is no longer true, for **seventeen** parents.

### The rule, in one sentence

If a parent is one of the **seventeen** that carry a recorded **PASS**
and **no later named refuse**, the site hands you its **D-126
overlap-confidence Kabsch** structure. **Every other parent — and every
parent outside the 27 — is handed the assembler.**

### The seventeen

2817, 2917, 2929, 3027, 3097, 3153, 3188, 3217, 3320, 3379, 3404, 3454,
3469, 3516, 3541, 3569, 3575.

That is the **17 PASS** list from *"Inventory on the 27"* above, unchanged
and not recomputed here. The other **ten** are the accept-refuse ten — the
Phase 5 eight (2938, 2939, 3179, 3190, 3321, 3368, 3566, 3432) plus Phase 4's
3272 and 3394 — and they keep the assembler **and** keep their labels.

### ⚠ Why seventeen and not twenty-four

D-126's **own** run refused only **three** of the 27 (2939, 3272, 3432),
which leaves 24. Seven of those 24 were later measured as **refused by a
different path**: six on D-128 `seam_jump_gt_10`, and 3394 on Phase 4
`rmsd_gt_10` (floor ≈ 4.77 Å, achieved ≈ 13.77 Å). **24 − 7 = 17.**

Serving a D-126 pose for a parent D-128 measured as `seam_jump_gt_10`
would mean handing out a structure we hold a recorded measurement
**against**. So the gate is *PASS **and** no later named refuse*. The 24
is written here because it is the number the next reader will reach for
first, and it is the wrong one.

### It takes four yeses, and any one missing means assembler

1. the parent is in the seventeen;
2. a `confidence_kabsch/{parent}/` tree is on disk;
3. that tree's provenance says the run **accepted** this parent;
4. `stitched.pdb` is actually in it.

**Artifacts alone can never flip a parent.** A tree appearing on disk, a
PR merging, or a pass count improving are none of them authority — the
seventeen are, and they are written out. When a parent is not flipped,
the page says **which** of the four failed: `not_in_pass_subset`,
`no_confidence_kabsch_artifacts`, `confidence_kabsch_refused`, or
`no_confidence_kabsch_success_pdb`. "Assembler" without the reason cannot
tell *never eligible* from *the run refused it*.

### ⚠ Right now, in this repository, that count is ZERO

There is **no** `confidence_kabsch/` tree committed to this repository —
the D-126 OPS output lives under an ops `out_root` on the volume and was
never checked in. So **seventeen parents are eligible and zero are
flipped**: every one of them resolves to the assembler with the reason
`no_confidence_kabsch_artifacts`. That is the fail-closed branch working,
and it is stated first because it is the number that would otherwise
embarrass this page.

### What comes with the bytes

The **pLDDT** and **PAE** beside a served D-126 structure come from the
**same** tree. D-126 runs its own winner-tile pass, so its residue picks —
and its confidence array — can differ from the assembler's; colouring
D-126 coordinates with assembler confidence would be a new dishonesty
invented by this change. Each falls back on its own if the tree does not
carry it. And a flipped parent downloads as
**`stitched_confidence_kabsch.pdb`**, never `stitched.pdb`: two files with
one name and different coordinates is a bug that outlives the tab.

### What this does not do

**No threshold moved.** The **10.0 Å** refuse gate and the three refuse
reasons are untouched, and nothing here was re-run, re-fit or
re-measured — this addendum ships **no** ops run and **no** Fly POST.
There is **no auto-flip**, **no sixth algorithm**, **no D-127 piecewise
revival**, **no RMSD-v2**, **no linker-v2**, and **no F-004**. The
accept-refuse ten stay accept-refuse; **3432 is not re-opened**; the
Phase 4 hunt stays **closed**; the rental stays **CLOSED**. No claim of
any kind is made about the 18 parents outside the 27 — no OPS run ever
touched them, and none is eligible.

**And a served D-126 structure is a recorded outcome, not a solved
join.** Seventeen served parents are **seventeen recorded outcomes**.
**Never claim 27/27 PASS. Never claim the seams are solved.**

## The rental is CLOSED

The rented GPU that folded these tiles is done. Hold-48 rental is **CLOSED**
(pod Terminated, 2026-09-05; **D-118**). Do not treat this page as a request
to rent another card. Do not Deploy. Do not emit.

---

## What this file is not

- Not a licence to call the joins scientifically solved, or to treat a
  Kabsch-path, D-127-path, or D-128-path file as the default served PDB.
  ⚠ **The D-126 path is served for the seventeen named in the D-139
  addendum, and for no one else** — that is an allowlist, not a default,
  and it is not a claim that those seventeen are solved.
- Not a licence to run a live restitch of the 27, or to re-open rental.
  The D-127 and D-128 ops figures above were **handed to this file as
  recorded**; nothing here ran, queried, or re-measured them.
- Not a licence to raise the **10.0 Å** refuse gate, to reopen a trim
  loop, or to treat 0-of-3 or 0-of-7 recovered as a reason to move
  either — nor to report either zero without the parents the same run
  gave back.
- Not a licence to re-open **3432**, which stays accept-refuse.
- Not a licence to re-open **3272 / 3394** as must-hunt, or to treat
  accept-refuse as solved. Both are **named refuse / accept-refuse**
  after Phase 4 OPS 0/2 and Matt's named-refuse sign (D-130-B / D-131).
- Not a licence to open **RMSD-v2** without a **new** explicit Matt GO
  and new evidence.
- Not a licence to ship an **accept-refuse** label without the recorded
  zero beside it (**0 of 7** for Phase 5 / D-128 and the **5 / 6**
  give-back; **0 of 2** for Phase 4 / D-130). The label is *why we stopped*;
  those numbers are *what we found*.
- Not F-004 / ranking ingest.
- Not the ADC-B `/adcs` page (D-122 already shipped that on `main`). Not the Nectin-4 Doc.
- Not a new science number. Window **1656** / overlap **128** are D-111's.
  Seam **~88.76 Å** is the IGF2R measurement D-117 / D-118 already recorded.
- Not a rewrite of #229. Phase 2 review UI stays merged.
