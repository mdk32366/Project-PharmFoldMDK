"""D-158 — the test suite refuses to run unless the target database PROVES it is disposable.

⚠⚠ **THE REGRESSION THIS FILE EXISTS FOR, AND IT HAS FIRED TWICE.** 2026-08-17 (`protein_analyses`
2,771 → 1) and 2026-09-13 (4,535 → 1), both on the same signature: `tests/conftest.py`'s
`TRUNCATE … CASCADE` running in a shell whose `DATABASE_URL` was a `fly mpg proxy` tunnel at
`127.0.0.1:16380`.

⚠ **The old guard trusted a HOSTNAME, and `127.0.0.1` was on its trusted list.** It named its own
blind spot in its own docstring — *"a tunnel to production looks exactly like localhost … this guard
is necessary and not sufficient"* — and the suite ran anyway, twice. A hostname cannot survive this
project's infrastructure pattern, because the tunnel is indistinguishable from loopback **by
construction**.

⚠⚠ **So trust moves from the URL to the DATABASE.** The target must hold a marker that only a
disposable database carries. A tunnel faithfully reports the target's contents — that is the whole
argument, and it is why this mechanism cannot be defeated by the thing that defeated the last one.

⚠ **The first test below is a FAILURE-red against the old implementation, not an error-red.** It
calls the guard the way the old one could answer, the old guard is reached, and it answers
`None` — permitted. That is the exact case that truncated production.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tests"))

from _db_safety import (  # noqa: E402
    MARKER_TABLE,
    OVERRIDE_ENV,
    db_host,
    db_name,
    override_value_for,
    refusal_reason,
)

#: ⚠ The shape `.env` had on both incident days: a tunnel, so the host is loopback.
TUNNELLED_PROD = "postgresql+psycopg://fly-user:secret@127.0.0.1:16380/pharmfoldmdk"
#: The pre-tunnel shape, kept because it is the 2026-08-17 URL.
NAMED_PROD = "postgresql://fly-user:secret@pgbouncer.zp2wjrej9lwodn4q.flympg.net/pharmfoldmdk"
DISPOSABLE = "postgresql+psycopg://postgres:postgres@localhost:5432/pharmfold_test"


def marker_present(url):          # noqa: ARG001 - a probe that finds the marker
    return True


def marker_absent(url):           # noqa: ARG001 - a probe that does not
    return False


def probe_explodes(url):          # noqa: ARG001
    raise RuntimeError("could not connect")


# ── ⚠⚠ the regression, named ────────────────────────────────────────────────────────────────────

def test_a_tunnelled_production_database_at_127_0_0_1_is_REFUSED():
    """⚠⚠ **THE CASE THAT FIRED, TWICE.** Loopback host, production contents, no marker.

    ⚠ This is the failure-red: the old hostname guard is *reached*, *answers*, and answers
    `None` — because `127.0.0.1` was on its trusted list. The guard was not absent; it was wrong.
    """
    reason = refusal_reason({"DATABASE_URL": TUNNELLED_PROD}, probe=marker_absent)
    assert reason is not None, (
        "a tunnel to production presents as 127.0.0.1 and MUST be refused — this is the exact "
        "configuration that truncated production on 2026-08-17 and again on 2026-09-13")
    assert "REFUSING TO RUN" in reason


def test_the_refusal_names_what_the_suite_would_have_done_and_cites_BOTH_incidents():
    """⚠ A refusal that does not name `TRUNCATE` teaches the reader to override it, and one that
    cites a single incident reads as bad luck rather than as a pattern."""
    reason = refusal_reason({"DATABASE_URL": TUNNELLED_PROD}, probe=marker_absent)
    assert "TRUNCATE" in reason
    assert "2026-08-17" in reason
    assert "2026-09-13" in reason, "the SECOND firing is the reason this mechanism changed"


def test_the_refusal_names_the_host_it_refused():
    """⚠ D-158 keeps `db_host` for exactly this: the reader must be told which target was refused.
    The parser stays, and so does its `@`-in-password test, because it still has a caller."""
    assert db_host(TUNNELLED_PROD) in refusal_reason(
        {"DATABASE_URL": TUNNELLED_PROD}, probe=marker_absent)


def test_the_refusal_does_NOT_hand_the_reader_a_paste_ready_override():
    """⚠⚠ The old refusal printed the override's exact value. A refusal that prints the bypass is a
    refusal that teaches the bypass. The FORM is explained; the working value is not assembled."""
    reason = refusal_reason({"DATABASE_URL": TUNNELLED_PROD}, probe=marker_absent)
    assert override_value_for(TUNNELLED_PROD) not in reason, (
        "the refusal contains a copy-pasteable override for the very database it just refused")


# ── the positive identity ───────────────────────────────────────────────────────────────────────

def test_a_database_carrying_the_marker_is_allowed():
    assert refusal_reason({"DATABASE_URL": DISPOSABLE}, probe=marker_present) is None


def test_the_marker_and_not_the_hostname_is_what_decides():
    """⚠⚠ The whole ruling in one assertion: **same loopback URL, opposite verdicts.** Under the
    old guard both of these returned `None`, because it never asked the database anything."""
    assert refusal_reason({"DATABASE_URL": TUNNELLED_PROD}, probe=marker_present) is None
    assert refusal_reason({"DATABASE_URL": TUNNELLED_PROD}, probe=marker_absent) is not None


def test_a_production_hostname_with_no_marker_is_still_refused():
    assert refusal_reason({"DATABASE_URL": NAMED_PROD}, probe=marker_absent) is not None


def test_no_database_url_at_all_is_the_ordinary_local_gate_and_never_probes():
    """⚠ The common case must not need an override or a database, or both become habitual."""
    def must_not_run(url):        # noqa: ARG001
        raise AssertionError("the probe ran with no DATABASE_URL set")
    assert refusal_reason({}, probe=must_not_run) is None


# ── fail closed ─────────────────────────────────────────────────────────────────────────────────

def test_a_probe_that_raises_REFUSES():
    """⚠ Cannot connect, cannot read, cannot decide ⇒ refuse. An undecidable target is not a
    target we can vouch for, and the old parser's own rule was the same."""
    reason = refusal_reason({"DATABASE_URL": TUNNELLED_PROD}, probe=probe_explodes)
    assert reason is not None
    assert "could not be established" in reason


def test_a_failed_probe_is_not_rescued_by_the_override():
    """⚠⚠ Fail-closed means closed. If the override could rescue an undecidable target, the
    override would be the way past every flaky connection — which is how it becomes habitual."""
    env = {"DATABASE_URL": TUNNELLED_PROD, OVERRIDE_ENV: override_value_for(TUNNELLED_PROD)}
    assert refusal_reason(env, probe=probe_explodes) is not None


def test_an_unparseable_url_is_refused():
    assert refusal_reason({"DATABASE_URL": "not a url at all"}, probe=marker_absent) is not None


# ── ⚠⚠ the CI bypass is GONE (B.6) ──────────────────────────────────────────────────────────────

def test_CI_true_no_longer_bypasses_anything():
    """⚠⚠ **B.6, and the most consequential assertion in this file.** The old guard returned `None`
    on `CI=true` before it looked at anything else. `CI=true` is set by a great many tools, so a
    developer shell carrying it plus a tunnel was 2026-09-13 with the new guard installed and
    asleep. CI now passes the REAL check — the workflow creates the marker on its service
    container — so the bypass buys nothing and costs the whole property."""
    assert refusal_reason(
        {"DATABASE_URL": TUNNELLED_PROD, "CI": "true"}, probe=marker_absent) is not None


def test_CI_with_the_marker_proceeds_exactly_like_anything_else():
    assert refusal_reason(
        {"DATABASE_URL": DISPOSABLE, "CI": "true"}, probe=marker_present) is None


def test_the_ci_workflow_creates_the_marker_between_migrations_and_pytest():
    """⚠ The bypass is only safe to delete if CI can satisfy the real check. Asserted over the
    workflow source, and ORDERED: the marker cannot precede the schema it lives in."""
    gate = (REPO / ".github" / "workflows" / "gate.yml").read_text(encoding="utf-8")
    # ⚠ Anchored on the RUN LINE, not on the marker's name. The name also appears in the comment
    # above the step, and a check that a comment satisfies is a check that a comment can satisfy.
    run = "run: python scripts/keel_mark_disposable.py"
    assert run in gate, "the postgres job never marks its service container disposable"
    upgrade = gate.index("alembic upgrade head")
    marker = gate.index(run)
    pytest_at = gate.index("pytest -m postgres")
    assert upgrade < marker < pytest_at, (
        "the marker must be created AFTER `alembic upgrade head` (it lives in the migrated "
        "schema) and BEFORE pytest (the guard speaks at pytest_configure)")


# ── ⚠ the override cannot be set once and forgotten (B.6) ───────────────────────────────────────

def test_the_override_must_name_the_exact_target_it_is_overriding():
    """⚠⚠ **The property the ruling had to hold: an override that cannot survive being set once
    and forgotten.** The old value was a constant sentence — paste it into `.env` and it authorises
    the truncation of every database you ever point at, for ever. This one is bound to the host and
    the database name, so it is not a blanket and it stops working the moment the target moves."""
    good = override_value_for(TUNNELLED_PROD)
    assert refusal_reason(
        {"DATABASE_URL": TUNNELLED_PROD, OVERRIDE_ENV: good}, probe=marker_absent) is None

    # ⚠ the same override, a different target — the case where it was set once and forgotten
    other = "postgresql+psycopg://fly-user:secret@127.0.0.1:16380/pharmfold_other"
    assert refusal_reason(
        {"DATABASE_URL": other, OVERRIDE_ENV: good}, probe=marker_absent) is not None, (
        "an override minted for one database authorised another — that is a blanket")


def test_the_old_blanket_override_value_no_longer_works():
    """⚠ The retired constant. If it still worked, every `.env` that already carries it would be
    armed, and the ruling would have changed nothing for the machines most at risk."""
    assert refusal_reason(
        {"DATABASE_URL": TUNNELLED_PROD, OVERRIDE_ENV: "i-know-this-truncates"},
        probe=marker_absent) is not None


def test_the_override_is_not_a_flag():
    for flick in ("1", "true", "yes", "TRUE"):
        assert refusal_reason(
            {"DATABASE_URL": TUNNELLED_PROD, OVERRIDE_ENV: flick},
            probe=marker_absent) is not None


# ── ⚠⚠ no migration may create the marker (B.2.1) ───────────────────────────────────────────────

def test_NO_migration_creates_the_marker():
    """⚠⚠ **LOAD-BEARING, and the condition the whole mechanism rests on.** If any revision creates
    the marker, then the first `alembic upgrade head` against production makes production look
    disposable and **the guard silently inverts** — it would permit precisely what it exists to
    refuse. Asserted over every revision file, by name."""
    versions = sorted((REPO / "db" / "migrations" / "versions").glob("*.py"))
    assert versions, "no migrations found — this guard would pass vacuously"
    offenders = [p.name for p in versions
                 if MARKER_TABLE in p.read_text(encoding="utf-8")]
    assert not offenders, (
        f"{offenders} reference {MARKER_TABLE!r}. A migration that creates the marker puts it in "
        f"PRODUCTION on the next `alembic upgrade head`, and the guard then permits the truncation "
        f"it exists to refuse. The marker is created by CI and by the local bootstrap, never by "
        f"the schema chain (A-031).")


def test_the_marker_is_created_by_a_bootstrap_that_is_not_a_migration():
    """⚠ Bar OR name: the marker has to come from somewhere, and that somewhere is named."""
    boot = REPO / "scripts" / "keel_mark_disposable.py"
    assert boot.is_file(), "no bootstrap creates the marker, so no developer can run the suite"
    text = boot.read_text(encoding="utf-8")
    # ⚠⚠ It must IMPORT the name, never restate it. Demanding a literal copy here would require a
    # second definition of the one constant the guard and the bootstrap must agree on — `F-046`'s
    # defect class, written into the test that is supposed to prevent it. The first draft of this
    # assertion did exactly that and went red against a correct implementation.
    assert "from _db_safety import" in text and "MARKER_TABLE" in text, (
        "the bootstrap does not take the marker name from the guard — a second copy of this "
        "constant is two paths to one quantity (F-046)")
    # ⚠⚠ Anchored on CODE, never on prose. The bootstrap's docstring explains `alembic upgrade
    # head` in order to say why the marker must not arrive that way, and a bare `"alembic" not in
    # text` reddens on the sentence that documents the rule. That is the same trap as the check
    # above and as D-145's, and it caught me twice in one file before it was written down here.
    assert "import alembic" not in text, "the bootstrap imports the migration runner"
    assert "down_revision" not in text and "revision =" not in text, (
        "the bootstrap carries alembic revision identifiers — it is a migration in disguise")
    assert boot.parent.name == "scripts", (
        "the bootstrap must not live in the migration chain's directory tree")
    versions = {p.resolve() for p in (REPO / "db" / "migrations" / "versions").glob("*.py")}
    assert boot.resolve() not in versions


# ── the guard is actually wired in, and EARLY (B.3.3) ───────────────────────────────────────────

def test_conftest_consults_the_guard_before_collection_imports_anything():
    """⚠⚠ **The hook moved to `pytest_configure`.** `pytest_collection_modifyitems` fires *after*
    every test module has been imported, so any module-level database work would run before the
    guard could speak. Nothing in this suite does that today — which is exactly when a class is
    cheap to close rather than expensive to discover."""
    src = (REPO / "tests" / "conftest.py").read_text(encoding="utf-8")
    assert "refusal_reason" in src, "conftest does not consult the guard"
    assert "def pytest_configure" in src, "the guard is not on the earliest hook available"
    assert "UsageError" in src, "the guard does not FAIL the run — a skip is what let this happen"
    # ⚠ `def ` anchors this on a HOOK REGISTRATION, not on the name appearing in prose. The
    # conftest docstring names the old hook in order to explain why it was abandoned, and a bare
    # substring check reddens on the sentence that records the fix — D-145's documented trap.
    assert "def pytest_collection_modifyitems" not in src, (
        "the late hook is still wired in; the guard must speak before modules are imported")


def test_the_probe_is_injectable_and_the_default_is_the_real_query():
    """⚠ A guard nobody can test is a guard nobody can trust — the property survives the rewrite,
    and it is the reason every assertion above can state a database without owning one."""
    import inspect

    import _db_safety
    sig = inspect.signature(_db_safety.refusal_reason)
    assert "probe" in sig.parameters, "the probe is not injectable"
    assert sig.parameters["probe"].default is None
    assert callable(_db_safety.marker_probe)
    src = inspect.getsource(_db_safety.marker_probe)
    assert MARKER_TABLE in src, "the default probe does not look for the marker"
    assert "connect_timeout" in src, (
        "the default probe sets no timeout — an unreachable host would hang collection rather "
        "than refuse quickly (B.3.1)")


def test_db_name_parses_the_target_out_of_the_url():
    assert db_name(TUNNELLED_PROD) == "pharmfoldmdk"
    assert db_name(DISPOSABLE) == "pharmfold_test"
    assert db_name("postgresql://u:p@h/db?sslmode=require") == "db"
    assert db_name("nonsense") == ""


def test_the_hostname_allowlist_is_gone_entirely():
    """⚠⚠ Not narrowed — GONE. A shorter list of trusted hostnames is the same defect with fewer
    entries, and `127.0.0.1` could not be removed from it: the disposable databases really are on
    loopback. The list had to stop being the thing that decides."""
    src = (REPO / "tests" / "_db_safety.py").read_text(encoding="utf-8")
    assert "DISPOSABLE_HOSTS" not in src, (
        "a hostname allowlist survived the rewrite — it is the mechanism that failed twice")


@pytest.mark.parametrize("url", [TUNNELLED_PROD, NAMED_PROD, DISPOSABLE])
def test_every_url_shape_is_decided_by_the_probe_and_never_by_its_host(url):
    """⚠ Parametrised over a tunnel, a named production host and a genuine test database: the
    verdict tracks the MARKER in all three, which is the property a hostname check cannot have."""
    assert refusal_reason({"DATABASE_URL": url}, probe=marker_present) is None
    assert refusal_reason({"DATABASE_URL": url}, probe=marker_absent) is not None


def test_the_docstring_does_not_name_an_unfixed_blind_spot():
    """⚠⚠ **D-074, applied to a SAFETY instrument for the first time — and this is the corollary
    the incident bought.** The old file named its own failure mode in its own docstring and the
    suite ran for 27 more days. A guard that names an unfixed hole in itself has generated a
    finding against itself, and that finding BLOCKS the work the guard protects.

    ⚠ The check is deliberately crude — it looks for the retired admission verbatim. A guard that
    tried to detect *any* confession in prose would be a guard nobody could reason about."""
    src = (REPO / "tests" / "_db_safety.py").read_text(encoding="utf-8")
    assert "necessary and not sufficient" not in src, (
        "the file still admits to a hole it has not closed")
    assert re.search(r"tunnel", src, re.I), (
        "the file should still explain the tunnel — the hazard is documented, just no longer live")
