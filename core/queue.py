"""Job-queue contract (D-009 §1, seam per D-012 §4).

WHAT LIVES WHERE, and why it matters for what the tests can honestly prove:

- ``is_stale`` is a **pure predicate** — arithmetic on two timestamps, no database,
  no concurrency. It is the reaping *decision* ("is this claim older than the
  threshold?"). It ships as production code and is exercised directly and
  exhaustively, boundaries included. This is **real coverage**.

- ``JobQueue`` is the **seam**. Its one genuinely Postgres-specific operation is
  ``claim`` — the atomic ``SELECT … FOR UPDATE SKIP LOCKED`` that lets a worker
  take a job without a second worker taking the same one. That atomicity is a
  **syntax error on SQLite** (`FOR UPDATE` is rejected outright — measured, D-012
  §3), so it cannot execute in the suite at all and is **never proven here**. Only
  a Postgres integration job (D-012 §5, still absent) will ever prove it.

The split is deliberate: the reaping rule is testable and tested; the claim's
atomicity is isolated behind the seam and honestly labelled unproven, rather than
the whole queue disappearing behind "it's tested" when only its callers are.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Protocol

# Status vocabulary (D-009 §1).
PENDING = "pending"
CLAIMED = "claimed"
COMPLETE = "complete"
FAILED = "failed"

# D-009 §1: "a claimed job older than a threshold (initially 30 min)". 30 min is
# stated in the decision, so 1800 is faithful — NOT an invented number.
DEFAULT_STALE_SECONDS = 30 * 60

# Retry budget (D-009 §1 Amendment 1). NOT a round number: the host reliability
# floor is ~1 fatal bugcheck per several weeks (survive one host loss → retry), and
# a 630 aa fold is 4-for-4 fatal (a deterministic crasher → don't re-dispatch
# without limit). 3 is the smallest cap serving the first without over-serving the
# second: the original dispatch plus at most two retry-induced crashes.
MAX_ATTEMPTS = 3

# Marker on the `error` of a job that exhausted the budget by repeated reaping —
# the worker vanished every time and never reported anything. Greppable, and
# distinguishable from an explicit failure whose `error` is the worker's own
# message (D-009 §1 Amendment 1: the two terminal paths must be tellable apart).
#
# A STATIC string on purpose: it is bound as a single parameter into the portable
# reap UPDATE (below), so it must not depend on per-row values. The vanish COUNT is
# not embedded here — the `attempts` column already records it — which is what lets
# the reap SQL stay one dialect-agnostic statement rather than per-row string-building.
REAPED_OUT_PREFIX = "[reaped-out]"
REAPED_OUT_REASON = (
    f"{REAPED_OUT_PREFIX} retry budget of {MAX_ATTEMPTS} exhausted; the worker vanished on "
    f"every attempt without ever reporting an error (see the attempts column for the count)"
)


def is_stale(claimed_at: Optional[datetime], now: datetime,
             timeout_seconds: int = DEFAULT_STALE_SECONDS) -> bool:
    """Is a claim old enough to reap? Pure; the reaping *decision*.

    Threshold is **strict** (`age > timeout`), a decided boundary, not incidental:
    at exactly the threshold a claim is NOT yet stale — "older than 30 minutes"
    means age must *exceed* 30 minutes. So 29:59 → False, 30:00 → False, 30:01 →
    True. A job never claimed (`claimed_at is None`) is not stale.
    """
    if claimed_at is None:
        return False
    return (now - claimed_at).total_seconds() > timeout_seconds


@dataclass
class Job:
    """A fold-queue row (D-009 §1). Transient operational state, deliberately
    separate from the durable ``protein_analyses`` record."""

    id: int
    analysis_id: int
    status: str = PENDING
    attempts: int = 0
    worker_id: Optional[str] = None
    claimed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    inference_settings: dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None


class JobQueue(Protocol):
    """The seam (D-012 §4). Implemented for real by ``PostgresJobQueue`` (not yet
    written) and, for testing the *callers*, by ``tests/doubles.py``'s
    ``UnlockedFakeJobQueue`` — whose name states the property it does not provide.

    ``claim`` is the operation whose atomicity is Postgres-specific and unproven in
    this suite. ``complete`` / ``fail`` / ``reap_stale`` are portable status
    transitions and are honestly exercisable.
    """

    def claim(self, worker_id: str) -> Optional[Job]:
        """Atomically take the oldest pending job — **FIFO by ``created_at`` is
        contract** (D-009 §1 Amendment 3), so the query carries an explicit
        ``ORDER BY created_at, id``, not a reliance on the index. Mark it
        ``claimed``, stamp ``claimed_at`` and ``worker_id``; ``None`` when none
        pending. The **atomicity** is the one unproven part (the seam)."""
        ...

    def complete(self, job_id: int) -> None:
        """``claimed`` → ``complete``, stamp ``completed_at``. Portable transition."""
        ...

    def fail(self, job_id: int, error: str) -> None:
        """Explicit worker-reported failure: terminal ``failed``, record ``error``.
        **``attempts`` is left untouched** (D-009 §1 Amendment 2) — the count is
        history and must not be zeroed. Not retried: a caught error is usually
        deterministic, so retrying reproduces it (the worker already told you what
        is wrong). Contrast ``reap_stale``, which retries because absence is
        uninformative."""
        ...

    def reap_stale(self, timeout_seconds: int = DEFAULT_STALE_SECONDS) -> int:
        """Recover jobs whose worker vanished. Each stale ``claimed`` job has
        ``attempts`` incremented; if that reaches ``MAX_ATTEMPTS`` the job goes
        terminal ``failed`` with the ``REAPED_OUT_REASON`` marker, otherwise it
        returns to ``pending`` (D-009 §1 Amendment 1). Returns the number of stale
        claims handled (requeued or terminated). Portable transition."""
        ...


def _row_to_job(row: Any) -> Job:
    """Map a result-row mapping to a ``Job`` DTO. ``inference_settings`` arrives as a
    dict from psycopg (JSONB) but is coerced from a JSON string defensively."""
    settings = row["inference_settings"]
    if isinstance(settings, str):
        import json
        settings = json.loads(settings or "{}")
    return Job(
        id=row["id"], analysis_id=row["analysis_id"], status=row["status"],
        attempts=row["attempts"], worker_id=row["worker_id"],
        claimed_at=row["claimed_at"], completed_at=row["completed_at"],
        error=row["error"], inference_settings=settings or {},
        created_at=row["created_at"],
    )


class PostgresJobQueue:
    """The production ``JobQueue``.

    ``claim`` is the one Postgres-only, atomicity-critical operation — ``SELECT …
    FOR UPDATE SKIP LOCKED`` — and the only thing the seam leaves unproven: it is a
    **syntax error on SQLite** (D-012 §3), so it cannot run in the suite and only a
    Postgres integration job (D-012 §5, absent) can prove it. ``complete`` /
    ``fail`` / ``reap_stale`` are **portable, parameterized DML** and are exercised
    for real against SQLite in the tests — so the seam is specifically ``SKIP
    LOCKED``, nothing wider.

    Time comes from an injected ``clock``, not the database's ``now()``. That is
    deliberate: SQLite has no ``now()``, so DB-side time would make these methods
    untestable on SQLite and reopen the very gap the portability closes. At
    single-writer scale (D-004) app-vs-DB clock skew is a non-issue.
    """

    def __init__(self, engine: Any, clock: Any = None) -> None:
        from sqlalchemy import text  # local import keeps the pure predicate/DTO sqlalchemy-free
        self._text = text
        self._engine = engine
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def claim(self, worker_id: str) -> Optional[Job]:
        sql = self._text(
            """
            UPDATE jobs SET status = 'claimed', claimed_at = :now, worker_id = :w
            WHERE id = (
                SELECT id FROM jobs
                WHERE status = 'pending'
                ORDER BY created_at, id          -- FIFO is contract (Amendment 3)
                FOR UPDATE SKIP LOCKED            -- the seam: Postgres-only, unproven here
                LIMIT 1
            )
            RETURNING id, analysis_id, status, attempts, worker_id,
                      claimed_at, completed_at, error, inference_settings, created_at
            """
        )
        with self._engine.begin() as conn:
            row = conn.execute(sql, {"now": self._clock(), "w": worker_id}).mappings().first()
        return _row_to_job(row) if row else None

    def complete(self, job_id: int) -> None:
        with self._engine.begin() as conn:
            conn.execute(
                self._text("UPDATE jobs SET status = 'complete', completed_at = :now WHERE id = :id"),
                {"now": self._clock(), "id": job_id},
            )

    def fail(self, job_id: int, error: str) -> None:
        # attempts deliberately untouched (Amendment 2): history, not to be zeroed.
        with self._engine.begin() as conn:
            conn.execute(
                self._text("UPDATE jobs SET status = 'failed', error = :e WHERE id = :id"),
                {"e": error, "id": job_id},
            )

    def reap_stale(self, timeout_seconds: int = DEFAULT_STALE_SECONDS) -> int:
        # Strict boundary matches is_stale: claimed_at < (now - timeout) ⟺ age > timeout,
        # so a claim exactly at the threshold is NOT reaped. One dialect-agnostic UPDATE;
        # the CASE branches requeue-vs-terminate on the incremented attempt count.
        cutoff = self._clock() - timedelta(seconds=timeout_seconds)
        with self._engine.begin() as conn:
            result = conn.execute(
                self._text(
                    """
                    UPDATE jobs
                    SET attempts   = attempts + 1,
                        claimed_at = NULL,
                        worker_id  = NULL,
                        status = CASE WHEN attempts + 1 >= :max THEN 'failed' ELSE 'pending' END,
                        error  = CASE WHEN attempts + 1 >= :max THEN :reason ELSE error END
                    WHERE status = 'claimed' AND claimed_at < :cutoff
                    """
                ),
                {"max": MAX_ATTEMPTS, "reason": REAPED_OUT_REASON, "cutoff": cutoff},
            )
            return result.rowcount
