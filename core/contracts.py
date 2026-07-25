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

# Per-tier fold recipe (D-018 / S-003), resolved at fold-time by `build_fold_spec` (D-047).
#
# It lives HERE, not in `core/enqueue.py`, for the same reason `FoldSpec` does: the serving
# tier (`app/artifacts.py`) must resolve it, and `core/enqueue.py` imports `worker.runner` at
# module load — which the serving image does not contain (DEP-001). `core/contracts.py` is the
# serving-safe leaf (stdlib only), so importing `TIER_RECIPE` here drags no `worker/` in.
#
# Values are literals (mirroring `worker.runner`'s int8/64 fold defaults) rather than imports,
# so the recipe table stays worker-free. D-042: rental `chunk_size` was `None` (D-011's
# assumption that more VRAM makes chunking unnecessary); the first rental run FALSIFIED that —
# the ESMFold trunk's triangular attention is O(L³), so IGF2R (2,491 aa) asked 230 GiB on a
# 44 GiB card. No rentable card closes that gap; chunking is the only mitigation, so rental now
# chunks like local. This table is the authority; a job's stored `dtype`/`chunk_size` is a
# non-authoritative enqueue-time hint (D-047).
TIER_RECIPE: dict[str, dict] = {
    "local":  {"dtype": "int8", "chunk_size": 64},   # int8 / chunk-64 (S-003, worker default)
    "rental": {"dtype": "fp16", "chunk_size": 64},   # D-011 → D-042 (chunk was None)
}


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
