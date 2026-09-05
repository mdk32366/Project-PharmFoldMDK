"""The never-folded census rows — shown, and REACHABLE by the name a reader types.

⚠⚠ The bug this file exists for: the ERBB2 row was listed and `HER2` still returned nothing, because
`aliases` was left `None`. **A row nobody can find is not shown.** Listing a protein and making it
searchable are two separate things, and shipping the first without the second looks like success.
"""
from __future__ import annotations

import pytest

import pathlib

from core.census_unfolded import REASON_COPY, counts_by_reason, unfolded_rows

ROWS = {r["accession"]: r for r in unfolded_rows()}

pytestmark = pytest.mark.skipif(not ROWS, reason="manifest or features artifact absent")


def test_her2_and_her3_are_present_and_carry_their_clinical_aliases():
    for acc, gene, alias in [("P04626", "ERBB2", "HER2"), ("P21860", "ERBB3", "HER3")]:
        row = ROWS[acc]
        assert row["gene"] == gene
        assert row["folded"] is False
        # ⚠⚠ the clause that was missing: present is not the same as findable
        assert alias in (row["aliases"] or []), (
            "%s is listed but carries no %s alias, so the search cannot reach it" % (gene, alias))


def test_closed_rental_copy_does_not_wait_on_a_terminated_pod():
    """D-118: 'waiting on rented capacity' is a live-queue claim and is false after closeout."""
    for copy in REASON_COPY.values():
        assert "waiting on rented capacity" not in copy
    assert "Terminated" in REASON_COPY["above_local_ceiling"]
    assert "out of class" in REASON_COPY["mucin_out_of_class"]


def test_every_row_states_a_reason_and_the_reasons_are_not_pooled():
    counts = counts_by_reason()
    assert set(counts) <= set(REASON_COPY)
    # ⚠ "too big" and "never tested" are different claims and must not be merged
    assert counts["above_local_ceiling"] > 0 and counts["ceiling_unmeasured"] > 0
    assert counts["above_local_ceiling"] != sum(counts.values())


def test_the_unexplained_row_keeps_its_own_category():
    """⚠⚠ P55073/DIO3 is tier `local`, span 237 aa. It should have folded and did not, and nothing
    records why. Folding it into "too big" would invent a fact about a protein nobody measured."""
    assert ROWS["P55073"]["not_folded_reason"] == "reason_unrecorded"
    assert "nothing records why" in ROWS["P55073"]["not_folded_copy"]


def test_no_fold_derived_value_is_reported_for_a_row_with_no_fold():
    for row in list(ROWS.values())[::120]:
        assert row["mean_plddt"] is None
        assert row["topology"] is None
        assert row["staining"] is None
        # ⚠ a CATEGORY, never None: "no fold to profile" is not "profile refused"
        assert row["profile_status"] == "not_folded"


def test_a_row_with_no_analysis_carries_no_id_to_link_by():
    assert all(r["id"] is None for r in list(ROWS.values())[:50])


def test_a_protein_in_BOTH_populations_still_serves_its_census_card():
    """⚠⚠ `P04626`/ERBB2 is one of the ranked 82 AND a census manifest row that was never folded.

    The route asked "is it cohort?" first, answered yes, and 404'd the card the census list had
    just linked to. **Being in one population does not stop a protein being in the other**, and
    this route serves the census one. The ordering is the whole fix.
    """
    src = pathlib.Path("app/read_routes.py").read_text(encoding="utf-8")
    unfolded_at = src.index("unfolded_rows")
    cohort_at = src.index('if outcome == "cohort"')
    assert unfolded_at < cohort_at, (
        "the cohort verdict is reached before the never-folded manifest is consulted, which 404s "
        "every protein that is in both populations — ERBB2 among them")
    assert "P04626" in ROWS, "ERBB2 must be in the never-folded manifest for that path to matter"
