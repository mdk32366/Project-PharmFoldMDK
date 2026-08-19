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

from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.features import FEATURE_NAMES
from core.structural_profile import profile_payload
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
