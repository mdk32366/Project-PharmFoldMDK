"""D-060 / D-041 — the scorer's test surface, written to bite.

The load-bearing tests here are the **leakage** ones (§3.1–3.3), because their failures are
invisible in the output: an evidence score that reaches the fit, a standardization computed over
the held-out row, a λ selected on full data. Each is asserted as a property, not left to review.
Alongside them the pre-registration is pinned (seven parameters, the 13-point λ grid, no `random`
import, 5-fold inner CV), and correctness is checked against hand-computed expectations (a
predictable-sign fit, a Spearman with a tie block, non-convergence that raises).

Fixtures use distinctive non-round values throughout — a false green in a scorer test propagates
straight into the reported result.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from core import scorer
from core.scorer import (
    INNER_CV_FOLDS,
    LAMBDA_GRID,
    N_PARAMS,
    LambdaChoice,
    ScorerNonConvergence,
    ScorerRow,
    assign_folds,
    average_ranks,
    irls_fit,
    leave_one_out,
    run_scorer,
    scorer_version,
    spearman,
)

FEATS = (1.13, 2.27, 3.41, 4.59, 5.73, 6.87)   # distinctive shared tail; feature 0 varies per row


def _row(symbol, f0, label, *, in_ranking=True, evidence=None, reason=None) -> ScorerRow:
    return ScorerRow(symbol, (f0, *FEATS[1:]), label, in_ranking, evidence, reason)


def _separable_ranking_set() -> list[ScorerRow]:
    """Ten ranking-set rows, feature 0 separating the four positives from the six negatives, with
    distinctive values so no accidental tie or zero hides a bug."""
    return [
        _row("PA", 0.71, 1, evidence=5.0), _row("PB", 1.33, 1, evidence=4.0),
        _row("PC", 1.94, 1), _row("PD", 2.58, 1, evidence=5.0),
        _row("NA", -2.17, 0, evidence=4.0), _row("NB", -1.61, 0), _row("NC", -1.19, 0),
        _row("ND", -0.73, 0), _row("NE", -0.34, 0), _row("NF", 0.22, 0),
    ]


# ── pre-registration ─────────────────────────────────────────────────────────
def test_exactly_seven_parameters():
    assert N_PARAMS == 7                                    # six coefficients + intercept (D-041)
    model = irls_fit(_separable_ranking_set(), 1.0)
    assert len(model.coefficients) == 6
    assert isinstance(model.intercept, float)


def test_lambda_grid_is_thirteen_points_1e_minus3_to_1e3():
    assert len(LAMBDA_GRID) == 13                           # D-060 dec 3
    assert LAMBDA_GRID[0] == pytest.approx(1e-3)
    assert LAMBDA_GRID[-1] == pytest.approx(1e3)
    # log-spaced: successive ratios equal
    ratios = [LAMBDA_GRID[i + 1] / LAMBDA_GRID[i] for i in range(12)]
    assert all(r == pytest.approx(ratios[0]) for r in ratios)


def test_no_random_import_in_the_scorer():
    """D-060 dec 2: determinism is structural, not seed-dependent. A `random` import is the thing
    that would let a result move silently, so its absence is asserted over the source."""
    source = Path(scorer.__file__).read_text(encoding="utf-8")
    assert "import random" not in source
    assert "from random" not in source


def test_inner_cv_is_five_fold_stratified():
    assert INNER_CV_FOLDS == 5
    rows = _separable_ranking_set()
    folds = assign_folds(rows, INNER_CV_FOLDS)
    # stratified round-robin: the four positives spread across distinct folds, never all in one.
    pos_folds = [folds[i] for i, r in enumerate(rows) if r.label == 1]
    assert len(set(pos_folds)) == len(pos_folds)           # 4 positives → 4 distinct folds


def test_no_third_party_import_in_scorer():
    source = Path(scorer.__file__).read_text(encoding="utf-8")
    for banned in ("import numpy", "import scipy", "import sklearn", "from numpy", "from scipy"):
        assert banned not in source


# ── leakage: the invisible failures (§3.1–3.3) ───────────────────────────────
def test_scrambling_evidence_scores_leaves_coefficients_identical():
    """§3.1 — the one that invalidates silently. The evidence score is the COMPARATOR, never the
    label or a feature. Scrambling it must not move a single coefficient; if it does, it is in the
    fit and D-041's negative-outcome test is degenerate."""
    rows = _separable_ranking_set()
    base = run_scorer(rows).final_model
    # Permute the evidence scores across rows (a different comparator), keep features/labels.
    ev = [r.evidence_score for r in rows]
    scrambled_ev = ev[::-1]
    scrambled = [
        ScorerRow(r.symbol, r.features, r.label, r.in_ranking_set, scrambled_ev[i], r.exclusion_reason)
        for i, r in enumerate(rows)
    ]
    after = run_scorer(scrambled).final_model
    assert after.coefficients == base.coefficients
    assert after.intercept == base.intercept


def test_changing_a_held_out_rows_features_leaves_the_fold_model_unchanged():
    """§3.2 — standardization and the fit use the training fold only. Mutate a held-out positive's
    features to an extreme value; the fold that holds it out must produce byte-identical scores for
    every OTHER target (its model never saw the held-out row)."""
    rows = _separable_ranking_set()
    folds_before = {f.held_out_symbol: f for f in leave_one_out(rows)}
    mutated = [
        _row("PA", 999.9, 1, evidence=5.0) if r.symbol == "PA" else r for r in rows
    ]
    folds_after = {f.held_out_symbol: f for f in leave_one_out(mutated)}
    fb, fa = folds_before["PA"], folds_after["PA"]
    for other in ("PB", "PC", "PD", "NA", "NB", "NC", "ND", "NE", "NF"):
        assert fb.scores[other] == fa.scores[other], f"{other} moved — held-out features leaked"


def test_lambda_is_selected_without_the_held_out_target():
    """§3.3 — λ is selected inside each LOO fold, on the remainder only. An injected recorder
    captures every training set the selector received; the held-out symbol must never appear."""
    rows = _separable_ranking_set()
    seen: dict[str, set[str]] = {}
    calls: list[set[str]] = []

    def recording_selector(train):
        calls.append({r.symbol for r in train})
        return LambdaChoice(1.0, "5fold", False)

    # Drive LOO with the recorder; match each call to the fold it belongs to by order.
    positives = sorted((r for r in rows if r.label == 1), key=lambda r: r.symbol)
    folds = leave_one_out(rows, lambda_selector=recording_selector)
    assert len(calls) == len(positives)
    for held, train_symbols in zip([p.symbol for p in positives], calls):  # noqa: B905
        assert held not in train_symbols, f"{held} leaked into its own λ selection"


# ── correctness ──────────────────────────────────────────────────────────────
def test_determinism_byte_identical():
    rows = _separable_ranking_set()
    a = run_scorer(rows)
    b = run_scorer(rows)
    assert a.final_model.coefficients == b.final_model.coefficients
    assert a.structural_percentiles == b.structural_percentiles
    assert a.spearman == b.spearman


def test_hand_checkable_fit_signs():
    """A separable fixture where feature 0 increases with the positive class: its coefficient must
    be positive, and a clear positive must score above a clear negative. Asserted by sign/order,
    not against whatever the code first emitted."""
    model = irls_fit(_separable_ranking_set(), 1.0)
    assert model.coefficients[0] > 0
    lo = model.predict_proba((-2.17, *FEATS[1:]))
    hi = model.predict_proba((2.58, *FEATS[1:]))
    assert hi > 0.5 > lo


def test_non_convergence_raises():
    """A perfectly separable fixture with no penalty (λ = 0) drives the coefficients to infinity;
    IRLS must RAISE, not return a silent estimate (D-060 dec 1)."""
    with pytest.raises(ScorerNonConvergence):
        irls_fit(_separable_ranking_set(), 0.0)


def test_perfect_separation_stays_finite_under_l2():
    """The same separable data with L2 converges to finite coefficients — one of the reasons D-041
    chose the penalty (§3.4). Not a bug, not a reason to drop features or targets."""
    model = irls_fit(_separable_ranking_set(), 1.0)
    assert all(abs(c) < 1e3 for c in model.coefficients)
    assert model.n_iter <= 100


def test_spearman_hand_fixture_with_a_tie_block():
    """x has a tie block; Spearman = Pearson on average-tie ranks. Hand value: ranks x=[1,2.5,2.5,4],
    y=[1,2,3,4] → r = 4.5 / (sqrt(4.5)·sqrt(5)) = 0.94868."""
    assert spearman([1.0, 2.0, 2.0, 4.0], [10.0, 20.0, 30.0, 40.0]) == pytest.approx(0.94868, abs=1e-5)


def test_average_rank_ties():
    assert average_ranks([1.0, 2.0, 2.0, 4.0]) == [1.0, 2.5, 2.5, 4.0]
    assert average_ranks([5.0, 5.0, 5.0]) == [2.0, 2.0, 2.0]


# ── shape of the result ──────────────────────────────────────────────────────
def test_loo_returns_a_distribution_length_equals_positive_count():
    rows = _separable_ranking_set()
    report = run_scorer(rows)
    n_pos = sum(1 for r in rows if r.label == 1)
    assert len(report.structural_percentiles) == n_pos     # a distribution, not a scalar
    assert all(0.0 <= p <= 1.0 for p in report.structural_percentiles)


def test_percentiles_are_computed_against_the_ranking_set():
    """D-060 dec 5: the reference set is the ranking set, not the folded cohort. A fixture whose
    ranking set (10) and folded set (12, incl. 2 excluded) differ in size — the excluded rows must
    NOT be in any fold's score set, so the percentile denominator is the ranking set."""
    rows = _separable_ranking_set() + [
        _row("XLOW", 99.0, 1, in_ranking=False, reason="below_floor"),
        _row("XOUT", 88.0, 0, in_ranking=False, reason="held_out"),
    ]
    folds = leave_one_out([r for r in rows if r.in_ranking_set])
    for f in folds:
        assert len(f.scores) == 10                          # the ranking set, not 12
        assert "XLOW" not in f.scores and "XOUT" not in f.scores


def test_head_to_head_uses_one_common_reference_set():
    """D-060 dec 8: both head-to-head distributions live in the common reference set (targets with
    a structural AND an evidence score). Four ranking rows carry evidence (PA, PB, PD positives, NA
    negative), so the common reference set is 4, and the three held-out positives among them drive
    equal-length structural/evidence lists."""
    report = run_scorer(_separable_ranking_set())
    assert report.headto_reference_n == 4                   # PA, PB, PD, NA carry evidence
    assert len(report.headto_structural_percentiles) == len(report.headto_evidence_percentiles)
    assert len(report.headto_structural_percentiles) == 3  # the three held-out positives with evidence


def test_excluded_targets_are_reported_with_reasons():
    """§3.5 — below-floor / held_out / not_folded targets are reported separately with their
    reason, never silently dropped."""
    rows = _separable_ranking_set() + [
        _row("CXCR5L", 47.6, 1, in_ranking=False, reason="below_floor"),
        _row("MSLNL", 75.0, 0, in_ranking=False, reason="held_out"),
    ]
    report = run_scorer(rows)
    excluded = dict(report.excluded)
    assert excluded["CXCR5L"] == "below_floor"
    assert excluded["MSLNL"] == "held_out"
    # excluded targets do not appear in the ranking
    ranked_symbols = {s for s, _, _ in report.ranking}
    assert "CXCR5L" not in ranked_symbols and "MSLNL" not in ranked_symbols


def test_every_statistic_carries_its_denominator():
    """§3.6 — a statistic without its denominator is not reportable (D-024, D-041 dec 3)."""
    report = run_scorer(_separable_ranking_set())
    assert report.n_ranking_set == 10
    assert report.spearman_n == report.headto_reference_n   # Spearman over the common set
    assert report.n_fit_positives == 4


def test_scorer_version_is_the_source_hash():
    import hashlib
    expected = hashlib.sha256(Path(scorer.__file__).read_bytes()).hexdigest()[:12]
    assert scorer_version() == expected
    assert len(scorer_version()) == 12


# ── D-063: per-fold non-convergence, and the LOO independent of the full-data fit ──
def test_a_fold_that_raises_is_recorded_and_does_not_abort_the_loop():
    """D-063 dec 2: a fold that fails to converge produces no percentile, is NAMED, and the loop
    completes over the survivors — one bad fold must not discard the other eleven. Forced by an
    injected selector that hands PA's fold λ=0 on separable data (→ singular) and everyone else a
    safe λ."""
    rows = _separable_ranking_set()                        # 4 positives: PA, PB, PC, PD
    def selector(train):
        symbols = {r.symbol for r in train}
        if "PA" not in symbols:                            # PA held out → this is PA's fold
            return LambdaChoice(0.0, "5fold", True)        # λ=0 on separable data → raises
        return LambdaChoice(5.0, "5fold", False)           # everyone else converges
    report = run_scorer(rows, lambda_selector=selector)
    assert report.nonconvergent_folds == ["PA"]            # named, not dropped
    assert report.converged_fold_count == 3
    assert len(report.structural_percentiles) == 3         # distribution over the survivors
    assert report.n_fit_positives == 4                     # denominator travels: 3 of 4
    pa = next(t for t in report.lambda_per_fold if t["symbol"] == "PA")
    assert pa["converged"] is False                        # PA flagged non-convergent in the per-fold record


def test_full_data_nonconvergence_does_not_abort_the_loo():
    """D-063 dec 1: the pre-registered LOO does not depend on the ranking-table full-data fit, so a
    full-data non-convergence must leave the distribution intact. Forced by a selector that raises
    ONLY the full-data fit (the call that sees all rows) while every fold converges."""
    rows = _separable_ranking_set()
    n_all = len(rows)
    def selector(train):
        if len(train) == n_all:                            # the full-data fit sees every row
            return LambdaChoice(0.0, "5fold", True)        # λ=0 on separable data → raises
        return LambdaChoice(5.0, "5fold", False)           # each fold (one row fewer) converges
    report = run_scorer(rows, lambda_selector=selector)
    # the ranking table is gone, but the pre-registered distribution stands
    assert report.final_fit_converged is False
    assert report.final_model is None
    assert report.ranking == []
    assert report.spearman is None                         # Spearman needs the full-data model
    assert report.converged_fold_count == 4                # the LOO still ran, all four folds
    assert len(report.structural_percentiles) == 4
    assert report.nonconvergent_folds == []


def test_zero_positives_raises_degenerate_label_set():
    """D-064 dec 2: a fit set with no positives is refused DISTINCTLY, before any IRLS iteration —
    so a meaningless input can never masquerade as a non-convergence result about the data (the
    zero-positive artifact that cost a full interpretive arc)."""
    from core.scorer import DegenerateLabelSet
    rows = [_row(f"N{i}", -2.0 + 0.3 * i, 0) for i in range(8)]     # all negatives, all in ranking set
    with pytest.raises(DegenerateLabelSet) as exc:
        run_scorer(rows)
    assert "0 positives" in str(exc.value) and "8 negatives" in str(exc.value)


def test_zero_negatives_raises_degenerate_label_set():
    from core.scorer import DegenerateLabelSet
    rows = [_row(f"P{i}", 0.3 * i, 1) for i in range(8)]            # all positives
    with pytest.raises(DegenerateLabelSet) as exc:
        run_scorer(rows)
    assert "0 negatives" in str(exc.value)


def test_intercept_stays_unpenalized_source_pin():
    """D-063 refusal: the intercept penalty coefficient stays 0 — penalizing it would make the
    Hessian invertible and the raise disappear by changing the model after seeing a result. Pinned
    over the source so that change reddens the gate."""
    source = Path(scorer.__file__).read_text(encoding="utf-8")
    assert "penalty = [0.0] + [1.0] * N_FEATURES" in source
