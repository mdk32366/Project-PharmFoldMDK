# DRAFT — `P-001` discussion section, 2026-09-15

> ⚠⚠ **DRAFT, third of three** (methods · results · discussion). Nothing here is a ruling, and the
> commensurability question remains the owner's.
>
> ⚠ **The over-claim guard governs this section more than the other two.** `F-009`'s rule is
> `P-001`'s and it binds: ***the comparator has blind spots*** stays strictly separate from
> ***our scorer fills them.*** A discussion section is exactly where that separation erodes, so it
> is restated here rather than assumed to have carried over from results §R5.

---

## D1. What was found

A structure-derived axis for ADC target prioritization **ranks attempted targets modestly above
chance, is orthogonal to an expression-and-attention comparator, and survives popularity-matching
on three frozen proxies.** It **cannot be shown to add anything** over that comparator at twelve
positives.

⚠ **Those are not in tension, and the paper's contribution is that they are reported together.**
*Orthogonal but unproven* is a different scientific object from *"the features re-learned the
comparator"* — and the second was the more likely prior. Establishing which one obtains is the
result, not a step toward one.

## D2. What the attention control changes about the reading

The obvious objection to any structure-derived ranking of ADC targets is that structure is a proxy
for attention: well-studied proteins have solved structures, better-predicted structures, and more
literature, **and have been tried as ADC targets.** If that is what the axis measures, it is a
popularity index wearing a geometry costume.

**Three frozen proxies say it is not.** ⚠ And the strongest single piece of evidence is not from
Run B at all — it is `F-005`'s: **`plddt_only` aligns *less* with the evidence score than the full
model does** (Spearman −0.2897 against −0.0483). Under the attention mechanism it should align
**more**. **The one measurement that bears directly on the pathway points the wrong way for it.**

⚠⚠ **Two honest weakenings travel with that.**

1. **The proxy set was chosen knowing Run A had survived** (methods §1). The arms were pre-specified
   and the interpretation table frozen before the numbers, so the *outcome* is uncontaminated — but
   *which instruments were built* was not a blind choice. **`pdb_present` is the arm a team that had
   seen Run A would most naturally reach for, and it is the arm that performs best.**
2. **The two PubMed arms disagree, and the disagreement's sign carries no warrant.** The mechanism
   that would have said which arm is conservative was **refuted before the freeze** (rho = +0.026).
   ⚠ It cannot be read as *"even the stricter arm survives"*, because **nothing establishes which
   arm is stricter.**

## D3. ⚠ What the size of the study forbids

At twelve positives, with the median quantised in 1/224 and per-target percentiles in 1/112, **only
differences of several increments are resolvable at all** (methods §5). The consequences are
specific rather than ritual:

- **No single-statistic headline.** The triple is the unit, and `pub_count_atm` is the concrete case:
  one resolvable margin, two at or under the resolution limit.
- **No significance claim.** None was pre-registered and none is computed; choosing a test after
  seeing the distribution is the degree of freedom pre-registration exists to remove.
- **No calibrated probability** (`F-006`). The fitted scores are compressed toward the base rate.
  **Ranks, never risks.**
- ⚠ **No claim of added value.** The head-to-head is a null and is reported as one. *"The structural
  axis adds nothing measurable at this cohort size"* is `D-041`'s own phrasing for this outcome, and
  it is the honest summary.

⚠⚠ **And the comparator's own degeneracy bounds what the comparison could ever have shown.** The
evidence percentiles take **exactly two values, 0.75 and 0.25**, recorded before any number existed.
**A comparison against a two-valued instrument cannot resolve a fine difference in either
direction** — so *"not distinguishable"* here is a statement about the pair of instruments, not
evidence that the two axes are equivalent.

## D4. ⚠⚠ What this does NOT license

**`F-009` established that four clinically-validated ADC targets sit outside Kathad's 82** — an
expression-and-attention filter dropped targets that went on to become approved ADCs.

⚠ **That fact is load-bearing for this paper's existence and it survives everything below
untouched.** It is *why an orthogonal structural axis is worth testing at all*: a comparator with
demonstrated false negatives is a comparator whose blind spots are worth probing from a different
direction. The four are the motivation, and the motivation is not retracted.

**What is retracted is any suggestion that this axis recovers them.**

> ⚠⚠ **The comparator has blind spots is NOT our scorer fills them.** No retrospective claim is
> made about the four, and none **can** be: **they were not in the ranking set**, and a method's
> value cannot be demonstrated on cases selected because the alternative missed them. Choosing the
> test cases by the comparator's failures guarantees the result and measures nothing.

⚠ So the two statements stand together and in this order: **the comparator demonstrably misses
targets that matter, which is why an orthogonal axis deserved a test; and this test does not show
that this axis would have caught them.**

Also not licensed:

- **No mechanism claim about pLDDT.** `F-005` shows two of six features carry the result and the
  attention explanation is unsupported. ⚠ **Unsupported is not refuted** — one measurement points
  away from the pathway; that is weaker than excluding it.
- **No claim about the hold-48 or tiled structures.** Those do not enter `F-004` (five modules say
  so in terms), and `F-078`'s 37-row loss is confined to that instrument work.
- **No commensurability claim.** See §D6.

## D5. What a reader should take from the negative results

⚠ **The two pre-registered negative outcomes are the most reusable part of this paper**, and a
discussion section that buried them would be misreporting the design.

- **The first fired.** The head-to-head is not distinguishable, **and the direction reverses between
  mean and median** — which axis looks better depends on which summary is chosen. That reversal is
  the cleanest available statement of *not distinguishable* at this size, and it is more informative
  than a p-value would have been.
- **The second did not fire.** A *strong* correlation with the comparator was pre-registered as
  **also** being a null, because it would mean the features proxy attention-and-precedent. Spearman
  −0.0483 says they do not.

⚠⚠ **The methodological point is offered AFTER the primary result and depends on it.** `F-072` is
ruled: the structural enrichment survives popularity-matching on three frozen proxies. **That is the
finding.** What follows is what the design additionally buys.

**A design in which both pre-registered outcomes were nulls, and which reports which of them
obtained, is doing something a single-hypothesis design cannot** — and it is worth more *because the
primary arm survived*, not instead of it. A pre-registration whose every branch returned nothing
demonstrates only that the branches were reachable.

⚠ **The ordering is deliberate.** A methodological claim offered where a result should be reads as
compensation for not having one; the same claim offered after a ruled finding reads as generality.
It is also narrower and more defensible than *"first honest measurement of an under-explored
axis"* — which is a claim about the field, and this one is a claim about the design.

## D6. ⚠ Open, and explicitly the owner's

- **Commensurability.** `P-001` amendment 2 returned the **third** pre-registered outcome —
  `underpowered` at n = 4, neither branch established — with the bars disagreeing on one row of
  four. The limitation stands as **dilution, unquantified, not bias with a sign.** ⚠ **Still the
  owner's ruling, and no claim in this paper rests on that arm.**
- **The steelman limitation**, which depends on the above.
- **Systematic lit review** (PRISMA-grade), **Site4Drug / PNAS 2026** verification.
- ⚠ **Span repairs** (`F-069` / `F-071`) are unblocked by the freeze, but **`D-075`'s anchor rests on
  a frozen set that a span change would move.** Repairing before submission trades one disclosure
  for a larger one, and that is a decision rather than a task.

## D7. ⚠⚠ The epistemic note, and why it is in the paper rather than a lab notebook

> **A pre-registration that MATCHES cannot distinguish *correctly anticipated* from *the data was
> never going to say otherwise*.**
> **Agreement is weaker evidence than disagreement.**

The commensurability prediction — *scattered, and more honestly underpowered* — was recorded before
the run and matched. ⚠ **At n = 4 no other answer was available, so the prediction cost nothing and
proved nothing.** Predictions that *failed* elsewhere in this project carried more information than
that one which held.

⚠ **Stated in general form deliberately:** the register asserts a count of specific misses that
**neither it nor anything else in the repository names**, and under `D-016` a claim that cannot say
how it is known does not enter a paper as a number.

**Why it belongs here:** a paper that pre-registers, and then reports a matching prediction as
though the match were evidence, teaches the wrong lesson about pre-registration. **The value of a
pre-registration is in the outcomes it could have been wrong about**, and saying so is the one claim
in this paper that generalises past the cohort, the axis, and the method.
