"""THE seam's other half (D-017) — the tests SQLite structurally cannot run.

These execute against a real PostgreSQL (the `postgres` CI job's service container,
Postgres 16 per D-014). They prove the three things the SQLite suite cannot:

1. the Alembic **chain** builds the schema (`alembic upgrade head`, not create_all),
   and env.py's `search_path` SET ran without error (or the upgrade would have failed);
2. `claim`'s `SELECT … FOR UPDATE SKIP LOCKED` is **atomic** — a locked row is skipped,
   a separate claimer takes the next, and all-locked yields None;
3. `complete` / `fail` / `reap_stale` (incl. the cap) behave identically on real PG.

Auto-skips without a postgresql `DATABASE_URL` (see the `pg_engine` fixture), so this
file is inert in the normal `test` job and runs only where a database exists.
"""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import text

from core.queue import MAX_ATTEMPTS, PostgresJobQueue

pytestmark = pytest.mark.postgres

BASE = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def _enqueue(engine, n=1, created_base=BASE):
    ids = []
    with engine.begin() as c:
        for i in range(n):
            rid = c.execute(
                text("INSERT INTO jobs (analysis_id, status, attempts, inference_settings, created_at) "
                     "VALUES (:a, 'pending', 0, '{}', :ts) RETURNING id"),
                {"a": 100 + i, "ts": created_base + timedelta(seconds=i)},
            ).scalar_one()
            ids.append(rid)
    return ids


def _row(engine, jid):
    with engine.connect() as c:
        return c.execute(text("SELECT status, attempts, error, claimed_at, completed_at "
                              "FROM jobs WHERE id = :id"), {"id": jid}).mappings().first()


# ── (1) the migration chain built the schema, on real Postgres ────────────────

def test_migration_chain_built_the_jobs_table(pg_engine):
    with pg_engine.connect() as c:
        cols = set(c.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name='jobs'"
        )).scalars().all())
    # If this passes, `alembic upgrade head` ran the whole chain against real PG and
    # env.py's Postgres-only search_path SET executed without error.
    assert {"id", "analysis_id", "status", "attempts", "worker_id",
            "claimed_at", "completed_at", "error", "inference_settings", "created_at"} <= cols

    with pg_engine.connect() as c:
        fks = c.execute(text(
            "SELECT COUNT(*) FROM information_schema.table_constraints "
            "WHERE table_name='jobs' AND constraint_type='FOREIGN KEY'"
        )).scalar_one()
    assert fks == 0, "analysis_id FK is deferred until protein_analyses exists (D-009 §1 Amendment 4)"


# ── (2) SKIP LOCKED atomicity — the thing nothing else in the repo can prove ──

def test_claim_skips_a_locked_row(pg_engine):
    """The crown jewel. Hold a lock on the oldest pending row in one open
    transaction; a claim on another connection must SKIP it and take the next."""
    a, b = _enqueue(pg_engine, 2)
    conn = pg_engine.connect()
    tx = conn.begin()
    locked = conn.execute(text(
        "SELECT id FROM jobs WHERE status='pending' ORDER BY created_at, id "
        "FOR UPDATE SKIP LOCKED LIMIT 1"
    )).scalar_one()
    assert locked == a                       # this transaction now holds row a
    try:
        job = PostgresJobQueue(pg_engine).claim("w2")
        assert job is not None
        assert job.id == b                   # SKIP LOCKED skipped the locked row a
    finally:
        tx.rollback()
        conn.close()


def test_claim_returns_none_when_every_pending_row_is_locked(pg_engine):
    _enqueue(pg_engine, 1)
    conn = pg_engine.connect()
    tx = conn.begin()
    conn.execute(text("SELECT id FROM jobs WHERE status='pending' FOR UPDATE SKIP LOCKED")).all()
    try:
        assert PostgresJobQueue(pg_engine).claim("w") is None
    finally:
        tx.rollback()
        conn.close()


def test_claim_is_fifo_and_marks_the_row(pg_engine):
    a, b = _enqueue(pg_engine, 2)
    q = PostgresJobQueue(pg_engine)
    first = q.claim("w1")
    assert first.id == a and first.status == "claimed" and first.worker_id == "w1"
    second = q.claim("w1")
    assert second.id == b                    # oldest-first, and a not handed out twice


# ── (3) portable transitions behave identically on real PG ────────────────────

def test_complete_and_fail_on_real_pg(pg_engine):
    a, b = _enqueue(pg_engine, 2)
    q = PostgresJobQueue(pg_engine)
    q.claim("w1")  # claims a
    q.complete(a)
    q.claim("w1")  # claims b
    q.fail(b, "CUDA OOM on a 512-residue input")
    assert _row(pg_engine, a)["status"] == "complete"
    rb = _row(pg_engine, b)
    assert rb["status"] == "failed" and rb["error"] == "CUDA OOM on a 512-residue input"
    assert rb["attempts"] == 0               # explicit fail leaves attempts untouched (Amendment 2)


def test_reap_requeues_then_caps_on_real_pg(pg_engine):
    (jid,) = _enqueue(pg_engine, 1)
    # Force it claimed with an old claimed_at, then reap with a clock past the window.
    with pg_engine.begin() as c:
        c.execute(text("UPDATE jobs SET status='claimed', claimed_at=:t, worker_id='w1' WHERE id=:id"),
                  {"t": BASE, "id": jid})
    reaper = PostgresJobQueue(pg_engine, clock=lambda: BASE + timedelta(minutes=31))

    for expected in range(1, MAX_ATTEMPTS):          # reaps 1 .. MAX-1: requeued
        assert reaper.reap_stale() == 1
        r = _row(pg_engine, jid)
        assert r["status"] == "pending" and r["attempts"] == expected
        with pg_engine.begin() as c:                 # re-claim for the next round
            c.execute(text("UPDATE jobs SET status='claimed', claimed_at=:t, worker_id='w1' WHERE id=:id"),
                      {"t": BASE, "id": jid})

    assert reaper.reap_stale() == 1                  # the reap that hits the cap
    r = _row(pg_engine, jid)
    assert r["status"] == "failed" and r["attempts"] == MAX_ATTEMPTS and "[reaped-out]" in r["error"]


def test_reap_leaves_a_fresh_claim_untouched_on_real_pg(pg_engine):
    (jid,) = _enqueue(pg_engine, 1)
    with pg_engine.begin() as c:
        c.execute(text("UPDATE jobs SET status='claimed', claimed_at=:t, worker_id='w1' WHERE id=:id"),
                  {"t": BASE, "id": jid})
    # exactly at the threshold — strict boundary, not stale
    reaper = PostgresJobQueue(pg_engine, clock=lambda: BASE + timedelta(minutes=30))
    assert reaper.reap_stale() == 0
    assert _row(pg_engine, jid)["status"] == "claimed"
