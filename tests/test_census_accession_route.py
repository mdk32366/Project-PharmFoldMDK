"""`/census/{id}` accepts an accession — and a cohort accession still does NOT load here.

⚠⚠ THE DEFECT, FOUND BY WALKING THE LIVE SURFACE. The path param was `analysis_id: int`, so
`/census/P28908` returned **HTTP 422**. The census table DISPLAYS the accession, so the accession is
the first thing a person pastes — and 422 tells them their input was malformed. It was not: it was
the right protein under the wrong key. Two different messages, two different fixes.

⚠ AND THE POPULATION BOUNDARY IS WHY THIS RESOLVES RATHER THAN REDIRECTS. `D-081` measures the 82
and the census under different span definitions. A cohort accession here returns 404 **naming where
it lives**; silently serving it would hand back a row measured by a rule the caller did not ask for.
"""
from __future__ import annotations

import ast
import pathlib

import pytest


def _route_source() -> str:
    return pathlib.Path("app/read_routes.py").read_text(encoding="utf-8")


def test_the_path_param_is_no_longer_typed_as_int():
    """⚠ The whole 422 came from this one annotation."""
    tree = ast.parse(_route_source())
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "get_census_detail")
    arg = next(a for a in fn.args.args if a.arg == "analysis_id")
    assert arg.annotation is not None
    assert getattr(arg.annotation, "id", None) == "str", (
        "the param is typed %r; an int annotation is what returned 422 for every accession"
        % ast.dump(arg.annotation))


def test_a_numeric_id_still_takes_the_original_path():
    src = _route_source()
    assert "analysis_id.isdigit()" in src, (
        "numeric ids must still resolve directly — an accession lookup for '1901' would be a "
        "different query answering the same question, which is the two-paths defect")


# ⚠⚠ THE BOUNDARY. This is the clause that must not regress into a redirect.
def test_a_cohort_accession_is_refused_and_told_where_it_lives():
    src = _route_source()
    assert '"cohort"' in src
    assert "D-081" in src, "the refusal must name WHY, not just refuse"
    assert "/targets" in src, "a refusal that does not say where the protein lives is unhelpful"
    # ⚠ and it must be a 404, never a redirect — the two populations are measured differently
    assert "RedirectResponse" not in src
    assert "status_code=307" not in src and "status_code=302" not in src


def test_an_unknown_accession_says_so_rather_than_failing_validation():
    assert "no census protein carries the accession" in _route_source()


@pytest.mark.parametrize("acc,expected", [
    ("p28908", "P28908"),      # ⚠ case-folded, because people paste lowercase
    ("  P28908  ", "P28908"),  # ⚠ and with whitespace
])
def test_the_resolver_normalises_what_a_person_actually_pastes(acc, expected):
    from app.reads import resolve_census_accession
    src = pathlib.Path("app/reads.py").read_text(encoding="utf-8")
    assert '.strip().upper()' in src
    assert callable(resolve_census_accession)


def test_the_resolver_returns_an_outcome_not_just_none():
    """⚠⚠ Three outcomes, never two. `None` alone cannot distinguish 'not a protein' from 'a
    protein this route deliberately does not serve', and those need different messages."""
    src = pathlib.Path("app/reads.py").read_text(encoding="utf-8")
    fn = src[src.index("def resolve_census_accession"):]
    for outcome in ('"census"', '"cohort"', '"unknown"'):
        assert outcome in fn[:2600], outcome


# ── AMENDMENT 3 §2 — the dual-population accessions, exercised BEHAVIOURALLY ─────────────────
#
# ⚠⚠ WHY THIS EXISTS, AND IT IS ABOUT THE TESTS ABOVE, NOT THE CODE BELOW THEM.
# Every assertion above reads SOURCE TEXT — `'"cohort"' in src`, `"D-081" in src`, and
# `callable(resolve_census_accession)`, which asserts the function EXISTS and never what it
# RETURNS. Not one of them calls the resolver. That is `F-054` verbatim — *every test asserted
# the SHAPE of the code, none asserted that a row came back* — sitting on top of behaviour that
# happens to be correct. Correct behaviour protected by strings is one refactor away from
# incorrect behaviour protected by strings, and nothing would go red.
#
# ⚠ The string assertions are KEPT, not replaced (AMENDMENT 3 §2.2). They are not worthless;
# they are not behavioural. Deleting them trades one blind spot for another.
#
# ⚠ PROVENANCE (D-016). These 43 pairs are MEASURED, not invented: read-only SQL against
# production on 2026-09-11 as `schema_admin` through the owner-held proxy, repo `main` at
# `ffea42e`. 117 accessions carry more than one `protein_analyses` row; 43 of those touch
# tranches 1-4, and every one is a tranche-0 (cohort-82) row paired with exactly ONE census row.
# Zero tile rows among them. `ranking_run_id` is set on 43 of 43 cohort rows and NULL on 43 of
# 43 census rows.
#
# ⚠⚠ A-017 CLAUSE (c), SATISFIED BY THE DATA RATHER THAN ASSERTED ABOUT IT:
# `cohort_id < census_id` on all 43. A resolver taking *whichever row came first* returns the
# COHORT row, so these assertions fail under the exact defect they guard against. The fixture
# cannot be degenerate and cannot pass under a broken implementation.
#
# ⚠ SQLite is the substrate here and `F-056` is acknowledged: what is under test is Python-level
# filtering in `resolve_census_accession`, not a database constraint, so the substrate cannot
# forgive the defect. A test that depended on engine semantics would not belong here.
DUAL_POPULATION_43: list[tuple[str, int, int, int]] = [
    # accession, cohort_id (tranche 0), census_id, census tranche
    ("O00478", 4, 2027, 3),
    ("O00592", 24, 2496, 4),
    ("O14798", 38, 2100, 3),
    ("O60637", 40, 1720, 2),
    ("O75841", 42, 1577, 2),
    ("O75954", 41, 1410, 2),
    ("O95196", 11, 2530, 4),
    ("O95832", 10, 1462, 2),
    ("O95858", 39, 1600, 2),
    ("P08195", 32, 2756, 4),
    ("P09693", 7, 1512, 2),
    ("P19397", 8, 1667, 2),
    ("P22607", 15, 2720, 4),
    ("P24530", 13, 1528, 2),
    ("P32302", 12, 1768, 2),
    ("P42081", 9, 2085, 3),
    ("P50281", 23, 2480, 4),
    ("P51810", 17, 138, 1),
    ("P55064", 2, 849, 1),
    ("Q01814", 3, 610, 1),
    ("Q13421", 67, 2677, 4),
    ("Q13433", 31, 1969, 3),
    ("Q14CZ8", 20, 2404, 3),
    ("Q15858", 25, 1910, 2),
    ("Q3KNW5", 26, 237, 1),
    ("Q53GD3", 33, 2196, 3),
    ("Q5BKX6", 34, 1239, 1),
    ("Q5VUB5", 14, 2050, 3),
    ("Q5ZPR3", 6, 2684, 4),
    ("Q8IYL9", 19, 969, 1),
    ("Q8ND94", 21, 2297, 3),
    ("Q8TDU6", 16, 1394, 1),
    ("Q96NY8", 1, 2577, 4),
    ("Q99835", 36, 2429, 3),
    ("Q9BXP2", 28, 2029, 3),
    ("Q9BXS9", 29, 365, 1),
    ("Q9BY67", 5, 2670, 4),
    ("Q9GZU1", 22, 2101, 3),
    ("Q9NQ40", 35, 1757, 2),
    ("Q9NRM0", 30, 1269, 1),
    ("Q9NV96", 37, 1984, 3),
    ("Q9UP95", 27, 1747, 2),
    ("Q9UPC5", 18, 1411, 2),
]


def _dual_population_engine():
    """The 43 as production holds them: one tranche-0 row and one census row per accession."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from db.models import Base, JobRecord, ProteinAnalysis

    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with Session(eng) as s:
        for acc, cohort_id, census_id, tranche in DUAL_POPULATION_43:
            s.add(ProteinAnalysis(
                id=cohort_id, input_type="uniprot", input_value=acc,
                cohort_tranche=0, ranking_run_id=2,
                pdb_path=f"/data/artifacts/{cohort_id}/structure.pdb",
                mean_plddt=80.0, meta={"tier": "local"}))
            s.add(ProteinAnalysis(
                id=census_id, input_type="uniprot", input_value=acc,
                cohort_tranche=tranche, ranking_run_id=None,
                pdb_path=f"/data/artifacts/{census_id}/structure.pdb",
                mean_plddt=70.0, meta={"tier": "local"}))
            # ⚠⚠ THE JOB ROWS ARE NOT SCENERY. Census reads now select BY the generation label in
            # `jobs.inference_settings`, and production carries `run: 1` on 3,656 of 3,656 rows.
            # A fixture with no job rows has no label, so `keep_run_1` drops every row and all 43
            # resolve to `cohort` — which is exactly what happened when the filter landed, and it
            # made the suite RED rather than WRONG. `F-056` at fixture scope: a fixture that does
            # not carry what production carries is testing a different system.
            for aid in (cohort_id, census_id):
                s.add(JobRecord(id=aid, analysis_id=aid, status="succeeded", tier="local",
                                inference_settings={"source": "sliced_ecd", "run": 1}))
        s.commit()
    return eng


def test_the_fixture_holds_both_populations_and_the_wrong_answer_is_reachable():
    """⚠ A-017 POSITIVE CONTROL, and it is not ceremony.

    Without it every assertion below could pass against a fixture holding only census rows,
    proving nothing about resolution at all — the exact defect `F-054` records."""
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from db.models import ProteinAnalysis

    eng = _dual_population_engine()
    with Session(eng) as s:
        for acc, cohort_id, census_id, _ in DUAL_POPULATION_43:
            rows = s.scalars(
                select(ProteinAnalysis).where(ProteinAnalysis.input_value == acc)).all()
            assert len(rows) == 2, f"{acc} is not a two-population fixture"
            assert {r.cohort_tranche == 0 for r in rows} == {True, False}, (
                f"{acc} does not hold one cohort row and one census row")
            # ⚠⚠ The clause that makes the rest of this file bite: the WRONG row sorts FIRST.
            assert cohort_id < census_id, (
                f"{acc}: the cohort row no longer sorts first, so 'whichever comes first' would "
                f"coincide with the right answer and these tests would stop discriminating")


def test_every_dual_population_accession_resolves_to_its_CENSUS_row():
    """⚠⚠ THE ASSERTION THIS FILE WAS MISSING.

    `D-081` measures the two populations under different span definitions, so serving the cohort
    row here hands back a row measured by a rule the caller did not ask for — silently, and with
    a perfectly plausible payload. `F-047`'s class."""
    from app.reads import resolve_census_accession

    eng = _dual_population_engine()
    wrong = []
    for acc, _cohort_id, census_id, _ in DUAL_POPULATION_43:
        got = resolve_census_accession(eng, acc)
        if got != (census_id, "census"):
            wrong.append((acc, got, census_id))
    assert not wrong, (
        "these accessions did not resolve to their census row "
        f"(accession, got, expected_census_id) — {len(wrong)} of {len(DUAL_POPULATION_43)}: "
        + repr(wrong[:8]))


def test_a_cohort_only_accession_is_refused_rather_than_served():
    """⚠ The third outcome, run rather than grepped. A cohort accession is not reachable here
    and is not redirected — it is told where it lives."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from app.reads import resolve_census_accession
    from db.models import Base, ProteinAnalysis

    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with Session(eng) as s:
        s.add(ProteinAnalysis(id=9001, input_type="uniprot", input_value="P99999",
                              cohort_tranche=0, ranking_run_id=2, meta={}))
        s.commit()
    assert resolve_census_accession(eng, "P99999") == (None, "cohort")
    assert resolve_census_accession(eng, "P00000") == (None, "unknown")


def test_normalisation_holds_on_a_dual_population_accession():
    """⚠ The test above asserts `'.strip().upper()' in src`. This one runs it, against an
    accession that has a wrong answer available."""
    from app.reads import resolve_census_accession

    eng = _dual_population_engine()
    acc, _cohort_id, census_id, _ = DUAL_POPULATION_43[0]
    for typed in (acc.lower(), f"  {acc}  ", f" {acc.lower()} "):
        assert resolve_census_accession(eng, typed) == (census_id, "census"), (
            f"{typed!r} did not resolve like {acc!r}")
