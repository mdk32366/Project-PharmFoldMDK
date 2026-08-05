#!/usr/bin/env python3
"""scripts/fit_scorer.py — the D-041/D-060 scorer's fit driver.

Assembles `ScorerRow`s from the persisted features (`protein_features`, joined to
`protein_analyses` for gene/disposition), the Group B labels (the owner-curated
`data/adc_reference_mapping.csv`), and the evidence-score comparator
(`data/evidence_scores.csv`), runs the pre-registered evaluation (`core.scorer.run_scorer`),
and stamps the `ranking_run` with the `scorer_version`.

⚠ **THIS SCRIPT DOES NOT RUN THE FIT AS A DELIVERED RESULT.** The first fit is an
owner-authorised run against curated labels that do not exist yet (D-060). Everything here is
tested against **fixture** labels — `build_scorer_rows` is pure and fixture-tested, and
`--fixture` runs the whole pipeline end to end on a tiny built-in cohort with no real label. The
`--run` path (real DB + real labels) is owner-only and refuses to read the label file unless asked.

**Per-target scores persist to the D-061 tables** (`target_scores` + `ranking_results`, migration
`0004`) on the `--run --persist` path. D-058 decision 3 said scores "hang off `ranking_runs`", but
that is a run-level table with no per-target rows (a gap in the ruling, D-061); `0004` gives the
per-target score + β_k·x_k attribution + rank a home in `target_scores`, and D-041's headline
*distribution* + Spearman + denominators a home in `ranking_results`. `--fixture` reports only.

`httpx` is not needed — this reads the database directly (like `core/enqueue.py`), not the read API,
because features already live in Postgres. Pure standard library plus SQLAlchemy.

Usage:
    python scripts/fit_scorer.py --fixture          # end-to-end on built-in fixture labels (no DB)
    python scripts/fit_scorer.py --run              # owner-only: real DB + real labels (the fit)
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from core.features import FEATURE_NAMES, feature_version  # noqa: E402
from core.scorer import FEATURE_SETS, ScorerRow, ScorerReport, run_scorer  # noqa: E402

PLDDT_FLOOR = 50.0
DEFAULT_LABELS = REPO / "data" / "adc_reference_mapping.csv"
DEFAULT_EVIDENCE = REPO / "data" / "evidence_scores.csv"
TARGET_LIST_VERSION = "Kathad-2024-PLOSONE-S3-82"


# ── row assembly (pure — fixture-tested, the heart of the driver) ────────────
@dataclass(frozen=True)
class FeatureRecord:
    """One `protein_features` row joined to its analysis's gene/disposition — the raw material the
    scorer rows are built from. Kept separate from the DB read so assembly is testable offline."""

    symbol: str                             # gene (for the evidence-score join)
    accession: str                          # UniProt accession (for the Group B label join, D-064 dec 1)
    features: tuple[Optional[float], ...]   # six, in FEATURE_NAMES order; any may be None
    disposition: Optional[str]              # ranked | held_out | excluded
    mean_plddt: Optional[float]
    below_plddt_floor: Optional[bool]
    analysis_id: Optional[int] = None       # the fold row these features came from (for persistence)
    # Feature 7 (D-075), CARRIED SEPARATELY and deliberately NOT folded into `features`.
    # `features` stays the six D-027 values because `features_complete` — which decides
    # `in_ranking_set` — is computed over it. Appending feature 7 there would let a null feature 7
    # push a row out of the ranking set and silently move F-004's 56. See `build_rows`.
    membrane_proximal_sasa: Optional[float] = None


def _exclusion_reason(rec: FeatureRecord, features_complete: bool) -> Optional[str]:
    """Why a target is out of the ranking set, or None if it is in. Three mechanisms, three names
    (D-060 §3.5): not folded / held out / below floor."""
    if not features_complete:
        return "not_folded"                 # a null feature means no usable structure
    if rec.disposition == "held_out":
        return "held_out"
    if rec.disposition == "excluded":
        return "excluded"
    if rec.mean_plddt is None:
        return "not_folded"
    if rec.mean_plddt < PLDDT_FLOOR:
        return "below_floor"
    return None


def build_scorer_rows(
    records: list[FeatureRecord],
    group_b_accessions: set[str],
    evidence_by_symbol: dict[str, float],
) -> list[ScorerRow]:
    """Assemble `ScorerRow`s. **The label is Group B membership (joined on ACCESSION, D-064 dec 1);
    the evidence score is the comparator (joined on gene) — they never mix** (D-060 §3.1).
    `in_ranking_set` = `ranked ∧ folded ∧ pLDDT ≥ 50` with all six features present; excluded rows
    keep their reason so the surface can render them."""
    rows: list[ScorerRow] = []
    for rec in records:
        # ⚠ `features_complete` is computed over the SIX D-027 features ONLY (D-075). Feature 7 is
        # deliberately excluded from this predicate: it decides `in_ranking_set`, so letting a null
        # feature 7 fail it would drop a row from the ranking set and move F-004's 56 — the
        # pre-registered result changed by an ablation's input. Membership stays defined by the six.
        features_complete = all(v is not None for v in rec.features)
        reason = _exclusion_reason(rec, features_complete)
        in_ranking = reason is None
        # A row that is not in the ranking set may lack features; give it zeros only as inert
        # placeholders it will never be fit or scored on (it is excluded), never an imputed mean.
        # Rows are assembled SEVEN wide: the six, then feature 7 at index 6 (D-075). `run_scorer`
        # projects onto its named set's indices, so the pre-registered fit still uses exactly 0-5.
        if features_complete:
            feats = (*(float(v) for v in rec.features), float(rec.membrane_proximal_sasa or 0.0))
        else:
            feats = (0.0,) * (len(FEATURE_NAMES) + 1)
        if in_ranking and rec.membrane_proximal_sasa is None:
            # Not fatal and not imputed: feature 7 comes from the same coordinates as features 5/6,
            # so a row with the six but no feature 7 means the extractor did not run since D-075.
            # Named loudly because `geom_proxy` would otherwise fit a 0.0 placeholder as if measured.
            print(f"WARNING: {rec.symbol} is in the ranking set but has no feature 7 "
                  f"(membrane_proximal_sasa) - re-run scripts/extract_features.py before "
                  f"--ablate geom_proxy; a 0.0 placeholder here would be an imputed value (D-027)")
        rows.append(ScorerRow(
            symbol=rec.symbol,
            features=feats,
            label=1 if rec.accession in group_b_accessions else 0,   # by ACCESSION (D-064 dec 1)
            in_ranking_set=in_ranking,
            evidence_score=evidence_by_symbol.get(rec.symbol),
            exclusion_reason=reason,
        ))
    return rows


# ── F-020: the named ablation refuses an unextracted feature 7 ───────────────
class Feature7NotExtracted(Exception):
    """`--ablate geom_proxy` was asked to fit on rows whose feature 7 was never extracted.

    ⚠ RAISED, NEVER WARNED, and this is the whole finding. `build_scorer_rows` coerces a null
    feature 7 to `0.0` (the placeholder is correct for EXCLUDED rows, which are never fit), and
    `Standardizer.apply` maps a zero-variance column to `0.0` for every row. So a `geom_proxy`
    fit over an unextracted column would collapse to `no_plddt` plus one inert parameter and
    land on the `no_plddt` baseline -- D-075 Decision 4's ambiguous row -- reported as a
    measurement of the SASA proxy when the proxy was never computed. Nothing would redden.
    """


def refuse_if_named_set_needs_feature_7(feature_set: str, records: list[FeatureRecord],
                                        rows: list[ScorerRow]) -> None:
    """Refuse if the NAMED set uses feature 7 and any RANKING-SET row lacks it.

    ⚠ SCOPED TO THE NAMED SET, NOT TO THE FIT. The pre-registered six have no feature 7 and must
    keep running untouched -- a guard that reddened that path would make F-004 unreproducible in
    order to protect an ablation.

    ⚠ SCOPED TO RANKING-SET ROWS. An excluded row's `(0.0,)*7` placeholder is inert by
    construction: it is never fit and never scored. Widening this to all rows would refuse on
    rows that cannot affect any result.

    ⚠ CALLED BEFORE `create_ranking_run()`. The refusal is run against live production
    deliberately (F-020's before/after pair), so a guard that raised after run creation would
    write a junk `ranking_runs` row on every demonstration.

    `records` and `rows` are 1:1 and same-ordered: `build_scorer_rows` appends exactly one row
    per record, in order. The null-ness must be read from `records` because `rows` has already
    coerced it to `0.0` and a genuine 0.0 is by then indistinguishable from an absent value.
    """
    if 6 not in FEATURE_SETS.get(feature_set, ()):
        return
    missing = [rec.symbol for rec, row in zip(records, rows)          # noqa: B905
               if row.in_ranking_set and rec.membrane_proximal_sasa is None]
    if not missing:
        return
    shown = ", ".join(missing[:10]) + (f", ... (+{len(missing) - 10} more)" if len(missing) > 10 else "")
    raise Feature7NotExtracted(
        f"REFUSING TO FIT --ablate {feature_set}: {len(missing)} of "
        f"{sum(1 for r in rows if r.in_ranking_set)} ranking-set rows have no feature 7 "
        f"(membrane_proximal_sasa is NULL): {shown}. "
        f"Feature 7 is a named input of the '{feature_set}' set; a 0.0 placeholder would "
        f"standardize to a constant, contribute nothing, and return the no_plddt baseline as "
        f"though it were a measurement of the proxy (D-027, D-075). "
        f"Run `scripts/extract_features.py --fill-feature-7` first."
    )


# ── label + comparator, ONE path each through core.adc_reference (D-064 dec 1) ──
# The bespoke `read_group_b_labels` / `read_evidence_scores` are DELETED, not repaired: a second
# path to the same quantity is what returned zero positives (D-064). These route through the
# functions `tests/test_adc_reference.py` already exercises against the real files.
def load_labels(path: Path | str = DEFAULT_LABELS) -> set[str]:
    """The Group B label accessions — `core.adc_reference.group_b_accessions` over the curated
    mapping (in-cohort join × development stage, D-040). One path, the tested one."""
    from core.adc_reference import cohort_accessions, group_b_accessions, load_mapping
    return group_b_accessions(load_mapping(path), cohort_accessions())


def load_evidence(path: Path | str = DEFAULT_EVIDENCE) -> dict[str, float]:
    """The comparator: {gene: evidence_score} for the published subset — via
    `core.adc_reference.load_evidence_scores` (the one path), keeping only targets with a score."""
    from core.adc_reference import load_evidence_scores
    payload = load_evidence_scores(path)
    return {e["symbol"]: float(e["evidence_score"])
            for e in payload["scores"] if e["evidence_score"] is not None}


def read_feature_records(engine) -> list[FeatureRecord]:
    """Join `protein_features` to `protein_analyses` (gene + disposition from `meta`). DB read, like
    `core/enqueue.py` — no read-API round trip, features already live in Postgres."""
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from db.models import ProteinAnalysis, ProteinFeatures

    records: list[FeatureRecord] = []
    with Session(engine) as s:
        rows = s.execute(
            select(ProteinFeatures, ProteinAnalysis)
            .join(ProteinAnalysis, ProteinFeatures.analysis_id == ProteinAnalysis.id)
        ).all()
        for feat, analysis in rows:
            meta = analysis.meta or {}
            records.append(FeatureRecord(
                symbol=meta.get("gene") or analysis.input_value,
                accession=analysis.input_value,          # the Group B label joins on this (D-064 dec 1)
                features=tuple(getattr(feat, name) for name in FEATURE_NAMES),
                membrane_proximal_sasa=getattr(feat, "membrane_proximal_sasa", None),
                disposition=meta.get("disposition"),
                mean_plddt=feat.mean_plddt,
                below_plddt_floor=feat.below_plddt_floor,
                analysis_id=analysis.id,
            ))
    return records


# ── persistence ──────────────────────────────────────────────────────────────
def create_ranking_run(engine, report: ScorerReport, *, target_list_version: str = TARGET_LIST_VERSION,
                       run_kind: str = "preregistered") -> int:
    """Create a **NEW** `ranking_run` for this scoring run and return its id. D-064 decision 3: the
    corrected run never overwrites a prior run — the invalid `ranking_run`/`ranking_results` from the
    zero-positive fit stays in place (marked, not erased), so a false artifact cannot vanish silently.
    `run_kind` is `preregistered` for the fit or `sensitivity` for a D-065 ablation, so the surface
    never serves an ablation as the result (D-065 dec 4)."""
    from sqlalchemy.orm import Session

    from db.models import RankingRun

    with Session(engine) as s:
        run = RankingRun(target_list_version=target_list_version, scorer_version=report.scorer_version,
                         run_kind=run_kind)
        s.add(run)
        s.commit()
        return run.id


def persist_results(
    engine,
    ranking_run_id: int,
    report: ScorerReport,
    symbol_to_analysis_id: dict[str, int],
) -> tuple[int, int]:
    """Write the D-061 tables: one `target_scores` row per ranked target (score, β_k·x_k
    attributions, descending rank) and one `ranking_results` row per run (the LOO distribution, the
    head-to-head, the Spearman, every denominator, the excluded set). A ranked target with no
    resolvable `analysis_id` is skipped with a warning, never given a fabricated row. Returns
    (n_target_scores, n_ranking_results)."""
    from sqlalchemy import delete
    from sqlalchemy.orm import Session

    from db.models import RankingResult, TargetScore

    with Session(engine) as s:
        # Idempotent: replace any prior rows for this run rather than duplicate them.
        s.execute(delete(TargetScore).where(TargetScore.ranking_run_id == ranking_run_id))
        s.execute(delete(RankingResult).where(RankingResult.ranking_run_id == ranking_run_id))

        written = 0
        for position, (symbol, score, contributions) in enumerate(report.ranking, start=1):
            analysis_id = symbol_to_analysis_id.get(symbol)
            if analysis_id is None:
                print(f"WARNING: no analysis_id for ranked target {symbol!r} - skipped (not fabricated)")
                continue
            s.add(TargetScore(
                ranking_run_id=ranking_run_id,
                analysis_id=analysis_id,
                score=score,
                attributions=list(contributions),
                rank=position,
            ))
            written += 1

        s.add(RankingResult(
            ranking_run_id=ranking_run_id,
            structural_percentiles=list(report.structural_percentiles),   # over CONVERGED folds (D-063)
            headto_structural_percentiles=list(report.headto_structural_percentiles),
            headto_evidence_percentiles=list(report.headto_evidence_percentiles),
            spearman=report.spearman,                                       # None if full-data fit raised
            spearman_n=report.spearman_n,
            n_ranking_set=report.n_ranking_set,
            n_fit_positives=report.n_fit_positives,                         # the LOO denominator (total positives)
            headto_reference_n=report.headto_reference_n,
            plddt_floor=PLDDT_FLOOR,
            # per fold: {symbol, lam, converged} — the non-convergent folds are named here (D-063 dec 2)
            lambda_per_fold=list(report.lambda_per_fold),
            lambda_at_grid_edge=report.lambda_at_grid_edge,
            excluded=[list(pair) for pair in report.excluded],
            # the three status fields (D-064 dec 5): a blocked statistic is null WITH the reason here
            loo_status=report.loo_status,
            fulldata_status=report.fulldata_status,
            status_detail=report.status_detail,
            scorer_version=report.scorer_version,
            feature_version=feature_version(),
        ))
        s.commit()
    return written, 1


def _build_engine():
    from sqlalchemy import create_engine

    from db.dburl import normalize_db_url

    return create_engine(normalize_db_url(os.environ["DATABASE_URL"]), future=True)


# ── reporting ────────────────────────────────────────────────────────────────
def _median(values: list[float]) -> Optional[float]:
    if not values:
        return None
    s = sorted(values)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def print_report(report: ScorerReport) -> None:
    print(f"scorer_version={report.scorer_version}")
    print(f"ranking set (ranked & folded & pLDDT>=50): N={report.n_ranking_set}, "
          f"positives={report.n_fit_positives}")
    print(f"status: loo={report.loo_status}, fulldata={report.fulldata_status} - {report.status_detail}")
    # The pre-registered headline: the LOO distribution over the folds that CONVERGED (D-063 dec 2).
    conv = report.converged_fold_count
    med = _median(report.structural_percentiles)
    if conv:
        print(f"headline LOO structural percentiles (over {conv} of {report.n_fit_positives} folds; "
              f"median={med:.3f}): {[round(p, 3) for p in report.structural_percentiles]}")
    else:
        print(f"headline LOO: 0 of {report.n_fit_positives} folds converged - NO distribution produced")
    if report.nonconvergent_folds:
        print(f"  non-convergent folds ({len(report.nonconvergent_folds)}, produced no percentile): "
              f"{report.nonconvergent_folds}")
    print(f"head-to-head over the common reference set (N={report.headto_reference_n}, "
          f"{len(report.headto_structural_percentiles)} converged held-out positives):")
    print(f"  structural: {[round(p, 3) for p in report.headto_structural_percentiles]}")
    print(f"  evidence  : {[round(p, 3) for p in report.headto_evidence_percentiles]}  "
          f"(two-valued comparator - degenerate by construction, D-060 dec 8)")
    if report.spearman is None:
        print(f"Spearman(structural, evidence): UNAVAILABLE - "
              f"{'full-data fit did not converge' if report.spearman_n >= 2 else 'n<2 common targets'} "
              f"(N={report.spearman_n})")
    else:
        print(f"Spearman(structural, evidence) over N={report.spearman_n}: {report.spearman:.4f}")
    if report.lambda_at_grid_edge:
        print("WARNING: a selected lambda landed at a grid edge - FINDING, not to fix by widening; "
              "under separation the low edge is structurally forced (D-063 dec 3)")
    print(f"excluded (reported, never dropped): {report.excluded}")
    if report.final_fit_converged:
        print("top of ranking (symbol, score, contributions):")
        for symbol, score, contribs in report.ranking[:10]:
            print(f"  {symbol:12s} {score:.4f}  " + " ".join(f"{c:+.3f}" for c in contribs))
    else:
        print(f"ranking table: UNAVAILABLE - the full-data fit did not converge at "
              f"lam={report.final_fit_lambda:g} (ranking is a NEW decision if needed, D-063 refusals)")
    print("NOTE: --run --persist writes these to target_scores + ranking_results (D-061); "
          "without --persist they are report-only.")


# ── a tiny built-in fixture cohort, so --fixture runs end to end with no labels ──
def _fixture_rows() -> list[ScorerRow]:
    # SEVEN wide (D-075): the six D-027 values plus feature 7 at index 6, matching what
    # `build_rows` now assembles, so --fixture exercises the real row shape.
    feats = (1.13, 2.27, 3.41, 4.59, 5.73, 6.87, 7.91)
    def mk(sym, f0, lab, rank=True, ev=None, reason=None):
        return ScorerRow(sym, (f0, *feats[1:]), lab, rank, ev, reason)
    return [
        mk("FIX_PA", 0.71, 1, ev=5.0), mk("FIX_PB", 1.33, 1, ev=4.0),
        mk("FIX_PC", 1.94, 1), mk("FIX_PD", 2.58, 1, ev=5.0),
        mk("FIX_NA", -2.17, 0, ev=4.0), mk("FIX_NB", -1.61, 0), mk("FIX_NC", -1.19, 0),
        mk("FIX_ND", -0.73, 0), mk("FIX_NE", -0.34, 0), mk("FIX_NF", 0.22, 0),
        mk("FIX_XLOW", 9.9, 1, rank=False, reason="below_floor"),
    ]


def run(argv: Optional[list[str]] = None, *, engine_factory: Callable[[], object] = _build_engine) -> int:
    parser = argparse.ArgumentParser(
        prog="python scripts/fit_scorer.py",
        description="Fit the D-041/D-060 scorer and report the pre-registered evaluation.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fixture", action="store_true",
                       help="run end to end on a built-in fixture cohort (no DB, no real labels)")
    group.add_argument("--run", action="store_true",
                       help="OWNER-ONLY: read the real DB + curated labels and fit (the delivered result)")
    parser.add_argument("--labels", default=str(DEFAULT_LABELS), help="Group B mapping CSV (--run only)")
    parser.add_argument("--evidence", default=str(DEFAULT_EVIDENCE), help="evidence scores CSV (--run only)")
    parser.add_argument("--persist", action="store_true",
                        help="stamp the ranking_run's scorer_version (--run only)")
    parser.add_argument("--ablate", choices=["no_plddt", "plddt_only", "geom_proxy"],
                        help="D-065 sensitivity ablation: fit one NAMED feature set (only these two; "
                             "arbitrary subsets are refused). Writes a run_kind='sensitivity' run, "
                             "never the pre-registered result. Owner-authorised, once each.")
    args = parser.parse_args(argv)

    if args.fixture:
        report = run_scorer(_fixture_rows())
        print_report(report)
        return 0

    # --run: the owner-authorised path. Reads real labels; produces a RECORDED result the moment it runs.
    from core.scorer import DegenerateLabelSet

    feature_set = args.ablate or "preregistered"          # D-065: the ablation, or the full six
    run_kind = "sensitivity" if args.ablate else "preregistered"
    print(f"WARNING: --run reads the owner-curated labels and produces a RECORDED result the moment "
          f"it exists (D-060). feature_set={feature_set}, run_kind={run_kind}.")
    engine = engine_factory()
    records = read_feature_records(engine)
    group_b = load_labels(args.labels)                    # one path (D-064 dec 1), joined on accession
    evidence = load_evidence(args.evidence)               # one path
    rows = build_scorer_rows(records, group_b, evidence)
    # F-020 — BEFORE run_scorer and three call sites before create_ranking_run(): a named set
    # that uses feature 7 refuses rather than fitting an unextracted column as a constant.
    refuse_if_named_set_needs_feature_7(feature_set, records, rows)
    try:
        report = run_scorer(rows, feature_set=feature_set)   # ValueError on any unnamed set (D-065 dec 4)
    except DegenerateLabelSet as exc:
        # A meaningless input must not produce a raise that reads like a result (D-064 dec 2).
        print(f"REFUSING TO FIT (degenerate label set): {exc}")
        return 1
    print_report(report)
    if args.persist:
        # A NEW ranking_run; the invalid id=1 stays in place (D-064 dec 3); tagged by kind (D-065 dec 4).
        rid = create_ranking_run(engine, report, run_kind=run_kind)
        symbol_to_analysis_id = {r.symbol: r.analysis_id for r in records if r.analysis_id is not None}
        n_scores, n_results = persist_results(engine, rid, report, symbol_to_analysis_id)
        print(f"wrote ranking_run id={rid} (run_kind={run_kind}, feature_set={feature_set}, "
              f"scorer_version={report.scorer_version}, loo_status={report.loo_status}, "
              f"fulldata_status={report.fulldata_status}); {n_scores} target_scores + "
              f"{n_results} ranking_results row(s)")
    return 0


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
