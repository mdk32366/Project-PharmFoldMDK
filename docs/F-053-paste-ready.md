# PASTE-READY — `F-‹N›` — for `docs/README.md`

**AUTHORED-SHA256** (range: **first `####` header → EOF**, anchored to line starts, **SECOND
occurrence of the marker**) = `394da30e685a5ca09ce8316d5738a6674428f3c82b4dab17174392251550679e`
**bytes** = `5056`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE.** Landing header **above** the marker, outside the range.
> ⚠⚠ **THE INTEGER IS `‹N›` AND CODE DETERMINES IT.** **`F-053` was next free at `740465b` and
> entries have landed since; `F-050` remains RESERVED for the guard-direction sweep.** **Report the
> number taken and substitute it in the one self-reference below, declaring the byte delta.**
> **Three greps.**

---

#### F-‹N› — ⚠⚠ `CEILING_KNOWN_GOOD = 440` is a LENGTH; what actually binds is ~1.26 GiB of headroom against a 5.24 GiB resident model — and the guard, the climb and the preflight all measure the wrong axis

- **Date:** 2026-08-20 · **Status:** ⚠ **OPEN.** It closes when the fold path constrains on the
  quantity that binds, or states in itself which quantity it constrains on.
- **How known (`D-016`):** ten local int8 chunk-64 folds at the census recipe, spans chosen at evenly
  spaced ranks, on the RTX PRO 2000 (8.0 GiB, display holding ~1.1 GiB). **Measured, not modelled.**

---

**1 — THE MEASUREMENT.**

| span | time | peak VRAM | free after |
|---|---|---|---|
| **1 aa** | 13.7 s ⚠ *≈11.7 s of it loading 4,498 tensors* | **5.24 GiB** | 1.48 GiB |
| **439 aa** | 73.1 s | **6.50 GiB** | ⚠⚠ **0.03 GiB** |

⚠ **The Planner ordered ten folds describing this range as *"well inside `CEILING_KNOWN_GOOD = 440`."*
The first fold refuted the premise, and Code stopped rather than act on a belief the data had just
contradicted.** **0.03 GiB free of 8.0 is not *inside* anything.**

**2 — ⚠⚠ THE DECOMPOSITION, AND IT IS THE FINDING.**

**ESMFold stays RESIDENT between folds, by design — ~5.24 GiB.** **So the 6.50 GiB peak is
`resident model + fold`, and the INCREMENTAL cost of the largest census span is only ~1.26 GiB.**

⚠⚠ **`CEILING_KNOWN_GOOD = 440` encodes a LENGTH. The quantity that binds is MEMORY HEADROOM against
a resident model. They are different constraints and the log conflates them** — **one is a property
of the sequence, the other is a property of the card, the model AND a caching policy.**

**3 — ⚠ THE EVIDENCE IS THREE MIS-CALIBRATIONS IN ONE RUN, ALL BY THE SAME MECHANISM.**

**Code's guard was set at 6.9 GiB and blocked everything** — ⚠ **6.88 GiB is essentially the whole
card, and the 6.50 GiB peak had succeeded.** **Then it guarded TOTAL ALLOCATION rather than
HEADROOM.** **Then 1.6 GiB free against a fold that had already completed from 1.48.**

⚠⚠ **Code's own diagnosis, and it is the entry's thesis:** ***"My guard mis-calibrated three times
precisely because I kept reasoning about the length-shaped quantity instead of the memory-shaped
one."*** **The final threshold was grounded in a MEASURED SUCCESS rather than a fourth guess.**

**4 — ⚠⚠ WHAT ELSE MEASURES THE WRONG AXIS, AND THIS IS WHY IT LANDS BEFORE THE CLIMB.**

- **`vram_guard.preflight()` refuses on an unmeasured LENGTH** — ⚠ `refused_no_measurement`.
  **`F-049` established it is written, tested and consulted by nothing.** ⚠⚠ **So the guard nobody
  calls would also have guarded the wrong quantity if anybody had.**
- **`scripts/ceiling_climb.py` climbs the LENGTH axis to bracket `(440, 630)`.** ⚠⚠ **If the binding
  constraint is memory-shaped, the climb measures a proxy — and a proxy whose relationship to the
  real constraint depends on a policy nobody has recorded.**
- ⚠ **`D-082`'s blood line is a host bugcheck from over-allocation.** **A length-shaped guard cannot
  see an over-allocation that arrives by any other route.**

**5 — ⚠⚠ THE CONSEQUENCE FOR RENTAL, STATED AS A HYPOTHESIS AND NOT AS A CLAIM.**

**The model is resident BY POLICY, not by physics.** ⚠⚠ **Releasing it between folds would free
~5.24 GiB — roughly five times the incremental cost of the largest census fold measured.**

**So a named, UNMEASURED hypothesis: some part of the `441–629` band may be foldable LOCALLY if the
model is released and reloaded around large folds.** ⚠ **`FC` placed 3 of 6 recoverable positives in
exactly that band.**

**⚠ The cost side, so this is not read as free:** **reloading costs ≈11.7 s.** **Across 2,690 census
folds that is ~8.7 h of pure loading and is absurd. Across a handful of large folds against 75 s+
each, it is trivial.** ⚠⚠ **The policy is not one decision — it is a per-tier decision that nobody
has recorded as a decision at all.**

**⚠ NOT MEASURED, NOT CLAIMED, AND NOT A REASON TO SPEND OR NOT SPEND.** **It is a question the
rental ruling should be made in front of rather than behind.**

**6 — ⚠ What this entry does NOT claim.**
- **Not that `CEILING_KNOWN_GOOD = 440` is wrong.** ⚠ **It is a correct measurement of a length under
  an unrecorded policy** — *and that is precisely the problem: it is presented as a property of the
  hardware.*
- **Not that the climb is worthless** — ⚠ **only that its result is conditional on a caching policy
  that is not stated beside it.**
- ⚠⚠ **Not that any of the `441–629` band folds locally.** **n = 2 at the extremes and 10 in total is
  not a distribution**, and the incremental figure is one measurement at one span.
- **Not a proposal to change the caching policy.** *`D-074` decision 3: name the check, do not build
  the framework.*

**Relied on by:** ⚠ the rental ruling · `F-049` · and any future citation of `CEILING_KNOWN_GOOD`,
**which should carry *"a length, under a resident-model policy"* wherever it appears.**
