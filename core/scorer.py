"""D-041 / D-060 — the ADC-suitability scorer: L2-regularized logistic regression, by hand.

**ZERO third-party math** (D-060 §1). `numpy`/`scipy`/`scikit-learn` are in no lock file, and
this module could reach the serving tier, so everything — standardization, IRLS, the 7×7 linear
solve, Spearman — is standard library. The problem is genuinely tiny (six features, ≤56 rows,
seven parameters); a 7×7 solve is not a numerical challenge, and a model small enough to read end
to end is the strongest form of D-041's argument that its smallness is what makes it defensible.

Pre-registration is the whole point (D-015 §3 → D-041 → D-060). Every operational parameter is
fixed here BEFORE any leave-one-out distribution exists:

- **IRLS** (Newton on the L2-penalized log-likelihood), converge `max|Δβ| < 1e-8` or **raise** at
  100 iterations — a silently unconverged fit is a result that looks like a result (D-060 dec 1).
- **No RNG** — fold assignment is deterministic round-robin over symbol-sorted rows within each
  label stratum; a test asserts no `random` import (D-060 dec 2).
- **λ grid** = 13 log-spaced points 1e-3..1e3, never re-centred after a fit; a selected edge value
  is a reported finding (D-060 dec 3).
- **Inner CV** = 5-fold stratified on the LOO training remainder, LOPO fallback under 5 positives
  (D-060 dec 4).
- **Percentile reference set** = the ranking set (`ranked ∧ folded ∧ pLDDT ≥ 50`), not "the folded
  cohort" (D-060 dec 5, F-002).
- **Ties take average rank** (D-060 dec 6); the score is the predicted probability (dec 7).
- **The head-to-head** puts both percentile distributions on ONE common reference set — the targets
  carrying a structural *and* an evidence score — because a percentile among 56 and a percentile
  among 12 are not comparable (D-060 dec 8). The comparator is two-valued, so its distribution is
  degenerate by construction; that bound is recorded before the result exists.

⚠ **The label and the comparator are different quantities.** Label = Group B membership. Comparator
= the evidence score. The evidence score never enters the feature matrix or the label — if it did,
the comparator would predict the label by construction and D-041's negative-outcome test would go
degenerate while looking normal (D-060 §3.1). A test scrambles the evidence scores and asserts the
coefficients are byte-identical.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from core.features import FEATURE_NAMES

N_FEATURES = len(FEATURE_NAMES)          # 6 (D-027, fixed)
N_PARAMS = N_FEATURES + 1                # 7 = six coefficients + intercept (D-041 / D-060)

# λ grid: 13 log-spaced points from 1e-3 to 1e3 (D-060 dec 3). Pinned by a test; never re-centred.
LAMBDA_GRID = tuple(10.0 ** (-3.0 + 6.0 * i / 12.0) for i in range(13))
INNER_CV_FOLDS = 5                       # D-060 dec 4
MAX_ITER = 100                           # D-060 dec 1
CONVERGENCE_TOL = 1e-8                   # max|Δβ| (D-060 dec 1)


class ScorerError(Exception):
    """Base for scorer failures — always raised, never a silent estimate."""


class ScorerNonConvergence(ScorerError):
    """IRLS did not reach `max|Δβ| < 1e-8` within 100 iterations (D-060 dec 1)."""


class DegenerateLabelSet(ScorerError):
    """The fit set has zero positives or zero negatives (D-064 dec 2). Raised BEFORE any IRLS
    iteration, distinctly from `ScorerNonConvergence`, because a degenerate *input* fails with the
    identical signature as a degenerate *geometry* — and a meaningless input must never produce a
    raise that reads like a result about the data (the zero-positive artifact of D-064)."""


# ── a row the scorer consumes (decoupled from the DB / the read API) ─────────
@dataclass(frozen=True)
class ScorerRow:
    """One target as the scorer sees it. `features` is the six D-027 values in `FEATURE_NAMES`
    order. `label` is Group B membership (1/0) — NOT the evidence score. `in_ranking_set` is
    `ranked ∧ folded ∧ pLDDT ≥ 50` (the reference set, D-060 dec 5). `evidence_score` is the
    comparator (present for the published subset, else None). `exclusion_reason` names why a row
    is out of the ranking set (below_floor / held_out / not_folded), reported never dropped."""

    symbol: str
    features: tuple[float, ...]
    label: int
    in_ranking_set: bool
    evidence_score: Optional[float] = None
    exclusion_reason: Optional[str] = None


# ── linear algebra (7×7, pure stdlib) ────────────────────────────────────────
def _dot(a: list[float], b: list[float]) -> float:
    return sum(ai * bi for ai, bi in zip(a, b))  # noqa: B905


def gaussian_solve(matrix: list[list[float]], rhs: list[float]) -> list[float]:
    """Solve `A x = b` by Gaussian elimination with partial pivoting. Raises `ScorerError` on a
    singular system — a singular Hessian mid-fit is a non-convergence signal, not something to
    paper over with a pseudo-inverse."""
    n = len(rhs)
    a = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]   # augmented
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-15:
            raise ScorerError("singular matrix in gaussian_solve (Hessian not invertible)")
        a[col], a[pivot] = a[pivot], a[col]
        pv = a[col][col]
        for r in range(n):
            if r == col:
                continue
            factor = a[r][col] / pv
            for c in range(col, n + 1):
                a[r][c] -= factor * a[col][c]
    return [a[i][n] / a[i][i] for i in range(n)]


def _sigmoid(z: float) -> float:
    if z >= 0.0:
        return 1.0 / (1.0 + math.exp(-z))
    ez = math.exp(z)
    return ez / (1.0 + ez)


def _log1pexp(z: float) -> float:
    """Numerically stable log(1 + e^z)."""
    if z > 35.0:
        return z
    if z < -35.0:
        return 0.0
    return math.log1p(math.exp(z))


# ── standardization (training rows only — D-060 §3.2) ────────────────────────
@dataclass(frozen=True)
class Standardizer:
    means: tuple[float, ...]
    stds: tuple[float, ...]

    def apply(self, features: tuple[float, ...]) -> list[float]:
        return [
            (features[j] - self.means[j]) / self.stds[j] if self.stds[j] > 0 else 0.0
            for j in range(len(features))
        ]


def fit_standardizer(rows: list[ScorerRow]) -> Standardizer:
    """Mean/std per feature over the given rows ONLY. Computing these over all rows would leak a
    held-out target into its own evaluation (D-060 §3.2) — invisible in the output, so it is a
    tested property, not a convention."""
    n = len(rows)
    means = []
    stds = []
    for j in range(N_FEATURES):
        col = [r.features[j] for r in rows]
        mu = sum(col) / n
        var = sum((v - mu) ** 2 for v in col) / n
        means.append(mu)
        stds.append(math.sqrt(var))
    return Standardizer(tuple(means), tuple(stds))


# ── the fit: L2-penalized logistic regression via IRLS ───────────────────────
@dataclass(frozen=True)
class Model:
    """A fitted model: seven parameters (intercept + six standardized coefficients), the
    standardizer they were fit under, the λ used, and the iteration count."""

    intercept: float
    coefficients: tuple[float, ...]      # six, on standardized features (D-041 attribution basis)
    standardizer: Standardizer
    lam: float
    n_iter: int

    def _linear(self, features: tuple[float, ...]) -> float:
        z = self.intercept
        std = self.standardizer.apply(features)
        for k in range(N_FEATURES):
            z += self.coefficients[k] * std[k]
        return z

    def predict_proba(self, features: tuple[float, ...]) -> float:
        return _sigmoid(self._linear(features))

    def contributions(self, features: tuple[float, ...]) -> list[float]:
        """The per-feature attribution β_k · x_k on standardized features (D-041 decision 1) — the
        statement 'feature k contributes this much to this target's score', no post-hoc explainer."""
        std = self.standardizer.apply(features)
        return [self.coefficients[k] * std[k] for k in range(N_FEATURES)]


def _penalized_neg_loglik(design: list[list[float]], y: list[int], beta: list[float], lam: float) -> float:
    ll = 0.0
    for i, row in enumerate(design):
        z = _dot(row, beta)
        ll += y[i] * z - _log1pexp(z)
    # intercept (index 0) is unpenalized
    reg = 0.5 * lam * sum(beta[j] * beta[j] for j in range(1, N_PARAMS))
    return -ll + reg


def irls_fit(rows: list[ScorerRow], lam: float, *, standardizer: Optional[Standardizer] = None) -> Model:
    """Fit L2-penalized logistic regression by Newton–Raphson (IRLS). The intercept is
    unpenalized. Step-halving guards the early iterations; convergence is `max|Δβ| < 1e-8`.
    **Raises `ScorerNonConvergence` at 100 iterations** — never a silent estimate (D-060 dec 1)."""
    if standardizer is None:
        standardizer = fit_standardizer(rows)
    design = [[1.0] + standardizer.apply(r.features) for r in rows]   # intercept column + 6 std feats
    y = [r.label for r in rows]
    beta = [0.0] * N_PARAMS
    penalty = [0.0] + [1.0] * N_FEATURES     # do not penalize the intercept
    prev_obj = _penalized_neg_loglik(design, y, beta, lam)

    for iteration in range(1, MAX_ITER + 1):
        grad = [0.0] * N_PARAMS
        hess = [[0.0] * N_PARAMS for _ in range(N_PARAMS)]
        for i, row in enumerate(design):
            p = _sigmoid(_dot(row, beta))
            w = p * (1.0 - p)
            resid = y[i] - p
            for a in range(N_PARAMS):
                grad[a] += row[a] * resid
                wa = w * row[a]
                for b in range(N_PARAMS):
                    hess[a][b] += wa * row[b]
        for j in range(N_PARAMS):
            grad[j] -= lam * penalty[j] * beta[j]
            hess[j][j] += lam * penalty[j]

        try:
            delta = gaussian_solve(hess, grad)      # Newton step: H Δ = g
        except ScorerError as exc:
            raise ScorerNonConvergence(
                f"IRLS Hessian became singular at iteration {iteration} (lam={lam:g}) - "
                f"the fit is not converging to a finite solution") from exc

        # Step-halving: accept the largest step (≤1) that does not increase the objective.
        step = 1.0
        candidate = beta
        for _ in range(60):
            candidate = [beta[j] + step * delta[j] for j in range(N_PARAMS)]
            if _penalized_neg_loglik(design, y, candidate, lam) <= prev_obj + 1e-12:
                break
            step *= 0.5
        max_change = max(abs(candidate[j] - beta[j]) for j in range(N_PARAMS))
        beta = candidate
        prev_obj = _penalized_neg_loglik(design, y, beta, lam)
        if max_change < CONVERGENCE_TOL:
            return Model(beta[0], tuple(beta[1:]), standardizer, lam, iteration)

    raise ScorerNonConvergence(
        f"IRLS did not converge (max abs coef change >= {CONVERGENCE_TOL:g}) in {MAX_ITER} "
        f"iterations at lam={lam:g}")


# ── deterministic stratified folds (no RNG — D-060 dec 2) ────────────────────
def assign_folds(rows: list[ScorerRow], k: int) -> list[int]:
    """Fold index per row: sort by symbol WITHIN each label stratum, assign round-robin 0..k-1.
    Deterministic and seedless — a seed-dependent split can move silently (D-060 dec 2)."""
    fold_of: dict[str, int] = {}
    for label in (1, 0):
        stratum = sorted((r for r in rows if r.label == label), key=lambda r: r.symbol)
        for i, r in enumerate(stratum):
            fold_of[r.symbol] = i % k
    return [fold_of[r.symbol] for r in rows]


LambdaSelector = Callable[[list[ScorerRow]], "LambdaChoice"]


@dataclass(frozen=True)
class LambdaChoice:
    lam: float
    scheme: str            # "5fold" | "lopo"
    at_grid_edge: bool


def select_lambda(train: list[ScorerRow]) -> LambdaChoice:
    """Choose λ by inner cross-validation on the training rows ONLY (D-060 §3.3). 5-fold stratified;
    falls back to leave-one-positive-out when the remainder holds fewer than 5 positives (D-060 dec
    4). Scores each λ by mean held-out log-likelihood (higher is better). A λ selected at a grid
    edge is flagged, not silently fixed by widening the grid (D-060 dec 3)."""
    positives = [r for r in train if r.label == 1]
    if len(positives) >= INNER_CV_FOLDS:
        scheme = "5fold"
        fold_ids = assign_folds(train, INNER_CV_FOLDS)
        folds = [[train[i] for i in range(len(train)) if fold_ids[i] == f] for f in range(INNER_CV_FOLDS)]
    else:
        scheme = "lopo"                 # leave-one-positive-out
        folds = [[p] for p in sorted(positives, key=lambda r: r.symbol)]

    best_lam = LAMBDA_GRID[0]
    best_score = -math.inf
    for lam in LAMBDA_GRID:
        total_ll = 0.0
        n_val = 0
        for held in folds:
            held_symbols = {r.symbol for r in held}
            inner_train = [r for r in train if r.symbol not in held_symbols]
            if not inner_train or all(r.label == inner_train[0].label for r in inner_train):
                continue  # a degenerate inner split contributes nothing
            try:
                model = irls_fit(inner_train, lam)
            except ScorerNonConvergence:
                total_ll = -math.inf
                break
            for r in held:
                p = min(max(model.predict_proba(r.features), 1e-12), 1 - 1e-12)
                total_ll += r.label * math.log(p) + (1 - r.label) * math.log(1 - p)
                n_val += 1
        mean_ll = total_ll / n_val if n_val else -math.inf
        if mean_ll > best_score:
            best_score = mean_ll
            best_lam = lam
    at_edge = best_lam in (LAMBDA_GRID[0], LAMBDA_GRID[-1])
    return LambdaChoice(best_lam, scheme, at_edge)


# ── ranks, percentiles, Spearman (average-rank ties — D-060 dec 6) ───────────
def average_ranks(values: list[float]) -> list[float]:
    """Ranks with ties resolved to the average rank (1-based). D-060 decision 6."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0                       # average of the tied 1-based ranks
        for t in range(i, j + 1):
            ranks[order[t]] = avg
        i = j + 1
    return ranks


def percentile_within(score: float, reference: list[float]) -> float:
    """The average-rank percentile of `score` within `reference` (which includes `score` itself):
    (#strictly-less + ½·#equal) / N. Higher score → higher percentile. Ties share the midpoint."""
    n = len(reference)
    less = sum(1 for s in reference if s < score)
    equal = sum(1 for s in reference if s == score)
    return (less + 0.5 * equal) / n


def _pearson(a: list[float], b: list[float]) -> float:
    n = len(a)
    ma = sum(a) / n
    mb = sum(b) / n
    cov = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    va = math.sqrt(sum((a[i] - ma) ** 2 for i in range(n)))
    vb = math.sqrt(sum((b[i] - mb) ** 2 for i in range(n)))
    if va == 0.0 or vb == 0.0:
        return 0.0          # a constant series has no linear relationship to report
    return cov / (va * vb)


def spearman(x: list[float], y: list[float]) -> float:
    """Spearman rank correlation = Pearson on average-tie ranks (D-041 decision 4). Rank rather
    than value because both quantities here are ordinal by construction."""
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    return _pearson(average_ranks(x), average_ranks(y))


# ── the leave-one-out evaluation (D-041 decision 3 / D-060) ──────────────────
@dataclass
class LOOFold:
    held_out_symbol: str
    lam: float
    scheme: str
    lam_at_grid_edge: bool
    converged: bool                          # did this fold's fit converge? (D-063 dec 2)
    scores: Optional[dict[str, float]]       # per-target predicted probability, or None if it raised


def leave_one_out(
    ranking_rows: list[ScorerRow],
    *,
    lambda_selector: LambdaSelector = select_lambda,
) -> list[LOOFold]:
    """Hold out one Group B positive at a time; select λ by inner CV on the remainder ONLY; refit;
    predict a probability for every ranking-set target under that fold's model (D-041 dec 3).

    **A fold that fails to converge is recorded as producing no percentile (`converged=False`,
    `scores=None`) and does NOT abort the loop (D-063 dec 2)** — each fold trains on the same
    separable geometry that raised the full-data fit, so one bad fold must not discard the others.
    `lambda_selector` is injected so a test can assert it never receives the held-out target
    (D-060 §3.3)."""
    positives = sorted((r for r in ranking_rows if r.label == 1), key=lambda r: r.symbol)
    folds: list[LOOFold] = []
    for held in positives:
        train = [r for r in ranking_rows if r.symbol != held.symbol]
        choice = lambda_selector(train)
        try:
            model = irls_fit(train, choice.lam)
            scores = {r.symbol: model.predict_proba(r.features) for r in ranking_rows}
            converged = True
        except ScorerNonConvergence:
            scores = None
            converged = False
        folds.append(LOOFold(held.symbol, choice.lam, choice.scheme, choice.at_grid_edge,
                             converged, scores))
    return folds


# ── the assembled report ─────────────────────────────────────────────────────
@dataclass
class ScorerReport:
    scorer_version: str
    n_ranking_set: int
    n_fit_positives: int                     # total positives in the ranking set (the LOO denominator)
    # headline: held-out-positive percentiles, over the folds that CONVERGED (D-063 dec 2)
    structural_percentiles: list[float]
    nonconvergent_folds: list[str]           # held-out targets whose fold raised — named, not dropped
    # head-to-head, both within the common reference set (D-060 dec 8), over converged folds
    headto_reference_n: int
    headto_structural_percentiles: list[float]
    headto_evidence_percentiles: list[float]
    spearman: Optional[float]                # None if the full-data fit did not converge (or n<2)
    spearman_n: int
    lambda_per_fold: list[dict]              # {symbol, lam, converged} per fold (D-063 dec 2)
    lambda_at_grid_edge: bool
    excluded: list[tuple[str, str]]          # (symbol, reason) — reported, never dropped (D-060 §3.5)
    final_fit_converged: bool                # did the ranking-table full-data fit converge?
    final_fit_lambda: float
    final_model: Optional[Model]             # None if the full-data fit did not converge
    ranking: list[tuple[str, float, list[float]]]    # (symbol, score, contributions); empty if no final fit
    # the survivorship status (D-064 dec 5): which pre-registered statistics were producible
    loo_status: str                          # complete | partial | none
    fulldata_status: str                     # converged | raised
    status_detail: str                       # human reason for any blocked statistic

    @property
    def converged_fold_count(self) -> int:
        return len(self.structural_percentiles)


def run_scorer(
    all_rows: list[ScorerRow],
    *,
    lambda_selector: LambdaSelector = select_lambda,
) -> ScorerReport:
    """The full pre-registered evaluation. **The LOO runs FIRST and independently** (D-063 dec 1):
    the pre-registered percentile distribution does not depend on the ranking-table full-data fit,
    so a full-data non-convergence must not abort it. A fold that raises is recorded as producing no
    percentile and the distribution is reported over the survivors, with the non-convergent count
    and names carried (D-063 dec 2). The full-data fit (ranking table + Spearman) runs after and is
    non-fatal. **Does not persist anything and is not the fit run** — that is `scripts/fit_scorer.py`."""
    ranking_rows = [r for r in all_rows if r.in_ranking_set]
    excluded = sorted(
        [(r.symbol, r.exclusion_reason or "not in ranking set")
         for r in all_rows if not r.in_ranking_set]
    )

    # ── Degenerate-input guard, BEFORE any IRLS iteration (D-064 dec 2). Zero positives or zero
    # negatives fails with the identical signature as separation; refuse distinctly rather than
    # let a meaningless input raise a ScorerNonConvergence that reads like a result about the data. ──
    n_pos = sum(1 for r in ranking_rows if r.label == 1)
    n_neg = sum(1 for r in ranking_rows if r.label == 0)
    if n_pos == 0 or n_neg == 0:
        raise DegenerateLabelSet(
            f"degenerate label set: {n_pos} positives, {n_neg} negatives in the ranking set "
            f"(N={len(ranking_rows)}) - the fit is meaningless and is refused before iterating (D-064 dec 2)")

    # ── LOO FIRST and independently (D-063 dec 1). Per-fold non-convergence is survived (dec 2). ──
    folds = leave_one_out(ranking_rows, lambda_selector=lambda_selector)
    converged = [f for f in folds if f.converged]
    nonconvergent_folds = sorted(f.held_out_symbol for f in folds if not f.converged)
    structural_percentiles = [
        percentile_within(f.scores[f.held_out_symbol], list(f.scores.values())) for f in converged
    ]

    # Head-to-head over the converged folds within the common reference set (D-060 dec 8).
    common = [r for r in ranking_rows if r.evidence_score is not None]
    common_symbols = {r.symbol for r in common}
    headto_structural: list[float] = []
    headto_evidence: list[float] = []
    if common:
        evidence_by_symbol = {r.symbol: r.evidence_score for r in common}
        evidence_values = list(evidence_by_symbol.values())
        for f in converged:
            if f.held_out_symbol not in common_symbols:
                continue
            common_scores = [f.scores[s] for s in common_symbols]
            headto_structural.append(percentile_within(f.scores[f.held_out_symbol], common_scores))
            headto_evidence.append(
                percentile_within(evidence_by_symbol[f.held_out_symbol], evidence_values)
            )

    # ── The ranking-table full-data fit, AFTER the LOO and NON-FATAL to it (D-063 dec 1). ──
    final_choice = lambda_selector(ranking_rows)
    final_model: Optional[Model] = None
    try:
        final_model = irls_fit(ranking_rows, final_choice.lam)
    except ScorerNonConvergence:
        final_model = None                    # ranking + Spearman unavailable; the LOO still stands

    spearman_val: Optional[float] = None
    ranking: list[tuple[str, float, list[float]]] = []
    if final_model is not None:
        if len(common) >= 2:
            struct = [final_model.predict_proba(r.features) for r in common]
            evid = [r.evidence_score for r in common]
            spearman_val = spearman(struct, evid)
        ranking = sorted(
            [(r.symbol, final_model.predict_proba(r.features), final_model.contributions(r.features))
             for r in ranking_rows],
            key=lambda t: t[1],
            reverse=True,
        )

    lam_per_fold = [{"symbol": f.held_out_symbol, "lam": f.lam, "converged": f.converged} for f in folds]
    lam_edge = final_choice.at_grid_edge or any(f.lam_at_grid_edge for f in folds)

    # ── Survivorship status (D-064 dec 5): which pre-registered statistics were producible. ──
    n_converged = len(structural_percentiles)
    if n_converged == 0:
        loo_status = "none"
    elif n_converged == n_pos:
        loo_status = "complete"
    else:
        loo_status = "partial"
    fulldata_status = "converged" if final_model is not None else "raised"
    detail_parts: list[str] = []
    if loo_status != "complete":
        detail_parts.append(
            f"LOO {loo_status}: {n_converged} of {n_pos} folds converged"
            + (f"; non-convergent: {nonconvergent_folds}" if nonconvergent_folds else ""))
    if final_model is None:
        detail_parts.append(
            f"full-data fit did not converge at lam={final_choice.lam:g} - Spearman and ranking table "
            f"BLOCKED (D-064 dec 5), reported null with this reason")
    status_detail = "; ".join(detail_parts) if detail_parts else "all pre-registered statistics produced"

    return ScorerReport(
        scorer_version=scorer_version(),
        n_ranking_set=len(ranking_rows),
        n_fit_positives=sum(1 for r in ranking_rows if r.label == 1),
        structural_percentiles=structural_percentiles,
        nonconvergent_folds=nonconvergent_folds,
        headto_reference_n=len(common),
        headto_structural_percentiles=headto_structural,
        headto_evidence_percentiles=headto_evidence,
        spearman=spearman_val,
        spearman_n=len(common),
        lambda_per_fold=lam_per_fold,
        lambda_at_grid_edge=lam_edge,
        excluded=excluded,
        final_fit_converged=final_model is not None,
        final_fit_lambda=final_choice.lam,
        final_model=final_model,
        ranking=ranking,
        loo_status=loo_status,
        fulldata_status=fulldata_status,
        status_detail=status_detail,
    )


# ── scorer_version: source-hash pin (D-041 / D-027 discipline) ───────────────
_SCORER_VERSION: Optional[str] = None


def scorer_version() -> str:
    """A short hash of THIS module's source, alongside `feature_version` — a refit against changed
    scorer code is detectable rather than silent (D-041 consequences, D-027's mechanism)."""
    global _SCORER_VERSION
    if _SCORER_VERSION is None:
        _SCORER_VERSION = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:12]
    return _SCORER_VERSION
