# PASTE-READY — `F-051` — REISSUE of the entry previously pasted as `F-050`

**AUTHORED-SHA256** (range: **first `####` header → EOF**, anchored to line starts, no newline
normalisation) = `b59ee6c1c90fbe97baf391033c7d029bc0c35ee49fa45c4d5f88df61636e8133`
**bytes** = `5249`

> ⚠⚠ **THIS SUPERSEDES THE `F-050` PASTE. DO NOT LAND BOTH.** `RESERVED.md` holds `F-050` for the
> **guard-direction sweep**; the Planner's paste asserted the same integer for a different subject.
> **Owner ruling 2026-08-19: the RESERVATION WINS** — ⚠ *`RESERVED.md` is the register of legitimate
> claims and a Planner paste is not.*
>
> ⚠ **CONFIRM `F-051` IS FREE AGAINST THE LIVE LOG BEFORE MERGING.** The Planner is on `7011e24` and
> cannot see what has landed. **If it is taken, take the next free integer and report which.**
>
> **Landing this resolves the RED invariant** — `F-050` was cited by `D-079` amendment 1 ruling 4 and
> was unresolved for that content. ⚠ **Update that citation to the integer actually taken.**

---

#### F-051 — ⚠⚠ "The two confidence features" is really one: `membrane_proximal_plddt` carries 32.2% of attribution and `mean_plddt_ecd` 6.4%

- **Date:** 2026-08-19 · **Status:** ⚠ **OPEN.** An observation with a pre-registered fork —
  **not a conclusion and not a reinterpretation of `F-005`.**
- **How known (`D-016`):** read-only SQL as the `pharmfold-readonly` role against `target_scores` and
  `protein_features`, **run 2, 56 targets**. ⚠ **No fit, no refit, no new ranking run.** Instruments
  committed as `scripts/fd1_recover_coefficients.py` and `scripts/fd1_attribution_share.py` — **the
  numbers are re-derivable, not quoted.**

---

**THE MEASUREMENT.** Mean share of total absolute attribution across the 56 scored targets:

| feature | share |
|---|---|
| ⚠⚠ **`membrane_proximal_plddt`** | **32.2%** |
| `largest_patch_fraction` | **24.0%** |
| `radius_of_gyration` | 16.6% |
| `ecd_length` | 12.3% |
| `sasa_normalized` | 8.5% |
| ⚠ **`mean_plddt_ecd`** | **6.4%** |
| **the confidence pair together** | **38.6%** |

**`32.2 / 6.4 = 5.03` — a factor of five between the pair.**
**Per target: median 40.8% · max 72.5% · ⚠ 11 of 56 above 50%.**

**THE RECOVERY THIS RESTS ON IS EXACT, AND IT WAS CHECKED THREE WAYS.**
- **All 56 rows lie on one line per feature — max residual `~1e-16`.** Attributions are precisely
  `coefficient × standardized feature`, as `D-041` decision 1 documents.
- ⚠⚠ **The feature↔attribution PAIRING was tested, not inherited: all 6×6 combinations, diagonal
  `~1e-16`, every off-diagonal `~1e-1`.** **A transposed index would have produced six plausible
  slopes and an entirely wrong attribution story.**
- ⚠ **The fit population is confirmed as these 56**: the `FD1`-implied means agree with means computed
  directly from `protein_features` over the same 56 to **`≤6.9e-09`.**

⚠ **The intercept fell out of the same recovery — `-1.324660466`, implied identically by all 56 rows,
spread `1.11e-15`** — so **seven parameters are known on the raw scale and fully determine the
model's predictions.** ⚠⚠ **But NOT the standardized coefficients: `sd_k` is not persisted, and
computing it over the fit set would be fitting.** See `F-049` amendment 1.

---

**WHAT THIS ADDS TO `F-005`, AND WHAT IT DOES NOT.**
`F-005` measured **`FULL 0.607 / 8-of-12`** against **`no_plddt 0.562 / 6-of-12`** — two of six
features carry the difference. ⚠⚠ **This says the work inside that pair is done almost entirely by
ONE of them, and it is the MEMBRANE-PROXIMAL one.**
⚠ **`F-005`'s result is unchanged. Its READING is what this bears on, and the reading is `P-001`'s to
settle.**

**⚠⚠ THE FORK, PRE-REGISTERED HERE SO IT IS NOT CHOSEN AFTER THE FACT.**

**A — the circularity reading.** A dominant *global* confidence feature would suggest the score partly
tracks **how PDB-like a sequence is**; the PDB is enriched for studied proteins, which is enriched for
existing drug targets. ⚠ **The same circularity that bars GPI status and `therapeutic_precedent`,
through a side door.**

**B — the informative-uncertainty reading.** A dominant *membrane-proximal* confidence feature
suggests **ESMFold is uncertain near the membrane boundary, and that uncertainty is itself
informative about the region an ADC must reach.**

⚠⚠ **THE MEASUREMENT FAVOURS B AND DOES NOT ESTABLISH IT. The dominant feature is REGIONAL, not
global — which is what A would have predicted least.** ⚠ **`D-075`'s `geom_proxy` — `membrane_proximal_sasa`, the confidence-blind measure of the same region — is the instrument that
separates them, and `F-017` records it firing at `0.6607 / 0.6324 / 8-of-12`.** **Whether that
settles the fork is a `P-001` question and is not settled here.**

---

**⚠⚠ WHAT THIS ENTRY DOES NOT CLAIM. THE FIRST IS LOAD-BEARING.**
- ⚠⚠ **ATTRIBUTION SHARE IS NOT VARIANCE EXPLAINED.** The features are correlated — `D-075` records
  feature 7 against pLDDT at **Pearson −0.49, Spearman −0.55** — and the share decomposes **one linear
  predictor**, not causal contribution. **A 32.2% share is not a 32.2% causal role.** *(Code's
  caution, adopted verbatim.)*
- ⚠ **Not that `mean_plddt_ecd` is useless.** A small share in a correlated set is evidence about
  **this decomposition on these 56 targets**, not about no contribution.
- ⚠ **Not a proposal to change `FEATURE_NAMES`.** `D-027`'s six IS the pre-registration, the gate
  asserts `len == 6`, and **a feature dropped because its share looked small is a post-hoc model
  change** — what `D-041`'s pre-registration exists to prevent.
- ⚠ **Not generalisable past the cohort.** 56 targets, 12 labelled positives, an
  **expression-selected** cohort — `A-014` and `F-011` both apply to the label side.
- ⚠⚠ **Not a statement about the census.** No census row is scored (`D-089`), **and no census row
  carries a feature row at all** — 0 of 2,690.

**Assumptions relied on:** `A-014` — the cohort's labels descend from an expression screen.
**Relied on by:** ⚠ `P-001`, which must state the confidence dependence rather than let a reviewer
find it — **and which now has a sharper thing to state than *"two of six features are confidence."***
