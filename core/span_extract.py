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
    ABSENT_WITH_REASON, GUARD_CHAIN_OVERRUNS_ANCHOR, GUARD_CHAIN_START_AMBIGUOUS,
    GUARD_CHAIN_SHORTER_THAN_LONGEST, NO_EXTRACELLULAR_SPAN,
    REASON_GPI_NO_CHAIN, REASON_GPI_NO_CHAIN_SPANS_ANCHOR,
    REASON_GPI_POSITION_UNANNOTATED, RULE_GPI_A,
    RULE_VOCABULARY, SPAN_BOUNDARY_UNKNOWN, TERM_UNRULED, V2_RULED_VOCABULARY, classify_term,
)


@dataclass
class SpanResult:
    """One protein's span under V2. ⚠ `span_aa` and `category` never both carry a value."""
    span_aa: Optional[int] = None
    #: ⚠ THE COORDINATES, not just the length. A length cannot slice a sequence — `core/manifest.py`
    #: has carried `ecd_start`/`ecd_end` for the 82 since D-024, and the census manifest was built
    #: with only `span_aa`, which means nothing downstream could actually have cut anything from it.
    span_start: Optional[int] = None
    span_end: Optional[int] = None
    rule: str = ""
    category: str = ""
    reason: str = ""
    #: ⚠ The coordinate we DO have when the other end is UNKNOWN. Recorded, never completed.
    boundary_coordinate: str = ""
    terms_unruled: list[str] = field(default_factory=list)
    terms_held: list[str] = field(default_factory=list)
    #: ⚠ Guards that FIRED on this row. A flag is not an error — it is a row a human should look at,
    #: carried on the artifact so nobody has to remember to re-run a check.
    guards: list[str] = field(default_factory=list)
    definition: str = V2_RULED_VOCABULARY

    def __post_init__(self) -> None:
        if self.span_aa is not None and (self.span_start is None or self.span_end is None):
            raise ValueError(
                f"a span without coordinates cannot be sliced: span_aa={self.span_aa!r} "
                f"start={self.span_start!r} end={self.span_end!r}")
        if self.span_aa is not None and self.span_end - self.span_start + 1 != self.span_aa:
            raise ValueError(
                f"the coordinates do not reconcile with the length: "
                f"{self.span_start}-{self.span_end} is not {self.span_aa} aa")
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
    """`min(start)`, `max(end)` over every `Chain`. ⚠ DIAGNOSTIC ONLY — see `divergence`.

    ⚠ **This is NOT the span selector and must never be used as one.** It was, and on `Q13421`
    MSLN it produced a 561 aa span carrying ~250 residues of the megakaryocyte-potentiating factor,
    which is cleaved off and secreted. `mature_chain_at_anchor` is the selector.
    """
    starts = [s for f in _features(data, "Chain") for s in (_bounds(f)[0],) if s is not None]
    ends = [e for f in _features(data, "Chain") for e in (_bounds(f)[1],) if e is not None]
    return (min(starts) if starts else None, max(ends) if ends else None)


def mature_chain_at_anchor(data: dict, anchor: Optional[int]) -> tuple[Optional[int], str, float]:
    """`(start, "", ratio)` of the mature GPI chain, or `(None, reason, 1.0)`.

    ⚠ **The chains that CONTAIN the anchor; among them, the LATEST start.** A GPI anchor is attached
    to a residue *inside* the mature chain, so containment — not a coincident end — is the test that
    a chain is the anchored species.

    ⚠ **This corrects a first ruling that tested for a coincident END.** That version excluded
    `P06731` CEACAM5 — chain 35-685, anchor 676 — on a nine-residue mismatch at a boundary rule A
    never reads. **A clinically-validated ADC target, dropped on annotation form rather than on
    biology.**

    ⚠ **Latest start can only under-read.** Where UniProt annotates both `Mesothelin` 37-598 and
    `Mesothelin, cleaved form` 296-598, it is asserting that 37-295 *can be removed* — so those
    residues are not reliably on the surface, and folding them would be folding something that is
    not there. On MSLN this lands on 296-597: the mature form the ADCs bind.

    The returned `ratio` is selected-span ÷ longest-candidate-span, recorded rather than thresholded.
    """
    if anchor is None:
        return None, REASON_GPI_POSITION_UNANNOTATED, 1.0
    starts = [s for s, e in ((_bounds(c)) for c in _features(data, "Chain"))
              if s is not None and e is not None and s <= anchor <= e]
    if not starts:
        return None, REASON_GPI_NO_CHAIN_SPANS_ANCHOR, 1.0
    selected, longest = anchor - max(starts), anchor - min(starts)
    return max(starts), "", (selected / longest if longest else 1.0)


def _chain_starts_disagree(data: dict) -> bool:
    """⚠ More than one `Chain` with DIFFERENT starts — the mature N-terminus is ambiguous."""
    starts = {b for b in (_bounds(f)[0] for f in _features(data, "Chain")) if b is not None}
    return len(starts) > 1


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
    best_bounds: tuple[Optional[int], Optional[int]] = (None, None)

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
            best, best_bounds = n, (s, e)

    if best is not None:
        return SpanResult(span_aa=best, span_start=best_bounds[0], span_end=best_bounds[1],
                          rule=RULE_VOCABULARY, terms_unruled=unruled, terms_held=held)

    lip = gpi_lipidation(data)
    if lip:
        pos = _bounds(lip[0])[0]
        guards: list[str] = []
        if _chain_starts_disagree(data):
            # ⚠ KEPT LIVE. This guard is what caught the MSLN over-read; it stays on the artifact
            # after the fix so a `Chain` set the selector does not explain is still visible.
            guards.append(GUARD_CHAIN_START_AMBIGUOUS)
        _, ce_all = mature_chain_bounds(data)
        if ce_all is not None and pos is not None and ce_all - pos > 1:
            # ⚠ EVALUATED BEFORE THE SELECTOR, DELIBERATELY. This guard is what barred rule B, and
            # the rows it was built for are exactly the ones the selector now EXCLUDES. If it ran
            # after, it would stop watching them at the moment they became interesting.
            guards.append(GUARD_CHAIN_OVERRUNS_ANCHOR)
        if not _features(data, "Chain"):
            return SpanResult(category=ABSENT_WITH_REASON, reason=REASON_GPI_NO_CHAIN,
                              terms_unruled=unruled, terms_held=held, guards=guards)
        cs, why, ratio = mature_chain_at_anchor(data, pos)
        if cs is None:
            return SpanResult(category=ABSENT_WITH_REASON, reason=why,
                              terms_unruled=unruled, terms_held=held, guards=guards)
        if ratio < 1.0:
            # ⚠ The selector had a choice. Flagged, not excluded — same posture as the C-terminal
            # guard on P08571. The ratio travels on the row so magnitude needs no threshold.
            guards.append(f"{GUARD_CHAIN_SHORTER_THAN_LONGEST}:{ratio:.3f}")
        if pos - 1 < cs:
            return SpanResult(category=ABSENT_WITH_REASON,
                              reason=REASON_GPI_POSITION_UNANNOTATED,
                              terms_unruled=unruled, terms_held=held, guards=guards)
        # ⚠ start → (anchor − 1): the anchored residue itself is the attachment point, not part
        # of the folded ectodomain.
        return SpanResult(span_aa=pos - cs, span_start=cs, span_end=pos - 1, rule=RULE_GPI_A,
                          terms_unruled=unruled, terms_held=held, guards=guards)

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
        "span_start": result.span_start if result.span_start is not None else "",
        "span_end": result.span_end if result.span_end is not None else "",
        "span_rule": result.rule,
        "span_category": result.category,
        "no_span_reason": result.reason,
        "span_boundary_coordinate": result.boundary_coordinate,
        "terms_unruled": ";".join(sorted(set(result.terms_unruled))),
        "terms_held": ";".join(sorted(set(result.terms_held))),
        "guards": ";".join(sorted(set(result.guards))),
        "parsed_under": result.definition,
    }
