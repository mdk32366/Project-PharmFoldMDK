# PharmFoldMDK — Design Decision Log

> **This file is mandatory reading and mandatory writing.**
>
> **THE RULE:** *Every design decision we make gets written in this file **before** the
> work it describes is finished.* The log leads the code. If you are about to build,
> change, or discard something and the reasoning is not yet here, stop and record it
> first. A PR whose work is not reflected in a decision entry is incomplete.
>
> **THE SECOND RULE (provenance, D-016):** *Every claim names how it is known.* A written
> record fixes a claim in place; it does not make it true. Before a number or a status enters
> this log, ARCHITECTURE, or a PR, name the artefact it came from — the raw log line, the query
> output, the run URL. If you cannot name it, you are recording a belief, not a finding. A
> summary is not knowing: prefer the breakdown to the total, and **prefer the query whose answer
> could disqualify you** (`pg_available_extensions` tells you a thing *exists*; `pg_extension`
> only that it is *on* — a zero from the second cannot distinguish *absent* from *off*).
>
> Companion documents:
> - [`../ARCHITECTURE.md`](../ARCHITECTURE.md) — the current-state architecture (must be
>   updated in the same PR as any architectural change, and before any PR is filed).
> - The planning docs in this folder (TDD, DB plan, UI plan, test plan, checklist) — the
>   *original* intent. Where a decision below diverges from them, **this log wins**.

## How to add a decision

> **Numbering note: there is no D-010.** The sequence runs D-001…D-009 then D-011. Nothing was
> deleted — the number was simply skipped. Not renumbered, because commit `c07b95b` already
> references D-011 by name. Spike entries use `S-NNN` and instrument/method findings use `F-NNN`.

Add a new `### D-NNN` entry at the **top** of the log (newest first). Use the template:

```
### D-NNN — <short title>
- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Superseded by D-XXX | Rejected
- **Context:** why this came up.
- **Decision:** what we are doing.
- **Deep-learning justification:** how this serves (or is neutral to) the DL-core mandate.
- **Consequences:** trade-offs, follow-ups, what it touches.
```

Every substantive decision must state its **deep-learning justification** — this is a
deep learning course project and the neural core is the graded deliverable (see
ARCHITECTURE §1).

## Method note: state a check precisely enough that its inadequacy is discoverable

Learned the hard way on 2026-07-19 (see S-001 and S-002, where two confidently-stated claims were
caught and reversed):

- **`params_all_on_cuda=True`** was a *true* summary that missed **spill** — every parameter really
  was on CUDA, while the allocation silently exceeded physical VRAM.
- **"217 WHEA events since May"** was a *true* summary that missed **severity** — 213 were
  corrected, only 4 fatal, and the fatal signature had no history at all.

Both errors came from **accepting a summary instead of returning to the raw records**, and both
were caught only because the check had been stated specifically enough to be *shown* inadequate.
So the rule is not "be careful" — it is:

1. **Write the check as a concrete assertion with units and a threshold**, so a later reader can
   test whether it actually covers the claim ("resident MiB vs *free* MiB", not "does it fit").
2. **Bucket before you count.** A total is compatible with more hypotheses than a breakdown is;
   prefer rates and severity splits to raw counts.
3. **Label inference status explicitly** — *measured* / *predicted* / *assumed* — and never let a
   *predicted* mechanism be cited later as a finding.
4. **Record the provenance chain when a claim changes**, including the wrong intermediate versions.
   The reversal is itself evidence about how much the current version should be trusted.
5. **Before using a metric as a *leading indicator*, verify its events actually PRECEDE the thing
   it predicts.** (Added 2026-07-19 after **F-001**.) WHEA corrected-error rate was used for hours
   as an early-warning signal for host crashes; per-second timestamps then showed the fatal is
   logged *in the same second* as the corrected errors, and that six burst days with 65/40/31
   corrected errors produced **zero** crashes. The metric was **anti-correlated** with its target.
   A metric can be real, well-defined, correctly queried — and still measure the *aftermath* of the
   event you meant to predict. **Check the time-ordering, not just the correlation.**
6. **Prefer the instrument-free comparison when one exists.** The strongest result in this whole
   investigation needs no event log at all: *4 crashes in 4 HER2 attempts, 0 in ~93 Trop-2 folds.*
   When a raw outcome count is available, it outranks any derived telemetry.

7. **⚠ A POINTER IS NOT PROOF OF ITS TARGET — and the sharpest case is the record pointing at itself.**
   (Added 2026-08-03 after **D-062**.) This project keeps re-learning one shape in different clothes:
   a *reference* to a thing is taken as evidence the thing exists and is sound.
   - **A green check is not a working system** — the gate proves the tests it has, not the behaviour.
   - **A summary is not the records** — `params_all_on_cuda=True` was true and missed spill;
     *"217 WHEA events"* was true and missed severity (S-001/S-002).
   - **A hash from an hour ago is not the file now** — re-verify immediately before a destructive act.
   - **A filename is not an identity** — a basename match nearly overwrote the 605 KB decision log with
     an unrelated project's `README.md`.
   - **A cited path is not a tracked file** — `intersection_check.py` was cited as provenance from a
     path that did not exist (D-073/D-074).
   - **⚠ AND: a commit message naming a decision is NOT evidence the decision was logged.** PR #90 was
     titled *"F-004 + D-062: … the scorer surface that renders it"*, and its diff added `### F-004` and
     **no `### D-062`**. Thirteen later citations then referred to D-062 as settled authority. **The
     record referred to itself into a false sense of completeness** — the most dangerous member of this
     family, because every other item is a pointer from outside the log into the world, where reality
     eventually pushes back, while this one is a pointer from the log into the log, where nothing does.
   - **The general rule: to confirm a thing exists, look at the thing — never at a reference to it.**
     For log entries that is one command: every cited `D-NNN`/`F-NNN` must have a matching `### ` entry.

   **⚠ STATE OF THE INVARIANT — do not assume it has always held.** As of **2026-08-04** every cited
   `D-NNN`/`F-NNN`/`S-NNN`/`DEP-NNN` in this log and in `ARCHITECTURE.md` either resolves to a real
   `### ` entry **or is listed in [`RESERVED.md`](RESERVED.md)**.

   **The distinction the register exists to hold.** A *forward* reference to an entry that announces
   its own absence is not the D-062 defect — D-062's harm was that thirteen citations treated a missing
   entry as **settled authority**, and nothing in the text suggested it was missing. A reference that
   says *"this is not written yet"* cannot do that. **But it is indistinguishable from the defect to a
   checker.**

   **That is why the exceptions are a file and not a paragraph.** This note first carried them as prose
   — one exception (`D-010`), then two (`D-078`), and within a day the set was five. Prose kept the
   property *"an undocumented miss is a real finding"* true only while the set was small enough to
   remember; `RESERVED.md` keeps it true as the set grows. **The checker whitelists that file and
   nothing else, and an unresolved reference not listed there is a finding immediately** — same class
   as D-062, found early. The command is in the register; **read its output, not its exit code.**

   **This closed state was RESTORED on that date; it did not hold before it.** Two holes were repaired
   the same day: **D-062**, cited **13 times** as the authority for a shipped surface with no entry
   (back-filled from artefacts and permanently marked as such), and **F-009**, cited by shipped UI and
   by `ARCHITECTURE.md` while existing only as a staged document (landed from that document, so sourced
   rather than reconstructed). **Both had accumulated citations for days without anything objecting** —
   which is the asymmetry above in practice.

   **What a future session should take from this:** the invariant is *maintained*, not *guaranteed*.
   Nothing in the gate enforces it — the check is deliberately **named, not built** (D-074 dec 3: do
   not answer a finding with a framework that becomes a second thing to drift). So **re-run it rather
   than trusting this paragraph** — which is itself only a pointer, and therefore not proof of its own
   target. Running it is one command; it found two holes the first time it was run.

---

## Log (newest first)

### F-017 — The confidence-blind structural axis recovers what `no_plddt` lost: Decision 4 row 1 fired, and the proxy that never reads confidence is nonetheless correlated with it

> **The fired row, quoted from `docs/README.md` §D-075 Decision (4), before any prose:**
>
> | **All three of `geom_proxy`'s statistics sit toward FULL** (median ≳0.6071, mean ≳0.6176, count 8-of-12) — the proxy recovers what `no_plddt` lost | **Confound weakened.** The signal is geometric accessibility, not confidence. The membrane-proximal information matters; its *pLDDT encoding* was not what carried it. |

**Cites D-075 and F-004. Amends neither.** F-004 stands as the record of the six-feature pre-registered result. D-075's frozen interpretation selected this reading before the number existed.

#### The triple, three-against-three (D-041 dec 4 — never one statistic)

| Run | median | mean | count ≥0.5 |
|---|---|---|---|
| **`geom_proxy` (id=5)** | **0.6607** | **0.6324** | **8-of-12** |
| FULL anchor (id=2) | 0.6071 | 0.6176 | 8-of-12 |
| `no_plddt` baseline (id=3) | 0.5625 | 0.5893 | 6-of-12 |
| *`plddt_only` (id=4) — not an anchor* | *0.6786* | *0.6295* | *9-of-12* |

All three of `geom_proxy`'s statistics clear the row's stated `≳` against FULL. **No threshold was invented; the row's own condition is the test.** This is not the ambiguous row and not the split row.

Twelve LOO percentiles: `0.1339 · 0.4732 · 0.4732 · 0.4732 · 0.6339 · 0.6518 · 0.6696 · 0.6875 · 0.6875 · 0.7946 · 0.9375 · 0.9732`. The triple was **recomputed from these by the Planner, independently of the run**, and reproduces to full float precision. `n_ranking_set` 56 · `n_fit_positives` 12 · `loo_status` complete, twelve folds converged · `scorer_version` `5ccab48772b5` · `geom_proxy` = 6 parameters (5 features + intercept).

Head-to-head over the **8 overlapping** targets — overlap with the two-valued evidence comparator, **not** a convergence count; all twelve folds converged. Spearman **+0.0483**, the same magnitude as FULL's with opposite sign, and **read as evidence of nothing** per Decision 4's dead-discriminator clause, whose quantisation behaviour the log predicted in advance.

#### ⚠ Three things this result does NOT license

1. **`geom_proxy`'s median exceeds FULL's. That is not a finding and is not reported as one.** The gap is **3.00 × (1/56)** — three of the finest increments the ranking set can express — and the median falls between the 6th and 7th sorted values, so one target's rank moves it. Decision 0.1–0.3 named this fragility before the run. **Decision 4 has no row for "better than FULL"; the row says *toward*.** Five features outscoring six at n=12 is within noise.
2. **`plddt_only` (id=4) carries the highest median and count of any run.** It is correctly not an anchor and Decision 4 does not use it. **It is reported here because omitting it would misrepresent the result.** The fired row's reading concerns *this comparison*; it is **not** a finding that confidence carries no signal — id=4 shows plainly that it does. The row's own second sentence is the synthesis: the membrane-proximal information matters, and its *pLDDT encoding* was not what carried it. **Two encodings of one quantity, both of which work.**
3. **F-005 is refined, not reversed, and is not amended.** F-005 remains true as recorded: remove pLDDT and the signal drops (id=3, 0.5625 / 0.5893 / 6-of-12). What is new is that **a single confidence-blind membrane-proximal feature recovers it.**

#### ⚠ The residual confound — measured, and it narrows the claim

Feature 7's confidence-blindness is **architectural**: `Atom` carries no `b_factor`, `parse_pdb` never reads columns 60-66, and the contaminated fixture reds on both arms — differing pLDDT *values* (11.1442 vs 88.1873) and differing pLDDT *array length* (11.1442 vs 12.2295). **The code cannot see confidence. That is proven, not assumed.**

**Blindness at the input is not independence at the statistic.** Feature 7 is computed over coordinates ESMFold itself produced. Measured over the 56 ranking-set rows, no nulls:

| | Pearson | Spearman |
|---|---|---|
| feature 7 vs feature 4 (`membrane_proximal_plddt`) | **−0.4898** | **−0.5490** |
| feature 7 vs feature 3 (`mean_plddt_ecd`) | **−0.6208** | **−0.4694** |
| *control:* feature 4 vs feature 3 | +0.7959 | +0.7695 |

⚠ **The confidence-blind proxy is confidence-correlated** — moderately to strongly, negatively, in the mechanistically expected direction: more exposed membrane-proximal SASA goes with lower pLDDT, because ESMFold is less confident where structure is less packed. It sits well below the two confidence features' correlation with each other, and nowhere near zero.

**This does not change which row fired, and it could not have selected it** — the measurement was specified before it ran and its interpretation was fixed in advance in both branches. **But it binds the claim.** The supportable statement is: **feature 7 recovers the membrane-proximal signal without reading confidence — not free of confidence.** Architecturally blind is proven; statistically independent is **measured false**.

**Instrument note.** These coefficients are a property of **this cohort as folded, at one recipe composition** — not a constant of the features. See D-075 Decision 6. They must not be cited as a general figure.

#### The attention control, and a disclosure that is not softened

Run B is blocked: `scripts/attention_control.py --freeze` is a deliberate stub. PR #109 shipped the assembly seam and not the network fetchers. **The snapshot protocol was pre-registered at `73bca8f`, before this result existed.** Under its §3, **Run A survived — so the proxies will be frozen knowing Run A survived.** That sentence goes on the snapshot's face and stands here. The query template and endpoints were already committed constants; **what is post-result is the data pull, and the rules governing that pull were fixed before the result existed.**

#### How this is known (D-016)

Run executed by Code against live production, 2026-08-06, from `ORDERS-Code-2026-08-05-D-075-run.md`. All governing §0 confirmations passed, including the confidence-blindness fixture's contaminated arm reddening on **both** arms.

**Two cross-version checks cleared beforehand.** `no_plddt` and `preregistered` each reproduced their stored anchors under today's `scorer_version` `5ccab48772b5`, so the boundary between id=2's `91e646e4a289` and the current scorer — opened by D-075 making the projection unconditional — is **closed by measurement rather than documented as closed**. ⚠ The first such check was specified against `no_plddt`, which had always projected and therefore could not have detected the change; the Planner corrected the specification to test `preregistered`, the arm that actually changed.

Post-state matched two independently written pre-registrations term for term: `ranking_runs` (4,4) → (5,5) · `ranking_results` 4 → 5 · `target_scores` 168 → 224 · `protein_features` unwritten, feature-7 non-null 79 → 79 · **id=2, id=3 and id=4 byte-unchanged**. No void condition fired.

**Every production number above is Code's reading. The Planner has no database access and recomputed only the triple from the twelve percentiles.**

Denominators, each stating its key, **never summed**: cohort of record **82** (Kathad-2024-PLOSONE) · rows carrying `protein_features` **80** (two named exclusions never enqueued, D-026) · ranking set **56** · excluded **24 of 80** (`held_out`, `below_floor`, and IGF2R `not_folded`).

---

### F-020 — An absent measurement coerced to zero and fit as though measured: `--ablate geom_proxy` would have returned D-075 Decision 4's ambiguous row for the wrong reason

- **Date:** 2026-08-06 (the defect was found and the guard shipped 2026-08-05)
- **Status:** **CLOSED under D-074** — the instrument no longer exhibits the defect. See **Closure**
  below for what that rests on and who read it.
- **Type:** A **finding** about the fit path. It cost nothing in the end because it was caught before
  the run it would have corrupted; what it would have cost is the point of the entry.
- **⚠ Number verified, not inherited.** Reserved in `RESERVED.md` on 2026-08-05 **before** the fix, per
  the F-017 precedent (*a number contested mid-task is contested under pressure*). At the time of
  writing the highest `### F-` in this log was **F-016**; F-017, F-018, F-019, F-021, F-022 and F-023
  are reserved and unwritten. Confirmed by reading this file for a `### F-020` header, not for a
  reference to one (method note item 7).
- **Provenance (D-016):** the three code sites are quoted from the tree at
  `PharmFoldMDK-snapshot-2026-08-05-4b7547c`. **The closure evidence is Code's reading of the live
  database on 2026-08-05 and is attributed as such below** — it is **not** Planner-verified, and the
  Planner has no database access.
- **Relates:** **D-075** (the pre-registration this would have spent); **F-004** (the pre-registered
  result, untouched); **F-021** (the loader defect found in the remedy); **F-023** (the residual bare
  null the fill left); **D-074** (a finding is not closed until the instrument stops exhibiting it);
  **D-027** (null-with-a-reason, never an imputed value).

**⚠ This is not F-018, and the two must not be merged.** F-018 is a **vocabulary** defect in the
**identity** path — an absent status recorded as an affirmative one — and it costs a **miscounted
census row**. F-020 is in the **fit** path and it costs a **fabricated result**. They are the same
*shape* at different altitudes, which is exactly why a later reader will be tempted to collapse them.

#### The defect — three links, none of which reddens

Migration `0007` created `protein_features.membrane_proximal_sasa`. **Nothing populated it.** Feature 7
is a named input of the `geom_proxy` ablation (`FEATURE_SETS["geom_proxy"] = (0, 1, 4, 5, 6)`), so a
`--ablate geom_proxy` run would then have done this:

1. **`scripts/fit_scorer.py`** assembled the row as
   `float(rec.membrane_proximal_sasa or 0.0)` — **an absent measurement becomes `0.0`.**
2. **The same file printed a WARNING and proceeded.** Its own text read *"a 0.0 placeholder here
   would be an imputed value (D-027)"* — ⚠ **it named the defect and then committed it.**
3. **`core/scorer.py`'s standardizer** is
   `(features[j] - self.means[j]) / self.stds[j] if self.stds[j] > 0 else 0.0` — a **zero-variance
   column standardises to `0.0` for every row.** No crash, no `NaN`, nothing red.

**So feature 7 would have entered the fit as a constant and contributed exactly nothing.**
`geom_proxy` `(0, 1, 4, 5, 6)` collapses to `no_plddt` `(0, 1, 4, 5)` **plus one inert dimension.**

#### ⚠ Why this was the most expensive available failure

The result would have landed at the `no_plddt` baseline — **D-075 Decision 4's second row**, which
this log names as *"the expected case at n=12"* and reports as **ambiguous**.

**And it would have fired for the wrong reason.** Not *"the SASA proxy did not recover the signal"*
but ***"the proxy was never computed."*** The two are indistinguishable in the output: same
`run_kind='sensitivity'`, a plausible triple, and the WARNING lines scrolled off above it.

⚠ **A pre-registered run producing its most likely outcome, for a reason invisible in its own
artifact, nine days before it is presented.** The pre-registration cannot protect against this,
because the pre-registration is about *what the numbers mean* — not about whether the input existed.

#### The guard

`--ablate geom_proxy` now **raises** rather than warns when any ranking-set row lacks feature 7.

- **Scoped to the named ablation, never to the fit.** The pre-registered six have no feature 7 and
  legitimately never did. ⚠ **A guard that reddened the pre-registered path would make F-004
  unreproducible in order to protect an ablation** — worse than the defect it fixes.
- **Scoped to ranking-set rows.** An excluded row's placeholder is inert by construction.
- **It runs before `create_ranking_run()`**, so a refusal writes no run row.
- **`or 0.0` was removed, not guarded around.** A membrane-proximal SASA of exactly `0.0` is a
  legitimate measurement — a fully buried window — and `or` cannot distinguish it from an absence.

#### Closure — what it rests on, and whose reading it is

**⚠ Read and reported by Code, 2026-08-05, against the live database. Not verified by the Planner,
who has no database access.** Recorded this way because D-016 permits an attributed reading and
forbids an anonymous one.

> **Code's reading, 2026-08-05:** the same guard was demonstrated **refusing** and then, after
> feature 7 was measured, **passing** — same guard, same rows, **with the run table untouched on both
> sides.** The refusal named **56 of 56** ranking-set rows; `ranking_runs` read `(4, 4)` before and
> after each demonstration. The pre-registered six-feature path passed throughout, so **F-004 remains
> reproducible.**

**The D-074 basis, stated explicitly:** *a finding is not closed when the fix is written; it is
closed when the instrument stops exhibiting it.* The before/after pair — refusal, then pass, on the
same instrument against the same population — **is** that evidence. ⚠ **The fix having been merged
would not have been.**

#### What it changed about how this project works

- **A warning that names a defect and proceeds is not a guard.** It transfers the decision to whoever
  is reading stdout, at the moment they are least likely to be reading it.
- **The dangerous failures are the plausible ones.** Nothing here would have crashed. Three separate
  artifacts on 2026-08-05 had this property, and it is why `test_zero_eligible_rows_is_an_ERROR_not_a_result`
  exists: *a census where nothing is fetchable is not a census result; it is a broken pipeline wearing one.*
- **A pre-registration protects the interpretation, not the input.** D-075's §0 had five confirmations
  and none of them asked whether feature 7 had a value.

---

### D-079 — The census: ingest 2,807 surface proteins, tranche the crank, fold everything reachable at a recorded recipe — and spend none of the pre-registration on it

- **Date:** 2026-08-05
- **Status:** Accepted. **Ruled before any ingest.** This entry is the census pre-registration; **it is
  void if code precedes it** (D-075 / D-077 precedent). **No census row exists at merge**, and no
  census code is in the commit that lands this.
- **Type:** A **decision**. It rules an ingest design, fixes four denominators, freezes a fold order,
  and — the load-bearing half — **rules what a census fold may and may not license.** Results land
  later as their own F-entries.
- **⚠ Number verified, not inherited.** At merge the highest `### D-` entry was **D-077** and the
  highest `### F-` was **F-016**; `D-078` and `D-080` are reserved and unwritten. **Confirmed by
  reading the log for a `### D-079` header, not for a reference to one** (method note item 7).
- **Provenance (D-016):** `data/census/membraneome-reconstructed-2026-08-04.csv`, sha256
  `5a705cc9165eb863f51116c31f2a5f56080bf8941bf994a612f9d85fc6944d37`, counted at first hand on
  2026-08-05 — every figure below was read off that file, not carried forward. Six owner rulings of
  2026-08-05, plus the Planner rulings of the same date listed under **Rulings that bind this entry**.
- **Relates:** **D-075** (the pre-registration this must not spend); **D-077** (the local fold
  envelope — its decision-1 prohibitions are inherited whole); **F-008** (the reported cohort, not
  re-folded); **F-011** and **F-016** (the annex and the unclassified — different mechanisms, never
  pooled); **D-047** (recipe resolved at fold time, never hand-passed); **D-016** (every count states
  how it is known); **D-078** (reserved — it interprets the precision overlap this entry creates).

**⚠ Where the deep learning is.** The census exists to make one measurement possible that n=12
positives cannot support: whether the structural axis survives once research attention is controlled
for, at n in the thousands. **pLDDT is ESMFold's own confidence output and it is the signal carrier
(F-005)** — so a census statistic over pLDDT is a statement about what the network's confidence
encodes, not a database exercise. That is also exactly why decision 2's heterogeneity is not a
bookkeeping detail and why decision 7 exists: **a quantization artifact sitting inside the confidence
variable is sitting inside the measurement.**

#### Rulings that bind this entry, cited and deliberately not restated

This entry names *that* each rule exists and *why*; the mechanism, the named fixtures, and the
over-claim guards live in the ruling documents. **Restating them here would create the second copy
this project has spent the day removing** — the standing consequence of
`AMENDMENT-2026-08-05-D-079-census-key.md`: *where two sections name the same quantity, one cites the
other rather than restating it.*

| Ruling | Binds |
|---|---|
| `AMENDMENT-2026-08-05-D-079-census-key.md` | the census key; the two axes (`verification_bucket` is a finding, never a gate) |
| `RULINGS-2026-08-05-class-collision.md` | the fourth tag and the four denominators below |
| `SPEC-2026-08-05-accession-map-schema.md` | the two grains, parent and child, and the schema's move into code |
| `RULINGS-2026-08-05-task2-task3-contract.md` | the producer/consumer contract; `fetch_eligible`; F-018 |
| `RULINGS-2026-08-05-identity-status-collapse.md` | the status vocabulary and the collapse function |
| `RULINGS-2026-08-05-status-wins-over-span.md` | `_STATUS_WINS_OVER_SPAN`; `no_topology` requires a successful fetch; `FETCH_FAILED` |
| `RULINGS-2026-08-05-prose-vocabulary-retirement.md` | prose cites the constant; retired members survive nowhere |
| `RULING-2026-08-05-D-079-denominators-in-the-log.md` | why the figures below are written correct rather than superseded |

#### The four denominators — each stating its key

**The key is the distinct current accession** (`uniprot_current_accession`), because a SURFY
identifier is not a protein: four HLA loci absorb 83 source rows, and a census keyed by identifier
would weight one family 83-fold inside the confidence distribution that is the census's headline use.

| Tag | Count | |
|---|---|---|
| `surface` | **2,807** | the census |
| `non_surface` | **2,209** | the annex (F-011) — ingested under its own tag, never pooled |
| `unclassified` | **2,793** | a *different* exclusion mechanism (F-016) — **not evidence for F-011's thesis** |
| `class_conflict` | **2** | source entries disagree on class, so the protein has no SURFY class |

**Reconciling to 7,811 distinct accessions.** ⚠ **Four denominators, never summed** — the
reconciliation is a check, not a reportable quantity. A collapse that loses its inputs is a deletion,
so every row carries `source_identifiers`.

#### Decision (1) — the D-075 gate is **narrowed, not lifted**

A fold is a **measurement**; a score is an **interpretation**. D-075 protects the interpretation.

**Permitted:** ingesting rows with class, accession, span, band, recipe, tranche · folding at a
recorded recipe · reporting **cost, coverage, and confidence-distribution** statistics, each labelled
with tranche and recipe.

**Forbidden until D-075 fires:** no census row scored, ranked, or ordered by suitability — **no census
path imports `core/scorer.py` or the fitter, asserted by test and proven by revert** · no census
statistic presented as evidence about ADC suitability in any artifact, deck, or briefing · **no
refit** — `ranking_run` id=2 is read from its row.

#### Decision (2) — fold everything reachable; record the recipe on every fold; disclose the heterogeneity

**Owner ruling, 2026-08-05.** The census folds every target it can reach, at whichever tier reaches
it, with the recipe stated. **A census that stops at 440 aa is truncated on ECD length — feature 1 of
the pre-registered six** — which would answer a confound by introducing a selection bias on the most
load-bearing feature, the F-009 error one level out. **Completeness wins.**

1. No target is left unfolded for recipe-hygiene reasons. Cost and hardware are the only limits.
2. **Every fold records its recipe at fold time** (D-047), resolved from `TIER_RECIPE`, never
   hand-passed. ⚠ **A fold that completes without a recorded recipe is a defect, not a gap** — the one
   such fold among the 82 becomes structurally impossible. Proven by revert.
3. Every census statistic reaching a surface, a deck, or the paper **states its recipe composition**
   beside the number, not in a methods appendix.
4. **Census heterogeneity is one-dimensional, and that is an improvement worth stating.** Both tiers
   chunk at 64 since D-042, so the census varies in **dtype only**. Tranche zero varies in dtype *and*
   chunking, which F-012 measured as output-affecting. **The census is cleaner than the cohort it
   extends, not messier.**
5. **Recipes are never pooled silently.** Any distributional claim is reported **per recipe as well as
   combined**, or not reported.

#### Decision (3) — a tranche is an **execution order**, never a filter, never a suitability axis

D-077 decision 1's three prohibitions are inherited whole: local-foldability must not become a model
feature, must not sit beside suitability without its label, must not filter the census.

Bands are **named, not inferred**: `local` · `unmeasured_band` (440–630, pending F-013) · `above_local`
· `no_topology` (**a category, never a length, never `0`**) · `unresolvable`. Under decision 2, bands
determine **which tier folds a target**, not **whether** it is folded. The band vocabulary also
carries the ineligibility categories ruled in `RULINGS-2026-08-05-status-wins-over-span.md`, where
**`no_topology` is reserved strictly for rows that were fetched successfully and returned no sliceable
span.**

#### Decision (4) — within a band, fold order is a **seeded random permutation**, frozen before the first fold

The crank turns for days and someone will want a number off the partial result. A partial set taken in
file, accession, or length order is a biased subsample of its own band — worst in length order,
because length is feature 1.

Seed recorded in the census manifest before the first fold. **Frozen reading, both directions:** a
**band-conditional** statistic on a partial tranche *is* reportable, stating band, n, seed, and recipe
composition. A **census-wide** statistic on a partial tranche is **not**, under any framing. ⚠ No
silent re-seed.

#### Decision (5) — accession work is **verification**, not derivation

The reconstructed membraneome already carries an accession on all 7,903 rows (0 blank), counted
2026-08-05. Re-deriving the mapping would produce a second accession source with nothing comparing it
to the first — the two-paths class, **caught in a standing Planner order before it executed.**

**The reconstructed CSV — not a fresh UniProt derivation — is the source of record for identity**, and
the operative census key is its `uniprot_current_accession` column; `UniProt Accession` is retained as
provenance. Buckets: `agrees` · `source_only` · `uniprot_only` · `disagrees` · `unresolvable`.
⚠ **A disagreement is a finding, not a merge conflict resolved by preference**, and a verification
bucket never gates a fetch. Empty buckets are asserted empty. **Owner-reserved:** how `disagrees` and
`multi` resolve.

#### Decision (6) — what a census fold licenses

✅ **Licensed:** *"Of the 2,807 surface-class ECDs, N are folded — M at (int8, 64) on a consumer 8 GB
GPU, K at (fp16, 64) on rented compute — as of [date]."* Dated, band-named, **recipe-composition
named**, derived from live routes.

❌ **Not licensed:** coupling foldability to suitability (D-077 dec 1) · any census filtered by
affordability (D-077 dec 3) · any statement about how many rows are good targets (D-028) · any
extrapolation from the 82's proportions to a census size (`core/census.py`'s standing refusal) · any
**pooled** confidence statistic without its recipe composition · any census-wide confidence claim
before the overlap set reads out (dec 7) · any census-wide statistic from a partial tranche (dec 4).

#### Decision (7) — the precision overlap set: what makes decision 2 recoverable rather than merely disclosed

Under decision 2 the census spans two dtypes. But **precision is assigned by tier, tier by length, and
length is feature 1** — so dtype and length are **perfectly confounded with no overlap**, the exact
structure F-008 recorded for the 82.

**Disclosure does not close it.** Stating the hardware and method makes the heterogeneity **visible**;
it does not make it **separable**. If census mean pLDDT differs between the int8 rows and the fp16
rows, no honest reporting tells a reader whether long ECDs genuinely fold with less confidence or
whether int8 quantization depresses pLDDT. ⚠ **A replicator following our stated method reproduces the
same confound** — replication then confirms reproducibility, not validity.

**The instrument that closes it, and it is cheap:** fold a pre-registered random sample of short
targets at **both** precisions, drawn beneath a *measured* fp16 local ceiling, sample size and seed
recorded before the first overlap fold. It buys a **measured** per-residue pLDDT offset — heterogeneity
becomes a nuisance parameter with a magnitude instead of a structural confound with none. If the offset
is negligible, decision 2 is vindicated **by measurement rather than by assumption.**

⚠ **The overlap is not a gate on the crank.** Folding proceeds; the overlap runs alongside. It is
required before any census-wide confidence statistic is reported, not before any fold happens. **Its
design and frozen interpretation land as `D-078`**, whose `RESERVED.md` trigger is amended in this
same commit from *"a raised local ceiling"* to **"the first census fold at a second precision"** —
the census now creates the overlap need directly.

#### Definition of done

- [x] Number confirmed against the live log by header; `RESERVED.md` checker run and read by output.
- [x] Entry merged **before** migration 0008 and before any census row exists.
- [ ] 0007 applied and **verified by column inspection**, not by alembic's exit code.
- [ ] Tranche column shipped; enumerating routes filtered; **proven by revert**.
- [ ] Manifest records seed + source sha256 + span run date **before** the first fold.
- [ ] Recipe recorded at fold time or the fold fails — proven by revert.
- [ ] Scorer-import refusal green and revert-proven.
- [ ] 2,807 + 2,209 + 2,793 + 2 ingested under four tags, nothing dropped, nothing pooled.
- [ ] fp16 local ceiling probed; overlap sample size + seed recorded before the first overlap fold.

---

### F-016 — The `Non_Surface` marker in the reconstructed Table S3 is a section heading, not a partition: everything below it is the **whole** membraneome

- **Date:** 2026-08-04. **Entered this log:** 2026-08-04, **in the same commit as F-011**, per
  `RULINGS-2026-08-04-F016` §6.1 — F-016 discharges F-011's flags and may not precede it.
- **Type:** A **finding** about a file this project was about to read positionally, caught before any
  census was built on it. **Nothing is ruled here.** One data artifact written, one script default
  removed.
- **Number:** **F-016**, the next free integer. F-013/F-014/F-015 stay reserved.
- **Relates:** **F-011** (whose magnitudes this discharges and whose `~5,102` it withdraws),
  **D-077 dec 1.3** (present-flagged-excluded-from-nothing, the treatment reused for inactive rows).
- **Full text:** `docs/F-016-non-surface-marker-is-not-a-partition.md`.

**The marker at row 2888 is a section heading, and the section it heads is the entire table.** All
2,886 surface rows appear **again** below it, field-for-field identical. **Splitting on row position
labels the entire positive class SURFY-negative** — the precise inversion `core/census.py` exists to
prevent. Derive class from the `Surfy` column, **never from row number.**

**Two gaps were live in the census before a single row was loaded:**

| | The gap | The cost had it shipped |
|---|---|---|
| 1 | The classes **do not partition** the table — 2,801 rows carry a blank class cell | "Not positive" overstates the negative class by **126%** (5,017 vs 2,216) |
| 2 | The **identifier count is not the protein count** | 2,886 identifiers are **2,807 distinct accessions**; 79 collapse into four HLA loci UniProt has merged |

⚠ **Three classes, always named:** `surface` · `non_surface` · `unclassified`. `unclassified` is
never merged into either and never dropped — and is **not evidence for F-011.**

**UniProt cross-check, 2026-08-04:** 7,746 active · 105 merged · 52 inactive · **0 unaccounted.** No
accession is corrupt; the divergence is eight years of upstream drift, which is itself the evidence
the reconstruction is faithful to a 2018 snapshot. Merged rows keep their pre-merge identifier;
inactive rows are `foldable=no`, retained and flagged, **never dropped.**

⟡ **`class_conflict` — the mechanism, not just the flag.** `Q96PC5` and `P01764` each carry rows in
two classes. **The classifier did not contradict itself:** each pair carries **distinct pre-merge
accessions** (`O15320`/`Q96PC5`, `P01765`/`P01764`) and exactly one row per pair is `merged`. SURFY
classified two separate entries; **UniProt's merge manufactured the contradiction** — the same
mechanism as the HLA collapse, surfacing as a contradiction instead of a count. **Resolved by
neither**, because resolving would assert that a merged entity has one localization, a biological
claim nobody has made. Both conflicts are `non_surface` × `unclassified`, so **the 2,807 surface
denominator is unaffected.**

⚠ **Not named `table_S3_surfaceome.xlsx`.** That name belongs to an artifact nobody has obtained —
the published URL still serves a 132-byte LFS pointer stub. Consequently `census_spans.py --source`
**has no default and is required**, and the script records the source file's sha256 in its output.

---

### F-011 — The surfaceome classifier's negative class is not "cannot be a target": localization is condition-dependent, and the excluded class may be the one with the best therapeutic window

- **Date:** 2026-08-04. **Entered this log:** 2026-08-04, **late** — see the landing note below.
- **Type:** A **finding** about a boundary this project was about to inherit, caught before
  inheriting it. **Nothing is ruled. No code, no route, no result.**
- **Number:** **F-011**, reserved for exactly this in `RESERVED.md`. F-012 is the Task 1c verdict;
  F-013/F-014/F-015 stay reserved.
- **Relates:** **F-009** (the same shape, a filter that removes the interesting cases), **F-016**
  (which read the table this entry could only cite, and supersedes two of its numbers), **A-014**
  (*an upstream model's negative class is a prediction, not a fact* — still blocked on KEEL-4).
- **Full text:** `docs/F-011-surfaceome-negative-class-v2.md`, which stays. Both existing is the
  **D-075 precedent**, not a duplication defect.

#### ⚠ Landing note — this entry is the D-062 defect in the Planner's own output

**F-011 v2 was written, placed in `docs/`, and pushed — and was never in this log.** "In `docs/` and
pushed" felt like landed and was not. That is **precisely D-062**: a citation treated as settled
authority with nothing in the text suggesting the entry was missing — committed one day after the
orders telling Code to **grep for the header, not trust the filename.**

**It surfaced only because F-016 ran that grep before merging on top of it.** F-016 discharges
F-011's flags, and an entry cannot discharge flags in an entry that does not exist. Recorded here
rather than quietly fixed, because the failure is the interesting part: the rule was written, the
rule was correct, and its author did not apply it to their own artifact.

#### ⚠ Supersession — `RULINGS-2026-08-04-F016` §6.4

- **2,216** moves from *unverified* to **counted** — off the file, matching the SURFY site exactly.
- **~5,102** is **WITHDRAWN, not corrected.** Never a row count; no corrected version exists. It
  assumed the classes partition the table. They do not — the table holds **7,903**, of which
  **2,801** carry a blank class cell.
- ⟡ **The argument is unchanged; its scope narrows.** This finding is about how SURFY defines its
  **negative** class. That holds **for the 2,216.** It says nothing about the 2,801 unclassified,
  which are unexamined by a different mechanism. **They must not be recruited into it.**

#### Provenance of every number — each with its key

⚠ A `verified` label answers *"where did this come from?"* and says nothing about *"is this the
quantity we need?"* — **a verified number with no key is incomplete by construction.** That is how
2,886 went wrong below: correct, verified, and not the denominator.

| Number | Key | Status | How known |
|---|---|---|---|
| **2,886** positive class | identifiers (entry names) | ✅ VERIFIED — ⚠ **not the denominator** | `surfaceome_ids.txt`: 2,886 lines, 2,886 unique. Counted, not cited. |
| **2,807** positive class | **distinct accessions** | ✅ **COUNTED — the denominator** | F-016. 79 collapse into four HLA loci UniProt has merged. Every join here is keyed by accession. |
| **2,216** negative class | identifiers | ✅ **COUNTED** *(was: not verified)* | F-016, off the `Surfy` column; matches the SURFY site. |
| **2,801** unclassified | identifiers | ✅ **COUNTED** | F-016. Blank `Surfy` cell. **Not this finding's subject.** |
| ~~**~5,102**~~ | — | ❌ **WITHDRAWN** | Planner arithmetic resting on an unstated partition assumption. |
| **93.5%** accuracy | — (a rate) | ⚠ Cited, not opened at first hand | PNAS abstract. |

#### The finding

The census universe was about to be defined as SURFY's positive class, with the negative class
treated as ineligible. That rests on a proposition nobody had stated: **"a protein SURFY calls
non-surface cannot be an ADC target."** **Mechanistically sound, empirically leaky — and every leak
runs toward the targets ADCs most want.**

**Sound:** an IgG cannot reach an epitope inside the ER lumen. A protein genuinely confined to an
intracellular membrane is unreachable. Not disputed.

- **Leak 1 — classifier error.** Reported accuracy 93.5%. Across a negative class of order two
  thousand, implied misclassifications are in the hundreds.
- **Leak 2 — steady-state localization is not "never at the surface."** The non-surface training set
  spans ER, endosome, Golgi, lysosome, mitochondrion, nucleus, peroxisome, cytosol (PNAS Fig. 1B).
  **Endosomal and lysosomal membrane proteins traverse the plasma membrane as part of their
  transport cycle** — their mechanism, not an exception to it.
- **Leak 3 — the labels encode normal conditions.** Trained on CSPA mass-spectrometry data from
  cultured cells. **A protein reaching the surface only under disease conditions is labelled
  non-surface by construction.**

#### ⚠ Why this is more than a caveat

**Condition-dependent surface trafficking is not a defect in a target — it is the selectivity
property an ADC exists to exploit.** Intracellular in normal tissue, surface-exposed in tumour, is a
*better* window than surface-everywhere. **So the classifier that makes the census tractable may
exclude, by construction, the class with the strongest theoretical window.**

#### The same shape a third time, and that is itself the finding

| Instance | The filter | What it excluded |
|---|---|---|
| **F-009** | Kathad's expression-and-selectivity filter | Trop-2, CD33, CD30, CEACAM5 — clinically validated ADC targets |
| **F-011** | SURFY's localization classifier | Potentially the condition-dependent-trafficking class |
| *(pattern)* | — | **The filter that makes a list tractable removes the interesting cases.** |

F-009's resolution applies unchanged: **name the boundary, do not inherit it silently, do not claim
to fill it.**

#### ⚠ Citation status, recorded not silent

Leaks 1–3 come from the SURFY resource page and the PNAS abstract and figure legends, read
2026-08-04. The examples offered in conversation — **GRP78/HSPA5, calreticulin, nucleolin, LAMP1** —
are **Planner-supplied from general knowledge, NOT opened at first hand.** Leads, not evidence.
**None may reach a surface, a deck, or a paper until its primary source is opened.** The finding
stands without them.

⟡ **The entry names its own weakest point:** it argues that an upstream model's negative class
should not be inherited as fact, while resting its magnitudes on that model's paper rather than its
data. Not fatal, not hidden — **and now discharged by F-016.**

#### What this rules — nothing. What it changes — the ingest.

- ✅ **Ingest the full membraneome table, not the positive subset.** SURFY score and class travel as
  columns. ⟡ **Done — `data/census/membraneome-reconstructed-2026-08-04.csv` (F-016).**
- ✅ **The negative class is a labelled annex** — retained, flagged.
- ❌ **Annex members are NOT census members and are NOT ranked.**
- ❌ **No claim that this project's method recovers them.** F-009's over-claim guard, verbatim.
- **Deep-learning justification.** Every discipline this log applies to ESMFold's pLDDT applies to
  SURFY's score. **An upstream model's negative class is a prediction, not a fact.**

---

### F-012 — ESMFold's chunked trunk is **not** output-invariant: chunk 16 diverges from chunk 64, and the folded cohort spans three different recipes

- **Date of run:** 2026-08-04. **Entered this log:** 2026-08-04, same day, before any use.
- **Type:** A **finding** — the result of D-077 Task 1c. It **cites D-077 and amends nothing.**
- **Number:** **F-012**, reserved for exactly this in `RESERVED.md` (amendment §1). F-011 belongs to
  the surfaceome negative class; F-013 stays reserved for Task 3 Arm A.
- **Relates:** **D-077 decision 2** (the two-row frozen table this reads against), **D-042** (which
  changed rental `chunk_size` `None`→`64` after O(L³) falsified the no-chunk assumption — the source
  of the cohort split below), **F-008** (the two-precision confound this adds a *third* axis to),
  **D-045/D-071** (fold provenance, without which the cohort split would be unknowable), **D-041 dec 4**
  (no threshold invented after the fact), **D-047** (recipe resolved at fold time).

#### The verdict, read against the frozen table and only against it

**⚠ Row 2 fired: the outputs DIFFER.** D-077 decision 2 fixed both readings before this ran, and its
second row says *"outputs differ **at all, by any margin**"* is the differ branch — **"nearly
identical" is the differ branch.** No tolerance was invented after seeing the numbers (D-041 dec 4).

| Comparison | Coordinates | pLDDT |
|---|---|---|
| **chunk 64 vs 32** | **0 / 342 differ** | **0 / 114 differ** |
| **chunk 64 vs 16** | **45 / 342 differ**, max abs delta **1.0e-3 Å** | **111 / 114 differ**, max abs delta **2.08e-3** |
| **chunk 32 vs 16** | 45 / 342 differ, max abs delta 1.0e-3 Å | 111 / 114 differ, max abs delta 2.08e-3 |

**First divergence (the evidence dec 2 calls for):** residue 0, field `plddt`,
`19.8300302028656` vs `19.829827547073364`.

**Therefore, per the pre-registered reading:** `chunk_size` is a **recipe dimension**, not a
memory/time knob. **The local ceiling is defined ONLY at chunk 64.** Folds produced at different
chunk sizes are **not commensurable**. **Task 3 Arm B — the extended envelope at chunk 32/16 — is
ABANDONED, NOT DEFERRED.**

#### How known (D-016), including the control that makes it interpretable

- **Run:** `scripts/chunk_invariance_run.py`, local NVIDIA RTX PRO 2000 Blackwell Laptop GPU (8151 MiB
  total, 7043 MiB free), torch 2.11.0+cu128, `dtype=int8` resolved from `TIER_RECIPE["local"]`.
  Artifacts: `data/derived/chunk_invariance/` (three PDBs, three pLDDT arrays, `verdict.json`).
- **Sequence:** the existing GPU-test fixture source (`tests/test_runner.py:209`), **114 aa**.
  Decision 2 permitted "the existing test fixture's source, **or** Trop-2 at ~248 aa"; the first was
  used because **Trop-2 has no sequence in this repo** — F-009 records TACSTD2/P09758 as one of the
  four clinically-validated ADC targets *excluded* from the 82, so it has no `protein_analyses` row,
  and `data/heldout_positives.csv` carries its accession and trial data only. The ~93 Trop-2 folds in
  `ARCHITECTURE.md:598-599` were dev-era.
- **⚠ THE DETERMINISM CONTROL, run before the verdict was believed.** Two folds at the **same** recipe
  were compared at chunk 64 and again at chunk 16: **byte-identical both times.** Without this, *"chunk
  16 differs"* is indistinguishable from *"folds are nondeterministic"* and the whole comparison is
  uninterpretable. The divergence is a real effect of `chunk_size`.
- **Comparator:** `worker/fold_compare.py`, exact equality, no tolerance, proven to bite against a
  deliberately contaminated rounding implementation before it was trusted.

#### ⚠ The consequence nobody had looked for: the folded cohort is already split across recipes

**How known (D-016):** read-only query over `protein_analyses.metadata->'fold_provenance'`, all 80 rows,
2026-08-04.

| `(dtype, chunk_size)` | Targets |
|---|---|
| `('int8', 64)` | **42** |
| `('fp16', None)` | **34** |
| `('fp16', 64)` | **3** |
| no `fold_provenance` recorded | **1** |

**34 folds ran unchunked.** That is D-042's own history — rental `chunk_size` was `None` until the
first rental run falsified the assumption that more VRAM makes chunking unnecessary — and D-045's
provenance capture is the only reason it is visible at all. **Until today this was harmless, because
chunking was assumed output-invariant. That assumption is what D-077 decision 2 said was never
measured, and it is now measured false for 16-vs-64.**

**⚠ WHAT THIS DOES AND DOES NOT ESTABLISH — the line matters.** This run compared **64 / 32 / 16 at
int8 on one 114-aa sequence**. It did **NOT** measure `None` versus `64`, did not measure at `fp16`,
and did not measure on a cohort-length sequence. So:

- **Established:** `chunk_size` can change ESMFold's output; the cohort contains three recipes.
- **NOT established:** that the 34 unchunked folds differ from the 37 chunked ones, or by how much.
  **`None` vs `64` is unmeasured**, and it is the comparison that would matter.
- **Refused:** any claim that the cohort's features are compromised, and equally any claim that they
  are fine. Both would be beliefs. The measurement that would settle it is **reserved as F-015**.

**This is F-008's shape one axis over.** F-008 recorded precision confounded with length and tier;
this adds `chunk_size`, and unlike F-008's it is confounded with *when the fold ran* rather than with
length. D-075 decision 6 already declined to resolve F-008 and is not weakened by this — but a
survival result there must not be over-read as excluding this either.

#### ⚠ The sub-structure, reported as evidence and explicitly NOT acted on

**chunk 64 and chunk 32 were perfectly identical; only chunk 16 diverged.** That is real information
and belongs in the record. **It is not a licence to probe Arm B at chunk 32.** Decision 2 says the
extended-envelope branch is *abandoned, not deferred*, on the differ branch — and "64 and 32 agreed on
one 114-aa sequence, so 32 is safe" is exactly the post-hoc carve-out the pre-registration exists to
forbid. n=1 sequence, at one length, on one card. **If chunk 32 is ever wanted, it is a new dated
entry with its own measurement, not an exception read out of this one.**

#### Honest limits of this finding

- **n = 1 sequence, 114 aa, one card, one torch build.** Generality is unmeasured.
- **Coordinates were compared through the PDB text format**, which quantises to 3 decimal places — so
  the observed 1.0e-3 Å max delta is *one unit in the last written place*. The true underlying
  difference may be smaller or larger; what is certain is that it is visible at file precision.
- **The magnitude is tiny and the direction of the ruling does not depend on that.** A reader who
  wants to call 2e-3 pLDDT "noise" is asking for a tolerance, and the answer is the one written before
  the numbers existed.

- **Deep-learning justification.** This is a statement about the model's numerics: chunking tiles the
  trunk's triangular attention, and the tiling changes the floating-point reduction order, so the
  network's own output is not invariant to a setting chosen purely for memory. That is load-bearing
  for whether folds produced under different memory budgets may share a ranking at all — the question
  the whole local-envelope idea rested on — and it is answered against the convenient direction.

- **Consequences.**
  - **Task 3 Arm B is abandoned.** Arm A (chunk 64, the production recipe) is unaffected and still
    ungated.
  - `LOCAL_CEILING` is **unchanged at 440** and now provably *recipe-scoped* — D-077 dec 3's binding
    of the constant to `(hardware, dtype, chunk_size)` is vindicated by its own Task 1.
  - **No reported result changes.** F-004, F-005, the LOO distribution and the ranking are untouched;
    nothing here reaches the scorer.
  - **F-015 reserved** for the `None`-vs-`64` measurement at fp16, which is the open question this
    opened and cannot itself answer.

### D-077 — The local fold envelope: measure it, bind it to its recipe, and slice the census by it — as a **cost and reproducibility** axis, never as a suitability axis

- **Date:** 2026-08-04
- **Status:** Accepted. **Ruled before any probe.** This entry is the pre-registration; **it is void if
  code precedes it** (D-075 precedent).
- **Type:** A **decision**. It rules a measurement design, freezes two interpretations, and — the
  load-bearing half — **rules what the resulting axis may and may not be used for.** Its results land
  later as their own F-entries (unassigned until they exist; highest `### F-` at merge is **F-010**).
- **⚠ Number verified, not inherited.** At merge the highest `### D-` entry was **D-076**, landed in the
  immediately preceding commit precisely so this entry's decision-7 citation of "D-076 Tier 1" resolves
  to a real entry. **Checked by reading the log, not a reference to it** (method note item 7).
- **Relates:** **D-024** (which left the local ceiling inside (440, 630) *deliberately open and cheap* —
  this closes that item); **S-004/S-005** (the original bisection and its anchors); **D-022** (the A6000
  ceiling probe, whose instrument this reuses); **D-047** (recipe resolved at fold-time, not frozen at
  enqueue); **D-042** (rental chunking, after O(L³) falsified the no-chunk assumption); **F-008** (the
  two-precision confound this creates the overlap to test); **D-075 decision 6** (which names F-008 as
  unresolved and not a prerequisite); **D-027** (the fixed six features — this entry adds none);
  **D-050** (derive, don't hardcode); **D-076** (Tier 1 IGF2R, unchanged by this entry).
- **Provenance (D-016):** owner observation, 2026-08-04 — *"we can slice the census by one more
  dimension: ability to fold on the laptop. All that costs is power."* Orders:
  `docs/ORDERS-Code-2026-08-04-D-077.md`; pre-work: `docs/PREWORK-2026-08-04.md`.

#### Context — what is actually unmeasured, and what it is costing

**How known (D-016):** each row below was read from the named source in the working clone at `7f391a7`
and **re-verified by the builder against the file, not against the planning document that cited it.**

| Fact | Source |
|---|---|
| `CEILING_KNOWN_GOOD = 440`, `CEILING_KNOWN_BAD = 630`, band **UNMEASURED** | `core/manifest.py:51-54` |
| 13 cohort targets route to rental with `tier_reason=unmeasured_local_ceiling` | `core/manifest.py:16-17,129-130` |
| Local recipe **int8 / chunk 64**; rental recipe **fp16 / chunk 64** — the tiers differ **only in dtype** | `core/contracts.py:31-34` `TIER_RECIPE` |
| 440 aa folded clean at chunk 64: 28.6 s, peak **6665 MiB**, **378 MiB** headroom against 7043 MiB free | `ARCHITECTURE.md:607-609,616` |
| 630 aa is **4-for-4 fatal** | `ARCHITECTURE.md:598-599` |
| *"HER2 might yet fold at chunk 16/32 … this is **untested**"* | `ARCHITECTURE.md:616-618` |

**Derived from `data/cohort_82_ecd.csv` (2026-07-21 snapshot), 13 targets with `largest_span_aa`
strictly inside (440, 630):**

`ENTPD1 441 · SCNN1A 456 · ADAM17 457 · MERTK 485 · CSF1R 498 · PDGFRB 500 · LRFN4 502 ·
LRFN3 523 · EPHA4 528 · GRIN1 541 · CDH11 564 · LRRN1 606 · EGFR 621`

**ENTPD1 was routed to paid compute for being one residue over a bound nobody has measured.**

> ⚠ **That CSV is a 2026-07-21 snapshot and 13 of its 82 rows carry an empty `largest_span_aa`
> (`bucket_by_largest='unknown'`, IGF2R among them).** The two 13s are **different rows** and neither
> count licenses the other. **No census claim in this entry may be derived from this CSV.** Every count
> that reaches a surface, a deck, or the paper **re-derives from `/api/coverage` and `/api/analyses`**
> (D-050 stale-literal discipline). The list above is *orientation for the probe's bounds*, not a
> reportable statistic.

#### Decision (1) — ⚠ **What this axis IS, and what it is NOT.** The load-bearing ruling.

**Local-foldability is a monotone step function of ECD length.** ECD length is **feature 1** of the
pre-registered six (D-027). Tier was assigned *by* length. Precision was assigned *by* tier. Therefore
**length, tier, precision, and local-foldability are, on the current cohort, four names for one
partition with no overlap** — precisely the confound F-008 recorded and D-075 decision 6 declines to
resolve.

**Rulings, binding on every downstream artifact:**

1. **Local-foldability MUST NOT become a model feature.** No seventh (or eighth) feature. The
   `--ablate` named-set refusal (D-075 decision 5) stands unamended; adding a foldability feature
   requires a new dated entry and would re-import F-008 under a new name.
2. **It MUST NOT be presented as a census axis alongside suitability without its label.** It is a
   **cost / tractability / reproducibility** axis. It says what a target costs to *compute*, and
   **nothing whatsoever** about whether it is a good ADC target. Any surface placing the two side by
   side must state that in the same visual frame (D-069, every surface self-sufficient).
3. **It MUST NOT be used to filter the census.** A comprehensive census (roadmap 3.1) that silently
   drops the targets it cannot afford to fold is a census of *our budget*, not of the surfaceome — and
   it would bias the census by length, i.e. by feature 1. Unaffordable targets stay in the census,
   flagged, unfolded. **This is the F-009 error one level out and it is refused here in advance.**
4. **The one thing it legitimately is:** a *pre-fold, sequence-only* predicate. It can be computed for
   an arbitrary census **without folding anything**, which makes it the only cost instrument available
   before the money is spent.

**Why this ruling is written before the measurement:** the measurement is cheap and the temptation
after it will be to promote a satisfying new number to an axis. **Naming what it is now removes that
option later.**

#### Decision (2) — the chunk-invariance question runs FIRST, because it decides whether "the ceiling" is a number or a curve

`ARCHITECTURE.md:616-618` records, **as inference not measurement**, that HER2 at 630 aa might fold at
chunk 16/32 — **untested.** If true, the local envelope is not a single length; it is a
length-per-chunk_size curve, and the "free" envelope is much larger than 440.

But a fold produced at a different `chunk_size` is only usable if **chunk_size does not change the
output.** Chunking is a tiling of the trunk's triangular attention; it *should* be output-invariant.
**Should is not measured.**

**The test, frozen before it runs.** On the local box, at `dtype=int8`, fold one fixed sequence
(the existing test fixture's source, or Trop-2 at ~248 aa — short enough that every chunk_size fits) at
**chunk_size 64, 32, and 16**. Compare the three outputs.

| Outcome | Reading — **fixed now** |
|---|---|
| All three produce **byte-identical CA coordinates and pLDDT** | `chunk_size` is a **memory/time knob only**. The ceiling is a curve, folds across chunk sizes are commensurable, and probing at chunk 16/32 is legitimate. |
| Outputs differ **at all**, by any margin | `chunk_size` is a **recipe dimension**. The ceiling is then defined **only at chunk 64**, folds across chunk sizes are **not** commensurable, and the extended-envelope branch (decision 4) is **abandoned, not deferred**. The difference is reported as a finding in its own right — *ESMFold's chunked trunk is not output-invariant* is a publishable methods note nobody reports. |

**No third reading. No tolerance threshold invented after seeing the diff** (D-041 decision 4).
**"Nearly identical" is the *differ* branch.** If a tolerance is ever wanted, it is a new dated entry.

#### Decision (3) — the ceiling is measured at the production recipe, and the constant is BOUND to it

**The failure this prevents:** `worker/ceiling_probe.py` takes `--dtype` and `--chunk-size` as free CLI
arguments and **defaults `--dtype` to `fp16`** (written for the A6000, D-022 — verified at
`worker/ceiling_probe.py:140`; `--chunk-size` defaults to `None`, looser still). A local run that
forgets `--dtype int8` measures a ceiling for a recipe **the local tier does not use**, and that number
would then be written into `CEILING_KNOWN_GOOD`, which routes production folds at int8. That is the
project's recurring shape: **two paths to one quantity, never compared** — the routing constant and the
recipe that measured it, free to drift.

**Ruled:**

- The bisection runs at **`dtype=int8, chunk_size=64`** — resolved from `TIER_RECIPE["local"]`, **not**
  passed by hand (D-047's principle, applied to the probe).
- **The measured ceiling is recorded as a triple `(hardware, dtype, chunk_size) → length`, never as a
  bare integer.** `CEILING_KNOWN_GOOD` acquires a named recipe alongside it, and a test asserts the
  constant and the recipe cannot be updated independently.
- A ceiling measured under any other recipe **may not** update the routing constant.

#### Decision (4) — the repeat rule, frozen before the probe, and the outcome the current instrument cannot express

**⚠ The existing probe assumes a sharp, monotone boundary, and cannot report that it isn't one.**
Verified by reading `worker/ceiling_probe.py`: `bounds_from_history` raises the floor on **any single**
`ok` (`good = max(good, length)`, line 73) and lowers the ceiling on **any single** failure (line 75);
`next_probe_length` **raises `ValueError` when `bad <= good`** (lines 53-54, asserted as correct by
`tests/test_ceiling_probe.py::test_requires_good_below_bad`); `ceiling_from_history` reports `max(ok)`
and **ignores `bad` entirely** (lines 79-85). So a sequence like *ok@560 then oom@500* — entirely
plausible **378 MiB** from the wall — makes the probe **crash rather than report the flakiness.** The
instrument has no vocabulary for *"the boundary is a band."*

This is **not** logged as a defect in the probe. It is a design assumption that was correct for the
A6000 (far from its wall) and is **not obviously correct for a card with 378 MiB of headroom.**
Recorded here so a `ValueError` during the run is read as **a result**, not a bug.

**The repeat rule, frozen:**

- A length is **known-good** only if it folds clean **4 times consecutively.** A length is **known-bad**
  only if it fails **4 times.** *k = 4 is inherited from the existing record — 630 aa was ruled fatal on
  4-for-4 (`ARCHITECTURE.md:598-599`) — not invented here.*
- Anything else at a given length is **`unstable`**, a **pre-registered, legitimate, reportable
  outcome**: the ceiling is then a **band**, reported as `(highest 4-for-4 good, lowest 4-for-4 bad)`,
  and **routing uses the conservative end.**
- **A single lucky fold never raises the routing constant.** This is the whole point of k.
- **Stopping rule frozen:** the bisection stops when `bad - good <= step`, `step = 8`. No "one more try"
  after a satisfying success. Re-running with the same JSONL history must be deterministic.

#### Decision (5) — the probe must not be able to touch the reported cohort

**Structurally true today, and asserted anyway (D-074).** `worker/ceiling_probe.py` writes only to an
append-only JSONL file and holds no database session — verified: its imports are `argparse`, `json`,
`sys`, `pathlib`, `typing` only. Probe folds cannot enter `protein_analyses`. **But this is a property
of the current call path, not a guarantee** — the same distinction D-075 decision 5 drew about
`persist_results()`.

**Ruled:** probe artifacts live under `data/derived/`, never in the analysis tables. A test asserts the
probe module imports no database session and no persistence helper, **proven by revert** (add the
import, watch it redden). **If a probe fold ever lands in `protein_analyses`, `/api/coverage`'s folded
count moves and F-004's denominator 56 moves with it** — from a measurement that exists only to decide
where to run things. That is **D-075's Corruption 2 in a new costume**, guarded before it can happen
rather than after.

#### Decision (6) — the census cost model, and what it may claim

A pure function over ECD span → `{local | rental | over-ceiling}` at the measured recipe, plus a script
that reports the split for an arbitrary list of spans. **No GPU, no network, fully unit tested.** This
is Phase 2's actual instrument: it answers *"what does a census of N targets cost?"* before a dollar is
spent.

**Two claims it licenses, and one it does not:**

- ✅ **Cost:** *"Of these N targets, M fold at zero marginal cost on an 8 GB consumer card; N−M need
  rented compute."* Derived, dated, recipe-named.
- ✅ **Reproducibility (paper-relevant):** *"M of the folds underlying this result are reproducible by
  any reader with a consumer 8 GB GPU and no cloud spend."* A real strength of the single-sequence /
  no-MSA design, costing nothing to state — **provided M is derived from the live endpoints and carries
  its recipe.**
- ❌ **Not licensed:** any statement coupling foldability to suitability, or any census filtered by it
  (decision 1).

#### Decision (7) — what this entry does NOT do

- **It does not run the F-008 precision A/B.** If the measured ceiling exceeds 440, some targets become
  foldable **locally at int8** that were folded **on rental at fp16** — creating, for the first time,
  **overlap in a partition F-008 recorded as having none.** That is F-008's own named resolution path
  and it becomes nearly free. **It is a separate, separately-pre-registered entry (D-078), written
  before any such fold runs, because its outcome can move F-004.** Naming it here is not authorising it.
- **It does not fold IGF2R, FAT2, or MUC16.** IGF2R remains **D-076** Tier 1 (rental); FAT2/MUC16 stay
  on ice behind their trigger.
- **It does not change the six features, the scorer, the pre-registered run, or any reported result.**
  Nothing in this entry has a path to F-004.

- **Deep-learning justification.** The ceiling is a property of **quantized ESMFold inference** — how
  the trunk's O(L³) triangular attention scales against 8 GB under int8 with chunked attention.
  Measuring it measures the neural core's operating envelope, and it determines what fraction of any
  future census the network can process without external compute. Decision 2 is the sharper DL
  question: **is ESMFold's chunked trunk output-invariant?** That is a statement about the model's
  numerics, it is cheap to test, and its answer is load-bearing for whether folds produced under
  different memory settings may share a ranking at all.

- **Consequences / test surface.** Chunk-invariance fixture reds on a deliberately perturbed comparison
  and greens on identical output · the probe resolves its recipe from `TIER_RECIPE["local"]` and a
  hand-passed dtype that contradicts the tier is refused · `CEILING_KNOWN_GOOD` cannot change without
  its recipe changing (test proven by revert) · a single `ok` does not raise the routing constant (k=4
  asserted) · `unstable` is representable and does not raise · the probe module imports no DB session
  (proven by revert) · the census cost function is pure and derives its ceiling from the named constant,
  never from a literal (D-050) · **`CEILING_KNOWN_GOOD` stays 440 in the implementing PR** — the
  instrument and the number move in separate PRs so it is always legible which change moved routing.

### D-076 — The last three unfolded targets: a scoped plan, one tier executed, two on ice behind a named trigger

- **Date of decision:** 2026-08-03 (drafted 2026-08-01). **Entered this log:** 2026-08-04.
- **Status:** Accepted. **Ruled before any re-fold** — no target named here has been folded under it.
- **Type:** A **decision** (scope + sequencing), carrying **one finding** inside it (the MUC16 disorder
  read). Nothing about F-004 changes; see §4 below.
- **⚠ Why the entry date lags, recorded not silent.** This decision lived as a staged document
  (`docs/D-076-last-three-fold-plan.md`) from 2026-08-01 and was **cited as settled authority before it
  entered the log** — by `PREWORK-run-session.md` §5.4, `PREWORK-next.md`, the 2026-08-01 MANIFEST, and
  then by the D-077 order and pre-registration (2026-08-04). That is the **D-062 defect shape**: a
  citation pointing at an authority the log did not contain. It is closed here, and it was closed
  *because merging D-077 while D-076 was absent would have placed the dangling citation inside the log
  itself* — D-077 decision 7 names "D-076 Tier 1". **Like F-009 and unlike D-062 this is not a
  reconstruction:** the staged document survives with its own reasoning, so this entry is **sourced**,
  not recovered from effects.
- **⚠ Numbering history, recorded because it is a near-miss.** Drafted **D-072**; that number was
  already taken by the miniature demo notebook (`d46aa1a`). Renumbered **D-076** on 2026-08-03 against
  the live log (highest decision entry was D-075) — **verified by reading the log, not inherited from
  an estimate** (`e9e7955`). The historical wording in `HOUSEKEEPING-2026-08-01-untracked-deletions.md`
  deliberately still names the old filename, since it documents the state at the time (D-073 precedent).
- **Relates:** **D-047** (recipe resolved at fold-time), **D-050** (derive, don't hardcode — the
  coverage numbers this moves), **F-007** (the manifest is not a reliable proxy for what ran — binding
  on any fold produced elsewhere), **D-016** (a fold from another lab names how it is known like any
  other), **F-004** (the result this entry is firewalled from), **D-022** (the named oversize
  exclusions MUC16/FAT2 originate here), **F-010** (IGF2R is the row whose `analysis_id` reports null),
  **D-077** (the local-envelope work that cites this entry's Tier 1 as unchanged).
- **Provenance (D-016):** owner/planner scoping pass 2026-08-01, written up as the staged document
  named above; lengths and unfolded status read from the cohort snapshot and `/api/coverage`.

#### Context — why the single "unfoldable" bucket was wrong

At delivery the cohort stands at **79 of 82 folded**. The three unfolded targets were carried as one
bucket ("unfoldable, surfaced as a finding, not a silent exclusion"). **That bucket is wrong: the three
are three different problems**, and collapsing them hid that one is trivially closable and the other
two are resource-access problems, not method walls. When the work is presented, *"why aren't all 82
folded?"* is the likely first question, and the correct answer is an engineer's answer — *yes it can be
done, here is how, here is the cost* — with feasibility stated cleanly and utility held as a **separate**
judgement.

| Target | Length | Why unfolded | Class |
|---|---|---|---|
| **IGF2R** | large ECD (2,491 aa), ordered | Hit a **transient A6000 rental-tier ceiling** on its run — not a size wall | **Compute limitation.** No asterisk once folded. |
| **FAT2** | 4,030 aa | Exceeds single-sequence capacity on available hardware; but **ordered** (cadherin repeat stack) | **Resource + method-seam.** Foldable with more VRAM or by domain assembly; assembly changes `boundary_method`. |
| **MUC16** | 14,451 aa | Off the end of the field's map; **largely intrinsically disordered** (tandem SEA repeats + glycosylated linkers) | **Biology, not compute.** A structure is producible; a meaningful whole-ECD structure for the six features is not. |

The distinction is load-bearing: it is the difference between *"one more run,"* *"a method with a
labelled seam,"* and *"the wrong question for this molecule."*

#### Decision (1) — Tier 1, IGF2R: **executes on its own schedule**, comparable, no asterisk

- **How.** Re-enqueue on the A6000 rental tier, **recipe resolved at fold time (D-047)**, sequence
  length checked against what ceilinged last run. If it still ceilings, escalate one rung (H100 80 GB,
  same workflow). **No new code, no new `boundary_method`.**
- **Comparability.** Same **ESMFold-v1 / sliced-ECD recipe** as the other 79, so its six features are
  directly comparable. This is the only one of the three where "unfolded" is a plain limitation.
- **Cost.** Hours. One rental block, <1 hr fold time, ~$0.54–2/hr.
- **Consequence on merge, pre-authorised here.** Cohort 79 → 80. **Every coverage/ranking number
  re-derives from the authoritative endpoints** (`/api/coverage`, `/api/ranking`) — no re-hardcoding
  (D-050). If IGF2R clears the pLDDT floor and is a ranked disposition it enters the ranking set; **if
  labelled, it enters the fit set and F-004's denominators move.** That is a **result update, executed
  through the gate, derived not typed** — never a silent edit.
- **⚠ Check the label first.** IGF2R's label status is checked against `data/adc_reference_mapping.csv`
  **before** the fold, so the consequence is known in advance rather than discovered after.

#### Decision (2) — Tiers 2 and 3 are ON ICE behind a named external trigger

**The trigger:** *external validation of the work's novelty* — a paper accepted, a research group
adopting the structural axis, or an equivalent signal that the cohort must become complete for
**reproducibility/coverage** reasons rather than demo optics.

**The utility inversion, recorded so the reasoning survives:**

- **Before validation:** these folds do not change F-004 (§4). MUC16's un-foldability is a *stronger*
  honesty artifact than a filled cell. Executing now spends real effort — and for MUC16 risks **trading
  a finding for an asterisk** — to make a coverage table prettier. Utility low-to-negative.
- **After validation:** a published method must be complete on its stated cohort. *"Couldn't fold 3 of
  82"* stops reading as sophistication and starts reading as an unfinished dataset. FAT2's seam becomes
  a methods-section paragraph (where seams belong); MUC16's disorder becomes a publishable finding.
  Utility flips positive.

**The trigger is external and identifiable. That is what makes "on ice" a plan and not a stall.**

**Tier 2 — FAT2, two routes.** *Route A:* 4,030 aa on an 80 GB card, one sequence — cleanest if it runs
(standard features, no seam), may fail, cheap to attempt. *Route B:* domain-wise fold in overlapping
windows, stitched on shared repeats — always runs, but **introduces a new `boundary_method` value**
(`assembled`/`domain_stitched`) that must travel with the features exactly as feature 4's cross-method
caveat does. Comparable *enough* to render **provided the seam is labelled and tested.** Cost: Route A
one big-pod block; Route B ~1–2 sessions.

**Tier 3 — MUC16, three routes.** *Route 1:* fold ordered SEA domains individually — legitimate domain
models, but a "MUC16" row carrying features from ~120-aa domains **would mislabel what was measured.**
*Route 2:* fold the membrane-proximal window an ADC would engage — biologically defensible but a
*choice of sub-region*, another labelled seam, larger. *Route 3:* run it and report the disorder — let
low-pLDDT regions render as the model reporting "no confident structure here." **Adds no false number.**

##### Finding embedded here (D-016) — MUC16's un-foldability is a structural result, not only a gap

MUC16 being intrinsically disordered means **"predict its ECD structure" is partly the wrong question**
— and that a disordered, heavily-glycosylated antigen is a genuinely different engineering problem for
an antibody. **The pipeline correctly placing MUC16 out of structural reach is itself informative about
its ADC-targeting profile.** Whichever route eventually runs, this framing is preserved: MUC16 is not
merely "too big," it is a case the structural axis flags as unreachable, **consistent with known
biology.**

#### Decision (3) — how a fold produced elsewhere enters

The two hard folds are a **resource-access problem more than a method problem.** A well-provisioned
academic lab with institutional GPU access is the natural executor of FAT2 Route A and MUC16 Route 1/2.
**Recorded as a candidate collaboration path, not a commitment.** If pursued, the same discipline
travels: any fold produced elsewhere **enters through the gate**, its `boundary_method` and environment
captured (**F-007's lesson — the manifest is not a reliable proxy for what ran**), and its features are
comparable only insofar as the seam is labelled. **A fold from another lab is not exempt from D-016.**

#### Decision (4) — the firewall around F-004

- **F-004 stands untouched by Tiers 2–3.** MUC16 and FAT2 are not among the 12 labelled positives; the
  LOO distribution, both nulls, the Spearman, and the "orthogonal but unproven" finding are unaffected
  by whether they fold.
- **Tier 1 may move F-004's denominators** *if* IGF2R is a labelled positive clearing the floor — a
  legitimate, **pre-authorised** result update through the gate.
- **The novelty claim is independent of coverage.** *"No published method ranks ADC targets on predicted
  ECD structure"* is true at 79/82, 80/82, or 82/82. Folding the last three **completes a dataset; it
  does not create or strengthen the contribution.**

#### Decision (5) — the one risk to hold

The temptation, now that a plan exists, is to execute all three **before** the trigger, to look complete
for a demo. **Resist it.** Doing MUC16 prematurely is **the single move in this project that would spend
honesty capital to buy coverage optics.** The plan's value now is that it *exists and is credible* —
scoped, tiered, triggered — **not that it has run.**

- **Deep-learning justification.** The three targets are three different statements about the neural
  core's operating envelope: IGF2R is *infrastructure* (the network folds it; we lacked the card),
  FAT2 is *sequence-length capacity* under O(L³) attention, and MUC16 is a case where the network's
  own low confidence is the informative output — the model reporting absence of confident structure is
  a real prediction, not a failure. Keeping the three distinct keeps ESMFold's limits legible instead
  of collapsing hardware limits and biological disorder into one excuse.

- **Consequences / open items.**
  - [x] Number confirmed against this log (2026-08-03), then **the entry itself landed** (2026-08-04).
  - [ ] IGF2R label status checked against `data/adc_reference_mapping.csv` **before** its fold.
  - [ ] Tier 1 executed: IGF2R re-enqueued, cohort → 80, all coverage/ranking numbers **re-derived from
        endpoints**, F-004 denominators updated through the gate if it is a labelled positive.
  - [ ] Tier 2/3 remain unstarted, trigger unmet — **verified, not assumed.**
  - [ ] Deck slide ("The last three: a plan, not a wall") reflects these tiers and this trigger.

### F-009 — The 82 is Kathad's comparator, not a target census: four clinically-validated ADC targets sit outside it, and that is what motivates the project

- **Date of finding:** 2026-08-01. **Entered this log:** 2026-08-03.
- **Type:** A finding — a property of the cohort plus a checkable list. Nothing is ruled.
- **⚠ Why the entry date lags:** the finding was written as a staged document
  (`docs/F-009-cohort-boundary-false-negatives.md`) and **cited by shipped code before it entered the
  log** — the `/about` and `/scorer` cohort-boundary note (2026-08-03) and `ARCHITECTURE.md` both name
  F-009. That made it the **last open instance of D-062's defect**: a citation pointing at an authority
  the log did not contain. This entry closes it. **Unlike D-062 this is not a reconstruction** — the
  staged document survives with its own reasoning and provenance, so this entry is *sourced*, not
  recovered from effects.
- **Relates:** D-075 (the confound §3's over-claim guard protects), F-004 (the result whose scope this
  bounds), D-029/D-040 (the curated reference the absences were checked against), D-062 (the defect
  class this closes), D-054 (the evidence-baseline deferral).
- **How known (D-016):** cohort membership checked by grep against `data/adc_reference_mapping.csv` and
  `data/cohort_82.txt` — CD30/TNFRSF8, CEACAM5, CD33/SIGLEC3 and TACSTD2 all **absent**. Accessions
  since verified from the **UniProt REST API** (see the closed checklist below).

#### The finding

The research question is *does a structure-derived axis reorder an **expression-based** ranking* — and
the expression-based ranking is **Kathad et al. 2024's**. The 82 is therefore *Kathad's cohort*,
inherited whole so both rankings cover the same targets and the delta means something. Adding a target
outside Kathad's ranking would have nothing to compare against: it would **break** the comparison, not
complete it. So *"why isn't CD30 in the 82"* has a clean answer — **because CD30 is not in Kathad's
cohort.** The boundary is a property of the comparator, not of this project's biology judgement.

**The sharper point, and the actual finding:** four clinically-validated ADC targets were **excluded by
Kathad's expression-and-selectivity filters**.

| Target | Accession | ADC | Furthest status | In the 82? |
|---|---|---|---|---|
| **Trop-2** (TACSTD2) | **P09758** | sacituzumab govitecan · datopotamab deruxtecan | FDA-approved (2 ADCs) | **No** |
| **CD33** (SIGLEC3) | **P20138** | gemtuzumab ozogamicin (Mylotarg) | FDA-approved 2000 | **No** |
| **CD30** (TNFRSF8) | **P28908** | brentuximab vedotin (Adcetris) | FDA-approved 2011 | **No** |
| **CEACAM5** | **P06731** | tusamitamab ravtansine | Phase 3 (CARMEN-LC03, NCT04154956) | **No** |

**Expression-and-selectivity filtering drops clinically-validated targets.** That is a concrete
demonstration that the expression axis is *incomplete*, and therefore that stress-testing it against a
different axis is worth doing at all. **The false negatives motivate the project; they do not undermine
it.**

#### ⚠ The over-claim guard — the load-bearing constraint

**Do NOT claim the structural method "would have caught" these targets.** Three reasons, all recorded
before any such claim could be made: (1) they are **unfolded and unscored** — there is no such result;
(2) CD30's 2011 approval makes it **maximally attention-rich**, so its pLDDT would be inflated for
exactly the reason D-075 interrogates — using it as validation walks into the confound; (3) the
defensible claim indicts the **comparator**, not this project's scorer: *the expression axis has
documented false negatives, therefore expression alone is insufficient, therefore an orthogonal axis is
worth measuring.* **"The comparator has blind spots" stays strictly separate from "our scorer fills
them."** Conflating them hands the critic the next punch. **This is now enforced as a denylist test on
both shipped placements, not as an editorial habit.**

#### An embedded correction (D-016) — the "first ADC" slip

**Adcetris (brentuximab vedotin, 2011) was *Seagen's* first ADC, not the first ADC.** That is
**Mylotarg** (gemtuzumab ozogamicin, CD33, FDA-approved **2000** — eleven years earlier). The two
claims share the word *"first"* and fuse in memory; only *"Seagen's first"* survives the record.
Mylotarg's 2000 approval, **2010 voluntary withdrawal** and 2017 re-approval at lower dose partly
erased it from the popular ADC narrative, which is why *"Adcetris was first"* is a common slip. **No
artifact may call Adcetris the first ADC** — a pharma-literate audience will catch it, and a wrong
historical claim in the setup is disproportionately costly for a project whose credibility rests on
how-known discipline. The staged deck was checked clean; the claim lived only in conversation.

> **⚠ Citation status, recorded not silent.** The sources for the CD33-was-first claim (Nature *Sig
> Transduct Target Ther* 2022; AACR *Clin Cancer Res* 2018; and the CEACAM5 phase-3 set) are
> **Planner-supplied and have not been opened by the builder or owner** — the same convention
> `data/adc_reference_mapping.csv` uses for its unopened citations. The claim is therefore recorded
> **as sourced but unverified-at-first-hand**, and — deliberately — **the shipped UI copy states neither
> the superlative nor the year.** The log carries the claim with its citation status; the user-facing
> surface makes only the part that needed no superlative. If the superlative is ever wanted on a
> surface, open the primary sources first.

#### What has happened since the finding was written (artefact-sourced)

- **§5's open accession checks are CLOSED.** All three were verified against the UniProt REST API on
  2026-08-01: **CD30/TNFRSF8 = P28908 ✓**, **CEACAM5 = P06731 ✓**, **Trop-2/TACSTD2 = P09758 ✓**
  (CD33 = P20138 re-verified). Every guess in the staged doc was correct — and was still checked.
- **§4's future-work item has been BUILT**, as the held-out validation set's Phase A:
  `data/heldout_positives.csv`, **20** clinically-validated ADC targets disjoint from the 82 by
  accession, each with a ClinicalTrials.gov source URL. The four above are members. **Phase B — folding
  and validating them — remains sealed behind D-075 surviving.** §4 said *"explicitly NOT claimed as
  done"*; the curation half now is, the validation half is not.
- **The framing reached the UI**, with the examples derived from that CSV rather than hardcoded and a
  drift test binding the two.

- **Deep-learning justification.** This bounds what the graded result *claims*. The scorer re-orders a
  comparator; without this entry a reader could take the ranking as a statement about the ADC-target
  space, which the data does not support. It also supplies the strongest available motivation for a
  structural axis existing at all — the expression axis demonstrably misses clinically-validated
  targets — while refusing the adjacent, unearned claim that our axis recovers them.

- **Consequences.** F-004/F-005/F-006 unchanged — this bounds scope, not result. The comparator's
  incompleteness is **not** a defect in the cohort choice: inheriting Kathad whole is what makes the
  delta meaningful (D-054's deferral rests on the same logic). ⚠ The 20-row held-out set carries its own
  named limit — **absence from that file is not evidence of absence from the field** — so it must never
  be presented as a complete census either; that would repeat this finding's error one level out.

### D-062 — The Scorer surface and the `GET /api/ranking` route ⚠ **BACK-FILLED 2026-08-03 — reconstructed from artifacts, NOT from contemporaneous record**

> ### ⚠ READ THIS BEFORE THE ENTRY
>
> **This entry did not exist until 2026-08-03.** D-062 was **cited 13 times** — ten in this log, three
> in `ARCHITECTURE.md` — as the authority for a *shipped* surface, and there was no `### D-062`. It was
> the **only** cited decision number with no entry (D-010 excepted; the log documents that one as
> deliberately skipped).
>
> **This is a governance defect on the project's own terms, not housekeeping.** The project rests on
> *the committed log is ground truth — continuity lives in the repository, not in memory.* Thirteen
> pointers to an authority that does not exist means anyone following them to learn **why** the ranking
> route behaves as it does — a later session, a reviewer, the owner in six months — arrives at nothing.
> The decision was *made* (the code shipped, the surface exists); the reasoning was never inscribed.
> That is the log's own **"true as reasoned, not true as recorded"** gap in its worst form: not a number
> that went underived, but an entire decision **referenced into existence without being written**.
>
> **How this entry was built, and the line it does not cross.** Everything below is derived from **two
> artefact classes only**: (1) the 13 surviving citations, which state what D-062 was *claimed* to have
> ruled, and (2) the **code that shipped under its authority**, which demonstrates what was *actually*
> decided. **No part of this entry is written from anyone's recollection of the original deliberation.**
> That deliberation was never logged and is therefore **gone**; reconstructing it from memory would
> inscribe a recollection as though it were a record — precisely the failure this log exists to prevent.
> Where reasoning cannot be recovered from an artefact, **this entry says so rather than supplying it.**
>
> **When the omission happened, verified.** PR **#90** (`0ed5b1f`, 2026-07-27, *"F-004 + D-062: the
> pre-registered result, and the scorer surface that renders it"*) added **`### F-004` and zero
> `### D-062`** to this file. Its own message reads *"Log leads code; the result is the thing D-062
> renders, landed first in its own commit"* — so the F-004 entry went in first and D-062's was meant to
> follow. It never did, while the commit title and the `ARCHITECTURE.md` prose were both written as
> though it had.

- **Date of decision:** 2026-07-27 (from `0ed5b1f`), amended 2026-07-29 (`42a74ad`, jointly with D-055).
- **Date of this entry:** 2026-08-03. **Status:** Accepted-in-effect — the work shipped and has been in
  production since 2026-07-27; this entry records it, it does not authorise it.
- **Relates:** F-004 (the result this surface renders), D-055 (the joint two-column/tooltip amendment),
  D-064 dec 3 (the invalid run that must never be served), D-065 (the `run_kind` filter), D-066 (the
  later reduction of the right column), F-005/F-006 (caveats that travel with the result), D-051 (the
  architecture-contract test this route fires), D-074 (the rule this omission most resembles).

#### What the shipped code demonstrably does (verified 2026-08-03 by reading it)

Stated as behaviour, because behaviour is what survived:

- **`GET /api/ranking` exists** and is declared in `ui/src/system-model.json` (1 occurrence), so the
  D-051 architecture-contract test — set-equality between the live route table and the model — passes
  with it present. It is served by `app/reads.py::ranking_payload`.
- **The route always returns 200 with a `result_status`.** `_result_status()` (`app/reads.py:249`)
  computes **four values**: `complete` (all pre-registered statistics produced) · `partial` (a
  distribution exists but a statistic is blocked — LOO partial, or the full-data fit raised so
  Spearman/ranking is blocked, D-064 dec 5) · `raised` · and **`not_run`**, returned with
  `run: None`, `result: None`, `rows: []` when no valid run exists (`app/reads.py:286`). An absent
  result is therefore a *named state*, never an error and never an empty success.
- **Two independent filters keep the wrong run off the surface** (`_latest_valid_result`): validity
  (`status_detail` must not begin `invalid`, which is how the zero-positive `ranking_results` id=1 is
  excluded — D-064 dec 3) **and** `run_kind = 'preregistered'` (D-065, so a sensitivity ablation is
  never served as the result). Ordering is `computed_at desc`, so id=2 wins on recency as well.
- **`ScorerView.jsx` renders exactly five sections**, verified present: **A** cascade · **B** labels ·
  **C** fixed-before-the-run · **D** the result · **E** the ranking table.
- **The ranking table is real scores at reduced scope** — rank · symbol · score · the excluded set with
  reasons — with baseline / delta / disagreement **named as deferred rather than mocked.**

#### What the citations CLAIM it decided (their words, not a reconstruction)

The fullest surviving account is `ARCHITECTURE.md:68–88`. Reduced to claims:

1. D-062 **landed UI Plan v2 step 6**, the `Scorer` surface, as the **sixth nav** item.
2. Every number on it — *"12, 22, 56, 8, the median, the Spearman"* — is **derived from `/api/ranking`,
   never typed** (Constraint A / D-050).
3. The **mean/median reversal is rendered**, and **caveat (b)** travels with the result.
4. β·x attributions are stored in `target_scores`, so the missing attribution column is *"a display gap
   not a data gap."*
5. It is the **fourth firing** of the D-051 architecture-contract test.
6. The **D-055/D-062 amendment** (2026-07-29) made the surface two-column and moved term-decoding to
   in-situ `Term` tooltips.
7. Elsewhere in this log it is cited as the owner of `result_status` (`:963`), of the validity filter
   (`:1639`), of the `run_kind` filter (`:1437`), of the `structural score` tooltip definition
   (`:1374`), and as *"the rendering surface"* that makes the result legible to a grader (`:1588`).

**Claims 1–7 are all consistent with the code as it stands today.** That is the strongest statement
available: the citations are *corroborated*, not merely repeated.

#### ⚠ What is NOT recoverable, and is therefore not supplied

- **Why the surface has five sections in that order**, rather than another arrangement. The order is
  observable; the argument for it is not in any artefact.
- **Why `result_status` is four-valued rather than three or five.** The four values and their
  boundaries are in the code and their *meanings* are in its docstring — but the reasoning that chose
  that partition is unrecorded. (`partial` is tied to D-064 dec 5, which is the closest thing to a
  recoverable rationale for one of the four.)
- **What alternatives were rejected** — the log's template calls for this and no artefact preserves it.
  For a normal entry the rejected options are often the most valuable part; here they are simply lost.
- **Whether the numbers listed in claim 2 were exhaustive at the time**, or an illustrative subset.
- **The original deliberation itself.** It was never written down. **It is gone.** This entry does not
  guess at it.

- **Deep-learning justification** (required of every entry; supplied here as the *shipped* system's
  justification, not a reconstructed intent). The surface is where the graded neural result becomes
  checkable by a reader: it renders F-004 — the pre-registered evaluation of a model over features
  derived from our own ESMFold folds — with every figure derived from the route rather than typed, and
  with the run-selection filters that stop an invalid or sensitivity run being read as the result. The
  DL core is only defensible if its result is legible and its provenance inspectable; this is the
  surface that makes it so.

- **Consequences / what this entry changes and does not change.**
  - **No code, no test, no route change.** The system is untouched; only the record is repaired.
  - **The 13 citations now resolve.** That was the defect and it is closed.
  - ⚠ **The entry is permanently marked back-filled.** A future reader must be able to tell a
    contemporaneous decision from a reconstruction, or the repair becomes a forgery of history. **This
    marking must never be removed**, and any later entry citing D-062 should be read knowing its
    reasoning is recovered from effects, not recorded at the time.
  - **Adjacent to D-074, and distinct.** D-074: an *instrument* diverges from its written record.
    D-062's defect: a *decision* was cited as an authority that had no record at all. Both are failures
    of the log-is-ground-truth principle; D-074 is drift, this is absence.
  - **The generalisable lesson, and the cheap guard it implies.** A commit whose *title* names a
    decision is not evidence the decision was *logged* — #90's title named D-062 and its diff did not
    add it. **The check that would have caught this is mechanical: every cited `D-NNN`/`F-NNN` must have
    a matching `### ` entry.** Running it over the whole log took one command and found exactly one hole
    besides the documented D-010 skip. **Not built as a gated test here** (that would be its own
    decision, and D-074 dec 3 warns against answering a finding with a framework), but named so the
    next person reaches for it.
  - ⚠ **A live instance of the same defect is open:** **F-009** is cited by the shipped `/about` and
    `/scorer` cohort-boundary note (#116) and by `ARCHITECTURE.md`, and it exists only as a **staged
    document** — it is not yet an entry in this log. It must land as a real `### F-009` in the next
    docs-placement pass, or the project has shipped a UI note citing a finding the log does not contain.

### F-010 — `/api/coverage`'s `analysis_id` is sourced only from folded rows, so the one target whose record most needs explaining reports `null`

- **Date:** 2026-08-03
- **Type:** A finding against an instrument. **Nothing is ruled and nothing is fixed here** — logged
  deliberately unfixed (owner ruling) so it is not smuggled into an unrelated UI PR. The fix belongs
  to whoever is next in `app/reads.py` with a reason to be there.
- **Relates:** **D-043** (a failed fold is not an unattempted one — the same family: a failure falling
  out of a path that succeeds for every other row); **D-038** (`/api/coverage` as the honest-denominator
  supplier); **D-073/D-074** (the same error class reproduced *inside* the instrument built to measure
  it, and the rule that a finding against an instrument is not closed until the instrument stops
  exhibiting it — see the closing note).
- **Numbering:** `F-009` is reserved for the cohort-boundary finding; merged `ARCHITECTURE.md` already
  cites F-009 with that meaning, so this took the next free integer rather than displacing it.

**How known (D-016):** `GET https://pharmfoldmdk.fly.dev/api/coverage`, 2026-08-03, while diagnosing
IGF2R's null `mean_plddt` for the sortable-list work. IGF2R's coverage row reports
**`analysis_id: null`** — while `/api/analyses` reports **`id: 57`** for the same target and the
database confirms `protein_analyses` id=57 exists. Read against `app/reads.py`
`_folded_accessions` / `_coverage_row`.

**The mechanism, named precisely.** `_folded_accessions()` builds `{accession: analysis_id}` under
`WHERE pdb_path IS NOT NULL`, and `_coverage_row()` then sets `analysis_id = folded.get(row.accession)`.
IGF2R's fold hit a CUDA OOM at 2,491 aa, so its `pdb_path` is null and it is absent from that map.

**So this is not a broken join — it is a NAME that does not mean what it says.** The field is called
`analysis_id`, which reads as *"the id of this target's analysis row"*, but it is populated only when
the fold **succeeded**. IGF2R *has* an analysis row; it has no *structure*. The value silently answers
a different question — `folded_analysis_id` — under a name that promises the general one. Adjacent to
D-074's lesson and distinct from it: D-074 is an instrument drifting from its written record; this is a
field whose **name over-promises relative to its own population rule**, and the record was never
written down at all.

#### ⚠ Why this is cosmetic *today* and stops being cosmetic the moment anything consumes it

**Today:** nothing reads `coverage.rows[].analysis_id`. The UI links to targets from `/api/analyses`
(which carries the real `id`), and the D-075 sortable list joins coverage by **accession**, not by
`analysis_id`. So the null is currently inert.

**The trap for a future consumer, stated explicitly so it is not inherited silently:** the first code
that uses `analysis_id` to link a coverage row to its analysis record will work for **79 of 80 rows**
and return null for the one row a reader is most likely to click — the failure they want explained. A
null that appears only on the exceptional row is the hardest kind to notice in review and the easiest
to mistake for "no record exists" when the record does exist. **Anyone reaching for this field should
either fix the population rule first or join by accession instead.**

**Also recorded:** the failure is *asymmetric by construction*, which is why it survived. Every healthy
row gets a correct `analysis_id`; only the failed fold gets a null. A test over the folded majority
passes. This is the D-043 shape again — the exceptional row being the one the code forgets — and it is
the third time this class has appeared (D-043 in the surface, D-073 inside the instrument, now in the
coverage projection).

- **Deep-learning justification.** Neutral to the model; measurement hygiene on the route that supplies
  the **honest denominator** the graded ranking claim rests on. The counts `/api/coverage` serves are
  correct — `fold_status` and `fail_reason` are right for IGF2R, which is what the denominators use — so
  no reported figure is affected. What is wrong is a per-row identifier nobody has consumed yet.

- **Consequences / what closing this requires (D-074).** Not fixed here. When it is fixed, the honest
  options are: populate `analysis_id` for every target that *has* an analysis row (renaming the folded
  map's role), or **rename the field to `folded_analysis_id`** so the name states its own rule. Either
  discharges the finding; a null left under the general name does not. **Per D-074, this entry alone
  does not close anything** — the instrument still exhibits the finding, so until `app/reads.py` changes
  or carries an in-file statement of this limit, F-010 stays open. **No code, no test, no route change
  in this entry.**

### D-075 — A confidence-blind structural axis: does the signal survive when pLDDT information is *replaced* rather than removed, and when attention is matched?

- **Date:** 2026-08-01
- **Status:** Proposed → Accepted on merge. **Ruled before any run.** This entry is the
  pre-registration; **it is void if code precedes it.**
- **Type:** A **decision** — it rules a design and freezes an interpretation before a result exists.
  Exactly D-065's shape, and like D-065 its *result* lands later as its own F-entry (unassigned until
  it exists). **Numbered D-075, not F-008:** F-008 is taken (the two-precision confound, `754e58f`),
  and the drafts predate the live log. The six staged 2026-08-01 documents are swept `F-008` → `D-075`
  in this same commit; all were untracked and never committed, so no published citation is broken
  (contrast D-011, which could not be renumbered because `c07b95b` already named it).
- **Relates:** **D-065** (the two feature-drop ablations this extends); **F-005** (their result — the
  measured baseline below); **F-004** caveat (b) (the confound); **F-008** (the two-precision confound
  — a *third* candidate explanation this design also cannot separate, see Decision 6); D-058 dec 2
  (sensitivity is permitted after the pre-registered result and never replaces it); D-041 (the model,
  unchanged) and **D-041 dec 4** (thresholds are not invented to make a call); D-060 (leakage guards,
  RNG discipline); D-027 (the fixed six).
- **Provenance (D-016):** the Grok adversarial second opinion (2026-08-01) escalated the
  pLDDT-attention confound from open caveat to potentially load-bearing and named the two tests D-065
  did not run — a confidence-blind *replacement* and a popularity-matched control. Orders:
  `docs/ORDERS-Code-2026-08-01-D-075-ablation.md`.

**Context — why D-065 alone is not enough.** D-065's `no_plddt` drops features 3 and 4 and asks *does
the shift survive their removal?* But dropping them also removes the **information** they carried
(membrane-proximal accessibility), so a null `no_plddt` result is ambiguous: signal gone because pLDDT
was confounded, or because real geometric information was amputated? This entry resolves the ambiguity
by **replacing** that information with a confidence-blind measure, and by testing attention directly.

#### Decision (0) — ⚠ the baseline is measured, not hypothetical, and it is not "chance"

**How known (D-016):** read-only `SELECT` over `ranking_results` ⋈ `ranking_runs`, 2026-08-01, against
the live MPG database. The percentile→symbol pairing is positional against `lambda_per_fold` and was
**verified, not assumed** — NECTIN4 0.8482→0.6339 and JAG1 0.5804→0.8304 reproduce F-005 Finding 5's
quoted values exactly, as do EGFR 0.9554, CDCP1 0.9018, ERBB2 0.8661.

| run | set | median | mean | ≥0.5 | Spearman | params |
|---|---|---|---|---|---|---|
| **id=2** | FULL (F-004, `run_kind='preregistered'`) | **0.6071** | **0.6176** | **8/12** | −0.04828045 | 7 |
| **id=3** | `no_plddt` (F-005, `sensitivity`) | **0.5625** | **0.5893** | **6/12** | −0.04828045 | 5 |
| id=4 | `plddt_only` (F-005, `sensitivity`) | 0.6786 | 0.6295 | 9/12 | −0.28968 | 3 |

Denominators identical across all three (D-065 dec 2): ranking set **56** · positives **12** ·
head-to-head **8** · floor **50.0**; 12/12 folds converged; no λ at a grid edge.

**⚠ `no_plddt` is NOT "≈ chance", and the drafted interpretation table said so wrongly.** Only the
**count** (6/12) is exactly even; the **median 0.5625 and mean 0.5893 are both above 0.5.** F-005's
"falls to exactly even" was a claim about the count alone. Three further properties of this baseline
bound how finely it can be read, and are recorded here **before** any comparison exists:

1. **The 6/12 count turns on one rank step.** `no_plddt`'s SLC3A2 = 0.4911 = **55/112**; chance is
   56/112. A single rank position separates 6/12 from 7/12.
2. **Percentiles are quantised in 1/112 (0.00893); the 12-value median in 1/224 (0.00446).** The
   FULL→`no_plddt` median gap is 10/224 = **0.0446** — ten steps of the finest available increment.
3. **Neither median sits on a datum.** `no_plddt`'s 6th/7th sorted values are 0.4911 and 0.6339 — the
   median is the midpoint of a 0.143-wide gap straddling 0.5, so it moves in large jumps. FULL's
   (0.5804/0.6339) is comparably placed. **At n=12 the median is not a stable anchor.**

#### Decision (1) — the confidence-blind feature set (frozen before any run)

| Set | Features | Parameters |
|---|---|---|
| `no_plddt` (D-065) | 1 (ECD length), 2 (Rg), 5 (SASA), 6 (patch fraction) | 5 |
| **`geom_proxy`** (new) | 1, 2, 5, 6, **+ 7 (membrane-proximal SASA, coordinate-only)** | **6** (5 features + intercept) |

`geom_proxy` restores the *membrane-proximal accessibility information* feature 4 carried, measured
from **geometry alone, with zero pLDDT input.** If the signal is real geometric structure, `geom_proxy`
recovers what `no_plddt` lost. If the signal was pLDDT-as-attention, it does not — the proxy carries no
confidence information.

#### Decision (2) — ⚠ the proxy MUST be confidence-blind, proven by a **two-armed** biting fixture

Feature 7, membrane-proximal SASA:

- computed on the **raw atomic coordinates** over the **same membrane-proximal window rule** feature 4
  uses — `k = max(1, ceil(MEMBRANE_PROXIMAL_FRACTION · n_res))`, C-terminal (`core/features.py:48,363`).
  **The rule is factored into a shared helper and reused; it is not redefined.**
- **`n_res` is derived from the parsed coordinate residues, never from `len(plddt)`** (strengthened
  2026-08-01 over the drafted order). Feature 4 sizes its window off the pLDDT array; feature 7 must
  not, or it inherits a dependency on the pLDDT file's *shape*.
- **must not read the pLDDT / B-factor column at any point** — no confidence weighting, no
  pLDDT-based residue filtering, no confidence-derived window adjustment.

**⚠ Tests that MUST go red first — both arms, on a deliberately contaminated implementation:**

| Arm | Fixture | Assertion |
|---|---|---|
| **A — values** | two structures, **identical backbone coordinates, different pLDDT/B-factor values** | byte-identical membrane-proximal SASA |
| **B — shape** | identical coordinates, **differing-length pLDDT array** | byte-identical membrane-proximal SASA |

Arm B exists because **arm A cannot catch a length dependency**: an implementation sizing its window
off `len(plddt)` passes a same-length/different-values fixture while still reading the pLDDT file.
Confidence-blindness would then be proven for values but not for shape.

- Build the contaminated impl (reads the B-factor; sizes off `len(plddt)`) → **both arms RED.** Confirm
  the red.
- Fix to coordinates-only → **both arms GREEN.**
- **If either arm cannot be made to go red on a contaminated impl, that fixture is not biting and the
  proxy's confidence-blindness is unproven — a stop-and-report condition, not a proceed.**

**Why this is the load-bearing test.** A proxy that silently leaked pLDDT would look clean while
reproducing the exact confound this entry exists to exclude — the *"function exists ≠ function does
what it claims"* failure class, and the same family as D-074 (an instrument diverging from its
written record). The whole value of `geom_proxy` is that it is confidence-blind; that property must be
**proven by a biting test, not asserted.**

> **Addendum to Decision 2 — added 2026-08-01, still before any run. Changes no test, no
> interpretation, and no feature set; it records a structural guarantee that already held.**
>
> **Feature 7's confidence-blindness is guaranteed by the parser, not merely tested by the fixture.**
> `core.features.Atom` carries **no `b_factor` field** and `parse_pdb` never reads columns 60-66, so a
> feature computed from parsed atoms **cannot reach the confidence column at all**. The leak objection
> is therefore *architecturally impossible via the coordinate path*, not just unobserved — and that
> strengthens the eventual result: a `geom_proxy` survival cannot be answered with *"your proxy
> probably leaked pLDDT somewhere,"* because the type it is built from has nowhere to leak from.
>
> Consequences for how the two arms are read, recorded so neither is over-sold:
> - **Arm B (differing length) is the load-bearing arm.** Sizing the window off `len(plddt)` is the
>   live, plausible mistake — feature 4 legitimately does exactly that — and no structural guarantee
>   prevents it, only the fixture.
> - **Arm A (differing values) guards a future regression**, not today's design: it bites against an
>   implementation that re-parses the raw PDB text itself, bypassing `Atom`. It passes near-trivially
>   for the clean design, which is why the guarantee is asserted *directly* by
>   `test_atom_type_cannot_carry_confidence` — if `Atom` ever gains a `b_factor`, that reddens and
>   arm A's strength must be re-argued rather than assumed.

#### Decision (3) — the popularity-matched control (the direct attention test)

D-065 tests attention only indirectly, via feature removal. This tests it directly.
`scripts/attention_control.py` computes, per target, two frozen attention proxies:

| Proxy | Definition | Source | Character |
|---|---|---|---|
| **`pdb_present`** | 1 if the target has an experimentally solved structure in the PDB, else 0 | RCSB / UniProt xref, **frozen date recorded** | binary, low-noise, the strong proxy |
| **`pub_count`** | literature density (PubMed hits for the gene symbol) | PubMed, **frozen query + date recorded** | continuous, noisier; catches attention without a solved structure |

**The control:** re-rank with the structural (ablated) score after covariate-adjusting or stratifying on
the attention proxy, and test whether positives still enrich. Run against `pdb_present` and `pub_count`
**separately** — a sensitivity pair, not one blessed number.

**⚠ Both proxies frozen (source + query + date recorded in this entry) BEFORE the control runs.** No
re-querying after seeing a result. Re-running with the same frozen inputs must be byte-identical.

#### Decision (4) — ⚠ THE FROZEN INTERPRETATION. Fixed before any run.

**No reading anchors on a single statistic.** Every cell below is judged on the **explicit triple —
median, mean, and count ≥0.5, reported side by side and read in prose.** The comparison is
three-against-three: **`geom_proxy` toward FULL (0.6071 / 0.6176 / 8-of-12)** versus **`geom_proxy` at
the `no_plddt` baseline (0.5625 / 0.5893 / 6-of-12)**. There is no threshold and none will be invented
after the fact — **D-041 decision 4**, D-065 precedent. Decision 0's three fragility properties travel
with every judgement.

| Outcome | Reading |
|---|---|
| **All three of `geom_proxy`'s statistics sit toward FULL** (median ≳0.6071, mean ≳0.6176, count 8-of-12) — the proxy recovers what `no_plddt` lost | **Confound weakened.** The signal is geometric accessibility, not confidence. The membrane-proximal information matters; its *pLDDT encoding* was not what carried it. |
| **All three sit at the `no_plddt` baseline** (median ≈0.5625, mean ≈0.5893, count 6-of-12) — the proxy does not recover it | **Two live readings, reported as both:** either the signal was pLDDT-as-attention, **or** real membrane-proximal information exists and neither a SASA proxy nor n=12 can capture it. **Ambiguous, and reported ambiguous.** ⚠ Note this is *not* "≈ chance" — the baseline itself is above 0.5 on median and mean (Decision 0). |
| **The three statistics disagree** (e.g. median toward FULL, count at baseline) | **Reported as a split, not resolved to one number.** Decision 0.1–0.3 make this the *expected* case at n=12: one target's rank moves the count, ten of the finest increments span the whole median gap. A split is a legitimate, reportable outcome. |
| **Signal survives popularity-matching on BOTH `pdb_present` and `pub_count`** | **Confound substantially excluded.** The strongest available evidence the axis is not attention. Grok's sinking question is answered. |
| **Signal survives one proxy but not the other** | **Informative split, reported honestly.** Not hidden, not averaged away. |
| **Signal vanishes under matching** | **Confound strengthened → Branch B.** The enrichment is not separable from research attention. **This is the finding, reported prominently** — it redirects the paper, and it is far better found here than by a reviewer. |

**⚠ Spearman is a dead discriminator here and carries no weight in any cell above.** Against the
two-valued comparator, FULL (id=2) and `no_plddt` (id=3) agree to **full float precision**
(−0.04828045495852675) while their per-target percentiles differ by up to 0.25 — exactly what F-005
Finding 5 predicted, since Spearman then depends only on the rank-sum of the score-5 group and is
quantised in ~0.024 steps. **If `geom_proxy` returns the same value again, that is not corroboration;
it is the statistic being blind.** It is reported for completeness and read as evidence of nothing.

#### Decision (5) — structural prevention of fishing and headline-drift (inherits D-065)

- **`--ablate` accepts only named sets:** `no_plddt`, `plddt_only` (D-065), `geom_proxy` (this entry).
  **Arbitrary subsets refused by the code** (`ValueError`, `core/scorer.py` `FEATURE_SETS`). No new set
  without a new dated entry.
- Each run writes its own `ranking_run`, `run_kind='sensitivity'`, set name tagged. The attention
  control writes its own tagged artifact, `run_kind='attention_control'`, proxy name + frozen date.
- **The pre-registered run (id=2) stays `run_kind='preregistered'`, is never recomputed, and is read
  from its row.** Verified read-only this session: `scripts/fit_scorer.py` always mints a *new* run
  (`create_ranking_run`) and no CLI path targets an existing id. ⚠ `persist_results()` itself is
  unguarded — handed `2` it would overwrite — so **read-only is a property of the call path, not the
  function.** Any new persist path added here must not weaken that.
- **F-004 is not amended.** Results land in this entry's later F-entry, citing F-004 and D-065,
  modifying neither.
- **The six-feature assertion on the pre-registered path stays green.** If it reddens, an ablation has
  leaked into the pre-registered path and the PR is wrong (D-065 dec 5).
- **No third proxy, no fourth ablation, to clarify an ambiguous result.** That is a new dated entry.

#### Decision (6) — what this design still cannot separate, named up front

**F-008's two-precision confound is a third candidate explanation and this design does not resolve
it.** Tier was assigned by length (≤440 aa local/int8, above rental/fp16), so precision, length, and
tier are mutually confounded with no overlap. Feature 7 is computed from coordinates produced under
that same split, so a `geom_proxy` result — either direction — inherits it. F-008's named resolution
path (a controlled A/B re-fold at the opposite precision, never touching the reported cohort) is **not
run here and is not a prerequisite.** Recorded so a survival result is not over-read as excluding
*all* confounds, only the confidence one.

⟡ **Second item, added 2026-08-06 with `### F-017` — fold-recipe heterogeneity.** The cohort spans
three fold recipes: `(int8, 64) × 42`, `(fp16, None) × 34`, `(fp16, 64) × 3`, and **one unrecorded**.
**F-015 is untested at the cohort's actual variable** (`None` vs `64`) — F-012 measured chunk 16 vs 64
and not this. ⚠ **No claim in either direction:** *"those 34 folds are fine"* is exactly as
unsupported as the opposite. This design cannot separate a recipe effect from the axis it measures.

⟡ **Third item, added 2026-08-06 with `### F-017` — the coordinate-mediated correlation.** Feature 7
is **architecturally blind** to pLDDT — `Atom` carries no `b_factor`, `parse_pdb` never reads columns
60-66, and the contaminated fixture reds on both arms — **and it is measurably correlated with it.**
Against feature 4 (`membrane_proximal_plddt`) Pearson **−0.4898** / Spearman **−0.5490**; against
feature 3 (`mean_plddt_ecd`) Pearson **−0.6208** / Spearman **−0.4694**; the two confidence features
correlate with each other at **+0.7959 / +0.7695**. The pathway is **the folded coordinates
themselves**: feature 7 is computed over structure ESMFold produced, so it can track confidence
without ever reading it. ⚠ **This design cannot separate *"membrane-proximal geometry carries the
signal"* from *"membrane-proximal geometry is a readout of the same thing confidence reads."***

> ⚠ **Scope of those coefficients, and it binds any later citation.** They were measured on **the 56
> ranking-set rows, at one recipe composition, on this cohort as folded**. They are a property of
> **this instrument's output on this cohort — not a constant of the features**, not a property of
> `membrane_proximal_sasa` in general, and not transferable to the census, to a re-fold at a
> different precision, or to any other population. **A number lifted out of this sentence and quoted
> alone would be a general claim this design never made.**

#### Implementation findings — ⚠ TWO invisible pre-registration corruptions, caught and guarded

**Recorded as findings, not as incidental fixes.** Both were latent in code that was green, both
would have silently changed the **pre-registered** result while every existing test passed, and
neither was anticipated by the order. *"A pre-registered result was silently corruptible through the
feature-projection skip and through the completeness check"* is the kind of near-miss this log exists
to capture. **Same class as the `runner.write_artifacts`-has-no-production-caller correction
(2026-07-23):** *function exists ≠ function does what it claims* — a true statement with a false
implication, found by checking the tree rather than trusting the premise.

**How known (D-016):** both found while wiring feature 7 through `run_scorer` and
`scripts/fit_scorer.py`; the first was **proven by reverting the fix and watching the guard redden**
(it reported 7 coefficients), the second by reading the predicate that decides ranking-set membership.

**Corruption 1 — the graded fit would have used seven features and eight parameters.**
`core/scorer.py`'s `run_scorer` projected rows onto the named feature set **only when the set was not
`preregistered`**:

```python
if indices != FEATURE_SETS["preregistered"]:      # the skip
    ranking_rows = [replace(r, features=…) for r in ranking_rows]
```

That was correct **only while every row carried exactly six features** — an invariant nothing
asserted. D-075 makes rows arrive **seven** wide, so the skip would have handed the pre-registered
model all seven columns: **8 parameters where D-041/D-060 pre-registered 7, with feature 7 — an
ablation input — inside the graded fit.** Nothing in the output would have shown it; the reported
distribution would simply have been a different model's. **Guarded:** projection is now
unconditional (a no-op for a six-long row, so no prior behaviour changes), and
`test_seven_wide_rows_do_not_leak_feature_7_into_the_preregistered_path` asserts 6 coefficients
against a 7-wide row *and* that the pre-registered fit is byte-identical with and without a seventh
column present. **The guard is proven, not assumed** — restoring the skip reddens it.

**Corruption 2 — F-004's 56 could have been moved by an ablation's input.** In
`scripts/fit_scorer.py`, `features_complete = all(v is not None for v in rec.features)` is what
decides `in_ranking_set`. Appending feature 7 to `FeatureRecord.features` — the obvious way to make
it available — would have meant **a null feature 7 dropped a target out of the ranking set**,
changing the pre-registered denominator **56** and therefore F-004 itself, from a column that exists
only for a sensitivity analysis. **Guarded:** feature 7 is carried in its own field, membership stays
defined by the six, and a ranking-set row arriving without feature 7 **warns loudly** rather than
being fitted on a `0.0` placeholder as though measured (D-027 — an imputed value is the worst option).

**The generalisable lesson.** Both corruptions share a shape: **a pre-registered quantity defined
implicitly, by the width or completeness of a data structure, rather than explicitly by name.** The
count of features and the membership of the ranking set were both *emergent* properties of a tuple,
so widening the tuple silently redefined them. **An ablation must not be able to reach the graded path
through a shared data structure** — which now holds by construction, asserted in both places.

**Process note, recorded plainly (D-016).** While proving corruption 1's guard by reverting the fix,
`core/scorer.py` was briefly left in the reverted (buggy) state because the backup path failed; it was
caught immediately, restored, and re-verified green. Recorded because caught-and-corrected process
facts belong in the record — no inflation, no omission.

- **Deep-learning justification.** The question is *what ESMFold's own confidence encodes* — structure,
  or training-set representation. pLDDT is a network output used as signal (D-041 §2 item 3). Replacing
  it with a coordinate-only measure and matching on attention directly tests whether the network's
  uncertainty was carrying structure or carrying popularity. This is the most directly DL-relevant
  follow-up available: one refit plus one control against an existing pipeline, no new model, no new
  parameters on the pre-registered path.

- **Consequences / test surface:**
  - **The confidence-blindness fixture reds on a contaminated impl and greens on the clean one, on
    BOTH arms (values and length)** — the load-bearing test; a non-biting arm is stop-and-report.
  - `--ablate` refuses any set not in the named three — asserted; arbitrary subset raises.
  - Feature-count assertion: `geom_proxy` = **6 parameters** (5 features + intercept).
  - `run_kind` persisted; sensitivity/attention runs never returned where the pre-registered run is
    expected — fixture holds all kinds.
  - The three D-060 leakage guards **re-assert on the `geom_proxy` path**: scrambled comparator →
    identical coefficients; held-out features unchanged; λ-selector never sees the held-out index.
  - Determinism: same fixture, two runs, byte-identical coefficients.
  - ⚠ **Watch λ against the grid edge.** `no_plddt` already moved MERTK 31.6→**100.0** (and CDH11,
    SLC39A6 10.0→31.6) without hitting an edge; `geom_proxy` restores a feature, so λ moves again.
    `lambda_at_grid_edge` is the assertion. **The grid is never re-centred** (D-063 refusal).
  - Attention proxies: frozen date/query persisted; re-running with the same frozen inputs is
    byte-identical.
  - **No run in the implementing PR.** Runs are owner-authorised after merge, interpretation already
    frozen by this entry.

### D-074 — A finding against an instrument is not closed until the instrument no longer exhibits it — or carries, in itself, the statement of what it gets wrong

- **Date:** 2026-07-30
- **Status:** Proposed → Accepted on merge.
- **Relates:** F-002 (the finding whose instrument drifted), D-073 (the tracking and correction that
  closed it in the file), D-016 (name how it is known — the citation left dangling), D-038
  (`/api/coverage` is the folded-set supplier — error class 1), D-043 (a failed fold is not an
  unattempted one — error class 2, reproduced *inside* the instrument built to measure it), F-001
  (the adjacent, distinct lesson — Decision 2).

**Context.** `intersection_check.py` computes the pre-registered reports A–I that supply the ranking
and comparator denominators. **F-002 and this log both cite it by path — `scripts/intersection_check.py`
— as their D-016 provenance artefact, and that path did not exist**; the file sat untracked at the
repo root from 2026-07-27 to 2026-07-30. Run as handed over on 2026-07-30, before it was touched, it
printed **`80` under the label "folded"** and **`13 of 80 = 16.2%` below the floor** — against
F-002's recorded **`79`** and **`12 of 79 = 15.2%`**, in the same repository. Both were errors
**F-002 had already found, named, and explained**, and neither had been closed in the file.
**F-002 was exemplary**: it caught both errors in its own instrument, recorded them *before* the
numbers, explained how they change the reading, and reported corrected figures. **The gap was not in
the log. It was that the log is not the instrument's home.** D-073 (`da86e87`) closed both errors in
the file and verified the correction by exact agreement with F-002's recorded figures.

#### Decision (1) — ⚠ the rule

**When a finding is against an instrument, it is not closed until the instrument no longer exhibits
the finding — or the instrument carries, in itself, the statement of what it gets wrong.** The second
is acceptable and sometimes the only option; an instrument that prints its own known limitation is
honest. **Silence in the file is not.** It converts the log from a record into a trap: the next
reader finds a tracked script at a cited path, runs it, and gets numbers the log contradicts, **with
no marker on the file saying so**. For a *claim*, recording it in the log **is** closing it — the log
is where claims live. For a *tool*, recording a finding against it is **half**.

#### Decision (2) — the boundary against F-001, named so this is not read as a restatement

**F-001** — a metric can be real, well-defined, correctly queried, and still measure the wrong thing
(WHEA corrected-error rate was *anti-correlated* with the crashes it was used to predict). It is
about **trusting an instrument's output**. **D-074** — an instrument can diverge from its own written
record, so that the log and the file disagree and only the log is read. It is about **the instrument
drifting from the document that describes it**. Adjacent, distinct, both carried. F-001 is about
whether the number means what you think; D-074 is about whether the tool still does what the log says
it does.

#### Decision (3) — what this authorizes as standing mechanism, and what it does not

**An instrument cited as provenance carries an in-file assertion that re-derives the finding it is
cited for, so drift fails loud rather than printing quietly.** `scripts/intersection_check.py`
**already satisfies this as of D-073**: the F-002 partition must reconcile (asserted, so the reports
refuse to be trusted if it stops), and F-002 Finding 1 — *every ranked target is folded* — is treated
as an **observation, not a guarantee**, warning on divergence instead of silently redefining the
ranking denominator D. **D-074 names that pattern as the rule; it does not commission a new build.**

**⚠ No drift-detection framework, no generic instrument-audit test, no new script, route, or test
file.** The mechanism is the per-instrument self-assertion, applied when an instrument is cited.
Building a framework here would add a second thing that can drift and would be its own violation.

#### Decision (4) — scope: the trigger is citation

The rule binds **instruments cited as provenance** — a script, query, or notebook the log names as
*how a number is known*. **It imposes nothing on throwaway or exploratory scripts.** The moment the
log points at a tool as authoritative, that tool owes an in-itself statement of what it re-derives or
what it gets wrong. Until then it owes nothing. This keeps the rule cheap and keeps it from
decaying into ceremony.

- **Deep-learning justification.** Neutral to the model; load-bearing for the graded claim. Reports
  D/E/G/H are the **fit and comparator denominators the D-041 scorer is trained and judged on** — an
  instrument that miscounts the folded set miscounts what the network learns from and what its result
  is measured against. The project's defensible claim is not that the network is good but that
  **its inputs and its evaluation are checkable**; an instrument whose known errors live only in the
  log, while the file keeps printing them, breaks exactly that property.

- **Consequences / test surface:**
  - **No new executable change.** The mechanism D-074 names is already present as of D-073
    (`da86e87`); this entry is a rule plus the naming of an existing pattern.
  - Filed as a **decision, not a finding** — F-entries are findings about the object of study (the
    cohort, the scorer, the ranking); **D-074 is about the method.** No F-number assigned;
    F-001…F-007 untouched.
  - The rule's cost is bounded by Decision (4): it applies on **citation**, not on authorship.
  - **The next instrument cited as provenance is the test of this entry** — if it is cited without a
    self-assertion and without an in-file statement of its limits, D-074 was written and not applied.

### D-073 — The intersection instrument is tracked, and the two errors F-002 recorded against it are closed in it

- **Date:** 2026-07-30
- **Status:** Accepted
- **Context:** `intersection_check.py` had been sitting **untracked at the repo root** since
  2026-07-27. It is not scratch: it computes the pre-registered reports A–I of
  `docs/ORDERS-Code-2026-07-27-ADDENDUM-intersection.md`, and **F-002 and this log already cite it
  by path as their D-016 provenance artefact** — `docs/README.md` §F-002 and
  `docs/F-002-final-and-F-003-draft.md` both name `scripts/intersection_check.py`, a path that did
  not exist. Deleting it as a stray would have silently falsified a provenance citation; leaving it
  untracked leaves the citation dangling. The commit was deliberately deferred — the addenda say
  *"do not commit `intersection_check.py` until the D-058 features PR is merged and green"* — and
  **that condition is discharged**: D-058 is `73c0742` (PR #85), contained in `main`.
- **Decision:** Move it to `scripts/intersection_check.py` and track it, **and fix in the
  instrument the two errors F-002 recorded against it and never closed.** Re-running the file as
  handed over reproduced both wrong numbers today (`80`, and `13 of 80 = 16.2%`):
  1. **`/api/analyses` is the ENQUEUED set, not the folded set** — `core/enqueue.py` writes a
     `protein_analyses` row at enqueue time. Report A printed its row count under the label
     *"folded"*. The folded set now comes from `/api/coverage` (the D-038 honest-denominator
     supplier), whose rows carry a per-target `fold_status`; the enqueued count is still printed,
     explicitly labelled as not a fold count.
  2. **A failed fold is not a low-confidence one** — the predicate `plddt is None or plddt < FLOOR`
     absorbed IGF2R (`fold_status=failed`, null pLDDT) into the below-floor bucket. **This is the
     D-043 error class reproduced inside the instrument built to measure it.** Failed folds are now
     reported separately. Below-floor is computed over folded targets only.
  Two self-checks are added rather than left implicit: the F-002 partition must reconcile
  (asserted), and F-002 Finding 1 (*every ranked target is folded*) is an **observation, not a
  guarantee**, so a future divergence prints a warning instead of silently redefining the ranking
  denominator D. No dated figure is hardcoded, so a later run reports the new truth rather than
  re-asserting the old one.
- **How known (D-016):** `scripts/intersection_check.py` run 2026-07-30 against the live
  deployment. **The corrected instrument reproduces F-002's recorded figures exactly** — 79 folded,
  **12 of 79 = 15.2%** below floor, 1 failed (IGF2R) separate, D = **56**, comparator = **12**,
  H = **8**, CXCR5/MSLN/MUC16 falling out by three distinct mechanisms, partition
  `82 = 67 + 13 + 2` and `79 + 1 + 2 = 82`. That agreement is the verification: the tracked
  instrument re-derives the finding the log already carries. The uncorrected version's `80` and
  `13 / 16.2%` are recorded here as what it actually printed today, not as history.
- **Deep-learning justification:** Neutral to the DL core — this is measurement hygiene, not model
  work. It is load-bearing *for* the DL core: reports D/E/G/H are the fit and comparator
  denominators the D-041 scorer is trained and judged on, so an instrument that miscounts the
  folded set miscounts what the network learns from. An instrument whose known errors live only in
  the log, while the file keeps printing them, is a trap for the next reader.
- **Consequences:** `scripts/` is already in `.dockerignore`, so tracking it does not touch the
  serving image. No gate runs it (it needs the live deployment); it stays owner-run, like
  `worker/ceiling_probe.py`. The `"(untracked at time of measurement)"` wording in the two
  citations stays **accurate as a historical statement** and is deliberately not edited — it
  records the state at measurement time, which is what a provenance note is for. F-002's numbers
  are unchanged by this entry; only the instrument changed, and it now agrees with them.
  `ARCHITECTURE.md`'s `scripts/` inventory is updated in this PR.

### D-072 — The miniature demo notebook: the whole pipeline on one live-folded target, no gate, no refit

- **Date:** 2026-07-30
- **Status:** Accepted
- **Context:** Delivery-eve, a professor-facing artifact was wanted that shows *the entire
  pipeline in miniature, on one real target, folded live* — not a screenshot, not a mock. Orders
  `ORDERS-Code-2026-07-30-miniature-notebook.md`. Target: NECTIN4 (UniProt Q96NY8), whose sliced
  ECD span 32–349 = 318 aa is under the local known-good ceiling (`core.manifest.CEILING_KNOWN_GOOD`
  = 440), so it folds on the 8 GB RTX PRO 2000 with the S-003 int8/chunk-64 recipe.
- **Decision:** `notebooks/miniature_NECTIN4.ipynb` — six steps (question / live fold / structure+pLDDT
  render / six features / place in the ranking / honest limits), a plain-language (8th-grade)
  markdown block before every step. It imports the **real** `core.features`, `core.scorer`,
  `core.contracts`, `core.manifest`, and `worker.runner` and runs them; every structural number is
  computed in-session. A **fourth dependency world**, `requirements-notebook.txt` (demo-only,
  GPU-tier), is created at repo root and is **never** added to `requirements.lock` /
  `requirements-dev.lock` / the image; `notebooks/` + `requirements-notebook.txt` are added to
  `.dockerignore` as belt-and-braces. Not gated, not in the serving image, **not merged by the
  builder** — the owner authorizes the drop-in.
- **Deep-learning justification:** the centrepiece cell is a **live ESMFold fold** — the graded
  neural core (D-003) doing its load-bearing work in front of the grader, sequence → 3-D structure
  + per-residue pLDDT, which then feed the real feature extractor and the real ranking. The notebook
  exists precisely to make the DL deliverable legible end-to-end on one target; it adds no new model.
- **Consequences / provenance (this session's `jupyter nbconvert --execute` run):**
  - **Two order-vs-repo discrepancies found; the repo won, both reported.** (1) The order named `esm`
    as a dependency, but the repo folds through `transformers` (`EsmForProteinFolding`), not the `esm`
    package — so `requirements-notebook.txt` pins `transformers`/`bitsandbytes`/`accelerate`, not `esm`.
    (2) Order Step 5 asked to *re-apply the fitted model* to NECTIN4's live features. But no fitted-model
    coefficients are persisted anywhere loadable — only per-target `score`/`rank`/`attributions`
    (`target_scores`) and the LOO distribution (`ranking_results`). Since NECTIN4 is itself one of the
    56 ranked targets, its deployed score/rank/LOO **already exist**; the notebook **loads** them from
    the live `/api/ranking` (F-004, no refit) and *places* the live-computed features against that given
    result via the real `core.scorer.percentile_within`. Re-applying a model we would have had to re-fit
    is both impossible here and forbidden (F-004); the load-the-deployed-result seam preserves the
    no-refit rule.
  - **Measured:** NECTIN4 folded live in **52.8 s** on the RTX PRO 2000 (int8/chunk-64), mean pLDDT
    **77.26** (matches the deployed NECTIN4 stored value — reproduces the deployed fold), all six
    features computed with `null_reasons` empty. Deployed result loaded: score **0.2655**, rank
    **8 of 56**, out-of-sample LOO percentile **0.848** (NECTIN4 is a labelled Group B positive, checked
    from the loaded distribution), reference score min/median/max **0.1163 / 0.2203 / 0.2853**. The score
    is `membrane_proximal_plddt`-dominated (+0.197 of the attribution) — a live illustration of F-005
    (ranking is substantially pLDDT-driven).
  - **Gate untouched and green:** `tests/test_image_contents.py` 15/15 pass (it reads the Dockerfile/
    `.dockerignore` as text; the explicit `COPY app/core/db/data` never pulls the notebook world in), full
    suite **340 passed, 15 skipped, 0 failed**. No file under the gate changed to accommodate the demo.

### D-071 — Provenance strength is three-valued: measured at fold time, measured later, or absent

- **Date:** 2026-07-29
- **Status:** Proposed → Accepted on merge.
- **Amends:** D-070 decision 2.
- **Relates:** D-045, D-048, D-070, F-007, F-008, D-016.

**Context.** 75 of 79 folds carry no environment record. D-070 ruled that **inferred** values never
enter the captured fields — correct, because F-007 showed the pinned manifest disagreeing with a
measured fold. **But a reading taken off the fold host is not an inference.** It is a measurement of
the same machine, taken later. **Weaker than fold-time capture, far stronger than a manifest.** D-070
collapsed the two; the distinction is worth having.

#### Decision (1) — three states, ordered by strength, each labelled

| Strength | Source | Renders |
|---|---|---|
| **1 — measured at fold time** | the fold's own `fold_provenance` (D-045) | the four fields, unqualified |
| **2 — measured later, same tier** | `data/tier_environments.json`, keyed by `tier` | the four fields, **with date and qualifier** |
| **3 — absent** | neither | one statement, plus D-070's block |

**⚠ State 2 is visually distinct and says what it is:** *"tier environment, measured {date} — not
recorded at fold time."* **A reader must never have to work out which kind of claim they are looking
at.**

#### Decision (2) — ⚠ AMENDS D-070 decision 2

> **Inferred values never enter the captured fields. A measurement may, with its date and scope
> stated.**

The distinction is **reconstruction versus observation**, not fold-time versus later. D-070's
reasoning was aimed at the manifest and over-reached to cover a reading off the machine. **Recorded as
a Planner over-application** — the same shape as the precedence ruling that over-applied from IGF2R to
TMEM108.

#### Decision (3) — ⚠ the rental tier gets NO state-2 record, deliberately

Local is measurable: the box exists. **The rental pod does not** — RunPod instances are ephemeral and
the 33 uncaptured rental folds ran on instances that are gone. **⚠ The 4 captured rental folds must
NOT populate the other 33** — they describe *those* folds, on *that* instance, on 2026-07-25; applying
them elsewhere is reconstruction wearing a measurement's clothes. **Local fills; uncaptured rental
stays at state 3.** The asymmetry is correct and informative: **ephemeral compute costs provenance you
cannot get back.**

#### Decision (4) — the artefact is a measurement with its own provenance, not a copy of the manifest

`data/tier_environments.json` records what was **read off the machine**, with `measured_at` and a note
that it post-dates the folds. **Not a copy of `worker/requirements.txt`** — F-007 is why those are
different things — and the manifest's contents are still never rendered (D-070 decision 3 stands).
`data/` ships in the runtime tier, so no DEP-001 problem.

- **Deep-learning justification.** F-008 established the cohort was folded under two precisions
  confounded with length, and that features 3–4 — which carry the signal per F-005 — are tier-shifted.
  **A reader cannot evaluate that without seeing what each tier ran.** This panel makes F-008 checkable
  rather than asserted.

- **Consequences / test surface:**
  - All three states render, each pinned by a fixture.
  - **State 2 never renders without its date and qualifier** — asserted.
  - **State 1 is never overwritten by state 2** — a captured fold ignores the tier record (asserted by
    the state-1 branch taking precedence).
  - **No rental tier record exists** — asserted (a rental detail's `tier_environment` is `None`), so a
    future edit cannot quietly add one.
  - Constraint-A: no version string, device name or date typed into a component; the state-2 values are
    served from `data/tier_environments.json`, the state-3 statement carries none.
  - D-070's block still renders for state 3. The four-"not captured"-fields grid is replaced there by
    one statement — better presentation, the asymmetry with state 2 (no values vs values) kept legible.
  - **⚠ Unrecoverability is attached to the ephemeral rental instance, not to state 3 in general.**
    State 3 is rental-only in production (all 42 local folds are state 2, verified), but the state-3
    sentence renders *"…cannot be reconstructed"* **only when `tier === 'rental'`**; a local fold that
    ever fell through would say it was not recorded but **not** that it is unrecoverable — the box
    exists. Asserting unrecoverability about a machine you own is the D-070 failure inverted (claiming
    *less* than the record supports); a defensive test pins the conditional.


#### ⚠ RUN B PRE-REGISTRATION — four free parameters closed, 2026-08-06

**Ruled by the owner 2026-08-06, after Run A returned Decision 4 row 1 (F-017), and BEFORE any
attention-proxy value existed** — `scripts/attention_control.py --freeze` was a deliberate stub,
`data/attention_proxies.json` did not exist, and no proxy had ever been computed for any target.
**The protection is that the data did not exist, not that the ruler was ignorant of Run A.** Stating
the second would be false; the first is checkable.

Decision 3 and Decision 4's matching rows were frozen before Run A. They left four parameters open.
Closing them after seeing a Run B result would be the fishing this entry exists to prevent. They are
closed here instead.

**Ruling 1 — which score Run B re-ranks: `geom_proxy` (`ranking_run` id=5).**
Decision 3 says *"re-rank with the structural (ablated) score."* When written, the only ablated run
was `no_plddt`. Decision 3's own opening sentence distinguishes this control from that one —
*"D-065 tests attention only indirectly, via feature removal. This tests it directly"* — and D-065
**is** `no_plddt`. `geom_proxy` is the confidence-blind structural axis the result now rests on.
⚠ `no_plddt` (id=3) is Decision 4's *baseline*; matching on it would answer a question nobody asked.

**Ruling 2 — covariate-adjust AND stratify, as a declared sensitivity pair.**
Decision 3 says *"covariate-adjusting or stratifying."* The `or` is a live free parameter inside a
frozen decision. **Both are run.** This is Decision 3's own discipline — *"a sensitivity pair, not
one blessed number"* — applied to the method rather than to the proxy. **Four results total: two
methods × two proxies.** ⚠ **Disagreement between methods is reported as disagreement and is not
resolved toward the cleaner one**, exactly as Decision 4 treats disagreement among the triple.
The stratification rule for `pub_count`, being a second free parameter, is fixed here: **quartiles of
the frozen `pub_count` over the 56 ranking-set rows, computed from the snapshot, never re-cut.**
`pdb_present` is binary and strata are its two values.

**Ruling 3 — what "still enrich" means: the triple, against `geom_proxy`'s unmatched result.**
Decision 4's matching rows say *survives* / *survives one but not the other* / *vanishes*, and never
operationalise *survives*. Run A needed no judgement because Decision 4 anchored it to explicit
numbers. Run B is read the same way: **median, mean, and count ≥0.5 of the matched positive
percentiles, read against `geom_proxy`'s unmatched triple — 0.6607 / 0.6324 / 8-of-12 — as the
anchor.** *Survives* = all three sit toward it. ⚠ **No threshold, no significance test, no single
statistic** (D-041 dec 4; D-065/D-075 dec 5). The anchor is a number that already exists in the
record and cannot be tuned.

**Ruling 4 — the proxies are three-valued, and absence excludes rather than defaults.**
Decision 3 defines `pdb_present` as *"1 if the target has an experimentally solved structure in the
PDB, else 0"* — binary, with no state for *"the lookup failed."* ⚠ **This fills that gap; it does
not amend the definition.** A protein with no PDB entry is a **measured zero**. A protein whose
lookup errored is an **absence**, and coercing it to `0`/`False` manufactures a positive claim about
the world out of a network failure — **which in a matching analysis does not merely miscount, it
moves the matching.** F-020's shape, in the control rather than the fit.

Both proxies are recorded as **`measured` / `measured_zero` / `absent_with_reason`.** An absent value
is a **CATEGORY** — never `0`, never `False`, never a bare null. **A target with an absent proxy is
excluded from that proxy's matched analysis and named**, never defaulted into it.

**The exclusion thresholds, fixed here and acknowledged as arbitrary:**
- **0 positives excluded** — report normally.
- **1–2 positives excluded** — ⚠ **run is reportable, with the excluded targets named, and the
  analysis repeated on the reduced set with both results shown.** At n=12 one exclusion is 8% of the
  label set; that fact is stated wherever the result appears.
- **3 or more positives excluded** — ⚠ **VOID.** Fix the fetcher, re-pull under a **new as-of date**,
  and record the void run and its reason. A void run is not deleted.

⚠ **These numbers are arbitrary and are recorded as arbitrary. An arbitrary threshold fixed before
any pull is legitimate; the same number chosen afterwards is not.** That difference is the whole
reason this block exists.

**Sequencing, unchanged from §3 of the run order:** Run B follows the wiring PR and the freeze, in
its own window, under separate owner authorisation. The proxies are frozen with source, query
string, and date recorded **before** any Run B result is read, and re-running from the frozen
snapshot must be byte-identical.
---

### F-008 — The cohort was folded under two precisions confounded with length; F-005 gains a third candidate explanation the design cannot rule out

- **Date:** 2026-07-29
- **Type:** A finding. Nothing ruled — it **bounds** F-005, it does not replace it.
- **How known (D-016):** read-only SQL over `protein_analyses` (79 folded) grouped by `tier`, plus a
  within-tier pLDDT~length regression. No re-fold, no mutation.

**Measured — the split.**

| tier | precision | n | fold length (aa) | mean pLDDT |
|---|---|---|---|---|
| **local** | int8, chunked | 42 | 13–439 (mean 175) | **61.88** |
| **rental** | fp16 | 37 | 441–2213 (mean 735) | **71.04** |

Tier was assigned by length (≤440 aa local), so **precision is confounded with length by
construction** — no protein folded both ways, no overlap in the length ranges.

#### Finding — a third horn for F-005

F-005 Finding 3 named two live explanations for the pLDDT-carried signal (training-set attention;
genuine order-versus-disorder). There is a third, not previously in the log: **pLDDT is a model
output, not a physical measurement, and int8 trunk quantization changes the numerics relative to
fp16.** Because tier = precision = length, and length is feature 1, **features 3–4 (pLDDT) partly
encode which machine and precision ran the fold, which was decided by size.** The signal F-005
attributes to confidence could in part be an artifact of the compute split.

#### ⚠ The direction complicates the artifact reading — do not call it an int8 penalty

The rental folds are **longer** (735 vs 175 aa) yet score **higher** (71.04 vs 61.88) — the *opposite*
of the usual expectation that longer chains fold with more disorder and lower confidence. So the
between-tier gap is **not straightforwardly an int8 quantization penalty**; something else moves with
it. **This makes the confound harder to characterise, not easier** — which is the honest position and
the stronger one.

#### The within-tier texture — "two curves", not "two populations on one line", but still unresolved

Regressing pLDDT on length **within** each tier, the slopes differ in sign:

| tier | slope (pLDDT per 100 aa) | corr(pLDDT, length) |
|---|---|---|
| local | **+4.09** | +0.43 |
| rental | **−1.45** | −0.53 |

The differing slopes **rule out a single straight-line length relationship** ("two populations on one
line"). But they are consistent **both** with precision changing the length-response **and** with a
single non-linear, humped pLDDT-length curve peaking near the 440-aa tier boundary. Because the length
ranges do not overlap, **the data cannot distinguish these.** It distinguishes *two curves from one
line*; it does not resolve *precision from length*.

#### The label bound — observed-balanced, not confound-free

The 12 labels split **6/6** across tiers (rate 14.3% local vs 16.2% rental). This is **consistent with
no hardware→label path, but does not establish one:** at n=12, a genuine 2:1 tier skew would produce
6/6 often enough that it cannot be ruled out. Balanced is what was observed; "no confound path" is more
than twelve points can carry.

#### Unresolvable by construction — the resolution path

Precision cannot be separated from length in this data (no overlap). The only test of the precision
effect is a **controlled A/B — re-fold a handful of proteins at the opposite precision as a diagnostic
spike, never touching the reported cohort** (D-070 dec 4 refuses re-folding the result's folds). Named
as the only resolution path; not run.

- **Deep-learning justification.** This names a possible measurement artifact in the **load-bearing
  feature** — the one F-005 shows carries the signal — and it is exactly the confound an examiner looks
  for in a cohort folded two ways. Naming it, bounded, is a stronger position than leaving it for a
  reader to notice.

- **Consequences.** F-005's open question gains a third, currently-inseparable candidate; **F-004 /
  F-005 / F-006 stand — this bounds them.** No code, no re-fold, no change to the reported result.
  **⚠ Root cause and the design lesson:** the length-threshold tier rule created this confound. A
  future cohort either folds at a single precision, or **deliberately overlaps the length ranges across
  precisions** so the effects can be separated — a lesson that generalises past this project.

---

### D-070 — An uncaptured environment is explained from what IS recorded, and never populated from inference

- **Date:** 2026-07-29
- **Status:** Proposed → Accepted on merge.
- **Relates:** D-045 (the capture), D-048 (the two-population panel), D-016 (name how it is known),
  D-050 (derived, never duplicated), DEP-001 (`worker/` is not in the serving image), F-007.

**Context.** 76 of 80 folds predate D-045 and show four fields as *not captured*. The owner knows which
machine ran them. **The system records `tier` and `folded_at` and does not record the environment.**
Those are different states of knowledge and the panel currently renders only the second.

#### Decision (1) — render what IS recorded, in a visually distinct block

For a fold with no captured environment, the panel additionally renders, **derived**: **`tier`** (which
machine class ran it), **`folded_at`** (already rendered), and a pointer to the pinned worker manifest
**by name**, as the place the intended environment is recorded. **This is strictly more informative
than "not captured" and asserts nothing that was not measured.**

#### Decision (2) — ⚠ inferred values NEVER enter the captured fields

`torch_version`, `transformers_version`, `device_name` and `cuda_version` render **only** from the
captured record. **An inferred value in a captured field is indistinguishable from a measured one**,
and **F-007 proves such an inference would have been wrong at least once.** The block is visually and
textually separate, and says what it is: *what we can say from the record*, not *what ran*.

#### Decision (3) — ⚠ the manifest's CONTENTS are not duplicated into the serving tier

Showing the pinned torch version would require the manifest in the serving image; **`worker/` is
excluded by DEP-001**, so the only routes are a constant typed into the UI or a copy of the file into
`data/` — **both a second source of truth that drifts the moment the pin changes.** **Ruled: name the
manifest, never render its contents.** A reader who wants the version reads the repo, where it is
authoritative.

#### Decision (4) — no backfill, no re-fold

**No inferred value is written to any record** — the block is computed at render time from data already
served. **⚠ Re-folding to populate the fields is refused, and not on cost grounds:** the six features,
F-004's fit, F-005's ablations and F-006's distribution were all computed from **these** folds; new
folds would produce new structures and features, and **the reported result would no longer correspond
to the data behind it.**

- **Deep-learning justification.** Provenance is the whole basis of the claim that *"we ran this
  ourselves"* is checkable rather than asserted (D-051, MethodNote). **A panel that mixes measured and
  inferred values destroys exactly the property it exists to provide** — and F-007 shows the inference
  would have been wrong on the one occasion it could be checked.

- **Consequences / test surface:**
  - The block renders **only** when the captured environment is absent — asserted both ways.
  - **The four captured fields still render `not captured`** when uncaptured, **never populated by the
    new block** — asserted.
  - `tier` is **derived**; **no manifest content, no version string, no device model appears in any
    component** — Constraint-A extended.
  - A captured fold renders **no** inference block. Readability delta reported.

---

### F-007 — The pinned worker environment and the measured one disagree on torch

- **Date:** 2026-07-29
- **Type:** A finding. Nothing ruled.
- **How known (D-016):** `worker/requirements.txt` pins **`torch==2.11.0+cu128`**, described in its own
  header as *"the versions MEASURED in the S-003 spike, on the RTX PRO 2000 (Blackwell sm_120)."* The
  captured environment on `protein_analyses` id=75 (folded 2026-07-25, rental tier) records
  **`torch_version: 2.8.0+cu128`**. `transformers` agrees at **5.14.1**; **torch does not.**

**The rental pod ran a different torch build than the pinned worker manifest.** Not necessarily a
defect — D-018 accepted this exact exposure in writing: *"these dependencies are NOT covered by the root
lock-file guarantee… a breaking release here reddens no gate and is discovered at fold time, on a GPU
host — that is the accepted cost of keeping CUDA out of CI."* **This is that accepted cost, observed
rather than anticipated.**

#### Finding — the manifest is not a reliable proxy for what ran

**On the single fold where both a manifest and a measurement exist, they disagree.** Any method that
reconstructs a fold's environment from the pinned manifest therefore has a **demonstrated failure rate
of one for one on the only case that can test it.** **This is D-045 paying for itself** — the entry was
written on the reasoning that *"same weights, different kernels"* is a real source of variation. It was,
and nothing else would have found it.

**⚠ The bound, stated:** the pin was measured on the **local** box; the disagreement is on the **rental**
tier. **No local fold post-dates D-045**, so the local path has no measurement and this finding says
nothing about it either way. **Unknown, not fine.**

**Amendment (2026-07-29, D-071 §1).** The local path was measured: on the fold host, in the worker
venv, `torch 2.11.0+cu128 · cuda 12.8 · NVIDIA RTX PRO 2000 Blackwell · transformers 5.14.1` — **an
exact match to the pin.** The local box agrees with `worker/requirements.txt`; the *"unknown, not
fine"* bound is closed for the local tier. **The rental disagreement (2.8.0 vs pinned 2.11.0) now
stands alone as the finding** — the pin is right where it was taken, wrong where the ephemeral pod ran
a different build.

---

### D-069 — Every surface is self-sufficient: what a reader needs to understand what they are looking at is on the surface they are looking at

- **Date:** 2026-07-29
- **Status:** Proposed → Accepted on merge.
- **Type:** A principle. **It names a pattern the project has already been following inconsistently**
  and makes it enforceable rather than remembered.
- **Relates:** D-024 (the denominator travels with the claim), D-055 + its amendment (terms decodable
  in situ, not on another page), D-062 (caveat (b) renders with the result), D-068 (a score never
  renders without its distribution context), D-050 (derived, never hardcoded).

---

**Context.** Three separate decisions have independently ruled the same thing: a number needs its
denominator beside it, a term needs its definition beside it, a result needs its caveat beside it.
**Each was ruled as a local fix. They are one rule**, and stating it once prevents the fourth
instance from being argued from scratch.

The immediate case: F-005's finding — that the ordering is carried by the model's confidence rather
than by geometry, and that this is ambiguous — is currently stated on the Scorer surface. **But a
reader forms their impression of it on the target page**, seeing the same pattern target after
target. **The explanation must be where the impression is formed.**

---

#### Decision (1) — the rule

**A reader must be able to understand what they are looking at without leaving the surface they are
on.** Every rendered number carries its denominator and its scale; every rendered claim carries its
boundary; every term of art is decodable in place.

**A surface that requires navigation to be understood is incomplete**, regardless of whether the
missing piece exists elsewhere in the app.

#### Decision (2) — ⚠ self-sufficiency is implemented as SHARED COMPONENTS, never duplicated prose

**This is the trap, and it is the one this project has been bitten by repeatedly.**

If F-005's ambiguity note is written once on Scorer and again on TargetView, **there are now two
copies of one claim, and they will drift.** That is *two paths to one quantity* — seven instances
recorded — **applied to prose instead of data**, and prose drift is harder to detect because no test
naturally compares two sentences.

**Ruled: a claim that appears on more than one surface is a component, not a string.** One source,
rendered in many places, changed in one. **A claim boundary duplicated as literal text in two
components is a defect** — the same class as a hardcoded denominator (D-050).

#### Decision (3) — self-sufficiency is LAYERED, so it does not fight readability

**The obvious objection: if everything must be on-surface, copy grows without bound and D-056's
readability ceiling breaks.** Story is already at FK 12.12 against a 12.5 ceiling.

**Resolved by layering, not by volume:**

- **Body copy carries the claim and its boundary, short.**
- **Tooltips carry the depth** — definitions, derivations, the F-005 ambiguity in full.

**Self-sufficiency means the reader never has to navigate away. It does not mean every word is in
the body.** The D-055 amendment already established the mechanism; this entry states why it is
required rather than merely preferred.

#### Decision (4) — what this promotes from deferred to required

- **⚠ The glossary copy sweep across the unscanned surfaces (11 prose-bearing, ~9 effective) is no
  longer optional.** A surface carrying undefined terms is not self-sufficient by definition.
  **Still post-freeze, but no longer discretionary** — it now has a principle behind it rather than
  a preference.
- **⚠ The `.term-def` overflow fix becomes load-bearing.** A definition that opens off the right
  edge of a narrow viewport **is not decodable in place**, which means the surface is not
  self-sufficient for that reader. **This upgrades the fix from cosmetic to principle-critical.**
- **Every surface rendering a cohort or result number must render its denominator** — D-024
  generalised beyond the coverage line.

#### Decision (5) — what this does NOT license

- **Not more claims.** Self-sufficiency is about making existing claims understandable, **not about
  saying more.** Every claim boundary in D-028, D-041 and D-062 stands unchanged.
- **Not duplicated numbers.** Numbers stay derived (D-050). A denominator rendered on two surfaces
  is computed twice from one endpoint, never typed twice.
- **Not a freeze-day sweep.** Applied **incrementally, per surface, as each is touched.** Attempting
  it everywhere at once would be exactly the scope creep the freeze exists to prevent.

---

- **Deep-learning justification.** The project's central claim is that the system is **visible about
  what it cannot do.** Visibility that requires navigation is not visibility — a reader who does not
  click does not see the bound, and forms an impression the system knows to be unsupported. **This
  entry is what makes the honesty claim operational rather than aspirational**, and it applies most
  sharply to F-005, whose finding is ambiguous in a way a casual reader will not infer unaided.

- **Consequences / test surface:**
  - **A claim rendered on two surfaces is a shared component** — asserted by absence of the
    duplicate literal in the second component.
  - **Every surface rendering a score, percentile or cohort count renders its denominator or scale**
    — asserted per surface as each is touched.
  - **Readability measured per surface after each application**, against D-056's ceiling. **If a
    surface breaches, depth moves to tooltips — the claim boundary is never the thing shortened.**
  - **Applied incrementally.** This entry does not itself change any surface; it governs the ones
    that follow, beginning with D-068.

---

### D-068 — The target record carries its scorer result, its status, and its attribution — never a bare number

- **Date:** 2026-07-29
- **Status:** Proposed → Accepted on merge.
- **Relates:** D-028 (attribution is a statement about the model, never about the target's biology),
  D-021 (held-out targets), D-024 (the denominator travels), F-004 (the result), F-005 (what carries
  it), F-006 (the scores are compressed and uncalibrated), D-062 (the scorer surface).

---

**Context.** A reader clicking a target from the ranking table lands on a page that says nothing about
the score that ranked it. **The loop does not close.** The target record already carries structure,
confidence, provenance and cancer associations; the one thing missing is the judgement the project
exists to produce.

#### Decision (1) — the panel is four-valued, and every target has one of the four

- **ranked** → score, rank, distribution context, attributions.
- **held out** → no score, and why (boundary-method incomparable, D-021).
- **below the confidence floor** → no score, and why (mean pLDDT under 50, D-041 §5).
- **not folded** → no score, and why, with the D-043 category.

**⚠ "No score" is a rendered state with a reason, never a blank or a `—`** — the same discipline as
D-043's three-valued `fold_status` and D-062's `result_status`. Most targets are not in the ranking,
so the not-ranked states are the **common case, not the edge case**.

**⚠ Precedence amendment (2026-07-29).** The resolver's order is **not_folded → held_out → below_floor
→ ranked** (+ the defensive `unranked_unexplained` fifth state). The owner's original ruling read
*"not folded → below floor → held out"*; the deployed walk's partition test caught that a folded,
held-out, below-floor target (**TMEM108**, pLDDT 41) was labelled *below_floor* on its target page
while the backend `_exclusion_reason` and the Scorer excluded-set said *held_out* — one target, two
surfaces, two reasons (the ninth *two-paths-to-one-quantity* instance). **`held_out` is
pLDDT-independent** (a whole-method target is incomparable at any confidence), so it is the primary
reason and now precedes `below_floor`, realigning the UI with what the backend already produced.
`not_folded` still leads — no fold, no measurements — so IGF2R is unaffected. Pinned by a partition
test: the four buckets sum to the cohort and the fifth state falls out at zero.

#### Decision (2) — ⚠ the score never appears without its distribution context

On the Scorer page a score sits inside a visible distribution; on a target page it has none, and a
reader seeing 0.187 alone cannot know whether that is high, low or typical. Every rendered score
carries, **derived**: its rank of 56, and its position relative to min / median / max (F-006).
Without that context a bare score is not interpretable, and rendering one would be **the first
uninterpretable number this project has shipped**.

#### Decision (3) — attribution is a statement about the model, and is framed by F-005

The six β_k · x_k contributions are already stored in `target_scores`, rendered as **which features
moved this target's score and in which direction**. Bounded per D-028: *"the model's confidence in
the membrane-proximal region contributed most to this target's rank"* is permitted; *"this target has
an accessible epitope"* is not. **⚠ F-005 must travel with the panel** — readers will see the pLDDT
features dominating target after target, and that pattern is ambiguous between structural order and
study-attention. The panel states the ambiguity **where the impression is formed**, not only on the
Scorer page.

#### Decision (4) — a labelled target shows BOTH its in-model score and its leave-one-out percentile

For the 12 Group B positives the fitted score is **not out-of-sample** — the model was fitted partly
on that target. The out-of-sample number exists: F-004's per-target LOO percentile. Both render, the
difference is stated, and the target is marked as **labelled** so no reader mistakes an in-fit score
for a prediction. This is the pre-registered statistic rendered per target, and it is **the most
defensible number on the page**.

#### Decision (5) — ⚠ MethodNote is corrected in the SAME PR

It currently reads that per-feature attribution is *"named but not yet rendered — a display gap, not a
data gap."* Rendering it here **makes that sentence false**. Shipping the panel without the correction
would re-introduce, on the same day, the exact defect class this week was spent removing.

#### Decision (6) — what the panel must NOT say

- No biological or clinical claim about the target (D-028).
- No *"this target is promising"*, and nothing that reads that way for a high-ranking unlabelled
  target — D-015's research question is about exactly those targets; the surface **poses** it, it does
  not answer it.
- No probability language (F-006).
- No implication that a high score means an ADC would work — the label is **attempted, not viable**
  (D-041).

---

- **Deep-learning justification.** The attributions are the point at which a neural network's output
  becomes an **inspectable judgement about one protein**. D-041 chose logistic regression over an
  embedding model precisely so a disagreement could be attributed to a feature rather than shrugged
  at — this panel is where that choice pays off, and it is the first surface where a reader sees
  F-005's finding **target by target** rather than as an aggregate.

- **Consequences / test surface:**
  - All four statuses render, each with a fixture, **none as a blank or `—`**.
  - A score never renders without rank and distribution context.
  - A labelled target renders both numbers and its labelled marker.
  - F-005's ambiguity note is present whenever attributions render, **asserted so it cannot be
    trimmed**.
  - Constraint-A absence for score, rank, median and percentile literals.
  - MethodNote's *"not yet rendered"* line gone, **asserted by absence**.
  - Readability delta reported.

---

### D-067 — The narrative surfaces are told through to the result, including a promise kept and a claim that outran the build

- **Date:** 2026-07-29
- **Status:** Accepted — the work shipped in **PR #94** (walk-verified live). **This entry is
  retroactive**; see Consequences for why, because the reason is itself part of the record.
- **Relates:** D-028 (the commitments this bounds), D-041 §2 (ESMFold is the deep learning; the
  scorer turns its output into a checkable judgement), D-043 (`failed` vs `not_folded`), D-050
  (derived, never hardcoded), D-056 (the readability ceiling), D-062 (the scorer surface), D-064 (the
  zero-positive defect the correction records), D-066 (the `ranked`/`rankable` vocabulary), F-004/F-005
  (the result and its reversal), D-069 (the self-sufficiency principle this foreshadows).

---

**Context.** The scorer shipped (F-004, F-005), but the two narrative surfaces still stopped before
the result: Story promised a ranking it said was "deliberately not built," and MethodNote asserted a
capability the build did not have. This entry tells both surfaces through to the result. Two Planner
corrections shaped it, and are recorded because they are the reason it reads as it does:

- **The swapped-attribution error.** The Planner reported from a screenshot that Story's
  IGF2R/FAT2/MUC16 attribution was *swapped*. It was not — `Story.jsx:25-26` derived the groups
  correctly. The real defect was a **hardcoded reason string contradicting a derived one**. A
  screenshot supported a suspicion; the source settled it. (Recorded so the next screenshot-driven
  suspicion is checked against the source before it becomes a claim.)
- **The audit found the known defect on a second surface.** Story's false claim was already known;
  the same claim sat on **MethodNote** and nobody had looked. That is why the §1.4 audit ran
  *mechanically across all prose-bearing components*, not on the surfaces a reviewer happened to open.

---

#### Decision (1) — Story's "deliberately not built" promise RESOLVES, it is not deleted

*"What is deliberately not built… we will not fake it."* The promise was **kept**: the scorer now
exists and has run, and the ranking is real at reduced scope. The paragraph resolves into a
commitment-met, not a boast, and is not silently removed — a reader who saw the promise deserves to
see it honoured.

#### Decision (2) — MethodNote's forward-looking section is FALSE and is SPLIT, not simply updated

*"What it will do — not yet, and never mocked… It waits on the scorer… It is not built."* Two claims
in one paragraph with **different truth values** now: the ranking **is** built (real scores, reduced
scope); disagreement classification is **not** (deferred, with baseline rank, delta and per-feature
attribution). Updating it wholesale would replace one false claim with another, so it is **split**
into what shipped and what is deferred-with-reason. Related, same file: the D-028 commitments opened
*"It classifies disagreement; it does not explain it"* — **present tense asserting a capability that
does not exist**, inside the section whose job is bounding claims. The commitment stands; the tense
must not assert the build.

#### Decision (3) — Story's hardcoded fail reason is DERIVED; D-043's distinction survives

`Story.jsx:58` hardcoded *"(a documented hardware ceiling)"* for the `failed` group — but IGF2R's
`tier_reason` is `whole_sequence_fold` (attempted as one sequence, ran out of GPU memory), and
"ceiling" describes `over_local_ceiling`, which is FAT2/MUC16's `not_folded` reason. **Derive it.**
D-043's distinction must survive: `failed` (attempted, did not complete) and `not_folded` (never
attempted) stay separate. *As shipped:* both groups carry a **category derived from `fold_status`**,
neither carries a hardcoded reason, and the per-target reason lives on Coverage where it is derived
and where the jargon belongs — the original defect was a *false* reason, not an *absent* one.

#### Decision (4) — `COHORT_MAX_PLDDT` is a cohort statistic typed as a constant; report before changing

`plddt.js`'s `COHORT_MAX_PLDDT = 84.23`: if only rendered, derive it (D-050); **if it also sets a
band boundary, it is a decision constant, not a statistic**, and converting it changes behaviour, so
report first. *As found:* rendered-only (the top-band caveat string; boundaries are 70/60/50/0), so
safe to derive — but **deferred** as a named Constraint-A gap rather than thread a data source into a
pure, source-free module on freeze day for a value correct today.

#### Decision (5) — the D-066 `ranked`/`rankable` vocabulary is applied across the components

D-066 fixed the vocabulary (`ranked` = the D-024 disposition over 82; `rankable` = the ranking's
membership after the pLDDT floor); this decision applies it consistently across the surfaces that
render those quantities. The ScorerView reconciliation was reworded (D-066 A2 amendment) to drop
`ranked`-as-membership; Story:50 and MethodNote:50 render *"ranked-and-folded"* (the D-024
denominator, not membership) and were assessed **correct as written** — a confirmation, not a change.

---

- **Deep-learning justification.** **MethodNote is where a reader learns that ESMFold is the deep
  learning** and that the scorer turns its output into a *checkable judgement* (D-041 §2) — an
  argument that until now lived only in the log. **Story is where the same reader learns what the
  result was and what remains unresolved.** Both were telling a story that stopped before the
  interesting part; this entry tells them through, so the honesty claim is made *on the surfaces*, not
  reserved for the record.

- **Consequences / test surface:**
  - **⚠ This entry was written AFTER its code shipped (#94), and that is itself recorded.** The orders
    file carrying the entry text (`ORDERS-Code-2026-07-29-D-067-narrative-surfaces.md`) **never
    reached the Builder** — the export channel's **fifth** loss. *"Log leads code" was violated here
    by a delivery failure, not a decision*, and the record says so rather than papering over the gap.
  - Story (beats 4–6, the correction, the resolved promise, the derived fail-reason) and MethodNote
    (the shipped/deferred split, the D-028 tense, the attribution example) shipped in #94; **UI 74/74**,
    and **readability held at FK 12.12 against the pinned 12.5 ceiling** (D-056), measured after wiring.
  - The self-sufficiency this reaches for — the explanation living where the impression forms — is
    generalised the same day by **D-069**.

---

### D-066 — `ranked` names two different quantities, and a shared component asserted a claim it cannot verify

- **Date:** 2026-07-29
- **Status:** Proposed → Accepted on merge.
- **Relates:** D-024 (the partition, and the denominator travelling with the claim), D-050 (derived,
  never hardcoded), F-002 (the cascade), F-006 (the count that exposed it).

**Context — the defect, on the deployed surface.** `CoverageLine.jsx` asserts *"The ranking … covers
these {rankedFolded}"*, which computes to **67**, **directly above a 56-row ranking table** on
`/scorer`. On `/coverage` the same 67 is correct.

**Root cause — one word, two referents:**

| Usage | Meaning | Value |
|---|---|---|
| `ranked` on `/coverage` | the **D-024 disposition** — ranked / held_out / excluded, over all 82 | **67** |
| `ranked` on `/scorer` | **membership in the actual ranking**, after the pLDDT-50 floor | **56** |

**⚠ Same class as the 67-vs-67 collision recorded in F-002** — two different quantities sharing a
word, and on that occasion sharing a *value*, which is what concealed it. **This is the fifth
instance of *two paths to one quantity, never compared*, and the first where the collision is
lexical rather than computational.**

**The tell was in the copy the whole time:** *"The ranking — once the scorer exists — covers these
67"* was written **before a ranking existed.** It was a forward-looking promise. It became a false
claim on one surface and an unverifiable one on the other the moment the scorer ran.

#### Decision (1) — `CoverageLine` states the partition and stops claiming what the ranking covers

**A coverage component cannot know what a ranking covers.** It knows the D-024 partition; the
ranking's membership is decided downstream by the pLDDT floor, which the component has no visibility
into. **The forward-looking clause is removed, not re-tensed.**

This fixes both surfaces at once: `/coverage` keeps a true partition statement, `/scorer` stops
carrying a false one.

#### Decision (2) — the scorer supplies the reconciliation beside its own table

Rendered in the right column, immediately above the table, **all three numbers derived**:

> **67** ranked · **56** rankable after the pLDDT-50 floor · **the table below shows those 56**

**⚠ Amended 2026-07-29 (freeze push).** The original copy read *"these 56 are ranked below"* — `ranked`
in the membership sense **decision 4 forbids.** Planner error: this copy was written before decision 4's
rule and never checked against it. Reworded to `rankable`; the component (`ranking-reconciliation`) and
this entry are amended **together**, because a component-only fix would leave the log teaching the wrong
thing.

**The missing step was never wrong, only absent from where it was needed** — it exists in cascade A,
in the left column, disconnected from the box making the claim. **A denominator in another column is
a denominator that does not travel with its claim** (D-024).

#### Decision (3) — ⚠ REJECTED: a prop supplying the post-floor count to the shared component

It would work and it is the smaller diff. **Rejected because it preserves the defect's shape:** the
component would continue to assert what the ranking covers, using a number handed to it, with no way
to verify the claim. **The next surface that reuses it inherits the same trap.**

#### Decision (4) — the vocabulary is fixed

- **`ranked`** — the D-024 disposition. Over 82. **Never means "in the ranking."**
- **`rankable`** — folded ∧ ranked ∧ above the pLDDT floor. The set the ranking covers. Already the
  term used in F-002 and cascade A.

**Any surface using `ranked` to mean the ranking's membership is a defect.**

- **Deep-learning justification:** none directly; this is a denominator-honesty decision. It bears
  on the model's reporting because **a ranking presented over the wrong denominator overstates its
  own coverage**, which is the failure D-024 exists to prevent.

- **Consequences / test surface:**
  - `CoverageLine` **no longer contains a ranking-coverage claim** — asserted by absence, on both
    surfaces.
  - The scorer's reconciliation line renders all three numbers **derived**, and a fixture with
    distinctive values proves none is typed.
  - **`/coverage` is unchanged in meaning** — its partition test stays green.
  - **The stale tense disappears with the clause**, so no separate tense fix is needed.

---

### F-006 — The fitted scores are compressed toward the base rate, and are not calibrated probabilities

- **Date:** 2026-07-29
- **Type:** A finding. **Nothing is ruled here.**
- **How known (D-016):** read-only SQL against `target_scores` where `ranking_run_id = 2` (the
  pre-registered run), over the live proxy on `localhost:16380` — `MIN`, `PERCENTILE_CONT(0.5)`,
  `MAX`, `COUNT(*)`.

| | |
|---|---|
| min | **0.116** |
| median | **0.220** |
| max | **0.285** |
| count | **56** |
| labelled fraction (12 / 56) | **0.214** |

---

#### Finding (1) — the median sits on the base rate, and nothing reaches 0.3

**Median 0.220 against a labelled fraction of 0.214.** The typical target is lifted almost nothing
off the prior. The whole field spans **0.116–0.285**; rank 1 is the ceiling and sits ~0.065 above
the median.

**⚠ A reader shown "rank 1 = 0.285" with no framing will read it as a middling probability**, when
it is the top of a field that never clears 0.3.

#### Finding (2) — ⚠ this is the expected signature of L2 shrinkage at n=12, not necessarily a weak ordering

**Compression of absolute scores toward the base rate is what an L2-penalized fit on twelve
positives is expected to produce.** D-041 chose L2 precisely to shrink unstable coefficients, and
shrunk coefficients yield outputs pulled toward the prior.

**The absolute spread is therefore weak evidence about the ordering, in either direction.** The
evidence about the ordering is **F-004's leave-one-out percentile distribution** — median 0.607, 8
of 12 above chance — which is computed on **positions, not values**, and is unaffected by
compression.

**Stated plainly: compressed scores do not by themselves make the ranking uninformative, and they
are not evidence that it is informative either.** The two questions are separate and only the second
was pre-registered.

#### Finding (3) — ⚠ the score is NOT a calibrated probability

A logistic model outputs a number in [0,1], **but calibration was never tested** and no calibration
claim was pre-registered. **Nothing on any surface may present 0.285 as "a 28.5% chance"**, and the
`Score` tooltip must say so explicitly.

**Recorded as a Planner correction:** an earlier draft of that tooltip read *"the model's estimated
probability that a target belongs to the labelled set."* **Withdrawn** — it implied calibration that
was never established.

---

#### Consequences

- The `Score` column tooltip carries **the scale, the observed range, the labelled fraction, and the
  non-calibration statement**, all derived from `/api/ranking`, none typed (D-050).
- **`COUNT(*) = 56` is what surfaced D-066** — the cross-check earned its place and is recorded as
  having done so.
- **No re-fit, no re-scaling, no calibration step.** Any of those would be a model change after
  seeing a result. If calibration is ever wanted it is a new entry, dated after this one.

---

### F-005 — The sensitivity analysis: the above-chance signal is carried by ESMFold's confidence, not by the geometry — and the attention explanation is not supported

- **Date:** 2026-07-29
- **Type:** A finding. **Nothing is ruled here.** The reading below follows D-065 decision 3's
  outcome table, which was fixed **before either ablation ran.**
- **⚠ This does NOT replace F-004.** D-058 decision 2 and D-065 decision 4: a sensitivity analysis
  is reported *after* the pre-registered result, presented as sensitivity, and never as the headline.
  **F-004 remains the result. This bounds it.**
- **Cites F-004; does not amend it** (D-065 decision 4).
- **How known (D-016):** two authorised runs of `scripts/fit_scorer.py --run --persist --ablate`,
  one each, after PR #91. Persisted as `ranking_run` **id=3** (`no_plddt`) and **id=4**
  (`plddt_only`), both `run_kind='sensitivity'`, `scorer_version=a927dc4532b7`. **Neither is served
  by `/api/ranking`**, which filters `valid ∧ run_kind='preregistered'` and continues to serve id=2.

---

#### The design held

**Denominators identical across all three runs** (D-065 decision 2): ranking set **56** · positives
**12** · head-to-head **8** · common reference **12**. All three: `loo_status=complete`, **12 of 12
folds converged**, `fulldata_status=converged`. **No raise in either ablation** — expected, since
fewer parameters make convergence more likely, and recorded because D-065 required a raise to be
reported as a finding had one occurred.

| Run | median | mean | ≥0.5 | Spearman | params |
|---|---|---|---|---|---|
| **FULL** (F-004, id=2) | **0.607** | 0.618 | **8/12** | −0.0483 | 7 |
| **`no_plddt`** (id=3) | **0.562** | 0.589 | **6/12** | −0.0483 | 5 |
| **`plddt_only`** (id=4) | **0.679** | 0.629 | **9/12** | **−0.2897** | 3 |

#### Finding (1) — D-065 decision 3, row 2, **first clause fires**

> *"`no_plddt` ≈ chance, `plddt_only` ≈ full-model shift → **the axis is substantially
> pLDDT-driven**."*

**`plddt_only`, on two features and three parameters, matches and slightly exceeds the full model.**
**`no_plddt`, on four features and five parameters, falls to 6 of 12 above chance — exactly even.**
**Two of the six features carry the result. The four geometry features are close to inert.**

This is consistent with predictions D-027 recorded before any data existed: **features 1 and 2 are
collinear by construction** (ECD length and length-normalised radius of gyration), and **feature 6
is the fragile one**. A geometry set that contributes little is the anticipated shape, not a surprise.

#### Finding (2) — ⚠ row 2's **second clause is NOT supported**, and this is the substantive result

D-065 decision 3's row 2 continues: *"the attention pathway is a live explanation."* **The one
measurement bearing on that pathway points the other way.** F-004 caveat (b) named a specific
mechanism: pLDDT partly reflects training-set representation → research attention → having been
attempted as an ADC. **If that were operating, `plddt_only` should align MORE closely with the
evidence score** (the project's available proxy for attention-and-precedent). **It aligns less** —
Spearman **−0.2897** vs **−0.0483** for FULL and `no_plddt`, further from zero and in the negative
direction, the opposite of what the attention mechanism predicts. **The pre-registered reading
half-fires**, and is reported as half-firing rather than forced onto a row.

**⚠ Bound on this inference.** The evidence score is a weak attention proxy — **two values, twelve
targets** (F-004; D-060 decision 8). *"Not supported"* means the one available test points away,
**not** that the pathway is excluded.

#### Finding (3) — what is now open, and it is a better question than the one it replaces

**ESMFold's own confidence about a protein predicts whether people have built an ADC against it
better than the geometry ESMFold predicts.** Two candidate explanations, both live, **neither
distinguishable by this design:** (1) **training-set representation → research attention** — F-004's
original confound, **weakened by Finding (2), not eliminated**; (2) **order versus disorder — a
genuine structural mechanism** — pLDDT tracks predicted order, disordered regions make poor antibody
epitopes, so a well-ordered ECD is a real structural argument for accessibility, and on this reading
**pLDDT is a legitimate feature, not a confound at all** (D-027's *epitope-region pLDDT* justification
borne out). **Distinguishing them requires an instrument this project does not have.** Named as the
open question. Not resolved, and not narrated as if it were.

#### Finding (4) — ⚠ `plddt_only` beating FULL is unremarkable and must not be over-read

**Three parameters against twelve positives generalises better than seven.** At this n that ordering
is expected and is **not evidence that pLDDT is superior** to the full set — only that the geometry
features are not adding enough to pay for their parameters **at this cohort size.**

#### Finding (5) — the three models disagree per target while agreeing on one coarse statistic

FULL and `no_plddt` return **identical Spearman to four decimals (−0.0483)** while producing
substantially different per-target percentiles (NECTIN4 0.848 → 0.634, JAG1 0.580 → 0.830). Against a
two-valued comparator six-and-six among twelve, **Spearman depends only on the rank-sum of the
score-5 group** and is quantised in steps of ~0.024, so two genuinely different models can agree on
that one statistic; `plddt_only`'s −0.2897 confirms it varies by run. **Agreement on a coarse
statistic computed against a degenerate comparator is not agreement between the models.**

---

#### Consequences

- **F-004 caveat (b) is now tested rather than open**, and its status changes rather than its text:
  the **specific** attention mechanism it named is **not supported** by the one available test; a
  **new, better-posed** open question replaces it (Finding 3). **F-004 is not amended** — this entry
  is the update, and the ordering of the two entries is the record.
- **⚠ The ranking rendered by `/api/ranking` is substantially a pLDDT-driven ordering.** Any surface
  describing what the score measures must not imply the geometry features are doing the work. **The
  `structural score` definition (D-055/D-062 tooltips) is read against this finding before it ships.**
- **The pre-registered result stands unchanged.** Six features, seven parameters, the reported
  distribution, both negative-outcome tests. No parameter altered after any result existed, and no
  third ablation run (D-065 decision 1).
- **The strongest available follow-up is now clear**, and it is not more parameters: an independent
  attention proxy, or an independent disorder measure, would separate Finding 3's two explanations.
  **That is a next-session arc with its own entry**, and D-041's line still governs — *the honest
  route is more labelled data, not more parameters.*

---

### D-065 — Two pre-specified ablations to test whether the structural signal is carried by pLDDT
- **Date:** 2026-07-29
- **Status:** Proposed → Accepted on merge. **Ruled before either ablation runs**, after the
  pre-registered result was reported (F-004) and rendered (D-062) — D-058 decision 2's condition.
- **Relates:** F-004 caveat (b) — the confound this addresses; D-027 (the fixed six, and its
  anticipation of feature-level ablation); D-058 decision 2 (sensitivity analyses are permitted
  *after* the pre-registered result is reported and never replace it); D-041 (the model, unchanged).

**Context — the sharpest open question in F-004.** Two of the six features are pLDDT-derived (feature
3, mean pLDDT over the folded ECD; feature 4, membrane-proximal pLDDT). **pLDDT is partly a function
of how well-represented a protein's family is in ESMFold's training data**, which tracks research
attention, which tracks having been attempted as an ADC. So F-004's modest above-chance shift could
arise from the network's confidence proxying attention rather than from structure. F-004 records this
as an **open** confound; it is **testable**, and leaving a testable confound untested when the test is
one run is not defensible. **D-027 anticipated exactly this:** *"the leave-one-out will show whether
any single feature is load-bearing or whether the set is redundant. Neither outcome invalidates the
pre-registration — both are informative."*

#### Decision (1) — exactly two ablations, named now, both reported regardless of outcome
| Set | Features | Parameters |
|---|---|---|
| **`no_plddt`** | 1 (ECD length), 2 (Rg), 5 (SASA), 6 (patch fraction) | 4 + intercept = **5** |
| **`plddt_only`** | 3 (mean pLDDT), 4 (membrane-proximal pLDDT) | 2 + intercept = **3** |

Both run, both reported, neither chosen after seeing the other. `no_plddt` asks *does the shift
survive without pLDDT?*; `plddt_only` asks *does pLDDT alone reproduce it?* — together they
triangulate. **⚠ No third ablation may be added after seeing these** — that requires its own entry,
dated after these results.

#### Decision (2) — everything else is held identical
Same 12 labels · same 56-target ranking set · same 13-point λ grid · same 5-fold stratified inner CV
· same LOO folds · same pLDDT floor of 50 · no RNG · same convergence criterion and raise. **Only the
feature columns change**, so a difference in outcome is attributable to the features and nothing else.

#### Decision (3) — ⚠ the interpretation is fixed BEFORE either run
| Outcome | Reading |
|---|---|
| **`no_plddt` shift ≈ full, `plddt_only` ≈ chance** | **Confound weakened** — signal is geometry, not confidence. Caveat (b) → tested. |
| **`no_plddt` ≈ chance, `plddt_only` ≈ full** | **Confound strengthened** — the axis is pLDDT-driven; the attention pathway is live. **Reported prominently as the finding.** |
| **Both below full** | The six are **jointly informative**; neither half carries it alone. Silent on the confound. |
| **Both ≈ full** | The set is **redundant**. Silent on the confound. |
| **Either raises** | Recorded as a raise with its status (D-063 dec 2). Fewer parameters make convergence *more* likely. |

**"≈" is deliberately not thresholded** (D-041 dec 4's precedent). The distributions are reported
side by side and read in prose against this table.

#### Decision (4) — the ablations are structurally prevented from becoming the headline
- **A named set is REQUIRED.** `--ablate` accepts only `no_plddt` or `plddt_only`; **arbitrary
  feature subsets are refused by the code** (`DegenerateLabelSet`'s sibling — a `ValueError`), so
  fishing is prevented by construction.
- Each ablation writes **its own `ranking_run`**, tagged `run_kind='sensitivity'`. **The
  pre-registered run (id=2) is `run_kind='preregistered'`** (migration `0006`, backfilled).
- **D-062's route filters on `run_kind`, not only validity** — it serves the latest valid
  **preregistered** run; a sensitivity run is never served where the pre-registered result is
  expected. A test asserts this.
- **F-004 is not amended by these results.** They land in a new finding entry (**F-005**), dated
  after the ablation runs, which cites F-004 and does not modify it.

#### Decision (5) — D-027's fixed six is NOT violated
D-027 fixed the count for **the pre-registered model** and anticipated ablation as a diagnostic. **The
pre-registered model remains six features and seven parameters, unchanged, already reported.** The
test asserting exactly six features on the pre-registered path must remain green; if it reddens, the
ablation has leaked into the pre-registered path and the PR is wrong.

- **Deep-learning justification.** F-004's result is bounded by a confound about **what the network's
  own uncertainty encodes.** pLDDT is a deep-learning output used as signal (D-041 §2 item 3), so
  whether it carries structure or training-set representation is a question *about the network*. This
  is the most directly deep-learning-relevant follow-up available, and it is one run against an
  existing pipeline.

- **Consequences / test surface:** `--ablate` refuses any set not in the named two (arbitrary subset
  raises); the six-feature assertion on the pre-registered path stays green; **5** parameters for
  `no_plddt`, **3** for `plddt_only`; `run_kind` persisted and a sensitivity run never returned where
  the pre-registered run is expected (fixture holding both kinds); the three leakage guards (D-060)
  re-assert on the ablation path; determinism holds. **Also folds in the D-063 all-folds-raise fixture**
  (the `loo_status='none'` path, handled but previously unpinned) — worth pinning before an ablation
  that fits 2 features against 12 positives, the regime where odd geometry is most plausible.
  **No run in this PR.**

---

### F-004 — The pre-registered result: the structural axis is modestly above chance, indistinguishable from the comparator, and not a proxy for it

- **Date:** 2026-07-28
- **Type:** The pre-registered result (D-041). **A finding, not a decision** — nothing is ruled here.
- **How known (D-016):** one authorised run of `scripts/fit_scorer.py --run --persist` against
  `main` after #89 (D-064's label fix). Persisted as **`ranking_run` id=2**,
  `scorer_version=91e646e4a289`, `ranking_results` id=2, 56 `target_scores`.
  **Run exactly once. No re-run, no parameter changed after the result existed.**
- **Provenance chain:** an earlier run under the D-064 defect produced `ranking_results` id=1 with
  a **zero-positive label set**. That row is **retained and marked invalid**, not overwritten
  (D-064 decision 3). `ranking_runs` id=1 is the enqueue's anchor for 80 folds and is untouched.

---

#### The inputs, all fixed before the run

Six features (D-027) · L2 logistic regression, seven parameters (D-041) · 13-point λ grid, 5-fold
stratified inner CV, no RNG (D-060) · pLDDT floor 50 (D-041 §5) · **12 curated label accessions**
(F-003) · ranking set **56** · comparator **12** · head-to-head **8** (F-002, recomputed against the
curated file).

#### Result (1) — the pre-registered object: the leave-one-out percentile distribution

**`loo_status = complete`. 12 of 12 folds converged. No non-convergent targets.**

| Target | Percentile | | Target | Percentile |
|---|---|---|---|---|
| EGFR | 0.955 | | SLC3A2 | 0.634 |
| CDCP1 | 0.902 | | JAG1 | 0.580 |
| ERBB2 | 0.866 | | CD276 | 0.562 |
| NECTIN4 | 0.848 | | CDH11 | 0.384 |
| MERTK | 0.812 | | FGFR3 | 0.384 |
| | | | UPK1B | 0.312 |
| | | | SLC39A6 | 0.170 |

**Median 0.607 · mean 0.617 · 8 of 12 above 0.5**, against a null expectation of 0.5.

**A modest upward shift.** D-041 decision 3 fixed the reported object as *the full distribution with
median and spread* and barred a single summary number as the headline. **No significance test was
pre-registered and none is computed** — at n=12 one would be underpowered, and choosing a test after
seeing the distribution is the degree of freedom pre-registration exists to remove.

#### Result (2) — D-041 decision 3's first negative outcome: **FIRES**

On the 8 held-out positives carrying an evidence score, percentiles computed within the common
reference set of 12 (D-060 decision 8):

| | structural | comparator |
|---|---|---|
| mean | **0.573** | **0.5625** |
| median | **0.625** | **0.750** |

**Not distinguishable — and the direction reverses between mean and median.** That reversal is the
cleanest possible statement of the finding: which axis looks better depends on which summary you
choose, which is what *"not distinguishable"* means at this size. D-041's own words for this case:

> *"the structural axis adds nothing measurable at this cohort size. That is the result."*

**⚠ The comparator's degeneracy was predicted and held.** The evidence percentiles came back as
**exactly two values, 0.75 and 0.25** — because the published evidence score takes only two values
(nine 4s, eight 5s across 17 targets). D-060 decision 8 recorded this **before any number existed**,
and it bounds what this comparison could ever have shown in either direction.

#### Result (3) — D-041 decision 4's second negative outcome: **DOES NOT FIRE**

**Spearman(structural, evidence) = −0.0483 over N=12.**

D-015 §3 pre-registered that a **strong** correlation with the evidence score would *also* be a null
— it would mean the features proxy attention-and-precedent rather than measuring structure.
**Near-zero says they do not.** The structural axis is measuring something largely orthogonal to the
comparator.

#### Result (4) — the two together, which is the finding

> **The structural score ranks attempted-ADC targets modestly above chance, is not distinguishable
> from an expression-and-attention comparator, and is not a proxy for it. At twelve positives, the
> axis measures something different and cannot be shown to add anything.**

That combination is more informative than either null alone: **orthogonal but unproven** is a
different result from *"the features just re-learned the comparator,"* and the second was the more
likely prior.

---

#### ⚠ Three caveats that travel with this result, always

**(a) The design is conservative and biases toward the null.** Each held-out positive is ranked
among a pool that still contains the eleven training positives the model was fit to score highly.
That pushes held-out percentiles **down**. Five targets nonetheless exceeded 0.80, so the training
positives do not uniformly dominate — but **the bias runs toward understating, not overstating.**

**(b) An open confound: pLDDT may carry attention.** Two of the six features are pLDDT-derived, and
**pLDDT is partly a function of how well-represented a protein's family is in ESMFold's training
data — which tracks research attention, which tracks having been attempted as an ADC.** That is a
path by which the score could proxy attention *through the network's own confidence* rather than
through structure. Result (3) argues against it, **but the evidence score is a weak stand-in for
attention** (two values, 17 targets). **Recorded as an open confound, not as resolved.** (Tested by
D-065.)

**(c) The top of the distribution is the famous targets.** EGFR, ERBB2 and NECTIN4 sit in the top
four. **Consistent with signal and equally consistent with (b).** It is not narrated as validation.

#### What this result does NOT claim

- **Not** that the score predicts clinical success. The label is *attempted*, not *viable* (D-041).
- **No per-target biological or clinical claim** (D-028). The delivery-agnostic framing appears once
  in the method note, never on a row.
- **Not** agreement with the paper: 12 derived labels against 22 published, with the gap recorded as
  a finding and its explanations named-but-unresolved (F-003 Finding 1).
- **Not** a significance claim. None was pre-registered; none is made.

#### Consequences

- **`fulldata_status = converged`**, 56 `target_scores` exist. **Both of D-041's negative-outcome
  tests are computable; neither is blocked** (D-064 decision 5's blocked branch does not apply).
- **The ranking table is buildable on real scores** — the first time in the project's history that
  has been true. It is still not mocked and still not required to be complete.
- **The honest route to a stronger result is more labelled data, not more parameters** (D-041).
  The roster's floor of 12 (F-003 Finding 6) is the binding constraint.
- **Deep-learning justification.** This is where the graded deliverable's claim actually resolves:
  ESMFold's structural output, turned into a judgement (D-041 §2), produces a pre-registered result
  that is falsifiable and honestly bounded — a modest, orthogonal, unproven signal, reported as
  such rather than dressed up. The rendering surface (D-062) makes that legible to a grader.

---

### D-064 — The fit driver read a schema the curated file never adopted, and ran on zero positives
- **Date:** 2026-07-28
- **Status:** Proposed → Accepted on merge.
- **Relates:** D-040 / D-029 (the curated file's schema), D-060 (the convergence raise), D-016
  (prefer the query whose answer could disqualify you), D-043 / D-027 (a degenerate state is
  reported, never imputed).
- **Invalidates:** D-063's original context paragraph and its Decision (3). See the amendment below.

**Context — what was actually run.** `data/adc_reference_mapping.csv` carries D-029/D-040's
**drug-centric** schema: `drug, application_number, antigen, uniprot_accession, source_citation,
marketing_status, development_stage`. **It has no `is_group_b` and no `symbol` column** — Group B is
*computed* by `core.adc_reference.group_b()` (in-cohort accession join × development stage).

`scripts/fit_scorer.py::read_group_b_labels` keyed on **`is_group_b` / `symbol`** — the
symbol-centric schema **proposed in `PREWORK-2026-07-27 §2` and never adopted.** It returned **zero
positives.** All 56 rankable rows entered the fit labelled negative. **The twelve curated labels
never reached the scorer.** The defect shipped in the D-061 PR and was present in **both** authorised runs.

#### Finding (1) — ⚠ a non-convergence raise does not identify its own cause
With zero positives the MLE intercept is at −∞; `p → 0`, the IRLS weights `w = p(1−p) → 0`,
`XᵀWX → 0`, and the Hessian goes singular **in the unpenalized intercept direction.** **That is the
identical failure signature as quasi-complete separation** — same iteration behaviour, same singular
direction, same message, same λ at the grid's low edge. **The raise text cannot distinguish "no
positives" from "perfect separation," and the Planner's entire interpretation followed from assuming
the second.** This is the finding, not the bug: a degenerate *input* and a degenerate *geometry* fail
identically, so the raise must never be read as evidence about the data without first measuring the input.

#### Decision (1) — one label path: `core.adc_reference.group_b()`, joined on accession
The driver reads labels through the same function the completeness check used and that
`tests/test_adc_reference.py` already exercises. **`read_group_b_labels`'s bespoke parsing is
deleted, not repaired** — a second path to the same quantity is what produced this. (Applied to the
comparator too: the driver's `read_evidence_scores` is likewise deleted for
`core.adc_reference.load_evidence_scores`, so evidence is one path as well.)

#### Decision (2) — a degenerate label set raises a DISTINCT named error, before fitting
**Zero positives, or zero negatives, raises `DegenerateLabelSet` with the counts in the message —
before any IRLS iteration.** D-060 decision 1 built the convergence raise so a meaningless *estimate*
could not be emitted silently. **This is the same principle one step earlier: a meaningless *input*
must not be allowed to produce a raise that reads like a result about the data.** The guard is cheap,
and its absence cost this project a full interpretive arc.

#### Decision (3) — the invalid artifact is MARKED, not overwritten
`ranking_results` **id=1** (zero positives, empty distribution) **stays in place.** Its
`status_detail` is set to name it invalid and why — **an owner action after merge, not part of this
PR.** The corrected run writes a **NEW `ranking_run`.** `persist_results` being idempotent per
`ranking_run` would silently erase the evidence that a false artifact existed; **this log records
corrections explicitly and never quietly fixes them (D-002), and the database is held to the same
standard.** Consequence: any surface reading `ranking_results` must filter on validity — D-062's
`/api/ranking` must never serve the invalid row.

#### Decision (4) — two test disciplines, generalised from this defect
- **(a) Any function that parses a committed artifact gets one test that loads THAT artifact**, not
  only a fixture. `build_scorer_rows` was fixture-tested with labels injected; `read_group_b_labels`
  **was never once run against `data/adc_reference_mapping.csv` in a test.**
- **(b) Where two code paths compute the same quantity, a test asserts they AGREE.** The completeness
  check and the fit driver computed the label count by different routes and disagreed **12 versus 0**,
  and nothing compared them.

#### Decision (5) — which pre-registered statistics survive a full-data non-convergence
Ruled here rather than in D-063 because it was not in the D-063 that merged — it existed only in a
Planner orders draft the main line never received. Recorded as a new decision rather than retrofitted,
so the date reflects when it was actually made.

| Statistic | Depends on | Survives a full-data raise? |
|---|---|---|
| LOO percentile distribution (D-041 dec. 3) | per-fold models | **YES** |
| Head-to-head vs comparator (D-041 dec. 3) | per-fold percentiles + evidence scores | **YES** |
| Spearman vs evidence score (D-041 dec. 4) | full-data per-target scores | **NO — blocked** |
| Ranking table (UI Plan v2 §6) | full-data per-target scores | **NO — blocked** |

A full-data raise therefore yields a **partial** pre-registered result: one of D-041's two
negative-outcome tests computable, the other not. **The blocked half is reported as blocked, with the
reason — never omitted, never null-without-explanation.** This is a statement about statistical
dependency, independent of any cause of failure, so it holds equally for the zero-positive artifact
and for any genuine non-convergence after the fix.

#### Finding (2) — ⚠ the fourth instance of one failure class in a single day
| # | Two paths to one quantity | Disagreement |
|---|---|---|
| 1 | `/api/analyses` (enqueued) vs `/api/coverage` (folded) | 80 vs 79 |
| 2 | intersection script's `folded ∧ ≥50` vs `CoverageLine`'s `ranked ∧ folded` | both 67 — **agreed by coincidence, different quantities** |
| 3 | completeness check via live API vs what the loader would write | asserted equal, verified only on challenge |
| 4 | completeness check via `group_b()` vs driver via `read_group_b_labels` | **12 vs 0** |

**Named: *two paths to one quantity, never compared.*** The discipline: **when a quantity is computed
twice, either compare them in a test or stop computing it twice.** Instance 2 is instructive — the two
paths *agreed*, on different quantities, and the agreement is what concealed the error.

#### Finding (3) — Planner error, recorded
**The Planner constructed a detailed scientific interpretation — separation geometry, λ degeneracy
under separation, a deterministic re-raise, a modal outcome of `loo_status='none'` — on a premise it
never asked to have measured: how many positives the fit actually saw.** That question is the
disqualifying one, and D-016 names the practice: *prefer the query whose answer could disqualify you.*
The Planner had, hours earlier, refused to accept a completeness count inferred from code-path
equivalence and required it be measured against prod — **then applied no such standard to the fit's own
input.** The rule was known, stated, enforced on others, and not self-applied. (A second Planner error
followed: an amendment to the merged D-063 was drafted against a six-decision structure that existed
only in an un-received orders draft, without reading the three-decision entry that shipped — "didn't
check the artifact before acting on it," the same class again. Recorded.)

#### Consequences
- **D-063 Decision (3) is VOID** (the λ-degeneracy finding — see the amendment). D-063 Decisions (1)
  and (2) and its refusals stand.
- **F-002 and F-003 are unaffected.** Both were written before the fit ran and neither derives from it.
  F-003 Finding 8's sizing arithmetic (12 positives / 7 parameters ≈ 1.7) comes from the label count,
  not the run.
- **The pre-registration is untouched.** Six features, seven parameters, the 13-point grid, both
  negative outcomes, the pLDDT floor and every refusal were fixed before any of this and none was
  informed by a bug.
- **⚠ The pre-registered result has still never run.** What twelve real positives against forty-four
  negatives in six dimensions produce is **unknown**. It may converge. **No prediction is recorded
  here, deliberately** — the last one was made without measuring its premise.
- **Deep-learning justification.** The scorer is the deep-learning deliverable's judgement layer; a
  fit run on zero positives is not a result about the model, and this entry is what stops that
  degenerate input from ever again reading as one. The guard and the one-label-path rule are what make
  the eventual pre-registered result trustworthy.

---

### AMENDMENT to D-063 (recorded 2026-07-28), mapped to what actually merged
D-063 (#88) shipped a **three-decision** entry; this amendment corrects it against that entry, not the
six-decision orders draft.

| Merged D-063 | Ruling |
|---|---|
| Context ¶ ("quasi-complete separation") | **Superseded** — the run had zero positives (D-064). |
| Decision (1) — LOO ordering defect | **Stands** — already built; correct irrespective of *why* the full-data fit failed. |
| Decision (2) — per-fold non-convergence + provenance note | **Stands.** The provenance note is **amended**: the ruling followed an **artifact**, not a real separation result — made with *less* genuine information than the note claimed (no real fold behaviour, no real full-data behaviour informed it), and **stronger for the disclosure**. |
| Decision (3) — λ-degeneracy under separation | **VOID** — built on the bug; **must not be cited.** D-060 Decision 3's rule against extending the grid stands on its original pre-registration grounds alone. |
| Refusals bullet (no intercept penalty, no grid change) | **Stands**, and now with **no observed result behind them at all**, which makes them easier to hold. |
| Everything else | Stands. |

---

### D-063 — The LOO ordering defect, the per-fold non-convergence ruling, and the λ-degeneracy finding
> **⚠ AMENDED 2026-07-28 by D-064:** the Context ¶ is **superseded** (the run had **zero positives**,
> not quasi-complete separation) and **Decision (3) (λ-degeneracy) is VOID** — built on that bug, must
> not be cited. Decisions (1)/(2) and the refusals stand; Decision (2)'s provenance note is amended
> (it followed an artifact). See the D-064 amendment above.
- **Date:** 2026-07-27
- **Status:** Proposed → Accepted on merge. **Ruled after observing the full-data fit raise at
  λ=0.001, and before observing any LOO fold outcome** — the provenance is stated precisely because
  the ruling was made with partial knowledge and that matters (D-016).
- **Discharges:** three things the scorer spec (D-041/D-060) left unfixed, surfaced when the first
  `--run` raised instead of producing a distribution.

---

- **Context — the first fit run raised, and the raise is real.** `fit_scorer.py --run --persist`,
  run once against prod (80 features loaded, 12 of 12 label accessions feature-complete, confirmed by
  querying `protein_features` directly), raised `ScorerNonConvergence: IRLS Hessian became singular
  at iteration 39 (lam=0.001)`. Two correctness facts were verified by reading the code before any
  interpretation:
  1. **The penalty enters the Hessian correctly** (`core/scorer.py:214-216`: `hess[j][j] += lam *
     penalty[j]`, `penalty = [0, 1,1,1,1,1,1]`). The six coefficient diagonals carry `+λ`; the
     **intercept is deliberately unpenalized**. Under quasi-complete separation `w = p(1−p) → 0`, so
     `XᵀWX → 0`; the six coefficient directions stay pinned at `λ > 0`, but the intercept diagonal
     `Σwᵢ + 0 → 0` and the Hessian goes singular **in that one unpenalized direction**. The MLE
     intercept is genuinely at ±∞ under separation, so the raise is **correct behaviour, not a bug**.
     (Objective is `½λ‖β‖²`, so the Hessian adds `λ`, not `2λ` — a consistent L2 convention.)
  2. **The raise came from the FULL-DATA fit, and the LOO never ran.** `run_scorer` computed the
     ranking-table full-data fit (`core/scorer.py:421-422`) **before** `leave_one_out`
     (`:425`), so the raise aborted the function before the pre-registered evaluation executed.
     **There is no percentile distribution yet — nothing ran.**

  **⚠ A phrasing error, retracted and recorded (D-016):** an earlier draft called the raise "a
  defensible negative" and reasoned that the features "separate the positives strongly." **Both are
  withdrawn.** A singular Hessian under separation is **expected from dimensionality** — twelve points
  in a six-dimensional space are almost always linearly separable from a modest complement — not from
  ADC biology, and it is near-uninformative about signal. And a non-convergence raise is **not** one
  of D-041's two pre-registered negatives (percentile-distribution-indistinguishable-from-comparator;
  strong Spearman). **It is a failure to produce the statistic — absence of evidence, not evidence of
  absence.** The honest headline is narrow: at n=12 with six features, the pre-registered procedure
  could not produce an estimate it could stand behind, and the machinery said so rather than emitting
  one.

#### Decision (1) — The LOO ordering defect is the spec's, and the fix makes the evaluation independent of the ranking fit
D-060's build order ("fit, then LOO") was transcribed faithfully into `run_scorer`, and **neither
D-041 nor D-060 said the LOO must execute independently of the full-data fit.** The coupling — a
full-data non-convergence aborting the pre-registered evaluation that does not depend on it — is a
**gap in the spec, recorded here as such, not a defect in the build.** The fix: **`leave_one_out`
runs first and independently**; the full-data fit (needed only for the ranking table and the
Spearman) runs after and its failure is non-fatal to the pre-registered distribution.

#### Decision (2) — A fold that raises is a fold that produced no percentile; the distribution is reported over the folds that converged
D-041/D-060 never specified what happens when a LOO fold fails to converge, and each fold trains on
**11 positives in the same six-dimensional space**, so folds may raise for the same reason the
full-data fit did. `leave_one_out` had **no per-fold guard**, so one fold's raise would abort all
twelve. **Ruling:**

- **A non-convergent fold is recorded as producing no percentile** — null-with-a-reason at the fold
  level (D-027/D-024 applied one layer down), never a fabricated value.
- **The percentile distribution is reported over the folds that converged**, with **the
  non-convergent count and the named held-out targets stated alongside it**, and the **denominator
  travels with the claim** (D-024): "distribution over K of 12 folds; N did not converge: [names]".
- **The alternative — all-or-nothing, one bad fold discarding eleven good ones — is worse
  epistemically** and would be chosen for the same reason the intercept temptation is (see the
  refusals).

**⚠ Provenance, stated exactly (D-016):** this ruling was made **after** the full-data raise at
λ=0.001 was observed and **before** any LOO fold outcome was observed. One cannot un-know the
full-data result; one can state precisely what was known when the rule was fixed. The rule is the
epistemically-correct one independent of the outcome, but the honest record is *when* it was set.

#### Decision (3) — The λ-selection degeneracy under separation, and why "don't extend the grid" is now also a technical rule
The inner CV selected the grid's **low edge, 0.001** — and that is **structurally guaranteed by the
separation geometry, not bad luck.** Under quasi-complete separation the least-regularized fit
predicts the inner held-out folds near-perfectly, so it wins on validation log-likelihood, every
time. **The λ-selection procedure is itself degenerate when the data separates.**

**Consequence:** extending the grid **downward** would make it strictly worse — a smaller λ wins
the CV and raises harder. So D-060's rule against extending the grid is not only a pre-registration
constraint here; **there is an independent technical reason it is correct.** This turns "we didn't
tune" from a discipline claim into a technical one, and it belongs in the write-up.

- **⚠ Two model changes stay REFUSED, and both are more tempting now than an hour ago:**
  - **Do not penalize the intercept.** It would make the Hessian invertible and the raise disappear —
    by changing the model after seeing the result. The unpenalized intercept is the standard, correct
    choice; the raise it produces is information, not a defect.
  - **Do not extend the λ grid** (in either direction). Downward is degenerate (Decision 3); any
    change is a model change after seeing a result. If a converged full-data fit is later needed for
    the ranking table, **that is a new decision in a new entry, dated after the pre-registered
    result** — never a number found tonight. (The "λ at which the full-data fit would converge" was
    explicitly not computed, for this reason.)

- **Deep-learning justification.** D-041's pre-registration is only meaningful if the procedure is
  fixed before the result and the result is reported whatever it is — including "the procedure could
  not produce the statistic on this fold." This entry makes the evaluation robust to per-fold
  non-convergence *without* changing the model, which is the only way the eventual distribution
  (however partial) is an honest read of the pre-registered procedure rather than a tuned one.

- **Consequences / test surface (written before the fix, project rule):**
  - **`leave_one_out` runs first and independently** in `run_scorer`; a full-data non-convergence is
    non-fatal to the LOO distribution (tested with a fixture where the full-data fit raises but the
    folds converge, and the distribution is still returned).
  - **Per-fold non-convergence is caught, recorded (held-out name + λ + `converged=False`), and does
    NOT abort the loop** — tested with a fixture that forces a fold to raise; the loop completes and
    the distribution covers the survivors.
  - **The denominator travels:** the report carries the converged-fold count, the non-convergent
    count, and the named non-convergent targets; `structural_percentiles` length equals the
    converged count.
  - **No model change:** a source assertion that the intercept penalty coefficient stays `0` and the
    λ grid stays the 13 pinned points — the refusals enforced by the gate, not by memory.
  - **The run then executes through tested code, once, and persists to `ranking_results`** — the
    per-fold convergence status and λ-per-fold are outputs of that run, not separate diagnostics.

---

### F-003 — The Group B curation pass: 12 labels against 22, and what the instrument got wrong

- **Date:** 2026-07-27
- **Type:** Instrument/method finding (`F-NNN`). **Not a decision** — it records what the curation
  produced and what the tooling got wrong. The classification judgements themselves are the owner's
  (D-040 decision 1).
- **How known (D-016), by tier, because the tiers are not equal evidence:**
  1. **Registry pass** — `scripts/curate_group_b.py` against ClinicalTrials.gov, 2026-07-26, all 82
     symbols under UniProt aliases. Output: `data/derived/adc_reference_mapping_REVIEW-2026-07-26.csv`.
  2. **Targeted literature + patent pass** — 2026-07-27, **20 symbols**, one query minimum each,
     sources opened and read.
  3. **Landscape survey** — 2026-07-27, **19 symbols**, checked against ADC clinical-landscape
     reviews enumerating the **>50 antigens** in the **>200-candidate** clinical pipeline.
     **A survey-level negative is weaker evidence than a target-specific one** and is recorded as
     such in the file header.
- **Produces:** `data/adc_reference_mapping.csv` — the labels D-041's fit consumes.

---

#### Finding 1 — 12 label accessions against the paper's 22; the name check passes

Measured by running `core.adc_reference` against the curated file:

```
drug rows loaded ......... 13
group_b drug rows ........ 13
group_b ACCESSIONS ....... 12     <- two ERBB2 drug rows collapse to one label
group_c rows ............. 0      (deferred with reason)
stages: approved 3, clinical 4, preclinical 6
D-040 name check ERBB2/NECTIN4/EGFR present: True
D-040 count check: 12 derived vs 22 published -> -10
```

**⚠ Drugs are not targets.** Two approved ERBB2 ADCs are two rows and **one** label. The fit set
counts accessions, not rows, and an earlier Planner figure of 15 conflated them. Corrected here.

**The −10 gap is a finding, not a discrepancy reconciled away** (D-040 decision 1 pre-registered
exactly this). Candidate explanations, **named and not resolved**:

- **The roster is incomplete by three** — see Finding 6. The count is a floor.
- **The preclinical tail is registry-invisible by construction**, which the 07-26 closeout already
  predicted from PODXL.
- **Our exclusion set may be stricter than theirs.** The paper says 22 targets were "tested as
  ADCs" and does not publish its inclusion rule; this entry's rule excludes radioimmunoconjugates,
  peptide-drug conjugates, naked antibodies and family precedent explicitly.
- **They may hold information not in the public record.**

**No criterion was loosened toward 22.** Doing so would fit the labels to the comparator and
silently pre-decide D-041's result.

#### Finding 2 — the script's `review_as_probable_group_b` routing carried a 27% false-positive rate

**4 of 15 routed positives were wrong**, each falsified by a target-specific search:

| Target | Why it failed | Class |
|---|---|---|
| **SORT1** | TH1902 (sudocetaxel zendusortide) is a **peptide-drug conjugate** | excluded modality |
| **MCOLN1** | zero hits; a lysosomal channel is the wrong compartment for an ADC | no agent |
| **SMO** | small-molecule target; hits were patent boilerplate and a saporin **research reagent** | no agent |
| **FLT1** | icrucumab (IMC-18F1) is a **naked** blocking IgG1 | no payload |

**This is not a defect in the script** — D-057 built it to *gather evidence and refuse to draw the
conclusion*, and it did. **The rate is what "probable" was worth: roughly 4 in 5.** Recorded so the
next runner sizes their review effort against a measured number rather than the word.

**The misses clustered where the biology makes an ADC implausible**, and the owner's domain read
flagged all four before any search ran.

#### Finding 3 — the script's peptide-drug-conjugate exclusion did not fire

SORT1 routed positive because TH1902 is a registry-visible SORT1-targeting conjugate and **the PDC
exclusion never triggered.**

**This is the same defect class as D-057 decision 3** — the `radioimmunoconjugate ⊃ immunoconjugate`
substring bug, which the calibration test caught *before the script ever reached a network*. The
calibration covered the radio case and **not** the peptide case. **A calibration set proves the
cases it contains and nothing else.**

**⚠ Compounding factor, observed in the primary literature:** an OSMR paper describes a **⁶⁷Cu
radioimmunoconjugate** and calls its own construct "the ADC" in the methods. **Exclusion cannot rely
on the source's terminology; the payload must be checked.**

#### Finding 4 — seven contaminant classes, each observed, none hypothetical

1. **Radioimmunoconjugate** — CDCP1's ch10D7-**⁸⁹Zr**; OSMR's ⁶⁷Cu.
2. **Family-member ADC** — NOTCH2←Notch3, EPHA4←EphA2/EphA5, CDH11←P-cadherin, TSPAN15←TSPAN8,
   ITGB5←ITGB6.
3. **Research-reagent conjugate** — FITC/HRP/PE/agarose/saporin catalogue antibodies.
4. **Patent boilerplate** — a generic ADC-embodiment paragraph present in nearly every therapeutic
   antibody patent (LRP6). **The most dangerous, because it reads as a target-specific hit.**
5. **Naked antibody** — PCDH7 (mAb7), ENTPD1 (Phase I blockers), BTN3A3 (ICT01), FLT1 (icrucumab).
6. **Excluded conjugate modality** — SORT1's peptide-drug conjugate.
7. **Lexically similar symbol** — FGFR1 returned on FLT1; SLC34A2 (NaPi2b) returned on SLC3A2.
   **Distinct from (2): not a family member, a look-alike symbol.**

#### Finding 5 — the family-adjacency pattern, and why it makes the silence credible

Four families in the cohort have real ADC programs, **every one against a sibling gene**: EphA2 and
EphA5 but not EphA4; Notch3 but not Notch2; P-cadherin and CDH6 but not CDH11; TSPAN8 but not
TSPAN15; ITGB6 but not ITGB5.

**This is the Kathad cohort's selection method showing through.** Targets were selected on
expression, not ADC precedent — so where a family holds a validated ADC antigen, the cohort often
contains the other member. **It is a structural reason the registry-invisible tail is genuinely
empty rather than merely unsearched**, and it strengthens the negatives rather than weakening them.

#### Finding 6 — ⚠ the roster is incomplete by three, and the file says so

**CXCR5, MSLN and MUC16** were routed probable-positive by the registry pass and were **never
verified** — they fell outside both the 33-row headroom set and the 12-row verification set.

**They are absent from the file because unverified, NOT because negative.** The file's header
carries an explicit carve-out to that effect, because *"absence is a negative"* would otherwise
mislabel three probable positives by omission.

**Consequence: the count of 12 is a floor, not a total.** None of the three is in the ranking set
anyway — CXCR5 is below the pLDDT floor (47.63), MSLN is `held_out`, MUC16 is unfolded — **so the
fit set is unaffected**, but D-040's count check is not final until they are curated.

#### Finding 7 — GRIN1's tooling gap is closed

Its registry pass ran on reduced aliases (a `[NMDA]` bracket-syntax query returning HTTP 400), so
its silence was weaker evidence than its neighbours'. **Closed by a targeted literature pass:** the
GRIN1 literature is entirely neurology — epilepsy variants, stroke neuroprotection, anti-NMDAR
encephalitis autoantibodies. Anti-GluN1 antibodies exist, naked, non-oncology. **No conjugate.**

**A documented tooling defect converted into a documented closed gap**, rather than left as a silent
weakness in one row.

#### Finding 8 — the day's net effect: the fit set did not grow; its composition was corrected

**12 rankable positives before curation, 12 after.** Four removed (SORT1, MCOLN1, SMO, FLT1), four
added (CDCP1, JAG1, UPK1B, CDH11).

**That is the more valuable operation.** Four false positives in a twelve-positive set is **33%
label noise**, and noise in the positive class is precisely what a seven-parameter logistic
regression cannot absorb. **Removing four wrong labels improves the fit more than adding four right
ones would have.**

**⚠ D-041's sizing clause stands and is triggered:** 12 positives against seven parameters is ~1.7
per parameter, versus the ~3 D-041 called *"the upper end of what this labelled set supports."*
**Recorded as a finding, not absorbed.**

---

#### Owner rulings recorded (D-040 decision 1 reserves these; they are transcribed, not made here)

- **A target-specific patent claiming antibodies AND conjugates COUNTS**, even without a named
  clinical agent — applied to **UPK1B** (WO2017112829A1) and **CDH11** (US12522657). **A generic
  ADC-embodiment paragraph inside an antibody patent does NOT** — LRP6.
- **SORT1 is excluded**, resolving the one row where the hand draft and the script disagreed.
  **The hand draft was right.** The disagreement was settled by evidence, not by preference, and
  the instrument defect it exposed is Finding 3.
- **Accepted risk:** citations on **CDCP1** and **JAG1** were opened and verified by the owner;
  the remaining Planner-supplied citations were **not**, and the file header names them. Recorded,
  not silent; amendable.
- **A label cannot be deferred to the reader.** An earlier instruction to "state the disagreement
  and let the user decide" was withdrawn: Group B is the fit's binary target, D-041 pre-registers
  that labels are fixed before fitting, and the loader has no undecided state. **The disagreement is
  recorded here; the label is decided.**

#### Consequences

- **`test_the_committed_scaffold_loads_empty_and_valid` is RED** and must be **rewritten, never
  deleted** — it asserted the scaffold held no roster and fired the moment one landed, which is the
  tripwire working. Replace with a pin on the curated roster: 13 drug rows, 12 label accessions,
  the three named targets present, `group_c() == []`.
- **`application_number` is blank on both ERBB2 rows**, pending openFDA reconciliation (D-029). The
  repo already has that check; run it rather than type the numbers from recall.
- **Group C is absent with reason**, so `group_c()` returns `[]`. D-027's out-of-cohort probe
  (TROP2/HER3/CLDN18.2) additionally requires those targets to be **folded**, and they were never
  enqueued. Deferred with its trigger.
- **`scripts/curate_group_b.py` carries two known gaps** — the PDC exclusion (Finding 3) and the
  bracket-syntax alias failure (Finding 7). Both are cheap fixes and neither is blocking.
- **D-041's intersection requirement is still not discharged.** The labelled ∧ folded ∧ above-floor
  intersection must be **recomputed against this file** before the fit, and that recomputation is
  the recorded one. F-002's provisional figures are superseded by it.

---

### F-002 — Pre-fit cohort measurement: the folded set, the floor cost re-measured, and the four denominators the scorer depends on

- **Date:** 2026-07-27
- **Type:** Instrument/method finding. **Not a decision.**
- **How known (D-016):** `scripts/intersection_check.py` (untracked at time of measurement), run
  2026-07-27 against the live deployment `https://pharmfoldmdk.fly.dev` — `GET /api/analyses` and
  `GET /api/coverage` — joined to `data/derived/adc_reference_mapping_REVIEW-2026-07-26.csv` and
  `data/evidence_scores.csv`. Standard library only, no database credentials.

---

#### Two Planner errors this measurement found, recorded before the numbers because they change how the numbers read

1. **`/api/analyses` is the enqueued set, not the folded set.** `core/enqueue.py` creates a
   `protein_analyses` row at **enqueue** time; the list route returns those rows. A first pass read
   its 80 rows as 80 folds. **The folded count is 79** (`/api/coverage`, the D-038 supplier built to
   be the honest denominator). **80 was never a fold count.**
2. **A failed fold was absorbed into the below-floor bucket.** The script's predicate was
   `plddt is None or plddt < FLOOR`, so IGF2R — `fold_status=failed`, no pLDDT — counted as
   below-floor. **This is the D-043 error class reproduced inside the instrument used to measure
   it:** a failed fold is not an unattempted one, and it is not a low-confidence one either.

**A third, methodological:** the uncorrected pass returned **67**, and D-050 records `CoverageLine`
correctly showing **67 = `ranked ∧ folded`** in the 79-fold era. Two different quantities, identical
value. The collision prompted the check that found a missing `disposition` filter. **A number that
matches one you already trust is the most dangerous kind of wrong.**

#### The partition, which reconciles exactly

```
82  = 67 ranked + 13 held_out + 2 excluded          (/api/coverage)
79 folded     = 67 ranked∧folded + 12 held_out∧folded
 1 failed     = IGF2R  (held_out, rental, whole_sequence_fold)
 2 not_folded = MUC16, FAT2  (excluded, over_local_ceiling)
```

#### Finding 1 — every `ranked` target is folded: 67 of 67

The three gaps sit in `held_out` and `excluded` — partitions that were never entering a ranking.

**⚠ The claim "the fold arc is complete" is NOT supported and was withdrawn before it was spoken.**
The Planner drafted it from `82 − 80 = 2`; the endpoint returned three non-folded targets and the
Builder refused the sentence. **The supported claim is narrower and stronger**, and it is the one
that goes to the demo.

#### Finding 2 — the floor cost, re-measured on the right denominator

D-041 §5 recorded **~24% below pLDDT 50, measured on 42 folds**, never re-measured since.

**IGF2R's `mean_plddt` is null** (measured 2026-07-27), so the failed fold is reported separately
rather than absorbed:

> **12 of 79 = 15.2% below the pLDDT 50 floor, plus 1 failed fold, reported separately.**
> **This supersedes D-041 §5's ~24%.**

**The floor is cheaper than D-041 feared.** Recorded with the same rigour a movement against the
project would get.

#### Finding 3 — the four denominators the scorer depends on

| Quantity | Value | Status |
|---|---|---|
| **Ranking denominator** — folded ∧ `ranked` ∧ pLDDT ≥ 50 | **56** | final |
| **Comparator denominator** (D-059) — evidence score ∧ ranking set | **12** | final |
| Provisional fit set — probable positives ∧ ranking set | 12 | **superseded by F-003** |
| Provisional head-to-head — fit set ∩ comparator | 8 | **superseded by F-003** |

#### Finding 4 — the comparator's covered set is positive-enriched, and this is pre-registered

**8 of 12** scored-and-rankable targets were probable positives (**67%**) against **12 of 56**
across the ranking set (**21%**). Expected — the paper's high-evidence targets are the ones people
built ADCs against — but **every comparator statistic is computed on a small, non-random,
positive-enriched subsample.**

**Recorded before the fit**, so a correlation arriving later reads as anticipated rather than
explained away. D-041 decision 4 already warns that *"a high correlation arrives looking like
validation and is not."*

#### Finding 5 — three positives fall outside the ranking set, for three different reasons

| Target | pLDDT | Mechanism |
|---|---|---|
| **CXCR5** | 47.63 | **below floor** — folded, confidence under 50 |
| **MSLN** | 75.04 | **`held_out`** — whole-method, boundary-method incomparable (D-021 §1a). **A method exclusion, not a quality one.** |
| **MUC16** | — | **not folded** — `over_local_ceiling`, 14,451 aa |

**Three mechanisms, three named targets, none silent.** MSLN is the one worth saying aloud: the
cohort's most-attempted ADC antigen after HER2, folded well, excluded because our boundary method
cannot produce a comparable feature 4 for it.

**⚠ A real question raised and deliberately not resolved:** mesothelin is GPI-anchored, so "whole
sequence" is close to "ECD" and the incomparability argument may not bite for this target.
**Resolving it under deadline, for the one target that would add a valuable positive, would be
fitting the method to the desired outcome.** The principled version — *whole-method targets with no
cytoplasmic domain may be method-comparable* — needs its own entry and its own evidence. **Deferred
with its trigger (D-054 manner), not dismissed.**

#### Consequences

- **Every 42-fold-era statistic is stale**, as is *"79 of 82 with 3 remaining"* and D-041 §5's ~24%.
  Re-derive, never re-hardcode at today's value (D-050).
- **`/api/analyses` must not be used as a fold count anywhere.** `/api/coverage` is the D-038
  supplier for that question.
- **⚠ This measurement does NOT discharge D-041's requirement.** The labelled ∧ folded intersection
  must be **recomputed against `data/adc_reference_mapping.csv`** before the fit. See F-003.

---

### D-061 — Where per-target scores and the pre-registered result live: migration 0004, two additive tables
- **Date:** 2026-07-27
- **Status:** Proposed → Accepted on merge. **Owner ruling**, folded into the label PR as migration
  `0004` (two additive tables, no `ALTER`).
- **Discharges — and this is a correction against the Planner (D-016):** D-058 decision 3 said
  *"scores hang off `ranking_runs`, which already carries `scorer_version`."* `ranking_runs` is a
  **run-level** table with no per-target rows, and the ruling never said where a per-target score
  actually goes. **That is a gap in the ruling, not in the build** — the D-060 driver was right to
  report scores and defer persistence rather than invent a home. Recorded as the Planner's gap.

---

- **Context — an unpersisted fit produces no durable artifact, and that is a delivery risk.** The
  scorer (D-041/D-060) computes a per-target score, its six `β_k·x_k` attributions, and a rank, plus
  a **run-level** result that D-041 fixed as a *distribution, not a scalar* (the LOO percentiles),
  a Spearman, and a set of denominators. None of these has a column anywhere. If the ranking-table
  PR does not land, the fit result must still be **queryable in the database** — persistence is the
  insurance on the last PR, so it lands now rather than with the route (a deliberate departure from
  D-058 decision 4's "with the route" framing, on delivery grounds, ruled by the owner).

#### Decision (1) — `target_scores`: one row per ranked target, per run
`ranking_run_id` → `ranking_runs`, `analysis_id` → `protein_analyses`, `score` (Float, the predicted
probability, D-060 dec 7), `attributions` (JSON — the six `β_k·x_k`, D-041 dec 1, in `FEATURE_NAMES`
order), `rank` (Integer, descending; average-rank ties are a display concern, the stored rank is the
ordinal position). Only ranking-set targets get a row; excluded targets are carried on the run
result with their reason, never given a fabricated score.

#### Decision (2) — `ranking_results`: one row per run, the pre-registered object's home
`ranking_run_id` → `ranking_runs`, and the D-041/D-060 result: `structural_percentiles` (JSON — the
**LOO distribution**, D-041 dec 3's headline), `headto_structural_percentiles` /
`headto_evidence_percentiles` (JSON — the common-reference-set head-to-head, D-060 dec 8), `spearman`
+ `spearman_n`, the denominators (`n_ranking_set`, `n_fit_positives`, `headto_reference_n`,
`plddt_floor`), `lambda_per_fold` (JSON) + `lambda_at_grid_edge`, `excluded` (JSON — `[symbol,
reason]`, D-060 §3.5), and `scorer_version` + `feature_version`. **D-041's headline is a
distribution; without this table it has no home** — a scalar column would silently discard exactly
the object the pre-registration is about.

#### Decision (3) — Additive only, verified by query
Migration `0004` creates the two tables and touches nothing else — no `ALTER`, no backfill (the
lowest-risk class, as `0003` was). **Verified by querying `information_schema.tables`, not by
alembic's exit code** (`docs/HAZARD-search-path-seams.md`); the `postgres` CI job runs the chain.
One prod `alembic upgrade head` then covers `0003` and `0004` together. Both are plain ORM models
(no pgvector), so they build under SQLite `create_all` too.

- **Deep-learning justification.** D-041's pre-registered negative outcomes ARE the deliverable's
  scientific content, and a result that exists only in a process's stdout is not a result anyone can
  audit on Wednesday. This entry gives the distribution, the Spearman, and every denominator a
  durable, queryable home — which is what makes the pre-registration checkable after the fit runs.

- **Consequences / test surface:** migration `0004` proven by `information_schema` query; both ORM
  models build under SQLite; the driver's persistence writes one `target_scores` row per ranked
  target and one `ranking_results` row per run, round-tripped in a test; the stored `rank` is
  descending by score; excluded targets never receive a `target_scores` row. **The fit itself is
  still not run here** — persistence is exercised on the fixture cohort; the first real fit is the
  owner-authorised run (D-060).

---

### D-060 — The scorer's remaining free parameters, fixed before the fit
- **Date:** 2026-07-27
- **Status:** Proposed → Accepted on merge. **Ruled before any fitting code exists and before the
  labels are curated** (D-015 §3's pre-registration discipline).
- **Discharges:** the operational choices D-041 delegated. D-041 fixed the architecture, the loss,
  the regularizer, the evaluation statistic and both negative outcomes. **It did not fix the
  optimizer, the λ grid, the inner-CV shape, the percentile's reference set, or tie handling** —
  and the reported result is sensitive to all five. Left open, they get chosen after seeing the
  leave-one-out distribution, which is what pre-registration exists to prevent.

---

- **Context — what F-002 changed.** D-041 was written when the ranking set and the folded set were
  not yet distinguished, and when the labelled∧folded intersection was unknown. F-002 measured both:
  the ranking set is **56** (`folded ∧ ranked ∧ pLDDT ≥ 50`), the provisional fit set is **12**, and
  the head-to-head denominator is **8**. Two of the decisions below exist because those numbers are
  now known.

#### Decision (1) — Optimizer: Newton–Raphson (IRLS) on the L2-penalized log-likelihood, pure Python
The penalized objective is strictly convex, so Newton converges; a step-halving guard handles the
early iterations. **Convergence criterion: maximum absolute coefficient change < 1e-8, or 100
iterations.** ⚠ **Non-convergence raises. It never returns a silent estimate.** A quietly
unconverged fit is a result that looks like a result.

#### Decision (2) — No RNG anywhere in the scorer
Fold assignment is deterministic: targets sorted by symbol, assigned round-robin within stratum.
**This is stronger than D-041's "deterministic given a fixed seed"** and deliberately so — a
seed-dependent result can move silently when a seed changes for an unrelated reason. **Determinism
here is structural, and a test asserts no `random` import.**

#### Decision (3) — The λ grid is fixed: 13 log-spaced points from 1e-3 to 1e3
Pinned by a test. **Not widened, shifted, or re-centred after any fit.** If the selected λ lands at
a grid edge, that is a **finding to report** — it means the grid was wrong — and it is reported, not
silently fixed by extending the grid.

#### Decision (4) — Inner CV: 5-fold, stratified on the label, on the LOO training remainder only
If the remainder holds fewer than 5 positives, fall back to leave-one-positive-out inner CV and
**record which was used in the run's provenance.** At 12 positives the remainder is 11, so 5-fold
holds — but the fallback is specified now rather than improvised if curation moves the count.

#### Decision (5) — The percentile's reference set is the ranking set (56), not "the folded cohort"
D-041 said *"rank percentile among the folded cohort"* when the two were not distinguished.
**Ranking claims are made on `ranked ∧ folded ∧ pLDDT ≥ 50` (D-041 §5, D-021, F-002)**, so that is
the reference set. Recorded as a clarification of D-041, not a change to it.

#### Decision (6) — Ties take average rank
Stated because it is load-bearing — see (8).

#### Decision (7) — The score is the fitted model's predicted probability, ranked descending

#### Decision (8) — ⚠ The head-to-head is computed on a common reference set, and the comparator is two-valued
Measured 2026-07-27 from `data/evidence_scores.csv`: the evidence score takes **exactly two
values across all 17 targets** — nine 4s and eight 5s — and **six 4s and six 5s** among the 12 that
fall in the ranking set. **The comparator is not a ranking. It is a two-tier grouping.**

Two consequences, both fixed here:

- **Both percentiles in the head-to-head are computed within the same reference set** — the 12
  targets carrying a structural score *and* an evidence score — over the 8 held-out positives in
  that set. A structural percentile computed among 56 and an evidence percentile computed among 12
  are not comparable quantities, and comparing them would be a bug that reads as a result.
  **The primary structural distribution (reported as the headline) is separately computed on the
  full ranking set of 56. Two statistics, both reported, never conflated.**
- **⚠ The comparator's percentile distribution is degenerate by construction.** With two values and
  average-rank ties, every held-out positive receives one of two percentiles. **D-041's first
  negative outcome — "not distinguishable from the comparator" — must be read against a comparator
  that can only sort targets into two bins over twelve targets.** That bound is recorded **before
  the result exists**, so it reads as a property of the source rather than an excuse for an
  outcome. **The pre-registered comparison is unchanged; only its interpretation is bounded.**

- **Deep-learning justification.** Every parameter above, left unfixed, is one that would otherwise
  be chosen after seeing the leave-one-out distribution. D-041's two pre-registered negative
  outcomes are falsifiable only if nothing in the procedure moves once a result exists. **This
  entry is the difference between a pre-registration and the appearance of one.** The scorer
  converts ESMFold's structural output into a judgement that can be checked and can be wrong (D-041
  §2) — its smallness (seven parameters, implementable from scratch in stdlib) is what makes that
  judgement defensible at 12 positives.

- **Consequences / test surface:** each of (1)–(8) pinned by a test; non-convergence raises; no
  `random` import (source assertion, in D-027's feature-count manner); `scorer_version` alongside
  `feature_version`. The label (Group B) and the comparator (evidence score) stay different
  quantities — a fixture that scrambles the evidence scores must produce byte-identical coefficients
  (§3.1); standardization and λ selection use the training fold only (§3.2/§3.3); perfect separation
  is expected and L2 keeps coefficients finite (§3.4); below-floor/held_out targets are reported
  separately with reasons, never dropped (§3.5); every statistic carries its denominator (§3.6).
  **This PR ships a tested scorer and driver; it does NOT run the fit** — the first fit is an
  owner-authorised run against curated labels that do not exist yet.

---

### D-058 — The extractor's open parameters, and where features are computed and stored
- **Date:** 2026-07-27
- **Status:** Proposed → Accepted on merge. **Ruled before any extraction code exists** (D-015 §3's
  pre-registration discipline, applied to the two parameters D-027 named and did not fix).
- **Discharges:** the gap D-027 left open in feature 6, and the topology question D-027's purity
  contract deliberately did not answer.

---

- **Context — two things are unfixed, and the fit is sensitive to both.**

  **(a) Feature 6's parameters.** D-027 fixed the feature — *largest contiguous accessible surface
  patch, as a fraction of total SASA* — and flagged it in the same entry as **the fragile one**:

  > *"The largest-contiguous-accessible-patch fraction depends on a SASA threshold and a
  > contiguity definition; it is the feature most sensitive to those choices, and the
  > leave-one-out is where that sensitivity should surface."*

  It named the sensitivity and fixed neither value. **Until they are fixed, D-027's
  pre-registration does not bind on feature 6** — a threshold chosen after seeing a ranking is
  precisely the degree of freedom the entry exists to close, and it is the cheapest one in the
  project to move without anyone noticing.

  **(b) Where extraction runs and where its output lives.** D-027 fixed the extractor as *"pure
  given `(structure.pdb, plddt, manifest_row)` — no network, no GPU, no database"*, which is a
  contract on the **function** and says nothing about the **program that calls it** or the
  artefact it produces. That gap is a D-047-class trap in a new place: resolve the wrong thing at
  the wrong time and the failure is latent. Specifically — **a scientific-computing dependency
  reaching the serving path reddens `test_image_contents.py`** (DEP-001), and a feature computed
  at request time makes every page load depend on a numerical routine.

- **Provenance of the all-atom premise (D-016).** `worker/runner.py:278–290` writes the PDB from
  `model.infer_pdb()` (falling back to `model.output_to_pdb()`), which is ESMFold's **all-atom**
  output path. **This is inferred from the library's contract, not measured on a stored
  artefact.** Features 5 and 6 as specified require side-chain atoms; if the persisted structures
  turn out to be backbone- or CA-only, both features change shape. **The probe below runs before
  any extraction code is written**, and its result is recorded here as an amendment either way.

---

#### Decision (1) — SASA is Shrake–Rupley, implemented in-repo, with conventional parameters fixed now

- **Probe radius 1.4 Å** (water). **Sphere sampling: 92 points per atom** — Shrake & Rupley's
  published value, golden-spiral distributed. **Atomic radii: a fixed table committed alongside
  the code**, not read from a library at runtime.
- **Implemented in `core/features.py` with ZERO third-party imports**, not taken from `freesasa` /
  `biotite` / `MDAnalysis`, and **not** written against numpy.

  **⚠ The dependency constraint is measured, not assumed (D-016).** Verified 2026-07-27: `numpy`
  and `scipy` appear in **neither** `requirements.lock` **nor** `requirements-dev.lock`, and
  `.github/workflows/gate.yml` installs `requirements-dev.lock --require-hashes` and nothing else.
  **`worker/` is not an alternative home** — `worker/requirements.txt` states *"THE GATE NEVER
  INSTALLS THIS"*, so code placed there is code the gate cannot test, and D-027 requires the
  feature-count test to run in the gate (*"this is the test that makes this entry real"*).

  **Argued, because "hand-roll it" is normally the wrong instinct.** The usual reason to prefer a
  library — it is tested and you are not — is answered here by D-027's own test requirement: the
  fixture must be *"verified against a computed expectation rather than against whatever the code
  happened to emit first."* **We are obliged to verify the output against an independent
  expectation regardless of who wrote the algorithm**, so the library buys less than it usually
  does. Against that, admitting numpy means regenerating a hash-pinned lock (D-013) two days before
  delivery. **The deciding factor is the anchor:** an isolated atom's SASA is exactly
  `4π(r + r_probe)²`, so the implementation can be checked against a closed-form value rather than
  against another implementation's opinion.

  **The pure-Python constraint has a measured trigger, not an assumption of adequacy.** The kernel
  is timed on a ~5,000-atom synthetic cloud **before the rest of the extractor is built on it**.
  **Above 60 seconds, the ruling reverses:** numpy enters `requirements-dev.txt` with a regenerated
  hash lock, recorded as a reversal. Extraction is a one-shot offline job and can afford to be
  slow; it cannot afford to be unrunnable, and the difference is cheap to measure in advance.

- **⚠ Rejected: choosing the library *because* the extractor runs offline and the dependency would
  never reach the image.** True of `scripts/`, and not a reason. **The extractor itself ships** —
  `core/` is in the runtime tier (ARCHITECTURE §5) — so a module-scope third-party import there is
  a latent landmine the image-contents test does not catch: the module is present and its
  dependency is not.

#### Decision (2) — Feature 6's two parameters, fixed by convention rather than by our data

- **A residue is `accessible` if its relative SASA ≥ 0.25** — its computed SASA over its
  theoretical maximum for that residue type. **0.25 is the standard exposed/buried cutoff in the
  structural-biology literature**, not a value this project selected.
- **Two accessible residues are contiguous if their CA atoms are within 8 Å.** A patch is a
  connected component under that relation. **8 Å is the conventional CA–CA residue-contact
  distance**, likewise inherited rather than chosen.
- **Feature 6 = (summed SASA of the largest connected component) / (total SASA over the folded
  span).**

  **Why convention-anchored is the load-bearing property, not the specific numbers.** This is the
  same move D-039 made for the pLDDT bands: *anchor to an external convention, then check it
  against our cohort* — never *choose against our cohort and present it as a convention*. Neither
  0.25 nor 8 Å is uniquely correct. What makes them defensible is that **they were fixed before a
  ranking existed, and their source is outside this project**, so no reviewer needs to take our
  word that they were not tuned.

- **⚠ Explicitly rejected, recorded so it cannot arrive later as a refinement:** selecting either
  parameter by which value improves the fit, the LOO distribution, or agreement with the
  comparator. **That is feature engineering against the evaluation**, and it would invalidate
  D-027's pre-registration exactly as adding a seventh feature would. If a sensitivity analysis
  is ever wanted, it is run *after* the pre-registered fit is reported, presented as a
  sensitivity analysis, and does not replace the headline result.

- **Pre-registered expectation (D-027 already said this; restated because this entry is where it
  becomes checkable):** feature 6 is the feature most likely to prove unstable under leave-one-out.
  **That is an anticipated finding, not a defect** — and it is only readable as anticipated
  because this entry is dated before the number exists.

#### Decision (3) — Extraction is an offline client of the public read API; features and scores persist in Postgres, on the tables the schema already anticipated

**⚠ Owner ruling, 2026-07-27, reversing the Planner's draft.** The draft deferred the table and
shipped a CSV snapshot, on risk grounds. **The owner ruled the table.** Two findings made after the
draft show the owner's call was better supported than the draft assumed, and they are recorded here
rather than folded in silently:

- **`ranking_runs` already exists** (`db/models.py`, migration `0002`), carrying
  `target_list_version` and `scorer_version`, with the committed rationale *"created here so the
  schema anticipates ranking without retrofitting a live migration chain."* **D-019's foresight
  was aimed at exactly this moment**, and the CSV path would have walked around it.
- **The migration is `0003` and is purely additive** — one new table, no `ALTER` on a populated
  table, no backfill, no data movement. **The lowest-risk migration class**, and the `postgres` CI
  job already exercises the chain end to end.

**The Planner's risk objection was calibrated to a migration that does not exist here.** Recorded
as a correction against the Planner (D-016): the objection was reasoned from a category
(*"a migration two days out"*) rather than from the artefact (*which migration, against what*).

- **The extractor function stays pure** (D-027, unchanged).
- **The driver — `scripts/extract_features.py` — is a client of the public read API**, consuming
  `GET /api/analyses`, `/api/analyses/{id}/structure`, and `/api/analyses/{id}/plddt`, joined to
  the local D-023 manifest for the boundary and ECD length. **No database credentials, no Volume
  access, no `worker/` import.**

  **This mirrors the shape the project already trusts:** the worker is a client of the `/jobs`
  API rather than a database peer (D-030/D-031), and the same reasoning applies — *the seam that
  makes the component testable is the seam that keeps its dependencies out of the serving tier.*
  It also means feature extraction runs from any laptop with network access, against the same
  public surface a grader can open.

- **Persistence is migration `0003`, one additive table, `protein_features`:**

  | Column | Meaning |
  |---|---|
  | `id` | PK |
  | `analysis_id` → `protein_analyses.id` | the fold these features were read from |
  | `ranking_run_id` → `ranking_runs.id` | the run they belong to (the table already exists) |
  | six named `Float` columns, **nullable** | D-027's features |
  | `null_reasons` (JSON) | **why** any feature is null — D-027's *null-with-a-reason*, **never an imputed mean** |
  | `mean_plddt`, `below_plddt_floor` | the D-041 §5 floor, stored not recomputed |
  | `feature_version` | D-027's source-hash pin |
  | `computed_at` | when |

  **Scores hang off `ranking_runs`, which already carries `scorer_version`.** Per target: the
  structural score, the six attribution contributions (`β_k · x_k`, D-041 decision 1), and the rank.

- **The loader writes to Postgres directly, exactly as `core/enqueue.py` does.** `enqueue` is the
  precedent and it is an exact one: a local CLI that builds an engine from `DATABASE_URL` via
  `db.dburl.normalize_db_url` and writes `ranking_runs` + `protein_analyses` rows. **A one-shot
  loader is the same shape as a one-shot enqueue**, so no new credential posture and no new seam
  is invented — the serving tier still never computes a feature, and the extractor function is
  still pure.

- **⚠ The ranking is still a snapshot, and the surface still must say so.** Moving the storage into
  Postgres does not make the score a live computation — it is the output of a named script over a
  named fold set at a named time. **The ranking surface renders the `ranking_run`'s
  `scorer_version` and `created_at` and its fold-set size, derived (D-050), never typed.** A
  snapshot presented as live is the same class of error as a hardcoded cohort count.

- **⚠ The migration's known hazard, named because this project has the scar.**
  `docs/HAZARD-search-path-seams.md` records `alembic upgrade head` **silently rolling back** —
  a `search_path SET` running before `context.begin_transaction()`, so SQLAlchemy 2.0 auto-opened
  a transaction Alembic did not own. **`0003` must be verified by querying for the table after the
  upgrade, not by reading the upgrade's exit code.** A zero exit status is exactly what that
  failure looked like.

#### Decision (4) — The ranking supplier is a new route, and it will redden the architecture contract test

`GET /api/ranking` serves the snapshot. **Adding it turns D-051's architecture contract test red
until `ui/src/system-model.json` is updated in the same PR.**

**Named in advance so it is not debugged as a surprise**, and because it is the third independent
instance of the mechanism firing (D-053's `/api/associations` was the first, unstaged). **This one
is staged, which makes it weaker evidence than D-053's and it should be described that way** — but
it is also the cheapest possible live demonstration of the claim, and it costs one line.

---

- **Deep-learning justification.** Every one of D-027's six features is computed from ESMFold's
  output; this entry is what makes two of them reproducible rather than merely specified. Feature
  6 in particular is the one whose value could have been quietly steered toward a nicer result,
  and fixing its parameters against external convention — before a fit exists — is what makes
  D-041's pre-registered negative outcomes falsifiable. **A pre-registration with a free parameter
  inside it is not a pre-registration.**

- **Consequences / test surface (written before the extractor, project rule):**
  - **All-atom is asserted by a test, not confirmed by a one-time probe.** Owner-confirmed
    2026-07-27 that stored structures are all-atom; the fixture test asserts distinct side-chain
    atom names on a **real stored structure**, so the premise is captured permanently rather than
    checked once and forgotten. **If it ever fails, features 5 and 6 need an amendment** (a coarse
    per-residue sphere model, recorded as an approximation, never presented as atomic SASA).
  - **Migration `0003` is verified by querying for the table**, not by alembic's exit code
    (`docs/HAZARD-search-path-seams.md`). Exercised in the `postgres` CI job.
  - **`null_reasons` is populated whenever a feature column is null** — asserted, so a silent
    null cannot pass as a computed one.
  - **The SASA anchor:** an isolated atom returns `4π(r + r_probe)²` within sampling tolerance;
    two atoms separated beyond `2(r + r_probe)` return exactly twice that. **A closed-form check,
    not a self-consistency check.**
  - **The two parameters are pinned by a test** — 0.25 and 8 Å asserted as named constants, so
    changing either reddens the gate rather than passing silently. Same discipline as D-027's
    feature-count test: *the test is what makes the entry real.*
  - **Feature count is exactly six** (D-027, restated because this entry is where the extractor
    that must satisfy it gets built).
  - **Determinism** — identical inputs yield byte-identical features across runs.
  - **Null-with-reason, never imputed** — a malformed structure produces a null and a reason
    string, and no fixture anywhere substitutes a mean.
  - **`feature_version` changes when feature code changes**, pinned over the extractor's source
    hash (D-027).
  - **Snapshot provenance test** — a ranking response carries its `ranking_run`'s
    `scorer_version` and `created_at`, so a surface cannot render a ranking without its
    provenance.
  - **`test_image_contents.py` still passes** — no SASA-adjacent dependency, no `scripts/` in the
    runtime stage. **The feature code lives in `core/` and ships**, but nothing in the serving
    path calls it.

---

### D-059 — The ranking surface's comparator coverage: what a row without a published evidence score renders
- **Date:** 2026-07-27
- **Status:** Proposed → Accepted on merge.
- **Discharges:** the requirement D-040 decision 2 imposed and left to the ranking view —
  *"the set on which a disagreement can be computed at all is smaller still and **must be computed
  before the ranking view is designed**."* This is that entry, written before the view.

---

- **Context — the comparator covers 17 of 82, and the ranking table's design assumes otherwise.**
  UI Plan v2 §3.1 specifies each row as *"target, baseline rank, structural rank, delta,
  disagreement class rendered visually distinct, and feature attribution."* **Three of those six
  are undefined without a baseline**, and D-040 decision 2 established that a baseline exists for
  **17 targets only** — the eight score-5 and nine score-4 targets named in the article text. The
  remaining 65 carry `score_not_published_in_text`. Verified 2026-07-27: `data/evidence_scores.csv`
  holds 17 data rows.

  Intersected with folded targets and then with D-041 §5's pLDDT floor at 50, **the set carrying
  both a structural score and a comparator is smaller still, and is not yet computed.**

  **This is not a defect in the comparator; it is a property of the source.** D-040 already ruled
  out the two ways of widening it by estimation, and this entry restates the ruling because
  **deadline pressure is exactly when reading a number off a radar plot starts to feel
  reasonable.**

---

#### Decision (1) — The primary axis is the structural score, and it is defined for every ranked row

The table ranks `ranked ∧ folded ∧ above-floor` targets by structural score. **Every row in that
set has a structural rank and a feature attribution.** The comparator is a second axis over a
subset, not a prerequisite for appearing.

#### Decision (2) — Comparator columns populate only where a published score exists; the rest render the reason, not a blank

- `baseline rank`, `delta`, and `disagreement class` populate **only** for targets carrying a
  published evidence score.
- Every other row renders **`no comparator published`** — the D-040 reason
  `score_not_published_in_text`, surfaced.
- **Not blank, not `—`, not omitted, and never imputed.** A blank cell reads as *zero* or as
  *missing data*; the honest statement is that **the paper did not publish this number**, which is
  a fact about the source rather than a hole in ours. Same discipline as D-024's three-valued
  `fold_status`: *attempted-and-failed is not never-attempted*, and *unpublished is not
  disagreement-free*.

#### Decision (3) — The disagreement denominator travels with the claim, and is derived

The surface states the count on which disagreement is computed — `N of 82` — **derived from the
artefacts at render time, never hardcoded** (D-050). If `N` is small, the surface says so in the
same breath as the comparison, per D-041 decision 3's warning that *a baseline comparison over a
handful of targets is weak evidence and must be labelled as such rather than presented as a
head-to-head.*

**No row is assigned a disagreement class it cannot support**, and no aggregate disagreement claim
is made over a denominator the reader cannot see.

#### Decision (4) — Two ways of widening coverage, rejected again and specifically rejected today

- **Reading the scores off Fig 4A/4B.** Already ruled out in D-040 (*"figure extraction is
  estimation presented as measurement"*). Restated here.
- **Recomputing the scores from the five published criteria.** D-040 ruled this makes it *our*
  score, not theirs, needing its own entry and its own defence. **Rejected again, and rejected
  specifically as a today action:** building a comparator under deadline, then comparing our
  ranking against it, is how a comparator quietly becomes a fabrication. **The remaining honest
  path is the one D-040 named — ask the corresponding author** — and it is not a today path.

---

- **Deep-learning justification.** D-041 decision 3's first pre-registered negative outcome is a
  comparison of two percentile distributions on the held-out positives, and decision 4's second is
  a Spearman correlation — **both computed on exactly the intersection this entry rules on.** If
  the denominator is unstated, neither negative result is interpretable, and a pre-registered null
  that cannot be read is not a null. **This entry is what makes D-041's evaluation reportable.**

- **Consequences / test surface:**
  - **Compute the intersection before the view is built** and record it, whatever it is. **A
    materially small number is a finding to report, not a reason to widen the comparator.**
  - **Tested:** a target without a published score renders the reason string, not an empty cell;
    the disagreement denominator on the surface equals the computed intersection (a fixture with
    a deliberately distinctive count, per the false-green discipline); no disagreement class is
    emitted for a row lacking a baseline; the denominator is absent from the source as a literal
    (the Constraint-A absence pattern from D-051/D-053).
  - **Blocks nothing upstream** — the fit, the LOO, and the Spearman are all computable before
    this view exists. **This entry governs presentation, and is written now only because D-040
    required it before the design, not before the fit.**

---

### D-057 — A curation script that gathers evidence and refuses to draw the conclusion

- **Date:** 2026-07-26
- **Status:** Proposed → Accepted on merge.
- **Relates:** D-040 (Group B's definition, and the reservation of the judgement to the owner),
  D-016 (a claim names how it is known), D-024/D-027 (null with a reason), D-053 (curated file in
  `data/`, no live retrieval in the product).
- **Blocks nothing. Unblocks:** the labelling pass that D-041's fit waits on.

**Context.** Group B needs 82 rows and a first pass produced 16, with 66 unassessed. The bottleneck
is search recall across 82 targets under many aliases — mechanical work, done badly by hand and well
by a query. The judgement that follows is not mechanical and is not automated here.

**Decision 1 — the script gathers evidence; it never labels.** `is_group_b` is emitted **blank on
every row**; there is no code path that writes a label, and a test asserts no input produces one
(D-040 decision 1 reserves the classification to the owner).

**Decision 2 — a registry miss is `needs_literature_check`, never `false`.** ClinicalTrials.gov holds
no preclinical work. PODXL is a Group B positive on the strength of a preclinical ADC in no registry.
If silence became `false`, the script would manufacture confident wrong labels — worse than a blank,
which announces its own ignorance.

**Decision 3 — exclusion markers take precedence over ADC phrasing, found by a test not by design.**
`radioimmunoconjugate` contains the substring `immunoconjugate`; on first run IGF2R — a radiolabelled
antibody D-040 excludes — routed as a probable positive. The calibration test caught it before any
network call. The fix is a precedence rule that would look arbitrary without this note.

**Decision 4 — offline tooling, not a runtime dependency.** The product retrieves nothing live
(D-053). The script runs once, emits a review sheet, and the artefact of record stays a committed,
cited file. `requests` is imported *deferred* so it never enters CI or the serving image.

- **Deep-learning justification:** none, stated plainly. This is label-acquisition tooling for a
  model that is pre-registered and unfit; its value is that it does **not** contaminate the labels —
  D-041's last free parameter — with an automated judgement.
- **Consequences:** `scripts/curate_group_b.py`, `tests/test_curate_group_b.py`, and a dated review
  sheet under `data/derived/`. No dependency reaches the serving image.

---

### D-056 — The plain-language pass, and a readability tripwire calibrated to what we actually wrote

- **Date:** 2026-07-26
- **Status:** Proposed → Accepted on merge.
- **Relates:** D-055 (the register rule this executes), D-049 (pin to observed values, not
  aspirations), D-051 Constraint A (which this pass is the single most likely thing to break).
- **Depends on:** D-055 merged — the copy references terms that must already exist.

**Context.** D-055 defines the terms. The surrounding sentences are still written at postgraduate
level in places — e.g. *"where a disagreement is explicable by known homology (convergent folds,
divergent sequences within a family)"* — which no glossary entry rescues, because the problem is the
sentence, not the word.

**Decision 1 — rewrite the domain copy; leave the ML copy alone.** D-055's register rule, executed
across every component that renders prose. Meaning is preserved exactly; only the reading level
moves. **Nothing that is currently precise becomes vague.** A shorter sentence that says less is a
failure of this pass, not a success of it.

**Decision 2 — a readability tripwire, ceiling set after the fact.** Flesch–Kincaid grade level is
computed over rendered text, with numerals stripped and glossary terms and gene symbols exempted
from the syllable count. **The ceiling is calibrated from the measured value once the rewrite is
done, plus a small margin** (the D-049 pattern: pin to what is observably true).

**⚠ What this test is and is not.** Flesch–Kincaid counts syllables and sentence lengths. **It does
not measure comprehension**, it is trivially gameable by chopping sentences, and it penalises terms
that cannot be avoided. It is a **regression tripwire** — it catches copy drifting back toward
density — and it is **not evidence that the writing is clear.** That claim is made by a human
reading it; a green test does not stand in for one.

- **Deep-learning justification:** none directly, and stated rather than manufactured. This pass
  makes the deep-learning claims *readable by the reader who has to assess them*.
- **Consequences:** copy edits across `Story`, `MethodNote`, `AdcContext`, `CoverageView`,
  `TargetView`, `CoverageLine`, `Provenance`, `PlddtSpread`, `CancerAssociations`; one new test.

---

### D-055 — A glossary, and a contract test that reddens when an undefined term reaches the screen

- **Date:** 2026-07-26
- **Status:** Proposed → Accepted on merge.
- **Relates:** D-051 (the narrative surfaces this makes legible), D-016 (a claim names how it is
  known — a term nobody can decode is a claim nobody can check), D-024 (the honest denominator,
  unreadable if the reader cannot parse its units), D-053 decision 5 (which kind of number may be a
  literal).
- **Amends:** nothing. Additive.

**Context.** The UI puts **pLDDT, PAE, ESMFold, ECD, ADC, quasi H-score, TCGA, IHC** and `int8` in
front of a reader (an **ML expert, oncology novice**), mostly undefined. pLDDT carries the entire
honesty argument, and nothing on screen says what it is. **A reader who cannot decode the term cannot
evaluate the honesty built on it.**

**Decision 1 — two registers, by domain.** Biology/oncology/chemistry → plain ~8th-grade language;
machine learning/statistics → peer level, unchanged. pLDDT sits on the boundary and gets both (the
precise form and the plain one). **⚠ This register split is a human judgement — no test enforces it**
(stated so the green contract test is not over-read, D-016).

**Decision 2 — the glossary is `ui/src/glossary.js`, definitions are literals.** Each entry carries
`expansion` and `plain`. Applying D-053 decision 5 (*would it change if our data changed?*) — a
definition would not, so it is correctly a literal and needs no route.

**Decision 3 — the contract test reddens when an undefined term reaches the screen.** A test renders
the prose surfaces through the D-046 harness and fails if a term the reader must decode is rendered
without a glossary entry. **Implementation note (orders §5.1 fallback, invoked):** an open scan for
acronym-shaped tokens proved impractical — rendered copy also carries decision references
(`D-045`, `DEP-001`), UniProt accessions (`Q96NY8`), cancer names and units, none of which are
glossary terms and none cleanly exemptible without weakening the assertion. So the contract is a
**curated `MUST_DEFINE` watchlist**, not an open scan. The gene-symbol exemption is **derived from
`data/cohort_82.txt`**, not typed. `<Term>` exposes each definition by **keyboard focus and tap**,
not hover alone.

- **Deep-learning justification:** pLDDT is the network's own uncertainty, and this project's whole
  argument is that it renders that uncertainty honestly. **An honest rendering of a term the reader
  cannot decode is not honest in any sense that matters.** This is the last step of making the
  model's output legible to the person judging it.
- **Consequences:** `ui/src/glossary.js`, `Term.jsx`, `Glossary.jsx` (a block on `/method`), inline
  `<Term>` on the narrative surfaces, and `Term.test.jsx` / `Glossary.test.jsx` /
  `glossary.contract.test.jsx`. No new dependency, no route, no supplier change.

---

### D-054 — The evidence baseline is deferred, on purpose, with a trigger

- **Date:** 2026-07-26
- **Status:** Accepted — **a deferral, not an omission.**
- **Relates:** D-040 (the evidence scores and their 17-of-82 curation gap), D-024 (the honest
  denominator), D-028 (non-goals as commitments), UI Plan v2 §8 (the ranking centrepiece).

**Context.** `data/evidence_scores.csv` holds 17 curated, cited rows — 9 scoring 4, 8 scoring 5 —
and is reachable from no route and no component. It is the published comparator half of the research
question, and it is invisible in the deployed product.

**Decision.** It stays invisible **this session**, and this entry exists so that fact is a recorded
choice rather than an oversight discovered later.

- **It is not blocked by the scorer.** A supplier and one view would ship it. It is blocked by
  judgement: it is one half of the centrepiece, and this project has declined to build the
  centrepiece in halves every session since UI Plan v2 §8. Doing it days before delivery would break
  that discipline at the exact moment the discipline is worth most.
- **The misreading risk is live.** Seventeen rows scoring only 4 and 5 read as *"these are the good
  ones."* The other 65 are **unpublished, not low.** Rendering the 17 without that denominator
  hard-wired into the surface would teach a reader something false — and the reader in question is a
  grader.

**Trigger — the next session, or the scorer fit, whichever comes first.** When built, it carries
D-024's denominator treatment: 17 of 82, the 65 rendered null-with-reason, and it is labelled the
**published comparator**, never "our ranking."

- **Deep-learning justification:** none, and that is the point. This surface would show a
  *published expression-derived* baseline. Its whole value is as the thing the structure-derived
  ranking is measured *against* — which means it is worth little until there is a ranking to
  compare, and actively misleading if shown alone.
- **Consequences:** none in code. A named debt with a trigger, so it cannot quietly vanish.

---

### D-053 — Per-target cancer associations, derived from the cohort's own source, including where the derivation disagrees

- **Date:** 2026-07-26
- **Status:** Proposed → Accepted on merge.
- **Relates:** D-040 (curated-and-cited discipline; *a different number is a finding, not a
  discrepancy to reconcile away*), D-016 (a claim names how it is known), D-050 (derived, not
  hardcoded), D-038 (a new supplier is its own route), D-024 (the honest denominator), D-052 (the
  boundary between what we produced and what we illustrate).
- **Amends:** the 2026-07-25 pre-work §4, which scoped this as a hand-curated literature roster
  requiring an owner curation pass. **Superseded:** a better source was found — the cohort's own
  paper — making the roster derivable rather than assembled. Recording the reversal explicitly.

**Context.** ESMFold says how confidently it folded a chain. It says nothing about why the chain
matters. Without that, a reader cannot weigh a pLDDT of 30.68 against one of 84.23 — both are just
numbers about proteins they have no reason to care about.

**Decision 1 — derive from the source paper, do not assemble from literature.** The Kathad
supplementary S3 File publishes a complete 82 × 20 grid of per-target, per-tumour-type **quasi
H-scores** (0–300; %low×1 + %med×2 + %high×3, from HPA IHC data). Applying **the paper's own stated
150 cutoff** yields **337 target–tumour pairs covering all 82 targets**. This is strictly better
provenance than a hand-assembled literature roster: one source, one citation, uniform coverage, no
selection by us, and reproducible from a file anyone can download.

**Decision 2 — the claim is an EXPRESSION claim, and the surface says so.** A row means *"highly
expressed in this tumour type, by the paper's measure."* It is **not** causal, **not** a claim the
target drives the disease, and **not** a clinical indication. This bound is rendered, not assumed.

**Decision 3 — record the disagreement; do not reconcile it away.** The disqualifying check was
run before the artefact was trusted: the paper states OSMR overexpressed in **10** indications (this
derivation: **10**, reproduced exactly); **290** target–indication combinations (this derivation:
**337**, not reproduced); **16** targets above cutoff in >7 tumour types (this derivation: **17**,
not reproduced). A strict `>150` cutoff gives 285 pairs — nearer the headline — but breaks OSMR
(7, not 10), so it is the *wrong* reading despite the closer number. Dropping any single tumour type
yields 296–334, never 290. S7 File has 213 rows, also not 290. **Conclusion: 290 is a different
quantity, produced by a filtering step the published files do not expose.** Therefore this is *our*
derivation from the paper's published scores — agreeing with one named claim, disagreeing with two —
and it is labelled that way wherever it appears. It is never rendered as "the paper's 290
combinations."

**Decision 4 — every association renders, ranked.** No top-N truncation (owner ruling). BTN3A3 has
16. Legibility is bought by **descending quasi H-score with the score shown**, which makes the list
ordered evidence rather than an unordered dump — so the ordering is a **tested contract**, not
styling.

**Decision 5 — a citation may be a literal; a statistic may not.** This sharpens D-050. The paper's
`290` and `16` are facts about a published document: static, and correct as literals. Our `337`,
`82`, and every per-target count are statistics over a file that can change: they derive from
`/api/associations`. **The test of which kind a number is: would it change if our data changed?**

- **Deep-learning justification:** the network's output is a confidence surface over a structure;
  its significance to a reader is entirely external to it. This supplies that significance from a
  cited source while stating precisely what the citation does and does not support — keeping the
  domain claim and the model claim separable, the same boundary D-052 defends in pictures.
- **Consequences:** `data/cancer_associations.csv` (337 rows + provenance header);
  `core/cancer_associations.py`; `GET /api/associations`; a `CancerAssociations` component in
  `TargetView`; tests at both tiers. `data/` is already in the image (`Dockerfile:38`) — no
  packaging change, no new dependency. **Migration trigger:** moves to a DB table **only** if it
  becomes a scorer feature or a query filter. **Correction folded in:** `data/cohort_82.txt` cited
  its source as sheet `Target_expression_in_normal`; S3's only sheet is `Target_expression_in_tumor`
  (the normal-tissue grid is S2). The 82 symbols are identical either way, so the cohort of record is
  unaffected — a provenance-label error, fixed and noted.

---

### D-052 — The ADC mechanism schematic is an illustration, and is structurally prevented from reading as model output

- **Date:** 2026-07-26
- **Status:** Proposed → Accepted on merge.
- **Relates:** D-051 (the narrative surfaces this ships alongside), D-016 (a claim names how it is
  known — a drawing that names nothing is the weakest claim on the site), D-024/D-028 (don't let a
  reader collapse two distinct classes), D-045/D-048 (the provenance layer whose whole purpose is
  making "this came from ESMFold, at a named revision" checkable), D-037 (hand-rolled SVG).
- **Amends:** `AdcContext` only. Nothing structural.

**Context.** UI Plan v2 §7.1 keeps the antibody/linker/payload metaphor because it is *mechanism,
not decoration*, and `AdcContext` already carries it in prose. A drawn schematic makes it land
faster for a non-specialist reader, which is the demo audience.

**The risk this entry exists to close.** A reader arrives at `/about` having just seen a 3Dmol
structure coloured per-residue by pLDDT. A drawn antibody on the next screen is, to that reader,
plausibly another thing the system produced. **It is not.** Letting that inference stand is a false
claim about the neural network's output — the precise error the entire provenance layer was built
to prevent, arriving through the one door provenance does not guard, because a picture has no
provenance panel.

**Decision — two parts, and the second is the load-bearing one.**

1. The schematic carries a visible label: *"Schematic illustration — not a structure produced by
   this system."* plus a link to a real folded target.
2. **It is structurally incapable of being a model output.** The component imports nothing from
   `api.js`, takes no analysis props, and is a pure function of nothing. A test asserts the
   mechanism, not just the words: with `api.js` mocked, **no export is invoked**. Labels can be
   edited away by a later hand; an import that does not exist cannot quietly start lying.

- **Deep-learning justification:** negative and protective. Everything else in this UI works to make
  the DL claim *checkable*; this works to keep it *bounded*, at the one surface where a reader is
  most likely to over-attribute. A sharp boundary around what the network produced is part of the
  claim, not a caveat on it.
- **Consequences:** `AdcContext.jsx` gains an `AdcSchematic.jsx` child and its test. No route, no
  supplier, no new dependency. Hand-rolled SVG (D-037) — no chart or diagram library enters the
  bundle for this.

---

### D-051 — The narrative surfaces: a Story that derives its numbers, and an Architecture diagram pinned to the route table

- **Date:** 2026-07-26
- **Status:** Proposed → Accepted on merge.
- **Relates:** D-050 (derived-not-hardcoded cohort statistics — the trap this entry must not
  re-arm), D-016 (every claim names how it is known, applied here to the project's account of
  itself), D-024/D-028 (the honest denominator; non-goals as commitments), D-004/DEP-001 (the
  topology the diagram must not mis-draw), D-046 (the harness), D-037 (hand-rolled SVG).
- **Amends:** `UI_Plan_v2.md` §3's *"four surfaces"* — see decision 0. `ARCHITECTURE.md` in the
  same PR.

**Context.** The UI is demo-ready but has no entry point for a reader meeting the project cold. The
Prime Directive is graded on whether deep learning does load-bearing work *and whether that is
defensible* — and a grader who cannot locate the neural network quickly cannot grade it as
load-bearing. Two surfaces are missing: the narrative that says what was done, and the picture that
says where inference runs.

**Decision 0 — five surfaces, by absorption, and the divergence from UI Plan v2 is ruled, not
drifted into.** UI Plan v2 §3 rules *"Four surfaces. No sidebar with six destinations."* That
constraint is honoured rather than overridden: Story takes `/`, Targets moves to `/targets`, and the
two new elements are **absorbed** into the pages that already motivate them — the architecture
diagram into `/method` (*how the system works* is the method), the mechanism schematic into
`/about`. Five destinations. Recording this because a surface that arrives *because the UI had space
for it* is exactly what D-028 §9 forbids; this one arrives because the audience changed.

**Decision 1 — the Story surface, and every number on it is derived.** The cold open: the research
question, that **we ran ESMFold ourselves** rather than retrieving structures, what came out, what
did not fold and why, and what is deliberately not built (the scorer and the ranking — D-028's
non-goals as commitments). **No cohort statistic is written as a literal.** D-050 was decided nine
days before delivery precisely because prose quoting a fold count rots silently; a Story saying "we
folded 79 targets" re-arms that trap on the most-read screen on the site. Counts, ranges and
fractions derive from `/api/analyses` and `/api/coverage`, or the claim is made qualitatively with
no number at all ("no target reaches the high-confidence range" needs no maximum to be true).

**Decision 2 — the architecture diagram is generated from a committed system model, and a test
asserts that model against the running app.** A hand-drawn system picture is a claim with no
provenance (D-016): it is wrong one PR after any route change and nothing reddens. So the diagram
is not drawn — it is **rendered from `ui/src/system-model.json`**, and
`tests/test_architecture_contract.py` walks the real FastAPI route table and asserts **set equality
in both directions**: every live route appears in the model, every modelled route is live. Adding a
route without updating the picture fails the gate. Precedent for a Python test reading a
non-Python artefact as its subject: `tests/test_image_contents.py` reads the `Dockerfile`.

The diagram's load-bearing content is the **topology**: inference runs on the GPU tier, *not* on Fly
(D-004); the serving image contains no `worker/` and no CUDA (DEP-001). That is the most-asked and
most-easily-mis-drawn fact about this system.

- **Deep-learning justification:** the neural network is the graded deliverable, and both surfaces
  exist to make it *locatable and bounded* — where the model ran, what it produced, what it did not,
  and where the system's claims stop. That is D-016 and D-024 applied to the project's account of
  itself rather than to a number inside it. Neither surface asserts anything about the model that
  the API cannot be asked to confirm live.
- **Consequences:**
  - `App.jsx`: `/` → `Story`, `/targets` → `TargetList`; nav is five items. `/target/:id` deep
    links unchanged.
  - New: `Story.jsx`, `ArchitectureDiagram.jsx`, `ui/src/system-model.json`, and their tests.
  - `MethodNote.jsx` renders `ArchitectureDiagram`.
  - New functional test `tests/test_architecture_contract.py`.
  - `ARCHITECTURE.md` updated in the same PR — we are shipping a surface that *draws* the
    architecture, so the prose and the picture must be brought into agreement together.
  - Follow-ups folded in (§5 of the orders): the `AdcContext` `77.26` literal and the `CoverageLine`
    zero-case wording, both named in the 2026-07-25 closeout §6.

---

### D-050 — Cohort statistics in UI copy must be derived, not hardcoded; the 42-fold-era prose is stale and self-contradicting

- **Date:** 2026-07-25
- **Status:** Accepted.
- **Relates:** D-049 (whose named-query figures the visible copy now contradicts), D-024 (the
  honest-denominator discipline this violates in the worst way — three denominators on screen at
  once), D-016 (a claim names how it is known — a hardcoded "42" names nothing and rots silently),
  D-038/D-034 (`/api/coverage` is the authoritative denominator source these components should
  read), D-048 (the renderers that compute — `CoverageLine`, `TargetList` — are already correct;
  this brings the prose components up to that standard).
- **Amends:** the copy in `AdcContext.jsx` and `MethodNote.jsx`; comment hygiene in
  `CoverageLine.jsx` / `TargetList.jsx`.

**The finding (provenance — the live pre-demo walk, 2026-07-25).** The deployed app shows three
different "how many did you fold" numbers on grader-visible surfaces: the `/api/coverage`-derived
`CoverageLine` correctly shows **67** ranked∧folded; `MethodNote` hardcodes *"40 ranked-and-folded
of 82"*; `AdcContext` hardcodes *"42 folded targets … 45% fall below 60 … 34.78 to 81.40."* The
cohort grew 42→79 folds (D-045 rental tier, D-049 recompute); every hardcoded 42-fold-era statistic
in the copy layer is now stale, and two are grader-visible and self-contradicting against the
live-computed values on the same screens — `AdcContext`'s "45% below 60" directly contradicts
D-049's 29.1%, and its "81.40" max contradicts the live 84.23 caveat D-049 shipped.

**Root cause — the lesson `CoverageLine` already embodies, not yet applied to prose.** Components
that compute from `/api/coverage` or `rows.length` (`CoverageLine` → 67, `TargetList` → 79) tracked
the growth automatically and are correct. Components with hardcoded prose (`AdcContext`,
`MethodNote`) rotted. This is not a wrong-number bug; it is an **architecture bug** — a cohort
statistic written as a literal in copy is a claim with no provenance (D-016) that silently falsifies
as the cohort grows. Re-hardcoding today's numbers resets the same trap; the next fold breaks it
again.

**Ruling — two parts, in priority order:**

1. **Structural fix (the durable one): derive cohort statistics from the authoritative source.**
   `AdcContext` and `MethodNote` take their folded-count, ranked∧folded, pLDDT range, and
   below-divider fraction from the data they already have access to — `/api/coverage` (the
   authoritative denominator, D-038) and/or the `/api/analyses` rows — the same way `CoverageLine`
   and `TargetList` already do. **A cohort statistic rendered to a grader is a computed value or it
   is a bug.** Where a component genuinely cannot reach the data at render time, the fallback is not
   a literal — it's omitting the specific number and stating the qualitative claim (e.g. "no target
   reaches the high-confidence range" needs no max literal to be true).

2. **Correctness floor (only if the structural fix can't fully land before the demo):** re-state to
   the D-049 named-query figures, explicitly dated — the minimum acceptable state is that no two
   visible surfaces disagree (`AdcContext` → 79 folded, 30.68–84.23, 29.1% below 60; `MethodNote` →
   67 ranked∧folded of 82). This is a stopgap, not the fix — it re-arms the same rot — so it is only
   acceptable as a time-boxed fallback, and the structural fix stays queued behind it.

- **Deep-learning justification:** the coverage story is the honesty layer that makes this a
  defensible DL deliverable rather than a wrapper (D-024). Three contradicting fold-counts on the
  deployed app don't just look sloppy — they hand a grader direct evidence that the system's
  self-reported scope can't be trusted, the exact credibility the provenance/coverage work was built
  to establish. Deriving the numbers is what makes "we folded 79, ranked 67, and here's why the rest
  didn't" a claim the app can stand behind live.
- **Consequences:**
  - `ui/src/components/AdcContext.jsx` (~52–53): folded count, pLDDT range, below-60 fraction →
    **derived** from `/api/analyses`.
  - `ui/src/components/MethodNote.jsx` (~20): "40 ranked-and-folded of 82" → **derived** from
    `/api/coverage`.
  - **Comment hygiene (D-016, not visible but rots the same way):** `CoverageLine.jsx:3` and
    `TargetList.jsx:8` ("nothing above 81.4") corrected — the same lesson as the D-049 header-comment
    fix (source must not grep to a stale number even in a comment).
  - The `CoverageLine` cosmetic (*"…not the 67 ranked (0 of them awaiting rental fold)"* — reads
    awkwardly now that all ranked targets are folded, `rankedUnfolded=0`) is a **separate, minor**
    copy-clarity issue. **Noted, not bundled** — mixing it into a correctness fix muddies the diff.
    Its own small follow-up.
  - **Tests-first, on the D-046 harness.** `AdcContext` and `MethodNote` are currently in the
    untested-components debt (D-046 §5); this fix pulls them out of it — the derived-number behaviour
    gets component tests (a fixture coverage/analyses payload → asserts the rendered numbers derive
    from the payload, so a future cohort change cannot silently break the copy). Structural fix plus
    a dent in the known debt, in one move.

---

### D-049 — pLDDT bands re-justified on the 79-fold cohort; the cohort-max caveat corrected (81.4 → 84.23)

- **Date:** 2026-07-25
- **Status:** Accepted.
- **Relates:** D-039 (the bands and the original 42-fold justification whose *numbers* this
  supersedes), D-016 (a claim names how it is known — this entry exists because the naming
  caught a stale one), D-024/D-028 (the caveat keeps a self-report legible as a self-report),
  D-048 (the band-contract pin, `plddt.bands.test.js`, whose 81.4 assertion this deliberately
  reddens-then-greens), D-045 (the two-tier cohort whose upward mass shift moved the distribution).
- **Amends:** D-039's stated fractions and `COHORT_MAX_PLDDT`. **Does not move a boundary.**

**Named query (provenance chain).** `GET https://pharmfoldmdk.fly.dev/api/analyses` (public read,
D-034), fetched **2026-07-25** → `200`, 18,502 bytes, **80 analyses** (82 cohort − 2 named
exclusions, D-022). **79 carry a `mean_plddt`**; the one null is IGF2R, the documented A6000
ceiling (correctly unfolded, D-047 context). The denominator is **79 folded targets** — the whole
current cohort, not the historical 42. min 30.68 · median 70.91 · max 84.23.

**Named counts — the shape moved, materially:**

| boundary | 42-fold (D-039) | 79-fold (current) |
|---|---|---|
| `< 50` | 24% | **15.2%** (12/79) |
| `< 60` | 45% | **29.1%** (23/79) |
| `< 70` | 57% | **44.3%** (35/79) |
| cohort max | 81.4 | **84.23** |

Every below-fraction fell 9–16 points as the cohort nearly doubled (42→79) and its mass shifted
up — the rental tier's fp16/unchunked folds scoring higher than the historical local set.

**Ruling — two consequences, ruled separately:**

1. **Keep 50/60/70; correct the justification, don't move the divider.** 50 and 70 are
   AlphaFold/ESMFold conventions and stand on their own. The 60 "trust divider" was justified in
   D-039 by the cohort's own mass — *"45% of folds fall below it."* That number is now **29.1%**.
   The divider still splits real mass and remains a defensible "how far to trust this" line, so the
   boundary does not move — but the stated justification is now false and must be corrected to the
   **15.2 / 29.1 / 44.3** fractions over the named query above. This is a *re-justification on the
   real cohort*, not a re-cut. A boundary whose justifying number no longer holds is a claim the log
   can no longer stand behind; correcting the number is what keeps 60 honest. The median at 70.91
   straddling the 70 line is noted — half the cohort now reaches the convention's reliable-backbone
   threshold, up from the 42-fold picture — but it argues for nothing to move; it's a fact about
   where the cohort sits, recorded so a later reader sees it.

2. **`COHORT_MAX_PLDDT` 81.4 → 84.23 is a real, visible bug, and it is the load-bearing fix.**
   `plddt.js` hard-codes 81.4, and the top-band caveat renders *"cohort max 81.4 — no target reaches
   the high-confidence range."* Three folds now exceed 81.4; the true max is **84.23**. The
   *conclusion* still holds — nothing reaches ≥90, there is still no high-confidence tier — but the
   *number* is wrong and would render next to an 84.23 fold, which is precisely the class of visible
   falsehood the confidence element exists to prevent (a reader seeing "max 81.4" beside a target
   that scores 84.23 catches the system lying about its own ceiling). The caveat text is corrected to
   84.23 while keeping the "no high-confidence tier" conclusion, which remains true.

- **Deep-learning justification:** pLDDT is the network's own confidence output; the bands make it
  legible as a self-report (D-039). A justification citing a fraction that no longer holds, and a
  caveat citing a max three folds now exceed, both degrade that legibility into stale assertion.
  Re-grounding both on the live cohort is what keeps the model's self-report honestly rendered — the
  same reason D-039 existed, applied to the cohort D-039 didn't yet have.
- **Consequences:**
  - `ui/src/plddt.js`: `COHORT_MAX_PLDDT` 81.4 → 84.23; the top-band caveat string updated to the
    new max (conclusion unchanged).
  - `ui/src/plddt.bands.test.js`: the contract pin asserting 81.4 flips to 84.23 — **red-then-green
    is the point** (the pin was doing its job by breaking; a change to a ruled constant must be a
    visible, failing-then-passing test, D-048's whole rationale for pinning it).
  - **No boundary constant changes** — `BANDS` mins stay `[70, 60, 50, 0]`. `bandFor` behavior is
    unchanged; only the max constant and the caveat prose move.
  - This entry **supersedes D-039's numbers, not its scheme.** D-039 stays in the log as the origin;
    D-049 is where the fractions and the max are now true-as-of the named query.
  - **The 42-fold vs 79-fold denominator shift is itself the finding:** the honest cohort is the one
    you can name today, not the one a prior entry was written against. The fractions are true as of
    the 2026-07-25 fetch of the deployed API; if more folds land (IGF2R on a bigger card, the
    domain-folded giants), the denominator moves again — so the entry names the query and the date
    precisely enough that a later reader knows exactly which cohort these numbers describe.

---

### D-048 — UI-depth §3: the two-population provenance panel, tier legibility, per-residue spread, and the band re-pin

- **Date:** 2026-07-25
- **Status:** Proposed → Accepted on merge.
- **Relates:** D-046 (the test harness this builds on, and the two-population render rule it
  implements — §3), D-045 (the two populations), D-039 (the bands this re-pins), D-043 (failed
  vs. not-folded, already shipped — the coverage half of UI-depth §2.1), D-024/D-028 (don't
  collapse distinct classes; a boolean is not a reason), D-016 (name the artefact behind a claim),
  D-037 (hand-rolled SVG over a chart lib in the weaker-guarantee dep world).
- **Amends:** nothing structural. Completes the UI layer for the demo; closes UI-depth §3.1–§3.4.

This lands the four UI-depth §3 components the harness (D-046) was built to make testable, all
tests-first on `vitest`/`@testing-library/react`, all asserting on rendered output as a reader
encounters it. **26 UI tests across 4 files, green; the `bandFor` smoke test is deleted** (owner
ruling, prework §3) — its boundary coverage re-homed into `plddt.bands.test.js` first, so nothing
was lost.

**§3.1 — the two-population provenance render (`Provenance.jsx`).** The panel now renders D-045's
split honestly (D-046 §3): the four environment fields (`torch_version`, `transformers_version`,
`device_name`, `cuda_version`) show their real captured values on post-D-045 folds, and read
**"not captured"** — never a value, never a bare em-dash — on pre-D-045 folds, whose gap is named
**once** at the population level *with its reason* (the record is written worker-side at fold time
and cannot be reconstructed), not repeated per field. The three provenance classes are visually
grouped and labelled — *what ran* (weights), *how it ran* (recipe), *what it ran on* (environment).
**No completeness score** (§3 "deliberately not done"): a fold we can say less about is not a worse
fold. This is the one component where a silent render bug produces a *plausible-but-false*
provenance claim, so it carries the most tests (9).

**§3.2 — tier legibility (`TargetList.jsx`).** The list shows each fold's `tier` per row and is
filterable by tier, so the two-machine cohort (local int8 vs. rental fp16) is legible without
opening a JSON payload (UI-depth §2.3). Tiers are **not** blended into a combined quality score
(D-028). **No supplier change** — `tier`/`tier_reason` are already in the light-list projection
(`app/reads.py` `_LIST_META_KEYS`), verified before speccing (UI-depth trap a).

**§3.3 — the bands, re-pinned against the enlarged cohort (`plddt.bands.test.js`).** D-039's
50/60/70 were justified over the 42-fold distribution (24%/45%/57% below 50/60/70). The prework's
rule (trap b) is *recompute, do not assume*. **Provenance limit stated honestly (D-016):** the
individual `mean_plddt` values live in production Postgres, not in any repo artefact, so the *new
distribution percentages cannot be recomputed here without fabricating them.* What this PR pins
instead is the **band contract as a single source of truth** — boundaries exactly 50/60/70, the
not-folded sentinel, `colorFor` derived from the same `BANDS` (so structure and legend cannot
disagree), and the cohort-max 81.4 caveat living only on the top band — plus a concrete check that
the four new rerun folds (ADAM17 72.78, SDK1 58.01, NOTCH2 57.89, PTPRZ1 30.68) classify sensibly.
**The numeric re-justification of the 60 line against the full current cohort is a named owner
action** (a live `GET /api/analyses` query over every `mean_plddt`); if the shape has moved
materially, D-039 gets amended with the new numbers rather than silently keeping a justification
that no longer holds.

**§3.4 — per-residue spread (`PlddtSpread.jsx`, rendered by `Confidence.jsx`).** The mean hides
the spread: NECTIN4 runs 50.1–93.4 on a mean of 77.26 (UI-depth §2.5). Beside the mean the panel
now states min/median/max, the fraction of residues below the trust divider (60), and a hand-rolled
SVG sparkline coloured by the same D-039 bands (D-037). It surfaces uncertainty and never
manufactures a headline confidence number (UI-depth trap c — more informative, not more confident).

- **Deep-learning justification:** every piece makes a *network output* legible as what it is. The
  provenance panel makes the Prime-Directive claim ("we ran ESMFold ourselves, at a named revision")
  **checkable** rather than asserted, and refuses to render a missing environment field as present —
  the exact failure that would convert an honest gap into a false assurance a grader cannot detect
  (D-046 §4). The per-residue spread surfaces the model's *own* confidence varying across the
  molecule — the single highest-information-per-pixel view of the DL output. Tier legibility keeps a
  methodological distinction (int8 vs. fp16, two torch builds) visible instead of blended. The band
  re-pin keeps the self-reported confidence scheme a single, visible, ruled contract.
- **Consequences:**
  - New: `ui/src/components/PlddtSpread.jsx` (+ test), `ui/src/components/Provenance.test.jsx`,
    `ui/src/components/TargetList.test.jsx`, `ui/src/plddt.bands.test.js`. Rewritten:
    `Provenance.jsx`, `TargetList.jsx`. Edited: `Confidence.jsx` (renders `PlddtSpread`),
    `styles.css`. **Deleted:** `ui/src/plddt.test.js` (D-046 smoke test, per owner ruling).
  - `bandFor`/`colorFor`/`BANDS` in `plddt.js` are unchanged — the scheme was re-pinned, not
    re-cut. Any future boundary change remains a visible, ruled change (D-039).
  - **Not built, not mocked:** the ranking table (UI Plan v2 step 6) still waits on the scorer
    (D-041 → fit). No new runtime dependencies; `test_image_contents.py` still guarantees the test
    deps never cross into the runtime image (D-046).
  - **Owner follow-up:** the §3.3 numeric recompute against the live cohort; the small stale-doc
    fixes carried in the prework §5 (runbook token `69`→`64`, the rent-guide Step 7 install path,
    the `worker/requirements.txt` `+cu128` pin split).

---

### D-047 — The fold recipe is resolved at fold-time, not frozen at enqueue

- **Date:** 2026-07-25
- **Status:** Proposed → Accepted on merge.
- **Relates:** D-042 (the rental recipe change that this incident proved never reached the
  already-enqueued jobs), D-044 (`--requeue`, which faithfully replayed the stale recipe),
  D-026 (enqueue stamps `inference_settings`), D-031 (`build_fold_spec`, the claim→FoldSpec
  projection this moves the resolution into), D-016 (provenance names how it is known),
  D-045 (the fold captures its real environment — where provenance actually lives).
- **Amends:** the data-flow of D-026/D-031 — `dtype`/`chunk_size` are no longer *trusted*
  from the job's stored `inference_settings`; they are resolved from the current
  `TIER_RECIPE` at claim. Does not reverse a ruling; closes a latent seam.

---

#### Part 1 — the incident (immutable history: what already happened)

The five-target rental rerun (2026-07-24, closeout `CLOSEOUT-2026-07-24-rerun.md`) produced
**zero folds on first attempt**. Every large target OOM'd with the tell `at chunk_size=None`
— **unchunked** — despite `TIER_RECIPE['rental']` reading `chunk_size=64` since D-042. IGF2R
(2491 aa) asked for **230 GiB** on a 44 GiB card.

**Root cause — a recipe frozen at the wrong time.** The fold recipe is snapshotted into the
job's `inference_settings` **at enqueue** (D-026) and never refreshed. The five were first
enqueued *before* D-042, when the rental recipe was `chunk_size=None`. **D-042 corrected the
recipe *table* — not the already-stamped jobs.** `requeue_jobs` (D-044) resets
status/claim/error/attempts but does **not** re-read `TIER_RECIPE`, so it faithfully replayed
the pre-D-042 config that had failed these targets the first time. Every component was
correct in isolation — the table was right, enqueue stamped it right, requeue reset the row
right — and the *interaction* (a recipe changing *after* jobs are enqueued, then a requeue) was
the one seam no test covered, because it had never occurred until D-042's change met D-044's
requeue on these specific pre-D-042 jobs.

**The manual fix that unblocked the live rental (recorded, not hidden — D-016).** With the pod
on the meter, the owner reached the current recipe into the frozen jobs by a **guarded one-time
`UPDATE`** of `inference_settings.chunk_size` (`None`→`64`, later →`32` for IGF2R's retry) on
the requeued rows. The guard was tight: worker **stopped first** (a running worker re-claims a
`pending` job within its 5-second poll and re-fails it before the edit lands — a second hazard
worth naming: *never edit a job a live worker can claim*); only `pending` rows; only that one
key via `jsonb_set`; asserted row count. **This changed an *input* recipe, not a provenance
record.** The fold still recorded what it *actually* ran (`fold_provenance`), so no provenance
was faked — the stored `chunk_size` per target is true to each fold (`64` on the three the fix
reached, `None` on ADAM17 which folded unchunked on the broken first attempt). These hand-edits
are now live in prod; the cure below makes such edits never necessary again.

#### Part 2 — the cure (the ruling)

**Recipe resolution moves to fold-time.** `build_fold_spec` (`app/artifacts.py`) resolves
`dtype`/`chunk_size` from the current **`TIER_RECIPE[tier]`** — reading `tier` from the analysis
`meta` it already loads — **not** from the job's stored `inference_settings`. No enqueued job
can ever carry a stale recipe again, because the recipe is no longer *stored-then-trusted*: it
is *resolved at claim*. `build_fold_spec` is **the one authoritative site**.

**The design tension, recorded honestly (D-016/D-004).** Freezing the recipe at enqueue was
arguably provenance — "what this job was *told* to run." Moving to fold-time trades that stored
*intent* for **correctness-by-construction**. The resolution: **the job's pre-fold
`inference_settings` was never the provenance record — `fold_provenance` is** (D-045). The fold
captures what it *actually* ran (`build_provenance` records the real `chunk_size`/`dtype`, plus
D-045's environment), so provenance is preserved at the fold, where it belongs. The intent is
not lost either:

- **Enqueue keeps stamping the recipe into `inference_settings`, now explicitly as a
  *non-authoritative hint*** — the enqueue-time intent, retained as a record, no longer trusted
  by the fold path. `inference_settings` remains **authoritative** for the per-target facts that
  are *not* the tier recipe: `model_revision` (the pinned weights), `source`, and the ECD bounds
  (`ecd_start`/`ecd_end`) — those are the target's slicing identity, not a compute knob D-042
  can revise. Only `dtype`/`chunk_size` become hints. (Stopping the stamp entirely was the
  alternative; keeping it preserves the intent record and the D-026 enqueue tests, at the cost of
  a field a future reader must know is a hint — so it is labelled one, in the code and here.)

**`TIER_RECIPE` relocates to `core/contracts.py`.** It lived in `core/enqueue.py`, which imports
`worker.runner` (→ `worker.orchestrator`) at module load. `build_fold_spec` is **serving-tier**
(`app/`), and the serving image copies only `app/`+`core/`+`db/`+`data/` — **no `worker/`**
(DEP-001) — so importing `TIER_RECIPE` from `core.enqueue` would crash the serving tier at
import time in prod. `core/contracts.py` is the serving-safe leaf that already holds `FoldSpec`
for exactly this reason; `TIER_RECIPE` joins it, with literal values (local `int8`/64, rental
`fp16`/64) mirroring `worker.runner`'s fold defaults. `test_image_contents.py` stays green — no
new `worker/`/torch enters the image.

**`requeue_jobs` gains a fail-loud tier guard.** With fold-time resolution, requeue no longer
needs to re-stamp — it just resets status. But it now **asserts each non-complete job's analysis
`meta` has a resolvable `tier`**, so a tier-less job fails loud *at requeue* (before the worker
claims it), not silently at fold. A complete job is still never touched.

- **Deep-learning justification:** the recipe (`dtype`/`chunk_size`) is what decides whether the
  ESMFold trunk's O(L³) triangular attention fits the card at all (D-042). A frozen-stale recipe
  is the difference between a fold and a 230 GiB OOM; resolving it at fold-time is what makes the
  mechanism D-042/D-044/D-045 built actually *reach* the fold.
- **Consequences:**
  - `app/artifacts.py` `build_fold_spec` resolves `dtype`/`chunk_size` from `TIER_RECIPE[tier]`;
    `core/contracts.py` gains `TIER_RECIPE`; `core/enqueue.py` imports it from there.
  - **Regression test (names the incident):** a job whose stored `inference_settings.chunk_size`
    is `None` but whose `tier` is `rental` → `build_fold_spec` yields `chunk_size=64` (current
    recipe wins over stored). Red before the fix, green after.
  - **Runbook change:** a future failed-target rerun is now just `--requeue` + refold — **no
    manual recipe patch, no `chunk_size` surgery.** That is the whole point.
  - **Not a rescue for last session's jobs.** This is the permanent cure for *future* runs; it
    was not deployed before the rental finished and did not touch the four (five) already-
    folded/failed jobs (see the incident's manual path). Deliberately uncoupled from the live run.

---

### D-046 — Component tests for the UI, and the two-population provenance render

- **Date:** 2026-07-24
- **Status:** Proposed → Accepted on merge.
- **Relates:** D-037 (the JS toolchain as a third dependency world — this adds to it),
  DEP-006 (the two-stage image that makes the addition safe), D-045 (the two populations this
  renders), D-016 (a claim names how it is known), D-028 (attribution, not explanation).
- **Amends:** nothing. This closes a gap rather than reversing a ruling.

---

#### 1. Context — the test rule has not been reaching the UI

The project's binding rule is **tests first, code later**, and nothing deploys unmerged-untested
(D-005/D-008). For Python that holds: 222 tests across 46 files. For the React tier it does not,
and the reason is mechanical rather than deliberate.

**Provenance (D-016).** `ui/package.json` at `3ccdcc5` declares four dependencies and two
devDependencies — `@vitejs/plugin-react`, `vite`. **No test runner.** `find ui -name "*.test.*"
-o -name "*.spec.*"` (excluding `node_modules`) → **zero files.** The one UI-adjacent test,
`tests/test_ui_serving.py`, is Python and asserts *route ordering and bundle serving* — that
`/api` and `/jobs` match before the SPA fallback — **not component behaviour**. So every component
shipped to date (TargetList, TargetView, Confidence, PlddtPlot, StructureViewer, Provenance,
CoverageView, CoverageLine, MethodNote, AdcContext) is **unverified by any automated test**.

This is stated as a finding, not a fault: PR A–C shipped under a real deadline and the gap was
invisible while the components were simple renderers. It becomes load-bearing now because
**UI-depth §3.1–§3.4 queues four more components**, the first of which (this one) must render a
*correctness-relevant distinction* — captured vs. not-captured environment — where a silent
render bug produces a **plausible-looking but false provenance claim**. That is the one class of
UI bug this project cannot tolerate, because the provenance panel exists precisely to make the
Prime Directive claim checkable.

---

#### 2. Decision (1) — add `vitest` + `@testing-library/react` as devDependencies

- **`vitest`** (not jest): it reads the existing `vite.config.js` and the project's ESM/JSX setup
  with no second toolchain. A jest install would need its own transform config — a second build
  description of the same source, and a drift surface.
- **`@testing-library/react`** + **`jsdom`**: assert on **rendered output as a reader encounters
  it** (visible text, roles) rather than component internals. This matters for the specific bug
  class above: the test should fail when a reader would see a wrong claim, not when a prop is
  renamed.
- **`npm ci` still governs** (D-037) — new devDependencies land in the committed
  `package-lock.json` as a reviewable diff.

**Why this is acceptable under D-037's third-dependency-world framing.** D-037 accepted the JS
toolchain's weaker (lockfile, not hash-verified) guarantee because it is **build-time only** —
nothing it installs reaches the runtime image, so a drifted dependency affects the bundle
produced, not the server running. **Test dependencies are strictly weaker still: they are neither
runtime nor build-output.** They run in CI and on a developer machine; they contribute *nothing*
to `npm run build`'s output.

**Verified against the artefact, not assumed** (D-016): `Dockerfile` stage 1 runs `npm ci` (which
does install devDependencies) but stage 2 copies **only `/ui/dist`** — `COPY --from=ui-build
/ui/dist ./ui_dist`. No `node_modules`, no Node binary, crosses the stage boundary.
`tests/test_image_contents.py` asserts that shape and reddens if a future edit breaks it. So the
blast radius of a compromised test dependency is a developer machine and a CI runner — **not the
deployed image**, which is the property D-037's reasoning turns on.

**What this does NOT provide, stated so it is not over-read.** Component tests assert that a
component renders correctly *given props*. They do **not** assert that the supplier provides those
props, that the API contract holds, or that the deployed bundle works — those remain the Python
tests' and the deploy gate's job. This closes a component-behaviour gap, not an end-to-end one.

---

#### 3. Decision (2) — the two-population render rule (the thing being tested)

D-045 split the cohort: **pre-D-045 folds carry no environment record; post-D-045 folds do.** The
panel renders that split honestly. Three rules, and each is a test:

1. **An absent field reads as _not captured_, never as a value and never as an em-dash that could
   be mistaken for "none."** The existing panel renders `'—'` for any null, which is correct for
   `ecd_start` on a whole-chain fold (genuinely not applicable) but **wrong for `torch_version`**,
   where the honest statement is *"this fold predates environment capture."* Conflating
   *not-applicable* with *not-recorded* is the D-024 failure in miniature — the same reason
   `fold_status` needed three states rather than two (D-043).

2. **The gap is named once, at the population level, not repeated per field.** A pre-D-045 fold
   shows a single note explaining that environment capture began at D-045 and this fold predates
   it — with the *reason* (the record is written worker-side and cannot be reconstructed), not just
   a flag. D-022's rule: a boolean is not a reason.

3. **Environment fields are visually grouped and labelled as the environment**, distinct from the
   recipe (`dtype`/`chunk_size`) and the weights (`model_id`/`model_revision`). The three answer
   different questions — *what ran*, *how it ran*, *what it ran on* — and D-028's rule against
   collapsing distinct classes applies to a provenance panel as much as to a score.

**Deliberately not done:** no per-target "provenance completeness" score, no percentage, no badge
ranking folds by how well documented they are. That would invite reading a *documentation* property
as a *quality* property — and it is the pre-work's trap (c): every addition must show more of what
the system does not know, never manufacture confidence. A fold from an unrecorded torch build is
not a worse fold; it is a fold we can say less about.

---

#### 4. Deep-learning justification

The provenance panel is where the Prime Directive claim — *"we ran ESMFold ourselves, at a named
revision"* — is made **checkable rather than asserted** (ARCHITECTURE §1). D-045 established that
the claim is weaker than it looks without the framework build underneath the weights. This entry
makes the *rendering* of that claim testable, which is what stops it from silently degrading into
a stronger claim than the data supports. **A provenance panel that renders a missing field as
present is worse than no panel**: it converts an honest gap into a false assurance, and a reader
(a professor, a reviewer) has no way to detect it. The tests exist for exactly that failure.

---

#### 5. Consequences

- `ui/package.json` gains `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `jsdom`
  as **devDependencies**; `package-lock.json` updated via `npm ci`-compatible install; a
  `"test": "vitest run"` script.
- `vite.config.js` gains a `test` block (jsdom environment). No change to the build output.
- **CI runs the UI tests** — the gate must execute them or the rule is decorative. The `test` job
  gains a Node step running `npm ci && npm run test` in `ui/`.
- **`tests/test_image_contents.py` remains the guarantee** that none of this reaches runtime; if a
  future edit copies `node_modules` into stage 2, it reddens. No change needed to it now.
- `ARCHITECTURE.md` updated in the same PR (the dependency-world description and the CI shape).
- **Follow-on:** §3.2–§3.4 (tier legibility, band recompute, per-residue distribution) are built
  tests-first under this harness. The existing untested components are **not** retro-tested in this
  PR — that is a separate, non-blocking cleanup, named here so it is a known debt rather than an
  omission.

---

### D-045 — Fold provenance captures the software environment, forward from now
- **Date:** 2026-07-24
- **Status:** Proposed → Accepted on merge.
- **Amends:** D-018 (the fold-runner's provenance record — `FoldProvenance` gains four optional
  environment fields). Relates to D-015 §1a (provenance the diagnostics depend on), D-016 (every
  claim names how it is known), D-042 (no diagnostic may fail the batch).
- **Context — what the record does not name, and the grep that proves it.** `FoldProvenance`
  (`worker/runner.py`) captures `model_id`, `model_revision`, `dtype`, `chunk_size`, the
  slice/truncation flags, `mean_plddt`, `ca_atom_count`, `folded_at`. It captures the *weights and
  the recipe* — **not the software environment that produced the fold.**
  `rg -rn "torch.__version__|transformers.__version__" --glob '*.py' .` → **zero hits, whole tree**
  (re-verified on branch). So the **80 landed folds came from two different torch builds** — 2.11.0
  local, 2.8.0 rental (closeout 2026-07-23 §7) — and **nothing in the database records which.**
- **Why the 80 are unbackfillable.** The record is written **worker-side, at fold time**, from a
  process that no longer exists. There is no server-side reconstruction path: the DB stores what the
  worker sent, and the worker did not send a torch version because the field did not exist. **The
  five rerun targets are the last chance to make the gap bounded rather than open-ended** — after
  them the cohort is folded and the door closes.
- **Provenance (D-016):** ruled against `worker/runner.py` (`FoldProvenance` at :62, `build_provenance`,
  `fold` filling `mean_plddt`/`ca_atom_count` post-fold at :257) and the zero-hit grep above.

---

- **Decision — capture forward from now; the cohort becomes two honest populations.** Add four
  `Optional[str] = None` fields to `FoldProvenance`: **`torch_version`**, **`transformers_version`**,
  **`device_name`** (`torch.cuda.get_device_name(0)`), **`cuda_version`** (`torch.version.cuda`).
  Populated inside `fold()` where torch is already imported, via a small `_capture_environment()`
  helper — **`build_provenance` stays torch-free** (the D-018 property that lets the whole module
  import and unit-test on the CI gate with no CUDA). The cohort splits into **pre-D-045 (no
  environment record) and post-D-045 (with)**, and the UI renders that split **honestly rather than
  hiding it** — an absent field reads as *"not captured"*, never as a fabricated value.
  - **All fields optional, none required** — so the 80 old records (whose provenance dicts lack these
    keys) deserialize unchanged. A required field would break the read API on every existing fold.
  - **`_capture_environment()` never raises** — every probe is guarded and defaults to `None`. A
    provenance-capture failure must never fail a fold (D-042's spirit: no diagnostic takes down the
    batch). An absent torch, an unavailable CUDA device, or a missing attribute yields `None`.
- **Deep-learning justification — this is a Prime Directive claim made checkable.** *"We ran ESMFold
  ourselves, at a named revision"* is the claim the provenance panel exists to support. A model
  revision **without the framework build underneath it is a weaker claim than it appears**: the same
  pinned weights on a different torch/CUDA build are the same numerics through different kernels.
  Recording the build closes the distance between the claim and what is actually verifiable.
- **Consequences / test surface:**
  - **Tested first** (`tests/test_runner.py`, CI gate, no GPU): `build_provenance` still imports and
    runs **with no torch present** and the four new fields are `None` on the pure path (the D-018
    guarantee); a `FoldProvenance` with the fields set `asdict()`s and JSON-round-trips; an
    **old-shaped provenance dict (no new keys) still constructs** without error (the one that would
    break the read API if wrong); `_capture_environment()` **returns the four keys and never raises**
    when torch/CUDA are absent (every value `None`-or-`str`). The GPU-populated path is validated on
    the owner's host (no CUDA in CI, D-018).
  - **Scope boundaries (per orders):** the read API, coverage, and the UI are **untouched** — a
    separate concern for a later PR. **No backfill of the 80** — there is no honest source.
  - **`ARCHITECTURE.md`** updated in this PR — the provenance record's shape is part of the data model.
- **Definition of done:** green gate, merged to `main`, **and the rerun's pod runs the merged worker
  code** — confirm the pod's checkout SHA is the post-merge commit, not `5bce970`. If the worker is
  behind the merge, the five land in the pre-D-045 population and this was wasted.

---

### D-044 — `core.enqueue --requeue`: a deliberate re-fold path, because idempotency has no reverse
- **Date:** 2026-07-24
- **Status:** Proposed → Accepted on merge.
- **Relates:** D-026 (enqueue idempotency — the thing this works *around*), D-030 (the job status
  machine and the reaper), D-009 §1 Am. 2 (attempts semantics). Motivated by the 5-target rerun
  (`RUNBOOK-rerun-5-targets.md`).
- **Context — the rerun exposed a one-way door.** D-026's enqueue is idempotent on
  `(target_list_version, accession)` via the **`protein_analyses` row** (`core/enqueue.py:123`):
  a second `enqueue` for a target that already has an analysis writes **nothing** — no new job.
  That is correct for *"one now, the rest later."* But it means enqueue **cannot re-offer a target
  that failed**: the five failed reruns already have analysis rows, so `enqueue --bucket rental`
  reports them `existed` and creates zero jobs. Their `jobs` rows are stuck non-`pending` (`claimed`,
  from the pre-D-042 mid-fold crashes), the worker claims only `pending` (`app/routes.py`), and
  **`reap_stale` has no production caller** (verified — no Fly cron, no app startup hook, no claim-
  path reap; it runs only in tests). So there is **no path, manual or automatic, back to `pending`**
  short of hand-run SQL against prod. That is a fragile step to leave in a runbook (the same class
  of by-hand-against-prod fiddliness that truncated a token and cost 70 minutes on the first run).
- **Provenance (D-016):** ruled against `core/enqueue.py` (idempotency at :123, the `run()` CLI),
  `core/queue.py` (`PENDING`/`COMPLETE` constants, the `claim` filter `WHERE status='pending'`,
  `reap_stale`), and the confirmed absence of any `reap_stale` prod caller.

---

- **Decision — add `python -m core.enqueue --requeue ACC [ACC …]`.** A pure `requeue_jobs(session,
  accessions)` + a CLI flag that short-circuits before the manifest/fetch path (requeue neither
  fetches sequences nor creates rows — it only moves existing jobs). For each accession, joined to
  its jobs via `protein_analyses.input_value` (the D-038 uniprot key):
  - a **non-`complete`** job → `pending`, clearing the stale claim (`claimed_at`/`worker_id`), the
    `error`, and **resetting `attempts` to 0** — a deliberate operator retry gets a full budget,
    distinct from `fail()`'s attempts-untouched rule (D-009 §1 Am. 2), which is about *automatic*
    history. This is an explicit override, and it says so.
  - a **`complete`** job is **left untouched** — re-folding a target whose structure already exists
    is paid and pointless. Requeue never destroys a good fold.
  - an accession with **no job at all** is **reported, not silently dropped** (understating what was
    requeued is the D-024-adjacent failure), and makes the CLI exit non-zero so a typo is loud.
  - **Idempotent:** requeuing a `pending` job is a no-op-shaped write; safe to re-run.
- **Deep-learning justification:** indirect but real — the reruns are how the network folds the
  above-ceiling targets the coverage surface (D-024) needs, and without a re-fold path a failed
  target is permanently stuck failed. The scorer's eventual denominator depends on these landing.
- **Consequences / test surface:**
  - **Tested first** (`tests/test_enqueue_cli.py`, hermetic SQLite): a `failed` job → `pending`
    with `attempts` reset and `error`/claim cleared; a `complete` job is **not** touched; an unknown
    accession is reported and the exit code is non-zero; requeue does **not** fetch (the fake fetcher
    asserts if called) and creates no new analysis/job rows.
  - **Runbook:** `RUNBOOK-rerun-5-targets.md` Phase 1 switches from the hand-run SQL snippet to this
    one guarded command.
  - **Not built:** a standing reaper / scheduled requeue (out of scope — the operational need is a
    one-time, operator-initiated re-fold, not an automatic recovery loop; the silent-hang/heartbeat
    question stays with D-030).

---

### D-043 — Coverage `fold_status` is three states: a failed fold is not an unattempted one
- **Date:** 2026-07-24
- **Status:** Proposed → Accepted on merge.
- **Amends:** D-038 (the coverage supplier payload — `fold_status` gains a third value and a reason
  field; the `coverage` partition object is untouched).
- **Context — D-024 says the reader must see what the system could not do, and today the coverage
  surface cannot.** Five targets (ADAM17, IGF2R, NOTCH2, PTPRZ1, SDK1) exist as enqueued work that
  did **not** fold — four exceeded the unchunked memory ceiling (D-042 §1: `tri_att_start` is O(L³);
  IGF2R asked 230 GiB on a 95 GiB card), one was interrupted mid-fold. D-038's supplier joins only
  the **folded** set (`_folded_accessions`, a completed `protein_analyses` row with `pdb_path` set)
  and collapses **everything else to `not_folded`**. So *attempted-and-failed* and *never-attempted*
  render identically — which is exactly the flattening D-024 forbids: a reader cannot tell a hardware
  ceiling the system hit from a target it never touched.
- **Provenance (D-016):** ruled against `app/reads.py` (`coverage_payload`, `_folded_accessions`,
  `_coverage_row` as shipped in #55), `db/models.py` (`JobRecord.status`/`.error`, `analysis_id` FK
  to `protein_analyses`), `core/queue.py`'s status machine (`PENDING → CLAIMED → COMPLETE | FAILED`,
  `REAPED_OUT_REASON`), and live `GET /api/coverage` returning the five as `not_folded`.

---

- **Decision — the supplier joins `jobs` and emits `fold_status ∈ {folded, failed, not_folded}` plus
  a `fail_reason`.** Precedence, in order, so the honest state always wins:
  1. **`folded`** — a completed `protein_analyses` row exists (`pdb_path` set). `fail_reason` null.
     A target that failed an early attempt and later folded reads `folded`; the success is the truth.
  2. **`failed`** — no completed row, but a **terminally `failed`** job exists for the accession.
     `fail_reason` carries `jobs.error` verbatim.
  3. **`not_folded`** — neither. `fail_reason` null.

  **Only the terminal `failed` status counts — `claimed`/`pending` are in-flight, not failures.** A
  target being re-folded right now (a fresh `pending` job) must not read `failed`; the moment its row
  completes it flips to `folded`. This is the D-030 status machine's own boundary, honoured here.

  **The join is `jobs.analysis_id → protein_analyses.id → input_value`**, the same accession-in-
  `input_value` key D-038 already documented (uniprot inputs only; a future non-uniprot type widens
  it rather than silently miscounting). Where multiple failed jobs share an accession, the **latest**
  (highest `id`) supplies the reason.

  **`fail_reason` is served verbatim, not prettified.** For the current five that means whatever the
  DB actually holds — and today, honestly, that may be nothing clean: four OOM'd by **crashing the
  worker before D-042's `fail()` path existed** (left `claimed`, then either stuck or reaped to
  `failed` with the generic `REAPED_OUT_REASON` marker, *not* the OOM text). **That is the correct
  behaviour, not a gap:** the supplier surfaces the truth of the record. The specific, presentable
  reason ("CUDA OOM, O(L³) attention") is written only when D-042's `fold → FoldError → fail(error)`
  path runs — i.e. **on the rerun** (D-042 rerun list). This entry builds the *mechanism*; the rerun
  supplies the *content*. The component is therefore built blind to which rows fail and renders
  **zero failures correctly** — so it does not depend on, and cannot be invalidated by, the rerun.
- **A payload-level `failed` count** sits beside `coverage` (not inside its partition): the `coverage`
  object stays pure-manifest and continues to sum `ranked + held_out + excluded == denominator`
  (D-038's invariant, untouched). `failed` is a DB-join fact, a subset of `not_folded`'s old count,
  and is documented as such so no client sums it into the denominator.
- **Deep-learning justification:** direct, via D-024. The coverage line is what keeps the eventual
  ranking honest; a surface that hides *attempted-and-failed* inside *not-yet* understates what the
  fold pipeline was asked to do and where the hardware ceiling actually bit. **Showing the failures —
  with reasons — is the honest-denominator discipline applied one level deeper.**
- **Consequences / test surface:**
  - **Tested first** (`tests/test_coverage_route.py`, hermetic — real manifest + in-memory SQLite):
    a terminal `failed` job with no completed row → `fold_status == "failed"`, `fail_reason == error`,
    `analysis_id is None`; a **`claimed`** job (in-flight) → `not_folded`, **not** `failed`; a folded
    row that also has a failed job → `folded` (precedence); `fail_reason` is null unless `failed`; the
    payload `failed` count equals the number of failed rows; the empty-DB default stays all
    `not_folded`. D-038's existing invariants (partition sums, denominator pinned at 82, exclusions by
    name) are unchanged and still pass.
  - **UI (`CoverageView.jsx`):** the two-way Fold cell becomes three-way (`folded` / `failed` /
    `not yet`); the note cell shows `fail_reason` for a failed row as it already shows
    `exclusion_reason` for an excluded one; a `.failed` style is added beside `.folded`/`.not-folded`.
  - **No supplier schema change, no migration:** `jobs` already carries `status` and `error`
    (D-009/D-012). CPU-only join over ≤82 rows; no new dependency, no new table.
  - **Not built:** a `failed` cell in the `coverage` partition object (would break D-038's sum
    invariant); prettifying the reaped marker (the UI may soften presentation later, the supplier
    stays literal).

---

### D-042 — Rental-tier hardening: chunking is mandatory, and no single fold may take down the batch
- **Date:** 2026-07-23
- **Status:** **Accepted** — the first rental run (`CLOSEOUT-2026-07-23-full.md`) exposed these; the
  fixes land in this change.
- **Amends:** D-011 (the rental recipe, and the hardware/cost estimate), D-022 (the A6000-class
  ceiling — now measured), D-030 (the loop's failure taxonomy, and the lease-heartbeat trigger),
  D-035 (PAE size at scale).
- **Context — five findings only the rental tier could expose.** 42 → 80 folds landed on a rented
  RTX PRO 6000 (95 GiB, $2/hr — **not** the A6000/48 GB/$0.49 D-011 specified); **5 failed**;
  coverage moved 40 → ~63 ranked ∧ folded. What the run taught, and what this change does:

#### 1. Chunking is not optional — D-011's core assumption is falsified
D-011's rental recipe set `chunk_size=None` on the premise that a large card "runs fp16 unquantised
and unchunked, so the local mitigation stack stops binding." **Measured false.** The ESMFold trunk's
triangular attention (`tri_att_start`) is **O(L³)**, not O(L²): **IGF2R (2,491 aa) asked 230 GiB** on
a 95 GiB card; LRP6 (~1,351 aa) asked 67 GiB against 37 free. No rentable card closes a 230 GiB gap.
**The unchunked ceiling on 95 GiB sits between 1,034 aa (JAG1, folded) and ~1,350 aa (does not).**
Chunking is the only mitigation — the local tier already uses it. **`TIER_RECIPE["rental"].chunk_size`:
`None` → `64`** (`core/enqueue.py`). Chunking trades speed for memory; the oversized targets run
slower and succeed.

#### 2. A fold failure must not crash the batch (closeout §3a)
D-030 §4 rules a fold failure calls `fail()`, records the error, and the loop continues. **It didn't:**
a `torch.OutOfMemoryError` propagated `fold → run_worker → main` and **killed the process — four
times over the night**, each taking down every good fold queued behind it (invisible on the local
tier, whose folds never OOM). Two-layer fix:
- **`runner.fold` classifies CUDA OOM as `FoldError`** — the classification D-030 §4 always intended
  but never implemented. OOM on a fixed (sequence, recipe) is deterministic, so it is terminal, not
  retried on a paid card.
- **`run_worker` gains a batch-resilience catch:** any *unexpected* fold exception is logged **loudly
  with a traceback** and the one job is failed — the batch survives. Loud-not-silent, so a real bug
  stays visible rather than masked.

#### 3. A rejected token stops the worker loudly (closeout §4b)
A `WORKER_AUTH_TOKEN` truncated to 12 chars (of 69, mangled by shell quoting) polled and was rejected
**401 every 5 s for 70 minutes** while the worker looked healthy — process alive, no stderr. Fly
logged every rejection; nobody watched, because the worker said nothing. **A 401 is now a distinct
`AuthError`** (a `TransportError` subclass, but **not** retried): the loop stops on the **first** one
with a loud log naming the cause. 70 minutes → 5 seconds.

#### 4. The model loads once per batch, not once per target (closeout §3c)
`fold` reconstructed the model on every call (`Loading weights: 4498` per target) — invisible on owned
hardware, a ~10–20% cost on rented silicon. **`_load_model` caches by `(dtype, revision)`**; a
single-recipe batch loads the weights once.

- **Deep-learning justification.** Direct: the rental tier is how the network folds the 29
  above-ceiling targets, and a tier that crashes on its largest inputs or silently burns paid time
  folds nothing. #1 is the load-bearing correction — the graded deliverable's coverage depends on
  these folds landing, and they cannot land unchunked.

- **Consequences / test surface:**
  - **Tested first (CI, no GPU):** the rental recipe is fp16/**64**; an `AuthError` from claim stops
    the loop on the first 401 (not a retry loop); an unexpected fold exception fails the one job and
    the batch continues (a good fold behind a bad one still lands); a 401 maps to `AuthError` while a
    500 stays `TransportError`. The OOM→`FoldError` line and the model cache are **GPU-validated on
    the owner's host** — no CUDA in CI (D-018).
  - **Rerun list (closeout §8):** ADAM17 (crashed mid-flight — retry as-is) + PTPRZ1/NOTCH2/SDK1/IGF2R
    (needed chunking — now fold under the new recipe). ~$2, coverage → 67 of 82. Not urgent; the
    scorer proceeds at 63.
  - **Ops (in the a6000 guide, not code):** run the worker **detached** (`nohup … &`, not a browser
    terminal foreground — closeout §4a lost ~1 hr of billing); **`WORKER_ARTIFACT_DIR` set** or rental
    PAE is silently lost; **`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`** a candidate against
    fragmentation (§3d, untested); **delete the network volume** after termination (attached against
    D-011, bills monthly).

---

### D-041 — The scorer: regularized logistic regression, and why the small model is the correct one
- **Date:** 2026-07-23
- **Status:** Proposed → Accepted on merge. **Ruled before any fitting code exists** (D-015 §3's
  pre-registration discipline).
- **Discharges:** the gap D-027 left open. D-027 fixed the *features*; D-015 §3 ruled a "small
  trained model" and ruled out both a learned embedding and a hand-weighted sum — but **named no
  architecture, no loss, no fitting procedure, and no leave-one-out statistic.** Until those are
  fixed, they get chosen after seeing results, which is what pre-registration exists to prevent.

---

- **Context — what the fit actually has to work with.** Six features (D-027). Group B labels,
  ~22 positives across the 82 (D-040). **But the fit runs only on targets that are both labelled
  and folded**, and only **40** targets are `ranked ∧ folded` today (29 rental-tier unfolded).
  **The labelled ∧ folded intersection is unknown until D-040's curation lands and is computed
  before fitting** — if it is materially under 22, this entry's sizing arguments tighten further
  and that is recorded as a finding, not absorbed.

---

#### Decision (1) — The model is **L2-regularized logistic regression** over the six standardized features

Binary target: Group B membership. One coefficient per feature plus an intercept — **seven
parameters**.

**Why this and not something deeper, argued rather than defaulted:**

- **The parameter budget is the whole argument.** ~22 positives against seven parameters is
  already ~3 positives per parameter. A 6→8→1 MLP is ~65 parameters — **three times more
  parameters than there are positive examples.** It would fit the training set perfectly and
  learn nothing generalizable, and leave-one-out would expose that as noise rather than signal.
  The small model is not a concession to the data size; **at this data size it is the only model
  whose output means anything.**
- **Interpretability is a ruled requirement, not a preference.** D-015 §3 and D-027 both turn on
  it: *"interpretability is what lets a disagreement be attributed to a feature rather than
  shrugged at."* D-028 then requires attribution rendered as a statement about the model. **A
  logistic regression's coefficients are exactly that statement** — feature *k* contributes
  `β_k · x_k` to this target's score, reportable per target, no post-hoc explainer needed and no
  approximation layer between the model and the claim.
- **L2 rather than none:** with six correlated features (D-027 flags 1 and 2 as collinear by
  construction), unregularized coefficients are unstable — small data changes swing them, and
  attribution built on a swinging coefficient is attribution of noise. **λ is selected by
  nested cross-validation inside each leave-one-out fold** (see (3)), never on the full data,
  because tuning on all of it leaks the held-out target into its own evaluation.
- **L2 rather than L1:** L1 would zero features out, silently reducing the pre-registered
  six-feature set to whatever survived — **a post-hoc feature selection wearing a regularizer's
  clothes**, and a direct violation of D-027's fixed count. L2 shrinks without eliminating, so
  all six remain in the model and the pre-registration holds.

---

#### Decision (2) — ⚠ Where the deep learning is, stated plainly because this entry is where it looks weakest

**A reader who opens the scorer file and finds logistic regression will ask where the neural
network is. The answer must be in the log before the question is asked.**

**ESMFold is the deep learning, and it is load-bearing under any reading of ARCHITECTURE §1 and
CLAUDE.md's Prime Directive:**

1. **The project runs the network itself** — own hardware, pinned checkpoint
   (`facebook/esmfold_v1`, revision `75a3841ee059…`), chosen precision and chunking, 42 folds
   through a production path (D-003, D-011). Not a hosted API, not retrieved structures — the
   distinction D-004 §5 rules on.
2. **Every one of D-027's six features is computed from that network's output** — CA coordinates
   for radius of gyration and SASA, per-residue pLDDT for features 3 and 4. **Without ESMFold
   there are no features; without features there is no scorer.** The network is upstream of the
   entire deliverable.
3. **pLDDT is the network's own uncertainty, used as signal** (features 3 and 4) rather than
   averaged away — the model's self-reported confidence is a model output doing work.
4. **D-015 §3's framing is explicit:** *"ESMFold stops being the deliverable and becomes the
   input to one. The network's output is now a judgement that can be wrong — which is the
   point."*

**The inversion worth naming: a bigger scorer would make the deep-learning claim WEAKER, not
stronger.** An MLP overfitting 22 positives would produce a ranking that could not be defended,
attributions that could not be trusted, and a leave-one-out distribution indistinguishable from
noise. **The graded contribution is a defensible judgement built on inference this project ran** —
and defensibility is what the parameter count buys. Choosing a large model to look like deep
learning, at a data size that cannot support it, would be **decoration in the opposite
direction** from the hand-weighted sum D-015 §3 rejected: both substitute the appearance of
rigour for rigour.

**If a larger model is ever wanted, the honest route is more labelled data, not more parameters** —
and that would be its own entry.

---

#### Decision (3) — Leave-one-out, and the statistic fixed **now**

D-015 §3 pre-registered LOO *"reported as a distribution, never a single CV number"* and did not
say what is distributed. **Fixed here, before any result:**

- **Procedure:** hold out one Group B positive; fit on the remainder (**λ selected by inner CV on
  that remainder only**); score all unlabelled-or-held-out targets; **record the held-out
  target's rank percentile** among the folded cohort.
- **The reported object is the distribution of those percentiles across all held-out positives** —
  shown as the full distribution, with median and spread. **No single summary number is the
  headline.**
- **"Ranks it highly" is defined as: the held-out positive's percentile, reported.** Not
  thresholded into a hit rate — a threshold chosen after seeing the distribution is exactly the
  degree of freedom pre-registration removes.

**The comparison that decides D-015 §3's first negative outcome:** the same percentile
distribution computed for the **comparator's evidence score** on the same held-out targets. If
the structural score's distribution is **not distinguishable** from the comparator's, *"the
structural axis adds nothing measurable at this cohort size. That is the result."*

**⚠ The comparator baseline is only computable where an evidence score exists — 17 of 82 (D-040).**
Intersected with folded-and-labelled targets it is smaller still. **Compute and report that
denominator with the comparison**; a baseline comparison over a handful of targets is weak
evidence and must be labelled as such rather than presented as a head-to-head.

---

#### Decision (4) — The second negative outcome is computed, not left to inspection

D-015 §3's subtler pre-registered null:

> *"If the structural score correlates **strongly** with the comparator's evidence score, that is
> **also** a null result — it means our features are proxying for attention-and-precedent rather
> than measuring structure. **Check this explicitly.**"*

**Ruled: Spearman rank correlation between the structural score and the evidence score, over the
targets carrying both, reported alongside the ranking — always, not on request.** Rank
correlation rather than Pearson because both quantities are ordinal by construction.

**No threshold is set for what counts as "strong," deliberately.** Setting one now would be
arbitrary; setting one later would be after seeing it. **The number is reported and interpreted
in prose against the pre-registered warning**, which is what D-015 asked for. A high correlation
arrives looking like validation and is not, and the entry that says so is dated before the
number exists.

---

#### Decision (5) — Ordering: the diagnostics gate the claim

D-015 §1a: *"Ruling out (3) is a precondition for claiming (1) or (2)."* **The four diagnostics
run and are reported BEFORE any disagreement is characterised:** fold sanity per target
(CA count vs sequence length, no NaN coordinates, radius of gyration consistent with a compact
globular expectation), boundary sanity (ECD from a UniProt topological-domain annotation, not
silently truncated), the pLDDT floor, and score stability under leave-one-out refitting.

**⚠ The pLDDT floor is now a live problem, not a formality.** Measured over the 42 folds: **24%
below 50, 45% below 60, 57% below 70**. D-015 §1a requires targets folding below a **pre-set**
threshold to be *"reported separately, not silently ranked."* **That threshold must be set before
the fit** — and D-039's bands (50/60/70, ruled against this cohort's own mass) are the natural
candidate. **Setting the floor at 50** — the "very low / not reliably interpretable" edge —
separates the 10 targets whose structures cannot support a structural claim at all.

**This is a real cost and is stated as one:** a floor at 50 removes ~24% of the folded cohort
from ranking claims, on a set that is already 40 of 82. **The alternative — ranking a 34.78
structure alongside a 77.26 one — is exactly the failure D-024 exists to prevent**, and it would
put the project's sharpest instrument on top of its weakest data.

---

- **Deep-learning justification.** Direct, and §2 is the entry's substance. The scorer converts
  ESMFold's output into a judgement that can be checked and can be wrong — the transition D-015
  §3 identified as where the Prime Directive is actually discharged. The model's smallness is
  what makes that judgement defensible at 22 positives, and its interpretability is what makes
  D-028's attribution honest rather than a post-hoc story.

- **Consequences / test surface:**
  - **Tested first:** the fit is deterministic given a fixed seed and fixture data; **exactly six
    coefficients plus an intercept** (the pre-registration enforced by the gate, as D-027's
    feature-count test does); λ is selected **inside** each LOO fold and never on full data
    (asserted, since leakage here is invisible in the output); LOO returns a distribution of
    percentiles, not a scalar; a target below the pLDDT floor is **excluded from ranking claims
    and reported separately**; standardization statistics are computed on the training fold only.
  - **`scorer_version`** alongside D-027's `feature_version`, so a refit against changed model
    code is detectable rather than silent.
  - **⚠ The honest claim is bounded, and "viable" is the wrong word for it.** D-015 §3 phrases
    the claim as *"does our score recover targets already known to be viable."* **Viable in what
    respect is doing unearned work there**, and the bound is tightened here:

    > **Does our structural score recover targets that have already been ATTEMPTED as ADCs?**

    "Attempted" is what the Group B label actually records (D-040) — someone built an ADC
    against this antigen and took it into development. **Never** *"does our score predict
    clinical success."* Group B is small, non-random, and survivorship-selected; the fit
    inherits all three.

  - **⚠ What the six features do NOT measure — a named non-goal, because the omissions are
    mostly the binding constraints.** The structural axis speaks to **antibody-accessible
    extracellular surface**, which is *one necessary condition among many* and rarely the
    deciding one. Absent from the feature set, and from any claim the system may make:
    **blood-brain-barrier penetration**, internalisation rate, antigen turnover and shedding,
    tumour penetration in solid masses, expression heterogeneity within a lesion, linker
    stability, payload choice, and bystander effect. **A structurally excellent antigen in a
    CNS indication may be undeliverable by a systemically administered ~150 kDa immunoconjugate
    regardless of how accessible its epitope is** — the paper's own glioma discussion reasons
    about *payload* brain penetration, not antigen quality, which is the distinction exactly.

  - **The axis is delivery-agnostic by construction, and that is the reason a class-2 hypothesis
    is worth generating at all.** Whether an antibody-accessible epitope exists does not depend
    on how the conjugate reached the tumour. Expression-and-attention rankings quietly encode
    the delivery constraint — *attempted* and *studied* are downstream of what developers
    believed they could deliver to. **So a structurally strong target that was never attempted
    may be absent from Group B because the delivery route did not exist when the field looked**,
    and delivery routes are moving: convection-enhanced delivery, focused-ultrasound BBB
    opening, intrathecal and intratumoral routing. **When delivery becomes a mechanical problem
    rather than a chemical one, a ranking computed on delivery-independent properties is the one
    that survives the change.**

    **⚠ Two limits on this argument, stated so it is not over-read:**
    1. **It does not rescue the labels.** The fit still trains on what was attempted, so the
       model still learns from a delivery-biased positive set. The argument bears on what the
       *structural score* means, not on what the *labels* mean.
    2. **The system may not make this claim per target.** *"This ranks high and delivery is the
       only obstacle"* is a biological causal claim about a specific target, which D-028 rules
       out. **The frame is stated once, in the method note, as the reason class-2 hypotheses are
       generated — never attached to an individual row.**
  - **Blocked by D-040** (labels and evidence scores). **Blocks** UI Plan v2 step 6.

---

### D-040 — Group B and the evidence score: what the paper actually publishes, and how each is established
- **Date:** 2026-07-23
- **Status:** Proposed → Accepted on merge.
- **Extends:** D-029 (the approved-ADC reference and its reviewed mapping file). Same seam,
  same discipline, one column wider — see §4.
- **Blocks:** the scorer arc entirely. Without Group B there is nothing to fit; without the
  evidence score there is no comparator, hence no disagreement, no classes, and no ranking view.

---

- **Context — a supplier gap in the *data*, found the same way the code gaps were.**
  D-015 §3 fits the scorer against **Group B**; D-015 §2 compares the structural ranking against
  the comparator's **1–5 evidence score**. **Neither is in the repo.** Verified 2026-07-23
  against the committed cohort files: `cohort_82_mapping.csv` carries
  `symbol, accession, primary, protein, status, note, candidates`; `cohort_82_ecd.csv` carries
  geometry and bucketing. **No evidence-score column, no positive-label column.**

- **⚠ Correction to D-015 §2, from the source (D-016).** D-015 §2 states the target list and
  expression matrices are published as supplementary files S2 and S3. **True of the target list
  and the expression matrices; false of the evidence scores.** Read from the article text
  (`10.1371/journal.pone.0308604`, CC-BY, 2026-07-23):

  - **S2** — expression levels of the 82 prioritized targets across **44 normal tissues** (Fig 2A).
  - **S3** — expression levels across **20 tumor tissues** (Fig 2B).
  - **The 1–5 evidence scores are Fig 4A/4B** — a radar plot and a wordcloud. **The paper names
    no supplementary file for them.**

  So the scores exist as *figures*, not as a table. Recorded because the project has been
  carrying "the scores are in the supplement" as a fact, and it is not one.

- **What the article text does publish, exactly and quotably:**
  - **Score 5 — eight targets:** CD276, EDNRB, EGFR, ERBB2, FGFR3, MUC16, SLC39A6, SLC44A4.
  - **Score 4 — nine targets:** CLDN1, CXCR5, GPC1, ITGB5, MERTK, MMP14, MSLN, NECTIN4, SLC3A2.
  - **17 of 82 have exact scores from text. The remaining 65 do not.**
  - **Group B: the count is confirmed, the membership is not.** The paper states 22 of the 82
    have already been tested as ADCs preclinically or clinically, **naming only HER2, NECTIN4,
    and EGFR**, with 60 additional targets not used for ADC development. 22 + 60 = 82 partitions
    cleanly, so the count is sound and the roster is absent.
  - The five scoring criteria are fully specified in the methods (literature, antibody, protein
    family, preclinical, clinical; a target is kept if it meets at least one, and the score is
    the count of criteria met).

---

- **Decision (1) — Group B is DERIVED HERE, pre-registered, then CHECKED against the paper's 22.**

  Not inherited. The paper does not publish the roster, so inheriting is not available — but the
  ruling would be the same if it did, for a reason worth stating: **D-015 already treats the
  comparator as comparator-not-oracle**, and the labels the scorer fits against are the one place
  an inherited judgement would silently determine the result.

  **The definition is fixed before any target is classified** (the D-015 §3 pre-registration
  discipline, applied to labels rather than features):

  > **A cohort target is Group B if a molecule directed against that antigen has entered
  > preclinical or clinical development as an antibody-drug conjugate**, evidenced by a named
  > agent with a citable source. Antibodies that are not ADCs do **not** qualify (the paper
  > counts these under its *antibody* criterion, which is a different thing). Protein-family
  > precedent does **not** qualify — an ADC against a family member is not an ADC against this
  > target, and the paper scores that separately too.

  **Each label cites its own source**, exactly as D-029 requires of the antigen mapping.

  **The check is the finding.** If independent derivation lands on **22** and contains HER2,
  NECTIN4, and EGFR, that is mutual validation and **better provenance than an inherited list** —
  two independently-derived rosters agreeing. If it lands on a different number, **that is a
  result to record, not a discrepancy to reconcile away**: it means our definition and theirs
  differ, and the difference is nameable. Either outcome is reportable; neither is a failure.

- **Decision (2) — the evidence score is used at the resolution the source supports, and the
  gap is carried explicitly.**

  **17 targets carry a score from the article text.** The other 65 carry **null with a reason**
  (`score_not_published_in_text`) — the same discipline D-027 rules for uncomputable features and
  D-024 rules for `tier_reason`. **No score is read off a radar plot or a wordcloud into the
  dataset.** Figure extraction is estimation presented as measurement; a comparator built partly
  from pixel-reading would be a fabricated axis, and a disagreement computed against it would be
  uninterpretable.

  **Consequence, and it is severe enough to state plainly: the comparator covers 17 of 82.**
  Intersected with the 40 `ranked ∧ folded` targets, the set on which a *disagreement* can be
  computed at all is smaller still and **must be computed before the ranking view is designed**.
  D-024's coverage discipline applies to the comparator exactly as it applies to folds: the
  denominator travels with the claim.

  **Two ways to widen it, neither blocking, both preferred to estimation:**
  - **Ask the authors.** CC-BY, corresponding author published (`umesh@lanternpharma.com`). The
    scores are a small table they already computed. **Cheapest path to the full 82 and the
    highest-provenance one.**
  - **Recompute from the published criteria.** The five criteria are fully specified in the
    methods, so the score is reproducible in principle — but doing so makes it *our* score, not
    theirs, and it would then need its own entry and its own defence. **Not a substitute for the
    published values**; a separate instrument if ever built.

- **Decision (3) — one curated file, not two.** Group B labels and D-029's approved-ADC mapping
  are **the same judgement** — drug → target antigen → UniProt accession, hand-reviewed, each row
  cited — differing only in whether the accession falls inside the 82. Curating them separately
  would produce two files that can disagree about the same antigen.

  **`data/adc_reference_mapping.csv` gains the columns to carry both**, extending D-029's schema:

  | Column | From | Meaning |
  |---|---|---|
  | `drug`, `application_number`, `antigen`, `uniprot_accession`, `source_citation`, `marketing_status` | D-029 | unchanged |
  | `development_stage` | **this entry** | `approved` / `clinical` / `preclinical` — Group B admits preclinical; Group C is approvals |
  | `in_cohort_82` | **this entry** | computed against the cohort, not curated — **Group B ⊆ in-cohort; Group C ⊆ out-of-cohort** |

  **`in_cohort_82` is computed, never typed.** It is a join against `cohort_82_mapping.csv`, so
  a curation error cannot silently move a target between Group B and Group C — which are the
  labelled set and the sharpest evaluation instrument respectively.

  **D-029's seam is preserved and extended:** openFDA is authority for **approval status only**;
  every antigen assignment and every development-stage judgement is **a reviewed human judgement,
  not FDA-sourced**, and must be labelled as such wherever surfaced. Group B rows are further
  from FDA data than Group C rows are — a preclinical ADC has no application number at all — so
  the seam matters *more* here, not less.

---

- **⚠ Recorded before the labels exist: how many Group B positives fall inside the folded 40 is
  UNKNOWN.** D-027 sized six features against 22 positives (~3.7 per feature, called "the upper
  end of what this labelled set supports"). **The scorer can only be fit on targets that are both
  labelled and folded.** If materially fewer than 22 Group B targets are in the folded 40, the
  fit is thinner than the pre-registration assumed. **Compute this number immediately after the
  labels land, before any fitting**, and if it is small, that is a finding for the log and
  possibly a reason to wait on the rental fold — not a reason to proceed quietly.

- **Deep-learning justification.** Direct and load-bearing. Group B **is** the training signal:
  every property of the fit — what it learns, whether leave-one-out means anything, whether a
  disagreement is real — is downstream of these labels. A pre-registered, independently derived,
  per-row-cited label set is what makes the fit falsifiable rather than circular. And the
  evidence score is the axis the structural ranking is compared against; **a comparator estimated
  from a figure would make every disagreement uninterpretable**, which would defeat D-015 §1's
  research question entirely.

- **Consequences / test surface:**
  - **Tested first:** the Group B definition is applied by a pure function over the curated file
    (fixture-testable, no network); `in_cohort_82` is computed by join and a hand-typed value is
    rejected; a row without `source_citation` fails; targets with no published evidence score
    carry **null with a reason** and **no imputation exists anywhere in the pipeline**.
  - **A test pinning the derived Group B count**, so a curation change that moves it is visible.
  - **The comparator's coverage — 17 of 82, and the labelled ∧ folded intersection — is reported
    with any ranking** (D-024), not stated once in a methods note.
  - **D-015 §2's S2/S3 claim is corrected in this change.**
  - **The reconciliation core (D-029) is unaffected** — it gains columns, not new behaviour.
  - **Attribution:** Kathad et al. 2024, `10.1371/journal.pone.0308604`, CC-BY 4.0. Reuse
    permitted with credit; the citation travels with the data file, not only the log.

---

### D-039 — pLDDT confidence bands: 50/60/70, convention-anchored and cohort-justified
- **Date:** 2026-07-23
- **Status:** **Accepted (2026-07-23)** — owner-ruled on review of the Builder's proposal (the
  boundaries and two-source justification approved; two label corrections applied below).
- **Context:** The target view (UI Plan v2 §3.2) renders `mean_plddt`, and §2/§10 rule a bare
  number is insufficient — a 34.78 structure must not read like NECTIN4's 77.26 (the D-024 failure
  in miniature). The bands are the interpretive frame; their boundaries carry a claim about how far
  to trust a structure and are **cited by the UI**, so they are a decision, not a component
  constant — a later change must be visible.
- **Decision — four bands, boundaries at 50 / 60 / 70:**

  | Band | Label |
  |---|---|
  | **>= 70** | Confident backbone (cohort max 81.4 - no target reaches the high-confidence range) |
  | **60-69** | Moderate |
  | **50-59** | Low - backbone unreliable |
  | **< 50** | Very low - not reliably interpretable |

- **Two-source justification (stronger than either alone).** Convention anchors the edges —
  ESMFold/AlphaFold treat >= 70 as a reliable backbone and < 50 as very low — while the **60 line
  is justified by this cohort's own measured mass**: of the 42 folded targets, **24% fall below 50,
  45% below 60, 57% below 70** (computed over all 42 `mean_plddt`, live `/api/analyses`). 60 is the
  honest "how far to trust this" divider the D-024 coverage story turns on, and it is the cohort's,
  not a convention's.
- **Two label disciplines (owner corrections to the proposal):**
  - **"Confident backbone," not "Confident."** pLDDT is a *self-reported* confidence about *local
    backbone geometry*; it says nothing about whether the fold is *correct*, and ESMFold's
    confidence is not calibrated against experimental structures for these targets. The qualifier
    keeps the claim where the metric lives — the same attribution-not-explanation discipline as
    D-028.
  - **The cohort-max caveat travels in the band, not only here.** No target exceeds **81.4**, so
    ">= 70" in this cohort means 70-81.4 and **there is no high-confidence tier at all.** A reader
    seeing "Confident" on the top band could assume some targets are excellent; none are. The caveat
    is surfaced where it is read (the target view's confidence element), not buried in this entry.
- **Deep-learning justification:** direct, via D-024/D-028. pLDDT is the network's *own* confidence
  output; rendering it as a bare number invites ranking on it and reading it as correctness. The
  bands make the model's self-report legible *as a self-report*, with its ceiling visible — which is
  what keeps the structure viewer honest about a network output this project runs itself.
- **Consequences:** cited by the target view's confidence element (PR B) and available to the
  coverage view (PR C). Per-residue colouring uses the same band scheme, **from the `/plddt`
  array — never the PDB B-factor column**, whose 0-100-vs-0-1 scale is unverified (S-001 cost real
  confusion on exactly that rescaling, D-016 method note). A later change to a boundary is a
  visible, ruled change, not a silent constant edit.

---

### DEP-006 — The serving image gains a build stage and a static-serve path

- **Date:** 2026-07-23
- **Status:** Proposed → Accepted on merge with the bundle.
- **Amends:** DEP-001 (*"what the Fly image contains, and what it must never contain"*), whose
  own consequence named this: *"When Streamlit lands, both this entry and the image change
  together"* — now React per D-033, which said the same: *"A React UI adds a build step (bundle)
  and a static-serve path, which is a DEP-001 amendment at that time."*
- **Context:** The image today is single-stage: `python:3.11-slim`, `requirements.lock` with
  `--require-hashes`, then `COPY app/ core/ db/`. A React bundle needs Node at **build** time and
  nothing at **run** time — a distinction the image must express, or the CUDA-free serving tier
  acquires a JS toolchain it never executes.

- **Decision — a two-stage build; the runtime stage stays exactly as ruled.**
  1. **Stage 1 (`node:20-slim`, build only):** `COPY ui/package.json ui/package-lock.json`,
     `npm ci`, `COPY ui/`, `npm run build` → static assets.
  2. **Stage 2 (`python:3.11-slim`, the runtime):** unchanged in every respect DEP-001 ruled —
     runtime lock with `--require-hashes`, `app/` + `core/` + `db/`, **no `worker/`, no torch** —
     plus `COPY --from=0` of the built assets only.

  **Node never enters the runtime image.** The built assets are static files; the serving tier
  remains Python + the hash-locked runtime lock.

- **Serving the bundle:** FastAPI mounts the static directory and serves `index.html` as the
  SPA fallback. **`/api` and `/jobs` are matched first** — a catch-all that swallowed `/api`
  would break the read API silently, so route ordering is the thing to assert, not eyeball.

- **⚠ Three constraints in the existing tree that this must not break** (verified, not assumed):
  - **`tests/test_image_contents.py` forbids the literal strings** `torch`, `transformers`,
    `bitsandbytes`, **and `streamlit`** anywhere in the Dockerfile's non-comment lines. React is
    none of these, so the test passes unchanged — **and it must keep passing unchanged.** Do not
    weaken it to accommodate the build stage.
  - **`test_copies_the_serving_packages`** asserts `copy app`, `copy core`, `copy db` are
    present. The two-stage rewrite must keep all three in the runtime stage.
  - **`.dockerignore` excludes `tests/`, `docs/`, `scripts/`, `worker/`.** A new `ui/` directory
    must **not** be added to it (stage 1 needs it), but `ui/node_modules/` and `ui/dist/`
    **must** be, or the build context balloons.

- **Test surface:** extend `test_image_contents.py` — the runtime stage still copies
  `app`/`core`/`db`; **no `npm` or `node` instruction appears after the runtime `FROM`**; the
  forbidden-string set is unchanged and still passes. Plus a route-ordering test: `GET /api/analyses`
  returns the API's JSON, **not** `index.html`.

- **Deep-learning justification:** indirect — the same separation-of-worlds DEP-001 exists to
  enforce, one tier out. A serving image that acquired a JS runtime it never executes is the
  same invisible-bloat failure as one that acquired CUDA.

- **Consequences:** DEP-004's meaning changes on this merge — **a green deploy will finally mean
  a UI is reachable**, which it has never meant before. That is DEP-004's own stated trigger
  (*"the first UI to ship amends what a green deploy means"*) and it is amended in the same PR.

---

### D-037 — The JS toolchain is pinned by lockfile, outside D-013's hash-verified guarantee

- **Date:** 2026-07-23
- **Status:** Proposed → Accepted on merge with the bundle.
- **Context:** D-033 flagged this precisely and left it open: *"No new runtime Python dependency.
  React is a build-time toolchain producing static assets; it does not enter `requirements.lock`.
  The JS toolchain's own pinning is a question for the entry that builds the UI, and it is
  **outside D-013's guarantee** in the same way `worker/requirements.txt` is (D-018) — stated now
  so it is not discovered later."* This is that entry.

- **Decision — `package-lock.json`, committed, installed with `npm ci`.**
  - **`npm ci`, never `npm install`, in the Dockerfile and in CI.** `ci` installs exactly the
    lockfile and **fails** if `package.json` and the lock disagree; `install` silently resolves
    and rewrites. That difference is the whole guarantee.
  - **The lockfile is committed** and treated as a source file — a dependency change is a
    reviewable diff, not a build-time surprise.

- **What this does NOT provide, stated plainly so it is not over-read.** D-013 gives the Python
  runtime tier **hash-verified** installs (`--require-hashes`) enforced identically in CI and the
  image. `npm ci` gives **version and integrity pinning from the lockfile**, which is weaker:
  the guarantee is "the same tree the lockfile records," not "hashes verified against a
  separately committed manifest." **The JS toolchain is therefore a third dependency world**,
  alongside the hash-locked runtime tier (D-013) and the unlocked GPU tier (D-018).

  **Why accept the weaker guarantee rather than build a stronger one:** the JS toolchain is
  **build-time only** — nothing it installs ships to the runtime image (DEP-006), so a compromised
  or drifted build dependency affects the *bundle produced*, not the *server running*. That is a
  materially smaller blast radius than the runtime tier's, and it is the reason the asymmetry is
  acceptable rather than an oversight. **It is not zero**, and this entry is where that is
  recorded rather than discovered.

- **Deep-learning justification:** neutral — build tooling. Recorded because D-013's guarantee is
  cited elsewhere in this log as though it covered the project's dependencies generally; it
  covers the runtime tier. **Two named exceptions now exist: D-018 (GPU) and this entry (JS).**

- **Test surface:** CI runs `npm ci` (not `install`); `package-lock.json` exists and is committed;
  the build fails if the lock and `package.json` disagree — which `npm ci` provides by
  construction, so the assertion is that the CI step uses `ci`.

- **Consequences:**
  - **Dependency count is a design constraint, not an afterthought.** Every added JS dependency
    enters a world with a weaker guarantee than the Python tier's. **3Dmol.js is required**
    (D-033). Beyond React, the router, and 3Dmol.js, additions should be justified rather than
    assumed — a chart library for the per-residue pLDDT plot is a real question, and hand-rolled
    SVG is a legitimate answer for a single plot type.
  - `requirements.lock` and `requirements-dev.lock` are **unchanged** — no Python dependency is
    added by the UI.

---

### D-038 — The coverage supplier: `GET /api/coverage`, computed from the manifest, joined to folds
- **Date:** 2026-07-23
- **Status:** Proposed → Accepted on merge.
- **Context — a supplier gap the Planner specced past, caught by the Builder against the tree.**
  UI Plan v2 §3.3/§4.1 specify a coverage surface showing *"the full 82: what is ranked, what is
  held out and why, what is excluded and why by name, what is folded and what is not yet."*
  **Nothing serves that data.**

  `GET /api/analyses` (D-034) returns the **42 folded rows** and structurally cannot supply:
  - the **denominator 82** — `protein_analyses` contains only rows that were enqueued;
  - the **excluded targets by name** (MUC16, FAT2) — D-026 gives them **no `protein_analyses`
    row at all**, so they are not missing from a response, they are missing from the *table*;
  - the **29 rental-tier unfolded** — not enqueued, and a fold-derived table has no
    representation for "not yet."

  **This is the same supplier-before-contract failure D-034 was written to avoid, one surface
  over** — caught for the target view, missed for the coverage view. Left unfixed, React would
  reconstruct a partial line from 42 folded rows and quietly lose the *"of 82,"* which is the
  whole point of D-024. **A coverage line that is confidently wrong is worse than none**: D-024
  exists because *"N ranked, M held out" travels with every ranking*, and a denominator of 42
  would misstate the cohort in the direction of completeness.

- **Provenance (D-016):** ruled against `core/manifest.py` (`coverage()` at :185, `ManifestRow`,
  `build_manifest`), `app/read_routes.py` as shipped in #52, and `GET /api/analyses` verified live
  returning 42 rows with dispositions `ranked` and `held_out` only. *(Tidy 2026-07-23: this line
  originally named `build_rows`; the function is `build_manifest`. Nothing load-bearing rested on
  it — the ninth correction of the session, recorded per D-016 rather than silently fixed.)*

---

- **Decision — `GET /api/coverage`, unauthenticated, under `/api` (D-034's posture unchanged).**

  **The cohort is the manifest, not the database.** The route computes `ManifestRow`s from the
  committed cohort data (`data/cohort_82_ecd.csv` and its companions) exactly as
  `core/manifest.py` already does — the same deterministic routing table D-023 made reviewable —
  and returns `coverage(rows)`'s object plus the per-row detail the drill-down needs.

  **Why the manifest is the source and the DB is the join, not the reverse:** the manifest is the
  only artefact that knows about all 82. It is deterministic, committed, and already
  test-covered. `protein_analyses` knows only what was enqueued and folded. **Reading coverage
  from the DB would make the denominator a function of how much work has happened**, which is
  precisely the failure D-024 forbids.

  **Payload:**
  - **`coverage`** — `coverage()`'s object verbatim: `denominator`, the three-cell partition
    (`ranked` / `held_out` / `excluded`), and the two breakout subsets (`unmeasured_tier`,
    `no_topology`). **The breakouts are subsets that cut across the partition and are NOT summed
    into it** — the response must not invite a client to add them.
  - **`rows`** — per target: `accession`, `gene`, `boundary_method`, `span`, `tier`,
    `tier_reason`, `disposition`, `excluded`, plus **`fold_status`** and **`analysis_id`**.
  - **`fold_status`** is the one field neither source has alone, and it is the reason this route
    joins rather than merely echoing the manifest: `folded` when a completed
    `protein_analyses` row exists for that accession, `not_folded` otherwise. Today that yields
    **42 folded, 40 not** — the honest partial state.

  **Exclusion reasons are carried, not just the flag.** D-022's requirement is that named
  exclusions are *visible*, and a boolean is not a reason. Where the manifest records why a
  target was excluded, that text travels in the row.

- **⚠ The join key is `accession`, and that is a deliberate choice with a caveat.**
  `protein_analyses.input_value` holds the accession; there is no accession *column* (the
  D-034 finding). The join is therefore on `input_value` for `input_type == 'uniprot'`. This is
  correct for the current cohort — every row is a uniprot input — and it is **stated here so
  that a future non-uniprot input type does not silently break the coverage count.**

- **Cost:** the manifest computation is CPU-only over 82 rows from committed CSVs, plus one
  indexed query. No new dependency, no new table.

- **Deep-learning justification:** direct, via D-024. The coverage line is the surface that keeps
  the scorer's eventual claim honest — *"N of 82 ranked"* is what prevents a ranking over 40
  folded targets reading as a ranking over the cohort. A supplier that could only report what had
  already been folded would make the denominator grow as work progressed, which is the
  self-flattering failure the entry exists to prevent. **The number that disqualifies you is the
  one worth serving.**

- **Consequences / test surface:**
  - **Tested first:** the partition sums to `denominator`; the breakouts are **not** summed into
    it; excluded targets appear **by name** with their reason; `fold_status` reflects the DB join
    (a seeded folded row reads `folded`, an unenqueued target reads `not_folded`); the route is
    unauthenticated and **D-034's prefix property still holds** (`/api` open, `/jobs` guarded).
  - **A test pinning the denominator at 82** — so a cohort-data edit that changes it is a
    deliberate, visible change rather than a drift.
  - **Blocks UI Plan v2 step 4** (coverage view). Step 3 (target view) is unaffected.
  - **`core/manifest.py` is not modified** — the route consumes it. If the manifest needs a
    change to be importable from `app/`, that is worth noting rather than refactoring past.
  - **DEP-001/DEP-006:** `data/` must be present in the serving image for the manifest to
    compute. **The image does not copy `data/` today** — verify and add it in the same PR, or the
    route works locally and 500s in production.

---

### D-036 — The PAE transfer route: a fifth worker route, not a widened upload
- **Date:** 2026-07-23
- **Status:** **Accepted (2026-07-23)** — the transfer-shape ruling D-035 §4 deferred; the route
  (option A) over a `fly ssh sftp` script.
- **Context:** D-035 rules PAE leaves the claim→complete cycle (option C) and is retrieved
  out-of-band, but deferred the *mechanism*. The rented A6000 is **not** a Fly machine, so PAE
  reaches the Volume only through one. Two shapes were weighed (D-035 §4 ruling 2): a dedicated
  route vs an `fly ssh sftp` script.
- **Decision:** a **fifth** worker→Fly route, **`POST /jobs/{job_id}/pae`**, bearer-guarded under
  `/jobs`.
  - **Body:** the gzipped PAE (`pae.json.gz`) — the same wire form the upload route accepted
    before D-035 part 2 stripped it.
  - **Semantics:** writes the Volume file **and** `pae_json_path` in the compensated Volume+DB
    boundary `persist_fold` already establishes (D-031 (a)) — file first, then the DB row,
    compensating by deleting the file if the DB write fails. **File and column cannot diverge.**
    Scoped to the PAE file: the `{job_id}/` dir already holds the fold's
    structure/plddt/provenance from the original upload, so compensation removes only
    `pae.json.gz`, never the directory.
  - **Idempotent:** a retried transfer re-writes the same path and re-stamps the same column
    (D-031's obligation, unchanged) — the property the retrieval script's re-run relies on.
  - **Not by widening (D-030 discipline):** the upload route keeps `pae` as an unused `Optional`
    and no longer receives it; the transfer is **its own route**, not an overload of `/artifacts`.
    *"A fifth route, not by widening an existing one."*
  - **Auth / prefix property (D-034 decision 5):** bearer-guarded under `/jobs`, so the
    introspecting auth test still classifies every route (`/jobs` guarded, `/api` open, no third
    category) — now with **five** `/jobs` routes and **four** `/api` routes. **Asserted, not
    assumed** (D-035 part 2 test surface §3).
- **Why a route rather than sftp:** reuses the compensated boundary (file/column cannot diverge),
  hermetically testable, idempotent by construction. The cost is a permanent surface for a
  one-time batch — accepted, because an untestable transfer that silently half-completes is the
  worse failure (D-035 §4 ruling 2).
- **Deep-learning justification:** indirect. PAE is the retained confidence artifact that keeps a
  future PAE-derived feature (D-027, deferred-not-dismissed) reachable without a **paid re-fold**
  of the cohort. The route is what makes the rental cohort's PAE durable under D-011's
  no-network-volumes rule.
- **Consequences:**
  - Lands with **D-035 part 2 as one PR** — the rental-scoped local persist, this route, and the
    upload change are only safe together (removing PAE from the upload before the local write and
    this route exist is the silent-drop window).
  - `app/artifacts.persist_pae` mirrors `persist_fold`'s compensation, scoped to `pae.json.gz`;
    `app/routes.py` gains the thin handler; `worker/http_client.upload` stops sending PAE (the
    runner still *produces* it — untouched).
  - Local persist is **rental-scoped/opt-in** (`WORKER_ARTIFACT_DIR`), **PAE-only**, wired into
    `worker/main.py`'s fold wrapper so `orchestrator.run_worker` stays pure; **non-fatal** on a
    local write error (logged) so it cannot cascade into a paid re-fold — the retrieval-verify
    step is the backstop.
  - The retrieval script (`scripts/retrieve_rental_pae.py`) POSTs each local `pae.json` gzipped to
    this route; the run guide states the **blocking pre-termination retrieval** in loss terms.
  - ARCHITECTURE's transport row becomes **five routes**.

---

### D-035 — The rental tier: PAE leaves the lease, and three hazards the measured gzip ratio exposed
- **Date:** 2026-07-23
- **Status:** **Accepted (2026-07-23)** — owner-ruled on the PAE path (§4, option C); §1 stands
  on measurement alone; §3's hazards ruled as stated.
- **Supersedes in part:** D-030's PAE upload reasoning (the 5–10× gzip estimate and the
  "inside the lease" conclusion it supported). D-030's *compress-and-store intent* is preserved
  and, under this entry, better served.
- **Closes:** D-011's open follow-up — *"decide where rented-run artifacts land (Fly Volume
  upload path, D-004 consequence, still open)."*

---

#### 0. Provenance (D-016)

Ruled against tree `0bc9258` (`worker/orchestrator.py`, `worker/http_client.py`,
`worker/runner.py`, `worker/main.py`, `fly.toml`, `core/manifest.py`), the production database
and Volume queried 2026-07-23, and D-011 / D-030 / D-031 read in full.

**The A6000 has not been rented and no rental fold has ever run.** Every claim below about
rental behaviour is *predicted* or *derived*, never *measured*, and is labelled (method note
item 3). The one measurement is the gzip ratio, and it is measured only at 318/361 aa.

---

#### 1. The 5–10× gzip estimate is falsified, and it was load-bearing

**Not a refinement of an estimate — the collapse of the argument a ruling rested on.**

D-030's PAE ruling reasoned in a chain: raw PAE for 2213 aa ≈ 75–100 MB → *"plausibly 30–80
minutes on a residential uplink"* → *"could exceed the 3600 s provisional lease before the fold
is even counted"* → **but gzip achieves 5–10×** → ~10–20 MB → *"at that size the upload is a few
minutes, **inside the lease**."* The entry labelled the ratio *"an estimate, not a measurement"*
and named its retirement: the first large fold.

**Measured: 2.2×** — 824,489 B gzipped from ~1.8 MB raw (`ls -l /data/artifacts/1/`, id 1,
318 aa); 1,070,270 B at id 37 (361 aa).

| Target | Raw PAE (est.) | At 5–10× (assumed) | At 2.2× (measured ratio) |
|---|---|---|---|
| 1652 aa (NOTCH2) | ~42–56 MB | 4–11 MB | **~19–25 MB** |
| 2213 aa | ~75–100 MB | 10–20 MB | **~34–45 MB** |

Applying D-030's own uplink figure (30–80 min for 75–100 MB ≈ 1.0–1.6 MB/min), 34–45 MB is
**~21–45 minutes of upload alone**, against a 3600 s lease whose clock starts at `claimed_at` —
*before* the worker has received the response, folded, or begun uploading. The fold is
unbudgeted in that window.

**The honest reading:** the measurement does not make the lease tighter; it removes the step that
concluded *"inside the lease."* The 3600 s provisional threshold is **under-justified for exactly
the tier it was raised to protect.** D-030 anticipated this structurally — *"a fixed timeout has
no correct value once fold durations are long or variable… the structural fix is a lease
heartbeat… flagged for its own entry"* — and this measurement is the trigger it named.

> **⚠ Inference status.** 2.2× is **measured** at 318/361 aa. That it holds at 1652–2213 aa is
> **assumed** — PAE is L×L and compression behaviour on a far larger float matrix is not
> established by two small samples. The uplink figure is D-030's **estimate**, never measured.
> The table is therefore *derived from one measurement and two unmeasured inputs*; its
> conclusion is **"the argument no longer closes,"** not "the upload will take 21–45 minutes."

---

#### 2. What the rental tier is — a framing correction with Prime-Directive stakes

The session opened with "build an API to a rented service." **D-011 does not describe a service
with an API.** It rules a *one-time batch* of **"committed, reproducible code in this repo"**
(the binding condition of D-009 §3), and D-004 §5 rules **out** "call a hosted inference API."
D-011's deep-learning justification turns on precisely this line:

> *"Renting a GPU changes whose silicon executes the model, not who runs it… categorically
> different from calling a hosted inference API… The graded DL claim is unaffected."*

**So the rental tier is not something we build an API *to*. It is the existing worker loop
running on a rented box, calling the same four transport routes.** `worker/orchestrator.py` is
transport-agnostic; `worker/http_client.py` already speaks the protocol; a rented A6000 runs
`python -m worker.main` against `pharmfoldmdk.fly.dev` exactly as the local box does. The tier
difference lives in the **FoldSpec** (fp16, unquantised, unchunked — D-011) and in **nothing
about the transport**.

**Why this is not pedantry:** if the rental tier were a hosted folding API, CLAUDE.md's Prime
Directive would be in play — it forbids shipping "only a wrapper around an external service."
The two readings of "rental API" are a defensible graded deliverable and an indefensible one.

---

#### 3. Three hazards the rental tier hits that the local tier structurally cannot expose

Every fold to date is ≤361 aa on a local box. None of these is guarded by a test; none had been
ruled.

**(a) There is no HTTP timeout anywhere in the client — RULED: set one explicitly.**
`worker/http_client.py:34` constructs `httpx.Client(base_url=base_url)` with **no `timeout`**.
httpx defaults to 5 s on connect/read/write/pool. `_post` catches `httpx.HTTPError` → raises
`TransportError` → the loop treats it as **retryable**, so a slow upload times out, retries,
exhausts `submit_attempts`, and the job reaps and **re-folds on a paid card** — the exact cost
D-030 named (*"a retry bug re-folds NOTCH2 up to three times on a paid card"*).

**RULED: `httpx.Timeout(connect=10.0, read=300.0, write=300.0, pool=10.0)`.** A short connect
timeout (a dead endpoint should fail fast) and a 5-minute read/write (an upload in progress is
not a hung connection). **This fix lands regardless of §4** — it is independent of PAE size, and
under option C a ~1 MB upload on a marginal uplink is still where an intermittent retry loop on
a paid card comes from.

**(b) Fly's request body limit is unruled and unverified — RULED: verify once, cost zero.**
D-031 listed *"upload size limits"* as its concern and appears not to have ruled a number;
`fly.toml` sets none. Under option C the rental upload is ~1 MB and any plausible limit passes,
so this stops being a gate before paid time — **but it is still a fact nobody on this project
has established.** A synthetic POST to `/jobs/{id}/artifacts` against prod settles it for free.

**(c) The 512 MB transport machine buffers whole bodies — RULED: no change, with the coupling
recorded.** `app/routes.py:artifacts` does `await pae.read()` (whole body into memory) on a
`memory = "512mb"` machine. **Option C removes the pressure** — the largest upload becomes ~1 MB.
The coupling between `[[vm]] memory` and max upload size is written down here so that raising
one without the other is a visible mistake rather than a silent one. **If PAE ever returns to
the upload path, this becomes live again.**

---

#### 4. RULED — PAE leaves the lease and is retrieved out-of-band (option C)

**The claim→complete cycle uploads `structure.pdb` + `plddt.json` + `provenance.json` only
(~1 MB even at 2213 aa). PAE is written to the rented box's local disk by a rental-scoped
local-persist step wired into the loop — which does not exist today and is built by this entry —
and transferred separately, in bulk, before pod termination via a dedicated retrieval route.**

**⚠ Correction, verified at the tree and ratified 2026-07-23 — the seventh correction of the
day and the most consequential.** `runner.write_artifacts` exists and is tested but has **no
production caller** (verified: only `tests/test_runner.py:102,117`; `run_worker` folds in memory
then uploads, `worker/main.py` adds no local write). The Planner's draft asserted this local
persistence already happened; **it does not.** Had §1(b) landed on that premise, rental PAE would
have existed only in `FoldResult.pae` and been discarded when the loop claimed the next job —
**silent, unrecoverable loss on a paid fold**, precisely the §1(c) hazard, one layer deeper than
the draft looked. *Function exists ≠ function runs* — a true statement with a false implication,
the pattern this log exists to catch (method note item 4; cf. `params_all_on_cuda=True`). The
Builder checked the claim against the tree instead of building it, which cost one exchange
instead of a paid re-fold of 29 targets.

**Why this shape rather than the two obvious alternatives:**

- **vs. building the heartbeat now:** the heartbeat is D-030's correct long-term fix and it is
  not retired here — but building it to protect an upload the pipeline does not need is solving
  a self-inflicted problem. **If a real reap of live work occurs, the heartbeat lands then, on
  evidence.**
- **vs. simply dropping rental PAE (option B, the Planner's first recommendation):** B was
  ruled against by the owner **on uniformity grounds**, and the objection is sound. B leaves the
  cohort split — 42 local rows with `pae_json_path` populated, 29 rental rows null — which is a
  provenance asymmetry the coverage line would have to carry forever, and it forecloses any
  future cohort-wide PAE consumer without a **paid re-fold**.

  > **Recorded honestly:** the Planner argued PAE is unread (Builder-verified against `main`:
  > only the producer and a nullable column no code reads; D-027 rejected the one PAE-derived
  > feature) and that "uniform" is partly illusory anyway, since **local PAE is int8/chunk-64 and
  > rental PAE is fp16/unchunked** — a cohort-wide PAE analysis would compare two inference
  > regimes. Both points stand. The owner's ruling is that preserving the option is worth ~1 hour
  > of pod time, and **option C obtains uniformity without re-opening §1 or §3 at all**, which is
  > why it supersedes both earlier options rather than splitting the difference.

**What this buys, stated as the reason it was chosen:** the lease pressure, the write-timeout
exposure, the body-limit question, and the 512 MB memory coupling are **all consequences of one
thing — PAE size inside the claim→complete cycle.** Moving PAE out of that cycle dissolves four
problems at once *and* keeps the artifact. Nothing is traded away except an operational step.

**The operational step is real and is named, not assumed.** D-011 rules **no network volumes**
(*"download weights, fold, upload artifacts, terminate"*), so PAE on container disk is
**destroyed on termination**. Retrieval is therefore a **blocking pre-termination step**, not a
convenience: the batch is not done when the last fold completes; it is done when PAE is off the
box. The rented machine's uplink is datacentre-grade, so ~0.6–1.3 GB is minutes, not the hours
the same transfer would take from the house — which is the whole reason this option costs almost
nothing.

**Ruled mechanism (2026-07-23, three rulings):**

1. **A dedicated fifth transport route — `POST /jobs/{id}/pae` — not a widening of the upload
   route** (D-030's discipline: *a fifth route, not by widening an existing one*). It writes the
   gzipped PAE to the Volume and sets `pae_json_path` in the **same `persist_fold`-style
   compensated Volume+DB boundary** (D-031 (a)), so the file and the column cannot diverge;
   idempotent (a re-run after a partial transfer converges); bearer-guarded like the other four,
   so D-034's prefix property holds unchanged (`/jobs` guarded, `/api` open, no third category).
   Chosen over a `fly ssh sftp` script because the route is **hermetically testable and atomic**
   where the script is neither; a route that outlives its one-time batch is a smaller cost than an
   untestable transfer that silently half-completes.
2. **Local persistence is rental-scoped and opt-in.** The loop persists PAE to
   `{WORKER_ARTIFACT_DIR}/{job_id}/` **only when `WORKER_ARTIFACT_DIR` is set** — local-tier
   behaviour and disk cost are unchanged, and `write_artifacts` finally gets its production
   caller. A **PAE-only** write: `structure`/`plddt`/`provenance` already persist server-side via
   upload, so duplicating them on the pod buys nothing.
3. **Sequencing (part 1 / part 2).** §3(a)'s timeout fix, the D-030/D-031 amendments, and the
   ARCHITECTURE row are independent and land first (**part 1**). §1(b) (upload omits PAE) + the
   rental-scoped local-persist wiring + the new route land **together** (**part 2**) — removing
   PAE from the upload before the local write and the route exist is exactly the silent-drop
   window this correction exposed.

**Landing location:** the Fly Volume, under each analysis's existing artifact directory, so the
rental cohort's on-disk shape matches the local cohort's. **`pae_json_path` is populated for
every row in both tiers** — the uniformity the ruling exists to obtain.

---

#### 5. Deep-learning justification

Direct, and it is why §2's correction matters. D-011's DL claim survives renting *silicon*
because we control the checkpoint, precision, chunking, and code, and we perform the inference —
the distinction the Prime Directive turns on. An entry that built "an API to a rented folding
service" would trade a defensible graded claim for a wrapper around an external service (D-004
§5). The rental tier is also what folds the 29 above-ceiling targets, moving the coverage line
(D-024) from **40/82 to 69/82 ranked-and-folded** and supplying the extractor (D-027).

---

#### 6. Consequences / follow-ups

- **Coverage is unchanged by the PAE ruling.** All 29 rental targets fold and land either way;
  PAE is a confidence matrix shipped *alongside* the structure, not the structure. The 13
  no-topology rows remain unfoldable by any tier (D-021 §1a) — **the rental cohort is 29**
  (13 `unmeasured_local_ceiling` + 16 `over_local_ceiling`), not 42.
- **D-030 is amended:** the 5–10× estimate is falsified at 2.2×; `DEFAULT_STALE_SECONDS = 3600`
  **stays PROVISIONAL with its justification recorded as weakened, not retired.** This entry
  does not change the number — it removes the reasoning that made it look safe, and option C
  restores the margin by a different route.
- **D-031's PAE ruling is amended** with the measured ratio in place of the estimate.
- **The heartbeat remains unbuilt and its trigger is restated:** any observed reap of live work,
  or PAE returning to the upload path.
- **D-034 (the read API) needs no change.** Rental folds land in the same table with the same
  `meta` shape and a populated `pae_json_path`. No PAE route exists and none is added.
- **Test surface (written before the code):** the client sets an explicit timeout (assert the
  configured `httpx.Timeout`, not the default); `upload` omits PAE while a **rental-scoped**
  local-persist step (`WORKER_ARTIFACT_DIR` set → `write_artifacts`, its first production caller)
  writes `pae.json` to the pod disk (the two must not be coupled); the loop's existing guarantees
  are unchanged (fold once per claim; upload before complete).
- **Sequencing:** §3(a)'s timeout fix and the upload change are ordinary PRs through the gate.
  **Neither requires the A6000**, so both land before any paid time is bought.

---

### D-034 — The read API: route shape, PDB serving, and an asymmetric auth posture
- **Date:** 2026-07-23
- **Status:** **Accepted (2026-07-23)** — owner-ruled on auth posture and co-serving; the
  route shape and payload split are ruled against the measured cohort below.
- **Context:** D-033 ruled the UI is React consuming the FastAPI API. **There is no API for it
  to consume.** `app/` exposes exactly the four worker→Fly routes (claim/artifacts/complete/fail,
  D-031) and zero read routes — verified against the tree at `0bc9258`: `app/routes.py` defines
  four `@router.post` handlers and no `@router.get`. React cannot be specced against an API that
  does not exist, so the read API is the UI arc's first build, and its shape is ruled before it
  is written.

  **Provenance (D-016) — this entry is ruled against the landed cohort, not against intent.**
  Every number below comes from the production database and Volume, queried 2026-07-23:

  | Claim | How it is known |
  |---|---|
  | 42 jobs, all `complete`, zero `failed` | `Counter(SELECT status FROM jobs)` → `{'complete': 42}` |
  | 42 `protein_analyses` rows, no null artifacts | `SELECT id,input_value,mean_plddt,pdb_path,pae_json_path…` — all 42 populated |
  | 40 `ranked`/`sliced_ecd` + 2 `held_out`/`whole`, all `local` | `Counter` over `metadata->>'disposition'`, `->>'tier'`, `->>'boundary_method'` |
  | `structure.pdb` 194 KB (318 aa) / 232 KB (361 aa) | `fly ssh console -C "ls -l /data/artifacts/1/ /data/artifacts/37/"` |
  | `pae.json.gz` 824 KB / 1.07 MB; `plddt.json` ~6 KB; total Volume 21 MB | same `ls -l`; `du -sh /data/artifacts` → `21M` |
  | mean pLDDT range 34.78–81.40 across the 42 | the `mean_plddt` column, all rows |

- **A correction to a number this project has repeated (D-016 pattern, fourth instance).**
  `docs/RUNGUIDE-startup-and-local-batch.md` says the local batch is **40 targets**. The batch
  landed **42**, and the two extras (`Q9NV96`/TMEM30A, `O14798`) are not errors: they are
  `held_out: true`, `boundary_method: "whole"`, `tier: "local"`. The guide's 40 counted
  *ranked-and-local*; `core.enqueue --bucket local` correctly filters on **tier**, and tier is
  orthogonal to disposition (D-024 iv, as `core/manifest.py`'s own docstring states). The
  number was true and its denominator was wrong — the same failure class as
  `params_all_on_cuda=True`. **`--bucket local` means 42, not 40**; the run guide is corrected
  in this change.

---

- **Decision (1) — two payload shapes, because `meta` is rich and `sequence` is heavy.**
  `metadata` carries a uniform key set on every row (verified on ids 1 and 37): `gene`, `label`,
  `tier`, `source`, `held_out`, `disposition`, `boundary_method`, `fold_length`, `full_length`,
  `ecd_start`/`ecd_end`, `uniprot_release`, `sequence`, and a complete `fold_provenance`
  (`model_id`, `model_revision`, `dtype`, `chunk_size`, `truncated`, `folded_at`, `mean_plddt`,
  `input_length`, `ca_atom_count`).

  - **`GET /api/analyses` — a light list.** Per row: `id`, `accession` (`input_value`), `label`,
    `gene`, `mean_plddt`, `disposition`, `held_out`, `tier`, `tier_reason`, `boundary_method`,
    `fold_length`, `full_length`. **Excludes `sequence` and `fold_provenance`.**
  - **`GET /api/analyses/{id}` — the full record**, including `sequence` and `fold_provenance`.

  **Why split rather than return the row:** `meta.sequence` is the entire folded sequence —
  318 and 361 residues on the two rows inspected, and rental-tier targets run to ~1600. Returning
  full `meta` for 42 rows ships tens of KB of sequence that a ranking table never renders, and
  scales with the cohort exactly where the UI least wants it. The split is measured, not stylistic.

- **Decision (2) — the PDB is its own streaming route, never inline.**
  **`GET /api/analyses/{id}/structure`** streams the file at the row's stored `pdb_path` as
  `text/plain`. Not embedded in the detail JSON, not base64.

  **Why:** `structure.pdb` measured **194 KB / 232 KB** — ~640 B per residue, so a 1600-residue
  rental fold is ~1 MB. Inlining it in `/api/analyses/{id}` would make every provenance-panel
  render pay the viewer's cost. A separate route also matches 3Dmol.js, which accepts a URL
  directly, and lets the browser cache the structure independently of the metadata.

  **⚠ Serve the stored path, never a reconstructed one.** Artifacts are written to
  `{artifact_root}/{job_id}/` (`app/artifacts.py:79`) and `pdb_path` is stored **absolute**
  (`/data/artifacts/1/structure.pdb`). In this cohort `job_id == analysis_id` coincidentally;
  they are different keys and nothing guarantees it. The route looks the row up by integer id and
  serves `row.pdb_path` — it never builds a path from a client-supplied value.

- **Decision (3) — `plddt.json` is served; PAE is not.**
  **`GET /api/analyses/{id}/plddt`** returns the per-residue array (~6 KB) — this is what colours
  the structure viewer by confidence (D-033).
  **No PAE route this session.** `pae.json.gz` is **824 KB–1.07 MB per target and ~85% of the
  21 MB Volume**, and nothing in the ruled scope renders it. Named here so its absence is a
  decision rather than an omission.

- **Decision (4) — reads are unauthenticated; writes stay bearer-guarded. Asymmetric by design.**
  The four worker routes keep `require_token`. The read routes carry **no credential**.

  **Why this is safe here, stated so it is checkable rather than assumed:** the data is 42
  ESMFold structures of **public UniProt targets**. No PII, nothing proprietary, nothing whose
  disclosure is a harm. Against that, every alternative adds machinery that can fail: a
  build-injected read token is published the moment the bundle ships (a browser bundle holds no
  secrets), and a session mechanism is login code, expiry, and storage for a dataset that does
  not need protecting. **The most robust posture is the one with the least to get wrong.**

  **D-004's no-inbound-exposure constraint is not violated, and the distinction matters.** That
  constraint governs the **GPU box** — the worker accepts no inbound connections, which is why
  the coupling is pull-based. It says nothing about Fly's public surface, which is already
  publicly reachable today (`pharmfoldmdk.fly.dev` answers 404 on `/` and 401 on
  `/jobs/claim`). Public reads on Fly leave the worker's posture untouched.

  **A cost of D-033 that D-033 did not trace, recorded here rather than discovered later:**
  under Streamlit this question would not have arisen. Streamlit renders server-side — the Python
  process holds the token and the browser receives only HTML. React is a client-side bundle, so
  **the credential problem is created by the React switch itself.** D-033 weighed the tradeoff as
  speed-to-demo; this is a second, unlisted item on that ledger. It is cheap here because the
  data is public, and it would not have been cheap if it were not.

- **Decision (5) — the auth *test property* changes shape, and must not silently weaken.**
  `app/deps.py` attaches `require_token` per-route via `dependencies=[...]` specifically so that
  "a route added later cannot silently inherit no check." **This entry adds routes that
  deliberately have no check** — which would turn a passing "every route is guarded" test into a
  false one, or force its deletion.

  The property is therefore **restated, not dropped**: *every route under `/jobs` requires the
  bearer token; every route under `/api` does not; there is no third category.* A route matching
  neither prefix fails the test. This keeps the guard's original strength — a new write route
  cannot appear unguarded — while making the read surface explicit.

- **Decision (6) — one app, `/api` prefix, static React co-served.**
  The React bundle is served by the same Fly app as FastAPI; read routes live under `/api`.
  **Why:** D-033 already argued the serving tier should be "one process serving two things";
  co-serving also means **no CORS, no second deploy path, no second machine's cost**, and the
  bundle is same-origin with its API by construction. **DEP-001 is amended when the bundle
  lands** (a build step + a static-serve path), which is that PR's work, not this entry's.

---

- **The coverage line this cohort actually produces (D-024), and why it is worth rendering.**
  Of the 82-target cohort: **40 ranked and folded, 2 held-out folded, 40 unfolded** (29
  rental-tier awaiting the A6000, 11 remaining held-out). The UI's coverage line shows a real,
  partial denominator on day one — which is the condition the pre-work sequenced the first fold
  *before* the UI to obtain.

  **And the confidence spread is a live D-024 concern, not a later one.** Measured mean pLDDT
  runs **34.78 (Q9UP95) to 81.40 (Q5VUB5)**, with a substantial fraction below 60 — a region
  where an ESMFold structure is not reliably interpretable. A list payload that returns
  `mean_plddt` as a bare number invites ranking on it. **The read API therefore returns
  `mean_plddt` alongside `disposition` and `held_out` on every row**, so the surface that renders
  a target always has the qualifiers that say how far to trust it. Rendering a 34.78 structure
  identically to a 77.26 one is the D-024 failure this shape exists to prevent.

- **Deep-learning justification.** Direct, via D-015 §3 and D-024. The read API is the only path
  by which the network's output becomes visible: `mean_plddt` and `fold_provenance`
  (`model_id`, `model_revision`, `dtype`, `truncated`) are what let a reader confirm **we ran
  ESMFold ourselves, at a named revision, and know how confident it was** — rather than that a
  structure appeared. Serving provenance as a first-class field, not a footnote, is what makes
  the deep-learning claim auditable. It is also the supplier for the scorer's surface (D-027):
  the ranking table (D-028) consumes this same list route once a structural ranking exists.

- **Consequences / follow-ups.**
  - **Tests first, per project rule.** The surface under test: light-list field set (asserting
    `sequence` and `fold_provenance` are **absent**); detail includes both; 404 on unknown id;
    structure route serves the stored `pdb_path` and 404s when the row has none; plddt route
    returns the array; **the restated auth property** (`/jobs` guarded, `/api` open, no third
    category); and that no read route mutates state.
  - **No PAE route** — revisit only when something renders PAE.
  - **`docs/RUNGUIDE-startup-and-local-batch.md` corrected**: `--bucket local` enqueues **42**
    (40 ranked + 2 held-out), not 40.
  - **`ARCHITECTURE.md` updated in this same PR** (CLAUDE.md rule 2): the read routes join the
    component table and the serving-tier description.
  - **DEP-004's meaning changes when the bundle ships, not now.** This PR adds read routes to a
    transport that is still API-only; a green deploy still does not mean a UI is reachable.
  - **The rental-tier path (29 targets) is a separate entry**, later this session. The read API
    is tier-agnostic — a rental fold lands in the same table with the same `meta` shape, so
    nothing here needs revisiting when those 29 land.

---

### DEP-005 — Applying the production schema: supervised first, automated after
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)** — owner-ruled via the deployment-arc orders (the Planner's
  draft was Proposed; these orders enact it: the corrections below, the phase-1/phase-2 split, and
  the verification surface).
- **Context — the gap the Builder surfaced rather than guessed past.** DEP-004 rules that a
  green deploy means *"the transport API is up and the queue is accepting work."* **That is
  false until the schema exists on the Fly database.** Nothing in DEP-001…004 says how
  `alembic upgrade head` runs against production, and the Builder deliberately did **not** add a
  `fly.toml` `release_command` for it, on the grounds that it touches the prod database and
  belongs in a decision. Correct call: this entry exists because of it.

  **Provenance (D-016):** ruled against `db/migrations/env.py`, `db/migrations/versions/`, and
  D-012 §5a / D-017 / D-019, read from the tree at `6792c21`. The Planner has **not** seen the
  `Dockerfile`, `fly.toml`, or deploy-job body built in PR #48 — those are Builder-reported, and
  the `release_command` wiring below must be checked against the actual `fly.toml` before it
  lands.

---

- **Why this is not a routine migration, stated before the ruling.** The chain is two
  migrations, and `0002` is not ordinary DDL:

  ```
  0001_create_jobs.py
  0002_protein_analyses.py   ← creates the extensions schema, the vector extension,
                                and analysis_embeddings (embedding vector(384))
  ```

  `0002` runs `CREATE SCHEMA IF NOT EXISTS extensions`, `CREATE EXTENSION IF NOT EXISTS vector
  SCHEMA extensions`, and then a **bare `vector(384)`** column that resolves only through
  `env.py`'s `SET search_path TO public, extensions` (D-012 §5a). So the first production
  migration is simultaneously:

  1. the first time the **migration chain** runs against the Fly MPG cluster (D-014);
  2. the first time `CREATE EXTENSION vector` is issued **on production**, where the role's
     privileges are the Fly cluster's, not CI's;
  3. the first time the `search_path` seam resolves a bare `vector` type **outside CI**.

  **Correction to a claim carried in this project's own hazard notes:** the `postgres` CI job
  uses a **pgvector image** (D-019), not stock `postgres:16` as
  `docs/HAZARD-search-path-seams.md` and D-032 both state. Seam 2 is therefore *better* covered
  than those documents say — the extension path is exercised in CI. **What CI still cannot
  prove is production role privileges on a managed cluster.** `CREATE EXTENSION` commonly
  requires elevated rights; if the Fly database role lacks them, this migration fails on the
  first run and only on production. That is the specific reason to watch it. *(Both documents are
  corrected in this same change.)*

---

- **Decision — two phases, and they compose:**

  **Phase 1 — the initial migration is run BY HAND, supervised, BEFORE the first deploy.**
  Not by `release_command`, not by the deploy job. The owner runs `alembic upgrade head`
  against the Fly database once, watches it, and confirms the schema exists.

  **Why supervised for the first run, specifically:** every item in the list above is
  first-time-on-prod, and a `release_command` failure surfaces as a deploy log to parse after
  the fact. A hand-run surfaces as an error message in front of a person who can act on it. The
  asymmetry is stark and one-directional — supervising costs five minutes; debugging a failed
  automated migration against a half-applied prod schema costs an evening, and it happens with
  the deploy already in flight.

  **Phase 2 — a `release_command` in `fly.toml` for steady state, ruled but wired AFTER
  phase 1 succeeds.** Once the schema is known-good and the app has come up clean, migrations
  become automatic and versioned with the deploy: Fly runs the release command in a one-off
  machine before the new version goes live, so **a failed migration aborts the release rather
  than shipping code against a schema that never applied.** That property is worth having, and
  it is why phase 2 is ruled now rather than left open.

  **The order is the substance of this entry.** Automating first would mean the riskiest
  migration in the project's history runs unattended; hand-running forever would mean "did prod
  get migrated" is a question rather than a guarantee. Supervised-then-automated gets both.

- **⚠ The merge that lands the deploy job must NOT precede phase 1.** DEP-004's promise —
  a green deploy means the queue accepts work — is only true once the tables exist. Merging
  first produces a green deploy over an empty database: **the transport would be up and every
  write would fail**, which is exactly the over-read DEP-004 was written to prevent, arriving by
  a different route.

---

- **Test surface / verification (what "phase 1 succeeded" means, so it is checkable rather
  than felt):**
  - `alembic current` against the Fly database reports **head** (`0002`).
  - The `extensions` schema exists and the `vector` extension is installed in it.
  - `analysis_embeddings` exists with an `embedding vector(384)` column — i.e. the bare
    `vector(384)` resolved, which is the seam actually being tested.
  - `jobs`, `protein_analyses`, and `ranking_runs` exist with the FK closure D-019 ruled.
  - **If `CREATE EXTENSION` fails on privileges**, that is a result, not a blocker to work
    around: it means the Fly role needs elevation or the extension needs pre-installing by the
    cluster owner, and that fact belongs in this entry as an amendment rather than in a
    workaround.

- **Deep-learning justification:** indirect. `analysis_embeddings` is the vector store the
  scorer's outputs (D-027) will land in. A schema that half-applied, or a `vector` type that
  silently failed to resolve, would surface later as missing data rather than as an error —
  the same invisible-corruption class D-017 and D-032 exist to guard against, one layer out.

- **Consequences / follow-ups:**
  - **`docs/HAZARD-search-path-seams.md` and D-032 both need correcting** on the stock-image
    claim: the `postgres` job uses a pgvector image per D-019. Seam 2's remaining exposure is
    **production role privileges**, not CI coverage. Its named trigger (the first
    `analysis_embeddings` write, downstream of D-027) is unchanged. *(Done in this change.)*
  - **Phase 2's `release_command` is a change to the deploy path**, which sits downstream of two
    required checks — so per D-008 it is proven, not merged on the strength of a passing run.
  - **The provisioning checklist is owner action and precedes everything here:** the app-scoped
    token as the `FLY_API_TOKEN` GitHub secret (DEP-003), `primary_region` matching the MPG
    cluster's region, `DATABASE_URL`, `WORKER_AUTH_TOKEN` matching the worker's, and the
    artifacts volume.

---

### DEP-004 — What a green deploy means, and what it does not
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)**
- **Series note:** first entries under the `DEP-NNN` prefix — deployment/operations, same log,
  appended at top, monotonic within series (D-002's single-log discipline unchanged). The
  precedent is `S-NNN` for spikes: a prefix that says which arc an entry belongs to, so a reader
  tracing the graded scientific claim can skip `DEP-*` and a reader debugging a deploy can find
  them together. **No deployment TDD** — considered and rejected as disproportionate; the
  coherent picture is D-004 plus these entries.
- **Context:** Deployment is about to produce a green "deploy succeeded" signal on every
  main-push. That signal is easy to over-read, and two facts make the honest reading narrower
  than the word "deployed" implies:
  - **The worker is not deployed** (D-004): `worker/` runs on the local GPU box and is started
    **by hand**. Nothing in the deploy pipeline starts it.
  - **There is no UI yet.** D-004 plans Streamlit as the serving tier's front end, but **it does
    not exist** — verified against the tree at `6792c21`: no `streamlit` dependency, no Streamlit
    code. `app/` is the FastAPI transport only (the four worker→Fly routes from D-031).
- **Decision — a green deploy means exactly this: the transport API is up on Fly and the queue
  is accepting work.** It does **not** mean:
  - that any fold has run, or can run without the owner starting the worker;
  - that a user-facing UI is reachable — there is none to reach;
  - that the full system is "live" in any sense a reader might assume from a green checkmark.

  Stated so the signal is not over-read — by the owner, or by a grader seeing a passing deploy.
- **Deep-learning justification:** neutral — operational honesty, not a model decision. Recorded
  because an over-read green is the deployment-arc version of the failure the whole log guards
  against: a signal that claims more than it demonstrates.
- **Consequences:**
  - When Streamlit is built, it is its own entry and it changes what a green deploy means — at
    which point this entry is amended, not silently outgrown. *(Superseded in part by D-033: the
    UI is React, not Streamlit — but the shape of this consequence is unchanged: the first UI to
    ship amends what a green deploy means.)*

    > **⚠ Amended by DEP-006 (2026-07-23) — this is that merge.** The React bundle now ships in the
    > two-stage image and is served under `/` (`/api` and `/jobs` matched first). **A green deploy
    > therefore now means a UI is reachable** at `pharmfoldmdk.fly.dev`, which it never did before.
    > DEP-004's own stated trigger — *"the first UI to ship amends what a green deploy means"* —
    > fired. A green deploy still does **not** mean any fold has run (that remains an owner action).
  - **Starting the worker on the GPU box is an owner action**, and it is the precondition for the
    first end-to-end fold (the measurement that retires D-030's provisional lease and D-031's PAE
    ratio).

---

### DEP-003 — `FLY_API_TOKEN`: an app-scoped deploy token, not an account token
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)**
- **Context:** The deploy job authenticates to Fly with a token held as a GitHub Actions secret.
  A GitHub Actions secret is readable by any workflow run on the repo, so its blast radius on
  compromise is the question, not merely its convenience.
- **Decision — an app-scoped deploy token (`fly tokens create deploy`), scoped to
  `pharmfoldmdk` alone.** Not an account/org-wide token.
  - **Rationale, owner's ruling:** there are **four other apps on the account**. An account-wide
    token in CI means a compromised workflow could redeploy or disrupt all five; an app-scoped
    token can touch only this one. The scope cost is nil — the deploy job only ever deploys this
    app — so there is no reason to hold more authority than the job uses.
  - **Rotation is an owner action, not automated.** If the token is rotated or revoked, the
    GitHub secret is updated by hand. No rotation automation is built; naming it here is what
    keeps "who can redeploy prod" an answerable question rather than an assumed one.
- **Deep-learning justification:** neutral — least-privilege on a deploy credential.
- **Consequences:**
  - The token grants deploy on `pharmfoldmdk` only; a second app would need its own.
  - Stored as the `FLY_API_TOKEN` GitHub Actions secret; referenced by the deploy job, never
    echoed.
  - **Owner action, precondition for the first green deploy:** create the token
    (`fly tokens create deploy -a pharmfoldmdk`) and set it as the `FLY_API_TOKEN` repo secret.
    Until it exists, the deploy step authenticates to nothing — the Builder cannot create it
    (it is a credential), and says so rather than stubbing around it.

---

### DEP-002 — The deploy guard lives on the job, never on the trigger
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)** — forced by D-008; ruled explicitly so the shape is not
  gotten backwards.
- **Context:** `gate.yml`'s own header carries the instruction:
  > *"When real Fly deploy is wired, guard the DEPLOY JOB (not the trigger) against doc-only
  > changes so docs still run tests but don't redeploy."*

  Without a guard, every docs-only PR merged to main would trigger a production deploy. The
  tempting fix — a `paths-ignore` on the workflow — is **the exact thing D-008 removed**, because
  a required status check that does not report on every PR leaves that PR unmergeable forever.
  `test` and `postgres` are both required (D-032); they must run on docs PRs too.
- **Decision — the deploy JOB is conditional on the change not being docs-only; the workflow
  TRIGGER is untouched.** `test` and `postgres` run on every PR and push, as now. The `deploy`
  job additionally checks whether the push changed anything outside `docs/**` and `*.md`, and
  **skips the Fly deploy step when it did not.** Docs still run the full required suite; they
  just do not redeploy.
- **Why this exact split, restated because it is easy to invert:** guarding the *trigger* would
  make the required checks stop reporting on docs PRs → deadlock (D-008). Guarding the *job*
  keeps the checks universal and makes only the *deploy* conditional. The first is a
  reintroduced bug; the second is the fix.
- **Deep-learning justification:** neutral — CI topology.
- **Consequences / test surface:**
  - **Testable, and tested first (project rule):** a docs-only change must not run the deploy
    step; a code change must. The doc-only detection (diff of changed paths against the previous
    main commit, matched against `docs/**` / `*.md`) is the unit under test.
  - The deploy job stays `needs: [test, postgres]` — it cannot run until both required checks are
    green, unchanged from the placeholder.

---

### DEP-001 — What the Fly image contains, and what it must never contain
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)**
- **Context:** The Fly image serves the transport tier. What goes into it is a decision because
  the failure mode of getting it wrong is silent: an image that includes the worker's CUDA stack
  would be multi-gigabyte, slow to build and deploy, and **would still work** — so nothing would
  flag it. D-004 (worker not deployed) and D-018 (the CUDA stack is a separate, unlocked
  dependency world) both bear on it, and neither is self-enforcing in a Dockerfile.
- **Decision — the image contains the runtime tier and nothing GPU:**
  - **Installs `requirements.lock`** — the hash-locked runtime file (D-013), which as of #47
    carries FastAPI/uvicorn/python-multipart. **Not** `requirements-dev.lock`, **not**
    `worker/requirements.txt`.
  - **Copies `app/` and `core/`.** `app/` is the FastAPI transport; `core/` because the `/claim`
    route calls `core.queue.PostgresJobQueue` (verified in `app/main.py`) and the routes import
    the queue/manifest primitives.
  - **Does NOT copy `worker/`** and **does NOT install any `torch`/`transformers` stack.** The
    worker runs on the GPU box (D-004); its `torch==2.11.0+cu128` build is a CUDA dependency world
    D-018 deliberately keeps out of the locked environment.
  - **No Streamlit** — it does not exist yet (verified against the tree). When it is built, this
    entry is amended to add it and its dependency.
- **Why explicit rather than left to whoever writes the `COPY` lines:** the image-bloat failure
  is invisible (it works), and the correct contents are dictated by two prior entries a Dockerfile
  author might not have in view. Ruling it makes the Dockerfile a transcription of a decision
  rather than a judgement call.
- **Deep-learning justification:** indirect — keeping the CUDA stack out of the serving image is
  the deployment face of D-018's separation, which is what makes the runtime environment a
  function of a committed lock file (D-013) rather than of an unpinned GPU toolchain.
- **Consequences / test surface:**
  - **Assertable and tested first:** the built image (or the Dockerfile's install/copy set) must
    contain no `torch` and no `worker/`. A test/CI check that greps the image or the Dockerfile
    for `torch` guards the invisible failure.
  - When Streamlit lands, both this entry and the image change together. *(Now React, per D-033 —
    a build step + static-serve path, a DEP-001 amendment when the UI is built, not before.)*
  - **Builder note (verified against the import graph at `6792c21`, 2026-07-22):** the COPY list
    above is corrected in two ways the ruling did not trace, **both preserving its intent** (no
    CUDA/worker world in the serving image):
    1. **The image also copies `db/`** (the SQLAlchemy ORM models). `app/artifacts.py` imports
       `db.models`; `db/` is serving-tier with no GPU dependency. DEP-001 under-listed it — an
       image of `app/` + `core/` alone would fail at import.
    2. **`FoldSpec` was relocated to `core/contracts.py`.** `app/artifacts.py` imported it from
       `worker/orchestrator.py`, which would have forced `worker/` into the image **against this
       very ruling**. `FoldSpec` is the claim contract — the route produces it, the loop consumes
       it — tier-neutral by nature; it now lives in `core/` and `worker.orchestrator` **re-exports**
       it, so the loop's tests are unchanged (D-031 rule) and the image ships `app/` + `core/` +
       `db/`, no `worker/`. The image-contents test enforces the "no `worker/`, no torch"
       property, so this correction is self-guarding rather than a promise.

---

### D-033 — The serving-tier UI is React, superseding D-004's Streamlit choice
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)**
- **Supersedes:** D-004's *"Serving tier — Fly.io: **Streamlit** + FastAPI…"* — that clause only.
  D-004's two-tier topology, pull-based coupling, and no-inbound-exposure constraints are
  **unchanged and still binding**.
- **Context:** D-004 named Streamlit on 2026-07-19, before the UI's actual requirements existed.
  Those requirements arrived later and are now specific:
  - **D-015 §1a** — disagreement classes must be **visually distinct**; a class-1 and a class-2
    that render identically in a sorted table mean entirely different things and would read the
    same.
  - **D-024** — a coverage line rendered *with* every ranking, held-out and excluded rows
    reachable from it, boundary method visible per target, fold provenance surfaced.
  - **D-028** — per-class **quality tooltips** carrying what each disagreement class can and
    cannot support, inline rather than on a separate methods page; plus feature attribution
    rendered as a statement about the model, never about the target.

  **Nothing is built.** There is no Streamlit dependency and no Streamlit code in the tree
  (verified at `6792c21`). So this supersession costs one entry and no code — which is precisely
  why it is made now rather than after a UI exists.

- **Decision — the serving-tier UI is a React application consuming the FastAPI API.**

  **Why, in terms of what the ruled entries actually require:** every UI commitment above is an
  *interaction* requirement — conditional styling per disagreement class, inline tooltips whose
  content varies by class, drill-down from a coverage line into held-out and excluded rows.
  Streamlit rations exactly that layer: it excels at rapid server-rendered dashboards and
  fights per-element styling and hover state. **The UI is the vehicle for D-028's claim
  discipline; a framework that makes tooltips awkward makes that discipline awkward.**

  **It also fits the architecture better than it did in July.** D-031 built `app/` as FastAPI
  routes — the serving tier is *already* an API. Streamlit would sit beside that API as a second
  Python server rendering server-side; React consumes it as a client. The serving tier becomes
  **FastAPI + a static React bundle**, which is one process serving two things rather than two
  processes.

- **3D visualization — the one real dependency of this switch, resolved not deferred.**
  `ARCHITECTURE.md` and `docs/UI_Plan.md` specify `py3Dmol`/`stmol`, which are Streamlit-bound.
  **`py3Dmol` is a Python wrapper around 3Dmol.js**, so React uses **3Dmol.js directly** and
  every capability the UI Plan lists survives intact: PDB load from path or string, residue
  highlighting and selection, surface/cartoon/stick representations, **colour-by-pLDDT**, pocket
  surface rendering, mutation highlighting. Nothing is lost; a wrapper is removed.

- **The tradeoff, recorded because it is real and was weighed rather than waved past.**
  Streamlit's advantage was **speed to a defensible demo** — a working data app in an afternoon,
  no bundler, no JS toolchain, for a solo builder on a course deadline. That advantage is
  genuine and this entry gives it up. It is given up because the UI is not incidental here: it
  is where D-015 §1a's class distinction, D-024's coverage line, and D-028's tooltips either
  become legible **to a grader** or do not. A UI that renders the ranking correctly but flattens
  the disagreement classes would satisfy the letter of those entries and defeat their purpose.
  **If the deadline later forces a retreat, that is a decision to make explicitly in an entry —
  not by quietly shipping a flatter UI.**

- **Deep-learning justification:** direct, via D-015 §3 and D-028. The scorer's contribution is
  only assessable if a reader can see *which* targets moved, *by how much*, in *which*
  disagreement class, and *what that class supports*. D-024 already ruled that the honest
  reading travels with the result; **this entry is about the surface that makes that possible
  rather than aspirational.** A learned scorer whose output is rendered indistinguishably from a
  heuristic's has had its deep-learning contribution made invisible.

- **Consequences / follow-ups:**
  - **`docs/UI_Plan.md` is now substantially wrong** — it names Streamlit as primary technology
    (§ header and §1) and `py3Dmol`/`stmol` for 3D (§3). It predates D-015, D-024 and D-028 and
    has no coverage or limitations surface at all. **It needs superseding or rewriting**, and
    that is its own task — not folded into this entry.
  - **`ARCHITECTURE.md` needs updating in three places** (the diagram at :63, the component
    table at :105, the serving-tier description at :205, and the roadmap note at :461).
  - **`docs/TDD_v3_ADC_Focused.md:103`** names "Streamlit frontend + FastAPI backend" — same
    correction.
  - **DEP-001 is affected when the UI is built, not before.** The image today ships `app/` +
    `core/` + the runtime lock. A React UI adds a **build step** (bundle) and a **static-serve
    path**, which is a DEP-001 amendment at that time. **Today's deploy is unchanged** — there is
    still no UI to ship.
  - **DEP-004's meaning is unchanged**: a green deploy means the transport API is up and the
    queue accepts work. It did not include a UI before this entry and does not now.
  - **No new runtime Python dependency.** React is a build-time toolchain producing static
    assets; it does not enter `requirements.lock`. The JS toolchain's own pinning is a question
    for the entry that builds the UI, and it is **outside D-013's guarantee** in the same way
    `worker/requirements.txt` is (D-018) — stated now so it is not discovered later.

---

### D-032 — Promoting the Postgres job to a required check: the D-017 bar, met
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)** — criterion 2 confirmed by the Builder against the
  job's run history (see below). The promotion itself is an owner-only repo-settings change
  (D-008) and is the owner's to apply.
- **Context:** D-025 authorized merge-on-green. Its own consequences named the constraint on its
  value: *"merge-on-green is only as strong as the set of required checks, and the Postgres
  integration job is still not one of them… until it is promoted, a migration bug can merge
  green."* Every merge on 2026-07-22 — including `core/enqueue.py` and `worker/orchestrator.py` —
  rode that authorization with the guard advisory.

  **A correction to how this item has been described, recorded because it was repeated all day.**
  Several documents in this session — the pre-work, the close-out draft, and the Planner's
  summaries — called the D-017 promotion bar *"still a vibe, not a number."* **That was wrong.**
  D-017 §"How far" sets an explicit, falsifiable three-part bar:

  1. the job completes on **≥ 5 consecutive PRs** since D-017;
  2. on every one, any red was attributable to a **genuine code/migration fault** and
     **never to service-container infrastructure** (startup timeout, `pg_isready` failure,
     connection-refused);
  3. **any infra-attributable failure resets the count to zero.**

  D-017 even says why the bar is shaped that way: *"the counter measures the thing that matters
  (would 'required' have blocked honest work?), not elapsed time."* **The item was not missing a
  number; nobody had checked the number against the runs.** That is a different failure — and a
  more embarrassing one, since the artefact was in the repo the whole time.

---

- **The bar, checked (D-016 — this is the part that needs an artefact, not an assertion):**

  **Criterion 1 — ≥ 5 consecutive PRs.** D-017 landed at PR #30. Since then: **#31 through #45**,
  fifteen PRs. `paths-ignore` was removed by D-008 precisely so **every** PR triggers the
  workflow, including docs-only ones — so all fifteen are countable, not just the code PRs.
  **Criterion 1 is met roughly threefold.**

  **Criterion 2 — no infra-attributable reds. CONFIRMED by the Builder, 2026-07-22.** This
  criterion cannot be established from the tree: the distinction D-017 draws — a red that was the
  job *doing its work* versus a red from a flaking service container — lives in **GitHub Actions
  run logs, not in the repository.** The Builder pulled the failed step and log for each red
  rather than inferring from branch names, which is the distinction the bar actually turns on.

  **42 runs across #31–#45** (the job's entire history since D-017 added it). **Exactly two
  reds, both genuine faults, zero infra flakes:**

  | Run | Branch | Failed step | Nature |
  |---|---|---|---|
  | 29879472591 | `postgres-integration-job` (D-017) | Postgres integration tests | **code** — caught the env.py transaction bug (a migration silently rolling back) |
  | 29882471328 | `protein-analyses-migration` (D-019) | Apply migrations (`alembic upgrade head`) | **migration** — caught 0002 re-creating an existing index |

  In both, `Initialize containers` succeeded, `pg_isready` health checks ran, and there was no
  startup timeout, connection-refused, or health failure. **The failure was strictly downstream,
  in the migration or test step** — the job doing its work.

  **Criterion 3 — reset on infra flake.** Not triggered; the count is intact.

  **Additional evidence beyond the bar, and it is stronger than the bar itself:** the two reds
  above are not merely *not-flakes* — they are the **two production-grade bugs the close-outs
  credit this job with catching**, now traced to their run IDs rather than recalled. The job also
  confirmed the re-anchored reap boundaries on real PG (#43). **A check that has fired correctly
  twice and falsely zero times in 42 runs is better evidenced than one that has merely been green
  five times.** D-017's bar measures the absence of flakes; this measures the presence of value.
  Both point the same way, which is the comfortable case.

---

- **Decision: add `postgres` to branch protection's required checks, effective BEFORE the
  transport PR.**

  **The timing is the substance of this entry, not a detail.** The alternative — naming a future
  threshold ("promote after N more clean runs") — would mean the transport PR merges first. That
  PR creates `app/`, the first FastAPI route handlers, and is the **largest new
  database-touching surface the project has produced**. It is precisely what the job exists to
  guard. Promoting after it inverts the point of having a guard.

  **What promotion changes:** a red `postgres` job blocks merge, with **no admin bypass**
  (D-008's `enforce_admins`). That is the intended cost. D-017 declined to promote early for a
  specific, still-valid reason — *"a required job with a service container that flakes would
  deadlock every PR with no admin bypass"* — which is exactly why criterion 2 is the one that
  matters and why it is the Builder's to confirm rather than the Planner's to assume.

- **What this does NOT change, stated so promotion is not mistaken for wider coverage:**
  - **Seam 2's remaining exposure is production role privileges, not CI coverage — correcting a
    claim this entry originally carried.** This entry (and `docs/HAZARD-search-path-seams.md`)
    said the `postgres` service image is stock `postgres:16` with no vector column; that is
    **wrong** and is corrected here per DEP-005. D-019 switched the CI image to
    `pgvector/pgvector:pg16`, and migration `0002` creates `analysis_embeddings` with a bare
    `vector(384)` column that resolves only through env.py's `search_path` — so the
    extension/type-resolution path **is** exercised in the `postgres` job at migration time.
    What a required Postgres job still does **not** prove is **production role privileges**:
    `CREATE EXTENSION` commonly needs elevated rights and the Fly managed cluster's role is not
    CI's (DEP-005). Per `docs/HAZARD-search-path-seams.md` this is **seam 2**, and its named
    trigger is unchanged — the first `analysis_embeddings` write, downstream of D-027. **A
    required Postgres job does not close it.**
  - **`worker/requirements.txt` remains outside the lock-file guarantee** (D-018, by design;
    `accelerate` unpinned). No CI job reddens on a breaking upstream release there.
  - **`--require-hashes` tamper rejection remains asserted, not demonstrated.**

- **Deep-learning justification:** indirect, and the same shape D-017 gave. The queue dispatches
  every neural inference; a broken migration or a silently-non-atomic claim corrupts the fold
  cache the deliverable is served from, invisibly, under a green SQLite suite. Making the guard
  *required* is what converts D-025's merge-on-green from a throughput convenience into a safe
  one.

- **Consequences / follow-ups:**
  - **Closes the standing constraint D-025 named on itself.** D-025's consequence block should be
    updated to reference this entry rather than leaving the promotion open.
  - **The transport PR (D-031) is held until this lands** — the owner's sequencing, and the point
    of the entry.
  - ~~If criterion 2 fails…~~ **Criterion 2 passed.** Retained as a note on method: the check was
    run against logs with the answer genuinely open, not to ratify a decision already taken. Had
    a red been infra-attributable, the count would have reset per D-017 (3) and this entry would
    have become a dated record of a bar checked and not met.
  - **The image is already `pgvector/pgvector:pg16` (D-019)** — switched when migration `0002`
    added the vector column, *before* this job became required. Any *future* change to this
    now-required check (image or otherwise) is proven RED→GREEN per D-008, not merged on the
    strength of a passing run (D-025).

---

### D-031 — The Fly transport: HTTP realization of the loop's discovered protocol
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)**
- **Context:** D-030 ruled the topology and deliberately deferred the transport, sequencing the
  loop first so the protocol would be *discovered by construction* rather than designed in the
  abstract. That worked: `worker/orchestrator.py` is built and green against an injected client,
  and the interface it needed is now known rather than imagined.

  **The contract the loop defined, reported untidied by the Builder:**
  - `claim()` → job **with the fold spec inline** (sequence, slice coords, tier params) or `None`
  - `upload(job, artifacts)` → returns nothing; **must be idempotent**
  - `complete(job)` / `fail(job, err)` — separate calls, *mergeable with upload* (flagged)
  - `TransportError` is the retry signal
  - **no `renew`** — the heartbeat D-030 flagged does not exist yet
  - route handlers **inherit the seam-1 obligation** (`docs/HAZARD-search-path-seams.md`)

  This entry rules the HTTP realization of exactly that. **It adds no capability the loop did
  not ask for.**

---

- **Decision — four routes, one auth scheme, one idempotency rule:**

  | Route | Method | Body | Returns |
  |---|---|---|---|
  | `/jobs/claim` | POST | `{worker_id}` | job + fold spec, or 204 |
  | `/jobs/{id}/artifacts` | POST | multipart: pdb, plddt, pae?, provenance | 204 |
  | `/jobs/{id}/complete` | POST | — | 204 |
  | `/jobs/{id}/fail` | POST | `{error}` | 204 |

  **(1) Claim carries the fold spec inline, as the loop requires.** The worker never queries for
  its input. This preserves D-026's guarantee that the job is self-contained against UniProt
  changing: the sequence the worker folds is the sequence the manifest reviewed, delivered with
  the claim. The route delegates to `PostgresJobQueue.claim()` — **FIFO and `SKIP LOCKED`
  atomicity are the primitive's, unchanged, and D-017's proof stands** (D-030 §1).

  **(2) Artifact upload is idempotent, as the loop requires.** A retried upload after a
  transport failure must not duplicate or corrupt. Idempotency key is the job id: **re-uploading
  overwrites** rather than appending or erroring, because the worker cannot distinguish "upload
  failed" from "upload succeeded but the response was lost," and the safe reading of an
  ambiguous failure is to retry.

  **(3) Upload and complete stay SEPARATE — this entry rules against merging them.**
  The Builder flagged them as mergeable. They should not be merged, for a reason D-030 §3
  already ruled and merging would quietly reverse: **status flips server-side only after
  artifacts are persisted.** A single call that accepts artifacts *and* flips status makes the
  ordering an implementation detail of one handler rather than a property of the protocol —
  and the forbidden state (a `complete` job with no structure behind it) becomes reachable by a
  handler bug rather than by protocol violation. Two calls make the ordering **externally
  observable and testable**. The extra round-trip is cheap against a fold measured in minutes.

  **(4) Authentication: a single shared bearer token, worker→Fly only.**
  D-004's requirement is no inbound exposure of the home machine; the Fly tier is already public.
  A shared secret in the `Authorization` header is sufficient at **single-worker scale (D-004)**
  and is the smallest thing that works. **`worker_id` is a label, not a credential** — it
  identifies which worker holds a lease, and D-030 already flagged that under HTTP it drifts
  toward being an auth concern. **This entry keeps them separate deliberately**: the token
  authenticates, the id labels. The shared bearer token is **RULED
  TERMINAL (2026-07-22), not a placeholder** — sufficient by design at single-worker scale
  (D-004), not an interim step toward something more. **Reopening conditions, named:** a second
  worker, or any need to attribute or revoke access per-worker, reopens this as its own entry;
  absent those, the shared token stands.

---

- **RULED (2026-07-22) — PAE is compressed (worker-side gzip) and stored; not discarded, not
  uploaded raw.** `worker/runner.py:200` emits PAE for **every** fold — `esmfold_v1` always
  returns `predicted_aligned_error`; `dtype`/`chunk_size` do not gate it (verified by the Builder
  against `main`) — so what to do with PAE was a ruling to make, not an outcome the model would
  spare us.

  Raw, a 2213 aa PAE is L×L ≈ 4.9M floats ≈ **75–100 MB of JSON**, which over a residential
  uplink is plausibly 30–80 minutes on its own and could exceed the 3600 s provisional lease
  (D-030) *before the fold is even counted*. A larger body limit does not fix that; **gzip
  does** — gzip on float-heavy JSON typically achieves 5–10×, putting a 75–100 MB PAE at roughly
  **10–20 MB — an estimate, not a measurement**. The actual ratio is observed on the first large
  fold, the same measurement that makes D-030's threshold interpretable. At that size the upload
  is a few minutes, inside the lease. So the **worker compresses** PAE and the **endpoint stores the compressed bytes**
  (the compression is client-side work, not a route concern).

  > **⚠ Amended by D-035 (2026-07-23).** The 5–10× ratio is **falsified — measured 2.2×**
  > (`ls -l /data/artifacts/1/`: 824,489 B gz from ~1.8 MB raw, 318 aa). The estimate and the
  > *"a few minutes, inside the lease"* conclusion it supported **do not hold**: a ~34–45 MB
  > compressed PAE at 2213 aa is ~21–45 min of upload alone. The compress-and-store *intent* is
  > preserved and better served — **D-035 moves PAE out of the claim→complete cycle entirely**
  > (retrieved out-of-band, option C). Kept rather than deleted; the reversal is itself evidence.

  **Store rather than discard:** nothing consumes PAE today (see the Builder note), so discard
  was viable and free — but D-027 deferred-not-dismissed a PAE-derived feature, and recovering a
  discarded PAE means a **paid re-fold** of the cohort. Compress-and-store buys that optionality
  cheaply. This also **settles what was upstream of D-030's threshold measurement:** a large-
  target upload is now bounded (~compressed PAE), so claim-stamp → upload-complete is
  interpretable.

  > **Builder note (verified against `main`, 2026-07-22): nothing downstream consumes PAE.** The
  > only references in the tree are the producer (`worker/runner.py`) and a nullable
  > `pae_json_path` column (`db/models.py:100`) that **no code reads**; D-027 rejected the one
  > PAE-derived feature considered. So "discard at the worker" does not merely make the item
  > *nearly* free — it **dissolves** the transfer, the lease interaction, and the compression
  > question at once, because there is no consumer to serve. The residual decision is only
  > whether to preserve PAE against a *future* consumer: D-027 deferred-not-dismissed a PAE
  > feature, and recovering a discarded PAE means a **paid re-fold**, so compress-and-store (PAE
  > gzips well) buys that optionality cheaply. But nothing today needs the bytes on the wire.

- **RULED (2026-07-22) — the upload route writes `protein_analyses`, not only the Volume; both
  in one transaction; provenance projects to columns and the remainder into `meta`.** The Builder
  surfaced this as the one thing the loop's protocol did not settle, and it is forced, not chosen:
  D-026 filled the **pre-fold** half of `protein_analyses` and assigned the **post-fold** half
  (`pdb_path`, `mean_plddt`, `pae_json_path`) to *"the worker."* But D-030 gave the worker **no
  database connection** — it holds only the injected `QueueClient`. So the actor D-026 named
  cannot do the write. The **only** actor with both the artifacts and a DB connection is the
  `/artifacts` route. This entry corrects D-026's assignment: **the upload route writes the
  post-fold columns.** `upload(job, artifacts)` was never "persist files"; it was always
  "persist the fold," and the durable record is half of that.

  **(a) One transaction spanning a non-transactional filesystem, with a defined ordering and a
  compensating delete.** The route touches two stores — a Fly Volume (files) and Postgres (the
  row) — and a partial write is the failure to design against: a DB row whose `pdb_path` names a
  file that was never written, or files on the Volume that no analysis points at. Neither is
  acceptable, so the ordering is fixed and the endpoint compensates:
  1. **Write the Volume files first**, to `{ARTIFACT_ROOT}/{job_id}/` (`structure.pdb`,
     `plddt.json`, `pae.json.gz` if present, `provenance.json`).
  2. **Then** update `protein_analyses` in a single DB transaction that stamps the paths.
  3. **If the file write fails, the DB is never touched** — no orphaned row (the pre-fold columns
     stay as enqueue left them, post-fold columns stay `NULL`).
  4. **If the DB transaction fails, the written files are deleted** before the error propagates —
     no orphaned files. The Volume is not transactional, so the route makes it *look* transactional
     by compensating; this is the honest bound, not a true 2-phase commit, and single-writer scale
     (D-004) is why the simple compensation is sufficient.
  The worker's retry (D-030 §4) then re-drives the whole `upload`, which is why **idempotency
  (§(2)) and this boundary are the same guarantee seen from two sides**: a retried upload
  re-writes the same paths and re-stamps the same row, converging, never duplicating.

  **(b) Provenance projection — columns where they exist, the whole record into `meta`, nothing
  dropped.** `FoldProvenance` (`worker/runner.py`) carries more than `protein_analyses` has
  columns for. The projection:
  - `mean_plddt` → the `mean_plddt` column (0–100 scale, already rescaled at fold time);
  - the `structure.pdb` Volume path → `pdb_path`;
  - the `pae.json.gz` Volume path → `pae_json_path` (**`NULL` when the fold emitted no PAE** — the
    column is nullable and stays honest about absence);
  - `structure_source` → `"esmfold"` (this structure came from our ESMFold runner, as opposed to
    `alphafold_db` or `user_upload` — the compute *tier* is not this column's job; it already
    lives in the job's `inference_settings` and in the provenance record);
  - **the full provenance dict → `meta["fold_provenance"]`**, so `ca_atom_count`, `truncated`,
    `original_length`, `input_length`, `dtype`, `chunk_size`, `folded_at`, and the ECD bounds are
    preserved verbatim — the §1a truncation/sanity flags (D-015) must survive to be queryable, and
    a column-only projection would silently drop them.

  **(c) `/complete` enforces the ordering against this write, server-side.** §(3) ruled upload and
  complete stay separate so the ordering is *externally observable*; this makes it observable
  concretely: **`/complete` rejects (HTTP 409) unless the job's analysis has `pdb_path IS NOT
  NULL`** — i.e. unless the upload's DB transaction actually committed. The forbidden state (a
  `complete` job with no structure behind it, D-030 §3) is now unreachable by a client that calls
  the routes out of order, not merely by a well-behaved loop. This is the concrete test behind
  §"Ordering is protocol-observable."

- **⚠ The route handlers are new application code touching the database — seam 1 applies
  again.** D-026's real-Postgres test closed the commit/rollback seam for the *enqueue* entry
  point. **The route handlers are a different entry point and inherit the obligation to prove it
  for themselves** — a write through a handler, re-read on a **fresh connection**. Per
  `docs/HAZARD-search-path-seams.md`, this is seam 1 only: no route here touches a vector
  column, so **seam 2 remains open with its trigger unchanged** (the first
  `analysis_embeddings` write, downstream of D-027).

- **No `renew` route.** D-030 ruled the heartbeat as a later entry; adding the route now would
  be building against an unruled design. When the heartbeat is ruled, it lands as a fifth route
  and the loop gains a renewal call — **not as a widening of `complete`.**

---

- **Test surface, written before the transport (project rule):**
  - **The loop's tests do not change.** If wiring the real client requires editing
    `worker/orchestrator.py`'s tests, the client does not implement the protocol the loop
    defined — that is the signal, and the client is wrong, not the tests.
  - **Idempotent upload** — the same artifacts posted twice leaves one set of files and no error.
  - **Ordering is protocol-observable** — a test posting `complete` for a job with no artifacts
    persisted **fails at the endpoint**, not merely in the loop. This is what makes §(3)'s
    separation load-bearing rather than stylistic.
  - **Auth** — an unauthenticated or wrong-token request is rejected on every route, asserted
    per route rather than once, so a route added later cannot silently inherit no check.
  - **Seam 1 for handlers** — a write through a real handler, re-read on a fresh connection,
    against real Postgres. **Marked `pytest.mark.postgres`; it cannot be hermetic** — SQLite has
    no schemas, so a hermetic version would pass and prove nothing.
  - **`TransportError` mapping** — non-2xx and connection failures both surface as the loop's
    retry signal, so the loop's already-proven failure taxonomy (D-030 §4) keeps working
    unchanged across the real transport.
  - **Claim returns the fold spec inline**, asserted explicitly — a route that returned a bare
    job id would compile and would silently reintroduce the worker-fetches-input design that
    D-026 ruled against.
  - **Transaction boundary (ruled above)** — a failed Volume write leaves the post-fold columns
    `NULL` (no orphaned row); a failed DB transaction leaves no files on the Volume (the
    compensating delete ran). Both directions asserted, hermetically, on the `persist_fold` seam.
  - **Provenance projection (ruled above)** — after an upload the columns hold what they should
    (`mean_plddt`, `pdb_path`, `pae_json_path`) and `meta["fold_provenance"]` holds the full
    record, so the §1a truncation/sanity flags are provably not dropped.

- **Deep-learning justification:** indirect and structural, same as D-030. This is the last
  component between a reviewable manifest and executed inference; its correctness is what makes
  fold provenance trustworthy downstream. A job marked complete with no structure behind it
  corrupts the coverage line (D-024) and the extractor's inputs (D-027) at once, and neither
  would show as an error — only as a target that quietly has no data.

- **Consequences / follow-ups:**
  - **`app/` is created by this entry** — the first application code on Fly. It is also the
    first component the `search_path` seam applies to *as a service* rather than as a script.
  - **D-026's post-fold assignment is corrected here (ruled above):** it named "the worker" as
    the writer of the post-fold columns before D-030 removed the worker's DB connection. The
    upload route is the writer. No change to D-026's pre-fold work; only the unreachable
    assignment is superseded.
  - **First web-framework dependency (D-013 change).** `app/` needs FastAPI; `requirements.txt`
    gains `fastapi` + `uvicorn` + `python-multipart` and `requirements-dev.txt` gains `httpx`
    (the `TestClient` transport, also the worker client's HTTP library). The hash-locked
    `requirements.lock` / `requirements-dev.lock` are regenerated with `uv pip compile
    --generate-hashes` and the addition is proven RED→GREEN per D-013 — the transport tests do
    not import before the lock carries FastAPI, and do after.
  - **PAE is compressed and stored (ruled above)** — settled before the first large rental fold,
    which also unblocks D-030's threshold measurement (a large-target upload is now bounded to a
    compressed PAE, so claim-stamp → upload-complete becomes interpretable).
  - **Per-worker credentials** when a second worker exists.
  - **Lease heartbeat** (D-030's flag) lands as a fifth route, not by widening an existing one.
  - **Nothing here is deployed to Fly until the full suite passes**, functional and user tests
    both.

---

### D-030 — The worker's job-pull orchestration: HTTP transport over the proven claim primitive
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)** — topology ruled; the pure orchestration loop is built
  here against an injected protocol; the concrete HTTP client + Fly endpoint API is deferred to
  D-031 (see §Consequences). The stale-threshold open item is ruled below: **raised
  provisionally**, not left unexamined.
- **Context:** D-026 built the enqueue and explicitly deferred what consumes it: *"the worker's
  job-pull orchestration (claim → the input is already stored → fold → upload) is the next
  build; D-004's pull contract governs it."* This entry rules it and re-opens nothing.

  Two facts read as a contradiction and are not one. `PostgresJobQueue.claim()` takes a
  **SQLAlchemy engine** and runs `UPDATE jobs … WHERE id = (SELECT … FOR UPDATE SKIP LOCKED
  LIMIT 1)`; D-004 specifies the worker **polls Fly over authenticated outbound HTTPS**, with
  *"no inbound exposure of the home machine; no tunnel required."* **Different layers:** the
  first is the atomic claim *primitive*, the second the *transport* by which a worker reaches
  it. A direct worker→Fly-Postgres connection would need the DB exposed or a tunnel — both
  rejected in that same D-004 sentence.

  **Ground truth on `main` (verified by the Builder):** no `app/` directory exists, and
  `PostgresJobQueue.claim()` is referenced only by `core/queue.py` and the test suite — never a
  worker or a route. The primitive is real and proven (D-017); the HTTP wrapper D-004 implies
  has never been built.
- **Decision — the topology:**

        worker (home GPU box)
          └── authenticated outbound HTTPS ──▶ Fly serving tier (FastAPI)
                                                └── PostgresJobQueue.claim() ──▶ Postgres
                                                └── Fly Volume (artifacts)

  **The engine lives on Fly, never on the worker.** The worker holds no database connection, no
  Volume mount, no inbound port.

  **(1) Claim is an authenticated HTTP call onto the existing SQL — not a re-implementation.**
  The endpoint invokes `PostgresJobQueue.claim(worker_id)` server-side. FIFO ordering (D-009 §1
  Amendment 3) and `SKIP LOCKED` atomicity live entirely in the primitive and are preserved
  unchanged; D-017's proof stays valid because the SQL it proved is the SQL that runs. Any
  future re-implementation of claim logic in the route rather than delegating to the primitive
  invalidates that proof and needs its own entry.

  **(2) Artifact transport is the same channel.** The worker uploads `structure.pdb`,
  `plddt.json`, `pae.json`, `provenance.json` over HTTPS; the endpoint writes the Volume.
  `runner.write_artifacts` keeps writing locally and knowing nothing about the DB (D-018).

  **(3) Done-ordering — the correctness heart.** The worker uploads artifacts, then calls
  complete; the status flip happens **server-side in complete, and only after the upload has
  persisted** — `upload → persist → complete`, never the reverse. A worker that dies between a
  persisted upload and complete leaves a `claimed` job that reaps and re-folds — wasteful but
  safe. The forbidden state is a `complete` job with no structure behind it, which no later
  process can detect as missing. **The loop encodes this by calling complete only after upload is
  confirmed** — the test that inverts it (upload raises ⟹ complete never called) is the guard.

  **(4) Failure taxonomy, split along the transport boundary:**

  | Failure | Handled by | DB state |
  |---|---|---|
  | Transport / connectivity (claim or submit fails) | worker's poll loop retries | none — job stays as it was |
  | Fold failure (deterministic: CUDA OOM, malformed) | worker reports → `fail()` | terminal `failed`, `attempts` untouched (D-009 §1 Amendment 2) |
  | Vanished worker (claimed, then silent) | `reap_stale()` + `MAX_ATTEMPTS`, already built | requeued, or terminal with `REAPED_OUT_REASON` |

  A submit that fails on transport is **retried, not re-folded** — re-uploading is cheap; a
  rental-tier re-fold is *paid*. This requires the submit to be **idempotent server-side**
  (completing an already-complete job is a no-op) — a route-contract obligation carried to D-031.
- **⚠ The stale threshold — RULED: `DEFAULT_STALE_SECONDS` is raised to 3600 (60 min),
  PROVISIONAL.** It was `30*60`, chosen when the implied topology was a worker holding a DB
  connection. Under HTTP the lease clock starts when the endpoint stamps `claimed_at` — before
  the worker has received the response, folded, or uploaded.

  The asymmetry is one-directional: too short requeues live work and pays to fold a rental-tier
  target twice; too long delays recovery from a rare vanish, on a workload that is offline batch
  cache-generation (D-011) and not latency-sensitive. 60 min sits above the worst plausible
  end-to-end for the largest folds (1652–2213 aa plus a large PAE upload over residential
  bandwidth) while the cost of the raise stays negligible.

  > **⚠ Amended by D-035 (2026-07-23).** The clause *"plus a large PAE upload over residential
  > bandwidth"* rested on the 5–10× gzip estimate, now **falsified at 2.2×** — so this
  > justification is **weakened, not retired**: `DEFAULT_STALE_SECONDS = 3600` is **unchanged and
  > still PROVISIONAL**. D-035's option C removes PAE from the upload path, restoring the margin by
  > a different route; the structural fix (a lease heartbeat) stays unbuilt, its trigger restated
  > (an observed reap of live work, or PAE returning to the upload path).

  Labelled **`PROVISIONAL — unmeasured under HTTP transport`** in the D-023 (iii) manner, retired
  by the named measurement: first end-to-end large-rental fold, claim-stamp → upload-complete.
  This is not a claim about the right number — it is a safe upper bound chosen on the cost
  asymmetry.

  **⚠ The measurement will not settle this, and the entry should not imply it will.** A fixed
  timeout has no correct value once fold durations are long or variable: a timeout large enough
  never to reap a live fold is necessarily large enough to make a genuine vanish slow to recover.
  The two constraints pull opposite ways and no constant satisfies both. The structural fix is a
  lease **heartbeat** — the worker renews `claimed_at` while folding — which decouples "is this
  fold alive" from "how long do we wait before recovering." Flagged for its own entry. The
  provisional 60 min covers immediate safety; it does not make the design correct.
- **⚠ The worker is the first component that spends money.** Every fold dispatched to the rented
  A6000 is billed; a retry bug re-folds NOTCH2 (1652 aa) up to three times on a paid card. The
  failure taxonomy is a cost-control decision as much as a correctness one.
- **Test surface (written before the loop):** the loop is **pure given injected collaborators**
  (a fake queue-client and a fake fold); a successful fold submits a result and never a failure;
  a deterministic fold failure routes to `fail()` and never submits a result; a transport
  failure at claim touches no DB state and is retried by the loop alone; a transport failure at
  submit is retried **without re-folding** (fold called once, submit called more than once); no
  GPU in the suite (`fold` injected, real fold owner-validated on the GPU host as
  `ceiling_probe.py` already is); and the claim seam stays where D-012 §5 put it — a hermetic
  test asserting the route "claims correctly" against SQLite would prove nothing about
  `SKIP LOCKED` and is not written.
- **Deep-learning justification:** this is the component that turns a reviewable manifest into
  executed inference — where *"we run ESMFold ourselves"* (D-003) becomes artifacts on a Volume.
  A job marked complete with no structure behind it would corrupt the coverage line (D-024) and
  the extractor's inputs (D-027) at once, so its correctness properties are what make fold
  provenance trustworthy downstream.
- **Consequences / follow-ups:**
  - **D-031 (the Fly endpoint) is deliberately sequenced AFTER this entry's loop.** The loop is
    transport-agnostic — it operates on a minimal client protocol (`claim() → job|None`,
    `upload(job, artifacts)`, `complete(job)`, `fail(job, err)`) and is fully buildable against
    injected doubles. The protocol the loop defines *by needing it* becomes the route list D-031
    must expose, so D-031 arrives as the HTTP realization of a proven interface rather than a
    design from scratch. **This is the reverse of D-023/D-024's supplier-before-contract
    ordering, and deliberately so:** there the manifest could not know the coverage line's shape
    without a ruling; here the loop discovers its own contract by construction. Auth, worker
    identity, route shape, upload size limits, and the §(4) idempotency obligation are all D-031.
  - **Lease heartbeat — its own entry,** triggered by the threshold measurement or by any
    observed reap of live work, whichever comes first.
  - **`app/` does not exist.** Creating it (the route handlers) is a new entry point that
    inherits the app-runtime `search_path` obligation (`docs/HAZARD-search-path-seams.md`): the
    claim/submit routes touch no vector column, so it is seam 1 again, proven for the route
    handlers on their own real-Postgres test — a D-031 concern.
  - **Worker identity (`worker_id`)** is free-form today; under HTTP it becomes an
    authentication concern, not a label. Flagged, ruled in D-031.
  - **The stale-threshold measurement** is an owner action, gated on the first end-to-end
    rental-tier fold.

---

### D-029 — The approved-ADC reference: openFDA for approval, a reviewed file for antigens, and two freshness dates
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)**
- **Context:** D-015 §2 leaves an item marked **blocking §2's completeness**:

  > **Open, blocking §2's completeness:** the reconciliation of the full approved-ADC target set
  > against the 82 has **not been run**. Group C is currently the three exclusions the authors
  > named; there may be others they did not. A mechanical reconciliation script closes this and
  > must run before the cohort is called final.

  Group C is the sharpest test the project has — targets the baseline pipeline filtered out
  that turned out to be validated. It is currently **three targets the paper itself named**
  (TROP2, HER3, CLDN18.2). Whether there are others the paper did not name is unknown, and
  "unknown" is doing load-bearing work in a claim the project intends to make.

  Closing it requires answering: *which UniProt accessions are targeted by approved ADCs?*
  **That question has no single authoritative source**, and this entry rules how it is answered.

---

- **Finding: the FDA database answers half the question, and the half it answers is not the
  hard half.**

  `https://api.fda.gov/drug/drugsfda.json` — free, no authentication required, updated daily
  Monday–Friday, full bulk download available. Its **five searchable top-level fields** are
  `application_number`, `openfda`, `products`, `sponsor_name`, `submissions`
  (verified 2026-07-22 against openFDA's own field reference).

  **There is no target-antigen field. There is no ADC flag.** Drugs@FDA records that a
  product was approved; it does not record what the molecule binds. So the query the project
  actually needs — accession-level — is **not answerable from FDA data alone**, and no amount
  of query construction changes that. This is a structural property of the dataset, not a gap
  to be worked around.

  **A second, narrower boundary:** Drugs@FDA excludes products regulated by CBER. Most
  oncology ADCs sit with CDER, so the practical impact is small — but it is a stated coverage
  limit, not an assumed-complete list.

  **The secondary literature disagrees with itself, and is stale by construction.** Reviews
  surveyed 2026-07-22 variously report 14 or 15 approved ADCs and describe belantamab
  mafodotin as withdrawn — but it was re-approved in October 2025 in combination, and a
  CD123-directed ADC was approved in May 2026. **Any count taken from a review paper is wrong
  the moment the field moves, and the field has moved twice in the last year.** A single-paper
  source is therefore rejected: it is simpler, but it inherits a cutoff with no way to detect
  that it has passed.

---

- **Decision — a three-part reference, with the seam between the parts stated:**

  **(1) openFDA is the authority for APPROVAL STATUS.** Queried by application number,
  recorded with the query date. Reproducible, citable, and refreshable.

  **(2) A checked-in mapping file is the authority for DRUG → TARGET ANTIGEN → UniProt
  ACCESSION.** Roughly 16 rows. **Each row cites its own source** for the antigen assignment —
  label, primary literature, or reference database — and the file is reviewed by hand.

  **Its smallness is a feature, not an embarrassment.** Sixteen rows can be read in full by a
  reviewer, which is the correct level of scrutiny for a set that determines what counts as a
  Group C finding. A computed mapping at this scale would be less trustworthy, not more.

  **(3) The mapping is NOT FDA-sourced, and the reference must say so wherever it is used.**
  This is the seam. Part (1) is authoritative and dated; part (2) is a reviewed human judgement.
  Presenting them as one "FDA-derived target list" would attribute to the FDA a claim it does
  not make — the same error class as the two `search_path` seams sharing a name
  (`docs/HAZARD-search-path-seams.md`), and as D-024's `tier=rental` needing `tier_reason` so a
  conservative routing could not read as a measured one.

---

- **Detection is automatable; assignment is not. The refresh is built accordingly.**

  A scheduled job queries openFDA and **diffs against the checked-in file**, reporting: new
  approvals absent from the mapping, withdrawals or marketing-status changes, and rows whose
  application number no longer resolves.

  **What it cannot do is extend the mapping** — assigning a target antigen to a new approval is
  a human read every time. So the job's output is *"the mapping is stale, and here is exactly
  which rows are missing,"* which is the useful half:

  > **The failure mode being guarded against is not INCOMPLETE — it is SILENTLY incomplete.**
  > A file with a freshness date and a job that detects drift is a materially different artefact
  > from a file someone compiled once and stopped thinking about. This entry does not claim the
  > list will be complete. It claims its incompleteness will be **dated and detectable.**

- **⚠ The refresh job is ADVISORY and MUST NOT be able to redden the gate.** It runs as a
  separate scheduled workflow that **opens an issue**; it is not a required check and not part
  of the test suite.

  **Rationale, and it is the same argument D-018 made** about `worker/requirements.txt` sitting
  outside the lock-file guarantee: a check that depends on an external service can go red for
  reasons unrelated to any change in this repository. If openFDA is unreachable, rate-limits, or
  renames a field, a gating check would redden the build on a day nobody touched the code —
  which trains everyone to ignore red, and a gate that is routinely ignored is worse than no
  gate. **The gate stays hermetic. Freshness is advisory.**

- **Two dates are surfaced in the UI, never collapsed into one.** They go stale at different
  rates and conflating them would overstate the weaker one:

  | Date | Meaning | Refresh |
  |---|---|---|
  | **Approvals reconciled** | last successful openFDA diff | automated, could be days old |
  | **Antigen mapping reviewed** | last human review of drug → accession | manual, will lag, and is the genuinely incomplete one |

  A single "last updated" stamp would take the automated date and imply it covers the manual
  one. **The mapping's review date is the honest one to show most prominently**, because it
  bounds what the reference can actually support.

---

- **Test surface, written before the script (project rule):**
  - **The reconciliation is pure given a fixture** — the openFDA response and the mapping file
    in, the diff out. **No network in the test suite.** A recorded fixture response is checked
    in; the live query happens only in the scheduled workflow.
  - **A new approval absent from the mapping is DETECTED**, and the diff names it. This is the
    job's entire purpose and it is the test that proves it works.
  - **A stale application number is detected** rather than silently dropped.
  - **Every mapping row has a non-empty source citation** — a row without one fails, so an
    uncited antigen assignment cannot enter the file.
  - **Accessions in the mapping resolve against the cohort** — a Group C candidate is either in
    the 82 or explicitly outside it, never ambiguous.
  - **The two dates are distinct fields** and no code path writes one from the other.

- **Deep-learning justification:** indirect but real. Group C is the project's sharpest
  evaluation instrument — a target the baseline filtered out and the world subsequently
  validated is worth more than any aggregate correlation. **The instrument is only as good as
  the set that defines it**, and D-015 §2 already carries the caveat that three named
  exclusions are *a single instance and not a demonstrated pattern*. This entry is what would
  let that caveat ever be lifted or strengthened by evidence rather than by assertion.

- **Consequences / follow-ups:**
  - **Closes D-015 §2's blocking item** once the reconciliation runs — the cohort cannot be
    called final before it does.
  - **Group C may grow.** If reconciliation finds approved-ADC targets among the 82 that the
    baseline did not name, Group C expands and D-015 §2's single-instance caveat weakens in the
    project's favour. **If it finds none, that is also a result** and must be reported as such
    rather than quietly leaving Group C at three.
  - **RULED (2026-07-22): the mapping file's owner is the project owner; the review cadence is
    diff-triggered with a floor of one review per iteration.** The scheduled openFDA diff is the
    trigger — a detected new approval prompts a review — and even with no trigger, the mapping is
    reviewed at least once per project iteration, so the "antigen mapping reviewed" date cannot
    silently outlive an iteration.
  - **This entry does not rule the antigen sources themselves** — which label, which database,
    which paper per row. That is per-row and belongs in the file's own citations, not here.

---

### D-028 — The system detects and classifies disagreement; it does not explain it
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)**
- **Numbering note:** drafted as D-027, renumbered to D-028 when the Builder claimed D-026 for
  the enqueue step and the feature-set entry moved to D-027.
- **Context:** D-015 §1 asks *which disagreements are checkable against outcomes the world has
  already decided, and which are hypotheses.* D-015 §1a requires disagreement classes to be
  visually distinct. D-024 makes coverage a first-class surface.

  **None of them says what the system may claim about WHY two rankings disagree** — and the
  gap is not neutral. A comparative ranking view showing baseline rank, structural rank, and
  delta invites exactly one question from any reader, grader included: *why?* Left unruled,
  that question gets answered by whatever the UI happens to render next to the delta, and
  the most natural thing to render is the feature that moved most. **That would be a causal
  claim the system cannot support.**

  D-027's six features are *interpretable* — a disagreement can be attributed to a feature.
  **Attribution is not explanation, and the gap between them is one sentence wide in a UI.**
  *"Feature 6 accounts for most of this target's structural rank"* is a statement about the
  model, and true. *"This target ranks higher because its epitope is more accessible"* is a
  statement about biology, and the system has no standing to make it. The second is what a
  reader will write in their notes after reading the first, unless the interface is explicit
  about which one it is asserting.

- **Decision:** The system's claim is bounded at **detection and classification**.

  **In scope:**
  - **Detect** disagreement between the structural ranking and the comparator's evidence
    score — the delta, the movers, the direction.
  - **Classify** it per D-015 §1a: **class-1** (checkable against decided outcomes) or
    **class-2** (hypothesis on an axis never measured), rendered visually distinct.
  - **Attribute** it to features — which of the six moved this target, and by how much. A
    statement about the model, labelled as such.

  **Explicitly OUT of scope, as a named non-goal:**
  - Any claim about the **biological cause** of a disagreement.
  - Any ranking, scoring, or ordering of disagreements by "interestingness" or "promise" —
    which is an explanation wearing a number.
  - Any generated prose that narrates a disagreement into a mechanism.

  **A non-goal is a commitment, not an omission.** It is recorded here so that a later
  iteration adding explanation does so as a ruled change with its own entry, rather than as a
  feature that arrived because the UI had space for it.

  **This is a scope ruling, not a modesty clause.** The system is *more* defensible for
  stopping here, not less ambitious: a detected, classified, feature-attributed disagreement is
  a claim that can be checked. An explained one cannot be, at this cohort size, on this
  evidence. The boundary is drawn where the artefact's support ends — which is the same
  discipline D-016 applies to documents, applied to the product's output.

- **The quality of each disagreement class travels with the result.** Per owner's ruling, and
  in the same discipline as D-024's coverage line: the honest reading is rendered *with* the
  finding, not on a separate page a reader may not reach. Every disagreement class carries an
  inline explanation of **what that class can and cannot support**:

  | Class | What it supports | What it does not |
  |---|---|---|
  | **Class-1 — checkable** | The comparator's ranking can be tested against an outcome already decided (e.g. an approved ADC target the baseline filtered out). A disagreement here is **evidence about the comparator**. | It is a *single instance*, not a demonstrated pattern (D-015 §2's own caveat about Trop-2). |
  | **Class-2 — hypothesis** | The structural axis orders this target differently. That is a **generated hypothesis**, on an axis no one has measured against outcome. | Nothing about whether the structural ordering is *right*. There is no outcome to check it against. |

  Rendered as inline tooltips or equivalent, not as a footnote or a separate methods page.

- **A third quality note is required, and it is the one most likely to be omitted: structure
  and sequence disagree for well-understood reasons that have nothing to do with this
  project's question.** Convergent folds, divergent sequences within a family, domain
  shuffling — all produce structure/annotation divergence, and all predate this work by
  decades. A disagreement explicable by known homology relationships is **class-2 with a
  known confound**, and the UI must say so where the disagreement is shown.

  **Why this note specifically:** the headline *"structure and sequence disagree"* invites the
  response *"yes, and?"* — because that is the premise of structural biology, not a result of
  this project. The finding this project can support is narrower and therefore stronger:
  *these particular targets are ordered differently on a structural axis, here is the class of
  that difference, and here is what the class supports.* Without the confound note, the
  system's most eye-catching output is a rediscovery presented as a finding, and a reader who
  knows the field will notice — the same failure mode D-022 avoided by making MUC16's absence
  visible rather than silent.

- **Deep-learning justification:** This entry is about the boundary of the model's claim,
  which is part of understanding the model. D-015 §3 pre-registered two negative results
  precisely so the project could report a null honestly; D-027 does the same work one level
  up, by preventing the *presentation layer* from upgrading a detected difference into an
  explained one. A system that says "these disagree, here is the class, here is what the
  class supports" is making a defensible claim. One that says "these disagree because…" is
  making an indefensible one with the same data.

- **Consequences / follow-ups:**
  - **The UI Plan needs this**, alongside D-024's coverage surface. Both are Iteration-1
    scope; neither is in `docs/UI_Plan.md`, which predates both.
  - **A future "analyse disagreement" affordance is anticipated and deliberately deferred.**
    The owner's framing: an LLM with domain grounding could *suggest* why a disagreement
    exists and what axes of investigation it opens. **That is a different system making a
    different kind of claim**, and it needs: its own entry, a clear visual separation from
    the structural result, and explicit labelling as generated suggestion rather than
    finding. Recorded now so that when it is built it is built as a ruled addition — and so
    that its absence in this version is a **decision**, not an oversight.
  - **This entry constrains D-027's attribution output.** Feature attribution is in scope and
    must be rendered as a statement about the model ("feature 6 accounts for most of this
    target's structural rank"), never as a statement about the target ("this target has a
    more accessible epitope").

---

### D-027 — The scorer's feature set, fixed before fitting; and the extractor that computes it
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)**
- **Numbering note:** drafted as D-026, renumbered to D-027 when the Builder claimed D-026 for
  the enqueue step. Recorded because a renumbered entry is otherwise indistinguishable from a
  misfiled one.
- **Context:** D-015 §3 ruled the scorer — *a learned model over structure-derived features,
  fit against Group B* — and named four features: **pocket geometry, surface accessibility,
  epitope-region pLDDT, ECD size/shape**. It then imposed a pre-registration condition it did
  not itself discharge:

  > **Feature count fixed before fitting**, and recorded in this entry when chosen. Growing the
  > feature set after seeing results is how 22 positives get overfit.

  That count has never been recorded. Until it is, the pre-registration is incomplete and any
  fit is unfalsifiable in the specific way D-015 §3 was written to prevent — because "we used
  the structural features" can absorb any number of additions after the fact.

  `docs/TDD_v3_ADC_Focused.md` **predates D-015 and does not specify feature computation.** It
  names `adc_suitability_score` and `surface_accessibility_notes` as schema fields and
  describes pocket identification as a product capability, but contains no method. So this is
  open, not a restatement.

  **Provenance of this entry's scope (D-016).** Before drafting, the Planner proposed an
  alternative framing — a composite structural axis with the ranking target left open — over
  several exchanges. **That framing contradicted D-015 §3, which had already ruled the scorer,
  named the four features, and pre-registered the evaluation.** The error was inferring what
  the log was building toward rather than reading what it says; it is the same class as the
  three errors recorded in `docs/PREWORK-2026-07-22.md`, and the only one that a single
  existing entry would have prevented outright. Recorded here because this entry's *narrowness*
  is the finding: **the open question was never "what should the scorer rank by," it was only
  "how many features, computed how."**

  **What the fold actually yields** (`worker/runner.py`, `FoldResult` / `write_artifacts`):
  `structure.pdb`, per-residue `plddt` (0–100, rescaled), and `pae` when the model returns it.
  Every feature below must be computable from those three artefacts plus the D-023 manifest
  row. **A feature that needs anything else is out of scope for this entry**, because it would
  need a data source the project has not ruled.

---

- **Decision — the feature set is SIX features, fixed as of this entry:**

  | # | Feature | Computed from | Which D-015 §3 name it discharges |
  |---|---|---|---|
  | 1 | **ECD length** (residues folded) | manifest row | ECD size/shape |
  | 2 | **Radius of gyration**, normalised by length | `structure.pdb` CA coords | ECD size/shape |
  | 3 | **Mean pLDDT over the folded ECD** | `plddt.json` | epitope-region pLDDT |
  | 4 | **Membrane-proximal pLDDT** — mean over the C-terminal 25% of the ECD | `plddt.json` + manifest boundary | epitope-region pLDDT |
  | 5 | **Solvent-accessible surface area**, normalised by length | `structure.pdb` | surface accessibility |
  | 6 | **Largest contiguous accessible surface patch**, as a fraction of total SASA | `structure.pdb` | pocket geometry + surface accessibility |

  **Six, and the count is now fixed.** Adding a seventh after any fit has been run
  invalidates the pre-registration and must be recorded as such in a new entry — not folded
  in silently.

- **Why six, argued rather than asserted.** Group B is 22 positives. Six features is ~3.7
  positives per feature, which is already generous and is the upper end of what this labelled
  set supports. Fewer would be defensible; more would not. **The number is a judgement, not a
  derivation** — there is no threshold that makes six correct and seven wrong. What makes it
  binding is that it is fixed *now*, before any result exists to be tempted by, which is
  precisely the condition D-015 §3 imposed and did not discharge. The four D-015 names
  map to six computed quantities because two of them (ECD size/shape, epitope-region pLDDT)
  are each naturally two numbers — a size and a shape, a global and a regional pLDDT — and
  collapsing either pair would discard the distinction that makes it informative.

- **Why these and not a learned embedding.** Ruled in D-015 §3 and restated here because it
  is the entry's load-bearing constraint: *interpretability is what lets a disagreement be
  attributed to a feature rather than shrugged at.* An embedding-distance model could rank
  well and would leave every disagreement unexplainable, which would make D-015 §1's actual
  research question unanswerable.

- **Two features that were considered and REJECTED, recorded so they are not quietly added
  later:**
  - **Predicted pocket volume via a pocket-detection algorithm** (fpocket-style). Rejected for
    this iteration: it introduces a third-party tool with its own parameters and failure
    modes, and feature 6 captures the ADC-relevant part (is there a large contiguous surface
    an antibody can reach) without it. *An antibody binds a surface patch, not a cavity* —
    small-molecule pocket detection is answering a different question.
  - **PAE-derived domain-boundary confidence.** Genuinely informative, and `pae` is already
    persisted — but it is not returned by every model path (`runner.py` guards it as
    optional), so a feature depending on it would be **absent for some targets and present
    for others**, which is a coverage problem D-024 would then have to express. Deferred, not
    dismissed.

---

- **The extractor's contract:**

  **Pure given `(structure.pdb, plddt, manifest_row)`.** No network, no GPU, no database. This
  is deliberate and matches the D-023 manifest's design: it makes the extractor **fully
  fixture-testable**, which for a component that feeds a 22-positive fit is not a convenience
  but a correctness requirement.

  **Output:** one row per target — six named floats, plus the `target_id`, the fold's
  provenance hash, and an explicit `feature_version`. The version exists so that a refit
  against changed feature code is detectable rather than silent.

  **Failure is explicit, never imputed.** If a feature cannot be computed for a target (a
  malformed PDB, a zero-length span), the row records `null` **with a reason**, in the same
  discipline as D-024's `tier_reason`. **Imputing a mean would be the worst available
  option** — it manufactures a plausible number for a target we failed on, and the fit would
  never know.

- **Test surface, written before the extractor (project rule):**
  - **Determinism** — the same PDB and pLDDT yield byte-identical features across runs. The
    fit is only reproducible if this holds.
  - **A hand-checkable fixture** — a small synthetic structure with known geometry, so radius
    of gyration and SASA are verified against a computed expectation rather than against
    whatever the code happened to emit first.
  - **Feature count is SIX** — an explicit test asserting the extractor emits exactly six
    features, so the pre-registration is enforced by the gate rather than by memory. **This is
    the test that makes this entry real.**
  - **Null-with-reason, never imputed** — a malformed input produces a null and a reason
    string, and no test fixture anywhere substitutes a mean.
  - **Membrane-proximal region is derived from the manifest boundary**, not from a fixed
    residue count, so a `whole`-method target and a `sliced_ecd` target are not silently
    treated alike.
  - **`feature_version` changes when feature code changes** — pinned by a test over the
    extractor's own source hash, in the D-009 §1 red-on-change manner.

- **Properties the leave-one-out is expected to expose (appended at ruling, 2026-07-22).**
  Named now, before the fit, so a result that reveals them reads as anticipated rather than
  excused after the fact:
  - **The count is a judgement, not a derivation.** Six is ~3.7 positives per feature; the
    leave-one-out will show whether any single feature is load-bearing or whether the set is
    redundant. Neither outcome invalidates the pre-registration — both are informative.
  - **Feature 6 is the fragile one.** The largest-contiguous-accessible-patch fraction depends
    on a SASA threshold and a contiguity definition; it is the feature most sensitive to those
    choices, and the leave-one-out is where that sensitivity should surface.
  - **Features 1 and 2 are collinear.** ECD length and length-normalised radius of gyration are
    geometrically related; expect overlapping signal — dropping one may barely move the fit,
    which is a finding about the feature set, not a failure of it.
  - **Feature 4 is cross-method incomparable.** Membrane-proximal pLDDT means a different thing
    for a `whole`-method target than for a `sliced_ecd` one (D-021); the leave-one-out over the
    held-out whole set may behave differently and must not be read as though comparable.

- **Deep-learning justification:** This entry is what makes D-015 §3's pre-registration
  binding rather than aspirational. A fixed feature count, enforced by a test, is the
  difference between a small-sample fit that can produce a falsifiable negative result and one
  that can absorb any outcome. D-015 §3 named **two** negative results — including the
  non-obvious one, that a strong correlation with the comparator's evidence score is *also*
  null, because it means the features proxy attention-and-precedent rather than structure.
  Neither negative is interpretable if the feature set moved during fitting.

- **Consequences / follow-ups:**
  - **The extractor needs folds**, and folds need the enqueue step and worker. This entry is
    rulable now and buildable only after the pipeline runs end to end. Ruling it now is
    deliberate: the feature count must be fixed **before** any fit, and the cheapest moment to
    fix it is before there is a result to be tempted by.
  - **Feature 4 depends on the boundary method.** For `whole`-method targets (the 13 held out
    per D-024) the "membrane-proximal 25%" is a different thing than for a sliced ECD. Those
    targets are already held out of cross-method ranking claims (D-021), so this is consistent
    — but the extractor must not silently compute it as though it were comparable.
  - **`feature_version` should be persisted alongside `inference_settings`**, so a stored score
    can always be traced to both the fold that produced it and the feature code that read it.
  - **Group C (TROP2, HER3, CLDN18.2) runs through the identical extractor**, with no
    special-casing — otherwise the out-of-cohort probe is not a probe.

---

### D-026 — Enqueue: the manifest becomes protein_analyses + jobs (the pull queue is fed)
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)** — ruled by the Builder; the three forks below decided
  here with justification, not inherited.
- **Context:** D-023's manifest produces a reviewable routing table but writes nothing. D-004's
  pull queue can be *claimed* but has no `enqueue` — the seam is claim/complete/fail/reap_stale
  only. This entry is the step between: turn each foldable manifest row into a `protein_analyses`
  row (WHAT to fold) plus a `jobs` row (a pending unit the local worker claims). It is **the first
  code in the project to write application rows** — which makes it the first exercise of a seam
  named-but-never-run (see Hazard).
- **Decision — who is enqueued.** The 80 targets with disposition `ranked` or `held_out` are
  folded; the 2 `excluded` (MUC16 `Q8WXI7`, FAT2 `Q9NYQ8`) get **no job** (D-022 — they fold on no
  card). **Held-out means held out of the RANKING, not of folding** (D-021/D-024): the 13
  `whole`-method targets are folded — they populate the coverage surface and the single-target
  view — but do not enter cross-method ranking claims.

  **Named as a deliberate spend:** those 13 held-out folds run on rented hardware
  (whole-sequence, mostly rental-tier) and contribute **nothing to the ranking**. That is the
  intended cost of an honest coverage surface and a working single-target view, recorded so it is
  not a surprise on the invoice. If cost ever forces a cut, the held-out folds are the first
  candidates — never the ranked ones.
- **Ruling (2026-07-22), forks decided by the Builder with justification:**

  **(i) The sequence and its UniProt release are fetched and STORED at enqueue — the job is
  self-contained.** Not "store the accession and let the worker fetch at fold time."
  Reproducibility is this project's differentiator, and **UniProt revises sequences**: a worker
  fetching months later could fold a *different molecule* than the manifest reviewed, silently.
  The analysis records the exact residues folded **and the release they came from**, so provenance
  names *which* UniProt. Cost: 80 one-time REST fetches — cheap, and it keeps new network code out
  of the not-yet-built worker orchestration. The fetcher is injected, so tests stay hermetic.

  **(ii) The fold target is the LARGEST extracellular span — inherited, not a fresh choice.**
  `largest_span_aa` is what the whole cohort was bucketed on (D-020) and what every routing and
  coverage decision keys on (D-024). Folding any *other* span would make the routing and the fold
  disagree about what was measured, so this is consistent-by-construction, not a new rule. The
  span folded (`[start,end]`, or `whole`) is **recorded on each row**, so the deferred
  ADC-relevant-span refinement can later identify exactly what changed. Multi-span selection beyond
  "largest" is out of scope here.

  **(iii) One `ranking_runs` row per enqueue; idempotent on (cohort version, accession).** Each
  enqueue mints a `ranking_runs` row stamped with the cohort's `target_list_version` (the
  Kathad-82 revision, D-020). Analyses/jobs are keyed idempotently, so a **second run reports
  "exists" and writes nothing new** — the enqueue is the irreversible step D-023's manifest-first
  guard existed to protect, so re-running it must be safe.
- **`inference_settings` per tier (D-018 / S-003 — recorded, not re-decided):** `local` →
  `int8`/`chunk_size=64`; `rental` → `fp16`/`chunk_size=None`; `MODEL_REVISION` pinned
  (`75a3841…`), `source ∈ {sliced_ecd, whole}`, and the ECD `[start,end]` when sliced. These are
  the reproducibility fields D-004/D-015 §1a require; the worker fills the post-fold half (pLDDT,
  CA count, folded_at).
- **Deep-learning justification:** this is the plumbing that turns a reviewed routing table into
  actual neural-inference work — where "we run ESMFold ourselves" (D-003/D-004) becomes jobs a GPU
  claims. Storing the exact input + release + fold parameters is what makes each fold
  **reproducible and legible to a grader** (D-015/D-016).
- **⚠ HAZARD — the app-runtime `search_path` seam, first exercised here.** env.py's `search_path`
  is proven on real Postgres (D-017); the **app-runtime connection is a different connection and
  has never written a row.** The enqueue is the first to do so. Its writes
  (`protein_analyses`/`jobs`/`ranking_runs`) do **not** reference the `vector` type, so they do not
  by themselves exercise the pgvector `extensions`-schema resolution — that specific seam stays
  unproven until vector-touching app code runs, stated so it is not mistaken for covered. What IS
  newly exercised is the app-runtime **write/commit path on real Postgres**, and it is tested on a
  **real connection, not a mock** (`test_enqueue_commits_on_real_postgres` re-reads on a fresh
  connection — the env.py-bug class: a green insert that silently rolled back).

  **Related, owner's call:** the Postgres integration job is **still not a required check**. Under
  D-025 merge-on-green, a migration bug can merge green — in the session most likely to produce
  one. **This PR writes no migration** (the tables exist, D-019), so it adds no such exposure; but
  the promotion decision remains the owner's, and it is the live constraint on D-025's value.
- **Test surface (written before the code):** 80 enqueued / the 2 excluded get no job; a re-run is
  idempotent (reports "exists", counts unchanged, one `ranking_run`); `inference_settings` is
  tier-correct (int8/64 local, fp16/None rental, revision pinned); slice provenance recorded
  (source + ECD bounds, or whole) and the UniProt release stored; every `jobs.analysis_id` FKs a
  real `protein_analyses` row; and — on a **real** connection — the rows commit.
- **Provenance (D-016).** Ruled against `db/models.py` (the jobs/protein_analyses/ranking_runs
  schema), `worker/runner.py` (`FoldProvenance` fields + `MODEL_REVISION`), `core/manifest.py` (the
  dispositions + slice bounds), and D-004/D-018/D-019/D-020/D-021/D-022/D-024 — read from HEAD.
- **Consequences / follow-ups:**
  - The worker's job-pull orchestration (claim → the input is already stored → fold → upload) is
    the next build; D-004's pull contract governs it.
  - `analysis_embeddings` (the vector path) is written later, by the scorer — that is when the
    app-runtime `search_path` seam finally bites and must be handled.
  - Group C reconciliation and any approved-ADC-list authority are out of scope here (owner-named
    source pending).

---

### D-025 — Merge-on-green authorization, and what it does not authorize
- **Date:** 2026-07-22
- **Status:** Accepted
- **Context:** The Builder (Code) asked whether the standing merge-on-green authorization from
  the JARVIS project carries over to PharmFoldMDK. The question was asked in chat, where an
  answer would have been invisible to every future session. Governance that lives only in a
  conversation is not governance (D-002).
- **Decision:** **Merge on green is authorized.** A PR whose required checks pass may be merged
  without waiting for owner review.
- **What green means here, stated because the phrase is doing real work:** the D-008 gate —
  the full suite, functional and user tests, plus the D-013 hash-locked install. Nothing
  reaches Fly.io that has not passed it first. Merge-on-green is an authorization to *not
  wait*; it is not a lowering of the bar, and it does not make an unproven check sufficient
  merely because it is green.
- **What it does NOT authorize:**
  - **Merging work whose decision entry does not exist.** THE RULE is unchanged: the log leads
    the code. A green PR that implements an unruled decision is still incomplete, and green
    does not substitute for a ruling. D-024's ordering fight this morning is the live example —
    the manifest could have been built green against an unratified contract.
  - **Changes to the gate itself.** Under D-008, a change to the required status check is
    exactly the class of change that gets *proven* RED→GREEN, not merged on the strength of a
    passing run.
  - **Silent scope growth.** A PR that grows beyond its entry needs the entry amended, in the
    same PR (governance rule 2).
- **Deep-learning justification:** neutral — this is a throughput decision. Recorded because
  its *absence* from the log was the defect: the Builder was blocked on an unwritten rule, and
  the next session would have been blocked identically.
- **Consequences:**
  - The **D-017 promotion bar was the live constraint on this entry's value — now CLOSED by
    D-032 (2026-07-22).** Merge-on-green is only as strong as the set of *required* checks, and
    the Postgres integration job was not one of them, so until it was promoted a migration bug
    could merge green. D-032 checked the D-017 bar against the job's actual run history (criterion
    2 confirmed by the Builder, not assumed) and promotes the job to a required check, effective
    before the transport PR — lifting the cap this consequence named on itself. *(The bar was
    never "a vibe without a number": D-017 §"How far" stated it explicitly; it had simply gone
    unchecked. See D-032.)*
  - Two seams remain outside any gate and are unaffected by this entry: the **app-runtime
    `search_path`** (never run) and **`worker/requirements.txt`** (outside the lock-file
    guarantee by design, D-018; `accelerate` unpinned).

### D-024 — Coverage and limitations are a first-class UI surface, not a footnote
- **Date:** 2026-07-21
- **Status:** **Accepted (2026-07-22)** — ruled with a **structured coverage object**: a
  three-cell disposition partition (`ranked` / `held_out` / `excluded`) plus two breakout
  subsets (`unmeasured_tier`, `no_topology`); `untested` routed to **rental with its reason
  recorded** and **ranked, not held out**; SDK1 bucketed but **pinned by a named test**. See
  "Ruling" below, including the §(i) correction of 2026-07-22.
- **Context:** Four separate decisions have now each produced a constraint that **must be
  visible in the interface**, and they have been accumulating as scattered consequences
  rather than as a designed surface:
  - **D-015 §1a** — disagreement classes must be visually distinct; a class-1 (checkable
    against decided outcomes) and a class-2 (hypothesis on an axis never measured) look
    identical in a sorted table and mean entirely different things.
  - **D-021** — *"N ranked, M held out"* travels with **every** ranking, as part of the
    result. A cohort of 82 that quietly becomes 69 invalidates the comparison.
  - **D-022** — named exclusions must be **visible, not silently missing**. MUC16 is CA-125;
    a reviewer who knows the field notices its absence immediately.
  - **D-020 / the ECD measurement** — 16% of the cohort has no sliceable topological domain
    and is folded by a different method.

  Left as consequences of four entries, these will be implemented as caveats if they are
  implemented at all. **They are the honest reading of the result and belong in the same
  screen as the result.**

  There is also a finding here that is genuinely interesting rather than merely
  disqualifying, and it would be lost as an apology: **two targets cannot be folded by this
  method on any hardware that exists.**

- **Decision:** The application carries a **Coverage & Limitations surface** as a designed,
  first-class deliverable — not a disclaimer block. It has two homes:

  **(a) Inline, wherever a ranking is shown.** The coverage line is rendered with the
  ranking itself: *"82 targets · N ranked · M held out (whole-chain method) · K excluded
  (named)."* Held-out and excluded rows are reachable from that line, not hidden. Boundary
  method (`sliced_ecd` / `gpi_predicted` / `whole`) is visible per target, and disagreement
  class is visually distinct per D-015 §1a.

  **(b) A dedicated Limitations page**, written as findings with their reasoning — the
  measured constraints of this approach, discovered rather than assumed.

- **The write-up that makes this worth doing — "What we cannot fold, and what it would
  take":**

  **MUC16 (Q8WXI7, 14,451 aa — CA-125) and FAT2 (Q9NYQ8, 4,030 aa)** cannot be folded as a
  single sequence. This is stated as a **property of the method**, with three routes
  addressed honestly:

  1. **Bigger hardware does not solve it.** ESMFold's memory scales roughly quadratically
     with sequence length. An 80 GB card buys perhaps 1.5× the length over a 48 GB one;
     MUC16 is ~30× the measured local ceiling. **There is no card.** *This is the point most
     readers will assume their way past, so it is stated first.*
  2. **Domain decomposition is the real answer, and may be the more correct method
     anyway.** MUC16 is a tandem-repeat mucin — dominated by ~60 repeats of a ~156-residue
     SEA domain plus a C-terminal membrane-proximal region. Folding the repeat unit once and
     the C-terminal domain separately is arguably **better science** than folding 14,451
     residues as a unit, because the global arrangement of a repeat array is not something
     single-sequence prediction recovers meaningfully. **For ADC purposes the relevant
     epitope region is the membrane-proximal portion** — the part an antibody can reach.
     Decomposition is therefore not a compromise here; it is plausibly the right method,
     deferred for scope rather than rejected on merit (D-022).
  3. **A different predictor changes the claim.** Models with different memory
     characteristics exist, but D-003's graded claim is that **we run ESMFold**, and mixing
     predictors across a cohort breaks the comparability D-021 exists to protect.

  **Why this is a finding and not an apology:** it demonstrates something a purely
  computational reader would miss — that **protein size is a real constraint on
  structure-based screening, and the constraint is biological rather than budgetary.**
  Tandem-repeat mucins are an entire class. CA-125 is the most-used ovarian-cancer biomarker
  in clinical practice, and it lies outside what single-sequence folding can reach. That is a
  genuine limitation of the whole approach, **discovered by measurement rather than
  anticipated** — and for a deep-learning course it is arguably the most instructive item on
  the page: *here is where the method stops working, here is why, and here is what it would
  cost to extend it.*

- **Deep-learning justification:** Direct, in two ways. First, the limits of a model are part
  of understanding the model; a system that reports its own coverage honestly is doing more
  DL-relevant work than one that silently drops what it cannot handle. Second, this surface
  is what makes D-015's claim discipline **enforceable** rather than aspirational — the
  class-1/class-2 distinction and the coverage line are worthless if the interface renders
  them identically.

- **Ruling (2026-07-22):** Ruled against the measured cohort in `data/cohort_82_ecd.csv`, not
  against this entry's own prose. The distribution the ruling is made on — recomputed from the
  CSV, 82 rows, partitioning cleanly:

  | `bucket_by_largest` | n | Meaning |
  |---|---|---|
  | `local` | **40** | largest sliceable span ≤ 440 aa (measured local ceiling, S-004/S-005) |
  | `rental` | **16** | ≥ 630 aa — includes the two named exclusions |
  | `untested` | **13** | in the **(440, 630) aa** band — unmeasured against the **local** ceiling |
  | `unknown` | **13** | 12 no-topology + SDK1 |
  | | **82** | |

  **(i) The coverage line is STRUCTURED, not prose — a THREE-CELL partition plus TWO
  BREAKOUTS.** The drafted line (`82 · N ranked · M held out · K excluded`) is right about the
  partition and wrong to stop there: it cannot express that 13 targets are routed on an
  unmeasured ceiling, or that 13 have no parseable topology. The ruled shape is a structured
  object the UI renders — a string cannot be asserted against an invariant, an object can:

      { denominator:      82,
        # DISPOSITION PARTITION — mutually exclusive, exhaustive, sums to denominator
        ranked:           N,
        held_out:         M,
        excluded:         K,
        # BREAKOUTS — subsets that CUT ACROSS the partition; they do NOT sum into it
        unmeasured_tier:  U,   # routed to rental on an unmeasured local ceiling; these are RANKED
        no_topology:      T }  # no parseable extracellular span; these are HELD OUT

  **The binding invariant is `ranked + held_out + excluded == denominator`, and only that.**
  Measured: **82 = 67 ranked + 13 held out + 2 excluded**, with `unmeasured_tier = 13` (a
  subset of `ranked`) and `no_topology = 13` (a subset of `held_out`). The prose rendering is a
  view of this object, never a separately-maintained sentence.

  **Correction, 2026-07-22, raised by the Builder against the entry rather than around it.**
  This clause first read *"the coverage line has FIVE states… the states sum to the
  denominator,"* listing all five alongside `denominator`. That is **not consistent with
  §(iii) or with test-surface item #7**: if `unmeasured_tier` were a partition cell, the 13
  would not be in `ranked`, which is precisely what §(iii) rules they must be. The error was
  the Planner's — the word *state* was used for two different things (a disposition and a
  reason-flag) in a single object, and an implementer could reasonably have built the strict
  five-cell version and produced a coverage line that silently understates ranked coverage by
  16%. **The distinction being drawn is the one D-024 exists to protect:** *disposition* is
  what a target contributes to a ranking claim; *tier* and *topology* are why it was routed as
  it was. They are orthogonal, per §(iv), and flattening them into one partition re-introduces
  exactly the tier/comparability conflation §(iv) forbids.

  **(ii) The denominator is 82 — and 79/3 was never a competing number.**
  `data/cohort_82_accessions.txt` records *79 clean single-hit + 3 resolved by the primary-match
  rule (ATP2B2/LRRN1/SMO)*. That is **mapping confidence**, not cohort size; both the ECD and
  mapping CSVs carry 82 rows. The 3 primary-match resolutions travel into the manifest as a
  **provenance flag on those rows**, per D-020 — visible, not averaged away.

  **(iii) The 13 `untested` targets route to RENTAL, with the reason recorded in the row.**
  Owner's ruling: completeness over thrift; the rented GPU is available and the 13 are not to
  be excluded. But the manifest **must not render this indistinguishable from a measured
  routing.** The row carries `tier=rental, tier_reason=unmeasured_local_ceiling` — the same
  discipline as D-023 (iii)'s self-labelling `UNMEASURED, conservative` config value, and for
  the same reason: *an unlabelled `rental` looks measured.* `scripts/ecd_lengths.py:46-52`
  deliberately buckets against **both** bounds rather than pretending to a single number
  ("The exact ceiling within (440, 630) is UNMEASURED"); routing these to rental without the
  reason would spend that honesty silently.

  **They are folded by `sliced_ecd` and are therefore RANKED, not held out.** This is the
  correction to the first pass of this ruling, and it matters: *held-out* is a
  **method-comparability** category (D-021), not a tier category. A target folded by the same
  boundary method as the local 40 is comparable to them regardless of which card did the
  arithmetic. Holding out 13 `sliced_ecd` targets would drop real, comparable data points from
  the ranking for no methodological reason — and would understate coverage by 16%.

  **(iv) `held_out` means boundary-method incomparability, and nothing else.** The
  `whole`-method targets are held out of cross-method ranking claims per D-021 §1a. Tier is
  orthogonal: a rental-tier `sliced_ecd` fold is ranked; a local-tier `whole` fold is held out.
  Conflating the two is what produced the error corrected in (iii).

  **(v) SDK1 (`Q7Z5N4`) is bucketed with the no-topology set, and PINNED BY A NAMED TEST.**
  Owner's ruling: bucketed, not given its own state — but not buried either. Its span is
  `None-2009(None)`: **a null start and a null width**, i.e. an extracellular annotation that
  exists but carries no numeric bounds. The hazard is specific and mechanical: it **passes** an
  `n_spans == 0` check and **fails** a `has_numeric_bounds` check, so a natural implementation
  admits it as annotated and then slices on `None`. A test naming `Q7Z5N4` explicitly asserts
  its null-bounds span is never parsed as a boundary — the same shape as
  `test_analysis_id_has_no_fk_yet`, so the case cannot be silently outlived if the bucketing
  is ever revisited.

  **(vi) The inline coverage line ships in Iteration 1. The Limitations page ships in
  Iteration 1 as well.** Owner's ruling. Both homes from the Decision above are Iteration-1
  scope; the page's per-target numbers are populated from the manifest rather than written by
  hand, so it is buildable as soon as the manifest exists.

  **What this ruling deliberately does NOT decide:** the exact local ceiling within
  (440, 630) aa. Routing the 13 to rental makes that measurement *unnecessary for coverage*,
  not *unnecessary*. It remains open and cheap (~535 aa bisection, local hardware, logic
  already unit-tested in `worker/ceiling_probe.py`), and if run, it moves some of the 13 from
  `tier_reason=unmeasured_local_ceiling` to a measured `local` — a cost reduction, not a
  correctness fix. Recorded, not scheduled.

- **Test surface fixed by this ruling** (written before the manifest, per the project rule):
  - **Partition invariant** — every accession has exactly one **disposition**, and
    `ranked + held_out + excluded == 82` (measured: 67 / 13 / 2). Asserted on the disposition
    partition **only**; `unmeasured_tier` and `no_topology` are breakout subsets and must NOT
    be summed into it. A test that adds all five fields and expects 82 encodes the ambiguity
    corrected in §(i) and would force the 13 out of `ranked`.
  - **Breakout containment** — `unmeasured_tier` ⊆ `ranked` and `no_topology` ⊆ `held_out`,
    asserted as set containment rather than count equality, so the relationship survives a
    change in either number.
  - **Source-bucket distribution** — the `bucket_by_largest` tally in `cohort_82_ecd.csv` is
    40 / 16 / 13 / 13. This is the **input** measurement, distinct from the disposition
    partition above; pinned so a change in the CSV reddens rather than silently re-routes.
  - **Named exclusions present, not absent** — MUC16 (`Q8WXI7`) and FAT2 (`Q9NYQ8`) appear as
    **excluded rows with a stated reason**. A test asserting they are *missing* would encode
    the exact bug D-022 exists to prevent.
  - **`tier_reason` is populated for all 13 `untested`→rental rows**, and a bare `rental` with
    no reason is a failure.
  - **GPI subset routes to `whole`, held out** — MSLN (`Q13421`) and GPC1 (`P35052`) route to
    `whole`, **not** `gpi_predicted`, per D-023 (ii)'s deferral. Pinned because an implementer
    reading D-021 first will reach for a method that does not yet exist.
  - **SDK1 (`Q7Z5N4`)** — null-bounds span never parsed as a numeric boundary.
  - **Primary-match provenance** — ATP2B2, LRRN1, SMO carry their D-020 mapping flag.
  - **Ranked ≠ local-tier** — a test asserting the 13 rental-tier `sliced_ecd` targets are in
    `ranked`, so a future refactor cannot quietly re-conflate tier with comparability.

- **Provenance of this ruling (D-016).** Made against `data/cohort_82_ecd.csv`,
  `data/cohort_82_accessions.txt`, `scripts/ecd_lengths.py:46-52`, and
  `worker/ceiling_probe.py`'s docstring — read from the tracked tree at HEAD, not from the
  decision entries' narrative. **Two Planner errors were caught this way while preparing it,
  both of the same class**, and both are recorded in `docs/PREWORK-2026-07-22.md` rather than
  quietly fixed: (1) the borderline set was first taken from D-022's prose (NOTCH2, PTPRZ1,
  LRP6, JAG1) when the CSV shows those are oversize-rental; (2) the corrected 13-target band
  was then attributed to the **A6000** probe when `ecd_lengths.py` shows the (440, 630) bounds
  are the **local** ceiling and `ceiling_probe.py` is measuring a different ceiling for a
  different set. *A decision entry's prose describes a measurement; it is not the measurement.*

- **Consequences / follow-ups:**
  - **The UI Plan (`docs/UI_Plan.md`) predates all of this** and has no limitations surface.
    It needs updating, or superseding, when the application is scoped.
  - **The coverage line must be computed, not hand-written.** It comes from the orchestrator
    manifest (D-023), so it is always current with the actual routing rather than a number
    someone remembered to update.
  - **If decomposition is ever built (D-022), this page changes** — MUC16 moves from
    "cannot" to "folded by decomposition," and the finding becomes a *method extension*
    rather than a limit. Written so that change is an edit, not a rewrite.
  - **Fold provenance belongs on the same surface**: model revision, dtype, `chunk_size`,
    mean pLDDT, boundary method, and whether the sequence was truncated — surfaced from
    `inference_settings` rather than left in JSONB. Per D-015, this is also what makes the
    "we ran this ourselves" claim legible to a reader, including a grader.
  - **Numbers to fill in once the orchestrator manifest exists:** exact ranked / held-out /
    excluded counts. Stated here as pending rather than estimated.

---

### D-023 — The orchestrator: cohort → boundary → tier → job (Accepted)
- **Date:** 2026-07-21
- **Status:** **Accepted (2026-07-21)** — all three choices ruled; the orchestrator emits a
  reviewable manifest first, defers the `gpi_predicted` predictor, and treats the A6000 ceiling
  as config with a self-labelling default. See "Ruling" below.
- **Context:** D-018 split the **runner** (folds one sequence) from the **orchestrator** (selects
  the right sequences, slices them at the right boundaries, routes them to the right tier) on
  correctness-condition grounds. Every input the orchestrator needs now exists: the cohort of
  record (D-020), the three-way boundary methods (D-021), the routing tiers incl. named
  exclusions and the ceiling-as-measurement (D-022), and the queue + `protein_analyses` (D-019).
  This scopes the orchestrator; it is not built until the choices below are ruled.
- **Correctness condition (D-018, restated):** the orchestrator is right iff the *right set* of
  sequences is selected, each sliced at the *right boundary by the right method*, and routed to
  the *right tier* — independently of whether any fold succeeds (that is the runner's condition).
- **Pieces:**
  1. Load the cohort of record (`data/cohort_82_accessions.txt`).
  2. Per target: fetch UniProt (sequence + `Topological domain` features) — reuse
     `scripts/ecd_lengths.py`'s fetch/parse rather than re-derive it.
  3. **Boundary method (D-021, three-way):** an extracellular topological span → `sliced_ecd`;
     the GPI-anchored subset → `gpi_predicted` (**predictor deferred — see choice (ii)**);
     otherwise → `whole`.
  4. **Route to tier (D-020/D-022):** largest sliceable span ≤ 440 → **local**; the named
     oversize (MUC16, FAT2) → **excluded**; between the local ceiling and the A6000 ceiling →
     **rental**; borderline decided by the **A6000 ceiling config** (iii); `whole`/unsliceable →
     folded but **held out of cross-method ranking claims** (D-021's binding constraint).
  5. Emit the result — **choice (i)**.
- **Choices for a ruling:**
  - **(i) Output: a routing MANIFEST first, or enqueue jobs directly?** *Recommend: manifest
    first* — a deterministic, reviewable table (target → method, span, tier, held-out flag,
    exclusion reason) that is **fully testable with UniProt fixtures, no queue/GPU/DB needed**,
    and can be reviewed before a single job is created. A thin enqueue step (into the D-019 queue
    + `protein_analyses`) and the worker↔app pull contract (D-004) are a *separate* build on top.
    The manifest is also where D-021's "N ranked, 13 held out" coverage line is computed.
  - **(ii) The `gpi_predicted` predictor: in scope, or deferred?** *Recommend: deferred* — D-021
    ruled it a separate scoped build (a SignalP/GPI DL component). Until it lands, the orchestrator
    routes the GPI subset (MSLN, GPC1, …) as `whole` (held out of ranking), and **upgrades** them
    to `gpi_predicted` when the predictor exists. This keeps the orchestrator shippable without
    blocking on a new model.
  - **(iii) The A6000 ceiling is config, not hard-coded.** Default conservative until
    `worker/ceiling_probe.py` (D-022, owner-run) measures it; borderline targets route on the
    config value, and the manifest records which ceiling produced the routing.
- **Testing:** the routing/slicing **decision** is pure and deterministic given a UniProt
  response, so it is fixture-tested on the gate — no live UniProt, no GPU, no DB for the manifest
  path. This is the whole payoff of the D-018 split: the orchestrator's correctness surface is
  exactly the part CI can cover.
- **Deferred / depends on:** the A6000 ceiling (probe, owner-run) for exact borderline routing;
  the SignalP/GPI predictor (D-021) for `gpi_predicted`; the worker↔app pull contract (D-004) +
  the enqueue step for the manifest→fold path.
- **Ruling (2026-07-21):**
  - **(i) Manifest first, not direct enqueue.** The orchestrator emits a deterministic routing
    table — target → boundary method, span, tier, held-out flag, exclusion reason — **reviewable
    before anything irreversible happens**. Enqueueing directly means the first sight of the
    routing decisions is when jobs already exist. This is also where D-021's coverage line
    ("N ranked, M held out, 82 minus named exclusions") is computed. The enqueue step + D-004
    pull contract are a separate build on top.
  - **(ii) The `gpi_predicted` predictor is deferred.** Route the GPI subset as `whole`/held-out
    and upgrade once SignalP/GPI is built as its own scoped piece. Blocking the orchestrator on a
    new model would repeat the runner/orchestrator conflation D-018 was written to avoid.
  - **(iii) The A6000 ceiling is config, defaulting conservative and labelled `UNMEASURED,
    conservative` in the config itself — not in a comment.** An unlabelled `2000` looks measured;
    the label must ride in the value a reader sees, so the routing cannot be mistaken for having
    been calibrated against a real fold. The probe (D-022) replaces the label with a measured
    number when it runs.
- **Deep-learning justification:** it is the mechanism that turns the 82 into the folds the D-015
  scorer consumes; its correctness (right boundary method per target, held-out set reported) is
  what keeps the ranking comparing like with like rather than mixing domain slices and whole
  chains.

---

> **D-021 and D-022 are a PAIR, logged together on purpose (D-020's measurement raised both).**
> They interact: decomposition (D-022) and the no-topology boundary rule (D-021) are both "this
> protein needs boundaries UniProt topology does not give us," so a decomposition mechanism, if
> built, would serve both — it supersedes D-022's first-pass exclusions and part of D-021's
> `whole` subset. Scope them together, not sequentially. **Both were ruled Accepted 2026-07-21**
> (see each entry's Ruling). Routing is now defined for every target — `local` / `gpi_predicted` /
> `whole` / rental / **named-excluded** — closing the gap that "route to a tier" assumed every
> target had a tier when MUC16 did not. **Remaining prerequisite before the orchestrator's rental
> routing is exact:** the A6000 single-fold ceiling (D-022), a GPU-host measurement.

### D-022 — Oversize targets: decompose or exclude
- **Date:** 2026-07-21
- **Status:** **Accepted (2026-07-21)** — exclude the definitively-oversize for the first pass,
  **named in this entry**; measure the A6000 ceiling to route the borderline; defer decomposition.
- **⚠ Amended by D-042 (2026-07-23): the ceiling is measured.** On a 95 GiB card, **unchunked**,
  the ceiling sits between **1,034 aa (folds) and ~1,350 aa (does not)** — and the limit is the
  trunk's O(L³) triangular attention, not raw VRAM, so *chunking*, not a bigger card, is the fix.
  See "Ruling" below.
- **Context:** D-020 measured the rental bucket (16 targets, largest ECD span ≥ 630 aa) and found
  it **non-uniform**. Two targets exceed single-sequence ESMFold feasibility on **any** card —
  **MUC16 (14 451 aa; CA-125)** and **FAT2 (4 030 aa)** — because the limit is **sequence length,
  not model weights**, so a 48 GB A6000 does not help. Several more sit near the edge
  (NOTCH2 1652, PTPRZ1 1612, LRP6 1351, JAG1 1034). D-011's ~$0.25 rental estimate, scoped to a
  handful of HER2-class targets, does not survive this.
- **Unmeasured prerequisite (same shape as the local ceiling once was):** the **A6000
  single-fold ceiling** is unknown. MUC16/FAT2 are over any plausible ceiling (decide regardless);
  the borderline targets cannot be routed until it is measured.
- **Options:**
  - **(a) Domain decomposition** — fold sub-domains separately. Real work, and it introduces a
    boundary-selection problem of its own (which is also D-021's problem — see the pairing note).
  - **(b) Exclusion** — drop the oversize targets from the folded set. Cheap. **The exclusions
    must be named and reported as coverage** — a cohort of 82 that silently becomes 78 is exactly
    the quiet drift that invalidates a comparison.
- **Recommendation (for a ruling):** for the first ranking pass, **exclude the definitively-
  oversize (MUC16, FAT2), named**, and **measure the A6000 ceiling** to route the borderline ones;
  treat decomposition as a later enhancement rather than a blocker. Coverage is then reported as
  "82 minus the named exclusions," never a silently smaller number.
- **Deep-learning justification:** indirect — this determines which targets have folds at all, and
  therefore which the D-015 scorer can rank; an unnamed exclusion would silently bias the ranking.

#### Ruling (2026-07-21)

**First-pass exclusions, named here so they are visible in the record, not silently missing:**

| Accession | Gene | Largest ECD span | Why excluded (first pass) |
|---|---|---|---|
| `Q8WXI7` | **MUC16** | 14 451 aa | Oversize — unfoldable as one sequence on any card. **This is CA-125, the most-used ovarian-cancer biomarker in clinical practice**; a field reviewer will notice its absence immediately, so it is named "excluded, oversize, first pass" rather than left quietly missing. |
| `Q9NYQ8` | **FAT2** | 4 030 aa | Oversize — beyond single-sequence fold feasibility. |

- **The A6000 single-fold ceiling is measured next** (same shape and method as the local ceiling,
  S-004/S-005; cheap on per-second billing) to route the borderline targets (NOTCH2 1652,
  PTPRZ1 1612, LRP6 1351, JAG1 1034, …). Until it is known, only the two definitely-oversize are
  excluded; the borderline are unrouted, not assumed.
- **Coverage is always reported as "82 minus the named exclusions"** — never a silently smaller
  ranked cohort (this ties to D-021's reporting constraint).
- **Decomposition is deferred, not rejected.** It is real work with its own boundary-selection
  problem, and — per the pairing note — a decomposition mechanism would also subsume part of
  D-021's `whole` subset (the multi-domain giants). So if it is ever built, it is scoped to serve
  **both** D-021 and D-022, and it supersedes both the first-pass exclusions here and the `whole`
  method there.

### D-021 — A second ECD-boundary method for the no-topology targets
- **Date:** 2026-07-21
- **Status:** **Accepted (2026-07-21)** — ruled with a **three-way method distinction** (not the
  two-way lean originally proposed) and a hard reporting constraint. See "Ruling" below.
- **Context:** D-020 measured **13 of 82 (16%)** with no usable extracellular topological-domain
  annotation, so D-009 §2 cannot slice them. At 16% this is a **routine path, not an edge case** —
  D-009 §2's "fold whole sequence + warn" fallback was written for a rarity. The 13 are **not
  homogeneous:**
  - **GPI-anchored ADC targets** — **MSLN** (mesothelin), **GPC1** (glypican-1) — whose ECD is
    essentially the whole mature chain (signal peptide trimmed, GPI-attachment signal removed);
  - **large multi-domain proteins UniProt does not annotate topologically** (IGF2R 2491, TLR3 904);
  - **multi-pass transporters** whose extracellular parts are small loops, not an ADC epitope
    domain (SLC44A3, UGT8);
  - **SDK1** — an extracellular annotation with **no numeric bounds**: neither sliceable nor
    cleanly unsliceable. Named separately so it is not silently bucketed with the others.
- **The stakes (same class as §1a's truncation exclusion):** a fold produced by a *different
  boundary method* is a different **kind of input** — a whole chain rather than a domain. If 16%
  of the cohort's structural features are computed on a different kind of input, **D-015's ranking
  is comparing two things.** Whether that is acceptable, correctable, or grounds for exclusion is
  the decision.
- **Options:**
  - **(a) Predicted boundary** — signal-peptide prediction (SignalP/Phobius) plus TM / GPI-anchor
    prediction (DeepTMHMM/NetGPI) to derive an ECD. For the GPI-anchored subset, mature-chain-
    minus-signal-peptide *is* a legitimate, domain-comparable ECD. Adds a prediction step (more DL,
    its own error), and does not fit the transporters (small loops) or the giants cleanly.
  - **(b) Whole-sequence with a provenance flag** — fold the whole mature chain, `source=whole`
    (the runner already records this), and **exclude from cross-method ranking claims** per §1a.
    Cheap, no new model, but produces folds not comparable to domain slices.
- **Binding requirement whichever is chosen (§1a):** the ranking **must know which boundary method
  produced each fold** (`source ∈ {sliced_ecd, predicted_ecd, whole, …}`), and a cross-method
  comparison must be visibly flagged — the same discipline as truncation exclusion. The runner's
  provenance field is where this is recorded.
- **Recommendation (for a ruling):** treat the 13 as the heterogeneous set they are —
  **predicted-boundary (a) for the GPI-anchored subset** (a real domain-comparable ECD),
  **whole-sequence-flag (b) elsewhere**, all provenance-tagged and held out of cross-method
  ranking claims until validated. This needs a ruling: it introduces a new predictor (a DL
  component, which the Prime Directive welcomes but which is its own work) and a per-fold
  provenance class the scorer must respect.
- **Deep-learning justification:** direct if (a) — a learned signal-peptide/GPI predictor is
  itself load-bearing neural work; and either way this governs whether 16% of the cohort produces
  comparable structural features, which is a precondition for the D-015 ranking meaning anything.

#### Ruling (2026-07-21)

**A three-way method distinction, not two.** The 13 are not one class, and a GPI-anchored ECD is
not a whole-chain fold — it is a **domain slice by a different route** (mature chain after signal-
peptide and GPI-anchor-signal removal), closer to a topology slice than to folding a whole
multi-domain protein. So the boundary **method** each fold used is recorded three ways, not two —
free to record and more informative for §1a:

| `source` | method | comparability |
|---|---|---|
| `sliced_ecd` | UniProt `Topological domain` = Extracellular (D-009 §2) | the reference class |
| `gpi_predicted` | SignalP + GPI-anchor prediction → mature-chain ECD (the GPI subset: MSLN, GPC1, …) | a domain slice; **comparable** to `sliced_ecd`, pending validation |
| `whole` | whole mature chain, no domain boundary available (IGF2R, TLR3, transporters, SDK1) | **not** comparable to a domain slice |

- The GPI-predicted method is its **own** method with its own name — not a variant of "predicted
  boundary." Building the SignalP/GPI predictor is a separate scoped piece (a DL component the
  Prime Directive welcomes).
- **`whole` is the CURRENT method for its subset, not the permanent one.** If domain decomposition
  is ever built (D-022), it likely **supersedes** part of the `whole` subset — the multi-domain
  giants especially. Written as current-not-permanent so that supersession is expected, not a
  reversal.
- SDK1 (extracellular annotation, no numeric bounds) is `whole` for now and flagged as its own
  small case.

**The reporting constraint — the real cost, and it is binding.** Holding `whole` folds out of
cross-method ranking claims means **D-015's ranking runs on a reduced cohort**, and that reduction
is **part of the result, not a footnote.** Wherever a ranking is reported — UI, report, or log —
it states the split explicitly, e.g. *"N ranked, 13 held out (whole-chain method)."* "82 targets"
silently becoming a smaller ranked set is exactly the drift that invalidates a comparison. The
exact N is whatever the GPI-predicted method recovers into the comparable set; it belongs next to
every ranking.

---

### D-020 — The 82-target cohort of record, gene→accession mapping, and the measured ECD distribution
- **Date:** 2026-07-21
- **Status:** Accepted (data provenance + method); the ECD distribution below is measured.
- **Context:** D-015 fixed the cohort (Group A = Kathad et al.'s 82 prioritised targets) and §4
  required measuring the ECD-length distribution before scoping the D-011 rental. The 82 lived
  in a downloaded XLSX; the reproducibility claim (§7) had a hole until the cohort was committed
  and the accessions derived by a recorded method.

- **Data provenance (D-015 §4: pin the version, not just the URL):**
  - **Source:** Kathad et al. 2024, *PLOS ONE* `10.1371/journal.pone.0308604`, **CC-BY**.
    Supplementary **S3**, sheet **`Target_expression_in_normal`** — its unique `Gene name`
    column is exactly **82** symbols. Retrieved **2026-07-21** from the PLOS file endpoint.
  - **Committed as the cohort of record:** `data/cohort_82.txt` (the 82 **gene symbols** — the
    supplementary carries no UniProt accessions), so the cohort no longer lives only in a
    downloaded binary.
  - **The comparator arrived with the cohort.** S3 also carries the `Clinical` / `Preclinical` /
    `Antibody generated` / `Literature evidence` columns — i.e. the evidence-score inputs D-015 §1
    needs as the comparator ranking. It is *obtainable from the same file*, not reconstructed.
    (Computing the 1–5 score from them is a later comparator task, not this entry.)
  - **Mapping:** `scripts/map_genes_to_uniprot.py` (stdlib; reads the committed symbol list) →
    UniProtKB REST search, **reviewed (SwissProt) only, taxon 9606 pinned**, retrieved 2026-07-21.
    Output committed: `data/cohort_82_mapping.csv`, resolved accessions `data/cohort_82_accessions.txt`.

- **Why a programmatic mapping is trusted — and it is NOT because it is automated.** A
  hand-curated list carries the same error rate with none of the flags; the 10-seed's confident
  MUC4 (for CLDN18.2) and PTPRU (for NECTIN4) are the proof. This mapping is trusted **because it
  reports what it cannot resolve.** An unresolved or renamed symbol is a visible flag, never a
  silent guess.
  - **The census runs on all 82, not a sample:** requested symbol in, returned **primary** gene
    out, asserted equal. That comparison — against the gene symbol, not the protein name — is
    exactly what would have caught both seed errors.
  - **Primary-match disambiguation:** a synonym-only hit is a *different gene*, never a
    candidate; among multiple reviewed hits, the one whose primary gene equals the requested
    symbol wins. **0 or ≥2 primary-matches would flag a genuine ambiguity** rather than paper
    over one — that is what makes the rule safe.

- **Result (observed): 79 clean + 3 resolved-by-primary-match = 82; 0 renamed, 0 ambiguous, 0
  absent.** Zero renames means the 2024 paper's symbols are all still current (staleness concern
  retired). The three resolved-from-ambiguity cases are recorded here so a future reader need not
  re-derive that the method worked — the flags are the evidence:

  | Symbol | resolved → (primary match) | discarded (synonym-only, a different gene) |
  |---|---|---|
  | ATP2B2 | `Q01814` | `P23634` (ATP2B4) |
  | LRRN1  | `Q6UXK5` | `O75427` (LRCH4) |
  | SMO    | `Q99835` | `Q9NWM0` (SMOX) |

- **Independently anchored, not just internally consistent.** The mapping was checked against the
  10-seed's already-verified accessions for the Group B symbols present in the 82 — **4/4 exact**
  (`ERBB2`→P04626, `EGFR`→P00533, `CD276`→Q5ZPR3, `NECTIN4`→Q96NY8). Verification against
  known-good values, the census applied to the mapping itself.

- **Cohort observation for the D-015 §2 reconciliation (a HYPOTHESIS, not established):** three
  symbols the 10-seed labelled Group B — **MET, TNFRSF17 (BCMA), FOLR1** — are **not in the 82**.
  TROP2 and FOLR1 absence is expected (TROP2 is a named author omission; FOLR1 is the GPI-anchored
  Group C case). BCMA's absence is **consistent with** the paper's haematopoietic-expression
  exclusion filter (BCMA is a plasma-cell antigen) — *plausible from the filter's presence, not
  verified against the paper's intermediate lists.* Belongs in the §2 approved-vs-82
  reconciliation as a check, not a conclusion. The seed's B-labels were illustrative, not
  authoritative on membership.

#### Measured ECD-length distribution (D-015 §4 — "report the size of the icebreaker, measured")

`scripts/ecd_lengths.py` over the 82 accessions (UniProt `Topological domain` = `Extracellular`,
per D-009 §2), bucketed against the **measured** local ceiling. Backing data:
`data/cohort_82_ecd.csv`.

| Bucket (by largest extracellular span) | n | % |
|---|---|---|
| **local** (≤440 aa) | 40 | 48.8 |
| **untested** (441–629 aa) | 13 | 15.9 |
| **rental** (≥630 aa) | 16 | 19.5 |
| **unsliceable** (no usable extracellular span) | 13 | 15.9 |

Three findings, each reportable in its own right:

1. **The GPI-anchored / no-topology class is a SECOND METHOD, not an edge case: 13 of 82 (16%).**
   FOLR1 established that D-009 §2's `Topological domain` method cannot slice GPI-anchored
   proteins; at 16% of the cohort this is not a fallback to bolt on but a real second boundary
   problem. Composition: **12** have no extracellular topological domain at all — including
   GPI-anchored ADC targets **MSLN** (mesothelin) and **GPC1** (glypican-1), plus proteins UniProt
   simply annotates without topology (IGF2R, TLR3, transporters) — and **1** (SDK1) has an
   extracellular annotation with **no numeric bounds**, unsliceable as measured. *Which of the 12
   are specifically GPI-anchored is a follow-up lookup, not asserted here.*
2. **The rental bucket is not uniform, and D-011's ~$0.25 estimate does not survive.** 16 targets
   exceed the local ceiling, but two — **MUC16** (14 451 aa; CA-125, a real giant mucin, anchor-
   confirmed not a parse artifact) and **FAT2** (4 030 aa) — are **too large to fold as a single
   sequence even on the rented A6000**, and several more (NOTCH2 1652, PTPRZ1 1612, LRP6 1351)
   approach that limit. "Rental" therefore splits again into *foldable-on-rental* vs
   *needs-domain-decomposition-or-exclusion* — a real refinement to D-011's scope, to be scoped
   before renting.
3. **Just under half (40/82, 49%) fold locally** on the 8 GB GPU with the S-003 int8 recipe — so
   the local tier carries the plurality of the cohort, and the expensive/hard remainder is now a
   measured ~35% (untested + rental) plus the 16% that needs a different boundary method.

- **Deep-learning justification:** the cohort is the labelled substrate the D-015 scorer is
  trained and evaluated on; without a provenance-pinned, accession-verified 82 there is nothing to
  fit or rank. The ECD measurement turns the compute requirement for cohort-scale structure
  prediction into an empirical finding (§4), which for an ML course is itself a result.

- **Consequences / follow-ups:** the §2 no-topology count (13) needs a second ECD-boundary rule
  before those targets can be folded (own decision later); the oversize rental targets need a
  decomposition-or-exclude call before the rental is scoped; the evidence-score comparator is
  ready to extract from the same S3 file; the BCMA hypothesis feeds the §2 reconciliation.
  `openpyxl` was used locally to read S3 but is **not** a project dependency — the committed
  `cohort_82.txt` is the reproducible artefact, and the stdlib mapping script reads it.

---

### D-019 — protein_analyses + ranking_runs + FK closure + pgvector: the last unproven point
- **Date:** 2026-07-21
- **Status:** Accepted; implemented in this PR (migration `0002`).
- **Context:** Three deferred obligations converge on exactly this migration: D-009 §1
  Amendment 4 (the `jobs.analysis_id` FK lands *in the migration that creates
  `protein_analyses`*), D-015 §4 (`ranking_runs` + a nullable `protein_analyses.ranking_run_id`
  FK, created in that same migration), and D-017 (pgvector `extensions`-schema resolution — the
  **single remaining unproven point in the system**). This PR discharges all three in one
  migration, because Amendment 4 requires the FK and its target in the same migration.

- **Decisions:**
  - **Scope.** `protein_analyses` (Database Plan §2.2 columns) and `ranking_runs` (D-015 §4:
    `target_list_version`, `scorer_version`, `created_at`) become ORM models — both
    SQLite-creatable, so the `create_all` test path is unaffected. `analysis_embeddings`
    (`embedding vector(384)` + HNSW) is created **in the migration only, as raw SQL** — kept out
    of `Base.metadata` so SQLite `create_all` never sees a Postgres vector type and **no
    `pgvector` Python dependency is added**. `mutations`/`reports` are **deferred** (Iteration
    2/3 children, nothing to do with FK-closure or pgvector).
  - **FK closure (Amendment 4).** `jobs.analysis_id` gains its FK → `protein_analyses(id)`.
    Per the standing "fail on the event" discipline, `test_analysis_id_has_no_fk_yet` was run
    *after* adding the FK and **confirmed to fail specifically on the FK-exists assertion** (not
    a collateral schema error) before being replaced with a positive test asserting the FK is
    present and references `protein_analyses`. Same for the postgres job's `fks == 0` assertion.
  - **A SECOND deferred FK, named not hidden.** `protein_analyses.user_id` is a nullable integer
    with **no FK yet** — `users`/auth is unbuilt, so the FK would have no target. Deferred
    exactly as `analysis_id` was (Amendment 4), and closes in the migration that creates
    `users`. The column matches the plan so it is forward-compatible; only the constraint waits.
  - **pgvector — D-012 §5a's tabled choice, finally made.** Rely on the env.py `search_path`
    seam (already in place): the migration runs `CREATE SCHEMA IF NOT EXISTS extensions;
    CREATE EXTENSION IF NOT EXISTS vector SCHEMA extensions;` then a **bare** `vector(384)`,
    which resolves because `extensions` is on the migration's search_path. Both statements are
    idempotent on prod, where D-014 measured the schema and the v0.8.2 extension already present
    — so this is a no-op there and a create in CI. NOT schema-qualifying every column and NOT
    `ALTER DATABASE` (D-012 §5a's rejected options).
  - **CI image switch.** The `postgres` job moves `postgres:16` → `pgvector/pgvector:pg16` so
    `CREATE EXTENSION vector` succeeds and the pgvector path is exercised **for real** — which
    is what closes the last unproven point rather than merely asserting it closed.

- **Deep-learning justification:** direct on two axes. `analysis_embeddings` is where learned
  embeddings become a load-bearing capability (D-015's semantic axis), and pgvector is what
  makes that a real deliverable rather than a lookup — the exact thing the unmanaged Postgres
  product could not host (D-014). `protein_analyses` is the durable record every fold and score
  attaches to; `ranking_runs` versions the ranking the D-015 scorer produces, so a result can be
  tied to the target-list and scorer that produced it (reproducibility, §7).

- **Consequences:**
  - Migration `0002_protein_analyses`; `ARCHITECTURE.md` §4 updated.
  - **The last unproven point is closed** — the pgvector `extensions` resolution now runs in the
    `postgres` job against a pgvector-enabled Postgres 16.
  - New deferred obligation logged: the `protein_analyses.user_id` FK, closing with `users`.
  - `mutations`/`reports` remain to come; the orchestrator (cohort → UniProt → ECD slice → tier
    route) and the D-015 scorer are the multi-day builds after this. The orchestrator's
    prerequisite — the 82's measured ECD-length distribution + GPI-anchored count (cheap, no GPU)
    — is slotted before/alongside it.

---

### D-018 — PR B is a pure fold-runner: sequence in, structure + provenance out
- **Date:** 2026-07-21
- **Status:** Accepted; scopes PR B. Implements the D-011 cache-generation entry point, narrowed.
- **Amendment 1 (2026-07-23) — the `accelerate` gap is closed and the full GPU env is captured.**
  `worker/requirements.txt` left `accelerate` unpinned *"until the first successful GPU install"*
  (D-016: name what is not known, do not invent a pin). That install happened on the first-fold
  night; the resolved version is **`accelerate==1.14.0`**, now pinned. Its complete resolved
  environment is captured in **`worker/requirements-frozen.txt`** — re-saved UTF-8 (it was UTF-16
  and untracked) and now tracked as a **reference snapshot, not a hash-locked guarantee**. The GPU
  tier stays outside D-013's lock by design (this entry's own ruling), so the freeze reproduces the
  working install for a GPU-box rebuild without pretending to CI enforcement: a breaking upstream
  release still reddens no gate — the freeze is simply what a rebuild pins against.
- **Context:** PR B was defined (session pre-work) as "the cache-generation entry point:
  host-agnostic, dtype and chunk_size as parameters, local defaults int8/chunk 64" — *before*
  D-015 turned single-target folding into the input to a cohort ranking. That raises the
  question of how much PR B should take on: just fold a sequence, or select/slice/route the
  whole 82-target cohort?

- **Decision: PR B is the pure fold-runner only.** Sequence + parameters in → structure
  artifacts (PDB, pLDDT, PAE) + an `inference_settings`/provenance record out. It does **not**
  select the cohort, query UniProt, choose ECD boundaries, or route to a compute tier — that is
  the *orchestrator*, a later step. It does **not** touch the database — artifacts go to files,
  and the DB wiring lands with the `protein_analyses` migration (see below).

  **Why split runner from orchestrator — the argument is correctness conditions, not tidiness.**
  The two are right about different things and fail in different places:
  - the **runner** is correct iff *a sequence in produces a valid structure out with an accurate
    provenance record*;
  - the **orchestrator** is correct iff *the right set of sequences is selected, sliced at the
    right boundaries, and routed to the right tier* (D-009 §2, D-011).

  Those are separately testable, and welding them means neither can fail cleanly. There is also
  a hard operational reason: the runner is what executes on the **rented A6000 where every minute
  bills** (D-011). That surface must be small, proven, and unable to need cohort data it cannot
  reach from a rental box.

- **Why no `protein_analyses` / no DB (this matters more than it looks).** The pgvector
  `extensions`-schema resolution is the **single remaining unproven point in the system** (D-017).
  The migration that creates `protein_analyses` is already scoped to do four things at once —
  create it, add the deferred `jobs.analysis_id` FK (D-009 §1 Amendment 4), create `ranking_runs`,
  add the nullable `ranking_run_id` FK (D-015 §4) — and it is where that last risk gets exercised.
  Dragging any of it into a standalone runner PR inherits the one remaining risk for **no
  benefit**. Artifacts to files now; paths recorded in the DB when that migration lands.

- **The CUDA manifest is a new, named, ACCEPTED gap — not an oversight.** PR B introduces
  `worker/requirements.txt` (torch, transformers, bitsandbytes, accelerate) — the GPU tier's
  dependencies, which D-013 §4 deliberately kept out of CI. Stated plainly: **the worker's
  dependencies are NOT covered by the lock-file guarantee** (D-013 Amendment A). A breaking
  release there reddens no gate and is discovered at fold time, on a GPU host. That is accepted
  because CI has no GPU and installing a CUDA stack there would be slow, fragile, and pointless.
  But because ARCHITECTURE §7 makes reproducibility a graded expectation, the manifest carries
  **exact pins** measured in the S-003 spike — `torch==2.11.0+cu128`, `transformers==5.14.1`,
  `bitsandbytes==0.49.2` — and the fold records the **model revision**
  (`75a3841ee059df2bf4d56688166c8fb459ddd97a`). Honest hole (D-016): `accelerate` has **no
  measured pin yet** (it was present but unrecorded in the spike venv); it is listed to be pinned
  from the first successful GPU install and the resolved version recorded here.

- **Truncation and slice-provenance are recorded at fold time — a D-015 §1a enforceability
  requirement, not a nicety.** §1a's diagnostics require that a fold on a **truncated** ECD be
  flagged and excluded from ranking claims (a truncated fold is a different molecule), and that
  the ECD boundary be known. The runner cannot know the cohort's intent, but it records what it
  was handed: whether the input was a **sliced ECD** or a **whole sequence** (the GPI-anchored /
  FOLR1 fallback case, D-009 §2), the ECD start/end when sliced, and whether any **length cap**
  truncated the input. If the runner does not capture this at fold time, it cannot be
  reconstructed later and the §1a diagnostic becomes unenforceable.

- **Testing split (the postgres-job pattern again).** The runner's **pure logic** — provenance
  construction, the pLDDT rescale (S-001 gotcha: ESMFold B-factor pLDDT returns on the 0–1 scale
  and must be ×100), length-cap/truncation recording, artifact layout — is unit-tested on the
  normal gate with no GPU (torch imported lazily, inside the fold call, so the module imports
  without it). The **actual fold** is GPU-bound: it cannot run in CI (no GPU runner) and is
  validated on a GPU host by the owner. The int8 recipe is already measured (S-003/S-005); a
  `@pytest.mark.gpu` test marks the boundary and skips without torch+CUDA, exactly as the
  postgres tests skip without a database.

- **Deep-learning justification: this is the neural core itself.** Every other decision has been
  scaffolding around it; PR B is the code that runs ESMFold and emits the structure every
  downstream feature (the D-015 scorer, pockets, embeddings) consumes. The provenance record it
  writes is what lets a later ranking claim be checked — D-016's principle applied at the point
  the numbers are born.

- **Consequences:**
  - New `worker/` package (`worker/runner.py`, `worker/requirements.txt`), first GPU-tier code.
  - `ARCHITECTURE.md` §7 (reproducibility) and §8 (layout) updated in this PR.
  - Deferred, explicitly: cohort selection / UniProt / ECD-boundary slicing / tier routing (the
    orchestrator); the DB wiring and the `protein_analyses`+`ranking_runs` migration; the
    worker↔app pull contract (D-004). Each is its own step.

---

### D-017 — Postgres integration CI job: the seam's other half
- **Date:** 2026-07-21
- **Status:** Accepted; implemented in this PR. Implements the job named as required by D-012 §5
  and D-014, not a new decision about *whether* — a decision about *how* and *how far*.
- **Context:** Since PR A this has been the single largest coverage hole. The `test` job builds
  schema with `create_all` and never runs the Alembic chain, and `FOR UPDATE SKIP LOCKED` is a
  **syntax error** on SQLite (D-012 §3) — so the migration chain and `PostgresJobQueue.claim`'s
  atomicity are provable by nothing in the repo. D-012 §4's seam made that gap *legible*; it did
  not close it. This closes it. (The shape is exactly JARVIS audit H2: a green SQLite suite that
  proved nothing about a fresh Postgres, closed only by a real-Postgres CI job.)
- **Decision:** A `postgres` CI job (`.github/workflows/gate.yml`) runs a **Postgres 16** service
  container (matching prod, D-014), installs the locked deps (D-013), applies migrations with
  `alembic upgrade head` — **the real chain, not `create_all`** — and runs the
  `@pytest.mark.postgres` tests. They prove three things the SQLite suite cannot:
  1. the chain builds the schema on real PG (and env.py's Postgres-only `search_path` SET ran
     without error, or `upgrade` would have failed);
  2. `claim`'s `SELECT … FOR UPDATE SKIP LOCKED` is **atomic** — a row locked in one open
     transaction is *skipped* by a claim on another connection, which takes the next row;
     all-locked yields `None`;
  3. `complete` / `fail` / `reap_stale` (incl. the cap → terminal `[reaped-out]`) behave
     identically on real PG.

  The postgres-marked tests **auto-skip** without a postgresql `DATABASE_URL` (the `pg_engine`
  fixture), so they are inert in the `test` job and run for real only here. `deploy` now
  `needs: [test, postgres]`.

- **How far — required-vs-advisory, decided explicitly (D-016 discipline: name what is *not* yet
  true).** The job runs on every PR and push, but is **not yet a branch-protection required
  check**. Two reasons: branch protection is owner-set (D-008 established it, `enforce_admins`),
  and a *required* job with a service container that flakes would deadlock every PR with no admin
  bypass — the exact hazard D-013 §3 declined pip caching to avoid. Interim gate: `deploy: needs
  postgres`, so a broken migration cannot **deploy** even if a PR merged.

  **Promotion criterion — a specific bar, not a vibe.** The owner adds `postgres` to branch
  protection's required checks once **all** of the following hold, so "stable" is falsifiable:
  1. The job has completed on **≥ 5 consecutive PRs** since this one.
  2. On every one of those, any red was **attributable to a genuine code/migration fault** — the
     job doing its work (like the env.py bug on run one) — and **never to service-container
     infrastructure**: container-startup timeout, `pg_isready` health-check failure, or
     connection-refused. An infra flake is the precise signal that a *required* version would
     have deadlocked a PR with no bypass.
  3. **Any infra-attributable failure resets the count to zero.** One flake in five PRs means
     not yet — the counter measures the thing that matters (would "required" have blocked
     honest work?), not elapsed time.

  Recorded as a recommendation with a bar, not silently done: it is a repo-settings change
  (owner-only, like branch protection itself, D-008) with a real downside if promoted early.

- **Still unexercised, stated not hidden:** the service image is stock `postgres:16`. There is no
  vector column yet, so env.py's `search_path`→`extensions` *resolution* is proven only insofar
  as the SET executes without error — the SET targeting a real populated `extensions` schema, and
  a `vector(384)` actually resolving through it, is exercised when the first vector-column
  migration lands and the image switches to `pgvector/pgvector:pg16`.

- **Deep-learning justification:** Indirect, and the strongest kind available for infrastructure.
  The queue runs every neural inference (D-009 §1); a silently-broken claim (double-dispatch,
  lost job) or a migration that fails on real PG would corrupt the cache the DL deliverable is
  served from, and would do so *invisibly* under a green SQLite suite. This is D-016's provenance
  principle applied to the queue: the claim path now has an artefact — a passing real-Postgres CI
  run — behind the assertion that it works.

- **It earned its keep on its first run.** The job immediately caught a real bug that a green
  SQLite suite could never have: env.py ran the `search_path` SET *before*
  `context.begin_transaction()`, auto-opening a SQLAlchemy-2.0 transaction alembic did not own,
  so `alembic upgrade head` logged "Running upgrade → 0001_create_jobs", exited 0, and the
  CREATE TABLE **silently rolled back** (`relation "jobs" does not exist` at the first test).
  Every production migration would have no-op'd invisibly. Fixed by moving the SET inside
  alembic's committed transaction; the artefact (run `29879472591`) is cited in env.py so it is
  not reintroduced. This is precisely the JARVIS-H2 class of failure the job exists to catch.

- **Consequences:**
  - The D-012 §4 seam is now proven on **both** sides. The unproven surface is no longer "claim
    atomicity" but only the narrower "pgvector type resolution," gated to the vector-column PR.
  - `ARCHITECTURE.md` §5 (deploy gate) updated in this PR.
  - The open-questions "largest coverage hole" item is closed (see below), with the pgvector
    caveat carried forward.

---

### D-016 — The provenance principle: every claim names how it is known
- **Date:** 2026-07-21
- **Status:** Accepted (standing rule)
- **Context:** THE RULE at the top of this file governs **durability** — a decision made in a
  chat window and never written down does not exist. Today exposed a different failure the rule
  did not cover: **every claim that got reversed was already written down.** The record was
  faithful; the record was the problem, because it preserved a claim nobody had checked in a
  form indistinguishable from one that had been. A durable record of an unverified claim is
  *worse* than no record — it reads like evidence.

  Four cases in two days, each a written claim **true as stated and wrong in what it implied**,
  each overturned only by returning to the raw artefact:

  | Written claim | Artefact that overturned it |
  |---|---|
  | `params_all_on_cuda=True` | resident 8116 MiB vs **7043 MiB free** — spilled before folding (S-001) |
  | "217 WHEA events since May" | 213 corrected / **4 fatal** — severity hidden by the total (F-001) |
  | "pgvector isn't enabled" (`pg_extension` → 0 rows) | `pg_available_extensions` → 0 rows: **not on the image at all** (D-014) |
  | placeholder commit SHAs in D-013 §6 | invented to fill a template before the runs existed — caught pre-merge, corrected in `8e177ad` |

  This is the discipline the *Method note* above already gestured at, now made a first-class
  standing rule rather than a lesson buried mid-file. It is also KEEL's proposed 8th principle
  (drafted from this session); the KEEL documents themselves live in the Keel project and are
  updated there separately.

- **Decision:** A **second standing rule**, added beneath THE RULE at the top of this file and
  mirrored as a living-documentation rule in `CLAUDE.md`:

  > **Every claim names how it is known.** Before a number or a status enters the log,
  > ARCHITECTURE, or a PR, name the artefact it came from — the raw log line, the query output,
  > the run URL. If you cannot name it, you are recording a belief, not a finding. A summary is
  > not knowing: prefer the breakdown to the total, and **prefer the query whose answer could
  > disqualify you** (`pg_available_extensions` answers "does it exist?"; `pg_extension` only
  > "is it on?" — a zero from the second cannot tell *absent* from *off*).

- **Deep-learning justification:** Indirect but load-bearing. The graded deliverable rests
  entirely on *measured* claims — `inference_settings` reproducibility (D-004), the int8 fit and
  length-ceiling findings (S-003/S-004/S-005), and the scorer's pre-registered evaluation
  (D-015 §1a/§3). Every one of those is a number that will be trusted later. A fabricated or
  unverified figure in this log corrupts the exact record the DL evaluation is judged against —
  the D-015 §1a diagnostics (rule out "our pipeline is wrong" before any claim) are this
  principle applied to the science. Protecting claim provenance protects the deliverable.

- **Consequences:**
  - Applies as a **standard going forward**, not a retroactive rewrite. Existing entries that
    already cite artefacts (S-00x, D-014, D-013 §6) are the model.
  - `CLAUDE.md` gains a fourth living-documentation rule; the top-of-file RULE block gains its
    second rule. No code change.
  - The KEEL provenance-principle draft and the `KEEL-*-v5` documents are **Keel-project**
    artefacts, deferred to a Keel-focused pass (not migrated into this repo).

---

### D-015 — Research question, target cohort, and the learned scorer
- **Date:** 2026-07-21
- **Status:** Accepted (scope); the scorer's feature set and evaluation are **pre-registered
  below and not yet run**
- **Context:** Until now the project's deliverable was single-target analysis: enter a
  protein, get structure, pockets, an ADC-suitability summary. That satisfies the Prime
  Directive only weakly — ESMFold is the headline, but nothing *uses* its output to produce
  a judgement that could be right or wrong. This entry commits the project to a research
  question with a control, a labelled set, and a falsifiable claim.

  **Prior art was surveyed before scoping, and it is substantial.** This is a settled field,
  not an empty one:
  - **Open Targets Platform** (EMBL-EBI/GSK) scores target–disease associations across 20+
    data sources with a prioritisation layer covering tractability, safety, and expression.
    Free REST API and bulk downloads.
  - **Kathad et al. 2024, PLOS ONE** (`10.1371/journal.pone.0308604`, Lantern Pharma) is the
    closest analogue: an *in silico* ADC-target prioritisation from 20,090 protein-coding
    genes down to **82 prioritised targets**, filtered on HPA v22 membrane annotation,
    critical-normal-tissue exclusion, a quasi-H-score ≥150 tumour-expression cutoff, the
    *in silico* human surfaceome, mRNA/IHC consistency, and haematopoietic-expression
    exclusion. **CC-BY licensed**; the target list and expression matrices are published as
    supplementary files (S2, S3).
  - Consensus ADC target-selection criteria across the literature are stable: high
    tumour-specific surface expression, minimal normal-tissue expression, efficient
    internalisation.

  **The gap this project occupies.** Every scheme above ranks on **expression, mutation,
  genetics, and internalisation**. None ranks on **predicted structural properties of the
  extracellular domain**, because none of them folds anything. That is the axis we add, and
  we add it by running our own ESMFold (D-003) rather than retrieving structures.

  There is a documented problem the structural axis plausibly bears on: clinical activity in
  solid tumours **often does not scale with antigen abundance** — an affinity–efficacy
  disconnect that abundance-based ranking cannot explain by construction. Whether a
  bindable, accessible epitope exists is a candidate explanation. *This is a motivating
  hypothesis, not a claim this project has established.*

---

> **REVISED 2026-07-21 (§1 and §3 replaced).** The original framing treated the Kathad
> result as a *baseline to recover*. It is not ground truth — it is another analysis, with
> stated filters, commercial authorship, and named omissions. Treating it as an oracle would
> make *agreement* the success condition and quietly turn this project into a reimplementation.
> §2, §4, context, and consequences stand as first drafted.

#### §1 — The research question (Accepted)

> **Does an ADC-suitability ranking built on structural features — computed from folds this
> project runs — differ from a ranking built on expression and evidence? Where the two
> disagree, which disagreements are checkable against outcomes the world has already decided,
> and which are hypotheses?**

Note what is *not* asked: whether our ranking matches theirs. **Agreement is not the success
condition and disagreement is not failure.** A structural axis that merely reproduces an
expression-based ranking has added nothing — it would mean structure carries no information
beyond abundance, which is itself a reportable (and surprising) negative result.

**The comparator is a comparator, not an oracle.** Kathad et al.'s 82 prioritised targets and
1–5 evidence scores are a **published, reproducible, independently derived** ranking — which is
exactly what makes them useful. They are not a gold standard:

- The filters are **explicit and consequential**: a quasi-H-score ≥150 cutoff on a 0–300 scale,
  exclusion of anything highly expressed in 13 critical normal tissues, mRNA/IHC consistency.
  The authors themselves record that these filters **excluded TROP2, HER3, and CLDN18.2**.
- The 1–5 evidence score is built from literature, antibody existence, protein family,
  preclinical, and clinical criteria — i.e. it substantially measures *how much attention a
  target has already received*. A popularity-and-precedent score as much as a biology score; a
  target nobody has studied scores low by construction.
- The work is authored by a commercial pharma company using a proprietary platform. Not an
  accusation of bad faith — the method is published in full and CC-BY, which is more than most.
  It is a reason not to treat the output as neutral ground truth.

**Our position is differently biased, not unbiased.** No commercial stake and no prior
commitment to any target is real — but inexperience is not neutrality; it also means not
knowing which failure modes the field has already understood and discarded. The defensible
claim is narrow and sufficient: **we are looking at an axis they did not measure at all.**
Structural accessibility of the extracellular domain appears nowhere in their feature set,
because they folded nothing.

**Two axes, kept orthogonal and never blended into one number:**

| Axis | Measures | Source |
|---|---|---|
| **ADC suitability** | Is this a good ADC target? | Structure-derived features (ours) + expression/evidence comparator |
| **Urgency / unmet need** | Does it matter clinically if it is? | Cancer-type survival, incidence, existing options |

Survival rate is a property of the *cancer*, not the *target*. A highly exploitable thyroid
target and a mediocre pancreatic target should both surface, for different reasons. Collapsing
them destroys the information a researcher needs. Urgency **ranks**; it does not **score**.

---

#### §1a — Disagreement is the expected outcome, and it is pre-registered (Accepted)

**Written before any result exists**, per the log's method note: *name the outcome that would
overturn the favoured hypothesis, and state a check precisely enough that its inadequacy is
discoverable.*

If our ranking disagrees with the comparator, there are exactly **three** explanations. They
are not equally likely, and they are not equally interesting. **The honest prior for a first
implementation is that (3) is most probable for any given disagreement.** A disagreement
claimed without ruling out (3) is worthless.

| # | Explanation | Checkable against | Status of a claim |
|---|---|---|---|
| **1** | **Their pipeline has a blind spot we can see.** A target their filters excluded or scored low that the world has since validated. | **Outcomes already decided** — approved ADCs, trials that succeeded. Group C exists for this. | **Checkable finding.** The strongest claim available, and the rarest. |
| **2** | **We measured an axis they did not.** A target we promote on structural grounds that they never evaluated structurally. | **Nothing — by construction.** They did not fold. Orthogonal information, not contradiction. | **Hypothesis.** Reportable as a generated candidate, never as a correction. |
| **3** | **Our pipeline is wrong.** Bad ECD boundaries, degenerate folds, a scorer fitting noise on 22 positives, a length-truncation artefact. | **Internal diagnostics** — below. | **A bug.** Reported as a finding about method, which for an ML course is a legitimate result. |

**Ruling out (3) is a precondition for claiming (1) or (2).** The diagnostics, fixed in advance:

- **Fold sanity per target**: CA-atom count matches sequence length, zero NaN coordinates,
  radius of gyration consistent with a compact globular expectation. (The S-003 checks; they
  generalise.)
- **Boundary sanity**: the ECD span came from a UniProt `Topological domain` annotation and was
  not silently truncated by a length cap. Any target folded on a truncated ECD is **flagged and
  excluded from ranking claims** — a truncated fold is a different molecule.
- **pLDDT floor**: targets whose ECD folds below a pre-set mean-pLDDT threshold are reported
  separately, not silently ranked. *ESMFold's own uncertainty is a feature of the pipeline, not
  noise to average over.*
- **Score stability**: a disagreement that vanishes under leave-one-out refitting is a scorer
  artefact, not a finding.

**A disagreement surviving all four diagnostics is interesting whichever way it falls.** One
that does not is a bug report — still a result, and for a DL course arguably a more instructive
one than a ranking that happened to work.

**Pre-registered negative outcome, stated so it cannot be quietly abandoned:** if the
structural ranking's disagreements with the comparator are **entirely** explained by (3), the
honest conclusion is that this pipeline, at this cohort size, with these features, does not add
measurable signal over expression-based prioritisation. That is the result, and it gets written
up as the result.

**Claim discipline, binding on the UI:** a class-(1) disagreement may be stated as evidence
about the comparator; a class-(2) disagreement may be stated **only** as a hypothesis. The
interface must make the class visible — the two look identical in a sorted table and mean
entirely different things.

---

#### §2 — The cohort (Accepted)

Three groups, kept **structurally distinct in the data model and visually distinct in the
UI**. Conflating them would be the same error as a test double that reads as coverage.

| Group | n | Role |
|---|---|---|
| **A — the 82** | 82 | Baseline cohort. Kathad et al.'s prioritised targets, with their published 1–5 evidence score as the **baseline ranking to compare against**. |
| **B — in-cohort positives** | 22 | Targets within A already tested as ADCs preclinically or clinically (incl. ERBB2, NECTIN4, EGFR). **The labelled set.** |
| **C — baseline exclusions** | ≥3 | Approved/advanced targets the baseline pipeline **filtered out** — TROP2, HER3, CLDN18.2. Folded and scored as an **out-of-cohort probe**, never mixed into A. |

> **⚠ Corrected by D-040 (2026-07-23) — what the paper actually publishes.** *(a)* Group A's
> "published 1–5 evidence score" is available for only **17 of the 82**: the article *text* gives
> exact scores for 17 (score 5 — 8 targets; score 4 — 9 targets), while the full set appears only
> as **Fig 4A/4B** (a radar plot + wordcloud) with **no supplementary file named**. The scores are
> **not** in S2/S3 — S2/S3 are the expression matrices (44 normal / 20 tumour tissues). The other
> 65 carry **null-with-reason** (`score_not_published_in_text`), never a figure-read value. *(b)*
> Group B's **roster is not published** — the paper names only ERBB2/NECTIN4/EGFR and the count 22
> — so B is **derived here, pre-registered, cited per row, then checked against the 22** (D-040), not
> inherited. Group B and Group C are one curated file (`data/adc_reference_mapping.csv`), split only
> by a computed `in_cohort_82`.

**Why B is better than "the 23 approved ADCs":** the labels sit *inside* the same cohort, so
evaluation is a within-cohort comparison rather than a join across two differently-derived
datasets. 60 of the 82 are unexplored for ADC development — that is the prediction set.

**Group C is the sharpest test available, and its provenance must be stated precisely,
because two different claims are involved:**

- **Theirs (cited):** Kathad et al. explicitly name TROP2, HER3, and CLDN18.2 as omitted by
  their filters, and offer the likely causes — the 150 quasi-H-score cutoff, the
  critical-normal-tissue rule, and missing IHC data. They record it as a limitation.
- **Ours (derived here, 2026-07-21):** that at least one of those omissions is the target of
  **two FDA-approved ADCs** (sacituzumab govitecan; datopotamab deruxtecan), making it a
  **false negative of the baseline** rather than a neutral methodological gap. The paper
  does not make this connection.

**Trop-2 is already folded** (248 aa ECD, int8 trunk, verified deterministic and
structurally sane — S-003). If the structural score ranks it well, that is a concrete
instance of the structural axis recovering something expression-based filtering discarded —
far sharper than an aggregate correlation.

**⚠ Stated as a limit, not buried:** three named exclusions, at least one approved, is a
**single instance and not a demonstrated pattern**. "The baseline has blind spots" is the
hypothesis this project tests, **not a finding inherited from the paper**. If the structural
score fails to recover Trop-2, that is a result, and no part of the UI may have promised
otherwise.

**Open, blocking §2's completeness:** the reconciliation of the full approved-ADC target set
against the 82 has **not been run**. Group C is currently the three exclusions the authors
named; there may be others they did not. A mechanical reconciliation script closes this and
must run before the cohort is called final.

---

#### §3 — Where the deep learning does load-bearing work (Accepted)

**A learned scorer**, not a weighted heuristic. Structure-derived features from our own ESMFold
folds → a small trained model → an ADC-suitability score, fit against Group B.

- **Trained**, per explicit ruling. A hand-weighted sum over literature numbers would make the
  neural network decorative — ARCHITECTURE §1's exact failure mode.
- **Small, interpretable feature set.** 22 positives cannot support many parameters. A handful
  of structural features (pocket geometry, surface accessibility, epitope-region pLDDT, ECD
  size/shape) — **not** a learned embedding over structure. Interpretability is not decoration
  here: it is what lets a disagreement be attributed to a feature rather than shrugged at.
- ESMFold stops being the deliverable and becomes the **input to** one. The network's output is
  now a judgement that can be wrong — which is the point.

**⚠ 22 positives is a small labelled set, and early stopping is not sufficient mitigation.**
Pre-registered here, **before any result exists**:

1. **Leave-one-out at the target level.** Hold out one Group B target at a time; ask whether
   the model still ranks it highly. Reported as a **distribution**, never a single CV number.
2. **Feature count fixed before fitting**, and recorded in this entry when chosen. Growing the
   feature set after seeing results is how 22 positives get overfit.
3. **Named negative outcome:** if leave-one-out ranking of held-out positives is
   indistinguishable from the comparator's evidence score, the structural axis adds nothing
   measurable at this cohort size. That is the result.
4. **A second named negative, easily missed:** if the structural score correlates *strongly*
   with the comparator's evidence score, that is **also** a null result — it means our features
   are proxying for attention-and-precedent rather than measuring structure. **Check this
   explicitly.** A high correlation would feel like validation and would not be.

**⚠ Group B is not a clean positive set, and the fit inherits its bias.** These targets were
pursued partly *because* they were tractable, and their tractability was assessed by people who
could see things we cannot. The honest claim is **"does our score recover targets already known
to be viable"** — never **"does our score predict clinical success."** Group B is small,
non-random, and survivorship-selected, and any model fit to it inherits all three properties.
Stated here so no downstream summary can quietly upgrade the claim.

---

#### §4 — Compute consequence: the cohort is measured before it is rented (Accepted)

Folding all 82 ECDs (plus Group C) against a **measured local ceiling in (440, 630) aa**
(S-004/S-005) means an unknown fraction goes to the D-011 rented GPU. The original D-011
estimate (~$0.25, HER2-class only) was scoped to a handful of targets and **does not survive
this decision unexamined**.

**Decision: measure the length distribution before scoping the rental.** A script queries
UniProt for each cohort accession, extracts `Topological domain` features with description
`Extracellular` (per D-009 §2), and reports the ECD-length distribution and the
above/below-ceiling split. Cheap, runs locally, needs no GPU.

**This is a reportable finding, not just planning.** For an ML course, the empirical
relationship between model memory footprint, sequence length, and required compute is at
least as germane as the biology. The deliverable includes: how many targets fit an 8 GB
consumer GPU, how many did not, what the overflow cost, and what that implies about the
hardware floor for structure-based screening at cohort scale. **We report the size of the
icebreaker, measured.**

- **Deep-learning justification:** §3 is the entry's core — a trained model producing a
  primary output from features derived from inference this project runs. §4 makes the
  compute requirement an empirical finding rather than an assumption. §2 supplies the
  control and the labels without which §3's output could not be evaluated at all.

- **Consequences / follow-ups:**
  - **Iteration 1 stays single-target; ranking is Iteration 2 and becomes the spine**, with
    single-target analysis as the drill-down. Per ruling.
  - **Schema anticipates ranking now.** A `ranking_runs` concept (target-list version,
    scorer version, timestamp) with a nullable FK from `protein_analyses`. Costs almost
    nothing today; retrofitting it into an applied migration chain is expensive. **Touches
    PR A's neighbourhood — coordinate before the migration lands.**
  - **UI must surface the DL contribution or it is invisible**, including to a grader. Named
    now, specified in its own entry: a comparative ranking view (baseline rank, structural
    rank, delta, movers), per-target fold provenance (model revision, dtype, chunk_size,
    pLDDT, date — surfaced from `inference_settings`, not left in JSONB), Group C marked
    visually distinct, and the Mission Briefing carrying the research question and the
    Trop-2 reasoning **with both attributions and the single-instance caveat**.
  - **Attribution:** Kathad et al. is CC-BY. The 82, the evidence scores, and the expression
    matrices are reused **with citation**, and the UI says so.
  - **Trop-2 sits outside Group A** — a real limitation of the baseline worth commenting on,
    and the reason Group C exists.
  - **Data sources to pin with retrieval dates**, since all are living resources: HPA v22,
    the surfaceome, UniProt, Open Targets. Reproducibility (ARCHITECTURE §7) requires the
    version, not just the URL.

---

### D-014 — Production Postgres is the existing Fly MPG cluster, own database
- **Date:** 2026-07-21
- **Status:** Accepted
- **Context:** D-012 committed the project to Postgres-first and named "the Fly Postgres
  addon" as the host. Provisioning it revealed that phrase covers **two different products
  with different capabilities and separate CLI surfaces**, and that the assumption behind
  it was wrong in both directions — first about capability, then about cost.

  **Measured on 2026-07-21. Every claim below is an observation, not documentation:**

  1. **Unmanaged Fly Postgres cannot run pgvector at all.** On the existing unmanaged
     cluster `jarvis-db2` (Postgres 17.7):
     - `SELECT extname FROM pg_extension WHERE extname='vector'` → **0 rows**
     - `SELECT name FROM pg_available_extensions WHERE name='vector'` → **0 rows**

     The second query is decisive: pgvector is not merely disabled, it is **absent from the
     image**. No `CREATE EXTENSION` can ever succeed. Enabling it there requires building a
     custom image on `flyio/postgres-flex`, compiling pgvector, publishing to a registry,
     recreating the cluster from a volume snapshot, and maintaining that image across every
     version bump.

  2. **An MPG cluster already exists and is already being paid for.**
     `sentinel-holy-rain-4562` (`gjpkdonnmkeoyln4`) — Basic, Shared×2, 1 GB RAM,
     **Postgres 16**, region **SJC**, pooling enabled, **10 GB provisioned / 2.5 GB used**,
     created 28 days ago. Cost Explorer month-to-date: **$8.55 MPG Cluster + $0.62 MPG
     Cluster Storage**, projecting to ~$38/month — which accounts for the account's jump
     from a $38.11 last invoice to a $66.57 upcoming one.

  3. **pgvector enables per-database on MPG, from the dashboard, with no app attached.**
     Database `pharmfoldmdk` created on that cluster; `vector` **v0.8.2** toggled on and
     reported as **enabled**, **installed in the `extensions` schema**.

  **The cost premise of the original draft was wrong.** That draft rejected Fly on the
  grounds that MPG meant a *new* $38/month plan and moved the database to Neon's free tier.
  With the cluster already provisioned and billed, the marginal cost of hosting
  PharmFoldMDK is **storage only** — pennies against 7.5 GB free — and the entire case for
  a second vendor evaporates.

- **Decision:** Production Postgres is the **existing MPG cluster
  `sentinel-holy-rain-4562`**, with PharmFoldMDK in its **own database (`pharmfoldmdk`)**,
  not sharing `fly-db`. pgvector v0.8.2 enabled on that database. Fly remains the serving
  tier and the Volume host; ARCHITECTURE §5's "Fly Postgres addon with pgvector" is
  **narrowed to MPG specifically** — the unmanaged product cannot satisfy it.

  **Rejected alternatives:**

  | Option | Rejected because |
  |---|---|
  | Share `jarvis-db2` | pgvector absent from the image (measured). Also no isolation — PharmFoldMDK migrations would run against the database JARVIS depends on daily. |
  | New unmanaged Fly cluster | Custom pgvector image to build, publish, and maintain; DR is ours. Recurring work, zero graded output — to obtain what MPG provides as a toggle. |
  | Neon free tier | Genuinely viable and was the recommendation until the sunk MPG cost surfaced. Costs private networking, adds a second vendor, adds free-tier schedule risk, and adds a 500 ms–2 s cold start — to save ~$0.28/month. |
  | Supabase free tier | Free projects **pause after 7 days** without database activity and need **manual unpause** (~30 s resume). A worker polling intermittently plus an irregularly-opened demo makes a 7-day quiet stretch plausible. The standard mitigation is a keep-alive cron whose failure is silent — the class of thing D-008 exists to eliminate. |
  | Share `fly-db` on the MPG cluster | No isolation, for no saving. MPG supports multiple databases per cluster and enables extensions **per-database**, so a separate database costs nothing and contains a bad migration. |

- **Deep-learning justification:** Direct. pgvector is what makes `analysis_embeddings` —
  learned embeddings powering semantic search — a real deliverable rather than a decorative
  one (ARCHITECTURE §1). The measured finding is that the originally-named host **cannot
  run pgvector at all**, so this entry is the difference between a named DL deliverable
  being possible and being quietly dropped at Iteration 3.

- **Consequences / follow-ups:**
  - **⚠ pgvector is installed in the `extensions` schema, not `public`.** A migration
    emitting `vector(384)` will fail with *type does not exist* unless `extensions` is on
    the `search_path` or the type is schema-qualified. **This must be handled in the first
    migration that creates a vector column**, and the chosen approach recorded here.
  - **Postgres 16** (MPG's default; the cluster predates this project). Pin local dev and CI
    to 16 so behavior matches; do not let tooling drift to 17.
  - **Shared compute with `fly-db`.** Basic is Shared×2 / 1 GB RAM across all databases on
    the cluster. Logical isolation is real (separate database, separate extension state, a
    bad migration is contained) but **CPU and memory are not isolated** — a runaway query in
    one database can starve the other, and a cluster-level incident takes both down. Load is
    expected to be light (a polling worker, occasional queries), but this is a **named
    coupling**, not an assumption of safety.
  - **Region SJC**, consistent with existing apps. Since February 2026 inter-region private
    network usage bills at Machine rates, so the serving tier should stay in SJC.
  - **Connection string is not yet obtainable** — the Connect page wants an app attached,
    and no PharmFoldMDK app exists. Not blocking: nothing connects until the first Alembic
    run. Consequence for sequencing: **the Fly app is created before the database is
    reachable**, inverting the usual order. Whether `flyctl mpg` can yield credentials
    without an attachment is unverified.
  - **Pooling is enabled.** Use the **direct** connection for Alembic (transaction-mode
    poolers break DDL and session-level operations) and the pooled connection for the app at
    runtime. Both strings recorded in secrets, never in the repo.
  - **D-005's Postgres integration CI job** should run a Postgres **service container**, not
    connect to this cluster — CI must not depend on an external service, live credentials,
    or shared compute. Per D-012 this remains the only thing that will ever prove the
    D-009 §1 `SKIP LOCKED` claim path.
  - **Unrelated but surfaced:** `jarvis-db2` (unmanaged) and the MPG cluster now both exist
    and both bill. Whether JARVIS should migrate is **out of scope here** and is not
    decided by this entry.

---

### D-012 — Prod DB is Postgres-first; the test-DB split and the job-queue seam it forces
- **Date:** 2026-07-21
- **Status:** Accepted. Authorizes PR A (`jobs` table, queue functions, migration).
- **Resolves:** the open question *"Prod DB choice: Postgres-first vs. SQLite-on-Volume
  prototype (Database Plan §5)."*
- **Depends on:** D-013 (the gate can now install SQLAlchemy/Alembic/psycopg).

#### §1 — Decision

**Postgres is the production database, from the first migration.** The SQLite-on-Volume
prototype path from Database Plan §5 is closed, not deferred.

There is no serious counter-case, and the entry is short on this point because the reasoning
is already load-bearing elsewhere in the log:

- **pgvector** is required for the semantic-search embeddings (Database Plan; D-004's serving
  tier). SQLite has no equivalent, so the prototype path ends in a rewrite the moment
  embeddings land — and embeddings are part of the graded DL claim, not an optional extra.
- **`SELECT … FOR UPDATE SKIP LOCKED`** is the claim mechanism D-009 §1 already ratified. It
  is Postgres-specific.
- **A managed Postgres host is already the topology** in D-004 §"serving tier". Choosing SQLite
  now would contradict a ratified decision to save work that has not started.

> **Host: see D-014, and do not reuse the phrase this entry originally used.** An earlier draft
> of this section named *"the Fly Postgres addon"* as the host. **That phrase covers two
> different Fly products with different capabilities and separate CLI surfaces, and only one of
> them can run pgvector at all** — measured, not documentation: on the unmanaged cluster
> `jarvis-db2`, `pg_available_extensions` returns **zero rows** for `vector`, so pgvector is
> absent from the image entirely and no `CREATE EXTENSION` could ever succeed. The host is
> resolved in **D-014**: the existing **MPG** cluster `sentinel-holy-rain-4562`, database
> `pharmfoldmdk`, pgvector **v0.8.2** enabled. This entry defers to D-014 for the host and does
> not restate it.

What makes this entry worth writing is not the choice. It is **what the choice forces**, in
§3–§5.

#### §2 — The test database stays SQLite (D-005), and that is now a real split

D-005 fixed the test DB as SQLite: fast, deterministic, no external service, no container in
CI. That still holds. But with §1 settled, prod and test are now **different engines**, and
the gap between them is no longer theoretical.

**Named precedent — JARVIS, same class of failure, observed twice.** In the JARVIS project the
pytest suite built its schema with SQLite `create_all` and never ran the Alembic chain, so
migration-bootstrap bugs were structurally invisible to the tests: a green suite proved
nothing about whether a fresh database could actually be built. That was audit finding H2,
and it was fixed by adding a CI job that runs `alembic upgrade head` against a throwaway
Postgres. The gate earned its keep the same day it was cited here — an unguarded column rename
passed the full local suite and failed immediately against fresh Postgres.

The lesson transfers exactly: **a green SQLite suite is not evidence about Postgres.** D-005
already flagged this; §3–§5 make it structural rather than a note.

#### §3 — CORRECTION: `FOR UPDATE SKIP LOCKED` is a **syntax error** on SQLite, not an
untested path

The session pre-work stated that today's suite "proves the claim function's behavior, not its
concurrency." That is **true and misleading**, in precisely the way this log's *Method note*
warns about — an accurate summary that conceals the failure mode. It reads as though the
statement runs on SQLite and merely fails to exercise contention. It does not run at all.

**Measured, not assumed** (stdlib `sqlite3`, library version **3.45.1**):

```
SELECT id FROM jobs WHERE status='pending' ORDER BY created_at LIMIT 1 FOR UPDATE SKIP LOCKED
  -> OperationalError: near "FOR": syntax error
```

Narrowing it, because "SKIP LOCKED is unsupported" would itself have been an imprecise claim:

| Fragment | SQLite 3.45.1 |
|---|---|
| `FOR UPDATE` | `OperationalError: near "UPDATE": syntax error` |
| `FOR UPDATE SKIP LOCKED` | `OperationalError: near "UPDATE": syntax error` |

**`FOR UPDATE` itself is rejected**, not just the `SKIP LOCKED` modifier. SQLite has no
row-level locking to express, so there is no clause to degrade gracefully.

**Why the distinction changes the design.** "Unverified concurrency" invites one function with
a dialect branch, tested on the SQLite arm and assumed on the Postgres arm. "Syntax error"
makes that impossible to do honestly: the Postgres arm cannot execute in the suite *at all*,
so any structure that presents the two arms as one tested function is a coverage claim the
tests do not support. Recorded as a correction rather than silently designed around, per the
Method note's provenance rule.

#### §4 — The claim-function seam: a repository interface

**Decision.** The queue is reached through a narrow interface, not a function with an engine
branch inside it:

```
core/queue.py
    class JobQueue(Protocol):          # claim / complete / fail / reap_stale
    class PostgresJobQueue:            # the real one — SELECT … FOR UPDATE SKIP LOCKED
                                       # NEVER executed by the SQLite suite
tests/doubles.py
    class UnlockedFakeJobQueue:        # in-memory. Name says what it is not.
```

**The argument for the seam is coverage honesty, not scale.** Worth stating plainly because
the obvious objection is right on its own terms: at D-004's single-worker scale the
indirection buys **nothing operationally**. One worker cannot contend with itself, and if that
were the whole argument, the seam would be premature abstraction and should be skipped.

The actual argument is about what the test report claims. A dialect branch inside one function
appears in coverage as *one function, exercised*, with a small variation — when the Postgres
arm has never run a single time. Not under-tested: never executed. A separate implementation
class makes that visible in the shape of the code, and a double named `UnlockedFakeJobQueue`
(rather than `InMemoryJobQueue` or `TestJobQueue`) makes it visible at every call site. The
name is doing real work: it is the difference between a reader concluding "the queue is
tested" and "the queue's *callers* are tested against a fake that does no locking."

**Consequence, stated so it cannot be mistaken later:** the suite will prove the claim
function's *callers* handle claim/complete/fail/stale-reap correctly. It will prove **nothing
whatsoever** about `FOR UPDATE SKIP LOCKED` — not its syntax, not its semantics, not its
behaviour under contention. The seam does not test the queue. It stops the tests from
*claiming* to.

#### §5 — The seam is an honesty mechanism, not coverage

Explicit because it is the easy mistake to make next session: **§4 closes no gap.** It makes an
existing gap legible. The only thing that will actually exercise `PostgresJobQueue` is a
**Postgres integration job in CI** — a service container running the real engine, the item
already sitting in this log's open questions as *"Postgres integration test job for
pgvector/Postgres-specific paths (D-005 gap)."*

That job is **not** built in PR A. Until it exists, the honest statement of coverage is:

> The claim path has never executed. Its callers are tested against a fake that does no
> locking, and the fake is named to say so.

It remains an open question with a named owner-decision pending, not a solved problem. When it
is built, the JARVIS precedent in §2 is the template: a throwaway Postgres service in the gate,
migrations applied, the real implementation exercised. **D-014 adds a constraint on how:** that
job must use a **service container**, not a connection to the production MPG cluster — CI must
not depend on an external service, live credentials, or compute shared with JARVIS.

#### §5a — Constraint inherited from D-014: pgvector lives in `extensions`, not `public`

Recorded here because it lands on **PR A's migration work**, not at Iteration 3 when the vector
column is finally written.

pgvector v0.8.2 on the `pharmfoldmdk` database is installed in the **`extensions` schema**. A
migration emitting a bare `vector(384)` therefore fails with **`type "vector" does not exist`**
— the type is real and enabled, just not on the default `search_path`.

Three ways to handle it, and the choice is deliberately **not** made here:

| Approach | Trade-off |
|---|---|
| Schema-qualify the type (`extensions.vector(384)`) | Explicit and local; every vector column must remember it |
| Set `search_path` in the Alembic env / connection | One place; invisible at the call site, and a future connection that forgets it fails confusingly |
| `ALTER DATABASE … SET search_path` | Outside the migration chain — the exact class of environment state that is not reproducible from the repo |

**PR A does not create a vector column**, so it does not have to resolve this. It is written
down now so the first migration that *does* is designed rather than debugged, and so the
approach is chosen with the trade-off visible. **D-014 requires the chosen approach to be
recorded back into that entry.**

**Postgres version:** D-014 pins prod to **Postgres 16** (the MPG cluster's version, which
predates this project). Local dev and any future Postgres CI service container should match —
do not let tooling drift to 17, or the suite starts proving things about an engine prod does
not run.

#### §6 — Deep-learning justification

Inherited from D-009 §1 and still load-bearing: the queue is the mechanism that lets neural
inference run on hardware that can actually hold the model. D-011 split compute across a local
tier (≤440 aa) and rented GPU (>440 aa); **both** pull work through this queue, so a queue that
loses or double-claims jobs corrupts the cache that Iteration 1's entire demo is served from.

The Postgres choice specifically carries the DL work in a second way: **pgvector is where the
learned embeddings live.** Semantic search over ADC targets is a place a neural model does
primary work rather than decorating a database lookup, and SQLite cannot host it. Choosing
SQLite for prod would have meant either dropping that capability or rewriting the storage layer
to reintroduce it.

#### §7 — Consequences

- `db/` is created in PR A, and `ARCHITECTURE.md` §8 repo layout is updated in that same PR
  (governance rule 2).
- Alembic migrations target Postgres. The SQLite suite does **not** run the migration chain —
  the exact JARVIS H2 shape from §2. Mitigation is the §5 integration job; until it exists,
  this is a known, named exposure and not an oversight.
- `psycopg[binary]` is already pinned and hash-locked into CI (D-013 + Amendment A), so PR A
  adds no new dependency risk to the gate.
- The `sqlite_conn` fixture from D-007 stays for tests that genuinely only need a scratch
  database. It is not the queue's test path.
- **Alembic connects on the DIRECT string, not the pooled one** (D-014): transaction-mode
  poolers break DDL and session-level operations. The app uses the pooled string at runtime.
  Both live in secrets, never in the repo.
- **The host is D-014's, and this entry's host claim was wrong before it was corrected.** The
  original draft named "the Fly Postgres addon" — a phrase spanning two products, only one of
  which can run pgvector. Left as a marker: a plausible name for a dependency is not the same
  as a verified capability of it, and the difference was only found by querying the actual
  cluster.

---

### D-013 — Pinned dependency manifest + gate install step
- **Date:** 2026-07-21
- **Status:** Accepted — proven, not asserted (see §5).
- **Sequenced before D-012 and before any model code.** This entry modifies the **required
  status check**. Under D-008 that is exactly the class of change that gets *proven*, and it
  gets proven *first*, because everything after it depends on the gate still working.

#### §1 — The problem

The gate installs `pip install --upgrade pip pytest` and nothing else. That was correct for
the keel (D-007), whose fixture deliberately used stdlib `sqlite3` so the suite needed no
dependencies at all. It stops being correct the moment any application code imports
SQLAlchemy or Alembic: the suite would fail to import, and there is no manifest for the gate
to install.

**Why this is not a trivial plumbing change.** `test` is a required check on a
branch-protected `main` with `enforce_admins: true` and no bypass — for the owner either.
Adding an install step introduces failure modes the gate did not previously have:

| New failure mode | Effect while it lasts |
|---|---|
| Resolution failure (bad pin, yanked release, conflicting constraints) | every PR red |
| Version drift (unpinned dep ships a breaking release) | every PR red, with no repo change to explain it |
| Index flake / network failure | every PR red, intermittently |

Each of these blocks **every PR in the repo, including the PR that would fix it**, because
there is no admin bypass. That is the same deadlock shape D-008 removed when it deleted
`paths-ignore` — a required check that cannot report leaves PRs unmergeable forever. The
mitigation is different here (the check *can* report; it just reports red), but the blast
radius is the same and it deserves the same care.

#### §2 — Decision

- **Two manifests, both pinned to exact versions (`==`).**
  - `requirements.txt` — runtime dependencies (what prod needs).
  - `requirements-dev.txt` — `-r requirements.txt` plus test-only tooling.
- **The gate installs `requirements-dev.txt`**, which transitively installs the runtime
  manifest. Deliberate: installing only dev dependencies would let a broken *runtime* pin
  reach deploy untested, which is precisely what D-005 exists to prevent.
- **Exact pins, not ranges.** A range means the gate's behaviour can change with no commit
  in this repo — a red `main` with an empty `git log` to explain it. Reproducibility is also
  a standing requirement of this project: D-004 records `inference_settings` (dtype, chunk
  size, model revision) per job so a fold can be reproduced. A floating dependency set
  undermines that at the environment level. Pins are upgraded deliberately, in a PR, where
  the gate proves them.

Initial pins:

| Package | Pin | Why now |
|---|---|---|
| `SQLAlchemy` | `2.0.51` | models + queue functions (D-012, PR A) |
| `alembic` | `1.18.5` | migrations (D-009 §1) |
| `psycopg[binary]` | `3.3.4` | Postgres driver for prod (D-012). psycopg **3**, not psycopg2 — actively developed and the current SQLAlchemy 2.0 recommendation. `[binary]` avoids needing libpq headers at install time. |
| `pytest` | `9.1.1` | the suite. Previously unpinned and floating. |

`psycopg` is unused by the SQLite test suite and is installed anyway — the manifest describes
what **prod** needs, and proving it resolves is the point.

#### §3 — Caching: **NO**, deliberately

`actions/setup-python` can cache the pip download directory keyed on a hash of the manifest.
**We are not enabling it yet.**

- The saving is small: this dependency set installs in roughly 10–20 s against a suite that
  runs in ~20 s.
- The cost is a new failure mode on a check that has no bypass. A cache is another thing that
  can be stale, poisoned, or partially restored, and its failures are intermittent —
  the hardest kind to diagnose while every PR is blocked.
- Reinstating it is a one-line change with an obvious trigger: install time becoming a real
  cost as `app/`, `core/`, and `worker/` acquire dependencies.

Recorded as a decision rather than an omission so the absence is legible later.

#### §4 — Explicitly NOT in this manifest

`torch`, `transformers`, `bitsandbytes`, and the ESMFold model weights. They belong to the
**local/rented GPU tier** (D-004, D-011), not the Fly serving tier and not CI. The gate must
never attempt to install a CUDA stack — it would be slow, fragile, and pointless on a CPU
runner. The worker acquires its own manifest when `worker/` is built, and it is a separate
file by design.

#### §5 — Proof (D-008 pattern: demonstrate, do not assert)

A gate change is proven by watching it behave, in both directions:

1. **RED first.** The manifest was pushed with a deliberately invalid pin
   (`SQLAlchemy==2.0.99999`, a version that does not exist). Expected: `test` fails at the
   install step with a resolution error, before pytest runs — confirming the gate actually
   installs the manifest rather than silently ignoring it.
2. **GREEN second.** Pin corrected to `2.0.51`, same PR. Expected: install succeeds, suite
   green, check reports pass.

Both observations are recorded in this entry when they land, and the PR is not merged until
green is witnessed. *Result: see §6.*

#### §6 — Observed result

- **RED — observed.** Commit `93dc215`, run `29867026923`. `test` failed in **8 s** at the
  `Install dependencies` step:

  ```
  ERROR: Could not find a version that satisfies the requirement SQLAlchemy==2.0.99999
  ERROR: No matching distribution found for SQLAlchemy==2.0.99999
  ```

  **pytest never ran** — verified by grepping the failed job's log for
  `passed`/`failed`/`collected` and getting zero matches, rather than inferring it from the
  step ordering. `deploy` reported `skipping`, confirming `needs: test` still holds.

  This is the load-bearing observation. It proves the gate genuinely *resolves* the manifest
  rather than installing it best-effort and continuing, so a future bad pin fails loudly here
  instead of reaching deploy.

- **GREEN — observed.** Commit `3bc3a8f`, run `29867598394`. Pin corrected to `2.0.51`;
  install succeeded, `test` passed in **20 s**, pytest reported `1 passed in 0.01s`.

  Full resolved set, transitives included, so a later drift is diagnosable rather than
  mysterious — the pins name four packages, the environment actually contains thirteen:

  ```
  Mako-1.3.12  MarkupSafe-3.0.3  SQLAlchemy-2.0.51  alembic-1.18.5
  greenlet-3.5.3  iniconfig-2.3.0  packaging-26.2  pluggy-1.6.0
  psycopg-3.3.4  psycopg-binary-3.3.4  pygments-2.20.0  pytest-9.1.1
  typing-extensions-4.16.0
  ```

  **The nine unpinned transitives are the residual exposure.** Exact pins on direct
  dependencies do not freeze the environment; a breaking release of `greenlet` or `pluggy`
  can still turn the gate red with no commit in this repo. Fully closing that needs a lock
  file (`pip-compile` / `uv lock`) and is deliberately deferred — it is a real cost in
  maintenance for a risk that has not yet bitten. Recorded here so the gap is known rather
  than assumed away, and so that when an unexplained red does appear, this is the first place
  to look.

#### §7 — Deep-learning justification

Indirect, and honest about being indirect. No neural network runs in CI and none should. What
this buys the DL work is **reproducibility of the environment around it**: D-004 requires each
fold to record its `inference_settings` so a result can be reproduced, and that guarantee is
worth less if the surrounding library versions drift underneath it. Pinning the serving-tier
manifest is the environment-level half of the same commitment. It also protects the *ability
to ship* the DL work at all — an unbypassable gate stuck red halts every subsequent PR,
including the ones that carry the model.

#### §8 — Consequences

- `ARCHITECTURE.md` §5 (deploy gate) and §8 (repo layout) updated in this PR.
- The gate's install step is now a thing that can break independently of the tests. When it
  does, read the *install* step, not the pytest output.
- Upgrading any pin is a PR that the gate proves. There is no other supported route.
- A **Postgres integration job** is still absent (D-005's known gap, restated in D-012). This
  entry does not address it and must not be read as having done so.

---

#### AMENDMENT A (2026-07-21) — exact pins did not close the gap; a lock file does

**Recorded as an amendment rather than an edit to §1**, because the reasoning that led to
deferring was correct on the information available at the time, and overwriting it would
destroy the evidence of *why* the gap was missed. §1 stands as written.

**What §1 claimed and what was actually true.** §1 identified "version drift (unpinned dep
ships a breaking release) → every PR red, with no repo change to explain it" as a failure mode
the exact pins would close. **That claim is true of the four direct dependencies and false of
the environment.** The green run resolved them to **thirteen** installed packages; nine were
unpinned transitives (`greenlet`, `pluggy`, `Mako`, `MarkupSafe`, `packaging`, `iniconfig`,
`pygments`, `typing-extensions`, `psycopg-binary`). A breaking release in any of them still
reddened the gate with no commit in this repo — precisely the failure mode §1 named as
addressed.

This is the same error shape the *Method note* describes and the same one that produced the
fabricated SHAs in §6 the same afternoon: **a true statement about the part that was checked,
read as a statement about the whole.** "Direct dependencies are pinned" was accurate. "The
environment is pinned" was not, and only the second one is what §1 needed.

**Decision — lock the full graph.**

- `requirements.lock` and `requirements-dev.lock`, compiled with **`uv pip compile
  --generate-hashes --universal --python-version 3.11`** (uv 0.11.30). Every transitive is
  pinned and hashed; `--universal` resolves across platforms so the same lock serves Linux CI
  and a Windows dev machine.
- **The gate installs the lock with `--require-hashes`**, so pip refuses any artifact whose
  hash does not match. The installed environment is now a function of a committed file, which
  is the actual requirement: *a red gate is attributable to a commit in this repo.*
- The `.txt` manifests remain the **human-edited inputs** — they say what we want; the locks
  say what that resolved to. Changing a dependency means editing the `.txt`, recompiling, and
  committing both.

**Why now rather than later, and it is not maintenance appetite.** Two reasons:

1. **Cost curve.** `app/`, `core/`, and `worker/` are about to land, and the worker's tree is
   the heavy one — PyTorch, transformers, bitsandbytes. Locking four direct dependencies is
   cheap; locking after that arrives is not.
2. **It is the same discipline this project already applies to model weights.**
   `ARCHITECTURE.md` §7 commits to reproducibility as a *graded* expectation, and D-004
   records per-fold `inference_settings` including the model revision so a result can be
   reproduced. An environment with nine floating packages undermines that claim for exactly
   the reason a floating model revision would. **A lock file is the environment-level version
   of a pinned checkpoint.** That argument outweighs the maintenance cost in a way that
   general engineering hygiene, on its own, would not have.

**Tool choice.** `uv` over `pip-compile`: faster resolution, and it handles the two-manifest
split cleanly (`requirements-dev.txt` includes `requirements.txt`, and the compiled dev lock
correctly attributes each entry). **uv is a local authoring tool only — it is NOT installed in
CI.** The lock is plain hashed requirements format, so the gate uses stock pip and gains no new
dependency. That keeps the required check's toolchain as small as possible.

**Residual exposure, stated so it is not assumed away in turn:** the lock fixes *versions and
artifact hashes*, not the index's availability. A PyPI outage still reddens the gate and is not
attributable to a commit here. That is a network-availability problem, not a reproducibility
one, and no lock file addresses it.

**Proof:** the gate must go green installing from the lock with `--require-hashes` before this
merges. *Result recorded below on observation.*

- **Observed.** Commit `f569a45`, run `29868958805`. `test` green in **15 s**, installing via
  `python -m pip install --require-hashes -r requirements-dev.lock`, then `1 passed in 0.01s`.
  **13 packages installed**, all hash-verified:

  ```
  alembic-1.18.5  greenlet-3.5.3  iniconfig-2.3.0  mako-1.3.12
  markupsafe-3.0.3  packaging-26.2  pluggy-1.6.0  psycopg-3.3.4
  psycopg-binary-3.3.4  pygments-2.20.0  pytest-9.1.1
  sqlalchemy-2.0.51  typing-extensions-4.16.0
  ```

  Note the lock contains **15** entries but CI installed **13**: `colorama` and `tzdata` carry
  `sys_platform == 'win32'` markers from the `--universal` resolution and are correctly skipped
  on the Linux runner. That difference is expected and is the marker mechanism working — worth
  recording so a future reader does not read it as the lock being partially applied.

  **Not proven here:** that a *tampered* artifact is rejected. `--require-hashes` is asserted to
  do that and is standard pip behaviour, but this run only demonstrates the happy path. A
  negative arm would require serving a mismatched artifact, which is not worth building; the
  load-bearing red arm for this gate was already taken in §6.

---

### D-011 — Split compute: local tier under the ceiling, rented GPU for large-ECD cache generation
- **Date:** 2026-07-19
- **Status:** Accepted
- **⚠ Amended by D-042 (2026-07-23), after the first rental run.** Three claims here are corrected:
  the **unchunked** rental recipe (`chunk_size=None`) is **falsified** — the trunk is O(L³), so it
  OOMs on large L on any rentable card; rental now chunks (64). The **hardware/cost** was an RTX PRO
  6000 (95 GiB) at **$2/hr**, not an A6000 (48 GB) at $0.49, and the run cost ~$10–14, not ~$0.25.
  **Network volumes are billed monthly even after termination** — delete separately.
- **Context:** S-004/S-005 bracketed the local sequence-length ceiling to **(440, 630) aa**.
  440 aa folds clean at chunk 64 (28.6 s, peak 6665 MiB, no spill, host stable);
  630 aa is **4-for-4 fatal host crashes**. HER2's full ECD (~630 aa) — the flagship ADC
  target — cannot be folded locally. D-004 §5 bounded the response to smaller model /
  narrower targets / different compute, explicitly **not** retrieval. This selects
  **"different compute."**
- **Decision — two paths, one pipeline:**
  - **Local tier** (Blackwell 8 GB, int8 trunk / bf16 base, chunk 64): every target
    under the measured ceiling. Trop-2 (~250), Nectin-4 (~350), and the 440 aa class.
    **0 crashes in ~94 folds.**
  - **Rented GPU, one-time batch:** targets above the ceiling. A ≥24 GB card runs fp16
    `esmfold_v1` unquantized and unchunked, so **the entire local mitigation stack stops
    binding.**
- **Provider: RunPod.** Per-second billing, no minimum commitment, zero egress fees.
  - **Card: RTX A6000 48 GB at $0.49/hr** (Secure Cloud). Chosen over the RTX 4090 24 GB
    at $0.69/hr — more VRAM for less money; **headroom matters more than speed** for a
    one-time batch. Community Cloud is ~50% cheaper but uses community-contributed
    hardware with reduced reliability; not worth the interruption risk on a job this
    short and this cheap.
  - **No network volumes.** Storage bills at $0.07/GB/month even while the pod is
    stopped. Use container disk; download weights, fold, upload artifacts, terminate.
  - **Estimated total cost for the full Iteration-1 large-ECD cache: ~$0.25.**
    (~5 min weight download + ~10 min folding at $0.49/hr.)
- **Fly.io GPU is eliminated, not deprioritized.** Fly deprecated GPU Machines; they
  become **unavailable after 2026-08-01**. D-003's "GPU deprecation on Fly.io" risk and
  D-004's Fly-compute framing are superseded — the option ceases to exist in 13 days.
  Fly remains the **serving tier** (CPU-only app + Postgres/pgvector + Volume), unchanged.
- **Deep-learning justification:** D-003's core is preserved intact — we run ESMFold
  ourselves on both paths.† Renting a GPU changes *whose silicon* executes the model, not
  *who runs it*: we still control the checkpoint, the precision, the chunking and the code,
  and we still perform the inference. That is categorically different from calling a hosted
  inference API or retrieving pre-computed structures, which is what D-004 §5 rules out.
  The graded DL claim is unaffected — arguably strengthened, since the project now
  demonstrates a measured hardware constraint and a reasoned compute split rather than a
  single-machine assumption.

  > † **The source text for this justification was truncated mid-sentence** at *"we run
  > ESMFold ourselves on both"*. The completion above is the obvious reading and is
  > flagged so it can be corrected if it misstates the intent.

- **Superseded by this entry (verified by grep across `docs/`, `ARCHITECTURE.md`, `CLAUDE.md`):**
  - `docs/README.md` D-004 context — *"Fly.io GPU is uncertain/expensive"* → now **eliminated**,
    with a date.
  - `docs/README.md` D-006 context — *"Fly.io GPU availability is uncertain"* → same.
  - `docs/TDD_v3_ADC_Focused.md` §7 — *"GPU deprecation on Fly.io: Handled by preferring
    pre-computed structures and lightweight models."* The **risk has materialised**; the stated
    mitigation is superseded by this split-compute decision. *(Planning docs are historical
    intent — per this log's preamble, the log wins where they diverge. Not edited.)*
  - `ARCHITECTURE.md` lines asserting Fly has **no** GPU are **correct and unchanged** — they
    already agree with this decision.
- **Follow-ups:** build the rented-GPU batch as **committed, reproducible code in this repo**
  (the binding condition of D-009 §3 — the cache pipeline must not be a one-off script);
  decide where rented-run artifacts land (Fly Volume upload path, D-004 consequence, still open);
  and note the untested possibility from S-005 that HER2 may yet fold locally at `chunk 16/32`,
  which would shrink the rented batch but does not block it.

### S-005 — bisect the length ceiling at 440 aa
- **Date:** 2026-07-19
- **Status:** **CLOSED 2026-07-19 — 440 aa FOLDED CLEAN (reading 1).** 28.6 s at `chunk 64`,
  peak 6665 MiB (no spill), pLDDT 84.27, 440/440 CA, zero WHEA events, zero bugchecks.
  **⇒ the ceiling is in (440, 630).** Most of the curated ADC set is locally foldable; only
  HER2-class targets (>440 aa) need external compute.
- **Type:** Spike — a single bisection step. **One run, then stop.**

**The bracket.** Length is the discriminator (S-004). The evidence, instrument-free:
- **248 aa (Trop-2): 0 crashes in ~93 folds** — both precisions, spilling and not.
- **630 aa (HER2): 4 crashes in 4 attempts.**

The ceiling lies somewhere in **(248, 630)**. **440 aa is the closest integer to the true midpoint**
(439), so a single run halves the remaining bracket **whichever way it goes** — maximum information
per crash, which matters when each observation costs a host.

**Sequence — hold everything constant except length.** Take the **HER2 ECD (`P04626`, 23–652) and
truncate to its first 440 residues**. Same protein, same amino-acid composition, same code path,
same UniProt-derived source. **Deliberately NOT a different protein at ~440 aa** — that would
reintroduce composition and fold-difficulty as confounds, and this run only has budget for one
variable.

**Configuration:** int8 (S-003 recipe), `chunk_size` 64 descending on OOM, driver 596.72,
GPU process list verified empty, WHEA window recorded from a noted T0.

**Expect JSON corruption on a crash.** S-004's results file was truncated to NUL bytes by the
unflushed mid-write. **That is now the known signature of a host loss, not a surprise or a bug** —
stdout is the surviving record, so read it first.

**THE THREE READINGS — fixed in advance:**

| # | Observation | Reading |
|---|---|---|
| **1** | **Completes clean** | Ceiling is in **(440, 630)**. Most of the curated ADC set is **locally foldable**; only HER2-class targets need external compute. |
| **2** | **Crashes** | Ceiling is in **(248, 440)**. The constraint is **broad**, and external compute does **most** of the cache work. |
| **3** | **Completes, with corrected errors but no fatal** | The **burst-without-crash** pattern seen on six historical days (F-001). **Treat as a PASS.** Interesting, but **uninformative about the ceiling** — corrected errors do not predict crashes. |

**Reading 3 exists because of F-001:** without it, corrected errors during a successful fold would
have been misread as a near-miss or a partial failure. They are neither.

- **Deep-learning justification:** the ceiling determines how much of the curated ADC target
  database the local tier can fold, and therefore how much of the graded DL pipeline runs on
  owned hardware versus rented compute.
- **Stop condition:** **one run.** Do not bisect further tonight regardless of outcome.

---

#### RESULTS (2026-07-19) — **CLOSED. Completed clean. READING 1 fired.**

**HER2 ECD truncated to 440 aa folded successfully on the first attempt.** Host alive; last reboot
remains 19:02:08 (the S-004 crash), i.e. **no new reboot**.

| Measure | Value |
|---|---|
| Chunk | **64** — first attempt, no descent needed |
| Wall time | **28.6 s** |
| Peak VRAM | **6665 MiB**, `spilled = False` (free was 7043 MiB) |
| mean pLDDT | **84.27** *(rescaled ×100 per the scale trap)* |
| CA count | **440 / 440** — exact |
| NaN/inf coords | **0** |
| Radius of gyration | **24.64 Å** (compact-globular reference for N=440 ≈ 22.2 Å) |
| **WHEA in window** | **0 corrected, 0 fatal** (window 19:22:23→19:24:50 contains folds 19:23:49→19:24:17) |
| **Bugchecks** | **0** |

Null verified against a same-day control (78 WHEA events today, last at 19:02:29 — the S-004 crash).
This is **reading 1, not reading 3**: there were no corrected errors at all.

**⇒ THE CEILING IS IN (440, 630).** The bracket is halved. Structure is sane (exact residue count,
no NaN, Rg slightly above the compact-globular estimate as expected for a multi-domain elongated
ECD), and pLDDT 84.27 is **notably higher** than Trop-2's 74.68.

**Product consequence:** **most of the curated ADC target set is locally foldable.** Typical ADC
target ECDs — Trop-2 ~250 aa, Nectin-4 ~350 aa, and now anything up to at least 440 aa — run on this
machine. **Only HER2-class targets (>440 aa) need external compute.** That is a far narrower
constraint than S-004 alone implied.

**⚠ Observation, labelled as inference not measurement — a memory-adjacent reading of the 630 aa
crash.** Peak at 440 aa was **6665 MiB against 7043 MiB free — only 378 MiB of headroom** at
`chunk 64`. Activation memory grows steeply with length, so **630 aa at `chunk 64` would very
plausibly have exceeded free VRAM and spilled during the fold**, even though it did *not* spill at
rest (`resident 5351 MiB`). S-004's peak was **destroyed with the corrupted JSON**, so this cannot
be confirmed. If it is right, **HER2 might still fold at `chunk 16/32`** — the descent existed but
S-004 crashed at `chunk 64` before reaching it. **Not tested; one run was the budget.** This does
not resurrect the spill mechanism generally (the fp16 control showed sustained spill at 248 aa
causes no crash), but it is a live possibility specifically for the 630 aa case.

**Next bisection step if resumed:** ~535 aa, same truncation method.

### F-001 — INSTRUMENT CORRECTION: WHEA corrected-error rate was **inverted**, not merely invalid
- **Date:** 2026-07-19
- **Status:** Accepted. **This retroactively restates evidence in S-001, S-002 and S-003.**
- **Type:** Finding about the *measuring instrument*, not about the system under test. Logged
  separately because it invalidates reasoning across multiple prior entries.

**The claim:** WHEA **Id 17 (corrected)** errors are **crash debris, not a precursor ramp.** Every
comparison in this investigation that used corrected-error *rate* was measuring the wrong quantity.

**Evidence 1 — corrected errors are logged *with* the fatal, never *before* it.** Per-second
grouping of all WHEA events today:

| Second | Events |
|---|---|
| 16:32:33 | **Id1 ×1** + Id17 ×13 *(same second)* |
| 16:32:34 | Id17 ×18 |
| 16:44:45 | **Id1 ×1** + Id17 ×31 *(same second)* |
| 16:48:16 | **Id1 ×1** + Id17 ×3 *(same second)* |
| 18:04:51 | Id17 ×3 *(no fatal)* |
| 18:06:27 | Id17 ×3 *(no fatal)* |
| 19:02:29 | **Id1 ×1** + Id17 ×3 *(same second)* |

In **all four** crashes the fatal is logged **first or simultaneously** with the corrected errors.
There is no gradual ramp preceding a fatal. The corrected errors are what the machine emits *as it
dies*.

**Evidence 2 — six burst days produced zero fatals.** Corrected-error volume does not predict crashes:

| Date | corrected | fatal |
|---|---|---|
| 2026-05-27 | 3 | **1** ← crash on only 3 corrected |
| 2026-06-09 | **65** | **0** ← 65 corrected, no crash at all |
| 2026-06-13 | 3 | 0 |
| 2026-06-15 | 3 | 0 |
| 2026-07-04 | 3 | 0 |
| 2026-07-10 | 31 | 0 |
| 2026-07-14 | 40 | 0 |
| 2026-07-19 | 74 | **4** |

**65 corrected errors with no crash (06-09), versus a crash on only 3 (05-27).** The instrument is
not just noisy — it is **anti-correlated with the thing we were using it to predict.**

**RESTATEMENTS forced by this finding:**

1. **S-002's rate comparison is void.** *"65 corrected in the crashing window vs 0 in clean runs"*
   was **three crash events versus zero crash events, double-counted** — the corrected errors were
   debris from those same three crashes. **The valid measure was always the fatal count: now 4 vs 0.**
2. **The fp16 control's "zero corrected errors" is weaker than recorded.** It reduces to
   **"no crash"** — which host survival had already established independently. **The refutation of
   the spill mechanism still stands, but it stands on the fatal count, not the corrected count.**
3. **"217 corrected errors since May, pre-existing" was true and largely irrelevant.** It does not
   describe a steadily degrading link. It describes a fault that **fires in bursts and usually
   recovers**. The 18:04/18:06 events previously attributed to the driver install **may equally have
   been a spontaneous burst — that is now unknowable, and is recorded as unknowable.**
4. **What survives with no instrument at all — and it is the strongest evidence in the
   investigation:**
   > **4 crashes in 4 HER2 (630 aa) attempts. 0 crashes in ~93 Trop-2 (248 aa) folds today** —
   > across **both precisions**, **spilling and not**, including 83 consecutive folds under
   > sustained load.

   This correlation depends on no event log, no severity bucketing, and no interpretation of WHEA
   semantics. Everything else in S-002 is weaker than this one line.

- **Deep-learning justification:** neutral (instrumentation), but it protects every downstream
  decision — the local tier's viability was being judged against a metric that was measuring
  crash aftermath.
- **Method note connection:** this is the same failure as `params_all_on_cuda` and the WHEA counts —
  **a true summary that answered a different question than the one asked.** Extend the method note:
  before using a metric as a *leading indicator*, verify its events actually **precede** the thing
  it is meant to predict.

### S-004 — int8 + HER2 (630 aa), the untested crash condition
- **Date:** 2026-07-19
- **Status:** **CLOSED 2026-07-19 — HOST CRASHED (4th bugcheck, `0x00020001`, 19:02:28).
  Pre-registered READING 4 fired: escalation is not gradual and the corrected-error instrument is
  invalid as a leading indicator.** Duration eliminated as the trigger; **sequence length** is the
  discriminator. See RESULTS and **F-001** below.
- **Type:** Spike. **This entry is a pre-registration** — the four readings below are fixed *now*
  so the result cannot be rationalised after the fact.

**Why this run:** every host bugcheck (3/3) occurred on **HER2, 630 aa**. Both S-002 Q1 arms used
**Trop-2, 248 aa**, so **the actual crash condition has never been reproduced**, and sequence length
changed alongside the driver update — neither the spill hypothesis nor the driver hypothesis is
cleanly isolated. HER2 is also the **flagship ADC target** the curated cache needs, so this is the
product requirement and the decisive experiment at once.

**Configuration:** **int8** (S-003) — deliberately the *lower-risk* option, since it does not spill;
`chunk_size` descending from 64 as needed; driver **596.72** held constant; WHEA counted against
recorded ISO windows (harness already emits per-fold timestamps).

**Read against the two-cap amendment (D-009 §3):** a fold completing at **`chunk 16` in four
minutes is a PASS for the cache path**, and simultaneously a FAIL for the interactive path. Do not
record a slow-but-successful fold as a failure.

**THE FOUR READINGS — fixed in advance:**

| # | Observation | Reading |
|---|---|---|
| **1** | Errors **escalate** (corrected → fatal), crash or not | **Spill/load mechanism supported**; driver hypothesis weakened |
| **2** | **Zero errors** across the run | **Mechanism substantially weakened**; driver becomes the leading explanation |
| **3** | Errors appear but **stay corrected** | Link *is* stressed by this workload, but **the new driver handles it** — both hypotheses partially right |
| **4** | **Host crashes with no prior corrected errors** | **Neither story is complete — escalation is not gradual.** This would invalidate our use of corrected-error rate as a leading indicator |

**Reading #4 is the one neither hypothesis anticipated.** Our entire model has assumed corrected
errors are the early-warning signal that precedes a fatal. If a crash arrives with a clean WHEA log,
that assumption is wrong and the monitoring approach in S-002 needs rebuilding, not just its
conclusion.

**Preconditions to record (verify, do not assert):** driver version, free VRAM, GPU compute-process
list, HVCI state, WHEA Id-17/Id-1 counts immediately before, and ISO start/end per fold.
**Everything committed and pushed before the run** — a host loss takes the session with it.
**Risk:** lower than the fp16 control (no spill), but this is the exact sequence length that
crashed the host three times. Host loss remains a plausible outcome.

- **Deep-learning justification:** HER2 is the flagship ADC target; folding its 630 aa ECD is the
  headline capability of the curated cache. This run decides whether the local tier can produce it.

---

#### RESULTS (2026-07-19) — **CLOSED. The host crashed. Pre-registered READING 4 fired.**

**Outcome: reading 4, not reading 3.** Reading 3 required errors to *"appear but stay corrected"* —
i.e. **no fatal**. A fatal occurred, and the corrected errors arrived **in the same second as the
fatal, not before it**. That is reading 4 verbatim: *"host crashes with no prior corrected errors →
neither story is complete; escalation is not gradual."* **The reading that neither hypothesis
anticipated is the one that fired** — which is precisely what pre-registering it was for.

**Fourth crash of the day, same signature:**

| # | Bugcheck | Code |
|---|---|---|
| 1 | 16:32:32 | `0x00020001` |
| 2 | 16:44:44 | `0x00020001` |
| 3 | 16:48:15 | `0x00020001` |
| **4** | **19:02:28** | **`0x00020001`** |

**What S-004 got before it died** (stdout survived; the results JSON was **corrupted to NUL bytes** —
an unflushed mid-write file, itself a signature of abrupt power loss rather than clean exit):

| | Value |
|---|---|
| Run start | 19:01:17 |
| Config | **int8**, `resident 5351 MiB`, **`spills_at_rest = False`** |
| Target | HER2 ECD `(23, 652)`, **630 aa** |
| **Chunk size** | **64** — the *first* attempt; it never reached the descent to 32/16/8 |
| **Peak VRAM** | **UNKNOWN — the record was destroyed by the crash.** No `OK` line was ever printed. |
| **Time into the fold** | **≈56 s** (fold began ≈19:01:32 after load; bugcheck 19:02:28) |
| PDB saved | none — no fold completed |

**Driver 596.72 and LM Studio are ELIMINATED as explanations** — the crash reproduced with the new
driver installed and with the GPU compute-process list verified empty at T0.

**⭐ Duration is NOT the trigger — sequence length is.** This is the one open mechanism question, and
the data now answers it:
- The **fp16 Trop-2 control** ran **five individual folds of 73.4–74.1 s each** — and **did not crash**.
- **S-004 crashed ≈56 s into a single fold** — *shorter* than folds the machine had just tolerated
  five times in a row.

**A shorter fold killed it while longer folds survived.** Single-fold duration up to ~74 s is
tolerated, so duration is eliminated. What differs is **sequence length / activation geometry**
(630 aa vs 248 aa). Spill is eliminated too: int8 does not spill at rest, and it crashed anyway.

**Cache-path verdict:** **FAIL** — but *not* on the two-cap latency criterion. It never produced a
structure at any chunk size, because the host died mid-fold. The two-cap amendment (which would have
scored a slow `chunk 16` fold as a PASS) never got the chance to apply.

### S-003 — Spike: find a configuration of `esmfold_v1` that fits under 7799 MiB
- **Date:** 2026-07-19
- **Status:** **CLOSED 2026-07-19 — PASS ON FIT** (int8 ESM-2 trunk quantization: peak 5779 MiB, no
  spill, all params on GPU). **Quality anomaly (+4.0 pLDDT) verified as real and non-degenerate**
  — deterministic across repeat folds and structurally sane — **but accuracy remains unproven**
  pending a cross-precision TM-score/RMSD comparison. Logged before the work per D-002; results and
  verification appended below.
- **Type:** Spike (time-boxed measurement). Produces a candidate configuration, not shipped code.
- **Question:** Is there a configuration of `facebook/esmfold_v1` whose **peak VRAM stays under
  7799 MiB** while **fold quality holds within a few points of the Trop-2 ECD baseline of
  mean pLDDT 70.7** (S-001)?
- **Why now:** S-001 measured the fp16 model resident at **8116 MiB** — over budget before any
  fold. S-002's (predicted, unmeasured) mechanism says the resulting spill traffic across PCIe is
  what escalates this GPU's long-standing corrected link errors into fatal ones. **S-003 produces
  the fitting configuration; S-002 Q1 then tests whether it stops the crashes.** Order matters:
  fit first, then sustained load.

**Method — test in this order, each against the same target:**
- **Baseline target:** Trop-2 / TACSTD2 ECD (`P09758`, topological range 27–274, **248 aa**),
  `chunk_size=64`, compared to **mean pLDDT 70.7** from S-001.
  1. **bfloat16** — same footprint as fp16, better numerical headroom. **Expected NOT to fit**
     (bf16 and fp16 are both 2 bytes/param); run it regardless, as a one-line change, for the
     numerical-stability/quality comparison.
  2. **8-bit quantization of the ESM-2 trunk** via `bitsandbytes`, **folding head left at full
     precision**. This is the real candidate: the ESM-2 LM is the bulk of the ~3B params, so int8
     roughly halves the dominant term.
  3. **4-bit** — only if 8-bit is insufficient. More quality risk; measure rather than assume.
- **EXCLUDED BY DESIGN — do not test CPU-offload of the trunk.** It trades VRAM for **PCIe
  traffic**, which is precisely the mechanism suspected (S-002) of escalating the link fault.
  Deprioritized *because of* what S-002 found, not for cost.

**Record per configuration:** resident VRAM after load; peak VRAM during fold; wall time; mean
pLDDT; and the pass flag **peak < 7799 MiB**. *(Note: 7799 MiB was free in S-001 run 1; runs 2–3
saw only 7043 MiB free because the desktop held more. The fixed 7799 MiB target is used as
specified, and actual free-at-start is recorded alongside so the margin is visible.)*

**Harness:** reuse the S-001 harness unchanged — parameter **placement assertion**, **spill
detection** against physical/free VRAM, **JSON written after every step** (so a host crash cannot
destroy partial results), and **pLDDT scale-trap handling** (0–1 → ×100, stated explicitly).
Each configuration runs in a **fresh process** so resident VRAM is measured clean.

- **Stop condition:** halt at the **first configuration that fits cleanly and holds pLDDT within a
  few points of 70.7**. **Do NOT proceed to HER2 (630 aa) or sustained load** — that is S-002 Q1
  and a separate, riskier test.
- **Deep-learning justification:** this *is* the model-execution engineering, and it strengthens
  the graded story rather than weakening it: *"we measured VRAM constraints on real hardware,
  quantized the LM trunk, and validated that fold quality held"* is substantially more interesting
  than *"we ran the model as shipped."* Quantization with a measured quality check against a
  baseline is legitimate DL inference work.
- **Decides:** the candidate configuration handed to S-002 Q1, and the **replacement rung one** of
  the invalidated D-006 ladder (which must be a *resident-footprint* reduction).
- **Deliverable:** results appended here; then D-006's ladder is rewritten with the measured rung
  one, and S-002 Q1 runs against the winning configuration.

---

#### RESULTS (2026-07-19) — **Status: CLOSED. A fitting configuration exists: int8 trunk quantization.**

All runs: Trop-2 / TACSTD2 ECD (`P09758`, 27–274, **248 aa**), `chunk_size=64`, fresh process each,
`physical=8151 MiB`, `free_at_start=7043 MiB`. Pass = peak < 7799 MiB **and** no spill **and**
pLDDT within 5 pts of 70.7.

| Config | resident | peak | fits <7799 | spilled | wall time | mean pLDDT | Δ vs 70.7 | verdict |
|---|---|---|---|---|---|---|---|---|
| fp16 (S-001 baseline) | 8116 MiB | 8545 MiB | ❌ | **yes** | 48.8 s | 70.7 | — | baseline |
| **bf16** | **8116 MiB** | 8544 MiB | ❌ | **yes** | 45.4 s | **70.9** | **+0.2** | **FAIL (fit)** |
| **int8 ESM-2 trunk** | **5351 MiB** | **5779 MiB** | ✅ | **no** | **26.6 s** | **74.7** | **+4.0** | **✅ PASS** |
| 4-bit | — | — | — | — | — | — | — | **NOT RUN** (stop condition met) |

**Winning configuration (reproducible recipe):**
- `BitsAndBytesConfig(load_in_8bit=True, llm_int8_skip_modules=['trunk', 'distogram_head',
  'ptm_head', 'lm_head', 'lddt_head', 'esm_s_mlp', 'esm_s_combine', 'af2_to_esm'])`,
  `device_map={"": 0}` — i.e. **quantize the ESM-2 LM only; the folding head stays full precision.**
- `bitsandbytes 0.49.2`, `torch 2.11.0+cu128`, `transformers 5.14.1`,
  revision `75a3841ee059df2bf4d56688166c8fb459ddd97a`, `chunk_size=64`.
- **Blackwell note:** bnb blockwise quantization verified working on **sm_120** before the run —
  this was a genuine feasibility risk worth checking ahead of a long job.

**Findings:**
1. **bf16 behaved exactly as predicted** — resident identical to fp16 *to the megabyte* (8116 MiB),
   because both are 2 bytes/param. It cannot fit by construction. **Keep it anyway** for numerical
   headroom: quality was unchanged (+0.2) at no cost.
2. **int8 is the fit remedy.** Resident drops **2765 MiB** (8116 → 5351) and peak lands
   **5779 MiB — comfortably under both the 7799 MiB target and the 7043 MiB actually free.**
   `spilled=False` for the first time in this project.
3. **It is also ~1.8× faster** (26.6 s vs 45–49 s). This is *indirect support* for S-002's
   spill-overhead mechanism — removing spill nearly halved wall time — but it is **not
   confirmation**; confirmation still requires the sustained-load test (S-002 Q1).

**⚠ Caveat on the +4.0 pLDDT — do not read this as "quantization improved quality."**
- **pLDDT is the model's self-confidence, not accuracy.** A higher pLDDT means the model is more
  confident, which is *not* the same as more correct. A +4.0 shift means the int8 run produced a
  **different** prediction, not a demonstrably better one.
- What the data *does* support: **quality did not degrade** by the agreed proxy, so the pass
  criterion is met honestly.

---

#### QUALITY VERIFICATION (2026-07-19) — the anomalous number, checked before it gets cited

Two holes were open in the +4.0 result: it could have been **run variance**, and a fold that
**collapses to something trivial** can score deceptively well on per-residue confidence while being
structurally wrong. Both are now closed. *(Same discipline as the WHEA correction: the surprising
number gets checked, not celebrated.)*

**1. Reproducibility — identical sequence folded twice under int8:**

| Run | wall time | mean pLDDT | CA count | NaN/inf coords | Rg |
|---|---|---|---|---|---|
| 1 | 11.9 s | **74.68** | 248 / 248 | 0 | 18.74 Å |
| 2 | 7.3 s | **74.68** | 248 / 248 | 0 | 18.74 Å |

**pLDDT run-to-run delta = 0.000; CA-RMSD between runs = 0.0000 Å.** The model is **fully
deterministic**, so **the +4.0 shift vs the fp16 baseline is a real effect of the precision change,
not run variance.** *(Hole closed.)*

**2. Non-degeneracy — the structure is genuinely folded, not trivial:**
- **Residue count exact:** 248 CA atoms for a 248 aa input — no truncation, no padding artifacts.
- **No NaN/inf coordinates** anywhere in the file (all ATOM records parsed and checked).
- **Radius of gyration 18.74 Å**, against reference bands for N=248:
  compact globular `2.2·N^0.38` = **17.9 Å** (expected) vs random coil `2.0·N^0.60` = **54.7 Å**.
  Measured sits **essentially on the compact-globular expectation** — not collapsed (which would be
  ≪12 Å) and not extended. *(Hole closed — the "confidently wrong garbage" failure mode is ruled
  out.)*
- PDBs saved (`trop2_int8_run{1,2}.pdb`, byte-identical) so the cross-precision comparison below is
  cheap to run later.

**What is now established:** the int8 configuration produces a **deterministic, structurally sane,
compact fold**, and its higher pLDDT is a genuine consequence of the precision change.

**What remains open — and why the quality claim is still bounded:** pLDDT is *still* self-confidence.
A sane, compact, confident structure can nonetheless differ from the truth. Settling *accuracy*
requires **TM-score / CA-RMSD between the fp16, bf16, and int8 structures**, ideally against an
experimental Trop-2 ECD structure. The fp16/bf16 PDBs were **not saved** during S-003, so this needs
one short re-run per precision. **Outstanding follow-up; do not claim accuracy until then.**
A plausible-but-untested reading of the direction: fp16's narrow exponent range can underflow in a
3B LM trunk, so the fp16 baseline may itself be the mildly degraded one. **Hypothesis, not finding.**

**Observation (weak, recorded as such):** the bf16 run spilled (peak 8544 > 8151 physical) for
~45 s and produced **no new WHEA errors**. Weakly consistent with S-002's mechanism being about
*sustained* traffic volume rather than spill per se — a 45-second fold may not accumulate enough.
Suggestive only; the three crashes were all on the 630 aa fold, a far longer job.

**Scope discipline:** stopped at the first passing configuration, as specified. **4-bit not run.
HER2 (630 aa) not run. Sustained load not run** — that is S-002 Q1, deliberately separate and
riskier.

**Hands off to:**
- **S-002 Q1** — run sustained load against the int8 configuration. The falsifiable prediction is
  now testable with a config that genuinely does not spill.
- **D-006** — replacement **rung one is measured**: *quantize the ESM-2 trunk to int8 (folding head
  full precision)*, with bf16 retained for the unquantized parts.
- **Follow-up:** structural comparison (TM-score/RMSD) across precisions to convert the pLDDT
  proxy into a real quality claim.

### S-002 — Spike: host stability under sustained GPU load, and a resident-footprint fix
- **Date:** 2026-07-19
- **Status:** **BOTH ARMS MEASURED 2026-07-19 — the spill mechanism is TESTED AND NOT SUPPORTED.**
  Non-spilling int8 (600 s, 83 folds) and **spilling fp16 (368 s, 5 folds)** each produced
  **0 corrected, 0 fatal, 0 bugchecks**. Restoring spill did not restore errors, so spill is not
  sufficient to trigger the fault under driver 596.72 at 248 aa. The **driver update is the leading
  explanation but is not established** — the original crash condition (HER2, 630 aa) was never
  reproduced, and a 6-minute clean window has weak power against a fault that historically appeared
  on 8 days out of ~54. Q2 superseded by S-003, which found the fitting config.
- **Type:** Spike (time-boxed investigation). Produces measurements and a decision input.
- **Why it exists:** S-001 ended in **three identical host bugchecks** (`0x00020001`
  HYPERVISOR_ERROR, byte-identical parameters, 16:32 / 16:44 / 16:48) during a 630 aa fold run
  under VRAM spill. Two questions are now open and they gate everything downstream.

**Q1 — Is the local inference tier viable at all?** (the decisive one)
> **REFRAMED after the Q1 results below.** This is no longer a generic "does it survive load"
> test — it is a **specific falsifiable prediction with a mechanism**: *spill traffic across the
> PCIe bus is what escalates this GPU's long-standing corrected link errors into fatal ones.*
> Therefore **a configuration that fits within VRAM should crash far less, or not at all.**
> Measure the fatal rate as a function of whether the workload spills — not merely whether one
> run survives.
- **The distinguishing test:** run a workload that fits *comfortably* in VRAM (well under
  7043 MiB free — e.g. a small model or a short sequence with the trunk sized to fit) under
  **sustained** GPU load for several minutes, and see whether the host stays up. Watch WHEA
  Id-17 corrected-error *rate* as the leading indicator, not just the crash/no-crash outcome.
  - **Runs clean, corrected-error rate stays low → spill-mediated escalation confirmed.** The
    resident-footprint fix (Q2) becomes the remedy that keeps the local tier alive.
  - **Crashes anyway, or corrected errors spike without spill → the link fails under GPU load
    generally.** Then the local GPU tier is not viable as designed, D-004's topology needs rework
    (not just its mitigation stack), and cache generation must happen elsewhere.
- **Record:** wall-clock survived under load, peak VRAM, GPU clocks/temperature, and any new
  Event-Viewer bugcheck (ID 41 / 1001) with its code and parameters.
- **Also worth doing:** read the existing minidumps (`071926-18656-01`, `071926-21093-01`,
  `071926-20781-01`) — the faulting module would separate "WDDM/shared-memory path" from
  "driver/hardware" cheaply, before any new run.

**Q2 — Which resident-footprint reduction actually fits 8 GB?** (bounded by D-004 §5)
- Candidates, each needing its own measurement (none is free):
  1. **Quantize the ESM-2 trunk** (e.g. 8-bit/4-bit) — cheapest to try; measure resident MiB,
     fold time, and **mean pLDDT vs the fp16 baseline (70.7 on Trop-2 248 aa)** to detect
     quality loss.
  2. **CPU-offload the language-model stack, keep the folding head resident** — trades VRAM for
     PCIe traffic; measure the wall-time cost honestly (this is the configuration D-004's stack
     never assumed).
  3. **Smaller ESM-2 backbone + folding head** — flagged as a **research project, not a config
     change**: `esmfold_v1` is the only released ESMFold checkpoint.
- **Out of bounds (restating D-004 §5):** making AlphaFold retrieval the deliverable. That is
  not a memory fix, it is abandoning D-003's graded DL claim.
- **Note:** warm-cache load is 15–16 s, so *load-per-job* is a live option and the worker need
  not hold the model resident.
- **Decides:** whether D-004's local tier survives; the D-006 replacement ladder (new rung one);
  and the D-009 §3 length cap, which stays unmeasured until a clean configuration exists.
- **Time box:** Q1 first — it is cheap and it can invalidate Q2 entirely. Do not spend effort
  choosing between quantization strategies for a host that cannot stay up under load.
- **Deliverable:** results appended here; then the D-006 ladder is rewritten and the D-009 §3
  cap is set (or the topology is reopened).

---

#### Q1 ANSWERED (2026-07-19) — **hardware fault: the GPU's PCIe link.** Not a memory-pressure cascade.

**Source discipline: the minidumps were NEVER READ.** `C:\Windows\Minidump` is inaccessible
without an elevated shell (we are not admin) and no debugger (`cdb`/`kd`/WinDbg) is installed.
Every finding below comes from **Windows event-log records** — WHEA-Logger (hardware errors) and
BugCheck/Kernel-Power (crashes). WHEA names the failing component directly, so it answers "what
faulted" better than `!analyze -v` would have; it does **not** by itself answer "since when",
which is why the history below is checked separately.

**What faulted — identified, not inferred:**
- All corrected errors are **PCI Express Advanced Error Reporting (AER)**, component
  *"PCI Express Legacy Endpoint"*, at bus:dev:fn `0x1:0x0:0x0`, device
  **`PCI\VEN_10DE&DEV_2D39&SUBSYS_234917AA&REV_A1`** — confirmed via `Get-PnpDevice` to be the
  **NVIDIA RTX PRO 2000 Blackwell Laptop GPU** (the inference GPU itself).
- **65 corrected AER errors today**, in bursts: **31 @ 16:32, 31 @ 16:44, 3 @ 16:48**.
- **3 × WHEA `Id 1` FATAL hardware errors** at **16:32:33, 16:44:45, 16:48:16** — one per
  bugcheck, matching the three `0x00020001` crashes 1:1.
- **No display-driver TDR** (no Event 4101 / `nvlddmkm` reset). So this is **not** a driver hang
  under memory pressure — it is link-level hardware error escalation.
- **VBS/HVCI is running** (`VirtualizationBasedSecurityStatus=2`, services `2,3,4`), which is why
  a fatal hardware error surfaces as **HYPERVISOR_ERROR**: the hypervisor is the reporting layer,
  not the culprit.

**History — checked, and it splits in two. A first-pass claim that "the fault predates the
project" was PARTLY REFUTED on inspection; both halves are recorded here.**

*Half that survives — the corrected link errors DO predate the project:*

| Date | Id 17 (corrected) | Id 1 (fatal) |
|---|---|---|
| 2026-05-27 | 3 | 1 |
| 2026-06-09 | 65 | – |
| 2026-06-13 | 3 | – |
| 2026-06-15 | 3 | – |
| 2026-07-04 | 3 | – |
| 2026-07-10 | 31 | – |
| 2026-07-14 | 40 | – |
| **2026-07-19** | **65** | **3** |

All **148 pre-today** corrected events are the *same component on the same device*:
`17 | PCI Express Legacy Endpoint | PCI\VEN_10DE&DEV_2D39&SUBSYS_234917AA&REV_A1`. So a
**corrected PCIe link problem on this GPU genuinely predates PharmFoldMDK** (7 days spanning
~7 weeks). That much is solid.

> ⚠ **Restated by F-001: true, but largely irrelevant.** This is **not** a steadily degrading link.
> It is a fault that **fires in bursts and usually recovers** — six of those seven days produced
> **zero** fatals (including 65 corrected on 06-09 with no crash). Corrected-error history says
> almost nothing about crash risk. The **18:04 / 18:06** events attributed above to the driver
> install **may equally have been a spontaneous burst — now unknowable, recorded as unknowable.**

*Half that was REFUTED — the CRASH does not predate it:*

All bugchecks in 90 days (only four):

| When | Bugcheck | Parameters |
|---|---|---|
| 2026-05-27 19:44 | **`0x00000133`** (DPC_WATCHDOG_VIOLATION) | `0x0, 0x500, 0x500, 0xfffff800c77c53c8` |
| 2026-07-19 16:32 | `0x00020001` | `0x28, 0x1, 0x29b92701, 0xfc801000` |
| 2026-07-19 16:44 | `0x00020001` | *(identical)* |
| 2026-07-19 16:48 | `0x00020001` | *(identical)* |

**The `0x00020001` signature has ZERO occurrences before today** — three today, all during
ESMFold runs. The single earlier fatal (May 27) came with a *different* bugcheck and mechanism.

**The clean split (213 corrected / 4 fatal out of 217):**

| | Corrected (Id 17) | Fatal (Id 1) |
|---|---|---|
| **Before today** | **148** across 7 days | **1** (May 27) |
| **Today** | **65** | **3** |

**Synthesis — three parts, all load-bearing:**

1. **The link fault is pre-existing and independently evidenced.** Corrected AER errors on this
   exact device occur on 7 days back to 2026-05-27 — including 65 on 06-09 and 40 on 07-14, days
   with no ESMFold anywhere near this machine. **The May 27 fatal is the key corroboration: the
   link can go fatal without ESMFold**, so the weakness is real and independent of us.
2. **The workload is an accelerant, not the cause. ⚠ THE RATE IS THE EVIDENCE — NOT THE RAW
   COUNTS.** **One fatal in eight weeks of ordinary use versus three in under twenty minutes**
   ≈ **four orders of magnitude**. Read the counts alone ("217 errors, going back to May →
   pre-existing, unrelated to us") and you reach the wrong conclusion — *which is exactly what
   happened in the first draft of this entry.* The counts are compatible with both hypotheses;
   only the **rate under load**, bucketed by **severity**, separates them. Neither "pre-existing
   hardware, unrelated to our workload" nor "our workload broke the machine" is correct: this is
   the **latent-fault-triggered** reading.
3. **Mechanism — ⛔ TESTED AND NOT SUPPORTED (2026-07-19; both arms measured, see Q1 CONTROL
   RESULTS).** Restoring spill did **not** restore the errors, so this chain is *undermined*, not
   confirmed; the driver update is now the leading explanation, though itself unestablished.
   The proposed chain was
   *spill → sustained PCIe traffic → corrected errors escalate to uncorrected*: the fp16 model
   overruns VRAM (resident 8116 MiB vs 7043 MiB free; peak 8545 MiB vs 8151 MiB physical — i.e.
   **~0.4 GB beyond total physical, ~1.1–1.5 GB beyond what was actually free**), and WDDM services
   that overrun by shuttling memory across the PCIe bus. This is **plausible and fits the data, but
   it is not established** — it connects S-001 to the crash rather than competing with it, and
   **S-002 Q1 is what confirms or refutes it.** Do not cite it as a finding until then; when
   measured, update this clause from *predicted* to *measured*.

**Falsifiable prediction (this is now S-002 Q1, with a mechanism instead of a generic load test):**
*a configuration that fits within VRAM should crash far less — or not at all — because it does not
generate the spill traffic.* If it holds, the resident-footprint fix is not merely a performance
optimization; it is the thing that keeps the local tier alive. If it fails, the link fails under
GPU load generally and the tier is done on this machine.

---

#### Q1 RESULTS — non-spilling arm (2026-07-19) — **prediction held; attribution confounded**

**Test:** int8 configuration (S-003), **Trop-2 ECD 248 aa only — deliberately NOT HER2**, folded
repeatedly under continuous load.

**Windows stated explicitly — containment, not assumed alignment:**

| Window | Start | End | Source |
|---|---|---|---|
| **WHEA query window** | **18:14:27** (T0, recorded to file) | **18:33:30** (T1, query clock) | recorded |
| **Fold window** | **≈18:17:05** | **≈18:27:05** (600.1 s) | **reconstructed** |

The WHEA window **strictly contains** the fold window, with ~2.6 min of margin before and ~6.4 min
after. Zero events across the *superset* therefore implies zero during folding — a stronger claim
than aligning two windows, and it needs no alignment assumption.

⚠ **Harness gap (fix before the fp16 control):** `s002_q1.py` recorded **only relative elapsed
times** (`elapsed_s`, `time_s`) and **no absolute timestamps**. The fold window above is therefore
*reconstructed* from file mtimes — the results JSON is rewritten after every fold, so its last write
(18:27:04.86) marks the end of the final fold, minus `total_elapsed_s = 600.1 s` for the start.
That reconstruction is sound but it is an inference, not a record. **The control harness must emit
ISO-8601 start/end timestamps per fold** so the fold and WHEA windows are *shown* to correspond.

| Measure | Value |
|---|---|
| Folds completed | **83 consecutive** |
| Sustained duration | **600.1 s** (10 min), GPU 99% util, 2190 MHz, 81 °C, ~75 W |
| Resident / peak VRAM | 5351 / **5779 MiB** — pinned, `spills_at_rest = False` |
| mean pLDDT | 74.68 on **every** fold (deterministic, as S-003 verification found) |
| **WHEA Id 17 (corrected) in window** | **0** |
| **WHEA Id 1 (fatal) in window** | **0** |
| **Bugchecks / unexpected shutdowns** | **0** — host survived |

**Null result verified, not assumed:** `Get-WinEvent` throws when it matches nothing, so an empty
result is indistinguishable from a broken query. A **control query over the same day returned 74
events** (71 corrected + 3 fatal), confirming the query works; the **last WHEA event of any kind was
18:06:27, before the window opened.**

> ⛔ **VOID — see F-001 (instrument correction).** The corrected-error comparison below measures
> **crash debris, not precursors**: the fatal is logged in the *same second* as the corrected errors
> in all four crashes, and six historical burst days produced 65/40/31 corrected errors with **zero**
> fatals. *"65 corrected in the crashing window vs 0 in clean runs"* is **three crash events versus
> zero, double-counted.* **The valid measure was always the fatal count: 4 vs 0.** Text retained
> for provenance.

**Rate contrast — phrased to what the data supports:** *the crashing window* (16:32–16:48) logged
**65 corrected + 3 fatal**; the int8 non-spilling arm logged **0 + 0** across 10 min of heavier,
*continuous* utilisation.

⚠ **Do not phrase the baseline as "the fp16 workload produced 65."** That 16-minute window contains
**three hard reboots and their recovery**, and device re-enumeration at boot plausibly generates
corrected AER events of its own. The per-minute clustering (31 @ 16:32, 31 @ 16:44, 3 @ 16:48) sits
right on the crash timestamps and is equally consistent with errors *preceding* the crash (fold
traffic escalating) or *following* it (reboot artifacts) — the log cannot separate those.
**"The crashing window logged 65" is defensible; "the fp16 workload produced 65" is not.** The
direction of the contrast is unaffected; its attribution is weaker than a raw reading suggests.

**⚠ CONFOUND — this does NOT yet establish causation.** The **NVIDIA driver was updated during this
session** (`595.71 / 32.0.15.9571` → **`596.72 / 32.0.15.9672`**), and PCIe link handling is driver
territory. Worse for attribution, the timing is adjacent: the last 6 corrected errors occurred at
**18:04 and 18:06** — plausibly the device reset from the driver installation itself — and **nothing
at all** afterwards. So the zero-event window begins essentially *at* the driver change. **Two
explanations remain live: (a) no spill ⇒ no escalation, or (b) the new driver fixed the link
handling.** The observed data cannot separate them.

---

#### Q1 CONTROL RESULTS (2026-07-19) — ⛔ **THE MECHANISM PREDICTION FAILED**

**Test:** sustained **fp16** (the spilling configuration), **new driver 596.72 held constant**,
Trop-2 ECD 248 aa, 5-minute window. Windows **recorded, not reconstructed** (harness gap fixed):
WHEA **18:44:41 → 18:52:12** strictly contains folds **18:45:31 → 18:51:39**.

| | int8 arm | **fp16 CONTROL arm** |
|---|---|---|
| Spilling | no — peak 5779 MiB | **yes — resident 8116 > 7043 free; peak 8544 > 8151 physical** |
| Duration | 600 s, 83 folds | **368 s, 5 folds** |
| Per-fold time | 7.2 s | **73–74 s** (10× penalty from thrashing) |
| mean pLDDT | 74.68 | 70.69 (matches the 70.7 fp16 baseline) |
| **WHEA corrected (Id 17)** | **0** | **0** |
| **WHEA fatal (Id 1)** | **0** | **0** |
| **Bugchecks** | **0** | **0** — host survived |

**The prediction was:** restoring spill should restore the corrected errors. **It did not.**
Continuous spill — a *larger* dose of the suspected trigger than the intermittent spill that
preceded three host bugchecks — produced **zero events of any severity**.

> ⚠ **Restated by F-001:** this arm's "zero corrected errors" reduces to **"no crash"**, which host
> survival already established independently. **The refutation below still stands — but on the
> fatal count, not the corrected count.** S-004 later strengthened it: HER2 crashed at int8 with
> **no spill at rest**, eliminating spill again by a different route.

**Therefore: the spill → PCIe-traffic → escalation mechanism is NOT SUPPORTED by this test.**
It moves from *predicted* to **tested and undermined** — not to *confirmed*. The leading explanation
for the cessation is now the **NVIDIA driver update (595.71 → 596.72)**, which is driver-side PCIe
link handling, exactly where such a fix would live.

**⚠ But "the driver fixed it" is NOT established either. Two limits:**
1. **The original crash condition was not reproduced.** All three bugchecks were on **HER2, 630 aa**.
   Both arms today used **Trop-2, 248 aa**. Sequence length changed *alongside* the driver, so this
   pair of runs cannot isolate the driver any more cleanly than it isolates spill.
2. **Weak power against a bursty fault.** Corrected errors historically appeared on **8 days out of
   ~54**, in clusters — most days logged zero. A 6-minute clean window is thin evidence of absence.
   *Absence of errors here is not evidence the fault is gone.*

**What this does and does not change:**
- **The S-003 int8 result stands entirely on its own merits** — it fits (5779 MiB peak), it is
  **10× faster** than fp16 under these conditions (7.2 s vs 73–74 s), and quality holds. None of
  that depended on the crash hypothesis.
- **The local tier looks better than feared** — ~16 minutes of combined sustained GPU load today
  with zero errors and no host loss — but that is *encouraging*, not *cleared*.
- **The decisive remaining test is HER2 (630 aa) under the new driver**, since that is the untested
  condition and the one that actually crashed. Under the **two-cap amendment** (D-009 §3) the
  sensible next run is **int8 + HER2**: it is simultaneously the *product* requirement (the flagship
  ADC target for the cache) and the *lower-risk* option (no spill), and a multi-minute fold at
  `chunk 16` would be a **PASS** for the cache path.

**Superseded:** the paragraph below was written before the control ran and predicted that errors
would return. Retained for provenance — it is the hypothesis this control tested and undermined.

**What was expected to close it — the fp16 sustained control** (now run, result above): hold the
**new driver constant**, restore **spill** by running sustained fp16, and see whether corrected
errors return. Errors return ⇒ spill is the mechanism (a). Still clean ⇒ the driver was the fix (b).
**Risk priced in:** sustained fp16 is *continuous* spill, a larger dose of the suspected trigger than
the intermittent spill of the HER2 folds that preceded the three crashes — **this experiment is
designed to reproduce the fault, so host loss is a likely outcome, not a surprise.** Mitigations:
**5-minute window rather than 10** (halves exposure, should discriminate as well), and the harness
writes per-fold JSON incrementally so a crash cannot destroy the record.

**Precondition deviations recorded (verified, not asserted):** free VRAM at start was **7899 MiB**,
not 8151 (8151 is *total*; 252 MiB reserved). GPU **compute** process list was empty (0 MiB) and
only our python held the GPU during the run — but **`ollama` and `ollama app` were running as
processes** throughout; they never claimed GPU memory, so they did not confound this arm.
HVCI/VBS confirmed still enabled (`VirtualizationBasedSecurityStatus = 2`, services `2,3,4`).

**Reliability floor (a design input, not a disqualifier).** The May 27 fatal happened in ordinary
use with no ESMFold involved. So **even a perfectly-fitting configuration will occasionally take
this machine down** — the floor is roughly *one host loss per several weeks of normal use*, and it
is now **measured rather than hypothetical**. This is precisely what D-009 §1's `jobs` table,
`claimed_at` + `worker_id`, `attempts`, and **30-minute stale-claim reaping** were designed for:
a worker that dies mid-job without warning. That design was written against an assumed unreliable
worker; it now has a number behind the assumption. **No redesign needed — the assumption was
right.**

**Named unknowns (not glossed):** what workload produced the 06-09 / 07-10 / 07-14 error bursts is
unknown; whether repair or replacement resolves it is unknown; whether a fitting configuration
drops the fatal rate to zero (versus merely reducing it) is **exactly what Q1 must measure**; the
minidumps remain unread.

**Provenance of this claim — it reversed direction twice, and the intermediate versions were
stated confidently and were wrong. A future reader should see the path, not just the destination:**

| Version | Source claimed | Conclusion | Why it was wrong |
|---|---|---|---|
| v1 | "read the minidumps" | GPU PCIe fault | **The minidumps were never read** — no admin, no debugger. The source was the Windows event log. |
| v2 | WHEA event **counts** (217 over 90 days) | "Pre-existing hardware, unrelated to our workload" | Counts were not bucketed by **severity**. 213 were *corrected*; only 4 were *fatal*. The fatal signature had zero prior occurrences. |
| v3 (current) | WHEA events **bucketed by severity**, plus all 4 bugcheck codes/params | Latent fault + workload accelerant; mechanism predicted, not measured | — |

**The failure mode both times was accepting a summary instead of returning to the raw data.**
`params_all_on_cuda=True` was a true summary that missed spill; "217 WHEA events since May" was a
true summary that missed severity. Each was caught only by re-deriving from the underlying records.

**⚠ Git history carries a superseded claim that cannot be rewritten.** PR #5 squash-merged as
commit **`5ad4c9b`** with the title:

> `docs: S-002 Q1 answered — GPU PCIe link fault (pre-existing hardware) (#5)`

That title was written **before** the correction, and its parenthetical **"(pre-existing hardware)"
is superseded by this entry** — the accurate reading is *latent pre-existing link weakness that this
workload accelerates*, per the provenance table above.

Two details matter for anyone auditing history:
- The squash **body** does contain all four constituent commit messages *including* the retractions,
  so a reader who opens the full commit sees the correction sequence. But **`git log --oneline`
  shows only the title**, and the body's *first* message also states the superseded
  "the fault predates the project / our load did not cause it" framing before later messages walk
  it back. History read top-down is therefore misleading in isolation.
- It **cannot be corrected in place**: `main` is branch-protected (D-008 — required `test` check,
  PR-only, `enforce_admins`), so rewriting history would require a force-push that protection
  forbids, and rewriting merged history would be the wrong remedy regardless.

**Authority rule: where commit metadata and this log disagree, THIS ENTRY WINS.** Commit titles are
not decision records; `docs/README.md` is.

**Adjacent audit (2026-07-19):** `git log -p --all -- .vscode/settings.json` confirms the file
existed in exactly two commits — added in `5ad4c9b`, removed in `a317a73` — and only ever contained
a 10-line `files.exclude` block (`.git`, `.svn`, `.hg`, `.DS_Store`, `Thumbs.db`, `.mule`).
**No credentials, tokens, or sensitive paths entered history.** No remediation required.

**Suggestive but NOT conclusive:** at idle the link reports `pcie.link.gen.current=1` (max 5) and
`width=8` (max 16). Consistent with AER-driven downtraining — **but confounded**, because NVIDIA
GPUs idle at low link speed for power management and some laptops are wired x8. Not offered as
proof; the 217 AER records are the solid evidence.

**Conclusions:**
1. **The local tier is NOT killed outright — it is conditional.** The mechanism in §3 above is what
   keeps it alive: if spill traffic mediates the escalation, then a configuration that fits in VRAM
   may not trigger the fault at all. **A resident-footprint fix is therefore not just an
   optimization — it is the candidate remedy**, and it must be measured before writing the tier
   off. (An earlier draft of this entry concluded "not viable regardless of the memory fix"; that
   inference was wrong — "a memory fix cannot repair a link" does not imply "a memory fix cannot
   avoid triggering it.")
2. **This is still also a platform problem.** Owner actions worth taking in parallel: update NVIDIA
   driver (595.71 current) and BIOS/EC firmware, and open a vendor support conversation — 148
   corrected PCIe AER errors over seven weeks plus a fatal on a machine this new is warranty
   territory. **Whether repair/replacement resolves it is UNKNOWN**; do not plan the project around
   that outcome either way.
3. **Project consequence — de-risk without abandoning.** Cache generation (D-009 §3 (A)) can move
   to **different compute** (cloud GPU / Colab / cluster) to remove the schedule dependency on
   both the hardware outcome *and* the Q1 result; a rented ≥16 GB GPU additionally makes the S-001
   fp16 non-fit stop binding, collapsing two problems into one. But this is **de-risking, not a
   verdict on the local tier** — Q1 may well restore it. Either way this stays **inside the
   D-004 §5 boundary** and is **not** a retreat to AlphaFold retrieval; D-003's graded DL claim is
   unaffected, since ESMFold still runs.
4. **Q2 (resident-footprint fix) is deferred, not cancelled** — whatever compute hosts the cache
   build still needs a configuration that fits, and the fp16-does-not-fit finding (S-001) travels
   with us to any 8 GB-class device. On a ≥16 GB device it may simply not bind.
5. **Minidumps remain unread** (need an elevated shell). Now low value — WHEA already identified
   the component. Only worth revisiting if the vendor asks for them.

### D-009 — Iteration 1 scope, job queue shape, and ECD boundary selection
- **Date:** 2026-07-19
- **Status:** **Accepted (2026-07-19)** — §1 and §2 accepted as originally logged; **§3 resolved
  by S-001 to (A) cache-first**, with the length cap explicitly left unmeasured. Note that
  Iteration-1 application work remains blocked, now on **S-002** rather than on §3: (A) is
  chosen but not executable until a folding configuration exists that fits and does not crash
  the host.
- **Context:** D-004 ratified the two-tier topology and carried three items forward: the
  job queue schema and claim mechanism, extracellular-domain boundary selection, and the
  Iteration-1 scope question (cache-first vs. live-first). The first two are resolvable
  from known constraints. The third depends on measured ESMFold performance on 8 GB VRAM,
  which does not yet exist. Per the log-leads-the-code rule, the resolvable parts are
  ratified here and the unresolved part is stubbed explicitly rather than guessed.

---

#### §1 — Job queue: dedicated `jobs` table (Accepted)

- **Decision:** Fold jobs live in a **dedicated `jobs` table**, not as additional columns
  on `protein_analyses`.
- **Rationale:** `protein_analyses` rows are durable scientific records; job state is
  transient operational state with retries, failures, and worker ownership. Merging them
  would (a) attach permanently-dead queue columns to every historical analysis, (b) make
  retry semantics awkward, since a retry is a new attempt against the same analysis, and
  (c) conflate "this analysis exists" with "this fold is in flight."
- **Shape (initial):**

  | Column | Type | Notes |
  |---|---|---|
  | `id` | SERIAL PK | |
  | `analysis_id` | INTEGER FK → `protein_analyses(id)` | the record this fold produces |
  | `status` | VARCHAR(20) | `pending` \| `claimed` \| `complete` \| `failed` |
  | `claimed_at` | TIMESTAMPTZ NULL | set at claim; used for stale-claim reaping |
  | `completed_at` | TIMESTAMPTZ NULL | |
  | `worker_id` | VARCHAR(64) NULL | which worker holds it |
  | `attempts` | INTEGER DEFAULT 0 | retry budget |
  | `error` | TEXT NULL | last failure message |
  | `inference_settings` | JSONB | dtype, `chunk_size`, model revision, sequence length — the reproducibility record (D-004) |
  | `created_at` | TIMESTAMPTZ | |

- **Claim mechanism:** `SELECT ... FOR UPDATE SKIP LOCKED` — the standard Postgres
  queue-claim pattern. Correct with a single worker and remains correct without change if
  a second worker is ever added.
- **Indexes:** `jobs(status, created_at)` for the claim query; `jobs(analysis_id)`.
- **Stale claims:** a `claimed` job older than a threshold (initially 30 min) is returned
  to `pending` and `attempts` incremented. Covers the laptop-sleeps-mid-fold case, which
  D-004 accepted as a normal operating condition rather than an error.
- **Deep-learning justification:** indirect but load-bearing — this is the mechanism that
  lets neural inference run on hardware that can actually hold the model. Without a
  durable queue, the local-GPU tier from D-004 is not viable and the graded DL work has
  nowhere to execute.

---

##### AMENDMENTS (2026-07-21) — settled while implementing §1 in PR A

The original §1 shape left three things underspecified. They surfaced when the queue
semantics were written as tests (log-leads-code checkpoint), and are settled here **before**
the implementing code. Each is expressed in code as an assertion of the chosen behaviour, so
a later change to any of them turns a test red rather than passing silently.

**Amendment 1 — retry budget is 3, then terminal `failed` with a distinguishable reason.**
§1 called `attempts` a "retry budget" but never stated the budget, so a job whose worker keeps
vanishing would be reaped and re-dispatched without limit. The cap is **3 attempts**
(`MAX_ATTEMPTS = 3`), derived from measured host behaviour, not a round number:

- The host reliability floor is roughly **one fatal bugcheck per several weeks** of ordinary
  use (S-002/F-001), independent of this project. A job must survive one host loss and still
  complete — one retry does that, two is comfortable margin.
- A **630 aa fold is 4-for-4 fatal** (S-004): a deterministic host-crasher. Every dispatch of
  such a job costs a host crash, so the cap must be low enough that a bad job cannot take the
  machine down repeatedly. Three attempts = the original dispatch plus **at most two
  retry-induced crashes** before the job stops asking.

  The two failure classes pull in opposite directions (survive transient loss vs. don't feed a
  deterministic crasher); 3 is the smallest cap that serves the first without over-serving the
  second.
- **The reaped-out terminal state must be distinguishable from an explicit failure.** Same
  `failed` status, but the `error` carries a machine-greppable marker (`[reaped-out] …`)
  stating the budget was exhausted with no error ever reported. A job that died three times
  without a worker ever reporting why is a different diagnostic situation, at 3 a.m., from one
  that reported a real exception — the record has to tell them apart.

  Mechanics: on each reap, `attempts` increments; if it reaches `MAX_ATTEMPTS` the job goes
  terminal `[reaped-out]` instead of returning to `pending`. So a persistently-vanishing job is
  dispatched at most 3 times.

**Amendment 2 — an explicit `fail` is terminal and does not touch `attempts`, and the
asymmetry with reaping is principled, not incidental.** An explicit fail means the worker
**caught its own error and survived to report it** — and a caught error is usually
deterministic (bad sequence, malformed input, OOM on an oversized target), so retrying
reproduces it. A stale reap means the worker **vanished** — usually environmental (sleep,
network, host bugcheck), where retrying is exactly right because absence is uninformative.
Therefore reaping retries and explicit failure does not: *reaping retries because absence tells
you nothing; explicit failure doesn't because the worker already told you what's wrong.* If
explicit failures were retried, an above-ceiling sequence would trigger three host crashes
instead of one.

  Consequence for the record, not just for retry semantics: `attempts` is **preserved, never
  zeroed**, on an explicit fail. A job reaped twice and then failing explicitly must read
  `attempts = 2` — that history is part of the diagnosis.

**Amendment 3 — FIFO is contract, stated, not inferred from an index.** §1 gave
`jobs(status, created_at)` as an index "for the claim query." An index makes an ordering cheap;
it does not guarantee one — a claim query with no explicit `ORDER BY` returns whatever the plan
yields, and that can change silently under a plan change. The claim query therefore **must
carry an explicit `ORDER BY created_at`** (with `id` as a deterministic tiebreak), and
oldest-pending-first is now a promised behaviour of `claim`, not a hopeful consequence of
index choice.

**Amendment 4 — the `analysis_id` FK is deferred, and what closes the gap is stated in
enforceable terms.** §1 specifies `analysis_id INTEGER FK → protein_analyses(id)`, but
`protein_analyses` does not exist and PR A is scoped to the queue. It is **not** created here.
The reason is not only PR size: a `protein_analyses` built now, in a queue PR, would be shaped
*for the FK's convenience* rather than from Database Plan v2's column-level decisions — and once
a table exists in an applied migration its shape is inertial, so the result would be a real FK
pointing at a wrong-for-the-wrong-reason table, then a later migration spent correcting it. A
named gap in a small PR is cheaper than a wrong table in the chain. The single-writer point also
holds: nothing enqueues jobs yet, so no code path can currently orphan an `analysis_id`.

So in PR A `jobs.analysis_id` is a **plain indexed integer with no FK constraint**.

- **Closure condition, in enforceable terms:** the migration that creates `protein_analyses`
  **adds the `analysis_id` FK constraint in that same migration**. Not "later," not "when
  convenient" — a deferred constraint with no stated closure is how a nominal integer becomes a
  permanent one.
- **Detectable, per the standing pattern:** `test_analysis_id_has_no_fk_yet` asserts the column
  currently carries no foreign key. When the FK lands, that test goes **red** and forces this
  amendment to be closed out deliberately rather than the gap being left open or silently
  half-satisfied — the same discipline as the `[reaped-out]` marker: name the transition and
  make it detectable.

**Seam note carried from D-012 §4, made sharper by these amendments.** The staleness *decision*
(`is_stale`) is pure arithmetic and is really covered. Amendments 1–3 make `complete`, `fail`,
and `reap_stale` (including the budget cap and the terminal-vs-requeue branch) **portable
status-transition logic** with no Postgres-specific construct — so they execute, for real,
against the SQLite test fixture. That shrinks the unproven surface to exactly one thing:
`claim`'s **atomicity** under `SELECT … FOR UPDATE SKIP LOCKED`. The seam stops being "where the
queue lives" and becomes specifically **where `SKIP LOCKED` lives** — the honest irreducible
minimum, provable only by the still-absent Postgres integration job (D-012 §5).

---

#### §2 — ECD boundary selection from UniProt topology (Accepted)

- **Decision:** For each target protein, fold **only the extracellular domain**, with
  boundaries taken from **UniProt's `Topological domain` feature annotations** where the
  description is `Extracellular`.
- **Method:** Query the UniProt REST API for the accession, read `features` of type
  `Topological domain`, select extracellular spans, slice the canonical sequence to that
  residue range, and submit only the slice to ESMFold.
- **Persistence:** store the selected range and its provenance on the analysis row
  (`metadata` JSONB: `ecd_start`, `ecd_end`, `ecd_source`) so the 3D viewer can label
  precisely what is being displayed, and so results are reproducible.
- **Fallback:** when no extracellular topological annotation exists, fall back to the full
  canonical sequence **and surface a visible warning in the UI** — the user should know
  they are looking at a whole-protein fold, which for a long target may fail the
  length cap. Absence of annotation is scientifically informative, not merely an error.
- **Multiple extracellular spans:** where a target has more than one, select the longest
  by default and record the choice; per-span selection is a later enhancement.
- **Deep-learning justification:** this is what makes the D-003 model choice tractable on
  D-004 hardware, and it is *scientifically* correct rather than merely convenient — ADC
  antibody binding occurs at the ECD, so the domain we fold is the domain that matters.
  Reference sizes: HER2 ECD ~630 aa, Trop-2 ECD ~250 aa, Nectin-4 ECD ~350 aa, against
  full lengths of 1255 / 323 / 510 aa respectively.

---

#### §3 — Iteration 1 scope — **RESOLVED 2026-07-19: (A) cache-first**

- **Status:** **Accepted.** Resolved by S-001. The pre-registered branch that fired was
  *"600 aa OOMs / won't load cleanly in fp16 → **(A) cache-first**, and escalate."*
- **Decision:** **(A) cache-first.** Iteration 1 ships the Mission Briefing plus the curated
  ADC target database served from cached PDB/pLDDT/PAE artifacts. User-submitted live folding
  is deferred. The demo does not depend on the laptop being awake — which, given three host
  bugchecks under load, is now a hard requirement rather than a convenience.
- **The length cap is deliberately NOT set.** D-009 §3 originally expected the cap to fall out
  of the bisection. It cannot: **no configuration ran clean**, and the 630 aa fold was never
  measured (3/3 host crashes). A cap derived from a spilling, crashing configuration would be
  fiction. **The cap stays unmeasured until a working configuration exists (S-002).**

---

##### STRUCTURAL AMENDMENT (2026-07-19): there are **TWO caps**, not one

**The problem this fixes:** D-006 and S-001 used a single sequence-length cap, and treated
**`chunk ≤16` as a FAIL** (*"severe chunking ⇒ ceiling below this length"*), alongside a
**`time < 120 s`** criterion. Those encoded an **interactive-latency assumption** — a user waiting
on a live fold cannot tolerate minutes, and heavy chunking means slow. **Cache-first (this section)
makes that assumption irrelevant for Iteration 1.** An offline cache build does not care whether a
fold takes four minutes; it runs unattended.

**Decision — split the cap into two numbers with two different criteria:**

| | **Interactive cap** | **Cache-build cap** |
|---|---|---|
| **Applies to** | live user-submitted folding (deferred to Iteration 1.5+) | offline pre-fold of the curated ADC target DB (**Iteration 1**) |
| **Bounded by** | **latency** — the user is waiting | **memory fit + host stability** only |
| **Criteria** | `chunk ≥ 32` **and** wall time `< 120 s` **and** no spill | **no spill** **and** host survives. Wall time is **not** a criterion. `chunk = 16` or `8` is **acceptable**. |
| **Status** | unmeasured | unmeasured |

**Consequence — read HER2 correctly when it is finally folded:** a HER2 ECD (630 aa) fold that
completes at `chunk 16` in four minutes without spilling is a **PASS for the cache path**, and
simultaneously a **FAIL for the interactive path**. Under the old single-cap criteria it would have
been recorded as a plain failure. **This is logged before HER2 runs precisely so the result is not
misread when it arrives.**

**Why this changes the product, not just the diagnosis:** it means the curated target database can
include **large ECDs that would never be viable interactively** — HER2 (630 aa) is the flagship ADC
target, and cache-first is what makes it reachable. The two-cap split converts a latency constraint
into a *scope* decision instead of an exclusion.

**Scoping note for D-006/S-001 criteria:** their `chunk ∈ {64,32}` and `time < 120 s` conditions are
hereby scoped to the **interactive** cap only. They were never valid criteria for the cache path.
- **The binding condition on (A) still applies** (from the original stub): cache-first does not
  weaken the graded DL content **only if the folding pipeline is real, committed, reproducible
  code in this repo** that produces the cache — not a one-off script. That condition is now
  *doubly* binding, because the cache is the only path to a demo.
- **Blocked downstream:** the cache cannot be built until S-002 yields a configuration that both
  fits and does not crash the host. **(A) is chosen, but not yet executable.**

*(Original stub text retained below for the record.)*

- **Status (superseded):** UNRESOLVED. This clause is deliberately incomplete. Iteration-1
  application work MUST NOT begin until it is filled in.
- **The fork:**
  - **(A) Cache-first.** Iteration 1 ships the Mission Briefing plus the curated ADC
    target database, folded offline by the real pipeline and served from cached
    PDB/pLDDT/PAE artifacts. The worker and `jobs` table exist and are exercised by the
    offline folding run, but user-submitted live folding is deferred to Iteration 1.5.
    Demo is independent of the laptop being awake.
  - **(B) Live-first.** Iteration 1 ships the full loop: user submits a sequence → job
    queues → local worker folds → result renders. More moving parts; demo depends on the
    inference tier being online at presentation time.
- **What decides it:** spike **S-001** (below). The threshold, set in advance so the
  result is not rationalized after the fact:
  - 600 aa fold completes in **under ~2 minutes** at acceptable peak VRAM → **(B) viable**
  - 600 aa fold takes materially longer, or OOMs at `chunk_size=32` in fp16 → **(A)**,
    and the length cap is revised downward to whatever 8 GB actually sustains.
- **Note on the DL claim under (A):** cache-first does not weaken the graded deep-learning
  content **provided the folding pipeline is real, committed, reproducible code in this
  repo** — invoked to produce the cache — and not a one-off script run once by hand. If
  (A) is chosen, that condition is binding.

---

#### Follow-ups
- Alembic migration for `jobs` (blocked on §3 only in timing, not in content).
- Worker credential handling — Fly secrets, referenced by name (Principle 4).
- Authenticated artifact-upload endpoint (D-004 consequence, still open).
- ARCHITECTURE.md §4 (data model) gains `jobs`; §6 Iteration-1 row updates once §3 resolves.

### S-001 — Spike: measure ESMFold fp16 performance on 8 GB Blackwell
- **Date:** 2026-07-19
- **Status:** **CLOSED 2026-07-19** — answer: **no, not in this configuration** (see RESULTS).
- **Type:** Spike (time-boxed investigation, not a feature). Produces a measurement and a
  decision input, not shipped functionality.
- **Question:** Does `facebook/esmfold_v1` in fp16 fold ADC-relevant extracellular domains
  on an 8 GB Blackwell laptop GPU, and how fast?
- **Method:**
  1. Load `esmfold_v1` with `torch_dtype=torch.float16` on the local GPU.
  2. Set `chunk_size=64`. Fold a ~300 aa sequence (Trop-2 ECD scale). Record peak VRAM
     (`torch.cuda.max_memory_allocated`) and wall time.
  3. Fold a ~600 aa sequence (HER2 ECD scale). Same measurements.
  4. If either OOMs, retry at `chunk_size=32` and record.
  5. If 600 aa OOMs at 32, bisect downward to find the actual sustainable ceiling.
- **Record:** peak VRAM and wall time per sequence length and chunk size; mean pLDDT of
  each output as a sanity check that fp16 has not degraded quality; model revision hash
  and torch version.
- **Decides:** D-009 §3 (cache-first vs. live-first) and the final API sequence-length cap
  in D-004.
- **Time box:** one afternoon. If the model will not load at all in fp16, stop and
  escalate — that invalidates the D-004 mitigation stack and D-003 needs revisiting.
- **Deliverable:** results appended to this entry, then D-009 §3 filled in and promoted
  to Accepted.

---

#### RESULTS (2026-07-19) — **Status: CLOSED.** Escalation branch fired.

**Reproducer pin (what actually ran):**

| Item | Value |
|---|---|
| torch | `2.11.0+cu128` (CUDA build 12.8) |
| transformers | `5.14.1` |
| model | `facebook/esmfold_v1`, revision **`75a3841ee059df2bf4d56688166c8fb459ddd97a`** |
| precision | `esm.half()` → fp16 LM trunk + fp32 folding trunk |
| GPU | NVIDIA RTX PRO 2000 Blackwell Laptop, capability sm_120 |
| **on-disk weights** | **9,581,481,414 B ≈ 9.58 GB** (`du`); the in-run tree walk reported 9.78 GB — Windows lacks symlink support so HF duplicates blobs into `snapshots/`. **Not the ~2.5 GB originally assumed.** Disk ≠ VRAM, but it is the worker's deployment footprint. |

**Unit correction (load-bearing, applies to every figure below):** `nvidia-smi` reports
**MiB**; torch reports **decimal GB**. `8151 MiB` = 8.55 GB decimal (≠ "8.15 GB").
All memory figures below are normalized to **MiB**.

**Memory — the model does not fit at rest:**

| Quantity | MiB |
|---|---|
| Physical VRAM | **8151** |
| Free at start (desktop using the rest) | 7043 (run 2/3); 7799 (run 1) |
| **Resident after fp16 load** | **8116** |
| Peak during 248 aa fold | **8545** |

`params_all_on_cuda = True` (all 4498 params on CUDA — no accelerate/`device_map` offload),
**but resident (8116) exceeds free VRAM (7043)**, so Windows WDDM silently spilled to shared
system RAM rather than raising OOM. Peak (8545) exceeds even *total* physical (8151).
**Conclusion: fp16 alone does not fit `esmfold_v1` in 8 GB.** The absence of an OOM is a
Windows artifact, not evidence of a fit; on Linux this would have raised `CUDA out of memory`.

**Load time — run 1's 631 s was WRONG as a load figure.** It was download-dominated. From a
warm cache, **load = 15–16 s** (runs 2 and 3, consistent). Relevant to D-004 worker design:
loading per job is cheap; holding resident is what does not fit.

**Folds actually measured:**

| Target | Len | Chunk | Time | Peak | mean pLDDT | Verdict |
|---|---|---|---|---|---|---|
| Trop-2/TACSTD2 ECD (23–274→27–274) | 248 | 64 | 48.8 s | 8545 MiB | 70.7 | **NOT-CLEAN — `vram-spill`** (run 1 logged `CLEAN` *before* spill detection existed; superseded) |
| **HER2/ERBB2 ECD (23–652)** | **630** | — | — | — | — | **NEVER MEASURED — host bugchecked, 3/3 attempts** |

**pLDDT scale trap fired for real:** raw B-factors came back on the **0–1 scale** and were
rescaled ×100 (`rescaled-x100(raw was 0-1 scale)`) to 70.7. Unrescaled, the guard would have
read 0.707 and wrongly flagged it as suspect/zero. The check is honest only because the
rescale is explicit.

**Host instability — the run never completed:** three attempts at the 630 aa fold, three
hard crashes, all with the **identical bugcheck `0x00020001` (HYPERVISOR_ERROR)**, byte-identical
parameters `(0x28, 0x1, 0x29b92701, 0xfc801000)`:

| # | Kernel-Power 41 (crash) | BugCheck 1001 (reboot) | Minidump |
|---|---|---|---|
| 1 | 2026-07-19 16:32:19 | 16:32:32 | `071926-18656-01.dmp` |
| 2 | 2026-07-19 16:44:28 | 16:44:44 | `071926-21093-01.dmp` |
| 3 | 2026-07-19 16:48:00 | 16:48:15 | `071926-20781-01.dmp` |

Identical signatures across three independent runs indicate a **reproducible fault**, not random
corruption. Whether it is a memory-pressure cascade (VRAM spill thrashing the WDDM/shared-memory
path) or an underlying hardware/driver problem is **not determined by this spike** → **S-002**.

**Decides:** D-009 §3 → **(A) cache-first** (the pre-registered "won't load cleanly in fp16 →
cache-first + escalate" branch). Length cap **remains unmeasured** — a cap cannot be set from a
configuration that never ran clean. D-004's mitigation stack is invalidated at rung one (amended
below). **The local inference tier's viability is now itself unproven** pending S-002.

### D-008 — Gate proven; branch protection required; paths-ignore removed
- **Date:** 2026-07-19
- **Status:** Accepted (supersedes the "doc-only commits bypass the test gate" clause of
  D-005 and the `paths-ignore` choice in D-007)
- **Context:** The CI gate (D-005/D-007) was only half a gate. `push: branches: [main]`
  makes the main-push run a **post-hoc check** — it runs on a commit *already on main*, so
  nothing is physically blocked; the keel run went green because the code was clean, not
  because a gate stood in the way. **The PR path is the real gate**, and it only blocks if
  `main` is *protected* and merging is the only route in. Proven empirically below.
- **Evidence (all on 2026-07-19):**
  - **Red gate on a PR:** PR #1 (`break-it`, deliberately broken assert) → gate run
    **`test` = failure, `deploy` = skipped** (`deploy: needs: test` did its job):
    https://github.com/mdk32366/Project-PharmFoldMDK/actions/runs/29706935765
  - **Advisory-only before protection:** PR #1 read `MERGEABLE / UNSTABLE` — a failing
    check did **not** block merge on its own.
  - **Blocking after protection:** same PR flipped to `MERGEABLE / BLOCKED` once `test`
    was required.
  - **Direct push refused:** `git push origin main` (empty commit) →
    `GH006: Protected branch update failed ... Changes must be made through a pull
    request ... Required status check "test" is expected.`
- **Decision:**
  1. **Branch protection on `main` is a hard prerequisite** and is now set: require a pull
     request (0 approvals), require the **`test`** status check, **`enforce_admins: true`**
     (no bypass — including the owner), no direct pushes. Direct pushes to `main` (like the
     keel commit `d656b63`, which predated protection) are no longer possible.
  2. **Remove `paths-ignore` from `gate.yml`.** With `test` now a *required* check, a
     doc-only PR that never triggered the workflow would leave the required check
     unreported and the PR **unmergeable forever**. Dropping `paths-ignore` makes the ~20s
     suite run on every PR, so the check always reports; docs pay a trivial always-green
     cost instead of deadlocking.
- **Deep-learning justification:** Neutral (process), but this is the difference between a
  gate that *looks* enforced and one that actually is — the guarantee that no untested
  inference code can reach prod now holds against a tired 11pm `git push origin main`.
- **Consequences / follow-ups:**
  - Doc-only commits now run the test suite (they pass trivially and are never blocked) —
    this is the accepted reversal of the earlier doc-bypass intent.
  - When the real Fly deploy replaces the placeholder, **guard the `deploy` job** (not the
    workflow trigger) against doc-only changes, so docs still run tests but don't redeploy.
  - `enforce_admins: true` means even the owner merges via PR with `test` green — by design.

### D-007 — Lay the keel: `tests/` + CI deploy gate scaffold
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** Realize the D-005 deploy gate as actual repo scaffolding **before** any
  application code exists, so the "no untested code to prod" discipline is in place from
  the first line of real code.
- **Decision:**
  - **`tests/`** with `conftest.py` exposing an **in-memory SQLite fixture** and one trivial
    passing smoke test. The fixture uses the **stdlib `sqlite3`** module (zero extra deps →
    CI green with only `pytest`); it will graduate to SQLAlchemy/SQLModel sessions when
    models land.
  - **`.github/workflows/gate.yml`**: `deploy` job `needs: test`; **native `paths-ignore`
    filter** (`**.md`, `docs/**`) so doc-only commits never trigger the workflow (that is
    how they "bypass the gate" per D-005). CI pins **Python 3.11**, `actions/checkout@v5`,
    `actions/setup-python@v6`.
  - The **`deploy` job is a placeholder** (echo) — real Fly deploy (flyctl + `FLY_API_TOKEN`)
    is wired in a later decision once the app exists. **No application code written.**
- **Deep-learning justification:** Neutral (scaffolding), but it stands up the gate that
  will protect the DL pipeline's correctness before any inference code can reach prod.
- **Consequences:** The SQLite fixture is stdlib-only for now; pgvector/Postgres paths still
  need the separate integration job flagged in D-005. Deploy is inert until wired.

### D-006 — ESMFold fold-path strategy for the 8 GB VRAM budget
- **Date:** 2026-07-19
- **Status:** ⚠ **INVALIDATED AT RUNG ONE (2026-07-19) by S-001 — REPLACEMENT RUNG ONE NOW MEASURED
  (S-003).** The ladder below assumes fp16 makes the model *fit at rest*; it does not
  (resident 8116 MiB vs 7043 MiB free). Rungs 2–6 reduce **activation** memory and cannot fix a
  **resident-weight** overrun. Do not implement this ladder as written.
  **New rung one (measured, S-003): quantize the ESM-2 LM trunk to int8 via `bitsandbytes`, leaving
  the folding head at full precision** → resident 5351 MiB, peak 5779 MiB, **no spill**, ~1.8×
  faster, pLDDT 74.7 vs 70.7 baseline. **Rung two: bf16** for the unquantized parts (same footprint
  as fp16, better numerical headroom, quality unchanged at +0.2). Chunking / length caps / ECD
  scoping remain valid as *activation*-memory rungs **below** these. Ladder retained verbatim below
  for the record; rewrite pending S-002 Q1 confirmation under sustained load.
  **⚠ ALSO RE-SCOPED (D-009 §3 two-cap amendment, 2026-07-19): this entry's `chunk ≥ 32` and
  `time < 120 s` conditions are INTERACTIVE-path criteria only.** They encoded a latency assumption
  that cache-first makes irrelevant. For the **offline cache build**, `chunk = 16` or `8` and a
  multi-minute fold are **acceptable**; the only criteria there are *no spill* and *host survives*.
- **Context:** The local inference GPU has **8 GB VRAM** (D-004). Full `esmfold_v1`
  (ESM-2 3B) wants ~16 GB+ for long sequences, so it will OOM on large proteins without a
  deliberate memory strategy. ADC targets are often large, but ADCs bind **cell-surface
  epitopes**, so the extracellular region is the scientifically relevant part to fold.
- **Decision — a layered strategy, applied in order:**
  1. **Half precision:** run the ESM-2 language-model trunk in fp16 on the GPU to roughly
     halve activation memory.
  2. **Axial-attention chunking:** set a `chunk_size` (start **128**, step down to 64/32 on
     OOM) to cap peak attention memory at a modest speed cost.
  3. **Extracellular-domain folding:** for a UniProt input, parse topology
     (`TRANSMEM` / `TOPO_DOM` features), extract the **extracellular domain(s)**, and fold
     those rather than the full chain — both ADC-appropriate and VRAM-friendly. If topology
     is unavailable, fall back to a length-capped full fold.
  4. **Interactive length cap:** the live "bring-your-own-sequence" path caps at
     **~400 residues** (starting value); longer inputs are routed to the offline pipeline
     or folded domain-only.
  5. **Graceful OOM degradation on the worker:** catch CUDA OOM → retry smaller
     `chunk_size` → **CPU-offload** the trunk (using the 31.5 GB system RAM, slow but
     completes) → else mark the job `needs_offline`.
  6. **Offline pre-compute pipeline:** a non-interactive worker mode folds the **curated
     ADC target database** ahead of time (CPU-offload allowed, no time pressure); results
     are cached as Volume artifacts + DB rows so the class demo path is always instant.
- **Deep-learning justification:** These are the model-execution decisions themselves —
  precision, attention chunking, and input truncation are standard neural-inference
  engineering, and folding the extracellular domain aligns the model's compute with the ADC
  biology. This is exactly the "how we actually run the deep model" reasoning the course
  expects, not an API wrapper.
- **Consequences / follow-ups:**
  - The 400-residue cap and `chunk_size=128` are **estimates**; measure real peak memory vs.
    sequence length on the 8 GB card and update this entry with the validated numbers.
  - Domain extraction needs a UniProt topology parser; proteins lacking topology annotation
    fall back to length-capped full folding.
  - fp16 may slightly reduce coordinate accuracy vs. fp32 — acceptable for exploration;
    note it in output caveats.
  - Adds an **offline pre-compute worker mode** to the `worker/` component (D-004).

### D-005 — CI/CD deploy gate + testing strategy (no untested code to prod)
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** Deployment to Fly.io must be rock-solid — **no untested code reaches prod.**
- **Decision:**
  - **GitHub Actions gate:** on PRs and pushes to `main`, run a `test` job; the Fly
    **deploy job runs only if tests pass** (`deploy: needs: [test]`).
  - **All tests live in `tests/`** (plural — matches the existing Test Plan and pytest
    convention; if you want the literal singular `test/`, say so and I'll rename).
  - **Two kinds of tests:** (1) **functional** — `pytest`, `*.py`, covering data layer,
    inference logic, API contracts (per Test Plan §A); (2) **user-based** — structured
    human scenarios (per Test Plan §B), run at iteration boundaries, gating iteration
    sign-off rather than each push.
  - **Test database is SQLite** (in-memory / temp file): fast, deterministic, no external
    DB in CI. All external calls — ESMFold inference, AlphaFold DB, UniProt — are mocked.
  - **Doc-only commits bypass the test gate:** a path filter treats changes limited to
    `docs/**`, `**/*.md`, `ARCHITECTURE.md`, `LICENSE`, etc. as non-code and skips the
    `test` job. Any change touching code runs the full gate.
- **Deep-learning justification:** Neutral (process), but it guards the DL pipeline's
  correctness — pLDDT/PAE parsing, fallback behavior, and the job-queue contract get
  tested before they can reach prod.
- **Consequences / known gaps:**
  - **SQLite ≠ Postgres/pgvector.** Vector search and Postgres-specific SQL cannot run on
    SQLite, so those paths must be mocked or covered by a **separate Postgres integration
    job** later (flag for Iteration 3). *(Same class of gap JARVIS hit: SQLite `create_all`
    never exercises real Postgres/migration behavior.)*
  - Deploy needs `FLY_API_TOKEN` in GitHub Actions secrets.
  - The local GPU worker (D-004) is out of the prod deploy path but its contract with the
    app (job schema, artifact upload) must be covered by functional tests.

### D-004 — Deployment & inference topology: Fly serving tier + local GPU worker (pull-based)
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** ESMFold (D-003) is GPU-heavy and Fly.io GPU is uncertain/expensive. The
  developer has a local machine with an **NVIDIA RTX PRO 2000 Blackwell Laptop GPU (8 GB
  VRAM)** and **31.5 GB system RAM**, and wants the app web-accessible but the model on
  local hardware.
- **Decision:** Split into two tiers.
  - **Serving tier — Fly.io:** Streamlit + FastAPI + Postgres/pgvector + Volume. Always-on,
    **no GPU**. Accepts analyses, stores data/artifacts, serves the UI.
  - **Inference tier — local machine:** a worker process running **ESMFold on the local
    NVIDIA GPU**.
  - **Coupling = pull-based job queue.** The web app enqueues an analysis job (a Postgres
    row, `status=pending`). The local worker **polls Fly over an authenticated outbound
    HTTPS connection**, claims pending jobs, folds, uploads artifacts (PDB / pLDDT / PAE)
    back to the Fly Volume, and sets `status=done|error`. **No inbound exposure of the home
    machine; no tunnel required.**
- **Deep-learning justification:** This is what makes running our own ESMFold feasible on a
  student budget — the neural inference runs on capable local hardware while the app stays
  web-accessible. The deep learning is still *ours*, executed by our worker.
- **Why pull-based over a tunnel (the ratified recommendation):** a laptop GPU sleeps,
  changes networks, and a fold takes seconds–minutes; pull-based tolerates intermittent
  connectivity, requeues on worker death/OOM, needs no open inbound port, and matches the
  async nature of folding. A synchronous tunnel (Tailscale/Cloudflare) would require the
  machine to be reachable and hold long HTTP requests open — kept only as a fallback.
- **Consequences / follow-ups (each becomes its own entry before we act):**
  - **8 GB VRAM is the binding constraint.** Full `esmfold_v1` (ESM-2 3B) wants ~16 GB+ for
    long sequences → OOM risk on large proteins. Mitigations to design: axial-attention
    `chunk_size`, a **live sequence-length cap**, folding only the **ADC-relevant
    extracellular domain**, and **pre-computing the curated ADC target DB offline** (can
    CPU-offload using the 31.5 GB system RAM and be patient).
  - **Availability:** if the local worker is offline, live jobs **queue** (no loss) but
    don't complete; pre-computed curated targets keep the class demo always-live.
  - **Worker plumbing needed:** an API token for the worker, job claim/lease semantics to
    avoid double-processing, and stale-job requeue on worker death (cf. JARVIS
    `recover_stale_jobs`).
  - **New repo component `worker/`** — runs locally, **not** deployed to Fly.

---

#### ⚠ AMENDMENT (2026-07-19, on S-001 results) — the mitigation stack is invalid at rung one

- **What broke.** The stack above (and its expansion in D-006) was ordered **fp16 → chunking →
  length cap → ECD scoping → caching**. Every rung *after the first* assumed the model **fits at
  rest** and that the remaining problem is activations. S-001 measured the opposite: the fp16
  model is resident at **8116 MiB against 7043 MiB free / 8151 MiB physical** — it spills to
  shared system RAM *before a single fold begins*. **fp16 alone does not get `esmfold_v1` into
  8 GB.** Chunking, caps, and ECD scoping all reduce *activation* memory; none of them reduce
  the *resident weight* footprint that is already over budget. The stack therefore needs
  **restructuring, not tuning**: the first rung must become a *resident-footprint* reduction.
- **Consequence for the topology.** D-004's two-tier design is not refuted, but the **local
  inference tier's viability is now unproven** — three attempts at a 630 aa fold ended in an
  identical host bugcheck (`0x00020001`). Whether the local GPU can sustain this work at all is
  **S-002**, and it gates the tier.
- **Bounded option space (restating §5 so the boundary is visible when the fix is picked).** A
  non-fit points to a **smaller/lighter folding configuration or narrower targets** — explicitly
  **NOT** a retreat to AlphaFold retrieval. Inside the boundary: **(a)** quantize the ESM-2
  trunk, **(b)** CPU-offload the language-model stack while keeping the folding head resident,
  **(c)** pair a smaller ESM-2 backbone with a folding head. Outside the boundary: making
  retrieval the deliverable (that would gut D-003's graded DL claim).
- **Reality check on (c):** `esmfold_v1` is the **only released ESMFold checkpoint**, so
  "just use a smaller variant" mostly is not a thing — (c) is a research project, not a config
  change. None of (a)/(b)/(c) is free and each needs its own measurement → **S-002**, not a
  guess made here.
- **Corrected worker input:** warm-cache load is **15–16 s**, not the 631 s recorded in run 1
  (that figure was download-dominated). Cheap loads make *load-per-job* viable, which matters
  precisely because *holding resident* is what does not fit.

### D-003 — Run ESMFold ourselves as the Iteration-1 deep-learning core
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** The course grade depends on a neural network doing load-bearing work
  (ARCHITECTURE §1). Structure prediction is the tool's foundational output, so it is the
  natural home for the graded DL. The two candidates were (a) run a protein-folding model
  ourselves vs. (b) retrieve pre-computed structures from AlphaFold DB with a smaller
  neural component elsewhere. Option (b) risks reading as "just an API wrapper."
- **Decision:** PharmFoldMDK will **run ESMFold in-project** to predict 3D structure
  directly from an amino-acid sequence. ESMFold (Meta AI) is a transformer stack: the
  ESM-2 protein language model produces residue representations that a folding head turns
  into 3D coordinates, **from a single sequence with no MSA required**. We load it via
  Hugging Face (`facebook/esmfold_v1`, `EsmForProteinFolding`) / PyTorch. It emits
  per-residue **pLDDT** and **PAE**, which map straight onto our data model
  (`protein_analyses.mean_plddt`, `pae_json_path`). AlphaFold DB / UniProt retrieval is
  demoted to an **optional fast path for already-solved canonical proteins and a
  fallback**, not the deliverable — ESMFold is what we run and defend.
- **Deep-learning justification:** This is the strongest available DL story: our system
  performs neural inference (a ~3B-parameter transformer language model + folding head) to
  produce the primary output. It gives us genuine DL substance to present and analyze —
  the ESM-2/transformer architecture, single-sequence inference vs. MSA-based AlphaFold2,
  pLDDT confidence calibration, and behavior on cancer-target variants that may not exist
  in AlphaFold DB. It also uniquely enables Iteration 2's **mutation impact** (fold the
  wild-type and the mutant and compare) — retrieval alone cannot fold an arbitrary mutant.
- **Consequences / follow-ups (each becomes its own decision entry before we act):**
  - **Compute & memory is the primary risk.** Full `esmfold_v1` is GPU-hungry
    (multi-GB weights; long sequences can exceed ~16 GB GPU RAM). Fly.io GPU availability
    is uncertain and the TDD flagged GPU deprecation. **Open D-00X:** where inference runs
    (in-process vs. dedicated worker/queue) and on what Fly compute (CPU-only tolerated for
    short sequences vs. GPU). Mitigations to evaluate: axial-attention `chunk_size`,
    sequence-length caps for the demo, and **pre-computing + caching** structures for the
    curated ADC target database so the live demo path is fast.
  - **Sequence-length limit** for the graded demo (ADC targets are often large; may fold
    only the extracellular domain relevant to ADC binding) — to be set in a later entry.
  - **Dockerfile / dependency weight** grows (torch, transformers, model weights); cold
    start includes model load — plan a warm-load path.
  - **Reproducibility:** pin the model revision and torch version; record device and any
    `chunk_size`/length settings with each analysis (course reproducibility expectation).
  - Updates `ARCHITECTURE.md` §3 (DL core ratified), §5 (compute now an active concern),
    and §6 (Iter-1 DL content confirmed).

### D-002 — Governance: living architecture doc + this decision log
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** The project must be maintainable and sustainable long-term, and its design
  rationale must be traceable for grading and for future work.
- **Decision:** Maintain `ARCHITECTURE.md` (repo root) as the single source of truth for
  system shape, updated in the same PR as any architectural change and brought current
  before any PR is filed. Maintain this `docs/README.md` as an append-at-top decision log
  where every design decision is written **before** its implementing work is finished.
  Both rules are encoded in `CLAUDE.md` so every working session is bound by them.
- **Deep-learning justification:** Neutral (process). Indirectly protects the DL mandate
  by forcing each decision to state where the deep learning is before code lands.
- **Consequences:** Slight up-front writing overhead per change; in exchange the project
  stays auditable and the DL story stays front-and-center.

### D-001 — Planning docs live in the repo under `docs/`
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** Planning docs (TDD v3, DB plan, UI plan, test plan, checklist, proposal)
  were sitting in a non-git sibling folder, unversioned.
- **Decision:** Moved all six into `docs/` with flattened filenames and committed
  (`6ea1e7e`). They are the reference intent; ratified changes are logged here.
- **Deep-learning justification:** Neutral (housekeeping).
- **Consequences:** Single versioned home for project intent; the `.docx` proposal is
  tracked as binary.

---

## Open questions awaiting a decision entry

These are known forks in the road. Each becomes a `D-NNN` entry **before** we act on it.

- ~~**DL core for Iteration 1**~~ — **resolved in D-003: run ESMFold ourselves.**
- ~~**Where inference runs + Fly compute**~~ — **resolved in D-004: local GPU worker,
  pull-based; Fly serving tier has no GPU.**
- ~~**Sequence-length cap / domain selection**~~ and ~~**pre-compute & cache pipeline**~~ —
  **resolved in D-006** (fp16 + `chunk_size` + extracellular-domain fold + 400-residue live
  cap + OOM degradation + offline pre-compute). Caps still need empirical validation.
- **Worker ↔ app contract:** job schema, claim/lease semantics, artifact upload, auth token.
- ~~**Prod DB choice**~~ — **resolved in D-012: Postgres-first**, from the first migration;
  the SQLite-on-Volume prototype path is closed, not deferred. The **test** DB remains SQLite
  per D-005, which D-012 §3–§5 turns from a footnote into a named, structural exposure.
- **Embedding model** for semantic search (which encoder, `vector(384)` assumed).
- ~~**Postgres integration test job**~~ — **BUILT in D-017.** The `postgres` CI job stands up a
  real Postgres 16 service container, applies migrations with `alembic upgrade head` (not
  `create_all`), and exercises `claim`'s `FOR UPDATE SKIP LOCKED` atomicity for the first time.
  What was "the single largest coverage hole" is closed. **Residual, narrower:** the job is not
  *yet* a branch-protection required check (owner action, deferred until proven stable — D-017),
  and pgvector **type resolution** through the `extensions` schema is still unexercised (no vector
  column yet; the job switches to a pgvector image when the first vector-column migration lands).
- **pgvector `extensions`-schema resolution** — a `vector(384)` column actually resolving via
  env.py's `search_path` seam, against a populated `extensions` schema, on real PG. Deferred to
  the first vector-column migration (D-017 residual; env.py seam already in place, D-012 §5a).
