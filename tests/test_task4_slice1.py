"""Task 4 slice 1 — the band's bounds, and the stop conditions an UNATTENDED run needs.

⚠⚠ WHAT THESE TESTS ARE FOR. Nobody is watching this run after ~13:00. Every assertion here is
about a bound holding or a stop condition being REACHABLE — because the failure that cost most on
2026-09-11 was not a wrong answer, it was a loop that could not stop.

⚠ `A-017` clause (c) throughout: each fixture contains a case where correct and incorrect differ.
"""
from __future__ import annotations

import csv
import pathlib
import sys
import time as _t

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts import task4_slice1 as S   # noqa: E402

HAS_MANIFEST = (REPO / "data" / "census" / "census_manifest.v7.csv").is_file()
needs_manifest = pytest.mark.skipif(not HAS_MANIFEST,
                                    reason="census manifest is not in this tree")


# ── the band ────────────────────────────────────────────────────────────────────────────────

@needs_manifest
def test_the_band_is_exactly_346_rows_inside_251_384():
    rows = S.the_band()
    assert len(rows) == S.EXPECTED_N == 346
    assert min(r["span"] for r in rows) >= S.BAND[0]
    assert max(r["span"] for r in rows) <= S.BAND[1] <= S.CAP_AA


@needs_manifest
def test_the_band_agrees_with_the_projectors_own_population():
    """⚠ One source agreeing with itself is not agreement. The projection this slice will be
    compared against was computed over the projector's band, so they must be the same rows."""
    from scripts.task3_timing_sample import population

    mine = {r["accession"] for r in S.the_band()}
    theirs = {r["accession"] for r in population() if r["band"] == "251-384"}
    assert mine == theirs


def test_a_band_that_does_not_enumerate_346_is_REFUSED_not_folded(monkeypatch, tmp_path):
    """⚠⚠ A slice of 344 is a different population than the one the owner ruled on, and the
    projection it will be compared against was computed over 346."""
    census = tmp_path / "data" / "census"
    census.mkdir(parents=True)
    with open(census / "census_manifest.v7.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["census_accession", "span_aa", "tranche"])
        for i in range(5):
            w.writerow([f"A{i:05d}", 300, 3])
    monkeypatch.setattr(S, "REPO", tmp_path)
    with pytest.raises(SystemExit) as e:
        S.the_band()
    assert "not 346" in str(e.value)
    assert "resolve that" in str(e.value), "the refusal must say what to do, not only that it won't"


def test_the_ceiling_can_never_be_raised_above_the_measured_envelope():
    """⚠ F-063 bugchecked this host before 392 and F-064 is open. The module asserts this at
    import; this pins the value so a later edit cannot quietly widen it."""
    assert S.BAND[1] == 384 == S.CAP_AA


# ── the stop conditions, which are the point of an unattended run ───────────────────────────

def _run(n, tmp):
    S.OUT_DIR = tmp
    S.PROGRESS_CSV = tmp / "progress.csv"
    allowed = {1000 + i: {"accession": f"A{i:04d}", "analysis_id": 2000 + i, "span_aa": 300}
               for i in range(n)}
    return S.SliceRun(allowed, "http://surface")


def test_the_run_stops_when_every_row_is_folded(tmp_path):
    r = _run(3, tmp_path)
    assert r.should_stop() is False
    r.done = 3
    assert r.should_stop() is True
    assert "all rows folded" in r.stop_reason


def test_an_IDLE_run_stops_CLEANLY_rather_than_polling_forever(tmp_path):
    """⚠⚠ THURSDAY'S DEFECT, GUARDED. The loop polled an empty queue forever because the stop
    condition counted successes and nothing was succeeding. Idle time is reachable whether or not
    anything is folding."""
    r = _run(346, tmp_path)
    r.last_progress = _t.time() - (S.IDLE_STOP_S + 1)
    assert r.should_stop() is True
    assert "no progress" in r.stop_reason
    assert "stopping cleanly" in r.stop_reason


def test_a_run_that_is_still_making_progress_does_NOT_stop(tmp_path):
    """⚠ A-017 (c) for the test above: an idle deadline that fires while work is happening would
    abandon the campaign, which is worse than polling."""
    r = _run(346, tmp_path)
    r.last_progress = _t.time()
    assert r.should_stop() is False


def test_the_wall_clock_backstop_is_reachable(tmp_path):
    r = _run(346, tmp_path)
    r.started = _t.time() - (S.MAX_WALL_S + 1)
    assert r.should_stop() is True
    assert "backstop" in r.stop_reason


# ── the fatal streak: a broken persistence path, not a broken fold ──────────────────────────

class _Spec:
    def __init__(self, job_id, sequence):
        self.job_id, self.sequence = job_id, sequence


class _Result:
    def __init__(self, pae=None, record=None):
        self.pae = pae
        self.fold_record = record or {"peak_vram": {"max_allocated_mib": 6000,
                                                    "max_reserved_mib": 6500}}


def _fold_into(r, monkeypatch, *, bytes_, pae_found=True, raises=False):
    """Drive one fold through `after_fold`, with the surface probe injected."""
    def _probe(base, artifact, analysis_id):
        if raises:
            raise SystemExit("cannot reach the surface")
        return (True, bytes_) if artifact == "structure" else (pae_found, 42)

    monkeypatch.setattr(S, "_head_served", _probe)
    jid = 1000 + r.done
    spec = _Spec(jid, "M" * 300)
    # the row `make_fold_callable` would have recorded, recorded here the same way
    r.rec.record(spec, _Result(pae=[[0.0]]), 50.0)
    r.after_fold(spec, _Result(pae=[[0.0]]))


def test_three_consecutive_unlanded_artifacts_stop_the_campaign(tmp_path, monkeypatch):
    """⚠⚠ THE ELEVEN EMPTY ROWS ARE WHY THIS EXISTS. A broken persistence path will not fix
    itself over the next 300 folds."""
    r = _run(346, tmp_path)
    for _ in range(S.FATAL_STREAK):
        _fold_into(r, monkeypatch, bytes_=0)
    assert r.should_stop() is True
    assert "persistence path is broken" in r.stop_reason


def test_a_single_bad_fold_does_NOT_stop_the_campaign(tmp_path, monkeypatch):
    """⚠ A-017 (c). §3.5: a fatal stops the campaign; a single fold failure does not. A threshold
    of one would abandon 345 rows on one bad artifact."""
    r = _run(346, tmp_path)
    _fold_into(r, monkeypatch, bytes_=0)
    _fold_into(r, monkeypatch, bytes_=199140)          # recovers
    assert r.fatal_streak == 0
    assert r.should_stop() is False


def test_an_UNREACHABLE_SURFACE_is_a_named_category_and_not_a_fatal(tmp_path, monkeypatch):
    """⚠⚠ §3.2 — a connection failure must never be counted as a fold failure. Three blips in a
    row would otherwise stop a healthy campaign: `refused_no_measurement`'s discipline, routed out
    is not tried-and-broke."""
    r = _run(346, tmp_path)
    for _ in range(S.FATAL_STREAK + 2):
        _fold_into(r, monkeypatch, bytes_=None, raises=True)
    assert r.fatal_streak == 0
    assert r.should_stop() is False
    assert all(v.startswith("surface_unreachable") for v in r.verdicts)


def test_a_pae_that_does_not_resolve_is_its_own_verdict(tmp_path, monkeypatch):
    """⚠ Distinct from an empty structure: the campaign exists for determinism AND PAE, so a
    structure that lands without its PAE is a different answer and gets a different word."""
    r = _run(346, tmp_path)
    _fold_into(r, monkeypatch, bytes_=199140, pae_found=False)
    assert r.verdicts == ["pae_did_not_resolve"]


# ── progress is written AS IT GOES ──────────────────────────────────────────────────────────

def test_progress_is_on_disk_after_each_fold_not_at_the_end(tmp_path, monkeypatch):
    """⚠ A five-hour run that reports only on completion tells the owner nothing at 13:00 and
    nothing at all if it dies at hour four."""
    r = _run(346, tmp_path)
    _fold_into(r, monkeypatch, bytes_=199140)
    rows = list(csv.DictReader(open(S.PROGRESS_CSV, encoding="utf-8")))
    assert len(rows) == 1 and rows[0]["verdict"] == "ok"
    _fold_into(r, monkeypatch, bytes_=199140)
    assert len(list(csv.DictReader(open(S.PROGRESS_CSV, encoding="utf-8")))) == 2


def test_the_free_mib_recorded_is_the_gates_own_reading(tmp_path, monkeypatch):
    """⚠ F-061 — the number the gate took, never re-read afterwards in the parent."""
    r = _run(346, tmp_path)
    r.rec._last_pf = type("P", (), {"length": 300, "free_mib": 7043, "required_mib": 6357})()
    _fold_into(r, monkeypatch, bytes_=199140)
    row = list(csv.DictReader(open(S.PROGRESS_CSV, encoding="utf-8")))[0]
    assert row["free_mib_before"] == "7043"
    assert row["peak_allocated_mib"] == "6000"


# ── the overlap with Task 3's twenty ────────────────────────────────────────────────────────

def test_the_band_overlaps_task_3s_sample_by_exactly_four():
    """⚠⚠ ARITHMETIC, NOT A DEFECT, AND IT MUST NOT SURPRISE ANYONE TWICE.

    The stratified sample drew 4 rows from 251-384 and they were folded as Run 2 on 2026-09-12.
    Enqueuing the band whole would give those four accessions a SECOND Run 2 row, which breaks the
    generation partition the campaign rests on. The band bound stays 346; the enqueue writes the
    complement.
    """
    import json

    enq = REPO / "data" / "control" / "task3_run2" / "enqueued.json"
    if not (HAS_MANIFEST and enq.is_file()):
        pytest.skip("needs the manifest and Task 3's enumeration")
    twenty = {e["accession"] for e in json.loads(enq.read_text(encoding="utf-8"))}
    band = {r["accession"] for r in S.the_band()}
    overlap = band & twenty
    assert len(overlap) == 4, f"expected 4 rows in both, got {sorted(overlap)}"
    assert overlap == {"O43556", "Q8N0V5", "Q8N3G9", "Q9H2X3"}
    assert len(band - twenty) == 342, "the complement is what gets enqueued"


def test_the_band_bound_is_unmoved_by_the_overlap():
    """⚠ A-017 (c). The fix must not be 'relax the band to 342' — the band is still 346 and
    `the_band()` still refuses anything else. Only the ENQUEUE writes a subset."""
    assert S.EXPECTED_N == 346
    if HAS_MANIFEST:
        assert len(S.the_band()) == 346
