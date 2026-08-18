"""D-099 + amendment 1 — the pre-registered control sample. SELECTION ONLY, no folding.

⚠⚠ TWO ARMS, and the second is why the first means anything:
  · MULTI-DOMAIN arm — >=2 UniProt `Domain` features wholly inside the V2 span.
  · SINGLE-DOMAIN arm — exactly 1, LENGTH-MATCHED. PAE rises with sequence separation in every
    structure, domain boundaries or not, so an all-multi-domain sample cannot distinguish
    *independently-positioned domains* from *residues far apart in sequence* — the two predict the
    same table. The single-domain arm supplies PAE at separation X inside one domain, which is the
    only baseline against which an inter-domain elevation means anything.

⚠ Ordered by `census_accession` ascending. ⚠⚠ NEVER by pLDDT, and the length match is on SPAN
LENGTH, never on confidence — matching on the confidence neighbour of the outcome is D-087.

⚠ Every stratum is reported, including empty ones. An absence is a category with a cause.

    python scripts/d099_control_sample.py
"""
from __future__ import annotations

import csv
import json
import pathlib
import sys
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.tranche6_domain_census import (  # noqa: E402
    UNIPROT_CACHE, bucket_domains, domain_like_features,
)

MANIFEST = REPO / "data" / "census" / "census_manifest.v7.csv"
OUT = REPO / "data" / "census" / "d099_control_sample.csv"

CONTROL_TRANCHES = ("3", "4")
PER_STRATUM = 5          # taken from each multi-domain stratum that has at least this many
N_SINGLE = 5             # the negative-control arm


def domains_inside(acc: str, s0: int, s1: int) -> int:
    doc = json.loads((UNIPROT_CACHE / f"{acc}.json").read_bytes().decode("utf-8"))
    only_domain = [f for f in domain_like_features(doc) if f.get("type") == "Domain"]
    return bucket_domains(only_domain, span_start=s0, span_end=s1).n_wholly_inside_span


def main() -> int:
    with MANIFEST.open(encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("tranche") in CONTROL_TRANCHES]

    recs = []
    for r in rows:
        try:
            n = domains_inside(r["census_accession"], int(r["span_start"]), int(r["span_end"]))
        except FileNotFoundError:
            continue
        recs.append({"acc": r["census_accession"], "tranche": r["tranche"],
                     "span_aa": int(r["span_aa"]), "n_dom": n})

    strata = Counter(x["n_dom"] for x in recs if x["n_dom"] >= 2)
    lo, hi = (min(strata), max(strata)) if strata else (0, 0)

    print("=" * 84)
    print("D-099 CONTROL SAMPLE — pre-registered selection, tranches 3-4")
    print("=" * 84)
    print("\nMULTI-DOMAIN STRATA — ⚠ every value in range reported, empty ones included")
    print("-" * 84)
    for n in range(lo, hi + 1):
        cnt = strata.get(n, 0)
        if cnt == 0:
            print(f"  {n:2d} domains : {cnt:4d}   ⚠ EMPTY — a category with a cause, not a gap "
                  f"in the enumeration")
        else:
            take = min(PER_STRATUM, cnt)
            print(f"  {n:2d} domains : {cnt:4d}   take {take}")

    multi = []
    for n in sorted(strata):
        pool = sorted((x for x in recs if x["n_dom"] == n), key=lambda x: x["acc"])
        multi.extend(pool[:PER_STRATUM])

    print(f"\n  MULTI-DOMAIN ARM: {len(multi)} folds")
    spans = [x["span_aa"] for x in multi]
    print(f"  span range: {min(spans)}-{max(spans)} aa")

    # ── the negative control: single-domain, length-matched to BRACKET the multi arm ──────────
    singles = sorted((x for x in recs if x["n_dom"] == 1), key=lambda x: x["acc"])
    in_band = [x for x in singles if min(spans) <= x["span_aa"] <= max(spans)]
    print(f"\nSINGLE-DOMAIN ARM — the negative control")
    print("-" * 84)
    print(f"  single-domain rows in tranches 3-4      : {len(singles)}")
    print(f"  of those, inside the multi arm's range  : {len(in_band)}")
    if len(in_band) < N_SINGLE:
        print(f"  ⚠ FEWER THAN {N_SINGLE} IN BAND — reported, not widened silently")

    # ⚠⚠ BRACKET, don't merely fall inside. Taking the first 5 by accession from the in-band pool
    # gave 228-359 against a multi arm of 219-435 — contained, not bracketing, and it left the
    # long tail with no baseline. The confound this arm exists to break is SEPARATION-DEPENDENT,
    # so a baseline that stops short of the longest subjects is absent exactly where it is needed.
    # Targets are evenly spaced across the multi arm's span range including both endpoints; the
    # nearest single-domain row to each target is taken, ties broken by accession ascending.
    # ⚠ The match is on SPAN LENGTH only. Never pLDDT (D-087).
    lo_s, hi_s = min(spans), max(spans)
    targets = [lo_s + (hi_s - lo_s) * i / (N_SINGLE - 1) for i in range(N_SINGLE)]
    single, used = [], set()
    for t in targets:
        pool = [x for x in in_band if x["acc"] not in used]
        if not pool:
            break
        pick = min(pool, key=lambda x: (abs(x["span_aa"] - t), x["acc"]))
        used.add(pick["acc"])
        single.append(pick)
    single.sort(key=lambda x: x["acc"])
    print(f"  bracketing targets (aa)                 : {[round(t) for t in targets]}")

    print(f"\n  SINGLE-DOMAIN ARM: {len(single)} folds")
    if single:
        ss = [x["span_aa"] for x in single]
        print(f"  span range: {min(ss)}-{max(ss)} aa   (multi arm: {min(spans)}-{max(spans)})")

    sample = [dict(x, arm="multi") for x in multi] + [dict(x, arm="single") for x in single]
    print("\n" + "=" * 84)
    print(f"TOTAL BUDGET: {len(sample)} folds  ({len(multi)} multi + {len(single)} single)")
    print("=" * 84)
    print(f"  {'acc':9s} {'arm':7s} {'tranche':>7s} {'span_aa':>8s} {'n_dom':>6s}")
    for x in sample:
        print(f"  {x['acc']:9s} {x['arm']:7s} {x['tranche']:>7s} {x['span_aa']:8d} {x['n_dom']:6d}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["acc", "arm", "tranche", "span_aa", "n_dom"])
        w.writeheader()
        w.writerows(sample)
    print(f"\nwrote {OUT}")
    print("⚠ SELECTION ONLY. No fold has run. The sample is fixed before the GPU spins.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
