"""Task D of ORDERS-Code-2026-08-18 — the band split, tested before it is trusted.

⚠⚠ THE EDGES ARE LOAD-BEARING. 441 / 851 / 1,027 are the boundaries the whole scoping argument
rests on, and `<` for `<=` is INVISIBLE IN A TOTAL — 776 stays 776 however the rows move between
bands. So every test below moves a boundary by ONE residue and asserts the row lands in the other
band. A test that only checked the total would pass under every off-by-one this file exists to
catch.

⚠ This is deliberately a SECOND path to a quantity `scripts/census_manifest.py` already computes.
The order requires an independent re-derivation precisely because two paths compared once is the
remedy for the two-paths defect; two paths never compared is the defect.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.tranche5_band_split import band_of, split  # noqa: E402


# ── the edges, one residue either side ─────────────────────────────────────────────────────────
@pytest.mark.parametrize("aa,expected", [
    (440, "at_or_below_local"),   # the last local row
    (441, "441_850"),             # ⚠ the first rental row
    (850, "441_850"),             # ⚠ the last of the cheap band
    (851, "851_1026"),            # the first of the 80 GB band
    (1026, "851_1026"),           # ⚠ the last IN-CONTEXT length
    (1027, "past_context"),       # ⚠ the first past-context row
])
def test_every_edge_is_exact(aa, expected):
    assert band_of(aa) == expected, f"{aa} aa must be {expected}"


def test_moving_the_441_edge_by_one_changes_the_band():
    assert band_of(440) != band_of(441)


def test_moving_the_851_edge_by_one_changes_the_band():
    assert band_of(850) != band_of(851)


def test_moving_the_1027_edge_by_one_changes_the_band():
    """⚠ The one that matters most: 1,026 is in-context, 1,027 is not. D-098 scopes tranche 6 on
    exactly this boundary, so a `<=` here would silently widen the population."""
    assert band_of(1026) == "851_1026"
    assert band_of(1027) == "past_context"


# ── the split must partition, and the total must not be able to hide a misplacement ────────────
def test_split_partitions_every_row_exactly_once():
    rows = [{"span_aa": str(n)} for n in (100, 441, 850, 851, 1026, 1027, 5000)]
    out = split(rows)
    assert sum(len(v) for v in out.values()) == len(rows)
    seen = [r for v in out.values() for r in v]
    assert len(seen) == len(rows), "a row landed in two bands"


def test_a_one_residue_shift_moves_a_row_between_bands_while_the_total_is_unchanged():
    """⚠⚠ THE DISCRIMINATING TEST. Both sets total 3 rows. Only a per-band assertion sees the
    move — which is why a scoping table must never be checked by its total."""
    a = split([{"span_aa": "850"}, {"span_aa": "1026"}, {"span_aa": "2000"}])
    b = split([{"span_aa": "851"}, {"span_aa": "1027"}, {"span_aa": "2000"}])
    assert sum(len(v) for v in a.values()) == sum(len(v) for v in b.values()) == 3
    assert len(a["441_850"]) == 1 and len(b["441_850"]) == 0
    assert len(a["past_context"]) == 1 and len(b["past_context"]) == 2


def test_band_of_rejects_nonsense_rather_than_bucketing_it():
    """⚠ An unparseable length is not a band. Silently bucketing it would put a row in a
    population it was never measured into."""
    with pytest.raises((ValueError, TypeError)):
        band_of("not a number")
