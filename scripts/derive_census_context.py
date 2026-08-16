#!/usr/bin/env python3
"""Re-derive every census context artifact. ⚠ Run this after ANY manifest revision.

    python scripts/derive_census_context.py --check     # report freshness, derive nothing
    python scripts/derive_census_context.py

⚠ **One command, because two commands is one command someone forgets.** `span_segments.csv` and
`census_labels.csv` are both derived from `census_manifest.v7.csv`, and a revision that refreshed
only one would leave the surface half-current with nothing saying which half.

⚠ **`--check` is the cheap habit.** It fetches nothing, derives nothing and prints a verdict per
artifact, so "are these current?" never requires re-running a derivation to find out.

⚠ **Nothing here auto-runs on read.** A surface that silently re-derived would hand a reader
different numbers on two loads with nothing saying why, and would do unrequested work inside a
request. The API **refuses** stale data instead; this is how a human clears it.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from core.derived_freshness import FRESH, check  # noqa: E402

CENSUS = REPO / "data" / "census"
MANIFEST = CENSUS / "census_manifest.v7.csv"
#: (provenance stem, script) — ⚠ the list is the contract; adding a derivation means adding it here.
DERIVATIONS = (("span_segments", "span_segments.py"), ("census_labels", "census_labels.py"))


def report() -> bool:
    all_fresh = True
    for stem, _script in DERIVATIONS:
        verdict, note = check(CENSUS / f"{stem}.provenance.json", MANIFEST)
        mark = "OK  " if verdict == FRESH else "⚠ ⚠"
        print(f"  {mark} {stem:<16} | {verdict:<22} | {note}")
        all_fresh = all_fresh and verdict == FRESH
    return all_fresh


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report freshness and derive nothing")
    args = ap.parse_args()

    print(f"manifest | {MANIFEST.name}")
    fresh = report()
    if args.check:
        # ⚠ Non-zero when stale, so CI or a shell `&&` can act on it rather than reading prose.
        print("\nall fresh" if fresh else "\n⚠⚠ AT LEAST ONE DERIVATION IS OUT OF DATE — re-run "
                                          "this script without --check")
        return 0 if fresh else 1

    for _stem, script in DERIVATIONS:
        print(f"\n── {script}")
        r = subprocess.run([sys.executable, str(REPO / "scripts" / script)], cwd=REPO)
        if r.returncode != 0:
            # ⚠ STOP. Continuing would leave the set half-derived, which is worse than not starting.
            print(f"⚠⚠ {script} FAILED (exit {r.returncode}) — stopping. The derivations are now "
                  f"in a MIXED state; re-run once the failure is fixed.", file=sys.stderr)
            return r.returncode

    print("\n── re-checking")
    return 0 if report() else 1


if __name__ == "__main__":
    raise SystemExit(main())
