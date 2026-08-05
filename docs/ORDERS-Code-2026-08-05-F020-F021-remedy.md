# ORDERS — Code — 2026-08-05 (third) — F-020 / F-021: make D-075 executable

> **Planner provenance (D-016):** written from the `feafeff`-derived tree read at first hand
> 2026-08-05, with `scripts/fit_scorer.py:100-130`, `core/scorer.py:144-160`, and
> `scripts/extract_features.py:145-197` quoted rather than recalled. **No GitHub connector.**
>
> ⚠ **Read this adversarially.** The Planner prescribed `extract_features.py --all --load` earlier
> today and it would have duplicated `protein_features` and bound the new rows to `plddt_only`.
> **That prescription was wrong after the same kind of reasoning that produced this order.** Check
> the premises against the tree before building; report before adapting.
>
> **Governed by `RULING-2026-08-05-STOP-feature-7-not-extracted.md`.** Where this order and that
> ruling differ, **the ruling governs.**

---

## §0 — The organizing idea: the refusal ships FIRST, and production is its fixture

**Task A lands a guard that must refuse to run against the database as it stands right now.** Task B
then makes the data satisfy it. Task D watches the same command proceed.

⚠ **This is red-then-green at the level of the system rather than the test file, and it is available
exactly once — tonight, while `membrane_proximal_sasa` is NULL on all 80 rows.** After the fill it
can only ever be demonstrated on a fixture again. **A guard proven against real production state is
a stronger artifact than one proven against a mock**, and this is the only window for it.

**Nothing here touches:** the pre-registered path · `core/features.py`'s six · the frozen proxy
definition · `ranking_run` id=2 · any interpretation.

---

## §1 — TASK A · `--ablate geom_proxy` REFUSES on a null feature 7 (F-020)

**How known (D-016), quoted from the tree:**
- `scripts/fit_scorer.py:111` — `feats = (*(float(v) for v in rec.features), float(rec.membrane_proximal_sasa or 0.0))`
- `scripts/fit_scorer.py:114-121` — prints `WARNING: … a 0.0 placeholder here would be an imputed value (D-027)` **and proceeds**
- `core/scorer.py:152` — `(features[j] - self.means[j]) / self.stds[j] if self.stds[j] > 0 else 0.0`

### Scope — read this twice

⚠ **The refusal is scoped to the named `geom_proxy` ablation. It is NOT a property of the fit.**
The pre-registered six-feature path legitimately has no feature 7 and **must keep running
untouched.** **A guard that reddens the pre-registered path is a worse defect than the one it
fixes** — it would make F-004 unreproducible in order to protect an ablation.

⚠ **The `(0.0,)*7` placeholder at line 113 stays.** Those rows are excluded from the ranking set and
never fit or scored; they are inert by construction, and the existing comment says so. **Only line
111's coercion on an in-ranking row is the defect.**

### Tests first

| Test | Assertion | Prove it bites by (A-016: realistic mistake, failing **at the assertion**) |
|---|---|---|
| `test_geom_proxy_refuses_when_a_ranking_row_lacks_feature_7` | Raises, naming the symbols | Restoring `or 0.0` → red at the assertion |
| `test_the_preregistered_path_is_unaffected_by_null_feature_7` | Six-feature fit completes normally on the same fixture | Scoping the guard to the fit rather than the ablation → red |
| ⚠ `test_the_refusal_precedes_create_ranking_run` | **No `ranking_runs` row is created when the refusal fires** | Raising after run creation → red |
| `test_excluded_rows_may_still_carry_the_inert_placeholder` | An out-of-ranking row with zeros does not trip the guard | Widening the guard to all rows → red |

⚠ **The third test is the one that stops Task D from littering the run table.** A guard that raises
*after* `create_ranking_run()` writes a run row per refusal — and this order asks you to refuse
against production deliberately.

### Then the demonstration — the reason this task is first

After the gate is green, run **`--ablate geom_proxy` against production, exactly as Run A would.**

**Expected: it refuses, names the affected symbols, and creates no `ranking_run` row.**

**Report:** the refusal message, the symbol count, and — read as its own fact — **`SELECT max(id),
count(*) FROM ranking_runs` before and after.** ⚠ **They must be identical.** If a run row appeared,
that is stop-and-report and Task B does not start.

**⚠ If it does NOT refuse, stop.** That means the null-coercion path is not the one traced, and every
premise in this order is suspect.

---

## §2 — TASK B · A feature-7 fill that writes ONE column and proves it changed nothing else (F-021)

**How known (D-016):** `scripts/extract_features.py:180-197` — `session.add(ProteinFeatures(...))`,
**pure insert, no delete, no upsert**, all seven columns written; `:173-177` — `ranking_run_id`
resolves to `order_by(RankingRun.id.desc()).first()`, **which is id=4 (`plddt_only`)**.

### Ruled shape — narrower than a general updater, deliberately

**A new `--fill-feature-7` mode that writes `membrane_proximal_sasa` and nothing else**, keyed by
`analysis_id`.

1. **It recomputes all seven**, then **compares features 1–6 against the stored values per row.**
2. **⚠ Any difference in 1–6 is stop-and-report**, not a value to accept. The row is named, both
   values printed, **nothing is written.** F-004's inputs do not move under an ablation's fill.
3. **Only `membrane_proximal_sasa` is written**, and only where it is currently NULL.
4. **Row count before == row count after**, asserted in the same transaction.
5. **`ranking_run_id` is not touched.** ⚠ **The latest-run default is DELETED, not corrected** —
   a default that silently picked id=4 is the `or "resolved"` class. `--load` gains a **required**
   `--ranking-run`; `--fill-feature-7` needs none because it creates no rows.

### Tests first

| Test | Assertion | Prove it bites by |
|---|---|---|
| ⚠ `test_fill_updates_and_never_inserts` | Row count identical; **80 before, 80 after** | Restoring `session.add(...)` → red on the count |
| `test_fill_writes_only_feature_7` | Every other column byte-identical per row | Writing a second column → red |
| `test_a_changed_feature_1_to_6_aborts_the_whole_fill` | Seeded drift on one row → raises, **nothing written**, row named | Writing the rows that matched → red |
| `test_load_requires_an_explicit_ranking_run` | `--load` without `--ranking-run` refuses | Restoring the latest-run default → red |
| `test_fill_is_idempotent` | Second run writes zero rows and says so | Re-writing → red |

⚠ **The third test is the load-bearing one.** *Fix what is broken and abort on everything else* is
the whole difference between this and the command that would have corrupted the table.

**⚠ A clean 80/80 match on features 1–6 is itself a result worth reporting** — it demonstrates the
extraction pipeline is deterministic across every code change since #109. **If it does not match,
that is a finding about the instrument and it outranks D-075.**

---

## §3 — TASK C · Run the fill (production write — owner at the keyboard)

Owner merges A and B first. Then, **owner in the proxy window:**

- **Dry run first** — `--fill-feature-7` with no write, reporting what it would change and the
  1–6 comparison. ⚠ **If any row's 1–6 differ, STOP. Do not proceed to the write.**
- Then the write.

**Then Code verifies independently**, two facts read separately:
- `count(*) FROM protein_features` — **must equal the pre-fill count.**
- `count(*) WHERE membrane_proximal_sasa IS NOT NULL`, **and the same count restricted to the
  ranking set.**

⚠ **The owner's reading is not Code's reading.** Same discipline that corroborated 0007-unapplied and
then 0007-applied today.

---

## §4 — TASK D · Re-run the refusal. It must now proceed.

**`--ablate geom_proxy` against production again.**

- **Task A's demonstration was the red. This is the green.** Report both outcomes together as one
  before/after pair — that pair is the evidence F-020 is closed under D-074 (*a finding is not closed
  until the instrument no longer exhibits it*).
- ⚠ **Stop at the point where the guard passes.** **Do not let the run continue into Run A.** Run A
  is governed by `ORDERS-Code-2026-08-05-D-075-run.md` and needs its own unhurried window with the
  frozen interpretation open.

---

## §5 — Out of scope

- **No Run A.** Its own order, its own session.
- **No re-fit, no touching `ranking_run` id=2, id=3, or id=4.**
- **No general-purpose updater.** `--fill-feature-7` writes one column; a general updater is a
  larger blast radius than the defect.
- **No census work, no migration 0008, no UI.**
- **⚠ No hand-written SQL against production**, by anyone, for any of this.

## §6 — Done when

Guard green and **demonstrated refusing against live production with `ranking_runs` unchanged** ·
fill mode landed with the abort-on-drift test proven by revert · dry run clean on features 1–6 ·
fill executed by the owner · non-null count verified independently by Code · **the same command that
refused now proceeds** · both readings reported as one pair · F-020 and F-021 written with their
numbers confirmed against `RESERVED.md` · gate green · **Run A not started.**
