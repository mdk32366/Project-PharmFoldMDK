"""Census experimental PDB metadata supplier — `D-171` / `D-172`.

Persisted rows only (latest VALID run). Metadata-only — never recomputes
structural_score / STRUCTURAL_ONLY. Does not import `app.reads` (one-way wall).
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from db.models import CensusPdbAccession, CensusPdbRun

RUN_VALID = "valid"


def pdb_index(engine: Any) -> dict[str, Any]:
    """Latest valid run → by_accession map. Empty/invalid → honest status."""
    with Session(engine) as session:
        run = session.scalar(
            select(CensusPdbRun)
            .where(CensusPdbRun.run_status == RUN_VALID)
            .order_by(desc(CensusPdbRun.id))
            .limit(1)
        )
        if run is None:
            return {"result_status": None, "by_accession": {}}
        rows = session.scalars(
            select(CensusPdbAccession).where(CensusPdbAccession.run_id == run.id)
        ).all()
        by_acc: dict[str, dict[str, Any]] = {}
        for row in rows:
            related = getattr(row, "pdb_related", None)
            by_acc[row.accession] = {
                "pdb_status": row.pdb_status,
                "pdb_ids": list(row.pdb_ids or []),
                "pdb_best": row.pdb_best,
                "entries": list(row.entries or []),
                "pdb_related": list(related or []),
            }
        return {"result_status": run.run_status, "by_accession": by_acc, "run_id": run.id}


def attach_pdb_fields(
    engine: Any,
    rows: list[dict[str, Any]],
    *,
    include_full_ids: bool = False,
) -> str | None:
    """Mutate census list/detail with pdb_status + pdb_best (+ ids/related on detail)."""
    idx = pdb_index(engine)
    status = idx.get("result_status")
    by_acc = idx.get("by_accession") or {}
    valid = status == RUN_VALID
    for row in rows:
        if not valid:
            row["pdb_status"] = "invalid"
            row["pdb_best"] = None
            row["pdb_related"] = []
            if include_full_ids:
                row["pdb_ids"] = []
                row["pdb_entries"] = []
            continue
        hit = by_acc.get(row.get("accession") or "")
        if hit is None:
            row["pdb_status"] = "ABSENT"
            row["pdb_best"] = None
            row["pdb_related"] = []
            if include_full_ids:
                row["pdb_ids"] = []
                row["pdb_entries"] = []
        else:
            row["pdb_status"] = hit["pdb_status"]
            row["pdb_best"] = hit["pdb_best"]
            # list: compact related length signal; detail gets full list
            if include_full_ids:
                row["pdb_ids"] = hit["pdb_ids"]
                row["pdb_entries"] = hit["entries"]
                row["pdb_related"] = hit["pdb_related"]
            else:
                # list may omit full related — expose empty/non-empty via compact list of ids only
                rel = hit["pdb_related"] or []
                row["pdb_related"] = rel  # Spec: may omit if heavy; keep for honesty when small
    return status
