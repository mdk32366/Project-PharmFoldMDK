"""dev-up.ps1 helper: verify the DB is actually reachable — not just the port.

A live port is not a live connection (the MPG tunnel drops silently, and a dropped tunnel made
an enqueue write nothing the first-fold night). This runs a real query against DATABASE_URL and
prints the job-status counter. Exit 0 on success, 1 on any failure, so the rig fails loudly on a
dead connection / wrong password / wrong scheme instead of proceeding.
"""

from __future__ import annotations

import collections
import os
import sys


def main() -> int:
    import sqlalchemy as sa

    url = os.environ.get("DATABASE_URL")
    if not url:
        print("[db] no DATABASE_URL in the environment")
        return 1
    try:
        # connect_timeout bounds a half-dead tunnel so the rig fails fast instead of hanging.
        engine = sa.create_engine(url, connect_args={"connect_timeout": 10})
        with engine.connect() as conn:
            n = conn.execute(sa.text("SELECT count(*) FROM jobs")).scalar()
            counts = collections.Counter(
                row[0] for row in conn.execute(sa.text("SELECT status FROM jobs")).fetchall()
            )
    except Exception as e:  # noqa: BLE001 — any failure means "not a live connection"
        print(f"[db] FAILED: {e}")
        return 1
    print(f"[db] OK - {n} jobs: {dict(counts)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
