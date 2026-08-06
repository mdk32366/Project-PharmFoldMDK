# CORRECTION — 2026-08-06 — `no_topology` does not mean "no topology annotation"

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority. Check the `### D-NNN` / `### F-NNN` header, not a reference to it.

> **Corrects the band vocabulary used in `e19b0bf` and in every span report of 2026-08-06.**
> ⚠ **The artifacts are not regenerated and the filter is not changed** — the counts are correct for
> what they measured; what was wrong is what everyone took them to mean, including me.
>
> **Found by the Planner reading `scripts/ecd_lengths.py` instead of theorising about UniProt.**
> Verified by Code against the 5,009 cached entry JSONs, no network.

---

## §1 — What the band actually measures

`scripts/ecd_lengths.py:194-196`:

```python
if feat.get("type") != "Topological domain":
    continue
description = feat.get("description", "") or ""
if "extracellular" not in description.lower():
    continue
```

⚠ **`no_topology` means "no `Topological domain` feature whose description contains the substring
`extracellular`."** It does **not** mean "no topology annotation," and the two were used
interchangeably all day — in the span reports, in the band split, and in two hypotheses built on top.

UniProt annotates topological domains with a controlled vocabulary. `Extracellular` is one term.
`Cytoplasmic` is another. So is **`Lumenal`** — and an ER, Golgi, endosomal, lysosomal or vesicular
membrane protein has its non-cytoplasmic face annotated `Lumenal`. **The filter drops every one of
them, by construction.**

## §2 — Measured over the cached entries, no network

**ANNEX (non_surface), 1,858 `no_topology` rows:**

```
has ANY Topological domain feature   752  (40.5%)
Transmembrane but NO Topological     734
neither                              372

   1177  Cytoplasmic          204  Mitochondrial intermembrane     13  Peroxisomal matrix
    843  Lumenal              166  Mitochondrial matrix            10  Exoplasmic loop
     32  Vesicular             28  Nuclear                          6  Peroxisomal
     27  Perinuclear space      1  Mother cell cytoplasmic
```

**⚠ SURFACE, 448 `no_topology` rows — the surface class is leaking too:**

```
has ANY Topological domain feature   121  (27.0%)
Transmembrane but NO Topological     197
neither                              130

    367  Cytoplasmic           20  Vesicular            3  Lumenal, melanosome
    239  Lumenal                8  Vacuolar             1  Intragranular
     23  Lumenal, vesicle       7  Mitochondrial matrix 1  Nuclear
     11  Mitochondrial intermembrane                    1  Exoplasmic loop
```

**265 `Lumenal`-family domains sit inside the SURFY *surface* class**, currently counted as having no
span.

## §3 — What this overturns

1. **The annex's 84.8% is largely an instrument artifact**, not a finding about UniProt's coverage of
   the membraneome. ⚠ **The F-016 collision dissolves**: the table can be the whole membraneome, these
   can be properly annotated membrane proteins, and they still read `no_topology` under a filter
   looking for one word.

2. **The topology-coverage hypothesis is doubly unsupported** — refuted by the 1,858 counterexample
   (SURFY scored them), and built on a measurement that was not measuring what it was said to measure.

3. ⚠ **Both foldable counts are floors, not totals.** `332` (annex) and `2,352` (surface) count only
   proteins with an explicitly *extracellular* span. The true numbers are unknown and larger.

4. ⚠ **The lumenal bridge is no longer a claim about pipeline reachability.** *"Same fetch, same
   slice, same fold — the pipeline scores them unmodified"* is **wrong**: the pipeline as it stands
   **cannot see them at all.** It is one substring from testable, which is better news than the
   version that was written, and a correction to three artifacts.

## §4 — ⚠ But the population splits THREE ways, and only one is a substring away

```
                     recoverable by      genuine annotation      no membrane
                     widening the        gap (TM present,        evidence
                     vocabulary          no TD at all)           at all
annex     1,858  =        752        +          734          +       372
surface     448  =        121        +          197          +       130
TOTAL     2,306  =        873        +          931          +       502
```

⚠ **"One substring away from testable" is right for 873 of them. The other 1,433 need a different
answer** — 931 are membrane proteins whose faces UniProt has not labelled, and 502 carry no membrane
evidence at all. Widening the filter does not recover either group, and reporting the fix as though
it recovers 2,306 would be the same over-claim in the opposite direction.

## §5 — What is NOT done here, and why

⚠ **The filter is not changed.** Widening `"extracellular"` to a vocabulary is a design decision that
**redefines what an ECD is for the entire census** — and D-079's bands, the 82-target cohort, F-004,
and every span in `data/census/` were measured under the current definition. A number that moves
because a definition moved is not a new measurement.

**It wants its own pre-registration, before the number changes**, stating which vocabulary terms count
as non-cytoplasmic and what the resulting count is expected to do. That is an owner ruling and is not
taken here.

⚠ **The artifacts are not regenerated.** `spans_surface.csv` and `spans_annex.csv` are correct for
what they measured, carry per-record provenance, and are cited by this correction. **Rewriting them
to a new definition would destroy the before-state that makes the correction checkable.**

**The unclassified diagnostic does not run.** Its hypothesis is dead and its reading is void.

## §6 — The reporting rule this earns

⚠ **A band name is a claim, and `no_topology` made a claim the filter could not support.** The band
should have been called what it measured — *no extracellular-described topological domain* — and the
gap between the two is where two hypotheses and a 6.7× candidate count went wrong.

**Numbered `F-025`** on the owner's 2026-08-06 ruling — it beat three other claimants because it has a
live consequence in a committed artifact, a wrong denominator in the census, and it gates the manifest.

---

# ADDENDUM — 2026-08-06, after the owner's biological ruling and the §3 gate

⚠ **This addendum corrects the `873` in §4 above, downward, to `659`.** §4 counted *domain
descriptions*, lexically. The owner ruled the vocabulary question is **biological, not lexical**, and
under that ruling the count is smaller. The original figure stays on the page.

## §7 — The per-term ruling

⚠ **The terms do not all mean the same thing, and "anything not cytoplasmic" is the wrong widening.**
Secretory-pathway faces traffic to the plasma membrane. Mitochondrial, peroxisomal and nuclear faces
do not — and F-011's argument is specifically about the secretory pathway. A filter widened to
`not cytoplasmic` would recruit domains that **cannot be ADC targets on any mechanism**, and would
inflate the atlas story exactly where it is most tempting.

| Ruled REACHABLE | Ruled NOT REACHABLE | Ruled CYTOPLASMIC |
|---|---|---|
| `Extracellular` · `Lumenal` · `Lumenal, vesicle` · `Lumenal, melanosome` · `Vesicular` · `Vacuolar` · `Perinuclear space` · `Intragranular` · `Exoplasmic loop` | `Mitochondrial intermembrane` · `Mitochondrial matrix` · `Nuclear` · `Peroxisomal` · `Peroxisomal matrix` | `Cytoplasmic` · `Mother cell cytoplasmic` |

Three of these are judgment calls and are recorded as such:

- **`Perinuclear space` → reachable.** It is continuous with the ER lumen, so it is secretory-pathway
  space. ⚠ **And it is a trap**: the string contains `nuclear`, so a widening implemented as
  "not cytoplasmic **and** not nuclear" silently drops all 27. The order of tests is load-bearing.
- **`Vacuolar` → reachable.** In human entries this is the lysosomal/endosomal lumen.
- **`Exoplasmic loop` → reachable.** ⚠ A **third** word for the same face — it would have been missed
  by a widening that searched for *lumenal*, and it is the term that hits one of the 82.

**Every term present in the census is ruled.** No description fell outside the table.

## §8 — The split re-measured PER PROTEIN under that ruling

⚠ **The unit is the protein, not the domain.** A protein with both a `Cytoplasmic` and a `Lumenal`
face is one recoverable protein, not two domains.

```
                                         surface    annex    TOTAL
RECOVERABLE — has a reachable face           106      553      659   ← was 873, lexically
unreachable face only (mito/perox/nuc)         2      143      145
cytoplasmic-only topological domain           13       56       69
TM present, no topological domain at all     197      734      931
no membrane evidence at all                  130      372      502
                                             ---     ----     ----
                                             448    1,858    2,306
```

Reconciles to §4: `106 + 2 + 13 = 121` surface with any TD ✅ · `553 + 143 + 56 = 752` annex ✅.

⚠ **214 proteins that the lexical count called recoverable are not.** 145 have only a face that never
reaches the cell surface — the annex's are `Mitochondrial intermembrane` 126, `Mitochondrial matrix`
89, `Peroxisomal matrix` 6, `Peroxisomal` 5, `Nuclear` 1; the surface class's are exactly two,
**Q8WWI5** and **Q6J4K2**. The other 69 have a topological domain annotated only `Cytoplasmic`.

**931 remains the sharper problem** and widening does not touch it: a protein UniProt says crosses a
membrane, whose faces nobody has labelled.

## §9 — ⚠⚠ THE §3 GATE READS **AFFECTED**. THE 82 ARE TOUCHED.

**All 82 are in the cache; 0 fetches; 82/82 answered offline.** ⚠ **3 of the 82 carry a topological
domain the filter drops**, and all three are `reachable`:

| accession | label | committed | under the ruled widening |
|---|---|---|---|
| `P11717` | **IGF2R** | `largest_span_aa` **empty**, `n_extracellular_spans` 0 | `Lumenal` → **2,264 aa** |
| `O15455` | **TLR3** | `largest_span_aa` **empty**, `n_extracellular_spans` 0 | `Lumenal` → **681 aa** |
| `Q9NV96` | **TMEM30A** | `largest_span_aa` **empty**, `n_extracellular_spans` 0 | `Exoplasmic loop` → **255 aa** |

⚠ **And the consequence is not a feature value — it is a ROUTING FLIP.** `core/manifest.py:239-251`
branches on `largest_span_aa` being numeric. An empty span means `boundary_method="whole"`,
`held_out=True`, fold the whole sequence. So under the widening all three move:

```
boundary_method   whole      → sliced_ecd     (all three)
disposition       held_out   → ranked         (all three)
folded molecule   2,491 aa   → 2,264 aa   IGF2R
                    904 aa   →   681 aa   TLR3
                    361 aa   →   255 aa   TMEM30A
tier              rental     → rental (over_local_ceiling)   IGF2R, TLR3
                  local      → local                          TMEM30A
coverage          82 = 67 ranked + 13 held_out + 2 excluded
                     → 82 = 70 ranked + 10 held_out + 2 excluded
```

⚠ **Feature 1 is `ecd_length = len(plddt)`** (`core/features.py:422`) — the length of *what was
actually folded*. For these three that is the **whole-sequence** length. The committed features are
not wrong under their own definition; they are measured under a definition that is about to move, on
a **different molecule** from the one the widened definition names. That is precisely the
boundary-method incomparability D-021 held them out for, and it is why the gate is decisive.

⚠ **IGF2R is the finding inside the finding.** It is `Lumenal` because it cycles through endosomes —
**it is a member of the exact population F-011's lumenal bridge is about, and it has been sitting
inside the 82 all along**, invisible, routed to a whole-sequence fold that then failed
(D-058 Addendum 2 §1).

### What the AFFECTED verdict binds, per the owner's §3

⚠ **The 82 stay frozen under the ORIGINAL definition, permanently.** No re-slice, no re-fold — F-008
forbids touching the reported cohort, and re-folding three targets onto different molecules to make
a definition apply retroactively would be fitting the cohort to the ruling.

⚠ **The census uses the widened definition**, once pre-registered. **Two definitions now exist, both
named, and no artifact may compare a span under one to a span under the other without saying which
produced it.** Every artifact naming a span states its definition.

⚠ **Nothing is renamed and no filter is changed in this commit.** The `no_topology` →
`no_extracellular_span` rename is right and is D-074's second clause, but the gate came back
AFFECTED and the owner's instruction was that nothing changes until it does. It is held for the
ruling, not forgotten.

⚠ **Task 4 stays gated.** The manifest freezes the foldable population with a seed, and freezing a
population defined by a filter narrower than its name is not recoverable once the crank turns.
