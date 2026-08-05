"""D-077 decision 2 — the chunk-invariance comparator must be EXACT.

These tests exist to make one property unfaggable: the comparison that decides
whether `chunk_size` is a memory knob or a recipe dimension must not be able to
call two different folds "the same". D-077 decision 2 fixed both readings before
any fold runs, and its second row says **"outputs differ at all, by any margin"**
is the *differ* branch. "Nearly identical" is not a third reading — there is no
third reading, and no tolerance may be invented after seeing a diff (D-041 dec 4).

So a tolerant comparator would not merely be imprecise; it would silently select
the *invariant* branch, unlock Arm B of the bisection (order §3), and license
folds at chunk 16/32 being ranked alongside folds at chunk 64. **The tolerance is
the failure mode, which is why `test_comparator_is_exact_not_tolerant` asserts
against it twice — behaviourally and statically.**

Pure logic. Runs on the CI gate. No GPU, no network, no database.
"""

from __future__ import annotations

import inspect
import re

import pytest

from worker.fold_compare import compare_folds


# ── fixtures: two folds that are byte-identical, and perturbations of one ─────

def _fold(coords, plddt):
    """A fold output as the comparator sees it: CA coordinates + per-residue pLDDT."""
    return {"coords": coords, "plddt": plddt}


BASE_COORDS = [
    (12.345, -4.210, 0.007),
    (15.880, -1.004, 2.331),
    (18.002, 1.775, 4.960),
]
BASE_PLDDT = [88.41, 91.02, 76.55]


def _base():
    return _fold(list(BASE_COORDS), list(BASE_PLDDT))


# ── the three required tests (order §1a) ─────────────────────────────────────

def test_comparator_detects_a_single_perturbed_coordinate():
    """One CA coordinate differing in the LAST DECIMAL PLACE must report not-identical.

    How this bites: a comparator that rounds, or that compares with any tolerance,
    passes an identical-vs-identical check happily and only fails here. If this test
    ever passes against a rounding implementation, it is not biting.
    """
    a = _base()
    b = _base()
    b["coords"][1] = (15.880, -1.004, 2.3310000000001)   # last-place perturbation

    result = compare_folds(a, b)

    assert result.identical is False
    assert result.divergence is not None
    assert result.divergence.residue_index == 1
    assert result.divergence.field == "z"


def test_comparator_detects_a_plddt_difference_with_identical_coordinates():
    """Coordinates match, pLDDT does not → not-identical.

    Guards a comparator that only reads coordinates. pLDDT is a model output and a
    change in it IS a change in the fold, even when every atom lands identically.
    """
    a = _base()
    b = _base()
    b["plddt"][2] = 76.55000000001

    result = compare_folds(a, b)

    assert result.identical is False
    assert result.divergence is not None
    assert result.divergence.residue_index == 2
    assert result.divergence.field == "plddt"


def test_comparator_is_exact_not_tolerant():
    """No tolerance anywhere in the comparison path — asserted twice, two ways.

    D-077 decision 2 forbids an invented tolerance. Asserted both behaviourally (a
    difference far below any plausible atol is still reported) and statically (the
    module's source contains no tolerance vocabulary), because either check alone
    is escapable: the behavioural one by a tolerance tighter than the probe value,
    the static one by an import alias.
    """
    # (a) behavioural — a difference smaller than any tolerance anyone would pick
    a = _base()
    b = _base()
    b["coords"][0] = (12.345 + 1e-15, -4.210, 0.007)
    assert compare_folds(a, b).identical is False, "a 1e-15 difference must still be a difference"

    # (b) static — no tolerance vocabulary in the comparison path
    import worker.fold_compare as mod

    source = inspect.getsource(mod)
    body = "\n".join(
        line for line in source.splitlines()
        if not line.lstrip().startswith("#")
    )
    # strip docstrings so the prose explaining *why* there is no tolerance
    # does not itself trip the check
    body = re.sub(r'""".*?"""', "", body, flags=re.S)
    body = re.sub(r"'''.*?'''", "", body, flags=re.S)

    for banned in ("atol", "rtol", "isclose", "approx", "round(", "np.allclose", "allclose"):
        assert banned not in body, f"tolerance vocabulary {banned!r} reached the comparison path"


# ── supporting properties (not in the order; they guard the same ruling) ──────

def test_identical_folds_compare_identical():
    """The trivial direction. Present so a comparator that returns False for
    everything cannot pass the three tests above by brute refusal."""
    result = compare_folds(_base(), _base())
    assert result.identical is True
    assert result.divergence is None


def test_first_divergence_is_the_first_one_not_an_arbitrary_one():
    """When two residues both differ, the reported divergence is the EARLIER one.

    The order calls for 'where they first diverge'. A comparator reporting the last
    difference, or a set, would satisfy 'not identical' while making the evidence
    for a reported finding wrong — and D-077 dec 2 says the first-divergence
    location IS the evidence if the differ branch fires.
    """
    a = _base()
    b = _base()
    b["coords"][1] = (15.880, -1.004, 99.0)
    b["coords"][2] = (0.0, 0.0, 0.0)

    result = compare_folds(a, b)

    assert result.identical is False
    assert result.divergence.residue_index == 1


def test_differing_lengths_are_a_divergence_not_a_crash():
    """Two folds of different residue counts must report, not raise.

    A chunk_size that truncated output would be the most dramatic possible
    non-invariance; the comparator must be able to say so rather than dying on a
    zip() or an IndexError.
    """
    a = _base()
    b = _base()
    b["coords"] = b["coords"][:2]
    b["plddt"] = b["plddt"][:2]

    result = compare_folds(a, b)

    assert result.identical is False
    assert result.divergence.field == "length"


def test_comparator_does_not_mutate_its_inputs():
    """It reports; it does not judge, and it does not touch (order §1b)."""
    a, b = _base(), _base()
    b["plddt"][0] = 1.0
    a_before = (list(a["coords"]), list(a["plddt"]))
    b_before = (list(b["coords"]), list(b["plddt"]))

    compare_folds(a, b)

    assert (a["coords"], a["plddt"]) == a_before
    assert (b["coords"], b["plddt"]) == b_before


@pytest.mark.parametrize("field,index", [("x", 0), ("y", 0), ("z", 0)])
def test_each_coordinate_axis_is_compared(field, index):
    """All three axes are read. A comparator checking only x would pass the
    single-perturbation test above (which perturbs z) only by accident."""
    axis = {"x": 0, "y": 1, "z": 2}[field]
    a = _base()
    b = _base()
    triple = list(b["coords"][index])
    triple[axis] += 1e-13
    b["coords"][index] = tuple(triple)

    result = compare_folds(a, b)

    assert result.identical is False
    assert result.divergence.field == field
