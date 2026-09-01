"""RB re-gate — pins on the local-tile fold harness (F-063 envelope, L≤384).

⚠ These tests do NOT fold. They pin the contracts Emma/Trinity need before the GPU run:
limit default 10, WORKER_FOLD_IN_CHILD refusal, never passing f059 as requirement_mib,
population 1482 then L≤384, descending length order, envelope 6357, summary path, and
>10% F-059 departure stopping the batch.
"""
from __future__ import annotations

import ast
import csv
import inspect
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "rb_local_tile_folds.py"
TILES = REPO / "data" / "census" / "tranche6_tiles.csv"
CLIMB_JSONL = REPO / "data" / "census" / "ceiling_climb.blackwell.int8.20260831.jsonl"

#: Longest-first L≤384 local tiles. Goes red if the filter or sort key drifts.
EXPECTED_TOP10 = [
    (380, "USH2A", 17),
    (374, "USH2A", 18),
    (362, "PTPRB", 4),
    (360, "LRP1", 22),
    (351, "PTPRB", 2),
    (340, "ITGAX", 1),
    (339, "PLB1", 2),
    (332, "FAT3", 0),
    (327, "CDHR2", 0),
    (324, "CPD", 0),
]


def _load_mod():
    """Load the script as a module without executing main."""
    sys.path.insert(0, str(REPO))
    name = "rb_local_tile_folds"
    if name in sys.modules:
        del sys.modules[name]
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_limit_default_is_ten():
    """RB4: default --limit is 10. No silent full run."""
    mod = _load_mod()
    assert mod.RB4_DEFAULT_LIMIT == 10
    src = SCRIPT.read_text(encoding="utf-8")
    tree = ast.parse(src)
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(getattr(node, "func", None), "attr", None) == "add_argument":
            args = [a for a in node.args if isinstance(a, ast.Constant) and a.value == "--limit"]
            if not args:
                continue
            for kw in node.keywords:
                if kw.arg == "default":
                    if isinstance(kw.value, ast.Name) and kw.value.id == "RB4_DEFAULT_LIMIT":
                        found = True
                    if isinstance(kw.value, ast.Constant) and kw.value.value == 10:
                        found = True
    assert found, "--limit default is not pinned to RB4_DEFAULT_LIMIT / 10"


def test_refuses_without_worker_fold_in_child(monkeypatch):
    """⚠ D-082 layer 3: unset switch is a hard refuse, not a warning."""
    mod = _load_mod()
    monkeypatch.delenv("WORKER_FOLD_IN_CHILD", raising=False)
    with pytest.raises(SystemExit) as ei:
        mod.assert_worker_fold_in_child()
    assert "WORKER_FOLD_IN_CHILD" in str(ei.value)


def test_never_passes_f059_as_requirement_mib():
    """⚠⚠ F-061: f059_peak_gib is recorded, never fed to preflight as requirement_mib."""
    src = SCRIPT.read_text(encoding="utf-8")
    tree = ast.parse(src)
    found = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = getattr(func, "id", None) or getattr(func, "attr", None)
        if name != "preflight":
            continue
        for kw in node.keywords:
            if kw.arg != "requirement_mib":
                continue
            found = True
            blob = ast.dump(kw.value)
            assert "f059" not in blob.lower()
            if isinstance(kw.value, ast.Name):
                assert "f059" not in kw.value.id.lower()
                assert kw.value.id in {"requirement_mib", "MEASURED_SUCCESS_PEAK_MIB"}
            elif isinstance(kw.value, ast.Constant):
                assert kw.value.value == 6357
                assert kw.value.value != 6665
            else:
                pytest.fail(f"preflight requirement_mib has unexpected form: {ast.dump(kw.value)}")
    assert found, "no preflight(..., requirement_mib=...) call site"
    assert "f059_peak_gib" in src
    # requirement_for_length / climb loader must not consult the law as a field lookup.
    mod = _load_mod()
    assert "f059" not in inspect.getsource(mod.requirement_for_length).lower()
    loader_src = inspect.getsource(mod.load_climb_ok_peaks)
    assert "max_allocated_mib" in loader_src
    loader_tree = ast.parse(loader_src)
    for node in ast.walk(loader_tree):
        if isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "get":
            for a in node.args:
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    assert "f059" not in a.value.lower(), (
                        f"climb loader looks up {a.value!r}; requirement must not come from F-059"
                    )


def test_envelope_constant_is_6357_not_6665():
    """F-063 last OK peak_alloc is the hard envelope. S-005's 6665 is not this card (F-062)."""
    mod = _load_mod()
    src = SCRIPT.read_text(encoding="utf-8")
    assert mod.MEASURED_SUCCESS_PEAK_MIB == 6357
    assert getattr(mod, "MEASURED_SUCCESS_MIB", None) != 6665
    compact = src.replace(" ", "")
    assert "MEASURED_SUCCESS_PEAK_MIB=6357" in compact
    assert "MEASURED_SUCCESS_MIB=6665" not in compact
    assert "MEASURED_SUCCESS_PEAK_MIB=6665" not in compact


def test_summary_path_is_regate384_and_does_not_overwrite_rb4():
    """New artifact. The RB4 summary stays where it is."""
    mod = _load_mod()
    assert mod.SUMMARY.name == "rb_local_summary.regate384.csv"
    assert mod.SUMMARY.as_posix().endswith("data/control/rb_local/rb_local_summary.regate384.csv")
    src = SCRIPT.read_text(encoding="utf-8")
    assert "rb_local_summary.regate384.csv" in src
    # The SUMMARY assignment must not be the old filename.
    tree = ast.parse(src)
    assigned = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "SUMMARY":
                    assigned = ast.unparse(node.value)
    assert assigned is not None
    assert "regate384" in assigned
    assert "rb_local_summary.csv" not in assigned or "regate384" in assigned


def test_local_population_is_1482_then_l384_filter_is_1478():
    """D-104: route=local is 1482. Re-gate filter is L≤384 (~1478). route_at untouched."""
    mod = _load_mod()
    assert mod.LOCAL_POPULATION == 1482
    assert mod.LOCAL_REGATE_MAX_LENGTH == 384
    with TILES.open(encoding="utf-8") as fh:
        local = [r for r in csv.DictReader(fh) if r.get("route") == "local"]
    assert len(local) == 1482
    le384 = [r for r in local if int(r["length"]) <= 384]
    assert len(le384) == 1478
    rows = mod.load_local_tiles()
    assert len(rows) == 1478
    assert all(int(r["length"]) <= 384 for r in rows)
    # The 1482 assert is still in the loader (goes red if someone drops it).
    src = inspect.getsource(mod.load_local_tiles)
    assert "LOCAL_POPULATION" in src
    assert "LOCAL_REGATE_MAX_LENGTH" in src
    # D-104 / route_at must not be rewritten by this filter.
    assert "route_at" not in src or "untouched" in SCRIPT.read_text(encoding="utf-8")


def test_order_is_descending_length_then_accession_then_tile_index():
    """KEY: descending (length, census_accession, tile_index) after the L≤384 filter."""
    mod = _load_mod()
    rows = mod.load_local_tiles()
    keys = [(int(r["length"]), r["census_accession"], int(r["tile_index"])) for r in rows]
    assert keys == sorted(keys, reverse=True)
    top = rows[:10]
    assert int(top[0]["length"]) >= int(top[-1]["length"])
    assert int(top[0]["length"]) == 380
    assert top[0]["gene"] == "USH2A"
    assert int(top[0]["tile_index"]) == 17
    # The previous RB4 head (440 aa) is filtered out; shorter Q96QU1 tiles may remain.
    assert int(top[0]["length"]) != 440
    assert not any(int(r["length"]) > 384 for r in rows)


def test_top10_identity_matches_regate384():
    """First ten after L≤384 longest-first. Goes red if the filter or CSV drifts."""
    mod = _load_mod()
    rows = mod.load_local_tiles()[:10]
    got = [(int(r["length"]), r["gene"], int(r["tile_index"])) for r in rows]
    assert got == EXPECTED_TOP10


def test_requirement_prefers_climb_exact_L_else_hard_envelope():
    """Synthetic peaks: exact OK length uses climb peak; anything else uses 6357."""
    mod = _load_mod()
    peaks = {360: 6239, 384: 6357}
    mib, src = mod.requirement_for_length(360, peaks)
    assert mib == 6239
    assert src == "climb_exact_L"
    mib, src = mod.requirement_for_length(380, peaks)
    assert mib == 6357
    assert src == "hard_envelope_6357"
    mib, src = mod.requirement_for_length(384, peaks)
    assert mib == 6357
    assert src == "climb_exact_L"
    # Never the law: F-059 at L=360 is 6232.09 in the climb jsonl.
    assert mod.requirement_for_length(360, peaks)[0] != 6232


def test_climb_loader_uses_peak_vram_max_allocated_not_f059(tmp_path):
    """Self-contained: outcome=ok + peak_vram.max_allocated_mib; skip non-ok; ignore f059."""
    mod = _load_mod()
    p = tmp_path / "climb.jsonl"
    p.write_text(
        json.dumps({"kind": "header", "f059_peak_mib": 1}) + "\n"
        + json.dumps({
            "kind": "attempt",
            "length": 360,
            "outcome": "ok",
            "f059_peak_mib": 6232.09,
            "f059_peak_gib": 6.086027,
            "peak_vram": {"max_allocated_mib": 6239, "max_reserved_mib": 6706},
        }) + "\n"
        + json.dumps({
            "kind": "attempt",
            "length": 392,
            "outcome": "oom_caught",
            "f059_peak_mib": 9999,
            "peak_vram": {"max_allocated_mib": 9999, "max_reserved_mib": 9999},
        }) + "\n",
        encoding="utf-8",
    )
    peaks = mod.load_climb_ok_peaks(p)
    assert peaks == {360: 6239}


def test_committed_climb_jsonl_360_is_6239_not_f059():
    """The disqualifying query on the F-063 artifact: allocated 6239, not f059 6232.09."""
    mod = _load_mod()
    assert CLIMB_JSONL.is_file()
    peaks = mod.load_climb_ok_peaks()
    assert peaks[360] == 6239
    assert 384 in peaks
    assert peaks[384] == 6357
    assert 380 not in peaks
    # Prove the file still carries the f059 field we must not use.
    found_360 = False
    with CLIMB_JSONL.open(encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            if rec.get("outcome") == "ok" and rec.get("length") == 360:
                found_360 = True
                assert rec["peak_vram"]["max_allocated_mib"] == 6239
                assert rec["f059_peak_mib"] == 6232.09
    assert found_360


def test_top10_requirement_mib_and_source():
    """Only L=360 in the top ten sits on the climb ladder → 6239 / climb_exact_L."""
    mod = _load_mod()
    peaks = mod.load_climb_ok_peaks()
    rows = mod.load_local_tiles()[:10]
    sources = []
    for r in rows:
        length = int(r["length"])
        mib, src = mod.requirement_for_length(length, peaks)
        sources.append((length, r["gene"], int(r["tile_index"]), mib, src))
        if length == 360:
            assert mib == 6239
            assert src == "climb_exact_L"
        else:
            assert mib == 6357
            assert src == "hard_envelope_6357"
            assert mib != float(r["f059_peak_gib"]) * 1024
    assert sum(1 for s in sources if s[4] == "climb_exact_L") == 1
    assert sources[3][:3] == (360, "LRP1", 22)


def test_card_identity_keys_and_summary_fields():
    """gpu_name / nvidia_driver_version / vram_total_mib on the run; never raises without GPU."""
    mod = _load_mod()
    ident = mod.capture_card_identity()
    assert set(ident) == {"gpu_name", "nvidia_driver_version", "vram_total_mib"}
    for key in ("gpu_name", "nvidia_driver_version", "vram_total_mib"):
        assert key in mod.SUMMARY_FIELDS
    assert "requirement_mib" in mod.SUMMARY_FIELDS
    assert "requirement_source" in mod.SUMMARY_FIELDS


def test_gt_10pct_f059_departure_sets_stop():
    """Stop condition: |measured-f059|/f059 > 0.10 stops the batch."""
    mod = _load_mod()
    assert mod.F059_DEPARTURE_STOP == 0.10
    depart = mod.pct_depart(measured_mib=6.5 * 1024 * 1.11, f059_gib=6.5)
    assert depart is not None and depart > mod.F059_DEPARTURE_STOP
    ok = mod.pct_depart(measured_mib=6.5 * 1024 * 1.05, f059_gib=6.5)
    assert ok is not None and ok <= mod.F059_DEPARTURE_STOP
    src = SCRIPT.read_text(encoding="utf-8")
    assert "f059_departure_gt_10pct" in src
    assert "continue-after-rb4" in src
    assert "preflight_" in src
    assert "fold_error:" in src


def test_script_imports_no_db_by_ast():
    """⚠ No db / core.enqueue / sqlalchemy import in the script source."""
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    banned = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            banned += [a.name for a in node.names if a.name.split(".")[0] in {"db", "sqlalchemy"}]
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            top = mod.split(".")[0]
            if top in {"db", "sqlalchemy"} or mod == "core.enqueue":
                banned.append(mod)
    assert not banned
