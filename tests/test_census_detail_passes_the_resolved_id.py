"""⚠⚠ EVERY ONE OF THE 2,690 FOLDED CENSUS CARDS RETURNED HTTP 500 IN PRODUCTION, AND THE GATE WAS GREEN.

`/census/{analysis_id}`'s path param was widened from `int` to `str` so an accession could be used
as a key — the right change, and `D-101`'s reason for it stands. But one downstream call kept passing
the **raw parameter** instead of the **resolved integer**:

    record["structural_profile_block"] = census_profile_block(engine, analysis_id)   # a str
                                                                       ^^^^^^^^^^^

`census_profile_block(engine, analysis_id: int)` does `session.get(ProteinAnalysis, analysis_id)`.

⚠⚠ **AND THIS IS WHY 1,015 TESTS SAW NOTHING.** The suite runs on **SQLite**, whose type affinity
**accepts `"1970"` as an integer primary key** and **returns `None` for `"A0AVI2"` without raising**.
Production is **Postgres**, which rejects both. **The gate was green on a database that forgives
exactly the mistake production rejects** — so the tests were not weak, they were run against the
wrong engine to see this class at all.

⚠ The guard therefore cannot be "does it 500" — on SQLite it never will. It asserts **what is passed**:
the resolved integer, never the raw path string. That is checkable on any engine.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

ROUTES_SRC = pathlib.Path("app/read_routes.py").read_text(encoding="utf-8")


def _route_fn():
    return next(n for n in ast.walk(ast.parse(ROUTES_SRC))
                if isinstance(n, ast.FunctionDef) and n.name == "get_census_detail")


def test_the_profile_block_is_given_the_resolved_id_not_the_path_string():
    """⚠ The defect in one identifier: `analysis_id` where `resolved` was meant."""
    fn = _route_fn()
    calls = [n for n in ast.walk(fn)
             if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Name) and n.func.id == "census_profile_block"]
    assert calls, "census_profile_block is no longer called from this route"
    for call in calls:
        key = call.args[1]
        assert isinstance(key, ast.Name), ast.dump(key)
        assert key.id == "resolved", (
            "census_profile_block takes `analysis_id: int`; the path param is a `str` so an "
            "accession can be used as a key. Passing the raw param 500s on Postgres for every "
            "folded census row — and SQLite will not reproduce it.")


def test_no_supplier_in_this_route_receives_the_raw_path_parameter_as_a_key():
    """⚠⚠ The class, not the instance. `analysis_id` may still be READ — it is the accession the
    404 messages name — but it must never be handed to something that wants a primary key."""
    fn = _route_fn()
    for call in (n for n in ast.walk(fn) if isinstance(n, ast.Call)):
        name = getattr(call.func, "attr", None) or getattr(call.func, "id", None)
        if name not in {"census_profile_block", "get_census_detail", "clinical_block"}:
            continue
        for arg in call.args:
            if isinstance(arg, ast.Name) and arg.id == "analysis_id":
                pytest.fail(
                    f"{name}() receives the raw path string; pass `resolved` (the int) instead")


# ⚠⚠ THE ENGINE DIVERGENCE ITSELF, ASSERTED — so the reason the gate was blind is recorded as a
# fact and not only as a comment. If a future SQLAlchemy or SQLite tightens this, the test says so.
def test_sqlite_forgives_the_string_primary_key_that_postgres_rejects():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from db.models import Base, ProteinAnalysis

    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(ProteinAnalysis(id=1970, input_type="uniprot", input_value="A0AVI2",
                              cohort_tranche=1))
        s.commit()
    with Session(engine) as s:
        # ⚠ a STRING primary key, silently coerced — this is what kept the suite green
        assert s.get(ProteinAnalysis, "1970") is not None, (
            "SQLite no longer coerces a string PK; if so this test's premise has changed and the "
            "gate may now be able to see the class directly")
        # ⚠ and a non-numeric key returns None rather than raising, so nothing reddened
        assert s.get(ProteinAnalysis, "A0AVI2") is None
