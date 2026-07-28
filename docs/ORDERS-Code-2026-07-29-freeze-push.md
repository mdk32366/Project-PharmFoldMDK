# Orders for Code — the freeze push: D-067 (amended), the audit gap, and one wrong number

> **⚠ Supersedes `ORDERS-Code-2026-07-29-D-067-narrative-surfaces.md`.** `CoverageLine` landed in
> #93, so it drops out of scope. Banner the old file in place.
> **Freeze is end of Wednesday.** Tiers below are ordered so that if time runs out, **the things that
> are factually wrong on screen land and the improvements don't.**
> **Scope:** `ui/src/`, `docs/`. No `app/`, `core/`, `scripts/`, migrations. No re-run.

---

## TIER 1 — wrong right now. These land or the freeze doesn't happen.

### 1.1 The false "not built" claim, on two surfaces

**`Story.jsx:72-74`** — *"What is deliberately not built… we will not fake it."* **The promise was
kept.** It **resolves**, it does not get deleted (D-067 decision 1). Owner copy.

**`MethodNote.jsx:56-59`** — *"What it will do — not yet… It waits on the scorer. It is not built."*
**Splits** into what shipped (the ranking, at reduced scope) and what is deferred with the reason
(disagreement classification, baseline rank, delta, per-feature attribution). **Updating it as one
claim replaces a false statement with another.**

**`MethodNote` D-028 commitments** — *"It classifies disagreement; it does not explain it"* asserts a
capability that does not exist. **The commitment stands; the tense must not assert the build.**

### 1.2 Story's hardcoded fail reason (D-067 decision 3)

**`Story.jsx:58`** hardcodes `(a documented hardware ceiling)` for the `failed` group; **IGF2R's
actual reason is `whole_sequence_fold`**, and *"hardware ceiling"* describes `over_local_ceiling` —
FAT2 and MUC16's reason. `CoverageView.jsx:55` already derives `r.fail_reason`.

**Derive it.** ⚠ **D-043's distinction must survive:** `failed` (attempted, did not complete) and
`not_folded` (never attempted) stay separate.

### 1.3 Story beats 4–6 and the correction paragraph

Half the story is missing. Appendix has the six beats. **Beats 4–6 and the correction are new; 1–3
need light touch only.**

**⚠ Keep the opening question as written** — *"if we rank these targets by their 3D shape."* That is
what was asked. **Beat 5 delivers the reversal.** Softening the question retroactively erases it.

### 1.4 ⚠ The audit gap — surfaces built since Monday have never been checked

**The Planner's audit ran against a Monday snapshot.** Everything built since — **`ScorerView`, the
two-column layout, the `Term` tooltips, the `Score` tooltip** — has **never had the five checks run
against it.** The Planner cannot do this; the source is not available to it.

**Run the five checks against every component touched since `fc28c7f` and REPORT before fixing:**

1. **Pre-scorer claims** — forward-looking, falsified, or fulfilled-promise.
2. **`ranked` used to mean "in the ranking"** (D-066 decision 4).
3. **Literals that should derive** (D-050) — including the new result numbers.
4. **Claims the log contradicts** — verified from the endpoint, not from the copy's confidence.
5. **Terms outside the glossary guard.**

**This is the highest-risk unchecked area in the project**: the newest surface, the most claims, the
one carrying the result. **Report the count; scope follows the count.**

### 1.5 The wrong number in the committed closeout correction

The appended correction says **"5 surfaces unscanned."** **That figure was a Planner estimate, not a
measurement, and it is wrong** — the prose-bearing unscanned set is roughly eleven.

**⚠ A correction about unmeasured claims that itself contains an unmeasured number.** Recorded as a
Planner error.

**Count it mechanically** — components rendering user-visible prose, minus the four in `surfaces()`
— **and amend the correction with the measured figure.** Do not estimate it a second time.

---

## TIER 2 — should land, not fatal if it slips

### 2.1 `MethodNote` remaining items

- **`:50`** — D-066 vocabulary (`ranked` = disposition; `rankable` = the ranking's membership).
- **`:27`** — the `82` literal. **Owner call**: constant fixed by the source paper, or statistic?
  Propose, do not decide.
- **The attribution example** — *"feature 6 drives this rank."* **F-005 found the geometry features
  nearly inert; D-027 flagged feature 6 as the fragile one.** It is now the worst available example.
  Propose a replacement.

### 2.2 `Story.jsx:50` — D-066 vocabulary

### 2.3 `plddt.js` — `COHORT_MAX_PLDDT = 84.23`

A cohort statistic as a module constant (D-067 decision 4). **⚠ Report before changing:** if it is
**only rendered**, derive it. **If it also sets a band boundary, it is a decision constant, not a
statistic**, and converting it changes behaviour.

### 2.4 `App.jsx:15-16` — code comment, not user-visible. Update for accuracy.

---

## TIER 3 — after the freeze, with owner ruling

- **Guard part one** — `ScorerView` into `surfaces()`, the 8 terms into `MUST_DEFINE`. **⚠ The eight
  definitions still need the owner's domain sign-off** — they were drafted, not approved.
- **Tooltip overflow** — shared `.term-def`, viewport clamp or edge flip. **Walk-verified, not
  gate-verified** (jsdom has no layout); record the `scrollWidth` figure as the evidence.
- **The remaining unscanned surfaces** — the copy sweep, size measured, deferred.

---

## ⚠ What must not break

Constraint-A absence, extended to `84.23` and the F-006 range · readability under its pinned ceiling
· `/coverage` still renders a true partition · all four `result_status` states · **caveat (b) with
the result and the coverage line with its table, desktop and stacked** · the DOM-order tests from #93
stay green.

## Owner copy calls — draft and flag, do not ship

1. **The resolved promise** (Story).
2. **The correction paragraph** — ⚠ **not told as a triumph.** Register matters more than content.
3. **The open question** (beat 6) — the project's actual conclusion.
4. **MethodNote's replacement attribution example.**
5. **The `82` literal** — constant or statistic.
6. **The eight glossary definitions** — still unapproved.

## Appendix — Story's six beats

1. **The question.** Does structure-derived information reorder an expression-based ranking?
2. **What was built.** Real ESMFold, owned hardware, pinned checkpoint, 80 folds, six features from
   the network's output.
3. **What was fixed before any result, and when** — D-027, D-041, D-060. **Dated.**
4. **What the fit found.** Modest above-chance ordering; not distinguishable from the comparator;
   not a proxy for it.
5. **What the sensitivity found.** The signal is carried by the model's confidence, not the geometry.
   **The opening question gets its answer here, and the answer is a reversal.**
6. **What is open.** Whether that confidence encodes structural order or training-set
   representation. **Ends on the question, not a claim.**

**The correction**, two or three sentences: the first fit ran on zero positives because the driver
read a schema the curated file never adopted; the raise was misread as a finding about the data; the
defect was found, the interpretation withdrawn, the invalid artifact kept and marked rather than
overwritten, and the corrected run produced the result now shown.

## If something is wrong

Say so before building — particularly if §1.4's audit finds more than a handful, or if
`COHORT_MAX_PLDDT` sets a threshold. **Both change the freeze's scope, and scope follows the
measurement.**
