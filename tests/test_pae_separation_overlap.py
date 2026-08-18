"""Task H — the PAE separation-overlap histogram, tested before it is run.

⚠⚠ THE WHOLE POINT OF THE MEASUREMENT is that PAE rises with sequence separation regardless of
domain structure. So the within-structure contrast is only available where **intra-domain and
inter-domain pairs EXIST AT THE SAME SEPARATION**. If domains run ~100 aa, intra separations top
out near 100 and inter separations start there, and the overlap window may be too narrow to
compare in.

⚠ THE DISCRIMINATING FIXTURE is `test_same_separation_can_be_intra_or_inter`. A classifier tested
only on pairs at different separations would pass while being useless for the actual question —
the question is entirely about pairs that share a separation.

No GPU, no matrices needed: these are pure functions on synthetic domain layouts.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.pae_separation_overlap import (  # noqa: E402
    UNASSIGNED,
    classify_pair,
    domain_index,
    overlap_window,
)


def test_domain_index_maps_local_positions_to_domain_ids():
    """Domains are given in CHAIN coordinates and the matrix is SPAN-local, so the mapping has to
    subtract span_start. ⚠ An off-by-one here silently shifts every classification."""
    idx = domain_index(span_start=101, span_len=10, domains=[(101, 103), (107, 110)])
    assert idx[0] == 0 and idx[2] == 0, "101-103 -> local 0-2, domain 0"
    assert idx[3] is UNASSIGNED, "104 is in no domain"
    assert idx[6] == 1 and idx[9] == 1, "107-110 -> local 6-9, domain 1"


def test_a_residue_outside_every_domain_is_unassigned_not_domain_zero():
    """⚠ An absence is a category. Defaulting to domain 0 would silently fold linker residues into
    the first domain and inflate the intra population."""
    idx = domain_index(span_start=1, span_len=5, domains=[(3, 4)])
    assert idx[0] is UNASSIGNED and idx[1] is UNASSIGNED
    assert idx[2] == 0 and idx[3] == 0
    assert idx[4] is UNASSIGNED


# ── ⚠⚠ THE DISCRIMINATING FIXTURE ─────────────────────────────────────────────────────────────
def test_same_separation_can_be_intra_or_inter():
    """Two pairs, IDENTICAL separation of 3, one intra and one inter. ⚠ This is the entire
    measurement: if no such pair exists in the real data, the within-structure contrast is
    unavailable and no amount of sample size fixes it."""
    # domain 0 = local 0-9, domain 1 = local 10-19
    idx = domain_index(span_start=1, span_len=20, domains=[(1, 10), (11, 20)])
    assert classify_pair(2, 5, idx) == "intra", "both inside domain 0, separation 3"
    assert classify_pair(8, 11, idx) == "inter", "across the boundary, separation 3"


def test_pairs_touching_a_linker_are_unassigned_not_inter():
    """⚠ A pair with one residue in no domain is neither intra nor inter. Counting it as inter
    would contaminate the very population the contrast depends on."""
    idx = domain_index(span_start=1, span_len=20, domains=[(1, 5), (11, 20)])
    assert classify_pair(2, 7, idx) == UNASSIGNED, "7 is in the linker"
    assert classify_pair(6, 7, idx) == UNASSIGNED, "both in the linker"


def test_classification_is_symmetric():
    idx = domain_index(span_start=1, span_len=20, domains=[(1, 10), (11, 20)])
    assert classify_pair(3, 15, idx) == classify_pair(15, 3, idx)


# ── the overlap window itself ──────────────────────────────────────────────────────────────────
def test_overlap_window_is_the_range_where_both_populations_exist():
    intra = {1: 10, 2: 8, 3: 5}
    inter = {3: 2, 4: 9, 5: 7}
    lo, hi, n_intra, n_inter = overlap_window(intra, inter)
    assert (lo, hi) == (3, 3), "only separation 3 has both"
    assert n_intra == 5 and n_inter == 2


def test_no_overlap_is_reported_as_none_not_as_an_empty_range():
    """⚠ The failure case must be legible. An empty range reported as (0, 0) reads like a
    measurement; None reads like the answer it is — the contrast is unavailable."""
    intra = {1: 10, 2: 8}
    inter = {5: 2, 6: 9}
    assert overlap_window(intra, inter) is None


def test_a_wide_overlap_reports_both_populations_fully():
    intra = {10: 3, 20: 4, 30: 5}
    inter = {20: 6, 30: 7, 40: 8}
    lo, hi, n_intra, n_inter = overlap_window(intra, inter)
    assert (lo, hi) == (20, 30)
    assert n_intra == 9, "4 + 5 intra pairs inside the window"
    assert n_inter == 13, "6 + 7 inter pairs inside the window"
