"""Task C of ORDERS-Code-2026-08-18 — the in-context multi-domain population.

⚠ COUNTS ONLY. The order says *"Do not run the comparison"* — this establishes whether the
population exists at all.

⚠⚠ CITATION CORRECTED. This file and the order both said the comparison "is a `D-095` decision".
When the order was written `D-095` was the next free integer; it is now **the tranche-6 tiling
design document**, which says nothing about a PAE comparison. **The reference resolved to a real
entry with the wrong content — worse than an unresolved one, and invisible to the citation
invariant, which checks that a reference RESOLVES and cannot check that it resolves to the right
thing.** The comparison needs its own entry; `D-101` is the next free integer at the time of
writing, and it must be confirmed against the live log before it is claimed.

⚠ SAME CODE PATH AS A1, deliberately. `bucket_domains` is imported from
`scripts/tranche6_domain_census.py` rather than reimplemented — a second bucketer would be two
paths to one quantity, which is the defect this project keeps rediscovering.

`D-099` pre-registers the control's eligibility as **tranche 3–4 rows with ≥2 UniProt `Domain`
features wholly inside the V2 span**, ordered by `census_accession` ascending, and ⚠⚠ **never
ordered or filtered by pLDDT** — selecting on the confidence neighbour of the outcome would
choose the control on the variable under test.

    python scripts/taskc_multidomain_population.py
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
    UNIPROT_CACHE,
    bucket_domains,
    domain_like_features,
)

MANIFEST = REPO / "data" / "census" / "census_manifest.v7.csv"

#: The order's population: the folded census, tranches 1–4.
FOLDED_TRANCHES = ("1", "2", "3", "4")
#: D-099's eligible subset for the control.
CONTROL_TRANCHES = ("3", "4")

#: ⚠ `Domain` only, not `Domain`+`Repeat`. D-099 says "UniProt `Domain` features" and the order
#: says the same. The wider set is reported alongside so the choice is visible, never substituted.
def counts_for(acc: str, s0: int, s1: int):
    doc = json.loads((UNIPROT_CACHE / f"{acc}.json").read_bytes().decode("utf-8"))
    feats = domain_like_features(doc)
    only_domain = [f for f in feats if f.get("type") == "Domain"]
    return (bucket_domains(only_domain, span_start=s0, span_end=s1),
            bucket_domains(feats, span_start=s0, span_end=s1))


def main() -> int:
    with MANIFEST.open(encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("tranche") in FOLDED_TRANCHES]

    print("=" * 88)
    print("TASK C — the in-context multi-domain population")
    print(f"artifact: {MANIFEST.name} ⋈ spancache   key: one row per census_accession")
    print(f"population scanned: {len(rows):,} rows (tranches {', '.join(FOLDED_TRANCHES)})")
    print("=" * 88)

    recs = []
    missing = 0
    for r in rows:
        acc = r["census_accession"]
        try:
            dom, wide = counts_for(acc, int(r["span_start"]), int(r["span_end"]))
        except FileNotFoundError:
            missing += 1
            continue
        recs.append({
            "acc": acc, "tranche": r["tranche"], "span_aa": int(r["span_aa"]),
            "n_domain_inside": dom.n_wholly_inside_span,
            "n_domainlike_inside": wide.n_wholly_inside_span,
        })

    if missing:
        print(f"⚠ {missing} rows not in the spancache — a category, reported not dropped")

    multi = [x for x in recs if x["n_domain_inside"] >= 2]
    print(f"\n⚠ THE HEADLINE: {len(multi):,} of {len(recs):,} folded rows carry >=2 UniProt "
          f"`Domain` features wholly inside the V2 span ({100*len(multi)/len(recs):.1f}%)")
    multi_wide = [x for x in recs if x["n_domainlike_inside"] >= 2]
    print(f"  (with `Repeat` included as well: {len(multi_wide):,} — reported so the choice of "
          f"`Domain`-only is visible, not substituted)")

    print("\nBY DOMAIN COUNT (Domain only, wholly inside the span)")
    print("-" * 88)
    c = Counter(x["n_domain_inside"] for x in recs)
    for n in sorted(c):
        bar = "#" * min(60, c[n] // 20)
        mark = "  <- eligible" if n >= 2 else ""
        print(f"  {n:3d} domains : {c[n]:5,d}{mark}  {bar}")

    print("\nBY TRANCHE — eligible rows (>=2 domains inside the span)")
    print("-" * 88)
    print(f"  {'tranche':>8s} {'rows':>7s} {'eligible':>9s} {'%':>7s}")
    for t in FOLDED_TRANCHES:
        sub = [x for x in recs if x["tranche"] == t]
        el = [x for x in sub if x["n_domain_inside"] >= 2]
        pct = 100 * len(el) / len(sub) if sub else 0
        star = "  <- D-099 eligible tranche" if t in CONTROL_TRANCHES else ""
        print(f"  {t:>8s} {len(sub):7,d} {len(el):9,d} {pct:6.1f}%{star}")

    print("\nBY SPAN LENGTH — eligible rows only")
    print("-" * 88)
    bands = [(1, 50), (51, 149), (150, 300), (301, 439), (440, 10**9)]
    for lo, hi in bands:
        sub = [x for x in multi if lo <= x["span_aa"] <= hi]
        label = f"{lo}-{hi}" if hi < 10**9 else f"{lo}+"
        print(f"  {label:>10s} aa : {len(sub):5,d}")

    # ── D-099's pre-registered control sample ────────────────────────────────────────────────
    eligible = sorted((x for x in multi if x["tranche"] in CONTROL_TRANCHES),
                      key=lambda x: x["acc"])
    print("\n" + "=" * 88)
    print("D-099 CONTROL POOL — tranches 3-4, >=2 Domain inside span, sorted by accession")
    print("⚠ NOT sorted or filtered by pLDDT. That would select on the variable under test.")
    print("=" * 88)
    print(f"  eligible pool: {len(eligible):,} rows")
    strata = Counter(x["n_domain_inside"] for x in eligible)
    print("  by domain-count stratum:")
    for n in sorted(strata):
        print(f"    {n:3d} domains : {strata[n]:4d}")
    print("\n  first 12 by accession (the order a budgeted sample would take):")
    for x in eligible[:12]:
        print(f"    {x['acc']:8s} tranche={x['tranche']} span={x['span_aa']:4d} "
              f"domains_inside={x['n_domain_inside']}")

    print("\n⚠ This task COUNTS. It does not run the comparison, which needs its own log entry")
    print("  (⚠ NOT D-095 — that integer is now the tranche-6 tiling document; see the header).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
