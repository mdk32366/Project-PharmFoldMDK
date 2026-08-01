# D-075 (pre-registered) — The pLDDT-ablation and popularity-matched control: does the structural axis survive without confidence-derived features?

> **Number — RESOLVED 2026-08-01.** Drafted as `F-008` (the snapshot's most recent finding was
> F-007); the live log was ahead and **F-008 was already taken** by the two-precision confound
> (`754e58f`). Renumbered **D-075** on landing — and re-typed as a **decision**, not a finding, since
> it rules a design and freezes an interpretation before a result exists (D-065's shape; its *result*
> becomes a later F-entry). The authoritative entry is `docs/README.md` §D-075. **This spec is
> written BEFORE the refit runs.** Its
> purpose is to fix the test and both interpretations in advance, so the outcome cannot be
> narrated after the fact. Log leads code; interpretation leads result.
>
> **⚠ RECONCILIATION — read with the D-075 order.** After this spec was drafted, the Planner found
> that **D-065 already exists** — it ruled two feature-drop ablations (`no_plddt`, `plddt_only`).
> **D-075 is therefore an EXTENSION of D-065, not a freestanding experiment.** The authoritative,
> reconciled version is `ORDERS-Code-2026-08-01-D-075-ablation.md`, which adds to D-065 exactly two
> things D-065 lacked: the confidence-blind *replacement* feature (`geom_proxy`) and the
> popularity-matched control. Where this spec and the order differ, **the order governs.** Confirm
> D-065's status (merged? run?) before executing either — the order's §0 spells out the branches.
>
> **Provenance of the challenge:** the Grok second-opinion (adversarial review, staged
> `GROK-PROMPT-second-opinion.md`) escalated the pLDDT-attention confound from an open caveat
> (F-004 caveat b/c) to a potentially load-bearing objection, and named the exact test F-004 never
> ran. This addendum runs it. The scores Grok assigned are set aside as noise; the *question* is
> the sharpest external challenge the project has received and is treated as such.

---

## §0 — The objection, stated at full strength (steelman)

The positive label is "attempted as an ADC target" = **research history.** Two of six features
(mean pLDDT, membrane-proximal pLDDT) are derived from ESMFold **confidence.** ESMFold confidence
tracks training-data representation (MSA depth / structural homologs) → which tracks research
attention → which tracks having-been-attempted-as-an-ADC. **The label and two features may share a
common cause.** Therefore the modest enrichment of the 12 positives (LOO median 0.607, 8/12 > 0.5)
is *exactly what the null "attention → higher pLDDT → higher rank" predicts on its own* — with no
ADC-relevant structural information required.

F-004's near-zero Spearman vs. the comparator does **not** exonerate this: the comparator takes only
a handful of discrete values across the cohort and is itself not a clean attention proxy. **The
honest pre-test status is therefore NOT "orthogonal but unproven." It is "orthogonal but unproven,
AND the attention-artifact explanation has not been excluded."** This addendum exists to exclude it,
or to fail to — and to pre-register both readings.

---

## §1 — The structural axis under test (frozen before refit)

The refit tests whether a **confidence-blind** structural axis carries the signal. Feature set:

**KEEP (pure geometry, no pLDDT anywhere in derivation):**
1. ECD length
2. Radius of gyration (Rg)
3. Normalized SASA
4. Largest-patch fraction

**REMOVE (pLDDT-derived):**
5. Mean pLDDT
6. Membrane-proximal pLDDT

**REPLACE the lost information with one pLDDT-free proxy:**
7. **Membrane-proximal SASA** — solvent-accessible surface computed on the raw coordinates over the
   same membrane-proximal residue window that feature 6 used, but measured **from geometry alone.**

### §1.1 — Hard constraint on the proxy (its own test, red-then-green)

**The proxy must not read the pLDDT / B-factor column at any point.** No confidence weighting, no
pLDDT-based residue filtering before measuring accessibility, no pLDDT-derived window selection.
The window is defined by the same topological/coordinate rule feature 6 used, then SASA is measured
on coordinates only.

- **Test (must go red first):** a fixture where two structures share identical backbone coordinates
  but different pLDDT columns must yield **identical** membrane-proximal SASA. If the proxy ever
  reads confidence, this fixture separates them and the test bites. Confirm it reds on a deliberately
  contaminated implementation before greening on the clean one.
- **Rationale:** the entire value of the ablation is a clean confidence-blind axis. A proxy that
  leaks pLDDT proves nothing and would be worse than omitting the replacement, because it would look
  clean while being contaminated — the F-004 §7 "function exists ≠ function runs" failure class, one
  level more insidious.

### §1.2 — Freeze discipline

The proxy definition, its residue window, and its extraction code are **frozen before the refit
runs.** No inspecting the refit result and then adjusting the proxy — that reintroduces the exact
researcher-degree-of-freedom pre-registration removes. Proxy frozen → refit → interpretation per §3,
in that order, no loop.

---

## §2 — The two runs

### Run A — the pLDDT-ablation (primary)

Refit the **same L2 logistic regression, same nested-CV λ selection, same LOO percentile
mechanic** (D-041 / D-060) on the 5-feature confidence-blind set {1,2,3,4,7}. Recompute:
- the 12 LOO percentiles, their median, and count above 0.5;
- the head-to-head vs. the Kathad comparator on the same 8 overlapping targets;
- Spearman(structural_ablated, comparator).

**Nothing else changes** — same 12 positives, same floor, same folds, same RNG discipline. Only the
feature set differs, so any change in result is attributable to removing confidence.

### Run B — popularity-matched control (harder, sensitivity check)

Grok's stronger demand: show the geometric signal is not literature density. Two attention proxies,
run as a **sensitivity pair** (not one blessed number):

- **B1 — PDB-presence** (binary): does each target have an experimentally solved structure in the
  PDB as of a frozen date? Source: RCSB PDB / UniProt cross-reference. The strong proxy — directly
  the "structural homolog in training data" mechanism, checkable, low-noise.
- **B2 — publication count** (continuous): literature density per target (e.g. PubMed hits for the
  gene symbol, frozen query + date). Noisier, but catches attention without a solved structure.

**The control:** stratify or covariate-adjust the ranking so positives and negatives are matched on
the attention proxy, then test whether the structural (ablated) ranks still enrich. Run against B1
and B2 separately.

- **Sequencing:** Run A first. It is cheaper and it is the load-bearing test — if the confidence-blind
  axis already collapses, B is moot (the signal was pLDDT). If A survives, B is what answers the room.

---

## §3 — Pre-registered interpretations (fixed before the numbers exist)

**Both outcomes are recorded now so neither can be spun later.**

### If Run A SURVIVES (ablated axis still enriches, roughly comparable to the 6-feature result):
- The attention-artifact explanation is **substantially weakened**: the signal does not depend on
  confidence-derived features. F-004's "orthogonal but unproven" strengthens toward "orthogonal, not
  a confidence artifact, still underpowered at n=12."
- Then Run B decides how much further it goes. If the signal survives popularity-matching on **both**
  B1 and B2, the attention critique is largely answered and you walk into any room with Grok's sinking
  question **already answered.** Survives one but not the other → an informative split, reported as
  such, not hidden.

### If Run A COLLAPSES (ablated axis is no better than chance):
- **This is a real, honest, publishable finding, not a failure:** the F-004 enrichment was carried
  by the pLDDT features, and once confidence is removed the pure-geometry axis shows nothing at n=12.
- The headline changes accordingly: *"the modest structural enrichment is not separable from ESMFold
  confidence, which is itself confounded with research attention; we cannot claim a
  confidence-independent geometric signal at this sample size."* That is a **stronger** contribution
  than an unexamined 0.607, because it is the result of running the test the critic named — and it is
  far better found by us than by the room.
- It also sharpens the future-work case for a better label (§4 of the pre-work / the false-negative
  set), because it shows attempt-history is too entangled with confidence to serve as a clean label.

**Either way the project is stronger.** A survival hardens the claim; a collapse converts a hidden
weakness into a stated finding and redirects the work. The only losing move is not running it.

---

## §4 — What this does and does not touch

- **F-004 stands as the record of the 6-feature pre-registered result.** D-075 is an addendum that
  tests its most serious confound — it does not overwrite F-004, it interrogates it. Both live in the
  log; the relationship (D-075 tests F-004 caveat b) is stated.
- **No deployed surface changes** until a result exists and goes through the gate. If the headline
  changes (collapse case), the UI's result framing updates from `/api/ranking` derivation like any
  other result change — not a silent edit.
- **The scorer arc, the ranking-table columns, the fold plan (D-072)** are untouched. This is a
  refit on existing folded structures + two attention proxies; it folds nothing new.

---

## §5 — Definition of done

- [ ] Number confirmed against `docs/README.md`; renumber if D-075 taken.
- [ ] Membrane-proximal-SASA proxy defined, window frozen, **§1.1 red-then-green test passing**
      (contaminated impl reds; clean impl greens; identical-backbone/different-pLDDT fixture proves
      confidence-blindness).
- [ ] Proxy frozen **before** Run A executes — verified, not assumed.
- [ ] Run A: 5-feature refit, LOO percentiles + head-to-head + Spearman recomputed, both interpretations
      from §3 available before reading the numbers.
- [ ] Run B1 (PDB-presence) and B2 (publication count) proxies frozen with source + date; matched-control
      run; split reported honestly if it splits.
- [ ] Result recorded as D-075 with the §3 interpretation that fired, through the gate, no silent edit.
- [ ] Deck + lit review updated to reflect the true post-ablation status (survival or collapse).
