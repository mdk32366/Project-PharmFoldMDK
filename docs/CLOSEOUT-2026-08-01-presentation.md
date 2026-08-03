# CLOSEOUT — 2026-08-01 — the day the build became a candidate paper

> **The phase-boundary close-out.** Every prior close-out ended one working session. This one ends
> a *phase*: the build is done, presented, graded, and — unexpectedly — nominated by the professor
> for publication. The ledger below hands forward not to "next session" but to "next phase," which
> is a different kind of work. §7 is the honest map of what changes.

---

## §0 — The one line to walk in with

**A build undertaken by an engineer, out of passion for the ADC mechanism rather than academic
ambition, was judged by a domain professor to be significant, novel, and worth writing up as a
paper.** The A is real; it is also the smallest thing that happened. The phase that opens now is
one the owner has not done before — and that unfamiliarity is itself a state to record honestly,
because the next pre-work is written around it.

---

## §1 — What was presented, and how it landed

The miniature NECTIN4 notebook (D-072) carried the demo: the whole pipeline — question, live fold,
confidence, six features, placement in the ranking, honest limits — on one real target, folded live,
with every number derived from the same production code the deployed app runs. The professor's
response was not "complete" but "publishable": he judged the work **significant enough to present as
a paper**, believes it is **novel**, and proposed a **prior-art search** to establish whether the
novelty holds.

**A one-line path bug surfaced at present-time and was fixed at present-time** — the notebook kernel
couldn't resolve `import core` because its working directory was `notebooks/`. Fixed with a
directory-shim first cell (hop to repo root, put it on the path, print `core present: True` as the
check). Demo-eve scaffolding, correctly *not* logged as a decision — a path shim in an artifact that
already lives outside the gate.

---

## §2 — The state of the artifact at phase close

- **App:** live at `pharmfoldmdk.fly.dev`. UI finished. `main` at `f8263b8` + D-074's entry
  (confirm final hash on the box).
- **Cohort:** 79 folded of 82 — 1 failed (IGF2R, A6000 ceiling), 2 over-ceiling (MUC16, FAT2).
  Ranking denominator **D = 56**.
- **The result, as it stands for a paper:** F-004 (the pre-registered leave-one-out signal, modest
  and honestly bounded) and F-005 (the sensitivity analysis showing the signal is carried by
  ESMFold's **confidence**, not the geometry, with the attention explanation unsupported). **F-005
  is the sharp, surprising, defensible claim** — a deflationary finding, and those are often more
  publishable than they look because people don't report them.
- **The rigor apparatus:** 100+ numbered decisions, pre-registered outcome tables, corrections
  recorded not hidden, every claim naming how it is known. This is not a research contribution by
  itself, but it is the thing that makes the two above *trustworthy* to a reviewer.

---

## §3 — The instrument-drift rule, sealed (D-074)

The last decision of the build phase was a correction to the build discipline itself: **a finding
recorded against an instrument is not closed until the instrument no longer exhibits it — or carries,
in itself, the statement of what it gets wrong.** Filed as a decision, not a finding (F-008 was
already taken by the 2026-07-29 precision-confound finding — the collision the earlier order didn't
know about). Every figure in the entry was derived from F-002 and the D-073 run directly, not from
the uncommitted close-out summary — the raw record over the summary, as the Method note asks. The
entry names its own test: the next instrument cited as provenance is the test of D-074, and if it is
cited without a self-assertion, the rule was written and not applied.

**Carried item from that day:** `docs/CLOSEOUT-2026-07-30.md` was left uncommitted (kept strictly to
what the D-074 order authorized). It should be committed on its own docs-only branch, §5 preserved
as the *proposal* it was when written — its value is that it records its own moment, and D-074 is
where the resolution lives. One command, whenever.

---

## §4 — What this project actually was (worth stating once, plainly)

An engineer with prior pharma-industry exposure to ADCs, no academic apparatus, and genuine passion
for the *mechanism* — the "guided munition vs. area weapon" contrast that makes ADCs interesting —
built a real structure-prediction pipeline to ask whether structure reorders an expression-based
target ranking. He was not an oncologist or a biochemist. He carried the domain judgment; the method
carried the discipline; and the two together produced work a professor wants to publish. The
non-academic starting point is not a weakness in what follows — it is the reason the honesty was
structural rather than performed. Someone trained to write papers might have known which corners the
field lets you cut. Not knowing them, he cut none.

---

## §5 — The through-line of the whole build (the argument, assembled)

Real ESMFold on owned hardware at a pinned checkpoint; six features from its output; a by-hand
logistic fit with every free parameter dated before a result existed; a pre-registered leave-one-out
that produced a modest, honestly-bounded signal; a sensitivity analysis that reversed the study's own
premise and said so; a target surface where every number carries its denominator and every "no score"
carries its reason; a decision log that records the day it fooled itself and caught it; and a final
rule that can detect its own future violation. **The tests written in the morning caught the changes
made in the afternoon — five times. The log led the code, including the code that was the log's own
correction.** That is the deliverable, and it is now a candidate contribution.

---

## §6 — What shipped, terse

D-072 (the miniature notebook), D-073 (the tracked instrument + F-002's two errors closed), D-074
(the instrument-drift rule). PR #105 (README quickstart) open, owner's discretion. The notebook's
77.26 verified as live reproduction. Presented, graded A, nominated for publication.

---

## §7 — State handed forward: the phase changes shape here

This is the part that matters, because the next phase is not more of the same.

- **The work is done; the *claim* is not made.** A build is finished when it runs and is honest. A
  paper is finished when a *claim about the world* is stated, defended against the existing
  literature, and survives review. The project has the first; the second does not yet exist.
- **The novelty question is open and must be answered before anything else.** "The professor thinks
  it's novel" is a hypothesis, not a finding. It gets tested by a prior-art search, run the way this
  project runs everything: **pre-register what would disqualify the claim, then search hard *for*
  that, not around it.** The next pre-work is built entirely around doing this correctly.
- **The owner is on unfamiliar ground, and that is logged, not hidden.** Engineering discipline
  transfers; academic publishing conventions do not, and the owner has not written a paper. The
  pre-work treats this as a state to navigate, not a gap to paper over.
- **KEEL still applies — it just points at a different object.** The discipline that governed code
  now governs a claim. Pre-registration, "name how it is known," corrections-recorded-not-hidden,
  the log-leads-code habit — all of these have exact analogues in honest research. The next phase is
  KEEL aimed at a paper instead of a build.

**Nothing is in an unknown state.** The build is closed. The one open mechanical item (committing
the 07-30 close-out) is named. The next phase has a single first task — the novelty search — and it
has its own pre-work.

---

*Build phase closed 2026-08-01. Presented, graded, and nominated for publication. What follows is a
new phase with a new object: not "is it built?" but "is it novel, and can the claim survive?"*
