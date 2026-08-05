# RULINGS — 2026-08-05 — The collapse function for `census_identity_status`, and the vocabulary that could not express one of its own populations

> **COMMITTED 2026-08-05 with `### D-079` (`docs/README.md`). CITED BY the log, not restated in it —
> where this file and the log differ, THE LOG GOVERNS.** ⚠ This file is provenance for a decision that
> lives in the log; it is not itself authority. Check the `### D-079` header, not a reference to it.

> **Amends `SPEC-2026-08-05-accession-map-schema.md` §3.2 and §4.2. Lands in #1's docs-only commit.**
> **Binding before Task 2 emits a roster row.**
>
> **Raised by Code**, checkpoint 6, 2026-08-05: *"§2 answered 'what is a row.' It didn't answer what
> happens to a column when N rows become one"* — and separately, that `inactive` has no member in the
> vocabulary the spec fixed. **Both correct. Both Planner defects.** Verified by the Planner against
> `membraneome-reconstructed-2026-08-04.csv` (sha256 `5a705cc9…`) on 2026-08-05.

---

## §1 — ⚠ Gap 2 first, because it is the worse one

`SPEC` §3.2 fixed `census_identity_status` at `resolved · merged · multi · obsolete · unresolved`.
The CSV's `uniprot_status` is `active_reviewed · merged · inactive`. **`inactive` maps to no member.**

§4.2 makes that vocabulary a single constant which **all three sites refuse an unrecognised value
against**. So as written, **the producer cannot emit a legal value for 52 proteins** — and the likely
response would be to quietly pick `obsolete` or `unresolved`.

**⚠ That is the `or "resolved"` defect wearing a different value, inside the constant written to
prevent it.** Code's read is exact and the shape is worth naming: **the guard was specified before
the vocabulary it guards was checked against its own data.**

### Ruling — the vocabulary is replaced, and `resolved` is RETIRED

**New vocabulary: `active` · `merged` · `inactive` · `multi` · `unresolved`.**

Two changes and each has a reason beyond tidiness:

1. **`obsolete` is deleted.** It was an invented synonym for a state UniProt already names. ⚠ **We do
   not create a second name for a thing the source names** — that is the two-paths class arriving
   through a glossary. `inactive` is UniProt's word and it is now ours.
2. **⚠ `resolved` is retired from the vocabulary and from the codebase.** It is the exact string
   behind F-018's `or "resolved"` default, at all three sites. Retiring it means **a surviving
   `or "resolved"` anywhere now fails the vocabulary check loudly** instead of passing silently.
   The defect stops being something a reviewer must notice and becomes something the constant
   rejects. **F-018's fix is strengthened by the rename, not merely accompanied by it.**

**Measured composition** (Planner, off the file, 2026-08-05): `active` **7,746** · `merged` **13** ·
`inactive` **52** = **7,811**. `multi` **0** and `unresolved` **0** — ⚠ **asserted empty, never left
blank.** An empty bucket is a finding; a missing key is an unanswered question wearing the same
clothes.

---

## §2 — Gap 1: the collapse function, and it is fully determined by the data

Code declined to infer a rule and was right to. Here is the rule, and the measurement showing it is
determined rather than chosen.

**Protein-level status signatures** (Planner, verified 2026-08-05, 7,811 proteins):

| Signature | Proteins | Self-identifier present? |
|---|---|---|
| `(active_reviewed,)` | 7,734 | yes |
| `(active_reviewed, merged)` | **12** | **all 12 have exactly one, and it is `active_reviewed`** |
| `(merged,)` | 13 | **zero of 13** |
| `(inactive,)` | 52 | yes — all 52 are singletons, `current == source` |

**Definition.** The **self-identifier** of a protein is the source row whose `source_accession`
equals the roster row's `census_accession` — the identifier that *names* the protein rather than
merely reaching it.

### Ruling — `census_identity_status` is the status of the self-identifier, or `merged` if there is none

```
exactly one self-identifier, active_reviewed   → active
exactly one self-identifier, inactive          → inactive
exactly one self-identifier, merged            → RAISE   (an accession merged into itself)
zero self-identifiers, all sources merged      → merged
zero self-identifiers, any other mixture       → RAISE
more than one self-identifier                  → RAISE
```

**Why this rule and not a majority or a precedence order.** ⚠ **A majority rule would make HLA-B
`merged` on the strength of 34 identifiers that are not it.** The merge is a fact about the
*identifiers*, and it is already fully preserved — losslessly — in `source_identifiers`. **The
protein's identity status is a fact about the protein, established by the identifier that names it.**
Code reached the same reading and correctly declined to enact it; this ruling enacts it.

**⚠ `merged` at protein grain is a real and distinct state, not a leftover.** The 13 all-merged
proteins have **no** self-identifier: they are present in the census *only* by inheritance, with no
SURFY entry that is itself the current accession. That is worth carrying, and it is why the rule does
not simply collapse everything to `active`.

**⚠ The three `RAISE` branches are not defensive decoration.** They are the whole point of stating a
rule rather than describing today's data. **None of the three occurs in the current file** — that is
measured, not assumed — and if a future UniProt release produces one, it must stop the pipeline, not
be absorbed. **A collapse function with no unrepresentable input is a default in disguise.**

---

## §3 — `fetch_eligible`, derived from the vocabulary, with the counts Code asked for

```
fetch_eligible = census_identity_status in {active, merged}
```

| Status | Eligible | `fetch_ineligible_reason` |
|---|---|---|
| `active` · `merged` | true | — |
| `inactive` | false | `uniprot_inactive` |
| `multi` | false | `identity_not_established_multi` |
| `unresolved` | false | `identity_not_established` |

**Expected eligible counts, derived and pinned:**

- **Whole roster: 7,811 − 52 = 7,759.**
- **⚠ Surface census: 2,807 − 7 = 2,800.** Seven of the 52 wholly-inactive proteins are surface —
  Code's number, reproduced by the Planner off the file.

**These are known before Task 2 runs**, because they depend only on `uniprot_status`. Verification-
driven ineligibility (`multi` / `unresolved`) is not known until Task 2 executes and is expected to
be zero.

⚠ **Pin 2,800 in the test with its derivation stated.** The membraneome parity test already
establishes why: *a test comparing two files only to each other stays green while both drift
together.* If upstream data changes and 2,800 moves, **that is a finding to be read, not a test to be
updated.**

| Test | Assertion | Prove it bites by |
|---|---|---|
| `test_identity_status_vocabulary_has_no_orphan_source_state` | Every distinct `uniprot_status` in the CSV maps to a declared member | Removing `inactive` from the constant → red |
| `test_the_string_resolved_appears_nowhere` | No `"resolved"` literal under `core/`, `scripts/` | Re-introducing `or "resolved"` → red |
| `test_collapse_uses_the_self_identifier_not_the_majority` | **P01889 → `active`**, on a protein whose 34 other identifiers are `merged` | A majority rule → red **on that row**, not on the 7,734 |
| `test_all_merged_protein_is_merged` | One of the 13 → `merged` | Collapsing to `active` → red |
| `test_each_raise_branch_raises` | Three synthetic fixtures, one per branch | Returning a value instead → red **at the assertion** |
| `test_no_raise_branch_fires_on_the_real_file` | All 7,811 collapse without raising; counts are 7,746 / 13 / 52 | Any drift → red |
| `test_surface_eligible_is_2800` | Derived from status, not typed as a bare literal | An eligibility rule change → red |

⚠ **`test_collapse_uses_the_self_identifier_not_the_majority` must name P01889.** A test over the
7,734 unanimous proteins passes under both rules — the same reason F-010's test had to name IGF2R and
the collision test had to name Q96PC5.

---

## §4 — Recorded

**Two defects, one shape.** The spec gave a **grain** and a **vocabulary** and no **collapse
function** — so the moment N rows became one, the column's value was an unstated inference. And the
vocabulary itself had never been checked against the data it would have to describe.

⚠ **The spec was written to end a distributed schema, and it introduced two new gaps of exactly the
kind it was closing** — both at the seam between what a document declares and what the data actually
contains. **Neither would have been caught by re-reading the spec.** Both were caught by Code doing
the thing §4 of the spec exists to force: **trying to make the constant express the real file.**

**Standing consequence, added to the amendment's:** a spec that declares a vocabulary must state the
**counts of the real data under each member** in the same document. A vocabulary with no measured
population is a hypothesis, and one of its members will turn out to be empty or missing.
