# RESULT — 2026-08-06 — Run A (`--ablate geom_proxy`): the numbers, for F-017 to be drafted against

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority. Check the `### D-NNN` / `### F-NNN` header, not a reference to it.

> ⚠ **This file exists because the chat channel corrupted five times on 2026-08-06** — including one
> paste of the numbers below. **Continuity lives in the repository, never in the conversation**
> (KEEL Principle 8). `### F-017` is drafted against **this file**, not against the transcript.
>
> **Read by:** Code, from the live database, 2026-08-06. **Not Planner-verified** — the Planner has
> no database access. Every value here is re-readable from `ranking_run` id=5.

---

## §1 — Provenance

| | |
|---|---|
| Command | `python scripts/fit_scorer.py --run --ablate geom_proxy --persist` |
| Row written | `ranking_run` **id=5**, `run_kind='sensitivity'`, `scorer_version='5ccab48772b5'` |
| Status | `loo_status='complete'` · `fulldata_status='converged'` |
| Populations | `n_ranking_set=56` · `n_fit_positives=12` |
| Parameters | `geom_proxy` = `(0, 1, 4, 5, 6)` → 5 features + intercept = **6** |

---

## §2 — The twelve LOO percentiles, in run order, numbered

```
 1/12  0.4732142857142857
 2/12  0.9732142857142857
 3/12  0.4732142857142857
 4/12  0.6696428571428571
 5/12  0.4732142857142857
 6/12  0.6339285714285714
 7/12  0.6875
 8/12  0.9375
 9/12  0.6517857142857143
10/12  0.13392857142857142
11/12  0.7946428571428571
12/12  0.6875
```

**count 12 · median `0.6607142857142857` · mean `0.6324404761904762` · count ≥0.5 = `8`**

---

## §3 — The triple, three-against-three

| run | median | mean | count ≥0.5 | scorer_version |
|---|---|---|---|---|
| **`geom_proxy` id=5** | **0.6607** | **0.6324** | **8-of-12** | `5ccab48772b5` |
| FULL anchor id=2 | 0.6071 | 0.6176 | 8-of-12 | `91e646e4a289` |
| `no_plddt` baseline id=3 | 0.5625 | 0.5893 | 6-of-12 | `a927dc4532b7` |
| `plddt_only` id=4 — **not an anchor** | 0.6786 | 0.6295 | 9-of-12 | `a927dc4532b7` |

⚠ **id=4 is reported beside the triple and is not used by Decision 4.** It carries the highest median
and count of any run. *"The signal is geometric accessibility, not confidence"* is the fired row's
reading of the `geom_proxy`-vs-`no_plddt` comparison; **it is not a finding that confidence carries no
signal, and id=4 shows plainly that it does.**

⚠ **`0.6607 > 0.6071` is NOT reported as a finding.** Five features beating six at n=12 is noise-range
and Decision 4 has no row for it. The row says *toward FULL*; it does not say *better than*.

**Spearman id=5:** `+0.04828045495852675` — same magnitude as id=2 and id=3, opposite sign.
Per Decision 4 it **carries no weight in any cell** and is reported as evidence of nothing.

---

## §4 — Head-to-head: the 8 is **overlap**, not convergence

```
loo_status                     'complete'      → all twelve folds converged
headto_reference_n             12
headto_structural_percentiles  n = 8
structural  [0.292, 0.625, 0.292, 0.542, 0.792, 0.625, 0.042, 0.708]
evidence    [0.75,  0.75,  0.75,  0.75,  0.25,  0.25,  0.75,  0.25 ]
```

`core/scorer.py:514-517` loops over **converged** folds then applies
`if f.held_out_symbol not in common_symbols: continue`. With `loo=complete`, **no fold failed**, so the
12 → 8 reduction is membership in the evidence comparator — the governing order's *"8 overlapping
targets"*. **There is no contradiction between `complete` and `8`.**

⚠ **Reporting defect, not a result defect:** `scripts/fit_scorer.py:354` prints *"8 converged held-out
positives"* when the operative constraint is **overlap**. True, and it reads as a convergence count.
**One-line fix belongs in the wiring PR. Not touched.**

---

## §5 — Exclusions: 24 of 80, key stated

```
cohort of record        82   Kathad-2024-PLOSONE-S3-82
with protein_features   80   2 named exclusions never enqueued (D-026, 80/82)
ranking set             56
excluded                24   = 80 − 56
```

**24 of the 80 rows carrying `protein_features`** — not of 82, not of 56. Reasons: `held_out` and
`below_floor` throughout, plus `IGF2R: not_folded`. All 24 reported with a reason, none dropped.

---

## §6 — ⚠ The residual confound, MEASURED. It is not low.

```
n = 56 ranking-set rows, no nulls

feature 7  vs  feature 4  membrane_proximal_plddt    Pearson −0.4898   Spearman −0.5490
feature 7  vs  feature 3  mean_plddt_ecd             Pearson −0.6208   Spearman −0.4694

control:   feature 4      vs  feature 3              Pearson +0.7959   Spearman +0.7695
```

**Feature 7 is moderately-to-strongly correlated with both confidence features, negatively.** More
exposed membrane-proximal SASA goes with *lower* pLDDT there — the coordinate-mediated pathway,
in the predicted direction.

⚠ **Architectural blindness is proven; statistical independence is now measured FALSE.** `Atom`
carries no `b_factor`, `parse_pdb` never reads columns 60–66, and the §0.5 fixture reds on both arms —
the code cannot see pLDDT. But feature 7 is computed over coordinates ESMFold produced, so it
correlates with confidence **through the structure**, never through the B-factor column.

**The honest form:** feature 7 recovers the membrane-proximal signal **without reading confidence** —
not **free of confidence**.

⚠ **This did not and could not select which row fired.** Row 1 fired on the triple; this was measured
afterwards and constrains what the result *licenses*, not what it *was*.

⚠ **Scope of this figure:** measured on **the 56 ranking-set rows at one recipe composition**. It is a
property of this cohort as folded, **not a constant of the features**, and must not later be cited as
a general value.

---

## §7 — Post-state, against both pre-registrations

```
ranking_runs      (4,4) → (5,5)        ranking_results   4 → 5
target_scores     168 → 224  (+56)     protein_features  80 → 80  (0 written)
feature 7 non-null  79 → 79
```

**Anchors byte-unchanged:** id=2 `0.6071 / 0.6176 / 8-of-12` spearman `−0.04828045495852675` ·
id=3 `0.5625 / 0.5893 / 6-of-12` · id=4 `0.6786 / 0.6295 / 9-of-12`. **Nothing written to id=2.**

**Both cross-version checks cleared before the run** (no persist, no row targeted):
`no_plddt` reproduced id=3 exactly; **`preregistered` reproduced id=2 byte-identically, Spearman
included**, on rows now **seven** long where id=2 was fitted at **six**. Decision 4's FULL anchor is
commensurable with the ablation it is read against.

**No void condition fired.** Gate 481 passed before the run.

---

## §8 — Binding on F-017

1. **The fired row is quoted from `docs/README.md` §D-075 Decision (4) first**, before any prose.
2. F-017 **cites D-075 and F-004 and amends neither.**
3. **F-005 is refined, not reversed** — remove pLDDT and the signal drops (id=3 = 0.5625) remains
   true as recorded. What is new is that one confidence-blind membrane-proximal feature recovers it.
4. **D-075 Decision 6 gains two items:** the cohort's fold-recipe heterogeneity, **and** §6's
   coordinate-mediated correlation with its number and its scope caveat.
5. ⚠ **The snapshot disclosure binds** (`SPEC-2026-08-06-attention-proxy-snapshot-protocol.md` §3):
   Run A survived, so the attention proxies will be frozen **knowing** it survived. That sentence goes
   on the snapshot's face and into F-017 — **not softened, not in a footnote.**
