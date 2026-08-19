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


# ───────────────────────────────── CB4 — the census↔HPA join, and the fixture that breaks it ──
#
# ⚠⚠ A JOIN TEST THAT PASSES ON CLEAN DATA IS TESTING NOTHING (KEEL-1 V9 Principle 6 clause (c)).
# The census keys on UniProt accession, HPA on Ensembl gene id — a two-hop mapping — and *a
# case-mismatched join returning a clean zero three times* is a catalogued `F-047` member. So the
# fixture below is deliberately DIRTY: mixed case, leading and trailing whitespace, and a version
# suffix. Every one of those is a real shape in these files, and each would silently produce an
# empty intersection under a naive `==`.

from scripts.hpa_census_coverage import ensg_from_entry, norm  # noqa: E402


def _entry(hpa_id=None, ensembl_gene=None):
    xr = []
    if hpa_id is not None:
        xr.append({"database": "HPA", "id": hpa_id, "properties": []})
    if ensembl_gene is not None:
        xr.append({"database": "Ensembl", "id": "ENST00000264162.7",
                   "properties": [{"key": "GeneId", "value": ensembl_gene}]})
    return {"uniProtKBCrossReferences": xr}


def test_the_join_key_survives_case_and_whitespace():
    """⚠ The discriminating fixture. Delete `.strip().upper()` from `norm` and this reds."""
    dirty = ("  ensg00000115850  ", "ENSG00000115850", "ensg00000115850\t", " Ensg00000115850 ")
    assert len({norm(x) for x in dirty}) == 1, "the join key is not case/whitespace stable"
    assert norm(dirty[0]) == "ENSG00000115850"

    # ⚠ and the control: a NAIVE join over the same values produces four distinct keys, which is
    # exactly the clean-zero intersection this test exists to prevent.
    assert len(set(dirty)) == 4


def test_the_ensembl_gene_id_is_unversioned_before_it_is_joined():
    """HPA's files carry `ENSG00000115850`; UniProt's Ensembl xref carries `ENSG00000115850.10`.
    ⚠ Joining them without stripping the version is a clean zero on every row."""
    hpa, ens = ensg_from_entry(_entry(hpa_id="ENSG00000115850",
                                      ensembl_gene="ENSG00000115850.10"))
    assert hpa == {"ENSG00000115850"}
    assert ens == {"ENSG00000115850"}, "the Ensembl version suffix was not stripped"


def test_more_than_one_gene_is_returned_as_a_set_and_never_resolved():
    """⚠⚠ `P2`: `accession_ambiguous` is a CATEGORY, not a resolution rule. The extractor returns
    a SET so that *more than one* is representable at all — a scalar return would have to invent a
    first-match or alphabetical tie-break simply to have a value, and that is a dial nobody
    recorded."""
    doc = {"uniProtKBCrossReferences": [
        {"database": "HPA", "id": "ENSG00000000001", "properties": []},
        {"database": "HPA", "id": "ENSG00000000002", "properties": []},
    ]}
    hpa, _ = ensg_from_entry(doc)
    assert hpa == {"ENSG00000000001", "ENSG00000000002"}
    assert len(hpa) == 2, "ambiguity was collapsed to a single value somewhere"


def test_an_entry_with_no_hpa_or_ensembl_xref_yields_empty_sets_not_a_guess():
    """`hpa_absent` is a category with a cause. ⚠ Empty sets, never a fabricated id."""
    assert ensg_from_entry({"uniProtKBCrossReferences": []}) == (set(), set())
    assert ensg_from_entry({}) == (set(), set())
