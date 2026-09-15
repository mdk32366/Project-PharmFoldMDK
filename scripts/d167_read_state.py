#!/usr/bin/env python3
"""D-167, step 1 — the live state of slice 2's 37, BEFORE `D-167` is written. READ-ONLY.

    python scripts/d167_read_state.py --url <tunnel url>        # the owner runs it

⚠⚠ **WHY THIS EXISTS.** Everything recorded about jobs 4869-4905 is the state *as the NULL-tier write
left it* (`PREWORK-2026-09-16.md` §1), not a measurement: it was not re-read on 2026-09-15. A
re-attach designed on remembered state is `F-047` amendment 6's class. This reads it — beside a
**positive control** (jobs 4866-4868, which completed normally) so `D-167` copies a correct completed
row column for column — and commits the answer as `data/control/d167/state_before.json`.

⚠⚠ **READ-ONLY BY THE DATABASE, NOT BY INTENTION** (`ORDERS-Code-2026-09-16` A1.8). Every read runs
inside `read_only_transaction`, whose first statement is `SET TRANSACTION READ ONLY`, so Postgres
refuses a write rather than a grep hoping there is none. `tests/test_d167_read_state.py` calibrates
that on a real database: an `UPDATE` inside the helper must raise.

⚠ **`D-159` first.** `assert_campaign_target` runs before any read that is reported.

⚠ **Columns come from the schema, never from log prose.** Rows are read whole (`to_jsonb`), and each
table's column list is recorded from `information_schema.columns`.

⚠ **One home.** The duplicate set, the claimed-job query and the foreign-key enumeration are imported
from `scripts/d166_collapse_duplicate_tiles.py`, so this read and the write it precedes ask the same
questions in the same words.

⚠ **What it does NOT decide.** It reports each expectation as met or not met, with the measured value.
**Any "not met" stops the work** (orders B.3): no `D-167`, no code. This script does not interpret a
disagreement, and it exits 2 so the operator cannot mistake one for success.

Tunnel (`D-162` rules 4-5): bound by name, Direct IP corroborated against `fly mpg status`,
`127.0.0.1` in the URL, one tunnel, closed after.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
import pathlib
import subprocess
import sys
from typing import Any

from sqlalchemy import create_engine, text

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from core.db_identity import assert_campaign_target  # noqa: E402
from db.dburl import normalize_db_url              # noqa: E402
from scripts.d166_collapse_duplicate_tiles import (  # noqa: E402
    CLAIMED_SQL,
    DUPLICATES_SQL,
    EXPECTED as COLLAPSE_EXPECTED,
    foreign_keys,
    json_parent_references,
    referencing_rows,
)

OUT = REPO / "data" / "control" / "d167" / "state_before.json"
ENQUEUED_JSON = REPO / "data" / "control" / "task4_slice2" / "enqueued.json"
#: ⚠ `ORDERS` A2.2: Task 3's Run-2 rows. Some fall in slice 2's band, so key 3 counts them while
#: slice 2's enqueue (and keys 1-2) excluded them through `_existing_run2`.
TASK3_ENQUEUED_JSON = REPO / "data" / "control" / "task3_run2" / "enqueued.json"

FIRST, LAST, N_OWED = 4869, 4905, 37
CONTROL_FIRST, CONTROL_LAST = 4866, 4868
SLICE2_IDS = (4389, 4905)          # data/control/task4_slice2/enqueued.json, first and last job id
SLICE2_BAND = (1, 30)              # scripts/task4_slice2.py BAND
EXPECTED_ALEMBIC = "0013_cancer_burden"
EXPECTED_SLICE2_FOLDED = 480

READ_ONLY = "SET TRANSACTION READ ONLY"


@contextlib.contextmanager
def read_only_transaction(engine):
    """A transaction the DATABASE holds read-only. ⚠ The SET is the first statement, before any
    read, because Postgres only accepts it before the transaction's first query."""
    with engine.begin() as conn:
        conn.execute(text(READ_ONLY))
        yield conn


def columns(conn, table: str) -> list[str]:
    return [r[0] for r in conn.execute(text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = current_schema() AND table_name = :t ORDER BY ordinal_position"),
        {"t": table})]


def whole_rows(conn, sql: str, **params) -> list[dict[str, Any]]:
    return [r[0] for r in conn.execute(text(sql), params)]


def write_state(state: dict, path: pathlib.Path) -> str:
    """Write `state` as JSON and return the sha256 of the bytes written. ⚠ Refuses to overwrite:
    this file is evidence, and a second read replacing the first is a read taken later."""
    if path.exists():
        raise SystemExit(f"REFUSING: {path} exists. It is evidence; move it aside deliberately.")
    path.parent.mkdir(parents=True, exist_ok=True)
    body = (json.dumps(state, indent=2, sort_keys=True, default=str) + "\n").encode("utf-8")
    path.write_bytes(body)
    return hashlib.sha256(body).hexdigest()


def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as e:
        return f"UNKNOWN ({e})"


def task3_overlap_ids(rows: list[dict], band: tuple[int, int]) -> list[int]:
    """Job ids of `rows` (an `enqueued.json`) whose span falls inside `band`. Pure. ⚠ Computed from
    the committed file in the run, never a hard-coded count (`ORDERS` A2.2)."""
    lo, hi = band
    return sorted(int(r["job_id"]) for r in rows if lo <= float(r["span_aa"]) <= hi)


def _expect(key: str, measured: Any, expected: Any) -> dict:
    return {"key": key, "measured": measured, "expected": expected, "met": measured == expected}


def collect(conn) -> dict:
    """Every read orders B.1 names, from one read-only transaction. Identity FIRST."""
    assert_campaign_target(conn)

    state: dict[str, Any] = {
        "identity": {
            "cluster_marker": conn.execute(text("SELECT cluster_id FROM keel_live_cluster LIMIT 1")).scalar(),
            "current_database": conn.execute(text("SELECT current_database()")).scalar(),
            "current_user": conn.execute(text("SELECT current_user")).scalar(),
            "server_now_utc": str(conn.execute(text("SELECT now()")).scalar()),
            "transaction_read_only": conn.execute(text("SHOW transaction_read_only")).scalar(),
        },
        "columns": {"jobs": columns(conn, "jobs"),
                    "protein_analyses": columns(conn, "protein_analyses")},
    }

    # ── 1 + 2: the 37 and the positive control, whole rows ─────────────────────────────────────
    jobs = whole_rows(conn, "SELECT to_jsonb(j) FROM jobs j WHERE j.id BETWEEN :a AND :b ORDER BY j.id",
                      a=CONTROL_FIRST, b=LAST)
    analyses = whole_rows(conn,
                          "SELECT to_jsonb(a) FROM protein_analyses a "
                          "WHERE a.id IN (SELECT analysis_id FROM jobs WHERE id BETWEEN :a AND :b) "
                          "ORDER BY a.id", a=CONTROL_FIRST, b=LAST)
    by_aid = {a["id"]: a for a in analyses}
    state["control"] = [{"job": j, "analysis": by_aid.get(j["analysis_id"])}
                        for j in jobs if j["id"] <= CONTROL_LAST]
    state["owed_37"] = [{"job": j, "analysis": by_aid.get(j["analysis_id"])}
                        for j in jobs if j["id"] >= FIRST]
    owed = [j for j in jobs if j["id"] >= FIRST]
    owed_a = [by_aid.get(j["analysis_id"]) or {} for j in owed]

    exp: list[dict] = []
    # ── 3: the analysis-id relation, measured on all 40 ───────────────────────────────────────
    offsets = sorted({j["analysis_id"] - j["id"] for j in jobs})
    exp.append(_expect("3. analysis_id - job_id over jobs 4866-4905 (distinct values)", offsets, [1]))
    exp.append(_expect("3. rows read in 4866-4905", len(jobs), 40))

    # ── 4: counts, each with its key ────────────────────────────────────────────────────────────
    exp.append(_expect("4. jobs rows, id 4869-4905", len(owed), N_OWED))
    exp.append(_expect("4. of those, status = 'complete'", sum(j["status"] == "complete" for j in owed), 0))
    exp.append(_expect("4. of those, analysis pdb_path IS NOT NULL",
                       sum(a.get("pdb_path") is not None for a in owed_a), 0))
    exp.append(_expect("4. of those, tier IS NULL", sum(j["tier"] is None for j in owed), N_OWED))
    exp.append(_expect("4. control 4866-4868, status = 'complete' AND pdb_path IS NOT NULL",
                       sum(c["job"]["status"] == "complete" and bool((c["analysis"] or {}).get("pdb_path"))
                           for c in state["control"]), 3))

    # ── 5: slice 2's population, under three keys ─────────────────────────────────────────────
    folded = ("j.status = 'complete' AND a.pdb_path IS NOT NULL")
    enqueued_ids = [r["job_id"] for r in json.loads(ENQUEUED_JSON.read_text(encoding="utf-8"))]
    keys = {
        "id range 4389-4905": ("j.id BETWEEN :lo AND :hi", {"lo": SLICE2_IDS[0], "hi": SLICE2_IDS[1]}),
        "enqueued.json job ids": ("j.id = ANY(:ids)", {"ids": enqueued_ids}),
        "run = '2' AND metadata span_aa in 1-30": (
            "j.inference_settings->>'run' = '2' "
            "AND (a.metadata->>'span_aa') ~ '^[0-9]+(\\.[0-9]+)?$' "
            "AND (a.metadata->>'span_aa')::numeric BETWEEN :blo AND :bhi",
            {"blo": SLICE2_BAND[0], "bhi": SLICE2_BAND[1]}),
    }
    slice2 = {}
    for name, (where, params) in keys.items():
        base = f"FROM jobs j JOIN protein_analyses a ON a.id = j.analysis_id WHERE {where}"
        total = conn.execute(text(f"SELECT count(*) {base}"), params).scalar()
        done = conn.execute(text(f"SELECT count(*) {base} AND {folded}"), params).scalar()
        slice2[name] = {"rows": total, "complete_and_pdb_path": done}
    state["slice2"] = slice2
    k1, k2, k3 = (v["complete_and_pdb_path"] for v in slice2.values())
    for name in list(keys)[:2]:
        exp.append(_expect(f"5. slice 2 [{name}]: complete AND pdb_path IS NOT NULL",
                           slice2[name]["complete_and_pdb_path"], EXPECTED_SLICE2_FOLDED))
    exp.append(_expect("5. keys 1 and 2 agree (id range, enqueued.json)", k1 == k2, True))

    # ⚠⚠ A2.2. Key 3 is not expected to equal keys 1-2: it also counts Task 3's Run-2 rows in the
    # band. The difference must be exactly those rows that the database reports folded — measured
    # here from the committed file, and recorded as a named category rather than a disagreement.
    in_band = task3_overlap_ids(json.loads(TASK3_ENQUEUED_JSON.read_text(encoding="utf-8")),
                                SLICE2_BAND)
    key3_where, key3_params = keys["run = '2' AND metadata span_aa in 1-30"]
    overlap_done = [r[0] for r in conn.execute(text(
        "SELECT j.id FROM jobs j JOIN protein_analyses a ON a.id = j.analysis_id "
        f"WHERE {key3_where} AND {folded} AND j.id = ANY(:t3) ORDER BY j.id"),
        {**key3_params, "t3": in_band})]
    state["task3_overlap"] = {"file": "data/control/task3_run2/enqueued.json",
                              "band": list(SLICE2_BAND), "ids_in_band": in_band,
                              "ids_complete_in_db": overlap_done}
    exp.append(_expect("5. key 3 minus key 2 equals task3_overlap "
                       "(Task 3 Run-2 rows in band 1-30, complete with pdb_path)",
                       k3 - k2, len(overlap_done)))

    # ── 6: the collapse set, in the collapse script's own words ───────────────────────────────
    live = {f"{r['parent']}/{r['tile_index']}": list(r["ids"])
            for r in conn.execute(DUPLICATES_SQL).mappings()}
    state["collapse_set"] = live
    exp.append(_expect("6. DUPLICATES_SQL", live,
                       {f"{p}/{t}": list(ids) for (p, t), ids in COLLAPSE_EXPECTED.items()}))

    # ── 7: references to the three drop ids ─────────────────────────────────────────────────
    drop_jobs = [drop for _keep, drop in COLLAPSE_EXPECTED.values()]
    drop_analyses = [r[0] for r in conn.execute(
        text("SELECT analysis_id FROM jobs WHERE id = ANY(:ids) ORDER BY id"), {"ids": drop_jobs})]
    fks = foreign_keys(conn)
    refs = referencing_rows(conn, fks, drop_jobs, drop_analyses)
    state["foreign_keys"] = [list(f) for f in fks]
    state["references_to_drop_rows"] = [list(r) for r in refs]
    exp.append(_expect("7. rows outside the collapse referencing its drop rows", len(refs), 0))
    children = json_parent_references(conn, drop_jobs)
    state["json_parent_references_to_drop_rows"] = children
    exp.append(_expect("7. jobs naming a drop row as inference_settings parent_job_id "
                       "(no declared constraint)", len(children), 0))

    # ── 8 + 9 ──────────────────────────────────────────────────────────────────────────────
    claimed = [r[0] for r in conn.execute(CLAIMED_SQL)]
    exp.append(_expect("8. jobs with status = 'claimed'", len(claimed), 0))
    version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    exp.append(_expect("9. alembic_version", version, EXPECTED_ALEMBIC))

    state["expectations"] = exp
    return state


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="D-167 step 1: the read, before D-167 (read-only)")
    ap.add_argument("--url", default=os.environ.get("DATABASE_URL", ""))
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args(argv)
    if not args.url:
        print("REFUSING: no --url and no DATABASE_URL.")
        return 1

    eng = create_engine(normalize_db_url(args.url), future=True,
                        connect_args={"connect_timeout": 15})
    try:
        with read_only_transaction(eng) as conn:
            state = collect(conn)
    finally:
        eng.dispose()

    state["provenance"] = {
        "script": "scripts/d167_read_state.py",
        "commit": _git("rev-parse", "HEAD"),
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "working_tree_clean": _git("status", "--porcelain", "--untracked-files=no") == "",
        "read_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        # ⚠ ORDERS A3.2: the URL's username is NOT the role. The committed 2026-09-15 read labels
        # it `target: … as pharmfoldmdk-app` while Postgres answered `schema_admin`.
        "target": f"{eng.url.host}:{eng.url.port}/{eng.url.database}",
        "url_username": eng.url.username,
    }

    print("=" * 78)
    print("D-167 STEP 1 - THE READ (read-only transaction, D-159 accepted)")
    print("=" * 78)
    for k, v in state["identity"].items():
        print(f"  {k:24s}: {v}")
    print()
    for e in state["expectations"]:
        print(f"  [{'MET' if e['met'] else 'NOT MET'}] {e['key']}")
        print(f"        measured {e['measured']!r}   expected {e['expected']!r}")

    sha = write_state(state, pathlib.Path(args.out))
    not_met = [e["key"] for e in state["expectations"] if not e["met"]]
    print(f"\nwritten : {args.out}")
    print(f"sha256  : {sha}")
    if not_met:
        print(f"\n{len(not_met)} expectation(s) NOT MET. Per ORDERS B.3 the work STOPS here and is "
              f"reported before D-167. This script does not interpret the disagreement.")
        return 2
    print("\nAll expectations met. Report to the Planner before D-167 (ORDERS B.3).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
