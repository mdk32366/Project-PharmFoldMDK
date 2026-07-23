"""D-034 — the read API's database + projection work, kept out of the route handlers
so it is unit-testable without HTTP (mirrors the ``routes.py`` / ``artifacts.py`` split).

The load-bearing decisions live here:

- **Two payload shapes (D-034 decision 1).** ``list_projection`` returns the light row a
  ranking table renders — twelve fields, and **never** ``sequence`` or ``fold_provenance``,
  which run to hundreds of residues and a full provenance block per row. ``detail_projection``
  returns the whole record, those heavy fields included. The split is measured, not stylistic
  (D-034: ~tens of KB of sequence across 42 rows a list never shows).

- **Where the fields live.** There is no ``accession``/``gene``/``folded_at`` column. ``accession``
  is ``input_value``; ``gene``/``label``/``tier``/``tier_reason``/``disposition``/``held_out``/
  ``boundary_method``/``fold_length``/``full_length``/``sequence``/``fold_provenance`` are all in
  ``meta`` (``core.enqueue`` writes them, the fold adds ``fold_provenance``). ``mean_plddt`` is a
  column. ``tier_reason`` is a key on every row but ``None`` on non-rental rows — projected as-is.

- **Ordering by ``id`` (D-034 / Orders §1).** ``created_at`` does **not** order the folds — 41 of
  42 rows share one batch timestamp — so the list is ordered by ``id``.

- **Serve the stored ``pdb_path`` (D-034 decision 2 / §2a).** ``pdb_path`` is looked up by integer
  id and returned verbatim; no path is ever reconstructed from ``{root}/{id}`` or built from a
  client value. On an unauthenticated surface that is also the path-traversal defence. The
  per-residue pLDDT lives beside it (``plddt.json`` in the stored path's directory), so it is
  derived from the stored absolute path, never from client input.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import ProteinAnalysis

# Meta keys carried into the light list, in payload order (D-034 decision 1 / Orders §1).
_LIST_META_KEYS = (
    "label", "gene", "disposition", "held_out", "tier", "tier_reason",
    "boundary_method", "fold_length", "full_length",
)
# Extra meta keys the detail record adds on top of the light fields (still excluding the
# two heavy ones, which are appended explicitly last so the split is obvious).
_DETAIL_EXTRA_META_KEYS = (
    "source", "uniprot_release", "ecd_start", "ecd_end", "primary_match",
)


def list_projection(row: ProteinAnalysis) -> dict[str, Any]:
    """The light list row (D-034 decision 1): twelve fields, no ``sequence``/``fold_provenance``.
    ``accession`` comes from ``input_value``, ``mean_plddt`` from the column, the rest from meta."""
    meta = row.meta or {}
    out: dict[str, Any] = {
        "id": row.id,
        "accession": row.input_value,
        "label": meta.get("label"),
        "gene": meta.get("gene"),
        "mean_plddt": row.mean_plddt,
    }
    for key in _LIST_META_KEYS:
        if key not in out:                       # label/gene already placed above
            out[key] = meta.get(key)
    return out


def detail_projection(row: ProteinAnalysis) -> dict[str, Any]:
    """The full record (D-034 decision 1): the light fields, the remaining meta, and the two
    heavy fields — ``sequence`` and the complete ``fold_provenance`` — which the list omits."""
    meta = row.meta or {}
    out = list_projection(row)
    out["structure_source"] = row.structure_source
    out["notes"] = row.notes
    for key in _DETAIL_EXTRA_META_KEYS:
        out[key] = meta.get(key)
    out["sequence"] = meta.get("sequence")
    out["fold_provenance"] = meta.get("fold_provenance")
    return out


def list_analyses(engine: Any) -> list[dict[str, Any]]:
    """Every analysis as a light row, ordered by ``id`` ascending (D-034 / Orders §1)."""
    with Session(engine) as s:
        rows = s.scalars(
            select(ProteinAnalysis).order_by(ProteinAnalysis.id)
        ).all()
        return [list_projection(r) for r in rows]


def get_analysis(engine: Any, analysis_id: int) -> Optional[dict[str, Any]]:
    """The full record for one id, or ``None`` if it does not exist (route → 404)."""
    with Session(engine) as s:
        row = s.get(ProteinAnalysis, analysis_id)
        return detail_projection(row) if row is not None else None


def get_structure_path(engine: Any, analysis_id: int) -> Optional[str]:
    """The row's **stored** ``pdb_path``, or ``None`` if the id is unknown or the fold has no
    structure yet (both → 404, never a 500). Never reconstructs a path (D-034 §2a)."""
    with Session(engine) as s:
        row = s.get(ProteinAnalysis, analysis_id)
        return row.pdb_path if row is not None else None


def get_plddt_path(engine: Any, analysis_id: int) -> Optional[str]:
    """The per-residue ``plddt.json`` beside the stored structure, derived from the absolute
    ``pdb_path`` (never from client input). ``None`` when there is no structure to sit beside."""
    pdb_path = get_structure_path(engine, analysis_id)
    if not pdb_path:
        return None
    return str(Path(pdb_path).parent / "plddt.json")
