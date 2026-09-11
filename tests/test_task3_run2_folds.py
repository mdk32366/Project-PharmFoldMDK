"""The 20 Run 2 folds — the §4.2 exception, its guards, and the three things the run must yield.

⚠⚠ WHAT THESE TESTS ARE FOR, AND IT IS NOT THE HAPPY PATH. The run writes to production, once,
with the owner at the keyboard, and it cannot be re-run to fix a recording mistake — twenty folds
are spent either way. So every assertion here is about a guard REFUSING, or about a number being
attached to the fold it was actually measured on.

⚠ `A-017` clause (c) throughout: each fixture contains a case where correct and incorrect differ,
so none of these can pass against a broken implementation.
"""
from __future__ import annotations

import csv
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts import task3_run2_folds as T   # noqa: E402

#: ⚠⚠ `data/census/spancache/` is GITIGNORED BY DESIGN (`.gitignore:236`, `data/census/*cache/`),
#: so CI never has it and the two tests that build REAL payloads cannot run there. They are
#: skipped with a named reason rather than weakened to run everywhere — ⚠ **and the machine that
#: will actually run the campaign has the cache, so they are exercised exactly where the campaign
#: is.** Everything else here, the owner gate included, runs on every platform.
HAS_SPANCACHE = (REPO / "data" / "census" / "spancache" / "Q8WXF7.json").is_file()
needs_spancache = pytest.mark.skipif(
    not HAS_SPANCACHE,
    reason="data/census/spancache/ is a local artifact (gitignored); this assertion runs on the "
           "campaign machine, not on CI")


# ── the population ──────────────────────────────────────────────────────────────────────────

def test_the_twenty_is_twenty_under_the_cap_and_holds_the_one_residue_row():
    rows = T.the_twenty()
    assert len(rows) == T.SAMPLE_N
    assert max(r["span"] for r in rows) <= T.CAP_AA, (
        "a fold above 384 aa on this card is refused — F-063 bugchecked the host before 392")
    # ⚠⚠ The 1-residue row is the campaign's whole open question and must not quietly drop out
    # of the sample: the owner's pre-registered rule decides 37-99 rows on its outcome.
    assert "Q8WXF7" in {r["accession"] for r in rows}


def test_the_selection_is_stratified_and_not_merely_the_shortest():
    """⚠ A-017 (c). A 'take the first N' or 'take the shortest N' implementation would return a
    DIFFERENT set, so this test discriminates rather than describing."""
    from scripts.task3_timing_sample import BANDS, population

    rows = T.the_twenty()
    shortest = {r["accession"] for r in sorted(population(), key=lambda r: r["span"])[:T.SAMPLE_N]}
    assert {r["accession"] for r in rows} != shortest
    # and every band carries exactly its quota, which the shortest-N set could not
    assert sorted(len([r for r in rows if r["band"] == f"{lo}-{hi}"])
                  for lo, hi in BANDS) == [4] * 5


def test_the_selector_is_deterministic_across_calls():
    """The population must be ENUMERABLE — a later reader has to find exactly these rows."""
    assert [r["accession"] for r in T.the_twenty()] == [r["accession"] for r in T.the_twenty()]


def test_an_over_cap_selection_is_refused_rather_than_trimmed(monkeypatch):
    """⚠⚠ Trimming would silently change the population; refusing makes the owner decide."""
    import scripts.task3_timing_sample as sample

    over = [{"accession": "X%02d" % i, "span": 10, "band": "1-10", "tranche": 1}
            for i in range(T.SAMPLE_N - 1)]
    over.append({"accession": "TOOBIG", "span": 400, "band": "251-384", "tranche": 4})
    monkeypatch.setattr(sample, "select", lambda *a, **k: over)
    with pytest.raises(SystemExit) as e:
        T.the_twenty()
    assert "TOOBIG(400aa)" in str(e.value) and "384" in str(e.value)


def test_a_selection_of_the_wrong_size_is_refused(monkeypatch):
    import scripts.task3_timing_sample as sample

    monkeypatch.setattr(sample, "select", lambda *a, **k: [{"accession": "A", "span": 5,
                                                            "band": "1-10", "tranche": 1}])
    with pytest.raises(SystemExit) as e:
        T.the_twenty()
    assert "not 20" in str(e.value)


@needs_spancache
def test_every_payload_satisfies_the_claim_contract_before_any_write():
    """⚠⚠ Ten jobs were once written whose `inference_settings` lacked `model_revision`: the dry
    run passed because it never called the contract it was writing for, and `/claim` stranded all
    ten with attempts=0. `run2_payloads` calls `assert_claimable` on all twenty — so this test
    passing IS the contract being exercised twenty times."""
    payloads = T.run2_payloads()
    assert len(payloads) == T.SAMPLE_N
    for p in payloads:
        assert p["inference_settings"]["model_revision"], p["accession"]
        assert p["meta"]["fold_length"] <= T.CAP_AA


# ── the recorder ────────────────────────────────────────────────────────────────────────────

class _Pf:
    """⚠ `outcome` is the REAL `core.vram_guard.FIT` constant, not the string "fit". A stub that
    spells the passing value by hand would make every test here pass through a gate that refuses
    in production — the substrate forgiving what production rejects (`F-056`)."""

    def __init__(self, length, free_mib, required_mib=6357):
        from core.vram_guard import FIT

        self.length, self.free_mib, self.required_mib = length, free_mib, required_mib
        self.outcome, self.detail = FIT, ""


class _Spec:
    def __init__(self, job_id, sequence):
        self.job_id, self.sequence = job_id, sequence


class _Result:
    def __init__(self, pae=None, record=None):
        self.pae = pae
        self.fold_record = record or {}


def test_a_job_outside_the_twenty_is_refused_rather_than_folded_into_the_exception():
    """⚠⚠ `run_worker` claims the next job of its TIER, not 'one of mine'. This is the assertion
    that keeps a 20-row exception at twenty rows."""
    rec = T.FoldRecorder({101: "Q8WXF7"})
    with pytest.raises(SystemExit) as e:
        rec.record(_Spec(999, "MM"), _Result(), 1.0)
    assert "not one of the 20" in str(e.value)
    assert rec.rows == []


def test_a_preflight_paired_to_the_wrong_fold_raises_rather_than_recording_it():
    """⚠ F-024's shape. Pairing is by call order; the length is the CHECK on that assumption, and
    a mismatch means every free_mib after this point would hang on the wrong fold."""
    rec = T.FoldRecorder({101: "Q8WXF7"})
    rec._last_pf = _Pf(length=377, free_mib=7000)
    with pytest.raises(SystemExit) as e:
        rec.record(_Spec(101, "M"), _Result(), 1.0)
    assert "pairing assumption is broken" in str(e.value)


def test_the_recorded_free_mib_is_the_number_the_GATE_took():
    """⚠⚠ Not re-read in the parent afterwards. A second reading at a different instant is a
    different measurement (F-061), and the question is what the NEXT preflight sees."""
    rec = T.FoldRecorder({101: "Q8WXF7"})
    seen = []

    def _real(length, dtype, chunk_size, **kw):
        seen.append(length)
        return _Pf(length=length, free_mib=7043)

    wrapped = rec.preflight(_real)
    pf = wrapped(1, "int8", 64, requirement_mib=6357, margin_mib=0)
    assert pf.free_mib == 7043 and seen == [1]
    rec.record(_Spec(101, "M"), _Result(pae=[[0.0]], record={"peak_vram": 6357}), 12.5)
    row = rec.rows[0]
    assert row["free_mib_before"] == 7043
    assert row["requirement_mib"] == 6357
    assert row["peak_vram_mib"] == 6357
    assert row["wall_seconds"] == 12.5
    assert row["emitted_pae"] is True


def test_a_fold_that_emits_no_pae_is_recorded_as_such_and_not_as_a_failure():
    """⚠ `no_pae_emitted` is a legitimate outcome and the owner's rule turns on it. Recording it
    as a failure would answer a pre-registered question with the wrong word."""
    rec = T.FoldRecorder({101: "Q8WXF7"})
    rec.record(_Spec(101, "M"), _Result(pae=None), 3.0)
    assert rec.rows[0]["emitted_pae"] is False


def test_the_csv_this_writes_is_what_the_projector_reads(tmp_path, monkeypatch):
    """⚠⚠ ONE projector, not two. The recorder's CSV is handed to the real
    `task3_timing_sample.project()` and must not be refused — a second projection here is how two
    figures for one campaign get quoted."""
    from scripts.task3_timing_sample import BANDS, band_of, project

    monkeypatch.setattr(T, "OUT_DIR", tmp_path)
    monkeypatch.setattr(T, "FOLDS_CSV", tmp_path / "folds.csv")
    rec = T.FoldRecorder({i: "A%02d" % i for i in range(1, 21)})
    spans = [1, 2, 7, 9, 13, 18, 22, 27, 37, 38, 38, 44, 120, 214, 222, 223, 315, 317, 329, 377]
    for i, span in enumerate(spans, start=1):
        rec.record(_Spec(i, "M" * span), _Result(pae=[[0.0]], record={"peak_vram": 100}), span / 10)
    path = rec.write()

    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    assert len(rows) == T.SAMPLE_N
    # every band is measured, so the projector must NOT refuse
    assert {band_of(int(r["span_aa"])) for r in rows} == {f"{lo}-{hi}" for lo, hi in BANDS}
    assert project(str(path)) == 0


def test_the_projector_refuses_a_partial_run_rather_than_projecting_over_it(tmp_path, monkeypatch):
    """⚠ A-017 (c) for the test above: with a band missing, the SAME call must return 1. Without
    this, `project(...) == 0` would prove only that the function runs."""
    from scripts.task3_timing_sample import project

    monkeypatch.setattr(T, "OUT_DIR", tmp_path)
    monkeypatch.setattr(T, "FOLDS_CSV", tmp_path / "partial.csv")
    rec = T.FoldRecorder({i: "A%02d" % i for i in range(1, 21)})
    for i, span in enumerate([1, 2, 7, 9], start=1):     # band 1 only
        rec.record(_Spec(i, "M" * span), _Result(record={"peak_vram": 100}), 1.0)
    assert project(str(rec.write())) == 1


# ── the VRAM question ───────────────────────────────────────────────────────────────────────

def test_vram_recovery_reports_a_recovering_series_as_recovering():
    rows = [{"free_mib_before": v} for v in (7043, 6980, 7010, 7043, 6990)]
    v = T.vram_recovery(rows)
    assert v["verdict"] == "recovers"
    assert v["series"] == [7043, 6980, 7010, 7043, 6990]


def test_vram_recovery_catches_F064s_actual_collapse():
    """⚠⚠ A-017 (c), and the fixture is the MEASURED collapse rather than an invented one:
    F-064 recorded 7043 -> 1649 MiB with a persistent child. If the new topology does not fix it,
    this is the shape the series takes, and the gate starts refusing mid-campaign."""
    rows = [{"free_mib_before": v} for v in (7043, 1649, 1649, 1649)]
    v = T.vram_recovery(rows)
    assert v["verdict"] == "DOES NOT RECOVER"
    assert v["lowest"] == 1649 and v["first"] == 7043
    assert "F-064" in v["detail"]


def test_vram_recovery_says_unmeasured_rather_than_recovers_when_nothing_was_read():
    """⚠ F-018. An absent reading must not be reported as a healthy one."""
    assert T.vram_recovery([{"free_mib_before": None}])["verdict"] == "unmeasured"
    assert T.vram_recovery([])["verdict"] == "unmeasured"


# ── the owner gate ──────────────────────────────────────────────────────────────────────────

def test_enqueue_without_the_owner_flag_never_builds_an_engine(monkeypatch, capsys):
    """⚠⚠ The dry run must not so much as connect. `DATABASE_URL` is deliberately absent here, so
    a code path that reached the database would raise KeyError rather than pass quietly.

    ⚠ Payloads are INJECTED rather than built from the span cache, so the guard that matters most
    — never write without the flag — runs on every platform including CI, instead of being
    skipped wherever a local artifact happens to be missing."""
    def _boom():
        raise AssertionError("the dry run built a database engine")

    fake = [{"accession": "Q8WXF7",
             "meta": {"fold_length": 1, "cohort_tranche": 1, "tier": "local"},
             "inference_settings": {"model_revision": "x"}}]
    monkeypatch.setattr(T, "run2_payloads", lambda: fake)
    monkeypatch.setattr(T, "_engine", _boom)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert T.main(["--enqueue"]) == 0
    out = capsys.readouterr().out
    assert "DRY RUN" in out and "nothing was written" in out
    assert "Q8WXF7" in out, "the dry run must ENUMERATE the population, not describe it"


def test_fold_without_an_enqueue_record_refuses(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(T, "ENQUEUED_JSON", tmp_path / "absent.json")
    assert T.main(["--fold", "--i-am-the-owner"]) == 1
    assert "Run --enqueue first" in capsys.readouterr().err


def test_report_without_a_fold_record_refuses(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(T, "FOLDS_CSV", tmp_path / "absent.csv")
    assert T.main(["--report"]) == 1
    assert "Nothing has been folded" in capsys.readouterr().err


def test_the_module_names_the_exception_it_is_and_refuses_to_generalise():
    """⚠ The one thing a later reader must not be able to miss: this is twenty rows, once."""
    src = (REPO / "scripts" / "task3_run2_folds.py").read_text(encoding="utf-8")
    assert "must not be cited as precedent" in src
    assert T.SAMPLE_N == 20 and T.RUN_LABEL == 2 and T.CAP_AA == 384


# ── the divergence guard (F-046) ────────────────────────────────────────────────────────────

def test_this_script_gates_exactly_as_the_production_worker_does():
    """⚠⚠ THE ONE PLACE THIS SCRIPT COULD DIVERGE FROM PRODUCTION, PINNED BEHAVIOURALLY.

    `worker.main.run()` builds its own fold callable and this script builds another, because the
    recorder needs the spec that `run()`'s lambda closes over. Two callables for one job is
    `F-046`'s shape — divergent parameters under one name — so both are DRIVEN here and their
    effects compared, rather than their source text being diffed. A source-text comparison is
    exactly the vacuous guard this repository catalogues.
    """
    import worker.main as WM
    from core.contracts import FoldSpec

    spec = FoldSpec(job_id=101, sequence="M" * 37, model_revision=WM.MODEL_REVISION,
                    dtype="int8", chunk_size=64, source="sliced_ecd",
                    ecd_start=1, ecd_end=37)

    def _fold_fn(sequence, **kw):
        return _Result(pae=[[0.0]], record={"peak_vram": 6357})

    seen: list[dict] = []

    def _preflight(length, dtype, chunk_size, **kw):
        seen.append({"length": length, "dtype": dtype, "chunk_size": chunk_size, **kw})
        return _Pf(length=length, free_mib=7043)

    posted: list[int] = []

    # 1 — production's call, through fold_from_spec exactly as run()'s lambda makes it
    WM.fold_from_spec(spec, _fold_fn, pae_post_fn=lambda jid, blob: posted.append(jid),
                      preflight_fn=_preflight)
    production = dict(seen[-1])

    # 2 — this script's call, through the extracted seam
    rec = T.FoldRecorder({101: "Q8NGZ5"})
    T.make_fold_callable(rec, lambda jid, blob: posted.append(jid), _fold_fn, _preflight)(spec)
    script = dict(seen[-1])

    assert script == production, (
        "the script gates on different parameters than production does — F-046, and the fold that "
        "was measured is not the fold that will run")
    # ⚠ margin_mib=0 and a MEASURED requirement are the two that must match, named explicitly so
    # a future change to either is visible here rather than only in the dict comparison.
    assert production["margin_mib"] == 0
    assert production["requirement_mib"] == 6357
    assert posted == [101, 101], "both paths must post the PAE to the D-036 route"
    assert len(rec.rows) == 1 and rec.rows[0]["free_mib_before"] == 7043


# ── the stranger check must ask EXACTLY the question the claim asks ──────────────────────────

def _queue_fixture(jobs):
    """A real queue: `(job_id, accession, tier, status)` rows through the real models.

    ⚠ SQLite is a fair substrate HERE and `F-056` is checked rather than waved at: the predicate
    under test is plain equality on a `tier` column, not a JSON path, so the two engines cannot
    disagree about it. A test that turned on JSON semantics would not belong on this substrate.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from db.models import Base, JobRecord, ProteinAnalysis

    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with Session(eng) as s:
        for jid, acc, tier, status in jobs:
            a = ProteinAnalysis(id=jid * 10, input_type="uniprot", input_value=acc, meta={})
            s.add(a)
            s.flush()
            s.add(JobRecord(id=jid, analysis_id=a.id, status=status, tier=tier,
                            inference_settings={}))
        s.commit()
    return eng


def _claimable(eng, tier="local"):
    from sqlalchemy.orm import Session

    with Session(eng) as s:
        return T._claimable_pending(s, tier)


def test_a_null_tier_pending_job_is_not_a_stranger():
    """⚠⚠ `core/queue.py`'s claim says it in its own comment: *`tier = :tier` is strict. A
    NULL-tier job is claimed by NOBODY, deliberately* — three-valued logic makes `NULL = 'local'`
    unknown, hence false. So a NULL-tier pending job cannot be folded by this run, and refusing
    to start because one exists refuses on a job that could never have been claimed."""
    eng = _queue_fixture([(1, "Q8WXF7", None, "pending")])
    assert _claimable(eng) == {}


def test_a_pending_job_of_ANOTHER_tier_is_not_a_stranger_either():
    """⚠ The same reasoning one step along, and it is why this filters on the tier rather than
    only on NULL: a pending `rental` job is exactly as unclaimable by a local worker as a
    NULL-tier one. Excluding only NULL would fix the symptom and leave the class."""
    eng = _queue_fixture([(1, "P04626", "rental", "pending"),
                          (2, "Q9NYQ8", "msa", "pending")])
    assert _claimable(eng) == {}


def test_a_CLAIMABLE_stranger_still_triggers_the_refusal():
    """⚠⚠ A-017 (c), and this is the clause that keeps the three tests above honest. Widen the
    filter too far — drop the status check, or return `{}` unconditionally — and this goes red.
    A guard that never fires is the vacuity this repository catalogues."""
    eng = _queue_fixture([(1, "Q8WXF7", "local", "pending"),      # one of the twenty
                          (2, "STRANGER", "local", "pending")])   # NOT one of the twenty
    claimable = _claimable(eng)
    assert claimable == {1: "Q8WXF7", 2: "STRANGER"}
    allowed = {1: "Q8WXF7"}
    assert {j: a for j, a in claimable.items() if j not in allowed} == {2: "STRANGER"}


def test_a_non_pending_job_is_not_claimable_whatever_its_tier():
    """⚠ The status half of the predicate, pinned separately so widening the tier half cannot
    silently take the status half with it."""
    eng = _queue_fixture([(1, "A", "local", "complete"),
                          (2, "B", "local", "failed"),
                          (3, "C", "local", "claimed")])
    assert _claimable(eng) == {}


def test_the_guard_asks_the_same_tier_the_run_will_pass_to_run_worker(monkeypatch):
    """⚠⚠ F-046 — divergent parameters under one name. If the guard checks `local` while the run
    claims `rental`, the guard is protecting a queue that will not be drained. One source for the
    tier, asserted rather than assumed."""
    monkeypatch.setenv("WORKER_TIER", "rental")
    assert T.worker_tier() == "rental"
    monkeypatch.delenv("WORKER_TIER", raising=False)
    assert T.worker_tier() == "local"

    eng = _queue_fixture([(1, "R", "rental", "pending"), (2, "L", "local", "pending")])
    assert _claimable(eng, T.worker_tier()) == {2: "L"}
    monkeypatch.setenv("WORKER_TIER", "rental")
    assert _claimable(eng, T.worker_tier()) == {1: "R"}


# ── the two defects the first run exposed, and it cost twenty jobs to find them ─────────────

def test_the_stop_condition_counts_ATTEMPTS_so_a_run_that_refuses_everything_terminates():
    """⚠⚠ THE DEFECT THAT LEFT THE LOOP POLLING FOREVER.

    `rec.rows` only grows on a fold that RETURNED. Every fold in the first run was refused by the
    gate, so nothing was ever recorded, `len(rec.rows)` stayed 0, and the stop condition could
    never be reached — the loop polled an empty queue until it was killed by hand.

    ⚠ A stop condition that is unreachable in the failure case is not a stop condition.
    """
    rec = T.FoldRecorder({i: "A%02d" % i for i in range(1, 21)})
    for job_id in range(1, 21):
        rec.attempted(job_id)          # claimed, then refused: nothing is ever recorded
    assert rec.rows == [], "the premise: a refused fold records nothing"
    assert rec.attempts == T.SAMPLE_N
    assert rec.attempts >= T.SAMPLE_N, "the stop condition must be reachable with zero recordings"


def test_attempts_and_rows_agree_when_folds_actually_succeed():
    """⚠ A-017 (c) partner: counting attempts must not stop counting successes. If `attempted`
    were never called on the success path, the stop condition would over-run past twenty."""
    rec = T.FoldRecorder({1: "Q8WXF7"})
    rec.attempted(1)
    rec.record(_Spec(1, "M"), _Result(pae=[[0.0]]), 1.0)
    assert rec.attempts == 1 and len(rec.rows) == 1


def test_a_cpu_only_interpreter_is_refused_before_a_single_job_is_claimed(monkeypatch):
    """⚠⚠ LEARNED BY SPENDING TWENTY JOBS.

    The first run was started under the interpreter on PATH — `torch 2.13.0+cpu`. `preflight`
    could not read free VRAM, every fold was correctly refused as `refused_no_measurement`, and
    `run_worker` reported each refusal as a deterministic failure: all twenty marked `failed`
    with **no fold attempted** and the GPU idle at 7,899 MiB free throughout.

    ⚠ The gate behaved exactly as designed. The campaign was started in a process that could
    never satisfy it, and that was checkable before anything was spent.
    """
    import torch

    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    ok, why = T.cuda_ready()
    assert ok is False
    assert "cuda.is_available() = False" in why
    assert "failed without a fold being attempted" in why, (
        "the refusal must say what it COSTS, not only what is wrong")


def test_a_cuda_interpreter_passes_the_same_check(monkeypatch):
    """⚠ A-017 (c). Without this, `cuda_ready` returning False unconditionally would pass above."""
    import torch

    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    ok, why = T.cuda_ready()
    assert ok is True and "cuda available" in why


def test_requeue_is_keyed_on_JOB_ID_and_never_on_accession():
    """⚠⚠ F-024. Each of the twenty accessions has TWO jobs — the Run 1 original and this
    campaign's Run 2 row — so `core.enqueue.requeue_jobs`, which keys on the accession, could
    reach a Run 1 job. This one takes the ids from `enqueued.json` and nothing else.

    ⚠ A source assertion, and it is named as the weaker kind: what it pins is the ABSENCE of a
    call, which no behavioural test can observe without the production rows this must not touch.
    """
    import ast
    import inspect

    # ⚠⚠ THE DOCSTRING IS STRIPPED FIRST, AND THAT IS THE POINT. The first version of this test
    # asserted `"requeue_jobs" not in body` and went red against its OWN docstring, which names
    # the function precisely to explain why it is not called. A source guard that matches its own
    # documentation is measuring the comment, not the code.
    tree = ast.parse(inspect.getsource(T.requeue))
    fn = tree.body[0]
    stripped = ast.unparse(ast.Module(body=fn.body[1:], type_ignores=[]))
    assert "requeue_jobs" not in stripped, (
        "requeue_jobs keys on the accession and would reach Run 1")
    body = stripped
    assert "JobRecord.id.in_(" in body
    # ⚠ `ast.unparse` normalises quote style, so the check must not depend on it - a guard that
    # turns on `"` vs `'` is testing the unparser.
    assert "j.status == 'complete'" in body, "a complete job must never be reset"
    assert "'pending'" in body and "attempts = 0" in body
