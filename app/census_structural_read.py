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

⚠⚠ **ONE EXCEPTION, RULED RATHER THAN SLIPPED IN — THE `D-147` SEGMENT-TOPOLOGY JOIN.** Every row
is joined against the **committed** `data/census/span_segments.csv` to carry `topology`,
`segment_count`, `extracellular_total_aa`, `discarded_aa` and — where the ECD arrives in more than
one segment — the flag `ecd_intermittent`. **No score, no factor and no rank is computed here or
changed by it**, and the sentence above still holds in the way it means to: the joined file is
version-controlled, so the answer is a function of the **deployed tree** and not of the minute the
request arrived. The alternative was persisting a column, which would require a `--load` against
production — superseding the run the surface is serving — before a *display* category could exist.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from core.census_segments import (
    FLAG_ECD_INTERMITTENT,
    SPAN_SEGMENTS,
    TOPOLOGY_UNKNOWN,
    SegmentJoin,
    segment_join,
)
from core.census_segments import FLAG_MEANING as SEGMENT_FLAG_MEANING
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
    # ⚠⚠ EVERY COUNT STATES ITS KEY (method-note item 2), and this one's key is the unusual half of
    # `D-147`: it is the ONE number in this payload that is not a property of the persisted run.
    "component_counts.by_flag.ecd_intermittent": {
        "kind": "SERVE_TIME_JOIN_AGAINST_COMMITTED_FILE", "text": (
            "Rows whose census topology is `intermittent` — the extracellular part arrives in more "
            "than one segment, and span_aa is the LARGEST of them (F-037). Joined at serve from "
            "data/census/span_segments.csv, which is freshness-checked against the population "
            "manifest by content hash, and COUNTED FROM THE ROWS THAT WERE SERVED rather than read "
            "off the derivation's provenance file — so it cannot disagree with the flags beside it. "
            "⚠ It is NOT a persisted column and NOT part of the run's own component_counts; see "
            "`segment_topology` for the verdict, the three-way topology breakdown, and whether a "
            "persisted count exists to agree with. ⚠⚠ It enters NO score: structural_score and rank "
            "are identical whether or not a row is flagged (D-147), and it is NOT internalization, "
            "which formula.excluded_factors records as never measured."
        )},
}

#: The joined artifact, named as a repo-relative path so the payload can say where a served
#: category came from without a consumer guessing. ⚠ A filename is not an identity — the content
#: hash in `segment_topology.derivation_note` is what pins it to a population.
SEGMENT_SOURCE = f"data/census/{SPAN_SEGMENTS.name}"

#: ⚠⚠ Served in BOTH branches, `valid` and `not_run`, and the sentence is the point: a reader
#: meeting a not-run panel must not conclude the topology disclosure is optional.
SEGMENT_JOIN_POSTURE = (
    "Joined at serve from a COMMITTED file, never a persisted column and never a query. A --load "
    "would have been needed to persist this category, and a load supersedes the run this route is "
    "serving — an ops action for a display fact (D-147). The joined file is version-controlled, so "
    "this answer is a function of the deployed tree, not of when the request arrived."
)


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
        # ⚠⚠ THE UNION OF BOTH SUPPLIERS' MAPPINGS (`D-147`). Six flags are the formula's own and
        # `ecd_intermittent` belongs to `core/census_segments.py`; a consumer must not have to know
        # which module produced a flag in order to look up what it means. A test asserts every flag
        # that can reach a served row has an entry here — the union, not either half.
        "flag_meaning": {**FLAG_MEANING, **SEGMENT_FLAG_MEANING},
    }


def _flags_with_topology(row: CensusStructuralScore, segments: SegmentJoin) -> list[str]:
    """The row's persisted flags, plus `ecd_intermittent` when the ECD is multi-segment.

    ⚠⚠ THE ONLY PLACE THE TWO SETS MEET, AND IT IS ADDITIVE ONLY. A persisted flag is never
    dropped, reordered or rewritten here — this function may only lengthen the list. A reader
    diffing yesterday's payload against today's therefore sees an append and not a reshuffle, and
    a bug in this join cannot silently retract `no_fold`.
    """
    persisted = list(row.flags or [])
    return persisted + [f for f in segments.flags_for(row.accession) if f not in persisted]


def _row_projection(row: CensusStructuralScore, segments: SegmentJoin) -> dict[str, Any]:
    """One ranked row. ⚠ The three factors travel with the product (`D-041`'s attribution
    discipline): a consumer must never have to divide the total back apart, and on a
    span-unrecorded row that division is by zero."""
    facts = segments.facts.get(row.accession)
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
        # ⚠⚠ `D-147`. The persisted flags PLUS the serve-time topology flag, and the union is
        # ordered persisted-first so a consumer diffing two payloads sees an append, never a
        # reshuffle. ⚠ A set union rather than a bare append: if a future loader ever persists
        # `ecd_intermittent`, this must not emit it twice.
        "flags": _flags_with_topology(row, segments),
        # ⚠⚠ THE SAME FOUR FIELD NAMES `/api/census/{id}` HAS SERVED SINCE `F-037`, deliberately.
        # A ranking row and a census card must not describe one protein's segment structure in two
        # vocabularies — `topology`, `segment_count`, `extracellular_total_aa`, `discarded_aa`.
        # ⚠ `topology` is a WORD, and a stale derivation reports its VERDICT rather than the old
        # value: `unknown` means nobody derived it, anything else means it was derived against a
        # manifest that has since moved. Different causes, different fixes.
        "topology": segments.topology_for(row.accession),
        "segment_count": facts.segment_count if facts else None,
        "extracellular_total_aa": facts.extracellular_total_aa if facts else None,
        "discarded_aa": facts.discarded_aa if facts else None,
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


def _segment_topology_block(
    segments: SegmentJoin,
    projected: list[dict[str, Any]],
    persisted_by_flag: dict[str, Any],
) -> dict[str, Any]:
    """Provenance for the `D-147` join: where it came from, what it counted, and what it is not.

    ⚠⚠ **THE COUNT IS TAKEN FROM THE PROJECTED ROWS, NOT FROM THE DERIVATION'S PROVENANCE FILE**,
    and that is `F-026`'s rule: `span_segments.provenance.json` already records
    `"intermittent": 1649`, and serving *that* integer beside rows flagged by a different traversal
    would report a number nothing in this payload can check. Counting the rows makes the two
    incapable of disagreeing.

    ⚠ **The persisted count is reported beside the served one rather than replaced by it.** Today
    no loader writes `by_flag.ecd_intermittent`, so `persisted_by_flag_count` is `null` — and if
    one ever does, `agrees_with_persisted` is the field that would go `false` instead of the
    disagreement being invisible. A single number here would have hidden exactly that.
    """
    served = sum(1 for r in projected if FLAG_ECD_INTERMITTENT in r["flags"])
    persisted = persisted_by_flag.get(FLAG_ECD_INTERMITTENT)
    by_topology: dict[str, int] = {}
    for r in projected:
        word = r["topology"] or TOPOLOGY_UNKNOWN
        by_topology[word] = by_topology.get(word, 0) + 1
    return {
        "source": SEGMENT_SOURCE,
        "posture": SEGMENT_JOIN_POSTURE,
        # ⚠ The freshness verdict and its sentence, on the payload rather than in a log line: a
        # stale derivation withholds every topology and flags nothing, and a consumer must be able
        # to tell that from a census in which nothing is intermittent.
        "derivation_status": segments.verdict,
        "derivation_note": segments.note,
        "n_joined": sum(1 for r in projected if r["accession"] in segments.facts),
        "n_rows": len(projected),
        # ⚠⚠ ALL THREE TOPOLOGY WORDS WITH THEIR COUNTS, so `no_accepted_segment` is VISIBLE as its
        # own category rather than folded into `intermittent`. The 125 GPI-architecture rows have
        # no topological domains BY DESIGN (F-025) — "not missing data, and not an intermittent
        # surface" — and a two-way breakdown is how that collapse would have happened quietly.
        "by_topology": by_topology,
        "served_by_flag_count": served,
        "persisted_by_flag_count": persisted,
        "agrees_with_persisted": persisted is None or persisted == served,
        # ⚠ The two denials the flag exists to survive a copy edit with, on the wire beside the
        # count rather than only in `formula.flag_meaning`.
        "enters_score": False,
        "is_internalization": False,
        "not_internalization_note": (
            "A multi-loop extracellular topology says nothing about whether an antibody bound to "
            "this protein would be internalised. internalization is named in "
            "formula.excluded_factors as never measured by this project for any protein, and this "
            "flag does not measure it (D-147)."
        ),
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
    # ⚠ ONE read of the committed derivation per request, before the session opens — a per-row
    # file read would make the join's cost a function of the population size on every request.
    segments = segment_join()
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
                # ⚠⚠ PRESENT ON A NOT-RUN PAYLOAD TOO (`D-147`), with zero counts and the live
                # derivation verdict. A block that appeared only alongside rows would read as an
                # optional extra; the topology disclosure is not optional, and a not-run panel is
                # exactly where a reader reaches for numbers from somewhere else.
                "segment_topology": _segment_topology_block(segments, [], {}),
                "rows": [],
            }
        rows = session.scalars(
            select(CensusStructuralScore)
            .where(CensusStructuralScore.run_id == run.id)
            .order_by(CensusStructuralScore.rank)
        ).all()
        projected = [_row_projection(r, segments) for r in rows]
        persisted_counts = dict(run.component_counts or {})
        persisted_by_flag = dict(persisted_counts.get("by_flag") or {})
        topology = _segment_topology_block(segments, projected, persisted_by_flag)
        # ⚠⚠ THE SERVE-TIME COUNT JOINS `by_flag`, WHICH IS WHERE A READER LOOKS FOR IT — and the
        # persisted breakdown is not otherwise touched. `segment_topology` carries both numbers and
        # `agrees_with_persisted`, so this overlay cannot hide a future loader disagreeing with it.
        persisted_by_flag[FLAG_ECD_INTERMITTENT] = topology["served_by_flag_count"]
        persisted_counts["by_flag"] = persisted_by_flag
        persisted_counts["by_topology"] = topology["by_topology"]
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
                # the breakdown beside the totals (method-note item 2), with the D-147 serve-time
                # `by_flag.ecd_intermittent` and `by_topology` overlaid — see `segment_topology`
                "component_counts": persisted_counts,
                "computed_at": run.computed_at.isoformat() if run.computed_at else None,
            },
            # ⚠ Also at the top level, because it is the number the honesty of this payload
            # rests on and a consumer should not have to reach into `run` to state a denominator.
            "n_candidates": run.n_candidates,
            # the D-147 join's own provenance: verdict, three-way breakdown, both counts
            "segment_topology": topology,
            "rows": projected,
        }
