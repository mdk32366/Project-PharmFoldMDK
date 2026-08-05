"""The surfaceome census cost split (surfaceome-spans-v2 §2-§3).

`core/foldability.py` answers "where does a target of span N fold?". This answers
the same question for a **census**, where two things go wrong that never went
wrong for a curated 82 — and both go wrong in the direction of making the census
look cheaper than it is:

  **Identifiers fail.** At census scale some entry names resolve to nothing and
  some to several. An identifier the pipeline could not resolve is not a free
  target; it is an unknown. `multi` and `unresolved` flow through as their own
  counts and are never dropped — a cost model that silently excludes what it
  could not resolve is understating the census.

  **Topology is often absent.** ~16% of the 82 had no sliceable ECD span. A
  silent `0` classifies every unsliceable target as trivially free. That is the
  `?? 0` defect `TargetList.jsx` already records, in a new place, and it is the
  reason `no_topology` is a category rather than a length.

═══════════════════════════════════════════════════════════════════════════════
⚠ MEASURED, NEVER SCALED — the refusal that is specific to this module
═══════════════════════════════════════════════════════════════════════════════

The 82's split is an **expression-filtered sample**, not a random draw from the
surfaceome. Multiplying its proportions by a census size would produce a
confident-looking number about a population it was never drawn from. **There is
no code path here that takes a ratio and a total**, and a test asserts there is
none — because the extrapolation would look like a helpful convenience at exactly
the moment someone wants a headline and does not yet have the spans.

Counts come from spans that were actually measured, or they do not come.

═══════════════════════════════════════════════════════════════════════════════
⚠ AND THE RULINGS INHERITED FROM D-077 DECISION 1, WHICH BIND HERE TOO
═══════════════════════════════════════════════════════════════════════════════

1. **This MUST NOT become a model feature.** Local-foldability is a monotone step
   function of ECD length, which is feature 1 of the pre-registered six (D-027).
   A test asserts `core/scorer.py` and `core/features.py` import neither this
   module nor `core/foldability.py`.
2. **It MUST NOT sit beside suitability without its label.** This is a **cost /
   tractability / reproducibility** axis. It says what a target costs to
   *compute* and **nothing** about whether it is a good ADC target.
3. **It MUST NOT filter the census.** A census that silently drops the targets it
   cannot afford to fold is a census of *our budget*, biased by length — the
   F-009 error one level out. Unaffordable rows stay in, flagged.

⟡ **The annex is not the census** (F-011). SURFY-negative rows are ingested and
flagged, never ranked, and a cost figure that silently merges annex and census
members is wrong in both directions. Callers split them before counting; this
module counts what it is given and does not know the difference.

The ceiling comes from `core.manifest.LOCAL_CEILING`, which carries the recipe it
was measured under. No ceiling literal and no census-size literal appear here;
tests fail if either does.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping

from core.foldability import LOCAL, OVER_CEILING, RENTAL, envelope
from core.manifest import LOCAL_CEILING, FoldCeiling

# Cost categories, re-exported from foldability so there is one vocabulary.
LOCAL = LOCAL
RENTAL = RENTAL
OVER_CEILING = OVER_CEILING

# Census-scale categories. Each is a way of NOT knowing a cost, kept distinct
# because merging them would hide which kind of ignorance applies.
NO_TOPOLOGY = "no_topology"     # resolved identity, but no numeric ECD span
MULTI = "multi"                 # entry name mapped to several accessions
UNRESOLVED = "unresolved"       # entry name mapped to none
OBSOLETE = "obsolete"           # accession withdrawn upstream

CATEGORIES = (LOCAL, RENTAL, OVER_CEILING, NO_TOPOLOGY, MULTI, UNRESOLVED, OBSOLETE)

# Identity statuses that are answers about the IDENTIFIER, not about the protein.
# They win over any span, because counting such a row by its span would assert an
# identity the mapping step explicitly declined to make.
_IDENTITY_FAILURES = {MULTI: MULTI, UNRESOLVED: UNRESOLVED, OBSOLETE: OBSOLETE}


def categorise(row: Mapping[str, Any], ceiling: FoldCeiling = LOCAL_CEILING) -> str:
    """The category for one census row. Order of precedence is the whole design.

    A row is `{"span_aa": int | None, "id_status": str}` (other keys ignored).

    1. **Identity failure wins.** `multi` / `unresolved` / `obsolete` are facts
       about the identifier. A `multi` row carrying a span is still `multi`.
    2. **Absent span is `no_topology`**, never 0 and never `local`. A span of 0 is
       treated the same way — a zero-length ECD is not a free fold, it is a
       measurement that did not happen.
    3. Otherwise the D-077 envelope, at the measured recipe.
    """
    status = (row.get("id_status") or "resolved").strip().lower()
    if status in _IDENTITY_FAILURES:
        return _IDENTITY_FAILURES[status]

    span = row.get("span_aa")
    if span is None or not isinstance(span, int) or span <= 0:
        return NO_TOPOLOGY

    return envelope(span, ceiling=ceiling)


def census_split(rows: Iterable[Mapping[str, Any]],
                 ceiling: FoldCeiling = LOCAL_CEILING) -> dict[str, int]:
    """Count a census by category. Exhaustive and conservative.

    Every row lands in exactly one category and the counts sum to the number of
    rows, so nothing can vanish from a cost estimate and nothing can be invented.

    ⚠ Counts what it is GIVEN. It does not filter, and callers must not use it to
    filter (refusal 3 above).
    """
    counts = Counter(categorise(r, ceiling) for r in rows)
    return {category: counts.get(category, 0) for category in CATEGORIES}


def describe_split(counts: Mapping[str, int], ceiling: FoldCeiling = LOCAL_CEILING,
                   source: str | None = None, source_date: str | None = None) -> str:
    """A one-screen summary that names the ceiling recipe, the source and the date.

    ⚠ The artifact names the ceiling that produced it, or two versions circulate
    with no way to tell which is current. A cost claim without its recipe is not
    checkable — the same span is affordable at int8 and not at fp16.
    """
    from core.foldability import describe

    measured = counts[LOCAL] + counts[RENTAL] + counts[OVER_CEILING]
    unknown = counts[NO_TOPOLOGY] + counts[MULTI] + counts[UNRESOLVED] + counts[OBSOLETE]

    lines = [
        f"ceiling      : {describe(ceiling)}",
        f"source       : {source or 'UNRECORDED'}",
        f"source date  : {source_date or 'UNRECORDED'}",
        "",
        f"  {LOCAL:<13} {counts[LOCAL]:>6}   inside the measured local envelope",
        f"  {RENTAL:<13} {counts[RENTAL]:>6}   needs rented compute",
        f"  {OVER_CEILING:<13} {counts[OVER_CEILING]:>6}   over every single-card ceiling",
        f"  {'-' * 13} {'-' * 6}",
        f"  {'costed':<13} {measured:>6}",
        "",
        f"  {NO_TOPOLOGY:<13} {counts[NO_TOPOLOGY]:>6}   no numeric ECD span (NOT free)",
        f"  {MULTI:<13} {counts[MULTI]:>6}   entry name -> several accessions",
        f"  {UNRESOLVED:<13} {counts[UNRESOLVED]:>6}   entry name -> none",
        f"  {OBSOLETE:<13} {counts[OBSOLETE]:>6}   accession withdrawn upstream",
        f"  {'-' * 13} {'-' * 6}",
        f"  {'uncosted':<13} {unknown:>6}",
        "",
        f"  total        {measured + unknown:>6}",
        "",
        "  ** Cost axis only. Not suitability. Not a census filter. Never scaled from a sample.",
    ]
    return "\n".join(lines)
