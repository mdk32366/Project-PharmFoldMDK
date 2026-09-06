"""D-128-B — read A's sibling ``linker_seam/{parent}/`` tree. Not a persist writer.

A already writes ``provenance.json`` / ``seams.jsonl`` / ``seam_honesty.jsonl``
under ``{out_root}/linker_seam/{parent_job_id}/`` (D-128-A). This module
*projects* that tree for the review card. It does not copy files, does
not overwrite the assembler ``stitched.pdb`` / D-125 ``kabsch/{id}/`` /
D-126 ``confidence_kabsch/{id}/`` / D-127 ``piecewise_kabsch/{id}/``
trees, and does not invent a jump, a window, an RMSD, or an honesty
verdict.

⚠ **One row per (path, seam) is the unit of disclosure** (log D-128-B
decision 4). A's ``seam_honesty.jsonl`` is *cross-path*: four trees, each
seam, the max Cα jump that path **ends** with. A mean jump per path, an
"N of M seams honest" tally, or a best-path badge would hide which path
is dishonest **where** — which is the entire content of Spec §1a, and the
D-126 lie surface re-created one level up, inside the fix for it. This
module therefore derives no mean, no min, no max, no tally, and no score.

⚠ **Unknown is not honest; null is not ``0.0``.** ``honest`` is
three-valued and is recomputed here by applying A's own
``honest_for_jump`` gate to A's own recorded jump — a verdict is never
copied out of a file unchecked, and a recorded ``true`` above the gate is
overridden fail-closed. This module carries no threshold constant of its
own.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from app.kabsch_path_read import (
    ASSEMBLER_PERSIST_STEM,
    candidate_roots,
    default_artifact_root,
    lookup_parent_ids,
    _as_float,
)
from app.piecewise_kabsch_path_read import (
    four_path_payload,
    read_piecewise_kabsch_path,
)
from core.hold48_linker_seam import (
    ALGORITHM,
    DECISION,
    HONESTY_PATHS,
    PATHS_DEFINING_LINKERS,
    RMSD_REFUSE_ANGSTROM,
    SEAM_HONESTY_GATE_ANGSTROM,
    WINDOW_HALF_WIDTH_AA,
    honest_for_jump,
    linker_seam_out_dir,
)

# Persist stems must not collide with assembler ``stitched``, D-125
# ``kabsch/``, D-126 ``confidence_kabsch/``, or D-127 ``piecewise_kabsch/``.
LINKER_SEAM_PERSIST_STEM_PREFIX = "linker_seam"

LINKER_SEAM_PATH_LABEL = (
    "Linker / seam honesty path (sibling tree) — per-path seam honesty "
    "rows, then at most one weighted rigid transform inside a ±32 aa "
    "window around the offending seam, then the same winner-tile "
    "assembler. Not the default served PDB. Seams are not scientifically "
    "solved"
)
EMPTY_REASON_MISSING = "no_linker_seam_artifacts"
# A tree A wrote without rows is an absence with a reason — never
# "0 seams measured" and never "0 dishonest seams".
EMPTY_REASON_NO_SEAM_ROWS = "no_seam_rows_recorded"
EMPTY_REASON_NO_HONESTY_ROWS = "no_seam_honesty_rows_recorded"


def linker_seam_persist_stem(parent_id: int) -> str:
    return f"{LINKER_SEAM_PERSIST_STEM_PREFIX}/{int(parent_id)}"


def find_linker_seam_dir(
    artifact_root: Path | str,
    parent_ids: list[int],
    *,
    assembler_pdb_path: Optional[str] = None,
) -> Optional[Path]:
    for root in candidate_roots(artifact_root, assembler_pdb_path=assembler_pdb_path):
        for pid in parent_ids:
            cand = linker_seam_out_dir(root, pid)
            for name in ("provenance.json", "seams.jsonl", "seam_honesty.jsonl"):
                if (cand / name).is_file():
                    return cand
    return None


def _as_int(raw: Any) -> Optional[int]:
    if raw is None or isinstance(raw, bool):
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _as_bool(raw: Any) -> Optional[bool]:
    return raw if isinstance(raw, bool) else None


def project_honesty_row(raw: dict[str, Any]) -> dict[str, Any]:
    """Project one §1a row: which path, which seam, what jump, honest or not.

    The verdict is **recomputed** from the recorded jump with A's own gate
    rather than copied: a hand-edited ``honest`` cannot make a seam above
    **10.0 Å** read as honest, and a null jump stays *unknown* rather than
    becoming a pass. ``honest_recorded`` keeps what the file said so the
    disagreement is visible rather than silently resolved.

    Linker fields belong to the one path that defines linkers (D-127). On
    the others they are **not applicable** — absent, not ``0``.
    """
    path = raw.get("path")
    jump = _as_float(raw.get("max_ca_jump_angstrom"))
    honest = honest_for_jump(jump)
    recorded = _as_bool(raw.get("honest"))
    applicable = path in PATHS_DEFINING_LINKERS
    return {
        "path": path,
        "moving_tile_index": _as_int(raw.get("moving_tile_index")),
        "reference_tile_index": _as_int(raw.get("reference_tile_index")),
        "max_ca_jump_angstrom": jump,
        "honest": honest,
        "honest_recorded": recorded,
        "honest_disagrees_with_record": recorded is not None and recorded is not honest,
        "linker_fields_applicable": applicable,
        "linker_n": _as_int(raw.get("linker_n")) if applicable else None,
        "max_linker_ca_jump": (
            _as_float(raw.get("max_linker_ca_jump")) if applicable else None
        ),
        "source": raw.get("source"),
        "absence_reason": raw.get("absence_reason"),
        "refuse_reason": raw.get("refuse_reason"),
        "honesty_gate_angstrom": SEAM_HONESTY_GATE_ANGSTROM,
    }


def project_linker_seam_row(raw: dict[str, Any]) -> dict[str, Any]:
    """Project one D-128 seam row: what was identified, fitted, and ended at.

    ``R`` / ``t`` are deliberately dropped: the card names measurements,
    not a transform a reader could mistake for a served pose. Every
    measure stays **null** when A refused before computing it — a
    refuse-before-transform has nothing to measure, and empty is not zero.
    """
    post_jump = _as_float(raw.get("max_ca_jump_angstrom"))
    source = raw.get("offending_seam_source")
    return {
        "moving_tile_index": _as_int(raw.get("moving_tile_index")),
        "reference_tile_index": _as_int(raw.get("reference_tile_index")),
        "overlap_start": _as_int(raw.get("overlap_start")),
        "overlap_end": _as_int(raw.get("overlap_end")),
        "offending_seam_source": source,
        "no_offending_seam": source is None,
        "seam_centre": _as_int(raw.get("seam_centre")),
        "window_start": _as_int(raw.get("window_start")),
        "window_end": _as_int(raw.get("window_end")),
        "window_half_width_aa": _as_int(raw.get("window_half_width_aa")),
        "n_ca": _as_int(raw.get("n_ca")),
        "rmsd_angstrom": _as_float(raw.get("rmsd_angstrom")),
        "max_ca_jump_angstrom": post_jump,
        "pre_transform_max_ca_jump_angstrom": _as_float(
            raw.get("pre_transform_max_ca_jump_angstrom")
        ),
        "honest": honest_for_jump(post_jump),
        "refuse_reason": raw.get("refuse_reason"),
        "accepted": raw.get("refuse_reason") is None,
    }


def _load_rows(directory: Path, name: str) -> list[dict[str, Any]]:
    jsonl = directory / name
    rows: list[dict[str, Any]] = []
    if not jsonl.is_file():
        return rows
    for line in jsonl.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            loaded = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(loaded, dict):
            rows.append(loaded)
    return rows


def _load_seams(directory: Path, provenance: dict[str, Any]) -> list[dict[str, Any]]:
    rows = _load_rows(directory, "seams.jsonl")
    if rows:
        return [project_linker_seam_row(r) for r in rows]
    raw_seams = provenance.get("seams") or []
    return [project_linker_seam_row(r) for r in raw_seams if isinstance(r, dict)]


def _load_honesty(directory: Path, provenance: dict[str, Any]) -> list[dict[str, Any]]:
    rows = _load_rows(directory, "seam_honesty.jsonl")
    if rows:
        return [project_honesty_row(r) for r in rows]
    raw_rows = provenance.get("seam_honesty") or []
    return [project_honesty_row(r) for r in raw_rows if isinstance(r, dict)]


def empty_linker_seam_block(*, parent_id: Optional[int] = None) -> dict[str, Any]:
    return {
        "present": False,
        "label": LINKER_SEAM_PATH_LABEL,
        "persist_stem": (
            linker_seam_persist_stem(parent_id) if parent_id is not None else None
        ),
        "algorithm": ALGORITHM,
        "decision": DECISION,
        "accepted": None,
        "repaired": None,
        "seams": [],
        "seams_empty_reason": EMPTY_REASON_NO_SEAM_ROWS,
        "seam_honesty": [],
        "seam_honesty_empty_reason": EMPTY_REASON_NO_HONESTY_ROWS,
        "honesty_paths": list(HONESTY_PATHS),
        "empty_reason": EMPTY_REASON_MISSING,
        "empty_note": (
            "Linker / seam honesty artifacts are not on disk for this parent. "
            "No per-path seam honesty row, no window fit, no Cα count, no "
            "weighted RMSD, and no max Cα jump to show. That absence is not "
            "a solved seam, and it is not a seam measured as honest"
        ),
        "files_on_disk": [],
        "success_pdb_on_disk": False,
        "has_dishonest_or_unknown_seam": None,
        "rmsd_refuse_angstrom": RMSD_REFUSE_ANGSTROM,
        "honesty_gate_angstrom": SEAM_HONESTY_GATE_ANGSTROM,
        "window_half_width_aa": WINDOW_HALF_WIDTH_AA,
        "default_served": False,
        "seams_solved": False,
    }


def read_linker_seam_path(
    artifact_root: Path | str | None,
    *,
    parent_analysis_id: int,
    parent_job_id: Optional[int] = None,
    assembler_pdb_path: Optional[str] = None,
    meta: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Project A's D-128 sibling tree, or an honest empty block."""
    root = Path(artifact_root) if artifact_root is not None else default_artifact_root()
    ids = lookup_parent_ids(
        parent_analysis_id=parent_analysis_id,
        parent_job_id=parent_job_id,
        meta=meta,
    )
    found = find_linker_seam_dir(root, ids, assembler_pdb_path=assembler_pdb_path)
    keyed = ids[0] if ids else parent_analysis_id
    if found is None:
        return empty_linker_seam_block(parent_id=keyed)

    provenance: dict[str, Any] = {}
    prov_path = found / "provenance.json"
    if prov_path.is_file():
        try:
            loaded = json.loads(prov_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                provenance = loaded
        except json.JSONDecodeError:
            provenance = {}

    parent_from_tree = _as_int(provenance.get("parent_job_id"))
    if parent_from_tree is None:
        parent_from_tree = keyed

    seams = _load_seams(found, provenance)
    honesty = _load_honesty(found, provenance)
    files = sorted(p.name for p in found.iterdir() if p.is_file())
    accepted = _as_bool(provenance.get("accepted"))
    # Existence, not a tally: one dishonest or unknown D-128 seam is enough
    # to withhold the success PDB (Spec §1a fail-closed). Counting how many
    # would invite the score this surface must not carry.
    dishonest = any(s["honest"] is not True for s in seams) if seams else None
    # All-or-nothing (Spec §2 / §1a): a leftover stitched.pdb is not a D-128
    # success when A recorded a refused parent, and a dishonest or unknown
    # seam may never carry one.
    success_pdb = bool(accepted) and ("stitched.pdb" in files) and dishonest is False
    return {
        "present": True,
        "label": LINKER_SEAM_PATH_LABEL,
        "persist_stem": linker_seam_persist_stem(parent_from_tree),
        "algorithm": provenance.get("algorithm") or ALGORITHM,
        "decision": provenance.get("decision") or DECISION,
        "accepted": accepted,
        "repaired": _as_bool(provenance.get("repaired")),
        "seams": seams,
        "seams_empty_reason": None if seams else EMPTY_REASON_NO_SEAM_ROWS,
        "seam_honesty": honesty,
        "seam_honesty_empty_reason": None if honesty else EMPTY_REASON_NO_HONESTY_ROWS,
        "honesty_paths": list(HONESTY_PATHS),
        "empty_reason": None,
        "empty_note": None,
        "files_on_disk": files,
        "dir_name": found.name,
        "success_pdb_on_disk": success_pdb,
        "has_dishonest_or_unknown_seam": dishonest,
        "rmsd_refuse_angstrom": _as_float(provenance.get("rmsd_refuse_angstrom"))
        or RMSD_REFUSE_ANGSTROM,
        "honesty_gate_angstrom": _as_float(provenance.get("seam_honesty_gate_angstrom"))
        or SEAM_HONESTY_GATE_ANGSTROM,
        "window_half_width_aa": _as_int(provenance.get("window_half_width_aa"))
        or WINDOW_HALF_WIDTH_AA,
        "default_served": False,
        "seams_solved": False,
    }


def five_path_payload(
    artifact_root: Path | str | None,
    *,
    parent_analysis_id: int,
    parent_job_id: Optional[int] = None,
    assembler_pdb_path: Optional[str] = None,
    meta: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Assembler + D-125 + D-126 + D-127 + D-128. Default served stays assembler."""
    four = four_path_payload(
        artifact_root,
        parent_analysis_id=parent_analysis_id,
        parent_job_id=parent_job_id,
        assembler_pdb_path=assembler_pdb_path,
        meta=meta,
    )
    linker_seam = read_linker_seam_path(
        artifact_root,
        parent_analysis_id=parent_analysis_id,
        parent_job_id=parent_job_id,
        assembler_pdb_path=assembler_pdb_path,
        meta=meta,
    )
    return {
        "assembler": four["assembler"],
        "kabsch": four["kabsch"],
        "confidence_kabsch": four["confidence_kabsch"],
        "piecewise_kabsch": four["piecewise_kabsch"],
        "linker_seam": linker_seam,
    }


def seam_note_for_five(
    kabsch: dict[str, Any],
    confidence_kabsch: Optional[dict[str, Any]] = None,
    piecewise_kabsch: Optional[dict[str, Any]] = None,
    linker_seam: Optional[dict[str, Any]] = None,
) -> str:
    """IGF2R caveat stays. A missing D-128 tree must not imply a fifth path."""
    base = (
        "IGF2R ≈ 88.76 Å is a measured caveat, not a solved structure. "
        "Seams are not scientifically solved"
    )
    d128 = linker_seam or {}
    if d128.get("present"):
        return (
            f"{base}. A linker / seam honesty sibling tree is named below as "
            "a fifth path: it reports, per path and per seam, the max Cα jump "
            "that path ends with and whether it is therefore honest at that "
            "seam. Those are measurements, not a verdict that the chain is "
            "lined up. The assembler PDB remains the default served structure"
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
    "EMPTY_REASON_NO_HONESTY_ROWS",
    "EMPTY_REASON_NO_SEAM_ROWS",
    "LINKER_SEAM_PATH_LABEL",
    "LINKER_SEAM_PERSIST_STEM_PREFIX",
    "empty_linker_seam_block",
    "find_linker_seam_dir",
    "five_path_payload",
    "four_path_payload",
    "linker_seam_persist_stem",
    "project_honesty_row",
    "project_linker_seam_row",
    "read_linker_seam_path",
    "read_piecewise_kabsch_path",
    "seam_note_for_five",
)
