"""The census cost model (D-077 decision 6): what a census of N targets COSTS.

A pure, sequence-only predicate over ECD span length. It folds nothing, calls
nothing, and can therefore answer "what would a census of N targets cost?" before
a dollar is spent — the only cost instrument available before the money is gone.

═══════════════════════════════════════════════════════════════════════════════
⚠ WHAT THIS AXIS IS, AND WHAT IT IS NOT — D-077 decision 1, copied verbatim
═══════════════════════════════════════════════════════════════════════════════

Local-foldability is a monotone step function of ECD length. ECD length is
**feature 1** of the pre-registered six (D-027). Tier was assigned *by* length.
Precision was assigned *by* tier. Therefore **length, tier, precision, and
local-foldability are, on the current cohort, four names for one partition with
no overlap** — which is precisely the confound F-008 recorded and D-075 decision 6
declines to resolve.

1. **Local-foldability MUST NOT become a model feature.** No seventh (or eighth)
   feature. The `--ablate` named-set refusal (D-075 decision 5) stands unamended;
   adding a foldability feature requires a new dated entry and would re-import
   F-008 under a new name.
2. **It MUST NOT be presented as a census axis alongside suitability without its
   label.** It is a **cost / tractability / reproducibility** axis. It says what a
   target costs to *compute*, and **nothing whatsoever** about whether it is a
   good ADC target. Any surface placing the two side by side must state that in
   the same visual frame (D-069, every surface self-sufficient).
3. **It MUST NOT be used to filter the census.** A comprehensive census (roadmap
   3.1) that silently drops the targets it cannot afford to fold is a census of
   *our budget*, not of the surfaceome — and it would bias the census by length,
   i.e. by feature 1. Unaffordable targets stay in the census, flagged, unfolded.
   **This is the F-009 error one level out and it is refused here in advance.**
4. **The one thing it legitimately is:** a *pre-fold, sequence-only* predicate. It
   can be computed for an arbitrary census **without folding anything**, which
   makes it the only cost instrument available before the money is spent.

Those four are reproduced here rather than cited because, per D-074, an instrument
that can be misused carries the statement of its own limits — and this one is a
single careless import away from becoming a seventh feature. A reader who reaches
for `envelope()` from a feature-extraction module will read this docstring and
nothing else. `tests/test_foldability.py` asserts they are still here, and asserts
structurally that neither `core/scorer.py` nor `core/features.py` imports this
module, so refusal 1 is checkable rather than editorial.

═══════════════════════════════════════════════════════════════════════════════
WHAT IT LICENSES (decision 6)
═══════════════════════════════════════════════════════════════════════════════

✅ **Cost:** "Of these N targets, M fold at zero marginal cost on an 8 GB consumer
   card; N−M need rented compute." Derived, dated, recipe-named.
✅ **Reproducibility:** "M of the folds underlying this result are reproducible by
   any reader with a consumer 8 GB GPU and no cloud spend." A real strength of the
   single-sequence / no-MSA design — **provided M is derived from the live
   endpoints and carries its recipe**, never from a CSV snapshot (D-050).
❌ **Not licensed:** any statement coupling foldability to suitability, or any
   census filtered by it.

The ceiling comes from `core.manifest.LOCAL_CEILING`, which carries the recipe
(int8 / chunk 64) it was measured under. No length literal appears in this module;
a test fails if one does.
"""

from __future__ import annotations

from collections import Counter
from typing import Iterable, Mapping

from core.manifest import LOCAL_CEILING, FoldCeiling

# The three verdicts. `OVER_CEILING` is deliberately distinct from `RENTAL`:
# "costs money" and "folds on no single card as one sequence" are different facts
# about the world, and collapsing them would let a census quote a price for
# something that cannot be bought.
LOCAL = "local"
RENTAL = "rental"
OVER_CEILING = "over_ceiling"

VERDICTS = (LOCAL, RENTAL, OVER_CEILING)


def envelope(span_aa: int, ceiling: FoldCeiling = LOCAL_CEILING) -> str:
    """Where a target of `span_aa` residues can be folded, at the measured recipe.

    Returns `local`, `rental`, or `over_ceiling`. Mirrors
    `core.manifest.tier_for_span` by construction — both read the same ceiling
    structure, and a test asserts they agree on every span in the cohort.

    Raises on a missing span rather than guessing. Thirteen of the 82 rows carry
    an empty `largest_span_aa`, and quietly bucketing an unmeasured target as
    affordable is how a cost estimate becomes a fiction — D-024 refused exactly
    that guess when it kept `untested` as a third bucket.
    """
    if span_aa is None:
        raise ValueError(
            "span_aa is None — the ECD span was never measured for this target. "
            "An unmeasured target has no envelope; it must be reported as unknown, "
            "not bucketed as affordable (D-024, D-077 dec 1 refusal 3)."
        )
    if not isinstance(span_aa, int):
        raise TypeError(f"span_aa must be an int, got {type(span_aa).__name__}")

    if span_aa <= ceiling.local_bound:
        return LOCAL
    if span_aa < ceiling.rental_bound:
        return RENTAL
    return OVER_CEILING


def split(spans: Iterable[int], ceiling: FoldCeiling = LOCAL_CEILING) -> Mapping[str, int]:
    """Count an arbitrary census by envelope. Exhaustive: every span lands in
    exactly one bucket and the counts sum to the input size, so no target can
    vanish from a cost estimate.

    ⚠ This counts what it is GIVEN. It does not filter, and callers must not use
    it to filter (refusal 3). Unaffordable targets stay in the census, flagged and
    unfolded — a census filtered by affordability is a census of our budget,
    biased by length.
    """
    counts = Counter(envelope(s, ceiling) for s in spans)
    return {verdict: counts.get(verdict, 0) for verdict in VERDICTS}


def describe(ceiling: FoldCeiling = LOCAL_CEILING) -> str:
    """One line naming the ceiling AND its recipe, for any report this feeds.

    A cost claim without its recipe is not checkable: the same span is affordable
    at int8 and not at fp16. D-077 dec 3 is why this is not just the number.
    """
    band = f", unstable band {ceiling.unstable_band}" if ceiling.unstable_band else ""
    return (f"{ceiling.hardware} at dtype={ceiling.dtype}, chunk_size={ceiling.chunk_size}: "
            f"local <= {ceiling.local_bound} aa, over-ceiling >= {ceiling.rental_bound} aa{band}")
