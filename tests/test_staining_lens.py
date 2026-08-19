"""The staining lenses — `D-102`. A way of looking, and it must say which way.

⚠⚠ The number that motivated the whole entry: over the same 1,727 census genes, "stains in 100% of
patients" is 728 genes under BEST_PANEL and 16 under POOLED. These tests exist so that difference
can never become invisible.
"""
from __future__ import annotations

import pytest

from core.staining_lens import (
    BEST_PANEL,
    CRITICAL_TISSUES,
    DEFAULT_MIN_PATIENTS,
    LENSES,
    POOLED,
    Panel,
    critical_hits,
    unknown_critical_tissues,
    view,
)


def P(cancer, h, m, l, nd):
    return Panel(cancer, h, m, l, nd)


# ⚠⚠ THE TWO LENSES DISAGREE ON THE SAME PROTEIN — the entire reason the ruling requires a name.
def test_the_same_protein_reads_differently_through_each_lens():
    panels = [P("ovarian cancer", 12, 0, 0, 0),        # 12/12 = 100%
              P("colorectal cancer", 0, 1, 1, 10)]     # 2/12  =  17%
    best = view(panels, BEST_PANEL, min_patients=10)
    pooled = view(panels, POOLED, min_patients=10)
    assert best.fraction == 1.0
    assert pooled.fraction == pytest.approx(14 / 24)
    # ⚠ the difference is not cosmetic; it is the finding
    assert best.fraction != pooled.fraction
    assert best.cancer == "ovarian cancer"
    assert pooled.cancer is None, "pooled has no single cancer and must not claim one"


def test_no_value_can_be_read_without_its_lens_and_its_n():
    v = view([P("x", 5, 0, 0, 5)], BEST_PANEL, min_patients=1)
    assert v.lens in LENSES
    assert v.patients_positive == 5 and v.patients_tested == 10
    # ⚠ the fraction is DERIVED from fields the consumer already holds — there is no bare number
    assert not hasattr(v, "value")
    assert v.fraction == 0.5


# ⚠⚠ F-043's defect, made unreachable by the floor.
def test_a_tiny_perfect_panel_does_not_beat_a_large_strong_one():
    panels = [P("rare cancer", 4, 0, 0, 0),            # 4/4 = 100%, n=4
              P("common cancer", 10, 1, 0, 1)]         # 11/12 = 92%, n=12
    unguarded = view(panels, BEST_PANEL, min_patients=1)
    assert unguarded.cancer == "rare cancer", "without a floor the small panel wins — the defect"

    guarded = view(panels, BEST_PANEL, min_patients=DEFAULT_MIN_PATIENTS)
    assert guarded.cancer == "common cancer"
    assert guarded.panels_excluded_small == 1, "the excluded panel is COUNTED, never silently gone"


def test_the_floor_reports_what_it_removed():
    v = view([P("a", 2, 0, 0, 1), P("b", 1, 0, 0, 2)], BEST_PANEL, min_patients=10)
    assert v.category == "no_panel_meets_floor"
    assert v.panels_considered == 2 and v.panels_excluded_small == 2
    assert v.fraction is None


# ⚠⚠ TWO ABSENCES, TWO CAUSES. Collapsing them reports the READER's choice as a fact about the
# PROTEIN.
def test_never_scored_and_no_panel_meets_floor_are_different_categories():
    assert view([], BEST_PANEL).category == "never_scored"
    assert view([P("a", 0, 0, 0, 0)], BEST_PANEL).category == "never_scored"
    assert view([P("a", 1, 0, 0, 1)], BEST_PANEL, min_patients=10).category == "no_panel_meets_floor"


def test_a_protein_that_never_stains_is_measured_not_absent():
    # ⚠ 3.5% of scored genes. `0 of 12` is a RESULT; it is not missing data.
    v = view([P("a", 0, 0, 0, 12)], BEST_PANEL, min_patients=10)
    assert v.category == "measured"
    assert v.fraction == 0.0
    assert v.patients_tested == 12


def test_ties_break_toward_the_larger_panel_never_arbitrarily():
    v = view([P("small", 10, 0, 0, 0), P("large", 30, 0, 0, 0)], BEST_PANEL, min_patients=10)
    assert v.cancer == "large" and v.patients_tested == 30


def test_an_unnamed_lens_is_refused_rather_than_defaulted():
    with pytest.raises(ValueError, match="named"):
        view([P("a", 1, 0, 0, 1)], "whatever")


# ⚠ the normal edge — independent, never combined
def test_critical_hits_flags_only_declared_tissues_at_High():
    rows = [("liver", "High"), ("lung", "Medium"), ("bronchus", "High"), ("kidney", "High")]
    assert critical_hits(rows) == ("kidney", "liver")


def test_medium_and_low_are_not_folded_into_the_critical_flag():
    assert critical_hits([("liver", "Medium"), ("lung", "Low")]) == ()


# ⚠⚠ THE `Cancer prognostics` DEFECT, GUARDED: a filter naming a tissue the data never uses removes
# nothing and looks like it worked.
def test_a_declared_tissue_absent_from_the_vocabulary_is_reported():
    assert unknown_critical_tissues(CRITICAL_TISSUES) == ()
    assert unknown_critical_tissues(["liver", "lung"]) == (
        "bone marrow", "cerebral cortex", "heart muscle", "kidney")


def test_every_declared_critical_tissue_exists_in_the_shipped_vocabulary():
    """⚠ Against HPA's real tissue strings, so a typo in the list cannot pass silently."""
    import csv
    import pathlib
    src = pathlib.Path("C:/Users/mdk32/Downloads/v22/normal_tissue.tsv")
    if not src.exists():
        pytest.skip("HPA normal_tissue.tsv not present locally")
    with src.open(encoding="utf-8") as fh:
        tissues = {r["Tissue"] for r in csv.DictReader(fh, delimiter="\t")}
    missing = unknown_critical_tissues(tissues)
    assert missing == (), "declared tissues absent from HPA's vocabulary: %s" % (missing,)
