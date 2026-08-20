"""The PAE read route — and why it is a route rather than filesystem access.

⚠⚠ THE 79 MATRICES LIVE ON THE PRODUCTION VOLUME. An analysis question needed them, and the two
ways to get them are not equivalent. Reaching in with `fly ssh` is production filesystem access for
a read — the shape closed the day before, where *a tunnel to production looks exactly like
localhost and the WINDOW is the hazard, not the query*. A route goes through the gate, is testable,
and uses the reader role that already exists.

⚠ 2,692 of 2,771 rows carry no PAE. A 404 here is the ORDINARY case for a census protein, so the
message has to say which — otherwise a caller reads a recorded finding (`F-042`) as a broken file.
"""
from __future__ import annotations

import ast
import pathlib

ROUTES = pathlib.Path("app/read_routes.py").read_text(encoding="utf-8")
READS = pathlib.Path("app/reads.py").read_text(encoding="utf-8")


def test_the_route_exists_and_is_a_GET():
    assert '@read_router.get("/analyses/{analysis_id}/pae")' in ROUTES


# ⚠⚠ READ-ONLY, ASSERTED STRUCTURALLY. A route that reaches production data must not be able to
# change it, and "it only reads" is a claim until something checks.
def test_the_route_performs_no_write():
    tree = ast.parse(ROUTES)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "get_pae")
    code = "\n".join(ast.dump(n) for n in fn.body)
    for banned in ("delete", "add", "commit", "execute", "update", "merge"):
        assert banned not in code.lower(), banned


def test_no_client_value_reaches_the_filesystem():
    """⚠ The path comes from the ROW, never from the request — the traversal defence that
    `get_structure_path` already established, reused rather than re-argued."""
    tree = ast.parse(READS)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "get_pae_path")
    code = "\n".join(ast.dump(n) for n in fn.body)
    # the only input is the analysis_id, and it is used to fetch a row — not to build a path
    assert "pae_json_path" in code
    assert "join" not in code.lower() and "Path(" not in code


# ⚠⚠ THE ABSENCE IS THE COMMON CASE AND MUST NOT READ AS A FAULT.
def test_no_pae_is_explained_as_a_recorded_finding_not_a_missing_file():
    seg = ROUTES[ROUTES.index("def get_pae("):]
    seg = seg[:seg.index("@read_router")] if "@read_router" in seg else seg
    assert "F-042" in seg, "the ordinary 404 must name the finding it reflects"
    assert "not a missing file" in seg
    assert "2,692" in seg, "the denominator makes it obvious this is the common case"


def test_a_stored_path_that_does_not_resolve_is_a_different_404():
    """⚠ 'no PAE recorded' and 'a recorded PAE that is gone' are different facts. One is F-042
    working as designed; the other is data loss, and collapsing them would hide the second."""
    seg = ROUTES[ROUTES.index("def get_pae("):]
    assert "does not resolve" in seg


def test_it_never_returns_500_for_either_absence():
    seg = ROUTES[ROUTES.index("def get_pae("):]
    seg = seg[:seg.index("@read_router")] if "@read_router" in seg else seg
    assert seg.count("status_code=404") == 2
    assert "status_code=500" not in seg
