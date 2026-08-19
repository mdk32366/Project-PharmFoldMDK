# ORDERS — Code — `FD1` as arithmetic, and re-keying the rental population before anything is priced

**AUTHORED-SHA256** (range: **first `## §` header → EOF**, anchored to line starts, no newline
normalisation) = `457cb37807962260da7e3d77c7d8b185d8311f875f0ab2a2b6871d87ba286d6e`
**bytes** = `6794`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE. No landing header.**
>
> ⚠ Planner grounding `7011e24`. **No GPU, no rental, no fold. Tranche 5 HELD** (`D-091` r2).
> ⚠⚠ **READ-ONLY THROUGHOUT.** Nothing fitted, refitted, scored, rescored, ingested or folded.

---

## §0 — Accepted, and the near-miss is the item

**The reader is proven at the database with a control** — three write verbs refused by name, **and two
`SELECT`s returning 2,771**, because ⚠ *a role refusing everything would produce identical errors.*
**A proof with no positive case cannot tell success from total failure.**
⚠⚠ **2,771 is the truncation's own number, read back through a role that cannot repeat it.**

⚠ **The credential boundary was satisfied BY CONSTRUCTION** — `fly mpg users create … --role reader`
authenticating through the owner's token. **Better than the order asked: it removed the password
rather than protecting it.**

**⚠⚠ `fly-db` — the near-miss, and the rule that follows.** A privilege sweep with no `--database`
landed on Fly's sample tables and returned **a clean, well-formed, entirely correct answer about the
wrong object.** **Had the `TRUNCATE` proof run there, it would have "proven" the reader safe against
a database that is not ours.** ⚠ **Caught by reading table names, not by any check.**

**STANDING RULE, effective now: `--database` is ALWAYS EXPLICIT on every `fly mpg` invocation, never
defaulted.** ⚠ **Same defect as a missing `straddle` argument** — *a dial with a default that does not
announce itself* — and `§9` fixed that one with a `TypeError`. **`F-047` member 21.**

---

## §1 — ⚠⚠ Task JA — re-key the rental population. It is stale and we nearly priced it

**`FA2` found 26 rental-tier targets already folded AND scored. `D-041`'s *"29 rental-tier unfolded"*
predates that.** ⚠⚠ **`FC`'s bands — 13 in 441–629 with 3 positives, 16 at ≥630 with 3 positives —
were computed against the stale 29.** **We were about to price a purchase that has partly already
been made.**

**JA1 — ⚠ The CURRENT unfolded set, measured against the database, not against `D-041`.** **How many
cohort targets are unfolded today?** **State the key: which population, which filter, which column,
and what *folded* means in that column.**

**JA2 — Of those, how many are LABELLED and how many are Group B POSITIVES?** ⚠ **Against the current
12 scored positives, not against `D-040`'s ~22 across the 82** — **two different denominators and the
order names both so neither is assumed.**

**JA3 — ⚠⚠ Bucket them by the local ceiling: `≤440` · `441–629` (UNMEASURED) · `≥630`.** **Report
accession, gene and `span_aa` for each — the rows, not the counts.** *A count of ten is not ten rows.*

**JA4 — ⚠ Re-state `FC`'s answer against the CURRENT set and say plainly whether it moved.**
**If the recoverable positives in `441–629` are now fewer than 3, the ceiling climb's justification
weakens and the Planner's sequencing recommendation is wrong.** ⚠⚠ **Report it either way — a finding
that removes a reason to spend is worth as much as one that supplies it.**

**JA5 — ⚠ The 13 `no_span_measured` targets.** `FC` found `40 + 29 + 13 = 82`, and **that third
bucket is a category `D-041` never named.** **Are they still unmeasured? Why?** **An absence is a
category with a cause, and this one has never been given one.**

**JA6 — ⚠ And the 10 local-tier targets scored at run 2's counterpart — local but NOT scored.**
You correctly declined to say why. ⚠⚠ **Now ask the predicate directly: what does `D-064`'s
ranking-set membership require, and which of the ten fails it, and on what?** **Report per row. Ten
rows failing for one reason and ten failing for six reasons are different findings.**

## §2 — Task JB — `FD1`, as reproduction from persisted values

**`TargetScore.attributions` persists per-feature `β_k·x_k`. `protein_features` holds the raw `x_k`
and the reader can read it.** ⚠ **So `attribution_k(i) / x_k(i) = coef_k / sd_k` — a constant, over
every scored row.**

**JB1 — Recover the raw-scale slope per feature**, across the scored set.
⚠ **Raw scale ONLY. `sd_k` is not persisted, so the standardized coefficient — `D-041` decision 1's
attribution basis — is NOT recoverable.** **Do not reconstruct a standardizer to get it. That is
fitting, and it is barred.**

**JB2 — ⚠⚠ THE SELF-CHECK IS THE POINT, NOT THE COEFFICIENTS.** **All rows must yield the same slope
per feature.** **Report the spread** — min, max, and the count of rows agreeing to full precision.
⚠ **Any deviation is a finding**: about determinism, about drift between rows, or about attributions
not being what `core/scorer.py` documents them as.

**JB3 — ⚠ Report which run you read**, and read **one** run. **Runs 3 and 4 share a `scorer_version`
at 5 and 3 parameters** — **mixing rows across runs would produce a clean, stable, meaningless
slope.** ⚠⚠ **That is the exact defect this order exists to detect, committed while detecting it.**

**JB4 — Handle `x_k(i) = 0`**: the ratio is undefined there. ⚠ **Report those rows as a CATEGORY with
its count — never dropped silently, never coerced.** `F-020`: *an absent measurement coerced to zero
and fit as though measured.*

**JB5 — ⚠ Report the six slopes with their SIGNS**, and say which features push a target up and which
push it down. **Two of the six are pLDDT** — `mean_plddt_ecd` and `membrane_proximal_plddt` — and
the Planner needs the direction to write the paper's confidence section honestly.

## §3 — Task JC — two small things the reads exposed

**JC1 — ⚠ `DEP-005`'s recorded criterion is *"reports head (0002)"* and production is at
`0009_job_tier`, seven migrations on.** **A check whose expected value is stale passes wrongly or
fails wrongly, and either way it is not checking.** **Report where that criterion lives and what it
would take to make it version-agnostic.** ⚠ **Name it; do not build it** — `D-074` decision 3.

**JC2 — ⚠⚠ `run_kind='preregistered'` is carried by TWO runs**, `id=1` being `D-064`'s invalid run,
kept rather than overwritten. **Confirm that `/api/ranking`'s `valid ∧` half is the ONLY thing
separating them**, and report what a consumer reading `run_kind` alone would get. **This joins
`F-049` — a field that reads as an identifier and is not one.**

## §4 — ⚠ What is NOT ordered

**No fit, no refit, no new ranking run, no standardizer reconstruction.** **No ingest, no migration,
no fold, no rental.** **No credential rotation** — the owner's standing decision.
⚠⚠ **If any question here cannot be answered without fitting or writing, STOP AND REPORT.**

## §5 — Report

⚠ **`JA` first and separately** — it is the input to the rental conversation and everything else can
follow it.
Then branch and tip · **number and title of any entry landed, in the message that lands it** · the
invariant with its keys tested before any merge · the gate without `.env` sourced.
