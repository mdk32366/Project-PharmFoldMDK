"""The census structural-profile supplier — deliberately NOT in `app/reads.py`.

⚠⚠ WHY A SEPARATE MODULE, AND IT IS NOT TIDINESS. `D-079` amendment 1 ruling 5 is the wall: the
profile may never re-enter the cohort's arc. `tests/test_structural_profile.py` asserts that
`app/reads.py` — which builds the cohort RANKING payload — cannot reach
`core/structural_profile.py`. Putting the census profile read into `reads.py` would have made that
test red, and **relaxing a wall test so a new feature fits is satisfying a test by editing it.**

⚠ So the separation is real rather than cosmetic: the module that serves run 2's scores and the
module that serves census profiles are different files, and the wall is checkable at file
granularity *and* transitively. The route layer composes them; neither imports the other.

⚠ `D-089` ruling 7 — *the surface reuses, never duplicates*. This does not open a second route.
It attaches a block to the census detail response `/api/census/{analysis_id}` already serves.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.features import FEATURE_NAMES
from core.hold48 import HOLD48_KIND_PARENT, HOLD48_KIND_TILE
from core.structural_profile import assembly_profile_payload, profile_payload
from db.models import ProteinAnalysis, ProteinFeatures

COHORT_TRANCHE = 0


def census_profile_block(engine: Any, analysis_id: int) -> Optional[dict]:
    """The profile block for one census analysis, or `None` if the row is not a census row.

    ⚠⚠ AN ABSENT FEATURE ROW IS A REFUSAL, NOT A MISSING KEY. A census protein folded but never
    feature-extracted must not render as a blank where a number goes — the reader fills a blank in
    with an assumption. It comes back as `refused_features_incomplete`, carrying its cause, which
    is `D-027`'s null-with-a-reason applied at the surface.
    """
    with Session(engine) as session:
        row = session.get(ProteinAnalysis, analysis_id)
        if row is None or row.cohort_tranche == COHORT_TRANCHE:
            return None                      # not a census row; the route already 404s on cohort ids
        accession = row.input_value
        if _incommensurable_assembly(row):
            return assembly_profile_payload(accession)
        feat = session.execute(
            select(ProteinFeatures).where(ProteinFeatures.analysis_id == analysis_id)
        ).scalars().first()

        if feat is None:
            features: dict[str, Optional[float]] = {n: None for n in FEATURE_NAMES}
            span_below_floor = False
        else:
            features = {n: getattr(feat, n) for n in FEATURE_NAMES}
            # ⚠ ruling 6 travels from the EXTRACTION record rather than being recomputed here.
            # Recomputing the F-048 set at read time would be a second implementation of a
            # membership test, and the two would drift silently.
            span_below_floor = feat.extraction_outcome == "refused_span_below_floor"

    return profile_payload(
        features, accession=accession, span_below_floor=span_below_floor)


#: The status vocabulary shown in the census TABLE. ⚠⚠ A CATEGORY, NEVER A MAGNITUDE.
#: `D-079` amendment 1 ruling 2: *"a sortable column is a ranking with extra steps."* The table is
#: sortable on every column by design (D-087), so a VALUE column would be one header click from a
#: ranked shortlist of 1,397 proteins — with `null` sorting last, the refusals would sweep to the
#: bottom and nothing on screen would say the order means nothing. A status column sorts into
#: GROUPS, which orders nothing by suitability.
PROFILE_STATUSES = (
    "computed",
    "refused_out_of_distribution",
    "refused_span_below_floor",
    "refused_features_incomplete",
    "refused_assembled_incommensurable",
    # ⚠⚠ A NEVER-FOLDED protein has no profile because there is no STRUCTURE to profile —
    # which is a different absence from the refusals above, all of which describe a fold
    # that exists. `None` here would be the absent-value defect: it cannot say which.
    'not_folded',
)


def _incommensurable_assembly(row: ProteinAnalysis) -> bool:
    """Assembled parent or tile window — not a single-pass measurement (D-120 / D-109)."""
    meta = row.meta or {}
    kind = meta.get("hold48_kind")
    if kind == HOLD48_KIND_TILE:
        return True
    if meta.get("parent_job_id") is not None and meta.get("tile_start") is not None:
        return True
    pdb_name = Path(row.pdb_path).name if row.pdb_path else ""
    if pdb_name == "stitched.pdb":
        return True
    return bool(kind == HOLD48_KIND_PARENT and row.pdb_path)


def census_profile_statuses(engine: Any) -> dict[int, str]:
    """`{analysis_id: status}` for every census row, in ONE query.

    ⚠⚠ THE VALUE IS COMPUTED AND DELIBERATELY DISCARDED. `structural_profile()` is the single
    implementation of the bar — recomputing "is it in range" here would be a second copy that
    drifts from the first (`F-052`). So the real function runs and **only its status is kept**; no
    number is returned, so none can reach the list payload. A test asserts the payload carries no
    float.

    ⚠ The three refusal causes stay DISTINCT. Pooling 1,225 + 58 + 10 into one "n/a" would lose
    the reason, and *an absence is a category with a cause*.
    """
    from core.structural_profile import structural_profile

    out: dict[int, str] = {}
    with Session(engine) as session:
        rows = session.execute(
            select(ProteinAnalysis, ProteinFeatures)
            .outerjoin(ProteinFeatures, ProteinFeatures.analysis_id == ProteinAnalysis.id)
            .where(ProteinAnalysis.cohort_tranche != COHORT_TRANCHE)
        ).all()

    for analysis, feat in rows:
        if _incommensurable_assembly(analysis):
            out[analysis.id] = "refused_assembled_incommensurable"
            continue
        if feat is None:
            features: dict[str, Optional[float]] = {n: None for n in FEATURE_NAMES}
            below = False
        else:
            features = {n: getattr(feat, n) for n in FEATURE_NAMES}
            below = feat.extraction_outcome == "refused_span_below_floor"
        result = structural_profile(features, accession=analysis.input_value, span_below_floor=below)
        # ⚠ only the CATEGORY escapes this function. `result.value` is not read.
        out[analysis.id] = "computed" if not result.is_refused else result.refusal.category
    return out
