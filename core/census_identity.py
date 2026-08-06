"""The census identity vocabulary — ONE constant, imported by every site that reads it.

⚠ F-018. Before this module the string vocabulary lived in three places that agreed *by
convention*: `core/census.py`, `scripts/ecd_lengths.py` and `scripts/census_spans.py`. Two of them
defaulted a missing status to `"resolved"` — **an absent status silently becoming an affirmative
one**, which is the absent-value rule violated in the *passing* direction. Any CSV lacking a status
column would have had every row treated as resolved.

⚠ `"resolved"` IS RETIRED, from the vocabulary and from the codebase. It was the exact string behind
those defaults, so retiring it means a surviving `or "resolved"` now **fails the vocabulary check
loudly** instead of passing silently. The defect stops being something a reviewer must notice and
becomes something the constant rejects.

⚠ `"obsolete"` IS DELETED — it was an invented synonym for a state UniProt already names. We do not
create a second name for a thing the source names; that is the two-paths class arriving through a
glossary. `inactive` is UniProt's word and it is now ours.

**Measured composition on `membraneome-reconstructed-2026-08-04.csv`, 2026-08-06:**
`active` 7,746 · `merged` 13 · `inactive` 52 = 7,811. `multi` 0 and `unresolved` 0, **asserted empty,
never left absent** — an empty bucket is a finding; a missing key is an unanswered question wearing
the same clothes.
"""

from __future__ import annotations

#: The operational identity vocabulary. ⚠ Consumed by `core/census.py`, `scripts/ecd_lengths.py`
#: and `scripts/census_spans.py`. No site holds a literal status string.
CENSUS_IDENTITY_STATUS: tuple[str, ...] = ("active", "merged", "inactive", "multi", "unresolved")

#: ⚠ Status wins over span. Named for the rule it encodes, not for the argument it used to host.
#: The old name `_IDENTITY_FAILURES` forced the question *"is `inactive` an identity failure?"* —
#: genuinely arguable, since the identity is known and the entry is withdrawn. That argument is not
#: the operative one. The operative question is *"does status decide this row instead of its span?"*,
#: and for `inactive` that is unambiguous. A name that states its own rule dissolves the debate
#: rather than hosting it (D-074; the same move that closed F-010 by rename).
#:
#: ⚠ Exactly the complement of `fetch_eligible`, and that is what buys the invariant below:
#: **`no_topology` requires a successful fetch.** "No sliceable ECD span" is a claim about the
#: protein and can only be made after looking; "never fetched" is a claim about the pipeline.
STATUS_WINS_OVER_SPAN: frozenset[str] = frozenset({"multi", "unresolved", "inactive"})

#: Fetchable identities. `merged` is NOT a failure: 13 proteins, present only by inheritance, with
#: no SURFY entry that is itself the current accession — they have spans and are categorised by them.
FETCH_ELIGIBLE_STATUS: frozenset[str] = frozenset({"active", "merged"})

#: An absent value is a CATEGORY with a cause, never a bare `false`.
FETCH_INELIGIBLE_REASON: dict[str, str] = {
    "inactive": "uniprot_inactive",
    "multi": "identity_not_established_multi",
    "unresolved": "identity_not_established",
}

#: The verification axis. ⚠ A FINDING, and it NEVER gates a fetch. `disagrees` is a fact about our
#: sources, not a statement that a protein is unfetchable — if it gated the pipeline a disagreement
#: would silently shrink the census, which is the F-009 error arriving through a column name.
VERIFICATION_BUCKET: tuple[str, ...] = (
    "agrees", "source_only", "uniprot_only", "disagrees", "unresolvable",
)


class UnknownIdentityStatus(ValueError):
    """A status outside `CENSUS_IDENTITY_STATUS`. ⚠ Raised, never defaulted.

    An absent status becoming an affirmative one is the F-018 defect, and **a different default is
    the same defect at a different value** — which is why the fix deletes the default rather than
    correcting it.
    """


def require_status(value: object) -> str:
    """Return `value` if it is a known status; raise otherwise. ⚠ There is no default branch."""
    if value in CENSUS_IDENTITY_STATUS:
        return str(value)
    raise UnknownIdentityStatus(
        f"unknown census identity status {value!r}; expected one of {CENSUS_IDENTITY_STATUS}. "
        f"⚠ An absent or unrecognised status is NEVER coerced to an affirmative one (F-018) — "
        f"note that 'resolved' is retired and will land here."
    )


def fetch_eligible(status: str) -> bool:
    """Whether this identity can be fetched. Validates first — an unknown status raises."""
    return require_status(status) in FETCH_ELIGIBLE_STATUS
