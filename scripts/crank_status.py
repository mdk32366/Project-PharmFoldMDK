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

⚠⚠ **And tranche 0 reconciles against the ROSTER, not against itself.** The first version of this
file printed `tranche-0 … total=80` and stopped. **The cohort is 82.** The two absent rows —
`MUC16` and `FAT2`, the D-022 named oversize exclusions — have no `protein_analyses` row and never
had one, **so a query over that table cannot see them and reported a low number instead of a
category.** That is the exact failure the project bans: *an absent value is a CATEGORY, never a low
number and never a bare null.* The reconciliation below is therefore not decoration — **it is the
only part of this file that can see something the database has no row for.**
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

    _reconcile_cohort(by_tranche.get(0, {}))
    return 0


def _reconcile_cohort(counts: dict[str, int]) -> None:
    """⚠ Tranche 0 against the roster of 82 — the only check here that sees a MISSING ROW.

    Every other number in this file is a count of rows that exist. **`MUC16` and `FAT2` have no
    `protein_analyses` row at all**, so they are invisible to the queries above by construction,
    and `total=80` would read as *"80 targets"* rather than *"82 minus two named exclusions."*
    """
    # ⚠ Derived from source, never a hand-kept list (F-027): the exclusions come out of the module
    # that rules them, so a change there cannot leave this reconciliation quietly stale.
    from core.manifest import EXCLUSIONS, NAMED_EXCLUSIONS

    roster_path = REPO / "data" / "cohort_82_accessions.txt"
    if not roster_path.is_file():
        # ⚠ A category, not a silent skip. "The roster was unreadable" and "the roster agreed"
        # must not produce the same output.
        print(f"{'COHORT':>14} | ⚠ ROSTER_UNREADABLE — {roster_path.name} absent; "
              f"tranche 0 is UNRECONCILED, not reconciled")
        return

    # ⚠ The file is `ACCESSION  SYMBOL` with `#` comments. Parsed by token, not by line: a
    # whole-line comparison against accessions matches nothing and reads as total divergence.
    roster = [l.split()[0] for l in roster_path.read_text().splitlines()
              if l.strip() and not l.lstrip().startswith("#")]

    excluded = sorted(a for a in roster if a in NAMED_EXCLUSIONS)
    expected = len(roster) - len(excluded)
    seen = sum(counts.values())

    print(f"{'COHORT':>14} | roster={len(roster)} − named_exclusions={len(excluded)} "
          f"→ expected_jobs={expected} | observed={seen} "
          f"| {'✅ reconciles' if seen == expected else '⚠⚠ DOES NOT RECONCILE'}")
    for a in excluded:
        # ⚠ "NOT_FOLDED" was wrong and is corrected (D-085): both of these are IN the census
        # manifest at tranche 5, tier=rental — SCHEDULED TO FOLD, not unfoldable. The label
        # asserted an impossibility the data contradicts.
        e = EXCLUSIONS[a]
        print(f"{'':>14} | ⚠ NOT IN COHORT TRANCHE 0 (no row exists) {a} — {e.reason}")
        print(f"{'':>14} |    foldable? {e.foldable}")
    if seen != expected:
        # ⚠ Stated, never reconciled away by adjusting the denominator to match.
        print(f"{'':>14} | ⚠⚠ {abs(expected - seen)} row(s) unaccounted for — STOP AND REPORT. "
              f"Do NOT adjust the expected count to agree.")


if __name__ == "__main__":
    raise SystemExit(main())
