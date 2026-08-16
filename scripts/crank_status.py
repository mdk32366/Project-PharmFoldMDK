#!/usr/bin/env python3
"""Read-only crank status: job states per tranche, as a COMPOSITION.

    python scripts/crank_status.py

⚠ **ORM only. No hand-written SQL touches production, by anyone, for any of this** — the owner's
standing rule, and the reason this file exists rather than an ad-hoc `text()` query typed at a
prompt. A one-off SELECT is exactly the thing that has no test, no review and no second reader.

⚠ **It prints a composition, never only a total.** `1,307` tells you nothing about whether the crank
is moving; `pending / claimed / complete / failed` per tranche does. **And every state is printed
even when it is zero** — an omitted `failed` row reads as *"no failures"* when it may equally mean
*"the key was never in the group-by."*

⚠ **Read-only, deliberately.** It opens a session, selects, and closes. Nothing here writes, so it
is safe to run against a live crank — which is the only time anyone wants it.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

#: ⚠ Printed even at zero. A state absent from the group-by is not a state at zero, and the two
#: must not look identical in the output.
STATES = ("pending", "claimed", "complete", "failed")


def main() -> int:
    import sqlalchemy as sa
    from sqlalchemy import func, select
    from sqlalchemy.orm import Session

    from db.models import JobRecord, ProteinAnalysis

    url = os.environ.get("DATABASE_URL")
    if not url:
        # ⚠ Stop and report. Guessing a connection string is how a read lands on the wrong database.
        print("⚠ no DATABASE_URL — stop and report", file=sys.stderr)
        return 1
    engine = sa.create_engine(url, connect_args={"connect_timeout": 10})

    with Session(engine) as s:
        rows = s.execute(
            select(ProteinAnalysis.cohort_tranche, JobRecord.status, func.count())
            .join(ProteinAnalysis, JobRecord.analysis_id == ProteinAnalysis.id)
            .group_by(ProteinAnalysis.cohort_tranche, JobRecord.status)
        ).all()

    by_tranche: dict[object, dict[str, int]] = {}
    for tranche, status, n in rows:
        by_tranche.setdefault(tranche, {})[status] = n

    # ⚠ `None` sorts last and is labelled, not silently dropped: an untranched job is a finding.
    for tranche in sorted(by_tranche, key=lambda t: (t is None, t)):
        counts = by_tranche[tranche]
        total = sum(counts.values())
        parts = " ".join(f"{st}={counts.get(st, 0):>5}" for st in STATES)
        # ⚠ A status the code has never heard of is surfaced, not swallowed by the fixed list.
        extra = {k: v for k, v in counts.items() if k not in STATES}
        label = "(no tranche)" if tranche is None else f"tranche-{tranche}"
        print(f"{label:>14} | {parts} | total={total}"
              + (f" | ⚠ UNRECOGNISED STATES {extra}" if extra else ""))

    grand = sum(sum(c.values()) for c in by_tranche.values())
    print(f"{'ALL':>14} | jobs={grand} across {len(by_tranche)} tranche key(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
