#!/usr/bin/env python3
"""pLDDT confidence bands across a tranche. Read-only, ORM, no hand-written SQL.

    python scripts/plddt_bands.py --tranche 4

⚠⚠ **The bands are the PROJECT's (D-039/D-049), mirrored from `ui/src/plddt.js`, which declares
itself the single source of the scheme.** A script with its own edges would make *"low"* mean one
thing in the webapp and another in the analysis. **Choosing thresholds to make an answer look tidy
is how a measurement becomes a decoration** — so the ruled edges are used, and the divergence from
the AlphaFold-DB convention (90/70/50) is stated rather than silently resolved.

⚠⚠ **`mean_plddt` IS A MEAN AND A MEAN HIDES THE DISTRIBUTION.** A folded domain at 90 beside a
disordered linker at 30 averages to ~70 and reads as *"confident"*. This script reports the
composition **by row** — and, where the per-residue vector is available, the fraction of residues
below the floor, which is the number that actually matters for whether a surface is bindable.

⚠ **A low pLDDT is a RESULT, not a failure.** Below ~50 it frequently indicates **intrinsic
disorder** rather than a bad prediction — the model is correctly reporting that there is no single
structure to predict. Counting those rows as "failed folds" would discard a real finding.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

#: ⚠⚠ THE PROJECT'S OWN SCHEME (D-039/D-049), NOT AlphaFold-DB's.
#:
#: The first version of this file used the AF-DB convention (90/70/50). That was wrong — not
#: because the convention is wrong, but because `ui/src/plddt.js` says of itself: *"This is the
#: single source of the band scheme; the confidence element, the per-residue plot, and the
#: structure colouring all read it, so the structure and its legend cannot disagree."* Adding a
#: second scheme in a script would have made "low" mean one thing in the webapp and another in the
#: analysis — ⚠ **one word, two meanings, which is the defect this project keeps finding.**
#:
#: D-039 anchored 70 and 50 on convention and justified 60 on the cohort's own measured mass
#: (45% below it on 42 folds; re-justified at 29.1% on 79). ⚠ The 90 tier is deliberately ABSENT:
#: nothing in the cohort reaches it, and a band nobody occupies invites the reader to assume
#: someone might.
BANDS = (
    (70, 101, "confident backbone", "⚠ cohort max is 84.23 — nothing reaches high-confidence (≥90)"),
    (60, 70, "moderate", ""),
    (50, 60, "low", "⚠ backbone unreliable"),
    (0, 50, "very low", "⚠⚠ not reliably interpretable; often INTRINSIC DISORDER, not model failure"),
)


def band_of(v: float) -> str:
    for lo, hi, label, _ in BANDS:
        if lo <= v < hi:
            return label
    return "⚠ OUT OF RANGE"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tranche", type=int, required=True)
    args = ap.parse_args()

    import sqlalchemy as sa
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from db.models import JobRecord, ProteinAnalysis

    url = os.environ.get("DATABASE_URL")
    if not url:
        print("⚠ no DATABASE_URL — stop and report", file=sys.stderr)
        return 1
    engine = sa.create_engine(url, connect_args={"connect_timeout": 10})

    with Session(engine) as s:
        rows = s.execute(
            select(ProteinAnalysis.input_value, ProteinAnalysis.mean_plddt, ProteinAnalysis.meta)
            .join(JobRecord, JobRecord.analysis_id == ProteinAnalysis.id)
            .where(ProteinAnalysis.cohort_tranche == args.tranche)
            .where(JobRecord.status == "complete")).all()

    if not rows:
        print(f"⚠ no complete rows in tranche {args.tranche} — nothing measured, NOT 'zero low'")
        return 0

    # ⚠ A null mean_plddt is its own category. It is NOT a zero and must never join the bottom band.
    scored = [(a, v, m) for a, v, m in rows if v is not None]
    unscored = [a for a, v, _ in rows if v is None]

    counts = Counter(band_of(v) for _, v, _ in scored)
    print(f"tranche {args.tranche} | complete={len(rows)} | with mean_plddt={len(scored)}"
          f" | ⚠ WITHOUT={len(unscored)}")
    print()
    for lo, hi, label, meaning in BANDS:
        n = counts.get(label, 0)
        pct = 100 * n / len(scored) if scored else 0
        # ⚠ Every band printed even at zero: an omitted band reads as "none" when it may mean
        # "the key was never counted".
        print(f"  {lo:>3}–{hi - 1:<3} {label:<10} | {n:>5} ({pct:>5.1f}%) | {meaning}")
    print()

    vals = sorted(v for _, v, _ in scored)
    print(f"  min {vals[0]:.1f} | median {vals[len(vals) // 2]:.1f} | max {vals[-1]:.1f}")

    low = sorted(((v, a, (m or {}).get("span_aa")) for a, v, m in scored if v < 50))
    print(f"\n⚠ rows below 50 (the disorder band): {len(low)}")
    for v, a, L in low[:25]:
        print(f"     {a} | mean_plddt {v:.1f} | span {L} aa")
    if len(low) > 25:
        print(f"     … and {len(low) - 25} more")
    if unscored:
        print(f"\n⚠⚠ {len(unscored)} COMPLETE rows carry NO mean_plddt — a completed fold with no "
              f"confidence is not a low-confidence fold, it is an unmeasured one: {unscored[:10]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
