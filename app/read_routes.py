"""D-034 — the four public read routes the React UI (D-033) consumes.

Thin over ``app/reads.py`` (the query/projection logic is unit-tested there without HTTP,
the same discipline as ``routes.py`` over ``artifacts.py``). All four are ``GET`` under
``/api`` and carry **no** ``require_token`` — the read surface is unauthenticated by design
(D-034 decision 4: public UniProt structures, no PII), while the ``/jobs`` write routes stay
bearer-guarded. The auth *property* that keeps this honest — ``/jobs`` guarded, ``/api`` open,
no third category — is pinned by an introspecting test (D-034 decision 5), not by a check on
these handlers.

| Route | Returns |
|---|---|
| `GET /api/analyses` | light list — one object per row (no sequence/provenance) |
| `GET /api/analyses/{id}` | full record incl. `sequence` + `fold_provenance` |
| `GET /api/analyses/{id}/structure` | the stored PDB file, `text/plain`, streamed |
| `GET /api/analyses/{id}/plddt` | the per-residue pLDDT array |
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app import reads
from app.deps import get_engine

read_router = APIRouter(prefix="/api")


@read_router.get("/analyses")
def list_analyses(engine: Any = Depends(get_engine)) -> list[dict]:
    """The light list — every fold as a ranking-table row (D-034 decision 1). No credential."""
    return reads.list_analyses(engine)


@read_router.get("/analyses/{analysis_id}")
def get_analysis(analysis_id: int, engine: Any = Depends(get_engine)) -> dict:
    """The full record for one fold, incl. ``sequence`` + ``fold_provenance`` (D-034 decision 1)."""
    record = reads.get_analysis(engine, analysis_id)
    if record is None:
        raise HTTPException(status_code=404, detail="unknown analysis")
    return record


@read_router.get("/analyses/{analysis_id}/structure")
def get_structure(analysis_id: int, engine: Any = Depends(get_engine)) -> FileResponse:
    """Stream the PDB at the row's **stored** ``pdb_path`` as ``text/plain`` (D-034 decision 2).
    404 — never 500 — when the id is unknown or the fold has no structure. The path is the
    stored absolute one; no client value reaches the filesystem (§2a, traversal defence)."""
    pdb_path = reads.get_structure_path(engine, analysis_id)
    if not pdb_path or not Path(pdb_path).is_file():
        raise HTTPException(status_code=404, detail="no structure for this analysis")
    return FileResponse(pdb_path, media_type="text/plain", filename="structure.pdb")


@read_router.get("/analyses/{analysis_id}/plddt")
def get_plddt(analysis_id: int, engine: Any = Depends(get_engine)) -> list:
    """The per-residue pLDDT array that colours the viewer (D-034 decision 3). 404 when the id
    is unknown or the structure — and so its sibling ``plddt.json`` — does not exist."""
    plddt_path = reads.get_plddt_path(engine, analysis_id)
    if not plddt_path or not Path(plddt_path).is_file():
        raise HTTPException(status_code=404, detail="no plddt for this analysis")
    return json.loads(Path(plddt_path).read_text(encoding="utf-8"))


@read_router.get("/coverage")
def get_coverage(engine: Any = Depends(get_engine)) -> dict:
    """The D-038 coverage supplier UI Plan v2 §3.3/§4.1 need — the honest denominator the read
    list cannot give. The D-024 coverage object (partition over **all 82**, computed from the
    committed manifest, not the 42 folded rows) plus the per-target drill-down with `fold_status`
    joined from the DB. No credential (D-034 posture)."""
    return reads.coverage_payload(engine)
