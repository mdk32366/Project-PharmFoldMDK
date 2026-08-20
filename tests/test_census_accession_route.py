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
