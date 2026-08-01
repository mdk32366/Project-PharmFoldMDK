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
    FEATURE_SETS,
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


# ── D-065: the two named ablations, and the refusal of everything else ──
def test_ablation_refuses_any_unnamed_feature_set():
    """D-065 dec 4: only `no_plddt` and `plddt_only` are permitted — an arbitrary subset raises, so
    fishing is prevented by construction, not by discipline."""
    rows = _separable_ranking_set()
    for bad in ("ecd_only", "feature_3", "", "all_but_one"):
        with pytest.raises(ValueError, match="D-065"):
            run_scorer(rows, feature_set=bad)


def test_ablation_parameter_counts():
    """D-065 dec 1: `no_plddt` fits 5 parameters (4 features + intercept), `plddt_only` fits 3
    (2 + intercept); the pre-registered path is unchanged at 7."""
    rows = _separable_ranking_set()
    assert len(run_scorer(rows, feature_set="preregistered").final_model.coefficients) == 6  # 7 params
    assert len(run_scorer(rows, feature_set="no_plddt").final_model.coefficients) == 4         # 5 params
    assert len(run_scorer(rows, feature_set="plddt_only").final_model.coefficients) == 2       # 3 params


def test_ablation_path_reasserts_the_comparator_leakage_guard():
    """D-065: the leakage guards are not exempted by a narrower feature set. Scrambling the evidence
    scores must still leave the ablation's coefficients byte-identical (§3.1, one layer over)."""
    rows = _separable_ranking_set()
    base = run_scorer(rows, feature_set="no_plddt").final_model
    ev = [r.evidence_score for r in rows]
    scrambled = [ScorerRow(r.symbol, r.features, r.label, r.in_ranking_set, ev[::-1][i], r.exclusion_reason)
                 for i, r in enumerate(rows)]
    after = run_scorer(scrambled, feature_set="no_plddt").final_model
    assert after.coefficients == base.coefficients and after.intercept == base.intercept


def test_ablation_is_deterministic():
    rows = _separable_ranking_set()
    a = run_scorer(rows, feature_set="plddt_only")
    b = run_scorer(rows, feature_set="plddt_only")
    assert a.final_model.coefficients == b.final_model.coefficients
    assert a.structural_percentiles == b.structural_percentiles


def test_all_folds_raise_produces_no_distribution_without_crashing():
    """D-063's all-folds-raise path, pinned here (folded into D-065): when every fold raises,
    `loo_status='none'`, the distribution is empty, every fold is named non-convergent, and
    `run_scorer` does not crash — the regime a two-feature ablation is most likely to reach."""
    rows = _separable_ranking_set()
    def selector(train):
        return LambdaChoice(0.0, "5fold", True)          # λ=0 on separable data → every fit raises
    report = run_scorer(rows, lambda_selector=selector)
    assert report.loo_status == "none"
    assert report.structural_percentiles == []
    assert report.converged_fold_count == 0
    assert len(report.nonconvergent_folds) == report.n_fit_positives   # all named
    assert report.final_fit_converged is False


def test_preregistered_path_stays_at_six_features():
    """D-065 dec 5: the ablations must not touch the pre-registered count. The default fit is still
    six coefficients + intercept."""
    model = run_scorer(_separable_ranking_set()).final_model      # default feature_set='preregistered'
    assert len(model.coefficients) == 6
    assert len(model.contributions((1.0,) * 6)) == 6


# ── D-075: geom_proxy — the confidence-blind ablation, feature 7 at index 6 ──
FEAT7 = 7.91                       # feature 7's distinctive shared value (membrane-proximal SASA)


def _row7(symbol, f0, label, *, in_ranking=True, evidence=None, reason=None) -> ScorerRow:
    """A SEVEN-feature row: the six D-027 values plus feature 7 (D-075) at index 6 — the shape
    `scripts/fit_scorer.py` now assembles, so the tests below exercise the real width."""
    return ScorerRow(symbol, (f0, *FEATS[1:], FEAT7), label, in_ranking, evidence, reason)


def _separable_ranking_set_7() -> list[ScorerRow]:
    return [
        _row7("PA", 0.71, 1, evidence=5.0), _row7("PB", 1.33, 1, evidence=4.0),
        _row7("PC", 1.94, 1), _row7("PD", 2.58, 1, evidence=5.0),
        _row7("NA", -2.17, 0, evidence=4.0), _row7("NB", -1.61, 0), _row7("NC", -1.19, 0),
        _row7("ND", -0.73, 0), _row7("NE", -0.34, 0), _row7("NF", 0.22, 0),
    ]


def test_geom_proxy_fits_six_parameters():
    """D-075 dec 1: `geom_proxy` = features 1,2,5,6 + 7 → five features, SIX parameters. One more
    than `no_plddt`'s five, because the amputated information is restored rather than dropped."""
    model = run_scorer(_separable_ranking_set_7(), feature_set="geom_proxy").final_model
    assert len(model.coefficients) == 5           # 5 features + intercept = 6 parameters


def test_geom_proxy_is_refused_if_not_named_and_unnamed_sets_still_raise():
    """D-075 dec 5 inherits D-065 dec 4: the permitted sets are exactly three. Anything else raises,
    so no fourth ablation can be run without a new dated entry."""
    assert sorted(FEATURE_SETS) == ["geom_proxy", "no_plddt", "plddt_only", "preregistered"]
    rows = _separable_ranking_set_7()
    for bad in ("geom_proxy_v2", "sasa_only", "feature_7", "no_plddt+7"):
        with pytest.raises(ValueError):
            run_scorer(rows, feature_set=bad)


def test_geom_proxy_actually_reads_feature_7_not_a_copy_of_no_plddt():
    """⚠ The test that makes `geom_proxy` real. If index 6 were dropped or mis-indexed, `geom_proxy`
    would silently BE `no_plddt` — an ablation that looks new and measures the old thing, which
    would void D-075 while every other test stayed green. Varying ONLY feature 7 must move the
    `geom_proxy` fit, and must leave `no_plddt` untouched."""
    rows = _separable_ranking_set_7()
    varied = [ScorerRow(r.symbol, (*r.features[:6], FEAT7 + (2.5 if r.label == 1 else -2.5)),
                        r.label, r.in_ranking_set, r.evidence_score, r.exclusion_reason)
              for r in rows]
    gp_base = run_scorer(rows, feature_set="geom_proxy").final_model
    gp_varied = run_scorer(varied, feature_set="geom_proxy").final_model
    assert gp_base.coefficients != gp_varied.coefficients, (
        "changing feature 7 did not change the geom_proxy fit - index 6 is not being read, so "
        "geom_proxy is a relabelled no_plddt and D-075 would be void"
    )
    np_base = run_scorer(rows, feature_set="no_plddt").final_model
    np_varied = run_scorer(varied, feature_set="no_plddt").final_model
    assert np_base.coefficients == np_varied.coefficients, (
        "changing feature 7 changed the no_plddt fit - no_plddt is picking up a column it must not"
    )


def test_seven_wide_rows_do_not_leak_feature_7_into_the_preregistered_path():
    """⚠⚠ THE LEAK GUARD (D-065 dec 5 / D-075 dec 5). Rows now arrive SEVEN features wide. The
    pre-registered fit must still be six features / seven parameters — it projects onto indices
    0-5 unconditionally. Before D-075 the projection was skipped for the pre-registered set (a
    no-op while every row was six long); with a seventh column present that skip would have fit
    the graded model on seven features and eight parameters, invisibly."""
    model = run_scorer(_separable_ranking_set_7()).final_model     # default = 'preregistered'
    assert len(model.coefficients) == 6, (
        f"pre-registered fit used {len(model.coefficients)} features against a 7-wide row - "
        "feature 7 leaked into the graded path"
    )
    # And the fit is byte-identical to the same rows without a seventh column present at all.
    six_wide = run_scorer(_separable_ranking_set()).final_model
    assert model.coefficients == six_wide.coefficients and model.intercept == six_wide.intercept, (
        "the presence of a seventh column changed the pre-registered result"
    )


def test_geom_proxy_reasserts_the_comparator_leakage_guard():
    """D-075 dec 5: the three D-060 guards are not exempted by the new feature set. Scrambling the
    evidence comparator must leave `geom_proxy`'s coefficients byte-identical — label and comparator
    are different quantities and never mix (D-041)."""
    rows = _separable_ranking_set_7()
    base = run_scorer(rows, feature_set="geom_proxy").final_model
    ev = [r.evidence_score for r in rows]
    scrambled = [ScorerRow(r.symbol, r.features, r.label, r.in_ranking_set, ev[::-1][i], r.exclusion_reason)
                 for i, r in enumerate(rows)]
    after = run_scorer(scrambled, feature_set="geom_proxy").final_model
    assert after.coefficients == base.coefficients and after.intercept == base.intercept


def test_geom_proxy_held_out_features_do_not_reach_the_fold_model():
    """D-060 guard 2, re-asserted on the geom_proxy path (D-075 dec 5): mutating a HELD-OUT row's
    features — including feature 7 — must not move any OTHER target's score in the fold that holds
    it out. The fold's model never saw the held-out row."""
    def project(rs):
        idx = FEATURE_SETS["geom_proxy"]
        return [ScorerRow(r.symbol, tuple(r.features[i] for i in idx), r.label,
                          r.in_ranking_set, r.evidence_score, r.exclusion_reason) for r in rs]

    rows = _separable_ranking_set_7()
    before = {f.held_out_symbol: f for f in leave_one_out(project(rows))}
    mutated = [ScorerRow(r.symbol, (999.9,) * 7 if r.symbol == "PA" else r.features,
                         r.label, r.in_ranking_set, r.evidence_score, r.exclusion_reason)
               for r in rows]
    after = {f.held_out_symbol: f for f in leave_one_out(project(mutated))}
    for other in ("PB", "PC", "PD", "NA", "NB", "NC", "ND", "NE", "NF"):
        assert before["PA"].scores[other] == after["PA"].scores[other], (
            f"{other} moved when held-out PA's features (incl. feature 7) changed - leakage"
        )


def test_geom_proxy_is_deterministic():
    """D-075 dec: same input, two runs, byte-identical coefficients and distribution. No RNG."""
    rows = _separable_ranking_set_7()
    a = run_scorer(rows, feature_set="geom_proxy")
    b = run_scorer(rows, feature_set="geom_proxy")
    assert a.final_model.coefficients == b.final_model.coefficients
    assert a.structural_percentiles == b.structural_percentiles


def test_geom_proxy_feature_indices_match_no_plddt_plus_feature_seven():
    """D-075 dec 1, pinned as a set relation rather than a literal tuple, so the intent survives a
    reordering: geom_proxy is exactly no_plddt's columns plus index 6, and nothing else."""
    assert set(FEATURE_SETS["geom_proxy"]) == set(FEATURE_SETS["no_plddt"]) | {6}
    assert 2 not in FEATURE_SETS["geom_proxy"] and 3 not in FEATURE_SETS["geom_proxy"], (
        "geom_proxy must contain NEITHER pLDDT feature (3 or 4) - that is the whole point"
    )


def test_intercept_stays_unpenalized_source_pin():
    """D-063 refusal: the intercept penalty coefficient stays 0 — penalizing it would make the
    Hessian invertible and the raise disappear by changing the model after seeing a result. Pinned
    over the source so that change reddens the gate."""
    source = Path(scorer.__file__).read_text(encoding="utf-8")
    # the intercept coefficient stays 0.0 (unpenalized); the count is dynamic for the D-065 ablations
    assert "penalty = [0.0] + [1.0] * (n_params - 1)" in source
