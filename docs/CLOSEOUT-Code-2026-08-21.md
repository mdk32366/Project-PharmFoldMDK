# CLOSEOUT — Code — session 2026-08-21

> ⚠ **DATE, STATED BECAUSE IT DIVERGES.** Log entries are stamped **2026-08-21**; the machine's wall
> clock stamped the commits **2026-08-19 / 20**. The companion is `CLOSEOUT-2026-08-20.md` — the
> **Planner's** closeout for the *previous* session, whose own companion is `PREWORK-2026-08-21.md`.
> **The precedent is `CLOSEOUT-2026-08-18.md`**, which names the same divergence in its title.
> ⚠ Named rather than reconciled: the clock is what it is, and a closeout that silently picked one
> date would make the sequence unreadable later.
>
> ⚠⚠ **Where this file and `docs/README.md` differ, THE LOG GOVERNS.** Every number below is
> checkable and every one of them should be re-derived rather than quoted.

---

## §0 — Grounding

**`main @ a0a7651`.** Gate **1,025 passed, 19 skipped** · UI **413 passed** across 46 files.
Parent invariant **160 defined | 15 reserved | 175 cited | 0 dangling**; amendment invariant
`cited − defined = 0`. **16 pull requests merged (#177–#192).**

**Landed in the log:** `F-054` · `F-055` · `F-056` · `F-057` · `F-058` · `F-047` amendments 3 and 4 ·
`D-034` amendment 1 · `D-093` amendment 10 (with §5 amended) · `D-102` amendment 2.
**In `PAPERS-v2.md`:** `P-001` amendments 1 and 2.

---

## §1 — ⚠⚠ The day's largest finding: a feature that shipped green and was entirely absent

**`F-054`.** PR #175/#176 deployed the 777 never-folded census rows — the fix that makes `HER2`
findable at all. **The gate was green: 1,012 passed.** Live `/api/census` returned **2,690 of 3,467**.
**The feature was not degraded. It was absent**, and the census had silently returned to the exact
state the owner had reported as a defect that morning.

**Cause:** `_attach_cohort_fold` read `c.error`; `ProteinAnalysis` has no such column. ⚠ Ordinary.
**⚠⚠ The finding is the second half:** one `try` wrapped **both the row construction and the optional
enrichment**, so the fault did not degrade the enrichment — **it deleted 777 rows and returned a
well-formed HTTP 200 shorter list.**

⚠ **Why 1,012 tests saw nothing:** every test on that path parses the module with `ast` and asserts
on the tree. ***An AST test asks whether code was WRITTEN. It cannot ask whether it RUNS***, and it
can never see a column that does not exist.

---

## §2 — ⚠⚠ THREE "GREEN TESTS, BROKEN PRODUCTION" FINDINGS IN ONE DAY, AND ONE IS STRUCTURAL

| | what the gate could not see | fixable by more tests? |
|---|---|---|
| `F-054` | an AST test cannot see a column that does not exist | ⚠ yes, with a different KIND of test |
| `F-057` | a widened parameter has as many defects as consumers | ⚠ yes |
| **`F-056`** | ⚠⚠ **SQLite accepts a string primary key that Postgres rejects** | **NO** |

**`F-056` is the one that matters.** Measured:

```
SQLite:   session.get(ProteinAnalysis, "1970")   -> row found   (silently coerced)
SQLite:   session.get(ProteinAnalysis, "A0AVI2") -> None, no raise
Postgres: rejects both
```

**All 2,690 folded census cards were HTTP 500 in production while the suite was green.**
⚠⚠ **Not a coverage gap — the test substrate has different semantics from the thing it stands in
for, so no quantity of SQLite tests would have caught it.** The guard therefore asserts **what is
passed** — the resolved int, checkable on any engine — plus a second test recording the divergence
**so it reddens if SQLite ever tightens.** *A known divergence that silently disappears is a guard
whose premise expired without notice.*

---

## §3 — `F-058` — three guards, three resolutions, each inheriting the last one's unit

| guard | its unit | what it could not see |
|---|---|---|
| NC | one component | four other components |
| PA / PC3 | the component set | ⚠ which BRANCH renders the value |
| the branch fix | the branch | ⚠ unknown — *and that is the point* |

**Each remedy adopted the granularity of the level it was fixing, and the next defect lived one level
down.** ⚠⚠ **A guard inherits its unit from the defect that prompted it, and that defect is by
construction the coarsest one anybody had noticed.**

**The named check is one sentence: when writing a guard, state its unit and name the next finer unit
it cannot see.** *`PC3` would have said "file-level; cannot see branches," and `F-058` would have
been unnecessary.*

⚠ The instance: in `CensusDetail` the HPA citation sat **only** on the branch rendering **no** HPA
value, and was **absent** from the branch rendering `qh_score`. **The licence precondition was
satisfied only where there was nothing to satisfy it about.**

---

## §4 — What the owner found by looking, that no test did

⚠⚠ **Four defects reached production and were caught by a person reading the page.**

1. **`HER2` absent from the census** — the whole `F-054` chain started here.
2. **The 3D viewer's stand-aside** — `/census/A0AVI2` said *"structure -> HTTP 422"*. ⚠ The page
   requested `/api/analyses/**A0AVI2**/structure`, the **accession**. The structure was never
   missing; **the asset was named wrongly by the page asking for it.**
3. **Two links, identical text, different destinations** — `/pathology` and `/tissue`, both reading
   *"View this protein on the Human Protein Atlas (v22)."*
4. **`1 of 1 cell types`**, twenty-six times on one card.

⚠ **And "no change to LAMP1", said twice.** Both times I verified my copy fix was live and reported
it working; both times the owner was reporting that **the section still had no content**.
***I fixed the sentence when the defect was the section.*** ⚠⚠ **I took "no change" as a cache
question before I took it as a signal that I had fixed the wrong thing.**

---

## §5 — ⚠⚠ The recurring shape of MY errors today: verifying the property I built

**Three times, hours apart, I confirmed the thing I had implemented instead of the thing the reader
gets.**

| check that passed | what the reader got |
|---|---|
| `textContent` matched `/Image\/data credit:/` | **"IMAGE/DATA CREDIT:"** — CSS uppercased it |
| `distinctDeepLinks: 2` | **one sentence printed twice** — hrefs differed, labels did not |
| `hits`/`tumours` keys returned 79/79 | **guessed key names** — the measurement was an artefact |

⚠ **And the sharpest: `census (tranche > 0): 0`.** Not a measurement — **the join failing and
returning a plausible zero.** `metadata->>'gene'` is populated on **80 of 80 cohort rows and 0 of
2,691 census rows.** *"No census protein carries IHC in the uncounted indications" would have been a
clean, quotable, entirely false result.* ⚠⚠ **What caught it was the number being IMPOSSIBLE rather
than merely surprising** — `clinical_pathology` is row-scoped to the census manifest, so a census
count of zero contradicts the table's own definition.

**⚠ Two more of the same family:** a `.title()` lookup returning `"Breast Cancer"` and missing
`"Breast cancer"`, and `column pa.meta does not exist` where the column is `"metadata"`.
***Wrong-key joins, four times in one day, in code written after documenting the first one.***

---

## §6 — ⚠ Shell and string handling: seven incidents, one permanent

**Backticks, heredocs and escapes corrupted files seven times.** ⚠⚠ **The worst was invisible:**
`\b` passed through a Python heredoc became **literal backspace bytes**, three of them, and
`Read` renders a backspace as *nothing*. **Two were inside `UB3`, so the guard was GREEN BECAUSE IT
WAS BROKEN** — a regex containing a backspace matches nothing, so "no offenders" was
indistinguishable from success. **Only `cat -A` showed it.**

⚠ **One reached a permanent record:** nested heredocs put a PR body into a commit message
(`8da40fe`). **Amend and force-push are barred, so it stands** — the diff is correct, the subject
line is not.

**The standing rule held every time it was followed: ⚠⚠ never round-trip a file through the shell.**

---

## §7 — The LAMP1 arc, and how the numbers narrowed

**The owner's report — *"no cancer associations"* — ran through six stages, and every one made the
claim smaller:**

**20 categories → 3 sourced → 4 subtype-defining targets → UNDERPOWERED at n = 4.**

- The section was fed by an **82-row** source; HPA's `pathology.tsv` covers **15,313 genes**.
  ⚠ Two true statements, adjacent, producing a false impression — *neither statement's fault, and the
  surface's.*
- The HPA panels were **promoted census-wide** (`D-093` amendment 10's parent ruling).
- ⚠⚠ **`XE` sourced 3 of 20**; seventeen are `unknown_to_code` and **the marker renders nothing** for
  them.
- **`XF3`: the scorer is untouched, and that is ENFORCED** — but ⚠⚠ **it reaches the COMPARATOR**,
  which is `P-001`'s headline arm and bigger than the entry it was found in.
- **`P-001` amendment 2:** the pre-registered measurement returned the **third** outcome.

**⚠ The honest result is smaller than the concern that started it, and is recorded at that size.**

---

## §8 — ⚠⚠ Habits confirmed today, in the owner's words

- ***A stopping condition that removes the option beats one that forbids it.*** **Three members:** the
  read-only role · `§6`'s empty Group C · ⚠ **`_self_check` refusing its own author** over a
  semicolon in a comment he had just written. **The third is the purest.**
- ***Pre-register the branches you expect AND the sentence that permits a third.*** ⚠ **Twice in one
  week a two-branch pre-registration met a three-answer question** (`KB3`, then `YA`). The remedy is
  demonstrated, not proposed: **§4 permitting a third outcome in advance is the only reason the
  result landed as a result.**
- ***A pre-registration that MATCHES cannot distinguish "correctly anticipated" from "the data was
  never going to say otherwise."*** ⚠ At n = 4 no other answer was available.
- ⚠⚠ ***A correction patched away is a correction nobody can check.*** Today produced a **correction
  of a correction** (`hpa_composition_undocumented`: original → over-correction → reconciliation) and
  a **three-deep supersession chain**, all links preserved and hash-verified.

---

## §9 — ⚠ Where a gate caught the thing that created it

**`D-093` amendment 10 §4 required a citation for every marker. Building the marker found the one
claim in the ruling that lacked one:** §5's worked example read *"NECTIN4 **DEFINES** the
enfortumab-vedotin population."* ⚠⚠ **Not sourced.** The tree sources that an approved ADC **targets**
NECTIN4 (Padcev, BLA 761137) — **not that patients are selected by its expression.**

**The surface rendered only the sourced claim and REPORTED the divergence** rather than softening it
silently; the owner then amended §5, **original preserved.** ⚠ Its illustrative count was wrong too —
`8/12` against a rendered `11/12`.

---

## §10 — Open, with holders

| item | holder |
|---|---|
| ⚠⚠ **Decision 6 item (5)** — the verbatim attribution string | **TWO suppliers now**: HPA (open since 2026-08-19) and SEER. *A pattern rather than an exception* |
| **13 crosswalk rows blocked only by a fetch** | ⚠ SEER is public domain; nothing stands between them and an incidence figure but decision 6 |
| ⚠ **SEER is US-only** | a scope limit on every figure, not a footnote — **owner's ruling** |
| `WE1`'s folded-census split | needs the manifest's accession↔symbol map; **not answerable from the database** |
| `F-050` | still **RESERVED** for the guard-direction sweep |
| ⚠ `FGFR3` renders no marker | its ADC is clinical, not approved — *the four-target set and the marker set are deliberately different* |

**⚠ Numbers that will be re-derived wrongly if not read here first:**
- **The census is 2,690 folded of 3,467 manifest.** The cohort is **79 folded of 82**, and `/targets`
  shows **80 rows** because two members have no analysis row.
- **56 scored of 82** — the ranking's population, not the cohort's.
- ⚠⚠ **`hpa_composition_undocumented` is 20 of 20**, with **3** rows carrying a *partial* subtype
  statement. **My "HPA documents three" was an over-correction** and is recorded as one.
