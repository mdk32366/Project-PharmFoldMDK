# How we fold long proteins: tiles, glue, and an assembler

*An eighth-grade write-up for the owner. Decision: [`D-121`](README.md)
(confirm the `### D-121` header exists before citing). Parents: **D-118**
(honesty — rental closed, assembler not Kabsch) and **D-120** (Phase 2 review
UI). #229 stays merged; this file does not reopen it.*

Facts come from entries that already exist. If those entries did not say it,
this file does not say it. ⚠ **Not a restitch run of the 27. Not F-004. Not `/adcs`.**
A D-125-B addendum names what a Kabsch-path restitch does and does not.
A D-126-B addendum names what weighted / trimmed Kabsch does and does not
versus the assembler and versus D-125.

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

## The rental is CLOSED

The rented GPU that folded these tiles is done. Hold-48 rental is **CLOSED**
(pod Terminated, 2026-09-05; **D-118**). Do not treat this page as a request
to rent another card. Do not Deploy. Do not emit.

---

## What this file is not

- Not a licence to call the joins scientifically solved, or to treat a
  Kabsch-path or D-126-path file as the default served PDB.
- Not a licence to run a live restitch of the 27, or to re-open rental.
- Not F-004 / ranking ingest.
- Not the ADC-B `/adcs` page (D-122 already shipped that on `main`). Not the Nectin-4 Doc.
- Not a new science number. Window **1656** / overlap **128** are D-111's.
  Seam **~88.76 Å** is the IGF2R measurement D-117 / D-118 already recorded.
- Not a rewrite of #229. Phase 2 review UI stays merged.
