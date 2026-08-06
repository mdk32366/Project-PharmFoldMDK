# ORDERS — Code — 2026-08-06 — F-017, Decision 6, and the wiring PR

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority. Check the `### D-NNN` / `### F-NNN` header, not a reference to it.

## FIVE TASKS: 0, 1, 2, 3, 4.
**If this document does not end with the line `— END OF ORDERS (5 of 5) —`, it truncated. Report that and request re-delivery. Do not execute a partial order.**

---

> **⚠ WHY THIS IS A FILE AND NOT A PASTE.**
> Four consecutive reports in each direction have arrived corrupted — middle table columns eaten, sentences terminating mid-word, and on 2026-08-06 an order truncated at the same byte twice, taking its **authorisation limits and stop conditions** with it. The safety clauses were the part that fell off. **The channel is a measured hazard, not bad luck.** This document is delivered as a file for that reason. Reports back should avoid box-drawing tables — use `filename | field | field` on one line per row, which survives.

> **Planner provenance (D-016).** Written 2026-08-06 from the `4b7547c` snapshot read at first hand, plus Code's reports of the Run A session. **No GitHub connector. No `.git` in the archive. No database access.**
> **Every number attributed to production below is Code's reading, not the Planner's.** The one exception is the triple, which the Planner recomputed independently from the twelve LOO percentiles and which reproduces to full float precision.

---

## AUTHORISATION LIMITS — READ BEFORE ANYTHING ELSE

**This document authorises:**
- one read-only query against production (Task 0)
- edits to `docs/README.md`, `docs/RESERVED.md`
- one build PR touching `scripts/attention_control.py` and `scripts/fit_scorer.py` (Task 4)

**This document does NOT authorise:**
- ⚠ **Run B.** It is described in Task 4's context so the build has a target. **It is not authorised here and must not be run at the end of Task 4.** Run B needs the wiring PR merged, the snapshot frozen under the committed protocol, and a separate owner authorisation, in its own window.
- any further scorer run, ablation, refit, or `--persist`
- any migration, any fold, any write to `ranking_runs`, `ranking_results`, `target_scores`, or `protein_features`
- any edit to `ranking_run` id=2, id=3, id=4, or id=5

⚠ **id=5 is now a committed result. It is read-only on the same terms as id=2.**

⚠ **After Task 4 the obvious next command is Run B. That is close-out error 8 in a new location. Close the window.**

---

## STOP AND REPORT — do not work around

- Task 0's query returns anything other than a single Pearson coefficient over n=56 with no nulls
- any task appears to require inscribing a number the Planner has not seen and you have not read
- the `RESERVED.md` checker's output is anything other than `UNRESOLVED AND UNRESERVED: none — invariant holds`
- Task 1's entry would need to amend `### D-075`, `### F-004`, or `### F-005` to be coherent — **it must cite and amend nothing**
- the gate reds anywhere

---

# TASK 0 — The missing Pearson. Blocking Task 1.

The 2026-08-06 report delivered `feature 7 vs feature 4` **Spearman −0.5490** and lost the Pearson to channel corruption. The pair for feature 3 arrived intact (Pearson −0.6208 / Spearman −0.4694), as did the control (feature 4 vs feature 3, +0.7959 / +0.7695).

**Re-run and report the single missing value:** Pearson correlation, `membrane_proximal_sasa` (feature 7) against `membrane_proximal_plddt` (feature 4), over the **56 ranking-set rows**, no nulls.

Read-only. No write. Report the coefficient and the n.

⚠ **`### F-017` does not commit with a placeholder in it.** A half-reported correlation pair is exactly the shape that gets cited later as though complete.

---

# TASK 1 — `### F-017` into `docs/README.md`

Commit the entry below **verbatim**, with `[PENDING — TASK 0]` replaced by Task 0's measured value and nothing else changed.

Position it by the file's existing convention. It is the D-075 result and nothing else — per its reservation, the number was claimed twice in one morning and the census orders were corrected to yield it.

## BEGIN F-017 ENTRY — COMMIT VERBATIM

```markdown
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
| feature 7 vs feature 4 (`membrane_proximal_plddt`) | **[PENDING — TASK 0]** | **−0.5490** |
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
```

## END F-017 ENTRY

---

# TASK 2 — `### D-075` Decision 6 gains two items

Decision 6 is *"what this design still cannot separate, named up front."* Append **two** items. Do not renumber or reword existing items.

**Item — fold-recipe heterogeneity.** The cohort spans three recipes: `(int8, 64) × 42`, `(fp16, None) × 34`, `(fp16, 64) × 3`, one unrecorded. F-015 is untested at the cohort's actual variable (`None` vs `64`). ⚠ **No claim in either direction** — *"those 34 folds are fine"* is exactly as unsupported as the opposite.

**Item — the coordinate-mediated correlation.** Feature 7 is architecturally blind to pLDDT and **measurably correlated with it** (F-017): Pearson/Spearman against features 4 and 3 as recorded there. The pathway is the folded coordinates themselves, and this design cannot separate *"membrane-proximal geometry carries the signal"* from *"membrane-proximal geometry is a readout of the same thing confidence reads."*

⚠ **Wording requirement, and it comes from Code's flag:** state that these coefficients were **measured on the 56 ranking-set rows at one recipe composition** — a property of this cohort as folded, **not a constant of the features.** Write it so it cannot later be lifted as a general figure.

---

# TASK 3 — `docs/RESERVED.md`

Strike the **F-017** row in the established `~~**F-011**~~` style, with `✅ **WRITTEN 2026-08-06** — see \`### F-017\` in the log.`

Then run the checker verbatim. **Read the output, not the exit code.**

- Expected: `UNRESOLVED AND UNRESERVED: none — invariant holds`
- Reserved set: **15 → 14**
- ⚠ If `F-017` appears in `missing`, the strike-through broke the reserved regex while the entry is not being seen by `defined`. That is a real failure, not a formatting nit. Report the literal output either way.

---

# TASK 4 — The wiring PR

**Write your expected post-state before you build.** The Planner's is deliberately absent from this document — that ordering is the remedy for the F-022 defect you caught in #129, where a pre-registration and the instruction not to read it sat in one linear document. **Yours arrives first; the Planner's after.**

## 4a — Three-valued proxies. This is the substance of the task.

Wire the RCSB/UniProt and PubMed fetchers into `scripts/attention_control.py`'s existing injection seam. **Do not change the committed constants** — `PUBMED_QUERY_TEMPLATE`, `PUBMED_ENDPOINT`, `UNIPROT_ENDPOINT` are frozen and are the reason the protocol holds.

⚠ **THE DEFECT TO PREVENT, AND IT IS F-020 IN A NEW LOCATION.**

- `pub_count = 0` for a gene with no PubMed hits is a **legitimate measurement**. `pub_count = 0` because the query errored is an **absence**. **They are the same integer.**
- `pdb_present = False` is worse, because the coercion is invisible: an unavailable lookup becomes `False`, which reads as *"this protein has no deposited structure"* — **a positive claim about the world manufactured from a failed network call.**

⚠ **In the attention control this does not merely miscount — it moves the matching, which is the confound test itself.**

**Both proxies are three-valued: `measured` / `measured_zero` / `absent_with_reason`.** An absent value is a **CATEGORY** — never `0`, never `False`, never a bare null. **A target with an absent proxy is excluded from that proxy's matched analysis and named**, not defaulted into it.

**Prove it by revert, with the positive control alongside (A-017):**
- **(a)** assert the fixture reaches the code — a non-zero count of targets processed
- **(b)** one property, one test — `measured_zero` and `absent_with_reason` get separate tests, since a compound test proves only its first failing assertion
- **(c)** ⚠ **the fixture must contain a case where correct and incorrect differ**: a target whose true `pub_count` is 0, **and** a target whose lookup failed. **A fixture without both does not discriminate and this task is not done.**
- revert the three-valued handling; confirm red fires **at the assertion distinguishing the two**, not at a collection error and not at a case that reds either way (A-016).

## 4b — The snapshot writer

Implement `build_snapshot()` against the protocol committed at `73bca8f`. The snapshot records: source · endpoint constant · committed query template · resolved query per symbol · as-of date · **and Run A's fired Decision-4 row by name.**

**The as-of date is the date of the first successful pull. One pull. The first pull is the snapshot.** A failure is recorded with its timestamp on the snapshot itself and the retry is disclosed — **no silent second attempt, and no per-symbol re-query.**

⚠ **The disclosure goes on the snapshot's face, in the artifact, not in a commit message:** *the attention-control proxies were frozen after Run A's result was known; the protocol governing the pull was pre-registered before it.* **Not softened. Not a footnote.**

## 4c — The `:354` label

`scripts/fit_scorer.py:354` prints *"8 converged held-out positives"* where the operative constraint is **membership in the evidence comparator's overlap set**, not convergence. True, and it reads as a convergence count. Correct the label to name overlap.

⚠ **Do not assign this a finding number.** Three findings are queued for one free integer and taking a contested number under pressure is the F-017 double-claim, seen coming. It goes in the close-out unnumbered until the owner rules on F-024.

## 4d — Then stop

⚠ **Run B is not authorised by this document.** It requires this PR merged, the snapshot frozen, and a separate owner authorisation in its own window. **After 4b the obvious next command is the freeze, and after the freeze the obvious next command is Run B. Close the window.**

---

## REPORT BACK

Plain lines, one item per line. **No box-drawing tables** — they are what the channel eats.

1. Task 0's Pearson and its n
2. Task 1 committed — the hash, and confirmation that `### F-017` is seen by the checker's `defined` set
3. Task 2 — the two Decision 6 items as committed
4. Task 3 — the checker's literal output and the reserved set size
5. Task 4 — your pre-registration, the revert proof's exact red location, and the gate count before and after
6. Confirmation that `ranking_runs` is still **(5,5)** and nothing was written

---

## THE STANDING ITEMS THIS DOES NOT TOUCH

- **F-024 / findings numbering** — three queued, one integer, **owner ruling required**
- **#128 and #129** — unmerged, on their own merits, and ⚠ **not to be merged to make any forecast come true**
- **KEEL v7** — still uncommitted; the repository holds no KEEL document at any version while `KEEL-4` is cited 32 times
- **The census** — untouched. Migration 0008 does not exist and `protein_analyses` is still the cohort
- **Phase B** — gated on D-075, which has now fired; its shape follows from the row, not from the hope

— END OF ORDERS (5 of 5) —
