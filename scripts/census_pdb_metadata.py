#!/usr/bin/env python3
"""Load / refresh census experimental PDB metadata — `D-171` / `D-172`.

Offline batch into Postgres. Never mutates structural_score tables.
Uses normalize_db_url (D-012).

Runbook (weekly refresh + manual anytime):
  1. Ensure migrations through 0016 applied.
  2. Optional widen JSON for ABSENT cohort: `--widen-json path.json`
     (map accession → list of API-shaped candidates with match_kind + pdb_id).
  3. Full refresh (all census accessions):
       python -m scripts.census_pdb_metadata --refresh --load
     Alias: `--refresh` implies re-fetch/re-select for the whole census (or
     `--from-json` / `--widen-json` offline paths).
  4. Schedule note: run weekly from laptop (or Fly cron stub calling the same
     entrypoint). Idempotent — supersedes prior valid run.

D-172 widen: only ABSENT cohort gets widen candidates merged; NO_ECD / span_absent
/ present are not reclassified by widen-only rules (refresh re-evals ECD for all).
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
from core.census_pdb_widen import merge_candidates, tag_direct  # noqa: E402

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
    req = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": "PharmFoldMDK-D172/1.0"}
    )
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
    widen: dict[str, list[dict[str, Any]]] | None,
    segments: dict[str, str],
    sleep_s: float = 0.05,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i, acc in enumerate(accessions):
        if cache is not None and acc in cache:
            direct = tag_direct(cache[acc])
        elif cache is not None:
            direct = []
        else:
            direct = tag_direct(fetch_pdbe(acc))
            if sleep_s:
                time.sleep(sleep_s)
        widen_hits = (widen or {}).get(acc) or []
        # First-pass select without widen
        seg = segments.get(acc, "")
        span_absent = not bool(seg and seg.strip())
        painted = select_pdb_for_accession(
            accession=acc,
            candidates_raw=direct,
            ecd_segments=seg,
            span_absent=span_absent,
        )
        # D-172: widen ONLY when still ABSENT (and widen data provided)
        if painted["pdb_status"] == STATUS_ABSENT and widen_hits:
            merged = merge_candidates(direct, widen_hits)
            painted = select_pdb_for_accession(
                accession=acc,
                candidates_raw=merged,
                ecd_segments=seg,
                span_absent=span_absent,
            )
        elif painted["pdb_status"] != STATUS_ABSENT and widen_hits:
            # refresh path: merge widen into all for ECD re-eval when refresh supplies it
            merged = merge_candidates(direct, widen_hits)
            painted = select_pdb_for_accession(
                accession=acc,
                candidates_raw=merged,
                ecd_segments=seg,
                span_absent=span_absent,
            )
        rows.append({
            "accession": acc,
            "pdb_status": painted["pdb_status"],
            "pdb_ids": painted["pdb_ids"],
            "pdb_best": painted["pdb_best"],
            "pdb_related": painted.get("pdb_related") or [],
            "entries": painted["entries"],
        })
        if (i + 1) % 100 == 0:
            print(f"... {i+1}/{len(accessions)}", flush=True)
    return rows


def persist(engine: Any, rows: list[dict[str, Any]], *, source: str, notes: str | None) -> int:
    from sqlalchemy import update
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
                pdb_related=r.get("pdb_related") or [],
            ))
        session.commit()
        return int(run.id)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--from-json", type=Path, help="Offline PDBe-shaped JSON map accession→list")
    p.add_argument("--widen-json", type=Path, help="ABSENT widen candidates accession→list (match_kind required)")
    p.add_argument("--accessions", nargs="*", help="Subset of accessions (default: full manifest)")
    p.add_argument("--load", action="store_true", help="Persist to DATABASE_URL")
    p.add_argument("--refresh", action="store_true",
                   help="Weekly/manual refresh: re-select whole census (same as full run)")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--sleep", type=float, default=0.05)
    args = p.parse_args(argv)

    segments = load_segments()
    accessions = args.accessions or load_manifest_accessions()
    cache = None
    source = "PDBe/graph-api/best_structures"
    if args.from_json:
        cache = json.loads(args.from_json.read_text(encoding="utf-8"))
        source = f"fixture:{args.from_json.name}"
    widen = None
    if args.widen_json:
        widen = json.loads(args.widen_json.read_text(encoding="utf-8"))
        source = source + f"+widen:{args.widen_json.name}"
    if args.refresh:
        source = source + "+refresh"

    rows = build_rows(
        accessions, cache=cache, widen=widen, segments=segments, sleep_s=args.sleep
    )
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["pdb_status"]] = counts.get(r["pdb_status"], 0) + 1
    print("counts", counts, "n", len(rows), flush=True)

    if args.dry_run or not args.load:
        if not args.load:
            print("pass --load to persist", flush=True)
        return 0

    import os
    from sqlalchemy import create_engine
    from db.dburl import normalize_db_url

    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL required for --load")
    engine = create_engine(normalize_db_url(url), future=True)
    run_id = persist(
        engine, rows, source=source,
        notes="D-172 census PDB metadata (widen+refresh)" if (widen or args.refresh) else "D-171/D-172 census PDB metadata",
    )
    print("wrote run_id", run_id, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
