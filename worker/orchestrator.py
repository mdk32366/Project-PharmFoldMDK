"""D-030 worker job-pull orchestration — the pure loop over an injected client.

Transport-agnostic by construction: the loop talks to a `QueueClient` protocol
(claim / upload / complete / fail) and an injected `fold`, so it is fully testable
with doubles and no GPU. **The concrete HTTP realization of `QueueClient` and the
Fly endpoint it calls are D-031** — this module defines the interface *by needing
it*, and that method list is the route list D-031 must expose.

Done-ordering (D-030 §3): `upload → (server persists) → complete`, never the
reverse. The loop calls `complete` ONLY after `upload` is confirmed; a worker that
dies between them leaves a `claimed` job that reaps and re-folds — wasteful, safe.
The forbidden state is a `complete` job with no structure behind it.

Failure taxonomy (D-030 §4):
  - **Transport** (claim / upload / complete raise `TransportError`) → retried;
    DB state untouched. Retried rather than re-folded because a rental-tier
    re-fold is PAID and a re-upload is not — which requires the endpoint to be
    idempotent server-side (D-031's obligation).
  - **Deterministic fold failure** (`FoldError`: CUDA OOM, malformed sequence) →
    reported via `fail()`; terminal, `attempts` left untouched (D-009 §1 Am. 2).
  - **Vanished worker** is not this module's concern — `reap_stale` + `MAX_ATTEMPTS`
    handle it server-side.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Protocol

from core.contracts import FoldSpec  # re-exported: FoldSpec now lives in the tier-neutral
# contracts module (DEP-001) so `app/` imports it without pulling `worker/` into the Fly
# image. The loop and its tests still `from worker.orchestrator import FoldSpec` unchanged.

log = logging.getLogger(__name__)


class TransportError(Exception):
    """A connectivity failure talking to the Fly endpoint. Retryable, no DB effect."""


class FoldError(Exception):
    """A deterministic fold failure (CUDA OOM, malformed sequence). The same recurs
    on retry, so it is reported via `fail()`, not retried. The real runner must
    raise this for its known failure modes."""


# FoldSpec is defined in core/contracts.py (DEP-001 relocation) and imported at the top of
# this module; it remains part of the orchestrator's public surface by re-export, so the
# claim contract still reads as "what the loop's client returns" right here.


class QueueClient(Protocol):
    """The interface the loop needs. Its concrete HTTP implementation is D-031; the
    method list here IS the route list D-031 must expose. Each network method raises
    `TransportError` on a connectivity failure."""

    def claim(self, worker_id: str) -> "FoldSpec | None": ...
    def upload(self, job_id: int, artifacts: Any) -> None: ...   # persists server-side; idempotent
    def complete(self, job_id: int) -> None: ...                 # flips status; ONLY after upload
    def fail(self, job_id: int, error: str) -> None: ...         # terminal


# spec -> artifacts (a FoldResult in prod). Injected: GPU-bound in prod, faked in tests.
Fold = Callable[[FoldSpec], Any]


def _submit(fn: Callable[..., None], *args: Any,
            attempts: int, sleep: Callable[[float], None], interval: float) -> bool:
    """Push a report through the transport, retrying on `TransportError`. Returns
    True if it landed, False if it gave up (the job reaps and retries — safe).
    Retrying is cheap; re-folding a rental target is paid, so retries are exhausted
    before letting go."""
    for i in range(attempts):
        try:
            fn(*args)
            return True
        except TransportError as e:
            log.warning("transport failure on %s (attempt %d/%d): %s",
                        getattr(fn, "__name__", fn), i + 1, attempts, e)
            if i < attempts - 1:
                sleep(interval)
    return False


def run_worker(
    client: QueueClient,
    fold: Fold,
    worker_id: str,
    *,
    poll_interval: float = 5.0,
    sleep: Callable[[float], None] = time.sleep,
    should_stop: Callable[[], bool] = lambda: False,
    submit_attempts: int = 5,
) -> None:
    """Poll → claim → fold → upload → complete, until `should_stop()`.

    The only place fold happens is between a successful claim and the upload; a
    fold NEVER runs twice for one claim (transport failures retry the report, not
    the fold), which is the loop's cost-control guarantee on a paid card."""
    while not should_stop():
        try:
            spec = client.claim(worker_id)
        except TransportError:
            sleep(poll_interval)          # §4: DB untouched, retry next poll
            continue
        if spec is None:
            sleep(poll_interval)          # empty queue
            continue

        try:
            artifacts = fold(spec)
        except FoldError as e:            # §4: deterministic → terminal fail()
            _submit(client.fail, spec.job_id, str(e),
                    attempts=submit_attempts, sleep=sleep, interval=poll_interval)
            continue

        # §3 done-ordering: upload MUST land before complete is even attempted.
        if not _submit(client.upload, spec.job_id, artifacts,
                       attempts=submit_attempts, sleep=sleep, interval=poll_interval):
            continue                      # upload never landed → do NOT complete; job reaps
        _submit(client.complete, spec.job_id,
                attempts=submit_attempts, sleep=sleep, interval=poll_interval)
