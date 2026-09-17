#!/usr/bin/env python3
"""TASK D -- the live feature-coverage report (ORDERS-Code-2026-09-17-TASK-D section 4). READ-ONLY.

    .\\.venv\\Scripts\\python.exe scripts/feature_coverage_report.py --url <tunnel url>

WHY THIS EXISTS, AND WHAT IT REFUSES TO REPRODUCE. `census_profile_statuses`
(`app/census_profile_read.py:127-129`) tests `_incommensurable_assembly` FIRST and `continue`s, so an
assembled parent or a tile window displays `refused_assembled_incommensurable` WHETHER OR NOT it has a
feature row. The Planner's file-based CSV did not model that, which is why its gap overstated the
display gap. So this report never asks "does a feature row exist?" alone -- it asks the page's question:

    C1a  census representatives with no `protein_features` row
    C1b  of those, how many ALREADY REFUSE as assembled -> extraction changes nothing visible for them
    C1c  C1a - C1b -- !! the ONLY true coverage gap
    C2   representatives whose accession's feature row hangs off a DIFFERENT analysis_id (stale
         representative): a named category, count AND ids, no pre-set expectation
    C3   cohort tranche-0 analyses with no feature row -- decides P2
    C4   C1a broken down by structure_kind, each branch its own count
    C5   did `census_features.v1` ever reach the table? Reported FIRST: the panel reads the TABLE and
         v1's manifest records `wrote_database_rows: false`

! THERE IS NO SOURCE TABLE TO REPRODUCE OR DIFFER FROM. The CSV behind the old coverage table is gone
(RECONSTRUCTION section 1), so THIS OUTPUT IS THE MEASUREMENT. The old gap figure is a historical
quotation and is never reconciled against here. The one surviving expectation is `C1a >= C1A_FLOOR`;
a SMALLER reading is a finding -- it would mean features arrived from a source not yet accounted for.

ONE HOME, NEVER A SECOND RULE: `choose_census_representative` is imported from `app.reads` and
`_incommensurable_assembly` from `app.census_profile_read`. A second copy of either would describe a
site that does not exist.

READ-ONLY BY THE DATABASE: `SET TRANSACTION READ ONLY` first, role preamble, then `D-159`. Output is
written ONCE with its sha256. Printed output is ASCII. It reads and reports only; nothing here deploys.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import sys
from typing import Any

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from app.census_profile_read import _incommensurable_assembly                 # noqa: E402
from app.reads import COHORT_TRANCHE, choose_census_representative, run_labels  # noqa: E402
from core.db_identity import assert_campaign_target                          # noqa: E402
from core.db_role import format_preamble, role_preamble                      # noqa: E402
from db.dburl import normalize_db_url                                        # noqa: E402
from db.models import ProteinAnalysis, ProteinFeatures                       # noqa: E402
from scripts.d167_read_state import _git, read_only_transaction, write_state  # noqa: E402

OUT = REPO / "data" / "control" / "coverage" / "feature_coverage_report.json"
V1_ARTIFACT = REPO / "data" / "census" / "census_features.v1.jsonl"

#: The one expectation that survives the loss of the source table. A SMALLER C1a is a finding.
C1A_FLOOR = 773

#: The kinds `choose_census_representative` returns (`app/reads.py:980-997`). ! FOUR, not the three
#: the orders name: `mucin` is its own kind and is never folded into `single-pass` -- which is exactly
#: MUC16's case (F-082). Reported here, per ORDERS section 4.1.
STRUCTURE_KINDS = ("assembled", "tiles_only", "single-pass", "mucin")

#: C5's equality sample. Capped on purpose, and the cap is reported as a cap.
SAMPLE_CAP = 50
LIST_CAP = 50

KEYS = {
    "C1a": ("census representatives (choose_census_representative over run-1 rows, "
            "cohort_tranche > 0) holding NO protein_features row"),
    "C1b": ("of C1a, those where _incommensurable_assembly is true -- already refused as assembled, "
            "so extraction changes nothing any page displays"),
    "C1c": ("C1a - C1b: representatives that would actually gain a rendered profile. "
            "THIS IS THE ONLY TRUE COVERAGE GAP"),
    "C2": ("representatives whose accession HAS a protein_features row, but attached to a different "
           "analysis_id than the representative's (a stale representative). Count AND ids; "
           "no pre-set expectation -- the count is the measurement"),
    "C3": "cohort rows (cohort_tranche = 0) with no protein_features row -- this decides P2",
    "C4": ("C1a broken down by the structure_kind the picker returned: assembled / tiles_only / "
           "single-pass / mucin, each branch its own count, never a subtraction from a total"),
    "C5": ("analysis_ids present in the committed census_features.v1 artifact that are present in "
           "the protein_features TABLE, plus a capped equality sample -- the panel reads the table, "
           "and v1's manifest records wrote_database_rows: false"),
}


#: ORDERS section 4: C5 is reported BEFORE C1 runs, because C5 can invalidate C1's expectation. The
#: sections are therefore selectable, and a C5-only run computes NOTHING else -- a pause that still
#: computed C1 first would not be a pause.
SECTIONS = ("C5", "C1", "C2", "C3", "C4")


def parse_sections(arg: str) -> list[str]:
    """`all`, or a comma-separated subset, returned in the order the orders fix. Pure."""
    if arg.strip().lower() == "all":
        return list(SECTIONS)
    want = {s.strip().upper() for s in arg.split(",") if s.strip()}
    unknown = sorted(want - set(SECTIONS))
    if unknown:
        raise SystemExit(f"REFUSING: unknown section(s) {unknown}. Known: {list(SECTIONS)}")
    return [s for s in SECTIONS if s in want]


def c1c(c1a: int, c1b: int) -> int:
    """C1a - C1b: the rows that would actually gain a rendered profile.

    !! This is the ONLY true coverage gap. C1a alone counts rows whose page never consults the
    feature row, so reporting C1a as "the gap" overstates it -- the Planner's CSV error.
    """
    return c1a - c1b


def c1a_verdict(c1a: int) -> dict[str, Any]:
    """The one surviving expectation, and it is a floor rather than an equality. Pure."""
    if c1a >= C1A_FLOOR:
        return {"reading": c1a, "floor": C1A_FLOOR, "finding": False,
                "meaning": f"at or above the floor of {C1A_FLOOR}"}
    return {"reading": c1a, "floor": C1A_FLOOR, "finding": True,
            "meaning": (f"BELOW the floor of {C1A_FLOOR}: features reached the table from a source "
                        f"not yet accounted for. A finding -- report it, do not reconcile it")}


def capped_list(label: str, count: int, rows: list, cap: int) -> dict[str, Any]:
    """A list that carries the count it was NOT derived from. Capped at the cap OR below it."""
    return {"label": label, "count": count, "cap": cap, "rows_shown": len(rows),
            "capped": count > len(rows), "rows": rows}


def format_capped(d: dict[str, Any]) -> str:
    if d["capped"]:
        return (f"{d['label']}: count {d['count']} (its own count); "
                f"list CAPPED at cap {d['cap']}, {d['rows_shown']} shown")
    return f"{d['label']}: count {d['count']} (its own count); list complete, {d['rows_shown']} shown"


def ascii_line(s: Any) -> str:
    """Printed output is ASCII. A non-ASCII character is escaped, never dropped."""
    return str(s).encode("ascii", "backslashreplace").decode("ascii")


def _say(s: Any = "") -> None:
    print(ascii_line(s))


def v1_analysis_ids() -> list[int]:
    """The analysis ids the committed v1 artifact claims. Read from the artifact, never assumed."""
    ids: list[int] = []
    with V1_ARTIFACT.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            aid = row.get("analysis_id")
            if aid is not None:
                ids.append(int(aid))
    return ids


def representative_readings(session: Session) -> dict[str, Any]:
    """C1a / C1b / C1c / C2 / C4 over census REPRESENTATIVES.

    The population is the picker's, so these are counted by walking every census row once and
    incrementing a named counter per representative. No counter is a list length and no branch is a
    subtraction from a total: C4's branches are counted where they are decided.
    """
    rows = session.scalars(
        select(ProteinAnalysis).where(ProteinAnalysis.cohort_tranche > COHORT_TRANCHE)).all()
    labels = run_labels(session, [r.id for r in rows])
    feature_ids = set(session.scalars(select(ProteinFeatures.analysis_id)).all())

    grouped: dict[str, list[ProteinAnalysis]] = {}
    for row in rows:
        acc = (row.input_value or "").strip().upper()
        if acc:
            grouped.setdefault(acc, []).append(row)

    c1a = c1b = c2 = 0
    # !! Every branch is present with a zero rather than absent (D-027: an absence is a category, and
    # a key that disappears when its count is zero reads as "not measured" instead of "measured none").
    # A kind the picker returns that is not listed here is ADDED, never dropped into another branch.
    by_kind: dict[str, int] = {k: 0 for k in STRUCTURE_KINDS}
    c2_ids: list[int] = []
    representatives = 0
    no_representative = 0

    for acc in sorted(grouped):
        group = grouped[acc]
        picked = choose_census_representative(group, run_labels=labels)
        if picked is None:
            no_representative += 1
            continue
        row, kind = picked
        representatives += 1
        if row.id in feature_ids:
            continue
        c1a += 1
        by_kind[kind] = by_kind.get(kind, 0) + 1
        if _incommensurable_assembly(row):
            c1b += 1
        for sibling in group:
            if sibling.id != row.id and sibling.id in feature_ids:
                c2 += 1
                c2_ids.append(row.id)
                break

    return {"C1a": c1a, "C1b": c1b, "C2": c2, "C4": by_kind, "C2_ids": sorted(c2_ids),
            "representatives": representatives, "accessions_without_a_representative": no_representative}


def collect(conn, sections: list[str] | None = None) -> dict:
    """Role, identity, then C5 first, then the representative readings and C3.

    ! `sections` selects what is READ, not what is printed: a section that is not requested is not
    computed at all, and its key is ABSENT from the output rather than present as a zero -- a zero
    would read as "measured none" when nothing was measured.
    """
    wanted = list(SECTIONS) if sections is None else list(sections)
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
        "keys": {k: v for k, v in KEYS.items()
                 if k in wanted or (k.startswith("C1") and "C1" in wanted)},
        "sections": wanted,
    }
    readings: dict[str, Any] = {}
    diagnostics: dict[str, Any] = {"note": (
        "diagnostics are not expectations. C4 keeps `mucin` as its own branch: the picker returns "
        "four kinds and folding one into another would be D-168's section 3 defect")}

    # -- C5 FIRST: the load-bearing reading. Did v1 ever reach the table at all?
    if "C5" in wanted:
        readings["C5"] = _c5(conn)

    if "C3" in wanted:
        # a row-level count, so it is SQL's own count(*)
        readings["C3"] = conn.execute(text(
            "SELECT count(*) FROM protein_analyses a LEFT JOIN protein_features f "
            "ON f.analysis_id = a.id WHERE a.cohort_tranche = 0 AND f.analysis_id IS NULL")).scalar()

    if {"C1", "C2", "C4"} & set(wanted):
        with Session(conn) as session:
            rep = representative_readings(session)
        if "C1" in wanted:
            readings["C1a"] = rep["C1a"]
            readings["C1b"] = rep["C1b"]
            readings["C1c"] = c1c(rep["C1a"], rep["C1b"])
            readings["C1a_verdict"] = c1a_verdict(rep["C1a"])
        if "C2" in wanted:
            readings["C2"] = {"count": rep["C2"], "ids": rep["C2_ids"]}
            diagnostics["C2_ids"] = capped_list("C2 stale-representative ids", rep["C2"],
                                                rep["C2_ids"][:LIST_CAP], LIST_CAP)
        if "C4" in wanted:
            readings["C4"] = rep["C4"]
        diagnostics["representatives"] = rep["representatives"]
        diagnostics["accessions_without_a_representative"] = rep["accessions_without_a_representative"]

    state["readings"] = readings
    state["diagnostics"] = diagnostics
    return state


def _c5(conn) -> dict[str, Any]:
    """C5, on its own, so it can be read and reported before C1 is computed."""
    v1_ids = v1_analysis_ids()
    v1_rows = conn.execute(text(
        "SELECT count(*) FROM (SELECT DISTINCT analysis_id FROM unnest(CAST(:ids AS bigint[])) "
        "AS analysis_id) s"), {"ids": v1_ids}).scalar()
    in_table = conn.execute(text(
        "SELECT count(*) FROM protein_features WHERE analysis_id = ANY(CAST(:ids AS bigint[]))"),
        {"ids": v1_ids}).scalar()
    sample_rows = conn.execute(text(
        "SELECT analysis_id, mean_plddt_ecd, ecd_length FROM protein_features "
        "WHERE analysis_id = ANY(CAST(:ids AS bigint[])) ORDER BY analysis_id LIMIT :cap"),
        {"ids": v1_ids, "cap": SAMPLE_CAP}).all()
    artifact = {}
    if sample_rows:
        wanted = {r[0] for r in sample_rows}
        with V1_ARTIFACT.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if row.get("analysis_id") in wanted:
                    artifact[int(row["analysis_id"])] = row.get("features") or {}
    checked = equal = 0
    differing: list[dict[str, Any]] = []
    for aid, mean_plddt, ecd_length in sample_rows:
        feats = artifact.get(aid)
        if feats is None:
            continue
        checked += 1
        same = (_close(feats.get("mean_plddt_ecd"), mean_plddt)
                and _close(feats.get("ecd_length"), ecd_length))
        if same:
            equal += 1
        else:
            differing.append({"analysis_id": aid,
                              "artifact": {"mean_plddt_ecd": feats.get("mean_plddt_ecd"),
                                           "ecd_length": feats.get("ecd_length")},
                              "table": {"mean_plddt_ecd": mean_plddt, "ecd_length": ecd_length}})

    return {"v1_rows": v1_rows, "in_table": in_table,
            "sample": {"cap": SAMPLE_CAP, "checked": checked, "equal": equal,
                       "differing": differing}}


def _close(a: Any, b: Any) -> bool:
    """Equality for a stored float against an artifact float. Absent on either side is NOT equal."""
    if a is None or b is None:
        return a is None and b is None
    return abs(float(a) - float(b)) <= 1e-9


def render(state: dict) -> None:
    """Print the report. Every reading states its key; every list says whether it is capped."""
    _say("=" * 78)
    _say("FEATURE COVERAGE REPORT (read-only; role, then D-159). C5 FIRST.")
    _say("=" * 78)
    for line in format_preamble(state.get("role", {})):
        _say(line)
    for k, v in state.get("identity", {}).items():
        _say(f"  {k:24s}: {v}")
    rd = state["readings"]
    keys = {**KEYS, **state.get("keys", {})}
    _say(f"  sections read           : {state.get('sections')}")
    if "C5" in rd:
        c5 = rd["C5"]
        _say("")
        _say(f"C5  [{keys['C5']}]")
        _say(f"    v1 artifact analysis_ids: {c5['v1_rows']}   "
             f"present in protein_features: {c5['in_table']}")
        s = c5["sample"]
        _say(f"    equality sample: checked {s['checked']}, equal {s['equal']}, "
             f"differing {s['checked'] - s['equal']} (cap {s.get('cap')})")
    if "C1a" in rd:
        for name in ("C1a", "C1b", "C1c"):
            _say("")
            _say(f"{name} [{keys[name]}]")
            _say(f"    {rd[name]}")
        v = rd["C1a_verdict"]
        _say(f"    C1a verdict: {'FINDING' if v['finding'] else 'ok'} -- {v['meaning']}")
    if "C2" in rd:
        _say("")
        _say(f"C2  [{keys['C2']}]")
        _say(f"    count {rd['C2']['count']}")
    if "C3" in rd:
        _say("")
        _say(f"C3  [{keys['C3']}]")
        _say(f"    {rd['C3']}")
    if "C4" in rd:
        _say("")
        _say(f"C4  [{keys['C4']}]")
        for kind, n in sorted(rd["C4"].items()):
            _say(f"    {kind:16s}: {n}")
    d = state.get("diagnostics", {})
    if d:
        _say("")
        _say("diagnostics (not expectations):")
        if "C2_ids" in d:
            _say(f"  {format_capped(d['C2_ids'])}")
        for k in ("representatives", "accessions_without_a_representative"):
            if k in d:
                _say(f"  {k}: {d[k]}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Feature coverage report (read-only, Phase 1)")
    ap.add_argument("--url", default=os.environ.get("DATABASE_URL", ""))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--sections", default="all",
                    help="all, or a comma-separated subset of C5,C1,C2,C3,C4. "
                         "C5 alone is the ORDERS section 4 pause: nothing else is computed.")
    args = ap.parse_args(argv)
    if not args.url:
        print("REFUSING: no --url and no DATABASE_URL. The operator names the target.")
        return 1
    sections = parse_sections(args.sections)
    out = pathlib.Path(args.out)
    if out.exists():
        raise SystemExit(f"REFUSING: {out} exists. It is evidence; move it aside deliberately.")

    eng = create_engine(normalize_db_url(args.url), future=True, connect_args={"connect_timeout": 15})
    try:
        with read_only_transaction(eng) as conn:
            state = collect(conn, sections)
    finally:
        eng.dispose()

    state["provenance"] = {
        "script": "scripts/feature_coverage_report.py",
        "orders": "ORDERS-Code-2026-09-17-TASK-D-coverage-report.md",
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
    if state["readings"].get("C1a_verdict", {}).get("finding"):
        _say("\nC1a is BELOW its floor. A finding: report it. This script does not interpret it.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
