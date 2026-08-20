# PASTE-READY — `D-095 amendment 2` — for `docs/README.md`

**AUTHORED-SHA256** (range: **first `####` header → EOF**, anchored to line starts, **SECOND
occurrence of the marker**) = `cca0ec74804a771735e58ce63720f8cb4d0e2c2c7b58c25604887c1c29292c79`
**bytes** = `5622`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE. No landing header.** Sub-entry — **no integer** — after
> `#### D-095 amendment 1`. **Three greps.**
>
> ⚠⚠ **THIS CLEARS ONE OF THE TWO REMAINING DANGLING AMENDMENT REFERENCES** found by `MB3`
> (`CLOSEOUT-2026-08-19:157`, `PREWORK-2026-08-20:106`). **Re-run the amendment invariant after
> landing and report it.**
>
> ⚠ **§2 IS AN OWNER RULING**, as the fourth `tile_cut_kind` value was. **Confirmed 2026-08-20.**

---

#### D-095 amendment 2 — ⚠⚠ Ten rows have NO LEGAL CUT SITE, tiling is mandatory for all of them, and amendment 1 discharged the design gate with that hole in it

- **Date:** 2026-08-20 · **Status:** **RULED.** ⚠ §2 confirmed by the owner, 2026-08-20.
- **Amends:** `D-095 amendment 1`, which moved `D-095` PROPOSED → RULED and discharged
  `D-091 (tranche 6 design gate)` ruling 3.

---

**1 — ⚠⚠ THE HOLE, AND IT WAS SHIPPED INSIDE THE AMENDMENT THAT CLOSED THE GATE.**

`D-095` decision 2 defines `tile_cut_kind ∈ {gap, domain_boundary, span_end}`, and amendment 1 added
a fourth, **`run_interior`**.

**Ten of the 141 carry NO `Domain` or `Repeat` anywhere in the UniProt entry** — cause
`no_domainlike_features_in_the_chain`, **10 of 10, a single cause, established at `U5`/`Y2` as a
GENUINE ABSENCE OF ANNOTATION rather than a rejection.**

⚠⚠ **So they have no gap, no domain boundary, and no run interior. Under the current vocabulary
there is NO LEGAL CUT SITE** — and **every one exceeds the 1,026 trained context, so tiling is
MANDATORY REGARDLESS OF HARDWARE**, because the trained context is a property of the **model**, not
of the card. ⚠ **Under `D-094` cut legibility is a MOUNT PRECONDITION: these ten cannot mount.**

⚠⚠ **Amendment 1's headline decomposition was 125 tile at gaps · 10 have nothing to tile at · 6 need
one `run_interior` cut. The middle term was printed and its consequence was not seen.** **A category
with a count and no ruling — one week after the engulfing category was exactly that, and the Planner
wrote both.**

**2 — ⚠⚠ RULING (owner, 2026-08-20): a FIFTH `tile_cut_kind` value, `unannotated_interior`.**

- **`unannotated_interior` DISCLOSES the cut as ARBITRARY rather than disguising it as a seam.**
  ⚠⚠ **The alternative is not "a better cut" — no better cut exists, because there is no annotation
  to place one.** **The choice is between an arbitrary cut that SAYS SO and an arbitrary cut wearing
  the name of a boundary.**
- ⚠ **Under `D-094` its disclosure is a MOUNT PRECONDITION**, identically to `run_interior` — **the
  cut is legible from the artifact alone or the row does not mount.**
- **THE OFFSET RULE IS A RECORDED PARAMETER, NOT A DEFAULT.** ⚠⚠ **`tile_offset_rule` is written on
  every affected artifact beside `merge_rule`, its gap tolerance, and `straddle_handling`** — *three
  unstated parameters were found on one derived object in two days; a fourth will not be added
  silently.* **A default that does not announce itself is the defect `straddle`'s `TypeError`
  closed.**

**⚠ THE COUNTERFACTUAL, STATED SO THE RULING IS A CHOICE AND NOT A DRIFT — HOLD THE TEN.**
**Weighed and rejected.** ⚠ The case for holding was real and is recorded: **a 1,500-residue span cut
blindly into two 750-residue tiles can produce two structures that are individually confident and
jointly meaningless**, and **the absence of any domain annotation may itself be informative** —
poorly characterised, disordered, or genuinely unusual proteins. **We would be risking
plausible-looking output on exactly the rows least able to warn us.**

**⚠⚠ THE OWNER'S REASONING, AND IT IS WHY A BEATS B RATHER THAN MERELY DIFFERING FROM IT:** *"if the
worst happens and there are ten 3K residue spans, then we'll figure it out again at that point with a
smaller batch of proteins remaining."*

⚠⚠ **THE LABEL IS WHAT MAKES THAT LATER DECISION POSSIBLE.** **Under `D-094`, `unannotated_interior`
renders on every affected tile — so if the ten turn out to need four blind cuts each, the artifact
SAYS SO on its face and the re-decision is made against rendered evidence.** **Holding them would
have deferred the identical question to a later date with NO ARTIFACT TO LOOK AT.** ⚠ **A rule that
fires and produces a labelled bad outcome beats no rule, because the label is what makes the outcome
visible.**

**3 — ⚠⚠ THE TEN ARE COUNTED AND NOT ENUMERATED. THAT IS AN OUTSTANDING MEASUREMENT, NAMED HERE.**

`docs/README.md:1064` and `MEASUREMENT-OUTPUT-2026-08-19-tranche6-straddle-rules.txt:86` both give
**10**. ⚠ **`BC2` ordered accession, gene and `span_aa` per row and it has not reported.**
**`BC3` ordered the tile count for each at THREE values of `tile_max_aa` — 440, 630, 1,026 — and it
has not reported.**

⚠⚠ **A count of ten is not ten rows**, and this entry does not pretend to know which they are.
**The enumeration lands as evidence beneath this amendment when it exists; the ruling does not wait
on it, because the vocabulary gap is established by the count alone.**

**4 — ⚠ What this does NOT do.**
- ⚠⚠ **It does not widen the boundary source.** `D-095` decision 1(b) rules `Domain` + `Repeat`, and
  **adding a feature type to give these ten something to cut at would be changing the instrument to
  suit the result.**
- **It does not authorise folding anything.** ⚠ **Tranche 5's 776 rows remain held by `D-091` ruling
  2 — RENTAL SPEND — and that ruling is untouched here.**
- ⚠ **It does not revisit `merge_rule`, gap tolerance or `straddle_handling`** — amendment 1 rules all
  three and the counterfactual for `merge_rule` is stated there.
- **It does not claim the ten are foldable, only that they are TILEABLE-IF-RULED.** ⚠ Whether a span
  with no domain annotation folds usefully at all is a different question and is not answered here.

**Assumptions relied on:** ⚠ `A-014` — **UniProt topology and domain annotation is a curated MODEL of
the protein, and its silence about these ten is the model's silence, not the molecule's.**
