"""RB — pins on the local-tile fold harness (D-104 / F-061 / measured-success gate).

⚠ These tests do NOT fold. They pin the contracts Emma/Trinity need before the GPU run:
limit default 10, WORKER_FOLD_IN_CHILD refusal, never passing f059 as requirement_mib,
population 1482, descending length order, and >10% F-059 departure stopping the batch.
"""
from __future__ import annotations

import ast
import csv
import os
import pathlib
import runpy
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "rb_local_tile_folds.py"
TILES = REPO / "data" / "census" / "tranche6_tiles.csv"


def _load_mod(monkeypatch=None):
    """Load the script as a module without executing main."""
    sys.path.insert(0, str(REPO))
    # Clear any prior load so env asserts re-run cleanly when imported via run path.
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
                    # default=RB4_DEFAULT_LIMIT or default=10
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
    # No call to preflight may pass requirement_mib=f059_* or a call to f059_peak_gib.
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
            # Must be MEASURED_SUCCESS_MIB (or a literal 6665), never f059.
            if isinstance(kw.value, ast.Name):
                assert kw.value.id == "MEASURED_SUCCESS_MIB", (
                    f"preflight requirement_mib uses {kw.value.id}, not MEASURED_SUCCESS_MIB"
                )
            elif isinstance(kw.value, ast.Constant):
                assert kw.value.value == 6665
            else:
                pytest.fail(f"preflight requirement_mib has unexpected form: {ast.dump(kw.value)}")
            # And the expression must not mention f059
            blob = ast.dump(kw.value)
            assert "f059" not in blob.lower()
    assert "MEASURED_SUCCESS_MIB = 6665" in src or "MEASURED_SUCCESS_MIB=6665" in src.replace(" ", "")
    # f059 must still be recorded on the row
    assert "f059_peak_gib" in src


def test_local_population_is_1482():
    """D-104: route=local population on the committed tile CSV is 1482."""
    mod = _load_mod()
    assert mod.LOCAL_POPULATION == 1482
    with TILES.open(encoding="utf-8") as fh:
        n = sum(1 for r in csv.DictReader(fh) if r.get("route") == "local")
    assert n == 1482


def test_order_is_descending_length_then_accession_then_tile_index():
    """KEY: descending (length, census_accession, tile_index)."""
    mod = _load_mod()
    rows = mod.load_local_tiles()
    keys = [(int(r["length"]), r["census_accession"], int(r["tile_index"])) for r in rows]
    assert keys == sorted(keys, reverse=True)
    # First ten are the RB4 set
    top = rows[:10]
    assert int(top[0]["length"]) >= int(top[-1]["length"])
    assert top[0]["census_accession"] == "Q96QU1"
    assert int(top[0]["length"]) == 440


def test_gt_10pct_f059_departure_sets_stop():
    """RB4 stop condition: |measured-f059|/f059 > 0.10 stops the batch."""
    mod = _load_mod()
    assert mod.F059_DEPARTURE_STOP == 0.10
    # 10% on a 6.5 GiB prediction is 0.65 GiB; 11% departure must trip.
    depart = mod.pct_depart(measured_mib=6.5 * 1024 * 1.11, f059_gib=6.5)
    assert depart is not None and depart > mod.F059_DEPARTURE_STOP
    ok = mod.pct_depart(measured_mib=6.5 * 1024 * 1.05, f059_gib=6.5)
    assert ok is not None and ok <= mod.F059_DEPARTURE_STOP
    src = SCRIPT.read_text(encoding="utf-8")
    assert "f059_departure_gt_10pct" in src
    assert "continue-after-rb4" in src


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
