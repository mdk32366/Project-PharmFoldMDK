"""RA2 / RA3 — the per-tile manifest, tested on quantities that can fail.

⚠ A TILE IS ONE MERGED RUN. Two-path against `data/census/tranche6_runs.csv` must be
exact: per accession, tile count == n_runs and max(length) == largest_run.
no_domains → 0 tiles / largest 0. A disagreement is a defect, not a rounding
difference. Cutting FAT4/FAT1 this pass would fail that comparison.

⚠ F-061: `requirement_mib=None` is still `refused_no_measurement`. Plugging
`f059_peak_gib` in as the measurement must red this file.
"""
from __future__ import annotations

import csv
import inspect
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from core.vram_guard import (  # noqa: E402
    REFUSED_NO_MEASUREMENT,
    f059_peak_gib,
    preflight,
)
from scripts.tranche6_tiles import (  # noqa: E402
    FIELDNAMES,
    GAP_TOLERANCE,
    MERGE_RULE,
    PREFLIGHT_WHY,
    ROUTE_AT,
    RULING,
    STRADDLE_HANDLING,
    TILE_CUT_KIND,
    TILE_MAX_AA,
    TRAINED_CONTEXT,
    route_of,
    tile_preflight,
    two_path_against_runs,
)

TILES = REPO / "data" / "census" / "tranche6_tiles.csv"
RUNS = REPO / "data" / "census" / "tranche6_runs.csv"
RUNS_SCRIPT = REPO / "scripts" / "tranche6_runs.py"
TILES_SCRIPT = REPO / "scripts" / "tranche6_tiles.py"

# ⚠ Pinned from the first RA2 emit, two-path exact. A change is a defect or drift.
MEASURED_LENGTH_LE440 = 1482
ORDERS_LE440_CITATION = 1242


def _tiles() -> list[dict[str, str]]:
    with TILES.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _runs() -> list[dict[str, str]]:
    with RUNS.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# ── two-path: the load-bearing test. It must be able to go red. ──────────────
def test_two_path_tile_count_and_largest_run_match_tranche6_runs_exactly():
    """For every accession in tranche6_runs.csv: len(tiles) == n_runs and
    max(length) == largest_run. Empty disagreements is the only pass."""
    disagreements = two_path_against_runs(_tiles(), RUNS)
    assert disagreements == [], (
        "two-path defect — tile count or max(length) disagrees with "
        f"tranche6_runs.csv:\n  " + "\n  ".join(disagreements)
    )


def test_no_domains_proteins_emit_zero_tiles_and_largest_zero():
    runs = {r["acc"]: r for r in _runs()}
    tiles = _tiles()
    by_acc: dict[str, list] = {}
    for t in tiles:
        by_acc.setdefault(t["census_accession"], []).append(t)
    none = [r for r in runs.values() if r["regime"] == "no_domains"]
    assert none, "the 10 no_domains rows vanished from tranche6_runs.csv"
    for r in none:
        got = by_acc.get(r["acc"], [])
        assert got == [], f"{r['acc']} {r['gene']} is no_domains but emitted {len(got)} tiles"
        assert int(r["n_runs"]) == 0 and int(r["largest_run"]) == 0


def test_tile_file_has_1532_data_rows():
    assert len(_tiles()) == 1532


# ── the 1242 key: named, not collapsed into length≤440 ───────────────────────
def test_the_1242_orders_figure_is_the_93_protein_aggregate_not_per_tile_length():
    """Orders cited 1,242 of 1,532 as length≤440 from tranche6_runs.csv.
    That file has no per-tile length. The number it CAN support is
    sum(n_runs) over proteins with largest_run≤440 = 93 proteins → 1,242.

    ⚠ The per-tile count of length≤440 is 1,482. Different key. Do not invent
    a fix that forces them equal — that would mean cutting sibling runs and
    failing two-path."""
    runs = _runs()
    aggregate = sum(
        int(r["n_runs"]) for r in runs
        if int(r["largest_run"]) <= 440 and int(r["n_runs"]) > 0
    )
    n_proteins = sum(1 for r in runs if int(r["largest_run"]) <= 440 and int(r["n_runs"]) > 0)
    assert n_proteins == 93
    assert aggregate == ORDERS_LE440_CITATION

    n_le440 = sum(1 for t in _tiles() if int(t["length"]) <= 440)
    assert n_le440 == MEASURED_LENGTH_LE440
    assert n_le440 != ORDERS_LE440_CITATION, (
        "the two keys collapsed — a later change made length≤440 equal the "
        "93-protein aggregate; that is either a cut or a dropped sibling"
    )


# ── D-104 routing ────────────────────────────────────────────────────────────
@pytest.mark.parametrize("length,expected", [
    (1, "local"),
    (440, "local"),
    (441, "rental"),
    (1026, "rental"),
    (1027, "unroutable"),
    (3037, "unroutable"),
])
def test_route_edges_are_exact(length, expected):
    assert route_of(length) == expected


def test_no_unroutable_row_is_routed():
    for t in _tiles():
        length = int(t["length"])
        if length > TILE_MAX_AA:
            assert t["route"] == "unroutable", (
                f"{t['census_accession']} {t['gene']} L={length} was routed {t['route']}"
            )
        assert t["route"] == route_of(length)


def test_the_six_oversized_runs_are_emitted_whole_and_unroutable_not_cut():
    """FAT4/FAT1 this pass: one whole_run tile at the published largest_run.
    A cut would change n_runs or max(length) and fail two-path."""
    want = {
        "FAT4": 3037, "FAT3": 2291, "FAT1": 2289,
        "MUC16": 1977, "FAT2": 1674, "CDH23": 1175,
    }
    tiles = _tiles()
    unroutable = [t for t in tiles if t["route"] == "unroutable"]
    assert len(unroutable) == 6
    got = {t["gene"]: int(t["length"]) for t in unroutable}
    assert got == want
    for t in unroutable:
        assert t["tile_cut_kind"] == "whole_run"


# ── every listed parameter on every row; D-104 named ─────────────────────────
def test_every_required_parameter_travels_on_every_row():
    tiles = _tiles()
    assert tiles
    for t in tiles:
        missing = [k for k in FIELDNAMES if k not in t or t[k] == ""]
        assert not missing, f"{t.get('census_accession')} missing {missing}"
        assert t["tile_cut_kind"] == TILE_CUT_KIND
        assert t["merge_rule"] == MERGE_RULE
        assert t["straddle_handling"] == STRADDLE_HANDLING
        assert t["gap_tolerance"] == GAP_TOLERANCE
        assert t["tile_max_aa"] == str(TILE_MAX_AA)
        assert t["route_at"] == str(ROUTE_AT)
        assert t["ruling"] == RULING
        assert t["ruling"] == "D-104"
        assert t["trained_context"] == str(TRAINED_CONTEXT)
        assert t["preflight_outcome"] == REFUSED_NO_MEASUREMENT
        assert t["preflight_why"] == PREFLIGHT_WHY


# ── F-061: a law is not a measurement ────────────────────────────────────────
def test_requirement_mib_none_is_still_refused_no_measurement(monkeypatch):
    """Must go red if someone plugs F-059 in as the measurement.

    Prove it bites: under stubbed free VRAM, passing f059_peak_gib as
    requirement_mib is NOT refused_no_measurement. tile_preflight must
    still pass None."""
    import core.vram_guard as g
    monkeypatch.setattr(g, "cuda_memory", lambda: (7000, 8150))
    monkeypatch.setattr(g, "apply_allocator_cap", lambda f: {"applied": False})

    r = tile_preflight(200)
    assert r.outcome == REFUSED_NO_MEASUREMENT
    assert r.required_mib is None
    assert r.may_fold is False

    peak_mib = int(f059_peak_gib(200) * 1024)
    plugged = preflight(200, "int8", 64, requirement_mib=peak_mib, apply_cap=False)
    assert plugged.outcome != REFUSED_NO_MEASUREMENT, (
        "the bite-proof itself broke: plugging F-059 under stubbed CUDA should "
        "NOT stay refused_no_measurement, otherwise the guard cannot see the plug-in"
    )


def test_tiles_script_passes_requirement_mib_none_and_does_not_pass_f059():
    """Static: the emit path must call preflight with None. A hand edit that
    passes f059_peak_gib as requirement_mib reds here rather than silently
    writing FIT or refused_insufficient_headroom into the CSV on a CUDA box."""
    src = TILES_SCRIPT.read_text(encoding="utf-8")
    assert "requirement_mib=None" in src
    assert "f059_peak_gib" in src
    assert "requirement_mib=f059" not in src
    assert "requirement_mib=int(" not in src
    sig = inspect.signature(tile_preflight)
    # tile_preflight takes only length — it cannot accept a requirement to plug in
    assert list(sig.parameters) == ["length"]


def test_f059_is_recorded_on_the_tile_from_the_law():
    t = _tiles()[0]
    length = int(t["length"])
    assert abs(float(t["f059_peak_gib"]) - f059_peak_gib(length)) < 5e-7


# ── the runs artifact this pass must not touch ───────────────────────────────
def test_tranche6_runs_csv_and_script_bytes_are_the_committed_ones():
    """RA2 must not rewrite the aggregate file it two-paths against."""
    import hashlib
    csv_hash = hashlib.sha256(RUNS.read_bytes()).hexdigest()
    assert csv_hash == "78f97db3fbef146baf32e9fa893d8c96d8f60b431e1dfd626fb5639b4f72c3af"
    script_hash = hashlib.sha256(RUNS_SCRIPT.read_bytes()).hexdigest()
    assert script_hash == "d5377a2cde087bf5926ae6cc145890d84d51b3a5b9fbff26af9f3d7709b79c39"
