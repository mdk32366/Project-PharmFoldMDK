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

# The tier recipe table is the authority for what dtype/chunk_size each tier runs
# (D-047). The ceiling below binds itself to it rather than restating the values,
# so the routing constant and the recipe that measured it cannot drift apart
# (D-077 dec 3). `core.contracts` is a stdlib-only serving-safe leaf, so this
# import drags no `worker/` in.
from core.contracts import TIER_RECIPE

_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = _ROOT / "data" / "cohort_82_ecd.csv"

# ── the local fold ceiling, BOUND to the recipe that measured it (D-077 dec 3) ──
#
# ⚠ This used to be two bare module-level ints, hand-duplicated in
# `scripts/ecd_lengths.py:51-52` — and the comment here said so ("mirrors
# scripts/ecd_lengths.py:46-52"), which is a written record of two paths to one
# quantity, free to drift. D-077 decision 3 names exactly that failure: the probe
# defaults `--dtype fp16` (it was written for the A6000), so a local run that
# forgot `--dtype int8` would measure a ceiling for a recipe the local tier does
# not use, and that number would land in the constant routing int8 production
# folds. Binding the length to its recipe makes the drift UNREPRESENTABLE rather
# than merely unlikely; `scripts/ecd_lengths.py` now imports this structure, and
# `tests/test_manifest.py::test_no_second_copy_of_the_ceiling_survives_in_the_tree`
# fails if a bare literal reappears anywhere under core/scripts/worker/app.


@dataclass(frozen=True)
class FoldCeiling:
    """A fold-length ceiling and the recipe under which it was measured.

    D-077 dec 3: the ceiling is recorded as a triple (hardware, dtype, chunk_size)
    → length, NEVER as a bare integer. A ceiling measured under any other recipe
    may not update this one.

    `unstable_band` is D-077 dec 4's pre-registered outcome for a boundary that is
    not sharp: `(highest 4-for-4 good, lowest 4-for-4 bad)`. It is None until a
    probe measures one. **When it is set, routing uses the LOW end** — the cost of
    routing an unfoldable target to local is a crashed host; the cost of routing a
    foldable one to rental is a few dollars.
    """

    hardware: str
    dtype: str
    chunk_size: int
    known_good: int
    known_bad: int
    unstable_band: tuple[int, int] | None = None
    provenance: str | None = None

    def recipe(self) -> dict:
        """The recipe this ceiling is valid for — comparable against `TIER_RECIPE`."""
        return {"dtype": self.dtype, "chunk_size": self.chunk_size}

    @property
    def local_bound(self) -> int:
        """Largest span that may route local. The conservative end of a band."""
        return self.unstable_band[0] if self.unstable_band else self.known_good

    @property
    def rental_bound(self) -> int:
        """At or above this, the span is definitively over the local ceiling."""
        return self.unstable_band[1] if self.unstable_band else self.known_bad


# Measured local fold ceiling, S-004/S-005: 440 aa folds clean (28.6 s, peak
# 6665 MiB, no spill); 630 aa is 4-for-4 fatal; (440, 630) is UNMEASURED — the
# band D-077 exists to close. **The number stays 440 until an F-entry measures a
# new one** (D-077: the constant moves in the same PR as the entry that measured
# it, or not at all).
LOCAL_CEILING = FoldCeiling(
    hardware="local NVIDIA Blackwell, 8 GB VRAM",
    dtype=TIER_RECIPE["local"]["dtype"],
    chunk_size=TIER_RECIPE["local"]["chunk_size"],
    known_good=440,
    known_bad=630,
    unstable_band=None,
    provenance="S-004/S-005 bisection; band (440, 630) unmeasured pending D-077",
)


def tier_for_span(span: int, ceiling: FoldCeiling = LOCAL_CEILING) -> tuple[str, str | None]:
    """Tier for a sliced_ecd fold of `span` aa against a measured ceiling.

    Every rental row carries a reason so it is never mistaken for a measured
    routing. The reasons are distinct on purpose: `unmeasured_local_ceiling` means
    nobody has looked, `unstable_ceiling_band` means someone looked and the
    boundary was not sharp. Collapsing them would lose the D-077 dec 4 result.
    """
    if span <= ceiling.local_bound:
        return "local", None                            # measured-clean local fold
    if span < ceiling.rental_bound:
        if ceiling.unstable_band is not None:
            return "rental", "unstable_ceiling_band"    # D-077 dec 4: band, conservative end
        return "rental", "unmeasured_local_ceiling"     # D-024 (iii)
    return "rental", "over_local_ceiling"               # definitively rental

# ⚠⚠ NAMED EXCLUSIONS (D-022, extended by D-085). READ THE SCOPE BEFORE USING THIS.
#
# ⚠ "Excluded" here has NEVER meant "cannot be folded", and reading it that way is the defect
# D-085 was raised to fix. Every entry states BOTH the path that skips it AND — when the protein
# is foldable at all — the CONDITIONS under which it folds. An exclusion whose reason stops at
# "excluded" tells a future reader nothing about whether the work is impossible or merely
# elsewhere, and the two lead to opposite decisions.
#
# ⚠ Proof that the distinction is not hypothetical: MUC16 and FAT2 are **in the census manifest at
# tranche 5, tier=rental** — they are SCHEDULED TO FOLD. A guard that treated this registry as
# "unfoldable" and applied it to the census path would silently drop two rows that are queued to
# succeed. That is why `scope` is a field and not a comment.


@dataclass(frozen=True)
class Exclusion:
    """One named exclusion. ⚠ `conditions` is REQUIRED whenever `foldable` is not `"no"`.

    Enforced in `__post_init__` rather than by review, because *"state the conditions"* is a rule
    that decays the moment someone adds an entry in a hurry.
    """

    symbol: str
    scope: str        #: ⚠ WHICH fold path skips it. Never "everywhere" without meaning it.
    reason: str       #: why it is skipped on that path
    foldable: str     #: ⚠ "no" | "yes, …" — a sentence, never a bare bool
    conditions: str   #: ⚠ the conditions under which it CAN be folded

    def __post_init__(self) -> None:
        if self.foldable != "no" and not self.conditions.strip():
            raise ValueError(
                f"{self.symbol}: `foldable` is {self.foldable!r} but no conditions are stated. "
                f"⚠ An exclusion that can be folded MUST say under what conditions — otherwise it "
                f"reads as impossible and the work is silently abandoned.")


EXCLUSIONS: dict[str, Exclusion] = {
    "Q8WXI7": Exclusion(
        symbol="MUC16 (CA-125), 14451 aa",
        scope="cohort tranche 0 (the 82, local card, whole sequence)",
        reason="folds on no single card as one sequence (D-022)",
        foldable="yes — and it is ALREADY QUEUED: census tranche 5, tier=rental",
        conditions=("Rental hardware, as one sequence. ⚠ A structure is PRODUCIBLE; a meaningful "
                    "whole-ECD structure is not, because MUC16 is largely intrinsically disordered "
                    "(tandem SEA repeats + glycosylated linkers) — D-076 Tier 3. ⚠ That is a "
                    "BIOLOGY limit, not a compute one, and more VRAM does not remove it."),
    ),
    "Q9NYQ8": Exclusion(
        symbol="FAT2, 4030 aa",
        scope="cohort tranche 0 (the 82, local card, whole sequence)",
        reason="folds on no single card as one sequence (D-022)",
        foldable="yes — and it is ALREADY QUEUED: census tranche 5, tier=rental",
        conditions=("Rental hardware as one sequence, or domain assembly on the local card. "
                    "⚠ It is ORDERED (a cadherin repeat stack), so unlike MUC16 this is a pure "
                    "resource limit — D-076 Tier 2. ⚠ Assembly changes `boundary_method`, so an "
                    "assembled structure is not comparable to a single-pass one without saying so."),
    ),
    "P55073": Exclusion(
        symbol="P55073, span 68–304 (237 aa)",
        scope="every ESMFold path, at any size, on any hardware",
        reason=("the span contains `U` (selenocysteine) and `U` is absent from the ESM "
                "vocabulary — the fold cannot be tokenised, let alone attempted (F-033)"),
        foldable="yes, but ONLY by folding a DIFFERENT SEQUENCE than the one on record",
        conditions=(
            "⚠⚠ Substitution is REQUIRED, and every option changes the molecule:\n"
            "  · `U`→`C` (cysteine): selenocysteine is the Se analogue of cysteine, so the "
            "backbone prediction is expected to be close. ⚠ BUT the artifact would then describe "
            "a sequence that is NOT the sequence of record — the MSLN class of defect (F-025), "
            "where something folds, scores and looks entirely normal while being the wrong "
            "molecule.\n"
            "  · `U`→`X` (unknown): `X` IS in the vocabulary (measured), so this tokenises. It "
            "masks the residue instead of asserting a wrong one.\n"
            "⚠ EITHER WAY the substitution must be recorded IN the artifact — a different "
            "`span_definition` or an explicit `residue_substitution` field — because an unlabelled "
            "substitution is indistinguishable from a correct fold.\n"
            "⚠ NOT DONE, and not Code's call: choosing a substitution is a modelling decision "
            "about what the structure means, not a bug fix."),
    ),
}

#: ⚠ COHORT-SCOPED VIEW, and the filter is the point. `core/manifest.py`'s cohort builder and
#: `crank_status.py`'s roster reconciliation consume this; **the census path must NOT**, because
#: `Q8WXI7` and `Q9NYQ8` are queued to fold there. Derived, never hand-maintained alongside.
NAMED_EXCLUSIONS: dict[str, str] = {
    acc: f"oversize: {e.symbol} — {e.reason}"
    for acc, e in EXCLUSIONS.items()
    if e.scope.startswith("cohort")
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
    tier: str                   # local | rental | msa (msa is claimable, not an ESMFold recipe — D-107)
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
    """Tier for a sliced_ecd fold of `span` aa, against the measured local ceiling.

    Kept as the internal name `build_manifest` calls; the routing rule itself now
    lives in the public `tier_for_span` so the census cost model (D-077 dec 6) and
    the manifest cannot disagree about what routes where.
    """
    return tier_for_span(span)


def _whole_tier(sequence_length: int | None) -> tuple[str, str | None]:
    """Tier for a whole-sequence fold. D-024 does not rule this (whole folds are
    held out of the ranking); rental is the conservative default, and every rental
    row must carry a reason so it is not mistaken for a measured routing."""
    if sequence_length is not None and sequence_length <= LOCAL_CEILING.local_bound:
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
