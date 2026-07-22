"""The four worker→Fly routes (D-031), thin over ``app/artifacts.py``.

Each route is the HTTP realization of one ``QueueClient`` method the loop defined
(D-030). The handlers stay thin on purpose: claim projection, the transaction boundary,
and the ordering check all live in ``app.artifacts`` where they are unit-tested without
HTTP, so a handler is only wiring + status codes.

| Route | Method | does |
|---|---|---|
| `/jobs/claim` | POST | claim + inline FoldSpec, or 204 |
| `/jobs/{id}/artifacts` | POST | persist files + post-fold columns (idempotent) |
| `/jobs/{id}/complete` | POST | flip status — 409 unless artifacts persisted |
| `/jobs/{id}/fail` | POST | terminal failure, delegates to the primitive |
"""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from pydantic import BaseModel

from app import artifacts as A
from app.deps import get_artifact_root, get_engine, get_queue, require_token

router = APIRouter()


class ClaimBody(BaseModel):
    worker_id: str


class FailBody(BaseModel):
    error: str


@router.post("/jobs/claim", dependencies=[Depends(require_token)])
def claim(body: ClaimBody, queue: Any = Depends(get_queue), engine: Any = Depends(get_engine)):
    """Claim → the fold spec inline (D-031 §1), or 204 when the queue is empty. A bare
    id is never returned — the eight-field body is the contract the loop folds from."""
    spec = A.build_fold_spec(queue, engine, body.worker_id)
    if spec is None:
        return Response(status_code=204)
    return asdict(spec)


@router.post("/jobs/{job_id}/artifacts", dependencies=[Depends(require_token)])
async def artifacts(
    job_id: int,
    pdb: UploadFile = File(...),
    plddt: UploadFile = File(...),
    provenance: UploadFile = File(...),
    pae: Optional[UploadFile] = File(None),
    engine: Any = Depends(get_engine),
    artifact_root: str = Depends(get_artifact_root),
):
    """Persist the fold — Volume files + the post-fold columns, in the ruled transaction
    boundary (D-031 (a)). Idempotent: a retried upload converges. PAE arrives already
    gzipped and is stored verbatim (the route never compresses)."""
    pdb_text = (await pdb.read()).decode("utf-8")
    plddt_list = json.loads(await plddt.read())
    provenance_dict = json.loads(await provenance.read())
    pae_gz = await pae.read() if pae is not None else None
    try:
        A.persist_fold(engine, artifact_root, job_id, pdb=pdb_text, plddt=plddt_list,
                       pae_gz=pae_gz, provenance=provenance_dict)
    except A.AnalysisNotFound:
        raise HTTPException(status_code=404, detail="unknown job")
    return Response(status_code=204)


@router.post("/jobs/{job_id}/complete", dependencies=[Depends(require_token)])
def complete(job_id: int, queue: Any = Depends(get_queue), engine: Any = Depends(get_engine)):
    """Flip status to complete — but only if the upload actually committed (D-031 (c)).
    The 409 makes the forbidden state (complete with no structure, D-030 §3) unreachable
    by a client that calls the routes out of order, not merely by a well-behaved loop."""
    if not A.artifacts_present(engine, job_id):
        raise HTTPException(status_code=409, detail="artifacts not persisted; upload before complete")
    queue.complete(job_id)
    return Response(status_code=204)


@router.post("/jobs/{job_id}/fail", dependencies=[Depends(require_token)])
def fail(job_id: int, body: FailBody, queue: Any = Depends(get_queue)):
    """Terminal failure — delegates to the primitive, which leaves ``attempts`` untouched
    (D-009 §1 Amendment 2). No re-implementation of queue logic here (D-031)."""
    queue.fail(job_id, body.error)
    return Response(status_code=204)
