"""RA2 — the per-tile manifest across the 141. Cache-only, no GPU, no fold.

⚠ A TILE IS ONE MERGED RUN, not a cut of an oversized run. Cutting FAT4/FAT1 this
pass would fail two-path against `data/census/tranche6_runs.csv`. Interior cuts
stay RD2. Runs past `tile_max_aa = 1026` (D-104) are emitted and `unroutable`,
not folded, not dropped.

⚠ Same inputs / merge / straddle as `scripts/tranche6_runs.py`. That script and
its CSV bytes are not this file's to change. `merge()` is imported from
`scripts/tranche6_domain_survey.py` (abutting OR overlapping: `start <= prev_end + 1`).
`domain_intervals(..., straddle="drop")` is the construction two-path compares.

⚠ RA3 / F-061: `F-059` is recorded on the tile as `f059_peak_gib`. It is a law,
not a measurement of the case. `preflight` is called with `requirement_mib=None`
and still returns `refused_no_measurement`. The fold loop still does not consult
the guard (RB, not this pass; F-049).

    python scripts/tranche6_tiles.py
"""
from __future__ import annotations

import csv
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from core.vram_guard import (  # noqa: E402
    REFUSED_NO_MEASUREMENT,
    f059_peak_gib,
    preflight,
)
from scripts.tranche6_domain_census import (  # noqa: E402
    UNIPROT_CACHE,
    domain_intervals,
    past_context_rows,
)
from scripts.tranche6_domain_survey import merge  # noqa: E402
from scripts.tranche6_runs import classify_regime  # noqa: E402

TRAINED_CONTEXT = 1026
TILE_MAX_AA = 1026
ROUTE_AT = 440
RULING = "D-104"
TILE_CUT_KIND = "whole_run"
MERGE_RULE = "abutting_or_overlapping"
STRADDLE_HANDLING = "drop"
GAP_TOLERANCE = "0"

LABELS = REPO / "data" / "census" / "census_labels.csv"
RUNS = REPO / "data" / "census" / "tranche6_runs.csv"
OUT = REPO / "data" / "census" / "tranche6_tiles.csv"

#: Fold loop still does not consult the guard. RA2 is cache-only: no live CUDA.
PREFLIGHT_WHY = (
    "fold loop does not consult the guard (RB, not this pass; F-049); "
    "F-059 is a law, not a measurement of this case (F-061); "
    "requirement_mib=None; RA2 cache-only, no live CUDA"
)

FIELDNAMES = (
    "census_accession",
    "gene",
    "tile_index",
    "start",
    "end",
    "length",
    "tile_cut_kind",
    "merge_rule",
    "straddle_handling",
    "gap_tolerance",
    "protein_regime",
    "route",
    "tile_max_aa",
    "route_at",
    "ruling",
    "trained_context",
    "f059_peak_gib",
    "preflight_outcome",
    "preflight_why",
)


def route_of(length: int) -> str:
    """D-104: L≤440 local, 441–1026 rental, L>1026 unroutable."""
    if length <= ROUTE_AT:
        return "local"
    if length <= TILE_MAX_AA:
        return "rental"
    return "unroutable"


def tile_preflight(length: int):
    """RA3 / F-061: the case is unmeasured. Do not pass `f059_peak_gib` here."""
    return preflight(length, "int8", 64, requirement_mib=None, apply_cap=False)


def genes_by_accession() -> dict[str, str]:
    genes: dict[str, str] = {}
    with LABELS.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            genes[r["census_accession"]] = r["gene"]
    return genes


def runs_for_accession(acc: str, span_start: int, span_end: int) -> list[list[int]]:
    cache = UNIPROT_CACHE / f"{acc}.json"
    if not cache.is_file():
        raise FileNotFoundError(
            f"spancache miss for {acc}: {cache}. RA2 is cache-only — a miss is a "
            f"category, not a fetch."
        )
    doc = json.loads(cache.read_bytes().decode("utf-8"))
    iv = domain_intervals(doc, span_start, span_end, straddle=STRADDLE_HANDLING)
    return merge(iv)


def tile_rows_for_protein(
    *,
    acc: str,
    gene: str,
    span_start: int,
    span_end: int,
    n_domains: int | None = None,
) -> list[dict[str, str]]:
    runs = runs_for_accession(acc, span_start, span_end)
    lengths = [b - a + 1 for a, b in runs]
    if n_domains is None:
        cache = UNIPROT_CACHE / f"{acc}.json"
        doc = json.loads(cache.read_bytes().decode("utf-8"))
        n_domains = len(domain_intervals(doc, span_start, span_end, straddle=STRADDLE_HANDLING))
    regime = classify_regime(n_domains=n_domains, runs=lengths)
    rows: list[dict[str, str]] = []
    for idx, (start, end) in enumerate(runs):
        length = end - start + 1
        pf = tile_preflight(length)
        rows.append({
            "census_accession": acc,
            "gene": gene,
            "tile_index": str(idx),
            "start": str(start),
            "end": str(end),
            "length": str(length),
            "tile_cut_kind": TILE_CUT_KIND,
            "merge_rule": MERGE_RULE,
            "straddle_handling": STRADDLE_HANDLING,
            "gap_tolerance": GAP_TOLERANCE,
            "protein_regime": regime,
            "route": route_of(length),
            "tile_max_aa": str(TILE_MAX_AA),
            "route_at": str(ROUTE_AT),
            "ruling": RULING,
            "trained_context": str(TRAINED_CONTEXT),
            "f059_peak_gib": f"{f059_peak_gib(length):.6f}",
            "preflight_outcome": pf.outcome,
            "preflight_why": PREFLIGHT_WHY,
        })
        if pf.outcome != REFUSED_NO_MEASUREMENT or pf.required_mib is not None:
            raise RuntimeError(
                f"F-061 violated for {acc} tile {idx}: preflight outcome={pf.outcome!r} "
                f"required_mib={pf.required_mib!r} — the law was plugged in as a measurement"
            )
    return rows


def build_tile_rows() -> list[dict[str, str]]:
    genes = genes_by_accession()
    rows: list[dict[str, str]] = []
    for r in past_context_rows():
        acc = r["census_accession"]
        rows.extend(tile_rows_for_protein(
            acc=acc,
            gene=genes.get(acc, ""),
            span_start=int(r["span_start"]),
            span_end=int(r["span_end"]),
        ))
    return rows


def two_path_against_runs(
    tiles: list[dict[str, str]],
    runs_path: pathlib.Path = RUNS,
) -> list[str]:
    """For every accession in tranche6_runs.csv: tile count == n_runs and
    max(length) == largest_run. no_domains → 0 tiles / largest 0.

    Returns disagreement lines. Empty means exact.
    """
    by_acc: dict[str, list[dict[str, str]]] = {}
    for t in tiles:
        by_acc.setdefault(t["census_accession"], []).append(t)

    disagreements: list[str] = []
    with runs_path.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            acc = r["acc"]
            expected_n = int(r["n_runs"])
            expected_largest = int(r["largest_run"])
            got = by_acc.get(acc, [])
            got_n = len(got)
            got_largest = max(int(t["length"]) for t in got) if got else 0
            if got_n != expected_n or got_largest != expected_largest:
                disagreements.append(
                    f"{acc} {r.get('gene', '')}: tiles={got_n} n_runs={expected_n} "
                    f"max(length)={got_largest} largest_run={expected_largest} "
                    f"regime={r['regime']}"
                )
    extra = set(by_acc) - {
        r["acc"] for r in csv.DictReader(runs_path.open(encoding="utf-8"))
    }
    for acc in sorted(extra):
        disagreements.append(f"{acc}: tile rows with no tranche6_runs.csv accession")
    return disagreements


def main() -> int:
    tiles = build_tile_rows()
    disagreements = two_path_against_runs(tiles)
    n_le440 = sum(1 for t in tiles if int(t["length"]) <= ROUTE_AT)
    n_rental = sum(1 for t in tiles if t["route"] == "rental")
    n_unroutable = sum(1 for t in tiles if t["route"] == "unroutable")
    n_local = sum(1 for t in tiles if t["route"] == "local")

    print("=" * 96)
    print("RA2 — per-tile manifest (D-104). Cache-only. No fold, no rental, no CUDA.")
    print(f"key: one row per merged run · tile_cut_kind={TILE_CUT_KIND}")
    print("=" * 96)
    print(f"  tile rows          : {len(tiles)}")
    print(f"  length<=440        : {n_le440}   (orders cited 1242 — different key; see D-104)")
    print(f"  route local        : {n_local}")
    print(f"  route rental       : {n_rental}")
    print(f"  route unroutable   : {n_unroutable}")
    if disagreements:
        print("\n⚠⚠ TWO-PATH DISAGREEMENT — a defect, not a rounding difference")
        for line in disagreements:
            print(f"  {line}")
        return 1
    print("  two-path           : exact  (tile count == n_runs and max(length) == largest_run)")

    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(FIELDNAMES))
        w.writeheader()
        w.writerows(tiles)
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
