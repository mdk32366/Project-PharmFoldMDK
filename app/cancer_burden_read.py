"""The US cancer burden supplier — `D-149`. Persisted rows only, latest VALID run.

⚠⚠ **`US only — SEER/NCI` RIDES ON THE HEADER, ON `meta`, AND ON EVERY ROW.** That is the same
argument `census_structural_read.py` makes for `STRUCTURAL_ONLY`, and it is stronger here: a burden
figure is exactly the sort of number that gets lifted out of a table into a slide, and *"lung cancer
kills 662,721 people"* is a sentence about the United States that reads as a sentence about the
world. So the sentence travels with the datum, never in a tooltip.

⚠⚠ **THIS ROUTE JOINS TO NOTHING AND SAYS SO ON THE WIRE.** It serves two tables that carry no
accession, no gene, no score and no rank, and it neither reads nor imports the ranking modules. A
test asserts that no served payload key or value ever contains an accession-shaped token, a
`structural_score`, or the word `GLOBOCAN`.

⚠ **A SEPARATE MODULE, LIKE `census_structural_read.py`.** `app/reads.py` does not import this file
and this file does not import `app/reads.py` — `D-079` amendment 1 ruling 5's wall, kept checkable
at file granularity.

⚠ **Reads persisted rows and recomputes nothing.** No rate is derived, no count is summed, no
both-sexes figure is synthesised. `scripts/seer_cancer_burden.py` carries the source's numbers
through unchanged at load time; a route that recomputed would make a published statistic a function
of when it was fetched.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from core.cancer_burden import (
    ATTRIBUTION,
    ATTRIBUTION_URL,
    COUNT_POPULATION_KEY,
    CROSSWALK_REFUSED,
    DEEP_LEARNING_POSITION,
    EXCLUDED_PRODUCT,
    EXCLUDED_TIER,
    GLOBOCAN_ABSENT,
    POPULATION_KEY,
    RATE_DENOMINATOR_LABEL,
    RUN_VALID,
    SEPARATION,
    SKIN_EXCLUSION,
    STATISTICS,
    STATUS_NOT_RUN,
    UNMAPPABLE_HPA_SITES,
    US_ONLY_DISCLAIMER,
    US_ONLY_SHORT,
    rate_denominator,
)
from db.models import CancerBurdenRun, CancerBurdenStat


def _meta_block(run: CancerBurdenRun | None) -> dict[str, Any]:
    """The `meta` block, identical whether or not a run exists.

    ⚠⚠ **THE DISCLAIMER AND THE ATTRIBUTION ARE PRESENT IN THE `not_run` CASE TOO**, and that is
    deliberate rather than tidy: a not-run panel is exactly where a reader is most likely to go
    looking for the number somewhere else, and a licence obligation that appears only when the data
    happens to be loaded is an obligation that a fresh database silently drops.

    ⚠ `us_only` is the LONG sentence and `us_only_short` is the badge. Two forms, one source
    (`core.cancer_burden`); a UI that renders only the badge still cannot invent its own wording.
    """
    return {
        # ── the obligation, and the geography ──────────────────────────────────
        "us_only": US_ONLY_DISCLAIMER,
        "us_only_short": US_ONLY_SHORT,
        "geography": run.geography if run else "united_states",
        "attribution": ATTRIBUTION,
        "attribution_url": ATTRIBUTION_URL,
        # ── which release, pinned. A product name is not a version (D-093 amd 6) ──
        "source": "NCI / SEER",
        "product": "SEER*Explorer",
        "release": run.release if run else None,
        "release_updated": run.release_updated if run else None,
        "source_file": run.source_file if run else None,
        "source_sha256": run.source_sha256 if run else None,
        # ── what this surface is not ───────────────────────────────────────────
        "separation": SEPARATION,
        "deep_learning_position": DEEP_LEARNING_POSITION,
        # ── the traps, named on the wire and not only in a README ──────────────
        "count_population_key": COUNT_POPULATION_KEY,
        "population_key": POPULATION_KEY,
        "skin_exclusion": SKIN_EXCLUSION,
        "site_vocabulary": "SEER Site Recode ICD-O-3/WHO 2008",
        # ── the stated absences. An absence with a cause is a category (F-018) ──
        "globocan": GLOBOCAN_ABSENT,
        "excluded_product": EXCLUDED_PRODUCT,
        "excluded_tier": EXCLUDED_TIER,
        "crosswalk_refused": CROSSWALK_REFUSED,
        "unmappable_hpa_sites": UNMAPPABLE_HPA_SITES,
        "statistics": list(STATISTICS),
    }


def _row_projection(row: CancerBurdenStat) -> dict[str, Any]:
    """One figure. ⚠ `period` and `count_population` travel ON the row, never in the header — see
    `db.models.CancerBurdenStat`: mortality is national and 2020-2024 (2019-2023 for two sites),
    incidence is registry-area and 2019-2023, and a header would have relabelled six rows."""
    return {
        "statistic": row.statistic,
        "seer_site_id": row.seer_site_id,
        "site_label": row.site_label,
        # ⚠ the label a surface should print: the sex is IN it whenever the figure is sex-specific,
        # so a row cannot be shown as "Breast" while carrying the female-only figure.
        "display_label": (row.site_label if row.sex == "both"
                          else f"{row.site_label} ({row.sex})"),
        "recode_group": row.recode_group,
        "sex": row.sex,
        "sex_substituted": row.sex_substituted,
        "rate_per_100k": row.rate_per_100k,
        # ⚠⚠ WHAT THE "PER 100,000" IS OVER, ON THE ROW. A sex-specific rate is per 100,000 of THAT
        # SEX: `Breast (female)` at 132.53 is per 100,000 women while `Lung and Bronchus` at 47.17
        # is per 100,000 people. Both are published that way and ranking them together is the
        # standard convention — but the denominators differ, and the effect is visible in this data
        # (by rate, female-only `Corpus and Uterus, NOS` outranks `Melanoma of the Skin`; by count
        # they reverse). Stating it makes the comparison a reader's choice rather than a hidden one.
        "rate_denominator": rate_denominator(row.sex),
        "rate_denominator_label": RATE_DENOMINATOR_LABEL[rate_denominator(row.sex)],
        "rate_se": row.rate_se,
        "rate_lower_ci": row.rate_lower_ci,
        "rate_upper_ci": row.rate_upper_ci,
        "observed_count": row.observed_count,
        "count_population": row.count_population,
        "period": row.period,
        "rate_basis": row.rate_basis,
        "is_context_row": row.is_context_row,
        "is_primary_sex_stratum": row.is_primary_sex_stratum,
        # ⚠⚠ ON EVERY ROW, DELIBERATELY. A single row lifted into a slide takes the sentence with
        # it. This is the whole reason the short form exists.
        "disclaimer": US_ONLY_SHORT,
    }


def _latest_valid_run(session: Session) -> CancerBurdenRun | None:
    """The one `valid` run. The loader supersedes the previous one in the same transaction that
    inserts the new one, so exactly one is expected; the order-by is belt and brace, newest first,
    so a hand-inserted second valid run cannot serve an older release."""
    return session.scalars(
        select(CancerBurdenRun)
        .where(CancerBurdenRun.run_status == RUN_VALID)
        .order_by(desc(CancerBurdenRun.ingested_at), desc(CancerBurdenRun.id))
    ).first()


def cancer_burden_meta_payload(engine: Any) -> dict[str, Any]:
    """`GET /api/cancer-burden/meta` — the release pin, the disclaimer, the attribution and the
    named absences, without 174 figures.

    ⚠ It exists as its own route because a consumer that wants to render the US-only badge and the
    NCI credit should not have to fetch the whole table to get them — and an obligation that is
    expensive to fetch is an obligation that gets skipped.
    """
    with Session(engine) as session:
        run = _latest_valid_run(session)
        return {
            "result_status": RUN_VALID if run else STATUS_NOT_RUN,
            "meta": _meta_block(run),
            "run": None if run is None else {
                "id": run.id,
                "run_status": run.run_status,
                "status_detail": run.status_detail,
                "n_sites": run.n_sites,
                "n_stats": run.n_stats,
                "component_counts": run.component_counts or {},
                "ingested_at": run.ingested_at.isoformat() if run.ingested_at else None,
            },
        }


def cancer_burden_payload(engine: Any, *, statistic: str | None = None) -> dict[str, Any]:
    """`GET /api/cancer-burden` — the latest VALID run's figures, ordered.

    Always 200. When no valid run exists, `result_status` is `not_run` with empty rows — and the
    US-only disclaimer and the NCI attribution are **still present**, per `_meta_block`.

    ⚠⚠ **THE ORDER DIFFERS BY STATISTIC, AND THAT IS THE HONEST CHOICE RATHER THAN A TIDY ONE.**
    Deaths are ordered by **count**, because the mortality count is national and *"which cancers
    kill the most people in the US"* is a question about people. Incidence is ordered by **rate**,
    because a SEER incidence count covers the registry catchment areas only — ordering incidence by
    count would rank a partial-US number as though it were a national one. `rank_within_statistic`
    states which basis was used on every row.
    """
    if statistic is not None and statistic not in STATISTICS:
        # ⚠ A REFUSAL, not an empty list. An unrecognised filter that returned nothing would look
        # like "no cancers match", which is a confident wrong answer about the data.
        return {
            "result_status": "invalid_request",
            "meta": _meta_block(None),
            "detail": (f"statistic must be one of {list(STATISTICS)}; got {statistic!r}. "
                       f"Refusing rather than returning an empty list, which would read as "
                       f"'no cancers match'."),
            "run": None,
            "n_stats": 0,
            "rows": [],
        }

    with Session(engine) as session:
        run = _latest_valid_run(session)
        if run is None:
            return {
                "result_status": STATUS_NOT_RUN,
                "meta": _meta_block(None),
                "run": None,
                # ⚠ stated as 0 beside a `not_run` status, never omitted: a consumer reading this
                # off a payload that lacks the key gets `undefined`, which renders blank rather
                # than as "no run".
                "n_stats": 0,
                "rows": [],
            }
        query = select(CancerBurdenStat).where(CancerBurdenStat.run_id == run.id)
        if statistic is not None:
            query = query.where(CancerBurdenStat.statistic == statistic)
        rows = list(session.scalars(query).all())

        projected = [_row_projection(r) for r in rows]
        for stat in STATISTICS:
            # ⚠ Ranked over the PRIMARY, NON-CONTEXT rows only. `All Cancer Sites Combined`
            # contains every other site, so ranking it beside them would be two populations in one
            # ordering (`F-031`); a non-primary sex stratum would double-count a site.
            ranked = [p for p in projected
                      if p["statistic"] == stat
                      and p["is_primary_sex_stratum"] and not p["is_context_row"]]
            basis = "observed_count" if stat == "mortality" else "rate_per_100k"
            ranked.sort(key=lambda p: -p[basis])
            for i, p in enumerate(ranked, start=1):
                p["rank_within_statistic"] = i
                p["rank_basis"] = basis
        for p in projected:
            # ⚠ An unranked row states WHY rather than carrying a bare null (`F-023`'s defect).
            if "rank_within_statistic" not in p:
                p["rank_within_statistic"] = None
                p["rank_basis"] = None
                p["not_ranked_because"] = (
                    "all_cancer_sites_combined_is_a_denominator" if p["is_context_row"]
                    else "not_the_primary_sex_stratum_for_this_site")

        projected.sort(key=lambda p: (
            p["statistic"],
            p["rank_within_statistic"] if p["rank_within_statistic"] is not None else 10_000,
            p["site_label"],
            p["sex"],
        ))
        return {
            "result_status": RUN_VALID,
            "meta": _meta_block(run),
            "run": {
                "id": run.id,
                "run_status": run.run_status,
                "status_detail": run.status_detail,
                "n_sites": run.n_sites,
                "n_stats": run.n_stats,
                "component_counts": run.component_counts or {},
                "ingested_at": run.ingested_at.isoformat() if run.ingested_at else None,
            },
            "n_stats": len(projected),
            "rows": projected,
        }
