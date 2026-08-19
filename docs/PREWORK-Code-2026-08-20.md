# PREWORK — Code — 2026-08-20 — what I know from having built it, and what I need ruled

> ⚠ `PREWORK-2026-08-20.md` is the Planner's and was written before this session's work landed.
> **Most of its §6 table is now discharged.** This is Code's view, written after.
> **Grounding:** `main` `4e12d9b`, release **v82**, schema `0010_feature_ingest`.

---

## §0 — ⚠⚠ Read this first: the state moved further than the Planner's prework assumes

That document opens by asking to re-key the rental population and wire `preflight`. **The re-key is
done and it changed the answer.** Measured against the database rather than `D-041`:

```
cohort targets unfolded today        3        (D-041 recorded 29 rental-tier unfolded)
of those, Group B positives          0
band 441–629: FC said 13 targets / 3 positives   →  measured 0 and 0
```

⚠⚠ **The ceiling climb buys nothing.** Everything in 441–629 is already folded. The two remaining
unfolded targets are **FAT2 at 4,030 aa and MUC16 at 14,451 aa**, plus **IGF2R**, which is a
different thing — it has a row and a recorded cause: *CUDA OOM at 2,491 aa, chunk_size 32*.

**So the rental question is a TILING question, not a ceiling question.** Any plan built on
*"raise the local ceiling and recover positives"* is planning against a number that moved.

---

## §1 — The one thing I most want ruled, and it is not technical

**`D-079` amendment 3 records a residual I cannot test away.** 1,397 census proteins now carry a
number, and those numbers span **0.1065–0.2927 — a band 0.19 wide on a 0-to-1 scale.**

Every guard is in place: the word is never *score*, the value never renders without the cohort's own
band beside it, refusals are rendered at equal weight, five preconditions sit in the same frame, and
the table column is a category with no magnitude. ⚠ **None of that stops a reader opening two
proteins in two tabs and subtracting.**

**Two mitigations are pre-recorded as *identified and not taken*** so choosing one is a decision
rather than a discovery:
1. **render the band position without digits**
2. **gate the value behind an explicit reveal**

⚠ I would not choose between these myself. **Both are small; the choice is about what the project is
willing to have read into it**, and that is the owner's.

---

## §2 — Confidence: the fork is set up and the instrument already exists

`F-051` established that *"the two confidence features"* is really one:
**`membrane_proximal_plddt` 32.2% of attribution against `mean_plddt_ecd`'s 6.4%** — a factor of
five. ⚠⚠ **And this session's out-of-range measurement confirmed ruling 4's prediction BY
MEASUREMENT**: the two confidence features are out-of-range offenders **#1 and #2** (33.1% and
18.5%). *The feature doing the most work is the one that leaves the fitted range first.*

**The fork, unchanged and still unresolved:**
- **A — circularity.** A dominant *global* confidence feature would suggest the score tracks how
  PDB-like a sequence is, which tracks research attention, which tracks having been tried as an ADC.
- **B — informative uncertainty.** A dominant *membrane-proximal* feature suggests ESMFold is
  uncertain near the membrane boundary and that uncertainty is itself informative.

⚠ **The measurement favours B and does not establish it** — the dominant feature is *regional*, which
is what A would predict least. **`D-075`'s `geom_proxy` is the instrument that separates them**, and
`F-017` already records it firing at `0.6607 / 0.6324 / 8-of-12`. **Nothing new needs building to ask
this question.**

⚠ **One caveat that must travel with any confidence claim** (`D-079` am 5 / ruling 9): the cohort's
`mean_plddt_ecd` minimum of 50.49 is **largely an artefact of `D-041`'s pLDDT floor**, and 831 of
that feature's 868 refusals fall below it. **A selection rule and a support gap at once.**

---

## §3 — Cost intuition I did not have yesterday and you should have now

- **Census feature extraction: 38 minutes**, not a night. Pure CPU, stdlib only. ⚠ It was ordered as
  an overnight job; the compute is **five minutes** and the rest is HTTP fetch from the Fly VM.
  **Extraction is not a rental claimant and never was.**
- **The ingest is idempotent and safe to re-run.** A second run keyed to the same `sha256` is a
  no-op — proven against production, with the table byte-identical before and after.
- **`fly mpg connect` costs nothing and is read-only under `pharmfold-readonly`.** Most questions
  asked this session were answered in one query. ⚠ **Ask the database before ordering a measurement.**
- ⚠ **IGF2R is the cheapest unfinished thing in the project.** The deck already scopes it: one
  rental block, under an hour, about $1. It is a compute limitation, not a size wall.

---

## §4 — ⚠⚠ Hazards I hit, that will bite the next session too

**Recorded as `F-052`: a convention that exists, is documented, and is obeyed by every caller except
the newest one.** Three instances on the production host in one day, and **in two of them I had
written a test for it and the test passed on the broken code.**

⚠ **Five separate tests reddened on CORRECT code** — banning a word that appeared in the *denial*,
or scanning prose that cannot tell *"I am one"* from *"that one is one"*.

**Two rules that worked every time, and I would apply them before writing any new guard:**
1. **Derive the set, never enumerate it.** Every enumerated rule protected only the members its
   author could see.
2. **Put meaning in a field, not in a string.** When a test needs to check what a sentence *means*,
   the meaning belongs in `kind`, not in prose a regex has to interpret.

⚠ **And use `.venv`, not the system Python.** Two failures this session came from a richer
interpreter: a spurious gate failure on missing `psycopg`, and a committed script the project's own
Python 3.11 **could not parse** because it was authored under 3.14.

---

## §5 — Open items, with holders. ⚠ Everything Code-held is discharged

| # | item | holder |
|---|---|---|
| 1 | **The 0.19-band residual** — pick a mitigation or accept it | **Owner** |
| 2 | **`D-075` `geom_proxy`** — settle the confidence fork | **Planner** |
| 3 | **Rental spend** — tiling FAT2/MUC16, or IGF2R alone (~$1) | **Owner** |
| 4 | **Where a computed profile is PERSISTED** — nothing stores it today | **Planner** |
| 5 | `refused_out_of_distribution` needs a home; **not** `extraction_outcome` | **Planner** |
| 6 | **`F-021` clause 1** — `--load` upserts, or the residual is accepted | **Owner** |
| 7 | **`F-050`** — the guard-direction sweep, reserved and unwritten | **Planner** |
| 8 | Seven `CensusView` CSS classes with no rule | Code, on request |

---

## §6 — What I need from you to start

⚠ **Nothing is blocked on me**, so a session can begin with any of the above. But two answers make
the difference between an hour and a day:

1. **Is the profile's presentation settled** (§1), or am I changing how it renders before anything
   else is built on it?
2. **Is the rental question tiling, or is it IGF2R alone?** They are different orders — one is a
   design decision about `D-095`'s tiling, the other is one rental block and a re-run.

⚠⚠ **And a request about how orders are written**, from three of them this session: **an order that
states a number I should reproduce is far more useful than one that states a conclusion.** `JB`
gave me a formula that was wrong — `attribution/x = coef/sd` — and saying so was worth more than
the task itself. **Keep doing that.** Every order that pre-registered both outcomes produced a
usable finding; the one that pre-registered a single expectation produced a correction.
