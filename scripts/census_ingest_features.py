"""scripts/census_ingest_features.py — the census feature ingest, on the `GC` pattern.

⚠⚠ IT READS THE ARTIFACT. IT DOES NOT RE-EXTRACT. That is the whole point and it is the gap this
   script exists to close: `scripts/extract_features.py --load` re-fetches from the read API and
   re-computes, so what it writes is *not* the bytes `census_features.v1.jsonl`'s sha256
   certifies. An artifact whose hash does not describe what landed is not provenance, it is
   decoration. Here the hash is verified, then the SAME rows are written.

⚠ UPSERT, NEVER INSERT (`F-021` clause 1). Backed by `uq_protein_features_analysis_id` (0010), so
  a second run cannot double the table even if this code is wrong.

⚠ THE ACCEPTANCE BAR RUNS INSIDE THE TRANSACTION, AGAINST WHAT WAS JUST WRITTEN (`GC2`), and a
  failure ROLLS BACK (`GC3`). A bar that runs after the commit is a report, not a gate.

⚠ IDEMPOTENCY (`GC4`): completion is recorded in `ingest_markers` keyed to the SOURCE sha256. A
  re-run against the same hash is a NO-OP; against a different hash it is a NEW ingest and says
  so rather than silently appending.

⚠ `ranking_run_id` IS LEFT NULL, DELIBERATELY. Features are a property of the structure; census
  rows belong to no ranking run. `extract_features.py --load` requires `--ranking-run` and there
  is no honest value to pass — stamping run 5 (a `sensitivity` run) would assert a relationship
  that does not exist. A null here is a CATEGORY: *belongs to no run*.

⚠⚠ THIS DOES NOT RUN AGAINST PRODUCTION BY ITSELF. It refuses unless `--i-am-the-owner` is
   passed alongside a non-local `DATABASE_URL`, because a production write is the owner's, at the
   keyboard. `--dry-run` is the default posture for everything else.

Usage:
    python scripts/census_ingest_features.py --dry-run            # report, write nothing
    DATABASE_URL=... python scripts/census_ingest_features.py --i-am-the-owner
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from core.clinical_ingest import IngestRefused, verify_source  # noqa: E402
from core.features import FEATURE_NAMES  # noqa: E402

ART = REPO / "data" / "census" / "census_features.v1.jsonl"
MAN = REPO / "data" / "census" / "census_features.v1.manifest.json"
INGEST_NAME = "census_features_v1"

# The outcomes this ingest will persist. ⚠ Anything else is a REFUSAL, not a row: a vocabulary
# that silently accepts an unknown token is how a category becomes a blank.
PERSISTED_OUTCOMES = {"ok", "refused_span_below_floor", "structure_file_absent",
                      "structure_malformed", "extraction_error"}


class IngestBarFailed(RuntimeError):
    """The acceptance bar failed against what was just written. The transaction is rolled back."""


def git_rev() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
                              text=True, check=True).stdout.strip()[:40]
    except Exception:                                            # noqa: BLE001
        return ""


def six_digest(rows) -> str:
    """A digest of the six-tuples, keyed by analysis_id. ⚠ Sorted by id so it is a property of
    the CONTENT and not of insertion order — an order-dependent digest would compare two
    identical datasets and call them different."""
    h = hashlib.sha256()
    for r in sorted(rows, key=lambda r: r["analysis_id"]):
        vals = r.get("features") or {}
        h.update(str(r["analysis_id"]).encode())
        h.update(b"|" + (r.get("outcome") or "").encode() + b"|")
        for name in FEATURE_NAMES:
            v = vals.get(name)
            h.update(b"NULL" if v is None else repr(float(v)).encode())
            h.update(b",")
        h.update(b"\n")
    return h.hexdigest()


def load_artifact() -> tuple[list[dict], dict, str]:
    """Read + verify. ⚠ The manifest's own sha256 is the pin; `verify_source` hard-errors on an
    absent file and on a mismatch with DIFFERENT messages, because they are different facts."""
    if not MAN.exists():
        raise IngestRefused(f"manifest {MAN} is ABSENT — refusing to guess what the artifact is")
    manifest = json.loads(MAN.read_text(encoding="utf-8"))
    verify_source(ART, manifest["sha256"])                       # raises IngestRefused on mismatch

    if manifest.get("partial", True):
        raise IngestRefused(
            "the artifact is marked PARTIAL. A partial extraction is not a census-wide dataset "
            "(D-079 dec 6: no census-wide statistic from a partial tranche). Finish the run.")

    rows = [json.loads(ln) for ln in ART.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if len(rows) != manifest["lines"]:
        raise IngestRefused(
            f"the artifact has {len(rows)} lines; its manifest declares {manifest['lines']}")
    if len(rows) != manifest["census_rows_expected"]:
        raise IngestRefused(
            f"{len(rows)} rows against {manifest['census_rows_expected']} expected — "
            f"a count that does not match its own key is not a measurement")

    ids = [r["analysis_id"] for r in rows]
    if len(set(ids)) != len(ids):
        dup = [i for i, c in Counter(ids).items() if c > 1][:5]
        raise IngestRefused(f"the artifact carries duplicate analysis_ids, e.g. {dup}")

    unknown = {r.get("outcome") for r in rows} - PERSISTED_OUTCOMES
    if unknown:
        raise IngestRefused(f"unknown outcome tokens in the artifact: {sorted(unknown)}")

    return rows, manifest, manifest["sha256"]


def ingest(engine, rows, manifest, source_sha: str, *, dry_run: bool) -> dict:
    """One transaction: upsert, then BAR, then marker. Any failure rolls the whole thing back."""
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from db.models import ProteinAnalysis, ProteinFeatures

    expected_digest = six_digest(rows)
    by_id = {r["analysis_id"]: r for r in rows}
    report: dict = {"expected_digest": expected_digest, "rows_in_artifact": len(rows)}

    with Session(engine) as s:
        # ── GC4: is this a no-op re-run, a new ingest, or the first? ─────────
        marker = _read_marker(s)
        if marker is not None:
            if marker["source_sha256"] == source_sha:
                report["outcome"] = "noop_rerun"
                report["detail"] = (
                    f"already ingested at {marker['completed_at']} from the SAME sha256 "
                    f"({source_sha[:16]}…). Nothing written.")
                return report
            report["prior_sha256"] = marker["source_sha256"]
            report["outcome_note"] = (
                "⚠ a marker exists for a DIFFERENT sha256 — this is a NEW ingest of a "
                "different artifact, not a re-run. Proceeding and REPLACING the marker.")

        # ⚠ every artifact row must point at an analysis that exists. A FK violation mid-write
        # would abort anyway; naming the missing ones is a better failure than a driver error.
        present = set(s.execute(select(ProteinAnalysis.id)).scalars().all())
        missing = sorted(set(by_id) - present)
        if missing:
            raise IngestRefused(
                f"{len(missing)} artifact rows reference analyses that do not exist here, "
                f"e.g. {missing[:5]}. Wrong database, or the artifact is from another environment.")

        existing = {f.analysis_id: f for f in s.execute(
            select(ProteinFeatures).where(ProteinFeatures.analysis_id.in_(list(by_id)))
        ).scalars().all()}
        report["updated"] = len(existing)
        report["inserted"] = len(by_id) - len(existing)

        for aid, rec in by_id.items():
            vals = rec.get("features") or {}
            fields = dict(
                ranking_run_id=None,                  # ⚠ a category: belongs to no ranking run
                extraction_outcome=rec["outcome"],
                null_reasons=rec.get("null_reasons") or {},
                feature_version=rec.get("feature_version") or "",
                **{name: vals.get(name) for name in FEATURE_NAMES},
            )
            fields["membrane_proximal_sasa"] = vals.get("membrane_proximal_sasa")
            row = existing.get(aid)
            if row is None:
                s.add(ProteinFeatures(analysis_id=aid, **fields))   # UPSERT, not blind INSERT
            else:
                for k, v in fields.items():
                    setattr(row, k, v)
        s.flush()

        # ── GC2: THE BAR, INSIDE THE TRANSACTION, AGAINST WHAT WAS JUST WRITTEN ──
        written = s.execute(
            select(ProteinFeatures).where(ProteinFeatures.analysis_id.in_(list(by_id)))
        ).scalars().all()
        readback = [{"analysis_id": f.analysis_id,
                     "outcome": f.extraction_outcome,
                     "features": {n: getattr(f, n) for n in FEATURE_NAMES}}
                    for f in written]
        got_digest = six_digest(readback)

        failures = []
        if len(written) != len(by_id):
            failures.append(f"read back {len(written)} rows, expected {len(by_id)}")
        if got_digest != expected_digest:
            failures.append(f"six-tuple digest {got_digest[:16]}… != artifact {expected_digest[:16]}…")
        dupes = [aid for aid, c in Counter(f.analysis_id for f in written).items() if c > 1]
        if dupes:
            failures.append(f"{len(dupes)} analyses carry more than one feature row")
        want_counts = Counter(r["outcome"] for r in rows)
        got_counts = Counter(f.extraction_outcome for f in written)
        if want_counts != got_counts:
            failures.append(f"outcome counts differ: artifact {dict(want_counts)} vs "
                            f"written {dict(got_counts)}")
        report["readback_digest"] = got_digest
        report["outcome_counts"] = dict(got_counts)

        if failures:
            s.rollback()
            raise IngestBarFailed(
                "the acceptance bar failed against what was just written; the transaction was "
                "ROLLED BACK and nothing persists:\n  - " + "\n  - ".join(failures))

        _write_marker(s, source_sha=source_sha, rows_written=len(by_id),
                      detail=f"digest {expected_digest}", replace=marker is not None)

        if dry_run:
            s.rollback()
            report["outcome"] = "dry_run_rolled_back"
            return report

        s.commit()
        report["outcome"] = "committed"
        return report


def _read_marker(s):
    from sqlalchemy import text
    row = s.execute(
        text("SELECT source_sha256, completed_at FROM ingest_markers "
             "WHERE ingest_name = :n AND source_path = :p"),
        {"n": INGEST_NAME, "p": ART.name}).first()
    return None if row is None else {"source_sha256": row[0], "completed_at": row[1]}


def _write_marker(s, *, source_sha: str, rows_written: int, detail: str, replace: bool) -> None:
    from sqlalchemy import text
    if replace:
        s.execute(text("DELETE FROM ingest_markers WHERE ingest_name = :n AND source_path = :p"),
                  {"n": INGEST_NAME, "p": ART.name})
    s.execute(
        text("INSERT INTO ingest_markers "
             "(ingest_name, source_path, source_sha256, rows_written, code_revision, detail) "
             "VALUES (:n, :p, :s, :r, :c, :d)"),
        {"n": INGEST_NAME, "p": ART.name, "s": source_sha, "r": rows_written,
         "c": git_rev(), "d": detail})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="run the whole thing including the bar, then roll back. Writes nothing.")
    ap.add_argument("--i-am-the-owner", action="store_true",
                    help="required to COMMIT against a non-local database (D-058 §1.5)")
    args = ap.parse_args(argv)

    url = os.environ.get("DATABASE_URL", "")
    if not url:
        print("REFUSING: DATABASE_URL is empty. This ingest needs a target, named explicitly.",
              file=sys.stderr)
        return 2
    is_local = any(t in url for t in ("localhost", "127.0.0.1", "sqlite"))
    if not args.dry_run and not is_local and not args.i_am_the_owner:
        print("REFUSING: a production write is the owner's, at the keyboard. Pass "
              "--i-am-the-owner deliberately, or --dry-run.", file=sys.stderr)
        return 2

    try:
        rows, manifest, sha = load_artifact()
    except IngestRefused as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 3

    print(f"  artifact  {ART.name}  {len(rows)} rows  sha256 {sha[:16]}…  partial={manifest['partial']}")
    print(f"  outcomes  {dict(Counter(r['outcome'] for r in rows))}")

    from sqlalchemy import create_engine
    engine = create_engine(url, future=True)
    try:
        report = ingest(engine, rows, manifest, sha, dry_run=args.dry_run)
    except (IngestRefused, IngestBarFailed) as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 4

    for k, v in report.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
