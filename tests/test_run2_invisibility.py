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

⚠ RESOLVED 2026-09-11 by `keep_run_1` at the query sites. Both assertions below are now live,
and the ``xfail(strict=True)`` markings are gone because the property HOLDS — `XPASS(strict)` is
what forced their removal, which is the marking working rather than a suite being tidied.

So this file asserts BOTH, separately:
  * the BEHAVIOUR — Run 1 is returned; and
  * the MECHANISM — that the LABEL does it, proven by inverting the ids so the wrong generation
    sorts first. A read riding on id ordering fails that one.

⚠⚠ And the residual is asserted rather than described: an UNLABELLED call to the picker still
resolves by ``min(id)``. The boundary filter is the guarantee; the picker's optional labels are
defence in depth.
"""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.reads import choose_census_representative, resolve_census_accession, run_labels
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


def test_the_representative_picker_prefers_run_1_when_given_the_labels():
    """⚠ Defence in depth. The boundary filter is the guarantee; this is the picker refusing
    to resolve a mixed group by id ordering when it is told what the generations are.

    ⚠⚠ The picker is PURE and has no session, so it cannot fetch labels itself. A caller
    that omits them gets the historical behaviour — which is exactly why `keep_run_1` at the
    query sites, and not this, is what makes reads Run-1-only."""
    eng = _two_generation_engine(run1_id=9002, run2_id=1002)   # Run 2 has the LOWER id
    with Session(eng) as s:
        rows = s.scalars(select(ProteinAnalysis).where(ProteinAnalysis.input_value == ACC)).all()
        labels = run_labels(s, [r.id for r in rows])
        picked = choose_census_representative(list(rows), run_labels=labels)
    assert picked is not None
    assert picked[0].id == 9002, "the picker took the lower id rather than the Run 1 label"


def test_the_picker_without_labels_still_resolves_by_id_and_that_is_recorded():
    """⚠⚠ THE RESIDUAL, ASSERTED RATHER THAN DESCRIBED. An unlabelled call still picks
    `min(id)`. That is not a defect to fix here — it is why the boundary filter exists —
    but it must be visible, because a future caller that forgets `keep_run_1` gets the old
    behaviour silently (`F-052`: a convention obeyed by every caller except the newest)."""
    eng = _two_generation_engine(run1_id=9003, run2_id=1003)
    with Session(eng) as s:
        rows = s.scalars(select(ProteinAnalysis).where(ProteinAnalysis.input_value == ACC)).all()
        picked = choose_census_representative(list(rows))
    assert picked is not None
    assert picked[0].id == 1003, (
        "an unlabelled picker no longer resolves by id — if this changed deliberately, the "
        "boundary-filter reasoning above needs rewriting")
