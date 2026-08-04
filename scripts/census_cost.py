#!/usr/bin/env python3
"""Report the cost split for an arbitrary census of ECD spans (D-077 decision 6).

    python scripts/census_cost.py --spans 248,350,441,621,2491
    python scripts/census_cost.py --file spans.txt

Answers "what would a census of N targets cost?" WITHOUT folding anything, from
sequence length alone, at the recipe the local ceiling was measured under.

⚠ THREE THINGS THIS SCRIPT WILL NOT DO, and one it will (D-077 decision 1):

  1. It does not filter. Every span you hand it is counted; unaffordable targets
     stay in the census, flagged. A census filtered by affordability is a census
     of our budget, biased by length — the F-009 error one level out.
  2. It says nothing about whether a target is a good ADC target. This is a
     cost / tractability / reproducibility axis and nothing else.
  3. Its numbers are not a substitute for the live endpoints. For any claim that
     reaches a surface, a deck, or the paper, the cohort counts re-derive from
     `/api/coverage` and `/api/analyses` (D-050). `data/cohort_82_ecd.csv` is a
     2026-07-21 snapshot and 13 of its 82 rows carry an empty `largest_span_aa`.

  What it legitimately licenses: "of these N targets, M fold at zero marginal cost
  on an 8 GB consumer card; N-M need rented compute" — dated, and carrying the
  recipe, which `--describe` prints.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.foldability import LOCAL, OVER_CEILING, RENTAL, describe, split  # noqa: E402


def _read_spans(args) -> tuple[list[int], list[str]]:
    """Returns (numeric spans, unparseable tokens). Unparseable is not dropped
    silently — an unmeasured target is reported as unknown, never bucketed."""
    if args.spans:
        tokens = [t.strip() for t in args.spans.replace(",", " ").split() if t.strip()]
    elif args.file:
        text = Path(args.file).read_text(encoding="utf-8")
        tokens = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith("#")]
    else:
        raise SystemExit("provide --spans or --file")

    spans, unknown = [], []
    for tok in tokens:
        try:
            spans.append(int(tok))
        except ValueError:
            unknown.append(tok)
    return spans, unknown


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--spans", help="comma- or space-separated ECD span lengths")
    src.add_argument("--file", help="file of span lengths, one per line")
    ap.add_argument("--describe", action="store_true", help="print the ceiling and its recipe, then exit")
    args = ap.parse_args(argv)

    if args.describe:
        print(describe())
        return 0

    spans, unknown = _read_spans(args)
    counts = split(spans)
    total = sum(counts.values())

    print(f"\nCeiling: {describe()}\n")
    print(f"  {LOCAL:<13} {counts[LOCAL]:>4}   zero marginal cost (consumer 8 GB card)")
    print(f"  {RENTAL:<13} {counts[RENTAL]:>4}   needs rented compute")
    print(f"  {OVER_CEILING:<13} {counts[OVER_CEILING]:>4}   folds on no single card as one sequence")
    print(f"  {'-' * 13} {'-' * 4}")
    print(f"  {'measured':<13} {total:>4}")

    if unknown:
        # Reported, never dropped: an unmeasured span has no envelope, and
        # counting it as affordable is how a cost estimate becomes a fiction.
        print(f"\n  ** {len(unknown)} span(s) unmeasured and therefore UNCLASSIFIED: "
              f"{', '.join(unknown[:10])}{' ...' if len(unknown) > 10 else ''}")
        print("    These stay in the census. They are not affordable-by-default.")

    if total:
        print(f"\n  {counts[LOCAL]}/{total} reproducible with no cloud spend at this recipe.")
    print("\n  ** Not a suitability axis. Not a census filter. For any published count, "
          "re-derive from /api/coverage (D-050).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
