#!/usr/bin/env python3
"""Census span pull + cost split (ORDERS-Code-2026-08-04-surfaceome-spans-v2 §3).

    python scripts/census_spans.py --map data/census/accession_map.csv \
                                   --source data/census/membraneome-reconstructed-2026-08-04.csv \
                                   --run-date 2026-08-04 \
                                   --cache data/census/uniprot_cache \
                                   --out  data/census/span_histogram.csv

Takes Task B's `accession_map.csv`, pulls ECD spans from UniProt (rate-limited and
disk-cached — thousands of requests, and a re-run reads the cache), feeds them to
`core.census.census_split`, and writes a histogram that **names the ceiling recipe
it was computed under and the date its spans were fetched.**

⚠ IT STARTS FROM TASK A/B OUTPUTS AND DOES NOT RE-DERIVE THEM. v2 exists because
two orders both claimed the download, the hashing and the counts — two paths to
one quantity, never compared. Acquisition and identity belong to the
scale-readiness order. **This script refuses to run without them rather than
improvising a substitute**, which is the same refusal in executable form.

⚠ WHAT IT MAY CLAIM (v2 §4)
  ✅ Cost: "of the N rows on this list, M fall inside the measured local envelope
     at (int8, chunk 64); N-M need rented compute; K exceed every single-card
     ceiling; U were unresolvable identifiers." Dated, recipe-named, derived.
  ✅ Reproducibility: "M of these folds are reproducible on a consumer 8 GB GPU
     with no cloud spend."
  ❌ NOT licensed: coupling foldability to suitability · any census filtered by
     affordability · any statement about how many rows are *good targets*. This
     measures sequence length and nothing else.

⚠ A large unfoldable fraction is a FINDING, not a failure — a measured limit of
the method at census scale, belonging in the paper's limitations at full strength.

⟡ The annex is not the census (F-011). SURFY-negative rows are ingested and
flagged, never ranked. Pass `--annex-column` so they are counted as their own
label; a cost figure that silently merges annex and census members is wrong in
both directions.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.census import CATEGORIES, census_split, describe_split  # noqa: E402
from core.manifest import LOCAL_CEILING  # noqa: E402
from scripts.ecd_lengths import fetch_cached, parse, read_accession_map  # noqa: E402


def _require(path: Path, what: str, owner: str) -> None:
    """Refuse to run on a missing input instead of improvising one.

    The failure this prevents is not a crash — it is a plausible-looking histogram
    computed over whatever happened to be lying around, with no way to tell from
    the artifact that its inputs were not the ones the order named.
    """
    if not path.exists():
        raise SystemExit(
            f"MISSING INPUT: {what}\n"
            f"  expected at : {path}\n"
            f"  produced by : {owner}\n"
            f"  This script starts from that order's outputs and does not re-derive them\n"
            f"  (surfaceome-spans-v2 §1, §5). Run it first; do not substitute another file."
        )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--map", default="data/census/accession_map.csv",
                    help="Task B output: entry name -> accession, with status")
    ap.add_argument("--cache", default="data/census/uniprot_cache",
                    help="disk cache for raw UniProt JSON; a re-run reads it")
    ap.add_argument("--out", default="data/census/span_histogram.csv")
    ap.add_argument("--source", required=True,
                    help="the artifact the identifiers came from; named AND sha256-hashed into "
                         "the histogram. NO DEFAULT, by ruling (RULINGS-2026-08-04-F016 §3): a "
                         "default naming a file that does not exist silently changes source the "
                         "day that file appears, with no diff and no signal; a default naming the "
                         "reconstruction launders provenance the same way. No implicit source.")
    ap.add_argument("--run-date", required=True,
                    help="date the spans were fetched (YYYY-MM-DD), recorded in the artifact")
    ap.add_argument("--annex-column", default=None,
                    help="column in the map marking SURFY-negative annex rows (F-011); "
                         "counted separately, never merged into the census")
    ap.add_argument("--limit", type=int, default=None, help="stop after N rows (smoke runs)")
    args = ap.parse_args(argv)

    map_path = Path(args.map)
    _require(map_path, "accession_map.csv (Task B)", "ORDERS-Code-2026-08-04-b-scale-readiness §2")

    # Provenance travels with the result, not with the invocation (RULINGS-2026-08-04-F016 §3).
    # Recording the path alone would let two different files answer to one name across runs.
    source_path = Path(args.source)
    _require(source_path, "the artifact named by --source", "RULINGS-2026-08-04-F016 §3")
    source_sha256 = hashlib.sha256(source_path.read_bytes()).hexdigest()
    print(f"source {source_path} sha256={source_sha256}", file=sys.stderr)

    rows = read_accession_map(str(map_path))
    if args.limit:
        rows = rows[:args.limit]
    print(f"read {len(rows)} rows from {map_path}", file=sys.stderr)

    census_rows, annex_rows = [], []
    for i, row in enumerate(rows, 1):
        span = None
        if row["id_status"] == "resolved" and row["accession"]:
            try:
                data = fetch_cached(row["accession"], args.cache)
                span = parse(row["accession"], "", data).largest_span
            except Exception as e:                      # noqa: BLE001
                # A fetch failure is an UNKNOWN, not a zero and not a drop.
                row = {**row, "id_status": "unresolved", "fetch_error": str(e)[:120]}
        out_row = {**row, "span_aa": span}
        (annex_rows if (args.annex_column and str(row.get(args.annex_column, "")).strip()
                        in ("1", "true", "True", "negative")) else census_rows).append(out_row)
        if i % 200 == 0:
            print(f"  {i}/{len(rows)}", file=sys.stderr)

    census_counts = census_split(census_rows)
    annex_counts = census_split(annex_rows) if annex_rows else None

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["# source", args.source])
        w.writerow(["# source_sha256", source_sha256])
        w.writerow(["# run_date", args.run_date])
        w.writerow(["# ceiling_hardware", LOCAL_CEILING.hardware])
        w.writerow(["# ceiling_dtype", LOCAL_CEILING.dtype])
        w.writerow(["# ceiling_chunk_size", LOCAL_CEILING.chunk_size])
        w.writerow(["# ceiling_local_bound", LOCAL_CEILING.local_bound])
        w.writerow(["# ceiling_rental_bound", LOCAL_CEILING.rental_bound])
        w.writerow(["# unstable_band", LOCAL_CEILING.unstable_band])
        w.writerow(["set", "category", "count"])
        for cat in CATEGORIES:
            w.writerow(["census", cat, census_counts[cat]])
        if annex_counts:
            for cat in CATEGORIES:
                w.writerow(["annex", cat, annex_counts[cat]])

    print("\n=== CENSUS ===")
    print(describe_split(census_counts, source=args.source, source_date=args.run_date))
    if annex_counts:
        print("\n=== ANNEX (SURFY-negative, F-011 — ingested and flagged, NEVER ranked) ===")
        print(describe_split(annex_counts, source=args.source, source_date=args.run_date))
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
