# RULING — 2026-08-05 — Task A ratified; three items closed; go on Task B

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority. Check the `### D-NNN` / `### F-NNN` header, not a reference to it.

> **Short by design.** Amends `ORDERS-Code-2026-08-05-F020-F021-remedy.md` §1 only.

---

## §1 — Task A ratified, and the before/after pair is the F-020 closure evidence

`ranking_runs` **(4, 4) before, (4, 4) after, across two deliberate production refusals.** Zero junk
rows. **56 of 56** ranking-set rows named — exactly F-004's population, so the guard sees what the
pre-registered result sees. Exit 1. `ranking_results` 4, `target_scores` 168, feature-7 non-null 0,
all unchanged.

⚠ **Running it twice to read the exit code past the pipe, and re-reading the counts after the
second, is the right instinct** — the second refusal is the one that proves the first left nothing
behind.

---

## §2 — ⚠ The fake red Code caught in its own work, and why it outranks the task

The ordering revert *"guard after run creation"* reddened at **`DID NOT RAISE`** — because the
fixture had no positives, so `run_scorer` raised `DegenerateLabelSet` and returned **before reaching
`create_ranking_run` at all.** ⚠ **The test would have passed under a guard placed anywhere**, and it
looked like proof.

**This is A-016 in Code's own revert proof, found by Code, three weeks after A-016 was written from
the same shape.** The remedy Code added is the part worth keeping:

> **`test_the_fixture_for_the_ordering_test_is_not_degenerate`** — asserting that with feature 7
> present, the same cohort **does** reach `create_ranking_run`.

**That is a positive control for the test's own fixture, and it is a generalisation of A-016 rather
than an instance of it.** A-016 says *confirm the red fires at the assertion.* This says
**confirm the fixture reaches the code under test at all** — a red can fire at the right assertion
and still prove nothing if the path was never entered.

**Ruled: this becomes a method note in its own right**, proposed to the assumption register when
KEEL-4 lands against v6, and **cited by name in any future order requiring a revert proof.** Reserve
its number with F-020/F-021 per §4.

⚠ **Recorded provenance:** found by Code, in Code's own work, unprompted, on the one test the
Planner had flagged as load-bearing. **The flag was right and would not have been sufficient.**

---

## §3 — The three items

**1. The refusal's surface — ruled: make it consistent, and do it in #124 before merge.**
`fit_scorer.py` already handles `DegenerateLabelSet` as `print("REFUSING TO FIT …")` + `return 1`
three lines away. Two refusal conventions in one file is a small two-paths instance.

⚠ **Code's proposed shape is the correct one and is adopted: the helper raises, the CLI catches and
formats.** A library that raises and a CLI that formats is the right layering — and it matters
beyond tidiness, because **a programmatic caller cannot accidentally proceed past a printed
message.** Do it in **#124 before merge**, so the refusal's contract lands in one commit rather than
being amended by the PR that fills the column.

**2. F-020 / F-021 — ruled: reserve them NOW, in #124, before Task B.**
Code's read of today's precedent is right: F-017 was reserved before the run it names, for exactly
this reason. **A number contested mid-task is contested under pressure.** Reserve in `RESERVED.md`:

- **`F-020`** — an absent measurement coerced to zero and fit as though measured; a guard naming the
  defect in its own warning text and proceeding anyway. ⚠ *Distinct from F-018 — identity path vs
  fit path, a miscounted row vs a fabricated result.*
- **`F-021`** — a loader that inserts where it must update, rewrites inputs it was not asked to
  touch, and binds to the most recent run by default.
- **⚠ Plus the §2 method note**, reserved as a numbered entry so it can be cited before it is
  written.

**3. The STOP ruling — it has not been delivered, and Code should NOT redo anything.**
⚠ **Third delivery failure today.** The Planner has compared Task A against
`RULING-2026-08-05-STOP-feature-7-not-extracted.md` §3.5 (*the ablation refuses; raise, not warn;
scoped to the named ablation, never to the fit*) and **Task A satisfies it exactly.**

**And note what that means.** Code built from premises it verified independently in the tree, with
the governing ruling never in hand, **and arrived at the same place.** That is a
two-independent-readings result on the *reasoning* rather than on a number — the first this project
has had. **Recorded as such, not as a lucky escape.**

**The ruling is still delivered and committed** — the finding numbers, the `extract_features.py`
hazards, and §4's account of the Planner's §0 gap exist nowhere else.

---

## §4 — Go on Task B, with one addition

**Build Task B as ordered.** One item added, cheap and only available now:

⚠ **Report the 1–6 comparison as a result even when it passes.** An 80/80 byte-identical match
demonstrates the extraction pipeline is deterministic across every code change since #109 merged —
**that is a finding about the instrument, and the instrument is what D-075 runs on.** If it does not
match, it **outranks D-075** and Task C does not proceed.

**Task C remains the owner's. Run A does not start.**
