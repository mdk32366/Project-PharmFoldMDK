"""Task §4.3 — Run 2 rows must be INVISIBLE to the reads, and the mechanism matters.

⚠⚠ REQUIRED RED BEFORE THE FIRST FOLD. Two rows per accession is `F-024`'s class — *a pattern
that occurs more than once, matched without a uniqueness check, takes the wrong occurrence* — with
`F-054`'s consequence. **If the scorer can see Run 2, `D-075`'s frozen anchor is back in play and
Run B breaks.**

⚠ THE FINDING THIS FILE RECORDS. Run 2 invisibility on the census detail route holds TODAY, and it
holds **BY ACCIDENT**: `choose_census_representative` ends at ``min(ordinary, key=lambda r: r.id)``,
so the older row wins because Run 2 rows are written later and get higher ids. **Nothing filters on
the generation label.** That is the right answer produced by id monotonicity rather than by a rule,
and it flips silently if the picker ever prefers the newest row, or if ids stop being monotonic in
write order.

So this file asserts BOTH, separately:
  * the BEHAVIOUR — Run 1 is returned — which passes today, and
  * the MECHANISM — that the label is what does it — which does NOT, and is marked ``xfail``
    ``strict=True`` so it cannot be quietly satisfied and flips the moment the filter lands.
"""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.reads import choose_census_representative, resolve_census_accession
from db.models import Base, JobRecord, ProteinAnalysis

ACC = "P00001"
RUN1_ID = 1000      # Run 1: written first, lower id
RUN2_ID = 9000      # Run 2: written later, higher id
TRANCHE = 2


def _two_generation_engine(run1_id: int = RUN1_ID, run2_id: int = RUN2_ID):
    """One accession, one census row per generation — what production looks like mid-campaign."""
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with Session(eng) as s:
        for aid, run in ((run1_id, 1), (run2_id, 2)):
            s.add(ProteinAnalysis(
                id=aid, input_type="uniprot", input_value=ACC, cohort_tranche=TRANCHE,
                ranking_run_id=None, pdb_path=f"/data/artifacts/{aid}/structure.pdb",
                mean_plddt=70.0, meta={"tier": "local"}))
            s.add(JobRecord(id=aid, analysis_id=aid, status="succeeded", tier="local",
                            inference_settings={"source": "sliced_ecd", "run": run}))
        s.commit()
    return eng


# ── A-017: the fixture must contain BOTH generations ─────────────────────────────────────────

def test_the_fixture_holds_both_generations():
    """⚠⚠ A-017. A uniqueness test against a single-generation fixture passes under ANY
    implementation, and is the exact defect `F-054` records."""
    eng = _two_generation_engine()
    with Session(eng) as s:
        rows = s.scalars(select(ProteinAnalysis).where(ProteinAnalysis.input_value == ACC)).all()
        runs = {s.get(JobRecord, r.id).inference_settings.get("run") for r in rows}
    assert len(rows) == 2, "not a two-generation fixture"
    assert runs == {1, 2}, f"the fixture does not hold both generations: {runs}"


# ── the behaviour: Run 1 is what comes back ──────────────────────────────────────────────────

def test_a_census_read_returns_the_run_1_row():
    """⚠ This passes today. The next test is about WHY."""
    eng = _two_generation_engine()
    aid, outcome = resolve_census_accession(eng, ACC)
    assert outcome == "census"
    assert aid == RUN1_ID, f"a census read returned {aid}, not the Run 1 row {RUN1_ID}"


# ── the mechanism: it must be the LABEL, not the id ordering ─────────────────────────────────

@pytest.mark.xfail(strict=True, reason=(
    "Task 4.1's run label is not consulted by any read. Run 1 wins only because "
    "choose_census_representative takes min(id) and Run 2 rows are written later. Flip the ids "
    "and the WRONG generation is served. This xfail is the required-red before the first fold; "
    "it turns green the moment the reads filter on the generation label."))
def test_the_run_label_is_what_selects_the_generation_not_the_id_ordering():
    """⚠⚠ THE ASSERTION THAT GATES THE CAMPAIGN.

    Invert the ids so Run 2 sorts FIRST. If the reads consulted the label, Run 1 would still be
    returned. If they are riding on id monotonicity, Run 2 is served — and the scorer's anchor is
    back in play the moment a Run 2 row can be picked up by anything keyed on accession.

    ⚠ This is `F-024` exactly: the right occurrence taken by luck is not a uniqueness check."""
    eng = _two_generation_engine(run1_id=9001, run2_id=1001)   # Run 2 now has the LOWER id
    aid, outcome = resolve_census_accession(eng, ACC)
    assert outcome == "census"
    assert aid == 9001, (
        "the read served the Run 2 row: selection is riding on id ordering, not on the "
        "generation label, so Run 2 invisibility holds only while ids stay monotonic in "
        "write order")


@pytest.mark.xfail(strict=True, reason="same gap, at the representative picker rather than the route")
def test_the_representative_picker_prefers_run_1_on_the_label():
    """⚠ The picker is where the choice is actually made; the route delegates to it."""
    eng = _two_generation_engine(run1_id=9002, run2_id=1002)
    with Session(eng) as s:
        rows = s.scalars(select(ProteinAnalysis).where(ProteinAnalysis.input_value == ACC)).all()
        picked = choose_census_representative(list(rows))
    assert picked is not None
    assert picked[0].id == 9002, "the picker took the lower id rather than the Run 1 label"
