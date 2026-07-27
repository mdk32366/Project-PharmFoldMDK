"""D-060 — the scorer fit driver (scripts/fit_scorer.py).

Row assembly is pure and fixture-tested: the label (Group B) and the comparator (evidence score)
are kept separate, and the three exclusion mechanisms get their three names. The `--fixture` path
runs the whole pipeline end to end with no real label, and `persist_ranking_run` stamps the
`scorer_version` into a SQLite `ranking_run`. No real label file is read anywhere here.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import fit_scorer as fs  # noqa: E402
from core.features import FEATURE_NAMES  # noqa: E402

SIX = (1.13, 2.27, 3.41, 4.59, 5.73, 6.87)


def _rec(symbol, f0, disp="ranked", plddt=71.5, features=None):
    feats = features if features is not None else (f0, *SIX[1:])
    return fs.FeatureRecord(symbol=symbol, features=feats, disposition=disp,
                            mean_plddt=plddt, below_plddt_floor=(plddt < 50 if plddt is not None else None))


def test_build_rows_keeps_label_and_comparator_separate():
    """The label is Group B membership; the evidence score is the comparator. A Group B symbol is a
    positive regardless of its evidence score, and a non-Group-B symbol with a high evidence score
    is still a negative (D-060 §3.1)."""
    records = [_rec("GB_HIGH", 1.4), _rec("NOTGB_HIGH", 1.9)]
    rows = fs.build_scorer_rows(records, group_b_symbols={"GB_HIGH"},
                                evidence_by_symbol={"GB_HIGH": 5.0, "NOTGB_HIGH": 5.0})
    by = {r.symbol: r for r in rows}
    assert by["GB_HIGH"].label == 1 and by["GB_HIGH"].evidence_score == 5.0
    assert by["NOTGB_HIGH"].label == 0 and by["NOTGB_HIGH"].evidence_score == 5.0  # high evidence ≠ label


def test_build_rows_names_the_three_exclusion_mechanisms():
    """Below-floor / held-out / not-folded are three mechanisms with three names (D-060 §3.5),
    each out of the ranking set with its reason recorded, never dropped."""
    records = [
        _rec("RANKED", 1.2, disp="ranked", plddt=71.0),
        _rec("LOW", 0.9, disp="ranked", plddt=47.63),                 # below floor
        _rec("WHOLE", 0.4, disp="held_out", plddt=75.04),             # held out
        _rec("FAILED", 0.0, disp="held_out", plddt=None,
             features=(None, None, None, None, None, None)),          # no features → not folded
    ]
    rows = {r.symbol: r for r in fs.build_scorer_rows(records, set(), {})}
    assert rows["RANKED"].in_ranking_set is True and rows["RANKED"].exclusion_reason is None
    assert rows["LOW"].in_ranking_set is False and rows["LOW"].exclusion_reason == "below_floor"
    assert rows["WHOLE"].in_ranking_set is False and rows["WHOLE"].exclusion_reason == "held_out"
    assert rows["FAILED"].in_ranking_set is False and rows["FAILED"].exclusion_reason == "not_folded"


def test_build_rows_never_imputes_a_mean_for_a_failed_target():
    """A feature-less (failed) target is excluded with inert placeholders it is never scored on —
    NOT an imputed mean (D-027/D-060). It must not enter the ranking set."""
    rec = _rec("FAILED", 0.0, plddt=None, features=(None,) * len(FEATURE_NAMES))
    (row,) = fs.build_scorer_rows([rec], set(), {})
    assert row.in_ranking_set is False
    assert row.exclusion_reason == "not_folded"


def test_persist_ranking_run_stamps_scorer_version():
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session

    from core.scorer import run_scorer
    from db.models import Base, RankingRun

    engine = create_engine("sqlite://", future=True)
    Base.metadata.create_all(engine)
    report = run_scorer(fs._fixture_rows())
    rid = fs.persist_ranking_run(engine, report, target_list_version="test-tl")
    with Session(engine) as s:
        run = s.get(RankingRun, rid)
        assert run.scorer_version == report.scorer_version
        assert run.target_list_version == "test-tl"
    # idempotent-ish: a second call updates the same run's version, does not duplicate
    rid2 = fs.persist_ranking_run(engine, report, target_list_version="test-tl")
    assert rid2 == rid
    with Session(engine) as s:
        assert len(s.execute(select(RankingRun)).scalars().all()) == 1


def test_fixture_run_end_to_end_returns_zero(capsys):
    """--fixture runs the whole pipeline on built-in labels — the §6 'able to run end to end against
    fixture labels' criterion, with no DB and no real label file."""
    rc = fs.run(["--fixture"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "scorer_version=" in out
    assert "ranking set" in out
    assert "head-to-head" in out


def test_run_path_does_not_touch_the_db_without_being_asked():
    """--fixture must never build an engine — a guard that the safe path is genuinely DB-free."""
    def exploding_engine():
        raise AssertionError("--fixture must not build a database engine")
    assert fs.run(["--fixture"], engine_factory=exploding_engine) == 0


# ── D-061: the scores tables and their persistence ───────────────────────────
def test_scores_tables_build_on_sqlite():
    from sqlalchemy import create_engine, inspect

    from db.models import Base

    engine = create_engine("sqlite://", future=True)
    Base.metadata.create_all(engine)
    names = set(inspect(engine).get_table_names())
    assert {"target_scores", "ranking_results"} <= names
    ts_cols = {c["name"] for c in inspect(engine).get_columns("target_scores")}
    assert {"ranking_run_id", "analysis_id", "score", "attributions", "rank"} <= ts_cols
    rr_cols = {c["name"] for c in inspect(engine).get_columns("ranking_results")}
    assert {"structural_percentiles", "spearman", "n_ranking_set", "excluded", "scorer_version"} <= rr_cols


def test_persist_results_writes_scores_and_the_distribution():
    """D-061: one target_scores row per ranked target (descending rank, six attributions) and one
    ranking_results row carrying the LOO distribution + denominators. The pre-registered distribution
    lands as a JSON list, not a scalar."""
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session

    from core.scorer import run_scorer
    from db.models import Base, ProteinAnalysis, RankingResult, TargetScore

    engine = create_engine("sqlite://", future=True)
    Base.metadata.create_all(engine)

    report = run_scorer(fs._fixture_rows())
    ranked_symbols = [s for s, _, _ in report.ranking]
    # create a protein_analyses row per ranked fixture symbol; map symbol -> analysis_id
    symbol_to_analysis_id: dict[str, int] = {}
    with Session(engine) as s:
        for sym in ranked_symbols:
            a = ProteinAnalysis(input_type="uniprot", input_value=sym)
            s.add(a)
            s.flush()
            symbol_to_analysis_id[sym] = a.id
        s.commit()

    rid = fs.persist_ranking_run(engine, report, target_list_version="test-tl")
    n_scores, n_results = fs.persist_results(engine, rid, report, symbol_to_analysis_id)
    assert n_scores == len(ranked_symbols)
    assert n_results == 1

    with Session(engine) as s:
        scores = s.execute(select(TargetScore).order_by(TargetScore.rank)).scalars().all()
        assert [t.rank for t in scores] == list(range(1, len(ranked_symbols) + 1))   # 1..N
        assert all(len(t.attributions) == 6 for t in scores)                          # six β_k·x_k
        top = scores[0]
        assert top.rank == 1                                                          # descending by score
        results = s.execute(select(RankingResult)).scalars().all()
        assert len(results) == 1
        rr = results[0]
        assert isinstance(rr.structural_percentiles, list)                            # a distribution, not a scalar
        assert len(rr.structural_percentiles) == report.n_fit_positives
        assert rr.n_ranking_set == report.n_ranking_set
        assert rr.plddt_floor == fs.PLDDT_FLOOR
        assert rr.scorer_version == report.scorer_version

    # idempotent: a second persist replaces, does not duplicate
    fs.persist_results(engine, rid, report, symbol_to_analysis_id)
    with Session(engine) as s:
        assert len(s.execute(select(RankingResult)).scalars().all()) == 1
        assert len(s.execute(select(TargetScore)).scalars().all()) == len(ranked_symbols)


@pytest.mark.postgres
def test_migration_0004_created_the_scores_tables(pg_engine):
    """0004 verified by querying information_schema, not by alembic's exit code
    (docs/HAZARD-search-path-seams.md). Runs in the postgres CI job."""
    from sqlalchemy import text

    with pg_engine.connect() as c:
        present = {r[0] for r in c.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema='public' AND table_name IN ('target_scores','ranking_results')"
        ))}
    assert present == {"target_scores", "ranking_results"}, "0004 must create both tables (proven by query)"
