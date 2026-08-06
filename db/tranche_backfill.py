"""The tranche-zero backfill, as one function so the migration and the test run the SAME code.

⚠ WHY IT TAKES A *BIND* AND NOT AN ENGINE, AND WHY THAT DISTINCTION DEADLOCKED PRODUCTION.

The first version took an `engine` and did `with Session(engine)`. Migration `0008` called it as
`backfill_tranche_zero(op.get_bind().engine)` — `.engine` discards the migration's Connection and
hands over the Engine, so the Session checked out a **second** connection from the pool.

By then `op.add_column` had already taken `ACCESS EXCLUSIVE` on `protein_analyses` inside the
migration's still-open transaction. The backfill's second connection then waited on a lock **its own
caller held**. It hung forever with **zero other clients** — scaling the app to 0 and restarting the
tunnel changed nothing, because nothing external was ever holding it.

⚠ AND THE TEST COULD NOT HAVE CAUGHT IT. `create_engine("sqlite://")` uses `SingletonThreadPool`, so
the "second connection" was the same connection, and there was no outer DDL transaction anyway. Two
paths to one behaviour, never compared under the condition that matters. The gate was green on code
that could not run.

**The rule this encodes: a helper shared by a migration and a test takes the caller's BIND, never a
factory it can open a new connection from.** A function that can create its own connection will, and
the one context where that is fatal is the one the tests do not reproduce.
"""

from __future__ import annotations

from typing import Any

TRANCHE_ZERO = 0


def backfill_tranche_zero(bind: Any) -> int:
    """Tag every currently-untagged `protein_analyses` row as tranche zero. Returns the row count.

    `bind` is a **Connection** (the migration passes `op.get_bind()`) or an **Engine** (tests).

    - Given a **Connection**, the UPDATE runs in the caller's transaction and **this function does
      not commit** — the migration owns that transaction and commits it. Committing here would end
      the migration's transaction early, mid-DDL.
    - Given an **Engine**, it opens its own short transaction via `begin()` and commits on exit.

    ⚠ Idempotent by construction: it touches only rows where `cohort_tranche IS NULL`, so a second
    run writes nothing and an existing census tranche is never dragged back into the cohort.
    """
    from sqlalchemy import update
    from sqlalchemy.engine import Connection

    from db.models import ProteinAnalysis

    stmt = (
        update(ProteinAnalysis)
        .where(ProteinAnalysis.cohort_tranche.is_(None))
        .values(cohort_tranche=TRANCHE_ZERO)
    )

    if isinstance(bind, Connection):
        # The caller's transaction. No commit — the migration owns it.
        return int(bind.execute(stmt).rowcount or 0)

    with bind.begin() as conn:
        return int(conn.execute(stmt).rowcount or 0)
