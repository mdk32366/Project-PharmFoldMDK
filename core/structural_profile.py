"""The census `structural_profile` — `D-079` amendment 1, ruled by amendment 2 on 2026-08-20.

⚠⚠ IT IS NOT A SCORE AND THE NAME IS THE RULING (amendment 1, ruling 1). Never `score`, never
`rank`, never `suitability`. `F-049`'s family is a word meaning two things on two surfaces and it
bit three times on 2026-08-19; a fourth is not acceptable.

⚠⚠ IT IS NEVER RANKED, INCLUDING BY SORT ORDER (ruling 2). This module exposes no ordering, no
`rank`, no `top_n`, and no comparison operator between profiles. *A value is a measurement; a rank
is a recommendation*, and the census has no labels to justify one.

⚠⚠ REFUSAL IS AN OUTCOME AND IT IS THE POINT (ruling 3). A row outside the cohort's fit range
yields a `ProfileRefusal` — **a CATEGORY, not a number, not a clamp, not a None**. Wired at the call
site: `structural_profile()` returns a `ProfileResult` whose value is `None` **only** when a refusal
is present, and a test asserts the two can never both be absent.

⚠ THE BAR IS THE COHORT'S OBSERVED MIN–MAX (amendment 2, ruling 8), not p05–p95 and not ±3 sd:
  · `±3 sd` rests on `sd_k`, which `F-049 amendment 1` proves is NOT recoverable.
  · `p05–p95` fires INSIDE the training support — it would refuse values the model was fit on.
  · strict is the actual support: no distributional assumption, no unrecoverable parameter.

⚠⚠ NO IMPORT OF `core/scorer.py` OR THE FITTER (`D-079` decision 1). The model is applied from
THIRTEEN NUMBERS recovered from persisted values — six slopes, six means, one intercept
(`data/census/run2_raw_scale_model.json`) — which reproduce every one of run 2's 56 persisted
scores to `2.2e-16`. ⚠ That is not a second implementation hoping to agree: it is the same function
evaluated from recovered parameters, and `tests/test_structural_profile.py` proves the agreement
against a committed fixture rather than asserting it.

⚠ Decision 1 claims that separation is *"asserted by test and proven by revert."* Measured
2026-08-20: **the only such test runs the other direction** (`core/scorer.py` must not import
census). The missing half is built in this module's test file.
"""
from __future__ import annotations

import json
import math
import pathlib
from dataclasses import dataclass
from typing import Mapping, Optional, Sequence

REPO = pathlib.Path(__file__).resolve().parents[1]
MODEL_PATH = REPO / "data" / "census" / "run2_raw_scale_model.json"
BASELINE_PATH = REPO / "data" / "census" / "cohort_feature_baseline.json"

#: The refusal vocabulary. ⚠ Every one is a CATEGORY WITH A CAUSE; none is a number or a null.
#: ⚠⚠ These are PROFILE-time refusals and deliberately NOT `protein_features.extraction_outcome`,
#: which records what happened at EXTRACTION. The bar can change without a feature changing;
#: pooling them would make a bar adjustment look like a re-extraction (amendment 2).
PROFILE_REFUSALS = (
    "refused_out_of_distribution",   # ruling 3 — outside the cohort's observed support
    "refused_span_below_floor",      # ruling 6 — F-048's engulfing set, excluded AT COMPUTATION
    "refused_features_incomplete",   # no six-vector to evaluate; an absence, never a zero
)

#: ⚠ Ruling 4. These travel with EVERY rendered profile, in the same frame — never a footnote.
MOUNT_PRECONDITIONS = (
    "unlabelled — there is no leave-one-out here. D-041's defence of the small model is that LOO "
    "exposes overfitting as noise; on unlabelled census proteins that instrument does not exist.",
    "out of the fit population — 56 targets from an expression-selected cohort (A-014, F-011: an "
    "upstream screen's positive class is a prediction, not a fact).",
    "not a probability — F-006 records the cohort's own values spanning 0.116 to 0.285, compressed "
    "toward the base rate. Whatever the census yields is narrower and will be read as a probability "
    "unless the frame says otherwise.",
    "confidence-dominated — F-051 measures membrane_proximal_plddt carrying 32.2% of attribution "
    "and the confidence pair 38.6%. The feature doing the most work is the one most likely to "
    "misbehave out of distribution, and the measurement confirmed it: the two confidence features "
    "are the #1 and #2 out-of-range offenders (33.1% and 18.5%).",
    "the mean_plddt_ecd bound is partly a selection artefact — the cohort minimum of 50.49 is very "
    "largely D-041's ranking-set floor (mean_plddt >= 50), not a natural limit, and 831 of that "
    "feature's 868 refusals fall below it. Real support gap AND selection rule at once; never "
    "present it as pure distribution shift (amendment 2, ruling 9).",
)


class ProfileMisuse(RuntimeError):
    """⚠ Raised when a caller asks this module for something ruling 2 forbids. An exception rather
    than a returned `None`, because *a failing check nobody is forced to obey is decoration*."""


@dataclass(frozen=True)
class ProfileRefusal:
    """A refusal, carrying its cause. ⚠ Never collapses to a bare `None` or a sentinel number."""

    category: str
    detail: str

    def __post_init__(self) -> None:
        if self.category not in PROFILE_REFUSALS:
            raise ProfileMisuse(
                f"{self.category!r} is not in the refusal vocabulary {PROFILE_REFUSALS}. "
                f"An unlisted refusal is how a category becomes a blank.")


@dataclass(frozen=True)
class ProfileResult:
    """Exactly one of `value` / `refusal` is present — asserted, not documented.

    ⚠⚠ NO ORDERING IS DEFINED ON THIS TYPE, DELIBERATELY (ruling 2). `__lt__` is not implemented,
    so `sorted()` over these raises `TypeError` rather than quietly producing a ranking. *A sortable
    column is a ranking with extra steps.*
    """

    accession: str
    value: Optional[float]
    refusal: Optional[ProfileRefusal]
    out_of_range_features: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if (self.value is None) == (self.refusal is None):
            raise ProfileMisuse(
                "a ProfileResult must carry exactly one of value / refusal — "
                "both absent is a silent null, both present is a computed-then-hidden value, and "
                "ruling 3 forbids each.")

    @property
    def is_refused(self) -> bool:
        return self.refusal is not None


def load_model(path: pathlib.Path = MODEL_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_support(path: pathlib.Path = BASELINE_PATH) -> dict[str, tuple[float, float]]:
    """The cohort's OBSERVED support per feature — amendment 2 ruling 8's bar, min and max only.

    ⚠ `p05`/`p95`/`sd_ddof0` are present in the baseline file and are deliberately NOT read here:
    reading them would make the bar a parameter of whoever calls this."""
    raw = json.loads(path.read_text(encoding="utf-8"))["features"]
    return {name: (d["min"], d["max"]) for name, d in raw.items()}


def out_of_range(features: Mapping[str, Optional[float]],
                 support: Optional[dict[str, tuple[float, float]]] = None) -> tuple[str, ...]:
    """Which features fall outside the cohort's observed support. ⚠ Order follows the model's
    declared `feature_order`, so the tuple is deterministic and not dict-insertion dependent."""
    support = load_support() if support is None else support
    order = load_model()["feature_order"]
    bad = []
    for name in order:
        v = features.get(name)
        if v is None:
            continue
        lo, hi = support[name]
        if v < lo or v > hi:
            bad.append(name)
    return tuple(bad)


def structural_profile(
    features: Mapping[str, Optional[float]],
    *,
    accession: str,
    span_below_floor: bool = False,
    model: Optional[dict] = None,
    support: Optional[dict[str, tuple[float, float]]] = None,
) -> ProfileResult:
    """One census row's structural profile, or a refusal with its cause.

    ⚠⚠ THE REFUSALS ARE CHECKED BEFORE ANY ARITHMETIC (ruling 6: *excluded at the point of
    computation, not filtered at display*). *A value computed and then hidden is a value that will
    eventually be exported.*
    """
    model = load_model() if model is None else model
    support = load_support() if support is None else support
    order = model["feature_order"]

    # ── ruling 6 — F-048's set never reaches the arithmetic ──────────────────
    if span_below_floor:
        return ProfileResult(accession, None, ProfileRefusal(
            "refused_span_below_floor",
            "F-048: the V2 span is engulfed by a larger domain, so geometric features on it are "
            "not a weak signal — they describe a different object. D-079 amendment 1 ruling 6."))

    missing = [n for n in order if features.get(n) is None]
    if missing:
        return ProfileResult(accession, None, ProfileRefusal(
            "refused_features_incomplete",
            f"no value for {', '.join(missing)}; a profile needs the complete six-vector and an "
            f"absent measurement is a category, never a zero (D-027)."))

    # ── ruling 3 — outside the cohort's observed support ─────────────────────
    bad = out_of_range(features, support)
    if bad:
        detail = "; ".join(
            f"{n}={features[n]:.6g} outside the cohort's observed "
            f"[{support[n][0]:.6g}, {support[n][1]:.6g}]" for n in bad)
        return ProfileResult(accession, None, ProfileRefusal(
            "refused_out_of_distribution",
            f"{len(bad)} of {len(order)} features outside the fit population's support: {detail}"),
            out_of_range_features=bad)

    z = model["intercept"] + sum(
        model["slope_raw"][n] * (float(features[n]) - model["mean_raw"][n]) for n in order)
    return ProfileResult(accession, 1.0 / (1.0 + math.exp(-z)), None)


def profile_many(rows: Sequence[Mapping], *, refused_accessions: frozenset[str] = frozenset()
                 ) -> list[ProfileResult]:
    """Profiles in the order given. ⚠⚠ THE ORDER IS THE CALLER'S AND IS NEVER CHANGED HERE — this
    function does not sort, and ruling 2 is why. Returns one result per input row, refusals
    included, so a caller cannot silently receive a filtered list."""
    out = []
    for r in rows:
        acc = r["accession"]
        out.append(structural_profile(
            r["features"], accession=acc, span_below_floor=acc in refused_accessions))
    assert len(out) == len(rows), "profile_many dropped a row — refusals are returned, never filtered"
    return out
