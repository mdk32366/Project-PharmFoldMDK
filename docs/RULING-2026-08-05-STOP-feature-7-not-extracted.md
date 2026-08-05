# RULING — 2026-08-05 — STOP confirmed. Run A does not start tonight, and the obvious remedy is unsafe.

> **Binding. Supersedes the run authorisation's expectation that Run A follows the 0007 apply.**
>
> **Found by Code**, post-migration, 2026-08-05 — the extraction gap. **Verified by the Planner
> line-by-line against the tree**, which surfaced **three further defects in the remedy Code
> proposed.** ⚠ **The prescribed fix would have silently corrupted `protein_features`.**

---

## §1 — Code's finding: confirmed exactly, at every link

`protein_features`: **80 rows, `membrane_proximal_sasa` NULL on all 80.** The column exists; nothing
populated it.

| Link | Verified | Effect |
|---|---|---|
| `scripts/fit_scorer.py:111` | `float(rec.membrane_proximal_sasa or 0.0)` | **NULL → 0.0 on every ranking-set row.** |
| `scripts/fit_scorer.py:114-121` | `print(f"WARNING: …")` | ⚠ **Prints and proceeds.** Its own text says *"a 0.0 placeholder here would be an imputed value (D-027)"* — and then imputes it. |
| `core/scorer.py:152` | `… / self.stds[j] if self.stds[j] > 0 else 0.0` | Zero variance → **0.0 for every row.** No crash, no NaN. |

**So `geom_proxy` collapses to `no_plddt` plus one inert dimension.** The run would land at or beside
**0.5625 / 0.5893 / 6-of-12** — Decision 4's **second row**, the ambiguous one the log names as the
expected case at n=12.

⚠ **And it would fire for the wrong reason.** Not *"the SASA proxy did not recover the signal"* but
*"the proxy was never computed."* **The artifact would be indistinguishable from a real
pre-registered outcome** — same `run_kind`, a plausible triple, 56 WARNING lines scrolled off above
it, and nothing red anywhere.

**This is the day's defect shape arriving inside the run the whole day was sequenced to protect:**
an absent value coerced to zero, producing a plausible artifact instead of an error. **Code stopped
at the one place where the smoothing would have been unrecoverable — a fabricated scientific result
carrying full provenance.**

---

## §2 — ⚠ The proposed remedy is unsafe. Three defects in `extract_features.py --all --load`.

Code proposed the owner run the extractor tonight. **Verified against `scripts/extract_features.py`
lines 163-197, that would do three things nobody intends:**

1. **It INSERTS; it does not update.** `session.add(ProteinFeatures(...))` per record, **no delete,
   no upsert.** `protein_features` holds 80 rows. `--all --load` makes it **160**, in two
   generations, and `fit_scorer`'s assembler would then have to pick between them.
2. **It rewrites features 1–6, not just feature 7.** Every column is recomputed and written fresh.
   ⚠ **F-004's stored result is safe** — `ranking_run` id=2 is read from its row, never recomputed —
   **but F-004's inputs would no longer be reproducible from the database.** The result would
   survive; its derivation would not.
3. **`ranking_run_id` defaults to the LATEST run** — `order_by(RankingRun.id.desc()).first()`, which
   is **id=4 (`plddt_only`)**, not id=2. The docstring calls it *"the run the analyses belong to"*,
   an assumption that was true when one run existed and is **false now that four do.**

**⚠ Note the shape.** The remedy for a null-coerced-to-zero defect was a command that would have
duplicated the feature table and bound the new rows to the wrong run. **It looks like the obvious
fix, it runs clean, it prints a row count, and nothing reddens.** Third instance today of a step
whose failure mode is a plausible artifact.

---

## §3 — RULING

1. **Run A does not start.** Not tonight, not until feature 7 is measured on the ranking set and
   verified non-null **by an independent reading.**
2. **⚠ `extract_features.py --all --load` is NOT run against production in its current form**, by
   the owner or by Code. This overrides §2's option 1 in Code's report.
3. **⚠ No hand-written `UPDATE` against production.** A one-off SQL write with no test, executed
   late in a long session, against the table the graded result derives from, is worse than the
   defect it fixes.
4. **The remedy is a code task with tests, a PR, and an owner merge** — Code's normal path. It is
   **not** an owner keystroke. Required behaviour:
   - **Update in place**, keyed by `analysis_id`. Row count before == row count after, asserted.
   - **`--ranking-run` explicit and required for `--load`.** ⚠ The latest-run default is removed,
     not corrected — a default that silently picked id=4 is the same class as `or "resolved"`.
   - **Features 1–6 byte-identical before and after**, asserted per row. Any drift is a
     **stop-and-report finding**, not a value to accept.
   - **Red-then-green in the corrected form (A-016):** a realistic mistake, failing at the
     assertion. The insert-instead-of-update revert must red on the row count.
5. **⚠ `--ablate geom_proxy` REFUSES to run** if any ranking-set row has a null feature 7. **Raise,
   not warn.** ⚠ **Scoped to the named ablation, not to the fit** — the pre-registered six-feature
   path legitimately has no feature 7 and must keep running untouched. **A guard that reddens the
   pre-registered path is a worse defect than the one it fixes.**
6. **Two new findings, separate numbers**, because they are in different subsystems with different
   consequences:
   - **`F-020`** — *an absent measurement coerced to zero and fit as though measured; a guard that
     names the defect in its own warning text and proceeds anyway.* ⚠ **Distinct from F-018**: that
     is a vocabulary defect in the identity path costing a miscounted census row; this is in the fit
     path and costs a fabricated result.
   - **`F-021`** — *a loader that inserts where it must update, rewrites inputs it was not asked to
     touch, and binds to the most recent run by default.*
7. **Environment findings** — `fly-user` cannot read `pg_stat_activity` on Managed Postgres;
   `env.py` sets no `connect_timeout`. **Land with the F-017 commit as Code proposed.**
8. **`plddt_only` (id=4) stays outside Decision 4's reading.** Confirmed by Code, restated once
   because §2.3 has now put its id in front of everyone twice.

---

## §4 — What this costs, stated plainly

**D-075 slips again — the fifth deferral — and this one is not a scheduling choice.** The
pre-registration was executable in principle and its input has never existed. **That was invisible
from every document, including the run order, which assumed the extractor had run since #109 merged.**

⚠ **The order's §0 had five confirmations and none of them checked whether feature 7 had a value.**
It confirmed the column's migration, the fixture's bite, both anchor runs, and the sealed
interpretation — **and not the one fact that decides whether the run means anything.** That is the
Planner's gap, not Code's.

**What was actually bought tonight:** 0007 applied and verified two ways · the whole fit chain traced
and three live defects found in it · the remedy's own hazards found before execution · and a
fabricated `ranking_run` with full provenance **not** written to the database.

**A run that would have produced the expected row for the wrong reason, nine days before it is
presented, is the single most expensive thing that could have happened today.** It didn't.
