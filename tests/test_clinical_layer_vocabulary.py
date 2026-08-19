"""`EC1`, `EC4`, `EC5` and ruling 4 — the clinical layer's vocabulary, tested before any ingest.

⚠⚠ **NOTHING HERE INGESTS.** These are constraints on a schema that does not exist yet, which is
the order the project requires: `D-093` is a pre-registration and is void if code precedes it, and
`D-093 amendment 2` is what authorised this.

⚠ **Every assertion is paired with the case that makes it fail.** A vocabulary test that only ever
sees valid values is the vacuity `AC3` named — it would pass against a parser that accepted anything.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from core.clinical_layer import (  # noqa: E402
    CATEGORY_LAYERS,
    DERIVED_FACT,
    LEVEL_NON_ORDINAL,
    LEVEL_ORDINAL,
    LEVEL_VALUES,
    MAPPING_OUTCOME,
    MEASURED_CATEGORIES,
    SUPPLIER_ENCODING,
    IncomparableEdges,
    UnhandledLevel,
    is_ordinal,
    layers_of,
    tumour_normal_ratio,
)


# ────────────────────────────────────── EC4 — `Level` is not a four-value ordinal ──

def test_the_full_level_value_set_is_asserted_not_assumed():
    """⚠⚠ Ruling 7. Eight values were MEASURED in HPA v22; four of them are not positions on a
    scale. A schema treating `Level` as a 4-value ordinal silently mishandles 2,114 rows."""
    assert len(LEVEL_VALUES) == 8
    assert set(LEVEL_ORDINAL) == {"Not detected", "Low", "Medium", "High"}
    assert set(LEVEL_NON_ORDINAL) == {"N/A", "Ascending", "Descending", "Not representative"}
    assert not set(LEVEL_ORDINAL) & set(LEVEL_NON_ORDINAL), "a value cannot be both"


@pytest.mark.parametrize("level", LEVEL_ORDINAL)
def test_the_four_ordinal_values_are_placeable(level):
    assert is_ordinal(level) is True


@pytest.mark.parametrize("level", LEVEL_NON_ORDINAL)
def test_the_four_non_ordinal_values_are_not_placeable(level):
    """⚠ `Ascending` and `Descending` are GRADIENTS. They describe how staining varies across a
    structure, not how much there is. **No weighting can place them**, and a score that treats them
    as levels invents a position the annotation declined to give."""
    assert is_ordinal(level) is False


def test_an_unhandled_level_raises_rather_than_falling_through():
    """⚠⚠ THE DISCRIMINATING CASE, and the one `EC4` asks to be proven.

    HPA may add a value in a later release. A silent fallthrough would file it as whichever branch
    happened to be last — which is how `no topology` came to mean five different things.
    """
    for bogus in ("Very high", "high", "", "Moderate", "Ascending "):
        if bogus.strip() in LEVEL_VALUES:
            continue
        with pytest.raises(UnhandledLevel):
            is_ordinal(bogus)


def test_the_raise_names_the_value_and_the_ruling():
    with pytest.raises(UnhandledLevel) as exc:
        is_ordinal("Moderate")
    msg = str(exc.value)
    assert "Moderate" in msg and "ruling 7" in msg, (
        "a refusal a reader cannot act on is a crash with better manners")


# ─────────────────────────────────────────── EC1 — the layering, and it PARTITIONS ──

def test_the_five_measured_categories_partition_across_three_layers():
    """⚠⚠ `EC1`'s question answered: TWO LAYERS ARE NOT ENOUGH, three are.

    `hpa_absent` and `accession_ambiguous` are outcomes of the MAPPING — they happen before any
    supplier is consulted, so there is no supplier encoding to record and the derived fact is
    **`not_determinable`, which is not a synonym for `no_ihc_available`.**
    """
    assert len(MEASURED_CATEGORIES) == 5
    assert set(MEASURED_CATEGORIES) == {
        "ihc_present", "ihc_gene_absent", "ihc_panel_empty", "hpa_absent", "accession_ambiguous"}

    # ⚠ every category lands in exactly one cell of layer 1
    for cat in MEASURED_CATEGORIES:
        m, s, d = layers_of(cat)
        assert m in MAPPING_OUTCOME, cat
        assert d in DERIVED_FACT, cat
        assert (s is None) == (m != "mapped_one_gene"), (
            f"{cat}: supplier encoding must be defined exactly when the mapping resolved")
        if s is not None:
            assert s in SUPPLIER_ENCODING, cat

    # ⚠⚠ layer 1 is the partitioning layer: the three outcomes are covered and disjoint
    covered = {layers_of(c)[0] for c in MEASURED_CATEGORIES}
    assert covered == set(MAPPING_OUTCOME), "layer 1 does not cover its own vocabulary"

    # ⚠ the two supplier encodings for 'no IHC' are DISTINCT — 1,008 empty panels vs 1,023 omitted
    # genes are the same underlying fact under two encodings, and the record keeps which.
    assert layers_of("ihc_panel_empty")[1] == "row_present_panel_empty"
    assert layers_of("ihc_gene_absent")[1] == "row_absent"
    assert layers_of("ihc_panel_empty")[2] == layers_of("ihc_gene_absent")[2] == "no_ihc_available"
    assert layers_of("ihc_panel_empty")[1] != layers_of("ihc_gene_absent")[1], (
        "the two encodings collapsed into one — that is exactly the laundering ruling 5 bars")


def test_not_determinable_is_not_a_synonym_for_no_ihc_available():
    """⚠⚠ One says *the supplier has nothing*; the other says *we cannot ask*. Different facts."""
    assert layers_of("hpa_absent")[2] == "not_determinable"
    assert layers_of("accession_ambiguous")[2] == "not_determinable"
    assert "not_determinable" != "no_ihc_available"
    assert len(set(DERIVED_FACT)) == 3


def test_an_unknown_category_raises():
    """⚠ A sixth category is a measurement that changed, not a lookup miss."""
    with pytest.raises(ValueError):
        layers_of("ihc_probably_fine")


# ────────────────────────────────── ruling 4 — the edges cannot be combined ──

def test_no_tumour_normal_ratio_exists_and_the_call_itself_is_the_error():
    """⚠⚠ Ruling 4, structural. `pathology.tsv` has patient COUNTS; `normal_tissue.tsv` has NONE.

    ⚠ The function raises rather than returning `None`, because a `None` invites a caller to treat
    the absence as a missing value and fill it. **The ratio is pre-registered as not computable
    from this supplier** — an absence with a cause, not an unfilled intention.
    """
    with pytest.raises(IncomparableEdges):
        tumour_normal_ratio(tumour={"High": 5}, normal="Medium")
    with pytest.raises(IncomparableEdges):
        tumour_normal_ratio()


def test_the_refusal_states_why_rather_than_only_that():
    with pytest.raises(IncomparableEdges) as exc:
        tumour_normal_ratio()
    msg = str(exc.value)
    assert "ruling 4" in msg and "patient counts" in msg and "side by side" in msg
