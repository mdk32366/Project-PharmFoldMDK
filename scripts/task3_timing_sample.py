#!/usr/bin/env python3
"""Task 3 — select the 20-fold stratified timing sample, and project the campaign from it.

    python scripts/task3_timing_sample.py --select              # the 20, with band weights
    python scripts/task3_timing_sample.py --project timings.csv # band-weighted projection

⚠⚠ THE PROJECTION IS BAND-WEIGHTED AND NEVER A SINGLE TOTAL, AND THAT IS THE WHOLE POINT.
The Planner's earlier ~22-hour estimate was **wrong by an order of magnitude** because it assumed
440-aa folds at ~30 s. The measured median span is **53 aa**, and fold time scales steeply with
length, so a mean-of-the-sample multiplied by 2,691 is the same error in a new costume: the sample
is stratified (4 per band) while the population is NOT (130 / 395 / 1,101 / 600 / 465).

  ⚠ A sample mean answers *"how long does a fold in my sample take"*.
  ⚠ The population needs *"how long does a fold in EACH BAND take, times how many are in it"*.

So the projection prints per-band time AND per-band n AND each band's share of the total, and the
total is presented as the SUM OF THE BANDS rather than as a figure in its own right. ⚠ It is
auditable by construction: a reader can recompute any band from the two numbers beside it.
"""

from __future__ import annotations

import argparse
import collections
import csv
import random
import sys
from typing import Optional

# ⚠⚠ BAND 5 IS 251-384, NOT 251-439, AND THE DIFFERENCE IS A CARD LIMIT.
# F-062: envelopes are CARD-BOUND. F-063: this host reached highest_ok=384 and
# BUGCHECKED before 392 was written. F-064: post-fold headroom collapse. Both OPEN,
# and scripts/rb_local_tile_folds.py caps at L<=384 on exactly that evidence.
# ⚠ 385-439 is a NAMED EXCLUDED CATEGORY WITH A CAUSE (D-016), never a low
# number and never folded into band 5. A band labelled 251-439 in the key while
# holding only 251-384 in the data is F-047 manufactured by a band definition.
BANDS = [(1, 10), (11, 30), (31, 100), (101, 250), (251, 384)]
EXCLUDED = (385, 439)
EXCLUDED_CAUSE = ("exceeds the 384 aa envelope measured safe on this card "
                  "(F-062 card-bound, F-063 host bugcheck at 392, F-064 "
                  "headroom collapse; all OPEN). Not folded locally.")
PER_BAND = 4                      # 5 bands x 4 = the 20 the order specifies
MANIFEST = "data/census/census_manifest.v7.csv"


def band_of(span: int) -> Optional[str]:
    for lo, hi in BANDS:
        if lo <= span <= hi:
            return f"{lo}-{hi}"
    return None


def excluded_rows() -> list[dict]:
    """The 385-439 category: named, counted, and never projected over."""
    out = []
    for r in csv.DictReader(open(MANIFEST, encoding="utf-8")):
        if str(r.get("tranche")) not in {"1", "2", "3", "4"} or not r.get("span_aa"):
            continue
        span = int(float(r["span_aa"]))
        if EXCLUDED[0] <= span <= EXCLUDED[1]:
            out.append({"accession": r["census_accession"], "span": span})
    return out


def population() -> list[dict]:
    rows = []
    for r in csv.DictReader(open(MANIFEST, encoding="utf-8")):
        if str(r.get("tranche")) not in {"1", "2", "3", "4"} or not r.get("span_aa"):
            continue
        span = int(float(r["span_aa"]))
        b = band_of(span)
        if b:
            rows.append({"accession": r["census_accession"], "span": span, "band": b,
                         "tranche": int(r["tranche"])})
    return rows


def select(seed: int = 20260911) -> list[dict]:
    pop = population()
    by_band = collections.defaultdict(list)
    for r in pop:
        by_band[r["band"]].append(r)
    rng = random.Random(seed)
    out = []
    for lo, hi in BANDS:
        b = f"{lo}-{hi}"
        out += rng.sample(by_band[b], min(PER_BAND, len(by_band[b])))
    return out


def report_selection() -> int:
    pop = population()
    counts = collections.Counter(r["band"] for r in pop)
    sample = select()
    exc = excluded_rows()
    print(f"foldable population (tranches 1-4, span <= 384): {len(pop)}")
    print(f"EXCLUDED 385-439: {len(exc)} rows")
    print(f"  cause: {EXCLUDED_CAUSE}")
    _b5 = len([r for r in pop if r["band"] == "251-384"])
    print(f"  {len(exc) / (len(pop) + len(exc)):.2%} of the 2,691 tranche 1-4 rows, "
          f"and {len(exc) / (_b5 + len(exc)):.1%} of the OLD band 5 (251-439).")
    print()
    print(f"{'band':<10}{'population n':>14}{'sampled':>9}{'sampling rate':>15}")
    for lo, hi in BANDS:
        b = f"{lo}-{hi}"
        n = counts[b]
        k = sum(1 for r in sample if r["band"] == b)
        print(f"{b:<10}{n:>14}{k:>9}{k / n:>14.2%}")
    print(f"{'TOTAL':<10}{len(pop):>14}{len(sample):>9}")
    print("\nWARN the sampling rate is NOT uniform across bands - that is deliberate, and it is")
    print("     exactly why a sample mean must never be multiplied by the population total.\n")

    print(f"{'accession':<12}{'span':>6}{'band':>10}{'tranche':>9}")
    for r in sorted(sample, key=lambda r: r["span"]):
        print(f"{r['accession']:<12}{r['span']:>6}{r['band']:>10}{r['tranche']:>9}")

    tiny = [r for r in sample if r["span"] <= 3]
    print()
    if tiny:
        print(f"WARN {len(tiny)} of the 20 fall in spans 1-3: "
              + ", ".join(f"{r['accession']}({r['span']}aa)" for r in tiny))
        print("     A re-fold of a 1-3 residue span tests whether the pipeline should be folding")
        print("     these at all. Those census pages already render an EMPTY viewer (measured")
        print("     2026-09-11: spans 1 and 3 empty, 8 and 24 render), so what Run 2 produces for")
        print("     them is worth reading before the campaign, not after.")
    else:
        print("no sampled span falls in 1-3; the smallest is "
              f"{min(r['span'] for r in sample)} aa")
    return 0


def project(timings_csv: str) -> int:
    """Band-weighted projection from measured `(accession, span_aa, wall_seconds)` rows."""
    measured = collections.defaultdict(list)
    for r in csv.DictReader(open(timings_csv, encoding="utf-8")):
        span = int(float(r["span_aa"]))
        b = band_of(span)
        if b:
            measured[b].append(float(r["wall_seconds"]))

    counts = collections.Counter(r["band"] for r in population())
    missing = [f"{lo}-{hi}" for lo, hi in BANDS if not measured.get(f"{lo}-{hi}")]
    if missing:
        print(f"REFUSING: no measurement for band(s) {missing}. A projection over an unmeasured",
              file=sys.stderr)
        print("band would be an estimate wearing a measurement's clothes.", file=sys.stderr)
        return 1

    print(f"{'band':<10}{'pop n':>8}{'measured':>10}{'mean s':>10}{'band hours':>12}{'share':>9}")
    total_s = 0.0
    per_band = []
    for lo, hi in BANDS:
        b = f"{lo}-{hi}"
        vals = measured[b]
        mean = sum(vals) / len(vals)
        secs = mean * counts[b]
        total_s += secs
        per_band.append((b, counts[b], len(vals), mean, secs))
    for b, n, k, mean, secs in per_band:
        print(f"{b:<10}{n:>8}{k:>10}{mean:>10.1f}{secs / 3600:>12.2f}{secs / total_s:>8.1%}")
    print(f"\nTOTAL = the SUM OF THE BANDS above: {total_s / 3600:.2f} hours "
          f"over {sum(counts[f'{lo}-{hi}'] for lo, hi in BANDS)} folds")
    print("WARN recompute any band as (mean s) x (pop n) / 3600. The total is not a figure in its")
    print("     own right and must not be quoted without the table that produced it.")
    naive = (sum(sum(v) for v in measured.values()) / sum(len(v) for v in measured.values())) * \
        sum(counts.values()) / 3600
    print(f"\nWARN the NAIVE sample-mean projection would read {naive:.2f} hours "
          f"({naive / (total_s / 3600):.1f}x the band-weighted figure).")
    print("     That gap is the error the band weights exist to prevent.")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="python scripts/task3_timing_sample.py")
    ap.add_argument("--select", action="store_true", help="print the stratified 20 and the weights")
    ap.add_argument("--project", metavar="TIMINGS_CSV",
                    help="band-weighted projection from measured wall times")
    args = ap.parse_args(argv)
    if args.project:
        return project(args.project)
    if args.select:
        return report_selection()
    ap.print_help()
    return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
