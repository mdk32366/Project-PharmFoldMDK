# PASTE-READY — FOUR entries — for `docs/README.md`

**AUTHORED-SHA256** (range: **first `### ` header → EOF**, anchored to line starts, **SECOND
occurrence of the marker**) = `0da46263da6e6ff767aa67ad1fc2287d21a88581c4713d331b22bb0cdf5aab1e`
**bytes** = `8855`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE.** Landing header **above** the marker, outside the range.
> ⚠⚠ **FOUR ENTRIES AT TWO LEVELS. SPLIT ON LANDING.** **Three are TOP-LEVEL `###` — none of their
> titles carries "amendment".** **One is `#### F-047 amendment ‹M›`.**
> ⚠ **Confirm every number against the live log; `F-050` stays RESERVED. Three greps each.**
> ⚠⚠ **The filename says nothing about the numbers. The header is the identifier** — *a paste whose
> filename said `F-054` was landed as `F-055` this week, and landing by filename would have
> collided.*

---

### F-‹A› — ⚠⚠ The test substrate forgives exactly the mistake production rejects: 2,690 census cards were 500 in production while the suite was green

- **Date:** 2026-08-21 · **Status:** ⚠ **OPEN.** It closes when no test's correctness depends on
  SQLite's coercion behaviour, or when each such test states that it does.
- **How known (`D-016`):** measured directly against both engines while diagnosing a live outage.

**⚠⚠ THE OUTAGE.** **Every one of the 2,690 FOLDED census cards returned HTTP 500 in production.**
**Sampled 8/8 folded → 500; 8/8 unfolded → 200.** ⚠ **The unfolded rows return before the offending
call, which is why they worked and why the scope stayed hidden.**

**⚠ THE CAUSE.** Widening `/census/{analysis_id}` to `str` so accessions could be used as keys left
one downstream consumer passing the raw parameter — `census_profile_block(engine, analysis_id)`,
signature `analysis_id: int`.

**⚠⚠ AND THE REASON THE GATE CANNOT SEE THIS CLASS AT ALL:**

```
SQLite:   session.get(ProteinAnalysis, "1970")   -> row found   (string PK silently coerced)
SQLite:   session.get(ProteinAnalysis, "A0AVI2") -> None, no raise
Postgres: rejects both
```

⚠⚠ **This is not a coverage gap. The test substrate has DIFFERENT SEMANTICS from the thing it stands
in for, and no quantity of additional SQLite tests would have caught it.** ⚠ *Distinguishing that
from the day's other two green-tests-broken-production findings is what makes this its own entry.*

**⚠ THE REMEDY, and it has two halves that do different work:**
1. **The guard asserts WHAT IS PASSED — the resolved `int` — which is checkable on ANY engine.**
   ⚠ *The assertion stops depending on the substrate.*
2. ⚠⚠ **A second test RECORDS THE DIVERGENCE AS A FACT, so it reddens if SQLite or SQLAlchemy ever
   tightens.** **A known divergence that silently disappears is a guard whose premise expired without
   notice.** *(Code's second half, and the one the Planner would have omitted.)*

⚠ **What this does NOT claim:** not that SQLite is the wrong substrate · not that every test is
suspect · ⚠⚠ **only that a test's correctness may rest on engine behaviour nobody stated, and that
every test in this project resolving a primary key stands on it.**

---

### F-‹B› — ⚠⚠ A parameter whose type widens has as many defects as it has consumers, and they do not announce themselves together

- **Date:** 2026-08-21 · **Status:** ⚠ **OPEN.**

**Widening `/census/{analysis_id}` produced TWO defects from ONE change:**

| consumer | defect | scope |
|---|---|---|
| `census_profile_block` | **HTTP 500 on Postgres** | **2,690 cards** |
| structure / pLDDT URLs | **HTTP 422** | the viewer |

⚠⚠ **The first was fixed one day before the second was found, by the same person, who did not look
for a second consumer.** *(Code's own framing, adopted verbatim as the entry's thesis.)*

⚠ **`F-052`'s family with a NEW MECHANISM.** **Not *a convention the newest caller missed* — a
SIGNATURE CHANGE whose blast radius nobody enumerated.** ⚠⚠ **And the two defects surfaced days apart
with different status codes on different surfaces, so nothing connected them.**

**⚠ THE REMEDY IS THE `PA` SHAPE: enumerate the consumers, BOTH DIRECTIONS, before fixing the one in
front of you.** *Forward — what does this function call? Reverse — what calls this parameter?*
⚠ **Name the check; do not build a framework** (`D-074` decision 3).

⚠⚠ **And the aggravating fact: `StructureViewer` had NO TEST FILE AT ALL.** **The component that
failed for five days was untested, which is why five days was possible.**

---

### F-‹C› — ⚠⚠ Three guards, three resolutions, and each fix inherited the previous level's unit

- **Date:** 2026-08-21 · **Status:** ⚠ **OPEN**, and ⚠⚠ **this entry is the reason the others recur.**

| # | guard | its unit | what it could not see |
|---|---|---|---|
| 1 | `NC`, the first attribution audit | **one component** | four other components rendering HPA data |
| 2 | `PA` / `PC3`, built to fix that | **the component set** | ⚠ **which BRANCH inside a component renders the value** |
| 3 | the branch fix | **the branch** | ⚠ *unknown — and that is the point* |

**⚠⚠ THE INSTANCE THAT NAMES IT.** In `CensusDetail`, the HPA attribution appeared **only in the
`status !== 'covered'` branch — which renders NO HPA value — and was absent from the branch rendering
`qh_score`, which is HPA content by `D-100`.**

⚠⚠ **So the licence precondition rendered where there was nothing to satisfy it about, and was absent
exactly where it binds.** **The suppression defect and the compliance defect were THE SAME DEFECT seen
from two sides, and only one of them looked like a defect.**

**⚠ `PC3` could not see it: *it asserts the file IMPORTS the attribution, and the file did.*** ⚠⚠ **A
file-level guard cannot see which branch renders the value.** *(Code's diagnosis.)*

**⚠⚠ THE GENERAL FORM, WHICH IS WHY THIS IS A FINDING AND NOT THREE INSTANCES: each remedy adopted
the granularity of the level it was fixing, and the next defect lived one level down.** ⚠ **A guard
inherits its unit from the defect that prompted it, and the defect that prompted it is by
construction the coarsest one anybody had noticed.**

**⚠ Named, not built** (`D-074` dec 3): **when writing a guard, state its UNIT explicitly and name the
next finer unit it cannot see.** ⚠⚠ **`PC3` would have said *"file-level; cannot see branches"*, and
this entry would have been unnecessary.**

---

#### F-047 amendment ‹M› — ⚠⚠ Three more, and all three are a check that PASSED while being wrong

- **Date:** 2026-08-21 · **Status:** `F-047` stays **OPEN and STANDING.**

**⚠⚠ MEMBER — AN INVISIBLE BYTE INVERTED A GUARD.** *(Code, self-caught.)* **`\b` escapes became
literal BACKSPACE bytes through a Python heredoc** — the regex was `/‹BS›import…/`. **Three of them,
two inside `UB3`.**
⚠⚠ ***`UB3` was green BECAUSE it was broken:*** **a regex containing an unmatchable byte returns `[]`,
and the *"no bad matches"* assertion passed.** ⚠ **Only `cat -A` showed it — the Read tool renders it
as nothing at all.**
⚠⚠ **Sixth string-mangling instance this week and the FIRST where the damage was an absence of a
rendered character rather than a visible corruption.** **Every prior one announced itself as garbage;
this one announced itself as correct.**
**⚠ The durable line: a check whose expected-empty result is ALSO its failure mode cannot distinguish
*nothing wrong* from *nothing looked at*.** **The remedy is a positive control — assert the pattern
matches something it should.**

**⚠⚠ MEMBER — A TEST ASSERTED THE RIGHT STRING AGAINST A PAGE SHOWING SOMETHING ELSE.** *(Code,
self-caught.)* **`text-transform: uppercase` renders `IMAGE/DATA CREDIT:`; `textContent` IGNORES CSS
transforms; so the existing assertion on `/Image\/data credit:/` PASSED against an uppercased page.**
⚠ **Second time this week a test was green about text the reader never saw.** **The new test reads
the stylesheet.** ⚠⚠ ***`textContent` is not what the reader reads.***

**⚠ MEMBER — THE PLANNER FLATTENED A DISTINCTION THE ENTRY ALREADY DREW.** *(Planner.)* **The order
said *"the four elements, PER DATUM."*** ⚠⚠ **`D-093 amendment 3` item 3 does not say that** — the
GENERAL case is two page-level obligations and the SPECIFIC case adds two more, **of which only the
DIRECT URL is per-datum.** **Code built what the order said: four full blocks on 79% of census cards,
zero on the rest, no middle case.**
⚠⚠ **And the de-duplication that looked obvious would have breached the licence: the four blocks
differ in exactly one field, and 75 of 79 cards carry THREE DISTINCT DEEP LINKS.** ***"Keep the first
and drop the rest" would have thrown away two working per-datum links*** — **the one element the
licence describes per-datum.**
⚠ **Suppression was the larger half: ~172 of 316 blocks carried attribution for no rendered value** —
`cancer_assoc` **78 of 79**, `surface_check` 51, `clin_normal` 39, `clin_tumour` 4. ⚠⚠ **More than
half the attribution on the surface was attached to nothing, which is citation inflation: a reader
cannot tell which citations are load-bearing.**

**⚠ AND A METHOD CORRECTION WORTH THE SPACE.** *(Code, self-caught.)* **A first pass at the
empty-block counts GUESSED the payload keys — `rows`/`tumour`/`normal` against the real
`hits`/`tumours`/`normal_tissues` — and returned a suspiciously uniform 79/79 for all three.**
⚠⚠ **A wrong key returning a clean, uniform, plausible answer, caught because the uniformity was too
good rather than by any check.** ***A result that is suspiciously tidy is evidence about the query,
not about the data.***
