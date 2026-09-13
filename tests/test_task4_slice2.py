"""Task 4 slice 2 — bands 1–30. ⚠ The machinery is slice 1's; these test what is NEW.

⚠⚠ WHAT IS DELIBERATELY NOT RE-TESTED HERE. `SliceRun`'s stop conditions, deferred probe and
progress record are IMPORTED from `task4_slice1`, not copied, and `tests/test_task4_slice1.py`
already pins them across nineteen assertions. Re-asserting them here would create a second copy
of the expectations to drift — the same duplication the module itself avoids (`F-046`).

⚠ So this file tests the band, the projection, the overlap arithmetic, that the machinery really
is shared, and the one defect the slice 1 campaign flagged and deferred: the hardcoded `/20`.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts import task4_slice1 as S1   # noqa: E402
from scripts import task4_slice2 as S2   # noqa: E402

HAS_MANIFEST = (REPO / "data" / "census" / "census_manifest.v7.csv").is_file()
needs_manifest = pytest.mark.skipif(not HAS_MANIFEST, reason="census manifest not in this tree")


# ── the band ────────────────────────────────────────────────────────────────────────────────

@needs_manifest
def test_the_band_is_exactly_525_rows_inside_1_30():
    rows = S2.the_band()
    assert len(rows) == S2.EXPECTED_N == 525
    assert min(r["span"] for r in rows) >= 1
    assert max(r["span"] for r in rows) <= 30 <= S2.CAP_AA


@needs_manifest
def test_the_sub_bands_are_130_and_395_as_the_projection_assumes():
    """⚠ The projection is computed per sub-band, so a shift between them changes the total while
    leaving the count at 525 — invisible to a count-only check."""
    spans = [r["span"] for r in S2.the_band()]
    assert sum(1 for s in spans if s <= 10) == 130
    assert sum(1 for s in spans if 11 <= s <= 30) == 395
    assert [n for _, _, n, _ in S2.SUB_BANDS] == [130, 395]


def test_a_band_that_does_not_enumerate_525_is_REFUSED(monkeypatch, tmp_path):
    census = tmp_path / "data" / "census"
    census.mkdir(parents=True)
    with open(census / "census_manifest.v7.csv", "w", newline="", encoding="utf-8") as fh:
        fh.write("census_accession,span_aa,tranche\n")
        for i in range(5):
            fh.write(f"A{i:05d},20,1\n")
    monkeypatch.setattr(S2, "REPO", tmp_path)
    with pytest.raises(SystemExit) as e:
        S2.the_band()
    assert "not 525" in str(e.value)
    assert "resolve that" in str(e.value), "the refusal must say what to do, not only that it won't"


def test_the_ceiling_cannot_exceed_the_measured_envelope():
    assert S2.BAND[1] <= S2.CAP_AA


# ── the corrected projection ────────────────────────────────────────────────────────────────

def test_the_projection_adds_transport_as_a_PER_FOLD_CONSTANT():
    """⚠⚠ `D-157 amendment 3`: slice 1's projector modelled fold time and nothing else, and was
    right only because a 7.5% over-estimate cancelled a 9.5% omission. Transport is additive per
    fold, not a fraction of fold time — so it is added to each row, never scaled onto the total."""
    total, lines = S2.projection()
    expected = (16.6 + 4.7) * 130 + (16.5 + 4.7) * 395
    assert total == pytest.approx(expected)
    assert total / 3600 == pytest.approx(3.10, abs=0.02)
    assert len(lines) == 2, "the projection is reported per sub-band, not as one number"


def test_dropping_the_transport_term_changes_the_answer():
    """⚠ `A-017` (c). Without the term the projection reads ~2.42 h — the error that made slice
    1's total right by coincidence rather than by modelling."""
    fold_only = 16.6 * 130 + 16.5 * 395
    assert S2.projection()[0] > fold_only * 1.2


# ── the overlap with Task 3's twenty ────────────────────────────────────────────────────────

@needs_manifest
def test_the_band_overlaps_the_twenty_by_eight_and_the_complement_is_517():
    """⚠ The stratified sample drew 4 rows from 1–10 and 4 from 11–30. Enqueuing the band whole
    would give those eight a SECOND Run 2 row, breaking the generation partition."""
    enq = REPO / "data" / "control" / "task3_run2" / "enqueued.json"
    if not enq.is_file():
        pytest.skip("Task 3's enumeration is not in this tree")
    twenty = {e["accession"] for e in json.loads(enq.read_text(encoding="utf-8"))}
    band = {r["accession"] for r in S2.the_band()}
    assert len(band & twenty) == 8
    assert len(band - twenty) == 517


@needs_manifest
def test_the_band_bound_is_not_relaxed_to_the_complement():
    """⚠ `A-017` (c): the fix for an overlap is to enqueue a subset, never to redefine the band."""
    assert S2.EXPECTED_N == 525 and len(S2.the_band()) == 525


# ── the deferred defect: the hardcoded /20 ──────────────────────────────────────────────────

def _spec():
    """⚠ The REAL `FoldSpec`, not a stand-in. `fold_from_spec` checks `model_revision` before it
    does anything else, and a hand-rolled stub missing that field would fail on the check rather
    than exercise the log line under test - the fixture-replacing-its-subject shape again."""
    from core.contracts import FoldSpec
    from worker.main import MODEL_REVISION

    return FoldSpec(job_id=7, sequence="M" * 12, model_revision=MODEL_REVISION,
                    dtype="int8", chunk_size=64, source="sliced_ecd", ecd_start=1, ecd_end=12)


class _Result:
    pae = [[0.0]]
    fold_record = {"peak_vram": {}}


def _fit_preflight(length, dtype=None, chunk_size=None, **kw):
    from core.vram_guard import FIT

    return type("P", (), {"length": length, "free_mib": 7043, "required_mib": 1,
                          "outcome": FIT, "detail": ""})()


def test_the_log_denominator_is_the_CALLERS_population_not_the_task_3_sample(capsys):
    """⚠⚠ THE DEFECT SLICE 1 FLAGGED AND DEFERRED. Its log read `[ 6/20]` beside its own
    `[ 6/342]`, because `make_fold_callable` hardcoded the Task 3 sample size — a wrong number in
    a log line a reader has no way to discount."""
    from scripts.task3_run2_folds import FoldRecorder, make_fold_callable

    rec = FoldRecorder({7: "ACC"})
    cb = make_fold_callable(rec, lambda *a: None, lambda seq, **kw: _Result(),
                            _fit_preflight, total=517)
    cb(_spec())
    line = next(l for l in capsys.readouterr().out.splitlines() if l.startswith("["))
    assert "/517]" in line, f"denominator is not the caller's population: {line!r}"
    assert "/20]" not in line


def test_the_default_denominator_is_unchanged_for_the_task_3_caller():
    """⚠ `A-017` (c). Slice 2's fix must not move Task 3's own number."""
    import inspect

    from scripts.task3_run2_folds import SAMPLE_N, make_fold_callable

    assert SAMPLE_N == 20
    assert inspect.signature(make_fold_callable).parameters["total"].default is None


# ── the machinery really is shared ──────────────────────────────────────────────────────────

def test_slice_2_imports_slice_1s_SliceRun_rather_than_redefining_it():
    """⚠⚠ A second copy of the campaign runner is how two campaigns diverge under one name. Those
    stop conditions and the deferred probe were debugged in production across 342 folds."""
    assert S2.SliceRun is S1.SliceRun
    src = (REPO / "scripts" / "task4_slice2.py").read_text(encoding="utf-8")
    assert "class SliceRun" not in src


def test_each_slice_writes_its_OWN_progress_record(tmp_path):
    """⚠ Shared machinery, separate records: a slice writing into another's file would corrupt
    both the resume count and the harvest."""
    assert S2.PROGRESS_CSV != S1.PROGRESS_CSV
    run = S2.SliceRun({1: {"accession": "A", "analysis_id": 2, "span_aa": 5}},
                      "http://x", progress_csv=tmp_path / "p.csv")
    assert run.progress == tmp_path / "p.csv"
    assert (tmp_path / "p.csv").is_file(), "the header is written at construction"


def test_printed_strings_stay_ascii():
    """⚠ The fourth-instance guard covers the operator scripts by name; slice 2 joins them."""
    import ast

    src = (REPO / "scripts" / "task4_slice2.py").read_text(encoding="utf-8")
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "print":
            for s in ast.walk(node):
                if isinstance(s, ast.Constant) and isinstance(s.value, str):
                    assert s.value.isascii(), f"line {s.lineno}: {s.value!r}"
