"""D-031 — the transport's database + Volume work, kept out of the route handlers so
it is unit-testable without HTTP.

Three things live here, each the load-bearing part of a route:

- ``build_fold_spec`` — turns ``claim()``'s ``Job`` into the **inline** ``FoldSpec`` the
  loop requires (D-030/D-031 §1), joining the job's ``inference_settings`` to the
  sequence D-026 stored on the analysis. The worker never queries for its own input.

- ``persist_fold`` — the ruled transaction boundary (D-031 ruling (a)): write the
  Volume files first, then the DB row in one transaction, and **compensate** by
  deleting the files if the DB write fails, so neither an orphaned row (paths to a
  file that was never written) nor orphaned files (no row pointing at them) can
  persist. The Volume is not transactional; the compensation is how the route makes it
  *look* transactional, which is the honest bound at single-writer scale (D-004).

- ``artifacts_present`` — the endpoint-enforced ordering check (D-031 ruling (c)):
  ``pdb_path IS NOT NULL`` for the job's analysis is exactly "the upload transaction
  committed", so ``/complete`` can refuse to flip status before the structure exists.

The provenance projection (ruling (b)) is in ``_update_analysis``: columns where they
exist, the whole record into ``meta["fold_provenance"]`` so the §1a flags survive.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Callable, Optional

from sqlalchemy import select, update

from core.queue import Job
from db.models import JobRecord, ProteinAnalysis
from worker.orchestrator import FoldSpec

STRUCTURE_SOURCE = "esmfold"   # this structure came from our ESMFold runner (D-031 (b))


class AnalysisNotFound(Exception):
    """A job id with no jobs row / no analysis behind it — the route maps this to 404."""


# ── claim → inline FoldSpec (D-031 §1) ────────────────────────────────────────

def build_fold_spec(queue: Any, engine: Any, worker_id: str) -> Optional[FoldSpec]:
    """Claim a job and assemble the fold spec the worker folds from, inline. Returns
    ``None`` when the queue is empty. The sequence comes from the analysis D-026
    stored (``meta["sequence"]`` — the exact residues the manifest reviewed), the tier
    params from the job's ``inference_settings``; neither is re-fetched."""
    job: Optional[Job] = queue.claim(worker_id)
    if job is None:
        return None
    with engine.connect() as conn:
        meta = conn.execute(
            select(ProteinAnalysis.meta).where(ProteinAnalysis.id == job.analysis_id)
        ).scalar_one()
    s = job.inference_settings
    return FoldSpec(
        job_id=job.id,
        sequence=meta["sequence"],
        model_revision=s["model_revision"],
        dtype=s["dtype"],
        chunk_size=s["chunk_size"],
        source=s["source"],
        ecd_start=s["ecd_start"],
        ecd_end=s["ecd_end"],
    )


# ── the two collaborators persist_fold injects (defaults; overridden in tests) ─

def _write_files(artifact_root: str, job_id: int, *, pdb: str, plddt: list,
                 pae_gz: Optional[bytes], provenance: dict) -> dict[str, str]:
    """Write the fold artifacts to ``{artifact_root}/{job_id}/`` and return their paths.
    Mirrors ``worker/runner.write_artifacts`` file names. The PAE is stored as the
    client's gzip bytes **verbatim** — the route never compresses (D-031 PAE ruling)."""
    out = Path(artifact_root) / str(job_id)
    out.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}

    (out / "structure.pdb").write_text(pdb, encoding="utf-8")
    paths["pdb"] = str(out / "structure.pdb")
    (out / "plddt.json").write_text(json.dumps(plddt), encoding="utf-8")
    paths["plddt"] = str(out / "plddt.json")
    if pae_gz is not None:
        (out / "pae.json.gz").write_bytes(pae_gz)          # already compressed, stored as-is
        paths["pae"] = str(out / "pae.json.gz")
    (out / "provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    paths["provenance"] = str(out / "provenance.json")
    return paths


def _remove_files(artifact_root: str, job_id: int) -> None:
    """Compensating delete for a failed DB write — best-effort, never masks the
    original error."""
    shutil.rmtree(Path(artifact_root) / str(job_id), ignore_errors=True)


def _update_analysis(engine: Any, analysis_id: int, *, pdb_path: str,
                     mean_plddt: Optional[float], pae_json_path: Optional[str],
                     provenance: dict) -> None:
    """Project provenance onto the post-fold columns and merge the full record into
    ``meta["fold_provenance"]`` (D-031 (b)), in ONE transaction. Reads current meta so
    the pre-fold keys D-026 wrote (gene, sequence, tier, ECD bounds, …) are preserved."""
    with engine.begin() as conn:
        current = conn.execute(
            select(ProteinAnalysis.meta).where(ProteinAnalysis.id == analysis_id)
        ).scalar_one()
        merged = dict(current or {})
        merged["fold_provenance"] = provenance
        conn.execute(
            update(ProteinAnalysis)
            .where(ProteinAnalysis.id == analysis_id)
            .values(
                pdb_path=pdb_path,
                mean_plddt=mean_plddt,
                pae_json_path=pae_json_path,
                structure_source=STRUCTURE_SOURCE,
                meta=merged,
            )
        )


# ── the ruled transaction boundary (D-031 (a)) ───────────────────────────────

def persist_fold(
    engine: Any,
    artifact_root: str,
    job_id: int,
    *,
    pdb: str,
    plddt: list,
    pae_gz: Optional[bytes],
    provenance: dict,
    write_files: Callable[..., dict[str, str]] = _write_files,
    update_analysis: Callable[..., None] = _update_analysis,
) -> dict[str, str]:
    """Persist one fold: Volume files first, then the analysis row, compensating on
    DB failure. Idempotent — a retried upload re-writes the same paths and re-stamps
    the same row (D-031 §2). Raises ``AnalysisNotFound`` if the job has no analysis."""
    analysis_id = _analysis_id_for(engine, job_id)
    if analysis_id is None:
        raise AnalysisNotFound(f"no analysis for job {job_id}")

    paths = write_files(artifact_root, job_id, pdb=pdb, plddt=plddt,
                        pae_gz=pae_gz, provenance=provenance)
    try:
        update_analysis(
            engine, analysis_id,
            pdb_path=paths["pdb"],
            mean_plddt=provenance.get("mean_plddt"),
            pae_json_path=paths.get("pae"),        # None when the fold emitted no PAE
            provenance=provenance,
        )
    except Exception:
        _remove_files(artifact_root, job_id)       # no orphaned files (D-031 (a) step 4)
        raise
    return paths


# ── ordering check for /complete (D-031 (c)) ─────────────────────────────────

def _analysis_id_for(engine: Any, job_id: int) -> Optional[int]:
    with engine.connect() as conn:
        return conn.execute(
            select(JobRecord.analysis_id).where(JobRecord.id == job_id)
        ).scalar_one_or_none()


def artifacts_present(engine: Any, job_id: int) -> bool:
    """True iff the job's analysis has ``pdb_path`` set — i.e. the upload transaction
    committed. This is the server-side proof ``/complete`` requires before flipping
    status, making the forbidden state (complete with no structure) unreachable."""
    with engine.connect() as conn:
        pdb_path = conn.execute(
            select(ProteinAnalysis.pdb_path)
            .select_from(JobRecord)
            .join(ProteinAnalysis, JobRecord.analysis_id == ProteinAnalysis.id)
            .where(JobRecord.id == job_id)
        ).scalar_one_or_none()
    return pdb_path is not None
