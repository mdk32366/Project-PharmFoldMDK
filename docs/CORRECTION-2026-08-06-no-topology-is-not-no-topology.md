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

**Recorded as unnumbered**, pending the owner's ruling on findings numbering. Three others are queued.
