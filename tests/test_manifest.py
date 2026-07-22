"""D-023 orchestrator-manifest tests, written against the D-024 ruling BEFORE the
implementation (THE RULE: the log leads the code).

Every assertion traces to a decision entry or to `data/cohort_82_ecd.csv`, per
D-016 — not to any entry's prose. The measured distribution (40/16/13/13) is
recomputed here from the CSV so the manifest is checked against the artefact.
"""
import collections
import csv
from pathlib import Path

from core.manifest import ManifestRow, build_manifest, coverage

_CSV = Path(__file__).resolve().parent.parent / "data" / "cohort_82_ecd.csv"
ROWS = build_manifest()
BY_ACC = {r.accession: r for r in ROWS}


def _csv_rows() -> list[dict]:
    with open(_CSV, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_one_row_per_target_82_unique():
    assert len(ROWS) == 82
    assert len(BY_ACC) == 82
    assert all(isinstance(r, ManifestRow) for r in ROWS)


def test_measured_bucket_distribution_is_40_16_13_13():
    """D-024 partition invariant, from the CSV not the prose: 40 local / 16 rental
    / 13 untested / 13 unknown, summing to 82."""
    dist = collections.Counter(r["bucket_by_largest"] for r in _csv_rows())
    assert dict(dist) == {"local": 40, "rental": 16, "untested": 13, "unknown": 13}
    assert sum(dist.values()) == 82


def test_coverage_dispositions_partition_the_cohort():
    """D-024 (i): ranked / held_out / excluded partition the 82 and sum to the
    denominator. Measured: 67 / 13 / 2. `unmeasured_tier` and `no_topology` are
    breakout counts (subsets), surfaced because an unlabelled rental looks
    measured — not additional partition cells."""
    cov = coverage(ROWS)
    assert cov["denominator"] == 82
    assert cov["ranked"] + cov["held_out"] + cov["excluded"] == 82
    assert (cov["ranked"], cov["held_out"], cov["excluded"]) == (67, 13, 2)
    assert cov["unmeasured_tier"] == 13   # ranked rows on the unmeasured local ceiling
    assert cov["no_topology"] == 13       # held_out rows with no numeric topology


def test_named_exclusions_present_with_reason():
    """D-022: MUC16 and FAT2 appear as EXCLUDED rows WITH a stated reason.
    Asserting they are absent would encode the exact bug the entry prevents."""
    for acc in ("Q8WXI7", "Q9NYQ8"):   # MUC16 (CA-125), FAT2
        r = BY_ACC[acc]
        assert r.excluded is True
        assert r.disposition == "excluded"
        assert r.exclusion_reason and r.exclusion_reason.strip()


def test_untested_route_to_rental_ranked_with_reason():
    """D-024 (iii): the 13 (440,630) targets route to RENTAL carrying
    tier_reason=unmeasured_local_ceiling, folded by sliced_ecd, and are RANKED
    (not held out — that would understate coverage by 16%)."""
    untested = [r["accession"] for r in _csv_rows() if r["bucket_by_largest"] == "untested"]
    assert len(untested) == 13
    for acc in untested:
        r = BY_ACC[acc]
        assert r.boundary_method == "sliced_ecd"
        assert r.tier == "rental"
        assert r.tier_reason == "unmeasured_local_ceiling"
        assert r.disposition == "ranked"


def test_no_bare_rental_row():
    """D-024 (iii) discipline: an unlabelled `rental` looks measured. Every
    rental-tier row must carry a reason."""
    for r in ROWS:
        if r.tier == "rental":
            assert r.tier_reason and r.tier_reason.strip(), f"{r.accession}: bare rental"


def test_gpi_subset_routes_to_whole_held_out_not_gpi_predicted():
    """D-023 (ii): the GPI predictor is deferred, so MSLN and GPC1 route to
    `whole` and are held out — NOT `gpi_predicted`, a method that does not exist.
    An implementer reading D-021 first reaches for the missing method."""
    for acc in ("Q13421", "P35052"):   # MSLN, GPC1
        r = BY_ACC[acc]
        assert r.boundary_method == "whole"
        assert r.held_out is True
        assert r.disposition == "held_out"
    assert all(r.boundary_method != "gpi_predicted" for r in ROWS)


def test_sdk1_null_bounds_never_parsed_as_a_boundary():
    """D-024 (v): SDK1 (Q7Z5N4) has an extracellular span with a null start and
    null width (`None-2009(None)`): n_spans==1 but NO numeric bounds. Keying off
    n_spans would slice a None; routing must key off numeric bounds, so SDK1 is
    `whole`, held out, with no span — never sliced_ecd."""
    r = BY_ACC["Q7Z5N4"]
    assert r.boundary_method == "whole"
    assert r.span is None
    assert r.held_out is True


def test_primary_match_provenance_carried_on_the_three():
    """D-020: the 3 primary-match resolutions carry their mapping-provenance flag
    into the manifest — visible, not averaged away — and only those three."""
    for acc in ("Q01814", "Q6UXK5", "Q99835"):   # ATP2B2, LRRN1, SMO
        assert BY_ACC[acc].primary_match is True
    assert sum(1 for r in ROWS if r.primary_match) == 3


def test_every_target_has_one_valid_boundary_method():
    for r in ROWS:
        assert r.boundary_method in ("sliced_ecd", "gpi_predicted", "whole")


def test_ranked_is_not_defined_as_local_tier():
    """D-024 (iv): tier is orthogonal to comparability. The rental-tier sliced_ecd
    targets are RANKED, so `ranked` must never be conflated with local-tier."""
    rental_ranked = [r for r in ROWS if r.disposition == "ranked" and r.tier == "rental"]
    assert len(rental_ranked) >= 13
    egfr = BY_ACC["P00533"]            # EGFR, 621 aa untested → rental, ranked
    assert egfr.tier == "rental" and egfr.disposition == "ranked"
