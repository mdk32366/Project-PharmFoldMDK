"""D-167 amendment 1 §2 — which database ROLE a Phase D script is, asked before anything it writes.

⚠⚠ **WHY THIS EXISTS.** Phase B's read connected through a URL naming `pharmfoldmdk-app` and Postgres
answered `current_user = schema_admin` (`data/control/d167/state_before.json`). Two paths to one
quantity disagreed, and why is **unestablished** (`ORDERS` A3.2). So every Phase D script prints the
role it actually holds — `session_user`, `current_user`, the `role` setting, the session role's
`rolconfig` — before its identity check and before its first write.

⚠⚠ **AND WHETHER IT CAN BUILD `0014` (A4.2, Planner error 3 corrected).** `CREATE INDEX` requires
**ownership** of the table, or membership in the owning role — not a `CREATE` grant. So the preamble
reads the owner of `jobs` and asks `pg_has_role(current_user, <owner>, 'USAGE')`. The answer is had
before the sitting's first write, not discovered when `alembic` refuses after an irreversible delete.

⚠ Reads only. No DDL, no DML, no transaction of its own.
"""

from __future__ import annotations

from typing import Any

KEYS = ("session_user", "current_user", "role", "rolconfig", "rolsuper", "jobs_owner",
        "can_build_jobs_index")

_PREAMBLE_SQL = """
    SELECT session_user                  AS su,
           current_user                  AS cu,
           current_setting('role')       AS role,
           (SELECT rolconfig FROM pg_roles WHERE rolname = session_user) AS rolconfig,
           (SELECT rolsuper  FROM pg_roles WHERE rolname = current_user) AS rolsuper,
           (SELECT tableowner FROM pg_tables
             WHERE schemaname = current_schema() AND tablename = 'jobs') AS jobs_owner
"""


def role_preamble(conn) -> dict[str, Any]:
    """Read the effective role and whether it can build an index on `jobs`."""
    from sqlalchemy import text                                   # noqa: PLC0415

    row = conn.execute(text(_PREAMBLE_SQL)).mappings().one()
    owner = row["jobs_owner"]
    can_build = False
    if owner:
        can_build = bool(conn.execute(
            text("SELECT pg_has_role(current_user, CAST(:o AS name), 'USAGE')"), {"o": owner}).scalar())
    return {
        "session_user": row["su"],
        "current_user": row["cu"],
        "role": row["role"],
        "rolconfig": list(row["rolconfig"]) if row["rolconfig"] is not None else None,
        "rolsuper": row["rolsuper"],
        "jobs_owner": owner,
        "can_build_jobs_index": can_build,
    }


def format_preamble(pre: dict[str, Any]) -> list[str]:
    return ["ROLE PREAMBLE (D-167 amendment 1 §2, read-only)",
            *[f"  {k:22s}: {pre.get(k)!r}" for k in KEYS]]


def index_build_refusal(pre: dict[str, Any]) -> str | None:
    """None when the effective role can build `0014`'s index; otherwise the refusal, naming the owner.

    ⚠ The collapse WAITS on this (its delete exists only to let the index build); the re-attach
    reports it and proceeds (A4.2)."""
    if pre.get("can_build_jobs_index"):
        return None
    return (f"REFUSING: role {pre.get('current_user')!r} cannot build 0014's index on jobs - jobs is "
            f"owned by {pre.get('jobs_owner')!r}, and CREATE INDEX requires ownership (or membership "
            f"in the owning role). The collapse WAITS with 0014 (D-167 amendment 1 §2). Report the "
            f"owner of jobs and stop the sitting here.")
