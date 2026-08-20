# SPEC — the peptide-backbone graphic, and the chemistry it must get right

> **COMMITTED 2026-08-20 as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file is a SPEC for the owner to rule, edit or
> reject; it is not itself authority and nothing in it is built.
>
> ⚠ **Landing header added by Code at landing.** The paste carried none and
> `tests/test_docs_landing_headers.py` reddened. ⚠⚠ It sits ABOVE the first `## §` marker and
> therefore OUTSIDE the AUTHORED-SHA256 range, which was re-verified after the insertion.

**AUTHORED-SHA256** (range: **first `## §` header → EOF**, anchored to line starts, **SECOND
occurrence of the marker**) = `1e506ed9bb059897807901f26d6bb3c59e85ad2bb35742945ab5031d245df78a`
**bytes** = `4037`

> ⚠ **A SPEC, not a decision and not a ruling.** Nothing is built. **For the owner to rule, edit or
> reject.** Landing header **above** the first `## §` marker, outside the hash range.

---

## §0 — ⚠⚠ The correction that motivates the spec

**The request was for *"a string of amino acids linked by H₂O molecules."*** ⚠⚠ **Peptide bond
formation is a CONDENSATION reaction: the residues join DIRECTLY into a C–N amide bond, and one H₂O
is EXPELLED.** **Water is the by-product, not the linker.**

⚠ **Recorded because a graphic showing residues linked BY water would be spotted instantly by any
biology-literate visitor** — **on a project whose flagship paper argues another group's rigour is
overstated.** **The idea is right; the arrow points the other way.**

---

## §1 — What it must show

- **The backbone repeat `N–Cα–C`**, three atoms per residue, ⚠ **and the peptide bond drawn PLANAR**
  — the C–N bond has partial double-bond character and does not rotate. **A diagram showing it as a
  free hinge teaches the wrong thing about why folding is constrained at all.**
- **Side chains hanging off the α-carbons**, distinguishable but not individually labelled.
- ⚠ **The condensation shown ONCE, at one junction**: `–COOH` + `H₂N–` → `–CO–NH–` **+ H₂O leaving.**
  **Once, not at every bond** — the point is made by one instance and obscured by twelve.
- **N-terminus and C-terminus marked**, because ⚠ **every span coordinate in this project is
  N-to-C and a reader needs the direction.**

## §2 — ⚠⚠ What makes it earn its place rather than decorate: COLOUR THE BACKBONE BY pLDDT

**The same chain, tinted per residue by the model's confidence.**

- ⚠⚠ **`mean_plddt` stops being a bare number.** **A reader sees WHERE the model is unsure, not just
  that it averages 61.38.**
- ⚠ **A 5-residue span and a 400-residue span must LOOK different at a glance.** **`F-048`'s 58 are
  the case this exists for** — `Q9ULH0` is **five residues** with `mean_plddt 61.38`, **and a mean
  over five residues is a different object from a mean over five hundred wearing the same label.**
- ⚠⚠ **BELOW SOME LENGTH, SHOW THE PER-RESIDUE VALUES INSTEAD OF A MEAN.** **At five residues a human
  can read all five.** *Principle 11 inverted: correctness stops being observable past what a person
  will read — and here, it starts being observable.* **The threshold is a stated parameter, not a
  default.**

## §3 — ⚠ What it must NOT do

- ⚠⚠ **It must not imply ESMFold folds by chemistry.** **The model has no energy function and
  simulates nothing** — it maps sequence to coordinates. **A graphic implying a physical folding
  process would be a confident wrong answer about the instrument.** **`D-094` applies: this is an
  educational surface.**
- ⚠⚠ **It must not present pLDDT as accuracy.** **It is the model's PREDICTION OF ITS OWN
  lDDT-Cα** — a second head, same weights, same forward pass. ⚠ **`D-039` records that calibration is
  not established for these targets, and the colour scale must not imply otherwise.**
- ⚠ **It must not become a structure viewer.** **That is 3Dmol's job** — and `PREWORK-2026-08-19` §5c
  records that viewer **failing live with a `200` that means `404`, still unreported.** **A teaching
  diagram beside a broken viewer must not be mistaken for the structure.**
- ⚠ **No ratio, no score, no rank.** **It renders a chain and a confidence, nothing derived.**

## §4 — ⚠ Deliberate absences, named so they read as choices

**Not shown: hydrogen bonds · secondary structure · solvent · charge · anything 3-D.** ⚠⚠ **This is a
1-D chain with a colour channel.** **The moment it implies a fold, it competes with the viewer and
loses.**

## §5 — What the owner rules

1. **Build it, or not.**
2. ⚠ **The length threshold below which per-residue values replace the mean** — stated parameter.
3. **The colour scale, and whether it carries the `D-039` calibration caveat in frame or in a
   tooltip.** ⚠ **`D-094` says mount precondition, which argues for in-frame.**
4. ⚠ **Where it mounts** — census pages, cohort pages, or both. **`F-048`'s 58 are census rows.**
