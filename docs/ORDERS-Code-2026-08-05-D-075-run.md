# ORDERS — Code — 2026-08-05 — Run D-075. This is a RUN, not a build.

> **COMMITTED 2026-08-05 with `### D-079` (`docs/README.md`). CITED BY the log, not restated in it —
> where this file and the log differ, THE LOG GOVERNS.** ⚠ This file is provenance for a decision that
> lives in the log; it is not itself authority. Check the `### D-079` header, not a reference to it.

> **⚠ TIER 0. This is the spine.** Deferred 2026-08-01, 2026-08-03, and 2026-08-04, each time for a
> good reason. **Owner ruling 2026-08-05: move on it.**
>
> **The build already merged** (`ORDERS-Code-2026-08-01-D-075-ablation.md`, PR #109). `geom_proxy`,
> the confidence-blindness fixture, `scripts/attention_control.py`, and migration `0007` all exist.
> **Nothing in this order writes a feature, a model, or an interpretation.** If you find yourself
> editing `core/features.py` or `core/scorer.py`, stop and report — the pre-registration has drifted.
>
> **Planner provenance (D-016):** the `feafeff` snapshot read at first hand 2026-08-05. **No GitHub
> connector.** PR #109's merge, migration 0007's state, and every run id below are **Code's to
> verify**, not the Planner's to assert.
>
> ⚠ **This order is not run in the same session as the census crank** unless the owner says so. It
> needs an unhurried window; that is why it has its own document.

---

## §0 — Five confirmations. Any failure is stop-and-report, not a workaround.

1. **`docs/README.md` §D-075 exists and Decision 4 reads exactly as merged.** Quote the table back.
   ⚠ **Where this order and the log differ, the log governs.** The sealed interpretation is the whole
   asset; a paraphrase of it is not it.
2. **Migration 0007 applied — verified by column inspection**, then separately by `alembic_version`.
   Report both. ⚠ **Alembic's exit code is not evidence.** If 0008 has since landed, check each
   column separately rather than the head revision.
3. **`ranking_run` id=2 (F-004) is intact and read-only:** `run_kind='preregistered'`,
   `scorer_version=91e646e4a289`, 56 rows, 12 positives. ⚠ Read-only is a property of the **call
   path**, not of `persist_results()`. Confirm no CLI path targets an existing id.
4. **`ranking_run` id=3 (`no_plddt`) is intact:** median **0.5625** / mean **0.5893** / **6-of-12**.
   This is Decision 4's anchor. ⚠ **It is not "≈ chance"** — only the count is even.
5. **The confidence-blindness fixture is green AND its contaminated arm still reds.** Both arms —
   differing pLDDT *values*, and differing pLDDT *array length*. The contaminated implementation is
   kept permanently in the test file precisely so the fixture's own bite is re-asserted every gate
   run. ⚠ **If it will not red, feature 7's confidence-blindness is unproven and D-075 is void while
   looking clean.** Stop.

---

## §1 — Freeze the attention proxies BEFORE the control runs

`scripts/attention_control.py` computes two proxies. **Both are frozen — source, query string, and
date — and recorded in the entry before a single result is read.**

| Proxy | Frozen as | Recorded |
|---|---|---|
| `pdb_present` | RCSB/UniProt cross-reference, **as-of date** | source + date |
| `pub_count` | PubMed hits for the gene symbol, **exact query string** | query + date |

⚠ **No re-querying after seeing a result.** Re-running PubMed because the first pass looked
unfavourable is the fishing this entry exists to prevent. If a query must change, that is a new dated
entry, not an edit.

---

## §2 — Run A: the `geom_proxy` refit (primary, and it runs first)

```
--ablate geom_proxy        # a NAMED set. Arbitrary subsets are refused by the code.
run_kind = 'sensitivity'
```

Same 12 positives, same floor, same folds, same nested-CV λ selection, same LOO mechanic, same RNG
discipline. **Only the feature set differs**, so any change is attributable to replacing confidence.

**Recompute and record:** the 12 LOO percentiles · **median, mean, and count-above-0.5 as an explicit
triple** (D-041 dec 4 — never one statistic) · head-to-head vs. the Kathad comparator on the 8
overlapping targets · Spearman(ablated, comparator).

⚠ **Spearman is a recorded dead discriminator.** FULL and `no_plddt` agree to full float precision
while their per-target percentiles differ by up to 0.25. **It is reported, not read as evidence.**

**Guards that must stay green through the run:** the three D-060 leakage guards re-assert on the
`geom_proxy` path (scrambled comparator → identical coefficients; held-out features unchanged;
λ-selector never sees the held-out index) · `geom_proxy` = **6 parameters** (5 features + intercept)
· the six-feature assertion on the **pre-registered** path stays green — if it reddens, an ablation
has leaked into the pre-registered path and the run is void · determinism: same fixture, two runs,
byte-identical coefficients.

⚠ **`ranking_run` id=2 is not re-run, not amended, not touched.** F-004 is read from its row.

---

## §3 — Run B: the popularity-matched control (only if A survives)

**Sequencing is ruled and not a preference:** A first. If the confidence-blind axis has already
collapsed, B is moot — the signal was pLDDT, and running B anyway invites a narrative built from two
results read together.

Stratify or covariate-adjust on the proxy, then test whether the positives still enrich. **Run
`pdb_present` and `pub_count` separately — a sensitivity pair, not one blessed number.**
`run_kind='attention_control'`, proxy name and frozen date persisted. Re-running with the same frozen
inputs must be byte-identical.

---

## §4 — ⚠ Read the result against the sealed interpretation **in the log**, and against nothing else

**Open `docs/README.md` §D-075 Decision (4). Read the rows there. Quote the row that fired from the
log. Do not write prose first.**

**⚠ This order reproduces none of those rows, deliberately.** An earlier draft did, and it dropped
one row and softened another — see `CORRECTION-2026-08-05-D-075-order-decision-4.md`. **There is one
copy of the frozen interpretation and it is in the log.**

Three things about reading it, each with a specific prior failure behind it:

1. **Judge on the explicit triple — median, mean, and count ≥0.5 — never on one statistic**
   (D-041 dec 4). The log anchors the comparison three-against-three with numbers; use the log's.
2. **⚠ The `no_plddt` baseline is not chance.** Any reading that treats it as chance is wrong before
   it starts.
3. **A disagreement among the three statistics is a legitimate, reportable outcome** — the log
   states it is the *expected* one at n=12. **It is not a failed run and it is not to be resolved to
   one number.**

**`≈` is deliberately not thresholded.** No tolerance invented after seeing the diff.

---

## §5 — Land it as its own F-entry, amending nothing

- **Reserve `F-017` for the D-075 result** in `RESERVED.md` **before the run**, so the number is not
  contested mid-session. ⚠ The census orders of the same morning originally claimed F-017 for a
  stop-condition; that collision is corrected there. **Confirm against the live log anyway.**
- The entry **cites D-075 and F-004 and amends neither.** F-004 stands as the record of the
  six-feature pre-registered result.
- **The entry states which Decision-4 row fired, quoted from the log**, before it states anything
  else.
- ⚠ **D-075 Decision 6 gains a fourth item:** the cohort's fold-recipe heterogeneity
  (`(int8,64)×42`, `(fp16,None)×34`, `(fp16,64)×3`, one unrecorded) is a thing this design **cannot
  separate**. F-015 is untested at the cohort's actual variable (`None` vs `64`). **No claim in
  either direction** — *"those 34 folds are fine"* is exactly as unsupported as the opposite.
- **No deployed surface changes in this PR.** If the headline moves, the UI's framing updates from
  `/api/ranking` derivation like any other result change — never a silent edit.

## §6 — Done when

Five §0 confirmations reported · proxies frozen with source, query, and date, recorded **before** any
result · Run A executed, triple + head-to-head + Spearman recorded · Run B executed **only if A
survived**, both proxies separately · the fired Decision-4 row quoted from the log **before** any
prose · result landed as its own F-entry citing D-075 and F-004, amending neither · Decision 6's
fourth item written · gate green · **no feature changed, no model changed, no interpretation
authored after the fact.**

---

## §7 — What this unblocks, stated so the day after is not improvised

Branch A or Branch B follows **from the row that fired, not from the hope.** P-001's claim is
selected by this run and has not been made. Phase B (held-out fold-and-validate), the census's
interpretive half, and the Pfizer novelty argument all take their shape from it.

⚠ **If it collapses to Branch B, that is a stronger paper than an unexamined 0.607** — it converts a
hidden weakness into a stated finding, and it was found here rather than by a reviewer or by a Head
of AI. **The only losing move is not running it.**
