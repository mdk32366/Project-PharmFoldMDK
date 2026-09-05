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
later nice-to-have.

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
structure.

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
the served PDB is still the assembler one. It does not overwrite the
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
can change that — never a pass count.

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

## The rental is CLOSED

The rented GPU that folded these tiles is done. Hold-48 rental is **CLOSED**
(pod Terminated, 2026-09-05; **D-118**). Do not treat this page as a request
to rent another card. Do not Deploy. Do not emit.

---

## What this file is not

- Not a licence to call the joins scientifically solved, or to treat a
  Kabsch-path, D-126-path, or D-127-path file as the default served PDB.
- Not a licence to run a live restitch of the 27, or to re-open rental.
- Not a licence to raise the **10.0 Å** refuse gate, to reopen a trim
  loop, or to treat 0-of-3 recovered as a reason to move either.
- Not F-004 / ranking ingest.
- Not the ADC-B `/adcs` page (D-122 already shipped that on `main`). Not the Nectin-4 Doc.
- Not a new science number. Window **1656** / overlap **128** are D-111's.
  Seam **~88.76 Å** is the IGF2R measurement D-117 / D-118 already recorded.
- Not a rewrite of #229. Phase 2 review UI stays merged.
