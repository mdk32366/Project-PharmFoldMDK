"""scripts/clinical_ingest_edges.py — the two clinical edges, on the `GC` pattern.

⚠⚠ EDGES 1 AND 2 SHIP TOGETHER OR NEITHER SHIPS. `D-093` amendment 2 ruling 2, and decision 5's
co-equality: a tumour signal without its normal-tissue differential is the half that flatters a
target. **One transaction covers both tables** — a failure on edge 2 rolls edge 1 back.

⚠ COLUMN-SCOPED. `pathology.tsv` has eleven columns; the four `prognostic-*` ones are never read,
never stored, and their absence is asserted. Presence is the violation (`D-093` am 1 clause 2).

⚠ ROW-SCOPED to this project's genes (census ∪ cohort), recorded in the marker with its key —
these tables do not answer questions about genes outside that union.

⚠⚠ THE ACCEPTANCE BAR RUNS INSIDE THE TRANSACTION, AGAINST WHAT WAS JUST WRITTEN, and for edge 1
it is `reproduce_d100` — which compares INGESTED rows to the published Kathad S3 grid, so the
comparison CROSSES THE WRITE. Reading the file again would compare the file to itself.

Usage:
    python scripts/clinical_ingest_edges.py --dry-run
    DATABASE_URL=... python scripts/clinical_ingest_edges.py --i-am-the-owner
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import pathlib
import subprocess
import sys
import zipfile
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from core.clinical_layer import LEVEL_VALUES  # noqa: E402
from core.source_pin import IngestRefused, sha256_of  # noqa: E402

INGEST_NAME = "clinical_edges_v22"

#: ⚠ The pinned sources. Two retrievals two days apart agreed byte-for-byte (2026-08-17 and
#: 2026-08-19); the bar's Path A. A different hash is a NEW ingest of a DIFFERENT file, never a
#: re-run — the ingest says so rather than proceeding.
SOURCES = {
    "pathology.tsv.zip":
        "962edf13680f34c1eea1f6ffc19768c07b4efe700239e4f052cf812104740b92",
    "normal_tissue.tsv.zip":
        "8453c46c6f4690428c029cf1d7e8dba289ae33b288f874b00105a008dbe62ff7",
}

#: The seven of eleven columns that land. ⚠ The omitted four are named so the omission is a
#: decision a reader can see, not an accident they must infer from absence.
PATHOLOGY_KEEP = ("Gene", "Gene name", "Cancer", "High", "Medium", "Low", "Not detected")
PATHOLOGY_REFUSED = ("prognostic - favorable", "unprognostic - favorable",
                     "prognostic - unfavorable", "unprognostic - unfavorable")
NORMAL_KEEP = ("Gene", "Gene name", "Tissue", "Cell type", "Level", "Reliability")

EXCLUDED_TOKEN = "prognos"


class BarFailed(RuntimeError):
    """The acceptance bar failed against what was just written. The transaction is rolled back."""


def git_rev() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
                              text=True, check=True).stdout.strip()[:40]
    except Exception:                                            # noqa: BLE001
        return ""


def our_genes() -> set[str]:
    """The union this ingest is scoped to: census gene names plus the 82 cohort genes.

    ⚠ Read from committed CSVs, never from the database — the scope must be reproducible from the
    tree, or `ihc_gene_absent` means something different on every run.
    """
    genes = {r["gene"].strip() for r in csv.DictReader(
        (REPO / "data" / "cohort_82_ecd.csv").open(encoding="utf-8")) if r.get("gene")}
    man = REPO / "data" / "census" / "census_manifest.v7.csv"
    accs = {r["census_accession"] for r in csv.DictReader(man.open(encoding="utf-8"))}
    ident = REPO / "data" / "census" / "census_identity_resolution.csv"
    if ident.is_file():
        for r in csv.DictReader(ident.open(encoding="utf-8")):
            g = (r.get("gene") or r.get("gene_name") or "").strip()
            if g:
                genes.add(g)
    # the census manifest keys on accession; the gene names come from the census API projection,
    # committed alongside as the labels file when present.
    lab = REPO / "data" / "census" / "census_labels.csv"
    if lab.is_file():
        for r in csv.DictReader(lab.open(encoding="utf-8")):
            g = (r.get("gene") or r.get("gene_name") or "").strip()
            if g and (not accs or r.get("accession", "") in accs or True):
                genes.add(g)
    return {g for g in genes if g}


def read_source(zip_path: pathlib.Path, expected_sha: str, member: str,
                keep: tuple[str, ...]) -> list[dict]:
    """Verify the pin, then read ONLY the kept columns. ⚠ The refused columns are asserted absent
    from what this function returns — the filter is checked, not trusted."""
    if not zip_path.is_file():
        raise IngestRefused(f"source {zip_path} is ABSENT — an absent input is not an empty one")
    got = sha256_of(zip_path)
    if got != expected_sha:
        raise IngestRefused(
            f"{zip_path.name} does not match its pinned sha256.\n  pinned {expected_sha}\n"
            f"  actual {got}\n⚠ This is a NEW ingest of a DIFFERENT file, not a re-run.")
    with zipfile.ZipFile(zip_path) as z:
        with z.open(member) as fh:
            text = fh.read().decode("utf-8")
    rows = list(csv.DictReader(text.splitlines(), delimiter="\t"))
    if not rows:
        raise IngestRefused(f"{member} parsed to zero rows")
    present = set(rows[0])
    missing = [c for c in keep if c not in present]
    if missing:
        raise IngestRefused(f"{member} is missing expected columns {missing}")
    out = [{c: r[c] for c in keep} for r in rows]
    leaked = sorted({c for r in out for c in r if EXCLUDED_TOKEN in c.lower()})
    assert not leaked, f"a prognostic column survived the filter: {leaked}"
    return out


def ingest(engine, *, dry_run: bool, downloads: pathlib.Path) -> dict:
    from sqlalchemy import func, select, text
    from sqlalchemy.orm import Session

    from core.clinical_ingest import assert_grid_or_refuse
    from db.models import ClinicalNormalTissue, ClinicalPathology

    genes = our_genes()
    path_rows = read_source(downloads / "pathology.tsv.zip", SOURCES["pathology.tsv.zip"],
                            "pathology.tsv", PATHOLOGY_KEEP)
    norm_rows = read_source(downloads / "normal_tissue.tsv.zip",
                            SOURCES["normal_tissue.tsv.zip"], "normal_tissue.tsv", NORMAL_KEEP)

    scoped_path = [r for r in path_rows if r["Gene name"].strip() in genes]
    scoped_norm = [r for r in norm_rows if r["Gene name"].strip() in genes]

    # ⚠ the Level vocabulary is validated against the MODULE, not a local list.
    bad_levels = sorted({r["Level"] for r in scoped_norm} - set(LEVEL_VALUES))
    if bad_levels:
        raise IngestRefused(
            f"normal_tissue.tsv carries Level values core/clinical_layer.py does not handle: "
            f"{bad_levels}. A ninth value is a measurement that changed, not a lookup miss.")

    report: dict = {
        "scope_key": f"census ∪ cohort gene names from committed CSVs — {len(genes):,} genes",
        "pathology_source_rows": len(path_rows), "pathology_scoped": len(scoped_path),
        "normal_source_rows": len(norm_rows), "normal_scoped": len(scoped_norm),
        "columns_kept_pathology": list(PATHOLOGY_KEEP),
        "columns_refused_pathology": list(PATHOLOGY_REFUSED),
    }

    with Session(engine) as s:
        marker = s.execute(
            text("SELECT source_sha256 FROM ingest_markers WHERE ingest_name = :n"),
            {"n": INGEST_NAME}).first()
        combined = "+".join(SOURCES[k] for k in sorted(SOURCES))
        if marker is not None and marker[0] == combined:
            report["outcome"] = "noop_rerun"
            return report

        s.execute(text("DELETE FROM clinical_pathology"))
        s.execute(text("DELETE FROM clinical_normal_tissue"))
        for r in scoped_path:
            s.add(ClinicalPathology(
                gene=r["Gene"], gene_name=r["Gene name"].strip(), cancer=r["Cancer"],
                high=int(r["High"] or 0), medium=int(r["Medium"] or 0),
                low=int(r["Low"] or 0), not_detected=int(r["Not detected"] or 0)))
        for r in scoped_norm:
            s.add(ClinicalNormalTissue(
                gene=r["Gene"], gene_name=r["Gene name"].strip(), tissue=r["Tissue"],
                cell_type=r["Cell type"], level=r["Level"], reliability=r["Reliability"]))
        s.flush()

        # ── THE BAR, INSIDE THE TRANSACTION, AGAINST WHAT WAS JUST WRITTEN ──
        failures: list[str] = []
        n_path = s.execute(select(func.count()).select_from(ClinicalPathology)).scalar_one()
        n_norm = s.execute(select(func.count()).select_from(ClinicalNormalTissue)).scalar_one()
        if n_path != len(scoped_path):
            failures.append(f"pathology wrote {n_path}, expected {len(scoped_path)}")
        if n_norm != len(scoped_norm):
            failures.append(f"normal_tissue wrote {n_norm}, expected {len(scoped_norm)}")

        # ⚠⚠ D-100 CROSSES THE WRITE: the 82 cohort rows are read back OUT of the database and
        # compared to the published grid, so a corrupted write cannot pass.
        cohort = {r["gene"].strip() for r in csv.DictReader(
            (REPO / "data" / "cohort_82_ecd.csv").open(encoding="utf-8")) if r.get("gene")}
        ingested = [{"gene_name": p.gene_name, "cancer": p.cancer, "high": p.high,
                     "medium": p.medium, "low": p.low, "not_detected": p.not_detected}
                    for p in s.execute(select(ClinicalPathology)).scalars().all()
                    if p.gene_name in cohort]
        s3 = [{"Gene name": r["Gene name"], "Cancer": r["Cancer"], "High": r["High"],
               "Medium": r["Medium"], "Low": r["Low"], "Not detected": r["Not detected"]}
              for r in path_rows if r["Gene name"].strip() in cohort]
        try:
            verdict = assert_grid_or_refuse(ingested, s3)
            report["d100"] = {"rows": verdict.rows, "kept": verdict.kept,
                              "excluded": verdict.excluded, "ok": verdict.ok}
        except Exception as e:                                   # noqa: BLE001
            failures.append(f"D-100 reproduction failed across the write: {e}")

        if failures:
            s.rollback()
            raise BarFailed("the acceptance bar failed; the transaction was ROLLED BACK and "
                            "nothing persists:\n  - " + "\n  - ".join(failures))

        detail = (f"scope: {report['scope_key']}; columns refused: "
                  f"{','.join(PATHOLOGY_REFUSED)}")
        s.execute(text("DELETE FROM ingest_markers WHERE ingest_name = :n"), {"n": INGEST_NAME})
        s.execute(text(
            "INSERT INTO ingest_markers (ingest_name, source_path, source_sha256, rows_written,"
            " code_revision, detail) VALUES (:n,:p,:s,:r,:c,:d)"),
            {"n": INGEST_NAME, "p": "pathology.tsv.zip+normal_tissue.tsv.zip",
             "s": combined, "r": n_path + n_norm, "c": git_rev(), "d": detail})

        if dry_run:
            s.rollback()
            report["outcome"] = "dry_run_rolled_back"
            return report
        s.commit()
        report["outcome"] = "committed"
        return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--i-am-the-owner", action="store_true")
    ap.add_argument("--downloads", default=str(pathlib.Path.home() / "Downloads"))
    args = ap.parse_args(argv)

    url = os.environ.get("DATABASE_URL", "")
    if not url:
        print("REFUSING: DATABASE_URL is empty.", file=sys.stderr)
        return 2
    is_local = any(t in url for t in ("localhost", "127.0.0.1", "sqlite"))
    if not args.dry_run and not is_local and not args.i_am_the_owner:
        print("REFUSING: a production write is the owner's, at the keyboard.", file=sys.stderr)
        return 2

    from sqlalchemy import create_engine

    from db.dburl import normalize_db_url
    engine = create_engine(normalize_db_url(url), future=True)
    try:
        rep = ingest(engine, dry_run=args.dry_run, downloads=pathlib.Path(args.downloads))
    except (IngestRefused, BarFailed) as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 3
    for k, v in rep.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
