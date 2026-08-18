"""KEEL V8-a — the test suite refuses to run against a database that is not disposable.

⚠⚠ **WHY THIS EXISTS.** On 2026-08-17 `tests/test_queue_postgres.py` was run with `.env` sourced.
Its `pg_engine` fixture opens **every test** with:

    TRUNCATE TABLE jobs, protein_analyses, ranking_runs RESTART IDENTITY CASCADE

It destroyed the production database — `protein_analyses` 2,771 → 1, `jobs` 2,771 → 1, sequences
reset. Recovered from a Fly backup **nobody had verified existed**.

⚠⚠ **THE EXISTING GUARD POINTED THE WRONG WAY.** `pg_engine` *skips unless* `DATABASE_URL` names a
reachable Postgres — so **supplying production credentials is precisely what ARMS the suite**. The
safety property was *"you probably do not have a database"*, which is not a safety property.

⚠ **This inverts it.** The suite runs only where the database is **disposable**: a loopback
address, a container hostname, or CI. Anything else is a **hard collection error, not a skip** — a
skip is exactly what let a destructive suite look harmless.

## ⚠ What this is deliberately NOT

**It is not a "does a backup exist?" check.** A backup makes **recovery** reliable; it does nothing
about **prevention**. Installing that here would file the incident as solved while the hole stayed
open. **Backup verification belongs to destructive operations** — migrations, DDL, bulk writes,
cluster changes — where the answer changes what you do. That is KEEL **V8-b**, and it is a separate
amendment on purpose.

## ⚠ The loopback caveat, stated rather than assumed

A tunnel to production **looks exactly like localhost**. `localhost:16380` is, right now, a proxy to
the live cluster. So this guard is **necessary and not sufficient**: it stops the obvious mistake
(production hostname in `DATABASE_URL`) and cannot stop the subtle one. The override is spelled
`i-know-this-truncates` so that reaching for it is a sentence someone has to mean.
"""

from __future__ import annotations

import os
import re

#: ⚠ Hosts whose data is expendable. See the loopback caveat above — a tunnel defeats this.
DISPOSABLE_HOSTS = ("localhost", "127.0.0.1", "::1", "postgres", "db")

#: ⚠ Not `1` or `true`. A flag someone can flick is a flag someone flicks by habit.
OVERRIDE_ENV = "PHARMFOLD_ALLOW_DESTRUCTIVE_DB"
OVERRIDE_VALUE = "i-know-this-truncates"


def db_host(url: str) -> str:
    """The host from a SQLAlchemy URL, lowercased. ⚠ Empty string when it cannot be parsed —
    treated as NOT disposable, because a URL we cannot read is not one we can vouch for.

    ⚠⚠ **GREEDY TO THE LAST `@`, and that is the whole correctness of this function.** The first
    version was `://[^@/]*@?([^/:?]+)`, which stops at the FIRST `@` — so a password containing
    `@` (`user:p@ss@prod.example.net`) parsed the host as `ss`. ⚠ **That misparse fails OPEN**: an
    unrecognised host is only refused because it is not in the disposable list, and `ss` is not
    either — but the reverse is easy to construct, and a guard whose parser can read a production
    host as something else is not a guard. Its own test caught this.

    ⚠ IPv6 hosts arrive bracketed (`[::1]`); the brackets are stripped so the literal matches.
    """
    # ⚠ The bracketed IPv6 branch is FIRST. Alternation is ordered, and the bare branch happily
    # matches a lone "[" and then stops at the colon inside "::1" — yielding "[", which strips to
    # nothing. An empty host reads as unparseable, so the guard would have refused a loopback run.
    m = re.search(r"://(?:.*@)?(\[[^\]]+\]|[^/:?@]+)", url or "")
    if not m:
        return ""
    return m.group(1).strip("[]").lower()


def refusal_reason(env: dict[str, str] | None = None) -> str | None:
    """`None` when the run may proceed, else the sentence explaining the refusal.

    ⚠ Pure and env-injectable, so the guard itself is testable without setting process-wide
    variables — a guard nobody can test is a guard nobody can trust.
    """
    env = os.environ if env is None else env
    url = env.get("DATABASE_URL", "")
    if not url:
        return None                                  # no database at all — the ordinary local gate
    if env.get("CI") == "true":
        return None                                  # the service container is the disposable one
    if env.get(OVERRIDE_ENV) == OVERRIDE_VALUE:
        return None
    host = db_host(url)
    if host in DISPOSABLE_HOSTS:
        return None
    return "\n".join([
        "",
        f"REFUSING TO RUN: DATABASE_URL points at host {host!r}, which is not a disposable database.",
        "  This suite TRUNCATEs jobs, protein_analyses and ranking_runs on every test that uses",
        "  the `pg_engine` fixture. On 2026-08-17 that destroyed production (2,771 rows -> 1).",
        "  Run the gate WITHOUT `.env` sourced, or point DATABASE_URL at a throwaway database.",
        f"  Override only if you mean it: {OVERRIDE_ENV}={OVERRIDE_VALUE}",
    ])
