#!/usr/bin/env python3
"""The census §0 confirmations. ⚠ READ-ONLY, and it is the ORM's models, not hand-written SQL.

    python scripts/census_preflight.py

⚠ **`alembic_version` AND the `cohort_tranche` column are read SEPARATELY, by two different
mechanisms, and then compared.** A migration is *recorded* in `alembic_version` and *applied* to the
schema; those are two facts and one of them can be true without the other. Reading the version and
inferring the column — or reading the column and inferring the version — asks one question and
reports two answers. **Disagreement is stop-and-report.**

⚠ **Every value is printed literally.** Never "as expected", never a tick. The comparison against
the expected value is printed beside the measured one so a reader can disagree with the expectation
rather than only with the verdict.

⚠ **NO WRITES. NO DDL. NO SCORING.** This opens a connection, reads, and closes.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

EXPECTED = {
    "protein_analyses": 80,
    "ranking_runs": 5,
    "ranking_results": 5,
    "target_scores": 224,
    "census_rows": 0,
}


def main() -> int:
    import sqlalchemy as sa
    from sqlalchemy import func, inspect, select
    from sqlalchemy.orm import Session

    from db.models import ProteinAnalysis, RankingResult, RankingRun, TargetScore

    url = os.environ.get("DATABASE_URL")
    if not url:
        print("[preflight] ⚠ no DATABASE_URL in the environment — STOP")
        return 1

    engine = sa.create_engine(url, connect_args={"connect_timeout": 10})
    failures: list[str] = []

    with engine.connect() as conn:
        # ── FACT 1: what the migration ledger SAYS ────────────────────────────
        version = conn.execute(sa.text("SELECT version_num FROM alembic_version")).scalar()
        print(f"alembic_version | {version!r}")

        # ── FACT 2: what the SCHEMA actually HAS. ⚠ A different mechanism, on purpose:
        # the inspector reads catalog metadata rather than the ledger, so the two can disagree.
        insp = inspect(conn)
        cols = {c["name"]: c for c in insp.get_columns("protein_analyses")}
        has_tranche = "cohort_tranche" in cols
        print(f"protein_analyses.cohort_tranche present | {has_tranche}")
        if has_tranche:
            c = cols["cohort_tranche"]
            print(f"cohort_tranche type | {c['type']!s} | nullable | {c['nullable']}")

        # ⚠ THE COMPARISON, MADE EXPLICIT. 0008 is the migration that adds the column.
        ledger_says_0008 = bool(version and version.startswith("0008"))
        print(f"⚠ ledger says 0008 applied | {ledger_says_0008} | schema has the column | "
              f"{has_tranche} | AGREE | {ledger_says_0008 == has_tranche}")
        if ledger_says_0008 != has_tranche:
            failures.append(
                f"alembic_version {version!r} and the presence of protein_analyses.cohort_tranche "
                f"({has_tranche}) disagree — a migration recorded but not applied, or applied but "
                f"not recorded")

    with Session(engine) as s:
        n_analyses = s.scalar(select(func.count()).select_from(ProteinAnalysis))
        print(f"protein_analyses rows | {n_analyses} | expected | {EXPECTED['protein_analyses']}")
        if n_analyses != EXPECTED["protein_analyses"]:
            failures.append(f"protein_analyses is {n_analyses}, expected {EXPECTED['protein_analyses']}")

        # ⚠ Tranche read as a COMPOSITION, never as "all zero". A null and a zero are different
        # facts and the difference is the whole point of the column.
        by_tranche = dict(s.execute(
            select(ProteinAnalysis.cohort_tranche, func.count())
            .group_by(ProteinAnalysis.cohort_tranche)).all())
        print(f"protein_analyses by cohort_tranche | {by_tranche}")
        n_null = by_tranche.get(None, 0)
        n_zero = by_tranche.get(0, 0)
        print(f"tranche null | {n_null} | tranche zero | {n_zero}")
        if n_null:
            failures.append(f"{n_null} protein_analyses rows have a NULL cohort_tranche")
        if n_zero != n_analyses:
            failures.append(f"cohort_tranche zero is {n_zero} but protein_analyses is {n_analyses}")

        n_runs = s.scalar(select(func.count()).select_from(RankingRun))
        max_run = s.scalar(select(func.max(RankingRun.id)))
        print(f"ranking_runs | count {n_runs} | max id {max_run} | expected (5,5)")
        if (n_runs, max_run) != (EXPECTED["ranking_runs"], EXPECTED["ranking_runs"]):
            failures.append(f"ranking_runs is ({n_runs},{max_run}), expected (5,5)")

        n_results = s.scalar(select(func.count()).select_from(RankingResult))
        print(f"ranking_results | {n_results} | expected | {EXPECTED['ranking_results']}")
        if n_results != EXPECTED["ranking_results"]:
            failures.append(f"ranking_results is {n_results}, expected {EXPECTED['ranking_results']}")

        n_scores = s.scalar(select(func.count()).select_from(TargetScore))
        print(f"target_scores | {n_scores} | expected | {EXPECTED['target_scores']}")
        if n_scores != EXPECTED["target_scores"]:
            failures.append(f"target_scores is {n_scores}, expected {EXPECTED['target_scores']}")

        # ── census rows: ⚠ counted as "not tranche zero", NOT as "tranche 1". A census row that
        # arrived with a wrong or absent tranche tag would be invisible to a `== 1` test.
        n_non_zero = s.scalar(
            select(func.count()).select_from(ProteinAnalysis)
            .where(ProteinAnalysis.cohort_tranche.is_distinct_from(0)))
        print(f"census rows (cohort_tranche IS DISTINCT FROM 0) | {n_non_zero} | expected | 0")
        if n_non_zero != EXPECTED["census_rows"]:
            failures.append(f"{n_non_zero} rows are not tranche zero — census rows are present")

    print()
    if failures:
        print(f"⚠ STOP AND REPORT — {len(failures)} disagreement(s):")
        for f in failures:
            print(f"  · {f}")
        return 1
    print("§0 CONFIRMATIONS | all measured values match the expected values above")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
