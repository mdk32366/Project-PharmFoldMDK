#!/usr/bin/env python3
"""R1-R4 -- the population-aware read (ORDERS-Code-2026-09-17-R1-R4; A9.2 carried verbatim). READ-ONLY.

    .\\.venv\\Scripts\\python.exe scripts/d167_population_read.py --url <tunnel url>   # the owner runs it

WHY THIS EXISTS. The Phase E read stopped on expectation 3 (identity-keyed 3,576 vs row-keyed 3,648).
The gap of 72 was explained from committed files as the cohort-82 x census overlap, but the un-truncated
group list and each row's `cohort_tranche` were never read. These four readings read them, against
expectations registered before the read:

    R1  groups of (accession, tile_start, tile_end) with > 1 complete run '1' row, own count(*)    72
    R2  each such group holds exactly one cohort_tranche = 0 row and exactly one tranche >= 1 row  72 of 72
    R3  the identity key WITH population: groups with > 1 complete row                              0
    R4  P11717, Q8WXI7, Q9NYQ8: no complete tranche-0 row and exactly one complete census row      3 of 3

Any miss is a finding and stops the work. This script does not interpret a miss.

THE POPULATION CONVENTION, from source (ORDERS section 3), never from a paraphrase:
- tranche 0 is the 82-target cohort: `scripts/census_ingest.py` COHORT_TRANCHE = 0 (and refuses to ingest
  it as census); migration `0008_cohort_tranche` backfilled every pre-census row to 0 via
  `db/tranche_backfill.py`.
- tranche >= 1 is census: `census_manifest.v7.csv` tranches 1-5, written by `census_ingest.py`; Run-2
  enqueues (`task3_run2_folds.py`, `task4_slice*.py`) copy the manifest tranche, restricted to 1-4; tiles
  inherit their parent's tranche (`core/hold48.py`).
- NULL is UNCLASSIFIED (`db/models.py`: "not a census member and not tranche zero"). It is its own
  population here and is never folded into either.

KEYS, stated so no reading is ambiguous:
- "complete run '1' row": `jobs.status = 'complete' AND inference_settings->>'run' = '1'`, joined to its
  `protein_analyses` row. Every job existing at the run-label backfill was stamped run 1, cohort included
  (`scripts/backfill_run_label.py`).
- R4 "complete census row" is counted at the WHOLE-PROTEIN identity (tile_start and tile_end absent) --
  the identity R1-R3 group on. A census parent's tiles are separate identities; they are counted in a
  diagnostic, never in R4.

THE DEFECT THIS INSTRUMENT MUST NOT REPEAT (Phase E's `LIMIT 50`): every reading is its own count(*);
every list is a diagnostic that states its count and whether it is capped.

READ-ONLY BY THE DATABASE: `d167_read_state.read_only_transaction` issues `SET TRANSACTION READ ONLY`
first. Role first (`core.db_role`), identity second (`D-159`), then the reads. Output written ONCE to
`data/control/d167/population_read/r1r4_read.json` with its sha256 printed. Exit 0 when all four are met,
2 when any is not. Printed output is ASCII (A7.4); run it after the step-0 encoding fix and probe anyway.
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

from core.db_identity import assert_campaign_target                      # noqa: E402
from core.db_role import format_preamble, role_preamble                  # noqa: E402
from db.dburl import normalize_db_url                                    # noqa: E402
from scripts.d167_read_state import _git, read_only_transaction, write_state  # noqa: E402

OUT = REPO / "data" / "control" / "d167" / "population_read" / "r1r4_read.json"

#: A9.2, verbatim (CLOSEOUT-2026-09-16 section 5.1).
EXPECTED_R1 = 72
EXPECTED_R3 = 0
R4_ACCESSIONS = ("P11717", "Q8WXI7", "Q9NYQ8")
#: "3 of 3" -- written down, never taken as the length of the tuple above.
EXPECTED_R4 = 3

#: Diagnostic lists only. A reading never reads a list.
LIST_CAP = 100

POPULATION_SQL = (
    "CASE WHEN a.cohort_tranche = 0 THEN 'cohort' "
    "WHEN a.cohort_tranche >= 1 THEN 'census' "
    "ELSE 'untagged' END")

_BASE = ("FROM jobs j JOIN protein_analyses a ON a.id = j.analysis_id "
         "WHERE j.inference_settings->>'run' = '1' AND j.status = 'complete'")
_IDENT = "a.input_value, j.inference_settings->>'tile_start', j.inference_settings->>'tile_end'"
_WHOLE = ("(j.inference_settings->>'tile_start' IS NULL "
          "AND j.inference_settings->>'tile_end' IS NULL)")

R1_SQL = f"SELECT count(*) FROM (SELECT 1 {_BASE} GROUP BY {_IDENT} HAVING count(*) > 1) g"
R2_SQL = (f"SELECT count(*) FROM (SELECT 1 {_BASE} GROUP BY {_IDENT} HAVING count(*) > 1 "
          f"AND count(*) FILTER (WHERE a.cohort_tranche = 0) = 1 "
          f"AND count(*) FILTER (WHERE a.cohort_tranche >= 1) = 1) g")
R3_SQL = (f"SELECT count(*) FROM (SELECT 1 {_BASE} GROUP BY {_IDENT}, {POPULATION_SQL} "
          f"HAVING count(*) > 1) g")
R4_SQL = (f"SELECT count(*) FROM unnest(CAST(:accs AS text[])) AS x(acc) "
          f"WHERE (SELECT count(*) {_BASE} AND a.input_value = x.acc AND a.cohort_tranche = 0) = 0 "
          f"AND (SELECT count(*) {_BASE} AND a.input_value = x.acc "
          f"AND a.cohort_tranche >= 1 AND {_WHOLE}) = 1")
UNTAGGED_SQL = f"SELECT count(*) {_BASE} AND a.cohort_tranche IS NULL"
R1_SIZES_SQL = (f"SELECT n, count(*) FROM (SELECT count(*) AS n {_BASE} GROUP BY {_IDENT} "
                f"HAVING count(*) > 1) g GROUP BY n ORDER BY n")
R4_DETAIL_SQL = (f"SELECT count(*) FILTER (WHERE a.cohort_tranche = 0), "
                 f"count(*) FILTER (WHERE a.cohort_tranche >= 1 AND {_WHOLE}), "
                 f"count(*) FILTER (WHERE a.cohort_tranche >= 1 AND NOT {_WHOLE}), "
                 f"count(*) FILTER (WHERE a.cohort_tranche IS NULL) "
                 f"{_BASE} AND a.input_value = :acc")
R1_LIST_SQL = (f"SELECT {_IDENT}, array_agg(j.id ORDER BY j.id), array_agg(a.cohort_tranche ORDER BY j.id) "
               f"{_BASE} GROUP BY {_IDENT} HAVING count(*) > 1 ORDER BY 1, 2, 3 LIMIT :cap")
R3_LIST_SQL = (f"SELECT {_IDENT}, {POPULATION_SQL}, array_agg(j.id ORDER BY j.id) "
               f"{_BASE} GROUP BY {_IDENT}, {POPULATION_SQL} HAVING count(*) > 1 "
               f"ORDER BY 1, 2, 3 LIMIT :cap")


def capped_list(label: str, count: int, rows: list, cap: int) -> dict[str, Any]:
    """A diagnostic list that carries the count it was NOT derived from. Pure.

    It is capped whenever it holds fewer rows than its own count(*) says exist -- at the cap or below it."""
    return {"label": label, "count": count, "cap": cap, "rows_shown": len(rows),
            "capped": count > len(rows), "rows": rows}


def format_capped(d: dict[str, Any]) -> str:
    """One ASCII line. The count is the count(*); the list length is only ever printed as 'shown'."""
    if d["capped"]:
        return (f"{d['label']}: count {d['count']} (own count(*)); "
                f"list CAPPED at cap {d['cap']}, {d['rows_shown']} shown")
    return f"{d['label']}: count {d['count']} (own count(*)); list complete, {d['rows_shown']} shown"


def ascii_line(s: str) -> str:
    """Printed output is ASCII (A7.4). A non-ASCII character is escaped, never dropped: the shared
    `core.db_role.format_preamble` header carries a section sign, and the calibration report named it."""
    return str(s).encode("ascii", "backslashreplace").decode("ascii")


def _say(s: str = "") -> None:
    print(ascii_line(s))


def _expect(key: str, measured: Any, expected: Any) -> dict:
    return {"key": key, "measured": measured, "expected": expected, "met": measured == expected}


def collect(conn) -> dict:
    """Role, identity, then R1-R4 and their diagnostics, from one read-only transaction."""
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

    r1 = conn.execute(text(R1_SQL)).scalar()
    r2 = conn.execute(text(R2_SQL)).scalar()
    r3 = conn.execute(text(R3_SQL)).scalar()
    r4 = conn.execute(text(R4_SQL), {"accs": list(R4_ACCESSIONS)}).scalar()

    untagged = conn.execute(text(UNTAGGED_SQL)).scalar()
    sizes = {str(n): c for n, c in conn.execute(text(R1_SIZES_SQL))}
    r4_detail = {}
    for acc in R4_ACCESSIONS:
        t0, whole, tiles, null = conn.execute(text(R4_DETAIL_SQL), {"acc": acc}).one()
        r4_detail[acc] = {"tranche0_complete": t0, "census_whole_complete": whole,
                          "census_tile_complete": tiles, "untagged_complete": null}
    r1_rows = [{"accession": r[0], "tile_start": r[1], "tile_end": r[2],
                "job_ids": list(r[3]), "cohort_tranches": list(r[4])}
               for r in conn.execute(text(R1_LIST_SQL), {"cap": LIST_CAP})]
    r3_rows = [{"accession": r[0], "tile_start": r[1], "tile_end": r[2], "population": r[3],
                "job_ids": list(r[4])}
               for r in conn.execute(text(R3_LIST_SQL), {"cap": LIST_CAP})]

    state["readings"] = {"R1": r1, "R2": {"meeting": r2, "of": r1}, "R3": r3, "R4": r4}
    state["diagnostics"] = {
        "R1_groups": capped_list("R1 groups (accession, tile_start, tile_end)", r1, r1_rows, LIST_CAP),
        "R3_groups": capped_list("R3 groups (identity + population)", r3, r3_rows, LIST_CAP),
        "R1_groups_by_row_count": sizes,
        "untagged_complete_run1_rows": untagged,
        "R4_detail": r4_detail,
        "note": "diagnostics are not expectations; no diagnostic stops or passes the read",
    }
    state["keys"] = {
        "complete_run1_row": _BASE,
        "identity": _IDENT,
        "population": POPULATION_SQL,
        "R4_census_row": f"cohort_tranche >= 1 AND {_WHOLE}",
    }
    state["expectations"] = [
        _expect("R1 groups of (accession, tile_start, tile_end) with > 1 complete run '1' row", r1, EXPECTED_R1),
        _expect("R2 groups holding exactly one tranche-0 row and exactly one tranche >= 1 row",
                {"meeting": r2, "of": r1}, {"meeting": EXPECTED_R1, "of": EXPECTED_R1}),
        _expect("R3 identity key with population: groups with > 1 complete row", r3, EXPECTED_R3),
        _expect("R4 P11717, Q8WXI7, Q9NYQ8: no complete tranche-0 row, exactly one complete census row",
                r4, EXPECTED_R4),
    ]
    return state


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="R1-R4 population-aware read (read-only, A9.2)")
    ap.add_argument("--url", default=os.environ.get("DATABASE_URL", ""))
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args(argv)
    if not args.url:
        _say("REFUSING: no --url and no DATABASE_URL. The operator names the target.")
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
        "script": "scripts/d167_population_read.py",
        "orders": "ORDERS-Code-2026-09-17-R1-R4.md",
        "commit": _git("rev-parse", "HEAD"),
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "tracked_files_clean": _git("status", "--porcelain", "--untracked-files=no") == "",
        "read_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "target": f"{eng.url.host}:{eng.url.port}/{eng.url.database}",
        "url_username": eng.url.username,
    }

    _say("=" * 78)
    _say("R1-R4 POPULATION-AWARE READ (read-only transaction; role, then D-159)")
    _say("=" * 78)
    for line in format_preamble(state["role"]):
        _say(line)
    for k, v in state["identity"].items():
        _say(f"  {k:24s}: {v}")
    _say()
    for e in state["expectations"]:
        _say(f"  [{'MET' if e['met'] else 'NOT MET'}] {e['key']}")
        _say(f"        measured {e['measured']!r}   expected {e['expected']!r}")
    d = state["diagnostics"]
    _say("\ndiagnostics (not expectations):")
    _say(f"  {format_capped(d['R1_groups'])}")
    _say(f"  {format_capped(d['R3_groups'])}")
    _say(f"  R1 groups by row count (size: groups): {d['R1_groups_by_row_count']}")
    _say(f"  untagged (NULL tranche) complete run-1 rows: {d['untagged_complete_run1_rows']}")
    for acc, det in d["R4_detail"].items():
        _say(f"  R4 {acc}: {det}")

    sha = write_state(state, out)
    _say(f"\nwritten : {out}")
    print(f"sha256  : {sha}")
    not_met = [e["key"].split(" ")[0] for e in state["expectations"] if not e["met"]]
    if not_met:
        _say(f"\nNOT MET: {', '.join(not_met)}. A finding: STOP and report. "
              f"This script does not interpret the reading.")
        return 2
    _say("\nR1-R4 all met. Report to the Planner.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
