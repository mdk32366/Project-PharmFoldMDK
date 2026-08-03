# D-076 — The last three unfolded targets: a scoped plan, one tier executed, two on ice behind a named trigger

> **Number check:** live log is ahead of the project snapshot (F-007 / D-070 / D-071 are the most
> recent seen). Drafted as **D-072**; that number was already TAKEN by the miniature demo notebook
> (`d46aa1a`), so this is renumbered **D-076** — verified 2026-08-03 against `docs/README.md`, whose
> highest decision entry is D-075. The number was checked, not inherited from an estimate
> before merging and renumber if needed. Log leads code — this entry is written before any re-fold.
>
> **Type:** A decision (scope + sequencing), carrying one finding inside it (the MUC16 disorder read).
> Nothing about F-004 changes. This entry does not touch the fitted scorer, the LOO distribution,
> the nulls, or the novelty claim — see §4.

---

## §0 — Why this entry exists

At delivery the cohort stands at **79 of 82 folded**. The three unfolded targets have, until now,
been carried as a single bucket ("unfoldable, surfaced as a finding, not a silent exclusion"). That
bucket is wrong: **the three are three different problems**, and collapsing them hid the fact that
one of them is trivially closable and the other two are resource-access problems, not method walls.

When the work is presented to a research team, "why aren't all 82 folded?" is the likely first
question. The correct answer is an engineer's answer — *yes it can be done, here is how, here is the
cost* — with feasibility stated cleanly and utility held as a separate judgement (§4). This entry is
that answer, recorded as pre-registered scope so it reads as a plan, not a reactive scramble.

---

## §1 — The three targets are three different problems

| Target | Length | Why unfolded | Class |
|---|---|---|---|
| **IGF2R** | large ECD, ordered | Hit a transient **A6000 rental-tier ceiling** on its run — not a size wall | **Compute limitation.** Genuinely "unfolded," no asterisk once folded. |
| **FAT2** | 4,030 aa | Exceeds single-sequence capacity on available hardware; but **ordered** (cadherin repeat stack) | **Resource + method-seam.** Foldable with more VRAM or by domain assembly; assembly changes `boundary_method`. |
| **MUC16** | 14,451 aa | Off the end of the field's map; **largely intrinsically disordered** (tandem SEA repeats + glycosylated linkers) | **Biology, not compute.** A structure is producible; a meaningful whole-ECD structure for the six features is not. |

The distinction is load-bearing: it is the difference between "one more run," "a method with a
labelled seam," and "the wrong question for this molecule."

---

## §2 — The plan, by tier (feasibility stated cleanly; utility deferred to §4)

### Tier 1 — IGF2R. **EXECUTE NOW.** Comparable, no asterisk.

- **How.** Re-enqueue on the A6000 rental tier, recipe resolved at fold time (D-047), sequence length
  checked against what ceilinged last run. If it still ceilings on the A6000, escalate one rung to a
  single larger-VRAM pod (H100 80 GB, same workflow). No new code, no new `boundary_method`.
- **Comparability.** Folds under the **same ESMFold-v1 / sliced-ECD recipe** as the other 79. Its six
  features are directly comparable. This is the only one of the three where "unfolded" is a plain
  limitation rather than a finding.
- **Cost.** Hours. One rental block, <1 hr fold time, ~$0.54–2/hr.
- **Consequence on merge.** Cohort 79 → 80 folded. **The ranking table and every coverage-derived
  number update from the authoritative endpoints** (no re-hardcoding — stale-literal discipline). If
  IGF2R clears the pLDDT floor and is a ranked disposition, it enters the ranking set; if labelled,
  it enters the fit set and F-004's denominators move. **That is a result update, pre-authorised
  here**, executed the same way any fold enters: through the gate, derived, not typed.
- **Sequencing:** independent of Tier 2/3. Do it whenever a rental block is convenient.

### Tier 2 — FAT2. **ON ICE.** Behind the §3 trigger. Two routes.

- **Route A — bigger single pass.** 4,030 aa on an 80 GB card, one sequence. Cleanest if it runs
  (standard features, no seam); may fail. Cheap to attempt.
- **Route B — domain-wise fold + assembly** (robust). Fold the CA-domain stack in overlapping
  windows, stitch on shared repeats. Always runs. **Introduces a new `boundary_method` value**
  ("assembled" / "domain_stitched") that must travel with the features exactly as Feature-4's
  cross-method caveat does — comparable *enough* to render, provided the seam is labelled and tested.
- **Cost.** Route A: one big-pod block, may fail. Route B: ~1–2 sessions (domain-boundary pass,
  windowing, stitch-and-validate, new `boundary_method` + tests). Feasible and honest; not free.

### Tier 3 — MUC16. **ON ICE.** Behind the §3 trigger. Produces a finding, maybe not a feature.

- **Route 1 — fold ordered SEA domains individually.** Legitimate domain models, but a "MUC16" row
  carrying features from ~120-aa domains would mislabel what was measured.
- **Route 2 — fold the membrane-proximal window** an ADC would engage. Biologically defensible, but a
  *choice of sub-region*; another labelled seam, larger.
- **Route 3 — run it, report the disorder.** Fold what folds; let low-pLDDT regions render as the
  model reporting "no confident structure here." Adds no false number.

#### Finding embedded here (D-016): MUC16's un-foldability is a structural result, not only a gap

MUC16 being intrinsically disordered means **"predict its ECD structure" is partly the wrong
question** — and that a disordered, heavily-glycosylated antigen is a genuinely different engineering
problem for an antibody. The pipeline correctly placing MUC16 out of structural reach is *itself
informative about its ADC-targeting profile*. Whichever route runs, this framing is preserved: MUC16
is not merely "too big," it is a case the structural axis flags as unreachable, consistent with
known biology.

---

## §3 — The trigger for Tier 2 and 3 (named, so the gate is explicit)

**Tier 2 and Tier 3 execute on: external validation of the work's novelty** — a paper accepted, a
research group adopting the structural axis, or an equivalent signal that the cohort must become
complete for *reproducibility/coverage* reasons rather than demo optics.

Rationale (the utility inversion, recorded so the reasoning survives):

- **Before validation:** the folds do not change F-004 (§4). MUC16's un-foldability is a *stronger*
  honesty artifact than a filled cell. Executing Tier 2/3 now spends real effort — and, for MUC16,
  risks trading a finding for an asterisk — to make a coverage table prettier. Utility low-to-negative.
- **After validation:** a published method must be complete on its stated cohort. "Couldn't fold 3
  of 82" stops reading as sophistication and starts reading as an unfinished dataset. FAT2's seam
  becomes a methods-section paragraph (where seams belong); MUC16's disorder becomes a publishable
  finding in its own right. Utility flips positive.

**The trigger is external and identifiable.** That is what makes "on ice" a plan and not a stall.

### Execution path for Tier 2/3 when the trigger fires

The two hard folds are a **resource-access problem more than a method problem.** A well-provisioned
academic lab (e.g. the UCLA contact from the Razzak introductions, with institutional GPU access)
is the natural executor of Route A (large single-pass) for FAT2 and Route 1/2 domain work for MUC16.
**Recorded as a candidate collaboration path, not a commitment.** If pursued, the same discipline
travels with it: any fold produced elsewhere enters through the gate, its `boundary_method` and
environment captured (F-007's lesson — the manifest is not a reliable proxy for what ran), and its
features are comparable only insofar as the seam is labelled. A fold from another lab is not exempt
from D-016; it names how it is known like any other.

---

## §4 — What this entry does NOT change (the firewall around F-004)

- **F-004 stands untouched by Tiers 2–3.** MUC16 and FAT2 are not in the 12 labelled positives; the
  LOO distribution, both nulls, the Spearman, and the "orthogonal but unproven" finding are
  unaffected by whether they fold.
- **Tier 1 (IGF2R) may move F-004's denominators** *if* IGF2R is a labelled positive that clears the
  floor — and if so, that is a legitimate, pre-authorised result update, run through the gate, not a
  silent edit. Check IGF2R's label status against `data/adc_reference_mapping.csv` before folding so
  the consequence is known in advance, not discovered after.
- **The novelty claim is independent of coverage.** "No published method ranks ADC targets on
  predicted ECD structure" is true at 79/82, 80/82, or 82/82. Folding the last three completes a
  dataset; it does not create or strengthen the contribution.

---

## §5 — The one risk to hold

The temptation, now that a plan exists, is to execute all three **before** the §3 trigger, to look
complete for a demo. **Resist it.** Doing MUC16 prematurely is the single move in this project that
would spend honesty capital to buy coverage optics. The plan's value now is that it *exists and is
credible* — scoped, tiered, triggered — not that it has run. IGF2R is the only tier that executes on
its own schedule, because it is the only one with no asterisk and no utility question attached.

---

## §6 — Definition of done for this entry

- [x] Number confirmed against `docs/README.md` (2026-08-03): D-072 was taken by the miniature
      notebook; this entry is **D-076**, the next free decision number.
- [ ] IGF2R label status checked against the reference file and recorded here **before** its fold.
- [ ] Tier 1 executed: IGF2R re-enqueued, folded, cohort → 80, results updated through the gate,
      all coverage/ranking numbers re-derived from endpoints (no re-hardcoding).
- [ ] Tier 2/3 remain unstarted, trigger unmet — verified, not assumed.
- [ ] Deck slide ("The last three: a plan, not a wall") reflects this entry's tiers and trigger.
