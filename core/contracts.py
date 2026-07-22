"""Tier-neutral contracts shared across the serving and worker tiers.

`FoldSpec` is the **claim contract**: the `/claim` route (serving tier, D-031) PRODUCES
it and the worker loop (D-030) CONSUMES it. It was first defined in
`worker/orchestrator.py` because D-030 discovered the protocol there — but it belongs to
neither tier exclusively, and leaving it in `worker/` would force the worker package into
the Fly image just to import one dataclass, against DEP-001. So it lives here, importable
by `app/` without dragging the worker's CUDA world into the serving image.
`worker.orchestrator` re-exports it, so every existing
`from worker.orchestrator import FoldSpec` keeps working and the loop's tests are unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FoldSpec:
    """What `claim()` returns — the fold INPUT carried INLINE, because the worker
    holds no database connection (D-030 topology). It is the denormalized join of
    a job's `inference_settings` and its analysis's stored sequence; the `/claim`
    route (D-031) must produce this, not a bare job id."""

    job_id: int
    sequence: str
    model_revision: str
    dtype: str
    chunk_size: int | None
    source: str            # sliced_ecd | whole
    ecd_start: int | None
    ecd_end: int | None
