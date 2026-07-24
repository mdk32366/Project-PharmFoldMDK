"""D-026 enqueue CLI (`core.enqueue.run`) — the prod invocation entry point.

Same shape as `worker/main.py`: it wires `build_manifest` (D-023) → a subset filter →
`enqueue_cohort` (D-026), with an engine + fetcher from the environment (injected here). The
one baked decision is **subset enqueuing** (`--accession` / `--bucket` / `--limit`), so the
first fold can be one local-tier target rather than all 82 — prove the path before A6000 spend.
Idempotency is D-026 (iii)'s, so subset-then-full is safe on the overlap by construction.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from core.enqueue import FetchedSequence, _build_engine, requeue_jobs, run, select_rows
from core.manifest import build_manifest
from core.queue import CLAIMED, COMPLETE, FAILED, PENDING
from db.models import Base, JobRecord, ProteinAnalysis

ROWS = build_manifest()
LOCAL_TARGET = "Q96NY8"      # NECTIN4 — local-tier sliced_ecd, a real marketed-ADC target


def _fake_fetch(accession: str) -> FetchedSequence:
    # long enough to slice any ECD span in the cohort (max folded end < 1700)
    return FetchedSequence(sequence="A" * 2500, uniprot_release="2024_06")


def _no_engine():
    raise AssertionError("engine must not be built on --dry-run")


@pytest.fixture
def engine():
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    return eng


# ── select_rows: the subset filter ────────────────────────────────────────────

def test_accession_selects_exactly_one_row():
    sel = select_rows(ROWS, accession=LOCAL_TARGET)
    assert len(sel) == 1
    assert sel[0].accession == LOCAL_TARGET and sel[0].tier == "local"


def test_bucket_filters_by_tier():
    sel = select_rows(ROWS, bucket="local")
    assert sel and all(r.tier == "local" for r in sel)


def test_limit_takes_n_foldable():
    sel = select_rows(ROWS, bucket="local", limit=1)
    assert len(sel) == 1 and sel[0].tier == "local" and not sel[0].excluded


def test_limit_drops_named_exclusions():
    # --limit counts FOLDABLE rows: the 2 named exclusions never consume a slot
    sel = select_rows(ROWS, limit=82)
    assert len(sel) == 80 and all(not r.excluded for r in sel)


def test_no_filter_is_the_whole_manifest():
    assert len(select_rows(ROWS)) == len(ROWS) == 82


# ── run(): filter → enqueue, with injected engine + fetch ─────────────────────

def test_run_accession_creates_one_analysis_and_one_job(engine):
    rc = run(["--accession", LOCAL_TARGET], engine_factory=lambda: engine, fetch=_fake_fetch)
    assert rc == 0
    with Session(engine) as s:
        assert s.scalar(select(func.count()).select_from(JobRecord)) == 1
        a = s.execute(
            select(ProteinAnalysis).where(ProteinAnalysis.input_value == LOCAL_TARGET)
        ).scalar_one()
        assert a.meta["tier"] == "local" and a.meta["sequence"]   # the folded residues are stored


def test_dry_run_touches_no_database(engine, capsys):
    rc = run(["--accession", LOCAL_TARGET, "--dry-run"],
             engine_factory=_no_engine, fetch=_fake_fetch)      # engine_factory must NOT be called
    assert rc == 0
    assert LOCAL_TARGET in capsys.readouterr().out


def test_no_match_is_nonzero_and_writes_nothing(engine):
    rc = run(["--accession", "NOPE"], engine_factory=lambda: engine, fetch=_fake_fetch)
    assert rc == 1
    with Session(engine) as s:
        assert s.scalar(select(func.count()).select_from(JobRecord)) == 0


# ── the important one: subset then full is idempotent on the overlap ──────────

def test_subset_then_full_cohort_idempotent_on_overlap(engine):
    run(["--accession", LOCAL_TARGET], engine_factory=lambda: engine, fetch=_fake_fetch)
    run([], engine_factory=lambda: engine, fetch=_fake_fetch)        # the full 82

    with Session(engine) as s:
        analyses = s.execute(
            select(ProteinAnalysis).where(ProteinAnalysis.input_value == LOCAL_TARGET)
        ).scalars().all()
        assert len(analyses) == 1                                    # NOT re-created
        jobs = s.execute(
            select(JobRecord).where(JobRecord.analysis_id == analyses[0].id)
        ).scalars().all()
        assert len(jobs) == 1
        # full cohort is 80 foldable jobs total (2 excluded), not 81
        assert s.scalar(select(func.count()).select_from(JobRecord)) == 80


# ── requeue: the deliberate re-fold path (D-044) ──────────────────────────────

def _seed_job(engine, accession: str, status: str, *, attempts: int = 3,
              error: str | None = "boom", pdb_path: str | None = None) -> int:
    """A protein_analyses row + a jobs row in `status` — the enqueue's output, reproduced
    directly so a requeue can act on it. Returns the job id."""
    with Session(engine) as s:
        pa = ProteinAnalysis(input_type="uniprot", input_value=accession,
                             structure_source="esmfold", pdb_path=pdb_path, meta={"gene": "SEED"})
        s.add(pa)
        s.flush()
        job = JobRecord(analysis_id=pa.id, status=status, attempts=attempts,
                        error=error, worker_id="w-old", inference_settings={})
        s.add(job)
        s.flush()
        jid = job.id
        s.commit()
    return jid


def test_requeue_resets_a_failed_job_to_pending(engine):
    jid = _seed_job(engine, "P11717", FAILED, attempts=3, error="CUDA OOM: 230 GiB")
    summary = requeue_jobs_on(engine, ["P11717"])
    assert summary.requeued == 1 and summary.skipped_complete == 0 and summary.not_found == []
    with Session(engine) as s:
        job = s.get(JobRecord, jid)
        assert job.status == PENDING          # claimable again
        assert job.attempts == 0              # a deliberate retry gets a full budget (D-044)
        assert job.error is None and job.claimed_at is None and job.worker_id is None


def test_requeue_resets_a_stuck_claimed_job(engine):
    # the real state of last night's five: crashed mid-fold, left claimed, no prod reaper
    jid = _seed_job(engine, "Q04721", CLAIMED, error=None)
    assert requeue_jobs_on(engine, ["Q04721"]).requeued == 1
    with Session(engine) as s:
        assert s.get(JobRecord, jid).status == PENDING


def test_requeue_never_touches_a_complete_job(engine):
    jid = _seed_job(engine, "Q96NY8", COMPLETE, attempts=1, error=None,
                    pdb_path="/data/artifacts/1/structure.pdb")
    summary = requeue_jobs_on(engine, ["Q96NY8"])
    assert summary.requeued == 0 and summary.skipped_complete == 1
    with Session(engine) as s:
        assert s.get(JobRecord, jid).status == COMPLETE     # a good fold is never destroyed


def test_requeue_reports_an_unknown_accession(engine):
    summary = requeue_jobs_on(engine, ["NOPE"])
    assert summary.requeued == 0 and summary.not_found == ["NOPE"]


def test_run_requeue_exits_nonzero_on_unknown_and_zero_on_success(engine):
    _seed_job(engine, "P11717", FAILED)
    assert run(["--requeue", "P11717"], engine_factory=lambda: engine, fetch=_fake_fetch) == 0
    assert run(["--requeue", "NOPE"], engine_factory=lambda: engine, fetch=_fake_fetch) == 1


def test_run_requeue_never_fetches_and_creates_nothing(engine):
    # requeue only moves existing jobs — it must not fetch a sequence or write a new row
    def _boom_fetch(acc):
        raise AssertionError("requeue must not fetch sequences")
    _seed_job(engine, "P23471", FAILED)
    before = _job_count(engine)
    run(["--requeue", "P23471"], engine_factory=lambda: engine, fetch=_boom_fetch)
    assert _job_count(engine) == before             # no new job/analysis rows


def _job_count(engine) -> int:
    with Session(engine) as s:
        return s.scalar(select(func.count()).select_from(JobRecord))


def requeue_jobs_on(engine, accessions):
    with Session(engine) as s:
        return requeue_jobs(s, accessions)


# ── env wiring builds a real engine, with scheme normalization (D-012) ────────

def test_build_engine_reads_and_normalizes_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@host:5432/db")
    eng = _build_engine()
    assert eng.url.drivername == "postgresql+psycopg"               # normalized + a real engine
