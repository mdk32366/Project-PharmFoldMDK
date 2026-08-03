# Pre-Work — next session (the run session)

> **Grounding:** confirm main with `git log --oneline -1` (expect **3fe61b9** or later). Read first:
> `CLOSEOUT-2026-08-01-execution.md`, then `docs/README.md` for the D-075 entry and its **sealed
> Decision 4** (merged #109 — this is the frozen interpretation; it cannot be amended).
> **Character of this session:** the last session *built and sealed* the ablation. This session
> **runs it** — the single act the whole D-075 apparatus was constructed for. It is a short,
> high-consequence session: apply one migration, authorise one run, read the result against an
> interpretation that is already frozen. **The reading is not up for negotiation — it was decided
> before the numbers existed. This session executes and records; it does not re-interpret.**

---

## §0 — Before the run: two owner-gated prerequisites

Neither is Coder's to do unilaterally. Both are the owner's verified steps.

1. **Apply migration 0007** (`membrane_proximal_sasa`, additive/nullable/no-backfill). DATABASE_URL
   points at live prod. **Verify by the search-path hazard, not by alembic's exit code** — the known
   failure mode is `search_path SET` running before `context.begin_transaction()`, which SQLAlchemy
   2.0 silently rolls back. Confirm the column exists in prod after, by inspection, not by trusting
   the migration's return.
   - **Why this is step one, not run-time:** the #112 deploy already shipped `db/models.py` declaring
     `ProteinFeatures.membrane_proximal_sasa`, but the column does not exist in prod (0007 unapplied).
     There is now a live window where the deployed ORM describes a column the DB lacks. It is harmless
     today *only because the serving path never queries `ProteinFeatures`* (app imports JobRecord,
     ProteinAnalysis, RankingResult, RankingRun, TargetScore — verified by hand, not enforced). Any
     future change that adds a `protein_features` query to serving would 500 until 0007 is applied.
     Applying 0007 first shuts that window. **Consider a guard or a written note that the safety of
     this window rests on an import-graph fact that nothing currently enforces** — a hand-checked
     invariant is one careless query from breaking.
2. **Confirm the pre-registration is intact.** Re-read the sealed Decision 4 in `docs/README.md`. The
   run's whole validity rests on the interpretation having been frozen before the numbers — verify it
   reads exactly as merged (#109), unmodified. If it differs, **stop** — something amended a sealed
   pre-registration, which is a D-011 violation and a bigger problem than the run.

---

## §1 — The run (the session's reason to exist)

Authorise, then execute per the D-075 order. Coder runs; owner authorises each step.

1. **geom_proxy ablation.** Refit on the 5-feature confidence-blind set, same λ/LOO mechanic, same 12
   positives, same floor. Produces the 12 LOO percentiles, median/mean/count, head-to-head on the 8,
   and Spearman. Writes its own `ranking_run`, `run_kind='sensitivity'`, tagged. **F-004 (id=2) not
   re-run, not touched.**
2. **Attention control.** `--freeze` snapshots both proxies (PDB-presence, publication count) once
   with query template + stated date; `--control` reads only the snapshot. **Freeze before the
   control reads.** Runs against both proxies separately — a sensitivity pair, not one number.
3. **Read the result against sealed Decision 4 — and ONLY against it.** Have the frozen table in front
   of you before looking at the numbers. The six outcome rows are already written; the run selects
   which one fired. **Do not invent a seventh reading, a threshold, or a "clarifying" third proxy to
   resolve an ambiguous result** — ambiguous is a pre-registered, legitimate outcome (Decision 4 row 2).

## §2 — Record the result

- Land the result as its own **F-entry** (the next free F-number — the D-075 order reserved "eventual
  result as a later F-entry," unassigned until now). It **cites D-075, does not amend it.**
- Report median / mean / count side by side; read three-against-three (toward-FULL vs.
  at-no_plddt-baseline); attach the attention-proxy results **per target** so "survives" cannot be
  claimed on the back of the attention-rich targets.
- **If it collapses (Branch B):** report it prominently — that is the finding, and it was
  pre-committed to be reported as prominently as survival. Better found by the run than by a reviewer.
- Through the gate, no silent edit. If the headline changes, the deck/lit-review result sections
  update from the result entry — flagged, not quietly.

## §3 — ⚠ The UI honesty-gap question (answer after the run, do not pre-build)

**The observation that prompts this:** after a session of substantial work, the deployed app is
byte-identical — `app/` and `ui/` untouched, F-004 still served unchanged. That is *correct* for the
ablation (no result exists yet, so nothing to show). But it surfaced a real question worth answering
deliberately: **is the deployed app as honest about its limitations as the decision log is?**

The project's stated success criterion is that the UI surfaces what the system *cannot* do as
prominently as what it can. Two facts are now known and committed to the log but **not visible in the
app** — and both were true *before* the run, independent of it:

1. **The cohort boundary (F-009).** The app presents a ranking over 82 targets. It does not surface
   that the 82 is a *comparator, not a census* — that clinically-validated ADC targets (CD30, CD33,
   CEACAM5, Trop-2) are excluded, including the target of the first ADC ever approved. That is a
   computed, verified honesty fact sitting in a CSV and F-009, not on screen. A "what this cohort is
   and isn't" note would surface it. **This gap exists regardless of the run's outcome.**
2. **The confound.** The app shows the F-004 result. Does it show, with equal prominence, that the
   result has a named pLDDT-attention confound? If not, **the deployed app is currently less honest
   than the decision log** — it presents "structural axis ranks targets" without "and we have not yet
   ruled out that this tracks research attention." That is precisely the gap the project exists to close.

**Why this is a post-run question, not a this-session build:** the *right* thing to show about the
confound depends on what the run returns.
- **If geom_proxy survives:** the confound is substantially excluded, and the UI should say so —
  "the structural signal survives removal of confidence-derived features" is a *strengthening* the app
  should surface.
- **If it collapses (Branch B):** the honest UI change is larger — the result framing itself changes,
  and the app must say the structural enrichment is not separable from confidence/attention.
- **Either way, the confound's UI treatment is downstream of the run.** Pre-building it now would be
  guessing which branch fired.

**The ruling for the run session:** after the result lands (§2), **answer explicitly, as an owner
decision logged as its own entry:** *does the deployed app surface (a) the F-009 cohort boundary and
(b) the confound's post-run status as visibly as it surfaces the F-004 result?* If no, that is a
scoped UI honesty task — not feature creep, but closing the stated success-criterion gap. The
cohort-boundary note (1) can be specced independently of the run; the confound treatment (2) waits on
the branch. **Do not build either before the run resolves — surface the question, let the result
shape the answer.**

## §4 — The fork this opens

The run's result decides the paper (roadmap Part II):
- **Survives → Branch A.** Then Phase B (fold + validate the 20 held-out targets against the frozen
  F-004 model) unlocks — its order is written and sealed, ready to authorise. And roadmap Tier 1
  (expand positives past n=12) becomes the next priority.
- **Collapses → Branch B.** The cautionary-methods paper. Phase B is *abandoned, not deferred* (the
  held-out order §0 says so). The held-out CSV survives as F-009 evidence regardless.

**Do not pre-judge which branch.** The interpretation is sealed precisely so the run, not the hope,
decides.

## §5 — Carried-forward housekeeping (fold in when convenient, not blocking the run)

1. **D-072 → D-076 renumber.** `D-072-last-three-fold-plan.md` needs its number updated; the MANIFEST
   references it by unsuffixed name, so keep that reference resolving through the rename.
2. **id=1 `status_detail` mojibake** — its own tiny housekeeping entry.
3. **Lit-review citations** — verify Site4Drug (arXiv 2606.01816), add PNAS 2026 surfaceome paper,
   before the novelty claim is pitched.
4. **IGF2R fold (D-076 Tier 1)** — still the one cheap, ungated, no-asterisk coverage fold. Independent
   of the run; do it whenever a rental block is convenient.

## §6 — Start-here

1. §0 — apply migration 0007 (verify by search-path, not exit code; this also shuts the ORM/schema
   window from the #112 deploy); confirm sealed Decision 4 intact.
2. §1 — authorise geom_proxy + attention control; read against the frozen table, only against it.
3. §2 — land the result as a new F-entry citing D-075; per-target attention proxies attached.
4. §3 — answer the UI honesty-gap question: does the app surface F-009's cohort boundary and the
   confound's post-run status as visibly as the F-004 result? Log the answer as its own entry; spec
   the cohort-boundary note now if desired, hold the confound treatment for the branch.
5. §4 — the branch the result selects sets the next session (Phase B, or Branch B pivot).
6. §5 — housekeeping when convenient, none of it blocks the run.

**The through-line:** everything the last two sessions built converges on one number-producing run
whose meaning is already fixed. Apply the migration, authorise the run, read the sealed table, record
which outcome fired. If the axis survives without its confidence features, the headline is bulletproof
and Phase B opens. If it doesn't, the collapse is the finding — and it was pre-committed to be reported
as loudly as a win. Either way, the honesty was guaranteed the moment the interpretation was sealed
before the numbers. This session just turns the key.
