"""Task A1 of ORDERS-Code-2026-08-18 — the domain bucketing, tested before it is written.

⚠ THE DISCRIMINATING FIXTURE is `test_domains_entirely_outside_the_span`. A test built only from
proteins whose domains sit inside the V2 span **passes under the chain-count defect** — the defect
where `n_domain` over the chain is silently reported as the number of domains we would fold. A
cytoplasmic-tail domain is a domain; it is not a domain in the span. The order says both numbers are
emitted and neither is allowed to stand alone, and only a protein with domains OUTSIDE the span can
tell the two apart.

⚠ The bucket-sum invariant is what makes the UNKNOWN-modifier branch provable by revert: delete the
branch and a real domain vanishes from every bucket, which no per-bucket assertion would notice but
the sum does.

Cache-only, synthetic fixtures, no network, no database.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.tranche6_domain_census import (  # noqa: E402
    UNKNOWN_COORDINATE,
    boundaries_of,
    bucket_domains,
    domain_like_features,
    matched_within,
)


def feat(kind: str, start, end, desc="X", modifier="EXACT"):
    """A synthetic UniProt feature. `start`/`end` of None model an absent value."""
    return {
        "type": kind,
        "description": desc,
        "location": {
            "start": {"value": start, "modifier": modifier},
            "end": {"value": end, "modifier": modifier},
        },
    }


def doc(*features):
    return {"features": list(features), "sequence": {"length": 5000}}


# ── fixture 1 — an unknown coordinate modifier becomes a CATEGORY, never a silent drop ──────────
def test_unknown_coordinate_modifier_is_a_named_category():
    d = doc(
        feat("Domain", 100, 200),
        feat("Domain", 300, 400),
        feat("Domain", None, 600, modifier="UNKNOWN"),
    )
    b = bucket_domains(domain_like_features(d), span_start=50, span_end=1000)

    assert b.n_unknown_coordinates == 1, "the unresolvable domain must be its own category"
    assert b.n_domainlike_chain == 3, "it is still a domain on the chain"
    # ⚠ THE REVERT PROOF LIVES HERE. Remove the UNKNOWN branch and this domain vanishes from every
    # bucket while n_domainlike_chain stays 3 — invisible to any single-bucket assertion.
    assert (
        b.n_wholly_inside_span
        + b.n_straddling_span
        + b.n_wholly_outside_span
        + b.n_unknown_coordinates
    ) == b.n_domainlike_chain, "buckets must account for every domain-like feature"


def test_unknown_category_is_reported_by_name_not_as_zero():
    d = doc(feat("Domain", None, None, modifier="UNKNOWN"))
    b = bucket_domains(domain_like_features(d), span_start=1, span_end=100)
    assert b.categories[UNKNOWN_COORDINATE] == 1


# ── fixture 2 — ⚠⚠ THE DISCRIMINATING ONE: domains entirely outside the V2 span ─────────────────
def test_domains_entirely_outside_the_span():
    """⚠ A protein whose domains lie wholly outside the span. `n_domain` over the chain is
    non-zero while the number we would fold is ZERO. A fixture without this case passes under the
    chain-count defect, which is why the order names it."""
    d = doc(
        feat("Domain", 2000, 2100, desc="cytoplasmic 1"),
        feat("Domain", 2200, 2300, desc="cytoplasmic 2"),
    )
    b = bucket_domains(domain_like_features(d), span_start=20, span_end=1000)

    assert b.n_domainlike_chain == 2, "the chain count is 2 and must still be reported"
    assert b.n_wholly_inside_span == 0, "⚠ none of them is a domain we would fold"
    assert b.n_wholly_outside_span == 2
    assert b.n_straddling_span == 0
    assert b.residues_in_domains_span == 0
    assert b.residues_in_span_not_in_any_domain == 981, "the whole span is unannotated"


def test_chain_and_span_counts_are_both_emitted_and_differ():
    """⚠ Neither number is allowed to stand alone (order §1). This asserts they are distinct
    fields, so a caller cannot collapse them by accident."""
    d = doc(feat("Domain", 100, 200), feat("Domain", 5000, 5100))
    b = bucket_domains(domain_like_features(d), span_start=50, span_end=1000)
    assert b.n_domainlike_chain == 2
    assert b.n_wholly_inside_span == 1
    assert b.n_domainlike_chain != b.n_wholly_inside_span


# ── fixture 3 — a domain straddling span_start ─────────────────────────────────────────────────
def test_domain_straddling_the_span_boundary():
    d = doc(
        feat("Domain", 10, 80, desc="straddles the start"),
        feat("Domain", 200, 300, desc="inside"),
        feat("Domain", 900, 1200, desc="straddles the end"),
    )
    b = bucket_domains(domain_like_features(d), span_start=50, span_end=1000)

    assert b.n_straddling_span == 2
    assert b.n_wholly_inside_span == 1
    assert b.n_wholly_outside_span == 0
    assert (
        b.n_wholly_inside_span
        + b.n_straddling_span
        + b.n_wholly_outside_span
        + b.n_unknown_coordinates
    ) == b.n_domainlike_chain


def test_straddling_is_in_exactly_one_bucket():
    """⚠ A straddling domain must not also be counted inside — double counting would make the
    buckets sum correctly by accident while both numbers are wrong."""
    d = doc(feat("Domain", 10, 80))
    b = bucket_domains(domain_like_features(d), span_start=50, span_end=1000)
    assert b.n_straddling_span == 1
    assert b.n_wholly_inside_span == 0
    assert b.n_wholly_outside_span == 0


# ── Repeat is not optional ─────────────────────────────────────────────────────────────────────
def test_repeat_features_count_as_domain_like():
    """⚠ UniProt splits a tandem array across `Domain` and `Repeat`. Counting only `Domain` drops
    34 LDL-receptor class B repeats from LRP1 alone, and the survivor still looks plausible."""
    d = doc(feat("Domain", 100, 200), feat("Repeat", 300, 400), feat("Repeat", 500, 600))
    feats = domain_like_features(d)
    assert len(feats) == 3
    b = bucket_domains(feats, span_start=50, span_end=1000)
    assert b.n_domain_chain == 1
    assert b.n_repeat_chain == 2
    assert b.n_domainlike_chain == 3


# ── residue accounting ─────────────────────────────────────────────────────────────────────────
def test_overlapping_domains_do_not_double_count_residues():
    """Two overlapping domains cover the union, not the sum — otherwise
    `residues_in_span_not_in_any_domain` can go negative and nothing notices."""
    d = doc(feat("Domain", 100, 200), feat("Domain", 150, 250))
    b = bucket_domains(domain_like_features(d), span_start=100, span_end=300)
    assert b.residues_in_domains_span == 151, "100-250 inclusive is 151 residues"
    assert b.residues_in_span_not_in_any_domain == 50


def test_residues_never_negative_and_partition_the_span():
    d = doc(feat("Domain", 10, 400))
    span_start, span_end = 100, 300
    b = bucket_domains(domain_like_features(d), span_start=span_start, span_end=span_end)
    span_len = span_end - span_start + 1
    assert b.residues_in_domains_span + b.residues_in_span_not_in_any_domain == span_len
    assert b.residues_in_span_not_in_any_domain >= 0


@pytest.mark.parametrize("kind", ["Glycosylation", "Transmembrane", "Chain", "Region"])
def test_non_domain_features_are_excluded(kind):
    d = doc(feat(kind, 100, 200))
    assert domain_like_features(d) == []


# ── Task C / D-099 — the control's eligibility predicate ───────────────────────────────────────
def test_domain_only_and_domainlike_are_different_populations():
    """⚠ D-099 says "UniProt `Domain` features". Silently widening to Domain+Repeat would change
    the control pool — 230 rows vs 277 on the real census. The two must not be interchangeable."""
    d = doc(feat("Domain", 100, 200), feat("Repeat", 300, 400))
    feats = domain_like_features(d)
    only_domain = [f for f in feats if f.get("type") == "Domain"]
    b_wide = bucket_domains(feats, span_start=50, span_end=500)
    b_narrow = bucket_domains(only_domain, span_start=50, span_end=500)
    assert b_wide.n_wholly_inside_span == 2
    assert b_narrow.n_wholly_inside_span == 1


def test_eligibility_threshold_excludes_exactly_one_domain():
    """⚠ '>=2 wholly inside' — a single-domain protein has no inter-domain interface, so it
    cannot serve as a control for assembly. Off-by-one here would pollute the pool."""
    one = bucket_domains(domain_like_features(doc(feat("Domain", 100, 200))),
                         span_start=50, span_end=500)
    two = bucket_domains(domain_like_features(doc(feat("Domain", 100, 200),
                                                  feat("Domain", 250, 350))),
                         span_start=50, span_end=500)
    assert one.n_wholly_inside_span == 1 and not (one.n_wholly_inside_span >= 2)
    assert two.n_wholly_inside_span == 2 and (two.n_wholly_inside_span >= 2)


def test_a_domain_outside_the_span_does_not_make_a_protein_eligible():
    """⚠ THE DISCRIMINATING ONE for Task C: one domain in the span and one outside is NOT a
    two-domain control. Counting the chain would enrol it and the fold would measure nothing."""
    d = doc(feat("Domain", 100, 200), feat("Domain", 900, 1000))
    b = bucket_domains(domain_like_features(d), span_start=50, span_end=500)
    assert b.n_domainlike_chain == 2
    assert b.n_wholly_inside_span == 1, "only one domain is in the span"
    assert not (b.n_wholly_inside_span >= 2), "must NOT be eligible"


# ── Task A3 — the agreement table ──────────────────────────────────────────────────────────────
def test_boundaries_are_starts_and_ends():
    feats = [feat("Domain", 10, 20), feat("Domain", 30, 40)]
    assert boundaries_of(feats) == [10, 20, 30, 40]


def test_agreement_at_k_zero_is_exact():
    a = [100, 200]
    assert matched_within(a, [100, 200], 0) == 2
    assert matched_within(a, [101, 199], 0) == 0


def test_agreement_widens_monotonically_with_k():
    a = [100, 200]
    b = [104, 210]
    assert matched_within(a, b, 0) == 0
    assert matched_within(a, b, 5) == 1     # 100~104 only
    assert matched_within(a, b, 10) == 2    # 200~210 now too
    assert matched_within(a, b, 25) == 2


def test_agreement_is_ASYMMETRIC_and_both_directions_must_be_reported():
    """⚠⚠ THE TRAP. One source having many boundaries near a single boundary of the other makes
    X->Y and Y->X different numbers. Reporting one of them as "the agreement" is a claim about
    the wrong quantity — a single figure hides which source is the denominator."""
    a = [100]
    b = [98, 99, 101, 102]
    assert matched_within(a, b, 5) == 1, "one a-boundary is matched"
    assert matched_within(b, a, 5) == 4, "but all four b-boundaries are matched"
    assert matched_within(a, b, 5) != matched_within(b, a, 5)


def test_one_boundary_matched_by_many_counts_once():
    assert matched_within([100], [99, 100, 101], 5) == 1


def test_empty_sources_are_zero_not_an_error():
    """⚠ An absence is a category. A protein InterPro does not annotate yields 0 matched of 0,
    which must not crash and must not be reported as perfect agreement."""
    assert matched_within([], [1, 2, 3], 5) == 0
    assert matched_within([1, 2, 3], [], 5) == 0
