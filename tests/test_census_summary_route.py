"""The census summary, and the route-ordering trap it sits on.

⚠⚠ `/census/summary` MUST be declared BEFORE `/census/{analysis_id}`. FastAPI matches in declaration
order and `{analysis_id}` is a `str` — so declared after, `summary` would be read as an ACCESSION and
return **404 with a sensible message about an unknown census protein**. Wrong-but-plausible,
produced by declaration order alone (`F-047`'s class).

⚠ The Story is the cold-open. `/census` is 7.1 MB uncompressed, 825 KB gzipped, ~4.8 s — measured
against production — so the summary exists because of weight, not tidiness.
"""
from __future__ import annotations

import ast
import pathlib

SRC = pathlib.Path("app/read_routes.py").read_text(encoding="utf-8")


def _decorated_paths() -> list[str]:
    """Every `@read_router.get(...)` path, in DECLARATION ORDER, read from the tree."""
    out: list[str] = []
    for node in ast.walk(ast.parse(SRC)):
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            fn = dec.func
            if getattr(fn, "attr", None) != "get":
                continue
            if dec.args and isinstance(dec.args[0], ast.Constant):
                out.append((node.lineno, dec.args[0].value))
    return [p for _, p in sorted(out)]


def test_summary_is_declared_before_the_detail_route():
    paths = _decorated_paths()
    assert "/census/summary" in paths, "the summary route is gone"
    assert "/census/{analysis_id}" in paths
    assert paths.index("/census/summary") < paths.index("/census/{analysis_id}"), (
        "`/census/summary` is declared after `/census/{analysis_id}`; FastAPI will match the "
        "detail route and look up the accession 'SUMMARY', returning a plausible 404")


def test_no_literal_path_is_shadowed_by_a_preceding_parameter_route():
    """⚠ The CLASS, not the instance. Any literal segment declared after a same-prefix parameter
    route is unreachable, and the failure is a sensible-looking 404 rather than an error."""
    paths = _decorated_paths()
    offenders = []
    for i, path in enumerate(paths):
        parts = path.split("/")
        if any(p.startswith("{") for p in parts):
            continue                                   # this one IS the parameter route
        for earlier in paths[:i]:
            e = earlier.split("/")
            if len(e) != len(parts):
                continue
            if all(a.startswith("{") or a == b for a, b in zip(e, parts)):
                offenders.append(f"{path} is shadowed by {earlier}")
    assert offenders == [], offenders


def test_the_summary_states_the_key_of_every_count_it_returns():
    """⚠ Every count states its key. The Story prints these numbers to every reader, so a
    denominator a reader has to guess is a denominator that will be guessed wrong."""
    reads = pathlib.Path("app/reads.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(reads))
              if isinstance(n, ast.FunctionDef) and n.name == "census_summary")
    code = ast.dump(fn)
    for field in ("manifest_rows", "folded", "max_mean_plddt"):
        assert field in code, field
    assert "keys" in code, "the payload must carry the key of each count"


def test_the_summary_reduces_the_list_rather_than_re_querying():
    """⚠⚠ Two independent queries over one population is how two surfaces come to disagree about it.
    `list_census` is the single definition of what a census row is; the summary reduces it."""
    reads = pathlib.Path("app/reads.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(reads))
              if isinstance(n, ast.FunctionDef) and n.name == "census_summary")
    calls = [n.func.id for n in ast.walk(fn)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
    assert "list_census" in calls
    assert "select" not in ast.dump(fn), "the summary must not build its own query"
