"""`boundary_method` is an opt-in, not a default — and the change is proven a no-op on the cohort.

⚠⚠ **THE DEFECT THIS CLOSES.** `core/enqueue.py:_fold_input` branched on
`boundary_method == "sliced_ecd"` and **fell through to fold the whole sequence** for every other
value. The coordinate `assert` fired only on that one literal, so the safe path cost a keystroke and
the unsafe path cost nothing. Measured 2026-08-07: a census row with `span_aa=302` and no
coordinates folded **2,000 residues** under `''`, `None`, `'whole'` and `'census_span'` alike.

⚠ `whole` is a LEGITIMATE recorded outcome, so nothing would have been red: fold succeeds, recipe
recorded, provenance intact, `source='whole'` — describing the wrong molecule 3,468 times.

⚠ **`### D-081` does not protect a defect.** It freezes measured results and forbids re-running
them; it does not preserve a fail-open default that fires only on inputs the cohort does not
contain. The no-op proof below is the condition on which that change was authorised.
"""

from __future__ import annotations

import pytest

from core.enqueue import RECOGNISED_BOUNDARY_METHODS, UnrecognisedBoundaryMethod, _fold_input
from core.manifest import build_manifest

SEQ = "M" * 2000


def _row(method, start=None, end=None):
    from core.manifest import ManifestRow
    return ManifestRow(accession="X", gene="g", label="l", boundary_method=method, span=302,
                       ecd_start=start, ecd_end=end, tier="local", tier_reason=None,
                       held_out=False, excluded=False, exclusion_reason=None, primary_match=False)


# ── ⚠ THE NO-OP PROOF. The condition the change was authorised on. ──────────
def test_every_cohort_row_carries_a_recognised_boundary_method():
    """⚠ If any cohort row were absent, empty or unrecognised, this change would newly RAISE on the
    82 and would stop being a no-op. Measured: `sliced_ecd` 69, `whole` 13, unrecognised 0.

    Prove it bites by adding `"gpi_predicted"` to a cohort row — D-023 ii defers that method, so it
    is not in the recognised set, and this reds naming the accession."""
    rows = build_manifest()
    assert len(rows) == 82, len(rows)
    bad = [(r.accession, r.boundary_method) for r in rows
           if r.boundary_method not in RECOGNISED_BOUNDARY_METHODS]
    assert not bad, (
        f"{len(bad)} cohort rows carry an unrecognised boundary_method: {bad}. The enqueue raise "
        f"is NOT a no-op on the cohort and the change must stop.")


def test_the_cohort_actually_contains_both_methods():
    """⚠ A-017 clause (c). If every row were `sliced_ecd`, the test above would pass under a
    recognised set that had dropped `whole` entirely."""
    methods = {r.boundary_method for r in build_manifest()}
    assert methods == {"sliced_ecd", "whole"}, methods


# ── the raise ───────────────────────────────────────────────────────────────
@pytest.mark.parametrize("method", ["", None, "census_span", "sliced", "WHOLE", "gpi_predicted"])
def test_an_unrecognised_boundary_method_raises_instead_of_folding_the_whole_sequence(method):
    """⚠⚠ THE GUARD. Every one of these used to return the full 2,000 residues silently.

    Prove it bites by restoring the fall-through `return full_sequence, WHOLE`: each case folds
    2,000 residues, nothing reds, and the artifact records a legitimate-looking `whole`."""
    with pytest.raises(UnrecognisedBoundaryMethod):
        _fold_input(_row(method), SEQ)


def test_sliced_ecd_without_coordinates_raises_rather_than_asserting():
    """⚠ Was an `assert`, which `python -O` strips — and this is the check standing between a span
    and a 2,000-residue fold. Prove it bites by reverting to `assert`, then running under `-O`."""
    with pytest.raises(UnrecognisedBoundaryMethod, match="cannot slice"):
        _fold_input(_row("sliced_ecd"), SEQ)


def test_whole_is_now_an_explicit_opt_in_and_still_works():
    """⚠ `whole` remains legitimate — it is D-024's routing for whole-method targets. What changed
    is that it must be ASKED FOR. The dangerous branch costs a keystroke now, not zero."""
    out, src = _fold_input(_row("whole"), SEQ)
    assert (len(out), src) == (2000, "whole")


def test_sliced_ecd_with_coordinates_cuts_exactly_the_recorded_span():
    """⚠ span_aa and the coordinates are two paths to one quantity. 296-597 is MSLN's mature form."""
    out, src = _fold_input(_row("sliced_ecd", 296, 597), SEQ)
    assert (len(out), src) == (302, "sliced_ecd")
