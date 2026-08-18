"""Tasks E and F of ORDERS-Code-2026-08-17 (second) — the Kathad reproduction, tested first.

⚠ THESE TESTS NEED NEITHER S3 NOR `xlrd`. They exercise the pure functions on synthetic fixtures,
so the gate stays green in CI — which has no S3 file and, per `D-093` decision 7, never will. The
I/O shim that reads the workbook is deliberately not under test here; it is operator tooling over a
file that is referenced by path and never vendored.

The three discriminating fixtures the order names, plus Task F's:

1. ⚠⚠ THE JOIN. S3's `Gene` is an Ensembl id; the symbol lives in `Gene name`. Joining on `Gene`
   returns a clean, plausible, entirely spurious ZERO overlap. A test that happens to join on the
   right column passes under the defect, so the fixture forces the wrong column and asserts it
   fails.
2. CASE. `Colorectal cancer` vs `colorectal cancer` must match; a genuinely different cancer must
   NOT. Removing normalisation must collapse the overlap to zero rather than degrade it.
3. THE `>=` / `>` BOUNDARY. A pair at exactly 150.0 is worth 51 real pairs.
4. ⚠ TASK F — AVAILABILITY. A row with `Low = 0` cannot lose a Low. The unconstrained count is an
   upper bound and must not be published as the finding.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.kathad_reproduction import (  # noqa: E402
    CUTOFF,
    available_one_moves,
    is_kept,
    join_key,
    normalise_cancer,
    one_move_flippable,
    qh_score,
)


# ── the score itself ───────────────────────────────────────────────────────────────────────────
def test_qh_uses_total_including_not_detected():
    """⚠ The denominator INCLUDES `Not detected`. D-100 read this off the file rather than
    recovering it by matching: percent_law == 100*Low/total on 1,640 of 1,640 rows."""
    # 3 high, 0 medium, 0 low, 9 not detected -> total 12
    assert qh_score(high=3, medium=0, low=0, total=12) == pytest.approx(75.0)
    # excluding Not detected would give 300.0 — a different quantity entirely
    assert qh_score(high=3, medium=0, low=0, total=3) == pytest.approx(300.0)


def test_qh_weights_are_one_two_three():
    assert qh_score(high=0, medium=0, low=12, total=12) == pytest.approx(100.0)
    assert qh_score(high=0, medium=12, low=0, total=12) == pytest.approx(200.0)
    assert qh_score(high=12, medium=0, low=0, total=12) == pytest.approx(300.0)


def test_qh_total_zero_is_a_category_not_a_score_of_zero():
    """⚠ An empty panel has no score. Returning 0.0 would rank it below a genuinely low-expressing
    protein, which is an absence dressed as a measurement."""
    assert qh_score(high=0, medium=0, low=0, total=0) is None


# ── 1. ⚠⚠ THE JOIN — the discriminating fixture ───────────────────────────────────────────────
def test_join_on_Gene_column_fails_because_it_is_an_ensembl_id():
    """⚠⚠ THE REGRESSION, named. S3's `Gene` is `ENSG...`; the symbol is in `Gene name`. Matching
    on `Gene` gives 0 of 82 — a clean, plausible, completely spurious empty intersection."""
    s3_row = {"Gene": "ENSG00000151694", "Gene name": "ADAM17", "Cancer": "Colorectal cancer"}
    held = {"symbol": "ADAM17", "cancer": "Colorectal cancer"}

    right = join_key(s3_row, symbol_field="Gene name")
    wrong = join_key(s3_row, symbol_field="Gene")
    held_key = (held["symbol"], normalise_cancer(held["cancer"]))

    assert right == held_key, "joining on `Gene name` must match"
    assert wrong != held_key, "joining on `Gene` must NOT match — it is an Ensembl id"


def test_a_wrong_column_join_yields_empty_not_an_error():
    """⚠ The failure mode is silence. Nothing raises; the intersection is simply empty, and an
    empty intersection reads as a legitimate result."""
    s3 = [{"Gene": "ENSG00000151694", "Gene name": "ADAM17", "Cancer": "Carcinoid"}]
    held_keys = {("ADAM17", normalise_cancer("Carcinoid"))}
    wrong = {join_key(r, symbol_field="Gene") for r in s3}
    assert wrong & held_keys == set(), "the defect produces an empty set, not an exception"


# ── 2. case normalisation ─────────────────────────────────────────────────────────────────────
def test_cancer_labels_match_across_case():
    assert normalise_cancer("Colorectal cancer") == normalise_cancer("colorectal cancer")
    assert normalise_cancer("  Breast Cancer ") == normalise_cancer("breast cancer")


def test_normalisation_does_not_collapse_genuinely_different_cancers():
    """⚠ The other half of the fixture. A normaliser that made everything match would pass the
    first assertion and be useless."""
    assert normalise_cancer("Colorectal cancer") != normalise_cancer("Breast cancer")
    assert normalise_cancer("Lung cancer") != normalise_cancer("Liver cancer")


# ── 3. the >= / > boundary — worth 51 real pairs ──────────────────────────────────────────────
def test_exactly_150_is_kept_under_ge_and_dropped_under_gt():
    assert is_kept(150.0, inclusive=True) is True
    assert is_kept(150.0, inclusive=False) is False


def test_the_inequality_sign_changes_the_count_by_exactly_the_boundary_rows():
    scores = [149.9, 150.0, 150.0, 150.1]
    n_ge = sum(1 for s in scores if is_kept(s, inclusive=True))
    n_gt = sum(1 for s in scores if is_kept(s, inclusive=False))
    assert n_ge == 3 and n_gt == 1
    assert n_ge - n_gt == 2, "the difference is exactly the count of rows at the boundary"


@pytest.mark.parametrize("score,ge,gt", [(149.999, False, False), (150.0, True, False),
                                         (150.001, True, True)])
def test_boundary_is_exact_not_approximate(score, ge, gt):
    assert is_kept(score, inclusive=True) is ge
    assert is_kept(score, inclusive=False) is gt


# ── 4. ⚠ TASK F — the availability constraint ─────────────────────────────────────────────────
def test_a_row_with_no_Low_cannot_lose_a_Low():
    """⚠⚠ THE PUBLICATION BLOCKER. The unconstrained 83 counts a pair as flippable whenever it
    sits within one step of the cutoff. It does not check that a patient EXISTS in the category
    the move comes from."""
    moves = available_one_moves(high=4, medium=0, low=0, not_detected=8)
    sources = {m[0] for m in moves}
    assert "low" not in sources, "there is no Low patient to move"
    assert "high" in sources, "there are High patients, so High->something is available"


def test_available_moves_never_invent_a_patient():
    moves = available_one_moves(high=0, medium=0, low=0, not_detected=12)
    assert all(m[0] == "not_detected" for m in moves), "only Not detected has patients"


def test_constrained_flip_is_not_more_permissive_than_unconstrained():
    """⚠ The constrained count is a SUBSET of the upper bound, always. If it ever exceeded the
    bound, the bound was not a bound."""
    row = dict(high=4, medium=0, low=0, not_detected=8, total=12)
    unconstrained = one_move_flippable(**row, constrained=False)
    constrained = one_move_flippable(**row, constrained=True)
    if constrained:
        assert unconstrained, "constrained flip implies unconstrained flip"


def test_a_zero_low_row_near_the_cutoff_is_not_downward_flippable_but_may_be_upward():
    """The fixture the order names. 4 High of 12 -> qh = 100. Move a Not detected to High and it
    rises; there is no Low to remove."""
    moves = available_one_moves(high=4, medium=0, low=0, not_detected=8)
    ups = [m for m in moves if m[1] in ("high", "medium", "low") and m[0] == "not_detected"]
    assert ups, "an upward move exists"
    assert not [m for m in moves if m[0] == "low"], "no downward move from Low exists"
