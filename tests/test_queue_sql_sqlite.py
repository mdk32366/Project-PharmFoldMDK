"""REAL SQL coverage — ``PostgresJobQueue``'s portable methods, run against SQLite.

This is the payoff of D-009 §1's amendments making the transitions portable: the
production code path for ``complete`` / ``fail`` / ``reap_stale`` executes here for
real, on a real (SQLite) database, not a fake. Only ``claim`` cannot — its ``FOR
UPDATE SKIP LOCKED`` is a syntax error on SQLite (D-012 §3), and that boundary is
itself asserted below. So the unproven surface is exactly ``SKIP LOCKED`` atomicity
and nothing wider.

Naive UTC datetimes throughout: SQLite's DateTime doesn't carry tz, and the queue's
injected clock lets us pin time deterministically. Production Postgres uses
timestamptz; the code handles both.
"""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import OperationalError

from core.queue import MAX_ATTEMPTS, PostgresJobQueue
from db.models import Base, JobRecord

BASE = datetime(2026, 1, 1, 12, 0, 0)          # naive UTC; SQLite-friendly
JOBS = JobRecord.__table__


@pytest.fixture
def engine():
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)              # NB: create_all, NOT the migration chain (D-005)
    return eng


def _insert(engine, **kw) -> int:
    values = dict(analysis_id=1, status="pending", attempts=0,
                  inference_settings={}, created_at=BASE)
    values.update(kw)
    with engine.begin() as conn:
        return conn.execute(JOBS.insert().values(**values)).inserted_primary_key[0]


def _row(engine, job_id: int):
    with engine.begin() as conn:
        return conn.execute(select(JOBS).where(JOBS.c.id == job_id)).mappings().first()


def _queue(engine, now=BASE):
    return PostgresJobQueue(engine, clock=lambda: now)


def test_complete_runs_as_real_sql(engine):
    jid = _insert(engine, status="claimed", claimed_at=BASE, worker_id="w1")
    _queue(engine).complete(jid)
    row = _row(engine, jid)
    assert row["status"] == "complete" and row["completed_at"] is not None


def test_fail_runs_as_real_sql_and_preserves_attempts(engine):
    # Amendment 2: explicit fail is terminal and leaves attempts alone.
    jid = _insert(engine, status="claimed", attempts=2, claimed_at=BASE, worker_id="w1")
    _queue(engine).fail(jid, "CUDA OOM on a 512-residue input")
    row = _row(engine, jid)
    assert row["status"] == "failed"
    assert row["error"] == "CUDA OOM on a 512-residue input"
    assert row["attempts"] == 2                                 # preserved, not zeroed


def test_reap_requeues_stale_below_cap(engine):
    jid = _insert(engine, status="claimed", attempts=0, claimed_at=BASE, worker_id="w1")
    q = _queue(engine, now=BASE + timedelta(minutes=60, seconds=1))     # just over
    assert q.reap_stale() == 1
    row = _row(engine, jid)
    assert row["status"] == "pending" and row["attempts"] == 1 and row["claimed_at"] is None


def test_reap_terminates_at_cap_with_marker(engine):
    # Amendment 1: the reap that reaches MAX_ATTEMPTS is terminal + [reaped-out].
    jid = _insert(engine, status="claimed", attempts=MAX_ATTEMPTS - 1, claimed_at=BASE, worker_id="w1")
    q = _queue(engine, now=BASE + timedelta(minutes=61))
    assert q.reap_stale() == 1
    row = _row(engine, jid)
    assert row["status"] == "failed"
    assert row["attempts"] == MAX_ATTEMPTS
    assert "[reaped-out]" in row["error"]


def test_reap_boundary_exactly_at_threshold_is_not_reaped(engine):
    # Strict boundary shared with is_stale: 30:00 exactly is not yet stale.
    _insert(engine, status="claimed", attempts=0, claimed_at=BASE, worker_id="w1")
    q = _queue(engine, now=BASE + timedelta(minutes=60))
    assert q.reap_stale() == 0


def test_reap_ignores_non_claimed_rows(engine):
    _insert(engine, status="pending", created_at=BASE)
    _insert(engine, status="complete", claimed_at=BASE)
    _insert(engine, status="failed", claimed_at=BASE)
    q = _queue(engine, now=BASE + timedelta(hours=5))
    assert q.reap_stale() == 0                                  # only CLAIMED is reapable


def test_claim_is_unsupported_on_sqlite(engine):
    # THE seam boundary, asserted. FOR UPDATE SKIP LOCKED is a syntax error here
    # (D-012 §3); claim's atomicity is provable only by the Postgres integration job.
    _insert(engine, status="pending", created_at=BASE)
    with pytest.raises(OperationalError):
        _queue(engine).claim("w1")


def test_analysis_id_fk_closes_amendment_4(engine):
    # D-009 §1 Amendment 4 CLOSED in D-019. The prior guard (test_analysis_id_has_no_fk_yet)
    # was confirmed to fail on exactly the FK-exists assertion before this replaced it — the
    # "fail on the event" discipline. Now assert the positive: the FK is present and points at
    # protein_analyses.
    fks = JOBS.c.analysis_id.foreign_keys
    assert len(fks) == 1
    assert next(iter(fks)).target_fullname == "protein_analyses.id"
