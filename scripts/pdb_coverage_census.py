#!/usr/bin/env python3
"""T0 -- the PDB coverage census instrument (SPEC-PDB-coverage-census-step1-tranches-v2 section 5).

    .\\.venv\\Scripts\\python.exe scripts/pdb_coverage_census.py --pass cohort --source <cache dir>

!! OFFLINE. T0 builds and proves the instrument; T1 is NOT authorised and NO live client exists here.
The only source is a local cache directory, and a missing cache entry is a RECORDED outcome
(`accession_unresolved`), never a network call and never a silent retry.

WHAT THIS MEASURES. Per accession: does a PDB entry map to it, does that entry overlap the ECD span
WE folded, and by how many residues. ! It does NOT compare a structure to a structure -- no lDDT, no
superposition, no coordinates. That is step 2 and it is not specified by the spec this implements.

!! TWO SUM CHECKS, NEVER ONE. The outcomes sum to 82 for the cohort pass AND to 3,467 for the census
pass. The populations OVERLAP BY 75, so a single combined check would double-count them; that is the
error SPEC v2 exists to correct, and the figure v1 used is void and appears nowhere here.

THE PRE-REGISTERED POLICY (spec section 3), fixed before any data is seen:
  * mapping comes from SIFTS-style residue-level UniProt<->PDB records -- never a name search
  * minimum overlap 50 residues, inclusive
  * minimum sequence identity 95% over the overlap, so isoform and ortholog mismatches are excluded
  * an overlap that is majority engineered mutation, or a chimera partner, is DISQUALIFIED
  * method and resolution are RECORDED, never filtered -- filtering belongs to step 2
  * many entries: all counted, the best ONE named (longest overlap; tie -> better resolution;
    tie -> lower PDB id, deterministically)
  * the folded ECD span is read from OUR record and the record is NAMED; no span -> `span_unknown`

! AN EIGHTH OUTCOME, ADDED AND REPORTED. The spec's seven have no home for an entry that overlaps
well but fails the identity floor. Folding it into `overlap_below_minimum` would report an ortholog
mismatch as a length problem; folding it into `no_pdb_entry` would report our filter as nature's. So
`overlap_identity_below_minimum` is ADDED -- which section 5 item 2 permits by name -- and raised to
the Planner rather than decided silently.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import sys
import time
from typing import Any, Optional

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

SPEC = "docs/SPEC-PDB-coverage-census-step1-tranches-v2.md"

COHORT_ROSTER = REPO / "data" / "cohort_82_accessions.txt"
COHORT_ECD = REPO / "data" / "cohort_82_ecd.csv"
CENSUS_MANIFEST = REPO / "data" / "census" / "census_manifest.v7.csv"
OUT_DIR = REPO / "data" / "pdb_coverage"

#: Spec section 3. Fixed before the data, never adjusted after seeing a distribution.
MIN_OVERLAP_RESIDUES = 50
MIN_IDENTITY_PERCENT = 95.0
MAJORITY_ENGINEERED = 0.5

#: The spec's seven, plus the eighth this instrument produces and therefore tallies (section 5 item 2:
#: an outcome the code produces that is not in the list is ADDED, never folded into another).
OUTCOMES = (
    "pdb_ecd_overlap",
    "overlap_below_minimum",
    "overlap_identity_below_minimum",
    "entry_but_no_ecd_overlap",
    "engineered_construct_only",
    "no_pdb_entry",
    "accession_unresolved",
    "span_unknown",
)

#: !! Per population, never their union: the two overlap by 75 and the union would double-count them.
EXPECTED_TOTALS = {"cohort": 82, "census": 3467}

LIST_CAP = 25


# -- pure core ------------------------------------------------------------------------------------

def new_tally() -> dict[str, int]:
    """Every outcome present at zero. A key that vanishes when empty reads as 'not measured'."""
    return {o: 0 for o in OUTCOMES}


def overlap_residues(span: tuple[int, int], start: int, end: int) -> int:
    """Residues an entry shares with the folded span. Inclusive on both ends; never negative."""
    lo = max(int(span[0]), int(start))
    hi = min(int(span[1]), int(end))
    return hi - lo + 1 if hi >= lo else 0


def _sort_key(cand: dict[str, Any]) -> tuple:
    """Longest overlap, then better resolution (smaller number), then lower PDB id."""
    res = cand.get("resolution")
    return (-cand["overlap"], float("inf") if res is None else float(res), str(cand["pdb_id"]))


def classify_accession(span: Optional[tuple[int, int]], entries: Optional[list[dict]],
                       unresolved: Optional[str] = None) -> tuple[str, dict[str, Any]]:
    """One accession -> one outcome, by a precedence fixed before the data.

    ! `accession_unresolved` and `span_unknown` are OURS, not the PDB's, and are never folded into
    `no_pdb_entry`: doing so would report our gap as nature's.

    Order: span_unknown -> accession_unresolved -> no_pdb_entry -> entry_but_no_ecd_overlap ->
    engineered_construct_only -> overlap_identity_below_minimum -> overlap_below_minimum ->
    pdb_ecd_overlap.
    """
    if span is None:
        return "span_unknown", {"meaning": "no folded ECD span is held in our record for this "
                                           "representative; never a computed guess"}
    if unresolved is not None or entries is None:
        return "accession_unresolved", {"reason": unresolved or "no record returned",
                                        "meaning": "an instrument condition, not a biology result"}

    considered = 0
    intersecting: list[dict[str, Any]] = []
    for e in entries:
        considered += 1
        n = overlap_residues(span, e["unp_start"], e["unp_end"])
        if n > 0:
            intersecting.append({
                "pdb_id": e["pdb_id"], "chain": e.get("chain"), "overlap": n,
                "identity": e.get("identity"), "method": e.get("method"),
                "resolution": e.get("resolution"),
                "engineered_fraction": e.get("engineered_fraction", 0.0),
                "is_chimera": bool(e.get("is_chimera", False)),
            })

    base = {"entries_considered": considered, "entries_intersecting": len(intersecting),
            "span": list(span)}
    if considered == 0:
        return "no_pdb_entry", {**base, "meaning": "no PDB entry maps to this accession"}
    if not intersecting:
        return "entry_but_no_ecd_overlap", {
            **base, "meaning": "an entry exists but shares no residue with the folded ECD span"}

    ok_construct = [c for c in intersecting
                    if not c["is_chimera"] and float(c["engineered_fraction"] or 0.0) <= MAJORITY_ENGINEERED]
    if not ok_construct:
        return "engineered_construct_only", {
            **base, "best_rejected": sorted(intersecting, key=_sort_key)[0],
            "meaning": "every overlapping entry is disqualified by the construct policy"}

    ok_identity = [c for c in ok_construct
                   if c["identity"] is not None and float(c["identity"]) >= MIN_IDENTITY_PERCENT]
    if not ok_identity:
        return "overlap_identity_below_minimum", {
            **base, "best_rejected": sorted(ok_construct, key=_sort_key)[0],
            "meaning": ("an overlap exists but falls below the identity floor -- an isoform or "
                        "ortholog mismatch, NOT a length problem and NOT an absent entry")}

    best = sorted(ok_identity, key=_sort_key)[0]
    if best["overlap"] < MIN_OVERLAP_RESIDUES:
        return "overlap_below_minimum", {**base, "best": best,
                                         "meaning": f"shorter than the {MIN_OVERLAP_RESIDUES}-residue minimum"}
    return "pdb_ecd_overlap", {**base, "best": best}


def sum_check(population: str, tally: dict[str, int], expected: int) -> dict[str, Any]:
    """One population, one sum. ! The two passes are checked SEPARATELY, never combined."""
    total = 0
    for name in OUTCOMES:
        total += tally.get(name, 0)
    return {"population": population, "total": total, "expected": expected, "ok": total == expected,
            "meaning": ("the outcomes reconcile with this population"
                        if total == expected else
                        "the outcomes do NOT reconcile with this population -- a silent category")}


def pass_state(name: str, tally: dict[str, int], read: int, population: int,
               release: Optional[str] = None) -> dict[str, Any]:
    """! A partial pass is reported AS partial, with how far it got.

    `population` is the size this pass reconciles against -- its OWN size, never the union of the
    two populations, which would double-count the 75 they share.
    """
    return {"pass": name, "tally": tally, "read": read, "population": population,
            "partial": read < population, "release": release,
            "sum_check": sum_check(name, tally, population)}


def capped_list(label: str, count: int, rows: list, cap: int) -> dict[str, Any]:
    return {"label": label, "count": count, "cap": cap, "rows_shown": len(rows),
            "capped": count > len(rows), "rows": rows}


def format_capped(d: dict[str, Any]) -> str:
    if d["capped"]:
        return (f"{d['label']}: count {d['count']} (its own count); "
                f"list CAPPED at cap {d['cap']}, {d['rows_shown']} shown")
    return f"{d['label']}: count {d['count']} (its own count); list complete, {d['rows_shown']} shown"


def policy_block() -> dict[str, Any]:
    return {"min_overlap_residues": MIN_OVERLAP_RESIDUES,
            "min_identity_percent": MIN_IDENTITY_PERCENT,
            "majority_engineered_fraction": MAJORITY_ENGINEERED,
            "mapping_source": "SIFTS-style residue-level UniProt<->PDB records",
            "method_and_resolution": "recorded, never filtered (filtering belongs to step 2)",
            "spec": SPEC}


def ascii_line(s: Any) -> str:
    return str(s).encode("ascii", "backslashreplace").decode("ascii")


def _say(s: Any = "") -> None:
    print(ascii_line(s))


# -- our records ----------------------------------------------------------------------------------

def population(name: str) -> list[str]:
    """The accessions of one population. ! They overlap by 75 and nothing here hides that."""
    if name == "cohort":
        out = []
        for line in COHORT_ROSTER.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                out.append(line.split()[0].strip().upper())
        return out
    if name == "census":
        with CENSUS_MANIFEST.open(encoding="utf-8", newline="") as fh:
            return [r["census_accession"].strip().upper() for r in csv.DictReader(fh)]
    raise SystemExit(f"REFUSING: unknown population {name!r}. Known: cohort, census")


def spans_for(name: str) -> dict[str, dict[str, Any]]:
    """The folded ECD span per accession, FROM OUR RECORD, with the record named on every row."""
    spans: dict[str, dict[str, Any]] = {}
    if name == "census":
        src = str(CENSUS_MANIFEST.relative_to(REPO)).replace("\\", "/")
        with CENSUS_MANIFEST.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                acc = row["census_accession"].strip().upper()
                try:
                    start, end = int(row["span_start"]), int(row["span_end"])
                except (TypeError, ValueError):
                    continue
                spans[acc] = {"start": start, "end": end, "source": src}
        return spans
    if name == "cohort":
        src = str(COHORT_ECD.relative_to(REPO)).replace("\\", "/")
        with COHORT_ECD.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                acc = (row.get("accession") or "").strip().upper()
                best = None
                for m in re.finditer(r"(\d+)-(\d+)\((\d+)\)", row.get("spans") or ""):
                    start, end, length = int(m.group(1)), int(m.group(2)), int(m.group(3))
                    if best is None or length > best[2]:
                        best = (start, end, length)
                if acc and best is not None:
                    # the LARGEST annotated extracellular span: the one the cohort fold used
                    spans[acc] = {"start": best[0], "end": best[1], "source": src,
                                  "rule": "largest annotated extracellular span"}
        return spans
    raise SystemExit(f"REFUSING: unknown population {name!r}")


# -- the source: offline only ---------------------------------------------------------------------

class DictSource:
    """An in-memory source. The T0 fixture shape, and the shape a cache directory is read into.

    A record is `{"entries": [...], "cache_hit": bool, "release": str}` or `{"error": "..."}`.
    ! There is NO live client in this module. T1 is not authorised.
    """

    def __init__(self, records: dict[str, dict[str, Any]]):
        self._records = records

    def fetch(self, accession: str) -> dict[str, Any]:
        rec = self._records.get(accession)
        if rec is None:
            return {"error": "not in the local cache (T0 is offline; no network call is made)"}
        return rec


class CacheDirSource(DictSource):
    """One JSON file per accession in a directory, read once into memory. Offline by construction."""

    def __init__(self, directory: pathlib.Path):
        records: dict[str, dict[str, Any]] = {}
        for path in sorted(directory.glob("*.json")):
            rec = json.loads(path.read_text(encoding="utf-8"))
            rec.setdefault("cache_hit", True)
            records[path.stem.strip().upper()] = rec
        super().__init__(records)


# -- the pass -------------------------------------------------------------------------------------

def load_progress(path: pathlib.Path) -> dict[str, dict[str, Any]]:
    """Records already held from an interrupted pass, keyed by accession."""
    held: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return held
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rec = json.loads(line)
                held[rec["accession"]] = rec
    return held


def run_pass(name: str, accessions: list[str], spans: dict[str, dict[str, Any]], source: Any,
             delay: float = 0.0, held: Optional[dict[str, dict[str, Any]]] = None,
             already_read_in: Optional[set[str]] = None,
             progress: Optional[pathlib.Path] = None) -> tuple[dict[str, int], list[dict[str, Any]]]:
    """Walk one population. Every outcome is tallied as it is decided -- no count is a list length."""
    tally = new_tally()
    records: list[dict[str, Any]] = []
    held = held or {}
    already = sorted(already_read_in or set())

    for accession in accessions:
        prior = held.get(accession)
        if prior is not None:
            tally[prior["outcome"]] = tally.get(prior["outcome"], 0) + 1
            records.append({**prior, "resumed": True})
            continue
        span_rec = spans.get(accession)
        span = (span_rec["start"], span_rec["end"]) if span_rec else None
        fetched = source.fetch(accession)
        if delay:
            time.sleep(delay)
        outcome, detail = classify_accession(
            span, fetched.get("entries"), unresolved=fetched.get("error"))
        tally[outcome] = tally.get(outcome, 0) + 1
        record = {"accession": accession, "outcome": outcome, "detail": detail,
                  "cache_hit": bool(fetched.get("cache_hit", False)),
                  "span_source": (span_rec or {}).get("source"),
                  "release": fetched.get("release")}
        if already:
            # ! the 75 and the 300 are read twice by design; the artifact says so
            record["re_read_of"] = already
        records.append(record)
        if progress is not None:
            with progress.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, sort_keys=True) + "\n")
    return tally, records


def write_artifact(state: dict[str, Any], path: pathlib.Path) -> str:
    """Write once, with the manifest the spec requires, and return the sha256 of the bytes."""
    if path.exists():
        raise SystemExit(f"REFUSING: {path} exists. It is evidence; move it aside deliberately.")
    body = dict(state)
    body["manifest"] = {
        "spec": SPEC,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED", "(unset)"),
        "written_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "policy": policy_block(),
        "release": state.get("release"),
        "note": ("a coverage number without a source release date is not reproducible: the archive "
                 "grows, so this number has a shelf life"),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(body, indent=2, sort_keys=True, default=str) + "\n").encode("utf-8")
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def render(state: dict[str, Any]) -> None:
    _say("=" * 78)
    _say(f"PDB COVERAGE CENSUS -- pass {state.get('pass')} (step 1; OFFLINE instrument)")
    _say("=" * 78)
    _say(f"  population   : {state.get('population')}   read: {state.get('read')}   "
         f"partial: {state.get('partial')}")
    _say(f"  source release: {state.get('release')}")
    _say("")
    for name in OUTCOMES:
        _say(f"    {name:34s}: {state['tally'].get(name, 0)}")
    s = state.get("sum_check") or {}
    _say("")
    _say(f"  sum check [{s.get('population')}]: total {s.get('total')} vs expected {s.get('expected')} "
         f"-> {'OK' if s.get('ok') else 'MISMATCH'}")
    _say("  ! the two populations overlap by 75; each pass reconciles against ITS OWN size")
    if state.get("examples"):
        _say(f"  {format_capped(state['examples'])}")
    p = state.get("policy") or {}
    if p:
        _say("")
        _say(f"  policy: min overlap {p.get('min_overlap_residues')} residues, "
             f"min identity {p.get('min_identity_percent')}%, "
             f"method/resolution {p.get('method_and_resolution')}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PDB coverage census, step 1 (T0 instrument, offline)")
    ap.add_argument("--pass", dest="which", required=True, choices=sorted(EXPECTED_TOTALS))
    ap.add_argument("--source", required=True,
                    help="a LOCAL cache directory of per-accession JSON records. T0 is offline; "
                         "no network client exists in this module.")
    ap.add_argument("--out", default=None)
    ap.add_argument("--delay", type=float, default=0.0, help="polite pacing between records")
    ap.add_argument("--resume", default=None, help="a .partial.jsonl written by an earlier run")
    args = ap.parse_args(argv)

    source_dir = pathlib.Path(args.source)
    if not source_dir.is_dir():
        raise SystemExit(
            f"REFUSING: --source {args.source!r} is not a directory. T0 reads a LOCAL cache only, "
            f"and T1 (the live pull) is not authorised.")

    accessions = population(args.which)
    spans = spans_for(args.which)
    source = CacheDirSource(source_dir)
    held = load_progress(pathlib.Path(args.resume)) if args.resume else {}
    progress = pathlib.Path(args.resume) if args.resume else None

    tally, records = run_pass(args.which, accessions, spans, source, delay=args.delay,
                              held=held, progress=progress)
    read = 0
    for _ in records:
        read += 1
    release = next((r.get("release") for r in records if r.get("release")), None)
    state = pass_state(args.which, tally, read, EXPECTED_TOTALS[args.which], release=release)
    examples = [r for r in records if r["outcome"] == "pdb_ecd_overlap"][:LIST_CAP]
    state["examples"] = capped_list("pdb_ecd_overlap examples", tally["pdb_ecd_overlap"],
                                    examples, LIST_CAP)
    state["policy"] = policy_block()
    state["records"] = records

    render(state)
    out = pathlib.Path(args.out) if args.out else OUT_DIR / f"{args.which}.step1.json"
    sha = write_artifact(state, out)
    _say(f"\nwritten : {out}")
    print(f"sha256  : {sha}")
    if not state["sum_check"]["ok"]:
        _say("\nThe sum check MISSED its population. A finding: report it.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
