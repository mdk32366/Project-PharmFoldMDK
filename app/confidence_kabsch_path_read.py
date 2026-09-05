"""D-126-B — read A's sibling ``confidence_kabsch/{parent}/`` tree. Not a persist writer.

A already writes ``provenance.json`` / ``seams.jsonl`` under
``{out_root}/confidence_kabsch/{parent_job_id}/`` (D-126-A). This module
*projects* that tree for the review card. It does not copy files, does
not overwrite assembler ``stitched.pdb`` or D-125 ``kabsch/{id}/``, and
does not invent RMSD, n_ca_eff, or trim counts.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from app.kabsch_path_read import (
    ASSEMBLER_PERSIST_STEM,
    assembler_path_block,
    candidate_roots,
    default_artifact_root,
    dual_path_payload,
    lookup_parent_ids,
    _as_float,
)
from core.hold48_confidence_kabsch import (
    ALGORITHM,
    DECISION,
    confidence_kabsch_out_dir,
)

# Persist stems must not collide with assembler ``stitched`` or D-125 ``kabsch/``.
CONFIDENCE_KABSCH_PERSIST_STEM_PREFIX = "confidence_kabsch"

CONFIDENCE_KABSCH_PATH_LABEL = (
    "Overlap-confidence Kabsch-path (sibling tree) — weighted + trimmed "
    "overlap-Cα rigid transform, then the same winner-tile assembler. "
    "Not the default served PDB. Seams are not scientifically solved"
)
EMPTY_REASON_MISSING = "no_confidence_kabsch_artifacts"


def confidence_kabsch_persist_stem(parent_id: int) -> str:
    return f"{CONFIDENCE_KABSCH_PERSIST_STEM_PREFIX}/{int(parent_id)}"


def find_confidence_kabsch_dir(
    artifact_root: Path | str,
    parent_ids: list[int],
    *,
    assembler_pdb_path: Optional[str] = None,
) -> Optional[Path]:
    for root in candidate_roots(artifact_root, assembler_pdb_path=assembler_pdb_path):
        for pid in parent_ids:
            cand = confidence_kabsch_out_dir(root, pid)
            if (cand / "provenance.json").is_file() or (cand / "seams.jsonl").is_file():
                return cand
    return None


def project_confidence_seam(raw: dict[str, Any]) -> dict[str, Any]:
    """Project one A seam row. Missing weighted / full-overlap / jump / trim stay null."""
    return {
        "moving_tile_index": raw.get("moving_tile_index"),
        "reference_tile_index": raw.get("reference_tile_index"),
        "overlap_start": raw.get("overlap_start"),
        "overlap_end": raw.get("overlap_end"),
        "n_ca": raw.get("n_ca"),
        "n_ca_eff": raw.get("n_ca_eff"),
        "rmsd_angstrom": _as_float(raw.get("rmsd_angstrom")),
        "rmsd_full_overlap_angstrom": _as_float(raw.get("rmsd_full_overlap_angstrom")),
        "max_ca_jump_angstrom": _as_float(raw.get("max_ca_jump_angstrom")),
        "trim_rounds": raw.get("trim_rounds"),
        "refuse_reason": raw.get("refuse_reason"),
    }


def _load_seams(directory: Path, provenance: dict[str, Any]) -> list[dict[str, Any]]:
    jsonl = directory / "seams.jsonl"
    rows: list[dict[str, Any]] = []
    if jsonl.is_file():
        for line in jsonl.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        if rows:
            return [project_confidence_seam(r) for r in rows if isinstance(r, dict)]
    raw_seams = provenance.get("seams") or []
    return [project_confidence_seam(r) for r in raw_seams if isinstance(r, dict)]


def empty_confidence_kabsch_block(*, parent_id: Optional[int] = None) -> dict[str, Any]:
    return {
        "present": False,
        "label": CONFIDENCE_KABSCH_PATH_LABEL,
        "persist_stem": (
            confidence_kabsch_persist_stem(parent_id) if parent_id is not None else None
        ),
        "algorithm": ALGORITHM,
        "decision": DECISION,
        "accepted": None,
        "seams": [],
        "empty_reason": EMPTY_REASON_MISSING,
        "empty_note": (
            "Overlap-confidence Kabsch-path artifacts are not on disk for "
            "this parent. No weighted RMSD, full-overlap RMSD, n_ca_eff, "
            "or trim count to show. That absence is not a solved seam"
        ),
        "files_on_disk": [],
        "success_pdb_on_disk": False,
    }


def read_confidence_kabsch_path(
    artifact_root: Path | str | None,
    *,
    parent_analysis_id: int,
    parent_job_id: Optional[int] = None,
    assembler_pdb_path: Optional[str] = None,
    meta: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Project A's D-126 sibling tree, or an honest empty block."""
    root = Path(artifact_root) if artifact_root is not None else default_artifact_root()
    ids = lookup_parent_ids(
        parent_analysis_id=parent_analysis_id,
        parent_job_id=parent_job_id,
        meta=meta,
    )
    found = find_confidence_kabsch_dir(root, ids, assembler_pdb_path=assembler_pdb_path)
    keyed = ids[0] if ids else parent_analysis_id
    if found is None:
        return empty_confidence_kabsch_block(parent_id=keyed)

    provenance: dict[str, Any] = {}
    prov_path = found / "provenance.json"
    if prov_path.is_file():
        try:
            loaded = json.loads(prov_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                provenance = loaded
        except json.JSONDecodeError:
            provenance = {}

    parent_from_tree = provenance.get("parent_job_id", keyed)
    try:
        parent_from_tree = int(parent_from_tree)
    except (TypeError, ValueError):
        parent_from_tree = keyed

    seams = _load_seams(found, provenance)
    files = sorted(p.name for p in found.iterdir() if p.is_file())
    accepted = provenance.get("accepted")
    # Fail-closed: a leftover stitched.pdb is not a D-126 success if A refused.
    success_pdb = bool(accepted) and ("stitched.pdb" in files)
    return {
        "present": True,
        "label": CONFIDENCE_KABSCH_PATH_LABEL,
        "persist_stem": confidence_kabsch_persist_stem(parent_from_tree),
        "algorithm": provenance.get("algorithm") or ALGORITHM,
        "decision": provenance.get("decision") or DECISION,
        "accepted": accepted,
        "seams": seams,
        "empty_reason": None,
        "empty_note": None,
        "files_on_disk": files,
        "dir_name": found.name,
        "success_pdb_on_disk": success_pdb,
    }


def triple_path_payload(
    artifact_root: Path | str | None,
    *,
    parent_analysis_id: int,
    parent_job_id: Optional[int] = None,
    assembler_pdb_path: Optional[str] = None,
    meta: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Assembler + D-125 kabsch + D-126 confidence_kabsch. Default served stays assembler."""
    dual = dual_path_payload(
        artifact_root,
        parent_analysis_id=parent_analysis_id,
        parent_job_id=parent_job_id,
        assembler_pdb_path=assembler_pdb_path,
        meta=meta,
    )
    confidence = read_confidence_kabsch_path(
        artifact_root,
        parent_analysis_id=parent_analysis_id,
        parent_job_id=parent_job_id,
        assembler_pdb_path=assembler_pdb_path,
        meta=meta,
    )
    return {
        "assembler": dual["assembler"],
        "kabsch": dual["kabsch"],
        "confidence_kabsch": confidence,
    }


def seam_note_for_triple(
    kabsch: dict[str, Any],
    confidence_kabsch: Optional[dict[str, Any]] = None,
) -> str:
    """IGF2R caveat stays. Missing D-126 tree must not imply a third path exists."""
    base = (
        "IGF2R ≈ 88.76 Å is a measured caveat, not a solved structure. "
        "Seams are not scientifically solved"
    )
    d126 = confidence_kabsch or {}
    if d126.get("present"):
        return (
            f"{base}. An overlap-confidence Kabsch sibling tree is named "
            "below as a third path. The assembler PDB remains the default "
            "served structure"
        )
    if kabsch.get("present"):
        return (
            f"{base}. A Kabsch-path sibling tree is named below as a second "
            "path. The assembler PDB remains the default served structure"
        )
    return (
        f"{base}. Kabsch-path artifacts are not on disk for this parent. "
        "No overlap RMSD is shown. That absence is not a solved seam"
    )


# Re-export so callers can keep one import surface.
__all__ = (
    "ASSEMBLER_PERSIST_STEM",
    "CONFIDENCE_KABSCH_PATH_LABEL",
    "CONFIDENCE_KABSCH_PERSIST_STEM_PREFIX",
    "assembler_path_block",
    "confidence_kabsch_persist_stem",
    "empty_confidence_kabsch_block",
    "find_confidence_kabsch_dir",
    "project_confidence_seam",
    "read_confidence_kabsch_path",
    "seam_note_for_triple",
    "triple_path_payload",
)
