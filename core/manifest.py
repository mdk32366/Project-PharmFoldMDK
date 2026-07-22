"""D-023 orchestrator manifest: cohort → boundary method → tier → routing table.

THE INPUT is `data/cohort_82_ecd.csv` (D-020's measured ECD distribution), not a
live UniProt call — the measurement already happened. THE OUTPUT is a
deterministic, reviewable routing table plus the D-024 structured coverage
object: the thing that makes the routing auditable in one screen before a single
job exists (D-023 i).

D-024 ruling (2026-07-22) fixes the shape this emits. Traceability:

- **boundary_method** ∈ {sliced_ecd, gpi_predicted, whole}. `gpi_predicted` is
  DEFERRED (D-023 ii), so the GPI subset routes to `whole`, held out, until the
  predictor lands. A target is `sliced_ecd` iff it has a NUMERIC largest ECD span.
  SDK1 (Q7Z5N4) has n_spans==1 but null bounds (`None-2009(None)`), so it is
  `whole` — keying off n_spans would slice a None (D-024 v).
- The 13 `untested` (440,630) targets route to RENTAL with
  `tier_reason=unmeasured_local_ceiling` and are RANKED (sliced_ecd, comparable),
  NOT held out (D-024 iii/iv). Holding them out would understate coverage by 16%.
- **held_out** means boundary-method incomparability only: whole-method targets
  are held out of cross-method ranking (D-021 §1a). Tier is orthogonal (D-024 iv).
- **MUC16 (Q8WXI7)** and **FAT2 (Q9NYQ8)** are the named exclusions (D-022).
- The 3 primary-match accessions carry a provenance flag (D-020).

COVERAGE OBJECT (D-024 i, corrected 2026-07-22). The three DISPOSITIONS —
ranked / held_out / excluded — are the binding partition: mutually exclusive,
exhaustive, `ranked + held_out + excluded == denominator`, and only that.
`unmeasured_tier` and `no_topology` are breakout SUBSETS that cut ACROSS the
partition (unmeasured_tier ⊆ ranked, no_topology ⊆ held_out); they are NOT summed
into it. The entry's §(i) first read this as a five-cell partition — the Planner's
error of flattening a disposition and a reason-flag into one object — which would
force the 13 `untested` out of `ranked` and understate coverage by 16%. The §(i)
correction (raised by the Builder against the entry, per D-024) rules the
three-cell-plus-breakouts shape this module implements.

What this module deliberately does NOT decide: the exact local ceiling within
(440, 630) aa (D-024 leaves it open and cheap); and the A6000 single-fold ceiling
that governs whether the large rental targets fold as one sequence (D-022, owner
action). Both are recorded as pending, not estimated here.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = _ROOT / "data" / "cohort_82_ecd.csv"

# Measured local fold ceiling, S-004/S-005 — mirrors scripts/ecd_lengths.py:46-52.
# 440 aa folds clean; 630 aa is 4-for-4 fatal; (440, 630) is UNMEASURED.
CEILING_KNOWN_GOOD = 440
CEILING_KNOWN_BAD = 630

# Named oversize exclusions (D-022): fold on no single card as one sequence. Named
# rather than thresholded because the A6000 ceiling that would set a threshold is
# itself unmeasured; these two are the definitively-oversize first pass.
NAMED_EXCLUSIONS: dict[str, str] = {
    "Q8WXI7": "oversize: MUC16 (CA-125), 14451 aa — folds on no single card as one sequence (D-022)",
    "Q9NYQ8": "oversize: FAT2, 4030 aa — folds on no single card as one sequence (D-022)",
}

# Primary-match resolutions (D-020): among multiple reviewed-human hits, the one
# whose PRIMARY gene name equals the requested symbol. Carried as provenance so a
# reader need not re-derive which symbols were ambiguous.
PRIMARY_MATCH: dict[str, str] = {
    "Q01814": "ATP2B2",   # contaminant P23634/ATP2B4
    "Q6UXK5": "LRRN1",    # contaminant O75427/LRCH4
    "Q99835": "SMO",      # contaminant Q9NWM0/SMOX
}


@dataclass(frozen=True)
class ManifestRow:
    """One target's routing decision. Reviewable before anything irreversible."""

    accession: str
    gene: str
    label: str
    boundary_method: str        # sliced_ecd | gpi_predicted | whole
    span: int | None            # largest ECD span LENGTH (sliced_ecd), else None
    ecd_start: int | None       # 1-based bounds of the folded span (sliced_ecd), else None
    ecd_end: int | None         # inherited: the LARGEST span, per D-024/D-026 (ii)
    tier: str                   # local | rental
    tier_reason: str | None     # required whenever tier == "rental"
    held_out: bool              # boundary-method incomparable (D-021 §1a)
    excluded: bool
    exclusion_reason: str | None
    primary_match: bool         # D-020 mapping-provenance flag

    @property
    def disposition(self) -> str:
        """The coverage disposition — exactly one of excluded / held_out / ranked.
        Excluded wins over held_out wins over ranked."""
        if self.excluded:
            return "excluded"
        if self.held_out:
            return "held_out"
        return "ranked"


def _int_or_none(value: str) -> int | None:
    value = (value or "").strip()
    return int(value) if value else None


_SPAN_RE = re.compile(r"^(\d+)-(\d+)\((\d+)\)$")


def _largest_span_bounds(spans: str, largest: int | None) -> tuple[int | None, int | None]:
    """From the CSV `spans` field ('215-671(457); 34-39(6)'), return the 1-based
    [start, end] of the span whose length equals `largest`. Inherited from the
    same measurement the cohort was bucketed on (D-020), so routing and fold agree
    on WHICH span. None when there is no numeric span (whole-method)."""
    if largest is None or not spans:
        return None, None
    for seg in spans.split(";"):
        m = _SPAN_RE.match(seg.strip())
        if m and int(m.group(3)) == largest:
            return int(m.group(1)), int(m.group(2))
    return None, None


def _sliced_tier(span: int) -> tuple[str, str | None]:
    """Tier for a sliced_ecd fold of `span` aa, against the measured local ceiling."""
    if span <= CEILING_KNOWN_GOOD:
        return "local", None                        # measured-clean local fold
    if span < CEILING_KNOWN_BAD:                     # (440, 630): local ceiling unmeasured
        return "rental", "unmeasured_local_ceiling"  # D-024 (iii)
    return "rental", "over_local_ceiling"            # >= 630: definitively rental


def _whole_tier(sequence_length: int | None) -> tuple[str, str | None]:
    """Tier for a whole-sequence fold. D-024 does not rule this (whole folds are
    held out of the ranking); rental is the conservative default, and every rental
    row must carry a reason so it is not mistaken for a measured routing."""
    if sequence_length is not None and sequence_length <= CEILING_KNOWN_GOOD:
        return "local", None
    return "rental", "whole_sequence_fold"


def build_manifest(csv_path: Path | str = DEFAULT_CSV) -> list[ManifestRow]:
    """Read the measured ECD cohort and emit one routing row per target."""
    rows: list[ManifestRow] = []
    with open(csv_path, encoding="utf-8") as fh:
        for src in csv.DictReader(fh):
            acc = src["accession"]
            span = _int_or_none(src["largest_span_aa"])       # NUMERIC bounds only (D-024 v)
            seq_len = _int_or_none(src["sequence_length"])

            if span is None:
                # No numeric ECD boundary → fold the whole sequence. gpi_predicted
                # is deferred (D-023 ii), so the GPI subset lands here, held out.
                boundary_method = "whole"
                tier, tier_reason = _whole_tier(seq_len)
                held_out = True
                ecd_start, ecd_end = None, None
            else:
                boundary_method = "sliced_ecd"
                tier, tier_reason = _sliced_tier(span)
                held_out = False
                ecd_start, ecd_end = _largest_span_bounds(src["spans"], span)

            rows.append(
                ManifestRow(
                    accession=acc,
                    gene=src["gene"],
                    label=src["label"],
                    boundary_method=boundary_method,
                    span=span,
                    ecd_start=ecd_start,
                    ecd_end=ecd_end,
                    tier=tier,
                    tier_reason=tier_reason,
                    held_out=held_out,
                    excluded=acc in NAMED_EXCLUSIONS,
                    exclusion_reason=NAMED_EXCLUSIONS.get(acc),
                    primary_match=acc in PRIMARY_MATCH,
                )
            )
    return rows


def coverage(rows: list[ManifestRow]) -> dict:
    """The D-024 structured coverage object. ranked/held_out/excluded partition the
    cohort (sum == denominator); unmeasured_tier and no_topology are breakout
    subsets surfaced for honesty, not additional partition cells."""
    return {
        "denominator": len(rows),
        "ranked": sum(1 for r in rows if r.disposition == "ranked"),
        "held_out": sum(1 for r in rows if r.disposition == "held_out"),
        "excluded": sum(1 for r in rows if r.disposition == "excluded"),
        "unmeasured_tier": sum(
            1 for r in rows
            if r.disposition == "ranked" and r.tier_reason == "unmeasured_local_ceiling"
        ),
        "no_topology": sum(
            1 for r in rows if r.disposition == "held_out" and r.span is None
        ),
    }


def coverage_line(cov: dict) -> str:
    """One-line human rendering of the coverage object (a view, never the source)."""
    return (
        f"{cov['denominator']} targets · {cov['ranked']} ranked "
        f"({cov['unmeasured_tier']} on an unmeasured local ceiling) · "
        f"{cov['held_out']} held out ({cov['no_topology']} no-topology, whole-method) · "
        f"{cov['excluded']} excluded (named)"
    )


def render(rows: list[ManifestRow]) -> str:
    """The auditable-in-one-screen table (D-023 i)."""
    header = f"{'accession':<10} {'gene':<10} {'method':<12} {'span':>5} " \
             f"{'tier':<7} {'disposition':<10} flags"
    lines = [header, "-" * len(header)]
    for r in sorted(rows, key=lambda x: (x.disposition, x.gene)):
        flags = []
        if r.tier_reason:
            flags.append(r.tier_reason)
        if r.excluded:
            flags.append("EXCLUDED")
        if r.primary_match:
            flags.append("primary-match")
        lines.append(
            f"{r.accession:<10} {r.gene:<10} {r.boundary_method:<12} "
            f"{(r.span if r.span is not None else '-'):>5} {r.tier:<7} "
            f"{r.disposition:<10} {', '.join(flags)}"
        )
    return "\n".join(lines)


def main() -> int:
    rows = build_manifest()
    print(coverage_line(coverage(rows)))
    print()
    print(render(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
