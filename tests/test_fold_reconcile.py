"""Three paths to one quantity: the manifest span, the sliced length, the structure's residues.

⚠ **NO `assert` DOES GUARD WORK HERE OR IN THE MODULE UNDER TEST.** `assert` vanishes under
`python -O`, so a guard written as one is a comment that occasionally runs — and the failure would
be silent, in the direction this whole day was spent closing.
"""

from __future__ import annotations

import pytest

from core.fold_reconcile import (
    FoldLengthMismatch, check_sliced_length, reconcile_fold, residues_in_pdb,
)


def _pdb(n, chain="A", start=1):
    """A minimal CA-only structure with `n` residues. Columns are fixed-width and load-bearing."""
    out = []
    for i in range(n):
        r = start + i
        out.append(f"ATOM  {i+1:>5}  CA  ALA {chain}{r:>4}    "
                   f"{i:8.3f}{0.0:8.3f}{0.0:8.3f}  1.00 50.00           C")
    return "\n".join(out)


# ── enqueue-time ────────────────────────────────────────────────────────────
def test_a_sliced_length_matching_its_span_passes_and_returns_the_length():
    assert check_sliced_length("MSLN", "sliced_ecd", 302, "M" * 302, 622) == 302


def test_a_sliced_length_disagreeing_with_its_span_raises():
    """⚠ THE CONSTRUCTION DEFECT. Prove it bites by deleting the comparison: a 641-residue slice
    is written to the record as a 302 aa span and nothing objects."""
    with pytest.raises(FoldLengthMismatch, match="two paths to one quantity"):
        check_sliced_length("MSLN", "sliced_ecd", 302, "M" * 641, 622)


def test_the_whole_branch_is_checked_too_not_only_the_sliced_one():
    """⚠ A GUARD THAT ONLY RUNS ON THE PATH ALREADY BELIEVED CORRECT GUARDS NOTHING — the same
    shape as a guard placed downstream of the filter it guards. `whole` makes a checkable claim.

    Prove it bites by dropping the `elif`: a `whole` row that was silently sliced passes."""
    assert check_sliced_length("X", "whole", None, "M" * 2000, 2000) == 2000
    with pytest.raises(FoldLengthMismatch):
        check_sliced_length("X", "whole", None, "M" * 302, 2000)


def test_sliced_ecd_with_no_span_raises_rather_than_skipping_the_check():
    """⚠ No span means there is no claim to verify — which is not the same as the claim holding."""
    with pytest.raises(FoldLengthMismatch, match="no span"):
        check_sliced_length("X", "sliced_ecd", None, "M" * 302, 2000)


def test_an_unrecognised_method_reaching_the_length_check_raises():
    with pytest.raises(FoldLengthMismatch, match="no claim to verify"):
        check_sliced_length("X", "census_span", 302, "M" * 302, 2000)


# ── post-fold, end to end ───────────────────────────────────────────────────
def test_the_structures_residue_count_is_read_from_the_structure():
    """⚠ Counted from the artifact, not from a field recorded beside it. A count taken from the
    same record as the claim cannot disagree with it."""
    assert residues_in_pdb(_pdb(302)) == 302


def test_three_agreeing_numbers_reconcile():
    r = reconcile_fold("MSLN", 302, 302, _pdb(302))
    assert r.agrees and r.structure_residues == 302


def test_a_structure_disagreeing_with_the_manifest_halts():
    """⚠⚠ THE END-TO-END CHECK, and the only one that can see corruption in transit — a truncated
    payload, a serialisation fault, a DB round-trip. The enqueue check proves the slice was right
    WHEN CUT; this proves the artifact is right when READ.

    Prove it bites by comparing `enqueue_length` to `span_aa` only: both agree at 302 while the
    structure holds 2,000 residues, and the fold of the wrong molecule passes."""
    with pytest.raises(FoldLengthMismatch, match="different molecule"):
        reconcile_fold("MSLN", 302, 302, _pdb(2000))


def test_the_fixture_actually_contains_a_disagreement():
    """⚠ A-017 clause (c). With a matching structure the test above passes under an implementation
    that never compares anything."""
    assert residues_in_pdb(_pdb(2000)) != 302


def test_a_survey_can_report_instead_of_halting():
    """For folds that already happened, the finding is the report rather than a halt."""
    r = reconcile_fold("X", 302, 302, _pdb(2000), strict=False)
    assert r.agrees is False and "structure_residues=2000" in r.detail


def test_reconciliation_refuses_to_pass_when_there_is_nothing_to_compare():
    """⚠ An absent claim is not a satisfied claim. Prove it bites by defaulting `agrees` to True."""
    with pytest.raises(FoldLengthMismatch):
        reconcile_fold("X", None, None, _pdb(302))
