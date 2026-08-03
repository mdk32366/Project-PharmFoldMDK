# META-ORDER — paste into Code — three UI orders, execution sequence (2026-08-01)

You are receiving THREE order documents for un-gated UI honesty work. This meta-order governs the
sequence and the boundaries. Read this first, then the three orders. **Do not deviate from the
sequence or scope without reporting back.**

## The three orders (and NOTHING else is authorized by this handoff)
1. `ORDERS-Code-2026-08-01-confidence-demotion.md`
2. `ORDERS-Code-2026-08-01-sortable-target-list.md`
3. `ORDERS-Code-2026-08-01-F009-cohort-ui-note.md`

## ⚠ Execution sequence — do these IN ORDER, one PR each, owner merges between

**FIRST — confidence-demotion (#1).**
Rationale: it changes what the target-list columns *are* (relabels/demotes the "Confidence" column,
reserves the target-quality slot). The sortable order (#2) makes columns sortable — so the column
semantics must be settled before sortability is layered on. #1 before #2 is a hard dependency, not a
preference.

**SECOND — sortable-target-list (#2), only after #1 is merged.**
⚠ #1 and #2 BOTH modify `ui/src/components/TargetList.jsx`. Do NOT open them as parallel PRs against
the same file. Land #1, let the owner merge it, re-base, then start #2 against the merged state. Its
load-bearing rule (absent values are a category, never coerced to 0) is the part that must not be
skipped — see the order's §2.

**THIRD — F-009 cohort-note (#3), any time (no collision).**
It touches `AdcContext.jsx` and `ScorerView.jsx`, NOT `TargetList.jsx`, so it does not collide with
#1/#2 and may run in parallel or after. It has its own §7 housekeeping sub-task (the `(1)`-suffixed
duplicate docs) — that is a SEPARATE commit, not entangled with the UI change.

## ⚠ Hard boundaries — what this handoff does NOT authorize
- **Do NOT build any suitability score, any "Structural Suitability" or "Clinical Opportunity" column,
  any tranche/census UI, any coverage reframe.** Those are GATED on the D-075 run and are NOT in this
  handoff. If any order's work drifts toward them, STOP and report.
- **Do NOT touch the D-075 machinery, the scorer, `core/`, `db/`, or the API.** These are UI-only orders.
- **Do NOT apply migration 0007 or run the geom_proxy ablation.** Those are owner-gated, separate, and
  not part of this handoff.
- **Do NOT move, create, or reorganize any other docs.** Only the three named orders are in play. If
  you notice other documents that seem relevant, do NOT act on them — report and wait.

## Per-order discipline (applies to all three)
- Log-leads-code where an order calls for an entry; tests red-first; no run in the PR unless the order
  says so (none of these run anything).
- Each deploys a real UI change → verify live post-merge, not just green tests.
- Copy is owner-reserved: scaffold with clearly-marked placeholders, owner finalizes wording.
- If an order's premise is wrong against the real code, report BEFORE building (each has a §"if
  something is wrong" clause) — do not silently adapt.

## Report-back checkpoints
- After reading all three: confirm the sequence and the `TargetList.jsx` collision are understood.
- After #1 merges: confirm before starting #2.
- If anything pushes toward a gated boundary above: STOP and report, do not proceed.
