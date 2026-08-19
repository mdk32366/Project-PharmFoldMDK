"""scripts/census_extract_features.py — LC: census feature extraction to an ARTIFACT.

⚠⚠ THIS WRITES A FILE, NEVER A DATABASE ROW. No engine, no session, no tunnel, no ingest.
   Ingest is a later, separate, gated step on the `GC` pattern (order §4). Not here.

⚠ Permitted by `D-079` decision 1, read and quoted rather than assumed:
     "A fold is a **measurement**; a score is an **interpretation**. D-075 protects the
      interpretation."
   The forbidden list is *"no census row scored, ranked, or ordered by suitability — no census
   path imports `core/scorer.py` or the fitter"*. Extraction does none of those, and
   `core/features.py` carries zero third-party imports and no scorer import (`D-058` dec 1,
   verified not asserted). Two of the six features ARE the confidence-distribution statistics
   decision 1 explicitly permits.

⚠ Determinism (`LA3`): `_largest_patch_fraction` iterates NO set. Its residue maps are dicts in
   PDB-file insertion order, `accessible` is a list, union-find runs in list order, and the final
   reduction is `max()` over floats where a tie cannot change the value. Deterministic by
   construction, and confirmed empirically at three `PYTHONHASHSEED` values. The seed is pinned
   and recorded in the manifest either way, because "we checked once" is not a guarantee.

Usage:
    python scripts/census_extract_features.py                 # run (resumes if partial)
    python scripts/census_extract_features.py --limit 50      # a bounded slice
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from core.features import extract_features, EXTENDED_FEATURE_NAMES, feature_version  # noqa: E402
from scripts.tranche6_domain_census import (  # noqa: E402
    UNIPROT_CACHE, domain_like_features, _coords, span_relation)

BASE = os.environ.get("PHARMFOLD_BASE", "https://pharmfoldmdk.fly.dev")
MANIFEST_CSV = REPO / "data" / "census" / "census_manifest.v7.csv"
OUT = REPO / "data" / "census" / "census_features.v1.jsonl"
OUT_MANIFEST = REPO / "data" / "census" / "census_features.v1.manifest.json"

# LC3 — every failure is a category with a cause. Never a skip, never a zero, never a blank.
OUTCOMES = (
    "ok",
    "refused_span_below_floor",   # LC4 / D-079 amendment 1 ruling 6 — F-048's engulfing set
    "structure_file_absent",
    "structure_malformed",
    "extraction_error",
)


def git_rev() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:                                        # noqa: BLE001
        return "<git rev unavailable>"


def http_get(url: str, timeout: int = 120) -> tuple[bytes | None, str | None]:
    """Returns (body, error). A 404 is an ABSENCE with a name, not an exception to swallow."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.read(), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except Exception as e:                                   # noqa: BLE001
        return None, repr(e)


def engulfing_accessions() -> set[str]:
    """F-048's set, RECOMPUTED from the cache rather than cited as a literal 58."""
    out = set()
    for r in csv.DictReader(MANIFEST_CSV.open(encoding="utf-8")):
        s0, s1 = r.get("span_start"), r.get("span_end")
        if not s0 or not s1:
            continue
        p = UNIPROT_CACHE / f"{r['census_accession']}.json"
        if not p.exists():
            continue
        doc = json.loads(p.read_text(encoding="utf-8"))
        for feat in domain_like_features(doc):
            a, b = _coords(feat)
            if a is not None and b is not None and span_relation(a, b, int(s0), int(s1)) == "engulfing":
                out.add(r["census_accession"])
                break
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--base", default=BASE)
    args = ap.parse_args()

    seed = os.environ.get("PYTHONHASHSEED")
    if seed is None:
        print("REFUSING: PYTHONHASHSEED is unset. The order requires it PINNED and recorded.\n"
              "  run:  PYTHONHASHSEED=0 python scripts/census_extract_features.py", file=sys.stderr)
        return 2

    started = dt.datetime.now(dt.timezone.utc).isoformat()
    t_start = time.perf_counter()

    rows, err = http_get(f"{args.base}/api/census")
    if rows is None:
        print(f"REFUSING: /api/census unreachable ({err})", file=sys.stderr)
        return 2
    census = json.loads(rows.decode("utf-8"))
    bmethod = {r["census_accession"]: r.get("boundary_method")
               for r in csv.DictReader(MANIFEST_CSV.open(encoding="utf-8"))}
    refused = engulfing_accessions()
    print(f"  census rows from /api/census : {len(census)}")
    print(f"  F-048 engulfing set, recomputed: {len(refused)}")

    # LC2 — RESUMABLE. Existing lines are kept; only their ids are skipped.
    done: set[int] = set()
    if OUT.exists():
        for line in OUT.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    done.add(json.loads(line)["analysis_id"])
                except Exception:                            # noqa: BLE001
                    pass
        print(f"  RESUMING: {len(done)} rows already in {OUT.name}")

    todo = [r for r in census if r["id"] not in done]
    if args.limit:
        todo = todo[:args.limit]
    print(f"  to process this pass: {len(todo)}\n")

    counts = Counter()
    for r in done:                       # resumed rows still count toward the totals
        counts["<resumed>"] += 1

    with OUT.open("a", encoding="utf-8", newline="\n") as fh:
        for i, r in enumerate(todo, 1):
            aid, acc = r["id"], r["accession"]
            rec = {"analysis_id": aid, "accession": acc, "gene": r.get("gene"),
                   "tranche": r.get("tranche"), "span_aa": r.get("span_aa"),
                   "boundary_method": bmethod.get(acc),
                   "feature_version": feature_version(), "outcome": None,
                   "features": None, "null_reasons": None, "error": None}

            if acc in refused:
                # LC4 — excluded AT COMPUTATION, not filtered at display. Nothing is computed.
                rec["outcome"] = "refused_span_below_floor"
                rec["error"] = ("F-048: the V2 span is engulfed by a larger domain; "
                                "D-079 amendment 1 ruling 6 excludes it at computation")
            else:
                pdb_b, e1 = http_get(f"{args.base}/api/analyses/{aid}/structure")
                pl_b, _e2 = http_get(f"{args.base}/api/analyses/{aid}/plddt")
                if pdb_b is None:
                    rec["outcome"] = "structure_file_absent"
                    rec["error"] = e1
                else:
                    try:
                        plddt = json.loads(pl_b.decode("utf-8")) if pl_b else None
                    except Exception as e:                   # noqa: BLE001
                        plddt = None
                        rec["error"] = f"plddt unparseable: {e!r}"
                    try:
                        text = pdb_b.decode("utf-8", "replace")
                        if not any(ln.startswith(("ATOM", "HETATM")) for ln in text.splitlines()):
                            rec["outcome"] = "structure_malformed"
                            rec["error"] = "no ATOM/HETATM records in the served file"
                        else:
                            fr = extract_features(text, plddt,
                                                  boundary_method=bmethod.get(acc),
                                                  mean_plddt=r.get("mean_plddt"))
                            rec["outcome"] = "ok"
                            rec["features"] = fr.as_extended_feature_dict()
                            rec["null_reasons"] = fr.null_reasons or {}
                    except Exception as e:                   # noqa: BLE001
                        rec["outcome"] = "extraction_error"
                        rec["error"] = repr(e)

            counts[rec["outcome"]] += 1
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            if i % 100 == 0 or i == len(todo):
                fh.flush()
                el = time.perf_counter() - t_start
                print(f"    {i:>5}/{len(todo)}  {el/60:6.1f} min elapsed  "
                      f"~{el/i*(len(todo)-i)/60:6.1f} min left   {dict(counts)}")

    ended = dt.datetime.now(dt.timezone.utc).isoformat()
    body = OUT.read_bytes()
    total_lines = sum(1 for ln in body.decode("utf-8").splitlines() if ln.strip())
    complete = total_lines == len(census)

    manifest = {
        "output": OUT.name,
        "sha256": hashlib.sha256(body).hexdigest(),
        "bytes": len(body),
        "lines": total_lines,
        "census_rows_expected": len(census),
        "partial": not complete,                   # LC2 — never mistaken for a complete one
        "code_revision": git_rev(),
        "feature_version": feature_version(),
        "PYTHONHASHSEED": seed,
        "started_utc": started,
        "ended_utc": ended,
        "base_url": args.base,
        "outcome_counts_this_pass": dict(counts),
        "outcomes_vocabulary": list(OUTCOMES),
        "key": ("one line per row of /api/census (analysis_id = protein_analyses.id); "
                "counts sum to census_rows_expected only when partial is false"),
        "wrote_database_rows": False,
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
    print(f"\n  manifest -> {OUT_MANIFEST.name}")
    print(f"  lines {total_lines}/{len(census)}   partial={not complete}")
    print(f"  sha256 {manifest['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
