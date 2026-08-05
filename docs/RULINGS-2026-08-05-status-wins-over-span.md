# RULINGS — 2026-08-05 — The retirement predicate, and the constant whose name was wrong for what it gates

> **COMMITTED 2026-08-05 with `### D-079` (`docs/README.md`). CITED BY the log, not restated in it —
> where this file and the log differ, THE LOG GOVERNS.** ⚠ This file is provenance for a decision that
> lives in the log; it is not itself authority. Check the `### D-079` header, not a reference to it.

> **Amends `RULINGS-2026-08-05-identity-status-collapse.md` §3 and `core/census.py`'s category set.
> Lands in #1's docs-only commit. Binding before Task 3.**
>
> **Raised by Code**, checkpoint 7, 2026-08-05. Both correct. ⚠ **The second is a live defect with a
> named blast radius: 52 proteins, 7 of them surface.** Verified by the Planner against the tree and
> the CSV on 2026-08-05.

---

## §1 — The collapse function executed clean, and that is recorded before anything else

Code implemented §2's rule including all three RAISE branches and ran it over all 7,811 proteins:
`active` **7,746** · `merged` **13** · `inactive` **52** · `multi` **0** · `unresolved` **0** ·
**RAISE branches fired: 0** · whole-roster eligible **7,759** · surface eligible **2,800**.

**Every expected figure reproduced.** The self-identifier audit confirms all four branches are
determined: `{1: 7734}`, `{1: 52}`, `{0: 13}`, `{1: 12}`. **P01889's self-identifier is `1B07_HUMAN`,
`active_reviewed`, surface**, with 34 non-self identifiers all `merged` — so the named test has a
real target and a majority rule genuinely returns something else.

---

## §2 — RULING: the retirement predicate is **exact string-literal equality**, and it needs no exception

Code is right that *"no `resolved` literal under `core/`, `scripts/`"* is unimplementable as written —
and right about why it matters: **whoever implements it will narrow it silently, which is an unstated
decision inside the guard against unstated decisions.** So the predicate is stated here, not left to
implementation.

**The predicate:** *no Python string literal **exactly equal** to `resolved` appears under `core/` or
`scripts/`.* Not substring. Not `startswith`.

**Verified by the Planner, 2026-08-05.** Under exact-literal matching there are **four** occurrences,
and they are precisely the four Code identified:

| Site | Occurrence |
|---|---|
| `core/census.py:97` | `(row.get("id_status") or "resolved")` — F-018 site |
| `scripts/ecd_lengths.py:128` | `... or "resolved"` — F-018 site |
| `scripts/census_spans.py:112` | `if row["id_status"] == "resolved"` — the gate |
| `scripts/accession_map.py:63` | `RESOLVED = "resolved"` — the constant |

**⚠ And no exception is required.** `resolved_on` is `"resolved_on"`; `unresolved` is `"unresolved"`;
`scripts/map_genes_to_uniprot.py:88` is `"resolved_primary"` — **a different vocabulary for a
different quantity, and not an exact match.** The prose hits at `core/enqueue.py:227`,
`core/scorer.py:333`, and `chunk_invariance_run.py` are comments about D-047 recipe resolution and are
not literals. **The predicate is zero-false-positive on today's tree; a whitelist would have been a
place for future silent narrowing and is not needed.**

**⚠ The test proves its own scope, in itself.** It asserts the four sites are gone **and** that a
fixture line containing `resolved_on` and `unresolved` does **not** trip it. Otherwise the next
person broadens it to a substring search, finds forty hits, and adds an allowlist — reproducing
exactly what this ruling avoided.

---

## §3 — RULING: `_IDENTITY_FAILURES` is renamed, because its name is wrong for what it gates

**The live defect.** `_IDENTITY_FAILURES = {MULTI, UNRESOLVED, OBSOLETE}`. `OBSOLETE` is deleted by
the previous ruling and `INACTIVE` is not a member. So the 52 ineligible proteins are never fetched,
carry `span_aa = None`, fall past the identity check, and land in `NO_TOPOLOGY` — **whose own comment
at `core/census.py:72` reads *"resolved identity, but no numeric ECD span."***

**That sentence would be false about all 52, including 7 surface targets.** ⚠ It is the contract
ruling's defect at reduced scale — **not an absence coerced low, but a category asserting a reason
the row did not have.** And Code is right that 7 rows in a 2,807-row band split is exactly the
magnitude that survives review, because the split would look entirely plausible.

### 3.1 — The rename

`_IDENTITY_FAILURES` → **`_STATUS_WINS_OVER_SPAN`.**

The old name forced the question *"is `inactive` an identity failure?"* — which is genuinely
arguable: the identity is known, the entry is withdrawn. **That argument is not the operative one.**
The operative question is *"does status decide this row instead of its span?"*, and for `inactive` the
answer is unambiguously yes. **A name that states its own rule dissolves the debate rather than
hosting it** — D-074's remedy, the same move that closed F-010 by rename.

**Members: `{multi, unresolved, inactive}` — exactly the complement of `fetch_eligible`.**
⚠ **`merged` is NOT a member:** 13 proteins, fetch-eligible, they have spans and are categorised by
them.

### 3.2 — The invariant this buys, and it is the durable half

> **⚠ `no_topology` requires a successful fetch. A row that was never fetched cannot be
> `no_topology`.**

*"No sliceable ECD span"* is a claim about the **protein**, and it can only be made after looking.
*"Never fetched"* is a claim about the **pipeline**. Because `_STATUS_WINS_OVER_SPAN` is exactly the
complement of `fetch_eligible`, status precedence now guarantees the invariant structurally rather
than by care.

### 3.3 — ⚠ One more conflation, in the same place, that will fire at census scale

`scripts/census_spans.py:117` rewrites `id_status` to `"unresolved"` on a fetch exception.

**A fetch failure is not an identity failure.** `unresolved` means *the entry name mapped to no
accession*; a network timeout means the accession was fine and the request was not. **At 82 rows this
never fired. At 2,807 fetches it will**, and each occurrence would record a false statement about the
identifier — while looking like a category the module already supports.

**Ruled: `FETCH_FAILED` becomes its own category.** `census_spans.py` stops rewriting `id_status`;
the failure is recorded as its own category with the error retained.

**The category set becomes:**
`LOCAL · RENTAL · OVER_CEILING · NO_TOPOLOGY · MULTI · UNRESOLVED · INACTIVE · FETCH_FAILED`
(**`OBSOLETE` deleted**).

⚠ This applies `core/census.py`'s own stated principle rather than adding one — its header already
says each category is *"a way of NOT knowing a cost, kept distinct because merging them would hide
which kind of ignorance applies."* **Three kinds of ignorance were sharing one bucket.**

### 3.4 — D-079's band vocabulary

D-079 dec 3's bands gain the ineligibility categories. **`no_topology` is reserved strictly for
fetch-eligible rows that were fetched and returned no sliceable span.** Every band split reports
`inactive` and `fetch_failed` as their own lines.

---

## §4 — Tests

| Test | Assertion | Prove it bites by |
|---|---|---|
| `test_the_literal_resolved_is_gone_and_the_predicate_is_exact` | Zero exact-`"resolved"` literals; a fixture with `resolved_on` + `unresolved` does **not** trip | Broadening to substring → red on the fixture |
| `test_inactive_is_categorised_inactive_not_no_topology` | An `inactive` row with `span_aa=None` → `inactive`. **Name one of the 7 surface proteins.** | Removing `inactive` from the constant → red **on that row** |
| `test_merged_is_categorised_by_its_span` | A `merged` row with a valid span → the envelope band, not a status category | Adding `merged` to the constant → red |
| `test_no_topology_requires_a_successful_fetch` | No row reaches `no_topology` without a recorded successful fetch | Reverting §3.2 → red |
| `test_fetch_failure_is_not_unresolved` | A seeded fetch exception → `fetch_failed`, and `id_status` is **unchanged** | Restoring the rewrite → red |
| `test_category_set_has_no_obsolete_and_the_split_is_exhaustive` | Categories == the eight; counts sum to row count | Dropping a category → red |

⚠ **The second test must name a specific surface protein.** A test over the 2,800 eligible rows
passes under both the bug and the fix — third time this session that a test needed a named row
(IGF2R, Q96PC5, P01889).

---

## §5 — Recorded

**Three sessions of rulings have now each exposed the next one**, and every defect has had the same
shape at a different altitude: a **category, name, or vocabulary asserting a reason the data did not
have.** `?? 0` coerced absence low. `no_topology` invented a reason. `unresolved` would have
mislabelled a network failure as an identity failure. **`_IDENTITY_FAILURES` hosted an argument
instead of stating a rule.**

⚠ **None of these were found by reading the documents.** All were found by Code executing the rule
against the real file — the collapse function ran clean, and the *running* is what surfaced the two
gaps that reading five documents had not. **Standing consequence, added: a ruling is not verified
until it has been executed against the real data, and "it reproduces on inspection" is not that.**
