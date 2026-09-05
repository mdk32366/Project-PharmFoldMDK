"""D-125-B — read A's sibling ``kabsch/{parent}/`` tree. Not a persist writer.

A already writes ``provenance.json`` / ``seams.jsonl`` under
``{out_root}/kabsch/{parent_job_id}/`` (D-125-A). This module *projects*
that tree for the review card. It does not copy files, does not overwrite
assembler ``stitched.pdb``, and does not invent RMSD or a max Cα jump.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

from core.hold48_kabsch import ALGORITHM, DECISION, kabsch_out_dir

# Persist stems must not collide with the D-120 assembler stem ``stitched``.
ASSEMBLER_PERSIST_STEM = "stitched"
KABSCH_PERSIST_STEM_PREFIX = "kabsch"

ASSEMBLER_PATH_LABEL = (
    "Assembler path (default served PDB) — pLDDT winner-tile, not a "
    "rigid-body transform"
)
KABSCH_PATH_LABEL = (
    "Kabsch-path (sibling tree) — overlap-Cα rigid transform, then the "
    "same winner-tile assembler. Not the default served PDB. Seams are "
    "not scientifically solved"
)
EMPTY_REASON_MISSING = "no_kabsch_artifacts"
SEAM_JUMP_KEYS = (
    "max_ca_jump_angstrom",
    "max_ca_jump",
    "ca_jump_max_angstrom",
)


def default_artifact_root() -> Path:
    return Path(os.environ.get("ARTIFACT_ROOT", "/data/artifacts"))


def assembler_path_block() -> dict[str, Any]:
    return {
        "label": ASSEMBLER_PATH_LABEL,
        "persist_stem": ASSEMBLER_PERSIST_STEM,
        "default_served": True,
    }


def kabsch_persist_stem(parent_id: int) -> str:
    return f"{KABSCH_PERSIST_STEM_PREFIX}/{int(parent_id)}"


def lookup_parent_ids(
    *,
    parent_analysis_id: int,
    parent_job_id: Optional[int] = None,
    meta: Optional[dict[str, Any]] = None,
) -> list[int]:
    """Ids that might key A's sibling tree. Job id first; analysis id fallback."""
    seen: list[int] = []
    meta_id = None
    if meta:
        raw = meta.get("parent_job_id")
        if raw is not None:
            try:
                meta_id = int(raw)
            except (TypeError, ValueError):
                meta_id = None
    for value in (parent_job_id, parent_analysis_id, meta_id):
        if value is None:
            continue
        n = int(value)
        if n not in seen:
            seen.append(n)
    return seen


def candidate_roots(
    artifact_root: Path | str,
    *,
    assembler_pdb_path: Optional[str] = None,
) -> list[Path]:
    """``{ARTIFACT_ROOT}`` and, if needed, the assembler PDB's grandparent."""
    roots: list[Path] = []
    for raw in (artifact_root,):
        p = Path(raw)
        if p not in roots:
            roots.append(p)
    if assembler_pdb_path:
        pdb = Path(assembler_pdb_path)
        # Typical layout: {root}/{job_id}/stitched.pdb → root is grandparent.
        if pdb.parent.name.isdigit():
            grand = pdb.parent.parent
            if grand not in roots:
                roots.append(grand)
    return roots


def find_kabsch_dir(
    artifact_root: Path | str,
    parent_ids: list[int],
    *,
    assembler_pdb_path: Optional[str] = None,
) -> Optional[Path]:
    for root in candidate_roots(artifact_root, assembler_pdb_path=assembler_pdb_path):
        for pid in parent_ids:
            cand = kabsch_out_dir(root, pid)
            if (cand / "provenance.json").is_file() or (cand / "seams.jsonl").is_file():
                return cand
    return None


def _as_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def project_seam(raw: dict[str, Any]) -> dict[str, Any]:
    """Project one A seam row. Missing jump / RMSD stay null — not invented."""
    jump = None
    for key in SEAM_JUMP_KEYS:
        if key in raw and raw[key] is not None:
            jump = _as_float(raw[key])
            break
    return {
        "moving_tile_index": raw.get("moving_tile_index"),
        "reference_tile_index": raw.get("reference_tile_index"),
        "overlap_start": raw.get("overlap_start"),
        "overlap_end": raw.get("overlap_end"),
        "n_ca": raw.get("n_ca"),
        "rmsd_angstrom": _as_float(raw.get("rmsd_angstrom")),
        "max_ca_jump_angstrom": jump,
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
            return [project_seam(r) for r in rows if isinstance(r, dict)]
    raw_seams = provenance.get("seams") or []
    return [project_seam(r) for r in raw_seams if isinstance(r, dict)]


def empty_kabsch_block(*, parent_id: Optional[int] = None) -> dict[str, Any]:
    return {
        "present": False,
        "label": KABSCH_PATH_LABEL,
        "persist_stem": kabsch_persist_stem(parent_id) if parent_id is not None else None,
        "algorithm": ALGORITHM,
        "decision": DECISION,
        "accepted": None,
        "seams": [],
        "empty_reason": EMPTY_REASON_MISSING,
        "empty_note": (
            "Kabsch-path artifacts are not on disk for this parent. "
            "No overlap RMSD and no max Cα jump to show. That absence "
            "is not a solved seam"
        ),
        "files_on_disk": [],
    }


def read_kabsch_dual_path(
    artifact_root: Path | str | None,
    *,
    parent_analysis_id: int,
    parent_job_id: Optional[int] = None,
    assembler_pdb_path: Optional[str] = None,
    meta: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Project A's sibling tree, or an honest empty block."""
    root = Path(artifact_root) if artifact_root is not None else default_artifact_root()
    ids = lookup_parent_ids(
        parent_analysis_id=parent_analysis_id,
        parent_job_id=parent_job_id,
        meta=meta,
    )
    found = find_kabsch_dir(root, ids, assembler_pdb_path=assembler_pdb_path)
    keyed = ids[0] if ids else parent_analysis_id
    if found is None:
        return empty_kabsch_block(parent_id=keyed)

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
    files = sorted(
        p.name
        for p in found.iterdir()
        if p.is_file()
    )
    return {
        "present": True,
        "label": KABSCH_PATH_LABEL,
        "persist_stem": kabsch_persist_stem(parent_from_tree),
        "algorithm": provenance.get("algorithm") or ALGORITHM,
        "decision": provenance.get("decision") or DECISION,
        "accepted": provenance.get("accepted"),
        "seams": seams,
        "empty_reason": None,
        "empty_note": None,
        "files_on_disk": files,
        "dir_name": found.name,
    }


def dual_path_payload(
    artifact_root: Path | str | None,
    *,
    parent_analysis_id: int,
    parent_job_id: Optional[int] = None,
    assembler_pdb_path: Optional[str] = None,
    meta: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    kabsch = read_kabsch_dual_path(
        artifact_root,
        parent_analysis_id=parent_analysis_id,
        parent_job_id=parent_job_id,
        assembler_pdb_path=assembler_pdb_path,
        meta=meta,
    )
    return {
        "assembler": assembler_path_block(),
        "kabsch": kabsch,
    }


def seam_note_for(kabsch: dict[str, Any]) -> str:
    """IGF2R caveat stays. PARKED is retired — B shipped; missing is an absence."""
    base = (
        "IGF2R ≈ 88.76 Å is a measured caveat, not a solved structure. "
        "Seams are not scientifically solved"
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
