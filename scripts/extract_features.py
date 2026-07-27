#!/usr/bin/env python3
"""scripts/extract_features.py — the D-058 offline feature-extraction driver and loader.

Reads structures from the **public read API** (`/api/analyses`, `/api/analyses/{id}/structure`,
`/api/analyses/{id}/plddt`), joins each to the local D-023 manifest for the boundary method,
computes the six D-027 features with `core.features.extract_features` (the pure function), and —
when explicitly asked — loads them into `protein_features` via `DATABASE_URL`, exactly as
`core/enqueue.py` builds its engine (D-058 decision 3). **No database credentials are needed to
extract**, only to load; and nothing here imports `worker/`.

Two disciplines from D-058 Addendum 2 are load-bearing here and are enforced by the tests:

- **§1 — a row is not a structure.** `/api/analyses` returns one row per *enqueued* analysis, so a
  failed fold (IGF2R: `fold_status=failed`, no PDB) still appears. Its structure/pLDDT endpoints
  404; the driver records all six features `null` with a reason naming the failure and **does not
  crash the batch** — a failed fold is a distinct state from a low-confidence one (D-043).
- **§2 — extract broadly, filter late.** Features are computed for *every* folded row, `held_out`
  included (MSLN, a well-folded target excluded from the fit for method reasons — D-021). The
  `ranked`/`held_out` partition and the pLDDT floor are scoring/display filters applied at fit and
  render time, never at extraction: a target with no feature row cannot be *reported* as excluded,
  only be absent (D-024). Every record carries `boundary_method` so feature 4's cross-method
  incomparability travels with the data.

`httpx` (pinned in `requirements-dev` + `worker/requirements.txt`) is imported at module scope;
`scripts/` is excluded from the runtime image (`test_image_contents.py`), so unlike `requests`
this is safe. Run this from any laptop with network access — the same public surface a grader opens.

Usage:
    python scripts/extract_features.py --one NECTIN4     # one target end to end, print its 6 features
    python scripts/extract_features.py --all             # extract every folded row, print a summary
    python scripts/extract_features.py --all --load      # ...and write protein_features (needs DATABASE_URL)
    python scripts/extract_features.py --all --api http://localhost:8000
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import httpx

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))   # so `core`/`db` import when run as a bare script

from core.features import FEATURE_NAMES, FeatureRow, extract_features  # noqa: E402
from core.manifest import ManifestRow, build_manifest  # noqa: E402

DEFAULT_API = "https://pharmfoldmdk.fly.dev"
HTTP_TIMEOUT_S = 60


# ── public read-API client (no DB, no worker/) ───────────────────────────────
def fetch_analyses(base_url: str, client: httpx.Client) -> list[dict]:
    """The light list of every analysis row (D-034). One row per *enqueued* target — a failed
    fold appears here too (D-058 Addendum 2 §1)."""
    resp = client.get(f"{base_url}/api/analyses", timeout=HTTP_TIMEOUT_S)
    resp.raise_for_status()
    payload = resp.json()
    return payload if isinstance(payload, list) else payload.get("analyses", payload.get("items", []))


def fetch_structure(base_url: str, analysis_id: int, client: httpx.Client) -> Optional[str]:
    """The stored `structure.pdb` as text, or `None` when the fold has no structure (404) — a
    failed fold (IGF2R). A 404 is expected and handled, never raised (D-058 Addendum 2 §1)."""
    resp = client.get(f"{base_url}/api/analyses/{analysis_id}/structure", timeout=HTTP_TIMEOUT_S)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.text


def fetch_plddt(base_url: str, analysis_id: int, client: httpx.Client) -> Optional[list[float]]:
    """The per-residue pLDDT list (0–100), or `None` when absent (404)."""
    resp = client.get(f"{base_url}/api/analyses/{analysis_id}/plddt", timeout=HTTP_TIMEOUT_S)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    data = resp.json()
    # The route serves the stored plddt.json (a list); tolerate an {"plddt": [...]} wrapper.
    return data if isinstance(data, list) else data.get("plddt")


# ── one record per folded row ────────────────────────────────────────────────
@dataclass
class ExtractedRecord:
    accession: str
    gene: Optional[str]
    analysis_id: int
    disposition: Optional[str]
    tier: Optional[str]
    boundary_method: Optional[str]
    row: FeatureRow


def extract_target(
    api_row: dict,
    manifest_row: Optional[ManifestRow],
    client: httpx.Client,
    base_url: str,
) -> ExtractedRecord:
    """Fetch one target's structure + pLDDT and compute its six features. The boundary method is
    joined from the **manifest** (D-058 §1.4), falling back to the API row. Never raises on a
    structure-less target — that becomes null-with-a-reason inside `extract_features`."""
    analysis_id = api_row["id"]
    boundary_method = (
        manifest_row.boundary_method if manifest_row is not None
        else api_row.get("boundary_method")
    )
    pdb_text = fetch_structure(base_url, analysis_id, client)
    plddt = fetch_plddt(base_url, analysis_id, client)
    row = extract_features(
        pdb_text, plddt,
        boundary_method=boundary_method,
        mean_plddt=api_row.get("mean_plddt"),
    )
    return ExtractedRecord(
        accession=api_row.get("accession"),
        gene=api_row.get("gene"),
        analysis_id=analysis_id,
        disposition=api_row.get("disposition"),
        tier=api_row.get("tier"),
        boundary_method=boundary_method,
        row=row,
    )


def extract_all(base_url: str, client: httpx.Client) -> list[ExtractedRecord]:
    """Extract features for **every** folded row — `held_out` included (D-058 Addendum 2 §2). No
    filtering by disposition or pLDDT floor here; those are fit/render-time filters."""
    analyses = fetch_analyses(base_url, client)
    manifest_by_accession = {r.accession: r for r in build_manifest()}
    records: list[ExtractedRecord] = []
    for api_row in analyses:
        accession = api_row.get("accession")
        records.append(
            extract_target(api_row, manifest_by_accession.get(accession), client, base_url)
        )
    return records


# ── the loader — writes protein_features via DATABASE_URL, exactly as enqueue does ──
def _build_engine():
    """A real SQLAlchemy engine from `DATABASE_URL`, normalized to the psycopg-3 scheme (D-012)
    the SAME way `core/enqueue.py` does — a one-shot loader is the same shape as a one-shot
    enqueue (D-058 decision 3), so no new credential posture is invented. Loud `KeyError` if
    `DATABASE_URL` is unset."""
    from sqlalchemy import create_engine

    from db.dburl import normalize_db_url

    return create_engine(normalize_db_url(os.environ["DATABASE_URL"]), future=True)


def load_features(engine, records: list[ExtractedRecord], *, ranking_run_id: Optional[int] = None) -> int:
    """Write one `protein_features` row per record. When `ranking_run_id` is None it resolves to
    the most recent `ranking_runs` row (the run the analyses belong to). Returns rows written.
    The serving tier still never computes a feature — this is an offline write, like enqueue."""
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from db.models import ProteinFeatures, RankingRun

    with Session(engine) as session:
        if ranking_run_id is None:
            run = session.execute(
                select(RankingRun).order_by(RankingRun.id.desc())
            ).scalars().first()
            ranking_run_id = run.id if run is not None else None

        for rec in records:
            r = rec.row
            session.add(ProteinFeatures(
                analysis_id=rec.analysis_id,
                ranking_run_id=ranking_run_id,
                ecd_length=r.ecd_length,
                radius_of_gyration=r.radius_of_gyration,
                mean_plddt_ecd=r.mean_plddt_ecd,
                membrane_proximal_plddt=r.membrane_proximal_plddt,
                sasa_normalized=r.sasa_normalized,
                largest_patch_fraction=r.largest_patch_fraction,
                null_reasons=r.null_reasons,
                mean_plddt=r.mean_plddt,
                below_plddt_floor=r.below_plddt_floor,
                feature_version=r.feature_version,
            ))
        session.commit()
    return len(records)


# ── printing ─────────────────────────────────────────────────────────────────
def _print_one(rec: ExtractedRecord) -> None:
    print(f"{rec.gene} ({rec.accession})  analysis_id={rec.analysis_id}  "
          f"disposition={rec.disposition}  boundary_method={rec.boundary_method}")
    print(f"  feature_version={rec.row.feature_version}")
    for name in FEATURE_NAMES:
        value = getattr(rec.row, name)
        shown = "null" if value is None else f"{value:.4f}"
        reason = rec.row.null_reasons.get(name)
        suffix = f"   [null: {reason}]" if reason else ""
        print(f"  {name:26s} {shown:>12}{suffix}")


def _print_summary(records: list[ExtractedRecord]) -> None:
    computed = sum(1 for r in records if not r.row.null_reasons)
    any_null = sum(1 for r in records if r.row.null_reasons)
    held_out = sum(1 for r in records if r.disposition == "held_out")
    print(f"extracted {len(records)} folded rows: "
          f"{computed} fully computed, {any_null} with at least one null-with-reason, "
          f"{held_out} held_out (extracted broadly, filtered late — D-058 Addendum 2 §2)")
    for rec in records:
        if rec.row.null_reasons:
            reasons = "; ".join(f"{k}={v}" for k, v in rec.row.null_reasons.items())
            print(f"  NULLS  {rec.gene:10s} {rec.accession:10s} {reasons}")


# ── CLI ──────────────────────────────────────────────────────────────────────
def run(
    argv: Optional[list[str]] = None,
    *,
    client_factory: Callable[[], httpx.Client] = httpx.Client,
    engine_factory: Callable[[], object] = _build_engine,
) -> int:
    """Parse args and drive extraction. `client_factory`/`engine_factory` are injected in tests
    (a fake httpx transport + a SQLite engine) and default to the real network + prod engine."""
    parser = argparse.ArgumentParser(
        prog="python scripts/extract_features.py",
        description="Extract the six D-027 features from stored folds (D-058).",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--one", metavar="ACCESSION_OR_GENE",
                       help="extract and print one target end to end")
    group.add_argument("--all", action="store_true",
                       help="extract every folded row and print a summary")
    parser.add_argument("--api", default=DEFAULT_API, help=f"read-API base URL (default {DEFAULT_API})")
    parser.add_argument("--load", action="store_true",
                        help="write protein_features to DATABASE_URL (owner-authorised; not against prod "
                             "until the owner says so — D-058 §1.5)")
    args = parser.parse_args(argv)

    with client_factory() as client:
        if args.one:
            analyses = fetch_analyses(args.api, client)
            manifest_by_accession = {r.accession: r for r in build_manifest()}
            match = next(
                (a for a in analyses
                 if a.get("accession") == args.one or a.get("gene") == args.one),
                None,
            )
            if match is None:
                print(f"no analysis found for {args.one!r}")
                return 1
            rec = extract_target(match, manifest_by_accession.get(match.get("accession")),
                                 client, args.api)
            _print_one(rec)
            records = [rec]
        else:
            records = extract_all(args.api, client)
            _print_summary(records)

    if args.load:
        engine = engine_factory()
        written = load_features(engine, records)
        print(f"loaded {written} protein_features rows")
    return 0


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
