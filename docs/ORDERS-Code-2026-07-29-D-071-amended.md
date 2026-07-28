# Orders for Code — D-071 (amended): fill the environment fields from one measurement, keyed by tier

> **⚠ SUPERSEDES `ORDERS-Code-2026-07-29-D-071-tier-environments.md`.** Banner in place if it
> reached you; if it didn't, this is the only version.
> **Scope:** `data/tier_environments.json` (new), `app/reads.py`, `ui/src/components/Provenance.jsx`,
> tests, `docs/`.
> **NOT in this PR:** new routes, `system-model.json`, migrations, `worker/`, any re-fold, any
> database mutation.
>
> **One measurement fills 42 folds.** The record is keyed by **tier**, not by target — every local
> fold renders from the same entry. There is nothing per-fold to gather.

---

## §0 — Two checks, reported before any build

### 0a — Does D-070's block render live?

Both screenshots of the panel were cropped at exactly the line where D-070's *"what we can say"*
block should begin. **It has never been confirmed live.** Scroll past the crop on a pre-D-045 fold,
or grep the served bundle.

**Not rendering → that is a live defect from #99, report before anything else.**

### 0b — Which tier do the frequently-clicked targets sit on?

```sql
SELECT meta->>'tier' AS tier, COUNT(*)
FROM protein_analyses WHERE mean_plddt IS NOT NULL GROUP BY 1;
```

…and the tier split of the **top 20 rows of `target_scores`** for the pre-registered run.

**Why it matters:** a reader arrives at a target page from the ranking table. **If the top-ranked
targets are mostly rental, this PR fills 42 pages nobody opens** — and a presentational fix to
state 3 would be the better spend. **If they are mostly local, this fixes the pages that get
looked at.** Report the split; it does not change the build, it changes what the owner does next.

---

## §1 — Measure the local tier, once, and report

On the fold host, in the worker venv:

```
python -c "import torch, transformers; print(torch.__version__, torch.version.cuda, torch.cuda.get_device_name(0), transformers.__version__)"
```

**Report verbatim before writing it anywhere.**

**⚠ Compare against `worker/requirements.txt`'s `torch==2.11.0+cu128`**, whose header claims it was
*measured on the RTX PRO 2000* — this box. **A disagreement is a second F-007, on the tier the pin
was supposedly taken from, and it outranks this PR.**

**The owner's basis for one reading covering all 42:** same box, same venv, folded within one
working week, no reinstall in between. **Sound — and the qualifier in §2 decision 1 carries the
residual uncertainty rather than hiding it.**

---

## §2 — The entry

### D-071 — Provenance strength is three-valued: measured at fold time, measured later, or absent

- **Date:** 2026-07-29
- **Status:** Proposed → Accepted on merge.
- **Amends:** D-070 decision 2.
- **Relates:** D-045, D-048, D-070, F-007, F-008, D-016.

**Context.** 75 of 79 folds carry no environment record. D-070 ruled that **inferred** values never
enter the captured fields — correct, because F-007 showed the pinned manifest disagreeing with a
measured fold.

**But a reading taken off the fold host is not an inference.** It is a measurement of the same
machine, taken later. **Weaker than fold-time capture, far stronger than a manifest.** D-070
collapsed the two, and the distinction is worth having.

#### Decision (1) — three states, ordered by strength, each labelled

| Strength | Source | Renders |
|---|---|---|
| **1 — measured at fold time** | the fold's own `fold_provenance` (D-045) | the four fields, unqualified |
| **2 — measured later, same tier** | `data/tier_environments.json`, keyed by `tier` | the four fields, **with date and qualifier** |
| **3 — absent** | neither | `not captured`, plus D-070's block |

**⚠ State 2 is visually distinct and says what it is:**

> *tier environment, measured {date} — not recorded at fold time*

**A reader must never have to work out which kind of claim they are looking at.**

#### Decision (2) — ⚠ AMENDS D-070 decision 2

> **Inferred values never enter the captured fields. A measurement may, with its date and scope
> stated.**

The distinction is **reconstruction versus observation**, not fold-time versus later. D-070's
reasoning was aimed at the manifest and over-reached to cover a reading off the machine. **Recorded
as a Planner over-application** — the same shape as the precedence ruling that over-applied from
IGF2R to TMEM108.

#### Decision (3) — ⚠ the rental tier gets NO state-2 record, deliberately

Local is measurable: the box exists. **The rental pod does not** — RunPod instances are ephemeral
and the 33 uncaptured rental folds ran on instances that are gone.

**⚠ The 4 captured rental folds must NOT populate the other 33.** They describe **those** folds, on
**that** instance, on 2026-07-25. Applying them elsewhere is reconstruction wearing a measurement's
clothes.

**Local fills; uncaptured rental stays at state 3.** The asymmetry is correct and informative:
**ephemeral compute costs provenance you cannot get back.**

#### Decision (4) — the artefact is a measurement with its own provenance, not a copy of the manifest

`data/tier_environments.json` records what was **read off the machine**, with `measured_at` and a
note that it post-dates the folds. **Not a copy of `worker/requirements.txt`** — F-007 is why those
are different things — and the manifest's contents are still never rendered (D-070 decision 3
stands). `data/` ships in the runtime tier, so no DEP-001 problem.

- **Deep-learning justification.** F-008 established the cohort was folded under two precisions
  confounded with length, and that features 3–4 — which carry the signal per F-005 — are
  tier-shifted. **A reader cannot evaluate that without seeing what each tier ran.** This panel
  makes F-008 checkable rather than asserted.

- **Consequences / test surface:**
  - All three states render, each pinned by a fixture.
  - **State 2 never renders without its date and qualifier** — asserted.
  - **State 1 is never overwritten by state 2** — a captured fold ignores the tier record.
  - **No rental tier record exists** — asserted, so a future edit cannot quietly add one.
  - **One local record serves all local folds** — asserted with two different local fixtures.
  - Constraint-A: no version string, device name or date typed into a component.
  - D-070's block still renders for state 3.

---

## §3 — Build

1. `data/tier_environments.json` — **local only**, from §1, with `measured_at` and the note.
2. `app/reads.py` — the **detail** projection gains `tier_environment`: the record for that row's
   `tier`, or `null`. **A field on an existing route — no new route, no `system-model.json` edit.**
3. `Provenance.jsx` — the three-state render.
4. Tests, gate, readability delta, owner merge.

## §4 — ⚠ What will bite

1. **Do not populate rental from the 4 captured folds.**
2. **Do not read `worker/requirements.txt`** — the value comes off the machine.
3. **Do not let state 2 render unqualified.** The qualifier is the entry.
4. **Report §0 and §1 before writing anything**, including any disagreement with the pin.

## §5 — Owner copy call

The state-2 qualifier. Proposed: *"tier environment, measured {date} — not recorded at fold time."*
**Short by design; it sits under a value, not beside a paragraph.**
