# ORDERS — Code — does PAE disagree with pLDDT on the 79, and what does refolding 2,690 locally cost?

**AUTHORED-SHA256** (range: **first `## §` header → EOF**, anchored to line starts, **SECOND
occurrence of the marker**) = `6b356de812b79b078507af704b51b8dc28e38a4fa6ed1825aa9372cc4e4f4e77`
**bytes** = `4812`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE.** Landing header **above** the first `## §` marker,
> **outside the hash range.**
>
> ⚠⚠ **§1 IS READ-ONLY AND NEEDS NO GPU. §2 IS TEN FOLDS AND NEEDS THE LOCAL CARD.** **Nothing else
> folds. No rental, no refit, no new ranking run, no ingest.** **Tranche 5 HELD** — `D-091` r2.
>
> ⚠ Grounding `b06d378`. **`F-042` is OPEN and nothing here closes it.**

---

## §0 — What this decides, pre-registered before either number exists

**§1 decides whether `P-006` has a paper in it.** **§2 decides `F-042`'s remediation path.**
⚠ **They are independent and §1 needs no card, so run §1 first.**

**⚠⚠ THE PLANNER'S EXPECTATION, RECORDED SO IT CANNOT BE ADJUSTED AFTERWARDS: I expect at least a
handful of the 79 to show high mean pLDDT with poor inter-domain PAE, and I expect the effect to be
strongest on the LONGEST, most multi-domain targets.** ⚠ **If pLDDT and PAE agree everywhere, `P-006`
dies cheaply and this sentence is the evidence the result was not fitted to.**

**⚠ And the cost framing, corrected before it propagates: the census span range is 1–439 aa and
`CEILING_KNOWN_GOOD` is 440, so EVERY CENSUS FOLD IS LOCAL.** **`F-042`'s remediation is card time,
not rental money, and does not compete with the rental budget.**

---

## §1 — ⚠⚠ Task SA — where do pLDDT and PAE disagree on the 79?

**`pae_json_path` is set on 79 of 80 cohort rows. Read-only, as the reader role.**

**SA1 — ⚠ First, characterise what is actually stored.** Matrix dimensions per row, units, and
⚠⚠ **whether the matrix is symmetric or directional** — *PAE is the error in residue `j`'s position
when the prediction is aligned on residue `i`, and it is NOT symmetric.* **Report which convention
the stored matrix uses.** ⚠ **Do not average across the diagonal until that is established.**

**SA2 — ⚠ Report the ONE row of 80 that lacks it, with its cause.** **An absence is a category with a
cause, never a low number.**

**SA3 — Derive a per-target inter-domain PAE summary**, and ⚠⚠ **report the rule you used, in full.**
**A summary statistic over a matrix has many defensible definitions** — mean off-diagonal, mean
between domain blocks, worst domain pair. ⚠ **Report at THREE definitions, not one.** *A single
setting is a dial wearing the costume of a measurement.*
⚠ **Domain blocks come from the same `Domain`/`Repeat` intervals `D-095` uses** — **reuse, do not
re-derive.** **Targets with fewer than two domains have no inter-domain quantity: report them as a
named category, not as zero.**

**SA4 — ⚠⚠ THE MEASUREMENT: rank the 79 by `mean_plddt_ecd` and by each inter-domain PAE summary, and
report the DISAGREEMENT.** Spearman between them, **and — more usefully — the targets in the top
quartile by pLDDT and the bottom quartile by PAE.** ⚠ **Name them. A count is not the finding; the
rows are.**

**SA5 — ⚠ Report whether disagreement tracks span length and domain count.** **If the effect is
confined to long multi-domain targets, that is the paper's population and it must be stated as a
scope bound, not discovered later.**

**SA6 — ⚠⚠ If pLDDT and PAE agree everywhere, SAY SO PLAINLY AND STOP.** **That kills `P-006` and it
is a good outcome measured cheaply.** **Do not go looking for a third statistic that disagrees.**

## §2 — Task SB — what does refolding the census locally cost?

**SB1 — Time TEN census folds at the exact census recipe — int8, chunk 64, local** — ⚠ **chosen at
evenly spaced RANKS of span length, not the first ten.** *The extraction run measured a 708× spread
between shortest and longest; folding will not be uniform either.*

**SB2 — Report seconds per fold, the spread, and the projected wall clock for 2,690.** ⚠ **Projection
and measurement both, as `LA2` did — *projected 0.71 h → measured 38.0 min* is how a projection earns
trust.**

**SB3 — ⚠⚠ Confirm PAE is EMITTED AND PERSISTED on those ten.** **`D-099` established emission at 25
of 25; this establishes whether the persistence path repair works.** ⚠ **If PAE is emitted and still
not persisted, STOP AND REPORT — that is a different defect from the one `F-042` names.**

**SB4 — ⚠ Report VRAM headroom observed across the ten**, and whether any approached the ceiling.
⚠⚠ **`vram_guard.preflight` is written, tested and consulted by nothing (`F-049`), and `D-082`'s
blood line is a host bugcheck.** **Ten folds at ≤439 aa is well inside `CEILING_KNOWN_GOOD = 440`, so
this is not the climb — but report the numbers, because they are free and nobody has them.**

## §3 — ⚠ Not ordered

**No refold of the 2,690.** **No `preflight` wiring** — that is a decision and it gates the climb.
**No rental, no refit, no ranking run, no census scoring, no `P-006` registration.**
⚠⚠ **If §1 cannot be answered without a fold, or §2 without a rental card, STOP AND REPORT.**

## §4 — Report

⚠ **`SA4` and `SA6` first — they decide whether `P-006` exists.** Then `SA1`'s convention · `SA3`'s
three definitions · `SB2`'s projection against measurement · `SB3` · branch and tip · both invariants
with their keys · the gate without `.env`.
