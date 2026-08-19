# ORDERS — Code — the scoring measurements, before rental is priced

**AUTHORED-SHA256** (range: **first `## §` header → EOF**, no newline normalisation) = `194d78c1835842a850cd42118f74a4c9560c6dbc1a22ca854e9831136df5c667`
**bytes** = `7291`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE.** ⚠ **No landing header** — it changes the bytes and breaks
> the hash. **Provenance goes in `SPEC-2026-08-19-landed-artifact-provenance.md`**, per your own
> ruling, which was right.
>
> ⚠⚠ **READ-ONLY. Nothing is fitted, refitted, scored, rescored or ingested under this order.**
> A refit is a decision with its own entry, and `D-041` / `D-060` fixed the fitting procedure
> **before** any fit existed. **Measuring the fit is not re-running it.**
>
> ⚠ Planner grounding `7011e24`. **No GPU, no rental, no fold. Tranche 5 HELD** (`D-091` r2).

---

## §0 — Why this exists, and one thing it already corrected

**The Planner opened a scoring conversation and asked whether the fitted scores are calibrated
probabilities or an ordering.** ⚠⚠ **`F-006` answered that on 2026-07-29** — *the fitted scores are
compressed toward the base rate, and are not calibrated probabilities*, **min 0.116 · median 0.220 ·
max 0.285 · count 56.** **The Planner reasoned from `D-041` and `core/features.py` and never searched
the findings.** **`F-047` member 14.**

**So this order asks only what the log does not already answer.** ⚠ **If any question below is
already answered by an existing entry, CITE IT AND DO NOT RE-DERIVE.** *That is the failure this
order was born from.*

---

## §1 — ⚠⚠ Task FA — the fit's denominators, which do not currently agree

**`D-041` records `40` targets `ranked ∧ folded`, with `29` rental-tier unfolded.
`F-006` counts `56` scored at `ranking_run_id = 2`. `D-040` records ~22 positives across the 82.**

⚠ **Three numbers, three keys, and no statement anywhere of how they reconcile.** *Every count states
its key.*

**FA1 — State the key on each of `40`, `56`, `22` and `82`**: which population, which filter, which
column, as of when. ⚠ **Say plainly which are superseded and which are current** — a superseded count
still sitting in an entry is a citation waiting to resolve wrongly.

**FA2 — ⚠⚠ Reconcile `40` against `56`.** They differ by 16 and both describe the scored cohort.
**Report the set difference, not the arithmetic** — which accessions are in one and not the other,
and why. **A difference of 16 explained by a sentence is not explained.**

**FA3 — How many of the `56` are LABELLED, and how many of those are POSITIVE?** ⚠ `F-006` records a
labelled fraction of **12 / 56**, against `D-040`'s ~22 positives across the 82. **Reconcile, both
directions.**

## §2 — ⚠ Task FB — has any fit run since `ranking_run_id = 2`?

**FB1 — Enumerate every ranking run**: id, date, `n` scored, `n` labelled, `n` positive, scorer
version, and ⚠ **whether it was pre-registered or exploratory.**

⚠⚠ **A pre-registered run is only pre-registered if later runs are distinguishable from it.** `F-006`
names run 2 as *the pre-registered run*. **If runs 3, 4, 5 exist and nothing marks the distinction,
the pre-registration is an assertion about a database column that may not carry it.**

**FB2 — Is `scorer_version()`'s output recorded on each run's rows?** ⚠ **If the coefficients moved
and the version string did not, two runs are comparable by appearance and not in fact.**

**FB3 — ⚠ Report whether `ranking_run_id = 2`'s coefficients are still reproducible today** — same
inputs, same procedure, byte-identical seven parameters. **`D-041` says they should be. Do not assume
it; run it and report the numbers.**

## §3 — ⚠⚠ Task FC — THE ONE THAT PRICES RENTAL. What does a rental fold buy the FIT?

**`D-041`: `29` rental-tier targets are unfolded. Rental spend has been discussed only as census
coverage. It is also statistical power.**

**FC1 — Of the 29, HOW MANY ARE LABELLED, and how many of those are POSITIVE?** ⚠⚠ **This is the
number the rental conversation cannot proceed without.** With ~22 positives against 7 parameters —
**~3 positives per parameter** — **every labelled positive recovered from the 29 is a material change
to the fit's power, and every unlabelled one is a scored row and nothing more.**

**FC2 — Report the 29 individually**: accession, gene, `span_aa`, labelled?, positive?, ⚠ **and which
side of the local ceiling each sits on.** `CEILING_KNOWN_GOOD = 440`; the **441–629 band is
unmeasured**. **Bucket them: ≤440 · 441–629 · ≥630.**

⚠⚠ **FC2 decides whether climbing the ceiling is worth anything.** **If most of the 29 sit above 630,
a higher local ceiling buys nothing and the money goes to rental regardless. If they cluster in
441–629, the climb is the cheapest thing on the board.** *Neither of us should guess this.*

**FC3 — ⚠ Is a refit on a larger `n` PRE-COMMITTED anywhere, or would it be a new decision?**
**Search `D-041`, `D-060`, `D-065`, `D-075` and report what you find, quoted.** ⚠⚠ **If nothing
pre-commits it, a refit after seeing that the first fit was thin is a post-hoc decision** — and
`F-022`'s discipline says that is ruled **before** the data arrives, not after.

## §4 — Task FD — the two pLDDT features, measured rather than argued

**Two of the six pre-registered features are confidence outputs**: `mean_plddt_ecd` and
`membrane_proximal_plddt`. ⚠ **One third of the feature vector is the model's self-assessment rather
than a geometric measurement.**

**FD1 — Report run 2's six standardized coefficients with their signs**, and ⚠ **the share of
attribution carried by the two pLDDT features** — `D-041` decision 1 makes coefficients on
standardized features the attribution basis, so this is reading the fit, not reinterpreting it.

**FD2 — ⚠ Report `D-065`'s sensitivity result as it stands**: the scorer supports **6, 4 or 2**
coefficients dynamically. **What happened to the ranking under each?** **Cite the entry; do not
re-run it if it is already recorded.**

**FD3 — ⚠⚠ Report `D-075` Run A's `geom_proxy` outcome, verbatim from the entry**, together with
`F-020`'s correction — *an absent measurement coerced to zero and fit as though measured*. **The
Planner needs the entry's own words, not a summary**, because the paper's framing turns on whether
that ablation is written as a **limitation** or as a **control**.

## §5 — ⚠ Task FE — the fit population is not the scoring population

**The scorer is fitted on tens of targets and applied to 2,690 census rows.**

**FE1 — State both populations and their keys**, side by side, with the ratio.
**FE2 — ⚠⚠ Are census rows scored at all, or only cohort rows?** `D-089` rules *a page per census
protein, **deliberately without a scorer panel***, and `Q9ULH0` served `scored=False`. **Report how
many of the 2,690 carry a score, and under which run.**
**FE3 — ⚠ If any census row carries a score, report how the surface labels it**, because a score from
a model fitted on an expression-selected cohort, applied to a surfaceome-wide population, is
`A-014` and `F-011` at once — **the training labels are an upstream screen's positive class, which is
a prediction and not a fact.**

---

## §6 — What this order does NOT authorise

⚠ **No refit. No new ranking run. No change to `FEATURE_NAMES` — the gate asserts `len == 6` and
`D-027`'s six IS the pre-registration.** ⚠ **No promotion of `membrane_proximal_sasa` out of
`EXTENDED_FEATURE_NAMES`** — `D-075` decision 5 keeps the graded path at six features and seven
parameters, and feature 7 exists only for the named ablation.

⚠⚠ **If any question here cannot be answered without fitting something, STOP AND REPORT.** **That is
the boundary, and a scope denial is stop-and-report — never a retry, never a workaround.**

## §7 — Report

⚠ **Answers only — no entry, no integer.** The Planner writes what the log needs after reading them.
Plus branch and tip, the invariant with its keys tested before any merge, and the gate without
`.env` sourced.
