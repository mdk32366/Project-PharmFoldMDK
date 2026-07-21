"""Test doubles. NOT coverage of the real queue — read the class docstring.

Imported as a top-level module (`from doubles import ...`) because pytest's
prepend import mode puts `tests/` on `sys.path` (same mechanism `conftest.py`
relies on).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from core.queue import (
    CLAIMED,
    COMPLETE,
    DEFAULT_STALE_SECONDS,
    FAILED,
    MAX_ATTEMPTS,
    PENDING,
    REAPED_OUT_REASON,
    Job,
    is_stale,
)


class UnlockedFakeJobQueue:
    """An in-memory ``JobQueue`` for testing the queue's *callers* without a
    database.

    THE NAME IS THE HONESTY BOUNDARY. ``Unlocked`` states the exact property this
    does not provide: it does **no locking**. Its ``claim`` is a plain
    single-threaded scan-and-mark, so it exercises the *semantics* callers depend
    on (oldest-first, claimed jobs aren't handed out twice) but proves **nothing**
    about ``SELECT … FOR UPDATE SKIP LOCKED`` — not its syntax, not its behaviour
    under two workers. It was not named ``InMemoryJobQueue`` or ``SqliteJobQueue``
    precisely because those read as "the queue is tested"; a name travels further
    than a log entry (D-012 §4).

    The reaping *decision* it makes comes from the shared ``is_stale`` predicate,
    so the boundary arithmetic here is the same code that would run in prod. The
    status *transitions* it performs are the fake's own — faithful to D-009 §1,
    but not the production SQL.

    A settable ``now`` clock makes staleness deterministic without patching time.
    """

    def __init__(self) -> None:
        self._jobs: dict[int, Job] = {}
        self._next_id = 1
        # Deterministic, injectable clock. Tests set/advance it directly.
        self.now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    # ── test-state construction (not part of the JobQueue seam) ──────────────
    def enqueue(self, analysis_id: int, inference_settings: Optional[dict[str, Any]] = None,
                created_at: Optional[datetime] = None) -> int:
        jid = self._next_id
        self._next_id += 1
        self._jobs[jid] = Job(
            id=jid, analysis_id=analysis_id, status=PENDING,
            inference_settings=inference_settings or {},
            created_at=created_at or self.now,
        )
        return jid

    def get(self, job_id: int) -> Job:
        return self._jobs[job_id]

    # ── the JobQueue seam ────────────────────────────────────────────────────
    def claim(self, worker_id: str) -> Optional[Job]:
        pending = [j for j in self._jobs.values() if j.status == PENDING]
        if not pending:
            return None
        # FIFO by created_at is CONTRACT (D-009 §1 Amendment 3), id as tiebreak. NO
        # locking — a real second worker could take the same row; that atomicity is
        # the one thing the seam leaves unproven.
        job = min(pending, key=lambda j: (j.created_at, j.id))
        job.status = CLAIMED
        job.claimed_at = self.now
        job.worker_id = worker_id
        return job

    def complete(self, job_id: int) -> None:
        job = self._jobs[job_id]
        job.status = COMPLETE
        job.completed_at = self.now

    def fail(self, job_id: int, error: str) -> None:
        # Explicit, worker-reported → terminal, attempts UNTOUCHED (D-009 §1
        # Amendment 2): the count is history, not to be zeroed.
        job = self._jobs[job_id]
        job.status = FAILED
        job.error = error

    def reap_stale(self, timeout_seconds: int = DEFAULT_STALE_SECONDS) -> int:
        handled = 0
        for job in self._jobs.values():
            if job.status == CLAIMED and is_stale(job.claimed_at, self.now, timeout_seconds):
                job.attempts += 1
                job.claimed_at = None
                job.worker_id = None
                if job.attempts >= MAX_ATTEMPTS:
                    # Budget exhausted by repeated vanishing (D-009 §1 Amendment 1):
                    # terminal, marked distinctly from an explicit failure.
                    job.status = FAILED
                    job.error = REAPED_OUT_REASON
                else:
                    job.status = PENDING
                handled += 1
        return handled
