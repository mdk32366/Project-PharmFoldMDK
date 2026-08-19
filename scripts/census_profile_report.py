"""Compute the census structural profile over the committed artifact, and report it.

⚠⚠ WRITES NOTHING. No database, no file. `D-079` amendment 2 ruled that the profile may be BUILT;
where a computed profile is PERSISTED and how it is RENDERED are separate decisions this script
does not make. It exists so the ruling's consequences are visible as numbers before either.

⚠ It does not sort, rank or take a top-N (ruling 2), and it reports refusals as CATEGORIES beside
the values rather than dropping them (ruling 3). ⚠ The mount preconditions are printed with the
distribution, not after it — ruling 4 puts them *in the same frame*, and a report is a frame.
"""
from __future__ import annotations

import json
import pathlib
import sys
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from core.features import FEATURE_NAMES  # noqa: E402
from core.source_pin import verify_source  # noqa: E402
from core.structural_profile import (  # noqa: E402
    MOUNT_PRECONDITIONS,
    load_model,
    profile_many,
)

ART = REPO / "data" / "census" / "census_features.v1.jsonl"
MAN = REPO / "data" / "census" / "census_features.v1.manifest.json"


def main() -> int:
    manifest = json.loads(MAN.read_text(encoding="utf-8"))
    verify_source(ART, manifest["sha256"])          # ⚠ the same pin the ingest refuses on
    rows = [json.loads(l) for l in ART.read_text(encoding="utf-8").splitlines() if l.strip()]

    refused_spans = frozenset(
        r["accession"] for r in rows if r["outcome"] == "refused_span_below_floor")
    inputs = [{"accession": r["accession"],
               "features": (r.get("features") or {})} for r in rows]

    model = load_model()
    bar = "=" * 96
    print(bar)
    print("CENSUS STRUCTURAL PROFILE — D-079 amendment 1, ruled by amendment 2 (2026-08-20)")
    print(bar)
    print(f"  artifact   {ART.name}  {len(rows)} rows  sha256 {manifest['sha256'][:16]}…")
    print(f"  model      {model['name']}  run {model['ranking_run_id']}  "
          f"scorer_version {model['scorer_version']}")
    print(f"  reproduces run 2's persisted scores to "
          f"{model['reproduction_max_abs_error_vs_persisted_score']:.1e} over the 56 fit rows")
    print(f"  bar        the cohort's OBSERVED min–max (amendment 2 ruling 8)")
    print(f"  ⚠ NOT p05–p95 (fires inside the training support) and NOT ±3 sd (rests on sd_k, "
          f"which F-049 amendment 1 proves is not recoverable)")
    print()

    results = profile_many(inputs, refused_accessions=refused_spans)
    assert len(results) == len(rows), "a row was dropped — refusals are reported, never filtered"

    cats = Counter(r.refusal.category if r.is_refused else "profile_computed" for r in results)
    print(bar)
    print("THE OUTCOME, AND IT SUMS TO THE ARTIFACT")
    print(bar)
    for k, v in cats.most_common():
        print(f"    {k:32s} {v:5d}   {100*v/len(results):5.1f}%")
    print(f"    {'TOTAL':32s} {sum(cats.values()):5d}")
    computed = [r for r in results if not r.is_refused]
    refused = [r for r in results if r.is_refused]
    print(f"\n  ⚠⚠ RULING 1 AND RULING 3 ARE BOTH OPERATIVE: {len(computed)} carry a profile, "
          f"{len(refused)} carry a refusal.")

    print()
    print(bar)
    print("WHICH FEATURE PUT A ROW OUT OF RANGE — a row can fail more than one, so these do NOT sum")
    print(bar)
    per = Counter()
    for r in refused:
        for n in r.out_of_range_features:
            per[n] += 1
    ood = [r for r in refused if r.refusal.category == "refused_out_of_distribution"]
    for n in FEATURE_NAMES:
        print(f"    {n:28s} {per.get(n,0):5d}   {100*per.get(n,0)/max(len(ood),1):5.1f}% of the "
              f"{len(ood)} out-of-distribution refusals")
    dist = Counter(len(r.out_of_range_features) for r in ood)
    print("\n  how many features each refused row fails:")
    for i in sorted(dist):
        print(f"    {i} feature{'s' if i != 1 else ' '}: {dist[i]:5d}")

    if computed:
        vals = sorted(r.value for r in computed)
        n = len(vals)
        q = lambda p: vals[min(n - 1, int(p * n))]                       # noqa: E731
        print()
        print(bar)
        print("THE PROFILE'S DISTRIBUTION — a value, never an ordering (ruling 2)")
        print(bar)
        print(f"    n {n}   min {vals[0]:.4f}   p25 {q(.25):.4f}   median {q(.5):.4f}   "
              f"p75 {q(.75):.4f}   max {vals[-1]:.4f}")
        print(f"    ⚠ F-006 records the COHORT's own fitted values spanning 0.116–0.285. "
              f"This span is {vals[-1]-vals[0]:.4f} wide.")
        print("    ⚠⚠ No target is named here and none is ranked. The distribution is the claim;")
        print("       which protein sits where is a surface decision this script does not make.")

    print()
    print(bar)
    print("RULING 4 — THE MOUNT PRECONDITIONS, IN THE SAME FRAME AS THE NUMBERS")
    print(bar)
    for i, m in enumerate(MOUNT_PRECONDITIONS, 1):
        print(f"    {i}. {m}")
    print()
    print("  ⚠⚠ AND WHAT THIS IS NOT LICENSED FOR (amendment 1, unamended): not P-001, not P-002,")
    print("     not target selection, not the atlas business case. Permission to build is not")
    print("     permission to conclude.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
