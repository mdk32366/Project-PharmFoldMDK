"""Task 4 slice 3 — band 31–100. ⚠ Machinery is slice 1's; these test what is NEW.

⚠⚠ THE ONE THING THIS SLICE MUST NOT DO is carry a transport term. `D-157 amendment 4` retracted
the per-fold-constant framing after slice 1 measured 4.7 s/fold and slice 2 measured 0.7 — a
factor of 6.7 — and band 31–100 sits BETWEEN them, which is exactly where an interpolation looks
most reasonable and is least licensed by two points.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts import task4_slice1 as S1   # noqa: E402
from scripts import task4_slice3 as S3   # noqa: E402

HAS_MANIFEST = (REPO / "data" / "census" / "census_manifest.v7.csv").is_file()
needs_manifest = pytest.mark.skipif(not HAS_MANIFEST, reason="census manifest not in this tree")


@needs_manifest
def test_the_band_is_exactly_1101_rows_inside_31_100():
    rows = S3.the_band()
    assert len(rows) == S3.EXPECTED_N == 1101
    assert min(r["span"] for r in rows) >= 31
    assert max(r["span"] for r in rows) <= 100 <= S3.CAP_AA


def test_a_band_that_does_not_enumerate_1101_is_REFUSED(monkeypatch, tmp_path):
    census = tmp_path / "data" / "census"
    census.mkdir(parents=True)
    with open(census / "census_manifest.v7.csv", "w", newline="", encoding="utf-8") as fh:
        fh.write("census_accession,span_aa,tranche\n")
        for i in range(5):
            fh.write(f"A{i:05d},50,1\n")
    monkeypatch.setattr(S3, "REPO", tmp_path)
    with pytest.raises(SystemExit) as e:
        S3.the_band()
    assert "not 1101" in str(e.value)


@needs_manifest
def test_the_overlap_is_four_and_the_complement_is_1097():
    enq = REPO / "data" / "control" / "task3_run2" / "enqueued.json"
    if not enq.is_file():
        pytest.skip("Task 3's enumeration is not in this tree")
    twenty = {e["accession"] for e in json.loads(enq.read_text(encoding="utf-8"))}
    band = {r["accession"] for r in S3.the_band()}
    assert len(band & twenty) == 4
    assert len(band - twenty) == 1097


# ── the transport term: declared absent, not estimated ──────────────────────────────────────

def test_this_slice_carries_NO_transport_term():
    """⚠⚠ D-157 amendment 4. Two measured points do not licence an interpolation, and 31–100
    sitting between 1–30 and 251–384 is where one looks most reasonable."""
    assert S3.TRANSPORT_S is None
    p = S3.projection()
    assert p["transport_s"] is None
    assert "UNMEASURED" in p["transport_status"]


def test_neither_existing_transport_value_appears_in_the_projection():
    """⚠ A-017 (c). The failure this guards is silent inheritance, so the assertion is that the
    retracted numbers are ABSENT rather than that some other number is present."""
    p = S3.projection()
    assert p["fold_only_h"] == pytest.approx(16.5 * 1101 / 3600)
    for banned in (4.7, 0.7):
        assert banned not in (p["transport_s"],)
        assert p["fold_only_h"] != pytest.approx((16.5 + banned) * 1101 / 3600)


def test_the_projection_refuses_to_state_an_ELAPSED_figure():
    """⚠⚠ An elapsed number without the transport term would be an estimate wearing a
    measurement's clothes — the exact shape amendment 4 retracted."""
    assert S3.projection()["elapsed_h"] is None


def test_the_source_carries_no_hardcoded_transport_constant():
    src = (REPO / "scripts" / "task4_slice3.py").read_text(encoding="utf-8")
    assert "TRANSPORT_S = None" in src
    assert "fold_s + TRANSPORT_S" not in src, "slice 2's projection formula must not survive here"


# ── shared machinery, including the guard ───────────────────────────────────────────────────

def test_slice_3_imports_the_machinery_rather_than_redefining_it():
    assert S3.SliceRun is S1.SliceRun
    assert S3.refuse_on_strangers is S1.refuse_on_strangers
    src = (REPO / "scripts" / "task4_slice3.py").read_text(encoding="utf-8")
    assert "class SliceRun" not in src and "def strangers" not in src


def test_the_fold_calls_the_stranger_guard_before_any_claim():
    """⚠⚠ The gate on this slice's enqueue. A guard that exists and is never called is the manual
    check with extra steps."""
    import inspect
    src = inspect.getsource(S3.fold)
    assert "refuse_on_strangers(" in src
    assert src.index("refuse_on_strangers(") < src.index("run_worker("), \
        "the guard must run BEFORE the loop that claims"


def test_each_slice_writes_its_own_progress_record():
    assert S3.PROGRESS_CSV not in (S1.PROGRESS_CSV,)


def test_printed_strings_stay_ascii():
    import ast
    src = (REPO / "scripts" / "task4_slice3.py").read_text(encoding="utf-8")
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "print":
            for s in ast.walk(node):
                if isinstance(s, ast.Constant) and isinstance(s.value, str):
                    assert s.value.isascii(), f"line {s.lineno}: {s.value!r}"
