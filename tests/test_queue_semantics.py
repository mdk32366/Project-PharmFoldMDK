"""SHAPE-ONLY coverage — the contract D-009 §1 implies, exercised via the fake.

These pin the *semantics* the queue's callers depend on: FIFO claim, a claimed
job not handed out twice, the status transitions, and stale-reap returning work
to pending with an incremented attempt count. They run against
``UnlockedFakeJobQueue``, so they establish that the contract is coherent and
that a correct implementation satisfies it — they establish **nothing** about
``PostgresJobQueue``'s SQL, and in particular nothing about the atomicity of
``claim`` under concurrent workers. That is the seam (D-012 §4) and only a
Postgres integration job proves across it.

The one exception is the reaping *edge*: the stale/not-stale decision comes from
the shared ``is_stale`` predicate (really covered in ``test_queue_rules``), so
the reap tests here inherit a real edge on top of a shape-only transition.
"""

from datetime import timedelta

import pytest

from core.queue import CLAIMED, COMPLETE, FAILED, PENDING
from doubles import UnlockedFakeJobQueue


@pytest.fixture
def q():
    return UnlockedFakeJobQueue()


def test_claim_returns_none_when_empty(q):
    assert q.claim("w1") is None


def test_claim_returns_oldest_pending_first(q):
    q.now = q.now  # BASE
    first = q.enqueue(analysis_id=1)
    q.now = q.now + timedelta(seconds=1)
    q.enqueue(analysis_id=2)
    assert q.claim("w1").id == first          # FIFO by created_at (D-009 §1)


def test_claim_does_not_hand_out_the_same_job_twice(q):
    q.enqueue(1)
    q.enqueue(2)
    a = q.claim("w1")
    b = q.claim("w2")
    assert a.id != b.id
    # NOTE: single-threaded. This is the semantic ("claimed jobs aren't re-served"),
    # NOT proof of atomicity under real concurrency — that lives below the seam.


def test_claim_stamps_status_worker_and_time(q):
    q.enqueue(1)
    j = q.claim("worker-A")
    assert j.status == CLAIMED
    assert j.worker_id == "worker-A"
    assert j.claimed_at == q.now


def test_complete_transitions_and_stamps(q):
    q.enqueue(1)
    j = q.claim("w1")
    q.complete(j.id)
    row = q.get(j.id)
    assert row.status == COMPLETE and row.completed_at == q.now


def test_fail_records_error_and_marks_failed(q):
    q.enqueue(1)
    j = q.claim("w1")
    q.fail(j.id, "CUDA out of memory")
    row = q.get(j.id)
    assert row.status == FAILED and row.error == "CUDA out of memory"


def test_reap_returns_stale_claim_to_pending_and_increments_attempts(q):
    jid = q.enqueue(1)
    q.claim("w1")
    q.now = q.now + timedelta(minutes=30, seconds=1)      # just over the edge
    assert q.reap_stale() == 1
    row = q.get(jid)
    assert row.status == PENDING
    assert row.attempts == 1
    assert row.claimed_at is None and row.worker_id is None


def test_reap_leaves_a_fresh_claim_untouched(q):
    jid = q.enqueue(1)
    q.claim("w1")
    q.now = q.now + timedelta(minutes=30)                 # exactly the edge — not stale
    assert q.reap_stale() == 0
    assert q.get(jid).status == CLAIMED


def test_reap_ignores_complete_and_failed_jobs(q):
    done = q.enqueue(1)
    bad = q.enqueue(2)
    q.claim("w1")
    q.complete(done)
    q.claim("w1")
    q.fail(bad, "boom")
    q.now = q.now + timedelta(hours=2)
    assert q.reap_stale() == 0                            # only CLAIMED is reapable


def test_reaping_retries_below_the_cap_then_terminates_at_it(q):
    """D-009 §1 Amendment 1: retry budget = 3. A vanished worker is retried, but a
    job whose worker keeps vanishing terminates at ``attempts == MAX_ATTEMPTS`` with
    a distinguishable reason — a deterministic host-crasher can't be re-dispatched
    without limit."""
    jid = q.enqueue(1)
    # First two reaps: still retried, back to pending.
    for expected in (1, 2):
        q.claim("w1")
        q.now = q.now + timedelta(minutes=31)
        q.reap_stale()
        assert q.get(jid).status == PENDING
        assert q.get(jid).attempts == expected
    # Third reap hits the cap: terminal, marked reaped-out.
    q.claim("w1")
    q.now = q.now + timedelta(minutes=31)
    q.reap_stale()
    row = q.get(jid)
    assert row.status == FAILED
    assert row.attempts == 3
    assert "[reaped-out]" in row.error          # distinguishable from an explicit fail


def test_explicit_fail_preserves_attempts_history(q):
    """D-009 §1 Amendment 2: an explicit fail is terminal and leaves ``attempts``
    untouched. A job reaped twice then failing explicitly must still read
    ``attempts == 2`` — the history is part of the diagnosis, not to be zeroed —
    and its error must be the worker's own message, NOT the reaped-out marker."""
    jid = q.enqueue(1)
    for _ in range(2):
        q.claim("w1")
        q.now = q.now + timedelta(minutes=31)
        q.reap_stale()
    assert q.get(jid).attempts == 2 and q.get(jid).status == PENDING

    q.claim("w1")
    q.fail(jid, "CUDA OOM on a 512-residue input")
    row = q.get(jid)
    assert row.status == FAILED
    assert row.attempts == 2                    # preserved, not zeroed
    assert row.error == "CUDA OOM on a 512-residue input"
    assert "[reaped-out]" not in row.error      # a real error, told apart from budget-exhaustion
