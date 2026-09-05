# How we fold long proteins: tiles, glue, and an assembler

*An eighth-grade write-up for the owner. Decision: [`D-121`](README.md)
(confirm the `### D-121` header exists before citing). Parents: **D-118**
(honesty — rental closed, assembler not Kabsch) and **D-120** (Phase 2 review
UI). #229 stays merged; this file does not reopen it.*

Facts come from entries that already exist. If those entries did not say it,
this file does not say it. ⚠ **Not a Kabsch GO. Not F-004. Not `/adcs`.**

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
A later Kabsch / restitch job is parked until the owner says GO.
This write-up is not that GO. There is no button that heals the join.

## The rental is CLOSED

The rented GPU that folded these tiles is done. Hold-48 rental is **CLOSED**
(pod Terminated, 2026-09-05; **D-118**). Do not treat this page as a request
to rent another card. Do not Deploy. Do not emit.

---

## What this file is not

- Not a licence to run Kabsch, restitch, or re-open rental.
- Not F-004 / ranking ingest.
- Not the ADC-B `/adcs` page (D-122 already shipped that on `main`). Not the Nectin-4 Doc.
- Not a new science number. Window **1656** / overlap **128** are D-111's.
  Seam **~88.76 Å** is the IGF2R measurement D-117 / D-118 already recorded.
- Not a rewrite of #229. Phase 2 review UI stays merged.
