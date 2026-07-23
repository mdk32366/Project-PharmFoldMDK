# Session Pre-Work — The Scorer Arc (Step 3)

**Preceded by:** the UI arc, complete. Read API, coverage supplier, and a four-surface React app
live on `pharmfoldmdk.fly.dev`; 42 folds rendered honestly; the ranking table deliberately
unbuilt because there is nothing to rank.
**Session type:** the project's **graded centre**. Decision-heavy at the front, then build.

---

## 0. Provenance (D-016)

Planner works from tree at `#58` + the live prod DB/API. Verified this session: `D-015` §§1–3
and `D-027` read in full; `data/cohort_82_mapping.csv` and `data/cohort_82_ecd.csv` column
headers read directly; `GET /api/coverage` live output cross-checked.

**What is asserted here and NOT yet verified:** whether the Kathad supplementary files (S2/S3)
are obtainable in the form the comparator needs. §2 is written as a blocker precisely because
the Planner has not confirmed it.

---

## 1. Why this arc is the one that matters

**The Prime Directive is only partly discharged today.** CLAUDE.md requires a neural network to
do load-bearing work and forbids shipping "only a wrapper around an external service." Right
now the project runs its own ESMFold — real, defensible, and *not sufficient on its own*:
D-015 §3 says so explicitly.

> *"ESMFold stops being the deliverable and becomes the **input to** one. The network's output
> is now a judgement that can be wrong — which is the point."*

**Everything shipped so far is the supply chain. This arc is the product.** The scorer is where
"a neural network does load-bearing work" becomes a claim a grader can check, and the ranking
table is where D-015's research question gets an answer.

---

## 2. ⚠ THE BLOCKER — the comparator data is not in the repo

**This gates everything and must be resolved first.** The fit needs two things the tree does
not contain:

| Needed | For | In the repo? |
|---|---|---|
| **Kathad 1–5 evidence score**, per target | The baseline ranking the structural ranking is compared against (D-015 §2, Group A) | **No** |
| **Group B membership** — which 22 of the 82 are known ADC positives | **The labels the scorer is fit against** (D-015 §3) | **No** |

Verified against the committed cohort files. `cohort_82_mapping.csv` carries
`symbol, accession, primary, protein, status, note, candidates`; `cohort_82_ecd.csv` carries
geometry and bucketing. **Neither has an evidence score or a positive-label column.**

**Consequences, stated sharply because they are easy to under-read:**
- **Without Group B labels there is nothing to fit.** A learned scorer needs targets marked
  positive; D-015 §3 rules the fit is against Group B and D-027 fixed six features for exactly
  22 positives.
- **Without the evidence score there is no comparator**, so there is no disagreement to detect,
  no classes to render, and the entire UI centrepiece has no second axis.

**Step 1 of the session is establishing both, with provenance.** D-015 records the source
(Kathad et al. 2024, PLOS ONE `10.1371/journal.pone.0308604`, **CC-BY**, supplementary S2/S3).
CC-BY permits reuse with attribution. What must be settled and entered in the log:

- **Where the numbers came from**, file by file, so a grader can reproduce the join.
- **How the join is keyed.** The paper works in gene symbols; this project works in UniProt
  accessions and `cohort_82_mapping.csv` already carries a `symbol → accession` mapping with a
  `status` column (`clean`, and other values worth checking). **A silent join failure would
  drop targets from the comparator and nobody would see it** — the same invisible-loss class as
  the `data/`-not-in-image bug caught this week.
- **What happens to targets with no evidence score.** Null with a reason, never imputed
  (D-027's discipline, and D-024 will have to express it).

**⚠ D-015 §2 records a second open item that blocks calling the cohort final:** the mechanical
reconciliation of the full approved-ADC target set against the 82 *"has not been run."* Group C
is currently only the three exclusions the authors named. **This is cheap and should run in this
arc**, because Group C is the sharpest available test (D-015 §1a class-1).

---

## 3. What is already ruled — do not re-litigate

D-027 is unusually complete. **The Planner's own note in that entry is worth heeding:** it
records that a previous Planner framing contradicted D-015 §3 by inferring what the log was
building toward instead of reading what it says.

- **Six features, fixed.** ECD length · normalised radius of gyration · mean pLDDT over the ECD ·
  membrane-proximal pLDDT (C-terminal 25%) · normalised SASA · largest contiguous accessible
  patch fraction. **Adding a seventh after any fit invalidates the pre-registration.**
- **The extractor is pure** given `(structure.pdb, plddt, manifest_row)` — no network, no GPU,
  no DB. Fully fixture-testable, which D-027 calls *a correctness requirement, not a
  convenience*, for a component feeding a 22-positive fit.
- **Failure is explicit.** Null **with a reason**, never imputed. *"Imputing a mean would be the
  worst available option — it manufactures a plausible number for a target we failed on, and the
  fit would never know."*
- **`feature_version`** pinned by a test over the extractor's source hash.
- **Rejected features, recorded so they are not quietly added:** fpocket-style pocket volume;
  PAE-derived domain-boundary confidence.
- **Evaluation is pre-registered:** leave-one-out at target level, reported as a **distribution,
  never a single CV number**.
- **Two named negative outcomes**, either of which is *the result* if it occurs — see §5.

**What D-027 does NOT rule, and this arc must:** the model itself. D-015 §3 says "a small
trained model" and rules out a learned embedding and a hand-weighted sum. It does not name an
architecture, a loss, or a fitting procedure. **That is this arc's first real decision** and it
belongs in an entry before code.

---

## 4. Sequence

1. **Resolve §2's blocker** — obtain the evidence scores and Group B labels, rule their
   provenance and join in an entry, land the data as committed files.
2. **Run D-015 §2's reconciliation** — the approved-ADC set against the 82. Cheap; sharpens
   Group C.
3. **Rule the model** (§3's gap): architecture, loss, fitting procedure, how leave-one-out is
   run, what "ranks it highly" means operationally. **An entry before code.**
4. **Build the extractor** — tests first, against D-027's stated test surface, including the
   **feature-count-is-six** test that makes the pre-registration real.
5. **Extract features for the 42 folded targets.** Note: only 40 are `ranked`; the 2 held-out
   are folded but not in the ranking.
6. **Fit, with the diagnostics from D-015 §1a run first** — fold sanity, boundary sanity, pLDDT
   floor, score stability. **Ruling out (3) is a precondition for claiming (1) or (2).**
7. **The ranking table** — UI Plan v2 step 6, D-028's classes and attribution.

**Steps 1–3 are decision work and come first.** Step 7 is the demo centrepiece and is last.

---

## 5. The traps, named before they can be rationalised

**(a) The cohort is 40, not 82.** Only 40 `ranked ∧ folded` targets exist. The 29 rental-tier
targets are unfolded (owner action, A6000). **A ranking over 40 of 82 is not a ranking of the
cohort**, and the coverage line must travel with it — which is exactly what D-024 ruled and what
the coverage view already renders. **How many Group B positives fall inside the folded 40 is
unknown and must be computed early**: if the labelled set is materially smaller than 22, the fit
is on even thinner ice than D-027 budgeted for, and that is a finding to record, not a reason to
proceed quietly.

**(b) Both named negative outcomes must survive contact with a result.** D-015 §3 pre-registered
two, and the second is the subtle one:

> *"If the structural score correlates **strongly** with the comparator's evidence score, that is
> **also** a null result — it means our features are proxying for attention-and-precedent rather
> than measuring structure. **Check this explicitly.** A high correlation would feel like
> validation and would not be."*

**This is the trap most likely to be sprung**, because a strong correlation arrives looking like
success. Compute it, state it, and let it mean what it means.

**(c) Group B is not a clean positive set** (D-015 §3): these targets were pursued partly
*because* they were tractable, assessed by people who could see things we cannot. The honest
claim is bounded accordingly and the write-up must not widen it.

**(d) Leave-one-out on 22 positives is noisy by construction.** D-027 already anticipates
feature 6 being fragile, features 1 and 2 being collinear, and feature 4 being cross-method
incomparable. **A result that reveals these reads as anticipated** — that is why they were named
before the fit.

**(e) The temptation to mock.** The ranking table has been deferred all week precisely so it is
not built against imagined data. It stays deferred until real scores exist.

---

## 6. Definition of done

- The comparator data and Group B labels **landed with provenance**, joined without silent loss.
- The model ruled in its own entry before any fitting code.
- The extractor built tests-first, six features enforced by the gate.
- Features extracted for the folded cohort; **null-with-reason where computation failed**.
- The fit run, with D-015 §1a's four diagnostics run **first**.
- Leave-one-out reported as a **distribution**; **both** named negative outcomes explicitly
  checked and reported whichever way they fall.
- The ranking table rendering real scores with D-028's classes — or, if a negative outcome
  obtains, **the honest write-up of that**, which D-015 says *is the result*.

---

## 7. Also on the board

- **The A6000 rental fold** (owner) — moves coverage 40/82 → 69/82 and is what actually tests
  D-030's lease. The transport is finished and waiting (D-035/D-036).
- **The browser check** of `/target/1` and `/coverage` — the one UI verification only a human
  can do.
- **Parked, twice-carried:** `worker/requirements-frozen.txt` (D-018 amendment),
  `docs/HAZARD-search-path-seams.md` + D-032 stock-image correction.
