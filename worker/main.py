"""Worker entry point — start the D-030 loop against the D-031 Fly transport (D-004).

Runs on the local GPU box, **NOT** on Fly. It wires three already-built, already-ruled pieces
and adds nothing the log has not decided:
  - the concrete transport client (`worker/http_client.py`, D-031) pointed at the Fly app,
  - the pure job-pull loop (`worker/orchestrator.py`, D-030),
  - the GPU fold-runner (`worker/runner.py`, D-018) as the injected `fold`.

Config comes from the environment, like the serving tier's `app/config.py`: the transport URL,
the shared bearer token that **must match** the app's `WORKER_AUTH_TOKEN` (D-031 §4), and a
`worker_id` label (a label, not a credential — D-031 §4). The real fold is GPU-bound and is the
owner's to run on the box; everything here is importable and tested without CUDA because
`torch` is imported lazily inside `runner.fold`.

Start it on the GPU box:

    WORKER_AUTH_TOKEN=<same-as-the-app> python -m worker.main
    # optional: TRANSPORT_URL=https://pharmfoldmdk.fly.dev  WORKER_ID=gpu-box-1
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

from worker.http_client import HttpQueueClient
from worker.orchestrator import FoldError, FoldSpec, run_worker
from worker.runner import MODEL_REVISION, fold, write_pae

log = logging.getLogger(__name__)

DEFAULT_TRANSPORT_URL = "https://pharmfoldmdk.fly.dev"


@dataclass(frozen=True)
class WorkerConfig:
    transport_url: str     # the Fly transport base URL the worker polls
    auth_token: str        # shared bearer secret; MUST match the app's WORKER_AUTH_TOKEN
    worker_id: str         # a lease label (D-031 §4), not a credential
    poll_interval: float = 5.0
    artifact_dir: Optional[str] = None   # D-036: set on the RENTAL box to persist PAE locally


def config_from_env() -> WorkerConfig:
    """Build worker config from the environment. `WORKER_AUTH_TOKEN` has no default — a
    missing token is a loud `KeyError`, never a silent unauthenticated poll.

    `WORKER_ARTIFACT_DIR` is the D-036 rental switch: **unset (the local tier) → no local
    persist**, behaviour and disk cost unchanged; set (the rented box) → each fold's PAE is
    written to `{dir}/{job_id}/` for out-of-band retrieval before pod termination."""
    return WorkerConfig(
        transport_url=os.environ.get("TRANSPORT_URL", DEFAULT_TRANSPORT_URL).rstrip("/"),
        auth_token=os.environ["WORKER_AUTH_TOKEN"],
        worker_id=os.environ.get("WORKER_ID", "local-gpu"),
        poll_interval=float(os.environ.get("WORKER_POLL_INTERVAL", "5")),
        artifact_dir=os.environ.get("WORKER_ARTIFACT_DIR"),
    )


def _persist_pae_local(result: Any, artifact_dir: str, job_id: int,
                       write_pae_fn: Callable[..., Any]) -> None:
    """Best-effort, rental-scoped local PAE write (D-036), keyed ``{artifact_dir}/{job_id}/``.

    **NON-FATAL by design.** A local write error must not propagate: it would crash the fold path
    *before* the upload, leaving the job to reap and **re-fold on a PAID card**. A missing local
    file is caught instead by the retrieval-verify step (`scripts/retrieve_rental_pae.py`), which
    is the blocking gate before pod termination — so a swallowed error here is loud downstream,
    not silent."""
    try:
        write_pae_fn(result, str(Path(artifact_dir) / str(job_id)))
    except Exception as e:  # noqa: BLE001 — deliberately swallowed; see docstring
        log.warning("local PAE persist failed for job %s: %s (retrieval-verify is the backstop)",
                    job_id, e)


def fold_from_spec(spec: FoldSpec, fold_fn: Callable[..., Any] = fold, *,
                   artifact_dir: Optional[str] = None,
                   write_pae_fn: Callable[..., Any] = write_pae) -> Any:
    """Adapt a claimed `FoldSpec` to the runner's `fold(...)` call.

    Guards that the job's pinned model revision matches this runner's (D-016/D-026): folding a
    different model than the manifest reviewed would be a provenance lie, so a mismatch fails the
    job **deterministically** — `FoldError` is reported via `fail()` and never retried (D-030 §4)
    — rather than silently folding the wrong model. `fold_fn` is injected in tests; in production
    it is the real GPU fold.

    When `artifact_dir` is set (the **rental** box, D-036), the fold's PAE is persisted locally
    here — inside the injected fold, so `orchestrator.run_worker` stays pure and transport-
    agnostic (it still only calls `fold(spec)`). The write is non-fatal (see `_persist_pae_local`)."""
    if spec.model_revision != MODEL_REVISION:
        raise FoldError(
            f"job pins model_revision {spec.model_revision!r} but this runner is "
            f"{MODEL_REVISION!r} — refusing to fold a different model than the manifest reviewed")
    result = fold_fn(
        spec.sequence,
        dtype=spec.dtype,
        chunk_size=spec.chunk_size,
        source=spec.source,
        ecd_start=spec.ecd_start,
        ecd_end=spec.ecd_end,
    )
    if artifact_dir:
        _persist_pae_local(result, artifact_dir, spec.job_id, write_pae_fn)
    return result


def build_client(config: WorkerConfig) -> HttpQueueClient:
    """The concrete transport client (D-031), carrying the shared bearer token on every call."""
    return HttpQueueClient(config.transport_url, config.auth_token)


def run(
    config: WorkerConfig | None = None,
    *,
    fold_fn: Callable[..., Any] = fold,
    run_worker_fn: Callable[..., None] = run_worker,
    **run_worker_kwargs: Any,
) -> None:
    """Build the client and drive the loop. `fold_fn` / `run_worker_fn` are injected in tests;
    in production they default to the real GPU fold and the real loop. This is the whole entry
    point — the loop, its retry/failure taxonomy, and the transport are all already built."""
    config = config or config_from_env()
    client = build_client(config)
    run_worker_fn(
        client,
        lambda spec: fold_from_spec(spec, fold_fn, artifact_dir=config.artifact_dir),
        config.worker_id,
        poll_interval=config.poll_interval,
        **run_worker_kwargs,
    )


def main() -> None:  # pragma: no cover — the production entry, exercised on the GPU box
    run()


if __name__ == "__main__":  # pragma: no cover
    main()
