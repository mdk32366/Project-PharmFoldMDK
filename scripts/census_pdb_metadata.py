#!/usr/bin/env python3
"""Load census experimental PDB metadata — `D-171`.

Offline batch into Postgres (or SQLite test). Never mutates structural_score tables.

Runbook (laptop → Fly DB):
  1. Ensure migration 0015 applied.
  2. Fetch/map (default: PDBe graph-api best_structures per accession) OR
     `--from-json tests/fixtures/d171_pdbe_best_structures.json` for offline.
  3. `python -m scripts.census_pdb_metadata --load` (DATABASE_URL).
  4. Prior valid run → superseded; new run → valid.

ECD spans: `data/census/span_segments.csv` (V2 segments). Coverage gate ≥ 0.50.
Attribution: PDBe/SIFTS + RCSB links on each best entry.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.census_pdb import (  # noqa: E402
    STATUS_ABSENT,
    STATUS_ABSENT_NO_ECD,
    STATUS_PRESENT,
    STATUS_SPAN_ABSENT,
    select_pdb_for_accession,
)

RUN_VALID = "valid"
RUN_SUPERSEDED = "superseded"
PDBE_BEST = "https://www.ebi.ac.uk/pdbe/graph-api/uniprot/best_structures/{acc}"
SEGMENTS = ROOT / "data" / "census" / "span_segments.csv"
MANIFEST = ROOT / "data" / "census" / "census_manifest.v7.csv"


def load_segments() -> dict[str, str]:
    out: dict[str, str] = {}
    with SEGMENTS.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            acc = row.get("census_accession") or ""
            out[acc] = row.get("segments") or ""
    return out


def load_manifest_accessions() -> list[str]:
    accs: list[str] = []
    with MANIFEST.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            a = row.get("census_accession")
            if a:
                accs.append(a)
    return accs


def fetch_pdbe(accession: str, timeout: float = 30.0) -> list[dict[str, Any]]:
    url = PDBE_BEST.format(acc=accession)
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "PharmFoldMDK-D171/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return []
        raise
    items = data.get(accession) or data.get(accession.upper()) or []
    if isinstance(items, dict):
        items = items.get("data") or []
    return list(items) if isinstance(items, list) else []


def build_rows(
    accessions: list[str],
    *,
    cache: dict[str, list[dict[str, Any]]] | None,
    segments: dict[str, str],
    sleep_s: float = 0.05,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i, acc in enumerate(accessions):
        if cache is not None and acc in cache:
            cands = cache[acc]
        elif cache is not None:
            cands = []
        else:
            cands = fetch_pdbe(acc)
            if sleep_s:
                time.sleep(sleep_s)
        seg = segments.get(acc, "")
        span_absent = not bool(seg and seg.strip())
        painted = select_pdb_for_accession(
            accession=acc,
            candidates_raw=cands,
            ecd_segments=seg,
            span_absent=span_absent,
        )
        rows.append({
            "accession": acc,
            "pdb_status": painted["pdb_status"],
            "pdb_ids": painted["pdb_ids"],
            "pdb_best": painted["pdb_best"],
            "entries": painted["entries"],
        })
        if (i + 1) % 100 == 0:
            print(f"... {i+1}/{len(accessions)}", flush=True)
    return rows


def persist(engine: Any, rows: list[dict[str, Any]], *, source: str, notes: str | None) -> int:
    from sqlalchemy import select, update
    from sqlalchemy.orm import Session
    from db.models import CensusPdbAccession, CensusPdbRun

    n_present = sum(1 for r in rows if r["pdb_status"] == STATUS_PRESENT)
    n_absent = sum(1 for r in rows if r["pdb_status"] == STATUS_ABSENT)
    n_absent_no_ecd = sum(1 for r in rows if r["pdb_status"] == STATUS_ABSENT_NO_ECD)
    n_span_absent = sum(1 for r in rows if r["pdb_status"] == STATUS_SPAN_ABSENT)

    with Session(engine) as session:
        session.execute(
            update(CensusPdbRun)
            .where(CensusPdbRun.run_status == RUN_VALID)
            .values(run_status=RUN_SUPERSEDED)
        )
        run = CensusPdbRun(
            run_status=RUN_VALID,
            source=source,
            n_accessions=len(rows),
            n_present=n_present,
            n_absent=n_absent,
            n_absent_no_ecd=n_absent_no_ecd,
            n_span_absent=n_span_absent,
            notes=notes,
        )
        session.add(run)
        session.flush()
        for r in rows:
            session.add(CensusPdbAccession(
                run_id=run.id,
                accession=r["accession"],
                pdb_status=r["pdb_status"],
                pdb_ids=r["pdb_ids"],
                pdb_best=r["pdb_best"],
                entries=r["entries"],
            ))
        session.commit()
        return int(run.id)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--from-json", type=Path, help="Offline PDBe-shaped JSON map accession→list")
    p.add_argument("--accessions", nargs="*", help="Subset of accessions (default: full manifest)")
    p.add_argument("--load", action="store_true", help="Persist to DATABASE_URL")
    p.add_argument("--dry-run", action="store_true", help="Compute only; print counts")
    p.add_argument("--sleep", type=float, default=0.05)
    args = p.parse_args(argv)

    segments = load_segments()
    accessions = args.accessions or load_manifest_accessions()
    cache = None
    source = "PDBe/graph-api/best_structures"
    if args.from_json:
        cache = json.loads(args.from_json.read_text(encoding="utf-8"))
        source = f"fixture:{args.from_json.name}"

    rows = build_rows(accessions, cache=cache, segments=segments, sleep_s=args.sleep)
    counts = {}
    for r in rows:
        counts[r["pdb_status"]] = counts.get(r["pdb_status"], 0) + 1
    print("counts", counts, "n", len(rows))

    if args.dry_run or not args.load:
        if not args.load:
            print("pass --load to persist")
        return 0

    import os
    from sqlalchemy import create_engine
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL required for --load")
    engine = create_engine(url)
    run_id = persist(engine, rows, source=source, notes="D-171 census PDB metadata")
    print("wrote run_id", run_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
