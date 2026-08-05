# RULINGS — 2026-08-05 — The fixture's legibility belongs to the assertion, and prose that restates a vocabulary is a second copy

> **COMMITTED 2026-08-05 with `### D-079` (`docs/README.md`). CITED BY the log, not restated in it —
> where this file and the log differ, THE LOG GOVERNS.** ⚠ This file is provenance for a decision that
> lives in the log; it is not itself authority. Check the `### D-079` header, not a reference to it.

> **Amends `RULINGS-2026-08-05-status-wins-over-span.md` §4 and folds into F-018's fix.**
> **Lands in #1's docs-only commit.**
>
> **Raised by Code**, checkpoint 8, 2026-08-05: the AST verification of the predicate, a proposed
> fixture, and four prose sites carrying retired vocabulary. **The prose point is correct and is the
> D-062 shape.**

---

## §1 — The AST verification, recorded

Code walked every `ast.Constant` string node under `core/` and `scripts/`: **4 exact matches — the
four named sites — and 22 near misses, none exact.** ⚠ **The predicate was verified by the predicate
as stated, not by a proxy for it**, which is the distinction §2 of the prior ruling existed to
protect. `resolved_primary` is a genuine near-miss and correctly untouched.

---

## §2 — RULING: the test's legibility is a property of the **assertion**, not of the fixture's fame

Code proposed `P33765 / ADORA3` — *"a recognizable GPCR, so a reader can see at a glance that the row
is a real surface protein correctly categorised inactive."* **The judgement is reasonable and the
reasoning inverts.**

⚠ **ADORA3 is a seven-transmembrane receptor whose extracellular portions are short loops.** Under
the bug it lands in `no_topology` — and for a GPCR **that looks entirely plausible.** A fixture whose
*wrong* answer is believable is the weakest of the seven for legibility, not the strongest. This is
the same property that made IGF2R the right F-010 fixture and the 2,800 eligible rows the wrong one:
**choose the row where the bug is visible, not the row that is recognisable.**

**But the deeper fix is to stop the test depending on that at all.**

### Ruled

1. **The assertion carries the meaning.** The test asserts **category `inactive` AND
   `fetch_ineligible_reason == uniprot_inactive`** — not the category alone. A failure then reads
   *expected `inactive`/`uniprot_inactive`, got `no_topology`*, which explains itself regardless of
   which protein is in the fixture.
2. **Two fixtures, parameterised** — near-zero cost, and it covers both shapes:
   - **`P33765` (ADORA3)** — ratified, the case where the wrong answer looks plausible.
   - **`Q5VU13` (VSIG8)** — the case where it does not. ⚠ **Code verifies the topology annotation
     before relying on that characterisation; the Planner has no UniProt access this session and is
     not asserting it as measured.** If it does not hold, pick another of the seven on the stated
     criterion and record which and why.
3. **All seven are singletons** (`n_ident=1`, `current == source`), so any is mechanically clean —
   Code's check, and it is what makes the choice a legibility question rather than a correctness one.

---

## §3 — RULING: prose that restates a vocabulary **cites the constant instead**

Code found four sites where retired vocabulary survives in prose:

| Site | Carries |
|---|---|
| `core/census.py:86` — `categorise()` docstring | *"multi / unresolved / obsolete are facts about the identifier"* |
| `scripts/ecd_lengths.py:115` | *"multi, unresolved and obsolete flow through"* |
| `scripts/accession_map.py:2` | *"FOUR BUCKETS: resolved · obsolete · multi · unresolved"* |
| `core/census.py:72` | `NO_TOPOLOGY = "no_topology"  # resolved identity, but no numeric ECD span` |

**The first is the exact docstring the amendment §4 already named** — *a precedence rule that stops
firing because its vocabulary moved, while its docstring goes on asserting it.* ⚠ **After the fix it
becomes the mirror image: the rule fires correctly and the docstring describes the vocabulary it had
before.** The defect does not close; it inverts.

**⚠ The fourth is wrong in two independent ways, and Code's read is exactly right.** It names a
retired member (`resolved`) **and** describes a condition that is no longer the operative one. Under
§3.2's invariant — *`no_topology` requires a successful fetch* — the correct phrasing is
**"fetched successfully, but no sliceable ECD span."** The old wording asserts something about
identity where the new rule asserts something about the fetch.

### Ruled

1. **Folded into F-018's fix**, as Code recommends. **Not a fifth document.** The fix is not complete
   while the strings the next reader will treat as the vocabulary still name the old one.
2. **⚠ Docstrings and comments do not restate the vocabulary — they cite the constant.**
   `categorise()`'s docstring says *"members of `_STATUS_WINS_OVER_SPAN` win over any span"* and does
   **not** list them. This is the standing consequence from the D-079 amendment — *where two sections
   name the same quantity, one cites the other rather than restating it* — applied to code prose,
   which is where it has now failed twice.
3. **`NO_TOPOLOGY`'s comment is rewritten to the invariant**, not merely to the new member names.

| Test | Assertion | Prove it bites by |
|---|---|---|
| `test_no_docstring_restates_the_status_vocabulary` | No module docstring or function docstring under `core/`/`scripts/` contains a member name of the status vocabulary, except the constant's own definition site | Re-listing the members in `categorise()`'s docstring → red |
| `test_no_retired_member_survives_anywhere` | `obsolete` appears nowhere as a status name, in code **or** prose | Restoring any of the four sites → red |

⚠ **The first test is deliberately stricter than removing `obsolete`.** Removing the retired words
fixes today's four sites and leaves the mechanism — a hand-maintained second copy — fully intact.
**A vocabulary listed in prose will drift again on the next rename, and the next rename is already
scheduled if `multi` or `unresolved` ever turn out non-empty.**

---

## §4 — Recorded

**This is D-062's shape at the level of a comment: the reference outlives the thing.** D-062 was
thirteen citations to entries that did not exist; this is four descriptions of a vocabulary that no
longer exists. ⚠ **Same defect, one altitude down, and it was invisible to the AST predicate by
construction** — the predicate was right to ignore docstrings, and being right about scope is exactly
what left this uncovered.

**A guard that is correctly scoped still leaves everything outside its scope unguarded, and the
correctness of the scoping is not evidence that the outside is clean.**
