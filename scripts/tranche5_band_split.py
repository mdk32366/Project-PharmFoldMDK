"""Task D of ORDERS-Code-2026-08-18 — re-derive the scoping counts, independently.

⚠ DELIBERATELY A SECOND PATH. `scripts/census_manifest.py` already computes a band; this does not
call it. The order requires an independent re-derivation because **two paths compared once** is the
remedy for this project's most-repeated defect, and **two paths never compared** is the defect.
A disagreement here is a DEFECT REPORT, not a rounding difference.

    python scripts/tranche5_band_split.py

⚠⚠ The 441 / 851 / 1,027 edges are load-bearing and `<` for `<=` is invisible in a total: 776 stays
776 however rows move between bands. `tests/test_tranche5_band_split.py` moves each edge by one
residue and asserts the row changes band.
"""
from __future__ import annotations

import csv
import pathlib
from typing import Any, Iterable

REPO = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = REPO / "data" / "census" / "census_manifest.v7.csv"
LABELS = REPO / "data" / "census" / "census_labels.csv"

TRAINED_CONTEXT = 1026

#: The ten named in D-091 ruling 3.
D091_TEN = {"Q14517", "Q9NYQ8", "Q8TDW7", "Q6V0I7", "Q07954",
            "Q9NZR2", "P98164", "O75445", "Q8WXG9", "Q86WI1"}
#: The three mucins named in CLOSEOUT-2026-08-17 §4.
MUCINS = {"Q8WXI7", "Q9UKN1", "Q685J3"}

BANDS = ("at_or_below_local", "441_850", "851_1026", "past_context")

#: The Planner's measurement, 2026-08-18, transcribed for comparison — NOT used to compute anything.
PLANNER = {
    "tranche5_total": 776,
    "441_850": 566,
    "851_1026": 69,
    "past_context": 141,
    "of_141_named_d091": 10,
    "of_141_mucins": 3,
    "of_141_named_nowhere": 128,
    "of_141_1027_2000": 102,
    "distinct_boundary_method": 1,
}


def band_of(span_aa: Any) -> str:
    """The band a span length falls in. ⚠ Raises on anything unparseable — an unreadable length
    is not a band, and bucketing it silently would place a row in a population it was never
    measured into."""
    n = int(span_aa)                     # raises ValueError/TypeError, deliberately
    if n <= 440:
        return "at_or_below_local"
    if n <= 850:
        return "441_850"
    if n <= TRAINED_CONTEXT:
        return "851_1026"
    return "past_context"


def split(rows: Iterable[dict]) -> dict[str, list[dict]]:
    """Partition rows by band. Every row lands in exactly one bucket."""
    out: dict[str, list[dict]] = {b: [] for b in BANDS}
    for r in rows:
        out[band_of(r["span_aa"])].append(r)
    return out


def main() -> int:
    with MANIFEST.open(encoding="utf-8") as fh:
        manifest = list(csv.DictReader(fh))
    genes = {}
    with LABELS.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            genes[r["census_accession"]] = r["gene"]

    t5 = [r for r in manifest if r.get("tranche") == "5"]
    bands = split(t5)
    past = bands["past_context"]
    named = {r["census_accession"] for r in past} & D091_TEN
    mucin = {r["census_accession"] for r in past} & MUCINS
    nowhere = [r for r in past
               if r["census_accession"] not in D091_TEN and r["census_accession"] not in MUCINS]
    only_just = [r for r in past if int(r["span_aa"]) <= 2000]
    methods = sorted({r["boundary_method"] for r in manifest})

    mine = {
        "tranche5_total": len(t5),
        "441_850": len(bands["441_850"]),
        "851_1026": len(bands["851_1026"]),
        "past_context": len(past),
        "of_141_named_d091": len(named),
        "of_141_mucins": len(mucin),
        "of_141_named_nowhere": len(nowhere),
        "of_141_1027_2000": len(only_just),
        "distinct_boundary_method": len(methods),
    }

    print("=" * 78)
    print("TASK D — independent re-derivation vs the Planner's measurement")
    print(f"artifact: {MANIFEST.name}   key: one row per census_accession")
    print("=" * 78)
    print(f"  {'quantity':28s} {'mine':>8s} {'planner':>9s}  verdict")
    print("  " + "-" * 62)
    defects = []
    for k, v in mine.items():
        p = PLANNER[k]
        ok = v == p
        if not ok:
            defects.append((k, v, p))
        print(f"  {k:28s} {v:8,d} {p:9,d}  {'agree' if ok else '⚠ DISAGREE'}")

    print()
    print(f"  boundary_method values present: {methods}")
    print(f"  manifest rows total           : {len(manifest):,}")
    print(f"  at_or_below_local in tranche 5: {len(bands['at_or_below_local'])}")

    if defects:
        print("\n⚠⚠ DISAGREEMENT IS A DEFECT REPORT, NOT A ROUNDING DIFFERENCE:")
        for k, v, p in defects:
            print(f"    {k}: mine={v} planner={p}")
        return 1

    print("\n✓ every quantity reconciles. Two paths, compared once, recorded.")
    print("⚠ Reconciling does NOT make either path correct — it makes them the same. Both could")
    print("  share an assumption; what is excluded is that one of them slipped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
