"""The census STRUCTURAL ranking supplier — `D-144`. Persisted rows only, latest VALID run.

⚠⚠ **`STRUCTURAL_ONLY — not HPA-weighted; not ADC-ready`**, and it rides on the payload header
**and on every row**. The `census_cost_read.py` argument applies with more force here than it
did there: a cost class beside a census invites reading cheap as good, and a **rank** beside a
census invites reading position 1 as *the next ADC target*. So the sentence travels with the
datum, not in a tooltip and not in a doc a reader has to go and find.

⚠⚠ **THIS IS NOT `/api/ranking` AND SAYS SO ON THE WIRE.** `/api/ranking` serves the **learned**
cohort-82 scorer (`D-041` / `D-060` / `D-062`): six pre-registered features, fit on Group B
labels, leave-one-out percentiles, 56 scored targets, `run_kind='preregistered'`. This route
serves a **fixed arithmetic product** over 3,467 census proteins from its own two tables. The
two populations are measured under **different span definitions** (`D-081`), so `separation` and
`population_key` name the other route explicitly — `F-049`'s lesson, that a payload which says
only what its own number *is* still lets a reader assume the other number means the same thing.

⚠ **A SEPARATE MODULE, LIKE `census_profile_read.py` AND `census_cost_read.py`.** `app/reads.py`
does not import this file and this file does not import `app/reads.py` — `D-079` amendment 1
ruling 5's wall, kept checkable at file granularity: the module that serves the learned scorer's
result and the module that serves a census rank are different files, and a test asserts that
`app/reads.py` never learns how to compute a census score.

⚠ **Reads persisted rows and recomputes nothing** (the `F-004` posture): the formula runs in
`scripts/census_structural_rank.py` at load time. A route that recomputed would make the served
rank a function of when it was fetched.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from core.census_structural import (
    DISCLAIMER,
    ECD_SATURATION_AA,
    EXCLUDED_FACTORS,
    FLAG_MEANING,
    MEMBRANE_OTHER,
    MEMBRANE_SURFACE,
    MODEL_FOLD_WITHOUT_PLDDT,
    MODEL_NO_FOLD,
    STRUCTURAL_ONLY,
    SURFACE_CLASS,
)
from db.models import CensusStructuralRun, CensusStructuralScore

#: The served run status. ⚠ One word, in one place: the loader writes it
#: (`scripts/census_structural_rank.RUN_VALID`) and this predicate reads it. A route that
#: filtered on "not superseded" would serve a run the loader had marked INVALID.
RUN_VALID = "valid"

#: ⚠ `not_run` is a 200 with empty rows, never a 404 and never a fetch error — the
#: `/api/ranking` posture (`D-062`), so a surface renders a not-run panel instead of breaking.
STATUS_NOT_RUN = "not_run"

#: ⚠⚠ THE OTHER ROUTE, NAMED. `F-049`'s third instance was two routes using the word `ranked`
#: for two different populations with nothing in either payload saying which.
SEPARATION = (
    "This is NOT the cohort-82 learned scorer. /api/ranking serves the pre-registered ridge "
    "model of D-041 / D-060 — six structure-derived features fit on Group B ADC labels over 56 "
    "scored targets of the 82-target Kathad cohort, with leave-one-out percentiles. THIS route "
    "serves a fixed arithmetic product over the census (3,467 proteins carrying a measured V2 "
    "extracellular span), fits nothing and learns nothing. The two populations are measured "
    "under different span definitions (D-081) and their numbers are not comparable."
)

POPULATION_KEY = {
    "n_candidates": {"kind": "COMMITTED_FILE_COUNT", "text": (
        "Rows of data/census/census_manifest.v7.csv MINUS the reference sink. The population is "
        "a committed file, hashed onto the run — never a query against protein_analyses, which "
        "would make the denominator a function of how much folding has happened (D-024). "
        "⚠ It is NOT `n_ranking_set` on /api/ranking (the cohort-82 fit-time set, 56) and NOT "
        "`coverage.ranked` on /api/coverage (the 82-target manifest disposition)."
    )},
    "n_reference": {"kind": "JOIN_AGAINST_CURATED_FILE", "text": (
        "Census proteins with a cited ADC already directed at them "
        "(data/adc_reference_mapping.csv, D-029 / D-040) — NECTIN4/Q96NY8 among them. They keep "
        "their computed score, carry `is_reference: true`, and sort AFTER every candidate: a "
        "yardstick is not a next target. Excluded from `n_candidates` for that reason."
    )},
    "n_with_fold": {"kind": "DATABASE_JOIN", "text": (
        "Population proteins whose census representative in protein_analyses carries a structure "
        "— `assembled` or `single-pass` (D-118 / D-134). ⚠ `tiles_only` and `mucin` are NOT "
        "folds and are counted in `n_without_fold`, the same definition /api/census uses."
    )},
    "n_without_fold": {"kind": "DATABASE_JOIN", "text": (
        "Population proteins with no structure held for them. They are RANKED, not dropped, at "
        "score_model = 0.3 — a penalty, never a neutral. A rank that omitted them would be a "
        "rank of what has already been computed rather than of the census."
    )},
    "rank": {"kind": "DERIVED_ORDER", "text": (
        "Descending structural_score over the whole population, references sunk to the end, ties "
        "broken by accession so two runs over identical inputs agree. ⚠ Rank 1 means "
        "'structurally tractable and confidently folded', NEVER 'best ADC target'."
    )},
}


def formula_block() -> dict[str, Any]:
    """The formula, its constants and its **exclusions**, served rather than typed on a surface.

    ⚠⚠ THE EXCLUSIONS ARE PART OF THE FORMULA, not a footnote to it. The offline draft carried
    `cancer`, `normal_risk`, `internalization` and `density` as **0.5 neutrals** — an imputed
    value multiplied into every row and then ranked on (`F-020`'s shape). They are named here so
    a reader of the JSON can see what is missing without reading this file.
    """
    return {
        "expression": "structural_score = score_membrane × score_ecd × score_model",
        "score_membrane": (
            f"{MEMBRANE_SURFACE} when census_class == '{SURFACE_CLASS}', else {MEMBRANE_OTHER} "
            f"(including `unclassified` and `class_conflict` — F-019 — neither of which is a "
            f"surface claim)"
        ),
        "score_ecd": (
            f"min(1.0, span_aa / {ECD_SATURATION_AA}); 0 when span_aa is missing or 0 — a named "
            f"absence, never imputed"
        ),
        "score_model": (
            f"mean_plddt / 100 with a fold and a persisted pLDDT; "
            f"{MODEL_FOLD_WITHOUT_PLDDT} with a fold whose pLDDT was not persisted (F-042); "
            f"{MODEL_NO_FOLD} with no fold at all — a PENALTY, not a neutral"
        ),
        "excluded_factors": [{"factor": name, "why": why} for name, why in EXCLUDED_FACTORS],
        "flag_meaning": FLAG_MEANING,
    }


def _row_projection(row: CensusStructuralScore) -> dict[str, Any]:
    """One ranked row. ⚠ The three factors travel with the product (`D-041`'s attribution
    discipline): a consumer must never have to divide the total back apart, and on a
    span-unrecorded row that division is by zero."""
    return {
        "rank": row.rank,
        "accession": row.accession,
        "gene": row.gene,
        "tranche": row.tranche,
        "census_class": row.census_class,
        "span_aa": row.span_aa,
        "score_membrane": row.score_membrane,
        "score_ecd": row.score_ecd,
        "score_model": row.score_model,
        "structural_score": row.structural_score,
        "has_fold": row.has_fold,
        "mean_plddt": row.mean_plddt,
        "is_reference": row.is_reference,
        "flags": row.flags or [],
        # ⚠⚠ ON EVERY ROW, DELIBERATELY. A single row lifted out of this list into a slide, a
        # notebook or a spreadsheet takes the sentence with it. That is the whole reason the
        # short form exists (see `core.census_structural.STRUCTURAL_ONLY`).
        "disclaimer": STRUCTURAL_ONLY,
        # ⚠ NOT a link and NOT an id into the cohort surface: an `analysis_id` here would be one
        # careless render from opening a census fold under a cohort target's own link
        # (`tests/test_no_census_leak_on_tranche_zero.py`). Consumers address the census row by
        # ACCESSION, which /api/census/{id} has resolved since D-118.
        "census_url": f"/api/census/{row.accession}",
    }


def _latest_valid_run(session: Session) -> CensusStructuralRun | None:
    """The one `valid` run. The loader supersedes the previous one in the same transaction it
    inserts the new one, so exactly one is expected; the order-by is belt and brace, newest
    first, so a hand-inserted second valid run cannot serve an older result."""
    return session.scalars(
        select(CensusStructuralRun)
        .where(CensusStructuralRun.run_status == RUN_VALID)
        .order_by(desc(CensusStructuralRun.computed_at), desc(CensusStructuralRun.id))
    ).first()


def census_structural_payload(engine: Any) -> dict[str, Any]:
    """The latest VALID census structural run: metadata, denominators, formula, ranked rows.

    Always 200. When no valid run exists, `result_status` is `not_run` with empty rows — and
    **the disclaimer and the separation are still present**, because a surface that renders a
    not-run panel is exactly where a reader is most likely to reach for the other route's
    numbers instead.
    """
    with Session(engine) as session:
        run = _latest_valid_run(session)
        if run is None:
            return {
                "result_status": STATUS_NOT_RUN,
                "disclaimer": DISCLAIMER,
                "structural_only": STRUCTURAL_ONLY,
                "separation": SEPARATION,
                "population_key": POPULATION_KEY,
                "formula": formula_block(),
                "run": None,
                # ⚠ Stated as 0 with a `not_run` status beside it, never omitted: a consumer
                # reading `n_candidates` off a payload that lacks the key gets `undefined`, which
                # renders as blank rather than as "no run".
                "n_candidates": 0,
                "rows": [],
            }
        rows = session.scalars(
            select(CensusStructuralScore)
            .where(CensusStructuralScore.run_id == run.id)
            .order_by(CensusStructuralScore.rank)
        ).all()
        return {
            "result_status": RUN_VALID,
            "disclaimer": DISCLAIMER,
            "structural_only": STRUCTURAL_ONLY,
            "separation": SEPARATION,
            "population_key": POPULATION_KEY,
            "formula": formula_block(),
            "run": {
                "id": run.id,
                "formula_version": run.formula_version,
                "span_definition": run.span_definition,
                "population_source": run.population_source,
                "population_sha256": run.population_sha256,
                "run_status": run.run_status,
                "status_detail": run.status_detail,
                "n_candidates": run.n_candidates,
                "n_reference": run.n_reference,
                "n_with_fold": run.n_with_fold,
                "n_without_fold": run.n_without_fold,
                # the breakdown beside the totals (method-note item 2)
                "component_counts": run.component_counts or {},
                "computed_at": run.computed_at.isoformat() if run.computed_at else None,
            },
            # ⚠ Also at the top level, because it is the number the honesty of this payload
            # rests on and a consumer should not have to reach into `run` to state a denominator.
            "n_candidates": run.n_candidates,
            "rows": [_row_projection(r) for r in rows],
        }
