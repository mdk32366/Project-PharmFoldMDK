"""D-075 Decision 3 — the popularity-matched control's test surface.

The load-bearing properties are the **freeze** ones: the control must read only frozen inputs, so
re-running it is byte-identical and no result can be produced by a re-query. The snapshot builder's
fetchers are injected, so every test here is hermetic — no network, no clock.
"""

from __future__ import annotations

import json

import pytest

from scripts.attention_control import (
    PROXY_NAMES,
    PUBMED_QUERY_TEMPLATE,
    StratumResult,
    TargetRow,
    build_snapshot,
    format_report,
    load_snapshot,
    matched_enrichment,
    percentile_within,
    rows_from,
    stratify,
)


def _rows() -> list[TargetRow]:
    """Twelve targets. Positives sit HIGH within both attention strata, so a correct control
    reports surviving enrichment — the fixture is built to make a flattening bug visible."""
    return [
        # pdb-present stratum: positives high
        TargetRow("PA", 0.91, 1, pdb_present=1, pub_count=900),
        TargetRow("PB", 0.83, 1, pdb_present=1, pub_count=750),
        TargetRow("NA", 0.22, 0, pdb_present=1, pub_count=810),
        TargetRow("NB", 0.31, 0, pdb_present=1, pub_count=640),
        TargetRow("NC", 0.18, 0, pdb_present=1, pub_count=705),
        # pdb-absent stratum: positives also high
        TargetRow("PC", 0.77, 1, pdb_present=0, pub_count=120),
        TargetRow("PD", 0.69, 1, pdb_present=0, pub_count=95),
        TargetRow("ND", 0.24, 0, pdb_present=0, pub_count=140),
        TargetRow("NE", 0.13, 0, pdb_present=0, pub_count=60),
        TargetRow("NF", 0.29, 0, pdb_present=0, pub_count=110),
        TargetRow("NG", 0.35, 0, pdb_present=0, pub_count=88),
        TargetRow("NH", 0.41, 0, pdb_present=0, pub_count=75),
    ]


# ── the percentile convention matches the scorer's ───────────────────────────
def test_percentile_ties_take_half_credit_like_the_scorer():
    """D-060 dec 6's convention, reimplemented here for stdlib independence — so it is pinned,
    not trusted. A tie must take half credit, or this percentile is not the scorer's percentile."""
    assert percentile_within(2.0, [1.0, 2.0, 3.0]) == pytest.approx((1 + 0.5) / 3)
    assert percentile_within(3.0, [1.0, 2.0, 3.0]) == pytest.approx((2 + 0.5) / 3)


def test_percentile_against_an_empty_population_raises():
    """A percentile against nothing is not a number and must not silently be 0.0."""
    with pytest.raises(ValueError):
        percentile_within(1.0, [])


# ── stratification ───────────────────────────────────────────────────────────
def test_pdb_present_yields_exactly_two_strata():
    strata = stratify(_rows(), "pdb_present")
    assert set(strata) == {"pdb_present", "pdb_absent"}
    assert len(strata["pdb_present"]) == 5 and len(strata["pdb_absent"]) == 7


def test_pub_count_splits_at_its_own_median_not_a_magic_number():
    """The continuous proxy is cut at the median of the data present (D-041 dec 4: no threshold
    invented for the occasion). Both strata must be non-empty and together cover every row."""
    strata = stratify(_rows(), "pub_count")
    assert set(strata) == {"pub_low", "pub_high"}
    assert len(strata["pub_low"]) + len(strata["pub_high"]) == len(_rows())
    assert min(r.pub_count for r in strata["pub_high"]) > max(r.pub_count for r in strata["pub_low"])


def test_a_missing_proxy_becomes_a_named_unknown_stratum_never_dropped():
    """D-027: a missing value is null-with-a-reason, never imputed and never silently excluded.
    An `unknown` stratum must appear and carry the row, so it is reported rather than vanishing."""
    rows = _rows() + [TargetRow("PX", 0.55, 1, pdb_present=None, pub_count=None)]
    strata = stratify(rows, "pdb_present")
    assert "unknown" in strata and [r.symbol for r in strata["unknown"]] == ["PX"]
    assert sum(len(v) for v in strata.values()) == len(rows)


def test_only_the_two_named_proxies_are_permitted():
    """D-075 dec 3 / §3 bite 5: no third proxy without a new dated entry. Refused in code."""
    assert sorted(PROXY_NAMES) == ["pdb_present", "pub_count"]
    for bad in ("citation_count", "grant_dollars", "", "pdb_count"):
        with pytest.raises(ValueError):
            stratify(_rows(), bad)


# ── the control itself ───────────────────────────────────────────────────────
def test_matched_enrichment_computes_percentiles_within_each_stratum():
    """⚠ The core property: a stratum's percentiles come from ITS OWN distribution. If the
    population leaked across strata, matching would not be matching — the whole control would be
    the unmatched result wearing a different label."""
    results = {r.name: r for r in matched_enrichment(_rows(), "pdb_present")}
    # PA (0.91) and PB (0.83) are the top 2 of 5 in their stratum -> high percentiles.
    present = results["pdb_present"]
    assert present.n == 5 and present.n_positives == 2
    assert present.mean_positive_percentile is not None
    assert present.mean_positive_percentile > 0.7
    # PC (0.77) and PD (0.69) are the top 2 of 7 in theirs -> also high.
    absent = results["pdb_absent"]
    assert absent.n == 7 and absent.n_positives == 2
    assert absent.mean_positive_percentile > 0.7


def test_a_stratum_with_no_positives_reports_null_not_zero():
    """D-064 dec 5 / D-027: a statistic that cannot be computed is null WITH its reason, never a
    number. A 0.0 here would read as 'positives ranked worst', the opposite of 'no positives'."""
    rows = [TargetRow("NA", 0.2, 0, pdb_present=1), TargetRow("NB", 0.4, 0, pdb_present=1),
            TargetRow("PA", 0.9, 1, pdb_present=0), TargetRow("NC", 0.1, 0, pdb_present=0)]
    results = {r.name: r for r in matched_enrichment(rows, "pdb_present")}
    assert results["pdb_present"].n_positives == 0
    assert results["pdb_present"].mean_positive_percentile is None
    assert results["pdb_absent"].mean_positive_percentile is not None


def test_control_is_byte_identical_across_runs():
    """D-075's test surface: 'Re-running the control with the same frozen inputs is
    byte-identical.' Asserted on the serialised results, not just on a float compare."""
    a = matched_enrichment(_rows(), "pub_count")
    b = matched_enrichment(_rows(), "pub_count")
    dump = lambda rs: json.dumps([r.__dict__ for r in rs], sort_keys=True)  # noqa: E731
    assert dump(a) == dump(b)


def test_flattened_enrichment_is_visible_as_such():
    """The Branch-B case must be legible, not merely absent. With positives placed mid-pack inside
    each stratum, the mean positive percentile lands near 0.5 — what 'vanishes under matching'
    looks like. If this reported high values, the control could not detect its own headline."""
    rows = [
        TargetRow("PA", 0.50, 1, pdb_present=1), TargetRow("NA", 0.90, 0, pdb_present=1),
        TargetRow("NB", 0.10, 0, pdb_present=1),
        TargetRow("PB", 0.50, 1, pdb_present=0), TargetRow("NC", 0.95, 0, pdb_present=0),
        TargetRow("ND", 0.05, 0, pdb_present=0),
    ]
    for r in matched_enrichment(rows, "pdb_present"):
        assert r.mean_positive_percentile == pytest.approx(0.5, abs=0.2)


# ── the freeze ───────────────────────────────────────────────────────────────
def test_snapshot_records_query_date_and_bounds():
    """D-075 dec 3: source + query + date recorded IN the artifact. A proxy whose query is not
    written down cannot be shown to have been frozen."""
    snap = build_snapshot(
        [("PA", "P11111"), ("PB", "P22222")],
        frozen_date="2026-08-01",
        fetch_pdb_present=lambda acc: 1,
        fetch_pub_count=lambda sym: 42,
    )
    assert snap["frozen_date"] == "2026-08-01"
    assert snap["pubmed_query_template"] == PUBMED_QUERY_TEMPLATE
    assert set(snap["bounds"]) == {"pdb_present", "pub_count"}      # the instrument's own limits
    assert snap["n_targets"] == 2


def test_snapshot_records_a_failed_fetch_as_null_with_a_reason():
    """A source that returns nothing must produce a null WITH a reason — never a 0 that would read
    as 'no publications' or 'no structure' (D-027)."""
    snap = build_snapshot(
        [("PA", "P11111")],
        frozen_date="2026-08-01",
        fetch_pdb_present=lambda acc: None,
        fetch_pub_count=lambda sym: None,
    )
    entry = snap["targets"][0]
    assert entry["pdb_present"] is None and entry["pub_count"] is None
    assert set(entry["null_reasons"]) == {"pdb_present", "pub_count"}


def test_snapshot_builder_takes_no_clock_so_the_date_is_stated_not_captured():
    """`frozen_date` is a required keyword. A date read from the clock inside the builder would let
    a re-freeze look identical to the original; stating it forces the caller to mean it."""
    with pytest.raises(TypeError):
        build_snapshot([("PA", "P1")], fetch_pdb_present=lambda a: 1,   # type: ignore[call-arg]
                       fetch_pub_count=lambda s: 1)


def test_control_refuses_to_run_without_a_frozen_snapshot(tmp_path):
    """⚠ The anti-fishing guard. The control must NOT fall back to a live query when the snapshot
    is missing — a silently-refreshed proxy is an unfrozen proxy, and the result would not be the
    pre-registered one. It raises instead."""
    with pytest.raises(FileNotFoundError, match="freeze"):
        load_snapshot(tmp_path / "does_not_exist.json")


def test_snapshot_target_without_a_structural_score_is_skipped_not_fabricated(capsys):
    """A frozen target with no deployed score is dropped WITH a warning, never given a score. The
    structural scores are read from the served pre-registered run, never recomputed (D-075 dec 5)."""
    snap = {"frozen_date": "2026-08-01", "n_targets": 2, "targets": [
        {"symbol": "PA", "accession": "P1", "pdb_present": 1, "pub_count": 10},
        {"symbol": "GHOST", "accession": "P2", "pdb_present": 0, "pub_count": 5},
    ]}
    rows = rows_from(snap, scores={"PA": 0.7}, labels={"PA"})
    assert [r.symbol for r in rows] == ["PA"]
    assert "GHOST" in capsys.readouterr().out


def test_report_states_the_proxy_bound_alongside_the_numbers():
    """D-074 dec 3: an instrument cited as provenance carries its own statement of what it gets
    wrong. The rendered report must show the proxy's bound and the freeze date, not just results."""
    snap = build_snapshot([("PA", "P1")], frozen_date="2026-08-01",
                          fetch_pdb_present=lambda a: 1, fetch_pub_count=lambda s: 7)
    text = format_report(matched_enrichment(_rows(), "pdb_present"), "pdb_present", snap)
    assert "2026-08-01" in text
    assert "bound:" in text and "fragment" in text          # the pdb_present limitation, printed
    assert "triple" in text                                  # D-075 dec 4's reading rule travels
