"""Task L — the run analysis across the 141, tested before it runs.

⚠⚠ THE RUN/DOMAIN DISTINCTION IS THE SUBJECT. A run is NOT a domain: FAT1's cadherin repeats
share exact boundaries (35-149, 150-257, ...) so 39 domains collapse into 9 runs, one of 2,289 aa.
Every individual domain is inside the 1,026 aa trained context; the RUNS are not. Reporting a run
as a domain was a real error in the first pass of this analysis, and `merge()`'s docstring in
`tranche6_domain_survey.py` preserves it — which is why Task L reuses that function rather than
reimplementing it. The correction is load-bearing, not commemorative.

⚠ The pre-registered question is whether D-095's TWO regimes hold across 141, so the classifier
must be able to express a third. A classifier with only two outcomes cannot answer the question
it was built for.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.tranche6_domain_survey import merge  # noqa: E402  — the docstring is the point
from scripts.tranche6_runs import REGIMES, classify_regime  # noqa: E402


def iv(*pairs):
    return [(a, b, "", "Domain") for a, b in pairs]


# ── merge: abutting is not overlapping, and both collapse ──────────────────────────────────────
def test_abutting_intervals_merge_into_one_run():
    """⚠ THE CASE THAT CAUSED THE ORIGINAL ERROR. 35-149 and 150-257 do not overlap — they abut.
    A merger that only joined OVERLAPPING intervals would leave them separate and report FAT1 as
    39 small runs, hiding the 2,289 aa stack entirely."""
    runs = merge(iv((35, 149), (150, 257)))
    assert runs == [[35, 257]], "abutting intervals are one run"


def test_overlapping_intervals_merge():
    assert merge(iv((10, 50), (40, 80))) == [[10, 80]]


def test_a_real_gap_does_not_merge():
    """⚠ The other half. A merger that joined everything would report one run always."""
    assert merge(iv((10, 50), (60, 90))) == [[10, 50], [60, 90]]


def test_one_residue_gap_does_not_merge():
    """35-149 then 151-260: a single unannotated residue between them IS a gap."""
    assert merge(iv((35, 149), (151, 260))) == [[35, 149], [151, 260]]


# ── regime classification must be able to express more than two ────────────────────────────────
def test_no_domains_is_its_own_regime_not_a_zero():
    """⚠⚠ Task A already found 10 of 141 rows with NO domain inside the span. A two-outcome
    classifier would have to file them under one of the two real regimes, which would be a
    category error dressed as a measurement."""
    assert classify_regime(n_domains=0, runs=[]) == "no_domains"


def test_one_oversized_run_is_regime_A():
    assert classify_regime(n_domains=39, runs=[2289, 640, 306]) == "one_oversized_run"


def test_all_runs_in_context_is_regime_B():
    assert classify_regime(n_domains=87, runs=[360, 223, 221]) == "all_runs_in_context"


def test_MULTIPLE_oversized_runs_is_a_DISTINCT_regime():
    """⚠ The third regime D-095 could not have seen on ten subjects. Two runs over context is not
    'one oversized run' — the cut count differs, and so does whether a single cut can fix it."""
    r = classify_regime(n_domains=60, runs=[2000, 1500, 300])
    assert r == "multiple_oversized_runs"
    assert r != "one_oversized_run"


def test_a_single_run_covering_everything_is_distinguishable():
    """⚠ One run and nothing else is not the same as one oversized run among several: there is no
    seam anywhere, not merely none in the big one."""
    assert classify_regime(n_domains=30, runs=[3000]) == "single_run_only"


def test_every_regime_name_is_declared():
    """⚠ A regime the reporter cannot name is a regime that will be silently bucketed."""
    for n, runs in ((0, []), (39, [2289, 300]), (87, [360]), (60, [2000, 1500]), (30, [3000])):
        assert classify_regime(n_domains=n, runs=runs) in REGIMES


def test_boundary_1026_is_exact():
    """1,026 is IN context; 1,027 is not. D-098 scopes on exactly this boundary."""
    assert classify_regime(n_domains=5, runs=[1026]) == "single_run_only"
    assert classify_regime(n_domains=5, runs=[1027]) == "single_run_only"
    assert classify_regime(n_domains=5, runs=[1026, 200]) == "all_runs_in_context"
    assert classify_regime(n_domains=5, runs=[1027, 200]) == "one_oversized_run"


# ── the order's exact discriminating fixture ───────────────────────────────────────────────────
def test_ORDER_fixture_abutting_merges_to_one_201aa_run():
    """⚠ The order's fixture, verbatim: 100-200 and 201-300 merge to ONE run of 201 aa."""
    runs = merge(iv((100, 200), (201, 300)))
    assert runs == [[100, 300]]
    assert runs[0][1] - runs[0][0] + 1 == 201


def test_ORDER_fixture_one_gap_does_NOT_merge():
    """⚠ And 100-200 with 202-300 must NOT merge — residue 201 is a real gap."""
    runs = merge(iv((100, 200), (202, 300)))
    assert runs == [[100, 200], [202, 300]]
    assert len(runs) == 2
