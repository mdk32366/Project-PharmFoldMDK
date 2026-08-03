# Orders for Code — F-009 cohort-boundary UI note (REVISED against the real repo)

> **⚠ REVISION NOTE.** These orders were rewritten after the Planner read the actual repo snapshot
> (2026-08-01). The earlier draft asked Coder to "report the UI structure first because the Planner
> can't see it" — that step is now discharged: the Planner has read `ui/src/` directly. The integration
> points below are named from the real code, not guessed. Where this differs from the earlier draft,
> this governs.
>
> **⚠ SCOPE IS SMALL AND SURGICAL.** One honesty gap: the UI presents the Kathad 82 as "the cohort"
> without stating it is an expression-selected *comparator*, not a census — and that clinically-
> validated ADC targets (CD30, CD33, CEACAM5, Trop-2) fall outside it (F-009). This closes that gap.
> **NOT the tranche/census UI** (gated on D-075 + a census that does not exist — `SPEC-tranche-ui-future.md`).
>
> **NOT in this PR:** any confound-disclosure change (the UI ALREADY has `PlddtAmbiguityNote.jsx` and
> the `AdcContext` "find me more NECTIN4s" caveat — do not touch them); any tranche structure; any
> change to `core/`, `db/`, the scorer, or the ranking computation.

---

## 0. What the Planner found in the repo (so these orders are grounded, not assumed)

The UI is already deeply honest — this is a targeted addition to an existing honesty layer, not a new
one. Confirmed present:

- **`ui/src/components/AdcContext.jsx`** (route `/about`) — the ADC framing/onboarding. Already derives
  cohort stats LIVE from `listAnalyses()` (D-050/D-051: "a literal count rots silently"), already
  carries the confound caveat ("could quietly encode 'find me more NECTIN4s'"). **This is the primary
  home for the cohort-boundary paragraph** — it already discusses what a good target needs and what
  the cohort is.
- **`ui/src/components/ScorerView.jsx`** §A "From the cohort to the fit set" (route `/scorer`) — the
  cascade. Line ~117 reads `<b>{denominator}</b> cohort targets (Kathad et al.)` — **this is the exact
  spot that presents Kathad as "the cohort" without the comparator/census distinction.** A short
  qualifier belongs here too.
- **`data/heldout_positives.csv`** — the derive source. Header documents D-016 provenance; accessions
  resolved live from UniProt. **The four example targets must derive from this file, not be hardcoded.**
- Existing patterns to reuse: `Term.jsx` (glossary terms), the `note` CSS class, the derive-live idiom.

---

## 1. The content (substance fixed; copy owner-reserved)

Two placements, one paragraph of substance shared between them.

### 1a — Primary: a paragraph in `AdcContext.jsx`
Add a subsection (after "Why this project exists", before or after the "success case is a bad prior"
block — owner's call on order). Substance:

- **The 82 is an expression-and-selectivity comparator cohort (Kathad et al. 2024), not a complete
  census of ADC-targetable antigens.**
- **Clinically-validated ADC targets fall OUTSIDE it** — CD30 (brentuximab vedotin), CD33 (gemtuzumab
  ozogamicin, the first ADC, 2000), CEACAM5 (tusamitamab ravtansine), Trop-2 (sacituzumab govitecan) —
  excluded by Kathad's expression filter, not because they are poor targets.
- **This is a boundary condition, stated plainly:** the ranking re-orders a fixed comparator set; it
  is not a claim about the complete target space. It connects to the existing honesty line — the same
  discipline that resists "find me more NECTIN4s" also refuses to present a slice as the whole.

### 1b — Secondary: a one-line qualifier in `ScorerView.jsx` §A
The cascade's first `<li>` ("{denominator} cohort targets (Kathad et al.)") gets a short inline
qualifier or a `Term`-style note: **"comparator cohort, not a census — see About."** Links to the
`AdcContext` paragraph rather than repeating it (single source of the framing).

### ⚠ Over-claim guard (F-009 §3) — MUST hold in copy AND as a test
The note indicts the **comparator's completeness**. It must NOT say or imply the scorer would have
caught these, or that the structural axis ranks them highly. They are unfolded, unscored, and CD30/CD33
are attention-rich (the D-075 confound). **State the comparator has blind spots; never claim the
scorer fills them.**

---

## 2. Derive, don't inscribe (matches the existing AdcContext pattern)

`AdcContext.jsx` already derives its stats live rather than hardcoding — the cohort note follows the
same rule. **Do not hardcode the four target names/accessions as a JSX literal.** Options, in order of
preference:

1. **Build-time constant generated from `data/heldout_positives.csv`** (a small derived asset), with a
   test asserting it matches the CSV. Four names is small; a live fetch may be disproportionate, so a
   tested build-time constant is likely the right weight here — but it must be *generated + tested*,
   never hand-typed.
2. If a build step for four names is too much ceremony, a hand-maintained constant is acceptable ONLY
   with a test that asserts every name+accession in it appears in `data/heldout_positives.csv` — the
   drift guard is non-negotiable, the generation method is negotiable.

Either way: **the UI and the CSV cannot silently diverge**, and every displayed accession traces to the
UniProt-verified source (the recall-error trap this project has hit).

---

## 3. Tests

- **The cohort note renders** in `AdcContext` (route `/about`) and the qualifier renders in `ScorerView`
  §A — presence tests, not buried.
- **Over-claim denylist test:** the rendered copy of BOTH placements does NOT contain claim-language
  matching the scorer catching/ranking these targets ("would have caught", "ranks highly", "our method
  identifies", "correctly prioritis", etc.). Makes F-009 §3 structural, not editorial.
- **Source-match test:** every example target name + accession shown appears in
  `data/heldout_positives.csv` (the drift guard).
- **The existing tests stay green** — `glossary.contract.test.jsx`, `readability.tripwire.test.jsx`,
  `AdcContext.test.jsx`, `ScorerView.test.jsx`, `test_architecture_contract.py`. This is additive; no
  route added, no contract changed. If `readability.tripwire` fires on the new prose, that is a real
  signal to tighten the copy, not to suppress the test.

---

## 4. Order of work

1. Tests red first (note-present ×2, over-claim denylist ×2, source-match).
2. The derived constant from `heldout_positives.csv` (§2) + its match test.
3. The `AdcContext.jsx` paragraph (§1a) — placeholder copy clearly marked for owner finalisation.
4. The `ScorerView.jsx` §A qualifier (§1b), linking to About.
5. Owner finalises copy (copy is owner-reserved).
6. Gate, dry-diff, owner merge. **This deploys** (real UI change) — after merge, verify both placements
   render live, per the deploy-verification discipline.

## 5. ⚠ Four things that will bite

1. **Do not touch the existing confound honesty** — `PlddtAmbiguityNote.jsx`, the `AdcContext`
   "find me more NECTIN4s" block, `ScorerView`'s "First negative outcome — FIRES". Those are shipped and
   correct. This PR ADDS the cohort-boundary point; it does not rework the confound layer (that is
   D-075-result-gated).
2. **Do not build the tranche/census UI.** If work drifts toward cohort-switching or census display,
   STOP — that is the gated future spec.
3. **Do not hardcode the target list.** Derive + test, per §2.
4. **Over-claim guard is a test, not polish.** CD30/CD33 are attention-rich; implying the scorer
   validates them pre-empts D-075 wrongly.

## 6. What "done" means

`/about` and `/scorer` state the 82 is a comparator not a census, with verified example targets derived
from `heldout_positives.csv`, the over-claim guard enforced by test, existing honesty layer untouched,
copy owner-finalised, gate green, both placements verified rendering live post-deploy.

## 7. Separate housekeeping the Planner found (NOT this PR — its own commit)

`docs/` contains basename-collision duplicates: `PharmFoldMDK_Deck (1).pptx`,
`PharmFoldMDK_Held_Out_Logic (1).docx`, `slide_lastthree (1).pptx`. Same `(1)`-suffix hazard swept once
already. Diff each against its unsuffixed twin; if byte-identical, delete the `(1)` copy; if not,
surface the difference. Own housekeeping commit, not entangled with the UI change.

## 8. If something is wrong with these orders

Say so before building. Specifically: if placing the paragraph in `AdcContext` disrupts the existing
narrative flow (a copy-structure finding the owner should rule on), or if the `readability.tripwire`
test reveals the cohort-boundary point can't be made within the prose budget without cutting existing
content — report the tradeoff rather than silently trimming honest existing copy.
