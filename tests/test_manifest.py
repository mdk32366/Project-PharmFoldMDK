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


def test_source_bucket_distribution_is_40_16_13_13():
    """D-024 test surface: the `bucket_by_largest` tally in the CSV is the INPUT
    measurement — 40 local / 16 rental / 13 untested / 13 unknown — distinct from
    the disposition partition below. Pinned so a change in the CSV reddens rather
    than silently re-routes."""
    dist = collections.Counter(r["bucket_by_largest"] for r in _csv_rows())
    assert dict(dist) == {"local": 40, "rental": 16, "untested": 13, "unknown": 13}
    assert sum(dist.values()) == 82


def test_coverage_dispositions_partition_the_cohort():
    """D-024 (i), corrected: ranked / held_out / excluded partition the 82 and sum
    to the denominator — and ONLY that. Measured: 67 / 13 / 2."""
    cov = coverage(ROWS)
    assert cov["denominator"] == 82
    assert cov["ranked"] + cov["held_out"] + cov["excluded"] == 82
    assert (cov["ranked"], cov["held_out"], cov["excluded"]) == (67, 13, 2)


def test_breakouts_cut_across_the_partition_and_do_not_sum_into_it():
    """D-024 (i), corrected: `unmeasured_tier` ⊆ `ranked` and `no_topology` ⊆
    `held_out` — breakout subsets that cut ACROSS the disposition partition,
    asserted as SET CONTAINMENT so the relationship survives either count changing
    (a local bisection could shrink `unmeasured_tier`). Summing all five fields and
    expecting 82 is the ambiguity the §(i) correction removed — it would force the
    13 out of `ranked`."""
    ranked = {r.accession for r in ROWS if r.disposition == "ranked"}
    held_out = {r.accession for r in ROWS if r.disposition == "held_out"}
    # Breakout membership derived WITHOUT the disposition filter, so this reddens if
    # a target ever leaks out of the disposition it must belong to.
    unmeasured_tier = {r.accession for r in ROWS if r.tier_reason == "unmeasured_local_ceiling"}
    no_topology = {r.accession for r in ROWS if r.boundary_method == "whole" and r.span is None}

    assert unmeasured_tier <= ranked        # every unmeasured-tier target is RANKED
    assert no_topology <= held_out          # every no-topology target is HELD OUT
    assert unmeasured_tier and no_topology  # they describe real targets today

    cov = coverage(ROWS)
    five_field_sum = (cov["ranked"] + cov["held_out"] + cov["excluded"]
                      + cov["unmeasured_tier"] + cov["no_topology"])
    assert five_field_sum != 82             # the wrong version, named as a failure


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


def test_sliced_rows_carry_the_largest_span_bounds():
    """D-026 (ii): a sliced_ecd row records the folded span's 1-based [start,end] —
    the LARGEST span, inherited from the bucketing (D-020), so routing and fold
    agree on which span. whole rows carry no bounds."""
    egfr = BY_ACC["P00533"]              # spans '25-645(621)'
    assert (egfr.boundary_method, egfr.span, egfr.ecd_start, egfr.ecd_end) \
        == ("sliced_ecd", 621, 25, 645)
    assert BY_ACC["Q7Z5N4"].ecd_start is None   # SDK1 whole → no bounds
    for r in ROWS:
        if r.boundary_method == "sliced_ecd":
            assert r.ecd_start is not None and r.ecd_end is not None
            assert r.ecd_end - r.ecd_start + 1 == r.span   # length consistency
        else:
            assert r.ecd_start is None and r.ecd_end is None


def test_ranked_is_not_defined_as_local_tier():
    """D-024 (iv): tier is orthogonal to comparability. The rental-tier sliced_ecd
    targets are RANKED, so `ranked` must never be conflated with local-tier."""
    rental_ranked = [r for r in ROWS if r.disposition == "ranked" and r.tier == "rental"]
    assert len(rental_ranked) >= 13
    egfr = BY_ACC["P00533"]            # EGFR, 621 aa untested → rental, ranked
    assert egfr.tier == "rental" and egfr.disposition == "ranked"


# ═══════════════════════════════════════════════════════════════════════════════
# D-077 decision 3 — the ceiling is BOUND to the recipe that measured it
# ═══════════════════════════════════════════════════════════════════════════════

def test_ceiling_constant_carries_its_recipe():
    """⚠ The ceiling cannot be read without its (dtype, chunk_size).

    They are ONE structure, not two module-level ints. Splitting them back apart
    reddens this test.

    The failure this prevents (D-077 dec 3): `worker/ceiling_probe.py` defaults
    `--dtype` to fp16 (written for the A6000). A local run that forgets
    `--dtype int8` measures a ceiling for a recipe the local tier does not use —
    and that number would be written into the constant that routes int8
    production folds. Two paths to one quantity, free to drift. Binding them
    makes the drift unrepresentable rather than merely unlikely.
    """
    from core.manifest import LOCAL_CEILING

    assert LOCAL_CEILING.known_good == 440         # unchanged in this task (order §2b)
    assert LOCAL_CEILING.known_bad == 630
    assert LOCAL_CEILING.dtype == "int8"
    assert LOCAL_CEILING.chunk_size == 64
    assert LOCAL_CEILING.hardware

    # the recipe must match the tier table it routes for — one source, not a copy
    from core.contracts import TIER_RECIPE

    assert LOCAL_CEILING.recipe() == TIER_RECIPE["local"]

    # and the bare ints must be GONE — a module-level int is exactly the shape
    # that let the number travel without its recipe
    import core.manifest as manifest

    assert not hasattr(manifest, "CEILING_KNOWN_GOOD"), \
        "the bare int is back; the ceiling can travel without its recipe again"
    assert not hasattr(manifest, "CEILING_KNOWN_BAD")


def test_the_ceiling_is_frozen_so_it_cannot_be_edited_in_place():
    """A mutable routing constant is one careless assignment from a silent
    reroute of the whole cohort."""
    import dataclasses

    import pytest

    from core.manifest import LOCAL_CEILING

    with pytest.raises(dataclasses.FrozenInstanceError):
        LOCAL_CEILING.known_good = 999


def test_unstable_band_routes_conservatively():
    """D-077 dec 4: with an `unstable` band, tier_for_span uses the LOW end.

    Using the high end reddens this. A band means the boundary is not sharp; the
    conservative end is the only one a routing decision may rely on, because the
    cost of routing an unfoldable target to local is a crashed host and the cost
    of routing a foldable one to rental is a few dollars.
    """
    from core.manifest import FoldCeiling, tier_for_span

    banded = FoldCeiling(
        hardware="test", dtype="int8", chunk_size=64,
        known_good=440, known_bad=630, unstable_band=(472, 512),
    )

    # below the low end of the band: still local
    assert tier_for_span(470, ceiling=banded)[0] == "local"
    # inside the band: NOT local — the band's low end is the routing bound
    assert tier_for_span(500, ceiling=banded)[0] == "rental"
    assert tier_for_span(512, ceiling=banded)[0] == "rental"

    # and the reason names the band rather than pretending to a measured ceiling
    assert "unstable" in (tier_for_span(500, ceiling=banded)[1] or "")


def test_routing_is_unchanged_by_the_refactor():
    """The 13 unmeasured-ceiling targets, and the local/rental split, must be
    byte-identical to what shipped before the ceiling gained its recipe. Task 2
    builds the instrument; it does not move a single target."""
    from core.manifest import tier_for_span

    assert tier_for_span(440) == ("local", None)
    assert tier_for_span(441)[0] == "rental"
    assert tier_for_span(441)[1] == "unmeasured_local_ceiling"
    assert tier_for_span(629)[1] == "unmeasured_local_ceiling"
    assert tier_for_span(630) == ("rental", "over_local_ceiling")

    unmeasured = [r for r in ROWS if r.tier_reason == "unmeasured_local_ceiling"]
    assert len(unmeasured) == 13


def test_no_second_copy_of_the_ceiling_survives_in_the_tree():
    """⚠ Found while implementing D-077 dec 3, and not in the order.

    `scripts/ecd_lengths.py:51-52` carried a HAND-DUPLICATED `CEILING_KNOWN_GOOD`
    / `CEILING_KNOWN_BAD`, and `core/manifest.py` documented it as "mirrors
    scripts/ecd_lengths.py:46-52". That is decision 3's own named failure — two
    paths to one quantity, never compared — sitting one file away from where the
    order pointed. Binding the constant to its recipe in `core/manifest.py` while
    leaving a bare int in `scripts/` would have satisfied the letter of the test
    above and none of its purpose.
    """
    import re
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    pattern = re.compile(r"^\s*CEILING_KNOWN_(GOOD|BAD)\s*=\s*\d+", re.M)

    offenders = []
    for path in list(root.glob("core/*.py")) + list(root.glob("scripts/*.py")) + \
            list(root.glob("worker/*.py")) + list(root.glob("app/*.py")):
        if pattern.search(path.read_text(encoding="utf-8")):
            offenders.append(str(path.relative_to(root)))

    assert not offenders, f"bare ceiling literal(s) still declared in: {offenders}"
