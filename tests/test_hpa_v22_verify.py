"""Task G/I/J support — the modality classification and panel arithmetic, tested first.

These are pure functions on synthetic rows: no HPA file, no S3, no network. The acceptance check
itself is operator tooling over files the repo does not contain, so it is not under test here.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.hpa_v22_verify import (  # noqa: E402
    is_empty_panel, modality, panel_counts, panel_total,
)


def row(h, m, lo, nd):
    return {"High": h, "Medium": m, "Low": lo, "Not detected": nd}


def test_panel_counts_and_total():
    assert panel_counts(row(4, 2, 0, 6)) == (4, 2, 0, 6)
    assert panel_total(row(4, 2, 0, 6)) == 12


def test_an_empty_panel_is_detected():
    assert is_empty_panel(row(0, 0, 0, 0)) is True
    assert is_empty_panel(row(0, 0, 0, 1)) is False


def test_all_not_detected_is_NOT_an_empty_panel():
    """The discriminating one. Twelve patients all scored `Not detected` is a real measurement
    with a real answer. An empty panel is no measurement at all. Collapsing them would turn a
    genuine negative into a missing value, and vice versa."""
    assert is_empty_panel(row(0, 0, 0, 12)) is False
    assert modality(row(0, 0, 0, 12)) == "ihc"


def test_modality_never_claims_mrna():
    """The table cannot tell us a substitution happened, only that IHC was unavailable for it to
    substitute for. Claiming `mrna` would be inventing provenance."""
    assert modality(row(0, 0, 0, 0)) == "no_ihc_panel"
    assert modality(row(1, 0, 0, 0)) == "ihc"
    assert "mrna" not in {modality(row(0, 0, 0, 0)), modality(row(1, 2, 3, 4))}


def test_string_counts_are_coerced():
    """pathology.tsv is TSV, so every field arrives as a string."""
    assert panel_counts({"High": "4", "Medium": "2", "Low": "0", "Not detected": "6"}) == (4, 2, 0, 6)


def test_blank_counts_are_zero_not_an_error():
    assert panel_counts({"High": "", "Medium": "1", "Low": "", "Not detected": "2"}) == (0, 1, 0, 2)
