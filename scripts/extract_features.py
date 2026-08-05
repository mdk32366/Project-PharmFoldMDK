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

from core.features import (  # noqa: E402
    EXTENDED_FEATURE_NAMES,
    FEATURE_NAMES,
    FeatureRow,
    extract_features,
)
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
                # Feature 7 (D-075) — coordinate-only, written alongside the six. It is NOT on the
                # pre-registered path; it exists for the named `geom_proxy` ablation.
                membrane_proximal_sasa=r.membrane_proximal_sasa,
                null_reasons=r.null_reasons,
                mean_plddt=r.mean_plddt,
                below_plddt_floor=r.below_plddt_floor,
                feature_version=r.feature_version,
            ))
        session.commit()
    return len(records)


# ── printing ─────────────────────────────────────────────────────────────────
# ── F-021: fill feature 7 in place, abort on anything else ───────────────────
SIX_FEATURE_COLUMNS = (
    "ecd_length", "radius_of_gyration", "mean_plddt_ecd",
    "membrane_proximal_plddt", "sasa_normalized", "largest_patch_fraction",
)


class FeatureDrift(Exception):
    """A recomputed feature 1-6 differs from what is stored, so the WHOLE fill aborts.

    ⚠ NOT a value to accept, and not a per-row skip. Features 1-6 are F-004's inputs; if they
    have moved since they were stored, the extraction pipeline is not deterministic across the
    changes since #109, and that is a finding about the instrument D-075 runs on. It outranks
    D-075: the fill stops, nothing is written, and the fold is examined before anything else.

    ⚠ Aborting the WHOLE fill rather than the drifting rows is the entire task. A fill that
    writes what matched and reports what did not is the corrupting command wearing a report.
    """


def ranking_set_analysis_ids(engine) -> set[int]:
    """The analysis_ids in the ranking set, read from `fit_scorer`'s OWN path.

    ⚠ NOT RE-DERIVED HERE, and that is the whole point. Membership is
    `ranked ∧ folded ∧ pLDDT >= 50 ∧ all six present`, defined once in `fit_scorer`. Writing that
    predicate a second time in this script would be two paths to one quantity -- the class that
    produced the F-017 double-claim, the producer/consumer schema mismatch, and the census key
    defined twice, all on 2026-08-05 alone.

    `group_b_accessions` and `evidence_by_symbol` are passed empty on purpose: they set the label
    and the comparator, neither of which participates in `in_ranking_set` (`_exclusion_reason`
    reads only disposition, mean_plddt and feature completeness). A test asserts this function
    agrees exactly with fit_scorer's path on a fixture that genuinely excludes a row.
    """
    import fit_scorer as _fs

    recs = _fs.read_feature_records(engine)
    rows = _fs.build_scorer_rows(recs, group_b_accessions=set(), evidence_by_symbol={})
    return {rec.analysis_id for rec, row in zip(recs, rows)          # noqa: B905
            if row.in_ranking_set and rec.analysis_id is not None}


def fill_feature_7(engine, records: list[ExtractedRecord], *, dry_run: bool,
                   ranking_set_ids: Optional[set[int]] = None) -> dict:
    """Write `membrane_proximal_sasa` and nothing else, in place, keyed by `analysis_id`.

    ⚠ UPDATE, NEVER INSERT. `load_features` is `session.add(...)` per record -- a pure insert --
    so running it to fill one column would double `protein_features` into two generations
    (F-021). Row count before == row count after, asserted inside the transaction.

    ⚠ ONLY WHERE NULL. An existing value is never overwritten, including a legitimate 0.0: a
    fully buried membrane-proximal window is a real measurement, not an absence.

    ⚠ `ranking_run_id` IS NOT TOUCHED. The fill creates no rows, so it needs no run id -- and
    the default that would have supplied one resolves to the most recent run, which is id=4
    (`plddt_only`), not the pre-registered id=2.

    ⚠ The 1-6 comparison runs on BOTH paths. The dry run is the owner's stop condition, so it
    must perform the same computation the write does, not a cheaper approximation of it.
    """
    from sqlalchemy import func, select as _select
    from sqlalchemy.orm import Session

    from db.models import ProteinFeatures

    by_analysis = {r.analysis_id: r for r in records}
    with Session(engine) as s:
        count_before = s.execute(_select(func.count()).select_from(ProteinFeatures)).scalar_one()
        stored = s.execute(
            _select(ProteinFeatures).order_by(ProteinFeatures.analysis_id)
        ).scalars().all()

        # ── the comparison, before any write, on every row we have a recomputation for ──
        drifts: list[str] = []
        compared = 0
        for row in stored:
            rec = by_analysis.get(row.analysis_id)
            if rec is None:
                continue
            compared += 1
            for col in SIX_FEATURE_COLUMNS:
                was, now = getattr(row, col), getattr(rec.row, col)
                if was != now:
                    drifts.append(f"analysis_id={row.analysis_id} {col}: stored={was!r} recomputed={now!r}")
        if drifts:
            raise FeatureDrift(
                f"ABORTING THE WHOLE FILL: {len(drifts)} of {compared} compared rows have a "
                f"feature 1-6 that differs from what is stored. NOTHING WAS WRITTEN.\n  "
                + "\n  ".join(drifts[:20])
                + (f"\n  ... (+{len(drifts) - 20} more)" if len(drifts) > 20 else "")
                + "\n⚠ Features 1-6 are F-004's inputs. Drift here means the extraction pipeline "
                  "is not deterministic across the changes since #109 -- a finding about the "
                  "instrument, which outranks D-075. Examine it before writing anything."
            )

        targets = [r for r in stored
                   if r.analysis_id in by_analysis and r.membrane_proximal_sasa is None]
        already = compared - len(targets)

        # ⚠ Task C stop condition 2, made evaluable AT THE KEYBOARD rather than after the write.
        # The fill's population (every row with coordinates) and the guard's population (the
        # ranking set) are DIFFERENT SETS BY DESIGN -- the original condition conflated them and
        # would have halted on the correct outcome. Two clauses, reported separately.
        # "Covered" asks: will this row have a value AFTER the fill? -- so an already-measured
        # ranking row counts, and a ranking row absent from the fill does not.
        rs = set(ranking_set_ids or ())
        target_ids = {r.analysis_id for r in targets}
        have_value = {r.analysis_id for r in stored if r.membrane_proximal_sasa is not None}
        covered = rs & (target_ids | have_value)

        result = {"compared": compared, "matched": compared, "already_present": already,
                  "written": 0, "would_write": len(targets), "dry_run": dry_run,
                  "rows_total": count_before,
                  "ranking_set_total": len(rs), "ranking_set_covered": len(covered),
                  "ranking_set_uncovered": sorted(rs - covered)[:20]}
        if dry_run:
            return result

        for row in targets:
            row.membrane_proximal_sasa = by_analysis[row.analysis_id].row.membrane_proximal_sasa
        s.flush()
        count_after = s.execute(_select(func.count()).select_from(ProteinFeatures)).scalar_one()
        if count_after != count_before:
            s.rollback()
            raise FeatureDrift(
                f"ABORTING: protein_features row count changed {count_before} -> {count_after}. "
                f"The fill must UPDATE, never INSERT. Rolled back."
            )
        s.commit()
        result["written"] = len(targets)
        return result


def _print_one(rec: ExtractedRecord) -> None:
    print(f"{rec.gene} ({rec.accession})  analysis_id={rec.analysis_id}  "
          f"disposition={rec.disposition}  boundary_method={rec.boundary_method}")
    print(f"  feature_version={rec.row.feature_version}")
    for name in EXTENDED_FEATURE_NAMES:          # the six, then feature 7 (D-075)
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
                        help="INSERT protein_features rows into DATABASE_URL (owner-authorised; not "
                             "against prod until the owner says so — D-058 §1.5). Requires --ranking-run.")
    parser.add_argument("--ranking-run", type=int, default=None,
                        help="the ranking_run id new rows belong to. REQUIRED with --load. ⚠ The "
                             "latest-run default was DELETED, not corrected (F-021): it resolved to "
                             "order_by(id.desc()) — id=4, `plddt_only` — on an assumption that held "
                             "when one run existed and is false now that four do.")
    parser.add_argument("--fill-feature-7", dest="fill_feature_7", action="store_true",
                        help="UPDATE membrane_proximal_sasa in place where it is NULL, and nothing "
                             "else. Aborts the whole fill if any row's features 1-6 differ from "
                             "stored. Creates no rows, so it needs no --ranking-run.")
    parser.add_argument("--dry-run", action="store_true",
                        help="with --fill-feature-7: run the 1-6 comparison and report what would "
                             "be written. Writes nothing (asserted by test, not promised by this flag).")
    args = parser.parse_args(argv)

    if args.load and args.fill_feature_7:
        parser.error("--load and --fill-feature-7 are different operations; pass one")
    if args.load and args.ranking_run is None:
        parser.error("--load requires --ranking-run: the latest-run default was removed (F-021) "
                     "because it silently resolved to the most recent run, id=4 (`plddt_only`)")
    if args.dry_run and not args.fill_feature_7:
        parser.error("--dry-run applies to --fill-feature-7")

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
        written = load_features(engine, records, ranking_run_id=args.ranking_run)
        print(f"loaded {written} protein_features rows (ranking_run_id={args.ranking_run})")
    elif args.fill_feature_7:
        engine = engine_factory()
        try:
            rs_ids = ranking_set_analysis_ids(engine)
            res = fill_feature_7(engine, records, dry_run=args.dry_run, ranking_set_ids=rs_ids)
        except FeatureDrift as exc:
            # ⚠ Formatted here, raised in the library: a programmatic caller must not be able to
            # proceed past a printed message. Same layering as fit_scorer's refusals.
            print(f"REFUSING TO FILL (features 1-6 drifted): {exc}")
            return 1
        mode = "DRY RUN — nothing written" if args.dry_run else "WRITE"
        print(f"[{mode}] features 1-6 compared on {res['compared']} rows, "
              f"{res['matched']} byte-identical, 0 drifted")
        print(f"[{mode}] feature 7: {res['would_write']} of {res['rows_total']} rows fillable, "
              f"{res['already_present']} already present, {res['written']} written")
        # ⚠ The owner's stop condition, printed so it can be read at the keyboard rather than
        # confirmed afterward. Two clauses: the fill's population, then the guard's population.
        print(f"[{mode}] ranking-set coverage: {res['ranking_set_covered']} of "
              f"{res['ranking_set_total']} ranking-set rows will have a value after this fill"
              + (f"  ⚠ UNCOVERED analysis_ids: {res['ranking_set_uncovered']}"
                 if res['ranking_set_uncovered'] else ""))
        print(f"[{mode}] STOP if: fillable+already < {res['rows_total']} rows, or "
              f"ranking-set coverage < {res['ranking_set_total']}")
    return 0


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
