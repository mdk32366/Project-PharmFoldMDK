"""KEEL V8-a — the guard that would have prevented 2026-08-17.

⚠ The suite must refuse to run when `DATABASE_URL` points at a database whose data is not
expendable. The previous guard pointed the wrong way: `pg_engine` skips *unless* Postgres is
reachable, so **production credentials armed it**.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tests"))

from _db_safety import DISPOSABLE_HOSTS, OVERRIDE_ENV, OVERRIDE_VALUE, db_host, refusal_reason  # noqa: E402

PROD = "postgresql://fly-user:secret@pgbouncer.zp2wjrej9lwodn4q.flympg.net/pharmfoldmdk"
LOCAL = "postgresql+psycopg://fly-user:secret@localhost:16380/pharmfoldmdk"


def test_it_refuses_the_exact_url_that_destroyed_production():
    """⚠⚠ THE REGRESSION, named. This is the shape `.env` had on 2026-08-17."""
    reason = refusal_reason({"DATABASE_URL": PROD})
    assert reason is not None
    assert "REFUSING TO RUN" in reason
    assert "pgbouncer.zp2wjrej9lwodn4q.flympg.net" in reason


def test_the_refusal_says_what_the_suite_would_have_done():
    """⚠ A refusal that does not name TRUNCATE teaches the reader to override it."""
    reason = refusal_reason({"DATABASE_URL": PROD})
    assert "TRUNCATE" in reason
    assert "2026-08-17" in reason, "the refusal should cite the incident, not just assert a rule"


def test_no_database_url_is_the_ordinary_local_gate():
    """⚠ The common case must not need an override, or the override becomes habitual."""
    assert refusal_reason({}) is None


def test_a_loopback_proxy_is_allowed():
    assert refusal_reason({"DATABASE_URL": LOCAL}) is None
    for host in DISPOSABLE_HOSTS:
        # ⚠ IPv6 arrives bracketed in a real URL; both forms must be recognised.
        h = f"[{host}]" if ":" in host else host
        assert refusal_reason({"DATABASE_URL": f"postgresql://u:p@{h}:5432/db"}) is None


def test_ci_is_allowed_because_its_database_is_a_service_container():
    assert refusal_reason({"DATABASE_URL": PROD, "CI": "true"}) is None


def test_the_override_must_be_a_sentence_not_a_flag():
    """⚠ `1`/`true` are what people set by habit. The value has to be meant."""
    assert refusal_reason({"DATABASE_URL": PROD, OVERRIDE_ENV: "1"}) is not None
    assert refusal_reason({"DATABASE_URL": PROD, OVERRIDE_ENV: "true"}) is not None
    assert refusal_reason({"DATABASE_URL": PROD, OVERRIDE_ENV: OVERRIDE_VALUE}) is None


def test_an_unparseable_url_is_treated_as_NOT_disposable():
    """⚠ Fail closed. A URL we cannot read is not a URL we can vouch for."""
    assert refusal_reason({"DATABASE_URL": "not a url at all"}) is not None


def test_the_host_parser_is_not_fooled_by_a_password_containing_an_at_sign():
    """⚠ A password with `@` in it would otherwise shift the parsed host, and a misparse here
    fails OPEN in the worst case — reading a production host as something disposable."""
    assert db_host("postgresql://user:p@ss@prod.example.net/db") == "prod.example.net"
    assert refusal_reason({"DATABASE_URL": "postgresql://user:p@ss@prod.example.net/db"}) is not None


def test_conftest_actually_wires_the_guard_in():
    """⚠ A guard that exists but is never called is a comment. Asserted over the source, so it
    survives the implementation being rewritten."""
    src = (REPO / "tests" / "conftest.py").read_text(encoding="utf-8")
    assert "refusal_reason" in src, "conftest does not consult the guard"
    assert "pytest_collection_modifyitems" in src, "the guard is not hooked into collection"
    assert "UsageError" in src, "the guard does not FAIL the run — a skip is what let this happen"


# ── ⚠ every .env variant must be ignored, not just the file called `.env` ────────────────────────
def test_every_env_variant_is_gitignored_not_just_dot_env():
    """⚠⚠ On 2026-08-17 a backup named `.env.env.bak-precluster-swap` was created during a cluster
    swap. It held the OLD production database password and was **not ignored** — one unscoped
    `git add -A` from a public repository.

    The pattern was `.env`, which matches the file called `.env` and nothing else: the narrowest
    possible reading of an intent that was obviously broader. ⚠ `.env.example` must stay tracked,
    so the negation is asserted too — a fix that ignores the template breaks every fresh clone."""
    ignore = (REPO / ".gitignore").read_text(encoding="utf-8")
    assert ".env*" in ignore, "a .env backup or variant would not be ignored"
    assert "!.env.example" in ignore, "the template must stay tracked or a fresh clone has no example"
