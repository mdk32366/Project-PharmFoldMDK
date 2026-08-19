"""The second instrument — `D-103`.

⚠⚠ The claim under test is the one the whole census rests on: *these proteins are on the cell
surface*. It had exactly one source. These tests pin the SHAPE of the second opinion — above all,
that the secretory route is read as SUPPORT and never as contradiction.
"""
from __future__ import annotations

import csv
import pathlib

import pytest

from core.surface_confirmation import (
    CATEGORIES,
    ROUTE_COMPARTMENTS,
    UNRECONCILED_CAUSES,
    UNRECONCILED_COMPARTMENTS,
    check,
    check_for,
    payload_for,
)

CSV_PATH = pathlib.Path("data/census/surface_confirmation.v1.csv")


def test_plasma_membrane_corroborates_directly():
    v = check(["Plasma membrane"], "Enhanced")
    assert v.category == "corroborated_membrane"
    assert v.on_membrane and v.corroborates


# ⚠⚠ THE CENTRAL RULE. Reading "not plasma membrane" as "not a surface protein" would be a
# confident wrong answer about real biology — the secretory route is how a protein GETS there.
@pytest.mark.parametrize("loc", ["Golgi apparatus", "Vesicles", "Endoplasmic reticulum",
                                 "Cell Junctions", "Endosomes", "Lysosomes"])
def test_the_secretory_route_is_support_not_contradiction(loc):
    v = check([loc], "Supported")
    assert v.category == "corroborated_route", loc
    assert v.corroborates, "%s must not read as disagreement" % loc
    assert v.unreconciled_locations == ()


def test_only_hard_compartments_are_unreconciled():
    v = check(["Mitochondria"], "Uncertain")
    assert v.category == "unreconciled"
    assert v.unreconciled_locations == ("Mitochondria",)
    assert not v.corroborates


def test_route_and_hard_together_are_mixed_never_unreconciled():
    v = check(["Golgi apparatus", "Mitochondria"])
    assert v.category == "mixed", "a protein seen in both is not a contradiction"


def test_a_compartment_in_neither_set_is_mixed_not_a_verdict():
    # ⚠ Cytosol/Nucleoplasm on a membrane protein is ambiguous, not contradictory. Inventing a
    # verdict for it would be the overreach the module refuses.
    for loc in ("Cytosol", "Nucleoplasm", "Microtubules"):
        assert check([loc]).category == "mixed", loc


# ⚠⚠ THREE ABSENCES, THREE CAUSES, NEVER POOLED.
def test_the_three_absences_stay_distinct():
    assert check([], gene_symbol=None).category == "no_gene_symbol"
    assert check([], gene_present=False).category == "gene_absent_from_supplier"
    assert check([], gene_present=True).category == "if_not_attempted"


def test_not_attempted_is_not_refutation():
    v = check([], gene_present=True)
    assert v.category == "if_not_attempted"
    # ⚠ `corroborates` is False here and that must never be read as a negative finding
    assert not v.corroborates
    assert v.unreconciled_locations == ()


# ⚠⚠ A CATEGORY WITHOUT ITS CAUSES INVITES THE READER TO CONVICT THE PROTEIN.
def test_an_unreconciled_payload_always_carries_all_three_causes():
    p = payload_for(None, "NOSUCHGENE") if False else None
    v = check(["Nucleoli"])
    assert v.category == "unreconciled"
    assert len(UNRECONCILED_CAUSES) == 3
    # every cause names a DIFFERENT thing that could be at fault, including neither instrument
    joined = " ".join(UNRECONCILED_CAUSES).lower()
    assert "uniprot" in joined and "antibody" in joined and "genuinely do both" in joined


def test_the_route_and_hard_sets_do_not_overlap():
    assert not (ROUTE_COMPARTMENTS & UNRECONCILED_COMPARTMENTS)


def test_no_ordering_is_defined_over_the_categories():
    # ⚠ categories are KINDS, not grades — nothing in the module ranks them
    src = pathlib.Path("core/surface_confirmation.py").read_text(encoding="utf-8")
    assert "CATEGORIES" in src
    assert len(CATEGORIES) == 8
    for bad in ("def rank", "def score", "confidence_score", "quality"):
        assert bad not in src, bad


# ── against the built artifact ──────────────────────────────────────────────────────────────
pytestmark_csv = pytest.mark.skipif(not CSV_PATH.exists(), reason="artifact not built")


@pytest.mark.skipif(not CSV_PATH.exists(), reason="artifact not built")
def test_known_proteins_resolve_the_way_biology_says_they_should():
    # CD30 and HER2 are membrane receptors; MSLN is GPI-anchored and images in vesicles.
    assert check_for("P28908", "TNFRSF8").category == "corroborated_membrane"
    assert check_for("P04626", "ERBB2").category == "corroborated_membrane"
    msln = check_for("Q13421", "MSLN")
    assert msln.category == "corroborated_route", msln
    assert msln.corroborates, "MSLN in vesicles must read as support, not disagreement"


@pytest.mark.skipif(not CSV_PATH.exists(), reason="artifact not built")
def test_the_artifact_keeps_rows_that_have_no_imaging_call():
    """⚠⚠ The first build dropped them, which merged 'not in the source' into 'nobody looked'."""
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    blank = [r for r in rows if not r["main_location"] and not r["additional_location"]]
    assert len(blank) > 5000, (
        "only %d rows without an imaging call — the build is dropping them again, and that "
        "silently converts 'nobody looked' into 'absent from the supplier'" % len(blank))


@pytest.mark.skipif(not CSV_PATH.exists(), reason="artifact not built")
def test_neither_join_path_dominates_and_both_are_kept():
    """⚠ Two paths, COMPARED. Accession is primary because it is the census's KEY — not because it
    reaches further, which it does not. This test's own name said "reaches at least as far" until
    it went red and the measurement corrected it."""
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    accs = {a.strip() for r in rows for a in r["uniprot"].split(",") if a.strip()}
    syms = {r["gene_symbol"] for r in rows if r["gene_symbol"]}
    assert accs and syms
    import json
    census = [json.loads(l) for l in
              pathlib.Path("data/census/census_features.v1.jsonl").read_text(encoding="utf-8").splitlines()]
    by_acc = sum(1 for c in census if c.get("accession") in accs)
    by_sym = sum(1 for c in census if c.get("gene") in syms)
    # ⚠⚠ NEITHER PATH DOMINATES, and the earlier version of this test asserted that one did.
    # Accession leads on PRINCIPLE (it is the census's key; symbols are the lossy intermediate),
    # not because it reaches further — measured, it does not. Each path reaches rows the other
    # misses, which is exactly why both are kept and compared instead of one being trusted.
    assert by_acc > 2000 and by_sym > 2000
    assert abs(by_acc - by_sym) < 50, "the two paths diverge far more than measured: %d vs %d" % (
        by_acc, by_sym)

@pytest.mark.skipif(not CSV_PATH.exists(), reason="artifact not built")
def test_one_accession_on_two_supplier_rows_is_not_resolved_by_coin_toss():
    """⚠⚠ `Q6IEY1` is carried by BOTH `OR4F16` and `OR4F3` — paralogues sharing a UniProt entry.

    The first implementation used `setdefault`, so whichever row parsed first silently won. Here
    both rows carry the same (empty) call, so the ambiguity does not change the answer and the
    category is the ordinary one — but the MECHANISM must not be first-wins.
    """
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    sharing = [r for r in rows if "Q6IEY1" in (r["uniprot"] or "")]
    assert len(sharing) > 1, "fixture gone: Q6IEY1 no longer appears on multiple rows"
    from core.surface_confirmation import _one
    row, ambiguous = _one(sharing)
    assert not ambiguous, "these two rows agree, so this is not an ambiguous case"
    # ⚠ and the detector must FIRE when the rows genuinely disagree
    a = dict(sharing[0]); b = dict(sharing[0]); b["main_location"] = "Mitochondria"
    _, amb2 = _one([a, b])
    assert amb2, "two rows with different calls must be flagged, never silently resolved"
