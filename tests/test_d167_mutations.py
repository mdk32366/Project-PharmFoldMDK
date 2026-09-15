"""D-167 read — each property test FAILS on a copy of the script that lacks the property.

⚠⚠ WHY THIS FILE EXISTS (`ORDERS-Code-2026-09-16` A2.3). `scripts/d167_read_state.py` was written
BEFORE `tests/test_d167_read_state.py` — a recorded deviation from tests-first. The compensation was
to break each property in a copy of the script and show the matching test failing. **That was done in
a session and existed nowhere else**, which is `D-162` rule 8's class: state outside version control
determining a result. It is committed here, so the claim re-runs on every build.

**How.** For each mutant: copy the real source into `tmp_path/scripts/`, apply ONE named textual
change, load it AS `scripts.d167_read_state`, and require the named test to fail at its assertion.

⚠ **The unmutated control is not optional.** The first, session-only version of this harness reported
a failure on EVERY mutant for the write-once test — because a copy loaded from another directory
computes a different `OUT`. That was the harness, not the property. Here `OUT` is pinned back to the
real value after loading, and the control requires every named test to PASS on an unmutated copy
loaded the same way. A harness that fails the control proves nothing about the mutants.

⚠ Each anchor must occur exactly once in the real script. If the script changes so an anchor no
longer matches, this fails loudly rather than silently testing nothing.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REAL = REPO / "scripts" / "d167_read_state.py"
REAL_OUT = REPO / "data" / "control" / "d167" / "state_before.json"

#: (mutant name, anchor in the real source, replacement, the test that must fail)
MUTANTS = [
    ("no SET TRANSACTION READ ONLY",
     "        conn.execute(text(READ_ONLY))\n",
     "        pass\n",
     "test_the_transaction_helper_sets_read_only_as_its_first_statement"),
    ("identity asked after a reported read",
     "    assert_campaign_target(conn)\n\n    state: dict",
     "    conn.execute(text(\"SELECT to_jsonb(j) FROM jobs j LIMIT 1\"))\n"
     "    assert_campaign_target(conn)\n\n    state: dict",
     "test_identity_is_asked_before_any_reported_read"),
    ("a mutating statement executed",
     "    claimed = [r[0] for r in conn.execute(CLAIMED_SQL)]",
     "    conn.execute(text(\"UPDATE jobs SET tier = NULL WHERE false\"))\n"
     "    claimed = [r[0] for r in conn.execute(CLAIMED_SQL)]",
     "test_the_sql_the_read_executes_contains_no_mutation"),
    ("evidence overwritten",
     "    if path.exists():\n",
     "    if False:\n",
     "test_the_state_is_written_once_with_its_sha256"),
    ("main opens its own transaction",
     "        with read_only_transaction(eng) as conn:\n",
     "        with eng.begin() as conn:\n",
     "test_main_reads_only_through_the_helper"),
    ("task3 overlap hard-coded",
     "    return sorted(int(r[\"job_id\"]) for r in rows if lo <= float(r[\"span_aa\"]) <= hi)\n",
     "    return [3698, 3699, 3700, 3701, 3702, 3703, 3704, 3705]\n",
     "test_task3_overlap_is_computed_from_the_rows_given"),
]

NAMED_TESTS = sorted({m[3] for m in MUTANTS})


def _load(source: str, tmp_path: Path, monkeypatch):
    """Load `source` as `scripts.d167_read_state` and point the property tests at it."""
    import scripts.d166_collapse_duplicate_tiles  # noqa: F401 - resolved before the copy's sys.path edit
    import test_d167_read_state as t

    path = tmp_path / "scripts" / "d167_read_state.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")
    monkeypatch.setattr(sys, "path", list(sys.path))          # the copy inserts its own REPO
    spec = importlib.util.spec_from_file_location("scripts.d167_read_state", path)
    mod = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "scripts.d167_read_state", mod)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "OUT", REAL_OUT)                 # ⚠ the harness artifact, pinned
    monkeypatch.setattr(t, "SCRIPT", path)
    return t


def _call(t, name: str, tmp_path: Path):
    fn = getattr(t, name)
    if "tmp_path" in fn.__code__.co_varnames[: fn.__code__.co_argcount]:
        return fn(tmp_path / "work")
    return fn()


def test_every_anchor_occurs_exactly_once_in_the_real_script():
    src = REAL.read_text(encoding="utf-8")
    for name, anchor, _new, _test in MUTANTS:
        assert src.count(anchor) == 1, f"mutant {name!r}: anchor occurs {src.count(anchor)} times"


def test_control_every_named_test_passes_on_an_unmutated_copy(tmp_path, monkeypatch):
    t = _load(REAL.read_text(encoding="utf-8"), tmp_path, monkeypatch)
    for name in NAMED_TESTS:
        _call(t, name, tmp_path / name)


@pytest.mark.parametrize("mutant", MUTANTS, ids=[m[0] for m in MUTANTS])
def test_the_named_test_fails_on_the_mutant(mutant, tmp_path, monkeypatch):
    name, anchor, new, test_name = mutant
    src = REAL.read_text(encoding="utf-8")
    assert src.count(anchor) == 1, f"mutant {name!r}: anchor not found once"
    t = _load(src.replace(anchor, new), tmp_path, monkeypatch)
    with pytest.raises((AssertionError, pytest.fail.Exception)):
        _call(t, test_name, tmp_path)
