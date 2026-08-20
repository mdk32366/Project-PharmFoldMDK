"""PAE is an L x L matrix, including when L is 1 — the case the corpus cannot reach.

⚠⚠ THE DEFECT. `outputs["predicted_aligned_error"].squeeze()` removes EVERY size-1 dimension, so a
one-residue span's `(1, 1, 1)` collapsed to a 0-dim scalar and `.tolist()` returned a float. **The
census minimum span is 1 aa**, so the output TYPE changed for a real input — a matrix for 2,689
proteins and a bare number for one — with nothing in the signature saying so.

⚠ IT WAS FOUND BY RUNNING, NOT BY READING. Ten timed folds selected at evenly spaced ranks of span
length put a 1-aa protein first, and `len(result.pae)` raised `TypeError: object of type 'float' has
no len()`. No test could have found it, because...

⚠⚠ ...THE CORPUS CANNOT EXERCISE IT. Every other census span is >= 21 aa and returns a proper NxN
matrix — nine of them measured. **Only a DELIBERATE fixture reaches the degenerate case**, which is
`F-046`'s lesson: a shape that occurs once in a corpus is not tested by the corpus.

⚠ And the pLDDT line directly above `pae` had the identical defect, patched IN PLACE without
generalising to its sibling. `F-052`.
"""
from __future__ import annotations

import pytest

from worker.runner import _pae_matrix


class _FakeTensor:
    """⚠ Stands in for a torch tensor: this test must not need a GPU or a model to run."""

    def __init__(self, data, ndim=None):
        self._data = data
        self.ndim = ndim if ndim is not None else _depth(data)

    def __getitem__(self, i):
        return _FakeTensor(self._data[i])

    def tolist(self):
        return self._data

    def squeeze(self):
        """⚠ torch's semantics, reproduced: remove EVERY size-1 dimension.

        Present so the revert proof reds at an ASSERTION rather than an AttributeError. A fake
        that cannot perform the defect cannot prove the fix — the harness has to be able to fail
        the way the real thing failed.
        """
        d = self._data
        while isinstance(d, list) and len(d) == 1:
            d = d[0]
        return _FakeTensor(d, ndim=_depth(d))


def _depth(x) -> int:
    return 1 + _depth(x[0]) if isinstance(x, list) and x else (0 if not isinstance(x, list) else 1)


# ⚠⚠ THE FIXTURE THE CORPUS CANNOT PROVIDE: a one-residue span.
def test_a_one_residue_span_returns_a_1x1_matrix_not_a_scalar():
    got = _pae_matrix(_FakeTensor([[[0.42]]]))
    assert got == [[0.42]], got
    # ⚠ the property that actually matters downstream: it can be indexed as a matrix
    assert isinstance(got, list) and isinstance(got[0], list)
    assert len(got) == 1 and len(got[0]) == 1


def test_a_scalar_that_already_collapsed_upstream_is_still_returned_as_a_matrix():
    """⚠ Defence in depth: if anything upstream squeezes before we see it, the shape is restored
    rather than propagated — because a float reaching a consumer is the failure being fixed."""
    assert _pae_matrix(_FakeTensor(0.42, ndim=0)) == [[0.42]]


def test_a_single_row_that_survived_as_a_vector_becomes_a_matrix():
    assert _pae_matrix(_FakeTensor([0.1, 0.2], ndim=1)) == [[0.1, 0.2]]


@pytest.mark.parametrize("n", [2, 21, 439])
def test_ordinary_spans_are_unchanged(n):
    """⚠ The fix must not alter the 2,689 proteins that were always fine."""
    m = [[float(i * n + j) for j in range(n)] for i in range(n)]
    got = _pae_matrix(_FakeTensor([m]))          # (batch, L, L)
    assert got == m
    assert len(got) == n and len(got[0]) == n


def test_the_batch_dimension_is_dropped_by_index_never_by_size():
    """⚠⚠ THE ROOT CAUSE, ASSERTED. `squeeze()` decides what to drop from how BIG a dimension is,
    so it behaves differently for L=1 than for L=2 — a shape rule that depends on the data."""
    # ⚠⚠ THE CODE, NOT THE SOURCE TEXT. The first version grepped `inspect.getsource` for
    # ".squeeze()" — and reddened on the DOCSTRING, which explains the defect using that word.
    # A guard matching its own warning text is the third instance of this shape today, and the
    # cure is the same each time: read structure, not prose.
    import ast
    import inspect
    tree = ast.parse(inspect.getsource(_pae_matrix).lstrip())
    fn = tree.body[0]
    body = fn.body[1:] if isinstance(fn.body[0], ast.Expr) else fn.body   # drop the docstring
    code = "\n".join(ast.dump(n) for n in body)
    assert "squeeze" not in code, "squeeze() decides shape from size; that is the defect"
    assert "Subscript" in code, "the batch dim must be dropped positionally"


def test_a_batch_of_one_with_a_one_residue_span_is_the_exact_shipped_case():
    """⚠ (1, 1, 1) is literally what ESMFold returned for the 1-aa census protein Q9H902."""
    assert _pae_matrix(_FakeTensor([[[7.5]]])) == [[7.5]]
