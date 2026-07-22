### D-027 — The scorer's feature set, fixed before fitting; and the extractor that computes it
- **Date:** 2026-07-22
- **Status:** **Proposed**
- **Numbering note:** drafted as D-026, renumbered to D-027 when the Builder claimed D-026 for
  the enqueue step. Recorded because a renumbered entry is otherwise indistinguishable from a
  misfiled one.
- **Context:** D-015 §3 ruled the scorer — *a learned model over structure-derived features,
  fit against Group B* — and named four features: **pocket geometry, surface accessibility,
  epitope-region pLDDT, ECD size/shape**. It then imposed a pre-registration condition it did
  not itself discharge:

  > **Feature count fixed before fitting**, and recorded in this entry when chosen. Growing the
  > feature set after seeing results is how 22 positives get overfit.

  That count has never been recorded. Until it is, the pre-registration is incomplete and any
  fit is unfalsifiable in the specific way D-015 §3 was written to prevent — because "we used
  the structural features" can absorb any number of additions after the fact.

  `docs/TDD_v3_ADC_Focused.md` **predates D-015 and does not specify feature computation.** It
  names `adc_suitability_score` and `surface_accessibility_notes` as schema fields and
  describes pocket identification as a product capability, but contains no method. So this is
  open, not a restatement.

  **Provenance of this entry's scope (D-016).** Before drafting, the Planner proposed an
  alternative framing — a composite structural axis with the ranking target left open — over
  several exchanges. **That framing contradicted D-015 §3, which had already ruled the scorer,
  named the four features, and pre-registered the evaluation.** The error was inferring what
  the log was building toward rather than reading what it says; it is the same class as the
  three errors recorded in `docs/PREWORK-2026-07-22.md`, and the only one that a single
  existing entry would have prevented outright. Recorded here because this entry's *narrowness*
  is the finding: **the open question was never "what should the scorer rank by," it was only
  "how many features, computed how."**

  **What the fold actually yields** (`worker/runner.py`, `FoldResult` / `write_artifacts`):
  `structure.pdb`, per-residue `plddt` (0–100, rescaled), and `pae` when the model returns it.
  Every feature below must be computable from those three artefacts plus the D-023 manifest
  row. **A feature that needs anything else is out of scope for this entry**, because it would
  need a data source the project has not ruled.

---

- **Decision — the feature set is SIX features, fixed as of this entry:**

  | # | Feature | Computed from | Which D-015 §3 name it discharges |
  |---|---|---|---|
  | 1 | **ECD length** (residues folded) | manifest row | ECD size/shape |
  | 2 | **Radius of gyration**, normalised by length | `structure.pdb` CA coords | ECD size/shape |
  | 3 | **Mean pLDDT over the folded ECD** | `plddt.json` | epitope-region pLDDT |
  | 4 | **Membrane-proximal pLDDT** — mean over the C-terminal 25% of the ECD | `plddt.json` + manifest boundary | epitope-region pLDDT |
  | 5 | **Solvent-accessible surface area**, normalised by length | `structure.pdb` | surface accessibility |
  | 6 | **Largest contiguous accessible surface patch**, as a fraction of total SASA | `structure.pdb` | pocket geometry + surface accessibility |

  **Six, and the count is now fixed.** Adding a seventh after any fit has been run
  invalidates the pre-registration and must be recorded as such in a new entry — not folded
  in silently.

- **Why six, argued rather than asserted.** Group B is 22 positives. Six features is ~3.7
  positives per feature, which is already generous and is the upper end of what this labelled
  set supports. Fewer would be defensible; more would not. **The number is a judgement, not a
  derivation** — there is no threshold that makes six correct and seven wrong. What makes it
  binding is that it is fixed *now*, before any result exists to be tempted by, which is
  precisely the condition D-015 §3 imposed and did not discharge. The four D-015 names
  map to six computed quantities because two of them (ECD size/shape, epitope-region pLDDT)
  are each naturally two numbers — a size and a shape, a global and a regional pLDDT — and
  collapsing either pair would discard the distinction that makes it informative.

- **Why these and not a learned embedding.** Ruled in D-015 §3 and restated here because it
  is the entry's load-bearing constraint: *interpretability is what lets a disagreement be
  attributed to a feature rather than shrugged at.* An embedding-distance model could rank
  well and would leave every disagreement unexplainable, which would make D-015 §1's actual
  research question unanswerable.

- **Two features that were considered and REJECTED, recorded so they are not quietly added
  later:**
  - **Predicted pocket volume via a pocket-detection algorithm** (fpocket-style). Rejected for
    this iteration: it introduces a third-party tool with its own parameters and failure
    modes, and feature 6 captures the ADC-relevant part (is there a large contiguous surface
    an antibody can reach) without it. *An antibody binds a surface patch, not a cavity* —
    small-molecule pocket detection is answering a different question.
  - **PAE-derived domain-boundary confidence.** Genuinely informative, and `pae` is already
    persisted — but it is not returned by every model path (`runner.py` guards it as
    optional), so a feature depending on it would be **absent for some targets and present
    for others**, which is a coverage problem D-024 would then have to express. Deferred, not
    dismissed.

---

- **The extractor's contract:**

  **Pure given `(structure.pdb, plddt, manifest_row)`.** No network, no GPU, no database. This
  is deliberate and matches the D-023 manifest's design: it makes the extractor **fully
  fixture-testable**, which for a component that feeds a 22-positive fit is not a convenience
  but a correctness requirement.

  **Output:** one row per target — six named floats, plus the `target_id`, the fold's
  provenance hash, and an explicit `feature_version`. The version exists so that a refit
  against changed feature code is detectable rather than silent.

  **Failure is explicit, never imputed.** If a feature cannot be computed for a target (a
  malformed PDB, a zero-length span), the row records `null` **with a reason**, in the same
  discipline as D-024's `tier_reason`. **Imputing a mean would be the worst available
  option** — it manufactures a plausible number for a target we failed on, and the fit would
  never know.

- **Test surface, written before the extractor (project rule):**
  - **Determinism** — the same PDB and pLDDT yield byte-identical features across runs. The
    fit is only reproducible if this holds.
  - **A hand-checkable fixture** — a small synthetic structure with known geometry, so radius
    of gyration and SASA are verified against a computed expectation rather than against
    whatever the code happened to emit first.
  - **Feature count is SIX** — an explicit test asserting the extractor emits exactly six
    features, so the pre-registration is enforced by the gate rather than by memory. **This is
    the test that makes this entry real.**
  - **Null-with-reason, never imputed** — a malformed input produces a null and a reason
    string, and no test fixture anywhere substitutes a mean.
  - **Membrane-proximal region is derived from the manifest boundary**, not from a fixed
    residue count, so a `whole`-method target and a `sliced_ecd` target are not silently
    treated alike.
  - **`feature_version` changes when feature code changes** — pinned by a test over the
    extractor's own source hash, in the D-009 §1 red-on-change manner.

- **Deep-learning justification:** This entry is what makes D-015 §3's pre-registration
  binding rather than aspirational. A fixed feature count, enforced by a test, is the
  difference between a small-sample fit that can produce a falsifiable negative result and one
  that can absorb any outcome. D-015 §3 named **two** negative results — including the
  non-obvious one, that a strong correlation with the comparator's evidence score is *also*
  null, because it means the features proxy attention-and-precedent rather than structure.
  Neither negative is interpretable if the feature set moved during fitting.

- **Consequences / follow-ups:**
  - **The extractor needs folds**, and folds need the enqueue step and worker. This entry is
    rulable now and buildable only after the pipeline runs end to end. Ruling it now is
    deliberate: the feature count must be fixed **before** any fit, and the cheapest moment to
    fix it is before there is a result to be tempted by.
  - **Feature 4 depends on the boundary method.** For `whole`-method targets (the 13 held out
    per D-024) the "membrane-proximal 25%" is a different thing than for a sliced ECD. Those
    targets are already held out of cross-method ranking claims (D-021), so this is consistent
    — but the extractor must not silently compute it as though it were comparable.
  - **`feature_version` should be persisted alongside `inference_settings`**, so a stored score
    can always be traced to both the fold that produced it and the feature code that read it.
  - **Group C (TROP2, HER3, CLDN18.2) runs through the identical extractor**, with no
    special-casing — otherwise the out-of-cohort probe is not a probe.
