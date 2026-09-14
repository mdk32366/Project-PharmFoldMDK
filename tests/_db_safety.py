"""KEEL V8-a / **D-158** — the suite runs only where the DATABASE proves it is disposable.

⚠⚠ **WHY THIS EXISTS, AND WHY IT WAS REWRITTEN.** `tests/conftest.py`'s `pg_engine` fixture opens
**every test** with:

    TRUNCATE TABLE jobs, protein_analyses, ranking_runs RESTART IDENTITY CASCADE

That is correct for test isolation. It carries one assumption: that `DATABASE_URL` names a database
whose data is expendable. **The assumption has been wrong twice.**

- **2026-08-17** — `protein_analyses` 2,771 → 1. Recovered from a Fly backup nobody had verified.
- **2026-09-13** — 4,535 → 1, across 19 tests and 2,887.94 s, uninterrupted. Recovered from an
  hourly backup taken 73 minutes before.

⚠⚠ **THE FIRST FIX POINTED AT THE URL, AND THE URL IS THE ONE THING A TUNNEL CONTROLS.** The guard
written after 2026-08-17 compared the host in `DATABASE_URL` against an allowlist of expendable
hostnames. `fly mpg proxy` puts production on `127.0.0.1:16380`, and loopback was on that list —
**it had to be, because the genuinely disposable databases are on loopback too.** The mechanism
could not be narrowed into correctness. It had to stop being the thing that decides.

## ⚠ What decides now: a marker the DATABASE carries

The target must hold `keel_disposable_marker`. A tunnel **faithfully reports the contents of
whatever it is pointed at** — that is precisely why it defeated a hostname check and precisely why
it cannot defeat this one. The verdict is a property of the database, not of the URL, the shell, or
the environment.

⚠⚠ **The marker is created by CI and by `scripts/keel_mark_disposable.py`. It is created by NO
MIGRATION, and a test asserts that over every revision file.** If a migration created it, the first
`alembic upgrade head` against production would make production look disposable and **the guard
would silently invert** — permitting exactly what it exists to refuse. That condition is load-bearing
and is registered as `A-031`.

## ⚠ What this is deliberately NOT

**It is not a "does a backup exist?" check.** A backup makes *recovery* reliable and does nothing
about *prevention*. Installing it here would file the incident as solved while the hole stayed open.
Backup verification belongs to destructive operations — migrations, DDL, bulk writes, cluster
changes — where the answer changes what you do. That is KEEL **V8-b**, still a separate amendment.

## ⚠ Two allowances that used to exist and do not any more (D-158)

- **`CI=true` returned "permitted" before anything else was examined.** `CI` is set by a great many
  tools, so a developer shell that happened to carry it, plus a tunnel, was this same incident with
  the new guard installed and asleep. CI now satisfies the real check: the workflow creates the
  marker on its service container between `alembic upgrade head` and pytest.
- **The override was a constant sentence.** Pasted into an `.env` once, it authorised the truncation
  of every database that file would ever name, for ever. It is now **bound to the host and the
  database it authorises**, so it cannot be a blanket and it stops working the moment the target
  moves. ⚠ The refusal explains the *form* and never assembles a working value — a refusal that
  prints the bypass is a refusal that teaches the bypass.
"""

from __future__ import annotations

import os
import re
from typing import Callable

#: ⚠ The marker. Created by CI and by the local bootstrap; created by no migration (`A-031`).
MARKER_TABLE = "keel_disposable_marker"

#: ⚠ Seconds. An unreachable target must refuse QUICKLY rather than hang collection — the guard now
#: does I/O, and a guard that hangs is one people learn to skip.
PROBE_TIMEOUT_S = 5

OVERRIDE_ENV = "PHARMFOLD_ALLOW_DESTRUCTIVE_DB"
#: ⚠ Not a flag. `1`/`true` are what people set by habit; and not a bare sentence either, because a
#: bare sentence is a blanket. The value must NAME its target — see `override_value_for`.
OVERRIDE_PREFIX = "i-know-this-truncates"


def db_host(url: str) -> str:
    """The host from a SQLAlchemy URL, lowercased. Empty string when it cannot be parsed.

    ⚠ **KEPT DELIBERATELY, AND NOT AS A DECISION INPUT.** The host no longer decides anything; it is
    carried so the refusal can name the target it refused, which is a real caller and the reason
    this function's `@`-in-password test is still meaningful (D-158 §B.7).

    ⚠⚠ **GREEDY TO THE LAST `@`, and that is the whole correctness of this function.** The first
    version stopped at the FIRST `@`, so a password containing `@` (`user:p@ss@prod.example.net`)
    parsed the host as `ss`. Its own test caught it.

    ⚠ IPv6 hosts arrive bracketed (`[::1]`); the brackets are stripped so the literal matches. The
    bracketed branch is FIRST because alternation is ordered.
    """
    m = re.search(r"://(?:.*@)?(\[[^\]]+\]|[^/:?@]+)", url or "")
    if not m:
        return ""
    return m.group(1).strip("[]").lower()


def db_name(url: str) -> str:
    """The database name from a SQLAlchemy URL, or `""` when it cannot be read.

    ⚠ Used to bind an override to its target. An unparseable URL yields `""`, which can never equal
    a real database name, so a malformed URL cannot be overridden into permission.
    """
    m = re.search(r"://[^/]*/([^/?#]+)", url or "")
    return m.group(1) if m else ""


def override_value_for(url: str) -> str:
    """The only override value that authorises THIS target.

    ⚠⚠ The property the ruling had to hold is that an override **cannot survive being set once and
    forgotten**. Binding it to host and database delivers that: a value pasted into `.env` stops
    working the moment the target changes, and it authorises nothing else in the meantime.
    """
    return f"{OVERRIDE_PREFIX}:{db_host(url)}/{db_name(url)}"


def marker_probe(url: str) -> bool:
    """`True` when the target carries `keel_disposable_marker`. Raises when it cannot be asked.

    ⚠ The default probe, and the only place this module touches a network. Injectable, so every
    assertion about the guard can state a database without owning one — *a guard nobody can test is
    a guard nobody can trust* is load-bearing and survives the rewrite.

    ⚠ `connect_timeout` is set explicitly: an unreachable host must fail fast enough that the
    refusal is read rather than waited out.
    """
    from sqlalchemy import create_engine, text          # noqa: PLC0415

    from db.dburl import normalize_db_url               # noqa: PLC0415

    engine = create_engine(
        normalize_db_url(url), future=True,
        connect_args={"connect_timeout": PROBE_TIMEOUT_S},
    )
    try:
        with engine.connect() as conn:
            found = conn.execute(
                text("SELECT to_regclass(:marker)"), {"marker": MARKER_TABLE}
            ).scalar()
            return found is not None
    finally:
        engine.dispose()


def refusal_reason(
    env: dict[str, str] | None = None,
    probe: Callable[[str], bool] | None = None,
) -> str | None:
    """`None` when the run may proceed, else the sentence explaining the refusal.

    ⚠ Pure but for the probe, and the probe is injected. The order of the gates is itself the
    ruling: **the identity check is asked FIRST**, and the override is consulted only after the
    database has failed to prove itself. An override in front of the check is not a check.
    """
    env = os.environ if env is None else env
    probe = marker_probe if probe is None else probe

    url = env.get("DATABASE_URL", "")
    if not url:
        # ⚠ The ordinary local gate: no database named, nothing to truncate, nothing to probe.
        return None

    try:
        disposable = probe(url)
    except Exception as exc:                              # noqa: BLE001
        # ⚠⚠ FAIL CLOSED, and not rescuable by the override. If an undecidable target could be
        # overridden, the override would become the way past every flaky connection — which is
        # exactly how it stops being a deliberate act.
        return _refusal(
            url,
            f"its disposability could not be established: the marker probe raised {exc!r}.",
        )

    if disposable:
        return None

    if env.get(OVERRIDE_ENV) == override_value_for(url):
        return None

    return _refusal(
        url,
        f"it does not carry the {MARKER_TABLE!r} marker, so it is not a disposable database.",
    )


def _refusal(url: str, why: str) -> str:
    host = db_host(url) or "<unparseable>"
    name = db_name(url) or "<unparseable>"
    return "\n".join([
        "",
        f"REFUSING TO RUN: DATABASE_URL points at {name!r} on host {host!r}, and {why}",
        "  This suite TRUNCATEs jobs, protein_analyses and ranking_runs on every test that uses",
        "  the `pg_engine` fixture. It has destroyed production TWICE, on the same signature:",
        "    2026-08-17  protein_analyses 2,771 -> 1",
        "    2026-09-13  protein_analyses 4,535 -> 1   (a tunnel makes production look local)",
        "  A tunnel presents production at 127.0.0.1, so the ADDRESS proves nothing and is no",
        "  longer consulted. Only the database itself can answer, and this one did not.",
        "",
        "  Run the gate WITHOUT `.env` sourced, or point DATABASE_URL at a throwaway database",
        f"  marked with `python scripts/keel_mark_disposable.py`.",
        f"  Override only if you mean it, and only for one named target:",
        f"    {OVERRIDE_ENV}={OVERRIDE_PREFIX}:<host>/<database>",
    ])
