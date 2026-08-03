# Pre-Work — Paper Phase — the novelty search, and what a paper actually is

> **Written for an engineer who has not done this before — on purpose.** You know build discipline
> cold. You have not written an academic paper, navigated a prior-art search, or made a novelty
> claim. This document assumes none of that knowledge and explains it as it goes. Where a term is
> jargon, it is defined the first time. Nothing here is beyond you — it is just unfamiliar, and
> unfamiliar is a state we map, not a wall we hit.
>
> **KEEL still governs.** Everything below is the discipline you already have, pointed at a new
> object. Where a step has a KEEL analogue, it is named, because the analogue is how you'll trust it.

---

## §0 — Before anything: do NOT touch the build

The strongest instinct right now will be to "improve the project for the paper" — add a feature,
re-fold something, polish the UI. **Resist it completely.** Here is why, and it is a real research
principle, not caution:

**The result was computed from a frozen state.** F-004's fit, F-005's ablations, F-006's
distribution — all of them were computed from *these* 79 folds and *this* D=56 ranking. If you
re-fold, re-fit, or add a target now, the numbers in the paper would no longer correspond to the
system that produced them, and you'd have to re-run and re-verify everything downstream. Worse: a
paper describes *what you did*, and what you did is already done. Changing the artifact after the
result exists is, in research terms, moving the goalposts after the shot. **The build is frozen. The
paper describes the frozen thing.** This is the same discipline as "no re-fold to populate fields"
(D-070 decision 4) — you already ruled this once; it now applies to the whole artifact.

The only build-side action still open is the trivial one from the last close-out: commit the 07-30
close-out on its own branch. That's housekeeping, not a change to the result.

---

## §1 — What a "paper" actually is (the honest orientation)

You've never written one, so here is the whole thing in plain terms, no mystique:

An academic paper is **one defensible claim about the world, plus the evidence for it, plus an honest
account of why the claim isn't already known.** That's it. Everything else is structure around those
three things. Concretely, a paper is built from these parts — you already *have* most of them:

- **The claim (your "contribution").** The one new true thing you're telling the field. You have two
  candidates (see §3). This is the hardest part and the thing the whole paper serves.
- **Related work.** A section that says "here is what was already known, and here is the specific gap
  my claim fills." This is what the novelty search feeds. Its job is to *prove you know the field*
  and to *locate your gap in it*. A paper with weak related work reads as "didn't check if this was
  already done" — the exact failure the novelty search prevents.
- **Methods.** What you did, precisely enough that someone could repeat it. **You have this already**
  — it's your decision log, your pinned checkpoint, your frozen cohort. Most first-time authors
  agonize over methods because they didn't record as they went. You recorded obsessively. This
  section will be the easiest one you write.
- **Results.** What you found. F-004 and F-005, stated as findings. **You have these, pre-registered
  and bounded.** Also unusually easy for you.
- **Limitations / threats to validity.** The honest account of what could be wrong. **This is
  normally where papers are weakest and yours will be strongest** — your entire project is an
  honesty apparatus. Reviewers respect this section enormously and most papers fake it.

The reason the professor sees a paper here: you are *missing* only the two hard parts (the sharp
claim and the related-work gap), and you *already have* the four parts that usually sink first-time
authors. That's a rare position to be in. Don't waste it by rushing the two you're missing.

---

## §2 — The one task for this phase: the prior-art search, done as pre-registration

A **prior-art search** (also called a **literature review** or **related-work search**) is: finding
every paper that might already have done what you claim is new, and honestly deciding whether it did.

**The trap, named so you can avoid it.** You *want* it to be novel. So you will be tempted to read
every near-miss paper as "not quite the same" and every absence as "nobody's done it." This is
motivated reasoning, and it is the single most common way novelty claims die in review — a reviewer
knows the one paper you talked yourself out of counting.

**The KEEL fix, which you already know how to run: pre-register the disqualifier.** Before you search,
write down — in advance, in a file — the exact finding that, *if it exists in the literature*, means
you are **not** novel. Then search **for that thing**, hard, trying to *find* it, not to miss it.
This is exactly F-005's move: you wrote the outcome table before the ablation ran, so you couldn't
rationalize the result. Same discipline, new object. **If the disqualifying paper exists, you want to
be the one who finds it, not the reviewer.**

Draft disqualifier (we'll sharpen this together before searching):

> *"A published paper that ranks ADC (or antibody-drug-conjugate) target proteins using features
> derived from a protein structure-prediction model, and compares that structure-derived ranking to
> an expression-based or other baseline ranking — OR a paper that uses a folding model's confidence
> (pLDDT) as a predictive signal for target suitability rather than as a structure-quality filter."*

If **either half** of that exists, the novelty is narrower than it looks and we scope the claim down
honestly. If **neither** exists, the gap is real and we can state it plainly.

---

## §3 — What, specifically, might be novel (three candidates, scoped honestly)

Novelty is never "the whole project" — it's a specific claim on open ground. The search has to tell
you *which* of these is standing where nobody's stood. They are different claims with different
strengths:

1. **The method** — real folding-model structures → ADC-suitability features → ranking-vs-expression
   comparison. *Most likely to have partial prior art in pieces* (people have used structure for
   druggability; people have ranked ADC targets). The search will probably narrow this one.
2. **The finding (the strong candidate)** — that the above-chance signal is carried by the folding
   model's *confidence* (pLDDT), **not** by the geometry features, and that the intuitive "attention/
   structure does the work" explanation is **unsupported**. *This is deflationary, surprising, and
   specific.* Deflationary findings are underreported precisely because they're not what people hope
   for — which is exactly what can make them novel and publishable. **If the search clears the pLDDT-
   as-signal half of the disqualifier, this is your paper.**
3. **The rigor apparatus** — pre-registration, honest denominators, corrections-recorded. *Not a
   research contribution on its own*, but a methods-transparency strength that makes 1 or 2
   trustworthy. It supports the claim; it isn't the claim.

**Working hypothesis for the search's purpose:** find out whether candidate 2 is novel. It's the
sharpest, most defensible, and least likely to be crowded. Candidates 1 and 3 support it.

---

## §4 — How we'll actually run the search (the instrument)

Not from memory — mine is stale on current literature, and a novelty search run from a language
model's recollection is worthless. It has to be **real retrieval against the actual literature.**

- **Elicit** (you have it connected) is the right instrument — it's built for systematic academic
  search over real papers, exactly this task, rather than a handful of web searches. We'll use it to
  search the three literatures the disqualifier touches: ADC target prioritization; protein-language-
  model / structure-prediction for druggability or target assessment; and — the sharp one — anyone
  using pLDDT or fold confidence as a *signal* rather than a quality filter.
- **The method, so it's honest:** we search *for* the disqualifier, log every near-miss with a
  one-line "why it does / doesn't count," and let the record show we tried to kill our own novelty.
  Same as red-then-green: a novelty claim that never faced a real attempt to disprove it isn't
  confirmed to hold.
- **The output** is a related-work map: what exists, where your gap sits in it, and a ruling on which
  of §3's three candidates survived. That map *is* your related-work section, drafted.

---

## §5 — The honest unknowns (what neither of us knows yet)

Stated plainly so nothing is oversold:

- **We don't know if it's novel.** The professor's belief is a hypothesis. The search tests it. It
  may come back "candidate 2 is genuinely open" or "someone did the pLDDT-signal thing in 2024" —
  and we report whichever, the same way F-005 reported the result that reversed the premise.
- **We don't know the venue yet** (a "venue" is the journal or conference a paper is submitted to;
  different venues want different things, and that shapes the paper). That's a later question, and
  the professor — who knows the field's venues — is the right guide for it. Don't pick one yet.
- **We don't know the author situation** — whether this is your paper, a joint paper with the
  professor, what "novel" means to the specific subfield. These are conversations to have *with the
  professor*, and worth having early, because they change how the paper is framed. This is domain
  navigation you should not do alone, and don't have to.

---

## §6 — Sequencing (what to do, in order, none of it tonight)

1. **Commit the 07-30 close-out** on its own docs-only branch. Housekeeping; closes the build cleanly.
2. **Talk to the professor before searching.** Ask three things: what does "novel" mean in *this*
   subfield; is this your paper or joint; and does he already know of prior work you should start
   from. He may hand you half the related-work map. (This is the biggest lever and costs one
   conversation.)
3. **Sharpen the disqualifier** (§2) into its final form, *with* whatever the professor adds. Write
   it down before searching. Pre-registration.
4. **Run the Elicit search** against the three literatures, searching *for* the disqualifier.
5. **Rule** on which of §3's candidates survived, and draft the related-work map from what the search
   returned.
6. **Then, and only then,** decide whether there's a paper and what its single claim is. Everything
   before this step is evidence-gathering; this step is the finding.

**Do steps 1 nor 2 whenever you're rested. The rest waits on step 2's conversation. There is no
clock on this** — a novelty search done fast and motivated is worse than useless, because it produces
a false "yes" a reviewer later destroys. Slow and adversarial beats fast and hopeful, every time.

---

*The build phase is closed. This phase has one object: is the claim novel, and can it survive contact
with the literature? We answer it the way we answered everything — pre-register the disqualifier, then
search hard for it. Same discipline, one more time, on unfamiliar ground you do not have to cross
alone.*
