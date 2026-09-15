"""D-166 — the interim serialization point for enqueue paths, while the identity is undesigned.

⚠⚠ **This is NOT a constraint and must not be read as one.** It is a **process-level** lock: it
serializes enqueues **that take it**, and does **nothing whatsoever** about an enqueue that does
not. A new enqueue path written by someone who has not read `D-166` will simply not call it — and
that is the *same shape* as the check-then-write it mitigates, one layer up.

⚠ The durable fix is a database constraint. `0014_enqueue_identity_unique` supplies it for the tile
identity, which lives on one table. The **Run-2 identity spans two**
(`protein_analyses.input_value` and `jobs.inference_settings->>'run'`) and no single-table index
expresses it; `D-166` §4b records that as owed and undesigned. **This module is what stands in the
gap until then, and the gap is the point.**

⚠ **Why an advisory lock and not `SELECT … FOR UPDATE`:** the rows being guarded against **do not
exist yet**. There is nothing to lock. A transaction-scoped advisory lock takes a lock on a *name*
rather than on a row, which is the only thing available when the conflict is between two inserts.

⚠⚠ **Transaction-scoped, never session-scoped.** `pg_advisory_xact_lock` is released by COMMIT or
ROLLBACK and cannot be leaked by a process that dies holding it. `pg_advisory_lock` can, and a
leaked enqueue lock would wedge every future enqueue until someone found it.
"""

from __future__ import annotations

import hashlib

from sqlalchemy import text
from sqlalchemy.orm import Session

# ⚠ The namespace is part of the key so two different enqueue families cannot collide into one
# lock and serialize against each other for no reason.
TILE_NAMESPACE = "pharmfold.enqueue.hold48_tiles"
RUN2_NAMESPACE = "pharmfold.enqueue.run2_band"


def lock_key(namespace: str) -> int:
    """A stable signed 64-bit key from a name.

    ⚠ Derived from the name rather than hand-assigned: a hand-assigned integer is a second copy of
    a constant, which is `F-014`'s class in the value that decides mutual exclusion.
    """
    digest = hashlib.sha256(namespace.encode("utf-8")).digest()
    unsigned = int.from_bytes(digest[:8], "big")
    return unsigned - (1 << 64) if unsigned >= (1 << 63) else unsigned


def hold_enqueue_lock(session: Session, namespace: str) -> bool:
    """Take the transaction-scoped enqueue lock. Returns whether it was actually taken.

    ⚠⚠ **Returns `False` on a non-Postgres engine rather than raising or pretending.** SQLite has
    no advisory locks and the test substrate must not report a protection it does not have —
    that is `F-056`'s class, and this project has already shipped it once.

    ⚠ Blocks until the lock is available. It does **not** time out, and it does **not** fall back
    to proceeding unlocked: a lock that gives up under contention protects exactly the case it was
    written for least.
    """
    if session.get_bind().dialect.name != "postgresql":
        return False
    session.execute(text("SELECT pg_advisory_xact_lock(:k)"), {"k": lock_key(namespace)})
    return True
