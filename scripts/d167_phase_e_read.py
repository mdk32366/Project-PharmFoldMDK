#!/usr/bin/env python3
"""D-167 Phase E -- the one read-only read after the sitting (ORDERS Amendment 8, A8.3). READ-ONLY.

    python scripts/d167_phase_e_read.py --url <tunnel url>        # the owner runs it

⚠⚠ **WHY THIS EXISTS.** Phase D's collapse deleted jobs 3693, 3695 and 3696, and A8.2 (Planner error 7)
found that at least one of them sat INSIDE the census key the close-out had called "untouched: 3,651"
(`run = '1' AND complete`): `data/control/f078/f078_scope.json` measures job 3696 there with
`run "1"`. So the census is read again, and its reading is classified against a table registered
BEFORE the read, every outcome at equal prominence:

    3,648           all three dropped rows were in the key            expected; recorded
    3,649 / 3,650   one or two unsampled drops carried no run '1'     named category; not a stop
    3,651           no drop in the key -- contradicts 3696's run '1'  finding; STOP
    anything else   rows outside the collapse changed                 finding; STOP

It also reads, as measurements rather than implications:
1. `DUPLICATES_SQL` (the collapse script's own words): expect no row.
3. the census identity-keyed -- distinct (accession, tile_start, tile_end), NULL tile for whole-protein
   rows -- expected to equal the row-keyed reading now that no duplicate remains. ⚠ A diagnostic lists
   every identity holding more than one row, so a mismatch names its rows instead of only its size.
4. every complete run-1 row holds a `pdb_path`; F-078's five non-complete run-1 rows (2 failed --
   P11717, P55073 -- and 3 pending) remain as they were.
5. keep rows 3673/3674/3675 complete with a `pdb_path`; 6. `alembic_version` = `0014`;
7. drop rows 3693/3695/3696 absent from `jobs` and `protein_analyses` (analysis id == job id for these
   three, `data/control/d167/phase_d/06-collapse-dry.txt`).

⚠⚠ **READ-ONLY BY THE DATABASE.** Every read runs inside `d167_read_state.read_only_transaction`
(`SET TRANSACTION READ ONLY` first). **Role first** (`core.db_role`, A3.2), **identity second**
(`D-159`), then the reads. Output is written ONCE to `data/control/d167/phase_e_read.json` and its
sha256 printed. Exit 0 when nothing stops; 2 when anything does. It does not interpret a stop.

⚠ Printed output is ASCII (A7.4). Run it after the step-0 environment fix and probe (A7.3) anyway.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import pathlib
import sys
from typing import Any, Optional

from sqlalchemy import create_engine, text

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from core.db_identity import assert_campaign_target                      # noqa: E402
from core.db_role import format_preamble, role_preamble                  # noqa: E402
from db.dburl import normalize_db_url                                    # noqa: E402
from scripts.d166_collapse_duplicate_tiles import DUPLICATES_SQL         # noqa: E402
from scripts.d167_read_state import _git, read_only_transaction, write_state  # noqa: E402

OUT = REPO / "data" / "control" / "d167" / "phase_e_read.json"

#: F-078 section 4: the run-1 census, complete and holding its artifact, measured 2026-09-15.
BASELINE_CENSUS = 3651
#: `06-collapse-dry.txt` / `07-collapse-owner.txt`: the rows kept and the rows deleted.
KEEP_JOBS = (3673, 3674, 3675)
DROP_JOBS = (3693, 3695, 3696)
#: `f078_scope.json`: the only dropped row the F-078 sweep sampled, measured `run "1"`, complete.
DROPS_MEASURED_IN_KEY = (3696,)
#: F-078 section 4: "5 absent are exactly the 5 rows the database does not call complete".
NONCOMPLETE_BY_STATUS = {"failed": 2, "pending": 3}
FAILED_ACCESSIONS = ("P11717", "P55073")
EXPECTED_ALEMBIC = "0014_enqueue_identity_unique"


def classify_census(n: int, baseline: Optional[int] = None) -> dict[str, Any]:
    """Classify the row-keyed census reading against the table A8.3 registered before the read. Pure."""
    b = BASELINE_CENSUS if baseline is None else baseline
    unsampled = [j for j in DROP_JOBS if j not in DROPS_MEASURED_IN_KEY]
    expected = b - len(DROP_JOBS)
    base = {"reading": n, "baseline": b, "expected": expected, "drops_outside_key": 0, "candidates": []}
    if n == expected:
        return {**base, "verdict": "expected", "stop": False,
                "meaning": f"all {len(DROP_JOBS)} dropped rows were in the key "
                           f"({DROPS_MEASURED_IN_KEY} measured, {unsampled} inferred)"}
    if expected < n <= expected + len(unsampled):
        k = n - expected
        return {**base, "verdict": "named_category", "stop": False, "drops_outside_key": k,
                "candidates": unsampled,
                "meaning": f"{k} of the unsampled dropped rows {unsampled} carried no run '1'"}
    if n == b:
        return {**base, "verdict": "finding", "stop": True,
                "meaning": f"no dropped row was in the key, contradicting job {DROPS_MEASURED_IN_KEY[0]}'s "
                           f"measured run '1' in f078_scope.json"}
    return {**base, "verdict": "finding", "stop": True,
            "meaning": "rows outside the collapse changed the census"}


def _expect(key: str, measured: Any, expected: Any, met: Optional[bool] = None) -> dict:
    return {"key": key, "measured": measured, "expected": expected,
            "met": (measured == expected) if met is None else met}


def collect(conn) -> dict:
    """Role, identity, then every A8.3 reading, from one read-only transaction."""
    pre = role_preamble(conn)
    assert_campaign_target(conn)

    state: dict[str, Any] = {
        "role": pre,
        "identity": {
            "cluster_marker": conn.execute(text("SELECT cluster_id FROM keel_live_cluster LIMIT 1")).scalar(),
            "current_database": conn.execute(text("SELECT current_database()")).scalar(),
            "current_user": conn.execute(text("SELECT current_user")).scalar(),
            "server_now_utc": str(conn.execute(text("SELECT now()")).scalar()),
            "transaction_read_only": conn.execute(text("SHOW transaction_read_only")).scalar(),
        },
    }
    run1 = "j.inference_settings->>'run' = '1'"
    joined = "FROM jobs j JOIN protein_analyses a ON a.id = j.analysis_id"
    ident = ("a.input_value, j.inference_settings->>'tile_start', j.inference_settings->>'tile_end'")

    duplicates = {f"{r['parent']}/{r['tile_index']}": list(r["ids"])
                  for r in conn.execute(DUPLICATES_SQL).mappings()}
    row_keyed = conn.execute(text(
        f"SELECT count(*) FROM jobs j WHERE {run1} AND j.status = 'complete'")).scalar()
    identity_keyed = conn.execute(text(
        f"SELECT count(*) FROM (SELECT DISTINCT {ident} {joined} "
        f"WHERE {run1} AND j.status = 'complete') s")).scalar()
    multi = [{"accession": r[0], "tile_start": r[1], "tile_end": r[2], "job_ids": list(r[3])}
             for r in conn.execute(text(
                 f"SELECT {ident}, array_agg(j.id ORDER BY j.id) {joined} "
                 f"WHERE {run1} AND j.status = 'complete' GROUP BY 1, 2, 3 HAVING count(*) > 1 "
                 f"ORDER BY 1, 2, 3 LIMIT 50"))]
    with_pdb = conn.execute(text(
        f"SELECT count(*) {joined} WHERE {run1} AND j.status = 'complete' AND a.pdb_path IS NOT NULL")).scalar()
    run1_total = conn.execute(text(f"SELECT count(*) FROM jobs j WHERE {run1}")).scalar()
    noncomplete = {r[0]: r[1] for r in conn.execute(text(
        f"SELECT j.status, count(*) FROM jobs j WHERE {run1} AND j.status <> 'complete' "
        f"GROUP BY 1 ORDER BY 1"))}
    failed_acc = sorted(r[0] for r in conn.execute(text(
        f"SELECT a.input_value {joined} WHERE {run1} AND j.status = 'failed'")))
    keep = [{"job_id": r[0], "status": r[1], "has_pdb_path": r[2]} for r in conn.execute(text(
        f"SELECT j.id, j.status, a.pdb_path IS NOT NULL {joined} WHERE j.id = ANY(:ids) ORDER BY j.id"),
        {"ids": list(KEEP_JOBS)})]
    drop_jobs = [r[0] for r in conn.execute(
        text("SELECT id FROM jobs WHERE id = ANY(:ids) ORDER BY id"), {"ids": list(DROP_JOBS)})]
    drop_analyses = [r[0] for r in conn.execute(
        text("SELECT id FROM protein_analyses WHERE id = ANY(:ids) ORDER BY id"), {"ids": list(DROP_JOBS)})]
    version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()

    classification = classify_census(row_keyed)
    state["readings"] = {
        "duplicates": duplicates,
        "census_row_keyed": row_keyed,
        "census_classification": classification,
        "census_identity_keyed": identity_keyed,
        "identity_groups_with_more_than_one_row": multi,
        "run1_complete_with_pdb_path": with_pdb,
        "run1_total": run1_total,
        "run1_noncomplete_by_status": noncomplete,
        "run1_failed_accessions": failed_acc,
        "keep_rows": keep,
        "drop_rows_present": {"jobs": drop_jobs, "protein_analyses": drop_analyses},
        "alembic_version": version,
    }
    state["expectations"] = [
        _expect("1. DUPLICATES_SQL returns no row", duplicates, {}),
        _expect("2. census row-keyed (run '1' AND complete) against the pre-registered table",
                {"reading": row_keyed, "verdict": classification["verdict"]},
                "expected or named_category", met=not classification["stop"]),
        _expect("3. census identity-keyed equals row-keyed", identity_keyed, row_keyed),
        _expect("4. every complete run-1 row holds a pdb_path", with_pdb, row_keyed),
        _expect("4. run-1 rows not complete, by status", noncomplete, NONCOMPLETE_BY_STATUS),
        _expect("4. failed run-1 accessions", failed_acc, sorted(FAILED_ACCESSIONS)),
        _expect("5. keep rows 3673, 3674, 3675 complete with a pdb_path",
                [(k["job_id"], k["status"], k["has_pdb_path"]) for k in keep],
                [(j, "complete", True) for j in KEEP_JOBS]),
        _expect("6. alembic_version", version, EXPECTED_ALEMBIC),
        _expect("7. drop rows 3693, 3695, 3696 absent from jobs and protein_analyses",
                {"jobs": drop_jobs, "protein_analyses": drop_analyses},
                {"jobs": [], "protein_analyses": []}),
    ]
    return state


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="D-167 Phase E read (read-only, A8.3)")
    ap.add_argument("--url", default=os.environ.get("DATABASE_URL", ""))
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args(argv)
    if not args.url:
        print("REFUSING: no --url and no DATABASE_URL. The operator names the target.")
        return 1

    eng = create_engine(normalize_db_url(args.url), future=True, connect_args={"connect_timeout": 15})
    try:
        with read_only_transaction(eng) as conn:
            state = collect(conn)
    finally:
        eng.dispose()

    state["provenance"] = {
        "script": "scripts/d167_phase_e_read.py",
        "commit": _git("rev-parse", "HEAD"),
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "tracked_files_clean": _git("status", "--porcelain", "--untracked-files=no") == "",
        "read_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "target": f"{eng.url.host}:{eng.url.port}/{eng.url.database}",
        "url_username": eng.url.username,
    }

    print("=" * 78)
    print("D-167 PHASE E READ (read-only transaction; role, then D-159)")
    print("=" * 78)
    for line in format_preamble(state["role"]):
        print(line)
    for k, v in state["identity"].items():
        print(f"  {k:24s}: {v}")
    c = state["readings"]["census_classification"]
    print(f"\ncensus row-keyed: {c['reading']}  (baseline {c['baseline']}, expected {c['expected']})")
    print(f"  verdict: {c['verdict']}  stop: {c['stop']}  -- {c['meaning']}")
    print(f"census identity-keyed: {state['readings']['census_identity_keyed']}")
    groups = state["readings"]["identity_groups_with_more_than_one_row"]
    if groups:
        print(f"  identities holding more than one complete run-1 row: {len(groups)} (first shown)")
        print(f"    {groups[0]}")
    print()
    for e in state["expectations"]:
        print(f"  [{'MET' if e['met'] else 'NOT MET'}] {e['key']}")
        print(f"        measured {e['measured']!r}   expected {e['expected']!r}")

    sha = write_state(state, pathlib.Path(args.out))
    print(f"\nwritten : {args.out}")
    print(f"sha256  : {sha}")
    not_met = [e["key"] for e in state["expectations"] if not e["met"]]
    if not_met:
        print(f"\n{len(not_met)} expectation(s) NOT MET. STOP and report (A8.3). "
              f"This script does not interpret the reading.")
        return 2
    print("\nAll expectations met. Report to the Planner (A8.7 step 4 follows: the E.2 walk).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
