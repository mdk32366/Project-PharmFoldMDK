"""D-167 amendment 1 §2 (ORDERS A3.2 + A4.2) — every Phase D script says which role it is BEFORE its
first write, and the index build's privilege is answered before the sitting's first write.

⚠⚠ Planner error 3 corrected: `CREATE INDEX` needs OWNERSHIP of `jobs` (or membership in the owning
role), not a `CREATE` grant. If the effective role cannot build `0014`, the collapse — an irreversible
delete whose only purpose is to let that index build — WAITS; the re-attach proceeds.

⚠ Calibrated (`D-162` rule 7): the preamble must report `can_build_jobs_index = False` for a role that
does not own `jobs`, not only `True` for the fixture's superuser.
"""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path

import pytest
from sqlalchemy import text

REPO = Path(__file__).resolve().parent.parent
PHASE_D_SCRIPTS = ("scripts/d167_reattach.py", "scripts/d166_collapse_duplicate_tiles.py")


def _module(name: str):
    assert importlib.util.find_spec(name) is not None, f"{name} does not exist"
    return importlib.import_module(name)


def test_the_refusal_names_the_owner_and_is_silent_when_the_role_can_build():
    role = _module("core.db_role")
    ok = {"current_user": "schema_admin", "jobs_owner": "schema_admin", "can_build_jobs_index": True}
    assert role.index_build_refusal(ok) is None
    bad = dict(ok, jobs_owner="fly_owner", can_build_jobs_index=False)
    msg = role.index_build_refusal(bad)
    assert msg and "fly_owner" in msg and "schema_admin" in msg and "0014" in msg


@pytest.mark.parametrize("rel", PHASE_D_SCRIPTS)
def test_every_phase_d_script_asks_its_role_before_its_identity_and_its_first_write(rel):
    from test_d159_enqueue_identity import _MUTATION, _code_only

    _module("core.db_role")
    code = _code_only((REPO / rel).read_text(encoding="utf-8"))
    assert "role_preamble(" in code, f"{rel} never prints the role preamble"
    pre = code.index("role_preamble(conn)" if "role_preamble(conn)" in code else "role_preamble(c)")
    ident = code.index("assert_campaign_target(")
    first = _MUTATION.search(code)
    assert pre < ident, f"{rel}: identity is asked before the role preamble"
    assert first is None or pre < first.start(), f"{rel}: a write precedes the role preamble"


@pytest.mark.postgres
def test_the_preamble_measures_the_role_and_can_say_no(pg_engine):
    role = _module("core.db_role")
    with pg_engine.begin() as c:
        pre = role.role_preamble(c)
    for key in ("session_user", "current_user", "role", "rolconfig", "rolsuper", "jobs_owner",
                "can_build_jobs_index"):
        assert key in pre, key
    assert pre["jobs_owner"], "the owner of jobs was not read"
    assert pre["can_build_jobs_index"] is True, pre

    with pg_engine.begin() as c:
        c.execute(text("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = "
                       "'d167_not_owner') THEN CREATE ROLE d167_not_owner NOLOGIN; END IF; END $$"))
    try:
        with pg_engine.begin() as c:
            c.execute(text("SET LOCAL ROLE d167_not_owner"))
            pre = role.role_preamble(c)
        assert pre["current_user"] == "d167_not_owner" and pre["role"] == "d167_not_owner"
        assert pre["can_build_jobs_index"] is False, pre
    finally:
        with pg_engine.begin() as c:
            c.execute(text("DROP ROLE IF EXISTS d167_not_owner"))


@pytest.mark.postgres
def test_the_collapse_waits_with_0014_when_the_role_cannot_build_the_index(live_db, monkeypatch,
                                                                            capsys):
    import scripts.d166_collapse_duplicate_tiles as c
    from test_d166_collapse_guards import _counts, _run

    monkeypatch.setattr(c, "role_preamble", lambda conn: {
        "session_user": "x", "current_user": "x", "role": "none", "rolconfig": None,
        "rolsuper": False, "jobs_owner": "someone_else", "can_build_jobs_index": False},
        raising=False)
    url = live_db.url.render_as_string(hide_password=False)
    before = _counts(live_db)
    rc = _run(["--url", url, "--i-am-the-owner"], monkeypatch)
    assert rc == 1, f"the role cannot build 0014 and the collapse returned {rc!r}"
    assert _counts(live_db) == before, "the collapse deleted rows the index could not then use"
    assert "someone_else" in capsys.readouterr().out, "the refusal does not name the owner of jobs"


from test_d166_collapse_guards import live_db, pre_0014  # noqa: E402,F401  (fixtures)
