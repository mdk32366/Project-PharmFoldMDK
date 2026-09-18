#!/usr/bin/env python3
"""E1 / E2 / E3 -- the three enumerations (AMENDMENT 2 section 5). READ-ONLY.

    .\\.venv\\Scripts\\python.exe scripts/d167_enumerations.py --url <tunnel url>

These rectify what the R1-R4 read left unmeasured. Each reports with its own count(*) and its key
stated. None is a pass/fail gate EXCEPT E3.

    E1  MUC16 (Q8WXI7) rows BY STATUS -- every status, whole-protein AND tile identity, run label
        named including `(absent)`. Closes F-082 sub-question 1.
        ! It does NOT reopen R4: R4's verdict is ruled (F-082) and is not contingent on this.
    E2  the run-1 rows that are not complete, NAMED: F-078 recorded 5 (2 failed, 3 pending) and
        never enumerated them. ! MUC16 may or may not be among the pending; nothing is asserted
        here that the read does not measure.
    E3  which of the 82 cohort accessions lack a complete tranche-0 row -- NAMED, not counted.

!! E3's STOP CONDITION. If the set is not exactly {P11717, Q8WXI7, Q9NYQ8} that is a FINDING and
Phase 1 does not start in this tunnel: the cohort account would be wrong in a way that bears on C3,
and C3 gates P2. Exit 2. This script does not interpret a stop.

THE COHORT ROSTER is read from `data/cohort_82_accessions.txt` in its documented format --
`ACCESSION  SYMBOL`, comment lines skipped. ! Reading it naively yields 86 rows and a ZERO overlap
with the census; the header says so and the file was measured before it was used.

READ-ONLY BY THE DATABASE: `SET TRANSACTION READ ONLY` first, role preamble, then D-159. Output is
written ONCE with its sha256. Printed output is ASCII.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import pathlib
import sys
from typing import Any

from sqlalchemy import create_engine, text

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from core.db_identity import assert_campaign_target                          # noqa: E402
from core.db_role import format_preamble, role_preamble                      # noqa: E402
from db.dburl import normalize_db_url                                        # noqa: E402
from scripts.d167_read_state import _git, read_only_transaction, write_state  # noqa: E402

OUT = REPO / "data" / "control" / "d167" / "enumerations" / "e1_e3_read.json"
COHORT_ROSTER = REPO / "data" / "cohort_82_accessions.txt"

#: AMENDMENT 2 section 5: the three the cohort account says should lack a complete tranche-0 row.
E3_EXPECTED = ("P11717", "Q8WXI7", "Q9NYQ8")

#: E1's subject.
MUC16 = "Q8WXI7"

KEYS = {
    "E1": (f"every jobs row for {MUC16} joined to its analysis, grouped by status x identity branch "
           f"x run label (whole_protein = both tile keys absent; '(absent)' = no run key at all), "
           f"each cell its own count(*)"),
    "E2": ("run-1 jobs rows whose status is not 'complete', grouped by status with the accessions "
           "NAMED -- F-078 counted 5 and never listed them"),
    "E3": ("cohort accessions (cohort_tranche = 0) from data/cohort_82_accessions.txt holding NO "
           "row with status 'complete' -- named, not counted. STOP if the set is not exactly "
           "P11717, Q8WXI7, Q9NYQ8"),
}

_IDENTITY_BRANCH = (
    "CASE WHEN j.inference_settings->>'tile_start' IS NULL "
    "AND j.inference_settings->>'tile_end' IS NULL THEN 'whole_protein' "
    "WHEN j.inference_settings->>'tile_start' IS NOT NULL "
    "AND j.inference_settings->>'tile_end' IS NOT NULL THEN 'tile' "
    "ELSE 'partial_tile_keys' END")

E1_SQL = (f"SELECT j.status, {_IDENTITY_BRANCH}, "
          f"coalesce(j.inference_settings->>'run', '(absent)'), a.cohort_tranche, count(*) "
          f"FROM jobs j JOIN protein_analyses a ON a.id = j.analysis_id "
          f"WHERE a.input_value = :acc GROUP BY 1, 2, 3, 4 ORDER BY 1, 2, 3, 4")
E1_TOTAL_SQL = ("SELECT count(*) FROM jobs j JOIN protein_analyses a ON a.id = j.analysis_id "
                "WHERE a.input_value = :acc")
#: !! ROWS and ACCESSIONS are different quantities and are counted separately. F-078 recorded "5
#: non-complete run-1 rows"; one accession can hold more than one such row (a cohort-side row and a
#: census-side row), so a list of names is NEVER the count of rows. Each is its own count(*).
E2_SQL = ("SELECT j.status, count(*), count(DISTINCT a.input_value) FROM jobs j "
          "JOIN protein_analyses a ON a.id = j.analysis_id "
          "WHERE j.inference_settings->>'run' = '1' AND j.status <> 'complete' "
          "GROUP BY 1 ORDER BY 1")
E2_NAMED_SQL = ("SELECT j.status, a.input_value, a.cohort_tranche, j.id "
                "FROM jobs j JOIN protein_analyses a ON a.id = j.analysis_id "
                "WHERE j.inference_settings->>'run' = '1' AND j.status <> 'complete' "
                "ORDER BY j.status, a.input_value")
E3_SQL = ("SELECT x.acc FROM unnest(CAST(:accs AS text[])) AS x(acc) "
          "WHERE NOT EXISTS (SELECT 1 FROM protein_analyses a JOIN jobs j ON j.analysis_id = a.id "
          "WHERE a.input_value = x.acc AND a.cohort_tranche = 0 AND j.status = 'complete') "
          "ORDER BY x.acc")
E3_RUN_LABEL_SQL = ("SELECT coalesce(j.inference_settings->>'run', '(absent)'), j.status, count(*) "
                    "FROM jobs j JOIN protein_analyses a ON a.id = j.analysis_id "
                    "WHERE a.cohort_tranche = 0 GROUP BY 1, 2 ORDER BY 1, 2")


def cohort_accessions() -> list[str]:
    """The 82, from the committed roster in its documented `ACCESSION  SYMBOL` format."""
    out: list[str] = []
    for line in COHORT_ROSTER.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line.split()[0].strip().upper())
    return out


def e3_verdict(missing: list[str]) -> dict[str, Any]:
    """Compare the reading against the pre-registered set. Pure. Order does not matter."""
    got, want = sorted(set(missing)), sorted(E3_EXPECTED)
    unexpected = [a for a in got if a not in want]
    absent = [a for a in want if a not in got]
    if not unexpected and not absent:
        return {"reading": got, "expected": want, "matches": True, "stop": False,
                "unexpected": [], "absent_from_reading": [],
                "meaning": "the cohort account is proven, not merely consistent"}
    return {"reading": got, "expected": want, "matches": False, "stop": True,
            "unexpected": unexpected, "absent_from_reading": absent,
            "meaning": ("the cohort account differs from the pre-registered set. A finding: Phase 1 "
                        "does not start in this tunnel, because C3 gates P2")}


def ascii_line(s: Any) -> str:
    """Printed output is ASCII. A non-ASCII character is escaped, never dropped."""
    return str(s).encode("ascii", "backslashreplace").decode("ascii")


def _say(s: Any = "") -> None:
    print(ascii_line(s))


def collect(conn) -> dict:
    """Role, identity, then E1, E2, E3."""
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
        "keys": KEYS,
    }

    e1_rows = [{"status": s, "identity": ident, "run_label": run, "cohort_tranche": tranche,
                "count": n}
               for s, ident, run, tranche, n in conn.execute(text(E1_SQL), {"acc": MUC16})]
    e1_total = conn.execute(text(E1_TOTAL_SQL), {"acc": MUC16}).scalar()

    e2_by_status = {}
    e2_accessions_by_status = {}
    for status, rows_n, accs_n in conn.execute(text(E2_SQL)):
        e2_by_status[status] = rows_n
        e2_accessions_by_status[status] = accs_n
    e2_named = [{"status": s, "accession": acc, "cohort_tranche": tranche, "job_id": jid}
                for s, acc, tranche, jid in conn.execute(text(E2_NAMED_SQL))]

    roster = cohort_accessions()
    missing = [r[0] for r in conn.execute(text(E3_SQL), {"accs": roster})]
    cohort_by_run = {}
    for run, status, n in conn.execute(text(E3_RUN_LABEL_SQL)):
        cohort_by_run.setdefault(str(run), {})[str(status)] = n

    state["readings"] = {
        "E1": {"accession": MUC16, "total": e1_total, "by_status": e1_rows},
        "E2": {"by_status": e2_by_status,
               "distinct_accessions_by_status": e2_accessions_by_status,
               "failed_accessions": sorted({r["accession"] for r in e2_named
                                            if r["status"] == "failed"}),
               "pending_accessions": sorted({r["accession"] for r in e2_named
                                             if r["status"] == "pending"}),
               "rows": e2_named},
        "E3": {"roster_size": conn.execute(
                   text("SELECT count(*) FROM unnest(CAST(:accs AS text[]))"), {"accs": roster}).scalar(),
               "missing": missing,
               "verdict": e3_verdict(missing)},
    }
    state["diagnostics"] = {
        "cohort_rows_by_run_label_and_status": cohort_by_run,
        "note": ("E1 and E2 are enumerations, not gates. Only E3 stops. E1 does not reopen R4, "
                 "whose verdict is ruled in F-082"),
    }
    return state


def render(state: dict) -> None:
    keys = state.get("keys", KEYS)
    _say("=" * 78)
    _say("E1 / E2 / E3 -- THE THREE ENUMERATIONS (read-only; role, then D-159)")
    _say("=" * 78)
    for line in format_preamble(state.get("role", {})):
        _say(line)
    for k, v in state.get("identity", {}).items():
        _say(f"  {k:24s}: {v}")
    rd = state["readings"]

    e1 = rd["E1"]
    _say("")
    _say(f"E1 [{keys['E1']}]")
    _say(f"    {e1.get('accession', 'Q8WXI7')}: {e1['total']} row(s) in total")
    for b in e1["by_status"]:
        _say(f"      status {b['status']:<10} identity {b['identity']:<17} run {b['run_label']:<9} "
             f"tranche {b['cohort_tranche']}  count {b['count']}")
    if not e1["by_status"]:
        _say("      (no rows at all)")

    e2 = rd["E2"]
    _say("")
    _say(f"E2 [{keys['E2']}]")
    _say(f"    rows by status              : {e2['by_status']}")
    _say(f"    DISTINCT accessions by status: {e2.get('distinct_accessions_by_status')}  "
         f"(rows and accessions are different quantities)")
    _say(f"    failed : {e2['failed_accessions']}")
    _say(f"    pending: {e2['pending_accessions']}")

    e3 = rd["E3"]
    v = e3["verdict"]
    _say("")
    _say(f"E3 [{keys['E3']}]")
    _say(f"    cohort accessions read: {e3.get('roster_size')}")
    _say(f"    lacking a complete tranche-0 row: {e3['missing']}")
    _say(f"    expected: {list(E3_EXPECTED)}")
    _say(f"    verdict: {'STOP' if v['stop'] else 'matches'} -- {v['meaning']}")
    if v["unexpected"] or v["absent_from_reading"]:
        _say(f"      unexpected: {v['unexpected']}   absent from the reading: {v['absent_from_reading']}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="E1/E2/E3 enumerations (read-only, AMENDMENT 2 s5)")
    ap.add_argument("--url", default=os.environ.get("DATABASE_URL", ""))
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args(argv)
    if not args.url:
        print("REFUSING: no --url and no DATABASE_URL. The operator names the target.")
        return 1
    out = pathlib.Path(args.out)
    if out.exists():
        raise SystemExit(f"REFUSING: {out} exists. It is evidence; move it aside deliberately.")

    eng = create_engine(normalize_db_url(args.url), future=True, connect_args={"connect_timeout": 15})
    try:
        with read_only_transaction(eng) as conn:
            state = collect(conn)
    finally:
        eng.dispose()

    state["provenance"] = {
        "script": "scripts/d167_enumerations.py",
        "orders": "ORDERS-Code-2026-09-17-AMENDMENT-2-phase1-and-enumerations.md section 5",
        "commit": _git("rev-parse", "HEAD"),
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "tracked_files_clean": _git("status", "--porcelain", "--untracked-files=no") == "",
        "read_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "target": f"{eng.url.host}:{eng.url.port}/{eng.url.database}",
        "url_username": eng.url.username,
    }

    render(state)
    sha = write_state(state, out)
    _say(f"\nwritten : {out}")
    print(f"sha256  : {sha}")
    if state["readings"]["E3"]["verdict"]["stop"]:
        _say("\nE3 STOPS: the cohort account differs from the pre-registered set. Phase 1 does not "
             "start in this tunnel. This script does not interpret the reading.")
        return 2
    _say("\nE1/E2 reported; E3 matches its pre-registered set.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
