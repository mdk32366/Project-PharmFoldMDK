"""D-127-B — read A's sibling ``piecewise_kabsch/{parent}/`` tree. Not a persist writer.

A already writes ``provenance.json`` / ``seams.jsonl`` under
``{out_root}/piecewise_kabsch/{parent_job_id}/`` (D-127-A). This module
*projects* that tree for the review card. It does not copy files, does
not overwrite assembler ``stitched.pdb`` / D-125 ``kabsch/{id}/`` /
D-126 ``confidence_kabsch/{id}/``, and does not invent RMSD, piece
counts, or linker counts.

⚠ **Per-piece rows are the unit of disclosure** (log D-127-B decision 4).
A D-127 seam holds *k* pieces, each with its own domain interval, Cα
count, weighted RMSD, and refuse reason. This module never reduces those
to one seam number — no mean, no best piece, no pass count. D-126's
lesson was that one flattering number can hide a 28–68 Å jump; deriving
a seam average here would re-create that lie inside the fix for it.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from app.confidence_kabsch_path_read import (
    read_confidence_kabsch_path,
    triple_path_payload,
)
from app.kabsch_path_read import (
    ASSEMBLER_PERSIST_STEM,
    candidate_roots,
    default_artifact_root,
    lookup_parent_ids,
    _as_float,
)
from core.hold48_piecewise_kabsch import (
    ALGORITHM,
    DECISION,
    RMSD_REFUSE_ANGSTROM,
    piecewise_kabsch_out_dir,
)

# Persist stems must not collide with assembler ``stitched``, D-125
# ``kabsch/``, or D-126 ``confidence_kabsch/``.
PIECEWISE_KABSCH_PERSIST_STEM_PREFIX = "piecewise_kabsch"

PIECEWISE_KABSCH_PATH_LABEL = (
    "Piecewise / domain-aware Kabsch-path (sibling tree) — one weighted "
    "rigid transform per UniProt domain on the overlap Cα, then the same "
    "winner-tile assembler. Not the default served PDB. Seams are not "
    "scientifically solved"
)
EMPTY_REASON_MISSING = "no_piecewise_kabsch_artifacts"
# A seam A recorded without a ``pieces`` list is an absence with a reason,
# never "0 pieces refused".
EMPTY_REASON_NO_PIECE_ROWS = "no_piece_rows_recorded"


def piecewise_kabsch_persist_stem(parent_id: int) -> str:
    return f"{PIECEWISE_KABSCH_PERSIST_STEM_PREFIX}/{int(parent_id)}"


def find_piecewise_kabsch_dir(
    artifact_root: Path | str,
    parent_ids: list[int],
    *,
    assembler_pdb_path: Optional[str] = None,
) -> Optional[Path]:
    for root in candidate_roots(artifact_root, assembler_pdb_path=assembler_pdb_path):
        for pid in parent_ids:
            cand = piecewise_kabsch_out_dir(root, pid)
            if (cand / "provenance.json").is_file() or (cand / "seams.jsonl").is_file():
                return cand
    return None


def _interval(raw: Any) -> Optional[list[int]]:
    """A's ``PieceFit.to_json`` writes ``interval`` as ``[start, end]``."""
    if not isinstance(raw, (list, tuple)) or len(raw) != 2:
        return None
    try:
        return [int(raw[0]), int(raw[1])]
    except (TypeError, ValueError):
        return None


def project_piece(raw: dict[str, Any]) -> dict[str, Any]:
    """Project one A piece row. A missing weighted RMSD stays null.

    ``R`` / ``t`` are deliberately dropped: the card names measurements,
    not a transform a reader could mistake for a served pose.
    """
    return {
        "interval": _interval(raw.get("interval")),
        "n_ca": raw.get("n_ca"),
        "rmsd_angstrom": _as_float(raw.get("rmsd_angstrom")),
        "refuse_reason": raw.get("refuse_reason"),
        "accepted": raw.get("refuse_reason") is None,
    }


def project_piecewise_seam(raw: dict[str, Any]) -> dict[str, Any]:
    """Project one A seam row, pieces included.

    Full-overlap RMSD, max Cα jump, and max linker jump stay **null** on
    refuse-before-transform (Spec §1 / §5) — never 0.0.
    """
    raw_pieces = raw.get("pieces")
    pieces = (
        [project_piece(p) for p in raw_pieces if isinstance(p, dict)]
        if isinstance(raw_pieces, list)
        else []
    )
    return {
        "moving_tile_index": raw.get("moving_tile_index"),
        "reference_tile_index": raw.get("reference_tile_index"),
        "overlap_start": raw.get("overlap_start"),
        "overlap_end": raw.get("overlap_end"),
        "pieces": pieces,
        "pieces_empty_reason": None if pieces else EMPTY_REASON_NO_PIECE_ROWS,
        "linker_n": raw.get("linker_n"),
        "max_linker_ca_jump": _as_float(raw.get("max_linker_ca_jump")),
        "rmsd_full_overlap_angstrom": _as_float(raw.get("rmsd_full_overlap_angstrom")),
        "max_ca_jump_angstrom": _as_float(raw.get("max_ca_jump_angstrom")),
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
            return [project_piecewise_seam(r) for r in rows if isinstance(r, dict)]
    raw_seams = provenance.get("seams") or []
    return [project_piecewise_seam(r) for r in raw_seams if isinstance(r, dict)]


def empty_piecewise_kabsch_block(*, parent_id: Optional[int] = None) -> dict[str, Any]:
    return {
        "present": False,
        "label": PIECEWISE_KABSCH_PATH_LABEL,
        "persist_stem": (
            piecewise_kabsch_persist_stem(parent_id) if parent_id is not None else None
        ),
        "algorithm": ALGORITHM,
        "decision": DECISION,
        "accepted": None,
        "seams": [],
        "empty_reason": EMPTY_REASON_MISSING,
        "empty_note": (
            "Piecewise / domain-aware Kabsch-path artifacts are not on disk "
            "for this parent. No per-piece Cα count or weighted RMSD, no "
            "full-overlap RMSD, no max Cα jump, and no linker count to "
            "show. That absence is not a solved seam"
        ),
        "files_on_disk": [],
        "success_pdb_on_disk": False,
        "rmsd_refuse_angstrom": RMSD_REFUSE_ANGSTROM,
    }


def read_piecewise_kabsch_path(
    artifact_root: Path | str | None,
    *,
    parent_analysis_id: int,
    parent_job_id: Optional[int] = None,
    assembler_pdb_path: Optional[str] = None,
    meta: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Project A's D-127 sibling tree, or an honest empty block."""
    root = Path(artifact_root) if artifact_root is not None else default_artifact_root()
    ids = lookup_parent_ids(
        parent_analysis_id=parent_analysis_id,
        parent_job_id=parent_job_id,
        meta=meta,
    )
    found = find_piecewise_kabsch_dir(root, ids, assembler_pdb_path=assembler_pdb_path)
    keyed = ids[0] if ids else parent_analysis_id
    if found is None:
        return empty_piecewise_kabsch_block(parent_id=keyed)

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
    # All-or-nothing (Spec §2): a leftover stitched.pdb is not a D-127
    # success when A recorded a refused parent.
    success_pdb = bool(accepted) and ("stitched.pdb" in files)
    return {
        "present": True,
        "label": PIECEWISE_KABSCH_PATH_LABEL,
        "persist_stem": piecewise_kabsch_persist_stem(parent_from_tree),
        "algorithm": provenance.get("algorithm") or ALGORITHM,
        "decision": provenance.get("decision") or DECISION,
        "accepted": accepted,
        "seams": seams,
        "empty_reason": None,
        "empty_note": None,
        "files_on_disk": files,
        "dir_name": found.name,
        "success_pdb_on_disk": success_pdb,
        "rmsd_refuse_angstrom": _as_float(provenance.get("rmsd_refuse_angstrom"))
        or RMSD_REFUSE_ANGSTROM,
    }


def four_path_payload(
    artifact_root: Path | str | None,
    *,
    parent_analysis_id: int,
    parent_job_id: Optional[int] = None,
    assembler_pdb_path: Optional[str] = None,
    meta: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Assembler + D-125 + D-126 + D-127. Default served stays assembler."""
    triple = triple_path_payload(
        artifact_root,
        parent_analysis_id=parent_analysis_id,
        parent_job_id=parent_job_id,
        assembler_pdb_path=assembler_pdb_path,
        meta=meta,
    )
    piecewise = read_piecewise_kabsch_path(
        artifact_root,
        parent_analysis_id=parent_analysis_id,
        parent_job_id=parent_job_id,
        assembler_pdb_path=assembler_pdb_path,
        meta=meta,
    )
    return {
        "assembler": triple["assembler"],
        "kabsch": triple["kabsch"],
        "confidence_kabsch": triple["confidence_kabsch"],
        "piecewise_kabsch": piecewise,
    }


def seam_note_for_four(
    kabsch: dict[str, Any],
    confidence_kabsch: Optional[dict[str, Any]] = None,
    piecewise_kabsch: Optional[dict[str, Any]] = None,
) -> str:
    """IGF2R caveat stays. A missing D-127 tree must not imply a fourth path."""
    base = (
        "IGF2R ≈ 88.76 Å is a measured caveat, not a solved structure. "
        "Seams are not scientifically solved"
    )
    d127 = piecewise_kabsch or {}
    if d127.get("present"):
        return (
            f"{base}. A piecewise / domain-aware Kabsch sibling tree is "
            "named below as a fourth path, one rigid move per UniProt "
            "domain. The assembler PDB remains the default served structure"
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
    "EMPTY_REASON_MISSING",
    "EMPTY_REASON_NO_PIECE_ROWS",
    "PIECEWISE_KABSCH_PATH_LABEL",
    "PIECEWISE_KABSCH_PERSIST_STEM_PREFIX",
    "empty_piecewise_kabsch_block",
    "find_piecewise_kabsch_dir",
    "four_path_payload",
    "piecewise_kabsch_persist_stem",
    "project_piece",
    "project_piecewise_seam",
    "read_confidence_kabsch_path",
    "read_piecewise_kabsch_path",
    "seam_note_for_four",
)
