"""Per-protein staining views for the census list — `D-102`.

⚠ A SEPARATE SUPPLIER MODULE, deliberately not in `app/reads.py`. The route layer composes
suppliers; keeping each in its own file is what makes the walls checkable at file granularity, and
it is the same reason `app/census_profile_read.py` and `app/clinical_read.py` stand alone.

⚠⚠ THIS MODULE RETURNS A LENS, NOT A VERDICT. Both lenses are computed and BOTH are returned, so
the surface can never quietly pick one. `D-102`: *"an unlabelled figure is a different number
wearing the same words."*

⚠ NOTHING IS ORDERED HERE. The census arrives unordered and the reader chooses; a supplier that
sorted would be making the choice on the page's behalf, which is what `D-079` decision 1 bars.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.staining_lens import (
    BEST_PANEL,
    CRITICAL_TISSUES,
    DEFAULT_MIN_PATIENTS,
    POOLED,
    Panel,
    critical_hits,
    unknown_critical_tissues,
    view,
)
from db.models import ClinicalNormalTissue, ClinicalPathology


def _as_block(v) -> dict[str, Any]:
    """One lens as a payload block. ⚠ `lens` and both counts travel with the fraction, always."""
    return {
        "lens": v.lens,
        "category": v.category,
        "patients_positive": v.patients_positive,
        "patients_tested": v.patients_tested,
        "cancer": v.cancer,
        "panels_considered": v.panels_considered,
        "panels_excluded_small": v.panels_excluded_small,
    }


def staining_by_gene(engine: Any, min_patients: int = DEFAULT_MIN_PATIENTS) -> dict[str, dict]:
    """gene_name -> both lenses plus the critical-tissue flag.

    ⚠⚠ THE FLOOR IS A PARAMETER AND IT IS ECHOED BACK. A reader who cannot see the floor that was
    applied is reading a filtered number as an unfiltered one.
    """
    panels: dict[str, list[Panel]] = defaultdict(list)
    normals: dict[str, list[tuple[str, str]]] = defaultdict(list)
    vocabulary: set[str] = set()

    with Session(engine) as s:
        for r in s.execute(select(ClinicalPathology)).scalars():
            panels[r.gene_name].append(
                Panel(r.cancer, r.high, r.medium, r.low, r.not_detected))
        for r in s.execute(
            select(ClinicalNormalTissue.gene_name, ClinicalNormalTissue.tissue,
                   ClinicalNormalTissue.level)
        ):
            normals[r.gene_name].append((r.tissue, r.level))
            vocabulary.add(r.tissue)

    # ⚠⚠ A DECLARED TISSUE THE DATA HAS NEVER HEARD OF REMOVES NOTHING AND LOOKS LIKE IT WORKED.
    # Reported on every payload rather than discovered later — `D-093 amendment 2` §3's defect.
    unknown = unknown_critical_tissues(vocabulary) if vocabulary else ()

    out: dict[str, dict] = {}
    for gene in set(panels) | set(normals):
        hits = critical_hits(normals.get(gene, ()))
        out[gene] = {
            "min_patients": min_patients,
            "best_panel": _as_block(view(panels.get(gene, ()), BEST_PANEL, min_patients)),
            "pooled": _as_block(view(panels.get(gene, ()), POOLED, min_patients)),
            "critical_normal_high": list(hits),
            # ⚠ the list is on the payload so the surface can DECLARE it. A reader who cannot see
            # the list cannot disagree with it.
            "critical_tissues_declared": list(CRITICAL_TISSUES),
            "critical_tissues_unknown": list(unknown),
            # ⚠⚠ amendment 5 — carried so no consumer can render the flag without the caveat.
            "normal_basis": "three individuals per tissue (a few six, one just one)",
        }
    return out
