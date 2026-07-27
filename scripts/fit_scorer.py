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

⚠ **Per-target scores are computed and reported, not yet persisted.** D-058 decision 3 anticipated
scores hanging off `ranking_runs`, but no per-target *scores* table exists and `db/` migrations are
out of this PR's scope (D-060). So the driver persists the `ranking_run` (its `scorer_version`) and
prints the per-target score + β_k·x_k attribution + rank; persisting them waits for an additive
scores table in the `/api/ranking` PR. Named here rather than hacked into `protein_features`.

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

from core.features import FEATURE_NAMES  # noqa: E402
from core.scorer import ScorerRow, ScorerReport, run_scorer  # noqa: E402

PLDDT_FLOOR = 50.0
DEFAULT_LABELS = REPO / "data" / "adc_reference_mapping.csv"
DEFAULT_EVIDENCE = REPO / "data" / "evidence_scores.csv"
TARGET_LIST_VERSION = "Kathad-2024-PLOSONE-S3-82"


# ── row assembly (pure — fixture-tested, the heart of the driver) ────────────
@dataclass(frozen=True)
class FeatureRecord:
    """One `protein_features` row joined to its analysis's gene/disposition — the raw material the
    scorer rows are built from. Kept separate from the DB read so assembly is testable offline."""

    symbol: str
    features: tuple[Optional[float], ...]   # six, in FEATURE_NAMES order; any may be None
    disposition: Optional[str]              # ranked | held_out | excluded
    mean_plddt: Optional[float]
    below_plddt_floor: Optional[bool]


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
    group_b_symbols: set[str],
    evidence_by_symbol: dict[str, float],
) -> list[ScorerRow]:
    """Assemble `ScorerRow`s. **The label is Group B membership; the evidence score is the
    comparator — they never mix** (D-060 §3.1). `in_ranking_set` = `ranked ∧ folded ∧ pLDDT ≥ 50`
    with all six features present; excluded rows keep their reason so the surface can render them."""
    rows: list[ScorerRow] = []
    for rec in records:
        features_complete = all(v is not None for v in rec.features)
        reason = _exclusion_reason(rec, features_complete)
        in_ranking = reason is None
        # A row that is not in the ranking set may lack features; give it zeros only as inert
        # placeholders it will never be fit or scored on (it is excluded), never an imputed mean.
        feats = tuple(float(v) for v in rec.features) if features_complete else (0.0,) * len(FEATURE_NAMES)
        rows.append(ScorerRow(
            symbol=rec.symbol,
            features=feats,
            label=1 if rec.symbol in group_b_symbols else 0,
            in_ranking_set=in_ranking,
            evidence_score=evidence_by_symbol.get(rec.symbol),
            exclusion_reason=reason,
        ))
    return rows


# ── readers (invoked only on the real --run path; not exercised by fixtures) ──
def read_group_b_labels(path: Path | str) -> set[str]:
    """Group B positive symbols from the owner-curated mapping CSV (schema per PREWORK-2026-07-27
    §2: `symbol, is_group_b, agent_name, development_stage, source_citation, exclusion_reason`).
    A positive with no citation is rejected — an uncited label is not a label (D-040)."""
    positives: set[str] = set()
    with open(path, encoding="utf-8") as fh:
        reader = csv.DictReader(ln for ln in fh if not ln.startswith("#"))
        for r in reader:
            if str(r.get("is_group_b", "")).strip().lower() in ("1", "true", "yes"):
                if not (r.get("source_citation") or "").strip():
                    raise ValueError(f"{r.get('symbol')}: Group B positive without a citation (D-040)")
                positives.add(r["symbol"].strip())
    return positives


def read_evidence_scores(path: Path | str) -> dict[str, float]:
    """The comparator: {symbol: evidence_score} from the published 17 (D-040). Two-valued in
    practice (4s and 5s) — D-060 dec 8."""
    out: dict[str, float] = {}
    with open(path, encoding="utf-8") as fh:
        reader = csv.DictReader(ln for ln in fh if not ln.startswith("#"))
        for r in reader:
            symbol = (r.get("symbol") or r.get("gene") or "").strip()
            raw = (r.get("evidence_score") or r.get("score") or "").strip()
            if symbol and raw:
                out[symbol] = float(raw)
    return out


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
                features=tuple(getattr(feat, name) for name in FEATURE_NAMES),
                disposition=meta.get("disposition"),
                mean_plddt=feat.mean_plddt,
                below_plddt_floor=feat.below_plddt_floor,
            ))
    return records


# ── persistence: stamp the ranking_run's scorer_version (per-target scores deferred) ──
def persist_ranking_run(engine, report: ScorerReport, *, target_list_version: str = TARGET_LIST_VERSION) -> int:
    """Stamp the `scorer_version` onto the cohort's `ranking_run` (creating one if none exists).
    Per-target scores are NOT persisted here — no scores table exists yet (see module docstring).
    Returns the ranking_run id."""
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from db.models import RankingRun

    with Session(engine) as s:
        run = s.execute(
            select(RankingRun).where(RankingRun.target_list_version == target_list_version)
        ).scalars().first()
        if run is None:
            run = RankingRun(target_list_version=target_list_version, scorer_version=report.scorer_version)
            s.add(run)
        else:
            run.scorer_version = report.scorer_version
        s.commit()
        return run.id


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
    med = _median(report.structural_percentiles)
    print(f"headline LOO structural percentiles (N={len(report.structural_percentiles)}, "
          f"median={med:.3f}): {[round(p, 3) for p in report.structural_percentiles]}"
          if med is not None else "headline LOO: no positives")
    print(f"head-to-head over the common reference set (N={report.headto_reference_n}, "
          f"{len(report.headto_structural_percentiles)} held-out positives):")
    print(f"  structural: {[round(p, 3) for p in report.headto_structural_percentiles]}")
    print(f"  evidence  : {[round(p, 3) for p in report.headto_evidence_percentiles]}  "
          f"(two-valued comparator - degenerate by construction, D-060 dec 8)")
    print(f"Spearman(structural, evidence) over N={report.spearman_n}: {report.spearman:.4f}")
    if report.lambda_at_grid_edge:
        print("WARNING: a selected lambda landed at a grid edge - FINDING to report, not to fix by widening (D-060 dec 3)")
    print(f"excluded (reported, never dropped): {report.excluded}")
    print("top of ranking (symbol, score, contributions):")
    for symbol, score, contribs in report.ranking[:10]:
        print(f"  {symbol:12s} {score:.4f}  " + " ".join(f"{c:+.3f}" for c in contribs))
    print("NOTE: per-target scores are reported, not persisted — no scores table yet (D-060 / see module docstring).")


# ── a tiny built-in fixture cohort, so --fixture runs end to end with no labels ──
def _fixture_rows() -> list[ScorerRow]:
    feats = (1.13, 2.27, 3.41, 4.59, 5.73, 6.87)
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
    args = parser.parse_args(argv)

    if args.fixture:
        report = run_scorer(_fixture_rows())
        print_report(report)
        return 0

    # --run: the owner-authorised path. Reads real labels; refuses silently otherwise handled by argparse.
    print("WARNING: --run reads the owner-curated labels and produces a RECORDED result the moment it exists (D-060).")
    engine = engine_factory()
    records = read_feature_records(engine)
    group_b = read_group_b_labels(args.labels)
    evidence = read_evidence_scores(args.evidence)
    rows = build_scorer_rows(records, group_b, evidence)
    report = run_scorer(rows)
    print_report(report)
    if args.persist:
        rid = persist_ranking_run(engine, report)
        print(f"stamped ranking_run id={rid} with scorer_version={report.scorer_version}")
    return 0


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
