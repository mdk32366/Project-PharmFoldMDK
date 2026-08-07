"""V2 span extraction — the ruled vocabulary, the GPI rule, and the coordinate category.

⚠ **This module is V2 ONLY and it is opt-in everywhere.** `scripts/ecd_lengths.py:parse()` is
untouched and still implements V1; `### D-081` freezes the 82 under V1 **permanently**, and the
frozen path must keep reproducing the old file byte for byte. **A shared code path between the two
definitions would make that impossible to guarantee**, so there is no shared code path — the
vocabulary lives in `core/span_definition.py` and the two extractors are separate.

⚠ **ABSENCE IS ALWAYS A CATEGORY WITH A CAUSE.** Never `0`, never a bare null, never a band that
means five things. Every row leaves here with either a span **and the rule that produced it**, or a
category **and the reason** — and the two are mutually exclusive by construction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from core.span_definition import (
    ABSENT_WITH_REASON, NO_EXTRACELLULAR_SPAN, RULE_GPI_A, RULE_GPI_B, RULE_VOCABULARY,
    SPAN_BOUNDARY_UNKNOWN, TERM_UNRULED, V2_RULED_VOCABULARY, classify_term,
)


@dataclass
class SpanResult:
    """One protein's span under V2. ⚠ `span_aa` and `category` never both carry a value."""
    span_aa: Optional[int] = None
    rule: str = ""
    category: str = ""
    reason: str = ""
    #: ⚠ The coordinate we DO have when the other end is UNKNOWN. Recorded, never completed.
    boundary_coordinate: str = ""
    terms_unruled: list[str] = field(default_factory=list)
    terms_held: list[str] = field(default_factory=list)
    definition: str = V2_RULED_VOCABULARY

    def __post_init__(self) -> None:
        if (self.span_aa is None) == (not self.category):
            raise ValueError(
                f"a SpanResult must carry exactly one of a span or a category, not both and not "
                f"neither: span_aa={self.span_aa!r} category={self.category!r}"
            )


def _features(data: dict, ftype: str) -> list[dict]:
    return [f for f in (data.get("features") or []) if f.get("type") == ftype]


def _bounds(feat: dict) -> tuple[Optional[int], Optional[int]]:
    loc = feat.get("location") or {}
    return (loc.get("start") or {}).get("value"), (loc.get("end") or {}).get("value")


def _location_repr(feat: dict) -> str:
    """⚠ The raw location, so `span_boundary_unknown` records what it does have. The artifact used
    to read `None-2009(None)` — a null stringified into something that still looks like a span."""
    loc = feat.get("location") or {}
    s, e = loc.get("start") or {}, loc.get("end") or {}
    return (f"start={s.get('value')}/{s.get('modifier')} end={e.get('value')}/{e.get('modifier')}")


def gpi_lipidation(data: dict) -> list[dict]:
    """⚠ The AUTHORITATIVE GPI test, and it is narrower than a substring scan for `gpi`.

    A GPI anchor is a `Lipidation` feature reading `GPI-anchor amidated <residue>`. A `Mutagenesis`
    of the anchor site or a `Region` that merely names it are **mentions of an anchor, not
    annotations of one** — counting those would be an absence coerced into an affirmative.
    """
    return [f for f in _features(data, "Lipidation")
            if "gpi-anchor" in (f.get("description", "") or "").lower()]


def mature_chain_bounds(data: dict) -> tuple[Optional[int], Optional[int]]:
    """`min(start)`, `max(end)` over every `Chain`.

    ⚠ **Not `Chain[0]`.** A proteolytically processed protein carries several `Chain` records, and
    taking the first produced a **negative** rule-A-minus-rule-B divergence on `P51654` during the
    pre-registration — an artifact of the pick, not a property of the data.
    """
    starts = [s for f in _features(data, "Chain") for s in (_bounds(f)[0],) if s is not None]
    ends = [e for f in _features(data, "Chain") for e in (_bounds(f)[1],) if e is not None]
    return (min(starts) if starts else None, max(ends) if ends else None)


def extract(data: dict) -> SpanResult:
    """One protein's V2 span. ⚠ Never raises on data shape — an absence is a named category.

    Precedence, and the order is load-bearing:

    1. **Vocabulary.** An accepted topological domain with computable coordinates wins outright.
    2. **GPI.** Only reached when no accepted domain produced a span — a GPI-anchored protein has
       no topology **by design**, so this is not a fallback for missing data, it is the correct
       rule for a different molecular architecture.
    3. **`span_boundary_unknown`.** An accepted term matched and the coordinate was `UNKNOWN`.
       ⚠ **Out of the bands and out of the foldable population**, because it is neither *no
       reachable domain* nor a usable span. **No coordinate is invented — not 1, not `Signal`+1.**
    4. **`term_unruled`.** A description outside accept/held/reject. Named, never guessed at.
    5. **`no_extracellular_span`.** The genuine absence, and now it means only that.
    """
    unruled: list[str] = []
    held: list[str] = []
    boundary: list[str] = []
    best: Optional[int] = None

    for f in _features(data, "Topological domain"):
        desc = f.get("description", "") or ""
        verdict = classify_term(desc)
        if verdict == "rejected":
            continue
        if verdict == "held":
            held.append(desc)
            continue
        if verdict == TERM_UNRULED:
            unruled.append(desc)
            continue
        s, e = _bounds(f)
        if s is None or e is None:
            # ⚠ The term MATCHED. What is missing is a coordinate, not a word.
            boundary.append(f"{desc}: {_location_repr(f)}")
            continue
        n = e - s + 1
        if best is None or n > best:
            best = n

    if best is not None:
        return SpanResult(span_aa=best, rule=RULE_VOCABULARY,
                          terms_unruled=unruled, terms_held=held)

    lip = gpi_lipidation(data)
    if lip:
        cs, ce = mature_chain_bounds(data)
        pos = _bounds(lip[0])[0]
        if cs is None:
            # ⚠ Named, never silently dropped from a denominator.
            return SpanResult(category=ABSENT_WITH_REASON,
                              reason="GPI-anchored but no `Chain` feature: mature chain start is "
                                     "unknown, so neither rule A nor rule B can be applied",
                              terms_unruled=unruled, terms_held=held)
        if pos is not None and pos - 1 >= cs:
            # Rule A — explicit about BOTH boundaries rather than trusting `Chain` to end correctly.
            # ⚠ It is primary for a measured reason: rule B over-reads on every protein where the
            # two diverge, because `Chain` runs through the C-terminal GPI signal that is cleaved
            # and replaced by the anchor — up to 266 residues on `Q96GW7`, and on three of six
            # divergent proteins that removed segment is not annotated anywhere.
            return SpanResult(span_aa=pos - cs, rule=RULE_GPI_A,
                              terms_unruled=unruled, terms_held=held)
        if ce is not None:
            return SpanResult(span_aa=ce - cs + 1, rule=RULE_GPI_B,
                              terms_unruled=unruled, terms_held=held)
        return SpanResult(category=ABSENT_WITH_REASON,
                          reason="GPI-anchored, `Lipidation` position unusable and `Chain` has no "
                                 "end: neither rule A nor rule B can be applied",
                          terms_unruled=unruled, terms_held=held)

    if boundary:
        return SpanResult(category=SPAN_BOUNDARY_UNKNOWN,
                          reason="an accepted topological domain matched and a coordinate is "
                                 "UNKNOWN; no coordinate is invented",
                          boundary_coordinate=" | ".join(boundary),
                          terms_unruled=unruled, terms_held=held)

    if unruled:
        return SpanResult(category=TERM_UNRULED,
                          reason="topological domain description(s) outside the ruled vocabulary: "
                                 + "; ".join(sorted(set(unruled))),
                          terms_unruled=unruled, terms_held=held)

    return SpanResult(category=NO_EXTRACELLULAR_SPAN,
                      reason="no topological domain with an accepted description, and no GPI anchor",
                      terms_unruled=unruled, terms_held=held)


def divergence(data: dict) -> Optional[tuple[int, int]]:
    """`(rule_A, rule_B)` for a GPI protein where both are computable, else `None`.

    ⚠ **A check on the rule, never an input to it.** Rule B fires only when `Lipidation` is absent,
    so wherever this returns two numbers, the one actually used is A. A divergence of much more than
    a residue is a `Chain` annotation that does not mean what was assumed — and it is a finding.
    """
    lip = gpi_lipidation(data)
    if not lip:
        return None
    cs, ce = mature_chain_bounds(data)
    pos = _bounds(lip[0])[0]
    if cs is None or ce is None or pos is None:
        return None
    return (pos - cs, ce - cs + 1)


def as_row(result: SpanResult) -> dict[str, Any]:
    """The flat output shape. ⚠ An empty string is the ABSENT marker; `0` is never written."""
    return {
        "span_aa": result.span_aa if result.span_aa is not None else "",
        "span_rule": result.rule,
        "span_category": result.category,
        "no_span_reason": result.reason,
        "span_boundary_coordinate": result.boundary_coordinate,
        "terms_unruled": ";".join(sorted(set(result.terms_unruled))),
        "terms_held": ";".join(sorted(set(result.terms_held))),
        "parsed_under": result.definition,
    }
